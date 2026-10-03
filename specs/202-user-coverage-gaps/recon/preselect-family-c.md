# 「要求调用方先选」这一族 —— batch51..batch76 全量排查（C 路）

> ★ **范围**：只扫 `mcp-server/tool_specs_batch51.py` **及之后**的全部批次（batch51…batch76，共 26 个文件 · **88 条工具**）。
> ★ **机制依据（事实 503，已在本轮逐字复核）**：`mcp-server/tool_registry.py` 的 `make_tool_function._impl` 里顺序是
> `kwargs[inject_as or inj] = resolver(params)` → `spec.pre_call(params)` → `kwargs.update(derived_args)` → 调目标函数。
> ⇒ **`inject` 解析器先跑**（`RESOLVERS["model"]` → `connect_solidworks()`，**会清空选区**），**`pre_call` 后跑**。
> ⇒ **凡是要求「调用方先选好某个东西」的工具，没有 `pre_call` 就经工具层永远拿不到那个选区。**
>
> ★ **盘点结论（本范围）**：真正挂了 `pre_call` 的只有 **batch74 的 2 条**（`_select_faces_for`），
> **batch58 / batch60 共 9 条通过 `tool_specs_batch29._spec` 工厂间接挂了 `pre_call=_select_face`**。
> **其余 79 条一条 `pre_call` 都没有**（全仓 grep `pre_call` 在本范围只命中 batch58/60 的 import、batch61 的注释、batch74 的 2 处挂载与 1 处 docstring）。

## 判读口径（三处细化，先声明，避免误读数字）

1. **「读选区?」列有三档**：`是` = 依赖调用前已存在的选区；`是（自建）` = 函数**自己**在调用前按选择器把选区建起来；
   `否` = 完全不碰选区。
2. ⚠ **按题目要求区分的两个方向**：**「函数返回/回读选区信息」≠「函数要求选区」**。
   `sw_selection_spec.get_selection_count` 属于**回读**——但它回读的对象**正是被 inject 清掉的那个选区**，
   所以它虽然不改模型，经工具层**永远只能看到 0** ⇒ 仍判「真危险」，依据栏写明它是**诊断型**。
3. ★ `是（自建）` 的归 **无关**：它**不要求调用方预选** ⇒ 不是事实 503 的受害者。
   （这批共 20 条，占「无关」的主体；把它们误报成受害者会虚增真危险数。）
4. ⚠ **另一类前置不算进本族**：`solidworks_sketch_fully_defined_status` 的前置是「**必须有活动草图**」、
   `solidworks_drawing_create_projected_view` 的前置是「`part_path` 必须已存盘」、
   `solidworks_drawing_create_detail_view` 的前置是「图上有局部圆」、`solidworks_drawing_create_break_view` 明写「**零选区前置**」
   ⇒ 这些**不是选区前置**，归「无关」，但在此点名，免得下一轮把它们当漏网之鱼。

---

