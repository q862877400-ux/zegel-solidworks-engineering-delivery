# PTC Creo Generative Design（GTO / GDX）

<!-- survey: class=G; repr=mesh; orchestration=template; verify=solver; deliver=mesh; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码（Creo 扩展）。产品页 https://www.ptc.com/en/technologies/cad/generative-design ；GDX 帮助 https://support.ptc.com/help/creo/creo_pma/r12/usascii/surfacing/freestyle/reconstruct_from_gdf.html |
| 许可 | 商业闭源 · **两个独立付费项**：GTO（Generative Topology Optimization，本机扩展）+ GDX（Generative Design Extension，云扩展）。官方服务说明：「To access GDX, the Customer must also have licenses for the Generative Topology Optimization (GTO) extension in Creo (purchased separately).」（来源：https://www.ptc.com/-/media/Files/PDFs/legal-agreements/cloud-terms/service-descriptions-creo/service-description-creo-1-3-2023-EN.pdf ） |
| 元数据 | PTC（Creo Parametric / Creo+）· https://www.ptc.com · 取数 2026-10-24（来源：https://www.ptc.com/en/technologies/cad/generative-design ） |
| 克隆 | 未克隆（闭源，无仓库） |
| 证据等级 | **元数据**（PTC 官方产品页 + 官方服务说明 PDF + 官方帮助页；无源码、无本地实测——需 Creo 许可与云端额度） |

## 1. 一句话定位

**这是「结构布局求解器」，不是「建模助手」**：人把设计空间、载荷、约束、目标、材料、工艺交进去，求解器吐出材料该往哪长的形状；出来的是**优化后的几何体**（也可以重建为 B-rep），**不是**带设计意图的参数化特征树（来源：https://www.ptc.com/en/technologies/cad/generative-design ）。

- **AI 落在哪一段工序**：**概念/方案布局（E1–E2）**——具体是「给定工况下的材料分布」。它落在建模的**最上游**，且**只做这一件事**。
- **明确不覆盖**：草图、详细特征、装配、仿真报告、工程图。官方把这些交给 Creo 的其它模块（同页「Creo capabilities」把 CAM / Additive / Simulation / MBD 分列为不同能力）。
- **两个产品分工**：GTO 在**本机**跑单目标拓扑优化；GDX 在**云端**并行跑多场景并挑出候选（来源：同上产品页）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入（全部由人给）**：设计空间 + 载荷与约束 + 目标（减重/最大刚度/某阶固有频率）+ 材料 + 制造工艺。官方原文：「Solo tiene que seleccionar espacios de diseño, añadir sus cargas y restricciones y, a continuación, definir los objetivos, el material y el proceso de fabricación para el escenario.」（来源：https://www.ptc.com/-/media/Files/PDFs/CAD/GTO-GDX-datasheet_SJB-Comments_es.pdf ，PTC 官方数据表西语版）。
2. **中间表示**：**优化结果场**——官方帮助把它落成一个「Generative Design Feature（GDF）」放在模型树里；GDF 有两种几何输出形态：**Tessellated（小面/网格体）**或 **Reconstructed（重建为 B-rep）**（来源：https://support.ptc.com/help/creo/creo_pma/r12/usascii/surfacing/freestyle/reconstruct_from_gdf.html ）。
3. **生成**：拓扑优化求解（GTO 本机）/ 云端多场景并行求解（GDX）。官方对 GTO 的定性：「Topology optimization converges on a single solution based only on functional objectives, constraints, and loads and solves for one solution at a time.」（来源：https://www.ptc.com/en/technologies/cad/generative-design ）——**单解**，一次一个。
4. **编排**：**template 型**——人先把「场景」配好（工况 + 目标 + 材料 + 工艺），求解器按这套配置跑。没有 LLM 代理循环，没有多步计划。
5. **执行**：GTO 在 Creo 本机；GDX 把研究送到 PTC 托管的云端跑（来源：服务说明 PDF 同上）。
6. **验证**：**求解器自身**（结构/模态/热分析）+ 人看结果。「Capacidad de previsualizar y cuestionar el diseño optimizado junto con los resultados de la simulación」（来源：数据表西语版同上）。
7. **交付**：
   - Tessellated：直接是网格/小面体，适合增材。
   - Reconstructed：右键 GDF → `Reconstruct`，生成**Freestyle 特征**（曲面重建）并转成实体（来源：帮助页同上）。
   - GDX 侧数据可导出为 Creo Parametric `*.prt`（来源：服务说明 PDF 同上，原文「Customer may extract Data available for export in Creo Parametric format (*.prt) format」）。

