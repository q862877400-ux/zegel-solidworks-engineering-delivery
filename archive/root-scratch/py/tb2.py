import os, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
BASE = Path(r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\design library")
print("=== design library 顶层 ===")
for d in sorted(BASE.iterdir()):
    n = len(list(d.rglob("*"))) if d.is_dir() else 1
    print("  %-30s %s" % (d.name, ("%d 项" % n) if d.is_dir() else "文件"))
print()
print("=== 你问的：丝杆 / 导轨 / 型材 ===")
KEY = ("ballscrew","ball_screw","screw","linear","guide","rail","profile",
       "extrusion","aluminum","aluminium","optical","bearing","nut","support")
hits = {}
for d, dn, fn in os.walk(BASE):
    for f in fn:
        fl = f.lower()
        if any(k in fl for k in KEY):
            cat = Path(d).name
            hits.setdefault(cat, []).append(f)
for cat, fs in sorted(hits.items()):
    print("  【%s】%d 个" % (cat, len(fs)))
    for f in sorted(fs)[:6]:
        print("     " + f)