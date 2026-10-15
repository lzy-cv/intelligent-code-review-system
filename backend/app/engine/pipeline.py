"""审查流水线：规则引擎(Semgrep) → RAG 增强 → LLM 深度分析 → 融合去重"""
import time

from . import semgrep, rag
from .llm_analyzer import analyze as llm_analyze

_SEV_ORDER = {"high": 0, "mid": 1, "low": 2}


# LLM 缺陷置信度阈值：低于该值视为不可靠，过滤以降低误报
CONFIDENCE_THRESHOLD = 0.7


def _merge(rule_defects: list[dict], llm_defects: list[dict]) -> list[dict]:
    merged, seen = [], set()
    for d in rule_defects:
        d = dict(d)
        d.setdefault("source", "rule")
        merged.append(d)
        seen.add((d["line"], d["title"]))
    for d in llm_defects:
        # 置信度过滤：低置信度视为幻觉，丢弃以降低误报
        if d.get("confidence", 0.5) < CONFIDENCE_THRESHOLD:
            continue
        if (d["line"], d["title"]) in seen:
            continue
        merged.append(d)
    # 去掉内部字段，保持输出结构不变
    for d in merged:
        d.pop("confidence", None)
    merged.sort(key=lambda d: (d["line"], _SEV_ORDER.get(d["level"], 9)))
    return merged


def _counts(defects: list[dict]) -> dict:
    return {
        "total": len(defects),
        "high": sum(1 for d in defects if d["level"] == "high"),
        "mid": sum(1 for d in defects if d["level"] == "mid"),
        "low": sum(1 for d in defects if d["level"] == "low"),
    }


def run_review(code: str, language: str = "javascript", ruleset: str = "local"):
    """返回 (defects, counts, duration_ms, rule_findings, llm_used)"""
    start = time.time()

    # 1. 规则引擎
    rule_defects, _, _, rule_findings = semgrep.run_review(code, language, ruleset)

    # 2. RAG：为规则缺陷附上参考修复代码 + CWE，并检索案例供 LLM 参考
    rag.enhance(rule_defects)
    rag_cases = rag.cases_for_llm(rule_defects)

    # 3. LLM 深度分析（未配置则跳过）
    llm_defects, llm_used = llm_analyze(code, language, rule_defects, rag_cases)

    # 4. 融合去重
    defects = _merge(rule_defects, llm_defects)
    counts = _counts(defects)
    duration_ms = int((time.time() - start) * 1000)

    return defects, counts, duration_ms, rule_findings, llm_used
