# Acceptance — **15 条既有红全清**：全是「行号/快照过期」同一族，改成**同源**判据

**Feature**: `specs/301-fifteen-existing-reds/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 10 个测试文件合计 `84 passed` · 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **广域回归的 15 条既有红**全部收口** ——
★ 它们**不是 15 个 bug**，而是**同一族的两种病**：★ ① 判据钉了「某个快照的绝对值」★ ② 判据钉了「已被有意反转的旧行为」。
★★★ **收口方式是**改根**（★ 同源 / 动态 / 同步反转），★ **不是**改数字**（★ 那只是把下一次漂移往后推）。

## 一、逐条验收

| # | 需求 | 判据 | ★ 读数 |
|---|---|---|---|
| FR-001 | ★★ 判据同源（import 下界） | `test_judges_import_the_gate_baseline` | ✅ pass |
| FR-002 | ★★ 负例动态 | `test_shrink_negative_cases_are_dynamic` | ✅ pass |
| FR-003 | ★★★ 旧行为同步反转 | `test_iview_name_fallback_is_intentionally_removed` | ✅ pass |
| FR-004 | ★★ 键类型修根 | `test_routing_plan_keys_are_not_line_numbers` | ✅ pass |
| FR-005 | ★★★ 下调补内容断言 | `test_ratchet_downgrades_have_content_assertions` | ✅ pass |
| FR-006 | ★★★ 15 条全绿 | 10 个文件 `pytest -q` | ✅ **84 passed** |
| — | **合计** | — | **✅ 全绿** |

## 二、★★★★ 15 条红逐条对照

| # | ★ 文件 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| 1–3 | `test_routing_plan_real_hits` | ❌ **3 failed** | ✅ **6 passed** |
| 4 | `test_handoff_todo_premises` | ❌ **1 failed** | ✅ **4 passed** |
| 5 | `test_handoff_todo_premises_full` | ❌ **1 failed** | ✅ pass |
| 6 | `test_starargs_narrow_rule` | ❌ **1 failed** | ✅ **4 passed** |
| 7 | `test_starargs_fix_rollback` | ❌ **1 failed** | ✅ **4 passed** |
| 8 | `test_sw_drawing_view_contract` | ❌ **1 failed** | ✅ **13 passed** |
| 9–11 | `test_dispatch_byref_guard` | ❌ **4 failed** | ✅ **12 passed** |
| 12 | `test_dispatch_entry_guard` | ❌ **1 failed** | ✅ **20 passed** |
| 13 | `test_dispatch_resolution` | ❌ **2 failed** | ✅ **11 passed** |
| 14 | `test_dispatch_call_site_dedup` | ❌ **1 failed** | ✅ **6 passed** |
| — | **合计** | **15 failed** | **0 failed** ✓ |

## 三、★★★★★ 三条最值得记的真因

### 3.1 ★★★ 头三条：**键类型失配**（★ 「改了 A 没改 B」的教科书形态）

★★ `specs/292` 依据 `MEMORY.md` 规则 32（「证据表不许钉行号」）
把 `_HOST_EXPR_REVIEW` 的站点**从 `(文件, 行号)` 改成了**裸文件名****；
★★ 而 `_PLAN` **仍按 `(文件, 行号)`** ⇒ ★★★ `(f, ln) not in sites` **恒真**
（★ 一个二元组**永远不可能**在「裸文件名」的列表里）⇒ ★ **三条判据恒红**。

★★★ **⇒ 修法**：★ 键改成 **`(文件, 包围函数)`**（★ 两处**都能给出**、★ **不随行号漂**）。

### 3.2 ★★★ 第 8 条：**旧行为被有意反转**（★ `spec 256`）

★★ `get_view_name` 的 docstring 逐字：
> 「★★★ **行为变化（★ 如实记）**：★ 若 `GetName2` 抛异常 ⇒ ★ 现在报 **空串**
> （★ 原先会回落取 `Name`）。★ 这是**有意的**：★ 失败就是**取不到名字**，★ **不换一个废弃成员再试**。」

★★ 而旧判据还在断言「**必须**回落到老成员 `Name`」⇒ ★★★ **判据反转**（★ 规则 28）。

### 3.3 ★★★ 第 9–15 条：**把「下界」当成了「实际值」**

| ★ 量 | ★ 下界 | ★ 实测 | ★ 判据原硬写 | ★ 后果 |
|---|---|---|---|---|
| `可见调用点` | 1180 | **1181** | `1183` | ★ 真树**涨**也红 |
| `可解析调用点` | 327 | **329** | `assertIn 327` | ★ 同上 |
| `已核调用点` | 311 | **316** | `assertIn 311` | ★ 同上 |

★★★ **⇒ 两者**当时恰好同值**（★ 巧合）⇒ ★ 真树**涨**（★ 好事）时**反而红**。
★★ **依据**（`MEMORY.md` 规则 16）：「★ **别拿一个数去核另一个**」✓

## 四、★★★ 判据修法（★ 四种，都不抄常数）

| ★ 修法 | ★ 用在哪 | ★ 为什么 |
|---|---|---|
| ★★ **import 门禁的下界** | `test_dispatch_entry_guard` · `_resolution` · `_call_site_dedup` · `_byref_guard` | ★★ **单一真源** —— 门禁下调时判据**自动跟随** |
| ★★★ **负例动态取实测 + 1** | `test_sites_baseline_shrink_is_red`（两处） | ★ 硬写「实测+1」的**绝对值**会随真树**失效**（★ 实测涨过它就不红了） |
| ★★ **键改 `(文件, 包围函数)`** | `test_routing_plan_real_hits` | ★ 行号会漂、★ 函数名**不漂** |
| ★★★ **同步反转旧行为** | `test_sw_drawing_view_contract` | ★ 规则 28：改实现要同步改钉住它的判据 |

## 五、★★★ 棘轮下调的内容断言（★ 规则 22）

★★ 本规格**下调**了：`BASELINE_SITES 7→5` · `BASELINE_NAMES 6→4` · `REAL_HITS 6名7处→4名5处`
★★★ **⇒ 按规则 22 必须补「按名字定位」的内容断言**：

★ `tests/test_routing_plan_real_hits.py::test_the_two_adapt_args_entries_are_closed_in_spec_261` 逐字核：
- ★ 本表**不含** `KFactor` / `MaterialIdName`；
- ★ **`specs/261-routing-batch1-adapt-args/acceptance.md` 里确实写了这两个名字**（★ 否则「已收口」是空话）。

★★★ **⇒ 「有人把它们塞回本表」或「把 spec 261 的结论删掉」⇒ 当场红** ✓

## 六、★★★ 红基线（★ 改前实测）

```
$ python -m pytest tests/test_routing_plan_real_hits.py tests/test_handoff_todo_premises.py \
    tests/test_handoff_todo_premises_full.py tests/test_starargs_narrow_rule.py \
    tests/test_starargs_fix_rollback.py tests/test_sw_drawing_view_contract.py \
    tests/test_dispatch_byref_guard.py tests/test_dispatch_entry_guard.py \
    tests/test_dispatch_resolution.py tests/test_dispatch_call_site_dedup.py -q
