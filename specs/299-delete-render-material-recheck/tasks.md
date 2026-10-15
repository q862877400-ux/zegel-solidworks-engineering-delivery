# Tasks — **`DeleteRenderMaterial` 后继可调性真机复核**

**Feature**: `specs/299-delete-render-material-recheck/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-299-01 先量（读证据）**：读 `output/render-material-family-evidence.json` 的**逐条** `ok`
  ⇒ ★ 旧 `true` · ★ 新 **`false`**。
- [x] **T-299-02 定性**：★ 那份证据的 `verdict` 逐字是「★ 新旧都能调 ⇒ **可以换**」
  ⇒ ★★ **与逐条读数打架** ⇒ ★ **必须独立复验**。
- [x] **T-299-03 写探针**：`output/_probe299_render_material.py`
  （★ 按 §十七：★ 开临时零件 ⇒ 试调两个入口 ⇒ ★ **`finally` 关闭且不保存**）。
- [x] **T-299-04 真机跑**：`sw_guard --timeout 600 -- python output/_probe299_render_material.py`
  ⇒ ★ 逐条读数（★ SW rev **34.4.1**）：
  - ★ 旧 `DeleteRenderMaterial(0, False)` ⇒ **`ok=True` · `True`**
  - ★★ 新 `DeleteDisplayStateSpecificRenderMaterial(0, False, 0)` ⇒ **`ok=False` · `TypeError`**
  - ★★ `getattr` ⇒ 旧 **`method`** · 新 **`bool`**
- [x] **T-299-05 对比**：本轮 vs 既有证据**逐条一致** ✓
- [x] **T-299-06 无残留**：`sw_guard --scan` ⇒ 弹窗 **0** · 打开文档 **0** ✓
- [x] **T-299-07 写判据（先红）**：`tests/test_render_material_successor_299.py`（**5 条**）。
- [x] **T-299-08 跑红基线**：拿走证据文件 ⇒ **`2 failed, 3 passed`** ✓
- [x] **T-299-09 跑绿**：⇒ **5 passed** ✓
- [x] **T-299-10 生成器链**：7 步 `rc=0`。
- [x] **T-299-11 门禁**：`release_check.py` @3.14.7 ⇒ 日志 `output/_gate299.log`。
- [x] **T-299-12 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `tests/test_render_material_successor_299.py` | ★ **新建判据**（5 例） |
| 2 | `output/_probe299_render_material.py` / `.txt` | ★ 真机探针与读数 |
| 3 | `specs/299-delete-render-material-recheck/*` | ★ 本规格四件套 |

★ **未改**：`scripts/sw_render_material.py`（★ **边界冻结** —— 本轮**只复核、不改路由**）。

---

## 三、判据读数

| # | 判据 | ★ 改前（拿走证据） | ★ 改后 |
|---|---|---|---|
| ① | `test_the_successor_is_still_not_callable_on_this_machine` | ❌ **FAILED** | ✅ pass |
| ② | `test_take_member_and_call_are_distinguished` | ❌ **FAILED** | ✅ pass |
| ③ | `test_the_decision_is_recorded_with_its_reason` | ✅ pass | ✅ pass |
| ④ | `test_the_evidence_file_is_not_trusted_by_its_verdict` | ✅ pass | ✅ pass |
| ⑤ | `test_probe_is_reusable_and_self_contained` | ✅ pass | ✅ pass |
| — | **合计** | **2 failed, 3 passed** | **5 passed** |

---

## 四、★★★ 真机读数对照（★ 本规格的决定性证据）

| ★ 入口 | ★ 既有证据 | ★ 本轮复验 | ★ 一致？ |
|---|---|---|---|
| ★ 旧 `DeleteRenderMaterial` | ★ `ok=true` · `True` | ★ **`ok=True` · `True`** | ✅ |
| ★★ 新 `DeleteDisplayStateSpecificRenderMaterial` | ★ `ok=false` · `TypeError` | ★ **`ok=False` · `TypeError`** | ✅ |
| ★ `getattr` 形态 | —（旧证据没记） | ★ 旧 **`method`** · 新 **`bool`** | ★ **本轮新增** |
