# 工具别名表（★ 由 C5 手核数据机械筛 + 增益实测 + **语义闸**得出）

> **生成物** —— 由 `tools/t1_tally_alias_gate.py` 产出，**不要手改**。
> 输入：`specs/204-bunny-moat-batches/recon/c5-gap-handcheck.json`（另一个对话的 C5 手核，只读复用）+ 本仓 `all_specs()` + 3 路独立裁判的语义判定。

## 一 · ★★ 头号结论：**C5 的「换名已有」经语义闸后大幅缩水**

| 阶段 | 数 | 说明 |
|---|---|---|
| C5 手核判「换名已有」 | **24** 行 | 另一个对话的人工判读（`conditional_pass`）|
| 其 `hits` 展开成候选对 | 97 对 | ★ `hits` 是**子串匹配**的产物 |
| 机械筛后（词必须出现在 name/title）| **79 对 / 52 工具** | ★ 丢掉 18 对子串疑云 |
| 增益实测（别名当查询）| 45/52 **提升** | ★★ 但**近似同义反复**（查询词就是别名本身）|
| ★★★ **语义闸（3 路裁判）** | ★ **same 仅 9** · related 28 · **wrong 15** | ★★ 83% 不是同一件事 |

★★ **所以：`hits` 里「子串命中」与「真是别名」是两回事，而增益实测分不开它们** ——
★ 只有**语义闸**能分开。本表最终只采纳 **9** 条。

## 二 · ★ 采纳（**9** 条 · 裁判判 `same`）

| 工具 | 别名 | 排名 现状→加别名 | 增益 |
|---|---|---|---:|
| `solidworks_assembly_list_components` | batch, list, operation, operations | 15 → **1** | +14 |
| `solidworks_drawing_insert_datum_tag` | annotation, balloon, datum, gdt, gtol, note, tolerance | 4 → **1** | +3 |
| `solidworks_collect_appearance_evidence` | appearance, background, scene | 2 → **1** | +1 |
| `solidworks_drawing_create_revision_table` | pdm, pdm_operations, revision, vault | 2 → **1** | +1 |
| `solidworks_entities_on_body` | body, edge, edges, entit, vertex, vertices | 2 → **1** | +1 |
| `solidworks_part_bounding_box` | bbox, bounding, box | 2 → **1** | +1 |
| `solidworks_assembly_check_interference` | combine, cut, interference, intersect | 1 → **1** | +0 |
| `solidworks_automation_explain_hresult` | error, error_handling, explain, hresult, whats_wrong | 1 → **1** | +0 |
| `solidworks_gtol_insert` | annotation, balloon, datum, gdt, gtol, note, tolerance | 1 → **1** | +0 |
| `solidworks_insert_global_bounding_box` | bbox, bounding, box | 1 → **1** | +0 |

## 三 · ★ 待复核（**21** 条 · 判 `related`）—— **不接进 doc**

★ 判据：「同域但不是同一件事」⇒ 接进去会把不该命中的工具抬上来。
- `solidworks_appearance_delete_render_material` ← appearance, background, export_image, photoview, render, scene, screenshot, take_photoview_screenshot
- `solidworks_assembly_list_mates` ← batch, list, operation, operations
- `solidworks_auto_dimension_sketch` ← hide, hide_all_sketches, show, sketch, sketches, visibility
- `solidworks_base_flange_params` ← bend, flange, hem, jog, sheet
- `solidworks_drawing_add_note` ← annotation, balloon, datum, drawing, gtol, note
- `solidworks_drawing_create_detail_view` ← balloon, drawing, note
- `solidworks_extrude_cut` ← combine, cut, interference, intersect
- `solidworks_extrude_midplane` ← hide, hide_all_planes, plane, show, visibility
- `solidworks_gui_screen_png` ← capture_screenshot, export_bmp, export_image, screen, screenshot
- `solidworks_list_render_materials` ← export_image, photoview, render, screenshot, take_photoview_screenshot
- `solidworks_macro_build_prompt` ← batch, execute_workflow, macro, record, recording, run, workflow
- `solidworks_macro_extract_vba_code` ← batch, execute_workflow, macro, record, recording, run, workflow
- `solidworks_macro_fallback_template` ← macro, record, recording
- `solidworks_macro_run` ← macro, record, recording
- `solidworks_ref_geometry_create_3d_bounding_box` ← bbox, bounding, box
- `solidworks_refresh_scene_graph` ← appearance, background, scene
- `solidworks_surface_cut` ← combine, cut, interference, intersect
- `solidworks_topology_create_factor_of_safety_constraint` ← optimize, optimize_performance, performance, topology
- `solidworks_topology_create_mass_constraint` ← optimize, optimize_performance, performance, topology
- `solidworks_topology_create_preserved_region` ← optimize, optimize_performance, performance, topology
- `solidworks_topology_create_stress_constraint` ← optimize, optimize_performance, performance, topology

