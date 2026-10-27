"""工具声明：按**坐标**建异型孔向导孔（`solidworks_hole_wizard_at_point`）。

## 为什么需要它

既有 `solidworks_hole_wizard` 走 `create_hole_wizard_at_selection_report`，
孔位由**面选择器**决定 ⇒ 孔只落在**面中心**，一个面只能放一个孔。

而首件板要 4 个孔在 `(10,10)/(90,10)/(10,50)/(90,50)`。
⇒ 把第 27 轮新增的 `create_hole_wizard_at_point_report`（射线穿过指定坐标）挂成工具，
   计划里才能按位置放孔。

## 单位口径

参数名带 `_mm`，**函数内部**换算成米（`float(x_mm) / 1000.0`）——
与同模块 `create_counterbore_hole_at_selection_report` 的既有做法一致
⇒ 本 ToolSpec **不加 `derived_args`**，避免换算两次。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具声明）
# 文件:   mcp-server/tool_specs_batch117.py
# 定位:   把 `sw_hole_features.create_hole_wizard_at_point_report` 挂成工具，
#          让计划能按坐标放异型孔向导孔（既有工具只能放面中心）。
# 官方依据: IFeatureManager.HoleWizard5（**27 参**；Depth 之后 13 个 double）·
#          IModelDocExtension.SelectByRay（12 参，Mark=0）
#          ★ 27 参这件事有实测对照：事实 562
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_MM = "in MILLIMETRES."

SPECS_BATCH117 = [
    ToolSpec(
        name="solidworks_hole_wizard_at_point",
        title="Hole Wizard at an Explicit Point",
        module="sw_hole_features",
        function="create_hole_wizard_at_point_report",
        inject="model",
        params=[
            Param("x_mm", float, description="Hole centre X in millimetres."),
            Param("y_mm", float, description="Hole centre Y in millimetres."),
            Param(
                "z_mm",
                float,
                description=(
                    "Z of the face the hole is drilled into, in millimetres; the ray is lifted from here and fired back"
                    " down."
                ),
            ),
            Param(
                "size",
                str,
                description=(
                    "Fastener size string such as 'M8'; an empty string or a bare number makes the wizard return nothin"
                    "g."
                ),
            ),
            Param("diameter_mm", float, default=8.0,
                  description="Hole diameter in millimetres. Defaults to 8."),
            Param("depth_mm", float, default=20.0,
                  description="Hole depth in millimetres when the hole is not through all geometry. Defaults to 20."),
            Param("through", bool, default=True,
                  description=(
                      "Whether the hole goes through all geometry, in which case the depth is ignored. Defaults to true"
                      "."
                  )),
        ],
        evidence=(
            "Create a HoleWizard hole at an explicit (x, y, z) point and report it. Unlike solidworks_hole_wizard, the "
            "position is not limited to the face centre. Criterion is the feature-tree increment, not the return value."
        ),
        doc=(
            "Create a Hole Wizard hole at an explicit point and read the hole parameters back. Writes a hole feature an"
            "d does not save the document; the ray starts above the given point and goes down, and the feature tree gro"
            "wing is the success criterion rather than the return value."
        ),
    ),
]
