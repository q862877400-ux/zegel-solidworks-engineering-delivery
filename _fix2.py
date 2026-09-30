import re, sys, io
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_geometry.py")
s = p.read_text(encoding="utf-8")
# 定位 ISurface 段里这两行
lines = s.splitlines()
fam = None
fixed = 0
for i, line in enumerate(lines):
    fm = re.match(r"^\s{4}['\"](\w+)['\"]\s*:\s*\{", line)
    if fm: fam = fm.group(1)
    if fam != "ISurface": continue
    m = re.match(r"^(\s+['\"])(FindMinimumRadius|IntersectCurve)(['\"]\s*:\s*)(\d+)(,?\s*)$", line)
    if m:
        lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}2{m.group(5)}"
        print("  修正 %s: %s -> 2" % (m.group(2), m.group(4)))
        fixed += 1
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("共修", fixed)
