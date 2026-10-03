# 「要求调用方先选好」族 —— batch1–batch25 全量排查

> ★ 范围：**只扫 `mcp-server/tool_specs_batch1.py` … `tool_specs_batch25.py`**（共 **81** 个 `ToolSpec`）。
> ★ 方法：AST 提取每个 `ToolSpec` 的 `module` / `function` / 有无 `pre_call`（不 import），再逐个回
> `scripts/` 里读**目标函数的 docstring 与函数体**，必要时回 `C:\swapi\types\<接口>\<成员>.md` 读官方 Remarks。
> ★ **没有跑 SolidWorks、没有跑 pytest、没有改任何已有文件。**

---

## 〇、判据与已核实的机制

### 0.1 注册器调用顺序（`mcp-server/tool_registry.py::make_tool_function._impl`，逐字核过）

```python
    inj = effective_inject(spec)
    if inj:
        ...
        kwargs[inject_as or inj] = resolver(params)      # ← 第 1 步：注入解析器
    if spec.extra_op is not None:
        return spec.extra_op(params)
    if spec.pre_call is not None:
        # ⚠ 在**调用目标函数之前**执行（选择类副作用）——
        #   实现里明写「调用前必须先选好」的函数靠它。
        spec.pre_call(params)                            # ← 第 2 步：唯一的「建立选区」窗口
    if spec.derived_args is not None:
        extra = spec.derived_args(params) or {}          # ← 第 3 步：第二个可用窗口
        ...
    mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
    return getattr(mod, spec.function)(**kwargs)         # ← 第 4 步：目标函数
```

⇒ **「声明式 `selection` → 建选区」只有 `pre_call`（第 2 步）与 `derived_args`（第 3 步）两个落点。**
⇒ 两者都没有 ⇒ 该工具在 MCP 表面**没有任何参数**能表达「选哪条边 / 哪个面」。

### 0.2 三档判据（与派活口径一致）

| 档 | 判据 |
|---|---|
| **真危险** | 依赖选区（前置）**且** 没有 `pre_call` / 也没有在 `derived_args` 里建选区 ⇒ 经工具层拿不到 |
| **安全** | 依赖选区 **且** 有 `pre_call`（或 `derived_args → resolve_entity`）⇒ 本仓正确形态 |
| **无关** | 不依赖选区（**含**：自己按名字选、自己清、以及**只回读选区**的工具） |

### 0.3 ★ 两个方向必须分清（本表已按此分档）

- **「要求选区」= 前置**：官方/实现明写「调用前必须先选」「caller must first select」。
- **「返回选区信息」= 回读**：`solidworks_current_selection` / `solidworks_entities_on_body` 读选区**只是为了回话**，
  拿不到选区也只是回 0 条，**不是受害者** ⇒ 归「无关」。

---

## 一、总表（81 条，逐条给依据）

「依据」列给的是**文件 + 可直接 grep 的原文片段**（不含行号）。

### batch1 — 模具 / 拓扑 / 材料（8 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_topology_create_study` | `sw_topology.create_topology_study` | 否 | 否 | 无关 | `scripts/sw_topology.py` 全文无 `SelectionManager` / `GetSelectedObject*`；`create_topology_study` 只接 `sw_app` |
| `solidworks_topology_evidence` | `sw_topology.collect_topology_evidence` | 否 | 否 | 无关 | 同上；纯遍历研究树 |
| `solidworks_topology_run` | `sw_topology.run_topology_study` | 否 | 否 | 无关 | 同上；docstring 原文「Mesh and solve the topology study and report whether results exist」 |
| **`solidworks_mold_parting_line`** | **`sw_mold.insert_parting_line`** | **是（前置）** | **否** | **★真危险** | ① `mcp-server/tool_specs_batch1.py`：doc=「Insert a mold parting line. **Select the draft-direction reference first** (edge/plane/axis); without it the call inserts nothing.」<br>② `scripts/sw_mold.py`：docstring「**调用前须由调用方选好拔模方向参考**（边线/基准面/轴）—— 官方在未选时会返回 None。」<br>③ 官方 `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` 的 Remarks：「**Before calling this method, you must select the direction of pull and the edges for the parting line** by calling IModelDocExtension::SelectByID2 with the following Marks: Direction of pull **1** / Parting line edges **4**」<br>④ 函数体只有 `fm = get_com_member(model, "FeatureManager")` → `InsertMoldPartingLine`，**自己一个实体都不选** |
| `solidworks_mold_shut_off_surface` | `sw_mold.insert_shut_off_surface` | 否 | 否 | 无关 | 官方 `InsertMoldShutOffSurface.md` 全文只有签名与 Returns，**无选区前置**；`sw_mold.py` docstring「无待补孔洞，或未先建分型线」—— 都不涉及选区 |
| `solidworks_mold_draft_analysis` | `sw_mold.mold_draft_analysis` | 否 | 否 | 无关 | 官方 `IModelDoc2/MoldDraftAnalysis.md` 的 Remarks **无任何 SelectByID2 句**；`sw_mold.py` 只写「本函数仍可能弹模态框」（**弹窗 ≠ 选区**，是另一类问题） |
| `solidworks_mold_evidence` | `sw_mold.mold_evidence` | 否 | 否 | 无关 | 纯只读计数；`read_only=True` |
| `solidworks_simulation_set_material` | `sw_simulation.set_material` | 否 | 否 | 无关 | 只写材料库；`sw_simulation.py` 里的 `SelectionManager` 全在 `_disp_array_from_selection` / `selection_count` 两个**载荷族**助手里，与本函数无关 |

