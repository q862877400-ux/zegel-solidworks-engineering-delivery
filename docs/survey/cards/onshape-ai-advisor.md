# Onshape AI Advisor

<!-- survey: class=I; repr=none; orchestration=none; verify=none; deliver=none; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码（Onshape 内的问答面板）。官方帮助 https://cad.onshape.com/help/Content/Home/ai_advisor.htm ；官方发布博客 https://www.onshape.com/en/blog/ai-advisor-guide-cad-pdm |
| 许可 | 商业闭源 · **订阅内置，不单收费**。官方帮助首句：「Available for all plans except Onshape Government.」（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ） |
| 元数据 | PTC（Onshape）· https://www.onshape.com · 取数 2026-10-24（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ） |
| 克隆 | 未克隆（闭源，无仓库） |
| 证据等级 | **元数据**（官方帮助页 + 官方博客；无源码、无本地实测——需 Onshape 账号） |

## 1. 一句话定位

**它不是建模器，是「会引用出处的帮助文档入口」**：官方定义只有一句——「AI Advisor is an AI expert that can answer your Onshape questions. Use the AI Advisor panel to ask a question to get information and references from Onshape's extensive resource library.」（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ）。

- **AI 落在哪一段工序**：**无（不进入建模工序）**。它落在「学习/查文档」这一步：给答案 + 编号引用，由人自己回到界面按步骤操作。
- **它连「代做」都没有**：官方全文没有「它会替你执行命令」这类表述；帮助页列的是「问 → 给答案 → 点引用 → 评分」四步（同上）。
- 这一条对本调研的价值不在「它做了什么」，而在**大厂把 AI 的第一落点放在知识层而不是几何层**——它是一个刻意保留的边界案例。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

★ 本卡大部分环节在官方文档里**不存在**，逐段如实标注：

1. **输入**：Prompt 框里的一句问题；同一会话内的后续提问会**累积**（官方：「responses are cumulative, and build upon prior questions. If you wish to start over, refresh the browser window.」）（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ）。
2. **中间表示**：**检索命中与引用条目**。官方只披露来源库的四类清单（见 §3），未披露切片/向量/排序等内部结构——**查不到**。
3. **生成**：答案文本 + 编号引用；点编号在新标签打开原文，也可展开 References 下拉看有序清单（同上）。
4. **编排**：**none**。没有工具调用、没有多步计划、没有修改文档的通道（官方全文无此描述）。
5. **执行**：**无**。它不执行任何 CAD 命令。
6. **验证**：**由人做**。两处硬约束：搜索页示例里印着「AI generated content can make mistakes. Review for accuracy.」；面板底部给 1–5 星评分并**逐星定义了含义**（1 星「Completely inaccurate」→ 5 星「Completely accurate」）（同上）。
7. **交付**：**文本 + 链接**。无 STEP、无网格、无特征树、无工程图——**不产出任何几何**。

## 3. 技术方案要点（可迁移的机制）

- **来源白名单，写进文档**：官方明列四类来源——「Help documentation / Learning center courses / Onshape blogs / Other Onshape resources」（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ）。★ 这是可抄的硬机制：**先说清「我只在这几个库里查」，再说答案**。
- **答案必须带编号引用，且引用可点开**：「Click a numbered reference to open its source in a new browser tab.」（同上）——引用不是装饰，是一等公民。
- **与既有搜索合流，而不是另开入口**：Help 菜单 → Help 的搜索结果页里，AI 答案直接排在其他结果**之上**（同上）。这避免了「两套帮助系统打架」。
- **评分刻度先定义再收集**：五档、每档一句定义（同上）。这让「答案准不准」这件事有可比的粗糙量化。
- **权限按「文档归属」判定**：「AI Advisor is only visible if the Document is owned by you or your company/classroom/enterprise.」（同上）——多租户下的可见性门。
- **默认开关按客户类型分级**：Company/Classroom 默认开，Enterprise 默认关，可集中切换（同上）。这是「企业可一键关掉」的合规姿态。
- **底座**：官方博客称与 AWS 合作，使用 Amazon Bedrock、SageMaker、S3 与 AWS GenAIIC（来源：https://www.onshape.com/en/blog/ai-advisor-guide-cad-pdm ）。

## 4. 运行条件与依赖

- **宿主**：Onshape 云端文档界面（Document 面板上的 AI Advisor 图标）**或** Learning Center / Help 搜索页（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ）。
- **账号与套餐**：所有套餐可用，**唯独 Onshape Government 的 app 内不可用**；官方给的替代路径是用免费账号在 cad.onshape.com 通过 Learning Center 访问（来源：https://www.onshape.com/en/blog/ai-advisor-guide-cad-pdm ）。
- **必须联网**（纯云产品）。
- **企业侧开关**：My Account → Company/Classroom/Enterprise settings → Preferences → AI Advisor（来源：帮助页同上）。
- **多组织用户**：可见性按「每个文档的归属组织是否开启」逐个判定，不是全局一刀切（同上）。
- **无额外许可证/无计量**：官方帮助与博客均未提任何单独计费或额度（**查不到**收费项）。

## 5. 失败模式与已知限制

### 5.1 ★ 官方逐条否认/限定的原文 + 链接

以下均出自 https://cad.onshape.com/help/Content/Home/ai_advisor.htm ，另有出处另注：

- **它只回答问题**：「AI Advisor is an AI expert that can answer your Onshape questions.」——没有任何「生成/修改几何」的措辞。
- **它只在四个库里查**：见 §3 的四类来源清单。★ 反过来说：**不在这些库里的东西（你的模型、你的公司标准、第三方教程）它没有依据**。
- **答案可能错、必须复核**：「AI generated content can make mistakes. Review for accuracy.」
- **会话会串味**：同一会话内「responses are cumulative」——问偏了只能刷新浏览器重开（同上）。
- **Government 版不做**：见 §4（来源：官方博客）。
- **企业默认关闭**：「Enterprise users have the AI Advisor panel disabled by default.」（同上）
- **没有文档归属就没有面板**：见 §3 权限条（同上）。

