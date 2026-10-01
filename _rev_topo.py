import json,re
from pathlib import Path
d = json.loads(Path(r"D:/AI/SW/output/orphan-capabilities.json").read_text(encoding="utf-8"))
rows = d["orphans"]
from collections import Counter
c = Counter(r["module"] for r in rows if r["first_param_is_injectable"])
print("top modules by injectable orphans (now):")
for m, n in c.most_common(8):
    print("   %-34s %d" % (m, n))
print()
print("sw_topology injectable orphans now:", [r["function"] for r in rows if r["module"]=="sw_topology.py" and r["first_param_is_injectable"]])
print()
# what the probe counts
print("counts block:", d["counts"])