### batch2 — 焊件 / 钣金 / 曲面（6 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_weldment_evidence` | `sw_weldment.weldment_evidence` | 否 | 否 | 无关 | `sw_weldment.py` 的 `ClearSelection2(True)` 只出现在 `create_structural_weldment`（**未挂**）；`weldment_evidence` 只读切割清单 |
| `solidworks_weldment_ensure_cut_list` | `sw_weldment.ensure_cut_list` | 否 | 否 | 无关 | 同上 |
| `solidworks_weldment_update_cut_list` | `sw_weldment.update_cut_list` | 否 | 否 | 无关 | 同上 |
| `solidworks_weldment_create_sub_weld_folder` | `sw_weldment.create_sub_weld_folder` | 否 | 否 | 无关 | 同上 |
| `solidworks_sheet_metal_evidence` | `sw_sheet_metal.sheet_metal_evidence` | 否 | 否 | 无关 | 只读厚度 / 弯曲半径 / 展开状态 |
| `solidworks_surface_evidence` | `sw_surface.collect_surface_evidence` | 否 | 否 | 无关 | `sw_surface.py` 里的 `GetSelectedObject6` **只出现在模块头注释**（官方示例摘录），不在函数体 |

### batch3 — 钣金基体法兰 / 单折弯（2 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_sheet_metal_create_base_flange` | `sw_sheet_metal.create_base_flange` | 否（**自选**） | 否 | 无关（⚠条件性） | `sw_sheet_metal.py` 的 `create_base_flange(model, sketch_ref, spec)` 把 `sketch_ref` 交给 `sw_part._ensure_sketch_selected` —— **能力层自己按名字选**。⚠ 但 `scripts/sw_part.py::_ensure_sketch_selected` 第一行是「`if str(sketch_name) == "__current_selection__" and _get_selection_count(model) > 0: return "__current_selection__"`」⇒ **`sketch_name="__current_selection__"` 是条件性受害者**（见 §三） |
| `solidworks_sheet_metal_create_one_bend` | `sw_sheet_metal.create_one_bend` | 否（自选） | 否 | 无关（⚠条件性） | 同上（`sketch_ref` → `_ensure_sketch_selected`） |

