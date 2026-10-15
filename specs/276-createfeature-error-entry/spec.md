# Spec — **给「`CreateFeature` 回 `None`」找到**能报错的入口**，并读出真因**

**Feature**: `specs/276-createfeature-error-entry/`
**日期**: 2026-10-10
**上游**: `specs/263-base-flange-failure-layers/`（★ 它逐层定位后**自己留的下一步**：★ 「`CreateFeature` 回 `None` 时**没有 `IFeature` 对象** ⇒ **读不到错误码 ⇒ 失败是静默的** ⇒ ★ **下一步先找能报错的入口**」）
**本轮只做一件事**：★ **把那个入口找到**，★ **把真因读出来**。

---

## 一、★★★ 为什么这一步值钱

★ 263 / 264 / 265 三轮都在**猜**失败原因（顺序 / 常量 / 预选 / 平面 / 模板 / 两条路），
★★ **因为 `CreateFeature` 回 `None` 时拿不到任何错误信息** ⇒ ★ 只能**穷举排除**。
★★★ **265 的最后猜测是「更像环境/许可/选项」** —— ★★ **本轮实测：不是**（★ 见 §三）。

---

## 二、★★★ 入口是**先读官方页**选出来的（★ 铁律：先读官方页，别猜）

| 候选入口 | ★ 官方页逐字 | ★ 对本族有用？ |
|---|---|---|
| `IFeatureManager::GetCreateFeatureErrors(Object&, String&)` | ★ **「valid **only** after attempting to create **Mate Controller** features」** | ✗ **不适用**（★ 官方明说只对 Mate Controller） |
| `IModelDocExtension::GetWhatsWrong(Object&, Object&, Object&)` | 「Gets the What's Wrong dialog information for this model document」 | ✗ 文档级「What's Wrong」⇒ ★ **无特征则空**（★ 实测 `Features=None`） |
| ★★★ `ISldWorks::GetErrorMessages(Object&, Object&, Object&)` | ★ **「Gets the last 20 messages issued in the current SOLIDWORKS Design session」** + ★ **「The stack is cleared after calling this method」** | ✅★ **就是它** |

⇒ ★★★ **只有 `GetErrorMessages` 是会话级、通用的** ⇒ ★ 用它。

---

## 三、★★★ 真机读数（SW **34.4.1** · ★ 只读探针 + 一个临时零件 · ★ 用完关闭不保存）

★ 复刻 `tests/solidworks_sheet_metal_regression.py` 的 setup（★ 新零件 + Front Plane + 3 条线开放折线 + `create_base_flange`）。

```
① 先清栈   ⇒ n=20（★ 历史消息，含前几轮的同一错）
② setup    ⇒ 拿到文档 · 草图 3 条线
③ 调用     ⇒ **失败**（`RuntimeError: CreateFeature(IBaseFlangeFeatureData) 创建失败`）
④ ★★★ 立刻读消息栈 ⇒ n=3
     Msgs   = ('选择失败。', '零件11 - 重建模型错误', '基体-法兰1: 所选的草图对此操作无效。')
     MsgIDs = (909, 1124, 1124)
```

### ★★★ 真因（★ 这是四轮里第一次读到）

> **「选择失败。」+「基体-法兰1: **所选的草图对此操作无效**。」**

⇒ ★★★ **根因在「草图选择 / 草图状态」，★ 不是环境、不是许可、不是加载项**。
★★ **推翻 265 的猜测**（★ 它说「更像**环境/许可/选项**」）—— ★ 实测**不是**。

### ★★ 加载项读数（★ 佐证「不是环境」）

| ProgID | 读数 |
|---|---|
| `SldWorks.SheetMetal` | **`None`**（★ 与 265 一致） |
| `SldWorks.SMWeldment` | **`None`** |
| `SldWorks.Weldment` | **`None`** |
| `SldWorks.FeatureWorks` | **`None`** |

★ **但官方示例（§四）不依赖任何加载项** ⇒ ★★ **加载项不是本族根因**（★ 不然 10-01 那次也不会成功）。

---

