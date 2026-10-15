import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
names = re.findall(r"^## (\w+)", c, re.M)
pats = ("TableAnnotation", "BomTable", "GeneralTable", "Table", "Equation", "Note")
hits = sorted({n for n in names if any(p.lower() in n.lower() for p in pats)})
print("候选表/注释类族 %d 个：" % len(hits))
for n in hits:
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % n, c)
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip()] if m else []
    meth = [l for l in lines if re.match(r"^\S+\s+\w+\s*\(", l) and not re.search(r"\bI[A-Z][a-z]", l)]
    print("  %-38s 成员 %3d / 方法 %3d" % (n, len(lines), len(meth)))
