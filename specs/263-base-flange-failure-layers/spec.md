# Spec — **逐层定位** `create_base_flange` 的失败点 + **一条被实验证伪的假设**

**Feature**: `specs/263-base-flange-failure-layers/`
**日期**: 2026-10-10
**上游**: `specs/262-base-flange-creation-regression/`（★ 实测它**回归**）
**本轮只做一件事**：★ **逐层**探它断在哪一步。

---

## 一、★★★ 逐层真机读数（`output/_probe263_layers.py` · SW rev **34.4.1**）

| 层 | 结果 |
|---|---|
| ③ 选前 `_ensure_sketch_selected` | ✅ `'草图1'` |
| ③ `SelectionManager.GetSelectedObjectCount2(-1)` | ✅ **1**（确实选中了） |
| ④ `CreateDefinition(34)` | ✅ **非 None** |
| ⑤ `CreateCustomBendAllowance()` | ✅ **非 None** |
| ⑤ `Initialize(...)` | ✅ **无异常** |
| ⑥ 设属性 ×5（`Thickness` / `BendRadius` / `D1…` / `Override…`） | ✅ **无异常** |
| ⑦ ★★ **`CreateFeature(data)`** | ★★ **回 `None`** |

★★★ **诊断含义**：★ 前面各层**全过** ⇒ ★ **数据对象是好的**，
★ **是 SolidWorks 拒了这个特征**（★ 不是我们没把数据填对）。

★ 另外：★ `data.AccessSelections(model, None)` **抛 `类型不匹配`**（★ 参数不对，★ 且它是**改**已有特征用的）。

---

## 二、★★★ 一条**被实验证伪**的假设（★ 留档，★ 免得重试）

### 假设
★ 官方示例 `Create_Base_Flange_Feature_Example_VBNET.md` 的顺序是
**「先设 `D1`/`D2`/`Thickness` → **最后**才 `Initialize`」**，
★ 而真树的顺序是 **「先 `Initialize` → 再设属性」** —— ★ 而 `Initialize` 的 Remarks 逐字说
「**After you call this method … you cannot change any of the properties associated with this method's parameters.**」
⇒ ★ 看起来**根因就是顺序反了**。

### 实验
★ `output/_probe263_order.py`：★ **只改顺序**（★ 其余照抄真树，★ 并改用官方那种
`data.GetCustomBendAllowance()` 取 bend allowance）⇒ ★★ **`CreateFeature` 仍回 `None`**。

### 结论
★★★ **假设证伪**（`falsified`）—— ★ **顺序不是根因**。
★★ **留档理由**：★ 不记下来 ⇒ ★ 下一个人会**再花一轮**试同一个假设。

---

## 三、★★ 已**确认正确**的两件事（★ 排除）

| 项 | 读数 |
|---|---|
| `SW_FM_BASE_FLANGE` | **34** —— ★ 与官方 `swFeatureNameID_e.swFmBaseFlange = 34` **一致** ✓ |
| 选前 | ★ `GetSelectedObjectCount2` = **1** ⇒ ★ **确实选中了** ✓ |

---

## 四、★★★ 一条诊断性发现：**失败是静默的**

★ `IFeatureManager::CreateFeature` 的官方页说：★ 用 **`IFeature::GetErrorCode2`** 取创建期的错误。
★★ **但它回的是 `None` ⇒ 没有 `IFeature` 对象 ⇒ 读不到错误码** ⇒ ★ **无从得知 SolidWorks 为什么拒**。
⇒ ★★ **下一步必须先找到能报错的入口**（★ 否则只能靠穷举）。

---

## 五、需求

### FR-001 ★★★ 失败点**恰好**是 `CreateFeature`
- **规则**：★ 前面各层（选前 / `CreateDefinition` / `GetCustomBendAllowance` / `Initialize` / 设属性）**全过**；
  ★★ **只有** `CreateFeature` 回 `None`。
- **验收场景**：`test_failure_point_is_exactly_create_feature` 通过；
  ★★ **能红的判据**：★ 任一前层失败 ⇒ 红；★ `CreateFeature` 竟然成功 ⇒ **也红**（★ 结论要改）。

### FR-002 ★★★ 被证伪的假设必须留档
- **规则**：假设 / 依据 / 实验 / 结论**四件齐**，★ `verdict = falsified`，★ 实验里要写「仍回 None」。
- **验收场景**：`test_falsified_hypothesis_is_recorded` 通过。

### FR-003 ★★ 常量与官方一致（★ 排除）
- **验收场景**：`test_constant_is_confirmed_against_the_official_enum` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 六、非目标

- **不**改 `scripts/`（★ 根因**未定** ⇒ ★ **不许瞎改**）⇒ ★ **不跑生成器链**。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 前层失败 ⇒ 红；`CreateFeature` 成功 ⇒ 红；假设记录不全 ⇒ 红 |
| SC-2 | 判据**是绿的** | `tests/test_base_flange_failure_layers.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机 | 护栏预检「读到文档 0 个」· ★ 临时零件**已关闭** |

## 八、未过门（本轮不做，如实登记）

- ★★ **根因未定** —— ★ 顺序已排除、常量已排除、选前已排除。
  ★ **下一步线索**：① 找**能报错的入口**（★ `CreateFeature` 回 None 时静默）；
  ② 换官方示例用的 **`Top` 平面**试；③ 试**老入口** `IModelDoc2::InsertSheetMetalBaseFlange2`。
- `_read_k_factor` 仍未被真机走到（★ 阻塞 = 造不出件）。
- 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · `create_hem` · 223 的 8 条既有红 · 未提交未部署。
