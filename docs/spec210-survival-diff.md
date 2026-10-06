# 规格 210 · 存活普查「声明 vs 观察」差异表（B3 的产物）

> ★ 由 `tools/gen_survival_diff.py` 从**真机普查结果**生成 —— **不要手改**。
> ★★ 本表按**声明分组**出具（★ `empty`）—— ★ 三组语义不同，**不许混在一张表里** ✓

## 硬红门禁（★ 本规格最要紧的一条）

★ 判据：★「**声明只读却观察到指纹变化**」⇒ 必须为 **0**（或逐条定性）。

★★ 实测：**0 条** —— **满足** ✓

## 四类统计

agree **47**

★★ **语义说明**（★ 四类不许混）：

· `agree`（47）：★ **一致**（声明「无写」，观察也确实**没变**）

## 逐条

**`solidworks_activate_model_for_preview`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`True`

**`solidworks_assembly_check_interference`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'asm_model' 但没给对应对象`

**`solidworks_assembly_external_reference_count`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'component' 但没给对应对象`

**`solidworks_automation_get_flag`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：pref`

**`solidworks_config_inspect`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'status': 'pilot', 'configurations': ['默认'], 'active_configuration': '默认', 'review_required': True, 'limitations': ['未执`

**`solidworks_config_list_display_states`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'ok': True, 'configuration': '默认', 'display_states': ['<默认>_显示状态 1'], 'count': 1, 'count_reported': 1, 'count_mismatch'`

**`solidworks_config_set_custom_properties`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：properties`

**`solidworks_costing_list_bodies`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'cost_manager' 但没给对应对象`

**`solidworks_costing_read_body`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：body_name`

**`solidworks_document_dependencies`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：document`

**`solidworks_drawing_current_sheet_info`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_drawing_current_sheet_name`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_drawing_get_current_sheet`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_drawing_list_sheets`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_drawing_sheet_count`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_drawing_sheet_names`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_drawing_sheets_summary`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）`

**`solidworks_entities_on_body`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：kind`

**`solidworks_equation_evaluate`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`-1`

**`solidworks_export_dxf`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：output_path`

**`solidworks_fastener_table_types`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: IHoleStandardsData.GetFastenerTableTypes('', 0) 返回 False —— 常见原因：`fastener_id` 不在 `list_fastener_typ`

**`solidworks_fastener_types`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: IHoleStandardsData.GetFastenerTypes('') 返回 False —— 常见原因：标准名拼错（用 `list_hole_standards()` 里的 `name`）`

**`solidworks_feature_whats_wrong`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'count': 0, 'entries': [], 'error': None, 'source_member': 'IModelDocExtension.GetWhatsWrongCount'}`

**`solidworks_get_costing_manager`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`<COMObject <unknown>>`

**`solidworks_get_view_model_doc`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'view' 但没给对应对象`

**`solidworks_helix_insert`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：height_mm`

**`solidworks_hole_standards`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`[{'id': 0, 'name': 'ANSI Inch'}, {'id': 1, 'name': 'ANSI Metric'}, {'id': 16, 'name': 'AS'}, {'id': 2, 'name': 'BSI'}, {`

**`solidworks_list_render_materials`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`[]`

**`solidworks_mold_evidence`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'counts': {'parting_lines': None, 'parting_surfaces': None, 'cavity_surfaces': None, 'core_surfaces': None}, 'parting_t`

**`solidworks_motion_collect_summary`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'asm_model' 但没给对应对象`

**`solidworks_motion_create_study`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'asm_model' 但没给对应对象`

**`solidworks_motion_study_manager`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'asm_model' 但没给对应对象`

**`solidworks_part_bounding_box`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: IPartDoc.GetBodies2(0, False) 没拿到实体 ⇒ 零件里可能没有实体（先建一个特征，或把 body_index 调小）`

**`solidworks_part_mass_properties`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'volume': 0.0, 'surface_area': 0.0, 'center_of_mass': [0.0, 0.0, 0.0], 'density': 0.0, 'mass': 0.0, 'units': {'volume':`

**`solidworks_read_document_units`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'ok': True, 'raw': '(0, 1, 8, 2, 0)', 'tuple': [0, 1, 8, 2, 0], 'tuple_named': {'LengthUnit': 0, 'FractionBase': 1, 'Fr`

**`solidworks_simulation_apply_link_connector`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：first`

**`solidworks_simulation_find_study`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：study_name`

**`solidworks_sketch_count_segments`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ derived_args 抛 RuntimeError: 取不到草图：试过 ['Sketch1', '草图1']；特征树里也没找到以 Sketch/草图 开头的特征`

**`solidworks_sketch_fully_defined_status`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 没有活动草图 ⇒ 取不到 ISketch（`GetActiveSketch2` 与 `SketchManager.ActiveSketch` 都回 None）。★ 完全定义状态只能问**正在编辑**的`

**`solidworks_sketch_mirror`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: ISketchManager.ActiveSketch 为 None ⇒ 当前不在草图编辑态。官方 SketchMirror 需要先进入草图并选中要镜像的实体（线段 mark=1 / 中心线 mark`

**`solidworks_sketch_spline`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：points`

**`solidworks_surface_evidence`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'sw_app' 但没给对应对象`

**`solidworks_topology_list_constraints`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'study' 但没给对应对象`

**`solidworks_view_get_next`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'view' 但没给对应对象`

**`solidworks_view_has_perspective`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'view' 但没给对应对象`

**`solidworks_weldment_create_weldment_profile`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 缺必填形参：output_path`

**`solidworks_weldment_read_property_manager`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 声明注入 'manager' 但没给对应对象`

## ⚠ 本记录的限度（★ 不许当成「448 个都验过了」）

· ★ 本轮**只覆盖** `writes == []`（已确认无写）那批 —— ★ 其余工具待普查 ✓
· ★★ **九类里 `display` 是「后端限定」**（★ `GetDisplayStateSetting` 三种 Option 全抛 `com_error -2147417851`）⇒ ★ 它**不参与差分**（★ 已单独成桶 `unavailable`）✓
· ★ 每条**各用一个新零件**（★ 样本隔离 —— ★ 同文档顺序调用会互相污染）✓
· ★ 判定**只看指纹**，★ **不看被调成员的返回值**（★ 本仓一贯纪律）✓

