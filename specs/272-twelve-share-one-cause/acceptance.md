# Acceptance — 12 条 `arity` 是同一病因

**Feature**: `specs/272-twelve-share-one-cause/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ 271 判的 2 条 `real-gap` **其实是**同一条约定****（★ 与 10 条 `byref-tail` 同病因）
⇒ ★★ **12 条同一处改法**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 表侧一律「不含 by-ref 出参」 | `test_table_side_excludes_byref_out` | ✅ 4 条**全自洽** |
| FR-002 | ★★★ 12 条同一病因 | `test_twelve_entries_share_one_cause` | ✅ **10 + 2 = 12** |
| FR-003 | ★★ 护栏会拒多传 | `test_checked_guard_rejects_extra_args` | ✅ `expected != len(args)` 在 |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| 表侧不自洽 | 报错 | ✅ `['X 的表侧值不自洽（1 + 1 ≠ 5）']` |
| 同类条数不对 | 报错 | ✅ `['同类条数 10 ≠ 10 + 2']` |

## 三、★★★ 先量

| 成员 | 表侧值 | 官方 | 差 |
|---|---|---|---|
| `GetNodeLocation` | ★ **1** | **4** | **−3** |
| `GetElementLocation` | ★ **1** | **4** | **−3** |

## 四、★★★ 关键：`table + byref_out == official`

| 成员 | 表侧 | 出参数 | 官方 | 自洽？ |
|---|---|---|---|---|
| `GetNodeLocation` | **1** | **3** | **4** | ✓ |
| `CreatePlot` | **4** | **1** | **5** | ✓ |
| `GetBOMStartNumber` | **0** | **1** | **1** | ✓ |

⇒ ★★★ **表侧一律「不含 by-ref 出参」** ⇒ ★★ **2 条 `real-gap` 与 10 条 `byref-tail` 同一条约定**。

## 五、★★★ 纠正 271 的定性

★ 271 按**差的个数**分桶 ⇒ 判 2 条为 `real-gap`。
★★ 272 按**病因**看 ⇒ ★ **12 条都是**「封装未接 by-ref 出参」★ 差 1 个还是 3 个**只是出参个数**。

## 六、★★ 下一轮动手前必须知道

★ `_checked` 逐字：`expected != len(args)` ⇒ 抛 `ValueError`
⇒ ★★ **想补出参就得**先改表****（★ 否则护栏先拦）。
★ 而那句提示**自己**就写着「**不含末尾 by-ref 出参**」⇒ ★ **约定写在代码里**。

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 八、未过门（如实登记）

1. ★★★ **12 条本体的改法未做** —— ★ **改法已明确**：① 改表（12 处）★ ② 接 by-ref 出参（`VT_BYREF | VT_R8`）★ ③ **真机验**。
2. ★ 1 条 `all-byref` 未修（★ 266 判「不值」）。
3. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
