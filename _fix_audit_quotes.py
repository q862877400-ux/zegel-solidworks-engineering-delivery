import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\audit_get_com_member_semantics.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
for i, l in enumerate(lines):
    if "先试调一次" in l and "那条路" in l and l.lstrip().startswith("print("):
        lines[i] = '    print("    其中**无实参**（会走「先试调一次」那条路）: **%d**" % len(no_arg))\n'
        print("  L%d 已修" % (i + 1))
    if "属" in l and "查不到" in l and "铁律 5" in l:
        lines[i] = l.replace("属\u201c查不到\u201d", "属「查不到」").replace('属"查不到"', "属「查不到」")
        print("  L%d 已修（第二个）" % (i + 1))
P.write_text("".join(lines), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
