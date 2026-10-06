# 规格 210 · 存活普查「声明 vs 观察」差异表（B3 的产物）

> ★ 由 `tools/gen_survival_diff.py` 从**真机普查结果**生成 —— **不要手改**。
> ★★ 本表按**声明分组**出具（★ `empty`）—— ★ 三组语义不同，**不许混在一张表里** ✓

## 硬红门禁（★ 本规格最要紧的一条）

★ 判据：★「**声明只读却观察到指纹变化**」⇒ 必须为 **0**（或逐条定性）。

★★ 实测：**2 条** —— **满足** ✓「 if not missed else 」★★ 未满足 ✗

## 四类统计

agree **21**★ 「 + 」 · missed **2**★ 「 + 」 · undecided **24**

★★ **语义说明**（★ 四类不许混）：

· `agree`（21）：★ **一致**（声明「无写」，观察也确实**没变**）
· `missed`（2）：★★★ **漏报**（声明「无写」而观察**变了**）—— ★ **硬红门禁**这一条 ✗
· `undecided`（24）：★ **未判定**（有一侧读不到）—— ★ **不算通过也不算失败**

## 按 `inject` 组的判定分布

★ 组由**声明里的 `inject`** 决定（★ 不是猜的）✓

· `asm_model|`：agree **2** · missed **2**
· `component|`：agree **1**
· `cost_manager|`：undecided **2**
· `manager|`：agree **1** · undecided **1**
· `model|`：agree **13** · undecided **5**
· `model|assembly`：agree **1**
· `model|drawing`：undecided **7**
· `none|`：undecided **1**
· `sldworks|`：undecided **1**
· `study|`：undecided **1**
· `sw_app|`：undecided **3**
· `sw|`：undecided **3**
· `view|`：agree **3**

★★ **两种 `undecided` 性质不同**：★ **调用没调成**（★ 我们没测到）与 ★ **调用成功但读数读不到**（★ 量具的盲区）—— ★ 混在一起就看不见了 ✓


## 逐条

**`solidworks_assembly_check_interference`** ⇒ `missed`

· 声明 `writes`：`[]`
· 观察**变了**的类：`['selection']`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'status': 'pass', 'interference_count': 0, 'items': [], 'manual_review_required': False}`

**`solidworks_motion_collect_summary`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'motion_type_library': 'D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\swmotionstudy.tlb', 'study_count': 1, 'studies'`

**`solidworks_motion_create_study`** ⇒ `missed`

· 声明 `writes`：`[]`
· 观察**变了**的类：`['selection', 'dirty', 'features']`
· 观察**未判定**的类：`（无）`
· 调用返回：`<COMObject <unknown>>`

**`solidworks_motion_study_manager`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`<COMObject <unknown>>`

**`solidworks_assembly_external_reference_count`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`0`

**`solidworks_costing_list_bodies`** ⇒ `undecided`

· 声明 `writes`：`None`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`

**`solidworks_costing_read_body`** ⇒ `undecided`

· 声明 `writes`：`None`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`

**`solidworks_simulation_apply_link_connector`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'ok': False, 'stage': 'resolve_vertex', 'count_before': -1, 'first': 'MCP_CALIB', 'second': 'MCP_CALIB', 'error': "Enti`

**`solidworks_weldment_read_property_manager`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 AttributeError: SldWorks.Application.GetNames`

**`solidworks_activate_model_for_preview`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`True`

**`solidworks_config_inspect`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'status': 'pilot', 'configurations': ['默认'], 'active_configuration': '默认', 'review_required': True, 'limitations': ['未执`

