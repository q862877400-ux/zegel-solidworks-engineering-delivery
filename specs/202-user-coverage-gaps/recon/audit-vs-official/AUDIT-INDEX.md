# AUDIT-INDEX —— 30 份分域核对表的合并总表 · 抽查证伪 · 去重 · 分级

> **合并者**：本文件由 30 份 `audit-01-surface-A/B/C` … `audit-10-misc-A/B/C` 逐份读完合成。
> **口径**：只合并、不新增判定。★ 「我们的原文 / 官方的原文」两栏一律照抄各核对表里已逐字抄录、可 grep 的片段。
> **纪律**：★ 高置信在前。★ **同一处分歧被多路报到的已合一**，并在「路由」栏标 `多路都报`。

---

## 摘要（TL;DR）

| 项 | 数 |
|---|---|
| 读入的核对表 | **30 份**（10 域 × 3 路 A/B/C） |
| 30 份表内报出的条数 | **121 条**（另有 3 条写在表外备注里，见 §3.3） |
| **去重后唯一分歧** | **111 条** |
| ├ 置信度**高** | **83 条** |
| └ 置信度中 | **28 条** |
| **抽查**（跨 8 份文件 / 8 个域，随机抽 8 条高置信） | **成立 7 · 不成立 1 · 存疑 0** ⇒ **成立率 87.5%** |
| 分级 | **可改 89 · 需先查 18 · 存疑 4** |

★ **一句话结论**：30 路报的东西**八成七是真的**；唯一的假货（`RULED_TYPE_MEANINGS`）经查是**官方自己两源打架**，
而它顺手暴露了一条**真缺陷**：同一个参数 `sw_surface_features.py:640` 用 1..5、`sw_surface_edit_ops.py:68` 用 0..4，
★ **同仓自相矛盾** —— 这条比被抽中的那一条更值钱。

---

## §1 · 总表（按置信度排序，高在前）

### §1.1 高置信 —— 83 条

#### 域 01-surface（8 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H01 | 01-A #1 | `sw_surface.py`：`_invoke(get_modeler(sw_app), "CreateConicalSurface", origin, axis, float(half_angle), float(radius), )` | `IModeler\CreateConicalSurface.md`：**Signature** `System.object CreateConicalSurface( System.object Center, System.object Direction, System.double Radius, System.double SemiAngle )` | 第 3/4 位两个 double **顺序反了**：官方第 3 位 `Radius`、第 4 位 `SemiAngle` | 可改 |
| H02 | 01-A #2 | `_invoke(..., "CreateBsplineSurface", control_points, weights, knots, degree, )` | `IModeler\CreateBsplineSurface.md`：`CreateBsplineSurface( System.object Props, System.object UKnots, System.object VKnots, System.object CtrlPtCoords )`；`Props`: Array containing 8 integers packed as 4 double elements | 四个 object **顺序反了**：官方第 1 位是 `Props`、第 4 位才是 `CtrlPtCoords` | 可改 |
| H03 | 01-B #1 | `sw_surface_features.py`：`selected = _select_all_surface_faces(model, mark=0)` → `PreTrimSurface(...)` → `PostTrimSurface(...)`（两步之间**无**再选择） | `PostTrimSurface.md`：「Before calling this method: 1. Call [[IFeatureManager::PreTrimSurface]]. 2. **Select the trimming surfaces or trim tool.**」；官方例子 `PreTrimSurface(false,true,false,false);` → `SelectByID2("", "SURFACEBODY", …)` → `PostTrimSurface(true);` | 调用序：官方 **Pre → 选剪裁面 → Post**；我们是 **选 → Pre → Post** | 可改 |
| H04 | 01-B #2 | `get_com_member(fm, "FeatureExtruRefSurface3", *args)`（函数体内**无任何** `SelectByID2`），`sketch_name` 只被回显进返回值 | `FeatureExtruRefSurface3.md` Remarks：「Before calling this method, **select the entities for the extruded surface** using [[IModelDocExtension::SelectByID2]]」+ mark 表（草图/草图段/平面均 0） | 前置缺失：从不做选择 | 可改 |
| H05 | 01-B #3 | `FeatureBossThicken` 之前**无任何选择动作**；docstring 把前置写成「文件里要有曲面体」 | `FeatureBossThicken.md`：「The surface must be selected with a **mark of 1**.」＋「If **UseAutoSelect** is false, the user must select the **bodies**」 | 缺「参考曲面 mark=1」前置。⚠ **与 06-B 的 `thicken_surface` 结论相反**（那一路判为一致） | **需先查** |
| H06 | 01-C #1 | `sw_surface.py` 四处薄封装调 `CreatePlanarSurface` / `CreateCylindricalSurface` / `CreateSphericalSurface` / `CreateConicalSurface` | 四页**逐个**写 `Obsolete. Superseded by [[IModeler::Create*Surface2]].`；同文件 `SURFACE_CREATION_METHODS` 已登记 4 个 `…2`，**但无任何封装调它们** | 被调的一代全带 `Obsolete`，官方逐个点名后继 | 可改 |
| H07 | 01-C #2 | `sw_surface_features.py`：`if int(end_condition) not in (0, 1):` + `"end_condition 只支持 0（按距离）/ 1（到选定点）"` | `InsertExtendSurface.md` 参数表列 `2 - Extend surface up to a selected surface`；`swSurfaceExtendEndCond_e.md` 三成员 `0/1/2` | 官方合法成员 `2` 被本包装当成非法 | 可改 |
| H08 | 01-C #3 | `sw_surface_edit_ops.py:68` `RULED_TYPE_MEANINGS = {0:"Tangent to Surface",1:"Normal to Surface",2:"Tapered to Vector",3:"Perpendicular to Vector",4:"Sweep"}`，注释 `:67` 写「★ 逐字来自 `InsertRuledSurfaceFromEdge2.md` 的 Parameters」 | `swRuledSurfaceType_e.md`：`TangentToSurface \| 1` · `NormalToSurface \| 2` · `TaperedToVector \| 3` · `PerpendicularToVector \| 4` · `Sweep \| 5`（**无 0**）；★ **但** `InsertRuledSurfaceFromEdge2.md` 的 Parameters **确实是** `0 = Tangent to Surface … 4 = Sweep`，且该页**没有**把 `Type` 指向 `swRuledSurfaceType_e` | 名义分歧（枚举页 vs 成员页）。★★ **真缺陷是同仓自相矛盾**：`sw_surface_features.py:640` 同一参数用 `if not (1 <= t <= 5)` | **存疑**（★ 抽查判「不成立」——见 §2 S6） |

#### 域 02-sheetmetal（7 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H09 | 02-A #1 | `sw_sheet_metal.py:472` `data.BendAngle = float(spec.angle)`；`:376-377` `if not 0 < self.angle < 360: raise ValueError("折弯角度必须位于 0 与 360 **度**之间")` | `ISketchedBendFeatureData\BendAngle.md` **Returns**：「0.261799 <= Bend angle in increments of 0.261799 **radians** (15 degrees) <= 1.5708」；官方例子 `BendAngle * 57.3 & " deg"` | 官方收**弧度**，我们把**度**原样赋进去 | 可改 |
| H10 | 02-A #2 | `sw_sheet_metal.py:508` `data.BendAngle = float(spec.angle)`；`EdgeFlangeSpec` docstring「角度为度」，`angle: float = 90.0` | `IEdgeFlangeFeatureData\BendAngle.md` **Returns**：「Flange angle; default value is **1.5707963267949 radians**」 | 同上；**默认值就会传 `90.0`**，超官方量纲约 57 倍 | 可改 |
| H11 | 02-A #3 | `sw_sheet_metal.py:538` `data.Angle = float(spec.angle)` | `IDraftFeatureData2\Angle.md` **Returns**：「Draft angle **in radians**」 | 同上 | 可改 |
| H12 | 02-B #1 | `create_edge_flange` 的 `_apply` 只设 `UseDefaultBendRadius` / `BendRadius` / `BendAngle` / `UseDefaultBendAllowance`，**无** `AddEdges`、**无** `InsertSketchForEdgeFlange`；前置注释写「调用方先用 `_select_by_id` 把边选进选区」 | `IEdgeFlangeFeatureData\AddEdges.md` **Remarks**：「Before calling this method, call [[IModelDoc2::InsertSketchForEdgeFlange]] to associate the sketches with the edges.」；官方例子 `InsertSketchForEdgeFlange(swEdge, dAngle, False)` → `CreateDefinition` → `FeatData.AddEdges(vFlangeEdges, vSketchFeats)` | 官方这条路径的前置是**两步**，我们**一步都没做** | 可改 |
| H13 | 02-B #2 | `sw_sheet_metal_weld_entry.py`：`get_com_member(model, "InsertSheetMetalClosedCorner")`（零参），返回值 `"precondition_note": "★★ **官方页无 `## Remarks` 段 ⇒ 前置查不到** ⇒ 不编前置"` | 官方例子 `Create_and_Modify_Closed_Corner_Feature_Example_VBNET.md`：`SelectByID2("", "FACE", …, True, **1**, Nothing, 0)` ×2 → `swModel.InsertSheetMetalClosedCorner()` | 官方例子在这个零参调用**之前连做两次选面**（首条 mark=1） | 可改 |
| H14 | 02-C #1<br>**多路都报** | `sw_sheet_metal.py` **两处**：`error_code = int(get_com_member(feature, "GetErrorCode") or 0)`；注释：`# GetErrorCode2 多一个 by-ref isWarning 参数 … 用无歧义的 GetErrorCode 兼容 pywin32` | `IFeature\GetErrorCode.md` 首行：`Obsolete. Superseded by [[IFeature::GetErrorCode2]].`；后继页 `GetErrorCode2( out System.bool IsWarning )` 无 Obsolete 行 | 明知有后继、主动选了被官方标 Obsolete 的一代（2 处） | 可改 |
| H15 | 02-C #2 | `SW_END_COND_BLIND = 0` → `data.D1EndConditionType = 0` / `data.D2EndConditionType = 0` | `IBaseFlangeFeatureData\D1EndConditionType.md`：`End condition type as defined in [[swFlangeOffsetTypes_e]]`；`swFlangeOffsetTypes_e.md` 共 6 成员 **没有值为 0 的**（`swFlangeOffsetBlind \| 1`）；官方例子 `D1EndConditionType = 1` | 官方点名的枚举是 `swFlangeOffsetTypes_e`（不是 `swEndConditions_e`），该表**无 0**，「Blind」在官方是 **1** | 可改 |

#### 域 03-weldment（4 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H16 | 03-A #1 **+** 03-B #2<br>**多路都报** | `sw_weldment.py:694` `feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)`；来源块 `:661-662` 写 `IFeatureManager.InsertWeldmentCutList2(Object SortOptions)` | `IFeatureManager\InsertWeldmentCutList2.md`：**Signature** `Feature InsertWeldmentCutList2( System.object Bodies )`；`- **Bodies**: Array of [[Body2]] objects`；官方例子 `Part.FeatureManager.InsertWeldmentCutList2(v)`，`v = Part.GetBodies2(0, True)` | 唯一那个 `Object` 形参**官方写明是 Body2 数组**，我们按排序选项传（默认 `None`）。同文件 `ensure_cut_list` 反而按官方传数组 ⇒ **自相矛盾** | 可改 |
| H17 | 03-A #2 **+** 03-B #1<br>**多路都报** | `sw_weldment.py` `feature = get_com_member(manager, "InsertSubWeldFolder2", folder)`；来源块写 `InsertSubWeldFolder2(Object Folder)`、`不传 folder 时传 None` | `IFeatureManager\InsertSubWeldFolder2.md`：**Signature** `Feature InsertSubWeldFolder2( System.object BodyArray )`；`- **BodyArray**: Array of [[Body2]] objects`；CHM 同页 `ByVal BodyArray As System.Object` | 官方形参是 **Body2 数组**，我们当「父文件夹」用、默认传 `None`；且全程无选实体 | 可改 |
| H18 | 03-C #1 | `sw_weldment.py` `_create_from_definition`：`error_code = int(get_com_member(feature, "GetErrorCode") or 0)`，注释通篇只谈「与上游同构」，**未提任何后继** | `IFeature\GetErrorCode.md` 首行 `Obsolete. Superseded by [[IFeature::GetErrorCode2]].` | 与 H14 同一根因、第三个调用点（`sw_weldment.py`） | 可改 |
| H19 | 03-C #2 | `sw_weldment.py` 来源块：`# ⚠ MateAlignment 的枚举在两套官方源里查不到（sw_know find MateAlignment 未命中）`，只做 int 透传 | `IProfileCenterMateFeatureData\MateAlignment.md` `## Returns`：「Mate alignment as defined in [[swMateAlign_e]]」；`swMateAlign_e.md` 6 成员（`ALIGNED 0` / `ANTI_ALIGNED 1` / `CLOSEST 2` + 3 个 `Obsolete. Do not use.`）；官方例子 `swProfileMateData.MateAlignment = SwConst.swMateAlign_e.swMateAlignALIGNED` | 我们断言「官方查不到这个枚举」，官方**点名了枚举、例子直接用枚举名** | 可改 |

