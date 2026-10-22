"""★ B6-a 曲面编辑的声明式工具（5 条）。

来源
====
仓库:   本项目自身（ToolSpec 声明层）
文件:   mcp-server/tool_specs_batch68.py
定位:   ★ 2026-10-03（轮 474）★ `specs/201-toolbar-gaps` 的 **B6-a**（曲面编辑第一组）：
  平面区域 / 等距曲面 / 直纹曲面 / 删除面 / 替换面。
  ★ 实现层在 `scripts/sw_surface_edit_ops.py`；★ **真机证据**在
  `output/b6a-surface-edit-evidence.json`（★ **5/5**）。

★ **判据（★ 本批 3/5 的官方返回是 `void`）** ⇒ 一律**双判据**：
  **返回值（非假）** **且** **`sw_part.feature_names` 的特征名增量非空**
  （★ 事实 8：COM 的 bool 返回值单独不可信；★ 规则 6：不静默成功）。

★★ **两处"代际与前置"的教训**（★ 都写进了实现层的注释，也值在这里记一笔）：
  · **替换面**：一开始用「拉伸**曲面**的面」⇒ 树无增量；★ 改用**实体**的面 ⇒ **成了**
    （★ 官方语义上它要的是实体面）。
  · **删除面**：一开始用 `IModelDoc2.InsertDeleteFace2(Refill)` —— ★ **官方标 Obsolete**
    ⇒ ★ 按铁律 4 改用后继 **`IModelDocExtension.InsertDeleteFace(Option)`**，
    而它的 `Option` 有**正经枚举** `swFaceDeleteOption_e`（0..3）⇒ ★ **一换就成** ✓

★ **规则 2**（`_mm` / `_deg` 只在边界换算一次）· **规则 3**（★ 本批参数都是
  **草图平面内的长度**或**枚举/标志** ⇒ 带 `_mm` 或为枚举，**不是裸坐标**）·
  **规则 6**（★ 实现层回的是带 `verified_by` 的 dict）。

★ **两处"要按 mark 选"要写进 doc**（★ 铁律 3 第三句，★ 官方 Remarks 逐字）：
  · 替换面 ⇒ 要被替换的面 **mark=1** · 替换面 **mark=2**
  · 直纹曲面 ⇒ 边 **mark=4**

官方依据（三源）:
  · `C:\\swapi\\types\\IModelDoc2\\InsertPlanarRefSurface.md`（`bool ()`）
  · `C:\\swapi\\types\\IModelDoc2\\InsertOffsetSurface.md`（`void (Thickness, Reverse)`）
  · `C:\\swapi\\types\\IFeatureManager\\InsertRuledSurfaceFromEdge2.md`（11 参 · Type 0..4 · mark 4）
  · `C:\\swapi\\types\\IModelDocExtension\\InsertDeleteFace.md`（`bool (Option)`）
  · `C:\\swapi\\enums\\swFaceDeleteOption_e.md`（★ 0..3 的取值表）
  · `C:\\swapi\\types\\IModelDoc2\\InsertFeatureReplaceFace.md`（`void ()` + mark 1/2）
许可:   本仓库 MIT。无第三方代码引入。
覆盖:   全文件
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   mcp-server/tool_specs_batch68.py
# 定位:   B6-a 曲面编辑的声明式工具（5 条）。
# 官方依据: = 各条 ToolSpec 所包装函数的来源（见同文件内 `module=` / `function=`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_BATCH68: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_insert_planar_surface",
        title="Insert Planar Surface",
        module="sw_surface_edit_ops", function="insert_planar_surface",
        inject="model",
        param_alias={},
        params=[],
        doc="★ 平面区域：`IModelDoc2.InsertPlanarRefSurface()`（**零参数**，回 `bool`）。"
            "★ 官方语义：用**当前选中的封闭边界**（草图 / 边）生成一张平面曲面 ⇒ ★ **调用前要选好边界**。"
            "★ 真机：树 6→7，新增 `曲面-基准面1`。",
    ),
    ToolSpec(
        name="solidworks_insert_offset_surface",
        title="Insert Offset Surface",
        module="sw_surface_edit_ops", function="insert_offset_surface",
        inject="model",
        param_alias={"thickness_mm": "thickness_mm", "reverse": "reverse"},
        params=[
            Param("thickness_mm", float, description="与参考面的距离（毫米）。"),
            Param("reverse", bool, description="反向偏移（★ 布尔是标志，不是长度）。",
                  required=False, default=False),
        ],
        doc="★ 等距曲面：`IModelDoc2.InsertOffsetSurface(Thickness, Reverse)`（回 `void`）。"
            "★ 真机：树 7→8，新增 `曲面-等距1`。⚠ 官方回 `void` ⇒ 判据只能是**特征树增量**。",
    ),
    ToolSpec(
        name="solidworks_insert_ruled_surface",
        title="Insert Ruled Surface",
        module="sw_surface_edit_ops", function="insert_ruled_surface",
        inject="model",
        param_alias={k: k for k in (
            "ruled_type", "length_mm", "flip_pull_dir", "flip_dir", "trim_and_sew",
            "angle_deg", "coord_input", "x_mm", "y_mm", "z_mm", "b_connect_surface")},
        params=[
            Param("ruled_type", int, description="官方 `Type`：0=Tangent to Surface · 1=Normal to Surface · "
                                                "2=Tapered to Vector · 3=Perpendicular to Vector · 4=Sweep。"),
            Param("length_mm", float, description="距离（毫米；★ 官方说只对 Tangent/Tapered/Perpendicular 有效）。",
                  required=False, default=0.0),
            Param("flip_pull_dir", bool, description="翻转拉伸方向（★ 官方说只对 Normal/Tapered 有效）。",
                  required=False, default=False),
            Param("flip_dir", bool, description="翻转方向（★ 官方说只对 Perpendicular 有效）。",
                  required=False, default=False),
            Param("trim_and_sew", bool, description="裁剪并缝合（★ 布尔是标志）。",
                  required=False, default=True),
            Param("angle_deg", float, description="角度（度；★ 官方说只对 Tapered to Vector 有效）。",
                  required=False, default=0.0),
            Param("coord_input", bool, description="启用坐标输入（★ 官方说只对 Sweep 有效）。",
                  required=False, default=False),
            Param("x_mm", float, description="X 坐标（毫米）。", required=False, default=0.0),
            Param("y_mm", float, description="Y 坐标（毫米）。", required=False, default=0.0),
            Param("z_mm", float, description="Z 坐标（毫米）。", required=False, default=0.0),
            Param("b_connect_surface", bool, description="移除连接曲面（★ 布尔是标志）。",
                  required=False, default=False),
        ],
        doc="★ 直纹曲面：`IFeatureManager.InsertRuledSurfaceFromEdge2(…)`（**11 参**，回 `Feature`）。"
            "⚠ 官方 Remarks 逐字：「If you select an edge with a **selection mark of 4**, the default "
            "face is used.」⇒ ★ **调用前先把边按 `mark=4` 选中**。★ 真机：树 7→8，新增 `直纹曲面1`。"
            "★ 用的是 `…FromEdge2`（★ `…FromEdge` 官方标 **Obsolete**，铁律 4）。",
    ),
    ToolSpec(
        name="solidworks_insert_delete_face",
        title="Insert Delete Face",
        module="sw_surface_edit_ops", function="insert_delete_face",
        inject="model",
        param_alias={"option": "option"},
        params=[
            Param("option", int, description="`swFaceDeleteOption_e`：0=Default · 1=Patch · 2=Fill · "
                                            "3=FillWithTangent（★ 默认 0）。",
                  required=False, default=0),
        ],
        doc="★ 删除面：**`IModelDocExtension.InsertDeleteFace(Option)`**（回 `bool`）。"
            "⚠ ★ 入口在 **Extension** 上；★ `IModelDoc2.InsertDeleteFace2` 官方标 **Obsolete**（铁律 4）⇒ 用后继版。"
            "★ 真机（`option=0`）：树 7→8，新增 `删除面1`。"
            "⚠ 官方 Returns 逐字：True 表示**插入了 DeleteFace 特征**。",
    ),
    ToolSpec(
        name="solidworks_insert_replace_face",
        title="Insert Replace Face",
        module="sw_surface_edit_ops", function="insert_replace_face",
        inject="model",
        param_alias={},
        params=[],
        doc="★ 替换面：`IModelDoc2.InsertFeatureReplaceFace()`（**零参数**，回 `void`）。"
            "⚠ 官方 Remarks 逐字：调用前要**选中面** —— 要被替换的面 **mark=1**、替换面 **mark=2**。"
            "★ 真机：树 7→8，新增 `替换面1`（★ 而前置要用**实体**的面，不是曲面体的面）。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找（★ 我上一轮写成 `SPECS` 就被它拒了）
SPECS_BATCH68 = _BATCH68