## 3. 技术方案要点（可迁移的机制）

- **「需求结构化」是生成的前提**：设计空间 / 载荷 / 约束 / 目标 / 材料 / 工艺，六项缺一不可。官方把「Setup」列成一节专门讲（来源：https://www.ptc.com/en/technologies/cad/generative-design ）。★ 可迁移：任何生成式能力，先把输入契约写死。
- **单解 vs 多解是两档产品**：GTO 一次给一个解；GDX 并行给多个场景并「identifies the top options」并配交互图表与报告（来源：https://www.ptc.com/-/media/Files/PDFs/CAD/GTO-GDX-datasheet_SJB-Comments_es.pdf ）。
- **同一结果、两种输出形态，按下游用途二选一**：增材 → tessellated；后续 CAD/CAM → reconstructed B-rep。这是很实用的产品设计（来源：帮助页同上）。
- **重建走的是 Freestyle 曲面路线**：`Reconstruct` 生成的是 Freestyle 特征（曲面）+ 可选的 Attach 微调（来源：帮助页同上）。★ 即：**从优化结果到可编辑几何，走的是「曲面重建」而不是「特征重放」**。
- **把「混合体（hybrid body）」这个概念显式化**：官方定义「Hybrid body refers to any geometry that is not b-rep ... Facets, triangulated or tessellated models, and volumetrically represented geometries」（来源：帮助页同上）。这给了「网格与 B-rep 同处一个模型树」的官方合法性。
- **云端额度的计量方式**：GDX 按 credits 计，一个包含 20,000 credits，按合同年过期（来源：服务说明 PDF 同上）。★ 可迁移：算力型能力的定价单位应可预测、可预算。
- **安全资质如实披露**：GDX 声明 SOC 2 Type 2，并**主动说明**「PTC's ISO 27001 certification does not cover this offering」（来源：服务说明 PDF 同上）。

## 4. 运行条件与依赖

- **宿主与版本**：Creo Parametric（GTO 为本机扩展）；GDX 是「preconfigured, PTC-hosted package」（来源：服务说明 PDF 同上）。
- **许可前置**：买 GDX 必须先有 GTO 许可（同买，见表格）；GTO 与 GDX 是**两个付费项**。
- **云端**：GDX 需把研究上传到 PTC 云端跑求解器；单用户访问按包计（「Single user access per GDX package purchased」）（同上）。
- **额度**：每包 20,000 credits，按合同年到期、不结转；超额另收费（同上）。
- **数据出口**：服务期临近结束时可按 `*.prt` 导出，否则到期后数据被删除（同上）。
- **人必须在场**：GTO 的结果需要人「review and select」才能进入后续开发（来源：https://www.ptc.com/en/technologies/cad/generative-design ）。
- **无免费/开源路径**：官方未提供免费的独立版本（查不到）。

## 5. 失败模式与已知限制

### 5.1 ★ 官方逐条限定 / 否认的原文 + 链接

- **GTO 一次只给一个解，且只按功能目标收敛**：「Topology optimization converges on a single solution based only on functional objectives, constraints, and loads and solves for one solution at a time.」（来源：https://www.ptc.com/en/technologies/cad/generative-design ）。
- **GDX 必须依附 GTO**：见表格许可行（来源：服务说明 PDF）。
- **产出是 GDF，不是特征树**：官方把产物定义为「generative design feature」，并在模型树里作为**一个**要素出现；重建时「The reconstructed geometry features including the Freestyle feature are created in the Model Tree.」（来源：https://support.ptc.com/help/creo/creo_pma/r12/usascii/surfacing/freestyle/reconstruct_from_gdf.html ）。
- **Tessellated 那条路做不了参数化**：PTC 官方帮助（`generative_design/generate_design.html`，本次可读的是 r8.0 俄语版）明确：小面（facet）要素**不能执行参数化功能**，只能做基本编辑操作；且「只构建被优化的那一个构件」。★ 该页中文/英文版因 JS 无法直读，见 §9。
- **GDX 不走 ISO 27001**：官方主动声明该产品不在其 ISO 27001 认证覆盖内（来源：服务说明 PDF）。
- **额度会过期**：credits 按合同年计算、不结转（同上）。

