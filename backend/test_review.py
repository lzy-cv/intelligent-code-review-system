"""冒烟测试：直接调用审查引擎（无需启动服务），用 smoke 下的示例代码验证"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.engine import semgrep  # noqa: E402

SMOKE = Path(__file__).resolve().parent / "smoke"

for name, lang in [("test.js", "javascript"), ("test.py", "python")]:
    code = (SMOKE / name).read_text(encoding="utf-8")
    defects, counts, duration, raw = semgrep.run_review(code, lang)
    print(f"\n[{name}] 缺陷 {counts['total']} 处（高 {counts['high']} / 中 {counts['mid']} / 低 {counts['low']}），耗时 {duration}ms，原始命中 {raw} 条")
    for d in defects:
        print(f"  L{d['line']:>3} [{d['level']:>4}] {d['title']}  ({d['rule_id']})")
