# T4-2 机械复核：`example_more_specific` 的分类与「与我们有关」的那一撮

> 生成物 —— 由 `tools/t4_2_more_specific_b.py` 产出，不要手改。
> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。

## 一 · 口径

| 项 | 值 |
|---|---|
| `example_more_specific` 条目 | **3806**（★ 另一对话的 tally 写 3806；★ **实量以此为准**）|
| 涉及成员 | **2242** |
| ★★ 其中我们真调用过的成员 | **258** |

★★ **本表「不算什么」**（★ 缺了它会被误用）：

- ★ **不等于**「这 3806 条都是缺陷」—— 该字段的语义是「**示例比 Remarks 更具体**」，
  ★★ 那是**中性的**（示例给了更多信息 ≠ 官方自相矛盾）⇒ ★ 本表**不判对错** ✓；
- ★ 另一对话自标它**只过了单侧闸**、**10–25% 需复核** ⇒ ★ 真缺陷率**未被独立验证** ✓；
- ★ 「我们真调用过」用 `ast` 判（事实 528）⇒ ★ 只覆盖两种形态，`getattr` 动态取用会漏 ✓；
- ★★ **本表把这批收窄到「与我们有关」的子集** —— 那才是值得花时间的部分 ✓

## 二 · ★★ 与我们有关的成员（**258** 个 · 按条目数排序）

