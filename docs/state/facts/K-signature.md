# K 维度 · 工具声明 ↔ 实际代码的对应关系

> 观测时间 **2026-10-24** · 观测方式：AST 静态解析（**不 import 任何 scripts 模块**，避免触发 COM）+ 读 `rc.all_specs()`
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_specs_vs_code.py --json docs/state/inventory-k.json
> ```

---

### K-01 501 条声明**全部**解析到真实函数：模块文件 0 缺、函数 0 缺

- **读数**：声明 **501** 条 · 解析到函数 **501** · 模块文件不存在 **0** · 函数不存在 **0**
- **观测方式**：`ToolSpec.module` → `scripts/<module 路径>.py`（或包 `__init__.py`）；在该文件**顶层** `def` 里找 `function`
- **证据**：`inventory-k.json` 的 `stats.resolved`
- **未确认**：只查**顶层** `def`；若某函数是类方法或嵌套函数，本判据会算「不存在」——本次 0 例，但口径如此

### K-02 `inject` 关键字 **零错配**

- **读数**：`inject` 非空但**不在**目标函数形参里的 **0** 条
- **判据**：`s.inject` 必须出现在函数形参名列表（`args.args` + `kwonlyargs`）
- **交叉核对**：`tool_registry.py:404-405` 逐字「注入用的**关键字名**必须与目标函数的**真实形参名**一致（`model` / `sw_app` / `study`）」
- **未确认**：无

### K-03 声明参数 **零错配**（经 `param_alias` 映射后）

- **读数**：声明参数映射到目标函数后**不在**形参里的 **0** 条
- **判据**：`param_alias` 里值为 `None` 的视为「由解析器消费、不传函数」，从比对集合中排除
- **未确认**：`derived_args` 产出的键（如 `spec`）**不在**本次比对集合内——它们是额外实参，不是声明参数

### K-04 **79** 条声明存在「函数有、声明面没有」的形参

- **读数**：函数形参中既不在声明参数、也不在 `inject`、也不在 `omitted_params` 的形参 ⇒ 命中 **79/501** 条
- **样本（逐字）**：`solidworks_sheet_metal_create_base_flange` 未暴露 `spec` · `solidworks_sheet_metal_create_swept_flange` 未暴露 `path_ref, profile_ref, spec`
- **未确认**：这些形参是否由别处（如 `extra_op`）补齐——本次未逐条核

### K-05 那 79 条里：**34** 条有 `derived_args`、**45** 条没有

| 分组 | 条数 | 记录员注（陈述） |
|---|---|---|
| 有 `derived_args` | **34** | `derived_args` 的契约是「从已声明标量派生额外实参并**并进**调用」（`tool_registry.py:414-419`）⇒ 未暴露形参**可能**由它补齐 |
| 无 `derived_args` | **45** | 这些形参既不来自声明面、也不来自 `derived_args` |

- **「无 derived_args」组的样本（逐字）**：
  - `solidworks_topology_create_demold_control` → `selection, selection_kind`
  - `solidworks_topology_create_symmetry_control` → `selection, selection_kind`
  - `solidworks_build_review_report` → `views, expected_outputs`
  - `solidworks_fillet` → `edges`
  - `solidworks_topology_set_iteration_options` → `iteration_option, iteration_limit`
  - `solidworks_config_create` → `options, if_exists, save`
  - `solidworks_config_activate` → `save`
  - `solidworks_config_set_custom_properties` → `property_type, save`
- **未确认**：这 45 条的未暴露形参**是否真有默认值**因而可不传——本次未读各函数的默认值；
  也未核注册器是否在调用时补默认参数（`tool_registry` 的调用装配段未逐行读）

### K-06 声明面与实现面的规模差

- **读数**：每条声明的「声明参数个数」与「函数形参个数」均记入 `inventory-k.json` 的 `rows`
- **未确认**：两者的整体分布（哪个方向偏多、偏多少）——本次未做分布统计

---

## 证据索引（每个事实号 → `inventory-k.json` 的键）

| 事实 | 证据载体 |
|---|---|
| K-01 | `stats.total` / `stats.resolved` / `counts.module_file_missing` / `counts.function_missing` |
| K-02 | `counts.inject_not_in_signature` + `inject_not_in_signature`（前 15 例） |
| K-03 | `counts.declared_param_not_in_signature` + `declared_param_not_in_signature`（前 15 例） |
| K-04 | `stats.has_undeclared_params`（79） + `rows[].undeclared` |
| K-05 | 由 `rows[].undeclared` 与各 spec 的 `derived_args` 是否存在交叉得出（见 `docs/state/inventory-k.json`） |
| K-06 | `rows[].declared` 与 `rows[].fn_params` |

---

## 本节未覆盖（留给后续补充）

- 45 条「无 derived_args」的未暴露形参**是否有默认值**（决定「不传也能调」还是「必填却传不进」）
- 注册器调用装配时如何处理未声明实参
- 装饰器路（45 个）与声明式路（501 条）的**功能重叠**
- 每个函数的实际可调用性（需 import，会触发 COM，本次刻意不做）
