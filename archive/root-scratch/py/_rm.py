import io, re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_drawing_view.py")
s = p.read_text(encoding="utf-8")
s = re.sub(r'^\s*"get_orient_toward",\s*\n', '', s, flags=re.M)
p.write_text(s, encoding="utf-8")
print("  [ok] 已从 __all__ 移除 get_orient_toward" if "get_orient_toward" not in s.split("__all__")[1][:600] else "  检查 __all__")
