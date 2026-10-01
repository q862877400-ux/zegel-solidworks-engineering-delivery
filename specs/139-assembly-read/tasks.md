# Tasks · Feature 139 装配只读

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 核缺口本身（21 个名字逐个核，不照数字排活）

- [x] 分出**已有工具**（`add_component` / `add_*_mate` / `collect_assembly_bom` / `pack_and_go`）
- [x] 查出**已实现、可注入、没挂**的只读函数三个
- [x] ★ 顺带查出**注入名的限制**（见 T1）

→ 验收: 三个函数都能 `getattr` 到且签名首参是 `asm_model`/`model`

## T1 · ★★ 给 `RESOLVERS` 加 `asm_model`（事实 169 的解法）

- [x] 核清：`make_tool_function` **没把 `inject_as` 传下去** ⇒ 注入名 = `inject` 的字面值
- [x] 而 `inject` 只能是 `RESOLVERS` 的键（`{"model","sw_app","study"}`）
- [x] ★ 加 `"asm_model": resolve_model`（★ 不动 `tool_registry`）

→ 验收: `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(sorted(rc.RESOLVERS))"`
  ⇒ 含 `'asm_model'`

## T2 · 写 `mcp-server/tool_specs_batch25.py`（3 个只读工具）

- [x] `solidworks_assembly_list_components`（`inject="asm_model"`）
- [x] `solidworks_assembly_list_mates`（`inject="model"`）
- [x] `solidworks_assembly_check_interference`（`inject="asm_model"`）
- [x] ★ 说明里**明写三态语义**（`pass`/`warn`/**`blocked` = 检查失败**，不可读成"无干涉"）

→ 验收: `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **81**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

→ 验收: 同 T2（81 而不是 78）

## T4 · 写真机证据 `tools/capture_assembly_evidence.py` —— ★ **一正一反**

- [x] 核 3 个声明解析得到 + **记下 `inject` 名**
- [x] 造**临时夹具零件**（40×20×10）存 `output/_fixtures/`（★ 证据里写明"不碰用户目录"）
- [x] ★ **重叠场景**（两次都插在 z=0）⇒ 断言 `count >= 1`
- [x] ★ **分开场景**（z=0 与 z=60）⇒ 断言 `count == 0` 且 `status == "pass"`
- [x] ★★ **判读**：两个场景的数**不同** ⇒ `discriminates.ok`
- [x] 安全：`CommandInProgress` + 关件不保存

→ 验收: `python tools/capture_assembly_evidence.py` ⇒ exit 0，`verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计
- [x] 计数守卫同步：`test_server_wiring` 78→**81** · `test_mcp_protocol_layer` 123→**126**
- [x] 无人值守基线：★ **只加 `assembly_read` 一条**（不重生成）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 171
- [x] `capabilities.yaml` 加 `assembly_read`（level=verified + evidence）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★★ **注入名只能是 `RESOLVERS` 的键** ⇒ 首参叫 `asm_model` 的函数挂不上 | ★ 给表**加一行**（表的设计用途）；记进 **known-facts 169** |
| D2 | ★★★ 干涉检查**修过三处成员名却从没验过** | ★ 本批设计**一正一反** ⇒ **首次真机验证通过**（重叠 1 / 分开 0）|
| D3 | ⚠ 收工脚本又中**事实 48**（`不判"装对了没有"` 内层直引号） | 改「」；★ 这已是本会话**第 N 次** ⇒ 本条纪律要更强 |
| D4 | ★★ **用户当面指出**：判据该先找开源的 | ★ 已落成纪律（见 known-facts 170/171 与 `AGENTS.md`）|