## 一、真危险（读到/依赖选区 + **无 `pre_call`**）—— 22 条

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据（文件 + 原文片段） |
|---|---|---|---|---|---|
| `solidworks_selection_count` | `sw_selection_spec.get_selection_count` | 是 | 否 | **真危险** | `scripts/sw_selection_spec.py`：`sm = get_com_member(model, "SelectionManager")`、`get_com_member(sm, "GetSelectedObjectCount2", -1)` —— 纯回读，**无 pre_call** ⇒ 诊断型，经工具层恒回 0 |
| `solidworks_resolve_selection` | `sw_selection_spec.resolve_selection` | 是 | 否 | **真危险** | `scripts/sw_selection_spec.py`：`count = get_selection_count(model)`、`"选择器 %r 解析后**选区计数为 0** —— 没选中任何东西"` —— `__current_selection__` 路径必失败 |
| `solidworks_selection_point` | `sw_selection_spec.selection_point` | 是 | 否 | **真危险** | `scripts/sw_selection_spec.py`：`get_com_member(sm, "GetSelectionPoint", ...)`、`"selection_count": int(...)`；docstring `★ 包一层「**先选点、再建孔**」` |
| `solidworks_resolve_entity` | `sw_selection_spec.resolve_entity_report` | 是 | 否 | **真危险** | `scripts/sw_selection_spec.py`：`out["count"] = int(get_selection_count(model))`、`"解析出了对象**而选区计数为 0** ⇒ 选择器是 __current_selection__ 时"` |
| `solidworks_sketch_stretch_entities` | `sw_sketch_modify_ops.sketch_stretch` | 是 | 否 | **真危险** | `scripts/sw_sketch_modify_ops.py` docstring：`★ 官方说明逐字 "Stretch the selected entities" ⇒ ★ **要求先选中实体**` —— 函数体**不自建选区** |
| `solidworks_insert_planar_surface` | `sw_surface_edit_ops.insert_planar_surface` | 是 | 否 | **真危险** | `scripts/sw_surface_edit_ops.py` docstring：`★ 官方语义：用**当前选中的封闭边界**（草图 / 边）生成一张平面曲面 ⇒ ★ **调用前要选好边界**` |
| `solidworks_insert_offset_surface` | `sw_surface_edit_ops.insert_offset_surface` | 是 | 否 | **真危险** | `scripts/sw_surface_edit_ops.py` docstring：`⚠ ★ 官方没写"要不要先选面"，而语义上要（参考面）；★ 调用方负责先选` |
| `solidworks_insert_ruled_surface` | `sw_surface_edit_ops.insert_ruled_surface` | 是 | 否 | **真危险** | `scripts/sw_surface_edit_ops.py` docstring：`★★ **调用前先把边按 \`mark=4\` 选中**（铁律 3 第三句）` |
| `solidworks_insert_replace_face` | `sw_surface_edit_ops.insert_replace_face` | 是 | 否 | **真危险** | `scripts/sw_surface_edit_ops.py` docstring：`⇒ ★ **调用方必须先把「要替换的面」按 \`mark=1\`、「替换成哪个面」按 \`mark=2\` 选好**` |
| `solidworks_insert_lofted_ref_surface` | `sw_surface_ref_ops.insert_lofted_ref_surface` | 是 | 否 | **真危险** | `scripts/sw_surface_ref_ops.py` docstring：`★★ **调用前要选好轮廓**`、`The mark for: **profile selections should be 1**` |
| `solidworks_create_revolved_surface` | `sw_surface_ref_ops.insert_revolved_ref_surface` | 是 | 否 | **真危险** | `scripts/sw_surface_ref_ops.py` docstring：`⚠ **调用前要选好轮廓**（★ 官方 Remarks 逐字："Make the selections using` —— 且明写「★ 官方**没给** mark」 |
| `solidworks_insert_ref_plane` | `sw_ref_geometry.insert_ref_plane` | 是 | 否 | **真危险** | `mcp-server/tool_specs_batch70.py` doc：`⚠⚠ **调用前必须按 mark 选参考实体**`、`**0 = First reference entity · 1 = Second · 2 = Third**` |
| `solidworks_insert_reference_point` | `sw_ref_geometry.insert_reference_point` | 是 | 否 | **真危险** | `mcp-server/tool_specs_batch70.py` doc：`★★ 而选面**必须紧接着调用** —— 中间隔别的步骤会把选区清掉。` |
| `solidworks_insert_global_bounding_box` | `sw_ref_geometry.insert_global_bounding_box` | **条件** | 否 | **真危险**（条件） | `scripts/sw_ref_geometry.py` docstring：`⚠ 官方 Remarks：「If \`BBoxType\` is \`swBoundingBoxType_CustomPlane\`, then **select a face`、`⇒ ★ **只有 \`CustomPlane\`(2) 才要先选面** ✓` |
| `solidworks_drawing_create_auxiliary_view` | `sw_drawing_create_missing.create_auxiliary_view` | 是 | 否 | **真危险** | `scripts/sw_drawing_create_missing.py` docstring：`> Creates an auxiliary view **based on a selected edge in a drawing view**.`、`sel = _selection_count(model)`、`★ 本模块**不代选**` |
| `solidworks_drawing_insert_surface_finish_symbol` | `sw_drawing_create_missing.insert_surface_finish_symbol` | 是 | 否 | **真危险** | `scripts/sw_drawing_create_missing.py` docstring：`**last selection**」⇒ ★ 调用前必须有选区；★ 本模块**不代选**（★ 规则 3）、`sel = _selection_count(model)` |
| `solidworks_drawing_insert_datum_tag` | `sw_drawing_create_missing.insert_datum_tag` | 是 | 否 | **真危险** | `scripts/sw_drawing_create_missing.py` docstring：`· 官方摘要逐字「Inserts a datum tag symbol **at a selected location**.」`、`⇒ ★★ **调用前必须先选中一个位置**`、`sel = _selection_count(model)` |
| `solidworks_sheet_metal_insert_miter_flange` | `sw_sheet_metal_weld_entry.insert_sheet_metal_miter_flange` | 是 | 否 | **真危险**（推定） | `scripts/sw_sheet_metal_weld_entry.py`：`"selection_marks": _selection_marks(model)`、`★★ **官方页无 \`## Remarks\` 段 ⇒ 前置查不到** ⇒ 本模块**不编前置**` —— 见「拿不准」 |
| `solidworks_sheet_metal_insert_closed_corner` | `sw_sheet_metal_weld_entry.insert_sheet_metal_closed_corner` | 是 | 否 | **真危险**（推定） | `scripts/sw_sheet_metal_weld_entry.py`：`"selection_marks": _selection_marks(model)`、`⚠⚠ **前置**：★ 官方页**无 \`## Remarks\` 段** ⇒ ★★ **前置查不到**（铁律 5）⇒ 本模块` + `★ 官方**零参**` |
| `solidworks_drawing_create_section_view` | `sw_drawing_expose.create_section_view` | 是 | 否 | **真危险** | `scripts/sw_drawing_expose.py` docstring：`★ 剖面视图（\`CreateSectionViewAt5\`）—— ★ **调用前必须先选好剖面线**（官方 Remarks 逐字）`、`pre = _selection_count(drawing_model)` |
| `solidworks_drawing_create_hole_table` | `sw_drawing_expose.create_hole_table` | 是 | 否 | **真危险** | `scripts/sw_drawing_expose.py` docstring：`基准原点**顶点 mark 1** ·`、`孔**边与面 mark 2**`、`★ 本函数**不代选**`、`marks = _selection_marks(drawing_model)` |
| `solidworks_drawing_add_note` | `sw_drawing_expose.add_drawing_note` | 是 | 否 | **真危险** | `scripts/sw_drawing_expose.py` docstring：`★ 注释/文字（\`InsertNote\`）—— ★ 引线附着点来自**调用前**的选择（官方 Remarks 逐字）。` |

