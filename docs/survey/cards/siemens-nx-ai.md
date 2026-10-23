# Siemens NX（Designcenter X NX）的 AI 功能：Copilot / Select Similar / PMI 预测

<!-- survey: class=I; repr=feature-tree; orchestration=none; verify=none; deliver=none; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码（NX 内置）。官方发布博客 https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/ ；Copilot 使用说明 https://blogs.sw.siemens.com/designcenter/designcenter-x-nx-tips-and-tricks-copilot/ |
| 许可 | 商业闭源 · **订阅内置 + 可选加购模块**。Select Similar / Selection Prediction 属「Mach3 Product Design 与 Mach3 Industrial Design 包」的标准功能；自定义 ML 模型生成是「optional add-on module」（来源：https://blogs.sw.siemens.com/nx-design/improve-productivity-and-usability-with-nx-core-architecture-upgrades-in-latest-release/ ） |
| 元数据 | Siemens Digital Industries Software · https://www.siemens.com （产品线 Designcenter X NX，原名 NX / NX X）· 取数 2026-10-24（来源：https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ ） |
| 克隆 | 未克隆（闭源，无仓库） |
| 证据等级 | **元数据**（Siemens 官方博客 / 官方 Designcenter 博客；无源码、无本地实测——需 NX 许可） |

## 1. 一句话定位

**把 AI 全部押在「人已经在做的那几步」上，一步也不替人做设计**：一块是 Copilot（把官方文档摘要成回答，并把命中的词变成可直接点的**命令入口**）；另一块是命令内的 ML 判别（相似面/边识别、选择预测、PMI 注释平面与模型视图预测）。官方对此的总纲是一句话——「they're designed to amplify your expertise, not replace it」（来源：https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/ ）。

- **AI 落在哪一段工序**：**选择（selection）** + **PMI 标注（annotation）** + **操作导航（command discovery）**。这三处都在「特征建好之后/建立过程中的人机交互」上，不在「生成几何」上。
- **明确没有的**：概念生成、草图生成、特征生成、装配求解、仿真、出图——官方博客通篇没有任何「AI 生成几何」的表述（同上 URL）。
- ★ 本卡的 `class=I` 只覆盖 Copilot 那一半；Select Similar / PMI 预测是「命令内的 ML 判别」，既不是助手也不生成几何，属混合型（见 §9）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：
   - Copilot：自然语言问题 + **最近用过的命令**（官方：「Copilot does not access personal user data, but it does consider recent commands you have used within your session.」，来源：https://blogs.sw.siemens.com/designcenter/designcenter-x-nx-tips-and-tricks-copilot/ ）。
   - Select Similar：用户先选中若干面/边 + **灵敏度区间（sensitivity range）**。
   - PMI 预测：待标注的 PMI 对象集合。
2. **中间表示**：**NX 自己的拓扑实体（面/边/特征）与 PMI 对象**。没有引入外来 DSL、没有网格中间态。
3. **生成**：
   - Copilot：**文档摘要 + 命令映射**。官方原话「It's a conversational user interface that answers your questions by summarizing information from our documentation.」，且「everything will be translated into domain-specific commands」（来源：https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ ）。
   - Select Similar：**几何相似性匹配结果**（一批面/边）。
   - PMI：**注释平面定义 / 模型视图**的预测值。
4. **编排**：**none**。没有代理循环、没有多步计划——Copilot 的产物是人可点的链接。
5. **执行**：**由人点**。官方：「Words that are highlighted within a response … are direct links to commands in Designcenter NX. Hovering over them with your cursor will display the path to the command and highlight them with a red box」（来源：https://blogs.sw.siemens.com/designcenter/designcenter-x-nx-tips-and-tricks-copilot/ ）。★ 这是「引导到命令」，不是「执行命令」。
6. **验证**：**由人做**。Copilot 的每条回答带编号来源（「The numbers are sources used when generating the responses. You can access these sources by scrolling down to the bottom of the response and clicking on them. This makes it easier to verify the information」）（同上）。Select Similar / PMI 的预测结果官方未描述任何自动校验环节。
7. **交付**：**无独立交付物**——改动落在 NX 模型本身（批量 blend/chamfer/pattern、PMI 对象）。无 STEP/图纸类交付能力声明。

## 3. 技术方案要点（可迁移的机制）

