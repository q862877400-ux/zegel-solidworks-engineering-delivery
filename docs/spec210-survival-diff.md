# 规格 210 · 存活普查「声明 vs 观察」差异表（B3 的产物）

> ★ 由 `tools/gen_survival_diff.py` 从**真机普查结果**生成 —— **不要手改**。
> ★★ 本轮取的是 **`writes == []`（已确认无写）** 那批 —— ★ 它们正是**硬红门禁**盯的那一批 ✓

## 硬红门禁（★ 本规格最要紧的一条）

★ 判据：★「**声明只读却观察到指纹变化**」⇒ 必须为 **0**（或逐条定性）。

★★ 实测：**0 条** —— **满足** ✓

## 四类统计

agree **20**

★★ **语义说明**（★ 四类不许混）：

· `agree`（20）：★ **一致**（声明「无写」，观察也确实**没变**）

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

## ⚠ 本记录的限度（★ 不许当成「448 个都验过了」）

· ★ 本轮**只覆盖** `writes == []`（已确认无写）那批 —— ★ 其余工具待普查 ✓
· ★★ **九类里 `display` 是「后端限定」**（★ `GetDisplayStateSetting` 三种 Option 全抛 `com_error -2147417851`）⇒ ★ 它**不参与差分**（★ 已单独成桶 `unavailable`）✓
· ★ 每条**各用一个新零件**（★ 样本隔离 —— ★ 同文档顺序调用会互相污染）✓
· ★ 判定**只看指纹**，★ **不看被调成员的返回值**（★ 本仓一贯纪律）✓