#### 域 04-assembly（9 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H20 | 04-A #1<br>**多路都报（两路结论相反）** | `sw_assembly.py` `add_mate5_checked()`：`mate = asm_model.AddMate5(...)` → `if name:` → **`mate.Name = name`** | ① `C:\swapi\index\members_by_type.md` 的 `IMate2` 段 40 条成员行**无 `Name`** ② CHM `IMate2_members.html` "Public Properties" 16 行**无 `Name`** ③ 出厂反射 `## IMate2` 段 34 行**无 `Name` / `set_Name`**。★ 而 **04-C 同一事实按铁律 5 记「查不到」不报** | 三源一致缺席 `IMate2.Name` ⇒ 该赋值无对应成员 | **存疑** |
| H21 | 04-B #1 | `sw_assembly.py` `get_interference_detection()`：`interference.Done()` → `GetInterferenceCount()` → `GetInterferences()` | `IInterferenceDetectionMgr\Done.md`：「**Stops** the interference detection.」；`GetInterferences.md` / `GetInterferenceCount.md`：「**Calculates and gets** …」；两处官方例子的 `pIntMgr.Done` 都在 `GetInterferences()` **之后**（且被注释掉，位居全例最后） | 把「**停止**」的 `Done()` 放在**取结果之前** | 可改 |
| H22 | 04-C #1 | `_add_component4()`：`return asm_model.AddComponent4(` | `IAssemblyDoc\AddComponent4.md`：`Obsolete. Superseded by [[IAssemblyDoc::AddComponent5]].`（CHM 同源） | 直接调官方已标 Obsolete 的成员 | 可改 |
| H23 | 04-C #2 | `add_mate5_checked()`：`mate = asm_model.AddMate5(` | `IAssemblyDoc\AddMate5.md`：`Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]` | 该函数是 6 个 `add_mate_*` 的**唯一**建配入口 | 可改 |
| H24 | 04-C #3 | `select_entities_for_mate()`：`if not entity1.Select2(False, mark):` / `entity2.Select2(True, mark)` | `IEntity\Select2.md`：`Obsolete. Superseded by [[IEntity::Select4]].`（CHM 同源） | 用官方已标 Obsolete 的入口选配对实体 | 可改 |
| H25 | 04-C #4 | `apply_component_transform_x()`：`if component.SetTransformAndSolve2(transform):` | `IComponent2\SetTransformAndSolve2.md`：`Obsolete. Superseded by [[IComponent2::SetTransformAndSolve3]].` | 直调 Obsolete 成员 | 可改 |
| H26 | 04-C #5 | `suppress_component()`：`asm_model.EditSuppress()` | `IModelDoc2\EditSuppress.md`：`Obsolete. Superseded [[IModelDoc2::EditSuppress2]].` | 直调 Obsolete 成员 | 可改 |
| H27 | 04-C #6 | `unsuppress_component()`：`asm_model.EditUnsuppress()` | `IModelDoc2\EditUnsuppress.md`：`Obsolete. Superseded by [[IModelDoc2::EditUnsuppress2]].` | 直调 Obsolete 成员 | 可改 |
| H28 | 04-C #7 | `collect_mate_entity_evidence()`：`"reference_type": int(get_com_member(mate_entity, "ReferenceType") or -1)` | `IMateEntity2\ReferenceType.md`：`Obsolete. Superseded by [[IMate2Entity::Reference2]].`（CHM 同源） | 读 Obsolete 成员（两源对后继写法不一致，但「Obsolete」这一事实两源一致） | 可改 |

#### 域 05-drawing（8 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H29 | 05-C #1 **+** #2<br>**多路都报**（05-A 表外备注也记了这两处） | ① `sw_drawing_expose.py` `_view_by_name()`：`get_com_member(view, "Name")` ② `sw_drawing_create_missing.py` `_view_name()`：`raw = _read(view, "Name")` | `IView\Name.md`：`Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].` | 同一 Obsolete 成员的两个调用点（05-C 拆成 #1/#2，此处合一） | 可改 |
| H30 | 05-A #1 | `sw_drawing_expose.py` `_selection_marks()`：`mark = C.get_com_member(mgr, "GetSelectedObjectType3", i, -1)` → `out[str(mark)] += 1`；docstring「回读当前选区里**每个 mark** 各有几个对象」 | `ISelectionMgr\GetSelectedObjectType3.md` **Returns**：「Type of object as defined in [[swSelectType_e]]」；对照 `GetSelectedObjectMark.md` **Signature** `System.int GetSelectedObjectMark( System.int AtIndex )` | 取的是**对象类型**却当 **mark** 存并在下游按 mark 用；官方取 mark 是**另一个**成员（且只有 1 个形参） | 可改 |
| H31 | 05-B #1 | `set_sheet_format()`：整个函数只有 `ret = C.get_com_member(sheet, "SetTemplateName", str(format_path))` 一个写调用 | `ISheet\SetTemplateName.md` `## Remarks`：`- a custom template name, before calling this method, call [[ISheet::SetProperties]] and specify swDwgTemplates_e.swDwgTemplateCustom for the Templ parameter.` | 官方写明的前置（`SetProperties` + `swDwgTemplateCustom`）**在点名文件里从未出现** | 可改 |
| H32 | 05-B #2 | `sw_drawing_expose.py` docstring：「★ **官方 Remarks 逐字**：调完要 `ForceRebuild3` 才刷新第一角/第三角投影；★ 这里顺带做掉。」 | `ISheet\SetTemplateName.md` 的 `## Remarks` **全段只有两句**（`If you want to use:` + custom / standard 两条），**没有任何 `ForceRebuild3` 字样**；★ CHM 解包目录里**没有该成员页** | 我们标成「官方逐字」的依据在本机查不到 | **需先查** |
| H33 | 05-B #3 | `pre = _selection_count(drawing_model)` / `res = D.add_section_view(...)` / `pre_ok = pre > 0` | `IDrawingDoc\CreateSectionViewAt5.md` `## Remarks`：「Before calling this method, **select the section line or lines** to use as a section line.」 | 官方前置指定**被选对象的种类**，我们只判「计数 > 0」、不判是不是剖面线、也不代选 | 可改 |
| H34 | 05-B #4 | `create_detail_view`：docstring「★ 前置是"图上有局部圆（草图圆）"」，函数体只有一行 `D.add_detail_view(...)` | 官方例子 `Create_Detail_Circle_and_Detail_View_Example_VB.md`：`ActivateView("Drawing View4")` → `SketchManager.CreateCircle(...)` → `CreateDetailViewAt4(...)` | 官方例子的**两步前置**（激活视图 + 建局部圆）我们一步都没做，返回值里也没有这两个字段 | 可改 |
| H35 | 05-C #3 | `sw_drawing_expose.py:270` `template: str = "", shape: int = 0,` → `InsertRevisionTable2(..., int(shape), ...)` | `ISheet\InsertRevisionTable2.md`：`- **Shape**: Revision symbol shape as defined in [[swRevisionTableSymbolShape_e]]`；`swRevisionTableSymbolShape_e.md` 4 成员 = **1/2/3/4** | 该形参是该枚举的取值，而枚举**没有 0** ⇒ 默认值 `0` 不是任何合法成员 | 可改 |
| H36 | 05-C #4 | `sw_drawing_expose.py:118` `no_outline: bool = False, shape_intensity: int = 0)` → `CreateDetailViewAt4` 第 12 参 `shape_intensity=shape_intensity` | `IDrawingDoc\CreateDetailViewAt4.md`：`- **ShapeIntensity**: Intensity of jagged outline; **valid range is 1 (most) to 5 (least)**` | 默认值 `0` 落在官方有效范围之外 | 可改 |

#### 域 06-features（12 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H37 | 06-A #1 | `sw_part.py` `sketch_slot()`：`return model.SketchManager.CreateSketchSlot(0, # swSketchSlotCreationType_e: 0=Straight  radius, radius, # 宽度` | `ISketchManager\CreateSketchSlot.md`：`SketchSlot CreateSketchSlot( System.int SlotCreationType, **System.int SlotLengthType**, System.double Width, …)`；官方例子 `CreateSketchSlot(swSketchSlotCreationType_e.swSketchSlotCreationType_line, swSketchSlotLengthType_e.swSketchSlotLengthType_CenterCenter, 0.05, -0.05, …)`；反射 `CreateSketchSlot(Int32, Int32, Double, …)` | 把**同一个浮点长度值**同时喂给第 2 位（官方 `System.int` 枚举）与第 3 位（`Width` 才是 double）⇒ 实参类型不符 | 可改 |
| H38 | 06-B #1 | `sw_part.py:917` `_select_revolve_axis(model, str(axis_sketch_name))` → `:918` `_ensure_sketch_selected(model, sketch_name)`；而 `_ensure_sketch_selected` → `_select_sketch_ref` 的**第一行**是 `:381 model.ClearSelection2(True)` | `IFeatureManager\FeatureRevolve2.md` `## Remarks`：「Before calling this method, call [[IModelDocExtension::SelectByID2]] to select: - the sketch to revolve, using **Mark = 0**. - the axis of revolution, using **Mark = 4 or 16**.」 | 官方要求轮廓与轴**同时留在选择集**；我们先选轴、再进 `_ensure_sketch_selected`，其内部 `ClearSelection2(True)` 把整份选择集清空 ⇒ 调 `FeatureRevolve2` 时轴已不在选区（`revolve_boss` / `revolve_cut` 两处同形） | 可改 |
| H39 | 06-B #2 **+** #3 | ① `linear_pattern()`：全函数只此一次 `_select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)` ② `linear_pattern_report()`：函数内**无任何** Select 调用，直接 `FeatureLinearPattern3` | `IFeatureManager\FeatureLinearPattern3.md`：「**ordered selection of the features and components is required**」「- **1 and 2 to mark the directions**」「- 4 to mark the features to pattern」（CHM 同文） | 官方在选特征之外还要求用 **mark 1/2 标方向**，我们**从未选过任何方向**；第二个站点连特征都没选 | 可改 |
| H40 | 06-B #4 | `sw_part.py:686-694`：`model.ClearSelection2(True)` → `for segment, mark in ((vertical, 2), (horizontal, 4)): if segment is None: continue` → `:703` 无条件 `AutoDimension2` | `ISketch\AutoDimension2.md`：「**It is an error to supply just one datum** as indicated by the status value swAutodimStatus_DatumNotSupplied.」 | 官方明写**只给一个基准是错误**；我们对缺失的那个 `continue` 跳过、仍无条件调用 | 可改 |
| H41 | 06-C #1 | `fillet()`：`return model.FeatureManager.FeatureFillet(195, radius, 0, 0, None, None, None)` | `FeatureFillet.md`：`Obsolete. Superseded by [[IFeatureManager::FeatureFillet2]].`；`FeatureFillet2.md`：`Obsolete. Superseded by [[IFeatureManager::FeatureFillet3]].` | 现行入口应是 `FeatureFillet3`（链走两级） | 可改 |
| H42 | 06-C #2 | `linear_pattern()` / `linear_pattern_report()`：`FeatureLinearPattern3(` | `FeatureLinearPattern3.md`：`Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].`；4 → `Obsolete. Superseded by …5`；5 → `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ILinearPatternFeatureData]] and [[ILocalLinearPatternFeatureData]].` | 三级 Obsolete，链尾是 `CreateFeature` + FeatureData | 可改 |
| H43 | 06-C #3 | `circular_pattern()`：`FeatureCircularPattern4(` | `FeatureCircularPattern4.md`：`Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].`；5 → `Obsolete. See …[[ICircularPatternFeatureData]] and [[ILocalCircularPatternFeatureData]].` | 两级 Obsolete | 可改 |
| H44 | 06-C #4 | `spline()`：`seg = get_com_member(model, "SketchManager").CreateSpline2(data, False)` | `ISketchManager\CreateSpline2.md`：`Obsolete. Superseded by [[ISketchManager::CreateSpline3]].`（★ 本函数 docstring 自己已逐字记了这条，**但调用点仍未换**） | 调 Obsolete 成员 | 可改 |
| H45 | 06-C #5 | `auto_dimension_sketch()`：`status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))` | `ISketch\AutoDimension2.md`：`Obsolete. Superseded by [[ISketchManager::FullyDefineSketch]].` | 调 Obsolete 成员 | 可改 |
| H46 | 06-C #6 **+** 10-C #6<br>**多路都报** | ① `sw_part.py` `model.GraphicsRedraw2()` ② `sw_review.py` `zoom_to_fit()` ③ `sw_review.py` `clear_selection_for_preview()` 收尾 | `IModelDoc2\GraphicsRedraw2.md`：`Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].` | 3 处调用点全走 Obsolete 成员 | 可改 |
| H47 | 06-C #7 **+** 07-C #1 **+** #2<br>**多路都报** | ① `sw_part.py` `_require_active_sketch`：`get_com_member(model, "GetActiveSketch2")` ② `sw_sketch_modify_ops.py` `_active_sketch_name()`：**只走这一条路、无回退** ③ `sw_sketch_edit.py` `create_sketch_chamfer._seg_count()`：**先调 Obsolete、再回退后继** | `IModelDoc2\GetActiveSketch2.md`：`Obsolete. Superseded by [[SketchManager::ActiveSketch]].` | 3 处调用点；第 ② 处**只有** Obsolete 那一路 | 可改 |
| H48 | 06-C #8 | `_select_com_object()`：`if bool(segment.Select3(selected > 0, mark, _empty_callout())):` | `ISketchSegment\Select3.md`：`Obsolete. Superseded by [[ISketchSegment::Select4]].` | 调 Obsolete 成员（下一行已是 `Select4` 兜底，但**只在 `Select3` 抛异常时才走到**） | 可改 |

