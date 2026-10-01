import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sketch_relations.py")
t = P.read_text(encoding="utf-8")

OLD = '''    relation = get_com_member(manager, "AddRelation", entities, int(constraint_type))'''
NEW = '''    #: ⚠⚠⚠ **实测（轮 161）**：`AddRelation` 官方有**两个重载**
    #: （`SketchRelation AddRelation(Object, Int32)` 与 `Void AddRelation(String)`）——
    #: 而那个 `Object` 是 **SAFEARRAY** ⇒ **直接传 Python `list` / `tuple` 都不行**：
    #: ```
    #:   list[0:2]  ⇒ com_error 0x80010105「服务器出现意外情况」  计数 3 → 3（**没加上**）
    #:   tuple(0,1) ⇒ 同上
    #:   VARIANT(VT_ARRAY | VT_DISPATCH, [实体…]) ⇒ 无错  计数 3 → **4**（**加上了**）
    #: ```
    #: ★★★ **所以本函数此前**从没在真机上跑通过** —— 契约测试用的是**假对象**，
    #: 而假对象测不出「实参要不要包 VARIANT」（已知事实 99/101 那一族）。
    #: ⚠ 另记：那个错误码 `0x80010105` 与已知事实 28/47 的「服务器出现意外情况」同一个码 ——
    #: 本轮的形态是「**数组实参没包 VARIANT**」，与那两条（`CreateBsplineSurface` /
    #: `AccessSelections`）**不同因同码**，报错本身看不出是哪一种。
    relation = get_com_member(manager, "AddRelation",
                              _dispatch_array(entities), int(constraint_type))'''
assert OLD in t, "AddRelation 锚点不符"
t = t.replace(OLD, NEW, 1)

HELPER = '''

def _dispatch_array(entities):
    """把实体序列包成 COM 要的 **SAFEARRAY of IDispatch**（`VARIANT(VT_ARRAY|VT_DISPATCH)`）。

    ⚠⚠ **不包就调不通**（轮 161 实测）：`list` / `tuple` 都报
    `com_error 0x80010105`（「服务器出现意外情况」），而包了之后计数**真的 +1**。
    ★ 已是 `VARIANT` 的直接原样返回（调用方自己包过就别再包一层）。
    """
    import pythoncom
    from win32com.client import VARIANT
    if hasattr(entities, "varianttype"):
        return entities
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(entities))
'''
if "_dispatch_array(" not in t.split("def add_relation")[0]:
    t = t.replace("def add_relation(", HELPER.strip() + "\n\n\ndef add_relation(", 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok add_relation 已改成包 VARIANT 数组")
