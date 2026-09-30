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
            if m and not re.match(r"^I[A-Z][a-z]", m.group(1)):
                out[com(m.group(1))] = (m.group(1), len([a for a in m.group(2).split(",") if a.strip()]))
    return out
print("### ISectionViewData 全部非内部成员")
for n,(r,a) in sorted(blk("ISectionViewData").items())[:12]:
    print("    %-30s 反射原名 %-30s %d 参" % (n, r, a))
print("### IModelViewManager 的 SnapShot 相关")
for n,(r,a) in sorted(blk("IModelViewManager").items()):
    if "snap" in n.lower():
        print("    %-30s 反射原名 %-30s %d 参" % (n, r, a))
print("### 五个表注解族全部非内部成员")
for f in ("IHoleTableAnnotation","IBendTableAnnotation","IFamilyTableAnnotation",
          "IGeneralTableAnnotation","IGeneralToleranceTableAnnotation"):
    print("   ", f)
    for n,(r,a) in sorted(blk(f).items()):
        print("       %-32s 反射原名 %-32s %d 参" % (n, r, a))
