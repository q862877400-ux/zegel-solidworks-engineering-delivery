# 直线模组 · 单任务测试流程设计（v3）

> **生成**：诊断分支，2026-10-01 · **v3 按业主「标准件是嘉立创 FA 插件 + Computer Use」这一条重写**
> **依据**：`capabilities.yaml` · `scripts/sw_jlcfa_*.py`（13 个模块）· `scripts/jlcfa_index.json`（15 MB 实测）·
> `tools/verify_in_context_reference_smoke.py`（轮 161 约定）· `docs/known-facts.md`
> **⚠ 只做设计，没改任何仓库文件、没连 SolidWorks。** 落点 `D:\AI\SW-transfer\`（两个仓库之外）。

---

## 〇、v2 → v3 的**关键更正**（我上一版错了）

**v2 说「本机没有丝杆/导轨/铝型材、真件拿不到」—— 错。**

真实情况：**标准件走的是嘉立创 FA 选型插件 + Computer Use**，已经能稳定插入。

**索引实测（`scripts/jlcfa_index.json`，15 MB）：**

| 项 | 数 |
|---|---|
| `codes` | **63,234** |
| `categories` | **200** |
| `parameters` | 330,208 |
| `parameter_values` | 447,527 |
| `builder_models` | **14,583** |
| ⚠ `codes_with_model` | **0**（模型挂在 `builder_models` 上，不是按 code） |

来源说明（索引自己的 `note`，**干净**）：
> 自嘉立创 FA 选型插件的运行时**明文 SQLite** 抽取（全库，非限品类）；
> **未解密 DB.zip、未逆向 DLL、未修改任何厂商文件。**

**品类里本场景要的全在：**
```
滚珠丝杠 · 滚珠丝杠支座组件（= 法兰式丝杆固定座）· 直线导轨 · 铝型材 ·
工业铝型材及配件 · 铝型材框架 · KK模组/单轴驱动器 · 导轨内嵌式直线模组 ·
铝基座直线模组 · 交叉滚子导轨/滑台 · 联轴器/万向节 · 伺服电机 · 步进电机 · 型材配件
```

---

## 一、⚠ 顺手查出的一处**体系缺口**

```
capabilities.yaml 含 'jlcfa' / '嘉立创' / 'standard_parts' / 'toolbox'  →  **全部 0 次命中**
tests/ 与 tools/ 里含 'jlcfa' 的文件                                  →  **0 个**
```
⇒ **一条 13 模块 + 15 MB 索引 + 6.3 万型号、且能稳定跑通的链，既无能力条目、又无任何测试。**

**13 个模块：**
```
sw_jlcfa_index   索引检索（load_index / summarize / list_categories / search）
sw_jlcfa_search  搜索（search_box / search_button / search / result_cards / first_result_point）
sw_jlcfa_cards   结果卡（code_labels / visible_codes / locate_code / scroll_card_into_view / category_cards）
sw_jlcfa_grid    网格（card_rows / named_cards_in_order / locate_card）
sw_jlcfa_select  选择与填充（pick_first / select_index / pending_edits / fill_edit / fill_to_100 / scroll）
sw_jlcfa_fill    参数填充（find_edit_by_label / type_into / fill_all / pending_params / first_missing_label）
sw_jlcfa_click   点击（click_control / click_point / click_rect / verify_click_landed / client_to_screen）
sw_jlcfa_gui     GUI 基元（sw_window / ensure_window / click / drag / wheel / find_node / snap）
sw_jlcfa_locate  定位（locate / locate_all / rect_of / focus_solidworks / capture_front）
sw_jlcfa_steps  ★ 带自检的分步执行器（read_state / page_kind / run_step / resume / act_with_focus）
sw_jlcfa_batch  批量抽查（run_one）
sw_jlcfa_audit  抽查审计（goto / goto_element / run_one）
```

**它自己记下的真机事实（值得进 `known-facts.md`）：**
```
· 分类导航是**死路**：UIA 报**虚拟坐标**（容器 rect 是视口坐标，但 125 张卡片 y=2509…8975 远超容器）
  ⇒ 卡片 rect **不能点** ⇒ 必须走**搜索**
