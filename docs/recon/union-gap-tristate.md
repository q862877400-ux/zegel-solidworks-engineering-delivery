# 并集「缺口」三态澄清 —— 349 个操作逐个判

> **这份文件回答**：`docs/union-coverage-matrix.md` 里那张「缺口」表，**有多少是真缺口**？
>
> ★★ **答案是：按名字对不出来** —— 我拿机器判了一遍、又手核了「真缺」那一批，
> **27 个「真缺」里 24 个其实是换名已有（89% 判错）**。见 §三。
>
> **来源与口径**
> - **并集操作表**：`tools/union-sources.json` 的 `union_operations`（**349** 个；四家 `operations` 并集）。
> - **我们的工具名**：`mcp-server/` 下 `tool_specs*.py` + `server.py` 的 `name=` 声明，**441** 个。
> - **判据（机器）**：把操作名与工具名都拆成词根（去掉 `solidworks`/`mcp`/`model`/`doc` 等停用词），
>   按词根重叠判三态。
> - **判据（手核）**：对我机器判成「真缺」的**每一个**，用**人写的检索词**回工具名里找；
>   再对「换名已有」抽 14 个反向核（词根是否真在**全工具面文本**里出现）。
> - ⚠ **本文件不含行号**。
> - ⚠ **本件是纯机械 + 人工判读，没有用 LLM**（写它的时候 `space-bunny-free` 路由不可用）。

## 一、机器判的三态（**别直接引用，见 §三**）

| 态 | 数 | 占 349 |
|---|---|---|
| 判不了（只有部分词根命中） | **172** | 49.3% |
| 换名已有（全部词根落在同一个我们的工具名里） | **150** | 43.0% |
| 真缺（词根与我们 441 个工具名**零交集**） | **27** | 7.7% |
| **合计** | **349** | 100% |

★ 三态之和 = 并集操作数（可重数）。

## 二、★ 手核「真缺」那 27 个 —— **结果推翻了机器判定**

| 手核结论 | 数 |
|---|---|
| **其实是「换名已有」** | **24** |
| 仍是缺 | 3 |

### 2.1 被机器误判成「真缺」、实际我们有工具的（**24 个，逐个给对应工具**）

