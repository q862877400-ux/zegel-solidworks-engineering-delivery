import json
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"D:\AI\SW\output\zero-arg-method-callsites.json").read_text(encoding="utf-8"))
danger = d["danger"]
#: **会改东西**的前缀（有界词表；只用来**缩清单**，不当作判据 —— 见事实 74/76）
MUT = ("Insert", "Add", "Delete", "Remove", "Create", "Set", "Run", "Update",
       "Mesh", "Scale", "Start", "Stop", "Save", "Close", "Open", "Edit", "Modify",
       "Rebuild", "Redraw", "Zoom", "Clear", "Reset", "Apply", "Execute", "Load",
       "Write", "Export", "Import", "Refresh", "Select", "Activate", "Break", "Merge")
hot = [x for x in danger if str(x[2]).startswith(MUT)]
print("  危险总数 %d ⇒ 其中**名字像"改东西"**的: **%d**" % (len(danger), len(hot)))
print()
seen = {}
for f, ln, m in hot:
    seen.setdefault(m, []).append((f, ln))
for m, ss in sorted(seen.items()):
    print("  %-30s %d 处   %s" % (m, len(ss), ", ".join("%s:%d" % (a.split(chr(92))[-1], b) for a, b in ss[:4])))
print()
print("  ⚠ **这只是"缩清单"**（按名字前缀）—— 逐条要人工看（事实 74/76）。")
print("  ⚠ 而**真正危险**的是其中之一小撮：**零参 + 有副作用**。")