### batch4 — 钣金边法兰 / 加强筋 / 拔模 / 扫掠（4 条）★ **本批是「正确形态」的样板**

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_sheet_metal_create_edge_flange` | `sw_sheet_metal.create_edge_flange` | **是（前置）** | **是**（`pre_call=_pre_edge_flange`） | **安全** | `scripts/sw_sheet_metal.py` docstring：「**调用前必须先用 ``sw_part._select_by_id`` 把目标边选入选区。**」；来源块另有「⚠ 边集合由调用方在创建前用 SelectByID2 选好；**本函数不代为选边**」。`tool_specs_batch4.py` 的 `_pre_edge_flange` → `resolve_selection(_model(), params.selection, "EDGE")` |
| `solidworks_sheet_metal_create_gusset` | `sw_sheet_metal.create_gusset` | **是（前置）** | **是**（`pre_call=_pre_gusset`） | **安全** | `sw_sheet_metal.py` 来源块：「⚠ **支撑面须由调用方先用 SelectByID2 选好；本函数不代为选面。**」；docstring「在已选中的支撑面区域创建原生钣金加强筋」。`_pre_gusset` → `resolve_selection(..., "FACE")` |
| `solidworks_sheet_metal_create_draft` | `sw_sheet_metal.create_draft` | **是（前置）** | **是**（`pre_call=_pre_draft`） | **安全** | `sw_sheet_metal.py` docstring：「在**已选中的**面上创建原生拔模特征。」；`_pre_draft` → `resolve_selection(..., "FACE")` |
| `solidworks_sheet_metal_create_swept_flange` | `sw_sheet_metal.create_swept_flange` | 是（但**自己解析成对象**） | 否（走 `derived_args`） | **安全**（★非 `pre_call` 形态） | `sw_sheet_metal.py` docstring：「官方示例用 ``SelectByRay`` 选边后 ``SelectionManager.GetSelectedObject6(1, -1)`` 取得」—— 但**工具层不等它**：`tool_specs_batch4.py::_swept_refs_and_spec` 在 `derived_args` 里直接 `resolve_entity(model, p.path_selection, "EDGE")` / `resolve_entity(..., "SKETCH")` 把**对象**塞进 `data.Path` / `data.Profile` ⇒ 选区不必活到第 4 步 |

### batch5–8 — 只读 / 视图 / 模具补挂（14 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_current_selection` | `sw_selection_spec.current_selection` | **是（回读方向）** | 否 | **无关** | ★ **本表最容易误判的一条**：`scripts/sw_selection_spec.py` 的 docstring 是「把**当前选区**取成对象列表」，但它是**回读工具**（`tool_specs_batch5.py` doc=「Read the current selection set」）⇒ 拿不到选区只是回空列表，**不是受害者** |
| `solidworks_clear_selection` | `sw_selection_spec.clear_selection` | 否（**清**选区） | 否 | 无关 | `sw_selection_spec.py::clear_selection` → `ClearSelection2` |
| `solidworks_set_standard_view` | `sw_review.set_standard_view` | 否 | 否 | 无关 | 官方 `IModelDoc2.ShowNamedView2` |
| `solidworks_list_render_materials` | `sw_render_material.list_render_materials` | 否 | 否 | 无关 | `sw_render_material.py` 无选区调用 |
| `solidworks_collect_appearance_evidence` | `sw_render_material.collect_appearance_evidence` | 否 | 否 | 无关 | 同上 |
| `solidworks_available_point_selectors` | `sw_geometry_selectors.available_point_selectors` | 否 | 否 | 无关 | 无参纯数据（`inject` 为空） |
| `solidworks_available_direction_selectors` | `sw_geometry_selectors.available_direction_selectors` | 否 | 否 | 无关 | 同上 |
| `solidworks_collect_assembly_bom` | `sw_delivery.collect_assembly_bom` | 否 | 否 | 无关 | `sw_delivery.py` 无选区调用 |
| `solidworks_activate_model_for_preview` | `sw_review.activate_model_for_preview` | 否 | 否 | 无关 | `sw_review.py::activate_model_for_preview` 只做 `GetTitle` + `ActivateDoc3` |
| `solidworks_clear_selection_for_preview` | `sw_review.clear_selection_for_preview` | 否（**清**选区） | 否 | 无关 | `sw_review.py::clear_selection_for_preview`：`get_com_member(model, "ClearSelection2", True)`，注释「清除选择高亮并重绘」 |
| `solidworks_refresh_scene_graph` | `sw_render_material.refresh_scene_graph` | 否 | 否 | 无关 | 图形刷新 |
| `solidworks_collect_model_summary` | `sw_review.collect_model_summary` | 否 | 否 | 无关 | 遍历特征树 |
| `solidworks_get_costing_manager` | `sw_costing.get_costing_manager` | 否 | 否 | 无关 | 取 Costing 管理器 |
| `solidworks_list_simulation_study_options` | `sw_simulation_study_options.list_setter_summary` | 否 | 否 | 无关 | 无参纯数据 |

### batch9 — 模具型芯/型腔 · 分型面 · 底切（3 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_mold_core_cavity_split` | `sw_mold.insert_core_cavity_solids` | 否 | 否 | 无关 | 官方 `InsertMoldCoreCavitySolids.md` 的 Remarks 列出四条前置（须有分型线 / 分型面 / 已分离 / 须有块草图）—— **全是「模型里已存在什么」，没有一条是选区** |
| **`solidworks_mold_parting_surface`** | **`sw_mold.insert_parting_surface`** | **是（有条件前置）** | **否** | **★真危险** | ① 官方 `C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md` 的 Remarks：「**f a parting line feature does not yet exist in the model, you must first select the direction of pull and the edges for the parting line** using IModelDocExtension::SelectByID2. For example, a face (direction of pull) has a mark of **1** and edges (parting lines) a mark of **4**.」<br>② `scripts/sw_mold.py` docstring：「:raises RuntimeError: 返回 None（常见原因：未先建分型线，**或未选面**）。」<br>③ 函数体只透传 8 个参数，**自己一个实体都不选** |
| `solidworks_mold_undercut_detect` | `sw_mold.mold_undercut_detect` | 否 | 否 | 无关 | 官方 `MoldUndercutDetect.md` 的 Parameters 全是「No description」；方向由 `Dx/Dy/Dz` 显式给（`sw_mold.py`：「默认 b_coord_input=True + 非零方向 (0,0,1) ⇒ **不依赖模型已定义方向**」）⇒ 不读选区（**但会弹模态框**，是另一类问题） |

