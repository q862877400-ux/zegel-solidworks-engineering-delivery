# 十小时计划之后 —— 后续计划（`plan-next.md`）

> 本文件**不写进度**（宪法：进度在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> 它写的是**队列、判据与理由**。★ 每次开批前**现场核编号**（计划里**不写死** —— 见下）。

## 〇、先厘清两个数 —— 它们**不是同一件事**

```
★ ① **能力层里已实现、可注入、却还没挂** = **131 个**      ← ★ **「我们自己的缺口」**
     （本会话现算：首参 ∈ {model, sw_app, study} 且不在 `all_specs()` 里）
★ ② **⑯ 域名字级缺口** = **343 个**                        ← ★ 大部分是**名字差异**或**别家独有**
⇒ ★★ 用户硬约束④：「**不搬别家那 336 个"缺口"（先挂自己的）**」
⇒ **后续计划的主体是 ①，不是 ②。** ② 只在"①做完了还有余力"时按名字逐条核。
★ 已核实：② 里的名字有相当一部分我们**功能上已有**（如 `bbox` = `solidworks_part_bounding_box`）——
  ★ **要核功能，不要核名字**（事实 166 的做法）。
```

## 一、优先级判据（按这个顺序，不按数字大小）

| 序 | 判据 | 为什么 |
|---|---|---|
| 1 | ★★ **护城河域优先** | 目标明写"建护城河"；四家在那些域是空的 ⇒ 每一步都是**净增** |
| 2 | ★★ **能真机验的优先** | 核心判据是「A 挂工具 与 B 真机验证**必须配对**」⇒ 验不了的批**不许上柜台** |
| 3 | ★ **有现成判据的优先** | 按 `AGENTS.md` §5.0：**先去开源/自己仓库里找判据**（本会话已有 15 条套路 + 四家 live 测试） |
| 4 | ★ 前置先做 | 有依赖的批要排在前面（如"建研究"必须早于"跑分析"） |
| 5 | ⚠ **避开已知不可靠的** | 如事实 40（`IModeler.Create*Surface` 返回值不可靠）⇒ 曲面批**要么先修可靠性，要么跳过** |

---

## 二、四条线（建议按此顺序推进）

### ★★★ 线 A · 仿真闭环补全（**护城河**，21 个未挂）

**为什么第一优先**：W7 只做到"**能加载荷**"；而 `sw_simulation` + `sw_simulation_study` 还躺着 **21 个**
⇒ ★ **把它们挂上，W7 才从"能加载荷"变成"能跑完并读数"** —— 那是**完整的仿真闭环**，也是护城河的实体。

| 批次 | 候选函数（能力层已有） | 为什么这一批 |
|---|---|---|
| **第 1 批** | `create_static_study` · `get_study_by_name` · `iter_studies` · `get_study_manager` | ★★ **W7 的 L1 遗留**（"没有建研究工具"⇒ `study_name` 只能引用已存在的）⇒ **它是最硬的前置** |
| **第 2 批** | `create_mesh` · `default_element_size_and_tolerance` · `run_analysis` · `collect_study_evidence` | ★★ **闭环的后半段**（网格 → 跑 → 读数）|
| **第 3 批** | `sw_simulation_study.export_study` · `get_results_of` · `mesh_and_run` | 研究级封装（★ 有 `mesh_and_run` 就可能一步到位）|
| **第 4 批** | `sw_simulation_loads` 剩的 **26 个**（压力/扭矩/重力/离心/轴承/远程载荷/12 种连接器）| ★ 载荷族的广度（★ 护城河越宽越好）|

**验收（现成，不用新造）**：`tools/capture_simulation_evidence.py` 的判据三条 ——
```
| 夹具/载荷 | 选区计数 = 1 **且** Count = 2 |
| 网格     | CreateMesh 返回 0 **且** ElementCount 是小的正整数 |
| 求解     | ★ **不是** RunAnalysis 的返回码，而是 study.Results 非空 + GetPlotCount > 0 |
```
★ **可直接扩展它**：建研究 → 加载荷 → 网格 → 跑 → 断言 `GetPlotCount == 4`（已知基线）。

**⚠ 风险**：`ensure_simulation_addin` 走 `LoadAddIn` 真路径（★ 本会话已验证 ⇒ **不是许可问题**）。

---

### ★★★ 线 B · 拓扑优化挂柜台（**护城河**，6 个未挂）

**为什么**：hindsight 记忆里 **A9 已达标**（拓扑优化核心闭环有可跑实现）⇒ ★ **这批就是"把它挂到 MCP"**。

| 批次 | 候选函数 | 备注 |
|---|---|---|
| **B1** | `collect_topology_numbers` · `get_topology_study_manager` · `list_topology_constraints_and_controls` | ★ **只读**，风险最低 ⇒ **先挂这批** |
| **B2** | `set_topology_goal` · `set_topology_iteration_options` · `get_topology_study_options` | 写操作（★ 改研究参数）|

**已有工具（不必重复挂）**：`solidworks_topology_create_study` / `_run` / `_evidence` /
`create_mass_constraint` / `create_stress_constraint` / `create_factor_of_safety` /
`create_thickness_control` / `create_symmetry_control` / `create_preserved_region` / `create_demold_control`
⇒ ★ **本批只补"读数/参数"那一环**。

---

### ★★ 线 C · 建模闭环补全（`sw_part` 的 17 个 · 非护城河但**最能被 AI 直接用**）

