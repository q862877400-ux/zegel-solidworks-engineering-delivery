# 等级审计（union-level-audit）

> ⚠ **本文件是生成物** —— 由 `python scripts/gen_level_audit.py` 产出；**不要手改**（改了会被下次生成覆盖）。
> 生成日期：2026-10-03 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
> ⚑ 本文件是 `scripts/check_union_conventions.py` docstring 里 **R8** 承诺的那一份 —— 在 2026-10-01（轮 60）之前，**它只有承诺、没有生成器**（详见本脚本 docstring）。

## 一、总表（逐条可核）

| # | 能力 id | level | source | 有 evidence | 有 provenance |
|---|---|---|---|---|---|
| 1 | `analysis_run_readback` | `stitched` | `original` | ✓ | — |
| 2 | `animation_export` | `stitched` | `original` | ✓ | — |
| 3 | `assembly_and_mates` | `verified` | `mixed` | ✓ | — |
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
| 15 | `curve_and_split` | `verified` | `original` | ✓ | — |
| 16 | `custom_properties_and_bom` | `verified` | `upstream` | ✓ | — |
| 17 | `declarative_hole_creation` | `verified` | `original` | ✓ | — |
| 18 | `dfm_checks` | `verified` | `mixed` | ✓ | — |
| 19 | `drawing_current_sheet_query` | `verified` | `original` | ✓ | — |
| 20 | `drawing_dimension_insertion` | `verified` | `mixed` | ✓ | — |
| 21 | `drawing_view_operations` | `verified` | `original` | ✓ | — |
| 22 | `drawing_views_and_summary` | `verified` | `original` | ✓ | — |
| 23 | `drawings_and_bom` | `verified` | `mixed` | ✓ | — |
| 24 | `dxf_preview_scene` | `verified` | `upstream` | ✓ | — |
| 25 | `equations` | `verified` | `original` | ✓ | — |
| 26 | `export_delivery` | `verified` | `upstream` | ✓ | — |
| 27 | `external_spur_gear_geometry` | `verified` | `upstream` | ✓ | — |
| 28 | `feature_build_extrude` | `verified` | `original` | ✓ | — |
| 29 | `feature_cosmetic_thread` | `verified` | `original` | ✓ | — |
| 30 | `feature_loft_cut` | `verified` | `original` | ✓ | — |
| 31 | `feature_readback_criterion` | `verified` | `original` | ✓ | — |
| 32 | `feature_revolve_cut` | `verified` | `original` | ✓ | — |
| 33 | `file_custom_property_read` | `verified` | `original` | ✓ | — |
| 34 | `geometric_tolerance` | `stitched` | `original` | ✓ | — |
| 35 | `geometry_and_delivery_review` | `verified` | `upstream` | ✓ | — |
| 36 | `geometry_measurement` | `verified` | `original` | ✓ | — |
| 37 | `gtol_insert` | `verified` | `original` | ✓ | — |
| 38 | `headless_open_format_writing` | `verified` | `upstream` | ✓ | — |
| 39 | `helix_and_spiral` | `verified` | `original` | ✓ | — |
| 40 | `holes_and_finishing` | `verified` | `upstream` | ✓ | — |
| 41 | `loft_and_sweep` | `verified` | `mixed` | ✓ | — |
| 42 | `mass_property_read` | `verified` | `original` | ✓ | — |
| 43 | `mesh_create_readback` | `verified` | `original` | ✓ | — |
| 44 | `mesh_size_sanity_gate` | `verified` | `original` | ✓ | — |
| 45 | `modeling_feature_readback_tools` | `verified` | `original` | ✓ | — |
| 46 | `mold_analysis` | `verified` | `original` | ✓ | — |
| 47 | `mold_parting_geometry` | `stitched` | `original` | ✓ | — |
| 48 | `mold_tools` | `stitched` | `mixed` | — | ✓ |
| 49 | `motion_study` | `verified` | `mixed` | ✓ | — |
| 50 | `motion_validation_and_preconditions` | `verified` | `original` | ✓ | — |
| 51 | `pack_and_go` | `verified` | `upstream` | ✓ | — |
| 52 | `parameter_updates` | `verified` | `upstream` | ✓ | — |
| 53 | `part_and_features` | `verified` | `upstream` | ✓ | — |
| 54 | `pattern_and_mirror` | `verified` | `original` | ✓ | — |
| 55 | `preview_and_review_report` | `verified` | `original` | ✓ | — |
| 56 | `ref_geometry` | `verified` | `original` | ✓ | — |
| 57 | `reference_axis` | `verified` | `mixed` | ✓ | — |
| 58 | `render_material_library` | `verified` | `original` | ✓ | — |
| 59 | `render_materials_and_appearance` | `verified` | `original` | ✓ | — |
| 60 | `replace_face` | `verified` | `original` | ✓ | — |
| 61 | `requirements_planning` | `verified` | `upstream` | ✓ | — |
| 62 | `routing` | `stitched` | `mixed` | ✓ | — |
| 63 | `selection_helpers` | `verified` | `original` | ✓ | — |
| 64 | `sheet_metal` | `verified` | `upstream` | ✓ | — |
| 65 | `sheet_metal_creation` | `stitched` | `original` | ✓ | — |
| 66 | `simulation_and_fea` | `verified` | `original` | ✓ | — |
| 67 | `simulation_load_family_breadth` | `verified` | `original` | ✓ | — |
| 68 | `simulation_loads_wiring` | `verified` | `original` | ✓ | — |
| 69 | `simulation_solver_options` | `verified` | `original` | ✓ | — |
| 70 | `simulation_study_create` | `verified` | `original` | ✓ | — |
| 71 | `sketch_build` | `verified` | `original` | ✓ | — |
| 72 | `sketch_chamfer` | `verified` | `original` | ✓ | — |
| 73 | `sketch_dimension_horizontal` | `verified` | `original` | ✓ | — |
| 74 | `sketch_dimension_vertical` | `verified` | `original` | ✓ | — |
| 75 | `sketch_edit_ops` | `stitched` | `original` | ✓ | — |
| 76 | `sketch_edit_ops_b3` | `verified` | `original` | ✓ | — |
| 77 | `sketch_line2` | `verified` | `original` | ✓ | — |
| 78 | `sketch_modify_ops` | `verified` | `original` | ✓ | — |
| 79 | `sketch_primitives_b1` | `verified` | `original` | ✓ | — |
| 80 | `sketch_query` | `verified` | `original` | ✓ | — |
| 81 | `sketch_slot_types` | `verified` | `original` | ✓ | — |
| 82 | `solidworks_addin_host` | `verified` | `upstream` | ✓ | — |
| 83 | `standard_parts_toolbox` | `verified` | `original` | ✓ | — |
| 84 | `surface_delete_hole` | `verified` | `original` | ✓ | — |
| 85 | `surface_edit_ops` | `verified` | `original` | ✓ | — |
| 86 | `surface_features` | `verified` | `mixed` | ✓ | — |
| 87 | `surface_flatten` | `verified` | `original` | ✓ | — |
| 88 | `surface_modeling` | `stitched` | `mixed` | — | — |
| 89 | `surface_offset` | `verified` | `original` | ✓ | — |
| 90 | `surface_planar_region` | `verified` | `original` | ✓ | — |
| 91 | `surface_ref_ops` | `verified` | `original` | ✓ | — |
| 92 | `surface_revolve` | `verified` | `original` | ✓ | — |
| 93 | `surface_thicken_silent_noop` | `stitched` | `original` | ✓ | — |
| 94 | `surface_untrim` | `verified` | `original` | ✓ | — |
| 95 | `topology_constraints_and_controls` | `verified` | `original` | ✓ | — |
| 96 | `topology_iteration_options_backend_limited` | `stitched` | `original` | ✓ | — |
| 97 | `topology_optimization` | `verified` | `original` | ✓ | — |
| 98 | `topology_readback` | `stitched` | `original` | ✓ | — |
| 99 | `weldment_cut_list` | `verified` | `original` | ✓ | — |
| 100 | `weldment_profile_and_curve` | `verified` | `original` | ✓ | — |
| 101 | `weldments` | `verified` | `upstream` | ✓ | — |

**合计 101 条**。

## 二、`level` 分布

| level | 条数 |
|---|---|
| `indexed` | 0 |
| `not_implemented` | 1 |
| `source_verified` | 0 |
| `stitched` | 12 |
| `verified` | 88 |

## 三、`source` 分布

| source | 条数 |
|---|---|
| `merged` | 0 |
| `mixed` | 11 |
| `original` | 71 |
| `undetermined` | 1 |
| `upstream` | 18 |

## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）

| level \ source | merged | mixed | original | undetermined | upstream |
|---|---|---|---|---|---|
| `indexed` | 0 | 0 | 0 | 0 | 0 |
| `not_implemented` | 0 | 0 | 0 | 0 | 1 |
| `source_verified` | 0 | 0 | 0 | 0 | 0 |
| `stitched` | 0 | 3 | 9 | 0 | 0 |
| `verified` | 0 | 8 | 62 | 1 | 17 |

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
