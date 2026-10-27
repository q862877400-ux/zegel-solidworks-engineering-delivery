"""第九批 MCP 工具声明：把**模具域「已实现 + 有测试 + 未暴露」**的 3 个接出去。

## 为什么是这 3 个（2026-10-01 轮 98，Spec Kit `018`）
`010` 把 338 个缺口分成四类，`012`–`017` 在**暴露我们自己的**能力。
轮 98 回头看**最小域的唯一"真缺口"** `tooling_split`（模具）：
```
官方成员：InsertMoldCoreCavitySolids / CoreCavitySplit
本仓库：scripts/sw_mold.py::insert_core_cavity_solids   ← **已经实现了**
        已暴露=**否** · 有测试=**是**
```
⇒ ★ **那个"真缺口"其实是「已实现但没暴露」** —— 正是 `010` 记的第三类。

⇒ 顺手把模具域同类的另两个也接出去（都**已实现 + 有测试 + 未暴露**）：
`insert_parting_surface` · `mold_undercut_detect`。

## ⚠ 一句要紧的话：**这不会让「缺口 338」变小**
难口的计数按**操作名归一**比：我们叫 `core_cavity_solids`、外部叫 `tooling_split`
⇒ **名字对不上，计数不动**。
★ **名字级计数 ≠ 能力级覆盖** —— 本批闭的是**能力**（用户现在能做这件事），不是那个数字。
（`010` 已提出这个区分；本批是它的**具体例证**。）

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch9.py
# 定位:   把模具域「已实现 + 有测试 + 未暴露」的 3 个接出去。
# 官方签名依据: 不适用（只做参数搬运）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH9"]


SPECS_BATCH9 = [
    ToolSpec(
        name="solidworks_mold_core_cavity_split",
        title="Insert Mold Core/Cavity Split",
        module="sw_mold",
        function="insert_core_cavity_solids",
        inject="model",
        evidence=(
            "Split the mold into core and cavity solids (this is the tooling split). ⚠ 0.0 means 'use the document defa"
            "ult' for scale/thickness/offset."
        ),
        doc="Split the mold into core and cavity solids (this is the tooling split). "
        "⚠ 0.0 means 'use the document default' for scale/thickness/offset.",
        param_alias={},
        params=[
            Param(
                "scale",
                float,
                default=0.0,
                description="Scale factor; 0.0 = document default.",
            ),
            Param(
                "thickness",
                float,
                default=0.0,
                description="Wall thickness; 0.0 = document default.",
            ),
            Param(
                "flip", bool, default=False, description="Reverse the split direction."
            ),
            Param(
                "offset",
                float,
                default=0.0,
                description="Offset; 0.0 = document default.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_mold_parting_surface",
        title="Insert Mold Parting Surface",
        module="sw_mold",
        function="insert_parting_surface",
        inject="model",
        evidence=(
            "Insert the mold parting surface."
        ),
        doc="Insert the mold parting surface.",
        param_alias={},
        params=[
            Param(
                "surface_type",
                int,
                default=0,
                description="Official surface type enum value.",
            ),
            Param(
                "flip",
                bool,
                default=False,
                description="Reverse the surface direction.",
            ),
            Param("use_trim", bool, default=False, description="Trim the surface."),
            Param(
                "distance",
                float,
                default=0.0,
                description="Distance parameter; 0.0 = default.",
            ),
            Param(
                "angle",
                float,
                default=0.0,
                description="Angle parameter; 0.0 = default.",
            ),
            Param("option", int, default=0, description="Official option enum value."),
            Param(
                "tolerance", float, default=0.0, description="Tolerance; 0.0 = default."
            ),
            Param(
                "alternate",
                bool,
                default=False,
                description="Use the alternate direction.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_mold_undercut_detect",
        title="Detect Mold Undercuts",
        module="sw_mold",
        function="mold_undercut_detect",
        inject="model",
        evidence=(
            "Detect mold undercuts along a direction. ⚠ The underlying IFeatureManager.MoldUndercutDetect is marked Obs"
            "olete by SOLIDWORKS (successor: MoldUndercutDetect2); kept deliberately until the successor shape is verif"
            "ied. See docs/obsolete-member-candidates.md. ★★ Parameter names now follow the official md (ColUndercut/Co"
            "lBase/BCoordInput/Dx/Dy/Dz); the earlier names (direction/option/include_hidden/a/b/c) did not, so the thi"
            "rd argument BCoordInput received False — which drops back to 'use the model's own draft direction' and pop"
            "s the modal 「此拔模方向尚未定义。」 on a part without one, stalling the session."
        ),
        doc="Detect mold undercuts along a direction. ⚠ The underlying IFeatureManager.MoldUndercutDetect is marked "
             "Obsolete by SOLIDWORKS (successor: MoldUndercutDetect2); kept deliberately until the successor shape is "
             "verified. See docs/obsolete-member-candidates.md. ★★ Parameter names now follow the official md "
             "(ColUndercut/ColBase/BCoordInput/Dx/Dy/Dz); the earlier names (direction/option/include_hidden/a/b/c) did "
             "not, so the third argument BCoordInput received False — which drops back to 'use the model's own draft "
             "direction' and pops the modal 「此拔模方向尚未定义。」 on a part without one, stalling the session.",
        param_alias={},
        params=[
            Param(
                "col_undercut",
                int,
                default=0,
                description="COLORREF for the faces invisible from one direction that form an undercut.",
            ),
            Param(
                "col_base",
                int,
                default=0,
                description="COLORREF for the faces that do not form undercuts.",
            ),
            Param(
                "b_coord_input",
                bool,
                default=True,
                description="True to use the coordinate input (Dx/Dy/Dz) as the pull direction; "
                "false to use the model's already-defined direction (which pops a modal "
                "dialog when the model has none).",
            ),
            Param(
                "dx",
                float,
                default=0.0,
                description="X component of the pull direction.",
            ),
            Param(
                "dy",
                float,
                default=0.0,
                description="Y component of the pull direction.",
            ),
            Param(
                "dz",
                float,
                default=1.0,
                description="Z component of the pull direction.",
            ),
        ],
    ),
]