## 四 · ★★ 弃用（**21** 条 · 判 `wrong`）—— 附裁判点名的泛词

★★ 这些是**子串/泛词命中**的证据：别名里只有 `drawing` / `sketch` / `box` / `macro` 这类
**在很多工具里都出现**的词，于是与工具匹配上了，但那个词**并不指向这个工具的功能**。

| 工具 | 别名 | 裁判点名的泛词 |
|---|---|---|
| `solidworks_add_sketch_relation` | hide, hide_all_sketches, show, sketch, sketches, visibility | sketch, sketches, hide, show, visibility, hide_all_sketches |
| `solidworks_assembly_show_exploded` | hide, hide_all_planes, hide_all_sketches, plane, show, sketch, visibility | show, hide, plane, sketch, visibility |
| `solidworks_costing_body_count` | body, edge, edges, entit, face, faces, vertex, vertices | body, edge, edges, face, faces, vertex, vertices |
| `solidworks_costing_list_bodies` | batch, list, operation, operations | list, batch, operation, operations |
| `solidworks_costing_list_templates` | batch, list, operation, operations | list, batch, operation, operations |
| `solidworks_costing_read_body` | body, edge, edges, entit, face, faces, vertex, vertices | body, edge, edges, face, faces, vertex, vertices |
| `solidworks_current_sketch_name` | hide, hide_all_sketches, show, sketch, sketches, visibility | sketch, sketches, hide, show, visibility |
| `solidworks_drawing_collect_view_evidence` | balloon, drawing, note | drawing, note, balloon |
| `solidworks_drawing_create_auxiliary_view` | balloon, drawing, note | drawing, note, balloon |
| `solidworks_drawing_create_broken_view` | balloon, drawing, note | drawing, note, balloon |
| `solidworks_drawing_current_sheet_info` | bend, flange, flatten, fold, hem, jog, sheet, unfold | sheet |
| `solidworks_drawing_current_sheet_name` | bend, flange, flatten, fold, hem, jog, sheet, unfold | sheet |
| `solidworks_drawing_get_current_sheet` | bend, flange, flatten, fold, hem, jog, sheet, unfold | sheet |
| `solidworks_drawing_set_sheet_format` | flatten, fold, sheet, unfold | sheet |
| `solidworks_insert_ref_plane` | hide, hide_all_planes, plane, show, visibility | plane |
| `solidworks_macro_normalize_model_family` | macro, record, recording | macro |
| `solidworks_revolve_cut` | combine, cut, interference, intersect | cut |
| `solidworks_simulation_default_element_size_and_tolerance` | datum, gdt, gtol, tolerance | tolerance, datum, gtol |
| `solidworks_sketch_add_3point_arc` | hide, hide_all_sketches, show, sketch, sketches, visibility | sketch, sketches, show, hide, visibility |
| `solidworks_sketch_add_3point_center_rectangle` | sketch, sketches | sketch, sketches |
| `solidworks_topology_create_demold_control` | optimize, optimize_performance, performance, topology | optimize, performance, topology |