· 数字会被逐键输入吃掉（EGH25SAZ0C → EGHSAZC）⇒ **必须剪贴板粘贴**
· Enter 不触发搜索 ⇒ 要点「搜索」按钮
· 完整链：结果页 → 选型页 → 100% → 「生成预览」→「建模完成！」
· 页面类型判定（首页/分类页/结果页/选型页）各有可读判据
· `SetCursorPos` 会**抢用户鼠标** ⇒ 动作之间必须让回
· Windows 只把键鼠事件投给**前台窗口** ⇒ 每个动作前必须确认前台是 SolidWorks
```

---

## 二、任务表（v3）

| # | 任务（做什么） | 测什么（模块 · **真实函数** · 判据） |
|---|---|---|
| **T1** | **选型检索**：按品类找件 | `sw_jlcfa_index` · `load_index` `list_categories` `summarize` `search`<br>**判据**：查到 `滚珠丝杠支座组件` / `直线导轨` / `铝型材` **各自 ≥1 条**，且条目 **`has_3d == 1`** |
| **T2** | ★ **用插件插入标准件**（Computer Use 全链） | `sw_jlcfa_steps`（`read_state` → `page_kind` → `run_step` → `resume`）<br>+ `sw_jlcfa_search` → `sw_jlcfa_cards` → `sw_jlcfa_select` → `sw_jlcfa_fill` → `sw_jlcfa_click`<br>**判据**：★ **`page_kind` 逐级推进到「选型页」→ 100% → 「建模完成！」**，且**每步有超时、失败留截图 + 状态 JSON**<br>⚠ **GUI 链：必须先确认前台是 SolidWorks**（否则跳过并留证，**绝不静默发按键**）|
| **T3** | **读回插入件的配置与尺寸** | 配置读取 · `sw_document_data.inspect_configurations` · `sw_part.get_bounding_box`<br>**判据**：**打印配置名与实测长度**（取证；业主说「选定尺寸就固定」，**本机未验**）|
| **T4** | ★★ **改造标准件**：把它的尺寸接到**全局变量 / 方程** | `sw_equation.add_equation` `evaluate_equations` · `sw_document_data.update_dimension_mm`<br>⚠ 插件生成的件可能需要**另存**（`sw_connect.save_document` 到 output）<br>**判据**：**改全局变量 ⇒ 该标准件长度实测值变化**（★ 空操作不变）<br>★ **业主点名的场景，全表最值钱的一环** |
| **T5** | 造**端板**（真非标）+ 螺丝孔 | `sw_part.start_sketch` `sketch_corner_rectangle` `end_sketch` `extrude_boss` · `sw_hole_features.create_counterbore_hole` `create_through_hole`<br>✅ `part_and_features`(2024+2026) · `holes_and_finishing`(2024+2026)<br>**判据**：跨度 == 传进去的**毫米数**（事实 73）+ **回读孔径轴位** ≤0.05/0.1 mm |
| **T5b** | ★★ **在铝型材上打螺纹通孔**（导轨**直接拧进型材**，**不用梯形螺母**）| ★ **这是一条真缺口，见 §十** · `sw_hole_features.configure_straight_tap`（**只有配置器**）+ `list_hole_standards` `list_fastener_types`<br>⚠ **创建路径没有**：`hole_wizard(...)` 是 `pass`；`HoleWizard5` **全仓从未被调用**<br>**判据（建成后）**：① 回读孔径与**螺纹规格**（如 M5）② 型材上**孔数 == 导轨安装孔数** ③ ★ **导轨与型材的孔轴同轴** |
| **T6** | **装配 + 加配合** | `sw_assembly.add_component` `add_mate_coincident` `add_mate_concentric` `add_mate_distance`<br>⚠ `assembly_and_mates` = `verified` **但只在 `2024` 验过，本机 2026 SP4.1**<br>**判据**：`collect_mate_feature_summary` 配合数 == 加进去的条数 |
| **T7** | ★ **端板与型材建立外部参考**（共线） | `sw_assembly_doc.edit_part_in_context` → `sw_sketch_edit.convert_entities` → `sketch_relations.add_relation(COLINEAR=27)` → `exit_edit_part_in_context`<br>★ **轮 161 已做（未提交）** · ⚠ **无能力条目**<br>**判据**：① `GetEditTarget` **非空** ② `GetRelationsCount` **N→N+1** ③ `ListExternalFileReferencesCount` **0→≥1**<br>⚠ **与另一会话重叠 —— 以他为准** |
| **T8** | ★ **参数化：行程驱动全设计** | `add_equation` `evaluate_equations` `create_configuration` `activate_configuration` `update_dimension_mm`<br>✅ `equations`(2026) · `configurations_and_design_tables`(2026) · `parameter_updates`(2024+2026)<br>**判据**：**改行程 ⇒ 端板宽 + 型材长 + T4 改造件长度 三处同时变**（★ **跨零件、跨标准件**）|
| **T9** | **干涉检查** | ⚠ **无能力条目** · **判据**：**故意让两件重叠 ⇒ 干涉数 ≥1**（反向验证）|
| **T10** | ★ **拓扑：端板镂空**（**提前**） | `sw_topology.create_topology_study` `set_topology_goal` `create_mass_constraint` `create_factor_of_safety_constraint` `create_preserved_region` `create_thickness_control` `run_topology_study` `collect_topology_numbers`<br>✅ `topology_optimization`(2026，真机跑通并取到 Material Mass)<br>**判据**：取到 Material Mass + **质量下降** · ★ 端板是**单实体**，不受官方限制 |
| **T11** | ★ **仿真：抗扭/刚性 —— 与 T10 对比**（**推后**） | `sw_simulation.set_material` `create_static_study` `apply_fixed_restraint` `apply_normal_force` `create_mesh` `run_analysis` `create_plot` · `sw_simulation_results.get_displacement_at_points`<br>✅ `simulation_and_fea`(2026)<br>**判据**：★ **拓扑前后各跑一次，对比位移/应力** ⇒ 「**镂空损失了多少刚性**」有数<br>★ **这就是业主的「不然拓扑了之后到底损失多少刚性，你怎么判断」** |
| **T12** | ★ **工程图：端板 + 型材加工图（含螺丝孔）** | `subskills/solidworks-engineering-drawing`（51 个函数）· `generate_drawing_from_spec`(DrawingSpec v1) `select_drawing_template` `create_standard_views` `insert_dimensions` `auto_insert_center_marks` **`get_hole_table`** `export_sheet_to_pdf`<br>✅ `drawings_and_bom`(2024+2026) · `drawing_dimension_insertion`(2024+2026)<br>**判据**：PDF 存在 **且** `inspect_drawing_structure` 视图数/尺寸数 ≥ 预期 |
| **T13** | **BOM + 打包** | `sw_delivery.collect_assembly_bom` `export_assembly_bom_csv` `build_bom_traceability` `pack_and_go`<br>✅ `custom_properties_and_bom`(2024+2026) · `pack_and_go`(2024+2026)<br>**判据**：BOM 行数 == 组件**种类**数 |
| **T14** | **导出** | `sw_export.export_to_step` `export_to_dxf` `export_to_pdf` `export_to_stl`<br>✅ `export_delivery`(2024+2026)<br>**判据**：**magic 头对**（`tools/probe_export_magic_matrix.py` 可复用）|
| **T15** | **审查 / 成本 / DFM**（顺带） | `sw_review.run_review` `collect_geometry_measurements` `validate_hole_positions` · `sw_costing.create_cost_analysis` `read_cost_analysis` · `dfm_checks`<br>✅ `geometry_and_delivery_review` ⚠ **未记版本** · `costing`(2026)<br>**判据**：报告生成 · 成本**非零** · DFM 有结论 |

---

## 三、支链

| 支 | 任务 | 测什么 · 为什么分开 |
|---|---|---|
| **支 A** | ★ **运动：丝杆转 ⇒ 滑块平移 → 导出 AVI** | `sw_motion.create_motion_study` `add_constant_speed_rotary_motor` `calculate_and_play` `configure_avi_parameter` `export_motion_study_avi`<br>✅ `motion_study`(2026) · ★ **覆盖「动画导出」——三个护城河域之一**<br>**分开理由**：需 Motion 加载项，耗时长 |
| **支 B** | ★ **焊件支架**：CNC **龙门 X 轴 ↔ 机架**的连接侧板（**两个支腿**，不做 Y 轴/加工平台） | `sw_weldment.create_weldment_profile` `create_structural_member` `ensure_cut_list` `set_cut_list_properties` `export_cut_list_csv` `create_profile_center_mate`<br>✅ `weldments`(2026)<br>⚠ **必须先量**：`create_structural_member` 要**轮廓**，而本机**没找到 `weldment profiles` 目录**（`D:\SOLIDWORKS Data\lang\english` 下没有）⇒ 可能要用 `create_weldment_profile` 自己造<br>**分开理由**：轮廓前提未知 + 是**另一个装配**（机架） |
| **支 C** | 给模组加个**钣金罩** | `sw_sheet_metal.create_base_flange`（**真机验过**）<br>⚠ `create_edge_flange` / `create_one_bend` / `create_gusset` —— **已知事实 47：pywin32 到不了**<br>**分开理由**：三条里两条预期会红 |

---

## 四、★★ 主链引入的**新测试维度**：GUI + COM 混用

这是 v2 没有的 —— T2（GUI）与 T3/T4（COM）**在同一个任务里交替**：

| 风险 | 说明 |
|---|---|
| **焦点** | Windows 只把键鼠事件投给**前台窗口** ⇒ 每个 GUI 动作前必须确认前台是 SolidWorks，**否则跳过并留证** |
| **抢鼠标** | `SetCursorPos` 会抢用户鼠标 ⇒ 动作之间必须让回 |
| **坐标** | 分类导航的 UIA 报**虚拟坐标** ⇒ 卡片 rect 不能点；画布坐标要从**截图**量 |
| **输入** | 数字会被逐键输入吃掉 ⇒ **必须剪贴板粘贴** |
| **单源** | 事实 24：COM 只能一个进程连 ⇒ GUI 链与 COM 步骤**不能并行** |
| **收尾** | GUI 链**没有** `CommandInProgress` 这层保护 ⇒ 弹窗风险更高（事实 64）|

⇒ ★ **主链的 T2 应当有「每一步的截图 + 状态 JSON + 超时」** —— 这正是 `sw_jlcfa_steps` 已经做的（业主当初的指正促成的）。

---

## 五、⚠ 明确**不覆盖**的

| 域 | 为什么 |
|---|---|
| **曲面** | `surface_modeling` = **`stitched`**；`IModeler.Create*Surface` 返回值**跨次会变**（事实 40）|
| **模具** | `mold_tools` = `stitched`；不属本场景 |
| **Routing** | 需加载项 + 许可证 |
| **3D 草图 / 样条族** | 与直线模组无关 |
| **外观** | ⚠ **能力清单里无条目** |

**覆盖度**：主链 T1–T15 覆盖 **约 16 条** + 支链 A/B/C **3 条** ⇒ **约 19 / 36 ≈ 53%**。

---

## 六、★ 预期会红的点（先写下来，别当事故）

1. **T6 装配** —— `assembly_and_mates` **只在 2024 验过**，本机 2026 SP4.1
2. **T4 改造标准件** —— 插件生成的件能不能接方程，**未知**
3. **T15 审查** —— `geometry_and_delivery_review` **未记 `verified_versions`**
4. **支 B 焊件** —— `weldment profiles` 目录本机没找到
5. **T2 GUI 链** —— 依赖前台焦点，**用户一动鼠标就可能失败**（这是设计约束，不是 bug）

---

## 七、必须先量

1. `GetRelationsCount(Filter)` 各 Filter 的**基线**
2. `ListExternalFileReferencesCount` 的**基线**
3. ★ **插件插入的件**：是不是配置驱动？长度能不能改？
4. ★ **插件插入的件**：能不能接方程 / 需不需要另存
5. **`create_structural_member` 的轮廓从哪来**
6. ★ **`sw_jlcfa_index.search` 的检索质量**（6.3 万型号里按品类查准不准）

---

## 八、给业主的两条**体系建议**（可选）

1. ★ **`jlcfa`（标准件选型）应当有一条能力条目** —— 现在 13 个模块、15 MB 索引、6.3 万型号，**在 `capabilities.yaml` 里 0 命中**。
   建议 `level: verified` 需先补冒烟（**现在 `tests/` 与 `tools/` 里 0 个 jlcfa 文件**）。
2. ★ **`sw_jlcfa_steps` 记下的那批真机事实**（虚拟坐标 / 剪贴板粘贴 / Enter 不触发 / 前台焦点 / 抢鼠标）**值得进 `docs/known-facts.md`** —— 它们与 COM 那套事实同等重要，而且更隐蔽。

---

## 九、与另一会话的现状对齐（截至 2026-10-01 19:15）

```
他：Spec Kit 081 · 最新提交 4e8cdab「fix(081): AddRelation 必须包 VARIANT(VT_ARRAY…)」
★ T7 与他的轮 161 **重叠** ⇒ 交接时以他的为准，别重复做。
```

---

## 十、★★ v5 更正：**螺纹通孔不是缺口** —— 我上一版错了

> ⚠⚠ **本节原写「真缺口」，是错的。** 保留在此作**反面教材**。
> 真实情况：`subskills/solidworks-threaded-holes/`（**`manifest.yaml: status: stable`**）**早已实现**，
> 且 **`capabilities.yaml` 的 `holes_and_finishing`（`verified`，2024+2026）覆盖它** ——
> 该条目的 label 就写着「**孔槽、螺纹、圆角与倒角**」。
>
> **我错在哪（错误链条，值得记）：**
> ```
> ① 只搜 scripts/sw_*.py                ⇒ 漏了 subskills/
> ② 正则里没有 攻丝/螺纹孔/thread_hole   ⇒ 又漏一次
> ③ ★ Select-Object -First 22 **截断输出** ⇒ 探针其实搜到了，我没往下看
> ④ ★★ 用一个 API 名（HoleWizard5）的 0 命中 ⇒ **推断一整类能力的缺失**
> ```
> ★ **第 ④ 条最根本**：官方**可能有多条路**。这个子技能走的是
> **「攻丝底孔（拉伸切除）+ 孔口倒角 + `Metric Tap` 真实 Thread 特征」**，**完全绕开 `HoleWizard5`**。
> ⇒ 「`HoleWizard5` 0 命中」是**真的**；「螺纹孔没实现」是**假的**。
>
> **实际状态：**
> ```
> subskills/solidworks-threaded-holes/    manifest.yaml: status: stable
>   · M3/M4/M5/M6/M8/M10/M12 粗牙 ISO 公制内螺纹；表外规格必须显式给底孔（不猜）
>   · 盲孔 + **真正 Through All** 贯穿孔
>   · **Metric Tap 真实 Thread** / CosmeticThread / 精确螺距 3D 证据螺旋线 —— **三级降级**
>   · ★ **SW2026 已实测 M6×1 6H 右旋盲孔与贯穿孔，重建后识别到真实 Thread 特征并通过交付审查**
>   · 交付：SLDPRT + STEP + parameters.json + review_report.json + 等轴测/三视图
> 测试：tests/test_threaded_hole_subskill.py（9 个测试，fake 对象 —— 契约测试）
> 登记：docs/skill-map.md · api-map.* · family-coverage.* · gap-analysis.md · signature-audit.md · usage-guide.md
> ```
> ⚠ **`HoleWizard5` 那条确实是待办** —— 但是**它自己的 roadmap 写的 P1**，不是我的推断：
> > ### P1：原生孔语义与现有零件（优先级最高）
> > **目标**：在用户要求**标准孔标注、孔表**或**数据库驱动螺纹规格**时，
> > 优先创建**原生 Hole Wizard 攻丝孔**，而不是**底孔 + Thread 组合**
> > **验收门槛**：盲孔/贯穿各至少 3 次连续成功；重开 SLDPRT 后仍能回读标准、规格、底孔、
> > 螺纹深度和孔位；**生成的工程图孔标注与模型一致**
>
> **⇒ 对业主的场景**（导轨直接拧进型材的螺纹通孔）：**M5/M6 贯穿螺纹孔现在就能用**
> （`create_threaded_hole_template.py --through`），**不需要立项**。


### 10.1 业主的两条澄清

**① 是 `FK` 法兰式丝杆固定座** —— 已核实嘉立创索引里**就有**：
```
FKA              方法兰丝杠支座组件 固定侧
FK-C5 / FK-C3 / FK-P5    圆法兰丝杠支座组件 标准型 固定侧
E-FK             经济型圆法兰丝杠支座组件 标准型 固定侧
（品类：滚珠丝杠支座组件）
```
⇒ **方法兰与圆法兰都有**，T1/T2 的检索目标就写这几个 code。

**② 新场景：直接在铝型材上打螺纹通孔，导轨直接拧进去，不用梯形螺母（T 型螺母）**
⇒ 已加为 **T5b**。

### 10.2 ⚠⚠ 为什么 T5b 是一条**真缺口**

我核了三层，**结论是我们建不出螺纹孔**：

| 层 | 实况 |
|---|---|
| **`create_blind_hole` / `create_through_hole`** | ★ 是 **`_circle_cut`（画圆 + 拉伸切除）**的等价物，**不是孔向导** ⇒ **打出来是光孔，没有螺纹** |
| **`hole_wizard(model, ...)`** | ★ **`pass` 空实现**（上游留下的框架），只在一句注释里提到 `HoleWizard5` |
| **`configure_straight_tap` / `configure_tapered_tap`** | ★ **只是配置器** —— 要先把 `IStraightTapElementData` / `ITaperedTapElementData` **拿到手**，而**没有任何生产代码拿到过它**；全仓唯一调用点在 `tests/test_extended_modules_contract.py`，**用的是假对象** |
| **`HoleWizard5`** | ★ **全仓 0 次实际调用**（只在 `sw_part.py:917` 的注释里出现） |

★ 这是本项目反复记录的同一类：**「孤立函数从没跑过」** —— 配置器有了，**创建路径没有**。

⚠ **而 `capabilities.yaml` 里 `holes_and_finishing` 是 `verified`（2024+2026）** ——
那是**光孔**的 verified，**不含螺纹孔**。⇒ 别把这两件事混起来。

### 10.3 官方入口（三源核实）

```
IFeatureManager.HoleWizard5( GenericHoleType, StandardIndex, FastenerTypeIndex, SSize,
    EndType, Diameter, Depth, Length, Value1..Value12, ThreadClass, RevDir,
    FeatureScope, AutoSelect, AssemblyFeatureScope, AutoSelectComponents,
    PropagateFeatureToParts )                       ← 27 参
