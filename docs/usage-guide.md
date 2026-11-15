# 官方使用指南（usage-guide）

> 生成日期：2026-09-29 · 示例总数 **2839**
> 官方示例来源：`C:\swapi\examples\`（`2839` 个）
> 归类依据：**解析示例代码块里实际调用的 API 成员**，经反射清单反查宿主接口再映射到功能域 —— 不是按标题猜测。
>
> **本文件与 `capability-matrix.md` 的分工**：
> - `capability-matrix.md` = 有哪些成员、参数什么顺序（**接口清单**）
> - `usage-guide.md` = 这件事**官方怎么用**（**使用指南**）
>
> **本轮全部内容由静态解析生成，未启动 SolidWorks、未执行任何示例代码。**

---

## 一分钟索引：14 个域的官方示例存量

| # | 功能域 | 官方示例（强相关） | 本仓库实现 |
|---|---|---|---|
| 1 | 应用与会话 | **2368** | `scripts/sw_connect.py`（连接/模板/凭据）、`sw_session.py`、`sw_preflight.py`、`sw_addin_host.py`（Add-in 宿主）、`sw_macro_guard.py` |
| 2 | 草图 | **951** | `scripts/sw_part.py`（草图实体与约束）、`subskills/solidworks-threaded-holes` |
| 3 | 零件特征 | **971** | `scripts/sw_part.py`（extrude / revolve / fillet / chamfer / pattern / rib） |
| 4 | 孔与螺纹 | **391** | `scripts/sw_hole_features.py`、`subskills/solidworks-threaded-holes` |
| 5 | 钣金 | **434** | `scripts/sw_sheet_metal.py` —— 5 个特征：`create_base_flange` / `create_one_bend` / `create_edge_flange` / `create_swept_flange` / `create_gusset` / `create_draft` |
| 6 | 焊件 | **460** | `scripts/sw_weldment.py` |
| 7 | 曲面 | **529** | `scripts/sw_surface.py` —— 19 个 `IModeler.Create*Surface` 登记，14 个薄封装；`advanced_surface_ocp.py`（OCP 路线，非原生） |
| 8 | 装配 | **915** | `scripts/sw_assembly.py` |
| 9 | 工程图 | **902** | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`（2033 行 / 53 函数）、`scripts/drawing_spec.py` |
| 10 | 几何与拓扑 | **778** | `scripts/sw_review.py`、`sw_appearance.py`、`advanced_geometry*.py` |
| 11 | 质量属性与导出 | **14** | `scripts/sw_export.py`、`sw_delivery.py` |
| 12 | 配置·材料·自定义属性 | **382** | `scripts/sw_document_data.py`、`sw_appearance.py` |
| 13 | 仿真(需许可证) ⚠ | **0** | `scripts/sw_simulation.py` —— 入口链 / 研究 / 载荷夹具 / 求解 / 证据回读 |
| 14 | 路由/Composer/PDM ⚠ | **0** | **无**（见 §未覆盖） |

> **多标签说明**：一个示例天然横跨多个域（`Select4` 几乎每个示例都调，`GetAnnotation` 三个域都有）。故本表按「该域被该示例调用的成员数」加权统计，同一示例会在多个域下出现。

---

## 逐域明细

### 应用与会话

- **官方示例（强相关）**：2368 个
- **本仓库实现**：`scripts/sw_connect.py`（连接/模板/凭据）、`sw_session.py`、`sw_preflight.py`、`sw_addin_host.py`（Add-in 宿主）、`sw_macro_guard.py`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 38 | CSharp | `Get_and_Set_User_Preferences_Example_CSharp` | `GetUserPreferenceDouble`, `GetUserPreferenceDoubleValue`, `GetUserPreferenceInteger`, `GetUserPreferenceIntegerValue`, `GetUserPreferenceString`, `GetUserPreferenceStringValue` |
| 38 | VB | `Get_and_Set_User_Preferences_Example_VB` | `GetUserPreferenceDouble`, `GetUserPreferenceDoubleValue`, `GetUserPreferenceInteger`, `GetUserPreferenceIntegerValue`, `GetUserPreferenceString`, `GetUserPreferenceStringValue` |
| 38 | VBNET | `Get_and_Set_User_Preferences_Example_VBNET` | `GetUserPreferenceDouble`, `GetUserPreferenceDoubleValue`, `GetUserPreferenceInteger`, `GetUserPreferenceIntegerValue`, `GetUserPreferenceString`, `GetUserPreferenceStringValue` |
| 37 | CSharp | `Get_Annotations_Arrays_Example_CSharp` | `AddDimension2`, `ClearSelection2`, `CreateLine`, `GetPathName`, `InsertDatumTag2`, `InsertDatumTargetSymbol2` |
| 35 | VBNET | `Get_Annotations_Arrays_Example_VBNET` | `AddDimension2`, `ClearSelection2`, `CreateLine`, `ForceRebuild3`, `InsertDatumTargetSymbol2`, `InsertGtol` |
| 27 | CSharp | `Create_TaskPaneView_Add-in_Example_CSharp` | `AddCallback`, `CreateTaskpaneView3`, `GetActiveDisplayPane`, `GetFirstDocument`, `GetFirstModelView`, `GetNext` |
| 24 | CSharp | `Get_Corresponding_Objects_in_Assembly_Component_Example_CSharp` | `ActivateDoc3`, `ClearSelection2`, `CreateArc`, `CreateLine`, `GetCorresponding`, `GetObjectId` |
| 24 | CSharp | `Inspect_Facets_Example_CSharp` | `ClearSelection2`, `CloseDoc`, `DeSelect`, `GetApplySelectionFilter`, `GetSelectedObject6`, `GetSelectedObjectType3` |
| 23 | CSharp | `Create_Edge_Flange_Example_CSharp` | `CreateLine2`, `EditSketch`, `GetActiveSketch2`, `GetSelectedObject6`, `InsertSketch2`, `InsertSketchForEdgeFlange` |
| 22 | CSharp | `Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_CSharp` | `AddConfiguration`, `ClearSelection2`, `CloseDoc`, `GetCurrentMacroPathFolder`, `GetSelectedObject6`, `GetUserPreferenceStringValue` |
| 22 | VBNET | `Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_VBNET` | `AddConfiguration`, `ClearSelection2`, `CloseDoc`, `GetCurrentMacroPathFolder`, `GetSelectedObject6`, `GetUserPreferenceStringValue` |
| 21 | CSharp | `Create_CommandManager_Tab_and_Tab_Boxes_Example_CSharp` | `Activate`, `AddCommandItem2`, `GetCommandManager`, `GetFirstDocument`, `GetNext`, `GetTitle` |
| 21 | CSharp | `Create_Planar_Surface_Feature_Example_CSharp` | `ClearSelection2`, `CreateSelectData`, `GetPathName`, `GetSelectedObject6`, `GetType`, `InsertPlanarRefSurface` |
| 20 | CSharp | `Create_Corner_Relief_Feature_Example_CSharp` | `ClearSelection2`, `CreateLine`, `EditSketch`, `GetSelectedObject6`, `InsertSketch`, `InsertSketchForEdgeFlange` |
| 20 | VBNET | `Create_Corner_Relief_Feature_Example_VBNET` | `ClearSelection2`, `CreateLine`, `EditSketch`, `GetSelectedObject6`, `InsertSketch`, `InsertSketchForEdgeFlange` |
| 20 | VBNET | `Get_Corresponding_Objects_in_Assembly_Component_Example_VBNET` | `ActivateDoc3`, `ClearSelection2`, `CreateArc`, `CreateLine`, `GetCorresponding`, `GetObjectId` |
| 20 | VBNET | `Inspect_Facets_Example_VBNET` | `ClearSelection2`, `CloseDoc`, `DeSelect`, `GetSelectedObject6`, `GetSelectedObjectType3`, `GetSelectionFilter` |
| 19 | ? | `Create_CommandManager_Tab_and_Tab_Boxes_Example_VB.NET` | `Activate`, `AddCommandItem2`, `GetCommandManager`, `GetFirstDocument`, `GetNext`, `GetType` |
| 19 | CSharp | `Create_Face_Plane_Intersection_SSMember_Example_CSharp` | `ClearSelection2`, `CreateStructureSystem`, `CreateStructureSystemMemberData`, `GetSelectedObject6`, `InsertSketch`, `NewDocument` |
| 19 | VBNET | `Create_Face_Plane_Intersection_SSMember_Example_VBNET` | `ClearSelection2`, `CreateStructureSystem`, `CreateStructureSystemMemberData`, `GetSelectedObject6`, `InsertSketch`, `NewDocument` |
| 19 | CSharp | `Create_Radiate_Surface_Example_CSharp` | `ClearSelection2`, `CreateSelectData`, `GetPathName`, `GetSelectedObject6`, `GetType`, `InsertRadiateSurface` |
| 19 | CSharp | `Create_SM_Corner_Relief_Feature_Example_CSharp` | `ClearSelection2`, `CreateLine`, `GetSelectedObject6`, `InsertSheetMetal3dBend`, `InsertSketch`, `NewDocument` |
| 19 | CSharp | `Create_Swept_Flange_Example_CSharp` | `ClearSelection2`, `CreateLine`, `GetSelectedObject6`, `InsertSketch`, `NewDocument`, `SelectByID2` |
| 19 | CSharp | `Create_and_Convert_Non-manifold_Bodies_Example_CSharp` | `ClearSelection2`, `CreateLine`, `CreateLine2`, `GetModeler`, `GetSelectedObject6`, `Insert3DSketch2` |
| 19 | CSharp | `Save_Drawing_as_DXF_Example_CSharp` | `GetPathName`, `GetUserPreferenceDoubleValue`, `GetUserPreferenceIntegerValue`, `GetUserPreferenceStringListValue`, `GetUserPreferenceToggle`, `SaveAs4` |
| … | | *其余 2343 个见* `_raw/examples_by_domain.txt` | |

