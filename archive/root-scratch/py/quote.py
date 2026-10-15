import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
src = Path(r"C:\swprojects\_tmp_mcp\pywin32_adapter.py").read_text(encoding="utf-8")
lines = src.splitlines()
def blk(a, b, title):
    print("=== %s (行 %d-%d) ===" % (title, a, b))
    for i in range(a-1, min(b, len(lines))):
        print("  %5d| %s" % (i+1, lines[i].rstrip()[:120]))
    print()
blk(62, 100, "① by-ref VARIANT 怎么造 + 0x80020005")
blk(255, 305, "② 启动顺序：为什么必须 dynamic.Dispatch")