import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
#: ① 冒烟改成用**清单内**的 tol_type
P = R / "tools" / "verify_gtol_smoke.py"
t = P.read_text(encoding="utf-8")
n = 0
for old, new in (
    ('tol_type="position"', 'tol_type="parallelism"'),      #: 22 ∈ 允许清单
    ('tol_type="flatness"', 'tol_type="perpendicularity"'),  #: 21 ∈ 允许清单
):
    if old in t:
        t = t.replace(old, new)
        n += 1
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  冒烟里改了 %d 处 tol_type" % n)
for i, l in enumerate(t.splitlines(), 1):
    if "tol_type=" in l:
        print("    L%-4d %s" % (i, l.strip()[:96]))