> ★★ **这 22 条里 20 条的 spec 连 `selection` 参数都没有**（batch73/74/75 全批无 `Param("selection")`）⇒
> ★ **调用方连「我选了哪个」都无法表达**，只能指望界面预选，而界面预选**必被 inject 清空** ⇒ **结构性死锁**。

## 二、安全（依赖选区 + **有 `pre_call`**）—— 11 条

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据（文件 + 原文片段） |
|---|---|---|---|---|---|
| `solidworks_simulation_apply_convection` | `sw_simulation_loads.apply_convection_report` | 是 | **是** | 安全 | `mcp-server/tool_specs_batch58.py`：`from tool_specs_batch29 import _SEL, _STUDY, _spec`；`mcp-server/tool_specs_batch29.py`：`pre_call=_select_face`、`def _select_face(params):` |
| `solidworks_simulation_apply_heat_flux` | `sw_simulation_loads.apply_heat_flux_report` | 是 | **是** | 安全 | 同上（batch58 经 batch29 工厂） |
| `solidworks_simulation_apply_heat_power` | `sw_simulation_loads.apply_heat_power_report` | 是 | **是** | 安全 | 同上 |
| `solidworks_simulation_apply_radiation` | `sw_simulation_loads.apply_radiation_report` | 是 | **是** | 安全 | 同上 |
| `solidworks_simulation_apply_elastic_connector` | `sw_simulation_loads.apply_elastic_connector_report` | 是 | **是** | 安全 | 同上 |
| `solidworks_simulation_apply_temperature` | `sw_simulation_loads.apply_temperature_report` | 是 | **是** | 安全 | 同上（⚠ 与文件头「仍不注册」的注释不一致，**工具实际已注册**） |
| `solidworks_simulation_apply_distributed_mass` | `sw_simulation_loads.apply_distributed_mass_report` | 是 | **是** | 安全 | `mcp-server/tool_specs_batch60.py`：`from tool_specs_batch29 import _SEL, _STUDY, _spec`（batch60 零 `ToolSpec`，全走工厂） |
| `solidworks_simulation_apply_force` | `sw_simulation_loads.apply_force_report` | 是 | **是** | 安全 | 同上 |
| `solidworks_simulation_apply_remote_load` | `sw_simulation_loads.apply_remote_load_report` | 是 | **是** | 安全 | 同上（⚠ 与文件头「不注册」的注释不一致，**工具实际已注册**） |
| `solidworks_weldment_insert_end_cap` | `sw_sheet_metal_weld_entry.insert_weldment_end_cap` | 是 | **是** | 安全 | `mcp-server/tool_specs_batch74.py`：`pre_call=_select_faces_for(0, 1),`、`"""★ 造一个 \`pre_call\`：调目标函数前按官方 mark 选 \`count\` 个面。` |
| `solidworks_weldment_gusset_create` | `sw_sheet_metal_weld_entry.insert_weldment_gusset` | 是 | **是** | 安全 | `mcp-server/tool_specs_batch74.py`：`pre_call=_select_faces_for(1, 2),`（官方 mark=1 · 两个面） |