### 5.2 【宣称】vs【事实】

- 【宣称】「El diseño generativo crea de forma autónoma diseños de modelos CAD óptimos a partir de un conjunto de requisitos especificado por usted.」（来源：https://www.ptc.com/-/media/Files/PDFs/CAD/GTO-GDX-datasheet_SJB-Comments_es.pdf ）——「autonomously」。
- 【事实】官方同页把autonomía的范围限定成「单目标、单解、按功能目标收敛」（见 §5.1 第一条），且产品页明确要人「review and select the most promising designs for further development」。
- 【宣称】数据表称结果可「reconstruirse como geometría CAD B-rep completa para usarse en procesos descendentes」（完整 B-rep，供下游使用）。
- 【事实】重建的具体机制是 `Reconstruct` → **Freestyle 曲面特征** + 可选的顶点 Attach 微调（来源：帮助页同上）——是曲面拟合式重建，**不是**原始设计的参数化特征回放。
- 【宣称】产品页「Is generative design AI?」的答案是「uses artificial intelligence (AI) and machine learning techniques to automate the design process」（来源：https://www.ptc.com/en/technologies/cad/generative-design ）。
- 【事实】同一节把机制描述成「generate and evaluate multiple design options based on input from the user」，且**GTO 是确定性求解**（拓扑优化）而非生成式模型的采样——官方自己在下一问把 generative design 与 topology optimization 拆成两件事（同上）。

### 5.3 其他限制

- **前置工作量全在人身上**：设计空间、载荷、约束、目标、材料、工艺六项都得人给；给错就没有正确的解（来源：产品页同上）。
- **结果需要「接回去」**：优化出的形状要回到详细设计，必须经过重建或手工重画；官方未提供「自动生成参数化特征」的路径（来源：帮助页同上）。
- **GDX 的云端时延/排队**：官方未披露（查不到）。

## 6. 对我方目标的可用处（机制层面，含**不能**学什么）

我方目标：让普通模型在 SolidWorks 里建出能用、规范的参数化模型。★ 本仓把「拓扑优化」列为自建护城河之一，所以本卡对我们是**同类能力的官方基准**。

**能学的**

- **输入契约六项（设计空间/载荷/约束/目标/材料/工艺）**：这是拓扑类能力的产品级最小输入集，我们的实现应照此定义参数，而不是让模型自由发挥。
- **「单解（本机）/ 多解（云并行）+ 候选排序」两档**：先把单解做对，再谈并行与排序。官方把「identifies the top options」当成独立卖点（来源：数据表西语版同上）。
- **双输出（tessellated / reconstructed）按下游用途二选一**：我们若做拓扑，必须同时提供「给增材的网格」与「给 CAD 的 B-rep/曲面」两条路，并明确告知哪条丢了设计意图。
- **安全与合规如实披露**：SOC 2 + 「ISO 27001 不覆盖本产品」——这种「主动说缺口」的写法值得照抄进我们的能力卡。
- **算力型能力的计价单位**：credits 可预算、按年过期——比「按次」更能让客户估算。

**不能学的**

- **「重建 = 参数化」这个隐含等式**：Creo 的重建给的是 Freestyle 曲面，不是特征历史。★ 我们的目标恰恰是**特征历史**，所以这条路不能抄；我们若做拓扑，必须额外解决「优化结果 → 特征序列」的重建，这在 Creo 的官方路径里**不存在**。
- **把优化结果直接当最终设计**：PTC 数据表允许「utilizarlos como el diseño final」，但对我们「规范参数化」的目标，那是反面教材。
- **云端求解器实现**：闭源，且是商业护城河（不学、也学不到）。
- **「AI」标签的泛化**：官方自己在 FAQ 里把 generative design 与 topology optimization 拆开；我们别把「拓扑优化」包装成「生成式 AI」，那是官方都不做的事。

