# patterns-shard-2 —— 分歧根因归类 + 批量可行性（audit-05 / 06 / 07）

**范围**：只抽 `audit-05-drawing-{A,B,C}` · `audit-06-features-{A,B,C}` · `audit-07-sketch-C` 这 **7 份**。
**抽取口径**：逐份逐行读「分歧表」，**一行一条**，不合并、不丢；各份的「没报的 / 查不到 / 核过但一致」不算分歧，未计入。
**★ 本 shard 只覆盖 7 片，不是 Lead 首轮的 17 片**：其中 `audit-07-sketch-A.md` 与 `audit-07-sketch-B.md` 在本仓
`specs/202-user-coverage-gaps/recon/audit-vs-official/` 下**不存在**（只有 `-C`），⇒ 域 07 的 A/B 两面本轮**无输入**，
下面所有 07 的数据都来自 `-C` 一片。

---

## 0. 我用的切法（与 Lead 首轮切法的差异）

Lead 首轮把根因分成：mark 值不对/没给 · 用了废弃成员 · 参数个数不符 · 枚举取值不是合法成员 · 类型不符 · 标量 vs 数组 · 参数顺序不符 · 前置没做 · 返回值/出参形状不符。

我**沿用其中 6 个类名，但改了 3 处的归并口径**（理由都在下面）：

| 我的类 | 与 Lead 的差别 | 为什么这么切 |
|---|---|---|
| **O · 用了废弃成员** | 同名 | 官方 Obsolete 标记是**一个可索引的文本事实**（每个 `types\<接口>\<成员>.md` 顶部一行），值得单列 |
| **P · 前置没做/前置判据过弱** | Lead 分成「mark 值不对/没给」+「前置没做」两档，我**并成一档** | ★ 本 shard 里**没有一条纯粹的「mark 值填错」**——所有涉及 mark 的分歧都是「**这一步整体没做，或只判了计数没判对象类型**」。拆两档会让同一形态（`pre = _selection_count(...)` 判 `>= 1`）散到两个类里，反而丢规律 |
| **E · 取值不在官方合法域** | Lead 的「枚举取值不是合法成员」扩展了一层 | ★ 本 shard 的 3 条里只有 1 条是**枚举成员**（`swRevisionTableSymbolShape_e`），另 2 条分别是**成员页写的有效范围**（`valid range is 1 to 5`）和**两源冲突**（md `-1` vs 反射 `1`）。三者判据形态不同（穷举表 / 区间 / 双源比对），但**修法形态完全一样**（把越界值换成域内保守值）⇒ 按「可批量性」并，而不是按「官方怎么写的」分 |
| **D · 文档性分歧（我们注释声称官方没给/没写，而官方页给了）** | ★ Lead 没有这一类 | 本 shard 有 **3 条**，它们与 COM 调用**无关**，是注释/文档字符串与官方原文对不上。不单列就会被前面几类按关键词误吸（Lead 的脚本里 `enum` / `取值表` 关键词就会命中）|
| **W · 取错了成员（语义错位）** | ★ Lead 没有这一类 | `GetSelectedObjectType3` 被当 mark 用，**名字对、类型对、个数错**——它既不是「废弃」也不是「参数个数」，单列才看得见 |
| **T · 实参类型与形参类型不符** | 同名 | — |

★ **本 shard 里 Lead 的「参数个数不符」「参数顺序不符」「标量 vs 数组」「返回值/出参形状不符」这 4 类合计 0 条**
——唯一那条「个数对不上」的（05-A#1）根因是**取错了成员**，我归到 W。

---

## 1. 全量分歧表（33 条）

置信度一栏沿用各核对表的原始判定；「批量可行性」是我给的估（理由见 §3）。

### 1.1 · `audit-05-drawing-A`（核对 A · 签名一致性）— 1 条

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-01 | A · 签名 | **W 取错了成员** | `scripts/sw_drawing_expose.py` · `mark = C.get_com_member(mgr, "GetSelectedObjectType3", i, -1)` 紧接着 `out[str(mark)] = out.get(str(mark), 0) + 1`；docstring 自述「回读当前选区里**每个 mark** 各有几个对象」 | `ISelectionMgr\GetSelectedObjectType3.md` · **Returns**: `Type of object as defined in [[swSelectType_e]]`；对照 `ISelectionMgr\GetSelectedObjectMark.md` · **Signature**: `System.int GetSelectedObjectMark( System.int AtIndex )` · **Returns**: `Number used as a mark for the selected item` | 高 | **低** |

