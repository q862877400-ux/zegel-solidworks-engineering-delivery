# 等级审计（union-level-audit）

> ⚠ **本文件是生成物** —— 由 `python scripts/gen_level_audit.py` 产出；**不要手改**（改了会被下次生成覆盖）。
> 生成日期：2026-10-04 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
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
| 22 | `drawing_current_sheet_query` | `verified` | `original` | ✓ | — |
| 23 | `drawing_dimension_insertion` | `not_implemented` | `mixed` | ✓ | — |
| 24 | `drawing_view_operations` | `verified` | `original` | ✓ | — |
| 25 | `drawing_views_and_summary` | `verified` | `original` | ✓ | — |
| 26 | `drawings_and_bom` | `verified` | `mixed` | ✓ | — |
| 27 | `dxf_preview_scene` | `verified` | `upstream` | ✓ | — |
| 28 | `equations` | `verified` | `original` | ✓ | — |
| 29 | `export_delivery` | `verified` | `upstream` | ✓ | — |
| 30 | `external_spur_gear_geometry` | `verified` | `upstream` | ✓ | — |
| 31 | `feature_build_extrude` | `verified` | `original` | ✓ | — |
| 32 | `feature_cosmetic_thread` | `verified` | `original` | ✓ | — |
| 33 | `feature_hole_wizard5` | `verified` | `original` | ✓ | — |
| 34 | `feature_loft_cut` | `verified` | `original` | ✓ | — |
| 35 | `feature_readback_criterion` | `verified` | `original` | ✓ | — |
| 36 | `feature_revolve_cut` | `verified` | `original` | ✓ | — |
| 37 | `file_custom_property_read` | `verified` | `original` | ✓ | — |
| 38 | `geometric_tolerance` | `stitched` | `original` | ✓ | — |
| 39 | `geometry_and_delivery_review` | `verified` | `upstream` | ✓ | — |
| 40 | `geometry_measurement` | `verified` | `original` | ✓ | — |
| 41 | `gtol_insert` | `verified` | `original` | ✓ | — |
| 42 | `headless_open_format_writing` | `verified` | `upstream` | ✓ | — |
| 43 | `helix_and_spiral` | `verified` | `original` | ✓ | — |
| 44 | `holes_and_finishing` | `verified` | `upstream` | ✓ | — |
| 45 | `loft_and_sweep` | `verified` | `mixed` | ✓ | — |
| 46 | `macro_execution` | `verified` | `original` | ✓ | — |
| 47 | `mass_property_read` | `verified` | `original` | ✓ | — |
| 48 | `mesh_create_readback` | `verified` | `original` | ✓ | — |
| 49 | `mesh_size_sanity_gate` | `verified` | `original` | ✓ | — |
| 50 | `modeling_feature_readback_tools` | `verified` | `original` | ✓ | — |
| 51 | `mold_analysis` | `verified` | `original` | ✓ | — |
| 52 | `mold_parting_geometry` | `stitched` | `original` | ✓ | — |
| 53 | `mold_tools` | `stitched` | `mixed` | — | ✓ |
| 54 | `motion_study` | `verified` | `mixed` | ✓ | — |
| 55 | `motion_validation_and_preconditions` | `verified` | `original` | ✓ | — |
| 56 | `pack_and_go` | `verified` | `upstream` | ✓ | — |
| 57 | `parameter_updates` | `verified` | `upstream` | ✓ | — |
| 58 | `part_and_features` | `verified` | `upstream` | ✓ | — |
| 59 | `pattern_and_mirror` | `verified` | `original` | ✓ | — |
| 60 | `preview_and_review_report` | `verified` | `original` | ✓ | — |
| 61 | `ref_geometry` | `verified` | `original` | ✓ | — |
| 62 | `reference_axis` | `verified` | `mixed` | ✓ | — |
| 63 | `render_material_library` | `verified` | `original` | ✓ | — |
| 64 | `render_materials_and_appearance` | `verified` | `original` | ✓ | — |
| 65 | `replace_face` | `verified` | `original` | ✓ | — |
| 66 | `requirements_planning` | `verified` | `upstream` | ✓ | — |
| 67 | `routing` | `stitched` | `mixed` | ✓ | — |
| 68 | `select_by_ray` | `verified` | `original` | ✓ | — |
| 69 | `selection_helpers` | `verified` | `original` | ✓ | — |
| 70 | `sheet_metal` | `verified` | `upstream` | ✓ | — |
| 71 | `sheet_metal_creation` | `stitched` | `original` | ✓ | — |
| 72 | `simulation_and_fea` | `verified` | `original` | ✓ | — |
| 73 | `simulation_load_family_breadth` | `verified` | `original` | ✓ | — |
| 74 | `simulation_loads_wiring` | `verified` | `original` | ✓ | — |
| 75 | `simulation_solver_options` | `verified` | `original` | ✓ | — |
| 76 | `simulation_study_create` | `verified` | `original` | ✓ | — |
| 77 | `sketch_build` | `verified` | `original` | ✓ | — |
| 78 | `sketch_chamfer` | `verified` | `original` | ✓ | — |
| 79 | `sketch_dimension_horizontal` | `verified` | `original` | ✓ | — |
| 80 | `sketch_dimension_vertical` | `verified` | `original` | ✓ | — |
| 81 | `sketch_edit_ops` | `verified` | `original` | ✓ | — |
| 82 | `sketch_edit_ops_b3` | `verified` | `original` | ✓ | — |
| 83 | `sketch_equation_curve` | `verified` | `original` | ✓ | — |
| 84 | `sketch_line2` | `verified` | `original` | ✓ | — |
| 85 | `sketch_modify_ops` | `verified` | `original` | ✓ | — |
| 86 | `sketch_offset_on_surface` | `verified` | `original` | ✓ | — |
| 87 | `sketch_primitives_b1` | `verified` | `original` | ✓ | — |
| 88 | `sketch_query` | `verified` | `original` | ✓ | — |
| 89 | `sketch_rotate_or_copy_3d` | `verified` | `original` | ✓ | — |
| 90 | `sketch_slot_types` | `verified` | `original` | ✓ | — |
| 91 | `sketch_spline` | `verified` | `original` | ✓ | — |
| 92 | `sketch_spline3_2d` | `verified` | `original` | ✓ | — |
| 93 | `solidworks_addin_host` | `verified` | `upstream` | ✓ | — |
| 94 | `standard_parts_toolbox` | `verified` | `original` | ✓ | — |
| 95 | `surface_delete_hole` | `verified` | `original` | ✓ | — |
| 96 | `surface_edit_ops` | `verified` | `original` | ✓ | — |
| 97 | `surface_features` | `verified` | `mixed` | ✓ | — |
| 98 | `surface_flatten` | `verified` | `original` | ✓ | — |
| 99 | `surface_modeling` | `stitched` | `mixed` | — | — |
| 100 | `surface_offset` | `verified` | `original` | ✓ | — |
| 101 | `surface_planar_region` | `verified` | `original` | ✓ | — |
| 102 | `surface_ref_ops` | `verified` | `original` | ✓ | — |
| 103 | `surface_revolve` | `verified` | `original` | ✓ | — |
| 104 | `surface_thicken_silent_noop` | `stitched` | `original` | ✓ | — |
| 105 | `surface_untrim` | `verified` | `original` | ✓ | — |
| 106 | `topology_constraints_and_controls` | `verified` | `original` | ✓ | — |
| 107 | `topology_iteration_options_backend_limited` | `stitched` | `original` | ✓ | — |
| 108 | `topology_optimization` | `verified` | `original` | ✓ | — |
| 109 | `topology_readback` | `verified` | `original` | ✓ | — |
| 110 | `weldment_cut_list` | `verified` | `original` | ✓ | — |
| 111 | `weldment_profile_and_curve` | `verified` | `original` | ✓ | — |
| 112 | `weldments` | `verified` | `upstream` | ✓ | — |

**合计 112 条**。

## 二、`level` 分布

| level | 条数 |
|---|---|
| `indexed` | 0 |
| `not_implemented` | 2 |
| `source_verified` | 0 |
| `stitched` | 10 |
| `verified` | 100 |

## 三、`source` 分布

| source | 条数 |
|---|---|
| `merged` | 0 |
| `mixed` | 11 |
| `original` | 82 |
| `undetermined` | 1 |
| `upstream` | 18 |

## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）

| level \ source | merged | mixed | original | undetermined | upstream |
|---|---|---|---|---|---|
| `indexed` | 0 | 0 | 0 | 0 | 0 |
| `not_implemented` | 0 | 1 | 0 | 0 | 1 |
| `source_verified` | 0 | 0 | 0 | 0 | 0 |
| `stitched` | 0 | 4 | 6 | 0 | 0 |
| `verified` | 0 | 6 | 76 | 1 | 17 |

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
