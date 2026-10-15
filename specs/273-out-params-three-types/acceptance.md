# Acceptance — 改表前先量：12 处的 by-ref 出参只有 3 种类型

**Feature**: `specs/273-out-params-three-types/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ 12 处的 by-ref 出参**只有 3 种类型** ⇒ ★★ **改表时要写的 VARIANT 写法只需 3 种**
（★ 不是 12 种，★ 也不是 8 种）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 出参只有 3 种类型 | `test_only_three_out_param_types` | ✅ `{Int32&, Double&, SwDmTableError&}` |
| FR-002 | ★★ 每种都有 VARIANT 写法 | `test_every_type_has_a_variant_form` | ✅ 3 种写法齐 |
| FR-003 | ★★ `GetWhatsWrong` 不在 12 条里 | `test_all_byref_is_not_in_the_twelve` | ✅ 12 条 · 出参总数 **16** |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★★ 先量：出参类型分布（★ 逐字来自 `output/_probe271_retriage.txt`）

| 出参类型 | 个数 | ★ VARIANT 写法 |
|---|---|---|
| `Int32&` | **9** | `VT_BYREF \| VT_I4` |
| `Double&` | **6** | `VT_BYREF \| VT_R8` |
| `SwDmTableError&` | **1** | `VT_BYREF \| VT_I4`（★ 枚举 ⇒ 整数） |
| **合计** | **16** | ★ **只有 3 种** |

★ **逐成员 12 条**：`GetBOMStartNumber`(`SwDmTableError&`) · `CreatePlot`(`Int32&`) ·
`CreateDeformedBody`(`Int32&`) · `GetDisplacementAtPoints`(`Int32&`) · `GetBucklingLoadFactors`(`Int32&`) ·
`GetNodeLocation`(`Double&`×3) · `GetElementLocation`(`Double&`×3) · `CreateNewStudy`(`Int32&`) ·
`CreateNewStudy2`(`Int32&`) · `CreateNewStudy3`(`Int32&`) · `DuplicateStudy`(`Int32&`) · `ConvertStudy`(`Int32&`)。
★ 9 + 6 + 1 = **16** ✓。

## 三、★★★ `GetWhatsWrong` **不在** 12 条里

★ 签名逐字 `IModelDocExtension.GetWhatsWrong(Object&, Object&, Object&)` ⇒ ★ 出参**为空**（★ `com = 3` = 形参 3）
⇒ ★ 它是 **`all-byref` 桶**（★ 253/266 的命名）⇒ ★ **它差 0** ⇒ ★ 与 12 条**不是同一处改法**（★ 266 判「不值」）。

## 四、★★ 红基线（★ 三组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 多一种类型（`String&`） | 报错 | ✅ `["类型集合与 VARIANT 表不符…", '出参类型 4 种 ≠ 3', '逐成员出参总数 16 ≠ 分布之和 17']` |
| 逐成员总数不符（`CreatePlot` 加一个出参） | 报错 | ✅ `['逐成员出参总数 17 ≠ 分布之和 16']` |
| 混进 `GetWhatsWrong` | 报错 | ✅ `['成员数 13 ≠ 12', '`GetWhatsWrong` 不该在 12 条里（★ 它差 0）']` |

## 五、★★★ 为什么这条值钱

★ 改表 + 接出参要写 **`VARIANT`** ⇒ ★ **类型数决定要写几种**。
★★ 量出只有 **3** 种 ⇒ ★★ **VARIANT 写法只需 3 种**（★ 不是 12 种）。
★★★ **不先量就会**：★ 要么**多写**（逐条查官方 12 次）★ 要么**少写**（漏一种 ⇒ 真机 `DISP_E_TYPEMISMATCH`）。

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate273.log` |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 七、未过门（如实登记）

1. ★★★ **12 条本体的改法未做** —— ★ **改法已明确且已量清**：① 改表（12 处）★ ② 接 by-ref 出参
   （★ **只需 3 种 VARIANT 写法**）★ ③ **真机验**。
2. ★ 1 条 `all-byref`（`GetWhatsWrong`）未修（★ 266 判「不值」）。
3. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
