# ── 24h 计划 v2 · 段 2：**草图图元**（`sw_part` 的 5 条真缺口）────────────────────────
# ★★★★ 2026-10-03（轮 398）来源：`tools/triage_real_gaps.py` 判定的「该挂」里 `sw_part`
# 那 15 条中
#   **属于"草图图元"的 5 条**（★ 其余归段 3 的实体特征）。★ 照既有 `tool_specs_batch21.py`
# 的 `sketch_line` / `sketch_circle` / `sketch_corner_rectangle` 模式（同模块、同注入、
# 同别名风格）。
#
# ★★ **为什么先做草图图元**（计划 §一 排序原则）：★ 它们让**测试几何更丰富** ——
#   ★ 后面每一段的真机验证都要造件，而"能造出什么形状"决定了"能验到什么深度"。
#
# ★★ **本批 5 条 + 1 条不做**（★ 逐条写清）：
#   ```
#   挂：sketch_arc · sketch_ellipse · sketch_polygon · sketch_slot · sketch_centerline
#   ★ 不做：sketch_spline
#     ⇒ 依据：`scripts/sw_part.sketch_spline` 的文档串（轮 141 真机实测）——
# `CreateSpline2` 返回 None（且此前是静默的）· 重绘后仍 0 段（排除了官方那句"必须重绘"）
# ·
#       旧版 `CreateSpline` 在迟到绑定里没有这个成员；
#       而后继 `CreateSpline3(Object, Object, Object, Boolean, Object&)` 末参是
#       **BYREF `Object&`** ⇒ 已知事实 47/68 的**架构限制**（pywin32 到不了）
#     ⇒ ★★ 挂出来只会给人"能调"的错觉（★ 与 13 条 `IModeler.Create*Surface` 同一处置）。
#   ```
#
# ★ 规则 2 / 3：长度一律 `*_mm`（别名映射到形参）· 坐标是**草图系内的毫米**（规则 3 的
#   书面例外 —— 见下面 `_GEOM_NOTE`）· 画之前要先 `solidworks_sketch_start`。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch54.py —— 本文件（新）
# 定位:   24h 计划 v2 段 2：把 `sw_part` 的草图图元族挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\ISketchManager\` 的 `CreateArc` / `CreateEllipse` / `Cre
# atePolygon` /
#   `CreateSketchSlot` / `CreateCenterLine`（本项目内的包装在 `scripts/sw_part.py`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

_GEOM_NOTE = (
    "⚠ Sketch geometry MUST be given as in-plane coordinates — this is the documented "
    "exception in rule 3 (a *drawing primitive* has no named entity to select). "
    "Coordinates are millimetres, relative to the SKETCH ORIGIN, in the sketch plane. "
    "★ Start a sketch with solidworks_sketch_start first, and finish with "
    "solidworks_sketch_end; read back with the solidworks_sketch_count_* tools."
)