来源：C:\swapi\types\IFeatureManager\HoleWizard5.md
现行入口是 HoleWizard5（反射里 HoleWizard → 2 → 3 → 4 → **5**）
```
**孔类型 `swWzdGeneralHoleTypes_e`：**
| 成员 | 值 | 说明 |
|---|---|---|
| `swWzdCounterBore` | 0 | |
| `swWzdCounterSink` | 1 | |
| `swWzdHole` | 2 | 光孔 |
| `swWzdPipeTap` | 3 | Tapered tap hole（锥螺纹）|
| ★ **`swWzdTap`** | **4** | ★ **Pipe/straight tap hole（直螺纹孔）** ← **T5b 要用的** |
| `swWzdLegacy` | 5 | 反射里查无数据 |

⚠ ⚑ **官方一条专门针对攻丝孔的坑**（`HoleWizard5.md` 的 `Length` 参数说明）：
> "For both straight/pipe and tapered tap holes, **the macro recorder fails to properly record this parameter**. Before running a macro recording, you must add **-1** at this position and delete a **-1** before `ThreadClass`."

⇒ **攻丝孔的 `Length` 参数与其它孔类型不同**，照着普通孔写会错位。

### 10.4 T5b 的建议做法与判据

```
① list_hole_standards / list_fastener_types / list_fastener_table_types   ← 已有，先拿螺纹标准与规格
② HoleWizard5(GenericHoleType=swWzdTap(4), StandardIndex=…, FastenerTypeIndex=…,
              SSize="M5", EndType=…, …, ThreadClass=…)                    ← ❌ **要新做**
   或 configure_straight_tap(...) 配置 + 同一个入口建                  ← 配置器已有，缺"拿到 element"的那一步