### batch10 — 包围盒 / 孔标准（4 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_part_bounding_box` | `sw_part.get_bounding_box` | 否 | 否 | 无关 | 走 `IBody2.GetBodyBox` |
| `solidworks_hole_standards` | `sw_hole_features.list_hole_standards` | 否 | 否 | 无关 | 首参是 `sw`（不是 `model`）⇒ 根本拿不到文档，选区无从谈起 |
| `solidworks_fastener_types` | `sw_hole_features.list_fastener_types` | 否 | 否 | 无关 | 同上 |
| `solidworks_fastener_table_types` | `sw_hole_features.list_fastener_table_types` | 否 | 否 | 无关 | 同上（`sw_hole_features.py` 里的 `GetSelectedObjectCount2` 全在 `_point_from_selection` 与孔向导报告里，与这三个纯列表函数无关） |

### batch11 — 拓扑约束 / 控制（4 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_topology_create_mass_constraint` | `sw_topology.create_mass_constraint` | 否 | 否 | 无关 | `_edit` 里只设 `SetMassPreference` / `SetValue` |
| `solidworks_topology_create_factor_of_safety_constraint` | `sw_topology.create_factor_of_safety_constraint` | 否 | 否 | 无关 | 同族，只设属性 |
| **`solidworks_topology_create_preserved_region`** | **`sw_topology.create_preserved_region`** | **是（前置）** | **否** | **★真危险** | ① `scripts/sw_topology.py` docstring：「⚑ **调用方须先选好要保留的面再调本函数** —— `ICWTopologyPreservedRegionControl` 的 `SelectFaces(Object)` 接受实体数组，但既有模式（`sw_simulation`）是用**选区**而非数组，本模块沿用该模式，**故本函数不接受面参数**：由调用方选好再调。」<br>② ★ `tool_specs_batch11.py` 的 doc **只字未提这条前置**（「Create a preserved region for a topology study (material that must not be removed).」）—— **比 demold/symmetry 更隐蔽**<br>③ 函数体只有 `CreatePreservedRegionControl` + `SetIncludeRegionDepth2`，**自己一个面都不选** |
| `solidworks_topology_create_thickness_control` | `sw_topology.create_thickness_control` | 否 | 否 | 无关 | 只设最小/最大成员尺寸 |

### batch12 — 拓扑脱模 / 应力 / 对称（3 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| **`solidworks_topology_create_demold_control`** | **`sw_topology.create_demold_control`** | **是（前置）** | **否** | **★真危险** | ① `scripts/sw_topology.py` docstring：「建脱模控制（制造约束）。**调用方须先选好拔模方向的面/边/基准面。**」<br>② `tool_specs_batch12.py` 的 doc 也写了：「The caller **must first select** the pull-direction face/edge/plane, then choose the direction option.」<br>③ 函数体只有 `CreateDemoldControl` + `SelectDemoldDirection`，**自己不选** |
| `solidworks_topology_create_stress_constraint` | `sw_topology.create_stress_constraint` | 否 | 否 | 无关 | 只设 `SetComparator` / `SetValue` |
| **`solidworks_topology_create_symmetry_control`** | **`sw_topology.create_symmetry_control`** | **是（前置）** | **否** | **★真危险** | ① `scripts/sw_topology.py` docstring：「建对称控制（官方教程用 1/4 对称）。**调用方须先选好对称平面。**」<br>② `tool_specs_batch12.py` 的 doc：「The caller **must first select** the symmetry plane(s).」<br>③ 函数体只有 `CreateSymmetryControl` + `SelectSymmetryType`，**自己不选** |

### batch13 — 仿真报告 / 网格（3 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_simulation_generate_report` | `sw_simulation_study.generate_report` | 否 | 否 | 无关 | 透传 `GenerateReport(template, path, append)` |
| `solidworks_simulation_create_mesh_for_control` | `sw_simulation_study.create_mesh_for_control` | 否 | 否 | 无关 | 按 `control_name` 划网格；`sw_simulation_study.py` 里的 `SelectionManager` **只在模块头的成员对照表注释里** |
| `solidworks_simulation_default_element_size_and_tolerance` | `sw_simulation.default_element_size_and_tolerance` | 否 | 否 | 无关 | 官方建议尺寸 |

