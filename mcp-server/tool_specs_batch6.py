"""第六批 MCP 工具声明：**孤立能力**里再挑 4 个（无参或纯读）。

## 为什么是这 4 个（2026-10-01 轮 93，Spec Kit `013`）
`012` 从「签名兼容现有注入」的 22 个里接了 5 个，**还剩 17 个**。
本轮接着挑，跳过两类：
* **COM 辅助/内部函数**（`get_extension` / `byref_pair` / `iter_features_recursive`）—— 不是用户操作；
* **需要新解析器**的（草图那 17 个读回函数要 `ISketch`，而 `GetActiveSketch2` **要求草图处于编辑态**
  ⇒ 本批**不做**，已记进 `013/converge.md`）。

⇒ 取这 4 个：

| 函数 | 模块 | 为什么 |
|---|---|---|
| `available_point_selectors` | `sw_geometry_selectors` | **无参纯读**：告诉 AI 有哪些点选择器可用 |
| `available_direction_selectors` | `sw_geometry_selectors` | 同上，方向选择器 |
| `collect_assembly_bom` | `sw_delivery` | 装配 BOM 表（与既有 `export_assembly_bom` **不同**：那个导出 CSV，
这个取结构化数据）|
| `get_mass_property_override_options` | `sw_export` | 质量属性覆盖选项（出图/导出前查）|

⚠ **两个无参函数不注入**（`inject=None`, `needs_model=False`）—— 它们不碰 COM 文档。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch6.py
# 定位:   「孤立能力暴露」第二步 —— 继续收**签名可直接暴露**的那批。
# 官方签名依据: 不适用（只做参数搬运）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH6"]


SPECS_BATCH6 = [
    ToolSpec(
        name="solidworks_available_point_selectors",
        title="Available Point Selectors",
        module="sw_geometry_selectors",
        function="available_point_selectors",
        read_only=True,
        doc="List the point-selector names usable when specifying geometry (no document needed).",
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_available_direction_selectors",
        title="Available Direction Selectors",
        module="sw_geometry_selectors",
        function="available_direction_selectors",
        read_only=True,
        doc="List the direction-selector names usable when specifying geometry (no document needed).",
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_collect_assembly_bom",
        title="Collect Assembly BOM",
        module="sw_delivery",
        function="collect_assembly_bom",
        inject="model",
        read_only=True,
        doc="Read the assembly BOM as structured rows (the CSV-export tool is a different one).",
        param_alias={},
        params=[
            Param(
                "include_excluded",
                bool,
                default=False,
                description="Include components excluded from the BOM; default false.",
            ),
        ],
    ),
    # ⚠⚠ **`get_mass_property_override_options` 未纳入本批**（2026-10-01 轮 93 真机实测
    # ）：
    #   它调 `IModelDocExtension.GetMassProperties(accuracy)`，而**任何参数数都报**
    # `(-2147352561, '非选择性的参数。')`；换 `GetMassProperties2(acc, outStatus, useSel
    # ected)`
    #   **能跑但返回的是扁平浮点数组**（13+ 个 float），**拿不到 `IMassProperty2`**
    #   ⇒ 该函数里 `GetOverrideOptions()` 那一步**前提本身不成立**。
    #   ★ **它不是「参数没调对」，是「从没跑通过」** —— 而它是个**孤立函数**（没人调用）
    #     ⇒ **孤立恰好掩盖了它坏掉这件事**。
    #   ⇒ 本轮**不修**（需查官方 API 换路子，超出「暴露」范围）；**如实记为缺陷**，
    #     见 `docs/orphan-functions-not-runnable.md`。
]
