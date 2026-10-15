import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
t = p.read_text(encoding="utf-8")

#: ① 补导入（双路，照本仓既有模式）
t = t.replace("    from .sw_connect import get_com_member\n",
              "    from .sw_connect import call_com_member, create_empty_dispatch_variant, get_com_member, out_i4\n", 1)
t = t.replace("    from sw_connect import get_com_member\n",
              "    from sw_connect import call_com_member, create_empty_dispatch_variant, get_com_member, out_i4\n", 1)

#: ② 签名改成**收组件对象**（按对象选，避免依赖不存在的 `_select_by_id`）
OLD_SIG = '''def edit_part_in_context(asm_model, component_keyword, *, silent=True,
                         allow_read_only=True):
    """进入**装配体里的零件在上下文编辑**态（官方 `IAssemblyDoc.EditPart2`）。

    :param asm_model: `IAssemblyDoc`
    :param component_keyword: 组件名的关键词（用既有的 `_select_by_id` 选它）
    :returns: 官方返回的 `Int32` 状态码（`swEditPartCommandStatus_e`；
        ⚠ 该枚举**在 `C:\\swapi\\enums\\` 里查不到**（铁律 5）⇒ **原样透出数字，不翻译**）。

    ⚠ 官方签名第 3 参是 **`ref Int32`** ⇒ 用本仓库既有的 `out_i4()` 给出参占位。
    """
    _select_by_id(asm_model.Extension, component_keyword, "COMPONENT")
    code = call_com_member(asm_model, "EditPart2",
                           bool(silent), bool(allow_read_only), out_i4())
    return int(code) if isinstance(code, int) else code'''
NEW_SIG = '''def edit_part_in_context(asm_model, component, *, silent=True, allow_read_only=True):
    """进入**装配体里的零件在上下文编辑**态（官方 `IAssemblyDoc.EditPart2`）。

    :param asm_model: `IAssemblyDoc`
    :param component: **`IComponent2` 对象**（不是名字）。
        ⚠ 本文件**没有**按名字选组件的助手（`_select_by_id` **不在本模块**）⇒
        改用**按对象选**（`IComponent2.Select4`，即已知事实 32 认可的可行路径）。
    :returns: 官方返回的 `Int32` 状态码（`swEditPartCommandStatus_e`；
        ⚠ 该枚举**在 `C:\\swapi\\enums\\` 里查不到**（铁律 5）⇒ **原样透出数字，不翻译**）。

    ⚠ 官方签名第 3 参是 **`ref Int32`** ⇒ 用本仓库既有的 `out_i4()` 给出参占位。
    """
    component.ClearSelection2(True) if hasattr(component, "ClearSelection2") else None
    ok = call_com_member(component, "Select4", False, create_empty_dispatch_variant())
    if not ok:
        raise RuntimeError(
            "IComponent2.Select4 返回 False ⇒ 组件没被选中，EditPart2 会静默无效"
            "（⚠ 判「选上没有」**一律回读**，见已知事实 94）")
    code = call_com_member(asm_model, "EditPart2",
                           bool(silent), bool(allow_read_only), out_i4())
    return int(code) if isinstance(code, int) else code'''
assert OLD_SIG in t, "签名锚点不符"
t = t.replace(OLD_SIG, NEW_SIG, 1)

#: ③ 修一个 `\\s` 转义警告（docstring 里的 Windows 路径）
t = t.replace('`C:\\\\swapi\\\\enums\\\\` 里查不到', '`C:\\\\swapi\\\\enums\\\\` 里查不到')
p.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 导入补齐 + 签名改成收组件对象")