### 草图

- **官方示例（强相关）**：951 个
- **本仓库实现**：`scripts/sw_part.py`（草图实体与约束）、`subskills/solidworks-threaded-holes`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 25 | CSharp | `Create_Sketch_Path_Example_CSharp` | `CreateCircle`, `CreateLine`, `GetConstraints`, `GetLength`, `GetRelationType`, `GetRelations` |
| 20 | CSharp | `Autodimension_All_Sketches_Example_CSharp` | `AutoDimension2`, `CreateCircle`, `CreateCornerRectangle`, `GetConstrainedStatus`, `GetEndPoint2`, `GetSketchPoints2` |
| 16 | CSharp | `Create_Corner_Relief_Feature_Example_CSharp` | `CreateLine`, `GetEndPoint2`, `GetSketchSegments`, `GetStartPoint2`, `InsertSketch`, `Select2` |
| 16 | CSharp | `Insert_DXF_File_and_Add_Dimensions_Example_CSharp` | `FullyDefineSketch`, `GetEndPoint2`, `GetSketchPoints2`, `GetSketchSegments`, `GetStartPoint2`, `GetType` |
| 15 | CSharp | `Create_Ellipse_Example_CSharp` | `CreateEllipse`, `GetCenterPoint2`, `GetEllipseCount`, `GetEllipses3`, `GetEndPoint2`, `GetLength` |
| 15 | CSharp | `Get_Corresponding_Objects_in_Assembly_Component_Example_CSharp` | `CreateArc`, `CreateLine`, `GetID`, `GetSketchContours`, `GetSketchSegments`, `GetType` |
| 14 | CSharp | `Create_Edge_Flange_Example_CSharp` | `GetEndPoint2`, `GetSketchSegments`, `GetStartPoint2`, `Select2`, `Select4`, `SketchUseEdge` |
| 14 | CSharp | `Get_Sketch_Relations_Example_CSharp` | `GetDefinitionEntities2`, `GetDisplayDimension`, `GetEntities`, `GetEntitiesType`, `GetID`, `GetRelationType` |
| 13 | CSharp | `Create_Parabola_Example_CSharp` | `CreateParabola`, `CreatePoint`, `GetEndPoint2`, `GetSketchPoints2`, `GetStartPoint2`, `GetType` |
| 13 | CSharp | `Inspect_Facets_Example_CSharp` | `DeSelect`, `GetType`, `Select`, `Select2` |
| 12 | VBNET | `Exclude_Faces_Before_Flattening_Example_VBNET` | `AccessSelections`, `Select`, `Select2`, `Select3` |
| 12 | CSharp | `Get_Names_of_Sketch_Segments_Example_CSharp` | `CreatePoint`, `GetEndPoint2`, `GetID`, `GetSketch`, `GetStartPoint2`, `GetType` |
| 12 | CSharp | `Get_Properties_of_Sketch-Pattern_Feature_Example_CSharp` | `AccessSelections`, `CreateCornerRectangle`, `CreatePoint`, `GetBasePoint`, `GetPatternBodyCount`, `GetPatternFaceCount` |
| 12 | VBNET | `Inspect_Facets_Example_VBNET` | `DeSelect`, `Select`, `Select2` |
| 11 | VB | `Autodimension_All_Sketches_Example_VB` | `AutoDimension2`, `CreateCircle`, `CreateCornerRectangle`, `InsertSketch`, `Select2`, `Select4` |
| 11 | VBNET | `Autodimension_All_Sketches_Example_VBNET` | `AutoDimension2`, `CreateCircle`, `CreateCornerRectangle`, `InsertSketch`, `Select2`, `Select4` |
| 11 | VB | `Exclude_Faces_Before_Flattening_Example_VB` | `Select`, `Select2`, `Select3` |
| 11 | CSharp | `Get_Area_Hatch_Data_Example_CSharp` | `GetFace`, `GetID`, `GetSketch`, `GetSketchHatches`, `Select4` |
| 11 | VBNET | `Get_Corresponding_Objects_in_Assembly_Component_Example_VBNET` | `CreateArc`, `CreateLine`, `GetSketchContours`, `GetSketchSegments`, `InsertSketch`, `Select2` |
| 11 | CSharp | `Get_Mirror_Part_Information_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess`, `Select`, `Select2` |
| 11 | CSharp | `Get_Mirror_Pattern_Feature_Data_Example_CSharp` | `AccessSelections`, `CreateCircle`, `GetPatternFeatureCount`, `ReleaseSelectionAccess`, `Select2`, `Select4` |
| 11 | CSharp | `Get_Sketch_Arc_Data_Example_CSharp` | `CreateArc`, `GetCenterPoint2`, `GetEndPoint2`, `GetNormalVector`, `GetRadius`, `GetRotationDir` |
| 11 | CSharp | `Get_Sketch_Contours_Example_CSharp` | `GetEdges`, `GetSketchContours`, `GetSketchSegments`, `GetType`, `IsClosed`, `Select2` |
| 11 | VB | `Get_Sketch_Contours_Example_VB` | `GetEdges`, `GetSketchContours`, `GetSketchSegments`, `GetType`, `IsClosed`, `Select2` |
| 11 | VBNET | `Get_Sketch_Contours_Example_VBNET` | `GetEdges`, `GetSketchContours`, `GetSketchSegments`, `GetType`, `IsClosed`, `Select2` |
| … | | *其余 926 个见* `_raw/examples_by_domain.txt` | |

### 零件特征

