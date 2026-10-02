# 「后缀候选」144 条的人工核样（2026-10-01 轮 101）

## 为什么要核
`docs/union-gap-triage.md` 把 **144 条**（占缺口 42%）归为
「**能力在、未暴露** —— `scripts/sw_*.py` 里有同名函数，只是没暴露成 MCP 工具」。
⚠ 该归类来自**字符串匹配**（后缀相同）。抽查一眼就觉得不对：
```
arc           -> sketch_arc          ✅ 同一操作
assembly      -> dissolve_assembly   ❌ 「分解装配体」不是「装配」
broken_view   -> call_view           ❌ 「断裂视图」不是「调用视图」
apply_template-> find_template       ❌ 「应用模板」不是「查找模板」
```
⇒ **人工核样，定出真实命中率。**

## 抽样规则（**可复算**）
对 `union-gap-triage.md` 的「后缀候选」表**每 6 条取 1**，得 **24** 条。

## 判定（三种：真 / 部分 / 假）

| # | 缺口操作 | 我们的候选 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | `3d_sketch` | `auto_dimension_sketch, end_sketch` | ❌ 假 | 3D 草图 ≠ 自动标注/结束草图 |
| 2 | `analyze_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 判断/校验 ≠ 分析 |
| 3 | `assembly_components` | `get_components` | ✅ 真 | 就是取装配体零件 |
| 4 | `bodies` | `get_bodies` | ✅ 真 | 同名 |
| 5 | `check_drawing_standards` | `get_hole_standards, list_standards` | ❌ 假 | 查标准 ≠ 检查图纸标准 |
| 6 | `close_model` | `_comtypes_active_model, _extract_comtypes_model` | ❌ 假 | **下划线内部函数**，且是取模型不是关模型 |
| 7 | `convert_text_to_native_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 转换 ≠ 判断 |
| 8 | `detail_view` | `activate_view, call_view` | ❌ 假 | 详图视图 ≠ 激活视图 |
| 9 | `drawing_sheet_size` | `_read_bmp_size, set_default_lot_size` | ❌ 假 | **内部函数** + 装箱尺寸 |
| 10 | `execute_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 执行 ≠ 校验 |
| 11 | `export_iges` | `export_to_iges` | ✅ 真 | 同一操作 |
| 12 | `extract_template` | `find_template, get_default_template` | ❌ 假 | 提取 ≠ 查找 |
| 13 | `flat_pattern_info` | `_file_info` | ❌ 假 | 钣金展开 ≠ 文件信息 |
| 14 | `hole_table` | `get_fastener_table` | ❌ 假 | 孔表 ≠ 紧固件表 |
| 15 | `manage_file_properties` | `apply_visual_properties, set_custom_properties` | ⚠ 部分 | `set_custom_properties` 是其中一种 |
| 16 | `model_view` | `activate_view, call_view` | ❌ 假 | 模型视图 ≠ 激活视图 |
| 17 | `point` | `click_point, first_result_point` | ❌ 假 | 草图点 ≠ 点击坐标 |
| 18 | `relation` | `add_sketch_relation` | ✅ 真 | 加草图关系 = relation 操作 |
| 19 | `run_vba_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 运行 ≠ 校验 |
| 20 | `scale_body` | `create_deformed_body, entities_on_body` | ❌ 假 | 缩放 ≠ 变形 |
| 21 | `sketch` | `auto_dimension_sketch, end_sketch` | ❌ 假 | 草图 ≠ 自动标注 |
| 22 | `sketch_polygon` | `sketch_polygon` | ✅ 真 | **完全同名** |
| 23 | `slot` | `create_semicircular_slot, sketch_slot` | ✅ 真 | 同一操作 |
| 24 | `template_custom_properties` | `apply_visual_properties, set_custom_properties` | ⚠ 部分 | 同上 |

## 结果
```
24 条抽样：✅ 真 **6** · ⚠ 部分 **2** · ❌ 假 **16**
⇒ 真实命中率 ≈ 6/24 = **25%**（⚠ 24 个样本，95% 区间约 12%~43%）
```

## ★★ 结论：**「144 = 能力在、未暴露」这个说法高估了**
```
原分档：能力在未暴露 144（42%） · 真缺 132（39%）
按 25% 命中率折算：
   真匹配 ≈ 144 × 25% ≈ **36**   ⇒ 仍在「已实现但没暴露」
   假匹配 ≈ **108**              ⇒ 应当归进「真缺」
⇒ 真缺 ≈ 132 + 108 ≈ **240**（不是 132）
```

