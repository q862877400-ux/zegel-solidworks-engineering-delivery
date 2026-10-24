# AI 自动建模 · 技术路径与现有效果 · 分析汇总

> **性质**：本文件只做**分析与汇总**，不给出判断、不做推荐、不做优先级排序。
> 所有数字均标注出处；凡属厂商自述、未独立复现、未公布的，均在原文位置标明。
> **数据来源**：`docs/survey/cards/` 下 50 张逐项目卡片（共约 756 KB）+ `docs/survey/architecture-matrix.md`
> 与 `docs/survey/step-matrix.md`（由 `scripts/gen_survey_matrix.py` 从卡片机读 tag 重算，非手写）
> + `docs/ai-cad-landscape-report.md`（v3 全景报告）+ `docs/survey/state.json`（偏差记录）。
> **汇总时间**：2026-10-24。

---

## §0 汇总口径（先说清楚这份报告能证明什么、不能证明什么）

### 0.1 证据等级：50 张卡里只有 4 张是「实测」

| 证据等级 | 张数 | 含义 |
|---|---|---|
| **读码** | **34** | 读过源码，技术路径与机制有代码出处 |
| **元数据** | **12** | 闭源产品，只能读官网/文档/检索索引正文，无源码 |
| **实测** | **4** | 本机真跑过（`triposr` · `cadam` · `mcp-cadquery` · `fusion360-mcp-server`）|

（来源：`docs/survey/architecture-matrix.md` 第 7 列统计）

★ **这 4 张「实测」里，只有 TripoSR 是「模型真跑出东西」**；其余 3 张跑的是**仓库自带单测**
（`fusion360-mcp-server` 367 passed / `blender-mcp` 494 passed / `cadam` 36 passed / `mcp-cadquery` 7 failed + 80 passed），
按 `docs/survey/state.json` 的 `deviations` 原文：「那是『包能装、单测能跑』的证据，**不是建模能力验证**」。

### 0.2 本报告不回答的问题

- 不回答「哪条路线最好」
- 不回答「本项目该走哪条路」
- 不回答「哪些数字可信到什么程度」——只陈述「该数字的出处与是否被独立复现」

---

## §1 技术路径的分类结构

### 1.1 十类架构与真实分布（50 家）

| 类 | 架构 | 家数 | 代表 |
|---|---|---|---|
| **H** | GUI/API 代理（改既有模型）| **15** | fusion360-mcp · freecad-mcp · blender-mcp · autocad-mcp · rhinoai · freecad-ai · build123d-mcp · adam · 4 家 SW 竞品 · leo-ai · sky 系 |
| **E** | 生成式网格 | **13** | hunyuan3d-2 · trellis · triposg · triposr · instantmesh · sf3d · spar3d · step1x-3d · meshy · rodin · tripo · spline · ptc-creo |
| **B** | 代码回环（写→执行→读错→重写）| **7** | agentcad · amagine3d · earthtojake-text-to-cad · cad-assistant · cadam · mcp-cadquery · zoo |
| **D** | 序列/DSL 专模 | **5** | deepcad · text2cad · flexcad · img2cad · drawing2cad · plankassembly |
| **F** | 逆向（图/点云/图纸→代码）| **4** | cad-coder · cad-recode · cadrille · img2cad |
| **I** | 知识/检索助手（不出几何）| **3** | onshape-ai-advisor · siemens-nx-ai · cadquery-llm-skill |
| **C** | 多智能体 | **1** | multi-agent-cad |
| **G** | 模板+参数+规则 | **1** | ptc-creo-generative |
| **J** | 世界模型/几何状态预测 | **1** | sky-001 |
| **A** | 代码单发 | **0**（卡片里无独立 A 类样本）| — |

（来源：`docs/survey/architecture-matrix.md` 第 3 列统计；A 类在原报告 §1 有定义但 50 张卡无成员）

★ 分布形态：**H（代理）+ E（网格）合计 28 家，占 56%**；真正「代码即 CAD」的 B/F 合计 11 家。

### 1.2 六个维度上的分布

**中间表示**（决定能否进 CAD）