③ 判据（三条，都能被空操作证伪）：
   ① 回读孔径与**螺纹规格** == 写死的（如 M5）
   ② 型材上的**孔数 == 导轨安装孔数**
   ③ ★ **导轨与型材的孔轴同轴**（这是"直接拧进去、不用 T 型螺母"的几何前提）
```

### 10.5 顺带：这条缺口**值得单独立项**

- 它是**真缺口**（不是"没验过"，是**没写**）
- 它**有官方依据**（签名 + 常量 + 那条攻丝坑都齐了）
- ★ 它是**业主真实工作流的第一步**（"导轨直接装在型材的螺纹通孔里"是很常见的做法）
- ⚠ 而且 `holes_and_finishing` 的 `verified` **不覆盖它** ⇒ 补齐后是**新增能力面**

---

## 十一、★★ v5 新增：端板加工图的**公差 + 粗糙度**标注

### 11.1 业主的场景
端板的加工图，**要标注误差（公差）与粗糙度** —— 在**工程图里做标注**时。

### 11.2 逐项实况（这次是「已注册未封装」还是「真缺」，分清了）

| 标注 | 官方入口 | 状态 |
|---|---|---|
| **形位公差 GD&T** | `IModelDoc2.InsertGtol` + `IGtolFrame.AddIndicator` | ✅ **已实现且真机验过** · `scripts/sw_gtol.py` · `tests/test_sw_gtol_contract.py` · `tools/verify_gtol_smoke.py`（`038` 补的）|
| **★ 表面粗糙度 Ra** | ★ `IModelDocExtension.InsertSurfaceFinishSymbol3` | ⚠ **已注册未封装**（登记表值 14/48）· 无实现 |
| **★ 尺寸公差** | `IDimension.set_Tolerance` / `set_ToleranceType` | ⚠ **已注册未封装**（登记表有）· 无实现 |
| **基准符号（独立）** | `IModelDocExtension.InsertDatumTag` | ⚠ 已注册未封装 |
| **焊接符号** | `InsertWeldSymbol` / `2` / `3` | ⚠ 已注册未封装 |

⚠ **「已注册未封装」= 半缺**（能调、没包）—— **不是真缺**。这正是 `EditPart2` 那一类。

### 11.3 ★★ 粗糙度符号有**三代废弃链**，而且跨了**三个接口**

```
IDrawingDoc.InsertSurfaceFinishSymbol       → Obsolete. Superseded by IModelDocExtension::InsertSurfaceFinishSymbol3
IModelDoc2.InsertSurfaceFinishSymbol2       → Obsolete. Superseded by IModelDocExtension::InsertSurfaceFinishSymbol3
★ IModelDocExtension.InsertSurfaceFinishSymbol3(SymType, LeaderType, LocX, LocY, LocZ,
      LaySymbol, ArrowType, MachAllowance, OtherVals, ProdMethod, SampleLen,
      MaxRoughness, MinRoughness, RoughnessSpacing) → SFSymbol        ← **现行**
