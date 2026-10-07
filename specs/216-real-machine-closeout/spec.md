# 规格 216 · 真机收口（台账订正 · 预选族 9 条 · AVI 边界）

> **来源（铁律 1 的四种合法来源）**：
> ① **用户授权**（2026-10-07）：「**第 3 点我允许你开，我从没说过不准开啊，纪律是开了用完要关**」✓
> ② **本仓实测读数**（同一轮）：`python tools/sw_guard.py --timeout 600 -- python tools/verify_costing_e2e.py`
>    ⇒ ★ **`verdict: pass`** · `assertions` **3/3** · `solidworks_revision` 修前 `''` / 修后 **`'34.4.1'`** ✓
> ③ **本仓既有文档**：`capabilities.yaml` 的 `costing` 条目（★ 其 2026-10-04 那段已被本轮推翻）、
>    `docs/preselect-family-baseline.json`（14 条分类）、`scripts/sw_motion.py` 的 AVI 来源块 ✓
> ④ **本项目既有模式**：★ `specs/202-user-coverage-gaps/recon/` 的「先分诊 → 再动手 → 再门禁化」工法 ✓

## 一、要解决什么

★ 三件**只剩真机才能收口**的事；★ 而本轮实测先**推翻了其中两件的原前提**（★ 订正记在 goal-bar）：

| # | 项 | ★ 原以为 | ★ 实测 |
|---|---|---|---|
| **③** | `costing` | 台账写「`verdict: partial`（5/6），卡在 `list_templates`」 | ★ **`verdict: pass`** · 断言 **3/3** · `templates` 步拿到真路径 ⇒ **旧阻塞点不复现** ✓ |
| **②** | `animation_export`（AVI） | 我写「根因是缺 Motion 加载项」 | ★ **台账 2026-10-01 就已订正过这句**（L1611 逐字「原写…而实测那条**不成立**」）；★ 真结论是 L1619：**`SaveToAVI` 需要 `CosmosMotion` 类算例、本机拿不到** ✓ |
| **①** | 14 条预选族 | 需要真机 + `pre_call` | ★ 待做（本规格的**主要工作量**）✓ |

★ 另发现**一个真缺陷**（③ 顺带）：`connect_solidworks` 的 `metadata` **从来没有 `revision` 键**，
★ 而 `tools/verify_costing_e2e.py` 读的正是它 ⇒ ★ 证据文件 `solidworks_revision` **恒为空串** ✗

## 二、本规格做什么

### ① 订正台账（本轮已完成）
★ `capabilities.yaml` **两处**：`costing`（`limitations` 加 4 条 · `evidence` 改判据命令与读数）·
`costing_readback`（`limitations` 加 1 条）—— ★ **一律"追加 + 标注旧条作废"，不删历史** ✓
★ 同步修**真缺陷**：`scripts/sw_connect.py` 复用既有 `get_sw_version()` 补 `revision`（★ 防御式：
取版本失败记 `None`、不拖垮连接）；`tools/verify_costing_e2e.py` 加 `or ""`（★ 免得写成字符串 `None`）✓

### ② 9 条预选族工具加 `pre_call`（★ 本规格主要工作量）
★ 依据 **事实 503**：调用序 = 注入解析器 → `pre_call` → `derived_args` → 目标函数，
★ 而 `RESOLVERS[inj]` **会清空选区** ⇒ ★ 选区**必须**由 `pre_call` 在注入**之后**重建 ✓
★ 形状照 `mcp-server/tool_specs_batch74.py` 的 `_select_faces_for` ✓
★ 逐条真机验证「选区建起来 + 特征真建成」；★「显式拒」3 条与「诊断型」2 条**不动**，但要复核结论仍成立 ✓

### ③ AVI：在两条路之间做**有依据的取舍**并落档
★ (a) 设法拿到 `CosmosMotion` 类算例 · ★ (b) 如实记为**已定位边界**的能力缺口 ✓
★ 判据固定为「**文件存在且大小 > 0**」—— ★ **不看返回值**（★ 返回码会撒谎：不 `Calculate` ⇒ 返 `True` 而 0 字节）✓

## 三、本规格**不做**什么
- ★ **不改 `specs/214` / `215`**（★ 已提交 ⇒ 按 Flow-forward 不动；★ 本轮纪律订正写在本规格）✗
- ★ **不重写历史**：★ 台账与 ROADMAP 里**旧轮次**的记录保持原样（★ 只订正**现状含义**）✗
- ★ **不裸跑真机**：★ 一律 `tools/sw_guard.py`（弹窗护栏 + 硬超时）✗
- ★ **不为凑数改已经对的**（★ 同规格 215 的纪律）✗

## 四、硬约束
1. ★★ **真机用完必须关**（★ 用户订正的原话）；★ 每批收尾走 `round_chain`（第④步就会关）✓
2. ★ **台账只追加、不删历史**；★ 每处订正写明**依据与日期** ✓
3. ★ **判据必须真机复跑过**才写进台账（★ 不许拿"期望"当"现状"—— 台账 L1564 那条教训逐字）✓
4. ★ 按路径提交 `python tools/commit_mine.py`；★ 索引复位为 0 后才能提交 ✓

## 五、验收判据

| # | 判据 | 怎么验 |
|---|---|---|
| **C1** | ★ 台账两处已订正且门禁绿 | `python scripts/check_union_conventions.py` ⇒ 退出 0 |
| **C2** | ★ `revision` 缺陷已修且**真机证明** | `output/costing-evidence.json` 的 `solidworks_revision` = `34.4.1`（★ 修前是空串）|
| **C3** | ★ 9 条预选族各带 `pre_call` | `python scripts/check_preselect_family.py` ⇒ 退出 0，★ 且未登记的新增为 0 |
| **C4** | ★ AVI 取舍已落档 | `capabilities.yaml` 的 `animation_export` 条目含本轮结论与三条实测事实 |
| **C5** | ★ 收尾链 + 按路径提交 | `pwsh tools/round_chain.ps1` ⇒ 首轮 OK；★ 索引 0 |
