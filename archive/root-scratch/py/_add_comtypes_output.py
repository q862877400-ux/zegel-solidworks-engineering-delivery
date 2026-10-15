import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_call_arity.py")
t = P.read_text(encoding="utf-8")

OLD = '''    print(f"  通过     {len(ok)}")
    print(f"  存疑     {len(doubt)}   ← 同名成员存在但 arity 全对不上")'''
NEW = '''    print(f"  通过     {len(ok)}")
    # ⚑ 轮 130：`comtypes` 早绑定站点**单独报**（本工具的 arity 规则是在 pywin32 上量的）
    print(f"  comtypes {len(comtypes)}   ← **本工具判不了**（早绑定自行分配 [out]）")
    print(f"  存疑     {len(doubt)}   ← 同名成员存在但 arity 全对不上")'''
assert OLD in t, "输出锚点不符"
t = t.replace(OLD, NEW, 1)

# 明细段
OLD2 = '''    print("── 存疑明细 ──")'''
NEW2 = '''    if comtypes:
        print("── comtypes 明细（**不是缺陷**，是有依据的单独归类）──")
        for lineno, member, argc, reason in comtypes:
            print(f"  {target}:{lineno}  {member}() 实参 {argc} —— {reason[:110]}")
    print("── 存疑明细 ──")'''
assert OLD2 in t, "明细锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已加 comtypes 输出段")
