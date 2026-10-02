# 24 小时计划（`plan-24h.md`）—— 挂柜台第二阶段

> 本文件**不写进度**（进度在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> 它写**队列、判据与理由**。★ 编号**现场核**（本会话已顺移三次）—— 下一个从 **141** 起。
> 前置：`docs/plan-next.md`（那是我先给的短版；本文件是**按 24 小时工作量**扩排的完整版）。

## 〇、24 小时该干什么 —— **由最窄的那个覆盖口径决定**

```
★ 覆盖口径 ③「**真机碰过**」= **1.53%**（126 / **8238** 个不重复成员名）
  ⇒ ★★ **8112 个成员名从未真机碰过** —— 这是"还剩多少活"的**唯一硬尺**（★ 台账自己标着
     口径 ①「名字出现过」≈100% 但**无判别力**，口径 ②「真的被调用」= 17.6%）
★ 而可挂的原料（首参 ∈ {model, sw_app, study} 且没挂）= **131 个**，覆盖 **29 个模块**
★ 另有 **5 条 `stitched` 待升级** + **1 条 `not_implemented`** + **5 条已记录的守卫缺口**

⇒ ★★ **24 小时 = 三件事并行**：
    ① **把 131 个自有能力挂出去**（主料，约 16–20 批）
    ② **把 5 条 `stitched` 升级成 `verified`**（★ 直接推进"验证分级"这个地基）
    ③ **把口径 ③ 从 1.53% 往上推**（★ 每批真机验证都会新增成员名 ⇒ 顺带完成）
```

**★ 节奏依据（本会话实测）**：一批（2–5 个工具 + 探针 + 真机证据 + 收工七步）≈ **1–1.5 小时**
⇒ **24 小时 ≈ 16–24 批** ⇒ ★ 正好覆盖 131 个的**一半左右** + stitched 升级 + 修地基。

---

## 段 1（0–4h）★★★ 仿真闭环**贯通** —— 护城河，也是 W7 唯一的硬前置

| 批 | 函数（能力层已有） | 判据 |
|---|---|---|
| **1.1** | `create_static_study` · `get_study_by_name` · `iter_studies` · `get_study_manager` | ★★ **W7 的 L1 遗留**：现在 `study_name` 只能引用**已存在**的研究 ⇒ 这批补上"能建研究" |
| **1.2** | `create_mesh` · `default_element_size_and_tolerance` · `run_analysis` · `collect_study_evidence` | ★ **闭环后半段**；判据现成：`ElementCount` 是正整数 · `study.Results` 非空 + `GetPlotCount > 0` |
| **1.3** | `sw_simulation_study` 的 `mesh_and_run` · `get_results_of` · `export_study` | ★ 研究级封装（★ `mesh_and_run` 可能一步到位）|

**贯通后的验收（一条命令）**：**建研究 → 赋材料 → 夹具 → 载荷 → 网格 → 跑 → 读数** 全链
⇒ ★ 这是护城河的**实体**：四家**一个都没有**。

---

## 段 2（4–8h）★★★ 仿真载荷族**广度** + 拓扑优化**挂柜台**

| 批 | 函数 | 备注 |
|---|---|---|
| **2.1** | `add_pressure` · `add_torque` · `add_gravity` · `add_centrifugal_force` | ★ 常用载荷四件套 |
| **2.2** | `add_bearing_load` · `add_remote_load` · `add_prescribed_displacement` · `add_temperature` | 进阶载荷 |
| **2.3** | `add_spring_connector` · `add_pin_connector` · `add_rigid_connector` · `add_bolt_connector` | ★ 12 种连接器里挑 4 个（装配体仿真用）|
| **2.4** | `collect_topology_numbers` · `list_topology_constraints_and_controls` · `get_topology_study_manager` · `get_topology_study_options` | ★★ **只读，风险最低 ⇒ 先挂**（★ 记忆里 A9 已达标，这批是"挂出去"）|
| **2.5** | `set_topology_goal` · `set_topology_iteration_options` | 拓扑参数（写）|

★ **验收**：载荷沿用 `Count == 2` 那类判据；拓扑沿用既有 `solidworks_topology_*` 的读法。

---

## 段 3（8–12h）★★ 建模闭环**补全** —— `sw_part` 的 17 个

| 批 | 函数 | 判据（★ 现成）|
|---|---|---|
| **3.1** | `sketch_rectangle` · `sketch_polygon` · `sketch_slot` · `sketch_ellipse` | ★ 与 batch21 同型：`count_lines` / `count_arcs` 回读断言 |
| **3.2** | `sketch_arc` · `sketch_centerline` · `sketch_spline` | 同上 |
| **3.3** | `add_dimension` · `auto_dimension_sketch` | ★ 回读尺寸值断言 |
| **3.4** | `linear_pattern` · `shell` · `rib` · `insert_dome` | ★★ **建特征 ⇒ 包围盒/特征树数字断言**（★ W4 续那套：40×20×10）|
| **3.5** | `insert_helix` · `insert_composite_curve` · `hole_wizard` | ⚠ `hole_wizard` 参数多；★ 既有 `create_hole_feature` 已挂 5 种孔 ⇒ **先核是否重叠** |

