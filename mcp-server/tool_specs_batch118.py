"""★ 批次 118：工程图 · 把模型标注插进图纸视图（补 `drawing_dimension_insertion` 的工具缺口）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现与来源块在 scripts/sw_drawing_annotations.py）
# 文件:   capabilities.yaml 的 `drawing_dimension_insertion`（原 not_implemented）
# 定位:   ★★ 该条原记 `not_implemented`，理由是「实现层没有对应函数」——经核那是**搜错了
#         成员名**：真正干活的是 `IDrawingDoc::InsertModelAnnotations4`（8 参），
#         子技能 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
#         的 `insert_dimensions` 早已实现，缺的只是**工具层暴露**。本批补这一格 ✓
# 官方依据: `C:\swapi\types\IDrawingDoc\InsertModelAnnotations4.md`（8 参 / 返回
#           IAnnotation 数组 / AllViews 语义）+ `InsertModelDimensions.md`（void，1 参）
#           + `C:\swapi\examples\Insert_Model_Annotations_Example_CSharp.md`（调用序）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具**
# ★★★ 等级如实：★★ 本工具**尚未真机建出非空插入** ⇒ 对应台账条目**只能到 `stitched`**
#         （红线⑥），★ 工具声明里不出现任何「已验证」措辞 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH118 = [
    ToolSpec(
        name="solidworks_drawing_insert_model_annotations",
        title="Insert Model Annotations into Drawing Views (with read-back)",
        module="sw_drawing_annotations",
        function="insert_model_annotations_report",
        inject="model",
        params=[
            Param(
                "view_name",
                str,
                default=None,
                description=(
                    "Optional drawing view name to select and activate before inserting. "
                    "Defaults to the current sheet's views."
                ),
            ),
            Param(
                "all_views",
                bool,
                default=True,
                description=(
                    "Insert into every view when true, or only the selected view when false. "
                    "Defaults to True."
                ),
            ),
        ],
        read_only=False,
        evidence=(
            "★ **把模型标注（标记为工程图的尺寸）插进当前图纸的视图** —— ★ 走官方 "
            "`IDrawingDoc::InsertModelAnnotations4`（8 参：Option / Types / AllViews / "
            "DuplicateDims / HiddenFeatureDims / UsePlacementInSketch / InsertAllAnnotations / "
            "InsertAllReferenceGeometry），★ 官方示例的调用序是「先 SelectByID2 选视图 → "
            "ActivateView → ClearSelection2 → 再插」✓ ★ 缺 4 时回退 `…3`（6 参），再不行退回 "
            "void 的 `InsertModelDimensions(0)` ✓ ★★ **判据是回读**：插入前后逐视图 "
            "`GetAnnotationCount` 求和，报 `delta`；★ **读不到就报 None 并判 ok=False**"
            "（★ 绝不把『返回 True/None』当插上了）✓ ★★★ **如实标注**：本工具**未真机建出"
            "非空插入** ⇒ 能力台账只到 `stitched`；★ 常见空结果原因：模型里没有『标记为工程图』"
            "的尺寸，或视图未激活／无可见几何 ✓"
        ),
        doc=(
            "Insert model annotations into drawing views and read the counts back. Writes "
            "annotations into the drawing and does not save the document; an empty result is "
            "reported as a failure rather than as success, and an unreadable count is reported "
            "as unknown. Falls back to the older annotation call and then to the void "
            "dimension call when the newest one is missing. Not yet verified on a real drawing "
            "that yields a non-empty insert."
        ),
    ),
]
