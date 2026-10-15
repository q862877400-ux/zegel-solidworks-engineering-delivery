# Acceptance — 造钣金件失败（`create_base_flange` 本机建不出来）

**Feature**: `specs/262-base-flange-creation-regression/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **`create_base_flange` 本机建不出特征** ⇒ ★ **回归**（★ 事实 34 记 2026-10-01 成功）；
★★ **已静态排除 261**（★ 261 只碰「读」，它走「写」）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 真机失败如实记录（★ 标回归） | `test_machine_failure_is_recorded` | ✅ `failed` · `CreateFeature…` · `regression=True` |
| FR-002 | ★★★ 静态排除 261 | `test_261_did_not_touch_create_base_flange` | ✅ 函数体里**无** `_read_k_factor`；写路径在 |
| FR-003 | ★★ 阻塞链写清 | `test_blocking_chain_is_explicit` | ✅ 真因 = **造不出** |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| 状态改 `ok` | 报错 | ✅ `["真机状态变了（'ok'）⇒ 请复核本文件的结论"]` |
| 失败点改掉 | 报错 | ✅ |
| ★ 函数体里混入 `_read_k_factor` | 报错 | ✅ `['`create_base_flange` 里出现了 `_read_k_factor` ⇒ 261 确实碰了它 ⇒ **结论要改**']` |

## 三、★★★ 真机读数

★ 跑**仓里维护的** `tests/solidworks_sheet_metal_regression.py`（mtime `10-03 07:17`）⇒
`{"status": "failed", "error": "CreateFeature(IBaseFlangeFeatureData) 创建失败"}`。
★ **它也失败** ⇒ ★ **不是探针写错**。

★★ **事实 34（2026-10-01）记它成功**（「特征树出现「钣金6 / 基体-法兰1 / 平展型式6」」）
⇒ ★★ **2026-10-01 成功 · 2026-10-10 失败 = 回归**。

## 四、★★★ 静态排除 261（★ 本轮最重要的自保）

| 261 改了什么 | 在 `create_base_flange` 里吗 |
|---|---|
| 新增 `_read_k_factor`（★ **读**） | ★ **不在** |
| 替换 `get_com_member(definition, "KFactor")`（★ **读**） | ★ **不在** |
| — | ★ 它走 **`bend_allowance.KFactor = float(spec.k_factor)`**（★ **写**） |

⇒ ★ **261 的嫌疑排除**，★ 判据钉住。

## 五、★★ 方法论教训

★ `git diff HEAD -- scripts/sw_sheet_metal.py` 回了 **120 增 / 26 删**，★ 里面**混着大量我没做的改动**
（★ 本仓工作树是**已 staged 的整树基线**）⇒ ★★ **`git diff HEAD` 不能用来核「我这轮改了什么」**。

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 七、未过门（如实登记）

1. **`create_base_flange` 未修** —— ★ 要真机逐层探（★ 属性层 8/8 已过 ⇒ ★ 失败在**预选**或 `CreateFeature` 的**错误码**）。
2. **`_read_k_factor` 仍未被真机走到**（★ 但阻塞原因已查明）。
3. 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · `create_hem` · 223 的 8 条既有红 · 未提交未部署。
