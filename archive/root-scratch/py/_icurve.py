import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
def com(n): return re.sub(r"^(get|set)_", "", n)
m = re.search(r"(?ms)^## ICurve\r?\n(.*?)(?=\r?\n## |\z)", sw)
seen=set()
print("### ICurve 里与「类型判断」相关的成员")
for l in m.group(1).splitlines():
    h = SIG.match(l.strip())
    if not h: continue
    n = com(h.group(1))
    if n in seen or re.match(r"^I[A-Z][a-z]", n): continue
    seen.add(n)
    if any(k in n.lower() for k in ("type","is","arc","spline","line","circle","period","closed")):
        ps=[a.strip() for a in h.group(2).split(",") if a.strip()]
        print("    %-32s %d 参" % (n, len([a for a in ps if not a.endswith("&")])))
