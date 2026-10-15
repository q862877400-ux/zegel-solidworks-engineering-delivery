import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
# 重写 L282..L287（1 基）
NEW = [
    "    if comtypes:\n",
    '        print("── comtypes 明细（**不是缺陷**，是有依据的单独归类）──")\n',
    "        for lineno, member, argc, reason in comtypes:\n",
    '            print(f"  {target}:{lineno}  {member}() 实参 {argc} —— {reason[:110]}")\n',
    "        print()\n",
    "    if doubt:\n",
    '        print("── 存疑明细 ──")\n',
]
lines[281:287] = NEW
t = "".join(lines)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
for i in range(279, 296):
    print("  L%-4d |%s|" % (i + 1, t.splitlines()[i][:92]))
