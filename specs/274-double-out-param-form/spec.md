# Spec — **`Double&` 出参**不吃** by-ref VARIANT（`out_double` 的类推被真机证伪）

**Feature**: `specs/274-double-out-param-form/`
**日期**: 2026-10-10
**上游**: `specs/273-out-params-three-types/`（★ 量出 12 条里 **6 个 `Double&`** · ★ 说「改表 + 接出参」）
**本轮只做一件事**：★ **真机核**「`Double&` 出参到底怎么传」—— ★ 因为它是**接线的前置**。

---

## 一、★★★ 为什么要先量（★ 273 的教训：动手前先量）

★ 273 量出：★ 12 条要接的出参**只有 3 种**，★ 其中 **`Double&` 占 6 个**。
★★ **接线要选「传法」** —— ★ 而本仓**已有的** 4 个 out 包装器里：

| 包装器 | 形态 | ★ 真机证据 |
|---|---|---|
| `out_i4` | `VT_BYREF \| VT_I4` | ★★ **有**（逐形态实测，五种只有这一种通） |
| `out_dispatch` | `VT_BYREF \| VT_DISPATCH` | ★★ **有**（逐形态实测） |
| `out_double` | `VT_BYREF \| VT_R8` | ⚠★ **无** —— ★ 源码注释自认「**形态照 `out_i4` 的真机结论**」= **类推** |
| `out_bstr` | `VT_BYREF \| VT_BSTR` | ⚠★ **无** —— ★ 同上 |

★★★ **本仓纪律逐字**（`sw_connect.out_dispatch` 的 docstring）：
**「本仓的纪律是**不凭类推**」** ⇒ ★★ **`out_double` 这一步从没做过**。

---

## 二、★★★ 真机读数（SolidWorks **34.4.1** · ★ 只读打开 `output/fixtures/刀柄_Holder.sldprt`）

### 靶子 A：`IBody2.GetExtremePoint(Double, Double, Double, Double&, Double&, Double&)`

★ 3 个入参 + **3 个 `Double&` 出参**（★ 与 `GetNodeLocation` **同形**）。

| 形态 | 结果 | 证据 |
|---|---|---|
| by-ref VARIANT（`VT_BYREF\|VT_R8`） | ✗ | `TypeError: float() argument must be a string or a real number, not 'VARIANT'` |
| `VT_R8`（**不带** BYREF） | ✗ | 同上 |
| `VT_BYREF\|VT_VARIANT` | ✗ | 同上 |
| **裸 `0.0`** | ✅ | `ret=(True, 0.0275, 0.0, 0.0)` ⇒ ★ **出参随返回元组回来** |
| **省略出参** | ✅ | 同上 |

### 靶子 B（判别器）：`IModelDocExtension.GetWhatsWrong(Object&, Object&, Object&)`

| 形态 | 结果 | 证据 |
|---|---|---|
| by-ref VARIANT（`VT_BYREF\|VT_VARIANT`） | ✅ | `ret=True`（★ 与 253 一致） |
| 裸 `None`×3 | ✗ | `-2147352571`（`DISP_E_TYPEMISMATCH`「类型不匹配」） |
| 省略（0 参） | ✗ | `-2147352561`（`DISP_E_PARAMNOTOPTIONAL`「非选择性的参数」） |

---

## 三、★★★ 结论：★ **传法取决于「该形参怎么声明」，不能按「出参」一刀切**

| 方法 | 出参类型 | by-ref VARIANT | 裸值 | 省略 |
|---|---|---|---|---|
| `IBody2::GetExtremePoint` | `Double&`×3 | ✗ | **✓** | **✓** |
| `IModelDocExtension::GetWhatsWrong` | `Object&`×3 | **✓** | ✗ | ✗ |

⇒ ★★★ **两张表正好相反** ⇒ ★★ **「出参一律 by-ref VARIANT」是错的**（★ 那是从 `out_i4` **类推**出来的）。
⇒ ★★ **`out_i4` 的「唯一可用形态」只对 `Int32&` / `Object&` 那类成立**；★ **`Double&` 是另一回事**。

---

## 四、★★★ 对既有代码的影响（★ 只登记，**不改行为**）

★ `sw_sensor.out_double` 用在 **`ISensor.GetSensorValue(out double Value, out string Units)`** 上
（★ `sw_sensor.py:35-48`）⇒ ★★ **它只有类推、没有 `Double&` 的真机正例**，★ 而本轮已有一个 **`Double&` 反例**。
★★ **本仓纪律「不凭类推」⇒ 不改它的行为**（★ 没直接验 `GetSensorValue`）⇒ ★ **只在原地写清「用前先真机核」**。

---

## 五、需求

### FR-001 ★★★ `Double&` **不吃** by-ref VARIANT
- **验收场景**：`test_double_out_does_not_take_a_byref_variant` 通过。

### FR-002 ★★ `Object&` **必须** by-ref VARIANT（对照 253）
- **验收场景**：`test_object_out_takes_a_byref_variant` 通过。

### FR-003 ★★★ 两张表**必须不同**（★ 不能一刀切）
- **验收场景**：`test_two_tables_must_differ` 通过。

### FR-004 ★★★ 4 个包装器的形态**回源码核** + 疑点**必须登记**
- **规则**：★ 形态**不靠手抄** —— ★ 判据**读源码**核；★ `out_double` 的疑点**登记且不得谎报为已验**。
- **验收场景**：`test_helper_forms_and_registered_risk` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 四组负例）。

---

## 六、非目标

- ★★ **不改 `out_double` 的形态**（★ 那是「凭类推」—— ★ 没直接真机验 `GetSensorValue`）。
- ★★ **不改 12 条的表**（★ 本轮只解决「`Double&` 怎么传」这个**前置**）。
- ★ **不改** `sw_connect.out_i4` / `out_dispatch`（★ 它们**有**真机证据）。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 两表合并 / 某表全 False / 疑点清空 / 谎报为已验 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_double_out_param_form.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |

## 八、未过门（本轮不做，如实登记）

- ★★★ **12 条本体未改** —— ★ 且本轮**提高了它的前置要求**：★ **6 个 `Double&` 不能用 `out_double` 的形态**
  ⇒ ★ **接线前必须逐个真机核**（★ 或找到 cosworks 上 `Double&` 的正例）。
- ★★ **`sw_sensor` 的非空路径仍未真机验**（★ 要一个真传感器，★ 而**建它只能走 UI**）⇒ ★ 本轮只登记疑点。
- `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
