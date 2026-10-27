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
        doc=(
            "Split the mold into core and cavity solids along the parting surface. Creates the tooling-split feature an"
            "d returns its name; it raises when SolidWorks returns nothing, which usually means no parting surface exis"
            "ts yet, and a value of 0.0 means the document default."
        ),
        param_alias={},
        params=[
            Param(
                "scale",
                float,
                default=0.0,
                description=(
                    "First numeric argument; by position it is a scale factor, but its meaning is unverified and 0.0 me"
                    "ans the document default. Defaults to 0.0."
                ),
            ),
            Param(
                "thickness",
                float,
                default=0.0,
                description=(
                    "Second numeric argument; by position it is a wall thickness, but its meaning is unverified. Defaul"
                    "ts to 0.0, which means the document default."
                ),
            ),
            Param(
                "flip", bool, default=False, description=(
                                                 "Boolean argument at the third position, taken as a direction reversal"
                                                 " but unverified; defaults to false."
                                             )
            ),
            Param(
                "offset",
                float,
                default=0.0,
                description=(
                    "Fourth argument, by position an offset, unverified. Defaults to 0.0, which means the document defa"
                    "ult."
                ),
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
        doc=(
            "Insert the mold parting surface so the tooling split has a surface to cut along. Creates a parting-surface"
            " feature and returns its name; it raises when SolidWorks returns nothing, which usually means the parting "
            "line does not exist yet or no face is selected, and most of the eight arguments have no documented meaning"
            "."
        ),
        param_alias={},
        params=[
            Param(
                "surface_type",
                int,
                default=0,
                description=(
                    "Surface type enum value passed through by position without documented meaning; defaults to 0."
                ),
            ),
            Param(
                "flip",
                bool,
                default=False,
                description="Whether to reverse the surface direction; the meaning is unverified. Defaults to false.",
            ),
            Param("use_trim", bool, default=False, description=(
                                                       "Whether the surface is trimmed; the meaning is unverified. Defa"
                                                       "ults to false."
                                                   )),
            Param(
                "distance",
                float,
                default=0.0,
                description=(
                    "Distance value whose name suggests a length, though its position and unit are unverified. Defaults"
                    " to 0.0, meaning the default."
                ),
            ),
            Param(
                "angle",
                float,
                default=0.0,
                description=(
                    "Angle value whose name suggests an angle, though its unit is unverified. Defaults to 0.0, meaning "
                    "the default."
                ),
            ),
            Param("option", int, default=0, description=(
                                                "Option enum value passed through by position without documented meanin"
                                                "g; defaults to 0."
                                            )),
            Param(
                "tolerance", float, default=0.0, description=(
                                                     "Tolerance value whose unit is unverified. Defaults to 0.0, meanin"
                                                     "g the default."
                                                 )
            ),
            Param(
                "alternate",
                bool,
                default=False,
                description="Whether to use the alternate direction; the meaning is unverified. Defaults to false.",
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
        doc=(
            "Detect mold undercuts along a pull direction and paint the faces that form them. Modifies the display colo"
            "rs of the faces and returns nothing, because the detection result is not in the return value; an all-zero "
            "pull direction is rejected before the call since it would fall back to a draft direction the part may not "
            "have."
        ),
        param_alias={},
        params=[
            Param(
                "col_undercut",
                int,
                default=0,
                description=(
                    "Color reference value for the faces that are invisible from the pull direction and form an undercu"
                    "t; defaults to 0."
                ),
            ),
            Param(
                "col_base",
                int,
                default=0,
                description="Color reference value for the faces that do not form undercuts; defaults to 0.",
            ),
            Param(
                "b_coord_input",
                bool,
                default=True,
                description=(
                    "True uses dx, dy and dz as the pull direction, false uses the draft direction already defined in t"
                    "he model and can raise a modal dialog when the part has none. Defaults to true."
                ),
            ),
            Param(
                "dx",
                float,
                default=0.0,
                description="X component of the pull direction, used only when b_coord_input is true; defaults to 0.0.",
            ),
            Param(
                "dy",
                float,
                default=0.0,
                description="Y component of the pull direction, used only when b_coord_input is true; defaults to 0.0.",
            ),
            Param(
                "dz",
                float,
                default=1.0,
                description=(
                    "Z component of the pull direction; defaults to 1.0, so the default pull direction runs along Z."
                ),
            ),
        ],
    ),
]
