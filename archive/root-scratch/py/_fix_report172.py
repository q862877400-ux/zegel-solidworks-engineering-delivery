import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\harvest-report.md")
t = P.read_text(encoding="utf-8")
NEW = "> 偏离上游：329 个文件 / +152,575 行 / -332 行 · 289 个 commit · 工作区 clean"
m = re.search(r"(?m)^> 偏离上游：.*$", t)
assert m
print("  改前: %s" % m.group(0))
P.write_text(t[:m.start()] + NEW + t[m.end():], encoding="utf-8")
print("  改后: %s" % NEW)
