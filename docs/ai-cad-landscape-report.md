# AI 自动建模 · 全网技术路径总图（v3）

**依据**：业主 2026-10-23 指令 ——「做 Agent 自动建模这个事情的全网调研、全网技术路线的总图：不同家有不同的做法，每个项目的技术路径是什么样子；一般来说有哪几类架构；具体每一类架构里面的每个步骤都有哪些做法。这是一个极其详细的报告，相当于我看了你的报告，就已经清楚地知道市面上任何一个 AI 自动建模的工具是怎么设计的了。」

**版本**：v3（2026-10-24）· 上一版 v2 只有 13 家的一手证据，**v3 建立在 50 张逐项目卡片上**
**数据来源**：`docs/survey/cards/` 下 50 张卡片；所有分布数字由 `scripts/gen_survey_matrix.py` 从卡片的机读 tag 重算
（`docs/survey/architecture-matrix.md` · `docs/survey/step-matrix.md`），**本文件不手写计数**。
**逐项目细节**：每张卡片有 12 字段 + 九节（技术路径/机制/运行条件/坑/许可/证据清单/未确认）。

---

## 0. 怎么读：三个坐标 + 十问自检

**任何 AI 建模工具 = ①表示 + ②编排 + ③验证 的三元组**，再加两个横向属性（交付格式、许可）。

**十问自检**（拿到任何一个工具，照问就知道它属于哪类）：

1. 产物是**可执行代码/特征树**，还是**三角网格**？（最快判据：导出清单里有没有 STEP/IGES）
2. 中间表示是开放词表（Python）还是封闭词表（自定义 token / DSL / 序列）？
3. 生成器是**通用 LLM**、**微调专模**、**云服务**，还是**没有 AI**（模板+规则）？
4. 有「执行 → 读错 → 重写」的回环吗？最多几轮？（`loop` 还是 `single`）
5. 失败时模型能看到什么？traceback / 几何度量 / 渲染图 / 求解器诊断 / 什么都没有？
6. 有**硬门禁**吗（不合法直接判失败，不听模型解释）？
7. 验证用**形状相似度**（CD/IoU）、**数值断言**、**导出回读**、**DFM 规则**、**求解器诊断**，还是**人眼看**？
8. 人插在哪？（给意图 / 选模板 / 批准变更 / 目视核验 / 完全不插）
9. 它要求多大的模型？1.5–2B 代码模型 / 7–13B 专模 / 闭源大模型 / 无要求？
10. 工具面有多少个？是「一动词一工具」还是「少工具 + 万能代码口」？

---

## 1. 十类架构（A–J）与 50 家的真实分布

| 类 | 架构 | 一句话 | 50 家里的代表 |
|---|---|---|---|
| **A** | 代码单发 | LLM 写脚本 → 执行一次 | cadam（七视角循环其实算 B，见卡）· 多数开源初版 |
| **B** | **代码回环** | 写 → 执行 → 读错 → 重写 | agentcad · amagine3d · earthtojake-text-to-cad · cad-assistant · build123d-mcp · zoo-text-to-cad |
| **C** | 多智能体 | 拆解/编码/渲染/纠错分工 | multi-agent-cad（**全库仅 1 家**）|
| **D** | 序列/DSL 专模 | 模型吐 CAD 命令序列或受限 DSL | deepcad · text2cad · flexcad · img2cad · drawing2cad · plankassembly |
| **E** | 生成式网格 | 扩散/流匹配直接出 mesh | hunyuan3d-2 · trellis · triposg · triposr · instantmesh · sf3d · spar3d · step1x-3d · meshy · rodin · tripo · spline |
| **F** | 逆向 | 图/点云/图纸 → 参数化代码 | cad-recode · cadrille · cad-coder · img2cad · drawing2cad |
| **G** | 模板+参数+规则 | 不生成几何，只选模板/填参/跑求解 | ptc-creo-generative · openscad-mcp-server（模板部分）|
| **H** | GUI/API 代理 | 改既有模型 | fusion-assistant · adam · fusion360-mcp · freecad-mcp · blender-mcp · autocad-mcp · rhinoai · freecad-ai · build123d-mcp · leo-ai · sky-001 |
| **I** | 知识/检索助手 | 不出几何 | onshape-ai-advisor · siemens-nx-ai · cadquery-llm-skill |
| **J** | **世界模型/几何状态** | 预测几何状态序列，不经文本 | sky-001（**全库仅 1 家**）|

