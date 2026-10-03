# S2-a 扫描：已挂工具 → 台账（正向差集）

> 只查不改：本次未修改任何已有文件，未运行 SolidWorks，未运行 pytest。
> 方法：纯静态解析（Python `ast` 读 `ToolSpec` / `json` 读台账），未做任何推断性替换。
> 落盘快照（本机时区）：**2026-10-03 21:00:46**；参与扫描的 `mcp-server\tool_specs_*.py` 共 **74** 个。

---

## 〇、口径（先读这一节，再读表）

### 0.1 台账字段名 —— 实读确认，未猜

`D:\AI\SW\capabilities.yaml` **内容其实是 JSON**（扩展名 `.yaml`，语法为 JSON 对象）。
顶层键：`backend_catalog`, `backend_schema_version`, `capabilities`, `operation_routes`, `schema_version`, `verified_versions`。

- 条目数组在 `capabilities` 键下，共 **110** 条。
- **台账里没有 `name` 字段**。与之对应的两个字段是 **`id`（英文 snake_case）** 与 **`label`（中文名）** —— 本报告的「id/name」即指这一对。
- 110 条出现过的全部键（并集）：`allowed_modes`, `backends`, `dependencies`, `evidence`, `id`, `label`, `level`, `limitations`, `mcp_tools`, `provenance`, `skills`, `source`, `source_evidence`, `title`, `verified_versions`。
- **`mcp_tools`**：70 / 110 条含该字段，合计 **300** 个引用、去重后 **226** 个工具名。
  它是台账里**唯一**结构化声明「哪个 MCP 工具属于哪条能力」的字段（`requirements_planning` 这类纯流程条目没有该字段）。
  实例（实读）：`id=solidworks_addin_host` → `mcp_tools=["solidworks_addin_host_status"]`；
  `id=part_and_features` → `mcp_tools` 含 8 个工具名；`id=holes_and_finishing` → 含 10 个。

### 0.2 工具侧口径

对每个 `tool_specs_batch*.py` **按语句顺序**求值顶层赋值，取出所有 `SPECS_*` 列表的元素，再逐元素取工具名。
三种形态都必须处理，否则会漏（都已处理，见各批文件实测）：

1. `ToolSpec(name="…", …)` —— 字面量 `name=`；
2. `ToolSpec(` 的 `name=` **不是字面量** —— 共 **2** 处，是 `_spec(...)` 工厂的**模板**（`tool_specs_batch29.py:103`、`tool_specs_batch30.py:70`），
   它们本身**不是**工具；这些批次的工具名要改从 `_spec(...)` 的**第 1 个位置参数**取；
3. 列表经过**别名或自引用拼接** —— `tool_specs_batch45.py` / `tool_specs_batch52.py` 用 `SPECS_BATCHnn = SPECS_BATCHnn + [...]`；
   `tool_specs_batch67.py` 起有批次写成私有 `_BATCHnn` 再 `SPECS_BATCHnn = _BATCHnn`。

### 0.3 「台账里没有」的判据

该工具名**不出现在任何一条 `capabilities[].mcp_tools`** 中。台账其它字段（`limitations` 散文偶尔提到某工具名）**不算数** ——
散文不是结构化归属声明，且措辞随人变。

### 0.4 「台账最接近条目」的判据（⚠ 是最近邻，**不是归属判定**）

在**已被台账引用的**工具名里，找与该差集工具名**词元重合最多**的一个（去掉 `solidworks` / `cadstudio` 前缀后按 `_` 切词；
并列时依次取「并集词元更少」「名字字典序更小」），再报出**拥有该近邻工具的台账条目**。

- 重合 ≥ 2 个词元 ⇒ 标「近邻匹配强」；
- 只重合 **1** 个词元 ⇒ 标「近邻匹配弱」，并在「判断」列写明**不作归属判定**（这类重合往往只是 `insert` / `surface` 之类泛词的巧合）；
- 完全没有重合 ⇒ 写「**查不到**」。

### 0.5 ⚠ 扫描期间工作树在变动（本节是本次扫描最重要的限定）

