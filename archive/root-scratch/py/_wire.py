import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\scripts\release_check.py")
s = p.read_text(encoding="utf-8")
s = s.replace('    "scripts/check_diff_markers.py",\n',
              '    "scripts/check_diff_markers.py",\n    "scripts/check_member_names.py",\n', 1)
s = s.replace('        "diff_markers": markers,\n',
              '        "diff_markers": markers,\n        "member_names": member_names,\n', 1)
p.write_text(s, encoding="utf-8")
print("  [ok] 已登记 check_member_names.py 并把结果并入返回值")