SPECS_BATCH54 = [
    ToolSpec(
        name="solidworks_sketch_add_arc",
        title="Add an Arc to the Sketch",
        module="sw_part",
        inject="model",
        function="sketch_arc",
        param_alias={
            "center_x_mm": "cx",
            "center_y_mm": "cy",
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
        },
        params=[
            Param("center_x_mm", float, description="Centre X in millimetres, measured from the sketch origin."),
            Param("center_y_mm", float, description="Centre Y in millimetres, measured from the sketch origin."),
            Param("start_x_mm", float, description="Arc start X in millimetres."),
            Param("start_y_mm", float, description="Arc start Y in millimetres."),
            Param("end_x_mm", float, description="Arc end X in millimetres."),
            Param("end_y_mm", float, description="Arc end Y in millimetres."),
            Param(
                "direction",
                int,
                default=1,
                description=(
                    "Arc direction as the reference parameter takes it, clockwise or counter-clockwise. Defaults to 1."
                ),
            ),
        ],
        evidence=(
            "★ **在当前草图里画一段圆弧**（圆心 + 起点 + 终点）。⚠ Sketch geometry MUST be given as in-plane coordinate"
            "s — this is the documented exception in rule 3 (a *drawing primitive* has no named entity to select). Coor"
            "dinates are millimetres, relative to the SKETCH ORIGIN, in the sketch plane. ★ Start a sketch with solidwo"
            "rks_sketch_start first, and finish with solidworks_sketch_end; read back with the solidworks_sketch_count_"
            "* tools."
        ),
        doc=(
            "Draw an arc in the active sketch from a centre, a start point and an end point. It modifies the sketch; th"
            "e coordinates are millimetres from the sketch origin in the sketch plane, which is the documented exceptio"
            "n to naming geometry for selection."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_ellipse",
        title="Add an Ellipse to the Sketch",
        module="sw_part",
        inject="model",
        function="sketch_ellipse",
        param_alias={
            "center_x_mm": "cx",
            "center_y_mm": "cy",
            "major_x_mm": "major_x",
            "major_y_mm": "major_y",
            "minor_x_mm": "minor_x",
            "minor_y_mm": "minor_y",
            "z_mm": "z",
        },
        params=[
            Param("center_x_mm", float, description="Ellipse centre X in millimetres."),
            Param("center_y_mm", float, description="Ellipse centre Y in millimetres."),
            Param("major_x_mm", float, description="Major-axis point X in millimetres."),
            Param("major_y_mm", float, description="Major-axis point Y in millimetres."),
            Param("minor_x_mm", float, description="Minor-axis point X in millimetres."),
            Param("minor_y_mm", float, description="Minor-axis point Y in millimetres."),
            Param(
                "z_mm", float, default=0.0, description="Sketch plane Z in millimetres. Defaults to 0.0."
            ),
        ],
        evidence=(
            "★ **在当前草图里画一个整椭圆**（官方 `ISketchManager.CreateEllipse`）。★ 官方那族另有**椭圆弧**（`CreateEl"
            "lipticalArc`）—— 本工具只画整椭圆。⚠ Sketch geometry MUST be given as in-plane coordinates — this is the d"
            "ocumented exception in rule 3 (a *drawing primitive* has no named entity to select). Coordinates are milli"
            "metres, relative to the SKETCH ORIGIN, in the sketch plane. ★ Start a sketch with solidworks_sketch_start "
            "first, and finish with solidworks_sketch_end; read back with the solidworks_sketch_count_* tools."
        ),
        doc=(
            "Draw a full ellipse in the active sketch from its centre, a major-axis point and a minor-axis point. It mo"
            "difies the sketch; it draws the full ellipse and never an elliptical arc, and the coordinates are millimet"
            "res in the sketch plane."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_polygon",
        title="Add a Polygon to the Sketch",
        module="sw_part",
        inject="model",
        function="sketch_polygon",
        param_alias={"center_x_mm": "cx", "center_y_mm": "cy", "radius_mm": "radius"},
        params=[
            Param("center_x_mm", float, description="Polygon centre X in millimetres."),
            Param("center_y_mm", float, description="Polygon centre Y in millimetres."),
            Param("radius_mm", float, description="Inscribed-circle radius in millimetres."),
            Param("sides", int, default=6, description="Number of sides, at least 3. Defaults to 6."),
        ],
        evidence=(
            "★ **在当前草图里画正多边形**（**内切圆**方式 —— 官方 `CreatePolygon` 的口径）。⚠ Sketch geometry MUST be g"
            "iven as in-plane coordinates — this is the documented exception in rule 3 (a *drawing primitive* has no na"
            "med entity to select). Coordinates are millimetres, relative to the SKETCH ORIGIN, in the sketch plane. ★ "
            "Start a sketch with solidworks_sketch_start first, and finish with solidworks_sketch_end; read back with t"
            "he solidworks_sketch_count_* tools."
        ),
        doc=(
            "Draw a regular polygon in the active sketch, sized by its inscribed-circle radius. It modifies the sketch;"
            " the coordinates are millimetres from the sketch origin, and the side count must be at least three."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_slot",
        title="Add a Slot to the Sketch",
        module="sw_part",
        inject="model",
        function="sketch_slot",
        param_alias={
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
            "radius_mm": "radius",
        },
        params=[
            Param("start_x_mm", float, description="Slot start X in millimetres."),
            Param("start_y_mm", float, description="Slot start Y in millimetres."),
            Param("end_x_mm", float, description="Slot end X in millimetres."),
            Param("end_y_mm", float, description="Slot end Y in millimetres."),
            Param("radius_mm", float, description="Slot radius, which is half the slot width, in millimetres."),
        ],
        evidence=(
            "★ **在当前草图里画槽口**（直槽 / 腰形孔 —— 两点 + 半径）。⚠ Sketch geometry MUST be given as in-plane coor"
            "dinates — this is the documented exception in rule 3 (a *drawing primitive* has no named entity to select)"
            ". Coordinates are millimetres, relative to the SKETCH ORIGIN, in the sketch plane. ★ Start a sketch with s"
            "olidworks_sketch_start first, and finish with solidworks_sketch_end; read back with the solidworks_sketch_"
            "count_* tools."
        ),
        doc=(
            "Draw a straight slot in the active sketch from two centre points plus a radius. It modifies the sketch; th"
            "e coordinates are millimetres from the sketch origin, and the radius is half the slot width."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_centerline",
        title="Add a Centerline to the Sketch",
        module="sw_part",
        inject="model",
        function="sketch_centerline",
        param_alias={
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
            "z_mm": "z",
        },
        params=[
            Param("start_x_mm", float, description="Centreline start X in millimetres."),
            Param("start_y_mm", float, description="Centreline start Y in millimetres."),
            Param("end_x_mm", float, description="Centreline end X in millimetres."),
            Param("end_y_mm", float, description="Centreline end Y in millimetres."),
            Param(
                "z_mm", float, default=0.0, description="Sketch plane Z in millimetres. Defaults to 0.0."
            ),
        ],
        evidence=(
            "★ **在当前草图里画一条中心线**（官方 `ISketchManager.CreateCenterLine`）。★★ 用途：中心线可以**当旋转轴**"
            "（见 `solidworks_revolve_boss` 那族对轴的要求）——所以它不只是画一条虚线，而是**建旋转特征的前置**。⚠ Sketc"
            "h geometry MUST be given as in-plane coordinates — this is the documented exception in rule 3 (a *drawing "
            "primitive* has no named entity to select). Coordinates are millimetres, relative to the SKETCH ORIGIN, in "
            "the sketch plane. ★ Start a sketch with solidworks_sketch_start first, and finish with solidworks_sketch_e"
            "nd; read back with the solidworks_sketch_count_* tools."
        ),
        doc=(
            "Draw a centreline in the active sketch. It modifies the sketch; a centreline can act as the axis of a revo"
            "lve, so this call is a prerequisite for revolve features and not only a construction line, and the coordin"
            "ates are millimetres from the sketch origin."
        ),
    ),
]