---

## 段 4（12–16h）★★★ 孔族 + 焊件 + 配置 + 导出 —— **广度**

| 批 | 函数 | 备注 |
|---|---|---|
| **4.1** | `create_blind_hole` · `create_through_hole` · `create_counterbore_hole` · `create_countersink_hole` | ★ 6 个孔族；⚠ **与既有 `solidworks_create_hole_feature` 可能重叠** ⇒ ★ 先核功能再挂 |
| **4.2** | `create_hole_pattern` · `create_semicircular_slot` | 同上 |
| **4.3** | `create_weldment_profile` · `create_structural_member` · `create_cut_list` · `set_cut_list_properties` | ★ 焊件（★ 族覆盖里焊件我们**有**，但只 1 个挂出）|
| **4.4** | `create_profile_center_mate` · `iter_features_recursive` | 焊件配合 + 树遍历 |
| **4.5** | `create_configuration` · `activate_configuration` · `inspect_configurations` · `update_dimension_mm` | ★ 配置族（★ 改尺寸 = 参数化建模的关键）|
| **4.6** | `export_to_step` · `export_to_iges` · `export_to_parasolid` · `export_to_stl` · `export_to_pdf` · `export_to_dxf` · `export_to_bmp` · `export_to_image` · `export_flat_pattern_dxf` | ★★ **9 种导出**（★ 每种的判据都是"文件真的产出了 + 大小 > 0" ⇒ **极好验**）|

---

## 段 5（16–20h）★★★ **5 条 `stitched` 升级** + 修地基

| 批 | 内容 | 为什么 |
|---|---|---|
| **5.1** | `convert_entities` · `sketch_mirror` · `create_sketch_chamfer` ⇒ **`sketch_edit_ops` 升级** | ★★ 它现在 `stitched`（8/10，"选中前置成立，但倒角报错"）⇒ ★ **本会话已把倒角单挂成功**（`specs/137`，正反场景都验过）⇒ **现在有条件升级整条** |
| **5.2** | `insert_gtol` ⇒ **`geometric_tolerance` 升级** | ★ `stitched` 待验 |
| **5.3** | `add_equation` · `list_equations` · `evaluate_equations` · `delete_equation` | 方程族（★ 4 个全未挂；⚠ `delete_equation` 是**删模型内内容**，要单独判断）|
| **5.4** | `create_render_material` · `add_render_material` · `delete_render_material` · `get_extension` | 渲染材质（⚠ 删除类同上）|
| **5.5** | ★ **修地基 D1–D5**（本会话已记录）| 见下 |

**★ 修地基五条（每条都有判据说它该修）**：
```
D1 ★★ 载荷之间**不清选区**没有守卫（specs/140 的 L4）⇒ 工具层自动清或报错，而不是静默累加
D2 ★ 「不 sketch_start 就画几何」**静默**（specs/135）⇒ 画几何前检查活动草图，没有就报错
D3 ★ `mass` 的**物理单位未确证**（事实 167）⇒ 用**已知密度材料**做对照实验（第 12 条套路）
D4 ★ **倒角断言升级**：用四家的 `0.5·w²·L` 断言"倒掉多少体积"（事实 171 的待办）
D5 ★ `_BARE_COORD_NAMES` 漏 `x1/y1/x2/y2`（规则 3 门禁盲区）⇒ 加名字（★ **不放松判据**）
```

---

## 段 6（20–24h）★★ 选择器底座 + 零散模块 + **收敛**

| 批 | 内容 | 为什么 |
|---|---|---|
| **6.1** | `sw_selection_spec` 的 `select_entity_by_index` · `select_object` · `get_selection_count` · `resolve_entity` | ★★ **规则 3 的底座**（★ 本会话多处用到，但底层函数没挂）|
| **6.2** | `sw_review` 的 `collect_geometry_measurements` · `run_review` · `save_preview` · `save_review_previews` · `zoom_to_fit` | ★ 检查/测量族（★ `specs/138` 的 L4 遗留：⑫inspect 还缺这些）|
| **6.3** | `sw_drawing_query` 的 `sheet_names` · `sheet_count` · `current_sheet_name` · `require_drawing` | 工程图读数（★ `specs/132` 只挂了 3 个）|
| **6.4** | 零散：`create_external_spur_gear` · `set_document_appearance` · `resolve_point` · `get_selection_manager` · `iter_features` · `custom_property_count` · `custom_property_manager` · `custom_property_names` · `mass_property_object` · `require_mass_property_document` · `study_options_of` | ★ 各模块的**边界函数**（★ 有些是**内部辅助** ⇒ ★ **要判断"该不该挂"**，不是无脑挂）|
| **6.5** | `iter_feature_tree` · `select_entities_for_mate`（sw_assembly）| 装配辅助 |
| **6.6** | ★★ **收敛**：刷新 `harvest-report` / 审计报告 / `THIRD-PARTY-NOTICES` · 重算 `metrics.md` · ROADMAP 游标汇总 | ★ 24 小时的**交付报告** |

