# Zoo（原 KittyCAD）Text-to-CAD / Zookeeper

<!-- survey: class=B; repr=code; orchestration=loop; verify=visual; deliver=STEP; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码（Text-to-CAD 模型与 Zookeeper 代理都是云端服务）。产品页 https://zoo.dev ；文档 https://docs.zoo.dev 。官方 v1 博客脚注另注明「应用层（不是引擎）是开源的」：https://github.com/kittycad/modeling-app |
| 许可 | 商业闭源 · 订阅 + 计量。Zookeeper 三档：Free（每月 $10 额度，超出 $0.50/分钟）、Plus（$20/月，含约 400 分钟/月）、Pro（$99/月不限量）（来源：https://docs.zoo.dev/blog/announcing-zookeeper ，该页自述「价格以发布当时为准」） |
| 元数据 | Zoo（原 KittyCAD）· https://zoo.dev · 取数 2026-10-24（来源：https://docs.zoo.dev/machine-learning-api ） |
| 克隆 | 未克隆（闭源，无模型/服务仓库；`modeling-app` 是应用层，不是本卡研究的生成能力） |
| 证据等级 | **元数据**（官方文档/官方博客/官方 API 参考；无源码、无本地实测——服务要账号与付费额度） |

## 1. 一句话定位

**把「CAD 建模」当成「写代码」来生成**：模型的中间表示不是网格、不是特征树序列，而是一份真正的程序（KCL 源码），由云端几何引擎执行；Zookeeper 是套在这套栈外面的对话式代理，按「计划 → 调工具 → 看结果 → 改计划」的循环干活（来源：https://docs.zoo.dev/research/zookeeper ）。

- **AI 落在哪一段工序**：概念 + 草图 + 特征 + 参数化重建（**单一零件**为主）。官方工具清单覆盖 `write_kcl_file`（写特征级代码：草图/拉伸/旋转/阵列/布尔/变换）、`execute_project`（执行建模）、`review_snapshot_of_project`（多视角复核）、质量特性计算（来源：https://docs.zoo.dev/research/zookeeper ）。
- **明确覆盖不到**：装配配合、工程图/GD&T、仿真、逆向重建（逐条见 §5.2）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：自然语言提示 + **视口里的当前选择**（面/边/特征）+ 当前项目上下文。官方：「Zookeeper is aware of any bodies, features, faces or edges highlighted by the user, so you can use your mouse to select areas of your model via the viewport to prompt more quickly.」（来源：https://docs.zoo.dev/blog/announcing-zookeeper ）。API 侧的迭代响应里带 `source_ranges`（文件 + 行/列起止），即支持**按源码区间**改（来源：https://docs.zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response ）。
2. **中间表示**：**KCL 源码**。API 响应里 `code` 字段的原文是「The code for the model. This is optional but will be required in the future once we are at v1.」——即**源码在响应里是可选的**，不是必然返回（同上 URL）。
3. **生成**：LLM 直接写 KCL；官方把 Zookeeper 类比 Codex/Claude Code——「powered by LLMs with strict context management」（来源：https://docs.zoo.dev/research/zookeeper ）。
4. **编排**：官方给的 agent 定义是「Plan -> Act (call tools) -> Observe results -> Update the plan -> Repeat until done」（同上）。工具族分五组：项目检视、建模编辑、文档与示例检索、执行与复核、代码卫生（`lint_and_fix_project` / `format_project`）。
5. **执行**：**两级**。先 `mock_execute_project`「quick syntax check without full engine run」，再 `execute_project`「run the model to generate geometry and catch runtime issues」（同上）。
6. **验证**：`review_snapshot_of_project`「check results against criteria from multiple camera views」+ `volume_/surface_area_/mass_/center_of_mass_of_project` 四个可计算指标（同上）。Zookeeper 博客另写「By default, Zookeeper will trigger snapshots to review and validate any modifications it makes」（来源：https://docs.zoo.dev/blog/announcing-zookeeper ）。
7. **交付**：`output_format` 枚举为 `fbx`/`glb`/`gltf`/`obj`/`ply`/`step`/`stl`（来源：https://docs.zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response ）；Design Studio v1 的导出清单为「STEP, glTF, FBX, STL, PLY, and OBJ」（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。