- **官方示例（强相关）**：971 个
- **本仓库实现**：`scripts/sw_part.py`（extrude / revolve / fillet / chamfer / pattern / rib）

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 52 | CSharp | `Insert_Sweep_Cut_Feature_Example_CSharp` | `AccessSelections`, `GetCutSweepOption`, `GetDefinition`, `GetFeatureScopeBodiesCount`, `GetPathType`, `GetSpecificFeature` |
| 47 | CSharp | `Get_Properties_of_Sketch-Pattern_Feature_Example_CSharp` | `AccessSelections`, `CreateDefinition`, `CreateFeature`, `FeatureExtrusion2`, `GetDefinition`, `GetPatternBodyCount` |
| 42 | CSharp | `Get_Guide_Curves_in_Loft_Feature_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetGuideCurvesCount`, `GetGuideCurvesType`, `GetTypeName2`, `InsertProtrusionBlend2` |
| 41 | CSharp | `Create_and_Access_Curve-driven_Pattern_Feature_Example_CSharp` | `AccessSelections`, `CreateDefinition`, `CreateFeature`, `FeatureCut3`, `GetDefinition`, `GetPatternBodyCount` |
| 41 | CSharp | `Get_Mirror_Pattern_Feature_Data_Example_CSharp` | `AccessSelections`, `FeatureExtrusion3`, `FeatureLinearPattern4`, `GetDefinition`, `GetMirrorFaceCount`, `GetMirrorPlaneType` |
| 40 | CSharp | `Get_Edge_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetEdgeChamferDistance`, `GetEdgeCount`, `GetFaceCount`, `GetIsFlipped` |
| 39 | CSharp | `Get_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetEdgeChamferDistance`, `GetEdgeCount`, `GetFaceCount`, `GetIsFlipped` |
| 37 | CSharp | `Get_Guide_Curves_in_Sweep_Feature_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetGuideCurvesCount`, `GetGuideCurvesType`, `GetTypeName2`, `InsertProtrusionSwept4` |
| 36 | CSharp | `Create_Swept_Flange_Using_Gauge_Table_Example_CSharp` | `AccessSelections`, `CreateDefinition`, `CreateFeature`, `GetDefinition`, `InsertRefPlane`, `ModifyDefinition` |
| 36 | CSharp | `Get_Cross_Break_Feature_Data_in_Sheet_Metal_Part_Example_CSharp` | `AccessSelections`, `CreateCustomBendAllowance`, `GetDefinition`, `GetFeatures`, `GetTypeName2`, `InsertCrossBreak` |
| 36 | CSharp | `Get_Mirror_Solid_Feature_Data_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetPatternBodyCount`, `InsertMirrorFeature2`, `ReleaseSelectionAccess`, `Select` |
| 36 | VBNET | `Get_Properties_of_Sketch-Pattern_Feature_Example_VBNET` | `AccessSelections`, `CreateDefinition`, `CreateFeature`, `FeatureExtrusion2`, `GetTransform`, `ReleaseSelectionAccess` |
| 36 | CSharp | `Insert_Extruded_Reference_Surface_Example_CSharp` | `AccessSelections`, `FeatureExtruRefSurface3`, `GetDefinition`, `GetDepth`, `GetEndCondition`, `GetReverseOffset` |
| 35 | CSharp | `Create_Structural_Member_Group_Example_CSharp` | `AccessSelections`, `CreateStructuralMemberGroup`, `GetDefinition`, `InsertStructuralWeldment3`, `InsertWeldmentFeature`, `ReleaseSelectionAccess` |
| 35 | CSharp | `Get_Broken_Out_Section_Feature_Data_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetRadius`, `ModifyDefinition`, `ReleaseSelectionAccess`, `Select` |
| 35 | VBNET | `Get_Cross_Break_Feature_Data_in_Sheet_Metal_Part_Example_VBNET` | `AccessSelections`, `CreateCustomBendAllowance`, `GetDefinition`, `GetFeatures`, `InsertCrossBreak`, `InsertSheetMetalBaseFlange2` |
| 35 | VBNET | `Insert_Extruded_Reference_Surface_Example_VBNET` | `AccessSelections`, `FeatureExtruRefSurface3`, `GetDepth`, `GetEndCondition`, `GetReverseOffset`, `GetTranslateSurface` |
| 35 | CSharp | `Insert_Structural_Weldment_Example_CSharp` | `AccessSelections`, `CreateStructuralMemberGroup`, `GetDefinition`, `InsertStructuralWeldment4`, `InsertWeldmentFeature`, `ReleaseSelectionAccess` |
| 35 | CSharp | `Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_CSharp` | `AccessSelections`, `CreateStructuralMemberGroup`, `GetDefinition`, `InsertStructuralWeldment5`, `InsertWeldmentFeature`, `ReleaseSelectionAccess` |
| 35 | VBNET | `Insert_Sweep_Cut_Feature_Example_VBNET` | `AccessSelections`, `GetWallThickness`, `InsertCutSwept4`, `ReleaseSelectionAccess` |
| 35 | CSharp | `Mirror_Sheet-metal_Part_Example_CSharp` | `AccessSelections`, `GetDefinition`, `GetMirrorPlaneType`, `InsertRefPlane`, `ReleaseSelectionAccess`, `Select` |
| 34 | CSharp | `Access_Structure_System_Corner_Treatments__Example_CSharp` | `AccessSelections`, `GetCornerManagementFolders`, `GetDefinition`, `GetSpecificFeature2`, `ModifyDefinition`, `ReleaseSelectionAccess` |
| 34 | CSharp | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp` | `AccessSelections`, `FeatureExtrusion3`, `FeatureRevolve2`, `GetDefinition`, `InsertCutSwept5`, `ReleaseSelectionAccess` |
| 34 | CSharp | `Create_Extrude_Feature_Using_Sketch_Contours_Example_CSharp` | `AccessSelections`, `FeatureExtrusion3`, `GetContoursCount`, `GetDefinition`, `ReleaseSelectionAccess` |
| 34 | CSharp | `Create_Sheet_Metal_Gusset_Example_CSharp` | `AccessSelections`, `CreateDefinition`, `CreateFeature`, `GetDefinition`, `ModifyDefinition`, `ReleaseSelectionAccess` |
| … | | *其余 946 个见* `_raw/examples_by_domain.txt` | |

### 孔与螺纹

- **官方示例（强相关）**：391 个
- **本仓库实现**：`scripts/sw_hole_features.py`、`subskills/solidworks-threaded-holes`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 18 | CSharp | `Set_New_End_Condition_for_Simple_Hole_Example_CSharp` | `AccessSelections`, `GetEndConditionReference`, `ReleaseSelectionAccess`, `SetEndConditionReference` |
| 18 | VBNET | `Set_New_End_Condition_for_Simple_Hole_Example_VBNET` | `AccessSelections`, `GetEndConditionReference`, `ReleaseSelectionAccess`, `SetEndConditionReference` |
| 17 | CSharp | `Get_Hole_Series_Information_Example_CSharp` | `AccessSelections`, `GetComponents`, `GetComponentsCount`, `GetSketchPoints`, `GetSketchPointsCount`, `ReleaseSelectionAccess` |
| 14 | CSharp | `Insert_Sweep_Cut_Feature_Example_CSharp` | `AccessSelections`, `GetFeatureScopeBodiesCount`, `ReleaseSelectionAccess` |
| 13 | CSharp | `Access_Structure_System_Corner_Treatments__Example_CSharp` | `AccessSelections`, `GetFeature`, `ReleaseSelectionAccess` |
| 13 | CSharp | `Insert_Join_Feature_Example_CSharp` | `AccessSelections`, `GetComponents`, `ReleaseSelectionAccess` |
| 13 | VBNET | `Insert_Join_Feature_Example_VBNET` | `AccessSelections`, `GetComponents`, `ReleaseSelectionAccess` |
| 13 | CSharp | `Replace_Face_Example_CSharp` | `AccessSelections`, `GetFeature`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Access_and_Release_Access_to_Edges_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Access_and_Release_Access_to_Edges_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Combine_Bodies_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Combine_Bodies_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Asymmetric_Elliptic_Fillets_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Create_Asymmetric_Elliptic_Fillets_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Curvature_Continuous_Variable_Fillet_Feature_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Create_Curvature_Continuous_Variable_Fillet_Feature_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Curve_Through_Reference_Points_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Create_Curve_Through_Reference_Points_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Extrude_Feature_Using_Sketch_Contours_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Create_Extrude_Feature_Using_Sketch_Contours_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Planar_Surface_Feature_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | VBNET | `Create_Planar_Surface_Feature_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Create_Projection_Split_Line_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| … | | *其余 366 个见* `_raw/examples_by_domain.txt` | |

