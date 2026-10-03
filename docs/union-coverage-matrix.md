# 并集广度地图

> **本文件是生成物** —— 由 `tools/build_union_map.py` 从
> `tools/union-sources.json` + `capabilities.yaml` 生成，不要手改。
>
> 配套规范：`docs/union-conventions.md`（命名 / 单位 / 选择 / 验证等级 / 出处 / 失败要响）

## 一 来源与许可（读**真实 LICENSE 文件**判定，不采信 README 徽章）

| 来源 | 许可 | 工具数 | 操作数 | 它自己声明跑过的环境 | 能抄吗 |
|---|---|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | 187 | 178 | **未声明** | ✅ 可抄改商用 |
| `andrewbartels1/SolidworksMCP-python` | MIT | 128 | 121 | **未声明** | ✅ 可抄改商用 |
| `vespo92/SolidworksMCP-TS` | MIT | 103 | 98 | **未声明** | ✅ 可抄改商用 |
| `Slacker-LLC/solidworks-mcp` | Apache-2.0 | 92 | 89 | SW 2026 SP3.2 简体中文 | ✅ 可抄（**须带 NOTICE + 声明改动文件**） |
| **本仓库（上游 + 本次）** | MIT | 272 | 272 | 见 capabilities.yaml | — |

> ⚠ **验证口径的真相**：四家里只有 `Slacker-LLC` 声明全工具真机跑过。
> `Eduardof0nt` 工具最多（187），但**仓库内测试文件数为 0**。
> 详见每家的 `note` 字段（`tools/union-sources.json`）。

## 二 域 × 来源 矩阵

> ⚠ **两列口径不同，不可互相替代**（2026-10-01 加）：
> - **本仓库（MCP）** = `mcp-server/server.py` 里静态抽出的**工具名**。
>   「缺口」列是它相对四家并集算出来的 —— 量的是**MCP 暴露面**之差。
> - **本仓库能力面** = `scripts/sw_*.py` 的**公开函数数**。
>   本仓库的能力多数**没被暴露成 MCP 工具**（`AGENTS.md` 已知事实 25：
>   `server.py` 只引用 25 个模块，我们后补的 58+ 个一个都没进）。
>
> **⇒ 只看「缺口」列会把已有的域记成「零」**（例：焊件列显示 `·`，
> 而 `scripts/sw_weldment.py` 有 666 行 / 20 个函数且 `capabilities.yaml` 里是 `verified`）。
> **判断「该实现哪个域」请看能力面列；判断「该暴露哪个工具」才看 MCP 列。**
>
> - 能力面列里的 **`⚠`** = 该域**缺口(MCP) > 0 而我们已有 ≥5 个函数** ⇒ **它多半不是能力缺口，只是没暴露成 MCP 工具**。
>   ⚠ 这是**启发式标记**（阈值 5），不是判定；**要下结论仍须逐域人工核**。

| 域 | Eduardof0nt | andrewbartels1 | vespo92 | Slacker-LLC | 本仓库(MCP) | 本仓库能力面 | 并集 | 缺口(MCP) |
|---|---|---|---|---|---|---|---|---|
| ① 会话 / 文档 / 文件 | 14 | 22 | 10 | 7 | 16 | 59⚠ | 49 | **33** |
| ② 参考几何 | 3 | 3 | · | 3 | 1 | 32⚠ | 5 | **4** |
| ③ 草图 | 26 | 15 | 16 | 20 | 40 | 99⚠ | 74 | **34** |
| ④ 尺寸 / 约束 / 参数 | 6 | 2 | 6 | 2 | 6 | 18⚠ | 16 | **10** |
| ⑤ 零件特征 | 23 | 11 | 3 | 13 | 22 | 82⚠ | 47 | **25** |
| ⑥ 曲面 | 11 | · | 1 | · | 12 | 31⚠ | 21 | **9** |
| ⑦ 钣金 | 10 | · | 1 | · | 6 | 16⚠ | 17 | **11** |
| ⑧ 焊件 | 5 | · | · | · | 12 | 15⚠ | 17 | **5** |
| ⑨ 模具 | 3 | · | · | · | 7 | 8⚠ | 10 | **3** |
| ⑩ 装配 | 13 | 7 | 4 | 3 | 10 | 55⚠ | 29 | **19** |
| ⑪ 工程图 | 18 | 18 | 15 | 17 | 19 | 55⚠ | 68 | **49** |
| ⑫ 检查 / 测量 / 反馈 | 11 | 3 | 7 | 6 | 6 | 28⚠ | 22 | **16** |
| ⑬ 仿真 / Motion | 3 | · | 1 | · | 30 | 105⚠ | 34 | **4** |
| ⑭ 外观 / 材质 / 配置 | 10 | 1 | 3 | 2 | 12 | 46⚠ | 22 | **10** |
| ⑮ 宏 / 自动化 | 4 | 22 | 21 | · | 1 | 19⚠ | 43 | **42** |
| ⑯ 高级 / 专项（含护城河候选） | · | · | · | · | 27 | 14 | 27 | ✓ |
| ⑰ 未归类 | 18 | 17 | 10 | 16 | 45 | 469⚠ | 87 | **42** |