来源：C:\swapi\types\IModelDocExtension\InsertSurfaceFinishSymbol3.md
原文：「Creates a surface-finish symbol **based on the last selection**.」
枚举：SymType→swSFSymType_e · LeaderType→swLeaderStyle_e · LaySymbol→swSFLaySym_e
★ 能写 **MaxRoughness / MinRoughness**（Ra 上下限）—— 正是业主说的「粗糙度」
```
⇒ ★ **比椭圆那条两级链更深**：这次是 `IDrawingDoc` → `IModelDoc2` → **`IModelDocExtension`**，**换了两级接口**。

### 11.4 尺寸公差的官方成员（反射实测）

```
IDimension:
  Double get_Tolerance() / set_Tolerance(Double)          ← ★ 公差值
  Int32  get_ToleranceType() / set_ToleranceType(Int32)   ← ★ 公差类型（swTolType_e）
```

### 11.5 加进任务表：**T12b**

| # | 任务 | 测什么 · **判据** |
|---|---|---|
| **T12b** | ★ **端板加工图的公差与粗糙度标注** | ① **GD&T**：`sw_gtol.insert_gtol(...)` + `add_gtol_indicator(...)`（`datum="A"`）—— ✅ **现在就能做**<br>② **粗糙度**：`InsertSurfaceFinishSymbol3`（**要新做**，走 `IModelDocExtension`）<br>③ **尺寸公差**：`IDimension.set_Tolerance` / `set_ToleranceType`（**要新做**）<br>**判据（三条，都能被空操作证伪）**：<br>　① 建 GTol 前后，视图上**公差框数量 +1**（`sw_drawing_view.get_annotations`）<br>　② 粗糙度符号**能被 `drawing_workflow` 的收集器读回**（`surface_finish_symbols` ≥1，`text_parts` 含 `Ra`）<br>　③ 尺寸的 `get_ToleranceType()` **等于写进去的枚举值** |

★ **②的判据特别好用**：`drawing_workflow` **已经有读回粗糙度符号的能力**（`_professional_annotation_record(owner, "surface_finish", ...)`）
⇒ **「插进去 ⇒ 读得回来」形成闭环** —— 这正是本项目爱用的「写==读」形状。

### 11.6 ⚠ 未验证

* `InsertSurfaceFinishSymbol3` **在 `IModelDocExtension` 上**（登记表在 `IModelDoc2`/`IDrawingDoc` 段也提到同名）⇒ **实际对象从哪拿要实测**
* `set_Tolerance` 的**语义**（是差值还是上下偏差）**没查**
* 工程图的**孔标注自动验收** —— `sw_sketch`/`threaded-holes` 的 roadmap 都列为**后续扩展**

---

## 十二、★★★ v6 补充：全量盘点后**漏掉的五块**

> 方法：不预设前缀、不截断，把 `scripts/`（**130 个 .py，113 个有公开函数**）、
> `subskills/`（**5 个**）、`examples/`（**11 个**）全列一遍，再对着场景筛。

### 12.1 ★★ `subskills/solidworks-fillet-chamfer-cnc`（**`status: stable`**）—— 我完全漏了 CNC

```
advanced_fillet_strategy.py       10 个  validate_variable_spec / validate_face_spec / validate_hold_line_spec / …
cnc_strategy.py                   11 个  ★ 离线参数 + DFM 约束 + 执行计划（**纯标准库，可在 CI 跑**）
create_cnc_mount_template.py      28 个  ★ **参数化 CNC 风格安装座**，带拓扑证据；`--dry-run` 可离线
hold_line_bridge.py                9 个  保持线（已知事实 47 的对照）
verify_advanced_fillets.py         2 个
verify_open_source_bracket.py      3 个  ★ 开源支架回归（**有现成对标件**）
verify_open_source_complex_case.py 11 个
```
⇒ ★★ **对「端板加工」与「CNC 龙门」是直接相关**，而且它 **stable、自带验证脚本、有开源对标件**。
⇒ **这是本项目里离「CNC 加工性」最近的一块，我前面十几版全漏了。**

### 12.2 ★★★ `scripts/sw_featureworks.py` —— **T3/T4 的隐藏前提**

```
FeatureWorks 自动特征识别：IFeatureWorksApp 封装
  recognize_and_create / recognize_interactive / set_advanced_options / set_performance…
域 14 · 路由 / Composer / PDM（**需许可证**）—— fworks 段共 2 个段 / 7 个成员
```
⇒ ★★★ **这才是「改造标准件」能不能做成的关键**：
**嘉立创插件插入的件如果是导入实体（无特征树）⇒ 没有尺寸可改** ⇒
**必须先 FeatureWorks 识别成特征，参数化才成立**。
⚠ 但它**在「需许可证」那一域** ⇒ **能不能用要先量**（若无许可，T4 只能改成"在装配里用方程驱动位置"）。

### 12.3 ★★ 外部 FEA + **网格收敛** —— 比单一仿真强

```
scripts/fea_analysis.py      6 个  validate_analysis / discover_solver / parse_calculix_results / build_calculix_i…
scripts/fea_convergence.py   2 个  ★ CalculiX **多网格收敛序列**执行与证据汇总
examples/generate_fea_convergence_example.py  ★ 五档真实 C3D8 悬臂梁网格收敛请求
```
⇒ ★ **T11 的加强版**：不只跑一次仿真，而是**跑五档网格看收敛** ⇒
**「网格够不够密 / 结果可不可信」有依据**。这是单一求解给不了的。

### 12.4 ★★ `scripts/delivery_compare.py` —— 参数化前后**交付对比**

```
snapshot_files / compare_snapshots / build_regeneration_request
「交付物版本比较与可审计重新生成计划」
```
⇒ ★ 与 **T8（参数化）** 天然配套：**改行程前存快照 → 改 → 再存 → 对比** ⇒
**「哪些文件变了、哪些没变」可审计**。这比只看一个边界框强得多。

### 12.5 ★★★ `subskills/solidworks-vibecad`（`experimental`）—— **可能就是流程设计本身**

```
plan_from_brief.py        7 个  「从自然语言需求生成 SolidWorks 参数化设计计划」
                                 ——把需求收敛为**可审查、可交给 API 封装执行的 JSON 计划**