### batch14–15 — 视图 / 体上实体 / 审查报告（3 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_get_active_view` | `sw_view.get_active_view` | 否 | 否 | 无关 | 官方 `IModelDoc.ActiveView` |
| `solidworks_entities_on_body` | `sw_selection_spec.entities_on_body` | **是（回读方向）** | 否 | **无关** | ★ 同 `current_selection`：**枚举体上的实体**（`IBody2.GetEdges/GetFaces/GetVertices`），与「当前选区」是两回事；`tool_specs_batch14.py` 也明写「Index order is NOT promised stable by the official API」 |
| `solidworks_build_review_report` | `sw_review.build_review_report` | 否 | 否 | 无关 | `sw_review.py::build_review_report` 只做 `ForceRebuild3` / `zoom_to_fit` / `save_review_previews` / `collect_model_summary` |

### batch16 — 草图关系 / 镜像（2 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| **`solidworks_add_sketch_relation`** | **`sw_part.add_sketch_relation`** | **是（前置）** | **否** | **★真危险** | ① 官方 `C:\swapi\types\IModelDoc2\SketchAddConstraints.md` 首句：「**Adds the specified constraint to the selected entities.**」<br>② `tool_specs_batch16.py` 的 doc 也写了：「Add a sketch geometric relation to **the current selection**.」<br>③ `scripts/sw_part.py::add_sketch_relation` 函数体只有一句 `return model.SketchAddConstraints(relation_type)` ⇒ **Python 体一个实体都不读，但官方 API 隐式吃选区** ⇒ 这类**最隐蔽**（没有任何报错线索） |
| `solidworks_mirror_feature` | `sw_part.mirror_feature` | 否（**自选**） | 否 | 无关 | `sw_part.py::mirror_feature` 自己按 mark 建选区：「`_select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=1)`」+「`_select_by_id(..., "PLANE", append=True, mark=2)`」 |

### batch17 — 圆形阵列 / 旋转凸台（2 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_circular_pattern` | `sw_part.circular_pattern` | 否（**自选**） | 否 | 无关 | `sw_part.py::circular_pattern` 开头两行就是 `_select_by_id(..., "BODYFEATURE", mark=4)` + `_select_by_id(..., "AXIS", append=True, mark=1)` |
| `solidworks_revolve_boss` | `sw_part.revolve_boss` | 否（**自选**） | 否 | 无关（⚠条件性） | `sw_part.py::revolve_boss` 开头「**先轴、后轮廓**（★ 顺序照官方示例 —— 反了会建不成）」：`if axis_sketch_name: _select_revolve_axis(...)` + `_ensure_sketch_selected(model, sketch_name)` ⇒ **自选**。⚠ 但 `sketch_name="__current_selection__"` 时走 `_ensure_sketch_selected` 的第一行 ⇒ 条件性受害者（见 §三） |

### batch18 — 草图只读计数（4 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_sketch_count_lines` | `sw_sketch.count_lines` | 否 | 否 | 无关 | 对象由 `derived_args` 的 `resolve_sketch(model, name)` 取；不碰选区 |
| `solidworks_sketch_count_arcs` | `sw_sketch.count_arcs` | 否 | 否 | 无关 | 同上 |
| `solidworks_sketch_count_segments` | `sw_sketch.count_segments` | 否 | 否 | 无关 | 同上 |
| `solidworks_sketch_is_3d` | `sw_sketch.is_3d_sketch` | 否 | 否 | 无关 | 同上 |

### batch19–20 — 工程图读数 / 自定义属性（5 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_drawing_list_sheets` | `sw_drawing_query.sheets_summary` | 否 | 否 | 无关 | 官方 `GetCurrentSheet` / `GetSheetCount` |
| `solidworks_drawing_get_current_sheet` | `sw_drawing_query.current_sheet_info` | 否 | 否 | 无关 | 官方 `ISheet.GetProperties2` |
| `solidworks_drawing_list_views` | `sw_drawing_query.list_views` | 否 | 否 | 无关 | 官方 `GetFirstView` / `GetNextView` |
| `solidworks_custom_property_get` | `sw_custom_property.custom_property` | 否 | 否 | 无关 | `IModelDocExtension.CustomPropertyManager` |
| `solidworks_custom_property_list` | `sw_custom_property.custom_properties` | 否 | 否 | 无关 | 同上 |

### batch21 — 建草图 + 画几何（5 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_sketch_start` | `sw_part.start_sketch` | 否（**先清后自选**） | 否 | 无关 | `sw_part.py::start_sketch` 第一行就是 `model.ClearSelection2(True)`，随后 `_select_first_candidate(..., "PLANE")` 按名字选基准面 |
| `solidworks_sketch_end` | `sw_part.end_sketch` | 否 | 否 | 无关 | `_capture_sketch_ref` + `InsertSketch(True)` |
| `solidworks_sketch_add_line` | `sw_part.sketch_line` | 否 | 否 | 无关 | `model.SketchManager.CreateLine(x1, y1, 0, x2, y2, 0)` —— 走**打开中的草图**，不碰选区 |
| `solidworks_sketch_add_circle` | `sw_part.sketch_circle` | 否 | 否 | 无关 | `CreateCircleByRadius` |
| `solidworks_sketch_add_rectangle` | `sw_part.sketch_corner_rectangle` | 否 | 否 | 无关 | `CreateCornerRectangle` |

