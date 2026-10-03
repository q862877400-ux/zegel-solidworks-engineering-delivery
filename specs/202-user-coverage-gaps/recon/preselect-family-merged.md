# 「要求调用方先选」工具族 —— ★ 三路合并总表（唯一总表）

> ★ **本文件是唯一总表**：`preselect-family-a.md`（batch1–25 · 81 条）/ `-b.md`（batch26–50 · 108 条）/
> `-c.md`（batch51–76 · 88 条）三路的**并集**，并补齐三路合计**一条不丢**的全部 ToolSpec。
> ★ 合并者 + 复核者；★ 已对「真危险」那批**逐条独立复核**（spec 侧 + 函数侧 + 官方页）。
> ★ **没有跑 SolidWorks、没有跑 pytest、没有改任何已有文件。**

## 〇、机制前提（复核者逐字核过，不是转述）

`mcp-server/tool_registry.py::make_tool_function._impl` 的调用序（★ 行号为本轮 grep 实测）：

```
507:  kwargs[inject_as or inj] = resolver(params)   ← 第 1 步：注入解析器
508:  if spec.extra_op is not None: return spec.extra_op(params)
510:  if spec.pre_call is not None:
513:      spec.pre_call(params)                    ← 第 2 步：唯一的「建立选区」钩子
514:  if spec.derived_args is not None:
516:      extra = spec.derived_args(params) or {}  ← 第 3 步：第二个可用窗口
524:  mod = __import__("scripts.%s" % spec.module, …)
525:  return getattr(mod, spec.function)(**kwargs) ← 第 4 步：目标函数
```

⇒ **「声明式 selection → 建选区」只有 `pre_call`（第 2 步）与 `derived_args`（第 3 步）两个落点。**
⇒ 两者都没有 ⇒ 该工具在 MCP 表面**没有任何参数**能表达「选哪个实体」。

### ★ 全仓 `pre_call` 盘点（AST 实测，非转述）

★ **全仓 277 条 ToolSpec 里只有 22 条挂了 `pre_call`**，`pre_call` 实现只有 6 个：
`_pre_draft` / `_pre_edge_flange` / `_pre_gusset`（batch4）· `_select_edge`（batch23）·
`_select_face`（batch26/29/58/60）· `_select_faces_for`（batch74）。
★ 另有 **1 条**走 `derived_args` 形态（batch4 的 `swept_flange`）。

### ★ 事实 503「`RESOLVERS` 会清空选区」—— 本轮找到了真机证据文件

★ A 路在其 §五.1 写「**『必被清空』这半句在静态上不成立**」。**本轮复核认为该保留为存疑的只有静态路径，真机路径已有证据**：

`D:\AI\SW\output\selection-lifetime-evidence.json`（`at: 2026-10-03 22:27:11`）逐步记录：
```
选 2 个面 mark=1（刚选完）      mark1 = 2  ✔
…（读 feature_names / GetBodies2 / GetFaces / FeatureManager / SelectionManager 都不掉）
调过 RESOLVERS['model'] 之后     mark1 = 0  ← ★ 这里被清掉
```
⇒ ★ 「顺序」与「必被清空」**两半都成立**（静态证不出是**因为清空发生在 `connect_solidworks()` 内部**，不在解析器那一行）。

### 分档口径（本轮统一，三路原本不一致）

| 档 | 判据 |
|---|---|
| **安全** | 读选区 ＋ 有 `pre_call`（或 `derived_args → resolve_entity`）⇒ 选区在 inject **之后**建立，能活到第 4 步 |
| **真危险·官方前置** | 官方 Remarks/描述行明写「调用前必须先选」＋ 函数体**不读**选区（选区由 SolidWorks 自己吃）⇒ 缺选区时**静默失败**（返回 None / 无树增量），最隐蔽 |
| **真危险·显式拒** | 函数体自己 `GetSelectedObjectCount2` ＋ 计数为 0 时 `return {"ok": False, "stage": "selection"}` ⇒ 经工具层**必然失败**、失败可见 |
| **真危险·诊断型** | 只读工具，读的就是那个被清空的选区 ⇒ 经工具层**恒回 0**；它不是受害者，是**受害者链的源头** |
| **真危险·条件** | 前置只对某些参数取值成立 |
| **真危险·软失败** | 前置是真的，但代码**不硬拒**：只把 `preconditions_held: False` 写进返回值后**仍然调** |
| **无关** | 不读选区（自建 / 按名选 / 清选区 / 只读遍历 / 纯数据），**或**官方明示可降级、或有回退路径 |

★ **三路口径原本打架的地方（已统一）**：
① A 路把 `solidworks_current_selection` 判「无关（回读方向）」，C 路把同族的
`solidworks_selection_count` / `resolve_selection` / `selection_point` / `resolve_entity` 判「真危险」。
★ 本轮按**同一条判据**统一为「真危险·诊断型」（5 条），并把 `current_selection` 计入（见 §三-改正 1）。
② A 路把 `solidworks_entities_on_body` 判「无关」——★ **这一条是对的**：复核确认它走
`GetBodies2` ＋ `IBody2.GetEdges/GetFaces/GetVertices` 按序号枚举，**完全不碰当前选区**（见总表依据列）。

### ★ 待补依据的判法

★ 凡**给不出可搜索原文片段**的，一律标 **待补依据**，★ 不替它编。
本轮标 **5 条**（见总表 `依据` 列末的「★ 官方依据缺失」/「依据链弱一档」）：
★ 拓扑三条（`CreateSymmetryControl` / `CreateDemoldControl` / `CreatePreservedRegionControl`）
在 `C:\swapi` 下检索**全部 0 命中**（本轮已重跑该检索）；
★ 钣金斜接法兰 / 钣金闭合角两条的官方页**无 `## Remarks` 段**（本轮已逐页核过），
能力层自己就把 `preconditions_held` 如实报成 `None`；
★ 基准点那一条的官方 `## Remarks` **只有 `NumberOfRefPoints` 那句、没有选区句**。
另：`IProfileCenterMateData` 在 `C:\swapi` 下亦**无命中** ⇒ 焊件型材中心配合的**官方 mark 无法引用**。

---

## 一、总表（277 条，按工具名排序；★ 三路并集，一条不丢）

★ 「依据」列给的是**文件 + 可直接 grep 的原文片段**（不含行号）。
★ 「路」列 = 该条出自哪一路候选（A/B/C）；`—` = 本轮补录（三路都没写）。

