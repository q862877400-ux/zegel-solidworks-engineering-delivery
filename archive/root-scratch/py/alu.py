import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
for kw in ("铝型材", "欧标", "4040"):
    hits = [p for p in d["parts"] if kw in p["product"] or kw in p["name"]]
    print("【%s】%d 个" % (kw, len(hits)))
    for h in hits[:6]:
        print("   %-24s %-46s %s" % (h["code"][:22], h["product"][:44], (h["category"] or [""])[0][:10]))
    print()