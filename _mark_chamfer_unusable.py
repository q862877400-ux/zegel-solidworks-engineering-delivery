import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch_edit.py")
t = P.read_text(encoding="utf-8")

OLD = '''    :returns: 倒角产生的草图线段（官方返回 `SketchSegment`）。
    :raises RuntimeError: 返回 `None`（最常见原因：**没有选中两条草图实体**）。
    """'''
NEW = '''    ⚠⚠ **本函数当前「不可用」（2026-10-01 轮 122 真机实测）** ——
    在**新零件**上画两条相接直线、**已确认选中 2 条**，然后调 `CreateChamfer`：
    ```
    type=2(distance_equal)  ⇒ **pywintypes.com_error: (-2147417851, '服务器出现意外情况')**
    ```
    ★ `0x80010105` **正是已知事实 47 / 28 那个错误码** ——
    即「**pywin32 迟到绑定到不了需要真实指针的接口**」这一**架构性限制**。
    ⚠ **按事实 53 停手**（不再试别的类型/参数组合）；本模块保留该函数作**可复算的证据**。

    :returns: 倒角产生的草图线段（官方返回 `SketchSegment`）。
    :raises RuntimeError: 返回 `None`（最常见原因：**没有选中两条草图实体**）。
    """'''
if "本函数当前「不可用」" not in t:
    assert OLD in t, "docstring 锚点不符"
    t = t.replace(OLD, NEW, 1)
    print("  ok create_sketch_chamfer 已加不可用警示")
else:
    print("  已有警示")

OLD_SRC = "# ⚠ **验证等级：`stitched`**"
NEW_SRC = ("# ⚠⚠ **验证等级：`stitched`，且其中一半已确认「到不了」**（2026-10-01 轮 122 真机实测）：\n"
           "#   ```\n"
           "#   convert_entities       ⚠ **未实测**（需要选中的边/环/面，本轮未造出前置）\n"
           "#   create_sketch_chamfer  ❌ **到不了** —— 已确认选中 2 条仍报\n"
           "#                             `0x80010105「服务器出现意外情况」`（= 事实 47 / 28 的错误码）\n"
           "#   sketch_mirror          ⚠ **未实测**（需要中心线 mark=2 + 线段 mark=1 的选中标记）\n"
           "#   ```\n"
           "#   ⇒ **`CreateChamfer` 在本后端到不了**，属「需要真实指针接口」那一族，**不是参数没调对**。\n"
           "#   ⚠ 按**事实 53** 停手，不再试别的类型/参数组合。\n"
           "# ⚠ **验证等级：`stitched`**")
if "其中一半已确认「到不了」" not in t:
    assert OLD_SRC in t, "来源块锚点不符"
    t = t.replace(OLD_SRC, NEW_SRC, 1)
    print("  ok 来源块已加分裂声明")
else:
    print("  来源块已有声明")

P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