★ **J 类是 2026-10 才出现的新类别**（SKY-001，Skyfall AI，2026-10-19 发布，闭源）：
它不生成文本也不生成网格，而是**直接预测「下一个几何状态」**（先出候选 → 层级拆解 → 逐步预测 2D 草图与 3D 状态 → 分层装配）。
自测 CAD IoU 79.7% / 3.9 秒，但**官方承认生成的还不是可编辑参数化 CAD 历史**，且演示中 2D 草图会与 3D 状态不一致
（来源：`docs/survey/cards/sky-001.md`）。

---

## 2. 六个维度上的真实分布（50 家）

### 2.1 中间表示（决定「普通模型能不能用」）

| 表示 | 家数 | 谁 | 能否进 CAD |
|---|---|---|---|
| `code` | **15** | agentcad · amagine3d · blender-mcp · build123d-mcp · cad-assistant · cad-coder · cad-recode · cadrille · cadam · cadquery-llm-skill · earthtojake-text-to-cad · mcp-cadquery · multi-agent-cad · zoo · freecad-ai | ✅ 多数能 |
| `mesh` | **13** | hunyuan3d-2 · instantmesh · meshy · ptc-creo · rodin · spar3d · spline · sf3d · step1x-3d · trellis · tripo · triposg · triposr | ❌ 不能（除 Creo 走重建）|
| `feature-tree` | **11** | adam · freecad-ai · freecad-mcp · fusion-assistant · fusion360-mcp · leo-ai · sw-* 四家 · rhinoai | ✅ 能（改既有模型）|
| `sequence` | **8** | autocad-mcp · deepcad · drawing2cad · flexcad · img2cad · plankassembly · sky-001 · text2cad | ⚠️ 需导入器 |
| `constraint` | 1 | slvsx-cli | ✅（求解器出解）|
| `dsl` | 1 | openscad-mcp-server | ⚠️ 出网格 |
| `none` | 1 | onshape-ai-advisor | — |

（来源：`docs/survey/step-matrix.md`）

★ **关键**：`code` 与 `mesh` 几乎对半（15 vs 13），但**性质完全不同** —— 前者多数能出 STEP，后者一律不能。
⇒ 判「是不是工程路线」不看用不用 AI，**看导出清单**。

### 2.2 编排（决定「错了能不能修」）

| 编排 | 家数 | 谁的特征 |
|---|---|---|
| `single` | **28** | 学术模型全部单发 + 网格云服务全部单发 + 只读桥 |
| `loop` | **13** | 几乎全是**开源工具**：agentcad · amagine3d · blender-mcp · build123d-mcp · cad-assistant · cadam · earthtojake-text-to-cad · mcp-cadquery · multi-agent-cad · zoo · freecad-ai · clvsx · rhinoai |
| `none` | 4 | 只答问或只给能力的：autocad-mcp · cadquery-llm-skill · onshape · siemens-nx |
| `human-approve` | **3** | **全部是商业产品**：adam · fusion-assistant · spline-ai |
| `multi-agent` | 1 | multi-agent-cad |
| `template` | 1 | ptc-creo |

（来源：`docs/survey/step-matrix.md`）

★ **这条分布说明的是责任归属**，不是技术先进度：开源工具把重试交给程序，商业产品把批准权交回人。

### 2.3 验证（决定「能不能用」）