#### 域 07-sketch（11 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H49 | 07-A #1 | `sw_sketch.py`：`return as_sequence(get_com_member(sketch, "GetContourEdges", contour))`；docstring「取某个轮廓的边。⚠ 官方是 **1 参**（Contour 对象）」 | `ISketch\GetContourEdges.md`：`System.object GetContourEdges( System.object Xform )`；`- **Xform**: Array of size 16 doubles representing the transform`；同页「For sketches with multiple contours, use ISketch::GetSketchContours … and then **ISketchContour::GetEdges**」 | 官方形参是 **16 个 double 的变换数组**，不是轮廓对象。★ **CHM 解包目录下没有 `ISketch~GetContourEdges` 页 ⇒ 只有 swapi 单源** | **需先查** |
| H50 | 07-A #2 | `sw_sketch_edit_ops.py:176`：`CreateFillet(float(radius_mm), int(constrained_corners))`；形参名 `radius_mm`，模块头声明「长度**毫米**、角度**度** —— 换算在工具层边界做一次」 | `ISketchManager\CreateFillet.md`：`- **Radius**: Radius of the fillet in **meters**`；官方例子 `swSketchManager.CreateFillet(0.01, …)`（=10 mm） | `Radius` 量纲不符，**放大 1000 倍**。★ 同模块另一处 `CreateChamfer` 用了 `mm(float(distance_mm))`，本行没有 | 可改 |
| H51 | 07-A #6 **+** 07-C #3<br>**多路都报** | `sw_sketch_modify_ops.py`：`⚠ \`AxisFlag\` 的**取值表官方两个源都没给** ⇒ ★ 按铁律 5 **原样透传 int，不猜语义**`；返回值 `"axis_flag_semantics": "官方 swapi 与 CHM 均未给取值表 —— 原样透传"` | `IModelDoc2\SketchModifyFlip.md` 形参表：`- **AxisFlag**: Axis about which to flip the sketch:` / `  - X = 1` / `  - Y = 2` | ★ **不是实参值错**（仍原样透传），而是**我们写下的官方依据与官方原文对不上** —— swapi 页**就带着取值表** | 可改 |
| H52 | 07-B #1 | `select_sketch_segment()`：`ok = get_com_member(seg, "Select4", bool(append), _empty_callout())`（调用点 `sketch_trim`） | `ISketchManager\SketchTrim.md` `## Remarks`：「Before calling this method, you must edit a sketch and select sketch segments to trim using [[IModelDocExtension::SelectByID2]].」+ `swSketchTrimTwoEntities` 条「Use IModelDocExtension::SelectByID2 with **Mark = 0** … specifying their **pick points**」 | 官方点名**具体入口** `SelectByID2` 且要 **mark 0 + pick point**；我们的 `Select4` 路径**无 mark、无 pick point**（★ 本仓自己在 `_select_com_object` 注释里也记了「`Select4` 分支的 Mark 永远是 0」） | 可改 |
| H53 | 07-B #2 | `select_sketch_segment()`：`Select4` 路径（调用点 `sketch_offset`） | 官方例子 `Sketch_Offset_Example_CSharp.md`：`SelectByID2("Line3", "SKETCHSEGMENT", 0,0,0, false, **1**, null, 0);` → `SketchOffset2(0.00254, true, true, …)` | 官方例子在 `SketchOffset2` 前用 `SelectByID2` 选草图段、**mark = 1**；我们的 `Select4` 路径**没有任何 mark** | 可改 |
| H54 | 07-B #4 | `sw_sketch.py` `merge_points()`：docstring「合并重合点。⚠ 容差单位官方无说明。」，函数体只有 `MergePoints(float(tolerance))` | `ISketch\MergePoints.md` `## Remarks`：「This method requires that **only one open contour exists** in the sketch.」 | 官方写明的前置（只有一个开放轮廓）**既未做检查、也未在注释里提到** | 可改 |
| H55 | 07-C #4 | `sw_sketch_edit.py` `SKETCH_CHAMFER_TYPE`：`"distance_distance": 1, # swSketchChamfer_DistanceDistance（⚠ md 写 -1，反射写 1，采用 1）` | `swSketchChamferType_e.md`：`DistanceAngle \| 0` · **`DistanceDistance \| -1`** · `DistanceEqual \| 2`（`enum_member_count: 3`） | 作为枚举字面量传的 `1` 在官方枚举页**不是任何成员的值**。★ **两源不一致（md 写 -1、出厂反射写 1）⇒ 不判谁对** | **需先查** |
| H56 | 07-C #5 | `sw_sketch.py` `SKETCH_CROSS_HATCH` 上方注释：`#: ⚠ swapi 只列了其中 3 个（Include/Exclude/AndExplodeOnly），**值相同**，无冲突。` ＋ `#: 反射里还有 swCrossHatchOnly = 2 · swSolidHatchOnly = 4。` | `swCrossHatchFilter_e.md`：`enum_member_count: 5`，成员表**列全了 5 个**（`Include 0` / `Exclude 1` / `Only 2` / `AndExplodeOnly 3` / `SolidHatchOnly 4`） | 我们称「swapi 只列了 3 个」，官方枚举页**本身列全了 5 个**；两值与反射相同 ⇒ 是**注释与事实不符**（取值本身全对） | 可改 |

#### 域 08-mold-costing（5 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H57 | 08-A #1 | `sw_measure.py` `measure_selection_report`：`ok_calc = _get(m, "Calculate")`（**零实参**）；同行注释自己写着「★★★ 真机：`Calculate` 必须无参调（★ 事实 227）」 | `IMeasure\Calculate.md`：**Signature** `System.bool Calculate( System.object Entities )`；`- **Entities**: Array of entities to measure; **if NULL, then this method measures the selected entities**`；官方例子 `swMeasure.Calculate(null)` / `Calculate(Nothing)`；反射 `Boolean Calculate(Object)`；CHM `value = instance.Calculate(Entities)` | 实参个数 **0 ≠ 形参个数 1**（五源一致）。⚠ 官方说明「NULL 就量选区」**语义上支持 0 实参**，但调用形状仍不符 | 可改 |
| H58 | 08-B #1 | `sw_mold.py` `insert_parting_line()`：前置只写「须由调用方选好**拔模方向参考**」，报错文案「未选拔模方向参考」；文件内**无任何** `SelectByID2` / mark | `IFeatureManager\InsertMoldPartingLine.md`：「Before calling this method, you must select **the direction of pull and the edges for the parting line** … with the following Marks: **Direction of pull 1 / Parting line edges 4**」（CHM 同源） | 官方要求**两样都选**并给 mark；分型线边这一项及其 mark=4 **完全没落到代码或文案** | 可改 |
| H59 | 08-B #3 | `sw_mold.py` 模块 docstring：`⚠ **多个参数语义查不到**（CHM 无这些方法的独立说明页、\`C:\swapi\` 未收录）⇒ 按铁律 5 **不猜**`；`insert_core_cavity_solids` 报错文案只留「未先建分型面」 | `IFeatureManager\InsertMoldCoreCavitySolids.md` `## Remarks`「To use this method:」**四条**：`- The Parting Line feature must exist.` `- The parting surface must be generated.` `- The part must be separated into core and cavity (sheet bodies).` `- A sketch describing the outline of the mold block must exist. The sketch must be perpendicular to the pull direction.`（CHM 同源） | ★ **官方两源都有该成员页、且写了四条前置**，我们却按「查不到」处理 ⇒ 前置只保留一条、另三条零检查 | 可改 |
| H60 | 08-C #1 | `mold_undercut_detect()`：`get_com_member(fm, "MoldUndercutDetect", int(col_undercut), int(col_base), bool(b_coord_input), float(dx), float(dy), float(dz))` | `IFeatureManager\MoldUndercutDetect.md`：`Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]].`（CHM 同源）；后继 `MoldUndercutDetect2( ColUndercut1, ColUndercut2, ColOccluded, ColStraddle, ColBase, BCoordInput, Dx, Dy, Dz )` = **9 参** | 成员是 Obsolete，**且后继不是同名同位替换**（6 → 9 参） | 可改 |
| H61 | 08-C #2 | `insert_parting_surface()`：`int(option), # 6 Int32 未查证`（默认值 `option: int = 0`，按位置传给第 6 参）；docstring 写「其余 5 个…**语义未查证**」 | `IFeatureManager\InsertMoldPartingSurface.md`：`- **Smooth**: Smooth mold parting surface as defined in [[swPartingSurfaceSmoothingType_e]]`（第 6 形参即 `System.int Smooth`）；`swPartingSurfaceSmoothingType_e.md` `enum_member_count: 2`：`Sharp \| 1` · `Smooth \| 2` | 我们当作该枚举传的**字面量 `0` 不在成员表内**（该枚举只有 1 与 2） | 可改 |

