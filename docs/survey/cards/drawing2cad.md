# Drawing2CAD

<!-- survey: class=D; repr=sequence; orchestration=single; verify=numeric; deliver=none; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/lllssc/Drawing2CAD · 论文 https://arxiv.org/abs/2508.18733 · ACM MM 2025 |
| 许可 | MIT（读克隆内 `LICENSE:1-3` 原文「MIT License」+「Copyright (c) 2025 lllssc」；`gh api` 报 `spdx_id=MIT`）→ **可借鉴**（保留版权声明） |
| 元数据 | stars 157 · 最近推送 2026-08-26T07:39:49Z · 语言 Python（来源：https://api.github.com/repos/lllssc/Drawing2CAD ，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\lllssc__Drawing2CAD （HEAD `0737117`，末次提交 2026-08-26T15:39:48+08:00；`git status --porcelain` 为空） |
| 证据等级 | 读码 |

## 1. 一句话定位

ACM MM 2025 的「**矢量工程图 → CAD 命令序列**」纯 seq2seq 方案：输入是**已矢量化的** SVG 路径命令序列（多视图），输出是 DeepCAD 约定的草图+拉伸命令序列，中间没有任何几何推理，全靠一个 Transformer 把一种形式语言翻成另一种（`README.md:3`、`README.md:63-65`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

★ **输入形态**：**矢量工程图**——SVG 里的路径命令，作者已对每个模型预备了四个视图 `Front` / `Top` / `Right` / `FrontTopRight`，并做过路径简化、去重、重排与 viewbox 归一（`README.md:55`）。★ 不是位图、不是线稿扫描件、**也不是实体的三视图线稿**（它用的是自己从 CAD 模型导出的 SVG 管线，`README.md:67`）。

★ **中间表示（这是本卡的分类要点）**：

1. **输入侧 = SVG 命令序列**：命令词只有 4 个——`SOS` / `EOS` / `L`（直线）/ `C`（贝塞尔），每条命令 8 个参数槽（起点、两个控制点、终点），逐命令用 `SVG_CMD_ARGS_MASK` 规定哪些槽有效（`config/macro.py:16-20`、`:30-32`、`:47-50`）。每个视图定长 100 个 token（`config/macro.py:59`），四视图 = 400 行；每行还带一个**视图编号**列（`dataset/bi_sequence_dataset.py:39-57`）。
2. **输出侧 = DeepCAD 命令序列**：6 个命令词（`Line`/`Arc`/`Circle`/`EOS`/`SOL`/`Ext`）+ 16 个参数槽（草图 5 + 平面 3 + 平移 4 + 拉伸 4），逐命令用 `CAD_CMD_ARGS_MASK` 掩码（`config/macro.py:3`、`:23-28`、`:40-45`）。上限：总长 60 个 token、10 次拉伸、每草图 6 个 loop、每 loop 15 条曲线（`config/macro.py:54-59`）。

- **生成**：`SVG2CADTransformer` = 编码器（4 层）→ `Bottleneck` → **两个解码器**。编码器把全部输入 token 做掩码平均池化成一个 latent `z`（`model/model.py:84`），解码器从**恒定查询**（`ConstEmbedding` 造出定长的空槽）出发，**一次性**给出整条序列（`model/model.py:50-62`、`:125-168`）。★ **非自回归**：没有逐步喂回前一个 token。参数解码器还把命令解码器的隐状态当 guidance 加进来（`model/model.py:200-204`、`:159-164`）。
- **编排**：**单次前向、无回环、无工具、无人工**；`test.py` 循环遍历测试集 batch 一次性出结果（`test.py:27-50`）。**训练依赖**，且仓库**不提供预训练权重**（`README.md:78-86` 只讲 training 与 evaluation）。
- **执行**：输出 logits 逐位 `argmax` → 反量化 → 按掩码回填 → 存成 h5（`trainer/trainer.py:42-53`、`test.py:44-49`）。
- **验证**：训练/验证期**逐参数位准确率**，按命令类型分组统计（plane / trans / extent / line / arc / circle，`trainer/trainer.py:83-100`）；测试期只把 `out_vec` 与 `gt_vec` 并排存进 h5（`test.py:44-49`）——**指标与几何导出要另接工具**（`README.md:86` 明写去用 DeepCAD 的代码）。
- **交付**：**仓库本身不导出任何 CAD 文件**（这是卡里 `deliver=none` 的依据）。要 STEP/网格/可视化，得自己按 DeepCAD 的脚本接（`README.md:86`）。

## 3. 技术方案要点（可迁移的机制）

