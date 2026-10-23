# Img2CAD

<!-- survey: class=F; repr=sequence; orchestration=single; verify=numeric; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/qq456cvb/Img2CAD · 项目页 https://qq456cvb.github.io/projects/img2cad · 论文 https://arxiv.org/abs/2408.01437 |
| 许可 | MIT（读克隆内 `LICENSE:1-3` 原文「MIT License」+「Copyright (c) 2024 Stanford University」；`gh api repos/qq456cvb/Img2CAD` 亦报 `spdx_id=MIT`）→ **可借鉴**（保留版权声明） |
| 元数据 | stars 39 · 最近推送 2026-10-05T13:15:50Z · 语言 Python（来源：https://api.github.com/repos/qq456cvb/Img2CAD ，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\qq456cvb__Img2CAD （HEAD `afe48af`，末次提交 2026-10-05T21:15:49+08:00；`git status --porcelain` 为空） |
| 证据等级 | 读码 |

## 1. 一句话定位

SIGGRAPH Asia 2025 的「**单张渲染图 → CAD 命令序列**」两段式方案：先让微调过的 Llama-3.2-11B-Vision 只出**离散结构**（哪些命令、什么顺序、带语义部件名），再让一个 transformer（TrAssembler）在结构已知的前提下**只回归连续参数**——把「图→CAD」条件分解成两个都更弱的子问题（`README.md:21-24`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

★ **输入形态**：**单视图渲染图**（`.png`，Blender 渲染产物）。不是线稿、不是三视图、不是矢量工程图、不是点云（`README.md:170-172`）。

★ **中间表示（两层，这是本卡的分类要点）**：

1. **文本层 —— 自定义命令语言**：`<SOL>` 开一个轮廓（profile），后跟 `L`/`A`/`R` 曲线命令；`<CUT>` 开一个切除块（必须插在基草图的命令之后、拉伸之前）；`E:` 开拉伸。提示词明写「不考虑曲线与拉伸的实际参数，只考虑它们的类型」（`LlamaFT/prompt.txt:5-10`）。
2. **向量层 —— DeepCAD 约定的定长向量**：6 个命令（Line/Arc/Circle/EOS/SOL/Ext）+ 参数槽（草图 5 + 平面 3 + 平移 4 + 拉伸 4，`cadlib/macro.py:17-22`），并由 `CMD_ARGS_MASK` 逐命令规定哪些参数位有效、其余补 `PAD_VAL`（`cadlib/macro.py:27-32`）。序列上限 `MAX_TOTAL_LEN = 100`、拉伸数上限 15、每草图 loop 上限 6、每 loop 曲线上限 15（`cadlib/macro.py:36-39`）。

- **生成**：① 结构 = Llama-3.2-11B-Vision-Instruct + LoRA 适配器（`r=16`、`target_modules=["q_proj","v_proj"]`、`lora_alpha=16`，`LlamaFT/finetune.py:171-176`），基础模型以 4-bit nf4 双量化 + bf16 计算加载（`LlamaFT/finetune.py:157`），推理同样 4-bit（`LlamaFT/infer.py:403-414`）且 `do_sample=False`（`LlamaFT/infer.py:518-523`）。② 参数 = **高斯混合流（GMFlow）条件扩散**，条件里含部件名的 CLIP 文本嵌入（`TrAssembler/model.py:16`、`TrAssembler/model.py:195`、`TrAssembler/dataset.py:485-490`）。
- **编排**：两段**串联、无回环**——`LlamaFT/infer.py` 出 h5，`TrAssembler/eval.py` 读 h5 算指标，中间没有"模型看自己结果再改"的循环（`README.md:223-260`）。**不是训练-free**：两段各有自己的权重（HF `qq456cvb/img2cad`，`README.md:119-131`）。
- **执行**：向量 → 网格靠 `utils/diffsdf.py` 的 `param2mesh_torch`/`param2sdf`（`TrAssembler/eval.py:29`、`TrAssembler/eval.py:202`）。
- **验证**：Chamfer Distance（双向最近点均值和，`TrAssembler/eval.py:95-116`）、OCC（**取「final.obj 是否存在」为 1/0**，`TrAssembler/eval.py:398-416`）、部件分割精度/mIoU（`README.md:311-319`）。**没有几何合法性闸门、没有导出回读**——这些是离线评测数字，不是运行期判据。
- **交付**：落盘 `.h5`（按部件名分 dataset，`*_bbox` 存部件包围盒，`README.md:218`）+ `.obj`（`TrAssembler/eval.py:347-348`、`TrAssembler/eval.py:399-402`）。**没有 STEP、没有特征树**——这是它与我方目标之间最大的一道缺口。

## 3. 技术方案要点（可迁移的机制）