### 1.2 · `audit-05-drawing-B`（核对 B · 前置与 mark）— 7 条

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-02 | B · 前置 | **P 前置没做** | `ret = C.get_com_member(sheet, "SetTemplateName", str(format_path))`（整个 `set_sheet_format` 只有这一个写调用） | `ISheet\SetTemplateName.md` · `## Remarks`：`- a custom template name, before calling this method, call [[ISheet::SetProperties]] and specify swDwgTemplates_e.swDwgTemplateCustom for the Templ parameter.` | 高 | **中** |
| S2-03 | B · 前置 | **D 文档性分歧** | docstring 里 `★ 官方 Remarks 逐字：调完要 ForceRebuild3 才刷新第一角/第三角投影；★ 这里顺带做掉。`，紧接着 `C.get_com_member(drawing_model, "ForceRebuild3", False)` | `ISheet\SetTemplateName.md` · `## Remarks` 全段只有两句（自定义模板要 `SetProperties` / 标准模板不用调本方法）——**该页没有 `ForceRebuild3` 任何字样** | 高 | **低** |
| S2-04 | B · 前置 | **P 前置没做** | `pre = _selection_count(drawing_model)` / `pre_ok=pre > 0` | `IDrawingDoc\CreateSectionViewAt5.md` · `## Remarks`：`Before calling this method, select the section line or lines to use as a section line.` | 高 | **中** |
| S2-05 | B · 前置 | **P 前置没做** | 函数体只有 `res = D.add_detail_view(drawing_model, _mm(x_mm), _mm(y_mm), scale, style=style, label=label,` 一行（docstring 自述「★ 前置是"图上有局部圆（草图圆）"」，代码里没有） | `examples\Create_Detail_Circle_and_Detail_View_Example_VB.md` 调用序：`swDrawing.ActivateView("Drawing View4")` → `swSketchManager.CreateCircle(...)` → `swDrawing.CreateDetailViewAt4(...)` | 高 | **中** |
| S2-06 | B · 前置 | **P 前置没做** | `sel = _selection_count(model)` 与 `"preconditions_held": bool(sel and sel >= 1)` | `IDrawingDoc\CreateAuxiliaryViewAt2.md` · 首行摘要：`Creates an auxiliary view based on a selected edge in a drawing view.` | 中 | **中** |
| S2-07 | B · 前置 | **P 前置没做** | `sel = _selection_count(model)`、`"preconditions_held": bool(sel and sel >= 1)`（docstring 复述为「★ 官方第 1 步逐字：Select one or more **views or sheets**」） | `IDrawingDoc\AutoBalloon5.md` · `## Remarks`：`1. Select one or more views or sheets for which to automatically create BOM balloons.` | 中 | **中** |
| S2-08 | B · 前置 | **P 前置没做** | `res = D.auto_insert_center_marks(drawing_model, requirements)`（该包装层两步前置都不做、不回读） | `IView\AutoInsertCenterMarks2.md` · `## Remarks`：`Before calling this method:` / `1. Call [[IDrawingDoc::ActivateView]] with the name of the view to activate.` / `2. Call [[IDrawingDoc::ActiveDrawingView]] to get a handle on the activated view.` | 中 | **中** |

### 1.3 · `audit-05-drawing-C`（核对 C · 废弃链与枚举取值）— 4 条

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-09 | C · 废弃 | **O 用了废弃成员** | `scripts/sw_drawing_expose.py` — `if str(C.get_com_member(view, "Name") or "") == str(view_name):` | `IView\Name.md` — `Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].` | 高 | **高** |
| S2-10 | C · 废弃 | **O 用了废弃成员** | `scripts/sw_drawing_create_missing.py` — `    raw = _read(view, "Name")`（`_view_name()` 里 `GetName2` 返回 `None` 时的兜底） | `IView\Name.md` — `Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].` | 高 | **高** |
| S2-11 | C · 取值 | **E 取值不在合法域** | `scripts/sw_drawing_expose.py` — `                          template: str = "", shape: int = 0,`（随后由 `int(shape)` 传给 `ISheet.InsertRevisionTable2` 的 `Shape` 形参） | `enums\swRevisionTableSymbolShape_e.md` — `enum_member_count: 4`，成员值全是 `swRevisionTable_CircleSymbol \| 1` / `_SquareSymbol \| 2` / `_TriangleSymbol \| 3` / `_HexagonSymbol \| 4` ⇒ **没有 0** | 高 | **高** |
| S2-12 | C · 取值 | **E 取值不在合法域** | `scripts/sw_drawing_expose.py` — `                       no_outline: bool = False, shape_intensity: int = 0) -> dict:`（逐字透传到 `CreateDetailViewAt4` 第 12 参） | `IDrawingDoc\CreateDetailViewAt4.md` — `**ShapeIntensity**: ... valid range is 1 (most) to 5 (least)` | 高 | **高** |

