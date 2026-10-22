"""第二十一批 MCP 工具声明：**建草图 + 画几何** 5 个（砌墙 W4）。

## ★★★ 本批是本仓库**最底层的短板**，没有它上面全用不了
```
★ 实测（轮 228）：MCP 里跟草图有关的只有 `solidworks_add_sketch_relation` + W1 那 4 个**只读** ——
  ★★ **不能建草图、不能画线/圆/矩形**。
⇒ 后果不只是"少几个工具"：
  ★ **已经挂出去的建模工具全都用不了** —— `solidworks_revolve_boss` ·
    `solidworks_create_hole_feature` · 钣金 `solidworks_sheet_metal_create_base_flange` …
    **它们都要一个「已存在的草图」**，而 AI 造不出草图。
  ⇒ ★★ 本仓库此前是「**会旋转、会打孔、会钣金，却连一条线都画不出来**」。
★ 而能力层里躺着一整族（**17 个**首参可注入的）：`start_sketch` · `end_sketch` · `sketch_line` ·
  `sketch_circle` · `sketch_corner_rectangle` · `sketch_polygon` · `sketch_slot` · `sketch_arc` …
```

## ★★ 参数命名：规则 2 与规则 3 的边界（本批的**设计决定**，见 known-facts 162）
```
`sw_part.sketch_line(model, x1, y1, x2, y2)` —— ★ 能力层用的是**裸坐标名**。
★ 而草图画几何**本质上就得给平面内坐标**（没有别的法子）⇒ 这不是偷懒，是问题本身如此。
★ 规则 3 **原文自带豁免**：「除非该工具本身是 `*_at_point` 类且注明用途」。
⇒ ★★ 本批的处置：**对外用语义名 + `_mm`** ——
     `start_x_mm` / `start_y_mm` / `end_x_mm` / `end_y_mm`（而不是 `x1_mm`，⚠ 那个**在黑名单里**）
   ★ 语义名既过规则 2（长度参数 `_mm` 结尾），**也不冒充"裸坐标"** ——
     它们说的是「草图平面上一条线的两个端点」，是**领域语义**，不是"随便给组坐标"。
   ★ 并在每个工具的说明里**注明豁免依据**：草图画几何必须给平面内坐标。
```
⚠ **门禁的盲区（如实记，不在本批顺手改）**：`_BARE_COORD_NAMES` **只查参数字面名**
  （`x` / `y` / `z` / `x_mm` / `y_mm` / `z_mm` / `point` / `coordinate`）
  ⇒ 能力层的 `x1`/`y1`/`x2`/`y2` **一个都不在黑名单里** ⇒ **门禁漏掉它们**
  （与事实 153「门禁只验了 3 句里的 1 句」同族）。★ **不为通过而放宽判据**，留后续单独开特性。

## ★ 为什么只有 5 个（不把 17 个全挂）
`sketch_rectangle`（中心 + 宽高）与 `sketch_corner_rectangle`（对角两点）**语义重叠** ——
★ 两个都挂会让 AI 选错 ⇒ **只挂对角那个**（语义无歧义）。
其余（`sketch_spline` / `sketch_polygon` / `sketch_slot` / `sketch_ellipse` / `auto_dimension_sketch` …）
**留到后续批次**，本批只补"能画出最基本图形"这条命脉。

## ★★ 验证方式与只读批**不同**：读写配对
```
建草图 → 画线 / 圆 / 矩形 → ★ **用 W1 已挂的只读工具回读断言**
   `solidworks_sketch_count_lines` / `_count_arcs` / `_count_segments` / `_is_3d`
⇒ ★ 两批工具就此**接上**（W1 只读，本批写）—— 这是本阶段 A/B 配对判据在"写"类批次上的延伸。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch21.py
# 定位:   「孤立能力暴露」第二十一批 / 砌墙 W4（Spec Kit `135`）。
# 官方签名依据: 不适用（只做参数搬运）；被搬运函数的官方依据见 `scripts/sw_part.py` 的来源块
#          （`ISketchManager.CreateLine` / `CreateCircleByRadius` / `CreateCornerRectangle` 一族）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH21"]

#: 每个工具都要说清的那件事（★ 规则 3 的豁免依据 + 单位 + 参照原点）
_GEOM_NOTE = (
    "⚠ Sketch geometry MUST be given as in-plane coordinates — this is the documented "
    "exception in rule 3 (a *drawing primitive* has no named entity to select). "
    "Coordinates are millimetres, relative to the SKETCH ORIGIN, in the sketch plane. "
    "★ Start a sketch with solidworks_sketch_start first, and finish with "
    "solidworks_sketch_end; read back with the solidworks_sketch_count_* tools."
)

_PLANE = (
    'Plane name, English or Chinese ("Front Plane" / "前视基准面", "Top Plane" / '
    '"上视基准面", "Right Plane" / "右视基准面").'
)


def _consumed(*names: str) -> dict:
    """这些入参由 `param_alias` 改名后传给目标函数（**不是**由 `derived_args` 消费）。"""
    return {n: None for n in ()}  #: 占位：本批用**改名**而非消费，故不标 None


SPECS_BATCH21 = [
    ToolSpec(
        name="solidworks_sketch_start",
        title="Start a Sketch",
        module="sw_part",
        function="start_sketch",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        params=[Param("plane_name", str, default="Front Plane", description=_PLANE)],
        doc="Enter a new sketch on a reference plane. ★ This is the prerequisite for every "
        "sketch-based feature (extrude, revolve, hole, sheet-metal flange).",
    ),
    ToolSpec(
        name="solidworks_sketch_end",
        title="End the Sketch",
        module="sw_part",
        function="end_sketch",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        params=[],
        doc="Leave the current sketch. ★ The resulting sketch reference is reusable by "
        "solidworks_extrude_* and other feature tools, so features can be built right after.",
    ),
    ToolSpec(
        name="solidworks_sketch_add_line",
        title="Add a Line to the Sketch",
        module="sw_part",
        function="sketch_line",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        param_alias={
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
        },
        params=[
            Param("start_x_mm", float, description="Start point X, mm."),
            Param("start_y_mm", float, description="Start point Y, mm."),
            Param("end_x_mm", float, description="End point X, mm."),
            Param("end_y_mm", float, description="End point Y, mm."),
        ],
        doc="Draw a straight LINE in the open sketch. " + _GEOM_NOTE,
    ),
    ToolSpec(
        name="solidworks_sketch_add_circle",
        title="Add a Circle to the Sketch",
        module="sw_part",
        function="sketch_circle",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        param_alias={"center_x_mm": "cx", "center_y_mm": "cy", "radius_mm": "radius"},
        params=[
            Param("center_x_mm", float, description="Centre X, mm."),
            Param("center_y_mm", float, description="Centre Y, mm."),
            Param("radius_mm", float, description="Radius, mm (must be > 0)."),
        ],
        doc="Draw a CIRCLE in the open sketch. " + _GEOM_NOTE,
    ),
    ToolSpec(
        name="solidworks_sketch_add_rectangle",
        title="Add a Rectangle to the Sketch (two opposite corners)",
        module="sw_part",
        function="sketch_corner_rectangle",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        param_alias={"x1_mm": "x1", "y1_mm": "y1", "x2_mm": "x2", "y2_mm": "y2"},
        params=[
            Param("x1_mm", float, description="First corner X, mm."),
            Param("y1_mm", float, description="First corner Y, mm."),
            Param("x2_mm", float, description="Opposite corner X, mm."),
            Param("y2_mm", float, description="Opposite corner Y, mm."),
        ],
        doc="Draw a RECTANGLE in the open sketch, given TWO OPPOSITE CORNERS. "
        "⚠ Not the same as a centre+size rectangle — this tool takes corners, which is "
        "unambiguous. " + _GEOM_NOTE,
    ),
]