- **把「不会」拆成「结构 + 数值」两个可分别负责的问题**：结构交给带语言先验的模型，数值交给受限回归。这是本卡最值得抄的一条（`README.md:21-24`）。
- **输出格式即校验格式**：命令集只有 6 个词，每个命令的参数槽由 `CMD_ARGS_MASK` 决定；无效应为 -1。结构合法性由表保证，不靠模型自觉（`cadlib/macro.py:27-32`）。
- **宽松解析器（把 LLM 输出当脏数据）**：去 markdown 代码块、按空行切块、`<SOL>` 粘连时拆行、剥掉 `//`/`#`/`;`/`--` 四种注释前缀，再做命令类型映射（`LlamaFT/infer.py:101-124`、`LlamaFT/infer.py:56-80`）。
- **解析失败不抛异常、只打日志**：`process_text_to_h5` 整段 try 包住，失败仅打印（`LlamaFT/infer.py:337-355`）⇒ 批量跑时"成功率"与"几何质量"是两件事，必须分别统计（`LlamaFT/infer.py:592-594` 就打印了这个成功率）。
- **语义作条件通道**：部件名先过 `extract_base_name`/去数字后缀，再用 CLIP 文本编码成嵌入当网络输入（`TrAssembler/dataset.py:483-490`）——自然语言标签不需要人工 schema 就能进模型。
- **分部件组织 + 包围盒**：h5 顶层键就是部件名，`*_bbox` 索引部件 3D 包围盒（`README.md:218`）——与我们「装配体里每个零件各自定位」同构。
- **对称性当推理期约束，不重训**：`symmetry_opt` 用"原 SDF 与反射 SDF 的绝对差"作损失，按 `rotational`/`reflection` 两类分别构造（`TrAssembler/eval.py:141-230`）。
- **命令导向的两阶段解码残余**：文本模型只出类型、数值模型条件在类型上——正好对应 SolidWorks 里"先定特征类型与次序，再定尺寸"。

## 4. 运行条件与依赖

- 官方条件：Python 3.8+、CUDA 显卡、16GB+ RAM（`README.md:76-80`）。
- 依赖钉得较死：`torch==2.5.1+cu118`（`requirements.txt:5`）、`torchvision==0.20.1+cu118`（`requirements.txt:6`）、`pytorch-lightning==2.5.1`（`requirements.txt:17`）、`transformers==4.46.1`（`requirements.txt:18`）。
- 三个"要 CUDA 工具链/要编译"的依赖：`torch-scatter==2.1.2`（`requirements.txt:26`）、`bitsandbytes==0.44.1`（`requirements.txt:36`）、`nvdiffrast` 直接走 git（`requirements.txt:49`）。
- **克隆不完整**：`GMFlow/` 是空目录，`.gitmodules:1-3` 指向 `https://github.com/qq456cvb/GMFlow.git`，需 `git submodule update --init --recursive` 才有 TrAssembler 的模型定义依赖（`TrAssembler/model.py:15-16`）。
- 本机判断（Windows / 默认 Python 3.14.7 / RTX 4080S 16GB）：**这次没装也没跑**（证据等级=读码）。默认解释器基本不可能直接 `pip install -r requirements.txt`——`torch==2.5.1` 没有 cp314 wheel（本卡未实测 wheel 清单）；即便另建 3.10/3.11 venv，上面三个编译型依赖还要额外的 VS 生成工具链，Windows 可行性**未验证**。
- 显存：README 只给 RAM 要求，没给显存明称值；11B 模型 4-bit 常驻 + TrAssembler 推理的实际占用**未实测**。

## 5. 失败模式与已知坑

- **类别域极窄**：只发布 chair / table / storagefurniture 三类的 checkpoint（`README.md:120-131`、`TrAssembler/config.yaml:4`）；换类别必须自己重训两段。
- **表示能力被硬编码上限卡死**：拉伸 ≤15、总长 ≤100、每草图 loop ≤6、每 loop 曲线 ≤15（`cadlib/macro.py:36-39`），零件稍复杂就被截断。
- **只有草图 + 拉伸**：命令表就 6 个词（`cadlib/macro.py:3`），没有倒角、圆角、孔、阵列、扫掠、放样，也没有装配约束；那个 `<CUT>` 只是二次轮廓切除（`LlamaFT/prompt.txt:7-8`）。
- **输入分布偏**：训练/评测图来自同一套 Blender 渲染（`README.md:170-172`），换成真实工程图、手绘或相机照片属域外，作者未声明泛化能力。
- **解析器失败吞掉整条样本**：`filter_lines`/`filter_blocks`/`parse_cmd_line` 是正则+字符串规则（`LlamaFT/infer.py:101-146`），输出里多一个噪声 token 就可能整块丢弃，而失败只打印。
- **评测口径与论文值未必等价**：仓库里的 `OCC` 实际是「final.obj 存在」而不是"CAD 序列可执行"（`TrAssembler/eval.py:398-416`）；引用论文数字时要标口径。
- **`README.md:319` 自述**部件分割的有效样本数会少于测试集（同一个 ShapeNet 模型可能对应多个 PartNet id），比分母时要小心。

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的 SolidWorks 模型。

