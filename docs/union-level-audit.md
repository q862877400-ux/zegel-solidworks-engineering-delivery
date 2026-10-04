# 等级审计（union-level-audit）

> ⚠ **本文件是生成物** —— 由 `python scripts/gen_level_audit.py` 产出；**不要手改**（改了会被下次生成覆盖）。
> 生成日期：2026-10-04 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
> ⚑ 本文件是 `scripts/check_union_conventions.py` docstring 里 **R8** 承诺的那一份 —— 在 2026-10-01（轮 60）之前，**它只有承诺、没有生成器**（详见本脚本 docstring）。

## 一、总表（逐条可核）

| # | 能力 id | level | source | 有 evidence | 有 provenance |
|---|---|---|---|---|---|
| 1 | `analysis_run_readback` | `stitched` | `original` | ✓ | — |
| 2 | `animation_export` | `stitched` | `original` | ✓ | — |
| 3 | `assembly_and_mates` | `stitched` | `mixed` | ✓ | — |
| 4 | `assembly_read` | `verified` | `original` | ✓ | — |
| 5 | `autocad_basic_drafting` | `not_implemented` | `upstream` | — | — |
| 6 | `autocad_dotnet_backend` | `verified` | `upstream` | ✓ | — |
| 7 | `autocad_headless_preview` | `verified` | `upstream` | ✓ | — |
| 8 | `autocad_script_backend` | `verified` | `upstream` | ✓ | — |
| 9 | `chamfer_fillet_on_selection` | `verified` | `original` | ✓ | — |
| 10 | `config_and_export` | `verified` | `original` | ✓ | — |
| 11 | `configurations_and_design_tables` | `verified` | `undetermined` | ✓ | — |
| 12 | `costing` | `verified` | `original` | ✓ | — |
| 13 | `costing_readback` | `verified` | `original` | ✓ | — |
| 14 | `costing_templates_and_defaults` | `verified` | `original` | ✓ | — |
| 15 | `coverage_gap_batch1` | `verified` | `original` | ✓ | — |
| 16 | `curve_and_split` | `verified` | `original` | ✓ | — |
| 17 | `curve_through_xyz` | `verified` | `original` | ✓ | — |
| 18 | `custom_properties_and_bom` | `verified` | `upstream` | ✓ | — |
| 19 | `declarative_hole_creation` | `verified` | `original` | ✓ | — |
| 20 | `dfm_checks` | `verified` | `mixed` | ✓ | — |
| 21 | `drawing_current_sheet_query` | `verified` | `original` | ✓ | — |
| 22 | `drawing_dimension_insertion` | `not_implemented` | `mixed` | ✓ | — |
| 23 | `drawing_view_operations` | `verified` | `original` | ✓ | — |
| 24 | `drawing_views_and_summary` | `verified` | `original` | ✓ | — |
| 25 | `drawings_and_bom` | `verified` | `mixed` | ✓ | — |
| 26 | `dxf_preview_scene` | `verified` | `upstream` | ✓ | — |
| 27 | `equations` | `verified` | `original` | ✓ | — |
| 28 | `export_delivery` | `verified` | `upstream` | ✓ | — |
| 29 | `external_spur_gear_geometry` | `verified` | `upstream` | ✓ | — |
| 30 | `feature_build_extrude` | `verified` | `original` | ✓ | — |
| 31 | `feature_cosmetic_thread` | `verified` | `original` | ✓ | — |
| 32 | `feature_hole_wizard5` | `verified` | `original` | ✓ | — |
| 33 | `feature_loft_cut` | `verified` | `original` | ✓ | — |
| 34 | `feature_readback_criterion` | `verified` | `original` | ✓ | — |
| 35 | `feature_revolve_cut` | `verified` | `original` | ✓ | — |
| 36 | `file_custom_property_read` | `verified` | `original` | ✓ | — |
| 37 | `geometric_tolerance` | `stitched` | `original` | ✓ | — |
| 38 | `geometry_and_delivery_review` | `verified` | `upstream` | ✓ | — |
| 39 | `geometry_measurement` | `verified` | `original` | ✓ | — |
| 40 | `gtol_insert` | `verified` | `original` | ✓ | — |
| 41 | `headless_open_format_writing` | `verified` | `upstream` | ✓ | — |
| 42 | `helix_and_spiral` | `verified` | `original` | ✓ | — |
| 43 | `holes_and_finishing` | `verified` | `upstream` | ✓ | — |
| 44 | `loft_and_sweep` | `verified` | `mixed` | ✓ | — |
| 45 | `mass_property_read` | `verified` | `original` | ✓ | — |
| 46 | `mesh_create_readback` | `verified` | `original` | ✓ | — |
| 47 | `mesh_size_sanity_gate` | `verified` | `original` | ✓ | — |
| 48 | `modeling_feature_readback_tools` | `verified` | `original` | ✓ | — |
| 49 | `mold_analysis` | `verified` | `original` | ✓ | — |
| 50 | `mold_parting_geometry` | `stitched` | `original` | ✓ | — |
| 51 | `mold_tools` | `stitched` | `mixed` | — | ✓ |
| 52 | `motion_study` | `verified` | `mixed` | ✓ | — |
| 53 | `motion_validation_and_preconditions` | `verified` | `original` | ✓ | — |
| 54 | `pack_and_go` | `verified` | `upstream` | ✓ | — |
| 55 | `parameter_updates` | `verified` | `upstream` | ✓ | — |
| 56 | `part_and_features` | `verified` | `upstream` | ✓ | — |
| 57 | `pattern_and_mirror` | `verified` | `original` | ✓ | — |
| 58 | `preview_and_review_report` | `verified` | `original` | ✓ | — |
| 59 | `ref_geometry` | `verified` | `original` | ✓ | — |
| 60 | `reference_axis` | `verified` | `mixed` | ✓ | — |
| 61 | `render_material_library` | `verified` | `original` | ✓ | — |
| 62 | `render_materials_and_appearance` | `verified` | `original` | ✓ | — |
| 63 | `replace_face` | `verified` | `original` | ✓ | — |
| 64 | `requirements_planning` | `verified` | `upstream` | ✓ | — |
| 65 | `routing` | `stitched` | `mixed` | ✓ | — |
| 66 | `select_by_ray` | `verified` | `original` | ✓ | — |
| 67 | `selection_helpers` | `verified` | `original` | ✓ | — |
| 68 | `sheet_metal` | `verified` | `upstream` | ✓ | — |
| 69 | `sheet_metal_creation` | `stitched` | `original` | ✓ | — |
| 70 | `simulation_and_fea` | `verified` | `original` | ✓ | — |
| 71 | `simulation_load_family_breadth` | `verified` | `original` | ✓ | — |
| 72 | `simulation_loads_wiring` | `verified` | `original` | ✓ | — |
| 73 | `simulation_solver_options` | `verified` | `original` | ✓ | — |
| 74 | `simulation_study_create` | `verified` | `original` | ✓ | — |
| 75 | `sketch_build` | `verified` | `original` | ✓ | — |
| 76 | `sketch_chamfer` | `verified` | `original` | ✓ | — |
| 77 | `sketch_dimension_horizontal` | `verified` | `original` | ✓ | — |
| 78 | `sketch_dimension_vertical` | `verified` | `original` | ✓ | — |
| 79 | `sketch_edit_ops` | `verified` | `original` | ✓ | — |
| 80 | `sketch_edit_ops_b3` | `verified` | `original` | ✓ | — |
| 81 | `sketch_equation_curve` | `verified` | `original` | ✓ | — |
| 82 | `sketch_line2` | `verified` | `original` | ✓ | — |
| 83 | `sketch_modify_ops` | `verified` | `original` | ✓ | — |
| 84 | `sketch_offset_on_surface` | `verified` | `original` | ✓ | — |
| 85 | `sketch_primitives_b1` | `verified` | `original` | ✓ | — |
| 86 | `sketch_query` | `verified` | `original` | ✓ | — |
| 87 | `sketch_rotate_or_copy_3d` | `verified` | `original` | ✓ | — |
| 88 | `sketch_slot_types` | `verified` | `original` | ✓ | — |
| 89 | `sketch_spline` | `verified` | `original` | ✓ | — |
| 90 | `sketch_spline3_2d` | `verified` | `original` | ✓ | — |
| 91 | `solidworks_addin_host` | `verified` | `upstream` | ✓ | — |
| 92 | `standard_parts_toolbox` | `verified` | `original` | ✓ | — |
| 93 | `surface_delete_hole` | `verified` | `original` | ✓ | — |
| 94 | `surface_edit_ops` | `verified` | `original` | ✓ | — |
| 95 | `surface_features` | `verified` | `mixed` | ✓ | — |
| 96 | `surface_flatten` | `verified` | `original` | ✓ | — |
| 97 | `surface_modeling` | `stitched` | `mixed` | — | — |
| 98 | `surface_offset` | `verified` | `original` | ✓ | — |
| 99 | `surface_planar_region` | `verified` | `original` | ✓ | — |
| 100 | `surface_ref_ops` | `verified` | `original` | ✓ | — |
| 101 | `surface_revolve` | `verified` | `original` | ✓ | — |
| 102 | `surface_thicken_silent_noop` | `stitched` | `original` | ✓ | — |
| 103 | `surface_untrim` | `verified` | `original` | ✓ | — |
| 104 | `topology_constraints_and_controls` | `verified` | `original` | ✓ | — |
| 105 | `topology_iteration_options_backend_limited` | `stitched` | `original` | ✓ | — |
| 106 | `topology_optimization` | `verified` | `original` | ✓ | — |
| 107 | `topology_readback` | `verified` | `original` | ✓ | — |
| 108 | `weldment_cut_list` | `verified` | `original` | ✓ | — |
| 109 | `weldment_profile_and_curve` | `verified` | `original` | ✓ | — |
| 110 | `weldments` | `verified` | `upstream` | ✓ | — |

**合计 110 条**。

## 二、`level` 分布

| level | 条数 |
|---|---|
| `indexed` | 0 |
| `not_implemented` | 2 |
| `source_verified` | 0 |
| `stitched` | 11 |
| `verified` | 97 |

## 三、`source` 分布

| source | 条数 |
|---|---|
| `merged` | 0 |
| `mixed` | 11 |
| `original` | 80 |
| `undetermined` | 1 |
| `upstream` | 18 |

## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）

| level \ source | merged | mixed | original | undetermined | upstream |
|---|---|---|---|---|---|
| `indexed` | 0 | 0 | 0 | 0 | 0 |
| `not_implemented` | 0 | 1 | 0 | 0 | 1 |
| `source_verified` | 0 | 0 | 0 | 0 | 0 |
| `stitched` | 0 | 4 | 7 | 0 | 0 |
| `verified` | 0 | 6 | 73 | 1 | 17 |

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
