# DeepCAD

<!-- survey: class=D; repr=sequence; orchestration=single; verify=numeric; deliver=sequence; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/rundiwu/DeepCAD · 论文 https://arxiv.org/abs/2105.09492（ICCV 2021）· 数据/权重 http://www.cs.columbia.edu/cg/deepcad/ （`README.md:40`、`:119`） |
| 许可 | **MIT** —— 读仓库内 `LICENSE` 原文：`LICENSE:1` 为 `MIT License`、`LICENSE:3` 为 `Copyright (c) 2022 Rundi Wu`（`gh api` 亦报 `license.spdx_id = MIT`）⇒ **可借鉴**（可商用，须保留版权声明） |
| 元数据 | stars **834** · forks 172 · open issues 19 · 语言 Python · 最近推送 **2024-04-12T13:45:36Z** · 创建 2021-07-31（来源：`gh api repos/rundiwu/DeepCAD`，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\rundiwu__DeepCAD |
| 证据等级 | **读码**（读 LICENSE / README / `cadlib/macro.py` / `cadlib/extrude.py` / `config/configAE.py` / `model/autoencoder.py` / `trainer/loss.py` / `dataset/json2vec.py` / `evaluation/*.py` / `utils/export2step.py` / `requirements.txt` + `gh api` + arXiv 摘要；**未**建环境、未训练、未跑推理） |

## 1. 一句话定位

它把 CAD 建模历史压成**定长、定元的「命令 + 参数字槽」整数矩阵**（每步 1 个命令 + 16 个参数槽，60 步封顶），用 Transformer 自编码器重建、再用 latent GAN 随机生成；这是后来 FlexCAD / Text2CAD 的共同底座（`cadlib/macro.py:3-40`、`config/configAE.py:54-68`、`README.md:3-8`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**① 输入**：主线是**无条件生成**（latent GAN 采样 z），重建实验则是「给一条 GT 序列 → 编码 → 解码」；仓库另带一个点云条件版本（`pc2cad.py`、`pc2cad_train.py`），但 README 正文没写其用法（`README.md:52-113` 未提）⇒ 该分支**未确认**。

**② 中间表示＝定长量化矩阵**（不是文本、不是树）：
- 命令空间 6 个：`Line / Arc / Circle / EOS / SOL / Ext`（`cadlib/macro.py:3`）；
- 每步参数 16 槽＝sketch 5（x, y, α, f, r）＋ 平面 3（θ, φ, γ）＋ 平移与尺寸 4（p_x, p_y, p_z, s）＋ 拉伸 4（e1, e2, b, u）（`cadlib/macro.py:17-22`）；
- **每个参数槽被量化成 256 类**（`ARGS_DIM=256`，`macro.py:40`），先归一化到单位立方、再 ×256 取整（归一化：`cadlib/extrude.py:289-292`；取整：`cadlib/curves.py:139-140`、`cadlib/extrude.py:190-196`）；
- 序列上限：整条 **60 步**、最多 10 段拉伸 / 6 个 loop / 每个 loop 15 条曲线（`macro.py:36-39`）；
- 落盘形式是 h5 里的 `vec`，形状 (L, 17)（`dataset/json2vec.py:45-46`）。
- **命令与参数解耦**：每个命令允许哪些参数槽由一张常量表决定（`CMD_ARGS_MASK`，`macro.py:27-32`）——这是「规范」的第一道机器可判据。

**③ 生成**：Transformer 自编码器，编码器 4 层 / 解码器 4 层、`d_model=256`、8 头、`dim_z=256`、FF 512（`config/configAE.py:54-60`）；**解码器是非自回归的**——没有 `tgt_mask`，60 个位置一次并行出（`model/autoencoder.py:116-123`）；条件生成再叠一个 latent GAN（`lgan.py`、`model/latentGAN.py`、`trainer/trainerLGAN.py`）。

**④ 编排＝单模型单轮**：无 agent、无工具调用、无迭代修复；`train.py` → `test.py`（rec / enc / dec 三模式，`README.md:80`、`:63`、`:103`）。

**⑤ 执行**：向量 → `vec2CADsolid` / `create_CAD`，用 pythonocc 依次建草图与拉伸实体（`utils/export2step.py:11-12`、`:39`、`:45`）。

**⑥ 验证（三层）**：① 命令准确率 `ACC_cmd` 与参数准确率 `ACC_param`，参数按**容差 3（即 3/256）** 判对、且只统计命令猜对的位置（`evaluation/evaluate_ae_acc.py:14`、`:45-63`）；② Chamfer 距离 + **invalid ratio**（`evaluation/evaluate_ae_cd.py:122-133`）；③ 导出时用 `BRepCheck_Analyzer` 过滤无效实体（`utils/export2step.py:51-55`）。

