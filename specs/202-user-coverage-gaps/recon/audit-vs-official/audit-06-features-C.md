# 核对 06-features · C（废弃链与枚举取值）

- **域**：06-features
- **只读文件**：`scripts/sw_part.py` · `scripts/sw_feature_entry_ops.py` · `scripts/sw_feature_readback.py`（三个文件都存在，无需 glob 兜底）
- **官方源**：`C:\swapi\types\<接口>\<成员>.md` · `C:\swapi\enums\<枚举>.md`
- **只报一种东西**：我们代码与官方原文对不上的地方。

---

## 表

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `sw_part.py` · `return model.FeatureManager.FeatureFillet(` … `195, radius, 0, 0, None, None, None` | `types/IFeatureManager/FeatureFillet.md` · `Obsolete. Superseded by [[IFeatureManager::FeatureFillet2]].`（且 `types/IFeatureManager/FeatureFillet2.md` · `Obsolete. Superseded by [[IFeatureManager::FeatureFillet3]].`） | 我们调的 `IFeatureManager.FeatureFillet` 被官方标 **Obsolete**；官方点名的后继是 `FeatureFillet2`，而 `FeatureFillet2` 自己也是 Obsolete ⇒ 现行入口是 `FeatureFillet3` | 高 |
| 2 | `sw_part.py` · `return model.FeatureManager.FeatureLinearPattern3(` （`linear_pattern`）与 `get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",` （`linear_pattern_report`） | `types/IFeatureManager/FeatureLinearPattern3.md` · `Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].`（`…Pattern4.md` 逐字 `Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern5]].`；`…Pattern5.md` 逐字 `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ILinearPatternFeatureData]] and [[ILocalLinearPatternFeatureData]].`） | 两处调用点都调在 **Obsolete** 成员上；官方点名的后继链走到底是 `CreateFeature` + `ILinearPatternFeatureData` / `ILocalLinearPatternFeatureData`（三级 Obsolete） | 高 |
| 3 | `sw_part.py` · `return model.FeatureManager.FeatureCircularPattern4(` | `types/IFeatureManager/FeatureCircularPattern4.md` · `Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].`（`…Pattern5.md` 逐字 `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ICircularPatternFeatureData]] and [[ILocalCircularPatternFeatureData]].`） | 我们调的成员是 **Obsolete**；官方点名的后继 `FeatureCircularPattern5` 亦 Obsolete ⇒ 后继是 `CreateFeature` + `ICircularPatternFeatureData` / `ILocalCircularPatternFeatureData`（两级 Obsolete） | 高 |
| 4 | `sw_part.py` · `seg = get_com_member(model, "SketchManager").CreateSpline2(data, False)` | `types/ISketchManager/CreateSpline2.md` · `Obsolete. Superseded by [[ISketchManager::CreateSpline3]].` | 我们调的是官方标 **Obsolete** 的 `ISketchManager.CreateSpline2`；官方点名后继 `CreateSpline3`。（★ 本函数 docstring 自己已逐字记了这条 —— 事实对上了，但调用点仍未换） | 高 |
| 5 | `sw_part.py` · `status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))` | `types/ISketch/AutoDimension2.md` · `Obsolete. Superseded by [[ISketchManager::FullyDefineSketch]].` | 我们调的 `ISketch.AutoDimension2` 被官方标 **Obsolete**；官方点名的后继是 `ISketchManager::FullyDefineSketch` | 高 |
| 6 | `sw_part.py` · `model.GraphicsRedraw2()` | `types/IModelDoc2/GraphicsRedraw2.md` · `Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].` | 我们在 `IModelDoc2` 上调的 `GraphicsRedraw2` 是 **Obsolete**；官方点名后继为 `IModelView::GraphicsRedraw` 与 `IModelView::IGraphicsRedraw` | 高 |
| 7 | `sw_part.py` · `sk = get_com_member(model, "GetActiveSketch2")`（在 `_require_active_sketch` 的包装体内） | `types/IModelDoc2/GetActiveSketch2.md` · `Obsolete. Superseded by [[SketchManager::ActiveSketch]].` | 我们在 `IModelDoc2` 上调的 `GetActiveSketch2` 是 **Obsolete**；官方点名后继为 `SketchManager::ActiveSketch`（★ 同文件另一处 `model.SketchManager.ActiveSketch` 已经是后继写法，两条路并存） | 高 |
| 8 | `sw_part.py` · `if bool(segment.Select3(selected > 0, mark, _empty_callout())):` | `types/ISketchSegment/Select3.md` · `Obsolete. Superseded by [[ISketchSegment::Select4]].`（这些 segment 来自 `types/ISketch/GetSketchSegments.md` · `Array of [[sketch segments]]`） | 我们在 `ISketchSegment` 上调的 `Select3` 是 **Obsolete**；官方点名后继 `ISketchSegment::Select4`（下一行已是 `Select4` 兜底，但只在 `Select3` **抛异常**时才走到） | 高 |
| 9 | `sw_part.py` · `for method_name in ("Select2", "Select4"):`（在 `_select_com_object` 内） | `types/ISketchSegment/Select2.md` · `Obsolete. Superseded by [[ISketchSegment::Select4]].` | `_select_com_object` **先试 `Select2`**；对 `ISketchSegment` 输入（`_select_sketch_ref` 的 `sketch_ref.segments`、`_select_revolve_axis` 的 `seg`）而言 `Select2` 已被官方标 **Obsolete** | 中 |

