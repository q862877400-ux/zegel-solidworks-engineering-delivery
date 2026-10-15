# Tasks — **15 条既有红全清**

**Feature**: `specs/301-fifteen-existing-reds/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-301-01 先量**：跑广域回归 ⇒ **`24 failed, 2983 passed`**；★ 逐条读红消息。
- [x] **T-301-02 ★★★ 隔离**：`git stash push -- <我改过的 10 个文件>` ⇒ **再跑一次**
  ⇒ ★★ **同样的 15 条红** ⇒ ★★★ **证明它们与我的改动无关**（★ 是**既有红**）✓
- [x] **T-301-03 定性**：15 条归**两族**：① 快照过期（13 条）② 旧行为反转（2 条）。
- [x] **T-301-04 ★★★ 头三条（键类型失配）**：AST 量出
  `_HOST_EXPR_REVIEW` 的站点是**裸文件名**（`['sw_render_material.py', …]`）、
  而 `_PLAN` 的键是 **`(文件, 行号)`** ⇒ ★★ `(f, ln) not in sites` **恒真** ⇒ 三条恒红。
- [x] **T-301-05 修根（键）**：`_PLAN` 的键改 **`(文件, 包围函数)`**；
  ★ 用 AST 量出**真实**包围函数名（`delete_render_material` · `linear_pattern` ·
  `linear_pattern_report` · `insert_local_curve_driven_pattern_report` · `insert_form_tool_report`）。
- [x] **T-301-06 移出 2 条不属 250 真命中的**：★ `KFactor`（★ 250 现判 `false-hit`）·
  ★ `MaterialIdName`（★ 不在 250 表里）⇒ ★ 两条**已在 `spec 261` 真机复验**。
- [x] **T-301-07 下调棘轮**（★ 规则 29）：`BASELINE_SITES 7→5` · `BASELINE_NAMES 6→4` ·
  `REAL_HITS 6名7处→4名5处`；★ **每处写「为什么是正当减少」**。
- [x] **T-301-08 ★★★ 补内容断言**（★ 规则 22）：
  `test_the_two_adapt_args_entries_are_closed_in_spec_261` ——
  ★ 逐字核「本表不含那两个名」+ ★「`specs/261-*/acceptance.md` 里确实写了它们」✓
- [x] **T-301-09 修 `_plan_failures`**：`sites` 是 `list[str]` ⇒ ★ 比对应是「**文件名在不在**」。
- [x] **T-301-10 同步反转旧行为**（★ 规则 28）：`test_sw_drawing_view_contract` 的兜底负例
  ⇒ ★ 改成「**不再回落**」（★ 随 `spec 256`）✓
- [x] **T-301-11 补源文件记号**：`scripts/check_dispatch_byref_guard.py` 补
  「**spec 267 的教训**」段 + 「**spec 267 **试过、已回滚****」记号（★ 判据逐字要求）。
- [x] **T-301-12 ★★★ 判据改同源**（★ 规则 16）：4 个 dispatch 测试
  **import 门禁的下界**（`BASELINE_VISIBLE` / `BASELINE_RESOLVED_SITES` / `BASELINE_BYREF_SITES`）。
- [x] **T-301-13 ★★ 负例改动态**：两处 `*_baseline_shrink_is_red` ⇒ ★ 改成「**实测 + 1**」
  （★ 硬写绝对值会随真树**失效** ⇒ 判据**静默不承重**）。
- [x] **T-301-14 修合成树期望**：`test_arity_mismatch_is_counted_not_convicted` ⇒
  ★ 期望桶从 `arity` 改成 **`starred`**（★ `spec 271` 的**正当**行为）。
- [x] **T-301-15 跑绿**：10 个文件 ⇒ **`84 passed`** ✓
- [x] **T-301-16 生成器链**：7 步 `rc=0`。
- [x] **T-301-17 门禁**：`release_check.py` @3.14.7 ⇒ 日志 `output/_gate301.log`。
- [x] **T-301-18 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `tests/test_routing_plan_real_hits.py` | ★ **键类型 + 移出 2 条 + 基线下调 + 内容断言** |
| 2 | `tests/test_handoff_todo_premises.py` | ★ `REAL_HITS` 6→4 · 站点 7→5 |
| 3 | `tests/test_handoff_todo_premises_full.py` | ★ 同上 |
| 4 | `scripts/check_dispatch_byref_guard.py` | ★ **补「spec 267 的教训」段** |
| 5 | `tests/test_sw_drawing_view_contract.py` | ★ **负例反转** |
| 6 | `tests/test_dispatch_byref_guard.py` | ★ **import 下界 + 动态负例 + `starred`** |
| 7 | `tests/test_dispatch_entry_guard.py` | ★ **import 下界** |
| 8 | `tests/test_dispatch_resolution.py` | ★ **import 下界 + 动态负例** |
| 9 | `tests/test_dispatch_call_site_dedup.py` | ★ **import 下界** |
| 10 | `specs/301-fifteen-existing-reds/*` | ★ 本规格四件套 |

★ **未改**：`tests/test_starargs_narrow_rule.py` / `_fix_rollback.py` 的**断言**
（★ 只补了**源文件**里的记号 ⇒ 它们自动绿）。

---

## 三、判据读数

| # | ★ 文件 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| 1 | `test_routing_plan_real_hits` | ❌ 3 failed | ✅ 6 passed |
| 2 | `test_handoff_todo_premises` | ❌ 1 failed | ✅ 4 passed |
| 3 | `test_handoff_todo_premises_full` | ❌ 1 failed | ✅ pass |
| 4 | `test_starargs_narrow_rule` | ❌ 1 failed | ✅ 4 passed |
| 5 | `test_starargs_fix_rollback` | ❌ 1 failed | ✅ 4 passed |
| 6 | `test_sw_drawing_view_contract` | ❌ 1 failed | ✅ 13 passed |
| 7 | `test_dispatch_byref_guard` | ❌ 4 failed | ✅ 12 passed |
| 8 | `test_dispatch_entry_guard` | ❌ 1 failed | ✅ 20 passed |
| 9 | `test_dispatch_resolution` | ❌ 2 failed | ✅ 11 passed |
| 10 | `test_dispatch_call_site_dedup` | ❌ 1 failed | ✅ 6 passed |
| — | **合计** | **15 failed, 68 passed** | **84 passed** ✓ |

---

## 四、★★★ 隔离证据（★ 本规格最重要的一步）

```
$ git stash push -- AGENTS.md docs/phase2-obsolete-status.md mcp-server/tool_specs_batch4.py \
    mcp-server/tool_specs_batch81.py mcp-server/tool_specs_batch93.py scripts/audit_call_arity.py \
    scripts/check_union_conventions.py tests/test_server_wiring.py tests/test_mcp_protocol_layer.py \
    tests/test_arity_comtypes_classification.py
$ python -m pytest <那 10 个文件> -q
15 failed, 68 passed          ← ★★ 去掉我的改动后**同样红**
$ git stash pop
```

★★★ **⇒ 证明这 15 条是**既有红**、★ 与本轮改动无关** ✓
（★ 这正是 `MEMORY.md` 事实 57 的可复用手法：「`git stash` 掉我的改动后仍失败，证明与我的改动无关」）