| 验证手段 | 家数 | 强度 |
|---|---|---|
| `visual` | **20** | ★ 最弱：13 家网格只能看图 + 5 家产品靠人眼 + 少数代码路线 |
| `numeric` | **13** | 中：学术的 CD/IoU（注意多为**择优值**）+ fusion360 的质量/包围盒/体数回带 |
| `run-only` | 7 | 最弱一档：**能跑就算过**（含 4 家 SW 竞品里的 3 家）|
| `none` | 4 | 无验证 |
| `dfm-rules` | **2** | 最强：earthtojake-text-to-cad（每条结论带测量证据 + 引用规则）· leo-ai（宣称）|
| `solver` | 2 | 强：ptc-creo（求解器收敛）· slvsx-cli（SolveSpace 返回码）|
| `export-readback` | 1 | 强：amagine3d（只认重新读回的文件）|
| `geometry-gate` | 1 | 强：plankassembly（线稿→形状程序的几何校验）|

（来源：`docs/survey/step-matrix.md`）

★ **最强的一档（dfm-rules / solver / export-readback / geometry-gate）合计只有 6 家**，
而 `visual + run-only + none` 合计 **31 家** —— 这就是「看起来能用」与「能用」的分界。

### 2.4 交付

`mesh` **20** · `STEP` **17** · `none` **9** · `sequence` 3 · `drawing` 1（来源：`docs/survey/step-matrix.md`）

★ `none` 的 9 家里有 4 家是「只改既有模型、不产出新文件」的桥 —— 它们的价值在**操作**不在**文件**。

### 2.5 工具粒度：九个真实样本，跨度 66 倍

| 项目 | 工具数 | 切法 |
|---|---|---|
| autocad-mcp | **8** 个工具分派 **72** 个操作 | 合并式极端：契约只写 docstring，Python 只转发 |
| openscad-mcp-server | **8**（3 写 5 读） | 生命周期切分 + 11 个基本体模板 |
| blender-mcp | **9** 模型可见（+5 App-only）| 反向收敛：逐操作交给模型写 bpy 代码 |
| freecad-mcp | **17** | 原语式 + 万能代码口 |
| slvsx-cli | **39** 种约束 + 8 类实体 | 只暴露约束词汇，不暴露坐标 |
| rhinoai | **42**（18 通用 + 12 GH1 + 12 GH2）| 只做读状态/选择/相机，建模交代码 |
| freecad-ai | **61**（6 类） | 受限操作集 + 唯一逃逸口（提示词标 last resort）|
| fusion360-mcp-server | **93** | 每条改模型命令回带质量/包围盒/体数增量 |
| Slacker-LLC（SW 竞品）| **92** | 一动词一工具 + 工程纪律（mm/deg 契约、串行化、`GetWhatsWrong`）|
| Eduardof0nt（SW 竞品）| **187** | 一动词一工具 + **零测试** |
| 本仓库（对照）| **529** | 一动词一工具 |

（来源：`docs/survey/cards/` 各卡 §3）

★ **成立的方式只有两种**：工具少 + 一个万能代码口；或工具多 + 每个都带结构化回读。
**没有一家靠「工具多 + 只回 success」成立** —— 187 工具 0 测试那家就是反例。

### 2.6 许可：四档，红线必须逐条读原文

| 档 | 项目 |
|---|---|
| MIT / Apache-2.0（可借鉴） | text-to-cad · Amagine3D · Multi-Agent-CAD · agentcad · build123d-mcp · cadquery-llm-skill · fusion360-mcp · RhinoAI · OpenSCAD-MCP · TRELLIS · TripoSG · TripoSR · InstantMesh · Step1X-3D · FlexCAD · DeepCAD · Img2CAD · Drawing2CAD · vcad · ai-cad · anvilate · Slacker-LLC（Apache，带 NOTICE 义务）|
| 有条件商用 | Hunyuan3D-2（欧盟/英国/韩国不适用 + MAU>100 万须申请 + 禁止反哺）· SF3D/SPAR3D（Stability：年营收 <100 万美元免费，超了许可终止）|
| **只读思想** | cad-recode（CC BY-NC 4.0）· Text2CAD（CC BY-NC-SA）· CAD-Assistant（CC BY-NC）· PlankAssembly（AGPL-3.0）· CADAM（GPL-3.0）· freecad-ai（LGPL-2.1）· slvsx-cli（GPL-3.0）|
| 陷阱 | **cadrille** 代码 Apache-2.0，但训练数据是 CC BY-NC 的 CAD-Recode ⇒ **代码许可不覆盖权重**；**InstantMesh** Apache-2.0 但 `src/` 下 19 个文件带 NVIDIA「禁止再分发」头；**CAD-Coder** 版权行仍是模板占位 |

