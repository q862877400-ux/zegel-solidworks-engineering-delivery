# AI 自动建模 · 全网技术路径逐项目调研计划

**依据**：业主 2026-10-23 指令 ——「把之前的调研结果先落文档，不是总的结果，而是**每一个项目**的情况。每个项目你都应该**克隆下来做全面的分析**，给出这个项目的**技术路径**，然后还有**技术方案**。然后再把多个项目放在一块儿做分类汇总，去分析现在已有的技术路径都是怎么做的。也可以去查学术论文和查一些新闻或者是社交媒体，看看有没有什么其他的路径。」以及「我想要的是把市面上的、包括学术界的、包括未发布的，一切的……技术路径都给它总结出来」。

**日期**：2026-10-23　**性质**：调研计划（执行中会按发现修订）

> ★★ **接手者先读 [`docs/survey/README.md`](survey/README.md)**（交接与索引：现状、目录地图、已完成/未完成、硬约束）
> 与 [`docs/survey/state.json`](survey/state.json)（机器可读状态：阶段、卡片清单、下一步动作）。
> 本轮已完成的实测事实：**40 个仓库全部克隆成功**（`D:\ai3d-survey\repos`，共 1.0 GB）；
> **SKY-001 情报专项已查清**（出卡 `docs/survey/cards/sky-001.md`，并新增第 10 类架构 `J=世界模型/几何状态`）。
**预期产出**：`docs/survey/cards/<slug>.md`（逐项目卡片，N 张）+ `docs/survey/architecture-matrix.md`（架构分类汇总）+ `docs/survey/step-matrix.md`（步骤做法矩阵）+ 更新 `docs/ai-cad-landscape-report.md`

---

## 0. 计划补强（我认为原计划缺的四件，已并入）

| # | 问题 | 补强 |
|---|---|---|
| 1 | 「每个项目都克隆」成本差别巨大 | **分三档**（§2）。TRELLIS 单仓库约 1.1 GB（来源：GitHub API `repos/microsoft/TRELLIS` 的 `size` 字段，实测 2026-10-23），商业闭源**根本没有源码** |
| 2 | 没有区分「真跑过」与「只读过代码」 | **每张卡片必须标注证据等级**（§4）：实测 / 读码 / 元数据；未实测写「未实测」，不许把 README 宣称当事实 |
| 3 | 16 GB 显存是硬约束（来源：本机 `nvidia-smi` 实测 RTX 4080 SUPER 16376 MiB，2026-10-23）| §3 列出**能跑 / 跑不了**名单；跑不了的只做架构复原 |
| 4 | 客户提到「SKY 001」这类未发布/自媒体信息 | 设**情报专项**（§6）：学术（arXiv）、新闻、社交平台；**查不到就写查不到**（AGENTS.md 铁律 5）|

---

## 1. 资源与红线（实测）

| 项 | 实测值 | 约束 |
|---|---|---|
| 克隆落点 | `D:\ai3d-survey\repos\` | D 盘剩余 2,763 GB（来源：`Get-PSDrive` 实测 2026-10-23）|
| 显存 | **RTX 4080 SUPER / 16 GB** | 见 §3 |
| Python | 3.14.7（来源：`python --version`）| ML 依赖需单独 venv/conda；**先验证再承诺能跑** |
| 网络 | GitHub `git ls-remote` 通（EXIT=0）| 可克隆；GitHub API 有 60 次/小时匿名限流，**批量取元数据要控速** |
| **许可红线** | 无 LICENSE / CC BY-NC / GPL/AGPL 的仓库 | **可克隆只读**（读 ≠ 用），**禁止把代码复制进本仓**；每张卡片写清许可与「只读思想」结论 |

---

## 2. 三档剖分（按「与目标的相关性 × 可行性」）

| 档 | 判据 | 做法 | 数量 |
|---|---|---|---|
| **T1 深挖** | 与「让普通模型建出可用规范的模」直接相关（代码即 CAD、桥接、模板/规则、验证）| **克隆 + 读关键源码 + 尽量真跑 + 逐文件证据** | 12–16 |
| **T2 复现架构** | 学术模型、生成式网格 | **克隆（`--depth 1`）+ 读代码/权重/论文 + 能跑就跑** | 15–20 |
| **T3 读文档** | 商业闭源、超大仓库、仅论文 | **不克隆**：官方文档 + API 文档 + 论文 + 元数据；标【宣称】/【事实】 | 15–20 |

> 「商业产品」没有源码可克隆 ⇒ 单独走**黑盒行为分析**（官方文档 + 免费额度实测 + 公开案例），并在卡片首行标明「无源码，证据来自官方文档」。

---

## 3. 显存可行性（16 GB 硬约束，来自各项目 README 明称值）

| 类别 | 项目 | 显存要求（各项目 README 明称值）| 16 GB（来源：`nvidia-smi` 实测）能否跑 |
|---|---|---|---|
| ✅ 能跑 | TripoSR ~6 GB、Hunyuan3D-2 形状 6 GB、SPAR3D 低显存 ~7 GB、TripoSG ≥8 GB、SF3D ~6 GB、SPAR3D 默认 10.5 GB（来源：各项目 README 明称值）| ≤16 GB | **能** |
| ⚠️ 边界 | Hunyuan3D-2 形状+纹理 16 GB、TRELLIS ≥16 GB | 贴上限 | **试，跑不动就写未实测** |
| ❌ 跑不了 | TRELLIS.2 ≥24 GB、Hunyuan3D-2.1 合计 29 GB | >16 GB | **只做架构复原** |

★ 网格类整体优先级**低于**代码类：它们的产物进不了 SolidWorks（见 `docs/ai-cad-landscape-report.md` §2）。

---

## 4. 逐项目卡片模板（12 字段，固定）

```markdown
# <项目名>

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | URL |
| 许可 | SPDX 或「无 LICENSE」；**只读思想 / 可借鉴** |
| 元数据 | stars · 最近推送 · 语言（来源：GitHub API 或仓库页，记日期）|
| 克隆 | 已克隆路径 / 未克隆（原因）|
| 证据等级 | **实测**（跑过，附命令与读数）/ **读码**（读过关键文件，附路径:行）/ **元数据**（只看了仓库页/论文）|

