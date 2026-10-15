# Tasks — R8 跨天假红：比对生成物时必须先剥掉「非数据字段」（日期）

**Feature**: `specs/295-r8-crossday-false-red/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-295-01 先量（复现）**：把 `docs/union-level-audit.md` 的生成日期改成昨天 ⇒
  `check_union_conventions` 报 `[FAIL] 规范与地图存在性 · … 与最新数据**不一致**`。
- [x] **T-295-02 定性**：`git diff` 只有 **2 行**（只差日期）⇒ ★ **不是数据变了**。
- [x] **T-295-03 同类扫描**：枚举 5 条新鲜度门禁 × 各自生成器 ⇒ ★ **只有 R8 有**这个病。
- [x] **T-295-04 写判据（先红）**：`tests/test_r8_crossday_false_red_295.py`（**5 条**）。
  ★ 含**正例**（只差日期 ⇒ 不报）与**负例**（数据变了 ⇒ 必报）。
- [x] **T-295-05 跑红基线**：`pytest tests/test_r8_crossday_false_red_295.py -q` ⇒ **`3 failed, 2 passed`** ✓
  ★ 两条对照（`test_real_data_difference_is_still_red` / `test_generator_and_manifest_untouched`）本来就绿。
- [x] **T-295-06 改**：`scripts/check_union_conventions.py`
  - **加** `normalize_generated_text(text)`（★ 只替换**已知的**非数据字段：生成日期 / 生成时间）；
  - **改** R8 的比对：两侧都过归一化；★ 报错文案补「已忽略**非数据字段**」。
- [x] **T-295-07 跑绿**：`pytest tests/test_r8_crossday_false_red_295.py -q` ⇒ **5 passed** ✓
- [x] **T-295-08 端到端复验**：再把日期改成昨天 ⇒ 真门禁 **`并入规范门禁通过` · `rc=0`** ✓
- [x] **T-295-09 生成器链**（★ 改了 `scripts/` ⇒ 必须）：7 步 `rc=0`。
- [x] **T-295-10 门禁**：`release_check.py` @3.14.7。
- [x] **T-295-11 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `scripts/check_union_conventions.py` | ★ **加 1 个函数** + **改 R8 比对 2 行** + 报错文案 |
| 2 | `tests/test_r8_crossday_false_red_295.py` | ★ **新建判据**（5 例） |
| 3 | `specs/295-r8-crossday-false-red/*` | ★ 本规格四件套 |

★ **未改**：`scripts/gen_level_audit.py`（★ 生成器**应当**记录生成时间）· `capabilities.yaml` · `docs/union-level-audit.md`。

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_normalizer_is_declared_and_named` | ❌ **FAILED** | ✅ pass |
| ② | `test_normalizer_keeps_data_lines_and_drops_dates` | ❌ **FAILED** | ✅ pass |
| ③ | `test_date_only_difference_is_not_a_freshness_failure` | ❌ **FAILED** | ✅ pass |
| ④ | `test_real_data_difference_is_still_red` | ✅ pass | ✅ pass |
| ⑤ | `test_generator_and_manifest_untouched` | ✅ pass | ✅ pass |
| — | **合计** | **3 failed, 2 passed** | **5 passed** |
