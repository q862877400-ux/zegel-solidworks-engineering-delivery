# Tasks — **把 `COMTYPES_CALL_SITES` 从「按行号」改成「按成员名」**

**Feature**: `specs/300-comtypes-table-name-keyed/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-300-01 先量**：跑 `tests/test_arity_comtypes_classification.py` ⇒
  「★ 应当恰好 **2** 条 comtypes，★ 实际 **0**」（★ 既有红）。
- [x] **T-300-02 定性**：表登记 **671/965** · ★ 审计实得 **672/966** ⇒ ★ **各 +1**。
- [x] **T-300-03 找 +1 的来源**：工作树里 `scripts/sw_delivery.py:248` 加了**一行**
  `#: dispatch-guard: exempt internal-helper` ⇒ ★ **别人的未提交改动**（★ 不是本轮的）。
- [x] **T-300-04 读表自己的注释**：`audit_call_arity.py:196-205` 记着**前两次**同一形态
  + ★ 「更稳的做法是改成**按成员名**登记」⇒ ★★ **本轮做它**。
- [x] **T-300-05 写判据（先红）**：`tests/test_comtypes_table_name_keyed_300.py`（**5 条**）。
- [x] **T-300-06 改键**：`COMTYPES_CALL_SITES` 的键 `tuple[str,int]` → **`tuple[str,str]`**；
  `audit()` 的查找点 `COMTYPES_CALL_SITES.get((stem, lineno))` → **`.get((stem, member))`**。
- [x] **T-300-07 改既有判据**（★ 规则 28）：`test_arity_comtypes_classification` 的断言
  从 `("sw_delivery.py", 671)` 改成 **`("sw_delivery.py", "IGetDocumentNames")`**；
  ★ 并**加负例**「键不许是 `int`」。
- [x] **T-300-08 跑绿**：新判据 **5 passed**；★ 既有 `test_arity_comtypes_classification` **4 passed**。
- [x] **T-300-09 红基线**：把表换回「按当前实际行号」的旧形态 ⇒ ★ **comtypes = 0** ✓
- [x] **T-300-10 生成器链**：7 步 `rc=0`。
- [x] **T-300-11 门禁**：`release_check.py` @3.14.7 ⇒ 日志 `output/_gate300.log`。
- [x] **T-300-12 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `scripts/audit_call_arity.py` | ★ **键类型 + 1 处查找点 + 注释** |
| 2 | `tests/test_arity_comtypes_classification.py` | ★ **断言改成成员名 + 加负例** |
| 3 | `tests/test_comtypes_table_name_keyed_300.py` | ★ **新建判据**（5 例） |
| 4 | `specs/300-comtypes-table-name-keyed/*` | ★ 本规格四件套 |

★ **未改**：`scripts/sw_delivery.py`（★ 那是**别人**的未提交改动）。

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_the_table_is_keyed_by_member_not_line` | ❌ **FAILED** | ✅ pass |
| ② | `test_adding_a_comment_does_not_break_it` | ❌ **FAILED** | ✅ pass |
| ③ | `test_audit_finds_both_sites` | ❌ **FAILED** | ✅ pass |
| ④ | `test_reasons_survive_the_rekeying` | ✅ pass | ✅ pass |
| ⑤ | `test_bucket_order_is_unchanged` | ✅ pass | ✅ pass |
| — | **合计** | **3 failed, 2 passed** | **5 passed** |

★ 另有既有判据 `tests/test_arity_comtypes_classification.py`：★ 改前 **1 failed, 3 passed** ⇒ 改后 **4 passed** ✓

---

## 四、★★★ 红基线（★ 旧形态复现）

```
ac.COMTYPES_CALL_SITES = {('sw_delivery.py', 671): …, ('sw_delivery.py', 965): …}   # 旧：按行号
ac.audit('scripts/sw_delivery.py', refs)
⇒ comtypes = 0（应是 2）· doubt members = {'IGetDocumentNames', 'OpenDoc6'}
```

★★ **⇒ 旧形态**确实**产出 0 条** ⇒ ★ 判据**真的在看这个形态**（★ 不是空判据）。

---

## 五、★★ 同类风险（★ 如实登记 · ★ 本轮不改）

| # | ★ 位置 | ★ 形态 | ★ 现状 |
|---|---|---|---|
| ① | `tests/test_arity_mismatch_triage.py` 的 `_TRIAGE` | ★ **也按行号**登记（16 条） | ★ **当前是绿的** ⇒ ★ **说明它从不校验行号** ⇒ ★★ **潜在**缺陷（★ 一旦有人校验就红） |