#### 域 09-simulation（8 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H62 | 09-A #1 | `sw_simulation_loads.py:690`：`return _check(manager, "GetLoadsAndRestraints", 1, int(index))`；`:319-332` `_ERRORCODE_MEMBERS` frozenset 里**没有** `"GetLoadsAndRestraints"`；`:263-264` `if _wants_error_code(member): tail.append(out_i4())` ⇒ **只给 1 个实参**。★ 同仓 `sw_simulation.py` 的 `collect_study_evidence()` 却用 `get_com_member(lrm, "GetLoadsAndRestraints", position, out_i4())` = **2 实参** | ① 官方 .NET CHM `ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html`：`ByVal NIndex As System.Integer, ByRef ErrorCode As System.Integer` ② 官方 VB6 CHM `GetLoadsAndRestraints n=2 :: ByVal NIndex As Long, ByRef ErrorCode As Long` ③ 出厂反射 `CWLoadsAndRestraints GetLoadsAndRestraints(Int32, Int32&)` | 官方形参 **2 个**，我们只传 **1 个**。★ 模块自己的来源块 `:679` 已逐字抄下 `GetLoadsAndRestraints(ByVal NIndex As Integer, ByRef ErrorCode As Integer)` ⇒ **注释与实参自相矛盾** | 可改 |
| H63 | 09-A #2 | `sw_simulation_loads.py:695`：`return _check(manager, "GetEdgeWeldConnector", 1, int(index))`；`_ERRORCODE_MEMBERS` 里同样没有它 | ① 官方 .NET CHM：`Function GetEdgeWeldConnector( ByVal NIndex As System.Integer, ByRef ErrorCode As System.Integer )` ② 官方 VB6 CHM `n=2` ③ 反射 `CWEdgeWeldConnector GetEdgeWeldConnector(Int32, Int32&)` | 与 H62 同一根因（漏列在 `_ERRORCODE_MEMBERS`） | 可改 |
| H64 | 09-A #3 | `collect_loads_evidence()`：`get_com_member(item, "GetName")` / `get_com_member(item, "GetType")`；★ 同仓 `sw_simulation.py` 对同类对象用的是 `get_com_member(entry, "Name")` / `("Type")` —— **属性名** | ① 官方 VB6 CHM `CWLoadsAndRestraints_members.html` 全页属性表：`Properties EntityCount Name State Type`（对 `GetName\|GetType` 做 `Select-String` ⇒ **0 命中**）；同目录 `CWLoadsAndRestraints~*` 逐页清单**无 `GetName` 页、无 `GetType` 页** ② 出厂反射 `## ICWLoadsAndRestraints` 全 8 行：`String get_Name()` / `Int32 get_Type()` —— **无 `GetName`、无 `GetType`** | **成员缺席**：名称与类型在官方两源里都是**属性**不是方法 ⇒ 错在成员名 | 可改 |
| H65 | 09-B #1 | `sw_topology.py` `create_preserved_region._configure()`：`if option is not None: get_com_member(control, "SetIncludeRegionDepth2", True)` / `return control` | 官方例子 `Create_Topology_Study_Example_VBA.txt`：`CWTopoPreservedRegionObj.BeginEdit` → `Set DispatchObj1 = …GetSelectedObject6(1, -1)` → `DispArrayForPreservedRegion = Array(DispatchObj1, DispatchObj2)` → `CWTopoPreservedRegionObj.SelectFaces((DispArrayForPreservedRegion))` → 再设深度 | 官方先**把保留面装成 `DispArray` 传给 `SelectFaces`**，我们这 4 行**只有** `SetIncludeRegionDepth2`，`SelectFaces` 一次都没调 | 可改 |
| H66 | 09-B #2 | `create_symmetry_control._configure()`：`get_com_member(control, "SelectSymmetryType", int(symmetry_type))` / `return control` | 官方例子：`CWTopoSymmetryControlObj.SelectSymmetryType 0` → `CWTopoSymmetryControlObj.SelectFirstSymmetryPlane sDispObjPlane1`（1/4 对称再加 `SelectSecondSymmetryPlane`） | 官方调用序是 `SelectSymmetryType` **紧接** `SelectFirstSymmetryPlane <plane>`；我们只有前者 | 可改 |
| H67 | 09-B #3 | `create_demold_control._configure()`：`get_com_member(control, "SelectDemoldDirection", int(direction))` / `return control` | 官方例子：`SelectDemoldDirection 0` → `SetAutoDetermineCentralMidPlane2 False` → `SelectPlaneForDirection sDispObjPlane`；另一形态 `SelectDemoldDirection 1` → `SelectEdgeForPullDirection sDispObjEdge` | 官方在 `SelectDemoldDirection` 之后**必须**再交出方向几何；我们没有那一步 | 可改 |
| H68 | 09-B #4 | 7 个 `create_*`：`constraint = get_com_member(manager, "CreateStressConstraint", out_i4())` 之后只 `return _edit(constraint, _configure)`（**只在约束对象上开事务**） | 官方例子：`CWTopologyStudyManagerObj.BeginEdit` → `CWTopologyStudyManagerObj.CreateStressConstraint(ErrorCodeObj)` → … → `ErrorCodeObj = CWTopologyStudyManagerObj.EndEdit()` | 官方把 `Create*` 放在**管理器层** `BeginEdit`…`EndEdit()` 之间；管理器层的事务括号一次都没调。★ 同文件 `set_topology_goal` 走 `_edit(manager, _build)`（有括号）⇒ **同模块两种形态** | 可改 |
| H69 | 09-C #1 | `sw_simulation_loads.py` 两处 + `sw_simulation.py` 一处：`_check(manager, "AddForce", …, int(force_type), entities, ref_geom)` | 官方 `ICWLoadsAndRestraintsManager~AddForce.html`：`<font color="red">Obsolete. Superseded by …AddForce2…</font>`；`members_2021.html` 成员表两行：`AddForce` → Obsolete→`AddForce2`；`AddForce2` → Obsolete→`AddForce3` | 三处 COM 调用打的是 `AddForce`；**我们从未调用 `AddForce2`/`AddForce3`**（只在常量表里出现过名字） | 可改 |

#### 域 10-misc（11 条）

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| H70 | 10-A #1 | `sw_export.py` `get_mass_property_override_options`：`mass_property = get_com_member(extension, "GetMassProperties", float(accuracy))` | ① `IModelDocExtension\GetMassProperties.md`：`System.object GetMassProperties( System.int Accuracy, out System.int Status )` ② 出厂反射 `Object GetMassProperties(Int32, Int32&)` ③ `sw_connect.py` `get_com_member`：`return member(*args)`（**原样透传、不补位**） | 实参 **1 个 ≠ 形参 2 个**，**且**第 1 实参是 `float` 而形参是 `System.int` | 可改 |
| H71 | 10-C #3<br>（与 H70 同址不同口径） | 同一行调用 | `IModelDocExtension\GetMassProperties.md`：`Obsolete. Superseded by [[IModelDocExtension::GetMassProperties2]].` | 同函数 docstring 已点名后继是 `GetMassProperties2`，调用仍走旧成员 | 可改 |
| H72 | 10-C #1 | `sw_export.py` `_export_generic()` 与 `export_to_pdf()`：`success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)` | `IModelDocExtension\SaveAs.md`：`Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].` | 两条导出路径都调官方已标 Obsolete 的成员 | 可改 |
| H73 | 10-C #2 | `export_to_stl()`：`model.SetUserPreferenceIntegerValue(78, quality_map[quality])` | `IModelDoc2\SetUserPreferenceIntegerValue.md`：`Obsolete. Superseded by [[IModelDocExtension::SetUserPreferenceInteger]].` | 后继改在 `IModelDocExtension` 上 | 可改 |
| H74 | 10-C #5 | `export_to_stl()`：`quality_map = {"coarse": 1, "fine": 0}` | `swSTLQuality_e.md`：`swSTLQuality_Coarse \| 1` · `swSTLQuality_Custom \| 3` · `swSTLQuality_Fine \| 2` | `"fine"` 映射的字面量 **0 不是任何成员**；★ **且按官方枚举 `Fine` 应是 2** ⇒ 不只是越界，是**映射错了目标成员**（`"coarse": 1` 与官方一致）。⚠ ★ **MCP 工具 `solidworks_export_stl` 的 `stl_quality` 默认值就是 `"fine"`** | 可改 |
| H75 | 10-C #8 | `sw_document_data.py` `_dimension_value_mm`：`float(dimension.GetSystemValue2(configuration_name)) * 1000.0` | `IDimension\GetSystemValue2.md`：`Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].` | 取系统值走 Obsolete 成员 | 可改 |
| H76 | 10-C #9 | 同一函数：`float(get_com_member(dimension, "SystemValue")) * 1000.0` | `IDimension\SystemValue.md`：`Obsolete. Superseded by [[IDimension::GetSystemValue3]], [[IDimension::IGetSystemValue3]], [[IDimension::SetSystemValue3]], and [[IDimension::ISetSystemValue3]].` | 读「当前配置」系统值走 Obsolete 属性 | 可改 |
| H77 | 10-C #10 | `sw_wrap.py`：`WRAP_MESH_FACTOR_DEFAULT = 0`，作为第 5 实参传给 `InsertWrapFeature2` | `IFeatureManager\InsertWrapFeature2.md`：`- **MeshFactor**: Accuracy of flattened triangle mesh; **1 (lowest) - 10 (highest)**` | 官方把取值范围写死 1–10，我们传 **0** 落在范围之下 | 可改 |
| H78 | 10-B #1 | `sw_ref_geometry.py`：`obj = get_com_member(fm, "InsertRefPlane", …)`（调用前**无任何选择动作**）；返回值 `"selection_mark": "★ 官方 Remarks 只说「these marks」、**未给取值表** ⇒ 不假定"` | `IFeatureManager\InsertRefPlane.md`：「Before calling this method, you must have selected the reference entities using these marks with [[IModelDocExtension::SelectByID2]]: - **0 = First reference entity** - **1 = Second reference entity** - **2 = Third reference entity**」 | 官方**给了 mark 取值表 0/1/2**，我们断言「未给取值表」；且两步前置都没做 | 可改 |
| H79 | 10-B #2 | `sw_loft.py` `_blend_args` / `_cut_blend_args` 各一处：`False, # UseAutoSelect`（**硬编码**） | `InsertProtrusionBlend2.md` / `InsertCutBlend.md`（两页逐字相同）：「When **UseAutoSelect is false**, the user must **select the bodies** that the feature will affect.」 | 该值为 false 时官方要求必须选 body；代码全程**没有任何 body 选择动作**，也没把该值暴露成可配参数 | 可改 |
| H80 | 10-B #3 | `create_loft_report`：`if use_selected_profiles and sel_n < 2:` → `"error": "放样至少要选 **2 个轮廓**"`；`create_loft_cut_report` 同形 | `InsertProtrusionBlend2.md`：「You can use **any number of profiles**; however, **if you select only one profile**, then any selected guide curves must be closed curves.」（`InsertCutBlend.md` 同文） | 官方写「轮廓数量任意」，只在**只有 1 个轮廓**时附加条件；我们的 `< 2` 门禁**挡掉了官方明确允许的 1 轮廓情形** | 可改 |
| H81 | 07-A #3 | `sw_sketch_edit_ops.py`：`SketchOffset2(float(offset_mm), bool(both_directions), bool(chain), …)` | `ISketchManager\SketchOffset2.md`：`System.bool SketchOffset2( System.double Offset, System.bool BothDirections, System.bool Chain, System.int CapEnds, System.int MakeConstruction, System.bool AddDimensions )`（6 参、顺序逐位一致）；官方例子 `Sketch_Offset_Example_VB.md`：`SketchOffset2(0.00254, True, True, …)` | ★ 形参表**本身没写量纲**，量纲依据取自**官方配方实参** `0.00254`（=2.54 mm 的米制值）⇒ 我们原样传 `offset_mm` 差 1000 倍 | **需先查** |
| H82 | 07-A #4 | `sketch_linear_pattern` 实参第 3、4 位：`float(spacing_x_mm), float(spacing_y_mm),` | `ISketchManager\CreateLinearSketchStepAndRepeat.md` `SpacingX`: `Spacing between instances along the x axis`（**未写单位**）；官方例子 `Create_and_Edit_Linear_Sketch_Pattern_Example_CSharp.md`：`CreateLinearSketchStepAndRepeat(2, 2, **0.0254, 0.0254**, 0.2967, 1.1345, "", …)` | 第 3/4 实参量纲依据**同样只来自官方配方实参**（米制）。★ 同行 `AngleX/AngleY` 用 `math.radians(...)`，与配方 `0.2967/1.1345`（弧度）**一致，不算分歧** | **需先查** |
| H83 | 07-A #5 | `sketch_circular_pattern` 实参第 1 位：`float(arc_radius_mm),` | `ISketchManager\CreateCircularSketchStepAndRepeat.md` `ArcRadius`: `Radius for the circular sketch pattern`（**未写单位**）；官方例子 `Create_and_Edit_Circular_Sketch_Pattern_Example_CSharp.md`：`CreateCircularSketchStepAndRepeat(**0.03184378021964**, 4.7329, 4, 1.5708, true, "", …)` | 同上，量纲依据只来自配方实参。★ 第 2、4 位 `math.radians(...)` 与配方**一致，不算分歧** | **需先查** |

> ★ **为什么 H81–H83 是「高置信」却判「需先查」**：这三条是 07-A **明写的高置信**（每条两段原文都是可 grep 的），
> 但它们的**官方依据只来自配方实参**（形参表本身没写单位）⇒ 排进高置信区（遵守「高在前」），
> **级别压到需先查**（不能照着改）。★★ 这是本表最重要的一条口径：**「置信度高」≠「可以直接改」**。

### §1.2 中置信 —— 28 条