| 表示 | 家数 | 能否进 CAD（报告原文表述）|
|---|---|---|
| `code` | **15** | ✅ 多数能出 STEP |
| `mesh` | **13** | ❌ 不能（除 Creo 走重建）|
| `feature-tree` | **11** | ✅ 能（改既有模型）|
| `sequence` | **8** | ⚠️ 需导入器 |
| `constraint` | 1 | ✅（求解器出解）|
| `dsl` | 1 | ⚠️ 出网格 |
| `none` | 1 | — |

（来源：`docs/survey/step-matrix.md`）

**编排**（决定错了能不能修）

| 编排 | 家数 | 构成 |
|---|---|---|
| `single` | **28** | 学术模型全部单发 + 网格云服务全部单发 + 只读桥 |
| `loop` | **13** | 几乎全是开源工具 |
| `none` | 4 | 只答问/只给能力 |
| `human-approve` | **3** | 全部是商业产品（adam · fusion-assistant · spline-ai）|
| `multi-agent` | 1 | multi-agent-cad |
| `template` | 1 | ptc-creo |

（来源：`docs/survey/step-matrix.md`）

**验证**（决定能不能用）

| 验证手段 | 家数 | 报告对其强度的表述 |
|---|---|---|
| `visual` | **20** | 「最弱：13 家网格只能看图 + 5 家产品靠人眼 + 少数代码路线」|
| `numeric` | **13** | 「中：学术的 CD/IoU（注意多为**择优值**）+ fusion360 的质量/包围盒/体数回带」|
| `run-only` | 7 | 「最弱一档：能跑就算过（含 4 家 SW 竞品里的 3 家）」|
| `none` | 4 | 无验证 |
| `dfm-rules` | 2 | 「最强：每条结论带测量证据 + 引用规则」|
| `solver` | 2 | 「强：求解器收敛」|
| `export-readback` | 1 | 「强：只认重新读回的文件」|
| `geometry-gate` | 1 | 「强：线稿→形状程序的几何校验」|

（来源：`docs/survey/step-matrix.md`；强度措辞引自 `docs/ai-cad-landscape-report.md` §2.3）

**交付**：`mesh` **20** · `STEP` **17** · `none` **9** · `sequence` 3 · `drawing` 1（来源：`step-matrix.md`）

### 1.3 工具粒度：九个真实样本，跨度 66 倍

| 项目 | 工具数 | 切法 |
|---|---|---|
| autocad-mcp | **8** 个工具分派 **72** 个操作 | 合并式极端：契约只写 docstring |
| blender-mcp | **9**（+5 App-only）| 逐操作交给模型写 bpy 代码 |
| freecad-mcp | **17** | 原语式 + 万能代码口 |
| slvsx-cli | **39** 种约束 + 8 类实体 | 只暴露约束词汇，不暴露坐标 |
| rhinoai | **42** | 只做读状态/选择/相机 |
| freecad-ai | **61** | 受限操作集 + 唯一逃逸口 |
| fusion360-mcp-server | **93** | 每条改模型命令回带质量/包围盒/体数增量 |
| Slacker-LLC（SW 竞品）| **92** | 一动词一工具 + mm/deg 契约 + `GetWhatsWrong` |
| Eduardof0nt（SW 竞品）| **187** | 一动词一工具 + **零测试** |
| andrewbartels1（SW 竞品）| **133** | 单一 STA 线程执行器 + 熔断 + 连接池 |
| vespo92（SW 竞品）| **96**（默认注册 86）| Node/TS win32 COM 网关，复杂操作生成 VBScript |

（来源：`docs/survey/cards/` 各卡 §3；`docs/ai-cad-landscape-report.md` §2.5）

---

## §2 现有效果：能查到的一手读数

### 2.1 唯一一次「模型真跑出几何」的实测