## ★ 为什么匹配器会错这么多
它按**后缀词**匹配（`sketch` / `view` / `template` / `macro`），
而这些词在 SolidWorks 里是**高频通用词** ⇒ 一个 `*_view` 就能配上几十个操作。
⚠ **这与已知事实 52（名字是弱信号）同源**，且与事实 53（启发式连续修补就该停）相邻：
**这一档不该由字符串匹配给出结论，只能人工核。**

## ⚠ 未查证
* 只核了 **24/144**（抽样），**剩余 120 条未逐条核**；
* ⚠ **本轮（轮 102）追加**：另两档「别名强/弱」**已全核**，见文末 —— **四档全都要打折，真实缺口约 270~290**；
* 「部分」那 2 条算不算命中，**口径未定**（本表按不计入"真"处理）。

---

# 追加：两档「别名」也核了（轮 102）

`010` 另有两档别名，**同样是字符串匹配**，且「强别名」档自称「**极可能同一操作**」。
⇒ 本轮**全核**（只有 63 条）：

## 别名（强）26 条 —— 命中率 ≈ **27%**

| # | 缺口操作 | 我们的候选 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | `advanced_features` | `inspect_hole_features` | ❌ 假 | 高级特征 ≠ 检查孔特征 |
| 2 | `assembly_analysis` | `mold_draft_analysis` | ❌ 假 | 装配分析 ≠ 模具拔模分析 |
| 3 | `assembly_configurations` | `inspect_configurations` | ✅ 真 | 就是看配置 |
| 4 | `configurations` | `inspect_configurations` | ✅ 真 | 同上 |
| 5 | `delete_feature` | `hole_feature` | ❌ 假 | **删除**特征 ≠ 孔特征 |
| 6 | `drawing` | `inspect_drawing` | ✅ 真 | 同一操作 |
| 7 | `extend_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 延伸曲面 ≠ 关曲面/OCP 曲面 |
| 8 | `extruded_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 拉伸曲面 |
| 9 | `features` | `inspect_hole_features` | ❌ 假 | 特征 ≠ 孔特征 |
| 10 | `filled_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 填充曲面 |
| 11 | `line` | `mold_parting_line` | ❌ 假 | 草图直线 ≠ 分型线 |
| 12 | `loft` | `ocp_loft` | ✅ 真 | 放样 |
| 13 | `mirror_feature` | `hole_feature` | ❌ 假 | 镜像 ≠ 孔 |
| 14 | `offset_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 偏移曲面 |
| 15 | `parting_line` | `mold_parting_line` | ✅ 真 | 分型线 |
| 16 | `pattern_features` | `inspect_hole_features` | ❌ 假 | 阵列 ≠ 孔 |
| 17 | `planar_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 平面曲面 |
| 18 | `rename_feature` | `hole_feature` | ❌ 假 | 重命名 ≠ 孔 |
| 19 | `revolved_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 旋转曲面 |
| 20 | `shut_off_surface` | `mold_shut_off_surface` | ✅ 真 | 关曲面 |
| 21 | `sketch_line` | `mold_parting_line` | ❌ 假 | 草图线 ≠ 分型线 |
| 22 | `split_line` | `mold_parting_line` | ❌ 假 | 分割线 ≠ 分型线 |
| 23 | `technical_drawing` | `inspect_drawing` | ✅ 真 | 工程图 |
| 24 | `thicken_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 加厚曲面 |
| 25 | `trim_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 裁剪曲面 |
| 26 | `unsuppress_feature` | `hole_feature` | ❌ 假 | 解除压缩 ≠ 孔 |

```
✅ 真 **7** / 26 ≈ **27%**
```
★ **最离谱的一处**：第 7/8/10/14/17/19/24/25 条 —— **8 个互不相同的曲面操作**
（延伸 / 拉伸 / 填充 / 偏移 / 平面 / 旋转 / 加厚 / 裁剪）**全被配到同样两个函数**
`mold_shut_off_surface, ocp_surface`。⇒ 匹配器只认到共同后缀 **`surface`**。

## 别名（弱）37 条 —— 命中率 ≈ **16%**

判定口径同上（✅ 真 / ⚠ 部分 / ❌ 假）。逐条：