### 1.4 · `audit-06-features-A`（核对 A · 签名一致性）— 1 条

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-13 | A · 签名 | **T 类型不符** | `scripts/sw_part.py`（`sketch_slot`）：`return model.SketchManager.CreateSketchSlot(` / `    0,  # swSketchSlotCreationType_e: 0=Straight` / `    radius, radius,  # 宽度` | `ISketchManager\CreateSketchSlot.md` — `SketchSlot CreateSketchSlot( System.int SlotCreationType, System.int SlotLengthType, System.double Width, ...`；反射 `SketchSlot CreateSketchSlot(Int32, Int32, Double, ...)` ⇒ 第 2 形参是**整数/枚举**，我们喂了同一个浮点 `radius` | 高 | **低** |

### 1.5 · `audit-06-features-B`（核对 B · 前置与 mark）— 6 条

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-14 | B · 前置 | **P 前置没做** | `sw_part.py` `revolve_boss`/`revolve_cut`：`if axis_sketch_name:` → `_select_revolve_axis(model, str(axis_sketch_name))` → 紧接着 `_ensure_sketch_selected(model, sketch_name)`，而它内部第一步是 `    model.ClearSelection2(True)` | `IFeatureManager\FeatureRevolve2.md`「Before calling this method, call [[IModelDocExtension::SelectByID2]] to select:」`- the sketch to revolve, using Mark = 0.` / `- the axis of revolution, using Mark = 4 or 16.` | 高 | **中** |
| S2-15 | B · mark | **P 前置没做** | `sw_part.py` `linear_pattern`（全函数只此一次选择）：`    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)` | `IFeatureManager\FeatureLinearPattern3.md`「ordered selection of the features and components is required」`- 1 and 2 to mark the directions` / `- 4 to mark the features to pattern` | 高 | **中** |
| S2-16 | B · 前置 | **P 前置没做** | `sw_part.py` `linear_pattern_report`（函数内**无任何** SelectByID2/Select）：`        get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",` | 同上 `FeatureLinearPattern3.md`「ordered selection of the features and components is required」 | 高 | **中** |
| S2-17 | B · 前置 | **P 前置没做** | `sw_part.py` `auto_dimension_sketch`：`    for segment, mark in ((vertical, 2), (horizontal, 4)):` / `        if segment is None:` / `            continue`（缺一个基准也照样调 `AutoDimension2`） | `ISketch\AutoDimension2.md`「**It is an error to supply just one datum** as indicated by the status value swAutodimStatus_DatumNotSupplied.」 | 高 | **中** |
| S2-18 | B · mark | **P 前置没做** | `sw_part.py` `fillet`（函数体内无任何选择代码，`edges` 形参收了不用）：`        edges: 预先选择的边线列表，None 则使用当前选择` / `    return model.FeatureManager.FeatureFillet(` | `IFeatureManager\FeatureFillet.md`「Before calling this method to create...」`Simple fillets` `1. Call [[IModelDocExtension::SelectByID2]] with Mark = 1 to select the edges to fillet.` | 中 | **中** |
| S2-19 | B · mark | **P 前置没做** | `sw_part.py` `shell`（`faces_to_remove` 形参收了不用）：`        faces_to_remove: 需预先选择要移除的面` / `    return model.InsertFeatureShell(thickness, False)` | `IModelDoc2\InsertFeatureShell.md`「Before calling this method, select faces to remove to create the shell using [[IModelDocExtension::SelectByID2]] with **Marks of 1**」 | 中 | **中** |