| 成员 | 条目数 | 我们的调用点 |
|---|---:|---|
| `CreateSketchSlot` | 4 | `scripts\sw_part.py:613` |
| `CreateSpline` | 4 | `tools\prove_createline2_and_createspline.py:107` |
| `CreateSpline2` | 4 | `scripts\sketch_relations.py:284` |
| `CreateSpline3` | 4 | `tools\probe_createspline3.py:69` |
| `CylinderParams` | 4 | `scripts\sw_review.py:877` |
| `InsertMidSurface` | 4 | `scripts\sw_sheet_metal_weld_entry.py:817` |
| `InsertMirrorFeature2` | 4 | `scripts\sw_part.py:1498` |
| `ActivateDoc2` | 3 | `scripts\sw_assembly.py:113` |
| `AddComponent4` | 3 | `scripts\sw_assembly.py:138` |
| `AddDimension2` | 3 | `scripts\sw_part.py:838` |
| `AddVerticalDimension2` | 3 | `scripts\sw_sketch_dimensions.py:74` |
| `AutoDimension2` | 3 | `scripts\sw_part.py:805` |
| `Component` | 3 | `scripts\sw_assembly.py:924` |
| `CreateEquationSpline2` | 3 | `tools\prove_equation_driven_curve.py:69` |
| `CreateLine2` | 3 | `tools\prove_createline2_and_createspline.py:96` |
| `CreateMassProperty` | 3 | `tools\compare_geometry.py:98` |
| `CreateParabola` | 3 | `scripts\sw_sketch_primitives.py:132` |
| `CreateStructureSystemMemberData` | 3 | `tools\prove_structure_system.py:104` |
| `Elliptical` | 3 | `tools\verify_dome_smoke.py:201` |
| `FeatureFillet3` | 3 | `scripts\sw_part.py:1144` |
| `GetActiveSketch2` | 3 | `scripts\sw_sketch_edit.py:124` |
| `GetCostingManager` | 3 | `scripts\sw_costing.py:159` |
| `GetCurrentSheet` | 3 | `scripts\sw_drawing_expose.py:165` |
| `GetFirstView` | 3 | `scripts\sw_drawing_expose.py:255` |
| `GetMassProperties` | 3 | `scripts\sw_export.py:589` |
| `GetModelDoc` | 3 | `scripts\sw_view.py:455` |
| `GetRelations` | 3 | `scripts\sketch_relations.py:189` |
| `GetSelectedObject6` | 3 | `scripts\sw_drawing_expose.py:230` |
| `GetSketchContours` | 3 | `scripts\sw_sketch.py:343` |
| `GetSketchHatches` | 3 | `scripts\sw_sketch.py:355` |
| `GetSystemValue3` | 3 | `tools\probe_dimension_unit.py:71` |
| `HoleWizard5` | 3 | `scripts\sw_hole_features.py:1196` |
| `InsertFeatureChamfer` | 3 | `scripts\sw_hole_features.py:116` |
| `InsertFillSurface2` | 3 | `scripts\sw_surface_features.py:622` |
| `InsertFlattenSurface2` | 3 | `scripts\sw_feature_entry_ops.py:319` |
| `InsertHoleTable3` | 3 | `scripts\sw_drawing_expose.py:317` |
| `InsertStructuralWeldment5` | 3 | `scripts\sw_weldment.py:198` |
| `InsertSurfaceFinishSymbol3` | 3 | `scripts\sw_drawing_create_missing.py:579` |
| `InsertWrapFeature2` | 3 | `scripts\sw_wrap.py:109` |
| `Parameter` | 3 | `scripts\check_param_binding.py:160` |
| `PreTrimSurface` | 3 | `scripts\sw_surface_features.py:1088` |
| `TreatCoincidenceAsInterference` | 3 | `scripts\sw_assembly.py:793` |
| `contours` | 3 | `scripts\sw_part.py:251` |
| `ActivateDoc3` | 2 | `scripts\sw_assembly.py:110` |
| `ActiveConfiguration` | 2 | `scripts\sw_document_data.py:78` |
| `ActiveDoc` | 2 | `scripts\sw_connect.py:655` |
| `ActiveSketch` | 2 | `scripts\sw_part.py:515` |
| `ActiveView` | 2 | `scripts\sw_import_mesh_reference.py:288` |
| `Add3` | 2 | `scripts\sw_document_data.py:447` |
| `AddCurvatureControl` | 2 | `scripts\sketch_relations.py:404` |
| `AddDisplayStateSpecificRenderMaterial` | 2 | `scripts\sw_render_material.py:263` |
| `AddEntity` | 2 | `tools\prove_render_material_sequence.py:101` |
| `AddIndicator` | 2 | `scripts\sw_gtol.py:306` |
| `AddPathLengthDim` | 2 | `scripts\sw_sketch_dimensions.py:82` |
| `AddSelectionListObject` | 2 | `tools\probe_batch88_return_types.py:109` |
| `AddSymmetricDimension` | 2 | `tools\prove_symmetric_angular_dimension.py:145` |
| `AddTangencyControl` | 2 | `scripts\sketch_relations.py:396` |
| `AddToDB` | 2 | `scripts\sw_gear.py:258` |
| `AutoBalloon5` | 2 | `scripts\sw_drawing_create_missing.py:760` |
| `Camera` | 2 | `scripts\sw_view.py:367` |
| `CanConvertFormat` | 2 | `scripts\sw_gtol.py:235` |
| `CenterOfMass` | 2 | `scripts\sw_geometry_selectors.py:154` |
| `CloseAllDocuments` | 2 | `mcp-server\server.py:1714` |
| `CloseDoc` | 2 | `scripts\sw_delivery.py:1011` |
| `ConvertFormat` | 2 | `scripts\sw_gtol.py:236` |
| `Create3DBoundingBox` | 2 | `scripts\sw_ref_geometry.py:282` |
| `CreateAutoBalloonOptions` | 2 | `scripts\sw_drawing_create_missing.py:725` |
| `CreateConic` | 2 | `scripts\sw_sketch_primitives.py:141` |
| `CreateCornerRectangle` | 2 | `scripts\sw_part.py:554` |
| `CreateFillet` | 2 | `scripts\sw_sketch_edit_ops.py:175` |
| `CreateStructureSystem` | 2 | `tools\prove_structure_system.py:166` |
| `Diameter` | 2 | `scripts\sw_routing.py:329` |
| `EditRebuild3` | 2 | `tools\probe_ruled_whats_wrong.py:97` |
| `EditSuppress2` | 2 | `scripts\sw_assembly.py:755` |
| `EditUndo2` | 2 | `scripts\sw_session.py:241` |
| `EditUnsuppress2` | 2 | `scripts\sw_assembly.py:768` |
| `FeatureLinearPattern4` | 2 | `tools\probe_linear_pattern_baseline.py:115` |
| `FeatureLinearPattern5` | 2 | `scripts\sw_part.py:1300` |
| `FrameHeight` | 2 | `scripts\sw_view.py:260` |
| `FrameLeft` | 2 | `scripts\sw_view.py:257` |
| `Get6` | 2 | `scripts\sw_custom_property.py:152` |
| `GetAddInObject` | 2 | `scripts\sw_simulation.py:248` |
| `GetAnnotationCount` | 2 | `scripts\sw_drawing_query.py:274` |
| `GetBodyCount` | 2 | `scripts\sw_weldment.py:409` |
| `GetBox` | 2 | `tools\prove_sketch_use_edge3.py:95` |
| `GetDisplayStates` | 2 | `tools\prove_render_material_sequence.py:86` |
| `GetEdges` | 2 | `scripts\sw_feature_entry_ops.py:95` |
| `GetExportFileData` | 2 | `scripts\sw_export.py:140` |
| `GetFirstDisplayDimension` | 2 | `tools\probe_hv_dimension_with_selection.py:106` |
| `GetFirstSubFeature` | 2 | `scripts\sw_weldment.py:299` |
| `GetFrame` | 2 | `scripts\sw_gtol.py:298` |
| `GetImportFileData` | 2 | `scripts\sw_connect.py:1045` |
| `GetLines2` | 2 | `scripts\sw_sketch.py:233` |
| `GetLoopCount` | 2 | `scripts\sw_curve_and_split.py:151` |
| `GetModelDoc2` | 2 | `scripts\sw_delivery.py:102` |
| `GetNextFeature` | 2 | `scripts\sw_review.py:714` |
| `GetPartBox` | 2 | `scripts\sw_review.py:855` |
| `GetPlotCount` | 2 | `scripts\sw_simulation.py:1188` |
| `GetProperties2` | 2 | `scripts\sw_drawing_query.py:147` |
| `GetRelationType` | 2 | `scripts\sketch_relations.py:346` |
| `GetRelationsCount` | 2 | `scripts\sketch_relations.py:353` |
| `GetSelectedObjectCount2` | 2 | `scripts\sw_assembly.py:356` |
| `GetSelectedObjectType3` | 2 | `scripts\sw_drawing_expose.py:231` |
| `GetSheetCount` | 2 | `scripts\sw_drawing_query.py:98` |
| `GetSketchPoints2` | 2 | `scripts\sw_sketch.py:320` |
| `GetSketchSegments` | 2 | `scripts\sw_part.py:988` |
| `GetSpecificFeature2` | 2 | `scripts\sw_sketch.py:521` |
| `GetStartVertex` | 2 | `scripts\sw_surface_features.py:574` |
| `GetTemplateName` | 2 | `scripts\sw_drawing_expose.py:179` |
| `GetTypeName2` | 2 | `scripts\sw_review.py:712` |
| `GetUserPoints2` | 2 | `scripts\sw_sketch.py:329` |
| `GetUserPreferenceInteger` | 2 | `scripts\sw_units.py:101` |
| `GetVisibleComponentCount` | 2 | `scripts\sw_drawing_view.py:474` |
| `GussetThickness` | 2 | `scripts\sw_sheet_metal.py:585` |
| `Initialize` | 2 | `scripts\sw_sheet_metal.py:199` |
| `InsertBreak3` | 2 | `scripts\sw_drawing_create_missing.py:384` |
| `InsertChainDimensions` | 2 | `scripts\sw_sketch_dimensions.py:109` |
| `InsertCoordinateSystem` | 2 | `scripts\sw_ref_geometry.py:205` |
| `InsertCurveFileBegin` | 2 | `scripts\sw_curve_and_split.py:322` |
| `InsertCurveFilePoint` | 2 | `scripts\sw_curve_and_split.py:325` |
| `InsertCutSurface` | 2 | `scripts\sw_surface_features.py:1211` |
| `InsertEndCapFeature3` | 2 | `scripts\sw_sheet_metal_weld_entry.py:572` |
| `InsertFeatureReplaceFace` | 2 | `scripts\sw_surface_edit_ops.py:251` |
| `InsertFeatureShell` | 2 | `scripts\sw_part.py:1477` |
| `InsertGussetFeature3` | 2 | `scripts\sw_sheet_metal_weld_entry.py:704` |
| `InsertOffsetSurface` | 2 | `scripts\sw_surface_edit_ops.py:146` |
| `InsertPlanarRefSurface` | 2 | `scripts\sw_surface_edit_ops.py:124` |
| `InsertProtrusionBlend2` | 2 | `scripts\sw_loft.py:87` |
| `InsertSplitLineProject` | 2 | `scripts\sw_curve_and_split.py:190` |
| `IsCircle` | 2 | `scripts\sw_hole_features.py:974` |
| `LoadFile4` | 2 | `scripts\sw_connect.py:1055` |
| `Mass` | 2 | `scripts\advanced_geometry_ocp.py:355` |
| `MaterialIdName` | 2 | `scripts\sw_simulation.py:803` |
| `ModelToSketchTransform` | 2 | `scripts\sw_sketch.py:422` |
| `ModifyDefinition` | 2 | `tools\probe_sweep_units_recheck.py:105` |
| `Name2` | 2 | `scripts\sw_delivery.py:97` |
| `Next` | 2 | `scripts\advanced_geometry_ocp.py:343` |
| `OpenDoc6` | 2 | `scripts\sw_connect.py:1071` |
| `OverrideDefaultSheetMetalParameters` | 2 | `scripts\sw_sheet_metal.py:214` |
| `Profile` | 2 | `scripts\sw_sheet_metal.py:755` |
| `ProfileLengthDim` | 2 | `scripts\sw_sheet_metal.py:595` |
| `ReplaceComponents2` | 2 | `scripts\sw_assembly.py:780` |
| `RevisionNumber` | 2 | `scripts\sw_connect.py:798` |
| `Save3` | 2 | `scripts\sw_connect.py:1137` |
| `SavePackAndGo` | 2 | `scripts\sw_delivery.py:850` |
| `SelectByRay` | 2 | `scripts\sw_hole_features.py:1181` |
| `SetCameraByName` | 2 | `scripts\sw_view.py:373` |
| `SetOverrideMassValue` | 2 | `scripts\sw_export.py:631` |
| `SetPathSegments` | 2 | `tools\prove_structure_system.py:147` |
| `SetSplitReferences` | 2 | `scripts\sw_weldment.py:755` |
| `SetSystemValue3` | 2 | `scripts\sw_document_data.py:365` |
| `SetUserPreferenceIntegerValue` | 2 | `scripts\sw_import_mesh_reference.py:133` |
| `SetUserPreferenceStringValue` | 2 | `scripts\sw_connect.py:876` |
| `ShowConfiguration2` | 2 | `scripts\sw_document_data.py:115` |
| `ShowNamedView2` | 2 | `scripts\sw_review.py:621` |
| `ShowSplineHandles` | 2 | `scripts\sketch_relations.py:420` |
| `SketchOffsetOnSurface` | 2 | `tools\prove_offset_on_surface_per_example.py:129` |
| `SketchUseEdge3` | 2 | `scripts\sw_sketch_edit.py:309` |
| `Thickness` | 2 | `scripts\sw_sheet_metal.py:215` |
| `ThinFeature` | 2 | `tools\probe_sweep_wall_units_via_hook.py:84` |
| `TranslateBy` | 2 | `scripts\sw_view.py:329` |
| `UseDefaultBendRelief` | 2 | `scripts\sw_sheet_metal.py:743` |
| `UseMaterialSheetMetalParameters` | 2 | `scripts\sw_sheet_metal.py:745` |
| `UseOffset` | 2 | `scripts\sw_sheet_metal.py:605` |
| `AddConfiguration3` | 1 | `scripts\sw_document_data.py:171` |
| `AddHorizontalDimension2` | 1 | `scripts\sw_sketch_dimensions.py:69` |
| `CircleParams` | 1 | `scripts\sw_hole_features.py:981` |
| `ClearSelection2` | 1 | `scripts\sw_assembly.py:351` |
| `ConfigurationManager` | 1 | `scripts\sw_document_data.py:77` |
| `CreateDisplayState` | 1 | `tools\prove_render_material_sequence.py:83` |
| `CreatePolygon` | 1 | `scripts\sw_part.py:580` |
| `CreateRenderMaterial` | 1 | `scripts\sw_render_material.py:193` |
| `CurveType` | 1 | `scripts\sketch_relations.py:415` |
| `D1EndConditionDistance` | 1 | `scripts\sw_sheet_metal.py:211` |
| `D1EndConditionType` | 1 | `scripts\sw_sheet_metal.py:210` |
| `D2EndConditionDistance` | 1 | `scripts\sw_sheet_metal.py:213` |
| `D2EndConditionType` | 1 | `scripts\sw_sheet_metal.py:212` |
| `Density` | 1 | `tools\probe_mass_units_controlled.py:120` |
| `DisplayMode` | 1 | `scripts\sw_view.py:278` |
| `Done` | 1 | `scripts\sw_assembly.py:794` |
| `Edge` | 1 | `scripts\advanced_geometry_ocp.py:250` |
| `EnableContourSelection` | 1 | `scripts\sw_selection.py:427` |
| `Equation` | 1 | `scripts\sw_equation.py:108` |
| `EvaluateAll` | 1 | `scripts\sw_equation.py:124` |
| `ExitApp` | 1 | `scripts\sw_delivery.py:1015` |
| `ExportToDWG2` | 1 | `scripts\sw_export.py:269` |
| `Extension` | 1 | `scripts\sw_assembly.py:662` |
| `FaceInSurfaceSense` | 1 | `scripts\sw_review.py:880` |
| `FeatureBossThicken` | 1 | `scripts\sw_surface_features.py:393` |
| `FeatureByPositionReverse` | 1 | `scripts\sw_sketch.py:680` |
| `FeatureCircularPattern4` | 1 | `scripts\sw_part.py:1441` |
| `FeatureCut4` | 1 | `scripts\sw_part.py:915` |
| `FeatureExtruRefSurface3` | 1 | `scripts\sw_surface_features.py:135` |
| `FeatureExtrusion3` | 1 | `scripts\sw_part.py:869` |
| `FeatureManager` | 1 | `scripts\sw_curve_and_split.py:377` |
| `FeatureRevolve2` | 1 | `scripts\sw_part.py:1047` |
| `ForceRebuild3` | 1 | `scripts\sw_delivery.py:974` |
| `FrameState` | 1 | `scripts\sw_view.py:261` |
| `FrameTop` | 1 | `scripts\sw_view.py:258` |
| `FrameWidth` | 1 | `scripts\sw_view.py:259` |
| `FullyDefineSketch` | 1 | `scripts\sw_sketch_dimensions.py:123` |
| `Get` | 1 | `scripts\advanced_geometry_ocp.py:352` |
| `GetAnnotations` | 1 | `scripts\sw_drawing_query.py:279` |
| `GetComponents` | 1 | `scripts\sw_delivery.py:72` |
| `GetContoursCount` | 1 | `scripts\sw_feature_readback.py:347` |
| `GetDocumentNamesCount` | 1 | `scripts\sw_delivery.py:834` |
| `GetDouble` | 1 | `tools\probe_safearray_comtypes.py:161` |
| `GetEllipses3` | 1 | `scripts\sw_sketch.py:285` |
| `GetEntitiesToJoinCount` | 1 | `tools\verify_composite_curve_smoke.py:190` |
| `GetEquationMgr` | 1 | `scripts\sw_equation.py:58` |
| `GetErrorCode` | 1 | `scripts\sw_sheet_metal.py:225` |
| `GetFaces` | 1 | `scripts\sw_curve_and_split.py:145` |
| `GetFastenerTable` | 1 | `scripts\sw_hole_features.py:350` |
| `GetFastenerTableTypes` | 1 | `scripts\sw_hole_features.py:308` |
| `GetFastenerTypes` | 1 | `scripts\sw_hole_features.py:286` |
| `GetFeatureTreeRootItem2` | 1 | `tools\probe_pattern_dimension_units.py:73` |
| `GetHoleStandards` | 1 | `scripts\sw_hole_features.py:521` |
| `GetHoleStandardsData` | 1 | `scripts\sw_hole_features.py:483` |
| `GetLastFeatureAdded` | 1 | `scripts\sw_helix.py:138` |
| `GetName2` | 1 | `scripts\sw_drawing_expose.py:259` |
| `GetOpenDocumentByName` | 1 | `scripts\sw_connect.py:997` |
| `GetSketchPointCount` | 1 | `scripts\sw_feature_readback.py:530` |
| `GetUserPreferenceIntegerValue` | 1 | `scripts\sw_units.py:138` |
| `Height` | 1 | `tools\verify_dome_smoke.py:198` |
| `InsertCurveFileEnd` | 1 | `scripts\sw_curve_and_split.py:329` |
| `InsertHelix` | 1 | `scripts\sw_helix.py:105` |
| `InsertRefPlane` | 1 | `scripts\sw_ref_geometry.py:176` |
| `InsertReferencePoint` | 1 | `scripts\sw_ref_geometry.py:239` |
| `InsertRevisionTable2` | 1 | `scripts\sw_drawing_expose.py:346` |
| `InsertSewRefSurface` | 1 | `scripts\sw_surface_features.py:263` |
| `InsertWeldmentTrimFeature2` | 1 | `tools\probe_t302_four_families_v2.py:190` |
| `IsCustomPropertyEditable` | 1 | `scripts\sw_custom_property.py:172` |
| `IsSuppressed` | 1 | `mcp-server\server.py:966` |
| `LoadAddIn` | 1 | `scripts\sw_simulation.py:257` |
| `MiterMergeCondition` | 1 | `scripts\sw_weldment.py:194` |
| `NewDocument` | 1 | `scripts\sw_connect.py:940` |
| `Orientation3` | 1 | `scripts\sw_view.py:379` |
| `PostTrimSurface` | 1 | `scripts\sw_surface_features.py:1095` |
| `ProfileDimensionScheme` | 1 | `scripts\sw_sheet_metal.py:584` |
| `Recalculate` | 1 | `tools\probe_mass_units_controlled.py:116` |
| `Reference` | 1 | `scripts\sw_assembly.py:865` |
| `ReferenceComponent` | 1 | `scripts\sw_assembly.py:867` |
| `ReferencedConfiguration` | 1 | `scripts\sw_delivery.py:96` |
| `RelationManager` | 1 | `scripts\sketch_relations.py:158` |
| `ResolveAllLightWeightComponents` | 1 | `scripts\sw_delivery.py:973` |
| `ResumeSelectionList` | 1 | `scripts\sw_selection.py:334` |
| `ResumeSelectionList2` | 1 | `scripts\sw_selection.py:332` |
| `SaveBMP` | 1 | `scripts\sw_export.py:667` |
| `ScaleRatio` | 1 | `scripts\sw_drawing_view.py:851` |
| `SelectionManager` | 1 | `scripts\sw_assembly.py:356` |
| `SetSaveToName2` | 1 | `scripts\sw_delivery.py:847` |
| `SetSuppression2` | 1 | `scripts\sw_assembly.py:224` |
| `SetTemplateName` | 1 | `scripts\sw_drawing_expose.py:176` |
| `SurfaceArea` | 1 | `tools\compare_geometry.py:105` |
| `Type` | 1 | `scripts\sw_drawing_query.py:188` |
| `UseAngleDimForProfile` | 1 | `scripts\sw_sheet_metal.py:594` |
| `UseDefaultBendAllowance` | 1 | `scripts\sw_sheet_metal.py:516` |
| `groups` | 1 | `scripts\audit_byref_args.py:104` |

## 三 · ★ 下一步（★ 仍需人读的那部分）

★ 对第二节那 258 个成员：逐条读 `Remarks` 与示例 ⇒ 判「示例多给的信息**是否改变调用形状**」；
★ 只有**改变调用形状**的才值得动（★ 单纯「说得更细」不用管）✓

★ **抽样建议**（★ 留给下一步）：先抽第二节里条目最多的 **20 条**人工判，
★ 得「真改变形状」的比例后，再决定是否全量复核 ✓