| 缺口操作 | 我们的候选 | 判定 |
|---|---|---|
| `activate_document` | `new_document, open_document` | ⚠ 部分 |
| `analyze_draft` | `sheet_metal_create_draft` | ❌ 假（**分析**拔模 ≠ **建**拔模）|
| `analyze_geometry` | `review_advanced_geometry` | ⚠ 部分 |
| `base_flange` | `sheet_metal_create_base_flange` | ✅ 真 |
| `batch_process_files` | `batch_export_files` | ⚠ 部分 |
| `bom` | `export_assembly_bom` | ✅ 真 |
| `check_geometry` | `review_advanced_geometry` | ⚠ 部分 |
| `close_document` | `new_document, open_document` | ❌ 假 |
| `construction_geometry` | `review_advanced_geometry` | ❌ 假 |
| `convert_file_format` | `write_open_format` | ⚠ 部分 |
| `diameter_dimension` | `update_dimension` | ⚠ 部分 |
| `dimension` | `update_dimension` | ✅ 真 |
| `draft` | `sheet_metal_create_draft` | ⚠ 部分 |
| `drawing_dimension` | `update_dimension` | ⚠ 部分 |
| `drawing_sheet_format` | `write_open_format` | ❌ 假 |
| `edge_flange` | `sheet_metal_create_edge_flange` | ✅ 真 |
| `export_document` | `new_document, open_document` | ❌ 假 |
| `gusset` | `sheet_metal_create_gusset` | ✅ 真 |
| `load_part` | `basic_part` | ❌ 假 |
| `mate` | `coincident_mate, concentric_mate` | ⚠ 部分 |
| `material` | `simulation_set_material` | ⚠ 部分 |
| `miter_flange` | `sheet_metal_create_*_flange` | ❌ 假 |
| `motion_study` | `validate_motion_study` | ⚠ 部分 |
| `open_documents` | `close_documents` | ❌ 假 |
| `part` | `basic_part` | ⚠ 部分 |
| `rebuild_document` | `new_document, open_document` | ❌ 假 |
| `reference_geometry` | `review_advanced_geometry` | ❌ 假 |
| `referenced_documents` | `close_documents` | ❌ 假 |
| `save_active_document` | `new_document, open_document` | ❌ 假 |
| `save_body_as_part` | `basic_part` | ❌ 假 |
| `save_part` | `basic_part` | ❌ 假 |
| `simulation_study` | `topology_create_study, validate_motion_study` | ⚠ 部分 |
| `sketch_dimension` | `update_dimension` | ⚠ 部分 |
| `sketch_status` | `addin_host_status` | ❌ 假（只配到 `status` 一词）|
| `sketched_bend` | `sheet_metal_create_one_bend` | ✅ 真 |
| `status` | `addin_host_status` | ❌ 假 |
| `update_sheet_format` | `write_open_format` | ❌ 假 |

```
✅ 真 **6** · ⚠ 部分 **14** · ❌ 假 **17** / 37 ⇒ 真 **16%**
```

## ★★ 合并后的结论：**四档全都要打折**
```
              条数   真    命中率
别名（强）      26     7     27%
别名（弱）      37     6     16%
后缀候选       144    36*    25%   (* 抽样外推)
真缺           132   132     —     (定义上就是缺)
------------------------------------------------
真匹配 ≈ 7 + 6 + 36 = **49**
⇒ 真实缺口 ≈ 338 − 49 ≈ **289**（`010` 当时说 **132**）
```

## ⚠ 这个数字的限度（必须一起读）
* **别名两档是全核**（63/63）；**后缀候选是抽样**（24/144）⇒ 后者有外推误差；
* 「部分」那 **16** 条口径未定；本表**不计入"真"** ⇒ 真匹配可能落在 **49~65** 之间；
* 因此结论应表述为「**真实缺口约 270~290，远大于 010 说的 132**」，
  而不是「就是 289」。

## ★ 这一轮的可复用认识
**同一个匹配器，越"强"的档也可能越不准** —— 「强别名」自称"极可能同一操作"，
实测 **27%**，与最弱的档**差不多**。
⇒ **分档的"强/弱"是给匹配规则起的名，不是给结论背的书。**

---

# 追加：132 条「真缺」的反向核样（轮 103）

## 为什么要核这一档
前三轮都在核「**别名 / 后缀候选**」三档（它们会把"其实没有"记成"有"）。
「真缺」132 条**方向相反**：它是"**连 `scripts/` 里也没有同名函数**"⇒
⚠ 可能把"**其实我们以别的名字实现了**"记成缺。轮 98 就撞到一例：
`tooling_split` 在真缺里，而我们**早有** `sw_mold.insert_core_cavity_solids`。

⇒ 核样：**每 6 取 1**（与轮 101 同规则）⇒ **22 条**。

## ⚠⚠ 我的自动检查这一轮**连续错三次**（必须记下来）
| 次 | 我写的判据 | 错在哪 |
|---|---|---|
| 1 | 在 `scripts/sw_*.py` 里找关键词 | 命中的是 `sw_api_sldworks.py` —— **API 名登记表，不是实现** |
| 2 | 再排除 `sw_api_*` | `save_as` 命中的是 `sw_com_traps.py` —— **COM 陷阱表**；`gdt` 命中的是 `sw_api_swdimxpert.py` |
| 3 | 再排除 `sw_com_traps` | `equation` 命中的是**参数名**；`export_vba` 命中的是 `sw_automation_knowledge`（**知识表**）|