## 四、★★★ 与官方示例**逐字对比**（★ `Create_Base_Flange_Feature_Example_VBNET.md`）

★ 官方序列逐字：
```
SelectByID2("Top", "PLANE", …)        ← ★ 在 **Top** 平面
SketchManager.InsertSketch(True)      ← ★ 开草图
ClearSelection2(True)
CreateLine ×3                          ← ★ 3 段开放折线
ClearSelection2(True)
SketchManager.InsertSketch(True)      ← ★★ **关草图**
swSKFeat = SelectionManager.GetSelectedObject6(1, -1)   ← ★★ **直接取「草图特征」**
CreateDefinition(swFmBaseFlange) → 设属性 → Initialize(…) → CreateFeature(…)
```

★★★ **三条关键差异**：

1. ★★★ **官方**不调** `AccessSelections`** ⇒ ★ **排除「我们漏调 `AccessSelections`」这条猜想**（★ 本仓的 `create_base_flange` 也没调）。
2. ★★★ **官方靠 `InsertSketch(True)` 关草图后「草图特征**自己**就是选中的」**，★ **直接** `GetSelectedObject6(1, -1)` 取它；
   ★ 而本仓走 `_ensure_sketch_selected` **重新选一遍**（★ 4 条策略：活动引用 / 缓存引用 / `FeatureByName` / `SelectByID2('SKETCH')`）
   ⇒ ★★ **「重新选」可能丢了官方那条路带上的选择状态/标记**（★ 与事实 384 的「选择标记」同族）。
3. ★ 官方在 **`Top`** 平面建草图；★ 而 265 实测 **`Top` 选不上**。

---

## 五、需求

### FR-001 ★★★ 报错入口**找到了**（★ 会话级）
- **规则**：★ `ISldWorks::GetErrorMessages` 能读出「上次 `CreateFeature` 失败」的消息。
- **验收场景**：`test_error_entry_is_found_and_readable` 通过。

### FR-002 ★★★ **真因**是「草图选择/状态」
- **规则**：★ 真机读数里必须有 **`所选的草图对此操作无效`**，★ 且有 **`选择失败。`**（MsgID **909**）与 **`重建模型错误`**（**1124**）。
- **验收场景**：`test_the_recorded_cause_is_about_the_sketch` 通过。

### FR-003 ★★ 另两个入口**被排除**（★ 带官方依据）
- **规则**：★ `GetCreateFeatureErrors` 的官方 Remarks 里**逐字**有 `Mate Controller` ⇒ ★ **不适用**。
- **验收场景**：`test_two_entries_are_ruled_out` 通过。

### FR-004 ★★★ 与官方示例的差异**已登记**
- **规则**：★ 「官方不调 `AccessSelections`」+「官方靠关草图后的**自带选择**」两条**都要在表里**。
- **验收场景**：`test_official_sequence_diff_is_registered` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 六、非目标

- ★★ **不修 `create_base_flange`**（★ 修法要**按官方序列对齐**并**真机验** ⇒ ★ **另开切片**；★ 且 `sw_part.py` 是**多调用点**文件，★ 动它要**跑生成器链 + 同步下界**）。
- ★ **不改** `sw_part._ensure_sketch_selected`（★ 同上）。
- ★ **不改** `scripts/` ⇒ ★ **不跑生成器链**。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 真因文本不符 / 缺 MsgID / 排除表空 / 差异表空 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_createfeature_error_entry.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 八、未过门（本轮不做，如实登记）

- ★★★ **`create_base_flange` 未修** —— ★ **下一 WIP 已定**：★ **按官方序列逐字对齐**
  （★ `ClearSelection2` + `InsertSketch(True)` 关草图后**直接**用 `GetSelectedObject6(1,-1)` 的草图特征，
  ★ **不再**经 `_ensure_sketch_selected` 重选）⇒ ★ 真机验。
- ★★ **同族的另 4 个**（`create_one_bend` / `create_draft` / `create_edge_flange` / `create_gusset`）**未用本入口复核** ⇒ ★ 下一轮逐个读消息栈。
- ★ 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
