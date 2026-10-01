import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

OLD = '''def sketch_spline(model, points):
    """
    画样条曲线

    参数:
        points: [(x1,y1), (x2,y2), ...] 控制点列表（单位: **毫米**）
    """
    import array
    point_array = array.array('d')
    for x, y in points:
        point_array.extend([x, y, 0.0])
    return model.SketchManager.CreateSpline2(point_array, False)'''

NEW = '''def sketch_spline(model, points):
    """画样条曲线（⚠ **本机实测：建不出来，见下**）。

    参数:
        points: [(x1,y1), (x2,y2), ...] 控制点列表（单位: **毫米**）

    ⚠⚠ **2026-10-01（轮 141）真机实测：本函数建不出样条，而且此前是**静默**的。**
    证据 `tools/probe_spline_creation.py` / `probe_spline_redraw.py`（SW 2026 SP4.1）::

        ① `CreateSpline2(arr, False)` ⇒ 返回 **None** ⇒ `get_sketch_segments` = **0**
        ② **重绘后**（`IModelView::GraphicsRedraw`）仍是 **0**
           ⇒ ★ **排除了官方 Remarks 那句"必须重绘才看得见"的解释**
        ③ `CreateSpline`（1 参旧版）⇒ **迟到绑定里没有这个成员**
        ④ 对照·同样流程画**直线** ⇒ 段数 **1** ⇒ **流程本身没问题**

    ★ **为什么**：`CreateSpline2` 官方已标 **Obsolete**，后继是
    `CreateSpline3(Object, Object, Object, Boolean, **Object&**)` ——
    ⚠ 末参是 **BYREF `Object&`** ⇒ 已知事实 47/68 的**架构限制**（pywin32 迟到绑定到不了）
    ⇒ **这条后端上「建成样条」不达**。

    :raises RuntimeError: 官方**返回 `None`** ⇒ **抛**（不再静默）。
        ★ 照 `sw_surface._invoke` 的先例（已知事实 40）：
        **一个失败如果看起来像正常值，比没有守卫更糟。**
    """
    import array
    point_array = array.array('d')
    for x, y in points:
        point_array.extend([x, y, 0.0])
    seg = get_com_member(model, "SketchManager").CreateSpline2(point_array, False)
    if seg is None:
        raise RuntimeError(
            "ISketchManager.CreateSpline2 返回 None ⇒ **样条没建出来**（本机实测，轮 141）。"
            "原因：该成员官方已废弃，后继 `CreateSpline3` 末参是 BYREF `Object&`，"
            "**pywin32 迟到绑定到不了**（已知事实 47 / 68）⇒ 这条后端上不达。"
            "`sw_surface` 的先例是**让失败可见**，本函数照办（已知事实 40）。"
        )
    return seg'''

if "2026-10-01（轮 141）真机实测：本函数建不出样条" not in t:
    assert OLD in t, "sketch_spline 锚点不符"
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok sketch_spline 已改成「失败即抛」并写明实测依据")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

#: 顺带确认 `get_com_member` 在本文件里可用
if "get_com_member" in P.read_text(encoding="utf-8"):
    print("  `get_com_member` 可用 ✓")
