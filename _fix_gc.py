import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\gate-classification.json")
t = P.read_text(encoding="utf-8")
bad = "`reflect\\enum_cosworks.txt`"
good = "`reflect/enum_cosworks.txt`"
if bad in t:
    t = t.replace(bad, good, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已把非法转义改成正斜杠")
d = json.loads(P.read_text(encoding="utf-8"))
print("  JSON OK · 登记 %d 条" % len(d["classification"]))
