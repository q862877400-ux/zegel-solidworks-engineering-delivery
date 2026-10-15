import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_composite_curve_smoke.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
for i, l in enumerate(lines):
    if '"能不能建成"仍未查明' in l:
        lines[i] = l.replace('"能不能建成"', "「能不能建成」")
        print("  L%d 已修" % (i + 1))
P.write_text("".join(lines), encoding="utf-8")
ast.parse("".join(lines))
print("  语法 OK")
