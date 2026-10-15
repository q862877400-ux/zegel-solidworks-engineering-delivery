import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

#: ⚠⚠⚠ **修第二个判据缺陷**（轮 173）：`_prop` / `_count` 这类**辅助函数**里，
#: `owner` 是**形参**，静态推不出接口 ⇒ 我第一版让它落到 `IObject` 兜底
#: ⇒ ★ **兜底值 `IObject` 必然不在成员的接口谱系里** ⇒ **必报** ⇒ **假阳性**。
#: ★ 修法：**推不出接口就留白**（`None`）⇒ 那一处**不检查**（宁少报，不假报）。
OLD = '''                owner_iface = None
                if isinstance(owner, ast.Name):
                    owner_iface = var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    owner_iface = var_iface.get(owner.attr)
                if not owner_iface:
                    continue
                #: ★ 由「持有者接口 + 成员名」查**返回类型** ⇒ 变量的接口'''
NEW = '''                owner_iface = None
                if isinstance(owner, ast.Name):
                    owner_iface = var_iface.get(owner.id)
                elif isinstance(owner, ast.Attribute):
                    owner_iface = var_iface.get(owner.attr)
                #: ★★ 推不出接口 ⇒ **留白**（**不许**落到 `IObject` 兜底 —— 那必然误报）
                if not owner_iface or owner_iface == "IObject":
                    continue
                #: ★ 由「持有者接口 + 成员名」查**返回类型** ⇒ 变量的接口'''
assert OLD in t, "锚点1不符"
t = t.replace(OLD, NEW, 1)

OLD2 = '''                if not oiface:
                    continue
                checked += 1'''
NEW2 = '''                #: ★★ 同上：**推不出就别检查**（兜底值会造成假阳性）
                if not oiface or oiface == "IObject":
                    continue
                checked += 1'''
assert OLD2 in t, "锚点2不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已修（推不出接口 ⇒ 留白，不兜底）")