sw_execution_outline.py   4 个  load_plan / build_outline / write_markdown
```
⇒ ★★★ **这正是业主想要的「设计流程」的自动化形态**：
**需求 → JSON 计划 → 可执行大纲**。
⇒ 建议：**把我们这张任务表喂给它试一次**，看它生成的大纲与本文档差多少 —— 那是一次**免费的对标**。

### 12.6 其它**值得加进场景**的（按价值）

| 模块 | 加它测什么 |
|---|---|
| **`scripts/sw_pattern.py`** | ★ 导轨安装孔的**线性阵列**（`configure_linear_pattern`）—— 真实做法 |
| **`scripts/sw_pdm.py`**（13 个）| 自定义属性 / 配置管理 ⇒ **BOM 与标题栏的基础** |
| **`scripts/sw_preflight.py`**（11 个）| ★ **开工前预检** —— 每个流程的**第一步**应固定是它 |
| **`scripts/dfm_review.py` + `dfm_profiles.py`** | DFM 报告 + **供应商能力档案合并** ⇒ 与 CNC 子技能配套 |
| **`scripts/sw_helix.py`** | 螺旋 ⇒ **丝杆**或螺旋槽 |
| **`scripts/sw_import_mesh_reference.py`** | 导入网格参考（扫描件/参考模型） |
| **`scripts/sw_view.py`**（27 个）· `sw_capture.py` · `sw_render_material.py`（8 个）| 视图/截图/渲染材质 ⇒ **证据与报告** |
| **`scripts/headless_cad_writer.py`**（9 个）| 无 CAD 输出 STL/OBJ/DXF/SVG/PDF ⇒ **离线交付** |
| **`scripts/sw_selection.py`**（24 个）· `sw_selection_tx.py` | ★ **选择集事务**（`edit_feature_selection`） |
| **`scripts/sw_com_traps.py`** | ★ `is_type_mismatch` / `explain` / `byref_pair` / `adaptive_arity` ⇒ **COM 陷阱诊断**（正是这几轮踩的） |
| **`scripts/sw_automation_knowledge.py`** | `explain_hresult` / `enter_command_lock` / `exit_command_lock` |
| **`scripts/sw_macro_guard.py`**（9 个）| `validate_vba_macro` / `extract_vba_code` |
| **`scripts/sw_geometry_selectors.py`** | `available_point_selectors` / `available_direction_selectors`（声明式选择的底座）|
| **`scripts/sw_session.py`** | 友好 Session API（`examples/06_friendly_api.py` 演示）|
| **`examples/` 11 个** | ★ **现成工作流样本**：`08_mini_fan_motion_assembly` · `09_sheet_metal` · `11_simulation_study` · `05_drawing` · `04_batch_export` |

### 12.7 仍**不覆盖**的（维持原判）

`sw_mold`（`stitched`）· `sw_routing`（需加载项+许可）· `sw_surface`/OCP 路线（`stitched`，事实 40）·
`subskills/autocad-automation`（另一个 CAD）· `sw_addin_host`（C# 宿主）。

### 12.8 ⇒ 覆盖度**上调**

```
v3 说约 19/36 ≈ 53%
v6 加上 CNC 子技能 + FeatureWorks + 外部FEA收敛 + 交付对比 + PDM/属性 + 预检 + 阵列
⇒ **约 24~26 / 36 ≈ 67~72%**
```
⚠ 但**新增的这几块大多还没进过我们的测试**，红的风险不低 —— 见 §六 的「预期会红」。

---

## 十三、★★ v7：**爆炸视图 + 渲染效果图** —— 覆盖情况

### 13.1 逐项实况（**先分清「已注册未封装」与「真缺」**）

| 你要的 | 官方入口 | 我们的状态 |
|---|---|---|
| **爆炸视图** | `IAssemblyDoc.CreateExplodedView` · `AutoExplode` · `ShowExploded2` · `ViewExplodeAssembly` · `GetExplodedViewNames2` · `EditExplodeParameters`<br>（登记表值：`CreateExplodedView` 155/169 · `AutoExplode` 50 · `ShowExploded2` 156/2 · `ViewExplodeAssembly` 16 · `GetExplodedViewNames2` 172 · `EditExplodeParameters` 35）| ⚠ **已注册未封装** = **半缺**<br>实测：这些名字**只出现在 `scripts/sw_assembly_doc.py` 的 arity 表**（L104/110/122/146/206/219，**字典条目**）⇒ 能通过 `call_assembly_doc` 调，**没包** |
| **爆炸动画（AVI）** | `IMotionStudyManager.CreateAVIParameter()`（零参）· `SaveToAVI` | ✅ **已实现** · `scripts/sw_motion.py` 的 `create_avi_parameter` / `configure_avi_parameter` / `SaveToAVI`<br>★ **真机端到端**：`tools/verify_motion_avi_e2e.py`（导出**非零 AVI**）· 契约测试 `tests/test_sw_motion_avi_contract.py`<br>⚠ `capabilities.yaml` 的 `animation_export` 仍是 **`stitched`**（API 链已真机验证，等 e2e 证据入账）<br>★ 这是**三个护城河域之一** |
| **★ 渲染效果图（光线追踪）** | ★ `IRayTraceRenderer.RenderToFile(String, Int32, Int32)` + `InvokeFinalRender()` | ❌ **实现里 0 命中** · 7 个成员**全没实现** |
| **外观 / 材质** | `IModelDocExtension.CreateRenderMaterial(String)` → 设 `IRenderMaterial` 属性 → `AddRenderMaterial` | ✅ **已实现** · `scripts/sw_render_material.py`（60 处）+ `tests/test_extended_modules_contract.py`<br>★ 走**现代路线**（不是旧的 `IMaterialVisualProperties`）|
| **普通截图 / PNG·JPG** | `IModelDoc2.SaveBMP` · `IModelDocExtension.SaveAs3`（图片过滤器）· GDI `PrintWindow` | ✅ **已实现三套，且分工明确**<br>`sw_export.export_to_bmp`（当前视图，可指定尺寸）· `sw_export.export_to_image`（**PNG/JPG**，尺寸不可指定）· `sw_capture.capture`（**抓窗口、不受遮挡**）|
| **多视角预览 + 审查证据** | — | ✅ `scripts/sw_review.py`：`save_review_previews` / `save_preview` / `set_standard_view` / `zoom_to_fit` / `inspect_bmp_preview` |
| **无 CAD 预览** | — | ✅ `scripts/headless_cad_writer.py`（SVG / PDF / PNG，无第三方依赖）|
| **★★ 离线批量渲染** | **`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS Visualize\OfflineRendererConsole.exe`** | ⚠ **本机装着、能跑、仓库 0 命中**（见 13.3）|

### 13.2 ⚠⚠ 一个**本项目自己记录的陷阱的活标本**

```
docs/family-coverage.md 里写着：
  | 全量索引/sldworks | `IRayTraceRenderer` | 7 | **7** | **100%** |
