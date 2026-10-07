# 等级审计（union-level-audit）

> ⚠ **本文件是生成物** —— 由 `python scripts/gen_level_audit.py` 产出；**不要手改**（改了会被下次生成覆盖）。
> 生成日期：2026-10-08 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
> ⚑ 本文件是 `scripts/check_union_conventions.py` docstring 里 **R8** 承诺的那一份 —— 在 2026-10-01（轮 60）之前，**它只有承诺、没有生成器**（详见本脚本 docstring）。

## 一、总表（逐条可核）

| # | 能力 id | level | source | 有 evidence | 有 provenance |
|---|---|---|---|---|---|
| 1 | `analysis_run_readback` | `verified` | `original` | ✓ | — |
| 2 | `animation_export` | `stitched` | `original` | ✓ | — |
| 3 | `assembly_and_mates` | `stitched` | `mixed` | ✓ | — |
| 4 | `assembly_exploded_views` | `verified` | `original` | ✓ | — |
| 5 | `assembly_read` | `verified` | `original` | ✓ | — |
| 6 | `autocad_basic_drafting` | `not_implemented` | `upstream` | — | — |
| 7 | `autocad_dotnet_backend` | `verified` | `upstream` | ✓ | — |
| 8 | `autocad_headless_preview` | `verified` | `upstream` | ✓ | — |
| 9 | `autocad_script_backend` | `verified` | `upstream` | ✓ | — |
| 10 | `chamfer_fillet_on_selection` | `verified` | `original` | ✓ | — |
| 11 | `config_and_export` | `verified` | `original` | ✓ | — |
| 12 | `configurations_and_design_tables` | `verified` | `undetermined` | ✓ | — |
| 13 | `costing` | `verified` | `original` | ✓ | — |
| 14 | `costing_readback` | `verified` | `original` | ✓ | — |
| 15 | `costing_templates_and_defaults` | `verified` | `original` | ✓ | — |
| 16 | `coverage_gap_batch1` | `verified` | `original` | ✓ | — |
| 17 | `curve_and_split` | `verified` | `original` | ✓ | — |
| 18 | `curve_driven_pattern` | `stitched` | `original` | ✓ | — |
| 19 | `curve_through_xyz` | `verified` | `original` | ✓ | — |
| 20 | `custom_properties_and_bom` | `verified` | `upstream` | ✓ | — |
| 21 | `declarative_hole_creation` | `verified` | `original` | ✓ | — |
| 22 | `dfm_checks` | `verified` | `mixed` | ✓ | — |
| 23 | `display_states` | `verified` | `original` | ✓ | — |
| 24 | `document_dependencies` | `verified` | `original` | ✓ | — |
| 25 | `drawing_bom_balloons` | `verified` | `original` | ✓ | — |
| 26 | `drawing_center_lines` | `stitched` | `original` | ✓ | — |
| 27 | `drawing_current_sheet_query` | `verified` | `original` | ✓ | — |
| 28 | `drawing_dimension_insertion` | `not_implemented` | `mixed` | ✓ | — |
| 29 | `drawing_model_annotations` | `stitched` | `original` | ✓ | — |
| 30 | `drawing_view_operations` | `verified` | `original` | ✓ | — |
| 31 | `drawing_views_and_summary` | `verified` | `original` | ✓ | — |
| 32 | `drawings_and_bom` | `verified` | `mixed` | ✓ | — |
| 33 | `dxf_preview_scene` | `verified` | `upstream` | ✓ | — |
| 34 | `equations` | `verified` | `original` | ✓ | — |
| 35 | `explode_line_sketch` | `verified` | `original` | ✓ | — |
| 36 | `export_delivery` | `verified` | `upstream` | ✓ | — |
| 37 | `external_spur_gear_geometry` | `verified` | `upstream` | ✓ | — |
| 38 | `feature_build_extrude` | `verified` | `original` | ✓ | — |
| 39 | `feature_cosmetic_thread` | `verified` | `original` | ✓ | — |
| 40 | `feature_hole_wizard5` | `verified` | `original` | ✓ | — |
| 41 | `feature_loft_cut` | `verified` | `original` | ✓ | — |
| 42 | `feature_readback_criterion` | `verified` | `original` | ✓ | — |
| 43 | `feature_revolve_cut` | `verified` | `original` | ✓ | — |
| 44 | `file_custom_property_read` | `verified` | `original` | ✓ | — |
| 45 | `fillet_weld_bead` | `stitched` | `original` | ✓ | — |
| 46 | `flat_pattern_dxf` | `verified` | `original` | ✓ | — |
| 47 | `forming_tool` | `verified` | `original` | ✓ | — |
| 48 | `geometric_tolerance` | `stitched` | `original` | ✓ | — |
| 49 | `geometry_and_delivery_review` | `verified` | `upstream` | ✓ | — |
| 50 | `geometry_measurement` | `verified` | `original` | ✓ | — |
| 51 | `gtol_insert` | `verified` | `original` | ✓ | — |
| 52 | `headless_open_format_writing` | `verified` | `upstream` | ✓ | — |
| 53 | `helix_and_spiral` | `verified` | `original` | ✓ | — |
| 54 | `holes_and_finishing` | `verified` | `upstream` | ✓ | — |
| 55 | `loft_and_sweep` | `verified` | `mixed` | ✓ | — |
| 56 | `macro_execution` | `verified` | `original` | ✓ | — |
| 57 | `macro_native_recording` | `stitched` | `original` | ✓ | — |
| 58 | `mass_property_read` | `verified` | `original` | ✓ | — |
| 59 | `mesh_create_readback` | `verified` | `original` | ✓ | — |
| 60 | `mesh_size_sanity_gate` | `verified` | `original` | ✓ | — |
| 61 | `modeling_feature_readback_tools` | `verified` | `original` | ✓ | — |
| 62 | `mold_analysis` | `verified` | `original` | ✓ | — |
| 63 | `mold_parting_geometry` | `stitched` | `original` | ✓ | — |
| 64 | `mold_tools` | `stitched` | `mixed` | — | ✓ |
| 65 | `motion_study` | `verified` | `mixed` | ✓ | — |
| 66 | `motion_validation_and_preconditions` | `verified` | `original` | ✓ | — |
| 67 | `move_copy_body` | `verified` | `original` | ✓ | — |
| 68 | `pack_and_go` | `verified` | `upstream` | ✓ | — |
| 69 | `parameter_updates` | `verified` | `upstream` | ✓ | — |
| 70 | `part_and_features` | `verified` | `upstream` | ✓ | — |
| 71 | `part_intersect` | `verified` | `original` | ✓ | — |
| 72 | `pattern_and_mirror` | `verified` | `original` | ✓ | — |
| 73 | `pdm` | `not_implemented` | `original` | ✓ | — |
| 74 | `preview_and_review_report` | `verified` | `original` | ✓ | — |
| 75 | `ref_geometry` | `verified` | `original` | ✓ | — |
| 76 | `reference_axis` | `verified` | `mixed` | ✓ | — |
| 77 | `render_material_library` | `verified` | `original` | ✓ | — |
| 78 | `render_materials_and_appearance` | `verified` | `original` | ✓ | — |
| 79 | `replace_face` | `verified` | `original` | ✓ | — |
| 80 | `requirements_planning` | `verified` | `upstream` | ✓ | — |
| 81 | `routing` | `stitched` | `mixed` | ✓ | — |
| 82 | `scale_feature` | `verified` | `original` | ✓ | — |
| 83 | `section_properties` | `stitched` | `original` | ✓ | — |
| 84 | `select_by_ray` | `verified` | `original` | ✓ | — |
| 85 | `selection_helpers` | `verified` | `original` | ✓ | — |
| 86 | `session_rebuild` | `verified` | `original` | ✓ | — |
| 87 | `sheet_metal` | `verified` | `upstream` | ✓ | — |
| 88 | `sheet_metal_creation` | `stitched` | `original` | ✓ | — |
| 89 | `sheet_metal_fold` | `verified` | `original` | ✓ | — |
| 90 | `sheet_metal_hem` | `stitched` | `original` | ✓ | — |
| 91 | `sheet_metal_unfold` | `verified` | `original` | ✓ | — |
| 92 | `simulation_and_fea` | `verified` | `original` | ✓ | — |
| 93 | `simulation_load_family_breadth` | `verified` | `original` | ✓ | — |
| 94 | `simulation_loads_wiring` | `verified` | `original` | ✓ | — |
| 95 | `simulation_solver_options` | `verified` | `original` | ✓ | — |
| 96 | `simulation_study_create` | `verified` | `original` | ✓ | — |
| 97 | `sketch_build` | `verified` | `original` | ✓ | — |
| 98 | `sketch_chamfer` | `verified` | `original` | ✓ | — |
| 99 | `sketch_construction_geometry` | `verified` | `original` | ✓ | — |
| 100 | `sketch_dimension_horizontal` | `verified` | `original` | ✓ | — |
| 101 | `sketch_dimension_vertical` | `verified` | `original` | ✓ | — |
| 102 | `sketch_edit_ops` | `verified` | `original` | ✓ | — |
| 103 | `sketch_edit_ops_b3` | `verified` | `original` | ✓ | — |
| 104 | `sketch_equation_curve` | `verified` | `original` | ✓ | — |
| 105 | `sketch_line2` | `verified` | `original` | ✓ | — |
| 106 | `sketch_modify_ops` | `verified` | `original` | ✓ | — |
| 107 | `sketch_offset_on_surface` | `verified` | `original` | ✓ | — |
| 108 | `sketch_primitives_b1` | `verified` | `original` | ✓ | — |
| 109 | `sketch_query` | `verified` | `original` | ✓ | — |
| 110 | `sketch_rotate_or_copy_3d` | `verified` | `original` | ✓ | — |
| 111 | `sketch_slot_types` | `verified` | `original` | ✓ | — |
| 112 | `sketch_spline` | `verified` | `original` | ✓ | — |
| 113 | `sketch_spline3_2d` | `verified` | `original` | ✓ | — |
| 114 | `sketch_visibility` | `verified` | `original` | ✓ | — |
| 115 | `solidworks_addin_host` | `verified` | `upstream` | ✓ | — |
| 116 | `speedpak` | `verified` | `original` | ✓ | — |
| 117 | `standard_parts_toolbox` | `verified` | `original` | ✓ | — |
| 118 | `surface_delete_hole` | `verified` | `original` | ✓ | — |
| 119 | `surface_edit_ops` | `verified` | `original` | ✓ | — |
| 120 | `surface_features` | `verified` | `mixed` | ✓ | — |
| 121 | `surface_flatten` | `verified` | `original` | ✓ | — |
| 122 | `surface_modeling` | `stitched` | `mixed` | — | — |
| 123 | `surface_offset` | `verified` | `original` | ✓ | — |
| 124 | `surface_planar_region` | `verified` | `original` | ✓ | — |
| 125 | `surface_ref_ops` | `verified` | `original` | ✓ | — |
| 126 | `surface_revolve` | `verified` | `original` | ✓ | — |
| 127 | `surface_thicken_silent_noop` | `stitched` | `original` | ✓ | — |
| 128 | `surface_untrim` | `verified` | `original` | ✓ | — |
| 129 | `sweep_surface` | `verified` | `original` | ✓ | — |
| 130 | `topology_constraints_and_controls` | `verified` | `original` | ✓ | — |
| 131 | `topology_iteration_options_backend_limited` | `stitched` | `original` | ✓ | — |
| 132 | `topology_optimization` | `verified` | `original` | ✓ | — |
| 133 | `topology_readback` | `verified` | `original` | ✓ | — |
| 134 | `untrim_surface` | `stitched` | `original` | ✓ | — |
| 135 | `weld_symbol` | `verified` | `original` | ✓ | — |
| 136 | `weldment_cut_list` | `verified` | `original` | ✓ | — |
| 137 | `weldment_gusset` | `stitched` | `original` | ✓ | — |
| 138 | `weldment_profile_and_curve` | `verified` | `original` | ✓ | — |
| 139 | `weldment_trim` | `stitched` | `original` | ✓ | — |
| 140 | `weldments` | `verified` | `upstream` | ✓ | — |

