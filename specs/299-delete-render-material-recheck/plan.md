# Plan — **`DeleteRenderMaterial` 后继可调性真机复核**

**Feature**: `specs/299-delete-render-material-recheck/`
**日期**: 2026-10-10

---

## 一、施工顺序

| # | 步 | ★ 内容 | ★ 为什么 |
|---|---|---|---|
| 1 | **先量（读证据）** | 读 `output/render-material-family-evidence.json` 的**逐条** `ok` | ★★ 记档已写明：**以逐条为准、不按 `verdict` 判** |
| 2 | **定性** | ★ `verdict` 说「都能调」· ★ 逐条说「新入口 `false`」⇒ ★ **两者打架** | ★ 证明**必须独立复验** |
| 3 | **写探针** | `output/_probe299_render_material.py`（★ 按 §十七：开临时件 ⇒ 试调 ⇒ `finally` 关闭） | ★ 证据要**能复跑** |
| 4 | **真机跑** | `sw_guard --timeout 600` ⇒ ★ 逐条读数 | ★★ **离线读旧证据不算复核** |
| 5 | **对比** | 本轮读数 vs 既有证据**逐条** | ★ 一致 ⇒ 结论稳 |
| 6 | **无残留** | `sw_guard --scan` = 0 弹窗 · 打开文档 = **0** | ★ 事实 76 |
| 7 | **写判据（先红）** | `tests/test_render_material_successor_299.py`（5 条） | ★ 含「区分取不到/调不了」与「`verdict` 不当事实」 |
| 8 | **跑红基线** | 拿走证据文件 ⇒ **`2 failed, 3 passed`** | ★ 证明判据**真的在看证据** |
| 9 | **跑绿** | ⇒ **5 passed** | ★ |
| 10 | **门禁 + 回写** | `release_check` @3.14.7 · 四处状态 | ★ `GOAL.md` §五 |

---

## 二、★★★ 本轮的判据设计（★ 为什么是这 5 条）

| ★ 判据 | ★ 它防的是什么 |
|---|---|
| `test_the_successor_is_still_not_callable_on_this_machine` | ★★ 拿**旧证据**当结论（★ 而不复跑） |
| `test_take_member_and_call_are_distinguished` | ★★ 把「pywin32 造不出包装」误读成「API 语义不允许」 |
| `test_the_decision_is_recorded_with_its_reason` | ★ 把「刻意保留」写成无法证伪的自称 |
| `test_the_evidence_file_is_not_trusted_by_its_verdict` | ★★★ **`verdict` 与逐条打架时按 `verdict` 判**（★ 那正是既有证据的坑） |
| `test_probe_is_reusable_and_self_contained` | ★ 证据**不能复跑**（★ 探针没清理 ⇒ 留文档） |

---

## 三、★ 官方/仓内依据

| 源 | ★ 逐字 | ★ 用途 |
|---|---|---|
| `official-members-index.json` 的 `obsolete_line` | 「**Not supported in SOLIDWORKS 2011 and later. Superseded by …**」 | ★★ 官方口径（★ **比 `Obsolete` 更强**） |
| `output/render-material-family-evidence.json` | ★ 逐条 `ok`：旧 `true` · 新 `false` | ★ 既有证据（★ 判据的靶子） |
| `scripts/sw_render_material.py` 记档 | 「★★★ **证据文件里的 `verdict` 是**结论**、★ 而逐条 `ok` 才是**事实**」 | ★★ 可复用定则 |
| `MEMORY.md` 事实 47 | 「`ISketchedBendFeatureData` 的 `AccessSelections`/`SetFixedFace` 在 pywin32 迟到绑定下不可调用」 | ★ **架构性**限制的先例 |
| `AGENTS.md` §十七 | 「按 `ToolSpec` 的契约调，别手调内部实现」 | ★ 探针的调用方式 |
| `MEMORY.md` 事实 76 | 「真机探针的 `finally` 清理必须事后用护栏预检确认『0 个文档』」 | ★ 无残留 |
