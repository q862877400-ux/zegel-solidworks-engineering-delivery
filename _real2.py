import sys, io, re, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
for fam, pat in (("ISheet", r"Size|Width|Height|Name|Scale|Count"),
                 ("IAnnotation", r"Visible|Drawn|Leader|Position|Type|BOM"),
                 ("IAnnotation", r"^Get")):
    print("### %s  /%s/" % (fam, pat))
    for it in reg[fam]["members"]:
        if re.search(pat, it["name"], re.I):
            print("    %-42s %d" % (it["name"], it["arity"]))
    print("    -- 属性 --", ", ".join(reg[fam]["properties"][:14]))