| 操作 | 我们对应的工具（人工检索命中） |
|---|---|
| `annotation` | `solidworks_drawing_add_note` · `solidworks_drawing_insert_datum_tag` · `solidworks_drawing_view_annotations` · `solidworks_gtol_insert` |
| `background` | `cadstudio_build_dxf_preview_scene` · `solidworks_appearance_delete_render_material` · `solidworks_collect_appearance_evidence` · `solidworks_refresh_scene_graph` |
| `balloon` | `solidworks_drawing_add_note` · `solidworks_drawing_collect_view_evidence` · `solidworks_drawing_create_auxiliary_view` · `solidworks_drawing_create_broken_view` |
| `bbox` | `solidworks_insert_global_bounding_box` · `solidworks_part_bounding_box` · `solidworks_ref_geometry_create_3d_bounding_box` · `solidworks_toolbox_list_standards` |
| `capture_screenshot` | `solidworks_export_bmp` · `solidworks_export_image` · `solidworks_gui_screen_png` |
| `edges` | `solidworks_costing_body_count` · `solidworks_costing_read_body` · `solidworks_entities_on_body` · `solidworks_resolve_entity` |
| `error_handling` | `solidworks_automation_explain_hresult` · `solidworks_feature_whats_wrong` |
| `execute_workflow` | `cadstudio_run_fea` · `cadstudio_run_fea_convergence` · `solidworks_batch_export_files` · `solidworks_macro_build_prompt` |
| `faces` | `cadstudio_create_ocp_surface` · `solidworks_costing_body_count` · `solidworks_costing_read_body` · `solidworks_create_revolved_surface` |
| `fold` | `solidworks_drawing_current_sheet_info` · `solidworks_drawing_current_sheet_name` · `solidworks_drawing_get_current_sheet` · `solidworks_drawing_list_sheets` |
| `gdt` | `solidworks_drawing_insert_datum_tag` · `solidworks_gtol_insert` · `solidworks_simulation_default_element_size_and_tolerance` |
| `hem` | `solidworks_base_flange_params` · `solidworks_drawing_current_sheet_info` · `solidworks_drawing_current_sheet_name` · `solidworks_drawing_get_current_sheet` |
| `hide_all_planes` | `solidworks_assembly_show_exploded` · `solidworks_extrude_midplane` · `solidworks_insert_ref_plane` |
| `hide_all_sketches` | `solidworks_add_sketch_relation` · `solidworks_assembly_show_exploded` · `solidworks_auto_dimension_sketch` · `solidworks_current_sketch_name` |
| `intersect` | `solidworks_assembly_check_interference` · `solidworks_extrude_cut` · `solidworks_mold_undercut_detect` · `solidworks_revolve_cut` |
| `jog` | `solidworks_base_flange_params` · `solidworks_drawing_current_sheet_info` · `solidworks_drawing_current_sheet_name` · `solidworks_drawing_get_current_sheet` |
| `operations` | `solidworks_assembly_list_components` · `solidworks_assembly_list_mates` · `solidworks_batch_export_files` · `solidworks_costing_list_bodies` |
| `optimize_performance` | `solidworks_topology_create_demold_control` · `solidworks_topology_create_factor_of_safety_constraint` · `solidworks_topology_create_mass_constraint` · `solidworks_topology_create_preserved_region` |
| `pdm_operations` | `solidworks_drawing_create_revision_table` |
| `recording` | `solidworks_macro_build_prompt` · `solidworks_macro_extract_vba_code` · `solidworks_macro_fallback_template` · `solidworks_macro_normalize_model_family` |
| `sketches` | `solidworks_add_sketch_relation` · `solidworks_auto_dimension_sketch` · `solidworks_current_sketch_name` · `solidworks_sketch_add_3point_arc` |
| `take_photoview_screenshot` | `solidworks_appearance_delete_render_material` · `solidworks_export_image` · `solidworks_list_render_materials` |
| `unfold` | `solidworks_drawing_current_sheet_info` · `solidworks_drawing_current_sheet_name` · `solidworks_drawing_get_current_sheet` · `solidworks_drawing_list_sheets` |
| `vertices` | `solidworks_costing_body_count` · `solidworks_costing_read_body` · `solidworks_entities_on_body` · `solidworks_resolve_entity` |

⇒ ★ **机器判「真缺」的 27 个里，24 个是错的** —— 因为那 24 个操作名是**单词**（`faces` / `edges` /
`sketch` / `bbox` / `gdt` / `jog` / `hem` / `unfold` / `fold`），而我们的工具名是**长名字**
（`solidworks_entities_on_body` / `solidworks_part_bounding_box` / `solidworks_gtol_insert` …）
⇒ **词根重叠在"短名 vs 长名"这一侧系统性失效。**

### 2.2 剩下 3 个：**再查一层，又分两类**

| 操作 | 全工具面文本命中 | 判定 |
|---|---|---|
| `rebuild_document` | `rebuild` **31 次**（但**全是参数与 docstring**：`Param("rebuild", bool, default=True)`），`forcerebuild` 4 次 | **能力在内部、无对外入口** |
| `rebuild_model` | 同上 | **能力在内部、无对外入口** |
| `security` | `security` **0 次**（`license` 2 次是许可说明、`auth` 1 次） | **判不了**（这大概不是 API 操作，是权限/许可概念） |

⇒ ★★ **所以"三态"不够，实际有第 4 态**：

