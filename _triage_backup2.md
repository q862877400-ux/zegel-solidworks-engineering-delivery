# B 级并入缺口分诊（`010`）

> ⚑⚑ **口径声明（2026-10-01 轮 199 加）：本表量的是「操作名缺口」，不是「能力缺口」。**
> ```
> · 本表：并集 349 个**操作名**里，有多少个在本仓库**没有同名 / 别名的操作名**
> · 而 `harvest-report.md` §10.3 的**判据更正**指出：那个数的根因是
>   `tools/build_union_map.py` 的 `_our_tools()` **只数 `mcp-server/server.py` 的 `@mcp.tool` 名字**，
>   而本仓库的能力实现在 `scripts/` 里、**没暴露成 MCP 工具**。
> ⇒ ★★ **同一个数，两个口径**：
>   · 「**能力**缺口」（本仓库有没有这个能力）≈ **0** —— 逐域核过：
>     焊件 地图说缺 5 / **实际 14 个函数且 verified**；草图 42/**57**；装配 19/**54**；工程图 49/**44**；
>     **唯一真缺口是模具 1 个**，轮 86 已并入
>   · 「**操作名**缺口」（有没有以**那个名字**暴露）≈ 本表下面四轮人工核出的数
> ⇒ ★ **不要把本表下面那个数读成「缺 N 个能力」** —— 那正是 §10.3 更正掉的那个读法。
> ★ **两个口径各自标注、互相指认，不合并成一个数**（与 `AGENTS.md §一 A2` 那条
>   「① 与 ② 不是同一件事 …… 两条线不该混」同型的纪律）。
> ⚠ 而**本表的数本身也会随并入而变** ⇒ 读它请连**「算于」那一行**一起读（它标着算的时间）。
> ```
>
> ⚠⚠ **2026-10-01 轮 101 修正**：本表「**能力在、未暴露 144（42%）**」这一档
> **高估了**。人工核样 24 条（每 6 取 1）⇒ **真 6 · 部分 2 · 假 16** ⇒ **真实命中率 ≈ 25%**。
> ⇒ 真缺应约 **240**（= 132 + 144×75%），不是 132。
> ⚠⚠ **轮 102 追加**：另两档「别名（强）26 / 别名（弱）37」**全核**后同样是**大量假匹配**
> （强档 **7/26≈27%** · 弱档 **6/37≈16%**）—— ⚠ **连自称「极可能同一操作」的强档也不例外**。
> ⇒ 四档合并：真匹配 ≈ **49** ⇒ **真实缺口 ≈ 289**（`010` 当时说 132）。
> ⚠ 限度：别名两档是全核，后缀候选是抽样 ⇒ 结论应表述为「**真实缺口约 270~290**」。
> ⚠⚠ **轮 103 追加**：**「真缺」132 条也反向核了**（每 6 取 1 ⇒ 22 条）。
> 反向错误率 ≈ **18%**（4/22 其实我们有，如 `tooling_split`、`save_as`、`measure`）。
> ⇒ 四轮合并：真匹配 ≈ **73** ⇒ **真实缺口 ≈ 265**（区间约 **245~265**）。
> 证据与逐条判定见 [`docs/union-gap-triage-sample.md`](union-gap-triage-sample.md)。
> ★ **根因**：该档来自**后缀词**匹配，而 `sketch` / `view` / `template` / `macro` 是高频通用词
> ⇒ **这一档不该由字符串匹配给结论，只能人工核**。

> **本表干什么**：把 `union-coverage-matrix.md` 的「缺 N」拆成「**别名候选**（我们其实有，只是名字不同）」与「**真缺**」，为并入**定范围**。
> ⚠ **主匹配器没动**（纪律：已知事实 53 —— 不靠模糊启发式硬凑）。
> 这张表是**另一口径**，用**有原则的规则**算出来，供人核。

**算于**：2026-10-01（轮 86）· 并集 **349** · 我们 **65** · 缺口 **339**

> ⚑⚑ **上面那三个数是**轮 86 的历史快照**，**已经不是当前值**（2026-10-01 轮 200 加）。
> ```
> ★ **当前值只有一个家**：`docs/union-coverage-matrix.md` 的「**合计**」行 ——
>   它由 `tools/build_union_map.py` **生成**，且由门禁 `check_map_fresh()` **重跑逐字比对**
>   ⇒ ★ 那个数**不会腐坏**；而**手写的快照会**。
> ★ 实测（轮 200）：重跑生成器得 **并集 424 · MCP 暴露面缺 338 · 本仓库独家 75** ——
>   **与上述 349 / 339 都不同**。
> ⇒ 根因：轮 129 修掉了「暴露面被低估 20 个」的缺陷（`_our_tools()` 原来只看
>   `server.py` 的 `@mcp.tool` 装饰器形式）⇒ 修完后「我们」变多、并集与缺口随之变，
>   而**这行快照没有跟着更新**（它自己写着「算于轮 86」⇒ 它**没有说谎**，只是**过期**了）。
> ⇒ ★★ **纪律：本表的数字只作历史锚点；要报当前值，去读生成物的合计行。**
> ```


