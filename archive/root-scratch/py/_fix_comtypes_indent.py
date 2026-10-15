import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
# 找出打印段的缩进，并修 L283-286
for i, l in enumerate(lines, 1):
    if "comtypes 明细" in l:
        indent = len(l) - len(l.lstrip())
        print("  L%-4d 缩进 %d: %s" % (i, indent, l.strip()[:60]))
        # 重写成单行（避免缩进问题）
        lines[i - 1] = " " * indent + 'print("── comtypes 明细（**不是缺陷**，是有依据的单独归类）──")\n'
        lines[i] = " " * (indent + 4) + "for lineno, member, argc, reason in comtypes:\n"
        lines[i + 1] = " " * (indent + 8) + 'print(f"  {target}:{lineno}  {member}() 实参 {argc} —— {reason[:110]}")\n'
        break
t = "".join(lines)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
