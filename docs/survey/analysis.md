# 跨项目对照分析（**42 张卡**）

**依据**：业主 2026-10-23 指令 ——「再把多个项目放在一块儿做分类汇总，去分析现在已有的技术路径都是怎么做的」。
**数据来源**：`docs/survey/cards/` 下 42 张逐项目卡片；全部计数由 `scripts/gen_survey_matrix.py` 从卡片机读 tag 重算 ⇒
`docs/survey/architecture-matrix.md`（42 行）与 `docs/survey/step-matrix.md`（四维分布）。**本文件不手写数字**。
**覆盖**：开源工程 CAD 21 家 · 学术 10 家 · 生成式网格 8 家 · 商业闭源 11 家（有重叠，去重后 42 张卡）。
**未覆盖**：R3 尾巴 8 家（Rhino / OpenSCAD-MCP / SLVSX / freecad-ai / 4 家 SW 竞品）仍在写。

---

## 一、四个维度上的真实分布（42 张的分母）

| 维度 | 分布（来源：`docs/survey/step-matrix.md`）|
|---|---|
| **中间表示** | `code` **14** · `mesh` **13** · `sequence` **8** · `feature-tree` **6** · `none` 1 |
| **编排** | `single` **23** · `loop` **10** · `none` 4 · `human-approve` 3 · `multi-agent` 1 · `template` 1 |
| **验证** | `visual` **19** · `numeric` **11** · `run-only` 4 · `none` 3 · `dfm-rules` 2 · `export-readback` 1 · `geometry-gate` 1 · `solver` 1 |
| **交付** | `mesh` **18** · `STEP` **12** · `none` 8 · `sequence` 3 · `drawing` 1 |

★ 一句话：**「能出可编辑实体（STEP）」的只有 12 家，出网格的 18 家；而「验证不靠模型自述」的只有 5 家**
（`dfm-rules` 2 + `export-readback` 1 + `geometry-gate` 1 + `solver` 1）。

---

## 二、五个可测的观察（每条都指回卡片或矩阵）

### 1. 表示层：代码 14 vs 网格 13 —— **几乎对半，但性质完全不同**

- `code` 的 14 家：agentcad · amagine3d · blender-mcp · build123d-mcp · cad-assistant · cad-coder · cad-recode · cadrille · cadam · cadquery-llm-skill · earthtojake-text-to-cad · mcp-cadquery · multi-agent-cad · zoo-text-to-cad（来源：`docs/survey/architecture-matrix.md`）
- `mesh` 的 13 家：hunyuan3d-2 · instantmesh · meshy · ptc-creo-generative · rodin · spar3d · spline-ai · stable-fast-3d · step1x-3d · trellis · tripo · triposg · triposr

★ 观察：**同样是 14/13，一边能进 CAD、一边不能** —— 判据不是表示难不难，而是**产物是不是 B-rep**（有没有 STEP/IGES）。
⇒ 只看「用没用 AI」没有意义，**要看导出清单**。

### 2. 编排层：`single` 23 家是多数，但那是**学术与云服务**的形态

- `single`（一次生成不回头）23 家，主要是：学术模型（cad-coder / cad-recode / cadrille / deepcad / drawing2cad / flexcad / img2cad / plankassembly / text2cad）+ 网格云服务（meshy / rodin / tripo / spline / trellis / triposr…）+ 只读桥（freecad-mcp / fusion360-mcp-server / sky-001）
- `loop`（写→执行→读错→重写）10 家：agentcad · amagine3d · blender-mcp · build123d-mcp · cad-assistant · cadam · earthtojake-text-to-cad · mcp-cadquery · multi-agent-cad ·（+ zoo 的 Zookeeper 代理）
- `human-approve` 3 家：adam-cad-copilot · fusion-assistant · spline-ai（全是商业产品）
- `multi-agent` 仅 1 家：multi-agent-cad

★ 观察：**回环几乎只出现在「开源工具」里**；商业产品一律是「人批准后才动」；学术模型一律单发。
⇒ 这不是技术先进与否的问题，是**责任归属**：开源工具把重试责任交给程序，商业产品交给用户。

### 3. 验证层：`visual` 19 家最大，但它是**最弱的一档**

- `visual` 19 家：8 家网格生成（只能看图）+ 5 家商业产品（人眼看）+ 4 家代码路线（blender / cadam / freecad-mcp / cad-assistant）+ multi-agent-cad
- `numeric` 11 家：学术用 CD/IoU（cad-coder / cad-recode / cadrille / deepcad / drawing2cad / flexcad …）+ fusion360（回带质量/包围盒）+ agentcad + sky-001
- **真正「不靠模型自述」的只有 5 家**：`dfm-rules` 2（earthtojake-text-to-cad · leo-ai）·`export-readback` 1（amagine3d）·`geometry-gate` 1（plankassembly）·`solver` 1（ptc-creo-generative）

