# COM 成员 → 本仓封装 反查表（生成物，勿手改）

**本文件由 `tools/gen_com_member_index.py` 生成。**

★ 来历：2026-10-26 业主质问「怎么又去查官方 API 了？我们自己不是有工具吗」。
  实情是我手写的 `AddDimension2` / `EditDelete` / `SelectByID2`
  全都有现成封装 ——
  而本仓**没有反查表**，只记得官方成员名，不记得自己封过。

★ 用法：动某个 COM 成员前，先在这里查 ——
  ```bash
  python -B tools/find_com_wrapper.py <成员名>
  ```

| COM 成员 | 本仓封装（模块::函数） |
|---|---|
| `Component2.Select4` | `scripts/sw_assembly_doc.py::edit_part_in_context` … |
| `FeatureManager.FeatureBossThicken` | `scripts/sw_feature_entry_ops.py::thicken_surface` … |
| `SketchManager.ActiveSketch` | `scripts/sw_sketch.py::active_sketch` … |
| `Modeler.Create` | `scripts/sw_export.py::get_mass_property_override_options` … |
| `PartDoc.GetBodies2` | `scripts/sw_feature_readback.py::solid_body_extent_mm` … |
| `ModelDocExtension.GetBox` | `scripts/sw_feature_readback.py::solid_body_extent_mm` … |
| `Sketch.GetConstrainedStatus` | `scripts/engineering/acceptance/e1_sketch.py::collect_sketch_constraint` … |
| `HoleStandardsData.GetFastenerTable` | `scripts/sw_connect.py::out_dispatch` … |
| `ModelDoc2.ActiveView` | `scripts/sw_review.py::set_standard_view` … |
| `Gtol.AddFrame` | `scripts/sw_gtol.py::add_gtol_frame` … |
| `CustomPropertyManager.Count` | `scripts/sw_custom_property.py::custom_property_count` … |
| `SketchManager.CreateCenterLine` | `scripts/sw_part.py::sketch_centerline` … |
| `SketchManager.CreateEllipse` | `scripts/sw_part.py::sketch_ellipse` … |
| `ModelDoc2.FeatureByName` | `scripts/sw_feature_readback.py::extrude_depth` … |
| `SldWorks.GetAddInObject` | `scripts/sw_costing.py::get_costing_manager` … |
| `Face2.GetArea` | `scripts/sw_mass_property.py::section_properties` … |
| `Body2.GetBodyBox` | `scripts/sw_feature_readback.py::solid_body_extent_mm` … |
| `HoleStandardsData.GetHoleStandards` | `scripts/audit_call_arity.py::load_signatures` … |
| `SldWorks.GetHoleStandardsData` | `scripts/sw_hole_features.py::_hole_standards_data` … |
| `SldWorks.GetProcessID` | `scripts/sw_connect.py::solidworks_process_id` … |
| `Body2.GetVertices` | `scripts/sw_selection_spec.py::entities_on_body` … |
| `FeatureManager.HoleWizard5` | `scripts/sw_hole_features.py::_holewizard5_call` … |
| `View.InsertBreak3` | `scripts/sw_drawing_create_missing.py::_find_view` … |
| `ModelDocExtension.InsertChainDimensions` | `scripts/sw_connect.py::get_com_member` … |
| `FeatureManager.InsertCoordinateSystem` | `scripts/sw_ref_geometry.py::insert_coordinate_system` … |
| `ModelDoc2.InsertDome` | `scripts/sw_part.py::insert_dome` … |
| `ModelDoc2.InsertFeatureReplaceFace` | `scripts/sw_surface_edit_ops.py::insert_replace_face` … |
| `ModelDoc2.InsertOffsetSurface` | `scripts/sw_surface_edit_ops.py::insert_offset_surface` … |
| `ModelDoc2.InsertPlanarRefSurface` | `scripts/sw_surface_edit_ops.py::insert_planar_surface` … |
| `FeatureManager.InsertRib` | `scripts/sw_part.py::rib` … |
| `FeatureManager.InsertRuledSurfaceFromEdge2` | `scripts/sw_surface_edit_ops.py::insert_ruled_surface` … |
| `Surface.IsCylinder` | `scripts/sw_feature_entry_ops.py::find_cylindrical_face` … |
| `ModelDoc2.MoldDraftAnalysis` | `scripts/sw_mold.py::mold_draft_analysis` … |
| `Sketch.RelationManager` | `scripts/sw_sketch_dimensions.py::_relations` … |
| `ModelDocExtension.SaveAs` | `scripts/sw_export.py::export_to_pdf` … |
| `View.ScaleRatio` | `scripts/sw_drawing_view.py::get_view_scale_ratio` … |
| `ModelDocExtension.Stretch` | `scripts/sw_sketch_modify_ops.py::sketch_stretch` … |
| `SldWorks.ActiveDoc` | `scripts/sw_simulation_worker.py::create_mesh_safely_by_name` |
| `AssemblyDoc.AddComponent5` | `scripts/sw_toolbox_index.py::part_path` |
| `ModelDoc2.AddDimension2` | `scripts/sw_part.py::add_dimension_report` |
| `ModelDoc2.AddHorizontalDimension2` | `scripts/sw_sketch_dimensions.py::add_horizontal_dimension` |
| `GtolFrame.AddIndicator` | `scripts/sw_gtol.py::add_gtol_indicator` |
| `ModelDocExtension.AddPathLengthDim` | `scripts/sw_sketch_dimensions.py::add_path_length_dimension` |
| `SketchRelationManager.AddRela` | `scripts/sw_sketch_relations.py::apply_sketch_relations` |
| `SketchRelationManager.AddRelation` | `scripts/sketch_relations.py::create_spline` |
| `ModelDoc2.AddVerticalDimension2` | `scripts/sw_sketch_dimensions.py::add_vertical_dimension` |
| `MathTransform.ArrayData` | `scripts/sw_sketch_modify_ops.py::_sketch_transform_translation` |
| `DrawingDoc.AutoBalloon5` | `scripts/sw_drawing_create_missing.py::auto_insert_balloons` |
| `Sketch.AutoDimension2` | `scripts/sw_part.py::auto_dimension_sketch` |
| `AssemblyDoc.AutoExplode` | `scripts/sw_assembly_doc.py::auto_explode` |
| `ModelDoc2.ClearSelection2` | `scripts/sw_selection_spec.py::clear_selection` |
| `SketchSegment.ConstructionGeometry` | `scripts/sw_sketch_edit_ops.py::_construction_flags` |
| `ModelDocExtension.Create3DBoundingBox` | `scripts/sw_ref_geometry.py::create_3d_bounding_box` |
| `DrawingDoc.CreateAuxiliaryViewAt2` | `scripts/sw_drawing_create_missing.py::create_auxiliary_view` |
| `AssemblyDoc.CreateExplodedView` | `scripts/sw_assembly_doc.py::create_exploded_view` |
| `CWTopologyStudyManager.CreateMassConstraint` | `scripts/sw_topology.py::set_topology_goal` |
| `ModelDocExtension.CreateMeasure` | `scripts/sw_measure.py::measure_selection_report` |
| `CWStudyManager.CreateNewStudy3` | `scripts/sw_connect.py::out_i4` |
| `SketchManager.CreatePolygon` | `scripts/sw_part.py::sketch_polygon` |
| `SelectionMgr.CreateSelectData` | `scripts/sw_part.py::_select_com_object` |
| `AssemblyDoc.CreateSpeedPak` | `scripts/sw_assembly_doc.py::create_speedpak_report` |
| `ModelDocExtension.CustomPropertyManager` | `scripts/sw_custom_property.py::custom_property_manager` |
| `SketchRelationManager.DeleteAllRelations` | `scripts/sw_sketch_dimensions.py::delete_all_sketch_relations` |
| `AssemblyDoc.EditAssembly` | `scripts/sw_assembly_doc.py::exit_edit_part_in_context` |
| `ModelDoc2.EditDelete` | `scripts/sw_part.py::feature_delete` |
| `AssemblyDoc.EditExplodeParameters` | `scripts/sw_assembly_doc.py::edit_explode_parameters` |
| `AssemblyDoc.EditPart2` | `scripts/sw_assembly_doc.py::edit_part_in_context` |
| `ModelDoc2.EditRebuild3` | `scripts/sw_session.py::rebuild_report` |
| `ModelDoc2.EditSuppress2` | `scripts/sw_part.py::feature_suppress` |
| `ModelDoc2.EditUndo2` | `scripts/sw_session.py::undo_report` |
| `ModelDoc2.EditUnsuppress2` | `scripts/sw_part.py::feature_unsuppress` |
| `CWMesh.ElementCount` | `scripts/sw_simulation.py::solve_memory_preflight` |
| `FeatureManager.FeatureCutThicken` | `scripts/sw_feature_entry_ops.py::thicken_surface` |
| `FeatureManager.FeatureExtruRefSurface3` | `scripts/sw_surface_features.py::create_extruded_surface_report` |
| `ModelDoc2.FeatureFillet` | `scripts/sw_part.py::fillet` |
| `FeatureManager.FeatureLinearPattern3` | `scripts/sw_part.py::linear_pattern_report` |
| `FeatureManager.FeatureLocalCurveDrivenPattern` | `scripts/sw_pattern.py::insert_local_curve_driven_pattern_report` |
| `FeatureManager.FeatureName` | `scripts/sw_sweep.py::create_sweep_surface_report` |
| `FeatureManager.FeatureRevolve2` | `scripts/sw_part.py::revolve_cut` |
| `ModelDoc2.ForceRebuild3` | `scripts/sw_session.py::rebuild_report` |
| `ModelDocExtension.ForceRebuildAll` | `scripts/sw_session.py::rebuild_report` |
| `SketchManager.FullyDefineSketch` | `scripts/sw_sketch_dimensions.py::fully_define_sketch` |
| `CustomPropertyManager.Get6` | `scripts/sw_custom_property.py::_read_value_via_get6` |
| `ModelDoc2.GetActiveConfiguration` | `scripts/sw_fingerprint.py::read` |
| `AssemblyDoc.GetComponents` | `scripts/sw_simulation_loads.py::apply_pin_connector_report` |
| `View.GetDatumTagCount` | `scripts/sw_drawing_create_missing.py::insert_datum_tag` |
| `ModelDocExtension.GetDisplayStateSetting` | `scripts/sw_fingerprint.py::read` |
| `SldWorks.GetDocuments` | `scripts/sw_connect.py::open_doc_count` |
| `ModelDoc2.GetEquationMgr` | `scripts/sw_equation.py::_manager` |
| `AssemblyDoc.GetExplodedViewConfigurationName` | `scripts/sw_assembly_doc.py::get_exploded_view_configuration_name` |
| `Body2.GetFaces` | `scripts/sw_curve_and_split.py::_face_loop_stats` |
| `HoleStandardsData.GetFastenerTableTypes` | `scripts/sw_hole_features.py::list_fastener_table_types` |
| `HoleStandardsData.GetFastenerTypes` | `scripts/sw_hole_features.py::list_fastener_types` |
| `FeatureManager.GetFeatureCount` | `scripts/sw_sensor.py::_iter_features` |
| `Feature.GetFirstDisplayDimension` | `scripts/sw_sketch_dimensions.py::count_sketch_dimensions` |
| `Gtol.GetFrame` | `scripts/sw_gtol.py::add_gtol_indicator` |
| `InterferenceDetectionMgr.GetInterferenceCount` | `scripts/engineering/acceptance/e4_assembly.py::judge_assembly_interference` |
| `InterferenceDetectionMgr.GetInterferences` | `scripts/sw_assembly.py::get_interference_detection` |
| `ModelDocExtension.GetLastFeatureAdded` | `scripts/sw_helix.py::_newest_feature_name` |
| `Face2.GetLoopCount` | `scripts/sw_curve_and_split.py::_face_loop_stats` |
| `ModelDocExtension.GetMassProperties` | `scripts/sw_export.py::get_mass_property_override_options` |
| `ModelDocExtension.GetMassProperties2` | `scripts/sw_export.py::get_mass_property_override_options` |
| `Sheet.GetName` | `scripts/sw_drawing_query.py::current_sheet_name` |
| `DisplayDimension.GetNext2` | `scripts/sw_sketch_dimensions.py::count_sketch_dimensions` |
| `Feature.GetNextDisplayDimension` | `scripts/sw_sketch_dimensions.py::count_sketch_dimensions` |
| `Feature.GetNextFeature` | `scripts/sw_sensor.py::_iter_features` |
| `View.GetNoteCount` | `scripts/sw_drawing_create_missing.py::auto_insert_balloons` |
| `FeatureManager.GetPartingLinesCount` | `scripts/sw_mold.py::mold_evidence` |
| `Sheet.GetProperties` | `scripts/sw_drawing_query.py::get_sheet_scale_report` |
| `Sheet.GetProperties2` | `scripts/sw_drawing_query.py::current_sheet_info` |
| `SketchRelationManager.GetRelationsCount` | `scripts/sw_sketch_dimensions.py::count_sketch_relations` |
| `View.GetSFSymbolCount` | `scripts/sw_drawing_create_missing.py::insert_surface_finish_symbol` |
| `ModelDoc2.GetSaveFlag` | `scripts/sw_session.py::open_documents` |
| `View.GetSection` | `scripts/sw_drawing_expose.py::create_section_view` |
| `SelectionManager.GetSelectedObjectCount2` | `scripts/sw_simulation.py::select_face_at` |
| `DrawingDoc.GetSheetCount` | `scripts/sw_drawing_query.py::sheet_count` |
| `DrawingDoc.GetSheetNames` | `scripts/sw_drawing_query.py::sheet_names` |
| `ModelDoc2.GetSldWorks` | `scripts/sw_units.py::read_units_report` |
| `StructureSystemMemberFeatureData.GetSplitMember` | `scripts/sw_weldment.py::configure_split_member` |
| `ModelDoc2.GetUnits` | `scripts/sw_units.py::read_units_report` |
| `ModelDocExtension.GetUserPreferenceInteger` | `scripts/sw_units.py::read_units_report` |
| `SldWorks.GetUserPreferenceIntegerValue` | `scripts/sw_units.py::read_units_report` |
| `ModelDoc2.InsertAxis2` | `scripts/sw_part.py::create_axis_report` |
| `FeatureManager.InsertCenterOfMass` | `scripts/sw_ref_geometry.py::insert_center_of_mass` |
| `ModelDoc2.InsertCompositeCurve` | `scripts/sw_part.py::insert_composite_curve` |
| `FeatureManager.InsertCosmeticThread3` | `scripts/sw_feature_entry_ops.py::insert_cosmetic_thread` |
| `FeatureManager.InsertCutSurface` | `scripts/sw_surface_features.py::cut_surface_report` |
| `ModelDoc2.InsertDatumTag2` | `scripts/sw_drawing_create_missing.py::insert_datum_tag` |
| `ModelDocExtension.InsertDeleteFace` | `scripts/sw_surface_edit_ops.py::insert_delete_face` |
| `ModelDoc2.InsertDeleteFace2` | `scripts/sw_surface_edit_ops.py::insert_delete_face` |
| `FeatureManager.InsertEndCapFeature3` | `scripts/sw_sheet_metal_weld_entry.py::insert_weldment_end_cap` |
| `SketchManager.InsertExplodeLineSketch` | `scripts/sw_assembly_doc.py::insert_explode_line_sketch_report` |
| `ModelDoc2.InsertExtendSurface` | `scripts/sw_surface_features.py::insert_extend_surface_report` |
| `FeatureManager.InsertFillSurface2` | `scripts/sw_surface_features.py::insert_fill_surface_report` |
| `FeatureManager.InsertFlattenSurface2` | `scripts/sw_feature_entry_ops.py::create_flatten_surface` |
| `FeatureManager.InsertGlobalBoundingBox2` | `scripts/sw_ref_geometry.py::insert_global_bounding_box` |
| `ModelDoc2.InsertGtol` | `scripts/sw_gtol.py::insert_gtol` |
| `FeatureManager.InsertGussetFeature3` | `scripts/sw_sheet_metal_weld_entry.py::insert_weldment_gusset` |
| `View.InsertHoleTable3` | `scripts/sw_drawing_expose.py::create_hole_table` |
| `ModelDoc2.InsertLoftRefSurface2` | `scripts/sw_surface_ref_ops.py::insert_lofted_ref_surface` |
| `FeatureManager.InsertMateReference2` | `scripts/sw_curve_and_split.py::insert_mate_reference` |
| `FeatureManager.InsertMidSurface` | `scripts/sw_sheet_metal_weld_entry.py::insert_mid_surface` |
| `FeatureManager.InsertRefPlane` | `scripts/sw_ref_geometry.py::insert_ref_plane` |
| `FeatureManager.InsertReferencePoint` | `scripts/sw_ref_geometry.py::insert_reference_point` |
| `Sheet.InsertRevisionTable2` | `scripts/sw_drawing_expose.py::create_revision_table` |
| `FeatureManager.InsertRevolvedRefSurface` | `scripts/sw_surface_ref_ops.py::insert_revolved_ref_surface` |
| `ModelDoc2.InsertSheetMetalClosedCorner` | `scripts/sw_sheet_metal_weld_entry.py::insert_sheet_metal_closed_corner` |
| `FeatureManager.InsertSheetMetalMiterFlange` | `scripts/sw_sheet_metal_weld_entry.py::insert_sheet_metal_miter_flange` |
| `ModelDoc2.InsertSplitLineProject` | `scripts/sw_curve_and_split.py::insert_split_line_project` |
| `ModelDoc2.InsertSplitLineSil` | `scripts/sw_curve_and_split.py::insert_split_line_silhouette` |
| `ModelDocExtension.InsertSurfaceFinishSymbol3` | `scripts/sw_drawing_create_missing.py::insert_surface_finish_symbol` |
| `ModelDoc2.InsertSweepRefSurface` | `scripts/sw_sweep.py::create_sweep_surface_report` |
| `DrawingDoc.InsertTableAnnotation` | `scripts/sw_drawing_expose.py::create_hole_table` |
| `FeatureManager.InsertWeldmentCutList` | `scripts/sw_weldment.py::create_cut_list` |
| `FeatureManager.InsertWrapFeature2` | `scripts/sw_wrap.py::create_wrap_report` |
| `Component2.ListExternalFileReferencesCount` | `scripts/sw_assembly_doc.py::list_external_file_references_count` |
| `FeatureManager.MoldUndercutDetect` | `scripts/sw_mold.py::mold_undercut_detect` |
| `ModelDocExtension.NeedsRebuild2` | `scripts/sw_session.py::needs_rebuild_status` |
| `SldWorks.NewDocument` | `scripts/sw_connect.py::open_document` |
| `CWMesh.NodeCount` | `scripts/sw_simulation.py::solve_memory_preflight` |
| `ModelDoc2.PartingType` | `scripts/sw_mold.py::mold_evidence` |
| `FeatureManager.PreTrimSurface` | `scripts/sw_surface_features.py::trim_surface_report` |
| `SldWorks.RevisionNumber` | `scripts/sw_connect.py::connect_solidworks` |
| `ModelDocExtension.SaveAs3` | `scripts/sw_export.py::export_to_image` |
| `ModelDoc2.SaveBMP` | `scripts/sw_export.py::export_to_bmp` |
| `Component2.Select2` | `scripts/sw_assembly_doc.py::edit_part_in_context` |
| `ModelDocExtension.SelectByRay` | `scripts/sw_hole_features.py::create_hole_wizard_at_point_report` |
| `ModelDoc2.SelectionManager` | `scripts/sw_selection.py::get_selection_manager` |
| `DrSection.SetLabel2` | `scripts/sw_drawing_expose.py::create_section_view` |
| `Sheet.SetScale` | `scripts/sw_drawing_query.py::set_sheet_scale_report` |
| `Sheet.SetTemplateName` | `scripts/sw_drawing_expose.py::set_sheet_format` |
| `AssemblyDoc.ShowExploded2` | `scripts/sw_assembly_doc.py::show_exploded` |
| `ModelDoc2.SketchModifyFlip` | `scripts/sw_sketch_modify_ops.py::sketch_flip` |
| `ModelDoc2.SketchModifyRotate` | `scripts/sw_sketch_modify_ops.py::sketch_rotate` |
| `ModelDoc2.SketchModifyScale` | `scripts/sw_sketch_modify_ops.py::sketch_scale` |
| `ModelDoc2.SketchModifyTranslate` | `scripts/sw_sketch_modify_ops.py::sketch_move` |
| `CWStaticStudyOptions.SolverType` | `scripts/sw_simulation.py::static_solver_type_report` |
| `SweepFeatureData.SweepType` | `scripts/sw_sweep.py::create_sweep_surface_report` |
| `Dimension.SystemValue` | `scripts/sw_document_data.py::_dimension_value_mm` |
| `Modeler.ThickenSheet` | `scripts/sw_feature_entry_ops.py::thicken_surface` |
| `AssemblyDoc.ViewCollapseAssembly` | `scripts/sw_assembly_doc.py::view_collapse_assembly` |
| `AssemblyDoc.ViewExplodeAssembly` | `scripts/sw_assembly_doc.py::view_explode_assembly` |

成员总数见 `docs/com-member-index.json`（生成物，勿手改）。