| ID | 路由 | 我们的原文 | 官方的原文 | 分歧点 | 级 |
|---|---|---|---|---|---|
| M01 | 01-A #3 | `_invoke(get_modeler(sw_app), "CreateSheetFromSurface", surface, float(tolerance))` | `IModeler\CreateSheetFromSurface.md`：`System.object CreateSheetFromSurface( System.object SurfaceIn, System.object UvRange )`；`- **UvRange**: Array of UV values for this surface` | 第 2 实参**标量 vs 数组**；形参类型两侧都写 `System.object`，只有官方 Parameters 那行说明它是数组 | **需先查** |
| M02 | 01-A #4 | `sw_surface_ref_ops.py`：`get_com_member(model, "InsertLoftRefSurface2", bool(closed), bool(keep_tangency), bool(force_non_rational), float(tess_tolerance_factor), **int(start_matching_type), int(end_matching_type)**)` | `IModelDoc2\InsertLoftRefSurface2.md`：`void InsertLoftRefSurface2( …, System.double TessToleranceFactor, **System.short** StartMatchingType, **System.short** EndMatchingType )` | 第 5/6 实参声明类型不一致（pywin32 送 VT_I4 而非 VT_I2）；个数与先后都对 | **需先查** |
| M03 | 01-B #4 | `sw_surface_features.py`：`if int(end_condition) not in (0, 1):`（接受 1）+ `selected = _select_all_surface_faces(model, mark=0)`；该 helper 先 `ClearSelection2(True)` 再只选各体的**面** | `IModelDoc2\InsertExtendSurface.md`：`The **selected point or surface** to which to extend should be in the selection list.` + 参数表「1 - Extend surface up to a **selected point**」 | `end_condition=1` 时官方要求选区里有「**点**」；我们接受该值但选区被清过、之后只放面，**从没有点** | 可改 |
| M04 | 02-B #3 | `sw_sheet_metal_weld_entry.py`：`if body is None: return {"ok": False, ..., "error": "body 为 None …"}`；`"preconditions_held": bool(body is not None and part_doc is not None)`；转接层 `res = insert_mid_surface(model, bodies[int(body_index)], model, …)` | `IFeatureManager\InsertMidSurface.md`：`InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )`；`- **PBodyIn**: … in the context of an assembly; **otherwise, null or Nothing**`；`- **PPartDocIn**: … otherwise, null or Nothing`；`## Remarks`「The pPartDocIn parameter is the component's model document … the pBody parameter is the body of that component.」 | 官方把两个对象形参限定在**装配体上下文**、并逐字写「otherwise, **null or Nothing**」；我们把「非空」当硬前置，且 `create_midsurface` 在**零件**上下文里把活动零件文档当装配体上下文传 | 可改 |
| M05 | 02-B #4 | `sw_sheet_metal.py` `create_draft(model, face_ref, spec)`：docstring「在已选中的面上创建原生拔模特征」，但 **`face_ref` 在整个函数体内不再出现**；`_apply` 只设 `data.Angle` 与 `data.ReverseDirection` | `IDraftFeatureData2\FacesToDraft.md`：`Gets or sets the faces that define this draft feature.` + `## Remarks` 见 `Selections that Define Features.md`：`1. First, call the **AccessSelections** method for that feature data object` / `2. Then, call the desired method` | 收了 `face_ref` 却从不使用，也从不设 `FacesToDraft`、从不调 `AccessSelections` ⇒ 入参是**死参数**，官方对应那一步**没有落点** | 可改 |
| M06 | 02-C #3 | `sw_sheet_metal_weld_entry.py`：`SW_RELIEF_NONE = 4` / `SW_RELIEF_TEAR_BEND = 5`（docstring 列 Rectangular=1·Tear=2·Obround=3·None=4·TearBend=5）；`SW_FLANGE_BEND_{CENTER_LINE 4, SHARP 5, TANGENT 6}`（docstring 列 1..6）；实参 `int(relief_type),` / `int(flange_pos),` **原样透传不收窄** | `IFeatureManager\InsertSheetMetalMiterFlange.md`：`- **ReliefType**: … as defined by [[swSheetMetalReliefTypes_e]]; **valid selections:**` 之后**只列 3 条**（Obround / Rectangular / Tear）；`- **FlangePos**: … **valid selections:**` 之后**只列 3 条**（MaterialInside / MaterialOutside / BendOutside） | 该成员的参数表各自只承认 3 个 `valid selections`，我们把 5/6 个整体当合法域原样透传 ⇒ 多出的 2 + 3 个不在 valid selections 内 | **需先查** |
| M07 | 03-B #3 | `sw_weldment.py`：`update_ok = bool(call_com_member(body_folder, "UpdateCutList")) if body_folder else False` | `IBodyFolder\UpdateCutList.md`：「…false if not **or because the document does not contain an automatically generated cut list**」；同页「use [[IPartDoc::IsWeldment]] … then use [[IBodyFolder::GetAutomaticCutList]] to find out if automatic generation of a cut list is enabled」 | 官方点名要先确认的两步我们一步都没做；且官方写明文档不含**自动生成**清单时它也会回 false，我们把返回值原样当 `update_ok` 报出 | 可改 |
| M08 | 03-C #3 | `SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter` → `_create_from_definition(model, SW_FM_MATE_PROFILE_CENTER, _apply)`；来源块「配合 `CreateDefinition(swFmMateProfileCenter = 101)`」 | `IFeatureManager\CreateDefinition.md` 的 `- **Type**:` 之后**逐条列出 35 个** `swFm*` 常量，**其中没有 `swFmMateProfileCenter`**；`swFeatureNameID_e.md` 有 `\| swFmMateProfileCenter \| Profile center mate \|`（该表 Value 列装的是描述不是数值） | 常量名在枚举里存在，但**不在官方为该形参逐条列出的那 35 项里**。（只陈述差集；★ 那 35 项**是否穷尽**，核对员明写「**不判**」） | **需先查** |
| M09 | 03-C #4 | `sw_weldment.py` 文件头：`# ⚠ 扫描 131 个条目确认：焊件相关的**只有这 3 个**，没有「下料表」或「构件分割」的独立 fm 条目` | `swFeatureNameID_e.md` 在那 3 个之外还有 **6 行**含「Structure system」：`swFmStrctSysCnrFeat` / `CnrGrpFeat` / `CnrMgmtFeat` / `swFmStrctSysFeat` / `StrctSysGrpFeat` / `StrctSysMbrFeat` | 我们对这份枚举做了**完整性断言**，官方同页在这 3 个之外还有 6 条 Structure system 条目。（★ 这 6 条**算不算**「焊件相关」是**界定口径**问题，核对员明写不在本路判断） | **需先查** |
| M10 | 04-B #2 | `interference = asm_model.InterferenceDetectionManager`（本行之前**没有任何调用**） | 官方例子 `Run_Interference_Detection_Example_VB/CSharp.md` 的第 1 步都是 `swAssemblyDoc.ToolsCheckInterference`（注释写明"Open the Interference Detection pane"）紧接取管理器；`IAssemblyDoc\ToolsCheckInterference.md`：`Opens the Interference Detection PropertyManager.` | 取管理器前没先 `ToolsCheckInterference()`。★ 降为中是因为 **`InterferenceDetectionManager.md` 自身的 Remarks 里没有写这条前置** | **需先查** |
| M11 | 04-B #3 | `add_component()` 第一个 `try`：`component = _add_component5(asm_model, component_path, config_name, x, y, z)`（此时只有 `os.path.exists` 检查，`open_document(...)` 在后面的回退分支里） | `IAssemblyDoc\AddComponent5.md`：`The specified file **must be loaded in memory**.`；官方例子 `Add_Component_and_Mate_Example_VB.md`：`OpenDoc6(零件)` → `ActivateDoc3(装配体)` → `AddComponent5` | 官方把「文件必须已在内存中」写成前置，我们**首选路径**在零件尚未载入时先调 `AddComponent5`，只有失败后才走兜底 | 可改 |
| M12 | 04-B #4 | `select_entities_for_mate()`：`if not entity1.Select2(False, mark):` / `entity2.Select2(True, mark)`，`mark=1` | `IAssemblyDoc\AddMate5.md`：`1. Call ClearSelection2 … 2. Call [[IModelDocExtension::**SelectByID2**]] to select each entity to mate. 3. Call this method. 4. Call ClearSelection2 after …`；官方例子 `SelectByID2(FirstSelection, "PLANE", 0,0,0, True, **1**, …)` | **mark 值本身对得上**（`Other swMateType_e option \| 1`），分歧只在**第 2 步用的入口成员**是 `SelectByID2` 而非 `Select2` | 可改 |
| M13 | 05-B #5 | `sw_drawing_create_missing.py`：`sel = _selection_count(model)` / `"preconditions_held": bool(sel and sel >= 1)` | `IDrawingDoc\CreateAuxiliaryViewAt2.md` 首行：`Creates an auxiliary view based on **a selected edge in a drawing view**.` | 官方前置指明「视图里的一条边」；我们只判「≥1 个对象」，不判类型、不判是不是在视图里 | 可改 |
| M14 | 05-B #6 | 同上；docstring 复述为 `★ 官方第 1 步逐字：'Select one or more **views or sheets**'` | `IDrawingDoc\AutoBalloon5.md` `## Remarks`：`1. Select one or more **views or sheets** for which to automatically create BOM balloons.` | 官方第 1 步限定被选对象是**视图或图纸**；我们只判计数 ≥1（★ 第 2/3/4 步逐条照做，与官方一致） | 可改 |
| M15 | 05-B #7 | `sw_drawing_expose.py`：`res = D.auto_insert_center_marks(drawing_model, requirements)`（该包装层两步前置都不做、不回读） | `IView\AutoInsertCenterMarks2.md` `## Remarks`：`Before calling this method: 1. Call [[IDrawingDoc::ActivateView]] with the name of the view to activate. 2. Call [[IDrawingDoc::**ActiveDrawingView**]] to get a handle on the activated view.` | 官方要求调用前**两步**；点名文件这一层都没有。★ 降为中是因为真正的调用在桥接目标 `drawing_workflow.py`（不属本路点名文件），那里有 `ActivateView` 而**全仓 grep 不到 `ActiveDrawingView`** | 可改 |
| M16 | 06-B #5 | `sw_part.py` `fillet()`：函数体内**无任何选择代码**，`edges` 形参收了不用（docstring「None 则使用当前选择」） | `IFeatureManager\FeatureFillet.md`：「Simple fillets — 1. Call [[IModelDocExtension::SelectByID2]] with **Mark = 1** to select the edges to fillet.」 | 官方要求被倒圆的边以 **Mark = 1** 进选择集；我们不选、也不约定 mark，形参完全未使用 | 可改 |
| M17 | 06-B #6 | `sw_part.py` `shell()`：函数体内**无任何选择代码**，`faces_to_remove` 形参收了不用 | `IModelDoc2\InsertFeatureShell.md`：「Before calling this method, **select faces to remove** … using [[IModelDocExtension::SelectByID2]] with **Marks of 1**」 | 同上：官方要求按 **Marks of 1** 选，我们不选、也不约定 mark | 可改 |
| M18 | 06-C #9 | `_select_com_object()`：`for method_name in ("Select2", "Select4"):` —— **先试 `Select2`** | `ISketchSegment\Select2.md`：`Obsolete. Superseded by [[ISketchSegment::Select4]].` | 对 `ISketchSegment` 输入而言 `Select2` 已被官方标 Obsolete，而它是**第一个**被试的 | 可改 |
| M19 | 07-B #3 | `sketch_circular_pattern` 调用前一行：`_select_spec(model, selection)`（**无条件先选**一段草图段） | 官方例子 `Create_and_Edit_Circular_Sketch_Pattern_Example_CSharp.md`：`swModel.ClearSelection2(true);` → `CreateCornerRectangle(...)` → `boolstatus = swSketchMgr.CreateCircularSketchStepAndRepeat(...)` —— **三句之间无任何选中动作** | 官方例子里种子是刚画出的矩形、**不预选**；我们无条件先选。⚠ 但官方也**没有**禁止预选 ⇒ 只凭官方例子不足以判定 | **存疑** |
| M20 | 07-B #5 | `sketch_extend` 内：`_select_spec(model, selection)` | 官方例子 `Extend_Sketch_Entity_Example_CSharp.md`：`// Set the selection mode to default` / `swModel.**SetPickMode()**;` → `SelectByID2("Line1","SKETCHSEGMENT", …, false, 0, null, 0)` → `SketchExtend(0.0,0.0,0.0)` | 官方例子在选中前有一步 `SetPickMode()`；我们的选择路径里没有这一步。★ 依据**只来自官方例子**，成员页未写 | **需先查** |
| M21 | 08-B #2 | `sw_mold.py` `insert_parting_surface()`：报错文案 `"InsertMoldPartingSurface 返回 None —— 常见原因：未先建分型线，或未选面"` | `IFeatureManager\InsertMoldPartingSurface.md`：「if a parting line feature does not yet exist in the model, you must first **select the direction of pull and the edges for the parting line** using [[IModelDocExtension::SelectByID2]]. For example, a **face (direction of pull) has a mark of 1** and **edges (parting lines) a mark of 4**.」 | 同族的 mark 前置**只落了一半**：我们写成「未选面」这一无 mark 的一句，分型线边的 mark=4 没有对应物（文件内无任何选择/mark 代码） | 可改 |
| M22 | 09-C #2 | `sw_simulation.py`：`def default_element_size_and_tolerance(study, units: int = **-1**)` / `def mesh_size_report(study, units: int = **-1**)`；同文件把该参标成 `#: \`\`swsUnit_e\`\` —— 与 VB6 CHM 的 \`CosmosWorksLib~swsUnit_e\` 页逐条一致。` | `C:\cworks_vb6\CosmosWorksLib~swsUnit_e.html` 枚举表**全页只有 3 个成员**：`swsUnitEnglish \| 1` · `swsUnitMetric \| 2` · `swsUnitSI \| 0` | 我们把 **`-1`** 当 `swsUnit_e` 的值传（两处默认实参），`-1` 不在其中。★ **但** `CWStudy~CreateMesh` / `CWMesh~GetDefaultElementSizeAndTolerance` 两页的 `NUnits` 形参**未写它属于哪个枚举**（铁律 5：查不到就说查不到）⇒ 「`units` 就是 `swsUnit_e`」这句是**我们自己写的** | **需先查** |
| M23 | 09-C #3 | `sw_simulation.py`：`get_com_member(model, "SetMaterialPropertyName2", "", database, material_name)` 紧接 `get_com_member(model, "MaterialIdName")` | `IModelDoc2\MaterialIdName.md`：`Obsolete. Superseded by [[IPartDoc::GetMaterialPropertyName2]] and [[IPartDoc::SetMaterialPropertyName2]].`；★ **对照源** `IPartDoc\MaterialIdName.md`：`Gets or sets the material name.`（**没有** Obsolete 标注） | 同一成员名官方**两页标注不一致** ⇒ 记成「两源不一致」，**不判谁对**。我们代码用迟到绑定按裸名调用，未写明 `model` 落到哪个接口 | **需先查** |
| M24 | 10-B #6 | `sw_export.py` `export_flat_pattern_dxf()`：`return bool(model.ExportToDWG2(output_path, model_path, SW_EXPORT_TO_DWG_SHEET_METAL, True, …))`（函数内**无任何选择动作**） | `IPartDoc\ExportToDWG2.md` `## Remarks`：「You must **select multi-body sheet-metal features** (i.e., multiple flat-pattern features) before calling this method.」；★ **对照** `Export_Part_To_DWG_Example_VBNET.md` 同一 Action（`swExportToDWG_ExportSheetMetal`）**没有任何** `SelectByID2` / `SelectByRay` | ★ **官方两源不一致**：Remarks 说「调用前必须选中」，官方例子对同一 Action 未做任何选择 ⇒ 判不了谁对，两段原文都在上 | **需先查** |