### 钣金

- **官方示例（强相关）**：434 个
- **本仓库实现**：`scripts/sw_sheet_metal.py` —— 5 个特征：`create_base_flange` / `create_one_bend` / `create_edge_flange` / `create_swept_flange` / `create_gusset` / `create_draft`
- ⚠ **前置**：**必须先有基体法兰**（`swFmBaseFlange`）—— 官方 `Create_Swept_Flange_Example_VBNET` 第 53 行先调 `InsertSheetMetalBaseFlange2` 再建扫掠法兰。

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 27 | CSharp | `Create_Swept_Flange_Using_Gauge_Table_Example_CSharp` | `AccessSelections`, `GetErrorCodes`, `GetGaugeTableParameters`, `ReleaseSelectionAccess`, `SetGaugeTableParameters` |
| 26 | CSharp | `Insert_Sweep_Cut_Feature_Example_CSharp` | `AccessSelections`, `GetFeatureScopeBodiesCount`, `GetPathType`, `ReleaseSelectionAccess` |
| 26 | CSharp | `Remove_Edge_from_Edge_Flange_Feature_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess`, `RemoveEdges` |
| 26 | VBNET | `Remove_Edge_from_Edge_Flange_Feature_Example_VBNET` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess`, `RemoveEdges` |
| 25 | CSharp | `Access_Structure_System_Corner_Treatments__Example_CSharp` | `AccessSelections`, `GetFeature`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Access_and_Release_Access_to_Edges_Example_CSharp` | `AccessSelections`, `GetEdgesCount`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Create_Planar_Surface_Feature_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Create_Projection_Split_Line_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Create_Radiate_Surface_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Create_Trimmed_Surface_Feature_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Create_and_Access_Curve-driven_Pattern_Feature_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Broken_Out_Section_Feature_Data_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Edge_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Fixed_Face_of_Flatten-Bends_Feature_Example_CSharp` | `AccessSelections`, `GetFixedFace`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Gusset_Feature_Data_Example_CSharp` | `AccessSelections`, `GetSupportingFaces`, `ReleaseSelectionAccess` |
| 25 | VBNET | `Get_Gusset_Feature_Data_Example_VBNET` | `AccessSelections`, `GetSupportingFaces`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Mirror_Part_Information_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Get_Mirror_Solid_Feature_Data_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Mirror_Sheet-metal_Part_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 25 | CSharp | `Replace_Face_Example_CSharp` | `AccessSelections`, `GetFeature`, `ReleaseSelectionAccess` |
| 24 | VBNET | `Access_and_Release_Access_to_Edges_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 24 | CSharp | `Combine_Bodies_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 24 | VBNET | `Combine_Bodies_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 24 | CSharp | `Create_Asymmetric_Elliptic_Fillets_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| … | | *其余 409 个见* `_raw/examples_by_domain.txt` | |

### 焊件

- **官方示例（强相关）**：460 个
- **本仓库实现**：`scripts/sw_weldment.py`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 21 | CSharp | `Insert_Weld_Symbol_Example_CSharp` | `GetArcCount`, `GetArrowHeadCount`, `GetContour`, `GetFieldWeld`, `GetLeaderCount`, `GetLineCount` |
| 13 | CSharp | `Access_Structure_System_Corner_Treatments__Example_CSharp` | `AccessSelections`, `GetFeature`, `GetProfileGroupFoldersCount`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Replace_Face_Example_CSharp` | `AccessSelections`, `GetFeature`, `ReleaseSelectionAccess` |
| 10 | CSharp | `Create_Path_Segment_SSMember_Example_CSharp` | `GetFeature`, `GetProfileGroupFolders`, `GetProfileGroupFoldersCount`, `GetSplitMember`, `GetStructureSystemMemberCount`, `GetStructureSystemMembers` |
| 10 | CSharp | `Insert_Cosmetic_Weld_Bead_Using_Geometric_Entities_Example_CSharp` | `AccessSelections`, `GetEntitiesWeldFrom`, `GetEntitiesWeldTo`, `ReleaseSelectionAccess` |
| 10 | VBNET | `Insert_Cosmetic_Weld_Bead_Using_Geometric_Entities_Example_VBNET` | `AccessSelections`, `GetEntitiesWeldFrom`, `GetEntitiesWeldTo`, `ReleaseSelectionAccess` |
| 9 | CSharp | `Get_Heal_Edges_Feature_Data_Example_CSharp` | `AccessSelections`, `GetFacesCount`, `ReleaseSelectionAccess` |
| 9 | CSharp | `Insert_and_Access_Fold_Feature_Example_CSharp` | `AccessSelections`, `GetBody`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Access_and_Release_Access_to_Edges_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Access_and_Release_Access_to_Edges_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Combine_Bodies_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Combine_Bodies_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Create_Asymmetric_Elliptic_Fillets_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Create_Asymmetric_Elliptic_Fillets_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Create_Curvature_Continuous_Variable_Fillet_Feature_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Create_Curvature_Continuous_Variable_Fillet_Feature_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Create_Curve_Through_Reference_Points_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Create_Curve_Through_Reference_Points_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Create_Extrude_Feature_Using_Sketch_Contours_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Create_Extrude_Feature_Using_Sketch_Contours_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | CSharp | `Create_Face_Plane_Intersection_SSMember_Example_CSharp` | `GetFeature`, `GetProfileGroupFolders`, `GetProfileGroupFoldersCount`, `GetStructureSystemMemberCount`, `GetStructureSystemMembers` |
| 8 | CSharp | `Create_Planar_Surface_Feature_Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| 8 | VBNET | `Create_Planar_Surface_Feature_Example_VBNET` | `AccessSelections`, `ReleaseSelectionAccess` |
| … | | *其余 435 个见* `_raw/examples_by_domain.txt` | |

### 曲面

