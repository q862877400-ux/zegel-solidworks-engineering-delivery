import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
t = P.read_text(encoding="utf-8")
OLD = '''    component.ClearSelection2(True) if hasattr(component, "ClearSelection2") else None
    ok = call_com_member(component, "Select4", False, create_empty_dispatch_variant())
    if not ok:
        raise RuntimeError(
            "IComponent2.Select4 返回 False ⇒ 组件没被选中，EditPart2 会静默无效"
            "（⚠ 判「选上没有」**一律回读**，见已知事实 94）")'''
NEW = '''    #: ⚠⚠ **实测（轮 161）**：本模块先前想用 `IComponent2.Select4(Append, Callout)` ——
    #: 那是 **`IEntity`** 的签名；**`IComponent2` 上的 `Select4` 第二参是 `SelectData`**，
    #: 传空 Dispatch 会报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`，
    #: **报错完全看不出是"参数类型不对"**）。
    #: ⇒ 改用 **`IComponent2.Select2(Boolean Append, Int32 Mark)`** ——
    #: 两个**标量**、**没有 Dispatch 参数**，最不容易踩坑。
    ok = call_com_member(component, "Select2", False, 0)
    if not ok:
        raise RuntimeError(
            "IComponent2.Select2 返回 False ⇒ 组件没被选中，EditPart2 会静默无效"
            "（⚠ 判「选上没有」**一律回读**，见已知事实 94）")'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已改用 IComponent2.Select2(False, 0)")