### 1.6 · `audit-06-features-C`（核对 C · 废弃链与枚举取值）— 9 条（**全部命中 O**）

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-20 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `return model.FeatureManager.FeatureFillet(` | `IFeatureManager\FeatureFillet.md` `Obsolete. Superseded by [[IFeatureManager::FeatureFillet2]].`（`FeatureFillet2.md` 亦 Obsolete ⇒ 现行入口 `FeatureFillet3`） | 高 | **低** |
| S2-21 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `return model.FeatureManager.FeatureLinearPattern3(` 与 `get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",` | `FeatureLinearPattern3.md` `Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].` ⇒ …`Pattern4` 也 Obsolete ⇒ 链尾是 `CreateFeature` + `ILinearPatternFeatureData` / `ILocalLinearPatternFeatureData`（三级 Obsolete） | 高 | **低** |
| S2-22 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `return model.FeatureManager.FeatureCircularPattern4(` | `FeatureCircularPattern4.md` `Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].`（`Pattern5` 亦 Obsolete ⇒ `CreateFeature` + `ICircularPatternFeatureData`） | 高 | **低** |
| S2-23 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `seg = get_com_member(model, "SketchManager").CreateSpline2(data, False)` | `ISketchManager\CreateSpline2.md` `Obsolete. Superseded by [[ISketchManager::CreateSpline3]].` | 高 | **高** |
| S2-24 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))` | `ISketch\AutoDimension2.md` `Obsolete. Superseded by [[ISketchManager::FullyDefineSketch]].` | 高 | **中** |
| S2-25 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `model.GraphicsRedraw2()` | `IModelDoc2\GraphicsRedraw2.md` `Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].` | 高 | **低** |
| S2-26 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `sk = get_com_member(model, "GetActiveSketch2")`（在 `_require_active_sketch` 的包装体内） | `IModelDoc2\GetActiveSketch2.md` `Obsolete. Superseded by [[SketchManager::ActiveSketch]].` | 高 | **高** |
| S2-27 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `if bool(segment.Select3(selected > 0, mark, _empty_callout())):`（下一行才是 `Select4` 兜底） | `ISketchSegment\Select3.md` `Obsolete. Superseded by [[ISketchSegment::Select4]].` | 高 | **高** |
| S2-28 | C · 废弃 | **O 用了废弃成员** | `sw_part.py` · `for method_name in ("Select2", "Select4"):`（`_select_com_object` **先试 `Select2`**） | `ISketchSegment\Select2.md` `Obsolete. Superseded by [[ISketchSegment::Select4]].` | 中 | **高** |

### 1.7 · `audit-07-sketch-C`（核对 C · 废弃链与枚举取值）— 5 条

| # | 核对面 | 根因类 | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|
| S2-29 | C · 废弃 | **O 用了废弃成员** | `scripts/sw_sketch_modify_ops.py` · `_active_sketch_name()`：`sk = get_com_member(model, "GetActiveSketch2")`（**只走这一条路，没有 `SketchManager.ActiveSketch` 回退**） | `IModelDoc2\GetActiveSketch2.md`：`Obsolete. Superseded by [[SketchManager::ActiveSketch]].` | 高 | **高** |
| S2-30 | C · 废弃 | **O 用了废弃成员** | `scripts/sw_sketch_edit.py` · `create_sketch_chamfer._seg_count()`：`sk = get_com_member(model, "GetActiveSketch2")` 下一行 `sk = get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")` | 同上（我们是**先调 Obsolete、再回退后继**） | 高 | **高** |
| S2-31 | C · 依据 | **D 文档性分歧** | `scripts/sw_sketch_modify_ops.py` · `sketch_flip()`：`⚠ AxisFlag 的**取值表官方两个源都没给** ⇒ ★ 按铁律 5 **原样透传 int，不猜语义**`；返回里 `"axis_flag_semantics": "官方 swapi 与 CHM 均未给取值表 —— 原样透传"` | `IModelDoc2\SketchModifyFlip.md`：`- **AxisFlag**: Axis about which to flip the sketch:` ／ `  - X = 1` ／ `  - Y = 2` | 高 | **低** |
| S2-32 | C · 取值 | **E 取值不在合法域** | `scripts/sw_sketch_edit.py` · `SKETCH_CHAMFER_TYPE`：`"distance_distance": 1,     # swSketchChamfer_DistanceDistance（⚠ md 写 -1，反射写 1，采用 1）` | `enums\swSketchChamferType_e.md`：`enum_member_count: 3`，成员表 `\| swSketchChamfer_DistanceAngle \| 0 \|` / `\| swSketchChamfer_DistanceDistance \| -1 \|` / `\| swSketchChamfer_DistanceEqual \| 2 \|` ⇒ 传给 `CreateChamfer` 的 `Type` 的 `1` **不是任何成员的值**（★ md 与出厂反射两源冲突，原文本身未判谁对） | 高 | **中** |
| S2-33 | C · 依据 | **D 文档性分歧** | `scripts/sw_sketch.py` · `SKETCH_CROSS_HATCH` 上方注释：`#: ⚠ swapi 只列了其中 3 个（Include/Exclude/AndExplodeOnly），**值相同**，无冲突。` ＋ `#: 反射里还有 swCrossHatchOnly = 2 · swSolidHatchOnly = 4。` | `enums\swCrossHatchFilter_e.md`：`enum_member_count: 5`，成员表含 `\| swCrossHatchAndExplodeOnly \| 3 \|` / `\| swCrossHatchExclude \| 1 \|` / `\| swCrossHatchInclude \| 0 \|` / `\| swCrossHatchOnly \| 2 \|` / `\| swSolidHatchOnly \| 4 \|` | 高 | **低** |

