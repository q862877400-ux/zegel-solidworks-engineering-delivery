import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
def seg(n):
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % n, c)
    return m.group(1) if m else None
for name in ("ISectionViewData", "IAnnotationView", "IModelViewManager",
             "ITableAnnotation", "IBomTableAnnotation", "ITableAnnotationParameters"):
    b = seg(name)
    if b is None:
        print("### %-28s ** 不在 sldworks 反射里 **" % name); continue
    lines = [l.strip() for l in b.splitlines() if l.strip()]
    meth = [l for l in lines if re.match(r"^\S+\s+\w+\s*\(", l) and not re.search(r"\bI[A-Z][a-z]", l)]
    prop = [l for l in lines if re.search(r"\b(get_|set_)\w+", l)]
    print("### %-28s 原始 %3d / 方法 %3d / 属性 %3d" % (name, len(lines), len(meth), len(prop)))
    for l in meth[:7]: print("      ", l)