**合计 140 条**。

## 二、`level` 分布

| level | 条数 |
|---|---|
| `indexed` | 0 |
| `not_implemented` | 3 |
| `source_verified` | 0 |
| `stitched` | 20 |
| `verified` | 117 |

## 三、`source` 分布

| source | 条数 |
|---|---|
| `merged` | 0 |
| `mixed` | 11 |
| `original` | 110 |
| `undetermined` | 1 |
| `upstream` | 18 |

## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）

| level \ source | merged | mixed | original | undetermined | upstream |
|---|---|---|---|---|---|
| `indexed` | 0 | 0 | 0 | 0 | 0 |
| `not_implemented` | 0 | 1 | 1 | 0 | 1 |
| `source_verified` | 0 | 0 | 0 | 0 | 0 |
| `stitched` | 0 | 4 | 16 | 0 | 0 |
| `verified` | 0 | 6 | 93 | 1 | 17 |

> ⚠ 读法：`level: verified` 说的是「**有我们自己的运行证据**」，
> `source: upstream` 说的是「**代码/广度来自上游**」—— **不是一回事**。

## 五、护城河三域（`AGENTS.md §〇`）

| 域 | level | source |
|---|---|---|
| `topology_optimization` | `verified` | `original` |
| `costing` | `verified` | `original` |
| `animation_export` | `stitched` | `original` |

## 六、不一致自检（**报告自己带「门禁怎么看」**）

| 检查 | 问题数 |
|---|---|
| `check_capabilities_schema()`（R1-R3/R6/R9/R10/**R12**/**R13**） | **0** |
| `check_capabilities_levels()`（规则 4 + R5/R7/R11） | **0** |

✅ **两项检查都为 0 问题** —— 本报告与门禁的判读一致。
