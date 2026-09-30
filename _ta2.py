import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
for n in ("IHoleTableAnnotation", "IBendTableAnnotation", "IFamilyTableAnnotation",
          "IGeneralTableAnnotation", "IGeneralToleranceTableAnnotation",
          "ITableAnnotation"):
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % n, c)
    if not m:
        print("### %s NOT FOUND" % n); continue
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
    print("### %s (%d)" % (n, len(lines)))
    for l in lines:
        if re.match(r"^\S+\s+\w+\s*\(", l) and not re.search(r"\bI[A-Z][a-z]", l):
            print("   ", l)
