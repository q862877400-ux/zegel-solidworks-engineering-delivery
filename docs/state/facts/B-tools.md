# B 维度 · MCP 工具声明层（`ToolSpec`）现状

> 观测时间 **2026-10-24** · 观测对象 `mcp-server/tool_specs_batch*.py` **116 个文件** + `mcp-server/tool_registry.py`
> 观测方式：脚本读 `register_capabilities.all_specs()`（**只读，未启动服务、未连 SolidWorks**）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_all_specs.py
> ```

---

### B-01 声明总数 501 条，`ToolSpec` 有 21 个字段

- **读数**：`len(all_specs()) == 501`；字段：`name title module function params inject needs_model read_only writes writes_source requires idempotent idempotent_source destructive load_automation extra_op doc omitted_params param_alias derived_args pre_call`
- **证据**：`mcp-server/tool_registry.py:391`（`class ToolSpec`）
- **未确认**：无

### B-02 工具名 100% 符合「`solidworks_` + 蛇形」正则

- **读数**：违规 **0** 条（正则 `^solidworks_[a-z][a-z0-9_]*$`）
- **读数（段数分布）**：2 段 **4** · 3 段 **110** · 4 段 **215** · 5 段 **137** · 6 段 **27** · 7 段 **8**
- **证据**：探测器输出；规则原文见 `docs/union-conventions.md:27`
- **未确认**：无

### B-03 4 条工具名只有 2 段（`solidworks_<动作>`，无「域」段）

| 工具名 | 位置 |
|---|---|
| `solidworks_chamfer` | `mcp-server/tool_specs_batch23.py:109` |
| `solidworks_fillet` | `mcp-server/tool_specs_batch23.py:135` |
| `solidworks_undo` | `mcp-server/tool_specs_batch52.py:94` |
| `solidworks_thicken` | `mcp-server/tool_specs_batch76.py:186` |

- **观测方式**：`name.split("_")` 段数 == 2 过滤
- **未确认**：规则 1 的判据只约束「前缀 + 蛇形」，对段数未作要求（`docs/union-conventions.md:27-41` 未写段数下限）⇒ 这 4 条是否算违规取决于读者口径

### B-04 4 个工具名**各被声明两次**

| 工具名 | 两处出处 |
|---|---|
| `solidworks_sketch_offset` | `tool_specs_batch66.py:104` · `tool_specs_batch116.py:206` |
| `solidworks_feature_cosmetic_thread` | `tool_specs_batch76.py:45` · `tool_specs_batch116.py:353` |
| `solidworks_sketch_spline` | `tool_specs_batch76.py:98` · `tool_specs_batch116.py:174` |
| `solidworks_export_flat_pattern_dxf` | `tool_specs_batch100.py:312` · `tool_specs_batch116.py:386` |

- **读数**：`collections.Counter(s.name)` 中计数为 2 的键 = 4 个
- **batch116 的自述目的**：文件头逐字「把 22 条「verified 但零工具」的能力接出来」（`mcp-server/tool_specs_batch116.py:1`）
- **未确认**：这 4 对里「后声明会覆盖前声明」还是「前一条被忽略」——注册器在建表时的具体行为本次未逐行核

### B-05 23 组「同一实现 ← 多个工具名」

- **读数**：按 `(module, function)` 分组，478 个实现中 **23 组**对应 2 个及以上工具名
- **下列为前 15 组**（探测器输出被截断，第 16–23 组用 B 维度复现命令可看全）：

| 实现 | 工具名 A | 工具名 B |
|---|---|---|
| `sw_assembly.collect_mate_feature_summary` | `solidworks_assembly_list_mates` | `solidworks_assembly_performance_analysis_report` |
| `sw_assembly.iter_feature_tree` | `solidworks_assembly_iter_feature_tree` | `solidworks_assembly_component_pattern_report` |
| `sw_assembly_doc.insert_explode_line_sketch_report` | `solidworks_insert_explode_line_sketch` | `solidworks_assembly_explode_line_sketch` |
| `sw_curve_and_split.insert_curve_through_points` | `solidworks_insert_curve_through_points` | `solidworks_curve_through_points` |
| `sw_delivery.collect_assembly_bom` | `solidworks_collect_assembly_bom` | `solidworks_assembly_sequence_report` |
| `sw_drawing_query.current_sheet_info` | `solidworks_drawing_get_current_sheet` | `solidworks_drawing_current_sheet_info` |
| `sw_drawing_query.sheets_summary` | `solidworks_drawing_list_sheets` | `solidworks_drawing_sheets_summary` |
| `sw_export.export_flat_pattern_dxf` | `solidworks_export_flat_pattern_dxf` | `solidworks_export_flat_pattern_dxf`（**同名**，见 B-04）|
| `sw_feature_entry_ops.create_flatten_surface` | `solidworks_flatten_surface` | `solidworks_surface_flatten` |
| `sw_feature_entry_ops.insert_cosmetic_thread` | `solidworks_feature_cosmetic_thread` | `solidworks_feature_cosmetic_thread`（**同名**）|
| `sw_part.revolve_cut` | `solidworks_revolve_cut` | `solidworks_feature_revolve_cut` |
| `sw_part.sketch_spline` | `solidworks_sketch_spline` | `solidworks_sketch_spline`（**同名**）|
| `sw_render_material.list_render_materials` | `solidworks_list_render_materials` | `solidworks_render_material_list` |
| `sw_simulation_study_options.list_setter_summary` | （第 14 组，截断）| — |
| （第 15 组，截断）| — | — |

- **未确认**：每组的两个名字是否**故意并存**（例如「同一实现的两种视角」）——`ToolSpec` 里没有「别名/取代」字段可表达，故从声明本身看不出意图

### B-06 参数 1,186 个；`_mm` 255 个、`_deg` 37 个

- **读数**：总参数 1,186；以 `_mm` 结尾 **255**；以 `_deg` 结尾 **37**
- **规则原文**：`docs/union-conventions.md:43`（「长度参数必须 `_mm` 结尾，角度必须 `_deg` 结尾」）
- **未确认**：无

### B-07 12 个参数名命中「像长度/角度但无后缀」的词表

| 工具 | 参数 |
|---|---|
| `solidworks_sheet_metal_create_base_flange` | `reverse_thickness` |
| `solidworks_sheet_metal_create_one_bend` / `create_edge_flange` / `create_swept_flange` / `insert_miter_flange` | `use_default_radius`（×4）|
| `solidworks_mold_core_cavity_split` | `thickness` · `offset` |
| `solidworks_mold_parting_surface` | `angle` |
| `solidworks_export_bmp` | `pixel_width` · `pixel_height` |
| `solidworks_drawing_set_sheet_scale` | `scale_anno_text_height` |
| `solidworks_weldment_insert_end_cap` | `is_given_offset` |

- **观测方式**：参数名匹配 `(depth|width|height|length|radius|diameter|thickness|gap|offset|clearance|angle)$` 且不以 `_mm`/`_deg` 结尾
- **记录员注（陈述，不判断）**：上表里 `use_default_radius` / `reverse_thickness` / `is_given_offset` 是**布尔名**，词表命中属启发式副作用；`pixel_width`/`pixel_height` 的名词是「像素」
- **未确认**：这些参数的**类型**是否真为长度/角度，本次未逐条核 `Param.type`

### B-08 `inject` 实际出现 **22 种取值**，契约文件登记 4 种

- **读数（按条数降序）**：`model` 274 · `''`(空) 58 · `study` 33 · `view` 23 · `manager` 17 · `sw_app` 13 · `doc` 13 · `asm_model` 12 · `cost_manager` 9 · `drawing_model` 9 · `selection` 9 · `sldworks` 5 · `sw` 5 · `defaults` 4 · `mesh` 3 · `results` 3 · `cost_part` 3 · `component` 2 · `motion_study` 2 · `cost_analysis` 2 · `options` 1 · `cost_body` 1
- **契约文件写法**：`docs/union-conventions.md` 与 `mcp-server/tool_registry.py:402-403` 均写「约定俗成的四个：`""` / `"model"` / `"sw_app"` / `"study"`」
- **实现侧说明**：`ToolSpec` docstring 逐字「取值由**调用方注册的解析器**决定 —— 本模块**不硬编码任何宿主 API**」（`mcp-server/tool_registry.py:400-401`）
- **未确认**：那 18 个额外取值各自对应哪个解析器、是否都有解析器——本次未核 `register_capabilities` 的 resolver 表

### B-09 `doc`（会变成 MCP 工具描述）空 **4** 条，其余中位 264 字符

- **读数**：空 **4** · 长度中位 **264** · 最短 **0** · 最长 **1,606**；首字符分布前五：`★` 225 · `R` 60 · `C` 49 · `A` 26 · `S` 20
- **空 doc 的 4 条**（全部在 `tool_specs_batch115.py`，声明里无 `doc=` 字段）：
  `solidworks_catalog_domains`:32 · `solidworks_catalog_retrieve`:40 · `solidworks_catalog_contract`:80 · `solidworks_catalog_exposure`:95
- **这 4 条的共同点（陈述）**：`module="engineering.catalog"`，是 `scripts/engineering/` 里**唯一被工具层引用**的模块
- **未确认**：无

### B-10 `read_only` 461 条未声明（`None`），`writes` 覆盖 1/501

- **读数**：`read_only`：`None` **461** · `True` **39** · `False` **1**
- **读数**：效应声明 `writes` 非空 **1/501**
- **字段意图原文**：`mcp-server/tool_registry.py:428`（「`read_only`: 只读工具 ⇒ `readOnlyHint=True`」）；`:447-449`（效应声明「**可能改**哪几类状态」）
- **未确认**：`None` 在注册时是否被默认成某个 hint——本次未核 `build_input_model`/注册路径对 `None` 的处理

### B-11 注册前门禁 `check_specs` 当前返回 **5 条**，`register()` 会整体拒绝

- **观测方式**：调用 `tool_registry.check_specs(rc.all_specs())`
- **原文（逐字）**：
  ```
  GateError: 声明未过门禁，未注册任何工具：
    - 规则 2 违反：工具 'solidworks_feature_revolve_cut' 的入参 'angle_rad' 像是**角度**，却不以 '_deg' 结尾 —— 要么改名（`angle_rad_deg`），要么在 `_ANGLE_SUFF…`
    - 工具名重复：'solidworks_sketch_spline'
    - 工具名重复：'solidworks_sketch_offset'
    - 工具名重复：'solidworks_feature_cosmetic_thread'
    - 工具名重复：'solidworks_export_flat_pattern_dxf'
  ```
- **抛出位置**：`mcp-server/tool_registry.py:964-967`；该函数 docstring 逐字「先 `check_specs` 全量校验 —— **有任何问题就整体不注册**（不让半套工具进到运行期）」（`:957-958`）
- **`all_specs()` 侧**：`import register_capabilities` **成功**，返回 501 条 ⇒ **声明可读、注册拒绝**是两条不同路径
- **未确认**：MCP 服务端启动时是否捕获该异常并降级——本次未启动服务验证（`mcp.json` 里 `solidworks: false`）

### B-12 仓库内有测试断言 `len(all_specs()) == 480`

- **证据**：`tests/test_server_wiring.py:300` 逐字 `assert len(all_specs()) == 480`；`tests/test_b1_b5_closeout_297.py:40` 记 `TRUTH_SPECS = 480`
- **实测**：**501**
- **同文件的另一处钉死**：`tests/test_b1_b5_closeout_297.py:64` 记 `test_mcp_protocol_layer.py → assert n == 524`
- **未确认**：这 480 是何时写下的、之后哪些批次增加了声明——本次未查 `git log -S'== 480'`

### B-13 与 B-11/B-12 相关的测试在**收集期**即报错

- **观测方式**：`python -m pytest tests\test_server_wiring.py -q -p no:cacheprovider`
- **读数**：**8 errors**（收集期），错误类型 `tool_registry.GateError`，未执行任何用例
- **报错的用例名（逐字）**：`test_cadstudio_tools_survive` · `test_all_declarative_specs_are_registered` · `test_expected_batch_size` · `test_declarative_tools_are_solidworks_prefixed` · `test_no_name_collision_with_upstream` · `test_every_injection_kind_has_a_resolver` · `test_every_registered_declarative_tool_has_a_description`
- **记录员注（陈述）**：这些用例名与 B-09（description）、B-04（name collision）、B-08（injection kind）逐一对应
- **未确认**：其它测试文件是否同因受阻——本次只跑了这一个文件

### B-14 `release_check.py` 不含工具注册门禁

- **证据（逐字）**：`scripts/release_check.py:1083` 写「⚠ 它不能代替 `tool_registry` 那套门禁 —— ★ 只是把装饰器路也**纳入可见范围**。」
- **实测**：`python scripts\release_check.py` ⇒ **EXIT 0 / status pass**（与 B-11 同时成立）
- **未确认**：`release_check` 的哪一道门「纳入可见范围」、纳入到什么程度——本次未逐行读该段

---

## 本节未覆盖（留给后续补充）

- 每个 `Param` 的 `type`/`default`/`description` 形态是否统一（只统计了名字后缀）
- `param_alias` / `derived_args` / `pre_call` / `omitted_params` 的使用分布
- 装饰器路（`@mcp.tool` ×45）与声明路的一致性
- 501 条声明对应的函数**是否实际存在且可调用**（`inspect.signature` 全量比对）
