# Leo AI（getleo.ai）

<!-- survey: class=E; repr=feature-tree; orchestration=loop; verify=dfm-rules; deliver=STEP; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码/无公开权重；官网 https://www.getleo.ai/ · 官方博客 https://www.getleo.ai/blog/can-ai-generate-cad-models-2026 |
| 许可 | 商业企业服务条款；公开定价页**查不到**（`getleo.ai/pricing` 返回 404），按企业合同交付 |
| 元数据 | Leo AI（getleo.ai）· 官网 https://www.getleo.ai/ · 取数日期 2026-10-24（来源：https://www.getleo.ai/ai-for-mechanical-engineering） |
| 克隆 | 未克隆（无源码） |
| 证据等级 | **元数据**（官方文档，无源码、无法本地实测） |

## 1. 一句话定位

面向机械工程的生成式平台：先用问题澄清需求，再去 PDM/PLM 里检索既有零件，跑工程计算，最后产出**带零件树与特征树的参数化装配**，官方口径是「compatible with SolidWorks, CATIA, Onshape, and Inventor」。它是这五张卡里唯一宣称交付参数化实体的产品；但**官方没有公布导出格式清单**，STEP/IGES 是否直出**查不到**——本卡 tag 里的 `deliver=STEP` 只表示「交付物是 CAD 实体、归入工程格式桶」，不代表已证实直出 STEP。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- 输入：自然语言需求（官方示例还包含草图、规格、CAD 约束）
- 中间表示：澄清问题（载荷、环境、包络）+ 库内候选零件 + 工程计算 + 约束——先有「为什么」，再有几何
- 生成：参数化装配（零件 + 特征），官方称每个尺寸都能追溯到一次计算或一条标准
- 编排：多轮问答 + 「先检索、后生成」的强顺序（官方原文：Only after exhausting existing options does Leo generate new geometry）
- 执行：云端平台，通过连接器读取 SolidWorks PDM / Windchill / Teamcenter / Onshape
- 验证：对项目合规要求做设计检查并标出问题（MIL-STD、ISO 13485、FDA 21 CFR 等）
- 交付：可编辑装配（原生 CAD 口径）；导出格式清单官方未公布

## 3. 技术方案要点（可迁移的机制）

- 生成前先检索：官方原文「Only after exhausting existing options does Leo generate new geometry」，即先查库里有没有能复用的件（来源：https://www.getleo.ai/blog/can-ai-generate-cad-models-2026）
- 尺寸必须可追溯：官方原文「Every dimension traces back to a calculation or standard」（来源：https://www.getleo.ai/blog/can-ai-generate-cad-models-2026）
- 交付形态是可编辑装配，不是网格：官方原文「the output is a full parametric assembly with a complete part tree and feature tree, compatible with SolidWorks, CATIA, Onshape, and Inventor」（来源：https://www.getleo.ai/blog/can-ai-generate-cad-models-2026）
- 每个零件带四类信息：参数约束、材料赋值、制造备注，加上装配层的零件树（来源：https://www.getleo.ai/blog/best-text-to-cad-ai-tools-2026）
- 生成前先问问题：把「载荷条件、使用环境、相邻装配的包络约束」当生成前置输入（来源：https://www.getleo.ai/blog/can-ai-generate-cad-models-2026）
- 合规检查是交付前的门禁：按行业框架（MIL-STD / ISO 13485 / FDA 21 CFR）检查并标出问题（来源：https://www.getleo.ai/blog/best-text-to-cad-ai-tools-2026）
- 原生读 B-rep 与特征树：检索侧直接读 B-rep、特征树、装配关系，而不是靠文件名或元数据（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）

## 4. 运行条件与依赖

- 形态：企业级 SaaS，需接入既有 PDM/PLM（SolidWorks PDM、Autodesk Vault、PTC Windchill、Siemens Teamcenter）（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）
- 平台口径：官方称生成结果「compatible with SolidWorks, Onshape, CATIA, and Inventor」（来源：https://www.getleo.ai/ai-for-mechanical-engineering）
- 知识与索引口径：官方页给出 1M+ 已审核工程来源、120M+ 供应商零件索引，并称零训练使用客户数据（来源：https://www.getleo.ai/ai-for-mechanical-engineering）
- 合规与安全：SOC 2、GDPR（来源：https://www.getleo.ai/ai-for-mechanical-engineering）
- 定价：**查不到**公开定价页（`getleo.ai/pricing` 为 404），也无 credits 口径可引

## 5. 失败模式与已知限制

官方博客里对**「文本转 CAD 这一类」**的承认（原文照引；这是类别级自述，不等于 Leo 承认自身缺陷）：

- 网格路线进 SolidWorks 只能当图形体：「If the API returns mesh data (STL or OBJ), SolidWorks can import it, but the result is a surface body or a graphics body, not a solid feature-based model.」（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）
- 脚本路线的 STEP 没有特征树：「CadQuery can export STEP files, which SolidWorks imports cleanly as dumb solids. Better than mesh, but still no feature tree.」（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）
- 用 LLM 驱动 CAD 引擎，复杂几何会崩：「This approach can produce native output, but the success rate drops quickly once geometry gets beyond basic extrusions and cuts.」（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）
- 生产级参数化工作流仍未自动化：「That is still a fundamentally manual process in 2026.」（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）
- 典型集成路径仍要人工重建：「A practical integration typically involves ... converts the geometry to STEP format if needed, imports it into SolidWorks, and then requires an engineer to manually rebuild or adapt the model」（来源：https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks）