| 类 | 个数 | 占比 | 含义 |
|---|---|---|---|
| **别名（强）** | 26 | 8% | 我们的操作名**以缺口名结尾**，且多出来的词**全是域词** ⇒ 极可能同一操作 |
| **别名（弱）** | 37 | 11% | 以缺口名结尾，但多出来的词里**含动词** ⇒ 疑似，语义可能不同 |
| **能力在、未暴露** | 144 | 42% | `scripts/sw_*.py` 里有同名函数，**只是没暴露成 MCP 工具** |
| **真缺** | 132 | 39% | 连 `scripts/` 里也没有同名函数 ⇒ **要从零实现** |

---

## 别名（强）（26）

| 缺口操作 | 我们的候选 |
|---|---|
| `advanced_features` | `inspect_hole_features` |
| `assembly_analysis` | `mold_draft_analysis` |
| `assembly_configurations` | `inspect_configurations` |
| `configurations` | `inspect_configurations` |
| `delete_feature` | `hole_feature` |
| `drawing` | `inspect_drawing` |
| `extend_surface` | `mold_shut_off_surface, ocp_surface` |
| `extruded_surface` | `mold_shut_off_surface, ocp_surface` |
| `features` | `inspect_hole_features` |
| `filled_surface` | `mold_shut_off_surface, ocp_surface` |
| `line` | `mold_parting_line` |
| `loft` | `ocp_loft` |
| `mirror_feature` | `hole_feature` |
| `offset_surface` | `mold_shut_off_surface, ocp_surface` |
| `parting_line` | `mold_parting_line` |
| `pattern_features` | `inspect_hole_features` |
| `planar_surface` | `mold_shut_off_surface, ocp_surface` |
| `rename_feature` | `hole_feature` |
| `revolved_surface` | `mold_shut_off_surface, ocp_surface` |
| `shut_off_surface` | `mold_shut_off_surface, ocp_surface` |
| `sketch_line` | `mold_parting_line` |
| `split_line` | `mold_parting_line` |
| `technical_drawing` | `inspect_drawing` |
| `thicken_surface` | `mold_shut_off_surface, ocp_surface` |
| `trim_surface` | `mold_shut_off_surface, ocp_surface` |
| `unsuppress_feature` | `hole_feature` |

## 别名（弱）（37）

| 缺口操作 | 我们的候选 |
|---|---|
| `activate_document` | `new_document, open_document` |
| `analyze_draft` | `sheet_metal_create_draft` |
| `analyze_geometry` | `review_advanced_geometry` |
| `base_flange` | `sheet_metal_create_base_flange, sheet_metal_create_edge_flange` |
| `batch_process_files` | `batch_export_files` |
| `bom` | `export_assembly_bom` |
| `check_geometry` | `review_advanced_geometry` |
| `close_document` | `new_document, open_document` |
| `construction_geometry` | `review_advanced_geometry` |
| `convert_file_format` | `write_open_format` |
| `diameter_dimension` | `update_dimension` |
| `dimension` | `update_dimension` |
| `draft` | `sheet_metal_create_draft` |
| `drawing_dimension` | `update_dimension` |
| `drawing_sheet_format` | `write_open_format` |
| `edge_flange` | `sheet_metal_create_base_flange, sheet_metal_create_edge_flange` |
| `export_document` | `new_document, open_document` |
| `gusset` | `sheet_metal_create_gusset` |
| `load_part` | `basic_part` |
| `mate` | `coincident_mate, concentric_mate` |
| `material` | `simulation_set_material` |
| `miter_flange` | `sheet_metal_create_base_flange, sheet_metal_create_edge_flange` |
| `motion_study` | `topology_create_study, validate_motion_study` |
| `open_documents` | `close_documents` |
| `part` | `basic_part` |
| `rebuild_document` | `new_document, open_document` |
| `reference_geometry` | `review_advanced_geometry` |
| `referenced_documents` | `close_documents` |
| `save_active_document` | `new_document, open_document` |
| `save_body_as_part` | `basic_part` |
| `save_part` | `basic_part` |
| `simulation_study` | `topology_create_study, validate_motion_study` |
| `sketch_dimension` | `update_dimension` |
| `sketch_status` | `addin_host_status` |
| `sketched_bend` | `sheet_metal_create_one_bend` |
| `status` | `addin_host_status` |
| `update_sheet_format` | `write_open_format` |