本仓库是多人共享工作树，`mcp-server\` 正在被**并发新增批次**。本次扫描窗口内实测到的漂移：

- `tool_specs_*.py` 文件数：**72 → 73 → 74**；
- 按 §0.2 同一口径解析出的工具名数：**256 → %d**。

落盘前做了两次间隔探测（20:55:59 与 20:58:19），两次均为 **74 个文件 / 264 个名字**，判定为当时的稳定点。
**下表全部以 2026-10-03 21:00:46 这一刻的磁盘内容为准**；任何后续复核都可能得到不同数字，那是工作树变了，不是本报告错。

落盘时最后写入的 3 个批次（证据）：`tool_specs_batch72.py`（10-03 18:56:59）、`tool_specs_batch73.py`（10-03 20:48:16）、`tool_specs_batch75.py`（10-03 20:58:04）。

### 0.6 未验证声明

- 「已挂工具」= **静态**读到的 `ToolSpec` 声明，**不等于**运行时一定注册成功（本次**未连 COM、未启动 SolidWorks**）。
- 「台账没有」= `mcp_tools` 未引用，**不等于**该能力没被实现。
- 「台账最接近条目」是词元最近邻，**不是**归属结论。

---

## 一、① 已挂工具清单（`ToolSpec` 名字，逐字去重）

共 **74** 个文件、**264** 个工具名；**逐字去重后仍是 264** 个（重复名：无）。
「台账引用它的条目数」= 0 即落在 §三 的正向差集里。

| # | 工具名 | batch 文件 | 台账引用它的条目数 |
|---:|---|---|---:|
| 1 | `solidworks_mold_draft_analysis` | `tool_specs_batch1.py` | 2 |
| 2 | `solidworks_mold_evidence` | `tool_specs_batch1.py` | 1 |
| 3 | `solidworks_mold_parting_line` | `tool_specs_batch1.py` | 2 |
| 4 | `solidworks_mold_shut_off_surface` | `tool_specs_batch1.py` | 2 |
| 5 | `solidworks_simulation_set_material` | `tool_specs_batch1.py` | 1 |
| 6 | `solidworks_topology_create_study` | `tool_specs_batch1.py` | 2 |
| 7 | `solidworks_topology_evidence` | `tool_specs_batch1.py` | 1 |
| 8 | `solidworks_topology_run` | `tool_specs_batch1.py` | 2 |
| 9 | `solidworks_sheet_metal_evidence` | `tool_specs_batch2.py` | 1 |
| 10 | `solidworks_surface_evidence` | `tool_specs_batch2.py` | 1 |
| 11 | `solidworks_weldment_create_sub_weld_folder` | `tool_specs_batch2.py` | 1 |
| 12 | `solidworks_weldment_ensure_cut_list` | `tool_specs_batch2.py` | 2 |
| 13 | `solidworks_weldment_evidence` | `tool_specs_batch2.py` | 2 |
| 14 | `solidworks_weldment_update_cut_list` | `tool_specs_batch2.py` | 2 |
| 15 | `solidworks_sheet_metal_create_base_flange` | `tool_specs_batch3.py` | 2 |
| 16 | `solidworks_sheet_metal_create_one_bend` | `tool_specs_batch3.py` | 2 |
| 17 | `solidworks_sheet_metal_create_draft` | `tool_specs_batch4.py` | 2 |
| 18 | `solidworks_sheet_metal_create_edge_flange` | `tool_specs_batch4.py` | 2 |
| 19 | `solidworks_sheet_metal_create_gusset` | `tool_specs_batch4.py` | 2 |
| 20 | `solidworks_sheet_metal_create_swept_flange` | `tool_specs_batch4.py` | 2 |
| 21 | `solidworks_clear_selection` | `tool_specs_batch5.py` | 1 |
| 22 | `solidworks_collect_appearance_evidence` | `tool_specs_batch5.py` | 1 |
| 23 | `solidworks_current_selection` | `tool_specs_batch5.py` | 1 |
| 24 | `solidworks_list_render_materials` | `tool_specs_batch5.py` | 1 |
| 25 | `solidworks_set_standard_view` | `tool_specs_batch5.py` | 2 |
| 26 | `solidworks_available_direction_selectors` | `tool_specs_batch6.py` | 1 |
| 27 | `solidworks_available_point_selectors` | `tool_specs_batch6.py` | 1 |
| 28 | `solidworks_collect_assembly_bom` | `tool_specs_batch6.py` | 2 |
| 29 | `solidworks_activate_model_for_preview` | `tool_specs_batch7.py` | 1 |
| 30 | `solidworks_clear_selection_for_preview` | `tool_specs_batch7.py` | 1 |
| 31 | `solidworks_refresh_scene_graph` | `tool_specs_batch7.py` | 1 |
| 32 | `solidworks_collect_model_summary` | `tool_specs_batch8.py` | 2 |
| 33 | `solidworks_get_costing_manager` | `tool_specs_batch8.py` | 1 |
| 34 | `solidworks_list_simulation_study_options` | `tool_specs_batch8.py` | 1 |
| 35 | `solidworks_mold_core_cavity_split` | `tool_specs_batch9.py` | 2 |
| 36 | `solidworks_mold_parting_surface` | `tool_specs_batch9.py` | 2 |
| 37 | `solidworks_mold_undercut_detect` | `tool_specs_batch9.py` | 2 |
| 38 | `solidworks_fastener_table_types` | `tool_specs_batch10.py` | 1 |
| 39 | `solidworks_fastener_types` | `tool_specs_batch10.py` | 1 |
| 40 | `solidworks_hole_standards` | `tool_specs_batch10.py` | 1 |
| 41 | `solidworks_part_bounding_box` | `tool_specs_batch10.py` | 1 |
| 42 | `solidworks_topology_create_factor_of_safety_constraint` | `tool_specs_batch11.py` | 1 |
| 43 | `solidworks_topology_create_mass_constraint` | `tool_specs_batch11.py` | 1 |
| 44 | `solidworks_topology_create_preserved_region` | `tool_specs_batch11.py` | 1 |
| 45 | `solidworks_topology_create_thickness_control` | `tool_specs_batch11.py` | 1 |
| 46 | `solidworks_topology_create_demold_control` | `tool_specs_batch12.py` | 1 |
| 47 | `solidworks_topology_create_stress_constraint` | `tool_specs_batch12.py` | 1 |
| 48 | `solidworks_topology_create_symmetry_control` | `tool_specs_batch12.py` | 1 |
| 49 | `solidworks_simulation_create_mesh_for_control` | `tool_specs_batch13.py` | 2 |
| 50 | `solidworks_simulation_default_element_size_and_tolerance` | `tool_specs_batch13.py` | 1 |
| 51 | `solidworks_simulation_generate_report` | `tool_specs_batch13.py` | 1 |
| 52 | `solidworks_entities_on_body` | `tool_specs_batch14.py` | 1 |
| 53 | `solidworks_get_active_view` | `tool_specs_batch14.py` | 1 |
| 54 | `solidworks_build_review_report` | `tool_specs_batch15.py` | 2 |
| 55 | `solidworks_add_sketch_relation` | `tool_specs_batch16.py` | 1 |
| 56 | `solidworks_mirror_feature` | `tool_specs_batch16.py` | 2 |
| 57 | `solidworks_circular_pattern` | `tool_specs_batch17.py` | 2 |
| 58 | `solidworks_revolve_boss` | `tool_specs_batch17.py` | 1 |
| 59 | `solidworks_sketch_count_arcs` | `tool_specs_batch18.py` | 1 |
| 60 | `solidworks_sketch_count_lines` | `tool_specs_batch18.py` | 1 |
| 61 | `solidworks_sketch_count_segments` | `tool_specs_batch18.py` | 1 |
| 62 | `solidworks_sketch_is_3d` | `tool_specs_batch18.py` | 1 |
| 63 | `solidworks_drawing_get_current_sheet` | `tool_specs_batch19.py` | 1 |
| 64 | `solidworks_drawing_list_sheets` | `tool_specs_batch19.py` | 1 |
| 65 | `solidworks_drawing_list_views` | `tool_specs_batch19.py` | 2 |
| 66 | `solidworks_custom_property_get` | `tool_specs_batch20.py` | 1 |
| 67 | `solidworks_custom_property_list` | `tool_specs_batch20.py` | 1 |
| 68 | `solidworks_sketch_add_circle` | `tool_specs_batch21.py` | 1 |
| 69 | `solidworks_sketch_add_line` | `tool_specs_batch21.py` | 1 |
| 70 | `solidworks_sketch_add_rectangle` | `tool_specs_batch21.py` | 1 |
| 71 | `solidworks_sketch_end` | `tool_specs_batch21.py` | 1 |
| 72 | `solidworks_sketch_start` | `tool_specs_batch21.py` | 1 |
| 73 | `solidworks_extrude_boss` | `tool_specs_batch22.py` | 1 |
| 74 | `solidworks_extrude_cut` | `tool_specs_batch22.py` | 1 |
| 75 | `solidworks_extrude_midplane` | `tool_specs_batch22.py` | 1 |
| 76 | `solidworks_chamfer` | `tool_specs_batch23.py` | 1 |
| 77 | `solidworks_fillet` | `tool_specs_batch23.py` | 1 |
| 78 | `solidworks_part_mass_properties` | `tool_specs_batch24.py` | 1 |
| 79 | `solidworks_assembly_check_interference` | `tool_specs_batch25.py` | 2 |
| 80 | `solidworks_assembly_list_components` | `tool_specs_batch25.py` | 2 |
| 81 | `solidworks_assembly_list_mates` | `tool_specs_batch25.py` | 2 |
| 82 | `solidworks_simulation_apply_fixed_restraint` | `tool_specs_batch26.py` | 1 |
| 83 | `solidworks_simulation_apply_normal_force` | `tool_specs_batch26.py` | 1 |
| 84 | `solidworks_simulation_create_study` | `tool_specs_batch27.py` | 1 |
| 85 | `solidworks_simulation_find_study` | `tool_specs_batch27.py` | 1 |
| 86 | `solidworks_simulation_list_studies` | `tool_specs_batch27.py` | 1 |
| 87 | `solidworks_simulation_collect_evidence` | `tool_specs_batch28.py` | 1 |
| 88 | `solidworks_simulation_create_mesh` | `tool_specs_batch28.py` | 1 |
| 89 | `solidworks_simulation_mesh_size` | `tool_specs_batch28.py` | 1 |
| 90 | `solidworks_simulation_run_analysis` | `tool_specs_batch28.py` | 1 |
| 91 | `solidworks_simulation_apply_centrifugal_force` | `tool_specs_batch29.py` | 1 |
| 92 | `solidworks_simulation_apply_gravity` | `tool_specs_batch29.py` | 1 |
| 93 | `solidworks_simulation_apply_pressure` | `tool_specs_batch29.py` | 1 |
| 94 | `solidworks_simulation_apply_torque` | `tool_specs_batch29.py` | 1 |
| 95 | `solidworks_topology_collect_numbers` | `tool_specs_batch30.py` | 1 |
| 96 | `solidworks_topology_list_constraints` | `tool_specs_batch30.py` | 1 |
| 97 | `solidworks_topology_manager_report` | `tool_specs_batch30.py` | 1 |
| 98 | `solidworks_topology_options_report` | `tool_specs_batch30.py` | 1 |
| 99 | `solidworks_topology_set_goal` | `tool_specs_batch30.py` | 1 |
| 100 | `solidworks_topology_set_iteration_options` | `tool_specs_batch30.py` | 1 |
| 101 | `solidworks_simulation_check_mesh_size` | `tool_specs_batch31.py` | 1 |
| 102 | `solidworks_part_insert_composite_curve` | `tool_specs_batch32.py` | 1 |
| 103 | `solidworks_part_insert_dome` | `tool_specs_batch32.py` | 1 |
| 104 | `solidworks_part_rib` | `tool_specs_batch32.py` | 1 |
| 105 | `solidworks_part_shell` | `tool_specs_batch32.py` | 1 |
| 106 | `solidworks_config_activate` | `tool_specs_batch33.py` | 2 |
| 107 | `solidworks_config_create` | `tool_specs_batch33.py` | 2 |
| 108 | `solidworks_config_inspect` | `tool_specs_batch33.py` | 2 |
| 109 | `solidworks_config_read_custom_property` | `tool_specs_batch33.py` | 2 |
| 110 | `solidworks_config_set_custom_properties` | `tool_specs_batch33.py` | 2 |
| 111 | `solidworks_config_update_dimension` | `tool_specs_batch33.py` | 3 |
| 112 | `solidworks_export_bmp` | `tool_specs_batch33.py` | 2 |
| 113 | `solidworks_export_dxf` | `tool_specs_batch33.py` | 2 |
| 114 | `solidworks_export_iges` | `tool_specs_batch33.py` | 2 |
| 115 | `solidworks_export_parasolid` | `tool_specs_batch33.py` | 2 |
| 116 | `solidworks_export_step` | `tool_specs_batch33.py` | 2 |
| 117 | `solidworks_export_stl` | `tool_specs_batch33.py` | 2 |
| 118 | `solidworks_hole_blind_by_selection` | `tool_specs_batch34.py` | 2 |
| 119 | `solidworks_hole_counterbore_by_selection` | `tool_specs_batch34.py` | 2 |
| 120 | `solidworks_hole_countersink_by_selection` | `tool_specs_batch34.py` | 2 |
| 121 | `solidworks_hole_through_by_selection` | `tool_specs_batch34.py` | 2 |
| 122 | `solidworks_slot_semicircular_by_selection` | `tool_specs_batch34.py` | 2 |
| 123 | `solidworks_weldment_create_cut_list` | `tool_specs_batch35.py` | 2 |
| 124 | `solidworks_weldment_create_profile_center_mate` | `tool_specs_batch35.py` | 2 |
| 125 | `solidworks_weldment_create_weldment_profile` | `tool_specs_batch35.py` | 2 |
| 126 | `solidworks_weldment_export_cut_list_csv` | `tool_specs_batch35.py` | 2 |
| 127 | `solidworks_weldment_read_property_manager` | `tool_specs_batch35.py` | 1 |
| 128 | `solidworks_weldment_set_cut_list_properties` | `tool_specs_batch35.py` | 2 |
| 129 | `solidworks_custom_property_count` | `tool_specs_batch36.py` | 1 |
| 130 | `solidworks_custom_property_names` | `tool_specs_batch36.py` | 1 |
| 131 | `solidworks_delivery_bom_traceability` | `tool_specs_batch36.py` | 2 |
| 132 | `solidworks_delivery_export_bom_csv` | `tool_specs_batch36.py` | 2 |
| 133 | `solidworks_delivery_pack_and_go_audit_matrix` | `tool_specs_batch36.py` | 2 |
| 134 | `solidworks_drawing_current_sheet_name` | `tool_specs_batch36.py` | 1 |
| 135 | `solidworks_drawing_sheet_count` | `tool_specs_batch36.py` | 1 |
| 136 | `solidworks_drawing_sheet_names` | `tool_specs_batch36.py` | 1 |
| 137 | `solidworks_selector_resolve_direction` | `tool_specs_batch36.py` | 1 |
| 138 | `solidworks_selector_resolve_point` | `tool_specs_batch36.py` | 1 |
| 139 | `solidworks_simulation_list_setter_summary` | `tool_specs_batch36.py` | 2 |
| 140 | `solidworks_simulation_configure_buckling_solver` | `tool_specs_batch37.py` | 2 |
| 141 | `solidworks_simulation_configure_frequency_solver` | `tool_specs_batch37.py` | 2 |
| 142 | `solidworks_simulation_configure_static_solver` | `tool_specs_batch37.py` | 2 |
| 143 | `solidworks_simulation_set_study_option` | `tool_specs_batch37.py` | 2 |
| 144 | `solidworks_simulation_set_study_options` | `tool_specs_batch37.py` | 2 |
| 145 | `solidworks_costing_body_count` | `tool_specs_batch38.py` | 2 |
| 146 | `solidworks_costing_default_template` | `tool_specs_batch38.py` | 3 |
| 147 | `solidworks_costing_evidence` | `tool_specs_batch38.py` | 2 |
| 148 | `solidworks_costing_list_bodies` | `tool_specs_batch38.py` | 2 |
| 149 | `solidworks_costing_list_templates` | `tool_specs_batch38.py` | 3 |
| 150 | `solidworks_costing_method_value` | `tool_specs_batch38.py` | 2 |
| 151 | `solidworks_costing_read_analysis` | `tool_specs_batch38.py` | 2 |
| 152 | `solidworks_costing_read_body` | `tool_specs_batch38.py` | 2 |
| 153 | `solidworks_equation_add` | `tool_specs_batch39.py` | 1 |
| 154 | `solidworks_equation_delete` | `tool_specs_batch39.py` | 1 |
| 155 | `solidworks_equation_evaluate` | `tool_specs_batch39.py` | 1 |
| 156 | `solidworks_equation_list` | `tool_specs_batch39.py` | 1 |
| 157 | `solidworks_gtol_insert` | `tool_specs_batch39.py` | 1 |
| 158 | `solidworks_helix_insert` | `tool_specs_batch39.py` | 1 |
| 159 | `solidworks_motion_collect_summary` | `tool_specs_batch40.py` | 1 |
| 160 | `solidworks_motion_create_study` | `tool_specs_batch40.py` | 1 |
| 161 | `solidworks_motion_ensure_type_library` | `tool_specs_batch40.py` | 2 |
| 162 | `solidworks_motion_study_manager` | `tool_specs_batch40.py` | 1 |
| 163 | `solidworks_motion_validate_studies` | `tool_specs_batch40.py` | 2 |
| 164 | `solidworks_motion_validate_summary` | `tool_specs_batch40.py` | 2 |
| 165 | `solidworks_gear_calculate_spur` | `tool_specs_batch41.py` | 1 |
| 166 | `solidworks_gear_create_spur` | `tool_specs_batch41.py` | 1 |
| 167 | `solidworks_sketch_convert_entities` | `tool_specs_batch41.py` | 1 |
| 168 | `solidworks_sketch_create_chamfer` | `tool_specs_batch41.py` | 1 |
| 169 | `solidworks_sketch_mirror` | `tool_specs_batch41.py` | 1 |
| 170 | `solidworks_toolbox_list_standards` | `tool_specs_batch41.py` | 1 |
| 171 | `solidworks_toolbox_load_index` | `tool_specs_batch41.py` | 1 |
| 172 | `solidworks_toolbox_part_path` | `tool_specs_batch41.py` | 1 |
| 173 | `solidworks_toolbox_search` | `tool_specs_batch41.py` | 1 |
| 174 | `solidworks_drawing_current_sheet_info` | `tool_specs_batch42.py` | 1 |
| 175 | `solidworks_drawing_sheets_summary` | `tool_specs_batch42.py` | 1 |
| 176 | `solidworks_drawing_collect_view_evidence` | `tool_specs_batch43.py` | 1 |
| 177 | `solidworks_drawing_view_scale` | `tool_specs_batch43.py` | 1 |
| 178 | `solidworks_drawing_view_set_scale` | `tool_specs_batch43.py` | 1 |
| 179 | `solidworks_drawing_set_sheet_scale` | `tool_specs_batch44.py` | 1 |
| 180 | `solidworks_drawing_sheet_scale` | `tool_specs_batch44.py` | 1 |
| 181 | `solidworks_surface_create_extruded` | `tool_specs_batch45.py` | 1 |
| 182 | `solidworks_measure_selection` | `tool_specs_batch46.py` | 1 |
| 183 | `solidworks_part_loft` | `tool_specs_batch47.py` | 1 |
| 184 | `solidworks_part_sweep` | `tool_specs_batch48.py` | 1 |
| 185 | `solidworks_part_axis` | `tool_specs_batch49.py` | 1 |
| 186 | `solidworks_part_wrap` | `tool_specs_batch50.py` | 1 |
| 187 | `solidworks_read_sensors` | `tool_specs_batch51.py` | 1 |
| 188 | `solidworks_read_document_units` | `tool_specs_batch52.py` | 1 |
| 189 | `solidworks_resolve_entity` | `tool_specs_batch53.py` | 1 |
| 190 | `solidworks_resolve_selection` | `tool_specs_batch53.py` | 1 |
| 191 | `solidworks_select_by_selector` | `tool_specs_batch53.py` | 1 |
| 192 | `solidworks_select_entity_by_index` | `tool_specs_batch53.py` | 1 |
| 193 | `solidworks_selection_count` | `tool_specs_batch53.py` | 1 |
| 194 | `solidworks_selection_point` | `tool_specs_batch53.py` | 1 |
| 195 | `solidworks_sketch_add_arc` | `tool_specs_batch54.py` | 1 |
| 196 | `solidworks_sketch_add_centerline` | `tool_specs_batch54.py` | 1 |
| 197 | `solidworks_sketch_add_ellipse` | `tool_specs_batch54.py` | 1 |
| 198 | `solidworks_sketch_add_polygon` | `tool_specs_batch54.py` | 1 |
| 199 | `solidworks_sketch_add_slot` | `tool_specs_batch54.py` | 1 |
| 200 | `solidworks_auto_dimension_sketch` | `tool_specs_batch55.py` | 1 |
| 201 | `solidworks_current_sketch_name` | `tool_specs_batch55.py` | 1 |
| 202 | `solidworks_add_dimension` | `tool_specs_batch56.py` | 1 |
| 203 | `solidworks_hole_pattern` | `tool_specs_batch57.py` | 1 |
| 204 | `solidworks_simulation_apply_convection` | `tool_specs_batch58.py` | 1 |
| 205 | `solidworks_simulation_apply_elastic_connector` | `tool_specs_batch58.py` | 1 |
| 206 | `solidworks_simulation_apply_heat_flux` | `tool_specs_batch58.py` | 1 |
| 207 | `solidworks_simulation_apply_heat_power` | `tool_specs_batch58.py` | 1 |
| 208 | `solidworks_simulation_apply_radiation` | `tool_specs_batch58.py` | 1 |
| 209 | `solidworks_simulation_apply_temperature` | `tool_specs_batch58.py` | 1 |
| 210 | `solidworks_export_image` | `tool_specs_batch59.py` | 1 |
| 211 | `solidworks_simulation_apply_distributed_mass` | `tool_specs_batch60.py` | 1 |
| 212 | `solidworks_simulation_apply_force` | `tool_specs_batch60.py` | 1 |
| 213 | `solidworks_simulation_apply_remote_load` | `tool_specs_batch60.py` | 1 |
| 214 | `solidworks_simulation_apply_rigid_connector` | `tool_specs_batch61.py` | 1 |
| 215 | `solidworks_weldment_create_structural_member` | `tool_specs_batch62.py` | 1 |
| 216 | `solidworks_select_face_selector` | `tool_specs_batch63.py` | 0 |
| 217 | `solidworks_simulation_apply_link_connector` | `tool_specs_batch64.py` | 0 |
| 218 | `solidworks_sketch_add_3point_arc` | `tool_specs_batch65.py` | 0 |
| 219 | `solidworks_sketch_add_3point_center_rectangle` | `tool_specs_batch65.py` | 0 |
| 220 | `solidworks_sketch_add_3point_rectangle` | `tool_specs_batch65.py` | 0 |
| 221 | `solidworks_sketch_add_conic` | `tool_specs_batch65.py` | 0 |
| 222 | `solidworks_sketch_add_parabola` | `tool_specs_batch65.py` | 0 |
| 223 | `solidworks_sketch_add_parallelogram` | `tool_specs_batch65.py` | 0 |
| 224 | `solidworks_sketch_add_partial_ellipse` | `tool_specs_batch65.py` | 0 |
| 225 | `solidworks_sketch_add_perimeter_circle` | `tool_specs_batch65.py` | 0 |
| 226 | `solidworks_sketch_add_tangent_arc` | `tool_specs_batch65.py` | 0 |
| 227 | `solidworks_sketch_circular_pattern` | `tool_specs_batch66.py` | 0 |
| 228 | `solidworks_sketch_extend` | `tool_specs_batch66.py` | 0 |
| 229 | `solidworks_sketch_fillet` | `tool_specs_batch66.py` | 0 |
| 230 | `solidworks_sketch_linear_pattern` | `tool_specs_batch66.py` | 0 |
| 231 | `solidworks_sketch_offset` | `tool_specs_batch66.py` | 0 |
| 232 | `solidworks_sketch_trim` | `tool_specs_batch66.py` | 0 |
| 233 | `solidworks_sketch_flip_entities` | `tool_specs_batch67.py` | 0 |
| 234 | `solidworks_sketch_move_entities` | `tool_specs_batch67.py` | 0 |
| 235 | `solidworks_sketch_rotate_entities` | `tool_specs_batch67.py` | 0 |
| 236 | `solidworks_sketch_scale_entities` | `tool_specs_batch67.py` | 0 |
| 237 | `solidworks_sketch_stretch_entities` | `tool_specs_batch67.py` | 0 |
| 238 | `solidworks_insert_delete_face` | `tool_specs_batch68.py` | 0 |
| 239 | `solidworks_insert_offset_surface` | `tool_specs_batch68.py` | 0 |
| 240 | `solidworks_insert_planar_surface` | `tool_specs_batch68.py` | 0 |
| 241 | `solidworks_insert_replace_face` | `tool_specs_batch68.py` | 0 |
| 242 | `solidworks_insert_ruled_surface` | `tool_specs_batch68.py` | 0 |
| 243 | `solidworks_insert_lofted_ref_surface` | `tool_specs_batch69.py` | 0 |
| 244 | `solidworks_insert_center_of_mass` | `tool_specs_batch70.py` | 0 |
| 245 | `solidworks_insert_coordinate_system` | `tool_specs_batch70.py` | 0 |
| 246 | `solidworks_insert_global_bounding_box` | `tool_specs_batch70.py` | 0 |
| 247 | `solidworks_insert_ref_plane` | `tool_specs_batch70.py` | 0 |
| 248 | `solidworks_insert_reference_point` | `tool_specs_batch70.py` | 0 |
| 249 | `solidworks_insert_curve_through_points` | `tool_specs_batch71.py` | 0 |
| 250 | `solidworks_create_revolved_surface` | `tool_specs_batch72.py` | 0 |
| 251 | `solidworks_hole_wizard` | `tool_specs_batch72.py` | 0 |
| 252 | `solidworks_sketch_fully_defined_status` | `tool_specs_batch72.py` | 0 |
| 253 | `solidworks_drawing_create_auxiliary_view` | `tool_specs_batch73.py` | 0 |
| 254 | `solidworks_drawing_create_broken_view` | `tool_specs_batch73.py` | 0 |
| 255 | `solidworks_drawing_insert_datum_tag` | `tool_specs_batch73.py` | 0 |
| 256 | `solidworks_drawing_insert_surface_finish_symbol` | `tool_specs_batch73.py` | 0 |
| 257 | `solidworks_drawing_add_note` | `tool_specs_batch75.py` | 0 |
| 258 | `solidworks_drawing_create_detail_view` | `tool_specs_batch75.py` | 0 |
| 259 | `solidworks_drawing_create_hole_table` | `tool_specs_batch75.py` | 0 |
| 260 | `solidworks_drawing_create_projected_view` | `tool_specs_batch75.py` | 0 |
| 261 | `solidworks_drawing_create_revision_table` | `tool_specs_batch75.py` | 0 |
| 262 | `solidworks_drawing_create_section_view` | `tool_specs_batch75.py` | 0 |
| 263 | `solidworks_drawing_insert_center_marks` | `tool_specs_batch75.py` | 0 |
| 264 | `solidworks_drawing_set_sheet_format` | `tool_specs_batch75.py` | 0 |

## 二、② 台账条目 id / name（`capabilities.yaml` → `capabilities` 数组）

共 **110** 条。台账无 `name` 字段，此处「name」= `label`；`mcp_tools 条数` = 该条目声明的工具个数。

| # | id | label（= name） | level | mcp_tools 条数 |
|---:|---|---|---|---:|
| 1 | `requirements_planning` | 需求分析与工程规划 | `verified` | 0 |
| 2 | `solidworks_addin_host` | SolidWorks C# 进程内 Add-in 宿主 | `verified` | 1 |
| 3 | `part_and_features` | 参数化零件与基础特征 | `verified` | 8 |
| 4 | `external_spur_gear_geometry` | 标准外啮合渐开线直齿轮实体 | `verified` | 2 |
| 5 | `holes_and_finishing` | 孔槽、螺纹、圆角与倒角 | `verified` | 10 |
| 6 | `parameter_updates` | 命名尺寸参数修改 | `verified` | 1 |
| 7 | `custom_properties_and_bom` | 自定义属性与装配 BOM CSV | `verified` | 5 |
| 8 | `pack_and_go` | SolidWorks 原生 Pack and Go | `verified` | 2 |
| 9 | `assembly_and_mates` | 装配体与配合 | `verified` | 3 |
| 10 | `motion_study` | 旋转马达 Motion Study | `verified` | 6 |
| 11 | `drawing_dimension_insertion` | SolidWorks 工程图模型尺寸自动插入 | `verified` | 0 |
| 12 | `drawings_and_bom` | 工程图、尺寸链与 BOM | `verified` | 3 |
| 13 | `export_delivery` | 文件导出与交付包 | `verified` | 7 |
| 14 | `headless_open_format_writing` | 无 CAD 开放格式写入 | `verified` | 1 |
| 15 | `geometry_and_delivery_review` | 几何、文件与交付复核 | `verified` | 7 |
| 16 | `dfm_checks` | 机加工、钣金、激光切割与 3D 打印 DFM 复核 | `verified` | 1 |
| 17 | `autocad_basic_drafting` | AutoCAD 二维绘图与批量改图 | `not_implemented` | 0 |
| 18 | `configurations_and_design_tables` | 配置与设计表 | `verified` | 6 |
| 19 | `sheet_metal` | 钣金建模与展开 | `verified` | 7 |
| 20 | `weldments` | 焊件与切割清单 | `verified` | 11 |
| 21 | `surface_modeling` | 复杂曲面与连续性检查 | `stitched` | 0 |
| 22 | `mold_tools` | 模具工具与分型检查 | `stitched` | 7 |
| 23 | `simulation_and_fea` | 仿真与 FEA | `verified` | 8 |
| 24 | `autocad_headless_preview` | AutoCAD 无头 DXF 预览与检查 | `verified` | 1 |
| 25 | `dxf_preview_scene` | DXF 安全 PreviewScene 转换 | `verified` | 1 |
| 26 | `autocad_script_backend` | AutoCAD SCR/AutoLISP 白名单命令桥 | `verified` | 0 |
| 27 | `autocad_dotnet_backend` | AutoCAD .NET Managed API 桥接 | `verified` | 0 |
| 28 | `routing` | Routing | `stitched` | 2 |
| 29 | `topology_optimization` | 拓扑优化（非参数化找形） | `verified` | 2 |
| 30 | `costing` | 成本估算（Costing） | `verified` | 9 |
| 31 | `animation_export` | 动画导出（AVI / 运动算例视频） | `stitched` | 0 |
| 32 | `helix_and_spiral` | 螺旋线与涡旋（定距） | `verified` | 1 |
| 33 | `sketch_edit_ops` | 草图编辑（倒角 / 镜像 / 转换实体引用） | `stitched` | 2 |
| 34 | `equations` | 方程式（增 / 列 / 删 / 求解） | `verified` | 4 |
| 35 | `sketch_query` | 草图读回（ISketch 按类型取几何） | `verified` | 5 |
| 36 | `geometric_tolerance` | 形位公差（新建 + 加公差指示符） | `stitched` | 0 |
| 37 | `standard_parts_toolbox` | 标准件（Toolbox 索引） | `verified` | 4 |
| 38 | `sketch_chamfer` | 草图倒角（CreateChamfer） | `verified` | 1 |
| 39 | `gtol_insert` | 形位公差：新建 GTol（InsertGtol） | `verified` | 1 |
| 40 | `drawing_current_sheet_query` | 工程图当前图纸的轻量只读读数（几张纸 / 图幅 / 视图清单） | `verified` | 8 |
| 41 | `file_custom_property_read` | 文件自定义属性读取（值 / 类型 / 全部清单） | `verified` | 2 |
| 42 | `sketch_build` | 建草图与画基本几何（线 / 圆 / 矩形） | `verified` | 11 |
| 43 | `feature_build_extrude` | 拉伸族（凸台 / 切除 / 中面）—— 把草图变成实体 | `verified` | 3 |
| 44 | `chamfer_fillet_on_selection` | 倒角 / 圆角（作用于声明式选择选中的边） | `verified` | 2 |
| 45 | `mass_property_read` | 读零件/装配的质量属性（体积 / 表面积 / 重心 / 密度 / 质量） | `verified` | 1 |
| 46 | `assembly_read` | 装配只读（零部件清单 / 配合清单 / 干涉检查） | `verified` | 3 |
| 47 | `simulation_loads_wiring` | ★ 仿真载荷包装层（夹具 / 法向力）—— 护城河域 | `verified` | 2 |
| 48 | `simulation_study_create` | 仿真研究族（新建 / 按名取 / 列出）—— 补 W7 的硬前置 | `verified` | 5 |
| 49 | `mesh_create_readback` | 网格尺寸 + 建网格（★ 回读报告；真机证据：7,250 单元） | `verified` | 4 |
| 50 | `analysis_run_readback` | 跑求解并回读结果（★ 未真机验证 —— RunAnalysis 仍会挂，被隔离兜住） | `stitched` | 2 |
| 51 | `simulation_load_family_breadth` | 仿真载荷族广度（压力 / 力矩 / 重力 / 离心力 4 类）—— ★ 未真机验证 | `verified` | 14 |
| 52 | `topology_iteration_options_backend_limited` | 拓扑迭代选项设置（★ pywin32 后端限制 —— 与事实 47/67 同族） | `stitched` | 1 |
| 53 | `mesh_size_sanity_gate` | 建网格前的地基闸门（★ 把「跑求解必挂」掐断在网格之前） | `verified` | 1 |
| 54 | `feature_readback_criterion` | 特征建成回读判据（★ 规则 6 的通用助手 —— 真机打磨三遍） | `verified` | 0 |
| 55 | `modeling_feature_readback_tools` | 建模闭环补全（抽壳 ✅ / 圆顶 ✅ 真机通过 · 筋 未验 · 复合曲线 真机失败） | `verified` | 5 |
| 56 | `config_and_export` | 配置族 + 导出族（★ 真机 10/12：配置 5/6 · 导出 5/6） | `verified` | 12 |
| 57 | `render_materials_and_appearance` | 渲染材质与外观（★ 真机 4/4，含读写配对） | `verified` | 4 |
| 58 | `selection_helpers` | 选择器底座（声明式选择 + 当前选区读数 + 可选值枚举） | `verified` | 13 |
| 59 | `declarative_hole_creation` | 声明式建孔（5 种孔型 · 参数里没有坐标） | `verified` | 5 |
| 60 | `weldment_cut_list` | 焊接切割清单（生成 / 属性 / 导出） | `verified` | 6 |
| 61 | `simulation_solver_options` | 仿真求解器选项（9 个族 / 202 个 setter 名） | `verified` | 6 |
| 62 | `topology_constraints_and_controls` | 拓扑优化的约束与控制（目标 / 质量 / 应力 / 安全系数 / 保留区 / 拔模 / 对称 / 厚度） | `verified` | 8 |
| 63 | `topology_readback` | 拓扑优化的读数与建研究 | `stitched` | 7 |
| 64 | `costing_readback` | 成本估算读数（护城河域） | `verified` | 8 |
| 65 | `render_material_library` | 渲染材质库（建 / 删 / 加） | `verified` | 0 |
| 66 | `sheet_metal_creation` | 钣金创建（基体法兰 / 边法兰 / 折弯 / 草绘折弯 / 放样法兰 / 通风口） | `stitched` | 6 |
| 67 | `mold_analysis` | 模具分析（拔模分析 / 底切检测） | `verified` | 2 |
| 68 | `preview_and_review_report` | 预览准备与模型审查报告 | `verified` | 3 |
| 69 | `motion_validation_and_preconditions` | 运动算例的验收与前置检查（类型库 / 要求核对） | `verified` | 3 |
| 70 | `drawing_views_and_summary` | 工程图视图与整图摘要 | `verified` | 3 |
| 71 | `weldment_profile_and_curve` | 焊件轮廓与轮廓中心配合 | `verified` | 2 |
| 72 | `costing_templates_and_defaults` | 成本模板与默认值（★ 护城河域的一部分） | `verified` | 2 |
| 73 | `mold_parting_geometry` | 模具分型几何（分型线 / 分型面 / 关断面 / 分型） | `stitched` | 4 |
| 74 | `pattern_and_mirror` | 阵列与镜像（特征级的重复几何） | `verified` | 2 |
| 75 | `drawing_view_operations` | 工程图视图操作（取视图 / 比例 / 注释数 / 可见件数） | `verified` | 3 |
| 76 | `surface_features` | 复杂曲面与连续性检查 | `verified` | 4 |
| 77 | `geometry_measurement` | 读零件/装配的质量属性（体积 / 表面积 / 重心 / 密度 / 质量） | `verified` | 1 |
| 78 | `loft_and_sweep` | 复杂曲面与连续性检查 | `verified` | 2 |
| 79 | `reference_axis` | 复杂曲面与连续性检查 | `verified` | 1 |
| 80 | `sketch_primitives_b1` | 草图图元 B1 批（3 点矩形 / 平行四边形 / 切线弧 / 3 点圆弧 / 部分椭圆 / 抛物线 / 圆锥 / 周边圆） | `verified` | 0 |
| 81 | `sketch_edit_ops_b3` | 草图编辑 B3 批（剪裁 / 延伸 / 等距 / 草图圆角 / 线性与圆周草图阵列） | `verified` | 0 |
| 82 | `sketch_modify_ops` | 草图编辑·移动族（移动 / 旋转 / 缩放 / 伸展 / 镜像） | `verified` | 0 |
| 83 | `surface_edit_ops` | 曲面编辑（平面区域 / 等距曲面 / 直纹曲面 / 删除面 / 替换面） | `verified` | 0 |
| 84 | `surface_ref_ops` | 曲面特征·参考曲面（放样曲面；★ 旋转曲面**未登记**） | `verified` | 0 |
| 85 | `ref_geometry` | 参考几何体（基准面 / 坐标系 / 点 / 质心 / 边界框） | `verified` | 0 |
| 86 | `curve_and_split` | 通过参考点的曲线 · 配合参考 · **分割线（投影/轮廓）**（★ 后两条 2026-10-03 真机建成） | `verified` | 0 |
| 87 | `surface_thicken_silent_noop` | 加厚曲面（★ 真机**静默不成** —— 已单列） | `stitched` | 0 |
| 88 | `surface_offset` | 等距曲面（★ **真机建成**） | `verified` | 0 |
| 89 | `surface_planar_region` | 平面区域（★ **真机建成**） | `verified` | 0 |
| 90 | `replace_face` | 替换面（★ **真机建成**） | `verified` | 0 |
| 91 | `surface_revolve` | 旋转曲面（★ **真机建成**·★★ 根因是“必须有中心线”） | `verified` | 0 |
| 92 | `sketch_dimension_horizontal` | 水平尺寸（`AddHorizontalDimension2`）—— ★ **真机建成** | `verified` | 0 |
| 93 | `sketch_dimension_vertical` | 竖直尺寸（`AddVerticalDimension2`）—— ★ **真机建成** | `verified` | 0 |
| 94 | `feature_revolve_cut` | 旋转切除（`FeatureRevolve2` 的 `IsCut=True`）—— ★ **真机建成** | `verified` | 0 |
| 95 | `sketch_slot_types` | 槽口四种（`CreateSketchSlot` + `swSketchSlotCreationType_e`）—— ★ **四个全真机建成** | `verified` | 0 |
| 96 | `surface_flatten` | 曲面展平（`InsertFlattenSurface2`）—— ★ **真机建成**·★★ 关键前置：**锚点 mark=16** | `verified` | 0 |
| 97 | `surface_untrim` | 解除剪裁曲面（`InsertUntrimSurface2`）—— ★ **真机建成**·★★ 关键：**选边 + `EdgeUntrimType=2`** | `verified` | 0 |
| 98 | `feature_loft_cut` | 放样 / 边界**切除**（`InsertCutBlend`）—— ★ **真机建成**·★★ 类型名是 **`BlendCut`** | `verified` | 0 |
| 99 | `surface_delete_hole` | 删除孔（曲面）（`InsertDeleteHoleForSurface`）—— ★ **真机建成**·★★ **继任者**（第一代 `InsertDeleteHole` 已废弃） | `verified` | 0 |
| 100 | `sketch_line2` | 中点线 / 直线（`IModelDoc2.CreateLine2`）—— ★ **真机建成** | `verified` | 0 |
| 101 | `feature_cosmetic_thread` | 螺纹线（`InsertCosmeticThread3`）—— ★ **真机建成**·★★ 前置：选**圆柱面的边** | `verified` | 0 |
| 102 | `sketch_spline` | 样条曲线（`ISketchManager.CreateSpline2`）—— ★ **真机建成**·★★ **三个条件缺一不可** | `verified` | 0 |
| 103 | `sketch_spline3_2d` | 样条曲线（`CreateSpline3` 的 **2D** 用法）—— ★ **真机建成**·★★ 它是 `CreateSpline2` 的**继任者** | `verified` | 0 |
| 104 | `sketch_rotate_or_copy_3d` | 复制实体（`ISketchManager.RotateOrCopy3DAboutXYZ` 的 **`Copy=True`**）—— ★ **真机建成** | `verified` | 0 |
| 105 | `sketch_equation_curve` | 方程式驱动的曲线（`ISketchManager.CreateEquationSpline2` 的 **显式用法**）—— ★ **真机建成** | `verified` | 0 |
| 106 | `curve_through_xyz` | 通过 XYZ 点的曲线（`InsertCurveFileBegin/Point/End` 三步式，★ 以及 **`InsertCurveFile`** 从文件）—— ★ **两套用法均真机建成** | `verified` | 0 |
| 107 | `select_by_ray` | 射线选择（`IModelDocExtension.SelectByRay`，**11 参**）—— ★ **真机选中**·★★ **它是 `HoleWizard5` 定孔位的前置** | `verified` | 0 |
| 108 | `feature_hole_wizard5` | 高级孔 / 异型孔向导（`IFeatureManager.HoleWizard5`，**27 参**）—— ★ **真机建成**·★★ **产出的是真的异型孔向导特征** | `verified` | 0 |
| 109 | `sketch_offset_on_surface` | 曲面上偏移（`IModelDocExtension.SketchOffsetOnSurface`）—— ★ **真机建成**·★★ **三步缺一不可** | `verified` | 0 |
| 110 | `coverage_gap_batch1` | 覆盖面缺口批 1：旋转曲面 · 孔向导 · 完全定义检查（★ 规格 `202-user-coverage-gaps`） | `verified` | 0 |

## 三、③ 正向差集 ＝ 已挂工具但台账没有

**49** 条（占已挂工具 264 条的 18.6%）。

| 工具名 | batch 文件 | 台账最接近条目 | 判断 |
|---|---|---|---|
| `solidworks_select_face_selector` | `tool_specs_batch63.py` | 近邻工具 `['selection_helpers']` → `selection_helpers`（选择器底座（声明式选择 + 当前选区读数 + 可选值枚举）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：select、selector） |
| `solidworks_simulation_apply_link_connector` | `tool_specs_batch64.py` | 近邻工具 `['simulation_load_family_breadth']` → `simulation_load_family_breadth`（仿真载荷族广度（压力 / 力矩 / 重力 / 离心力 4 类）—— ★ 未真机验证） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：apply、connector、simulation） |
| `solidworks_sketch_add_3point_rectangle` | `tool_specs_batch65.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：add、rectangle、sketch） |
| `solidworks_sketch_add_3point_center_rectangle` | `tool_specs_batch65.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：add、rectangle、sketch） |
| `solidworks_sketch_add_parallelogram` | `tool_specs_batch65.py` | 近邻工具 `['holes_and_finishing']` → `holes_and_finishing`（孔槽、螺纹、圆角与倒角） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：add、sketch） |
| `solidworks_sketch_add_tangent_arc` | `tool_specs_batch65.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：add、arc、sketch） |
| `solidworks_sketch_add_3point_arc` | `tool_specs_batch65.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：add、arc、sketch） |
| `solidworks_sketch_add_partial_ellipse` | `tool_specs_batch65.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：add、ellipse、sketch） |
| `solidworks_sketch_add_parabola` | `tool_specs_batch65.py` | 近邻工具 `['holes_and_finishing']` → `holes_and_finishing`（孔槽、螺纹、圆角与倒角） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：add、sketch） |
| `solidworks_sketch_add_conic` | `tool_specs_batch65.py` | 近邻工具 `['holes_and_finishing']` → `holes_and_finishing`（孔槽、螺纹、圆角与倒角） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：add、sketch） |
| `solidworks_sketch_add_perimeter_circle` | `tool_specs_batch65.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：add、circle、sketch） |
| `solidworks_sketch_trim` | `tool_specs_batch66.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「sketch」重合，**不作归属判定**） |
| `solidworks_sketch_extend` | `tool_specs_batch66.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「sketch」重合，**不作归属判定**） |
| `solidworks_sketch_offset` | `tool_specs_batch66.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「sketch」重合，**不作归属判定**） |
| `solidworks_sketch_fillet` | `tool_specs_batch66.py` | 近邻工具 `['chamfer_fillet_on_selection']` → `chamfer_fillet_on_selection`（倒角 / 圆角（作用于声明式选择选中的边）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「fillet」重合，**不作归属判定**） |
| `solidworks_sketch_linear_pattern` | `tool_specs_batch66.py` | 近邻工具 `['part_and_features', 'pattern_and_mirror']` → `part_and_features`（参数化零件与基础特征）、`pattern_and_mirror`（阵列与镜像（特征级的重复几何）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「pattern」重合，**不作归属判定**） |
| `solidworks_sketch_circular_pattern` | `tool_specs_batch66.py` | 近邻工具 `['part_and_features', 'pattern_and_mirror']` → `part_and_features`（参数化零件与基础特征）、`pattern_and_mirror`（阵列与镜像（特征级的重复几何）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：circular、pattern） |
| `solidworks_sketch_move_entities` | `tool_specs_batch67.py` | 近邻工具 `['sketch_edit_ops']` → `sketch_edit_ops`（草图编辑（倒角 / 镜像 / 转换实体引用）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：entities、sketch） |
| `solidworks_sketch_rotate_entities` | `tool_specs_batch67.py` | 近邻工具 `['sketch_edit_ops']` → `sketch_edit_ops`（草图编辑（倒角 / 镜像 / 转换实体引用）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：entities、sketch） |
| `solidworks_sketch_scale_entities` | `tool_specs_batch67.py` | 近邻工具 `['sketch_edit_ops']` → `sketch_edit_ops`（草图编辑（倒角 / 镜像 / 转换实体引用）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：entities、sketch） |
| `solidworks_sketch_stretch_entities` | `tool_specs_batch67.py` | 近邻工具 `['sketch_edit_ops']` → `sketch_edit_ops`（草图编辑（倒角 / 镜像 / 转换实体引用）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：entities、sketch） |
| `solidworks_sketch_flip_entities` | `tool_specs_batch67.py` | 近邻工具 `['sketch_edit_ops']` → `sketch_edit_ops`（草图编辑（倒角 / 镜像 / 转换实体引用）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：entities、sketch） |
| `solidworks_insert_planar_surface` | `tool_specs_batch68.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_offset_surface` | `tool_specs_batch68.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_ruled_surface` | `tool_specs_batch68.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_delete_face` | `tool_specs_batch68.py` | 近邻工具 `['equations']` → `equations`（方程式（增 / 列 / 删 / 求解）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「delete」重合，**不作归属判定**） |
| `solidworks_insert_replace_face` | `tool_specs_batch68.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_lofted_ref_surface` | `tool_specs_batch69.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_center_of_mass` | `tool_specs_batch70.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_global_bounding_box` | `tool_specs_batch70.py` | 近邻工具 `['modeling_feature_readback_tools']` → `modeling_feature_readback_tools`（建模闭环补全（抽壳 ✅ / 圆顶 ✅ 真机通过 · 筋 未验 · 复合曲线 真机失败）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：bounding、box） |
| `solidworks_insert_coordinate_system` | `tool_specs_batch70.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_ref_plane` | `tool_specs_batch70.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_reference_point` | `tool_specs_batch70.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_insert_curve_through_points` | `tool_specs_batch71.py` | 近邻工具 `['modeling_feature_readback_tools']` → `modeling_feature_readback_tools`（建模闭环补全（抽壳 ✅ / 圆顶 ✅ 真机通过 · 筋 未验 · 复合曲线 真机失败）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：curve、insert） |
| `solidworks_create_revolved_surface` | `tool_specs_batch72.py` | 近邻工具 `['surface_features']` → `surface_features`（复杂曲面与连续性检查） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：create、surface） |
| `solidworks_hole_wizard` | `tool_specs_batch72.py` | 近邻工具 `['holes_and_finishing']` → `holes_and_finishing`（孔槽、螺纹、圆角与倒角） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「hole」重合，**不作归属判定**） |
| `solidworks_sketch_fully_defined_status` | `tool_specs_batch72.py` | 近邻工具 `['sketch_build']` → `sketch_build`（建草图与画基本几何（线 / 圆 / 矩形）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「sketch」重合，**不作归属判定**） |
| `solidworks_drawing_create_broken_view` | `tool_specs_batch73.py` | 近邻工具 `['drawing_view_operations']` → `drawing_view_operations`（工程图视图操作（取视图 / 比例 / 注释数 / 可见件数）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：drawing、view） |
| `solidworks_drawing_create_auxiliary_view` | `tool_specs_batch73.py` | 近邻工具 `['drawing_view_operations']` → `drawing_view_operations`（工程图视图操作（取视图 / 比例 / 注释数 / 可见件数）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：drawing、view） |
| `solidworks_drawing_insert_surface_finish_symbol` | `tool_specs_batch73.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_drawing_insert_datum_tag` | `tool_specs_batch73.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |
| `solidworks_drawing_create_projected_view` | `tool_specs_batch75.py` | 近邻工具 `['drawing_view_operations']` → `drawing_view_operations`（工程图视图操作（取视图 / 比例 / 注释数 / 可见件数）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：drawing、view） |
| `solidworks_drawing_create_section_view` | `tool_specs_batch75.py` | 近邻工具 `['drawing_view_operations']` → `drawing_view_operations`（工程图视图操作（取视图 / 比例 / 注释数 / 可见件数）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：drawing、view） |
| `solidworks_drawing_create_detail_view` | `tool_specs_batch75.py` | 近邻工具 `['drawing_view_operations']` → `drawing_view_operations`（工程图视图操作（取视图 / 比例 / 注释数 / 可见件数）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（2 个词元重合：drawing、view） |
| `solidworks_drawing_set_sheet_format` | `tool_specs_batch75.py` | 近邻工具 `['drawing_current_sheet_query']` → `drawing_current_sheet_query`（工程图当前图纸的轻量只读读数（几张纸 / 图幅 / 视图清单）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配强（3 个词元重合：drawing、set、sheet） |
| `solidworks_drawing_add_note` | `tool_specs_batch75.py` | 近邻工具 `['part_and_features']` → `part_and_features`（参数化零件与基础特征） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「add」重合，**不作归属判定**） |
| `solidworks_drawing_create_hole_table` | `tool_specs_batch75.py` | 近邻工具 `['config_and_export', 'configurations_and_design_tables']` → `config_and_export`（配置与设计表）、`configurations_and_design_tables`（配置族 + 导出族（★ 真机 10/12：配置 5/6 · 导出 5/6）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「create」重合，**不作归属判定**） |
| `solidworks_drawing_create_revision_table` | `tool_specs_batch75.py` | 近邻工具 `['config_and_export', 'configurations_and_design_tables']` → `config_and_export`（配置与设计表）、`configurations_and_design_tables`（配置族 + 导出族（★ 真机 10/12：配置 5/6 · 导出 5/6）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「create」重合，**不作归属判定**） |
| `solidworks_drawing_insert_center_marks` | `tool_specs_batch75.py` | 近邻工具 `['gtol_insert']` → `gtol_insert`（形位公差：新建 GTol（InsertGtol）） | 已挂工具、台账 `mcp_tools` 未引用；近邻匹配弱（仅 1 个词元「insert」重合，**不作归属判定**） |

## 四、附带事实：反向差集（不在 S2-a 判据内，仅记录）

台账 `mcp_tools` 引用了 **11** 个**不在** `tool_specs_*.py` 里的工具名：`cadstudio_build_dxf_preview_scene`、`cadstudio_check_dfm`、`cadstudio_check_routing`、`cadstudio_routing_preflight`、`cadstudio_write_open_format`、`solidworks_addin_host_status`、`solidworks_pack_and_go`、`solidworks_surface_extend`、`solidworks_surface_fill`、`solidworks_surface_knit`、`solidworks_undo`。

⇒ 它们注册在别处（本次**未查**，不做任何断言）。反向存在即说明「台账有」**不**等于「写在 `tool_specs_*.py` 里」，两向差集要分开看。

## 五、可复核口径（落盘瞬间的数字）

```
tool_specs_*.py 文件数  = 74
工具名（去重）          = 264
台账条目数              = 110
台账工具引用（去重）    = 226
正向差集（工具 - 台账） = 49
反向差集（台账 - 工具） = 11   （仅记录，非本题判据）
```
