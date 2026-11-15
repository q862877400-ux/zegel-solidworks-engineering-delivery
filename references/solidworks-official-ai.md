# SOLIDWORKS 官方 AI 能力调研（对比我们的上游与我们自己）

- 档位：**L2 主题横评**
- 对象类型：厂商产品能力（非代码项目，所以不做星数/许可体检）
- 抓取日期：2026-11-07
- 建档目的：竞对功能跟踪 —— 官方 AI 能力已进入我们必须盯的列表

---

## 一、它包含哪些功能

### A. 产品内生成式功能（SOLIDWORKS 2026 桌面，已 GA）

来源：【一手】达索官方媒体公告 2025-11-18
<https://www.3ds.com/newsroom/media-alerts/dassault-systemes-announces-solidworks-2026-ai-powered-design-and-collaboration-generative-economy>

| 功能 | 内容 |
|---|---|
| **Auto-Generate Drawing（Beta）** | 「新建」菜单下，一键生成图纸视图 + 建议尺寸，自动识别孔（原生或导入件） |
| **AI 紧固件识别与自动装配** | 自动识别像紧固件的零件（螺母、螺栓、垫圈）并装配 |
| **选择性加载** | 大装配只加载需要的数据 |
| **命令搜索增强 / 常用命令高亮 / 断网可用** | 体验层改进 |
| **工程图戳记（新增用户属性）** | 变更管理与追溯 |
| **托管切割清单** | 3DEXPERIENCE 上，工程 BOM 与制造 BOM 合一 |
| **Command Predictor** | 【转述】xApps 里用 AI 预测下一步命令，最多 7 个建议 |

### B. Virtual Companions —— 三个 AI 代理

来源：【一手】达索官方新闻稿 2026-07-23
<https://www.3ds.com/newsroom/press-releases/dassault-systemes-expands-3dexperience-ai-native-agentic-platform-new-virtual-companion-skills-co-engineer-humans>

| 代理 | 职责 | 状态 |
|---|---|---|
| **AURA** | 知识副驾：回答怎么做、总结社区/公司知识，**给来源链接** | 2025 首发；SOLIDWORKS 2026 SP1 / FD01 起可在 **SOLIDWORKS Labs (Beta)** 标签页内用 |
| **LEO** | 工程代理：建模、验证、仿真、走向制造 | 同上 Beta |
| **MARIE** | 材料、化学、科学 | 2026 稍晚 |

**共 19 项 competency**，每项是一组 skill，覆盖业务、产品设计、工程、仿真、制造、运营。

### C. LEO 在 2026-02 大会现场演示过的动作

来源：【一手】DEVELOP3D 现场报道
<https://develop3d.com/cad/event-report-3dexperience-world-2026/>

- 初始图 → 带可调参数和尺寸的**草图**
- **Sketch-to-3D** → 三维参数化模型
- **代理模型（surrogate modelling）** → 用一句 prompt 对零件跑 FEA，走「快速、算力便宜的数学近似」
- **从规格直接出水箱**：给容积、地点、当地环保法规，自己算出满载重量、受力、桁架结构，**含焊件**
- 【转述】把图片转成网格；给导入的 STEP 加参数化特征；评估装配并标出设计错误

---

## 二、它的架构

```
┌──────────────────────────────────────────────────────────┐
│ 交互层                                                    │
│   SOLIDWORKS Design 内「SOLIDWORKS Labs (Beta)」标签页     │
│   3DEXPERIENCE xDesign（云端）—— 完整能力要它              │
├──────────────────────────────────────────────────────────┤
│ 代理层                                                    │
│   AURA（项目管理/知识） LEO（工程） MARIE（科学）           │
│   19 项 competency，每项 = 一组 skill                      │
│   流程：理解意图 → 在工业语境里推理 → 决策 → 产出结果        │
├──────────────────────────────────────────────────────────┤
│ 模型层                                                    │
│   Mistral AI 基础模型（在转 Nvidia「完整 AI 库」）          │
├──────────────────────────────────────────────────────────┤
│ 算力与数据层                                               │
│   OUTSCALE（达索自有云 + AI 运营商），三大洲部署，主权基础设施 │
└──────────────────────────────────────────────────────────┘
```

