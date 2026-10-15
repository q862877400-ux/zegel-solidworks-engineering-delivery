import json, sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
c = Counter()
for p in d["parts"]:
    for cat in (p["category"] or ["(无)"]):
        c[cat] += 1
print("库里的分类（按型号数）:")
for cat, n in c.most_common(28):
    print("   %-18s %5d" % (cat, n))