> ★ **这 11 条是本仓「正确形态」的样板**：`pre_call` 在 inject **之后**跑 ⇒ 选区能存活到第 3 步。

## 三、无关（不依赖调用方预选）—— 55 条

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据（文件 + 原文片段） |
|---|---|---|---|---|---|
| `solidworks_read_sensors` | `sw_sensor.read_sensors_report` | 否 | 否 | 无关 | `scripts/sw_sensor.py` docstring：`本函数走**特征树遍历 + \`GetSpecificFeature2()\`**` |
| `solidworks_read_document_units` | `sw_units.read_units_report` | 否 | 否 | 无关 | `scripts/sw_units.py`：主源 `IModelDoc2.GetUnits()` + 用户偏好，无 SelectionManager |
| `solidworks_undo` | `sw_session.undo_report` | 否 | 否 | 无关 | `scripts/sw_session.py`：官方 `IModelDoc2.EditUndo2`，**1 参**、回 `void`，判据是特征树增量 |
| `solidworks_select_entity_by_index` | `sw_selection_spec.select_entity_by_index` | 是（自建） | 否 | 无关 | `scripts/sw_selection_spec.py`：`select_object(` —— 按序号**自己选中** |
| `solidworks_select_by_selector` | `sw_selection_spec.select_by_selector_report` | 是（自建） | 否 | 无关 | `scripts/sw_selection_spec.py` docstring：`★ 它把 \`select_object\`（吃 COM 对象）与 \`resolve_entity\`（吐 COM 对象）**接起来**` |
| `solidworks_sketch_add_arc` | `sw_part.sketch_arc` | 否 | 否 | 无关 | `scripts/sw_part.py`：走 `ISketchManager.CreateArc`，坐标为入参 |
| `solidworks_sketch_add_ellipse` | `sw_part.sketch_ellipse` | 否 | 否 | 无关 | 同上（`ISketchManager.CreateEllipse`） |
| `solidworks_sketch_add_polygon` | `sw_part.sketch_polygon` | 否 | 否 | 无关 | 同上（内切圆 + 边数为入参） |
| `solidworks_sketch_add_slot` | `sw_part.sketch_slot` | 否 | 否 | 无关 | 同上（两点 + 半径为入参） |
| `solidworks_sketch_add_centerline` | `sw_part.sketch_centerline` | 否 | 否 | 无关 | 同上（`ISketchManager.CreateCenterLine`） |
| `solidworks_current_sketch_name` | `sw_part.current_sketch_name` | 否 | 否 | 无关 | 同上：按名取草图，不碰选区 |
| `solidworks_auto_dimension_sketch` | `sw_part.auto_dimension_sketch` | 是（自建） | 否 | 无关 | `scripts/sw_part.py`：`model.ClearSelection2(True)`、`for segment, mark in ((vertical, 2), (horizontal, 4)):`、`segment.Select3(selected > 0, mark, ...)` |
| `solidworks_add_dimension` | `sw_part.add_dimension_report` | 是（自建） | 否 | 无关 | `scripts/sw_part.py` docstring：`⇒ ★ 本包装用**声明式选择器**先选中（★ 规则 3），★ 选不中就**不开工**。` |
| `solidworks_hole_pattern` | `sw_hole_features.hole_pattern_report` | 否 | 否 | 无关 | `scripts/sw_hole_features.py`：孔位 `positions` 是显式坐标列表（规则 3 书面例外） |
| `solidworks_export_image` | `sw_export.export_image_report` | 否 | 否 | 无关 | `scripts/sw_export.py`：判据是**文件**（存在且 size > 0） |
| `solidworks_simulation_apply_rigid_connector` | `sw_simulation_loads.apply_rigid_connector_by_objects_report` | 是（自建） | 否 | 无关 | `scripts/sw_simulation_loads.py` docstring：`★ 本包装**自己把两组实体装好**（★ \`entities_as_array\`）` + `★★ **没有 \`pre_call\`** —— ★ 本工具**不读选区**` |
| `solidworks_weldment_create_structural_member` | `sw_weldment.create_structural_member_from_sketch` | 否 | 否 | 无关 | `scripts/sw_weldment.py`：草图**按名**取 + `.sldlfp` 轮廓路径，判据看特征树类型名 |
| `solidworks_select_face_selector` | `sw_simulation.select_face_by_selector_report` | 是（自建） | 否 | 无关 | `scripts/sw_simulation.py`：`point = resolve_face_selector(model, selection)`（在 `select_face_by_selector` 内）⇒ **自选** |
| `solidworks_simulation_apply_link_connector` | `sw_simulation_loads.add_link_connector_report` | 是（自建） | 否 | 无关 | `scripts/sw_simulation_loads.py`：`from .sw_selection_spec import resolve_entity` ⇒ 两个**顶点**由选择器内部解析 |
| `solidworks_sketch_add_3point_rectangle` | `sw_sketch_primitives.sketch_3point_corner_rectangle` | 否 | 否 | 无关 | `scripts/sw_sketch_primitives.py`：`Create3PointCornerRectangle`，三点为入参 |
| `solidworks_sketch_add_3point_center_rectangle` | `sw_sketch_primitives.sketch_3point_center_rectangle` | 否 | 否 | 无关 | 同上（`Create3PointCenterRectangle`） |
| `solidworks_sketch_add_parallelogram` | `sw_sketch_primitives.sketch_parallelogram` | 否 | 否 | 无关 | 同上（`CreateParallelogram`） |
| `solidworks_sketch_add_tangent_arc` | `sw_sketch_primitives.sketch_tangent_arc` | 否 | 否 | 无关 | 同上（`CreateTangentArc`，相切对象是**上一条自己画的段**） |
| `solidworks_sketch_add_3point_arc` | `sw_sketch_primitives.sketch_3point_arc` | 否 | 否 | 无关 | 同上（`Create3PointArc`） |
| `solidworks_sketch_add_partial_ellipse` | `sw_sketch_primitives.sketch_elliptical_arc` | 否 | 否 | 无关 | 同上（`CreateEllipticalArc`） |
| `solidworks_sketch_add_parabola` | `sw_sketch_primitives.sketch_parabola` | 否 | 否 | 无关 | 同上（`CreateParabola`，焦点/顶点/端点为入参） |
| `solidworks_sketch_add_conic` | `sw_sketch_primitives.sketch_conic` | 否 | 否 | 无关 | 同上（`CreateConic`，签名与抛物线同形） |
| `solidworks_sketch_add_perimeter_circle` | `sw_sketch_primitives.sketch_perimeter_circle` | 否 | 否 | 无关 | 同上（`PerimeterCircle`，官方**只有 6 个参数**） |
| `solidworks_sketch_trim` | `sw_sketch_edit_ops.sketch_trim` | 是（自建） | 否 | 无关 | `scripts/sw_sketch_edit_ops.py`：`_select_spec(model, selection)` —— **自建**；docstring 虽写 `★ 官方 Remarks 对**每个选项**都写了"调用前必须先选几条段"` 但**本函数按选择器先选好** |
| `solidworks_sketch_extend` | `sw_sketch_edit_ops.sketch_extend` | 是（自建） | 否 | 无关 | 同上：`_select_spec(model, selection)` |
| `solidworks_sketch_offset` | `sw_sketch_edit_ops.sketch_offset` | 是（自建） | 否 | 无关 | 同上：`_select_spec(model, selection)` |
| `solidworks_sketch_fillet` | `sw_sketch_edit_ops.sketch_fillet` | 是（自建） | 否 | 无关 | 同上：`_select_spec(model, selection)` |
| `solidworks_sketch_linear_pattern` | `sw_sketch_edit_ops.sketch_linear_pattern` | 是（自建） | 否 | 无关 | 同上：`_select_spec(model, selection)` |
| `solidworks_sketch_circular_pattern` | `sw_sketch_edit_ops.sketch_circular_pattern` | 是（自建） | 否 | 无关 | 同上：`_select_spec(model, selection)` |
| `solidworks_sketch_move_entities` | `sw_sketch_modify_ops.sketch_move` | 否 | 否 | 无关 | `scripts/sw_sketch_modify_ops.py`：`SketchModifyTranslate`，改的是**草图坐标系**（4 个坐标入参） |
| `solidworks_sketch_rotate_entities` | `sw_sketch_modify_ops.sketch_rotate` | 否 | 否 | 无关 | 同上（`SketchModifyRotate`，中心 + 角度入参） |
| `solidworks_sketch_scale_entities` | `sw_sketch_modify_ops.sketch_scale` | 否 | 否 | 无关 | 同上（`SketchModifyScale`，比例因子入参） |
| `solidworks_sketch_flip_entities` | `sw_sketch_modify_ops.sketch_flip` | 否 | 否 | 无关 | 同上（`SketchModifyFlip`，`AxisFlag` int 透传） |
| `solidworks_insert_delete_face` | `sw_surface_edit_ops.insert_delete_face` | 否 | 否 | 无关 | `scripts/sw_surface_edit_ops.py`：`InsertDeleteFace(Option)` **官方后继版**，单参数、不需选区 |
| `solidworks_insert_center_of_mass` | `sw_ref_geometry.insert_center_of_mass` | 否 | 否 | 无关 | `scripts/sw_ref_geometry.py`：`IFeatureManager.InsertCenterOfMass()` **零参数** |
| `solidworks_insert_coordinate_system` | `sw_ref_geometry.insert_coordinate_system` | 否 | 否 | 无关 | 同上（`InsertCoordinateSystem` 3 参，全是翻转标志） |
| `solidworks_insert_curve_through_points` | `sw_curve_and_split.insert_curve_through_points` | 否 | 否 | 无关 | `scripts/sw_curve_and_split.py`：`InsertCurveFileBegin()` → `Point`×N → `End`，点是显式坐标 |
| `solidworks_sketch_fully_defined_status` | `sw_sketch_status.get_constrained_status` | 否 | 否 | 无关 | `scripts/sw_sketch_status.py`：`⚠ **前置**：**必须有一个正在编辑的草图**` ⇒ ★ **不是选区前置**（见口径 4） |
| `solidworks_drawing_create_broken_view` | `sw_drawing_create_missing.insert_break_lines` | 否 | 否 | 无关 | `scripts/sw_drawing_create_missing.py` docstring：`★ **零选区前置**`、`本模块改成**按视图名解析**，★ 所以不要求调用者备选区` |
| `solidworks_surface_midsurface_create` | `sw_sheet_metal_weld_entry.create_midsurface` | 否 | 否 | 无关 | `scripts/sw_sheet_metal_weld_entry.py`：按**体号**给的入口，实体由入参解析 |
| `solidworks_drawing_create_projected_view` | `sw_drawing_expose.create_projected_view` | 否 | 否 | 无关 | `scripts/sw_drawing_expose.py` docstring：`★ 前置：\`part_path\` 必须是**已存盘的模型完整路径且含 \`.sldprt\`/\`.sldasm\`**` ⇒ **不是选区前置** |
| `solidworks_drawing_create_detail_view` | `sw_drawing_expose.create_detail_view` | 否 | 否 | 无关 | 同上：前置是 `图上有局部圆（草图圆）` ⇒ **不是选区前置** |
| `solidworks_drawing_set_sheet_format` | `sw_drawing_expose.set_sheet_format` | 否 | 否 | 无关 | 同上：`ISheet.SetTemplateName` + `ForceRebuild3`，不碰选区 |
| `solidworks_drawing_create_revision_table` | `sw_drawing_expose.create_revision_table` | 否 | 否 | 无关 | 同上：`ISheet.InsertRevisionTable2`，模板与表同型，不碰选区 |
| `solidworks_drawing_insert_center_marks` | `sw_drawing_expose.insert_center_marks` | 否 | 否 | 无关 | 同上：`AutoInsertCenterMarks2`，按**视图清单**批量插，不碰选区 |
| `solidworks_feature_cosmetic_thread` | `sw_feature_entry_ops.insert_cosmetic_thread` | 是（自建） | 否 | 无关 | `scripts/sw_feature_entry_ops.py` docstring：`再取它的**第一条边**并按 \`mark=0\` 选中 ⇒ ★ 调用方**不必**先选`、`_select_com_object(edges[0], append=False, mark=0)` |
| `solidworks_sketch_spline` | `sw_part.sketch_spline` | 否 | 否 | 无关 | `scripts/sw_part.py`：控制点为显式坐标入参 |
| `solidworks_flatten_surface` | `sw_feature_entry_ops.create_flatten_surface` | 是（自建） | 否 | 无关 | `scripts/sw_feature_entry_ops.py` docstring：`★ 本函数**自己选**（★ 调用方不必先选）：取**曲面体的第一张面**按 \`mark=1\`` |
| `solidworks_thicken` | `sw_feature_entry_ops.thicken_surface` | 是（自建） | 否 | 无关 | 同上 docstring：`⇒ ★ 本函数**自己把第一张面按 \`mark=1\` 选上**（★ 与展平那条同一手法）` |