**四个设计取向（这是它真正难抄的地方）：**

1. **知识模型当护城河**：官方原话是「基于市场上第一批 mission-critical 的知识与 know-how 模型」——把项目管理、工程、仿真、生物科学的行业知识编码成可调用的模型，而不是让 LLM 现场推理。
2. **按专业域拆代理**，不是一个万能代理。同一个问题问三个代理会给三个不同答案，各自贴合专业视角。
3. **结果必须「有科学和工业依据」**（grounded in science and industry-accurate reality）。
4. **按消耗计费**，不按座位。CEO 说「一张简单桌子用的算力比一辆钢制汽车少」。

**使用前提（硬约束）：** 必须登录 3DEXPERIENCE + 联网；代理跑在云上，不在工作站；完整能力要迁到云端 xDesign。

---

## 三、对比：官方 vs 上游 vs 我们

先给一条已核实的关键事实：**上游没有自己的模型。** 全仓扫 `import openai` / `anthropic` / `chat/completions` 等 —— **0 处真实模型调用**，只有一处指向 Claude 文档的 URL。它的「AI」= 给宿主 agent（Codex / Claude / Cursor）编译 prompt + 打包 skill。我们同样没有自有模型。

| 维度 | 达索官方 | 上游（wzyn20051216） | 我们 |
|---|---|---|---|
| 基础模型 | **自有**（Mistral → Nvidia） | 无，借宿主 LLM | 无，借宿主 LLM |
| 算力 | OUTSCALE 自有云，三大洲 | 本机 | 本机 |
| 运行位置 | 云 / 云端 xDesign | 本机 COM | 本机 COM |
| 联网 | **必须** | 不必须 | 不必须 |
| 几何执行 | 官方内核 | SolidWorks COM | SolidWorks COM |
| 知识资产 | 19 competency + know-how 模型 | 5 个子技能 + prompt 模板 | 140 条能力 + E1–E7 判据 + GB/T 层 |
| 交付形态 | 订阅 + 按消耗计费 | 开源 MIT | 内部 |
| 状态 | 核心能力仍是 **Beta** | — | — |
| 中国国标 | **不覆盖** | **不覆盖** | **唯一覆盖** |

### 三条判断

**① 官方现在做的事，正好压在我们和上游想做的上半段。**
图纸自动生成、紧固件识别装配、Sketch-to-3D、从规格出水箱 —— 这些覆盖了「把设计意图变成模型」这一段。

**② 但官方和我们的目标不是同一个。**
官方定位是「让**已经在用 CAD 的人**更快」。CEO 原话：「AI 只是乘数，你才是价值」，并反复强调不替代人。我们要的是「让**不会 CAD 的人**出可交付零件」。这两个目标在前半段重叠，在后半段分叉。

**③ 官方明确承认最像我们的那件事还没做到。**
DEVELOP3D 原文：上传图片得到**可制造**模型、跟代理对话定义设计，**「will all happen in the next couple of years」**。也就是说 —— 文字/图片 → 可制造零件，官方自己说还要两三年。

### 官方目前的软肋（我们的机会）

| 软肋 | 依据 |
|---|---|
| 必须联网 + 云端 + 订阅 | 官方架构决定 |
| 核心能力仍是 Beta | 2026 SP1/FD01 才进 Labs Beta 标签页 |
| 用户抵触涨价与迁云 | DEVELOP3D：355 场分会只有 **5%** 讲 AI；说服用户接受涨价和迁云「需要时间」 |
| 实际可用度低 | 经销商 morphos3d：Leo「抛光的舞台演示」和「Beta 按钮在你脏的生产数据上跑」不是一回事，建议只在废项目上试 |
| **完全不碰中国国标** | 全库检索无 GB/T 相关能力 |
| 不承诺验收判据 | 它给「生成结果」，不给「可验收结果」+ 证据链 |

### 我们该抄的四段（写到文件级）

