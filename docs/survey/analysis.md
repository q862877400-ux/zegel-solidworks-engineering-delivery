# 跨项目对照分析（第一批 13 张卡）

**依据**：业主 2026-10-23 指令 ——「再把多个项目放在一块儿做分类汇总，去分析现在已有的技术路径都是怎么做的」。
**数据来源**：`docs/survey/cards/` 下 13 张逐项目卡片；计数与分类由 `scripts/gen_survey_matrix.py` 从卡片重算，
见 `docs/survey/architecture-matrix.md` 与 `docs/survey/step-matrix.md`（**不手写**）。
**范围**：本批 13 个项目（text-to-CAD 系 + 桥接层 + 多智能体 + 知识型 + 1 个闭源世界模型）。
**未覆盖**：学术序列模型（10 张，R4 进行中）、生成式网格（8 张，R5）、商业产品（13 张，R6）。

---

## 一、五个可测的观察

### 1. 中间表示：**代码**压倒性（9/13）

`docs/survey/step-matrix.md` 的 E2 分布：`code` **9** 家 · `feature-tree` 2 家 · `sequence` 2 家。
- `code`：agentcad · amagine3d · blender-mcp · build123d-mcp · cadam · cadquery-llm-skill · earthtojake-text-to-cad · mcp-cadquery · multi-agent-cad（来源：`docs/survey/architecture-matrix.md`）
- `feature-tree`：freecad-mcp · fusion360-mcp-server（都是**操作宿主软件**的桥，不是从零生成）
- `sequence`：autocad-mcp（AutoLISP 命令）· sky-001（几何状态序列）

★ 观察：**只要目标是「生成一个可编辑的实体」，工程界几乎一致选「让模型写代码」**；选 feature-tree 的都是在改既有模型，选 sequence 的要么是宿主的老命令体系、要么是闭源世界模型。

### 2. 编排：**回环（loop）是工程常态（7/13）**，多智能体是少数派（1/13）

`docs/survey/step-matrix.md` 的 E4/E7 分布：`loop` **7** · `single` 3 · `none` 2 · `multi-agent` 1。
- `loop`：agentcad · amagine3d · blender-mcp · build123d-mcp · cadam · earthtojake-text-to-cad · mcp-cadquery
- `single`：freecad-mcp · fusion360-mcp-server · sky-001（前两家是「等模型再下一条命令」，本身不做自动重试）
- `multi-agent`：multi-agent-cad（唯一一家，且它自己把「省 token」当一等指标）

★ 观察：**「写—执行—读错—重写」是默认形态，不是高级技巧**；多智能体只在有人专门优化 token 时才有意义。

### 3. 验证：**没有任何一家把「可制造性」做成硬门禁**（12/13 都不是）

E6 分布：`visual` **4** · `numeric` **3** · `run-only` **3** · `dfm-rules` **1** · `export-readback` **1** · `none` **1**。
- 唯一的 `dfm-rules`：earthtojake-text-to-cad（它的 `dfm` 技能要求每条结论带**测量证据 + 引用规则**）
- 唯一的 `export-readback`：amagine3d（**只读回导出文件判成败**，`pass=true` 仍只到「待视觉评审」）
- `run-only` 三家（autocad-mcp · build123d-mcp · mcp-cadquery）都**能跑就算过**，其中 mcp-cadquery 连几何门禁都没有

★ 观察：验证手段的分歧最大，而这恰好是「能用 vs 看起来能用」的分水岭。这一条与 `docs/ai-cad-landscape-report.md` §5「全行业没有一家给出可验证的可制造定义」互相印证。

### 4. 交付：**STEP 是硬分界（7/13 有 STEP）**

E8 分布：`STEP` **7** · `none` 3 · `mesh` 2 · `drawing` 1。
- 有 STEP：agentcad · amagine3d · build123d-mcp · earthtojake-text-to-cad · fusion360-mcp-server · mcp-cadquery · multi-agent-cad
- 只有 mesh：blender-mcp · cadam（CADAM 是 OpenSCAD，出 STL/SCAD/DXF）
- 出图：autocad-mcp（DWG/DXF 侧）

★ 观察：**「导出格式里有没有 STEP/IGES」是判定一个工具是工程路线还是外观路线的最快判据**（不需要读代码）。

