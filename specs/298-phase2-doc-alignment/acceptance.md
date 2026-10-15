# Acceptance — **二级文档对齐**：`phase2-obsolete-status.md` 的旧措辞必须与 `sw_part.py` 的订正一致

**Feature**: `specs/298-phase2-doc-alignment/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立（`3 failed, 2 passed`）· 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **「同一事实写在两处、只改了一处」被收口**（★ `MEMORY.md` 规则 30 的形态）。

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | ★★ 旧措辞不作为主张 | `test_doc_no_longer_says_five_is_the_current_generation` | ❌ **FAILED** | ✅ pass |
| FR-002 | ★★ 写出官方后继与「跨族」 | `test_doc_carries_the_official_successor` | ❌ **FAILED** | ✅ pass |
| FR-003 | ★★★ 两处一致 | `test_the_two_places_agree_on_the_verdict` | ❌ **FAILED** | ✅ pass |
| FR-004 | ★ 指回一级真源 | `test_doc_points_back_to_the_primary_source` | ✅ pass | ✅ pass |
| FR-005 | ★★ 全篇无「没有后继」主张 | `test_no_stale_no_successor_claim_anywhere_in_the_doc` | ✅ pass | ✅ pass |
| — | **合计** | — | **3 failed, 2 passed** | **5 passed** |

## 二、★★★★ 两处的口径（★ 订正后）

| ★ 处 | ★ 位置 | ★ 逐字 |
|---|---|---|
| ★ 一级真源 | `scripts/sw_part.py:1457-1466` | ★ 「**后继不是 `FeatureLinearPattern6`，★ 是 `CreateFeature` + `I*FeatureData`**」+「∴ `5` 是**本族最高代**、★ 而**不是"没有后继"**」 |
| ★ 二级文档 | `docs/phase2-obsolete-status.md:36` | ★ 「**⚠ 订正（★ spec 293 · 2026-10-10）**：★ 此处**原写**「`5` **就是现行那代**」⇒ ★★ **那句话会被读成「没有后继」**，★ **而官方给了后继**」+ 官方逐字 + 「**跨族**」+「**本族最高代**」 |

★★★ **两处都含**：★ 官方后继句 `See \`IFeatureManager::CreateFeature\`` · ★ 「跨族」· ★ 「本族最高代」 ✓

## 三、★★★ 判据形态（★ 撤回式引述**不算主张**）

★★ 订正**必须引旧话**（★ 否则读者不知道改了什么）⇒ ★ 判据不能简单 grep「这句话不许出现」。
★★★ **口径逐字沿用本仓既有做法**（`scripts/check_official_md_claims.py::_is_retracted`）：
> 「★ 该行是不是「**已被我撤回的引述**」」

★ 本规格的 `_is_retracted()` 用同款词表（`更正`/`此前`/`原写`/`原先`/`曾经`/`是错的`/`错了`/`撤销`）
⇒ ★★ **同行带撤回标记 ⇒ 不算主张**；★ **不带 ⇒ 报红** ✓

## 四、★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `docs/phase2-obsolete-status.md` | ★ **改 1 行**（★ 第 36 行那条表行：补官方后继 + 跨族口径 + 指回一级真源） |
| 2 | `tests/test_phase2_doc_alignment_298.py` | ★ **新建判据**（5 例） |
| 3 | `specs/298-phase2-doc-alignment/*` | ★ 本规格四件套 |

★ **未改**：`scripts/sw_part.py`（★ 边界冻结 —— 它 **293 已订正**，本轮只对齐读者侧）。

## 五、★★★ 红基线（★ 改前实测 · ★ 用 `git show HEAD:` 取改前原文）

```
$ git show HEAD:docs/phase2-obsolete-status.md > docs/phase2-obsolete-status.md   # 还原改前
$ python -m pytest tests/test_phase2_doc_alignment_298.py -q
FAILED tests/test_phase2_doc_alignment_298.py::test_doc_no_longer_says_five_is_the_current_generation
FAILED tests/test_phase2_doc_alignment_298.py::test_doc_carries_the_official_successor
FAILED tests/test_phase2_doc_alignment_298.py::test_the_two_places_agree_on_the_verdict
3 failed, 2 passed
```

★★ **红基线用的是 `git show HEAD:<path>` 的原文** —— ★ 与事实 62 的可复用手法一致
（「用修复前的原文当负例输入 —— 比手写一个『像 bug 的样本』硬得多」）。

## 六、★ 生成器链

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate298.log` |

## 八、未过门（如实登记）

★ **无**。★ 本规格只对齐**文档**，★ 不动任何代码与能力状态。