| 项 | 读数 | 出处 |
|---|---|---|
| 模型 | TripoSR（单图 → 三平面 NeRF → 抽面）| `docs/survey/cards/triposr.md` |
| 硬件 | RTX 4080 SUPER 16 GB | 同上 §4 |
| 峰值显存 | **1,866.5 MB**（allocated）| 同上；原始 JSON `D:\ai3d-survey\logs\triposr-run.json` |
| 前向耗时 | **0.9 秒** | 同上 |
| 输出 | **3,001 顶点 / 5,998 面**，watertight | 同上 |
| ★ 该次运行的性质 | **打补丁后跑通**：`torchmcubes` 本机编不过（三层失败链已记录），改用 `skimage.measure.marching_cubes` 兜底 ⇒ 顶点顺序可能与原实现不同，未逐点比对 | `docs/survey/state.json` `deviations` 第 1 条 |
| 官方宣称 | A100 上「不到 0.5 秒」 | 卡 §1 引 README |

### 2.2 仓库自带单测的真跑读数（4 家，均为「包能装、单测能跑」）

| 项目 | 单测结果 | 环境说明 |
|---|---|---|
| fusion360-mcp-server | **367 passed / 15.69 s** | `PYTHONUTF8=1` 下；默认 GBK 环境 **17 failed / 350 passed**，17 条全为同一编码类问题 |
| blender-mcp | **494 passed** | 纯 Python 单测；「服务端能装，真机跑不了」|
| cadam | **36 passed** | — |
| mcp-cadquery | **7 failed / 80 passed** | 在临时副本内跑，宿主解释器需绕开 3.14 |

（来源：`docs/survey/cards/` 各卡 §4；`docs/survey/state.json` `deviations` 第 3 条）

### 2.3 各项目自述的效果数字（**均标注为未独立复现**）

| 项目 | 自述数字 | 复现状态 |
|---|---|---|
| agentcad | 「48% higher CAD Score、21.8% lower cost、2.5× valid outputs」| 作者自写「那是单次 run、不是匹配基线的对照」（卡 §1 引 `README.md:19-…`）|
| SKY-001 | 自测 CAD IoU **79.7%** / 3.9 秒 | 「厂商自测，无第三方复现」；另有独立批评指 BIM 绝对质量自测平均 IoU **43.6%**（`sky-001.md` §5 引 orcarouter）|
| FlexCAD | 可渲染有效率 **93.4%** | 论文数字 |
| CADSmith | IoU 中位 **0.8085 → 0.9629**（加硬门禁前后）；去掉视觉复核后平均 CD **1.42 → 49.68** | 论文数字 |
| CodeGen-3D（IEEE Access 2026）| 通用 LLM 单发失败率 **21–92%** → 迭代 agent **3–4%** | 论文数字 |
| CAD-Llama | 多任务平均超出 GPT-4 的**相对**幅度 **15.7%** | 论文数字 |
| LL3M | 每脚本可用复杂操作数 **5.86 vs 1.21**（有/无文档 RAG）| 论文数字 |
| CAD-Recode | 程序化合成训练数据 **100 万条** | 论文数字 |

（来源：`docs/ai-cad-landscape-report.md` §7「数字索引（可复核）」）

### 2.4 关键的反向读数（效果的另一面）

| 读数 | 含义 | 出处 |
|---|---|---|
| **1.42 → 49.68** | 去掉视觉复核后的平均 CD ⇒ 视觉复核被移除时的假收敛 | CADSmith，报告 §7 |
| **DoF 恒写死 0** | slvsx-cli 的 `diagnostics.dof` 恒为 0 ⇒ 求解器诊断未真正回传 | `slvsx-cli` §3/§5，报告 §6 |
| **「工具没报错就报成功，但几何可能不是你要的」** | Fusion Assistant **官方 FAQ** 自己写下的显式警告 | `fusion-assistant` §5，报告 §5 |
| **`status: success` 只表示比较跑了** | agentcad 把「成功」语义反复拆开：`passed` 才是 spec 检查结果 | `agentcad` §3 引 `guide.py:279-282` |
| **BIM 绝对 IoU 43.6%** | 同一产品自测 CAD 侧 79.7%，BIM 侧 43.6% ⇒ 域间差异 | `sky-001` §5 |
| **187 工具 / 0 测试** | Eduardof0nt 的工具最多，仓库里没有任何测试文件 | `sw-eduardof0nt`，报告 §2.5 |

### 2.5 本仓库在调研里的对照位

