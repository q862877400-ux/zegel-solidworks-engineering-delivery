import sys, io, re, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
for k in ("ISweepFeatureData","ILoftFeatureData","IBoundaryBossFeatureData","IMidSurface3",
          "IRevolveFeatureData2","IChainPatternFeatureData","IFace2","IBody2"):
    i = reg[k]
    print("### %-28s 原始%4d I%3d 属%3d 方%4d" % (k, i["raw_members"],
          i["internal_dispatch"], i["property_count"], i["method_count"]))
    names = [x["name"] for x in i["members"]]
    for n in names[:6]: print("      " + n)
    print("      属性: " + ", ".join(i["properties"][:8]))
