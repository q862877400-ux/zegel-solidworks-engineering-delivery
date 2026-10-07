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

---

## 五、★★ A 型逐条**深化**（★ 2026-10-07 补 —— **读台账第一现场之后**，★ 它几乎把 6 条全答了）

> ★★ **起因**：★ 我原本打算"给 6 条各加一个 `pre_call` 造选区"。
> ★ 而在动手前按 `AGENTS.md` 的纪律**先读该能力的 `limitations`** ⇒ ★★ **结论变了 3 条** ✓
> ⚠ 同一轮还发现我差点违反**known-facts 186**：「轮 249-251 **重复造了证据脚本**，
>   而仓库里早有更强的既有冒烟 ⇒ ★ 先找要覆盖『**判据 + 证据脚本 + 批量入口**』三样」✓

### 5.1 `insert_dome` —— ★ 可修，且**做法已被既有冒烟证明**

| 事实 | 逐字依据 |
|---|---|
| 官方要 **mark=1**，传 mark=0 报 `0x8002000F` | 台账 `modeling_feature_readback_tools`：「传 mark=0 时 `InsertDome` 报 **`0x8002000F` 非选择性的参数** —— ★ 那个错误**看不出是 mark 的问题**」✓ |
| **选择形态已被证明** | `tools/verify_dome_smoke.py` L133-139：先 `SelectByID2("", "FACE", W/2, H/2, D, …, 0, callout, 0)`，★ 然后 `ClearSelection2(True)`，★ 再 **`SelectByID2(…, mark=1, …)`** ⇒ ★ 该冒烟 **9/9** ✓ |
| ⚠ **而规则 3 不许工具收裸坐标** | 故**不能**照抄冒烟里的 `W/2, H/2` ⇒ ★ 正解是用**声明式选择器**（本仓既有 `sw_selection_spec.resolve_selection` / `"+z"` 那一族）✓ |
| ★ 一个**未定**的点 | ★ `SetSelectedObjectMark(AtIndex, Mark, Value)` 的**第 3 参语义**（反射 arity=3）未查 ⇒ ★ 要么**实测**它，要么走"先按点选 mark=0 → 清选 → 再 mark=1"这条**已被证明**的两步式 ✓ |

### 5.2 `insert_composite_curve` —— ★★ **不是"补选区"能修的：已查清是后端墙**

★★ 台账 `part_and_features` 逐字（**6 种选法全败、已按事实 53 强停**）：
> 累计 **6 种选法全部失败**（草图整体 / 实体边 / 草图段 × 各两种选法）⇒ ★★★ **卡点查明**：
> `IEntity.Select4` **没有 mark 参数**（选完 mark 仍是 0），而 `SelectByID2` 需要**名字**、
> **边与草图段都没有名字** ⇒ **「选中 2 个实体 + mark=1」这个官方前提，在这条后端上我没能同时满足**

⇒ ★★ **结论**：★ 给它补选区**注定无效** ⇒ ★ 应归入**如实记为能力缺口**那一档
（★ 与本规格 ② AVI 的处置同型）✓ —— ★ 这也意味着 **A 型从 6 条降到 5 条** ✓

### 5.3 `insert_reference_point` —— ★ 可修，且**失败原因已写明**

★ 台账 `ref_geometry` 逐字：
> ★ **两处都要「先选后调」（按 mark）**：… 点（`InsertReferencePoint`）要先选实体，
> **而选面必须紧接着调用**（★ 中间隔别的步骤会把选区清掉 —— 这正是它「在诊断里成、在探针里不成」的原因）

⇒ ★★ 修法明确：★ **选区必须在调用前**那一下建好（★ 我们的 `pre_call` / 函数内自选**正好**满足这一点）✓

### 5.4 剩下 3 条 —— ★ 尚未查到条目级依据（★ 如实标注，★ 不猜）

★ `section_properties` · `dissolve_assembly` · `sketch_stretch` —— ★ 本轮 grep 未命中它们的条目段
（★ 可能记在别的 `capabilities[].id` 下）⇒ ★ **下一步先逐条把它们捞出来再定**（★ 不凭推断写结论）✓
★ 已知的仅有 `sketch_stretch` 一条：台账 `sketch_modify_ops` 逐字「官方说明是 'Stretch the **selected** entities'
⇒ **要求先选中实体**；本次真机测到的变化很小（±20 → -19.997/20.003），★ 与「没选中时只有极小效应」一致」✓

### 5.5 由此对执行顺序的修正

```
① 假阳性 2 条           ★ 已完成（本规格 T-216-05）
② insert_dome           ★ 可修 —— 走"两步式选面（先 mark=0 清选、再 mark=1）"+ 声明式选择器入参
③ insert_reference_point★ 可修 —— 选区必须**紧邻调用**
④ section_properties / dissolve_assembly / sketch_stretch
                        ★ 先逐条捞台账条目，再定（★ 不猜）
⑤ insert_composite_curve★ **不修** ⇒ 走"如实记为能力缺口"（★ 依据是 6 种选法全败 + 后端墙）
```