调研报告把本仓库作为对照列出：工具数 **529**（报告 v3 口径）· 一动词一工具切法。
另据 `docs/state/facts/B-tools.md` B-01 与 `J-runtime.md` J-03 的实测：声明式 **501** + 装饰器 **45**。
★ **两组数口径不同**（报告写 529 = 497+32；台账实测 501+45=546），本报告只并列，不做取舍。

---

## §3 同一环节的做法总目录（E1–E9）

| 环节 | 有哪些做法（报告原文，每格至少两个真实样本）|
|---|---|
| **E1 需求** | 一次提示直出（多数）· 批量追问 + 出站许可（本仓 `design_ir.py`）· 三层绑定（Amagine3D：不可变 intent / 可变源码 / 场景）· 规格文件标 `origin: user_stated`（anvilate）|
| **E2 表示** | 代码 15 · 网格 13 · 特征树 11 · 序列 8 · 约束 1 · DSL 1 · 无 1 |
| **E3 知识** | 版本化 API 文档检索（CADSmith KB1）· 示例/零件库少样本（mcp-cadquery `part_library`）· 错误模式库（CADSmith KB2）· 标准件/选型表（本仓 `standard_parts.py` 22 张表）· 指南唯一真源 + 内容哈希（agentcad）· 技能以 MCP resource 暴露（build123d-mcp）|
| **E4 生成** | 单发 28 家 · 采样多候选择优（CAD-Recode）· 微调专模 7–13B · 程序化合成数据（CAD-Recode 100 万条）· RL 后训练（cadrille）· 多智能体（1 家）|
| **E5 执行** | 进程内 COM（本仓）· 进程外客户端 + 宿主主线程（fusion360-mcp）· 纯离线内核（本仓 `compiler.py`）· 保证流形输出的内核（manifold）· 沙箱隔离子进程 + 超时（CADSmith 60 s）|
| **E6 验证** | 内核级硬门禁（`BRepCheck_Analyzer`）· 网格级（水密/绕序/欧拉数）· 求解器诊断（DoF/冗余）· 可执行 DFM 规则（vcad / ai-cad / 本仓 `manufacturing_rules.py`）· 视觉复核（CADSmith 三视图）· 独立评审模型 · 导出回读（Amagine3D）|
| **E7 回环** | traceback 回传重写 · 错误模式库辅助 · 几何度量回传 · 一次只改一处 + 重编译比对（ai-cad 回归门）· 有界修复（multi-agent-cad）· 失败按归属路由（multi-agent-cad 四路）|
| **E8 交付** | 只出网格 20 家 · STEP 17 家 · 只出序列 3 家 · 工程图 PDF（text-to-cad）· DFM 评分 · 诚实账本（anvilate `not evaluated` / 本仓 `capabilities.yaml` level+evidence）|
| **E9 人机** | 人只在两端（商业共识）· 变更前审批（adam/fusion/spline）· 人当场点选（Spline 强制在 4 张预览里选）· 无门禁（run-only 7 家）|

（来源：`docs/ai-cad-landscape-report.md` §4）

---

## §4 被反复实现的具体机制（12 条，每条带一手出处）

| # | 机制 | 出处 |
|---|---|---|
| 1 | 导出回读判成败（`pass=true` 仍只到「待视觉评审」）| amagine3d §2 |
| 2 | 惯性轴对齐 + BRep 布尔体积 IoU | cad-coder §3（`SolidAlign/_cq.py:7-52,43-46`）|
| 3 | 判活三级：能跑 → 能导出 → 文件真的在 | cad-coder §3（`scripts/generate_model_cad.py:25-48`）|
| 4 | 几何 → token 位注入（`attention_mask` 的 -1 当哨兵位、前向覆写 embedding，不改模型结构）| cad-recode §3 · cadrille §3 |
| 5 | 指南唯一真源 + 内容哈希指纹 | agentcad §3（`guide.py:1-12`）|
| 6 | 分层 gate + `first_failure` + 未确定项必须显式写出 | agentcad §3（`validation.py:99-108`）|
| 7 | `design_audit`：±10% 参数扰动判「有效形状 ≠ 可编辑设计」| build123d-mcp §3（`server.py:445-448`）|
| 8 | 改前父子关系预检 + 改后下游影响清单 | adam-cad-copilot §5 |
| 9 | 「工具没报错就报成功，但几何可能不是你要的」写成显式警告 | fusion-assistant §5 |
| 10 | 两级执行门：语法快检 → 真跑 | zoo-text-to-cad §3 |
| 11 | 约束外置：只让模型写约束（39 种），坐标交求解器 | slvsx-cli §3/§5 |
| 12 | 参数损失的容差软标签（量化后「差一档」不该与「差百档」同罚）| drawing2cad §3（`tuner/loss.py:41-59`，tolerance=3）|

