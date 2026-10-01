# 012 · 暴露试点：把 5 个孤立能力接成 MCP 工具

**Status**: Implemented（轮 90）

## 背景
`011` 量出 308 个「孤立能力」（既没暴露、也没人调用）。
本轮从「**签名兼容现有注入**」的那 22 个里挑 **5 个只读/低风险**的接出去。

## 挑法（**先筛再挑，不是随手选**）
1. 从 308 里筛出「第一个参数叫 `model` 或完全无参」的 ⇒ **22 个**（不需新解析器）；
2. 其中挑**纯读或改视图状态**的 5 个：

| 工具名 | 实现 | 为什么 |
|---|---|---|
| `solidworks_current_selection` | `sw_selection_spec.current_selection` | 查当前选区（AI 最需要知道"选了什么"）|
| `solidworks_clear_selection` | `sw_selection_spec.clear_selection` | 清选区（操作收尾）|
| `solidworks_set_standard_view` | `sw_review.set_standard_view` | 切标准视图（出图/复核准备）|
| `solidworks_list_render_materials` | `sw_render_material.list_render_materials` | 列外观材质（复核）|
| `solidworks_collect_appearance_evidence` | `sw_render_material.collect_appearance_evidence` | 外观证据（与证据驱动一贯做法一致）|

## 判据
| ID | 判据 |
|---|---|
| SC-801 | `tool_specs_batch5.py` 声明 5 条，名字全 `solidworks_` 前缀 |
| SC-802 | 每条指向的 `module`/`function` **真实存在** |
| SC-803 | 声明的参数名**都在真实签名里**（手抄会漂移，用 `inspect.signature` 钉）|
| SC-804 | 5 条**已接入** `register_capabilities.BATCH_MODULES`（不是"声明了没人注册"）|
| SC-805 | 暴露面从 **72 → 77**（可复算）|
| SC-806 | 缺口从 **339 → 338**（首次下降）|
| SC-807 | 门禁 + 回归不退化 |

## 明确不做
* 不接需要新解析器的（如 `sketch` 作首参的 17 个草图函数）；
* 不接会改几何的。
