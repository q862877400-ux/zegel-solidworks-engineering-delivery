import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml").read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("level") == "stitched":
        print("── %s（%s）" % (c.get("id"), c.get("label")))
        print("   backends=%s · verified_versions=%s" % (c.get("backends"), c.get("verified_versions")))
        ev = c.get("evidence") or []
        print("   evidence %d 条:" % len(ev))
        for s in ev[:3]:
            print("      · %s" % str(s)[:150])
        lim = c.get("limitations") or []
        print("   limitations 第 1 条: %s" % (str(lim[0])[:160] if lim else "（无）"))
        print()
