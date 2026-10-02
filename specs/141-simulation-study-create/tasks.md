# Tasks · Feature 141 仿真研究族（建 / 取 / 列）

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ §5.0 先找后搓（**强制第一步**）

- [x] 四家 live 测试 ⇒ **没有**建研究的判据（`andrewbartels1` 0 处，其余三家无）
- [x] ★ **再查自己的仓库** ⇒ ★★ **有**：`tools/capture_simulation_loads_evidence.py:109`
      **已在用** `create_static_study(sw, "DSH-W7")` 且真机跑通
- [x] ★ 结论：**不搓新判据** —— 沿用那条链并**加强**

→ 验收: `python tools/probe_simulation_study_shapes.py`（真机）能跑完并落
  `output/simulation-study-shapes.json`

## T1 · ★★ 核三个函数的**真实形状**（W1 的教训：断言前先知道形状）

- [x] `create_static_study` ⇒ **tuple(3)** `(CDispatch, str, int)`；
      ★ `iter_studies` **从没被任何工具/证据用过** ⇒ 形状未知 ⇒ 必须核
- [x] 实测：`iter_studies` yield **`(index, study)` 元组**（含 COM 对象）
- [x] 实测：`get_study_by_name` 找不到 ⇒ **回 `None`，不抛错**
- [x] 产物 `output/simulation-study-shapes.json`

→ 验收: 证据里 `create_return.entry_name == "CreateNewStudy3"` 且
  `get_study_missing.returns_none == true`

## T2 · 加三个**薄能力层函数**（★ 既有四个一行未改）

- [x] `create_study_report(sw_app, name)` ⇒ `{ok, requested_name, study_name, entry_name, error_code}`
- [x] `list_studies(sw_app)` ⇒ `[{index, name}]`（★ 取不到名字的**也列出**，不跳过）
- [x] `find_study(sw_app, name)` ⇒ `{found, requested_name, study_name}`
- [x] 更新 `__all__`

→ 验收: `python -c "import sys;sys.path.insert(0,r'C:\swprojects\sw-skill-fork\scripts');import sw_simulation as s;print(all(n in s.__all__ for n in ('create_study_report','list_studies','find_study')))"`
  ⇒ `True`

## T3 · 写 `mcp-server/tool_specs_batch27.py`（3 个工具）

- [x] `solidworks_simulation_create_study` / `_list_studies` / `_find_study`（都 `inject="sw_app"`）
- [x] ★ **`param_alias={"study_name": "name"}`**（★ 见 D1 —— 第一版**漏了**）
- [x] ★ 说明里写明：`entry_name` 的语义（空 ⇒ 没建成）· **只支持静力学** · `found` 的语义

→ 验收: `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **86**

## T4 · ★★ 加**参数绑定门禁** `scripts/check_param_binding.py`（**本批的额外产出**）

- [x] 判据三条：① 声明名 ∈ 形参 或 ∈ `param_alias` ② `param_alias` 目标名存在 ③ `inject` ∈ `RESOLVERS`
- [x] 接进 `release_check.py`（`_run_param_binding_gate` + `_gate_results`）
- [x] ★ 登记 `docs/gate-classification.json`（`kind: hard`）
- [x] ★★ **用负例证明它抓得住**（临时摘掉 `param_alias` ⇒ exit 1 且精确指出参数名）

→ 验收: `python scripts/check_param_binding.py` ⇒ exit 0，且**负例时 exit 1**（两条都要跑）

## T5 · 写真机证据（**走工具真实路径**）

- [x] `tools/capture_simulation_study_evidence.py` —— ★ 四条断言：
      `entry_name` 非空 · 建完回读名字逐字相等 · 列出含该名字 · 负例 `found` 为假
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_simulation_study_evidence.py` ⇒ exit 0，`verdict == "pass"`

## T6 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计（★ **顺序**：能力清单改完**再**跑生成器）
- [x] 计数守卫同步：`test_server_wiring` 83→**86** · `test_mcp_protocol_layer` 128→**131**
- [x] 无人值守基线：★ **只加 `simulation_study_create` 一条**（不重生成）
- [x] ★ **`docs/signature-audit.md`**：`sw_simulation.py` 调用点 **47 → 50**（★ 加了 3 个函数 ⇒ 门禁抓到并给了修法）
- [x] 门禁链 exit 0（★ 现在 **18 道**）· 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 173
- [x] `capabilities.yaml` 加 `simulation_study_create`
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| **D1** | ★★★ **又是漏写 `param_alias`**：能力层形参 `name`，我对外声明 `study_name` ⇒ 真机 `TypeError`（★ 与 W7 的 `magnitude_n` **同一族**） | 修 + ★★ **加门禁 `check_param_binding.py`**（**用负例证明它抓得住**）。★ 定则：**"记下来"不等于"下次不犯"** —— 要**机器化** |
| D2 | ★ `iter_studies` **从没被用过** ⇒ 形状未知 | ★ **T1 先核**（yield `(index, study)` 元组，含对象 ⇒ 不可直接挂）|
| D3 | ★ `get_study_by_name` 找不到**回 None 不抛错** | ★ 对外用**显式 `found`** 字段（避免把"没有"当"有"）|
| D4 | ★ 收工脚本又中**事实 48**（内层直引号） | 修。★ 这已是本会话**第 N 次** ⇒ ★ **是否也该给它加门禁？**（★ 记为待办，见 L4）|
| D5 | ★ 生成器**顺序**错了（先跑 `gen_level_audit` 再加能力） | ★ 重跑即可；★ 记：**能力清单是上游，依赖它的生成器要后跑** |
| D6 | ★ `docs/signature-audit.md` **两张表**都写了 `sw_simulation.py`（6 列 / 5 列） | ★ **两处都改**（量的是同一模块）|
