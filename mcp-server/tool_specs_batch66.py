"""★ ToolSpec 批 66：B3 批草图编辑 6 个（剪裁 / 延伸 / 等距 / 圆角 / 线性阵列 / 圆周阵列）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具声明）
# 文件:   mcp-server/tool_specs_batch66.py
# 定位:   ★ 2026-10-03（轮 465）★ `specs/201-toolbar-gaps` **B3 批**的 MCP 工具声明。
# ★★ 包装在 `scripts/sw_sketch_edit_ops.py`（★ 签名与枚举逐条取自 `C:\\swapi\\`，见其来
# 源块）。
#   ★★★ **只挂验成的 6 个** —— ★ B3 的第 7 条「交叉曲线」**未验成**
#     （真因：官方前置是 3D 草图 + 两个相交面，而 `Insert3DSketch` 在本机回 `None`）
#     ⇒ ★ 按本仓纪律，**未验成的不挂**（它的包装留在模块里，等前置打通再挂）✓
# ★★ **`inject="model"` 一律显式写**（★ 轮 461 修过的坑，门禁 `check_inject_binding` 会
# 拦）✓
# ★ **选择走声明式下标**：`selection="index:0"` / `"index:0,index:1"` / `"__current_sele
# ction__"`
#     —— ★ 不收坐标（规则 3）✓
# 官方依据: `C:\swapi\types\ISketchManager\` 的 `SketchTrim` / `SketchExtend` / `SketchO
#           ffset2` /
# `CreateFillet` / `CreateLinearSketchStepAndRepeat` / `CreateCircularSketchStepAndRepea
# t`；
# 枚举 `swSketchTrimChoice_e` / `swSkOffsetCapEndType_e` / `swSkOffsetMakeConstructionTy
# pe_e`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 走注入绑定 + 参数绑定门禁；真机证在 `output/b3-sketch-edit-evidence.json`。

from tool_registry import Param, ToolSpec

_SEL = (
    " ★ 声明式选择（规则 3，不收坐标）：`index:<n>` 选当前草图第 n 段（0 基），"
    "多条用逗号 `index:0,index:1`，或 `__current_selection__` 用现有选区。"
    "★ 草图段**按名字选不中**（已知事实 32）⇒ 本工具内部按**对象**选。"
)

SPECS_BATCH66 = [
    ToolSpec(
        name="solidworks_sketch_trim",
        title="Trim Sketch Entities",
        module="sw_sketch_edit_ops",
        function="sketch_trim",
        inject="model",
        param_alias={"option": "option", "x_mm": "x", "y_mm": "y"},
        params=[
            Param("selection", str, description=(
                                        "Declarative selection of the sketch segment: 'index:<n>' for the n-th segment "
                                        "of the current sketch, several as a comma list, or '__current_selection__' to "
                                        "reuse the current selection."
                                    )),
            Param(
                "option",
                str,
                description=(
                    "Trim flavour: closest takes one segment and corner takes two, and the other accepted values are tw"
                    "o_entities, entity_point, entities, outside and inside. Defaults to 'closest'."
                ),
                required=False,
                default="closest",
            ),
            Param(
                "x_mm",
                float,
                description="Trim point X in millimetres, used by the options that take a point. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "y_mm",
                float,
                description="Trim point Y in millimetres. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
        ],
        evidence=(
            "Trim the selected sketch entities. ⚠ How many segments must be selected DEPENDS on the option (official Re"
            "marks: closest = exactly one, corner = exactly two)."
        ),
        doc=(
            "Trim the selected sketch entities. It modifies the active sketch; how many segments you must select depend"
            "s on the option, with closest taking exactly one and corner exactly two."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_extend",
        title="Extend a Sketch Entity",
        module="sw_sketch_edit_ops",
        function="sketch_extend",
        inject="model",
        param_alias={"x_mm": "x", "y_mm": "y"},
        params=[
            Param("selection", str, description=(
                                        "Declarative selection of the sketch segment: 'index:<n>' for the n-th segment "
                                        "of the current sketch, several as a comma list, or '__current_selection__' to "
                                        "reuse the current selection."
                                    )),
            Param(
                "x_mm",
                float,
                description="Extend-to X in millimetres. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "y_mm",
                float,
                description="Extend-to Y in millimetres. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
        ],
        evidence=(
            "Extend the selected sketch entity to the nearest entity."
        ),
        doc=(
            "Extend the selected sketch entity to the nearest entity. It modifies the active sketch and needs the segme"
            "nt to extend already selected; the extend-to point is used by the flavours that take one."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_offset",
        title="Offset Sketch Entities (offset entities)",
        module="sw_sketch_edit_ops",
        function="sketch_offset",
        inject="model",
        param_alias={
            "offset_mm": "offset_mm",
            "both_directions": "both_directions",
            "chain": "chain",
            "cap_ends": "cap_ends",
            "make_construction": "make_construction",
            "add_dimensions": "add_dimensions",
        },
        params=[
            Param("selection", str, description=(
                                        "Declarative selection of the sketch entities: 'index:<n>' for the n-th segment"
                                        " of the current sketch, several as a comma list, or '__current_selection__' to"
                                        " reuse the current selection."
                                    )),
            Param("offset_mm", float, description="Offset distance in millimetres."),
            Param(
                "both_directions",
                bool,
                description="Whether to offset to both sides of the entities. Defaults to false.",
                required=False,
                default=False,
            ),
            Param(
                "chain",
                bool,
                description="Whether to select the whole chain of entities. Defaults to true.",
                required=False,
                default=True,
            ),
            Param(
                "cap_ends",
                str,
                description="How to cap the ends of an open offset: none, arc or line. Defaults to 'none'.",
                required=False,
                default="none",
            ),
            Param(
                "make_construction",
                str,
                description="Which result to make construction geometry: dont, orig, offs or both. Defaults to 'dont'.",
                required=False,
                default="dont",
            ),
            Param(
                "add_dimensions",
                bool,
                description="Whether to add dimensions to the offset result. Defaults to false.",
                required=False,
                default=False,
            ),
        ],
        evidence=(
            "Offset the selected sketch entities (official swSkOffsetCapEndType_e / swSkOffsetMakeConstructionType_e va"
            "lues are used verbatim)."
        ),
        doc=(
            "Offset the selected sketch entities by a distance. It modifies the active sketch; the cap-end and construc"
            "tion options take the official enum values, and a chain selection follows the whole connected chain instea"
            "d of the picked segment alone."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_fillet",
        title="Draw a Sketch Fillet",
        module="sw_sketch_edit_ops",
        function="sketch_fillet",
        inject="model",
        param_alias={
            "radius_mm": "radius_mm",
            "constrained_corners": "constrained_corners",
        },
        params=[
            Param(
                "selection",
                str,
                description=(
                    "Declarative selection of the two segments: 'index:<n>' for a segment of the current sketch, severa"
                    "l as a comma list, or '__current_selection__' to reuse the current selection."
                ),
            ),
            Param("radius_mm", float, description="Fillet radius in millimetres."),
            Param(
                "constrained_corners",
                int,
                description="Corner-constraint option passed straight to the reference call. Defaults to 0.",
                required=False,
                default=0,
            ),
        ],
        evidence=(
            "Create a SKETCH fillet on two selected, intersecting sketch segments."
        ),
        doc=(
            "Create a fillet between two intersecting sketch segments. It modifies the active sketch and needs exactly "
            "those two segments selected; the radius is given in millimetres."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_linear_pattern",
        title="Linear Sketch Pattern",
        module="sw_sketch_edit_ops",
        function="sketch_linear_pattern",
        inject="model",
        param_alias={
            "x_count": "num_x",
            "y_count": "num_y",
            "spacing_x_mm": "spacing_x_mm",
            "spacing_y_mm": "spacing_y_mm",
            "angle_x_deg": "angle_x_deg",
            "angle_y_deg": "angle_y_deg",
            "delete_instances": "delete_instances",
        },
        params=[
            Param("selection", str, description=(
                                        "Declarative selection of the sketch entities: 'index:<n>' for the n-th segment"
                                        " of the current sketch, several as a comma list, or '__current_selection__' to"
                                        " reuse the current selection."
                                    )),
            Param(
                "x_count",
                int,
                description="Number of instances along X, a count and not a coordinate. Defaults to 2.",
                required=False,
                default=2,
            ),
            Param(
                "y_count",
                int,
                description="Number of instances along Y, a count and not a coordinate. Defaults to 1.",
                required=False,
                default=1,
            ),
            Param(
                "spacing_x_mm",
                float,
                description="Spacing along X in millimetres. Defaults to 10.0.",
                required=False,
                default=10.0,
            ),
            Param(
                "spacing_y_mm",
                float,
                description="Spacing along Y in millimetres. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "angle_x_deg",
                float,
                description="Pattern angle about X in degrees, converted once at the boundary. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "angle_y_deg",
                float,
                description="Pattern angle about Y in degrees. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "delete_instances",
                str,
                description="Instance numbers to skip, as a comma list such as '2,3'. Defaults to empty.",
                required=False,
                default="",
            ),
        ],
        evidence=(
            "Create a LINEAR sketch pattern of the selected entities (official 12-arg call)."
        ),
        doc=(
            "Create a linear sketch pattern of the selected entities. It modifies the active sketch; both counts are in"
            "stance counts rather than coordinates, and both angles are given in degrees and converted once at the boun"
            "dary."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_circular_pattern",
        title="Circular Sketch Pattern",
        module="sw_sketch_edit_ops",
        function="sketch_circular_pattern",
        inject="model",
        param_alias={
            "arc_radius_mm": "arc_radius_mm",
            "arc_angle_deg": "arc_angle_deg",
            "pattern_num": "pattern_num",
            "pattern_spacing_deg": "pattern_spacing_deg",
            "pattern_rotate": "pattern_rotate",
            "delete_instances": "delete_instances",
        },
        params=[
            Param("selection", str, description=(
                                        "Declarative selection of the sketch entities: 'index:<n>' for the n-th segment"
                                        " of the current sketch, several as a comma list, or '__current_selection__' to"
                                        " reuse the current selection."
                                    )),
            Param(
                "arc_radius_mm",
                float,
                description="Radius of the arc the instances follow, in millimetres. Defaults to 20.0.",
                required=False,
                default=20.0,
            ),
            Param(
                "arc_angle_deg",
                float,
                description="Angle of the arc the instances follow, in degrees. Defaults to 360.0.",
                required=False,
                default=360.0,
            ),
            Param(
                "pattern_num",
                int,
                description="Number of instances. Defaults to 4.",
                required=False,
                default=4,
            ),
            Param(
                "pattern_spacing_deg",
                float,
                description="Spacing between instances, in degrees. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "pattern_rotate",
                bool,
                description="Whether to rotate the instances as they are patterned. Defaults to true.",
                required=False,
                default=True,
            ),
            Param(
                "delete_instances",
                str,
                description="Instance numbers to skip, as a comma list. Defaults to empty.",
                required=False,
                default="",
            ),
        ],
        evidence=(
            "Create a CIRCULAR sketch pattern of the selected entities (official 9-arg call)."
        ),
        doc=(
            "Create a circular sketch pattern of the selected entities. It modifies the active sketch; the instances fo"
            "llow an arc that you define by radius and angle, and skipped instance numbers are left out of the pattern."
        ),
    ),
]
