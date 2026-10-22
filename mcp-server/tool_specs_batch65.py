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

_GEOM = (" ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名实体）⇒ "
         "坐标在草图平面内、**相对草图原点**、单位**毫米**。★ 先 `solidworks_sketch_start`，"
         "再画，最后 `solidworks_sketch_end`。")

SPECS_BATCH65 = [
    ToolSpec(
        name="solidworks_sketch_add_3point_rectangle",
        title="Add a 3-Point Corner Rectangle (any angle)",
        module="sw_sketch_primitives", function="sketch_3point_corner_rectangle",
        inject="model",
        param_alias={"x1_mm": "x1", "y1_mm": "y1", "x2_mm": "x2",
                     "y2_mm": "y2", "x3_mm": "x3", "y3_mm": "y3"},
        params=[
            Param("x1_mm", float, description="Corner 1 X, mm."),
            Param("y1_mm", float, description="Corner 1 Y, mm."),
            Param("x2_mm", float, description="Corner 2 X, mm."),
            Param("y2_mm", float, description="Corner 2 Y, mm."),
            Param("x3_mm", float, description="Third point X (sets the angle/height), mm."),
            Param("y3_mm", float, description="Third point Y, mm."),
        ],
        doc="Draw a 3-point corner rectangle at any angle. " + _GEOM,
    ),
    ToolSpec(
        name="solidworks_sketch_add_3point_center_rectangle",
        title="Add a 3-Point Center Rectangle (any angle)",
        module="sw_sketch_primitives", function="sketch_3point_center_rectangle",
        inject="model",
        param_alias={"center_x_mm": "x1", "center_y_mm": "y1", "x2_mm": "x2",
                     "y2_mm": "y2", "x3_mm": "x3", "y3_mm": "y3"},
        params=[
            Param("center_x_mm", float, description="Centre X, mm."),
            Param("center_y_mm", float, description="Centre Y, mm."),
            Param("x2_mm", float, description="A corner X, mm."),
            Param("y2_mm", float, description="A corner Y, mm."),
            Param("x3_mm", float, description="Third point X (sets the height), mm."),
            Param("y3_mm", float, description="Third point Y, mm."),
        ],
        doc="Draw a 3-point CENTER rectangle (first point is the centre). " + _GEOM,
    ),
    ToolSpec(
        name="solidworks_sketch_add_parallelogram",
        title="Add a Parallelogram",
        module="sw_sketch_primitives", function="sketch_parallelogram",
        inject="model",
        param_alias={"x1_mm": "x1", "y1_mm": "y1", "x2_mm": "x2",
                     "y2_mm": "y2", "x3_mm": "x3", "y3_mm": "y3"},
        params=[
            Param("x1_mm", float, description="Corner X, mm."),
            Param("y1_mm", float, description="Corner Y, mm."),
            Param("x2_mm", float, description="End of one adjacent edge, X, mm."),
            Param("y2_mm", float, description="End of one adjacent edge, Y, mm."),
            Param("x3_mm", float, description="End of the other adjacent edge, X, mm."),
            Param("y3_mm", float, description="End of the other adjacent edge, Y, mm."),
        ],
        doc="Draw a parallelogram (a corner plus the two adjacent edge endpoints). " + _GEOM,
    ),
    ToolSpec(
        name="solidworks_sketch_add_tangent_arc",
        title="Add a Tangent Arc",
        module="sw_sketch_primitives", function="sketch_tangent_arc",
        inject="model",
        param_alias={"end_x_mm": "x1", "end_y_mm": "y1",
                     "through_x_mm": "x2", "through_y_mm": "y2"},
        params=[
            Param("end_x_mm", float, description="Arc end X, mm."),
            Param("end_y_mm", float, description="Arc end Y, mm."),
            Param("through_x_mm", float, description="A point the arc passes through, X, mm."),
            Param("through_y_mm", float, description="A point the arc passes through, Y, mm."),
            Param("arc_type", int, description="Official ArcType (int). ⚠ 取值表未在官方源查到 ⇒ 默认 1，未核实。",
                  required=False, default=1),
        ],
        doc=("Draw an arc TANGENT to the last sketch segment. ⚠ The sketch must already contain a "
             "segment to be tangent to." + _GEOM),
    ),
    ToolSpec(
        name="solidworks_sketch_add_3point_arc",
        title="Add a 3-Point Arc",
        module="sw_sketch_primitives", function="sketch_3point_arc",
        inject="model",
        param_alias={"start_x_mm": "x1", "start_y_mm": "y1", "end_x_mm": "x2",
                     "end_y_mm": "y2", "through_x_mm": "x3", "through_y_mm": "y3"},
        params=[
            Param("start_x_mm", float, description="Start X, mm."),
            Param("start_y_mm", float, description="Start Y, mm."),
            Param("end_x_mm", float, description="End X, mm."),
            Param("end_y_mm", float, description="End Y, mm."),
            Param("through_x_mm", float, description="A point on the arc, X, mm."),
            Param("through_y_mm", float, description="A point on the arc, Y, mm."),
        ],
        doc="Draw a 3-point arc (start / end / a point on the arc). " + _GEOM,
    ),
    ToolSpec(
        name="solidworks_sketch_add_partial_ellipse",
        title="Add a Partial Ellipse (elliptical arc)",
        module="sw_sketch_primitives", function="sketch_elliptical_arc",
        inject="model",
        param_alias={"center_x_mm": "cx", "center_y_mm": "cy",
                     "major_x_mm": "major_x", "major_y_mm": "major_y",
                     "minor_x_mm": "minor_x", "minor_y_mm": "minor_y",
                     "start_x_mm": "x1", "start_y_mm": "y1",
                     "end_x_mm": "x2", "end_y_mm": "y2"},
        params=[
            Param("center_x_mm", float, description="Ellipse centre X, mm."),
            Param("center_y_mm", float, description="Ellipse centre Y, mm."),
            Param("major_x_mm", float, description="A point on the MAJOR axis, X, mm."),
            Param("major_y_mm", float, description="A point on the MAJOR axis, Y, mm."),
            Param("minor_x_mm", float, description="A point on the MINOR axis, X, mm."),
            Param("minor_y_mm", float, description="A point on the MINOR axis, Y, mm."),
            Param("start_x_mm", float, description="Arc start X, mm."),
            Param("start_y_mm", float, description="Arc start Y, mm."),
            Param("end_x_mm", float, description="Arc end X, mm."),
            Param("end_y_mm", float, description="Arc end Y, mm."),
            Param("direction", int, description="1 = counter-clockwise, -1 = clockwise.",
                  required=False, default=1),
        ],
        doc="Draw a PARTIAL ellipse (elliptical arc). " + _GEOM,
    ),
    ToolSpec(
        name="solidworks_sketch_add_parabola",
        title="Add a Parabola",
        module="sw_sketch_primitives", function="sketch_parabola",
        inject="model",
        param_alias={"focus_x_mm": "fx", "focus_y_mm": "fy",
                     "apex_x_mm": "ax", "apex_y_mm": "ay",
                     "start_x_mm": "x1", "start_y_mm": "y1",
                     "end_x_mm": "x2", "end_y_mm": "y2"},
        params=[
            Param("focus_x_mm", float, description="Focus X, mm."),
            Param("focus_y_mm", float, description="Focus Y, mm."),
            Param("apex_x_mm", float, description="Apex X, mm."),
            Param("apex_y_mm", float, description="Apex Y, mm."),
            Param("start_x_mm", float, description="Start X, mm."),
            Param("start_y_mm", float, description="Start Y, mm."),
            Param("end_x_mm", float, description="End X, mm."),
            Param("end_y_mm", float, description="End Y, mm."),
        ],
        doc="Draw a parabola (focus + apex + two endpoints). " + _GEOM,
    ),
    ToolSpec(
        name="solidworks_sketch_add_conic",
        title="Add a Conic Curve",
        module="sw_sketch_primitives", function="sketch_conic",
        inject="model",
        param_alias={"focus_x_mm": "fx", "focus_y_mm": "fy",
                     "apex_x_mm": "ax", "apex_y_mm": "ay",
                     "start_x_mm": "x1", "start_y_mm": "y1",
                     "end_x_mm": "x2", "end_y_mm": "y2"},
        params=[
            Param("focus_x_mm", float, description="Focus X, mm."),
            Param("focus_y_mm", float, description="Focus Y, mm."),
            Param("apex_x_mm", float, description="Apex X, mm."),
            Param("apex_y_mm", float, description="Apex Y, mm."),
            Param("start_x_mm", float, description="Start X, mm."),
            Param("start_y_mm", float, description="Start Y, mm."),
            Param("end_x_mm", float, description="End X, mm."),
            Param("end_y_mm", float, description="End Y, mm."),
        ],
        doc=("Draw a conic curve. ⚠ Official signature is IDENTICAL in shape to CreateParabola "
             "(focus + apex + two endpoints)." + _GEOM),
    ),
    ToolSpec(
        name="solidworks_sketch_add_perimeter_circle",
        title="Add a Perimeter Circle (3-point circle)",
        module="sw_sketch_primitives", function="sketch_perimeter_circle",
        inject="model",
        param_alias={"x1_mm": "x1", "y1_mm": "y1", "x2_mm": "x2",
                     "y2_mm": "y2", "x3_mm": "x3", "y3_mm": "y3"},
        params=[
            Param("x1_mm", float, description="Point 1 X, mm."),
            Param("y1_mm", float, description="Point 1 Y, mm."),
            Param("x2_mm", float, description="Point 2 X, mm."),
            Param("y2_mm", float, description="Point 2 Y, mm."),
            Param("x3_mm", float, description="Point 3 X, mm."),
            Param("y3_mm", float, description="Point 3 Y, mm."),
        ],
        doc=("Draw a 3-point PERIMETER circle. ⚠ Official signature has NO Z argument "
             "(6 doubles only) — unlike its siblings." + _GEOM),
    ),
]
