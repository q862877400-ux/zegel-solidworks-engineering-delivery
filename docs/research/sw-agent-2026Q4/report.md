# SolidWorks × Agent 三个月增量调研 · 主报告

> **窗口**：2026-08-01 → 2026-11-02（双轨：此后首次公开 **或** 近 90 天仍活跃）
> **依据**：业主 2026-11-02 指令；任务书见 [`00-brief.md`](00-brief.md)；档位 L3（候选池 > 10，跨 5 层）
> **状态**：**五线全部收口** —— A（10 卡）· B（4 卡 + 2 份实测分析）· C（2 卡）· D（5 卡）· E（台账复核）· 商业侧（2 条 JSONL）。新增 **21 张**卡片全部过 `check_survey_cards.py`；`release_check` exit 0。

---

## 0. 结论先行（先给判断，证据在 §2）

### 0.1 对「有没有完整体能让我们停止自研」的答复

**开源侧：没有。商业侧：找到了一个真正对题的，一手核完之后结论是「可以买来做底座，但不能让我们停止自研」。**

| 候选 | 一手核实到的事实 | 对我们意味着什么 | 结论 |
|---|---|---|---|
| **MecAgent V2.0**（闭源商业，**已用官方文档核实**） | **支持 SW 2024/2025/2026（技术团队测试过）**；Text-to-CAD / **STEP-to-CAD（重建可编辑特征树）** / Drawing-to-CAD / CAD-to-Drawing / 装配配合 / 爆炸图 / 运动算例 / 材料 / 方程式 / 配置 / 宏；实时 agent 在**用户已打开的会话**里干活；后台任务在服务端跑 | **它把「让 Agent 在 SolidWorks 里建模」这件事做成了产品**，版本、形态、能力都对着我们的环境。但它自己声明：**「保证工程图的认证或法规合规性」做不到**；**工程图标准只有 ISO / ASME Y14.5（无 GB）**；**「设计意图、验证和发布仍由您掌控」**——它不负责任何几何验证 | **可买作底座，不能停自研**（我们的核心价值 E1–E7 判据 + 中国规范合规，正是它明确不承担的）|
| **Spectral Labs（SGS-Mk2 + Quartz）** | 自称自主通过 CSWP，判对标准 **体积/质心/距离在 0.1% 内**；自述通过多次但**未满分**；45 道自建题 | 它的 0.1% 判据与我们几何门直接可比，是个「考试式验收」的样板 | **待核**（仍需一手报告原文）|
| **SolidCraft / CADCraft**（开源，MIT OR Apache-2.0） | 完整的参数化 CAD / 2D 制图应用，带 MCP | **它们不驱动 SolidWorks**，读不了 `.SLDPRT`，且缺工程图/CAM | **不是解**，是另一条路的实证 |

**⇒ 我们没有找到一个可以停止自研的完整体。** 但 MecAgent 的存在改变了一件事：**「从零让 agent 会建模」这部分已经被商品化了**，我们不值得再重复造；值得继续自研的，是**判据（E1–E7）与中国规范合规**这一层——而那恰好是它公开说不做的。

### 0.2 对「有没有聪明技术路径」的答复

**有，而且是本轮最确定的收获。** 五条可直接搬，按性价比排序：

1. **★★★ 把判据塞进调用里（`expect` 内联断言）** —— SolidCraft 的 `execute`/`batch` 接受 `expect {volume_mm3, tol, bodies, bbox}`，执行完自动比对并回 `mismatch`；默认容差 **0.2% / 0.05 mm**。我们把「建完再单独查一次」改成「判据跟着动作走」，是零成本的改造。
2. **★★★ 选择歧义必须显式失败** —— `soheil-mp` 的 `EntityRef`：声明式查询 `where` **必须带命中数 `expect`**，不符就抛 `EntityAmbiguous` 并列出候选。这是本批对「**持久引用**」这个问题最好的答案，也直击我方「选错面/边却不报错」的静默故障。
3. **★★★ oracle 三段式** —— 解析闭式解 + 独立内核（FreeCAD，当外部程序跑，不是依赖）+ **交付物回读**；**90/90** 常绿，容差 1e-3，附 Hausdorff 距离。这直接补我们 E1–E7 缺的那层。
4. **★★★ 少工具 + 运行时发现** —— SolidCraft 用 **21 个工具**覆盖全部建模能力；我方上游**自带** `SW_MCP_DISCOVERY=search`，实测能把 66 个工具的 `tools/list` 从 **23,411 tokens** 压到 **474**。我们用 **439 个工具**。这不是风格差异，是成本差异。
5. **★★ 离线拿到体积** —— `blussyya/solidworks-converters`（**Apache-2.0**，零依赖 Node）直接从内嵌 Parasolid B-rep 精确积分，**在本仓 8 个零件上复现了 SolidWorks 的读数**（7 个相对差 <1e-11，1 个完全相等）。这条能把我方几何门从「开 SW 回读」搬到离线。

**另有一条环境级发现**：`infei12306` 诊断出「**类型库版本错配**」——注册表登记 21.0/1.0 而 `.tlb` 内是 33.0，导致 `LoadRegTypeLib` / `EnsureModule` / `EnsureDispatch` 全报 `TYPE_E_LIBNOTREGISTERED`；正解是按路径 `LoadTypeLib` + 私有 stub + 走 ROT attach。**这可能是我方「makepy 时好时坏」的原因，一条命令可自查（见 §8 第 4 条）。**

**还有一条来自商业侧的机制**：MecAgent 的 **General Knowledges** —— 把公司标准、材料、供应商文档做成一个文件夹挂给 agent 当上下文，**一个请求用一个文件夹**，也可开启「每个请求都带上」。它明确说「公司特定规则请放进 General Knowledges，不要每次重复在提示词里」。⇒ 这正是我方**「规则包」思路的商品化实现**，说明「规则外置成可挂载的资料」这条路是对的；差别在于**它只把规则当上下文喂给模型，我方要把规则做成可执行的判据（E1–E7）**——后者才是我们不该放弃的部分。

### 0.3 一条必须写进台账的趋势

