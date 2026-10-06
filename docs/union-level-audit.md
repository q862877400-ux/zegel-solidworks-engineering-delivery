# 等级审计（union-level-audit）

> ⚠ **本文件是生成物** —— 由 `python scripts/gen_level_audit.py` 产出；**不要手改**（改了会被下次生成覆盖）。
> 生成日期：2026-10-07 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
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
| 18 | `curve_through_xyz` | `verified` | `original` | ✓ | — |
| 19 | `custom_properties_and_bom` | `verified` | `upstream` | ✓ | — |
| 20 | `declarative_hole_creation` | `verified` | `original` | ✓ | — |
| 21 | `dfm_checks` | `verified` | `mixed` | ✓ | — |
| 22 | `display_states` | `verified` | `original` | ✓ | — |
| 23 | `document_dependencies` | `verified` | `original` | ✓ | — |
| 24 | `drawing_bom_balloons` | `verified` | `original` | ✓ | — |
| 25 | `drawing_center_lines` | `stitched` | `original` | ✓ | — |
| 26 | `drawing_current_sheet_query` | `verified` | `original` | ✓ | — |
| 27 | `drawing_dimension_insertion` | `not_implemented` | `mixed` | ✓ | — |
| 28 | `drawing_model_annotations` | `stitched` | `original` | ✓ | — |
| 29 | `drawing_view_operations` | `verified` | `original` | ✓ | — |
| 30 | `drawing_views_and_summary` | `verified` | `original` | ✓ | — |
| 31 | `drawings_and_bom` | `verified` | `mixed` | ✓ | — |
| 32 | `dxf_preview_scene` | `verified` | `upstream` | ✓ | — |
| 33 | `equations` | `verified` | `original` | ✓ | — |
| 34 | `export_delivery` | `verified` | `upstream` | ✓ | — |
| 35 | `external_spur_gear_geometry` | `verified` | `upstream` | ✓ | — |
| 36 | `feature_build_extrude` | `verified` | `original` | ✓ | — |
| 37 | `feature_cosmetic_thread` | `verified` | `original` | ✓ | — |
| 38 | `feature_hole_wizard5` | `verified` | `original` | ✓ | — |
| 39 | `feature_loft_cut` | `verified` | `original` | ✓ | — |
| 40 | `feature_readback_criterion` | `verified` | `original` | ✓ | — |
| 41 | `feature_revolve_cut` | `verified` | `original` | ✓ | — |
| 42 | `file_custom_property_read` | `verified` | `original` | ✓ | — |
| 43 | `fillet_weld_bead` | `stitched` | `official` | ✓ | — |
| 44 | `geometric_tolerance` | `stitched` | `original` | ✓ | — |
| 45 | `geometry_and_delivery_review` | `verified` | `upstream` | ✓ | — |
| 46 | `geometry_measurement` | `verified` | `original` | ✓ | — |
| 47 | `gtol_insert` | `verified` | `original` | ✓ | — |
| 48 | `headless_open_format_writing` | `verified` | `upstream` | ✓ | — |
| 49 | `helix_and_spiral` | `verified` | `original` | ✓ | — |
| 50 | `holes_and_finishing` | `verified` | `upstream` | ✓ | — |
| 51 | `loft_and_sweep` | `verified` | `mixed` | ✓ | — |
| 52 | `macro_execution` | `verified` | `original` | ✓ | — |
| 53 | `macro_native_recording` | `stitched` | `original` | ✓ | — |
| 54 | `mass_property_read` | `verified` | `original` | ✓ | — |
| 55 | `mesh_create_readback` | `verified` | `original` | ✓ | — |
| 56 | `mesh_size_sanity_gate` | `verified` | `original` | ✓ | — |
| 57 | `modeling_feature_readback_tools` | `verified` | `original` | ✓ | — |
| 58 | `mold_analysis` | `verified` | `original` | ✓ | — |
| 59 | `mold_parting_geometry` | `stitched` | `original` | ✓ | — |
| 60 | `mold_tools` | `stitched` | `mixed` | — | ✓ |
| 61 | `motion_study` | `verified` | `mixed` | ✓ | — |
| 62 | `motion_validation_and_preconditions` | `verified` | `original` | ✓ | — |
| 63 | `move_copy_body` | `verified` | `original` | ✓ | — |
| 64 | `pack_and_go` | `verified` | `upstream` | ✓ | — |
| 65 | `parameter_updates` | `verified` | `upstream` | ✓ | — |
| 66 | `part_and_features` | `verified` | `upstream` | ✓ | — |
| 67 | `part_intersect` | `verified` | `original` | ✓ | — |
| 68 | `pattern_and_mirror` | `verified` | `original` | ✓ | — |
| 69 | `preview_and_review_report` | `verified` | `original` | ✓ | — |
| 70 | `ref_geometry` | `verified` | `original` | ✓ | — |
| 71 | `reference_axis` | `verified` | `mixed` | ✓ | — |
| 72 | `render_material_library` | `verified` | `original` | ✓ | — |
| 73 | `render_materials_and_appearance` | `verified` | `original` | ✓ | — |
| 74 | `replace_face` | `verified` | `original` | ✓ | — |
| 75 | `requirements_planning` | `verified` | `upstream` | ✓ | — |
| 76 | `routing` | `stitched` | `mixed` | ✓ | — |
| 77 | `scale_feature` | `verified` | `official` | ✓ | — |
| 78 | `section_properties` | `stitched` | `official` | ✓ | — |
| 79 | `select_by_ray` | `verified` | `original` | ✓ | — |
| 80 | `selection_helpers` | `verified` | `original` | ✓ | — |
| 81 | `session_rebuild` | `verified` | `original` | ✓ | — |
| 82 | `sheet_metal` | `verified` | `upstream` | ✓ | — |
| 83 | `sheet_metal_creation` | `stitched` | `original` | ✓ | — |
| 84 | `sheet_metal_fold` | `verified` | `original` | ✓ | — |
| 85 | `sheet_metal_hem` | `stitched` | `original` | ✓ | — |
| 86 | `sheet_metal_unfold` | `verified` | `original` | ✓ | — |
| 87 | `simulation_and_fea` | `verified` | `original` | ✓ | — |
| 88 | `simulation_load_family_breadth` | `verified` | `original` | ✓ | — |
| 89 | `simulation_loads_wiring` | `verified` | `original` | ✓ | — |
| 90 | `simulation_solver_options` | `verified` | `original` | ✓ | — |
| 91 | `simulation_study_create` | `verified` | `original` | ✓ | — |
| 92 | `sketch_build` | `verified` | `original` | ✓ | — |
| 93 | `sketch_chamfer` | `verified` | `original` | ✓ | — |
| 94 | `sketch_construction_geometry` | `verified` | `original` | ✓ | — |
| 95 | `sketch_dimension_horizontal` | `verified` | `original` | ✓ | — |
| 96 | `sketch_dimension_vertical` | `verified` | `original` | ✓ | — |
| 97 | `sketch_edit_ops` | `verified` | `original` | ✓ | — |
| 98 | `sketch_edit_ops_b3` | `verified` | `original` | ✓ | — |
| 99 | `sketch_equation_curve` | `verified` | `original` | ✓ | — |
| 100 | `sketch_line2` | `verified` | `original` | ✓ | — |
| 101 | `sketch_modify_ops` | `verified` | `original` | ✓ | — |
| 102 | `sketch_offset_on_surface` | `verified` | `original` | ✓ | — |
| 103 | `sketch_primitives_b1` | `verified` | `original` | ✓ | — |
| 104 | `sketch_query` | `verified` | `original` | ✓ | — |
| 105 | `sketch_rotate_or_copy_3d` | `verified` | `original` | ✓ | — |
| 106 | `sketch_slot_types` | `verified` | `original` | ✓ | — |
| 107 | `sketch_spline` | `verified` | `original` | ✓ | — |
| 108 | `sketch_spline3_2d` | `verified` | `original` | ✓ | — |
| 109 | `sketch_visibility` | `verified` | `original` | ✓ | — |
| 110 | `solidworks_addin_host` | `verified` | `upstream` | ✓ | — |
| 111 | `standard_parts_toolbox` | `verified` | `original` | ✓ | — |
| 112 | `surface_delete_hole` | `verified` | `original` | ✓ | — |
| 113 | `surface_edit_ops` | `verified` | `original` | ✓ | — |
| 114 | `surface_features` | `verified` | `mixed` | ✓ | — |
| 115 | `surface_flatten` | `verified` | `original` | ✓ | — |
| 116 | `surface_modeling` | `stitched` | `mixed` | — | — |
| 117 | `surface_offset` | `verified` | `original` | ✓ | — |
| 118 | `surface_planar_region` | `verified` | `original` | ✓ | — |
| 119 | `surface_ref_ops` | `verified` | `original` | ✓ | — |
| 120 | `surface_revolve` | `verified` | `original` | ✓ | — |
| 121 | `surface_thicken_silent_noop` | `stitched` | `original` | ✓ | — |
| 122 | `surface_untrim` | `verified` | `original` | ✓ | — |
| 123 | `sweep_surface` | `verified` | `official` | ✓ | — |
| 124 | `topology_constraints_and_controls` | `verified` | `original` | ✓ | — |
| 125 | `topology_iteration_options_backend_limited` | `stitched` | `original` | ✓ | — |
| 126 | `topology_optimization` | `verified` | `original` | ✓ | — |
| 127 | `topology_readback` | `verified` | `original` | ✓ | — |
| 128 | `untrim_surface` | `stitched` | `official` | ✓ | — |
| 129 | `weldment_cut_list` | `verified` | `original` | ✓ | — |
| 130 | `weldment_gusset` | `stitched` | `official` | ✓ | — |
| 131 | `weldment_profile_and_curve` | `verified` | `original` | ✓ | — |
| 132 | `weldment_trim` | `stitched` | `official` | ✓ | — |
| 133 | `weldments` | `verified` | `upstream` | ✓ | — |