（来源：`docs/survey/cards/` 各卡 §7）

---

## 3. 逐项目技术路径（50 家，按类分组）

> 完整细节见各卡片；本表只给「一句话 + 表示/编排/验证/交付」四格。

### 3.1 代码即 CAD 系（B 类为主）

| 项目 | 路径要点 | 表示 | 编排 | 验证 | 交付 |
|---|---|---|---|---|---|
| earthtojake/text-to-cad | 12 个技能分阶段 + `step.parts` 查标准件 + `dfm` 出证据 | code | loop | dfm-rules | STEP |
| Amagine3D | 三层绑定（不可变 intent / 可变源码 / 场景）+ 修复差分分类 6 态 | code | loop | export-readback | STEP |
| Multi-Agent-CAD | 只传紧凑结构化状态；双引擎 QA + 独立 Judge + 有界修复 | code | multi-agent | visual | STEP |
| agentcad | 指南唯一真源 + 内容哈希指纹；分层 gate + `first_failure` | code | loop | numeric | STEP |
| build123d-mcp | 一次一特征、每步量测/渲染/校验；`design_audit` 用 ±10% 扰动判「可编辑」| code | loop | run-only | STEP |
| cadquery-llm-skill | 纯提示词资产（无执行器）；明文写模型能力门槛 | code | none | none | none |
| CADAM | 浏览器内 OpenSCAD→WASM；七视角拼图回灌自评 | code | loop | visual | mesh |
| zoo-text-to-cad | KCL 真程序 + 云引擎；Zookeeper 是 plan→act→observe 代理 | code | loop | visual | STEP |
| cad-assistant | 训练-free：写 FreeCAD Python + 自建感知工具序列化回喂 | code | loop | visual | STEP |
| mcp-cadquery | 整段源码在「每 workspace 一 venv」子进程跑，凭 result_id 导出 | code | loop | run-only | STEP |

### 3.2 学术序列/逆向系（D/F 类）

| 项目 | 路径要点 | 表示 | 基座 |
|---|---|---|---|
| CAD-Recode | 点云 → CadQuery；采样多候选按 CD 选优 | code | **Qwen2-1.5B** |
| cadrille | 三模态（点云/图/文）→ CadQuery | code | Qwen2-VL-2B |
| CAD-Coder | 图 → CadQuery → STEP；**惯性轴对齐 + BRep 体积 IoU** | code | vicuna-13b |
| FlexCAD | 扁平文本命令串 + 层级掩码 | sequence | LLaMA-3-8B/70B |
| Text2CAD | 自然语言 → 量化 sketch-extrusion 序列 | sequence | BERT-large + 8 层 |
| DeepCAD | 定长 (60,17) 量化矩阵 + Transformer AE + latent GAN | sequence | — |
| Img2CAD | 结构/参数**分开预测**（Llama 出结构、扩散回归参数）| sequence | Llama-3.2-11B |
| PlankAssembly | 三视图线稿 → 板件形状程序（**只做柜类**）| sequence | — |
| Drawing2CAD | 矢量四视图 → 命令序列（非自回归，无预训练权重）| sequence | — |

### 3.3 生成式网格（E 类）

Hunyuan3D-2（flow-matching DiT + 独立纹理分支）· TRELLIS（SLAT 统一潜码，一份解码成网格/高斯/辐射场）· TripoSG（1.5B rectified flow + SDF-VAE）· TripoSR（LRM 前馈 + CPU 兜底）· InstantMesh（Zero123++ 六视图 → 三平面 → FlexiCubes）· SF3D（三平面 + marching-tet + 烘焙 PBR）· SPAR3D（SF3D + 点云扩散，中间表示变可编辑点云）· Step1X-3D（TSDF-VAE + 3D DiT，**水密**）

