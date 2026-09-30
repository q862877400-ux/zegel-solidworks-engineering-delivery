import json, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.json").read_text(encoding="utf-8"))
tot = 0; fams = 0
for r in d:
    miss = r.get("missing_members") or []
    if miss:
        fams += 1; tot += len(miss)
        print("  %-34s %s" % (r["family"], ", ".join(miss[:6])))
print("未命中族 %d / 成员 %d" % (fams, tot))
