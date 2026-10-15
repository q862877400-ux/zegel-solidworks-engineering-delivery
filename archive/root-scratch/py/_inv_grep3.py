import re, io
from pathlib import Path
ROOT = Path(r"D:\AI\SW")
o = io.StringIO()
def show(rel, lo, hi, label):
    p = ROOT/rel
    if not p.is_file():
        o.write("### %s -> MISSING %s\n" % (label, rel)); return
    ls = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    o.write("\n### %s  (%s lines %d-%d)\n" % (label, rel, lo, hi))
    for i in range(max(0,lo-1), min(len(ls), hi)):
        o.write("%5d| %s\n" % (i+1, ls[i]))
# our projected curve
show("scripts/sw_curve_and_split.py", 1, 60, "OUR projected curve header")
# our bodies list function
p = ROOT/"scripts/sw_feature_entry_ops.py"
ls = p.read_text(encoding="utf-8", errors="ignore").splitlines()
o.write("\n### sw_feature_entry_ops.py public defs\n")
for i,l in enumerate(ls,1):
    if re.match(r"^def ", l): o.write("%5d| %s\n" % (i,l))
# grep fold / plane / bodies across scripts
for pat,label in [(r"SheetMetalFold|InsertSheetMetalFold|CreateFold","FOLD-API"),
                  (r"HideAllPlanes|ShowAllPlanes|HidePlane|ShowPlane","PLANE-VIS-API"),
                  (r"^def .*bod","BODIES-DEF"),
                  (r"InsertProjectedSketch2|InsertProjectedSketch","PROJCURVE-API")]:
    rx = re.compile(pat, re.M)
    o.write("\n### grep %s (%s)\n" % (pat,label))
    for f in sorted(list((ROOT/"scripts").glob("sw_*.py")) + list((ROOT/"mcp-server").glob("tool_specs_*.py"))):
        for i,l in enumerate(f.read_text(encoding="utf-8",errors="ignore").splitlines(),1):
            if rx.search(l):
                o.write("  %s:%d: %s\n" % (f.name,i,l.strip()[:150]))
open(r"D:\AI\SW\_inv_grep3.txt","w",encoding="utf-8").write(o.getvalue())
print("ok")