### batch22–25 — 拉伸 / 倒角圆角 / 质量 / 装配（9 条）

| 工具名 | module.function | 读选区? | 有 pre_call? | 档位 | 依据 |
|---|---|---|---|---|---|
| `solidworks_extrude_boss` | `sw_part.extrude_boss` | 否（自选） | 否 | 无关（⚠条件性） | `sw_part.py::extrude_boss` 调 `_ensure_sketch_selected(model, sketch_name)` **自己选草图**；⚠ `sketch_name="__current_selection__"` 时走 `_ensure_sketch_selected` 的首行判定 |
| `solidworks_extrude_cut` | `sw_part.extrude_cut` | 否（自选） | 否 | 无关（⚠条件性） | 同上（`_ensure_sketch_selected` + `FeatureCut4`） |
| `solidworks_extrude_midplane` | `sw_part.extrude_midplane` | 否（自选） | 否 | 无关（⚠条件性） | 同上 |
| `solidworks_chamfer` | `sw_part.chamfer` | **是（前置）** | **是**（`pre_call=_select_edge`） | **安全** | ① `tool_specs_batch22.py` 批头逐字：「★ `chamfer`……**它没有 `edges` 参数** ⇒ 倒哪些边必然来自**当前选择**」<br>② `sw_part.py::chamfer` 函数体只有 `model.FeatureManager.InsertFeatureChamfer(4, 1, distance, angle_rad, 0,0,0,0)`，**edges 传不下去**<br>③ `tool_specs_batch23.py::_select_edge` → `resolve_selection(_model(), params.selection, "EDGE")` |
| `solidworks_fillet` | `sw_part.fillet` | **是（前置）** | **是**（`pre_call=_select_edge`） | **安全** | ① `sw_part.py::fillet` docstring：「**edges: 预先选择的边线列表，None 则使用当前选择**」，函数体 `FeatureFillet(195, radius, 0, 0, None, None, None)` ⇒ 三个对象参数全是 `None`<br>② 官方 `C:\swapi\types\IFeatureManager\FeatureFillet.md` 的 Remarks：「**Call IModelDocExtension::SelectByID2 with Mark = 1 to select the edges to fillet.**」<br>③ `pre_call=_select_edge` |
| `solidworks_part_mass_properties` | `sw_mass_property.mass_properties` | 否 | 否 | 无关 | `model.Extension.CreateMassProperty`（属性形态） |
| `solidworks_assembly_list_components` | `sw_assembly.get_components` | 否 | 否 | 无关 | 遍历组件 |
| `solidworks_assembly_list_mates` | `sw_assembly.collect_mate_feature_summary` | 否 | 否 | 无关 | 遍历 MateGroup |
| `solidworks_assembly_check_interference` | `sw_assembly.get_interference_detection` | 否 | 否 | 无关 | `InterferenceDetectionManager.GetInterferences()`；★ `sw_assembly.py` 里的 `GetSelectedObjectCount2` 在 `select_entities_for_mate` / `add_mate5_checked`（**batch25 没挂这两个**） |

---

## 二、统计

| 档位 | 条数 | 工具 |
|---|---|---|
| **★ 真危险** | **6** | `mold_parting_line` · `mold_parting_surface` · `topology_create_preserved_region` · `topology_create_symmetry_control` · `topology_create_demold_control` · `add_sketch_relation` |
| **安全** | **6** | `sheet_metal_create_edge_flange` · `sheet_metal_create_gusset` · `sheet_metal_create_draft` · `sheet_metal_create_swept_flange` · `chamfer` · `fillet` |
| **无关** | **69** | 其余全部（见 §一各表） |
| 合计 | **81** | batch1–batch25 |

★ 其中「无关」里有 **7 条带 ⚠ 条件性**（见 §三），**真危险**里有 **1 条是条件触发**（`mold_parting_surface`）。
⇒ 若把「条件性」也算进去，受影响面是 **13 条**，但**无条件失败**的只有 **5 条**。

---

## 三、⚠ 条件性：靠 `__current_selection__` 拿选区的那 7 条

这 7 条**不在**真危险档（它们平时靠传**名字**自选，能跑），但一旦传 `__current_selection__` 就与真危险同型。
共同根因在 `scripts/sw_part.py::_ensure_sketch_selected` 的**第一行**：

```python
    if str(sketch_name) == "__current_selection__" and _get_selection_count(model) > 0:
        return "__current_selection__"
```

⇒ 它**只检查、只使用**，**从不自己建立**选区 ⇒ 选区必须活到第 4 步。

