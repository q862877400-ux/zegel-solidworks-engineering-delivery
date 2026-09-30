import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_geometry.py")
s = p.read_text(encoding="utf-8")
s = s.replace('get_com_member(tolerance, "GetFitType")', 'get_com_member(tolerance, "FitType")')
s = s.replace('#     Int32   GetFitType() / Type()               ← 零参方法',
              '#     Int32   FitType() / Type()                  ← 零参方法')
p.write_text(s, encoding="utf-8")
print("  [ok] GetFitType -> FitType")