- **视图编号当一等嵌入**：`view_embed = nn.Embedding(4, 4)`，与命令嵌入、参数嵌入**拼接**后过一层 MLP（`model/model.py:15-20`、`:41-45`）。⇒ "这条命令属于哪张图"是显式输入，不是靠位置猜。
- **一个模型、三种输入档位**：`--input_option {1x,3x,4x}`（`train.py:73-75`、`config/config.py:95`）只改数据切片，不改网络——`1x` 取第 4 个视图那 100 行（`dataset/bi_sequence_dataset.py:44-47`），`3x` 取前三视图（`:49-52`），`4x` 取全部（`:54-57`）。★ 注意 `1x` 取的是 `FrontTopRight` 而不是正视图（切片上界 300 = 3 × `SVG_MAX_TOTAL_LEN`）。
- **非自回归 + 恒定查询**：整条序列的槽位一次给全，再逐槽做分类（`model/model.py:50-62`、`:84-85`）。⇒ 误差不会沿时间步累积，训练也容易并行。
- **命令导向（command-guided）双解码器**：先解命令，再把命令解码器的隐状态当**额外输入**加到参数解码器（`model/model.py:200-204`、`:159-164`）——参数预测以"这是什么命令"为条件，是"命令-参数掩码"的软版本。
- **掩码回填保证输出合法**：`logits2vec` 按命令类型把不该有的参数位强制成 -1（`trainer/trainer.py:42-53`，掩码表 `config/macro.py:40-45`）。
- **容差软标签损失（很值得抄）**：参数损失不是硬 CE，而是先按 `tolerance=3`、`alpha=2.0` 造一个"以真值为中心、邻位指数衰减"的软目标分布，再算交叉熵并只在该命令的有效参数位上平均（`trainer/loss.py:41-59`）。⇒ 量化到 256 档的连续量，"差一档"不该与"差 100 档"同罚。
- **丢失与填充用两套掩码**：命令损失按"可见性 × 填充"掩码过滤（`trainer/loss.py:23-24`、`:32`），参数损失用命令掩码（`trainer/loss.py:30`、`:58`）。
- **诊断粒度贴着表示结构**：准确率不是总分，而是按 plane / trans / extent / line / arc / circle 分开报（`trainer/trainer.py:83-100`）——一眼看出是"平面摆错了"还是"圆弧半径错了"。

## 4. 运行条件与依赖

- 官方条件（自述）：Python 3.9、CUDA 11.8+（`README.md:42-43`）。
- 依赖钉版：`torch==2.1.0` / `torchvision==0.16.0` / `torchaudio==2.1.0`，另有 `shapely`、`trimesh`、`h5py`、`x-clip`、`tensorboardX`（`requirements.txt`，逐行见文件）。
- **GPU 是硬要求**：训练/推理都把网络 `.cuda()`（`trainer/trainer.py:14`、`trainer/loss.py:20-21`），命令行帮助明写 "CPU not supported"（`config/config.py:79`）。
- 默认超参不小：batch 256、200 epochs（`config/config.py:81`、`:84`），16GB 卡上大概率要调小（本卡未实测）。
- 数据要自己下：Google Drive 三份（`svg_raw` / `svg_vec` / `cad_vec`，`README.md:53-65`），CAD 模型源自 DeepCAD（`README.md:67`）。
- **没有预训练权重**：`test.py` 必须给 `--ckpt`（`test.py:19`、`trainer/base.py:69-83`），而 README 未提供下载链接（`README.md:78-86`）⇒ 想复现必须先自己训。
- 本机判断（Windows / 默认 Python 3.14.7 / RTX 4080S 16GB）：**不能按仓库给的方式直接跑**——`torch==2.1.0` 没有 cp314 wheel，需另建 3.9/3.10 venv（本卡未实测 wheel 清单）。本次**未安装、未运行**；显存实际占用**未实测**。

## 5. 失败模式与已知坑

- **必须先训**：无权重 + `--ckpt` 必填（`test.py:19`）⇒ 拿不到"开箱即用"的结果；200 epochs 的训练成本（`config/config.py:84`）没人替你付。
- **表示上限硬**：总长 60 个 token、拉伸 ≤ 10 次、每草图 ≤ 6 loop、每 loop ≤ 15 曲线（`config/macro.py:54-58`）⇒ 复杂零件直接被截。
- **只有草图 + 拉伸**：命令表就 6 个词（`config/macro.py:3`），没有倒角/圆角/孔/阵列/扫掠/放样，也没有装配。
- **输入必须是已矢量化的 SVG**：位图要先自己矢量化；而且作者的四视图是**从 CAD 模型渲染出来的**（`README.md:67` 的 STEP2SVG-Pipeline），真实工程图里的尺寸标注、公差、剖面线、螺纹符号一律没有对应词表。
- **`1x` 的语义容易读错**：`1x` 取的是第 4 个视图（`FrontTopRight`）那一段切片（`dataset/bi_sequence_dataset.py:44-47`），不是"任意单张正视图"——按名字猜会读反。
- **评测链路断在仓库边界**：仓库只到 `out_vec`/`gt_vec`（`test.py:44-49`），连 CD/IR 指标都要借 DeepCAD 的代码（`README.md:86`）⇒ 想复现论文数字要自己补一截。
- **数据预处理不在本仓**：SVG 的简化/去重/重排/viewbox 归一在外部仓库（`README.md:67` 的 `STEP2SVG-Pipeline`）⇒ 换数据源要自己重做这一步。

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的 SolidWorks 模型。