⇒ 但「实现里 0 命中」—— 7 个成员一个都没写。
★ 那个「100%」是**编目录口径**（名字在 sw_api_sldworks.py 的**接口名字符串列表**里，
  见 L417 `'IRayTraceRenderer',`），**不是"有实现"**。
```
⇒ ★★★ **这正是 `AGENTS.md` §一 自己写的那个坑**：
> 「**三列不可合并**。早先只报一列，「族触及率 100%」是靠**把名字列进登记表**达成的」

**`IRayTraceRenderer` 就是那个「100%」的活标本** —— 用来当教学例子很合适。

### 13.3 ★★ 新发现：本机装着 **SOLIDWORKS Visualize**（仓库 0 命中）

```
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS Visualize\
  SLDWORKSVisualize.exe                主程序
  ★★ OfflineRendererConsole.exe        **命令行离线渲染器**（30,808 B · 2026-08-14）
  ★  OfflineRenderer.exe               离线渲染器
  SWVisualize.Queue.exe                队列
  Bunkspeed.Exchange.dll               交换（**Bunkspeed** = 达索收购的专业渲染内核）
  Bunkspeed.Exchange.SolidWorksUtils.dll
  SWVisualize.Exchange.PluginHost.exe  ← ★ **SolidWorks ↔ Visualize 交换插件**
  AMD.ProRender.dll · amd_fidelityfx_vk.dll   GPU 渲染后端

D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS Visualize Boost\
  broker_node.exe · remote_node.exe     ★ **分布式渲染节点**
```
**实测（有超时、不碰 COM）：**
```
OfflineRendererConsole.exe --help  ⇒  15 秒内自己退出（退出码 -1），输出：
    CreateContext - type=Bunkspeed.Applications.OfflineRendererConsole.IOfflineRendererConsoleBootstrapContext
    CreateContext - type=Bunkspeed.Rendering.OfflineRendererApplication.Manage.IOfflineRendererShellContext
    CreateContext - type=Bunkspeed.Applications.OfflineRendererConsole.IOfflineRenderingConsoleDocumentContext
    ★★ Cannot find input folder for rendering: ''
⇒ **它要一个「输入文件夹」**，但**参数形态未定**：
  试了 4 种（位置参数 / `/input:` / `-i` / `/folder:`）都还是 `''`
  ⇒ 按**已知事实 53**（连续修补 ≥3 次就停下，不要继续猜）**停手，记「查不到」**