## 3. 技术方案要点（可迁移的机制）

- **代码即唯一真相源**：官方把代码当模型的正式定义，理由是「syntax is terse enough for human reviewable version-control diffs」（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。这让「模型的每次改动」变成可 diff、可 review、可回滚的文本。
- **执行分两级门**：`mock_execute_project`（只查语法，不跑引擎）→ `execute_project`（真跑引擎）。便宜的门先挡掉大量低级失败（来源：https://docs.zoo.dev/research/zookeeper ）。
- **自检是「固定视角的多视图快照」**，不是自由截图：`describe_snapshot_of_project`「render snapshots from set views」，`review_snapshot_of_project`「check results against criteria from multiple camera views」（同上）。
- **把 UI 选择变成上下文**：`read_user_selections`「read the faces/edges/features you've selected」（同上）——省掉「用文字描述你说的是哪个面」这一步。
- **质量特性当验收判据**：体积/表面积/质量/质心，四者可算、可与预期比（同上）。
- **文档检索是工具而不是提示词**：`search_docs`/`get_docs`/`list_all_docs`/`retrieve_kcl_code_examples` 让代理在写之前先查语言参考（同上）。
- **对自己产出的代码做规范化**：`lint_and_fix_project` + `format_project`（同上）——产物风格一致，才有后续可维护性。
- **官方自述为何不走直出 B-rep**：先试过 Text-to-B-Rep，后改走「设计语言 + LLM 写代码」，因为 CAD 是「intent-based workflow」，且「most generative 3D research fails to lead to useful tools for working designers and engineers」（同上）。

## 4. 运行条件与依赖

- **纯云端**：REST + WebSocket + bearer token，文档自述「REST endpoints use predictable URLs, standard HTTP methods, bearer-token authentication」（来源：https://docs.zoo.dev/machine-learning-api ）。无自托管选项（官方未提供）。
- **客户端**：Design Studio 原生 app 覆盖 macOS/Windows/Linux「fully featured」，Web 客户端「currently single-file workflows」（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。
- **账号与付费**：要 Zoo 账号；Zookeeper 与 API 共用同一份月度额度（来源：https://zoo.dev/pricing ）。免费额度用尽后无付款方式会被切断（来源：https://docs.zoo.dev/blog/turning-on-billing-for-text-to-cad ）。
- **版本耦合**：响应里带 `kcl_version`，请求可指定 kcl 版本；`model` 字段区分 `cad` / `kcl` / `kcl_iteration` 三种后端（来源：https://docs.zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response ）。
- **企业定制**：官方称可把客户的 NX/Creo/CATIA/SolidWorks 文件（带特征树）转成 KCL 并做私有微调（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。

## 5. 失败模式与已知限制

### 5.1 官方自己承认的「会错」

- **官方不用「AI」这个词**：「Today's models learn from feature-tree data; they'll misfire, and we'll tune them. ... Until then, it's ML」（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。
- **可编辑的源码不是必然有**：`code` 字段「This is optional but will be required in the future once we are at v1.」（来源：https://docs.zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response ）。
- **官方承认「形状只是中间产物」**：「The shape itself is only an intermediate artifact.」（来源：https://docs.zoo.dev/blog/why-ai-must-generate-parametric-cad ）——不是「出形即完成」。
- **Zookeeper 自评仍处早期**：「We view Zookeeper as being in its early stages」（来源：https://docs.zoo.dev/research/zookeeper ）。

### 5.2 ★ 刻意不做的段（逐条引官方原文 + 链接）