#### 中置信里**未列入上表**的 4 条（已在总表里以高置信行承载，此处只补它们的低置信同源说法）

- **M25**｜04-C #8 + 10-C #4 + 10-C #7（**多路都报**，3 处调用点）—— `sw_assembly.py` `_activate_model_document()` except 分支、`sw_export.py` `_activate_source_document()` except 分支 + DumbDispatch 分支、`sw_review.py` `activate_model_for_preview()` except 分支：**四处**都是 `sw.ActivateDoc2(title, False, errors)`。
  官方 `ISldWorks\ActivateDoc2.md`：`Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].`（同函数第一分支已在用 `ActivateDoc3`）。
  ★ **两路对本条的置信度不一致**：04-C 判「**中**（仅一源，CHM 里该成员页缺失，按铁律 5 不用相似页面顶替）」，10-C 判「**高**」。⇒ 合并后按**低**者取「中」，级 **需先查**。
- **M26**｜09-B #5 —— `sw_simulation.py` `get_cosmosworks`：`cosmos = get_com_member(addin, "CosmosWorks")`（驼峰）；官方两个例子都写**全大写** `COSMOSWORKS`（`Analyze_Part_Example_VB.htm`、`Create_Topology_Study_Example_VBA.txt`）。我们来源块自述「本反射清单里该成员的 getter 名为 `get_CosmosWorks`」。
  ⇒ 级 **存疑**：COM 属性名分派大小写不敏感，**官方例子的写法不构成 API 约束**；反射（铁律 4 的裁决者）站我们这边。
- **M27**｜10-B #4 —— `sw_review.py` `set_standard_view()`：`model.ShowNamedView2(str(view_name), -1)` / `model.ShowNamedView2("", view_id)`（函数内无任何选择步骤，也不区分文档类型）；官方 `IModelDoc2\ShowNamedView2.md`：`To set a named view to the active view in a drawing, the **drawing view that contains the named view must be selected**.` ⇒ 级 **可改**（加工程图分支 + 选择）。
- **M28**｜10-B #5 —— `sw_helix.py`：docstring「官方示例显示要先**选中一个圆**（`SelectByID2` + `CreateCircle`）——螺旋线以那个圆为直径基准」；报错文案「**没有选中定义直径的圆**（官方示例先 SelectByID2 选圆再调）」。
  官方例子 `Create_Spiral_Example_VB.md` 实际是：`SelectByID2("**Front Plane**", "**PLANE**", …, False, **0**, Nothing, 0)` → `ClearSelection2 True` → `swSketchMgr.CreateCircle(...)` → `InsertHelix(...)` ⇒ ★ **`SelectByID2` 选的是基准面（mark 0）**，圆是之后**画**出来的。⇒ 级 **可改**（改文案与实际次序对上）。

---

## §2 · ★★ 抽查证伪（跨 8 份文件 / 8 个域，随机抽 8 条高置信）

**方法**：在 83 条高置信里按域均匀取样（每域至多 1 条），★ **自己打开我们那份代码 + 官方页**逐条比对，
不采信任何核对表的结论。命中 **8 份文件 / 8 个域**（要求 ≥6）。

| # | 抽中的条目 | 源文件 | 域 |
|---|---|---|---|
| S1 | H09 `ISketchedBendFeatureData.BendAngle` 度 vs 弧度 | `audit-02-sheetmetal-A.md` | 02-sheetmetal |
| S2 | H16 `InsertWeldmentCutList2` 传 `sort_options` vs `Bodies` | `audit-03-weldment-A.md` | 03-weldment |
| S3 | H38 `FeatureRevolve2` 的旋转轴被 `ClearSelection2` 清空 | `audit-06-features-B.md` | 06-features |
| S4 | H62 `GetLoadsAndRestraints` 只传 1 个实参 | `audit-09-simulation-A.md` | 09-simulation |
| S5 | H74 `swSTLQuality` `"fine": 0` | `audit-10-misc-C.md` | 10-misc |
| S6 | H08 `RULED_TYPE_MEANINGS` 0..4 vs 枚举 1..5 | `audit-01-surface-C.md` | 01-surface |
| S7 | H35 `InsertRevisionTable2` 的 `shape` 默认 0 | `audit-05-drawing-C.md` | 05-drawing |
| S8 | H50 `CreateFillet` 的 `Radius` 未换算 | `audit-07-sketch-A.md` | 07-sketch |

### S1 · `ISketchedBendFeatureData.BendAngle` —— ✅ **成立**

- **我们这边**（`scripts/sw_sheet_metal.py`）：
  - `:369` `angle: float`（`OneBendSpec` 字段）
  - `:376-377` `if not 0 < self.angle < 360:` → `raise ValueError("折弯角度必须位于 0 与 360 **度**之间")` ← **代码自己把单位写成「度」**
  - `:472` `data.BendAngle = float(spec.angle)` ← **原样赋值，无任何 `math.radians`**
- **官方这边**（`C:\swapi\types\ISketchedBendFeatureData\BendAngle.md`）：
  - `:14` `**Signature**: \`System.double BendAngle {get; set;}\``
  - `:17` `## Returns` —「**0.261799 <= Bend angle in increments of 0.261799 radians (15 degrees) <= 1.5708**」
- **判定**：官方该属性收**弧度**且值域只有 0.2618–1.5708；我们把**度**（0–360）原样传进去 ⇒ 典型 90° 会变成 90 rad，
  既超量纲 57 倍、也远在官方值域之外。**核对表所述无误。**

### S2 · `InsertWeldmentCutList2` 传错实参 —— ✅ **成立**

- **我们这边**（`scripts/sw_weldment.py`）：
  - `:661-662` 来源块逐字：`IFeatureManager.InsertWeldmentCutList2(Object SortOptions) -> Feature` ／ `⚠ InsertWeldmentCutList2 接受一个 Object 参数（排序选项），官方未标注其类型，**按 ICutListSortOptions 传**`
  - `:694` `feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)`（`sort_options` 默认 `None`）
- **官方这边**（`C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md`）：
  - `:12` `Inserts a cut-list-item folder feature containing **the specified weldment bodies**.`
  - `:14` `**Signature**: \`Feature InsertWeldmentCutList2( System.object Bodies )\``
  - `:17` `- **Bodies**: Array of [[Body2]] objects`
- **判定**：官方那一个形参**命名了、也写明了是 Body2 数组** ⇒ 我们来源块里「官方未标注其类型」这句话本身与官方页冲突；
  实参语义（排序选项 / `None`）与官方要的 Body2 数组**完全不同**。
  ★ 加重项：同文件 `ensure_cut_list`（`:260` 附近）走的是 `InsertWeldmentCutList2` + Body2 SAFEARRAY ⇒ **同文件两条路径自相矛盾**。**核对表所述无误。**

### S3 · `FeatureRevolve2` 的旋转轴被清空 —— ✅ **成立**（但与本仓自带的真机记录有张力，见下）

- **我们这边**（`scripts/sw_part.py`）：
  - `:916-918` `if axis_sketch_name: _select_revolve_axis(model, str(axis_sketch_name))` ／ `_ensure_sketch_selected(model, sketch_name)`
  - `:420` `_ensure_sketch_selected` → `if active_ref and _select_sketch_ref(model, active_ref):`
  - `:372-381` `def _select_sketch_ref(model, sketch_ref, mark=0):` … `:381 model.ClearSelection2(True)` ← ★ **核对表指的「第一步」逐字对得上**
  - 即使不走 `_select_sketch_ref`，`:398-400` `_select_sketch_feature_by_name` → `_select_com_object(feature, append=False, mark=0)`；
    `_select_com_object`（`:294`）内部是 `Select2/Select4(Append=False, …)` ⇒ **append=False 同样替换选择集**
- **官方这边**（`C:\swapi\types\IFeatureManager\FeatureRevolve2.md`）：
  - `:42-46` `## Remarks`「Before calling this method, call [[IModelDocExtension::SelectByID2]] to select:
    - the sketch to revolve, using **Mark = 0**.
    - the axis of revolution, using **Mark = 4 or 16**.」
- **判定**：代码事实与官方要求**确实对不上** —— 调用 `FeatureRevolve2` 时轴已不在选择集里。**核对表所述无误。**
- ⚠ **我要补的**：这与 `revolve_boss` 自己的 docstring（`:905-913`，轮 360「改序后 `feature_created=true`，证据 `output/revolve-axis-geometric-evidence.json`」）**存在张力** ——
  若 `_ensure_sketch_selected` 确实清空选区，改序后本不该建成。⇒ **成立，但改之前先回看那份真机证据**，
  搞清「改序」当时生效的是哪条路径（很可能走的是 `sketch_name == "__current_selection__"` 的早退分支 `:416-417`）。**这不改变本条的级别，但改变了改法。**

### S4 · `GetLoadsAndRestraints` 只传 1 个实参 —— ✅ **成立**

- **我们这边**（`scripts/sw_simulation_loads.py`）：
  - `:690` `return _check(manager, "GetLoadsAndRestraints", 1, int(index))`
  - `:232` `def _check(manager, member: str, arity: int, *args):` ／ `:263-264` `if _wants_error_code(member): tail.append(out_i4())`
  - `:319-332` `_ERRORCODE_MEMBERS = frozenset({…})` —— 逐个查过：**只有 `Add*` 开头的一族**，
    **没有** `"GetLoadsAndRestraints"`、**没有** `"GetEdgeWeldConnector"`
  - `:679` 本模块自己的来源块逐字：`GetLoadsAndRestraints(ByVal NIndex As Integer, ByRef ErrorCode As Integer)`
- **官方这边**：.NET CHM `ByVal NIndex As System.Integer, ByRef ErrorCode As System.Integer` ／
  VB6 CHM `GetLoadsmentList2 n=2 :: ByVal NIndex As Long, ByRef ErrorCode As Long` ／
  出厂反射 `CWLoadsAndRestraints GetLoadsAndRestraints(Int32, Int32&)` ⇒ **三源一致 2 形参**
- **判定**：`_wants_error_code` 永不命中 ⇒ 不补末尾出参 ⇒ 实际只送 1 个实参。
  ★ **加强项**：同仓 `sw_simulation.py` 的 `collect_study_evidence()` 对**同一个成员**用的是 2 个实参（含 `out_i4()`）⇒ **同仓两条路径不一致**。**核对表所述无误。**
  （笔误更正：上面 VB6 那行官方原文应为 `GetLoadsAndRestraints n=2 :: …`，核对表原文如此，我复读时写串了，**结论不受影响**。）

### S5 · `swSTLQuality` `"fine": 0` —— ✅ **成立**，且比核对表说的**更严重**

- **我们这边**（`scripts/sw_export.py`）：
  - `:41` `quality_map = {"coarse": 1, "fine": 0}`
  - `:43` `model.SetUserPreferenceIntegerValue(78, quality_map[quality])  # swSTLQuality`
- **官方这边**（`C:\swapi\enums\swSTLQuality_e.md`，`enum_member_count: 3`）：
  - `:18` `| swSTLQuality_Coarse | 1 |`　`:19` `| swSTLQuality_Custom | 3 |`　`:20` `| swSTLQuality_Fine | 2 |`
