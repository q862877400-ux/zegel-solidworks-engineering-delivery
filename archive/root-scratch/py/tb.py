import os, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
ROOTS = [r"C:\Program Files\SOLIDWORKS Corp",
         r"C:\Program Files (x86)\SOLIDWORKS Corp",
         r"C:\ProgramData\SolidWorks",
         r"C:\Users\Zegel\AppData\Roaming\SolidWorks",
         r"C:\Users\Zegel\AppData\Local\SolidWorks",
         r"C:\Users\Zegel\Documents\SOLIDWORKS"]
PAT = ("toolbox", "swbox", "standard part", "library", "sldlib")
found = []
for root in ROOTS:
    if not os.path.isdir(root):
        print("  (无) %s" % root); continue
    for d, dn, fn in os.walk(root):
        dl = d.lower()
        if any(p in dl for p in PAT):
            found.append(("DIR ", d))
        for f in fn:
            fl = f.lower()
            if any(p in fl for p in PAT) or fl.endswith((".swbox", ".sldlib", ".sldprt")):
                found.append(("FILE", os.path.join(d, f)))
    print("  (扫过) %s" % root)
print()
print("=== 命中 %d 项 ===" % len(found))
for kind, p in found[:40]:
    try: sz = os.path.getsize(p) if kind == "FILE" else 0
    except Exception: sz = 0
    print("  %s %-96s %d" % (kind, p[:96], sz))