**合计**：并集 588 个操作；**MCP 暴露面**缺 **316** 个（**不是**能力缺口 —— 见上）。

### 缺口按域排序（大 → 小）

| 域 | 缺 |
|---|---|
| ⑪ 工程图 | 49 |
| ⑮ 宏 / 自动化 | 42 |
| ⑰ 未归类 | 42 |
| ③ 草图 | 34 |
| ① 会话 / 文档 / 文件 | 33 |
| ⑤ 零件特征 | 25 |
| ⑩ 装配 | 19 |
| ⑫ 检查 / 测量 / 反馈 | 16 |
| ⑦ 钣金 | 11 |
| ④ 尺寸 / 约束 / 参数 | 10 |
| ⑭ 外观 / 材质 / 配置 | 10 |
| ⑥ 曲面 | 9 |
| ⑧ 焊件 | 5 |
| ② 参考几何 | 4 |
| ⑬ 仿真 / Motion | 4 |
| ⑨ 模具 | 3 |

### 不做 + 原因（A1 的另一半）

> `AGENTS.md §一 A1`：「…每一格**都有来源，或写明「不做 + 原因」**」。
> **有来源**那一半由 `capabilities.yaml` 的 `source`/`source_evidence` 承担（R12/R13 守着）；
> **本表**承担「不做 + 原因」那一半。数据源 `docs/union-not-doing.json`，形状由 R14 守。
>
> ⚠ **本表是显式清单，不是默认放行** —— 没登记在这里、又没在 `capabilities.yaml` 里的，
> 就仍是**缺口**（见上表的「缺 N」），不是「不做」。

| 不做 | 原因 | 依据（可核） |
|---|---|---|
| 动画导出 AVI（Motion 分析算例） | **环境受限** —— 本机没有 SolidWorks Motion 加载项，而 AVI 导出需要 CosmosMotion 系列算例。 | · 真机实测（2026-10-01 轮 66，`D:\AI\SW\probe_motion_addin.py`）：set StudyType=4/8/16（CosmosMotion 家族）⇒ **回读仍是 2，静默失败**；1（Assembly）与 2（PhysicalSimulation）能生效但导出仍失败。<br>· Motion 加载项 4 个 ProgID 全返 None：`CMotionswapi.CMOTIONSWAddin` · `SldWorks.Motion` · `SolidWorks.Motion` · `SWMotionStudy.SWMotionStudyAddin`。<br>· 验收命令 `python tools/verify_motion_avi_e2e.py` ⇒ `verdict: fail`（已排除 6 种条件）。<br>· ⚠ **`AGENTS.md §九.4`：需要用户提供的东西 ⇒ 停下报告，不自行拍板。** 需要用户提供 **SolidWorks Motion 加载项**。<br>· ⓘ **装上即可闭合**：`capabilities.yaml` 的 `animation_export` 现为 `stitched`，装上后跑验收脚本得 `verdict: pass` 即可升 `verified`。 |
| AGPL / GPL / 无许可 / 全版权保留 来源的**代码移植** | **许可红线**（`AGENTS.md §二 铁律 6`）：那几类**只读思想**，不抄代码、不抄文本。 | · `AGENTS.md §二 铁律 6` 的许可表：MIT「读抄改商用」· Apache-2.0「+ NOTICE」· AGPL/GPL「**只读思想**」· 无许可/全版权保留「**只读思想**」。<br>· `scripts/check_license_redlines.py`（A6 门禁）在核「来源块声明的许可是否在白名单内」。<br>· ⓘ 已评估但**未并入**的 AGPL 类来源见 `THIRD-PARTY-NOTICES.md §二`。 |
| 破解相关（SolidWorks-CAD / Solidworks-Crack 类投递页、破解指南、序列号） | **零接触红线**（`AGENTS.md §二 铁律 2`）：不碰破解相关任何内容。 | · `AGENTS.md §二 铁律 2` 的红线段明写「破解相关…**零接触**」。<br>· 另两条红线：不动注册表 / 全局环境变量 / 系统层；未经确认不 push / 不建远端 / 不发 release。 |
| 对外发布（推远端 / 建自建远端 / 提 PR / release） | **未获授权**（用户已明示「GitHub 上的东西不着急，等我们完全开发完毕了再上传」）。 | · 用户原话：「GitHub上的东西不着急，等我们完全开发完毕了再上传」。<br>· `AGENTS.md §七` 的动作批准表：`git push`（任何远端）/ 提 PR / 发布 release **都要先批准**。<br>· ⇒ 本项目至今**只做本地 commit**（两仓库各自提交，已 179 个 commit）。 |