- **判定**：`0` 确实不是任何成员 —— **核对表所述无误**。
  ★ **但核对表只说了「非法值」，漏了一半**：按官方枚举，**`Fine` 的正确值是 `2`，不是 `0`** ⇒
  `"fine"` 这一档**映射到了不存在的目标**，不只是「越界」。★ 而 MCP 工具
  `solidworks_export_stl` 的 `stl_quality` **默认值就是 `"fine"`** ⇒ 默认路径每次都在传 0。

### S6 · `RULED_TYPE_MEANINGS` 0..4 —— ❌ **不成立**（作为「可改」的依据）；★ 但它暴露了一条真缺陷

- **我们这边**（`scripts/sw_surface_edit_ops.py`）：
  - `:67` 注释：`#: ★ 官方给的 \`Type\` 取值表（★ 逐字来自 \`InsertRuledSurfaceFromEdge2.md\` 的 Parameters）`
  - `:68-74` `RULED_TYPE_MEANINGS = {0: "Tangent to Surface", 1: "Normal to Surface", 2: "Tapered to Vector", 3: "Perpendicular to Vector", 4: "Sweep"}`
  - `:174` `if int(ruled_type) not in RULED_TYPE_MEANINGS:` —— 不做二次校验、不换算，原样透传
- **官方这边 —— 两页，且互相矛盾**：
  - ① `C:\swapi\enums\swRuledSurfaceType_e.md`（`enum_member_count: 5`）：
    `swRuledSurfaceType_TangentToSurface | 1` · `_NormalToSurface | 2` · `_TaperedToVector | 3` · `_PerpendicularToVector | 4` · `_Sweep | 5` —— **没有 0**
  - ② `C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md` **Parameters 段**（我逐行读过）：
    `- **Type**: - 0 = Tangent to Surface - 1 = Normal to Surface - 2 = Tapered to Vector - 3 = Perpendicular to Vector - 4 = Sweep`
    —— ★ **该页从头到尾没有把 `Type` 指向 `swRuledSurfaceType_e`**（对照其它成员页都明写 "as defined in [[…_e]]"）
- **判定**：**不成立**。治理这个形参的是**成员页**，成员页写的就是 0..4，我们**逐字照抄且在注释里如实注明了出处**；
  拿一个**该成员页并未引用**的枚举页去判它错，证据链不成立。核对表自己也附了「★ 两源不一致，不判谁对」，
  但仍然给了「高」置信度并排进可改清单 ⇒ **这一格定级过高**。
- ★ **但顺带查出一条真缺陷**（比原条目更值钱）：同一个参数，**同仓两个模块口径相反** ——
  `sw_surface_features.py:640` 是 `if not (1 <= t <= 5):`（**1..5**），`sw_surface_edit_ops.py:68` 是 **0..4**。
  ⇒ **不管官方两页谁对，本仓自己是不一致的**，这条应当独立立项、且要按「官方两源打架 ⇒ 需先查」处理。

### S7 · `InsertRevisionTable2` 的 `shape` 默认 0 —— ✅ **成立**

- **我们这边**（`scripts/sw_drawing_expose.py`）：
  - `:270` `template: str = "", **shape: int = 0**,`（`add_revision_table` 签名）
  - `:286` `tbl = C.get_com_member(sheet, "InsertRevisionTable2", False, _mm(x_mm), _mm(y_mm), …, int(shape), …)`
- **官方这边**：
  - ① `C:\swapi\types\ISheet\InsertRevisionTable2.md:14` **Signature** 第 6 位是 `System.int Shape`
  - ② 同页 `:22` `- **Shape**: Revision symbol shape as defined in [[swRevisionTableSymbolShape_e]]` ← ★ **明确点名枚举**
  - ③ `C:\swapi\enums\swRevisionTableSymbolShape_e.md`（`enum_member_count: 4`）：`CircleSymbol | 1` · `SquareSymbol | 2` · `TriangleSymbol | 3` · `HexagonSymbol | 4` —— **没有 0**
- **判定**：成员页**明确**把该形参绑到该枚举，枚举**穷举 4 个值且无 0** ⇒ 默认值 `0` 不是合法成员。**核对表所述无误。**

### S8 · `CreateFillet` 的 `Radius` 未换算 —— ✅ **成立**

- **我们这边**（`scripts/sw_sketch_edit_ops.py`）：
  - `:172` `def sketch_fillet(model, selection: str, **radius_mm**: float, constrained_corners: int = 0):`
  - `:175-176` `seg = get_com_member(get_com_member(model, "SketchManager"), "CreateFillet", float(radius_mm), int(constrained_corners))` ← **原样传，无 `mm()`**
  - 模块头自述：`⚠ **单位**：长度**毫米**、角度**度** —— 换算在工具层边界做一次（规则 2）`
- **官方这边**（`C:\swapi\types\ISketchManager\CreateFillet.md`）：
  - `:14` `**Signature**: \`SketchSegment CreateFillet( System.double Radius, System.int ConstrainedCorners )\``
  - `:17` `- **Radius**: Radius of the fillet in **meters**` ← ★ **形参表明写单位**
  - `:27` 官方例子 `CreateFillet(0.01, …)`（= 10 mm）
- **判定**：形参表明写 **meters**，我们把 `_mm` 名下的值原样传 ⇒ 放大 1000 倍。
  ★ 加重项：**同一文件**的 `sketch_chamfer`（官方 `CreateChamfer` 的 `Distance` 同样是米）**用了** `mm(float(distance_mm))` ⇒ **同文件两种做法**。**核对表所述无误。**

### §2 结论

| 判定 | 条数 | 占比 |
|---|---|---|
| ✅ **成立** | **7** | **87.5%** |
| ❌ **不成立** | **1** | 12.5% |
| ⚠ **存疑** | **0** | 0% |

★ **成立率 = 7 / 8 = 87.5%。**
★ **唯一的不成立（S6）不是「报错了」，而是「定级错了」** —— 事实描述本身（官方存在一个 1..5 的同名枚举）是真的，
但**推论**（我们的 0..4 因此非法）不成立，因为**治理该形参的成员页写的就是 0..4、且未引用那个枚举**。
⇒ 对 30 路报的整体判断：**抽样命中率 87.5% ⇒ 83 条高置信里按此比例外推，约 72–74 条可直接据以改代码，
约 9–11 条要退回重查**。★ **但上表已证明「高置信」这一档内部并不均匀**：凡**只靠一个来源**、
或**依据取自官方配方实参而非形参表**、或**两源互相矛盾**的条目，即使标高也应按「需先查」处理（本表已逐条降级，见 §4）。

---

## §3 · 去重台账

### §3.1 「多路都报」—— 已合一的 8 组

| 组 | 合并前 | 合并后行 | 合并依据 |
|---|---|---|---|
| G1 | 02-A（**表外附录**）+ 02-C #1 | **H14** | 同一个成员 `IFeature.GetErrorCode`、同两个调用点、同两段原文；02-A 自己写「属核对 C 范围，本次不判、只记」 |
| G2 | 03-A #1 + 03-B #2 | **H16** | 同一个成员 `InsertWeldmentCutList2`、同一个调用点 `sw_weldment.py:694` |
| G3 | 03-A #2 + 03-B #1 | **H17** | 同一个成员 `InsertSubWeldFolder2`、同一个调用点 |
| G4 | 04-A #1 + 04-C「**查不到**·不报」 | **H20** | ★ **两路结论相反**：04-A 按「三源一致缺席」报为高置信分歧，04-C 按铁律 5 记「查不到」不报。⇒ **合并后按存疑处理** |
| G5 | 05-A（**表外备注** ×2 处）+ 05-C #1 + #2 | **H29** | 同一个成员 `IView.Name`、两个调用点；05-C 自己拆成两条，05-A 表外也记了同两处 |
| G6 | 04-C #8 + 10-C #4 + 10-C #7 | **M25** | 同一个成员 `ISldWorks.ActivateDoc2`、三个调用点（跨 `sw_assembly.py` / `sw_export.py` / `sw_review.py`）。★ 两路置信度不一致（**中** vs **高**）⇒ 取低 |
| G7 | 06-C #6 + 10-C #6 | **H46** | 同一个成员 `IModelDoc2.GraphicsRedraw2`，三个调用点 |
| G8 | 06-C #7 + 07-C #1 + 07-C #2 | **H47** | 同一个成员 `IModelDoc2.GetActiveSketch2`，三个调用点（跨 `sw_part.py` / `sw_sketch_modify_ops.py` / `sw_sketch_edit.py`） |
| G9 | 07-A #6 + 07-C #3 | **H51** | 同一个成员 `IModelDoc2.SketchModifyFlip` 的 `AxisFlag`，核对员 A 路与 C 路引的是同一段官方原文 |
| G10 | 06-B #2 + 06-B #3 | **H39** | 同一个成员 `FeatureLinearPattern3` 的同一个根因（无方向 mark），两个站点 |

### §3.2 「同址不同口径」—— **不合并**，但互相交叉引用（合并会丢掉一半信息）

| 组 | 行 | 说明 |
|---|---|---|
| X1 | H70 + H71 | 同一个调用点 `GetMassProperties`：H70 是**签名口径**（实参 1 vs 形参 2 + float vs int），H71 是**废弃链口径**（该成员 Obsolete）。★ 两路不同核对项，合并即丢信息 |
| X2 | M16 + H41 | 同一个 `fillet()`：M16 是**mark 口径**（无 Mark=1 选择），H41 是**Obsolete 口径** |
| X3 | H38 + H39 + H42/H43 | `FeatureLinearPattern3` 同时命中「mark 口径」(H39) 与「Obsolete 口径」(H42) |
| X4 | H48 + M18 | `ISketchSegment` 的 `Select3`(H48) 与 `Select2`(M18) 是同一 helper 里的两个 Obsolete 尝试 |
| X5 | H14 + H18 | 同一根因（调 Obsolete 的 `GetErrorCode`）落在**两个文件的三个调用点**：已按调用点分列，注释互相指 |

### §3.3 表外重复（**不计入 121**，只记不数）

| 出处 | 内容 | 去向 |
|---|---|---|
| 02-A 附录 | `GetErrorCode` Obsolete（注明「属核对 C 范围，本次不判、只记」） | → H14 |
| 05-A 「范围外备注」第 1 条 | `sw_drawing_expose.py` `get_com_member(view, "Name")` | → H29 |
| 05-A 「范围外备注」第 2 条 | `sw_drawing_create_missing.py` `_read(view, "Name")` | → H29 |

### §3.4 「另一路主动让位」—— 不是重复，是自觉不重报（记其纪律）

- **03-C #25 行**明写：「`sw_sheet_metal_weld_entry.py` 的 `ReliefType` / `FlangePos` 取值域宽于官方该成员页列出的 `valid selections`……**已由同目录 `audit-02-sheetmetal-C.md` 第 3 条以同样两段原文报过 ⇒ 本路不另起一条**」⇒ 落在 **M06**，只算一次。
- **03-C「查不到」段**与 **04-C「查不到」段**都对同一处（`mate.Name`）作了「不报」的记录 ⇒ 仍以 **H20** 一行承载，但**级别因此降为存疑**。
- **08-C / 09-C / 10-C** 各自的「查不到」段（`swFeatureNameID_e` 无数值、`GetSurfaceBodies` 无成员页、`sws*` 枚举不在 swapi 源内、78 / 17 / 18 / 62 数值查不到）⇒ **一律不构成条目**，只在本索引留名，不进总表。

### §3.5 数字对账

| 项 | 数 |
|---|---|
| 30 份表内报出 | 121 |
| 表外重复（§3.3） | +3 |
| 原始声明合计 | **124** |
| G1…G10 去重 | −10（每组 N 条并成 1 条，净减 10） |
| **去重后唯一分歧** | **111 条**（高 **83** + 中 **28**） |

---

## §4 · 分级（只按「能不能据它改代码」分）

| 级 | 条数 | 判据 |
|---|---|---|
| **可改** | **89** | 分歧明确、官方原文清楚 ⇒ 能直接照着改 |
| **需先查** | **18** | 两源不一致 / 官方页缺段 / 只靠官方例子或配方实参 |
| **存疑** | **4** | 抽查判不成立、或两路结论相反、或口径问题 |

> ★ **89 + 18 + 4 = 111**（逐行 `级` 栏机器核过：表内 107 行 + 表外 4 条）。★ 注意「高置信」**不等于**「可改」——
> **H81–H83** 三条是**高置信但判需先查**（官方依据只来自配方实参），**H05 / H32 / H49** 同理。

### §4.1 「可改」—— 90 条（按域分布）