**2026-10-07 同一天，两个 AI 编码 agent 生成的完整 CAD 应用上线**：SolidCraft（Fusion 风格，13,016★）与 CADCraft（AutoCAD 风格，7,429★），同为纯 Rust、同为 clean-room、同为 MIT/Apache 双许、同暴露 MCP。这不是孤立事件，是**一条可复制的配方**：领域知识 + AI 编码 agent + 单栈 + 双许可 + MCP。

对我们的意义不是「去写一个 CAD」，而是：**同样的配方能不能用来重做我们自己的验证链**（把「开 SolidWorks 回读」换成离线几何核验）。

---

## 1. 方法与边界

### 1.1 怎么找的（可复现）

```powershell
# 检索口径（2026-11-02，gh 已认证，4999/5000 配额）
gh api -X GET "search/repositories?q=<q>+in:name,description,readme+pushed:>2026-08-01&sort=stars&per_page=100"
```

查询集：`solidworks mcp`、`solidworks agent`、`solidworks llm`、`solidworks ai`、`solidworks copilot`、`solidworks automation`、`solidworks python api`、`solidworks in:name`、`topic:solidworks`、`solidworks ... created:>2026-08-01`、`solidworks ... pushed:>2026-09-15 stars:>10`。

命中规模：`solidworks in:name` **4,849** · `topic:solidworks` **948** · `solidworks ... created:>2026-08-01` **1,327** · `solidworks ... pushed:>2026-09-15 stars:>10` **30**。
人工筛出与本命题相关的新对象约 **30 个**，去重后分 5 线（见任务书 §L3.7）。

### 1.2 边界（主动划，不假装全面）

- **不跑 SolidWorks**（业主口径）。所以任何「它能在 SW 里建出正确几何」的结论最高到 `source`/`转述`，到不了 `tested`。
- 只对 **C 线做了 clone + 读码**；A/B/D 由并行探查员做，完成后追加。
- **未编译 SolidCraft**（Rust 工具链不在本轮范围）⇒ 它的 90/90 是**它 CI 的宣称**。
- 商业产品（MecAgent / Spectral Labs）只有媒体转述与少量官网元数据。

---

## 2. 本轮发现（分线）

### 2.1 C 线 · 换底座：SolidCraft 与 CADCraft

**SolidCraft（`tangency-labs/solidcraft`）** —— 卡片见 [`docs/survey/cards/sw-tangency-labs-solidcraft.md`](../survey/cards/sw-tangency-labs-solidcraft.md)。

已实测的一手数字：**13,016★ / 1,701 forks / 创建 2026-10-07 / 推送 2026-11-02 / MIT OR Apache-2.0**；`crates/` 下 **1,509 个 `.rs`、734,867 行**；**21 个 MCP 工具**（`crates/mcp/src/tools.rs` 的 `tool(` 调用计数）；**90 个 oracle case**；**17 个 SKILL.md**。

它做对的三件事（也是我们最该抄的三件）：
1. **`expect` 内联断言**：判据跟着调用走，`EXPECT_VOLUME_TOL = 0.002`、`EXPECT_BBOX_TOL_MM = 0.05`。
2. **oracle 三段式**：69 个解析闭式解 + 21 个 FreeCAD 独立内核交叉 + **每件导出 STEP 再读回**；`docs/oracle.md:10` 明写「No expected value comes from a commercial CAD product」。
3. **21 工具 + 运行时发现命令**：`list_commands`/`describe_command` 让模型查命令表，而不是把 439 个工具塞进上下文。

它做不成的事（硬缺口）：
- **没有工程图**（Drawings 里程碑 3/21，还在 `drawings` 分支）—— 对 GB 图样交付是硬伤；
- **没有 CAM**（0 完成）；**曲面 6/14**；
- **不能读 `.SLDPRT`，不能驱动 SolidWorks**（Import 里程碑 7/39，SolidWorks 导入仍未做）；
- 内核正在从 truck 迁 NVIDIA SMLib（未进发布）。

它自己的定性（`docs/capabilities.md:5-9`）：**「early but usable for simple parts」**，且「These checks do not establish complete geometric or workflow equivalence」。

**CADCraft（`storytold/cadcraft`）** —— 卡片见 [`docs/survey/cards/sw-storytold-cadcraft.md`](../survey/cards/sw-storytold-cadcraft.md)。7,429★、2026-10-07 创建、AutoCAD 风格 clean-room、README 自称 agent-drivable over MCP。**只读到 README，未读码**。它是「同一天、同一配方」的第二例，价值在趋势不在技术。

**反证（必须记）**：第三方评测明确劝退复杂用途 ——「Do not adopt it as your production CAD tool for complex assemblies, since the project's own oracle checks do not establish complete geometric equivalence with FreeCAD」（[hysenlabs](https://hysenlabs.com/projects/bherbruck-solidcraft)）；另有报道称两项目均为「vibe-coded」（[3dprintingindustry 2026-10-18](https://3dprintingindustry.com/news/vibecoded-clones-of-solidworks-and-autocad-released-as-open-source-255770/)），星数在两周内从约 2.9k 涨到 13k，增速本身不是质量证据。

### 2.2 E 线 · 已有台账复核（三个月内到底动了什么）

| 对象 | 三个月内 | 判定 |
|---|---|---|
| `eyfel/mcp-server-solidworks`（SolidPilot，AGPL） | 近 15 个提交全是面向 2026 SP3 的版本号、adapter `/health` 与代理修复、README 图片替换。**它自述的 make-or-break「持久引用解析器」没有任何实现提交** | **无实质进展**，台账结论仍成立 |
| `Bennyco86/q3ds-solidworks-mcp` | **仓库已 404** | 台账需修正（原记「SolidPilot 的 fork，58 工具」）|
| `Slacker-LLC/solidworks-mcp` | **仓库与账号均 404**（`gh api users/Slacker-LLC` 返回 404） | 台账需修正；其 Apache-2.0 源码已无从获取，若我们引用过它的机制，须改为「已消失，来源不可再取」|
| `andrewbartels1/SolidworksMCP-python`（MIT） | **2026-11-01/02 密集提交并发 1.5.0，首次上 PyPI**；提交信息含 `verify fillets`、`cut Through All both ways as a double-ended cut`、`never launch SolidWorks outside the adapter` | **实质进展**，且三条都对着我们已知事实（through_all_both 坑、单源 COM）|
| `wzyn20051216/solidworks-automation-skill`（本仓上游） | 2026-10-31 → 11-01 连续做 **GD&T、基准、复合公差框、结构化自动落图、装配改名后的配合引用核对** | 上游在动，方向是**图样合规**（对应我们 E6）|
| `Cai-aa/CAD-Agent-Hub` | 最近一次是 **CATIA V5 适配**（2026-10-25），不是 SolidWorks | 与本命题相关性下降 |
| `just1step/solidworks-mcp` | 最后推送 2026-04-10 | **死项目** |

