import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
def seg(n):
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % n, c)
    return m.group(1) if m else ""
def find(n, pat):
    out=[]
    for l in seg(n).splitlines():
        l=l.strip()
        if l and re.search(pat, l, re.I) and re.match(r"^\S+\s+\w+\s*\(", l):
            out.append(l)
    return out
print("### IModelDocExtension.SelectByID2 反射签名")
for l in find("IModelDocExtension", r"SelectByID2"): print("   ", l)
print("### IModelDocExtension.CustomProperty*")
for l in find("IModelDocExtension", r"CustomProperty"): print("   ", l)
print("### ClearSelection2 在哪个接口？")
for iface in ("IModelDoc2","IModelDocExtension","ISelectionMgr"):
    h = find(iface, r"ClearSelection2")
    if h: print("   %-20s %s" % (iface, h))
print("### IModelDoc2.Extension 属性")
for l in seg("IModelDoc2").splitlines():
    if "Extension" in l and ("get_" in l or "set_" in l): print("   ", l.strip())
print("### IModelDocExtension 上的 FeatureManager / MassProperties / SelectAll")
for pat in (r"FeatureManager", r"MassProperties", r"SelectAll", r"NeedsRebuild|EditRebuild3", r"GetWhatsWrong"):
    h = find("IModelDocExtension", pat)
    print("   %-24s %s" % (pat, h[:2] if h else "(无)"))
