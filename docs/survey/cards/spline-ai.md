# Spline AI

<!-- survey: class=E; repr=mesh; orchestration=human-approve; verify=visual; deliver=mesh; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码/无公开权重；官网 https://spline.design/ · 文档 https://docs.spline.design/ |
| 许可 | 商业服务条款：按席位订阅 + 每月 AI credits（Hobby / Pro / Max / Enterprise），无单独 AI 订阅（来源：https://docs.spline.design/account/pricing） |
| 元数据 | Spline（spline.design）· 官网 https://spline.design/ · 取数日期 2026-10-24（来源：https://docs.spline.design/account/pricing） |
| 克隆 | 未克隆（无源码） |
| 证据等级 | **元数据**（官方文档，无源码、无法本地实测） |

## 1. 一句话定位

网页 3D 设计工具里的「文本 / 图 → 网格」入口。它自己不训模型：模型下拉里列的是四家第三方引擎（Hunyuan3D、Hunyuan 3.1 Pro、Trellis 2、Meshy）；导出只有 GLTF / GLB / STL / USDZ（加 `.spline` 原生与代码/原生嵌入），**没有 STEP/IGES，连 FBX/OBJ 都没有**。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- 输入：prompt / 参考图 / 文本+图三选一（官方要求参考图是单物体的正面图）
- 中间表示：先出「图像预览集」，人挑一张，再把那张图交给所选引擎建网格——人先审图，再审模型
- 生成：由下拉里选中的第三方引擎完成（默认 Hunyuan3D）
- 编排：生成按钮在编辑器工具栏（AI → AI Generate），成品直接落进当前场景；同一输入可跑多家、结果可来回切换
- 执行：云端跑，官方明确「不需要特殊硬件」
- 验证：工具条四件套 Wireframe / Clay / Preview maps / Environment / Auto-rotate，官方明确要求「在 Clay 模式里看，贴图会掩盖不平整的形状」
- 交付：GLTF / GLB / STL / USDZ + `.spline` + 网页 URL / 代码 / iOS·Android 原生嵌入（来源：https://docs.spline.design/basics/faq）

## 3. 技术方案要点（可迁移的机制）

- 多引擎并列、人工选优：模型下拉四家引擎，同一张图可跑多家并保留全部结果，官方写明「switching is instant and doesn't use more credits」（来源：https://docs.spline.design/generate/ai-3d-generation）
- 生成被拆成两个人工关口：先出图像预览，选中后才建网格；官方原话还要求「预览都不像就改提示词重发，别挑最像的那个」（来源：https://docs.spline.design/generate/ai-3d-generation）
- 验证工具条把「形状」和「贴图」分开看：Clay 模式隐藏颜色与贴图，Preview maps 单独看贴图，Environment 换光照——官方提示「贴图会掩盖不平整的形状」（来源：https://docs.spline.design/generate/ai-3d-generation）
- 导出契约写成「支持 / 不支持」两栏：GLTF/GLB 支持几何、颜色层、基础贴图；不支持全部材质层、后处理、动画、物理、环境光与雾、状态与交互（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-gtlf-glb）
- 贴图支持写清了适用面：只支持带 UV 投影的 primitive 几何，「Smooth & Edit」几何没有贴图（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-gtlf-glb）
- STL 是纯几何且单独收费：官方写明「Exporting STL format is a paid feature」，需要 Professional 或 Team 订阅，且 STL 不含颜色与材质（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-stl-3d-printing）
- 一个成品可能花掉多次生成的额度：官方写明「a single model can cost more than one generation」，因为图像预览与网格生成各自计费（来源：https://docs.spline.design/account/pricing）

## 4. 运行条件与依赖

- 形态：浏览器 SaaS，无本地/离线路径；AI 生成在云端完成（来源：https://docs.spline.design/generate/ai-3d-generation）
- credits 单池：所有 AI 功能（编辑器里的 AI agent、AI 3D Generation、AI Textures、Hana 的 generate）共用一份每月 AI credits——Hobby 2,000 / Pro 3,000 / Max 10,000，Enterprise 定制（来源：https://docs.spline.design/account/pricing）
- 加量方式：在套餐基础上按 1,000 的步长追加，价格在套餐卡与付款页确认（来源：https://docs.spline.design/account/pricing）
- 付费墙之一：STL 导出属 Professional / Team 订阅功能（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-stl-3d-printing）
- 付费墙之二：GLTF/GLB 的「Color & Texture」材质模式属付费功能，含在 Professional 与 Team 订阅里（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-gtlf-glb）

## 5. 失败模式与已知限制

