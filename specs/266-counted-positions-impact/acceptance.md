# Acceptance — 先量 `counted_positions` 口径缺陷的影响面

**Feature**: `specs/266-counted-positions-impact/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ 改口径**只移出 1 条** ⇒ ★★ **收益/成本比很差 ⇒ 降级**（★ 253 的「4 条」不是同一病因）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 影响面只 1 条 | `test_impact_is_only_one_entry` | ✅ **16 → 15 · 移出 1** |
| FR-002 | ★★★ 4 条分两类病因 | `test_the_four_false_positives_have_two_causes` | ✅ `all-byref` **1** + `starargs` **3** |
| FR-003 | ★★ `PURE_OUT` 只跳 `Object&` | `test_pure_out_skips_only_object` | ✅ |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| 移出数改成 4 | 报错 | ✅ `['移出数 4 与两个计数之差 1 不符']` |
| 计数改成 12 | 报错 | ✅ `['移出数 1 与两个计数之差 4 不符']` |
| 两类之和 ≠ 4 | 报错 | ✅ |

## 三、★★★ 先量读数

| 口径 | `arity` 桶条数 |
|---|---|
| ★ **现行**（跳 `PURE_OUT`） | **16** |
| ★ **实验**（不跳） | **15** |
| ★★ **移出** | ★★ **1** —— `sw_feature_readback.py:133 GetWhatsWrong` |

★ `PURE_OUT` 实测只跳过 **`Object&`**。

## 四、★★★ 结论：降级

| 病因 | 条数 | 改口径能救吗 |
|---|---|---|
| `all-byref-false-positive` | **1** | ★ 能 |
| `starargs-false-positive` | **3** | ★★ **不能**（★ 另一病因：`*args` 透传） |

⇒ ★★ **改口径只解决 1 条**，★ 而改它要动**门禁本体** ⇒ ★★★ **优先级下调**。

## 五、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 六、未过门（如实登记）

1. ★★ **`counted_positions` 未改**（★ 量完判「不值」）—— ★ **触发条件** = 同病因条目变多。
2. ★ **3 条 `starargs` 假阳性未修** —— ★ **病因不同** ⇒ ★ 另开切片。
3. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