---

## 核对 C ② · 字面量当枚举传的地方（**全部合法，0 条发现**）

逐个对 `C:\swapi\enums\*.md` 查过，命中的都是合法成员：

| 字面量 | 我们的注释/实参 | `enums/*.md` 原文 | 结论 |
|---|---|---|---|
| `195` | `fillet` 的 `Options` | `swFeatureFilletOptions_e`：`swFeatureFilletPropagate \| 1 or 0x1` · `swFeatureFilletUniformRadius \| 2 or 0x2` · `swFeatureFilletAttachEdges \| 64 or 0x40` · `swFeatureFilletKeepFeatures \| 128 or 0x80` | 195 = 1+2+64+128，四项均为合法位成员 |
| `0` | `fillet` 的 `Ftyp` / `OverflowType` | `swFeatureFilletType_e`：`swFeatureFilletType_Simple \| 0` · `swFilletOverFlowType_e`：`swFilletOverFlowType_Default \| 0` | 合法 |
| `4` / `1` | `chamfer` 的 `Options` / `ChamferType` | `swFeatureChamferOption_e`：`swFeatureChamferTangentPropagation \| 4 or 0x4` · `swChamferType_e`：`swChamferAngleDistance \| 1` | 合法 |
| `0` `0` `6` | `FeatureExtrusion3` 的 `T1/T2`、`FeatureCut4` 的终止条件、`FeatureRevolve2` 的 `Dir1Type/Dir2Type` | `swEndConditions_e`：`swEndCondBlind \| 0` · `swEndCondThroughAll \| 1` · `swEndCondMidPlane \| 6` | 合法 |
| `0` | `FeatureRevolve2` 的 `ThinType` | `swThinWallType_e`：`swThinWallOneDirection \| 0` | 合法 |
| `0` | `InsertMirrorFeature2` 的 `ScopeOptions` | `swFeatureScope_e`：`swFeatureScope_AllBodies \| 0` | 合法 |
| `1` `1` `-1` `1` `-1` | `AutoDimension2` 五个实参 | `swAutodimEntities_e`：`swAutodimEntitiesAll \| 1` · `swAutodimScheme_e`：`swAutodimSchemeBaseline \| 1` · `swAutodimHorizontalPlacement_e`：`swAutodimHorizontalPlacementBelow \| -1` · `swAutodimVerticalPlacement_e`：`swAutodimVerticalPlacementLeft \| -1` | 合法 |
| `2` / `4` | `auto_dimension_sketch` 的两个 mark | `swAutodimMark_e`：`swAutodimMarkHorizontalDatum \| 2 or 0x2` · `swAutodimMarkVerticalDatum \| 4 or 0x4` | 合法 |
| `0` / `1` | `CreateSketchSlot` 的 `SlotCreationType` / `CenterArcDirection` | `swSketchSlotCreationType_e`：`swSketchSlotCreationType_line \| 0 = Straight` · `CreateSketchSlot.md`：`1 = Counterclockwise (CCW)` | 合法 |
| `1` | `insert_cosmetic_thread` 的 `Standard`（`STD_ANSI_METRIC`） | `swCosmeticStandardType_e`：`swStandardType_StandardAnsiMetric \| 1` | 合法 |
| `0` / `2` | `END_TYPE_BLIND` / `END_TYPE_THROUGH` | `swCosmeticEndConditions_e`：`swEndConditionBlind \| 0` · `swEndConditionThrough \| 2` | 合法 |
| `0` / `1` | `_BODY_TYPE_SOLID` / `_BODY_TYPE_SURFACE` | `swBodyType_e`：`swSolidBody \| 0 = Solid body` · `swSheetBody \| 1 = Sheet body` | 合法 |
| `0` | `thicken_surface` 的 `direction` | `swThickenDirection_e`：`swThickenDirection_Side1 \| 0` | 合法 |
| `1` `16` `2` `4` `8` | `create_flatten_surface` 的 mark | `InsertFlattenSurface2.md`：`Faces or surfaces to flatten 1` / `Anchor point from which to flatten 16` / `Edges to guide the shape … 2` / `Map edges 4` / `Tear edges 8` | 与官方逐字一致 |

