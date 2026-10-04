# 自查：产出物之间的**共享数字**一致性（★ SC-5 的落点）

> 生成物 —— 由 `tools/s206_number_selfcheck.py` 产出，不要手改。

## 一 · 单一真值源（★ 每个数字的依据）

| 键 | 真值 | 依据 |
|---|---:|---|
| `conflict_ok` | **544** | c4-merged 的 quote_ok |
| `conflict_total` | **598** | c4-merged 的 conflicts tally |
| `dead_link_candidate` | **212** | b2-defects.json 的 type 计数 |
| `lookup_entries` | **424** | 本线的必查表 |
| `lookup_members` | **368** | 本线的必查表 |
| `mark_diff` | **10** | c4-merged 的 kinds |
| `more_specific` | **3806** | c4-merged.json 的 tally `more_specific` |
| `more_specific_members` | **2242** | c4-merged 里 example_more_specific 的 distinct 成员 |
| `precondition_checkable` | **102** | 本线的机械分类结果 |
| `precondition_not_covered` | **322** | c3-merged 的 state=not_covered |
| `preconditions_total` | **534** | c3-merged.json 的 preconditions 总数 |
| `recon_json_total` | **40** | specs/203-*/recon (10) + specs/204-*/recon (30) |
| `unit_diff` | **15** | c4-merged 的 kinds |
| `verified_defects` | **964** | b2-defects.json 的 verified=True 计数 |

## 二 · 各文件里的出现情况

| 文件 | 命中的真值键 |
|---|---|
| `competitor-crosscheck-archival.md` | mark_diff=10 · unit_diff=15 · verified_defects=964 · precondition_checkable=102 · lookup_members=368 · lookup_entries=424 |
| `conflicts-25-crosscheck.md` | recon_json_total=40 · mark_diff=10 · unit_diff=15 · precondition_checkable=102 |
| `conflicts-25.md` | recon_json_total=40 · mark_diff=10 · unit_diff=15 · conflict_ok=544 · conflict_total=598 |
| `conflicts-8-judge-materials.md` | recon_json_total=40 · mark_diff=10 · unit_diff=15 |
| `mark-audit.md` | recon_json_total=40 · mark_diff=10 · unit_diff=15 |
| `more-specific-audit.md` | recon_json_total=40 · more_specific=3806 · more_specific_members=2242 · mark_diff=10 · unit_diff=15 · dead_link_candidate=212 |
| `more-specific-sample20.md` | recon_json_total=40 · more_specific=3806 · more_specific_members=2242 · mark_diff=10 · unit_diff=15 |
| `pre-code-conflict-lookup.md` | recon_json_total=40 · mark_diff=10 · unit_diff=15 · preconditions_total=534 · lookup_members=368 · lookup_entries=424 |
| `README.md` | recon_json_total=40 · mark_diff=10 · dead_link_candidate=212 · verified_defects=964 · preconditions_total=534 · precondition_checkable=102 |
| `spelling-pairs.md` | mark_diff=10 · unit_diff=15 · verified_defects=964 · precondition_checkable=102 |
| `unit-audit.md` | recon_json_total=40 · mark_diff=10 · unit_diff=15 |
| `tool-aliases.md` | mark_diff=10 · unit_diff=15 |
| `precondition-coverage-gaps.md` | recon_json_total=40 · mark_diff=10 · preconditions_total=534 · precondition_not_covered=322 · precondition_checkable=102 |

## 三 · ★ 矛盾检测结果

- ★ `more-specific-sample20.md`：出现 `3709`，而真值是 **3806**
- ★ `README.md`：出现 `3709`，而真值是 **3806**

## 四 · 本表的「不算什么」

- ★ 它只查**已登记的真值键**（14 个）⇒ ★ 未登记的数字它**看不见** ✓
- ★★ 判据是**子串匹配** ⇒ ★ 数字出现在**举例/引用**语境时会**误报** ✓
- ★ 它**不判**数字对不对 —— 只判「产出物之间一不一致」；★ 真值本身由各自的依据负责 ✓
- ★ 真值源是**原始 JSON** 与**本线实测** ⇒ ★ 若原始 JSON 更新，本表要跟着更新 ✓

