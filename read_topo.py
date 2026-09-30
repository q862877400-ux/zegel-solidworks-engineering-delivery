import re, sys, html
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
def text(p):
    s = p.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S|re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return "\n".join(l.strip() for l in s.splitlines() if l.strip())
for name in ("c_topology_optimization_disk_brake.htm", "t_creating_topology_study.htm"):
    print("=" * 70)
    print("### %s" % name)
    print("=" * 70)
    print(text(Path(r"C:\topo_en") / name))
    print()