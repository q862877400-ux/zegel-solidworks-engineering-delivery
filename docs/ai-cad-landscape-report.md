# AI 自动建模 · 全网技术路线总图

**依据**：业主 2026-10-23 指令 ——「做 Agent 自动建模这个事情的全网调研、全网技术路线的总图：不同家有不同的做法，每一个项目的技术路径是什么样子；一般来说有哪几类架构；具体每一类架构里面的每个步骤都有哪些做法。这是一个极其详细的报告，相当于我看了你的报告，就已经清楚地知道市面上任何一个 AI 自动建模的工具是怎么设计的了。」

**日期**：2026-10-23　**性质**：技术路线总图（描述现状与原理，不含落地计划）
**调研方式**：7 路并行只读调研（A 工程 CAD / B 生成式网格 / C 桥接层 / D 学术谱系 / E 商业产品 / F 工程手段 / G 图纸与知识）＋ 本仓库代码实测。
**证据约定**：量化断言尽量落在表格的「来源」列（可点链接或本仓路径）；正文里的数字附「来源：…」。**未核验写「未确认」**；营销说法标【宣称】，官方文档写明标【事实】。

---

## 0. 怎么读这份报告（三个坐标 + 一次自检）

**任何 AI 自动建模工具，都可以用三个坐标定位：**

| 坐标 | 要回答的问题 | 见 |
|---|---|---|
| **① 表示层** | 模型最终吐出什么？（代码 / 命令序列 / DSL / 网格 / 约束 / 只填参数） | §2 |
| **② 编排层** | 一次生成，还是带校验的循环，还是多个智能体分工？ | §3 |
| **③ 验证层** | 怎么判断「成了」？靠数值、几何、看图、求解器、还是 DFM 规则？ | §4 |

**「5 分钟看懂任意一个 AI 建模工具」自检 10 问**（照着问，答案决定它属于哪一类）：

1. 它最终产出的是 **可执行代码** 还是 **网格**？（看导出格式有没有 STEP/IGES —— 有＝B-rep 路线，没有＝网格路线）
2. 中间表示是开放词表（Python）还是封闭词表（自定义 token / DSL）？
3. 生成器是**通用 LLM**、**微调过的专模**、还是**没有 AI**（模板+规则）？
4. 有没有「执行 → 读错误 → 重写」的循环？最多几轮？
5. 失败时模型能看到什么？（traceback / 几何度量 / 渲染图 / 求解器诊断）
6. 有没有**硬门禁**（不合法直接判失败，不听模型解释）？
7. 验证用的是**形状相似度**（CD/IoU）还是**尺寸/公差/可制造**？
8. 人插在哪一步？（给意图 / 选模板 / 批准变更 / 目视核验）
9. 它要求多大的模型？（1.5–2B 代码模型 / 7–13B 专模 / 闭源大模型 / 无要求）
10. 交付物是什么？（STEP / 工程图 PDF / GLB / 只是建议文字）

---

## 1. 九类架构（全景）

> 一个工具通常落在其中一类；混合型写明「主类 + 副类」。

