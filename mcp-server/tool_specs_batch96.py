"""★ 批次 96：规格 209 · B4-5 —— 把模型标注插进工程图视图（`InsertModelAnnotations4`，8 参）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_drawing_create_missing.py`（本轮追加段）
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-5** · 外部项目 idx **205 `model_a
#           nnotations`**。
#   ★★ 裁决书的**建议落点**是 `scripts/sw_drawing.py`，★ 而**我落在 `sw_drawing_create_missing.py`**
#     —— 理由**可核**：前者只有 **29 行**、是**桥接壳**（`exec_module` 加载 subskill 再 `globals().update`），
#     往里加实现会被桥接逻辑覆盖；★ 而带视图助手（`_iter_views` / `_sum_over_views` / `_delta` /
#     `_find_view`）的是后者 —— ★ **裁决书自己要求「复用该文件已有的读侧助手，别新造」** ✓
#     ★ 这条**偏离已写进 tasks.md**（不静默）。
# 官方依据: `C:\\swapi\\types\\IDrawingDoc\\InsertModelAnnotations4.md`（8 参 + Paramete
#           rs + Returns）·
#   `C:\\swapi\\enums\\{swImportModelItemsSource_e,swInsertAnnotation_e}.md`（★ 后者 **26 个成员**位掩码）·
#   `C:\\swapi\\types\\IView\\GetAnnotationCount.md` ·
#   ★★ `C:\\swapi\\examples\\Insert_Model_Annotations_Example_VB.md`（**调用序**：
#     选中视图 → **ActivateView** → 清选区 → 调它）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 444 → **445**
# ★★ **诚实边界（别读成「成了」）**：本条在真机上**只验到"可达 + 回读可用"**，
#   ★★ **没能产出非空插入**（我们的零件**没有可插的标注/尺寸**）⇒ 能力标 **`stitched`** ✓
#   ★ 本工具**不设** `require_verified` 式硬闸 —— 因为「插不进去」在这里是**数据相关**的
#     （模型里有没有标注），★ **不是**后端到不了 ⇒ 硬闸会误杀 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH96"]

SPECS_BATCH96 = [
    ToolSpec(
        name="solidworks_drawing_insert_model_items",
        title="Insert Model Annotations into a Drawing View (InsertModelAnnotations4)",
        module="sw_drawing_create_missing", function="insert_model_annotations",
        inject="model",
        params=[
            Param("view_name", str, default="",
                  description="要操作的**视图名** —— ★ 留空 = 用当前图纸上的**第一个**视图。"),
            Param("source", str, default="entire_model",
                  description="官方 `Option`（`swImportModelItemsSource_e`）：`entire_model`(0) · "
                              "`selected_feature`(1) · `selected_component`(2) · `assembly_only`(3)。"),
            Param("types", str, default="",
                  description="官方 `Types`（`swInsertAnnotation_e` 的**位掩码**）—— 收**逗号分隔的类型名**"
                              "（可省 `swInsert` 前缀，如 `Dimensions,Planes`）。"
                              "★ 官方逐字：**只在两个 `insert_all_*` 都是 `False` 时才有意义**。"),
            Param("all_views", bool, default=False,
                  description="官方 `AllViews`：`True` 插到**所有视图**（★ 官方示例走的就是这一路）；"
                              "`False` 只插**当前选中的视图** —— ⚠ 那时**视图必须留在选区里**"
                              "（★ 真机踩过：清掉选区 ⇒ 回空数组）✓"),
            Param("duplicate_dims", bool, default=False,
                  description="官方 `DuplicateDims`：`True` = **消除重复尺寸**。"),
            Param("hidden_feature_dims", bool, default=False,
                  description="官方 `HiddenFeatureDims`：`True` 连**隐藏特征**的尺寸也插。"),
            Param("use_placement_in_sketch", bool, default=False,
                  description="官方 `UsePlacementInSketch`：`True` 按**草图里的摆放**插尺寸。"),
            Param("insert_all_annotations", bool, default=False,
                  description="官方 `InsertAllAnnotations`：`True` 插**全部标注**（忽略 `Types`）。"),
            Param("insert_all_reference_geometry", bool, default=False,
                  description="官方 `InsertAllReferenceGeometry`：`True` 插**全部参考几何**（忽略 `Types`）。"),
        ],
        doc="★ **把模型标注插进工程图视图**（官方 `IDrawingDoc::InsertModelAnnotations4`，**8 参**）—— "
            "★★ **状态：`stitched`**（真机只验到**可达 + 回读可用**，★ **没能产出非空插入**）—— "
            "原因**已查明且如实**：我们的零件是**纯坐标画出来的**（**一个尺寸都没有**），"
            "★ 而本仓的 `add_horizontal_dimension` 等助手**需要先选中实体**才建得出尺寸"
            "（官方 `AddDimension2` 摘要逐字「for **selected entities**」）⇒ ★ 那份夹具里"
            "**根本没有可插的东西** ✓ —— ★ 这是**数据相关**的失败，**不是**后端到不了。"
            "★ 调用序**照官方示例**：选中视图（`DRAWINGVIEW`）⇒ **`ActivateView`**"
            "（★ 这一步签名里看不出来）⇒（`AllViews=True` 时）清选区 ⇒ 调它 ✓ "
            "★★ **判据（规则 6）**：它回的是 **COM 标注对象数组**（**过不了 JSON 边界**）⇒ "
            "判据是 **`IView::GetAnnotationCount()` 的前后回读**"
            "（★ 本模块既有 `_sum_over_views` + `_delta`）—— ★ **不拿返回数组长度当唯一判据** ✓",
    ),
]