- **不做装配配合（mates）**：v1 的 Roadmap 原文「Constraints 2.0 & Assembly Mates – define relationships between parts to ensure the final product always fits. We're seeking feedback with our spec open for comments.」（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。★ 注意别读错：v1 的已交付清单里**有**「Assemblies」——即能摆多个零件，但「配合关系」在 Roadmap。
- **不做工程图 / GD&T**：同一 Roadmap 原文「Drawings & GD&T – production-ready 2D output」（同上）——即当日**未交付**。
- **不做逆向（STEP/STL → 参数化）**：研究页 Roadmap 原文「Reverse engineering: We are training Zookeeper to infer parametric intent from static geometries, such as those defined by STEP and STL files」（来源：https://docs.zoo.dev/research/zookeeper ）——是「在训练」，不是「已有」。
- **不做图像输入**：「Multimodality: ... Our next update enables users to add image attachments within Zookeeper prompts」（同上）。
- **不做多代理并行**：「Fleets of agents: Manage a team of Zookeeper agents working concurrently」（同上）。
- **不做仿真/DFM/公差**：官方自报的工具清单里没有任何仿真、可制造性检查或公差标注工具（逐条见 https://docs.zoo.dev/research/zookeeper 的「What are your tools?」原文清单）；且官方把公差与检验放在「下游」：「the work lives in the intent built into the model ... and in the downstream steps that depend on it (toolpaths, setups, tolerances, inspection)」（来源：https://docs.zoo.dev/blog/why-ai-must-generate-parametric-cad ）。

### 5.3 【宣称】vs【事实】

- 【宣称】「enable designers and engineers of all skill levels to more efficiently produce manufacturable, high-quality 3D designs」（来源：https://docs.zoo.dev/research/zookeeper ）。
- 【事实】同页工具清单里**没有**任何可制造性校核工具；能拿来判「对不对」的只有引擎能否跑通、多视角快照、四个质量特性。
- 【宣称】「Text-to-CAD ... One for generating 3D B-Rep models via prompting」（同上）。
- 【事实】API 的 `output_format` 允许拿到的文件格式只到 STEP/STL/glTF/OBJ/PLY/FBX（来源：https://docs.zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response ）——**没有**原生 CAD 格式（没有 .sldprt/.prt/.f3d）。
- 【宣称】当年「in the future, we will give you the generated KCL code」（2023 年博客，来源：https://docs.zoo.dev/blog/introducing-text-to-cad ）。
- 【事实】今天 API 确实回 `code`，但它是**可选**字段（见 §5.1）。

### 5.4 其他限制

- Web 客户端只支持 single-file 工作流（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。
- 计费按时间而非按调用：「pay-as-you-go pricing of $0.50 per minute」，且「You are not charged for any failed API calls」（来源：https://docs.zoo.dev/blog/turning-on-billing-for-text-to-cad ）——**失败不收费**这条对试错成本很关键。

## 6. 对我方目标的可用处（机制层面，含**不能**学什么）

**能学的**

- **「两级执行门」直接搬**：语法级快检 → 真跑引擎。映射到 SolidWorks 就是：静态签名比对（不连 COM）→ 真机跑一遍，正好对上本仓「签名三源互证 → 本机实测」的顺序。
- **「代码即模型」→ 我们的「声明式特征 spec」**：KCL 能当唯一真相源，是因为写出来的就是模型定义。我们对应的落点是「一份可 diff 的特征声明（参数 + 选择器 + 期望几何量）」，而不是「一段命令式 COM 调用脚本」。
- **「选择即上下文」**：`read_user_selections` 这条工具把界面选择变成代理的输入。我们已有同样的原料（当前选中实体），该把它接进提示/校验链，而不是让模型猜「你说的那个面」。
- **「固定视角多视图快照」当验收**：与 CADAM 卡的结论同向——视角固定才可跨模型比较。
- **「质量特性当判据」**：体积/质量/质心是**数值**判据，比「看着像」硬。我们可用同样四量做回归断言。
- **「文档检索工具化」**：把语言/API 参考做成可检索工具，而不是把手册塞进提示词。

**不能学的**