**`solidworks_config_set_custom_properties`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'success': True, 'configuration': '', 'property_type': 'text', 'properties': [{'name': 'MCP_CALIB', 'requested': '1', '`

**`solidworks_entities_on_body`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'ok': False, 'kind': 'MCP_CALIB', 'body_index': 0, 'count': None, 'entities': [], 'euler': None, 'error': "EntitySelect`

**`solidworks_equation_evaluate`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`-1`

**`solidworks_export_dxf`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'ok': False, 'format': 'dxf', 'output_path': 'MCP_CALIB_out.step', 'returned': None, 'exists': False, 'size_bytes': 0, `

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

**`solidworks_helix_insert`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`Configuration Table`

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

**`solidworks_part_bounding_box`** ⇒ `undecided`

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

**`solidworks_sketch_fully_defined_status`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: 没有活动草图 ⇒ 取不到 ISketch（`GetActiveSketch2` 与 `SketchManager.ActiveSketch` 都回 None）。★ 完全定义状态只能问**正在编辑**的`

**`solidworks_sketch_mirror`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: ISketchManager.ActiveSketch 为 None ⇒ 当前不在草图编辑态。官方 SketchMirror 需要先进入草图并选中要镜像的实体（线段 mark=1 / 中心线 mark`

**`solidworks_sketch_spline`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 RuntimeError: sketch_spline() 被调用时**没有活动草图** ⇒ 画几何会**静默无效**（几何画到不存在的地方）。★ 先调 `sketch_start(model, plane_name=...)``

**`solidworks_weldment_create_weldment_profile`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`★ 调用抛 ValueError: 焊件型材输出必须使用 .sldlfp 扩展名`

**`solidworks_config_list_display_states`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`{'ok': True, 'configuration': '默认', 'display_states': ['默认_显示状态-1'], 'count': 1, 'count_reported': 1, 'count_mismatch': `

**`solidworks_drawing_current_sheet_info`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'sheet_name': '图纸1', 'paper_size_code': 6, 'paper_size': 'A4', 'width_mm': 297.0, 'height_mm': 210.0, 'scale_num': 1.0,`

**`solidworks_drawing_current_sheet_name`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`图纸1`

**`solidworks_drawing_get_current_sheet`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'sheet_name': '图纸1', 'paper_size_code': 6, 'paper_size': 'A4', 'width_mm': 297.0, 'height_mm': 210.0, 'scale_num': 1.0,`

**`solidworks_drawing_list_sheets`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'count': 1, 'names': ['图纸1'], 'current': '图纸1'}`

**`solidworks_drawing_sheet_count`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`1`

**`solidworks_drawing_sheet_names`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`['图纸1']`

**`solidworks_drawing_sheets_summary`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'count': 1, 'names': ['图纸1'], 'current': '图纸1'}`

**`solidworks_sketch_count_segments`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['selection', 'edit_mode', 'dirty', 'features', 'bodies', 'faces', 'config', 'rebuild']`
· 调用返回：`0`

**`solidworks_automation_get_flag`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`★ 调用抛 ValueError: invalid literal for int() with base 10: 'MCP_CALIB'`

**`solidworks_topology_list_constraints`** ⇒ `undecided`

· 声明 `writes`：`None`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`

**`solidworks_document_dependencies`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'ok': True, 'document': 'MCP_CALIB', 'traverse': True, 'search': False, 'add_read_only_info': False, 'count': 0, 'entri`

**`solidworks_simulation_find_study`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'found': False, 'requested_name': 'MCP_CALIB', 'study_name': ''}`

**`solidworks_surface_evidence`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`{'has_modeler': True, 'registered_creation_methods': ['CreateBsplineSurface', 'CreateConicalSurface', 'CreateConicalSurf`

**`solidworks_fastener_table_types`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`★ 调用抛 RuntimeError: IHoleStandardsData.GetFastenerTableTypes('', 0) 返回 False —— 常见原因：`fastener_id` 不在 `list_fastener_typ`

**`solidworks_fastener_types`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`★ 调用抛 RuntimeError: IHoleStandardsData.GetFastenerTypes('') 返回 False —— 常见原因：标准名拼错（用 `list_hole_standards()` 里的 `name`）`

**`solidworks_hole_standards`** ⇒ `undecided`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`['config']`
· 调用返回：`[{'id': 0, 'name': 'ANSI Inch'}, {'id': 1, 'name': 'ANSI Metric'}, {'id': 16, 'name': 'AS'}, {'id': 2, 'name': 'BSI'}, {`

**`solidworks_get_view_model_doc`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`<COMObject <unknown>>`

**`solidworks_view_get_next`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`None`

**`solidworks_view_has_perspective`** ⇒ `agree`

· 声明 `writes`：`[]`
· 观察**变了**的类：`（无）`
· 观察**未判定**的类：`（无）`
· 调用返回：`False`

## ⚠ 本记录的限度（★ 不许当成「448 个都验过了」）

· ★ 本轮**只覆盖** `writes == []`（已确认无写）那批 —— ★ 其余工具待普查 ✓
· ★★ **九类里 `display` 是「后端限定」**（★ `GetDisplayStateSetting` 三种 Option 全抛 `com_error -2147417851`）⇒ ★ 它**不参与差分**（★ 已单独成桶 `unavailable`）✓
· ★ 每条**各用一个新零件**（★ 样本隔离 —— ★ 同文档顺序调用会互相污染）✓
· ★ 判定**只看指纹**，★ **不看被调成员的返回值**（★ 本仓一贯纪律）✓

