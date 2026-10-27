"""第七批 MCP 工具声明：暴露候选的**收尾** 3 个。

## 来源与筛选（2026-10-01 轮 96，Spec Kit `016`）
候选来自 `tools/probe_unexposed_functions.py` 的「签名兼容现有注入」那批（17 个）。
`012`/`013` 接了 8 个；`014` 普查定性 **2 个坏了**（已记档并改成失败可见）。
**剩下 7 个里，本批再取 3 个**，另外 4 个**明确不取**（理由见下）。

| 取 | 函数 | 为什么 |
|---|---|---|
| ✅ | `sw_review.activate_model_for_preview` | 复核/截图前的准备 |
| ✅ | `sw_review.clear_selection_for_preview` | 上一条的配对操作 |
| ✅ | `sw_render_material.refresh_scene_graph` | 改外观后刷新图形（与已暴露的外观工具配套）|

| 不取 | 理由 |
|---|---|
| `sw_render_material.get_extension` | **COM 辅助**：返回 `IModelDocExtension`，不是用户操作 |
| `sw_com_traps.byref_pair` | **COM 辅助**：构造 BYREF 对，内部用 |
| `sw_weldment.iter_features_recursive` | **生成器**：注册器按值传参/返回，生成器需先物化，**本批不动** |
| `sw_assembly.iter_feature_tree` | 同上 |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch7.py
# 定位:   「孤立能力暴露」第三步（收尾）—— `012`→`013`→本批，共 11 个。
# 官方签名依据: 不适用（只做参数搬运）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH7"]


SPECS_BATCH7 = [
    ToolSpec(
        name="solidworks_activate_model_for_preview",
        title="Activate Model For Preview",
        module="sw_review",
        function="activate_model_for_preview",
        inject="model",
        evidence=(
            "Activate the model for preview/review (prepares the document for capture). ⚠ May mark the document as modi"
            "fied (view/selection state changes count)."
        ),
        doc=(
            "Activate the document to review so preview capture does not photograph another active part or sub-assembly"
            ". Modifies the active document state and may mark it as modified, because view and selection changes count"
            "."
        ),
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_clear_selection_for_preview",
        title="Clear Selection For Preview",
        module="sw_review",
        function="clear_selection_for_preview",
        inject="model",
        evidence=(
            "Clear the selection so the preview does not show highlighted entities. ⚠ May mark the document as modified"
            " (view/selection state changes count)."
        ),
        doc=(
            "Clear the current selection so the preview does not show highlighted entities. Modifies the view state and"
            " may mark the document as modified, because selection changes count."
        ),
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_refresh_scene_graph",
        title="Refresh Scene Graph",
        module="sw_render_material",
        function="refresh_scene_graph",
        inject="model",
        evidence=(
            "Refresh the graphics/scene graph, e.g. after an appearance change. ⚠ May mark the document as modified (vi"
            "ew/selection state changes count)."
        ),
        doc=(
            "Refresh the graphics scene graph so an appearance change becomes visible. Modifies the view state and may "
            "mark the document as modified, because view changes count."
        ),
        param_alias={},
        params=[
            Param(
                "update",
                bool,
                default=True,
                description="Whether to force a graphics update. Defaults to true.",
            ),
        ],
    ),
]