**⑦ 交付**：`.step`（`utils/export2step.py:59` 的 `write_step_file`）与 h5 中间结果；**主产物仍是序列**，STEP 是下游导出脚本。

**★ 学术项补全**：中间表示＝定长 (60, 17) 量化矩阵（见 ②）；模型基座＝**从零训的 Transformer AE**（不是 LLM），4+4 层 / 256 维（`configAE.py:54-60`），参数量仓库未写 ⇒ **查不到**；训练数据＝**Onshape 公开文档**（经 ABC 数据集的链接爬取）→ 自建 **178,238** 个模型及其建模序列（`README.md:49`；条数来源：https://arxiv.org/abs/2105.09492 摘要）；评测指标＝`ACC_cmd`/`ACC_param`、Chamfer、invalid ratio、以及随机生成的 COV/MMD/JSD（`README.md:88-113`）。

## 3. 技术方案要点（可迁移的机制）

| 机制 | 说明（只讲机制，不抄代码） | 证据 |
|---|---|---|
| **命令–参数解耦 + 参数合法性掩码** | 每个位置同时输出「6 类命令」和「16 个参数槽各 256 类」，但**只有该命令合法的槽参与损失**（用一张命令×参数 0/1 表筛）⇒ 非法参数在训练时就不产生梯度，模型学不到「给 Line 编 r 参数」 | `cadlib/macro.py:27-32`、`trainer/loss.py:16`、`:27-33` |
| **非自回归定长解码** | 60 步一次并行预测，没有逐步停止、没有 exposure bias；代价是长度上限写死、且必须靠 EOS/SOL 符号表达结构 | `config/configAE.py:68`、`model/autoencoder.py:116-123` |
| **group embedding：显式的「同一特征」归属** | 组 id 不是另存的标签，而是从命令序列里现算（`(commands == EXT_IDX).cumsum`），每个位置都知道自己属于第几段 sketch–extrusion | `model/model_utils.py:54-59`、`model/autoencoder.py:19-24` |
| **量化 + 容差判据** | 256 级量化把回归变成分类；评测时参数差 < 3 才算对，且 `b`（bool）与 `u`（extent type）要求严格相等 | `cadlib/macro.py:40`、`evaluation/evaluate_ae_acc.py:55-60` |
| **无效即过滤、且单独成指标** | 建体失败不修、只丢；`invalid ratio` 作为一等数字单独打印，而不是混进平均分 | `utils/export2step.py:51-55`、`evaluation/evaluate_ae_cd.py:122-133` |
| **超限即丢弃（数据侧硬门）** | 序列超 60 步或超各层上限时 `to_vector` 直接返回 `None`，数据准备阶段打印 "exceed length condition" 并跳过 | `cadlib/extrude.py:263-270`、`dataset/json2vec.py:36-38` |
| **结构符号靠保留字** | `EOS`（序列结束）与 `SOL`（sketch 开始）本身占一个命令位，使定长矩阵仍能表达变长结构 | `cadlib/macro.py:24-25`、`model/model_utils.py:28-44` |

## 4. 运行条件与依赖

- **平台**：README 明写 **Linux**、**NVIDIA GPU + CUDA/cuDNN**、**Python 3.7 / PyTorch 1.5+**（`README.md:18-20`）。
- **依赖**：`requirements.txt` 全部 pin 死老版本——`numpy==1.18.1`、`torch==1.5.1`、`h5py==2.10.0`、`scipy==1.4.1`、`trimesh==3.2.19` 等（`requirements.txt:1-13`）；几何内核走 conda：`conda install -c conda-forge pythonocc-core=7.5.1`（`README.md:34`）。
- **显存**：README **未给明称值（查不到）**；训练默认 `batch_size: 512`（`config/configAE.py:84`）、`nr_epochs: 1000`（`:87`），作者用 `-g 0` 单卡起（`README.md:56`）但没写卡型号。
- **本机（Windows / Python 3.14.7 / RTX 4080S 16GB，本机配置非仓库声明）能不能跑**：**不能直接跑**，三条硬阻碍：（来源：本卡 §4 环境探查）
  1. **`np.int` / `np.float` 已被 numpy ≥1.24 删除**，仓库里这类调用共 **36 处**（来源：对 `*.py` 递归跑 `Select-String -Pattern 'np\.int\b|np\.float\b|np\.bool\b'`，2026-10-24 取数），分布在 `cadlib/curves.py:139`、`cadlib/extrude.py:61`、`evaluation/evaluate_ae_acc.py:36`、`utils/export2step.py:38`、`utils/show.py:48`、`test.py:63` 等；而 `requirements.txt:5` 又要求 `numpy==1.18.1`（该版本在 Python 3.14 上装不了）⇒ **老 numpy 与新 Python 互斥**，必须换 py3.7–3.9 的 conda 环境并接受老依赖；
  2. `pythonocc-core=7.5.1`（`README.md:34`）只走 conda，且没有新 Python 的构建；
  3. 显存：训练 batch 512 与 1000 epoch（`configAE.py:84`、`:87`）明显不是 16 GB 卡的量级（16 GB 为本机配置、非仓库声明）；推理/小 batch 微调是否可行**未实测**。