### 1.8 · 跨片重复（不算重复条目，仅记账）

- `IView.Name` 这个 Obsolete 成员在 `audit-05-drawing-A.md` 的「范围外备注」里被提到，但**该片明确声明不计入统计**（属核对 C）⇒ 它就是本表 S2-09 / S2-10，**本表不另计**。
- `IModelDoc2.GetActiveSketch2` 这一个 Obsolete 成员在 **06-C（S2-26）与 07-C（S2-29 / S2-30）** 三处被命中，分成 3 条计数（调用点不同、文件不同、修法也略有差别）。

---

## 2. 按类汇总

| 根因类 | 条数 | 占比 | 分布（核对面 / 域） | 静态**找全** | 共用**修法**改完 | 综合批量可行性 |
|---|---|---|---|---|---|---|
| **O · 用了废弃成员** | **13** | **39.4%** | C 面 × 13（05-C 2 · 06-C 9 · 07-C 2）· 跨域 3 个（drawing / features / sketch） | **高** | **中** | **中高** |
| **P · 前置没做 / 前置判据过弱** | **12** | **36.4%** | B 面 × 11（05-B 5 · 06-B 6）· A 面 × 1（05-A）| **中** | **中** | **中** |
| **E · 取值不在官方合法域** | 3 | 9.1% | C 面 × 3（05-C 2 · 07-C 1） | **高** | **高** | **高**（但量最小）|
| **D · 文档性分歧（注释与官方原文不符）** | 3 | 9.1% | B 面 × 1（05-B）· C 面 × 2（07-C） | **低** | **高** | **低** |
| **W · 取错了成员（语义错位）** | 1 | 3.0% | A 面 × 1（05-A） | 低 | 低 | **低** |
| **T · 实参类型与形参类型不符** | 1 | 3.0% | A 面 × 1（06-A） | 中 | 低 | **低** |
| **（无：参数个数 / 参数顺序 / 标量vs数组 / 返回值形状）** | **0** | 0% | — | — | — | — |
| **合计** | **33** | 100% | A 面 2 · B 面 12 · C 面 19 | | | |

★ **核对面分布很不均**：19/33 在核对 C（废弃与取值），12/33 在核对 B（前置），只有 2 条在核对 A（签名）
⇒ **本 shard 的分歧重心不在「签名写错」，而在「调用前的状态不对 + 调的是废弃入口」**。

---

## 3. 能不能「一类一修」

**结论先说：不能整类一修。** 但拆成「静态找全」与「共用修法改完」两半看，两半的答案完全不一样 —— 这就是本 shard 最重要的发现。

### 3.1 · 静态**找全**（一个脚本能不能把这一类全捞出来？）