（来源：`docs/ai-cad-landscape-report.md` §5）

---

## §5 50 家看下来「没有对应实现」的位置（报告原文的 9 条）

| # | 空白 | 报告给出的证据 |
|---|---|---|
| 1 | 可验证的「可制造」定义（公差/DFM/工艺对应，逐条可引条款）| 11 家商业产品无一家给出；开源侧只有 vcad / ai-cad 骨架 + 本仓 `manufacturing_rules.py` + `rule_service.py` |
| 2 | 可执行 DFM 接进回环 | `dfm-rules` 只有 2 家（text-to-cad / leo 宣称），无一家把 DFM 做成回环内硬门禁 |
| 3 | 求解器诊断回传闭环 | slvsx 的 DoF 恒写死 0、冗余被错报成奇异 |
| 4 | 「读懂图纸 → 重建」的通路 | 「读懂」已商业化（Werk24 按次收费），「重建」全限小域（PlankAssembly 只做柜类）|
| 5 | 开源的标准件选型表 + 选型逻辑 | 最接近的 ai-cad `sourcing-tables` 自标 provisional stub |
| 6 | 版本化 API 文档检索做成 MCP 默认件 | 论文里有（CADSmith KB1），没开源成通用件 |
| 7 | 中文工程语言 + 中国国标口径 | 50 家里所有项目均为英文/欧美标准（ASME / ISO 侧）|
| 8 | 「人在环修正」的量化收益 | 无任何论文/产品报告这个数字 |
| 9 | 「有效形状 ≠ 可编辑设计」的通用判据 | 只有 build123d-mcp 用 ±10% 扰动做了单点尝试 |

（来源：`docs/ai-cad-landscape-report.md` §6）

---

## §6 许可分布（四档，均读原文）

| 档 | 项目 |
|---|---|
| **MIT / Apache-2.0** | text-to-cad · Amagine3D · Multi-Agent-CAD · agentcad · build123d-mcp · cadquery-llm-skill · fusion360-mcp · RhinoAI · OpenSCAD-MCP · TRELLIS · TripoSG · TripoSR · InstantMesh · Step1X-3D · FlexCAD · DeepCAD · Img2CAD · Drawing2CAD · vcad · ai-cad · anvilate · Slacker-LLC（Apache，带 NOTICE 义务）|
| **有条件商用** | Hunyuan3D-2（欧盟/英国/韩国不适用 + MAU>100 万须申请 + 禁止反哺）· SF3D/SPAR3D（Stability：年营收 <100 万美元免费，超了许可终止）|
| **只读思想** | cad-recode（CC BY-NC 4.0）· Text2CAD（CC BY-NC-SA）· CAD-Assistant（CC BY-NC）· PlankAssembly（AGPL-3.0）· CADAM（GPL-3.0）· freecad-ai（LGPL-2.1）· slvsx-cli（GPL-3.0）|
| **陷阱** | cadrille 代码 Apache-2.0 但训练数据是 CC BY-NC 的 CAD-Recode ⇒ 代码许可不覆盖权重 · InstantMesh Apache-2.0 但 `src/` 下 19 个文件带 NVIDIA「禁止再分发」头 · CAD-Coder 版权行仍是模板占位 |

（来源：`docs/ai-cad-landscape-report.md` §2.6；逐条原文见各卡 §7）

---

## §7 查不到的（避免重复检索）

