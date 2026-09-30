import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
def com(n): return re.sub(r"^(get|set)_", "", n)
def blk(iface):
    cur, out = None, {}
    for raw in txt.splitlines():
        if raw.startswith("## "):
            if cur == iface: break
            cur = raw[3:].strip()
            if cur == iface: out = {}
        elif cur == iface and raw.strip():
            m = SIG.match(raw.strip())
            if m:
                nm = m.group(1)
                out[com(nm)] = (nm, len([a for a in m.group(2).split(",") if a.strip()]))
    return out
want = {
 "IModelDocExtension": ["CustomProperty", "PersistReference", "RunCommand", "Rebuild", "MassProperties"],
 "ISectionViewData": ["Selection", "Features", "Bodies", "Components"],
 "IAnnotationView": ["Count", "Annotations", "Activate"],
 "IModelViewManager": ["SnapShot", "ActivateModel", "ActivateControl", "AddControl"],
 "IHoleTableAnnotation": ["HoleTable", "Sort"],
 "IBendTableAnnotation": ["BendTable"],
 "IFamilyTableAnnotation": ["FamilyTable", "Sheet"],
 "IGeneralTableAnnotation": ["GeneralTable", "Sort"],
 "IGeneralToleranceTableAnnotation": ["GeneralToleranceTable"],
}
for iface, pats in want.items():
    print("###", iface)
    b = blk(iface)
    for name, (raw, ar) in sorted(b.items()):
        if any(p.lower() in name.lower() for p in pats):
            print("    COM名 %-34s 反射原名 %-36s %d 参" % (name, raw, ar))
