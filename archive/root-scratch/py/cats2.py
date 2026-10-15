import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
for cat in ("机床防护罩","轴承附件","导轨","丝杆","型材","联轴器","带轮","皮带"):
    hits = [p for p in d["parts"] if cat in (p["category"] or [])]
    print("【%s】%d 个" % (cat, len(hits)))
    for h in hits[:5]:
        print("    %-22s %-44s" % (h["code"][:20], h["product"][:42]))
    print()