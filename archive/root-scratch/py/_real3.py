import sys, io, re, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
for fam, pat in (("IFace2", r"Normal|Surface|Param|Curve|Loop"),
                 ("IBody2", r"Type|Volume|SurfaceArea|Mass|Count|Name")):
    print("### " + fam)
    for it in reg[fam]["members"]:
        if re.search(pat, it["name"], re.I):
            print("    %-40s %d" % (it["name"], it["arity"]))
    print("    -- attrs --", ", ".join(reg[fam]["properties"][:12]))