---

## 二、⚠ **不做的**（有据，写清理由）

| 不做 | 理由 |
|---|---|
| ⚠ **曲面族 14 个**（`sw_surface`：loft/sweep/knit/thicken/trim/extend/thick_offset…）| ★★ **事实 40**：`IModeler.Create*Surface` 返回值**跨次都会变**（4 个已 `Obsolete`、`*2` 也回 `None`）⇒ 进去只会得到"**看起来像能跑**"的工具。★ **要做就先修可靠性**（那本身是一整条线）|
| ⚠ **`save_document`**（sw_connect）| ★ **高风险写操作**（保存/另存）⇒ 计划明确的边界 |
| ★ **不搬 343 个名字级缺口** | 你的硬约束④；★ 且要**核功能不核名字** |
| ★ 动画导出 AVI / 模具部分（`stitched` 里环境受限的）| 本机**没有 Motion 加载项**（已在"不做"清单）|
| ★ **不 push** | 你的长期指示；届时**必带 `THIRD-PARTY-NOTICES.md`** |

## 三、每批的收工纪律（与十小时计划同一条，**不改**）

```
① 修 harvest-report 偏离数字 → ② 门禁链 8 条 exit 0 → ③ 全量 pytest 0 failed
→ ④ Spec Kit 五件套（`specs/<NNN>-<slug>/`）→ ⑤ ROADMAP §一 游标 → ⑥ known-facts 一条
→ ⑦ **两仓库各自 commit（不 push）**
★ 编号现场核（下一个从 141 起）· ★ 证据走**工具真实路径**（"能力层能跑"≠"工具能跑"）
```

## 四、★ 判据"**先找后搓**"（`AGENTS.md` §5.0，强制第一步）

```
1. 四家的 live 测试：`Get-ChildItem C:\swprojects\andrewbartels1 -Recurse -Filter 'test_live_*.py'`
   （★ 6 个 live · ~3800 行 / 543 处断言 —— ★ 覆盖倒角/切除/单位/参考点）
2. ★ **再查自己的仓库**（答案常在）：既有 **11 个 `capture_*.py`** + **50 个 `probe_*.py`** +
   `output/` 里 **91 个 json** + `known-facts.md` 172 条 + `capabilities.yaml` 的 `limitations`
   ⇒ ★ 本会话的「插件不在」假象与「漏清选区」**都是没查自己仓库造成的**
3. 都没有 ⇒ 自己搓，并**说明"找过"**
```

## 五、可复用套路（15 条 · 逐批累加）

```
① 先写真机探针答"对象怎么取"（先判断要不要探针）② 先核缺口本身（名字级匹配会骗人）
③ 能力落 scripts/，不改生成物 ④ ★★ 证据走工具真实路径 ⑤ 证据必带负例
⑥ 期望值本身也要被怀疑 ⑦ 长文本进源码立刻 ast.parse（中文内层引号用「」）
⑧ 判据用"行为"不用"类型" ⑨ 可用性看"封送形状" ⑩ 对外名与对内名不同用 param_alias
⑪ "不确定"先核一分钟，别降级为记录 ⑫ 官方没写的语义 ⇒ 设计对照实验
⑬ 行为判据要配"对象归属"判据 ⑭ 判据先去开源项目里找（用户指令）
⑮ 判断"在不在/能不能用"之前，先查项目里有没有查过它
```

## 六、24 小时的**验收**（做完怎么算成）

```
★ 数字（都由生成物现算，不手改）：
   · 工具数 `all_specs()`：83 → **≥ 145**（+62，131 个里的一半）
   · 能力清单：47 → **≥ 75 条**（每批 1 条）
   · `stitched`：**5 → ≤ 2**（★ 升级 3 条：sketch_edit_ops / gtol / 一条环境受限的除外）
   · 覆盖口径 ③「真机碰过」：**1.53% → 上涨**（★ 每批真机验证都新增成员名）
★ 质量（不变）：
   · 每批**两条验收都绿**（① 静态 + 门禁 ② ★ 真机 `verdict: pass`）
   · 全量 pytest **0 failed** · 门禁链 8 条 exit 0
   · ★ **不许有"验不过还留在柜台上"的工具**
```
