import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
t = {i["name"]: i["arity"] for i in reg["IFeatureManager"]["members"]}
for n in ("FeatureExtrusion","FeatureExtrusion2","FeatureExtrusion3","FeatureCut4","FeatureCut"):
    print("    %-22s %s" % (n, t.get(n, "❌ 不在表里")))
