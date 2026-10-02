# Tasks · Feature 136 拉伸族

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T1 · 核要挂的三个函数的语义与依赖（不猜）

- [x] `extrude_boss(model, sketch_name, depth, direction=True, merge=True)` —— depth **毫米**
- [x] `extrude_cut(model, sketch_name, depth, direction=True, flip=False)` —— depth **毫米**，
      ★ **0 = 完全贯穿**
- [x] `extrude_midplane(model, sketch_name, total_depth)` —— **总深**（每侧一半）
- [x] 确认三个都**只要草图名、不需要"选择"** ⇒ 证据脚本能干净地写

→ 验收: `python -c "import sys;sys.path.insert(0,'scripts');import inspect,sw_part as p;print(inspect.signature(p.extrude_boss))"`
  ⇒ 输出 `(model, sketch_name, depth, direction=True, merge=True)`

## T1b · ★ 核 `chamfer` 能不能进本批（结论：形态对，但**本批不做**）

- [x] 按铁律 4 核 `InsertFeatureChamfer` 的签名与枚举
- [x] `swChamferType_e.swChamferAngleDistance = 1`（swapi 与反射**两源一致**）
- [x] 实现传 `(4, 1, distance, angle_rad, …)` ⇒ 与官方说明**一致** ✓
- [x] ★ 但**没有 `edges` 参数** ⇒ 需要 `selection` 包装层 ⇒ **单独一批**

→ 验收: `Get-Content 'C:\swapi\enums\swChamferType_e.md'` 里 `swChamferAngleDistance | 1`

## T2 · 写 `mcp-server/tool_specs_batch22.py`（3 个工具）

- [x] `solidworks_extrude_boss` / `_cut` / `_midplane`
- [x] `param_alias` 把 `depth_mm`→`depth`、`total_depth_mm`→`total_depth`（★ 能力层**一行未改**）
- [x] 工具说明写明：**0 = 完全贯穿** / 中面是**总深** / 需要**已存在的草图** / 切除的正确入口

→ 验收: `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **75**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

- [x] 加 `"tool_specs_batch22"` 并注明"第一批能建实体"

→ 验收: 同 T2（75 而不是 72）

## T4 · 写真机证据 `tools/capture_feature_build_evidence.py`

- [x] ★ 核 3 个声明解析得到 + **把 `param_alias` 记进证据**
- [x] ★★ **数字断言**：矩形 40×20 拉伸 10 ⇒ `size == [40.0, 20.0, 10.0]`
- [x] 切除 `depth_mm=0` ⇒ 特征树**多一个特征**（19 → 21）
- [x] 中面拉伸总深 10 ⇒ `size == [40,20,10]` 且 **min/max = ±5**（两侧对称）
- [x] **负例**：不存在的草图名 ⇒ **报错**
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_feature_build_evidence.py` ⇒ exit 0，`output/feature-build-evidence.json` 的 `verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计
- [x] 计数守卫同步：`test_server_wiring` 72→**75** · `test_mcp_protocol_layer` 117→**120**
- [x] 无人值守基线：★ **只加 `feature_build_extrude` 一条**（不重生成）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 164
- [x] `capabilities.yaml` 加 `feature_build_extrude`（level=verified + evidence）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★ 证据脚本**第一版选择"只记录不断言"**（理由：包围盒返回结构未核） | ★ 核了 docstring ⇒ 结构**明确写着** ⇒ **改回真断言**。★ 定则：**"不确定就不敢断言"是对的，但"不确定"要先花一分钟去核，而不是直接降级为记录** |
| D2 | ⚠ 证据脚本又中**事实 48**（`"多了一个特征"` 内层直引号） | 改「」；★ 这已是本会话第 N 次 ⇒ 写含中文的字面量时**内层一律用「」** |
| D3 | `Param` **没有** `exclusive_minimum`（W4 也踩过） | 只用 `name/kind/default/description/required` |
| D4 | ★ `chamfer` 的形态核了但**没进本批** | ★ 核对产物是"**不做它的理由**"，下一批直接用（见 `plan.md` 第二节）|