## 五 · 口径（★ 与数字一起读）

- ★ **采纳面只到 9 条**，因为语义闸逐条判 —— 不是「45 条都有效」；
- ★ **误报率自查**：`wrong 15 / 52 = 28.8%` ⇒ ★★ **远超我自定的 D-1 阈值（≤5%）**
  ⇒ **本批候选不得直接进门禁/进 doc**，只把 `same` 的 9 条作为**候选队列**，
  ★ 且需**再上真实语料复测**（当前无中文语料）；
- ★ **每条只被 1 路裁判判过**（3 路各判 1/3）⇒ 未做多数票 ⇒ 记 `conditional_pass`；
- ★★ **不构成**任何「中文用户会怎么说」的证据（别名全是英文词）。

## 六 · ★★ T1-5 / T1-6 收口：**实测把采纳面从 10 缩到 5**（2026-10-04）

### 6.1 两面都测（★ 避免只报有利的一面）

| 面 | 测什么 | 现状（剥掉别名）| 装上别名后 | 差 |
|---|---|---|---|---|
| **A** | 48 题的**中文**查询 | top-1 19% · top-5 25% | top-1 19% · top-5 25% | ★★ **精确的 0** |
| **B** | 别名**自己的词**当查询 | top-1 7 · top-5 37% | top-1 10 · top-5 38% | ★ 几乎不动 |

★★ **面 A 是 0 的原因**：别名是**英文**，中文查询与它**词元不重叠** ⇒ ★ **英文别名对中文用户无效** ✓

### 6.2 ★★★ 但平均值**掩盖了**真实效果（本轮第三个方法论发现）

逐工具量（十个别名同时装）却是：**提升 5 · 不变 5 · 变差 0** ——
★ 因为不变的那 5 个里有 **4 个本来就是 rank 1**（**没有上升空间**）✓
⇒ ★★ **平均值既不能证明有效、也不能证明无效** —— 必须看**逐项** ✓

### 6.3 ★ 按 D-2 判据收口（别名必须挣到字节）

| 工具 | 联合下的排名 | 处置 |
|---|---|---|
| `solidworks_assembly_list_components` | **15 → 1** | ★ **留下** |
| `solidworks_drawing_insert_datum_tag` | **4 → 2** | ★ **留下** |
| `solidworks_collect_appearance_evidence` | **2 → 1** | ★ **留下** |
| `solidworks_drawing_create_revision_table` | **2 → 1** | ★ **留下** |
| `solidworks_entities_on_body` | **2 → 1** | ★ **留下** |
| `solidworks_assembly_check_interference` | 1 → 1 | ✗ **已回退**（挣不到字节）|
| `solidworks_automation_explain_hresult` | 1 → 1 | ✗ **已回退**（挣不到字节）|
| `solidworks_gtol_insert` | 1 → 1 | ✗ **已回退**（挣不到字节）|
| `solidworks_insert_global_bounding_box` | 1 → 1 | ✗ **已回退**（挣不到字节）|
| `solidworks_part_bounding_box` | 2 → 2 | ✗ **已回退**（挣不到字节）|

⇒ ★★ **最终只保留 5 条别名行**（`doc` 里追加一行，不动 schema 契约；已实测工具总数仍 **433**）✓

### 6.4 ★★★ 三条方法论教训（★ 比这 5 条别名值钱）

1. ★★ **「增益实测」分不开对错** —— 查询词就是被追加的别名本身 ⇒ 语义上错的别名一样会提升（★ 要与语义闸配合，见 §二/§四）；
2. ★★ **「逐条增益」推不出「整体增益」** —— 孤立测时 45/52 提升、最大 56→1；十个一起装后平均几乎不动（★ 同族缺陷：**局部外推到整体**）；
3. ★★ **平均值会掩盖天花板** —— 『平均只涨 1 个点』说的是那 5 个**已经在 rank 1** 的工具，不是那 5 个真提升的工具 ✓