### 5.2 【宣称】vs【事实】

- 【宣称】「an AI-powered assistant designed to provide expert knowledge and best practices for using Onshape」（来源：https://www.onshape.com/en/blog/ai-advisor-guide-cad-pdm ）。
- 【事实】官方帮助把它定义成「answer your Onshape questions」，且来源限定为四类内部资料（来源：https://cad.onshape.com/help/Content/Home/ai_advisor.htm ）——**「专家知识」= 自家资料库的回读**。
- 【宣称】（AWS 高管引语，在官方博客内）该方案「surpasses traditional help resources and generic AI tools with its accuracy and context-awareness」（来源：同上博客）。这是**合作方引语**，官方未给任何指标。
- 【事实】官方全文**没有任何**准确率、覆盖率、响应时间的数字（同上两页均无）——即「更好」无量化依据（查不到）。
- 【宣称】博客称可帮用户「simplify their transition from legacy CAD systems」，并举了 SOLIDWORKS 迁移提问为例（同上）。
- 【事实】它给的仍是**文字步骤**；迁移这件事本身仍需人去做（帮助页无任何迁移执行能力）。

### 5.3 其他限制

- **答案质量与提问质量绑定**（官方未直说，但帮助页给的是「输入问题 → 得答案」单通道，没有澄清追问机制）。
- **引用是唯一可核验面**：没有引用就意味着无法核验，而帮助页未承诺「每条答案必有引用」——只承诺「get information and references」（来源：同上）。

## 6. 对我方目标的可用处（机制层面，含**不能**学什么）

我方目标是让普通模型在 SolidWorks 里建出能用、规范的参数化模型。这张卡**基本不能直接借能力**，但它在机制与边界上给了三条硬提示：

**能学的**

- **来源白名单 + 编号引用**：我们的工具输出（尤其是「这个 API 该怎么调」类回答）必须能指到本地官方文档的具体页（本仓已有 `C:\swapi\types\<接口>\<成员>.md` 与 CHM 解包两套源），而不是让模型凭记忆。★ 这条与我们「查不到就说查不到」是同一件事的产品化形态。
- **「答案可能错，请复核」写在答案旁边**：不是藏在条款里。我们每个 AI 产出的建模步骤，都该在返回值里带一句同类声明 + 可核验项（例如「体积应为 X」）。
- **先定义评分刻度再收集反馈**：五档带定义。我们的验收判据也应先写清档位（例如「跑通 / 尺寸对 / 特征树干净 / 可制造」四级），再谈打分。
- **默认关闭 + 组织级开关**：企业侧默认关、可集中开。这对「AI 功能进受监管流程」是现成的合规范式。

**不能学的**

- **把「问答」当「建模」**：它不碰几何，所以我们无法从它身上学到任何「怎么把意图变成特征」的东西。★ 本卡在工序矩阵里应记为「无」。
- **依赖「自家资料库」**：它的知识边界由 PTC 的文档团队维护。我们没有这样的库，只有官方 API 文档——所以我们的检索必须建立在**可枚举的文件树**上（本仓两套离线源），不能假装有「专家库」。
- **「expert」这种定位**：不可验收。我们的目标要求「可 grep 的判据」，不能停在「专家级回答」。

## 7. 许可与红线

- **商业闭源订阅**：不抄其提示词、UI 文案、评分档位描述文字；可吸收机制（引用制、白名单、默认关）。
- **不得把它当 SolidWorks 侧的参照实现**：它没有几何能力，任何「Onshape 的 AI 能建模」的说法都与官方文档冲突（官方帮助无一字支持）。
- **引用官方页面时带 URL**（本卡已按此执行）。

## 8. 证据清单

- https://cad.onshape.com/help/Content/Home/ai_advisor.htm —— 权威一手帮助页：可用套餐范围、四类来源清单、编号引用与 References 下拉、搜索页合流、「AI generated content can make mistakes」、五档评分定义、企业默认关、文档归属可见性规则。
- https://www.onshape.com/en/blog/ai-advisor-guide-cad-pdm —— PTC 官方发布博客：定位（专家知识/最佳实践）、三类典型提问（迁移设置/性能优化/特征细节）、知识来源扩充说明、AWS 合作与 Bedrock/SageMaker/S3、Government 版不可用及替代路径、AWS 高管引语。
- （间接）https://cad.onshape.com/help/Content/Home/ai_advisor.htm 内的搜索示例片段：展示了答案排在其他检索结果之上、以及「Review for accuracy」提示的实际呈现形态。

## 9. 未确认事项

- **内部检索实现**：切片粒度、是否语义检索、模型型号、上下文窗口——官方**完全未披露**（查不到）。
- **准确率/覆盖率的任何数字**：两页均无（查不到）。本卡因此不写任何百分比，也不引第三方测评。
- **是否支持图片/截图提问**：帮助页只描述文字 Prompt（查不到）。
- **是否会在未来具备几何能力**：官方博客末段只有「Stay tuned for future updates」这类泛指（来源：https://www.onshape.com/en/blog/ai-advisor-guide-cad-pdm ）；按本调研纪律，**未来计划不纳入现状判断**。
- **它对「Onshape 专属概念」之外的问题（如通用机械设计）如何作答**：官方未界定知识边界，只给了来源清单；边界外的行为**未确认**。
- **`Getting Started` 之外的多语言行为**：帮助页为多语言站点，但 AI Advisor 的作答语言策略未说明（未确认）。
