"""★ B8 参考几何体的声明式工具（★ 只登记真机建成的 3 条）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）
# 文件:   mcp-server/tool_specs_batch70.py
# 定位:   ★ 2026-10-03（轮 479）★ `specs/201-toolbar-gaps` 的 **B8** + **T701**。
# 实现层在 `scripts/sw_ref_geometry.py`；★ 真机证据 `output/b8-ref-geometry-evidence.jso
# n`。
#
# ==================  ==================================================  ==========  ==
# ======
# 工具栏原文           官方成员                                             真机
# 登记
# ==================  ==================================================  ==========  ==
# ======
# 质心                 `IFeatureManager.InsertCenterOfMass()`               ✅
#  ✅
# 边界框               `IFeatureManager.InsertGlobalBoundingBox2(…)`        ✅ Status=0
#  ✅
# 坐标系               `IFeatureManager.InsertCoordinateSystem(…)`          ✅
#  ✅
# 基准面               `IFeatureManager.InsertRefPlane(6 参)`               ❌
#  ✗
# 点                   `IFeatureManager.InsertReferencePoint(4 参)`          ❌
#   ✗
# ==================  ==================================================  ==========  ==
# ======
#
#   ★★ **台账 T701 给的成员是错的**（★ 本仓 201 规格里那条）：
#     它写 `Create3DBoundingBox` ⇒ ★ 官方原话是「Creates a 3D bounding box for a
#     **cut list item in a weldment part**」⇒ ★★ **焊件切割清单专用**，
#     ★ 普通零件上不成是**应然的**。
#     ⇒ ★ 工具栏那个的真名是 **`IFeatureManager.InsertGlobalBoundingBox2`** ✓
#
#   ★★ **两个"代际"**（★ 铁律 4）：
#     · `IModelDoc2.InsertCoordinateSystem` **标 Obsolete** ⇒ 用 `IFeatureManager` 那个
#       （★ 且新版回 `Feature`、旧版回 `bool` ⇒ 判据更强）
#     · `InsertGlobalBoundingBox2` 是 `…1` 的后继（★ 本模块直接用 `…2`）
#
#   ★★ **out 参数的正确传法**（★ 这一条踩过）：
# `InsertGlobalBoundingBox2` 的第 5 个形参 `Status` 是 **out**（`swGlobalBoundingBoxResu
# lt_e`，
#     **`Success=0`**）。⚠ 裸传 `0` 真机回
#     `com_error: (-2147352571, '类型不匹配。', None, **5**)`（★ 位置 5 就是它）
#     ⇒ ★ 必须用 **`sw_connect.out_i4()`**（其 docstring 逐字：「创建 `Int32&` 出参的
#       VARIANT 包装 —— **唯一被真机验证通过的形态**」）。
#     ★★ 而**判据也因此更强**：`Status == Success(0)` 是**官方给的成败码**，
#        比"特征树有没有多东西"更直接 ✓
#
# ★ 判据 = **回对象非 None** + **特征树叶子名增量**（`sw_part.feature_names`；
# ★ 边界框那条另用 `Status`）。★ 规则 2/3/6 均遵守（★ 参数是枚举/标志，**不是裸坐标**）
# 。
#
# 官方依据（三源）:
#   · `C:\\swapi\\types\\IFeatureManager\\InsertCenterOfMass.md`（`Feature ()`）
# · `C:\\swapi\\types\\IFeatureManager\\InsertGlobalBoundingBox2.md`（5 参 · `Status` 是
#  out）
#   · `C:\\swapi\\enums\\swGlobalBoundingBoxResult_e.md`（★ **Success=0**）
#   · `C:\\swapi\\types\\IFeatureManager\\InsertCoordinateSystem.md`（3 参 → Feature）
#   · `C:\\swapi\\types\\IModelDoc2\\InsertCoordinateSystem.md`（★ **Obsolete** 那一行）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
# ★ 注：本文件**没有**头部多行 docstring（★ 上面那个是**注释块**，不是字符串）——
#   ★ 轮 476 我在 `tool_specs_batch69.py` 栽过一次（**多写了一个 `"""`**），这里刻意避开。

from __future__ import annotations

from tool_registry import Param, ToolSpec

_BATCH70: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_insert_center_of_mass",
        title="Insert Center of Mass",
        module="sw_ref_geometry",
        function="insert_center_of_mass",
        inject="model",
        param_alias={},
        params=[],
        evidence=(
            "★ 质心：`IFeatureManager.InsertCenterOfMass()`（**零参数**，回 `Feature`）。★ 真机建成（★ 判据 = 回对象非 "
            "None + 特征树增量）。"
        ),
        doc=(
            "Insert a center-of-mass feature into the active document. Creates one reference feature, and the criterion"
            " is the returned feature object together with the growth of the feature tree."
        ),
    ),
    ToolSpec(
        name="solidworks_insert_global_bounding_box",
        title="Insert Global Bounding Box",
        module="sw_ref_geometry",
        function="insert_global_bounding_box",
        inject="model",
        param_alias={
            k: k
            for k in (
                "bbox_type",
                "lwta_direction_type",
                "include_hidden_bodies",
                "include_surface_bodies",
            )
        },
        params=[
            Param(
                "bbox_type",
                int,
                description=(
                    "Bounding box fit option: 1=best fit, 2=custom plane, 3=custom coordinate system; only 2 needs a fa"
                    "ce or plane selected first. Defaults to 1."
                ),
                required=False,
                default=1,
            ),
            Param(
                "lwta_direction_type",
                int,
                description=(
                    "Length-width-thickness-along direction: 0=unspecified, 1=XYZ, 2=YXZ, 3=YZX, 6=XZY, and 7, 8, 9 for"
                    " the X, Y and Z axis directions. Defaults to 0."
                ),
                required=False,
                default=0,
            ),
            Param(
                "include_hidden_bodies",
                bool,
                description="Whether hidden bodies are included in the box. Defaults to false.",
                required=False,
                default=False,
            ),
            Param(
                "include_surface_bodies",
                bool,
                description="Whether surface bodies are included in the box. Defaults to false.",
                required=False,
                default=False,
            ),
        ],
        evidence=(
            "★ 边界框：`IFeatureManager.InsertGlobalBoundingBox2(…)`（5 参，回 `IFeature`）。★★ **台账 T701 给的 `Creat"
            "e3DBoundingBox` 是焊件切割清单专用的另一个** ——官方的才是这条。★ 第 5 个形参 `Status` 是 **out**（`swGloba"
            "lBoundingBoxResult_e`，**Success=0**）⇒ 实现层用 `sw_connect.out_i4()` 包（★ 裸传 int 会 `类型不匹配`，位"
            "置 5）。★ 真机建成：**`Status=0 (Success)`** + 特征树增量。"
        ),
        doc=(
            "Insert a global bounding box feature for the active model and report its status. Creates a reference featu"
            "re; bbox_type 2 needs a face or plane selected first, and the returned status is 0 for success."
        ),
    ),
    ToolSpec(
        name="solidworks_insert_coordinate_system",
        title="Insert Coordinate System",
        module="sw_ref_geometry",
        function="insert_coordinate_system",
        inject="model",
        param_alias={k: k for k in ("x_flipped", "y_flipped", "z_flipped")},
        params=[
            Param(
                "x_flipped",
                bool,
                description="Whether to flip the X axis direction. Defaults to false.",
                required=False,
                default=False,
            ),
            Param(
                "y_flipped",
                bool,
                description="Whether to flip the Y axis direction. Defaults to false.",
                required=False,
                default=False,
            ),
            Param(
                "z_flipped",
                bool,
                description="Whether to flip the Z axis direction. Defaults to false.",
                required=False,
                default=False,
            ),
        ],
        evidence=(
            "★ 坐标系：`IFeatureManager.InsertCoordinateSystem(…)`（3 参，回 `Feature`）。★ 用的是 `IFeatureManager` 那"
            "个 —— `IModelDoc2.InsertCoordinateSystem` 官方标 **Obsolete**（铁律 4），★ 且新版回 `Feature`、旧版回 `boo"
            "l`。★ 真机建成。"
        ),
        doc=(
            "Insert a coordinate system feature into the active part and return it. Creates a reference feature; each f"
            "lip flag reverses one axis, and this uses the feature-manager entry point rather than the obsolete documen"
            "t one."
        ),
    ),
    ToolSpec(
        name="solidworks_insert_ref_plane",
        title="Insert Reference Plane",
        module="sw_ref_geometry",
        function="insert_ref_plane",
        inject="model",
        param_alias={
            k: k
            for k in (
                "first_constraint",
                "first_angle_or_dist",
                "second_constraint",
                "second_angle_or_dist",
                "third_constraint",
                "third_angle_or_dist",
            )
        },
        params=[
            Param(
                "first_constraint",
                int,
                description=(
                    "First constraint type: 1=parallel, 4=coincident, 8=distance, 16=angle, 128=mid-plane, and option b"
                    "its such as 256=flip or 512=origin-on-curve may be added."
                ),
            ),
            Param(
                "first_angle_or_dist",
                float,
                description=(
                    "Angle or distance for the first constraint, passed through in document units because the official "
                    "call documents no unit. Defaults to 0.0."
                ),
                required=False,
                default=0.0,
            ),
            Param(
                "second_constraint",
                int,
                description="Second constraint type from the same table; 0 means unused. Defaults to 0.",
                required=False,
                default=0,
            ),
            Param(
                "second_angle_or_dist",
                float,
                description="Angle or distance for the second constraint. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
            Param(
                "third_constraint",
                int,
                description="Third constraint type from the same table; 0 means unused. Defaults to 0.",
                required=False,
                default=0,
            ),
            Param(
                "third_angle_or_dist",
                float,
                description="Angle or distance for the third constraint. Defaults to 0.0.",
                required=False,
                default=0.0,
            ),
        ],
        evidence=(
            "★ 基准面：`IFeatureManager.InsertRefPlane`（6 参，回 [[Reference plane]]）。⚠⚠ **调用前必须按 mark 选参考"
            "实体** —— 官方 Remarks 逐字给了表：**0 = First reference entity · 1 = Second · 2 = Third**。★ 真机：选一个"
            "面（**mark=0**）+ `Coincident(4)` ⇒ 树新增 `基准面1`。"
        ),
        doc=(
            "Insert a reference plane from the preselected entities, using constraint codes such as 4=coincident or 8=d"
            "istance. Creates a reference plane feature; select the entities first with marks 0, 1 and 2 for the first,"
            " second and third constraint, and the angle or distance values pass through without unit conversion."
        ),
    ),
    ToolSpec(
        name="solidworks_insert_reference_point",
        title="Insert Reference Point",
        module="sw_ref_geometry",
        function="insert_reference_point",
        inject="model",
        param_alias={
            k: k
            for k in (
                "ref_point_type",
                "along_curve_type",
                "distance_or_percent",
                "number_of_ref_points",
                "selection",
                "selection_kind",
            )
        },
        params=[
            Param(
                "ref_point_type",
                int,
                description=(
                    "Reference point type: 0=invalid, 1=undefined, 2=along curve, 3=center of edge, 4=face center, 5=fa"
                    "ce vertex projection, 6=intersection, 7=sketch point."
                ),
            ),
            Param(
                "along_curve_type",
                int,
                description=(
                    "Along-curve placement rule: 0=distance, 1=percentage, 2=evenly distributed. Defaults to 0."
                ),
                required=False,
                default=0,
            ),
            Param(
                "distance_or_percent",
                float,
                description=(
                    "Distance along the curve or percentage of it, depending on along_curve_type. Defaults to 0.0."
                ),
                required=False,
                default=0.0,
            ),
            Param(
                "number_of_ref_points",
                int,
                description=(
                    "Number of reference points to create; the official call requires exactly 1 and rejects any other v"
                    "alue. Defaults to 1."
                ),
                required=False,
                default=1,
            ),
            #: ★★ 2026-10-07（接手轮 · 规格 216 T-216-06b-2）**新增两个声明式选区入参**
            #: ——
            #: ★ 起因：★ 台账 `ref_geometry` 逐字「点（`InsertReferencePoint`）要先选实
            #: 体，
            #: **而选面必须紧接着调用**（★ 中间隔别的步骤会把选区清掉）」；★ 而解析器**
            #: 会清空选区**
            #:     （事实 503）⇒ ★ 模型**没有任何办法**在调工具前选好 ✗
            #: ★ 规则 3 **不许收裸坐标** ⇒ ★ 收**选择器字符串 + 实体种类**（★ 由函数紧邻
            #: 调用前自己选）✓
            Param(
                "selection",
                str,
                description=(
                    "Declarative selection of the entity named above, as index:<n> or __current_selection__; empty sele"
                    "cts nothing. Defaults to empty."
                ),
                required=False,
                default="",
            ),
            Param(
                "selection_kind",
                str,
                description=(
                    "Entity kind to select: FACE, EDGE or VERTEX, matched to ref_point_type so that 4 pairs with FACE a"
                    "nd 3 pairs with EDGE. Defaults to FACE."
                ),
                required=False,
                default="FACE",
            ),
        ],
        evidence=(
            "★ 点：`IFeatureManager.InsertReferencePoint`（4 参，回 [[IFeature]]）。⚠ 官方 Remarks：`NumberOfRefPoints`"
            " **必须是 1**。★ 真机：先选一个面（**mark=0**）+ `FaceCenter(4)` ⇒ 树新增 `点1`。★★ 而选面**必须紧接着调用"
            "** —— 中间隔别的步骤会把选区清掉。"
        ),
        doc=(
            "Insert a reference point on the selected entity, for example 4=face center or 3=edge center. Creates a poi"
            "nt feature; the selection has to be made immediately before the call because any step in between clears it"
            ", and only the value 1 for the point count is accepted."
        ),
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH70 = _BATCH70