1. **非自回归骨架最适合"普通模型"**：先把整条特征序列的槽位摆出来（类型 + 参数位），再逐槽分类（`model/model.py:50-62`、`:84-85`）——比逐步自回归更不容易"一步错、步步错"。
2. **命令导向双解码器**：先定特征类型，再让参数以类型为条件（`model/model.py:200-204`）——正是"先选拉伸/切除/旋转，再填尺寸"的机器版。
3. **容差软标签直接可用**：尺寸量化后，"差 1 档"与"差 100 档"应当不同罚；指数衰减软目标 + 有效位掩码（`trainer/loss.py:41-59`）是现成的做法。
4. **掩码回填保证输出合法**：命令类型决定哪些参数位存在，其余强制空（`trainer/trainer.py:42-53`）——普通模型最常见的失败是"给了不该给的参数"，这条能从结构上消掉。
5. **多来源用"视图/来源编号嵌入 + 配置切换"**：一套网络吃 1/3/4 张图，只改切片与嵌入（`model/model.py:15-20`、`config/config.py:95`）——我方要做"工程图 / 草图 / 文字"多入口时同构。
6. **分项准确率当日常指标**：按参数类别分开报（`trainer/trainer.py:83-100`），比一个总分更能指出该修哪一块。
7. **反面警示**：它到"命令序列"为止就交卷了（`deliver=none`）⇒ 中间表示若不带特征语义与导出链，最后仍进不了 SolidWorks。

## 7. 许可与红线

- MIT（`LICENSE:1-3`，「Copyright (c) 2025 lllssc」）⇒ **可借鉴**：可读、可抄、可改、可商用，义务是保留版权与许可声明。
- 但它**建立在 DeepCAD 的数据表示与数据之上**（`README.md:67`、`README.md:92`）：命令词表、参数槽、`cad_vec` 都来自 DeepCAD。⇒ 若要搬这套表示，**表示本身的来源是 DeepCAD（另有许可）**，需单独核；本卡未核对 DeepCAD 的许可条款。
- 依赖里 `shapely`（BSD）、`trimesh`（MIT）、`x-clip`（CLIP 相关，条款需另核）、`CairoSVG`（LGPL，仅 README 提到用于 PNG 转换，`README.md:55-61`）——都不在本仓内 vendored。
- 数据集的条款不随仓库 LICENSE 走（Google Drive 分发，`README.md:53`）。

## 8. 证据清单

- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\LICENSE:1-3`（MIT + lllssc 版权行）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\README.md:42-43`（Python 3.9 / CUDA 11.8+）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\README.md:53-65`（数据三份 + 四视图 + 预处理）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\README.md:67`（CAD 模型源自 DeepCAD；SVG 管线在外部仓库）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\README.md:73-86`（训练/评测命令；导出与可视化借 DeepCAD 代码）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\config\macro.py:3`、`:16-20`、`:23-28`、`:30-32`、`:40-45`、`:47-50`、`:54-59`（两套命令表、参数槽、掩码、上限）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\config\config.py:79`、`:81`、`:84`、`:95`（GPU 必需 / batch 256 / 200 epochs / input_option 默认 3x）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\dataset\bi_sequence_dataset.py:39-57`（npy 列 = 视图/命令/参数；1x/3x/4x 切片）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\model\model.py:15-20`、`:24-26`、`:41-45`（视图/命令/参数嵌入拼接）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\model\model.py:50-62`、`:84-85`（恒定查询解码器；掩码平均池化成一个 z）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\model\model.py:159-168`、`:181-211`（命令导向参数解码、总装）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\trainer\loss.py:23-33`、`:41-59`（两套掩码；容差软标签损失）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\trainer\trainer.py:14`、`:42-53`、`:83-100`（`.cuda()` / 掩码回填 / 分项准确率）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\test.py:19`、`:27-50`（必须给 ckpt；只存 out_vec/gt_vec）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\trainer\base.py:69-83`（ckpt 加载/保存）
- `D:\ai3d-survey\repos\lllssc__Drawing2CAD\requirements.txt`（torch 2.1.0 等）
- https://api.github.com/repos/lllssc/Drawing2CAD （stars/推送/语言，取数日 2026-10-24）

## 9. 未确认事项

- **未安装、未运行**：全部读码；Windows + 独立 venv 里能否装出 `torch==2.1.0`（CUDA 11.8）**未验证**。
- **没有预训练权重**：README 未提供、仓库也没有下载脚本（`README.md:78-86`）⇒ 论文分数的复现路径**查不到**。
- 数据集实际规模（多少模型、多少训练/测试样本）**查不到**：README 只给了下载链接，没给数量；我也没下数据。
- DeepCAD 的许可与表示细则本卡**未核对**（它是这套表示的上游）。
- `x-clip`（`requirements.txt`）在本仓里我没找到使用点，是否闲置**未确认**。
- `class=D`（序列/DSL）是按本仓 A–J 枚举的判读：输入是工程图、输出是命令序列；若 R7 改按"输入形态"优先，它会与 PlankAssembly / Img2CAD 一起落到 F（逆向）。★ 需 R7 统一裁决。
