import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\harvest-report.md")
t = P.read_text(encoding="utf-8")
m = re.search(r"(?m)^> 偏离上游：.*$", t)
assert m, "找不到那行"
NEW = "> 偏离上游：292 个文件 / +146,468 行 / -317 行 · 260 个 commit · 工作区 clean"
t = t[:m.start()] + NEW + t[m.end():]
#: 顺带同步"轮 N 实测"那一行的数字（若有）
t = re.sub(r"(> 轮 \d+ 实测：\s+)292 个文件 / \+146,468 行 / -317 行 · 260 个 commit( · )?",
           r"\g<1>292 个文件 / +146,468 行 / -317 行 · 260 个 commit\g<2>", t)
P.write_text(t, encoding="utf-8")
print("  ok 已按门禁给的数更新")
print("     %s" % NEW)