1. **条件分解直接照搬**：普通模型只负责"建哪些特征、什么次序、依附于谁"，数值交给约束求解/几何计算——这正是把"能力不足"转成"分工"的最有效手段（`README.md:21-24`）。
2. **命令 DSL + 参数掩码**：定义一个 10~20 词的 SolidWorks 特征 DSL（拉伸/切除/旋转/圆角/孔/阵列），每词只允许自己的参数位，其余强制空——输出合法性由表结构保证（`cadlib/macro.py:27-32` 的形态）。
3. **鲁棒解析层是必需品而非附赠**：普通模型的格式漂移是常态，需要一层"去代码块 / 拆粘连 token / 容忍多种注释"的解析器，并把"解析成功率"与"几何质量"分开报（`LlamaFT/infer.py:101-146`、`LlamaFT/infer.py:592-594`）。
4. **语义标签当条件通道**：零件/特征的自然语言名可先编码成嵌入参与决策，省掉手工 schema（`TrAssembler/dataset.py:483-490`）。
5. **对称/共面/同心当推理期约束**：用几何量（如反射后 SDF 差）作测试期目标，不改模型也能提高"规范性"（`TrAssembler/eval.py:141-230`）。
6. **反面教材也值钱**：它交付的是命令序列 + obj，没有特征树、没有 STEP ⇒ 提示我方**中间表示必须保住特征语义**，否则事后再想导回 SolidWorks 特征树是不可能的。

## 7. 许可与红线

- 仓库顶层 MIT（`LICENSE:1-3`，「Copyright (c) 2024 Stanford University」）⇒ **可借鉴**：可读、可抄、可改、可商用，义务是保留版权与许可声明。
- 但它依赖的权重与数据另有约束：模型权重与数据集托管在 Hugging Face（`README.md:112-116`、`README.md:141-146`），**仓库 LICENSE 不自动覆盖权重/数据集的条款**——用前要各自看那张卡。
- 基础模型 `meta-llama/Llama-3.2-11B-Vision-Instruct` 走 Meta 自己的许可（门控模型，需申请/登录，`LlamaFT/infer.py:512-516` 用 `HF_TOKEN`）⇒ 它自身是**第三方条款**，与我们是否 MIT 无关。
- 上游致谢里的 DeepCAD / GMFlow 是各自许可（`README.md:343`），本仓未内联它们的代码副本（`GMFlow/` 是子模块引用，非 vendored 副本）。

## 8. 证据清单

- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\README.md:21-24`（条件分解的两个子问题）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\README.md:76-80`（Python 3.8+ / CUDA / 16GB+ RAM）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\README.md:119-131`（三类 × 三段 checkpoint 清单）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\README.md:170-172`（Blender 渲染图输入）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\README.md:218`（h5 键=部件名、`*_bbox`）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\README.md:311-319`（CD/OCC/分割指标与样本数说明）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\LICENSE:1-3`（MIT + Stanford 版权行）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\LlamaFT\prompt.txt:5-10`（命令语言定义 + 只出类型）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\LlamaFT\infer.py:101-146`（宽松解析器：切块/拆粘连/剥注释）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\LlamaFT\infer.py:337-355`（文本→h5，失败只打印）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\LlamaFT\infer.py:403-414`、`:518-523`、`:540`（4-bit 加载 / do_sample=False / 模型 id）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\LlamaFT\finetune.py:157`、`:171-176`（QLoRA 配置）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\cadlib\macro.py:3`、`:17-22`、`:27-32`、`:36-39`（命令表 / 参数槽 / 掩码 / 上限）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\TrAssembler\model.py:16`、`:195`（GMFlow 依赖与主模型）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\TrAssembler\dataset.py:483-490`（部件名 CLIP 嵌入）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\TrAssembler\eval.py:95-116`、`:141-230`、`:398-416`（CD / 对称优化 / OCC 口径）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\requirements.txt:5-6`、`:26`、`:36`、`:49`（钉版与编译型依赖）
- `D:\ai3d-survey\repos\qq456cvb__Img2CAD\.gitmodules:1-3`（GMFlow 子模块；`GMFlow/` 当前为空）
- https://api.github.com/repos/qq456cvb/Img2CAD （stars/推送/语言，取数日 2026-10-24）

## 9. 未确认事项

- **未安装、未运行**：全部结论来自读码；`pip install` 能否在本机 Windows 成功（尤其 `torch-scatter`/`bitsandbytes`/`nvdiffrast` 三个编译型依赖）**未验证**。
- **显存实测值未知**：`README.md:78-80` 只给 RAM（16GB+）不给显存；11B 4-bit + TrAssembler 在本机 16GB 卡上能否跑 **查不到明称值**。
- 论文正文的方法细节（GMFlow 的超参、训练数据量）本卡未读论文，只有仓库代码与 README 依据。
- HF 上权重/数据集的实际许可条款本卡未核对（仓库内没有它们的 LICENSE 副本）。
- `class=F` 归入「逆向」是我按本仓 A–J 枚举的判读（任务书亦如此定位）；若 R7 汇总改按"输出表示"优先分类，它与 PlankAssembly/Drawing2CAD 同属"序列生成"，归类会动。★ 这一点需 R7 统一裁决，不要各自拍板。
