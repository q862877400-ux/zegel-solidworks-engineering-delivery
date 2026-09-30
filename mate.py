import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    t = p.read_text(encoding="utf-8", errors="replace")
    cur = None
    for l in t.splitlines():
        if l.startswith("## "): cur = l[3:].strip()
        elif cur and re.match(r"^\s*\S+\s+AddMate\d?\s*\(", l):
            m = re.match(r"^\s*\S+\s+(AddMate\d?)\s*\((.*)\)\s*$", l)
            ps = [a.strip() for a in m.group(2).split(",") if a.strip()]
            print("  %-22s %-24s %d 参" % (p.name[:20], cur, len(ps)))