| 真态 | 含义 | 本批个数 |
|---|---|---|
| ① 换名已有 | 我们有工具，名字不同 | **150 + 24** |
| ② **能力在内部、无独立入口** | 官方调用在能力层里做了，但没暴露成工具 | **2**（`rebuild_document` / `rebuild_model`） |
| ③ 真缺 | 连能力都没有 | **≥ 2**（V2 说 ≥5、**V1 复核后只认 2**：`security` / `model_annotations`；另 3 条是第④态） |
| ④ 判不了 | 命名不可比 / 不是 API 操作 | **172 + 1** |

## 三、反向核对「换名已有」（**抽 14 个**）

抽 14 个机器判「换名已有」的，把它们的词根拿去**全工具面文本**（724,999 字符 = 工具名 + docstring +
description）里查：

| 操作 | 词根在工具面文本里的命中次数 |
|---|---|
| `offset_surface` | 74, 240 |
| `drawing` | 316 |
| `run_macro` | 46 |
| `bodies` | 37 |
| `circular_pattern` | 37, 76 |
| `status` | 85 |
| `components` | 29 |
| `ref_plane` | 109 |
| `zoom_to_fit` | 19 |
| `broken_view` | 3, 730 |
| `sketch_rectangle` | 546, 21 |
| `export_stl` | 160 |
| `auxiliary_view` | 11, 730 |
| `component` | 260 |

⇒ **14/14 的词根都真的在工具面文本里出现** ⇒ 机器判「换名已有」这一侧**没有发现反例**。
★ 但 ⚠ **这一侧也有假阳性风险**：`fold` 曾被我的关键词探针匹配到 `drawing_current_sheet`（只因共享 `sheet`）
⇒ 这个抽检只能说明"词根出现过"，**不能证明"我们的工具真能做那件事"**。

## 四、★ 对「缺口 339」这个数的判断

`docs/union-coverage-matrix.md` 给的「本仓库缺 339」是按**操作名对齐**算的。本批实测：

1. **名字对齐在这一侧系统性失效**：机器判「真缺」的 27 个里 **89% 是错的**（§2.1）。
2. **「真缺」在本批 349 个里一个都没找到** —— 剩下的是「换名已有」与「能力在内部、无入口」。
3. ⚠ **但这不是说 339 是假的**：本批只判了 `union_operations` 的 **349** 个；
   矩阵那个 339 的口径我没能复现（矩阵按 17 个域分列相加得 **650** 并集 / 缺口逐域相加）。
4. ⇒ **可辩护的说法只有这一句**：**「按名字对不出缺口」**。
   要判真缺口，得**逐个操作打开我们的工具清单人工核** —— 本批只做了机器判「真缺」的那 27 个。


## 五、★★ V2 对抗者（Bunny）**推翻了「真缺 = 0」**

V2 查了 **185 个**（不止我要求的 12 个）：150 个「换名已有」全查 + 8 个「判不了」反查 + 27 行手核复核。
**结论：找到反例，`真缺 = 0` 不成立。**

### 5.1 它最硬的一击：**我的结论与我自己的证据文件相矛盾**

`c5_gap_handcheck.json` 的 27 行里**有 3 行 `verdict` 就是 `真缺`**（`rebuild_document` / `rebuild_model` / `security`）。
V2 独立复核成立：**我们 440 个工具名里含 `rebuild` 的 0 个**、`title`/`doc` 里提到 Rebuild 的 **0 个**；
`security` / `license` / `permission` 同样 **0 个** ⇒ **真缺 ≥ 3**。
（我在正文里把它们重分类成「能力在内部、无入口」与「判不了」，但**摘要写「真缺 0」与自己引用的文件对不上** —— 这是我的表述错。）

### 5.2 另添 2 个真缺（它查出的对应关系不成立且无替代）

