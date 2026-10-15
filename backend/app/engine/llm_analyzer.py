"""LLM 深度分析：调用 DeepSeek（OpenAI 兼容）做语义级代码审查。

未配置 DEEPSEEK_API_KEY 时自动跳过（返回空），不影响规则引擎。
带重试 + 退避，容忍大模型接口的间歇性失败。
"""
import json
import os
import sys
import time
from pathlib import Path


def _load_dotenv():
    p = Path(__file__).resolve().parent.parent.parent / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


def _config() -> dict:
    return {
        "api_key": os.environ.get("DEEPSEEK_API_KEY", "") or os.environ.get("LLM_API_KEY", ""),
        "base_url": os.environ.get("LLM_BASE_URL", "https://api.deepseek.com"),
        "model": os.environ.get("LLM_MODEL", "deepseek-chat"),
    }


def is_enabled() -> bool:
    return bool(_config()["api_key"])


def _normalize(items) -> list[dict]:
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        try:
            line = int(it.get("line", 0))
        except (TypeError, ValueError):
            line = 0
        level = str(it.get("level", "low")).lower()
        if level not in ("high", "mid", "low"):
            level = "low"
        title = str(it.get("title", "")).strip()
        if not title:
            continue
        try:
            conf = float(it.get("confidence", 0.5))
        except (TypeError, ValueError):
            conf = 0.5
        conf = max(0.0, min(1.0, conf))
        out.append({
            "line": line,
            "level": level,
            "cat": str(it.get("cat", "语义")),
            "title": title,
            "desc": str(it.get("desc", "")),
            "fix": str(it.get("fix", "")),
            "source": "llm",
            "rule_id": "",
            "cwe": "",
            "code": "",
            "confidence": conf,
        })
    return out


def analyze(code: str, language: str, rule_defects: list[dict], rag_cases: list[dict]) -> tuple[list[dict], bool]:
    """返回 (llm_defects, used)。未配置或多次重试仍失败时返回 ([], False)。"""
    cfg = _config()
    if not cfg["api_key"]:
        return [], False

    from openai import OpenAI

    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])

    rule_summary = "\n".join(
        f"- 第 {d['line']} 行 [{d['level']}] {d['title']}" for d in rule_defects[:10]
    ) or "无"
    rag_text = "\n".join(
        f"### {c['cwe']} {c['title']}\n{c['desc']}\n修复示例：{c['fix']}" for c in rag_cases
    ) or "无"

    system = (
        "你是一名资深代码审查专家，负责在规则引擎（Semgrep）之外做深度语义分析，"
        "找出需要业务理解才能发现的逻辑缺陷、健壮性问题与安全风险。\n\n"
        f"【规则引擎已发现的缺陷（无需重复报告）】\n{rule_summary}\n\n"
        f"【RAG 检索到的相似缺陷案例（供参考）】\n{rag_text}\n\n"
        "【输出要求】\n"
        "1. 只报告规则引擎未覆盖的、语义层面的新问题（如输入校验缺失、错误处理缺失、资源泄漏、逻辑错误、越权等）。\n"
        "2. 严格输出一个 JSON 对象，格式："
        '{"defects": [{"line": 行号, "level": "high|mid|low", "cat": "分类", "title": "问题标题", "desc": "问题描述", "fix": "修复建议", "confidence": 0到1的置信度}]}\n'
        "3. confidence 表示你对该判断的把握程度（0-1）：只有非常有把握的缺陷才给 0.8 以上，不确定的给 0.5 以下。\n"
        '4. 没有新问题则输出 {"defects": []}。\n'
        "5. 不要输出 JSON 以外的任何文字。"
    )

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=cfg["model"],
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"语言：{language}\n代码：\n{code[:6000]}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=30,
            )
            content = resp.choices[0].message.content or "{}"
            data = json.loads(content)
            items = data.get("defects", []) if isinstance(data, dict) else []
            return _normalize(items), True
        except Exception as e:
            print(f"[LLM] 第 {attempt + 1} 次调用失败：{type(e).__name__}: {str(e)[:150]}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    return [], False