| 类 | 答案 | 为什么 |
|---|---|---|
| **O** | ★★ **能** | 官方 Obsolete 标记是**一行机器可读文本**，形如 `Obsolete. Superseded by [[X::Y]].`，**每个 `C:\swapi\types\<接口>\<成员>.md` 顶部一条** ⇒ 建「成员名 → Obsolete 后继」索引，再拿我们的调用点（成员名 × 宿主接口）做一次 join 就完事。★ 3 个核对面的 C 片**本来就各自在做这件事**（05-C 核了 62 处成员、06-C 核了 53 个调用点、07-C 核了 50 处成员）—— **它已经是本仓现成的一等公民**。 |
| **E** | ★★ **能** | 判据形态有三样，但**都能解析**：① 枚举页的成员表（`enums\<枚举>.md` 的成员表是 markdown 表）；② 成员页正文里的范围句式（本 shard 命中的是 `valid range is 1 (most) to 5 (least)`）；③ 双源比对（`enums` 页 vs 出厂反射 dump）。难点不在「官方值域从哪来」，而在**把常量从调用点传播到形参位**（`int(shape)` 这种包装），这一层要做 AST，不能靠 grep。 |
| **P** | △ **半能** | `## Remarks` 段落的位置是确定的（`types\<接口>\<成员>.md` 里的固定小节）⇒ **「哪些成员该去查 Remarks」可以脚本枚举**；但 Remarks 是**自然语言散文**（「Before calling this method, select the section line or lines…」），要把它抽成「前置 = 选 X，mark = N」的结构化事实，**只能靠 LLM 逐成员读，没有判据函数**。 |
| **D** | ✗ **不能** | 判据本身是「**我们注释里写了『官方没给 / 没写』，而官方页其实给了**」—— 要把我们的注释与官方页做语义比对。**没有任何静态特征能定位候选**，只能全文搜「没给 / 没写 / 查不到 / 原样透传」这类措辞当粗筛，再逐条人工确认。 |
| **W / T** | ✗ / △ | W 只有 1 条，且要靠「返回值的**语义用途**与成员的官方定义对不上」来判（`out[str(mark)] = out.get(str(mark), 0) + 1` 这种下游用法，静态看不出来）；T 可以靠「反射的形参类型表 × 实参 AST 类型」查，但要看**我们的形参是否经过包装**。 |

### 3.2 · 共用**修法**改完（同一个改法能不能把这一类全改掉？）

这里答案**反过来**了 —— 越是「找起来容易」的类，**改起来越不整齐**：

- **O（13 条）—— 内部要分三档，不能一刀切**：
  1. **「废弃成员只出现在兜底/回退分支，后继已经在主路径」** ⇒ 修法就是**删掉那个兜底分支**，共 **5 条**：S2-09 / S2-10（`IView.Name` 兜底，主路径已是 `GetName2`）、S2-26（`sw_part.py` 同文件另一处已是 `SketchManager.ActiveSketch`）、S2-27（下一行就是 `Select4`）、S2-28（`("Select2","Select4")` 的 `Select2`）。**这一档是本 shard 最标准化的批量修复。**
  2. **「废弃成员在首位、后继没被调过」** ⇒ 换成后继调用，共 **3 条**：S2-23（`CreateSpline2`→`CreateSpline3`）、S2-29（`GetActiveSketch2`→`SketchManager.ActiveSketch`）、S2-30（调换先后顺序即可）。
  3. **「后继自己也是 Obsolete，链尾是 `CreateFeature` + `XxxFeatureData`」** ⇒ **整段调用形状都要重写**，共 **4 条**：S2-20（`FeatureFillet`→2→3）、S2-21（`FeatureLinearPattern3`→4→5→`CreateFeature`）、S2-22（`FeatureCircularPattern4`→5→`CreateFeature`）、S2-25（`GraphicsRedraw2` 换宿主到 `IModelView`）。**这 4 条没有任何共用的修法**，必须逐条按新接口的 `XxxFeatureData` 文档重写。
- **P（12 条）** —— 分两小档：
  - 「**前置判据只判选区计数、没判对象类型**」共 **4 条**（S2-04 / S2-06 / S2-07 / S2-08）⇒ **同一个改法**：把 `_selection_count(...) >= 1` 换成「按官方前置的对象类型 + mark 判」。**这 4 条是最值得批量改的**（同一个函数形态、同一个判据表达式）。
  - 「**前置这一步根本没做**」共 **8 条**（S2-02 / S2-05 / S2-14 / S2-15 / S2-16 / S2-17 / S2-18 / S2-19）⇒ 每条要补的 `SelectByID2` 对象与 mark **各不相同**（剖面线 / 局部圆 / 方向 mark 1+2 / Mark=1 的边 / Marks of 1 的面 / `SetProperties` …）⇒ **只能逐条按官方原文补**。