- **未实测**：没有装 conda 环境、没有下载 `data.tar` / `pretrained.tar`（`README.md:40`、`:119`）、没有跑 `train.py` / `test.py`。

## 5. 失败模式与已知坑

| # | 坑 | 来源 |
|---|---|---|
| 1 | **现代 numpy 上直接崩**：`np.int`/`np.float` 共 36 处（来源：对 `*.py` 递归跑 `Select-String -Pattern 'np\.int\b|np\.float\b|np\.bool\b'`，2026-10-24 取数） | `cadlib/curves.py:139`、`evaluation/evaluate_ae_acc.py:36`、`utils/export2step.py:38`、`test.py:63` |
| 2 | **长度上限写死、超限静默丢弃**：60 步 / 10 拉伸 / 6 loop / 15 曲线（`macro.py:36-39`），超了 `to_vector` 返回 `None`、数据准备阶段直接跳过 ⇒ 复杂零件根本不在数据集里，评测也看不到它们 | `cadlib/macro.py:36-39`、`cadlib/extrude.py:263-270`、`dataset/json2vec.py:36-38` |
| 3 | **精度只有 1/256**，且评测容差 3/256 就算对 ⇒ 「参数准确」是弱判据，尺寸差 1% 量级也可能算对 | `cadlib/macro.py:40`、`evaluation/evaluate_ae_acc.py:14`、`:55` |
| 4 | **只有拉伸一族建模操作**：命令表 6 个里 5 个是草图/边界符号、只有 `Ext` 一个实特征（`macro.py:3`），拉伸类型只 3 类、布尔操作只 4 类（`macro.py:11-14`）⇒ 没有圆角/倒角/孔/旋转/扫描 | `cadlib/macro.py:3`、`:11-14` |
| 5 | **多 profile 被拆开**：源码注释写明「only support single sketch profile. Extrusion with multiple profiles is decomposed」⇒ 一个实体被拆成多段拉伸，语义有损 | `cadlib/extrude.py:78-79` |
| 6 | **无效实体只过滤不修复**：`BRepCheck_Analyzer` 不过就 `continue`，没有修复/重试路径 | `utils/export2step.py:51-55` |
| 7 | **评测脚本用 `np.bool`**（同样已被删除），参数掩码那段在新 numpy 上直接抛 | `evaluation/evaluate_ae_acc.py:62`、`:91` |
| 8 | 序列会被截断/补 EOS 到定长，重建时靠 `EOS`/`SOL` 恢复结构——一旦模型把 `EOS` 放错位置，后面全是噪声 | `cadlib/extrude.py:274-282`、`model/model_utils.py:28-44` |
| 9 | 点云条件分支（`pc2cad.py`）README 未给用法与数据，**未确认**能否跑通 | `README.md:52-113`（未提及）、`pc2cad.py` |

## 6. 对我方目标的可用处（机制层面）

我方目标：让**普通模型**也能建出**能用、规范**的模型。

1. **「命令–参数解耦 + 参数合法性掩码」是我方最该抄的机制**：它把「这个特征允许哪些参数」写成一张常量表，让非法组合在**训练/生成时就拿不到表达力**。对应到我方：每个 SolidWorks 特征（拉伸/切除/圆角/孔）应先声明「允许的参数槽 + 单位 + 取值范围」，普通模型只在这些槽里填数——「规范」从"事后检查"变成"结构上写不出错的"。
2. **定长、非自回归的「一次出整个计划」**：对普通模型友好——不需要它自己决定何时停，也不需要它维护逐步上下文；代价是必须有一个固定的计划骨架（我方可以固定成「草图 N + 特征 M」的槽位模板）。
3. **group/index 显式化归属**：让每个位置自带「我属于第几个特征」的列，模型就不必靠上下文猜「这行是给哪个特征的」。映射到我方：每条调用都带 `feature_id`，装配关系带 `mate_id`。
4. **把「建不出来」单独统计成指标**（invalid ratio）比把它混进平均 Chamfer 有价值得多——我方的验证报告必须有这一列，并且要有 `BRepCheck`/几何有效性这类**硬门**。
5. **容差判据要写数值**：它把「参数对」定义成「差 < 3/256」，我方的数值验证也必须把阈值写在门禁里，而不是说"基本一致"。
6. **反面（同样是收获）**：它只是"历史重放"——重建的是几何，不是**可编辑的特征树**；没有圆角/孔/约束，也没有工程规范（配合、公差、标准件）。SolidWorks 的价值恰恰在这些下游，所以它的表示可以借，**目标不能停在这里**。

