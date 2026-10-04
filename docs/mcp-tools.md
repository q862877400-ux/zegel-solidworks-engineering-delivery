# MCP 工具全量索引（★ 由 `tools/gen_tool_domain_catalogue.py` 生成，**不要手改**）

> ★ 按**域**分组；每条给：工具名 · 参数 · 注入键 · 一句话。
> ★ 用途：人/agent **按需查**（★ 不是每轮都读 —— 那正是本文件要避免的事）。

## `sw_part`（33 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_add_dimension` | x_mm, y_mm, selector, kind | `model` | ★ **给已选中的实体加一个显示尺寸**（官方 `IModelDoc2.AddDimension2`，**3 参**） |
| `solidworks_add_sketch_relation` | relation_type | `model` | Add a sketch geometric relation to the current selection. |
| `solidworks_auto_dimension_sketch` | — | `model` | ★ **按官方 `ISketch.AutoDimension2` 流程给当前草图建真实模型尺寸** ——★ 生成的尺寸是**真实的 `DisplayDimens |
| `solidworks_chamfer` | selection, distance_mm, angle_deg | `model` | Chamfer the selected edge(s). ★ The edge comes from `selection` (declarative), b |
| `solidworks_circular_pattern` | feature_name, axis_name, angle_deg, count, equal_spacing | `model` | Create a circular pattern about an axis. |
| `solidworks_current_sketch_name` | fallback | `model` | ★ **读当前活动草图的特征名** |
| `solidworks_extrude_boss` | sketch_name, depth_mm, direction, merge | `model` | Extrude a sketch into a solid BOSS (adds material). ★ This is the first tool in  |
| `solidworks_extrude_cut` | sketch_name, depth_mm, direction, flip | `model` | Extrude a sketch as a CUT (removes material). ★ depth_mm = 0 means through-all.  |
| `solidworks_extrude_midplane` | sketch_name, total_depth_mm | `model` | Extrude a sketch symmetrically about its plane. ⚠ The parameter is the TOTAL dep |
| `solidworks_feature_delete` | feature_name | `model` | Delete one FEATURE via `IModelDoc2.EditDelete()` (0 params, NOT deprecated). ★ I |
| `solidworks_feature_suppress` | feature_name | `model` | Suppress one FEATURE via the successor entry point `IModelDoc2.EditSuppress2()`  |
| `solidworks_feature_unsuppress` | feature_name | `model` | Unsuppress one FEATURE via the successor entry point `IModelDoc2.EditUnsuppress2 |
| `solidworks_fillet` | selection, radius_mm | `model` | Round the selected edge(s) with the given radius. ★ The edge comes from `selecti |
| `solidworks_mirror_feature` | feature_name, mirror_plane_name | `model` | Mirror an existing feature about a plane. |
| `solidworks_part_axis` | reverse | `model` | ★ **从当前选中的几何建一条参考轴** —— 走 `IModelDoc2.InsertAxis2`（★ **注意入口在 `IModelDoc2` 上**，不在 |
| `solidworks_part_bounding_box` | body_index, include_hidden | `model` | Get the bounding box of the first solid body. ⚠⚠ SOLIDWORKS documents the return |
| `solidworks_part_insert_composite_curve` | feature_name | `model` | Join the selected entities into a composite curve and return a READ-BACK report  |
| `solidworks_part_insert_dome` | height_mm, feature_name, reverse, elliptic | `model` | Add a dome on the selected face and return a READ-BACK report (★ rule 6). ⚠ The  |
| `solidworks_part_rib` | sketch_name, thickness_mm, feature_name, direction | `model` | Create a rib from an existing sketch and return a READ-BACK report (feature in t |
| `solidworks_part_shell` | thickness_mm, feature_name | `model` | Hollow the part with a wall thickness and return a READ-BACK report: whether the |
| `solidworks_revolve_boss` | sketch_name, angle_deg, axis_sketch_name | `model` | Revolve a profile sketch into a boss feature. ⚠ This call is routed through a cl |
| `solidworks_revolve_cut` | sketch_name, angle_deg, axis_sketch_name | `model` | ★ 官方签名（逐字，来自 FeatureRevolve2.md）：`Feature FeatureRevolve2( System.bool SingleDir |
| `solidworks_sketch_add_arc` | center_x_mm, center_y_mm, start_x_mm, start_y_mm, end_x_mm, end_y_mm, direction | `model` | ★ **在当前草图里画一段圆弧**（圆心 + 起点 + 终点） |
| `solidworks_sketch_add_centerline` | start_x_mm, start_y_mm, end_x_mm, end_y_mm, z_mm | `model` | ★ **在当前草图里画一条中心线**（官方 `ISketchManager.CreateCenterLine`） |
| `solidworks_sketch_add_circle` | center_x_mm, center_y_mm, radius_mm | `model` | Draw a CIRCLE in the open sketch. ⚠ Sketch geometry MUST be given as in-plane co |
| `solidworks_sketch_add_ellipse` | center_x_mm, center_y_mm, major_x_mm, major_y_mm, minor_x_mm, minor_y_mm, z_mm | `model` | ★ **在当前草图里画一个整椭圆**（官方 `ISketchManager.CreateEllipse`） |
| `solidworks_sketch_add_line` | start_x_mm, start_y_mm, end_x_mm, end_y_mm | `model` | Draw a straight LINE in the open sketch. ⚠ Sketch geometry MUST be given as in-p |
| `solidworks_sketch_add_polygon` | center_x_mm, center_y_mm, radius_mm, sides | `model` | ★ **在当前草图里画正多边形**（**内切圆**方式 —— 官方 `CreatePolygon` 的口径） |
| `solidworks_sketch_add_rectangle` | x1_mm, y1_mm, x2_mm, y2_mm | `model` | Draw a RECTANGLE in the open sketch, given TWO OPPOSITE CORNERS. ⚠ Not the same  |
| `solidworks_sketch_add_slot` | start_x_mm, start_y_mm, end_x_mm, end_y_mm, radius_mm | `model` | ★ **在当前草图里画槽口**（直槽 / 腰形孔 —— 两点 + 半径） |
| `solidworks_sketch_end` | — | `model` | Leave the current sketch. ★ The resulting sketch reference is reusable by solidw |
| `solidworks_sketch_spline` | points | `model` | ★ **草图样条曲线**：`ISketchManager.CreateSpline2(data, False)` |
| `solidworks_sketch_start` | plane_name | `model` | Enter a new sketch on a reference plane. ★ This is the prerequisite for every sk |

## `sw_view`（24 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_collect_view_evidence` | — | `view` | ★ 官方签名（逐字，来自 sw_view.py）：`查不到 —— 「collect_view_evidence」本身**不是官方成员**（官方 IModelVi |
| `solidworks_get_active_view` | — | `model` | Get the currently active 3D view (the official member is IModelDoc.ActiveView). |
| `solidworks_get_view_model_doc` | — | `view` | ★ 官方签名（逐字，来自 sw_view.py）：`查不到 —— C:\swapi\types\IModelView\GetModelDoc.md 不存在（IM |
| `solidworks_view_activate` | — | `view` | ★ 官方签名（逐字，来自 Activate.md）：`void Activate()` |
| `solidworks_view_add_perspective` | — | `view` | ★ 官方签名（逐字，来自 AddPerspective.md）：``void AddPerspective()`` |
| `solidworks_view_get_camera` | — | `view` | ★ 官方签名（逐字，来自 Camera.md）：`Camera Camera {get; set;}` |
| `solidworks_view_get_display_mode` | — | `view` | ★ 官方签名（逐字，来自 DisplayMode.md）：`System.int DisplayMode {get; set;}` |
| `solidworks_view_get_frame` | — | `view` | ★ 官方签名（逐字，来自 FrameLeft.md）：`System.int FrameLeft {get; set;}` |
| `solidworks_view_get_next` | — | `view` | ★ 官方签名（逐字，来自 GetNext.md）：``System.object GetNext()`` |
| `solidworks_view_get_scale` | — | `view` | ★ 官方签名（逐字，来自 Scale.md）：`**Signature**: `System.double Scale {get; set;}`` |
| `solidworks_view_has_perspective` | — | `view` | ★ 官方签名（逐字，来自 HasPerspective.md）：``System.bool HasPerspective()`` |
| `solidworks_view_initialize_shading` | — | `view` | ★ 官方签名（逐字，来自 InitializeShading.md）：`void InitializeShading()` |
| `solidworks_view_redraw` | scope_or_none | `view` | ★ 官方签名（逐字，来自 GraphicsRedraw.md）：`void GraphicsRedraw( System.object Rect )` |
| `solidworks_view_remove_perspective` | — | `view` | ★ 官方签名（逐字，来自 RemovePerspective.md）：`void RemovePerspective()` |
| `solidworks_view_roll_view` | angle_deg | `view` | ★ 官方签名（逐字，来自 RollBy.md）：`void RollBy( System.double Angle )` |
| `solidworks_view_rotate_about_center` | x_angle_deg, y_angle_deg | `view` | ★ 官方签名（逐字，来自 RotateAboutCenter.md）：`**Signature**: `void RotateAboutCenter( Syst |
| `solidworks_view_set_camera_by_name` | name | `view` | ★ 官方签名（逐字，来自 SetCameraByName.md）：`System.bool SetCameraByName( System.string Nam |
| `solidworks_view_set_display_mode` | mode | `view` | ★ 官方签名（逐字，来自 DisplayMode.md）：`**Signature**: `System.int DisplayMode {get; set;} |
| `solidworks_view_set_frame` | left_px, top_px, width_px, height_px | `view` | ★ 官方签名（逐字，来自 FrameLeft.md）：`System.int FrameLeft {get; set;}` |
| `solidworks_view_set_scale` | scale | `view` | ★ 官方签名（逐字，来自 Scale.md）：`System.double Scale {get; set;}` |
| `solidworks_view_start_dynamics` | — | `view` | ★ 官方签名（逐字，来自 StartDynamics.md）：`void StartDynamics()` |
| `solidworks_view_stop_dynamics` | — | `view` | ★ 官方签名（逐字，来自 StopDynamics.md）：``void StopDynamics()`` |
| `solidworks_view_translate_view` | dx_mm, dy_mm | `view` | ★ 官方签名（逐字，来自 TranslateBy.md）：`**Signature**: `void TranslateBy( System.double X, |
| `solidworks_view_zoom_by_factor` | factor | `view` | ★ 官方签名（逐字，来自 ZoomByFactor.md）：`void ZoomByFactor( System.double Factor )` |

## `sw_simulation`（21 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_select_face_selector` | selection, mark, append | `model` | Select ONE face by a **declarative selector** and return a READ-BACK report. ★★  |
| `solidworks_simulation_apply_fixed_restraint` | study_name, selection | `study` | Apply a FIXED restraint (fixture) to the selected face(s) of a static study and  |
| `solidworks_simulation_apply_normal_force` | study_name, selection, magnitude_n | `study` | Apply a NORMAL force to the selected face(s) of a static study and return the IC |
| `solidworks_simulation_check_mesh_size` | element_size_mm, memory_budget_gb | `—` | Decide whether a global element size is sane for the ACTIVE part BEFORE meshing, |
| `solidworks_simulation_collect_evidence` | — | `sw_app` | Return a JSON-able summary of every study in the active document: per-study `nam |
| `solidworks_simulation_create_mesh` | study_name, units, element_size_mm, tolerance_mm | `study` | Mesh the study and return a READ-BACK report `{ok, return_code, return_is_trustw |
| `solidworks_simulation_create_mesh_safely` | study_name, units, element_size_mm, tolerance_mm, memory_budget_gb | `study` | **THE RECOMMENDED WAY to mesh a study.** One call does seven things, all measure |
| `solidworks_simulation_create_study` | study_name | `sw_app` | Create a STATIC simulation study and return a JSON-able report: `{ok, requested_ |
| `solidworks_simulation_create_study_by_type` | name, study_type, mesh_type | `sw_app` | ★ 官方签名（逐字，来自 sw_simulation.py）：`CWStudy CreateNewStudy3( String Name,` |
| `solidworks_simulation_default_element_size_and_tolerance` | study_name, units | `study` | Get the suggested element size and tolerance (millimetre-scale when units=-1). |
| `solidworks_simulation_default_solve_memory_budget_gb` | — | `—` | ★ 官方签名（逐字，来自 sw_simulation.py）：`查不到 —— 它不是 SolidWorks API 成员（源码 sw_simulation.py |
| `solidworks_simulation_ensure_addin` | — | `sw_app` | ★ 官方签名（逐字，来自 sw_simulation.py）：`查不到（repo_original —— ensure_simulation_addin 本身* |
| `solidworks_simulation_find_study` | study_name | `sw_app` | Look up a simulation study by name and return `{found, requested_name, study_nam |
| `solidworks_simulation_get_study_manager` | — | `sw_app` | ★ 官方签名（逐字，来自 sw_simulation.py）：`ICWModelDoc.get_StudyManager() → CWStudyManager（ |
| `solidworks_simulation_list_studies` | — | `sw_app` | List every simulation study in the active document as `[{index, name}, …]`. ★ Re |
| `solidworks_simulation_mesh_settings_report` | — | `study` | ★ 官方签名（逐字，来自 sw_simulation.py）：`查不到 —— C:\swapi\types\ 下**没有 ICWMesh\ 目录**（Test- |
| `solidworks_simulation_mesh_size` | study_name, units | `study` | Return the suggested mesh `{element_size, tolerance, units}` for a study. ★ The  |
| `solidworks_simulation_run_analysis` | study_name | `study` | Run the study and return a READ-BACK report `{ok, return_code, return_is_trustwo |
| `solidworks_simulation_set_material` | material_name, database | `model` | Assign a material to the active part and RETURN THE READ-BACK MaterialIdName. An |
| `solidworks_simulation_solve_memory_preflight` | element_count, node_count, memory_budget_gb, solver_name | `—` | ★ 官方签名（逐字，来自 sw_simulation.py）：`查不到（非 SolidWorks API 成员）` |
| `solidworks_simulation_solver_type` | study_name | `study` | Return `{ok, value, name, reason}` for `ICWStaticStudyOptions.SolverType` (`swsS |

## `sw_costing`（20 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_costing_assign_custom_cost` | amount, body_name | `cost_body` | 给**一个成本实体**指定自定义成本 |
| `solidworks_costing_body_count` | — | `cost_manager` | Return how many bodies Costing sees (★ cost is computed per body). ★ Read-only. |
| `solidworks_costing_default_template` | category | `cost_manager` | Return the default Costing template name for a category. ★ Read-only. |
| `solidworks_costing_defaults` | — | `cost_manager` | ★ 官方签名（逐字，来自 sw_costing.py）：`Object get_CostingDefaults()` |
| `solidworks_costing_evidence` | — | `cost_manager` | Return the Costing overview (body count + whether a cost analysis exists). ★ Rea |
| `solidworks_costing_include_body` | body_name, include | `cost_part` | 把某个实体纳入（或排除出）**成本计算** |
| `solidworks_costing_list_bodies` | — | `cost_manager` | Return the Costing body names (★ feed one to solidworks_costing_read_body). ★ Re |
| `solidworks_costing_list_templates` | category | `cost_manager` | Return the Costing template names available for a category. ★ Read-only. |
| `solidworks_costing_method_value` | method_name | `cost_manager` | Return the current value of one cost method. ★ Read-only. |
| `solidworks_costing_read_analysis` | — | `cost_manager` | Read every readable field of the part's cost analysis as a dict. ★ Use it to dis |
| `solidworks_costing_read_body` | body_name | `cost_manager` | Read one body's cost data. ★ An unknown body name fails with the list of valid n |
| `solidworks_costing_set_default_lot_size` | single_body, multibody | `defaults` | ★ 官方签名（逐字，来自 sw_costing.py）：`查不到（`C:\swapi\types\` 下**没有** ICostingDefaults 目录 — |
| `solidworks_costing_set_default_manufacturing_method` | category, method | `defaults` | ★ 官方签名（逐字，来自 sw_costing.py）：`查不到 —— C:\swapi\types\ICostingDefaults\ 目录不存在（该目录下按 |
| `solidworks_costing_set_default_material` | category, material_name | `defaults` | ★ 官方签名（逐字，来自 sw_costing.py）：`查不到 —— C:\swapi\types\ICostingDefaults\ 目录不存在（该目录下按 |
| `solidworks_costing_set_default_template` | category, template_name | `defaults` | ★ 官方签名（逐字，来自 sw_costing.py）：`查不到（C:\swapi\types\ICostingDefaults\SetTemplateName |
| `solidworks_costing_set_lot_size` | lot_size | `cost_analysis` | 设成本分析的**批量大小** |
| `solidworks_costing_set_markup` | markup_type, markup_percent | `cost_analysis` | 设成本分析的**加价**（类型 + 百分比） |
| `solidworks_costing_set_method` | method_name, method | `cost_part` | 设某个成本方法的取值 |
| `solidworks_costing_update_cost_for_all_bodies` | — | `cost_part` | 对**全部实体**重算成本 |
| `solidworks_get_costing_manager` | — | `model` | Get the SOLIDWORKS Costing manager object for the active document. |

## `sw_feature_readback`（16 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_base_flange_params` | feature_name | `model` | ★ **读钣金基体法兰特征的一组参数**（★ 厚度 / 折弯半径 / K 因子 / 释放槽 / 若干开关） |
| `solidworks_csys_params` | feature_name | `model` | ★ **读坐标系特征的一组参数**（★ 原点实体类型 / 三轴实体数 / 变换对象） |
| `solidworks_dome_params` | feature_name | `model` | ★ **读圆顶特征的一组参数**（★ 高度 / 是否椭圆 / 方向 / 面数） |
| `solidworks_extrude_depth` | feature_name, forward | `model` | ★ **读拉伸特征的深度**（★ 官方 `IExtrudeFeatureData2::GetDepth(bool Forward)`） |
| `solidworks_extrude_params` | feature_name | `model` | ★ **读拉伸特征的一组参数**（★ 端条件 / 拔模角 / 轮廓数 / 两向开关） |
| `solidworks_feature_info` | feature_name | `model` | ★ **读一个特征的一组通用属性**（★ 元数据 / 面数 / 可见性 / 子父特征） |
| `solidworks_feature_list_names` | limit | `model` | ★ 官方签名（逐字，来自 sw_feature_readback.py）：`查不到（本函数不是 API 成员，无签名可抄） |
| `solidworks_feature_present` | feature_name | `model` | ★ 官方签名（逐字，来自 sw_feature_readback.py）：`查不到（本函数不是 API 成员，无签名可抄） |
| `solidworks_feature_whats_wrong` | — | `model` | ★ 官方签名（逐字，来自 GetWhatsWrongCount.md）：`System.int GetWhatsWrongCount()` |
| `solidworks_fillet_params` | feature_name | `model` | ★ **读简单圆角特征的一组参数**（★ 默认半径 / 类型 / 边数 / 若干开关） |
| `solidworks_hole_params` | feature_name | `model` | ★ **读异型孔向导特征的一组参数**（★ 尺寸 / 标准 / 类型 / 端条件） |
| `solidworks_loft_params` | feature_name | `model` | ★ **读放样特征的一组参数**（★ 轮廓数 / 引导线 / 起止相切 / 拔模角 / 薄壁 / 闭合） |
| `solidworks_pattern_params` | feature_name | `model` | ★ **读线性阵列特征的一组参数**（★ 两向实例数/间距 + 若干开关 + 计数） |
| `solidworks_revolve_params` | feature_name | `model` | ★ **读旋转特征的一组参数**（★ 角度 / 轴类型 / 方向 / 薄壁 / 轮廓数） |
| `solidworks_shell_params` | feature_name | `model` | ★ **读抽壳特征的一组参数**（★ 厚度 / 方向 / 移除面数 / 多厚度面数与逐面厚度） |
| `solidworks_sweep_params` | feature_name | `model` | ★ **读扫描特征的一组参数**（★ 类型 / 薄壁 / 圆轮廓直径 / 壁厚 / 扭转角 / 引导线数） |

## `sw_simulation_loads`（16 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_simulation_apply_centrifugal_force` | study_name, selection | `manager` | Apply a CENTRIFUGAL FORCE to the selected entity of a static study and return a  |
| `solidworks_simulation_apply_convection` | study_name, selection | `manager` | Apply a **CONVECTION** load to the selected face(s) and return a READ-BACK repor |
| `solidworks_simulation_apply_distributed_mass` | study_name, selection, mass, units | `manager` | Add a **DISTRIBUTED MASS** to the selected face(s) and return a READ-BACK report |
| `solidworks_simulation_apply_elastic_connector` | study_name, selection | `manager` | Add an **ELASTIC CONNECTOR** between the selected face(s) and return a READ-BACK |
| `solidworks_simulation_apply_force` | study_name, selection, force_type | `manager` | Add a **FORCE / MOMENT** to the selected face(s) and return a READ-BACK report.  |
| `solidworks_simulation_apply_gravity` | study_name, selection | `manager` | Apply a GRAVITY load to the selected entity of a static study and return a READ- |
| `solidworks_simulation_apply_heat_flux` | study_name, selection | `manager` | Apply a **HEAT FLUX** load to the selected face(s) and return a READ-BACK report |
| `solidworks_simulation_apply_heat_power` | study_name, selection | `manager` | Apply a **HEAT POWER** load to the selected face(s) and return a READ-BACK repor |
| `solidworks_simulation_apply_link_connector` | study_name, first, second, first_body_index, second_body_index | `manager` | Add a **LINK CONNECTOR** between two **vertices** and return a READ-BACK report. |
| `solidworks_simulation_apply_pressure` | study_name, selection, pressure_type | `manager` | Apply a PRESSURE load to the selected face(s) of a static study and return a REA |
| `solidworks_simulation_apply_radiation` | study_name, selection, radiation_type | `manager` | Apply a **RADIATION** load to the selected face(s) and return a READ-BACK report |
| `solidworks_simulation_apply_remote_load` | study_name, selection, load_type, units, dx, dy, dz | `manager` | Add a **REMOTE LOAD** (location + direction + magnitude) to the selected face(s) |
| `solidworks_simulation_apply_rigid_connector` | study_name, source_indices, target_indices, kind, source_body_index, target_body_index | `manager` | Add a **RIGID CONNECTOR** between two bodies and return a READ-BACK report. ★★ * |
| `solidworks_simulation_apply_temperature` | study_name, selection | `manager` | Apply a **TEMPERATURE** load to the selected face(s) and return a READ-BACK repo |
| `solidworks_simulation_apply_torque` | study_name, selection | `manager` | Apply a TORQUE load (`AddForce` with swsForceTypeTorque) to the selected face(s) |
| `solidworks_simulation_get_edge_weld_connector` | index | `manager` | ★ 官方签名（逐字，来自 ICWLoadsAndRestraintsManager~GetEdgeWeldConnector.txt）：`Function Ge |

## `sw_topology`（16 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_topology_collect_numbers` | study_name | `study` | Read the topology study's numbers as a JSON-able dict: results presence, plot co |
| `solidworks_topology_create_demold_control` | study_name, direction | `study` | Create a de-mold (manufacturing) control for a topology study. The caller must f |
| `solidworks_topology_create_factor_of_safety_constraint` | study_name, specified_factor | `study` | Create a factor-of-safety constraint for a topology study (stress must stay belo |
| `solidworks_topology_create_mass_constraint` | study_name, reduce_percent | `study` | Create a mass constraint for a topology study (mass-reduction percent semantics) |
| `solidworks_topology_create_preserved_region` | study_name, option | `study` | Create a preserved region for a topology study (material that must not be remove |
| `solidworks_topology_create_stress_constraint` | study_name, value, comparator | `study` | Create a stress constraint for a topology study. |
| `solidworks_topology_create_study` | study_name, mesh_type, delete_existing | `sw_app` | Create a topology optimization study (analysis type 13) on the ACTIVE part. Topo |
| `solidworks_topology_create_symmetry_control` | study_name, symmetry_type | `study` | Create a symmetry control for a topology study. The caller must first select the |
| `solidworks_topology_create_thickness_control` | study_name, min_thickness_mm, max_thickness_mm | `study` | Create a thickness control for a topology study (minimum/maximum thickness). Uni |
| `solidworks_topology_evidence` | — | `sw_app` | Read back the topology studies on the active document: names, analysis types, an |
| `solidworks_topology_list_constraints` | study_name | `study` | Report which constraints and controls already exist on the topology study as BOO |
| `solidworks_topology_manager_report` | study_name | `study` | Return a JSON-able report about the topology study manager: whether it exists, i |
| `solidworks_topology_options_report` | study_name | `study` | Return a JSON-able report about the topology study options: whether the options  |
| `solidworks_topology_run` | study_name, units, element_size_mm, tolerance_mm | `study` | Mesh and solve the topology study and report whether results exist. A zero RunAn |
| `solidworks_topology_set_goal` | study_name, goal_type, mass_reduce_percent | `study` | Set the topology study goal and return a READ-BACK report comparing the number o |
| `solidworks_topology_set_iteration_options` | study_name | `study` | Set the topology iteration options and return a READ-BACK report comparing the r |

## `sw_review`（15 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_activate_model_for_preview` | — | `model` | Activate the model for preview/review (prepares the document for capture). ⚠ May |
| `solidworks_build_review_report` | output_dir, basename | `model` | Build structured review-report data (exports preview images and writes a report  |
| `solidworks_clear_selection_for_preview` | — | `model` | Clear the selection so the preview does not show highlighted entities. ⚠ May mar |
| `solidworks_collect_model_summary` | — | `model` | Summarise the model: title, type, feature tree (name + type), save path. |
| `solidworks_review_collect_geometry_measurements` | — | `model` | ★ 官方签名（逐字，来自 GetPartBox.md）：`**Signature**: `System.object GetPartBox( System.bo |
| `solidworks_review_drawing_layout` | structure, padding_m, preview_evidence | `—` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到（非 API 成员，无官方 **Signature**: 行；源码签名 `review_drawi |
| `solidworks_review_evaluate_report` | report | `—` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到` |
| `solidworks_review_export_previews` | output_dir, basename, views | `model` | ★ 官方签名（逐字，来自 SaveBMP.md）：`System.bool SaveBMP( System.string FileNameIn, System. |
| `solidworks_review_inspect_bmp` | path, sample_limit | `—` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到` |
| `solidworks_review_pdf_text_layout` | path, maximum_spans, minimum_overlap_area_pt2 | `—` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到 —— 本函数不是 SolidWorks API 成员，是本仓纯 Python 函数（第三方库 P |
| `solidworks_review_run` | output_dir, basename, views, expected_outputs | `model` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到` |
| `solidworks_review_write_report` | report, output_path | `—` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到` |
| `solidworks_review_write_summary` | report, output_path | `—` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到 —— write_markdown_summary 不是 SolidWorks API 成员：s |
| `solidworks_set_standard_view` | view_name | `model` | Switch the model to a named standard view (e.g. isometric, front, top). |
| `solidworks_view_zoom_to_fit` | — | `model` | ★ 官方签名（逐字，来自 sw_review.py）：`查不到` |

## `sw_assembly_doc`（12 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_assembly_auto_explode` | — | `doc` | Automatically generate an exploded view of the current configuration (official ` |
| `solidworks_assembly_create_exploded_view` | — | `doc` | Create an explode view of the active assembly configuration (official `System.bo |
| `solidworks_assembly_dissolve` | — | `doc` | ★ 官方签名（逐字，来自 DissolveSubAssembly.md）：`**Signature**: `System.bool DissolveSubAss |
| `solidworks_assembly_edit_explode_parameters` | — | `doc` | Call `IAssemblyDoc.EditExplodeParameters` (zero arguments). ⚠ The official page  |
| `solidworks_assembly_exit_edit_part_in_context` | — | `asm_model` | ★ 官方签名（逐字，来自 EditAssembly.md）：``void EditAssembly()`` |
| `solidworks_assembly_exploded_view_configuration` | arg | `doc` | Thin wrapper over `IAssemblyDoc.GetExplodedViewConfigurationName` (one argument) |
| `solidworks_assembly_external_reference_count` | — | `component` | ★ 官方签名（逐字，来自 ListExternalFileReferencesCount.md）：``System.int ListExternalFileRe |
| `solidworks_assembly_get_exploded_view_count` | configuration_name | `doc` | Return the number of exploded views in a configuration (official `System.int Get |
| `solidworks_assembly_get_exploded_view_names` | configuration_name | `doc` | Return the exploded-view NAMES of a configuration as a list of strings (official |
| `solidworks_assembly_show_exploded` | show_it, explode_view_name | `doc` | Display the named exploded view (official `System.bool ShowExploded2(Boolean Sho |
| `solidworks_assembly_view_collapse` | — | `doc` | Collapse the display back (official `void ViewCollapseAssembly()`, zero argument |
| `solidworks_assembly_view_explode` | — | `doc` | Explode the selected exploded view in the display (official `void ViewExplodeAss |

## `sw_weldment`（12 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_weldment_create_cut_list` | sort_options, collect_identical_bodies | `model` | Create the weldment cut list and return the cut-list folders as evidence. |
| `solidworks_weldment_create_profile_center_mate` | entities, mate_alignment, offset_distance_mm, flip_dimension | `model` | Create a profile-center mate between declaratively selected structural members. |
| `solidworks_weldment_create_structural_member` | sketch_name, profile_path | `model` | Create a **STRUCTURAL MEMBER** (weldment) along a path sketch with a weldment pr |
| `solidworks_weldment_create_sub_weld_folder` | — | `model` | Create a sub-weldment folder in the active weldment part. |
| `solidworks_weldment_create_weldment_profile` | sketch_ref, output_path, properties | `model` | Create a weldment profile from a declaratively selected sketch and write it to o |
| `solidworks_weldment_ensure_cut_list` | — | `model` | Create the cut list if it is missing, and return the cut-list folders. |
| `solidworks_weldment_evidence` | create_missing_cut_list, update_cut_list_too | `model` | Read back the weldment state: structural members, cut-list folders, and their qu |
| `solidworks_weldment_export_cut_list_csv` | evidence, output_path | `—` | Write a cut-list evidence dict to CSV and return the path. ★ The criterion is th |
| `solidworks_weldment_iter_features` | — | `model` | ★ 官方签名（逐字，来自 sw_weldment.py）：`查不到（本函数不是 API 成员，无官方签名可抄） |
| `solidworks_weldment_read_property_manager` | core_only | `manager` | Read the active PropertyManager page's controls as a JSON-able dict. ★ Read-only |
| `solidworks_weldment_set_cut_list_properties` | properties | `model` | Set cut-list properties and return the read-back list. ⚠ Does NOT save the docum |
| `solidworks_weldment_update_cut_list` | — | `model` | Refresh the cut list and return the updated folders. |

## `sw_drawing_query`（11 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_drawing_current_sheet_info` | — | `model` | Return info about the sheet currently being edited as a dict. ★ Read-only. |
| `solidworks_drawing_current_sheet_name` | — | `model` | Return the name of the sheet currently being edited. ★ Read-only. |
| `solidworks_drawing_get_current_sheet` | — | `model` | Read the current sheet: paper size (name + code), WIDTH/HEIGHT IN MILLIMETRES, s |
| `solidworks_drawing_list_sheets` | — | `model` | Sheet overview of the active drawing: how many sheets, their names, and which on |
| `solidworks_drawing_list_views` | — | `model` | List the views on the CURRENT SHEET: name + type code. ⚠ The sheet itself is NOT |
| `solidworks_drawing_set_sheet_scale` | numerator, denominator, scale_anno_position, scale_anno_text_height, sheet_name | `model` | ★ **设工程图图纸的比例并回读** —— 走 `ISheet.SetScale(numerator, denominator, scale_anno_posi |
| `solidworks_drawing_sheet_count` | — | `model` | Return the number of sheets in the active drawing. ★ Read-only. |
| `solidworks_drawing_sheet_names` | — | `model` | Return the drawing's sheet names as a list. ★ Read-only. |
| `solidworks_drawing_sheet_scale` | sheet_name | `model` | ★ **读工程图图纸的比例** —— 走官方 Remarks 指定的 `ISheet.GetProperties`，取其中两个数作为比例的分子/分母 ⇒ 回 ` |
| `solidworks_drawing_sheets_summary` | — | `model` | Return a per-sheet summary dict for the active drawing (★ 页名 / 视图数 等). ★ Read-on |
| `solidworks_drawing_view_annotations` | — | `model` | ★ **读当前图纸**每个视图上的注释 / 显示尺寸 / 弧数****（★ **工程图读侧第一批**）✓★★★★★★ **为什么做它**：★ 本仓有 `add_ |

## `sw_hole_features`（10 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_fastener_table_types` | standard_name, fastener_id, hole_type_id | `sw` | List the fastener table type ids for one fastener (official IHoleStandardsData.G |
| `solidworks_fastener_types` | standard_name, hole_type_id | `sw` | List the fastener types under a Hole Wizard standard. Returns [{id, name}, ...]. |
| `solidworks_hole_blind_by_selection` | selection, diameter_mm, depth_mm, plane_name, name | `model` | Create a blind circular hole at a declaratively selected point (★ rule 3). Retur |
| `solidworks_hole_counterbore_by_selection` | selection, hole_diameter_mm, counterbore_diameter_mm, counterbore_depth_mm, plane_name, name | `model` | Create a counterbore hole at a declaratively selected point (★ rule 3). |
| `solidworks_hole_countersink_by_selection` | selection, hole_diameter_mm, countersink_diameter_mm, included_angle_deg, plane_name, name | `model` | Create a countersink hole at a declaratively selected point (★ rule 3). |
| `solidworks_hole_pattern` | positions, kind, diameter_mm, depth_mm, plane_name, name | `model` | ★ **按显式孔位一次创建一组孔**（★ 官方走 `HoleWizard5` 那族） |
| `solidworks_hole_standards` | hole_type_id | `sw` | List the Hole Wizard standards available for a hole type (official ISldWorks.Get |
| `solidworks_hole_through_by_selection` | selection, diameter_mm, plane_name, name | `model` | Create a fully-through circular hole whose position comes from a declarative sel |
| `solidworks_hole_wizard` | selection, size | `model` | ★ **孔向导 / 异型孔**：`IFeatureManager.HoleWizard5`（★ 官方 24+ 参，本工具已把前置配好） |
| `solidworks_slot_semicircular_by_selection` | start_selection, end_selection, width_mm, depth_mm, plane_name, name | `model` | Create a semicircular-end slot spanning two declaratively selected points (★ rul |

## `sw_assembly`（9 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_assembly_add_mate_checked` | mate_type, align, flip, distance_mm, distance_upper_mm, distance_lower_mm, gear_num, gear_den, angle_deg, angle_upper_deg, angle_lower_deg, for_positioning_only, lock_rotation_deg, width_mate_option_mm, name, clear_selection | `asm_model` | ★ 官方签名（逐字，来自 AddMate5.md）：`**Signature**: `Mate2 AddMate5( System.int MateTypeFr |
| `solidworks_assembly_add_parallel_mate` | face1_name, face2_name | `asm_model` | ★ 官方签名（逐字，来自 sw_assembly.py）：`def add_mate_parallel(asm_model, face1_name, face2 |
| `solidworks_assembly_apply_component_transform_x` | tx_mm, ty_mm, tz_mm, angle_deg | `component` | ★ 官方签名（逐字，来自 sw_assembly.py）：`查不到 —— 本函数**不是 SolidWorks API 成员**（它没有同名官方页，故无签名可抄 |
| `solidworks_assembly_check_interference` | — | `asm_model` | Run interference detection on the ACTIVE assembly and return an auditable report |
| `solidworks_assembly_list_components` | top_level_only | `asm_model` | List the components of the ACTIVE assembly: for each one its name, file path, wh |
| `solidworks_assembly_list_mates` | — | `model` | List the MateGroup and mate features of the active assembly (name, type, tree de |
| `solidworks_assembly_replace_component` | old_component_name, new_part_path | `asm_model` | ★ 官方签名（逐字，来自 ReplaceComponents2.md）：`System.bool ReplaceComponents2( System.stri |
| `solidworks_assembly_suppress_component` | component_name | `asm_model` | ★ 官方签名（逐字，来自 EditSuppress2.md）：``System.bool EditSuppress2()`` |
| `solidworks_assembly_unsuppress_component` | component_name | `asm_model` | ★ 官方签名（逐字，来自 EditUnsuppress2.md）：`System.bool EditUnsuppress2()` |

## `sw_drawing_expose`（9 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_drawing_add_note` | x_mm, y_mm, text | `drawing_model` | ★ **注释/文字**：`InsertNote` |
| `solidworks_drawing_create_detail_view` | x_mm, y_mm, scale, label, shape_intensity | `drawing_model` | ★ **局部视图**：`CreateDetailViewAt4`（官方 **12 参**） |
| `solidworks_drawing_create_hole_table` | view_name, x_mm, y_mm, anchor_type, start_value, template, tag_order, tag_type | `drawing_model` | ★ **孔表**：**`IView.InsertHoleTable3`（9 参、未废弃）** |
| `solidworks_drawing_create_projected_view` | part_path, view_name, x_mm, y_mm, scale | `drawing_model` | ★ **投影/模型视图**：`CreateDrawViewFromModelView3`（经 `add_view`） |
| `solidworks_drawing_create_revision_table` | x_mm, y_mm, anchor_type, template, shape, auto_update_zoom_cells | `drawing_model` | ★ **修订表**：**`ISheet.InsertRevisionTable2`（7 参、未废弃）** |
| `solidworks_drawing_create_section_view` | x_mm, y_mm | `drawing_model` | ★ **剖面视图**：`CreateSectionViewAt5` |
| `solidworks_drawing_create_three_standard_views` | part_path, projection | `drawing_model` | ★ 官方签名（逐字，来自 Create1stAngleViews2.md）：`System.bool Create1stAngleViews2( System. |
| `solidworks_drawing_insert_center_marks` | requirements | `drawing_model` | ★ **中心符号线**（批量）：`AutoInsertCenterMarks2` |
| `solidworks_drawing_set_sheet_format` | format_path | `drawing_model` | ★ **图纸格式/模板**：**`ISheet.SetTemplateName(String NameIn)`**（官方 **`void`、未废弃**） |

## `sw_selection`（9 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_selection_clear_colors` | — | `selection` | ★ 官方签名（逐字，来自 ClearSelectionColors.md）：`void ClearSelectionColors()` |
| `solidworks_selection_collect_evidence` | — | `selection` | ★ 官方签名（逐字，来自 sw_selection.py）：`查不到（本函数不是 SolidWorks API 成员，无签名可抄） |
| `solidworks_selection_deselect` | item, mark | `selection` | ★ 官方签名（逐字，来自 DeSelect2.md）：`System.int DeSelect2( System.object AtIndex, System. |
| `solidworks_selection_enable` | enabled | `selection` | ★ 官方签名（逐字，来自 EnableSelection.md）：`System.bool EnableSelection {get; set;}` |
| `solidworks_selection_enable_contour` | enabled | `selection` | ★ 官方签名（逐字，来自 EnableContourSelection.md）：`System.bool EnableContourSelection {get |
| `solidworks_selection_is_coord_sys_element_selected` | index, mark | `selection` | ★ 官方签名（逐字，来自 IsCoordSysElementSelected.md）：`System.bool IsCoordSysElementSelecte |
| `solidworks_selection_is_in_edit_target` | index, mark | `selection` | ★ 官方签名（逐字，来自 IsInEditTarget2.md）：`System.bool IsInEditTarget2( System.int Index, |
| `solidworks_selection_set_object_mark` | index, mark, action | `selection` | ★ 官方签名（逐字，来自 SetSelectedObjectMark.md）：`System.bool SetSelectedObjectMark( Syste |
| `solidworks_selection_suspend_list` | — | `selection` | ★ 官方签名（逐字，来自 SuspendSelectionList.md）：`System.int SuspendSelectionList()` |

## `sw_selection_spec`（9 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_clear_selection` | — | `model` | Clear the current selection set. |
| `solidworks_current_selection` | mark | `model` | Read the current selection set (optionally filtered to one selection mark). |
| `solidworks_entities_on_body` | kind, body_index | `model` | List the entities of one body (kind EDGE, FACE, or VERTEX). ⚠ Index order is NOT |
| `solidworks_resolve_entity` | selector, kind, body_index | `model` | ★ **解析声明式选择器并回报结果**（★ 只回 JSON —— 把 COM 对象挡在里面） |
| `solidworks_resolve_selection` | selector, kind, body_index | `model` | ★ **把声明式选择器解析并选中**，只回报**回读到的选区计数** |
| `solidworks_select_by_selector` | selector, kind, body_index, append | `model` | ★ **用声明式选择器选中一个实体** —— ★ MCP 可用的形态（★ 只回 JSON，**不回 COM 对象**） |
| `solidworks_select_entity_by_index` | kind, index, body_index, append | `model` | ★ **按序号选中体上的一个实体**（`kind` = `EDGE` / `FACE` / `VERTEX`，`index` 从 0 起） |
| `solidworks_selection_count` | — | `model` | ★ **回读当前选区计数**（`ISelectionMgr.GetSelectedObjectCount2(-1)`） |
| `solidworks_selection_point` | — | `model` | ★ **读当前选区那个点的坐标**（★ **毫米**，规则 2） |

## `sw_sketch_primitives`（9 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_add_3point_arc` | start_x_mm, start_y_mm, end_x_mm, end_y_mm, through_x_mm, through_y_mm | `model` | Draw a 3-point arc (start / end / a point on the arc).  ★ 草图图元按官方文档属**规则 3 的书面例外 |
| `solidworks_sketch_add_3point_center_rectangle` | center_x_mm, center_y_mm, x2_mm, y2_mm, x3_mm, y3_mm | `model` | Draw a 3-point CENTER rectangle (first point is the centre).  ★ 草图图元按官方文档属**规则 3 |
| `solidworks_sketch_add_3point_rectangle` | x1_mm, y1_mm, x2_mm, y2_mm, x3_mm, y3_mm | `model` | Draw a 3-point corner rectangle at any angle.  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选 |
| `solidworks_sketch_add_conic` | focus_x_mm, focus_y_mm, apex_x_mm, apex_y_mm, start_x_mm, start_y_mm, end_x_mm, end_y_mm | `model` | Draw a conic curve. ⚠ Official signature is IDENTICAL in shape to CreateParabola |
| `solidworks_sketch_add_parabola` | focus_x_mm, focus_y_mm, apex_x_mm, apex_y_mm, start_x_mm, start_y_mm, end_x_mm, end_y_mm | `model` | Draw a parabola (focus + apex + two endpoints).  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有 |
| `solidworks_sketch_add_parallelogram` | x1_mm, y1_mm, x2_mm, y2_mm, x3_mm, y3_mm | `model` | Draw a parallelogram (a corner plus the two adjacent edge endpoints).  ★ 草图图元按官方 |
| `solidworks_sketch_add_partial_ellipse` | center_x_mm, center_y_mm, major_x_mm, major_y_mm, minor_x_mm, minor_y_mm, start_x_mm, start_y_mm, end_x_mm, end_y_mm, direction | `model` | Draw a PARTIAL ellipse (elliptical arc).  ★ 草图图元按官方文档属**规则 3 的书面例外**（图元没有可选的具名实体 |
| `solidworks_sketch_add_perimeter_circle` | x1_mm, y1_mm, x2_mm, y2_mm, x3_mm, y3_mm | `model` | Draw a 3-point PERIMETER circle. ⚠ Official signature has NO Z argument (6 doubl |
| `solidworks_sketch_add_tangent_arc` | end_x_mm, end_y_mm, through_x_mm, through_y_mm, arc_type | `model` | Draw an arc TANGENT to the last sketch segment. ⚠ The sketch must already contai |

## `sw_motion`（8 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_motion_calculate_and_play` | play, motion_study_name | `motion_study` | 两步：`IMotionStudy::Calculate()` 再（可选）`IMotionStudy::Play()` |
| `solidworks_motion_collect_summary` | — | `asm_model` | Return a JSON-able summary of the assembly's motion studies. ★ Read-only. |
| `solidworks_motion_create_study` | name, duration, study_type | `asm_model` | Create a Motion Study on the active assembly and return it. ★ Needs an ASSEMBLY  |
| `solidworks_motion_ensure_type_library` | raise_on_error | `—` | Check (and load) the Motion type library. ★ Zero-argument apart from the flag —  |
| `solidworks_motion_export_avi` | file_path, motion_study_name | `motion_study` | 把运动算例导出成 **AVI** —— ★★ **AVI 导出是本仓三个「业界空白域护城河」之一** ✓ ★ 官方签名逐字：`C:\swapi\types\IM |
| `solidworks_motion_study_manager` | load_type_library | `asm_model` | Return the assembly's motion study manager (★ the entry point for the rest). ★ R |
| `solidworks_motion_validate_studies` | study_name, expected_study_type, minimum_duration_seconds, minimum_motor_count, require_results | `asm_model` | Validate the motion studies against the given requirements and return the result |
| `solidworks_motion_validate_summary` | summary, study_name, expected_study_type, minimum_duration_seconds, minimum_motor_count, require_results | `—` | Validate a motion-study summary dict (★ pure data — no SolidWorks call). ★ Usefu |

## `sw_simulation_study_options`（8 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_list_simulation_study_options` | — | `—` | List the simulation study option setters available (no document needed). |
| `solidworks_simulation_configure_buckling_solver` | family, modes, positive_only | `study` | Configure the buckling solver options of the injected study. ⚠ Only the non-None |
| `solidworks_simulation_configure_frequency_solver` | family, decouple, reference_pressure | `study` | Configure the frequency solver options of the injected study. ⚠ Only the non-Non |
| `solidworks_simulation_configure_static_solver` | family, free_body_force, contact_penalty, reference_pressure | `study` | Configure the static solver options of the injected study and return a report. ⚠ |
| `solidworks_simulation_list_setter_summary` | — | `—` | Return the catalogue of simulation study-option setters (family / name / type) a |
| `solidworks_simulation_set_registered_study_option` | family, name, value | `options` | ★ 官方签名（逐字，来自 sw_simulation_study_options.py）：`查不到 —— 本函数不是 SolidWorks API 成员（官方  |
| `solidworks_simulation_set_study_option` | family, name, value | `study` | Set one study option by its registered family/name and return a report. ★★ **未知的 |
| `solidworks_simulation_set_study_options` | family, values | `study` | Set several study options and return the read-back dict. ★★ **未知的 family/name 会返 |

## `sw_export`（7 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_export_bmp` | output_path, pixel_width, pixel_height | `model` | Export a BMP image of the active document and return a READ-BACK report (file ex |
| `solidworks_export_dxf` | output_path | `model` | Export to DXF and return a READ-BACK report (file exists and is non-empty). ⚠⚠ T |
| `solidworks_export_iges` | output_path | `model` | Export to IGES and return a READ-BACK report (file exists and is non-empty). |
| `solidworks_export_image` | output_path | `model` | ★ **把当前视图存成图片**（PNG / JPG，走官方 `IModelDocExtension.SaveAs3`） |
| `solidworks_export_parasolid` | output_path | `model` | Export to Parasolid and return a READ-BACK report (file exists and is non-empty) |
| `solidworks_export_step` | output_path | `model` | Export the active document to STEP and return a READ-BACK report: the file must  |
| `solidworks_export_stl` | output_path, quality | `model` | Export to STL and return a READ-BACK report (file exists and is non-empty). ★ Th |

## `sw_macro_guard`（7 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_macro_build_prompt` | user_request, model_name, strict | `—` | Build the prompt that asks a model to write SolidWorks VBA for `user_request`. ★ |
| `solidworks_macro_extract_vba_code` | text | `—` | Pull the VBA code out of a model's reply (official-free helper: pure text). ★ Re |
| `solidworks_macro_fallback_template` | user_request | `—` | Return the local fallback VBA template for `user_request` — used when generation |
| `solidworks_macro_normalize_model_family` | model_name | `—` | Map a concrete model name onto one of the prompt families this repo uses (gpt /  |
| `solidworks_macro_select_template` | user_request | `—` | Choose the local VBA template key whose keywords match `user_request`. ★ Pure fu |
| `solidworks_macro_validate_vba_code` | code | `—` | Check a VBA macro against the minimum this repo requires before it may be handed |
| `solidworks_macro_write_file` | code, output_path | `—` | Write VBA source to a file so a human or an agent can load it into SolidWorks. ★ |

## `sw_mold`（7 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_mold_core_cavity_split` | scale, thickness, flip, offset | `model` | Split the mold into core and cavity solids (this is the tooling split). ⚠ 0.0 me |
| `solidworks_mold_draft_analysis` | draft_angle_deg, analysis_type, option | `model` | Run mold draft analysis. Returns the official return code as-is: that code has N |
| `solidworks_mold_evidence` | — | `model` | ★ **当前这条在真机上**读不到东西**、★ 如实说明** —— 处置 `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #9`）：★  |
| `solidworks_mold_parting_line` | draft_analysis | `model` | Insert a mold parting line. Select the draft-direction reference first (edge/pla |
| `solidworks_mold_parting_surface` | surface_type, flip, use_trim, distance, angle, option, tolerance, alternate | `model` | Insert the mold parting surface. |
| `solidworks_mold_shut_off_surface` | — | `model` | Auto-create shut-off surfaces over holes for mold separation. Zero parameters. |
| `solidworks_mold_undercut_detect` | col_undercut, col_base, b_coord_input, dx, dy, dz | `model` | Detect mold undercuts along a direction. ⚠ The underlying IFeatureManager.MoldUn |

## `sw_sheet_metal`（7 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sheet_metal_create_base_flange` | sketch_name, thickness_mm, bend_radius_mm, depth_mm, k_factor, relief_ratio, reverse_direction, reverse_thickness | `model` | Create a native base flange (swFmBaseFlange) from an open or closed sketch. Retu |
| `solidworks_sheet_metal_create_draft` | selection, angle_deg, depth_mm, reverse_direction | `model` | Create a native draft on a SELECTED face. NOTE: the implementation's own `face_r |
| `solidworks_sheet_metal_create_edge_flange` | selection, bend_radius_mm, flange_length_mm, angle_deg, use_default_radius, reverse_direction | `model` | Create a native edge flange on a SELECTED edge. The edge is selected for you fro |
| `solidworks_sheet_metal_create_gusset` | selection, thickness_mm, profile_distance_1_mm, profile_distance_2_mm, profile_angle_deg | `model` | Create a native sheet-metal gusset on a SELECTED supporting face. The face is se |
| `solidworks_sheet_metal_create_one_bend` | sketch_name, bend_radius_mm, angle_deg, reverse_direction, use_default_radius | `model` | Create a single sheet-metal bend on the selected sketch. ⚠ **仍不可用，但原因已具体化**（2026 |
| `solidworks_sheet_metal_create_swept_flange` | path_selection, profile_selection, start_offset_mm, end_offset_mm, thickness_mm, bend_radius_mm, use_default_radius, flange_position, flatten_along_path, trim_side_bends, use_default_bend_relief, use_gauge_table, use_material_parameters, override_default_sheet_metal_parameters, reverse_direction | `model` | Create a native swept flange along a path. REQUIRES an existing base flange firs |
| `solidworks_sheet_metal_evidence` | — | `model` | Read back the sheet-metal state of the active part: thickness, bend radius, bend |

## `sw_sketch_edit_ops`（7 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_circular_pattern` | selection, arc_radius_mm, arc_angle_deg, pattern_num, pattern_spacing_deg, pattern_rotate, delete_instances | `model` | Create a CIRCULAR sketch pattern of the selected entities (official 9-arg call). |
| `solidworks_sketch_extend` | selection, x_mm, y_mm | `model` | Extend the selected sketch entity to the nearest entity. |
| `solidworks_sketch_fillet` | selection, radius_mm, constrained_corners | `model` | Create a SKETCH fillet on two selected, intersecting sketch segments. |
| `solidworks_sketch_linear_pattern` | selection, x_count, y_count, spacing_x_mm, spacing_y_mm, angle_x_deg, angle_y_deg, delete_instances | `model` | Create a LINEAR sketch pattern of the selected entities (official 12-arg call). |
| `solidworks_sketch_offset` | selection, offset_mm, both_directions, chain, cap_ends, make_construction, add_dimensions | `model` | Offset the selected sketch entities (official swSkOffsetCapEndType_e / swSkOffse |
| `solidworks_sketch_select_segment` | index, append | `model` | ★ 官方签名（逐字，来自 sw_sketch_edit_ops.py）：`查不到（本函数无同名官方成员 —— 官方 ISketchManager/ISketch |
| `solidworks_sketch_trim` | selection, option, x_mm, y_mm | `model` | Trim the selected sketch entities. ⚠ How many segments must be selected DEPENDS  |

## `sw_automation_knowledge`（6 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_automation_enter_command_lock` | — | `sldworks` | Set `ISldWorks.CommandInProgress = True` to stop the operations that pop modal d |
| `solidworks_automation_exit_command_lock` | — | `sldworks` | Release the lock set by `solidworks_automation_enter_command_lock`. ⚠ The wrappe |
| `solidworks_automation_explain_hresult` | code | `—` | Turn an HRESULT into plain words using THIS REPO's table. ★★ Its own docstring s |
| `solidworks_automation_get_flag` | pref | `sldworks` | Read a preference switch back from `ISldWorks`. ★ The wrapped function notes the |
| `solidworks_automation_is_command_locked` | — | `sldworks` | Read whether `CommandInProgress` is currently set. ★ The wrapped function notes  |
| `solidworks_automation_set_flag` | pref, value | `sldworks` | Set a preference switch on `ISldWorks`. ★ Use it to mute the dialogs a given ope |

## `sw_document_data`（6 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_config_activate` | configuration_name, rebuild | `model` | Activate a configuration and verify it by read-back. ⚠ Does NOT save the documen |
| `solidworks_config_create` | configuration_name, comment, alternate_name, activate, rebuild | `model` | Create a configuration, optionally activate and rebuild, then read the result ba |
| `solidworks_config_inspect` | — | `model` | List the document's configurations and the active one as a JSON-able dict. ★ Rea |
| `solidworks_config_read_custom_property` | name, configuration_name | `model` | Read one custom property as a JSON-able dict. ★ Read-only. |
| `solidworks_config_set_custom_properties` | properties, configuration_name | `model` | Set several custom properties and return the read-back list. ⚠ Does NOT save the |
| `solidworks_config_update_dimension` | dimension_name, value_mm, configuration_mode, configuration_names, rebuild | `model` | Update an exact named dimension and return a read-back report (before/after). ⚠  |

## `sw_ref_geometry`（6 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_insert_center_of_mass` | — | `model` | ★ 质心：`IFeatureManager.InsertCenterOfMass()`（**零参数**，回 `Feature`） |
| `solidworks_insert_coordinate_system` | x_flipped, y_flipped, z_flipped | `model` | ★ 坐标系：`IFeatureManager.InsertCoordinateSystem(…)`（3 参，回 `Feature`） |
| `solidworks_insert_global_bounding_box` | bbox_type, lwta_direction_type, include_hidden_bodies, include_surface_bodies | `model` | ★ 边界框：`IFeatureManager.InsertGlobalBoundingBox2(…)`（5 参，回 `IFeature`） |
| `solidworks_insert_ref_plane` | first_constraint, first_angle_or_dist, second_constraint, second_angle_or_dist, third_constraint, third_angle_or_dist | `model` | ★ 基准面：`IFeatureManager.InsertRefPlane`（6 参，回 [[Reference plane]]） |
| `solidworks_insert_reference_point` | ref_point_type, along_curve_type, distance_or_percent, number_of_ref_points | `model` | ★ 点：`IFeatureManager.InsertReferencePoint`（4 参，回 [[IFeature]]） |
| `solidworks_ref_geometry_create_3d_bounding_box` | — | `model` | ★ 官方签名（逐字，来自 Create3DBoundingBox.md）：`**Signature**: `void Create3DBoundingBox() |

## `sw_simulation_results`（6 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_simulation_activate_plot` | plot_name | `results` | ★ 官方签名（逐字，来自 CosmosWorksLib~CWResults~ActivatePlot.html）：`Public Function Activa |
| `solidworks_simulation_collect_mesh_evidence` | — | `mesh` | ★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到 —— 本函数不是 SolidWorks API 成员（官方 API 参考 |
| `solidworks_simulation_delete_plot` | plot_name | `results` | ★ 官方签名（逐字，来自 CosmosWorksLib~CWResults~DeletePlot.html）：`Public Function DeletePl |
| `solidworks_simulation_get_buckling_load_factors` | — | `results` | ★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在 —— `C:\swapi\types\` 无 `ICWRe |
| `solidworks_simulation_get_worst_jacobian_ratio` | — | `mesh` | ★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在）—— ★ `C:\swapi\types\` 下**没有  |
| `solidworks_simulation_is_component_failed` | component_name | `mesh` | ★ 官方签名（逐字，来自 sw_simulation_results.py）：`查不到（官方页不存在）—— ★ `C:\swapi\types\` 下**没有  |

## `sw_gui_modal`（5 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_gui_assert_no_modal` | main_hwnd, where | `—` | ★ **每个动作之前调用**：发现弹窗就**抛**，不让它吃掉后续输入 ✓ ★★ 本仓的死因里，「弹窗把 COM 调用冻住」是头号 ⇒ ★ 这条断言就是那个前置 |
| `solidworks_gui_close_modals` | main_hwnd, rounds | `—` | 关掉所有模态框并**回读**，返回关掉几个 ✓ ★★ 本仓的两段式处置：先 `PostMessage`（快）⇒ **验窗口是否真消失** ⇒ 没消失才上**真实 |
| `solidworks_gui_find_modals` | main_hwnd | `—` | 找出**同进程、与主窗口分离的可见顶层对话框**（★ 判据：Win32 类 `#32770` **或** 有 Button **或** 有可读文本 —— ★ 本 |
| `solidworks_gui_modal_report` | main_hwnd | `—` | 把当前弹窗状况打成一份**可判的报告**（★ 给「要不要点 / 能不能继续」提供判据）✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_mod |
| `solidworks_gui_screen_png` | path | `—` | ★ 官方签名（逐字，来自 sw_gui_modal.py）：`查不到 —— 本函数是本仓自研的 PIL 整屏截图助手，**不对应任何 SolidWorks 官方 |

## `sw_sheet_metal_weld_entry`（5 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sheet_metal_insert_closed_corner` | — | `model` | ★ **钣金闭合角**：`IModelDoc2.InsertSheetMetalClosedCorner()` → **`void`**（★ **零参**） |
| `solidworks_sheet_metal_insert_miter_flange` | use_default_radius, global_radius_mm, rip_gap_mm, use_default_relief, use_relief_ratio, relief_ratio, relief_width_mm, relief_depth_mm, relief_type, trim_side_bends, flange_pos, offset_dist1_mm, offset_dist2_mm | `model` | ★ **钣金斜接法兰**：`IFeatureManager.InsertSheetMetalMiterFlange(14 参)` → `Feature` |
| `solidworks_surface_midsurface_create` | body_index, placement, knit | `model` | ★ **曲面中面**：`IFeatureManager.InsertMidSurface(4 参)` → `System.object` |
| `solidworks_weldment_gusset_create` | depth_mm, dir_type, loc_type, is_profile, profile_d1_mm, profile_d2_mm, profile_d3_mm, profile_angle_deg, profile_d4_mm, offset_reference_plane, d_profile_offset_mm, crv_index, reverse_dir, reverse_face, use_len_dim, profile_d5_mm, profile_d6_mm, profile_chamfer_angle_deg, use_len_dim_for_chamfer, need_chamfer_in_gusset | `model` | ★ **焊件角撑板**：`IFeatureManager.InsertGussetFeature3(20 参)` → `IFeature` |
| `solidworks_weldment_insert_end_cap` | depth_mm, is_given_offset, is_chamfer, offset_value_mm, wall_ratio, chamfer_value_mm, is_corner_treatment, depth_offset_mm, is_reverse, is_end_cap_inward | `model` | ★ **焊件顶端盖**：`IFeatureManager.InsertEndCapFeature3(10 参)` → `IFeature` |

## `sw_sketch_modify_ops`（5 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_flip_entities` | axis_flag | `model` | ★ 镜像/翻转：`IModelDoc2.SketchModifyFlip(AxisFlag)` |
| `solidworks_sketch_move_entities` | start_x_mm, start_y_mm, end_x_mm, end_y_mm | `model` | ★ 移动实体：`IModelDoc2.SketchModifyTranslate`（★ 改的是**草图坐标系**） |
| `solidworks_sketch_rotate_entities` | center_x_mm, center_y_mm, angle_deg | `model` | ★ 旋转实体：`IModelDoc2.SketchModifyRotate`（★ 改的是**草图坐标系**） |
| `solidworks_sketch_scale_entities` | factor | `model` | ★ 缩放实体比例：`IModelDoc2.SketchModifyScale` —— ★ **本批唯一有 bool 返回值**的成员 |
| `solidworks_sketch_stretch_entities` | base_x_mm, base_y_mm, dest_x_mm, dest_y_mm, keep_relations | `model` | ★ 伸展实体：**`IModelDocExtension.Stretch`**（★ 入口在 **Extension** 上，不是 `IModelDoc2`） |

## `sw_surface_edit_ops`（5 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_insert_delete_face` | option | `model` | ★ 删除面：**`IModelDocExtension.InsertDeleteFace(Option)`**（回 `bool`） |
| `solidworks_insert_offset_surface` | thickness_mm, reverse | `model` | ★ 等距曲面：`IModelDoc2.InsertOffsetSurface(Thickness, Reverse)`（回 `void`） |
| `solidworks_insert_planar_surface` | — | `model` | ★ 平面区域：`IModelDoc2.InsertPlanarRefSurface()`（**零参数**，回 `bool`） |
| `solidworks_insert_replace_face` | — | `model` | ★ 替换面：`IModelDoc2.InsertFeatureReplaceFace()`（**零参数**，回 `void`） |
| `solidworks_insert_ruled_surface` | ruled_type, length_mm, flip_pull_dir, flip_dir, trim_and_sew, angle_deg, coord_input, x_mm, y_mm, z_mm, b_connect_surface | `model` | ★ 直纹曲面：`IFeatureManager.InsertRuledSurfaceFromEdge2(…)`（**11 参**，回 `Feature`） |

## `sw_surface_features`（5 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_surface_create_extruded` | depth_mm, sketch_name, through_all | `model` | ★ **用已有草图建「曲面-拉伸」特征** —— 走 `IFeatureManager.FeatureExtruRefSurface3`（官方 **22 个参数 |
| `solidworks_surface_cut` | flip, keep_piece_index, use_feat_scope, use_auto_select | `model` | ★ 官方签名（逐字，来自 InsertCutSurface.md）：``Feature InsertCutSurface( System.bool Flip,  |
| `solidworks_surface_extend` | distance_mm, extend_linear, end_condition | `model` | ★ **延伸曲面** —— 走 `IModelDoc2.InsertExtendSurface`（官方 **3 参** · ★★ **返回 `void`**） |
| `solidworks_surface_fill` | resolutions, options, selection | `model` | ★ **填充曲面** —— 走 `IFeatureManager.InsertFillSurface2`（官方 **6 参**） |
| `solidworks_surface_knit` | knit_tolerance_mm, try_to_form_solid | `model` | ★ **把曲面缝成一张** —— 走 `IFeatureManager.InsertSewRefSurface`（官方 **5 参**） |

## `sw_busy`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_session_busy_status` | — | `—` | Report whether SolidWorks is busy, with the evidence that decided it. ★★ The jud |
| `solidworks_session_solver_processes` | — | `—` | List the solver kernels currently running (the COSMOS/M family, enumerated via t |
| `solidworks_session_stuck_status` | — | `—` | Report whether SolidWorks looks stuck, using BOTH signals: it is not responding  |
| `solidworks_session_wait_until_idle` | timeout, interval | `—` | Block until `solidworks_session_busy_status` reports idle, or until the timeout  |

## `sw_custom_property`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_custom_property_count` | config_name | `model` | Return how many custom properties the document (or one configuration) has. ★ Rea |
| `solidworks_custom_property_get` | name, config_name | `model` | Read ONE file custom property: its value, its type (swCustomInfoType_e) and whet |
| `solidworks_custom_property_list` | config_name | `model` | Read ALL file custom properties of the active document: every name with its valu |
| `solidworks_custom_property_names` | config_name | `model` | Return the custom property names as a list. ★ Read-only. |

## `sw_delivery`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_collect_assembly_bom` | include_excluded | `model` | Read the assembly BOM as structured rows (the CSV-export tool is a different one |
| `solidworks_delivery_bom_traceability` | bom_rows, model_path, drawing_path, review_path | `—` | Build a traceability record from BOM rows. ★ Pure data — no SolidWorks call. |
| `solidworks_delivery_export_bom_csv` | output_path, include_excluded, overwrite | `model` | Export the assembly BOM to CSV. ★ The criterion is the FILE (exists and non-empt |
| `solidworks_delivery_pack_and_go_audit_matrix` | source_path, dependencies, component_records, associated_drawings, outputs, include_drawings, include_toolbox_components, include_suppressed | `—` | Build the audit matrix that a Pack-and-Go hand-off is reviewed against. ★ Pure d |

## `sw_drawing_create_missing`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_drawing_create_auxiliary_view` | x_mm, y_mm, z_mm, label, not_aligned, show_arrow, flip | `model` | ★ **辅助视图**：`IDrawingDoc.CreateAuxiliaryViewAt2(7 参)` |
| `solidworks_drawing_create_broken_view` | view_name, position1_mm, position2_mm, orientation, style, shape_intensity, break_sketch_blocks | `model` | ★ **断裂视图**：`IView.InsertBreak3(6 参)` → `BreakLine` |
| `solidworks_drawing_insert_datum_tag` | — | `model` | ★ **基准符号**：`IModelDoc2.InsertDatumTag2()` → `DatumTag`（★ **官方零参数**） |
| `solidworks_drawing_insert_surface_finish_symbol` | sym_type, leader_type, x_mm, y_mm, z_mm, lay_symbol, arrow_type, mach_allowance, other_vals, prod_method, sample_len, max_roughness, min_roughness | `model` | ★ **表面粗糙度符号**：`IModelDocExtension.InsertSurfaceFinishSymbol3(14 参)` |

## `sw_equation`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_equation_add` | equation, index, solve | `model` | Add a global equation. ★ Verify by reading the equations back (the criterion the |
| `solidworks_equation_delete` | index | `model` | Delete one global equation by index. ⚠ Does NOT save the document. |
| `solidworks_equation_evaluate` | — | `model` | Solve the global equations and return the result. ⚠ Does NOT save the document. |
| `solidworks_equation_list` | — | `model` | Return the document's global equations as a list. ★ Read-only. |

## `sw_geometry_selectors`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_available_direction_selectors` | — | `—` | List the direction-selector names usable when specifying geometry (no document n |
| `solidworks_available_point_selectors` | — | `—` | List the point-selector names usable when specifying geometry (no document neede |
| `solidworks_selector_resolve_direction` | selector | `—` | Resolve a named direction selector to its (x, y, z) vector. ★ Pure lookup — no S |
| `solidworks_selector_resolve_point` | selector, body_index | `model` | Resolve a named point selector to its (x, y, z) coordinates in MILLIMETRES. ★ No |

## `sw_gui_focus`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_gui_assert_focus` | hwnd, where | `—` | ★ **每个动作之前调用**：焦点不对就**修复**，**修不好就抛** ✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_focus.py` |
| `solidworks_gui_ensure_focus` | hwnd, retries, settle_seconds | `—` | 把 `hwnd` 置为前台并**回读确认**，返回**是否真的成功** ✓（★ 判据是回读，不是调用返回）★ 官方依据：**本仓自研**（`scripts/sw |
| `solidworks_gui_focus_state` | want | `—` | 读当前焦点状态（★ 期望窗口是否真的在前台）✓ ★ 官方依据：**本仓自研**（`scripts/sw_gui_focus.py`，pywin32 `GetFo |
| `solidworks_gui_get_foreground_window` | — | `—` | ★ 官方签名（逐字，来自 sw_gui_focus.py）：`查不到（非 SolidWorks API 成员）—— ★ 底层真源是 **pywin32 的 `w |

## `sw_render_material`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_appearance_delete_render_material` | index, cascade | `model` | ★ 官方签名（逐字，来自 DeleteRenderMaterial.md）：``System.bool DeleteRenderMaterial( System |
| `solidworks_collect_appearance_evidence` | — | `model` | Collect appearance evidence for the active document (read-only, for verification |
| `solidworks_list_render_materials` | — | `model` | List the render materials available in the active document. |
| `solidworks_refresh_scene_graph` | update | `model` | Refresh the graphics/scene graph, e.g. after an appearance change. ⚠ May mark th |

## `sw_simulation_study`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_simulation_create_mesh_for_control` | study_name, control_name | `study` | Mesh the study using a named mesh control. |
| `solidworks_simulation_generate_report` | study_name, template, path, append | `study` | Generate a study report to a file. ⚠ `template` valid values were NOT found in t |
| `solidworks_simulation_get_loads_manager` | — | `study` | ★ 官方签名（逐字，来自 sw_simulation_study.py）：`查不到 —— C:\swapi\types\ 下 566 个接口目录里没有任何 co |
| `solidworks_simulation_get_results` | — | `study` | ★ 官方签名（逐字，来自 sw_simulation_study.py）：`查不到 —— C:\swapi\types\ 下无 ICWStudy 目录（C:\s |

## `sw_sketch`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_count_arcs` | sketch_name | `—` | Count the ARCS in a sketch (the underlying call returns 16 floats per arc). ⚠ A  |
| `solidworks_sketch_count_lines` | sketch_name | `—` | Count the straight LINES in a sketch. ⚠ Use this rather than the raw getter: the |
| `solidworks_sketch_count_segments` | sketch_name | `—` | Count ALL segments in a sketch. ⚠ Not the same as the line count: segments are t |
| `solidworks_sketch_is_3d` | sketch_name | `—` | Whether the sketch is a 3D sketch (ISketch.Is3D). |

## `sw_toolbox_index`（4 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_toolbox_list_standards` | index | `—` | List the Toolbox standards available in the local index. ★ Pure data — no SolidW |
| `solidworks_toolbox_load_index` | path | `—` | Load the Toolbox index as a JSON-able dict. ★ Pure data — no SolidWorks call. |
| `solidworks_toolbox_part_path` | standard, part_name, index | `—` | Resolve a Toolbox part name to its file path. ★ Pure data — no SolidWorks call.  |
| `solidworks_toolbox_search` | keyword, standard, category | `—` | Search the Toolbox index by keyword. ★ Pure data — no SolidWorks call. |

## `sw_chamfer_geometry`（3 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_chamfer_circular_rim_volume` | radius_mm, width_mm | `—` | 算**圆孔缘** 45° 等距倒角**切掉的体积**（mm³）—— ★ 纯数学 ✓ ★ 官方依据：**本仓自研的几何公式**（`scripts/sw_chamf |
| `solidworks_chamfer_straight_edge_volume` | length_mm, width_mm | `—` | 算**直边** 45° 等距倒角**切掉的体积**（mm³）—— ★ **纯数学**、不碰 COM ✓ ★ 用途：★ 把「倒角到底切掉多少」变成**可判的判据* |
| `solidworks_chamfer_volume_report` | kind, volume_before_mm3, volume_after_mm3, expected_removed_mm3 | `—` | ★ 把「**倒角断言**」做成一条**可判的判据**：把实测的前后体积差与**公式算出的应切体积**对比 ⇒ ★ 不靠肉眼说「看着像倒角了」 ✓ ★ 官方依据： |

## `sw_drawing_view`（3 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_drawing_collect_view_evidence` | — | `model` | Collect the capability layer's per-view evidence for every view on the drawing.  |
| `solidworks_drawing_view_scale` | view_name | `model` | Get one view's scale by name. ★ An unknown name fails with the list of valid nam |
| `solidworks_drawing_view_set_scale` | view_name, scale | `model` | Set one view's scale and return before/after. ★ The criterion is that the READ-B |

## `sw_feature_entry_ops`（3 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_feature_cosmetic_thread` | standard, standard_type, size, diameter_mm, end_type, depth_mm, note | `model` | ★ **装饰螺纹线**：`IFeatureManager.InsertCosmeticThread3`（**7 参** · 官方 md **未标 Obsolet |
| `solidworks_flatten_surface` | accuracy_factor, should_use_tears, body_type | `model` | ★ **曲面展平**：`IFeatureManager.InsertFlattenSurface2(AccuracyFactor, ShouldUseTears |
| `solidworks_thicken` | thickness_mm, cut, direction, fill_volume, merge, use_feat_scope, use_auto_select | `model` | ★ **加厚 / 加厚切除**：**`IFeatureManager.FeatureBossThicken`（7 参）** / **`IFeatureManag |

## `sw_sketch_edit`（3 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_convert_entities` | chain, inner_loops | `model` | Convert the selected model edges into the active sketch. ★ The criterion is that |
| `solidworks_sketch_create_chamfer` | chamfer_type, distance_mm | `model` | Create a chamfer on the selected sketch entities. ★ Needs entities selected firs |
| `solidworks_sketch_mirror` | — | `model` | Mirror the selected sketch entities about the selected centerline. ★ The criteri |

## `sw_com_traps`（2 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_api_deprecated_successor` | member | `—` | Given a member name, return the successor this repo maps it to — and `None` when |
| `solidworks_repo_find_real_implementations` | needle, root | `—` | Search the repo for real implementations and return `["file:line", …]`. ★★ **Why |

## `sw_gear`（2 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_gear_calculate_spur` | spec | `—` | Compute the external involute spur gear geometry from a spec dict. ★ Pure calcul |
| `solidworks_gear_create_spur` | spec, plane_name | `model` | Create an external spur gear body. ★ The criterion is that the FEATURE TREE chan |

## `sw_import_mesh_reference`（2 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_mesh_configure_import_preferences` | units, model_type, import_textures, as_ps_mesh, segmented | `sw` | ★ 官方签名（逐字，来自 SetUserPreferenceIntegerValue.md）：`System.bool SetUserPreferenceInt |
| `solidworks_mesh_restore_import_preferences` | report | `sw` | ★ 官方签名（逐字，来自 SetUserPreferenceIntegerValue.md）：`System.bool SetUserPreferenceInt |

## `sw_surface`（2 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_surface_evidence` | — | `sw_app` | Read back the surface bodies on the active document: counts and types. Read-only |
| `solidworks_surface_runtime_available` | method | `—` | ★ 查某方法在**本机实测**里是否可取（`True` = 可取；**未实测的返回 `False`**）✓ ★★ 为什么它重要：`IModeler.Create |

## `sw_surface_ref_ops`（2 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_create_revolved_surface` | angle_deg, rev_type, reverse_dir, angle2_deg | `model` | ★ **旋转曲面**：`IFeatureManager.InsertRevolvedRefSurface(…)` → `IFeature` |
| `solidworks_insert_lofted_ref_surface` | closed, keep_tangency, force_non_rational, tess_tolerance_factor, start_matching_type, end_matching_type | `model` | ★ 放样曲面：`IModelDoc2.InsertLoftRefSurface2(…)`（6 参，回 `void`） |

## `sw_curve_and_split`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_insert_curve_through_points` | points_mm | `model` | ★ 通过参考点的曲线：`InsertCurveFileBegin()` → `InsertCurveFilePoint(X,Y,Z)`×N → `InsertC |

## `sw_gtol`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_gtol_insert` | — | `model` | Insert a GTol annotation (★ zero-argument: IModelDoc2.InsertGtol()). ★ The crite |

## `sw_helix`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_helix_insert` | height_mm, pitch_mm, revolution | `model` | Insert a helix/spiral. ★ Needs the document state the official API requires (a c |

## `sw_loft`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_part_loft` | profile_sketches, closed, use_selected_profiles | `model` | ★ **用「轮廓草图」放样** —— 走 `IFeatureManager.InsertProtrusionBlend2`（官方 **18 参**） |

## `sw_macro`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_macro_run` | file_path, module_name, procedure_name, options | `sw_app` | Run a macro from a project file (official `System.bool RunMacro2(String FilePath |

## `sw_mass_property`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_part_mass_properties` | — | `model` | Read the mass properties of the ACTIVE part, without any conversion: volume (mm^ |

## `sw_measure`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_measure_selection` | arc_option | `model` | ★ **量当前选中的实体**（逐几何量测）—— 走 `IModelDocExtension.CreateMeasure` → `IMeasure` |

## `sw_misumi`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_misumi_suggest_part` | keyword, count | `—` | ★ 官方签名（逐字，来自 sw_misumi.py）：`查不到（非 SolidWorks API 成员 —— 本函数是仓库自写的纯 Python HTTP 辅助 |

## `sw_preflight`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_preflight_check_com_dependencies` | — | `—` | ★ 官方签名（逐字，来自 sw_preflight.py）：`查不到（非 SolidWorks API 成员）` |

## `sw_sensor`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_read_sensors` | — | `model` | ★ **列出文档里的传感器并读它们当前的值** —— 走 `ISensor`（10 个成员） |

## `sw_session`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_undo` | steps | `model` | ★ **撤销** —— 走 `IModelDoc2.EditUndo2`（官方 **1 参** · ★★ **返回 `void`**） |

## `sw_sketch_dimensions`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_insert_chain_dimensions` | selection | `model` | ★ 官方签名（逐字，来自 InsertChainDimensions.md）：`System.object InsertChainDimensions( Sys |

## `sw_sketch_status`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_sketch_fully_defined_status` | — | `model` | ★ **草图完全定义状态**：`ISketch.GetConstrainedStatus()` → `System.int`（官方零参数、只读） |

## `sw_sweep`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_part_sweep` | profile_sketch, path_sketch, cut | `model` | ★ **用「轮廓 + 路径」建扫描特征** —— 走官方**现代入口** `IFeatureManager.CreateDefinition(swFmSweep |

## `sw_units`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_read_document_units` | — | `model` | ★ **读文档单位**（★ 两条路：主源 + 对照源，★ 它们是**不同层次**、**允许不同**） |

## `sw_wrap`（1 个）

| 工具 | 参数 | 注入键 | 说明（首句） |
|---|---|---|---|
| `solidworks_part_wrap` | wrap_type, thickness_mm, reverse | `model` | ★ **对已选中的「草图（mark=4）+ 面（mark=1）」建包覆特征** —— 走官方 `IFeatureManager.InsertWrapFeatur |

