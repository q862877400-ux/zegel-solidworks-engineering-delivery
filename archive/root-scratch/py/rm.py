import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    cur = None
    for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("## "): cur = l[3:].strip()
        elif cur and re.match(r"^\s*\S+\s+RunMacro\d?\s*\(", l.strip()):
            sig = re.match(r"^\s*(\S+)\s+(\w+)\s*\((.*)\)\s*$", l.strip())
            ps = [a.strip() for a in sig.group(3).split(",") if a.strip()]
            print("  %-16s %-12s %2d 参 / by-ref: %s" % (
                p.name[:16], sig.group(2), len(ps),
                [a for a in ps if a.endswith("&")] or "无"))