## 1. 一句话定位
## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）
逐段写；每段标「它怎么做的」与「关键文件:行」。
## 3. 技术方案要点（可迁移的机制）
只写机制，不抄代码；每条给证据。
## 4. 运行条件与依赖
显存/OS/内核/语言版本；实测命令与输出摘要。
## 5. 失败模式与已知坑
issue/README 警告/实测到的失败。
## 6. 对我方目标的可用处（机制层面）
## 7. 许可与红线
## 8. 证据清单
路径:行 / URL（每条一行，可复核）
## 9. 未确认事项（诚实清单）
```

**验收判据**（每张卡片必须全部满足才计入「完成」）：
1. 12 个字段无空缺（字段定义逐字见 `docs/survey/README.md`，来源：本文件 §4 模板），空的地方写「查不到」而不是留白；
2. 每条量化断言后面有可复核指向（`文件:行` 或 URL）；
3. 有「证据等级」，且等级与实际动作相符；
4. 有「未确认事项」段（允许为空，但要显式写「无」）。

---

## 5. 分批执行（每轮一个批次，产出可核验）

| 轮 | 批次 | 内容 | 产出 |
|---|---|---|---|
| R1 | 基建 + 情报专项 | 建目录、卡片模板、克隆脚本、**SKY-001 定位**（§6）；克隆 T1 第一批 | 目录就绪 + 情报结论 + 克隆完成清单 |
| R2 | T1-代码路线 | text-to-cad、Amagine3D、Multi-Agent-CAD、agentcad、cadquery-llm-skill、build123d-mcp、mcp-cadquery、CADAM | 8 张卡片 |
| R3 | T1-桥接层 | fusion360-mcp、freecad-mcp、mcp-for-blender、RhinoAI、autocad-mcp、openscad-mcp、SLVSX + 本地 4 家 SW MCP（已有克隆）| 11 张卡片 |
| R4 | T2-学术 | CAD-Recode、cadrille、CAD-Coder、FlexCAD、Text2CAD、DeepCAD、CAD-MLLM、Img2CAD、NURBGen、CAD-Assistant | 10 张卡片 |
| R5 | T2-网格（含实测）| Hunyuan3D-2、TRELLIS、TripoSG、TripoSR、InstantMesh、SF3D、SPAR3D、Step1X-3D | 8 张卡片（能跑的附实测读数）|
| R6 | T3-商业与情报 | Zoo、Fusion、Onshape、NX、Creo、Adam、Backflip、DriveWorks、Meshy、Rodin、Tripo、Spline、Leo + 新闻/社交/arXiv 补漏 | 13 张卡片（无源码，标【宣称】/【事实】）|
| R7 | 汇总 | `architecture-matrix.md` + `step-matrix.md` + 更新总图 v3 | 2 张矩阵 + 1 份总图 |

> 每轮**只做一件事并落盘**，轮的边界以「卡片通过验收判据」为准，不以时间为准。

---

## 6. 情报专项：定位「SKY-001」

业主原话：「看到一个叫 SKY 001，据说他们做了一个专门用来建模的模型，但是现在的模型都是大语言模型了，我就搞不懂他们是什么意思」。

**要做的事**：
1. 用搜索（中/英）查 `SKY-001`、`SKY 001 建模`、`Sky001 3D`、`sky-001 model`；
2. 列候选并逐一排除：Skywork（昆仑万维，SkyReels/Skywork 系列）、Seed3D（字节）、Skybox、Sky-T1，以及「非 LLM 的建模模型」这一族（如 3D 扩散/流匹配、CAD 专用生成模型、NURBS 生成）；
3. 若查到：写出**它的技术路径**（是否 LLM？表示是什么？训什么数据？）
4. 若查不到：**按铁律 5 写「查不到」并列出检索过的关键词**，不做推测性断言。

★ 这一条可能会改变架构分类（「专门建模的模型」在 §1 的九类里属于 D/E/F 三类之一），所以放在 R1 最先做。

---

## 7. 汇总方法（Phase 2）

**不允许手写汇总表**，由脚本从卡片生成，保证可重生成、可核验：

1. 脚本扫 `docs/survey/cards/*.md`，抽取「表示 / 编排 / 验证 / 交付」四列 → `architecture-matrix.md`；
2. 抽 E1–E9 各环节的「做法」标签 → `step-matrix.md`（做法 × 采用项目数）；
3. 汇总里每个项目名都指向它的卡片文件（可点）。

---

## 8. 验收（整个调研的完成判据）

1. 卡片数 ≥ 45，且 **T1 全数完成**；
2. 每张卡片过 §4 的四条判据（由 `scripts/check_survey_cards.py` 机检，**计划在 R1 一并写出来**）；
3. 汇总表由脚本生成，且与卡片一致（脚本同时做一致性断言）；
4. 情报专项有结论（查到写路径，查不到写关键词清单）；
5. 总图 v3 与 v2 的差异处**逐条说明为什么变**。

---

## 9. 附：机读 tag 行的枚举（含**新增取值的登记**）

卡片 H1 之下必须有一行：

```html
<!-- survey: class=B; repr=code; orchestration=loop; verify=geometry-gate; deliver=STEP; evidence=读码 -->
```

| 字段 | 允许取值 |
|---|---|
| `class` | A 代码单发 · B 代码回环 · C 多智能体 · D 序列/DSL 专模 · E 生成式网格 · F 逆向 · G 模板+规则 · H GUI/API 代理 · I 知识助手 · J 世界模型/几何状态 |
| `repr` | code · sequence · dsl · feature-tree · mesh · constraint · params |
| `orchestration` | single · loop · multi-agent · template · human-approve · none |
| `verify` | none · run-only · geometry-gate · numeric · visual · solver · dfm-rules · export-readback |
| `deliver` | STEP · mesh · drawing · gcode · **sequence** · none |
| `evidence` | 实测 · 读码 · 元数据 |

### 新增取值登记（★ 每次扩充都要在这里留一行，否则后人会以为是笔误）

| 取值 | 何时加 | 为什么 | 依据 |
|---|---|---|---|
| `deliver=sequence` | 2026-10-24（R4 学术批次）| 学术序列模型（DeepCAD / Text2CAD / FlexCAD / Img2CAD / Drawing2CAD 一类）的交付物**就是命令序列本身**，STEP/STL 只是可选的下游脚本产物 ⇒ 记 `none` 失真、记 `STEP` 撒谎 | `docs/survey/cards/deepcad.md` · `docs/survey/cards/flexcad.md` |
| `repr=none` | 2026-10-24（R6 商业批次）| Onshape AI Advisor **完全不碰几何**（只答问并给引用）⇒ 没有中间表示可言；用 `code`/`mesh` 任一都会失真 | `docs/survey/cards/onshape-ai-advisor.md` |
| `class=G` 用于拓扑优化 | 2026-10-24（R6 商业批次）| PTC Creo Generative Design 的机制是「**给约束 → 求解器吐材料分布**」，A–J 里没有对位项；判词是「模板+规则+求解」族，暂寄 `G` 并在卡内注明 | `docs/survey/cards/ptc-creo-generative.md` |
| `class=J`（世界模型） | 2026-10-23（R1 情报专项）| SKY-001 一族不是 LLM 也不是网格生成，而是**预测几何状态序列** | `docs/survey/cards/sky-001.md` |

### 分类口径裁决（2026-10-24，R4 提出的交叠问题）

**规则 1：`class` 按「生成机制」判，不按「输入形态」判。**

理由（来自 R4 的真实交叠）：PlankAssembly（三视图线稿 → 板件形状程序）与 Drawing2CAD（矢量四视图 → 命令序列）
的**输入**都不是自然语言，但它们的**机制**是「让模型学一种形状/命令语言」= D 类；
若改按输入形态判，它们会和 Img2CAD（单图 → CAD，机制是**条件分解 + 参数回归**）一起塌进 F 类，
**把三种完全不同的机制压成同一个标签**，汇总表就失去区分度。

⇒ 输入形态写进卡片 §2（技术路径的第一段），**不进 `class`**。
⇒ 需要跨卡统一改类时，必须在 R7 一次性改全部卡片并在此登记理由，**禁止单卡私改**。

**规则 2：闭源产品的 `deliver=STEP` 表示「工程格式桶」，不是「已证实直出 STEP」。**

背景（R6 的 LEO AI 案例）：它的官网/博客**没有公布导出格式清单**，但产品的定位与客户案例是
「交付带特征树的参数化装配、进 SolidWorks/CATIA」。此时：
- 记 `none` 会失真（它明明交付工程格式）；
- 记 `STEP` 会过度断言（没人证实它直出 STEP）。

⇒ 允许闭源产品用 `deliver=STEP` 表示「工程格式桶」，**但必须在卡片 §1 与 §9 明写「是否已证实直出 STEP」**，
并在 §8 证据清单列出支撑链接。R7 汇总时这类条目要在矩阵里加脚注。