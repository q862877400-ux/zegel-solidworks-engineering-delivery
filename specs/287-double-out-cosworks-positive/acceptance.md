# Acceptance — cosworks 的 `Double&` 正例找到了

**Feature**: `specs/287-double-out-cosworks-positive/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿（★ 274 的判据同步更新后仍 5/5）· 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **274 缺的那个 cosworks `Double&` 正例**一直在仓里**** ——
★ `sw_simulation.py` 的 `ICWMesh::GetDefaultElementSizeAndTolerance`（★ 官方 `ByRef … As Double`）
用 `VT_BYREF | VT_R8`，★ **2026-10-01 真机实测取回了值** ⇒ ★★ **12 条接线的前置全部解除**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 仓里有 cosworks `Double&` 正例 | `test_the_positive_example_exists_in_the_repo` | ✅ |
| FR-002 | ★★★ `Double&` 按接口族分 | `test_double_out_is_interface_dependent` | ✅ 2 档 |
| FR-003 | ★★★ 12 条前置全部解除 | `test_the_twelve_entries_are_now_unblocked` | ✅ 3 种 |
| FR-004 | ★★★ 回源码核 | `test_source_check_proves_the_positive_example` | ✅ 4 项 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★★ 正例（★ 逐字来自 `sw_simulation.py`）

| 项 | 内容 |
|---|---|
| ★ 成员 | ★ `ICWMesh::GetDefaultElementSizeAndTolerance` |
| ★ 官方签名 | ★ **`ByRef DElementSize As Double`**（★ VB6 CHM 逐字） |
| ★ 形态 | ★ `VARIANT(pythoncom.VT_BYREF \| pythoncom.VT_R8, 0.0)` |
| ★ **真机读数 1** | ★ `NUnits=-1` ⇒ **4.9339 / 0.2467**（★ 毫米级） |
| ★ **真机读数 2** | ★ `NUnits=2` ⇒ **0.0049339 / 0.0002467**（★ 米级） |

⇒ ★★★ **两条**不同**读数** ⇒ ★ 不是只测一次 ⇒ ★★ **正例成立** ✓

## 三、★★★ 精炼后的模型：★ `Double&` **没有唯一形态 —— 按接口族分**

| 接口族 | ★ 形态 | ★ 证据 |
|---|---|---|
| ★ **cosworks**（★ **无**类型信息） | ★ `VT_BYREF \| VT_R8` | ★ **本条**（★ 2026-10-01 真机取回值） |
| ★ **sldworks.tlb**（★ **有**类型信息） | ★ **裸值 / 省略** | ★ 274（★ `IBody2::GetExtremePoint` ⇒ 传 by-ref VARIANT 报 `TypeError`） |

★★★ ⇒ **274 的「两表不同」结论仍然成立**，★ 而**两张表现在都有真机证据** ✓

## 四、★★★ 12 条接线的前置**全部解除**

| 出参 | 个数 | ★ 正例 |
|---|---|---|
| `Int32&` | **9** | ★ `out_i4` ⇒ `VT_BYREF \| VT_I4`（★ 2026-10-01 逐形态实测） |
| ★ **`Double&`** | **6** | ★★ **`VT_BYREF \| VT_R8`**（★ **本条**） |
| `SwDmTableError&` | **1** | ★ 枚举 ⇒ `VT_BYREF \| VT_I4` |

## 五、★★ 同步更新了 274 的判据（★ 它的结论**已被推翻**）

| 项 | ★ 274 原值 | ★ 287 更新后 |
|---|---|---|
| `VERIFIED_ON_MACHINE["out_double"]` | ★ **`False`** | ★★ **`True`** |
| 那个集合 | ★ `CONTRADICTED_BY_274 = {"out_double"}`（★ 语义：**证伪**） | ★★ `INTERFACE_DEPENDENT_BY_287 = {"out_double"}`（★ 语义：**按接口族分**） |
| 断言 | ★「`out_double` 至今**无**真机证据」 | ★★「**287 已在 cosworks 上找到正例**」 |

★ 并给 `specs/274-double-out-param-form/acceptance.md` 补了**订正块** ✓

## 六、★★ 红基线（★ 五组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 正例字段少 | 报错 | ✅ `['★ 正例应 5 个字段，实测 3', '★ 两条读数**不该相同**…']` |
| 两条读数相同 | 报错 | ✅ `['★ 两条读数**不该相同**（★ 相同就说明只测了一次）']` |
| 形态不对 | 报错 | ✅ `['★ 形态应是 `VT_BYREF \| VT_R8`（★ **两半都要**）']` |
| 接口相关表不 2 档 | 报错 | ✅ `['★ 接口相关表应 2 档（★ cosworks / sldworks.tlb）']` |
| 前置不 3 条 | 报错 | ✅ `['★ 三种出参的前置都要记']` |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate287.log` |

★ **未改** `scripts/` ⇒ ★ **不跑生成器链**。

## 八、未过门（如实登记）

1. ★★★ **12 条本体仍未改** —— ★ 但**前置已解除**（★ 三种出参都有真机正例）⇒ ★ **下一轮动手**：
   ★ **先改表** ⇒ ★ 再接 `out_i4` / `VT_BYREF | VT_R8` ⇒ ★ **真机验**。
2. ★★ **`out_bstr` 仍无真机证据**（★ 与本条无关 ⇒ ★ 如实标注）。
3. ★ ② 段第 2 条（250 的 7 处换路由）· `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