---

## 四、统计

| 档位 | 条数 |
|---|---|
| **真危险** | **22** |
| **安全** | **11** |
| **无关** | **55** |
| 合计 | **88** |

★ 其中「无关」里有 **20 条是「自建选区」**（`是（自建）`）——★ 它们**不要求调用方预选**，不是事实 503 的受害者；
★ 真危险的 **22** 条里，**20 条的 spec 连 `selection` 参数都没有**（batch73/74/75 全批），只有 `solidworks_sketch_stretch_entities`
与 `solidworks_insert_global_bounding_box` 之外的 drawing 四条靠**界面预选**——★ 而那必被 inject 清空。

## 五、真危险那批的建议排序（按「最可能拿到选区的方式」）

> 排序依据 = **仓内现成的「声明式选区」构件离它多近** + **官方有没有给出可编程的 mark**。
> ★ 通用手法已经现成：`mcp-server/tool_specs_batch74.py` 的 `_select_faces_for(mark, count)`
> （**按对象遍历体→面、按 mark 选、回读计数、不够就抛**）——★ 它就是这 22 条的直接解法模板。

### 第 1 档 · 面/边选择器已在仓内现成 ⇒ 加一个 `pre_call` 就能活（**9 条 · 建议先修**）

`sw_simulation.select_face_by_selector`（`FACE_SELECTORS = +x/-x/+y/-y/+z/-z`）已真机跑通，
`sw_selection_spec.resolve_entity(selector="index:<n>")` 也在 ⇒ 这批只需把 batch74 的 `_select_faces_for` 复用到它们身上：

