import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
def com(n): return re.sub(r"^(get|set)_", "", n)
for iface in ("IView", "IModelView"):
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % iface, sw)
    if not m: continue
    print("###", iface)
    seen = set()
    for l in m.group(1).splitlines():
        h = SIG.match(l.strip())
        if not h: continue
        n = com(h.group(1))
        if n in seen or re.match(r"^I[A-Z][a-z]", n): continue
        seen.add(n)
        if any(k in n.lower() for k in ("scale","orient","decimal","decimalplaces","vieworient")):
            ps=[a.strip() for a in h.group(2).split(",") if a.strip()]
            print("    %-36s %d 参" % (n, len([a for a in ps if not a.endswith("&")])))