## 三 每个域的**独家来源**（只有一家有 ⇒ 只能抄它，且必须自己测）

| 域 | 独家操作 | 唯一来源 |
|---|---|---|
| ① 会话 / 文档 / 文件 | 26 个：`activate_document`, `active_document_info`, `apply_template`, `close_all`, `close_document`, `compare_templates`… | andrewbartels1/SolidworksMCP-python |
| ② 参考几何 | 1 个：`reference_planes` | Slacker-LLC/solidworks-mcp |
| ③ 草图 | 16 个：`3d_sketch`, `3point_arc`, `check_sketch_fully_defined`, `close_sketch`, `construction_geometry`, `convert_entities`… | Eduardof0nt/Solidworks-MCP-Server |
| ④ 尺寸 / 约束 / 参数 | 8 个：`delete_equation`, `design_table_create`, `design_table_refresh`, `diameter_dimension`, `global_var`, `link_dimension_to_equation`… | Eduardof0nt/Solidworks-MCP-Server |
| ⑤ 零件特征 | 17 个：`combine_bodies`, `curve_driven_pattern`, `delete_body`, `dome`, `fill_pattern`, `helix`… | Eduardof0nt/Solidworks-MCP-Server |
| ⑥ 曲面 | 9 个：`boundary_boss`, `extend_surface`, `extruded_surface`, `filled_surface`, `knit_surfaces`, `revolved_surface`… | Eduardof0nt/Solidworks-MCP-Server |
| ⑦ 钣金 | 11 个：`base_flange`, `edge_flange`, `export_flat_pattern`, `flat_pattern_info`, `flatten_sheet_metal`, `hem`… | Eduardof0nt/Solidworks-MCP-Server |
| ⑧ 焊件 | 5 个：`end_cap`, `gusset`, `structural_member`, `trim_weldment`, `weld_symbol` | Eduardof0nt/Solidworks-MCP-Server |
| ⑨ 模具 | 3 个：`parting_line`, `shut_off_surface`, `tooling_split` | Eduardof0nt/Solidworks-MCP-Server |
| ⑩ 装配 | 16 个：`assembly_analysis`, `assembly_components`, `assembly_mates`, `assembly_tree`, `explode_assembly`, `fix_component`… | vespo92/SolidworksMCP-TS |
| ⑪ 工程图 | 38 个：`activate_drawing_view`, `activate_sheet`, `analyze_drawing_annotations`, `analyze_drawing_comprehensive`, `analyze_drawing_dimensions`, `analyze_drawing_views`… | Slacker-LLC/solidworks-mcp |
| ⑫ 检查 / 测量 / 反馈 | 9 个：`analyze_geometry`, `calculate_mass_properties`, `check_errors`, `display_mode`, `measure`, `reference_geometry`… | andrewbartels1/SolidworksMCP-python |
| ⑬ 仿真 / Motion | 4 个：`motion_study`, `run_simulation`, `simulation_setup`, `simulation_study` | Eduardof0nt/Solidworks-MCP-Server |
| ⑭ 外观 / 材质 / 配置 | 8 个：`activate_display_state`, `appearance_color`, `assembly_configurations`, `background`, `display_states`, `materials`… | Eduardof0nt/Solidworks-MCP-Server |
| ⑮ 宏 / 自动化 | 37 个：`analyze_macro`, `batch_execute_macros`, `batch_file_operations`, `batch_operations`, `batch_process_files`, `batch_run_macros`… | andrewbartels1/SolidworksMCP-python |
| ⑰ 未归类 | 31 个：`advanced_features`, `api_automation`, `classify_feature_tree`, `composite_curve`, `edges`, `error_handling`… | vespo92/SolidworksMCP-TS |

## 四 本仓库独家（别人都没有）

共 239 个操作只有本仓库有：