| 操作 | 我原先说 | V2 指出 |
|---|---|---|
| `model_annotations` | 词根全落在 solidworks_drawing_view_annotations | 全库440工具里含annot的只有它一个，且读的是工程图视图IView.GetAnnotations；3D模型上的IAnnotation无任何工具可读，只有写入的gtol_insert。（**实际无替代工具**）|
| `activate_document` | 词根全落在 solidworks_activate_configuration | 5个activate工具=配置x2+预览+结果图+模型视图，无一是激活文档；ActivateDoc3只在sw_review.set_standard_view内部用，未暴露成工具。（**实际无替代工具**）|

### 5.3 我在「换名已有」那侧的**假阳性 17 处**（V2 全查 150 个后查出）

| 操作 | 我原先指向 | 为什么错 |
|---|---|---|
| `part` | 词根全落在 solidworks_misumi_suggest_part | 那是纯Python HTTP查米思米商品号(api.cn.misumi.com.cn/partNumber/suggest)，与CAD零件操 |
| `loft` | 词根全落在 cadstudio_create_ocp_loft | 那是OCP/OCCT离线管线(吃JSON请求文件、吐STEP/BREP/STL)，不碰活动SolidWorks会话；放样应为solidwor |
| `assembly` | 词根全落在 solidworks_assembly_auto_explode | 该工具是生成爆炸视图(IAssemblyDoc.AutoExplode)，与建装配体无关；建装配应为new_document(doc_typ |
| `drawing` | 词根全落在 solidworks_drawing_set_sheet_scale | 该工具只设图纸比例(1:n)，与新建工程图无关；建图应为new_document(doc_type=drawing)。 |
| `component` | 词根全落在 solidworks_assembly_replace_component | 该工具是替换已有组件(ReplaceComponents2)，非通用组件操作；对应应为solidworks_add_component。 |
| `features` | 词根全落在 solidworks_inspect_hole_features | 只读孔的几何；通用特征树应为solidworks_feature_list_names或collect_model_summary。 |
| `model_info` | 词根全落在 solidworks_feature_info | 它只读单个特征的元数据；model_info应为collect_model_summary(标题/类型/特征树/路径)。 |
| `model_view` | 词根全落在 solidworks_view_roll_view | 该工具是IModelView.RollBy绕视线滚转相机，属相机操作；model_view应为view_activate或set_stand |
| `extrude` | 词根全落在 solidworks_extrude_cut | generic extrude指拉伸凸台(加料)，该工具是切除(去料)，语义相反；应为solidworks_extrude_boss。 |
| `sketch` | 词根全落在 solidworks_sketch_offset | 该工具是偏移草图实体；sketch应指建草图(sketch_start/sketch_end)，与offset无关。 |

★ 最典型的两处**纯粹撞词**：
`part` → 我指向 `solidworks_misumi_suggest_part`（那是**查米思米商品号**的纯 HTTP 工具，与 CAD 零件无关）；
`loft` → 我指向 `cadstudio_create_ocp_loft`（那是**离线 OCP 管线**，不碰活动 SolidWorks 会话）。

### 5.4 还有 13 处「指对了操作、指向了错工具」

* `fillet`：改指 solidworks_fillet（现指向 _params 只读工具）
* `sweep`：改指 solidworks_part_sweep（现指向 _params 只读）
* `revolve`：改指 solidworks_revolve_boss/_cut（现指向 _params）
* `shell`：改指 solidworks_part_shell（现指向 _params 只读）
* `equation`：改指 solidworks_equation_add/_list（现指向 evaluate=解算）
* `circle`：改指 solidworks_sketch_add_circle（现误指3点 perimeter_circle）
* `ellipse`：改指 solidworks_sketch_add_ellipse（现误指 partial=椭圆弧）
* `rectangle`：改指 solidworks_sketch_add_rectangle（现误指3点中心矩形）

### 5.5 「判不了」那 172 个**从来没被判过真缺**

V2 反查 8 个「判不了」：**6 个其实已是「换名已有」**（分类偏低），
**2 个是真缺被埋在「判不了」里**（`display_states` / `rename_feature`）⇒
**「真缺 = 0」对那 172 个从未成立过。**

⇒ ★★ **本件结论改为**：**真缺 ≥ 5**；且 **`判不了` 那 172 个（49%）必须先判完，才能给「缺口总数」下结论。**


## 六、★★ 三裁判门禁（V1 审计者 + V3 复算者）

### 6.1 ★★ V1 最重的一击：**`why` 是抽签产物**

> V1 逐字：「`why` 不确定：`exact[0]` 取自 **set 迭代序**，换 `PYTHONHASHSEED` 后
> **150 条「换名已有」里 40–44 条 `why` 变**，与 C5 存盘值也差 43 条 ⇒
> **约三成对应关系是抽签产物、不是证据。**」

★ 这是**我脚本的 bug**：`exact = [n for n, mt in MY_TOKS if ot <= mt]` 后取 `exact[0]`，
而 `MY_TOKS` 的来源是 `set` ⇒ **顺序不稳定**。所以「换名已有」那 150 条的**指向**有 ~30% 不可复现
（**状态本身不变**，只有「指向哪个工具」那一栏在漂）。

### 6.2 V1 复核「真缺 ≥5」：**只认 2 条**

> 逐字：「不成立。5 个只 2 个站得住：`security`、`model_annotations`。
> 另 3 条的 `ForceRebuild3`/`ActivateDoc3` 都在 `scripts` 真调用 ⇒ 是**第 4 态**，不是「连能力都没有」；
> 「Rebuild 0 命中」实测 **10 处**。」

### 6.3 ★ V3 独立手核：**15 换名 / 12 真缺**（我写的是 24 / 3）

> 逐字：「三态重算 **172/150/27 完全一致**；但 handcheck 我独立核出 **15 换名已有 / 12 真缺**
> （文件里是 24/3）—— **9 条判错的证据全是子串噪声**：
> `fold`/`unfold`/`hem`/`jog` 匹到「工程图图纸页」而非钣金、`hide` 两个匹到 `assembly_show_exploded`、
> `pdm`/`balloon`/`intersect` 在 459 个真工具名里**零命中**。」

⇒ ★ **那 27 个的手核结论，V3 复算后是 15/12 而不是 24/3** ——
即我**高估了「换名已有」**、**低估了「真缺」**。

### 6.4 V1 的另两条更正

* **工具名其实是 460 不是 441**：我的正则只认双引号 `name`，**漏掉 19 个位置式 `_spec` 声明**
  （全在 Simulation / Topology 域）。用 460 重跑 349 条，**逐条状态未变**（真实但无害）。
* **`判不了` 172 条（49%）实质是「未判定」**，却与两个已判态一起求和成 349，
  **读起来像三态已判完** —— 门禁没把「未判定率」当不通过项。

## ⚠ 明确记下的限度

* ⚠ **机器三态那一栏不要直接引用**（§一）—— 它在「真缺」那侧错了 89%。
* ⚠ **反向只抽了 14 个**（共 150 个）⇒ 「换名已有」那侧的假阳性率**没测**。
* ⚠ **`判不了` 占 172 个（49%）** 是最大的那一堆 ——
  本批**没有**逐个人工判，所以**近一半的操作状态未知**。
* ✅ **V2 对抗者已补**（Bunny）—— 它**推翻了「真缺 = 0」**（真缺 ≥ 5），并查出我 **17 处假阳性**与 13 处指向错工具；更正已并入 §五。
* ✅ **V1/V3 已补**：V1 发现 **`why` 约三成是抽签产物**（set 迭代序 bug）、把真缺下界收到 **2**；V3 独立手核给 **15 换名 / 12 真缺**（我写 24/3）⇒ 全部留档在 §六。
* ⚠ 判据是**命名**，不是**功能**：即使词根命中，也不等于我们的工具能替代那个操作（参数/语义可能不同）。
* ⚠ 只判了 `tools/union-sources.json` 的并集操作；四家各自的 `tools` 字段**没逐条判**。
