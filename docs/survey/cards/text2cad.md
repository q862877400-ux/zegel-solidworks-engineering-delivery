# Text2CAD

<!-- survey: class=D; repr=sequence; orchestration=single; verify=numeric; deliver=sequence; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/SadilKhan/Text2CAD · 论文 https://arxiv.org/abs/2409.17106 · 数据集 https://huggingface.co/datasets/SadilKhan/Text2CAD（README 徽章链接，`README.md:18-20`） |
| 许可 | **CC BY-NC-SA 4.0（非商用 + 相同方式共享）** —— 读仓库内 `LICENSE` 原文：`LICENSE:1` 标题 `### Text2CAD Community License Agreement`、`LICENSE:7`「This project named, **Text2CAD**, was developed by [Deutsche Forschungszentrum für Kuntlische Inlligenz (DFKI GmbH)] … It is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.」⇒ **只读思想，不可商用**（`gh api` 报 `license.spdx_id = NOASSERTION`，即以文件原文为准，不是标准 SPDX 标识） |
| 元数据 | stars **489** · forks 80 · open issues 1 · 语言 Python · 最近推送 **2025-05-15T15:53:24Z** · 创建 2024-09-17（来源：`gh api repos/SadilKhan/Text2CAD`，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\SadilKhan__Text2CAD |
| 证据等级 | **读码**（读 LICENSE / README / `Cad_VLM/config/*.yaml` / `Cad_VLM/models/*.py` / `Cad_VLM/test.py` / `CadSeqProc/utility/macro.py` / `CadSeqProc/cad_sequence.py` / `CadSeqProc/json2vec.py` / `Evaluation/eval_seq.py` / `environment.yml` + `gh api`；**未**建环境、未下载权重、未跑推理） |

## 1. 一句话定位

它把「自然语言 → 参数化 CAD 建模序列」做成一个**小型条件语言模型**：BERT-large 读文本、8 层 Transformer 解码器逐 token 吐出 DeepCAD 风格的**量化 sketch–extrusion 序列**，并按 4 个提示详细度（beginner→expert）分别评测（`README.md:3`、`Cad_VLM/config/trainer.yaml:12`、`Cad_VLM/config/trainer.yaml:36`、`Evaluation/eval_seq.py:36`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**① 输入**：一条自然语言提示（`README.md:141` 的例子是 "A rectangular prism with a hole in the middle."）；同一模型吃 4 个详细度级别（评测循环 `for level in range(1,5)`，`Evaluation/eval_seq.py:36`）。

**② 中间表示＝量化的 sketch–extrusion 序列向量**（不是文本、不是 AST）：
- 每步一个 **2 列整数张量**（起始 `[START, 0]`，`CadSeqProc/cad_sequence.py:244`、`:264`）；
- 词表按 `one_hot_size = END_PAD(7) + BOOLEAN_PAD(4) + 2^8(256)` 设计，`N_BIT=8`（`CadSeqProc/utility/macro.py:6`、`:11`、`:12`、`:41`）；
- 另有两路**结构元数据**：`flag_vec`（0＝sketch token，1…11＝extrusion 的第几项，`macro.py:36`、`cad_sequence.py:256-257`）与 `index_vec`（该 token 属于第几个 sketch–extrusion 对，`cad_sequence.py:258`）；
- 长度上限：整序列 **272** 步（`macro.py:14`）、sketch 段 150（`macro.py:34`）、最多 10 段 extrusion（`macro.py:35`）、单段 10 项（`macro.py:36`）；
- 参数归一化系数 `NORM_FACTOR=0.75`（`macro.py:26`）。

**③ 生成**：文本编码器＝**BERT-large**（`model_name: bert_large_uncased`，`Cad_VLM/config/trainer.yaml:12`；`in_dim: 1024`，`:21`），**整个基座冻结**（`Cad_VLM/train.py:85-87`）；上面挂一层 8 头自适应层（`trainer.yaml:24-25`）；解码器 8 层 × 8 头、隐维 1024、状态维 256（`trainer.yaml:32-38`）。**总参数量仓库未写 ⇒ 查不到**（有 `total_parameters()` 方法但无记录值，`Cad_VLM/models/text2cad.py:114-121`）。

**④ 编排＝单模型单轮自回归**：无 agent、无工具调用、无回环；默认 `sampling_type: "max"` 时 `TOPK = 1`，只有非 max 采样时才 `TOPK = 5`（即 5 个候选再挑）（`Cad_VLM/test.py:184-187`、`:195-201`）。

