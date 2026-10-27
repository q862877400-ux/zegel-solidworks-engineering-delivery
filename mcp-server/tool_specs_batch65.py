"""★ ToolSpec 批 65：B1 批草图图元（3点矩形 / 平行四边形 / 切线弧 / 3点圆弧 / 部分椭圆 / 抛物线 / 圆锥 / 周边圆）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具声明）
# 文件:   mcp-server/tool_specs_batch65.py
# 定位:   ★ 2026-10-03（轮 464）★ `specs/201-toolbar-gaps` **B1 批**的 MCP 工具声明。
# ★★ 包装在 `scripts/sw_sketch_primitives.py`（★ 签名取自 `C:\\swapi\\types\\ISketchMana
# ger\\`，
#     逐条读过）；本文件只做**声明式接线** ✓
#   ★★★ **`inject="model"` 一律显式写** —— ★ 那是轮 461 刚修的坑（16 个 ToolSpec 漏声明
#     ⇒ 走 MCP 必炸），★ 而门禁 `tools/check_inject_binding.py` 现在会拦 ✓
# ★ **参数名带单位后缀**（`_mm`）而包装收短名 ⇒ 走 `param_alias`（规则 2：换算与改名在边
# 界做一次）✓
# 官方依据: `C:\swapi\types\ISketchManager\*.md`（9 个成员）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 走 `tools/check_inject_binding.py`（注入绑定）+ `scripts/check_param_binding
# .py`（参数绑定）。

from tool_registry import Param, ToolSpec

_GEOM = (
    " ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名实体）⇒ "
    "坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，"
    "再画，最后 `solidworks_sketch_end`。"
)

SPECS_BATCH65 = [
    ToolSpec(
        name="solidworks_sketch_add_3point_rectangle",
        title="Add a 3-Point Corner Rectangle (any angle)",
        module="sw_sketch_primitives",
        function="sketch_3point_corner_rectangle",
        inject="model",
        param_alias={
            "x1_mm": "x1",
            "y1_mm": "y1",
            "x2_mm": "x2",
            "y2_mm": "y2",
            "x3_mm": "x3",
            "y3_mm": "y3",
        },
        params=[
            Param("x1_mm", float, description="X of the first corner in millimetres, from the sketch origin."),
            Param("y1_mm", float, description="Y of the first corner in millimetres."),
            Param("x2_mm", float, description="X of the second corner in millimetres."),
            Param("y2_mm", float, description="Y of the second corner in millimetres."),
            Param(
                "x3_mm", float, description=(
                                    "X of the third point in millimetres, which sets the rectangle angle and height."
                                )
            ),
            Param("y3_mm", float, description="Y of the third point in millimetres."),
        ],
        evidence=(
            "Draw a 3-point corner rectangle at any angle.  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的"
            "具名实体）⇒ 坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再画，最后 `"
            "solidworks_sketch_end`。"
        ),
        doc=(
            "Draw a corner rectangle at any angle from three points in the open sketch. Creates sketch geometry in mill"
            "imetres measured from the sketch origin; start the sketch first with solidworks_sketch_start, draw, then c"
            "all solidworks_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_3point_center_rectangle",
        title="Add a 3-Point Center Rectangle (any angle)",
        module="sw_sketch_primitives",
        function="sketch_3point_center_rectangle",
        inject="model",
        param_alias={
            "center_x_mm": "x1",
            "center_y_mm": "y1",
            "x2_mm": "x2",
            "y2_mm": "y2",
            "x3_mm": "x3",
            "y3_mm": "y3",
        },
        params=[
            Param("center_x_mm", float, description="X of the rectangle centre in millimetres, from the sketch origin."),
            Param("center_y_mm", float, description="Y of the rectangle centre in millimetres."),
            Param("x2_mm", float, description="X of a corner in millimetres."),
            Param("y2_mm", float, description="Y of that corner in millimetres."),
            Param("x3_mm", float, description="X of the third point in millimetres, which sets the rectangle height."),
            Param("y3_mm", float, description="Y of the third point in millimetres."),
        ],
        evidence=(
            "Draw a 3-point CENTER rectangle (first point is the centre).  ★ 草图图元按官方文档属**规则 3 的书面例外**"
            "（图元没有可选的具名实体）⇒ 坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_star"
            "t`，再画，最后 `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw a centre rectangle from its centre point, one corner and one more point. Creates sketch geometry in m"
            "illimetres from the sketch origin; the first point is the centre, and the sketch must be open, so start it"
            " with solidworks_sketch_start and finish with solidworks_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_parallelogram",
        title="Add a Parallelogram",
        module="sw_sketch_primitives",
        function="sketch_parallelogram",
        inject="model",
        param_alias={
            "x1_mm": "x1",
            "y1_mm": "y1",
            "x2_mm": "x2",
            "y2_mm": "y2",
            "x3_mm": "x3",
            "y3_mm": "y3",
        },
        params=[
            Param("x1_mm", float, description="X of the corner in millimetres, from the sketch origin."),
            Param("y1_mm", float, description="Y of the corner in millimetres."),
            Param("x2_mm", float, description="X of the end of the first adjacent edge in millimetres."),
            Param("y2_mm", float, description="Y of the end of the first adjacent edge in millimetres."),
            Param("x3_mm", float, description="X of the end of the second adjacent edge in millimetres."),
            Param("y3_mm", float, description="Y of the end of the second adjacent edge in millimetres."),
        ],
        evidence=(
            "Draw a parallelogram (a corner plus the two adjacent edge endpoints).  ★ 草图图元按官方文档属**规则 3 的书"
            "面例外**（图元没有可选的具名实体）⇒ 坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_ske"
            "tch_start`，再画，最后 `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw a parallelogram from one corner and the ends of its two adjacent edges. Creates sketch geometry in mi"
            "llimetres from the sketch origin; start the sketch first with solidworks_sketch_start, draw, then call sol"
            "idworks_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_tangent_arc",
        title="Add a Tangent Arc",
        module="sw_sketch_primitives",
        function="sketch_tangent_arc",
        inject="model",
        param_alias={
            "end_x_mm": "x1",
            "end_y_mm": "y1",
            "through_x_mm": "x2",
            "through_y_mm": "y2",
        },
        params=[
            Param("end_x_mm", float, description="X of the arc end in millimetres, from the sketch origin."),
            Param("end_y_mm", float, description="Y of the arc end in millimetres."),
            Param(
                "through_x_mm",
                float,
                description="X of a point the arc passes through, in millimetres.",
            ),
            Param(
                "through_y_mm",
                float,
                description="Y of that point the arc passes through, in millimetres.",
            ),
            Param(
                "arc_type",
                int,
                description=(
                    "Arc type as an integer passed through unchanged, because its value table could not be found in the"
                    " available sources; defaults to 1."
                ),
                required=False,
                default=1,
            ),
        ],
        evidence=(
            "Draw an arc TANGENT to the last sketch segment. ⚠ The sketch must already contain a segment to be tangent "
            "to. ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名实体）⇒ 坐标在草图平面内、**相对草图原"
            "点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再画，最后 `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw an arc tangent to the last sketch segment, through one point and ending at another. Creates sketch ge"
            "ometry in millimetres from the sketch origin; the open sketch must already hold the segment the arc stays "
            "tangent to, and arc_type is an integer whose value table no available source documents."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_3point_arc",
        title="Add a 3-Point Arc",
        module="sw_sketch_primitives",
        function="sketch_3point_arc",
        inject="model",
        param_alias={
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
            "through_x_mm": "x3",
            "through_y_mm": "y3",
        },
        params=[
            Param("start_x_mm", float, description="X of the arc start in millimetres, from the sketch origin."),
            Param("start_y_mm", float, description="Y of the arc start in millimetres."),
            Param("end_x_mm", float, description="X of the arc end in millimetres."),
            Param("end_y_mm", float, description="Y of the arc end in millimetres."),
            Param("through_x_mm", float, description="X of a point on the arc, in millimetres."),
            Param("through_y_mm", float, description="Y of that point on the arc, in millimetres."),
        ],
        evidence=(
            "Draw a 3-point arc (start / end / a point on the arc).  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元"
            "没有可选的具名实体）⇒ 坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再"
            "画，最后 `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw an arc through three points: its start, its end and one point on the arc. Creates sketch geometry in "
            "millimetres from the sketch origin; start the sketch first with solidworks_sketch_start, draw, then call s"
            "olidworks_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_partial_ellipse",
        title="Add a Partial Ellipse (elliptical arc)",
        module="sw_sketch_primitives",
        function="sketch_elliptical_arc",
        inject="model",
        param_alias={
            "center_x_mm": "cx",
            "center_y_mm": "cy",
            "major_x_mm": "major_x",
            "major_y_mm": "major_y",
            "minor_x_mm": "minor_x",
            "minor_y_mm": "minor_y",
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
        },
        params=[
            Param("center_x_mm", float, description="X of the ellipse centre in millimetres, from the sketch origin."),
            Param("center_y_mm", float, description="Y of the ellipse centre in millimetres."),
            Param("major_x_mm", float, description="X of a point on the major axis in millimetres."),
            Param("major_y_mm", float, description="Y of that point on the major axis in millimetres."),
            Param("minor_x_mm", float, description="X of a point on the minor axis in millimetres."),
            Param("minor_y_mm", float, description="Y of that point on the minor axis in millimetres."),
            Param("start_x_mm", float, description="X of the arc start in millimetres."),
            Param("start_y_mm", float, description="Y of the arc start in millimetres."),
            Param("end_x_mm", float, description="X of the arc end in millimetres."),
            Param("end_y_mm", float, description="Y of the arc end in millimetres."),
            Param(
                "direction",
                int,
                description="Sweep direction: 1 = counter-clockwise, -1 = clockwise; defaults to 1.",
                required=False,
                default=1,
            ),
        ],
        evidence=(
            "Draw a PARTIAL ellipse (elliptical arc).  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名"
            "实体）⇒ 坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再画，最后 `soli"
            "dworks_sketch_end`。"
        ),
        doc=(
            "Draw a partial ellipse from its centre, a point on each axis and the arc start and end. Creates sketch geo"
            "metry in millimetres from the sketch origin; direction sets the sweep sense, so start the sketch first wit"
            "h solidworks_sketch_start and finish with solidworks_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_parabola",
        title="Add a Parabola",
        module="sw_sketch_primitives",
        function="sketch_parabola",
        inject="model",
        param_alias={
            "focus_x_mm": "fx",
            "focus_y_mm": "fy",
            "apex_x_mm": "ax",
            "apex_y_mm": "ay",
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
        },
        params=[
            Param("focus_x_mm", float, description="X of the focus in millimetres, from the sketch origin."),
            Param("focus_y_mm", float, description="Y of the focus in millimetres."),
            Param("apex_x_mm", float, description="X of the apex in millimetres."),
            Param("apex_y_mm", float, description="Y of the apex in millimetres."),
            Param("start_x_mm", float, description="X of the start point in millimetres."),
            Param("start_y_mm", float, description="Y of the start point in millimetres."),
            Param("end_x_mm", float, description="X of the end point in millimetres."),
            Param("end_y_mm", float, description="Y of the end point in millimetres."),
        ],
        evidence=(
            "Draw a parabola (focus + apex + two endpoints).  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选"
            "的具名实体）⇒ 坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再画，最后"
            " `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw a parabola from its focus, its apex and two points that set its ends. Creates sketch geometry in mill"
            "imetres from the sketch origin; start the sketch first with solidworks_sketch_start, draw, then call solid"
            "works_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_conic",
        title="Add a Conic Curve",
        module="sw_sketch_primitives",
        function="sketch_conic",
        inject="model",
        param_alias={
            "focus_x_mm": "fx",
            "focus_y_mm": "fy",
            "apex_x_mm": "ax",
            "apex_y_mm": "ay",
            "start_x_mm": "x1",
            "start_y_mm": "y1",
            "end_x_mm": "x2",
            "end_y_mm": "y2",
        },
        params=[
            Param("focus_x_mm", float, description="X of the focus in millimetres, from the sketch origin."),
            Param("focus_y_mm", float, description="Y of the focus in millimetres."),
            Param("apex_x_mm", float, description="X of the apex in millimetres."),
            Param("apex_y_mm", float, description="Y of the apex in millimetres."),
            Param("start_x_mm", float, description="X of the start point in millimetres."),
            Param("start_y_mm", float, description="Y of the start point in millimetres."),
            Param("end_x_mm", float, description="X of the end point in millimetres."),
            Param("end_y_mm", float, description="Y of the end point in millimetres."),
        ],
        evidence=(
            "Draw a conic curve. ⚠ Official signature is IDENTICAL in shape to CreateParabola (focus + apex + two endpo"
            "ints). ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名实体）⇒ 坐标在草图平面内、**相对草图"
            "原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再画，最后 `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw a conic curve from its focus, its apex and two points that set its ends. Creates sketch geometry in m"
            "illimetres from the sketch origin; the argument layout is identical in shape to the parabola one, so start"
            " the sketch first and finish with solidworks_sketch_end."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_add_perimeter_circle",
        title="Add a Perimeter Circle (3-point circle)",
        module="sw_sketch_primitives",
        function="sketch_perimeter_circle",
        inject="model",
        param_alias={
            "x1_mm": "x1",
            "y1_mm": "y1",
            "x2_mm": "x2",
            "y2_mm": "y2",
            "x3_mm": "x3",
            "y3_mm": "y3",
        },
        params=[
            Param("x1_mm", float, description="X of the first point in millimetres, from the sketch origin."),
            Param("y1_mm", float, description="Y of the first point in millimetres."),
            Param("x2_mm", float, description="X of the second point in millimetres."),
            Param("y2_mm", float, description="Y of the second point in millimetres."),
            Param("x3_mm", float, description="X of the third point in millimetres."),
            Param("y3_mm", float, description="Y of the third point in millimetres."),
        ],
        evidence=(
            "Draw a 3-point PERIMETER circle. ⚠ Official signature has NO Z argument (6 doubles only) — unlike its sibl"
            "ings. ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名实体）⇒ 坐标在草图平面内、**相对草图"
            "原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，再画，最后 `solidworks_sketch_end`。"
        ),
        doc=(
            "Draw a circle that passes through three points in the open sketch. Creates sketch geometry in millimetres "
            "from the sketch origin; this call takes six numbers and no Z value, unlike its sibling primitives, so star"
            "t the sketch first and finish with solidworks_sketch_end."
        ),
    ),
]