| 类 | 架构名 | 一句话 | 代表 | 致命弱点 | 普通模型能否 |
|---|---|---|---|---|---|
| **A** | 代码即 CAD·单发 | LLM 写参数化脚本 → 内核执行一次 | 多数开源 text-to-CAD | 一次错就全错 | 勉强 |
| **B** | 代码即 CAD·回环 | 同上 + 执行→报错→重写（≤3 轮） | [CADSmith](https://ar5iv.labs.arxiv.org/html/2603.26512)、[Query2CAD](http://arxiv.org/pdf/2406.00144) | 要进程隔离与超时 | ✅ **能** |
| **C** | 多智能体编排 | 拆解 / 编码 / 渲染 / 纠错分工 | [Multi-Agent-CAD](https://github.com/Pan-Chera/Multi-Agent-CAD)、[ASSEMCAD](https://arxiv.org/html/2607.05123v1) | token 成本 | ✅ 能 |
| **D** | 序列 / DSL 生成 | 专用模型吐 CAD 命令序列或受限 DSL | DeepCAD、[Text2CAD](https://papers.neurips.cc/paper_files/paper/2024/hash/0e5b96f97c1813bb75f6c28532c2ecc7-Abstract-Conference.html)、[FlexCAD](https://arxiv.org/abs/2411.05823)、Zoo KCL | 要 8B+ 专模与配对数据；操作集窄 | ❌ 难 |
| **E** | 生成式网格 | 扩散/流匹配直接出 mesh | [TRELLIS](https://github.com/microsoft/TRELLIS)、[Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)、[TripoSG](https://github.com/VAST-AI-Research/TripoSG) | 产物不可参数化编辑 | ✅（但工程无用）|
| **F** | 逆向重建 | 图/点云/图纸 → 参数化代码 | [CAD-Recode](https://github.com/filaPro/cad-recode)、[cadrille](https://github.com/AIRI-Institute/cadrille)、[CAD-Coder](https://github.com/anniedoris/CAD-Coder) | 单件、几何简单 | ✅ 能（1.5–2B）|
| **G** | 模板 + 参数 + 规则 | 不生成几何，只选模板/填参/跑规则 | [DriveWorks](https://driveworks.co.uk/products/driveworksxpress/)、`step.parts`、[cq_warehouse](https://cq-warehouse.readthedocs.io/en/stable/)、本仓 `standard_parts.py` | 覆盖域窄，模板要人写 | ✅ **最友好** |
| **H** | GUI / API 代理 | 看屏点选，或调宿主 API 改既有模型 | [NX Select Similar](https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/)、Adam、[Fusion Assistant](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html) | 脆；受 UI 限制 | ⚠️ |
| **I** | 知识/检索助手 | 不出几何，只答规则与选型 | [Onshape AI Advisor](https://onshape.com/en/features/ai-advisor)、Leo AI | 不产生模型 | ✅ 能 |

**两条跨切面**（不属于某一类，任何类都可以加）：
- **横切 X1：检索增强**——把 API 文档/示例/零件库做成可检索库（见 §3 的 E3）；
- **横切 X2：约束求解外置**——模型只写约束，坐标交给求解器（见 §3 的 E2-6）。

---

## 2. 表示层：六种表示与它们的代价

| # | 表示 | 定义 | 代表 | 对普通模型 | 可编辑性 | 来源 |
|---|---|---|---|---|---|---|
| 1 | **可执行代码** | 生成 CadQuery / build123d / FreeCAD / SW API 的 Python | CAD-Recode、`text-to-cad`、本仓 | ★★★★★ 开放词表、可程序化合成、可执行即免费验证 | ✅ 可 diff、可重跑 | [CAD-Recode 论文](https://arxiv.org/abs/2412.14042) |
| 2 | 命令序列 token | 把 CAD 操作编码成定长 token（16 参数/命令） | DeepCAD、Text2CAD、CAD-MLLM | ★★ 封闭词表、要从零训 | ⚠️ 需导入 CAD | [DeepCAD](https://arxiv.org/abs/2105.09492) |
| 3 | 分层结构化文本 | 曲线/环/面/草图/拉伸六层级 + 层级 mask | FlexCAD | ★★ 要 8B | ✅ | [FlexCAD](https://arxiv.org/abs/2411.05823) |
| 4 | 受限 DSL | KCL / CSG / OpenSCAD | Zoo KCL、OpenSCAD | ★★★ 表达力受限 | ✅ | [KCL 文档](https://docs.zoo.dev/docs/kcl) |
| 5 | 特征树 JSON | 为「AI 可读可改」专门设计的特征树 | cadjson 一类（G 路）| ★★★★ | ✅ | 见 §4 |
| 6 | 网格 / 3D 高斯 | 三角网或高斯点 | TRELLIS、TripoSG、LGM | ★★★ | ❌ 不可参数化 | [TRELLIS](https://github.com/microsoft/TRELLIS) |

**关键结论（有数据）**：表示越「像自然语言」，越吃模型先验。代码表示的 SOTA 由 **1.5B / 2B** 模型拿到（CAD-Recode 用 Qwen2-1.5B、cadrille 用 Qwen2-VL-2B，来源：[两篇论文](https://arxiv.org/abs/2505.22914)），而自然语言式/图像条件式表示要 8B（FlexCAD、CAD-Llama）到 13B（CAD-Coder）。**token 序列派参数量最小，但要从零训、词表封闭，反而不算「对普通模型友好」。**

---

## 3. 逐环节做法总目录（这是「每个步骤都有哪些做法」）

> 9 个环节，每环节列全部已知做法、代表、效果、代价、**什么时候选它**。

### E1 需求理解与澄清

| # | 做法 | 代表 | 效果/代价 | 什么时候选 |
|---|---|---|---|---|
| 1-1 | 一次性提示词直出 | 多数开源项目 | 最省，歧义靠模型猜 | 任务简单、可重试 |
| 1-2 | 批量追问（问题清单一次问完） | 本仓 `design_ir.py` 的 `ElicitBatch`/`Elicitation` | 多一轮交互，歧义显著下降 | 工程件、有尺寸要求 |
| 1-3 | 规格文件 + 每个值标来源（`origin: user_stated` / 推定） | [anvilate](https://github.com/clay-good/anvilate) | 要人写 spec；换来可审计 | 批量、可追溯场景 |
| 1-4 | 强模型当 planner 现场澄清 | [CAD-Assistant](https://github.com/dimitrismallis/CAD-Assistant)（GPT-4o） | 依赖强模型（见 §4 的数字） | 只做一次性、不计成本 |
| 1-5 | 图纸/草图当输入（人画意图） | Free2CAD、Sketch2CAD、Backflip | 人便宜、机器省 | 有参考图/草图 |

### E2 表示与「算」的归属（**最关键的决策**）

| # | 做法 | 代表 | 说明 |
|---|---|---|---|
| 2-1 | 让模型自由写代码 | 多数开源 | 表达力最强，错误最多 |
| 2-2 | 让模型只调**受限操作集** | [ghbalf/freecad-ai](https://github.com/ghbalf/freecad-ai)（50 个结构化操作）、`openscad-mcp` 的 `list_templates` | 更安全可验，覆盖域窄 |
| 2-3 | 让模型只**选模板 + 填参** | `step.parts`、cq_warehouse、DriveWorks | 闭集选择，最省模型能力 |
| 2-4 | 让模型只写**约束**，坐标交求解器 | [SLVSX](https://github.com/snoble/slvsx-cli)、FreeCAD Sketcher | 约束过定义/冗余由求解器报 |
| 2-5 | 让模型只产**装配 JSON/参数**，几何由零件族工厂出 | [ASSEMCAD](https://arxiv.org/html/2607.05123v1)（8 个 base-frame factory）| 装配级任务；工厂要人写 |
| 2-6 | 让模型输出**受限 DSL** | Zoo KCL、OpenSCAD | 表达力换稳定性；**但 DSL 不自动合法**（见 §4 的 Invalidity Ratio）|

### E3 知识注入（把「记住 API」换成「查一下」）

| # | 做法 | 代表 | 效果 | 代价 |
|---|---|---|---|---|
| 3-1 | **版本化 API 文档检索**（关键词即可，不必向量） | CADSmith KB1（155 条方法 + 28 个可跑示例）、LL3M 的 BlenderRAG | LL3M：每脚本可用复杂操作 5.86 vs 1.21（来源：[LL3M](https://ar5iv.labs.arxiv.org/html/2508.08228)） | 按库版本维护语料 |
| 3-2 | **示例/零件库少样本检索** | `mcp-cadquery` 的 `part_library`+`search_parts`、cq_warehouse | 消融：few-shot→zero-shot 偏差 0.126→0.141（来源：[CADCodeVerify 消融](https://arxiv.org/abs/2410.05340)） | 检索错件会固化错误 |
| 3-3 | **错误模式库**（trigger → 根因 → 修法） | CADSmith KB2（25 条） | 并入回环使用 | 人工积累 |
| 3-4 | **标准件表 / 选型表可查** | 本仓 `standard_parts.py`、`selection_calc.py` | 直接消除「算」与「查表」两格 | 覆盖域窄 |
| 3-5 | 把用户的历史决定注入（记忆） | 本仓 Hindsight 记忆机制 | 减少重复问答 | 需维护 |

### E4 生成

| # | 做法 | 代表 | 代价 |
|---|---|---|---|
| 4-1 | 单次代码生成 | 多数 | 一次错全错 |
| 4-2 | **采样多候选择优** | CAD-Recode：采 10 个候选按 CD 选优（来源：[论文](https://arxiv.org/abs/2412.14042)） | 算力×N |
| 4-3 | **微调专模**（7–8B） | CAD-Llama、FlexCAD、CAD-Coder | 要配对数据与 GPU |
| 4-4 | **程序化合成训练数据**（零人工标注） | CAD-Recode（100 万条，含 `ValidateCADModel`/`CheckDuplicate`） | 要写生成器 |
| 4-5 | 强化学习后训练 | cadrille（GRPO/DPO/CPPO） | 工程复杂 |
| 4-6 | 多智能体分工生成 | Multi-Agent-CAD、ASSEMCAD | token 成本 |

### E5 执行内核

| # | 做法 | 代表 | 关键点 |
|---|---|---|---|
| 5-1 | 进程内 COM / 宿主 API | 本仓主路线、Fusion 插件 | STA/弹窗会死锁 |
| 5-2 | **进程外客户端 + 宿主主线程执行** | [faust-machines/fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server)：stdio MCP → TCP:9876 → 插件 → 主线程 CustomEvent | 结构性避开死锁 |
| 5-3 | 纯离线内核（不碰 COM） | 本仓 `compiler.py`（docstring 明写不 import COM 模块） | 可离线批量 |
| 5-4 | 保证流形输出的内核 | [manifold](https://github.com/elalish/manifold)（非法几何编译不出来） | 换范式（网格 vs B-rep）|
| 5-5 | 沙箱隔离子进程 + 超时 | CADSmith（60 s 隔离子进程，内环 ≤3 次） | 回环的前置条件 |

### E6 验证（决定「能不能用」）

| # | 做法 | 代表 | 效果 | 局限 |
|---|---|---|---|---|
| 6-1 | **内核级硬门禁**（体积/包围盒/面边点计数/`BRepCheck_Analyzer`） | CADSmith；本仓 `sw-automation-skill/advanced_geometry_ocp.py` | CADSmith IoU 中位 0.8085→0.9629（来源：[CADSmith](https://ar5iv.labs.arxiv.org/html/2603.26512)） | 各内核对「有效」定义不同 |
| 6-2 | 网格级校验（水密/绕序/欧拉数） | trimesh | —— | 实战：1990 个实体里 5 个不水密照报体积（来源：[spatialworkflow](https://spatialworkflow.io/mesh-not-watertight-volume-wrong/)）|
| 6-3 | 求解器诊断（DoF/冗余/过定义） | FreeCAD Sketcher、SLVSX | —— | 对初值与顺序敏感 |
| 6-4 | **可执行 DFM 规则** | [vcad](https://github.com/ecto/vcad)（TOML 工艺规则包）、[ai-cad](https://github.com/ai-cad-labs/ai-cad)（JSON 规则 + 回归门）、本仓 `manufacturing_rules.py` | —— | 规则覆盖度＝护城河 |
| 6-5 | 视觉复核（多视图喂 VLM） | CADSmith 三视图 Judge、CADCodeVerify | 去掉视觉后 CD 1.42→49.68（来源：CADSmith）| 会漏（缝隙漏判）、贵 |
| 6-6 | 独立评审模型（Judge≠生成） | CADSmith（Sonnet 生成 / Opus 判）| 整环 IoU 0.81→0.96 | 双模型成本，裁判也会错 |

### E7 修复回环（**杠杆最大**）

| # | 做法 | 代表 | 效果 |
|---|---|---|---|
| 7-1 | traceback 回传重写 | Query2CAD（`error_iter` 默认 3）、CADSmith | 通用 LLM 单发失败率 21–92% → 迭代 **3–4%**（来源：[CodeGen-3D](https://scholarworks.sjsu.edu/faculty_rsca/6835/)）|
| 7-2 | 错误模式库辅助（命中关键词给 before/after） | CADSmith KB2 | 无单独消融 |
| 7-3 | 几何度量回传（改到数值达标记为止） | CADSmith | 与 7-1 合并计 |
| 7-4 | 一次只改一处 + 重编译比对 | ai-cad 的回归门、LLM-Aided DFM | 防止连锁破坏 |

★ 反例（F 路实测）：错误信息会误导模型「把报错那行删掉」（LL3M 观察到）⇒ 回环需要「错误模式库」兜底。

### E8 交付

| # | 做法 | 代表 | 判据 |
|---|---|---|---|
| 8-1 | 只出网格 | Meshy/Rodin/Tripo/Spline | 导出清单**无 STEP/IGES** |
| 8-2 | **出 STEP/B-rep** | Zoo、`text-to-cad`、本仓 | 导出清单**有 STEP** |
| 8-3 | 出工程图 PDF（视图/尺寸/孔标注/标题栏） | `text-to-cad` 的 `engineering-drawing` skill | 【事实】官方 README 列明 |
| 8-4 | 出 DFM 评分/可制造性 | `dfm` skill、ai-cad、vcad、HCL DFMPro（闭源） | E 路核 14 家产品，**无一家**给出可验证定义 |
| 8-5 | **诚实账本**（未验标 `not evaluated`，未过盖 `UNVALIDATED`） | anvilate；本仓 `capabilities.yaml`（level+evidence） | 见 §5 |

### E9 人机边界

| # | 做法 | 代表 | 说明 |
|---|---|---|---|
| 9-1 | 人只在两端（意图 / 判定） | 商业共识：Autodesk、Onshape、Siemens | 【事实】官方原文见 §4 |
| 9-2 | 人当场点选（模板选择 / 4 图里挑 1） | Spline AI（强制在 4 张预览里选） | 把不确定性交给人 |
| 9-3 | 变更前必须批准 | Adam（官方 pause for approval） | 面向既有模型改造 |

---

## 4. 各家的技术路径（逐项目）

> 列：项目 | 类 | 表示 | 生成 | 编排 | 验证 | 交付 | 许可 | 来源

### 4.1 开源·工程 CAD（代码路线）

| 项目 | 类 | 表示 | 生成 | 编排 | 验证 | 交付 | 许可 |
|---|---|---|---|---|---|---|---|
| [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | B+G | build123d 代码 | LLM + 12 个技能 | 技能分阶段（含 `step.parts` 查标准件、`dfm` 出证据）| DFM 规则 + 工程图 | STEP/STL/3MF/GLB + PDF | MIT |
| [Amagine3D](https://github.com/amagine-ai/Amagine3D) | B | build123d/OCP | LLM | 语义场景 → 真 B-rep | **只读回导出文件判成败**（特征归属/壁厚/干涉）| STEP/STL/3MF | Apache-2.0 |
| [Multi-Agent-CAD](https://github.com/Pan-Chera/Multi-Agent-CAD) | C | build123d | LangGraph 多智能体 | 拆解/编码/渲染/纠错 | 渲染回读 | STEP/STL/GLB | MIT |
| [agentcad](https://github.com/jdilla1277/agentcad) | B | build123d | LLM | CLI+MCP，几何度量回环 | 几何度量 | STEP/PNG/STL | Apache-2.0 |
| [cadquery-llm-skill](https://github.com/jmwright/cadquery-llm-skill) | — | CadQuery | 提示词技能包 | 教 BRep 心智模型 + 选择器表 + 反模式 | 无 | — | Apache-2.0 |
| [CADAM](https://github.com/Adam-CAD/CADAM) | A | OpenSCAD（WASM） | LLM | 生成与求值分层 | 无 | 网格/B-rep 取决于内核 | GPL-3.0（只读思想）|

### 4.2 开源·逆向与学术

| 项目 | 类 | 表示 | 模型 | 数据 | 验证 | 许可 |
|---|---|---|---|---|---|---|
| [CAD-Recode](https://github.com/filaPro/cad-recode) | F | CadQuery 代码 | Qwen2-1.5B + 点云编码 | 程序化合成 100 万条 | CD/IoU，采样 10 候选选优 | **CC BY-NC 4.0**（非商用）|
| [cadrille](https://github.com/AIRI-Institute/cadrille) | F | CadQuery 代码 | Qwen2-VL-2B | 合成 + 在线 RL | CD/IoU | Apache-2.0 |
| [CAD-Coder](https://github.com/anniedoris/CAD-Coder) | F | CadQuery 代码 | LLaVA-1.5 / Qwen2.5-Coder-14B | GenCAD-Code 163,671 对 | VSR/IoU | Apache-2.0 |
| [CAD-Assistant](https://github.com/dimitrismallis/CAD-Assistant) | H+B | FreeCAD Python | **GPT-4o planner** | 无训练 | 外部约束检查 + 渲染 | 见仓库 |
| [FlexCAD](https://github.com/microsoft/FlexCAD) | D | 六层级结构化文本 | Llama-3-8B（LoRA 3.4M）| DeepCAD 178,238 | PV 有效率 93.4% | MIT |
| [Text2CAD](https://github.com/SadilKhan/Text2CAD) | D | 命令序列 token | BERT + 8 层 Transformer | DeepCAD ~170K + 660K 文本 | 命令/参数准确率 | **CC BY-NC-SA** |
| [DeepCAD](https://github.com/rundiwu/DeepCAD) | D | 命令序列 token | 4 层 Transformer 自编码 | 178,238 个 Onshape 模型 | ACC/CD/Invalid Ratio | MIT |
| [BlenderLLM](https://arxiv.org/abs/2412.14203) | A | bpy 脚本（网格）| Qwen2.5-Coder-7B | BlendNet 8k | 语法错误率 E_syntax + GPT-4o 裁判 | 论文 |

### 4.3 开源·生成式网格

| 项目 | 类 | 输入→输出 | 显存（README 明称）| 许可 | 来源 |
|---|---|---|---|---|---|
| [TRELLIS](https://github.com/microsoft/TRELLIS) / [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) | E | 图/文 → 网格 GLB | ≥16 GB / ≥24 GB | **MIT** | 仓库页 |
| [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) / 2.1 / Omni | E | 图 → 带纹理网格 | 6 GB / 16 GB | 腾讯社区许可（排除 EU/UK/韩）| 仓库页 |
| [TripoSG](https://github.com/VAST-AI-Research/TripoSG) / [TripoSR](https://github.com/VAST-AI-Research/TripoSR) | E | 图 → 网格 GLB | ≥8 GB / ~6 GB | **MIT** | 仓库页 |
| [InstantMesh](https://github.com/TencentARC/InstantMesh) | E | 图 → 网格 | 未标 | Apache-2.0 | 仓库页 |
| [Step1X-3D](https://github.com/stepfun-ai/Step1X-3D) | E | 图 → 几何+纹理 | 未标 | Apache-2.0 | 仓库页 |
| [Zero123++](https://github.com/SUDO-AI-3D/zero123plus) | E(前置) | 图 → **多视角图**（不产网格）| ~5 GB | Apache-2.0 | 仓库页 |
| [LGM](https://github.com/3DTopia/LGM) | E | 文/图 → **3D 高斯**（不直接产网格）| 未标 | MIT | 仓库页 |

### 4.4 桥接层（AI → CAD 软件）

| 项目 | 桥的软件 | 形态 | 关键设计 | 许可 |
|---|---|---|---|---|
| [faust-machines/fusion360-mcp-server](https://github.com/faust-machines/fusion360-mcp-server) | Fusion 360 | MCP + add-in | **进程外客户端 + 主线程 CustomEvent 执行**（93 工具）| MIT |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | FreeCAD | MCP + 插件 | 10 个左右工具 + 可执行任意 Python | MIT |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | Blender | MCP + addon | 原名 blender-mcp | MIT |
| [mcneel/RhinoAI](https://github.com/mcneel/RhinoAI) | Rhino 8/9 | MCP + C# 插件 | **厂商官方**，默认分支 `rhino-9.x` | MIT |
| [puran-water/autocad-mcp](https://github.com/puran-water/autocad-mcp) | AutoCAD LT | MCP | **只有 8 个合并工具**却 588★ | MIT |
| [pzfreo/build123d-mcp](https://github.com/pzfreo/build123d-mcp) | build123d/OCCT | MCP | 反馈调试 | Apache-2.0 |
| [SLVSX](https://github.com/snoble/slvsx-cli) | SolveSpace | CLI | 明写「designed for AI agents」的求解器 | GPLv3（只读思想）|

### 4.5 商业产品（工序位置）

| 产品 | 类 | AI 放在哪一段 | 刻意不放 | 交付 |
|---|---|---|---|---|
| Zoo Text-to-CAD / Zookeeper | A | 自然语言 → **KCL 代码** | 不开放模型（官方 MCP 测试断言 `text_to_cad` 未注册）| B-rep/STEP |
| Fusion — Autodesk Assistant | H | 命令级执行 + AutoTimeline（几何→参数化历史）| 【事实】「不能做草图尺寸或约束」「可能报成功但几何不对，必须目视核验」| 原生可编辑 |
| Onshape AI Advisor | I | 只检索文档并带引用回答 | 【事实】逐条否认生成设计/预测错误/工程决策/生成式设计 | 无几何 |
| Siemens NX（Copilot / Select Similar） | H | 重复编辑的「选择/识别」段 + 标注 | 【事实】amplify your expertise, not replace it | 原生可编辑 |
| PTC Creo Generative Design | E/D 混 | 拓扑优化方案生成 | 「可制造」以**人给的工艺约束**为前提 | 可编辑 |
| Adam（CAD copilot） | H | 在**既有特征树**上改 | 【事实】变更前 pause for approval | 可编辑 |
| Backflip | F | 图纸/照片/扫描 → **特征树** | Photo 模式要人给一个已知尺寸定标 | 参数化 + 特征树 |
| DriveWorks | G | **无 AI**：捕获参数→建表单→写规则 | 不确定性只落在可审的规则上 | SOLIDWORKS 原生文件 |
| Meshy / Rodin / Tripo / Spline | E | 造型 + 贴图 | 无 STEP/IGES；Spline 官方明写「别指望高精度」| 网格 |

---

## 5. 「可制造」这件事：全行业都含糊

- **E 路核过 14 家商业产品，没有一家给出可验证的「可制造」定义**（公差/DFM 规则/工艺对应）。Creo 的 manufacturable 是【宣称】，实义是「人所给工艺约束下的优化结果」。
- 开源侧只有两个可运行骨架：[vcad](https://github.com/ecto/vcad)（TOML 工艺规则包 + BRep 打分）、[ai-cad](https://github.com/ai-cad-labs/ai-cad)（JSON 规则 + 严重度 + 回归门）。
- 学界只有一篇预印本在做「LLM 辅助 DFM 重设计」（[arXiv 2609.05559](https://arxiv.org/abs/2609.05559)，作者自述 preliminary）。
- 本仓已有零件：`manufacturing_rules.py`（螺纹/间隙孔/特征顺序/降级阶梯）、`rule_service.py`（**公式与依据分开** + 权威性/新鲜度检查）。

---

## 6. 几组值得记住的数字（带来源）

| 数字 | 含义 | 来源 |
|---|---|---|
| 21–92% → 3–4% | 通用 LLM 单发失败率 → 迭代 agent 失败率 | [CodeGen-3D](https://scholarworks.sjsu.edu/faculty_rsca/6835/) |
| 0.8085 → 0.9629 | IoU 中位（加硬门禁前后）| [CADSmith](https://ar5iv.labs.arxiv.org/html/2603.26512) |
| 1.42 → 49.68 | 去掉视觉复核后的平均 CD（假收敛证据）| [CADSmith](https://ar5iv.labs.arxiv.org/html/2603.26512) |
| 5.86 vs 1.21 | 每脚本可用复杂操作数（有/无文档 RAG）| [LL3M](https://ar5iv.labs.arxiv.org/html/2508.08228) |
| 0.791 / 0.614 | SGPBench 2D 得分（GPT-4o / GPT-4 mini）| [CAD-Assistant](https://arxiv.org/abs/2412.13810) |
| 15.7% | CAD-Llama 多任务平均超出 GPT-4 的**相对**幅度 | [CAD-Llama](https://arxiv.org/abs/2505.04481) |
| 100 万条 | CAD-Recode 程序化合成训练数据量 | [CAD-Recode](https://arxiv.org/abs/2412.14042) |
| 93.4% | FlexCAD 可渲染有效率 | [FlexCAD](https://arxiv.org/abs/2411.05823) |
| 0.126 → 0.141 | few-shot → zero-shot 的偏差劣化 | [CADCodeVerify](https://arxiv.org/abs/2410.05340) |

---

## 7. 本仓在这张图上的位置（实测，非计划）

| 环节 | 本仓现状 | 证据 |
|---|---|---|
| E1 澄清 | ✅ 有 `DesignIR` / `ElicitBatch` / `OutboundPermit` | `scripts/engineering/design_ir.py` |
| E2 表示 | ✅ 代码路线 + 四类 IR | `scripts/engineering/compiler.py` |
| E3 检索 | ⚠️ 只有任务域分面检索接了工具 | `mcp-server/tool_specs_batch115.py`（引用 `engineering.catalog` 4 处）|
| E4 生成 | ✅ 工具层大 | 见 `AGENTS.md` §一 |
| E5 执行 | ✅ COM + `tools/sw_guard.py` 护栏 | `tools/sw_guard.py` |
| E6 验证 | ⚠️ 有零件（`manufacturing_rules.py`、`rule_service.py`、`BRepCheck_Analyzer`），未成体系 | `scripts/engineering/manufacturing_rules.py` |
| E7 回环 | ❌ 无（无错误模式库、无自动重写循环）| 本次研核实测 |
| E8 交付 | ✅ 诚实账本 | `capabilities.yaml`（verified 100 / stitched 37 / not_implemented 3，来源：该文件实测）|
| E9 接线 | ❌ **最大缺口**：58 个 engineering 模块里只有 `catalog` 被工具层引用 | 本次 `mcp-server/*.py` 实测 |

---

## 8. 查不到清单（避免重复检索）

| 类别 | 查不到的 |
|---|---|
| 模型/权重 | Zoo 的 text-to-CAD 模型；Hunyuan3D-2.5（仓库 404）；Meshy 权重；Rodin（404）；MeshGPT 官方仓库；CAD-Llama 官方代码 |
| 论文 | CAD 生成方向的专门蒸馏论文 |
| 图纸 | GD&T + 剖视 + 尺寸链**完整**转 3D 的开源实现 |
| 插画 | 机械插画/爆炸图 → 可编辑几何（最接近者只出知识图谱）|
| 知识 | 开源的标准件选型表 + 选型逻辑 |
| 手段 | 可执行 DFM 接进回环；求解器诊断回传闭环；渲染回环做服务器默认件；「选模板」决策的评估 |
| 配置 | 1.5B/2B 模型的纯 CPU 推理数据 |

---

## 9. 许可速查

| 许可 | 项目 | 用途 |
|---|---|---|
| MIT / Apache-2.0 | text-to-cad、Amagine3D、Multi-Agent-CAD、agentcad、build123d-mcp、cadquery-llm-skill、fusion360-mcp-server、TRELLIS(.2)、TripoSG、TripoSR、InstantMesh、Step1X-3D、vcad、ai-cad、anvilate、DriveWorks（免费版）| 可借鉴；**Apache 系带 NOTICE** |
| 有条件商用 | Hunyuan3D-2.x/Omni（排除 EU/UK/韩 + MAU 条款）、SF3D/SPAR3D（年营收 <100 万美元免费）| 逐条读正文 |
| 非商用 | Hunyuan3D-1（NON-COMMERCIAL）、MeshAnything（S-Lab 1.0）、cad-recode（CC BY-NC 4.0）、Text2CAD（CC BY-NC-SA 4.0）| 只读思想 |
| GPL/AGPL/LGPL | CADAM、freecad-ai、SLVSX、orcaslicer-mcp、mcp-3D-printer-server | 只读思想 |
| 无 LICENSE | CraftsMan3D、NURBGen、Text-to-CadQuery、CAD-MLLM、CAD-GPT、hedless/onshape-mcp、cadquery-mcp-server | 默认全版权保留 |

---

## 10. 一句话总图

**所有 AI 自动建模工具 = ①表示 + ②编排 + ③验证 的三元组。**
表示决定「普通模型能不能用」（代码 > 特征树 > DSL > 序列 > 网格）；编排决定「错了能不能修」（回环 > 单发）；验证决定「能不能用」（硬门禁 + 可造性 > 视觉 > 只跑通）。
**九类架构里，只有 B（代码+回环）、C（多智能体）、G（模板+规则）在普通模型上成立，且 G 最省、B 最通用、C 最稳。**