### 3.4 桥接层（H 类）

| 项目 | 通道 | 工具数 |
|---|---|---|
| fusion360-mcp-server | 客户端 → stdio → **TCP:9876 → 插件守护线程 → CustomEvent → Fusion 主线程** | 93 |
| freecad-mcp | XML-RPC `localhost:9875` + Qt 主线程调度队列 | 17 |
| blender-mcp | 裸 TCP+JSON `localhost:9876`，addon 用**唯一一个** bpy timer 排空队列 | 9（+5 App-only）|
| autocad-mcp | `C:/temp/*.json` + `PostMessageW(WM_CHAR)` 击键触发 AutoLISP | 8→72 操作 |
| RhinoAI | MCP 端点 + 多实例路由；建模靠 `run_python`/`run_csharp` | 42 |
| freecad-ai | 受限操作集 61 个 + 唯一逃逸口 `execute_code` | 61 |
| slvsx-cli | **只写约束**、SolveSpace 解坐标 | 39 约束 |

### 3.5 商业产品（11 家）

Zoo（KCL 程序 + 云引擎）· Fusion Assistant（批准后执行，**官方承认「报成功但几何可能不对」**）· Onshape AI Advisor（不碰几何）· Siemens NX（只做选择/PMI/导航）· PTC Creo GD（求解器吐材料分布，**不出特征树**）· Adam（无自有内核，**改前父子关系预检**）· Meshy/Rodin/Tripo/Spline（纯网格）· Leo AI（**宣称**参数化装配，格式清单未公布）

---

## 4. 同一环节的做法总目录（E1–E9）

| 环节 | 有哪些做法（每格至少两个真实样本）|
|---|---|
| **E1 需求** | 一次提示直出（多数）· 批量追问 + 出站许可（我方 `design_ir.py`）· 三层绑定（Amagine3D：不可变 intent / 可变源码 / 场景）· 规格文件标 `origin: user_stated`（anvilate）|
| **E2 表示** | 代码 15 · 网格 13 · 特征树 11 · 序列 8 · 约束 1 · DSL 1 · 无 1 |
| **E3 知识** | 版本化 API 文档检索（CADSmith KB1）· 示例/零件库少样本（mcp-cadquery 的 `part_library`）· 错误模式库（CADSmith KB2）· 标准件/选型表（我方 `standard_parts.py` 22 张表）· 指南唯一真源 + 内容哈希（agentcad）· 技能以 MCP resource 暴露（build123d-mcp）|
| **E4 生成** | 单发 28 家 · 采样多候选择优（CAD-Recode）· 微调专模 7–13B · 程序化合成数据（CAD-Recode 100 万条）· RL 后训练（cadrille）· 多智能体（1 家）|
| **E5 执行** | 进程内 COM（我方）· 进程外客户端 + 宿主主线程（fusion360-mcp，**与我方 COM/STA 同构**）· 纯离线内核（我方 `compiler.py`）· 保证流形输出的内核（manifold）· 沙箱隔离子进程 + 超时（CADSmith 60 s）|
| **E6 验证** | 内核级硬门禁（`BRepCheck_Analyzer`）· 网格级（水密/绕序/欧拉数，**实战会漏**）· 求解器诊断（DoF/冗余）· **可执行 DFM 规则**（vcad / ai-cad / 我方 `manufacturing_rules.py`）· 视觉复核（CADSmith 三视图，去掉后 CD 1.42→49.68）· 独立评审模型 · 导出回读（Amagine3D）|
| **E7 回环** | traceback 回传重写 · 错误模式库辅助 · 几何度量回传 · 一次只改一处 + 重编译比对（ai-cad 回归门）· 有界修复（multi-agent-cad）· 失败按归属路由（multi-agent-cad 四路）|
| **E8 交付** | 只出网格 20 家 · STEP 17 家 · 只出序列 3 家 · 工程图 PDF（text-to-cad）· DFM 评分 · **诚实账本**（anvilate 的 `not evaluated` / 我方 `capabilities.yaml` 的 level+evidence）|
| **E9 人机** | 人只在两端（商业共识）· 变更前审批（adam/fusion/spline）· 人当场点选（Spline 强制在 4 张预览里选）· 无门禁（run-only 7 家）|