**⑤ 执行**：解码向量 → `CADSequence.from_vec(...).create_cad_model()` 用 pythonocc 建 B-rep（`Cad_VLM/test.py:230-238`）→ 采 8192 点点云（`test.py:237`）。序列本身也能落 STEP/STL/PLY（`CadSeqProc/README.md:37-43` 的 `save_stp(type="step"|"stl")` 与 `save_points`）。

**⑥ 验证**：
- **有效性**：建模型失败即 `is_invalid = 1`、Chamfer 记 `-1`，评测阶段再过滤——**不把失败当成功**（`Cad_VLM/test.py:240-241`、`:268-269`）；
- **序列级指标**：按命令类型算 recall / precision / F1（line、arc、circle…），并按 4 个级别分别汇总（`Evaluation/eval_seq.py:69-80`、`:36-41`）。

**⑦ 交付**：`output.pkl`（`Cad_VLM/test.py:283-286`）＋可选 STEP/STL/PLY（`CadSeqProc/README.md:37-43`）＋ Gradio demo（`README.md:169`、`App/app.py`）。**主产物仍是序列**，STEP 是下游可选步骤。

**★ 学术项补全**：中间表示＝三元量化序列（token/flag/index，见 ②）；基座＝BERT-large（1024 维）+ 8 层 transformer 解码器（`trainer.yaml:12`、`:36`）；训练数据＝**DeepCAD 的 json 转向量**（`README.md:49`、`:57`）＋**Mistral / LLaVA-NeXT 生成的文本标注**（arXiv 摘要）⇒ 具体条数 **查不到**（README 未写；上游 DeepCAD 数据集是 178,238 个模型，来源：https://arxiv.org/abs/2105.09492 摘要，但 Text2CAD 实际用了多少条**没有记录**）；评测指标＝命令级 P/R/F1 + Chamfer 距离 + invalid 比例（`eval_seq.py:69-80`、`test.py:260-269`）。

## 3. 技术方案要点（可迁移的机制）

| 机制 | 说明（只讲机制，不抄代码） | 证据 |
|---|---|---|
| **冻结大文本编码器 + 只训小解码器** | BERT-large 全冻结，只训自适应层与解码器 ⇒ 显存与训练成本被压到「一个小模型」的量级 | `Cad_VLM/train.py:85-87`、`Cad_VLM/models/text2cad.py:123-127` |
| **序列三元组：token / flag / index** | 除了「这一步是什么」还显式给出「属于 sketch 还是 extrusion 的第几项」和「属于第几个特征对」——把结构归属变成可监督信号，不让模型自己猜 | `macro.py:40-44`、`cad_sequence.py:244-273` |
| **解码期同步重建结构列** | 每生成一个 token 就同步算 `flag_vec` / `index_vec`，并对 dummy token 做掩码；源码注释直言「flag/index 错了会得到 invalid model」 | `Cad_VLM/models/decoder.py:236-258`、`:260-280` |
| **无效即显式标记并剔除** | 解析/建体异常统一记 `is_invalid=1` 与 `cd=-1`，评测阶段过滤 ⇒ 失败率是可见字段，不是被平均值吸收 | `Cad_VLM/test.py:240-241`、`:268-269` |
| **多候选再择优（仅采样模式）** | `sampling_type != "max"` 时一次出 5 个结果，用与 GT 的 Chamfer 距离挑最好的那个（默认 max 模式只有 1 个候选，不走这条路）；注意这属于**用真值挑样本**，不是可部署策略 | `Cad_VLM/test.py:184-187`、`:195-201`、`:259-273` |
| **提示分级（4 级）** | 同一批模型配 4 档文字详细度，评测按级别拆分，能看出「描述越细是否建得越准」 | `Evaluation/eval_seq.py:36-41` |
| **采样策略可切** | `nucleus_prob=0` + `sampling_type: "max"` 即贪心/top-1（`TOPK=1`），改采样时 `TOPK=5` 走 nucleus；配置层面就区分「稳定复现」与「多样性」 | `Cad_VLM/config/inference.yaml:61-62`、`Cad_VLM/test.py:184-187`、`Cad_VLM/models/decoder.py:212-228` |

## 4. 运行条件与依赖

