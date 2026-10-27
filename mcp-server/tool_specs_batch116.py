"""第一百一十六批 MCP 工具声明：把 22 条「verified 但零工具」的能力接出来。

## ★★★★ 为什么这一批只做这件事

2026-10-18 盘查：140 条能力里 **84 有工具 / 56 零工具**；其中 **37 条 `level=verified`**
（有真机证据）却**零工具** ⇒ **已验证却拿不出来用**。这是项目「集大成」目标里
唯一同时提升广度与可用性的缺口，故单独成批。

## ★ 接之前逐条核实过（★ 否则就是假工具）

- `scripts/sw_<模块>.py` 存在 ✓
- 目标函数真存在、`inspect.signature` 能读 ✓
- `inject` 关键字名 = 目标函数**真实形参名**（本批绝大多数是 `model` / `doc`）

## ★★ 纪律：本批**不新增任何 verified 声称**

工具只是**暴露**，不改 `capabilities.yaml` 的 `level`。能力本身的验证等级由
它的 `evidence` 决定，不由「有没有工具」决定。

## ★ 参数命名（规则 2）

长度一律带 `_mm`、角度带 `_deg`；枚举与计数不带后缀；不传裸坐标（规则 3）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch116.py
# 定位:   把 22 条 verified-零工具 的能力接上 MCP 工具（业主指令「只做对目标有利的事」
#           ）。
# 官方依据: mcp-server/tool_registry.py L331–L360（ToolSpec 契约，inject 关键字名必须与
#           真实形参名一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import math

from tool_registry import Param, ToolSpec


#: ★★ 事实 503：`RESOLVERS` 会清空选区 ⇒ 要「调用方先选」的工具，选区**必须**由 `pre_cal
#: l`
#:   在注入之后重建。本批只有 `solidworks_surface_offset` 属于这一类。
#:   形状照 `tool_specs_batch74.py::_select_faces_for`；判据用**回读计数**（事实 8：
#:   `Select4` 的 bool 返回值不可信），没选够就**抛**，不静默。
def _select_faces_for(mark: int, count: int):
    """★ 造一个 `pre_call`：调目标函数前按官方 mark 选 `count` 个面。"""

    def _pick(params):  # noqa: ANN001, ARG001
        import register_capabilities as _rc

        from scripts.sw_connect import get_com_member
        from scripts.sw_part import _select_com_object

        model = _rc.RESOLVERS["model"](None)  #: ★ 与注册器取同一个对象
        try:
            get_com_member(model, "ClearSelection2", True)
        except Exception:  # noqa: BLE001
            pass
        sm = get_com_member(model, "SelectionManager")
        picked = 0
        for body in list(get_com_member(model, "GetBodies2", 0, True) or []):
            for face in list(get_com_member(body, "GetFaces") or []):
                if picked >= count:
                    break
                try:
                    _select_com_object(face, append=(picked > 0), mark=mark)
                    got = int(get_com_member(sm, "GetSelectedObjectCount2", mark) or 0)
                except Exception:  # noqa: BLE001
                    continue
                if got > picked:
                    picked = got
        if picked < count:
            raise RuntimeError(
                "预选失败：需要 %d 个面，只选到 %d 个 ⇒ ★ 不静默把「前置未成立」当成「能力不成」"
                % (count, picked)
            )

    return _pick


SPECS_BATCH116 = [
    # ── 读回 / 材质 ────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_feature_readback",
        title="Read Back One Feature",
        module="sw_feature_readback",
        function="feature_readback",
        inject="model",
        params=[
            Param("feature_name", str, description="Feature name in the tree."),
            Param(
                "do_rebuild",
                bool,
                default=True,
                description="Rebuild before reading back.",
            ),
        ],
        evidence=(
            "Read a feature back from the tree. ★ Criterion = the returned dict, not a guess."
        ),
        doc="Read a feature back from the tree. ★ Criterion = the returned dict, not a guess.",
    ),
    ToolSpec(
        name="solidworks_render_material_list",
        title="List Render Materials",
        module="sw_render_material",
        function="list_render_materials",
        inject="model",
        params=[],
        evidence=(
            "List the render materials applied in the active document."
        ),
        doc="List the render materials applied in the active document.",
    ),
    # ── 草图尺寸 / 实体 ────────────────────────────────────────────
    ToolSpec(
        name="solidworks_sketch_dimension_horizontal",
        title="Add a Horizontal Sketch Dimension",
        module="sw_sketch_dimensions",
        function="add_horizontal_dimension",
        inject="model",
        #: ★★ 单位换算（事实 2：入参毫米 · COM 侧米）—— 本仓门禁要求**恰好换算一次**。
        #:   内部实现 `add_horizontal_dimension(model, x_mm, y_mm)` 把值**原样**传给
        #:   `AddHorizontalDimension2(X, Y, Z)`（★ 该 COM 接口吃**米**）⇒ 工具层必须换算。
        derived_args=lambda p: {
            "x_mm": float(p["x_mm"]) / 1000.0,
            "y_mm": float(p["y_mm"]) / 1000.0,
        },
        params=[
            Param("x_mm", float, description="Pick point X in MILLIMETRES."),
            Param("y_mm", float, description="Pick point Y in MILLIMETRES."),
        ],
        evidence=(
            "Add a horizontal dimension at the given pick point. ★ Needs a sketch open."
        ),
        doc="Add a horizontal dimension at the given pick point. ★ Needs a sketch open.",
    ),
    ToolSpec(
        name="solidworks_sketch_dimension_vertical",
        title="Add a Vertical Sketch Dimension",
        module="sw_sketch_dimensions",
        function="add_vertical_dimension",
        inject="model",
        #: ★★ 同上：`AddVerticalDimension2(X, Y, Z)` 吃米，工具层收毫米 ⇒ 这里换算一次。
        derived_args=lambda p: {
            "x_mm": float(p["x_mm"]) / 1000.0,
            "y_mm": float(p["y_mm"]) / 1000.0,
        },
        params=[
            Param("x_mm", float, description="Pick point X in MILLIMETRES."),
            Param("y_mm", float, description="Pick point Y in MILLIMETRES."),
        ],
        evidence=(
            "Add a vertical dimension at the given pick point. ★ Needs a sketch open."
        ),
        doc="Add a vertical dimension at the given pick point. ★ Needs a sketch open.",
    ),
    ToolSpec(
        name="solidworks_feature_revolve_cut",
        title="Revolve Cut",
        module="sw_part",
        function="revolve_cut",
        inject="model",
        #: ★ 目标形参是 `angle_rad`（弧度），工具面按规则 2 一律用 `_deg` 收度
        #: ⇒ `angle_deg` 由 `derived_args` 消费（不进目标函数，故 alias 为 None），
        #:   换算在工具层边界做一次，能力层签名不动。
        param_alias={"angle_deg": None},
        derived_args=lambda p: {"angle_rad": math.radians(float(p["angle_deg"]))},
        params=[
            Param("sketch_name", str, description="Sketch that defines the profile."),
            Param("angle_deg", float, description="Revolve angle in DEGREES."),
            Param(
                "axis_sketch_name",
                str,
                default=None,
                description="Sketch holding the axis (optional).",
            ),
        ],
        evidence=(
            "Revolve cut from a sketch. ★ Angle is given in degrees; converted once at this boundary."
        ),
        doc="Revolve cut from a sketch. ★ Angle is given in degrees; converted once at this boundary.",
    ),
    #: ⚠ 2026-10-18 未接：`sw_sketch.get_sketch_slots(sketch)` —— ★ 首参名是 `sketch`，
    #: 而 `register_capabilities.RESOLVERS` 的 21 个键里**没有** `sketch`（见该文件 L396
    #: ：
    #:   「注入名只能是这张表的键」）⇒ 挂上去会在运行期抛
    #:   `TypeError: unexpected keyword argument 'model'`。
    #:   ★ 处置：本批**不接**它。要接需先在 RESOLVERS 里加一个 `resolve_sketch`，
    #:   那属于改注册器，须单独论证（★ 本轮不擅自改）。
    ToolSpec(
        name="solidworks_sketch_rotate",
        title="Rotate Sketch Entities",
        module="sw_sketch_modify_ops",
        function="sketch_rotate",
        inject="model",
        params=[
            Param(
                "center_x_mm", float, description="Rotation centre X in MILLIMETRES."
            ),
            Param(
                "center_y_mm", float, description="Rotation centre Y in MILLIMETRES."
            ),
            Param("angle_deg", float, description="Rotation angle in DEGREES."),
        ],
        evidence=(
            "Rotate the selected sketch entities about a centre."
        ),
        doc="Rotate the selected sketch entities about a centre.",
    ),
    # ── 曲面族 ───────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_surface_offset",
        title="Offset Surface",
        module="sw_surface_edit_ops",
        function="insert_offset_surface",
        inject="model",
        #: ★★ 事实 503：本工具要求调用方先选面 ⇒ 必须给 `pre_call` 重建选区。
        pre_call=_select_faces_for(mark=0, count=1),
        params=[
            Param(
                "thickness_mm", float, description="Offset thickness in MILLIMETRES."
            ),
            Param(
                "reverse",
                bool,
                default=False,
                description="Reverse the offset direction.",
            ),
        ],
        evidence=(
            "Insert an offset surface from the selected face(s). ★ Selects one face itself via pre_call."
        ),
        doc="Insert an offset surface from the selected face(s). ★ Selects one face itself via pre_call.",
    ),
    ToolSpec(
        name="solidworks_surface_planar",
        title="Planar Surface",
        module="sw_surface_edit_ops",
        function="insert_planar_surface",
        inject="model",
        params=[],
        evidence=(
            "Insert a planar surface from the selected closed sketch / edges."
        ),
        doc="Insert a planar surface from the selected closed sketch / edges.",
    ),
    ToolSpec(
        name="solidworks_surface_replace_face",
        title="Replace Face",
        module="sw_surface_edit_ops",
        function="insert_replace_face",
        inject="model",
        params=[],
        evidence=(
            "Replace a solid face with a surface face. ★ Select declaratively first."
        ),
        doc="Replace a solid face with a surface face. ★ Select declaratively first.",
    ),
    ToolSpec(
        name="solidworks_surface_untrim",
        title="Untrim Surface",
        module="sw_surface_features",
        function="untrim_surface_report",
        inject="model",
        params=[
            Param(
                "face_untrim_type", int, default=0, description="Face untrim type enum."
            ),
            Param(
                "edge_untrim_type", int, default=0, description="Edge untrim type enum."
            ),
        ],
        evidence=(
            "Untrim a surface and report what happened."
        ),
        doc="Untrim a surface and report what happened.",
    ),
    ToolSpec(
        name="solidworks_surface_flatten",
        title="Flatten Surface",
        module="sw_feature_entry_ops",
        function="create_flatten_surface",
        inject="model",
        params=[
            Param(
                "accuracy_factor",
                int,
                default=4,
                description="Flatten accuracy factor.",
            ),
            Param("should_use_tears", bool, default=False, description="Allow tears."),
        ],
        evidence=(
            "Flatten a surface. ★ Criterion = the feature tree gained a feature."
        ),
        doc="Flatten a surface. ★ Criterion = the feature tree gained a feature.",
    ),
    ToolSpec(
        name="solidworks_surface_sweep",
        title="Sweep Surface",
        module="sw_sweep",
        function="create_sweep_surface_report",
        inject="model",
        params=[],
        evidence=(
            "Sweep a surface from the selected profile and path."
        ),
        doc="Sweep a surface from the selected profile and path.",
    ),
    ToolSpec(
        name="solidworks_surface_revolved_ref",
        title="Revolved Reference Surface",
        module="sw_surface_ref_ops",
        function="insert_revolved_ref_surface",
        inject="model",
        params=[
            Param("angle_deg", float, description="Revolve angle in DEGREES."),
            Param("rev_type", int, default=0, description="Revolve type enum."),
            Param("reverse_dir", bool, default=False, description="Reverse direction."),
        ],
        evidence=(
            "Insert a revolved reference surface."
        ),
        doc="Insert a revolved reference surface.",
    ),
    ToolSpec(
        name="solidworks_curve_through_points",
        title="Curve Through XYZ Points",
        module="sw_curve_and_split",
        function="insert_curve_through_points",
        inject="model",
        params=[
            Param(
                "points_mm",
                list,
                description="Points in MILLIMETRES (list of triples).",
            )
        ],
        evidence=(
            "Insert a curve through the given XYZ points."
        ),
        doc="Insert a curve through the given XYZ points.",
    ),
    # ── 特征 / 焊件 / 导出 ────────────────────────────────────────
    ToolSpec(
        name="solidworks_feature_loft_cut",
        title="Loft Cut",
        module="sw_loft",
        function="create_loft_cut_report",
        inject="model",
        params=[
            Param("closed", bool, default=False, description="Closed loft."),
            Param(
                "use_selected_profiles",
                bool,
                default=True,
                description="Use the selected profiles.",
            ),
        ],
        evidence=(
            "Loft cut and report the outcome."
        ),
        doc="Loft cut and report the outcome.",
    ),
    ToolSpec(
        name="solidworks_weld_symbol",
        title="Insert Weld Symbol",
        module="sw_weldment",
        function="insert_weld_symbol_report",
        inject="model",
        params=[
            Param("face_index", int, default=0, description="Target face index."),
            Param("top", bool, default=False, description="Place on top."),
            Param("left", str, default="", description="Left-side text."),
        ],
        evidence=(
            "Insert a weld symbol and report the outcome."
        ),
        doc="Insert a weld symbol and report the outcome.",
    ),
    ToolSpec(
        name="solidworks_assembly_explode_line_sketch",
        title="Explode Line Sketch",
        module="sw_assembly_doc",
        function="insert_explode_line_sketch_report",
        inject="doc",
        params=[],
        evidence=(
            "Insert an explode line sketch in an assembly and report the outcome."
        ),
        doc="Insert an explode line sketch in an assembly and report the outcome.",
    ),
]