## 7. 许可与红线

**MIT**（`LICENSE:1` `MIT License`；`LICENSE:3` `Copyright (c) 2022 Rundi Wu`）：**可读、可改、可商用**，义务是保留版权声明与许可文本；`gh api` 报 `license.spdx_id = MIT`，与文件原文一致。待核：① 数据 `data.tar` 与预训练权重 `pretrained.tar` 在 README 里声明「公开可用」（`README.md:40`、`:49`、`:119`），但**数据再分发的具体条款不在本仓库内（查不到）**；② 数据源自 Onshape 公开文档（`README.md:49`），Onshape 自身条款未核。⇒ 借用其**表示与判据**无碍；**若要把他发布的 h5 数据或权重搬进我方交付物，先核这两项**。

## 8. 证据清单

| 证据 | 出处 |
|---|---|
| 许可原文 | `LICENSE:1`、`LICENSE:3` |
| 定位与论文 | `README.md:3-8`、https://arxiv.org/abs/2105.09492 |
| 平台/依赖声明 | `README.md:18-20`、`README.md:31-35` |
| 依赖 pin 列表 | `requirements.txt:1-13` |
| 数据来源与规模提示 | `README.md:40-49`、https://arxiv.org/abs/2105.09492（178,238） |
| 命令表与参数槽定义 | `cadlib/macro.py:3-25` |
| 命令×参数合法表 | `cadlib/macro.py:27-32` |
| 序列上限 | `cadlib/macro.py:36-39` |
| 量化与归一化 | `cadlib/macro.py:40`、`cadlib/extrude.py:289-292`、`cadlib/curves.py:139-140`、`cadlib/extrude.py:190-196` |
| 向量化/超限返回 None | `cadlib/extrude.py:263-282`、`dataset/json2vec.py:26-46` |
| 模型结构 | `config/configAE.py:49-68`、`model/autoencoder.py:8-123` |
| 损失与参数掩码 | `trainer/loss.py:16-33` |
| group 归属 | `model/model_utils.py:54-59`、`model/autoencoder.py:19-24` |
| 评测判据（容差 3） | `evaluation/evaluate_ae_acc.py:14`、`:45-63` |
| invalid ratio | `evaluation/evaluate_ae_cd.py:122-133` |
| STEP 导出与 BRep 过滤 | `utils/export2step.py:36-59` |
| 可视化 | `utils/show.py:48-51`、`cadlib/visualize.py:19`、`:25` |
| 仓库元数据 | `gh api repos/rundiwu/DeepCAD`（2026-10-24 取数） |

## 9. 未确认事项

1. **未实测**：没建 conda 环境、没下数据/权重、没跑任何 `train.py`/`test.py`/`evaluation/*`；「本机不能跑」是**读码 + 版本冲突推断**，不是运行结果。
2. **参数量查不到**：`configAE.py` 给了层数/维度（`configAE.py:54-60`），但仓库没写总参数量，我不自行折算。
3. **数据条款查不到**：`data.tar` 的再分发许可、以及 Onshape 侧条款都不在仓库里。
4. **点云条件分支（`pc2cad.py`）状态未确认**：README 只列 AE 与 latent GAN 两条线，未说明该分支的数据与命令。
5. **论文里的指标数值未取**（未读 PDF）⇒ 本卡只记录指标的**定义与阈值**，不写任何百分比/倍数。
6. **`np.int` 类调用"会让现代 numpy 崩"是根据 numpy 1.24 的移除清单推断**，我没有在本机装 numpy 试（纪律：不装包）。
7. **tag 行 `deliver=sequence` 不在给定枚举内**（枚举是 STEP/mesh/drawing/gcode/none）：按任务模板逐字保留，此处标注——真实交付物是 h5/序列，STEP 由 `utils/export2step.py` 另跑。