- **平台**：README 明写 **Linux**（`README.md:32`）、**Python >=3.9**（`README.md:33`）。
- **环境**（`environment.yml`，conda 环境名 `text2cad`）：`python=3.9`（`environment.yml:11`）、`pytorch=2.2.1`（`:13`）、`torchvision=0.17.1`（`:14`）、`pythonocc-core=7.7.2`（`:15`）、`cuda`（`:16`）；pip 段含 `gradio`（`:38`）、`open3d`、`trimesh` 等。
- **显存**：README 没有给推理显存明称值（**查不到**）；但训练配置里 `batch_size: 16 # for 80 GB gpu`（`Cad_VLM/config/trainer.yaml:60`，即作者按 **80 GB 卡**、约 150 epoch 的规模记的，`trainer.yaml:62`），推理配置 `batch_size: 4 # for 80 GB gpu`（`Cad_VLM/config/inference.yaml:52`）。
- **本机（Windows / Python 3.14.7 / RTX 4080S 16GB）能不能跑**：**不能直接跑**。① README 只声明 Linux（`README.md:32`），且数据准备脚本把多进程启动方式设成 `forkserver`（`CadSeqProc/json2vec.py:42`）——Windows 只支持 `spawn`，这一行在 Windows 上直接抛错；② `pythonocc-core=7.7.2` 只有 conda 通道、且锁 `python=3.9`（`environment.yml:11`、`:15`），本机 3.14.7 不匹配；③ 即便推理，16 GB 显存要放下 BERT-large + 8 层解码器（16 GB 为本机配置、非仓库声明；模型维度见 `Cad_VLM/config/trainer.yaml:21`、`:32-38`），是否够用**未实测**（README 没给推理显存值）。⇒ 判断：**要跑必须另建 Linux/conda 环境**，本机只适合读码。
- **未实测**：没有下载 `text2cad_v1.0` 权重与数据（`README.md:92`），没有执行任何训练/推理命令。

## 5. 失败模式与已知坑

| # | 坑 | 来源 |
|---|---|---|
| 1 | **生成的序列会无效**：靠 `from_vec().create_cad_model()` 的异常来判定，异常率即 `is_invalid`；没有语法约束解码（无 grammar/CFG） | `Cad_VLM/test.py:229-242` |
| 2 | **长度上限写死**：整序列 272 步、sketch 段 150、最多 10 段 extrusion（`macro.py:14`、`:34`、`:35`）⇒ 更复杂的零件根本装不进表示 | `CadSeqProc/utility/macro.py:14-36` |
| 3 | **flag/index 掩码写错就崩**：源码注释三次强调「wrong flag / wrong index / wrong masking may result in invalid model」，说明这是踩过的坑而非假想 | `Cad_VLM/models/decoder.py:237`、`:249`、`:261` |
| 4 | **量化参数无精度解释**：8 bit 量化（`N_BIT=8`，`macro.py:6`）后，尺寸只能是 1/256 档；评测里对参数也只有「近似」判据 | `macro.py:6`、`Evaluation/eval_seq.py:69-80` |
| 5 | **采样模式下靠真值择优**：`TOPK=5` 时用与 GT 的 Chamfer 距离在 5 个候选里挑最好的（默认 max 模式不触发），此时指标偏乐观——不能当作可部署的「生成质量」 | `Cad_VLM/test.py:184-187`、`:259-273` |
| 6 | **只覆盖 sketch–extrude 两族命令**：`CURVE_TYPE=["Line","Arc","Circle"]`、`EXTRUDE_OPERATIONS` 只 4 类（`macro.py:20-23`）⇒ 没有圆角/倒角/抽壳/孔/扫描 | `macro.py:20-23` |
| 7 | **Windows 直接不可用**：`forkserver` 启动方式（`json2vec.py:42`）+ README 只声明 Linux（`README.md:32`） | `CadSeqProc/json2vec.py:42` |
| 8 | 训练/推理配置里的 batch 都按 80 GB 卡标注，说明原作者也没在消费级卡上验证过 | `trainer.yaml:60`、`inference.yaml:52` |
| 9 | 数据集页面我这次取数失败（HTTP 404，2026-10-24；https://huggingface.co/datasets/SadilKhan/Text2CAD ）⇒ 数据规模与标注条数**查不到** | 本机 `web_fetch` 结果 |

## 6. 对我方目标的可用处（机制层面）

我方目标：让**普通模型**也能建出**能用、规范**的模型。

1. **「冻结大模型 + 只训小头」的成本取向**值得照搬思路：让普通模型可用的关键不是训更大的模型，而是把「文本理解」和「序列生成」拆开、只训后者——我方若做「自然语言 → 建模计划」，也应把重活压在推理侧的小结构上（模板/校验器），而不是指望模型记住 API。
2. **结构元数据显式化**（flag/index）是我方最该学的一条：把「这一步属于哪个特征/哪张草图」写成**独立的列**，而不是让模型在上下文里记。对应到 SolidWorks：每次调用都带「目标特征 id / 目标草图 id」，模型就不可能张冠李戴。
3. **`is_invalid` 作为一等字段**：把「建不出来」的比例单独统计并过滤，与我方「验证等级」制度同构——交付报告里必须有这个数，而不是被平均分吸收。
4. **提示分级**给了「同一需求不同详细度」的评测范式：我方可以用同一份建模脚本吃「一句话」和「带尺寸的一整段」，观测在哪一级开始建错。
5. **反面（同样是收获）**：它的表示只有 sketch–extrude，**没有工程特征**；建出来的东西可能「几何像」但「不规范」（无倒角、无标准件、无约束）。我方目标里「规范」这一半，它没有回答。

