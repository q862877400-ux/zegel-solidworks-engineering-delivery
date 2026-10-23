# Adam（AI CAD copilot，adam.new）

<!-- survey: class=H; repr=feature-tree; orchestration=human-approve; verify=run-only; deliver=none; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码（云端服务 + 各 CAD 的插件/连接器）。产品主页 https://adam.new ；文档 https://docs.adam.new （索引 https://docs.adam.new/llms.txt ） |
| 许可 | 商业闭源 · 订阅 + 用量额度。三档：Free（$0/月）、Pro、Max；Pro/Max 的具体价格页写「See pricing」，数字未取到（来源：https://adam.new ）。用量按日/周额度计量，见 https://docs.adam.new/admin/billing.md |
| 元数据 | Adam（adam.new，官网自述「Backed by Y Combinator」）· https://adam.new · 取数 2026-10-24（来源：https://adam.new ） |
| 克隆 | 未克隆（闭源，无仓库） |
| 证据等级 | **元数据**（官方主页 + 官方文档站；无源码、无本地实测——服务需账号与已连接的 CAD） |

## 1. 一句话定位

**它不是一个新建模器，而是一个「插进你现有 CAD/PLM 里替你动手」的代理**：官方首页的原话是「Adam is the AI mechanical engineer that works in your CAD, PLM and simulation tools, and hands back finished work.」（来源：https://adam.new ）——注意「works in your tools」，它不提供自己的几何引擎。

- **AI 落在哪一段工序**：**全流程的都摸，但每处都是「改文件」而非「出几何」**——读图纸/BOM/规格、按现有历史改尺寸与特征、加配合、重建、同步 BOM、起草邮件与文档、开始仿真并挂结果（同上）。
- **对本调研最关键的一点**：它**明写支持 SolidWorks**（Windows，经 Desktop Connector）（来源：https://docs.adam.new/integrations/desktop-connector.md ）——这是六家里唯一在文档层面直接点名 SolidWorks 的。
- **它没有自己的建模内核**：所有几何改动都发生在宿主 CAD 里（同 §2）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：任务消息（自然语言）+ **当前打开的设计与当前选择** + 已连接工具里的数据（几何、BOM、图纸、修订、规格）。官方：「Adam can use the open design and your current selection. In your message, still describe the geometry, constraints, and changes that matter.」（来源：https://docs.adam.new/integrations/fusion.md ）
2. **中间表示**：**宿主 CAD 的原生数据模型**——官方 FAQ 描述为「adjusting a dimension, adding a feature, or mating a component while respecting the existing history and references」（来源：https://adam.new ）。没有中间 DSL，没有网格化。
3. **生成**：由云端模型规划改动（官方未披露模型名与版本，「List available models」是 API 端点之一，见 https://docs.adam.new/api-reference/adam-api/list-available-models.md ）。
4. **编排**：**task 制的长任务**。官方定义：「A task is a conversation with Adam and everything produced during that conversation」；任务状态有四态：Running / Needs input / Completed / Scheduled（来源：https://docs.adam.new/guides/core-concepts.md ）。
5. **执行**：**在宿主里执行**——Fusion 走 add-in（Fusion 必须开着）、Onshape 走账号连接（Onshape 可不打开）、SolidWorks/Revit/Blender/SketchUp/Unreal 走 Desktop Connector（必须开着）（来源：https://docs.adam.new/integrations/desktop-connector.md 与 https://docs.adam.new/resources/faq.md ）。
6. **验证**：**重建 + 影响面清单**。官方 FAQ：「It regenerates the model, shows you which downstream features and BOM lines changed, and flags any edit that would break a parent-child relationship instead of forcing a rebuild.」（来源：https://adam.new ）★ 这是本卡最值得抄的一条（见 §3）。
7. **交付**：落在宿主的原生文件里；Files 页可预览/下载/按可用格式导出（来源：https://docs.adam.new/guides/files.md ）。★ 官方**未枚举**具体导出格式（见 §9）。

## 3. 技术方案要点（可迁移的机制）