- 锐边明确不保证：官方 prompt 指南原文「Models with more organic shapes will generate better results, while objects with very sharp edges might not look as good.」（来源：https://docs.spline.design/generate/ai-3d-generation）
- 官方直接劝退高精度场景：指南的小标题就是「Focus on objects that don't require high-precision」（来源：https://docs.spline.design/generate/ai-3d-generation）
- 结果好坏先由第三方引擎决定：模型下拉里 Hunyuan3D、Hunyuan 3.1 Pro、Trellis 2、Meshy 四家并列，Spline 只负责编排与场景集成（来源：https://docs.spline.design/generate/ai-3d-generation）
- 官方「Limitations」段只有通用免责，没有逐条质量承诺：原文只写「The development and research of artificial intelligence (AI) is an ongoing process with several factors that can limit its capabilities. You will likely find bugs and some issues」（来源：https://docs.spline.design/generate/ai-3d-generation）
- 导出面窄且能力被砍：GLTF/GLB 不支持动画、物理、后处理、环境光；STL 只有几何（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-gtlf-glb）
- 不能当离线工具：全部在浏览器里跑，生成依赖云端（来源：https://docs.spline.design/generate/ai-3d-generation）

## 6. 对我方目标的可用处（机制层面，含**不能学什么**）

我方目标：让普通模型建出能用、规范的参数化模型（SolidWorks）。

可用（机制级）：

- 两段式人工确认（图 → 人挑 → 网格）是最省成本的 human-approve 形态：错了只废一张图，不废一整个模型。我们的生成流程也应把「最便宜的中间产物」放在人眼前让他先否掉。
- 把验证拆成互相独立的视图（线框看拓扑、Clay 看形状、Preview maps 看贴图、Environment 换光照）：这四件事在 SolidWorks 里同样要分开验——几何、外观、材质、光照不能混在一次「看起来对」里。
- 多引擎同输入、结果可切回：把「换引擎」做成零成本操作，是一种可迁移的编排形态（对应我们就是：同一需求可由不同生成策略产出，结果并列可比、选中才落地）。
- 导出说明写成「支持 / 不支持」两栏：这份格式契约的写法值得照抄到我们的导出说明里，明确到「哪些特性会丢」。

不能学（边界）：

- 把浏览器里的可编辑当参数化：它是场景图编辑（位置、样式、动画），没有草图、约束、特征顺序。
- 用它的导出格式做工程交换：清单里连 FBX/OBJ 都没有，只有 GLTF/GLB/STL/USDZ，进 CAD 只能当网格或 graphics body。
- 不能学它「不训模型、只编排」的定位：它的质量上限握在第三方手里，我们要有自己能验的判据，不能把结论建在别人的模型版本上。

## 7. 许可与红线

- 闭源商业服务；席位订阅 + AI credits，AI 不是单独订阅而是一个 credits 池（来源：https://docs.spline.design/account/pricing）
- 付费功能边界：STL 导出、GLTF/GLB 的材质与贴图导出都需要相应付费档（来源：https://docs.spline.design/exporting-your-scene/files/exporting-as-stl-3d-printing）
- 红线一：不得把 Spline 场景里的「可编辑」表述成「参数化可改尺寸」
- 红线二：不得把其 GLTF/STL 输出当作工程交付；STL 是几何容器，不含材质与公差
- 红线三：不得把四家第三方引擎的质量结论记到 Spline 头上（它只是编排方），引用需分开归属

## 8. 证据清单

- https://docs.spline.design/generate/ai-3d-generation —— AI 3D Generation 全流程：付费、credits、四家引擎下拉、图像预览人工选优、Clay/线框等验证工具、锐边与高精度的劝退原文、Limitations 段
- https://docs.spline.design/basics/faq —— 可导出内容的完整清单：GLTF/GLB/STL/USDZ、`.spline`、网页 URL、代码、iOS/Android 原生嵌入
- https://docs.spline.design/account/pricing —— AI credits 单池与各档额度（Hobby 2,000 / Pro 3,000 / Max 10,000）、按 1,000 步长加量、一次成品的 credit 消耗可能不止一次生成
- https://docs.spline.design/exporting-your-scene/files/exporting-as-gtlf-glb —— GLTF/GLB 导出的支持/不支持清单、贴图仅限 UV 投影的 primitive 几何、材质模式属付费功能
- https://docs.spline.design/exporting-your-scene/files/exporting-as-stl-3d-printing —— STL 导出的付费门槛与「纯几何、无颜色材质」

## 9. 未确认事项

- 各档的具体价格（美元数字只在官方定价页，文档页只给 credits 口径）——卡内不落金额，**查不到文档内价目**
- Spline 是否对生成物提供任何尺度或精度保证：官方文档只给出「不要求高精度」的定位，未见精度指标——**查不到**
- 编辑器里 AI agent 与 MCP 工具调用的细节（额度、可调用面）——**未核**
- 生成物进入场景后的拓扑是否可再编辑（除重拓扑外）——文档未列，**查不到**
