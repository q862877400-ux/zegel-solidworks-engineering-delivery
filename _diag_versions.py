import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml").read_text(encoding="utf-8"))
print("  本机 SolidWorks RevisionNumber = 34.4.1 ⇒ **SW 2026 SP4.1**")
print("  capabilities.yaml 顶层声明: %s" % d.get("verified_versions"))
print()
groups = {}
for x in d["capabilities"]:
    groups.setdefault(tuple(x.get("verified_versions") or []), []).append((x["id"], x["level"]))
for k in sorted(groups, key=lambda t: (len(t), t)):
    print("  ── verified_versions = %-24s  %d 条" % (str(k), len(groups[k])))
    for i, lv in groups[k]:
        flag = ""
        if k == ("2024",):
            flag = "   ⚠ **只在 2024 验过，本机是 2026**"
        elif k == ():
            flag = "   ⚠ **没记版本**"
        print("      %-36s %-16s%s" % (i, lv, flag))