- **★ 父子关系预检 + 拒绝硬重建**：「flags any edit that would break a parent-child relationship instead of forcing a rebuild」（来源：https://adam.new ）。这是把「编辑会不会把下游搞崩」变成**事前判定**而不是事后修——直接对应 SolidWorks 里最疼的那类失败（改草图 → 特征丢失引用）。
- **下游影响面回显**：「shows you which downstream features and BOM lines changed」——不是只说「改好了」，而是列出「为此变了哪些东西」。这是「改动的可核验清单」。
- **「先解释计划再改」写在文档里**：Fusion 集成页的原话是「For an important edit, ask Adam to explain the planned changes and wait for your approval before applying them.」（来源：https://docs.adam.new/integrations/fusion.md ）——注意它是 **提示（TIP）**，不是强制闸门（见 §5.1）。
- **任务四态把「等人」显式化**：Needs input（「a question or approval is waiting for someone who can respond」）是一个独立状态，而不是超时（来源：https://docs.adam.new/guides/core-concepts.md ）。
- **失败后先去查现场**：官方排障第一条针对「Adam 可能在报错前已经改了东西」——「check the file or record before asking it to try again」（来源：https://docs.adam.new/resources/troubleshooting.md ）。★ 这是「非幂等操作」的正确处置顺序。
- **按宿主能力分层连接**：能云连的就云连（Onshape 不必打开），必须本地跑的就要求本地常开（Fusion/SolidWorks）。官方把这条差异明确写在文档里（来源：https://docs.adam.new/resources/faq.md ）。
- **连接器安全模型**：一次性配对码会过期、按设备配对、可解除配对；自定义 MCP 需 Streamable HTTP 端点（来源：https://docs.adam.new/integrations/desktop-connector.md ）。
- **有 MCP 层**：官方提供 `Adam MCP` 与版本化 REST API（个人 API key）（来源：https://docs.adam.new/mcp/overview.md ）。

## 4. 运行条件与依赖

- **账号与计划**：三档（Free / Pro / Max）；某些模型与推理选项按计划或剩余额度放开（来源：https://docs.adam.new/resources/faq.md ）。
- **用量刷新**：「Daily usage refreshes at midnight UTC. Paid weekly included usage refreshes Monday at midnight UTC.」用尽后降到 Lite 走日额度（同上；细则见 https://docs.adam.new/admin/billing.md ）。
- **CAD 连接**：
  - Fusion：装 add-in，Fusion 与设计**必须开着**（来源：https://docs.adam.new/integrations/fusion.md ）。
  - Onshape：连账号即可，**Onshape 可不打开**（来源：https://docs.adam.new/resources/faq.md ）。
  - SolidWorks：**仅 Windows**，走 Desktop Connector，SolidWorks 与连接器必须开着（来源：https://docs.adam.new/integrations/desktop-connector.md ）。
  - Revit：目前经 Autodesk 的 **Public MCP Server Tech Preview** 支持 Revit 2027（同上）。
- **PLM**：已支持 Arena（items / BOM / suppliers / files / changes）（来源：https://docs.adam.new/integrations/arena.md ）。
- **安全（官方口径）**：SOC 2 Type I 通过；传输 TLS 1.2+、存储 AES-256；每用户沙箱、闲置即停；模型输入在其供应商商业条款下**不用于训练**（来源：https://adam.new ）。
- **网络**：纯云服务（同前）。

## 5. 失败模式与已知限制

### 5.1 ★ 官方逐条限定 / 承认的原文 + 链接