- **官方示例（强相关）**：529 个
- **本仓库实现**：`scripts/sw_surface.py` —— 19 个 `IModeler.Create*Surface` 登记，14 个薄封装；`advanced_surface_ocp.py`（OCP 路线，非原生）

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 24 | CSharp | `Create_Trimmed_Surface_Feature_Example_CSharp` | `AccessSelections`, `CreateLine`, `GetPiecesToKeepCount`, `GetTrimToolsCount`, `GetType`, `ReleaseSelectionAccess` |
| 23 | CSharp | `Create_Planar_Surface_Feature_Example_CSharp` | `AccessSelections`, `GetBoundingEntitiesCount`, `GetRadiatedEntitiesCount`, `GetType`, `ReleaseSelectionAccess` |
| 22 | CSharp | `Create_Projection_Split_Line_Example_CSharp` | `AccessSelections`, `CreateEllipse`, `GetType`, `ReleaseSelectionAccess` |
| 22 | CSharp | `Create_Radiate_Surface_Example_CSharp` | `AccessSelections`, `GetRadiatedEntitiesCount`, `GetType`, `ReleaseSelectionAccess` |
| 22 | CSharp | `Get_Guide_Curves_in_Sweep_Feature_Example_CSharp` | `AccessSelections`, `CreateEllipse`, `CreateLine`, `ReleaseSelectionAccess` |
| 22 | VBNET | `Get_Guide_Curves_in_Sweep_Feature_Example_VBNET` | `AccessSelections`, `CreateEllipse`, `CreateLine`, `ReleaseSelectionAccess` |
| 22 | CSharp | `Get_Offset_Surface_Data_Example_CSharp` | `AccessSelections`, `GetEntitiesCount`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Create_Curvature_Continuous_Variable_Fillet_Feature_Example_CSharp` | `AccessSelections`, `CreateLine`, `ReleaseSelectionAccess` |
| 21 | VBNET | `Create_Curvature_Continuous_Variable_Fillet_Feature_Example_VBNET` | `AccessSelections`, `CreateLine`, `ReleaseSelectionAccess` |
| 21 | VBNET | `Create_Projection_Split_Line_Example_VBNET` | `AccessSelections`, `CreateEllipse`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Create_Swept_Flange_Using_Gauge_Table_Example_CSharp` | `AccessSelections`, `CreateLine`, `ReleaseSelectionAccess` |
| 21 | VBNET | `Create_Trimmed_Surface_Feature_Example_VBNET` | `AccessSelections`, `CreateLine`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Create_and_Access_Curve-driven_Pattern_Feature_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Get_Broken_Out_Section_Feature_Data_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Get_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Get_Edge_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Get_Heal_Edges_Feature_Data_Example_CSharp` | `AccessSelections`, `GetFacesCount`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Get_Mirror_Part_Information_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Get_Mirror_Solid_Feature_Data_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Merge_Arc_Segment_Bodies_With_Adjacent_Bodies_Example_CSharp` | `AccessSelections`, `CreateLine`, `ReleaseSelectionAccess` |
| 21 | VBNET | `Merge_Arc_Segment_Bodies_With_Adjacent_Bodies_Example_VBNET` | `AccessSelections`, `CreateLine`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Mirror_Sheet-metal_Part_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess` |
| 21 | CSharp | `Remove_Edge_from_Edge_Flange_Feature_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess` |
| 21 | VBNET | `Remove_Edge_from_Edge_Flange_Feature_Example_VBNET` | `AccessSelections`, `GetEdgeCount`, `ReleaseSelectionAccess` |
| 20 | CSharp | `Access_Structure_System_Corner_Treatments__Example_CSharp` | `AccessSelections`, `ReleaseSelectionAccess` |
| … | | *其余 504 个见* `_raw/examples_by_domain.txt` | |

### 装配

- **官方示例（强相关）**：915 个
- **本仓库实现**：`scripts/sw_assembly.py`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 13 | CSharp | `Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_CSharp` | `AddComponent5`, `AddConcentricMateWithTolerance`, `AddMate5`, `EditConcentricMate`, `GetConcentricAlignmentType`, `GetCurrentMisalignedDeviation` |
| 10 | CSharp | `Insert_Join_Feature_Example_CSharp` | `AccessSelections`, `EditPart2`, `GetComponents`, `GetMateEntityCount`, `GetMates`, `InsertJoin2` |
| 8 | VBNET | `Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VBNET` | `AddComponent5`, `AddConcentricMateWithTolerance`, `AddMate5`, `EditConcentricMate`, `SetConcentricAlignmentType`, `SetMaximumMisalignedDeviation` |
| 8 | VBNET | `Insert_Join_Feature_Example_VBNET` | `AccessSelections`, `EditPart2`, `GetComponents`, `GetMates`, `InsertJoin2`, `InsertNewPart2` |
| 8 | CSharp | `Suppress_Component_Feature_Example_CSharp` | `EditAssembly`, `EditPart2`, `FeatureByName`, `GetEditTarget`, `GetPathName`, `GetType` |
| 7 | CSharp | `Add_Multibody_Part_Explode_Step_Example_CSharp` | `CreateExplodedView`, `GetBodies`, `GetConfigurationNames`, `GetExplodedViewConfigurationName`, `GetExplodedViewNames`, `ShowExploded` |
| 7 | CSharp | `Autodimension_All_Sketches_Example_CSharp` | `FeatureByName`, `FirstFeature`, `GetConstrainedStatus`, `GetType`, `Select2`, `Select4` |
| 7 | CSharp | `Edit_Mate_Example_CSharp` | `EditMate3`, `GetMateEntityCount`, `GetPathName`, `MateEntity`, `Select2`, `Select4` |
| 7 | CSharp | `Get_Hole_Series_Information_Example_CSharp` | `AccessSelections`, `FirstFeature`, `GetComponents`, `GetPathName`, `ReleaseSelectionAccess`, `Select4` |
| 6 | CSharp | `Create_Exploded_Views_Example_CSharp` | `CreateExplodedView`, `GetExplodedViewCount`, `GetExplodedViewNames`, `ShowExploded2`, `ViewCollapseAssembly`, `ViewExplodeAssembly` |
| 6 | CSharp | `Get_Corresponding_Objects_in_Assembly_Component_Example_CSharp` | `AddComponent5`, `GetCorresponding`, `GetID`, `GetPathName`, `GetType`, `Select2` |
| 6 | CSharp | `Inspect_Facets_Example_CSharp` | `DeSelect`, `GetBodies2`, `GetBody`, `GetType`, `Select`, `Select2` |
| 6 | CSharp | `Remove_Material_From_Bodies_Example_CSharp` | `GetBodies2`, `GetChildren`, `GetConfigurationNames`, `GetPathName`, `GetType`, `RemoveMaterialProperty` |
| 5 | CSharp | `Activate_Smart_Features_in_an_Assembly_Example_CSharp` | `GetComponents`, `GetSmartComponentData`, `IsSmartComponent`, `SetSmartComponentData` |
| 5 | CSharp | `Add_and_Edit_Distance_Mate_Example_CSharp` | `AddComponent5`, `AddDistanceMate`, `EditDistanceMate`, `Select2`, `Select4` |
| 5 | VBNET | `Add_and_Edit_Distance_Mate_Example_VBNET` | `AddComponent5`, `AddDistanceMate`, `EditDistanceMate`, `Select2`, `Select4` |
| 5 | VB | `Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB` | `AddComponent5`, `AddConcentricMateWithTolerance`, `AddMate5`, `SetConcentricAlignmentType`, `SetTransformAndSolve2` |
| 5 | CSharp | `Get_Component_State_Example_CSharp` | `GetID`, `GetPathName`, `GetSuppression`, `IsFixed`, `IsHidden` |
| 5 | CSharp | `Get_Component_from_Feature_Example_CSharp` | `GetComponent`, `GetPathName`, `GetType`, `Select2`, `Select4` |
| 5 | CSharp | `Get_Corresponding_Entities_Between_Parts_and_Views_Example_CSharp` | `FeatureByName`, `GetCorresponding`, `GetCorrespondingEntity`, `Select4` |
| 5 | VB | `Get_Corresponding_Entities_Between_Parts_and_Views_Example_VB` | `FeatureByName`, `GetCorresponding`, `GetCorrespondingEntity`, `Select4` |
| 5 | VBNET | `Get_Corresponding_Entities_Between_Parts_and_Views_Example_VBNET` | `FeatureByName`, `GetCorresponding`, `GetCorrespondingEntity`, `Select4` |
| 5 | CSharp | `Get_Exploded_Views_for_Configuration_Example_CSharp` | `CreateExplodedView`, `GetExplodedViewConfigurationName`, `GetExplodedViewCount2`, `GetExplodedViewNames2`, `ShowExploded2` |
| 5 | VBNET | `Get_Exploded_Views_for_Configuration_Example_VBNET` | `CreateExplodedView`, `GetExplodedViewConfigurationName`, `GetExplodedViewCount2`, `GetExplodedViewNames2`, `ShowExploded2` |
| 5 | CSharp | `Get_Mates_Example_CSharp` | `GetComponents`, `GetMateEntityCount`, `GetMates` |
| … | | *其余 890 个见* `_raw/examples_by_domain.txt` | |

### 工程图

- **官方示例（强相关）**：902 个
- **本仓库实现**：`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`（2033 行 / 53 函数）、`scripts/drawing_spec.py`
- ⚠ **前置**：**必须先有已建好的工程图文档**；视图类接口挂在 `IDrawingDoc` 上，按名取页用参数化属性 `Sheet`（官方 getter 为 `get_Sheet(String)`，**不是** `GetSheet`）。

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 29 | CSharp | `Get_Annotations_Arrays_Example_CSharp` | `ActivateSheet`, `Create3rdAngleViews2`, `CreateDrawViewFromModelView3`, `ForceRebuild`, `GetAnnotation`, `GetCurrentSheet` |
| 23 | CSharp | `Modify_and_Reload_Sheet_Format_Template_Example_CSharp` | `ActivateSheet`, `EditSheet`, `EditTemplate`, `GetAnnotation`, `GetCurrentSheet`, `GetName` |
| 20 | CSharp | `Get_Weld_Bead_End_Treatment_Symbol_Data_Example_CSharp` | `GetAnnotation`, `GetArcCount`, `GetCurrentSheet`, `GetDisplayData`, `GetFirstView`, `GetFirstWeldBead` |
| 18 | CSharp | `Get_Multi-jog_Leader_Data_Example_CSharp` | `GetAnnotation`, `GetArrowHeadCount`, `GetCurrentSheet`, `GetFirstMultiJogLeader2`, `GetFirstView`, `GetLineAtIndex` |
| 16 | CSharp | `Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp` | `Activate`, `ActivateView`, `AddControl2`, `CreateFeatureMgrWindowFromHandlex64`, `DisplayWindowFromHandlex64`, `GetNext` |
| 16 | VBNET | `Add_.NET_Controls_to_SolidWorks_Using_an_Add-in_Example_VBNET` | `Activate`, `ActivateView`, `AddControl2`, `CreateFeatureMgrWindowFromHandlex64`, `DisplayWindowFromHandlex64`, `GetNext` |
| 16 | CSharp | `Create_Flyouts_in_the_CommandManager_Example_CSharp` | `Activate`, `GetNext`, `GetType`, `Show`, `Sort` |
| 16 | VBNET | `Create_Flyouts_in_the_CommandManager_Example_VBNET` | `Activate`, `GetNext`, `GetType`, `Show`, `Sort` |
| 16 | CSharp | `Get_Centerlines_in_Drawing_Example_CSharp` | `ActivateView`, `GetAnnotation`, `GetFirstCenterLine`, `GetFirstView`, `GetName`, `GetName2` |
| 16 | CSharp | `Get_Dimension_Values_in_Drawing_Example_CSharp` | `GetAnnotation`, `GetDimension`, `GetFirstDisplayDimension5`, `GetFirstView`, `GetName`, `GetNext3` |
| 15 | CSharp | `Get_Centers_of_Mass_in_Drawing_Views_Example_CSharp` | `GetAnnotation`, `GetFirstCenterOfMass`, `GetName`, `GetName2`, `GetNext`, `GetViewCount` |
| 14 | CSharp | `Get_Corresponding_Objects_in_Assembly_Component_Example_CSharp` | `GetAnnotation`, `GetCorresponding`, `GetID`, `GetType`, `Select2`, `SetLeader3` |
| 14 | VBNET | `Modify_and_Reload_Sheet_Format_Template_Example_VBNET` | `ActivateSheet`, `EditSheet`, `EditTemplate`, `GetSheetNames`, `GetTemplateName`, `GetTextFormat` |
| 14 | CSharp | `Select_All_Center_Marks_Example_CSharp` | `GetAnnotation`, `GetFirstCenterMark2`, `GetFirstView`, `GetName`, `GetNext`, `GetNextView` |
| 13 | VBNET | `Add_Button_to_Context-sensitive_Menu_Example_VBNET` | `GetNext`, `GetType`, `Show`, `Sort` |
| 13 | VBNET | `Add_Menu_and_Menu_Item_Example_VBNET` | `GetNext`, `GetType`, `Show`, `Sort` |
| 13 | CSharp | `Add_Toolbars_Example_CSharp` | `GetNext`, `GetType`, `Show`, `Sort` |
| 13 | VBNET | `Add_Toolbars_Example_VBNET` | `GetNext`, `GetType`, `Show`, `Sort` |
| 13 | CSharp | `Get_Patterned_Cosmetic_Thread_Annotations_Data_Example_CSharp` | `GetAnnotation`, `GetFirstCThread`, `GetFirstView`, `GetName`, `GetNext`, `GetNextView` |
| 13 | VB | `Get_Patterned_Cosmetic_Thread_Annotations_Data_Example_VB` | `GetAnnotation`, `GetFirstCThread`, `GetFirstView`, `GetName`, `GetNext`, `GetNextView` |
| 13 | VBNET | `Get_Patterned_Cosmetic_Thread_Annotations_Data_Example_VBNET` | `GetAnnotation`, `GetFirstCThread`, `GetFirstView`, `GetName`, `GetNext`, `GetNextView` |
| 13 | CSharp | `Get_Total_Columns_Rows_Example_CSharp` | `GetAnnotation`, `GetFirstTableAnnotation`, `GetFirstView`, `GetName`, `GetNext`, `GetNextView` |
| 13 | VB | `Get_Weld_Bead_End_Treatment_Symbol_Data_Example_VB` | `GetAnnotation`, `GetDisplayData`, `GetFirstWeldBead`, `GetNext` |
| 13 | VBNET | `Get_Weld_Bead_End_Treatment_Symbol_Data_Example_VBNET` | `GetAnnotation`, `GetDisplayData`, `GetFirstWeldBead`, `GetNext` |
| 12 | CSharp | `Create_CommandManager_Tab_and_Tab_Boxes_Example_CSharp` | `Activate`, `GetNext`, `GetType`, `Show` |
| … | | *其余 877 个见* `_raw/examples_by_domain.txt` | |

### 几何与拓扑

- **官方示例（强相关）**：778 个
- **本仓库实现**：`scripts/sw_review.py`、`sw_appearance.py`、`advanced_geometry*.py`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 20 | VB | `Get_Set_And_Remove_Tracking_IDs_On_Body_Example_VB` | `GetTrackingIDs`, `GetTrackingIDsCount`, `RemoveTrackingID`, `SetTrackingID` |
| 20 | VB | `Get_Set_And_Remove_Tracking_IDs_On_Edge_Example_VB` | `GetTrackingIDs`, `GetTrackingIDsCount`, `RemoveTrackingID`, `SetTrackingID` |
| 20 | VB | `Get_Set_And_Remove_Tracking_IDs_On_Face_Example_VB` | `GetTrackingIDs`, `GetTrackingIDsCount`, `RemoveTrackingID`, `SetTrackingID` |
| 20 | VB | `Get_Set_And_Remove_Tracking_IDs_On_Vertex_Example_VB` | `GetTrackingIDs`, `GetTrackingIDsCount`, `RemoveTrackingID`, `SetTrackingID` |
| 20 | CSharp | `Select_Edges_of_All_Holes_on_Face_Example_CSharp` | `Evaluate`, `FaceInSurfaceSense`, `GetCurve`, `GetCurveParams`, `GetEdgeCount`, `GetEdges` |
| 17 | CSharp | `Fill_Holes_in_Part_Example_CSharp` | `Copy`, `GetCurve`, `GetEdges`, `GetFirstFace`, `GetFirstLoop`, `GetNext` |
| 17 | CSharp | `Get_Sketch_Regions_Example_CSharp` | `GetEdgeCount`, `GetEdges`, `GetFirstLoop`, `GetNext`, `GetPoint`, `GetVertexCount` |
| 17 | VB | `Get_Sketch_Regions_Example_VB` | `GetEdgeCount`, `GetEdges`, `GetFirstLoop`, `GetNext`, `GetPoint`, `GetVertexCount` |
| 17 | VBNET | `Get_Sketch_Regions_Example_VBNET` | `GetEdgeCount`, `GetEdges`, `GetFirstLoop`, `GetNext`, `GetPoint`, `GetVertexCount` |
| 17 | CSharp | `Get_UV_Parameters_For_XYZ_Location_Example_CSharp` | `Evaluate`, `GetCurve`, `GetCurveParams2`, `GetEdges`, `GetFirstFace`, `GetNextFace` |
| 13 | CSharp | `Get_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `GetEdges`, `GetFaceCount`, `ReleaseSelectionAccess` |
| 12 | CSharp | `Inspect_Facets_Example_CSharp` | `DeSelect`, `GetBody`, `GetGraphicsBody`, `GetMeshBody`, `GetType`, `IsGraphicsBody` |
| 11 | CSharp | `Create_Imported_Surface_Body_from_Sketch_Example_CSharp` | `CreateBodyFromSurfaces`, `CreateTrimmedSurface`, `GetClosestPointOn`, `GetType`, `IAddProfileArc`, `IAddProfileLine` |
| 11 | CSharp | `Create_and_Convert_Non-manifold_Bodies_Example_CSharp` | `Copy`, `Display2`, `GetFirstFace`, `GetNextFace`, `GetTessellation`, `Hide` |
| 11 | CSharp | `Get_Loops_Example_CSharp` | `GetEdgeCount`, `GetFirstLoop`, `GetLoopCount`, `GetNext`, `GetVertexCount`, `IsOuter` |
| 10 | CSharp | `Get_Faces_Affected_by_Feature_Example_CSharp` | `Display`, `GetEdgeCount`, `GetEdges` |
| 10 | CSharp | `Get_Maximum_Edge_and_Vertex_Gaps_Example_CSharp` | `GetEdges`, `GetSelectionId`, `GetType`, `GetVertices`, `IsTolerant` |
| 10 | CSharp | `Insert_Boundary_Feature_Example_CSharp` | `AccessSelections`, `GetCurvesCount`, `GetDirectionVector`, `GetDraftAngle`, `GetDraftAngleReverseDirection`, `GetGuideTangencyType` |
| 9 | CSharp | `Delete_Blended_Faces_Example_CSharp` | `Copy`, `DeleteBlends3`, `FindAttribute`, `GetFirstFace`, `GetNextFace`, `IsTemporaryBody` |
| 9 | CSharp | `Get_Edge_Chamfer_Distances_Example_CSharp` | `AccessSelections`, `GetEdgeCount`, `GetFaceCount`, `ReleaseSelectionAccess` |
| 9 | CSharp | `Get_Mirror_Part_Information_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess`, `Select`, `Select2` |
| 9 | VBNET | `Insert_Boundary_Feature_Example_VBNET` | `AccessSelections`, `GetCurvesCount`, `GetDirectionVector`, `GetDraftAngle`, `GetDraftAngleReverseDirection`, `GetGuideTangencyType` |
| 9 | CSharp | `Mirror_Sheet-metal_Part_Example_CSharp` | `AccessSelections`, `GetType`, `ReleaseSelectionAccess`, `Select`, `Select2` |
| 9 | CSharp | `Return_Untrimmed_Curve_Example_CSharp` | `CreateTrimmedCurve2`, `Evaluate`, `Evaluate2`, `GetEndParams`, `GetSurface`, `GetTessPts` |
| 8 | CSharp | `Check_Edges_for_Faults_Example_CSharp` | `Check`, `Check2`, `GetEdges`, `GetSelectionId`, `GetType` |
| … | | *其余 753 个见* `_raw/examples_by_domain.txt` | |

