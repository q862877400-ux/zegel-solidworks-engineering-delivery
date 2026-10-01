import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\harvest-report.md")
t = P.read_text(encoding="utf-8")
m = re.search(r"(?m)^> 偏离上游：.*$", t)
assert m, "找不到那行"
NEW = "> 偏离上游：295 个文件 / +146,872 行 / -318 行 · 261 个 commit · 工作区 clean"
t = t[:m.start()] + NEW + t[m.end():]
P.write_text(t, encoding="utf-8")
print("  ✓ %s" % NEW)
