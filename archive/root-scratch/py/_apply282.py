import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
data = json.loads(Path(r"D:\AI\SW\_promote282.json").read_text(encoding="utf-8"))
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "costing_templates_and_defaults")
x["level"] = "verified"
if not x.get("verified_versions"):
    x["verified_versions"] = ["2026"]
x["evidence"] = data["evidence"]
x["limitations"] = data["limitations"]
for cid in ("costing_readback", "costing"):
    y = next((z for z in d["capabilities"] if z["id"] == cid), None)
    if y is None:
        continue
    lim = list(y.get("limitations") or [])
    if not any("GetTemplatePathnames" in t for t in lim):
        lim.insert(0, data["note_for_others"])
    y["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
vf = sum(1 for z in d["capabilities"] if z.get("level") == "verified")
st = sum(1 for z in d["capabilities"] if z.get("level") == "stitched")
print("  ok · verified=%d stitched=%d" % (vf, st))