| 类别 | 查不到的 |
|---|---|
| 模型/权重 | Zoo 的 text-to-CAD 模型（官方 MCP 测试断言 `text_to_cad` 未注册）· Hunyuan3D-2.5（仓库 404）· Meshy 权重 · Rodin（404）· MeshGPT 官方仓库 · CAD-Llama 官方代码 |
| 论文 | CAD 生成方向的专门蒸馏论文 |
| 图纸 | GD&T + 剖视 + 尺寸链**完整**转 3D 的开源实现 |
| 插画 | 机械插画/爆炸图 → 可编辑几何（最接近者只出知识图谱）|
| 知识 | 开源的标准件选型表 + 选型逻辑 |
| 手段 | 可执行 DFM 接进回环 · 求解器诊断回传闭环 · 渲染回环做服务器默认件 · 「选模板」决策的评估 |
| 商业 | Zoo 现行价目 · Fusion Flex tokens 额度与单价 · Adam Pro/Max 价格 · LEO AI 的导出格式清单 |

（来源：`docs/ai-cad-landscape-report.md` §8）

---

## §8 调研自身的偏差与未完成项（原样记录）

| 偏差 | 原文 |
|---|---|
| TripoSR 是打补丁后跑通 | `torchmcubes` 本机编不过（三层失败链），改用 `skimage.measure.marching_cubes` 兜底 ⇒ 顶点顺序可能与原实现不同，未逐点比对 |
| 其余 7 家生成式模型未跑 | Hunyuan3D-2 / TRELLIS / TripoSG / InstantMesh / SF3D / SPAR3D / Step1X-3D：缺编译型 CUDA 扩展（flash-attn/spconv/kaolin/utils3d/diso/torch-cluster 无 Windows 轮；torchmcubes/nvdiffrast/diffoctreerast 连 PyPI 都没有）⇒ 一律标「读码」|
| 4 家单测跑过 ≠ 建模能力 | fusion360-mcp-server / blender-mcp / cadam / mcp-cadquery：那是「包能装、单测能跑」的证据 |
| 12 家商业产品无源码 | 证据等级只能是「元数据」；其中 3 个页面是 JS 应用，引文取自检索索引正文，逐字引用前建议浏览器复核（各卡 §9 已标注）|
| LEO AI 导出格式未公布 | `deliver=STEP` 只表示「工程格式桶」，卡 §1/§9 已写明未证实 |

（来源：`docs/survey/state.json` `deviations`；`docs/ai-cad-landscape-report.md` §7 注）

---

## §9 汇总层面的观察（陈述分布，不含评价）

1. **证据结构**：50 张卡里 34 张靠读码、12 张靠元数据、4 张有实测；4 张实测里只有 1 张是「模型出几何」。
2. **验证强度结构**：`visual + run-only + none` 合计 **31 家**；`dfm-rules + solver + export-readback + geometry-gate` 合计 **6 家**。
3. **编排与主体性质相关**：`human-approve` 3 家全部是商业产品；`loop` 13 家几乎全是开源工具。
4. **表示与能否进 CAD 相关**：`mesh` 13 家全部不能直接出 STEP/IGES（除 Creo 走重建）；`code` 15 家多数能出 STEP。
5. **工具数与质量不相关**：样本里 187 工具那家零测试；92 工具那家是四家 SW 竞品里工程纪律最被报告肯定的。
6. **效果数字的可得性**：能查到具体数值的，多数来自论文或厂商自述；本机可复现的只有 1 个模型（TripoSR）与 4 套单测。

---

## §10 出处索引

| 材料 | 路径 |
|---|---|
| 50 张逐项目卡 | `docs/survey/cards/*.md`（约 756 KB）|
| 架构分类矩阵（机算）| `docs/survey/architecture-matrix.md` |
| 步骤做法矩阵（机算）| `docs/survey/step-matrix.md` |
| 全景报告 v3 | `docs/ai-cad-landscape-report.md` |
| 调研计划与判据 | `docs/ai-3d-survey-plan.md` |
| 调研进度与偏差 | `docs/survey/state.json` |
| 竞品与官方签名交叉核对 | `docs/recon/competitor-signature-crosscheck.md` · `docs/recon-206/competitor-crosscheck-archival.md` |
| 本仓库实测台账（对照用）| `docs/state/INDEX.md` → `facts/B-tools.md` · `C-capabilities.md` · `Q3-tests-full.md` |
| 矩阵生成器 | `scripts/gen_survey_matrix.py` |