| # | 工具名 | batch | module.function | 读选区 | pre_call | 档位 | 路 | 依据（可 grep 原文片段） |
|---|---|---|---|---|---|---|---|---|
| 1 | `solidworks_activate_model_for_preview` | b7 | `sw_review.activate_model_for_preview` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 2 | `solidworks_add_dimension` | b56 | `sw_part.add_dimension_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 3 | `solidworks_add_sketch_relation` | b16 | `sw_part.add_sketch_relation` | 是 | 否 | 真危险·官方前置 | A | `C:\swapi\types\IModelDoc2\SketchAddConstraints.md` **描述行**逐字：「Adds the specified constraint to the selected entities.」；`sw_part.py::add_sketch_relation` 函数体只有一句 `return model.SketchAddConstraints(relation_type)` ⇒ Python 体一个实体都不读，官方 API 隐式吃选区（★ 最隐蔽：没有任何报错线索） |
| 4 | `solidworks_assembly_check_interference` | b25 | `sw_assembly.get_interference_detection` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 5 | `solidworks_assembly_list_components` | b25 | `sw_assembly.get_components` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 6 | `solidworks_assembly_list_mates` | b25 | `sw_assembly.collect_mate_feature_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 7 | `solidworks_auto_dimension_sketch` | b55 | `sw_part.auto_dimension_sketch` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 8 | `solidworks_available_direction_selectors` | b6 | `sw_geometry_selectors.available_direction_selectors` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 9 | `solidworks_available_point_selectors` | b6 | `sw_geometry_selectors.available_point_selectors` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 10 | `solidworks_build_review_report` | b15 | `sw_review.build_review_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 11 | `solidworks_chamfer` | b23 | `sw_part.chamfer` | 是 | 是 | 安全 | - | batch23 `pre_call=_select_edge` → `resolve_selection(..., "EDGE")` |
| 12 | `solidworks_circular_pattern` | b17 | `sw_part.circular_pattern` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 13 | `solidworks_clear_selection` | b5 | `sw_selection_spec.clear_selection` | 否 | 否 | 无关 | - | 清选区（`ClearSelection2`） |
| 14 | `solidworks_clear_selection_for_preview` | b7 | `sw_review.clear_selection_for_preview` | 否 | 否 | 无关 | - | 清选区（`ClearSelection2`） |
| 15 | `solidworks_collect_appearance_evidence` | b5 | `sw_render_material.collect_appearance_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 16 | `solidworks_collect_assembly_bom` | b6 | `sw_delivery.collect_assembly_bom` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 17 | `solidworks_collect_model_summary` | b8 | `sw_review.collect_model_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 18 | `solidworks_config_activate` | b33 | `sw_document_data.activate_configuration` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 19 | `solidworks_config_create` | b33 | `sw_document_data.create_configuration` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 20 | `solidworks_config_inspect` | b33 | `sw_document_data.inspect_configurations` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 21 | `solidworks_config_read_custom_property` | b33 | `sw_document_data.read_custom_property` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 22 | `solidworks_config_set_custom_properties` | b33 | `sw_document_data.set_custom_properties` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 23 | `solidworks_config_update_dimension` | b33 | `sw_document_data.update_dimension_mm` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 24 | `solidworks_costing_body_count` | b38 | `sw_costing.get_body_count_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 25 | `solidworks_costing_default_template` | b38 | `sw_costing.get_default_template_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 26 | `solidworks_costing_evidence` | b38 | `sw_costing.collect_costing_evidence_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 27 | `solidworks_costing_list_bodies` | b38 | `sw_costing.list_cost_bodies_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 28 | `solidworks_costing_list_templates` | b38 | `sw_costing.list_costing_templates_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 29 | `solidworks_costing_method_value` | b38 | `sw_costing.get_costing_method_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 30 | `solidworks_costing_read_analysis` | b38 | `sw_costing.read_cost_analysis_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 31 | `solidworks_costing_read_body` | b38 | `sw_costing.read_cost_body_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 32 | `solidworks_create_revolved_surface` | b72 | `sw_surface_ref_ops.insert_revolved_ref_surface` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md` Remarks 逐字：「**Make the selections using IModelDocExtension::SelectByID2 before calling this method.**」★ 官方**没给 mark** ⇒ 修的时候不能假定 |
| 33 | `solidworks_current_selection` | b5 | `sw_selection_spec.current_selection` | 是 | 否 | 真危险·诊断型 | A | ★ **经复核改正**：A 路判「无关（回读方向）」。按与其余 4 条**同一判据**（真的读选区 ＋ 无 `pre_call`）复核后改判。`sw_selection_spec.py::current_selection`：`count = get_selection_count(model)` ＋ `get_com_member(sm, "GetSelectedObject6", i, int(mark))` ⇒ **确实读选区**；`tool_specs_batch5.py` 的 spec **无 `pre_call`/`derived_args`** |
| 34 | `solidworks_current_sketch_name` | b55 | `sw_part.current_sketch_name` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 35 | `solidworks_custom_property_count` | b36 | `sw_custom_property.custom_property_count` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 36 | `solidworks_custom_property_get` | b20 | `sw_custom_property.custom_property` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 37 | `solidworks_custom_property_list` | b20 | `sw_custom_property.custom_properties` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 38 | `solidworks_custom_property_names` | b36 | `sw_custom_property.custom_property_names` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 39 | `solidworks_delivery_bom_traceability` | b36 | `sw_delivery.build_bom_traceability` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 40 | `solidworks_delivery_export_bom_csv` | b36 | `sw_delivery.export_assembly_bom_csv` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 41 | `solidworks_delivery_pack_and_go_audit_matrix` | b36 | `sw_delivery.build_pack_and_go_audit_matrix` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 42 | `solidworks_drawing_add_note` | b75 | `sw_drawing_expose.add_drawing_note` | 是 | 否 | 无关（经复核改正） | C | ★ **经复核改正**：原判「真危险」，实为**无关（官方明示降级）**。依据 `C:\swapi\types\IModelDoc2\InsertNote.md` Remarks 逐字：「The leader attachment points for the new note come from the selections made before calling this method. … **If there are no selections, the note: Does not have a leader / Is free standing / Is at the origin of the model or drawing**」⇒ 无选区也能建，只是没引线。spec doc 自己也记了真机证据「两格（选中 / 不选）都返回非 None」 |
| 43 | `solidworks_drawing_collect_view_evidence` | b43 | `sw_drawing_view.collect_view_evidence_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 44 | `solidworks_drawing_create_auxiliary_view` | b73 | `sw_drawing_create_missing.create_auxiliary_view` | 是 | 否 | 真危险·软失败 | C | `C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt2.md` **描述行**逐字：「Creates an auxiliary view **based on a selected edge in a drawing view**.」（★ 该页无 `## Remarks`）；`sw_drawing_create_missing.py::create_auxiliary_view` 只把 `sel = _selection_count(model)` 写进 `preconditions_held`，**仍然调** `CreateAuxiliaryViewAt2` |
| 45 | `solidworks_drawing_create_broken_view` | b73 | `sw_drawing_create_missing.insert_break_lines` | 否 | 否 | 无关 | - | 源码自记「★ **零选区前置**」 |
| 46 | `solidworks_drawing_create_detail_view` | b75 | `sw_drawing_expose.create_detail_view` | 否 | 否 | 无关 | - | 前置是「图上有局部圆（草图圆）」，不是选区前置 |
| 47 | `solidworks_drawing_create_hole_table` | b75 | `sw_drawing_expose.create_hole_table` | 是 | 否 | 无关（经复核改正） | C | ★ **经复核改正**：原判「真危险」，实为**无关（告警后仍尝试）**。依据 `scripts/sw_drawing_expose.py::create_hole_table`：`if not pre:` 段（源码内注「★★ 2026-10-03（接手轮）**从"硬失败"改成"告警后仍然尝试**」⇒ 记 `preconditions_held: False` + `attempted_without_precondition: True` 后**仍然调** `InsertHoleTable3`）⇒ 不因选区为空而必然失败。注：官方前置本身是真的（`InsertHoleTable3.md` Remarks 逐字「…**pre-selected** holes… datum origin that is also **pre-selected**…Before calling this method, call …」） |
| 48 | `solidworks_drawing_create_projected_view` | b75 | `sw_drawing_expose.create_projected_view` | 否 | 否 | 无关 | - | 前置是「`part_path` 必须已存盘」，不是选区前置 |
| 49 | `solidworks_drawing_create_revision_table` | b75 | `sw_drawing_expose.create_revision_table` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 50 | `solidworks_drawing_create_section_view` | b75 | `sw_drawing_expose.create_section_view` | 是 | 否 | 真危险·软失败 | C | `C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md` Remarks 逐字：「**Before calling this method, select the section line or lines to use as a section line.**」；`sw_drawing_expose.py::create_section_view` 只 `pre = _selection_count(drawing_model)` 写进 `pre_ok`，**仍然调** |
| 51 | `solidworks_drawing_current_sheet_info` | b42 | `sw_drawing_query.current_sheet_info` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 52 | `solidworks_drawing_current_sheet_name` | b36 | `sw_drawing_query.current_sheet_name` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 53 | `solidworks_drawing_get_current_sheet` | b19 | `sw_drawing_query.current_sheet_info` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 54 | `solidworks_drawing_insert_center_marks` | b75 | `sw_drawing_expose.insert_center_marks` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 55 | `solidworks_drawing_insert_datum_tag` | b73 | `sw_drawing_create_missing.insert_datum_tag` | 是 | 否 | 真危险·软失败 | C | `C:\swapi\types\IModelDoc2\InsertDatumTag2.md` **描述行**逐字：「Inserts a datum tag symbol **at a selected location**.」（★ 该页无 `## Remarks`）；官方**零参数** ⇒ 落点完全由选区决定；函数只报 `preconditions_held` 后仍调 `InsertDatumTag2()` |
| 56 | `solidworks_drawing_insert_surface_finish_symbol` | b73 | `sw_drawing_create_missing.insert_surface_finish_symbol` | 是 | 否 | 真危险·软失败 | C | `C:\swapi\types\IModelDocExtension\InsertSurfaceFinishSymbol3.md` **描述行**逐字：「Creates a surface-finish symbol **based on the last selection**.」；函数只把 `sel = _selection_count(model)` 写进 `preconditions_held` 后仍调 |
| 57 | `solidworks_drawing_list_sheets` | b19 | `sw_drawing_query.sheets_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 58 | `solidworks_drawing_list_views` | b19 | `sw_drawing_query.list_views` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 59 | `solidworks_drawing_set_sheet_format` | b75 | `sw_drawing_expose.set_sheet_format` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 60 | `solidworks_drawing_set_sheet_scale` | b44 | `sw_drawing_query.set_sheet_scale_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 61 | `solidworks_drawing_sheet_count` | b36 | `sw_drawing_query.sheet_count` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 62 | `solidworks_drawing_sheet_names` | b36 | `sw_drawing_query.sheet_names` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 63 | `solidworks_drawing_sheet_scale` | b44 | `sw_drawing_query.get_sheet_scale_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 64 | `solidworks_drawing_sheets_summary` | b42 | `sw_drawing_query.sheets_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 65 | `solidworks_drawing_view_scale` | b43 | `sw_drawing_view.get_view_scale_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 66 | `solidworks_drawing_view_set_scale` | b43 | `sw_drawing_view.set_view_scale_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 67 | `solidworks_entities_on_body` | b14 | `sw_selection_spec.entities_on_body` | 否 | 否 | 无关 | - | **不读选区**：走 `GetBodies2` + `IBody2.GetEdges/GetFaces/GetVertices` 按序号枚举（★ 与 `current_selection` 那一族不同，故 A 路判「无关」是对的） |
| 68 | `solidworks_equation_add` | b39 | `sw_equation.add_equation` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 69 | `solidworks_equation_delete` | b39 | `sw_equation.delete_equation` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 70 | `solidworks_equation_evaluate` | b39 | `sw_equation.evaluate_equations` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 71 | `solidworks_equation_list` | b39 | `sw_equation.list_equations` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 72 | `solidworks_export_bmp` | b33 | `sw_export.export_bmp_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 73 | `solidworks_export_dxf` | b33 | `sw_export.export_dxf_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 74 | `solidworks_export_iges` | b33 | `sw_export.export_iges_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 75 | `solidworks_export_image` | b59 | `sw_export.export_image_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 76 | `solidworks_export_parasolid` | b33 | `sw_export.export_parasolid_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 77 | `solidworks_export_step` | b33 | `sw_export.export_step_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 78 | `solidworks_export_stl` | b33 | `sw_export.export_stl_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 79 | `solidworks_extrude_boss` | b22 | `sw_part.extrude_boss` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 80 | `solidworks_extrude_cut` | b22 | `sw_part.extrude_cut` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 81 | `solidworks_extrude_midplane` | b22 | `sw_part.extrude_midplane` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 82 | `solidworks_fastener_table_types` | b10 | `sw_hole_features.list_fastener_table_types` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 83 | `solidworks_fastener_types` | b10 | `sw_hole_features.list_fastener_types` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 84 | `solidworks_feature_cosmetic_thread` | b76 | `sw_feature_entry_ops.insert_cosmetic_thread` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 85 | `solidworks_fillet` | b23 | `sw_part.fillet` | 是 | 是 | 安全 | - | batch23 `pre_call=_select_edge` → `resolve_selection(..., "EDGE")` |
| 86 | `solidworks_flatten_surface` | b76 | `sw_feature_entry_ops.create_flatten_surface` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 87 | `solidworks_gear_calculate_spur` | b41 | `sw_gear.calculate_external_spur_gear_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 88 | `solidworks_gear_create_spur` | b41 | `sw_gear.create_external_spur_gear_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 89 | `solidworks_get_active_view` | b14 | `sw_view.get_active_view` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 90 | `solidworks_get_costing_manager` | b8 | `sw_costing.get_costing_manager` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 91 | `solidworks_gtol_insert` | b39 | `sw_gtol.insert_gtol` | 否 | 否 | 无关 | - | **软依赖**：官方明说没选中时符号无引线、独立存在（降级不成失败） |
| 92 | `solidworks_helix_insert` | b39 | `sw_helix.insert_helix` | 是 | 否 | 无关（经复核改正） | B | ★ **经复核改正**：原判「真危险」，实为**无关**。官方示例 `C:\swapi\examples\Create_Spiral_Example_VB.md` 在调 `InsertHelix` **之前**执行 `swModel.ClearSelection2 True` 且**并未选中圆**（只 `SelectByID2("Front Plane","PLANE",…)` 选基准面后建圆）⇒ ★ 前置是「**活动草图里有圆**」，**不是选区**。另：能力层 `sw_helix.py::insert_helix` docstring 写「官方示例显示要先**选中一个圆**（`SelectByID2` + `CreateCircle`）」**与示例不符**（把选基准面的 `SelectByID2` 与建圆混为一谈）。★ `tool_specs_batch39.py` 的 spec doc 自己写的才是对的：「Needs the document state the official API requires (a circular sketch to revolve about)」 |
| 93 | `solidworks_hole_blind_by_selection` | b34 | `sw_hole_features.create_blind_hole_at_selection_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 94 | `solidworks_hole_counterbore_by_selection` | b34 | `sw_hole_features.create_counterbore_hole_at_selection_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 95 | `solidworks_hole_countersink_by_selection` | b34 | `sw_hole_features.create_countersink_hole_at_selection_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 96 | `solidworks_hole_pattern` | b57 | `sw_hole_features.hole_pattern_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 97 | `solidworks_hole_standards` | b10 | `sw_hole_features.list_hole_standards` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 98 | `solidworks_hole_through_by_selection` | b34 | `sw_hole_features.create_through_hole_at_selection_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 99 | `solidworks_hole_wizard` | b72 | `sw_hole_features.create_hole_wizard_at_selection_report` | 是（自建） | 否 | 无关（自建选区）· ★ **三路均未出现在报告里**（batch72） | — | `sw_hole_features.py::create_hole_wizard_at_selection_report` **自己建选区**：`model.ClearSelection2(True)` ＋ `ext.SelectByRay(sx, sy, sz, …, int(SW_SEL_FACES), False, 0, 0)` ⇒ 它只 `GetSelectedObjectCount2(-1)` **回读自己那条射线**的结果（`if not ok_ray or sel_n < 1: raise`）⇒ **不是**受害者。补录以保证总表覆盖 277 条 |
| 100 | `solidworks_insert_center_of_mass` | b70 | `sw_ref_geometry.insert_center_of_mass` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 101 | `solidworks_insert_coordinate_system` | b70 | `sw_ref_geometry.insert_coordinate_system` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 102 | `solidworks_insert_curve_through_points` | b71 | `sw_curve_and_split.insert_curve_through_points` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 103 | `solidworks_insert_delete_face` | b68 | `sw_surface_edit_ops.insert_delete_face` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 104 | `solidworks_insert_global_bounding_box` | b70 | `sw_ref_geometry.insert_global_bounding_box` | 是 | 否 | 真危险·条件 | C | `InsertGlobalBoundingBox2.md` Remarks 逐字：「**If** BBoxType is set to swGlobalBoundingBoxFitOptions_e.swBoundingBoxType_**CustomPlane**, then select a face or plane using IModelDocExtension::SelectByRay … before calling this method.」⇒ ★ 仅 `bbox_type=2` 触发；默认 `BestFit(1)` 不需要 |
| 105 | `solidworks_insert_lofted_ref_surface` | b69 | `sw_surface_ref_ops.insert_lofted_ref_surface` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IModelDoc2\InsertLoftRefSurface2.md` Remarks 逐字：「Use IModelDocExtension::SelectByID2 to select the profiles and guide curves. The mark for: **profile selections should be 1**」 |
| 106 | `solidworks_insert_offset_surface` | b68 | `sw_surface_edit_ops.insert_offset_surface` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IModelDoc2\InsertOffsetSurface.md` Remarks 逐字：「**Make the selections using IModelDocExtension::SelectByID2 before calling this method.**」★ **经复核改正**：能力层 docstring 写「★ 官方没写"要不要先选面"」**与官方页不符** —— 官方明写了；档位成立且证据应升到官方级 |
| 107 | `solidworks_insert_planar_surface` | b68 | `sw_surface_edit_ops.insert_planar_surface` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IModelDoc2\InsertPlanarRefSurface.md` Remarks 逐字：「Before calling this method, select the surface's boundary entities using IModelDocExtension::SelectByID2 with **Marks of 1**.」 |
| 108 | `solidworks_insert_ref_plane` | b70 | `sw_ref_geometry.insert_ref_plane` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IFeatureManager\InsertRefPlane.md` Remarks 逐字：「Before calling this method, you must have selected the reference entities using these marks with IModelDocExtension::SelectByID2: **0 = First reference entity · 1 = Second · 2 = Third**」 |
| 109 | `solidworks_insert_reference_point` | b70 | `sw_ref_geometry.insert_reference_point` | 是 | 否 | 真危险·条件 | C | ★ 依据链**比同表其它条弱一档**：`C:\swapi\types\IFeatureManager\InsertReferencePoint.md` 的 `## Remarks` **只写 NumberOfRefPoints 必须为 1、没有选区句**；唯一依据是 `tool_specs_batch70.py` 的 spec doc 真机记录「先选一个面（mark=0）+ `FaceCenter(4)` ⇒ 树新增 `点1`」「★★ 而选面**必须紧接着调用**」⇒ 仅对 `FaceCenter(4)`/`FaceVertexProjection(5)` 等部分 `ref_point_type` 成立 |
| 110 | `solidworks_insert_replace_face` | b68 | `sw_surface_edit_ops.insert_replace_face` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IModelDoc2\InsertFeatureReplaceFace.md` Remarks 逐字：「Before calling this method, select the faces to replace by calling IModelDocExtension::SelectByID2 with **Marks of 1** and select the replacement surfaces … with **Marks of 2**.」 |
| 111 | `solidworks_insert_ruled_surface` | b68 | `sw_surface_edit_ops.insert_ruled_surface` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md` Remarks 逐字：「If you select an edge with a **selection mark of 4**, the default face is used.」 |
| 112 | `solidworks_list_render_materials` | b5 | `sw_render_material.list_render_materials` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 113 | `solidworks_list_simulation_study_options` | b8 | `sw_simulation_study_options.list_setter_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 114 | `solidworks_measure_selection` | b46 | `sw_measure.measure_selection_report` | 是 | 否 | 真危险·显式拒 | B | `sw_measure.py::measure_selection_report`：`sel_n = int(_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", -1))` ＋ `if sel_n == 0: return {"ok": False, "stage": "selection", …}` ⇒ 经工具层**必然失败** |
| 115 | `solidworks_mirror_feature` | b16 | `sw_part.mirror_feature` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 116 | `solidworks_mold_core_cavity_split` | b9 | `sw_mold.insert_core_cavity_solids` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 117 | `solidworks_mold_draft_analysis` | b1 | `sw_mold.mold_draft_analysis` | 否 | 否 | 无关 | - | 会弹模态框，但**不读选区**（另一类问题，非本族） |
| 118 | `solidworks_mold_evidence` | b1 | `sw_mold.mold_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 119 | `solidworks_mold_parting_line` | b1 | `sw_mold.insert_parting_line` | 是 | 否 | 真危险·官方前置 | A | `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` Remarks 逐字：「Before calling this method, you must select the direction of pull and the edges for the parting line by calling IModelDocExtension::SelectByID2 with the following Marks: Direction of pull **1** / Parting line edges **4**」；`sw_mold.py::insert_parting_line` 函数体只有 `InsertMoldPartingLine`，一个实体都不选 |
| 120 | `solidworks_mold_parting_surface` | b9 | `sw_mold.insert_parting_surface` | 是 | 否 | 真危险·官方前置（条件） | A | `InsertMoldPartingSurface.md` Remarks 逐字：「f a parting line feature does not yet exist in the model, you must first select the direction of pull and the edges for the parting line using IModelDocExtension::SelectByID2」⇒ ★ 仅当模型里还没有分型线时触发 |
| 121 | `solidworks_mold_shut_off_surface` | b1 | `sw_mold.insert_shut_off_surface` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 122 | `solidworks_mold_undercut_detect` | b9 | `sw_mold.mold_undercut_detect` | 否 | 否 | 无关 | - | 方向由 `Dx/Dy/Dz` 显式给 ⇒ 不依赖选区（但会弹模态框，另一类问题） |
| 123 | `solidworks_motion_collect_summary` | b40 | `sw_motion.collect_motion_study_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 124 | `solidworks_motion_create_study` | b40 | `sw_motion.create_motion_study` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 125 | `solidworks_motion_ensure_type_library` | b40 | `sw_motion.ensure_motion_type_library` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 126 | `solidworks_motion_study_manager` | b40 | `sw_motion.get_motion_study_manager` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 127 | `solidworks_motion_validate_studies` | b40 | `sw_motion.validate_motion_studies_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 128 | `solidworks_motion_validate_summary` | b40 | `sw_motion.validate_motion_study_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 129 | `solidworks_part_axis` | b49 | `sw_part.create_axis_report` | 是 | 否 | 真危险·显式拒 | B | `sw_part.py::create_axis_report`：`if sel_n == 0: return {"ok": False, "stage": "selection", "error": "建轴要先选中几何…"}` |
| 130 | `solidworks_part_bounding_box` | b10 | `sw_part.get_bounding_box` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 131 | `solidworks_part_insert_composite_curve` | b32 | `sw_part.insert_composite_curve_report` | 是 | 否 | 真危险·官方前置 | B | `C:\swapi\types\IModelDoc2\InsertCompositeCurve.md` Remarks 逐字：「To use this method, select the entities by calling IModelDocExtension::SelectByID2 with a **mark number of 1**」 |
| 132 | `solidworks_part_insert_dome` | b32 | `sw_part.insert_dome_report` | 是 | 否 | 真危险·官方前置 | B | `C:\swapi\types\IModelDoc2\InsertDome.md` Remarks 逐字：「Before using this method, you must select the face for the dome using a **selection mark of 1**.」 |
| 133 | `solidworks_part_loft` | b47 | `sw_loft.create_loft_report` | 是 | 否 | 真危险·显式拒 | B | `sw_loft.py::create_loft_report`：`if use_selected_profiles and sel_n < 2: return {"ok": False, "stage": "selection", "error": "放样至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）…"}` |
| 134 | `solidworks_part_mass_properties` | b24 | `sw_mass_property.mass_properties` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 135 | `solidworks_part_rib` | b32 | `sw_part.rib_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 136 | `solidworks_part_shell` | b32 | `sw_part.shell_report` | 否 | 否 | 无关 | - | **软依赖**：`faces_to_remove` 未暴露、函数体 `InsertFeatureShell(thickness, False)` 不读选区 |
| 137 | `solidworks_part_sweep` | b48 | `sw_sweep.create_sweep_report` | 是 | 否 | 真危险·显式拒 | B | `sw_sweep.py::create_sweep_report`：`for mark, label in ((1, "profile"), (4, "path"), (2, "guide"))` 回读 ＋ `if sel.get("profile", 0) < 1 or sel.get("path", 0) < 1: return {"ok": False, "stage": "selection", …}` |
| 138 | `solidworks_part_wrap` | b50 | `sw_wrap.create_wrap_report` | 是 | 否 | 真危险·显式拒 | B | `sw_wrap.py::create_wrap_report`：`for mark, label in ((4, "sketch"), (1, "face"))` ＋ `if sel.get("sketch", 0) < 1 or sel.get("face", 0) < 1: return {"ok": False, "stage": "selection", …}` |
| 139 | `solidworks_read_document_units` | b52 | `sw_units.read_units_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 140 | `solidworks_read_sensors` | b51 | `sw_sensor.read_sensors_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 141 | `solidworks_refresh_scene_graph` | b7 | `sw_render_material.refresh_scene_graph` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 142 | `solidworks_resolve_entity` | b53 | `sw_selection_spec.resolve_entity_report` | 是 | 否 | 真危险·诊断型 | C | `sw_selection_spec.py::resolve_entity_report`：`out["count"] = int(get_selection_count(model))` ＋ `"解析出了对象**而选区计数为 0** ⇒ 选择器是 __current_selection__ 时"` |
| 143 | `solidworks_resolve_selection` | b53 | `sw_selection_spec.resolve_selection` | 是 | 否 | 真危险·诊断型 | C | `sw_selection_spec.py::resolve_selection`：`count = get_selection_count(model)` ＋ `raise EntitySelectionError("选择器 %r 解析后**选区计数为 0**")` ⇒ `__current_selection__` 路径必失败 |
| 144 | `solidworks_revolve_boss` | b17 | `sw_part.revolve_boss` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 145 | `solidworks_select_by_selector` | b53 | `sw_selection_spec.select_by_selector_report` | 否 | 否 | 无关 | - | **自建选区**：`select_object(...)` 按序号自己选 |
| 146 | `solidworks_select_entity_by_index` | b53 | `sw_selection_spec.select_entity_by_index` | 否 | 否 | 无关 | - | **自建选区**：按序号自己 `Select4` |
| 147 | `solidworks_select_face_selector` | b63 | `sw_simulation.select_face_by_selector_report` | 否 | 否 | 无关 | - | **自建选区**：`resolve_face_selector(model, selection)` |
| 148 | `solidworks_selection_count` | b53 | `sw_selection_spec.get_selection_count` | 是 | 否 | 真危险·诊断型 | C | `sw_selection_spec.py::get_selection_count`：`get_com_member(sm, "GetSelectedObjectCount2", -1)`；spec 无 `pre_call`/`derived_args` ⇒ 经工具层**恒回 0**（事实 503：`RESOLVERS["model"]` 会清空选区） |
| 149 | `solidworks_selection_point` | b53 | `sw_selection_spec.selection_point` | 是 | 否 | 真危险·诊断型 | C | `sw_selection_spec.py::selection_point`：`if not out["selection_count"]: out["error"] = "当前**没有选中任何东西** ⇒ 读不到点。…"` |
| 150 | `solidworks_selector_resolve_direction` | b36 | `sw_geometry_selectors.resolve_direction` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 151 | `solidworks_selector_resolve_point` | b36 | `sw_geometry_selectors.resolve_point` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 152 | `solidworks_set_standard_view` | b5 | `sw_review.set_standard_view` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 153 | `solidworks_sheet_metal_create_base_flange` | b3 | `sw_sheet_metal.create_base_flange` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 154 | `solidworks_sheet_metal_create_draft` | b4 | `sw_sheet_metal.create_draft` | 是 | 是 | 安全 | - | batch4 `pre_call=_pre_draft` → `resolve_selection(..., "FACE")` |
| 155 | `solidworks_sheet_metal_create_edge_flange` | b4 | `sw_sheet_metal.create_edge_flange` | 是 | 是 | 安全 | - | batch4 `pre_call=_pre_edge_flange` → `resolve_selection(..., "EDGE")` |
| 156 | `solidworks_sheet_metal_create_gusset` | b4 | `sw_sheet_metal.create_gusset` | 是 | 是 | 安全 | - | batch4 `pre_call=_pre_gusset` → `resolve_selection(..., "FACE")` |
| 157 | `solidworks_sheet_metal_create_one_bend` | b3 | `sw_sheet_metal.create_one_bend` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 158 | `solidworks_sheet_metal_create_swept_flange` | b4 | `sw_sheet_metal.create_swept_flange` | 是 | 是 | 安全 | - | ★ 非 `pre_call` 形态：batch4 `derived_args=_swept_refs_and_spec` 把选择器**解析成对象**塞进 `data.Path`/`data.Profile` ⇒ 选区不必活到第 4 步 |
| 159 | `solidworks_sheet_metal_evidence` | b2 | `sw_sheet_metal.sheet_metal_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 160 | `solidworks_sheet_metal_insert_closed_corner` | b74 | `sw_sheet_metal_weld_entry.insert_sheet_metal_closed_corner` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 161 | `solidworks_sheet_metal_insert_miter_flange` | b74 | `sw_sheet_metal_weld_entry.insert_sheet_metal_miter_flange` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 162 | `solidworks_simulation_apply_centrifugal_force` | b29 | `sw_simulation_loads.apply_centrifugal_force_report` | 是 | 是 | 安全 | - | batch29 同上 |
| 163 | `solidworks_simulation_apply_convection` | b58 | `sw_simulation_loads.apply_convection_report` | 是 | 是 | 安全 | - | batch58 经 `tool_specs_batch29._spec` 工厂 |
| 164 | `solidworks_simulation_apply_distributed_mass` | b60 | `sw_simulation_loads.apply_distributed_mass_report` | 是 | 是 | 安全 | - | batch60 经 batch29 工厂 |
| 165 | `solidworks_simulation_apply_elastic_connector` | b58 | `sw_simulation_loads.apply_elastic_connector_report` | 是 | 是 | 安全 | - | batch58 同上 |
| 166 | `solidworks_simulation_apply_fixed_restraint` | b26 | `sw_simulation.apply_fixed_restraint` | 是 | 是 | 安全 | - | batch26 `pre_call=_select_face` + `derived_args=_derive_model` |
| 167 | `solidworks_simulation_apply_force` | b60 | `sw_simulation_loads.apply_force_report` | 是 | 是 | 安全 | - | batch60 同上 |
| 168 | `solidworks_simulation_apply_gravity` | b29 | `sw_simulation_loads.apply_gravity_report` | 是 | 是 | 安全 | - | batch29 同上 |
| 169 | `solidworks_simulation_apply_heat_flux` | b58 | `sw_simulation_loads.apply_heat_flux_report` | 是 | 是 | 安全 | - | batch58 同上 |
| 170 | `solidworks_simulation_apply_heat_power` | b58 | `sw_simulation_loads.apply_heat_power_report` | 是 | 是 | 安全 | - | batch58 同上 |
| 171 | `solidworks_simulation_apply_link_connector` | b64 | `sw_simulation_loads.add_link_connector_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 172 | `solidworks_simulation_apply_normal_force` | b26 | `sw_simulation.apply_normal_force` | 是 | 是 | 安全 | - | batch26 同上 |
| 173 | `solidworks_simulation_apply_pressure` | b29 | `sw_simulation_loads.apply_pressure_report` | 是 | 是 | 安全 | - | batch29 `_spec` 工厂 `pre_call=_select_face` |
| 174 | `solidworks_simulation_apply_radiation` | b58 | `sw_simulation_loads.apply_radiation_report` | 是 | 是 | 安全 | - | batch58 同上 |
| 175 | `solidworks_simulation_apply_remote_load` | b60 | `sw_simulation_loads.apply_remote_load_report` | 是 | 是 | 安全 | - | batch60 同上 |
| 176 | `solidworks_simulation_apply_rigid_connector` | b61 | `sw_simulation_loads.apply_rigid_connector_by_objects_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 177 | `solidworks_simulation_apply_temperature` | b58 | `sw_simulation_loads.apply_temperature_report` | 是 | 是 | 安全 | - | batch58 同上（★ 文件头「不注册」的注释与代码不符，工具实际已注册） |
| 178 | `solidworks_simulation_apply_torque` | b29 | `sw_simulation_loads.apply_torque_report` | 是 | 是 | 安全 | - | batch29 同上 |
| 179 | `solidworks_simulation_check_mesh_size` | b31 | `sw_simulation.check_mesh_size_sane` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 180 | `solidworks_simulation_collect_evidence` | b28 | `sw_simulation.collect_study_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 181 | `solidworks_simulation_configure_buckling_solver` | b37 | `sw_simulation_study_options.configure_buckling_solver_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 182 | `solidworks_simulation_configure_frequency_solver` | b37 | `sw_simulation_study_options.configure_frequency_solver_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 183 | `solidworks_simulation_configure_static_solver` | b37 | `sw_simulation_study_options.configure_static_solver_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 184 | `solidworks_simulation_create_mesh` | b28 | `sw_simulation.create_mesh_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 185 | `solidworks_simulation_create_mesh_for_control` | b13 | `sw_simulation_study.create_mesh_for_control` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 186 | `solidworks_simulation_create_study` | b27 | `sw_simulation.create_study_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 187 | `solidworks_simulation_default_element_size_and_tolerance` | b13 | `sw_simulation.default_element_size_and_tolerance` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 188 | `solidworks_simulation_find_study` | b27 | `sw_simulation.find_study` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 189 | `solidworks_simulation_generate_report` | b13 | `sw_simulation_study.generate_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 190 | `solidworks_simulation_list_setter_summary` | b36 | `sw_simulation_study_options.list_setter_summary` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 191 | `solidworks_simulation_list_studies` | b27 | `sw_simulation.list_studies` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 192 | `solidworks_simulation_mesh_size` | b28 | `sw_simulation.mesh_size_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 193 | `solidworks_simulation_run_analysis` | b28 | `sw_simulation.run_analysis_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 194 | `solidworks_simulation_set_material` | b1 | `sw_simulation.set_material` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 195 | `solidworks_simulation_set_study_option` | b37 | `sw_simulation_study_options.set_study_option_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 196 | `solidworks_simulation_set_study_options` | b37 | `sw_simulation_study_options.set_study_options_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 197 | `solidworks_sketch_add_3point_arc` | b65 | `sw_sketch_primitives.sketch_3point_arc` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 198 | `solidworks_sketch_add_3point_center_rectangle` | b65 | `sw_sketch_primitives.sketch_3point_center_rectangle` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 199 | `solidworks_sketch_add_3point_rectangle` | b65 | `sw_sketch_primitives.sketch_3point_corner_rectangle` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 200 | `solidworks_sketch_add_arc` | b54 | `sw_part.sketch_arc` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 201 | `solidworks_sketch_add_centerline` | b54 | `sw_part.sketch_centerline` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 202 | `solidworks_sketch_add_circle` | b21 | `sw_part.sketch_circle` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 203 | `solidworks_sketch_add_conic` | b65 | `sw_sketch_primitives.sketch_conic` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 204 | `solidworks_sketch_add_ellipse` | b54 | `sw_part.sketch_ellipse` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 205 | `solidworks_sketch_add_line` | b21 | `sw_part.sketch_line` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 206 | `solidworks_sketch_add_parabola` | b65 | `sw_sketch_primitives.sketch_parabola` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 207 | `solidworks_sketch_add_parallelogram` | b65 | `sw_sketch_primitives.sketch_parallelogram` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 208 | `solidworks_sketch_add_partial_ellipse` | b65 | `sw_sketch_primitives.sketch_elliptical_arc` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 209 | `solidworks_sketch_add_perimeter_circle` | b65 | `sw_sketch_primitives.sketch_perimeter_circle` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 210 | `solidworks_sketch_add_polygon` | b54 | `sw_part.sketch_polygon` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 211 | `solidworks_sketch_add_rectangle` | b21 | `sw_part.sketch_corner_rectangle` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 212 | `solidworks_sketch_add_slot` | b54 | `sw_part.sketch_slot` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 213 | `solidworks_sketch_add_tangent_arc` | b65 | `sw_sketch_primitives.sketch_tangent_arc` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 214 | `solidworks_sketch_circular_pattern` | b66 | `sw_sketch_edit_ops.sketch_circular_pattern` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 215 | `solidworks_sketch_convert_entities` | b41 | `sw_sketch_edit.convert_entities` | 是 | 否 | 真危险·官方前置 | B | `C:\swapi\types\ISketchManager\SketchUseEdge3.md` Remarks 逐字：「Specifying true for the Chain argument creates the **selected** sketch entity and any other sketch entities that belong to the same sketch contour or chain…」 |
| 216 | `solidworks_sketch_count_arcs` | b18 | `sw_sketch.count_arcs` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 217 | `solidworks_sketch_count_lines` | b18 | `sw_sketch.count_lines` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 218 | `solidworks_sketch_count_segments` | b18 | `sw_sketch.count_segments` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 219 | `solidworks_sketch_create_chamfer` | b41 | `sw_sketch_edit.create_sketch_chamfer` | 是 | 否 | 真危险·官方前置 | B | `C:\swapi\types\ISketchManager\CreateChamfer.md` **描述行**逐字：「Creates a chamfer **between two selected sketch entities**.」（★ 该页无 `## Remarks` 段 ⇒ 证据在描述行） |
| 220 | `solidworks_sketch_end` | b21 | `sw_part.end_sketch` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 221 | `solidworks_sketch_extend` | b66 | `sw_sketch_edit_ops.sketch_extend` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 222 | `solidworks_sketch_fillet` | b66 | `sw_sketch_edit_ops.sketch_fillet` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 223 | `solidworks_sketch_flip_entities` | b67 | `sw_sketch_modify_ops.sketch_flip` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 224 | `solidworks_sketch_fully_defined_status` | b72 | `sw_sketch_status.get_constrained_status` | 否 | 否 | 无关 | - | 前置是「**必须有活动草图**」，不是选区前置 |
| 225 | `solidworks_sketch_is_3d` | b18 | `sw_sketch.is_3d_sketch` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 226 | `solidworks_sketch_linear_pattern` | b66 | `sw_sketch_edit_ops.sketch_linear_pattern` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 227 | `solidworks_sketch_mirror` | b41 | `sw_sketch_edit.sketch_mirror` | 是 | 否 | 真危险·官方前置 | B | `C:\swapi\types\IModelDoc2\SketchMirror.md` Remarks 逐字：「If the entity to mirror is: a sketch segment, then use a **selection mark of 1**; a centerline, then use a **selection mark of 2**.」★ 复核改正：B 路写的路径 `ISketchManager/SketchMirror.md` **不存在**，正确路径是 `IModelDoc2/SketchMirror.md` |
| 228 | `solidworks_sketch_move_entities` | b67 | `sw_sketch_modify_ops.sketch_move` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 229 | `solidworks_sketch_offset` | b66 | `sw_sketch_edit_ops.sketch_offset` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 230 | `solidworks_sketch_rotate_entities` | b67 | `sw_sketch_modify_ops.sketch_rotate` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 231 | `solidworks_sketch_scale_entities` | b67 | `sw_sketch_modify_ops.sketch_scale` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 232 | `solidworks_sketch_spline` | b76 | `sw_part.sketch_spline` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 233 | `solidworks_sketch_start` | b21 | `sw_part.start_sketch` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 234 | `solidworks_sketch_stretch_entities` | b67 | `sw_sketch_modify_ops.sketch_stretch` | 是 | 否 | 真危险·官方前置 | C | `C:\swapi\types\IModelDocExtension\Stretch.md` **描述行**逐字：「Stretch the **selected** entities.」（★ 该页无 `## Remarks` 段） |
| 235 | `solidworks_sketch_trim` | b66 | `sw_sketch_edit_ops.sketch_trim` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 236 | `solidworks_slot_semicircular_by_selection` | b34 | `sw_hole_features.create_semicircular_slot_at_selection_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 237 | `solidworks_surface_create_extruded` | b45 | `sw_surface_features.create_extruded_surface_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 238 | `solidworks_surface_evidence` | b2 | `sw_surface.collect_surface_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 239 | `solidworks_surface_extend` | b45 | `sw_surface_features.insert_extend_surface_report` | 否 | 否 | 无关 | - | **自建选区**：复用 `_select_all_surface_faces`；spec doc 自记「不选面它也能成（★ 真机实测）」 |
| 240 | `solidworks_surface_fill` | b45 | `sw_surface_features.insert_fill_surface_report` | 是 | 否 | 无关（经复核改正） | B | ★ **经复核改正**：原判「真危险」，实为**无关（可降级）**。依据 `scripts/sw_surface_features.py::insert_fill_surface_report`：声明式分支回读计数为 0 时 **不失败、而是回退**——`_selected_readback <= 0` ⇒ 设 `_fallback_note` 并把 `_declarative` 置 False ⇒ 走 `ext.SelectByID2("", "EDGE", 中点, True, MARK_BOUNDARY, callout, 0)` 自动选边路径（★ 在 inject 之后执行 ⇒ 不受影响，**真机建成过**）⇒ 传 `selection` 也**不会失败**。注：官方前置本身是真的（`InsertFillSurface2.md` Remarks 逐字「You must use IModelDocExtension::SelectByID2 and the following Mark values … Boundary curves = 1」） |
| 241 | `solidworks_surface_knit` | b45 | `sw_surface_features.knit_surfaces_report` | 否 | 否 | 无关 | - | **自建选区**：`_select_all_surface_faces` 先 `ClearSelection2` 再按 mark 选全部面 |
| 242 | `solidworks_surface_midsurface_create` | b74 | `sw_sheet_metal_weld_entry.create_midsurface` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 243 | `solidworks_thicken` | b76 | `sw_feature_entry_ops.thicken_surface` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 244 | `solidworks_toolbox_list_standards` | b41 | `sw_toolbox_index.list_standards` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 245 | `solidworks_toolbox_load_index` | b41 | `sw_toolbox_index.load_index` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 246 | `solidworks_toolbox_part_path` | b41 | `sw_toolbox_index.part_path` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 247 | `solidworks_toolbox_search` | b41 | `sw_toolbox_index.search` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 248 | `solidworks_topology_collect_numbers` | b30 | `sw_topology.collect_topology_numbers` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 249 | `solidworks_topology_create_demold_control` | b12 | `sw_topology.create_demold_control` | 是 | 否 | 真危险·官方前置 | A | `sw_topology.py::create_demold_control` docstring：「调用方须先选好拔模方向的面/边/基准面」；`tool_specs_batch12.py` doc 亦写「The caller must first select the pull-direction face/edge/plane」★ **官方依据缺失**：`C:\swapi` 检索 `CreateDemoldControl` ⇒ **0 命中**（复核已重跑） |
| 250 | `solidworks_topology_create_factor_of_safety_constraint` | b11 | `sw_topology.create_factor_of_safety_constraint` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 251 | `solidworks_topology_create_mass_constraint` | b11 | `sw_topology.create_mass_constraint` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 252 | `solidworks_topology_create_preserved_region` | b11 | `sw_topology.create_preserved_region` | 是 | 否 | 真危险·官方前置 | A | `sw_topology.py::create_preserved_region` docstring：「⚑ 调用方须**先选好要保留的面**再调本函数」；函数体只有 `CreatePreservedRegionControl` + `SetIncludeRegionDepth2`。★ **官方依据缺失**：`Get-ChildItem C:\swapi -Recurse -Filter *.md \| Select-String "CreatePreservedRegionControl"` ⇒ **0 命中**（复核已重跑） |
| 253 | `solidworks_topology_create_stress_constraint` | b12 | `sw_topology.create_stress_constraint` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 254 | `solidworks_topology_create_study` | b1 | `sw_topology.create_topology_study` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 255 | `solidworks_topology_create_symmetry_control` | b12 | `sw_topology.create_symmetry_control` | 是 | 否 | 真危险·官方前置 | A | `sw_topology.py::create_symmetry_control` docstring：「调用方须先选好对称平面」；`tool_specs_batch12.py` doc 亦写「The caller must first select the symmetry plane(s)」★ **官方依据缺失**：`C:\swapi` 检索 `CreateSymmetryControl` ⇒ **0 命中**（复核已重跑） |
| 256 | `solidworks_topology_create_thickness_control` | b11 | `sw_topology.create_thickness_control` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 257 | `solidworks_topology_evidence` | b1 | `sw_topology.collect_topology_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 258 | `solidworks_topology_list_constraints` | b30 | `sw_topology.topology_constraints_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 259 | `solidworks_topology_manager_report` | b30 | `sw_topology.topology_manager_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 260 | `solidworks_topology_options_report` | b30 | `sw_topology.topology_options_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 261 | `solidworks_topology_run` | b1 | `sw_topology.run_topology_study` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 262 | `solidworks_topology_set_goal` | b30 | `sw_topology.set_topology_goal_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 263 | `solidworks_topology_set_iteration_options` | b30 | `sw_topology.set_topology_iteration_options_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 264 | `solidworks_undo` | b52 | `sw_session.undo_report` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 265 | `solidworks_weldment_create_cut_list` | b35 | `sw_weldment.create_cut_list` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 266 | `solidworks_weldment_create_profile_center_mate` | b35 | `sw_weldment.create_profile_center_mate` | 是 | 否 | 真危险·官方前置 | B | `sw_weldment.py::create_profile_center_mate` docstring「在所选实体间创建型材中心配合」+ `raise ValueError("entities 为 None：须先选中要配合的实体")` + `set_com_member(data, "EntitiesToMate", entities)`；而 `tool_specs_batch35.py` 的 `Param("entities", str, default="__current_selection__")` 是**字符串直传**（无 `param_alias` / 无 `pre_call` / 无 `derived_args`）⇒ 声明式选择根本没被解析。★ **官方依据缺失**：`IProfileCenterMateData` 在 `C:\swapi` 下**无命中**（本轮实测）⇒ ★ 官方 mark 无法引用 |
| 267 | `solidworks_weldment_create_structural_member` | b62 | `sw_weldment.create_structural_member_from_sketch` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 268 | `solidworks_weldment_create_sub_weld_folder` | b2 | `sw_weldment.create_sub_weld_folder` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 269 | `solidworks_weldment_create_weldment_profile` | b35 | `sw_weldment.create_weldment_profile` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 270 | `solidworks_weldment_ensure_cut_list` | b2 | `sw_weldment.ensure_cut_list` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 271 | `solidworks_weldment_evidence` | b2 | `sw_weldment.weldment_evidence` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 272 | `solidworks_weldment_export_cut_list_csv` | b35 | `sw_weldment.export_cut_list_csv` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 273 | `solidworks_weldment_gusset_create` | b74 | `sw_sheet_metal_weld_entry.insert_weldment_gusset` | 是 | 是 | 安全 | - | batch74 `pre_call=_select_faces_for(1, 2)`（官方 mark=1 · 两个面） |
| 274 | `solidworks_weldment_insert_end_cap` | b74 | `sw_sheet_metal_weld_entry.insert_weldment_end_cap` | 是 | 是 | 安全 | - | batch74 `pre_call=_select_faces_for(0, 1)`（按 mark 选 1 个面，回读计数，不够就抛） |
| 275 | `solidworks_weldment_read_property_manager` | b35 | `sw_weldment.read_property_manager` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 276 | `solidworks_weldment_set_cut_list_properties` | b35 | `sw_weldment.set_cut_list_properties` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |
| 277 | `solidworks_weldment_update_cut_list` | b2 | `sw_weldment.update_cut_list` | 否 | 否 | 无关 | - | 目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据） |

---

## 二、统计

| 档位 | 条数 |
|---|---|
| **真危险**（合计） | **36** |
| ├ 真危险·官方前置 | 20 |
| ├ 真危险·显式拒 | 5 |
| ├ 真危险·诊断型 | 5 |
| ├ 真危险·条件 | 2 |
| └ 真危险·软失败 | 4 |
| 安全 | 23 |
| 无关 | 218 |
| **合计** | **277** |

★ **36 + 23 + 218 = 277** ✓（batch1–25 **81** + batch26–50 **108** + batch51–76 **88** = **277** ✓）
★ 其中 **★ 待补依据 5 条**（见 §〇 末段）。

---

## 三、★ 复核结论

### 3.1 复核了几条

★ **逐条独立复核 41 条**（三路标为「真危险」的全部条目）。
★ **两侧都自己打开看过**，不是转述：
- **spec 侧**：AST 解析每个 `ToolSpec`/`_spec` 调用（含跨文件工厂）⇒ **41 条全部确认 `pre_call` 与 `derived_args` 都为 `None`**；
- **函数侧**：41 条目标函数的源码全文逐条读过（24 条函数体**零选区 token**——靠官方 API 隐式吃选区，故逐条读 docstring + spec doc + 官方页）；
- **官方侧**：对能定位的成员**逐页打开 `C:\swapi\types\<接口>\<成员>.md`** 取 `## Remarks` / 描述行原文。

### 3.2 改正了几条

★ **改正 5 条**（4 条降级 + 1 条升级）：

| # | 工具 | 原判 | 实为 | 依据 |
|---|---|---|---|---|
| 1 | `solidworks_surface_fill` | B 路：真危险 | **无关（可降级）** | `scripts/sw_surface_features.py::insert_fill_surface_report`：声明式分支回读计数为 0 时 **不失败而是回退** —— `_selected_readback <= 0` ⇒ 设 `_fallback_note`、`_declarative = False` ⇒ 走 `SelectByID2(…, MARK_BOUNDARY, …)` 自动选边路径（**在 inject 之后执行** ⇒ 不受事实 503 影响，真机建成过）⇒ 传 `selection` 也不失败。★ B 路自己在「拿不准 1」里留了这个口子，但**档位仍按保守口径计了真危险** |
| 2 | `solidworks_drawing_create_hole_table` | C 路：真危险 | **无关（告警后仍尝试）** | `scripts/sw_drawing_expose.py::create_hole_table`：`if not pre:` 段源码内注「★★ 2026-10-03（接手轮）**从"硬失败"改成"告警后仍然尝试"**」⇒ 只记 `preconditions_held: False` + `attempted_without_precondition: True` 后**仍然调** `InsertHoleTable3` |
| 3 | `solidworks_helix_insert` | B 路：真危险 | **无关** | ★ 官方示例 `C:\swapi\examples\Create_Spiral_Example_VB.md` 在 `InsertHelix` **之前**执行 `swModel.ClearSelection2 True` 且**并未选中圆**（只 `SelectByID2("Front Plane","PLANE",…)` 选基准面后 `CreateCircle`）⇒ ★ 前置是「**活动草图里有圆**」，不是选区。★ B 路依据的能力层 docstring「官方示例显示要先**选中一个圆**」**与示例不符** |
| 4 | `solidworks_drawing_add_note` | C 路：真危险 | **无关（官方明示降级）** | `C:\swapi\types\IModelDoc2\InsertNote.md` Remarks 逐字：「…**If there are no selections, the note: Does not have a leader / Is free standing / Is at the origin of the model or drawing**」⇒ 无选区也能建，只是没引线 |
| 5 | `solidworks_current_selection` | A 路：无关 | **真危险·诊断型（升级）** | ★ 与 C 路那 4 条**同一判据**下 A 路口径不自洽。复核：`sw_selection_spec.py::current_selection` 确实 `count = get_selection_count(model)` + `GetSelectedObject6(i, mark)` **读选区**；`tool_specs_batch5.py` 的 spec **无 `pre_call`/`derived_args`** ⇒ 经工具层恒回空列表 |

### 3.3 ★ 另有 1 处**依据链改正**（档位不变，但证据该升级）

★ `solidworks_insert_offset_surface`：能力层 `sw_surface_edit_ops.py::insert_offset_surface` 的 docstring 写
「⚠ ★ **官方没写"要不要先选面"**，而语义上要（参考面）」—— ★ **与官方页不符**。
`C:\swapi\types\IModelDoc2\InsertOffsetSurface.md` 的 `## Remarks` 首句逐字就是：
「**Make the selections using IModelDocExtension::SelectByID2 before calling this method.**」
⇒ ★ **档位不变（真危险·官方前置），但依据应从「语义推断」升到「官方逐字」** ⇒ ★ 这条比 C 路原本写的**更硬**。

### 3.4 ★ 本轮补录（三路都漏了、但不影响档位）

★ `solidworks_hole_wizard`（batch72）**在三份候选报告里都不出现**。复核结果：**无关（自建选区）** ——
`sw_hole_features.py::create_hole_wizard_at_selection_report` 自己 `ClearSelection2(True)` ＋
`ext.SelectByRay(…, int(SW_SEL_FACES), …)` 建孔位，只 `GetSelectedObjectCount2(-1)` **回读自己那条射线**。
★ 补录以保证「总表覆盖全部 ToolSpec」这一条成立。

### 3.5 ★ 三路原本的覆盖缺口（本轮已补）

★ 三路的 batch 切分是 **1–25 / 26–50 / 51–76**，本轮用 AST 逐文件核过条数：
**81 / 108 / 88**，合计 **277**，与仓库里 AST 抽出的 ToolSpec 总数**完全一致**（无重名、无缺 `module`/`function`）。
★ ⇒ **并集没有丢行**；唯一的缺口是上面 3.4 那条（三路都漏报，但档位正确）。

---

## 四、★ 最该先修的 5 条

★ 排序口径（两条，按题目要求）：
① **「覆盖率关键词命中」** = 官方页里 `SelectByID2` / `selection mark` / `Marks of` / `pre-selected` 这些字样的密度
—— 命中越多 = 官方把前置写得越死 = 越不可能是「猜的」；
② **是否已有其它工具覆盖** = 同一个官方能力，仓里是不是已经有别的工具能做（已有 ⇒ 边际收益低；没有 ⇒ 空白）。

| 排序 | 工具 | ① 关键词命中 | ② 其它工具覆盖 | 为什么排这里 |
|---|---|---|---|---|
| **1** | `solidworks_mold_parting_line` | ★★★ 官方给了**完整 mark 表**：方向 mark 1 / 分型线边 mark 4 | ❌ **无**。全仓只有这一条碰 `InsertMoldPartingLine` | ★ 官方前置写得最死（逐字 + 表格）· mark 现成 · `resolve_selection` 的 `EDGE`/`FACE` **两种 kind 现成** · 照 `batch23::_select_edge` 抄一个 `_pre_parting_line` 连做两次（第二次 `append`）即可 ⇒ **改动量最小、收益最直接** |
| **2** | `solidworks_mold_parting_surface` | ★★★ 与第 1 条**完全同形**（同一段官方表述：方向 mark 1 + 边 mark 4） | ❌ 无 | ★ **与第 1 条可共用同一个 `pre_call`** ⇒ 修第 1 条时顺手一起改，**边际成本≈0**；只是触发条件窄（模型里还没有分型线时），故排第 2 |
| **3** | `solidworks_part_wrap` | ★★★ 官方 `InsertWrapFeature2.md` Remarks 给了一张**完整 mark 表**（面=1 / 拔模方向实体 / 线性边…） | ⚠ 部分：`solidworks_sketch_offset`/`fillet`/`linear_pattern` 走 `_select_spec`，但**没有**「草图 mark=4 + 面 mark=1 同时」的双 mark 工具 | ★ 现成解法**已经在仓里**：`tool_specs_batch74.py::_select_faces_for(mark, count)`（按对象遍历体→面、按 mark 选、回读计数、不够就抛）—— ★ 直接复用两个 `pre_call` 即可（`(4,1)` + `(1,1)`）⇒ **改造成本最低、官方 mark 最全** |
| **4** | `solidworks_part_sweep` / `solidworks_part_loft` / `solidworks_part_axis` / `solidworks_part_wrap`（四件套的**共同底座**） | ★★☆ 三条都有官方 mark（sweep: 轮廓 1 / 路径 4 / 引导线 2；loft: 轮廓 1；axis: 未定） | ⚠ 四条**各自只有自己**，但**四条同型** ⇒ 一起修 | ★ ★ **这四条是「显式拒」里最硬的**（计数为 0 就 `return {"ok": False, "stage": "selection"}` ⇒ 经工具层**必然失败、且失败原因明确**）· ★ 四条共用同一个 `_select_faces_for` 形状 ⇒ **一次改动修四条**。⚠ `axis` 的 mark 官方**没给**（圆柱面/圆锥面/两点）⇒ 先做前三条 |
| **5** | `solidworks_add_sketch_relation` | ★☆ 官方**只有描述行**一句（`Adds the specified constraint to the selected entities.`），**没有 mark** | ❌ 无 | ★ **隐蔽度最高**（Python 体一行、零报错线索，失败时只回一个 bool）⇒ 「用户投诉找不到原因」的头号候选。⚠ 但**修起来比前四条难**：需要的实体是**草图图元**（线/圆/点），而 `resolve_selection` 的 `ENTITY_KINDS` 只有 `EDGE`/`FACE`/`VERTEX`，**三种都不覆盖草图段** ⇒ 要么给底座加第四种 kind（动公共底座），要么复用 `sw_sketch_edit_ops._select_spec`（它已能做「草图段按 index」）—— ★ **排在第 5 正是因为它要动公共底座，不是抄一个 `pre_call` 就完** |

★ **通用建议（三条，按性价比）**：

1. **★ 先做 1 + 2**：两条共用一个 `pre_call`，`kind` 现成、官方 mark 现成 ⇒ 一次改动修两条。
2. **★ 再做第 4 组的四条**：复用 `tool_specs_batch74.py::_select_faces_for(mark, count)` 这个仓内**现成、已被 fact 503 检验过的形状**。
3. **★ 补一条静态门禁**：现状是「只有 `batch4`/`batch23`/`batch26`/`batch29`/`batch58`/`batch60`/`batch74` 记得写 `pre_call`」。
   判据可以照 `mcp-server/tool_registry.py::check_spec` 的形态写：**当 spec 的 `doc`（或目标函数 docstring）含
   「调用前 / 先选 / caller must first select / the selected entities / selected profiles / last selection」
   且 `pre_call is None and derived_args is None` ⇒ 报。**
   ★ 这条门禁一次就会抓住本表 **30 条**（36 条里减掉 5 条诊断型 + 1 条条件——那 6 条的 doc 里没有「先选」字样，
   得靠另一条判据「doc 里没有 `selection` 参数却引用 SelectionManager」）。

★ **诊断型那 5 条**（`selection_count` / `resolve_selection` / `selection_point` / `resolve_entity` / `current_selection`）
**单独处置、不要混进上面那批**：它们不是「缺 `pre_call`」，而是 **`inject="model"` 本身会清空它们要读的东西**
⇒ ★ 修法是**让它们绕开 `RESOLVERS["model"]`**（它们并不需要解析器去连文档），
★ ★ **而这一条改完，上面几档里凡以 `__current_selection__` 为入口的也一起活了** ⇒ 投入产出比最高，但**机制不同**，别当同一件事做。
