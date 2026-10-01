# Tasks · Feature 137 倒角 / 圆角

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 设计对照实验（本批的核心未知）

- [x] 官方 Remarks 只说 "edge chamfers"，**没说"哪些边"** ⇒ ★ **不假设**
- [x] 证据脚本里加**对照**：「选中 `index:0`」vs「**清空选区**」⇒ 看结果是否不同
- [x] ★ 并规定：**若相同 ⇒ 本批设计是假设计，必须改**（不许把假设计当成功）

→ 验收: `output/chamfer-fillet-evidence.json` 里有 `control_no_selection` 这一项

## T1 · 核 selection 机制与可用读数（不猜）

- [x] `sw_selection_spec.resolve_selection(model, selector, kind, *, body_index=0)` ✓
- [x] `ENTITY_KINDS = ('EDGE', 'FACE')` ✓
- [x] ★ 核"能断言什么"：**没有**体积/质量属性工具 ⇒ 用**特征树计数 + 特征名**
- [x] ★ 并查清**包围盒不能用**（倒角不改变最大坐标）

→ 验收: `python -c "import sys;sys.path.insert(0,r'C:\swprojects\sw-skill-fork\scripts');import inspect,sw_selection_spec as s;print(inspect.signature(s.resolve_selection), s.ENTITY_KINDS)"`

## T2 · 写 `mcp-server/tool_specs_batch23.py`（2 个工具）

- [x] `solidworks_chamfer` / `solidworks_fillet`
- [x] ★ `pre_call = _select_edge`（复用 `batch4` 的 `resolve_selection` 逻辑）
- [x] `param_alias`：`selection` → `None`（由 `pre_call` 消费）+ `distance_mm`→`distance` / `radius_mm`→`radius`
- [x] ★ **能力层一行未改**（形态已验证是对的）

→ 验收: `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **77**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

→ 验收: 同 T2（77 而不是 75）

## T4 · 写真机证据 `tools/capture_chamfer_fillet_evidence.py`

- [x] 核 2 个声明解析得到 **且都有 `pre_call`**
- [x] ★★ 走**工具真实路径**（`spec.pre_call(_P(selection))` 再调目标函数）
- [x] 倒角 ⇒ 特征「倒角1」（19→20）· 圆角 ⇒ 特征「圆角1」（→21）
- [x] ★★ **对照实验**：清空选区 ⇒ 记录结果（与"选中"对比）
- [x] **负例**：`index:9999` ⇒ 必须报错
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_chamfer_fillet_evidence.py` ⇒ exit 0，`verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计
- [x] 计数守卫同步：`test_server_wiring` 75→**77** · `test_mcp_protocol_layer` 120→**122**
- [x] 无人值守基线：★ **只加一条**（不重生成）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 165
- [x] `capabilities.yaml` 加 `chamfer_fillet_on_selection`
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★★ **对照实验的结论**：清空选区 ⇒ 特征数**不变**（21→21）⇒ 证实设计成立；⚠ **但不抛错**（静默） | 记进 capability 的 `limitations`；★ **不假称有守卫** |
| D2 | ★ 证据脚本里 `new_names`（**特征树列表差集**）**不可靠** —— 一度显示 `["凸台-拉伸1"]`（那是**基体**的名字） | ★ 断言改用**计数** + **返回对象的名字**；差集字段保留但**标注不可靠** |
| D3 | ⚠ 又是**事实 48**（收工脚本里 `"清空选区"` 用了直引号） | 改「」；★ 本会话已第 N 次 ⇒ 写含中文的字面量时**内层一律用「」** |
| D4 | ★ 本批是第一**次用 `pre_call` 驱动建特征** | 复用 `batch4` 的既有机制，**不新造** |