---

## 5. 十二条最值得借鉴的机制（都有一手出处）

| # | 机制 | 出处 |
|---|---|---|
| 1 | **导出回读判成败**（`pass=true` 仍只到「待视觉评审」）| amagine3d §2 |
| 2 | **惯性轴对齐 + BRep 布尔体积 IoU**（比网格 IoU 严格一级，补「实体 vs 规范件」比对口径）| cad-coder §3（`SolidAlign/_cq.py:7-52,43-46`）|
| 3 | **判活三级**：能跑 → 能导出 → 文件真的在 | cad-coder §3（`scripts/generate_model_cad.py:25-48`）|
| 4 | **几何 → token 位注入**（用 `attention_mask` 的 -1 当哨兵位、前向覆写 embedding，不改模型结构）| cad-recode §3 · cadrille §3 |
| 5 | **指南唯一真源 + 内容哈希指纹**（「装了旧规范」变成机器可检出的事实）| agentcad §3（`guide.py:1-12`）|
| 6 | **分层 gate + `first_failure` + 未确定项必须显式写出** | agentcad §3（`validation.py:99-108`）|
| 7 | **`design_audit`：±10% 参数扰动判「有效形状 ≠ 可编辑设计」** | build123d-mcp §3（`server.py:445-448`）|
| 8 | **改前父子关系预检**（宁可拒绝也不硬重建）+ 改后下游影响清单 | adam-cad-copilot §5 |
| 9 | **「工具没报错就报成功，但几何可能不是你要的」写成显式警告** | fusion-assistant §5（官方 FAQ）|
| 10 | **两级执行门**：语法快检（`mock_execute_project`）→ 真跑（`execute_project`）| zoo-text-to-cad §3 |
| 11 | **约束外置**：只让模型写约束（39 种），坐标交求解器；**DoF 必须真回传**（slvsx 的 `diagnostics.dof` 恒写死 0 是反例）| slvsx-cli §3 · §5 |
| 12 | **参数损失的容差软标签**（量化后「差一档」不该与「差百档」同罚）| drawing2cad §3（`tuner/loss.py:41-59`，tolerance=3）|

---

## 6. 全行业空白（50 家看下来仍然空着的位置）

| # | 空白 | 证据 |
|---|---|---|
| 1 | **可验证的「可制造」定义**（公差/DFM/工艺对应，逐条可引条款）| 11 家商业产品**无一家**给出；开源侧只有 vcad / ai-cad 骨架 + 我方 `manufacturing_rules.py` + `rule_service.py` |
| 2 | **可执行 DFM 接进回环** | 50 家里 `dfm-rules` 只有 2 家（text-to-cad / leo 宣称），且没有一家把 DFM 做成**回环内的硬门禁** |
| 3 | **求解器诊断回传闭环** | 有「给 AI 用的求解器」（slvsx），但 DoF **恒写死 0**、冗余被错报成奇异 ⇒ 诊断没回传 |
| 4 | **「读懂图纸 → 重建」的通路** | 「读懂」已商业化（Werk24 按次收费），「重建」全限小域（PlankAssembly 只做柜类）|
| 5 | **开源的标准件选型表 + 选型逻辑** | 最接近的 ai-cad `sourcing-tables` 自标 provisional stub |
| 6 | **版本化 API 文档检索做成 MCP 默认件** | 论文里有（CADSmith KB1），没开源成通用件 |
| 7 | **中文工程语言 + 中国国标口径** | 50 家里所有项目均为英文/欧美标准（ASME / ISO 侧）|
| 8 | **「人在环修正」的量化收益** | 无任何论文/产品报告这个数字 |
| 9 | **「有效形状 ≠ 可编辑设计」的通用判据** | 只有 build123d-mcp 用 ±10% 扰动做了单点尝试 |

