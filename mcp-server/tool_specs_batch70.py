"""★ B8 参考几何体的声明式工具（★ 只登记真机建成的 3 条）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）
# 文件:   mcp-server/tool_specs_batch70.py
# 定位:   ★ 2026-10-03（轮 479）★ `specs/201-toolbar-gaps` 的 **B8** + **T701**。
#   实现层在 `scripts/sw_ref_geometry.py`；★ 真机证据 `output/b8-ref-geometry-evidence.json`。
#
#   ==================  ==================================================  ==========  ========
#   工具栏原文           官方成员                                             真机        登记
#   ==================  ==================================================  ==========  ========
#   质心                 `IFeatureManager.InsertCenterOfMass()`               ✅           ✅
#   边界框               `IFeatureManager.InsertGlobalBoundingBox2(…)`        ✅ Status=0  ✅
#   坐标系               `IFeatureManager.InsertCoordinateSystem(…)`          ✅           ✅
#   基准面               `IFeatureManager.InsertRefPlane(6 参)`               ❌           ✗
#   点                   `IFeatureManager.InsertReferencePoint(4 参)`          ❌           ✗
#   ==================  ==================================================  ==========  ========
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
#     `InsertGlobalBoundingBox2` 的第 5 个形参 `Status` 是 **out**（`swGlobalBoundingBoxResult_e`，
#     **`Success=0`**）。⚠ 裸传 `0` 真机回
#     `com_error: (-2147352571, '类型不匹配。', None, **5**)`（★ 位置 5 就是它）
#     ⇒ ★ 必须用 **`sw_connect.out_i4()`**（其 docstring 逐字：「创建 `Int32&` 出参的
#       VARIANT 包装 —— **唯一被真机验证通过的形态**」）。
#     ★★ 而**判据也因此更强**：`Status == Success(0)` 是**官方给的成败码**，
#        比"特征树有没有多东西"更直接 ✓
#
# ★ 判据 = **回对象非 None** + **特征树叶子名增量**（`sw_part.feature_names`；
#   ★ 边界框那条另用 `Status`）。★ 规则 2/3/6 均遵守（★ 参数是枚举/标志，**不是裸坐标**）。
#
# 官方依据（三源）:
#   · `C:\\swapi\\types\\IFeatureManager\\InsertCenterOfMass.md`（`Feature ()`）
#   · `C:\\swapi\\types\\IFeatureManager\\InsertGlobalBoundingBox2.md`（5 参 · `Status` 是 out）
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
        module="sw_ref_geometry", function="insert_center_of_mass",
        inject="model",
        param_alias={},
        params=[],
        doc="★ 质心：`IFeatureManager.InsertCenterOfMass()`（**零参数**，回 `Feature`）。"
            "★ 真机建成（★ 判据 = 回对象非 None + 特征树增量）。",
    ),
    ToolSpec(
        name="solidworks_insert_global_bounding_box",
        title="Insert Global Bounding Box",
        module="sw_ref_geometry", function="insert_global_bounding_box",
        inject="model",
        param_alias={k: k for k in ("bbox_type", "lwta_direction_type",
                                    "include_hidden_bodies", "include_surface_bodies")},
        params=[
            Param("bbox_type", int, description="`swGlobalBoundingBoxFitOptions_e`："
                                              "1=BestFit · 2=CustomPlane · 3=CustomCoordSys（默认 1）。"
                                              "⚠ 只有 **2=CustomPlane** 才要先选面/基准面。",
                  required=False, default=1),
            Param("lwta_direction_type", int, description="`swGlobalBBoxLWTADirectionType_e`："
                                                        "0=Unspecified · 1=LWTDir_XYZ · 2=YXZ · 3=YZX · 6=XZY · "
                                                        "7/8/9=AxisDir_X/Y/Z（默认 0）。",
                  required=False, default=0),
            Param("include_hidden_bodies", bool, description="是否含隐藏体（★ 布尔是标志）。",
                  required=False, default=False),
            Param("include_surface_bodies", bool, description="是否含曲面体（★ 布尔是标志）。",
                  required=False, default=False),
        ],
        doc="★ 边界框：`IFeatureManager.InsertGlobalBoundingBox2(…)`（5 参，回 `IFeature`）。"
            "★★ **台账 T701 给的 `Create3DBoundingBox` 是焊件切割清单专用的另一个** ——"
            "官方的才是这条。"
            "★ 第 5 个形参 `Status` 是 **out**（`swGlobalBoundingBoxResult_e`，**Success=0**）"
            "⇒ 实现层用 `sw_connect.out_i4()` 包（★ 裸传 int 会 `类型不匹配`，位置 5）。"
            "★ 真机建成：**`Status=0 (Success)`** + 特征树增量。",
    ),
    ToolSpec(
        name="solidworks_insert_coordinate_system",
        title="Insert Coordinate System",
        module="sw_ref_geometry", function="insert_coordinate_system",
        inject="model",
        param_alias={k: k for k in ("x_flipped", "y_flipped", "z_flipped")},
        params=[
            Param("x_flipped", bool, description="X 轴翻转（★ 官方形参名 `XFlippedIn`）。",
                  required=False, default=False),
            Param("y_flipped", bool, description="Y 轴翻转。", required=False, default=False),
            Param("z_flipped", bool, description="Z 轴翻转。", required=False, default=False),
        ],
        doc="★ 坐标系：`IFeatureManager.InsertCoordinateSystem(…)`（3 参，回 `Feature`）。"
            "★ 用的是 `IFeatureManager` 那个 —— `IModelDoc2.InsertCoordinateSystem` 官方标 **Obsolete**"
            "（铁律 4），★ 且新版回 `Feature`、旧版回 `bool`。★ 真机建成。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH70 = _BATCH70
