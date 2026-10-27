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
            Param("feature_name", str, description=(
                                           "Feature name expected in the tree, spelled as this SolidWorks interface sho"
                                           "ws it."
                                       )),
            Param(
                "do_rebuild",
                bool,
                default=True,
                description="Whether to rebuild the model before reading it back. Defaults to true.",
            ),
        ],
        evidence=(
            "Read a feature back from the tree. ★ Criterion = the returned dict, not a guess."
        ),
        doc=(
            "Read one feature back from the tree to check that it really exists. It rebuilds the model unless do_rebuil"
            "d is false, then reports presence, rebuild success, the What's Wrong count and the last few feature names;"
            " ok is true only when the feature is present, the rebuild worked and the What's Wrong count is 0."
        ),
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
        doc=(
            "List the render material objects applied in the active document. Read-only; an empty document returns an e"
            "mpty list, and nothing is converted or applied."
        ),
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
            Param("x_mm", float, description="Pick point X in millimetres, where the dimension text is placed."),
            Param("y_mm", float, description="Pick point Y in millimetres, where the dimension text is placed."),
        ],
        evidence=(
            "Add a horizontal dimension at the given pick point. ★ Needs a sketch open."
        ),
        doc=(
            "Add a horizontal dimension whose text is placed at the given pick point. Requires a sketch to be open, it "
            "writes a display dimension into that sketch, and it does not save the document."
        ),
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
            Param("x_mm", float, description="Pick point X in millimetres, where the dimension text is placed."),
            Param("y_mm", float, description="Pick point Y in millimetres, where the dimension text is placed."),
        ],
        evidence=(
            "Add a vertical dimension at the given pick point. ★ Needs a sketch open."
        ),
        doc=(
            "Add a vertical dimension whose text is placed at the given pick point. Requires a sketch to be open, it wr"
            "ites a display dimension into that sketch, and it does not save the document."
        ),
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
            Param("sketch_name", str, description="Name of the sketch that defines the profile, selected with mark 0."),
            Param("angle_deg", float, description=(
                                          "Revolve angle in degrees; it is converted to radians once at this boundary."
                                      )),
            Param(
                "axis_sketch_name",
                str,
                default=None,
                description=(
                    "Name of the sketch holding the revolve axis, selected with mark 4 or 16 before the profile. Defaul"
                    "ts to unset, so no separate axis is selected."
                ),
            ),
        ],
        evidence=(
            "Revolve cut from a sketch. ★ Angle is given in degrees; converted once at this boundary."
        ),
        doc=(
            "Revolve a sketch profile as a cut and remove material around an axis. It selects the axis sketch before th"
            "e profile because that order matters, writes a cut feature into the active part and does not save the docu"
            "ment."
        ),
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
                "center_x_mm", float, description=(
                                          "Rotation centre X in millimetres, converted to metres once at this boundary."
                                      )
            ),
            Param(
                "center_y_mm", float, description=(
                                          "Rotation centre Y in millimetres, converted to metres once at this boundary."
                                      )
            ),
            Param("angle_deg", float, description=(
                                          "Rotation angle in degrees, converted to radians once at this boundary."
                                      )),
        ],
        evidence=(
            "Rotate the selected sketch entities about a centre."
        ),
        doc=(
            "Rotate the selected sketch entities about a centre point. It writes the rotated geometry into the open ske"
            "tch and does not save the document; the returned report compares the sketch bounding box and the sketch tr"
            "ansform before and after."
        ),
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
                "thickness_mm", float, description=(
                                           "Offset distance in millimetres, converted to metres once at this boundary."
                                       )
            ),
            Param(
                "reverse",
                bool,
                default=False,
                description="Whether to offset to the other side. Defaults to false.",
            ),
        ],
        evidence=(
            "Insert an offset surface from the selected face(s). ★ Selects one face itself via pre_call."
        ),
        doc=(
            "Insert an offset surface at a given distance from a face that this tool selects itself. It writes a surfac"
            "e feature into the active part and does not save the document, and the insert call returns nothing, so suc"
            "cess shows only as a new feature in the tree."
        ),
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
        doc=(
            "Insert a planar surface from the closed boundary that is currently selected, such as a sketch or a loop of"
            " edges. It writes a surface feature and does not save the document; select the closed boundary first, and "
            "success needs both a non-false return and a new feature in the tree."
        ),
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
        doc=(
            "Replace a solid face with a surface face. It writes a replace-face feature and does not save the document;"
            " select the face to replace with mark 1 and the replacement face with mark 2 first, and use solid faces ra"
            "ther than surface bodies."
        ),
    ),
    ToolSpec(
        name="solidworks_surface_untrim",
        title="Untrim Surface",
        module="sw_surface_features",
        function="untrim_surface_report",
        inject="model",
        params=[
            Param(
                "face_untrim_type", int, default=0, description=(
                                                        "Face untrim type: 0=automatic, 1=manual. Defaults to 0."
                                                    )
            ),
            Param(
                "edge_untrim_type", int, default=0, description=(
                                                        "Edge untrim type: 0=automatic, 1=manual. Defaults to 0."
                                                    )
            ),
        ],
        evidence=(
            "Untrim a surface and report what happened."
        ),
        doc=(
            "Untrim a surface so the trimmed-away part of the face grows back. It writes an untrim feature and does not"
            " save the document; it is valid only on surface parts and requires the face or edges to be preselected, an"
            "d success shows as a new feature in the tree."
        ),
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
                description=(
                    "Flatten accuracy factor from 1 (highest accuracy) to 10; the real-machine run used 4. Defaults to "
                    "4."
                ),
            ),
            Param("should_use_tears", bool, default=False, description=(
                                                               "Whether to allow tears in the flattened result. Default"
                                                               "s to false."
                                                           )),
        ],
        evidence=(
            "Flatten a surface. ★ Criterion = the feature tree gained a feature."
        ),
        doc=(
            "Flatten a surface body into a flat surface feature. It writes a flatten feature and does not save the docu"
            "ment; the tool selects the surface face with mark 1 and a vertex with mark 16 by itself, and it reports pr"
            "econditions_held false when there is no surface body to flatten."
        ),
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
        doc=(
            "Skip this tool, NOT USABLE on this machine: every entry point returns nothing and the tree stays unchanged"
            ". It is meant to sweep a surface from a selected profile and path, but it writes no geometry into the part"
            ", so do not use it and do not read a returned report as a built feature."
        ),
    ),
    ToolSpec(
        name="solidworks_surface_revolved_ref",
        title="Revolved Reference Surface",
        module="sw_surface_ref_ops",
        function="insert_revolved_ref_surface",
        inject="model",
        params=[
            Param("angle_deg", float, description=(
                                          "Revolve angle in degrees, converted to radians once here; with rev_type 1 it"
                                          " is the total angle."
                                      )),
            Param("rev_type", int, default=0, description=(
                                                  "Revolve type: 0=one direction, 1=mid-plane, 2=two directions. Defaul"
                                                  "ts to 0."
                                              )),
            Param("reverse_dir", bool, default=False, description=(
                                                          "Whether to revolve the other way. Defaults to false."
                                                      )),
        ],
        evidence=(
            "Insert a revolved reference surface."
        ),
        doc=(
            "Revolve a profile into a reference surface about a centreline. It writes a surface feature and does not sa"
            "ve the document; select the profile before calling, and 3D sketches are not supported."
        ),
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
                description=(
                    "Points as a list of [x, y, z] triples in millimetres; the API coordinate unit is assumed to be met"
                    "res, converted once here and echoed back in the report."
                ),
            )
        ],
        evidence=(
            "Insert a curve through the given XYZ points."
        ),
        doc=(
            "Insert a curve through a list of XYZ points. It writes a curve feature into the active part and does not s"
            "ave the document; success is judged by the three call returns together with a new feature in the tree."
        ),
    ),
    # ── 特征 / 焊件 / 导出 ────────────────────────────────────────
    ToolSpec(
        name="solidworks_feature_loft_cut",
        title="Loft Cut",
        module="sw_loft",
        function="create_loft_cut_report",
        inject="model",
        params=[
            Param("closed", bool, default=False, description="Whether to close the loft. Defaults to false."),
            Param(
                "use_selected_profiles",
                bool,
                default=True,
                description="Whether to use the profiles that are already selected. Defaults to true.",
            ),
        ],
        evidence=(
            "Loft cut and report the outcome."
        ),
        doc=(
            "Loft a cut through the selected sketch profiles. It writes a cut feature and does not save the document; p"
            "rofiles must be selected first and in the order you want them used, and success needs a new feature whose "
            "type name is Blend."
        ),
    ),
    ToolSpec(
        name="solidworks_weld_symbol",
        title="Insert Weld Symbol",
        module="sw_weldment",
        function="insert_weld_symbol_report",
        inject="model",
        params=[
            Param("face_index", int, default=0, description=(
                                                    "Index of the face to select before inserting the symbol. Defaults "
                                                    "to 0."
                                                )),
            Param("top", bool, default=False, description=(
                                                  "Whether to draw the symbol above the horizontal line instead of belo"
                                                  "w it. Defaults to false."
                                              )),
            Param("left", str, default="", description="Text for the left side of the symbol. Defaults to empty."),
        ],
        evidence=(
            "Insert a weld symbol and report the outcome."
        ),
        doc=(
            "Insert a weld symbol on a face of the active part. It selects the face at face_index first, writes an anno"
            "tation and does not save the document, and success is judged by reading the symbol back rather than by the"
            " returned flag."
        ),
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
        doc=(
            "Insert or close an explode line sketch in the active assembly. It writes a sketch into the assembly and do"
            "es not save it; the assembly needs an exploded view first, and success is judged by the feature tree and t"
            "he active sketch rather than by the returned flag."
        ),
    ),
]