## 7. 许可与红线

**CC BY-NC-SA 4.0（非商用 + 相同方式共享）** —— 原文见 `LICENSE:1`、`LICENSE:7`：许可方为 **DFKI GmbH**，条款为 Attribution（署名）/ **NonCommercial（不可商用）** / **ShareAlike（衍生作品须用同一许可分发）**（`LICENSE:15-17`）。

**红线（对我方）**：
1. **只读思想，不可商用**：不能把它的代码、文本、权重、数据用于任何商业交付；
2. **不能抄代码/不能抄文本**：ShareAlike 会传染——一旦改编进我方产物，我方产物就得按 CC BY-NC-SA 分发，等于自断商用；
3. **数据也不能混**：其文本标注与预处理 pkl 来自 HF 数据集页（`README.md:61`、`:92`），同样受该许可（及上游 DeepCAD 数据条款）约束；
4. 可以做的：读它的**架构与判据**（例如「结构列显式化」「invalid 单独统计」），用自己的代码重新实现，**不复制任何一行源码/提示词模板**。
5. 待核：上游 DeepCAD 数据本身的再分发条款**不在本仓库内（查不到）**。

## 8. 证据清单

| 证据 | 出处 |
|---|---|
| 许可原文（CC BY-NC-SA 4.0） | `LICENSE:1`、`LICENSE:7`、`LICENSE:15-17` |
| 定位与 4 级提示 | `README.md:3`、`Evaluation/eval_seq.py:36-41` |
| 平台/版本声明 | `README.md:32-33` |
| 数据来源（DeepCAD） | `README.md:49`、`:53`、`:57`、`:61` |
| 向量表示与长度上限 | `CadSeqProc/utility/macro.py:6-14`、`:34-36`、`:40-44` |
| 序列构造（token/flag/index） | `CadSeqProc/cad_sequence.py:242-274` |
| 模型结构 | `Cad_VLM/models/text2cad.py:20-29`、`Cad_VLM/config/trainer.yaml:12-42` |
| 文本编码器冻结 | `Cad_VLM/train.py:85-87`、`Cad_VLM/models/text2cad.py:123-127` |
| 解码与掩码 | `Cad_VLM/models/decoder.py:166-282` |
| 无效序列处理 | `Cad_VLM/test.py:229-286` |
| 评测指标 | `Evaluation/eval_seq.py:69-80` |
| STEP/STL/PLY 导出 | `CadSeqProc/README.md:37-43` |
| 依赖与环境 | `environment.yml:11-16`、`:38` |
| Windows 不可用（forkserver） | `CadSeqProc/json2vec.py:42` |
| Demo | `README.md:151-170`、`App/app.py` |
| 仓库元数据 | `gh api repos/SadilKhan/Text2CAD`（2026-10-24 取数） |
| 论文摘要（文本标注来源） | https://arxiv.org/abs/2409.17106 |

## 9. 未确认事项

1. **未实测**：没建 conda 环境、没下载 `Text2CAD_1.0.pth`（`README.md:92`）、没跑过 `train.py` / `test.py` / `eval_seq.py` ⇒ 生成质量与无效率为**读码结论**。
2. **数据规模查不到**：README 只说「下载 DeepCAD 数据再转向量」＋「下载文本标注」，没写条数；HF 数据集页本次取数 404（2026-10-24）。上游 DeepCAD 是 178,238 个模型（https://arxiv.org/abs/2105.09492 摘要），但 Text2CAD 实际使用的子集大小**没有记录**。
3. **参数量查不到**：仓库有 `total_parameters()` 但没写结果；我按配置能算出「BERT-large + 8 层×8 头/1024 维」，但**不自行折算出参数量数字**。
4. **`is_invalid` 的实际比例未知**（论文表格未读原文 PDF），故不写任何百分比。
5. **许可边界需法务确认**：CC BY-NC-SA 4.0 下「读机制再用自己代码实现」是否构成衍生作品，属解释问题；本卡按其最严口径处理（只读思想）。
6. **tag 行 `deliver=sequence` 不在给定枚举内**（枚举是 STEP/mesh/drawing/gcode/none）：按任务模板逐字保留，此处标注——真实交付物是 `output.pkl` 里的序列，STEP/STL 是可选下游步骤。
