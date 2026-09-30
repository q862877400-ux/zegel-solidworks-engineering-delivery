import json, sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
fm = {i["name"] for i in reg["IFeatureManager"]["members"]}
dd = {i["name"] for i in reg["IDrawingDoc"]["members"]}
fmp = set(reg["IFeatureManager"]["properties"]); ddp = set(reg["IDrawingDoc"]["properties"])
print("  IFeatureManager 候选：")
for n in ("FeatureCount","GetSolidFeatureCount","GetSurfaceFeatureCount","DefinitionTemplate","GetDefinition","InsertFeatureTreeNode2"):
    print("    %-26s %s" % (n, "✓" if n in fm or n in fmp else "❌"))
print("  IDrawingDoc 候选：")
for n in ("GetPathName","GetTitle","GetSheetCount","GetCurrentSheet","GetFirstView","GetSheetNames","GetSheetCount"):
    print("    %-26s %s" % (n, "✓" if n in dd or n in ddp else "❌"))
print("  IFeatureManager 里含 Count/Feature 的（找证据回读该用什么）：")
for n in sorted(fm):
    if re.search(r"Count$|Definition|Template", n): print("    " + n)
print("  IDrawingDoc 里含 Sheet/View/Path 的：")
for n in sorted(dd):
    if re.search(r"Sheet|View|Path|Title", n): print("    " + n)
