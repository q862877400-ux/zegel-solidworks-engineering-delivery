import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
for kw in ("齿轮","齿条"):
    hits=[p for p in d["parts"] if kw in (p["category"] or [])]
    print("【%s】%d 个: %s" % (kw, len(hits), [h["code"] for h in hits[:6]]))