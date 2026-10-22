"""第八批 MCP 工具声明：**第三个候选池**（未暴露 + 只被测试调用）。

## 为什么要换池子（2026-10-01 轮 97，Spec Kit `017`）
`012`/`013`/`016` 用「**孤立**」（既没暴露、也没人调用）选候选。
轮 97 想暴露"特征树遍历"时撞见 `sw_review.collect_model_summary` ——
**它已经遍历特征树并返回 JSON-ready 数据**，正是要的能力，**却没暴露**。
查它为什么没被发现：**它只被测试调用** ⇒ **两个口径都排除了它**。

★ **而这一池特性最好**：**有测试 ⇒ 跑过的概率高** · **未暴露 ⇒ 用户够不到**。
⇒ 本批从这池（12 个）取 3 个，**不取需要传 `spec` 数据类对象的**（那些要另设计展平）。

| 取 | 函数 | 为什么 |
|---|---|---|
| ✅ | `sw_review.collect_model_summary` | **特征树摘要**（本轮起念的那个能力）|
| ✅ | `sw_costing.get_costing_manager` | Costing 管理器（护城河域之一）|
| ✅ | `sw_simulation_study_options.list_setter_summary` | 研究选项设置器清单（**无参**）|

| 不取 | 理由 |
|---|---|
| `create_render_material` / `create_external_spur_gear` | 收 `spec` **数据类对象** ⇒ 需先设计展平 |
| `add_render_material` | 收 `material` 对象 ⇒ 同上 |
| `create_cut_list` | **已定性为后端不可用**（`014`/`015`）|
| `extrude_midplane` / `auto_dimension_sketch` | 参数带默认对象（`sketch` / `sketch_segments`）⇒ 需先查默认语义 |
| `get_mass_property_override_options` | **已定性为后端不可用** |
| `reset_labels` | GUI 标签重置，不是建模能力 |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch8.py
# 定位:   「换口径」后的第一批 —— 从「只被测试调用」池子里取。
# 官方签名依据: 不适用（只做参数搬运）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH8"]


SPECS_BATCH8 = [
    ToolSpec(
        name="solidworks_collect_model_summary",
        title="Collect Model Summary",
        module="sw_review",
        function="collect_model_summary",
        inject="model",
        read_only=True,
        doc="Summarise the model: title, type, feature tree (name + type), save path.",
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_get_costing_manager",
        title="Get Costing Manager",
        module="sw_costing",
        function="get_costing_manager",
        inject="model",
        read_only=True,
        doc="Get the SOLIDWORKS Costing manager object for the active document.",
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_list_simulation_study_options",
        title="List Simulation Study Options",
        module="sw_simulation_study_options",
        function="list_setter_summary",
        read_only=True,
        doc="List the simulation study option setters available (no document needed).",
        param_alias={},
        params=[],
    ),
]
