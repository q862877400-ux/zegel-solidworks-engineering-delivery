import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''            bodies = asm.GetBodies2(0, False)      #: 0 = swSolidBody
            bodies = list(bodies) if bodies else []
            #: 第二个加的组件是「型材」⇒ 取**最后一个**实体的第一条边
            cand = None
            for b in reversed(bodies):
                eds = b.GetEdges()
                eds = list(eds) if eds else []
                if eds:
                    cand = eds[0]
                    break'''
NEW = '''            #: ⚠⚠ 第一版用 `asm.GetBodies2(...)` ⇒ `<unknown>.GetBodies2` ——
            #: 那是 **`IPartDoc`** 的成员，**不在 `IAssemblyDoc` 上**。
            #: ⇒ ★ 从**组件**取：`IComponent2.GetBody2()`（零参，返回 `Body2`）。
            bodies = []
            b2 = sw_connect.safe_get_com_member(comps[1], "GetBody2")
            if b2 is not None:
                bodies = [b2]
            #: 型材那条边 ⇒ 取第一条
            cand = None
            for b in bodies:
                eds = sw_connect.safe_get_com_member(b, "GetEdges")
                eds = list(eds) if eds else []
                if eds:
                    cand = eds[0]
                    break'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改用 IComponent2.GetBody2()")
