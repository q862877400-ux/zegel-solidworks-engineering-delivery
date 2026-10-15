# Acceptance — 给「`CreateFeature` 回 `None`」找到能报错的入口

**Feature**: `specs/276-createfeature-error-entry/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★ **真因读出来了**（★ 四轮里第一次）—— ★ **「选择失败。」+「所选的草图对此操作无效」**
⇒ ★★ 根因在**草图选择 / 草图状态**，★ **不是环境、不是许可、不是加载项**（★ **推翻 265 的猜测**）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 报错入口找到了 | `test_error_entry_is_found_and_readable` | ✅ 读到 **3** 条 |
| FR-002 | ★★★ 真因是「草图选择/状态」 | `test_the_recorded_cause_is_about_the_sketch` | ✅ `所选的草图对此操作无效` |
| FR-003 | ★★ 另两个入口被排除 | `test_two_entries_are_ruled_out` | ✅ 排除理由**逐字引官方** |
| FR-004 | ★★★ 与官方示例的差异已登记 | `test_official_sequence_diff_is_registered` | ✅ 两条 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★ 入口怎么选出来的（★ 先读官方页，别猜）

| 候选 | ★ 官方页逐字 | ★ 有用？ |
|---|---|---|
| `IFeatureManager::GetCreateFeatureErrors(Object&, String&)` | ★ **「valid **only** after attempting to create **Mate Controller** features」** | ✗ **不适用** |
| `IModelDocExtension::GetWhatsWrong(Object&, Object&, Object&)` | 「Gets the What's Wrong dialog information for this model document」 | ✗ 文档级 ⇒ ★ 无特征则空（★ 实测 `Features=None`） |
| ★★★ `ISldWorks::GetErrorMessages(Object&, Object&, Object&)` | ★ **「Gets the last 20 messages issued in the current SOLIDWORKS Design session」** + ★ **「The stack is cleared after calling this method」** | ✅★ **就是它** |

## 三、★★★ 真机读数（SolidWorks **34.4.1** · ★ 走 `sw_guard` · ★ 临时零件用完关闭不保存）

★ 复刻 `tests/solidworks_sheet_metal_regression.py` 的 setup（★ 新零件 + Front Plane + 3 条线开放折线 + `create_base_flange`）：

```
① 先清栈   ⇒ n=20（★ 历史消息，含前几轮同一错）
② setup    ⇒ 拿到文档 · 草图 3 条线
③ 调用     ⇒ **失败**（`RuntimeError: CreateFeature(IBaseFlangeFeatureData) 创建失败`）
④ ★★★ 立刻读 ⇒ n=3
     Msgs   = ('选择失败。', '零件11 - 重建模型错误', '基体-法兰1: 所选的草图对此操作无效。')
     MsgIDs = (909, 1124, 1124)
```

★ 读数原文 `output/_probe276_error_entry.txt` · ★ 探针 `output/_probe276_error_entry.py`。

### ★★ 加载项读数（★ 佐证「不是环境」）

| ProgID | 读数 |
|---|---|
| `SldWorks.SheetMetal` / `SldWorks.SMWeldment` / `SldWorks.Weldment` / `SldWorks.FeatureWorks` | **全 `None`** |

★ **但官方示例不依赖任何加载项** ⇒ ★★ **加载项不是本族根因**（★ 不然 10-01 那次也不会成功）。

## 四、★★★ 与官方示例**逐字对比**（★ `Create_Base_Flange_Feature_Example_VBNET.md`）

**官方序列**：`SelectByID2("Top","PLANE")` → `InsertSketch(True)` → `ClearSelection2(True)` → `CreateLine ×3`
→ `ClearSelection2(True)` → ★ **`InsertSketch(True)`（关草图）** → ★★ **`SelectionManager.GetSelectedObject6(1,-1)`（取草图特征）**
→ `CreateDefinition(swFmBaseFlange)` → 设属性 → `Initialize(…)` → `CreateFeature(…)`。

| # | ★ 差异 | ★ 含义 |
|---|---|---|
| ① | ★ **官方**不调** `AccessSelections`** | ★ **排除「我们漏调」这条猜想** |
| ② | ★★ 官方靠 `InsertSketch(True)` 关草图后**草图特征自带选中**；★ 本仓走 `_ensure_sketch_selected` **重选** | ★★ **「重选」可能丢了选择状态/标记**（★ 与事实 384 同族） |
| ③ | ★ 官方在 **`Top`** 平面建草图 | ★ 而 265 实测 **`Top` 选不上** |

## 五、★★ 红基线（★ 五组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 真因文本不符 | 报错 | ✅ `["真因子串 '所选的草图对此操作无效' **不在**读数里 ⇒ 入口没读对", 'n=3 与 ids/msgs 长度不符']` |
| 入口表空 | 报错 | ✅ `['可用的入口应**恰有 1 个**，实测 0 个：[]', '入口表为空 ⇒ 检查量为 0']` |
| 两个可用 | 报错 | ✅ `["可用的入口应**恰有 1 个**，实测 2 个：['ISldWorks::GetErrorMessages', 'IModelDocExtension::GetWhatsWrong']"]` |
| 差异表空 | 报错 | ✅ `['差异表为空 ⇒ 检查量为 0']` |

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates` / `gates_passed` | **47** / **44** |
| 日志 | `output/_gate276.log` |

★ **只改了 `tests/`** ⇒ ★ **不跑生成器链**。

## 七、未过门（如实登记）

1. ★★★ **`create_base_flange` 未修** —— ★ **下一 WIP 已定**：★ **按官方序列逐字对齐**
   （★ `ClearSelection2` + `InsertSketch(True)` 关草图后**直接**用 `GetSelectedObject6(1,-1)` 的草图特征，
   ★ **不再**经 `_ensure_sketch_selected` 重选）⇒ ★ 真机验。
2. ★★ **同族另 4 个**（`create_one_bend` / `create_draft` / `create_edge_flange` / `create_gusset`）
   **未用本入口复核** ⇒ ★ 下一轮**逐个读消息栈**。
3. 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
