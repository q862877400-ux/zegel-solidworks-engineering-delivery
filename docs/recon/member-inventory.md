# 仓库 `scripts/*.py` 用到的 COM 成员名 · 官方源对账表

> **来源（两侧都真读）**
> - **代码侧**：`D:\AI\SW\scripts\*.py` **全部 168 个 `.py`**（0 个语法错误）。用 `ast` 解析
>   （**不是正则**），取 `get_com_member` / `set_com_member` / `call_com_member` / `safe_get_com_member`
>   / `get_com_member_raw` 五个包装的**第 2 个实参**（字符串字面量），并按 AST 回读
>   「形参名转手」的辅助函数（`_count(name)` / `_invoke(obj, member, …)` 那类）的**调用点**。
> - **官方侧 ①**：`C:\swapi\types\` —— 真读 **566** 个接口目录、**11,557** 个成员页的 frontmatter
>   （`member:` 字段），建立「成员名 → 页面」索引（**8,238** 个不同成员名）。
>   ⚠ 任务要求「接口目录可能带或不带前导 `I`，两种都试」—— **两种都试了**：先按成员名**精确**查，
>   不中再按「去掉前导 `I`」查。实测**第二种一次都没用上**（`only-stripped = 0`）——
>   因为本表索引是**按成员名**（不是按接口目录名）建的，而页面里 `member:` 字段本就写成去前缀的裸名。
> - **官方侧 ②**：`D:\AI\SW\_raw\**\iface_*.txt` —— **15** 份出厂反射清单（**11,120** 个不同成员名），
>   用于「`C:\swapi\types` 里没有页」的那些成员（本仓 `check_member_names.py` 自称的官方反射源）。
> - **判据**：沿用 `docs/recon/README.md` 的三条，并按 `docs/recon/family-scan-100-criteria-defects.md`
>   已报的洞**拆开**：废弃记严格版（页头行首 `Obsolete.`，只看 `**Signature**` 之前）；指针记
>   **大小写不敏感 + 认 `in-porcess` 笔误**。
>
> ⚠ **本文件不含任何行号**（行号会漂，实测偏过 47 行）；代码出处一律给**文件名**，可 `grep`。

## 一、统计

| 指标 | 数 |
|---|---|
| 扫过的 `.py` | **168**（`scripts/` 下全部；`ast` 语法错误 0） |
| `*_com_member` **调用点（全部）** | **1429** |
| —— 其中第 2 实参是**字符串字面量**（可对账） | **1345** |
| —— 其中第 2 实参是**变量/表达式**（对账不了，列在第五节） | 84 |
| **去重后的成员名** | **744** |
| 至少 1 个官方 `C:\swapi\types` 页 | **524** |
| —— 其中命中**多个**接口目录（同名成员分属多族） | 204 |
| `C:\swapi\types` **无页**、但**在反射清单里查得到** | **220** |
| 两个官方源**都**查不到 | **0** |
| 精确名不中、靠「去前导 `I`」才命中的 | **0**（两种都试过，第二种没用上） |
| 命中页中页头 `Obsolete.`（严格） | 74 |
| 命中页中含指针标记（全文，含 `In-process` / `in-porcess`） | 0 |
| 命中页里去重后的**页面**张数 | 1415 |

交叉验算：524 + 220 = **744** = 去重成员名总数。

### 1.1 ⚠ 与仓库既有门禁的口径差（**两个数都真，差在扫描方法**）

| 口径 | 调用点数 | 说明 |
|---|---|---|
| 本表（`ast` 精确解析） | **1429** | 多行调用、跨行实参、辅助函数转手**都算** |
| 本仓 `scripts/check_member_names.py`（正则） | **987** | 该门禁自带 `[^,()]+` 行内匹配，**多行调用与转手形态收不到** |

⇒ 本表**不是**复述该门禁的输出；两数之差是本轮**多找出来的调用点**。⚠ 两者**不矛盾**：
门禁判的是「名字在不在反射里」，本表判的是「这个名字有几处、官方页在哪、是不是废弃/指针」。

### 1.2 ★ 指针成员命中数为 **0**，且这是**实测**出来的（不是「没查」）

| 口径 | 页数 | 其中含 `in-process` 标记 |
|---|---|---|
| 官方源**全部**成员页 | 11,557 | **739** |
| 本仓代码**真正用到**的那些页（去重） | 1,415 | **0** |

⇒ 两件事同时成立：**官方源里指针页有 739 张（占 6.4%）**，而**本仓代码一处都没碰**。
这与已知事实 47 吻合（那条记的是 `create_one_bend` / `create_edge_flange` / `create_gusset`
三条**走不到建成**）；本表补的是：**除那三条之外，`scripts/` 里被调用的成员名没有一个是指针成员**。
⚠ 本表**只判名字**，不判「这些名字在真机上能不能建成」—— 那是主线的判据。

## 二、主表 —— 有官方 `C:\swapi\types` 页的 524 个成员

| 成员名 | 出现文件数 | 调用点 | 官方页数 | 官方页（接口/文件） | Obsolete | 指针 | Returns 首行 |
|---|---|---|---|---|---|---|---|
| Name | 23 | 59 | 24 | `IBody2/Name.md`；`IBomFeature/Name.md`；`ICommandGroup/Name.md`；`ICommandTab/Name.md` …（共 24） | 是 | 否 | Name of selected body |
| Extension | 19 | 28 | 1 | `IModelDoc2/Extension.md` | 否 | 否 | [[IModelDocExtension]] object |
| FeatureManager | 15 | 42 | 1 | `IModelDoc2/FeatureManager.md` | 否 | 否 | [[IFeatureManager]] object |
| GetSelectedObjectCount2 | 14 | 25 | 1 | `ISelectionMgr/GetSelectedObjectCount2.md` | 否 | 否 | Number of selected objects |
| SelectionManager | 14 | 25 | 1 | `IModelDoc2/SelectionManager.md` | 否 | 否 | 查不到 |
| GetBodies2 | 13 | 17 | 2 | `IComponent2/GetBodies2.md`；`IPartDoc/GetBodies2.md` | 是 | 否 | Array of [[bodies]] in the component |
| FeatureByName | 8 | 18 | 4 | `IAssemblyDoc/FeatureByName.md`；`IComponent2/FeatureByName.md`；`IDrawingDoc/FeatureByName.md`；`IPartDoc/FeatureByName.md` | 否 | 否 | Object for the feature |
| GetType | 8 | 8 | 13 | `IAnnotation/GetType.md`；`IBody2/GetType.md`；`IComponent2/GetType.md`；`ICustomPropertyManager/GetType.md` …（共 13） | 是 | 否 | Type of the annotation as defined in [[swAnnotationType_e]] |
| GetTitle | 7 | 10 | 2 | `IDesignTable/GetTitle.md`；`IModelDoc2/GetTitle.md` | 否 | 否 | Design table title |
| FirstFeature | 6 | 18 | 3 | `IComponent2/FirstFeature.md`；`IModelDoc2/FirstFeature.md`；`IPartDoc/FirstFeature.md` | 否 | 否 | Pointer to the first [[feature]] in this component |
| GetFaces | 6 | 8 | 8 | `IBody2/GetFaces.md`；`IDimXpertFeature/GetFaces.md`；`IFeature/GetFaces.md`；`IMateLoadReference/GetFaces.md` …（共 8） | 否 | 否 | Array of [[faces]] on the body |
| GetNextFeature | 6 | 18 | 1 | `IFeature/GetNextFeature.md` | 否 | 否 | Next [[feature]] |
| GetTypeName2 | 6 | 22 | 1 | `IFeature/GetTypeName2.md` | 否 | 否 | String identifying the type of feature (see **Remarks**) |
| SketchManager | 6 | 25 | 1 | `IModelDoc2/SketchManager.md` | 否 | 否 | [[Sketch manager]] |
| ClearSelection2 | 5 | 10 | 1 | `IModelDoc2/ClearSelection2.md` | 否 | 否 | 查不到 |
| GetPathName | 5 | 8 | 2 | `IComponent2/GetPathName.md`；`IModelDoc2/GetPathName.md` | 否 | 否 | Full path name for this component, including the filename |
| ActiveView | 4 | 5 | 1 | `IModelDoc2/ActiveView.md` | 否 | 否 | Current active [[model view]] in this document |
| Count | 4 | 8 | 4 | `IBalloonStack/Count.md`；`ICustomPropertyManager/Count.md`；`IFaultEntity/Count.md`；`IParagraphs/Count.md` | 否 | 否 | Number of balloons in this balloon stack, excluding the master balloon |
| GetBodyBox | 4 | 5 | 1 | `IBody2/GetBodyBox.md` | 否 | 否 | Array of 6 doubles representing the extents of the bounding box (see **Remarks**) |
| GraphicsRedraw | 4 | 4 | 2 | `IModelDoc2/GraphicsRedraw.md`；`IModelView/GraphicsRedraw.md` | 是 | 否 | 查不到 |
| ActiveDoc | 3 | 4 | 1 | `ISldWorks/ActiveDoc.md` | 否 | 否 | [[Model document]] or Nothing or null if the operation fails |
| ActiveSketch | 3 | 6 | 1 | `ISketchManager/ActiveSketch.md` | 否 | 否 | Active [[sketch]] |
| ConfigurationManager | 3 | 4 | 1 | `IModelDoc2/ConfigurationManager.md` | 否 | 否 | [[IConfigurationManager]] object |
| CreateDefinition | 3 | 5 | 2 | `IFeatureManager/CreateDefinition.md`；`IMotionStudy/CreateDefinition.md` | 否 | 否 | [[thread]], [[sweep]], [[library]], [[library form tool]], [[tab and slot]], [[bounding box]], [[ground plane]], [[mirror components]], [[projection curve]], [[sheet metal normal cut]], [[sheet metal swept flange]], [[sheet metal gusset]], [[sheet metal edge flange]], [[convert solid to sheet metal]], [[simple fillet/chamfer]], [[belt/chain]], [[sheet metal base flange]], [[sheet metal corner reli … |
| CreateFeature | 3 | 5 | 2 | `IFeatureManager/CreateFeature.md`；`IMotionStudy/CreateFeature.md` | 否 | 否 | [[IFeature]] |
| EditRebuild3 | 3 | 6 | 1 | `IModelDoc2/EditRebuild3.md` | 否 | 否 | True if only those features that need to be rebuilt are rebuilt in the active configuration in the model, false if not |
| Equation | 3 | 4 | 2 | `IEquationMgr/Equation.md`；`IStraightTapElementData/Equation.md` | 否 | 否 | Equation for the blind depth or offset distance as defined in [[swStraightTapHoleEquation_e]] |
| GetComponents | 3 | 5 | 6 | `IAssemblyDoc/GetComponents.md`；`IBomTableAnnotation/GetComponents.md`；`ICollision/GetComponents.md`；`ICollisionDetectionGroup/GetComponents.md` …（共 6） | 是 | 否 | Array of [[IComponent2]]s (see **Remarks**) |
| GetDefinition | 3 | 11 | 2 | `IAttribute/GetDefinition.md`；`IFeature/GetDefinition.md` | 否 | 否 | Object for the attribute definition |
| GetEdges | 3 | 4 | 8 | `IBody2/GetEdges.md`；`IFace2/GetEdges.md`；`ILoop2/GetEdges.md`；`IRuledSurfaceFeatureData/GetEdges.md` …（共 8） | 是 | 否 | Array of [[edges]] |
| GetFirstView | 3 | 4 | 1 | `IDrawingDoc/GetFirstView.md` | 否 | 否 | First drawing [[view]] in this drawing document |
| GetName | 3 | 5 | 9 | `IAnnotation/GetName.md`；`IAttribute/GetName.md`；`IDetailCircle/GetName.md`；`IDrSection/GetName.md` …（共 9） | 否 | 否 | Name of this annotation |
| GetName2 | 3 | 4 | 1 | `IView/GetName2.md` | 否 | 否 | Name of the drawing view |
| GetNextView | 3 | 5 | 1 | `IView/GetNextView.md` | 否 | 否 | Next [[view]] |
| GetSelectedObject6 | 3 | 3 | 1 | `ISelectionMgr/GetSelectedObject6.md` | 否 | 否 | Selected object as defined in [[swSelectType_e]]; Nothing or null might be returned if the type is not supported or if nothing is selected |
| GetSketchSegments | 3 | 5 | 4 | `ISketch/GetSketchSegments.md`；`ISketchContour/GetSketchSegments.md`；`ISketchPath/GetSketchSegments.md`；`IStructuralMemberFeatureData/GetSketchSegments.md` | 否 | 否 | Array of [[sketch segments]], which include line, arc, spline, parabola, and ellipse entities, in this sketch (see **Remarks**) |
| GetSurface | 3 | 3 | 1 | `IFace2/GetSurface.md` | 否 | 否 | Underlying [[surface]] for this face |
| IsCylinder | 3 | 3 | 1 | `ISurface/IsCylinder.md` | 否 | 否 | True if surface is cylinder, false if not |
| RevisionNumber | 3 | 4 | 1 | `ISldWorks/RevisionNumber.md` | 否 | 否 | SOLIDWORKS Design version number (See **Remarks**) |
| SelectByID2 | 3 | 6 | 1 | `IModelDocExtension/SelectByID2.md` | 否 | 否 | True if item was successfully selected, false if not |
| Type | 3 | 4 | 36 | `IBodyFolder/Type.md`；`ICalloutVariable/Type.md`；`ICamera/Type.md`；`IChamferFeatureData2/Type.md` …（共 36） | 否 | 否 | Type of body folder as defined in [[swBodyFolderFeatureType_e]] |
| AccessSelections | 2 | 3 | 117 | `IAdvancedHoleFeatureData/AccessSelections.md`；`IBaseFlangeFeatureData/AccessSelections.md`；`IBeltChainFeatureData/AccessSelections.md`；`IBendsFeatureData/AccessSelections.md` …（共 117） | 否 | 否 | True if the selections are successfully accessed, false if not |
| ActiveConfiguration | 2 | 3 | 1 | `IConfigurationManager/ActiveConfiguration.md` | 否 | 否 | Pointer to the [[IConfiguration]] object |
| BendRadius | 2 | 3 | 10 | `IBaseFlangeFeatureData/BendRadius.md`；`IBendsFeatureData/BendRadius.md`；`IConvertSolidFeatureData/BendRadius.md`；`IEdgeFlangeFeatureData/BendRadius.md` …（共 10） | 否 | 否 | Value of the bend radius |
| CenterOfMass | 2 | 2 | 1 | `IMassProperty2/CenterOfMass.md` | 否 | 否 | Array of three doubles of the x, y, and z coordinates of the center of mass |
| ConfigurationName | 2 | 2 | 4 | `IDocumentSpecification/ConfigurationName.md`；`ILibraryFeatureData/ConfigurationName.md`；`IStructuralMemberFeatureData/ConfigurationName.md`；`IView3D/ConfigurationName.md` | 否 | 否 | Name of configuration to load |
| CustomPropertyManager | 2 | 6 | 5 | `IComponent2/CustomPropertyManager.md`；`IConfiguration/CustomPropertyManager.md`；`ICutListItem/CustomPropertyManager.md`；`IFeature/CustomPropertyManager.md` …（共 5） | 否 | 否 | Pointer to [[ICustomPropertyManager]] object |
| CylinderParams | 2 | 2 | 1 | `ISurface/CylinderParams.md` | 否 | 否 | Array of doubles describing the parameters of a cylindrical surface |
| ForceType | 2 | 3 | 1 | `ISimulationForceFeatureData/ForceType.md` | 否 | 否 | Type of force as defined in [[swSimulationForceType_e]] |
| GetAnnotationCount | 2 | 2 | 3 | `IDimXpertPart/GetAnnotationCount.md`；`IModelDocExtension/GetAnnotationCount.md`；`IView/GetAnnotationCount.md` | 否 | 否 | Number of DimXpert annotations |
| GetAnnotations | 2 | 2 | 3 | `IDimXpertPart/GetAnnotations.md`；`IModelDocExtension/GetAnnotations.md`；`IView/GetAnnotations.md` | 否 | 否 | Array of [[IDimXpertAnnotation]]s |
| GetArea | 2 | 2 | 1 | `IFace2/GetArea.md` | 否 | 否 | Face area in square meters (see **Remarks**) |
| GetBodyCount | 2 | 3 | 1 | `IBodyFolder/GetBodyCount.md` | 否 | 否 | Number of bodies in the folder |
| GetComponentCount | 2 | 2 | 3 | `IAssemblyDoc/GetComponentCount.md`；`ICollisionDetectionGroup/GetComponentCount.md`；`IInterference/GetComponentCount.md` | 否 | 否 | Number of components |
| GetErrorCode | 2 | 3 | 1 | `IFeature/GetErrorCode.md` | 是 | 否 | Feature error code as defined in [[swFeatureError_e]] |
| GetFirstSubFeature | 2 | 2 | 1 | `IFeature/GetFirstSubFeature.md` | 否 | 否 | First sub-feature of this [[feature]] |
| GetLoopCount | 2 | 2 | 3 | `IFace2/GetLoopCount.md`；`IShutOffSurfaceFeatureData/GetLoopCount.md`；`ISimpleFilletFeatureData2/GetLoopCount.md` | 否 | 否 | Number of loops in this face |
| GetModelDoc2 | 2 | 3 | 1 | `IComponent2/GetModelDoc2.md` | 否 | 否 | [[Model document]] |
| GetNames | 2 | 3 | 1 | `ICustomPropertyManager/GetNames.md` | 否 | 否 | Names of the custom properties |
| GetNextSubFeature | 2 | 2 | 1 | `IFeature/GetNextSubFeature.md` | 否 | 否 | Next sub-[[feature]] |
| GetPlotCount | 2 | 2 | 1 | `ICosmosMotionStudyResults/GetPlotCount.md` | 否 | 否 | Number of plots |
| GetRelations | 2 | 2 | 4 | `ISketchPath/GetRelations.md`；`ISketchPoint/GetRelations.md`；`ISketchRelationManager/GetRelations.md`；`ISketchSegment/GetRelations.md` | 否 | 否 | Array of [[sketch relations]] |
| GetRelationsCount | 2 | 2 | 4 | `ISketchPath/GetRelationsCount.md`；`ISketchPoint/GetRelationsCount.md`；`ISketchRelationManager/GetRelationsCount.md`；`ISketchSegment/GetRelationsCount.md` | 否 | 否 | Number of sketch relations |
| GetSheetNames | 2 | 2 | 1 | `IDrawingDoc/GetSheetNames.md` | 否 | 否 | Array containing the names of the drawing sheets in this drawing |
| GetSketchContours | 2 | 3 | 1 | `ISketch/GetSketchContours.md` | 否 | 否 | Array of [[sketch contours]] |
| GetSketchRegions | 2 | 3 | 1 | `ISketch/GetSketchRegions.md` | 否 | 否 | Array of [[sketch regions]] |
| GetSpecificFeature2 | 2 | 4 | 1 | `IFeature/GetSpecificFeature2.md` | 否 | 否 | Specific interface (see **Remarks**) |
| InsertFeatureReplaceFace | 2 | 2 | 1 | `IModelDoc2/InsertFeatureReplaceFace.md` | 否 | 否 | True if the edges match, false if not |
| InsertOffsetSurface | 2 | 2 | 1 | `IModelDoc2/InsertOffsetSurface.md` | 否 | 否 | 查不到 |
| InsertPlanarRefSurface | 2 | 2 | 1 | `IModelDoc2/InsertPlanarRefSurface.md` | 否 | 否 | True if the reference surface is created, false if not |
| InsertRuledSurfaceFromEdge2 | 2 | 2 | 1 | `IFeatureManager/InsertRuledSurfaceFromEdge2.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| IsSuppressed | 2 | 2 | 4 | `IComponent2/IsSuppressed.md`；`IDimXpertAnnotation/IsSuppressed.md`；`IDimXpertFeature/IsSuppressed.md`；`IFeature/IsSuppressed.md` | 是 | 否 | True if this component is suppressed, false if not |
| Name2 | 2 | 8 | 2 | `IComponent2/Name2.md`；`IConnectionPointFeatureData/Name2.md` | 否 | 否 | Name of this component |
| RelationManager | 2 | 6 | 1 | `ISketch/RelationManager.md` | 否 | 否 | [[Sketch relation manager]] |
| Select4 | 2 | 2 | 5 | `IComponent2/Select4.md`；`IEntity/Select4.md`；`ISketchHatch/Select4.md`；`ISketchPoint/Select4.md` …（共 5） | 否 | 否 | True if the component is selected, false if not |
| Unit | 2 | 4 | 3 | `IPMIDatumTarget/Unit.md`；`IPMIDimensionItem/Unit.md`；`IPMIGtolBoxData/Unit.md` | 否 | 否 | Units as defined in [[swPMIUnit_e]] |
| Volume | 2 | 2 | 2 | `IInterference/Volume.md`；`IMassProperty2/Volume.md` | 否 | 否 | Volume of the interference |
| Activate | 1 | 1 | 8 | `IAnnotationView/Activate.md`；`ICommandGroup/Activate.md`；`IModelView/Activate.md`；`IModelWindow/Activate.md` …（共 8） | 否 | 否 | True if the annotation view is activated, false if not |
| Add2 | 1 | 1 | 2 | `ICustomPropertyManager/Add2.md`；`IEquationMgr/Add2.md` | 是 | 否 | - 1 if custom property is added |
| AddConfiguration3 | 1 | 1 | 1 | `IModelDoc2/AddConfiguration3.md` | 否 | 否 | Newly created [[configuration]] |
| AddCurvatureControl | 1 | 1 | 1 | `ISketchSpline/AddCurvatureControl.md` | 否 | 否 | [[Spline handle]] |
| AddDimension2 | 1 | 1 | 1 | `IModelDoc2/AddDimension2.md` | 否 | 否 | Newly created [[dimension]] |
| AddDisplayStateSpecificRenderMaterial | 1 | 1 | 1 | `IModelDocExtension/AddDisplayStateSpecificRenderMaterial.md` | 否 | 否 | True if appearance is added, false if not |
| AddFrame | 1 | 1 | 1 | `IGtol/AddFrame.md` | 否 | 否 | True if frame successfully added, false if not |
| AddHorizontalDimension2 | 1 | 1 | 1 | `IModelDoc2/AddHorizontalDimension2.md` | 否 | 否 | Newly created [[dimension]] |
| AddIndicator | 1 | 1 | 1 | `IGtolFrame/AddIndicator.md` | 否 | 否 | True if tolerance indicator successfully added, false if not |
| AddMate5 | 1 | 1 | 1 | `IAssemblyDoc/AddMate5.md` | 是 | 否 | [[Mate]] |
| AddPathLengthDim | 1 | 1 | 1 | `IModelDocExtension/AddPathLengthDim.md` | 否 | 否 | [[IDisplayDimension]] |
| AddPerspective | 1 | 1 | 1 | `IModelView/AddPerspective.md` | 否 | 否 | 查不到 |
| AddRelation | 1 | 1 | 2 | `IModelDoc2/AddRelation.md`；`ISketchRelationManager/AddRelation.md` | 是 | 否 | [[Sketch relation]] |
| AddSelectionListObject | 1 | 1 | 1 | `ISelectionMgr/AddSelectionListObject.md` | 否 | 否 | True if successful, false if not |
| AddTangencyControl | 1 | 1 | 1 | `ISketchSpline/AddTangencyControl.md` | 否 | 否 | [[Spline handle]] |
| AddVerticalDimension2 | 1 | 1 | 1 | `IModelDoc2/AddVerticalDimension2.md` | 否 | 否 | Newly created [[dimension]] |
| AdvancedGraphics | 1 | 1 | 1 | `IMaterialVisualPropertiesData/AdvancedGraphics.md` | 是 | 否 | True if the part is displayed with shaded textures, false if not |
| Ambient | 1 | 2 | 1 | `IRenderMaterial/Ambient.md` | 否 | 否 | Ambient light intensity |
| Angle | 1 | 1 | 27 | `IAngleMateFeatureData/Angle.md`；`ICalloutAngleVariable/Angle.md`；`ICountersinkElementData/Angle.md`；`IDimXpertChamferFeature/Angle.md` …（共 27） | 否 | 否 | Angle in radians |
| ApplyAppearance | 1 | 1 | 1 | `IMaterialVisualPropertiesData/ApplyAppearance.md` | 否 | 否 | True to apply the appearance of material, false to not (see **Remarks**) |
| ApplyMaterialColorToPart | 1 | 1 | 1 | `IMaterialVisualPropertiesData/ApplyMaterialColorToPart.md` | 否 | 否 | True if the part color matches the material color, false if not |
| ApplyMaterialHatchToSection | 1 | 1 | 1 | `IMaterialVisualPropertiesData/ApplyMaterialHatchToSection.md` | 否 | 否 | True if the [[drawing section views]] use the material hatch, false if not |
| ArrayData | 1 | 1 | 3 | `IMathPoint/ArrayData.md`；`IMathTransform/ArrayData.md`；`IMathVector/ArrayData.md` | 否 | 否 | Array of 3 doubles representing the x,y,z coordinates of the math point |
| AutoBalloon5 | 1 | 1 | 1 | `IDrawingDoc/AutoBalloon5.md` | 否 | 否 | Array of [[INotes]] |
| AutoDimension2 | 1 | 1 | 1 | `ISketch/AutoDimension2.md` | 是 | 否 | swAutodimStatusSuccess if the sketch is automatically dimensioned successfully; see [[swAutodimStatus_e]] for values for reasons for possible failures |
| BlendColor | 1 | 1 | 2 | `IMaterialVisualPropertiesData/BlendColor.md`；`ITexture/BlendColor.md` | 否 | 否 | True to blend the color with the texture, false to not |
| BodyPattern | 1 | 3 | 4 | `ICircularPatternFeatureData/BodyPattern.md`；`ICurveDrivenPatternFeatureData/BodyPattern.md`；`ILinearPatternFeatureData/BodyPattern.md`；`ISketchPatternFeatureData/BodyPattern.md` | 否 | 否 | True for bodies and structure systems, false for features and faces |
| Camera | 1 | 1 | 1 | `IModelView/Camera.md` | 否 | 否 | [[Camera]] |
| CanConvertFormat | 1 | 1 | 1 | `IGtol/CanConvertFormat.md` | 否 | 否 | True if can be converted, false if not |
| CircleParams | 1 | 1 | 1 | `ICurve/CircleParams.md` | 否 | 否 | Array of doubles (see **Remarks**) |
| ClearSelectionColors | 1 | 1 | 1 | `ISelectionMgr/ClearSelectionColors.md` | 否 | 否 | 查不到 |
| ClearanceValue | 1 | 1 | 1 | `IClearanceResult/ClearanceValue.md` | 否 | 否 | Clearance value |
| Close | 1 | 1 | 3 | `ILoftFeatureData/Close.md`；`IModelDoc2/Close.md`；`IPropertyManagerPage2/Close.md` | 否 | 否 | True for closed loft features, false for open |
| CloseDoc | 1 | 1 | 1 | `ISldWorks/CloseDoc.md` | 否 | 否 | 查不到 |
| CollectIdenticalBodies | 1 | 1 | 1 | `ICutListSortOptions/CollectIdenticalBodies.md` | 否 | 否 | True to collect identical bodies, false to not |
| CommandInProgress | 1 | 3 | 1 | `ISldWorks/CommandInProgress.md` | 否 | 否 | Set to True before calling the sequence of API calls, then set to false after calling the sequence of API calls |
| Component | 1 | 1 | 4 | `IDrawingComponent/Component.md`；`IMateInPlace/Component.md`；`IMateLoadReference/Component.md`；`IMotionPlotAxisFeatureData/Component.md` | 否 | 否 | Associated [[IComponent2]] object for the referenced assembly document |
| ConvertFormat | 1 | 1 | 1 | `IGtol/ConvertFormat.md` | 否 | 否 | 0 if successfully converted, otherwise error code as defined by [[swGtolFormatConversionError_e]] |
| CoreCavitySplit | 1 | 1 | 1 | `IPartingLineFeatureData/CoreCavitySplit.md` | 否 | 否 | True to enable a core/cavity split, false to not |
| Create3DBoundingBox | 1 | 1 | 1 | `IModelDocExtension/Create3DBoundingBox.md` | 否 | 否 | 查不到 |
| Create3PointArc | 1 | 1 | 2 | `IModelDoc2/Create3PointArc.md`；`ISketchManager/Create3PointArc.md` | 是 | 否 | True if successfully created, false otherwise |
| Create3PointCenterRectangle | 1 | 1 | 1 | `ISketchManager/Create3PointCenterRectangle.md` | 否 | 否 | Array of [[sketch segments]] that represent the edges and diagonals created for this center rectangle |
| Create3PointCornerRectangle | 1 | 1 | 1 | `ISketchManager/Create3PointCornerRectangle.md` | 否 | 否 | Array of [[sketch segments]] that represent the edges created for this corner rectangle |
| CreateArc | 1 | 1 | 3 | `IModelDoc2/CreateArc.md`；`IModeler/CreateArc.md`；`ISketchManager/CreateArc.md` | 是 | 否 | [[Curve]] |
| CreateAutoBalloonOptions | 1 | 1 | 1 | `IDrawingDoc/CreateAutoBalloonOptions.md` | 否 | 否 | [[IAutoBalloonOptions]] |
| CreateAuxiliaryViewAt2 | 1 | 1 | 1 | `IDrawingDoc/CreateAuxiliaryViewAt2.md` | 否 | 否 | Newly created auxiliary view |
| CreateBsplineSurface | 1 | 1 | 2 | `IBody2/CreateBsplineSurface.md`；`IModeler/CreateBsplineSurface.md` | 否 | 否 | A new B-spline surface |
| CreateCenterLine | 1 | 1 | 2 | `IModelDoc2/CreateCenterLine.md`；`ISketchManager/CreateCenterLine.md` | 是 | 否 | True if success, false if not |
| CreateCenterRectangle | 1 | 1 | 1 | `ISketchManager/CreateCenterRectangle.md` | 否 | 否 | Array of [[sketch segments]] that represent the edges and diagonals created for this center rectangle |
| CreateChamfer | 1 | 1 | 1 | `ISketchManager/CreateChamfer.md` | 否 | 否 | [[Sketch segment]] for the chamfer |
| CreateCircleByRadius | 1 | 1 | 2 | `IModelDoc2/CreateCircleByRadius.md`；`ISketchManager/CreateCircleByRadius.md` | 是 | 否 | [[Sketch segment]] for the circle |
| CreateCircularSketchStepAndRepeat | 1 | 1 | 2 | `IModelDoc2/CreateCircularSketchStepAndRepeat.md`；`ISketchManager/CreateCircularSketchStepAndRepeat.md` | 是 | 否 | True if the sketch pattern was created successfully, false otherwise |
| CreateConic | 1 | 1 | 1 | `ISketchManager/CreateConic.md` | 否 | 否 | [[Sketch segment]] for the conic curve |
| CreateConicalSurface | 1 | 1 | 1 | `IModeler/CreateConicalSurface.md` | 是 | 否 | 查不到 |
| CreateCoonsBSurface | 1 | 1 | 1 | `IModeler/CreateCoonsBSurface.md` | 否 | 否 | [[B-surface]] |
| CreateCornerRectangle | 1 | 1 | 1 | `ISketchManager/CreateCornerRectangle.md` | 否 | 否 | Array of [[sketch segments]] that represent the edges created for this corner rectangle |
| CreateCustomBendAllowance | 1 | 1 | 1 | `IFeatureManager/CreateCustomBendAllowance.md` | 否 | 否 | Pointer to the [[ICustomBendAllowance]] object |
| CreateCylindricalSurface | 1 | 1 | 1 | `IModeler/CreateCylindricalSurface.md` | 是 | 否 | 查不到 |
| CreateEllipse | 1 | 1 | 3 | `IModelDoc2/CreateEllipse.md`；`IModeler/CreateEllipse.md`；`ISketchManager/CreateEllipse.md` | 是 | 否 | [[Curve]] |
| CreateEllipticalArc | 1 | 1 | 1 | `ISketchManager/CreateEllipticalArc.md` | 否 | 否 | [[Sketch segment]] for the elliptical arc |
| CreateExtrusionSurface | 1 | 1 | 2 | `IBody2/CreateExtrusionSurface.md`；`IModeler/CreateExtrusionSurface.md` | 否 | 否 | New surface of extrusion (tabulated cylinder) |
| CreateFillet | 1 | 1 | 1 | `ISketchManager/CreateFillet.md` | 否 | 否 | [[Sketch segment]] for the fillet |
| CreateLine | 1 | 1 | 3 | `IModelDoc2/CreateLine.md`；`IModeler/CreateLine.md`；`ISketchManager/CreateLine.md` | 是 | 否 | Newly created [[line]] |
| CreateLinearSketchStepAndRepeat | 1 | 1 | 2 | `IModelDoc2/CreateLinearSketchStepAndRepeat.md`；`ISketchManager/CreateLinearSketchStepAndRepeat.md` | 是 | 否 | True if the sketch pattern was created successfully, false otherwise |
| CreateMassProperty2 | 1 | 1 | 1 | `IModelDocExtension/CreateMassProperty2.md` | 否 | 否 | [[IMassProperty2]] |
| CreateOffsetSurface | 1 | 1 | 2 | `IBody2/CreateOffsetSurface.md`；`IModeler/CreateOffsetSurface.md` | 否 | 否 | Newly created offset surface |
| CreateParabola | 1 | 1 | 1 | `ISketchManager/CreateParabola.md` | 否 | 否 | [[Sketch segment]] for the parabola |
| CreateParallelogram | 1 | 1 | 1 | `ISketchManager/CreateParallelogram.md` | 否 | 否 | Array of [[sketch segments]] for the parallelogram |
| CreatePlanarSurface | 1 | 1 | 2 | `IBody2/CreatePlanarSurface.md`；`IModeler/CreatePlanarSurface.md` | 是 | 否 | New planar surface |
| CreatePolygon | 1 | 1 | 1 | `ISketchManager/CreatePolygon.md` | 否 | 否 | Array of [[sketch segments]] in the polygon |
| CreateRenderMaterial | 1 | 1 | 1 | `IModelDocExtension/CreateRenderMaterial.md` | 否 | 否 | [[Appearance]] |
| CreateRevolutionSurface | 1 | 1 | 1 | `IBody2/CreateRevolutionSurface.md` | 否 | 否 | New surface of revolution |
| CreateRuledSurface | 1 | 1 | 2 | `IBody2/CreateRuledSurface.md`；`IModeler/CreateRuledSurface.md` | 否 | 否 | Pointer to ruled [[surface]] |
| CreateSheetFromSurface | 1 | 1 | 1 | `IModeler/CreateSheetFromSurface.md` | 否 | 否 | Newly created [[body]] |
| CreateSketchSlot | 1 | 1 | 1 | `ISketchManager/CreateSketchSlot.md` | 否 | 否 | [[Sketch slot]] |
| CreateSphericalSurface | 1 | 1 | 1 | `IModeler/CreateSphericalSurface.md` | 是 | 否 | 查不到 |
| CreateSpline2 | 1 | 1 | 1 | `ISketchManager/CreateSpline2.md` | 是 | 否 | [[Sketch segment]] for the spline |
| CreateStructuralMemberGroup | 1 | 1 | 1 | `IFeatureManager/CreateStructuralMemberGroup.md` | 否 | 否 | [[Structural-member group]] |
| CreateSweptSurface | 1 | 1 | 1 | `IModeler/CreateSweptSurface.md` | 否 | 否 | Newly created [[surface]] |
| CreateTangentArc | 1 | 1 | 2 | `IModelDoc2/CreateTangentArc.md`；`ISketchManager/CreateTangentArc.md` | 是 | 否 | [[Sketch segment]] of the tangent arc |
| CreateToroidalSurface | 1 | 1 | 1 | `IModeler/CreateToroidalSurface.md` | 否 | 否 | Untrimmed toroidal [[surface]] |
| CurveDegree | 1 | 1 | 1 | `ISketchSpline/CurveDegree.md` | 否 | 否 | Degree of curve or -1 if not a Bezier curve style spline |
| CurveType | 1 | 1 | 2 | `ICurveParamData/CurveType.md`；`ISketchSpline/CurveType.md` | 否 | 否 | Type of curve as defined in [[swCurveTypes_e]] |
| CustomSizing | 1 | 2 | 2 | `IStraightTapElementData/CustomSizing.md`；`ITaperedTapElementData/CustomSizing.md` | 否 | 否 | Custom sizing as defined in [[swStraightTapHoleCustomSizing_e]] |
| D1Axis | 1 | 1 | 2 | `ILinearPatternFeatureData/D1Axis.md`；`ILocalLinearPatternFeatureData/D1Axis.md` | 否 | 否 | Direction 1 entity: linear [[edge]], [[line]], [[axis]], [[dimension]], planar [[face]], planar [[surface]], conical face, conical surface, circular edge, or reference [[plane]] |
| D1Direction | 1 | 1 | 2 | `ICurveDrivenPatternFeatureData/D1Direction.md`；`ILocalCurvePatternFeatureData/D1Direction.md` | 否 | 否 | Pattern direction entity (see **Remarks**) |
| D1EndCondition | 1 | 1 | 2 | `ILinearPatternFeatureData/D1EndCondition.md`；`ILocalLinearPatternFeatureData/D1EndCondition.md` | 否 | 否 | Spacing of pattern instances in Direction 1 as defined in [[swPatternEndCondition_e]] |
| D1EndConditionDistance | 1 | 1 | 1 | `IBaseFlangeFeatureData/D1EndConditionDistance.md` | 否 | 否 | Distance |
| D1EndRefOffset | 1 | 1 | 2 | `ILinearPatternFeatureData/D1EndRefOffset.md`；`ILocalLinearPatternFeatureData/D1EndRefOffset.md` | 否 | 否 | Offset of last pattern instance from [[ILinearPatternFeatureData::D1EndReference]] |
| D1EndRefReverseOffset | 1 | 1 | 2 | `ILinearPatternFeatureData/D1EndRefReverseOffset.md`；`ILocalLinearPatternFeatureData/D1EndRefReverseOffset.md` | 否 | 否 | True to reverse [[ILinearPatternFeatureData::D1EndRefOffset]] from [[ILinearPatternFeatureData::D1EndReference]], false to not |
| D1EndSeedReference | 1 | 1 | 2 | `ILinearPatternFeatureData/D1EndSeedReference.md`；`ILocalLinearPatternFeatureData/D1EndSeedReference.md` | 否 | 否 | Seed geometry ([[vertex]], [[edge]], [[face]], or [[plane]]) to offset from [[ILinearPatternFeatureData::D1EndReference]] |
| D1EndUseSeedReference | 1 | 1 | 2 | `ILinearPatternFeatureData/D1EndUseSeedReference.md`；`ILocalLinearPatternFeatureData/D1EndUseSeedReference.md` | 否 | 否 | True to offset a pattern seed reference, false to offset a centroid |
| D1EndUseSpacing | 1 | 1 | 2 | `ILinearPatternFeatureData/D1EndUseSpacing.md`；`ILocalLinearPatternFeatureData/D1EndUseSpacing.md` | 否 | 否 | True to use spacing, false to use number of pattern instances in Direction 1 |
| D1FaceNormal | 1 | 1 | 2 | `ICurveDrivenPatternFeatureData/D1FaceNormal.md`；`ILocalCurvePatternFeatureData/D1FaceNormal.md` | 否 | 否 | [[IFace2]] |
| D1IsEqualSpaced | 1 | 1 | 2 | `ICurveDrivenPatternFeatureData/D1IsEqualSpaced.md`；`ILocalCurvePatternFeatureData/D1IsEqualSpaced.md` | 否 | 否 | True spaces the pattern items equally, false does not |
| D1ReverseDirection | 1 | 2 | 4 | `ICurveDrivenPatternFeatureData/D1ReverseDirection.md`；`ILinearPatternFeatureData/D1ReverseDirection.md`；`ILocalCurvePatternFeatureData/D1ReverseDirection.md`；`ILocalLinearPatternFeatureData/D1ReverseDirection.md` | 否 | 否 | True reverses the pattern direction, false does not |
| D1Spacing | 1 | 2 | 4 | `ICurveDrivenPatternFeatureData/D1Spacing.md`；`ILinearPatternFeatureData/D1Spacing.md`；`ILocalCurvePatternFeatureData/D1Spacing.md`；`ILocalLinearPatternFeatureData/D1Spacing.md` | 否 | 否 | Pattern spacing |
| D1TotalInstances | 1 | 1 | 2 | `ILinearPatternFeatureData/D1TotalInstances.md`；`ILocalLinearPatternFeatureData/D1TotalInstances.md` | 否 | 否 | Total number of pattern instances in Direction 1 |
| D2Axis | 1 | 1 | 2 | `ILinearPatternFeatureData/D2Axis.md`；`ILocalLinearPatternFeatureData/D2Axis.md` | 否 | 否 | Direction 2 entity: linear [[edge]], [[line]], [[axis]], [[dimension]], planar [[face]], planar [[surface]], conical face, conical surface, circular edge, or reference [[plane]] |
| D2Direction | 1 | 1 | 2 | `ICurveDrivenPatternFeatureData/D2Direction.md`；`ILocalCurvePatternFeatureData/D2Direction.md` | 否 | 否 | Pattern direction entity |
| D2EndCondition | 1 | 1 | 2 | `ILinearPatternFeatureData/D2EndCondition.md`；`ILocalLinearPatternFeatureData/D2EndCondition.md` | 否 | 否 | Spacing of pattern instances in Direction 2 as defined in [[swPatternEndCondition_e]] |
| D2IsEqualSpaced | 1 | 1 | 2 | `ICurveDrivenPatternFeatureData/D2IsEqualSpaced.md`；`ILocalCurvePatternFeatureData/D2IsEqualSpaced.md` | 否 | 否 | True spaces the pattern items equally, false does not |
| D2PatternSeedOnly | 1 | 2 | 4 | `ICurveDrivenPatternFeatureData/D2PatternSeedOnly.md`；`ILinearPatternFeatureData/D2PatternSeedOnly.md`；`ILocalCurvePatternFeatureData/D2PatternSeedOnly.md`；`ILocalLinearPatternFeatureData/D2PatternSeedOnly.md` | 否 | 否 | True patterns the seed feature only in Direction 2 |
| D2ReverseDirection | 1 | 2 | 4 | `ICurveDrivenPatternFeatureData/D2ReverseDirection.md`；`ILinearPatternFeatureData/D2ReverseDirection.md`；`ILocalCurvePatternFeatureData/D2ReverseDirection.md`；`ILocalLinearPatternFeatureData/D2ReverseDirection.md` | 否 | 否 | True reverses Direction 2, false does not |
| D2Spacing | 1 | 2 | 4 | `ICurveDrivenPatternFeatureData/D2Spacing.md`；`ILinearPatternFeatureData/D2Spacing.md`；`ILocalCurvePatternFeatureData/D2Spacing.md`；`ILocalLinearPatternFeatureData/D2Spacing.md` | 否 | 否 | Pattern spacing |
| D2TotalInstances | 1 | 1 | 2 | `ILinearPatternFeatureData/D2TotalInstances.md`；`ILocalLinearPatternFeatureData/D2TotalInstances.md` | 否 | 否 | Total number of pattern instances in Direction 2 |
| DeSelect2 | 1 | 1 | 1 | `ISelectionMgr/DeSelect2.md` | 否 | 否 | 1 if the specified entity is deselected, 0 if not |
| Delete | 1 | 1 | 5 | `IAttribute/Delete.md`；`IComment/Delete.md`；`ICustomPropertyManager/Delete.md`；`IEquationMgr/Delete.md` …（共 5） | 是 | 否 | True if the attribute is deleted, false if not |
| DeleteAllRelations | 1 | 1 | 2 | `IModelDoc2/DeleteAllRelations.md`；`ISketchRelationManager/DeleteAllRelations.md` | 否 | 否 | True if all of the logical sketch relations are deleted, false if not |
| DeleteColumn | 1 | 1 | 1 | `ITableAnnotation/DeleteColumn.md` | 是 | 否 | True if column is deleted successfully, false if not |
| DeletePoint | 1 | 1 | 1 | `ISketchSpline/DeletePoint.md` | 否 | 否 | True if the point is deleted, false if not |
| DeleteRelation | 1 | 1 | 1 | `ISketchRelationManager/DeleteRelation.md` | 否 | 否 | True if the sketch relation is deleted, false if not |
| DeleteRenderMaterial | 1 | 1 | 1 | `IModelDocExtension/DeleteRenderMaterial.md` | 否 | 否 | True if the appearance is deleted, false if not |
| DeleteRow | 1 | 1 | 1 | `ITableAnnotation/DeleteRow.md` | 是 | 否 | True if the row is deleted successfully, false if not |
| Density | 1 | 1 | 1 | `IMassProperty2/Density.md` | 否 | 否 | Density |
| Description | 1 | 1 | 5 | `IAdvancedSaveAsOptions/Description.md`；`IConfiguration/Description.md`；`IFeature/Description.md`；`ILayer/Description.md` …（共 5） | 否 | 否 | Description |
| Diameter | 1 | 1 | 8 | `IAdvancedHoleElementData/Diameter.md`；`ICosmeticThreadFeatureData/Diameter.md`；`IFillPatternFeatureData/Diameter.md`；`IMeasure/Diameter.md` …（共 8） | 否 | 否 | Diameter of the Advanced Hole |
| Diffuse | 1 | 2 | 2 | `IAppearanceSetting/Diffuse.md`；`IRenderMaterial/Diffuse.md` | 否 | 否 | 0 <= *diffuseness* <= 1 |
| DimensionType | 1 | 1 | 2 | `IDimXpertDimensionTolerance/DimensionType.md`；`IStructureSystemSplitMember/DimensionType.md` | 否 | 否 | Type of this DimXpert dimension tolerance as defined in [[swDimXpertDimensionToleranceType_e]] |
| DisplayMode | 1 | 2 | 3 | `IModelDocExtension/DisplayMode.md`；`IModelView/DisplayMode.md`；`IView3D/DisplayMode.md` | 否 | 否 | Display mode as defined by [[swViewDisplayMode_e]] |
| DisplayZebraStripes | 1 | 1 | 1 | `IModelView/DisplayZebraStripes.md` | 否 | 否 | True to display the zebra stripes, false if not |
| DissolveSubAssembly | 1 | 1 | 1 | `IAssemblyDoc/DissolveSubAssembly.md` | 否 | 否 | True if the subassembly was successfully dissolved, false if not |
| DrillPointAngle | 1 | 1 | 2 | `IStraightElementData/DrillPointAngle.md`；`IStraightTapElementData/DrillPointAngle.md` | 否 | 否 | Drill point angle |
| DrillPointAngleOverride | 1 | 1 | 2 | `IStraightElementData/DrillPointAngleOverride.md`；`IStraightTapElementData/DrillPointAngleOverride.md` | 否 | 否 | True to override the drill point angle, false to not |
| EditAssembly | 1 | 1 | 1 | `IAssemblyDoc/EditAssembly.md` | 否 | 否 | 查不到 |
| EditDelete | 1 | 1 | 1 | `IModelDoc2/EditDelete.md` | 否 | 否 | 查不到 |
| EditPart2 | 1 | 1 | 1 | `IAssemblyDoc/EditPart2.md` | 否 | 否 | swEditPartSuccessful if successful |
| EditRoute | 1 | 1 | 1 | `IModelDoc2/EditRoute.md` | 否 | 否 | 查不到 |
| EditSuppress2 | 1 | 1 | 1 | `IModelDoc2/EditSuppress2.md` | 否 | 否 | True if the selected feature, component, or owning feature of the selected face is suppressed, false if not |
| EditUndo2 | 1 | 1 | 1 | `IModelDoc2/EditUndo2.md` | 否 | 否 | 查不到 |
| EditUnsuppress2 | 1 | 1 | 1 | `IModelDoc2/EditUnsuppress2.md` | 否 | 否 | True if the selected feature or component is unsuppressed, false if not |
| Emission | 1 | 2 | 1 | `IRenderMaterial/Emission.md` | 否 | 否 | Amount of light projected from the appearance |
| EnableContourSelection | 1 | 2 | 1 | `ISelectionMgr/EnableContourSelection.md` | 否 | 否 | True to enable contour selection, false to disable it |
| EnableGraphicsUpdate | 1 | 1 | 1 | `IModelView/EnableGraphicsUpdate.md` | 否 | 否 | True to refresh the model view, false to not |
| EnableSelection | 1 | 2 | 1 | `ISelectionMgr/EnableSelection.md` | 否 | 否 | True if selection is enabled, false if disabled |
| EndConditionOverride | 1 | 1 | 3 | `ICounterboreElementData/EndConditionOverride.md`；`ICountersinkElementData/EndConditionOverride.md`；`ITaperedTapElementData/EndConditionOverride.md` | 否 | 否 | True to override the end condition, false to not (see **Remarks**) |
| EndShape | 1 | 1 | 2 | `IStraightElementData/EndShape.md`；`IStraightTapElementData/EndShape.md` | 否 | 否 | End shape as defined in [[swEndShape_e]] |
| EntitiesToMate | 1 | 1 | 17 | `IAngleMateFeatureData/EntitiesToMate.md`；`ICamFollowerMateFeatureData/EntitiesToMate.md`；`ICoincidentMateFeatureData/EntitiesToMate.md`；`IConcentricMateFeatureData/EntitiesToMate.md` …（共 17） | 否 | 否 | Array of entities to mate (see **Remarks**) |
| ErrorStatus | 1 | 1 | 1 | `IMateFeatureData/ErrorStatus.md` | 否 | 否 | Status of adding or editing this mate as defined in [[swAddMateError_e]] |
| EvaluateAll | 1 | 1 | 1 | `IEquationMgr/EvaluateAll.md` | 否 | 否 | -1 for both success and failure |
| FaceInSurfaceSense | 1 | 1 | 1 | `IFace2/FaceInSurfaceSense.md` | 否 | 否 | True if face normal and surface normal are in the opposite direction, false if they are in same direction |
| FeatureBossThicken | 1 | 1 | 2 | `IFeatureManager/FeatureBossThicken.md`；`IModelDoc2/FeatureBossThicken.md` | 是 | 否 | Pointer to the [[IFeature]] object |
| FeatureByPositionReverse | 1 | 1 | 1 | `IModelDoc2/FeatureByPositionReverse.md` | 否 | 否 | Pointer to the *n*th from last [[feature]] in the document |
| FeatureExtruRefSurface3 | 1 | 1 | 1 | `IFeatureManager/FeatureExtruRefSurface3.md` | 否 | 否 | 查不到 |
| FeatureLinearPattern5 | 1 | 1 | 1 | `IFeatureManager/FeatureLinearPattern5.md` | 是 | 否 | Linear pattern [[feature]] |
| FeatureScope | 1 | 1 | 15 | `IBoundaryBossFeatureData/FeatureScope.md`；`ICircularPatternFeatureData/FeatureScope.md`；`ICurveDrivenPatternFeatureData/FeatureScope.md`；`IExtrudeFeatureData2/FeatureScope.md` …（共 15） | 否 | 否 | True if only the [[specified bodies]] in the multibody part are affected by the boundary feature, false if all of the bodies in the multibody part are affected by the boundary feature |
| FileName | 1 | 1 | 6 | `IDesignTable/FileName.md`；`IDocumentSpecification/FileName.md`；`IRenderMaterial/FileName.md`；`ISaveTo3DExperienceOptions/FileName.md` …（共 6） | 否 | 否 | Full path and filename for the Microsoft Excel file |
| FixComponent | 1 | 1 | 1 | `IAssemblyDoc/FixComponent.md` | 否 | 否 | 查不到 |
| FlipDimension | 1 | 1 | 4 | `IAngleMateFeatureData/FlipDimension.md`；`IDistanceMateFeatureData/FlipDimension.md`；`IProfileCenterMateFeatureData/FlipDimension.md`；`IWidthMateFeatureData/FlipDimension.md` | 否 | 否 | True to flip the dimension, false to not |
| ForceRebuild3 | 1 | 1 | 1 | `IModelDoc2/ForceRebuild3.md` | 否 | 否 | True if all features in the active configuration at the specified assembly level in the model are rebuilt, false if not |
| FrameHeight | 1 | 2 | 2 | `IModelView/FrameHeight.md`；`ISldWorks/FrameHeight.md` | 否 | 否 | Height of document window in client area in pixels |
| FrameLeft | 1 | 2 | 2 | `IModelView/FrameLeft.md`；`ISldWorks/FrameLeft.md` | 否 | 否 | Left position of document window in client area in pixels |
| FrameState | 1 | 1 | 2 | `IModelView/FrameState.md`；`ISldWorks/FrameState.md` | 否 | 否 | Window state as defined in [[swWindowState_e]] |
| FrameTop | 1 | 2 | 2 | `IModelView/FrameTop.md`；`ISldWorks/FrameTop.md` | 否 | 否 | Top position of document window in client area in pixels |
| FrameWidth | 1 | 2 | 2 | `IModelView/FrameWidth.md`；`ISldWorks/FrameWidth.md` | 否 | 否 | Width of document window in client area in pixels |
| FullName | 1 | 1 | 1 | `IDimension/FullName.md` | 否 | 否 | Name of the dimension including the feature and model |
| FullyDefineSketch | 1 | 1 | 1 | `ISketchManager/FullyDefineSketch.md` | 否 | 否 | Not currently defined |
| GeometryPattern | 1 | 3 | 7 | `ICircularPatternFeatureData/GeometryPattern.md`；`ICurveDrivenPatternFeatureData/GeometryPattern.md`；`IFillPatternFeatureData/GeometryPattern.md`；`ILinearPatternFeatureData/GeometryPattern.md` …（共 7） | 否 | 否 | True to use only the geometry of the feature to create the pattern (faster), false to pattern and solve each instance of the feature in its entirety (slower) |
| Get3DExperienceType | 1 | 1 | 1 | `IConfiguration/Get3DExperienceType.md` | 否 | 否 | Type of 3DEXPERIENCE configuration as defined in [[sw3DExperienceCfgType_e]] |
| GetActiveSketch2 | 1 | 1 | 1 | `IModelDoc2/GetActiveSketch2.md` | 是 | 否 | Active [[sketch]] |
| GetAddInObject | 1 | 2 | 1 | `ISldWorks/GetAddInObject.md` | 否 | 否 | Your add-in object |
| GetAllowedRelations | 1 | 1 | 1 | `ISketchRelationManager/GetAllowedRelations.md` | 否 | 否 | Array of sketch relation types valid for the specified entities as defined in [[swConstraintType_e]] |
| GetArcCount | 1 | 1 | 10 | `IDatumTag/GetArcCount.md`；`IDatumTargetSym/GetArcCount.md`；`IDisplayData/GetArcCount.md`；`IGtol/GetArcCount.md` …（共 10） | 否 | 否 | Number of arcs |
| GetArcs2 | 1 | 1 | 2 | `ISketch/GetArcs2.md`；`IView/GetArcs2.md` | 是 | 否 | Array of doubles containing the arcs in the sketch (see **Remarks**) |
| GetAutomaticSolve | 1 | 1 | 1 | `ISketch/GetAutomaticSolve.md` | 否 | 否 | True if automatic solving is on, false if off |
| GetBodies | 1 | 1 | 4 | `IBodyFolder/GetBodies.md`；`IComponent2/GetBodies.md`；`IPartDoc/GetBodies.md`；`IPartExplodeStep/GetBodies.md` | 是 | 否 | Array of [[IBody2]] objects |
| GetBreakLines | 1 | 1 | 1 | `IView/GetBreakLines.md` | 否 | 否 | [[Breaks]] in this view |
| GetCavitySurfacesCount | 1 | 1 | 1 | `IToolingSplitFeatureData/GetCavitySurfacesCount.md` | 否 | 否 | Number of cavity surface bodies |
| GetConfigurationNames | 1 | 1 | 3 | `IComponent2/GetConfigurationNames.md`；`IModelDoc2/GetConfigurationNames.md`；`ISldWorks/GetConfigurationNames.md` | 否 | 否 | Array of configuration names |
| GetConstrainedStatus | 1 | 1 | 2 | `IComponent2/GetConstrainedStatus.md`；`ISketch/GetConstrainedStatus.md` | 否 | 否 | Constrained status as defined in [[swConstrainedStatus_e]] |
| GetContourEdges | 1 | 1 | 1 | `ISketch/GetContourEdges.md` | 否 | 否 | Array of [[edges]] |
| GetContoursCount | 1 | 1 | 3 | `IExtrudeFeatureData2/GetContoursCount.md`；`IRevolveFeatureData2/GetContoursCount.md`；`ISplitLineFeatureData/GetContoursCount.md` | 否 | 否 | Number of selected contours |
| GetCoordinateSystem | 1 | 1 | 1 | `ICoordinateSystemElement/GetCoordinateSystem.md` | 否 | 否 | [[IFeature]] |
| GetCoreSurfacesCount | 1 | 1 | 1 | `IToolingSplitFeatureData/GetCoreSurfacesCount.md` | 否 | 否 | Number of core surface bodies |
| GetCostingManager | 1 | 1 | 1 | `IModelDocExtension/GetCostingManager.md` | 否 | 否 | [[ICostManager]] |
| GetCount | 1 | 1 | 3 | `IColorTable/GetCount.md`；`IEquationMgr/GetCount.md`；`ILayerMgr/GetCount.md` | 否 | 否 | Number of colors defined in the color table |
| GetCurrentSheet | 1 | 2 | 1 | `IDrawingDoc/GetCurrentSheet.md` | 否 | 否 | Sheet |
| GetCurve | 1 | 1 | 4 | `ICoEdge/GetCurve.md`；`IEdge/GetCurve.md`；`ISilhouetteEdge/GetCurve.md`；`ISketchSegment/GetCurve.md` | 否 | 否 | Curve that is attached to this coedge (see **Remarks**) |
| GetCutListItems | 1 | 1 | 1 | `IConfiguration/GetCutListItems.md` | 否 | 否 | Array of [[ICutListItem]]s |
| GetDependencies | 1 | 1 | 2 | `IModelDoc2/GetDependencies.md`；`IModelDocExtension/GetDependencies.md` | 是 | 否 | Array of strings (see **Remarks**) |
| GetDepth | 1 | 1 | 2 | `IExtrudeFeatureData2/GetDepth.md`；`ISurfExtrudeFeatureData/GetDepth.md` | 否 | 否 | Depth of the extrusion |
| GetDetachSegmentOnDrag | 1 | 1 | 1 | `ISketch/GetDetachSegmentOnDrag.md` | 否 | 否 | True if **Detach Segment on Drag** is selected, false if not |
| GetDisplayDimensions | 1 | 1 | 3 | `IMacroFeatureData/GetDisplayDimensions.md`；`ISketchBlockDefinition/GetDisplayDimensions.md`；`IView/GetDisplayDimensions.md` | 否 | 否 | Array of [[display dimensions]] |
| GetDocumentNamesCount | 1 | 1 | 1 | `IPackAndGo/GetDocumentNamesCount.md` | 否 | 否 | Number of documents comprising the model |
| GetEdgeCount | 1 | 1 | 7 | `IBody2/GetEdgeCount.md`；`IChamferFeatureData2/GetEdgeCount.md`；`IEdgeFlangeFeatureData/GetEdgeCount.md`；`IFace2/GetEdgeCount.md` …（共 7） | 否 | 否 | Number of edges |
| GetEllipses3 | 1 | 1 | 2 | `ISketch/GetEllipses3.md`；`IView/GetEllipses3.md` | 是 | 否 | Array of doubles (see **Remarks**) |
| GetEndCondition | 1 | 1 | 2 | `IExtrudeFeatureData2/GetEndCondition.md`；`ISurfExtrudeFeatureData/GetEndCondition.md` | 否 | 否 | End condition type as defined in [[swEndConditions_e]] |
| GetEndPoint2 | 1 | 1 | 4 | `ISketchArc/GetEndPoint2.md`；`ISketchEllipse/GetEndPoint2.md`；`ISketchLine/GetEndPoint2.md`；`ISketchParabola/GetEndPoint2.md` | 否 | 否 | [[Sketch point]] |
| GetEndVertex | 1 | 1 | 1 | `IEdge/GetEndVertex.md` | 否 | 否 | Vertex |
| GetEntitiesCount | 1 | 1 | 5 | `IBreakCornerFeatureData/GetEntitiesCount.md`；`IRenderMaterial/GetEntitiesCount.md`；`ISketchRelation/GetEntitiesCount.md`；`ISurfaceKnitFeatureData/GetEntitiesCount.md` …（共 5） | 否 | 否 | Number of faces or edges |
| GetEntityParamsSize | 1 | 1 | 1 | `IMateEntity2/GetEntityParamsSize.md` | 否 | 否 | Number of parameters for this mate entity |
| GetEquationMgr | 1 | 1 | 1 | `IModelDoc2/GetEquationMgr.md` | 否 | 否 | [[Equation manager]] |
| GetExcludeFromBOM2 | 1 | 1 | 1 | `IComponent2/GetExcludeFromBOM2.md` | 否 | 否 | Array of values indicating whether this component is: |
| GetFastenerTable | 1 | 2 | 1 | `IHoleStandardsData/GetFastenerTable.md` | 否 | 否 | True if fastener data table successfully retrieved, false if not |
| GetFastenerTableTypes | 1 | 2 | 1 | `IHoleStandardsData/GetFastenerTableTypes.md` | 否 | 否 | True if the fastener table type IDs are successfully retrieved, false if not |
| GetFastenerTypes | 1 | 2 | 1 | `IHoleStandardsData/GetFastenerTypes.md` | 否 | 否 | True if fastener types successfully retrieved, false if not |
| GetFeature | 1 | 2 | 28 | `IBendTable/GetFeature.md`；`IBodyFolder/GetFeature.md`；`IBomFeature/GetFeature.md`；`ICommentFolder/GetFeature.md` …（共 28） | 否 | 否 | [[IFeature]] |
| GetFeatureCount | 1 | 1 | 6 | `IBody2/GetFeatureCount.md`；`IDimXpertPart/GetFeatureCount.md`；`IFeatureFolder/GetFeatureCount.md`；`IFeatureManager/GetFeatureCount.md` …（共 6） | 否 | 否 | Number of features in this body |
| GetFrame | 1 | 1 | 1 | `IGtol/GetFrame.md` | 否 | 否 | [[IGtolFrame]] |
| GetFrameCount | 1 | 2 | 2 | `IGtol/GetFrameCount.md`；`IPMIGtolData/GetFrameCount.md` | 否 | 否 | Number of frames in this GTol symbol |
| GetHoleStandards | 1 | 3 | 1 | `IHoleStandardsData/GetHoleStandards.md` | 否 | 否 | True if Hole Wizard standards retrieved successfully, false if not |
| GetHoleStandardsData | 1 | 1 | 1 | `ISldWorks/GetHoleStandardsData.md` | 否 | 否 | [[IHoleStandardsData]]; null if HoleTypeID is 5 (swWzdLegacy) |
| GetInterferenceCount | 1 | 1 | 1 | `IInterferenceDetectionMgr/GetInterferenceCount.md` | 否 | 否 | Number of interferences |
| GetInterferences | 1 | 1 | 1 | `IInterferenceDetectionMgr/GetInterferences.md` | 否 | 否 | Array of the [[interferences]] |
| GetLastFeatureAdded | 1 | 1 | 1 | `IModelDocExtension/GetLastFeatureAdded.md` | 否 | 否 | [[Feature]] |
| GetLightWeightComponentCount | 1 | 1 | 1 | `IAssemblyDoc/GetLightWeightComponentCount.md` | 否 | 否 | Number of lightweight components |
| GetLines2 | 1 | 1 | 2 | `ISketch/GetLines2.md`；`IView/GetLines2.md` | 是 | 否 | Array of doubles (see **Remarks**) |
| GetMassProperties | 1 | 1 | 4 | `IBody2/GetMassProperties.md`；`IModelDoc2/GetMassProperties.md`；`IModelDocExtension/GetMassProperties.md`；`ISldWorks/GetMassProperties.md` | 是 | 否 | Array of objects (see **Remarks**) |
| GetMateEntityCount | 1 | 1 | 2 | `IMate2/GetMateEntityCount.md`；`IMateInPlace/GetMateEntityCount.md` | 否 | 否 | Number of entities for this mate |
| GetModelDoc | 1 | 1 | 3 | `IComponent2/GetModelDoc.md`；`IDerivedPartFeatureData/GetModelDoc.md`；`IMirrorPartFeatureData/GetModelDoc.md` | 是 | 否 | [[Model document]] |
| GetModeler | 1 | 1 | 1 | `ISldWorks/GetModeler.md` | 否 | 否 | [[IModeler]] |
| GetMotionStudyManager | 1 | 1 | 1 | `IModelDocExtension/GetMotionStudyManager.md` | 否 | 否 | [[MotionManager]] |
| GetMultipleThicknessAtIndex | 1 | 1 | 1 | `IShellFeatureData/GetMultipleThicknessAtIndex.md` | 否 | 否 | Shell thickness |
| GetNext | 1 | 1 | 22 | `IAnnotation/GetNext.md`；`ICThread/GetNext.md`；`ICenterLine/GetNext.md`；`ICenterMark/GetNext.md` …（共 22） | 是 | 否 | Next [[centerline]] in this drawing view |
| GetOverrideOptions | 1 | 1 | 1 | `IMassProperty2/GetOverrideOptions.md` | 否 | 否 | [[IMassPropertyOverrideOptions]] |
| GetPackAndGo | 1 | 1 | 1 | `IModelDocExtension/GetPackAndGo.md` | 否 | 否 | [[IPackAndGo]] object |
| GetParabolas2 | 1 | 1 | 2 | `ISketch/GetParabolas2.md`；`IView/GetParabolas2.md` | 否 | 否 | Array of doubles (see **Remarks**) |
| GetPartBox | 1 | 1 | 1 | `IPartDoc/GetPartBox.md` | 否 | 否 | Array of 6 doubles containing the 2 diagonal points that bound the part |
| GetPartingLinesCount | 1 | 1 | 3 | `IDraftFeatureData2/GetPartingLinesCount.md`；`IPartingLineFeatureData/GetPartingLinesCount.md`；`IPartingSurfaceFeatureData/GetPartingLinesCount.md` | 否 | 否 | Number of parting lines |
| GetPartingSurfacesCount | 1 | 1 | 1 | `IToolingSplitFeatureData/GetPartingSurfacesCount.md` | 否 | 否 | Number of parting surface bodies |
| GetPatternBodyCount | 1 | 1 | 6 | `ICircularPatternFeatureData/GetPatternBodyCount.md`；`ICurveDrivenPatternFeatureData/GetPatternBodyCount.md`；`ILinearPatternFeatureData/GetPatternBodyCount.md`；`IMirrorSolidFeatureData/GetPatternBodyCount.md` …（共 6） | 否 | 否 | Number of seed bodies |
| GetPatternFaceCount | 1 | 1 | 5 | `ICircularPatternFeatureData/GetPatternFaceCount.md`；`ICurveDrivenPatternFeatureData/GetPatternFaceCount.md`；`ILinearPatternFeatureData/GetPatternFaceCount.md`；`ISketchPatternFeatureData/GetPatternFaceCount.md` …（共 5） | 否 | 否 | Number of patterned faces |
| GetPatternFeatureCount | 1 | 1 | 6 | `ICircularPatternFeatureData/GetPatternFeatureCount.md`；`ICurveDrivenPatternFeatureData/GetPatternFeatureCount.md`；`ILinearPatternFeatureData/GetPatternFeatureCount.md`；`IMirrorPatternFeatureData/GetPatternFeatureCount.md` …（共 6） | 否 | 否 | Number of seed features |
| GetPoint | 1 | 2 | 1 | `IVertex/GetPoint.md` | 否 | 否 | Array of three doubles representing the x, y, and z coordinates of the point |
| GetPointCount | 1 | 1 | 4 | `IDisplayData/GetPointCount.md`；`IFreePointCurveFeatureData/GetPointCount.md`；`ISketchSpline/GetPointCount.md`；`ITablePatternFeatureData/GetPointCount.md` | 否 | 否 | Number of points |
| GetPoints | 1 | 2 | 2 | `IPrimaryMemberPointLengthFeatureData/GetPoints.md`；`ISketchSpline/GetPoints.md` | 是 | 否 | Array of [[IVertex]]es, [[ISketchPoint]]s, and/or [[IRefPoint]]s |
| GetPolylines | 1 | 1 | 2 | `ISketch/GetPolylines.md`；`IView/GetPolylines.md` | 是 | 否 | 查不到 |
| GetProcessID | 1 | 3 | 1 | `ISldWorks/GetProcessID.md` | 否 | 否 | Process ID |
| GetProperties2 | 1 | 1 | 1 | `ISheet/GetProperties2.md` | 否 | 否 | Array of doubles (see **Remarks**) |
| GetRelationType | 1 | 1 | 1 | `ISketchRelation/GetRelationType.md` | 否 | 否 | Type of sketch relation as defined in [[swConstraintType_e]] |
| GetRenderMaterials2 | 1 | 1 | 2 | `IComponent2/GetRenderMaterials2.md`；`IModelDocExtension/GetRenderMaterials2.md` | 否 | 否 | Array of [[appearances]] |
| GetRenderMaterialsCount2 | 1 | 1 | 2 | `IComponent2/GetRenderMaterialsCount2.md`；`IModelDocExtension/GetRenderMaterialsCount2.md` | 否 | 否 | Number of appearances |
| GetSelectedObjectMark | 1 | 1 | 1 | `ISelectionMgr/GetSelectedObjectMark.md` | 否 | 否 | Number used as a mark for the selected item; this number is used by certain API functions that require ordered entity selection |
| GetSelectedObjectType2 | 1 | 1 | 1 | `ISelectionMgr/GetSelectedObjectType2.md` | 是 | 否 | 查不到 |
| GetSelectedObjectsComponent3 | 1 | 1 | 1 | `ISelectionMgr/GetSelectedObjectsComponent3.md` | 是 | 否 | [[Component]] |
| GetSelectedObjectsDrawingView2 | 1 | 1 | 1 | `ISelectionMgr/GetSelectedObjectsDrawingView2.md` | 否 | 否 | [[Drawing view]] |
| GetSelectedObjectsFace | 1 | 1 | 1 | `ISelectionMgr/GetSelectedObjectsFace.md` | 否 | 否 | [[Face]] |
| GetSelectionPoint2 | 1 | 1 | 1 | `ISelectionMgr/GetSelectionPoint2.md` | 否 | 否 | Array of 3 doubles (x,y,z) |
| GetSelectionPointInSketchSpace2 | 1 | 1 | 1 | `ISelectionMgr/GetSelectionPointInSketchSpace2.md` | 否 | 否 | Array of 3 doubles (x,y,z) |
| GetSensorValue | 1 | 1 | 1 | `ISensor/GetSensorValue.md` | 否 | 否 | True if successful, false if not |
| GetSheetCount | 1 | 1 | 1 | `IDrawingDoc/GetSheetCount.md` | 否 | 否 | Number of drawing sheets in the drawing |
| GetSheetFormatName | 1 | 1 | 1 | `ISheet/GetSheetFormatName.md` | 否 | 否 | Name of the sheet format |
| GetSketchBlockInstances | 1 | 1 | 1 | `ISketch/GetSketchBlockInstances.md` | 否 | 否 | Array containing the [[block instances]] in this sketch |
| GetSketchHatches | 1 | 1 | 1 | `ISketch/GetSketchHatches.md` | 否 | 否 | Array of [[sketch hatches]] |
| GetSketchPaths | 1 | 1 | 2 | `ISketch/GetSketchPaths.md`；`ISketchSegment/GetSketchPaths.md` | 否 | 否 | Array of [[sketch paths]] |
| GetSketchPictures | 1 | 1 | 2 | `ISketch/GetSketchPictures.md`；`IView/GetSketchPictures.md` | 否 | 否 | Array of [[pictures]] on this sketch |
| GetSketchPointCount | 1 | 1 | 1 | `IWizardHoleFeatureData2/GetSketchPointCount.md` | 否 | 否 | Number of center-hole sketch points |
| GetSketchPoints2 | 1 | 1 | 1 | `ISketch/GetSketchPoints2.md` | 否 | 否 | Array of [[sketch points]] in this sketch |
| GetSketchSlots | 1 | 1 | 1 | `ISketch/GetSketchSlots.md` | 否 | 否 | Array of [[sketch slots]] |
| GetSkippedItemCount | 1 | 1 | 9 | `ICircularPatternFeatureData/GetSkippedItemCount.md`；`ICurveDrivenPatternFeatureData/GetSkippedItemCount.md`；`IDerivedPatternFeatureData/GetSkippedItemCount.md`；`ILinearPatternFeatureData/GetSkippedItemCount.md` …（共 9） | 否 | 否 | Number of skipped items |
| GetSplines | 1 | 1 | 3 | `ISketch/GetSplines.md`；`ISketchBlockDefinition/GetSplines.md`；`IView/GetSplines.md` | 是 | 否 | Array of doubles (see **Remarks**) |
| GetStartPoint2 | 1 | 1 | 4 | `ISketchArc/GetStartPoint2.md`；`ISketchEllipse/GetStartPoint2.md`；`ISketchLine/GetStartPoint2.md`；`ISketchParabola/GetStartPoint2.md` | 否 | 否 | [[Sketch point]] |
| GetStartVertex | 1 | 1 | 1 | `IEdge/GetStartVertex.md` | 否 | 否 | Vertex |
| GetSuppression | 1 | 1 | 1 | `IComponent2/GetSuppression.md` | 是 | 否 | Suppression state of this component instance as defined in [[swComponentSuppressionState_e]] |
| GetTemplateName | 1 | 1 | 1 | `ISheet/GetTemplateName.md` | 否 | 否 | Template path name |
| GetType2 | 1 | 2 | 1 | `ICustomPropertyManager/GetType2.md` | 否 | 否 | Type of custom property as defined in [[swCustomInfoType_e]] |
| GetUnits | 1 | 1 | 2 | `IDisplayDimension/GetUnits.md`；`IModelDoc2/GetUnits.md` | 否 | 否 | Units for this display dimension as defined in [[swLengthUnit_e]] or [[swAngleUnit_e]] (see **Remarks**) |
| GetUserPoints2 | 1 | 1 | 2 | `ISketch/GetUserPoints2.md`；`IView/GetUserPoints2.md` | 否 | 否 | Array of doubles (see **Remarks**) |
| GetUserPreferenceInteger | 1 | 1 | 1 | `IModelDocExtension/GetUserPreferenceInteger.md` | 否 | 否 | Value of UserPref |
| GetUserPreferenceIntegerValue | 1 | 1 | 2 | `IModelDoc2/GetUserPreferenceIntegerValue.md`；`ISldWorks/GetUserPreferenceIntegerValue.md` | 是 | 否 | Numeric value associated with the specified UserPreferenceValue |
| GetUserPreferenceToggle | 1 | 1 | 3 | `IModelDoc2/GetUserPreferenceToggle.md`；`IModelDocExtension/GetUserPreferenceToggle.md`；`ISldWorks/GetUserPreferenceToggle.md` | 是 | 否 | True if the item specified by UserPreferenceToggle is currently toggled on, false if the item is currently toggled off |
| GetVisibleComponentCount | 1 | 1 | 1 | `IView/GetVisibleComponentCount.md` | 否 | 否 | Number of visible components |
| GetWhatsWrong | 1 | 1 | 1 | `IModelDocExtension/GetWhatsWrong.md` | 否 | 否 | True if this method runs successfully, false if not |
| GetWhatsWrongCount | 1 | 1 | 1 | `IModelDocExtension/GetWhatsWrongCount.md` | 否 | 否 | Number of items in the What's Wrong dialog |
| HasLegacyCustomProperties | 1 | 1 | 1 | `IModelDocExtension/HasLegacyCustomProperties.md` | 否 | 否 | True if the model has legacy custom properties, false if not |
| HasPerspective | 1 | 1 | 1 | `IModelView/HasPerspective.md` | 否 | 否 | True if the view currently has perspective viewing turned on, false otherwise |
| HasUnloadedComponents | 1 | 1 | 2 | `IAssemblyDoc/HasUnloadedComponents.md`；`IComponent2/HasUnloadedComponents.md` | 否 | 否 | True if the assembly has hidden or suppressed unloaded components, false if not |
| HlrQuality | 1 | 1 | 1 | `IModelView/HlrQuality.md` | 否 | 否 | Type of HLR done as defined in [[swHlrQuality_e]] |
| HoleWizard5 | 1 | 1 | 1 | `IFeatureManager/HoleWizard5.md` | 否 | 否 | [[Feature]] |
| InitializeShading | 1 | 1 | 1 | `IModelView/InitializeShading.md` | 否 | 否 | 查不到 |
| InsertBreak3 | 1 | 1 | 1 | `IView/InsertBreak3.md` | 否 | 否 | [[Break line]] |
| InsertCenterOfMass | 1 | 1 | 1 | `IFeatureManager/InsertCenterOfMass.md` | 否 | 否 | [[IFeature]] |
| InsertChainDimensions | 1 | 1 | 1 | `IModelDocExtension/InsertChainDimensions.md` | 否 | 否 | Array of [[IDisplayDimension]]s |
| InsertCompositeCurve | 1 | 1 | 1 | `IModelDoc2/InsertCompositeCurve.md` | 否 | 否 | 查不到 |
| InsertCoordinateSystem | 1 | 1 | 2 | `IFeatureManager/InsertCoordinateSystem.md`；`IModelDoc2/InsertCoordinateSystem.md` | 是 | 否 | [[Feature]] |
| InsertCosmeticThread3 | 1 | 1 | 1 | `IFeatureManager/InsertCosmeticThread3.md` | 否 | 否 | [[IFeature]] |
| InsertCurveFileBegin | 1 | 1 | 1 | `IModelDoc2/InsertCurveFileBegin.md` | 否 | 否 | 查不到 |
| InsertCurveFileEnd | 1 | 1 | 1 | `IModelDoc2/InsertCurveFileEnd.md` | 否 | 否 | True if curve is created successfully, false if not |
| InsertCurveFilePoint | 1 | 1 | 1 | `IModelDoc2/InsertCurveFilePoint.md` | 否 | 否 | True if this call is successful, false if not |
| InsertCutBlend | 1 | 1 | 2 | `IFeatureManager/InsertCutBlend.md`；`IModelDoc2/InsertCutBlend.md` | 是 | 否 | [[Feature]] |
| InsertCutSurface | 1 | 1 | 2 | `IFeatureManager/InsertCutSurface.md`；`IModelDoc2/InsertCutSurface.md` | 是 | 否 | Surface-cut [[feature]] |
| InsertDatumTag2 | 1 | 1 | 1 | `IModelDoc2/InsertDatumTag2.md` | 否 | 否 | Newly created [[datum tag]] |
| InsertDeleteFace | 1 | 1 | 2 | `IModelDoc2/InsertDeleteFace.md`；`IModelDocExtension/InsertDeleteFace.md` | 是 | 否 | True if a DeleteFace feature is inserted, false if not |
| InsertDome | 1 | 1 | 1 | `IModelDoc2/InsertDome.md` | 否 | 否 | 查不到 |
| InsertEndCapFeature3 | 1 | 1 | 1 | `IFeatureManager/InsertEndCapFeature3.md` | 否 | 否 | [[IFeature]] |
| InsertExtendSurface | 1 | 1 | 1 | `IModelDoc2/InsertExtendSurface.md` | 否 | 否 | 查不到 |
| InsertFillSurface2 | 1 | 1 | 1 | `IFeatureManager/InsertFillSurface2.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| InsertFlattenSurface2 | 1 | 1 | 1 | `IFeatureManager/InsertFlattenSurface2.md` | 否 | 否 | Surface-flatten [[feature]] |
| InsertGlobalBoundingBox2 | 1 | 1 | 1 | `IFeatureManager/InsertGlobalBoundingBox2.md` | 否 | 否 | [[IFeature]] |
| InsertGtol | 1 | 1 | 2 | `IDimXpertPart/InsertGtol.md`；`IModelDoc2/InsertGtol.md` | 否 | 否 | [[IDimXpertAnnotation]] |
| InsertGussetFeature3 | 1 | 1 | 1 | `IFeatureManager/InsertGussetFeature3.md` | 否 | 否 | [[IFeature]] |
| InsertLoftRefSurface2 | 1 | 1 | 1 | `IModelDoc2/InsertLoftRefSurface2.md` | 否 | 否 | 查不到 |
| InsertMateReference2 | 1 | 1 | 1 | `IFeatureManager/InsertMateReference2.md` | 否 | 否 | [[IFeature]] |
| InsertMidSurface | 1 | 1 | 1 | `IFeatureManager/InsertMidSurface.md` | 否 | 否 | Newly created [[midsurface feature]] |
| InsertMoldCoreCavitySolids | 1 | 1 | 1 | `IFeatureManager/InsertMoldCoreCavitySolids.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| InsertMoldPartingLine | 1 | 1 | 1 | `IFeatureManager/InsertMoldPartingLine.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| InsertMoldPartingSurface | 1 | 1 | 1 | `IFeatureManager/InsertMoldPartingSurface.md` | 否 | 否 | Pointer to [[IFeature]] object |
| InsertMoldShutOffSurface | 1 | 1 | 1 | `IFeatureManager/InsertMoldShutOffSurface.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| InsertProtrusionBlend2 | 1 | 1 | 2 | `IFeatureManager/InsertProtrusionBlend2.md`；`IModelDoc2/InsertProtrusionBlend2.md` | 是 | 否 | [[IFeature]] |
| InsertRefPlane | 1 | 1 | 1 | `IFeatureManager/InsertRefPlane.md` | 否 | 否 | [[Reference plane]] |
| InsertReferencePoint | 1 | 1 | 1 | `IFeatureManager/InsertReferencePoint.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| InsertRevolvedRefSurface | 1 | 1 | 2 | `IFeatureManager/InsertRevolvedRefSurface.md`；`IModelDoc2/InsertRevolvedRefSurface.md` | 是 | 否 | Pointer to [[IFeature]] object |
| InsertRib | 1 | 1 | 2 | `IFeatureManager/InsertRib.md`；`IModelDoc2/InsertRib.md` | 是 | 否 | 查不到 |
| InsertSewRefSurface | 1 | 1 | 2 | `IFeatureManager/InsertSewRefSurface.md`；`IModelDoc2/InsertSewRefSurface.md` | 是 | 否 | [[Feature]] |
| InsertSheetMetalClosedCorner | 1 | 1 | 1 | `IModelDoc2/InsertSheetMetalClosedCorner.md` | 否 | 否 | 查不到 |
| InsertSheetMetalMiterFlange | 1 | 1 | 2 | `IFeatureManager/InsertSheetMetalMiterFlange.md`；`IModelDoc2/InsertSheetMetalMiterFlange.md` | 是 | 否 | Pointer to the [[IFeature]] object or NULL |
| InsertSplitLineProject | 1 | 1 | 1 | `IModelDoc2/InsertSplitLineProject.md` | 否 | 否 | 查不到 |
| InsertSplitLineSil | 1 | 1 | 1 | `IModelDoc2/InsertSplitLineSil.md` | 否 | 否 | 查不到 |
| InsertStructuralWeldment5 | 1 | 1 | 1 | `IFeatureManager/InsertStructuralWeldment5.md` | 否 | 否 | Structural weldment [[feature]] |
| InsertSubWeldFolder2 | 1 | 1 | 1 | `IFeatureManager/InsertSubWeldFolder2.md` | 否 | 否 | [[IFeature]] |
| InsertSurfaceFinishSymbol3 | 1 | 1 | 1 | `IModelDocExtension/InsertSurfaceFinishSymbol3.md` | 否 | 否 | Newly inserted [[surface finish symbol]] |
| InsertWeldmentCutList2 | 1 | 2 | 1 | `IFeatureManager/InsertWeldmentCutList2.md` | 否 | 否 | [[IFeature]] |
| InsertWeldmentFeature | 1 | 1 | 1 | `IFeatureManager/InsertWeldmentFeature.md` | 否 | 否 | Pointer to the [[IFeature]] object |
| InsertWrapFeature2 | 1 | 1 | 1 | `IFeatureManager/InsertWrapFeature2.md` | 否 | 否 | Wrap [[feature]] |
| InstancesToVary | 1 | 1 | 2 | `ICircularPatternFeatureData/InstancesToVary.md`；`ILinearPatternFeatureData/InstancesToVary.md` | 否 | 否 | True to vary the spacing of pattern instances, false to not |
| IntersectCurves | 1 | 1 | 1 | `ISketchManager/IntersectCurves.md` | 否 | 否 | 查不到 |
| Is3D | 1 | 2 | 1 | `ISketch/Is3D.md` | 否 | 否 | True if this sketch is 3D, false if it is 2D |
| IsBroken | 1 | 1 | 1 | `IView/IsBroken.md` | 否 | 否 | True if the view is displayed with a break, false if not |
| IsCircle | 1 | 1 | 2 | `ICurve/IsCircle.md`；`ISketchArc/IsCircle.md` | 否 | 否 | True if the curve is a circle, false if other curve type |
| IsComponentTreeValid | 1 | 1 | 1 | `IAssemblyDoc/IsComponentTreeValid.md` | 否 | 否 | True if the component tree is currently valid, false if the tree is currently invalid |
| IsCoordSysElementSelected | 1 | 1 | 1 | `ISelectionMgr/IsCoordSysElementSelected.md` | 否 | 否 | True if coordinate system element selected, false if not |
| IsCustomPropertyEditable | 1 | 1 | 1 | `ICustomPropertyManager/IsCustomPropertyEditable.md` | 否 | 否 | True if the custom property is editable, false if not |
| IsInEditTarget2 | 1 | 1 | 1 | `ISelectionMgr/IsInEditTarget2.md` | 否 | 否 | True if the selected item specified by AtIndex belongs to a model that is the current edit target, false if not |
| IsRationalCurve | 1 | 1 | 1 | `ISketchSpline/IsRationalCurve.md` | 否 | 否 | True if rational, false if non-rational |
| IsSheetMetal | 1 | 1 | 1 | `IBody2/IsSheetMetal.md` | 否 | 否 | True if this body was created by a sheet metal feature, false if not |
| IsStyleSpline | 1 | 1 | 1 | `ISketchSpline/IsStyleSpline.md` | 否 | 否 | True if a style spline, false if not |
| KFactor | 1 | 1 | 5 | `IBaseFlangeFeatureData/KFactor.md`；`IBendsFeatureData/KFactor.md`；`ICustomBendAllowance/KFactor.md`；`IOneBendFeatureData/KFactor.md` …（共 5） | 是 | 否 | K-factor |
| Length | 1 | 1 | 9 | `IBalloonStack/Length.md`；`ICalloutLengthVariable/Length.md`；`IDragArrowManipulator/Length.md`；`IHemFeatureData/Length.md` …（共 9） | 否 | 否 | Maximum number of balloons in one row of the stack; valid values are from 2 to 100 |
| LengthType | 1 | 1 | 1 | `ISketchSlot/LengthType.md` | 否 | 否 | Type of length of this sketch slot as defined in [[swSketchSlotLengthType_e]] |
| LengthUnit | 1 | 1 | 2 | `IImportDxfDwgData/LengthUnit.md`；`IModelDoc2/LengthUnit.md` | 否 | 否 | Unit as defined in [[swLengthUnit_e]] |
| ListExternalFileReferencesCount | 1 | 2 | 4 | `IComponent2/ListExternalFileReferencesCount.md`；`IFeature/ListExternalFileReferencesCount.md`；`IModelDoc2/ListExternalFileReferencesCount.md`；`IModelDocExtension/ListExternalFileReferencesCount.md` | 是 | 否 | Number of external references |
| LoadAddIn | 1 | 1 | 1 | `ISldWorks/LoadAddIn.md` | 否 | 否 | Status of loading the add-in as defined in [[swLoadAddinError_e]] |
| LockRotation | 1 | 1 | 2 | `IConcentricMateFeatureData/LockRotation.md`；`IProfileCenterMateFeatureData/LockRotation.md` | 否 | 否 | True to lock rotation, false to not |
| Mass | 1 | 1 | 1 | `IMassProperty2/Mass.md` | 否 | 否 | Mass |
| MateAlignment | 1 | 1 | 12 | `IAngleMateFeatureData/MateAlignment.md`；`ICamFollowerMateFeatureData/MateAlignment.md`；`ICoincidentMateFeatureData/MateAlignment.md`；`IConcentricMateFeatureData/MateAlignment.md` …（共 12） | 否 | 否 | Mate alignment as defined in [[swMateAlign_e]] |
| MateComponentName | 1 | 1 | 1 | `IMateInPlace/MateComponentName.md` | 否 | 否 | 查不到 |
| MateEntityType | 1 | 1 | 1 | `IMateInPlace/MateEntityType.md` | 否 | 否 | 查不到 |
| MaterialIdName | 1 | 1 | 3 | `IFace2/MaterialIdName.md`；`IModelDoc2/MaterialIdName.md`；`IPartDoc/MaterialIdName.md` | 是 | 否 | Material name |
| MaterialName | 1 | 1 | 1 | `ITexture/MaterialName.md` | 否 | 否 | Path and file name of the texture (see **Remarks**) |
| MemberType | 1 | 1 | 1 | `IStructureSystemSplitMember/MemberType.md` | 否 | 否 | Type of split as defined by [[swStructureSplitMemberType_e]] |
| MergePoints | 1 | 1 | 1 | `ISketch/MergePoints.md` | 否 | 否 | True if successful, false if not |
| MirrorProfile | 1 | 1 | 3 | `IStructuralMemberGroup/MirrorProfile.md`；`IStructureSystemMemberProfile/MirrorProfile.md`；`IThreadFeatureData/MirrorProfile.md` | 否 | 否 | True to mirror the profile, false to not |
| ModelToSketchTransform | 1 | 3 | 1 | `ISketch/ModelToSketchTransform.md` | 否 | 否 | [[Math transform]] |
| MoldDraftAnalysis | 1 | 1 | 1 | `IModelDoc2/MoldDraftAnalysis.md` | 否 | 否 | 查不到 |
| MoldUndercutDetect2 | 1 | 1 | 1 | `IFeatureManager/MoldUndercutDetect2.md` | 否 | 否 | 查不到 |
| NumberofSplitInstances | 1 | 1 | 1 | `IStructureSystemSplitMember/NumberofSplitInstances.md` | 否 | 否 | Number of instances |
| OffsetDistance | 1 | 1 | 10 | `IAdvancedHoleElementData/OffsetDistance.md`；`IEdgeFlangeFeatureData/OffsetDistance.md`；`IEndCapFeatureData/OffsetDistance.md`；`IJogFeatureData/OffsetDistance.md` …（共 10） | 否 | 否 | Offset distance (see **Remarks**) |
| OffsetPiercePoint | 1 | 1 | 1 | `IStructureSystemMemberProfile/OffsetPiercePoint.md` | 否 | 否 | True to offset the pierce point, false to not |
| OffsetPiercePointHorizontalAxis | 1 | 1 | 1 | `IStructureSystemMemberProfile/OffsetPiercePointHorizontalAxis.md` | 否 | 否 | Horizontal offset of the pierce point |
| OffsetPiercePointVerticalAxis | 1 | 1 | 1 | `IStructureSystemMemberProfile/OffsetPiercePointVerticalAxis.md` | 否 | 否 | Vertical offset of the pierce point |
| Orientation3 | 1 | 2 | 1 | `IModelView/Orientation3.md` | 否 | 否 | [[View orientation matrix]] |
| OverrideCenterOfMass | 1 | 1 | 1 | `IMassPropertyOverrideOptions/OverrideCenterOfMass.md` | 否 | 否 | True to override the calculated center of mass, false to not |
| OverrideMass | 1 | 1 | 1 | `IMassPropertyOverrideOptions/OverrideMass.md` | 否 | 否 | True to override the calculated mass value, false to not |
| OverrideMomentsOfInertia | 1 | 1 | 1 | `IMassPropertyOverrideOptions/OverrideMomentsOfInertia.md` | 否 | 否 | True to override the calculated moments of inertia, false to not |
| PartingType | 1 | 1 | 1 | `IPartingSurfaceFeatureData/PartingType.md` | 否 | 否 | Type of parting surface as defined in [[swPartingSurfaceMoldParmType_e]] (see **Remarks**) |
| PatternElement | 1 | 1 | 5 | `ICircularPatternFeatureData/PatternElement.md`；`ICurveDrivenPatternFeatureData/PatternElement.md`；`IFillPatternFeatureData/PatternElement.md`；`ILinearPatternFeatureData/PatternElement.md` …（共 5） | 否 | 否 | Type of entities on which to base this circular pattern feature defined in [[swPatternElementSelection_e]] |
| PerimeterCircle | 1 | 1 | 1 | `ISketchManager/PerimeterCircle.md` | 否 | 否 | [[3-point perimeter arc]] |
| PostTrimSurface | 1 | 1 | 2 | `IFeatureManager/PostTrimSurface.md`；`IModelDoc2/PostTrimSurface.md` | 是 | 否 | [[Feature]] |
| PreTrimSurface | 1 | 1 | 2 | `IFeatureManager/PreTrimSurface.md`；`IModelDoc2/PreTrimSurface.md` | 是 | 否 | True if successful, false if not |
| ProfileAlignmentAngle | 1 | 1 | 1 | `IStructureSystemMemberProfile/ProfileAlignmentAngle.md` | 否 | 否 | Alignment angle in radians |
| ProfileAlignmentType | 1 | 1 | 1 | `IStructureSystemMemberProfile/ProfileAlignmentType.md` | 否 | 否 | Profile alignment type as defined by [[swStructureProfileAlignmentType_e]] |
| ProfileMirrorType | 1 | 1 | 1 | `IStructureSystemMemberProfile/ProfileMirrorType.md` | 否 | 否 | Axis about which to flip this member profile as defined by [[swStructureProfileMirrorType_e]] |
| ProfileSize | 1 | 1 | 2 | `IProfileGroupFolder/ProfileSize.md`；`IStructureSystemMemberProfile/ProfileSize.md` | 否 | 否 | Weldment profile size as defined in a weldment profile |
| ProfileStandard | 1 | 1 | 2 | `IProfileGroupFolder/ProfileStandard.md`；`IStructureSystemMemberProfile/ProfileStandard.md` | 否 | 否 | Weldment profile standard as defined in a weldment profile |
| ProfileType | 1 | 1 | 5 | `IGussetFeatureData/ProfileType.md`；`IProfileGroupFolder/ProfileType.md`；`ISMGussetFeatureData/ProfileType.md`；`ISpring/ProfileType.md` …（共 5） | 否 | 否 | Type of profile as defined in [[swGussetProfileType_e]] |
| PropagateVisualProperty | 1 | 1 | 9 | `ICircularPatternFeatureData/PropagateVisualProperty.md`；`ICurveDrivenPatternFeatureData/PropagateVisualProperty.md`；`IDerivedPatternFeatureData/PropagateVisualProperty.md`；`IFillPatternFeatureData/PropagateVisualProperty.md` …（共 9） | 否 | 否 | True to propagate all visual properties, false to not |
| RealView | 1 | 1 | 1 | `IMaterialVisualPropertiesData/RealView.md` | 否 | 否 | True if textures are RealView graphics, false if Standard graphics |
| Reference | 1 | 1 | 2 | `IMateEntity2/Reference.md`；`IRefPlaneFeatureData/Reference.md` | 否 | 否 | [[Mate reference]] |
| ReferenceComponent | 1 | 1 | 2 | `IMateEntity2/ReferenceComponent.md`；`ISimulationForceFeatureData/ReferenceComponent.md` | 否 | 否 | [[Component]] |
| ReferenceType | 1 | 1 | 2 | `IMateEntity2/ReferenceType.md`；`IMateReference/ReferenceType.md` | 是 | 否 | 查不到 |
| ReferenceType2 | 1 | 1 | 1 | `IMateEntity2/ReferenceType2.md` | 否 | 否 | Type of mate reference as defined in [[swSelectType_e]] |
| ReferencedConfiguration | 1 | 2 | 2 | `IComponent2/ReferencedConfiguration.md`；`IView/ReferencedConfiguration.md` | 否 | 否 | Name of the configuration |
| ReleaseSelectionAccess | 1 | 1 | 117 | `IAdvancedHoleFeatureData/ReleaseSelectionAccess.md`；`IBaseFlangeFeatureData/ReleaseSelectionAccess.md`；`IBeltChainFeatureData/ReleaseSelectionAccess.md`；`IBendsFeatureData/ReleaseSelectionAccess.md` …（共 117） | 否 | 否 | 查不到 |
| RemovePerspective | 1 | 1 | 1 | `IModelView/RemovePerspective.md` | 否 | 否 | 查不到 |
| ResumeSelectionList | 1 | 1 | 1 | `ISelectionMgr/ResumeSelectionList.md` | 是 | 否 | 查不到 |
| ResumeSelectionList2 | 1 | 1 | 1 | `ISelectionMgr/ResumeSelectionList2.md` | 否 | 否 | 查不到 |
| RollBy | 1 | 1 | 1 | `IModelView/RollBy.md` | 否 | 否 | 查不到 |
| RotateAboutCenter | 1 | 1 | 1 | `IModelView/RotateAboutCenter.md` | 否 | 否 | 查不到 |
| Rotation | 1 | 1 | 2 | `IFillPatternFeatureData/Rotation.md`；`IView3D/Rotation.md` | 否 | 否 | Counterclockwise rotation of the seed instance |
| Roughness | 1 | 2 | 2 | `IDSPBRMaterial/Roughness.md`；`IRenderMaterial/Roughness.md` | 否 | 否 | 0.0 (default) <= Specular spread <= 1.0 |
| RouteType | 1 | 1 | 1 | `IConnectionPointFeatureData/RouteType.md` | 否 | 否 | Route type as defined in [[swModelRouteType_e]] |
| SaveAs3 | 1 | 3 | 2 | `IModelDoc2/SaveAs3.md`；`IModelDocExtension/SaveAs3.md` | 是 | 否 | True if the save is successful, false if not |
| SaveBMP | 1 | 1 | 1 | `IModelDoc2/SaveBMP.md` | 否 | 否 | True if file is created successfully, false if not |
| Scale | 1 | 2 | 8 | `IFaceHatch/Scale.md`；`IMathPoint/Scale.md`；`IMathVector/Scale.md`；`IModelDoc2/Scale.md` …（共 8） | 是 | 否 | Newly created scaled [[math point]] or NULL if the operation fails |
| Scale2 | 1 | 1 | 7 | `IDisplayDimension/Scale2.md`；`IFaceHatch/Scale2.md`；`IMaterialVisualPropertiesData/Scale2.md`；`IModelView/Scale2.md` …（共 7） | 否 | 否 | Scale applied to the dimension value |
| ScaleDecimal | 1 | 1 | 1 | `IView/ScaleDecimal.md` | 否 | 否 | Drawing view scale |
| ScaleRatio | 1 | 3 | 1 | `IView/ScaleRatio.md` | 否 | 否 | Array of 2 doubles (see **Remarks**) |
| Select2 | 1 | 1 | 12 | `IAnnotation/Select2.md`；`IBody2/Select2.md`；`IComponent2/Select2.md`；`IConfiguration/Select2.md` …（共 12） | 是 | 否 | True if the body was selected, false if not |
| SelectByRay | 1 | 1 | 2 | `IModelDoc2/SelectByRay.md`；`IModelDocExtension/SelectByRay.md` | 是 | 否 | True if a selection is made, false if not |
| SelectionColor | 1 | 1 | 1 | `ISelectionMgr/SelectionColor.md` | 否 | 否 | 查不到 |
| SendMsgToUser2 | 1 | 1 | 1 | `ISldWorks/SendMsgToUser2.md` | 否 | 否 | Value corresponding to the button the user clicked as defined in [[swMessageBoxResult_e]] |
| SensorType | 1 | 1 | 1 | `ISensor/SensorType.md` | 否 | 否 | Type of sensor as defined in [[swSensorType_e]] |
| SetAutomaticSolve | 1 | 1 | 1 | `ISketch/SetAutomaticSolve.md` | 否 | 否 | True if set, false if not |
| SetCameraByName | 1 | 1 | 1 | `IModelView/SetCameraByName.md` | 否 | 否 | True if the camera is set, false if not |
| SetComponentSuppression | 1 | 1 | 1 | `IAssemblyDoc/SetComponentSuppression.md` | 否 | 否 | True if the selected components are suppressed, resolved, or set to lightweight, false |
| SetMaterialPropertyName2 | 1 | 1 | 1 | `IPartDoc/SetMaterialPropertyName2.md` | 否 | 否 | 查不到 |
| SetOverrideMassValue | 1 | 1 | 1 | `IMassPropertyOverrideOptions/SetOverrideMassValue.md` | 否 | 否 | True if the mass is successfully overridden, false if not |
| SetOverrideOptions | 1 | 1 | 1 | `IMassProperty2/SetOverrideOptions.md` | 否 | 否 | True if the mass property override options are set successfully, false if not |
| SetSelectedObjectMark | 1 | 1 | 1 | `ISelectionMgr/SetSelectedObjectMark.md` | 否 | 否 | True if the selection is successfully set, false if not |
| SetSelectionPoint | 1 | 1 | 1 | `ISelectionMgr/SetSelectionPoint.md` | 是 | 否 | 查不到 |
| SetSplitReferences | 1 | 1 | 1 | `IStructureSystemSplitMember/SetSplitReferences.md` | 否 | 否 | True if split member references successfully set, false if not |
| SetTemplateName | 1 | 1 | 1 | `ISheet/SetTemplateName.md` | 否 | 否 | 查不到 |
| SetUserPreferenceToggle | 1 | 1 | 3 | `IModelDoc2/SetUserPreferenceToggle.md`；`IModelDocExtension/SetUserPreferenceToggle.md`；`ISldWorks/SetUserPreferenceToggle.md` | 是 | 否 | True if the toggle is successful, false if not |
| ShapeIntensity | 1 | 1 | 2 | `IBreakLine/ShapeIntensity.md`；`IDetailCircle/ShapeIntensity.md` | 否 | 否 | Shape intensity of a jagged cut break line; valid range is 1 (most) to 5 (least) (see **Remarks**) |
| ShowConfiguration2 | 1 | 1 | 1 | `IModelDoc2/ShowConfiguration2.md` | 否 | 否 | True if the configuration is activated successfully, false if not |
| ShowSplineHandles | 1 | 1 | 1 | `ISketchSpline/ShowSplineHandles.md` | 否 | 否 | True to show spline handles, false to not |
| SketchExtend | 1 | 1 | 1 | `ISketchManager/SketchExtend.md` | 否 | 否 | True if the sketch entity is extended to meet the nearest sketch entity, false if not |
| SketchModifyFlip | 1 | 1 | 1 | `IModelDoc2/SketchModifyFlip.md` | 否 | 否 | 查不到 |
| SketchModifyRotate | 1 | 1 | 1 | `IModelDoc2/SketchModifyRotate.md` | 否 | 否 | 查不到 |
| SketchModifyScale | 1 | 1 | 1 | `IModelDoc2/SketchModifyScale.md` | 否 | 否 | True if successful, false if not |
| SketchModifyTranslate | 1 | 1 | 1 | `IModelDoc2/SketchModifyTranslate.md` | 否 | 否 | The sketch is translated from the XY start point position to the XY end point position. |
| SketchOffset2 | 1 | 1 | 2 | `IModelDoc2/SketchOffset2.md`；`ISketchManager/SketchOffset2.md` | 是 | 否 | True if the offset is successful, false if not |
| SketchTrim | 1 | 1 | 2 | `IModelDoc2/SketchTrim.md`；`ISketchManager/SketchTrim.md` | 是 | 否 | True if the sketch entities are trimmed, false if not |
| SketchUseEdge3 | 1 | 1 | 1 | `ISketchManager/SketchUseEdge3.md` | 否 | 否 | True if the sketch entities are created, false if not |
| Specular | 1 | 2 | 3 | `IAppearanceSetting/Specular.md`；`IDSPBRMaterial/Specular.md`；`IRenderMaterial/Specular.md` | 否 | 否 | 0 <= *specular_value* <= 1; valid only when [[IAppearanceSetting::SpecularSpread]] > 0 |
| SplitLength | 1 | 1 | 1 | `IStructureSystemSplitMember/SplitLength.md` | 否 | 否 | Length |
| SplitLengthRevDirection | 1 | 1 | 1 | `IStructureSystemSplitMember/SplitLengthRevDirection.md` | 否 | 否 | True to reverse the direction of the length, false to not |
| StartDynamics | 1 | 1 | 1 | `IModelView/StartDynamics.md` | 否 | 否 | 查不到 |
| State | 1 | 1 | 1 | `IPropertyManagerPageCheckbox/State.md` | 否 | 否 | State of this check box as defined in [[swPropertyManagerCheckboxState_e]] |
| StopDynamics | 1 | 1 | 1 | `IModelView/StopDynamics.md` | 否 | 否 | 查不到 |
| Stretch | 1 | 1 | 1 | `IModelDocExtension/Stretch.md` | 否 | 否 | 查不到 |
| Style | 1 | 1 | 17 | `IAnnotation/Style.md`；`IAutoBalloonOptions/Style.md`；`IBalloonOptions/Style.md`；`IBreakLine/Style.md` …（共 17） | 否 | 否 | Line style as defined in [[swLineStyles_e]] |
| Suppressed | 1 | 2 | 1 | `ISketchRelation/Suppressed.md` | 否 | 否 | True the relation is suppressed, false it is not |
| SurfaceArea | 1 | 1 | 1 | `IMassProperty2/SurfaceArea.md` | 否 | 否 | Surface area |
| SuspendSelectionList | 1 | 1 | 1 | `ISelectionMgr/SuspendSelectionList.md` | 否 | 否 | 0 if the suspended list is empty, 1 if not |
| Thickness | 1 | 1 | 11 | `IBaseFlangeFeatureData/Thickness.md`；`IEndCapFeatureData/Thickness.md`；`IGussetFeatureData/Thickness.md`；`IIndentFeatureData/Thickness.md` …（共 11） | 否 | 否 | Value for thickness |
| ThreadClass | 1 | 2 | 3 | `IStraightTapElementData/ThreadClass.md`；`ITaperedTapElementData/ThreadClass.md`；`IWizardHoleFeatureData2/ThreadClass.md` | 否 | 否 | Thread class as defined in [[swStraightTapHoleThreadClass_e]] |
| ThreadClassOverride | 1 | 2 | 2 | `IStraightTapElementData/ThreadClassOverride.md`；`ITaperedTapElementData/ThreadClassOverride.md` | 否 | 否 | True to override the thread class, false to not |
| Title | 1 | 1 | 5 | `IMessageBarDefinition/Title.md`；`IModelWindow/Title.md`；`IPropertyManagerPage2/Title.md`；`ITableAnnotation/Title.md` …（共 5） | 否 | 否 | Non-empty title string |
| ToolboxPartType | 1 | 1 | 1 | `IModelDocExtension/ToolboxPartType.md` | 否 | 否 | Type of SOLIDWORKS Toolbox part type as defined in [[swToolBoxPartType_e]] |
| Transform | 1 | 1 | 4 | `IComponent2/Transform.md`；`ICoordinateSystemFeatureData/Transform.md`；`IModelView/Transform.md`；`IRefPlane/Transform.md` | 是 | 否 | [[Math transform]] |
| TranslateBy | 1 | 1 | 1 | `IModelView/TranslateBy.md` | 否 | 否 | 查不到 |
| TranslateComponent | 1 | 1 | 1 | `IAssemblyDoc/TranslateComponent.md` | 否 | 否 | 查不到 |
| Translation3 | 1 | 1 | 1 | `IModelView/Translation3.md` | 否 | 否 | [[Model view translation vector]] |
| Transparency | 1 | 2 | 3 | `IDSPBRMaterial/Transparency.md`；`IModelDocExtension/Transparency.md`；`IRenderMaterial/Transparency.md` | 否 | 否 | 0.0 (opaque) default <= Transparency <= 1.0 (translucent) |
| TypeName | 1 | 2 | 1 | `IMateFeatureData/TypeName.md` | 否 | 否 | Mate type as defined in [[swMateType_e]] |
| UpdateCutList | 1 | 1 | 1 | `IBodyFolder/UpdateCutList.md` | 否 | 否 | True if the automatically generated cut list is successfully updated, false if not or because the document does not contain an automatically generated cut list |
| UpdateRenderMaterialsInSceneGraph | 1 | 1 | 1 | `IModelDocExtension/UpdateRenderMaterialsInSceneGraph.md` | 否 | 否 | 查不到 |
| UseSheetScale | 1 | 2 | 1 | `IView/UseSheetScale.md` | 否 | 否 | 1 if the view scale is the same as the sheet scale, 0 if the view scale is independent of the sheet scale |
| UseStandardDepth | 1 | 1 | 3 | `ICounterboreElementData/UseStandardDepth.md`；`ICountersinkElementData/UseStandardDepth.md`；`ITaperedTapElementData/UseStandardDepth.md` | 否 | 否 | True to use the standard offset distance, false to not (see **Remarks**) |
| VarySketch | 1 | 3 | 3 | `ICircularPatternFeatureData/VarySketch.md`；`ICurveDrivenPatternFeatureData/VarySketch.md`；`ILinearPatternFeatureData/VarySketch.md` | 否 | 否 | True to allow the pattern instances of a seed sketch to vary in relation to enclosing geometry, false to not |
| Visible | 1 | 1 | 16 | `IAnnotation/Visible.md`；`IBody2/Visible.md`；`ICommandTab/Visible.md`；`IComponent2/Visible.md` …（共 16） | 否 | 否 | Visibility state as defined in [[swAnnotationVisibilityState_e]] |
| Width | 1 | 1 | 9 | `IAnnotation/Width.md`；`IDrawingComponent/Width.md`；`ILayer/Width.md`；`IPMIDatumTarget/Width.md` …（共 9） | 否 | 否 | Line style as defined in [[swLineWeights_e]] |
| X | 1 | 2 | 4 | `IMeasure/X.md`；`ISelectData/X.md`；`ISketchPoint/X.md`；`ISplineHandle/X.md` | 否 | 否 | x coordinate of the selected point in model space or -1 if this property is invalid for the selected entity |
| XorHighlight | 1 | 1 | 1 | `IModelView/XorHighlight.md` | 否 | 否 | True to Xor the hightlight state, false to not |
| Y | 1 | 2 | 4 | `IMeasure/Y.md`；`ISelectData/Y.md`；`ISketchPoint/Y.md`；`ISplineHandle/Y.md` | 否 | 否 | y coordinate of the selected point in model space or -1 if this property is invalid for the selected entity |
| ZoomByFactor | 1 | 1 | 1 | `IModelView/ZoomByFactor.md` | 否 | 否 | 查不到 |

## 三、`C:\swapi\types` 无页、只在反射清单里的 220 个成员

> 这些**不是**「查不到」—— 它们都在**出厂反射清单**里有签名，只是 `C:\swapi\types` 这个
> **带说明文档的源**没收录它们（多为加载项程序集：cosworks / sldcostingapi / SWRoutingLib / swdocumentmgr）。
> ⇒ **判据 1/2（废弃、指针）在这些成员上「无从适用」**，本表如实写「查不到」，**不推测**。

| 成员名 | 出现文件数 | 调用点 | 反射清单（源） | Obsolete | 指针 | Returns 首行 |
|---|---|---|---|---|---|---|
| AddCovering | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddToRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateCovering | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateFlattenRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreatePipeDrawingforPipeRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateRouteLine | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ExitRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ExportPipeData | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ExportTubeData | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| FromComponentReference | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| FromPinReference | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetAllRouteSegmentCount | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetAutoRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetCableProperty | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetCoresCount | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetCuttingLength | 1 | 2 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetElectricalRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetRouteErrorsCount | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetRouteProperty | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetRouteSegmentIDsCount | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| HasCovering | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MinimumBendRadius | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| RemoveCovering | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetRoutePathForWire | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| StartRoute | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ToComponentReference | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ToPinReference | 1 | 1 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| UserName | 1 | 2 | `iface_SWRoutingLib.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ActivatePlot | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ActiveStudy | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddBearingLoad | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddBoltConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddCentrifugalForce | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddConvection | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddCyclicSymmetryRestraint | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddDistributedMass | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddEdgeWeldConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddElasticConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddForce | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddGravity | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddHeatFlux | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddHeatPower | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddLinkConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddPinConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddPrescribedDisplacement | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddPressure | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddRadiation | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddRemoteLoad | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddRestraint | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddRigidConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddSpotWeldConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddSpringConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddTemperature | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AnalysisType | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AxialStiffnessValue | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| BeginEdit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Category | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ClearanceUnit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ContactName | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ContactSetType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ConvertStudy | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CoordSystemType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CosmosWorks | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateDeformedBody | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateDemoldControl | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateFactorOfSafetyConstraint | 1 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateGoal | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateMassConstraint | 1 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateMesh | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateMeshForMeshControl | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateNewStudy | 2 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateNewStudy2 | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateNewStudy3 | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreatePlot | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreatePreservedRegionControl | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateStressConstraint | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateSymmetryControl | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateThicknessControl | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| DeletePlot | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| DeleteStudy | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| DirectionType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| DuplicateStudy | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| DynamicAnalysisSubType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ElementCount | 2 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ElementSize | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| EndEdit | 1 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| EntityCount | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| EquationAngularUnit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| EquationCoordinateSystemType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| EquationLinearUnit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ExportSimulationStudy | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ForceBeginEdit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ForceEndEdit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| FrictionValue | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GapType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GenerateReport | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetBucklingLoadFactors | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetDefaultElementSizeAndTolerance | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetDisplacementAtPoints | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetEdgeWeldConnector | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetElementLocation | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetLoadsAndRestraints | 2 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetMassConstraint | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetMaximumAvailableSteps | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetNoOfFailedComponents | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetNodeLocation | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetPlotNames | 2 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetStudy | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetTimeCurve | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetWorstJacobianRatio | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GrowthRatio | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| HFValue | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| IncludeCreep2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| IncludeFriction2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| IncludeNonUniformDistribution2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| IsComponentFailed2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| IsMeshFailed | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| JacobianPoints | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| LoadsAndRestraintsManager | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MassUnit | 1 | 1 | `iface_cosworks.txt`、`iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MaterialUnits | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MaxAspectRatio | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MaxElementSize | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Mesh | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MeshAndRun | 2 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MeshControlCount | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MeshState | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MeshType | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MesherType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MinElementSize | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ModelType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| NodeCount | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| NonlinearAnalysisSubType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| NormalForceOrTorqueValue | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| NumberOfLoops | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| OffLoad | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| PerUnitLength2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| PhaseAngle | 1 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| PhaseAngleUnit | 1 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| PressureType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Quality | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| RemoveConstraint | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| RenameStudyFromName | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ResistanceType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ResistanceUnit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Results | 3 | 4 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ReverseDirection2 | 1 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| RunAnalysis | 3 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SelectDemoldDirection | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SelectSymmetryType | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetComparator | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetConvergenceCheck | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetIncludeMaxMemberThickness2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetIncludeMinMemberThickness2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetIncludeRegionDepth2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetIterationLimit | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetIterationOption | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetMassPreference | 1 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetMaxMemberThickness | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetMinimumMemberThickness | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetValue | 1 | 5 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| StudyCount | 2 | 2 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| StudyManager | 2 | 3 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| TopologyStudyManager | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| TopologyStudyOptions | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| UseTemperatureCurve2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| UseTimeCurve2 | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| VersionNumber | 1 | 1 | `iface_cosworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateFeatures | 1 | 1 | `iface_fworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| RecognizeFeatureInteractive | 1 | 1 | `iface_fworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetAdvancedOptions | 1 | 1 | `iface_fworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetPerformanceOptions | 1 | 1 | `iface_fworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AssignCustomCost | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| BodyStatus | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CostingDefaults | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CostingModel | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CostingTemplateName | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CostingType | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreateCostAnalysis | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CurrencyCode | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CurrencyName | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CurrencySeparator | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetBodyType | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetCostAnalysis | 1 | 2 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetCostingMethod | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetManufacturingCost | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetMaterialCost | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetSWBody | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetSetupCost | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetTemplatePathnames | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetTotalCostToCharge | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetTotalCostToManufacture | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| IncludeBody | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| LotSize | 1 | 2 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| LotSizeForMultibody | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| LotSizeForSingleBody | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MarkUpPercent | 1 | 2 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| MarkUpType | 1 | 2 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetCostingMethod | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetManufacturingMethod | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| SetMaterialName | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| TotalQuantity | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| UnitSystem | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| UpdateCostForAllBodies | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| WaitForUIUpdate | 1 | 1 | `iface_sldcostingapi.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| ViewZoomtofit2 | 1 | 1 | `iface_sldworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Xform | 1 | 1 | `iface_sldworks.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddCustomProperty | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddInvisibleCustomProperty | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| AddRevisionRow | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Author | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Comments | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| CreationDate | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| DeleteCustomProperty | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetAllExternalReferences | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| GetBOMStartNumber | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Keywords | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| LastSavedBy | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| LastSavedDate | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |
| Subject | 1 | 1 | `iface_swdocumentmgr.txt` | 查不到（该源无此字段） | 查不到（该源无此字段） | 查不到 |

### 3.1 按反射清单来源汇总

| 反射清单 | 本表收录的成员数 |
|---|---|
| `iface_cosworks.txt` | 140 |
| `iface_sldcostingapi.txt` | 34 |
| `iface_SWRoutingLib.txt` | 28 |
| `iface_swdocumentmgr.txt` | 13 |
| `iface_fworks.txt` | 4 |
| `iface_sldworks.txt` | 2 |

## 四、特殊项（单列，**不混进主表凑数**）

### 4.1 同一成员名命中**多个**接口目录（204 个）—— 用错接口 = 对象对成员没反应

> 已知事实 36 的形态：同名接口分属不同族时，**用错的后果是连读都读不到**。
> 本表只报**事实**（哪些同名的都命中），**不判**代码该用哪一个。

| 成员名 | 官方页数 | 全部命中页（接口/文件） |
|---|---|---|
| AccessSelections | 117 | `IAdvancedHoleFeatureData/AccessSelections.md`；`IBaseFlangeFeatureData/AccessSelections.md`；`IBeltChainFeatureData/AccessSelections.md`；`IBendsFeatureData/AccessSelections.md`；`IBoundaryBossFeatureData/AccessSelections.md`；`IBoundingBoxFeatureData/AccessSelections.md`；`IBreakCornerFeatureData/AccessSelections.md`；`IBrokenOutSectionFeatureData/AccessSelections.md`；`ICavityFeatureData/AccessSelections.md`；`IChainPatternFeatureData/AccessSelections.md`；`IChamferFeatureData2/AccessSelections.md`；`ICircularPatternFeatureData/AccessSelections.md`；`IClosedCornerFeatureData/AccessSelections.md`；`ICombineBodiesFeatureData/AccessSelections.md`；`ICompositeCurveFeatureData/AccessSelections.md`；`IConnectionPointFeatureData/AccessSelections.md`；`IConvertSolidFeatureData/AccessSelections.md`；`ICoordinateSystemFeatureData/AccessSelections.md`；`ICoreFeatureData/AccessSelections.md`；`ICornerReliefFeatureData/AccessSelections.md`；`ICornerTreatmentFeatureData/AccessSelections.md`；`ICosmeticThreadFeatureData/AccessSelections.md`；`ICosmeticWeldBeadFeatureData/AccessSelections.md`；`ICrossBreakFeatureData/AccessSelections.md`；`ICurveDrivenPatternFeatureData/AccessSelections.md`；`IDeleteBodyFeatureData/AccessSelections.md`；`IDeleteFaceFeatureData/AccessSelections.md`；`IDerivedPartFeatureData/AccessSelections.md`；`IDerivedPatternFeatureData/AccessSelections.md`；`IDimPatternFeatureData/AccessSelections.md`；`IDomeFeatureData2/AccessSelections.md`；`IDraftFeatureData2/AccessSelections.md`；`IEdgeFlangeFeatureData/AccessSelections.md`；`IEndCapFeatureData/AccessSelections.md`；`IExtrudeFeatureData2/AccessSelections.md`；`IFillPatternFeatureData/AccessSelections.md`；`IFillSurfaceFeatureData/AccessSelections.md`；`IFlatPatternFeatureData/AccessSelections.md`；`IFoldsFeatureData/AccessSelections.md`；`IGroundPlaneFeatureData/AccessSelections.md`；`IGussetFeatureData/AccessSelections.md`；`IHealEdgesFeatureData/AccessSelections.md`；`IHemFeatureData/AccessSelections.md`；`IHoleSeriesFeatureData2/AccessSelections.md`；`IIndentFeatureData/AccessSelections.md`；`IIntersectFeatureData/AccessSelections.md`；`IJogFeatureData/AccessSelections.md`；`IJoinFeatureData/AccessSelections.md`；`ILibraryFeatureData/AccessSelections.md`；`ILibraryFormToolFeatureData/AccessSelections.md`；`ILinearPatternFeatureData/AccessSelections.md`；`ILocalCircularPatternFeatureData/AccessSelections.md`；`ILocalCurvePatternFeatureData/AccessSelections.md`；`ILocalLinearPatternFeatureData/AccessSelections.md`；`ILocalSketchPatternFeatureData/AccessSelections.md`；`ILoftFeatureData/AccessSelections.md`；`ILoftedBendsFeatureData/AccessSelections.md`；`IMacroFeatureData/AccessSelections.md`；`IMateControllerFeatureData/AccessSelections.md`；`IMirrorComponentFeatureData/AccessSelections.md`；`IMirrorPartFeatureData/AccessSelections.md`；`IMirrorPatternFeatureData/AccessSelections.md`；`IMirrorSolidFeatureData/AccessSelections.md`；`IMiterFlangeFeatureData/AccessSelections.md`；`IMoveCopyBodyFeatureData/AccessSelections.md`；`IMoveFaceFeatureData/AccessSelections.md`；`IOneBendFeatureData/AccessSelections.md`；`IPartingLineFeatureData/AccessSelections.md`；`IPartingSurfaceFeatureData/AccessSelections.md`；`IProjectionCurveFeatureData/AccessSelections.md`；`IRefAxisFeatureData/AccessSelections.md`；`IRefPlaneFeatureData/AccessSelections.md`；`IRefPointFeatureData/AccessSelections.md`；`IReferencePointCurveFeatureData/AccessSelections.md`；`IReplaceFaceFeatureData/AccessSelections.md`；`IRevolveFeatureData2/AccessSelections.md`；`IRibFeatureData2/AccessSelections.md`；`IRipFeatureData/AccessSelections.md`；`IRuledSurfaceFeatureData/AccessSelections.md`；`ISMGussetFeatureData/AccessSelections.md`；`ISMNormalCutFeatureData2/AccessSelections.md`；`ISaveBodyFeatureData/AccessSelections.md`；`IScaleFeatureData/AccessSelections.md`；`ISheetMetalFeatureData/AccessSelections.md`；`IShellFeatureData/AccessSelections.md`；`IShutOffSurfaceFeatureData/AccessSelections.md`；`ISimpleFilletFeatureData2/AccessSelections.md`；`ISimpleHoleFeatureData2/AccessSelections.md`；`ISketchPatternFeatureData/AccessSelections.md`；`ISketchedBendFeatureData/AccessSelections.md`；`ISmartComponentFeatureData/AccessSelections.md`；`ISplitBodyFeatureData/AccessSelections.md`；`ISplitLineFeatureData/AccessSelections.md`；`IStructuralMemberFeatureData/AccessSelections.md`；`IStructureSystemMemberFeatureData/AccessSelections.md`；`ISurfExtrudeFeatureData/AccessSelections.md`；`ISurfRevolveFeatureData/AccessSelections.md`；`ISurfaceCutFeatureData/AccessSelections.md`；`ISurfaceExtendFeatureData/AccessSelections.md`；`ISurfaceFlattenFeatureData/AccessSelections.md`；`ISurfaceKnitFeatureData/AccessSelections.md`；`ISurfaceOffsetFeatureData/AccessSelections.md`；`ISurfacePlanarFeatureData/AccessSelections.md`；`ISurfaceRadiateFeatureData/AccessSelections.md`；`ISurfaceTrimFeatureData/AccessSelections.md`；`ISweepFeatureData/AccessSelections.md`；`ISweptFlangeFeatureData/AccessSelections.md`；`ITabAndSlotFeatureData/AccessSelections.md`；`ITablePatternFeatureData/AccessSelections.md`；`IThickenFeatureData/AccessSelections.md`；`IThreadFeatureData/AccessSelections.md`；`IToolingSplitFeatureData/AccessSelections.md`；`IVariableFilletFeatureData2/AccessSelections.md`；`IWeldmentBeadFeatureData/AccessSelections.md`；`IWeldmentTrimExtendFeatureData/AccessSelections.md`；`IWizardHoleFeatureData2/AccessSelections.md`；`IWrapSketchFeatureData/AccessSelections.md` |
| ReleaseSelectionAccess | 117 | `IAdvancedHoleFeatureData/ReleaseSelectionAccess.md`；`IBaseFlangeFeatureData/ReleaseSelectionAccess.md`；`IBeltChainFeatureData/ReleaseSelectionAccess.md`；`IBendsFeatureData/ReleaseSelectionAccess.md`；`IBoundaryBossFeatureData/ReleaseSelectionAccess.md`；`IBoundingBoxFeatureData/ReleaseSelectionAccess.md`；`IBreakCornerFeatureData/ReleaseSelectionAccess.md`；`IBrokenOutSectionFeatureData/ReleaseSelectionAccess.md`；`ICavityFeatureData/ReleaseSelectionAccess.md`；`IChainPatternFeatureData/ReleaseSelectionAccess.md`；`IChamferFeatureData2/ReleaseSelectionAccess.md`；`ICircularPatternFeatureData/ReleaseSelectionAccess.md`；`IClosedCornerFeatureData/ReleaseSelectionAccess.md`；`ICombineBodiesFeatureData/ReleaseSelectionAccess.md`；`ICompositeCurveFeatureData/ReleaseSelectionAccess.md`；`IConnectionPointFeatureData/ReleaseSelectionAccess.md`；`IConvertSolidFeatureData/ReleaseSelectionAccess.md`；`ICoordinateSystemFeatureData/ReleaseSelectionAccess.md`；`ICoreFeatureData/ReleaseSelectionAccess.md`；`ICornerReliefFeatureData/ReleaseSelectionAccess.md`；`ICornerTreatmentFeatureData/ReleaseSelectionAccess.md`；`ICosmeticThreadFeatureData/ReleaseSelectionAccess.md`；`ICosmeticWeldBeadFeatureData/ReleaseSelectionAccess.md`；`ICrossBreakFeatureData/ReleaseSelectionAccess.md`；`ICurveDrivenPatternFeatureData/ReleaseSelectionAccess.md`；`IDeleteBodyFeatureData/ReleaseSelectionAccess.md`；`IDeleteFaceFeatureData/ReleaseSelectionAccess.md`；`IDerivedPartFeatureData/ReleaseSelectionAccess.md`；`IDerivedPatternFeatureData/ReleaseSelectionAccess.md`；`IDimPatternFeatureData/ReleaseSelectionAccess.md`；`IDomeFeatureData2/ReleaseSelectionAccess.md`；`IDraftFeatureData2/ReleaseSelectionAccess.md`；`IEdgeFlangeFeatureData/ReleaseSelectionAccess.md`；`IEndCapFeatureData/ReleaseSelectionAccess.md`；`IExtrudeFeatureData2/ReleaseSelectionAccess.md`；`IFillPatternFeatureData/ReleaseSelectionAccess.md`；`IFillSurfaceFeatureData/ReleaseSelectionAccess.md`；`IFlatPatternFeatureData/ReleaseSelectionAccess.md`；`IFoldsFeatureData/ReleaseSelectionAccess.md`；`IGroundPlaneFeatureData/ReleaseSelectionAccess.md`；`IGussetFeatureData/ReleaseSelectionAccess.md`；`IHealEdgesFeatureData/ReleaseSelectionAccess.md`；`IHemFeatureData/ReleaseSelectionAccess.md`；`IHoleSeriesFeatureData2/ReleaseSelectionAccess.md`；`IIndentFeatureData/ReleaseSelectionAccess.md`；`IIntersectFeatureData/ReleaseSelectionAccess.md`；`IJogFeatureData/ReleaseSelectionAccess.md`；`IJoinFeatureData/ReleaseSelectionAccess.md`；`ILibraryFeatureData/ReleaseSelectionAccess.md`；`ILibraryFormToolFeatureData/ReleaseSelectionAccess.md`；`ILinearPatternFeatureData/ReleaseSelectionAccess.md`；`ILocalCircularPatternFeatureData/ReleaseSelectionAccess.md`；`ILocalCurvePatternFeatureData/ReleaseSelectionAccess.md`；`ILocalLinearPatternFeatureData/ReleaseSelectionAccess.md`；`ILocalSketchPatternFeatureData/ReleaseSelectionAccess.md`；`ILoftFeatureData/ReleaseSelectionAccess.md`；`ILoftedBendsFeatureData/ReleaseSelectionAccess.md`；`IMacroFeatureData/ReleaseSelectionAccess.md`；`IMateControllerFeatureData/ReleaseSelectionAccess.md`；`IMirrorComponentFeatureData/ReleaseSelectionAccess.md`；`IMirrorPartFeatureData/ReleaseSelectionAccess.md`；`IMirrorPatternFeatureData/ReleaseSelectionAccess.md`；`IMirrorSolidFeatureData/ReleaseSelectionAccess.md`；`IMiterFlangeFeatureData/ReleaseSelectionAccess.md`；`IMoveCopyBodyFeatureData/ReleaseSelectionAccess.md`；`IMoveFaceFeatureData/ReleaseSelectionAccess.md`；`IOneBendFeatureData/ReleaseSelectionAccess.md`；`IPartingLineFeatureData/ReleaseSelectionAccess.md`；`IPartingSurfaceFeatureData/ReleaseSelectionAccess.md`；`IProjectionCurveFeatureData/ReleaseSelectionAccess.md`；`IRefAxisFeatureData/ReleaseSelectionAccess.md`；`IRefPlaneFeatureData/ReleaseSelectionAccess.md`；`IRefPointFeatureData/ReleaseSelectionAccess.md`；`IReferencePointCurveFeatureData/ReleaseSelectionAccess.md`；`IReplaceFaceFeatureData/ReleaseSelectionAccess.md`；`IRevolveFeatureData2/ReleaseSelectionAccess.md`；`IRibFeatureData2/ReleaseSelectionAccess.md`；`IRipFeatureData/ReleaseSelectionAccess.md`；`IRuledSurfaceFeatureData/ReleaseSelectionAccess.md`；`ISMGussetFeatureData/ReleaseSelectionAccess.md`；`ISMNormalCutFeatureData2/ReleaseSelectionAccess.md`；`ISaveBodyFeatureData/ReleaseSelectionAccess.md`；`IScaleFeatureData/ReleaseSelectionAccess.md`；`ISheetMetalFeatureData/ReleaseSelectionAccess.md`；`IShellFeatureData/ReleaseSelectionAccess.md`；`IShutOffSurfaceFeatureData/ReleaseSelectionAccess.md`；`ISimpleFilletFeatureData2/ReleaseSelectionAccess.md`；`ISimpleHoleFeatureData2/ReleaseSelectionAccess.md`；`ISketchPatternFeatureData/ReleaseSelectionAccess.md`；`ISketchedBendFeatureData/ReleaseSelectionAccess.md`；`ISmartComponentFeatureData/ReleaseSelectionAccess.md`；`ISplitBodyFeatureData/ReleaseSelectionAccess.md`；`ISplitLineFeatureData/ReleaseSelectionAccess.md`；`IStructuralMemberFeatureData/ReleaseSelectionAccess.md`；`IStructureSystemMemberFeatureData/ReleaseSelectionAccess.md`；`ISurfExtrudeFeatureData/ReleaseSelectionAccess.md`；`ISurfRevolveFeatureData/ReleaseSelectionAccess.md`；`ISurfaceCutFeatureData/ReleaseSelectionAccess.md`；`ISurfaceExtendFeatureData/ReleaseSelectionAccess.md`；`ISurfaceFlattenFeatureData/ReleaseSelectionAccess.md`；`ISurfaceKnitFeatureData/ReleaseSelectionAccess.md`；`ISurfaceOffsetFeatureData/ReleaseSelectionAccess.md`；`ISurfacePlanarFeatureData/ReleaseSelectionAccess.md`；`ISurfaceRadiateFeatureData/ReleaseSelectionAccess.md`；`ISurfaceTrimFeatureData/ReleaseSelectionAccess.md`；`ISweepFeatureData/ReleaseSelectionAccess.md`；`ISweptFlangeFeatureData/ReleaseSelectionAccess.md`；`ITabAndSlotFeatureData/ReleaseSelectionAccess.md`；`ITablePatternFeatureData/ReleaseSelectionAccess.md`；`IThickenFeatureData/ReleaseSelectionAccess.md`；`IThreadFeatureData/ReleaseSelectionAccess.md`；`IToolingSplitFeatureData/ReleaseSelectionAccess.md`；`IVariableFilletFeatureData2/ReleaseSelectionAccess.md`；`IWeldmentBeadFeatureData/ReleaseSelectionAccess.md`；`IWeldmentTrimExtendFeatureData/ReleaseSelectionAccess.md`；`IWizardHoleFeatureData2/ReleaseSelectionAccess.md`；`IWrapSketchFeatureData/ReleaseSelectionAccess.md` |
| Type | 36 | `IBodyFolder/Type.md`；`ICalloutVariable/Type.md`；`ICamera/Type.md`；`IChamferFeatureData2/Type.md`；`IConfiguration/Type.md`；`ICornerTreatmentGroupFolder/Type.md`；`ICustomBendAllowance/Type.md`；`IDimXpertAnnotation/Type.md`；`IDimXpertBlockTolerances/Type.md`；`IDimXpertFeature/Type.md`；`IDimensionTolerance/Type.md`；`IDraftFeatureData2/Type.md`；`IHemFeatureData/Type.md`；`IHoleSeriesFeatureData2/Type.md`；`IMate2/Type.md`；`IMotionPlotAxisFeatureData/Type.md`；`IRefAxisFeatureData/Type.md`；`IRefPlaneFeatureData/Type.md`；`IRefPointFeatureData/Type.md`；`IRevolveFeatureData2/Type.md`；`IRibFeatureData2/Type.md`；`IRuledSurfaceFeatureData/Type.md`；`IScaleFeatureData/Type.md`；`ISimpleFilletFeatureData2/Type.md`；`ISimpleHoleFeatureData2/Type.md`；`ISimulationDamperFeatureData/Type.md`；`ISimulationSpringFeatureData/Type.md`；`ISketchPoint/Type.md`；`ISurfRevolveFeatureData/Type.md`；`ISurfaceExtendFeatureData/Type.md`；`ITableAnchor/Type.md`；`ITableAnnotation/Type.md`；`IThreadFeatureData/Type.md`；`IView/Type.md`；`IWizardHoleFeatureData2/Type.md`；`IWrapSketchFeatureData/Type.md` |
| GetFeature | 28 | `IBendTable/GetFeature.md`；`IBodyFolder/GetFeature.md`；`IBomFeature/GetFeature.md`；`ICommentFolder/GetFeature.md`；`ICornerManagementFolder/GetFeature.md`；`ICornerTreatmentFeatureData/GetFeature.md`；`ICornerTreatmentGroupFolder/GetFeature.md`；`IDimXpertCompositeDistanceBetweenDimTol/GetFeature.md`；`IDimXpertDistanceBetweenDimTol/GetFeature.md`；`IDimXpertPart/GetFeature.md`；`IFace2/GetFeature.md`；`IFamilyTableFeature/GetFeature.md`；`IFlatPatternFolder/GetFeature.md`；`IGeneralTableFeature/GetFeature.md`；`IGeneralToleranceTableFeature/GetFeature.md`；`IHoleTable/GetFeature.md`；`IProfileGroupFolder/GetFeature.md`；`IPunchTable/GetFeature.md`；`IRevisionTableFeature/GetFeature.md`；`ISheetMetalFolder/GetFeature.md`；`ISketchBlockDefinition/GetFeature.md`；`ISketchPicture/GetFeature.md`；`IStructureSystemFolder/GetFeature.md`；`IStructureSystemMemberFeatureData/GetFeature.md`；`ITableAnchor/GetFeature.md`；`ITitleBlock/GetFeature.md`；`ITitleBlockTableFeature/GetFeature.md`；`IWeldmentCutListFeature/GetFeature.md` |
| Angle | 27 | `IAngleMateFeatureData/Angle.md`；`ICalloutAngleVariable/Angle.md`；`ICountersinkElementData/Angle.md`；`IDimXpertChamferFeature/Angle.md`；`IDraftFeatureData2/Angle.md`；`IFaceHatch/Angle.md`；`IGtol/Angle.md`；`IHemFeatureData/Angle.md`；`IHingeMateFeatureData/Angle.md`；`IMagneticLine/Angle.md`；`IMaterialVisualPropertiesData/Angle.md`；`IMeasure/Angle.md`；`IMoveFaceFeatureData/Angle.md`；`INote/Angle.md`；`IPartingLineFeatureData/Angle.md`；`IRefPlaneFeatureData/Angle.md`；`IRevisionCloud/Angle.md`；`IRuledSurfaceFeatureData/Angle.md`；`ISketchBlockInstance/Angle.md`；`ISketchHatch/Angle.md`；`ISketchLine/Angle.md`；`ISketchPicture/Angle.md`；`ISplitLineFeatureData/Angle.md`；`IStructuralMemberGroup/Angle.md`；`ITexture/Angle.md`；`IToolingSplitFeatureData/Angle.md`；`IView/Angle.md` |
| Name | 24 | `IBody2/Name.md`；`IBomFeature/Name.md`；`ICommandGroup/Name.md`；`ICommandTab/Name.md`；`IComment/Name.md`；`IComponent2/Name.md`；`IConfiguration/Name.md`；`IDimXpertAnnotation/Name.md`；`IDimXpertFeature/Name.md`；`IDimension/Name.md`；`IDrawingComponent/Name.md`；`IExplodeStep/Name.md`；`IFeature/Name.md`；`ILayer/Name.md`；`IManipulator/Name.md`；`IMateLoadReference/Name.md`；`IMateReference/Name.md`；`IMotionStudy/Name.md`；`IPartExplodeStep/Name.md`；`ISketchBlockInstance/Name.md`；`ISnapShot/Name.md`；`ITextAndCustomProperty/Name.md`；`IView/Name.md`；`IView3D/Name.md` |
| GetNext | 22 | `IAnnotation/GetNext.md`；`ICThread/GetNext.md`；`ICenterLine/GetNext.md`；`ICenterMark/GetNext.md`；`ICenterOfMass/GetNext.md`；`ICoEdge/GetNext.md`；`IDatumOrigin/GetNext.md`；`IDatumTag/GetNext.md`；`IDatumTargetSym/GetNext.md`；`IDisplayDimension/GetNext.md`；`IDowelSymbol/GetNext.md`；`ILoop2/GetNext.md`；`IModelDoc2/GetNext.md`；`IModelView/GetNext.md`；`IMultiJogLeader/GetNext.md`；`INote/GetNext.md`；`IRevisionCloud/GetNext.md`；`ISFSymbol/GetNext.md`；`ITableAnnotation/GetNext.md`；`ITreeControlItem/GetNext.md`；`IWeldBead/GetNext.md`；`IWeldSymbol/GetNext.md` |
| EntitiesToMate | 17 | `IAngleMateFeatureData/EntitiesToMate.md`；`ICamFollowerMateFeatureData/EntitiesToMate.md`；`ICoincidentMateFeatureData/EntitiesToMate.md`；`IConcentricMateFeatureData/EntitiesToMate.md`；`IDistanceMateFeatureData/EntitiesToMate.md`；`IGearMateFeatureData/EntitiesToMate.md`；`IHingeMateFeatureData/EntitiesToMate.md`；`ILockMateFeatureData/EntitiesToMate.md`；`IParallelMateFeatureData/EntitiesToMate.md`；`IPerpendicularMateFeatureData/EntitiesToMate.md`；`IProfileCenterMateFeatureData/EntitiesToMate.md`；`IRackPinionMateFeatureData/EntitiesToMate.md`；`IScrewMateFeatureData/EntitiesToMate.md`；`ISlotMateFeatureData/EntitiesToMate.md`；`ISymmetricMateFeatureData/EntitiesToMate.md`；`ITangentMateFeatureData/EntitiesToMate.md`；`IUniversalJointMateFeatureData/EntitiesToMate.md` |
| Style | 17 | `IAnnotation/Style.md`；`IAutoBalloonOptions/Style.md`；`IBalloonOptions/Style.md`；`IBreakLine/Style.md`；`ICenterMark/Style.md`；`IDrawingComponent/Style.md`；`ILayer/Style.md`；`IPropertyManagerPageCombobox/Style.md`；`IPropertyManagerPageLabel/Style.md`；`IPropertyManagerPageListbox/Style.md`；`IPropertyManagerPageNumberbox/Style.md`；`IPropertyManagerPageOption/Style.md`；`IPropertyManagerPageSelectionbox/Style.md`；`IPropertyManagerPageSlider/Style.md`；`IPropertyManagerPageTextbox/Style.md`；`ISketchSegment/Style.md`；`IStackedBalloonOptions/Style.md` |
| Visible | 16 | `IAnnotation/Visible.md`；`IBody2/Visible.md`；`ICommandTab/Visible.md`；`IComponent2/Visible.md`；`IDrawingComponent/Visible.md`；`IFeature/Visible.md`；`ILayer/Visible.md`；`IManipulator/Visible.md`；`IModelDoc2/Visible.md`；`INote/Visible.md`；`IProjectionArrow/Visible.md`；`IPropertyManagerPageControl/Visible.md`；`IPropertyManagerPageGroup/Visible.md`；`ISketchBlockInstance/Visible.md`；`ISldWorks/Visible.md`；`IStatusBarPane/Visible.md` |
| FeatureScope | 15 | `IBoundaryBossFeatureData/FeatureScope.md`；`ICircularPatternFeatureData/FeatureScope.md`；`ICurveDrivenPatternFeatureData/FeatureScope.md`；`IExtrudeFeatureData2/FeatureScope.md`；`IFillPatternFeatureData/FeatureScope.md`；`ILinearPatternFeatureData/FeatureScope.md`；`ILoftFeatureData/FeatureScope.md`；`IMirrorPatternFeatureData/FeatureScope.md`；`IRevolveFeatureData2/FeatureScope.md`；`ISimpleHoleFeatureData2/FeatureScope.md`；`ISketchPatternFeatureData/FeatureScope.md`；`ISurfaceCutFeatureData/FeatureScope.md`；`ISweepFeatureData/FeatureScope.md`；`IThickenFeatureData/FeatureScope.md`；`IWizardHoleFeatureData2/FeatureScope.md` |
| GetType | 13 | `IAnnotation/GetType.md`；`IBody2/GetType.md`；`IComponent2/GetType.md`；`ICustomPropertyManager/GetType.md`；`IDimension/GetType.md`；`IDisplayDimension/GetType.md`；`IEntity/GetType.md`；`IModelDoc2/GetType.md`；`IOneBendFeatureData/GetType.md`；`IParameter/GetType.md`；`ISketchSegment/GetType.md`；`ISplitLineFeatureData/GetType.md`；`ISurfaceTrimFeatureData/GetType.md` |
| MateAlignment | 12 | `IAngleMateFeatureData/MateAlignment.md`；`ICamFollowerMateFeatureData/MateAlignment.md`；`ICoincidentMateFeatureData/MateAlignment.md`；`IConcentricMateFeatureData/MateAlignment.md`；`IDistanceMateFeatureData/MateAlignment.md`；`IHingeMateFeatureData/MateAlignment.md`；`IParallelMateFeatureData/MateAlignment.md`；`IProfileCenterMateFeatureData/MateAlignment.md`；`IScrewMateFeatureData/MateAlignment.md`；`ISlotMateFeatureData/MateAlignment.md`；`ISymmetricMateFeatureData/MateAlignment.md`；`ITangentMateFeatureData/MateAlignment.md` |
| Select2 | 12 | `IAnnotation/Select2.md`；`IBody2/Select2.md`；`IComponent2/Select2.md`；`IConfiguration/Select2.md`；`IEntity/Select2.md`；`IFeature/Select2.md`；`ISilhouetteEdge/Select2.md`；`ISketchContour/Select2.md`；`ISketchHatch/Select2.md`；`ISketchPoint/Select2.md`；`ISketchRegion/Select2.md`；`ISketchSegment/Select2.md` |
| Thickness | 11 | `IBaseFlangeFeatureData/Thickness.md`；`IEndCapFeatureData/Thickness.md`；`IGussetFeatureData/Thickness.md`；`IIndentFeatureData/Thickness.md`；`ILoftedBendsFeatureData/Thickness.md`；`IRibFeatureData2/Thickness.md`；`ISheetMetalFeatureData/Thickness.md`；`IShellFeatureData/Thickness.md`；`ISweptFlangeFeatureData/Thickness.md`；`IThickenFeatureData/Thickness.md`；`IWrapSketchFeatureData/Thickness.md` |
| BendRadius | 10 | `IBaseFlangeFeatureData/BendRadius.md`；`IBendsFeatureData/BendRadius.md`；`IConvertSolidFeatureData/BendRadius.md`；`IEdgeFlangeFeatureData/BendRadius.md`；`IJogFeatureData/BendRadius.md`；`IMiterFlangeFeatureData/BendRadius.md`；`IOneBendFeatureData/BendRadius.md`；`ISheetMetalFeatureData/BendRadius.md`；`ISketchedBendFeatureData/BendRadius.md`；`ISweptFlangeFeatureData/BendRadius.md` |
| GetArcCount | 10 | `IDatumTag/GetArcCount.md`；`IDatumTargetSym/GetArcCount.md`；`IDisplayData/GetArcCount.md`；`IGtol/GetArcCount.md`；`INote/GetArcCount.md`；`ISFSymbol/GetArcCount.md`；`ISketch/GetArcCount.md`；`ISketchBlockDefinition/GetArcCount.md`；`IView/GetArcCount.md`；`IWeldSymbol/GetArcCount.md` |
| OffsetDistance | 10 | `IAdvancedHoleElementData/OffsetDistance.md`；`IEdgeFlangeFeatureData/OffsetDistance.md`；`IEndCapFeatureData/OffsetDistance.md`；`IJogFeatureData/OffsetDistance.md`；`IMoveFaceFeatureData/OffsetDistance.md`；`IPartingSurfaceFeatureData/OffsetDistance.md`；`IProfileCenterMateFeatureData/OffsetDistance.md`；`ISMGussetFeatureData/OffsetDistance.md`；`IThreadFeatureData/OffsetDistance.md`；`IWizardHoleFeatureData2/OffsetDistance.md` |
| GetName | 9 | `IAnnotation/GetName.md`；`IAttribute/GetName.md`；`IDetailCircle/GetName.md`；`IDrSection/GetName.md`；`INote/GetName.md`；`IParameter/GetName.md`；`ISelectionSet/GetName.md`；`ISheet/GetName.md`；`ISketchSegment/GetName.md` |
| GetSkippedItemCount | 9 | `ICircularPatternFeatureData/GetSkippedItemCount.md`；`ICurveDrivenPatternFeatureData/GetSkippedItemCount.md`；`IDerivedPatternFeatureData/GetSkippedItemCount.md`；`ILinearPatternFeatureData/GetSkippedItemCount.md`；`ILocalCircularPatternFeatureData/GetSkippedItemCount.md`；`ILocalCurvePatternFeatureData/GetSkippedItemCount.md`；`ILocalLinearPatternFeatureData/GetSkippedItemCount.md`；`ILocalSketchPatternFeatureData/GetSkippedItemCount.md`；`ITablePatternFeatureData/GetSkippedItemCount.md` |
| Length | 9 | `IBalloonStack/Length.md`；`ICalloutLengthVariable/Length.md`；`IDragArrowManipulator/Length.md`；`IHemFeatureData/Length.md`；`IMagneticLine/Length.md`；`IMeasure/Length.md`；`IPrimaryMemberPointLengthFeatureData/Length.md`；`ISketchSlot/Length.md`；`IWizardHoleFeatureData2/Length.md` |
| PropagateVisualProperty | 9 | `ICircularPatternFeatureData/PropagateVisualProperty.md`；`ICurveDrivenPatternFeatureData/PropagateVisualProperty.md`；`IDerivedPatternFeatureData/PropagateVisualProperty.md`；`IFillPatternFeatureData/PropagateVisualProperty.md`；`ILinearPatternFeatureData/PropagateVisualProperty.md`；`IMirrorPatternFeatureData/PropagateVisualProperty.md`；`IMirrorSolidFeatureData/PropagateVisualProperty.md`；`ISketchPatternFeatureData/PropagateVisualProperty.md`；`ITablePatternFeatureData/PropagateVisualProperty.md` |
| Width | 9 | `IAnnotation/Width.md`；`IDrawingComponent/Width.md`；`ILayer/Width.md`；`IPMIDatumTarget/Width.md`；`IPlaneManipulator/Width.md`；`IPropertyManagerPageControl/Width.md`；`IRenderMaterial/Width.md`；`ISketchSegment/Width.md`；`ISketchSlot/Width.md` |
| Activate | 8 | `IAnnotationView/Activate.md`；`ICommandGroup/Activate.md`；`IModelView/Activate.md`；`IModelWindow/Activate.md`；`IMotionStudy/Activate.md`；`IPropertyManagerPageTab/Activate.md`；`ISnapShot/Activate.md`；`IView3D/Activate.md` |
| Diameter | 8 | `IAdvancedHoleElementData/Diameter.md`；`ICosmeticThreadFeatureData/Diameter.md`；`IFillPatternFeatureData/Diameter.md`；`IMeasure/Diameter.md`；`IPMIDatumTarget/Diameter.md`；`ISimpleHoleFeatureData2/Diameter.md`；`IThreadFeatureData/Diameter.md`；`IWizardHoleFeatureData2/Diameter.md` |
| GetEdges | 8 | `IBody2/GetEdges.md`；`IFace2/GetEdges.md`；`ILoop2/GetEdges.md`；`IRuledSurfaceFeatureData/GetEdges.md`；`ISketchContour/GetEdges.md`；`ISketchRegion/GetEdges.md`；`ISketchText/GetEdges.md`；`IVertex/GetEdges.md` |
| GetFaces | 8 | `IBody2/GetFaces.md`；`IDimXpertFeature/GetFaces.md`；`IFeature/GetFaces.md`；`IMateLoadReference/GetFaces.md`；`IMidSurface3/GetFaces.md`；`ISMCornerReliefData/GetFaces.md`；`ISimpleFilletFeatureData2/GetFaces.md`；`IWeldmentBeadFeatureData/GetFaces.md` |
| Scale | 8 | `IFaceHatch/Scale.md`；`IMathPoint/Scale.md`；`IMathVector/Scale.md`；`IModelDoc2/Scale.md`；`IModelView/Scale.md`；`ISketchBlockInstance/Scale.md`；`ISketchHatch/Scale.md`；`IView3D/Scale.md` |
| GeometryPattern | 7 | `ICircularPatternFeatureData/GeometryPattern.md`；`ICurveDrivenPatternFeatureData/GeometryPattern.md`；`IFillPatternFeatureData/GeometryPattern.md`；`ILinearPatternFeatureData/GeometryPattern.md`；`IMirrorPatternFeatureData/GeometryPattern.md`；`ISketchPatternFeatureData/GeometryPattern.md`；`ITablePatternFeatureData/GeometryPattern.md` |
| GetEdgeCount | 7 | `IBody2/GetEdgeCount.md`；`IChamferFeatureData2/GetEdgeCount.md`；`IEdgeFlangeFeatureData/GetEdgeCount.md`；`IFace2/GetEdgeCount.md`；`ILoop2/GetEdgeCount.md`；`IShutOffSurfaceFeatureData/GetEdgeCount.md`；`ISimpleFilletFeatureData2/GetEdgeCount.md` |
| Scale2 | 7 | `IDisplayDimension/Scale2.md`；`IFaceHatch/Scale2.md`；`IMaterialVisualPropertiesData/Scale2.md`；`IModelView/Scale2.md`；`IPageSetup/Scale2.md`；`ISketchBlockInstance/Scale2.md`；`ISketchHatch/Scale2.md` |
| FileName | 6 | `IDesignTable/FileName.md`；`IDocumentSpecification/FileName.md`；`IRenderMaterial/FileName.md`；`ISaveTo3DExperienceOptions/FileName.md`；`ISketchBlockDefinition/FileName.md`；`ISwOLEObject/FileName.md` |
| GetComponents | 6 | `IAssemblyDoc/GetComponents.md`；`IBomTableAnnotation/GetComponents.md`；`ICollision/GetComponents.md`；`ICollisionDetectionGroup/GetComponents.md`；`IExplodeStep/GetComponents.md`；`IHoleSeriesFeatureData2/GetComponents.md` |
| GetFeatureCount | 6 | `IBody2/GetFeatureCount.md`；`IDimXpertPart/GetFeatureCount.md`；`IFeatureFolder/GetFeatureCount.md`；`IFeatureManager/GetFeatureCount.md`；`IModelDoc2/GetFeatureCount.md`；`ISimpleFilletFeatureData2/GetFeatureCount.md` |
| GetPatternBodyCount | 6 | `ICircularPatternFeatureData/GetPatternBodyCount.md`；`ICurveDrivenPatternFeatureData/GetPatternBodyCount.md`；`ILinearPatternFeatureData/GetPatternBodyCount.md`；`IMirrorSolidFeatureData/GetPatternBodyCount.md`；`ISketchPatternFeatureData/GetPatternBodyCount.md`；`ITablePatternFeatureData/GetPatternBodyCount.md` |
| GetPatternFeatureCount | 6 | `ICircularPatternFeatureData/GetPatternFeatureCount.md`；`ICurveDrivenPatternFeatureData/GetPatternFeatureCount.md`；`ILinearPatternFeatureData/GetPatternFeatureCount.md`；`IMirrorPatternFeatureData/GetPatternFeatureCount.md`；`ISketchPatternFeatureData/GetPatternFeatureCount.md`；`ITablePatternFeatureData/GetPatternFeatureCount.md` |
| CustomPropertyManager | 5 | `IComponent2/CustomPropertyManager.md`；`IConfiguration/CustomPropertyManager.md`；`ICutListItem/CustomPropertyManager.md`；`IFeature/CustomPropertyManager.md`；`IModelDocExtension/CustomPropertyManager.md` |
| Delete | 5 | `IAttribute/Delete.md`；`IComment/Delete.md`；`ICustomPropertyManager/Delete.md`；`IEquationMgr/Delete.md`；`IMateLoadReference/Delete.md` |
| Description | 5 | `IAdvancedSaveAsOptions/Description.md`；`IConfiguration/Description.md`；`IFeature/Description.md`；`ILayer/Description.md`；`ITextAndCustomProperty/Description.md` |
| GetEntitiesCount | 5 | `IBreakCornerFeatureData/GetEntitiesCount.md`；`IRenderMaterial/GetEntitiesCount.md`；`ISketchRelation/GetEntitiesCount.md`；`ISurfaceKnitFeatureData/GetEntitiesCount.md`；`ISurfaceOffsetFeatureData/GetEntitiesCount.md` |
| GetPatternFaceCount | 5 | `ICircularPatternFeatureData/GetPatternFaceCount.md`；`ICurveDrivenPatternFeatureData/GetPatternFaceCount.md`；`ILinearPatternFeatureData/GetPatternFaceCount.md`；`ISketchPatternFeatureData/GetPatternFaceCount.md`；`ITablePatternFeatureData/GetPatternFaceCount.md` |
| KFactor | 5 | `IBaseFlangeFeatureData/KFactor.md`；`IBendsFeatureData/KFactor.md`；`ICustomBendAllowance/KFactor.md`；`IOneBendFeatureData/KFactor.md`；`ISheetMetalFeatureData/KFactor.md` |
| PatternElement | 5 | `ICircularPatternFeatureData/PatternElement.md`；`ICurveDrivenPatternFeatureData/PatternElement.md`；`IFillPatternFeatureData/PatternElement.md`；`ILinearPatternFeatureData/PatternElement.md`；`ISketchPatternFeatureData/PatternElement.md` |
| ProfileType | 5 | `IGussetFeatureData/ProfileType.md`；`IProfileGroupFolder/ProfileType.md`；`ISMGussetFeatureData/ProfileType.md`；`ISpring/ProfileType.md`；`IStructureSystemMemberProfile/ProfileType.md` |
| Select4 | 5 | `IComponent2/Select4.md`；`IEntity/Select4.md`；`ISketchHatch/Select4.md`；`ISketchPoint/Select4.md`；`ISketchSegment/Select4.md` |
| Title | 5 | `IMessageBarDefinition/Title.md`；`IModelWindow/Title.md`；`IPropertyManagerPage2/Title.md`；`ITableAnnotation/Title.md`；`IUserNotificationDefinition/Title.md` |
| BodyPattern | 4 | `ICircularPatternFeatureData/BodyPattern.md`；`ICurveDrivenPatternFeatureData/BodyPattern.md`；`ILinearPatternFeatureData/BodyPattern.md`；`ISketchPatternFeatureData/BodyPattern.md` |
| Component | 4 | `IDrawingComponent/Component.md`；`IMateInPlace/Component.md`；`IMateLoadReference/Component.md`；`IMotionPlotAxisFeatureData/Component.md` |
| ConfigurationName | 4 | `IDocumentSpecification/ConfigurationName.md`；`ILibraryFeatureData/ConfigurationName.md`；`IStructuralMemberFeatureData/ConfigurationName.md`；`IView3D/ConfigurationName.md` |
| Count | 4 | `IBalloonStack/Count.md`；`ICustomPropertyManager/Count.md`；`IFaultEntity/Count.md`；`IParagraphs/Count.md` |
| D1ReverseDirection | 4 | `ICurveDrivenPatternFeatureData/D1ReverseDirection.md`；`ILinearPatternFeatureData/D1ReverseDirection.md`；`ILocalCurvePatternFeatureData/D1ReverseDirection.md`；`ILocalLinearPatternFeatureData/D1ReverseDirection.md` |
| D1Spacing | 4 | `ICurveDrivenPatternFeatureData/D1Spacing.md`；`ILinearPatternFeatureData/D1Spacing.md`；`ILocalCurvePatternFeatureData/D1Spacing.md`；`ILocalLinearPatternFeatureData/D1Spacing.md` |
| D2PatternSeedOnly | 4 | `ICurveDrivenPatternFeatureData/D2PatternSeedOnly.md`；`ILinearPatternFeatureData/D2PatternSeedOnly.md`；`ILocalCurvePatternFeatureData/D2PatternSeedOnly.md`；`ILocalLinearPatternFeatureData/D2PatternSeedOnly.md` |
| D2ReverseDirection | 4 | `ICurveDrivenPatternFeatureData/D2ReverseDirection.md`；`ILinearPatternFeatureData/D2ReverseDirection.md`；`ILocalCurvePatternFeatureData/D2ReverseDirection.md`；`ILocalLinearPatternFeatureData/D2ReverseDirection.md` |
| D2Spacing | 4 | `ICurveDrivenPatternFeatureData/D2Spacing.md`；`ILinearPatternFeatureData/D2Spacing.md`；`ILocalCurvePatternFeatureData/D2Spacing.md`；`ILocalLinearPatternFeatureData/D2Spacing.md` |
| FeatureByName | 4 | `IAssemblyDoc/FeatureByName.md`；`IComponent2/FeatureByName.md`；`IDrawingDoc/FeatureByName.md`；`IPartDoc/FeatureByName.md` |
| FlipDimension | 4 | `IAngleMateFeatureData/FlipDimension.md`；`IDistanceMateFeatureData/FlipDimension.md`；`IProfileCenterMateFeatureData/FlipDimension.md`；`IWidthMateFeatureData/FlipDimension.md` |
| GetBodies | 4 | `IBodyFolder/GetBodies.md`；`IComponent2/GetBodies.md`；`IPartDoc/GetBodies.md`；`IPartExplodeStep/GetBodies.md` |
| GetCurve | 4 | `ICoEdge/GetCurve.md`；`IEdge/GetCurve.md`；`ISilhouetteEdge/GetCurve.md`；`ISketchSegment/GetCurve.md` |
| GetEndPoint2 | 4 | `ISketchArc/GetEndPoint2.md`；`ISketchEllipse/GetEndPoint2.md`；`ISketchLine/GetEndPoint2.md`；`ISketchParabola/GetEndPoint2.md` |
| GetMassProperties | 4 | `IBody2/GetMassProperties.md`；`IModelDoc2/GetMassProperties.md`；`IModelDocExtension/GetMassProperties.md`；`ISldWorks/GetMassProperties.md` |
| GetPointCount | 4 | `IDisplayData/GetPointCount.md`；`IFreePointCurveFeatureData/GetPointCount.md`；`ISketchSpline/GetPointCount.md`；`ITablePatternFeatureData/GetPointCount.md` |
| GetRelations | 4 | `ISketchPath/GetRelations.md`；`ISketchPoint/GetRelations.md`；`ISketchRelationManager/GetRelations.md`；`ISketchSegment/GetRelations.md` |
| GetRelationsCount | 4 | `ISketchPath/GetRelationsCount.md`；`ISketchPoint/GetRelationsCount.md`；`ISketchRelationManager/GetRelationsCount.md`；`ISketchSegment/GetRelationsCount.md` |
| GetSketchSegments | 4 | `ISketch/GetSketchSegments.md`；`ISketchContour/GetSketchSegments.md`；`ISketchPath/GetSketchSegments.md`；`IStructuralMemberFeatureData/GetSketchSegments.md` |
| GetStartPoint2 | 4 | `ISketchArc/GetStartPoint2.md`；`ISketchEllipse/GetStartPoint2.md`；`ISketchLine/GetStartPoint2.md`；`ISketchParabola/GetStartPoint2.md` |
| IsSuppressed | 4 | `IComponent2/IsSuppressed.md`；`IDimXpertAnnotation/IsSuppressed.md`；`IDimXpertFeature/IsSuppressed.md`；`IFeature/IsSuppressed.md` |
| ListExternalFileReferencesCount | 4 | `IComponent2/ListExternalFileReferencesCount.md`；`IFeature/ListExternalFileReferencesCount.md`；`IModelDoc2/ListExternalFileReferencesCount.md`；`IModelDocExtension/ListExternalFileReferencesCount.md` |
| Transform | 4 | `IComponent2/Transform.md`；`ICoordinateSystemFeatureData/Transform.md`；`IModelView/Transform.md`；`IRefPlane/Transform.md` |
| X | 4 | `IMeasure/X.md`；`ISelectData/X.md`；`ISketchPoint/X.md`；`ISplineHandle/X.md` |
| Y | 4 | `IMeasure/Y.md`；`ISelectData/Y.md`；`ISketchPoint/Y.md`；`ISplineHandle/Y.md` |
| ArrayData | 3 | `IMathPoint/ArrayData.md`；`IMathTransform/ArrayData.md`；`IMathVector/ArrayData.md` |
| Close | 3 | `ILoftFeatureData/Close.md`；`IModelDoc2/Close.md`；`IPropertyManagerPage2/Close.md` |
| CreateArc | 3 | `IModelDoc2/CreateArc.md`；`IModeler/CreateArc.md`；`ISketchManager/CreateArc.md` |
| CreateEllipse | 3 | `IModelDoc2/CreateEllipse.md`；`IModeler/CreateEllipse.md`；`ISketchManager/CreateEllipse.md` |
| CreateLine | 3 | `IModelDoc2/CreateLine.md`；`IModeler/CreateLine.md`；`ISketchManager/CreateLine.md` |
| DisplayMode | 3 | `IModelDocExtension/DisplayMode.md`；`IModelView/DisplayMode.md`；`IView3D/DisplayMode.md` |
| EndConditionOverride | 3 | `ICounterboreElementData/EndConditionOverride.md`；`ICountersinkElementData/EndConditionOverride.md`；`ITaperedTapElementData/EndConditionOverride.md` |
| FirstFeature | 3 | `IComponent2/FirstFeature.md`；`IModelDoc2/FirstFeature.md`；`IPartDoc/FirstFeature.md` |
| GetAnnotationCount | 3 | `IDimXpertPart/GetAnnotationCount.md`；`IModelDocExtension/GetAnnotationCount.md`；`IView/GetAnnotationCount.md` |
| GetAnnotations | 3 | `IDimXpertPart/GetAnnotations.md`；`IModelDocExtension/GetAnnotations.md`；`IView/GetAnnotations.md` |
| GetComponentCount | 3 | `IAssemblyDoc/GetComponentCount.md`；`ICollisionDetectionGroup/GetComponentCount.md`；`IInterference/GetComponentCount.md` |
| GetConfigurationNames | 3 | `IComponent2/GetConfigurationNames.md`；`IModelDoc2/GetConfigurationNames.md`；`ISldWorks/GetConfigurationNames.md` |
| GetContoursCount | 3 | `IExtrudeFeatureData2/GetContoursCount.md`；`IRevolveFeatureData2/GetContoursCount.md`；`ISplitLineFeatureData/GetContoursCount.md` |
| GetCount | 3 | `IColorTable/GetCount.md`；`IEquationMgr/GetCount.md`；`ILayerMgr/GetCount.md` |
| GetDisplayDimensions | 3 | `IMacroFeatureData/GetDisplayDimensions.md`；`ISketchBlockDefinition/GetDisplayDimensions.md`；`IView/GetDisplayDimensions.md` |
| GetLoopCount | 3 | `IFace2/GetLoopCount.md`；`IShutOffSurfaceFeatureData/GetLoopCount.md`；`ISimpleFilletFeatureData2/GetLoopCount.md` |
| GetModelDoc | 3 | `IComponent2/GetModelDoc.md`；`IDerivedPartFeatureData/GetModelDoc.md`；`IMirrorPartFeatureData/GetModelDoc.md` |
| GetPartingLinesCount | 3 | `IDraftFeatureData2/GetPartingLinesCount.md`；`IPartingLineFeatureData/GetPartingLinesCount.md`；`IPartingSurfaceFeatureData/GetPartingLinesCount.md` |
| GetSplines | 3 | `ISketch/GetSplines.md`；`ISketchBlockDefinition/GetSplines.md`；`IView/GetSplines.md` |
| GetUserPreferenceToggle | 3 | `IModelDoc2/GetUserPreferenceToggle.md`；`IModelDocExtension/GetUserPreferenceToggle.md`；`ISldWorks/GetUserPreferenceToggle.md` |
| MaterialIdName | 3 | `IFace2/MaterialIdName.md`；`IModelDoc2/MaterialIdName.md`；`IPartDoc/MaterialIdName.md` |
| MirrorProfile | 3 | `IStructuralMemberGroup/MirrorProfile.md`；`IStructureSystemMemberProfile/MirrorProfile.md`；`IThreadFeatureData/MirrorProfile.md` |
| SetUserPreferenceToggle | 3 | `IModelDoc2/SetUserPreferenceToggle.md`；`IModelDocExtension/SetUserPreferenceToggle.md`；`ISldWorks/SetUserPreferenceToggle.md` |
| Specular | 3 | `IAppearanceSetting/Specular.md`；`IDSPBRMaterial/Specular.md`；`IRenderMaterial/Specular.md` |
| ThreadClass | 3 | `IStraightTapElementData/ThreadClass.md`；`ITaperedTapElementData/ThreadClass.md`；`IWizardHoleFeatureData2/ThreadClass.md` |
| Transparency | 3 | `IDSPBRMaterial/Transparency.md`；`IModelDocExtension/Transparency.md`；`IRenderMaterial/Transparency.md` |
| Unit | 3 | `IPMIDatumTarget/Unit.md`；`IPMIDimensionItem/Unit.md`；`IPMIGtolBoxData/Unit.md` |
| UseStandardDepth | 3 | `ICounterboreElementData/UseStandardDepth.md`；`ICountersinkElementData/UseStandardDepth.md`；`ITaperedTapElementData/UseStandardDepth.md` |
| VarySketch | 3 | `ICircularPatternFeatureData/VarySketch.md`；`ICurveDrivenPatternFeatureData/VarySketch.md`；`ILinearPatternFeatureData/VarySketch.md` |
| Add2 | 2 | `ICustomPropertyManager/Add2.md`；`IEquationMgr/Add2.md` |
| AddRelation | 2 | `IModelDoc2/AddRelation.md`；`ISketchRelationManager/AddRelation.md` |
| BlendColor | 2 | `IMaterialVisualPropertiesData/BlendColor.md`；`ITexture/BlendColor.md` |
| Create3PointArc | 2 | `IModelDoc2/Create3PointArc.md`；`ISketchManager/Create3PointArc.md` |
| CreateBsplineSurface | 2 | `IBody2/CreateBsplineSurface.md`；`IModeler/CreateBsplineSurface.md` |
| CreateCenterLine | 2 | `IModelDoc2/CreateCenterLine.md`；`ISketchManager/CreateCenterLine.md` |
| CreateCircleByRadius | 2 | `IModelDoc2/CreateCircleByRadius.md`；`ISketchManager/CreateCircleByRadius.md` |
| CreateCircularSketchStepAndRepeat | 2 | `IModelDoc2/CreateCircularSketchStepAndRepeat.md`；`ISketchManager/CreateCircularSketchStepAndRepeat.md` |
| CreateDefinition | 2 | `IFeatureManager/CreateDefinition.md`；`IMotionStudy/CreateDefinition.md` |
| CreateExtrusionSurface | 2 | `IBody2/CreateExtrusionSurface.md`；`IModeler/CreateExtrusionSurface.md` |
| CreateFeature | 2 | `IFeatureManager/CreateFeature.md`；`IMotionStudy/CreateFeature.md` |
| CreateLinearSketchStepAndRepeat | 2 | `IModelDoc2/CreateLinearSketchStepAndRepeat.md`；`ISketchManager/CreateLinearSketchStepAndRepeat.md` |
| CreateOffsetSurface | 2 | `IBody2/CreateOffsetSurface.md`；`IModeler/CreateOffsetSurface.md` |
| CreatePlanarSurface | 2 | `IBody2/CreatePlanarSurface.md`；`IModeler/CreatePlanarSurface.md` |
| CreateRuledSurface | 2 | `IBody2/CreateRuledSurface.md`；`IModeler/CreateRuledSurface.md` |
| CreateTangentArc | 2 | `IModelDoc2/CreateTangentArc.md`；`ISketchManager/CreateTangentArc.md` |
| CurveType | 2 | `ICurveParamData/CurveType.md`；`ISketchSpline/CurveType.md` |
| CustomSizing | 2 | `IStraightTapElementData/CustomSizing.md`；`ITaperedTapElementData/CustomSizing.md` |
| D1Axis | 2 | `ILinearPatternFeatureData/D1Axis.md`；`ILocalLinearPatternFeatureData/D1Axis.md` |
| D1Direction | 2 | `ICurveDrivenPatternFeatureData/D1Direction.md`；`ILocalCurvePatternFeatureData/D1Direction.md` |
| D1EndCondition | 2 | `ILinearPatternFeatureData/D1EndCondition.md`；`ILocalLinearPatternFeatureData/D1EndCondition.md` |
| D1EndRefOffset | 2 | `ILinearPatternFeatureData/D1EndRefOffset.md`；`ILocalLinearPatternFeatureData/D1EndRefOffset.md` |
| D1EndRefReverseOffset | 2 | `ILinearPatternFeatureData/D1EndRefReverseOffset.md`；`ILocalLinearPatternFeatureData/D1EndRefReverseOffset.md` |
| D1EndSeedReference | 2 | `ILinearPatternFeatureData/D1EndSeedReference.md`；`ILocalLinearPatternFeatureData/D1EndSeedReference.md` |
| D1EndUseSeedReference | 2 | `ILinearPatternFeatureData/D1EndUseSeedReference.md`；`ILocalLinearPatternFeatureData/D1EndUseSeedReference.md` |
| D1EndUseSpacing | 2 | `ILinearPatternFeatureData/D1EndUseSpacing.md`；`ILocalLinearPatternFeatureData/D1EndUseSpacing.md` |
| D1FaceNormal | 2 | `ICurveDrivenPatternFeatureData/D1FaceNormal.md`；`ILocalCurvePatternFeatureData/D1FaceNormal.md` |
| D1IsEqualSpaced | 2 | `ICurveDrivenPatternFeatureData/D1IsEqualSpaced.md`；`ILocalCurvePatternFeatureData/D1IsEqualSpaced.md` |
| D1TotalInstances | 2 | `ILinearPatternFeatureData/D1TotalInstances.md`；`ILocalLinearPatternFeatureData/D1TotalInstances.md` |
| D2Axis | 2 | `ILinearPatternFeatureData/D2Axis.md`；`ILocalLinearPatternFeatureData/D2Axis.md` |
| D2Direction | 2 | `ICurveDrivenPatternFeatureData/D2Direction.md`；`ILocalCurvePatternFeatureData/D2Direction.md` |
| D2EndCondition | 2 | `ILinearPatternFeatureData/D2EndCondition.md`；`ILocalLinearPatternFeatureData/D2EndCondition.md` |
| D2IsEqualSpaced | 2 | `ICurveDrivenPatternFeatureData/D2IsEqualSpaced.md`；`ILocalCurvePatternFeatureData/D2IsEqualSpaced.md` |
| D2TotalInstances | 2 | `ILinearPatternFeatureData/D2TotalInstances.md`；`ILocalLinearPatternFeatureData/D2TotalInstances.md` |
| DeleteAllRelations | 2 | `IModelDoc2/DeleteAllRelations.md`；`ISketchRelationManager/DeleteAllRelations.md` |
| Diffuse | 2 | `IAppearanceSetting/Diffuse.md`；`IRenderMaterial/Diffuse.md` |
| DimensionType | 2 | `IDimXpertDimensionTolerance/DimensionType.md`；`IStructureSystemSplitMember/DimensionType.md` |
| DrillPointAngle | 2 | `IStraightElementData/DrillPointAngle.md`；`IStraightTapElementData/DrillPointAngle.md` |
| DrillPointAngleOverride | 2 | `IStraightElementData/DrillPointAngleOverride.md`；`IStraightTapElementData/DrillPointAngleOverride.md` |
| EndShape | 2 | `IStraightElementData/EndShape.md`；`IStraightTapElementData/EndShape.md` |
| Equation | 2 | `IEquationMgr/Equation.md`；`IStraightTapElementData/Equation.md` |
| FeatureBossThicken | 2 | `IFeatureManager/FeatureBossThicken.md`；`IModelDoc2/FeatureBossThicken.md` |
| FrameHeight | 2 | `IModelView/FrameHeight.md`；`ISldWorks/FrameHeight.md` |
| FrameLeft | 2 | `IModelView/FrameLeft.md`；`ISldWorks/FrameLeft.md` |
| FrameState | 2 | `IModelView/FrameState.md`；`ISldWorks/FrameState.md` |
| FrameTop | 2 | `IModelView/FrameTop.md`；`ISldWorks/FrameTop.md` |
| FrameWidth | 2 | `IModelView/FrameWidth.md`；`ISldWorks/FrameWidth.md` |
| GetArcs2 | 2 | `ISketch/GetArcs2.md`；`IView/GetArcs2.md` |
| GetBodies2 | 2 | `IComponent2/GetBodies2.md`；`IPartDoc/GetBodies2.md` |
| GetConstrainedStatus | 2 | `IComponent2/GetConstrainedStatus.md`；`ISketch/GetConstrainedStatus.md` |
| GetDefinition | 2 | `IAttribute/GetDefinition.md`；`IFeature/GetDefinition.md` |
| GetDependencies | 2 | `IModelDoc2/GetDependencies.md`；`IModelDocExtension/GetDependencies.md` |
| GetDepth | 2 | `IExtrudeFeatureData2/GetDepth.md`；`ISurfExtrudeFeatureData/GetDepth.md` |
| GetEllipses3 | 2 | `ISketch/GetEllipses3.md`；`IView/GetEllipses3.md` |
| GetEndCondition | 2 | `IExtrudeFeatureData2/GetEndCondition.md`；`ISurfExtrudeFeatureData/GetEndCondition.md` |
| GetFrameCount | 2 | `IGtol/GetFrameCount.md`；`IPMIGtolData/GetFrameCount.md` |
| GetLines2 | 2 | `ISketch/GetLines2.md`；`IView/GetLines2.md` |
| GetMateEntityCount | 2 | `IMate2/GetMateEntityCount.md`；`IMateInPlace/GetMateEntityCount.md` |
| GetParabolas2 | 2 | `ISketch/GetParabolas2.md`；`IView/GetParabolas2.md` |
| GetPathName | 2 | `IComponent2/GetPathName.md`；`IModelDoc2/GetPathName.md` |
| GetPoints | 2 | `IPrimaryMemberPointLengthFeatureData/GetPoints.md`；`ISketchSpline/GetPoints.md` |
| GetPolylines | 2 | `ISketch/GetPolylines.md`；`IView/GetPolylines.md` |
| GetRenderMaterials2 | 2 | `IComponent2/GetRenderMaterials2.md`；`IModelDocExtension/GetRenderMaterials2.md` |
| GetRenderMaterialsCount2 | 2 | `IComponent2/GetRenderMaterialsCount2.md`；`IModelDocExtension/GetRenderMaterialsCount2.md` |
| GetSketchPaths | 2 | `ISketch/GetSketchPaths.md`；`ISketchSegment/GetSketchPaths.md` |
| GetSketchPictures | 2 | `ISketch/GetSketchPictures.md`；`IView/GetSketchPictures.md` |
| GetTitle | 2 | `IDesignTable/GetTitle.md`；`IModelDoc2/GetTitle.md` |
| GetUnits | 2 | `IDisplayDimension/GetUnits.md`；`IModelDoc2/GetUnits.md` |
| GetUserPoints2 | 2 | `ISketch/GetUserPoints2.md`；`IView/GetUserPoints2.md` |
| GetUserPreferenceIntegerValue | 2 | `IModelDoc2/GetUserPreferenceIntegerValue.md`；`ISldWorks/GetUserPreferenceIntegerValue.md` |
| GraphicsRedraw | 2 | `IModelDoc2/GraphicsRedraw.md`；`IModelView/GraphicsRedraw.md` |
| HasUnloadedComponents | 2 | `IAssemblyDoc/HasUnloadedComponents.md`；`IComponent2/HasUnloadedComponents.md` |
| InsertCoordinateSystem | 2 | `IFeatureManager/InsertCoordinateSystem.md`；`IModelDoc2/InsertCoordinateSystem.md` |
| InsertCutBlend | 2 | `IFeatureManager/InsertCutBlend.md`；`IModelDoc2/InsertCutBlend.md` |
| InsertCutSurface | 2 | `IFeatureManager/InsertCutSurface.md`；`IModelDoc2/InsertCutSurface.md` |
| InsertDeleteFace | 2 | `IModelDoc2/InsertDeleteFace.md`；`IModelDocExtension/InsertDeleteFace.md` |
| InsertGtol | 2 | `IDimXpertPart/InsertGtol.md`；`IModelDoc2/InsertGtol.md` |
| InsertProtrusionBlend2 | 2 | `IFeatureManager/InsertProtrusionBlend2.md`；`IModelDoc2/InsertProtrusionBlend2.md` |
| InsertRevolvedRefSurface | 2 | `IFeatureManager/InsertRevolvedRefSurface.md`；`IModelDoc2/InsertRevolvedRefSurface.md` |
| InsertRib | 2 | `IFeatureManager/InsertRib.md`；`IModelDoc2/InsertRib.md` |
| InsertSewRefSurface | 2 | `IFeatureManager/InsertSewRefSurface.md`；`IModelDoc2/InsertSewRefSurface.md` |
| InsertSheetMetalMiterFlange | 2 | `IFeatureManager/InsertSheetMetalMiterFlange.md`；`IModelDoc2/InsertSheetMetalMiterFlange.md` |
| InstancesToVary | 2 | `ICircularPatternFeatureData/InstancesToVary.md`；`ILinearPatternFeatureData/InstancesToVary.md` |
| IsCircle | 2 | `ICurve/IsCircle.md`；`ISketchArc/IsCircle.md` |
| LengthUnit | 2 | `IImportDxfDwgData/LengthUnit.md`；`IModelDoc2/LengthUnit.md` |
| LockRotation | 2 | `IConcentricMateFeatureData/LockRotation.md`；`IProfileCenterMateFeatureData/LockRotation.md` |
| Name2 | 2 | `IComponent2/Name2.md`；`IConnectionPointFeatureData/Name2.md` |
| PostTrimSurface | 2 | `IFeatureManager/PostTrimSurface.md`；`IModelDoc2/PostTrimSurface.md` |
| PreTrimSurface | 2 | `IFeatureManager/PreTrimSurface.md`；`IModelDoc2/PreTrimSurface.md` |
| ProfileSize | 2 | `IProfileGroupFolder/ProfileSize.md`；`IStructureSystemMemberProfile/ProfileSize.md` |
| ProfileStandard | 2 | `IProfileGroupFolder/ProfileStandard.md`；`IStructureSystemMemberProfile/ProfileStandard.md` |
| Reference | 2 | `IMateEntity2/Reference.md`；`IRefPlaneFeatureData/Reference.md` |
| ReferenceComponent | 2 | `IMateEntity2/ReferenceComponent.md`；`ISimulationForceFeatureData/ReferenceComponent.md` |
| ReferenceType | 2 | `IMateEntity2/ReferenceType.md`；`IMateReference/ReferenceType.md` |
| ReferencedConfiguration | 2 | `IComponent2/ReferencedConfiguration.md`；`IView/ReferencedConfiguration.md` |
| Rotation | 2 | `IFillPatternFeatureData/Rotation.md`；`IView3D/Rotation.md` |
| Roughness | 2 | `IDSPBRMaterial/Roughness.md`；`IRenderMaterial/Roughness.md` |
| SaveAs3 | 2 | `IModelDoc2/SaveAs3.md`；`IModelDocExtension/SaveAs3.md` |
| SelectByRay | 2 | `IModelDoc2/SelectByRay.md`；`IModelDocExtension/SelectByRay.md` |
| ShapeIntensity | 2 | `IBreakLine/ShapeIntensity.md`；`IDetailCircle/ShapeIntensity.md` |
| SketchOffset2 | 2 | `IModelDoc2/SketchOffset2.md`；`ISketchManager/SketchOffset2.md` |
| SketchTrim | 2 | `IModelDoc2/SketchTrim.md`；`ISketchManager/SketchTrim.md` |
| ThreadClassOverride | 2 | `IStraightTapElementData/ThreadClassOverride.md`；`ITaperedTapElementData/ThreadClassOverride.md` |
| Volume | 2 | `IInterference/Volume.md`；`IMassProperty2/Volume.md` |

### 4.2 命中页里页头写了 `Obsolete.` 的成员（74 个）

> 页面存在 ≠ 可用。这些成员在官方页头被标废弃，**代码里仍在用** —— 只报事实，不判该不该改。

| 成员名 | 出现文件数 | 官方页（接口/文件） |
|---|---|---|
| Add2 | 1 | `ICustomPropertyManager/Add2.md`；`IEquationMgr/Add2.md` |
| AddMate5 | 1 | `IAssemblyDoc/AddMate5.md` |
| AddRelation | 1 | `IModelDoc2/AddRelation.md`；`ISketchRelationManager/AddRelation.md` |
| AdvancedGraphics | 1 | `IMaterialVisualPropertiesData/AdvancedGraphics.md` |
| AutoDimension2 | 1 | `ISketch/AutoDimension2.md` |
| Create3PointArc | 1 | `IModelDoc2/Create3PointArc.md`；`ISketchManager/Create3PointArc.md` |
| CreateArc | 1 | `IModelDoc2/CreateArc.md`；`IModeler/CreateArc.md`；`ISketchManager/CreateArc.md` |
| CreateCenterLine | 1 | `IModelDoc2/CreateCenterLine.md`；`ISketchManager/CreateCenterLine.md` |
| CreateCircleByRadius | 1 | `IModelDoc2/CreateCircleByRadius.md`；`ISketchManager/CreateCircleByRadius.md` |
| CreateCircularSketchStepAndRepeat | 1 | `IModelDoc2/CreateCircularSketchStepAndRepeat.md`；`ISketchManager/CreateCircularSketchStepAndRepeat.md` |
| CreateConicalSurface | 1 | `IModeler/CreateConicalSurface.md` |
| CreateCylindricalSurface | 1 | `IModeler/CreateCylindricalSurface.md` |
| CreateEllipse | 1 | `IModelDoc2/CreateEllipse.md`；`IModeler/CreateEllipse.md`；`ISketchManager/CreateEllipse.md` |
| CreateLine | 1 | `IModelDoc2/CreateLine.md`；`IModeler/CreateLine.md`；`ISketchManager/CreateLine.md` |
| CreateLinearSketchStepAndRepeat | 1 | `IModelDoc2/CreateLinearSketchStepAndRepeat.md`；`ISketchManager/CreateLinearSketchStepAndRepeat.md` |
| CreatePlanarSurface | 1 | `IBody2/CreatePlanarSurface.md`；`IModeler/CreatePlanarSurface.md` |
| CreateSphericalSurface | 1 | `IModeler/CreateSphericalSurface.md` |
| CreateSpline2 | 1 | `ISketchManager/CreateSpline2.md` |
| CreateTangentArc | 1 | `IModelDoc2/CreateTangentArc.md`；`ISketchManager/CreateTangentArc.md` |
| Delete | 1 | `IAttribute/Delete.md`；`IComment/Delete.md`；`ICustomPropertyManager/Delete.md`；`IEquationMgr/Delete.md` |
| DeleteColumn | 1 | `ITableAnnotation/DeleteColumn.md` |
| DeleteRow | 1 | `ITableAnnotation/DeleteRow.md` |
| FeatureBossThicken | 1 | `IFeatureManager/FeatureBossThicken.md`；`IModelDoc2/FeatureBossThicken.md` |
| FeatureLinearPattern5 | 1 | `IFeatureManager/FeatureLinearPattern5.md` |
| GetActiveSketch2 | 1 | `IModelDoc2/GetActiveSketch2.md` |
| GetArcs2 | 1 | `ISketch/GetArcs2.md`；`IView/GetArcs2.md` |
| GetBodies | 1 | `IBodyFolder/GetBodies.md`；`IComponent2/GetBodies.md`；`IPartDoc/GetBodies.md`；`IPartExplodeStep/GetBodies.md` |
| GetBodies2 | 13 | `IComponent2/GetBodies2.md`；`IPartDoc/GetBodies2.md` |
| GetComponents | 3 | `IAssemblyDoc/GetComponents.md`；`IBomTableAnnotation/GetComponents.md`；`ICollision/GetComponents.md`；`ICollisionDetectionGroup/GetComponents.md` |
| GetDependencies | 1 | `IModelDoc2/GetDependencies.md`；`IModelDocExtension/GetDependencies.md` |
| GetEdges | 3 | `IBody2/GetEdges.md`；`IFace2/GetEdges.md`；`ILoop2/GetEdges.md`；`IRuledSurfaceFeatureData/GetEdges.md` |
| GetEllipses3 | 1 | `ISketch/GetEllipses3.md`；`IView/GetEllipses3.md` |
| GetErrorCode | 2 | `IFeature/GetErrorCode.md` |
| GetLines2 | 1 | `ISketch/GetLines2.md`；`IView/GetLines2.md` |
| GetMassProperties | 1 | `IBody2/GetMassProperties.md`；`IModelDoc2/GetMassProperties.md`；`IModelDocExtension/GetMassProperties.md`；`ISldWorks/GetMassProperties.md` |
| GetModelDoc | 1 | `IComponent2/GetModelDoc.md`；`IDerivedPartFeatureData/GetModelDoc.md`；`IMirrorPartFeatureData/GetModelDoc.md` |
| GetNext | 1 | `IAnnotation/GetNext.md`；`ICThread/GetNext.md`；`ICenterLine/GetNext.md`；`ICenterMark/GetNext.md` |
| GetPoints | 1 | `IPrimaryMemberPointLengthFeatureData/GetPoints.md`；`ISketchSpline/GetPoints.md` |
| GetPolylines | 1 | `ISketch/GetPolylines.md`；`IView/GetPolylines.md` |
| GetSelectedObjectType2 | 1 | `ISelectionMgr/GetSelectedObjectType2.md` |
| GetSelectedObjectsComponent3 | 1 | `ISelectionMgr/GetSelectedObjectsComponent3.md` |
| GetSplines | 1 | `ISketch/GetSplines.md`；`ISketchBlockDefinition/GetSplines.md`；`IView/GetSplines.md` |
| GetSuppression | 1 | `IComponent2/GetSuppression.md` |
| GetType | 8 | `IAnnotation/GetType.md`；`IBody2/GetType.md`；`IComponent2/GetType.md`；`ICustomPropertyManager/GetType.md` |
| GetUserPreferenceIntegerValue | 1 | `IModelDoc2/GetUserPreferenceIntegerValue.md`；`ISldWorks/GetUserPreferenceIntegerValue.md` |
| GetUserPreferenceToggle | 1 | `IModelDoc2/GetUserPreferenceToggle.md`；`IModelDocExtension/GetUserPreferenceToggle.md`；`ISldWorks/GetUserPreferenceToggle.md` |
| GraphicsRedraw | 4 | `IModelDoc2/GraphicsRedraw.md`；`IModelView/GraphicsRedraw.md` |
| InsertCoordinateSystem | 1 | `IFeatureManager/InsertCoordinateSystem.md`；`IModelDoc2/InsertCoordinateSystem.md` |
| InsertCutBlend | 1 | `IFeatureManager/InsertCutBlend.md`；`IModelDoc2/InsertCutBlend.md` |
| InsertCutSurface | 1 | `IFeatureManager/InsertCutSurface.md`；`IModelDoc2/InsertCutSurface.md` |
| InsertDeleteFace | 1 | `IModelDoc2/InsertDeleteFace.md`；`IModelDocExtension/InsertDeleteFace.md` |
| InsertProtrusionBlend2 | 1 | `IFeatureManager/InsertProtrusionBlend2.md`；`IModelDoc2/InsertProtrusionBlend2.md` |
| InsertRevolvedRefSurface | 1 | `IFeatureManager/InsertRevolvedRefSurface.md`；`IModelDoc2/InsertRevolvedRefSurface.md` |
| InsertRib | 1 | `IFeatureManager/InsertRib.md`；`IModelDoc2/InsertRib.md` |
| InsertSewRefSurface | 1 | `IFeatureManager/InsertSewRefSurface.md`；`IModelDoc2/InsertSewRefSurface.md` |
| InsertSheetMetalMiterFlange | 1 | `IFeatureManager/InsertSheetMetalMiterFlange.md`；`IModelDoc2/InsertSheetMetalMiterFlange.md` |
| IsSuppressed | 2 | `IComponent2/IsSuppressed.md`；`IDimXpertAnnotation/IsSuppressed.md`；`IDimXpertFeature/IsSuppressed.md`；`IFeature/IsSuppressed.md` |
| KFactor | 1 | `IBaseFlangeFeatureData/KFactor.md`；`IBendsFeatureData/KFactor.md`；`ICustomBendAllowance/KFactor.md`；`IOneBendFeatureData/KFactor.md` |
| ListExternalFileReferencesCount | 1 | `IComponent2/ListExternalFileReferencesCount.md`；`IFeature/ListExternalFileReferencesCount.md`；`IModelDoc2/ListExternalFileReferencesCount.md`；`IModelDocExtension/ListExternalFileReferencesCount.md` |
| MaterialIdName | 1 | `IFace2/MaterialIdName.md`；`IModelDoc2/MaterialIdName.md`；`IPartDoc/MaterialIdName.md` |
| Name | 23 | `IBody2/Name.md`；`IBomFeature/Name.md`；`ICommandGroup/Name.md`；`ICommandTab/Name.md` |
| PostTrimSurface | 1 | `IFeatureManager/PostTrimSurface.md`；`IModelDoc2/PostTrimSurface.md` |
| PreTrimSurface | 1 | `IFeatureManager/PreTrimSurface.md`；`IModelDoc2/PreTrimSurface.md` |
| ReferenceType | 1 | `IMateEntity2/ReferenceType.md`；`IMateReference/ReferenceType.md` |
| ResumeSelectionList | 1 | `ISelectionMgr/ResumeSelectionList.md` |
| SaveAs3 | 1 | `IModelDoc2/SaveAs3.md`；`IModelDocExtension/SaveAs3.md` |
| Scale | 1 | `IFaceHatch/Scale.md`；`IMathPoint/Scale.md`；`IMathVector/Scale.md`；`IModelDoc2/Scale.md` |
| Select2 | 1 | `IAnnotation/Select2.md`；`IBody2/Select2.md`；`IComponent2/Select2.md`；`IConfiguration/Select2.md` |
| SelectByRay | 1 | `IModelDoc2/SelectByRay.md`；`IModelDocExtension/SelectByRay.md` |
| SetSelectionPoint | 1 | `ISelectionMgr/SetSelectionPoint.md` |
| SetUserPreferenceToggle | 1 | `IModelDoc2/SetUserPreferenceToggle.md`；`IModelDocExtension/SetUserPreferenceToggle.md`；`ISldWorks/SetUserPreferenceToggle.md` |
| SketchOffset2 | 1 | `IModelDoc2/SketchOffset2.md`；`ISketchManager/SketchOffset2.md` |
| SketchTrim | 1 | `IModelDoc2/SketchTrim.md`；`ISketchManager/SketchTrim.md` |
| Transform | 1 | `IComponent2/Transform.md`；`ICoordinateSystemFeatureData/Transform.md`；`IModelView/Transform.md`；`IRefPlane/Transform.md` |

### 4.3 命中页含 `in-process, unmanaged C++` 标记的成员（0 个）

> 本仓后端是 pywin32（**进程外**）⇒ 已知事实 47：这一类**到不了**。

| 成员名 | 出现文件数 | 官方页（接口/文件） |
|---|---|---|

## 五、对账不了的地方（如实列出，**不推测**）

### 5.1 第 2 实参不是字符串字面量的调用点（84 个）

> 这些是**转发包装器**（`def get(obj, member, *args): return get_com_member(obj, member, *args)`）
> 或条件表达式。**名字由调用方决定 ⇒ 本表对这一类只能报「判不出来」**，不去猜。
> ⚠ 转发包装器**自己的调用点**已在主表里（AST 回读 `relay` 形态）。

| 文件 | 包装函数 | 第 2 实参写法（原文） |
|---|---|---|
| `sw_api_cosworks.py` | `get_com_member` | `member` |
| `sw_api_dsgnchk.py` | `get_com_member` | `member` |
| `sw_api_fworks.py` | `get_com_member` | `member` |
| `sw_api_gtswutilities.py` | `get_com_member` | `member` |
| `sw_api_sldcostingapi.py` | `get_com_member` | `member` |
| `sw_api_sldtoolboxconfigureaddin.py` | `get_com_member` | `member` |
| `sw_api_sldworks.py` | `get_com_member` | `member` |
| `sw_api_swdimxpert.py` | `get_com_member` | `member` |
| `sw_api_swdocumentmgr.py` | `get_com_member` | `member` |
| `sw_api_swmotionstudy.py` | `get_com_member` | `member` |
| `sw_api_swpublished.py` | `get_com_member` | `member` |
| `sw_api_SWRoutingLib.py` | `get_com_member` | `member` |
| `sw_assembly_doc.py` | `get_com_member` | `member` |
| `sw_assembly_doc.py` | `relay:call_assembly_doc` | `'HideComponent' if hidden else 'ShowComponent'` |
| `sw_connect.py` | `get_com_member` | `attr_name` |
| `sw_costing.py` | `get_com_member` | `member` |
| `sw_delivery.py` | `get_com_member` | `name` |
| `sw_drawing_create_missing.py` | `get_com_member` | `member` |
| `sw_drawing_create_missing.py` | `relay:_read` | `member` |
| `sw_drawing_create_missing.py` | `set_com_member` | `key` |
| `sw_drawing_query.py` | `get_com_member` | `_mem` |
| `sw_drawing_view.py` | `get_com_member` | `member` |
| `sw_drawing_view.py` | `relay:call_view` | `member` |
| `sw_feature_entry_ops.py` | `get_com_member` | `kind` |
| `sw_feature_entry_ops.py` | `get_com_member` | `m` |
| `sw_feature_entry_ops.py` | `get_com_member` | `memo` |
| `sw_feature_readback.py` | `get_com_member` | `name` |
| `sw_featureworks.py` | `get_com_member` | `member` |
| `sw_loft.py` | `get_com_member` | `_m` |
| `sw_mass_property.py` | `get_com_member` | `_nm` |
| `sw_mass_property.py` | `get_com_member` | `name` |
| `sw_mold.py` | `get_com_member` | `name` |
| `sw_part.py` | `get_com_member` | `attr_name` |
| `sw_part.py` | `relay:_safe_com_member` | `name` |
| `sw_part.py` | `get_com_member` | `meth` |
| `sw_pattern.py` | `get_com_member` | `member` |
| `sw_pdm.py` | `get_com_member` | `member` |
| `sw_render_material.py` | `set_com_member` | `str(key)` |
| `sw_routing.py` | `get_com_member` | `member` |
| `sw_selection.py` | `get_com_member` | `member` |
| `sw_selection_spec.py` | `get_com_member` | `member` |
| `sw_selection_spec.py` | `get_com_member` | `_nm` |
| `sw_sensor.py` | `get_com_member` | `meth` |
| `sw_sensor.py` | `get_com_member` | `attr` |
| `sw_sheet_metal_weld_entry.py` | `get_com_member` | `member` |
| `sw_sheet_metal_weld_entry.py` | `get_com_member` | `name` |
| `sw_simulation_loadprops.py` | `get_com_member` | `begin` |
| `sw_simulation_loadprops.py` | `get_com_member` | `end` |
| `sw_simulation_loads.py` | `get_com_member` | `member` |
| `sw_simulation_results.py` | `get_com_member` | `member` |
| `sw_simulation_study.py` | `get_com_member` | `member` |
| `sw_simulation_study_options.py` | `get_com_member` | `accessor` |
| `sw_simulation_study_options.py` | `set_com_member` | `name` |
| `sw_simulation_study_options.py` | `relay:set_option` | `name` |
| `sw_simulation_study_options.py` | `get_com_member` | `name` |
| `sw_sketch.py` | `get_com_member` | `members[0]` |
| `sw_surface.py` | `get_com_member` | `method` |
| `sw_sweep.py` | `get_com_member` | `meth` |
| `sw_topology.py` | `get_com_member` | `getter` |
| `sw_units.py` | `get_com_member` | `getter` |
| `sw_weldment.py` | `get_com_member` | `next_member` |
| `sw_wrap.py` | `get_com_member` | `meth` |

### 5.2 语法解析失败的文件（0 个）

（无 —— 168 个 `.py` 全部 `ast.parse` 成功。）

## 六、本轮发现的判据缺陷（供主线决断，**已按拆开报处理，未擅自改已发布数字**）

1. **指针判据原本是大小写敏感的** —— 官方原文**同时存在大写 `In-process`**
   （`IView.IGetBreakOutSections` 的 `## Returns` 逐字为 `In-process, unmanaged C++: Pointer to an array of
   broken-out section [[features]]`；`IView.IGetVisibleEntities2` 同）。
   ⇒ 按原判据这两页被判「非指针」；**B1 那份 `iview-read-members.md` 把它们算进了主表**
   （其第二节 267 行里含这两个名字，而第四节 45 个里没有）。
   ⇒ 本表与 A 任务的表**已改用大小写不敏感**；**B1 已发布的数字（45 / 267）未动**，请主线决定是否重发。
2. **官方原文笔误 `in-porcess`**（`IDrawingDoc.IGetPenInfo`）—— 字面串匹配会漏。本表已认上。
3. **`(?:pro|por)` 这类可选片段不能简写成 `por?`** —— 本轮我自己先用
   `in-por?cess` 写错过一次，`?` 只作用于紧邻的单个字符，结果**四种接口的指针数全部误报成 0**；
   读数与 B1 不符才发现。⇒ 定则：**改判据之后必须拿一份已发布的结果做回归**（B1 的 45/149/267 就是回归基准）。