1. **答案必须带来源**：AURA 的回答强制附来源链接。我们的 `evidence` 字段方向一致，但现在是自由文本，应升级为可核验的产物 + 结论字段（本轮之前已查过：81 个产物 JSON 全部带结论字段，改造成本约 1 小时）。
2. **按专业域拆代理**：不要一个万能代理，按专业分工。我们目前是单链流水线。
3. **代理模型（surrogate modelling）做快速预估**：LEO 用便宜数学近似先给一版 FEA。我们 `simulation_and_fea` 标了 verified 但 **`fea_analysis.py` 根本不存在**，这条是实打实的缺口。
4. **把知识组织成可调用模型**：我们有 `specs/` 2449 个文件 + GB/T 层，但没组织成官方那种「competency」形态。

---

## 四、强制反证节

**搜了什么：** `SOLIDWORKS AURA AI criticism limitations not useful review`、
`Dassault Systèmes generative CAD text to 3D part creation SOLIDWORKS`

**搜出什么（真命中 3 条）：**

1. **经销商自己劝退**：morphos3d（SOLIDWORKS 经销商）明确指出 Aura 是唯一低风险的，Leo 应该「只在废项目或内部项目上试，不要排进真活的关键路径」，Marie「大多数车间可以直接忽略」。
2. **AI 在官方议程里占比很小**：DEVELOP3D 记录 355 场分会只有 5% 涉及 AI。
3. **最关键的那件事被官方排到未来**：文本/图片 → 可制造模型，「未来两三年」。

**另有一条弱证据（【转述】，不采信为事实）：** 捷克论坛评论称 AURA 仍是 beta、模型很小（1.5B）、且是外部 Add-in 形态。—— 其中「1.5B」无法核实，不写入结论。

---

## 五、覆盖自查

- **候选池**：官方 AI 相关对象登记 **6** 个（AURA / LEO / MARIE / SOLIDWORKS 2026 产品内功能 / xDesign 云 / Command Predictor）；另有第三方竞品 **CADABRA**（SOLIDWORKS 内的 AI copilot 插件）1 个，只到 metadata，未深挖 —— 列入「已知遗漏」。
- **depth 分布**：`fulltext` 2（两份官方新闻稿）、`source` 1（DEVELOP3D 全文）、`readme` 1（morphos3d 全文）、`metadata` 2（CADABRA、捷克论坛）。
- **反证节**：约 400 字，真命中 **3** 条。

## 六、复核总账

抽查 8 条事实（>10%）：

| 结论 | 记法 |
|---|---|
| SOLIDWORKS 2026 于 2025-11 发布，含生成式图纸与紧固件识别 | 确认 |
| 三个代理名为 AURA / LEO / MARIE | 确认 |
| 19 项 competency | 确认（2026-07-23 官方稿原文） |
| 跑在 Mistral 模型 + OUTSCALE 云 | 确认（官方稿 + DEVELOP3D 双向一致） |
| AURA/LEO 已可在 SOLIDWORKS 2026 SP1/FD01 的 Labs Beta 内使用 | 确认（morphos3d，单一来源，标【转述】级） |
| 正在转向 Nvidia AI 库 | 确认（DEVELOP3D） |
| 文本→可制造模型官方称还要两三年 | 确认（DEVELOP3D 原文） |
| 上游无自有模型调用 | **确认（本机全仓扫描，0 命中）** |
| AURA 模型规模 1.5B | **无法核实**，不采信 |

**错误率：0 / 8 = 0%**，但样本仅 8 条，不作为质量保证；`morphos3d` 为经销商来源，立场可能偏向自家服务。

---

## 七、尚未查的（已知遗漏）

- **CADABRA**（SOLIDWORKS 内第三方 AI copilot 插件）：能做自然语言改模型、概念到 CAD、生成制造图纸（含 GD&T/BOM）。这是比官方更接近我们形态的竞品，**本轮只到 metadata，未深挖**。
- 官方的**定价**：CEO 说按消耗计费，具体数字未公布。
- **xDesign 完整能力的实际门槛**：是否需要额外订阅、迁移成本多少。
- 官方的 **API / 二次开发入口**：代理能不能被外部程序调用（决定我们能否对接）。
