# 官方示例 ↔ 成员页 `Remarks` 的内部冲突

> **这份文件回答**：同一个官方成员，**示例里写的**与**成员页 `Remarks` 里写的**，
> 有没有**不能同时成立**的说法？
>
> **答案**：有，但**少** —— 过闸后 **544 条**（16.0% 的成员）；
> 而**「示例比成员页更具体」**有 **3709 条**。
> ⚠ **但 V3 指出这两个数不同级**：544 是**双侧**过闸、3709 是**单侧**过闸，「多近一个数量级」**口径不对等**。
> ⚠ **V1 还估 `example_more_specific` 有 10–25%（约 400–900 条）需复核**（见 §六）。
>
> **来源与口径**
> - **对象**：`C:\swapi\examples\` 的成员里，**既有官方成员页、又有用到它的示例**的 **3735** 个。
> - **分箱**：每箱 7 个成员，**534 箱**；实际落盘 **486 箱**（**91% 覆盖**）。
> - **分工**：Bunny（`opencode-zen` / `space-bunny-free`），**每 30 箱一个独立 job**（见 §五的作业教训）。
> - **引文闸**：每条冲突两段 `quote` **各自逐字回查**成员页与示例文件 ——
>   **过闸 544 · 未过闸 54**（未过的**已剔除**）。
> - ⚠ **本文件不含行号**。

## 一、统计（**只算过闸的**）

| 指标 | 数 |
|---|---|
| 落盘箱数 | **486 / 534**（91%） |
| 判过的成员 | **3399** |
| 成员页 `## Remarks` 段**为空** | **1474**（43.4%） |
| 机械报出的冲突 | 598 |
| **引文闸通过（= 本文件的数）** | **544**（16.0% 的成员） |
| 引文闸**未过**（已剔除） | **54**（9.0% 的机械报出） |
| **`example_more_specific`（过闸）** | **3709** |

### 1.1 冲突类型（过闸后）

| 类型 | 数 |
|---|---|
| **`precondition_diff`**（调用前必须先做什么，两侧说法不同） | **286** |
| `other_conflict` | 162 |
| **`return_shape_diff`**（返回值形状不同） | **73** |
| `unit_diff`（单位不同） | 14 |
| `mark_diff`（mark 值不同） | 9 |

⇒ ★ **`precondition_diff` 是最大的一类**（占 53%）——
即**「调用前必须先做什么」这件事，示例与成员页经常不一致**。

## 二、★ 过闸的冲突全表（544 条）