⚠ **没有找到 PhotoView 360 目录** ⇒ 本机是 **Visualize** 而不是 PhotoView
⚠ **仓库里对 Visualize 是 `0 命中`** ⇒ 这条**能自动化的路从没被发现**
```

### 13.4 加进任务表

| # | 任务 | 测什么 · **判据** |
|---|---|---|
| **T16** | ★ **爆炸视图**（**半缺，要做**） | `call_assembly_doc('CreateExplodedView', …)` / `AutoExplode` / `ShowExploded2`<br>**判据**：① `GetExplodedViewNames2` 数 **0 → ≥1** ② `GetExplodedViewCount2` 一致 ③ 爆炸前后组件的**变换矩阵**变了（`sw_assembly.build_transform_data_x`）|
| **支 A′** | ★ **爆炸动画 → AVI** | 爆炸视图 + `create_avi_parameter` / `configure_avi_parameter` / `SaveToAVI`<br>**判据**：**AVI 文件非零**（`verify_motion_avi_e2e.py` 已经是这个判据）|
| **支 D** | ★★ **渲染效果图**（**两条路都没走**） | ① **COM 路**：`IRayTraceRenderer.RenderToFile(path, w, h)` + `InvokeFinalRender()`（**要新做**，7 个成员全空）<br>② **Visualize 路**：`OfflineRendererConsole.exe`（**参数形态要先查**）<br>**判据**：出图**非空且非纯色**（`inspect_bmp_preview` 已有像素检查能力）|

### 13.5 ⚠ 未验证 / 要先量

* `OfflineRendererConsole.exe` 的**参数形态**（试了 4 种，**未定**）
* `RenderToFile` 在 pywin32 下**能不能拿到 `IRayTraceRenderer` 对象**（先要 `ISldWorks` 上的入口，**没查**）
* `CreateExplodedView` 的参数与**是否需要预先选中组件**
* 本机**有没有 PhotoView 360 的许可**（目录都没有，走 COM 那条可能直接失败）

---

## 十四、★★★ v8：**「零命中 / 没做到 / 连计划都没有」的清单**

> 方法：**不猜** —— 直接问项目自己的台账 `docs/family-coverage.json`（881 族逐族覆盖，三列口径）。
> ⚠ 该表**由静态解析生成，未执行仓库代码、未连 SolidWorks**。

### 14.1 全局三列（881 族 / 15,466 成员）

```
编目录    15,466  (100%)     ← 名字在代码里出现过（**含只写在登记表里的**）
护栏可调  10,573  ( 68%)     ← 登记在某模块能力表里，且有 _checked(...) 可达路径
直接调     2,605  ( 17%)     ← 静态上看得见字面量的调用
```
⇒ ★★★ **83% 的成员「编进了目录、从没被真正调用」。**
**真·零覆盖（连名字都没编进目录）= 0 个族** —— 881 族名字全在。

⚠ ⚑ **一处不一致（值得记）**：`family-coverage.md` 的口径说明写
「16,615 个成员里，编入目录 12,870（77%）、真调用 2,636（16%）」，
而 `family-coverage.json` 实际合计是 **15,466 / 15,466 / 2,605**。
⇒ **md 的正文与 json 对不上**（可能是先后两次生成）。**以 json 为准，并记下这处不一致。**

### 14.2 按域归口（`hit>0` 且 `used==0` —— 编进目录、从没直接调）

| 域 | 族 | 成员 |
|---|---|---|
| 全量索引/sldworks | 102 | **841** |
| ★★ **仿真（需许可证）** | **36** | **642** |
| 路由/Composer/PDM | 52 | 233 |
| ★ **swdimxpert**（DimXpert 自动公差）| 42 | 153 |
| ★ **sldcostingapi**（成本细分）| 7 | 121 |
| swpublished | 11 | 75 |
| swmotionstudy | 7 | 51 |
| SWRoutingLib | 3 | 14 |
| dsgnchk（Design Checker）| 1 | 8 |
| sldtoolboxconfigureaddin | 2 | 7 |
| **合计** | **263 族** | **2,145** |

### 14.3 ★★★ 最扎眼：**仿真域 36 族 / 642 个成员，直接调全为 0**

```
ICWDynamicStudyOptions          119   ICWStaticStudyOptions            57
ICWFrequencyStudyOptions         33   ICWDropTestSetup                 30
ICWFatigueStudyOptions           27   ICWBeamBody                      27
ICWLoadCaseManager               27   ICWBucklingStudyOptions          26
ICWTopologyStudyManager          24   ICWThermalStudyOptions           22
ICWMultipleContactSetsEditManager 22  ICWContactManager                20
ICWCable                         19   ICWEdgeWeldConnector             19
… （共 36 族）
```
⇒ **我们对外说 `simulation_and_fea = verified`，但验的只是 `ICWStudy` 的一小部分**；
**动态 / 静力选项 / 频率 / 跌落 / 疲劳 / 梁 / 载荷工况 / 屈曲 / 拓扑管理器 / 热 / 接触 / 点焊 / 线缆 —— 全部没碰。**

### 14.4 ★★★ 与「我们反复踩的坑」直接对应的一个**零调用族**

```
ISafeArrayUtility    21 个成员    护栏=21    直接调=0
```
⇒ **这是本项目一连串 BYREF / 数组坑的官方工具集** —— 而**我们一个没用**：
```
事实 12  VARIANT(VT_DISPATCH, None)
事实 33  SelectByID2/Select4 的 Callout 必须传 VARIANT(VT_DISPATCH, None)
事实 68  Object& 出参必填（VT_BYREF|VT_VARIANT）
轮 081   fix: AddRelation 必须包 VARIANT(VT_ARRAY…)
```
★ **官方给了 21 个成员的 SAFEARRAY 工具，我们全靠手搓 `VARIANT(...)`。**

### 14.5 其它**零调用、且与场景相关**的族（25 个）

| 族 | 成员 | 为什么值得看 |
|---|---|---|
| **`IRayTraceRendererOptions`** | 36 | ★★ **渲染选项** —— 上轮只找到 `IRayTraceRenderer`(7)，**选项另一半 36 个** |
| **`ISwScene`** | 35 | ★★ **场景（背景/环境/地板/光源）** —— 效果图的**另一半** |
| **`ITessellation`** | 28 | 三角剖分/网格化 ⇒ 几何核验与导出 |
| **`IDragOperator`** | 25 | ★★ **拖拽 + 碰撞检测** —— 装配体干涉的官方做法 |
| `IFrame` | 25 | SW 主窗口框架（add-in） |
| **`ICostAnalysisMachining`** | 24 | ★ **机加工成本**（与 CNC 龙门直接相关）|
| `IRouteManager` | 21 | 管线（需加载项） |
| `ICommandManager` | 21 | add-in 命令管理 |
| **★ `ISafeArrayUtility`** | 21 | 见 14.4 |
| `ITabAndSlotGroupData` | 21 | 钣金 tab/slot |
| **`ICostAnalysisSheetMetal`** | 20 | ★ 钣金成本 |
| **`IMBD3DPdfData`** | 20 | ★★ **MBD / 3D PDF** —— 无纸化交付 |
| **`IPrintSpecification`** | 20 | ★ **打印 / 出图规格** |
| `ISimulationMotorFeatureData` | 20 | 仿真马达 |
| `ICostAnalysisPlastic` / `Structural` / `3dPrinting` / `Casting` | 15/15/14/12 | ★ **成本分析只做了通用那块 —— 细分 6 族共 100 个成员全没碰** |
| `IMBDSTEP242Data` · `IPMIFrameData` | 6 · 6 | ★ **MBD / PMI（形位公差的三维标注）** |
| `IAutoRoute` · `IElectricalRouteProperty` | 7 · 5 | 电气布线 |
| `IPropertyManagerPage2Handler9` | 37 | ★ add-in 的 PropertyManager 回调 |

### 14.6 ⚠ **不是缺口**的一个陷阱样本（别误读台账）

```
IGtolFrame    9 个成员    编目录=9    护栏=9    **直接调=0**
⇒ 但我们对它**确实有实现**：scripts/sw_gtol.py 的 add_gtol_indicator 走 IGtolFrame.AddIndicator
⇒ 之所以「直接调=0」，是因为**成员名是通过变量传的**，静态归因看不到字面量
```
★ **这正是台账自己写的「直接调**系统性低估**，不是精确值」** ——
**读这张表时必须三列一起看，不能只看「直接调」。**

### 14.7 ⇒ **「连计划都没有」的**（不在任何规划里的）

| 项 | 状态 |
|---|---|
| **MBD / 3D PDF / PMI**（`IMBD3DPdfData` 20 + `IPMIFrameData` 6 + `IMBDSTEP242Data` 6）| ❌ **零调用，且任何文档里都没提过** |
| **`ISafeArrayUtility`（21）** | ❌ 零调用，**而且我们一直在手搓它该干的事** |
| **成本分析 6 个细分族（100 成员）** | ❌ 只做了通用那块 |
| **渲染的 `Options`(36) + `ISwScene`(35)** | ❌ 零调用（`RenderToFile` 那条上轮才被发现）|
| **`IDragOperator`（25）** | ❌ 零调用 |
| **`ITessellation`（28）** | ❌ 零调用 |
| **`IPrintSpecification`（20）** | ❌ 零调用 |
| **仿真动态/频率/屈曲/疲劳/热/跌落/梁/接触（642 成员）** | ❌ 零调用（对外却标 `verified`）|
| **DimXpert 42 族 / 153 成员** | ❌ 零调用（与 T12b 公差标注相关）|
| **Design Checker（dsgnchk，8）** | ❌ 零调用 |
| **`SOLIDWORKS Visualize` + `OfflineRendererConsole`** | ❌ **仓库 0 命中**（上轮才发现）|

### 14.8 ⚠ 引用这张表时的两条纪律

1. **三列不可合并** —— 「编目录 100%」只证明「这份 API 清单做完了」，
   **不等于「这些 API 都能用了」**（`IRayTraceRenderer` 就是那个 100% 的标本）。
2. **「直接调=0」≠「没实现」** —— `IGtolFrame` 是反例（有实现，名字走变量）。
   ⇒ 要判「有没有」，**必须回代码核**，不能只读这张表。