**合计 133 条**。

## 二、`level` 分布

| level | 条数 |
|---|---|
| `indexed` | 0 |
| `not_implemented` | 2 |
| `source_verified` | 0 |
| `stitched` | 19 |
| `verified` | 112 |

## 三、`source` 分布

| source | 条数 |
|---|---|
| `merged` | 0 |
| `mixed` | 11 |
| `original` | 96 |
| `undetermined` | 1 |
| `upstream` | 18 |

## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）

| level \ source | merged | mixed | original | undetermined | upstream |
|---|---|---|---|---|---|
| `indexed` | 0 | 0 | 0 | 0 | 0 |
| `not_implemented` | 0 | 1 | 0 | 0 | 1 |
| `source_verified` | 0 | 0 | 0 | 0 | 0 |
| `stitched` | 0 | 4 | 10 | 0 | 0 |
| `verified` | 0 | 6 | 86 | 1 | 17 |

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
| `check_capabilities_schema()`（R1-R3/R6/R9/R10/**R12**/**R13**） | **7** |
| `check_capabilities_levels()`（规则 4 + R5/R7/R11） | **7** |

⚠ **有问题**（逐条）：

* 能力 section_properties 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 scale_feature 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 untrim_surface 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 sweep_surface 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 weldment_trim 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 weldment_gusset 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 fillet_weld_bead 的 source='official' 不在枚举 ['merged', 'mixed', 'original', 'undetermined', 'upstream'] 内
* 能力 section_properties 的 allowed_modes 含非法值: ['assembly', 'part']
* 能力 scale_feature 的 allowed_modes 含非法值: ['assembly', 'part']
* 能力 untrim_surface 的 allowed_modes 含非法值: ['part']
* 能力 sweep_surface 的 allowed_modes 含非法值: ['part']
* 能力 weldment_trim 的 allowed_modes 含非法值: ['part']
* 能力 weldment_gusset 的 allowed_modes 含非法值: ['part']
* 能力 fillet_weld_bead 的 allowed_modes 含非法值: ['part']