**为什么**：本会话已接通「建草图 → 画几何 → 拉伸 → 倒角」⇒ ★ **这批是它的自然延伸**，
而**验证方式现成**（★ W4 续 那套**包围盒数字断言**：40×20×10）。

| 批次 | 候选 | 判据（可直接复用）|
|---|---|---|
| **C1** | `sketch_rectangle` · `sketch_polygon` · `sketch_slot` · `sketch_ellipse` · `sketch_arc` · `sketch_centerline` · `sketch_spline` | ★ 与 batch21 同型（画几何 + `count_lines`/`count_arcs` 回读断言）|
| **C2** | `add_dimension` · `auto_dimension_sketch` | 尺寸（★ 回读尺寸值断言）|
| **C3** | `linear_pattern` · `shell` · `rib` · `insert_dome` · `insert_composite_curve` · **`hole_wizard`** | ★ **建特征** ⇒ **包围盒/特征树数字断言**；⚠ `hole_wizard` 参数多（既有 `create_hole_feature` 已挂 5 种孔）|

---

### ★★ 线 D · 修地基（补本会话**已发现、已记录**的守卫缺口）

**为什么**：这些是**我自己查出来的洞**，而且**每一条都有明确的判据说它该修**。

| # | 缺口 | 出处 | 建议判据 |
|---|---|---|---|
| **D1** | ★★ **「每次载荷之间要清空选区」没有守卫** | `specs/140` 的 L4 | 工具层加载荷前自动 `ClearSelection2`，或**报错**而不是静默累加 |
| **D2** | ★ **「不 `sketch_start` 就画几何」静默** | `specs/135` 的未知项 | 画几何前检查活动草图，没有就**报错** |
| **D3** | ★ **`mass` 的物理单位未确证** | 事实 167 · `specs/138` L1 | 用一个**已知密度的材料**做对照实验（★ 按第 12 条套路）|
| **D4** | ★ **倒角断言可用四家的体积公式升级** | 事实 171 的待办 | 用 `test_live_sw_add_chamfer_tool.py` 的 `0.5·w²·L` 断言"倒掉多少体积"（★ 从"多了一个特征"升级）|
| **D5** | ★ `_BARE_COORD_NAMES` 漏 `x1/y1/x2/y2` | 本会话记录 | 规则 3 的门禁盲区（★ **不放松判据**，加名字）|

---

## 三、不做的（有据，写清理由）

| 不做 | 理由 |
|---|---|
| ★ **不搬 ② 那 343 个别家缺口** | 用户硬约束④；且大部分是**名字差异** |
| ⚠ **曲面族（`sw_surface` 14 个）暂缓** | ★ **事实 40**：`IModeler.Create*Surface` 返回值**跨次都会变**（4 个已 `Obsolete`、`*2` 也返回 `None`）⇒ ★ **先进去会得到"看起来像能跑"的工具** ⇒ **要么先修可靠性，要么跳过** |
| ★ **不做高风险写操作** | 计划明确的边界（保存/另存/删除）|
| ★ **不 push** | 用户长期指示（P8 推迟）⇒ 仅在明确批准后，且**必带 `THIRD-PARTY-NOTICES.md`** |

---

## 四、每批的收工纪律（与十小时计划同一条，不改）

```
① 修 harvest-report 偏离数字 → ② 门禁链 8 条 exit 0 → ③ 全量 pytest 0 failed
→ ④ Spec Kit 五件套（`specs/<NNN>-<slug>/`）→ ⑤ ROADMAP §一 游标
→ ⑥ known-facts 一条 → ⑦ **两仓库各自 commit（不 push）**
★ 编号：**现场核下一个空闲号**（本会话已顺移三次 —— 因为一个 W 会拆成多个特性）⇒ **计划里不写死**
★ 已用号：… 131 132 133 134 135 136 137 138 139 140 ⇒ 下一个从 **141** 起核
```

## 五、判据"先找后搓"（`AGENTS.md` §5.0，强制第一步）

```
★ 写任何探针/证据之前：
  1. 先查四家的 live 测试：`Get-ChildItem C:\swprojects\andrewbartels1 -Recurse -Filter 'test_live_*.py'`
     （★ 6 个 live · ~3800 行 / 543 处断言）
  2. ★ **再查自己的仓库**（答案常在）：既有 `tools/capture_*.py`、`docs/known-facts.md` 的 172 条、
     `capabilities.yaml` 的 `limitations`
     ⇒ ★ 本会话的「插件不在」假象与「漏清选区」**都是没查自己仓库造成的**
  3. 都没有 ⇒ 自己搓，并**说明"找过"**
```

## 六、可复用套路（15 条，逐批累加）

```
① 先写真机探针答"对象怎么取"（但先判断要不要探针）② 先核缺口本身（名字级匹配会骗人）
③ 能力落 scripts/，不改生成物 ④ ★★ **证据走工具真实路径**（"能力层能跑"≠"工具能跑"）
⑤ 证据必带负例 ⑥ 期望值本身也要被怀疑 ⑦ 长文本进源码立刻 ast.parse（中文内层引号用「」）
⑧ 判据用"行为"不用"类型" ⑨ 可用性看"封送形状"不看"代数新旧"
⑩ 对外名与对内名不同时用 param_alias ⑪ "不确定"先核一分钟，别降级为记录
⑫ 官方没写的语义 ⇒ 设计**对照实验**（事先规定"若两种情况相同即设计错了"）
⑬ 行为判据要配"对象归属"判据 ⑭ ★ **判据先去开源项目里找**（用户指令）
⑮ ★ **判断"在不在/能不能用"之前，先查项目里有没有查过它**
```
