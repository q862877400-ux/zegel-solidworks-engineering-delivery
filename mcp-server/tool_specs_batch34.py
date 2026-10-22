"""第三十四批 MCP 工具声明：**声明式建孔 5 个**（24h 段 4 续 / Spec Kit `151`）。

## ★★★★ 为什么这一族值得做（★ 它比"把既有函数挂上去"更好）
```
★★ 上游的统一建孔工具 `solidworks_create_hole_feature`（`mcp-server/server.py` L2244）
   吃 **`center_x_mm` / `center_y_mm`** —— ★★ **那是**裸坐标参数名****（规则 3 的**字面**红线）。
★ 而能力层既有的 `create_through_hole(model, center, …)` 吃 `center`（坐标元组）
  —— ★ 名字不表态（在 `_COORD_COMPONENT_NOTE` 里），★ **但绕过规则 3 的**精神****。
⇒ ★★★ **本批是"规则 3 合规版"**：★ **只吃声明式 `selection`**，
  ★ **内部用 `sw_selection_spec.selection_point` 从选区读点**
  ⇒ ★★ **于是工具参数里没有坐标** ✓
★ 单位已定（★ 轮 267 三点对照）：★ `GetSelectionPoint2` 回的是 **毫米**。
```

## ⚠ 与上游的**命名**关系（★ 不撞名）
```
★ 上游名叫 `solidworks_create_hole_feature`（**一个统一入口**）；
★★ 本批是 **5 个专用入口**、名字形如 **`solidworks_hole_*`**
   ⇒ ★ 两者**不撞名**（★ 上游那个**仍在柜台上**，★ 而本批是**它的合规替代**）。
```

## 判据（规则 6 + 本项目既有）
```
★ 每个工具的返回值都来自能力层的 `HoleFeatureEvidence`（★ **本来就是回读证据**），
  ★★ 再套一层"**选区点的坐标**" ⇒ ★ **调用方能看出它建在哪个点上**（★ 而不是"说成功了"）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch34.py
# 定位:   24h 计划 段 4 续（Spec Kit `151`）—— 声明式建孔 5 个。
# 官方依据: `IModelDoc2.HoleWizard5` 族（★ 见 `scripts/sw_hole_features.py` 的来源块）·
#          `ISelectionMgr.GetSelectionPoint2(Index, Mark)`（★ 读点，Index 从 1 起）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH34"]

_SEL = (
    'Declarative selection, e.g. "index:0" or "__current_selection__". '
    "★ The hole's position comes from what this selects — **no coordinates are passed**."
)
_PLANE = 'Sketch plane name (English or Chinese, e.g. "Front Plane" / "前视基准面").'


SPECS_BATCH34 = [
    ToolSpec(
        name="solidworks_hole_through_by_selection",
        title="Create a Through Hole at a Declaratively Selected Point",
        module="sw_hole_features",
        function="create_through_hole_at_selection_report",
        inject="model",
        params=[
            Param("selection", str, description=_SEL),
            Param("diameter_mm", float, description="Hole diameter in MILLIMETRES."),
            Param("plane_name", str, default="Front Plane", description=_PLANE),
            Param("name", str, default="通孔", description="Feature name."),
        ],
        doc="Create a fully-through circular hole whose position comes from a declarative "
        "selection (★ rule 3: no coordinates in the tool signature). Returns the read-back "
        "evidence plus the point that was actually used.",
    ),
    ToolSpec(
        name="solidworks_hole_blind_by_selection",
        title="Create a Blind Hole at a Declaratively Selected Point",
        module="sw_hole_features",
        function="create_blind_hole_at_selection_report",
        inject="model",
        params=[
            Param("selection", str, description=_SEL),
            Param("diameter_mm", float, description="Hole diameter in MILLIMETRES."),
            Param("depth_mm", float, description="Blind depth in MILLIMETRES."),
            Param("plane_name", str, default="Front Plane", description=_PLANE),
            Param("name", str, default="盲孔", description="Feature name."),
        ],
        doc="Create a blind circular hole at a declaratively selected point (★ rule 3). "
        "Returns the read-back evidence plus the point used.",
    ),
    ToolSpec(
        name="solidworks_hole_counterbore_by_selection",
        title="Create a Counterbore Hole at a Declaratively Selected Point",
        module="sw_hole_features",
        function="create_counterbore_hole_at_selection_report",
        inject="model",
        params=[
            Param("selection", str, description=_SEL),
            Param(
                "hole_diameter_mm",
                float,
                description="Main hole diameter in MILLIMETRES.",
            ),
            Param(
                "counterbore_diameter_mm",
                float,
                description="Counterbore diameter in MILLIMETRES.",
            ),
            Param(
                "counterbore_depth_mm",
                float,
                description="Counterbore depth in MILLIMETRES.",
            ),
            Param("plane_name", str, default="Front Plane", description=_PLANE),
            Param("name", str, default="沉头孔", description="Feature name."),
        ],
        doc="Create a counterbore hole at a declaratively selected point (★ rule 3).",
    ),
    ToolSpec(
        name="solidworks_hole_countersink_by_selection",
        title="Create a Countersink Hole at a Declaratively Selected Point",
        module="sw_hole_features",
        function="create_countersink_hole_at_selection_report",
        inject="model",
        params=[
            Param("selection", str, description=_SEL),
            Param(
                "hole_diameter_mm",
                float,
                description="Main hole diameter in MILLIMETRES.",
            ),
            Param(
                "countersink_diameter_mm",
                float,
                description="Countersink diameter in MILLIMETRES.",
            ),
            Param(
                "included_angle_deg",
                float,
                default=90.0,
                description="Countersink included angle in DEGREES (★ rule 2: _deg).",
            ),
            Param("plane_name", str, default="Front Plane", description=_PLANE),
            Param("name", str, default="锥沉孔", description="Feature name."),
        ],
        doc="Create a countersink hole at a declaratively selected point (★ rule 3).",
    ),
    ToolSpec(
        name="solidworks_slot_semicircular_by_selection",
        title="Create a Semicircular-End Slot Between Two Declaratively Selected Points",
        module="sw_hole_features",
        function="create_semicircular_slot_at_selection_report",
        inject="model",
        params=[
            Param(
                "start_selection",
                str,
                description="Declarative selection for the START point. " + _SEL,
            ),
            Param(
                "end_selection",
                str,
                description="Declarative selection for the END point. " + _SEL,
            ),
            Param("width_mm", float, description="Slot width in MILLIMETRES."),
            Param(
                "depth_mm",
                float,
                default=0.0,
                description="Slot depth in MILLIMETRES. ⚠ 0.0 = through.",
            ),
            Param("plane_name", str, default="Front Plane", description=_PLANE),
            Param("name", str, default="半圆端槽", description="Feature name."),
        ],
        doc="Create a semicircular-end slot spanning two declaratively selected points "
        "(★ rule 3: **both** endpoints come from selections, not coordinates).",
    ),
]