## 后缀候选（需人工核）（144）

| 缺口操作 | 我们的候选 |
|---|---|
| `3d_sketch` | `auto_dimension_sketch, end_sketch` |
| `3point_arc` | `sketch_arc` |
| `activate_display_state` | `_suppression_state, _toolbox_state` |
| `activate_drawing_view` | `activate_view, call_view` |
| `active_document_info` | `_file_info` |
| `analyze_drawing_annotations` | `get_annotations` |
| `analyze_macro` | `is_swp_macro, validate_vba_macro` |
| `appearance_color` | `set_selection_color` |
| `apply_drawing_template` | `find_template, get_default_template` |
| `apply_template` | `find_template, get_default_template` |
| `arc` | `sketch_arc` |
| `assembly` | `dissolve_assembly` |
| `assembly_components` | `get_components` |
| `assembly_tree` | `iter_feature_tree` |
| `auto_dimension_view` | `activate_view, call_view` |
| `auxiliary_view` | `activate_view, call_view` |
| `batch_apply_template` | `find_template, get_default_template` |
| `batch_export` | `batch_export` |
| `bodies` | `get_bodies, update_cost_for_all_bodies` |
| `boundary_boss` | `extrude_boss, revolve_boss` |
| `broken_view` | `activate_view, call_view` |
| `calculate_mass_properties` | `apply_visual_properties, set_custom_properties` |
| `center_mark` | `get_selected_object_mark, set_selected_object_mark` |
| `chamfer` | `chamfer` |
| `check_drawing_standards` | `get_hole_standards, list_standards` |
| `circle` | `sketch_circle` |
| `circular_pattern` | `_contains_any_pattern, circular_pattern` |
| `classify_feature_tree` | `iter_feature_tree` |
| `clear_selection` | `clear_selection, current_selection` |
| `close_all` | `fill_all, locate_all` |
| `close_model` | `_comtypes_active_model, _extract_comtypes_model` |
| `close_sketch` | `auto_dimension_sketch, end_sketch` |
| `combine_bodies` | `get_bodies, update_cost_for_all_bodies` |
| `compare_drawing_templates` | `ensure_default_templates, list_templates` |
| `compare_templates` | `ensure_default_templates, list_templates` |
| `components` | `get_components` |
| `convert_text_to_native_macro` | `is_swp_macro, validate_vba_macro` |
| `curve_driven_pattern` | `_contains_any_pattern, circular_pattern` |
| `delete_body` | `create_deformed_body, entities_on_body` |
| `delete_face` | `find_largest_cylinder_face, get_selected_face` |
| `design_table` | `get_fastener_table` |
| `design_table_create` | `recognize_and_create` |
| `detail_view` | `activate_view, call_view` |
| `display_mode` | `get_display_mode, set_display_mode` |
| `drawing_annotations` | `get_annotations` |
| `drawing_from_model` | `_comtypes_active_model, _extract_comtypes_model` |
| `drawing_scale` | `get_view_scale, set_view_scale` |
| `drawing_sheet_info` | `_file_info` |
| `drawing_sheet_size` | `_read_bmp_size, set_default_lot_size` |
| `drawing_sketch` | `auto_dimension_sketch, end_sketch` |
| `drawing_view` | `activate_view, call_view` |
| `edges` | `get_contour_edges` |
| `edit_macro` | `is_swp_macro, validate_vba_macro` |
| `edit_sketch` | `auto_dimension_sketch, end_sketch` |
| `execute_macro` | `is_swp_macro, validate_vba_macro` |
| `exit_sketch` | `auto_dimension_sketch, end_sketch` |
| `explode_assembly` | `dissolve_assembly` |
| `export_drawing_pdf` | `export_to_pdf` |
| `export_file` | `write_macro_file` |
| `export_flat_pattern` | `_contains_any_pattern, circular_pattern` |
| `export_iges` | `export_to_iges` |
| `export_pdf` | `export_to_pdf` |
| `export_step` | `_parse_step, export_to_step` |
| `export_stl` | `export_to_stl` |
| `export_with_options` | `get_mass_property_override_options, get_topology_study_options` |
| `extract_drawing_template` | `find_template, get_default_template` |
| `extract_template` | `find_template, get_default_template` |
| `extrude_cut` | `_circle_cut, extrude_cut` |
| `file_properties` | `apply_visual_properties, set_custom_properties` |
| `fill_pattern` | `_contains_any_pattern, circular_pattern` |
| `fillet` | `fillet` |
| `fix_component` | `add_component, fix_component` |
| `flat_pattern_info` | `_file_info` |
| `generate_drawing_report` | `build_review_report, evaluate_review_report` |
| `generate_vba_batch_export` | `batch_export` |
| `generate_vba_code` | `extract_vba_code, locate_code` |
| `hide_component` | `add_component, fix_component` |
| `hole` | `create_blind_hole, create_counterbore_hole` |
| `hole_table` | `get_fastener_table` |
| `initialized_macro` | `is_swp_macro, validate_vba_macro` |
| `linear_pattern` | `_contains_any_pattern, circular_pattern` |
| `load_assembly` | `dissolve_assembly` |
| `macro_library` | `ensure_motion_type_library` |
| `manage_design_table` | `get_fastener_table` |
| `manage_file_properties` | `apply_visual_properties, set_custom_properties` |
| `materials` | `list_render_materials` |
| `measure_distance` | `add_mate_distance` |
| `mirror_component` | `add_component, fix_component` |
| `model_annotations` | `get_annotations` |
| `model_info` | `_file_info` |
| `model_view` | `activate_view, call_view` |
| `move_body` | `create_deformed_body, entities_on_body` |
| `move_component` | `add_component, fix_component` |
| `open_model` | `_comtypes_active_model, _extract_comtypes_model` |
| `optimize_macro` | `is_swp_macro, validate_vba_macro` |
| `pack_and_go_assembly` | `dissolve_assembly` |
| `point` | `click_point, first_result_point` |
| `polygon` | `sketch_polygon` |
| `projected_view` | `activate_view, call_view` |
| `rebuild_model` | `_comtypes_active_model, _extract_comtypes_model` |
| `rectangle` | `sketch_corner_rectangle, sketch_rectangle` |
| `reference_point` | `click_point, first_result_point` |
| `relation` | `add_sketch_relation` |
| `replace_component` | `add_component, fix_component` |
| `revision_table` | `get_fastener_table` |
| `rib` | `rib` |
| `run_macro` | `is_swp_macro, validate_vba_macro` |
| `run_vba_code` | `extract_vba_code, locate_code` |
| `run_vba_macro` | `is_swp_macro, validate_vba_macro` |
| `save_all` | `fill_all, locate_all` |
| `save_assembly` | `dissolve_assembly` |
| `save_file` | `write_macro_file` |
| `save_template_to_library` | `ensure_motion_type_library` |
| `save_to_template_library` | `ensure_motion_type_library` |
| `scale_body` | `create_deformed_body, entities_on_body` |
| `section_view` | `activate_view, call_view` |
| `security_info` | `_file_info` |
| `select_entity` | `get_assembly_entity, get_component_feature_entity` |
| `setup_template_positions` | `validate_hole_positions` |
| `shell` | `shell` |
| `sketch` | `auto_dimension_sketch, end_sketch` |
| `sketch_arc` | `sketch_arc` |
| `sketch_circle` | `sketch_circle` |
| `sketch_circular_pattern` | `_contains_any_pattern, circular_pattern` |
| `sketch_constraint` | `create_factor_of_safety_constraint, create_mass_constraint` |
| `sketch_linear_pattern` | `_contains_any_pattern, circular_pattern` |
| `sketch_polygon` | `sketch_polygon` |
| `sketch_rectangle` | `sketch_corner_rectangle, sketch_rectangle` |
| `sketch_segments` | `get_sketch_segments, group_coaxial_hole_segments` |
| `sketch_spline` | `sketch_spline` |
| `sketch_text` | `get_text, set_text` |
| `sketch_tutorial_simple_hole` | `create_blind_hole, create_counterbore_hole` |
| `slot` | `create_semicircular_slot, sketch_slot` |
| `spline` | `sketch_spline` |
| `split_body` | `create_deformed_body, entities_on_body` |
| `structural_member` | `_optional_com_member, _safe_com_member` |
| `suppress_component` | `add_component, fix_component` |
| `template` | `find_template, get_default_template` |
| `template_custom_properties` | `apply_visual_properties, set_custom_properties` |
| `template_library` | `ensure_motion_type_library` |
| `tutorial_simple_hole` | `create_blind_hole, create_counterbore_hole` |
| `view` | `activate_view, call_view` |
| `view_orientation` | `get_view_orientation, set_view_orientation` |
| `zoom_to_fit` | `zoom_to_fit` |

