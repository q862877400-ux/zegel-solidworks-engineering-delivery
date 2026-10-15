# Acceptance — 重量分桶 + 268 的副作用

**Feature**: `specs/269-arity-retriage-new-rule/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ 新口径下 `arity` **11 = 10 `byref-tail` + 1 `all-byref`**；
★★★ **268 的窄规则误移了 2 条 `real-gap`** ⇒ ★ **掩盖了真缺口**（★ 已记录，修法已写明）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 重量分桶 | `test_retriage_under_the_new_rule` | ✅ **11 = 10 + 1** |
| FR-002 | ★★★ 268 误移 2 条 `real-gap` | `test_the_narrow_rule_wrongly_moved_two_real_gaps` | ✅ 5 = 3 + **2** |
| FR-003 | ★★ 正方向写清两半来源 | `test_right_direction_for_the_fix` | ✅ 「267 的位置 + 268 的计数」 |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| 桶之和 ≠ 11 | 报错 | ✅ `['新口径的桶之和 10 ≠ 11']` |
| 误移桶名不对 | 报错 | ✅ |

## 三、★★★ 重量分桶

| 桶 | 条数 | 特征 |
|---|---|---|
| ★ `byref-tail-convention` | **10** | 差 **−1** · 末位 `Int32&` |
| ★ `all-byref-false-positive` | **1** | 差 **0** · 末位 `Object&` |

⇒ ★★ **`starargs` 与 `real-gap` 都消失了** —— ★ 前者预期，★ **后者不是**。

## 四、★★★ 268 的副作用

| 移走的 | 条数 | 对不对 |
|---|---|---|
| `starargs-false-positive` | **3** | ★ 对 |
| ★★ **`real-arity-gap`** | ★★ **2** | ★★★ **错** |

★ `ICWMesh::GetNodeLocation(Int32, Double&, Double&, Double&)` 也是「1 实参 vs 4 形参」
⇒ ★ 满足窄规则 ⇒ ★ 被判成 `starred` —— ★ 而它**不是 `*args`**，★ 是**真缺口**。

★★★ **要紧之处**：★ `starred` **算已核** ⇒ ★ **那 2 条真缺口不再被计数** ⇒ ★ **门禁把它们藏起来了**。

## 五、★★★ 正方向

★ **267 的位置 + 268 的计数**：★ 窄规则移回 `com_args`（★ 那里知道 `*args`）★ 但 `main` 仍算已核。

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 七、未过门（如实登记）

1. ★★★ **268 的窄规则未修** —— ★ **它掩盖了 2 条真缺口** ⇒ ★ **修法已写明**（★ 移回 `com_args` + `main` 算已核）⇒ ★ 另开切片。
2. ★ 10 条 `byref-tail` 仍是约定问题 · ★ 1 条 `all-byref` 未修（★ 266 判「不值」）。
3. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
