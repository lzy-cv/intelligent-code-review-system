"""Semgrep 规则引擎封装：子进程运行 -> 解析 JSON -> 映射为统一缺陷模型"""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path


class SemgrepRunError(Exception):
    pass


RULES_DIR = Path(__file__).resolve().parent.parent.parent / "rules"

LANG_EXT = {
    "javascript": "js",
    "typescript": "ts",
    "python": "py",
    "java": "java",
    "go": "go",
    "php": "php",
    "c": "c",
    "cpp": "cpp",
    "ruby": "rb",
    "rust": "rs",
}

# 规则集 -> semgrep --config 参数
RULESETS = {
    "local": str(RULES_DIR / "demo.yaml"),
    "default": "p/default",
    "owasp": "p/owasp-top-ten",
    "security-audit": "p/security-audit",
    "auto": "auto",
}

SEVERITY_MAP = {"ERROR": "high", "WARNING": "mid", "INFO": "low"}
SEV_ORDER = {"high": 0, "mid": 1, "low": 2}

CATEGORY_MAP = {
    "security": "安全",
    "code-quality": "代码质量",
    "correctness": "正确性",
    "maintainability": "可维护性",
    "performance": "性能",
}

# 规则 id 末尾段 -> (标题, 描述, 修复建议)
RULE_INFO = {
    "hardcoded-secret": (
        "硬编码 API 密钥",
        "检测到明文写入的密钥常量，属于敏感信息泄露。密钥一旦进入代码仓库即视为泄露，可被用于未授权调用下游服务。",
        "将密钥迁移到环境变量或密钥管理服务（KMS/Vault），并立即轮换已泄露的密钥。",
    ),
    "sql-injection": (
        "SQL 注入风险",
        "SQL 语句通过字符串拼接用户输入构造，攻击者可注入恶意 SQL 绕过认证或拖库。",
        "使用参数化查询 / 预编译语句，禁止字符串拼接 SQL。",
    ),
    "sql-injection-js": (
        "SQL 注入风险",
        "SQL 语句通过模板字符串拼接用户输入，攻击者可注入恶意 SQL 绕过认证或拖库。",
        "使用参数化查询 / 预编译语句，禁止字符串拼接 SQL。",
    ),
    "eval": (
        "eval() 危险函数调用",
        "eval 会执行由用户输入拼接出的字符串，等价于远程代码执行（RCE）。",
        "删除 eval，改用 JSON.parse 或安全的序列化方式处理数据。",
    ),
    "innerhtml-xss": (
        "XSS 跨站脚本攻击",
        "innerHTML 直接注入未转义的内容，攻击者可注入恶意标签窃取 Cookie、执行任意脚本。",
        "改用 textContent 赋值，或对内容做转义 / 白名单过滤后再渲染。",
    ),
    "cookie-httponly": (
        "Cookie 安全属性缺失",
        "Cookie 未开启 httpOnly，一旦发生 XSS 即可被脚本窃取会话。",
        "开启 httpOnly 与 SameSite，生产环境同时开启 Secure。",
    ),
    "var-declaration": (
        "使用 var 声明变量",
        "var 存在变量提升与函数级作用域问题，易引发意外覆盖与闭包 bug。",
        "改用 let / const 声明。",
    ),
    "debug-log": (
        "遗留调试日志",
        "调试输出遗留在生产代码中，可能泄露内部数据并影响性能。",
        "移除或改用统一日志框架并控制日志级别。",
    ),
}


def _humanize(seg: str) -> str:
    return seg.replace("-", " ").replace("_", " ").title()


def _cwe(metadata: dict) -> str:
    c = metadata.get("cwe")
    if isinstance(c, list) and c:
        return str(c[0])
    if isinstance(c, str):
        return c
    return ""


def _build_defects(results: list) -> list[dict]:
    defects = []
    seen = set()
    for r in results:
        check_id = r.get("check_id", "")
        seg = check_id.split(".")[-1].lower()
        start = r.get("start") or {}
        extra = r.get("extra") or {}
        line = start.get("line", 0)
        severity = extra.get("severity", "INFO")
        level = SEVERITY_MAP.get(severity, "low")
        metadata = extra.get("metadata") or {}
        cat = CATEGORY_MAP.get(metadata.get("category", ""), "其他")
        cwe = _cwe(metadata)

        info = RULE_INFO.get(seg)
        if info:
            title, desc, fix = info
        else:
            title = _humanize(seg)
            desc = extra.get("message", "") or "Semgrep 规则命中"
            fix = "请参考相关安全规范修复该问题。"

        # 按「行号 + 规则」去重
        key = (line, seg)
        if key in seen:
            continue
        seen.add(key)

        defects.append({
            "line": line,
            "level": level,
            "cat": cat,
            "title": title,
            "desc": desc,
            "fix": fix,
            "rule_id": seg,
            "cwe": cwe,
        })

    defects.sort(key=lambda d: (d["line"], SEV_ORDER.get(d["level"], 9)))
    return defects


def run_review(code: str, language: str = "javascript", ruleset: str = "local"):
    """运行 Semgrep，返回 (defects, counts, duration_ms, rule_findings)"""
    ext = LANG_EXT.get(language, "js")
    config = RULESETS.get(ruleset, RULESETS["local"])

    start = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / f"code.{ext}"
        target.write_text(code, encoding="utf-8")

        cmd = [
            "semgrep", "scan", "--json", "--config", config,
            "--metrics=off", "--disable-version-check", str(target),
        ]
        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", env=env, timeout=180)
        except FileNotFoundError:
            raise SemgrepRunError("未找到 semgrep 命令，请先安装：pip install semgrep")
        except subprocess.TimeoutExpired:
            raise SemgrepRunError("Semgrep 执行超时（180s）")

        if not proc.stdout.strip():
            raise SemgrepRunError(f"Semgrep 未返回结果：{proc.stderr.strip()[:300]}")

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise SemgrepRunError(f"Semgrep 输出解析失败：{e}")

        if proc.returncode not in (0, 1) and data.get("errors"):
            raise SemgrepRunError(json.dumps(data["errors"], ensure_ascii=False)[:500])

        defects = _build_defects(data.get("results", []))
        rule_findings = len(data.get("results", []))

    duration_ms = int((time.time() - start) * 1000)
    counts = {
        "total": len(defects),
        "high": sum(1 for d in defects if d["level"] == "high"),
        "mid": sum(1 for d in defects if d["level"] == "mid"),
        "low": sum(1 for d in defects if d["level"] == "low"),
    }
    return defects, counts, duration_ms, rule_findings