★ 观察：**验证层级比生成能力更区分产品档次** —— 12 家能出 STEP，但其中只有 2 家把验证做成「不看模型自述」。

### 4. 交付层：**STEP 12 vs mesh 18**，中间还有 8 家根本不交付几何

- `STEP` 12 家 · `mesh` 18 家 · `sequence` 3 家（学术只交序列）· `drawing` 1 家 · `none` 8 家
- `none` 的 8 家很值得注意：adam / cadquery-llm-skill / drawing2cad / freecad-mcp / fusion-assistant / onshape / siemens-nx / spline？—— 其中 4 家是**只改既有模型、不产出新文件**的桥

### 5. 工具粒度：五个真实样本，跨度 66 倍

| 项目 | 工具数 | 来源 |
|---|---|---|
| autocad-mcp | **8** 个工具分派 72 个操作 | `docs/survey/cards/autocad-mcp.md` |
| blender-mcp | **9** 个模型可见（另 5 个 App-only） | `docs/survey/cards/blender-mcp.md` |
| freecad-mcp | **17** 个 | `docs/survey/cards/freecad-mcp.md` |
| fusion360-mcp-server | **93** 个 | `docs/survey/cards/fusion360-mcp-server.md` |
| 本仓库（对照） | **529** 个 | `AGENTS.md` |

★ 观察：8/9/17/93 都成立，但成立方式只有两种 —— **工具少 + 一个万能代码口**，或**工具多 + 每个都带结构化回读**。
**没有一家靠「工具多 + 只回 success」成立。**

---

## 三、同一环节的不同做法（每环节至少两个真实样本）

| 环节 | 做法 A | 做法 B | 做法 C |
|---|---|---|---|
| **E1 需求** | 一次提示直出（多数） | 批量追问 + 出站许可（我方 `design_ir.py`） | 三层绑定：不可变 intent / 可变源码 / 场景（amagine3d） |
| **E2 表示** | 代码 14 家 | 网格 13 家（含 4 家商业纯网格） | 特征树 6 家（都是改既有模型） |
| **E3 知识** | 指南唯一真源 + 内容哈希（agentcad） | 纯提示词资产（cadquery-llm-skill，无执行器） | 技能以 MCP resource 暴露 + 一键装到四家代理（build123d-mcp） |
| **E4 生成** | 单发（学术 23 家 `single`） | 采样多候选择优（cad-recode 采多个按 CD 选优） | 多智能体分工（multi-agent-cad，仅 1 家） |
| **E6 验证** | 数值增量回带（fusion360：每条改模型命令回带质量/包围盒/体数） | 导出回读（amagine3d：只认重新读回的文件） | DFM 规则 + 证据（text-to-cad；leo 宣称） |
| **E7 回环** | 分层 gate + `first_failure`（agentcad） | 双引擎 QA + 独立 Judge + 有界修复（multi-agent-cad） | 七视角拼图回灌自评（cadam） |
| **E9 人机** | 变更前审批（fusion-assistant / adam / spline 三家 `human-approve`） | 人只在最终审查（amagine3d 的「待视觉评审」） | 无门禁（`run-only` 4 家） |

---

## 四、三条可操作的结论（只从证据推）

1. **能进 CAD 的最小组合 = 代码/特征树表示 + 回环编排 + 数值以上验证。**
   42 家里同时满足的不到 8 家（agentcad / amagine3d / multi-agent-cad / earthtojake-text-to-cad / fusion360 / build123d-mcp / cad-assistant / zoo），
   而这 8 家恰好是「证据等级最实」的那批（来源：`docs/survey/architecture-matrix.md`）。
2. **「会不会错」与「错了能不能发现」是两件事** —— 12 家能出 STEP，5 家能独立判定对错；
   交集只有 2 家（earthtojake-text-to-cad 的 DFM 证据、amagine3d 的导出回读）。
3. **商业产品集体选择「不碰几何正确性」** —— 官方 FAQ 里 Fusion 直接写「工具没报错就报成功，但几何可能不是你要的」，
   Onshape 完全不碰几何，Creo 只出材料分布不保证可参数化（来源：`docs/survey/cards/fusion-assistant.md` · `onshape-ai-advisor.md` · `ptc-creo-generative.md`）。
   ⇒ **这是全行业主动留空的位置**，也是 `docs/ai-cad-landscape-report.md` §5「没有一家给出可验证的可制造定义」的 42 张实证版。

---

## 五、本批尚未覆盖（后续补）

| 问题 | 谁来补 |
|---|---|
| 桥接层最后 8 家（Rhino / OpenSCAD-MCP / SLVSX / freecad-ai / 4 家 SW 竞品） | R3 尾巴（进行中）|
| 每个项目的 `class` 判定复核 | R7 收口 |
| 总论从 v2 更新到 v3（把 42 张的新分类 J 类、`deliver=sequence`、规则 1/2 并入） | R7 |
| 卡片门禁从「暂缓接线」改为正式接线（含负例测试） | R7 |
