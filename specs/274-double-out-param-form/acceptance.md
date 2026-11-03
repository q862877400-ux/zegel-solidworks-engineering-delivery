# Acceptance — `Double&` 出参不吃 by-ref VARIANT

**Feature**: `specs/274-double-out-param-form/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★ **「出参一律 by-ref VARIANT」是错的** —— ★ 真机实测**两张表正好相反**：
★ `Double&` **不吃** by-ref VARIANT（★ 裸值 / 省略通）· ★ `Object&` **必须** by-ref VARIANT。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ `Double&` 不吃 by-ref VARIANT | `test_double_out_does_not_take_a_byref_variant` | ✅ `TypeError` |
| FR-002 | ★★ `Object&` 必须 by-ref VARIANT | `test_object_out_takes_a_byref_variant` | ✅ 裸值/省略均 ✗ |
| FR-003 | ★★★ 两张表必须**不同** | `test_two_tables_must_differ` | ✅ 正好相反 |
| FR-004 | ★★★ 形态**回源码核** + 疑点**登记** | `test_helper_forms_and_registered_risk` | ✅ 4/4 核过 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 四组负例全红 |

## 二、★★★ 真机读数（SolidWorks **34.4.1** · ★ 只读打开 `output/fixtures/刀柄_Holder.sldprt`）

### 靶子 A：`IBody2.GetExtremePoint(Double, Double, Double, Double&, Double&, Double&)`

| 形态 | 结果 | 证据 |
|---|---|---|
| by-ref VARIANT（`VT_BYREF\|VT_R8`） | ✗ | `TypeError: float() argument must be a string or a real number, not 'VARIANT'` |
| `VT_R8`（**不带** BYREF） | ✗ | 同上 |
| `VT_BYREF\|VT_VARIANT` | ✗ | 同上 |
| **裸 `0.0`** | ✅ | `ret=(True, 0.0275, 0.0, 0.0)` ⇒ ★ 出参**随返回元组回来** |
| **省略出参** | ✅ | 同上 |

### 靶子 B（★ 判别器）：`IModelDocExtension.GetWhatsWrong(Object&, Object&, Object&)`

| 形态 | 结果 | 证据 |
|---|---|---|
| by-ref VARIANT（`VT_BYREF\|VT_VARIANT`） | ✅ | `ret=True`（★ 与 253 一致） |
| 裸 `None`×3 | ✗ | `-2147352571`（`DISP_E_TYPEMISMATCH`「类型不匹配」） |
| 省略（0 参） | ✗ | `-2147352561`（`DISP_E_PARAMNOTOPTIONAL`「非选择性的参数」） |

★ 读数原文：`output/_probe274_double_out.txt` · ★ 探针：`output/_probe274_double_out.py`。

## 三、★★★ 结论

| 方法 | 出参 | by-ref VARIANT | 裸值 | 省略 |
|---|---|---|---|---|
| `IBody2::GetExtremePoint` | `Double&`×3 | ✗ | **✓** | **✓** |
| `IModelDocExtension::GetWhatsWrong` | `Object&`×3 | **✓** | ✗ | ✗ |

⇒ ★★★ **「出参一律 by-ref VARIANT」是错的** —— ★ 传法**取决于该形参怎么声明**。
⇒ ★★ **`out_i4` 的「唯一可用形态」只对 `Int32&`/`Object&` 那类成立**；★ **`Double&` 是另一回事**。
★★ **判别器为什么必要**：★ 只有靶子 A ⇒ ★ 分不清「是 `Double&` 的问题」还是「是 `IBody2` 的问题」；
★ 加了**同机同文档**的 `Object&` ⇒ ★ 变量**收敛到「形参类型」**。

## 四、★★★ 对既有代码的影响（★ 只登记，**不改行为**）

★ `sw_sensor.out_double` 用在 **`ISensor.GetSensorValue(out double Value, out string Units)`** 上
⇒ ★★ **只有类推、没有 `Double&` 真机正例**，★ 而本轮已有**同族反例**。
★★ 本仓纪律「**不凭类推**」⇒ ★ **不改它的行为**（★ 没直接验 `GetSensorValue`）
⇒ ★ 只在原地写清「**用前先真机核**」（★ 已写入 `scripts/sw_sensor.py`）。

## 五、★★ 红基线（★ 四组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 两张表合并 | 报错 | ✅ `['Double& 与 Object& 的形态表**相同** ⇒ 一刀切 ⇒ 与真机读数不符']` |
| 某表全 False | 报错 | ✅ `['Double& 表里**没有**任何通过的形态 ⇒ 读数不可信']` |
| 疑点清空 | 报错 | ✅ `['CONTRADICTED_BY_274 为空 ⇒ 检查量为 0 ⇒ 不许通过']` |
| 把疑点谎报为已验 | 报错 | ✅ `["'out_double' 被登记为「已真机验」却同时在疑点表里 ⇒ 自相矛盾"]` |

## 六、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate274.log` |

## 八、未过门（如实登记）

1. ★★★ **12 条本体未改** —— ★ 且**前置要求提高**：★ **6 个 `Double&` 不能用 `out_double` 的形态**
   ⇒ ★ 接线前**逐个真机核**（★ 或找到 cosworks 上 `Double&` 的正例）。
   ★★★ **订正（2026-10-10 · 规格 287）**：★★ **那个「cosworks 正例」找到了** —— ★ **它一直在仓里**：
   ★ `scripts/sw_simulation.py` 的 `ICWMesh::GetDefaultElementSizeAndTolerance`
   （★ 官方 `ByRef DElementSize As Double`）用 `VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)`，
   ★ **2026-10-01 真机实测取回了值**（★ `NUnits=-1` ⇒ 4.9339 / 0.2467 · ★ `NUnits=2` ⇒ 0.0049339 / 0.0002467）。
   ⇒ ★★ 精炼后的模型：★ **`Double&` 没有唯一形态 —— 它按「接口有没有类型信息」分**
   （★ cosworks ⇒ by-ref VARIANT ✓ · ★ sldworks.tlb ⇒ 裸值 ✓）
   ⇒ ★★★ **274 的「两表不同」结论仍然成立**，★ 且**两张表都有真机证据** ⇒ ★ **12 条接线的前置**全部满足****。
   ★ 判据 `tests/test_double_out_cosworks_positive.py`（★ 新）· ★ `tests/test_double_out_param_form.py` 已同步更新。
2. ★ `sw_sensor` 非空路径仍未真机验（★ 要真传感器 ⇒ **只能走 UI 建**）⇒ ★ 只登记疑点。
3. ★ 1 条 `all-byref`（`GetWhatsWrong`）未修（★ 266 判「不值」）。
4. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