- **自建几何内核**：官方为此投入「fewer than 30 engineers」和两年（来源：https://docs.zoo.dev/blog/zoo-design-studio-v1 ）。我们没有内核，也不能有——我们的宿主是 SolidWorks 的 Parasolid。★ 任何「自己算几何」的路线直接排除。
- **私有微调**：需要客户带特征树的原始 CAD 文件做训练集（同上）。我们没有也不该有。
- **「一次生成整棵特征树」**：Zoo 可以这么干，因为 KCL 里的对象是它自己命名的；SolidWorks 里特征是**宿主命名**、父子引用会断。我们只能生成「可重放的建模步骤 + 稳定选择器」，不能生成「一次成型的树」。
- **「出形即交付」的心态**：官方自己说形状只是中间产物（§5.1），这条要反过来当成对我方的警告。

## 7. 许可与红线

- **服务与模型闭源**：不抄 KCL 语法的实现代码、不抄官方提示词文本（提示词是产品资产）。可以吸收机制（两级执行、快照复核、工具分组）。
- 官方脚注称 `github.com/kittycad/modeling-app` 是开源的应用层——**其具体许可本次未核**（见 §9），若将来要用其代码，必须先读仓库内 `LICENSE` 原文。
- 官方声明企业微调「using their own proprietary datasets for exclusive use」——即模型不因客户数据共享，这条与我们的数据红线一致，可引为对照。

## 8. 证据清单

- https://docs.zoo.dev/machine-learning-api —— API 总览入口：Engine API / Agent API（Zookeeper）/ File Format API 三块；REST + bearer token。
- https://docs.zoo.dev/research/zookeeper —— 研究页：B-rep 三特性、为何放弃直出 B-rep、agent 循环定义、**完整工具清单**、Roadmap（逆向/多模态/多代理）。
- https://docs.zoo.dev/blog/announcing-zookeeper —— Zookeeper 发布博客：能力四块、视口选择即上下文、默认触发快照、KCL 定位、三档价格。
- https://docs.zoo.dev/blog/zoo-design-studio-v1 —— v1：已交付清单（含 Assemblies、六种导出）、Roadmap（Assembly Mates / Drawings & GD&T / 图像输入）、「it's ML」原话、企业微调。
- https://docs.zoo.dev/blog/why-ai-must-generate-parametric-cad —— 为何必须是参数化 B-rep：网格/体素的逐条否证、「CAD Recipe」六项、形状只是中间产物。
- https://docs.zoo.dev/blog/introducing-text-to-cad —— 2023 首发：直出 B-rep 的动机、feature-tree 描述优于名词、「alpha launch」。
- https://docs.zoo.dev/docs/developer-tools/api/ml/get-a-text-to-cad-response —— 响应字段：`code`（可选）、`output_format` 七种、`model` 三种、`source_ranges` 区间改法。
- https://docs.zoo.dev/blog/turning-on-billing-for-text-to-cad —— 计费口径：按服务器时间、失败调用不计费。
- https://zoo.dev/pricing —— 定价页（正文由 JS 渲染，仅取到「Zookeeper 与 API 共用同一份额度」一句，见 §9）。

## 9. 未确认事项

- **当前实际价格**：https://zoo.dev/pricing 与 https://zoo.dev/text-to-cad 都是 JS 应用，直读拿不到价目表（后者直接返回客户端异常）。本卡的档位数字全部来自 Zookeeper 发布博客，而该页自己声明「价格以发布当时为准」⇒ 现行价目**查不到**。
- **`modeling-app` 的具体开源许可**：未读仓库内 `LICENSE`，只看到官方脚注说它开源。
- **是否有「改前批准」环节**：官方博客/研究页描述了协作式计划与用户复核，但**没有**任何一处写「apply 前必须人工批准」。故本卡 tag 里的 `orchestration=loop` 指的是「代理循环」，**不是**「人工批准循环」。
- **精度**：官方没有任何关于尺寸误差、成功率或幻觉率的量化指标（本卡不引第三方测评）。
- **同一响应是否能同时拿到 STEP 与 KCL**：文档的 `outputs` 是「path → base64」的映射，`code` 是另一字段；两者在同一次调用里是否都出现，未实测。
- **Zookeeper 与 Text-to-CAD API 是不是同一后端**：官方说 API 中「Agent API — Bring AI-powered CAD assistance into your applications with Zookeeper」，但两套端点的能力差异未逐条比对。