---

## 已核查但**未**报的点（避免误报，列出以示口径）

- **同名异接口的 Obsolete 不算数**（事实 36 那条纪律）：`IModelDoc2.FeatureExtrusion3` / `IModelDoc2.FeatureCut4` / `IModelDoc2.FeatureRevolve2` / `IModelDoc2.InsertRib` / `IModelDoc2.InsertSketch` / `IModelDoc2.CreateLine` / `CreateEllipse` / `CreateCenterLine` / `CreateCircleByRadius` / `CreateArc` / `IModelDoc2.FeatureBossThicken` / `IModelDoc2.FeatureCutThicken` / `IComponent2.GetBodies2` 在**它们各自那一页**上都带 Obsolete —— 但我们调的是 `model.FeatureManager.*` / `model.SketchManager.*` / `IPartDoc.GetBodies2`，那些页**没有** Obsolete 行 ⇒ **不报**。
- `sw_feature_entry_ops.py` 的文件头断言「`InsertCosmeticThread3`（**7 参**，md **未标 Obsolete**）」与 `thicken_surface` 的「✓ **未废弃**：`IFeatureManager.FeatureBossThicken`（**7 参**）· `IFeatureManager.FeatureCutThicken`（**6 参**）」—— 两页逐字均无 Obsolete 行 ⇒ 与官方一致，**不报**。
- `sw_feature_readback.py` 全部成员（`FirstFeature` / `EditRebuild3` / `GetNextFeature` / `Name` / `GetTypeName2` / `GetWhatsWrongCount` / `GetWhatsWrong`）逐页读过，**均无** Obsolete 行 ⇒ **不报**。
- `IFeature.Select2` **没有** Obsolete 行 ⇒ `_select_com_object` 的第 9 条只落在 `ISketchSegment::Select2` 上，不扩大到面/边/顶点。
- **查不到就说查不到**：`C:\swapi\types\IFace2\` 与 `IVertex\` 目录下**没有** `Select2.md` / `Select3.md`，`IEdge2` 目录整个不存在 ⇒ 关于面/边/顶点的 `Select2`，两套离线源都给不出原文，**不报**。

---

核了几处：① 废弃链 **53 个调用点**逐个对 `C:\swapi\types\<接口>\<成员>.md` 顶部 Obsolete 行（另排除 30 处「同名异接口」误报）＋ ② 枚举字面量 **30 处**逐个对 `C:\swapi\enums\*.md` = **共 83 处**。
报了几条：**9 条**（全部来自 ①；② 全部合法，0 条）。
高置信：**#1 #2 #3 #4 #5 #6 #7 #8 共 8 条为高**；**#9 为中**。
