import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\t2.py")
s = p.read_text(encoding="utf-8")
s = s.replace('m.is_swp_macro(b"\\xd0\\xcf\\x11\\xe0\\xa1\\xb1\\x1a\\xe1"+"j")',
              'm.is_swp_macro(b"\\xd0\\xcf\\x11\\xe0\\xa1\\xb1\\x1a\\xe1" + b"junk")')
p.write_text(s, encoding="utf-8")
print("fixed")