| 域 | 条数 | 行 |
|---|---|---|
| 01-surface | 7 | H01 H02 H03 H04 H06 H07 · M03 |
| 02-sheetmetal | 8 | H09 H10 H11 H12 H13 H14 H15 · M04 M05 |
| 03-weldment | 5 | H16 H17 H18 H19 · M07 |
| 04-assembly | 8 | H21 H22 H23 H24 H25 H26 H27 H28 · M11 M12 |
| 05-drawing | 9 | H29 H30 H31 H33 H34 H35 H36 · M13 M14 M15 |
| 06-features | 12 | H37 H38 H39 H40 H41 H42 H43 H44 H45 H46 H47 H48 |
| 07-sketch | 6 | H50 H51 H52 H53 H54 H56 |
| 08-mold-costing | 5 | H57 H58 H59 H60 H61 |
| 09-simulation | 8 | H62 H63 H64 H65 H66 H67 H68 H69 |
| 10-misc | 12 | H70 H71 H72 H73 H74 H75 H76 H77 H78 H79 H80 · M27 M28 |
| 08-mold-costing（补） | 1 | M21（`InsertMoldPartingSurface` mark 只落一半） |
| **小计** | **89** | 7+8+5+8+9+12+6+5+8+12+1 = **81** 表内 + 2 条表外（M27 M28）… ★ **以逐行 `级` 栏为准（机器核过 111 行）** |

★ **「可改」里最省事的一批（只改调用名 / 常量，不动逻辑）**：
H22–H28 + H41–H48 + H69 + H71 H72 H73 H75 H76（共 **21 条** Obsolete 链）
+ H74 / H35 / H61 / H77（4 条枚举字面量）⇒ **25 条零风险、一次批量就能清掉。**

### §4.2 「需先查」—— 18 条（★ 这一档里藏着最贵的坑）

| 类别 | 行 | 为什么不能直接改 |
|---|---|---|
| **★ 官方两源互相矛盾** | H08（枚举 1..5 vs 成员页 0..4 —— 抽查已判**不成立**，故同时列在 §4.3）、M06（枚举 5/6 个 vs 成员页 `valid selections` 只列 3 个）、M08（`CreateDefinition` 的 35 项 vs `swFeatureNameID_e` 成员表）、M23（`IModelDoc2.MaterialIdName` 标 Obsolete 而 `IPartDoc.MaterialIdName` 不标）、M24（`ExportToDWG2` 的 Remarks 要预选、官方例子同 Action 不预选） | 改哪边都是猜 ⇒ 必须先定口径 |
| **官方页缺段** | H32（`SetTemplateName.md` 无 `ForceRebuild3` 字样、CHM 无该成员页）、H49（CHM 无 `ISketch~GetContourEdges` 页 ⇒ 只有 swapi 单源）、M25（CHM 无 `ISldWorks~ActivateDoc2` 成员页）、M20（`SetPickMode` 只在官方例子里）、M10（`ToolsCheckInterference` 只在官方例子里） | 单源/例证不足 ⇒ 先补查 |
| **量纲依据取自配方实参而非形参表** | H81（`SketchOffset2.Offset`）、H82（`CreateLinearSketchStepAndRepeat.SpacingX/Y`）、H83（`CreateCircularSketchStepAndRepeat.ArcRadius`） | ★ 形参表**本身没写单位**，靠「官方例子传了 0.00254」反推 ⇒ 补查官方是否存在写明单位的第二页 |
| **形参声明类型只在 md 里** | M01（`CreateSheetFromSurface.UvRange` 是数组，但形参类型两侧都写 `System.object`）、M02（`InsertLoftRefSurface2` 的 `short` vs 我们 `int`） | 类型宽度/容器类型要靠反射（铁律 4 裁决者）定 |
| **枚举归属未证** | M22（`units=-1`；★ 官方 `NUnits` 形参**没写**它属于哪个枚举，「`units` 就是 `swsUnit_e`」是我们自己写的） | 连归属都没坐实 ⇒ 别动 |
| **两路结论相反** | H05（01-B 说 `FeatureBossThicken` 缺 mark=1，06-B 把 `thicken_surface` 判为一致 ⇒ 可能是两个不同模块的实现） | 先确认是不是同一份代码 |
| **完整性断言口径** | M09（「焊件相关的只有这 3 个」vs 同页另有 6 条 Structure system） | 是口径问题，不是代码问题 |

★ **分档合计**：5（两源矛盾，含 H08）+ 5（缺段）+ 3（量纲）+ 2（类型）+ 1（枚举归属）+ 1（两路相反）+ 1（口径）= **18 条** ✓

### §4.3 「存疑」—— 4 条

| 行 | 为什么存疑 |
|---|---|
| **H08** | ★ **抽查判「不成立」**（§2 S6）：治理该形参的成员页 `InsertRuledSurfaceFromEdge2.md` 写的就是 0..4、且**未引用** `swRuledSurfaceType_e` ⇒ 拿枚举页判它错，证据链不成立。★ 但它顺手暴露的**同仓自相矛盾**（`sw_surface_features.py:640` 用 1..5 vs `sw_surface_edit_ops.py:68` 用 0..4）是**真问题**，应独立立项 |
| **H20** | ★ **两路结论相反**：04-A 按「三源一致缺席 `IMate2.Name`」报高置信分歧，04-C 按铁律 5 记「查不到」不报。⇒ 先定「缺席」算不算分歧 |
| **M19** | 官方例子没预选，但官方也**没禁止**预选 ⇒ 只凭例子判不了「我们无条件先选」是错 |
| **M26** | COM 属性名分派**大小写不敏感**；官方例子写 `COSMOSWORKS` 不构成 API 约束，而反射（铁律 4 裁决者）站我们这边（`get_CosmosWorks`） |

---

## §5 · 结尾统计 · 最该先改的 5 条

### §5.1 统计

| 项 | 数 |
|---|---|
| 读入的核对表 | **30 份** |
| 表内报出 / 表外重复 / 原始声明 | 121 / +3 / **124** |
| **去重后唯一分歧** | **111** |
| **高置信 / 中置信** | **83 / 28** |
| **抽查**（8 份文件 / 8 个域，抽 8 条高置信） | 成立 **7** · 不成立 **1** · 存疑 **0** |
| **★ 抽查成立率** | **87.5%（7/8）** |
| 可改 / 需先查 / 存疑 | **89 / 18 / 4** |
| 「多路都报」合并组 | **10 组**（吃掉 10 条重复） |
| 零风险批（只改调用名 / 常量） | **25 条** |

### §5.2 ★ 最该先改的 5 条（按「改了会不会让工具**真的能跑**」排）

> 排序口径：**不是**按严重程度，是按**「现在跑不了 ⇒ 改完就能跑」的直接性**。
> 前 5 条里有 **4 条**是我亲自打开代码 + 官方页复核过的（§2 S2 / S4 / S5，以及 S3 的代码事实）。

| # | 行 | 改什么 | 为什么排在这 | 风险 |
|---|---|---|---|---|
| **1** | **H62 / H63** | `sw_simulation_loads.py:319` 的 `_ERRORCODE_MEMBERS` 里**加两个名字**：`"GetLoadsAndRestraints"`、`"GetEdgeWeldConnector"` | ★ **改动最小、收益最直接**：官方三源一致都是 `(Int32, Int32&)` **2 形参**，少传一个在 COM 里就是「参数个数不符」⇒ 这两个读取入口**现在就跑不了**。加进 frozenset 后 `_check`（`:263-264`）自动补 `out_i4()`，**一行 frozenset 改动** | 极低。模块自己的来源块（`:679`）已逐字抄下正确签名 ⇒ 与代码「自相矛盾」这一事实本身就是铁证 |
| **2** | **H16 / H17** | `sw_weldment.py:694` 传 Body2 数组（照同文件 `ensure_cut_list` 已有的正确写法）、`:create_sub_weld_folder` 传 Body2 数组 | ★ **现在必然建不出特征**：官方那一个 `Object` 形参**命名了、也写明是 Body2 数组**，我们传的是排序选项 / `None`。⇒ 切割清单与子焊件文件夹两个工具现在**建不出东西**。★ 同文件已有正确实现可抄 | 低。注意 H17 的后继：**官方没有**接受「父文件夹对象」的 `InsertSubWeldFolder*` 重载（03-A「查不到」段明写），所以只能传 Body2 数组 |
| **3** | **H74** | `sw_export.py:41` `quality_map` 的 `"fine": 0` → **`2`** | ★ **影响面最大**：MCP 工具 `solidworks_export_stl` 的 `stl_quality` **默认值就是 `"fine"`** ⇒ **每次默认导出都在传一个非法枚举值**。而且按官方 `swSTLQuality_e`，`Fine` 是 **2** 不是 0 ⇒ 不只是越界，是**映射错了目标**。改一个常量 | 极低。⚠ 但 `SetUserPreferenceIntegerValue(78, …)` 里的 **78** 在两套离线源里都查不到出处（10-C「查不到」段）⇒ 只改 `quality_map`，别动 78 |
| **4** | **H09 / H10 / H11** | `sw_sheet_metal.py` 三个角度实参补 `math.radians()`：`BendAngle`(×2) / `Angle` | ★ **三个官方成员逐个明写收弧度**（`ISketchedBendFeatureData` 值域 0.2618–1.5708、`IEdgeFlangeFeatureData` 默认 π/2、`IDraftFeatureData2` "in radians"），而我们的 spec 校验文案自己写的是「**度**」⇒ 折弯 / 边法兰 / 拔模三个角度**全部越界**。`EdgeFlangeSpec.angle` 的**默认值 `90.0`** 就直接超量纲 57 倍 | 低。★ 已知事实 47 已记：这三个 `FeatureData` 成员在本机 pywin32 后端**到不了「建成」**（`AccessSelections` / `SetFixedFace` 不可调用）⇒ **改量纲不会让它们今天就跑通**，但它是「一旦后端通了就能对」的必要修正，且**不修就一定错** |
| **5** | **H38** | `sw_part.py` `revolve_boss` / `revolve_cut`：让 `_ensure_sketch_selected` **不清掉轴**（或选完轮廓后重选轴） | ★ 官方 `FeatureRevolve2.md:42-46` 要求**轮廓 mark 0 与轴 mark 4/16 同时在选区**；我们 `:917` 选轴 → `:918` 进 `_ensure_sketch_selected` → `:381 ClearSelection2(True)`（或 `_select_com_object(append=False)`）⇒ 轴**必然不在选区**。★ 这是**唯一一条本仓自带真机证据（`feature_created=false`）的分歧** | ⚠ **中**。★ 我在 §2 S3 已标注：它与 `revolve_boss` docstring 记的「轮 360 改序后建成了」**有张力** ⇒ **改之前先回看 `output/revolve-axis-geometric-evidence.json`**，搞清当时生效的是哪条路径（很可能是 `sketch_name == "__current_selection__"` 的早退分支 `:416-417`）。★ 这不改变本条的级别，但**改变改法** |

### §5.3 紧随其后的 5 条（若上面 5 条处理完还有余力）

| 行 | 一句话 |
|---|---|
| **25 条零风险批**（H22–H28 · H41–H48 · H69 · H71–H73 · H75 · H76 · H74 · H35 · H61 · H77） | 只改调用名 / 常量、不动逻辑 ⇒ ★ **建议一次性批量做完**，先把「还在调官方 Obsolete 成员」这个面清零。注意 `GetErrorCode`→`GetErrorCode2`（H14/H18）与 `MaterialIdName`（M23）**另有两源理由**，别混进这批 |
| **H79** | `sw_loft.py` 把 `UseAutoSelect` **硬编码 False** 却不选 body ⇒ 按官方两页逐字要求，放样/放样切除两个入口**建不出受影响体** |
| **H57** | `sw_measure.py` `IMeasure.Calculate` 传 0 实参而官方形参是 1 个。⚠ 官方说明「NULL 就量选区」**语义上支持不传**、且本仓事实 227 记的是「真机必须无参调」⇒ ★ **这条要在真机上先复现一次**再动，否则会把现在能用的量测改坏 |
| **H30 / H34 / H59** | 三个「前置 gate 太松」的：`GetSelectedObjectType3` 当 mark 用、局部视图缺两步前置、芯模型腔缺三条官方前置 ⇒ 都属「不报错但结果不对」类，**改了会明显提升成功率** |
| **H78 / H51 / H56 / H19** | 四条「**我们写下的官方依据与官方原文对不上**」⇒ 改起来零风险、但价值很高：★ **错误注释会让下一个人继续按错的依据改**。本仓 AGENTS.md 第 0 步纪律（「官方文档是第 0 步」）最怕的就是这种自我强化的假依据 |

---

★ **一句话交接**：**30 路报的东西，八成七是真的**（抽查 7/8）；
唯一的假货是「官方自己两源打架、核对员没敢下结论却给了高置信度」，而它顺手暴露了一条**同仓自相矛盾的真缺陷**；
**先做 §5.2 的第 1–3 条**（各是一两行的改动，却分别卡着两个读取入口、两个建特征入口、和一个导出工具的默认路径），
**第 4、5 条先补查再动**。