## 7. 许可与红线

- **商业闭源**：不抄代码、不抄提示词；可引产品页/服务说明/帮助页的**机制与限制**（带 URL）。
- **官方服务说明是合同级文本**：其中的「必须同时持有 GTO 许可」「credits 不过期结转」「数据到期删除」属法律条款，引用时按原文照录、不改写。
- **不使用第三方对 Creo GD 的评测**（本卡未使用）。
- **本卡不构成对 PTC 产品的可用性判断**：只做现状描述。

## 8. 证据清单

- https://www.ptc.com/en/technologies/cad/generative-design —— 官方产品/FQA 页：GTO 与 GDX 的分工与集成方式、拓扑优化「单解、按功能目标收敛」、generative vs topology vs parametric 三者的区别、AI 的官方定义、增材与减材都支持。
- https://support.ptc.com/help/creo/creo_pma/r12/usascii/surfacing/freestyle/reconstruct_from_gdf.html —— 官方帮助（r12 英文）：GDF 可建 tessellated 或 b-rep；`Reconstruct` 生成含 Freestyle 的重建特征；Attach 模式可调顶点；hybrid body 的定义。
- https://www.ptc.com/-/media/Files/PDFs/legal-agreements/cloud-terms/service-descriptions-creo/service-description-creo-1-3-2023-EN.pdf —— 官方 SaaS 服务说明（英文 PDF）：GDX 是云扩展、必须另购 GTO、单用户/包、20,000 credits/包、credits 年度过期不结转、SOC 2 Type 2 且不含 ISO 27001、数据以 `*.prt` 导出。
- https://www.ptc.com/-/media/Files/PDFs/CAD/GTO-GDX-datasheet_SJB-Comments_es.pdf —— PTC 官方数据表（西语版）：GTO 的输入六项、动态更新、自动重建为 B-rep 或 tessellated、结构/模态/热分析；GDX 的多场景并行、候选自动识别、以图表与报告呈现。
- https://support.ptc.com/help/creo/creo_pma/r8.0/russian/generative_design/generate_design.html —— 官方帮助（r8.0 俄语）：`Generate Design` 的两种几何输出（Tessellated / Reconstructed）、小面要素**不能**做参数化功能、只构建被优化的那一个构件、研究收敛后才可出现该命令。

## 9. 未确认事项

- **英文/中文帮助正文未能直读**：`support.ptc.com/help/creo/...` 的正文页是 JS 应用，直接抓取返回「DOM storage is disabled」。本卡引用的英文 reconstruct 页与俄语 generate_design 页内容取自检索索引正文。★ 逐字引用前请在浏览器复核（尤其「小面要素不能执行参数化功能」这一条，它是本卡的关键否定结论）。
- **GTO 的具体求解算法与网格规模**：官方未披露（查不到）。
- **重建精度/成功率**：官方无量化指标（数据表只说可选分辨率等级，未给数字）。
- **GDX 的并发场景数上限**：官方只说「多个场景」，未给上限（查不到）。
- **`class=G` 的选择有争议**：拓扑优化在 A–J 分类里没有对位项（它不是代码、不是序列、不是网格生成器）。本卡取 G（约束/规则驱动）为最接近项；汇总时若不认同，需在 v3 报告中说明，而非由本卡擅自新增类别。
- **`deliver=mesh` 的口径**：主输出形态是 tessellated 网格；reconstructed B-rep 再由 Creo 常规导出到 STEP——这后半段**不是** GDX/GTO 自身的能力声明，故 tag 不取 `deliver=STEP`。
- **Creo+ 与 GDX 的绑定关系**：官方产品页提到 Creo+ 是 SaaS 版 Creo，但 GDX 在 Creo+ 下是否同样可用，未核实。