### 质量属性与导出

- **官方示例（强相关）**：14 个
- **本仓库实现**：`scripts/sw_export.py`、`sw_delivery.py`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 9 | CSharp | `Get_Mass_Properties_Using_IMassProperty_Example_CSharp` | `GetMomentOfInertia`, `GetOverrideOptions`, `Recalculate`, `SetOverrideMassValue`, `SetOverrideMomentsOfInertiaValue`, `SetOverrideOptions` |
| 7 | VBNET | `Get_Mass_Properties_Using_IMassProperty_Example_VBNET` | `GetMomentOfInertia`, `SetOverrideMassValue`, `SetOverrideMomentsOfInertiaValue`, `SetOverrideOptions` |
| 6 | CSharp | `Add_and_Remove_Files_from_Pack_and_Go_Example_CSharp` | `AddExternalDocuments`, `GetDocumentNames`, `GetDocumentNamesCount`, `RemoveExternalDocuments`, `SetDocumentSaveToNames`, `SetSaveToName2` |
| 5 | VB | `Add_and_Remove_Files_from_Pack_and_Go_Example_VB` | `AddExternalDocuments`, `GetDocumentNames`, `RemoveExternalDocuments`, `SetDocumentSaveToNames`, `SetSaveToName2` |
| 5 | VBNET | `Add_and_Remove_Files_from_Pack_and_Go_Example_VBNET` | `AddExternalDocuments`, `GetDocumentNames`, `RemoveExternalDocuments`, `SetDocumentSaveToNames`, `SetSaveToName2` |
| 4 | VB | `Get_Mass_Properties_using_MassProperty_Object_Example_VB` | `GetMomentOfInertia`, `SetOverrideMassValue` |
| 4 | CSharp | `Pack_and_Go_an_Assembly_Example_CSharp` | `GetDocumentNames`, `GetDocumentNamesCount`, `GetDocumentSaveToNames`, `SetSaveToName` |
| 3 | CSharp | `Get_Mass_Properties_of_Multibody_Assembly_Component_Example_CSharp` | `AddBodies`, `GetMomentOfInertia` |
| 3 | VB | `Get_Mass_Properties_of_Multibody_Assembly_Component_Example_VB` | `AddBodies`, `GetMomentOfInertia` |
| 3 | VBNET | `Get_Mass_Properties_of_Multibody_Assembly_Component_Example_VBNET` | `AddBodies`, `GetMomentOfInertia` |
| 3 | CSharp | `Pack_and_Go_Part_and_Linked_Equation_Example_CSharp` | `GetDocumentNames`, `SetDocumentSaveToNames`, `SetSaveToName` |
| 3 | ? | `Pack_and_Go_Part_and_Linked_Equation_Example_vb` | `GetDocumentNames`, `SetDocumentSaveToNames`, `SetSaveToName` |
| 3 | ? | `Pack_and_Go_Part_and_Linked_Equation_Example_vbnet` | `GetDocumentNames`, `SetDocumentSaveToNames`, `SetSaveToName` |
| 3 | VBNET | `Pack_and_Go_an_Assembly_Example_VBNET` | `GetDocumentNames`, `GetDocumentSaveToNames`, `SetSaveToName` |

