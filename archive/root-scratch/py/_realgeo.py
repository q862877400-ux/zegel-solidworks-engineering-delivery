import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
def com(n): return re.sub(r"^(get|set)_", "", n)
for iface in ("IDimensionTolerance", "IMate2", "ISurface"):
    m = re.search(r"(?ms)^## %s\r?\n(.*?)(?=\r?\n## |\z)" % iface, sw)
    if not m: print("### %s 不存在" % iface); continue
    print("###", iface)
    seen = set()
    for l in m.group(1).splitlines():
        h = SIG.match(l.strip())
        if not h: continue
        n = com(h.group(1))
        if n in seen or re.match(r"^I[A-Z][a-z]", n): continue
        seen.add(n)
        ps = [a.strip() for a in h.group(2).split(",") if a.strip()]
        real = len([a for a in ps if not a.endswith("&")])
        if any(k in n.lower() for k in ("min","max","type","name","format","scope","adjacent","toler","value")):
            print("    %-34s %d 参" % (n, real))
