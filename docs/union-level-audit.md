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
| 15 | `custom_properties_and_bom` | `verified` | `upstream` | ✓ | — |
| 16 | `declarative_hole_creation` | `verified` | `original` | ✓ | — |
| 17 | `dfm_checks` | `verified` | `mixed` | ✓ | — |
| 18 | `drawing_current_sheet_query` | `verified` | `original` | ✓ | — |
| 19 | `drawing_dimension_insertion` | `verified` | `mixed` | ✓ | — |
| 20 | `drawing_view_operations` | `verified` | `original` | ✓ | — |
| 21 | `drawing_views_and_summary` | `verified` | `original` | ✓ | — |
| 22 | `drawings_and_bom` | `verified` | `mixed` | ✓ | — |
| 23 | `dxf_preview_scene` | `verified` | `upstream` | ✓ | — |
| 24 | `equations` | `verified` | `original` | ✓ | — |
| 25 | `export_delivery` | `verified` | `upstream` | ✓ | — |
| 26 | `external_spur_gear_geometry` | `verified` | `upstream` | ✓ | — |
| 27 | `feature_build_extrude` | `verified` | `original` | ✓ | — |
| 28 | `feature_readback_criterion` | `verified` | `original` | ✓ | — |
| 29 | `file_custom_property_read` | `verified` | `original` | ✓ | — |
| 30 | `geometric_tolerance` | `stitched` | `original` | ✓ | — |
| 31 | `geometry_and_delivery_review` | `verified` | `upstream` | ✓ | — |
| 32 | `geometry_measurement` | `verified` | `original` | ✓ | — |
| 33 | `gtol_insert` | `verified` | `original` | ✓ | — |
| 34 | `headless_open_format_writing` | `verified` | `upstream` | ✓ | — |
| 35 | `helix_and_spiral` | `verified` | `original` | ✓ | — |
| 36 | `holes_and_finishing` | `verified` | `upstream` | ✓ | — |
| 37 | `loft_and_sweep` | `verified` | `mixed` | ✓ | — |
| 38 | `mass_property_read` | `verified` | `original` | ✓ | — |
| 39 | `mesh_create_readback` | `verified` | `original` | ✓ | — |
| 40 | `mesh_size_sanity_gate` | `verified` | `original` | ✓ | — |
| 41 | `modeling_feature_readback_tools` | `verified` | `original` | ✓ | — |
| 42 | `mold_analysis` | `verified` | `original` | ✓ | — |
| 43 | `mold_parting_geometry` | `stitched` | `original` | ✓ | — |
| 44 | `mold_tools` | `stitched` | `mixed` | — | ✓ |
| 45 | `motion_study` | `verified` | `mixed` | ✓ | — |
| 46 | `motion_validation_and_preconditions` | `verified` | `original` | ✓ | — |
| 47 | `pack_and_go` | `verified` | `upstream` | ✓ | — |
| 48 | `parameter_updates` | `verified` | `upstream` | ✓ | — |
| 49 | `part_and_features` | `verified` | `upstream` | ✓ | — |
| 50 | `pattern_and_mirror` | `verified` | `original` | ✓ | — |
| 51 | `preview_and_review_report` | `verified` | `original` | ✓ | — |
| 52 | `reference_axis` | `verified` | `mixed` | ✓ | — |
| 53 | `render_material_library` | `verified` | `original` | ✓ | — |
| 54 | `render_materials_and_appearance` | `verified` | `original` | ✓ | — |
| 55 | `requirements_planning` | `verified` | `upstream` | ✓ | — |
| 56 | `routing` | `stitched` | `mixed` | ✓ | — |
| 57 | `selection_helpers` | `verified` | `original` | ✓ | — |
| 58 | `sheet_metal` | `verified` | `upstream` | ✓ | — |
| 59 | `sheet_metal_creation` | `stitched` | `original` | ✓ | — |
| 60 | `simulation_and_fea` | `verified` | `original` | ✓ | — |
| 61 | `simulation_load_family_breadth` | `verified` | `original` | ✓ | — |
| 62 | `simulation_loads_wiring` | `verified` | `original` | ✓ | — |
| 63 | `simulation_solver_options` | `verified` | `original` | ✓ | — |
| 64 | `simulation_study_create` | `verified` | `original` | ✓ | — |
| 65 | `sketch_build` | `verified` | `original` | ✓ | — |
| 66 | `sketch_chamfer` | `verified` | `original` | ✓ | — |
| 67 | `sketch_edit_ops` | `stitched` | `original` | ✓ | — |
| 68 | `sketch_query` | `verified` | `original` | ✓ | — |
| 69 | `solidworks_addin_host` | `verified` | `upstream` | ✓ | — |
| 70 | `standard_parts_toolbox` | `verified` | `original` | ✓ | — |
| 71 | `surface_features` | `verified` | `mixed` | ✓ | — |
| 72 | `surface_modeling` | `stitched` | `mixed` | — | — |
| 73 | `topology_constraints_and_controls` | `verified` | `original` | ✓ | — |
| 74 | `topology_iteration_options_backend_limited` | `stitched` | `original` | ✓ | — |
| 75 | `topology_optimization` | `verified` | `original` | ✓ | — |
| 76 | `topology_readback` | `stitched` | `original` | ✓ | — |
| 77 | `weldment_cut_list` | `verified` | `original` | ✓ | — |
| 78 | `weldment_profile_and_curve` | `verified` | `original` | ✓ | — |
| 79 | `weldments` | `verified` | `upstream` | ✓ | — |

**合计 79 条**。

## 二、`level` 分布

| level | 条数 |
|---|---|
| `indexed` | 0 |
| `not_implemented` | 1 |
| `source_verified` | 0 |
| `stitched` | 11 |
| `verified` | 67 |

## 三、`source` 分布

| source | 条数 |
|---|---|
| `merged` | 0 |
| `mixed` | 11 |
| `original` | 49 |
| `undetermined` | 1 |
| `upstream` | 18 |

## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）

| level \ source | merged | mixed | original | undetermined | upstream |
|---|---|---|---|---|---|
| `indexed` | 0 | 0 | 0 | 0 | 0 |
| `not_implemented` | 0 | 0 | 0 | 0 | 1 |
| `source_verified` | 0 | 0 | 0 | 0 | 0 |
| `stitched` | 0 | 3 | 8 | 0 | 0 |
| `verified` | 0 | 8 | 41 | 1 | 17 |

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