| 建议顺序 | 工具 | 可用的选择器 / mark |
|---|---|---|
| 1 | `solidworks_insert_planar_surface` | 只需「一个封闭边界」⇒ 面上任意一点即可，**mark 官方未给** ⇒ 用 `mark=0` |
| 2 | `solidworks_insert_offset_surface` | 一个参考面 ⇒ 同上 |
| 3 | `solidworks_drawing_insert_datum_tag` | 官方示例就是 `SelectByID2("", "EDGE", …)` ⇒ **一条边 `mark=0`** |
| 4 | `solidworks_drawing_insert_surface_finish_symbol` | 官方逐字 `based on the **last selection**` ⇒ 需要**两个点**（面 + 边），**14 参入口** |
| 5 | `solidworks_insert_ruled_surface` | 官方逐字给了 `mark=4` ⇒ **一条边**，`_select_faces_for(4, 1)` 可直接用 |
| 6 | `solidworks_insert_replace_face` | 官方给了完整 mark 表：被替换面 `mark=1` + 替换面 `mark=2` ⇒ `_select_faces_for(1,1)` ×2 |
| 7 | `solidworks_sheet_metal_insert_closed_corner` | 零参 void ⇒ 必须靠选区；`mark` 官方未给（`_selection_marks` 只回读）⇒ **先查 CHM 示例** |
| 8 | `solidworks_sheet_metal_insert_miter_flange` | 同上，**官方页无 Remarks** ⇒ 前置查不到（铁律 5）⇒ **先补查再定 mark** |
| 9 | `solidworks_insert_global_bounding_box` | **仅 `bbox_type=CustomPlane`(2)** 才要选面 ⇒ 在 `pre_call` 里按 `bbox_type` 分支，默认 `BestFit(1)` 不选 |