### 配置·材料·自定义属性

- **官方示例（强相关）**：382 个
- **本仓库实现**：`scripts/sw_document_data.py`、`sw_appearance.py`

| 命中 | 语言 | 官方示例 | 关键成员 |
|---|---|---|---|
| 10 | CSharp | `Get_Design_Table_Example_CSharp` | `Attach`, `Detach`, `GetColumnCount`, `GetEntryText`, `GetRowCount`, `GetTitle` |
| 8 | CSharp | `Get_Custom_Properties_for_Configuration_Example_CSharp` | `Add3`, `Delete2`, `Get6`, `GetAll3`, `GetType2`, `IsCustomPropertyEditable` |
| 8 | VB | `Get_Custom_Properties_for_Configuration_Example_VB` | `Add3`, `Delete2`, `Get6`, `GetAll3`, `GetType2`, `IsCustomPropertyEditable` |
| 8 | VBNET | `Get_Custom_Properties_for_Configuration_Example_VBNET` | `Add3`, `Delete2`, `Get6`, `GetAll3`, `GetType2`, `IsCustomPropertyEditable` |
| 5 | VB | `Add_and_Get_Custom_Properties_Example_VB` | `Add3`, `Get`, `GetType` |
| 5 | CSharp | `Create_CommandManager_Tab_and_Tab_Boxes_Example_CSharp` | `Add`, `GetTitle`, `GetType` |
| 5 | CSharp | `Delete_Attribute_Example_CSharp` | `Delete`, `GetName`, `SetDoubleValue2`, `SetStringValue2` |
| 5 | CSharp | `Get_Component_IDs_Example_CSharp` | `GetChildren`, `GetID`, `GetRootComponent3`, `GetType` |
| 5 | CSharp | `Get_Mirror_Part_Information_Example_CSharp` | `GetTitle`, `GetType`, `Select`, `Select2` |
| 5 | CSharp | `Mirror_Sheet-metal_Part_Example_CSharp` | `GetTitle`, `GetType`, `Select`, `Select2` |
| 4 | CSharp | `Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp` | `Add`, `GetType` |
| 4 | VBNET | `Add_.NET_Controls_to_SolidWorks_Using_an_Add-in_Example_VBNET` | `Add`, `GetType` |
| 4 | CSharp | `Add_Button_to_Context-sensitive_Menu_Example_CSharp` | `Add`, `GetType` |
| 4 | VBNET | `Add_Button_to_Context-sensitive_Menu_Example_VBNET` | `Add`, `GetType` |
| 4 | VB | `Add_Equation_And_Evaluate_All_Example_VB` | `Add2`, `Delete` |
| 4 | CSharp | `Add_Menu_and_Menu_Item_Example_CSharp` | `Add`, `GetType` |
| 4 | VBNET | `Add_Menu_and_Menu_Item_Example_VBNET` | `Add`, `GetType` |
| 4 | CSharp | `Add_Toolbars_Example_CSharp` | `Add`, `GetType` |
| 4 | VBNET | `Add_Toolbars_Example_VBNET` | `Add`, `GetType` |
| 4 | ? | `Create_CommandManager_Tab_and_Tab_Boxes_Example_VB.NET` | `Add`, `GetType` |
| 4 | CSharp | `Create_Ellipse_Example_CSharp` | `GetCenterPoint2`, `GetType`, `Select2` |
| 4 | CSharp | `Create_Flyouts_in_the_CommandManager_Example_CSharp` | `Add`, `GetType` |
| 4 | VBNET | `Create_Flyouts_in_the_CommandManager_Example_VBNET` | `Add`, `GetType` |
| 4 | CSharp | `Create_Imported_Surface_Body_from_Sketch_Example_CSharp` | `Add`, `GetType` |
| 4 | CSharp | `Create_TaskPaneView_Add-in_Example_CSharp` | `Add`, `GetType` |
| … | | *其余 357 个见* `_raw/examples_by_domain.txt` | |