- **「重要改动先等批准」是建议，不是硬闸门**：Fusion 集成页把它写在 `TIP` 框里——「For an important edit, **ask** Adam to explain the planned changes and wait for your approval before applying them.」（来源：https://docs.adam.new/integrations/fusion.md ）。★ 措辞是「你去要求它」，**不是**「它必然先问」。
- **预览不能替代核验**：「Open editable CAD files in their CAD application before approving a design change. The preview may not show feature history or other design details.」（来源：https://docs.adam.new/guides/files.md ）
- **可能「改了一半才报错」**：「If Adam may have changed something before the error appeared, check the file or record before asking it to try again.」（来源：https://docs.adam.new/resources/troubleshooting.md ）——即**非原子**。
- **桌面类 CAD 必须常开**：「Keep Fusion and applications connected through the Desktop Connector open while Adam works with them.」（来源：https://docs.adam.new/resources/faq.md ）
- **SolidWorks 仅 Windows**：「SolidWorks support is available on Windows.」（来源：https://docs.adam.new/integrations/desktop-connector.md ）
- **任务删除不可恢复**：「Deletion is permanent.」（来源：https://docs.adam.new/resources/faq.md ）
- **分享会带出全部附件**：发布任务为只读链接前要「Review the conversation and every attachment first.」（同上）
- **自定义 MCP 的风险自负**：「Only connect servers you trust. Their tools may be able to change files or data on your computer and in other products.」（来源：https://docs.adam.new/integrations/desktop-connector.md ）
- **会话上下文仍需人补**：即使能读当前选择，官方仍要求「In your message, still describe the geometry, constraints, and changes that matter.」（来源：https://docs.adam.new/integrations/fusion.md ）

### 5.2 【宣称】vs【事实】

- 【宣称】「Works with every major CAD platform」（来源：https://adam.new ）。
- 【事实】文档实际枚举的连接为：Onshape、Autodesk Fusion、SolidWorks（Windows）、Revit（经 Tech Preview）、Blender、SketchUp、Unreal Engine（来源：https://docs.adam.new/integrations/desktop-connector.md ）。★ 「every major」未被文档逐一点名支撑。
- 【宣称】「Adam reads your assembly and PLM, and keeps the BOM in sync as the model changes」（来源：https://adam.new ）。
- 【事实】官方承认会「flagging part-number, quantity, and revision mismatches」（同上）——即**报不一致**，不是保证一致。
- 【宣称】「hands back finished work」（同上）。
- 【事实】同页 FAQ 与排障文档都在讲「改了一半」「要你自己核」「预览看不到特征历史」（§5.1）——**finished 由人认定**。
- 【宣称】「Designed from the ground up for IP protection」，SOC 2 Type I（同上）。
- 【事实】SOC 2 **Type 1**（不是 Type 2）；文档未披露模型供应商名单（同上，查不到）。

### 5.3 其他限制

- **连接类故障是已知面**：Fusion add-in 可能加载失败，官方给了 Shift+S → Add-Ins → AdamFusion → Run 的手工兜底路径；云账号会过期，掉线需回 Integrations 重新连接（来源：https://docs.adam.new/resources/troubleshooting.md ）。
- **模型/推理选项受计划约束**：「Some model and reasoning choices require a particular plan or enough remaining usage.」（来源：https://docs.adam.new/resources/faq.md ）

## 6. 对我方目标的可用处（机制层面，含**不能**学什么）

**能学的（这张卡是六家里机制上最贴近我们的）**

- **★ 变更前做父子关系预检、宁可拒绝也不硬重建**：这正是 SolidWorks 参数化最脆弱的地方。我们可以把它落成「改之前先算引用闭包，列出会受影响的特征；有断链风险就拦下并给出替代方案」。
- **★ 改动后输出「下游影响清单」**：不是「我改好了」，而是「改了 X，因此 Y/Z 的尺寸和 W 条 BOM 行发生变化」。这等于给我们每次 AI 改动附一张可核验的差异表。
- **任务状态里显式包含「等人」**：`Needs input` 是一等状态。我们不能靠超时来判断「模型卡住了」，要能表达「在等人批准」。
- **非幂等操作的排障顺序**：报错后**先查现场再重试**，而不是自动重试——这条对 COM 自动化尤其重要（重试一次可能再切一刀）。
- **按宿主能力分层**：能远程就连远程（Onshape），必须本地就要求常开（Fusion/SolidWorks）。我们的 SolidWorks 天然是「必须本地常开」那一类，要有对应的连接健康检查。
- **配对码 + 可解除配对**的设备信任模型：给「本机 COM 桥」这类组件一个可复用的信任设计。

**不能学的**

