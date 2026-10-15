import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\signature-audit.md")
t = P.read_text(encoding="utf-8")
OLD = "| `sw_simulation.py` | 44 | **44** | 0 | 0 |"
NEW = "| `sw_simulation.py` | 45 | **45** | 0 | 0 |"
if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok sw_simulation 44 → 45")
else:
    m = re.search(r"(?m)^\| `sw_simulation\.py`.*$", t)
    print("  实际那一行: %r" % (m.group(0) if m else "找不到"))
    if m:
        row = m.group(0)
        #: 把第一个数字列改成 45
        nums = re.findall(r"\d+", row)
        new_row = row.replace(nums[0], "45", 1)
        P.write_text(t.replace(row, new_row, 1), encoding="utf-8")
        print("  ok 已改成: %s" % new_row)