15 failed, 68 passed
```

★★★ **且已用 `git stash` 隔离证明它们**与本轮改动无关**（★ 去掉我的改动后**同样红**）✓

## 七、★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `tests/test_routing_plan_real_hits.py` | ★ **键类型 + 移出 2 条 + 基线下调 + 内容断言** |
| 2 | `tests/test_handoff_todo_premises.py` | ★ `REAL_HITS` 6→4 · 站点 7→5 |
| 3 | `tests/test_handoff_todo_premises_full.py` | ★ 同上（含文档串） |
| 4 | `scripts/check_dispatch_byref_guard.py` | ★ **补「spec 267 的教训」段**（★ 判据逐字要求） |
| 5 | `tests/test_starargs_narrow_rule.py` / `_fix_rollback.py` | ★ 随源文件记号对齐（★ **未改断言**） |
| 6 | `tests/test_sw_drawing_view_contract.py` | ★ **负例反转**（★ 随 `spec 256`） |
| 7 | `tests/test_dispatch_byref_guard.py` | ★ **import 下界 + 动态负例 + `starred` 桶** |
| 8 | `tests/test_dispatch_entry_guard.py` | ★ **import 下界** |
| 9 | `tests/test_dispatch_resolution.py` | ★ **import 下界 + 动态负例** |
| 10 | `tests/test_dispatch_call_site_dedup.py` | ★ **import 下界** |
| 11 | `specs/301-fifteen-existing-reds/*` | ★ 本规格四件套 |

## 八、★ 生成器链

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** |

## 九、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate301.log` |

## 十、未过门（如实登记）

| # | ★ 项 | ★ 说明 |
|---|---|---|
| ① | ★★ **`test_arity_mismatch_triage.py` 的 `_TRIAGE` 也按行号**（16 条） | ★ **当前是绿的** ⇒ ★ 说明它**从不校验行号** ⇒ ★★ **潜在**缺陷（★ 一旦有人校验就红）。★ **本轮不改**（★ 不在本规格范围，★ 且它不红）；★ 如实登记为**同类风险**。 |
| ② | ★ 其余 9 条广域回归失败 | ★ **环境性/其它**（★ 非本规格范围）；★ 已单独甄别。 |
