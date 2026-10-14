"""冒烟测试：RAG 检索 + 审查流水线（未配置 LLM key 时自动跳过 LLM）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.engine import rag, pipeline  # noqa: E402
from app.engine.llm_analyzer import is_enabled  # noqa: E402

SMOKE = Path(__file__).resolve().parent / "smoke"

# 1. RAG 检索：查询「SQL 注入」应命中 CWE-89
cases = rag._engine.search("SQL 注入 字符串拼接 攻击者")
print("1. RAG 检索「SQL 注入」→ top:", [c["cwe"] for c in cases])
assert cases and cases[0]["cwe"] == "CWE-89"

# 2. 流水线（LLM 未配置时 llm_used=False）
code = (SMOKE / "test.js").read_text(encoding="utf-8")
defects, counts, duration, raw, llm_used = pipeline.run_review(code, "javascript")
print(f"\n2. 流水线：缺陷 {counts['total']} 处（高 {counts['high']}/中 {counts['mid']}/低 {counts['low']}），llm_used={llm_used}")
print(f"   LLM 是否已配置：{is_enabled()}")
for d in defects:
    extra = f"  code={len(d.get('code',''))}字符" if d.get("code") else ""
    print(f"   L{d['line']:>3} [{d['level']:>4}] [{d.get('source')}] {d['title']}{extra}")

# 3. 校验 RAG 已给规则缺陷附上参考修复代码
assert any(d.get("code") for d in defects), "RAG 未附加修复代码"
assert all("source" in d for d in defects), "缺陷缺少 source 字段"
print("\n✅ RAG 检索 + 流水线融合 通过（LLM 需配置 DEEPSEEK_API_KEY 后启用）")
