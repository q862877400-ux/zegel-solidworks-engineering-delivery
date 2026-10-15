import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
d = json.loads((R / "capabilities.yaml").read_text(encoding="utf-8"))
for cid in ("surface_modeling", "mold_tools"):
    for c in d["capabilities"]:
        if c.get("id") != cid:
            continue
        print("══ %s（%s）" % (cid, c.get("label")))
        print("   level=%s · backends=%s · verified_versions=%s"
              % (c.get("level"), c.get("backends"), c.get("verified_versions")))
        print("   evidence: %s" % (c.get("evidence") or "**（空）**"))
        print("   limitations %d 条：" % len(c.get("limitations") or []))
        for i, s in enumerate((c.get("limitations") or [])[:4], 1):
            print("     %d) %s" % (i, str(s)[:260]))
        print()