产品自身的失败模式（错件、配合错误、尺寸越界、生成失败的兜底策略）——官方**没有**专门页面，**查不到**。

## 6. 对我方目标的可用处（机制层面，含**不能学什么**）

我方目标：让普通模型建出能用、规范的参数化模型（SolidWorks）。

可用（机制级，这条卡对我们最贴）：

- 「澄清 → 检索 → 计算 → 生成 → 合规检查」这条显式流水线，正好把我们仓库已有的顺序（先扫 dead-ends、再读 capabilities 的 limitations、再动手）搬到生成侧：**先查再建**，而不是让模型直接开画。
- 「每个尺寸追溯到一次计算或一条标准」= 我们要的「参数必须有来源」。这条可以直接落成门禁：凡是没有来源的尺寸，不许进模型。
- 交付物按「零件树 + 特征树」描述，而不是按「网格 + 贴图」描述——这正是我们该有的交付口径；它把「可编辑」定义为「能在原生 CAD 里改任何一个参数」，而不是「能在 DCC 里拖点」。
- 合规检查作为交付前门禁（按行业框架列检查项），可以借成我们的「导出前 checklist」形态：检查项来自标准，结果可 grep。

不能学（边界）：

- 不能把「compatible with SolidWorks」当成 STEP 直出的证据：官方没有给格式清单，这是营销级表述，不是格式承诺。
- 不能学「LLM 直接驱动 CAD API」这条路——它自己的博客就承认，超过基本拉伸与切除后成功率快速下降；这条与我们已知的「COM 调用契约脆弱」是同一个坑。
- 不能把它的价值主张照搬：它的重心是「检索既有参数化零件」（复用），我们的目标是「建出新的规范参数化模型」（生成），落点不同；学它的流水线顺序可以，学它的产品定位不行。

## 7. 许可与红线

- 闭源商业企业服务；公开定价**查不到**，只能按合同口径描述，不落金额
- 红线一：不得把它写成「STEP/IGES 已验证」——官方未公布导出格式，本卡只能记为「工程路线候选、格式待证」
- 红线二：不得把类别级自述（它批评「文本转 CAD 这一类」的原文）包装成「Leo 自认的缺陷」
- 红线三：它的能力建立在读取客户 PDM/PLM 之上，涉及客户数据边界；我们的仓库不引入其任何数据、模型或接口凭据

## 8. 证据清单

- https://www.getleo.ai/ai-for-mechanical-engineering —— 产品定位与官方能力口径：LMM、1M+ 来源、120M+ 零件索引、SOC 2、零训练、连接 Windchill/Teamcenter/Onshape/SolidWorks PDM、「generates editable, standards-compliant CAD starting points」
- https://www.getleo.ai/blog/can-ai-generate-cad-models-2026 —— 完整流程原文：先问澄清问题、先搜 PDM、再生成；「full parametric assembly with a complete part tree and feature tree, compatible with SolidWorks, CATIA, Onshape, and Inventor」；「Every dimension traces back to a calculation or standard」
- https://www.getleo.ai/blog/best-text-to-cad-ai-tools-2026 —— 每个零件含参数约束/材料赋值/制造备注；按 MIL-STD、ISO 13485、FDA 21 CFR 做合规检查
- https://www.getleo.ai/blog/text-to-cad-api-integration-solidworks —— 对「文本转 CAD」这一类的自述限制：网格只能进成图形体、STEP 无特征树、LLM 驱动 CAD 的复杂几何成功率下降、生产级仍靠人工
- https://www.getleo.ai/blog/step-file-ai-agent-what-translator-dropped —— 官方对 STEP 的信息损失口径：特征树、配置、GD&T、配合关系通常不在 STEP 里
- https://www.getleo.ai/ —— 首页定位：从高层设计到细节几何，找公式、跑计算、复用既有零件来拼装配

## 9. 未确认事项

- **导出格式清单**：STEP / IGES / Parasolid / 原生 SolidWorks 文件，官方页面与博客均未列举——**查不到**（也因此 `deliver=STEP` 是桶归类，不是格式证实）
- 公开定价与试用门槛：`getleo.ai/pricing` 为 404——**查不到**
- 装配配合是否自动：只见第三方工程媒体转述 CEO 原话（「配合需手动补」），官方页未找到同句——按纪律**不计入结论**
- 同名干扰：`iamleo.ai` 是另一款法语工具（另有 credits 口径），Dassault 在 SOLIDWORKS R2026x FD04 说明里也提到名为 LEO 的助手（https://3dswym.3dexperience.3ds.com/wiki/solidworks-news-info/solidworks-design-ai-r2026x-fd04_jdGbk_4uTHmLKxYMvQ7Krw）；本卡按 **getleo.ai** 写，若目标指后者，本卡需整体替换
- 训练数据与权重：闭源，无公开——**查不到**