★ **⇒ 结论：按名字做的自动检查在这个问题上「两个方向都不可靠」**：
* 前三轮：把**没有**的记成**有**（假阳性）；
* 这一轮：把**有**的（换名实现）记成**没有**，同时又把**参数名/知识表**当成实现（**又是假阳性**）。

⇒ **⇒ 唯一站得住的做法是逐条人工判**（下面就是）。

## 22 条逐条判定

| # | 缺口操作 | 我们其实有吗 | 判定 | 说明 |
|---|---|---|---|---|
| 1 | `activate_sheet` | 无 | ❌ 没有 | 只有 `activate_configuration` / `_activate_model_document` |
| 2 | `assembly_mates` | `collect_mate_feature_summary` | ⚠ 部分 | 有**配合摘要**，不是"列配合" |
| 3 | `batch_operations` | `batch_export` | ⚠ 部分 | 只有**批量导出**，不是通用批量操作 |
| 4 | `check_drawing_compliance` | 无 | ❌ 没有 | |
| 5 | `convert_entities` | 无（`SketchUseEdge` 只登记未实现）| ❌ 没有 | |
| 6 | `drawing_dimensions` | 无 | ❌ 没有 | `review_drawing_layout` 是复核布局，不是尺寸 |
| 7 | `equation` | 无（命中的是**参数名**）| ❌ 没有 | ⚠ 自动检查在这里**假阳性** |
| 8 | `export_vba` | 无（命中的是**知识表**）| ❌ 没有 | ⚠ 同上 |
| 9 | `gdt` | 无 | ❌ 没有 | 形位公差 |
| 10 | `generate_vba_file_operations` | 无 | ❌ 没有 | |
| 11 | `helix` | 无 | ❌ 没有 | 螺旋线 |
| 12 | `jog` | 无 | ❌ 没有 | 折弯 |
| 13 | `measure` | **`collect_geometry_measurements`** | ✅ **有** | 几何测量收集 |
| 14 | `pattern_component_circular` | **`circular_pattern`（`sw_part`）** | ✅ **有** | ⚠ 但那是**特征**圆周阵列，不是**零部件**阵列 —— **口径存疑** |
| 15 | `recording` | 无 | ❌ 没有 | 宏录制 |
| 16 | `save_as` | **`SaveAs`（`sw_connect` / `sw_export`）** | ✅ **有** | 另存为 |
| 17 | `sheets` | `sheet_names`（`sw_export`）| ⚠ 部分 | 只是导出用的辅助，不是"图纸"操作 |
| 18 | `sketch_chamfer` | 无 | ❌ 没有 | 草图倒角 |
| 19 | `sketch_mirror` | 无 | ❌ 没有 | 草图镜像 |
| 20 | `stop_native_macro_recording` | 无 | ❌ 没有 | |
| 21 | `tooling_split` | **`insert_core_cavity_solids`** | ✅ **有** | **轮 98 已确认**（能力在、未暴露）|
| 22 | `validate_drawing_completeness` | 无 | ❌ 没有 | |

```
✅ 确实有 **4**  ·  ⚠ 部分 **2**  ·  ❌ 没有 **16**
⇒ 反向错误率 ≈ 4/22 ≈ **18%**（含"部分"则 27%）
```

## ★★ 四轮合并后的估算
```
              条数   真    来源
别名（强）      26     7    轮 102 全核
别名（弱）      37     6    轮 102 全核
后缀候选       144    36    轮 101 抽样外推
真缺           132    24    轮 103 抽样（132 × 18%）
----------------------------------------
真匹配 ≈ 73   ⇒   真实缺口 ≈ 338 − 73 ≈ **265**
```

## ⚠ 这个数字的限度（比前几轮更多）
* **后缀候选**（144）与**真缺**（132）都是**抽样外推**（24/144 · 22/132）；
* 「部分」共 **18** 条口径未定 ⇒ 真匹配区间约 **73~95** ⇒ **真实缺口约 245~265**；
* `pattern_component_circular` 那条**口径存疑**（特征阵列 ≠ 零部件阵列）——
  按严格口径它不算"有"，那真匹配降到 72、缺口升到 266。

## ★ 本轮的**方法**收获（比数字重要）
> **按名字做的自动检查，在这个问题上两个方向都靠不住。**

它既会把"没有"记成"有"（前三轮），也会把"有"记成"没有"，
**还会把参数名和知识表当成实现**。
⇒ **四轮下来唯一站得住的动作都是同一件：把每条拿出来人工看一眼。**