| # | 成员 | 类型 | 成员页 `Remarks` 说 | 示例说 | 示例文件 |
|---|---|---|---|---|---|
| 1 | `ActivateDoc3` | other_conflict | If the document needs a rebuild upon activation, and you have specifie | Set swModel = swApp.ActivateDoc3(AssemblyTitle, True, swUserDecision,  | `Add_Component_and_Mate_Example_VB.md` |
\| 2 \| `ActivateSelectedFeature` \| other_conflict \| This method shows the selected feature's dimensions in the graphic are \|     swModel.ClearSelection2 True
    swSketchManager.InsertSketch True | `Create_3D_Sketch_Plane_Example_VB.md` |
| 3 | `ActivateSelectedFeature` | other_conflict | This method shows the selected feature's dimensions in the graphic are |     status = swModelDocExt.SelectByID2("Plane1", "SKETCHSURFACES", 0,  | `Create_3D_Sketch_Plane_Example_VB.md` |
| 4 | `ActiveConfiguration` | other_conflict | 1. IConfigurationManager::ActiveConfiguration (called only once) | swConfiguration = (Configuration)swConfigurationMgr.ActiveConfiguratio | `Are_the_Assembly_Configurations_Loaded_Example_CSharp.md` |
| 5 | `AddCallback` | other_conflict | Not currently used | AddinCallbackData callbackdata = (AddinCallbackData)dsp; | `Create_TaskPaneView_Add-in_Example_CSharp.md` |
| 6 | `AddCallback` | other_conflict | Data related to the event | Debug.Assert(data == addinID); | `Create_TaskPaneView_Add-in_Example_CSharp.md` |
| 7 | `AddCommandTab` | precondition_diff | If another CommandManager tab exists with the same name, then another  | If Not cmdTab Is Nothing And Not getDataResult Or ignorePrevious Then  | `Create_Flyouts_in_the_CommandManager_Example_VBNET.md` |
| 8 | `AddCommands` | other_conflict | **TextDisplayStyles**: Array of the text display styles for the button | TextType[0] = (int)swCommandTabButtonTextDisplay_e.swCommandTabButton_ | `Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp.md` |
| 9 | `AddComponent5` | other_conflict | **IMPORTANT:** X, Y, and Z are relative to the bounding box of the com | Set swcomponent = swAssy.AddComponent5(strCompModelname, swAddComponen | `Add_Component_and_Mate_Example_VB.md` |
| 10 | `AddConfiguration` | other_conflict | The Options argument can be a combination of any of the following valu | swConfig = (Configuration)swConfigMgr.AddConfiguration("nxn", "", "",  | `Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_CSharp.md` |
| 11 | `AddCornerReliefCorner` | precondition_diff | 1. Call [[IModelDocExtension::SelectByID2]] with Mark = 0 and Append = | swModel.ClearSelection2(true); | `Create_Corner_Relief_Feature_Example_CSharp.md` |
| 12 | `AddCornerReliefCorner` | other_conflict | Index of corner to which to apply the corner relief; used by [[IFeatur | myReliefType = swModel.FeatureManager.AddCornerReliefType(-1, (int)swC | `Create_Corner_Relief_Feature_Example_CSharp.md` |
| 13 | `AddDistanceMate` | other_conflict | To specify a distance mate without limits, set the DistanceAbsUpperLim | Set swMate = swAssembly.AddDistanceMate(2, False, 0.2, 0, 0, 1, 1, err | `Add_and_Edit_Distance_Mate_Example_VB.md` |
| 14 | `AddDistanceMate` | precondition_diff | 2. Call [[IModelDoc2::ClearSelection2]]. | swEnt2.Select4 True, Nothing | `Add_and_Edit_Distance_Mate_Example_VB.md` |
| 15 | `AddExplodeStep2` | other_conflict | If AutoSpaceComponentsOnDrag is set to true, then RotateAboutOrigin is | Set explStep = config.AddExplodeStep2(0.5, -1, True, num, -1, True, Fa | `Add_Explode_Step_Example_VB.md` |
| 16 | `AddExplodeStep2` | precondition_diff | 2. Call [[IAssemblyDoc::ShowExploded2]] to activate an explode view. | Call swModel.AutoExplode | `Add_Explode_Step_Example_VB.md` |
\| 17 \| `AddFilletedCorners` \| precondition_diff \| This property is valid only if [[ISMCornerReliefData::ReliefType]] is  \|            cornerItr.AddFilletedCorners = True
           cornerItr.Co | `Create_SM_Corner_Relief_Feature_Example_VBNET.md` |
| 18 | `AddFrame` | precondition_diff | This method is valid only if this Gtol was created in SOLIDWORKS 2022  | // Preconditions:
// 1. Open a drawing that contains a GTol created wi | `Get_Gtol_Frame_Information_Example_CSharp.md` |
| 19 | `AddMenuItem5` | precondition_diff | Text to show in the SOLIDWORKS Design status bar when the user moves t | menuId = iSwApp.AddMenuItem5((int)swDocumentTypes_e.swDocPART, addinID | `Add_Menu_and_Menu_Item_Example_CSharp.md` |
| 20 | `AddMenuItem5` | precondition_diff | Text to show in the SOLIDWORKS Design status bar when the user moves t | menuId = iSwApp.AddMenuItem5(swDocumentTypes_e.swDocPART, addinID, "My | `Add_Menu_and_Menu_Item_Example_VBNET.md` |
| 21 | `AddProfileBspline` | other_conflict | NumCtrlPtCoord = NumCtrlPoints + DimensionControlPoints | double[] cPoints = new double[18]; | `Create_Reference_Curve_Example_CSharp.md` |
| 22 | `AddRow` | other_conflict | Do not use [[IDesignTable::Attach]] or [[IDesignTable::Detach]] with t | swDesignTable.EditTable | `Add_Row_to_Design_Table_Example_VB.md` |
| 23 | `AddSelectionListObjects` | other_conflict | For VB.NET and C# applications, specify Objects as an array of System. | numAdded = selMgr.AddSelectionListObjects((selObjs), selData); | `Add_Objects_to_Selection_List_Example_CSharp.md` |
| 24 | `AddSelectionListObjects` | other_conflict | 4. Call [[ISelectionMgr::ResumeSelectionList]] to reinstate the suspen | selMgr.ResumeSelectionList2(true); | `Add_Objects_to_Selection_List_Example_CSharp.md` |
\| 25 \| `AddToolbar5` \| precondition_diff \| When your add-in is unloaded, you must call [[ISldWorks::RemoveToolbar \|         public bool DisconnectFromSW()
        {
            DetachEve | `Add_Toolbars_Example_CSharp.md` |
| 26 | `AddToolbar5` | precondition_diff | When your add-in is unloaded, you must call [[ISldWorks::RemoveToolbar |     Function DisconnectFromSW() As Boolean Implements SolidWorks.Inter | `Add_Toolbars_Example_VBNET.md` |
\| 27 \| `AddToolbarCommand2` \| return_shape_diff \| If ButtonEnableMethod returns...

**Then SOLIDWORKS Design...**

0

De |     Function ButtonEnableMethod() As Boolean
        ' TODO: Add your  | `Add_Toolbars_Example_VBNET.md` |
| 28 | `AllowFlip` | precondition_diff | This property is valid only if [[IDragArrowManipulator::ShowOppositeDi | swDrag.ShowOppositeDirection = true; | `Create_Drag_Arrow_Manipulator_Example_CSharp.md` |
| 29 | `AllowFlip` | precondition_diff | This property is valid only if [[IDragArrowManipulator::ShowOppositeDi | swDrag.ShowOppositeDirection = True | `Create_Drag_Arrow_Manipulator_Example_VBNET.md` |
| 30 | `AnnotationCount` | precondition_diff | Call this method before calling [[IAnnotationView::IGetAnnotations]] t |                 annotations = (object[])swAnnView.GetAnnotations2(fals | `Get_Where_Annotations_Can_Be_Shown_Example_CSharp.md` |
| 31 | `ApplySavedSortScheme` | precondition_diff | 1. Set [[IBomTableSortData::SaveCurrentSortParameters]] to true to ind | sortSaved = swSortData.SaveCurrentSortParameters; | `Sort_Table_Example_CSharp.md` |
| 32 | `ApplySavedSortScheme` | precondition_diff | 3. [[IBomTableAnnotation::GetBomTableSortData]] to populate SortData. | BomTableSortData swSortData = swSpecTable.GetBomTableSortData(); | `Sort_Table_Example_CSharp.md` |
| 33 | `ApplyTransform` | other_conflict | The origin of the temporary body is relative to the part instead of th | 'Apply transform to move copies to their correct positions in the asse | `Check_Interference_Between_Two_Bodies_Example_VB.md` |
| 34 | `Aspect` | other_conflict | The ViewingAspect argument uses the DVASPECT enumeration, which has th | Debug.Print("  Viewing aspect (1=Content, 2=Thumbnail, 4=Icon, 8=DocPr | `Get_OLE_Object_Data_Example_CSharp.md` |
| 35 | `AutoDimension2` | mark_diff | Select and mark a unique vertical edge, vertex, sketch point, or verti | bRet = swSketchSegVert.Select4(True, Nothing) | `Autodimension_All_Sketches_Example_VB.md` |
| 36 | `BackgroundImage` | precondition_diff | This property is valid only if [[ISwScene::BackgroundType]] is [[swSce |     Scene.BackgroundType = swSceneBackgroundType_e.swBackgroundType_Us | `Get_and_Set_Scene_Properties_Example_VB.md` |
| 37 | `BehindSheet` | precondition_diff | This property places a note on the sheet format behind a drawing sheet | swDrawing.EditSheet2 | `Place_Note_Behind_Drawing_Sheet_Example_VB.md` |
\| 38 \| `BlindDepth` \| precondition_diff \| This property is valid only if [[IAdvancedHoleFeatureData::UseBaseline \|             swAdvHole_Near_3.Diameter = ConvFactorLength * 0.266;
     | `Create_Advanced_Hole_Example_CSharp.md` |
| 39 | `BlindDepth` | precondition_diff | This property is valid only if [[IAdvancedHoleFeatureData::UseBaseline | swAdvHole_Far_2 = (AdvancedHoleElementData)swModel.Extension.CreateAdv | `Create_Advanced_Hole_Example_CSharp.md` |
| 40 | `BreakView` | other_conflict | Use [[IDrawingDoc::InsertBreakHorizontal]] or [[IDrawingDoc::InsertBre | swBreakLine = (BreakLine)swView.InsertBreak(0, -0.0291950859897372, 0. | `Create_Broken_View_Example_CSharp.md` |
| 41 | `CalloutString` | precondition_diff | This property is valid only if [[IAdvancedHoleFeatureData::CustomizeCa | Set feat = swFeatureMgr.AdvancedHole2((advHoleNearArr), (advHoleFarArr | `Create_Advanced_Hole_Example_VB.md` |
\| 42 \| `Capture3DView` \| precondition_diff \| This method requires that the SOLDWORKS MBD add-in be loaded. ([[ISldW \| ' 1. Open a part or assembly.
' 2. Open an Immediate window. | `Capture_3DView_Example_VB.md` |
| 43 | `CenterOnBendLines` | precondition_diff | - [[ISMCornerReliefData::ReliefType]] is set to [[swCornerReliefType_e |                cornerItr.CenterOnBendLines = true;

               cor | `Create_SM_Corner_Relief_Feature_Example_CSharp.md` |
| 44 | `CheckInterference` | other_conflict | To align the two bodies, apply the transformation from [[IComponent2:: | Set swTransform1 = swComponent1.Transform | `Check_Interference_using_Modeler_CheckInterference_Example_VB.md` |
| 45 | `CheckInterferenceBetweenTwoBodies` | other_conflict | Use [[IComponent2::Transform2]] to get the transform of each component | Set swTransform1 = swComponent1.Transform | `Check_Interference_Between_Two_Bodies_Example_VB.md` |
| 46 | `CheckInterferenceBetweenTwoBodies` | other_conflict | 5. Specify Body1 and Body1 with the bodies that have been transformed  | bValue = swModeler.CheckInterferenceBetweenTwoBodies(swBodyCopy1, swBo | `Check_Interference_Between_Two_Bodies_Example_VB.md` |
| 47 | `CircularProfileDiameter` | precondition_diff | This property is valid only if [[ISweepFeatureData::CircularProfile]]  | swSweep.CircularProfileDiameter = 0# | `Insert_Bidirectional_Swept-cut_Feature_Example_VB.md` |
| 48 | `ConeParams` | unit_diff | The half angle, origin, and radius parameters are in meters. | " & vCone(7) * 57.3 & " deg" | `Locate_Apex_of_Conical_Face_Example_VB.md` |
| 49 | `ContourLineColor` | precondition_diff | This property is only available when [[IRayTraceRendererOptions::Conto | Debug.Print("  Contour line color = " + swRayTraceRenderOptions.Contou | `Render_Model_Example_CSharp.md` |
| 50 | `ContourLineThickness` | precondition_diff | This property is only available when [[IRayTraceRendererOptions::Conto | Debug.Print("  Contour line thickness = " + swRayTraceRenderOptions.Co | `Render_Model_Example_CSharp.md` |
| 51 | `CopyDocument` | precondition_diff | There can be no documents open when using this method. | Preconditions: Open an assembly document. | `Copy_Document_and_Its_Dependencies_Example_VB.md` |
\| 52 \| `CornerFilletDiameter` \| precondition_diff \| This property is valid only if:

- [[ISMCornerReliefData::AddFilletedC | cornerItr.ReliefType = (int)swCornerReliefType_e.swCornerCircularRelie | `Create_SM_Corner_Relief_Feature_Example_CSharp.md` |
| 53 | `CounterDrillAngle` | precondition_diff | This property is relevant only for swCounterDrilled and swCounterDrill | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 54 | `CounterDrillDepth` | precondition_diff | This property is relevant only for swCounterDrilled and swCounterDrill | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 55 | `CounterDrillDiameter` | precondition_diff | This property is relevant only for swCounterDrilled and swCounterDrill | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 56 | `CounterSinkAngle` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 57 | `CounterSinkDiameter` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 58 | `CreateBodyFromBox` | return_shape_diff | [[Body]] | swBoxBody = (Body2)swModeler.CreateBodyFromBox((vBoxArr)); | `Create_Solid_Bodies_using_Geometry_and_Topology_APIs_Example_CSharp.md` |
| 59 | `CreateByExplode` | precondition_diff | ' Precondition: Active document contains an exploded view of an assemb | ' MotionStudy 1 and a collapsed exploded view. | `sldworksapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md` |
| 60 | `CreateByRotateModel` | other_conflict | ' set the animation duration to 5 seconds, and play | 'Set the animation duration to 10 seconds | `sldworksapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md` |
| 61 | `CreateCircle2` | other_conflict | This method creates a partial arc in the active 2D sketch. | A named view is activated and a circle centered about the view's origi | `Create_Detail_View_Example_VB.md` |
| 62 | `CreateCommandGroup2` | other_conflict | Set IgnorePreviousVersion to true to prevent SOLIDWORKS from saving th | if (!CompareIDs((int[])registryIDs, knownIDs)) // If the IDs don't mat | `Create_Flyouts_in_the_CommandManager_Example_CSharp.md` |
| 63 | `CreateExtrudedBody` | precondition_diff | 3. Call [[ISurface::CreateTrimmedSheet4]] or [[ISurface::ICreateTrimme |     Set profileBody = planeSurf.CreateTrimmedSheet((trimCurves)) | `Create_Temporary_Extruded_Body_Example_VB.md` |
| 64 | `CreateFeatureMgrControl2` | other_conflict | To add a tab to a FeatureManager design tree that has been split, spec | swFeatMgrTabTop = swModViewMgr.CreateFeatureMgrControl2(iconSmall, "ac | `Add_ActiveX_Tabs_to_FeatureManager_Design_Tree_Example_VBNET.md` |
\| 65 \| `CreateFeatureMgrControl4` \| other_conflict \| Add a tab to the FeatureManager design tree, specify WhichPane with sw \| ' NOTE: To add a tab to the FeatureManager tree,
' you must set IModel | `Add_ActiveX_Tab_to_FeatureManager_Design_Tree_Example_VBNET.md` |
| 66 | `CreateFeatureMgrWindowFromHandlex64` | precondition_diff | Fully qualified path to the bitmap file that you want to use for the c | public_documents\\samples\\tutorial\\api\\addin\\pm_extruded_block.bmp | `Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp.md` |
| 67 | `CreateInstance5` | other_conflict | If you add an attribute to an entity, SOLIDWORKS strips the attribute  | swAttribute = swAttributeDef.CreateInstance5(swModel, swFace, "TestAtt | `Add_Attribute_to_Feature_and_Include_in_Library_Feature_Example_CSharp.md` |
| 68 | `CreateMassProperty2` | precondition_diff | A mass properties object with information about one or more components | MyMassProp = (MassProperty2)Extn.CreateMassProperty2(); | `Get_Mass_Properties_Using_IMassProperty_Example_CSharp.md` |
| 69 | `CreateMate` | precondition_diff | [[IMateFeatureData]] is the base interface for the following mate-spec |             boolstatus = swModel.Extension.SelectByRay(0.0086885795659 | `Create_Limit_Angle_Mate_Example_CSharp.md` |
| 70 | `CreatePCurve` | other_conflict | numKnots = NumCtrlPoints + Order |     Dim nKnot(9) As Double | `Create_Space_Parameter_Curve_on_Surface_Example_VB.md` |
\| 71 \| `CreatePlotFeatureData` \| precondition_diff \| Set the entities for the x-axis and y-axis feature data objects. \|             swSimPlotYAxisFeatureData[0].Entities = swEntityArray;
    | `sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md` |
| 72 | `CreatePlotXAxisFeatureData` | precondition_diff | Set the entities for the x-axis and y-axis feature data objects. |             swSimPlotYAxisFeatureData[0].Entities = swEntityArray;
    | `sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md` |
| 73 | `CreatePlotYAxisFeatureData` | precondition_diff | Set the entities for the x-axis and y-axis feature data objects. |             swSimPlotYAxisFeatureData[0].Entities = swEntityArray;
    | `sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md` |
| 74 | `CreatePoint2` | precondition_diff | This method creates a point in the active 2D or 3D sketch. If a sketch |     Set pSketchPoint1 = pDrawing.CreatePoint2(0.1, 0.14, 0) | `Create_Sketch_Line_with_Visual_Properties_Example_VB.md` |
| 75 | `CreatePropertyManagerPage` | other_conflict | Specify swPropertyManagerPageOptions_e.swPropertyManagerOptions_Locked | Dim options As Integer = swPropertyManagerPageOptions_e.swPropertyMana | `Add_.NET_Controls_to_SolidWorks_Using_an_Add-in_Example_VBNET.md` |
\| 76 \| `CreateSectionViewAt5` \| precondition_diff \| Before calling this method, select the section line or lines to use as \|     swModel.ClearSelection2 True
    ' Create section-view line
    Se | `Create_Section_View_and_Get_Some_Data_Example_VB.md` |
| 77 | `CreateSeedCutPolygonSides` | precondition_diff | This property is valid only if both are true:

- [[IFillPatternFeature | 		            swFeatData.CreateSeedCutPolygonSides = 0;
		             | `Create_Fill_Pattern_Example_CSharp.md` |
| 78 | `CreateSpline` | precondition_diff | This method creates a spline in the active 2D sketch. | This example shows how to create a 3D spline. | `Create_3D_Spline_Example_VB.md` |
| 79 | `CreateSpline2` | precondition_diff | This method creates a spline in the active 2D sketch. | Part.SketchManager.Insert3DSketch True | `Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md` |
| 80 | `CreateTaskpaneView3` | precondition_diff | ImageList contains paths to PNG or BMP images in six pixel sizes: | string[] bitmap = new string[1]; | `Create_TaskPaneView_Add-in_Example_CSharp.md` |
\| 81 \| `CreateTransform` \| other_conflict \| The SOLIDWORKS transformation matrix is stored as a homogeneous matrix \| ' Create unit transform
    Set swXform = swMathUtil.CreateTransform(N | `Align_Assembly_Component_to_Assembly_Origin_and_Planes_Example_VB.md` |
| 82 | `CreateTrimmedSurface` | precondition_diff | Before you call this method, you must call one of the base-surface cre | swSurface.AddTrimmingLoop(nCurves,
Order, Dim, Periodic, nKnots, nCtrl | `Create_Imported_Surface_Body_from_Sketch_Example_CSharp.md` |
| 83 | `Curvature` | precondition_diff | Curvature control must be enabled for this property to have an effect. |         Debug.Print " Curvature: " & swSplineHandle(i).Curvature | `Get_and_Set_Spline_Handles_Example_VB.md` |
| 84 | `D1Direction` | precondition_diff | Use this property only when editing the pattern feature. | patternDirection = swCurveDrivenPatternFeatureData.D1Direction; | `Create_and_Access_Curve-driven_Pattern_Feature_Example_CSharp.md` |
| 85 | `DeSelect2` | other_conflict | If running SOLIDWORKS x64, then you must declare AtIndex as a Long in  | Dim atIndex(1) As Integer | `Apply_and_Remove_Texture_By_Configuration_Example_VBNET.md` |
| 86 | `DefineAttribute` | precondition_diff | The Name argument used for this attribute definition must be unique an | swAttributeDef = (AttributeDef)swApp.DefineAttribute("TestPropagationO | `Add_Attribute_to_Feature_and_Include_in_Library_Feature_Example_CSharp.md` |
\| 87 \| `DeleteBlends3` \| other_conflict \| Typically when deleting blends, an entire chain of blends is deleted. \| // 1. Creates a new part, which has the same body as
//    the origina | `Delete_Blended_Faces_Example_CSharp.md` |
| 88 | `DeleteDecal` | other_conflict | However, if you set BReassignIdsAndInvalidate to true, then decal ID 2 | // 1. Deletes all of the decals. | `Delete_Decal_Example_CSharp.md` |
| 89 | `DeleteFaces3` | other_conflict | Call [[IBody2::Check3]] to verify that the body is a valid solid after | nRetval = swCopyBody.Check2 | `Delete_Faces_Example_VB.md` |
| 90 | `DeleteFrame` | precondition_diff | This method is valid only if this Gtol was created in SOLIDWORKS 2022  | either SolidWorks 2021 or SolidWorks 2022/2022+. | `Get_Gtol_Frame_Information_Example_CSharp.md` |
\| 91 \| `DeleteOriginalFace` \| precondition_diff \| This property is only available if [[ISurfExtrudeFeatureData::BothDire \| ' Create a blind surface extrude
    ' in two directions from the sele | `Insert_Extruded_Reference_Surface_Example_VB.md` |
| 92 | `Diagonal` | precondition_diff | This property is valid only if both are true:

- [[IFillPatternFeature | swFeatData.CreateSeedCutType = 0;
swFeatData.Diagonal = 0.008; | `Create_Fill_Pattern_Example_CSharp.md` |
| 93 | `Diagonal` | precondition_diff | - [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToP | swFeatData.FeaturesToPatternType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 94 | `Diameter` | precondition_diff | This property is valid only if [[IAdvancedHoleElementData::DiameterOve | swAdvHole_Near_1.Diameter = ConvFactorLength * 0.225; | `Create_Advanced_Hole_Example_CSharp.md` |
\| 95 \| `Diameter` \| precondition_diff \| This property is valid only if [[IAdvancedHoleElementData::DiameterOve \| swAdvHole_Near_2.Diameter = ConvFactorLength * 0.089;
swAdvHole_Near_2 | `Create_Advanced_Hole_Example_CSharp.md` |
| 96 | `Diameter` | precondition_diff | This property is valid only if [[IAdvancedHoleElementData::DiameterOve | Debug.Print("   Diameter in m: " + ((AdvancedHoleElementData)swCounter | `Create_Advanced_Hole_Example_CSharp.md` |
| 97 | `Dimension` | precondition_diff | - [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToP | swFeatData.FeaturesToPatternType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 98 | `Dimension` | precondition_diff | - [[IFillPatternFeatureData::CreateSeedCutType]] is set to one of the  | swFeatData.CreateSeedCutType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 99 | `DisplayAsOneItem` | precondition_diff | This property applies to top-level only BOM tables. Use [[IBomFeature: | BomType = swBomType_Indented | `Insert_and_Show_BOM_Table_and_BOM_Balloon_Example_VB.md` |
| 100 | `DisplayControlPolygon` | precondition_diff | To add a control polygon, set [[ISldWorks::SetUserPreferenceToggle]] s | swSpline.DisplayControlPolygon = True | `Get_and_Set_Spline_Properties_Example_VB.md` |
| 101 | `DistanceFromEnd` | precondition_diff | This property is valid only if [[IWidthMateFeatureData::ConstraintType |                 swWidthMateData.ConstraintType = (int)swMateWidthOptio | `Create_Width_Mate_Example_CSharp.md` |
| 102 | `DistanceFromEnd` | precondition_diff | This property is valid only if [[IWidthMateFeatureData::ConstraintType |         swWidthMateData.ConstraintType = SwConst.swMateWidthOptions_e. | `Create_Width_Mate_Example_VB.md` |
| 103 | `DivergeFromAxis` | precondition_diff | If you want to set this property to true, then you must first set IExp | explStep.DivergeFromAxis = Not explStep.DivergeFromAxis | `Edit_Radial_Explode_Step_Example_VB.md` |
\| 104 \| `DraftSideFaces` \| precondition_diff \| After setting this property to true, set [[ISMGussetFeatureData::Draft \| swFeatData.DraftAngle = 3 * 0.0175;
swFeatData.DraftSideFaces = true; | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 105 | `DynamicFrictionCoefficient` | precondition_diff | Available only when [[ISimulation3DContactFeatureData::FrictionOption] |             If swContFeat.FrictionOption = swMotionContactFrictionType | `Create_3D_Contact_Feature_Example_VBNET.md` |
| 106 | `DynamicFrictionVelocity` | precondition_diff | Available only when [[ISimulation3DContactFeatureData::FrictionOption] |             If swContFeat.FrictionOption = swMotionContactFrictionType | `Create_3D_Contact_Feature_Example_VBNET.md` |
\| 107 \| `EdgeChamferAngle` \| precondition_diff \| This method is relevant only for an angle-distance type of chamfer. \| 	            swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1);
	   | `Get_Chamfer_Distances_Example_CSharp.md` |
| 108 | `EdgeFilletRadius` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::FilletGussetEdg | swFeatData.FilletGussetEdges = false; | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 109 | `EdgeFilletRadius` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::FilletGussetEdg | swFeatData.GussetType = (int)swSheetMetalRibGussetType_e.swSheetMetalR | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 110 | `Edit` | other_conflict | This method applies the parameters to the actual features. After calli | swModel.EditRebuild3(); | `Edit_Mate_Reference_Example_CSharp.md` |
| 111 | `EditAssembly` | precondition_diff | This method is used with [[IAssemblyDoc::EditPart2]], which allows you | swTopLevelAssembly.EditAssembly() | `Create_Auto_Route_Example_VBNET.md` |
| 112 | `EditDelete` | precondition_diff | Use [[IModelDocExtension::DeleteSelection2]] to turn off prompting the | swModel.EditDelete(); | `Copy_Components_With_Mates_To_Assembly_Example_CSharp.md` |
\| 113 \| `EditMate3` \| mark_diff \| The two mated items must be selected with a selection mark of 1. \|         '   IAssemblyDoc::EditMate3 requires that mate entities
       | `Edit_Mate_Example_VB.md` |
| 114 | `EditTable2` | precondition_diff | If the return value of this method is assigned to a variable, then it  | swDesignTable.UpdateTable swDesignTableUpdateOptions_e.swUpdateDesignT | `Disable_Cell_Drop-down_Lists_in_Design_Table_Example_VB.md` |
| 115 | `EditTable2` | other_conflict | To avoid problems with zooming, set bNewWindow to True. | Set myWorksheet = swDesignTable.EditTable2(False) | `Disable_Cell_Drop-down_Lists_in_Design_Table_Example_VB.md` |
| 116 | `EditTemplate` | other_conflict | You can use this method with [[IDrawingDoc::EditSheet]] or [[IDrawingD | swModel.EditSketch(); | `Create_Drawing_Sheet_Zones_Example_CSharp.md` |
| 117 | `EndCondition` | precondition_diff | This property can be set for a given hole element only when its corres | swAdvHole_Near_1.EndCondition = (int)swEndConditions_e.swEndCondBlind; | `Create_Advanced_Hole_Example_CSharp.md` |
| 118 | `EndConditionOffsetDistance` | precondition_diff | [[IThreadFeatureData::EndConditionOffset]] is set to true. | Debug.Print "End condition offset distance: " & swThreadFeatData.EndCo | `Create_a_Thread_Feature_Example_VB.md` |
| 119 | `EndConditionOffsetReverse` | precondition_diff | [[IThreadFeatureData::EndConditionOffset]] is set to true. | Debug.Print "Reverse end condition offset? " & swThreadFeatData.EndCon | `Create_a_Thread_Feature_Example_VB.md` |
| 120 | `EndVariablePitchHelix` | other_conflict | 2. [[IFeatureManager::AddVariablePitchHelixFirstPitchAndDiamenter]] to | status = swFeatureManager.AddVariablePitchHelixFirstPitchAndDiameter(0 | `Create_Variable_Pitch_Helix_Example_VBNET.md` |
| 121 | `EntityParams` | return_shape_diff | To define the mate entity, the following information is returned based | Debug.Assert 7 = UBound(vEntParam) | `Get_Mate_Definition_Example_VB.md` |
\| 122 \| `EnumDocuments2` \| return_shape_diff \| The list of [[IModelDoc2]] objects contained in the [[IEnumDocuments2] \| LPENUMDOCUMENTS pDocEnum
= NULL;
hres = TheApplication->m_pSldWorks->E | `Traverse_All_Open_Documents_Example_CPlusPlus_COM.md` |
| 123 | `EqualSpacing2` | precondition_diff | This property is only available when:

- [[ICircularPatternFeatureData |             if (swCircularPatternFeatureData.Direction2 == true)
      | `Create_Bidirectional_Circular_Pattern_Feature_Example_CSharp.md` |
| 124 | `ExitApp` | precondition_diff | This method is not normally used with macros (*.swp) because it shuts  | Sub Macro1()
Dim
swApp As Object
Set
swApp = CreateObject("SldWorks.Ap | `SOLIDWORKS_Visible_or_BackGround_Example_VB.md` |
| 125 | `ExportToDWG2` | precondition_diff | You must select multi-body sheet-metal features (i.e., multiple flat-p | 1. Creates three DWG files containing: | `Export_Part_To_DWG_Example_VB.md` |
| 126 | `ExtensionLineUseDocumentDisplay` | precondition_diff | This property is valid only if [[IDisplayDimension::ExtensionLineSameA | Debug.Print("Extension line uses document settings? " + dispdim.Extens | `Set_Properties_of_Angular_Running_Dimension_Example_CSharp.md` |
| 127 | `ExternalState` | return_shape_diff | The return value for each event is a double that specifies the new for | return 1; | `sldworksapi__Fire_Events_for_External_Output_Time_Step_Changes_Example_CSharp.md` |
| 128 | `ExternalState` | other_conflict | IMotionStudy ForceTimeStepChangeNotify and ForceOutputTimeStampChangeN | motionstudy.ForceOutputTimeStepChangeNotify += this.motionStudy_ForceO | `sldworksapi__Fire_Events_for_External_Output_Time_Step_Changes_Example_CSharp.md` |
| 129 | `FaceInSurfaceSense` | other_conflict | You might need this method because the underlying surface geometry can | ' cannot be in the same direction as the normal | `Get_Normal_of_Planar_Surface_Example_VB.md` |
| 130 | `FarCounterSinkAngle` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | (int)swWzdGeneralHoleTypes_e.swWzdCounterBore | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 131 | `FarCounterSinkDiameter` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | (int)swWzdGeneralHoleTypes_e.swWzdCounterBore | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 132 | `FeatureByPositionReverse` | other_conflict | However, IModelDoc2::GetFeatureCount does not recognize Sheet-Metal an | for (i = 0; i <= swModel.GetFeatureCount() - 1; i++) | `Get_Features_in_Reverse_Order_Example_CSharp.md` |
| 133 | `FeatureCircularPattern4` | unit_diff | Spacing between each instance of the circular pattern; total angle in  | myModel.FeatureManager.FeatureCircularPattern4 3, 1.25663706143592, Tr | `Get_Cosmetic_Threads_in_a_Part_Document_Example_VB.md` |
| 134 | `FeatureExtruRefSurface2` | mark_diff | Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0 | boolstatus = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, f | `Create_Surface_Knit_Feature_Example_CSharp.md` |
| 135 | `FeatureExtruRefSurface2` | mark_diff | Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0 | status = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false | `Create_Temporary_Bodies_by_Offsetting_Surface_Body_Example_CSharp.md` |
| 136 | `FeatureFilters` | precondition_diff | This API is in force only when [[IDimXpertAutoDimSchemeOption::ScopeAl | retval = swDXPart.AutoDimensionScheme(schemeOption) | `Auto_Dimension_Scheme_Example_VB.md` |
| 137 | `FeatureLinearPattern4` | unit_diff | - **Offset1**: Offset in meters from a selected reference in Direction | * 0.l9 (Offset1; furthest instance in Direction 1 is offset by 190 mm | `Create_Linear_Pattern_Example_VB.md` |
| 138 | `FeatureLinearPattern4` | mark_diff | - 8388608 to mark a seed instance reference when FromCentroid1 or From | status = swModelDocExt.SelectByID2("Boss-Extrude2", "SOLIDBODY", 0, 0, | `Change_Linear_Pattern_Example_VB.md` |
| 139 | `FeatureRevolve2` | precondition_diff | - the sketch to revolve, using Mark = 0. | status = swModelDocExt.SelectByID2("Line2", "SKETCHSEGMENT", -0.026416 | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp.md` |
| 140 | `FeatureSelectorOptions` | other_conflict | Array of long values as defined in [[swDimXpertFeatureSelectorOption_e | int[] dimarray = new int[1]; | `Get_and_Set_Datum_Example_CSharp.md` |
| 141 | `FeaturesToPatternType` | other_conflict | [[IFillPatternFeatureData::CreateSeedCutType]] to get or set the type  | swFeatData.CreateSeedCutType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 142 | `FieldOfViewAngle` | unit_diff | Camera's horizontal angle of the field of view in radians | swCamera.FieldOfViewAngle * 1000.0 + " mm" | `Insert_Camera_Example_CSharp.md` |
| 143 | `FieldOfViewAngle` | unit_diff | Camera's horizontal angle of the field of view in radians | swCamera.FieldOfViewAngle * 1000# & " mm" | `Insert_Camera_Example_VB.md` |
| 144 | `FieldOfViewAngle` | unit_diff | Camera's horizontal angle of the field of view in radians | swCamera.FieldOfViewAngle * 1000.0# & " mm" | `Insert_Camera_Example_VBNET.md` |
| 145 | `FilletGussetEdges` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::GussetType]] is | swFeatData.GussetType = (int)swSheetMetalRibGussetType_e.swSheetMetalR | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 146 | `FilletInnerCorners` | precondition_diff | After setting this property, set [[ISMGussetFeatureData::InnerCornerFi | swFeatData.FilletInnerCorners = false; //no inner corner fillet | `Insert_Sheet_Metal_Gusset_Feature_Example_CSharp.md` |
| 147 | `FilletOuterCorners` | precondition_diff | After setting this property, set [[ISMGussetFeatureData::OuterCornerFi | swFeatData.FilletOuterCorners = false; //no outer corner fillet | `Insert_Sheet_Metal_Gusset_Feature_Example_CSharp.md` |
| 148 | `FirstColor` | other_conflict | Use [[ISectionViewData::ShowSectionCap]] to display the caps of sectio | data.KeepCapColor = True | `Create_Section_View_in_Model_Example_VB.md` |
| 149 | `FirstPlane` | return_shape_diff | [[Plane]] or [[planar face]] | p1 = (Feature)data.FirstPlane; | `Get_Section_View_Data_Example_CSharp.md` |
| 150 | `FitToSWWindow` | precondition_diff | This property is valid only if [[ISwScene::BackgroundType]] is [[swSce | Scene.BackgroundType = (int)swSceneBackgroundType_e.swBackgroundType_U | `Get_and_Set_Scene_Properties_Example_CSharp.md` |
\| 151 \| `FixedReference` \| return_shape_diff \| Fixed reference entity (edge or face) \|     Set swFixedFace = swSheetMetal.FixedReference
    If Not swFixedFa | `Get_Template_Sheet_Metal_Feature_Data_Example_VB.md` |
| 152 | `FlattenAlongPath` | precondition_diff | This property is valid only when not creating the swept flange on an e | myFeature = Part.FeatureManager.InsertSheetMetalBaseFlange2(0.0007366, | `Create_Swept_Flange_Example_CSharp.md` |
\| 153 \| `FlipFaceTangentTo` \| other_conflict \| Index of the loop to use to create the patch \|     params = swFeatData.Edges

    For i = 0 To UBound(params)

       | `Get_Shut-Off_Surface_Data_Example_VB.md` |
| 154 | `FloorReflections` | precondition_diff | This property is valid only if [[ISwScene::FloorShadows]] is set to tr | Scene.FloorReflections = true; | `Get_and_Set_Scene_Properties_Example_CSharp.md` |
| 155 | `FloorRotation` | precondition_diff | This property is valid only if [[ISwScene::FloorAutoSize]] is false. | Debug.Print("Scene floor rotation: " + Scene.FloorRotation); | `Get_and_Set_Scene_Properties_Example_CSharp.md` |
\| 156 \| `FromScale` \| precondition_diff \| This property is valid only if [[IPrintSpecification::ScaleMethod]] is \|     printSpec.FromScale = 1.5
    printSpec.ToScale = 0.5
    printSpe | `Print_Drawing_as_High_Quality_Example_VB.md` |
| 157 | `GeneralTopology` | other_conflict | If you set this property to True, then set it back to false as soon as | swModeler.GeneralTopology = true; | `Create_and_Convert_Non-manifold_Bodies_Example_CSharp.md` |
\| 158 \| `Get3DViewCount` \| precondition_diff \| This method requires that the SOLDWORKS MBD add-in be loaded. ([[ISldW \| ' Preconditions:
' 1. Open a part or assembly.
' 2. Open an Immediate  | `Capture_3DView_Example_VB.md` |
| 159 | `Get3DViewNames` | precondition_diff | This method requires that the SOLDWORKS MBD add-in be loaded. ([[ISldW | ' Preconditions:
' 1. Open a part or assembly.
' 2. Open an Immediate  | `Capture_3DView_Example_VB.md` |
| 160 | `GetAttachedEntities2` | return_shape_diff | COM applications can use QueryInterface to obtain the specific object  | swEntity = (Entity)attachedEntityArray[i]; | `Get_BOM_Balloon_Properties_Example_CSharp.md` |
| 161 | `GetAttachedEntities3` | return_shape_diff | COM applications can use QueryInterface to obtain the specific object  | swEntity = (Entity)vAttEntArr[i]; | `Attach_Annotation_to_Entity_Example_CSharp.md` |
| 162 | `GetAttachedEntities3` | other_conflict | To determine the corresponding object type in the IAnnotation::GetAtta | vAttEntTypeArr = (int[])swAnn.GetAttachedEntityTypes2(); | `Get_Types_of_Entities_for_Selected_Dimension_Example_CSharp.md` |
\| 163 \| `GetBendState` \| precondition_diff \| A part with bend information is being edited in context of the assembl \|     nBendState = swModel.GetBendState
    Debug.Print "File = " & swMo | `Flatten_Sheet_Metal_Part_Example_VB.md` |
| 164 | `GetCavitySurfacesCount` | precondition_diff | Call this method before calling [[IToolingSplitFeatureData::IGetCavity |     cavSurf = swToolingSplitFeatData.CavitySurfaces
    For i = 0 To s | `Get_Tooling_Split_Feature_Data_Example_VB.md` |
| 165 | `GetCentermarks` | return_shape_diff | This method returns an empty array for center marks that are annotatio | Debug.Assert
Not IsEmpty(vCenterMarkArr) | `List_Center_Marks_in_Drawing_Example_VB.md` |
| 166 | `GetCoEdges` | precondition_diff | Call this method for body-related edges, not reference curve or sketch | 1. Open a part, assembly, or drawing document. | `Select_Tangent_Edges_Example_VB.md` |
| 167 | `GetCollisions` | precondition_diff | Use [[ICollisionDetectionManager::IsCollisionPresent]] to determine wh | numCollisions = cdm.GetCollisions(true, out var1); | `Manage_Collision_Detection_Example_CSharp.md` |
| 168 | `GetCommandIDsCount` | precondition_diff | Call this method before calling [[ICommandManager::IGetGroupDataFromRe | Dim getDataResult As Boolean = iCmdMgr.GetGroupDataFromRegistry(mainCm | `Create_Flyouts_in_the_CommandManager_Example_VBNET.md` |
| 169 | `GetCommandTabs` | other_conflict | To activate and query the add-in CommandManager tabs, call [[ICommandM | swModelDocExt.ActiveCommandTab = "Sketch"; | `Activate_SOLIDWORKS_CommandManager_Tab_Example_CSharp.md` |
\| 170 \| `GetConfigurationParamsCount` \| return_shape_diff \| Number of parameters in this configuration \| hr
= pCfgMgr->GetConfigurationParamsCount(sCfgName,
&NumParams); | `Get_Configuration_Parameters_Example_CPlusPlus_COM.md` |
| 171 | `GetConfigurationParamsCount` | other_conflict | System.int GetConfigurationParamsCount( System.string ConfigName ) | hr
= pCfgMgr->GetConfigurationParamsCount(sCfgName,
&NumParams); | `Get_Configuration_Parameters_Example_CPlusPlus_COM.md` |
| 172 | `GetContoursCount` | other_conflict | This method returns the total number of sketch contours and sketch reg |             Debug.Print("Number of sketch contours in this extrude fea | `Create_Extrude_Feature_Using_Sketch_Contours_Example_CSharp.md` |
| 173 | `GetCustomBendAllowance` | precondition_diff | This method is valid only if [[IBaseFlangeFeatureData::UseDefaultBendA | cba = (CustomBendAllowance)swBaseFlangeFeat.GetCustomBendAllowance(); | `Create_Base_Flange_Feature_Example_CSharp.md` |
\| 174 \| `GetDependencies2` \| return_shape_diff \| If AddReadOnlyInfo is set to True, then a string of True or false is a \| vDepend
= swModel.GetDependencies2(True,
True, True)
Debug.Print
swMod | `Get_Active_Document_Dependents_Example_VB.md` |
| 175 | `GetDetailCircleCount2` | return_shape_diff | Call this method before calling [[IView::GetDetailCircles]] to get the | vDetCirc
= swView.GetDetailCircleInfo2
nNumDetCirc
= swView.GetDetailC | `Get_Detail_Circle_Information_Example_VB.md` |
| 176 | `GetDisplayState` | return_shape_diff | True if the setting specified is turned on, false if not | "  Sectioned = " & swModView.GetDisplayState(swIsViewSectioned) | `Get_Display_State_Example_VB.md` |
\| 177 \| `GetDisplayStateSetting` \| other_conflict \| 1. Call [[IDisplayStateSetting::Names]] or [[IDisplayStateSetting::ISe \| swDisplayStateSetting.Entities = swComponents;
swDisplayStateSetting.O | `Change_Color_of_Component_in_Specific_Display_State_Example_CSharp.md` |
| 178 | `GetDisplayStatesCount` | precondition_diff | Call this method before calling [[IConfiguration::IGetDisplayStates]]  | displayStateNames = swConfig.GetDisplayStates
nbrDisplayStates = swCon | `Add_and_Delete_Materials_from_Specific_Display_States_Example_VB.md` |
| 179 | `GetDistance` | return_shape_diff | 0 if success; -1 if failure | Debug.Print("IEquity::GetDistance return value (0 = success; 1 = failu | `Get_Distance_Between_Entities_Example_CSharp.md` |
| 180 | `GetDocumentNamesCount` | other_conflict | Call this method before calling [[IPackAndGo::IGetDocumentNames]] and  | object[] pgFileNames = new object[namesCount - 1]; | `Pack_and_Go_an_Assembly_Example_CSharp.md` |
| 181 | `GetDraftAngle` | precondition_diff | Call [[IBoundaryBossFeatureData::GetCurvesCount]] to get a valid range | if (nbrCurves >= 0) | `Insert_Boundary_Feature_Example_CSharp.md` |
| 182 | `GetDraftedEntities` | precondition_diff | See [Accessing Selections that Define Features](<../../docs/Programmin | // No need to roll back to get affected faces | `Get_Faces_Affected_by_Draft_Feature_Example_CSharp.md` |
| 183 | `GetEndVertex` | precondition_diff | If no vertex exists for this edge (such as the edge of a newly created | vPoint2 = swVertex2.GetPoint | `Check_Interference_Between_Two_Bodies_Example_VB.md` |
| 184 | `GetEndVertex` | other_conflict | Because edges have no natural direction, you cannot necessarily predic | If AsyRadius1 <> 0.008 Then ErrorMsg SwApp, "Radius R1 at vertex V1 is | `Create_Asymmetric_Elliptic_Fillets_Example_VB.md` |
| 185 | `GetEnvironment` | unit_diff | All numeric values returned from the IEnvironment object are relative  |         Debug.Print ("        " & lineSymbols(i)) | `Analyze_Text_and_Geometry_in_GTol_Flat_Symbol_Example_VB.md` |
| 186 | `GetEquationParameters` | other_conflict | Obsolete. Superseded by [[ISketchSpline::GetEquationParameters2]]. |     Call skSpline.GetEquationParameters(y, r1, r2, rad, ang, xOff, yOf | `Create_Equation-driven_Curve_Example_VB.md` |
| 187 | `GetExplodeStep` | precondition_diff | Before calling this method, call [[IConfiguration::GetNumberOfExplodeS | swExplodeStep = (ExplodeStep)swConfiguration.GetExplodeStep(0); | `Get_Explode_Step_Example_CSharp.md` |
| 188 | `GetExplodedViewNames` | return_shape_diff | Array of strings of the names of the exploded views in the active conf | vViewName = (object[])swAssembly.GetExplodedViewNames(); | `Create_Exploded_Views_Example_CSharp.md` |
| 189 | `GetExtendedLength` | precondition_diff | You can use a value from 0 to ICenterMark::GroupCount for the GroupID  | for (i = 0; i <= nbrInGroup - 1; i++) | `Get_and_Set_Center_Marks_Set_Example_CSharp.md` |
\| 190 \| `GetFaceTangentTo` \| other_conflict \| - **Index**: Index for the loop where to create the patch \| 	            @params = (object[])swFeatData.Edges;
	            for (i | `Get_Shut-Off_Surface_Data_Example_CSharp.md` |
| 191 | `GetFacesForReplacementCount` | precondition_diff | Call this method before calling [[IReplaceFaceFeatureData::IGetFacesFo | vFacesToReplace = (object[])featData.FacesForReplacement; | `Replace_Face_Example_CSharp.md` |
| 192 | `GetFarSideElements` | return_shape_diff | Array of far side hole elements | swCounterBoreFar = featdata.GetFarSideElements(0) | `Create_Advanced_Hole_Example_VBNET.md` |
\| 193 \| `GetFirstDisplayDimension` \| precondition_diff \| Before you can get a feature's IDisplayDimension, use [[IModelDoc2::Se \| ' Preconditions:
' 1. Open public_documents\samples\tutorial\lesson2\t | `Iterate_Through_Dimensions_in_Model_Example_VB.md` |
| 194 | `GetFirstDisplayDimension` | precondition_diff | Before you can get a feature's IDisplayDimension, use [[IModelDoc2::Se | ' Preconditions:
' 1. Open public_documents\samples\tutorial\advdrawin | `Get_Dimension_of_Distance_Mate_Example_VB.md` |
| 195 | `GetFirstDisplayDimension5` | other_conflict | Call [[IDisplayDimension::GetNext5]] to get the next display dimension | swDispDim = (DisplayDimension)swDispDim.GetNext3(); | `Get_Dimension_Values_in_Drawing_Example_CSharp.md` |
| 196 | `GetFirstDisplayDimension5` | other_conflict | Call [[IDisplayDimension::GetNext5]] to get the next display dimension | swDispDim = swDispDim.GetNext3 | `Get_Dimension_Values_in_Drawing_Example_VBNET.md` |
| 197 | `GetFirstDisplayDimension6` | other_conflict | Call [[IDisplayDimension::GetNext5]] to get the next display dimension | Set swDispDim = swDispDim.GetNext3 | `Get_Dimension_Values_in_Drawing_Example_VB.md` |
| 198 | `GetFirstDocument` | return_shape_diff | If the document first opened is an assembly, then this method returns  | ModelDoc2 modDoc = (ModelDoc2)iSwApp.GetFirstDocument(); | `Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp.md` |
| 199 | `GetFirstSegment` | other_conflict | Because edges returned by this method are not selectable; you should n |         status = swEntity.Select4(True, Nothing) | `Get_Curve_Segments_Example_VB.md` |
| 200 | `GetFitFontHeight` | precondition_diff | This value is used only if the [[IDimensionTolerance::GetFitFontUseDim | Debug.Print("  Height of fit tolerance font: " + fontHeight * 1000.0 + | `Get_Dimension_Tolerance_Example_CSharp.md` |
| 201 | `GetFitFontUseDimension` | other_conflict | True if the fit tolerance font is the same size as the dimension font, | Debug.Print("Dimension fit tolerance font same size as tolerance font? | `Get_Dimension_Tolerance_Example_CSharp.md` |
| 202 | `GetFrameCount` | other_conflict | This method returns the number of frames that this symbol has stored,  | for (int idx = 1; idx <= (swGtol.GetFrameCount() - 1); idx++) | `Get_Text_Items_in_GTol_Frame_Example_CSharp.md` |
| 203 | `GetFrameSymbols3` | precondition_diff | Frame number to examine (1 or 2) | for (int idx = 1; idx <= (swGtol.GetFrameCount() - 1); idx++) | `Get_Text_Items_in_GTol_Frame_Example_CSharp.md` |
\| 204 \| `GetFrameToleranceType` \| other_conflict \| TolType may be one of only swGtolGeomCharSymbol_e.:

- swGcsANG

- swG | boolstatus = swGtolFrame.SetFrameToleranceType((int)swGtolGeomCharSymb | `Get_Gtol_Frame_Information_Example_CSharp.md` |
| 205 | `GetFrameValues` | precondition_diff | Frame number to examine (1 or 2) | for (int idx = 1; idx <= (swGtol.GetFrameCount() - 1); idx++) | `Get_Text_Items_in_GTol_Frame_Example_CSharp.md` |
\| 206 \| `GetFromTo` \| precondition_diff \| If this method returns true, then call [[IGtol::GetFromToText]] and [[ \| boolstatus = swGtol.GetFromTo
boolstatus = swGtol.GetFromToText(swFrom | `Get_Gtol_Frame_Information_Example_VBNET.md` |
| 207 | `GetFromToText` | precondition_diff | Before calling this method, use [[IGtol::GetFromTo]] to determine whet | boolstatus = swGtol.GetFromTo();
boolstatus = swGtol.GetFromToText(out | `Get_Gtol_Frame_Information_Example_CSharp.md` |
| 208 | `GetGTolCount` | precondition_diff | Call this method before calling [[IView::IGetGTols]] to determine the  | Object[] Annotations = (Object[])swView.GetGTols(); | `Get_Annotations_Arrays_Example_CSharp.md` |
\| 209 \| `GetGraphicsBody` \| precondition_diff \| This method is valid only if [[IBody2::IsGraphicsBody]] is true. \| swThisGraphicsBody = (GraphicsBody)swCurBod.GetGraphicsBody();
if (swT | `Inspect_Facets_Example_CSharp.md` |
| 210 | `GetGuideCurvesType` | return_shape_diff | See [Accessing Selections that Define Features](<../../docs/Programmin | Debug.Print (" Type of feature: " & swLoftFeatureData.GetGuideCurvesTy | `Get_Guide_Curves_in_Loft_Feature_Example_VB.md` |
| 211 | `GetImportFileData` | precondition_diff | Path and name of the IGES or DXF/DWG file | stepFileName = "C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2019\s | `Import_STEP_File_Example_VB.md` |
| 212 | `GetImportFileData` | return_shape_diff | [[IGES import data]] or [[DXF/DWG import data]] | swImportStepData = (ImportStepData)swApp.GetImportFileData(stepFileNam | `Import_STEP_File_Example_CSharp.md` |
\| 213 \| `GetInterferenceCount` \| precondition_diff \| Call this method before calling [[IInterferenceDetectionMgr::IGetInter \| vInts = (object[])pIntMgr.GetInterferences();
Debug.Print("Number of i | `Run_Interference_Detection_Example_CSharp.md` |
| 214 | `GetLeaderPointsAtIndex` | precondition_diff | The number of points must also be passed to the method to help prevent | vLeaderPt = swAnn.GetLeaderPointsAtIndex(i) | `Get_Display_Dimensions,_Gtols,_and_Surface-Finish_Symbols_Example_VB.md` |
| 215 | `GetLeaderPointsAtIndex` | other_conflict | - If IAnnotation::GetLeaderStyle returns swNO_LEADER, then the number  | If True = swAnn.GetBentLeader Then | `Get_Display_Dimensions,_Gtols,_and_Surface-Finish_Symbols_Example_VB.md` |
| 216 | `GetLeaderPointsAtIndex` | return_shape_diff | retval[0] = X-coordinate of first leader point | ReDim leaderPt(nNumPts) As Double | `Get_Display_Dimensions,_Gtols,_and_Surface-Finish_Symbols_Example_VB.md` |
| 217 | `GetLength3` | precondition_diff | This method returns the length of the holding (e.g., trimmed) curve an | Debug.Print "  length      = " & swCurve(0).GetLength3(dStartParam, dE | `Create_Temporary_Elliptical_Extrusion_Example_VB.md` |
| 218 | `GetLineAtIndex` | other_conflict | - **Index**: Index of the line; index begins at 0 | lineData = swMultiJogLeader.GetLineAtIndex(1) | `Get_Multi-jog_Leader_Data_Example_VB.md` |
| 219 | `GetLinkedMate` | other_conflict | This mate and its linked mate are siblings in a Hole Set, which is def | swMate = (Mate2)swAssembly.AddConcentricMateWithTolerance((int)swMateA | `Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_CSharp.md` |
| 220 | `GetMaxValue` | other_conflict | - set the tolerance values, use [[IDimensionTolerance::SetValues]]. | status = swDimensionTolerance.SetValues2(0.01, 0.015, swSetValueInConf | `Change_Dimension_Tolerance_in_Configuration_Example_VB.md` |
| 221 | `GetMenuStrings` | other_conflict | Use this method with methods that require you to supply the name of th | swApp.RemoveFromMenu swCommands_Suppress, 1, 3, False | `Remove_Menu_Commands_Menus_and_Toolbar_Buttons_Example_VB.md` |
| 222 | `GetMergeDistance` | unit_diff | By default, points within 0.001mm are merged. | Debug.Print " Merge distance: " & (importData.GetMergeDistance("") * 1 | `Import_DXF_File_into_Part_Sketch_Example_VB.md` |
\| 223 \| `GetMeshBody` \| precondition_diff \| This method is valid only if [[IBody2::IsMeshBody]] is true. \| swThisMeshBody = (MeshBody)swCurBod.GetMeshBody(); //
if (swThisMeshBo | `Inspect_Facets_Example_CSharp.md` |
| 224 | `GetMeshDataAtIndex` | other_conflict | Before calling this method, call [[IScanto3D::GetMeshCount]] to obtain | For i = 0 To MeshCount | `Get_Mesh_Data_Example_VB.md` |
| 225 | `GetMeshDataCountAtIndex` | other_conflict | Before calling this method, call [[IScanto3D::GetMeshCount]] to obtain | For i = 0 To MeshCount | `Get_Mesh_Data_Example_VB.md` |
| 226 | `GetMinValue` | other_conflict | set the tolerance values, use [[IDimensionTolerance::SetValues]]. | status = swDimensionTolerance.SetValues2(0.01, 0.015, (int)swSetValueI | `Change_Dimension_Tolerance_in_Configuration_Example_CSharp.md` |
| 227 | `GetModelPathNamesCount` | precondition_diff | Call this method before calling [[IBomTableAnnotation::IGetModelPathNa |                 vModelPathNames = swTableAnnotation.GetModelPathNames( | `Get_Model_Path_Names_in_BOM_Table_Example_VB.md` |
| 228 | `GetMotionStudy` | return_shape_diff | This method gets the names of both SOLIDWORKS Simulation and SOLIDWORK | Set swMotionStudy1 = swMotionMgr.GetMotionStudy("PhysSim") | `Get_Motion_Study_Example_VB.md` |
| 229 | `GetMotionStudy` | precondition_diff | Use [[IMotionStudy::StudyType]] to ensure that a given study is a moti | swMotionStudy1.StudyType = swMotionStudyType_e.swMotionStudyTypePhysic | `Get_Motion_Study_Example_VB.md` |
\| 230 \| `GetMotionStudyCount` \| precondition_diff \| Use [[IMotionStudy::StudyType]] to ensure that a given study is a moti \| numStudies = swMotionMgr.GetMotionStudyCount()
Set swMotionStudy = swM | `sldworksapi__Fire_Events_for_External_Output_Time_Step_Changes_Example_VB.md` |
| 231 | `GetMotionStudyNames` | precondition_diff | This method gets the names of both SOLIDWORKS Simulation and SOLIDWORK | vNames = swMotionMgr.GetMotionStudyNames()
For i = 0 To UBound(vNames) | `sldworksapi__Create_Motion_Studies_Example_VB.md` |
| 232 | `GetNamedEntitiesCount` | return_shape_diff | **Signature**: `System.int GetNamedEntitiesCount()` | hr
= pPart->GetNamedEntitiesCount
(&nEntCount); | `Get_Named_Entities_Example_CPlusPlus_COM.md` |
| 233 | `GetNextFeature` | other_conflict | When traversing the FeatureManager design tree, your application shoul | typeName = feat.Name
typeName = UCase(typeName)
If "SKETCH" = Left(typ | `Add_Objects_to_Selection_List_Example_VB.md` |
| 234 | `GetNextFeature` | other_conflict | any feature has a specific name. Because features can be renamed, you  | boolstatus = swModel.Extension.SelectByID2("Sketch2", "SKETCH", 0, 0,  | `Add_Objects_to_Selection_List_Example_VB.md` |
\| 235 \| `GetNextSegment` \| other_conflict \| Because edges returned by this method are not selectable; you should n \| 'Select each edge
Do While Not swEdge Is Nothing
Set swEntity = swEdge | `Get_Curve_Segments_Example_VB.md` |
| 236 | `GetNominalNotch` | other_conflict | The longitudinal i, j, and k component vectors indicate the direction  | = "Longitudinal i-component of pierce unit vector is " | `Get_DimXpert_Feature2_Example_VBNET.md` |
\| 237 \| `GetOpenDocument` \| precondition_diff \| Only call this method for a document that has already been opened in i \| ' Assembly components are opened, but are not visible
        ' until  | `Get_Names_of_Open_Documents_Example_VB.md` |
| 238 | `GetOpenDocumentByName` | precondition_diff | Only call this method for a document that has already been opened in i | strDocumentName = swBomFeature.GetReferencedModelName();
	             | `Get_Model_Path_Names_in_BOM_Table_Example_CSharp.md` |
| 239 | `GetPMIData` | return_shape_diff | [[IPMIDatumData]], [[IPMIDimensionData]], [[IPMIGtolData]]; null or No | swPMIDatumData = (PMIDatumData)swAnnotation.GetPMIData();
Debug.Print( | `Get_PMI_Data_Example_CSharp.md` |
| 240 | `GetPMIType` | precondition_diff | This API does not yet support note annotations. | IAnnoType = swAnnotation.GetType();
IAnnoPMIType = swAnnotation.GetPMI | `Get_PMI_Data_Example_CSharp.md` |
| 241 | `GetPTZHeight2` | precondition_diff | is valid only if this Gtol was created in a version of SOLIDWORKS earl | swGtol = (Gtol)swModel.InsertGtol(); | `Insert_GTol_Example_CSharp.md` |
| 242 | `GetParent` | return_shape_diff | If the component is the root component or a top-level component, then  | Set swParentConfig = swConfig.GetParent | `Display_Configuration_Description_in_Bill_of_Materials_Example_VB.md` |
| 243 | `GetPartingLinesCount` | return_shape_diff | Call this method before calling [[IDraftFeatureData2::IGetPartingLines | Debug.Print("    Number of parting lines: " + swPartingSurfaceFeatureD | `Get_and_Set_Parting_Surface_Feature_Data_Example_CSharp.md` |
\| 244 \| `GetPersistReferenceCount3` \| return_shape_diff \| **Signature**: System.int GetPersistReferenceCount3( System.object Di \| long sizePersistIDs;
swDocExt->GetPersistReferenceCount3(disp, &sizePe | `Get_Object_s_Persistent_Reference_ID_Example_CPlusPlus_COM.md` |
| 245 | `GetPreviewBitmap` | precondition_diff | This method is not supported in macros or out-of-process applications  | Option Explicit
Dim swApp As SldWorks.SldWorks
Sub main()
    Set swAp | `Get_Preview_Bitmap_Example_VB.md` |
| 246 | `GetRelatedTangentEdgeCount` | return_shape_diff | Array of visible tangent edges for the specified bendline | nbrRelatedTangentEdges = swView.GetRelatedTangentEdgeCount(BendlinesAr | `Get_Tangent_Edges_of_Bendlines_Example_VB.md` |
\| 247 \| `GetRootComponent3` \| precondition_diff \| 1. [[IModelDoc2::GetConfigurationByName]] (called only once) \|     Set swConfig = swConfigMgr.ActiveConfiguration
    Set swRootComp  | `Fire_Notifications_When_Renaming_Components_Example_VB.md` |
| 248 | `GetRowHeight` | unit_diff | Height of the specified row in meters | RowHeight = swTableAnn.GetRowHeight(J); | `C:\swapi\examples\Get_Components_in_Each_BOM_Table_Row_Example_CSharp.md` |
| 249 | `GetSelectedFaceCount` | other_conflict | Do not use this method for general selection handling. If you want to  | status = swModelDocExt.SelectByID2("", "FACE", -0.0258707587273648, -0 | `Get_Selected_Faces_on_Process_Body_Example_CSharp.md` |
| 250 | `GetSelectedFaceCount` | other_conflict | If you want to handle items selected by the user or items selected wit | swSelFaceCount = swProcBody.GetSelectedFaceCount(); | `Get_Selected_Faces_on_Process_Body_Example_CSharp.md` |
| 251 | `GetSelectedFaces` | other_conflict | Do not use this method for general selection handling. If you want to  | status = swModelDocExt.SelectByID2("", "FACE", -0.0258707587273648, -0 | `Get_Selected_Faces_on_Process_Body_Example_CSharp.md` |
| 252 | `GetSelectedFaces` | other_conflict | If you want to handle items selected by the user or items selected wit | swSelFaceVar = (object[])swProcBody.GetSelectedFaces(); | `Get_Selected_Faces_on_Process_Body_Example_CSharp.md` |
\| 253 \| `GetSelectedObject6` \| return_shape_diff \| ISelectionMgr object obtained from a part or assembly document

[[ICom | swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1); | `Access_and_Release_Access_to_Edges_Example_CSharp.md` |
| 254 | `GetSelectedObject6` | return_shape_diff | ISelectionMgr object obtained from a part or assembly document

[[ICom | Set segments(0) = swSelMgr.GetSelectedObject6(1, 0) | `Access_Structure_System_Corner_Treatments_Example_VB.md` |
| 255 | `GetSelectionFilters` | return_shape_diff | Array of long values representing the [[swSelectType_e]] enumeration | vFilters = (int[])swApp.GetSelectionFilters(); | `Inspect_Facets_Example_CSharp.md` |
| 256 | `GetSketchHatches` | other_conflict | - in drawing views, use [[IView::GetFaceHatchCount]], [[IView::GetFace | Hatching applied by the user is accessed through the ISketchHatch obje | `Get_Hatching_Data_Example_VB.md` |
| 257 | `GetSketchHatches` | other_conflict | - in drawing views, use [[IView::GetFaceHatchCount]], [[IView::GetFace | vSketchHatch = (object[])swSketch.GetSketchHatches(); | `Get_Area_Hatch_Data_Example_CSharp.md` |
\| 258 \| `GetSolidHatchCount` \| return_shape_diff \| - **ArraySize**: Number of solid-fill hatches

## Returns
Size of the  | nbrSolidFillHatches = swView.GetSolidHatchCount(out ArraySize);
       | `Get_Solid-fill_Hatch_Information_Example_CSharp.md` |
| 259 | `GetSpecificFeature2` | other_conflict | For some feature types, this method returns Nothing or null because th | swCornerMgmtFolder = (CornerManagementFolder)swFeat.GetSpecificFeature | `Access_Structure_System_Corner_Treatments__Example_CSharp.md` |
\| 260 \| `GetSplinesInterpolate` \| return_shape_diff \| This complete set of data repeats itself for each spline found in the  \| long splineArraySize = 1
 + (nbrSketchPoints * 3); | `Get_Spline_Points_Example_CPlusPlus_COM.md` |
| 261 | `GetSplinesInterpolate` | return_shape_diff | The return value is an array of doubles formatted as:

[ [NumSplinePoi |  //First value in vSplines array is the number of
//sketch (or spline) | `Get_Spline_Points_Example_CPlusPlus_COM.md` |
| 262 | `GetSplitInformation` | other_conflict | Piece of the table that this is |     If 1 = nIndex Then
        ' Add header offset for first portion o | `Export_BOMs_to_XML_Example_VB.md` |
| 263 | `GetSubAssemblyExplodeSteps` | return_shape_diff | Array of [[IExplodeSteps]] in the subassembly explode view | Set nestedStep = steps(j) | `Add_Explode_Step_Example_VB.md` |
| 264 | `GetSuppression` | return_shape_diff | Suppression state of this component instance as defined in [[swCompone | hres = swComponent->GetSuppression(&lComponentSuppressState); | `Access_Assembly_Example_CPlusPlus_COM.md` |
| 265 | `GetSustainability` | return_shape_diff | [[ISustainabilityApp]] | sustain = (swgsustainabilityApp)PDoc.Extension.GetSustainability(); | `Calculate_Environmental_Impact_of_Part_Example_CSharp.md` |
| 266 | `GetTessPts` | return_shape_diff | The array returned contains the x, y, z location of the tessellation p | For i = 0 To UBound(vTessPts) Step 6 | `Get_Intersecting_Faces_Example_VB.md` |
| 267 | `GetTessTriangles` | precondition_diff | Tessellation information is available only when the component is loade | = swFace.GetTessTriangles(True) | `Get_Part_Bounding_Box_Example_VB.md` |
| 268 | `GetText` | precondition_diff | swDimensionTextParts_e.swDimensionTextAll is not a valid value for the | swDispDim.GetText(swDimensionTextAll) | `Get_Block_Information_Example_VB.md` |
| 269 | `GetTransform` | precondition_diff | 1 <= *Instance* <= [[ICircularPatternFeatureData::TotalInstances]] | for (i = 0; i < NbrInstances; i++) | `Get_Transform_for_Each_Circular_Pattern_Instance_Example_CSharp.md` |
| 270 | `GetUIState` | other_conflict | To see your changes in the FeatureManager design tree, call [[IModelDo | pPartDoc->EditRebuild(); | `Display_of_Item_in_Feature_Manager_Example_CPlusPlus_COM.md` |
| 271 | `GetUnloadedComponentNames` | return_shape_diff | To get whether an assembly has hidden or suppressed unloaded component | if (Reasons[index] == 1) | `Get_Hidden_Components_Filenames_Example_CSharp.md` |
| 272 | `GetUseDocTextFormat` | precondition_diff | The index argument is not used and should be set to 0. | swDetailCircle.GetUseDocTextFormat() | `Create_Detail_Circle_and_Detail_View_Example_CSharp.md` |
\| 273 \| `GetUserPoints2` \| return_shape_diff \| This set of data repeats for each user point in the sketch. The size o \| For i = 0 To UBound(vSketchUserPt) / 3 - 1
        ' Coordinates in sk | `Get_Sketch_Points_and_Their_Persistent_IDs_Example_VB.md` |
| 274 | `GetUserPreferenceInteger` | other_conflict | This method is equivalent to interactively setting document properties | Select Case ModelDocExtension.GetUserPreferenceInteger(swUserPreferenc | `Get_and_Set_User_Preferences_Example_VB.md` |
| 275 | `GetUserPreferenceStringListValue` | other_conflict | - **UserPreference**: User preference as defined in [[swUserPreference | Debug.Print("DxfMappingFiles        = " + swApp.GetUserPreferenceStrin | `Save_Drawing_as_DXF_Example_CSharp.md` |
| 276 | `GetValues` | other_conflict | 8. Set the entities for the x-axis and y-axis feature data objects. | swSimPlotYAxisFeatureData[0].Entities = swEntityArray; | `sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md` |
| 277 | `GetVertexChamferDistance` | other_conflict | The Side parameter is relevant only for vertex-type of chamfers. | swChamfer.GetVertexChamferDistance(0) * 1000.0 + " mm" | `Get_Edge_Chamfer_Distances_Example_CSharp.md` |
| 278 | `GetViewCount` | other_conflict | Gets all of the number of all of views, including the number of sheets | Debug.Print("There are " + count + " views in this drawing including t | `Get_Break_Line_Data_Example_CSharp.md` |
\| 279 \| `GetVirtualEdges` \| other_conflict \| Do not perform any operations on the returned edges as they are only t \|     For i = LBound(ve) To UBound(ve)
        boolstatus = ve(i).Select | `Modify_Fillet_Weld_Bead_Example_VB.md` |
| 280 | `GetVisibleEntities` | other_conflict | Visible entities are only those entities not completely obscured by ot | Iterate and select all edges on the first visible component | `Get_All_Edges_in_Visible_Component_in_Drawing_View_Example_VB.md` |
| 281 | `GetWallThickness` | precondition_diff | This method is relevant only for thin features. | Debug.Print " Is a thin-walled sweep feature? " & swSweep.IsThinFeatur | `Get_Properties_of_Sweep_Feature_Example_VB.md` |
| 282 | `GroupCount` | return_shape_diff | use this property to get a range of valid values for [[ICenterMark::Ge | Debug.Print(" Number in set: " + (nbrInGroup - 1)); | `Get_and_Set_Center_Marks_Set_Example_CSharp.md` |
| 283 | `HWnd` | other_conflict | **All applications are required to be compatible with SOLIDWORKS x64.  | HWnd = swModelWindow.HWnd; | `Switch_Documents_Example_CSharp.md` |
| 284 | `HideNewComponentModels` | precondition_diff | This property applies only to assembly configurations. SOLIDWORKS alwa | ' 1. Open a part that contains one or more configurations. | `Change_Configuration_Properties_Example_VB.md` |
\| 285 \| `IActivateDoc3` \| return_shape_diff \| This file becomes the active document, and this method returns a point \| hres = swApp->IActivateDoc3(sActiveAssembly,
false, &lErrorActivatingD | `Access_Assembly_Example_CPlusPlus_COM.md` |
| 286 | `IActivateDoc3` | return_shape_diff | This file becomes the active document, and this method returns a point | swApp->IActivateDoc3(sAssemblyName,
true, &lErrors, &swModel); | `Add_Component_and_Mate_Example_CPlusPlus_COM.md` |
| 287 | `IAddComponents2` | return_shape_diff | **Signature**: Component2 IAddComponents2( ref System.int Count, ref  | = pAssy->IAddComponents2(&nNumComp,
sPartPath, dTransform, swCompArr); | `Add_Components_and_Transforms_Example_CPlusPlus_COM.md` |
| 288 | `IAddControl` | return_shape_diff | **Signature**: PropertyManagerPageControl IAddControl( System.int ID, | hres = m_pSwGroup_1->IAddControl(id,
controlType, caption, alignment,  | `Set_Up_PropertyManager_Page_Slider_Control_Example_CPlusPlus_COM.md` |
| 289 | `ICreateCircle2` | other_conflict | This method creates a partial arc in the active 2D sketch. | ' Postconditions: A cylinder is created. | `Create_Cylinder_Example_CPlusPlus_COM.md` |
| 290 | `IFirstFeature` | other_conflict | any feature has a specific name. Because features can be renamed, you  | hres = swFeature->get_Name(&sGetFeatureName); | `Access_Assembly_Example_CPlusPlus_COM.md` |
| 291 | `IFirstFeature` | other_conflict | When traversing the FeatureManager design tree, your application shoul | if (sGetFeatureName == sFeatureName) | `Access_Assembly_Example_CPlusPlus_COM.md` |
\| 292 \| `IGetActiveSketch2` \| precondition_diff \| Before you can use this method, you must select and activate a sketch. \| swDoc->IGetActiveSketch2(&swSketch);
if (swSketch == NULL) | `Create_Cylinder_Example_CPlusPlus_COM.md` |
| 293 | `IGetBCurveParams` | return_shape_diff | Pointer to an array of doubles describing the parameters of the curve  | pCurve->IGetBCurveParams( dSplineParams); | `Get_Curve_Spline_Points_Example_CPlusPlus_COM.md` |
\| 294 \| `IGetBCurveParamsSize2` \| return_shape_diff \| Size of the data set returned by [[ICurve::IGetBCurveParams]]. \| pCurve->IGetBCurveParamsSize2( FALSE, TRUE,
&nParamSize); | `Get_Curve_Spline_Points_Example_CPlusPlus_COM.md` |
| 295 | `IGetBody` | other_conflict | This method returns a valid IBody2 object only for fully resolved comp | resultVal = pFace->IGetBody(&pCheckBody); | `Enumerate_Bodies_Example_CPlusPlus_COM.md` |
| 296 | `IGetCurveParams2` | return_shape_diff | The return value is the following array of 11 doubles: | edgeData[10]={NULL}; | `Get_Edge_Data_By_Name_Example_CPlusPlus_COM.md` |
| 297 | `IGetSplinePts` | return_shape_diff | The array returned contains the x, y, z location of the spline points | pCurve->IGetSplinePts( dSplinePts); | `Get_Curve_Spline_Points_Example_CPlusPlus_COM.md` |
| 298 | `IGetSplinePts` | other_conflict | [[ICurve::IGetSplinePtsSize]] defines the spline and determines the si | pCurve->IGetBCurveParams( dSplineParams); | `Get_Curve_Spline_Points_Example_CPlusPlus_COM.md` |
| 299 | `IGetSplinePtsSize` | other_conflict | PropArray contains 4 integers: | *dKnotArray = &dSplineParams[2]; | `Get_Curve_Spline_Points_Example_CPlusPlus_COM.md` |
\| 300 \| `IGetUnits` \| return_shape_diff \| The format of the returned data is an array of shorts: \| hres
= pModelDoc->IGetUnits(unitArray); | `Get_and_Set_Units_Example_CPlusPlus_COM.md` |
| 301 | `IGetVersionHistoryCount` | return_shape_diff | Size of array required for the version history | hres
= pModelDoc->IGetVersionHistoryCount(&versHistCount); | `Document_Version_History_Example_CPlusPlus_COM.md` |
| 302 | `INewDocument2` | return_shape_diff | Newly created [[document]] or NULL if the operation fails | hres = swApp->INewDocument2(sDrawingDocTemplate,
lPaperSize, dWidth, d | `Access_Assembly_Example_CPlusPlus_COM.md` |
| 303 | `ISketchSplineByEqnParams` | return_shape_diff | True if created successfully, false if not | hr
= pModel->ISketchSplineByEqnParams(pPropArray,
pKnotsArray, pCntrlP | `Insert_Spline_in_Drawing_Example_CPlusPlus_COM.md` |
| 304 | `ISketchSplineByEqnParams` | other_conflict | The PropArray argument contains 4 integers packed into the first two d | int
pPropArray[4]; | `Insert_Spline_in_Drawing_Example_CPlusPlus_COM.md` |
| 305 | `IVersionHistory` | return_shape_diff | Array of strings showing the history of the document | hres
= pModelDoc->IVersionHistory(versionHistStrings); | `Document_Version_History_Example_CPlusPlus_COM.md` |
| 306 | `InnerRadius` | precondition_diff | - [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToP | swFeatData.FeaturesToPatternType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 307 | `InnerRadius` | precondition_diff | - [[IFillPatternFeatureData::CreateSeedCutType]] = [[swCreateSeedCutTy | swFeatData.CreateSeedCutType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 308 | `InsertBomTable3` | precondition_diff | The system does not default to the Default configuration when you spec |             swBomTableAnnotation = (BomTableAnnotation)swModelDocExt.I | `Get_BOM_Balloon_Properties_Example_CSharp.md` |
\| 309 \| `InsertBomTable6` \| precondition_diff \| If the BOM table is a parts-only or indented-style BOM and the Configu \|     BomType = swBomType_Indented
    TableTemplate = "C:\Program Files | `Dissolve_Subassembly_in_a_BOM_Table_Example_VB.md` |
| 310 | `InsertBreak` | other_conflict | - **Orientation**: Horizontal or vertical cut as defined in [[swBreakL |             swBreakLine = (BreakLine)swView.InsertBreak(0, -0.02919508 | `Create_Broken_View_Example_CSharp.md` |
| 311 | `InsertCoordinateSystem` | precondition_diff | Make the selections using [[IModelDocExtension::SelectByID2]] with a m | bRet = swSkCofG.Select4(True, swSelData): Debug.Assert bRet | `Insert_Coordinate_System_Feature_at_Center_of_Mass_Example_VB.md` |
| 312 | `InsertCoordinateSystem` | return_shape_diff | Feature InsertCoordinateSystem( System.bool XFlippedIn, System.bool YF | bRet = swModel.InsertCoordinateSystem(False, False, False): Debug.Asse | `Insert_Coordinate_System_at_Center_of_Mass_Example_VB.md` |
| 313 | `InsertCutSurface` | other_conflict | Empty array indicating to cut all bodies that intersect with the cut | swFeature = (Feature)swFeatureManager.InsertCutSurface(false, 0, false | `Insert_Surface-cut_Feature_Example_CSharp.md` |
| 314 | `InsertCutSwept5` | mark_diff | - 1 = Sketch profile or tool body | status = swModelDocExt.SelectByID2("", "EDGE", -0.0372983839416747, 0. | `Create_Cut-sweep_Feature_Using_Circular_Profile_Example_CSharp.md` |
\| 315 \| `InsertCutSwept5` \| mark_diff \| - 2 = Guide curve, if provided

- 4 = Sweep path | status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp.md` |
| 316 | `InsertDwgOrDxfFile2` | precondition_diff | Before calling this method, select a plane or planar surface on which  | bRet = swModel.Extension.SelectByID2("Sheet1", "SHEET", 0.0, 0.0, 0, f | `Insert_and_Position_DXF_File_in_Drawing_Example_CSharp.md` |
\| 317 \| `InsertEndCapFeature2` \| other_conflict \| Call [[IFeatureManager::InsertEndCapFeature3]] if you want to pre-sele \| boolstatus
= Part.Extension.SelectByID2("", "FACE", 0.6023443450227,
0 | `Insert_Weldment_Features_Example_CSharp.md` |
| 318 | `InsertFeatureReplaceFace` | return_shape_diff | True if the edges match, false if not | Part.InsertFeatureReplaceFace(); | `Replace_Face_Example_CSharp.md` |
| 319 | `InsertFillSurface2` | precondition_diff | You must use [[IModelDocExtension::SelectByID2]] and the following Mar | bRet = swEnt.Select4(true, swSelData); | `Get_and_Fill_Gaps_in_Body_Example_CSharp.md` |
| 320 | `InsertFillSurface2` | other_conflict | **VPatchBoundaries**: Array of [[edges]] or [[sketches]] for the patch | swFeat = (Feature)swFeatMgr.InsertFillSurface2(3, (int)swFeatureFillSu | `Get_and_Fill_Gaps_in_Body_Example_CSharp.md` |
| 321 | `InsertProtrusionBlend2` | mark_diff | - 2 = guide curve selections | status = swModelDocExt.SelectByID2("Sketch3", "SKETCH", 0, 0, 0, true, | `Get_Guide_Curves_in_Loft_Feature_Example_CSharp.md` |
| 322 | `InsertRefPlane` | precondition_diff | Before calling this method, you must have selected the reference entit |             stat = modDocExt.SelectByRay(0.199999999999932d, 0.0028064 | `Create_Face_Plane_Intersection_SSMember_Example_CSharp.md` |
| 323 | `InsertReferencePoint` | return_shape_diff | Pointer to the [[IFeature]] object |     vFeatArr = swFeatMgr.InsertReferencePoint(swRefPointAlongCurve, sw | `Insert_Reference_Points_Example_VB.md` |
| 324 | `InsertReferencePoint` | precondition_diff | The NumberOfRefPoints argument must contain a value of 1 to successful |     vFeatArr = swFeatMgr.InsertReferencePoint(swRefPointAlongCurve, sw | `Insert_Reference_Points_Example_VB.md` |
| 325 | `InsertRevisionCloud` | other_conflict | 3. Call [[IRevisionCloud::ArcRadius]] to set the arc radius of the rev |                     RevCloud.ArcRadius = 0.00508; | `Insert_Revision_Cloud_into_Drawing_Example_CSharp.md` |
| 326 | `InsertRow` | precondition_diff | - is valid only if Where is set to swTableItemInsertPosition_e.swTable | boolstatus = theTableAnnotation.InsertRow(4, 0) | `Get_and_Set_Column_Types_and_Cell_Equations_Example_VB.md` |
| 327 | `InsertScene` | other_conflict | Call [[IModelView::GraphicsRedraw]] or [[IModelView::IGraphicsRedraw]] | // and rebuild the model to see it | `Get_Render_References_Example_CSharp.md` |
\| 328 \| `InsertSewRefSurface` \| unit_diff \| A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1  | Debug.Print("  Knit tolerance: " + swSurfaceKnitFeature.KnitTolerance  | `Create_Surface_Knit_Feature_Example_CSharp.md` |
| 329 | `InsertSewRefSurface` | unit_diff | A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1  | swNewFeatMgr.InsertSewRefSurface(true, false, false, 3.001639406912E-0 | `Fill_Holes_in_Part_Example_CSharp.md` |
| 330 | `InsertSketchForEdgeFlange` | precondition_diff | After calling this method, you must create the profile for the flange  | swFeature = swModel.FeatureManager.InsertSheetMetalEdgeFlange2((vFlang | `Create_Corner_Relief_Feature_Example_CSharp.md` |
| 331 | `InsertSketchText` | other_conflict | If an entity is not selected, Text appears horizontally starting at th | This example shows how to insert a sketch of text at an angle. | `Insert_Text_at_Angle_Example_VB.md` |
| 332 | `InsertVariablePitchHelix` | other_conflict | 2. [[IFeatureManager::AddVariablePitchHelixFirstPitchAndDiamenter]] to | status = swFeatureManager.AddVariablePitchHelixFirstPitchAndDiameter(0 | `Create_Variable_Pitch_Helix_Example_CSharp.md` |
| 333 | `InsertVaryInstanceIncrement` | other_conflict |   "Spacing Increment" | boolstatus = swFeatureMgr.InsertVaryInstanceIncrement("Space Increment | `Create_Circular_Pattern_Example_CSharp.md` |
\| 334 \| `InsertVaryInstanceOverride` \| other_conflict \|   If OverrideType is ...
  Then set Direction to ...

  2

  - 0 = dir | status = swFeatureManager.InsertVaryInstanceOverride("D1@Sketch2@cstic | `Insert_Advanced_Variable_Pattern_Feature_Example_CSharp.md` |
| 335 | `InsertVaryInstanceOverride` | other_conflict |   "Spacing Increment" | boolstatus = swFeatureMgr.InsertVaryInstanceOverride("Space Increment" | `Create_Circular_Pattern_Example_CSharp.md` |
| 336 | `InsertWeldTable` | other_conflict | - **AnchorType**: Anchor type as defined by [[swBomConfigurationAnchor | boolResult = swActiveView.InsertWeldTable(false, true, true, 0, 0, (in | `Insert_Weld_Table_Example_CSharp.md` |
\| 337 \| `InsertWeldmentTrimFeature2` \| mark_diff \| - 1 = Body or bodies to trim

- 2 = Trimming boundaries (body or face) | = Part.Extension.SelectByID2("Structural Member1[2]", "SOLIDBODY",
0,  | `Insert_Weldment_Features_Example_CSharp.md` |
| 338 | `InsertWrapFeature` | precondition_diff | - 2 = Pull direction if Type is swWrapSketchType_e.swWrapSketchType_Em |     ' Mark the sketch to use for wrap feature as 4
    boolstatus = sw | `Insert_Wrap_Feature_Example_VB.md` |
| 339 | `InstallModelColorizer` | other_conflict | the SOLIDWORKS Design software calls [[ISwColorContour::Value]] on eac | public class ColorContour : ISwColorContour1 | `Custom_Colorize_a_Model_Example_CSharp.md` |
\| 340 \| `InstanceCount` \| precondition_diff \| This property is available to all types of chain patterns when [[IChai \| swChainPatternFeatureData.FillPath = true;
Debug.Print("Number of inst | `Create_and_Modify_Distance_Chain_Pattern_Feature_Example_CSharp.md` |
| 341 | `InstanceSpacing` | precondition_diff | Only valid

Both are true:

[[IFillPatternFeatureData::LayoutSpacingTy | swFeatData.InstanceSpacing = 0.0170240490494193;
swFeatData.LayoutSpac | `Create_Fill_Pattern_Example_CSharp.md` |
| 342 | `IsBcurve` | other_conflict | This method returns True if the curve is an intersection curve, ellips | Set swCurve = swEdge.GetCurve: Debug.Assert swCurve.IsBcurve | `Get_Length_of_Spline_or_Elliptical_Edge_Example_VB.md` |
\| 343 \| `IsCircle` \| other_conflict \| Use [[IEdge::GetCurveParams2]] or [[IEdge::IGetCurveParams2]] to deter \| if(S_OK!=pCurve->IsCircle(&pCBool)\|\|pCBool==FALSE) \| `Get_Circular_Holes_In_Face_Example_CPlusPlus_COM.md` \|
| 344 | `IsClosed` | return_shape_diff | True if the sketch contour is open, false if closed | if ((closed == false)) | `Get_Sketch_Contours_Example_CSharp.md` |
| 345 | `IsClosed` | return_shape_diff | True if the sketch contour is open, false if closed | Debug.Print("  Sketch contour " + i + " is closed? " + skcontour.IsClo | `Create_Extrude_Feature_Using_Sketch_Contours_Example_CSharp.md` |
| 346 | `IsCustomPropertyEditable` | precondition_diff | Use [[ICustomPropertyManager::GetNames]] to populate PropertyName. | bRet = cusPropMgr.IsCustomPropertyEditable("ADATE", config.Name) | `Get_Custom_Properties_for_Configuration_Example_VB.md` |
| 347 | `IsDetached` | precondition_diff | - [[ICenterMark::GroupCount]] to get a valid value for Index for a cen | For i = 0 To nbrInGroup - 1 | `Get_and_Set_Center_Marks_Set_Example_VBA.md` |
\| 348 \| `IsFixed` \| precondition_diff \| To determine if a component is fixed or floating, you must begin the t \| ' Select subassembly
status = swModelDocExt.SelectByID2("blade shaft-1 | `Get_Component_State_Example_VB.md` |
| 349 | `IsHiddenLock` | precondition_diff | Call this property during FeatureManager tree traversal to locate the  | Debug.Print(feat.Name + " has a hidden lock? " + feat.IsHiddenLock()); | `Move_Freeze_Bar_Example_CSharp.md` |
| 350 | `IsMultipleRadius` | precondition_diff | This property is valid only for symmetric constant radius fillets and  | // 1. Open a model document with a simple fillet feature. | `Get_Data_for_Simple_Fillet_Example_CSharp.md` |
| 351 | `IsMultipleRadius` | precondition_diff | This property is valid only for symmetric constant radius fillets and  | Debug.Print("   Multiple radii? " + swFillet.IsMultipleRadius); | `Get_Data_for_Simple_Fillet_Example_CSharp.md` |
\| 352 \| `IsOpenedViewOnly` \| precondition_diff \| You application should check for view-only mode to determine how to pr \|     vVersionHistory = swDocument.VersionHistory
    If (Not IsEmpty(vV | `Get_Version_History_of_Future_Version_Document_Example_VB.md` |
| 353 | `IsOpenedViewOnly` | precondition_diff | **NOTE:** When a file is in view-only mode, many API queries return NU | lOptions = lOptions Or swOpenDocOptions_e.swOpenDocOptions_Silent
     | `Get_Version_History_of_Future_Version_Document_Example_VBNET.md` |
| 354 | `IsSamePersistentID` | precondition_diff | Use this method when your application is passed two entities that your | // Get the persistent reference IDs of the
            // selected obj | `Compare_Selected_Objects_and_Their_Persistent_Reference_IDs_Example_CSharp.md` |
| 355 | `IsSamePersistentID` | precondition_diff | Use this method when your application is passed two entities that your | selObjPID1 = swModelDocExt.GetPersistReference3(selObj1)
        selOb | `Compare_Selected_Objects_and_Their_Persistent_Reference_IDs_Example_VB.md` |
| 356 | `IsSupportedMatesAvailable` | precondition_diff | If this property is true, then use [[IAssemblyDoc::CollectAllSupportiv | boolstatus = Assem.IsSupportedMatesAvailable;
var = (object[])Assem.Co | `Create_Mate_Controller_Example_CSharp.md` |
| 357 | `IsTolerant` | other_conflict | is greater than 1/2 of the session precision (i.e., > 5.0E-9 mm), then | * tolerant (distance to neighbor is greater than 5.0E-9 mm). | `Get_Maximum_Edge_and_Vertex_Gaps_Example_VB.md` |
\| 358 \| `KeepCapColor` \| precondition_diff \| This property is valid only if [[ISectionViewData::ShowSectionCap]] is \| data.ShowSectionCap = True
    data.KeepCapColor = True
    data.Graph | `Create_Section_View_in_Model_Example_VB.md` |
| 359 | `KeepCurrentItemNumbers` | other_conflict | Rows in a BOM table can be reordered in several different ways. For ex | Debug.Print("   Keep missing items:       " + swWeldmentCutListFeat.Ke | `Get_Weldment_Cut-list_Feature_and_Annotations_Example_CSharp.md` |
| 360 | `KeepReplacedCompOption` | precondition_diff | This property is valid only if [[IBomFeature::KeepMissingItems]] is se | Debug.Print("  Strikeout missing items? " + swBOMFeature.StrikeoutMiss | `Insert_and_Show_BOM_Table_and_BOM_Balloon_Example_CSharp.md` |
\| 361 \| `KnitResult` \| precondition_diff \| This property is only available if:

- [[ISurfExtrudeFeatureData::Both |     swFeatureManager.FeatureExtruRefSurface3 False, False, swStartCond | `Insert_Extruded_Reference_Surface_Example_VB.md` |
| 362 | `KnitResult` | precondition_diff | - [[ISurfExtrudeFeatureData::DeleteOriginalFace]] = true. |     swFeatureManager.FeatureExtruRefSurface3 False, False, swStartCond | `Insert_Extruded_Reference_Surface_Example_VB.md` |
| 363 | `Layer` | other_conflict | In Drawing documents, annotations can be created on a specific layer.  | Debug.Print (" Orientation: " & swBreakLine.Layer) | `Create_Broken_View_Example_VB.md` |
| 364 | `LayerOverride` | return_shape_diff | When you get this property, the returned bit value indicates which pro | Debug.Print("      Layer override? " + swSketchHatch.LayerOverride); | `Get_Area_Hatch_Data_Example_CSharp.md` |
\| 365 \| `LightWeight` \| precondition_diff \| [[IDocumentSpecification::UseLightWeightDefault]] must be false for th \|         swDocSpecification.UseLightWeightDefault = true;
        swDoc | `Get_Whether_Components_Are_Loaded_Example_CSharp.md` |
| 366 | `LightWeight` | precondition_diff | [[IDocumentSpecification::UseLightWeightDefault]] must be false for th |         swDocSpecification.UseLightWeightDefault = True
        swDocS | `Get_Whether_Components_Are_Loaded_Example_VBNET.md` |
| 367 | `LinkParentConfiguration` | other_conflict | After setting this property, call [[IModelDoc2::EditRebuild3]]. | if (status)
{
    Debug.Print("Projected view now linked to parent con | `Link_Projected_View_to_Parent_Configuration_Example_CSharp.md` |
| 368 | `ListExternalFileReferencesCount` | other_conflict | Call this method before calling [[IComponent2::IListExternalFileRefere | nRefCount = swComp.ListExternalFileReferencesCount
swComp.ListExternal | `Get_External_References_Example_VB.md` |
| 369 | `LoadFile4` | precondition_diff | Before calling this method, turn on 3D Interconnect by setting **Tools | Set newDoc = swApp.LoadFile4(filename, "", importData, longerrors) | `Import_DXF_File_into_Part_Sketch_Example_VB.md` |
\| 370 \| `LockAngle` \| precondition_diff \| This property is valid only when:

- merging two bodies in a multibody | FeatData.LockAngle = true;
                FeatData.OffsetType = (int) | `Create_Edge_Flange_Example_CSharp.md` |
| 371 | `LowerText` | other_conflict | You can only get or set the lower text in a BOM balloon using [[INote: | StackedBalloonParams.LowerText = "Lower Text"; | `Insert_and_Show_BOM_Table_in_Assembly_Example_CSharp.md` |
\| 372 \| `MaintainThreadLength` \| precondition_diff \| This property is valid only if:

- [[IThreadFeatureData::Offset]] is s | Debug.Print("Offset the starting location of the helix? " + swThreadFe | `Create_a_Thread_Feature_Example_CSharp.md` |
| 373 | `MaintainThreadLength` | precondition_diff | - [[IThreadFeatureData::EndCondition]] is set to [[swThreadEndConditio | swThreadFeatData.EndCondition = (int)swThreadEndCondition_e.swThreadEn | `Create_a_Thread_Feature_Example_CSharp.md` |
| 374 | `MajorDiameter` | precondition_diff | This property is relevant only for swTapered and swTaperedDrilled hole | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 375 | `MakeAssemblyFromSelectedComponents` | other_conflict | If **Tools > Options > System Options > Assemblies >  Save new compone | '    on the Tools > Options > Assemblies dialog is selected. | `Make_Assembly_From_Selected_Components_Example_VB.md` |
| 376 | `MakeAssemblyFromSelectedComponents` | precondition_diff | Be sure to save the parent assembly before calling this method. | ' NOTE: Because the assembly is used elsewhere, do not save changes. | `Make_Assembly_From_Selected_Components_Example_VB.md` |
\| 377 \| `MakeOffset` \| precondition_diff \| Creates a new temporary body by offsetting the selected surface body b \| ' 3. Selects an edge on the surface body to offset.
' 4. Creates two t | `Create_Temporary_Bodies_by_Offsetting_Surface_Body_Example_VB.md` |
| 378 | `MakeSketchBlockFromSelected` | precondition_diff | Creates a block definition at the specified location from the selected | Set swSketchBlockDef = swSketchMgr.MakeSketchBlockFromSelected(Nothing | `Create_Block_Definition_and_Insert_Block_Instance_Example_VB.md` |
\| 379 \| `MaterialPropertyValues2` \| precondition_diff \| This property is intended to be used on bodies other than the base bod \|     For i = 0 To 5
        vBodyArr = swPart.GetBodies2(i, False) | `Get_Material_Property_Values_Example_VB.md` |
| 380 | `MaxDamping` | precondition_diff | Available only when [[ISimulation3DContactFeatureData::UseRestitutionC |                 if (swContFeat.UseRestitutionCoefficient)
             | `Create_3D_Contact_Feature_Example_CSharp.md` |
| 381 | `MaxValueForGapRange` | unit_diff | Maximum gap should be in the range of [[ISurfaceKnitFeatureData::KnitT |             Debug.Print("  Maximum value for gap range: " + swSurfaceK | `Create_Surface_Knit_Feature_Example_CSharp.md` |
| 382 | `MaxValueForGapRange` | precondition_diff | [[ISurfaceKnitFeatureData::UseGapFilters]] must be true for this prope |             Debug.Print("  Maximum value for gap range: " + swSurfaceK | `Create_Surface_Knit_Feature_Example_CSharp.md` |
| 383 | `MaxVariation` | precondition_diff | This property is valid only if [[IPMIDimensionItem::TolType]] returns  |                                         Debug.Print("    Tolerance typ | `Get_PMI_Data_Example_CSharp.md` |
\| 384 \| `MaxWitnessLineLength` \| other_conflict \| After using this property, use [[IModelDoc2::GraphicsRedraw2]] to redr \|       swDisplayDim.MaxWitnessLineLength = 130
   End If
   maxLineLeng | `Set_and_Get_Maximum_Extension_Line_Length_Example_VB.md` |
| 385 | `MaximumAngle` | precondition_diff | This property is valid only if [[IAngleMateFeatureData::IsAdvancedMate | swAngleMateData.MaximumAngle = 0.523599; | `Create_Limit_Angle_Mate_Example_CSharp.md` |
| 386 | `MaximumDistance` | precondition_diff | This property is valid only if [[IDistanceMateFeatureData::IsAdvancedM | swDistMateData.MaximumDistance = 0.0254 | `Create_Limit_Distance_Mate_Example_VB.md` |
\| 387 \| `MergeBendTags` \| precondition_diff \| Unmerge a merged bend tag

1. Select the drawing view in which the mer | status = swDrawingDoc.ActivateView("Drawing View1");
            statu | `Merge_and_Unmerge_Bend_Tags_Example_CSharp.md` |
| 388 | `MergeSmoothFaces` | precondition_diff | This property corresponds to the **Merge smooth faces** check box on t | boolstatus = swModel.Extension.SelectByID2("Sketch4", "SKETCH", 3.6837 | `Insert_Bidirectional_Swept-cut_Feature_Example_VB.md` |
| 389 | `MidCounterSinkAngle` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | (int)swWzdGeneralHoleTypes_e.swWzdCounterBore, (int)swWzdHoleStandards | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 390 | `MidCounterSinkDiameter` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | (int)swWzdGeneralHoleTypes_e.swWzdCounterBore, (int)swWzdHoleStandards | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 391 | `MinimumAngle` | precondition_diff | This property is valid only if [[IAngleMateFeatureData::IsAdvancedMate | swAngleMateData.MinimumAngle = 0.506145; | `Create_Limit_Angle_Mate_Example_CSharp.md` |
| 392 | `MinimumDistance` | precondition_diff | This property is valid only if [[IDistanceMateFeatureData::IsAdvancedM | swDistMateData.MinimumDistance = 0.01; | `Create_Limit_Distance_Mate_Example_CSharp.md` |
| 393 | `MinorDiameter` | precondition_diff | This property is relevant only for swTapered and swTaperedDrilled hole | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 394 | `MirrorPart2` | return_shape_diff | Feature MirrorPart2( System.bool BreakLink, System.int Options, out Mo | mirrorFeature = swPart.MirrorPart2(False, mirrorOptions, resultPart) | `Get_Mirror_Part_Information_Example_VBNET.md` |
| 395 | `MirrorTransferOptions` | other_conflict | If not set, this property defaults to swMirrorPartOptions_e.swMirrorPa | importOptions = (int)swMirrorPartOptions_e.swMirrorPartOptions_ImportS | `Mirror_Components_II_Example_CSharp.md` |
\| 396 \| `MirroredComponentFilenames` \| precondition_diff \| [[IMirrorComponentFeatureData::NameModifierType]] is set to [[swMirror \| swMirroCompFeatData.MirroredComponentFilenames = namesVar;
swMirroComp | `Mirror_Components_II_Example_CSharp.md` |
| 397 | `MiterMergeCondition` | precondition_diff | This property is only available when [[IStructuralMemberGroup::CornerT | Debug.Print(" Original merge miter trimmed bodies setting: " + group.M | `Merge_Miter_Trimmed_Bodies_Example_CSharp.md` |
| 398 | `MiterMergeCondition` | other_conflict | [[swSolidworksWeldmentEndCondOptions_e]].swEndConditionMiter | Debug.Print(" Corner treatment type (1 = swSolidworksWeldmentEndCondOp | `Merge_Miter_Trimmed_Bodies_Example_CSharp.md` |
| 399 | `MotionBlur` | precondition_diff | A ray-trace rendering engine must be active to enable motion blur when | swSaveAVIData.RendererType = (int)swRendererType_e.swRendererType_Soli | `sldworksapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_CSharp.md` |
\| 400 \| `Names` \| precondition_diff \| After calling this method:

1. Call [[IDisplayStateSetting::Entities]] | swDisplayStateSetting.Entities = swComponents
swDisplayStateSetting.Op | `Change_Color_of_Component_in_Specific_Display_State_Example_VB.md` |
| 401 | `NearCounterSinkDiameter` | precondition_diff | This property is relevant only for swCounterSunk and swCounterSunkDril | Debug.Print("  NearCounterSinkDiameter      = " + swWizHole.NearCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 402 | `NearSideCounterSink` | other_conflict | ****NOTE:** This property is a get-only property. Set is not implement | FeatureData.NearSideCounterSink = true; | `Select_Near_and_Far_Side_Countersink_Hole_Options_Example_CSharp.md` |
| 403 | `Normal` | precondition_diff | If the face is not a planar face, then this property returns 0,0,0. | ' 2. Select a sketch. | `Get_Plane_or_Face_for_Sketch_Example_VB.md` |
| 404 | `NumberOfCopies` | precondition_diff | Call this property after calling [[IMoveCopyBodyFeatureData::Copy]]. | Debug.Print("  Number of copies: " + swMoveCopyBodyFeatureData.NumberO | `Move_and_Copy_Body_Using_Vertex_Example_CSharp.md` |
| 405 | `ObjectType` | return_shape_diff | Currently only [[features]] and [[components]] are supported. Null is  | nodeObjectType = node.ObjectType; | `Expand_and_Collapse_FeatureManager_Design_Tree_Nodes_Example_CSharp.md` |
\| 406 \| `Option` \| precondition_diff \| After calling this method:

1. Call [[IDisplayStateSetting::Names]] or | swDisplayStateSetting.Entities = swComponents
swDisplayStateSetting.Op | `Change_Color_of_Component_in_Specific_Display_State_Example_VBNET.md` |
| 407 | `Orientation` | precondition_diff | This property is not valid if [[IAdvancedHoleElementData::ElementType] | Set swAdvHole_Near_2 = swModel.Extension.CreateAdvancedHoleElementData | `Create_Advanced_Hole_Example_VB.md` |
| 408 | `Orientation` | precondition_diff | This property is not valid if [[IAdvancedHoleElementData::ElementType] | Set swAdvHole_Far_2 = swModel.Extension.CreateAdvancedHoleElementData( | `Create_Advanced_Hole_Example_VB.md` |
| 409 | `Origin` | precondition_diff | Before calling this property to change the origin setting, set [[IDrag | swDrag.Origin = swPickPt; | `Create_Drag_Arrow_Manipulator_Example_CSharp.md` |
| 410 | `Origin` | precondition_diff | Before calling this property to change the origin setting, set [[IDrag | swTmpManipulator.Origin = swMathPoint; | `Create_Drag_Arrow_Manipulator_Example_CSharp.md` |
\| 411 \| `OverrideMomentsOfInertia` \| precondition_diff \| After setting this property to true, call:

- [[IMassPropertyOverrideO | OvProp.OverrideMomentsOfInertia = true; OvProp.SetOverrideMomentsOfIne | `Get_Mass_Properties_Using_IMassProperty_Example_CSharp.md` |
| 412 | `Penetration` | precondition_diff | Available only when [[ISimulation3DContactFeatureData::UseRestitutionC |         If swContFeat.UseRestitutionCoefficient Then
            Debug | `Create_3DContact_Feature_Example_VB.md` |
| 413 | `PlanarTrimOption` | precondition_diff | This property is valid only if [[IComplexCornerTreatmentFeatureData::P | 'Below is valid only if PlanarTrimToolType is set to
'swCornerTreatmen | `Access_Structure_System_Corner_Treatments_Example_VB.md` |
| 414 | `PostIntersect` | precondition_diff | Before calling this method, you must call [[IFeatureManager::PreInters | bodyArray = (object[])swFeatureMgr.PreIntersect2(false, 1); | `Create_Intersect_Feature_Example_CSharp.md` |
\| 415 \| `PostMessageToApplication` \| other_conflict \| **All applications are required to be compatible with SOLIDWORKS x64.  \| iSwApp.PostMessageToApplication(userAddin.Cookie,
    pCallbackData.To | `Create_TaskPaneView_Add-in_Example_CSharp.md` |
| 416 | `PostSplitBody2` | precondition_diff | 2. Call [[IFeatureManager::PreSplitBody]] to get all of the bodies cre | vResultingBodies = (object[])swFeatMgr.PreSplitBody2(); | `Create_Split-body_Feature_Example_CSharp.md` |
| 417 | `PreSplitBody2` | other_conflict | 3. Create the Split feature using [[IFeatureManager::PostSplitBody]]. | Set swFeat = swFeatMgr.PostSplitBody2((vBodiesToMark), True, (vBodyOri | `Create_Split-body_Feature_Example_VB.md` |
\| 418 \| `PreTrimSurface` \| precondition_diff \| After calling this method:

1. Select the trimming surfaces or trim to | // Select surface features
            status = swModelDocExt.SelectBy | `Create_Solid_Body_Surface_Trim_Feature_Example_CSharp.md` |
| 419 | `PrincipalMomentsOfInertia` | precondition_diff | If [[IMassPropertyOverrideOptions::OverrideMomentsOfInertia]] is true  |        	pmoi = MyMassProp.PrincipalMomentsOfInertia
       	Debug.Prin | `Get_Mass_Properties_Using_IMassProperty_Example_VBNET.md` |
| 420 | `ProfileAngleDim` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::UseAngleDimForP | swFeatData.ProfileAngleDim = 0.0; | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 421 | `ProfileHeightDim` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::ProfileDimensio | swFeatData.ProfileHeightDim = 0.0; | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 422 | `ProfileLengthDim` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::ProfileDimensio | swFeatData.ProfileDimensionScheme = (int)swSheetMetalGussetProfileDimT | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 423 | `ProfileSize` | return_shape_diff | **Signature**: `System.string ProfileSize {get;}` | profDef.ProfileSize = "ROUND BAR 23"; | `Access_Structure_System_Corner_Treatments__Example_CSharp.md` |
| 424 | `ProfileStandard` | return_shape_diff | **Signature**: `System.string ProfileStandard {get;}` | profDef.ProfileStandard = "GB"; | `Access_Structure_System_Corner_Treatments__Example_CSharp.md` |
| 425 | `PropagateVisualProperty` | other_conflict | See [Accessing Selections that Define Features](<../../docs/Programmin | swFeatData.PropagateVisualProperty = true; | `Create_Table_Pattern_Example_CSharp.md` |
\| 426 \| `PublishSTEP242File` \| precondition_diff \| This method requires that the SOLDWORKS MBD add-in be loaded. ([[ISldW \| // 1. Verify that:
//    * specified part,
//    * SOLIDWORKS MBD 3D P | `Export_SOLIDWORKS_MBD_to_STEP_242_Example_CSharp.md` |
| 427 | `PublishTo3DPDF` | precondition_diff | - requires the that the SOLDWORKS MBD add-in be loaded. ([[ISldWorks:: | // 1. Verify that the specified SOLIDWORKS MBD 3D PDF theme,
//    fil | `Attach_Files_to_MBD_3D_PDF_Example_CSharp.md` |
| 428 | `RadiusOfCurvature` | precondition_diff | Curvature control must be enabled for this property to have an effect. | swSplineHandle.RadiusOfCurvature = swSplineHandle.RadiusOfCurvature /  | `Get_and_Set_Spline_Handles_Example_CSharp.md` |
| 429 | `RealView` | precondition_diff | [[IMaterialVisualPropertiesData::AdvancedGraphics]] must be True to se | // Set the material visual properties to be just color, no advanced gr | `Get_and_Set_Material_Visual_Properties_Example_CSharp.md` |
\| 430 \| `RealView` \| other_conflict \| [[IMaterialVisualPropertiesData::AdvancedGraphics]] must be True to se \| if (bRealView == false)
{
    Debug.Print("Advanced graphics - SOLIDWO | `Get_and_Set_Material_Visual_Properties_Example_CSharp.md` |
| 431 | `Rebuild` | precondition_diff | Use [[IModelDoc2::GetType]] to check the type of document. | 'After rebuilding the part
    Set obj = Nothing
    Call Part.Rebuild | `Get_Object_s_Persistent_Reference_ID_Example_VB.md` |
| 432 | `Reference` | return_shape_diff | Mate references can be one or more entities of a component used for au | swEnt = (Entity)swMateEnt.Reference; | `Edit_Mate_Example_CSharp.md` |
\| 433 \| `ReferencedConfiguration` \| precondition_diff \| You can use this property to change the active configuration of:

- a  | ' 1. Open an assembly document.
' 2. Select a component. | `Change_Referenced_Configuration_Example_VB.md` |
| 434 | `ReferencedDocument` | return_shape_diff | Because section views do not have referenced documents, this method re | swModel = (ModelDoc2)swView.ReferencedDocument;
            swPart = ( | `Set_Body_for_View_Example_CSharp.md` |
| 435 | `ReferencedDocument` | return_shape_diff | Because section views do not have referenced documents, this method re | Set swDrawModel = swView.ReferencedDocument
    sModelName = swView.Ge | `Get_Document_Referenced_by_Drawing_View_Example_VB.md` |
| 436 | `Refresh3DViews` | precondition_diff | This method requires that the SOLDWORKS MBD add-in be loaded. ([[ISldW | swModelExt.Refresh3DViews(); | `Capture_3DView_Example_CSharp.md` |
| 437 | `ReliefDepth` | precondition_diff | - [[IBaseFlangeFeatureData::UseReliefRatio]] returns false, | Call swBaseFlangeFeat.Initialize(False, False, cba, False, swSheetMeta | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 438 | `ReliefTearType` | other_conflict | The default value of this property is swReliefTearType_e.swReliefTearT | FeatData.ReliefTearType = (int)swReliefTearTypes_e.swReliefTearTypeRip | `Create_Edge_Flange_Example_CSharp.md` |
\| 439 \| `ReliefWidth` \| precondition_diff \| This property is valid when:

- [[IBaseFlangeFeatureData::UseReliefRat | Call swBaseFlangeFeat.Initialize(False, False, cba, False, swSheetMeta | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 440 | `RemoveCommandGroup` | other_conflict | This method removes CommandGroups created using [[ICommandManager::Add | cmdGroup = iCmdMgr.CreateCommandGroup2(mainCmdGroupID, Title, ToolTip, | `Create_Flyouts_in_the_CommandManager_Example_CSharp.md` |
\| 441 \| `RemovePresentationTransform` \| other_conflict \| After calling IComponent2::RemovePresentationTransfrom, the component  \| swComp.RemovePresentationTransform
swComp.PresentationTransform = swMa | `Use_Presentation_Transforms_to_Move_Component_Example_VB.md` |
| 442 | `RenderToFile` | other_conflict | After calling this method, call [[IRayTraceRenderer::CloseRayTraceRend | status = swRayTraceRenderer.CloseFinalRenderWindow | `Include_Note_in_Render_File_Example_VB.md` |
| 443 | `RenderToFile` | other_conflict | After calling this method, call [[IRayTraceRenderer::CloseRayTraceRend | status = swRayTraceRenderer.CloseFinalRenderWindow(); | `Render_Annotations_to_Separate_Image_File_Example_CSharp.md` |
| 444 | `RenderType` | precondition_diff | This property is only available when [[IRayTraceRendererOptions::Conto | Debug.Print("  Render type = " + swRayTraceRenderOptions.RenderType); | `Render_Model_Example_CSharp.md` |
| 445 | `RenderType` | precondition_diff | This property is only available when [[IRayTraceRendererOptions::Conto | Debug.Print("  Render type (0 = cartoon; 1 = contour) = " + swRayTrace | `Update_Graphics_After_Changing_Render_Options_Example_CSharp.md` |
| 446 | `ReplaceFileLocations` | other_conflict | Gets or sets the file locations of existing files that are to be repla | 5. Replaces FileName1.sldprt with check1.sldprt in c:\API\MirrorComps. | `Mirror_Components_II_Example_CSharp.md` |
\| 447 \| `ResetBlockingState` \| precondition_diff \| **NOTE:** You must call this method every time you call IModelDoc2::Se \| If nResponse = vbYes Then
        swModel.ResetBlockingState
    Else
 | `C:\swapi\examples\Set_Blocking_State_Example_VB.md` |
| 448 | `ResolveAllLightWeightComponents` | precondition_diff | The assembly must be open in its own window. Call [[ISldWorks::Activat |             swAssy = (AssemblyDoc)swModel;
            swModelDocExt = | `Resolve_All_Components_Fix_A_Component_Example_CSharp.md` |
| 449 | `ReverseDirection` | precondition_diff | True to reverse the item ordering, false to not; only valid when [[IAu | autoballoonParams.ItemOrder = swBalloonItemNumbers_DoNotChangeItemNumb | `Add_Autoballoon_to_Face_Example_VB.md` |
| 450 | `ReverseRotationDirection` | precondition_diff | This property is valid only if [[IExplodeStep::ExplodeStepType]] is se | explStep.ReverseRotationDirection = Not explStep.ReverseRotationDirect | `Edit_Radial_Explode_Step_Example_VB.md` |
| 451 | `ReverseThickness` | precondition_diff | The setter of this property is valid only if [[IBaseFlangeFeatureData: | featDef.ReverseThickness = False | `Create_Base-Flange_Feature_Using_Gauge_Table_Example_VB.md` |
| 452 | `ReverseTranslationDirection` | precondition_diff | This property is valid only if [[IExplodeStep::ExplodeStepType]] is se | explStep.ReverseTranslationDirection = Not explStep.ReverseTranslation | `Edit_Radial_Explode_Step_Example_VB.md` |
| 453 | `RevolutionVal` | precondition_diff | - swRevolutionsPerUnitLength, then specify this property with the numb | MateData.RevolutionVal = 1; | `Create_Screw_Mate_Example_CSharp.md` |
| 454 | `RotateAboutEachComponentOrigin` | precondition_diff | This property is valid only if [[IExplodeStep::ExplodeStepType]] is se |     explStep.RotateAboutEachComponentOrigin = Not explStep.RotateAbout | `Edit_Radial_Explode_Step_Example_VB.md` |
| 455 | `Rotation` | precondition_diff | - [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToP | swFeatData.FeaturesToPatternType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
| 456 | `Rotation` | precondition_diff | - [[IFillPatternFeatureData::CreateSeedCutType]] is set to one of the  | swFeatData.CreateSeedCutType = 0; | `Create_Fill_Pattern_Example_CSharp.md` |
\| 457 \| `RoundCorners` \| precondition_diff \| This property is valid only if [[ISimpleFilletFeatureData2::CurvatureC \| // 1. Open a model document with a simple fillet feature.
// 2. Select | `Get_Data_for_Simple_Fillet_Example_CSharp.md` |
| 458 | `ScaleDecimal` | other_conflict | Changing this property can cause changes to the graphics of the drawin | bRet = swModel.EditRebuild3: Debug.Assert bRet | `Set_View_Scale_Example_VB.md` |
\| 459 \| `ScaleUniform` \| precondition_diff \| **NOTE:** If uniform scaling is disabled, then use these properties to \|             Debug.Print("   Is uniform = " + swScale.IsUniform);
      | `Get_Data_for_Scale_Feature_Example_CSharp.md` |
| 460 | `ScaleX` | precondition_diff | **NOTE:** To get or set the scaling factor when uniform scaling is ena |             Debug.Print("   Uniform scaling factor = " + swScale.Scale | `Get_Data_for_Scale_Feature_Example_CSharp.md` |
\| 461 \| `ScaleY` \| precondition_diff \| **NOTE:** To get or set the scaling factor when uniform scaling is ena \|             Debug.Print("   X scaling factor = " + swScale.ScaleX);
   | `Get_Data_for_Scale_Feature_Example_CSharp.md` |
| 462 | `SelectByRay` | other_conflict | Defines a cylindrical region of infinite length that begins at pointIn | boolstatus = Part.Extension.SelectByRay(-0.0108900020093756, 0.0655319 | `Add_and_Edit_Distance_Mate_Example_VBNET.md` |
| 463 | `SelectedFaceProperties` | precondition_diff | Specify the reflectivity properties (*Diffuse*, *Specular*, *Shininess | boolstatus = swModel.SelectedFaceProperties(0, 0, 0, 0, 0, 0, 0, True, | `Get_Component_Face_By_Name_Example_VB.md` |
\| 464 \| `SelectedFeatureProperties` \| precondition_diff \| This method requires that the feature to be selected. \| swModel.ClearSelection2 True
    ' Set the property values for the sel | `Create_Thicken_Feature_Example_VB.md` |
| 465 | `SetAutomaticCutList` | precondition_diff | a cut list folder already exists in the part. You must delete the cut  | 2. Inspect the cut list folder. | `Get_Features_of_Multibody_Sheet_Metal_Part_Example_CSharp.md` |
| 466 | `SetBendState` | precondition_diff | This method only works for old-style sheet metal parts or non-sheet me | 1. Open a sheet metal part. | `Flatten_Sheet_Metal_Part_Example_VB.md` |
\| 467 \| `SetBlockingState` \| precondition_diff \| **IMPORTANT:** There must be a corresponding call to IModelDoc2::Reset \|     Else
    ' If use responds no, then set blocking state to
    ' di | `Set_Blocking_State_Example_VB.md` |
| 468 | `SetBoundingBoxDirection1` | precondition_diff | - The bounding box cannot be created because [[ISlicingData::PlaneRefe | boolstatus = sliceData.SetBoundingBoxDirection1(0.1397); | `Slice_a_Model_Example_CSharp.md` |
| 469 | `SetColumnType` | return_shape_diff | This method is consistent with the user interface and should return a  | boolstatus = theTableAnnotation.SetColumnType(theTableAnnotation.Colum | `Insert_Part_Number_Column_in_BOM_Table_Example_VB.md` |
| 470 | `SetCustomCheckResult` | other_conflict | Upper dimension contains the size (number) of failed items ,and the lo | ReDim Preserve FailedItemsArr(1 To 2, 1 To nFailedItemCount) As String | `Custom_Check_Document_Example_VB.md` |
| 471 | `SetDisplayMode3` | other_conflict | Once the drawing view has precision quality, whether you created it th | 1. Changes the display modes of all drawing views to draft quality. | `Change_Display_Mode_to_Draft_Quality_Example_VB.md` |
| 472 | `SetDisplayMode3` | other_conflict | swFACETED_WIREFRAME, swFACETED_HIDDEN_GREY, and swFACETEDHIDDEN | case swFACETED_HIDDEN_GREYED: | `Set_View_Display_Mode_Example_CPlusPlus_COM.md` |
| 473 | `SetDocumentSaveToNames` | other_conflict | To override the paths and filenames set by this method, use [[IPackAnd | status = swPackAndGo.SetSaveToName2(true, myPath); | `Add_and_Remove_Files_from_Pack_and_Go_Example_CSharp.md` |
| 474 | `SetDraftAngle` | precondition_diff | Call [[IBoundaryBossFeatureData::GetCurvesCount]] to get a valid range | if (nbrCurves >= 0) | `Insert_Boundary_Feature_Example_CSharp.md` |
| 475 | `SetDraftAngleReverseDirection` | precondition_diff | Call [[IBoundaryBossFeatureData::GetCurvesCount]] to get a valid range | if (nbrCurves >= 0) | `Insert_Boundary_Feature_Example_CSharp.md` |
| 476 | `SetFaceUserId` | precondition_diff | See [Accessing Selections that Define Features](<../../docs/Programmin | swMacroFeatData = (MacroFeatureData)((Feature)feature).GetDefinition() | `Create_Multibody_Macro_Feature_Example_CSharp.md` |
| 477 | `SetFaces` | other_conflict | See [Accessing Selections that Define Features](<../../docs/Programmin | boolstatus = swWeldBead.SetFaces(swWeldBeadOtherSide, (f1), (f2)) | `Change_Weld_Bead_Faces_Example_VB.md` |
\| 478 \| `SetFrameToleranceType` \| precondition_diff \| TolType may be one of only swGtolGeomCharSymbol_e.:

- swGcsANG

- swG | boolstatus = swGtolFrame.SetFrameToleranceType((int)swGtolGeomCharSymb | `Get_Gtol_Frame_Information_Example_CSharp.md` |
| 479 | `SetFrameToleranceType` | precondition_diff | TolType may be one of only swGtolGeomCharSymbol_e.:

- swGcsANG

- swG | boolstatus = swGtolFrame.SetFrameToleranceType(swGtolGeomCharSymbol_e. | `Get_Gtol_Frame_Information_Example_VBNET.md` |
| 480 | `SetFrameValues2` | precondition_diff | This method is valid only if this Gtol was created in a version of SOL | swGtol = (Gtol)swModel.InsertGtol(); | `Insert_GTol_Example_CSharp.md` |
| 481 | `SetFromPointMembers` | other_conflict | Array of [[IStructureSystemMemberFeatureData]]s | Members[0] = swSelMgr.GetSelectedObject6(2, 0); | `Create_Secondary_SSMembers_Example_CSharp.md` |
| 482 | `SetOverrideDefaultParameter2` | precondition_diff | This property is only valid for multibody sheet metal parts created in | Part = swApp.NewDocument("C:\ProgramData\SolidWorks\SOLIDWORKS 2022\te | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 483 | `SetOverrideDefaultParameter2` | return_shape_diff | This property is only valid for multibody sheet metal parts created in | Debug.Print("Result code for override of AutoRelief as defined by swSh | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 484 | `SetPaperSize` | precondition_diff | This method only supports importing to a drawing; it does not support  | bRet = importData.SetPaperSize("", (int)swDwgPaperSizes_e.swDwgPaperAs | `Insert_DXF_File_and_Add_Dimensions_Example_CSharp.md` |
| 485 | `SetProperties2` | precondition_diff | The **Tools > Options > Document Properties > Drawing Sheets > Use cus | swSheet.SetProperties2 swDwgPaperSizes_e.swDwgPapersUserDefined, swDwg | `Get_and_Set_Whether_to_Hide_Cutting_Line_Shoulders_Example_VB.md` |
| 486 | `SetReferences` | other_conflict | Some SolidWorks properties and methods, such as this method, have an i |     ' Set the references for positioning the library feature on the pa | `Create_Library_Feature_With_References_Example_VB.md` |
\| 487 \| `SetRegionParameterAtIndex` \| precondition_diff \| Must specify a value greater than the previous region's revolution val \| //Revolution must be smaller than previous region's
//revolution and l | `Create_and_Modify_Variable-pitch_Helix_Example_CSharp.md` |
| 488 | `SetSheetScale` | precondition_diff | This method only supports importing to a drawing; it does not support  | importData.set_ImportMethod("", (int)swImportDxfDwg_ImportMethod_e.swI | `Insert_DXF_File_and_Add_Dimensions_Example_CSharp.md` |
| 489 | `SetSheetScale` | precondition_diff | This method only supports importing to a drawing; it does not support  | importData.ImportMethod("") = swImportDxfDwg_ImportMethod_e.swImportDx | `Insert_DXF_File_and_Add_Dimension_Example_VB.md` |
| 490 | `SetSheetScale` | precondition_diff | This method only supports importing to a drawing; it does not support  | importData.ImportMethod("") = swImportDxfDwg_ImportMethod_e.swImportDx | `Insert_DXF_File_and_Add_Dimensions_Example_VBNET.md` |
| 491 | `SetSmartComponentData` | other_conflict | Create two boolean arrays whose elements map one-to-one with the eleme | componentsSelected(j - 1) = True | `Activate_Smart_Features_in_an_Assembly_Example_VB.md` |
| 492 | `SetStringValue2` | other_conflict | Sets the double or integer value of a named configuration option param |     bRet = swParamName.SetStringValue2(AttName & " - " & AttLenDimName | `Create_Attribute_Example_VB.md` |
| 493 | `SetSuppression2` | return_shape_diff | Status as defined in [[swSuppressionError_e]] |                 Debug.Assert((int)swComponentResolveStatus_e.swResolve | `Set_Fully_Resolved_Assembly_to_Lightweight_Example_CSharp.md` |
| 494 | `SetSuppression2` | other_conflict | System.int SetSuppression2( System.int State ) | hres = swComponent->SetSuppression2(swComponentSuppressed, | `Access_Assembly_Example_CPlusPlus_COM.md` |
| 495 | `SetSystemValue3` | unit_diff | Sets the value of this dimension in system units (meters) in the speci | ' Change D3 of LocalCirPattern1 from 360 degrees to 270 degrees (4.72  | `Change_Dimension_Example_VB.md` |
| 496 | `SetTemplateName` | precondition_diff | a custom template name, before calling this method, call [[ISheet::Set | swSheet.SetProperties2 swDwgPaperSizes_e.swDwgPapersUserDefined, swDwg | `Get_and_Set_Whether_to_Hide_Cutting_Line_Shoulders_Example_VB.md` |
| 497 | `SetTextAtIndex` | precondition_diff | After completing any note changes, you must perform an [[IModelDoc2::E | ' 4. Examine the title block again to verify step 3. | `Change_Note_Text_Example_VB.md` |
| 498 | `SetUnits` | other_conflict | If the UseDoc argument is true, then the display dimension unit inform | hres = pModelDoc->SetUnits(swINCHES, swFRACTION, denom, unitArray[3],  | `Get_and_Set_Units_Example_CPlusPlus_COM.md` |
| 499 | `SetUserPreferenceDouble` | other_conflict | This method is equivalent to interactively setting document properties | boolstatus = ModelDocExtension.SetUserPreferenceDouble((int)swUserPref | `Get_and_Set_User_Preferences_Example_CSharp.md` |
| 500 | `SetUserPreferenceInteger` | other_conflict | This method is equivalent to interactively setting document properties | boolstatus = swModel.Extension.SetUserPreferenceInteger((int)swUserPre | `Create_Drawing_Sheet_Zones_Example_CSharp.md` |
| 501 | `SetUserPreferenceString` | other_conflict | This method is equivalent to interactively setting document properties | boolstatus = ModelDocExtension.SetUserPreferenceString((int)swUserPref | `Get_and_Set_User_Preferences_Example_CSharp.md` |
| 502 | `SetupSheet6` | other_conflict | To modify the setups of multiple drawing sheets with just one call to  | swDrawing.SetSheetsSelected(sheetNameArray); | `Modify_Multiple_Drawing_Sheets_Setups_Example_CSharp.md` |
| 503 | `SetupSheet6` | unit_diff | Multiplying ZoneRow by ZoneCol equals the total number of zones in the | 0.2794, 0.2159, "Default", False, 0.5, 0.5, 0.5, 0.5, 3, 3) | `Create_Drawing_Sheet_Zones_Example_VB.md` |
| 504 | `ShowChildComponentsInBOM` | precondition_diff | This property applies only to assembly configurations. SOLIDWORKS alwa | Open a part that contains one or more configurations. | `Change_Configuration_Properties_Example_VB.md` |
| 505 | `ShowChildComponentsInBOM` | precondition_diff | This property applies only to assembly configurations. SOLIDWORKS alwa | Open a part or assembly. | `Traverse_Hierarchy_of_Configurations_Example_VB.md` |
| 506 | `ShowConfiguration2` | precondition_diff | If you made changes to the model and the configuration to which you ar | status = swDimensionTolerance.SetValues2(0.01, 0.015, (int)swSetValueI | `Change_Dimension_Tolerance_in_Configuration_Example_CSharp.md` |
| 507 | `ShowParenthesis` | other_conflict | This property supports bilateral, symmetric, or fit-with-tolerance typ | Debug.Print " Show parenthesis: " & swDisplayDimension.ShowParenthesis | `Get_Display_Dimension_Properties_Example_VB.md` |
| 508 | `Simplify` | precondition_diff | The sketch must be in edit mode and a spline must be preselected. | skSpline = skSegment | `Create_Equation-driven_Curve_Example_VBNET.md` |
| 509 | `SortCutList` | precondition_diff | If you set IgnoreInvalidFacesOrFeatures to false and there are invalid | 3. Sorts the cut list. | `Get_Features_of_Multibody_Sheet_Metal_Part_Example_VB.md` |
| 510 | `Spacing` | precondition_diff | This property is only available for distance and linkage distance chai | swChainPatternFeatureData.Spacing = 0.078; | `Create_and_Modify_Distance_Chain_Pattern_Feature_Example_CSharp.md` |
\| 511 \| `Spacing2` \| precondition_diff \| This property is only available when:

- [[ICircularPatternFeatureData | if (swCircularPatternFeatureData.Direction2 == true)
            {
    | `Create_Bidirectional_Circular_Pattern_Feature_Example_CSharp.md` |
| 512 | `SpecifyMaterial` | precondition_diff | Set to false to modify elastic properties: | Debug.Print "  Use impact force:"
Debug.Print "    Exponent of exponen | `Create_3DContact_Feature_Example_VB.md` |
| 513 | `SuppressNewComponentModels` | precondition_diff | This property applies only to assembly configurations. SOLIDWORKS alwa | 1. Open a part that contains one or more configurations. | `Change_Configuration_Properties_Example_VB.md` |
\| 514 \| `SuspendSelectionList` \| return_shape_diff \| 0 if the suspended list is empty, 1 if not \| ret = selMgr.SuspendSelectionList();
                Debug.Print("The  | `Add_Objects_to_Selection_List_Example_CSharp.md` |
| 515 | `SweepPlanarLoop` | precondition_diff | This method requires simplification of the imported body. | ' Preconditions:
' 1. Open a model document.
' 2. Select a planar face | `Sweep_Planar_Loop_Along_Vector_Example_VB.md` |
| 516 | `SynchronizeFlexibleComponents` | precondition_diff | If this property is set to true, then when you move components in the  | swLocalLinearPatternFD = (LocalLinearPatternFeatureData)swFeatureManag | `Create_Local_Linear_Pattern_Example_CSharp.md` |
\| 517 \| `TangentToBend` \| precondition_diff \| - [[ISMCornerReliefData::ReliefType]] is set to [[swCornerReliefType_e \| cornerItr.TangentToBend = True
            cornerItr.ReliefType = swCo | `Create_SM_Corner_Relief_Feature_Example_VBNET.md` |
| 518 | `TapDrillDepth` | precondition_diff | This property is relevant only for:

- swTapBlind

- swTapBlindCounter | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 519 | `TapDrillDiameter` | precondition_diff | This property is relevant only for:

- swTapBlind

- swTapBlindCounter | swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounte | `Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md` |
| 520 | `ThemeName` | other_conflict | You can also get or set the SOLIDWORKS MBD 3D PDF path for a theme usi | swMBDPdfData.ThemeName = "C:\\Program Files\\SolidWorks Corp\\SOLIDWOR | `Attach_Files_to_MBD_3D_PDF_Example_CSharp.md` |
| 521 | `Thickness` | precondition_diff | The setter of this property is valid only if [[IBaseFlangeFeatureData: | ' If above override value is true, then use following properties to se | `Create_Base-Flange_Feature_Using_Gauge_Table_Example_VB.md` |
| 522 | `ThicknessRatioForOffset` | precondition_diff | [[IEndCapFeatureData::UseThicknessRatioForOffset]] must be set to true | Set myFeature = Part.FeatureManager.InsertEndCapFeature3(0.005, False, | `Insert_Weldment_End_Cap_Example_VB.md` |
| 523 | `ThirdColor` | other_conflict | Use [[ISectionViewData::ShowSectionCap]] to display the caps of sectio | data.KeepCapColor = true; | `Create_Section_View_in_Model_Example_CSharp.md` |
\| 524 \| `ToScale` \| precondition_diff \| This property is valid only if [[IPrintSpecification::ScaleMethod]] is \| printSpec.FromScale = 1.5;
            printSpec.ToScale = 0.5;
       | `Print_Drawing_as_High_Quality_Example_CSharp.md` |
| 525 | `TolerancePerUnitType` | precondition_diff | This property is valid only if [[IPMIFrameData::GeometricCharacteristi |                                             for (k = 0; k <= swPMIFram | `Get_PMI_Data_Example_CSharp.md` |
| 526 | `TolerancePerUnitValue1` | precondition_diff | This property is valid only if [[IPMIFrameData::GeometricCharacteristi |                                             Debug.Print("      Toleran | `Get_PMI_Data_Example_CSharp.md` |
\| 527 \| `TolerancePerUnitValue2` \| precondition_diff \| This property is valid only if:

- [[IPMIFrameData::GeometricCharacter |                                             Debug.Print("      Toleran | `Get_PMI_Data_Example_CSharp.md` |
| 528 | `TotalInstances2` | precondition_diff | This property is only available when: - [[ICircularPatternFeatureData: |             if (swCircularPatternFeatureData.Direction2 == true)
      | `Create_Bidirectional_Circular_Pattern_Feature_Example_CSharp.md` |
| 529 | `Type2` | return_shape_diff | After using this property, use [[IModelDoc2::GraphicsRedraw2]] to redr | Debug.Print("Dimension type as defined in swDimensionType_e: " & swDis | `Get_Chamfer_Display_Dimension_Example_VBNET.md` |
\| 530 \| `Update` \| other_conflict \| To change the length of a handle, use [[IDragArrowManipulator::Length] \| swTmpManipulator.Origin = swMathPoint;
            swTmpManipulator.Up | `Create_Drag_Arrow_Manipulator_Example_CSharp.md` |
| 531 | `UpperText` | precondition_diff | You can only get or set the upper text in a BOM autoballoon using [[IN | swStackedBalloons.UpperText = """" | `Add_Balloon_to_Stacked_Balloon_Example_VB.md` |
| 532 | `UpperText` | other_conflict | You can only get or set the upper text in a BOM autoballoon using [[IN | Dim swStackedBalloons As SldWorks.StackedBalloonOptions | `Add_Balloon_to_Stacked_Balloon_Example_VB.md` |
| 533 | `UpperTextContent` | other_conflict | To get or set document default values for UpperTextContent... | StackedBalloonOptions swStackedBalloons = default(StackedBalloonOption | `Add_Balloon_to_Stacked_Balloon_Example_CSharp.md` |
| 534 | `UseAngleDimForProfile` | precondition_diff | This property is valid only if [[ISMGussetFeatureData::ProfileDimensio | swFeatData.ProfileDimensionScheme = (int)swSheetMetalGussetProfileDimT | `Create_Sheet_Metal_Gusset_Example_CSharp.md` |
| 535 | `UseDefaultBendAllowance` | other_conflict | Whether to use the default bend allowance is set during the initializa | 'UseDefaultBendAllowance=False, | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 536 | `UseDefaultBendAllowance` | precondition_diff | If this property is false, then use [[IBaseFlangeFeatureData::GetCusto | Call swBaseFlangeFeat.Initialize(False, False, cba, False, swSheetMeta | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 537 | `UseDefaultBendRelief` | other_conflict | Whether to use the default bend relief was set during the [[initializa | 'UseDefaultBendRelief=False, | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 538 | `UseDefaultBendRelief` | precondition_diff | If this property is false, then you can get the type of bend relief an | Call swBaseFlangeFeat.Initialize(False, False, cba, False, swSheetMeta | `Create_Base_Flange_Feature_Example_VBNET.md` |
| 539 | `ViewCollapseAssembly` | precondition_diff | Collapses the selected exploded view on the Configuration tab of the F | hres = swAssemblyDoc->ViewCollapseAssembly(); | `Access_Assembly_Example_CPlusPlus_COM.md` |
\| 540 \| `ViewCollapseAssembly` \| precondition_diff \| Use this method with [[IAssemblyDoc::ViewExplodeAssembly]] to toggle t \| hres = swAssemblyDoc->AutoExplode(&retVal);
hres = swAssemblyDoc->View | `Access_Assembly_Example_CPlusPlus_COM.md` |
| 541 | `WeldmentProfilePath` | other_conflict | Weldment profiles are located in *install_dir***/lang/***lang***/weldm | swWeldFeatData.WeldmentProfilePath = "C:\Program Files\SolidWorks Corp | `Set_Profile_for_Structural_Member_Example_VB.md` |
| 542 | `component` | other_conflict | The associated [[IComponent2]] object should have the same properties  | ' Returns empty strings for root component | `C:\swapi\examples\Get_Components_Properties_in_Drawing_View_Example_VB.md` |
| 543 | `origin` | precondition_diff | Before calling this property to change the origin setting, set [[IDrag | swDrag.origin = swPickPt | `Create_Drag_Arrow_Manipulator_Example_VB.md` |
| 544 | `pointArray` | return_shape_diff | The ArrayDataIn argument is an array of doubles containing 3 * points: | For i = 0 To nbrPoints - 1 | `Insert_Free_Point_Curve_Feature_Example_VB.md` |

## 三、★ `example_more_specific`（3709 条）—— **不是矛盾，但是只有示例才有的信息**

> **这一类比冲突多近一个数量级**，是本次扫描**最大的产出**：
> 成员页 `Remarks` 没写、而示例里明确写了的东西。

| # | 成员 | 是什么 | 示例里的逐字 |
|---|---|---|---|
| 1 | `Accuracy` | 示例给出具体枚举成员 swLow；页面 Returns 只写见 sw3DPDFAccuracy_e。 | swMBDPdfData.Accuracy = (int)sw3DPDFAccuracy_e.swLow; |
| 2 | `AccuracyFactor` | 示例表明须先 AccessSelections 才读得到该值；成员页无此前置说明。 | swSurfaceFlattenFeatureData.AccessSelections(swModel, null); |
| 3 | `AccuracyFactor` | 示例建特征时实参取 8，落在页面给的 1..10 区间内（页面不给具体值）。 | swFeature = (Feature)swFeatureManager.InsertFlattenSurface2(8, true); |
| 4 | `ActionLocation` | 示例赋的是一个 FACE，而 Returns 只列 Vertex／圆形边／直线边。 | swForceFeat.ActionLocation = swSelMgr.GetSelectedObject6(1, -1) |
| 5 | `ActionType` | 示例给出具体枚举成员；页面 Returns 只指向 swSimulationForceActionType_e。 | swForceFeat.ActionType = swSimulationForceAction_ActionOnly |
| 6 | `ActionType` | 示例给出该数据对象的来路：MotionStudy1.CreateDefinition。 | Set swForceFeat = swMotionStudy1.CreateDefinition(swFmAEMLinearForce) |
| 7 | `ActivateControlTab` | Name 用与 AddControl 相同的常量，激活后用 IsControlTabActive 回验。 | status = swModViewMgr.ActivateControlTab(calTabName1) |
| 8 | `ActivateControlTab` | 示例走 AddControl 而非 See Also 列出的 AddControl3，先建页签再激活。 | swModViewMgr.AddControl(calTabName1, |
| 9 | `ActivateDoc` | 示例用 NewPart 造件后只传标题 Part1，不带文件扩展名 | Part = swApp.ActivateDoc("Part1") |
| 10 | `ActivateDoc` | 同一示例另一处 ActivateDoc2 传 True 作 silent，而 ActivateDoc 签名无此形参 | Part = swApp.ActivateDoc2("Part1",True,errors) |
| 11 | `ActivateDoc2` | Errors 是 out 形参，VBA 侧须先 Dim 声明 Long 变量再传 | Dim longstatus As Long, longwarnings As Long |
| 12 | `ActivateDoc2` | 四份示例全部丢弃返回值，改读 swApp.ActiveDoc 取激活后的文档 | swModel = (ModelDoc2)swApp.ActiveDoc; |
| 13 | `ActivateDoc2` | Name 传不带扩展名的标题 box，正是 Remarks 点名的歧义场景 | swApp.ActivateDoc2("box", false, ref longstatus); |
| 14 | `ActivateDoc3` | C# 侧须把返回值强转 AssemblyDoc 才能当装配体用，Returns 只写 Model document | swAssembly = (AssemblyDoc)swApp.ActivateDoc3(AssemblyTitle, true, 0, longstatus) |
| 15 | `ActivateDoc3` | Option 实参写法不统一：本份用枚举名 swUserDecision，另三份用字面量 0 | Set swModel = swApp.ActivateDoc3(AssemblyTitle, True, swUserDecision, errors) |
| 16 | `ActivateGroundPlane` | 选中地面的 SelectByID2 类型串是 MAGNETICGROUNDPLANE，不是 PLANE | boolstatus = Part.Extension.SelectByID2("Ground Plane1", "MAGNETICGROUNDPLANE",  |
| 17 | `ActivateGroundPlane` | 激活后用 GetActiveGroundPlane(swAllConfiguration, Null) 回读验证 | groundPlanes = Part.GetActiveGroundPlane(swAllConfiguration, Null) |
| 18 | `ActivateGroundPlane` | Config_opt 取 swThisConfiguration 时 Config_names 显式传 Null | boolstatus = Part.ActivateGroundPlane(swThisConfiguration, Null) |
| 19 | `ActivateModelTab` | VBA 以不带括号的形式调用 ActivateModelTab | status = swModViewMgr.ActivateModelTab |
| 20 | `ActivateModelTab` | 示例给出完整调用序：AddControl → ActivateControlTab → IsModelTabActive → ActivateModelTab | status = swModViewMgr.ActivateControlTab(calTabName1) |
| 21 | `ActivateMotionStudy` | 算例名不存在时返回 False 而不抛错，示例原地标注 Should return False | boolstatus = swMotionMgr.ActivateMotionStudy("Motion Study 4") ' Should return F |
| 22 | `ActivateMotionStudy` | 前置给出 MotionManager 页签的具体菜单路径 View > MotionManager | ' 2. If the MotionManager tab is not visible, click View > MotionManager. |
| 23 | `ActivateSelectedFeature` | Activate_Feature_Example_VB 给出与 Remarks 一致的前置：先选中特征再调用 | ' 2. Select the feature for which you want to show |
| 24 | `ActivateSheet` | 图纸本身就在 GetFirstView 链上，ActivateSheet 的入参直接取该链的 GetName2。 | bRet = swDraw.ActivateSheet(swView.GetName2) |
| 25 | `ActivateView` | 示例把 false 当常规分支：断言该视图名等于图纸名，再改调 ActivateSheet。 | Debug.Assert swSheet.GetName = swView.GetName2 |
| 26 | `ActiveCommandTab` | 示例给出前置：须先打开一个零件文档，属性经 swModelDoc.Extension 取。 | Preconditions: Open a part. |
| 27 | `ActiveCommandTab` | 写入用的是页签名字符串；读回时当前页签预期为 "Features"。 | swModelDocExt.ActiveCommandTab = "Sketch"; |
| 28 | `ActiveCommandTabIndex` | 同一索引还被当作 CommandTabVisible 的入参，示例指明 Mold Tools 即索引 5。 | //      * Mold Tools tab (tab index 5) is visible. |
| 29 | `ActiveCommandTabIndex` | 改完 ActiveCommandTab 后重读该索引，用来回读设置是否联动生效。 | activeTabIndex = swModelDocExt.ActiveCommandTabIndex; |
| 30 | `ActiveConfiguration` | 示例把它当作取得爆炸步 Configuration 对象的入口，而非 Remarks 说的遍历起点。 | Set config = swModel.ConfigurationManager.ActiveConfiguration |
| 31 | `ActiveConfiguration` | 示例中它只是引导取值，随即在 For 循环里被 GetConfigurationByName 覆盖。 | Set swConf = swConfMgr.ActiveConfiguration |
| 32 | `ActiveDoc` | 示例显示 OpenDoc6 之后仍须先 ActivateDoc2，ActiveDoc 才返回想要的那份文档。 | swApp.ActivateDoc2("box", false, ref longstatus); |
| 33 | `ActiveDoc` | 示例直接强制转型、不判空，与 Remarks 所述 Nothing/null 返回路径未被示例覆盖。 | swModel = (ModelDoc2)swApp.ActiveDoc; |
| 34 | `ActiveDrawingView` | 示例前置要求先点选一个视图使其成为活动视图，否则取值为 NULL 不可直接取名。 | 2. Click a drawing view to activate it. |
| 35 | `ActiveDrawingView` | 示例演示读取链路：ActivateView 之后立刻回读本属性取得 View 对象。 | swView = (View)swDrawingDoc.ActiveDrawingView; |
| 36 | `ActiveFeatureManagerTabIndex` | 示例给出前置：写该索引前须先把 Manager Pane 设为可见（HideFeatureManager 传 false）；成员页只说读写索引，未提可见性。 | swModelDocExtension.HideFeatureManager(false); |
| 37 | `ActiveFeatureManagerTabIndex` | 示例说明合法索引范围来自 GetFeatureManagerTabs() 返回数组的长度，按 0..n-1 遍历写入；成员页未给取值范围。 | tabs = (object[])swModelViewManager.GetFeatureManagerTabs(); |
| 38 | `ActiveSketch` | 示例显式判空并给出提示，说明没有活动草图时该属性取到的是 Nothing（VB 里显示为 Is Nothing）。 | swApp.SendMsgToUser2("No active sketch; thus, a sketch could not be selected.",  |
| 39 | `ActiveSketch` | 示例在 InsertSketch 收尾之前取该属性（紧跟建线之后），说明须在草图仍处编辑态时取；成员页未提时机。 | swSketch = (Sketch)swSketchManager.ActiveSketch; |
| 40 | `ActiveView` | 示例把返回的 object 显式转成 ModelView 才使用，说明 Signature 里的 System.object 需落类型；页面未给具体类型。 | swModelView = (ModelView)swModel.ActiveView; |
| 41 | `ActiveView` | 示例取到后直接调 GraphicsRedraw，且 rect 声明为 int[] 传 null，说明该属性取回即可驱动图形重绘。 | swModelView.GraphicsRedraw(rect); |
| 42 | `Add3` | 示例的 manager 取自选中的焊件 Feature，而非从模型文档取，比页面的「configuration or model document」更细一层。 | Set swCustPropMgr = swFeat.CustomPropertyManager |
| 43 | `Add3` | 示例给出第 4 个实参的一个具体枚举成员 swCustomPropertyDeleteAndAdd；页面只指向 swCustomPropertyAddOptio | nRetVal = swCustPropMgr.Add3("Date added", swCustomInfoType_e.swCustomInfoDate,  |
| 44 | `AddAlongXDimension` | 示例给出被标注对象：调用前先用 SelectByID2 选两个 SKETCHPOINT，第二个 append=true；Remarks 未说选什么。 | boolstatus = Part.Extension.SelectByID2("Point4", "SKETCHPOINT", 0.0844553769717 |
| 45 | `AddAlongXDimension` | 示例表明三个坐标实参按米传（0.05 即 50 mm，与所选两点 x 差 0.08445537697179 对应 84.46 mm），而参数表未标单位。 | myDisplayDim = (DisplayDimension)Part.SketchManager.AddAlongXDimension(0.05, -0. |
| 46 | `AddAlongYDimension` | 示例给出被标注对象：调用前先用 SelectByID2 选两个 SKETCHPOINT，第二个 append=true；Remarks 未说选什么。 | boolstatus = Part.Extension.SelectByID2("Point4", "SKETCHPOINT", 0.0844553769717 |
| 47 | `AddAlongYDimension` | 示例表明三个坐标实参按米传，且首参即维度起点 x：(-0.1, 0, 0.01111142101618) 与注释里 y 向 63.24 mm 的起点一致；参数表 | myDisplayDim = (DisplayDimension)Part.SketchManager.AddAlongYDimension(-0.1, 0,  |
| 48 | `AddAlongZDimension` | 调用会弹出 Modify dimension 对话框，示例要求人工点绿勾；成员页只字未提 | 3. Click the green check mark in the Modify dimension dialog |
| 49 | `AddAlongZDimension` | 须先选中两个 SKETCHPOINT，第二次 SelectByID2 必须 Append=True | boolstatus = Part.Extension.SelectByID2("Point4", "SKETCHPOINT", 0.0844553769717 |
| 50 | `AddAngularRunningDim` | 基准实体是按面上的点坐标选的（空名字 + EDGE + xyz），Remarks 未说怎么选 | boolstatus = Part.Extension.SelectByID2("", "EDGE", 0.163726736787323, 0.1991150 |
| 51 | `AddAngularRunningDim` | 返回的数组被丢弃，另按尺寸名重选后才拿到 IDisplayDimension | boolstatus = Part.Extension.SelectByID2("D2@Sketch31@foodprocessor.SLDDRW", "DIM |
| 52 | `AddCallback` | 注册前必须先调 SetAddinCallbackInfo 把宿主与 cookie 交给 SolidWorks | iSwApp.SetAddinCallbackInfo(0, this, addinID); |
| 53 | `AddCallback` | 回调须为公有方法，dsp 需标注 IDispatch，并对该 IDispatch 做引用计数释放 | IntPtr pCallbackData = Marshal.GetIDispatchForObject(callbackdata); |
| 54 | `AddCommandItem` | 8 个实参的实际取值范式：Position 用 -1，ImageListIndex 用 0..4，EnableMethod 给方法名 | cmdIndex0 = cmdGroup.AddCommandItem("WinFromInTaskPane", -1, "Add Windows Form I |
| 55 | `AddCommandItem` | 加完命令项后还须置 HasToolbar/HasMenu 再 Activate，成员页未写 | cmdGroup.HasToolbar = true; |
\| 56 \| `AddCommandItem2` \| MenuTBOption 按位或传 swMenuItem\|swToolbarItem；成员页只说见枚举，未说是位掩码 \| int menuToolbarOption = (int)(swCommandItemType_e.swMenuItem \| swCommandItemType \|
| 57 | `AddCommandItem2` | EnableMethod 传空串表示不启用；成员页只写 Optional function | cmdIndex0 = cmdGroup.AddCommandItem2("CreateCube", -1, "Create a cube", "Create  |
| 58 | `AddCommandItem2` | 返回的索引须再经 get_CommandID 换成命令 ID 才能喂给标签框 | cmdIDs[0] = cmdGroup.get_CommandID(cmdIndex0); |
| 59 | `AddCommandTab` | 须按文档类型逐个建标签，一个类型调一次 | int[] docTypes = { (int)swDocumentTypes_e.swDocASSEMBLY, (int)swDocumentTypes_e. |
| 60 | `AddCommandTab` | 返回值在 .NET 里要显式转成 ICommandTab 才能用 | cmdTab = (ICommandTab)iCmdMgr.AddCommandTab(type, Title); |
| 61 | `AddCommandTabBox` | 「必须先加按钮」的具体动作就是紧接着调 AddCommands | bResult = cmdBox.AddCommands(cmdIDs, TextType); |
| 62 | `AddCommandTabBox` | 喂进去的必须是 AddCommandItem2 返回索引换来的命令 ID，不是 UserID | cmdIDs[0] = cmdGroup.get_CommandID(cmdIndex0); |
| 63 | `AddCommands` | Remarks 写 CommandID 或 ToolbarId 二选一；示例把两者混装进同一个 cmdIDs 数组（前两项 CommandID、第三项 Tool | cmdIDs[2] = cmdGroup.ToolbarId; |
| 64 | `AddCommands` | 给出可跑的调用序：CreateCommandGroup→AddCommandItem2→HasToolbar/HasMenu→Activate→GetComma | bResult = cmdBox.AddCommands(cmdIDs, TextType); |
| 65 | `AddComment` | 要拿到 CommentFolder 必须先遍历设计树、匹配 GetTypeName() 为 CommentsFolder 的特征再 GetSpecificFea | swCommentFolder = (CommentFolder)swFeat.GetSpecificFeature2(); |
| 66 | `AddComment` | 示例补充了可见性时序：加批注前 Comments folder 在设计树里不显示，UpdateFeatureTree 之后才显示，需按 F5 复核。 | // so that Comments folder is shown |
| 67 | `AddComponent` | X/Y/Z 实为米制数值（6.253e-3 约 6.25 mm）；成员页 Parameters 只写 X coordinate，未给单位。 | status = swAssembly.AddComponent("C:\temp\RevolveComponent.SLDPRT", 6.2531365765 |
| 68 | `AddComponent` | 返回值按 Boolean 接收，且同一零件连调三次插入三个实例。 | Dim status As Boolean |
| 69 | `AddComponent4` | 示例先用 OpenDoc6 把零件载入内存再调用，印证 Remarks 的必须已载入这条前置不是空话。 | swApp->OpenDoc6(sCompName, |
| 70 | `AddComponent4` | X/Y/Z 全传 -1 作哨兵；示例自己说该方法只适合粗定位。 | sDefaultConfiguration, -1, -1, -1, &swComponent); |
| 71 | `AddComponent4` | Remarks 说精确定位用 IComponent2::Transform2；示例改用选两个基准面 + AddMate3 定位，全程不调 Transform2。 | swAssy->AddMate3(swMateCOINCIDENT, |
| 72 | `AddComponent5` | 示例把 CompName 传成裸文件名 camtest.sldprt 而非全路径，同时另用 OpenDoc6 按全路径载入满足前置。 | strCompModelname = "camtest.sldprt" |
| 73 | `AddComponent5` | X/Y/Z 实为米制数值（0.1196 约 120 mm）；成员页只写 coordinate of the component center，未给单位。 | swInsertedComponent = swAssembly.AddComponent5("C:\\Users\\Public\\Documents\\SO |
| 74 | `AddComponent5` | Remarks 指定用 IComponent2::Transform2 精确定位；示例改用配合定位，全程不调 Transform2。 | Set matefeature = swAssy.AddMate5(swMateCOINCIDENT, swMateAlignALIGNED, False, 0 |
| 75 | `AddComponents3` | 示例给出 16 个元素的具体排布：0-8 旋转、9-11 平移、12 缩放、末三个不用；成员页只说 16 doubles 并转引 IMathTransform。 | // The last three elements in the transformation matrix are unused |
| 76 | `AddComponents3` | Remarks 的矩阵为 null 这条，示例落成一行被注释掉的 Nothing，并说明同样得到零旋转零平移。 | //vcompXforms = Nothing |
| 77 | `AddConcentricMateWithTolerance` | ErrorStatus 等于 1 即成功（swAddMateError_NoError）；成员页只说见 swAddMateError_e，未给成功值。 | if (errors == 1) |
| 78 | `AddConcentricMateWithTolerance` | 选两个实体用 SelectByRay，Append=true、Mark=1；成员页只说 select the two entities，未说怎么选、要用什么 m | SelectByRay(-0.0362917984178921, -0.0292363280984205, 0.194521666713399, -0.4000 |
| 79 | `AddConcentricMateWithTolerance` | 调用前要先清选区、移动组件制造错位、再重选两个面；成员页没写这套时序，而错位正是本方法的前提。 | //Move a component in order to add another mate |
| 80 | `AddConcentricMateWithTolerance` | Remarks 要求父标准同心配合「必须已存在」；示例是在同一步流程里先用 AddMate5 现建的。 | swMate = (Mate2)swAssembly.AddMate5((int)swMateType_e.swMateCONCENTRIC, |
| 81 | `AddConfiguration` | 同名（含派生）配置已存在时返回 Nothing/null；页的 Returns 只说「新建的配置」。 | // Nohting or null if the new configuration already exists. |
| 82 | `AddConfiguration2` | 非派生配置把 ParentConfigName 传空串 ""，只有派生配置才传父名；页只写 Name of parent configuration。 | ConfigMgr.AddConfiguration2 "Config1", "Config1 comment", "alternateName", 1, "" |
| 83 | `AddConfiguration3` | Options 具体用 DoDisolveInBOM + DontShowPartsInBOM；该页无 Remarks，一个具体选项都没列。 | swConfig = (Configuration)swModel.AddConfiguration3("Config2", "", "", (int)swCo |
| 84 | `AddContextMenuFlyout` | 该 flyout 组须先由 CommandManager.CreateFlyoutGroup2 建出，并在同一次调用里带上图标与回调；成员页完全没提这一步。 | flyoutGroup = iCmdMgr.CreateFlyoutGroup2(flyoutGroupID, "Dynamic Flyout", "Dynam |
| 85 | `AddContextMenuFlyout` | 给出文档类型与选择类型的具体配对（零件 + 面），页只说按两个枚举传。 | bResult = flyoutGroup.AddContextMenuFlyout((int)swDocumentTypes_e.swDocPART, (in |
| 86 | `AddControl` | 返回值赋给调用方自己声明的 ActiveX 控件接口变量（页的 Returns 只说「指针」），且 BstrLicKey 实传空串而非 NULL。 | Set calCtrl1 = swModViewMgr.AddControl(calTabName1, "activex_control_CLSID_or_Pr |
| 87 | `AddControl` | 须先打开零件文档、再从 ModelDoc2 取 ModelViewManager 才能建标签页，成员页未提这一前置。 | swModViewMgr = swModel.ModelViewManager; |
| 88 | `AddCornerReliefType` | 示例在按 Mark=0 SelectByID2 选完钣金体后，下一句就是 ClearSelection2 —— 体选区在调用本方法前已被丢弃 | swModel.ClearSelection2 True |
| 89 | `AddCornerReliefType` | 页面 Length2/Length3 未写单位；示例传 0.0007366 / 0.00018415，说明是米制量级 | myReliefType = swModel.FeatureManager.AddCornerReliefType(-1, swCornerSquareReli |
| 90 | `AddCornerReliefType` | 示例给出两种 ReliefType 的完整实参组合：方relief 用 AddFilletedCorners=True 配 Length3 圆角半径 | myReliefType = swModel.FeatureManager.AddCornerReliefType(-1, swCornerObroundRel |
| 91 | `AddCurvatureControl` | 示例给出唯一的前置：先在图形区选中样条段，再由选区取到 ISketchSpline | 2. Select the spline in the graphics area. |
| 92 | `AddCurvatureControl` | 页面 XPos/YPos/ZPos 无单位；示例用 /1000 换算，说明坐标是米 | Set swSplineH2 = swSpline.AddCurvatureControl(6.3 / 1000, 15.075 / 1000, 0) |
| 93 | `AddCustomButton` | 示例用宏文件夹拼出绝对路径传位图名，Remarks 未说路径要求 | result = swTaskPane.AddCustomButton(folder + "save.png", "Save (custom png)"); |
| 94 | `AddCustomButton` | 示例显示必须先 AddCustomButton/AddStandardButton 再 AddControl，按钮才出现在顶部 | swTaskPane.AddControl(ctrlName, ctrlLicKey); |
| 95 | `AddCustomButton` | 示例显示自定义按钮的索引是 0（ButtonIndex+1 落在 case 1） | Debug.Print("Save (custom png) button clicked."); |
| 96 | `AddDecal` | 示例给出页面没有的前置：必须已激活光线追踪渲染引擎 | ' 3. Verify that a ray-trace rendering engine is active. |
| 97 | `AddDecal` | 示例要求先 CreateDecal 并给该 Decal 挂上面实体，才能传给本方法 | Set swDecal = swModelDocExt.CreateDecal |
| 98 | `AddDecal` | 示例给出调用后还要 Rebuild，并说明 Decal 用 .p2d + .bmp 两个文件名 | Call swModelDocExt.Rebuild(swRebuildAll) |
| 99 | `AddDimension2` | 示例没有显式 SelectByID2，选中态直接来自上一句 SketchManager.CreateLine | swModel.SketchManager.CreateLine 0.01, 0.01, 0, 0.01, 0.01 + Height, 0 |
| 100 | `AddDimension2` | 示例把 swInputDimValOnCreate 这个开关设在 ISldWorks（swApp）上，建完再置回 True，Remarks 未说归属对象 | swApp.SetUserPreferenceToggle swInputDimValOnCreate, True |
| 101 | `AddDimension2` | 工程图示例按实体对象选（SelectEntity）而非按名或按坐标，与 Remarks 的「按位置别按名」不矛盾 | = swView.SelectEntity(swEnt, False) |
| 102 | `AddDisplayEnt` | 示例的数据坐标（0.12 / 0.09 等）是图纸米制，Remarks 的 data 说明未给单位 | boolstatus = selDim.AddDisplayEnt(2, (vEntData)) ' Filled triangle |
| 103 | `AddDisplayEnt` | 示例对同一尺寸连发 4 次本方法再叠 AddDisplayText，凑成一张替换图形；Remarks 未说可多次叠加 | boolstatus = selDim.AddDisplayEnt(4, (vEntData)) ' Arc |
| 104 | `AddDisplayEnt` | 示例说明取本对象前必须按 DIMENSION 选中并核对 GetSelectedObjectType3 = swSelDIMENSIONS | If selType = SwConst.swSelDIMENSIONS Then |
| 105 | `AddDisplayStateSpecificRenderMaterial` | 示例把 DisplayStateOption 传 swAllDisplayState，并把 GetDisplayStates() 的结果转成 string[]  | status = swModelDocExt.AddDisplayStateSpecificRenderMaterial(swRenderMaterial, ( |
| 106 | `AddDisplayStateSpecificRenderMaterial` | 两个 out ID 返回后，还可用 IRenderMaterial::GetMaterialIds 再回读同一对 ID。 | swRenderMaterial.GetMaterialIds materialID1, materialID2 |
| 107 | `AddDisplayText` | 调用前须先选中尺寸并经 ISelectionMgr 取回 DisplayDimension，示例还判 selType = swSelDIMENSIONS；页面未 | If selType = SwConst.swSelDIMENSIONS Then |
| 108 | `AddDisplayText` | Format 实参是 ITextFormat，取自 GetUserPreferenceTextFormat(swDetailingDimensionTextFo | boolstatus = selDim.AddDisplayText("Hi!", (vEntData), textFont, SwConst.swTextJu |
| 109 | `AddDistanceMate` | 示例传 FirstArcCondition=1、SecondArcCondition=1 并回读打印 DistanceFirstArcCondition/Sec | Debug.Print "First arc condition as defined in swDistanceMateArcConditions_e: "  |
| 110 | `AddEdges` | 两个实参是 object[]；示例把 InsertSketchForEdgeFlange 用的那条 Edge 放进 aFlangeEdges，Sketch 取自 | aFlangeEdges[0] = swEdge; |
| 111 | `AddEdges` | AddEdges 紧接在 CreateDefinition(swFmEdgeFlange) 之后、其余 FeatData 属性之前调用；返回的 swEdgeFl | Call FeatData.AddEdges(vFlangeEdges, vSketchFeats) |
| 112 | `AddEntity` | 实参是实体对象而非选区：示例先经 GetSelectedObject6 取到 Face2，再 ClearSelection2 清掉选区，之后才调 AddEnti | swModel.ClearSelection2(true); |
| 113 | `AddEntity` | AddEntity 也可作用在 Decal 上：示例把 CreateDecal() 返回的 Decal 直接转成 RenderMaterial 再调 AddEn | swMaterial = (RenderMaterial)swDecal; |
| 114 | `AddExplodeStep2` | 两个索引都传 -1；示例只选 mark=2 的方向实体（SelectByRay 的 Mark 参数为 2），未选 mark=32 的旋转轴。 | boolstatus = swModel.Extension.SelectByRay(9.95048714770577E-02, 0.1043173061133 |
| 115 | `AddExplodeStep2` | 返回值直接赋给 SldWorks.ExplodeStep，并回读 ExplodeDistance/RotationAngle 等属性；页面 Returns 只写 | Debug.Print "Explode distance (m): " & explStep.ExplodeDistance |
| 116 | `AddExternalDocuments` | C# 里字符串数组要先经 BStrWrapper[] 包装才能传入，而 GetRenderStockReferences() 返回的 object[] 可直接传 | status = swPackAndGo.AddExternalDocuments(ObjectArrayToBStrWrapperArray(otherFil |
| 117 | `AddExternalDocuments` | VB/VB.NET 里 String 数组直接传即可；AddExternalDocuments 须早于 SetSaveToName2 与 SavePackAnd | status = swPackAndGo.AddExternalDocuments(otherFiles) |
| 118 | `AddFilletedCorners` | 示例写明刚拿到的角对象 ReliefType 默认是 tear（成员页未给默认值）。 |            // Default is tear relief for all Sketched Bends |
\| 119 \| `AddFrame` \| 示例给出成功判据：GetFrameCount 加一；成员页只说返回 bool。 \| FrameCount = swGtol.GetFrameCount(); // frame count
should increase by one |
| 120 | `AddGroupBox` | 示例把两个 swAddGroupBoxOptions_e 值按位或成 Options；成员页只说「as defined in swAddGroupBoxOpti |             caption = "Sample Group Box";
            options = (int)swAddGroupB |
| 121 | `AddGroupBox` | 示例要求页内每个控件 ID 唯一，群组 ID 单独 const 出来。 |     //Each object in the page needs a unique ID
    const int GroupID = 1; |
| 122 | `AddHorizontalDimension2` | 示例写明视图里无法转换的边会让调用返回 NULL（成员页无 Remarks，也未写失败形状）。 | NULL if cannot convert edge in this view
Set
swDispDim = swDrawModel.AddHorizont |
| 123 | `AddIndicator` | 示例逐一列出受支持的 BorderType 四个值；成员页只指向枚举、不列举。 | // supported border types: swGtolIndicatorBorderType_CollectionPlane,
swGtolIndi |
| 124 | `AddIndicator` | 示例把 swGtolGeomCharSymbol_e 的值塞进 BorderType 槽，标注 unsupported 并靠返回值判失败。 | boolstatus = swGtolFrame.AddIndicator((int)swGtolGeomCharSymbol_e.swGcsFLAT,
(in |
| 125 | `AddInstanceAt` | 示例要求先回滚并 AccessSelections 才能改实例表，成员页没提这一步。 |     'Roll back and access the variable pattern feature
    status = swDimensionD |
| 126 | `AddInstanceAt` | 示例在 AddInstanceAt 之后用 GetInstanceCount 复核，并只用返回 bool 判成败。 |     status = swDimensionDrivenTablePatternFeat.AddInstanceAt(False, -1)
    Debu |
| 127 | `AddInstanceAt` | 示例把 SetInstanceDimensionValue 的实例号取成添加前读到的 GetInstanceCount 值。 |     status = swDimensionDrivenTablePatternFeat.AccessSelections(swModel, Nothing |
\| 128 \| `AddItem` \| 示例给出 Property 的真实写法「Document name -- SW Special」，Condition 以十六进制 0x4 传入。 \|             // Add selection criteria to query list
            AddRetVal = Adva |
| 129 | `AddMenuItem5` | 示例给出验证「支持高分辨率缩放」的实操：改系统文字大小后重跑再比对按钮尺寸 | // 5. Change the size of the text and other items on your computer. |
| 130 | `AddMenuItem5` | ImageList 实测只填 3 个路径（nxn / nnxnn / nnnxnnn 三档），而备注列的是 6 档像素 | images(0) = "Pathname_to_menu_item_nxn_image" |
| 131 | `AddMenuPopupIcon3` | 示例先 SwApp.Frame() 取到 IFrame 接收者再调用，成员页未写接收者从哪来 | frame = SwApp.Frame() |
| 132 | `AddMenuPopupIcon3` | ImageList 只放 3 张（nxn/nnxnn/nnnxnnn），备注列的是 6 档像素 | imageList[0] = "Pathname_to_button_nxn_image"; |
\| 133 \| `AddMenuPopupIcon3` \| 示例给出高分辨率缩放的验证动作：改显示缩放后重跑，比对右键菜单按钮尺寸 \| // 3. Note the size of the button added by this add-in to the
//    context-sens |
| 134 | `AddNewPosition` | 示例给出成员页没有的前置：装配体须含带槽配合、且该配合受距离/百分比约束 | // Preconditions: Open an assembly document that contains
 a mechanical slot fea |
| 135 | `AddNewPosition` | 示例给出调用序：Initialize 之后逐个 AddNewPosition，最后 CreateFeature | mateControllerObj.Initialize(dArray);
mateControllerObj.AddNewPosition("Position |
| 136 | `AddNote` | 示例要求先用 SelectByID2 选中 NOTE 再取 INote 传入，成员页只说「要附加的注释」 | boolstatus = Part.Extension.SelectByID2("DetailItem350@Drawing View1", "NOTE", 0 |
| 137 | `AddNote` | 示例给出「同一视图」规则的可观测后果：跨视图注释的 AddNote 失败 | // This fails because note belongs to a different view |
\| 138 \| `AddOrUpdateSearchData` \| 示例给出成员页没写的必做项：须在 选项>搜索 勾选 Always index 才会建索引 \| ' 2. Click Tools > Options > Search > Always index (may slow
' SOLIDWORKS Design |
| 139 | `AddOrUpdateSearchData` | 示例要求保存文档后才可被检索；成员页只说「索引之后」 | boolstatus = swModel.Save3(swSaveAsOptions_Silent, longstatus, longwarnings) |
| 140 | `AddPartExplodeStep` | ExplDirIndex 不设置时示例传具体哨兵值 -1；成员页只说 neither，未给值 | explStep = (PartExplodeStep)config.AddPartExplodeStep("Exploded View1", 0.07, -1 |
| 141 | `AddPartExplodeStep` | 成员页要求用 GetCurrentPartExplodeViewName 取名；示例改从 GetExplodedViewNames 取并传视图名 | varViews = (object[])swModel.GetExplodedViewNames((string)configVar[0]); |
| 142 | `AddPathLengthDim` | 成员页未标 X/Y/Z 单位；示例实参是米量级小数 | myDisplayDim = (DisplayDimension)Part.Extension.AddPathLengthDim(-0.058039547403 |
| 143 | `AddPathLengthDim` | 示例给出该路径尺寸的期望读数 15.75 | see the path length dimension of 15.75. |
| 144 | `AddPrefix` | 示例按属性直接赋值，且与 AddSuffix 成对设置前缀后缀 | swPackAndGo.AddPrefix = "SW_"; |
| 145 | `AddPrintRange` | 示例只调用一次且只打第 1 页，打印后用 ResetPrintRange 清范围 | printSpec.AddPrintRange(1, 1); |
| 146 | `AddProfileBspline` | 成员页只举 CreateRevolutionSurface / CreateExtrusionSurface，示例改用 FeatureReferenceCurv | swRefCurve = (ReferenceCurve)swModel.FeatureReferenceCurve(1, (vCurve), true, "" |
| 147 | `AddRebuildSaveMark` | 版本门槛：SW2013 及以后才有这种标记配置的用法 | // * In SOLIDWORKS 2013 and later, to mark each configuration |
| 148 | `AddRebuildSaveMark` | 前置：必须先激活该配置再写这个属性 | //   1. Activate each configuration and set |
| 149 | `AddRevision` | Revision 实参是单个字母（示例传 "A"），返回值被当作新版本号打印 | Debug.Print("  New revision: " + revTableAnno.AddRevision("A")); |
| 150 | `AddRevision` | 前置：须先由 Sheet.InsertRevisionTable2 建表拿到该注解，成员页未写 | // Insert a revision table and add a revision row |
| 151 | `AddRow` | CellValues 第 0 格是新行的配置名（示例赋 "190"），第 1 格才是列数据 | ' Name of configuration for newly created row |
| 152 | `AddSelectionListObject` | SelectData 实参可传 null/Nothing，示例全程不调 CreateSelectData | retval = swSelectionManager.AddSelectionListObject(swSketchPoint, null); |
| 153 | `AddSelectionListObject` | Object 也可为 TearEdges 里的 Edge；参数说明 "(see Remarks)" 未列可用类型 | status = swSelMgr.AddSelectionListObject(swEdge, null); |
| 154 | `AddSelectionListObjects` | VB.NET 示例把 Objects 声明成 Object() 数组（6 个 sketch 特征），非 Remarks 要求的 DispatchWrapper | Dim selObjs() As Object |
| 155 | `AddSketchConstraints` | 它是带字符串索引的布尔属性：可读 AddSketchConstraints("") 也可写回 True | importData.AddSketchConstraints("") = True |
| 156 | `AddSlicingPlanesAndSketchesToFolder` | 示例先读该属性打印默认值、再置 true，靠随后的 InsertSlicing 才生成 Slice1 文件夹。 |            Debug.Print("Add slicing planes and sketches to folder? " + sliceData |
\| 157 \| `AddSnapShot` \| 示例把三种参数形态各用一次：具名、"?" 弹框、空串取默认名。 \|     Set snap1 = mvmgr.AddSnapShot("ASnap")
    ' Open dialog box to name the nex |
| 158 | `AddSnapShot` | 示例 Postconditions 列出实际得到的名字，坐实空串按 Snap*n* 递增。 | ' 4. Creates four snapshots in the DisplayManager:
' * Home
' * ASnap
' * Snap2
 |
| 159 | `AddSpecificDimension` | 示例在草图里用 SelectByID2 选两条 SKETCHSEGMENT（append 先 false 后 true）再调用；Remarks 的调用序只给图纸 |             boolstatus = Part.Extension.SelectByID2("Line3", "SKETCHSEGMENT", -0 |
| 160 | `AddSpeedPak2` | 示例只给具体取值 Type=1、PartThreshold=0.5，且返回值未被接收；成员页未给推荐取值。 |     ConfigMgr.AddSpeedPak2 1, 0.5 |
\| 161 \| `AddSpeedPak2` \| 示例 Postconditions 点名新建配置名为 Default_speedpak，成员页没写这个名字。 \| ' 1. Adds active_configuration (Default_speedpak) to the
'    ConfigurationManag |
| 162 | `AddStandardButton` | 示例先 CreateTaskpaneView2 建视图、再 AddControl 加载控件，按钮才出现在面板顶部；成员页无任何前置。 |             swTaskPane = (TaskpaneView)swApp.CreateTaskpaneView2(bitmap, toolTip |
| 163 | `AddStandardButton` | 示例点击处理用 ButtonIndex+1，说明按钮序号 0 基且含先前 AddCustomButton 那一枚。 |             switch ((ButtonIndex + 1)) |
\| 164 \| `AddSuffix` \| 示例给出赋值时序：SetSaveToName 与 FlattenToSingleFolder 之后、SavePackAndGo 之前。 \|             // Add a prefix and suffix to the filenames
            swPackAndGo. |
| 165 | `AddSymmetricDimension` | 示例除抑制弹框外，建完还把 swInputDimValOnCreate 复位为 true；Remarks 只说抑制、不提恢复。 |             swApp.SetUserPreferenceToggle((int)swUserPreferenceToggle_e.swInputD |
| 166 | `AddSymmetricDimension` | 示例在 ClearSelection2 之后重选中心线与一条线，说明调用时须恰有这两个实体被选中；Remarks 未写此前置。 |             swModel.ClearSelection2(true); |
| 167 | `AddTangencyControl` | 示例把 XPos/YPos 写成毫米除以 1000（即米），而成员页 Parameters 只写 x coordinate，未给单位 |     Set swSplineH1 = swSpline.AddTangencyControl(-48.92 / 1000, -5.07 / 1000, 0) |
| 168 | `AddTangencyControl` | 示例前置：先按 SKETCHSEGMENT 选中样条再从 SelectionManager 取对象；成员页无任何前置说明 |     boolstatus = swModelDocExt.SelectByID2("Spline1", "SKETCHSEGMENT", 0, 0, 0,  |
| 169 | `AddText` | 示例首条 AddText 的 X/Y/Z 三参数全传 0，说明索引只由调用先后决定，与坐标无关 |      swNote.AddText "zero pt", 0, 0, 0 |
| 170 | `AddText` | 示例给出完整调用序：先 DrawingDoc.CreateCompoundNote 建复合注释，再 AddText；成员页只说选中的复合注释 |     Set swNote = swDrawing.CreateCompoundNote(0.00635, 0.05, 0.2, 0#) |
| 171 | `AddText` | 示例用 GetTextCount/GetTextAtIndex 回读，名字不同于页内 See Also 的 Compound 版 |         count = swNote.GetTextCount() |
| 172 | `AddTo` | 示例在 AddTo 前另发一次 SelectByID2 选面，被选中的面决定该气泡显示的数量文本 |     status = swModelDocExt.SelectByID2("", "FACE", -0.292957708052256, 3.1619250 |
| 173 | `AddTo` | 样式为数量时仍照传上文字符串 12 与下文字符串空串，按 Remarks 这两个参数会被忽略 |            Set swNote2 = swBalloonStack.AddTo(swBalloonTextContent_e.swBalloonTe |
| 174 | `AddToDB` | 示例在 3D 草图内打开该开关画包围盒点线，关掉后再 Enter3DSketch 收尾；成员页只谈二维草图语境 |             swSketchMgr.AddToDB = true; |
\| 175 \| `AddToDB` \| 块定义示例让该开关跨越 MakeSketchBlockFromSelected 与插入块实例，作用域大于页内所说的 sketch entity creation \| Set
swSketchBlockDef = swSketchMgr.MakeSketchBlockFromSelected(Nothing) |
| 176 | `AddToolbar4` | 示例是 C++ 原生 COM 写法：返回的 toolbarID 用出参接收，而非直接取值 | iSwApp->AddToolbar4(addinID,
title, smallImageFile, largeImageFile, menuPos, doc |
| 177 | `AddToolbar4` | 示例说明工具栏由 C++ COM Addin 向导自动生成、位图文件名来自资源，成员页无此生成前提 | Toolbars are added automatically by the C++ |
| 178 | `AddToolbar5` | 示例传入 3 条图标条图片路径，但只为 ToolbarIndex 0 建了一个命令，其余索引不会显示 |             toolbarImages[2] = "Pathname_to_toolbar_nnnxnnn_image"; |
| 179 | `AddToolbar5` | 示例把 MenuPositionForToolbar 传字面 0，与页内 Not used 一致；DocumentType 传 swDocTemplateTyp |             iToolbarId = iSwApp.AddToolbar5(addinID, "Test Toolbar", toolbarImag |
| 180 | `AddToolbarCommand2` | C# 示例把 ButtonEnableMethod 声明为 int 并返回 1，是 Remarks 那张 0 至 3 表的具体形态 |         public int ButtonEnableMethod() |
| 181 | `AddToolbarCommand2` | C++ COM 示例用 VARIANT_BOOL 出参接收本方法的返回，且四个字符串参数实为 CComBSTR | toolbarID, 0, callback, enable, tip, hint, &added); |
\| 182 \| `AddTrimmingLoop` \| 成员页 8 个参数全写 No description、无 Returns；示例给出一次真实 8 参调用及一组可用取值（二阶、Dim=2、非周期、每段 4 节点  \| swSurface.AddTrimmingLoop(nCurves,
Order, Dim, Periodic, nKnots, nCtrlPts, Knots |
| 183 | `AddTrimmingLoop` | 示例里承载该 trimming loop 的曲面由 ICreateExtrusionSurface 创建；成员页对本成员只字未提曲面来源（后继页 AddTrim | swSurface = swBody.ICreateExtrusionSurface((SldWorks.Curve)swCurve, |
| 184 | `AddTrimmingLoop2` | Remarks 只给规则；三份示例给出可直接用的成套取值：4 条二阶非周期直线、每段 4 节点 2 控制点、Dimen=2，正好满足 NumKnots=NumC | isGood = TmpSurf.AddTrimmingLoop2(NumCurves, Order, Dimen, Periodic, NumKnots, N |
| 185 | `AddTrimmingLoop2` | Remarks 只说「不指定 UV range 就传 null/Nothing」；示例给出一组实测值并按 U低/U高/V低/V高 摆放 | UVRange(3) = 1 |
| 186 | `AddTrimmingLoop2` | 示例给出 Remarks 所说「前置曲面」的实际形态：先 CreatePlanarSurface(RootPoint, Normal) 拿到 ISurface  | TmpSurf = (Surface)SurfaceBody.CreatePlanarSurface(RootPoint, Normal); |
| 187 | `AddVariablePitchHelixFirstPitchAndDiameter` | Remarks 第 1 步只写「调 InsertVariablePitchHelix」；示例显示必须先有一张草图圆，且第三实参要指明按「高+转数」定义 | status = swFeatureMgr.InsertVariablePitchHelix(false, true, (int)swHelixDefinedB |
| 188 | `AddVariablePitchHelixFirstPitchAndDiameter` | 示例先画圆（半径/圆心坐标都给死），才建可变节距螺旋；成员页未提前置草图圆 | swSketchSegment = (SketchSegment)swSketchManager.CreateCircle(0.0, 0.0, 0.0, 0.0 |
| 189 | `AddVariablePitchHelixFirstPitchAndDiameter` | 四份示例给出同一组实参 FirstPitch=0.053、FirstDiameter=0.05382625271268；成员页未给任何数值样例 | status = swFeatureManager.AddVariablePitchHelixFirstPitchAndDiameter(0.053, 0.05 |
| 190 | `AddVariablePitchHelixSegment` | Remarks 说「one or more times」但不给次数；示例固定用 4 次把剩余段加完（Height 0.0265/0.03975/0.046375 | status = swFeatureManager.AddVariablePitchHelixSegment(0.0265, 0.05382625271268, |
| 191 | `AddVariablePitchHelixSegment` | 示例给出完整参数序列：直径全程保持 0.05382625271268 不变，只 Height（转数）与 Pitch 递增；成员页未给数值 | status = swFeatureMgr.AddVariablePitchHelixSegment(0.03975, 0.05382625271268, 0. |
| 192 | `AddVector` | 示例把返回的 MathPoint 的 ArrayData 三个分量原样交给 CreatePoint2 建 3D 草图点，未做任何换算 | swApexPt = swModel.CreatePoint2(swApex.ArrayData(0), swApex.ArrayData(1), |
| 193 | `AddVector` | 示例先 CreateVector 再 Scale，最后才 AddVector——实参是 MathVector 而非裸数组，成员页只写 object | swApex = swOrigin.AddVector(swAxis) |
| 194 | `AddVerticalDimension2` | 示例每次调用前先用 SelectEntity 把模型那条边在当前视图里选中（逐视图重新选中），成员页未写这一前置 | = swView.SelectEntity(swEnt, False) |
| 195 | `AddVerticalDimension2` | 示例明确该视图里边转换不了就返回 NULL；成员页 Returns 只写「Newly created dimension」 | NULL if cannot convert edge in this view |
| 196 | `AddVerticalDimension2` | 示例先按视图坐标判断边是竖直还是水平再选 AddVerticalDimension2 / AddHorizontalDimension2，说明「Vertical | Must be vertical |
| 197 | `AdditionalSymbol` | 示例给出拿到该属性的完整链路：注解 GetPMIData → GetDimensionItemAtIndex(k) → PMIDimensionItem；成员页 | swPMIDataDimItem = (PMIDimensionItem)swPMIDataDim.GetDimensionItemAtIndex(k); |
| 198 | `AdditionalSymbol` | 示例按 swToleranceZoneModifier_e 解读读数，且只读取不赋值，与成员页的 get-only 声明一致 | Additional symbol as defined in swToleranceZoneModifier_e: " & swPMIDataDimItem. |
| 199 | `AdvancedHole2` | C# 侧数组参数须把每个元素包成 DispatchWrapper、传 DispatchWrapper[]，不能直接传 AdvancedHoleElementDa | DispatchWrapper[] dispArray = ObjectArrayToDispatchWrapperArray(new object[] { a |
| 200 | `AdvancedHole2` | 元素直径/深度按米传入，示例用 25.4/1000 的英寸→米系数；成员页对该方法的数组元素未提任何单位 | ConvFactorLength = 25.4 / 1000; |
| 201 | `AlignAxis` | 示例给出实际写入的枚举成员（Vertical）；成员页只说「as defined in swMirrorProfileOrAlignmentAxis_e」，未给 | Group2.AlignAxis = (int)swMirrorProfileOrAlignmentAxis_e.swMirrorProfileOrAlignm |
| 202 | `AlignDrawingView` | 必须先选中辅助视图再调用（示例用 SelectByID2 类型 DRAWINGVIEW + SelectionManager 取 View）；成员页未给任何前置 | 2. Modify this macro to select the auxiliary view. |
| 203 | `AlignDrawingView` | 示例列出实际使用的四个 swAlignDrawingViewTypes_e 成员；成员页只给枚举名不给取值 | boolstatus = DrawView.AlignDrawingView(swHorizontalToSheetClockwise) |
| 204 | `AlignMethod` | 示例只读 AlignMethod（Debug.Print）从不写入，且须先 AccessSelections 取定义；成员页未说明读写方向 | Debug.Print " Align method: " & swChainPatternFeatureData.AlignMethod |
| 205 | `AlignRunningDimension` | 示例前置限定为已打开的工程图文档；成员页（无 Remarks）未说明适用文档类型 | 1. Open public_documents\samples\tutorial\advdrawings\foodprocessor.slddrw. |
| 206 | `AllowFlip` | 成员页无示例段；示例给出取操纵器→转为 DragArrowManipulator→再设 AllowFlip 的具体调用序。 | (DragArrowManipulator)swManip.GetSpecificManipulator(); |
\| 207 \| `AllowMultipleSelectOfSameEntity` \| 示例把它紧接在 SingleEntityOnly=false 之后设置，且整块都在 pm_Page.Show() 之前，成员页未提与 SingleEntityO \| pm_Selection.SingleEntityOnly = false;
            pm_Selection.AllowMultipleSel |
| 208 | `AlongCurveOption` | 唯一带创建动作的示例给出前置：必须预选边，并用 InsertReferencePoint 传四个参数建多点。 | ' An edge must be preselected
    vFeatArr = swFeatMgr.InsertReferencePoint(swRe |
| 209 | `AlongCurveOption` | 其余三份示例只读取回显、从不赋值，说明该属性可只读使用。 | Debug.Print "    AlongCurveOption   = " & swRefPtData.AlongCurveOption |
| 210 | `AlphaOutput` | 三份示例只在“Current rendering values”里读取它；后面的“Change rendering values”段写了其余全部选项，唯独跳过  | Debug.Print("  Alpha output? " + swRayTraceRenderOptions.AlphaOutput); |
| 211 | `AlphaOutput` | 示例里取得渲染器的那一行被注释掉，却直接用 swRayTraceRenderer 取选项（VBA 版同样被注释）。 | //swRayTraceRenderer = (RayTraceRenderer)swApp.GetRayTraceRenderer((int)swRayTra |
\| 212 \| `AlternateName` \| 示例给出必须先把 BOMPartNoSource 置成 UserSpecified 再写 AlternateName 的顺序，并连写两次同一值。 \| thisConfig.BOMPartNoSource = swBOMPartNumber_UserSpecified
        thisConfig.Al |
| 213 | `AlternateName` | 示例只在 BOMPartNoSource 为 UserSpecified 的分支里读 AlternateName，正是备注那条清空规则的反面用法。 | BOMPartNumber = config.AlternateName |
| 214 | `AnchorType` | 孔表示例给出四种锚点的对角映射（BottomLeft↔TopRight 等）并回写 AnchorType，成员页只说类型由该枚举定义。 | newCorner = swBOMConfigurationAnchorType_e.swBOMConfigurationAnchor_TopRight; |
| 215 | `AnchorType` | Get_General_Table_Feature 两例只读取 AnchorType 回显，从不赋值。 | anchorType = swTableAnnotation.AnchorType; |
| 216 | `Anchored` | 孔表示例给出取锚点对象的实际路径：从视图所属 Sheet 上按表类型取 TableAnchor，成员页只让用 AnchorType 与 GetPosition。 | holeTableAnchor = (TableAnchor)drwView.Sheet.get_TableAnchor((int)swTableAnnotat |
| 217 | `Anchored` | 锚点位置写在 TableAnchor.Position 上（与表自身的 GetPosition 不是同一处），这是示例才有的落点。 | holeTableAnchor.Position = dNewPosition; |
| 218 | `AngleOverride` | 示例给出取值路径：先把 AdvancedHoleElementData 转成 CountersinkElementData，才能写本属性 |             swCounterSinkNear = (CountersinkElementData)swAdvHole_Near_1; |
| 219 | `AngleSelection` | Remarks 只列 Angle/MaxVal/MinVal，示例还要把两个角度实体写进 EntitiesToMate[2] |             MateData.EntitiesToMate[2] = AngleEntitiesToMateVar; |
| 220 | `AngleSelection` | 示例给出取本对象的方式：先 CreateMateData(22) 再转成 HingeMateFeatureData |             HingeMateFeatureData MateData = (HingeMateFeatureData)swAssembly.Cre |
| 221 | `AngularTolerance` | 成员页无任何前置说明，示例要求先 AccessSelections，读完再 ReleaseSelectionAccess |             swHealEdgesFeature.AccessSelections(swModel, null); |
| 222 | `AnimateDuringSimulation` | 示例给出取属性对象的路径：GetProperties(4) 后再转 CosmosMotionStudyProperties | swMotionStudyProps = swMotionStudy1.GetProperties(4) |
\| 223 \| `AnnotationCount` \| 示例读取计数前先调 Activate() 激活该注释视图，成员页未提这一步 \|                 swAnnView.Activate();
                annotations = (object[])sw |
| 224 | `AnnotationViewCount` | 示例给出配对用法：AnnotationViews 只取一次，随后用 AnnotationViewCount 作 <= count-1 的循环上界遍历同一数组 | for (i = 0; i <= swModelExt.AnnotationViewCount - 1; i++) |
| 225 | `AnnotationViews` | 示例把返回值直接强制转成 object[] 数组使用（VBA 版则当 Variant 赋给 swAnnViews） | swAnnViews = (object[])swModelExt.AnnotationViews; |
| 226 | `AppPageSetup` | 示例独有信息：ScaleDraftEdges 只在高质量打印下才有意义，故必须先判 HighQuality | Debug.Print("Drawing not set to print in high quality. Can only scale draft edge |
| 227 | `ApplicationType` | 示例把它当门禁用：与 swApplicationType_e.swApplicationType_3DEXPERIENCE 相等才走保存/重开流程 | If swApp.ApplicationType = swApplicationType_e.swApplicationType_3DEXPERIENCE Th |
| 228 | `ApplyAppearance` | 示例独有信息：改完该属性仍须再调 SetMaterialVisualProperties 才会写回零件 | longstatus = myPart.SetMaterialVisualProperties(myMatVisProps, (int)swInConfigur |
| 229 | `ApplyMaterialColorToPart` | 示例独有信息：先读原值取反再写回，且同样须跟一次 SetMaterialVisualProperties 才落盘 | myMatVisProps.ApplyMaterialColorToPart = !orgApply; |
| 230 | `ApplyMaterialHatchToSection` | 示例在零件文档上经 GetMaterialVisualProperties() 取到该属性读写，成员页只提工程图剖视图 | myMatVisProps = myPart.GetMaterialVisualProperties(); |
| 231 | `ApplyMaterialHatchToSection` | 改完属性必须回写 SetMaterialVisualProperties 才生效，成员页未提这一步 | longstatus = myPart.SetMaterialVisualProperties(myMatVisProps, (int)swInConfigur |
| 232 | `ApplySavedSortScheme` | 示例另给前置：表须先选中，且 BOM 表为四列并取消 Follow assembly order | //    Follow assembly order in Item Numbers is not selected. |
| 233 | `ApplySavedSortScheme` | 调用前先 InsertRow(2,2) 插一行，再套用已保存的排序方案 | swTable.InsertRow(2, 2); |
| 234 | `ApplyThread` | 示例显示 BlindDepth/Diameter 需乘 1000.0 才是毫米，成员页未给单位 | Debug.Print("      BlindDepth       = " + swCosThread.BlindDepth * 1000.0 + " mm |
| 235 | `ApplyThread` | 示例读完 ApplyThread 后无条件读 BlindDepth，不按 Remarks 做条件分支 | Debug.Print("      ApplyThread      = " + swCosThread.ApplyThread); |
| 236 | `ApplyThread` | 线程由 InsertCosmeticThread3 以盲孔端条件与 0.025 建出，属示例独有信息 | swFeat = swModel.FeatureManager.InsertCosmeticThread3((int)swCosmeticStandardTyp |
| 237 | `ApplyTransform` | 示例先 Body.Copy 再变换，原体不动 | Set swBodyCopy1 = swBody1.Copy |
| 238 | `ApplyTransform` | 示例用 MathUtility.CreateTransform 从 16 元 double 数组造 MathTransform | MathXform = (MathTransform)MathUtility.CreateTransform(vXform); |
| 239 | `ApplyTransforms` | 示例先对每个检测组 SetComponents，再 ApplyTransforms | longstatus = cdg.SetComponents(comp); //Holder |
| 240 | `ApplyTransforms` | 变换数组由 CreateTransform 生成后装入 MathTransform[] 再传入 | transform[0] = (MathTransform)swMathUtil.CreateTransform((TransformDataVariant)) |
| 241 | `ApplyTransforms` | 返回值收进 longstatus 后未检查，直接进入 IsCollisionPresent | longstatus = cdm.IsCollisionPresent(true); |
| 242 | `ArcExtensionLineOrOppositeSide` | 示例在草图编辑态按名字选草图内尺寸 D1 再取 DisplayDimension | status = swModelDocExt.SelectByID2("D1@Sketch1@box.SLDPRT", "DIMENSION", -5.0921 |
| 243 | `ArcExtensionLineOrOppositeSide` | 设完立即读回同一属性自检 | Debug.Print ("Leader attached to arc extension line? " + swDisplayDimension.ArcE |
| 244 | `ArcLength` | 读前须先设 ArcOption（0 中心到中心 / 1 最小 / 2 最大）并 Calculate 成功 | swMeasure.ArcOption = 0; |
| 245 | `ArcLength` | 示例选的是两个面而非圆弧，ArcLength 实际走 -1 哨兵分支 | status = swModelDocExt.SelectByID2("", "FACE", -0.00382117299216134, -0.00322469 |
| 246 | `ArcLength` | 打印时不做任何单位换算 | Debug.Print("Arc length: " + swMeasure.ArcLength); |
\| 247 \| `ArcOption` \| 示例逐字给出 0/1/2 三值含义（中心到中心/最小距离/最大距离），成员页只指向枚举名 \| 'Can set this to 0
    ' 0 = center to center
    ' 1 = minimum distance
    ' 2 |
| 248 | `ArcRadius` | 示例给出实际赋值 0.00508 与调用序：InsertRevisionCloud→GetAnnotation→SetPosition→ArcRadius→Se | RevCloud.ArcRadius = 0.00508 |
| 249 | `Area` | 示例给出读值前置：必须先 CreateMeasure 并设 ArcOption，再 Calculate 返回 True 后各量才有意义 | status = swMeasure.Calculate(Nothing) |
| 250 | `AreaStyle` | 示例给出取到该属性的对象链：须先 GetPMIData→GetDatumTarget 得 PMIDatumTarget，前置 IAnnoType=2 且 IAn | Debug.Print "  Area style as defined in swPMIDatumTargetAreaStyle_e: " & swPMIDa |
| 251 | `ArrangeWindows` | 示例给出调用序：先 CreateNewWindow 再 ArrangeWindows，且实际传 1；C++ 示例用局部变量 lWindowStyle=2 | swApp.ArrangeWindows 1 |
| 252 | `ArrowSide` | 示例给出取值路径：须先 View.GetFirstDisplayDimension 取到 DisplayDimension 再逐个 GetNext 遍历后读该属 | Debug.Print " Arrow side: " & swDisplayDimension.ArrowSide |
| 253 | `Ascending` | 示例显示 Ascending 是按下标索引的可写属性：0=主排序、1=次排序逐级设方向；三级排序缺席时 ColumnIndex(2)=-1 且不写 Ascend | swSortData.Ascending(0) = True ' sort ascending |
| 254 | `Ascending` | 示例给出唯一取得途径：先从 IBomTableAnnotation 取 BomTableSortData 再逐级赋值，页面完全未提对象从哪来 | Set swSortData = swSpecTable.GetBomTableSortData |
| 255 | `Aspect` | 示例给出取得该对象的唯一路径：模型里先插入 OLE 对象，再用 GetSelectedObject6(1,0) 取已选中项；Remarks 无任何前置或获取说明 | swOleObj = (SwOLEObject)swSelMgr.GetSelectedObject6(1, 0); |
| 256 | `AttachAnnotation` | 示例的第二项选择是视图内的一个 FACE（按点 SelectByID2，append=True、mark=0），而非 Remarks 所说的整个 drawing | boolstatus = part.Extension.SelectByID2("", "FACE", 0.0783563575357558, 0.174480 |
| 257 | `AttachAnnotation` | 示例附着前先 SetLeader3 设为弯引线（swBENT），Remarks 没有任何引线前置要求 | ret = anAnnot.SetLeader3(swLeaderStyle_e.swBENT, swLeaderSide_e.swLS_SMART, true |
| 258 | `AttachAnnotation` | 示例先 ActivateView 激活目标视图、再往选区追加面，Remarks 只说 multi-select 未提激活 | boolstatus = draw.ActivateView("Drawing View1"); |
| 259 | `AutoBalloon2` | 参数 Layout 取自用户首选项 DetailingAutoBalloonLayout，示例以常量 -1 表示默认；页面两个参数都只写 No descript | Const swDetailingBalloonLayout_Default As Long = -1 |
| 260 | `AutoBalloon2` | 返回形状由示例给出：已有气球或文档为 lightweight 时返回空数组，否则每个已解析组件一个 Note；页面无 Returns 段 | ' Returns an empty array if: |
| 261 | `AutoBalloon2` | 前置：必须先选中一个 drawing view 并激活，页面未提任何前置 | bRet = swModelDocExt.SelectByID2("Drawing View1", "DRAWINGVIEW", 0, 0, 0, False, |
| 262 | `AutoBalloon3` | 只有示例列出返回空数组的两种情况：文档任一视图已有气泡、或文档为轻量；成员页未写。 | Balloons already exist in any drawing view on any on sheet in |
| 263 | `AutoBalloon3` | 示例把 GetAttachPos / GetAnnotation.GetPosition 的读数乘 1000 再按 mm 打印 ⇒ 这些读数是米；成员页未写单位 | vAttachPos(0) * 1000# |
| 264 | `AutoBalloon5` | 示例把「打开带 BOM 表的工程图」列为前置，成员页步骤 1 只要求先选中视图或图纸。 | Preconditions: Open a drawing with a bill of materials (BOM) table. |
| 265 | `AutoBalloon5` | 示例列出成员页只以「Set the properties」一句带过的 IAutoBalloonOptions 属性名。 | autoballoonParams.EditBalloonOption = swEditBalloonOption_Resequence |
| 266 | `AutoDimension` | 示例用空名字＋米制坐标选顶点作基准；成员页只说「选中顶点/草图点并打 mark」。 | status = swModelDocExt.SelectByID2("", "VERTEX", 0.20215546544586, 0.2496899375, |
| 267 | `AutoDimension2` | 打基准 mark 的实际入口是 IEntity::Select3 的第二个形参；成员页只说「mark」，未指明 API。 | bRet = swSketchSegHoriz.Select3(True, swAutodimMarkHorizontalDatum, Nothing) |
| 268 | `AutoDimension2` | 示例指出进入草图编辑会清掉选区，必须重新选中基准；成员页未提。 | ' Editing sketch clears selections |
| 269 | `AutoDimension2` | 示例注释确认「竖线作水平基准」，与成员页的基准对应关系相同。 | ' Vertical line is for horizontal datum |
| 270 | `AutoDimensionScheme` | 示例给出成员页没写的可选前置：先多选三个面来指定主、次、第三基准。 | 2. (Optional) Multi-select three faces to specify primary, secondary, |
| 271 | `AutoDimensionScheme` | 示例要求先在 Tools > References 里 Browse 并加载类型库，成员页未提这一步。 | Find and select install_dir\swdimxpert.tlb. |
| 272 | `AutoExplode` | C++ 示例在 CollapseAssembly 里再次调 AutoExplode 再调 ViewCollapseAssembly，把它当收起用。 | hres = swAssemblyDoc->AutoExplode(&retVal); |
| 273 | `AutoExplode` | 示例显示自动爆炸只是起点：紧接着取第 0 步、删掉、重加 explode step。 | Set explStep = config.GetExplodeStep(0) |
| 274 | `AutoInsertCenterMarks2` | 示例给出 Gap 生效的配套动作：先清掉 Scale by view scale 勾选；成员页只列了取/设该开关。 | ' Clear Scale by view scale check box to set gap |
| 275 | `AutoInsertCenterMarks2` | 示例第 5 参 UseDocumentDefaults=true 时仍传 Size/Gap 等（0.0025 即 2.5 mm），成员页说这些仅在 false  | boolstatus = swActiveView.AutoInsertCenterMarks2(7, 11, true, true, true, 0.0025 |
| 276 | `AutoInsertCenterMarks2` | 示例先 SuppressView 目标视图、插完再 UnsuppressView；成员页只说对每个活动视图调用。 | Draw.SuppressView |
| 277 | `AutoReliefType` | 选 Tear 让位后还需配对设 ReliefTearType（swReliefTearTypes_e），成员页未提这层配套。 |                 FeatData.AutoReliefType = (int)swSheetMetalReliefTypes_e.swSheet |
\| 278 \| `AutomaticSolveOrder` \| 置 true 的实际次序语义：独立方程先于从属方程执行；成员页只说「由 SOLIDWORKS 定序」。 \| // 1. Sets the equation's Automatic solve order option
//    to true, which resu |
| 279 | `BOMPartNoSource` | 示例把 4 个枚举值各自对应的件号来源逐一展开，并含 ParentName 的递归取父配置；成员页只写「见 swBOMPartNumberSource_e」。 |     Select Case config.BOMPartNoSource |
| 280 | `BOMPartNoSource` | 示例给出赋值顺序：先设 UserSpecified 再赋 AlternateName，并另需 UseAlternateNameInBOM=True 才在 BOM |         thisConfig.UseAlternateNameInBOM = True |
| 281 | `BackWards` | 成员页无 Remarks；示例给出取得 ITextFormat 的路径之一：Callout.TextFormat。 |         swTextFormat = myCallout.TextFormat |
| 282 | `BackWards` | 成员页无 Remarks；示例给出另一条路径：草图文字段的 SketchText.GetTextFormat。 |     ProcessTextFormat swApp, swModel, swSkText.GetTextFormat |
| 283 | `BackgroundBottomGradientColor` | 示例全程未把 BackgroundType 设为 Graduated，只在改动 BackgroundType 之前读取该属性。 |     Debug.Print "Scene background bottom gradient color: " & Scene.BackgroundBot |
| 284 | `BackgroundEnvImage` | 示例给出必须先写的那句赋值；Remarks 只说要满足 UseEnvironment，没给写法。 |     Scene.BackgroundType = swSceneBackgroundType_e.swBackgroundType_UseEnvironme |
| 285 | `BackgroundProcessingOption` | 示例比 Remarks 多一步：先用 GetOpenDocSpec 取 DocumentSpecification 并置 Silent=True 再 OpenD |     docSpecification.Silent = True |
| 286 | `BackgroundProcessingOption` | VBA 版直接写枚举字面量 2，C#/VB.NET 写枚举名；Remarks 只给枚举名这一种写法。 |      swDrawingDoc.BackgroundProcessingOption = 2 |
| 287 | `BackgroundTopGradientColor` | 成员页未写怎么拿到 ISwScene；示例给出唯一路径：先取活动配置再 GetScene() | Scene = swConfig.GetScene(); |
| 288 | `BackgroundTopGradientColor` | 示例把它当可直接拼接的 int 读出，且读取发生在给 BackgroundType 赋值之前 | Debug.Print("Scene background top gradient color: " + Scene.BackgroundTopGradien |
| 289 | `BackgroundTopGradientColor` | 示例实际用的 BackgroundType 值是 UseEnvironment，不在 Remarks 那张只列 Plain/Graduated 的表里 | Scene.BackgroundType = (int)swSceneBackgroundType_e.swBackgroundType_UseEnvironm |
| 290 | `BackgroundType` | C# 侧把枚举赋给这个 int 属性必须显式转 int | Scene.BackgroundType = (int)swSceneBackgroundType_e.swBackgroundType_UseEnvironm |
| 291 | `BackgroundType` | 同一赋值在 VB 侧不转 int，说明转与不转都成立、只取决于语言 | Scene.BackgroundType = swSceneBackgroundType_e.swBackgroundType_UseEnvironment |
| 292 | `BalloonsPerLine` | 示例给出完整链：CreateStackedBalloonOptions() 拿对象→设本属性→整体交给 InsertStackedBalloon2 | swStackedBalloons.BalloonsPerLine = 10; |
| 293 | `BalloonsPerLine` | 示例的 Postconditions 要求先选中一个面，本属性是在此之后才设的 | status = swModelDocExt.SelectByID2("", "FACE", -0.311973500811291, 0.03296933432 |
| 294 | `BalloonsPerLine` | BOM 表示例独立给出同一取值 10，且 StackDirection 排在其后设置 | StackedBalloonParams.BalloonsPerLine = 10; |
| 295 | `BeadLength` | 成员页是空壳（无 Signature/Returns）；示例显示它是按箭头侧索引的带参属性，不是标量 | bdlen = swWeldBead.BeadLength(swWeldBeadSide_e.swWeldBeadArrowSide) |
| 296 | `BeadLength` | 赋值同样带侧索引，且须先 AccessSelections 回滚、最后 ModifyDefinition 提交 | swWeldBead.BeadLength(swWeldBeadSide_e.swWeldBeadArrowSide) = bdlen * 0.5 |
| 297 | `BeadPitch` | 成员页无任何签名与说明；示例显示它是带 swWeldBeadSide_e 索引的带参属性 | bdPitch = swWeldBead.BeadPitch(swWeldBeadSide_e.swWeldBeadArrowSide) |
| 298 | `BeadPitch` | 示例写侧为乘 0.5 缩放，说明返回的是长度类数值（页未给任何单位） | swWeldBead.BeadPitch(swWeldBeadSide_e.swWeldBeadArrowSide) = bdPitch * 0.5 |
| 299 | `BeadSize` | Returns 只写「Weld bead thickness」无单位；示例乘 39.37 输出 in，说明存值单位是米 | Debug.Print("   Weld bead size: " + swCosmeticWeldBeadFeatureData.BeadSize * 39. |
| 300 | `BeadSize` | 在本接口上它是无参标量属性，且读之前必须先 AccessSelections | swCosmeticWeldBeadFeatureData.AccessSelections(swModel, null); |
| 301 | `BeadType` | 成员页无签名与 Returns；示例显示它按侧索引，取值属 swWeldBeadType_e | bdTy = swWeldBead.BeadType(swWeldBeadSide_e.swWeldBeadArrowSide) |
| 302 | `BeadType` | 换面示例改用另一侧索引并设成 intermittent，两个标识符在原文里都未声明 | swWeldBead.BeadType(swWeldBeadOtherSide) |
| 303 | `BeginDrag` | 示例给出完整调用序：AddComponent → 设 TransformType/DragMode → BeginDrag → 循环 Drag → EndDra | bRet = swDragOp.BeginDrag(); |
| 304 | `BeginDrag` | 示例显示 BeginDrag 之后必须反复调 Drag 直至累计到目标角度，再调 EndDrag 收尾。 | bRet = swDragOp.EndDrag(); |
| 305 | `BeginSketchEdit` | 示例用文档对象上的 VBA 专用建线成员造几何（Remarks 只列 CreateLine2/CreateArc2 家族）。 | swDrawing.CreateLineVB 0, 0, 0, 0.01, 0.01, 0 |
| 306 | `BeginSketchEdit` | 示例顺序是 AddText 两段 → BeginSketchEdit → 造几何 → EndSketchEdit，几何窗口被两端夹住。 | swNote.BeginSketchEdit |
| 307 | `BehindSheet` | 示例还要求：先选中 SHEET 进图框编辑模式，ClearSelection2 后再按名字选注释对象赋属性。 | swNote.BehindSheet = True |
| 308 | `BeltLength` | 示例把 BeltLength 的单位标为米（Remarks 未写单位），初值 0.59492、修改值 0.3。 | Debug.Print("Belt length (m) changed to " + swFeatData.BeltLength); |
| 309 | `BeltLength` | 示例在创建与修改两处都先置 DrivingLength = true，满足 Remarks 的前置。 | beltChainFeatData.DrivingLength = true; |
| 310 | `BeltLocationPlane` | 示例的取值来自当前选区第 3 个对象（SelectByRay 选出的滑轮面），不是另建的基准面。 | beltChainFeatData.BeltLocationPlane = selMgr.GetSelectedObject6(3, -1); |
| 311 | `BeltThickness` | 示例把 BeltThickness 单位标为米（Remarks 未写单位），创建值 0.003、修改值 0.002。 | Debug.Print("Belt thickness (m) changed to " + swFeatData.BeltThickness); |
| 312 | `BeltThickness` | 修改阶段重设 BeltThickness 时并未再设 UseBeltThickness，说明该开关随特征保留。 | swFeatData.BeltThickness = 0.002d; |
| 313 | `Bends` | 读 Bends 前必须先 AccessSelections、读完必须 ReleaseSelectionAccess；Remarks 只指向一篇外部文档，未给调用 | status = swFoldsFeatureData.AccessSelections(swModel, Nothing) |
| 314 | `Bends` | C# 版显示返回值必须转成 object[] 才能按下标取元素，比 Returns 的“Array of bend features”更具体。 | bendsArray = (object[])swFoldsFeatureData.Bends; |
| 315 | `BentLeaderLength` | Remarks 只列出会返回 -1 的三种情形；示例给出使之为有效的那个调用：先用 swBENT 设置引线。 | errors = swAnno.SetLeader3(swLeaderStyle_e.swBENT, swLeaderSide_e.swLS_LEFT, Tru |
| 316 | `BentLeaderLength` | 示例给出赋值 0.05 并立刻回读的全过程；同文件其余坐标均为米制量级，成员页未标注单位。 | swAnno.BentLeaderLength = 0.05 |
| 317 | `Bidirectional` | 成员页连 Examples 段都没有；示例给出取得承载该属性的对象的入口与常量 swFmRefCurve。 | Set swFeatData = swFeatMgr.CreateDefinition(swFmRefCurve) |
| 318 | `BlankRefGeom` | Remarks 只说“select a reference plane”；示例给出确切选择调用形态：按名字 Plane1、PLANE、append=False、 | boolstatus = Part.Extension.SelectByID2("Plane1", "PLANE", -6.93294107213475E-02 |
| 319 | `BlankSketch` | 恢复显示前必须在 FeatureManager 树里重新选中同一批草图，示例用 Stop 强制中断来保证这一点。 | Stop |
| 320 | `BlankSketch` | 该 ModelDoc2 成员在工程图里也可用：示例先激活视图，再对视图内带 @Drawing View1 后缀的草图调用。 | boolstatus = swModelDocExt.SelectByID2("Sketch1@resetsketchvisibility-7@Drawing  |
| 321 | `BlendColor` | 对象须由 IPartDoc 取回；成员页只说 get/set，没说从哪拿。 | Set myMatVisProps = myPart.GetMaterialVisualProperties() |
| 322 | `BlendColor` | 赋值后必须再调 SetMaterialVisualProperties 才生效；成员页完全没提这一步。 | longstatus = myPart.SetMaterialVisualProperties(myMatVisProps, swThisConfigurati |
| 323 | `BlindDepth` | 示例把该值当米：写入用 25.4/1000 的英寸→米系数，读回打印为 "Blind depth in m"；成员页未写单位。 | Debug.Print("   Blind depth in m: " + ((AdvancedHoleElementData)swCounterSinkNea |
| 324 | `BlindDepth` | 示例用 AdvancedHole2 第 3 个实参 false 来满足 Remarks 的 UseBaselineDimensions=false 前置，而不是 | feat = swFeatureMgr.AdvancedHole2(dispArray, dispArray2, false, true, false, out |
\| 325 \| `BlockToleranceDecimalPlaces` \| 示例只在 DimensionType=BlockToleranceNoNominal 且 blockTols.Type=ASMEInch 分支里读它；角度类型改 \|                 If isAngleType Then
                    strs.Add ("Angular Block |
| 326 | `BlockToleranceDecimalPlacesIntraFeature` | 示例把它挂在 Select Case annotation.DimensionTypeIntraFeature 分支下（页面未说是哪个判据）；同一子过程的 pa |             strs.Add ("Feature locating Dimension Type: Block Tolerance No Nomin |
\| 327 \| `BloomEnabled` \| 示例在 BloomEnabled=false 之后仍继续写 Threshold=70 与 Radius=4，说明三者互相独立、可读可写。 \|             swRayTraceRenderOptions.BloomEnabled = false;
            Debug.Prin |
| 328 | `BloomRadius` | 示例给出 Radius 的实参 4（int 赋值），页面 Returns 未给取值范围。 |             swRayTraceRenderOptions.BloomRadius = 4; |
\| 329 \| `BloomThreshold` \| 示例给出 Threshold 的实参 70 并在设为 false 的 BloomEnabled 之后单独赋值，读回时用字符串拼接。 \|             swRayTraceRenderOptions.BloomThreshold = 70;
            Debug.Print |
| 330 | `BlurLength` | 示例先设 MotionBlur=True 再写 BlurLength=10；页面无 Remarks 说明这一先后依赖，Returns 只给 0~100、默认 5 |             swSaveAVIData.MotionBlur = true;
            swSaveAVIData.BlurLengt |
| 331 | `BlurOffset` | 示例给出取得 IAVIParameter 的入口；成员页只字未提这个对象从哪里来。 | Set swSaveAVIData = swMotionMgr.CreateAVIParameter() |
\| 332 \| `BlurOffset` \| 示例先设 MotionBlur=True 与 BlurLength=10 再设 BlurOffset，说明该值只在启用运动模糊时有意义；成员页无此依赖。 \|     swSaveAVIData.MotionBlur = True
    swSaveAVIData.BlurLength = 10
    swSave |
| 333 | `Body` | 成员页连 Returns 段都没有；示例显示返回值是单个 Body2 对象，Set 赋值后直接当实体用。 | Set swBody = swPart.Body |
| 334 | `Body` | 示例的装配分支改用 IComponent2::GetBody 取体，只有零件分支才调本成员。 | Set swBody = swComp.GetBody |
| 335 | `BoltDiameter` | 示例注明未配置 SOLIDWORKS Toolbox 时读螺栓/螺母信息会报错；成员页无此前置。 | ' Bolt and nut information causes an error |
| 336 | `BoltDiameter` | 示例给出取得 IHoleSeriesFeatureData2 的入口（按类型名找特征再 GetDefinition），成员页未写。 | Set swFeatData = swFeat.GetDefinition |
| 337 | `BoltHeadDiameter` | 示例注明未配置 SOLIDWORKS Toolbox 时读螺栓/螺母信息会报错；成员页无此前置。 | ' Bolt and nut information causes an error |
| 338 | `BoltHeadDiameter` | 示例给出取得 IHoleSeriesFeatureData2 的入口（按类型名找特征再 GetDefinition），成员页未写。 | Set swFeatData = swFeat.GetDefinition |
| 339 | `BomFeature` | 页面只说返回 IBomFeature 指针；示例用它取 BOM 的 Name，作为 MBD 3D PDF 的 BOM 映射名。 | BOMTableName = swBOMFeature.Name; |
| 340 | `BomFeature` | 示例注释说明因 BomType 是 swBomType_TopLevelOnly，才改用 BomFeature 读写配置。 | Names = swBomFeat.GetConfigurations(false, ref Visible); |
| 341 | `BorderLineWeight` | 示例在 InsertTableAnnotation2 之后、判空块内把它与 GridLineWeight 一起写成字面量 0。 | swTableAnnotation.BorderLineWeight = 0; |
| 342 | `BothDirections` | 页面只给布尔语义；示例的读序是先 AccessSelections 再读属性，末尾 ReleaseSelectionAccess。 | swSurfExtrudeFeature.AccessSelections(swModel, null); |
| 343 | `BothDirections` | 示例建双向盲拉伸时对两个方向各给一组 depth 与 end condition 参数。 | Debug.Print("  Surface extruded in both directions? " + swSurfExtrudeFeature.Bot |
| 344 | `BoundingBox` | 页面只说返回两个 IMathpoint；示例用 ArrayData 取 double[3] 的 x/y/z。 | arrData = (double[])swMathPoint.ArrayData; |
| 345 | `BoundingBox` | 示例的基准面由 InsertRefPlane 首参 8（距离）偏置 0.0889 生成，非默认面。 | swRefPlane = (RefPlane)swFeatureMgr.InsertRefPlane(8, 0.0889, 0, 0, 0, 0); |
| 346 | `BoundingEntities` | 页面 Remarks 只给文档交叉引用；示例给出读序：先 AccessSelections，读后 Release。 | boolStatus = swPlane.AccessSelections(Part, null); |
| 347 | `BoundingEntities` | 示例建面时四条边界边一律以 mark=1 选中，成员页未写该 mark。 | boolStatus = Part.Extension.SelectByID2("", "EDGE", -0.0150796523155918, 0.03306 |
| 348 | `BoundingEntities` | 页面 Returns 只说数组；示例说明元素可转成 Entity，循环上界取计数减一。 | swEnt = (Entity)vBoundEnt[i]; |
| 349 | `BoundingSketch` | 页面 Remarks 只给文档交叉引用；示例的读序是先 AccessSelections 再取该属性。 | b = swCoreFeat.AccessSelections(swModel, Nothing) |
| 350 | `BoundingSketch` | 页面 Returns 只说指向 IFeature；示例实际当作 Feature 用并取其 Name 打印。 | Debug.Print "Name of bounding sketch = " & nam |
| 351 | `BoundingSketch` | 示例的前置还要求在特征树里选中该 core 特征，页面未写此前置。 | ' 3. Select the core feature in the FeatureManager design tree. |
| 352 | `BreakAngle` | 页面 Returns 只写 Angle 无单位；示例建特征首参传 1.5707963267949 即 pi/2，再回读打印。 | swFeature = (Feature)swFeatureManager.InsertCrossBreak(1.5707963267949, 0.000635 |
| 353 | `BreakAngle` | 示例把该角度与 BreakRadius、ReverseDirection 一并打印，成员页未列这一组。 | Debug.Print("  Angle: " + swCrossBreakFeatureData.BreakAngle); |
| 354 | `BreakLinksToOriginalPart` | 示例给出成员页没写的赋值顺序：CreateDerivedConfigurations 先置 False，再置本属性，两行都在 CreateFeature 之前。 | swMirroCompFeatData.CreateDerivedConfigurations = false; |
| 355 | `BreakLinksToOriginalPart` | 示例指出 Remarks 里「opposite-hand version」具体指哪个列表：OppositeHandComponents（CTMOH）。 | swMirroCompFeatData.OppositeHandComponents = CTMOH; |
| 356 | `BreakRadius` | 示例把读取夹在 AccessSelections 与 ReleaseSelectionAccess 之间；成员页无任何调用序。 | swCrossBreakFeatureData.AccessSelections(swModel, null); |
| 357 | `BreakRadius` | 示例里 InsertCrossBreak 第 2 实参写作 0.000635（米制字面量），即该半径；成员页只写 Radius、无单位。 | swFeature = (Feature)swFeatureManager.InsertCrossBreak(1.5707963267949, 0.000635 |
| 358 | `BreakView` | Remarks 只说「拖动」重定位；示例给出程序化对应调用 IBreakLine::SetPosition。 | status = swBreakLine.SetPosition(-0.03, 0.05); |
| 359 | `BreakView` | 示例确认零参无返回，且随后用 UnBreakView 成对撤销。 | swDrawingDoc.BreakView() |
| 360 | `BufferSize` | 示例给出取得 ISwOLEObject 实例的路径：从当前选区 GetSelectedObject6(1, 0)；成员页只讲 IGetBuffer 的前置顺序。 | swOleObj = (SwOLEObject)swSelMgr.GetSelectedObject6(1, 0); |
| 361 | `BumpTextureFilename` | 示例给出写入时机：在 CreateRenderMaterial + AddEntity 之后、AddDisplayStateSpecificRenderMate | swRenderMaterial.BumpTextureFilename = fileName; |
| 362 | `BumpTextureFilename` | 示例演示同一对象上再读回该路径；Remarks 只讲 UI 上「From File」的对应关系。 | Debug.Print("  Surface finish's file name: " + swRenderMaterial.BumpTextureFilen |
| 363 | `ButtonCount` | 示例给出取 IFlyoutGroup 的路径：CreateFlyoutGroup2 建好后用 iCmdMgr.GetFlyoutGroup 按用户 ID 取，即 | Debug.Print("  Button count: " + fogrp.ButtonCount); |
| 364 | `Calculate` | 示例只传 null，完全依赖前面 SelectByID2 建立的选区；成员页虽写 if NULL 但没给配套选区做法。 | status = swMeasure.Calculate(null); |
| 365 | `Calculate` | 示例用 == -1 作为「该量不适用」的哨兵，逐项守卫后才打印；成员页与 Returns 都没提 -1。 | if ((!(swMeasure.Length == -1))) |
| 366 | `Calculate` | 返回 false 时官方给出的失败文案是「实体组合无效」；Returns 只写 false if not。 | Debug.Print("Invalid combination of selected entities."); |
| 367 | `Calculate` | 示例在 Calculate 之前显式设 ArcOption（0=中心到中心）。 | swMeasure.ArcOption = 0; |
| 368 | `CalloutString` | 示例给出具体串：两个带尖括号的符号各跟一个变量、空格分隔 | CalloutString = "<MOD-DIAM> " & StrDiam & " " & "<HOLE-DEPTH> " & strDepth |
| 369 | `CalloutText` | 示例显示只能在遍历 PMIDimensionData 的尺寸项时拿到本属性 | swPMIDataDimItem = (PMIDimensionItem)swPMIDataDim.GetDimensionItemAtIndex(k); |
| 370 | `Camera` | 返回的 Camera 可直接转成 Feature 取名字（相机本身即特征） | swFeature = (Feature)swCamera; |
| 371 | `Camera` | 同一个 null 也用作写侧开关：赋 null 即关闭相机视图 | swModelView.Camera = null; |
| 372 | `CanBeFlipped` | 示例用 Type 限定：仅 ANGLE/DISTANCE 才读 MaximumVariation/MinimumVariation | If swMateANGLE = swMate.Type Or swMateDISTANCE = swMate.Type Then |
| 373 | `CanBeFlipped` | 示例指出 GEAR 类型不允许改对齐，直接 return | // Cannot change alignment on these mate types |
| 374 | `CanConvertFormat` | 除 true 外，示例还要求当前格式是 GTOL_SW2021 才去转换 | if (lFormatType1 == (int)swGtolFormatType_e.GTOL_SW2021) |
| 375 | `CanConvertFormat` | 转换成功后文档应变脏，GetSaveFlag 应返回 True | boolstatus = swModel.GetSaveFlag(); // if successful, converted Gtol |
| 376 | `CanShowInAnnotationView` | 取某视图的标注前必须先 Activate 该视图 | swAnnView.Activate(); |
| 377 | `CanShowInAnnotationView` | 视图对象要先转成 Feature，才拿得到传入本方法的 Name | swFeat = (Feature)swAnnView; |
| 378 | `CanShowInMultipleAnnotationViews` | 示例把它紧接在逐视图 CanShowInAnnotationView 之后，作为同一标注的汇总判断 | Debug.Print("              multiple = " + swAnn.CanShowInMultipleAnnotationViews |
| 379 | `CapEnds` | 示例先调 AccessSelections 再读 CapEnds，末尾 ReleaseSelectionAccess，成员页未给调用序 | b = swCoreFeat.AccessSelections(swModel, Nothing) |
| 380 | `CapEnds` | 前置还要求在特征树中选中该特征，示例用 GetSelectedObject6 取得 Feature | Set swFeat = swSelMgr.GetSelectedObject6(1, -1) |
| 381 | `CapPlanar` | 示例给出读取时机：PostIntersect 建出 Intersect1、GetDefinition 之后才读 CapPlanar | Set featData = swFeat.GetDefinition |
| 382 | `CapPlanar` | 示例用 PreIntersect(False) 并就地注释 Do not cap，把 True/False 极性锚在“不封口”侧 | 'Do not cap planar surface openings of intersect feature |
| 383 | `Capture3DView` | 示例展示返回对象上可直接读 ModelBreakViewName、ConfigurationName 等，成员页只写“返回 IView3D” | sw3DView.ModelBreakViewName |
| 384 | `CavitySurfaces` | 示例先 AccessSelections、读完整组 CavitySurfaces 后才 ReleaseSelectionAccess，Remarks 只指向外部 | bRet = swToolingSplitFeatData.AccessSelections(swModel, Nothing) |
| 385 | `CavitySurfaces` | C# 侧把返回值 cast 成 object[] 并按 GetCavitySurfacesCount 定长索引出 Body2 | cavSurf = (object[])swToolingSplitFeatData.CavitySurfaces; |
| 386 | `CenterDistance` | 示例在 Calculate 之前先设 ArcOption，并把 0/1/2 注释为中心到中心/最小距离/最大距离 | ' 0 = center to center |
| 387 | `CenterDistance` | 示例对 CenterDistance 也先判是否等于 -1 再打印，与 Returns 的失效约定对应 | If (Not (swMeasure.CenterDistance = -1)) Then |
| 388 | `CenterFooter` | 示例先把 UsePageSetup 置为 swPageSetupInUse_Document，再取 ModelDoc.PageSetup 去写页脚 | swModelDocExt.UsePageSetup = swPageSetupInUse_e.swPageSetupInUse_Document |
| 389 | `CenterFooter` | 页脚内容由两个 GetHeaderFooterString 返回值夹一个字面分隔串拼成，成员页未说内容形态 | footerText = (footerTextNumber & " of " & footerTextCount) |
| 390 | `CenterLineFont` | 示例给出遍历序：图纸 GetFirstView/GetNextView，视图内 GetFirstCenterMark2/GetNext 后读该布尔 | swCenterMark = swView.GetFirstCenterMark2 |
| 391 | `CenterOfMass` | 返回值是米：示例乘 1000 再打印 mm，而成员页 Returns 完全没写单位 |             Debug.Print("Center of mass = (" + vCoM[0] * 1000.0 + ", " + vCoM[1] |
\| 392 \| `CenterOfMass` \| 调用序：先 AddBodies 装载实体，随即取 CenterOfMass \|             bRet = swMass.AddBodies((dispArray));

            //Get mass proper |
| 393 | `CenterOnBendLines` | 示例点明初始 ReliefType 默认为 Tear（CollectAllCorners 的实参） |            longstatus = cornerReliefFeatData.CollectAllCorners((int)swCornerReli |
| 394 | `CenteredOnBendLines` | 前置调用序：GetDefinition 后必须先 AccessSelections 才能读写该属性 |             swBreakCornerFeatureData = (BreakCornerFeatureData)swFeature.GetDefi |
| 395 | `CenteredOnBendLines` | 改完须以 ModifyDefinition 提交 |             status = swFeature.ModifyDefinition(swBreakCornerFeatureData, swMode |
| 396 | `ChamferDistance` | 单位是米：示例乘 1000 打印 mm，成员页 Returns 未写单位 | 	            Debug.Print("    Chamfer distance or fillet radius                  |
| 397 | `ChamferDistance` | 该例第3实参 BIsChamfer=false，故读到的其实是 Returns 里的 fillet radius 分支 | 	            myFeature = Part.FeatureManager.InsertEndCapFeature3(0.005, false,  |
\| 398 \| `ChamferPrecision` \| 带索引的取值：0=倒角距离小数位数，1=倒角角度小数位数 \|         indx = swDispDim.ChamferPrecision(0)

	        Debug.Print("Precision of |
| 399 | `ChamferPrecision` | 前置：显示尺寸必须是倒角尺寸（Type2=10） | 	        Debug.Print("Dimension type as defined in swDimensionType_e: " & swDisp |
\| 400 \| `ChamferType` \| 读取前置：注解类型须为 swDimXpertDimTol_ChamferDimension \|     ElseIf annoType = swDimXpertDimTol_ChamferDimension Then

        Select Cas |

（另有 3309 条，原始 JSON 在 `specs/204-*/recon/c4-rows/`）

## 四、⚠ 明确记下的限度

* ⚠ **覆盖 91%**：**48 箱未落盘**（散箱，多为个别 agent 失败）⇒
  本文件的数**是下界**，不是全量。
* ⚠ **54 条机械报出的冲突未过引文闸**（9.0%）⇒ **已全部剔除**。
  ★ 这个比例比 C1（0/131）和 C3（0/131）**高得多** —— 因为这一件要**同时**引两处原文，
  任一处抄错（或换行差异）就整条作废。
* ⚠ **「冲突」是 agent 的判断，我只机械核了引文**：两段引文都为真 **不等于** 两者真的不能同时成立
  （可能是**详略不同**而非矛盾）。⇒ **要用于判据请逐条再看一遍**。
* ⚠ **`example_more_specific` 只过了示例侧的引文闸**，没有反查成员页确认「真的没写」。
* ✅ **三裁判已齐**：V1 把真冲突估到 **220–270（~8%）**、V2 找到 **10 条反例 + 8 条漏报**、V3 指出**丢箱系统性偏向头部**与**引文闸口径依赖** ⇒ 全部留档在 §六，文件头两个数已改成有两个口径。
* ⚠ **没有改任何官方文件**（`C:\swapi\` 是只读源）。


## 六、★★ 三裁判门禁（**三件里改动最大的一件**）

**V1 审计者（DeepSeek）** 抽检 12 · **9 条判据缺陷** · **不同意 6 个数**
**V2 对抗者（Bunny）** 攻 13 · **10 条反例** + **6 条 more_specific 假阳性** + **8 条漏报**
**V3 复算者（Bunny）** 独立重算 · **5 处与报告不一致**

### 6.1 ★★ V1 最重的一击：**`544` 里只有约 1/3 是真互斥**

> V1 逐字：「抽检 12 条只有 4 条真互斥（33%）；按类加权估真冲突约 **220–270** 条，
> 「16%」宜改为**约 8%**。」

它给的判据缺陷是对的：**我的判据把「不能同时成立」放宽成了「示例没照文档做」** ——
12 条里 8 条属**漏写前置 / 建议未被遵守 / 作用域不同**，那些是**详略差异，不是矛盾**。

⇒ **本件的真冲突数应读作 220–270（约 8%），不是 544（16%）。**

### 6.2 ★★ V2 的漏报：**一整类缺陷我的流水线完全没设闸**

V2 找到 **8 条漏报**，**全部属同一类** —— **成员页 `Remarks` 回链的成员名，在同一个接口里根本不存在**
（官方笔误或改名前的残留名）。逐字样本：

| 成员 | 那一处 |
|---|---|
| `PositionOffsetDistance` | conflits=[]。Remarks 前置引 `[[IEdgeflangeFeatureData::PostionOffsetType]]`（官方笔误，缺 i），接口里不存在；示例设的是真成员 PositionOffsetType。照页面写代码必然失败，agent 只把它记成 more_speci |
| `AddComponent4` | confllicts=[]。Remarks 逐字「you can use [[IAssemblyDoc::AddComponents]] or [[IAssemblyDoc::AddComponents2]]」；IAssemblyDoc 目录只有 AddComponents.md 与 AddComp |
| `AddComponent5` | conflits=[]。同一处 ghost：Remarks 引 AddComponents2，接口无此页。agent note 只写「ConfigName 传 Default…不冲突」，没核成员名是否存在。 |
| `InsertVariablePitchHelix` | conflicts=[]。Remarks 第 2 步逐字「[[IFeatureManager::AddVariablePitchHelixFirstPitchAndDiamenter]] to add the first segment」；IFeatureManager 实际只有 AddVariab |
| `EndVariablePitchHelix` | conflits=[]。Remarks 同样引 AddVariablePitchHelixFirstPitchAndDiamenter，成员名不存在。四步调用序里的第 2 步照抄即断。 |
| `GetLength3` | conflits=[]。Remarks 逐字「The now obsolete [[ICurve::Length2]] returned the length of the base curve.」；ICurve 下只有 GetLength/GetLength2/GetLength3，无 Lengt |

★ 这一类**照页面写代码必然失败**，而它**不属于**「示例 ↔ 成员页冲突」——
它是**成员页自己的死链**（与我在 B2 里扫到的 65 条真死链同族）。
⇒ **我的四类判据里没有这一类** ⇒ **漏报**。

### 6.3 V2 的 10 条反例（7 条硬）—— 典型三种错法

| 成员 | 为什么我的「冲突」不成立 |
|---|---|
| `SetupSheet6` | 示例调用的 SetSheetsSelected 就是 Remarks 要求的那一步；页面写 SetSelectedSheets 是官方笔误。另一条 unit_diff 也反了：示例注释写「9 zones」且实参 ZoneRow=3 ZoneCol=3，正好等于 |
| `Penetration` | 示例把 Penetration 放在 Else 分支里读，即 UseRestitutionCoefficient 为假时——正是 Remarks 要求的前提。判据只按关键词命中，没看分支极性。 |
| `GetLeaderPointsAtIndex` | 示例先按引线样式算点数再 ReDim 出正确长度的数组，正是 Remarks 规定的前置；agent 引的 ReDim 行与调用行只隔 4 行，属行窗口误判。 |
| `UseDefaultBendRelief` | 被当成例证的那一行是 VBNET 里以单引号开头的注释块；生效代码只 Debug.Print 读它，而 Remarks 禁的只是「改」，不禁「读」。 |
| `UseDefaultBendAllowance` | 同上：引文是注释行，生效代码是 Initialize 的实参 + 只读回显，与 Remarks 完全一致。 |
| `ShowChildComponentsInBOM` | 引文是示例的 Preconditions 注释「Open a part…」，不是对该成员的断言；代码只读一次，而 Remarks 明写读零件配置就返回 false。 |
| `SetSheetScale` | Remarks 禁的是「导入到零件草图」即 swImportDxfDwg_ImportToPartSketch；示例用的是 ImportToExistingPart，是另一个枚举成员，页面并未禁止。属把 ExistingPart 误读成 part sketch |

三种错法：① **引的是注释行**（VBNET 里以单引号开头的注释块）；② **分支极性读反**
（示例把读操作放在 `Else` 分支里 —— 正是 Remarks 要求的前提）；③ **把方法描述句当硬前置**。

### 6.4 ★ V3 的两处口径问题

1. **丢箱是系统性的**：箱 1–420 丢 **2.4%**，箱 421–533 丢 **33.3%** ⇒
   **尾部成员根本没进过判定**，样本**偏向头部批次**。真实总体是 **3685 个不同页**（不是 3399）。
2. **引文闸 `544/54` 只在「折叠空白」口径下成立** —— **严格字节级回查得 `488/110`**。
   多出的 56 条靠折空白命中。⇒ **该闸测的是抄录保真度，不是语义矛盾。**
3. **「16%」是冲突条数 ÷ 成员数 —— 两个不同单位相除**（598 ÷ 3735）。
   按「有 ≥1 条冲突的成员」算是 **504 个（13.7% 全量 / 15.0% 已判）**。

### 6.5 V1 对 `example_more_specific` 的独立估计

> 逐字：「漏洞真实且不对称：3709 只过示例侧闸、从未回查成员页。客观下界 **129 条（3.5%）**
> 的 `what` 自称「与 Remarks 一致/印证」；**179 条（4.9%）** 的 `quote` 显著记号已全在页上；
> 手核 4 条「页未写」断言有 1 条不成立。估 **10–25%（约 400–900 条）需复核**。」

## 五、★ 作业教训：`parallel` 会被单个 hang 的 agent 阻塞整批

第 6 轮我用**一个 workflow 串行跑 7 批**（`c4-rest`）以求省事 ⇒ 它**卡在 `batch-121` 整整两轮没推进**
（`parallel` 等**所有** thunk 返回，一个 hang 锁死整批 60 路）。
⇒ **改法**：每 **30 箱一个独立 workflow job**，同时最多 2 个 ⇒
**一轮从 240 推到 485**（171 箱）。**一个 job 卡住不影响另一个。**