- **「在你的工具里干活」这套集成架构**：Adam 靠每家 CAD 的官方扩展点（Fusion add-in、Onshape API、Desktop Connector）。我们在 SolidWorks 上只有 COM/Add-in 两条路，且是**单实例**（本仓已知事实 24：多个进程抢同一 COM 连接会死锁）——它的「多工具并存」模型不能照搬。
- **「计划—批准」不设强制**：官方只是 TIP 建议。我们不能学这个松散度——我们的目标要求**硬闸门**（不批准不执行）。
- **预览即验收**：官方自己说预览看不到特征历史。我们不能把「缩略图/截图看起来对」当验收。
- **「finished work」这种交付话术**：不可验收。我们要的是「体积/质量/特征树/引用完整性」这类可算的判据。
- **把 BOM/PLM 纳进来**：超出我们当前目标（参数化建模），且会引入我们无权处理的数据。

## 7. 许可与红线

- **商业闭源**：不抄提示词、不抄 UI/文档文案；可引其**行为契约与限制**（带 URL）。
- **数据红线**：官方称模型输入不用于训练、企业计划数据私有（来源：https://adam.new ）。这与我方数据纪律一致；但**具体供应商与留存期限未披露**，不能据此做合规承诺。
- **连接器红线**：官方自己警告自定义 MCP 服务器可改本机文件——我们若做同类桥接，必须同样默认不信任第三方端点。
- 本卡未使用任何第三方对 Adam 的评测。

## 8. 证据清单

- https://adam.new —— 官方主页与内嵌 FAQ：定位（在你的 CAD/PLM/仿真工具里工作）、读图纸/BOM/规格、BOM 同步与差异提示、**父子关系预检与拒绝硬重建**、邮件/文档类动作「pause for approval」、安全（SOC 2 Type I、TLS 1.2+、AES-256、沙箱、不用于训练）、三档计划。
- https://docs.adam.new/llms.txt —— 文档总索引：任务/项目/文件/集成/MCP/API/计费/排障的全部分页清单（本卡据此逐页取证）。
- https://docs.adam.new/guides/core-concepts.md —— 任务四态（含 Needs input）、文件与输出、团队角色、集成三类、Memory。
- https://docs.adam.new/guides/files.md —— Files 页与导出；**「approving a design change 前要在 CAD 里打开原件，预览可能看不到特征历史」**。
- https://docs.adam.new/integrations/desktop-connector.md —— Desktop Connector：支持的宿主清单、SolidWorks 仅 Windows、Revit 经 Autodesk Public MCP Tech Preview、自定义 MCP 需 Streamable HTTP、配对码/解除配对、第三方服务器风险警告。
- https://docs.adam.new/integrations/fusion.md —— Fusion add-in 安装与故障兜底；**「重要改动先要它解释计划并等你批准」写作 TIP**；仍要求人描述几何与约束。
- https://docs.adam.new/resources/faq.md —— 哪些 CAD 必须常开、Onshape 可不开、模型/推理受计划限制、任务删除不可恢复、公开分享需先审阅。
- https://docs.adam.new/resources/troubleshooting.md —— 排障：**「报错前可能已改过，先查现场再重试」**、Fusion 离线、连接器离线、云账号过期。

## 9. 未确认事项

- **Pro / Max 的价格与额度数字**：主页只写「See pricing」，本次未取到价目（查不到）；日/周额度的具体数值也未见（细则页 https://docs.adam.new/admin/billing.md 未逐字核读）。
- **模型供应商与型号**：官方只说「Settings → Billing 可看计划与用量」，未列模型名单（查不到）；API 有 `list-available-models` 端点，但未调用。
- **导出格式清单**：Files 页说「choose an available export format」，但**未枚举**（查不到）——故本卡 `deliver` 取 `none`。
- **「父子关系预检」的实现口径**：官方未说明它如何判定（引用闭包？特征 ID？）——只在 FAQ 里给了行为描述。**未在真机验证**。
- **它到底怎样驱动 SolidWorks**：文档只说经 Desktop Connector + 需常开；底层是 COM、Add-in 还是其它，**未披露**。
- **审批是否可强制**：官方把「等批准」写成建议；是否存在可配置的强制审批模式，**未确认**。
- **`verify=run-only` 的判据**：官方只描述「重建 + 展示下游变化 + 标记断链」，未描述任何几何正确性校验，故本卡按「只有重建这一道自动核查」记。
