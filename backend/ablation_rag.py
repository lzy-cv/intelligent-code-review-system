"""RAG 消融实验：验证 RAG 对缺陷报告与修复建议质量的贡献。

对比两组（其余流水线完全一致，唯一变量是有无 RAG）：
  A. Full   — RAG 增强（给规则缺陷附 CWE + 参考修复代码）+ 案例注入 LLM Prompt
  B. NoRAG  — 关闭 RAG

指标：
  ① 结构化增强覆盖率（确定性，无需 LLM 参与）
     - 附 CWE 编号的缺陷占比
     - 附参考修复代码的缺陷占比
  ② 修复建议质量（LLM 参与）
     - 修复建议平均长度
     - 修复建议具体度：是否命中该缺陷类型的「预期修复手段」关键词
       * 关键词表由人工按缺陷类型定义，独立于 RAG 案例库，避免循环论证
       * 只在「命中人工标注真值」的缺陷上统计（即真正例）

用法：
    python ablation_rag.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.engine import semgrep, rag  # noqa: E402
from app.engine.llm_analyzer import analyze as llm_analyze  # noqa: E402
from app.engine.pipeline import _merge  # noqa: E402
from benchmark import SAMPLES, TOL  # noqa: E402


# 各缺陷类型「合理的修复手段」关键词。
# 注意：这份表是人工按缺陷语义定义的，与 rag.py 里的 CORPUS 无关联，
# 因此用它评分不会构成「用 RAG 的结果验证 RAG」的循环论证。
FIX_EXPECT = {
    "硬编码密钥": ["环境变量", "配置", "密钥管理", "轮换", "kms", "vault", ".env"],
    "硬编码口令": ["环境变量", "配置", "密钥管理", "轮换", ".env"],
    "SQL注入": ["参数化", "预编译", "占位符", "绑定参数", "prepare", "execute"],
    "XSS": ["转义", "textcontent", "净化", "白名单", "sanitize", "escape"],
    "eval": ["json.parse", "json.loads", "删除", "替换", "安全解析"],
    "Cookie安全": ["httponly", "samesite", "secure"],
    "输入未校验": ["校验", "验证", "白名单", "类型", "长度", "合法性"],
    "除零未校验": ["校验", "为零", "零", "异常", "try"],
    "缺少错误处理": ["try", "except", "catch", "异常", "错误处理"],
    "资源未释放": ["close", "with", "上下文管理器", "释放", "finally", "关闭"],
    "返回敏感数据": ["脱敏", "只返回", "最小", "过滤", "字段"],
    "敏感信息": ["脱敏", "过滤", "日志", "敏感"],
    "调试日志": ["移除", "删除", "日志框架", "logging", "级别"],
    "调试输出": ["移除", "删除", "日志框架", "logging", "级别"],
    "var声明": ["let", "const"],
    "路径穿越": ["校验", "白名单", "basename", "规范化", "realpath", "路径"],
    "弱随机数": ["secrets", "systemrandom", "加密安全", "随机数", "uuid"],
    "弱哈希算法": ["sha256", "sha-256", "bcrypt", "argon2", "加盐", "salt", "哈希"],
    "会话安全": ["httponly", "samesite", "secure", "签名", "csp"],
}


def _fix_is_specific(label: str, fix_text: str):
    """命中该缺陷类型任一预期修复关键词即视为「具体」。未定义类型返回 None。"""
    keys = FIX_EXPECT.get(label)
    if not keys:
        return None
    text = (fix_text or "").lower()
    return any(k.lower() in text for k in keys)


def match_pairs(reported: list[dict], truth, tol: int = TOL) -> list[tuple[str, dict]]:
    """与 evaluate() 一致的贪心行号匹配，返回 [(真值标签, 报告缺陷), ...]。"""
    ordered = sorted(reported, key=lambda d: d["line"])
    used, pairs = set(), []
    for gline, label in truth:
        for i, r in enumerate(ordered):
            if i not in used and abs(r["line"] - gline) <= tol:
                used.add(i)
                pairs.append((label, r))
                break
    return pairs


def run_group(sample: dict, use_rag: bool):
    """跑一次融合流水线。use_rag=False 时既不增强规则缺陷，也不注入案例。"""
    code, lang = sample["code"], sample["lang"]
    rule_defects, _, _, _ = semgrep.run_review(code, lang)
    if use_rag:
        rag.enhance(rule_defects)
        rag_cases = rag.cases_for_llm(rule_defects)
    else:
        rag_cases = []
    llm_defects, llm_used = llm_analyze(code, lang, rule_defects, rag_cases)
    return _merge(rule_defects, llm_defects), llm_used


def part1_enhancement() -> dict:
    """确定性指标：RAG 对规则缺陷的结构化增强覆盖率（不调用 LLM）。"""
    print("① 结构化增强覆盖率（确定性，无需 LLM）")
    print(f"{'样本':<16}{'规则缺陷':>9}{'附 CWE':>9}{'附参考代码':>11}")
    print("-" * 46)
    total = with_cwe = with_code = 0
    for s in SAMPLES:
        rules, _, _, _ = semgrep.run_review(s["code"], s["lang"])
        n = len(rules)
        rag.enhance(rules)
        c = sum(1 for d in rules if d.get("cwe"))
        k = sum(1 for d in rules if d.get("code"))
        total += n
        with_cwe += c
        with_code += k
        print(f"{s['name']:<16}{n:>9}{c:>9}{k:>11}")
    print("-" * 46)
    print(f"{'合计':<16}{total:>9}{with_cwe:>9}{with_code:>11}")
    print(f"启用 RAG：CWE 覆盖率 {with_cwe / total * 100:.1f}%，"
          f"参考代码覆盖率 {with_code / total * 100:.1f}%")
    print("关闭 RAG：两项覆盖率均为 0.0%（规则引擎自身不产出 CWE 与修复代码）\n")
    return {"total": total, "with_cwe": with_cwe, "with_code": with_code}


def part2_llm(use_rag: bool) -> dict:
    """LLM 相关指标。为降低外部服务波动影响，失败样本会计数并提示。"""
    stats = {
        "defects": 0, "fix_chars": 0,
        "llm_defects": 0, "llm_fix_chars": 0,
        "matched": 0, "specific": 0,
        "llm_matched": 0, "llm_specific": 0,
        "fail": 0,
    }
    for s in SAMPLES:
        defects, used = run_group(s, use_rag)
        if not used:
            stats["fail"] += 1

        for label, d in match_pairs(defects, s["truth"]):
            hit = _fix_is_specific(label, d.get("fix", ""))
            if hit is None:
                continue
            stats["matched"] += 1
            stats["specific"] += 1 if hit else 0
            if d.get("source") == "llm":
                stats["llm_matched"] += 1
                stats["llm_specific"] += 1 if hit else 0

        for d in defects:
            stats["defects"] += 1
            stats["fix_chars"] += len(d.get("fix", ""))
            if d.get("source") == "llm":
                stats["llm_defects"] += 1
                stats["llm_fix_chars"] += len(d.get("fix", ""))

        tag = "OK" if used else "失败"
        print(f"  [{tag}] {s['name']:<14} 缺陷 {len(defects):>2} 条")
        time.sleep(3)
    return stats


def _pct(a: int, b: int) -> float:
    return a / b * 100 if b else 0.0


def main():
    print("=" * 72)
    print("RAG 消融实验：Full（启用 RAG） vs NoRAG（关闭 RAG）")
    print("=" * 72)

    enhance = part1_enhancement()

    print("② 修复建议质量（LLM 参与）")
    print("正在运行 NoRAG 组…")
    norag = part2_llm(use_rag=False)
    print("正在运行 Full 组…")
    full = part2_llm(use_rag=True)

    print("\n" + "=" * 72)
    print(f"{'指标':<30}{'NoRAG':>14}{'Full':>14}")
    print("-" * 72)
    rows = [
        ("缺陷总数", norag["defects"], full["defects"], "int"),
        ("全部缺陷修复建议平均长度",
         round(norag["fix_chars"] / max(norag["defects"], 1), 1),
         round(full["fix_chars"] / max(full["defects"], 1), 1), "int"),
        ("LLM 缺陷数", norag["llm_defects"], full["llm_defects"], "int"),
        ("LLM 修复建议平均长度",
         round(norag["llm_fix_chars"] / max(norag["llm_defects"], 1), 1),
         round(full["llm_fix_chars"] / max(full["llm_defects"], 1), 1), "int"),
        ("命中缺陷的修复具体度", _pct(norag["specific"], norag["matched"]),
         _pct(full["specific"], full["matched"]), "pct"),
        ("其中 LLM 缺陷的修复具体度", _pct(norag["llm_specific"], norag["llm_matched"]),
         _pct(full["llm_specific"], full["llm_matched"]), "pct"),
        ("LLM 调用失败样本数", norag["fail"], full["fail"], "int"),
    ]
    for name, a, b, kind in rows:
        if kind == "pct":
            print(f"{name:<30}{a:>13.1f}%{b:>13.1f}%")
        else:
            print(f"{name:<30}{a:>14}{b:>14}")

    print("-" * 72)
    print(f"（修复具体度统计样本量：NoRAG {norag['matched']} 处，Full {full['matched']} 处；"
          f"其中 LLM 缺陷 NoRAG {norag['llm_matched']} 处，Full {full['llm_matched']} 处）")

    if norag["fail"] or full["fail"]:
        print("\n⚠ 存在 LLM 调用失败的样本，本次结果仅供参考，建议服务稳定后重跑。")

    result = {
        "samples": len(SAMPLES),
        "tolerance": TOL,
        "enhancement": enhance,
        "norag": norag,
        "full": full,
    }
    Path("ablation_rag.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n结果已保存到 ablation_rag.json")


if __name__ == "__main__":
    main()