### 第 2 档 · 官方给了明确 mark 表，但需要「按草图/曲面体里的东西选」⇒ 需扩展选择器（**5 条**）

| 工具 | 需要的选区 | 已有构件 |
|---|---|---|
| 10 | `solidworks_insert_ref_plane` | 官方给了 `0/1/2 = First/Second/Third reference entity` ⇒ **最多三个参考实体**；`_select_faces_for(0,1)` 只够第一档 |
| 11 | `solidworks_drawing_create_hole_table` | 官方 mark 表齐全（顶点 1 · 边与面 2 · X 向参考 4 · Y 向参考 8）⇒ **四组 mark**，需 `_select_marks_for(1,2,4,8)` |
| 12 | `solidworks_insert_lofted_ref_surface` | 轮廓 `mark=1`，`closed=True` 时**至少三条** ⇒ 需**草图轮廓**选择器（不是面） |
| 13 | `solidworks_sketch_stretch_entities` | 官方 `Stretch the selected entities` ⇒ **草图实体**选择器；`sw_sketch_edit_ops._select_spec` 已能做「草图段按 index」⇒ **可复用** |
| 14 | `solidworks_create_revolved_surface` | 轮廓 + 中心线；★ **官方没给 mark** ⇒ 需先在 CHM 找示例（与 batch69/72 同一坑） |