### 5. 工具粒度：五个真实样本，跨度 66 倍

| 项目 | 工具数 | 来源 |
|---|---|---|
| autocad-mcp | **8** 个工具分派 72 个操作 | `docs/survey/cards/autocad-mcp.md` |
| blender-mcp | **9** 个模型可见（另 5 个 App-only） | `docs/survey/cards/blender-mcp.md` |
| freecad-mcp | **17** 个 | `docs/survey/cards/freecad-mcp.md` |
| fusion360-mcp-server | **93** 个 | `docs/survey/cards/fusion360-mcp-server.md` |
| 本仓库（对照） | **529** 个 | `AGENTS.md` |

★ 观察：**收敛（8–17）与铺开（93）都有人做，但都不走「按 API 成员逐个铺」到 500+ 这条**。AutoCAD 的 8 个工具之所以撑得住 72 个操作，是因为 Python 只做转发、真实现在一层命令表里（`docs/survey/cards/autocad-mcp.md`）。

---

## 二、同一环节的不同做法（每环节至少两个真实样本）

| 环节 | 做法 A | 做法 B | 做法 C |
|---|---|---|---|
| **E1 需求** | 一次提示直出（多数） | 批量追问 + 出站许可（`design_ir.py`，我方） | 规格绑定三层（Amagine3D：不可变 intent / 可变源码 / 场景绑定） |
| **E2 表示** | 代码（9 家，见上） | 特征树（fusion/freecad，改既有模型） | 几何状态序列（sky-001，闭源） |
| **E3 知识** | 指南「唯一真源 + 内容哈希」（agentcad） | 纯提示词资产（cadquery-llm-skill，无执行器） | 技能以 MCP resource 暴露 + 一键装到四家代理（build123d-mcp） |
| **E4 生成** | 单发写脚本 | 多候选择优（CAD-Recode 类，R4 补证） | 多智能体分工（multi-agent-cad） |
| **E6 验证** | 数值增量回带（fusion360：每条改模型命令回带质量/包围盒/体数） | 导出回读（amagine3d：只认重新读回的文件） | DFM 规则 + 证据（text-to-cad） |
| **E7 回环** | 分层 gate + `first_failure`（agentcad） | 双引擎 QA + 独立 Judge + 有界修复（multi-agent-cad） | 视觉自评循环（cadam：七视角拼图回灌模型） |
| **E9 人机** | 变更前审批（fusion360 的 human-approve 语义） | 人只在最终审查（amagine3d 的「待视觉评审」） | 无门禁（多数 run-only 家） |

---

## 三、三条可操作的结论（只从证据推，不写计划）

1. **「表示 = 代码」+「编排 = 回环」+「验证 ≥ 数值」是这批 13 家里能同时满足的最小组合** ——
   9 家选了代码，7 家选了回环；而三样齐全的（agentcad / multi-agent-cad / amagine3d / text-to-cad）
   恰好也是把验证做得最实的那几家（来源：`docs/survey/architecture-matrix.md`）。
2. **验证层级比生成能力更区分产品档次**：同样「能出 STEP」的 7 家里，只有 2 家把验证做成了「不看模型自述」
   （amagine3d 的导出回读、text-to-cad 的 DFM 证据）——这正是 `docs/ai-cad-landscape-report.md` 里
   「假成功」风险的现实对照。
3. **工具粒度的可行区间被 4 个独立样本夹出来了**：8 / 9 / 17 / 93 都成立了，但成立方式全部是
   「工具少 + 一个万能代码口」或「工具多 + 每个都带结构化回读」；没有一家靠「工具多 + 只回 success」成立。

---

## 四、本批尚未覆盖（后续批次补）

| 问题 | 谁来补 |
|---|---|
| 学术序列/DSL 路线（D 类）到底能做到什么程度 | R4（10 张，进行中）|
| 生成式网格（E 类）的真实成熟度与许可 | R5（8 张）|
| 商业产品的工序切分（Zoo / Fusion / Onshape / Creo / Adam / DriveWorks…）| R6（13 张）|
| 「图纸 → 模型」「插画 → 几何」这条空白路 | R6 情报专项 |
| 每个项目的**架构类**是否判对（本批 13 张是 Lead 按卡片内容回填 tag） | R7 收口时逐卡复核 |
