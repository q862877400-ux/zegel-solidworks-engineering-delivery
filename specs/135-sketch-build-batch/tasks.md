# Tasks · Feature 135 建草图 + 画几何

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 核"要不要探针"这一步（结论：**不需要**，理由要写）

- [x] 查证：`start_sketch` / `sketch_line` / `sketch_circle` / `end_sketch` **已在 W1/W2/W3 的
      证据脚本里真机跑过**（每次都成功）⇒ ★ 探针那一步**已被既有证据覆盖**
- [x] ★ 但把**行为上的未知**（不 start 就画线 / 坏面名）放进证据脚本，**如实记录、不断言**

→ 验收: `output/sketch-build-evidence.json` 里有 `record_draw_without_start` 与 `record_bad_plane` 两条记录

## T1 · 核要挂的四个函数的语义（不猜）

- [x] `start_sketch(model, plane_name='Front Plane')` —— 中英文面名都支持
- [x] `end_sketch(model)` —— 返回可复用草图引用（可传给 `extrude_boss`）
- [x] `sketch_line` / `sketch_circle` / `sketch_corner_rectangle` —— ★ docstring **明写单位毫米**
- [x] 确认 `sw_part` 的模块单位是**毫米**（事实 73）⇒ **不做换算**

→ 验收: `python -c "import sys;sys.path.insert(0,'scripts');import inspect,sw_part as p;print(inspect.signature(p.sketch_line))"`
  ⇒ 输出含 `(model, x1, y1, x2, y2)`

## T2 · 写 `mcp-server/tool_specs_batch21.py`（5 个工具）

- [x] `solidworks_sketch_start` / `_end` / `_add_line` / `_add_circle` / `_add_rectangle`
- [x] ★ **参数用语义名 + `_mm`**（`start_x_mm` 等），由 `param_alias` 映射到能力层的 `x1`
      —— ★ **能力层一行不改**（改形参名会动到既有调用点）
- [x] ★ **只挂对角矩形**（中心那个语义重叠 ⇒ 不挂，免得 AI 选错）
- [x] 每个工具的说明里注明**规则 3 的豁免依据**（画几何必须给平面内坐标）

→ 验收: `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **72**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

- [x] 加 `"tool_specs_batch21"` 并注明"补最底层短板"

→ 验收: 同 T2（72 而不是 67）

## T4 · 写真机证据 `tools/capture_sketch_build_evidence.py` —— ★ **读写配对**

- [x] ★ 核 5 个声明的 `module`/`function` 解析得到，**并把每个的 `param_alias` 记进证据**
- [x] ★★ **读写配对**：start → 画线 ⇒ `count_lines==1` → 画圆 ⇒ `count_arcs==1` →
      画矩形 ⇒ `count_lines==5` → end ⇒ **仍读到 5**
- [x] ★ **记录（不断言）**两条未知：不 start 就画线 / 坏基准面名
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_sketch_build_evidence.py` ⇒ exit 0，`output/sketch-build-evidence.json` 的 `verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计（都新增了公开函数 / 能力条目）
- [x] 计数守卫同步：`test_server_wiring` 67→**72** · `test_mcp_protocol_layer` 112→**117**
- [x] 无人值守基线：★ **只加 `sketch_build` 一条**（不重生成）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 163
- [x] `capabilities.yaml` 加 `sketch_build`（level=verified + evidence，★ 含**静默行为的限制**）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★ **Spec Kit 编号 134 已被占**（`134-static-simulation-reverified` 是已提交特性）| 按 flow-forward **顺移为 135**；★ 并把 W5–W7 一并顺移（计划里写明原因） |
| D2 | `Param` **没有** `exclusive_minimum` 字段（我第一版写了） | 去掉；`Param` 只有 `name/kind/default/description/required` |
| D3 | ★ **不 start 就画几何是静默的**（真机实测） | ★ **如实记录**，写进 capability 的 `limitations`；**不假称有守卫** |
| D4 | 坏基准面名 ⇒ **ValueError**（这条是好的） | 记录；说明"选不中就报错"这条纪律在本族成立 |
| D5 | ★ 门禁只看参数字面名 ⇒ `x1/y1` 溜过去 | ★ **不改门禁**（不为通过而放宽判据）；记进 known-facts，**留后续单独开特性** |
