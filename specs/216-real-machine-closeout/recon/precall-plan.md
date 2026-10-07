# 规格 216 · 预选族 14 条的**判型**与修法计划（T-216-05）

> **来源**：★ `docs/preselect-family-baseline.json`（14 条）· ★ 逐条**读目标函数体**（本次真读，非推断）·
> ★ 事实 503（`RESOLVERS[inj]` **会清空选区** ⇒ 选区必须由 `pre_call` 在注入**之后**重建）✓
> ⚠ **本表推翻了 goal 里"9 条要修、5 条不动"的分法** —— ★ 真读之后分法是下面这**四型** ✓

## 一、判型结果（★ 14 条，每条给**依据行**）

| # | 工具 | 目标函数 | ★ 型 | ★ 依据（读到的原文） |
|---|---|---|---|---|
| 1 | `solidworks_assembly_suppress_component` | `sw_assembly.suppress_component` | ★★ **假阳性** | `L15 _select_by_id(asm_model.Extension, component_name, "COMPONENT")` ⇒ ★ **它自己按名字选** ✓ |
| 2 | `solidworks_insert_form_tool` | `sw_sheet_metal.insert_form_tool_report` | ★★ **假阳性** | `L44 SS.select_entity_by_index(model, "FACE", face_index)` ＋ `L49-53` **回读计数、为 0 就报错** ⇒ ★ **自足且判据正确** ✓ |
| 3 | `solidworks_part_insert_dome` | `sw_part.insert_dome_report` | **A** 造选区 | 零选区 token；官方 Remarks 要求先选面（与 #4 同坑）|
| 4 | `solidworks_part_insert_composite_curve` | `sw_part.insert_composite_curve_report` | **A** | docstring 逐字「⚠ 调用前**必须先用 mark = 1 选好实体**」；零 token |
| 5 | `solidworks_insert_reference_point` | `sw_ref_geometry.insert_reference_point` | **A** | 零 token；官方要求选实体 |
| 6 | `solidworks_section_properties` | `sw_mass_property.section_properties` | **A** | 零 token；`ISectionProperties` 需选面/基准面 |
| 7 | `solidworks_assembly_dissolve` | `sw_assembly_doc.dissolve_assembly` | **A** | 零 token；`DissolveSubAssembly` 需选中子装配 |
| 8 | `solidworks_sketch_stretch_entities` | `sw_sketch_modify_ops.sketch_stretch` | **A** | docstring 逐字「官方说明…'Stretch the **selected** entities' ⇒ 要求先选中实体」；零 token |
| 9 | `solidworks_selection_point` | `sw_selection_spec.selection_point` | **B** 读当前选区 | 语义**就是**取"当前选区那个点"（`GetSelectionPoint2`）|
| 10 | `solidworks_measure_selection` | `sw_measure.measure_selection_report` | **B** | 语义**就是**"量当前选区"（读 `GetSelectedObjectCount2`）|
| 11 | `solidworks_drawing_insert_balloons` | `sw_drawing_create_missing.auto_insert_balloons` | **B/D** | 官方第 1 步逐字「Select one or more **views or sheets**」；函数读计数并显式拒 |
| 12 | `solidworks_part_axis` | `sw_part.create_axis_report` | **D** 需指定参照 | 读计数 + 显式拒；★ 语义是"**从当前选中几何**建轴" ⇒ **选哪个**必须由调用方说 |
| 13 | `solidworks_topology_create_demold_control` | `sw_topology.create_demold_control` | **D** | ★ docstring 逐字「调用方须**先选好拔模方向的面/边/基准面**」⇒ ★ **不能由函数乱造**（方向有语义）|
| 14 | `solidworks_topology_create_symmetry_control` | `sw_topology.create_symmetry_control` | **D** | 同上，逐字「调用方须**先选好对称平面**」|

★ **分布**：★ **假阳性 2** · ★ **A（造选区）6** · ★ **B（读当前）3** · ★ **D（需指定参照）3** ✓

## 二、四型各自的修法（★ 不同型**不能**用同一种修法）

### ★★ 假阳性（2 条）⇒ **不动工具，修门禁**
★ 这两条的函数**自己就会选**，★ 而 `scripts/check_preselect_family.py` 的 `SELF_SELECT` token 集**不含**
`_select_by_id` / `select_entity_by_index` ⇒ ★★ **门禁自己的假阳性**（★ 与本仓已修过的两次同型：
`audit_byref_args` 的 `BYREF_OK` 只认裸名 · `check_probe_reuse` 的判据过宽）✓
⇒ ★ 修法：★ **把这两个名字加进 `SELF_SELECT`**；★ 并把 baseline 这两条的 verdict
**从"待修工作项"改成"已自足（门禁假阳性）"**，★ 写明依据行 ✓

### **A 型（6 条）⇒ `pre_call` 造选区**
★ 形状照 `mcp-server/tool_specs_batch74.py` 的 `_select_faces_for` ✓
★ 要点：★ `pre_call` 在**注入之后**跑（★ 事实 503）⇒ ★ 那时选区已被清空 ⇒ **必须重建** ✓
⚠ **每条要先定"选什么"的判据**（★ 不许乱选）：★ 首选"**唯一实体**"（如单实体板的唯一面）
★ 或"**参数指定的序号**"（★ 如 #2 的 `face_index` 就是既有范式 ✓）；★ 判据写进 ToolSpec 的注释 ✓

### **B 型（3 条）⇒ 加**声明式 `selection` 入参**
★★ 这 3 条的**语义就是"读调用方当前选的东西"** ⇒ ★ 给它**乱造**一个选区会**改语义** ✗
⇒ ★ 正解：★ 让调用方**声明**要量/要取的对象（★ 本仓既有的 `selection` 形态入参 +
`resolve_selection` 机制 ✓）⇒ ★ `pre_call` 在注入后 `resolve_selection` 把它**选回来** ✓
★ 附带好处：★ 加 `selection` 入参后，★ 本门禁的第 ③ 条条件（"没有 `selection` 形态入参"）
**自动不再命中** ⇒ ★ 这正是门禁预留的**正道出口** ✓

### **D 型（3 条）⇒ 同 B（加声明式 `selection`），但**判据更严**
★ 这 3 条要的**不是"随便一个选区"，而是有语义的参照**（拔模方向的面/边/基准面 · 对称平面 ·
建轴的几何）⇒ ★★ **绝不能由函数自己挑**（挑错方向 ⇒ 结果是错的而**看不出来**）✗
⇒ ★ 一律**加 `selection` 入参**（★ 与 B 同形），★ 并在 docstring 里写清"这项选择**决定结果语义**" ✓

## 三、执行顺序（★ 按"风险 ÷ 收益"）

```
① 假阳性 2 条：修门禁 + 改 baseline verdict        ★ 最便宜、且防未来误报
② A 型 6 条：各加 pre_call（先定"选什么"的判据）    ★ 主体工作量
③ B/D 型 6 条：加 selection 入参 + pre_call 选回     ★ 要改工具契约（Param 变更）
④ 逐条真机验证 + check_preselect_family.py 退出 0 + 全量 pytest
```

## 四、★ 一个必须先说清的边界

★ 本规格**只保证"选区能被建立"**（★ 即"注册 ≠ 能跑"那一类的另一半）——
★ 而**特征能不能真建成**是另一件事（★ 本仓既有 14 条里有 `stitched` 的钣金族就是例证）✓
⇒ ★ 每条的验收读数是**两段**：★ ① 选区计数 > 0 ✓ · ★ ② **特征树增量**（★ 不看返回值）✓
