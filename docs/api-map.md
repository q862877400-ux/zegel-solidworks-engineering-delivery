# 官方 API 成员 → 本仓库函数 反向索引（api-map）

> 生成日期：2026-09-29
> 覆盖：本仓库 **152** 个 .py 文件，对撞到 **351** 个官方成员、**860** 处调用点。
> 调用形态分布：反射式 get/safe_member 409 · 直接调用 obj.Member( 451
> 反射来源：`D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`（20,627 成员）+ `iface_cosworks.txt`（cosworks）
>
> **怎么用这张表**：拿着官方文档里的成员名，在下面 §二 搜，
> 就能知道本仓库哪个函数能调到它。若搜不到，说明该能力**本仓库尚未实现**。
>
> **本表由 AST 解析 + 反射清单对撞生成，未执行任何仓库代码、未连接 SolidWorks。**

---

## 一、按功能域汇总

| 功能域 | 触及的官方成员数 | 本仓库模块 |
|---|---|---|
| 其他/未归类 | **255** | — |
| 质量属性与导出 | **33** | `sw_delivery.py`, `sw_export.py` |
| 零件特征 | **31** | `sw_gear.py`, `sw_part.py` |
| 应用与会话 | **20** | `sw_addin_host.py`, `sw_connect.py`, `sw_macro_guard.py`, `sw_preflight.py`, `sw_session.py` |
| 几何与拓扑 | **19** | `sw_review.py` |
| 焊件 | **18** | `sw_weldment.py` |
| 装配 | **17** | `sw_assembly.py` |
| 仿真(需许可证) | **16** | `sw_simulation.py` |
| 孔与螺纹 | **12** | `sw_hole_features.py`, `sw_hole_table.py` |
| 钣金 | **11** | `sw_sheet_metal.py` |
| 配置·材料·自定义属性 | **8** | `sw_appearance.py`, `sw_document_data.py` |
| 曲面 | **6** | `sw_surface.py` |

---

## 二、成员 → 函数 逐条索引

| 官方成员 | 宿主接口 | 参数 | 本仓库调用点 |
|---|---|---|---|
| `ClearSelection2` | `IModelDoc2` | 1 | `scripts/sw_part.py::auto_dimension_sketch` ×3<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×3<br>`scripts/sw_assembly.py::select_entities_for_mate` ×2<br>… 另 32 处 |
| `Select2` | `IAnnotation` / `IBody2` / `IComponent2` … 另 9 个接口 | 2 | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×9<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_full_round` ×3<br>`scripts/sw_assembly.py::select_entities_for_mate` ×2<br>… 另 15 处 |
| `ForceRebuild3` | `IModelDoc` / `IModelDoc2` | 1 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::apply_treatment` ×2<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::create_threaded_hole_block` ×2<br>`scripts/sw_delivery.py::_comtypes_pack_and_go` ×1<br>… 另 20 处 |
| `InsertSketch` | `IModelDoc` / `IModelDoc2` / `ISketchManager` | IModelDoc(0); IModelDoc2(1) | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::build_model` ×10<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_add_projected_hold_line` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_box` ×2<br>… 另 4 处 |
| `SelectByID2` | `IModelDocExtension` | 9 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::build_model` ×4<br>`scripts/sw_assembly.py::_select_by_id` ×1<br>`scripts/sw_part.py::SketchSelectionRef` ×1<br>… 另 13 处 |
| `FeatureByName` | `IAssemblyDoc` / `IComponent2` / `IDrawingDoc` … 另 1 个接口 | 1 | `subskills/solidworks-fillet-chamfer-cnc/scripts/hold_line_bridge.py::create_hold_line_via_native_addin` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_add_projected_hold_line` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×2<br>… 另 9 处 |
| `GetBodies2` | `IComponent2` / `IPartDoc` | IComponent2(1); IPartDoc(2) | `scripts/sw_geometry_selectors.py::resolve_point` ×1<br>`scripts/sw_hole_features.py::_find_hole_entry_edge` ×1<br>`scripts/sw_part.py::get_bounding_box` ×1<br>… 另 12 处 |
| `Add3` | `ICustomPropertyManager` / `IEquationMgr` | ICustomPropertyManager(4); IEquationMgr(5) | `subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::write_thread_properties` ×10<br>`scripts/sw_document_data.py::set_custom_properties` ×1<br>`scripts/sw_weldment.py::set_cut_list_properties` ×1 |
| `GetErrorMessages` | `ISldWorks` | 3 | `scripts/sw_api_SWRoutingLib.py::<模块级>` ×1<br>`scripts/sw_api_cosworks.py::<模块级>` ×1<br>`scripts/sw_api_dsgnchk.py::<模块级>` ×1<br>… 另 9 处 |
| `GetTitle` | `IDesignTable` / `IModelDoc` / `IModelDoc2` | 0 | `scripts/sw_session.py::SolidWorksSession` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_verify_one` ×2<br>… 另 6 处 |
| `GetCurrentSheet` | `IDrawingDoc` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×3<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_drawing_views` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_arrange_drawing_dimensions` ×1<br>… 另 6 处 |
| `CreateDefinition` | `IFeatureManager` | 1 | `scripts/check_member_owner_interface.py::<模块级>` ×1<br>`scripts/sw_pattern.py::<模块级>` ×1<br>`scripts/sw_sheet_metal.py::_create_from_definition` ×1<br>… 另 7 处 |
| `Add` | `ICustomPropertyManager` / `IEquationMgr` / `IMathVector` | ICustomPropertyManager(3); IEquationMgr(2); IMathVector(1) | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `CreateFeature` | `IFeatureManager` | 1 | `scripts/sw_sheet_metal.py::_create_from_definition` ×1<br>`scripts/sw_sheet_metal.py::create_base_flange` ×1<br>`scripts/sw_weldment.py::_create_from_definition` ×1<br>… 另 5 处 |
| `GraphicsRedraw2` | `IModelDoc` / `IModelDoc2` | 0 | `scripts/sw_import_mesh_reference.py::import_mesh_reference` ×1<br>`scripts/sw_part.py::auto_dimension_sketch` ×1<br>`scripts/sw_review.py::clear_selection_for_preview` ×1<br>… 另 5 处 |
| `GetDefinition` | `IAttribute` / `IFeature` | 0 | `scripts/sw_assembly.py::configure_mate_feature_data` ×1<br>`scripts/sw_sheet_metal.py::sheet_metal_evidence` ×1<br>`scripts/sw_surface.py::<模块级>` ×1<br>… 另 4 处 |
| `GetPathName` | `IComponent` / `IComponent2` / `IModelDoc` … 另 1 个接口 | 0 | `scripts/sw_connect.py::save_document` ×1<br>`scripts/sw_delivery.py::_comtypes_active_model` ×1<br>`scripts/sw_delivery.py::collect_assembly_bom` ×1<br>… 另 4 处 |
| `GetTypeName2` | `IFeature` | 0 | `scripts/sw_sheet_metal.py::_feature_type` ×1<br>`scripts/sw_weldment.py::create_structural_member` ×1<br>`scripts/sw_weldment.py::ensure_cut_list` ×1<br>… 另 4 处 |
| `InsertFeatureChamfer` | `IFeatureManager` | 8 | `scripts/sw_hole_features.py::_chamfer_hole_entry` ×1<br>`scripts/sw_part.py::chamfer` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::apply_treatment` ×1<br>… 另 4 处 |
| `SetFaces` | `ISimpleFilletFeatureData2` / `IWeldmentBeadFeatureData` | ISimpleFilletFeatureData2(2); IWeldmentBeadFeatureData(3) | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_face` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_surface_combo` ×2<br>… 另 1 处 |
| `SetValue` | `ICWTopologyDisplacementConstraint` / `ICWTopologyFactorOfSafetyConstraint` / `ICWTopologyMassConstraint` … 另 1 个接口 | 1 | `scripts/sw_topology.py::set_topology_goal` ×3<br>`scripts/sw_topology.py::<模块级>` ×1<br>`scripts/sw_topology.py::create_factor_of_safety_constraint` ×1<br>… 另 2 处 |
| `FeatureExtrusion3` | `IFeatureManager` / `IPartDoc` | IFeatureManager(23); IPartDoc(18) | `scripts/audit_call_arity.py::direct_call_sites` ×1<br>`scripts/sw_part.py::extrude_boss` ×1<br>`scripts/sw_part.py::extrude_midplane` ×1<br>… 另 3 处 |
| `FirstFeature` | `IComponent2` / `IModelDoc` / `IModelDoc2` … 另 1 个接口 | 0 | `scripts/sw_review.py::collect_model_summary` ×1<br>`scripts/sw_sheet_metal.py::iter_features` ×1<br>`scripts/sw_weldment.py::create_structural_member` ×1<br>… 另 3 处 |
| `GetEdges` | `IBody2` / `IFace` / `IFace2` … 另 7 个接口 | IBody2(0); IFace(2) | `scripts/sw_hole_features.py::_find_hole_entry_edge` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::all_edges` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_bracket.py::_body_stats` ×1<br>… 另 3 处 |
| `GetFastenerTable` | `IHoleStandardsData` | 4 | `scripts/sw_hole_features.py::get_fastener_table` ×6 |
| `GetSelectedObjectCount2` | `ISelectionMgr` | 1 | `scripts/sw_simulation.py::select_face_at` ×2<br>`scripts/sw_assembly.py::select_entities_for_mate` ×1<br>`scripts/sw_review.py::clear_selection_for_preview` ×1<br>… 另 2 处 |
| `GetType` | `IAnnotation` / `IBody` / `IBody2` … 另 12 个接口 | IAnnotation(0); IBody(1) | `scripts/advanced_surface_ocp.py::collect_surface_continuity_evidence` ×2<br>`scripts/sw_connect.py::connect_solidworks` ×1<br>`scripts/sw_delivery.py::collect_assembly_bom` ×1<br>… 另 2 处 |
| `GetViews` | `IDrawingDoc` / `ISheet` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_drawing_views` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_arrange_drawing_dimensions` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_insert_center_marks` ×1<br>… 另 3 处 |
| `ViewZoomtofit2` | `IModelDoc` / `IModelDoc2` | 0 | `scripts/sw_import_mesh_reference.py::import_mesh_reference` ×1<br>`scripts/sw_review.py::zoom_to_fit` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::build_model` ×1<br>… 另 3 处 |
| `CreateCenterRectangle` | `ISketchManager` | 6 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::build_model` ×3<br>`scripts/sw_part.py::sketch_rectangle` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_box` ×1 |
| `GetAddInObject` | `ISldWorks` | 1 | `scripts/sw_simulation.py::ensure_simulation_addin` ×2<br>`scripts/sw_costing.py::get_costing_manager` ×1<br>`scripts/sw_featureworks.py::<模块级>` ×1<br>… 另 1 处 |
| `GetBodyBox` | `IBody` / `IBody2` | 0 | `scripts/sw_geometry_selectors.py::resolve_point` ×1<br>`scripts/sw_part.py::get_bounding_box` ×1<br>`scripts/sw_simulation.py::resolve_face_selector` ×1<br>… 另 2 处 |
| `GetCurve` | `ICoEdge` / `IEdge` / `ISilhouetteEdge` … 另 1 个接口 | 0 | `scripts/sw_hole_features.py::_find_hole_entry_edge` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::circle_center_radius` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::edge_direction` ×1<br>… 另 2 处 |
| `GetPoint` | `IVertex` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::edge_points` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_point` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_complex_case.py::edge_signature` ×1<br>… 另 1 处 |
| `Initialize` | `IBaseFlangeFeatureData` / `IConvertSolidFeatureData` / `ICornerReliefFeatureData` … 另 3 个接口 | IBaseFlangeFeatureData(9); IConvertSolidFeatureData(3); ICornerReliefFeatureData(1); ILibraryFeatureData(1); IMateControllerFeatureData(1) | `scripts/sw_sheet_metal.py::create_base_flange` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_face` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_full_round` ×1<br>… 另 2 处 |
| `Next` | `IEnumBodies` / `IEnumBodies2` / `IEnumCoEdges` … 另 16 个接口 | 3 | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `SaveAs` | `IModelDoc` / `IModelDoc2` / `IModelDocExtension` | IModelDoc(1); IModelDoc2(6) | `scripts/sw_connect.py::save_document` ×1<br>`scripts/sw_export.py::_export_generic` ×1<br>`scripts/sw_export.py::export_to_pdf` ×1<br>… 另 2 处 |
| `SetUserPreferenceToggle` | `IModelDoc` / `IModelDoc2` / `IModelDocExtension` … 另 1 个接口 | IModelDoc(2); IModelDoc2(3) | `scripts/sw_automation_knowledge.py::set_flag` ×1<br>`scripts/sw_connect.py::ensure_default_templates` ×1<br>`scripts/sw_import_mesh_reference.py::configure_mesh_import_preferences` ×1<br>… 另 2 处 |
| `ActivateDoc2` | `ISldWorks` | 3 | `scripts/sw_export.py::_activate_source_document` ×2<br>`scripts/sw_assembly.py::_activate_model_document` ×1<br>`scripts/sw_review.py::activate_model_for_preview` ×1 |
| `ActivateDoc3` | `ISldWorks` | 4 | `scripts/sw_export.py::_activate_source_document` ×2<br>`scripts/sw_assembly.py::_activate_model_document` ×1<br>`scripts/sw_review.py::activate_model_for_preview` ×1 |
| `CreateCircleByRadius` | `IModelDoc` / `IModelDoc2` / `ISketchManager` | IModelDoc(2); IModelDoc2(4) | `scripts/sw_part.py::sketch_circle` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::build_model` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_cylinder` ×1<br>… 另 1 处 |
| `Delete` | `IAttribute` / `IComment` / `ICustomPropertyManager` … 另 2 个接口 | IAttribute(1); IComment(0); ICustomPropertyManager(1); IEquationMgr(1) | `subskills/autocad-automation/scripts/acad_session.py::AutoCADSession` ×3<br>`scripts/sw_equation.py::delete_equation` ×1 |
| `EndEdit` | `ICWBearingConnector` / `ICWCable` / `ICWGeneralSpringConnector` … 另 12 个接口 | 0 | `scripts/sw_topology.py::<模块级>` ×2<br>`scripts/sw_topology.py::_edit` ×2 |
| `FeatureFillet3` | `IFeatureManager` / `IModelDoc` / `IModelDoc2` | IFeatureManager(14); IModelDoc(9) | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_setback` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_variable` ×1<br>… 另 1 处 |
| `GetAnnotation` | `IBlockInstance` / `ICenterLine` / `ICenterMark` … 另 16 个接口 | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_annotation_box` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_note_annotation` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_arrange_drawing_dimensions` ×1<br>… 另 1 处 |
| `GetFaces` | `IBody2` / `IFeature` / `IMateLoadReference` … 另 4 个接口 | IBody2(0); IFeature(1); IMateLoadReference(3); IMidSurface3(3) | `scripts/sw_hole_features.py::_find_hole_entry_edge` ×1<br>`scripts/sw_review.py::collect_geometry_measurements` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_bracket.py::_body_stats` ×1<br>… 另 1 处 |
| `GetModeler` | `ISldWorks` | 0 | `scripts/sw_surface.py::<模块级>` ×3<br>`scripts/sw_surface.py::get_modeler` ×1 |
| `GetSelectedObject6` | `ISelectionMgr` | 2 | `scripts/sw_selection_spec.py::current_selection` ×1<br>`scripts/sw_sheet_metal.py::create_swept_flange` ×1<br>`scripts/sw_simulation.py::_selected_dispatch_array` ×1<br>… 另 1 处 |
| `GetSheetNames` | `IDrawingDoc` | 0 | `scripts/sw_export.py::export_to_pdf` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_arrange_drawing_dimensions` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::export_sheet_to_pdf` ×1<br>… 另 1 处 |
| `GetTextFormat` | `IAnnotation` / `IDetailCircle` / `IDetailingDefaults` … 另 7 个接口 | IAnnotation(1); IDetailCircle(0) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::estimate_dimension_text_box` ×4 |
| `OpenDoc6` | `ISldWorks` | 6 | `scripts/sw_connect.py::open_document` ×2<br>`scripts/sw_com_traps.py::byref_long` ×1<br>`scripts/sw_delivery.py::_comtypes_pack_and_go` ×1 |
| `RevisionNumber` | `ISldWorks` | 0 | `scripts/sw_connect.py::_wait_until_ready` ×1<br>`scripts/sw_connect.py::get_sw_version` ×1<br>`scripts/sw_delivery.py::_active_solidworks_major` ×1<br>… 另 1 处 |
| `Select4` | `IComponent2` / `IEntity` / `ISketchHatch` … 另 2 个接口 | IComponent2(3); IEntity(2) | `scripts/sw_selection_spec.py::<模块级>` ×2<br>`scripts/sw_part.py::auto_dimension_sketch` ×1<br>`scripts/sw_selection_spec.py::select_object` ×1 |
| `AccessSelections` | `IAdvancedHoleFeatureData` / `IBaseFlangeFeatureData` / `IBeltChainFeatureData` … 另 122 个接口 | IAdvancedHoleFeatureData(2); IBaseFlangeFeatureData(2); IBeltChainFeatureData(1); IBendsFeatureData(2) | `scripts/sw_surface.py::<模块级>` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/hold_line_bridge.py::create_hold_line_via_native_addin` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_feature_data_evidence` ×1 |
| `BeginEdit` | `ICWBearingConnector` / `ICWCable` / `ICWGeneralSpringConnector` … 另 12 个接口 | 0 | `scripts/sw_topology.py::<模块级>` ×2<br>`scripts/sw_topology.py::_edit` ×1 |
| `CreateLine` | `IModelDoc` / `IModelDoc2` / `IModeler` … 另 1 个接口 | IModelDoc(2); IModelDoc2(6) | `scripts/sw_part.py::sketch_line` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_add_projected_hold_line` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::add_visible_thread_helix` ×1 |
| `CreateMesh` | `ICwAddincallback` / `ICWStudy` | ICwAddincallback(0); ICWStudy(3) | `scripts/sw_topology.py::run_topology_study` ×2<br>`scripts/sw_simulation.py::create_mesh` ×1 |
| `FeatureCut4` | `IFeatureManager` / `IModelDoc` / `IModelDoc2` | IFeatureManager(27); IModelDoc(17) | `scripts/sw_part.py::extrude_cut` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::cut` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::cut_hole_from_sketch` ×1 |
| `GetBaseView` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_map_native_standard_views` ×2<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_map_standard_views_from_sheet_views` ×1 |
| `GetEndVertex` | `IEdge` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::edge_points` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_edge_points` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_complex_case.py::edge_signature` ×1 |
| `GetErrorCode` | `IFeature` | 0 | `scripts/sw_sheet_metal.py::_create_from_definition` ×1<br>`scripts/sw_sheet_metal.py::create_base_flange` ×1<br>`scripts/sw_weldment.py::_create_from_definition` ×1 |
| `GetFaceCount` | `IBody` / `IBody2` / `IChamferFeatureData2` … 另 6 个接口 | IBody(0); IBody2(1) | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_face` ×2<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_full_round` ×1 |
| `GetFrameCount` | `IGtol` / `IPMIGtolData` | 0 | `scripts/sw_gtol.py::ensure_gtol_frame` ×2<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetHoleStandards` | `IHoleStandardsData` | 2 | `scripts/sw_hole_features.py::_hole_standards_data` ×1<br>`scripts/sw_hole_features.py::get_hole_standards` ×1<br>`scripts/sw_hole_features.py::list_hole_standards` ×1 |
| `GetName` | `IAnnotation` / `IAttribute` / `IDetailCircle` … 另 15 个接口 | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::setup_current_sheet` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::setup_current_sheet_as_a3` ×1 |
| `GetNextFeature` | `IFeature` | 0 | `scripts/sw_review.py::collect_model_summary` ×1<br>`scripts/sw_sheet_metal.py::iter_features` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::collect_feature_evidence` ×1 |
| `GetNextView` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_drawing_views` ×2<br>`scripts/sw_drawing_view.py::get_next_view` ×1 |
| `GetOverrideOptions` | `IMassProperty2` | 0 | `scripts/sw_export.py::get_mass_property_override_options` ×2<br>`scripts/sw_export.py::set_mass_property_override` ×1 |
| `GetRenderMaterials` | `IComponent2` / `IModelDocExtension` | 0 | `scripts/sw_render_material.py::<模块级>` ×2<br>`scripts/sw_render_material.py::list_render_materials` ×1 |
| `GetRenderMaterialsCount` | `IComponent2` / `IModelDocExtension` | 0 | `scripts/sw_render_material.py::<模块级>` ×2<br>`scripts/sw_render_material.py::list_render_materials` ×1 |
| `GetStartVertex` | `IEdge` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::edge_points` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_edge_points` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_complex_case.py::edge_signature` ×1 |
| `GetSurface` | `IFace` / `IFace2` | 0 | `scripts/sw_review.py::collect_geometry_measurements` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_surface_type` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_bracket.py::_body_stats` ×1 |
| `IsCircle` | `ICurve` / `ISketchArc` | 0 | `scripts/sw_hole_features.py::_find_hole_entry_edge` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::circle_center_radius` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::circle_center_radius` ×1 |
| `LoadFile4` | `ISldWorks` | 4 | `scripts/sw_connect.py::open_document` ×2<br>`scripts/sw_import_mesh_reference.py::import_mesh_reference` ×1 |
| `ReleaseSelectionAccess` | `IAdvancedHoleFeatureData` / `IBaseFlangeFeatureData` / `IBeltChainFeatureData` … 另 122 个接口 | 0 | `scripts/sw_surface.py::<模块级>` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/hold_line_bridge.py::create_hold_line_via_native_addin` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_feature_data_evidence` ×1 |
| `SetMassPreference` | `ICWTopologyMassConstraint` | 1 | `scripts/sw_topology.py::<模块级>` ×1<br>`scripts/sw_topology.py::create_mass_constraint` ×1<br>`scripts/sw_topology.py::set_topology_goal` ×1 |
| `ActivateView` | `IDrawingDoc` / `IFeatMgrView` | IDrawingDoc(1); IFeatMgrView(0) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_insert_center_marks` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::insert_dimensions` ×1 |
| `AddMate5` | `IAssemblyDoc` | 15 | `scripts/sw_assembly.py::add_mate5_checked` ×1<br>`scripts/sw_assembly_doc.py::add_mate` ×1 |
| `AddRenderMaterial` | `IModelDocExtension` | 2 | `scripts/sw_render_material.py::<模块级>` ×1<br>`scripts/sw_render_material.py::add_render_material` ×1 |
| `AddRestraint` | `ICWLoadsAndRestraintsManager` | 4 | `scripts/sw_simulation.py::_selected_dispatch_array` ×1<br>`scripts/sw_simulation_study.py::<模块级>` ×1 |
| `Close` | `IAnimation` / `IModelDoc` / `IModelDoc2` … 另 1 个接口 | IAnimation(0); IModelDoc(1) | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `CloseDoc` | `ISldWorks` | 1 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1<br>`scripts/sw_session.py::SolidWorksSession` ×1 |
| `CreateDrawViewFromModelView3` | `IDrawingDoc` | 5 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_view` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::create_adaptive_standard_views` ×1 |
| `CreateFactorOfSafetyConstraint` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_factor_of_safety_constraint` ×1<br>`scripts/sw_topology.py::set_topology_goal` ×1 |
| `CreateGoal` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::<模块级>` ×1<br>`scripts/sw_topology.py::set_topology_goal` ×1 |
| `CreateMassConstraint` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_mass_constraint` ×1<br>`scripts/sw_topology.py::set_topology_goal` ×1 |
| `CreateRenderMaterial` | `IModelDocExtension` | 1 | `scripts/sw_render_material.py::<模块级>` ×1<br>`scripts/sw_render_material.py::create_render_material` ×1 |
| `DeleteRenderMaterial` | `IModelDocExtension` | 2 | `scripts/sw_render_material.py::<模块级>` ×1<br>`scripts/sw_render_material.py::delete_render_material` ×1 |
| `EvaluateAll` | `IEquationMgr` | 0 | `scripts/sw_equation.py::evaluate_equations` ×2 |
| `FeatureFillet` | `IFeatureManager` / `IModelDoc` / `IModelDoc2` | IFeatureManager(7); IModelDoc(5) | `scripts/sw_part.py::fillet` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::apply_treatment` ×1 |
| `Get` | `ICustomPropertyManager` | 1 | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `Get6` | `ICustomPropertyManager` | 6 | `scripts/sw_document_data.py::read_custom_property` ×1<br>`scripts/sw_weldment.py::_read_property` ×1 |
| `GetBox` | `IAssemblyDoc` / `IComponent` / `IComponent2` … 另 3 个接口 | IAssemblyDoc(1); IComponent(2); IComponent2(0); IFace(1) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_annotation_box` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_face_box` ×1 |
| `GetDocumentNamesCount` | `IPackAndGo` | 0 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1<br>`scripts/sw_delivery.py::_pywin32_pack_and_go` ×1 |
| `GetEdgeChamferDistance` | `IChamferFeatureData` / `IChamferFeatureData2` | 1 | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_feature_data_evidence` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_complex_case.py::apply_complex_width_width_chamfer` ×1 |
| `GetExportFileData` | `ISldWorks` | 1 | `scripts/sw_export.py::export_to_pdf` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::export_sheet_to_pdf` ×1 |
| `GetFastenerTableTypes` | `IHoleStandardsData` | 3 | `scripts/sw_hole_features.py::get_fastener_table_types` ×1<br>`scripts/sw_hole_features.py::list_fastener_table_types` ×1 |
| `GetFastenerTypes` | `IHoleStandardsData` | 3 | `scripts/sw_hole_features.py::get_fastener_types` ×1<br>`scripts/sw_hole_features.py::list_fastener_types` ×1 |
| `GetFirstSubFeature` | `IFeature` | 0 | `scripts/sw_weldment.py::iter_features_recursive` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::collect_thread_feature_evidence` ×1 |
| `GetFirstView` | `IDrawingDoc` | 0 | `scripts/sw_drawing_view.py::get_first_view` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_drawing_views` ×1 |
| `GetFrame` | `IGtol` | 1 | `scripts/sw_gtol.py::add_gtol_indicator` ×2 |
| `GetHoldLineCount` | `ISimpleFilletFeatureData2` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/hold_line_bridge.py::create_hold_line_via_native_addin` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_create_hold_line` ×1 |
| `GetLastFeatureAdded` | `IModelDocExtension` | 0 | `scripts/sw_helix.py::_newest_feature_name` ×2 |
| `GetLoadsAndRestraints` | `ICWLoadsAndRestraintsManager` | 2 | `scripts/sw_simulation.py::collect_study_evidence` ×1<br>`scripts/sw_simulation_loads.py::_require` ×1 |
| `GetMassProperties` | `IBody` / `IBody2` / `IModelDoc` … 另 3 个接口 | IBody(1); IBody2(0); IModelDoc(2); IModelDoc2(2) | `scripts/sw_export.py::get_mass_property_override_options` ×2 |
| `GetMaterial` | `IModelDocExtension` | 2 | `scripts/sw_render_material.py::<模块级>` ×1<br>`scripts/sw_simulation_study.py::<模块级>` ×1 |
| `GetNames` | `ICustomPropertyManager` | 0 | `scripts/sw_weldment.py::read_property_manager` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/advanced_fillet_strategy.py::inspect_typelib_members` ×1 |
| `GetNext` | `IAnnotation` / `IBlockInstance` / `ICenterLine` … 另 23 个接口 | 0 | `scripts/sw_view.py::get_next_view` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_center_marks` ×1 |
| `GetOpenDocumentByName` | `ISldWorks` | 1 | `scripts/sw_connect.py::open_document` ×1<br>`scripts/sw_export.py::batch_export_formats` ×1 |
| `GetOrientationName` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_map_native_standard_views` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_map_standard_views_from_sheet_views` ×1 |
| `GetOutline` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_refine_standard_view_spacing` ×2 |
| `GetPackAndGo` | `IModelDocExtension` | 0 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1<br>`scripts/sw_delivery.py::_get_pack_and_go` ×1 |
| `GetPoints` | `IPrimaryMemberPointLengthFeatureData` / `ISketchSpline` | 0 | `scripts/sketch_relations.py::collect_spline_evidence` ×1<br>`scripts/sketch_relations.py::get_spline_points` ×1 |
| `GetPosition` | `IAnnotation` / `IBreakLine` / `ICamera` … 另 2 个接口 | IAnnotation(0); IBreakLine(1); ICamera(4) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_annotation_position` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::estimate_dimension_text_box` ×1 |
| `GetProcessID` | `ISldWorks` | 0 | `scripts/sw_connect.py::residual_dialogs` ×1<br>`scripts/sw_connect.py::solidworks_process_id` ×1 |
| `GetRenderMaterials2` | `IComponent2` / `IModelDocExtension` | 2 | `scripts/sw_render_material.py::<模块级>` ×2 |
| `GetRenderMaterialsCount2` | `IComponent2` / `IModelDocExtension` | 2 | `scripts/sw_render_material.py::<模块级>` ×2 |
| `GetSketchSegments` | `ISketch` / `ISketchContour` / `ISketchPath` … 另 1 个接口 | ISketch(0); ISketchContour(1) | `scripts/sw_sketch.py::get_sketch_segments` ×1<br>`scripts/sw_sketch_edit.py::create_sketch_chamfer` ×1 |
| `GetSplitMember` | `IStructureSystemMemberFeatureData` | 0 | `scripts/sw_weldment.py::configure_split_member` ×2 |
| `GetStudy` | `ICWStudyManager` | 1 | `scripts/sw_simulation.py::iter_studies` ×1<br>`scripts/sw_topology.py::collect_topology_evidence` ×1 |
| `GetText` | `ICustomSymbol` / `IDisplayDimension` / `IGtol` … 另 5 个接口 | ICustomSymbol(1); IDisplayDimension(0); IGtol(1) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_dimension_text_evidence` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_note_text` ×1 |
| `GetVisibilityOfConstructPlanes` | `IModelDoc` / `IModelDoc2` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::hide_reference_planes` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::hide_reference_planes` ×1 |
| `Insert3DSketch` | `IModelDoc` / `IModelDoc2` / `ISketchManager` | IModelDoc(0); IModelDoc2(1) | `subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::add_visible_thread_helix` ×2 |
| `InsertBomTable4` | `IModelDocExtension` / `IView` | IModelDocExtension(9); IView(10) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::insert_bom_table` ×2 |
| `InsertModelAnnotations4` | `IDrawingDoc` | 8 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::insert_dimensions` ×2 |
| `InsertRefPlane` | `IFeatureManager` | 6 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::offset_front_plane` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::create_offset_plane` ×1 |
| `InsertWeldmentCutList2` | `IFeatureManager` | 1 | `scripts/sw_weldment.py::create_cut_list` ×2 |
| `IsCylinder` | `ISurface` | 0 | `scripts/sw_review.py::collect_geometry_measurements` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_bracket.py::_body_stats` ×1 |
| `IsLine` | `ICurve` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::edge_direction` ×1<br>`subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_complex_case.py::edge_signature` ×1 |
| `PostTrimSurface` | `IFeatureManager` / `IModelDoc` / `IModelDoc2` | 1 | `scripts/sw_surface.py::<模块级>` ×2 |
| `RunAnalysis` | `ICwAddincallback` / `ICWStudy` | 0 | `scripts/sw_connect.py::call_com_member` ×1<br>`scripts/sw_connect.py::get_com_member` ×1 |
| `SaveBMP` | `IModelDoc` / `IModelDoc2` | 3 | `scripts/sw_export.py::export_to_bmp` ×1<br>`scripts/sw_review.py::save_preview` ×1 |
| `SavePackAndGo` | `IModelDocExtension` | 1 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1<br>`scripts/sw_delivery.py::_pywin32_pack_and_go` ×1 |
| `Scale` | `IMathPoint` / `IMathVector` / `IModelDoc` … 另 1 个接口 | IMathPoint(1); IMathVector(0) | `scripts/sw_drawing_view.py::set_view_scale` ×1<br>`scripts/sw_view.py::set_view_scale` ×1 |
| `Select` | `IAdvancedSelectionCriteria` / `IAnnotation` / `IBody2` … 另 27 个接口 | IAdvancedSelectionCriteria(0); IAnnotation(1); IBody2(2); IBomTable(2); IBreakLine(2); ICenterMark(3); IComponent(5) | `subskills/autocad-automation/scripts/acad_session.py::AutoCADSession` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_arrange_drawing_dimensions` ×1 |
| `SetSaveToName` | `IPackAndGo` | 2 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1<br>`scripts/sw_delivery.py::_pywin32_pack_and_go` ×1 |
| `SetSheets` | `IExportPdfData` | 2 | `scripts/sw_export.py::export_to_pdf` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::export_sheet_to_pdf` ×1 |
| `SetSuppression2` | `IComponent2` / `IFeature` | IComponent2(1); IFeature(3) | `scripts/sw_assembly.py::resolve_component` ×2 |
| `SetUserPreferenceIntegerValue` | `IModelDoc` / `IModelDoc2` / `ISldWorks` | 2 | `scripts/sw_export.py::export_to_stl` ×1<br>`scripts/sw_import_mesh_reference.py::configure_mesh_import_preferences` ×1 |
| `SetViewPosition` | `IView` | 2 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_apply_view_layout` ×1<br>`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_set_view_center` ×1 |
| `ShowNamedView2` | `IModelDoc` / `IModelDoc2` | 2 | `scripts/sw_review.py::set_standard_view` ×2 |
| `UpdateRenderMaterialsInSceneGraph` | `IModelDocExtension` | 1 | `scripts/sw_render_material.py::<模块级>` ×1<br>`scripts/sw_render_material.py::refresh_scene_graph` ×1 |
| `ViewDispRefplanes` | `IModelDoc` / `IModelDoc2` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py::hide_reference_planes` ×1<br>`subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::hide_reference_planes` ×1 |
| `Activate` | `IAnnotationView` / `ICommandGroup` / `IModelView` … 另 4 个接口 | IAnnotationView(0); ICommandGroup(1) | `scripts/sw_connect.py::get_com_member` ×1 |
| `Add2` | `ICustomPropertyManager` / `IEquationMgr` | 3 | `scripts/sw_equation.py::add_equation` ×1 |
| `AddComponent4` | `IAssemblyDoc` | 5 | `scripts/sw_assembly.py::_add_component4` ×1 |
| `AddCurvatureControl` | `ISketchSpline` | 3 | `scripts/sketch_relations.py::add_spline_curvature` ×1 |
| `AddDefaultRenderMaterial` | `IModelDocExtension` | 2 | `scripts/sw_render_material.py::<模块级>` ×1 |
| `AddDimension2` | `IModelDoc` / `IModelDoc2` | 3 | `scripts/sw_part.py::add_dimension` ×1 |
| `AddDisplayStateSpecificRenderMaterial` | `IModelDocExtension` | 5 | `scripts/sw_render_material.py::<模块级>` ×1 |
| `AddIndicator` | `IGtolFrame` | 3 | `scripts/sw_gtol.py::add_gtol_indicator` ×1 |
| `AddInitialConditionForDynamicStudy` | `ICWLoadsAndRestraintsManager` | 12 | `scripts/sw_simulation.py::<模块级>` ×1 |
| `AddRelation` | `IModelDoc` / `IModelDoc2` / `ISketchRelationManager` | IModelDoc(1); IModelDoc2(2) | `scripts/sketch_relations.py::add_relation` ×1 |
| `AddRevision` | `IRevisionTableAnnotation` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_revision` ×1 |
| `AddTangencyControl` | `ISketchSpline` | 3 | `scripts/sketch_relations.py::add_spline_tangency` ×1 |
| `AddText` | `INote` | 4 | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `AlignDimensions` | `IModelDoc` / `IModelDoc2` / `IModelDocExtension` | IModelDoc(0); IModelDoc2(2) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::auto_arrange_drawing_dimensions` ×1 |
| `AutoDimension2` | `ISketch` | 5 | `scripts/sw_part.py::auto_dimension_sketch` ×1 |
| `BlankSketch` | `IModelDoc` / `IModelDoc2` | 0 | `subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::hide_visible_thread_sketch` ×1 |
| `CanConvertFormat` | `IGtol` | 0 | `scripts/sw_gtol.py::ensure_gtol_frame` ×1 |
| `ConvertFormat` | `IGtol` | 0 | `scripts/sw_gtol.py::ensure_gtol_frame` ×1 |
| `Create3rdAngleViews2` | `IDrawingDoc` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::create_standard_views` ×1 |
| `CreateArc` | `IModelDoc` / `IModelDoc2` / `IModeler` … 另 1 个接口 | IModelDoc(4); IModelDoc2(5); IModeler(10) | `scripts/sw_part.py::sketch_arc` ×1 |
| `CreateChamfer` | `ISketchManager` | 3 | `scripts/sw_sketch_edit.py::create_sketch_chamfer` ×1 |
| `CreateCornerRectangle` | `ISketchManager` | 6 | `scripts/sw_part.py::sketch_corner_rectangle` ×1 |
| `CreateDemoldControl` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_demold_control` ×1 |
| `CreateDetailViewAt4` | `IDrawingDoc` | 12 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_detail_view` ×1 |
| `CreateNewStudy2` | `ICWStudyManager` | 3 | `scripts/sw_topology.py::create_topology_study` ×1 |
| `CreateNewStudy3` | `ICWStudyManager` | 4 | `scripts/sw_connect.py::out_i4` ×1 |
| `CreatePolygon` | `ISketchManager` | 8 | `scripts/sw_part.py::sketch_polygon` ×1 |
| `CreatePreservedRegionControl` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_preserved_region` ×1 |
| `CreateSectionView` | `IDrawingDoc` / `IModelViewManager` | IDrawingDoc(0); IModelViewManager(1) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::create_feature_manager_section_view` ×1 |
| `CreateSectionViewAt5` | `IDrawingDoc` | 7 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_section_view` ×1 |
| `CreateSectionViewData` | `IModelViewManager` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::create_section_view_data` ×1 |
| `CreateSketchSlot` | `ISketchManager` | 14 | `scripts/sw_part.py::sketch_slot` ×1 |
| `CreateSpline2` | `ISketchManager` | 2 | `scripts/sketch_relations.py::create_spline` ×1 |
| `CreateStressConstraint` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_stress_constraint` ×1 |
| `CreateSymmetryControl` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_symmetry_control` ×1 |
| `CreateThicknessControl` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::create_thickness_control` ×1 |
| `DeleteColumn` | `ITableAnnotation` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::delete_table_column` ×1 |
| `DeletePoint` | `ISketchSpline` | 1 | `scripts/sketch_relations.py::delete_spline_point` ×1 |
| `DeleteRevision` | `IRevisionTableAnnotation` | 2 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::delete_revision` ×1 |
| `DeleteRow` | `ITableAnnotation` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::delete_table_row` ×1 |
| `Done` | `IInterferenceDetectionMgr` | 0 | `scripts/sw_assembly.py::get_interference_detection` ×1 |
| `EditSuppress` | `IModelDoc` / `IModelDoc2` / `IPartDoc` | 0 | `scripts/sw_assembly.py::suppress_component` ×1 |
| `EditUnsuppress` | `IModelDoc` / `IModelDoc2` / `IPartDoc` | 0 | `scripts/sw_assembly.py::unsuppress_component` ×1 |
| `ExitApp` | `ISldWorks` | 0 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1 |
| `ExportToDWG2` | `IPartDoc` | 9 | `scripts/sw_export.py::export_flat_pattern_dxf` ×1 |
| `FaceInSurfaceSense` | `IFace` / `IFace2` | 0 | `scripts/sw_review.py::collect_geometry_measurements` ×1 |
| `FeatureCircularPattern4` | `IFeatureManager` | 7 | `scripts/sw_part.py::circular_pattern` ×1 |
| `FeatureLinearPattern3` | `IFeatureManager` | 10 | `scripts/sw_part.py::linear_pattern` ×1 |
| `FeatureRevolve2` | `IFeatureManager` / `IModelDoc` / `IModelDoc2` … 另 1 个接口 | IFeatureManager(20); IModelDoc(5); IModelDoc2(5) | `scripts/sw_part.py::revolve_boss` ×1 |
| `ForceBeginEdit` | `ICWForce` | 0 | `scripts/sw_simulation.py::apply_normal_force` ×1 |
| `ForceEndEdit` | `ICWForce` | 0 | `scripts/sw_simulation.py::apply_normal_force` ×1 |
| `Get3DExperienceType` | `IConfiguration` | 0 | `scripts/sw_pdm.py::collect_pdm_evidence` ×1 |
| `GetActiveSketch2` | `IModelDoc` / `IModelDoc2` | 0 | `scripts/sw_sketch_edit.py::create_sketch_chamfer` ×1 |
| `GetAllowedRelations` | `ISketchRelationManager` | 1 | `scripts/sketch_relations.py::get_allowed_relations` ×1 |
| `GetAnnotationCount` | `IModelDocExtension` / `IView` | 0 | `scripts/sw_drawing_view.py::get_annotation_count` ×1 |
| `GetAnnotations` | `IModelDocExtension` / `IView` | 0 | `scripts/sw_drawing_view.py::get_annotations` ×1 |
| `GetAppearanceSetting` | `IModelDocExtension` | 0 | `scripts/sw_render_material.py::<模块级>` ×1 |
| `GetArcs2` | `ISketch` / `IView` | 0 | `scripts/sw_sketch.py::get_arcs` ×1 |
| `GetArea` | `IFace` / `IFace2` | 0 | `scripts/sw_review.py::collect_geometry_measurements` ×1 |
| `GetBodies` | `IBodyFolder` / `IComponent2` / `IPartDoc` … 另 1 个接口 | IBodyFolder(0); IComponent2(1) | `scripts/check_diff_markers.py::scan` ×1 |
| `GetCenterLines` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetCenterMarks` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_center_marks` ×1 |
| `GetChildren` | `IComponent` / `IComponent2` / `IConfiguration` … 另 2 个接口 | 0 | `scripts/sw_jlcfa_gui.py::find_node` ×1 |
| `GetColumnCustomProperty` | `IBomTableAnnotation` / `IRevisionTableAnnotation` / `IWeldmentCutListAnnotation` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::get_table_custom_property_column` ×1 |
| `GetComponents` | `IAssemblyDoc` / `IBomTableAnnotation` / `ICollision` … 另 4 个接口 | IAssemblyDoc(1); IBomTableAnnotation(1); ICollision(0) | `scripts/sw_delivery.py::collect_assembly_bom` ×1 |
| `GetConfigurationNames` | `IComponent2` / `IModelDoc` / `IModelDoc2` … 另 1 个接口 | IComponent2(0); IModelDoc(1) | `scripts/sw_document_data.py::_configuration_names` ×1 |
| `GetContourEdges` | `ISketch` | 1 | `scripts/sw_sketch.py::get_contour_edges` ×1 |
| `GetControlPointRadiusAtIndex` | `IVariableFilletFeatureData2` | 3 | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_feature_data_evidence` ×1 |
| `GetCorresponding` | `IComponent2` / `IModelDocExtension` / `IPartDoc` … 另 1 个接口 | 1 | `scripts/sw_assembly.py::get_assembly_entity` ×1 |
| `GetCostingManager` | `IModelDocExtension` | 0 | `scripts/sw_costing.py::get_costing_manager` ×1 |
| `GetCount` | `IColorTable` / `IEquationMgr` / `ILayerMgr` | 0 | `scripts/sw_equation.py::list_equations` ×1 |
| `GetCutListItems` | `IConfiguration` | 0 | `scripts/sw_weldment.py::weldment_evidence` ×1 |
| `GetDatumIdentifier` | `IGtol` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetDatumTags` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetDefaultElementSizeAndTolerance` | `ICWMesh` | 3 | `scripts/sw_simulation.py::default_element_size_and_tolerance` ×1 |
| `GetDependencies2` | `IModelDoc` / `IModelDoc2` | 3 | `scripts/sw_delivery.py::_document_dependency_paths` ×1 |
| `GetDetachSegmentOnDrag` | `ISketch` | 0 | `scripts/sw_sketch.py::collect_sketch_evidence` ×1 |
| `GetDimension` | `IDisplayDimension` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×1 |
| `GetDisplayDimensions` | `IMacroFeatureData` / `ISketchBlockDefinition` / `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_display_dimensions` ×1 |
| `GetEllipses3` | `ISketch` / `IView` | 0 | `scripts/sw_sketch.py::get_ellipses` ×1 |
| `GetEndPoint2` | `ISketchArc` / `ISketchEllipse` / `ISketchLine` … 另 1 个接口 | 0 | `scripts/sw_part.py::auto_dimension_sketch` ×1 |
| `GetEquationMgr` | `IModelDoc2` | 0 | `scripts/sw_equation.py::_manager` ×1 |
| `GetExtent` | `IBomTable` / `INote` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_note_box` ×1 |
| `GetFirstCenterMark` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_center_marks` ×1 |
| `GetFirstCenterMark2` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_center_marks` ×1 |
| `GetFirstDisplayDimension` | `IFeature` / `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_display_dimensions` ×1 |
| `GetFirstDisplayDimension5` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_display_dimensions` ×1 |
| `GetGTols` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetHoleStandardsData` | `ISldWorks` | 1 | `scripts/sw_hole_features.py::_hole_standards_data` ×1 |
| `GetImportFileData` | `ISldWorks` | 1 | `scripts/sw_connect.py::open_document` ×1 |
| `GetLabel` | `IDatumTag` / `IDetailCircle` / `IDrSection` … 另 1 个接口 | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetLines2` | `ISketch` / `IView` | ISketch(1); IView(0) | `scripts/sw_sketch.py::get_lines` ×1 |
| `GetMassConstraint` | `ICWTopologyStudyManager` | 2 | `scripts/sw_topology.py::set_topology_goal` ×1 |
| `GetMassProperties2` | `IModelDoc` / `IModelDoc2` / `IModelDocExtension` … 另 1 个接口 | IModelDoc(1); IModelDoc2(3); IModelDocExtension(3) | `scripts/sw_export.py::get_mass_property_override_options` ×1 |
| `GetMateEntityCount` | `IMate2` / `IMateInPlace` | 0 | `scripts/sw_assembly.py::collect_mate_in_place_evidence` ×1 |
| `GetMaterialPropertyValues` | `IFeature` / `IModelDocExtension` | IFeature(0); IModelDocExtension(2) | `scripts/sw_appearance.py::get_material_property_values` ×1 |
| `GetMaximumAvailableSteps` | `ICWResults` | 0 | `scripts/sw_topology.py::collect_topology_numbers` ×1 |
| `GetModelDoc` | `IComponent` / `IComponent2` / `IDerivedPartFeatureData` … 另 2 个接口 | 0 | `scripts/sw_view.py::get_view_model_doc` ×1 |
| `GetModelDoc2` | `IComponent2` | 0 | `scripts/sw_delivery.py::collect_assembly_bom` ×1 |
| `GetNameForSelection` | `IDimension` / `IDisplayDimension` / `IFeature` | IDimension(0); IDisplayDimension(1) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×1 |
| `GetNextDisplayDimension` | `IFeature` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_view_display_dimensions` ×1 |
| `GetNoOfFailedComponents` | `ICWMesh` | 0 | `scripts/sw_simulation_results.py::collect_mesh_evidence` ×1 |
| `GetNotes` | `IBlockDefinition` / `ICustomSymbol` / `IMagneticLine` … 另 3 个接口 | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×1 |
| `GetParabolas2` | `ISketch` / `IView` | 0 | `scripts/sw_sketch.py::get_parabolas` ×1 |
| `GetParameters` | `IConfiguration` / `IMacroFeatureData` | IConfiguration(2); IMacroFeatureData(3) | `scripts/refresh_api_signatures.py::<模块级>` ×1 |
| `GetPartBox` | `IPartDoc` | 1 | `scripts/sw_review.py::collect_geometry_measurements` ×1 |
| `GetPlotCount` | `ICWResults` | 0 | `scripts/sw_topology.py::collect_topology_numbers` ×1 |
| `GetPlotNames` | `ICWResults` | 0 | `scripts/sw_topology.py::collect_topology_numbers` ×1 |
| `GetPolylines` | `ISketch` / `IView` | 0 | `scripts/sw_sketch.py::get_polylines` ×1 |
| `GetRelations` | `ISketchPath` / `ISketchPoint` / `ISketchRelationManager` … 另 1 个接口 | ISketchPath(0); ISketchPoint(1) | `scripts/sketch_relations.py::list_relations` ×1 |
| `GetRelationsCount` | `ISketchPath` / `ISketchPoint` / `ISketchRelationManager` … 另 1 个接口 | ISketchPath(0); ISketchPoint(1) | `scripts/sketch_relations.py::collect_relation_evidence` ×1 |
| `GetSFSymbols` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GetSectionViewData` | `IModelViewManager` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::get_feature_manager_section_data` ×1 |
| `GetSelectionSetFolder` | `IFeatureManager` | 0 | `scripts/sw_topology.py::<模块级>` ×1 |
| `GetSketchBlockInstances` | `ISketch` | 0 | `scripts/sw_sketch.py::get_sketch_block_instances` ×1 |
| `GetSketchContours` | `ISketch` | 0 | `scripts/sw_sketch.py::get_sketch_contours` ×1 |
| `GetSketchHatches` | `ISketch` | 0 | `scripts/sw_sketch.py::get_sketch_hatches` ×1 |
| `GetSketchPaths` | `ISketch` / `ISketchSegment` | 0 | `scripts/sw_sketch.py::get_sketch_paths` ×1 |
| `GetSketchPictures` | `ISketch` / `IView` | 0 | `scripts/sw_sketch.py::get_sketch_pictures` ×1 |
| `GetSketchPoints2` | `ISketch` | 0 | `scripts/sw_sketch.py::get_sketch_points` ×1 |
| `GetSketchRegions` | `ISketch` | 0 | `scripts/sw_sketch.py::get_sketch_regions` ×1 |
| `GetSketchSlots` | `ISketch` | 0 | `scripts/sw_sketch.py::get_sketch_slots` ×1 |
| `GetSpecificFeature2` | `IFeature` | 0 | `scripts/sw_weldment.py::update_cut_list` ×1 |
| `GetSplines` | `ISketch` / `ISketchBlockDefinition` / `IView` | 0 | `scripts/sw_sketch.py::get_splines` ×1 |
| `GetStartPoint2` | `ISketchArc` / `ISketchEllipse` / `ISketchLine` … 另 1 个接口 | 0 | `scripts/sw_part.py::auto_dimension_sketch` ×1 |
| `GetSystemValue2` | `IDimension` | 1 | `scripts/sw_document_data.py::_dimension_value_mm` ×1 |
| `GetTableAnnotations` | `IBendTable` / `IBomFeature` / `IFamilyTableFeature` … 另 8 个接口 | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×1 |
| `GetTemplateName` | `ISheet` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::inspect_drawing_structure` ×1 |
| `GetTextAtIndex` | `ICustomSymbol` / `IDatumTag` / `IDatumTargetSym` … 另 5 个接口 | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_annotation_text_parts` ×1 |
| `GetTextCount` | `ICustomSymbol` / `IDatumTag` / `IDatumTargetSym` … 另 5 个接口 | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_annotation_text_parts` ×1 |
| `GetUserPoints2` | `ISketch` / `IView` | 0 | `scripts/sw_sketch.py::get_user_points` ×1 |
| `GetUserPreferenceStringValue` | `IModelDoc` / `IModelDoc2` / `ISldWorks` | 1 | `scripts/sw_connect.py::ensure_default_templates` ×1 |
| `GetUserPreferenceToggle` | `IModelDoc` / `IModelDoc2` / `IModelDocExtension` … 另 1 个接口 | IModelDoc(1); IModelDoc2(2) | `scripts/sw_automation_knowledge.py::get_flag` ×1 |
| `GetVisibleComponentCount` | `IView` | 0 | `scripts/sw_drawing_view.py::get_visible_component_count` ×1 |
| `GetWeldSymbols` | `IView` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_collect_view_professional_annotations` ×1 |
| `GraphicsRedraw` | `IModelDoc` / `IModelDoc2` / `IModelView` | IModelDoc(0); IModelDoc2(1) | `scripts/sw_view.py::redraw_view` ×1 |
| `HasPerspective` | `IModelView` | 0 | `scripts/sw_view.py::has_perspective` ×1 |
| `IGetDocumentNames` | `IPackAndGo` | 2 | `scripts/sw_delivery.py::_comtypes_document_names` ×1 |
| `InitializeShading` | `IModelView` | 0 | `scripts/sw_view.py::initialize_shading` ×1 |
| `InitializeThreadData` | `IThreadFeatureData` | 0 | `subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::add_real_thread_feature` ×1 |
| `InsertCosmeticThread3` | `IFeatureManager` | 7 | `subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py::add_cosmetic_thread_feature` ×1 |
| `InsertFeatureShell` | `IModelDoc` / `IModelDoc2` | 2 | `scripts/sw_part.py::shell` ×1 |
| `InsertHelix` | `IModelDoc` / `IModelDoc2` | 10 | `scripts/sw_helix.py::insert_helix` ×1 |
| `InsertMirrorFeature2` | `IFeatureManager` | 5 | `scripts/sw_part.py::mirror_feature` ×1 |
| `InsertModelAnnotations3` | `IDrawingDoc` | 6 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::insert_dimensions` ×1 |
| `InsertMoldCoreCavitySolids` | `IFeatureManager` | 4 | `scripts/sw_mold.py::insert_core_cavity_solids` ×1 |
| `InsertMoldPartingLine` | `IFeatureManager` | 1 | `scripts/sw_mold.py::insert_parting_line` ×1 |
| `InsertMoldShutOffSurface` | `IFeatureManager` | 0 | `scripts/sw_connect.py::get_com_member` ×1 |
| `InsertNote` | `IModelDoc` / `IModelDoc2` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_note` ×1 |
| `InsertRib` | `IFeatureManager` / `IModelDoc` / `IModelDoc2` | IFeatureManager(10); IModelDoc(8) | `scripts/sw_part.py::rib` ×1 |
| `InsertSplitLineProject` | `IModelDoc` / `IModelDoc2` | 2 | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py::_add_projected_hold_line` ×1 |
| `InsertSubWeldFolder2` | `IFeatureManager` | 1 | `scripts/sw_weldment.py::create_sub_weld_folder` ×1 |
| `Is3D` | `ISketch` | 0 | `scripts/sw_sketch.py::is_3d_sketch` ×1 |
| `IsPlane` | `ISurface` | 0 | `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_open_source_bracket.py::_body_stats` ×1 |
| `IsSheetMetal` | `IBody2` | 0 | `scripts/sw_sheet_metal.py::sheet_metal_evidence` ×1 |
| `LoadAddIn` | `ISldWorks` | 1 | `scripts/sw_simulation.py::ensure_simulation_addin` ×1 |
| `Lock` | `IModelDoc` / `IModelDoc2` | 0 | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `MergePoints` | `ISketch` | 1 | `scripts/sw_sketch.py::merge_points` ×1 |
| `MoldDraftAnalysis` | `IModelDoc2` | 4 | `scripts/sw_mold.py::mold_draft_analysis` ×1 |
| `MoldUndercutDetect` | `IFeatureManager` | 6 | `scripts/sw_mold.py::mold_undercut_detect` ×1 |
| `NewDocument` | `ISldWorks` | 4 | `scripts/sw_connect.py::new_document` ×1 |
| `NewSheet4` | `IDrawingDoc` | 16 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_sheet` ×1 |
| `Parameter` | `IFeature` / `IModelDoc` / `IModelDoc2` | 1 | `scripts/sw_document_data.py::update_dimension_mm` ×1 |
| `PutDouble` | `ISafeArrayUtility` | 3 | `scripts/audit_byref_args.py::<模块级>` ×1 |
| `Quit` | `IModelDoc` / `IModelDoc2` | 0 | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `RemoveConstraint` | `ICWTopologyStudyManager` | 1 | `scripts/sw_topology.py::set_topology_goal` ×1 |
| `RemoveSectionView` | `IModelViewManager` | 0 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::remove_feature_manager_section_view` ×1 |
| `ReplaceComponents2` | `IAssemblyDoc` | 5 | `scripts/sw_assembly.py::replace_component` ×1 |
| `ResolveAllLightWeightComponents` | `IAssemblyDoc` | 1 | `scripts/sw_delivery.py::_comtypes_pack_and_go` ×1 |
| `ResumeSelectionList` | `ISelectionMgr` | 0 | `scripts/sw_selection.py::resume_selection_list` ×1 |
| `ResumeSelectionList2` | `ISelectionMgr` | 1 | `scripts/sw_selection.py::resume_selection_list` ×1 |
| `RollBy` | `IModelView` | 1 | `scripts/sw_view.py::roll_view` ×1 |
| `RotateAboutCenter` | `IModelView` | 2 | `scripts/sw_view.py::rotate_about_center` ×1 |
| `RunMacro2` | `ISldWorks` | 5 | `subskills/solidworks-fillet-chamfer-cnc/scripts/hold_line_bridge.py::create_hold_line_via_native_addin` ×1 |
| `Save` | `IBody` / `IBody2` / `IModelDoc` … 另 2 个接口 | IBody(1); IBody2(0); IModelDoc(1) | ⚠ 疑似撞名（仅出现在非 COM 模块） |
| `Save3` | `IModelDoc2` | 3 | `scripts/sw_connect.py::save_document` ×1 |
| `Select3` | `IAnnotation` / `IComponent2` / `IEntity` … 另 3 个接口 | IAnnotation(2); IComponent2(3) | `scripts/sw_part.py::auto_dimension_sketch` ×1 |
| `SelectDemoldDirection` | `ICWTopologyDemoldControl` | 1 | `scripts/sw_topology.py::create_demold_control` ×1 |
| `SelectSymmetryType` | `ICWTopologySymmetryControl` | 1 | `scripts/sw_topology.py::create_symmetry_control` ×1 |
| `SendMsgToUser2` | `ISldWorks` | 3 | `scripts/sw_automation_knowledge.py::send_message` ×1 |
| `SetAutomaticSolve` | `ISketch` | 1 | `scripts/sw_sketch.py::set_automatic_solve` ×1 |
| `SetCameraByName` | `IModelView` | 1 | `scripts/sw_view.py::set_view_camera_by_name` ×1 |
| `SetColumnCustomProperty` | `IBomTableAnnotation` / `IRevisionTableAnnotation` / `IWeldmentCutListAnnotation` | 2 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::set_table_custom_property_column` ×1 |
| `SetComparator` | `ICWTopologyDisplacementConstraint` / `ICWTopologyFactorOfSafetyConstraint` / `ICWTopologyStressConstraint` | 1 | `scripts/sw_topology.py::create_stress_constraint` ×1 |
| `SetConvergenceCheck` | `ICWTopologyStudyOptions` | 1 | `scripts/sw_topology.py::set_topology_iteration_options` ×1 |
| `SetIncludeMaxMemberThickness2` | `ICWTopologyThicknessControl` | 1 | `scripts/sw_topology.py::create_thickness_control` ×1 |
| `SetIncludeMinMemberThickness2` | `ICWTopologyThicknessControl` | 1 | `scripts/sw_topology.py::create_thickness_control` ×1 |
| `SetIncludeRegionDepth2` | `ICWTopologyPreservedRegionControl` | 1 | `scripts/sw_topology.py::create_preserved_region` ×1 |
| `SetIterationLimit` | `ICWTopologyStudyOptions` | 1 | `scripts/sw_topology.py::set_topology_iteration_options` ×1 |
| `SetIterationOption` | `ICWTopologyStudyOptions` | 1 | `scripts/sw_topology.py::set_topology_iteration_options` ×1 |
| `SetMaterialPropertyName2` | `IJournalManager` / `IPartDoc` | 3 | `scripts/sw_simulation.py::set_material` ×1 |
| `SetMaxMemberThickness` | `ICWTopologyThicknessControl` | 1 | `scripts/sw_topology.py::create_thickness_control` ×1 |
| `SetMinimumMemberThickness` | `ICWTopologyThicknessControl` | 1 | `scripts/sw_topology.py::create_thickness_control` ×1 |
| `SetOverrideMassValue` | `IMassProperty` / `IMassPropertyOverrideOptions` | IMassProperty(3); IMassPropertyOverrideOptions(1) | `scripts/sw_export.py::set_mass_property_override` ×1 |
| `SetOverrideOptions` | `IMassProperty2` | 3 | `scripts/sw_export.py::set_mass_property_override` ×1 |
| `SetPosition2` | `IAnnotation` | 3 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::_set_annotation_position` ×1 |
| `SetSplitReferences` | `IStructureSystemSplitMember` | 1 | `scripts/sw_weldment.py::configure_split_member` ×1 |
| `SetSystemValue3` | `IDimension` | 3 | `scripts/sw_document_data.py::update_dimension_mm` ×1 |
| `SetTemplateName` | `ISheet` | 1 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::set_sheet_format` ×1 |
| `SetTransformAndSolve2` | `IComponent2` | 1 | `scripts/sw_assembly.py::apply_component_transform_x` ×1 |
| `SetUserPreferenceStringValue` | `IModelDoc` / `IModelDoc2` / `ISldWorks` | 2 | `scripts/sw_connect.py::ensure_default_templates` ×1 |
| `ShowConfiguration2` | `IModelDoc` / `IModelDoc2` | 1 | `scripts/sw_document_data.py::activate_configuration` ×1 |
| `SketchAddConstraints` | `IModelDoc` / `IModelDoc2` | 1 | `scripts/sw_part.py::add_sketch_relation` ×1 |
| `SketchMirror` | `IModelDoc` / `IModelDoc2` | 0 | `scripts/sw_sketch_edit.py::sketch_mirror` ×1 |
| `SketchUseEdge3` | `ISketchManager` | 2 | `scripts/sw_sketch_edit.py::convert_entities` ×1 |
| `Sort` | `IBomTableAnnotation` / `IGeneralTableAnnotation` / `IHoleTableAnnotation` … 另 1 个接口 | IBomTableAnnotation(1); IGeneralTableAnnotation(2) | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::sort_table` ×1 |
| `TranslateBy` | `IModelView` | 2 | `scripts/sw_view.py::translate_view` ×1 |
| `ZoomByFactor` | `IModelView` | 1 | `scripts/sw_view.py::zoom_view` ×1 |

> **宿主接口列**只列前 3 个：某些成员（如 `AccessSelections`）挂在 80+ 个 `*FeatureData` 接口上，全列出来表格就没法读了。
> 完整接口清单见 `_raw/` 下的反射清单，或跑 `python tools/gen_api_map.py` 时保留的 JSON。
>
> 表中「参数」列若显示多个数字且带 ⚠，说明该成员名在**多个接口上参数个数不同**
> （如 `RunAnalysis`：既在 `ICwAddincallback` 上，也在 `ICWStudy` 上；
> `CreateMesh`：在 `ICWStudy` 上是 3 参、在 `ICwAddincallback` 上是 0 参）。
> 此时须结合「本仓库调用点」列判断实际调的是哪一个。

---

## 三、这张表覆盖不到的部分（重要）

| 情况 | 原因 |
|---|---|
| 通过 `CreateDefinition` + FeatureData **属性赋值**间接触及的成员 | 属性名出现在赋值左侧而非调用形态中（如 `data.Thickness = 0.001`）。本表只统计「可静态识别形态」的调用，不统计属性赋值。这部分由 `scripts/sw_sheet_metal.py` 的 `SURFACE_CREATION_METHODS`、`scripts/sw_surface.py` 的 `SURFACE_CREATION_METHODS`、`scripts/sw_simulation.py` 的 5 组 `SWS_*` 表**逐条登记**，另有各函数来源块列出所用的官方成员名 |
| Simulation 域 27 个载荷方法 | 反射清单与两套官方文档都没有签名，本仓库**刻意不提供**入口（AGENTS.md 铁律 5） |
| 「其他/未归类」域下的成员 | 来自 `subskills/` 与 `scripts/` 里未登记到 DOMAIN_OF_MODULE 的模块（如 advanced_*、fea_*、dfm_* 等），它们不属于 14 个功能域的原生 API 面 |

> ⚠ 因此本表是**下界**而非全集：它只统计「形态可静态识别」的直接调用。完整的签名级核对请看 `docs/signature-audit.md`。