- **E（3 条）** —— ★ **修法完全统一**：把越界/非法默认值换成官方域内的保守值。S2-11（`shape=0` → 域内最小成员 `1`）、S2-12（`shape_intensity=0` → 域内最小值 `1`）、S2-32（`1` vs `-1` 是两源冲突，**这一条要先裁决用哪源**才能定修法 —— 所以它实际是「中」而不是「高」）。
- **D（3 条）** —— ★ **改法统一**（把「官方没给」改成引用官方原文），但**改法统一 ≠ 可批量**，因为**找全**这一步就卡住了 ⇒ 综合判「低」。
- **W（1 条）/ T（1 条）** —— 逐条，各一条。

### 3.3 · 量化结论

| 口径 | 条数 | 占比 |
|---|---|---|
| **检测**端能做到「一个静态脚本找全」 | **O 13 + E 3 = 16** | **48.5%** |
| **修复**端能做到「共用同一形态的改法」的子集 | O 第1档 5 + O 第2档 3 + P 的 4 + E 的 2（S2-11/S2-12，S2-32 待裁决）+ D 的 3 = **17** | **51.5%** |
| **两半都成立（真正的「一类一修」）** | **E 的 2 条** + **P 的 4 条**（判据形态统一）+ **O 的第 1 档 5 条** = **11 条** | **33.3%** |
| 必须逐条读官方原文再改 | **19 条** | 57.6% |

**一句话答案：**
★★ **不能一类一修。** 全 33 条里只有 **11 条（33%）** 真正「一类一修」得动 —— 也就是 **「废弃成员出现在兜底分支」这一档（5 条）**、
**「前置判据只判计数」这一档（4 条）**、**「取值越界」里的 2 条**。
其余 **19 条（58%）必须逐条读官方原文**（每条的 mark 值 / 前置对象 / 后继接口都不一样）。
★ 而 **O（13 条 · 39%）这一类恰恰是最不可整类修的**：它是**最好静态找全**的一类，却内含**三种互不相同的修法**（删兜底 / 换后继 / 按 `CreateFeature`+`FeatureData` 整段重写）。
⇒ ★★ **「找得全」与「改得动」在本 shard 是两个独立的轴，不能用同一个类目去推断批量收益。**

---

## 4. 我看到的三条与 Lead 首轮不同的判断

1. ★ **本 shard 里没有一条「mark 值填错」**。Lead 首轮「mark 类」占 33% 是全 17 片的数；在我这 7 片（工程图 / 高级特征 / 草图）里，
   涉及 mark 的分歧（06-B #4）原文自己写明「**两个 mark 值本身 2=horizontal datum / 4=vertical datum 与官方一致，不算分歧**」，
   05-C 也写明 `InsertHoleTable3` 的 mark gate「**官方示例实际只用了 mark 1 与 mark 2 ⇒ 不构成对不上，不报**」。
   ⇒ **这类分歧集中在别的域（选择族 / 仿真族），不在本 shard。** 但**「前置没做」在 B 面吃掉了 11 条** —— 它才是本 shard 的 mark 侧真问题。
2. ★ **必须单列「文档性分歧」（D）这一类**，否则会被按关键词误吸。Lead 的分类脚本里 `枚举` / `enum` / `取值表` 这几个关键词会把
   S2-31（`SketchModifyFlip` 的 `AxisFlag` 其实**官方给了** `X=1 / Y=2`）和 S2-33（`swCrossHatchFilter_e` 其实**官方列全了 5 个**）吸进「枚举类」——
   但它们**跟枚举取值对不对毫无关系**，是**我们的注释对官方文档做了错误的存在性声明**。这类最容易被漏掉，因为代码本身能跑。
3. ★ **S2-03（`ForceRebuild3` 的「官方 Remarks 逐字」标注）也属 D 类**，它藏在核对 B 里 —— 核对 B 的口径是「前置与 mark」，
   这条既不是前置也不是 mark，是**注释声称官方写了而官方页没有** ⇒ **单开一类之后，它才从 B 面的「前置没做」里露出来。**

---

**抽了 33 条**（05-A 1 · 05-B 7 · 05-C 4 · 06-A 1 · 06-B 6 · 06-C 9 · 07-C 5；`audit-07-sketch-A/B` 本仓不存在，域 07 只有 C 面有输入）。