---

## 7. 数字索引（可复核）

| 数字 | 含义 | 来源 |
|---|---|---|
| 21–92% → 3–4% | 通用 LLM 单发失败率 → 迭代 agent 失败率 | CodeGen-3D（IEEE Access 2026）|
| 0.8085 → 0.9629 | IoU 中位（加硬门禁前后）| CADSmith |
| 1.42 → 49.68 | 去掉视觉复核后的平均 CD（假收敛证据）| CADSmith |
| 5.86 vs 1.21 | 每脚本可用复杂操作数（有/无文档 RAG）| LL3M |
| 0.791 / 0.614 | SGPBench 2D 得分（GPT-4o / GPT-4 mini）| CAD-Assistant |
| 15.7% | CAD-Llama 多任务平均超出 GPT-4 的**相对**幅度 | CAD-Llama |
| 100 万条 | CAD-Recode 程序化合成训练数据量 | CAD-Recode |
| 93.4% | FlexCAD 可渲染有效率 | FlexCAD |
| 79.7% / 3.9 秒 | SKY-001 自测 CAD IoU 与时延（**厂商自测，无第三方复现**）| `docs/survey/cards/sky-001.md` |
| 187 / 133 / 96 / 93 / 92 | SolidWorks 系竞品工具数（实测）| `docs/survey/cards/sw-*.md` · `fusion360-mcp-server.md` |

---

## 8. 查不到清单（避免重复检索）

| 类别 | 查不到的 |
|---|---|
| 模型/权重 | Zoo 的 text-to-CAD 模型（官方 MCP 测试断言 `text_to_cad` 未注册）· Hunyuan3D-2.5（仓库 404）· Meshy 权重 · Rodin（404）· MeshGPT 官方仓库 · CAD-Llama 官方代码 |
| 论文 | CAD 生成方向的**专门蒸馏**论文 |
| 图纸 | GD&T + 剖视 + 尺寸链**完整**转 3D 的开源实现 |
| 插画 | 机械插画/爆炸图 → 可编辑几何（最接近者只出知识图谱）|
| 知识 | 开源的标准件选型表 + 选型逻辑 |
| 手段 | 可执行 DFM 接进回环 · 求解器诊断回传闭环 · 渲染回环做服务器默认件 · 「选模板」决策的评估 |
| 商业 | Zoo 现行价目 · Fusion Flex tokens 额度与单价 · Adam Pro/Max 价格 · LEO AI 的导出格式清单 |

---

## 9. v2 → v3 改了什么（逐条写理由，不留暗改）

| 改动 | 理由 |
|---|---|
| 架构从 9 类扩到 **10 类（新增 J 世界模型）** | SKY-001 既不是 LLM 也不是网格生成，而是预测几何状态序列（`docs/survey/cards/sky-001.md`）|
| `deliver` 枚举新增 **`sequence`** | 学术序列模型的交付物就是序列本身，记 `none` 失真、记 `STEP` 撒谎（`docs/ai-3d-survey-plan.md` §9）|
| `repr` 枚举新增 **`none`** | Onshape AI Advisor 完全不碰几何，没有中间表示可言 |
| 新增**规则 1**：`class` 按机制判、不按输入形态判 | PlankAssembly/Drawing2CAD 按输入会与 Img2CAD 一起塌进 F 类，把三种机制压成一个标签 |
| 新增**规则 2**：闭源产品 `deliver=STEP` 表示「工程格式桶」 | LEO AI 官网未公布导出清单，记 `STEP` 会过度断言、记 `none` 会失真 |
| 全部计数从「手写估算」改为**脚本从卡片 tag 重算** | 13 家时的计数是人工数的；50 家必须机算，否则会漂 |
| 网格类从「重要分支」降级为「外观路线」 | 13 家网格**没有一家**能出 STEP/IGES（`docs/survey/step-matrix.md`）|