| 工具 | 暴露的参数字面 |
|---|---|
| `solidworks_sheet_metal_create_base_flange` | `sketch_name` 的描述逐字：「The special value `'__current_selection__'` reuses the current selection instead of selecting by name.」 |
| `solidworks_sheet_metal_create_one_bend` | 同上 |
| `solidworks_extrude_boss` | `_SKETCH` 常量里的 `sketch_name` |
| `solidworks_extrude_cut` | 同上 |
| `solidworks_extrude_midplane` | 同上 |
| `solidworks_revolve_boss` | `sketch_name`（`axis_sketch_name` 空串已被 `derived_args` 归一成 `None`，**不构成第二条路**） |

（另：`solidworks_sheet_metal_create_swept_flange` 的 `path_selection` / `profile_selection` 也接受
`__current_selection__`，但它走 `derived_args → resolve_entity`，后者**选不中就抛 `EntitySelectionError`**
（原文：「选择器是 %r，但当前**没有任何选中项**」）⇒ **失败可见**，不归这一档。）

---

## 四、真危险 6 条：按「最可能拿到选区的方式」排序 + 建议

排序判据：**① 需要的实体类型能不能被现成的 `sw_selection_spec.resolve_selection(model, sel, kind)` 覆盖
（它的 `kind` 只有 `EDGE` / `FACE` / `VERTEX` 三种，见 `ENTITY_KINDS`）；② 需不需要多选 / 对象数组；
③ 有没有现成的 `pre_call` 样板可照抄（`tool_specs_batch23.py::_select_edge`）。**

| 排序 | 工具 | 需要的选区（官方 mark） | 现成手段 | 建议 |
|---|---|---|---|---|
| **1** | `solidworks_mold_parting_line` | 拔模方向面/边/基准面（**mark 1**）+ 分型线**边**（**mark 4**） | ✅ `EDGE` + `FACE` **两种 kind 现成** | ★ **最容易**：照 `batch23::_select_edge` 抄一个 `_pre_parting_line`，连做两次 `resolve_selection`（第二次 `append`）。两个 mark 都有官方原文 |
| **2** | `solidworks_add_sketch_relation` | **草图图元**（线/圆/点），数量不定 | ⚠ `EDGE`/`FACE`/`VERTEX` **都不覆盖草图段** | 草图**打开时**对象来源现成（`sw_sketch` 有段枚举）⇒ 只需给 `resolve_selection` 加第四种 kind（按 `sw_sketch` 的段逐个 `Select4`）。工作量小，但要动公共底座 |
| **3** | `solidworks_mold_parting_surface` | 与第 1 条**完全同形**（mark 1 面 + mark 4 边） | ✅ 同上 | ★ **可与第 1 条共用同一个 `pre_call`**；只是**触发条件窄**（模型里还没有分型线时）⇒ 优先级排在第 1 条之后，但**修第 1 条时顺手一起改**成本最低 |
| **4** | `solidworks_topology_create_demold_control` | 拔模方向的**面 / 边 / 基准面** | ⚠ `FACE` 现成，**基准面（PLANE）不在三种 kind 里** | 需要 `resolve_selection` 支持 PLANE（或允许 `__current_selection__` + 回读计数）。★ 另外 `tool_specs_batch12.py` 的 doc **已经写了前置却没实现** ⇒ 属「说了没做」，比第 1 条更难解释 |
| **5** | `solidworks_topology_create_symmetry_control` | **对称平面**（几乎总是基准面 PLANE） | ❌ `PLANE` 完全没有 kind | 同第 4 条，且**几乎只可能是 PLANE** ⇒ 对底座的要求更单一也更硬 ⇒ 排在第 4 条后 |
| **6** | `solidworks_topology_create_preserved_region` | **面数组**（`ICWTopologyPreservedRegionControl.SelectFaces(Object)` 接受实体数组） | ❌ `resolve_selection` **一次只解决一个实体** | ★ **工作量最大**：要「多选 + 取对象数组」的新底座；而且 ★ **本条的工具 doc 连前置都没写**（`batch11`）⇒ 补的时候**必须先改 doc**，否则调用方根本不知道要先选 |

### 通用建议（三条，按性价比）

1. **★ 先做 1 + 3**：两条共用一个 `pre_call`，`kind` 现成，官方 mark 现成 ⇒ 一次改动修两条。
2. **★ 补一条静态门禁**：现状是「只有 `batch4` / `batch23` 记得写 `pre_call`」。
   ★ 现成判据可以照 `mcp-server/tool_registry.py::check_spec` 的形态写一条新门禁：
   **当 spec 的 `doc`（或目标函数 docstring）含「调用前/先选/caller must first select/the selected entities」
   且 `pre_call is None and derived_args is None` ⇒ 报。**
   ★ 这条门禁**一次就会抓住本表的 6 条真危险**（`preserved_region` 抓不到——它 doc 没写 ⇒ 说明**还要反向查能力层 docstring**，
   而能力层 docstring 与 spec 的 doc 不同源这件事本身就该记一条）。