### 仿真(需许可证)

- **官方示例（强相关）**：0 个
- **本仓库实现**：`scripts/sw_simulation.py` —— 入口链 / 研究 / 载荷夹具 / 求解 / 证据回读
- ⚠ **前置**：**必须先加载 Simulation 加载项**并取到 `CosmosWorks`（挂在 `ICwAddincallback` 上，属性名首字母大写）。

> ⚠ **该域在 `C:\swapi\examples` 中没有任何示例。**官方示例集只覆盖 sldworks 等 12 个程序集，而该域对应的程序集（cosworks / SWRoutingLib / sldcostingapi）**不在收录范围内** —— 这与 `capability-matrix.md` 记录的「两套官方源同时失效」是同一个根因。

### 路由/Composer/PDM

- **官方示例（强相关）**：0 个
- **本仓库实现**：**无**（见 §未覆盖）

> ⚠ **该域在 `C:\swapi\examples` 中没有任何示例。**官方示例集只覆盖 sldworks 等 12 个程序集，而该域对应的程序集（cosworks / SWRoutingLib / sldcostingapi）**不在收录范围内** —— 这与 `capability-matrix.md` 记录的「两套官方源同时失效」是同一个根因。

---

## 专题 · 域 7 曲面的两条互补路线（读官方示例才看得出来）

曲面域的官方示例几乎全部演示**路线 B**，而脚本能直接调的只有**路线 A**。
只查接口清单会漏掉这个区分，故单列。

### 路线 A · 脚本直接造几何曲面

`ISldWorks.GetModeler()` → `IModeler` 的 19 个非指针 `Create*Surface`
（平面 / 圆柱 / 球 / 圆锥 / 圆环 / 偏置 / 拉伸 / 旋转 / 直纹 / 扫掠 /
B 样条 / Coons / 加厚 / Loft / 由边成面）。

**本仓库实现**：`scripts/sw_surface.py`

### 路线 B · 界面创建 + 脚本参数化

```vbnet
swFeat = (Feature)swFeatureMgr.PostTrimSurface(true)          ' 唯一有脚本入口的
surfTrimFeatData = (SurfaceTrimFeatureData)swFeat.GetDefinition()
surfTrimFeatData.AccessSelections(swModel, Nothing)
... 读 / 改属性 ...
surfTrimFeatData.ReleaseSelectionAccess()
```

Radiate / Planar / Extend / Knit / Fill 等**没有脚本创建入口**——
官方示例一律是「用户在界面里 Insert ▸ Surface 建好，脚本再用 `GetDefinition()` 取回参数化」。

依据：扫描 `IFeatureManager` 全部 263 个方法，曲面类 `Post*` **只有** `PostTrimSurface` 一个。

> ⚑ **更正记录**：本项目早前依据「无任何接口返回 `ISurface*FeatureData`」
> 判定它们「不是创建入口」——这结论对；但由此推断「官方不用它们」是错的。
> 官方示例（`Create_Radiate_Surface_Example_CSharp`、
> `Create_Planar_Surface_Feature_Example_CSharp`、
> `Create_Trimmed_Surface_Feature_Example_CSharp`、`Access_Selections_Example_VB`）
> 证明它们是**路线 B 的载体**。

---

## 未被官方示例覆盖的域（与 A1 的「不覆盖+原因」对应）

| 域 | 官方示例 | 本仓库 | 原因 |
|---|---|---|---|
| 仿真(需许可证) | **0** | `scripts/sw_simulation.py`（部分） | `C:\swapi` 只收录 12 个程序集，**不含 cosworks**；CHM `cosworks` 册是 JS 空壳。两个官方源同时失效 ⇒ 84 个接口里只有 7 个载荷方法拿得到签名。 |
| 路由/Composer/PDM | **0** | **无** | 同上（SWRoutingLib / sldcostingapi / swdocumentmgr 均不在 `C:\swapi` 收录范围），且需许可证。 |

> ⚠ 这两行的「0 个官方示例」本身就是**重要结论**：不是我没写指南，是**官方在这个域就没给可参考的示例**。

---

## 附：语言分布（可参考选哪种语言的示例来读）

| 语言 | 示例数 |
|---|---|
| VB | 1201 |
| CSharp | 794 |
| VBNET | 777 |
| CPlusPlus_COM | 41 |
| ? | 26 |

> 本仓库是 **Python**，而官方示例里**没有一个 Python 版本**（VB 1,201 / C# 794 / VB.NET 777 / C++ COM 41）。读 VB 即可 —— 迟到绑定的调用形状与 VB 最接近，这也是 AGENTS.md §六 多条「按 VB 推断 Python 调用形状」结论的由来。