- **「答案里的每个名词都是一个可点的命令」**：这是本卡最值得抄的一条——把帮助文本从「读」升级为「可执行入口」，且悬停即显示命令路径 + 红框高亮（来源：https://blogs.sw.siemens.com/designcenter/designcenter-x-nx-tips-and-tricks-copilot/ ）。
- **「文档 → 命令」的映射是产品能力，不是提示词技巧**：官方说「everything will be translated into domain-specific commands」（来源：https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ ）。
- **按最近命令预测下一步**：官方明确把 Copilot 的建议与 NX 既有的 Command Prediction 类比——「Copilot considers the recent commands you have used to anticipate what questions you might have next」（来源：tips-and-tricks 同上）。
- **相似性检索要暴露「灵敏度」这一个旋钮**：官方设计成「选中 → 调 sensitivity → 找全部匹配」（来源：https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/ ）。★ 可迁移点：**ML 检索必须给人一个可调的宽严档**，否则误选无法收敛。
- **相似性结果要能直接接批量操作**：官方：「support for bulk operations—like blends, chamfers, or pattern recognition—across geometrically similar regions」（同上）。
- **可复用的「区域」概念**：「You can even define reusable regions to speed up the process when making multiple changes.」（同上）
- **ML 模型可分「开箱」与「用自己数据训」两档**：官方在 Selection Prediction 上同时提供 out-of-the-box 与「generate custom selection prediction machine learning models using in-house data」（来源：https://blogs.sw.siemens.com/nx-design/improve-productivity-and-usability-with-nx-core-architecture-upgrades-in-latest-release/ ）。
- **隐私边界写成一句话**：「Copilot does not access personal user data, but it does consider recent commands」（来源：tips-and-tricks 同上）——数据边界用可核验的短句表达。

## 4. 运行条件与依赖

- **宿主**：Designcenter X NX（含「with built-in data management」版本亦可）（来源：https://blogs.sw.siemens.com/designcenter/designcenter-x-nx-tips-and-tricks-copilot/ ）。
- **入口**：搜索栏旁「两个星」图标，点击即在 NX 会话内开一个 Copilot 会话（同上）。
- **许可分层**：Select Similar / Selection Prediction 属 Mach3 Product Design 与 Mach3 Industrial Design 包的标准功能；自定义 ML 模型生成是可选加购（来源：https://blogs.sw.siemens.com/nx-design/improve-productivity-and-usability-with-nx-core-architecture-upgrades-in-latest-release/ ）。
- **Copilot 的独立许可**：官方博客未写它归属哪个包、也未写是否另计费（详见 §9）。
- **依赖云/文档服务**：Copilot 要读「官方文档」作答（来源：core-capabilities 同上）；离线可用性未说明。
- **PMI 预测的部署方式**：「Whether you're using data mining with in-house machine learning models or leveraging out-of-the-box deployment」（来源：https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/ ）——两种模式。

## 5. 失败模式与已知限制

### 5.1 ★ 官方逐条限定的原文 + 链接

以下除非另注，均出自 https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/ ：

- **不替代工程师**：「they're designed to amplify your expertise, not replace it」。
- **Copilot 只做文档摘要**：「It's a conversational user interface that answers your questions by summarizing information from our documentation.」（来源：https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ ）
- **Copilot 只给命令入口，不执行**：见 §2.5 的「direct links to commands」原文（来源：tips-and-tricks 博客）。
- **不碰个人数据**：「Copilot does not access personal user data, but it does consider recent commands」（同上）。
- **相似性检索需要人调宽严**：「Simply select the faces or edges of the feature you need to change, adjust the sensitivity range for your search」（来源：December 2025 博客）——★ 隐含承认：默认参数不一定对。
- **答案好坏取决于提问**：「the quality of Copilot's responses is tied to the quality and detail of your prompts」（来源：tips-and-tricks 博客）。

### 5.2 【宣称】vs【事实】

- 【宣称】「Designcenter X NX Copilot … brings innovation to life by turning natural language into action」（来源：https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ ）。
- 【事实】同一段紧接着的自我定义是「answers your questions by summarizing information from our documentation」；「action」在实现上是「高亮词 = 命令链接，由人点」（来源：tips-and-tricks 博客）。
- 【宣称】「AI-powered recognition, instant results … finds matching faces and edges in no time at all」（来源：December 2025 博客）。
- 【事实】同一段要求人先选种子、再调灵敏度区间；且官方给出的价值表述是「complete operations faster」（相对比较），**未给任何准确率或召回率**（同上）。
- 【宣称】PMI 预测「automated, rapid definition of annotation planes with predictable results based on industry best practices」（同上）。
- 【事实】实现是「uses domain-specific machine learning models to automatically predict and assign」——**是预测**，官方未描述自动校验或拒绝机制（同上）。
- 【宣称】Siemens 官方博客引用行业数据：「Early adopters of AI technologies are reporting time saving on common tasks of more than 40%」（来源：https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ ）。
- 【事实】该数字是**行业平均值**的引述，不与 NX Copilot 的任何实测挂钩（同页无 NX 侧指标）。

### 5.3 其他限制（官方文档层面的空缺，按「查不到」处理）

- **PMI 预测的错误处理**：预测错了怎么办、能否回退、是否记录置信度——官方博客**未提**。
- **Select Similar 的判据定义**：「geometrically similar」的具体度量（曲率？包围盒？拓扑？）**未披露**。
- **Copilot 的文档覆盖面**：只知「our documentation」，范围与更新时延**未披露**。

## 6. 对我方目标的可用处（机制层面，含**不能**学什么）

**能学的**