3. **★ `derived_args` 与 `pre_call` 二选一就够**：`swept_flange` 证明「在 `derived_args` 里把选区解析成**对象**塞进实参」
   同样能绕开选区存活问题 ⇒ 对「只需要一个实体」的族，**用对象比用选区更稳**（选区还要活到第 4 步，对象不用）。

---

## 五、拿不准 / 需要别人裁的地方（如实写，不猜）

1. **★ 事实 503 的「解析器会清空选区」这半句，我在当前树上没能静态证实。**
   ★ 已逐个核过第 1 步会经过的三处，**都没有 `ClearSelection2`**：
   · `mcp-server/register_capabilities.py::resolve_model` / `resolve_sw_app` / `resolve_study` ⇒ 都只调 `_connect()`
   · `mcp-server/register_capabilities.py::_connect` ⇒ `scripts/sw_connect.py::connect_solidworks`
     —— 该函数体内**没有** `ClearSelection2` / `SelectionManager`（`grep -n "ClearSelection|SelectionManager" scripts/sw_connect.py` ⇒ **0 命中**）；
     它走的是 `GetActiveObject` → `_LaunchGuard` → `_read_active_document(sw)`
   · `mcp-server/server.py::_run_locked` ⇒ 只做 `_load_automation_modules()`（`importlib.import_module` 列表）与
     `pythoncom.CoInitialize()`，**两者都不碰文档**
   ⇒ ★ **所以「顺序」这半句成立、「必被清空」这半句在静态上不成立。** 这**不影响本表的分档**：
   决定性的事实是「**没有 `pre_call` / `derived_args` ⇒ MCP 表面根本没有表达『选哪个』的参数**」，
   这与解析器是否清空无关。★ 但若要写进正式报告，**这一句要么补真机证据，要么按静态结论改写。**

2. **`InsertFeatureChamfer` 的官方 Remarks 里没有「先选边」的句子**（我读了 `C:\swapi\types\IFeatureManager\InsertFeatureChamfer.md` 全文）。
   ★ `chamfer` 归「安全」靠的是**两条间接证据**：`tool_specs_batch22.py` 批头的逐字判断
   「它没有 `edges` 参数 ⇒ 倒哪些边必然来自当前选择」＋ 函数体 8 个参数里**没有任何边数组**。
   ⇒ 与 `FeatureFillet`（官方 Remarks 逐字写了「Call SelectByID2 with Mark = 1」）**证据强度不同**，如需对齐请标注。

3. **`solidworks_mold_draft_analysis` 与 `solidworks_mold_undercut_detect` 会弹模态框**（`sw_mold.py` 自述：
   「本函数仍可能弹模态框（与 `MoldUndercutDetect` 同族）：未定义拔模方向 / 无实体时官方会弹「此拔模方向尚未定义。」」）。
   ★ 那**不是选区问题**，但它与事实 503 是**同一族「工具层拿不到工具需要的前置状态」**。
   ⇒ 我**没有**把它们算进本表任何一档的「真危险」；若派活的口径要把「拿不到任何前置」也算进去，这两条要**另立一档**。

4. **拓扑那三条（`preserved_region` / `symmetry` / `demold`）的「先选」只有能力层 docstring 作证**，
   `C:\swapi\` 下**检索不到** `CreateSymmetryControl` / `CreateDemoldControl` / `CreatePreservedRegionControl` 的 md
   （`Get-ChildItem C:\swapi -Recurse -Filter *.md | Select-String "CreateSymmetryControl|CreateDemoldControl|CreatePreservedRegionControl"`
   ⇒ **0 命中**）⇒ 按铁律 5 记「**官方两源查不到**」，依据只到能力层 docstring 这一层。

5. **`solidworks_current_selection` / `solidworks_entities_on_body` 我判「无关」**，理由是「回读方向 ≠ 前置方向」。
   ⇒ 若派活口径把「函数体里读选区」一律算「读选区?＝是」，这两条的「读选区?」列应填**是**、但**档位仍是无关**。

6. **范围边界**：本表只覆盖 `tool_specs_batch1..25`。★ `batch26`–`batch76` 未扫（另有他路负责）。
   ★ 另：`mcp-server/server.py` 里**手写**的 ~45 个 `@mcp.tool`（不走 `ToolSpec`）**也不在本表** ——
   按机制它们不受 `make_tool_function` 支配（没有 resolver→pre_call 这个顺序问题）。
