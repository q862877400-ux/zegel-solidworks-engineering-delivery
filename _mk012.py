import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\012-expose-pilot")
S.mkdir(parents=True, exist_ok=True)

spec = """# 012 · 暴露试点：把 5 个孤立能力接成 MCP 工具

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
"""

plan = """# 012 · Plan

**不重造**：形式与 `tool_specs_batch1..4` 完全一致，只加一个模块 + 一行注册。

## 步骤
1. 筛「签名兼容」的孤立能力（22 个）
2. 挑 5 个只读/低风险
3. 写 `tool_specs_batch5.py`（`SPECS_BATCH5`）
4. 在 `register_capabilities.py` 的 `BATCH_MODULES` 加一行
5. 写契约测试（对着真实签名核）
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 声明手抄漂移 | 契约测试用 `inspect.signature` 核（沿用 batch1 的做法）|
| 钉死数量的测试红 | `test_expected_batch_size` 20→25，**并写明这是它的设计意图** |
| 「声明了但没注册」 | 加 SC-804：断言 `all_specs()` 里真的包含这 5 条 |
"""

tasks = """# 012 · Tasks（全部完成，轮 90）

- [x] T-801 从 308 里筛签名兼容的 ⇒ 22 个 → `→ 验收:` `python tools/probe_unexposed_functions.py`
- [x] T-802 挑 5 个只读/低风险
- [x] T-803 写 `mcp-server/tool_specs_batch5.py`
- [x] T-804 接入 `BATCH_MODULES` → `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`
- [x] T-805 契约测试 `tests/test_tool_specs_batch5.py`（**18 passed**）
- [x] T-806 更新 `test_expected_batch_size` 20→25（那是它的设计意图）
- [x] T-807 重生成地图/digest + 同步报告数字
- [x] T-808 门禁 + 回归 → `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 012 · Converge

**Converged**: 2026-10-01（轮 90）

## 结果
| 判据 | 结论 |
|---|---|
| SC-801 声明 5 条、全 `solidworks_` 前缀 | ✅ |
| SC-802/803 指向真实函数、参数在签名里 | ✅（契约测试 **18 passed**）|
| SC-804 已接入 `BATCH_MODULES` | ✅（`all_specs()` 20 → **25**）|
| SC-805 暴露面 72 → **77** | ✅ |
| SC-806 缺口 339 → **338** | ✅（**首次下降**）|
| SC-807 门禁 + 回归 | ✅ `release_check` exit 0 · **988 passed / 0 failed** |

## 不符合项 / 实测记录
1. **两处门禁红都是"改了东西没同步"**：`check_union_conventions`（地图未重生成）、
   `check_report_freshness`（数字未同步）—— 都是**正常流程**，非缺陷。
2. **一处测试红是设计意图**：`test_expected_batch_size` 钉死批次数 20 ⇒ 加批次必须改它。
   **已改成 25 并写明"这是它的设计意图：让悄悄多注册工具这件事可见"**。

## 未查证
* **5 个工具的**真机行为**未测**：契约测试只核「声明 vs 签名一致」，**不跑 COM**。
  它们是否真能用，需要真机冒烟（本轮未做）。
* 308 → **303**（本轮接了 5 个）；**剩下的仍有 303 个**，其中大部分需要新解析器或会改几何。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