## 真缺（132）

| 缺口操作 | 我们的候选 |
|---|---|
| `activate_sheet` | — |
| `analyze_drawing_comprehensive` | — |
| `analyze_drawing_dimensions` | — |
| `analyze_drawing_views` | — |
| `annotation` | — |
| `api_automation` | — |
| `assembly_mates` | — |
| `auto_center_marks` | — |
| `background` | — |
| `balloon` | — |
| `batch_execute_macros` | — |
| `batch_file_operations` | — |
| `batch_operations` | — |
| `batch_run_macros` | — |
| `batch_vba` | — |
| `bbox` | — |
| `capture_screenshot` | — |
| `centerline` | — |
| `check_drawing_compliance` | — |
| `check_errors` | — |
| `check_sketch_fully_defined` | — |
| `compare_drawing_versions` | — |
| `composite_curve` | — |
| `configurations_batch` | — |
| `convert_entities` | — |
| `delete_equation` | — |
| `design_table_refresh` | — |
| `diagnose_macro_execution` | — |
| `display_states` | — |
| `dome` | — |
| `drawing_dimensions` | — |
| `drawing_tables` | — |
| `drawing_vba` | — |
| `drawing_views` | — |
| `ellipse` | — |
| `end_cap` | — |
| `equation` | — |
| `error_handling` | — |
| `execute_workflow` | — |
| `export_drawing_dwg` | — |
| `export_dwg` | — |
| `export_image` | — |
| `export_vba` | — |
| `extrude` | — |
| `faces` | — |
| `feature_vba` | — |
| `flatten_sheet_metal` | — |
| `fold` | — |
| `gdt` | — |
| `generate_vba_assembly_insert` | — |
| `generate_vba_assembly_mates` | — |
| `generate_vba_drawing_dimensions` | — |
| `generate_vba_drawing_views` | — |
| `generate_vba_extrusion` | — |
| `generate_vba_file_operations` | — |
| `generate_vba_macro_recorder` | — |
| `generate_vba_part_modeling` | — |
| `generate_vba_revolve` | — |
| `generate_vba_script` | — |
| `global_var` | — |
| `helix` | — |
| `hem` | — |
| `hide_all_planes` | — |
| `hide_all_sketches` | — |
| `interference` | — |
| `intersect` | — |
| `jog` | — |
| `knit_surfaces` | — |
| `link_dimension_to_equation` | — |
| `macro_recording` | — |
| `mass_props` | — |
| `mates` | — |
| `measure` | — |
| `mirror` | — |
| `native_macro_recording` | — |
| `operations` | — |
| `optimize_performance` | — |
| `pattern_circular` | — |
| `pattern_component_circular` | — |
| `pattern_component_linear` | — |
| `pause_resume_macro_recording` | — |
| `pdm_configure` | — |
| `pdm_operations` | — |
| `projected_curve` | — |
| `recording` | — |
| `ref_axis` | — |
| `ref_plane` | — |
| `reference_planes` | — |
| `revolve` | — |
| `run_simulation` | — |
| `save_as` | — |
| `save_as_copy` | — |
| `security` | — |
| `sensors` | — |
| `sheet` | — |
| `sheet_metal` | — |
| `sheets` | — |
| `show_all_planes` | — |
| `show_all_sketches` | — |
| `simple_extrude` | — |
| `simulation_setup` | — |
| `sketch_centerline` | — |
| `sketch_chamfer` | — |
| `sketch_construction` | — |
| `sketch_convert_entities` | — |
| `sketch_ellipse` | — |
| `sketch_extend` | — |
| `sketch_fillet` | — |
| `sketch_mirror` | — |
| `sketch_offset` | — |
| `sketch_trim` | — |
| `sketches` | — |
| `standard_views` | — |
| `stop_macro_recording` | — |
| `stop_native_macro_recording` | — |
| `stop_recording` | — |
| `suppress` | — |
| `surface_modeling` | — |
| `sweep` | — |
| `take_photoview_screenshot` | — |
| `tooling_split` | — |
| `trim_weldment` | — |
| `undo` | — |
| `unfold` | — |
| `units` | — |
| `update_title_block` | — |
| `validate_drawing_completeness` | — |
| `vertices` | — |
| `view_grayscale_enhanced` | — |
| `view_rotate` | — |
| `weld_symbol` | — |
| `wrap` | — |

