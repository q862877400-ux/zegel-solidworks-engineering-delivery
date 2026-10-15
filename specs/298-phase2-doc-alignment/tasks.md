# Tasks — **二级文档对齐**：`phase2-obsolete-status.md` 的旧措辞必须与 `sw_part.py` 的订正一致

**Feature**: `specs/298-phase2-doc-alignment/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-298-01 先量**：读两处原文 ⇒ ★ 一级真源（`sw_part.py:1457-1466`）**已订正**；
  ★ 二级文档（`docs/phase2-obsolete-status.md:36`）**仍是旧措辞**。
- [x] **T-298-02 定性**：★ 「`5` 就是现行那代」**会被读成「没有后继」**，★ 而官方**给了**跨族后继
  ⇒ ★★ 形态 = `MEMORY.md` 规则 30（「同一事实写在 N 处，改了 A 没改 B」）。
- [x] **T-298-03 查钉住**：搜「有没有测试钉住那句旧话」⇒ ★ 无 ⇒ ★ 改它**不会**破既有判据。
- [x] **T-298-04 写判据（先红）**：`tests/test_phase2_doc_alignment_298.py`（**5 条**）。
  ★ 含**撤回式引述**口径（★ 逐字沿用 `check_official_md_claims._is_retracted` 的同款词表）。
- [x] **T-298-05 跑红基线**：用 `git show HEAD:docs/phase2-obsolete-status.md` 还原改前原文
  ⇒ ★ **`3 failed, 2 passed`** ✓
- [x] **T-298-06 改**：`docs/phase2-obsolete-status.md` **改 1 行**（★ 第 36 行）——
  补**官方后继逐字** + **「跨族」口径** + **「本族最高代」** + **指回 `scripts/sw_part.py`**。
- [x] **T-298-07 跑绿**：⇒ **5 passed** ✓
- [x] **T-298-08 生成器链**：7 步 `rc=0`。
- [x] **T-298-09 门禁**：`release_check.py` @3.14.7 ⇒ 日志 `output/_gate298.log`。
- [x] **T-298-10 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `docs/phase2-obsolete-status.md` | ★ **改 1 行**（★ 第 36 行表行） |
| 2 | `tests/test_phase2_doc_alignment_298.py` | ★ **新建判据**（5 例） |
| 3 | `specs/298-phase2-doc-alignment/*` | ★ 本规格四件套 |

★ **未改**：`scripts/sw_part.py`（★ 边界冻结 —— 它 **293 已订正**）。

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_doc_no_longer_says_five_is_the_current_generation` | ❌ **FAILED** | ✅ pass |
| ② | `test_doc_carries_the_official_successor` | ❌ **FAILED** | ✅ pass |
| ③ | `test_the_two_places_agree_on_the_verdict` | ❌ **FAILED** | ✅ pass |
| ④ | `test_doc_points_back_to_the_primary_source` | ✅ pass | ✅ pass |
| ⑤ | `test_no_stale_no_successor_claim_anywhere_in_the_doc` | ✅ pass | ✅ pass |
| — | **合计** | **3 failed, 2 passed** | **5 passed** |