### 第 3 档 · 前置在**图纸/图形区**而非零件体上 ⇒ 选择器形态不同（**3 条**）

| 工具 | 需要的选区 | 难点 |
|---|---|---|
| 15 | `solidworks_drawing_create_auxiliary_view` | 官方逐字 `based on a **selected edge in a drawing view**` ⇒ 选的是**图纸视图里的边**，现有选择器都作用在零件体上 |
| 16 | `solidworks_drawing_create_section_view` | 官方逐字「**调用前必须先选好剖面线**」⇒ 剖面线是**草图**（§视图中已有），同样要图纸侧选择器 |
| 17 | `solidworks_drawing_add_note` | 引线附着点来自**调用前**的选择 ⇒ 弱前置（无附着点时也能建注释），优先级最低 |

### 第 4 档 · 只读诊断 + 一个条件性条目（**2 条 · 建议与「选择底座」一起处置**）

| 工具 | 说明 |
|---|---|
| 18–21 | `solidworks_selection_count` · `solidworks_resolve_selection` · `solidworks_selection_point` · `solidworks_resolve_entity` —— ★ 这 4 条是**选择底座本身**，它们不是「受害者」而是**受害者链的源头**：inject 清空 ⇒ 恒回 0。⇒ 建议**改判据**：让它们绕开 `inject`（它们并不需要 `RESOLVERS["model"]` 去连文档）★ **这一条改完，上面 3 档的 17 条里凡以 `__current_selection__` 为入口的也一起活了** |
| 22 | `solidworks_insert_reference_point` —— 只有 `ref_point_type=FaceCenter(4)` / `FaceVertexProjection(5)` 之类才需要参考面；★ **`NumberOfRefPoints` 必须是 1**（官方）⇒ 加 `pre_call` 前先按 `ref_point_type` 分支 |

> ★★ **一句话建议**：**先做第 4 档的「选择底座 4 条」**（改 `inject` 即可，零几何工作量、影响面最大），
> ★ 再照 `_select_faces_for` 批量给第 1 档 9 条挂 `pre_call`，第 2/3 档需要先补选择器形态。

## 六、拿不准处（如实标注，未当成结论）

1. ★★ `solidworks_sheet_metal_insert_miter_flange` 与 `solidworks_sheet_metal_insert_closed_corner`
   —— ★ **官方页没有 `## Remarks` 段**（能力层自己逐字核过并写进 docstring：`**官方页无 ## Remarks 段 ⇒ 前置查不到**`）
   ⇒ 我判「真危险」是**按语义 + 「零参/回 void」推的**（没有返回对象可读 ⇒ 结果只能由选区决定），
   **不是官方逐字依据** ⇒ 按铁律 5，需先查 CHM 示例页确认 mark。
2. ⚠ `solidworks_insert_global_bounding_box` 是**条件性**前置（★ 官方：只有 `CustomPlane`(2) 才要先选面）；
   默认 `BestFit(1)` 不需要 ⇒ 我在表里标「真危险（条件）」而不是无脑算一条。
3. ⚠ `solidworks_insert_reference_point` 的选区前置**只对部分 `ref_point_type` 成立**；
   我据的是 **spec 的 doc 字段**（`★ 真机：先选一个面（mark=0）+ FaceCenter(4) ⇒ 树新增 点1。`），
   **不是能力层函数自己的 docstring**（函数 docstring 只写了 `NumberOfRefPoints` 那条）—— 依据链比同表其它条弱一档。
4. ⚠ **口径本身的不确定**：我把「自建选区」的 20 条归进了「无关」。
   若 Lead 认为「函数碰了选区」就算「读选区」，那「无关」里要划出 20 条「无关·自建」子类，**三个数会变成 真危险 22 / 安全 11 / 无关 35 + 无关·自建 20**。
   ★ 我按**事实 503 的实际后果**（能不能活）分档，而不是按「有没有碰选区」分档。
5. ⚠ **计数口径**：88 = 26 个批次文件的工具声明总数（`ToolSpec(...)` 逐条 + batch58/60 走 `_spec(...)` 工厂的 9 条）。
   ★ `tool_specs_batch58.py` 与 `batch60.py` 的**文件头注释**说「temperature / remote_load 不注册」，
   ★ **但代码里两条都注册了** ⇒ 本表按**代码**（= 注册器实际看到的东西）计。