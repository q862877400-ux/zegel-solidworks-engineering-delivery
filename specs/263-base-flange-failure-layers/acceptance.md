# Acceptance — 逐层定位 `create_base_flange` 的失败点

**Feature**: `specs/263-base-flange-failure-layers/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **失败点恰好是 `CreateFeature`**（★ 前层全过）· ★★ **「顺序反了」假设被实验证伪**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 失败点恰好是 `CreateFeature` | `test_failure_point_is_exactly_create_feature` | ✅ 前层全过 · 只有它回 `None` |
| FR-002 | ★★★ 被证伪的假设留档 | `test_falsified_hypothesis_is_recorded` | ✅ 四件齐 · `falsified` |
| FR-003 | ★★ 常量与官方一致 | `test_constant_is_confirmed_against_the_official_enum` | ✅ **34** = `swFmBaseFlange` |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| 前层失败 | 「失败点上移，结论要改」 | ✅ `["第 'Initialize(...)' 层就失败了（'抛异常'）⇒ ★ 失败点上移，★ 结论要改"]` |
| ★ `CreateFeature` **竟然成功** | 「结论要改」 | ✅ `['`CreateFeature` 竟然成功了 ⇒ ★ **结论要改**（失败点不在这）']` |
| 假设记录不全 | 报错 | ✅ |

## 三、★★★ 逐层读数

| 层 | 结果 |
|---|---|
| 选前 | ✅ `'草图1'` · `GetSelectedObjectCount2` = **1** |
| `CreateDefinition(34)` | ✅ 非 None |
| `CreateCustomBendAllowance()` | ✅ 非 None |
| `Initialize(...)` | ✅ 无异常 |
| 设属性 ×5 | ✅ 无异常 |
| ★★ **`CreateFeature(data)`** | ★★ **回 `None`** |

⇒ ★ **数据对象是好的，是 SolidWorks 拒了这个特征**。

## 四、★★★ 被证伪的假设

★ **假设**：真树「先 `Initialize` → 再设属性」，官方示例「**先设属性 → 最后 `Initialize`**」⇒ 顺序反了是根因。
★ **实验**（`output/_probe263_order.py`）：★ 只改顺序 ⇒ ★★ **`CreateFeature` 仍回 `None`**。
★★★ **结论：假设证伪** —— ★ 顺序**不是**根因。★ **留档免得重试**。

## 五、★★★ 诊断性发现：**失败是静默的**

★ 官方说用 `IFeature::GetErrorCode2` 取错误 ⇒ ★ **但回 `None` ⇒ 没有 `IFeature` ⇒ 读不到**。
⇒ ★ **下一步必须先找到能报错的入口**（★ 否则只能穷举）。

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 七、未过门（如实登记）

1. ★★ **根因未定** —— ★ 顺序已排除 · 常量已排除 · 选前已排除。
   ★ **下一步线索**：① 找**能报错的入口**；② 换官方示例用的 **`Top` 平面**；③ 试**老入口** `InsertSheetMetalBaseFlange2`。
2. `_read_k_factor` 仍未被真机走到（★ 阻塞 = 造不出件）。
3. 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · `create_hem` · 223 的 8 条既有红 · 未提交未部署。
