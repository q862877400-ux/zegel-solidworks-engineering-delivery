import sys, io, re, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
for fam, pat in (("IDisplayDimension", r"Text|Value|Format"),
                 ("ITableAnnotation", r"Text|Cell|Row|Column"),
                 ("ISheet", r"Size|Width|Height|Name|Scale"),
                 ("IAnnotation", r"Visible|Drawn|Leader|Position|Type")):
    print("### " + fam)
    items = reg[fam]
    for it in items["members"]:
        if re.search(pat, it["name"], re.I):
            print("    %-42s %d" % (it["name"], it["arity"]))
    print("    -- 属性 --")
    for p in items["properties"]:
        if re.search(pat, p, re.I):
            print("    %s" % p)