### 2.3 商业侧 · MecAgent 一手核实（本报告最重要的发现）

**来源**：官方[中文用户指南](https://mecagent.com/zh/user-guide)（2026-10-20 抓取）、[价格页](https://mecagent.com/zh/pricing)、[关于页](https://mecagent.com/zh/about)。★ 这是本报告唯一「一手文档」级的商业产品证据，不再是媒体转述。

**它是什么**：面向机械工程师的 AI CAD 智能体，V2.0 把 V1.2 的五个独立模式合并成一个。两种工作方式：

| 方式 | 说明 | 对我们的意义 |
|---|---|---|
| **CAD 智能体（实时）** | 在**用户已打开的 SolidWorks 会话**里建模/改装配/加材料/驱动方程式/重命名/导出/出工程图/写宏 | 与我方「单源 COM」同一个形态，说明这条路是主流 |
| **后台任务（异步）** | Drawing-to-CAD、CAD-to-Drawing、Text-to-CAD、STEP-to-CAD、宏生成**在它服务器上跑**，产出 STEP/PDF 文件 | 数据外发；对我方保密件是红线 |

**能力面（逐条摘自官方「能做什么」）**：带**可编辑特征树**的 Text-to-CAD；STEP 重建为原生可编辑零件；装配体内设计并配合；爆炸视图；运动算例；材料与质量更新；全局变量/方程式/配置；**重命名而保留参考关系**；批量导出 STEP/PDF/DXF；CAD-to-Drawing；Drawing-to-CAD（PDF/图片 → 可编辑零件）；宏（**C# 运行环境**，不是 VBA）；General Knowledges（挂公司文档当上下文）。

**它自己声明的边界（官方「暂时不能做什么」，逐条）**：

1. 未经工程审核就发布工程图或零件；
2. **保证工程图的认证或法规合规性**；← **这是对我方最关键的否决项**
3. 复杂自由曲面 / A 级曲面；
4. 在模糊指令下做人类水平推理；
5. **应用从未提供过的公司特定规则**（须先加进 General Knowledges）；
6. 原生支持 SolidWorks 以外的 CAD；
7. **2024 之前的版本不保证**。

**工程图能力的具体口径**（官方 §6.7）：制图标准只有 **ISO** 或 **ASME Y14.5**；单位 mm/inch；图纸 A4–A0；可用**自己的空白模板**（公司标题栏）；可点选基准 A/B/C 与「关键表面」；可勾选「完整标注」。**⇒ 没有 GB/中国国标选项。** 官方技术建议里还写着「发布前审核每张工程图，尤其是公差和 GD&T」。

**⇒ 对我们意味着三件事**：

1. **「从零让 agent 会建模」已经商品化**（含最能体现工程价值的 STEP-to-CAD 重建特征树）。**这部分不值得我们再从头做。**
2. **它明确不承担的，正好是我们的护城河**：GB/中国规范合规、E1–E7 判据、可独立复核的验证层。官方原话「设计意图、**验证**和发布仍由您掌控」。
3. **商业条款上它是云服务**：请求/上下文/操作与服务器交换；隐私模式只在 Starter/Advanced+；Enterprise 才有 SOC 2 / 本地部署。**保密件场景直接排除免费版**。

**价格（两处口径不一致，如实记录）**：[价格页](https://mecagent.com/zh/pricing)写 Starter ~~$125/月~~、Advanced+ ~~$625/用户/月~~（15,000 / 90,000 token 每月）；用户指南 §8.1 写 Starter **US$99**、Advanced+ **US$499**，并注「按年付费约可省 17%」。⇒ **月付价 vs 年付价的差别，未在页面上明确对应关系**。

**安装与依赖**：Windows 10/11 64 位；安装包约 333 MB；**需要出站 HTTPS 443 到 `proxy.mecagent.com`**；自动检测并连接 SolidWorks。

**与 Spectral Labs 的区别**：Spectral Labs 是「模型 + 执行环境」（SGS-Mk2 + Quartz），卖的是**能力**，并对 CSWP 考试给了 0.1% 的量化判据；MecAgent 卖的是**产品**（装进 SolidWorks 的副驾驶 + 后台任务）。两者不是同一层。

---

## 3. 对不上的地方（不抹平）

1. **「开源有完整体」这个假设不成立。** 三个月里最热的两个 CAD 开源项目都不驱动 SolidWorks；真正对标的（MecAgent / Spectral Labs）是闭源商业。
2. **星数 ≠ 能力。** SolidCraft 一周 13k 星，但它自己写「early but usable for simple parts」；Spectral Labs 靠考试背书，但自认「未满分」。两边的自述都比外面的欢呼保守。
3. **我们台账里两个条目已失效**（q3ds、Slacker-LLC 双双 404），这是本轮实测发现，不是推断。
4. **SolidPilot 的 make-or-break 问题三个月零进展** —— 这条既是它的问题，也说明「持久引用解析」在这个圈子里是真难，不是我们笨。

---

## 4. 待核清单（按优先级）

| # | 待核项 | 怎么核 | 为什么必须先核 |
|---|---|---|---|
| 1 | **MecAgent：实测一次**（免费版），只验三件事：① 它是否真在 SolidWorks 原生 API 上建特征（而非导入几何再"伪装"特征树）② 用**我们自己的空白模板（公司标题栏）**能否绕过「只有 ISO/ASME」出图 ③ General Knowledges 挂我方规则包后，它能不能按我们的判据自检 | 装 333 MB 客户端 + 免费账户，拿一个首件跑一遍；**开隐私模式/企业协议再动真实项目** | 这是唯一可能改变「继续自研」判断的东西。**文档已核，但文档不等于运行时行为**（协议规矩：字段描述 ≠ 运行时行为）|
| 2 | **Spectral Labs 的 CSWP 通过**是否可复现、其官方报告原文 | 读其公开报告；对照 CSWP 评分口径 | 0.1% 判据与我们几何门直接可比 |
| 3 | SolidCraft 的 **90/90 oracle 是否能在本机跑通** | `cargo xtask oracle`（需 Rust 工具链）| 我们可能要照抄它的 oracle 结构 |
| 4 | SolidCraft 的**持久命名**实际强度 | 读 `crates/doc/src/face_anchor.rs` + 做「改参数后旧引用是否仍指同一面」实验 | 这是 SolidPilot 至今没做成的事 |
| 5 | `Slacker-LLC` / `q3ds` 消失后，我们台账里引用它们的地方是否需要改 | 全仓 grep 这两个 slug | 台账引用失效会导致误引 |
| 6 | andrewbartels1 的三条修复对我们是否有可直接抄的实现 | 读对应 commit diff | 它已跑过真机（自述）|
| 7 | **MecAgent 价格口径**：价格页 $125/$625 vs 用户指南 $99/$499 | 结账页实测 | 影响采购判断，不影响技术判断 |

---

## 5. 反证检索记录（协议强制）

**搜了什么**：`SolidCraft tangency-labs 争议 被高估 刷星` · `solidcraft CAD rust criticism limitations review` · `solidcraft.io CAD 评测 问题` · `SolidWorks MCP AI agent 2026 最新 项目` · `AI CAD agent SolidWorks LLM 2026 news` · `vibe coded CAD clone 2026 ArtCraft SolidCraft trend`

**搜出什么（命中，按影响排序）**：
1. **第三方明确劝退复杂用途**（hysenlabs）：oracle 不建立与 FreeCAD 的完全几何等价 ⇒ 削弱「它能替代」的想象。
2. **「vibe-coded」定性**（3dprintingindustry / Fabbaloo / HN 22 条评论）：说明代码由 AI 生成，长期可维护性存疑；HN 上有人指出它「很像 Fusion，但不是官方 ArtCraft 应用」。
3. **星数增长曲线异常**（gitdiscover 记 +691/24h；shadowgraph 记 8,531；gitnova 记 11,406；今日 13,016）：增速本身不构成质量证据。
4. **正面但克制的第三方**（hysenlabs）：建议「用它做可脚本化的参数化建模，别当生产级复杂装配 CAD」。
5. **意外收获（推翻我的初始候选池）**：搜出 **MecAgent V2** 与 **Spectral Labs** —— 这两条**不在 GitHub 搜索结果里**，是「其他渠道酌情」捞到的，且是本次唯一真正对着「完整体」的问题回答的东西。**★ 其中 MecAgent 已在第二轮补到一手官方文档（见 §2.3），从「转述」升为「一手」。**

**第二轮反证（针对 MecAgent 自己）**：读了它的官方「暂时不能做什么」与工程图设置页，**它自己否掉了**「能替代合规出图」这个想象——标准只有 ISO/ASME Y14.5、明确不保证法规合规、验证留给用户。⇒ 我原本「它可能让我们停研」的假设，被**它自己的文档**反驳掉了。

**0 条命中的方向**：没有找到任何「SolidCraft 复现失败/benchmark 造假/安全事件」的实质反证。它的问题主要是**能力边界**，不是**诚信问题**。

---

## 6. 覆盖自查（两本账 · 账一）

**回答三个数（协议强制）**：

### 6.1 候选池有多少？我登记了几个？

| 检索口径 | 命中总数（`gh api search`，2026-11-02） |
|---|---:|
| `solidworks in:name` | 4,849 |
| `topic:solidworks` | 948 |
| `solidworks … created:>2026-08-01` | 1,327 |
| `solidworks … pushed:>2026-09-15 stars:>10` | **30** |

从 1,327 个「三个月内新建」里人工筛出与本命题相关的新对象 **约 30 个**，去重后 5 线分配。**登记结果**：

| 线 | 出卡 | 具名剔除 | 小计 |
|---|---:|---:|---:|
| A 驱动 SolidWorks 的 MCP/agent | 10 | 4 | 14 |
| B Skill 包路线 | 4 | 13（含 1 个并入 D 线） | 17 |
| C 换底座 | 2 | 0 | 2 |
| D 不装 SW 读 SLDPRT | 5 | 2 | 7 |
| E 已登记台账复核 | 0（改台账结论） | 2（404） | 2 |
| 商业闭源（其他渠道） | 0（JSONL 记 2 条） | 0 | 2 |
| **合计** | **21 张新卡** | **21** | **44** |

⇒ **44 = 21 张卡 + 21 具名剔除 + 2 条商业侧 JSONL 记录**，账平（每个被剔除的都写了理由，见 JSONL 的 `verdict=不适用` 行）。

### 6.2 登记的里，`depth` 分布是什么？几个只到 `metadata`？

`jsonl` 侧车 31 行（含 6 条非本批对象）的深度分布：

| depth | 条数 | 占已登记 |
|---|---:|---:|
| `tested`（本机真跑过它的代码/单测） | **7** | 23% |
| `source`（读了源码或官方文档） | **14** | 45% |
| `readme`（只读 README 或媒体转述） | 4 | 13% |
| `metadata`（只看星数/许可/最后提交） | **6** | 19% |

**只到 `metadata` 的 6 个，全部 `verdict=不适用` 或 `待核`**，没有一个被判「借鉴」——这符合协议的「`depth=metadata` 不得判借鉴」禁令，也说明**判「借鉴」的 14 条全部至少读到了源码**。

### 6.3 反证节写了多少字，真命中几条？

§5 共 **6 组查询词**，**命中 5 条实质反证**（第三方劝退、vibe-coded 定性、星数曲线异常、正面但克制的评测、以及推翻我初始候选池的 MecAgent/Spectral Labs），**0 条**「造假/复现失败/安全事件」类反证。见 §5。

### 6.4 已知遗漏（主动交代）

1. **两路并行探查员（B、D）在收尾阶段失败**，未交收尾报告。我按磁盘实际产出接手：B 线缺的 2 张深挖卡（`27painter`、`LTGOz`）由我补写；D 线的 6 张卡与 2 份分析（`dup-report.md`、`token-cost.md`）已落盘，我做了复核。
2. **D 线 3 个快筛对象未出卡**：`monozukuri-ai/sldkit`（许可 NOASSERTION）、`djbarrow/freecad_solidworks_plugin`（LGPL，与我方离线读件相关）——JSONL 里记 `待核`；`blussyya/solidworks-converters` 已出卡。
3. **B 线 13 个快筛全部未单独出卡**，其判断依据是 `dup-report.md` 的重复度实测 + `token-cost.md` 的成本实测（覆盖 17–18 个仓库），不是逐个读过源码 ⇒ 这一批的证据等级只到 `readme`。
4. **一个项目都没在真机跑过**（业主口径）⇒ 一切「建模能力」结论止步 `source`。
5. **Commercial 侧只有媒体转述**，无一手产品文档。

---

## 7. 复核总账（账二 · 抽样 ≥10%）

**方法**：对本报告里可机验的量化断言重新跑一遍命令（2026-11-02 晚间）。

| # | 断言 | 复核结果 | 判定 |
|---|---|---|---|
| 1 | SolidCraft MCP 工具数 = 21 | 重算 `[regex]'\btool\("...'` ⇒ **21** | 确认 |
| 2 | SolidCraft oracle case = 90 | `(Get-ChildItem tests\oracle -Directory).Count` ⇒ **90** | 确认 |
| 3 | SolidCraft 双许可 MIT OR Apache-2.0 | 两个 license 文件在位（`LICENSE-APACHE` 10,351 B / `LICENSE-MIT` 1,101 B） | 确认 |
| 4 | SolidCraft Rust 1,509 文件 / 734,867 行 | 重算 ⇒ **1,509 / 734,867** | 确认 |
| 5 | `q3ds` 与 `Slacker-LLC` 均已 404 | 两个 `gh api` 均返回 HTTP 404 | 确认 |
| 6 | LTGOz `verify()` 在 `sw_bridge.py:645`，`tol=0.01`、`golden_iou=0.99` | `Select-String 'def verify\('` ⇒ **L645**，签名含两个默认值 | 确认 |
| 7 | 27painter 的 token 三角 83,732 / 23,411 / 107,143 / 839 | `README.md` 的 **L41 / L45 / L48-49 / L281 / L398** 逐条命中 | 确认 |
| 8 | **B 线的重复度账**：报「24 组 / 50 文件，逐字节相同（SHA-256）」 | **错误（2 处）**：① 报的哈希值 `b710072027b9` 复现不出来，真值是 `303ef103d3b2`；② 口径不是「原始字节」——`dup_scan.py` 用 `Path.read_text()`，**换行符被归一后才哈希**，所以它证明的是「忽略换行后内容相同」 | **错误 + 已改正** |
| 9 | 我据此重算的干净口径：第一方、非空、跨仓逐字节相同 = **24 组 / 52 文件** | 重算脚本排除 `node_modules`/`third-party-patched`/`obj`/空文件/许可证样板 ⇒ **24 / 52**；并按仓库对列出 15/8/2/2/1 | 确认（本报告 §9.2 已改） |
| 10 | 「`e3b0c44298fc` 是空文件哈希」 | 它是 SHA-256 空串值；该组 24 个文件全是 0 字节 `__init__.py` 与 `obj` 残留 ⇒ 必须排除 | 确认 |
| 11 | 本批新增卡片数、全库 71 张、门禁 0 问题 | 收口自查时发现我自己写的是「22 张」——**D 线是 5 张不是 6 张**（`openswx` / `sldprt-format-research` / `solidworks-converters` / `sld2step` / `sw-rs`）。实测 `50 + 21 = 71` 与门禁读数一致 ⇒ 正确值 **21** | **错误（我自己的加法）+ 已改正** |
| 12 | JSONL 31 行、6 个必填字段齐、无重复 id | 脚本校验 ⇒ `missing: none` / `duplicate ids: none` | 确认 |
| 13 | **MecAgent「可能是完整体」**（我第一轮的判读） | 读官方 §1.6「暂时不能做什么」与 §6.7「制图标准只有 ISO 或 ASME Y14.5」⇒ **它自己否掉了这个假设**。判定从「待核」改为「可买作底座、不能停自研」，证据从媒体转述升为一手官方文档 | **判定被自己修正**（非计数错误，是结论修订）|

**错误率**：抽查 **13 条**，**错 2 条**（第 8 条来自并行探查员的脚本、第 11 条是我自己的加法）+ **1 条结论修订**（第 13 条）⇒ **事实错误率 15.4%**。

**必须让读者看到的三点**：
1. 第 8 条错在**判据的措辞与哈希值**（结论「skill 包互相复制」成立），来自并行探查员的自动化脚本；我照抄进报告没当场重算，**这是我的方法错误**。改正后数字接近（24 / 52），但**性质不同**：原口径会把「只差换行符」和「第三方依赖」也算成复制。
2. 第 11 条是我自己的算术错（把 D 线 5 张写成 6 张）——**收口自查时靠「50 + N 是否等于门禁读数」这一条交叉验算抓到的**。教训：**卡片数这类「我数过」的数字，必须用门禁读数反算一次**。
3. **第 13 条是我自己的结论被推翻**：第一轮我把 MecAgent 当作「唯一可能让我们停研的东西」，第二轮读它自己的文档发现它公开不承担法规合规与验证 ⇒ **它不是那个东西**。这条比任何计数错误都重要，所以单列。

---

## 8. 建议我们下一步做什么（按性价比，五件）

1. **今天就做（零成本）**：给现有建模工具加 `expect_volume_mm3` / `expect_bbox_mm` 可选参数（照 SolidCraft 的 0.2% / 0.05 mm 默认），把回读从「事后单独查」变成「判据跟着调用走」。
2. **本周做**：把 `tests/oracle/` 那套结构搬过来 —— 每件一个 `recipe` + 一个 `expected`（解析闭式值）+ 可选 `reference.stl`，跑 `compare_step`。我们已有 `scripts/sw_net_blend.py` 这类几何读取，缺的是**期望值的来源与回读闭环**。
3. **顺手打开一个开关**：上游**已经自带** `SW_MCP_DISCOVERY=search`（发现式工具表）。66 个工具的 `tools/list` 从 **23,411 tokens** 压到 **474**——我方 439 个工具，这是最大的一笔上下文节省，且不需要写代码。
4. **跑一条自查命令**：按 `infei12306` 的诊断法查我方是否也有类型库版本错配（`LoadRegTypeLib` 注册版本 vs `.tlb` 实际版本）。若同病，这能一次性解释一批「makepy 时好时坏」的怪事。
5. **做一次有边界的试用（不是采购评估）**：MecAgent 免费版只验三件事——① 它是不是真在 SolidWorks 原生 API 上建特征 ② 用我们自己的空白模板能否出我们要的图 ③ General Knowledges 挂我方规则包后它能不能按我们的判据自检。**结论很可能不变**（它公开说不做法规合规），但这一步能把「我们为什么要继续自研」写成**对照实验**，而不是立场。

**反过来说：不该做的**——不要再从头写「让 agent 会建模」的那一层。MecAgent 已经把它商品化（含 STEP-to-CAD 重建特征树），SolidCraft 用开源方式重做了一遍并给了 oracle。**我们的钱和力气应该只花在判据与规范合规上。**

---

## 9. A / B / D 三线回收

### 9.1 A 线 · 驱动 SolidWorks 的 MCP 服务端（6 深挖 + 4 快筛）

**这批的共同形状：都在往「回读验证」上叠，而且各有各的解法。** 与三个月前的四家（`docs/survey/cards/sw-*.md`）相比，明显的进步是**没人再满足于「调用成功 = 建好了」**。

| 项目 | 工具数 | 它把「验证」做成了什么 | 最值得抄的一件 |
|---|---:|---|---|
| `hjbaard/SolidWorks-MCP`（MIT，实测） | **87** | **每个建模调用都返回实测体积/质量/包围盒**；专用 STA COM 线程；「失败即回滚到调用前特征树」的守卫 | **回滚守卫**：失败不留脏特征树 |
| `kumar1441/forge_ai`（MIT，读码） | — | **`GroundTruth` 237 个按命令拆分的独立测量文件**，明写与执行管线零共享代码；每条命令回 `Verified` 布尔，**验不过 fail-closed** | **独立复算教义**：验证器不许复用执行器的测量代码 |
| `raylanlin/Millwright`（Apache-2.0，实测） | **87** | 每个改动类工具**前后各拍一张几何快照并按类别断言 ΔV 的方向**；`build_part` 一次提交整件计划 | **ΔV 方向断言**（比绝对值容差更抗「碰巧对了」）|
| `soheil-mp/solidworks-mcp`（MIT，读码） | **161（最宽）** | 几何引用是联合类型（`id` / 声明式查询 `where` + **必填命中数 `expect`** / 最近点 / 名字），**命中数不符抛 `EntityAmbiguous` 并列出候选** | **选择歧义必须显式失败**：不猜「你要选哪一个」 |
| `HarrierPigeon/Solidworks-MCP-Server`（MIT，读码） | **95** | 每个特征/草图/实体发稳定 ID（`feat:`/`sketch:`/`comp:`）；**把面编号画在截图上让模型照着点** | **视觉化选择**：让模型看图选面，而不是猜坐标 |
| `arthurle3210/SwpilotCLI`（读码） | 不发工具 | **路线最不同**：把 Claude Code / Codex CLI 嵌进 Task Pane，agent 自己写 C# 小工具编译运行，干完把可复用的提升进工具库 | **agent 自建工具库**（工具是产物，不是前提）|
| `Robusr/Vulcan`（GPL，读码） | 窄 | LLM 只输出受控 JSON 特征树，执行器完全确定性；**没有任何回读验证**，还留了 `SendKeys` 兜底 | 反例：受控 DSL 讲得最清楚，但覆盖面与验证都不足 |
| `infei12306/solidworks-bridge`（MIT，读码） | 15 子命令 + 代码口 | 导出结构判据（STEP 头 `ISO-10303-21;` / STL 字节算术）；**诊断出「类型库版本错配」**（注册表 21.0 vs `.tlb` 33.0 ⇒ `TYPE_E_LIBNOTREGISTERED`），正解是按路径 `LoadTypeLib` + 私有 stub + ROT attach | ★★★ **一条命令可查我方是否同病**；另实测「模态框存在时 150/150 并发调用仍成功」（阻塞但不拒绝）|
| `qdaia/Auto-SolidWorks`（MIT，读码） | 32 阶段工具 | 唯一带 **IR**（`src/CadModeling.Ir/` 22 文件）且执行推到独立进程；图纸→识别→尺寸绑定→编译→建模→回读；「回执三态（完成/失败/**未知**）」 | **「阶段工具」范式** + 把「未知」当一等状态（我方若要收敛 439 工具，这是唯一现存的替代样本）。★ lease/persistent references 只在文档声明、代码未核 |
| `muerus/SolidWorks-Python`（MIT，实测 31 passed） | 0（嵌入式） | 把 **CPython 嵌进 SW 进程**，从架构上消掉「单源 COM」；`with model.batch()`（静音 UI + 一次重建 + 异常也恢复）、`25 * mm` 单位对象 | 架构上它是单源 COM 唯一的结构性解法样本；但崩溃即带走 SW，代价我方不能接受 |

**A 线的结论**：三个月里这条线**没有人做出「完整体」**，但**「验证」这件事被四家分别解了一半**：
- `forge_ai` 解了「验证器与被验对象独立」；
- `hjbaard` 解了「失败回滚」；
- `Millwright` 解了「改动的方向性断言」；
- `soheil-mp` 解了「选择歧义显式失败」。

**这四件拼起来，正好是我们缺的那一层。** 单抄任何一家都不够，四家合起来才是完整答案。

**A 线四件套横切（协议要求的 Q2 逐条答复）**：

| 难题 | 三个月内的真实进展 | 谁做得最好 |
|---|---|---|
| **持久引用** | **没有一家用持久拓扑 ID 解决**。四家独立收敛到「每次用谓词重查」（hjbaard 方向+点 / HarrierPigeon 描述谓词+面积序 / SwPy 链式过滤 / soheil-mp 谓词+命中数断言）。差别只在**选错时怎么表现**：**只有 soheil-mp 会失败并列出候选**，其余会「挑最像的那个」继续 ⇒ 静默选错 | `soheil-mp` 的 `EntityRef{where, expect}` |
| **回读验证** | 从「调用成功」升级到「几何对不上就失败」，四档并存 | `forge_ai`（独立第二实现 + fail-closed）> `soheil-mp`（体积方向 + 回滚）≈ `Millwright`（分类 ΔV + 完备性门禁）> `infei`（导出文件结构）> `hjbaard`（只测量、判据外包给模型）|
| **事务式建模** | **只有两家有真回滚**（特征集合差 + 删本次新增） | `hjbaard`、`soheil-mp`；Millwright 是「确认卡 + 改前备份」（救文件不救步骤）|
| **单源 COM 互斥** | 全部停在**进程内一档**（单 STA 线程/单队列）。结构性解法只有 SwPy（COM 所有者唯一，外部送代码） | `muerus/SolidWorks-Python`（架构消解）；反例三家：HarrierPigeon / SwpilotCLI / Vulcan 各自多连 |

**Q3 工具面与粒度（实测计数）**：MCP 服务端 4 家（soheil-mp **161**、HarrierPigeon **95**、hjbaard **87**、qdaia **32 阶段工具**）；桌面应用 2 家（Millwright **87**、forge_ai **270**）；CLI 2 家（SwpilotCLI 36 目录、infei 15 子命令 + 代码口）；嵌入式宿主 1 家（SwPy 0 工具）。
⇒ **「一动词一工具」仍是主流（4 家），但出现了三种新档：整件计划口（Millwright `build_part`）、阶段工具 + IR（qdaia）、链式 Python API（SwPy）。** 我方若要给 439 个工具收敛，**qdaia 的「阶段工具」是唯一现存的替代范式样本**。

**A 线额外副产品（可直接进我方台账）**：`kumar1441/forge_ai` 的 `docs/SOLIDWORKS-GOTCHAS.md`（274 行）与 `infei12306` 的 `REFERENCE.md`（196 行）是两份与我方 `docs/known-facts.md` / `docs/dead-ends.md` 高度重合的**外部坑表**，且三处独立来源（含 `LTGOz` 的 `api-pitfalls.md`）指向同一批事实（类型库签名不可信、VARIANT 三规则、ROT 陷阱、中文本地化名、`SketchTrim` 成功返 False）⇒ **交叉验证价值高，应优先并入我方台账。**

### 9.2 B 线 · Skill 包路线（核心结论：**大部分是同一份东西的复制**）

**实测重复度**（`D:\swagent-2026Q4\dup-report.md` 由 B 线脚本 `dup_scan.py` 产出；★ 复核后我**重算了口径**，见 §7 账二第 3 条）：

**复核后的干净口径**（排除 `node_modules`/`third-party-patched`/`obj`/空文件/许可证样板；命令见 §7 账二）：

| 判定 | 组数 | 文件数 |
|---|---:|---:|
| 跨仓**逐字节完全相同**（第一方、非空、非样板） | **24** | **52** |
| 含许可证/README 样板 | 25 | 57 |
| 按 B 线原口径（文本换行归一后） | 74 | 194 —— **其中 72 组只是换行符不同，且多为 `js-yaml` 等第三方依赖**，不能算「skill 包互相复制」 |

**谁在复制谁**（逐字节相同的共享文件数）：

| 仓库对 | 共享文件数 | 性质 |
|---|---:|---|
| `tian-yu200__dsh-solidworks` ↔ `tian-yu200__solidworks-cad-skill` | **15** | **同作者**同一份 `mcp-server-solidworks` 的两份拷贝 ⇒ 候选池虚增 |
| `GaoFei-Max__DSH_SW` ↔ `LU0220-code-pro-max__dsh-solidworks-modeling` | **8** | 不同作者，含 `swapi.py`(313 行)、`sw_bridge.py`(186 行)、`SKILL.md`(203 行) |
| `GaoFei-Max__DSH_SW` ↔ `fyjgtddco__DSH-SW-and-CAD` | 2 | 复用同一批 examples |
| `LU0220-code-pro-max__dsh-solidworks-modeling` ↔ `fyjgtddco__DSH-SW-and-CAD` | 2 | 同上 |
| `hxyulin__sw-rs` ↔ `schwitters__openswx` | 1 | 同一个 `LICENSE`（D 线两个工具共享上游许可文本，不算抄袭）|

⇒ **17 个被扫的 skill 包里，独立实现的数量远少于 17**：真正互相复制的是 `GaoFei-Max / LU0220 / fyjgtddco` 三家（8+2+2 个文件），其余是作者自复制或许可证样板。**这条线的主要产出是提示词包装，不是新能力。**

**成本实测**（`D:\swagent-2026Q4\token-cost.md`，`cl100k_base`）：

| 项 | tokens |
|---|---:|
| skill 入口文档（17 个，最小/最大） | 609 / 7,190 |
| **直连 SolidWorks MCP 的 `tools/list`（66 工具）** | **23,411** |
| 直连 AutoCAD MCP 的 `tools/list` | **83,732** |
| 某包用 discovery 模式后的常驻入口 | **839** |

⇒ **这是本轮最硬的一个成本数字**：我们自己 **439 个工具**，若照直连模式进上下文，量级会在 10 万 tokens 以上；而「少入口 + 运行时发现」能压到三位数。**这解释了为什么 SolidCraft 只给 21 个工具。**

（上表三项 MCP 读数为 `27painter__dsh-sw-cad/README.md` 的自述，**转述，非本机实测**。）

**B 线四条自出卡的结论**（各有独立价值，不是纯噪声）：

| 项目 | 星 | 它真正提供的东西 | 判定 |
|---|---:|---|---|
| `delancy827/solidworks-skills`（MIT） | 152 | 双形态包（skill + 自带 27 工具 MCP）；主体价值是**一份 SW 2024 COM 双接口（makepy 早绑定 + 动态 IDispatch）怪癖台账** | 取其台账做交叉验证，不取工具面 |
| `LTGOz/solidworks-agent-skill`（MIT） | 3 | **JSON 配方 + trimesh 断言层**（水密/体积/包围盒/golden-IoU，断言不过整条配方失败）；附 12 节 COM 坑手册；只支持 SW2023 | ★ 借它的「断言对象是导出物」与 **IoU 形状判据** |
| `27painter/dsh-sw-cad`（MIT） | 6 | **配置层 + token 预算**：把上游两个 MCP 装进 DSH/Codex，用上游自带 discovery 把 107,143 → 839；钉版本 commit + ProgID 探针 + 失败即抛 | ★★★ 立刻打开上游自带的 `SW_MCP_DISCOVERY=search` |
| `GaoFei-Max/solidworks-build-part-from-drawing`（MIT） | 15 | **零脚本的两阶段提示词纪律**：尺寸账本（禁止按像素猜）+ 特征计划 + 一次确定性构建 | 借这条纪律，无可搬代码 |

### 9.3 D 线 · 不装 SolidWorks 读写 SLDPRT（**本轮第二个确定性收获**）

**核心问题「能不能替代开 SolidWorks 回读」的答案是：部分能，而且有一条已经在我们自己的文件上复现读数。**

| 项目 | 读到什么粒度 | 能不能算 | 结论 |
|---|---|---|---|
| `blussyya/solidworks-converters`（**Apache-2.0**，实测） | 内嵌 **Parasolid B-rep** | **精确积分出体积**，`--step` / `--stl` / `--volume` 三命令；**能在我们自己的文件上复现 SolidWorks 读数** | **可直接用**（零依赖纯 Node）|
| `dsandall/sld2step`（AGPL，实测） | Parasolid → 逐节点灌 **OpenCASCADE** 重建 B-rep | `BRepCheck_Analyzer` 判有效、按体积符号判朝向；出 STEP AP214 + glTF | 只读思想（AGPL）|
| `schwitters/openswx`（MIT，实测） | 容器 + B-rep 拓扑（五子库） | **质量属性是从文件里「抄」的，不是自己算的** | 作参照，不作 oracle |
| `hxyulin/sw-rs`（MIT，实测） | 元数据 + **存盘显示网格**，明确不做 B-rep | 读出的 SW 存盘质量属性 | 诚实性机制可抄（`limitations` 字段）|

**D 线的结论**：`blussyya/solidworks-converters` 给出了**离线拿到体积的路**，而且 Apache-2.0 可并入；但它的覆盖面（只算体积、一部分几何）是否够撑起 E1–E7 的几何门，**未验**。

⚠ **许可红线**：同一作者的 `blussyya/sldprt-format-research` 是 **CC-BY-SA-4.0**（传染性）——**只读思想，绝不抄其文本或代码**。

### 9.4 门禁状态（收口实测）

```
python -B scripts\check_survey_cards.py
⇒ 卡片 71 张 · 问题 0 处
⇒ [PASS] 全部卡片满足四条验收判据
```

这是 `release_check` 的 `survey_cards` 硬门禁同一判据。**收口前曾 26 处红**（D 线 5 张卡的量化断言行没有可追溯引用形态），已逐行补齐 `来源：`/`文件:行` 形态后转绿；B 线两张由我补写的卡也同样过门。

**全仓门禁**（`python -B scripts\release_check.py`，2026-11-02 收口时实跑）：

```
EXIT=0    missing: []
```

两条非 `pass` 的读数，如实列出：
- `provenance` = `skipped`（本轮改动不触发该门）；
- `fact_single_home` = `hits`，**告警级不拦（exit 0）**：`docs\dead-ends.md` 逐字复述事实 230、`specs\202-user-coverage-gaps\recon\verify50\vd50-A-surface.md` 逐字复述事实 303 —— **两处都是本轮之前就存在的文件，不是本次改动引入**。

⚠ **一个环境坑（值得写进工具手册）**：`release_check` 在 **GBK 控制台**下会**假红**——它会调用 `check_s3_blockers.py`，而该脚本 `print("⇒")` 在 GBK 下抛 `UnicodeEncodeError`，父进程把子进程崩溃当成「门禁未通过」，报出「S3 拦截台门禁未通过（台账与验收报告不一致，丢证据了）」这种**完全误导**的结论。实测：同一棵树上 `check_s3_blockers.py` 单跑在 UTF-8 下是 **PASS**。⇒ **跑门禁前先设 `PYTHONIOENCODING=utf-8`**，否则会去查一个不存在的台账问题。

---

## 10. 交付物清单

| 路径 | 内容 |
|---|---|
| [`docs/research/sw-agent-2026Q4/00-brief.md`](00-brief.md) | **L3 任务书七块**（问题、基线、产出格式、证据四档、已判死清单、分线规则、边界声明）|
| [`docs/research/sw-agent-2026Q4/report.md`](report.md) | **本报告**（结论先行 → 分线发现 → 对不上的地方 → 待核 → 反证记录 → 两本账 → 建议）|
| [`docs/research/sw-agent-2026Q4/projects.jsonl`](projects.jsonl) | **机器可读侧车**：**31 行**，6 个必填字段齐（`id`/`url`/`verdict`/`evidence_url`/`fetched`/`depth`），无重复 id，`depth=metadata` 无一条判「借鉴」|
| `docs/survey/cards/sw-*.md` | **21 张新卡片**（A 10 · B 4 · C 2 · D 5），全部过 `check_survey_cards.py` |
| `D:\swagent-2026Q4\repos\` | **39 个克隆**（`--depth 1`，未进仓库，`C:\swprojects\` 零改动）|
| `D:\swagent-2026Q4\dup-report.md` | B 线重复度实测（★ 其口径与哈希值经我复核改正，见 §7 第 8–10 条）|
| `D:\swagent-2026Q4\token-cost.md` | skill 入口与 `tools/list` 的 token 成本实测（`cl100k_base`）|

**判定分布**（`verdict`）：借鉴 **14** · 不适用 **7** · 可选 **7** · 待核 **3**。
**证据深度**（`depth`）：`tested` **7** · `source` **14** · `readme` **4** · `metadata` **6**。
