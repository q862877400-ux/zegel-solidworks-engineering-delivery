# Tasks · Feature 140 仿真载荷包装层（护城河）

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 先找判据（`AGENTS.md` §5.0 的强制第一步）

- [x] 查四家的 **live 测试**有没有仿真载荷的判据 ⇒ ★ **没有**（三家为"无"）
- [x] 查四家的**工具名** ⇒ 合计 **4 个**，**全是"建研究/跑"**，**没有一个挂载荷/约束**
- [x] ★ 结论：**找过了、没有 ⇒ 自己搓**（★ 且这坐实了"护城河"）

→ 验收: `python tools/measure_simulation_moat.py`（★ 在**代码仓库**里跑）⇒
  ① 段的 `Eduardof0nt` / `Slacker-LLC` / `SolidworksMCP-TS` 三个 owner 都是「（无）」

## T1 · ★★ 核能力层**是不是已是包装层**（目标里那句话）

- [x] `apply_fixed_restraint(study, *, model=None, restraint_type=0)` ⇒ ★ **首参是 `study`** ✓
- [x] `apply_normal_force(study, magnitude, *, model=None, …)` ⇒ ★ 同上 ✓
- [x] ★ 结论：**已是包装层 ⇒ 本特性就是"直接挂"**（不写能力层）

→ 验收: `python -c "import sys;sys.path.insert(0,r'C:\swprojects\sw-skill-fork\scripts');import inspect,sw_simulation as s;print(inspect.signature(s.apply_fixed_restraint))"`
  ⇒ 首参为 `study`

## T2 · ★★★ 核清加载项可达性（★ 差点误判的那一步）

- [x] ⚠ `Dispatch("SldWorks.Simulation")` ⇒ 「找不到指定的模块」（★ **这是假象**）
- [x] ★ 查项目里有没有查过 ⇒ **事实 141/142** + `ensure_simulation_addin`
- [x] `ensure_simulation_addin(sw_app)` ⇒ **CDispatch** ✓ · `get_cosmosworks` ⇒ **CDispatch** ✓

→ 验收: `python -c "…;import sw_simulation as s;print(type(s.ensure_simulation_addin(sw)).__name__)"` ⇒ `CDispatch`

## T3 · 写 `mcp-server/tool_specs_batch26.py`（2 个工具）

- [x] `solidworks_simulation_apply_fixed_restraint` / `_apply_normal_force`
- [x] ★ **三件套组合**：`inject="study"` + `pre_call`（选面）+ `derived_args`（补 `model`）
- [x] `param_alias`：`study_name`/`selection` 标 `None`（★ 与既有 3 个 simulation 工具同一写法）
- [x] ★★ **`magnitude_n` → `magnitude` 的改名映射**（★ 见 D1 —— 第一版漏了）
- [x] ★ 能力层**一行未改**

→ 验收: `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **83**

## T4 · 写**走工具路径**的真机证据

- [x] `tools/capture_simulation_loads_evidence.py`
- [x] ★ 按注册器**同一顺序**走：`inject` → `pre_call` → `derived_args` → 目标函数
- [x] ★ 判据**沿用既有脚本**那条：选区计数 = 1 且 `Count == 2`
- [x] ★ 每次之间 `ClearSelection2(True)`（★ 见 D2 —— 第一版漏了）
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_simulation_loads_evidence.py` ⇒ exit 0，`verdict == "pass"`

## T5 · 另跑既有脚本（能力层整链，作为**对照**）

- [x] `python tools/capture_simulation_evidence.py` ⇒ **PASS**（夹具+载荷 Count=2 ·
      网格 7,310 单元 · Results 非空 · 4 张图）
- [x] ★ 它的作用是**对照**：证明"能力层对"而"声明层可能错"（见 D1）

→ 验收: 该脚本 `verdict == "pass"`

## T6 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计
- [x] 计数守卫同步：`test_server_wiring` 81→**83** · `test_mcp_protocol_layer` 126→**128**
- [x] 无人值守基线：★ **只加 `simulation_loads_wiring` 一条**（不重生成）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 172
- [x] `capabilities.yaml` 加 `simulation_loads_wiring`（level=verified + evidence）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| **D1** | ★★★ **声明层的真 bug**：`magnitude_n` → `magnitude` 的**改名映射我漏了** ⇒ `TypeError: apply_normal_force() got an unexpected keyword argument 'magnitude_n'` | ★ 加 `param_alias={"magnitude_n": "magnitude"}`。★★ **关键**：若证据只直调能力层（像既有脚本那样），**这个 bug 永远不会暴露** —— ★ **因为能力层本身是对的，错的是我新加的声明** ⇒ ★ 这就是**「证据走工具真实路径」**这条纪律的价值 |
| **D2** | ★ **我自己的证据脚本漏了 `ClearSelection2`** ⇒ 夹具那个面仍在选区 ⇒ 第二次回读计数变 **2** ⇒ 判据假红 | ★ 照**既有脚本** L145/L148 补上 ⇒ 1/1 通过。⇒ ★★ **正是用户那条「先找」的纪律** —— 我该先读它而不是自己搓 |
| D3 | ★★ **「插件不在」是假象** | ★ 用项目认定的取法（`ensure_simulation_addin`）⇒ **CDispatch**；记进 spec/plan |
| D4 | ★ 包装形状是**三种机制的组合**（第五种） | ★ 组合既有机制（8 个先例），不新造 |