- **「帮助文本 → 可点命令」**：我们的 AI 输出不应止于文字步骤，应给出**可执行入口**（SolidWorks 侧就是「工具名 + 参数 + 选择器」的结构化卡片），且人能一键确认后执行。这正好落在我们的 human-approve 编排上。
- **「相似检索 + 单一宽严旋钮」**：我们要做「找同类型特征/同规格孔」这类批量操作时，必须暴露一个可调阈值，并把命中集回显给人确认——NX 的做法是现成范式。
- **「相似集 → 批量操作」**：命中之后直接接 blend/chamfer/pattern，而不是让用户逐个点。对应我们「按选择集批量改」的能力设计。
- **「可复用区域」**：把一次相似检索的结果命名保存，供后续复用。
- **「最近命令作为上下文」**：比「猜用户在干什么」更可靠——我们已有「当前选中实体 + 最近操作」这两个原料。
- **ML 模型两档（开箱 / 自训）**：给我们一个明确的产品分层参考：通用能力内置，客户特化另算。

**不能学的**

- **「AI 参与几何生成」这条路它没走过**：NX 的 AI 全部是**判别式**（相似性、预测、检索），没有一处是**生成式几何**。所以本卡不能给我们任何「怎么让模型建出参数化特征」的机制——只能给交互范式。
- **「靠文档摘要驱动 CAD 操作」**：Copilot 的产物是「命令路径」，而 SolidWorks 的 API 调用要 20+ 个参数与 mark 选择语义（本仓已知事实 1/33/36）——文档摘要给不出这个精度。我们必须要**结构化签名 + 参数契约校验**，不能靠自然语言概览。
- **「PMI 预测式自动标注」直接搬**：那是判别式 ML + 行业训练数据；我们没有训练集，且 GD&T 错了比不标更危险。我们只该做**规则校验**（标了没有、基准对不对），不做「预测该标哪」。
- **「不设自动校验」**：NX 这几处 AI 都没有自动验收环节。我们要反着做——每个 AI 动作都要有可核验的后置条件。

## 7. 许可与红线

- **商业闭源**：不抄博客文案、不抄提示词；可引其**机制描述**作设计依据（带 URL）。
- **官方博客是官方渠道但不是产品文档**：`blogs.sw.siemens.com` 的措辞属发布口径（【宣称】），功能细节仍以 NX 帮助为准——本次未取得 NX 帮助原文（见 §9），故本卡把博客表述全部按「官方博客」标注，不冒称「产品文档原文」。
- 不引用任何第三方媒体对 NX AI 的转述（本卡未使用）。

## 8. 证据清单

- https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/ —— 2025-12 发布的 AI 专题：Copilot 定位、Select Similar Faces/Edges（种子 + 灵敏度 + 批量操作 + 可复用区域）、PMI Annotation Plane 与 Model View Prediction、「amplify your expertise, not replace it」。
- https://blogs.sw.siemens.com/designcenter/core-capabilities-whats-new-in-designcenter-nx-core-capabilities/ —— Copilot 的官方定义句（「summarizing information from our documentation」/「translated into domain-specific commands」）与行业 40% 时间节省引述。
- https://blogs.sw.siemens.com/designcenter/designcenter-x-nx-tips-and-tricks-copilot/ —— 使用说明：入口图标、基于最近命令的建议、编号来源、高亮词 = 命令直达链接（悬停显示路径 + 红框）、不访问个人数据、答案质量与提问质量挂钩。
- https://blogs.sw.siemens.com/nx-design/improve-productivity-and-usability-with-nx-core-architecture-upgrades-in-latest-release/ —— 早期三件套：Select Similar Components（ML 形状识别）、Selection Prediction（Mach3 包标准功能、可用自有数据训模型）、NX Voice Command Assist、自定义 ML 模型生成（可选加购）。
- https://blogs.sw.siemens.com/designcenter/whats-new-june-2025-x-essentials/ —— AI Chat Copilot：从官方文档取答案并「includes direct links to launch relevant commands」。

## 9. 未确认事项

- **Copilot 的许可归属与是否计费**：官方博客未写（查不到）。本卡只写「订阅内置」这一笼统口径。
- **NX 帮助原文**：本次只用 `blogs.sw.siemens.com` 的官方博客，**未取得 NX 产品帮助页**（`support.sw.siemens.com`/`docs.sw.siemens.com` 未在本次抓取范围内）。故「PMI 预测无自动校验」这类**否定性结论**只能表述为「官方博客未描述」，不能表述为「官方声明不做」。
- **Select Similar 与 Selection Prediction 的算法与判据**：未披露（查不到）。
- **Copilot 是否有「带做」模式（逐步引导执行）**：tips-and-tricks 博客展示的是「给步骤文本 + 用户自己操作」，未见「助手代执行」的描述；但**是否为未公开能力，未确认**。
- **`class` 的混合性**：本卡用 `class=I` 覆盖 Copilot；Select Similar / PMI 预测属「命令内 ML 判别」，在 A–J 分类里没有对位项。汇总时若要单列，需在 v3 报告中说明这一混合（不由本卡擅自新增类别）。
- **PMI 预测是否覆盖 GD&T 语义还是仅注释平面/视图布置**：官方措辞是「PMI Annotation Plane and Model View Prediction」——只预测**平面与视图**，是否涉及其它 PMI 属性**未确认**。
