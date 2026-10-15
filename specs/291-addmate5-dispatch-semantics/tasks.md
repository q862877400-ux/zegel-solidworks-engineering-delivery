# Tasks — `AddMate5` 分流语义复核

**Feature**: `specs/291-addmate5-dispatch-semantics/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-291-01 先量**：读两处「该怎么换」段 + 官方三页 + 241 核心事实四/五 + `sw_com_traps.py` 登记表 + `_REGISTERED`。
  ★ **读数**：★ 三处权威记录**都对**；★ 两处 docstring 的「该怎么换」**都错**（★ 4 类缺陷）。
- [x] **T-291-02 查钉住**（★ 铁律 28）：`test_obsolete_addmate5_kept_on_purpose.py`（4 条）· `test_deprecated_entry_interlock.py`（`_REGISTERED`）· `test_sw_assembly_doc_contract.py`（**无** docstring 断言）。
  ★ **结论**：★ 改 docstring **不会**破既有判据（★ 只要保留「记档保留 / Obsolete / ≥2 条分流 / `IMateFeatureData` / 仍调 `AddMate5`」）。
- [x] **T-291-03 写判据（先红）**：新建 `tests/test_addmate5_dispatch_semantics.py`（**6 条**）。
  ★ 取点：★ **AST 按名字** + **按标记取段**（★ 不按行号）。
- [x] **T-291-04 跑红基线**：`pytest tests/test_addmate5_dispatch_semantics.py -q` ⇒ ★ **`3 failed, 3 passed`** ✓
- [x] **T-291-05 改**（★ 只改 docstring 的「该怎么换」段 · ★ 2 个文件）：
  - `scripts/sw_assembly.py::add_mate5_checked`：加**限定词** + **「定不下来」表态** + **后继前置** + 「本轮只订正记档、不动路由」。
  - `scripts/sw_assembly_doc.py::add_mate`：**真调用方名** `add_mate5_checked` + 同上。
- [x] **T-291-06 跑绿**：本判据 **6 passed**；★ 三条既有回归合计 **28 passed**。
- [x] **T-291-07 跑生成器链**（★ 改了 `scripts/` ⇒ 必须）：7 步全部 `rc=0` · ★ 打包副本 **471 files · pruned []**。
- [x] **T-291-08 门禁**：`release_check.py` @**3.14.7** ⇒ 日志 `output/_gate291.log`。
- [x] **T-291-09 回写四处**：`GOAL.md` §七（② 段待办 **2 → 1**）· `AUTO_HANDOFF.md` ①/② · `docs/ROADMAP.md` §一 · `memory/2026-10-09.md` · `output/AUTO_RUN_*.md` · `.specify/feature.json`。

---

## 二、改动面（★ 只有 2 个文件 · ★ 都只动 docstring）

| # | 文件 | ★ 函数 | ★ 性质 |
|---|---|---|---|
| 1 | `scripts/sw_assembly.py` | `add_mate5_checked` | ★ **仅 docstring**（★ 调用 `asm_model.AddMate5(...)` **一字不动**） |
| 2 | `scripts/sw_assembly_doc.py` | `add_mate` | ★ **仅 docstring**（★ `get_com_member(doc, "AddMate5", *args)` **一字不动**） |
| 3 | `tests/test_addmate5_dispatch_semantics.py` | — | ★ **新建判据**（6 例） |

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_official_successor_pages_state_their_preconditions` | ✅ pass | ✅ pass |
| ② | `test_how_to_switch_keeps_the_official_qualifiers` | ❌ **FAILED** | ✅ pass |
| ③ | `test_how_to_switch_says_mate_type_alone_cannot_decide` | ❌ **FAILED** | ✅ pass |
| ④ | `test_doc_site_names_the_real_caller` | ❌ **FAILED** | ✅ pass |
| ⑤ | `test_routing_is_frozen_this_round` | ✅ pass | ✅ pass |
| ⑥ | `test_pure_function_is_red_able` | ✅ pass | ✅ pass |
| — | **合计** | **3 failed, 3 passed** | **6 passed** |

---

## 四、不做（★ 登记）

- ★ **不跑 COM** · ★ **不动路由** · ★ **不动** `sw_com_traps.py` / `_REGISTERED`。
- ★ **不改** `tests/test_obsolete_addmate5_kept_on_purpose.py`（★ 4 条仍成立）。
