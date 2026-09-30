import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
print("=== ① 我的 12 份索引里有没有 Toolbox / 标准件机制 ===")
tot = 0
for p in sorted(Path(r"C:\swprojects\sw-skill-fork\scripts").glob("sw_api_*.py")):
    t = p.read_text(encoding="utf-8")
    hits = sorted(set(re.findall(r"^        '(\w*(?:Toolbox|ToolBox|Component5?|GetBoxItem|SnapPoint|AddComponent)\w*)'", t, re.M)))
    if hits:
        print("  %-24s %s" % (p.stem, ", ".join(hits[:10])[:110]))
        tot += len(hits)
print("  命中成员名合计:", tot)
print()
print("=== ② 本机有没有 Toolbox 数据（标准件库本体）===")
import os
for root in (r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS",
             r"C:\ProgramData\SolidWorks"):
    if not os.path.isdir(root): continue
    for d, dn, fn in os.walk(root):
        low = d.lower()
        if "toolbox" in low or any("toolbox" in f.lower() for f in fn[:40]):
            print("  ", d)
            if len(d) > 200: break