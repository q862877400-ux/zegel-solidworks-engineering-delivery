import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
m = re.search(r"(?ms)^## IAnnotationView\r?\n(.*?)(?=\r?\n## |\z)", txt)
lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
print("IAnnotationView 段行数 =", len(lines))
for l in lines:
    if "Annotation" in l or "Activate" in l:
        print("   ", l)
print()
print("GetBuildNumbers 原文：")
for iface in ("ISldWorks",):
    mm = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % iface, txt)
    for l in mm.group(1).splitlines():
        if "GetBuildNumbers" in l:
            print("   ", l.strip())