- `activate_model_for_preview`（⑰ 未归类）
- `active_view`（⑪ 工程图）
- `addin_host_status`（⑰ 未归类）
- `assembly_check_interference`（⑩ 装配）
- `assembly_list_components`（⑩ 装配）
- `assembly_list_mates`（⑩ 装配）
- `auto_dimension_sketch`（③ 草图）
- `available_direction_selectors`（⑰ 未归类）
- `available_point_selectors`（⑰ 未归类）
- `basic_part`（⑰ 未归类）
- `batch_export_files`（⑮ 宏 / 自动化）
- `check_dfm`（⑯ 高级 / 专项（含护城河候选））
- `check_routing`（⑯ 高级 / 专项（含护城河候选））
- `clear_selection_for_preview`（⑰ 未归类）
- `close_documents`（① 会话 / 文档 / 文件）
- `coincident_mate`（⑩ 装配）
- `collect_appearance_evidence`（⑭ 外观 / 材质 / 配置）
- `collect_assembly_bom`（⑩ 装配）
- `collect_model_summary`（⑰ 未归类）
- `concentric_mate`（⑩ 装配）
- `config_activate`（⑭ 外观 / 材质 / 配置）
- `config_create`（⑭ 外观 / 材质 / 配置）
- `config_inspect`（⑭ 外观 / 材质 / 配置）
- `config_read_custom_property`（⑭ 外观 / 材质 / 配置）
- `config_set_custom_properties`（⑭ 外观 / 材质 / 配置）
- `config_update_dimension`（⑭ 外观 / 材质 / 配置）
- `costing_body_count`（⑯ 高级 / 专项（含护城河候选））
- `costing_default_template`（⑯ 高级 / 专项（含护城河候选））
- `costing_evidence`（⑯ 高级 / 专项（含护城河候选））
- `costing_list_bodies`（⑯ 高级 / 专项（含护城河候选））
- `costing_list_templates`（⑯ 高级 / 专项（含护城河候选））
- `costing_manager`（⑯ 高级 / 专项（含护城河候选））
- `costing_method_value`（⑯ 高级 / 专项（含护城河候选））
- `costing_read_analysis`（⑯ 高级 / 专项（含护城河候选））
- `costing_read_body`（⑯ 高级 / 专项（含护城河候选））
- `current_selection`（⑰ 未归类）
- `current_sketch_name`（③ 草图）
- `custom_property_count`（⑰ 未归类）
- `custom_property_get`（⑰ 未归类）
- `custom_property_list`（⑰ 未归类）
- `custom_property_names`（⑰ 未归类）
- `delivery_bom_traceability`（⑰ 未归类）
- `delivery_export_bom_csv`（① 会话 / 文档 / 文件）
- `delivery_pack_and_go_audit_matrix`（⑰ 未归类）
- `distance_mate`（⑩ 装配）
- `drawing_collect_view_evidence`（⑪ 工程图）
- `drawing_current_sheet_info`（⑪ 工程图）
- `drawing_current_sheet_name`（⑪ 工程图）
- `drawing_get_current_sheet`（⑪ 工程图）
- `drawing_list_sheets`（⑪ 工程图）
- `drawing_list_views`（⑪ 工程图）
- `drawing_set_sheet_scale`（⑪ 工程图）
- `drawing_sheet_count`（⑪ 工程图）
- `drawing_sheet_names`（⑪ 工程图）
- `drawing_sheet_scale`（⑪ 工程图）
- `drawing_sheets_summary`（⑪ 工程图）
- `drawing_view_scale`（⑪ 工程图）
- `drawing_view_set_scale`（⑪ 工程图）
- `dxf_preview_scene`（⑰ 未归类）
- `entities_on_body`（⑤ 零件特征）
- `equation_add`（④ 尺寸 / 约束 / 参数）
- `equation_delete`（④ 尺寸 / 约束 / 参数）
- `equation_evaluate`（④ 尺寸 / 约束 / 参数）
- `equation_list`（④ 尺寸 / 约束 / 参数）
- `export_active`（① 会话 / 文档 / 文件）
- `export_assembly_bom`（⑩ 装配）
- `export_bmp`（① 会话 / 文档 / 文件）
- `export_dxf`（① 会话 / 文档 / 文件）
- `export_parasolid`（① 会话 / 文档 / 文件）
- `extrude_boss`（⑤ 零件特征）
- `extrude_midplane`（⑤ 零件特征）
- `fastener_table_types`（⑰ 未归类）
- `fastener_types`（⑰ 未归类）
- `fea_preflight`（⑰ 未归类）
- `gear_calculate_spur`（⑰ 未归类）
- `gear_create_spur`（⑰ 未归类）
- `generate_drawing`（⑪ 工程图）
- `gtol_insert`（⑰ 未归类）
- `health_check`（⑰ 未归类）
- `helix_insert`（⑤ 零件特征）
- `hole_blind_by_selection`（⑤ 零件特征）
- `hole_counterbore_by_selection`（⑤ 零件特征）
- `hole_countersink_by_selection`（⑤ 零件特征）
- `hole_feature`（⑤ 零件特征）
- `hole_pattern`（⑤ 零件特征）
- `hole_standards`（⑤ 零件特征）
- `hole_through_by_selection`（⑤ 零件特征）
- `inspect_configurations`（⑭ 外观 / 材质 / 配置）
- `inspect_drawing`（⑪ 工程图）
- `inspect_hole_features`（⑫ 检查 / 测量 / 反馈）
- `inspect_motion_studies`（⑬ 仿真 / Motion）
- `measure_selection`（⑫ 检查 / 测量 / 反馈）
- `mold_core_cavity_split`（⑨ 模具）
- `mold_draft_analysis`（⑨ 模具）
- `mold_evidence`（⑨ 模具）
- `mold_parting_line`（⑨ 模具）
- `mold_parting_surface`（⑨ 模具）
- `mold_shut_off_surface`（⑨ 模具）
- `mold_undercut_detect`（⑨ 模具）
- `motion_collect_summary`（⑬ 仿真 / Motion）
- `motion_create_study`（⑬ 仿真 / Motion）
- `motion_ensure_type_library`（⑬ 仿真 / Motion）
- `motion_study_manager`（⑬ 仿真 / Motion）
- `motion_validate_studies`（⑬ 仿真 / Motion）
- `motion_validate_summary`（⑬ 仿真 / Motion）
- `ocp_loft`（⑥ 曲面）
- `ocp_surface`（⑥ 曲面）
- `pack_and_go`（⑰ 未归类）
- `part_axis`（② 参考几何）
- `part_bounding_box`（⑫ 检查 / 测量 / 反馈）
- `part_insert_composite_curve`（⑰ 未归类）
- `part_insert_dome`（⑤ 零件特征）
- `part_loft`（⑥ 曲面）
- `part_mass_properties`（⑫ 检查 / 测量 / 反馈）
- `part_rib`（⑤ 零件特征）
- `part_shell`（⑤ 零件特征）
- `part_sweep`（⑤ 零件特征）
- `part_wrap`（⑤ 零件特征）
- `prepare_fea`（⑰ 未归类）
- `read_document_units`（① 会话 / 文档 / 文件）
- `read_sensors`（⑫ 检查 / 测量 / 反馈）
- `refresh_scene_graph`（⑰ 未归类）
- `render_materials`（⑭ 外观 / 材质 / 配置）
- `replace_face`（⑰ 未归类）
- `resolve_backend`（⑰ 未归类）
- `resolve_entity`（⑰ 未归类）
- `resolve_selection`（⑰ 未归类）
- `review_active`（⑰ 未归类）
- `review_advanced_geometry`（⑫ 检查 / 测量 / 反馈）
- `review_drawing`（⑪ 工程图）
- `review_report`（⑰ 未归类）
- `revolve_boss`（⑤ 零件特征）
- `rotary_motor`（⑰ 未归类）
- `routing_preflight`（⑯ 高级 / 专项（含护城河候选））
- `ruled_surface`（⑥ 曲面）
- `run_fea`（⑰ 未归类）
- `run_fea_convergence`（⑰ 未归类）
- `select_by_selector`（⑰ 未归类）
- `select_entity_by_index`（⑰ 未归类）
- `select_face_selector`（⑰ 未归类）
- `selection_count`（⑰ 未归类）
- `selection_point`（⑰ 未归类）
- `selector_resolve_direction`（⑰ 未归类）
- `selector_resolve_point`（⑰ 未归类）
- `sheet_metal_create_base_flange`（⑦ 钣金）
- `sheet_metal_create_draft`（⑦ 钣金）
- `sheet_metal_create_edge_flange`（⑦ 钣金）
- `sheet_metal_create_gusset`（⑧ 焊件）
- `sheet_metal_create_one_bend`（⑦ 钣金）
- `sheet_metal_create_swept_flange`（⑦ 钣金）
- `sheet_metal_evidence`（⑦ 钣金）
- `simulation_apply_fixed_restraint`（⑬ 仿真 / Motion）
- `simulation_apply_link_connector`（⑬ 仿真 / Motion）
- `simulation_apply_normal_force`（⑬ 仿真 / Motion）
- `simulation_apply_rigid_connector`（⑬ 仿真 / Motion）
- `simulation_check_mesh_size`（⑬ 仿真 / Motion）
- `simulation_collect_evidence`（⑬ 仿真 / Motion）
- `simulation_configure_buckling_solver`（⑬ 仿真 / Motion）
- `simulation_configure_frequency_solver`（⑬ 仿真 / Motion）
- `simulation_configure_static_solver`（⑬ 仿真 / Motion）
- `simulation_create_mesh`（⑬ 仿真 / Motion）
- `simulation_create_mesh_for_control`（⑬ 仿真 / Motion）
- `simulation_create_study`（⑬ 仿真 / Motion）
- `simulation_default_element_size_and_tolerance`（⑯ 高级 / 专项（含护城河候选））
- `simulation_find_study`（⑬ 仿真 / Motion）
- `simulation_generate_report`（⑬ 仿真 / Motion）
- `simulation_list_setter_summary`（⑬ 仿真 / Motion）
- `simulation_list_studies`（⑬ 仿真 / Motion）
- `simulation_mesh_size`（⑬ 仿真 / Motion）
- `simulation_run_analysis`（⑬ 仿真 / Motion）
- `simulation_set_material`（⑬ 仿真 / Motion）
- `simulation_set_study_option`（⑬ 仿真 / Motion）
- `simulation_set_study_options`（⑬ 仿真 / Motion）
- `simulation_study_options`（⑬ 仿真 / Motion）
- `sketch_add_3point_arc`（③ 草图）
- `sketch_add_3point_center_rectangle`（③ 草图）
- `sketch_add_3point_rectangle`（③ 草图）
- `sketch_add_arc`（③ 草图）
- `sketch_add_centerline`（⑪ 工程图）
- `sketch_add_circle`（③ 草图）
- `sketch_add_conic`（③ 草图）
- `sketch_add_ellipse`（③ 草图）
- `sketch_add_line`（③ 草图）
- `sketch_add_parabola`（③ 草图）
- `sketch_add_parallelogram`（③ 草图）
- `sketch_add_partial_ellipse`（③ 草图）
- `sketch_add_perimeter_circle`（③ 草图）
- `sketch_add_polygon`（③ 草图）
- `sketch_add_rectangle`（③ 草图）
- `sketch_add_slot`（③ 草图）
- `sketch_add_tangent_arc`（③ 草图）
- `sketch_count_arcs`（③ 草图）
- `sketch_count_lines`（③ 草图）
- `sketch_count_segments`（③ 草图）
- `sketch_create_chamfer`（③ 草图）
- `sketch_end`（③ 草图）
- `sketch_flip_entities`（③ 草图）
- `sketch_is_3d`（③ 草图）
- `sketch_move_entities`（③ 草图）
- `sketch_relation`（③ 草图）
- `sketch_rotate_entities`（③ 草图）
- `sketch_scale_entities`（③ 草图）
- `sketch_start`（③ 草图）
- `sketch_stretch_entities`（③ 草图）
- `slot_semicircular_by_selection`（③ 草图）
- `standard_view`（⑪ 工程图）
- `surface_create_extruded`（⑥ 曲面）
- `surface_evidence`（⑥ 曲面）
- `surface_extend`（⑥ 曲面）
- `surface_fill`（⑥ 曲面）
- `surface_knit`（⑥ 曲面）
- `toolbox_list_standards`（⑯ 高级 / 专项（含护城河候选））
- `toolbox_load_index`（⑯ 高级 / 专项（含护城河候选））
- `toolbox_part_path`（⑯ 高级 / 专项（含护城河候选））
- `toolbox_search`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_demold_control`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_factor_of_safety_constraint`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_mass_constraint`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_preserved_region`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_stress_constraint`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_study`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_symmetry_control`（⑯ 高级 / 专项（含护城河候选））
- `topology_create_thickness_control`（⑯ 高级 / 专项（含护城河候选））
- `topology_evidence`（⑯ 高级 / 专项（含护城河候选））
- `topology_run`（⑯ 高级 / 专项（含护城河候选））
- `update_dimension`（④ 尺寸 / 约束 / 参数）
- `validate_motion_study`（⑬ 仿真 / Motion）
- `weldment_create_cut_list`（⑧ 焊件）
- `weldment_create_profile_center_mate`（⑧ 焊件）
- `weldment_create_structural_member`（⑧ 焊件）
- `weldment_create_sub_weld_folder`（⑧ 焊件）
- `weldment_create_weldment_profile`（⑧ 焊件）
- `weldment_ensure_cut_list`（⑧ 焊件）
- `weldment_evidence`（⑧ 焊件）
- `weldment_export_cut_list_csv`（⑧ 焊件）
- `weldment_read_property_manager`（⑧ 焊件）
- `weldment_set_cut_list_properties`（⑧ 焊件）
- `weldment_update_cut_list`（⑧ 焊件）
- `write_open_format`（① 会话 / 文档 / 文件）

## 五 可执行的并入清单（按域）

> **怎么读**：`来源` 列给出该域最有货的家；`来源验证` 列是**该来源自己声明的跑过的环境** —— 空 = **它没声明跑过**，抄进来只能先标 `stitched`，必须我们实测过才能升 `verified`（规则 4）。

### ① 会话 / 文档 / 文件（缺 33）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `andrewbartels1/SolidworksMCP-python` | 22 | MIT | **未声明** |
| `Eduardof0nt/Solidworks-MCP-Server` | 14 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 10 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 7 | Apache-2.0 | SW 2026 SP3.2 简体中文 |

缺口操作：`activate_document`、`active_document_info`、`apply_template`、`close_all`、`close_document`、`close_model`、`compare_templates`、`convert_file_format`、`export_document`、`export_dwg`、`export_file`、`export_pdf`、`export_with_options`、`extract_template`、`manage_file_properties`、`open_documents`、`open_model`、`part`、`rebuild_document`、`rebuild_model`、`referenced_documents`、`save_active_document`、`save_all`、`save_as`
（还有 9 个，见 `tools/union-sources.json`）

### ② 参考几何（缺 4）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 3 | MIT | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 3 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 3 | Apache-2.0 | SW 2026 SP3.2 简体中文 |

缺口操作：`ref_axis`、`ref_plane`、`reference_planes`、`reference_point`

### ③ 草图（缺 34）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 26 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 20 | Apache-2.0 | SW 2026 SP3.2 简体中文 |
| `vespo92/SolidworksMCP-TS` | 16 | MIT | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 15 | MIT | **未声明** |

缺口操作：`3d_sketch`、`3point_arc`、`check_sketch_fully_defined`、`circle`、`close_sketch`、`construction_geometry`、`convert_entities`、`edit_sketch`、`ellipse`、`exit_sketch`、`hide_all_sketches`、`polygon`、`rectangle`、`show_all_sketches`、`sketch`、`sketch_arc`、`sketch_chamfer`、`sketch_circle`、`sketch_constraint`、`sketch_construction`、`sketch_dimension`、`sketch_ellipse`、`sketch_line`、`sketch_polygon`
（还有 10 个，见 `tools/union-sources.json`）

### ④ 尺寸 / 约束 / 参数（缺 10）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 6 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 6 | MIT | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 2 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 2 | Apache-2.0 | SW 2026 SP3.2 简体中文 |

缺口操作：`delete_equation`、`design_table`、`design_table_create`、`design_table_refresh`、`diameter_dimension`、`equation`、`global_var`、`link_dimension_to_equation`、`manage_design_table`、`relation`

### ⑤ 零件特征（缺 25）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 23 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 13 | Apache-2.0 | SW 2026 SP3.2 简体中文 |
| `andrewbartels1/SolidworksMCP-python` | 11 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 3 | MIT | **未声明** |

缺口操作：`combine_bodies`、`curve_driven_pattern`、`delete_body`、`dome`、`draft`、`extrude`、`fill_pattern`、`helix`、`hole`、`intersect`、`linear_pattern`、`loft`、`mirror`、`move_body`、`pattern_circular`、`pattern_features`、`revolve`、`save_body_as_part`、`scale_body`、`shell`、`simple_extrude`、`split_body`、`sweep`、`tutorial_simple_hole`
（还有 1 个，见 `tools/union-sources.json`）

### ⑥ 曲面（缺 9）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 11 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 1 | MIT | **未声明** |

缺口操作：`boundary_boss`、`extend_surface`、`extruded_surface`、`filled_surface`、`knit_surfaces`、`revolved_surface`、`surface_modeling`、`thicken_surface`、`trim_surface`

### ⑦ 钣金（缺 11）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 10 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 1 | MIT | **未声明** |

缺口操作：`base_flange`、`edge_flange`、`export_flat_pattern`、`flat_pattern_info`、`flatten_sheet_metal`、`hem`、`jog`、`miter_flange`、`sheet_metal`、`sketched_bend`、`unfold`

### ⑧ 焊件（缺 5）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 5 | MIT | **未声明** |

缺口操作：`end_cap`、`gusset`、`structural_member`、`trim_weldment`、`weld_symbol`

### ⑨ 模具（缺 3）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 3 | MIT | **未声明** |

缺口操作：`parting_line`、`shut_off_surface`、`tooling_split`

### ⑩ 装配（缺 19）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 13 | MIT | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 7 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 4 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 3 | Apache-2.0 | SW 2026 SP3.2 简体中文 |

缺口操作：`assembly`、`assembly_analysis`、`assembly_components`、`assembly_mates`、`assembly_tree`、`components`、`explode_assembly`、`fix_component`、`hide_component`、`interference`、`load_assembly`、`mirror_component`、`move_component`、`pack_and_go_assembly`、`pattern_component_circular`、`pattern_component_linear`、`replace_component`、`save_assembly`、`suppress_component`

### ⑪ 工程图（缺 49）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 18 | MIT | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 18 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 17 | Apache-2.0 | SW 2026 SP3.2 简体中文 |
| `vespo92/SolidworksMCP-TS` | 15 | MIT | **未声明** |

缺口操作：`activate_drawing_view`、`activate_sheet`、`analyze_drawing_annotations`、`analyze_drawing_comprehensive`、`analyze_drawing_dimensions`、`analyze_drawing_views`、`annotation`、`apply_drawing_template`、`auto_center_marks`、`auto_dimension_view`、`auxiliary_view`、`balloon`、`bom`、`broken_view`、`center_mark`、`centerline`、`check_drawing_compliance`、`check_drawing_standards`、`compare_drawing_templates`、`compare_drawing_versions`、`detail_view`、`drawing`、`drawing_annotations`、`drawing_dimension`
（还有 25 个，见 `tools/union-sources.json`）

### ⑫ 检查 / 测量 / 反馈（缺 16）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 11 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 7 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 6 | Apache-2.0 | SW 2026 SP3.2 简体中文 |
| `andrewbartels1/SolidworksMCP-python` | 3 | MIT | **未声明** |

缺口操作：`analyze_draft`、`analyze_geometry`、`bbox`、`calculate_mass_properties`、`capture_screenshot`、`check_errors`、`check_geometry`、`display_mode`、`mass_props`、`measure`、`measure_distance`、`reference_geometry`、`sensors`、`status`、`view_orientation`、`zoom_to_fit`

### ⑬ 仿真 / Motion（缺 4）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 3 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 1 | MIT | **未声明** |

缺口操作：`motion_study`、`run_simulation`、`simulation_setup`、`simulation_study`

### ⑭ 外观 / 材质 / 配置（缺 10）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 10 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 3 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 2 | Apache-2.0 | SW 2026 SP3.2 简体中文 |
| `andrewbartels1/SolidworksMCP-python` | 1 | MIT | **未声明** |

缺口操作：`activate_display_state`、`appearance_color`、`assembly_configurations`、`background`、`configurations`、`display_states`、`material`、`materials`、`pdm_configure`、`take_photoview_screenshot`

### ⑮ 宏 / 自动化（缺 42）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `andrewbartels1/SolidworksMCP-python` | 22 | MIT | **未声明** |
| `vespo92/SolidworksMCP-TS` | 21 | MIT | **未声明** |
| `Eduardof0nt/Solidworks-MCP-Server` | 4 | MIT | **未声明** |

缺口操作：`analyze_macro`、`batch_apply_template`、`batch_execute_macros`、`batch_export`、`batch_file_operations`、`batch_operations`、`batch_process_files`、`batch_run_macros`、`batch_vba`、`configurations_batch`、`convert_text_to_native_macro`、`diagnose_macro_execution`、`drawing_vba`、`edit_macro`、`execute_macro`、`export_vba`、`feature_vba`、`generate_vba_assembly_insert`、`generate_vba_assembly_mates`、`generate_vba_batch_export`、`generate_vba_code`、`generate_vba_drawing_dimensions`、`generate_vba_drawing_views`、`generate_vba_extrusion`
（还有 18 个，见 `tools/union-sources.json`）

### ⑰ 未归类（缺 42）

| 来源 | 该域有 | 许可 | 来源验证 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | 18 | MIT | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 17 | MIT | **未声明** |
| `Slacker-LLC/solidworks-mcp` | 16 | Apache-2.0 | SW 2026 SP3.2 简体中文 |
| `vespo92/SolidworksMCP-TS` | 10 | MIT | **未声明** |

缺口操作：`advanced_features`、`api_automation`、`arc`、`bodies`、`classify_feature_tree`、`composite_curve`、`delete_feature`、`edges`、`error_handling`、`execute_workflow`、`faces`、`features`、`file_properties`、`fold`、`gdt`、`hide_all_planes`、`line`、`load_part`、`mate`、`mates`、`model_info`、`operations`、`optimize_performance`、`pdm_operations`
（还有 18 个，见 `tools/union-sources.json`）

