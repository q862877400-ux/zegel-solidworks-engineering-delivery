# FlexCAD

<!-- survey: class=D; repr=sequence; orchestration=single; verify=numeric; deliver=sequence; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/microsoft/FlexCAD · 权重 https://huggingface.co/microsoft/FlexCAD · 论文 https://arxiv.org/abs/2411.05823 |
| 许可 | **MIT** —— 读仓库内 `LICENSE` 原文：`LICENSE:1` 为 `MIT License`、`LICENSE:3` 为 `Copyright (c) Microsoft Corporation.`（`gh api repos/microsoft/FlexCAD` 亦报 `license.spdx_id = MIT`）⇒ **可借鉴**（可商用，须保留版权声明） |
| 元数据 | stars **104** · forks 18 · open issues 2 · 语言 Python · **仓库已归档（archived: true，不再维护）** · 最近推送 **2025-05-28T07:49:48Z**（来源：`gh api repos/microsoft/FlexCAD`，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\microsoft__FlexCAD |
| 证据等级 | **读码**（读 README / LICENSE / `sample.py` / `finetune.py` / `utils/convert.py` / `utils/parser.py` / `utils/eval_cad.py` / `dataset.py` / 两份 yaml + `gh api`；**未**建 conda 环境、未训练、未跑推理） |

## 1. 一句话定位

它把 CAD 模型写成一串**结构化文本命令**（`circle/line/arc … <curve_end> … <loop_end> <face_end> <sketch_end> add,… <extrusion_end>`），再用**层级掩码（hierarchy-aware masking）**微调 LLaMA 3，让**一个模型**对 sketch-extrusion / extrusion / sketch / face / loop / curve 全部层级做「填空式」可控生成（`README.md:6-11`、`README.md:59`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**① 输入**：一个已有 CAD 序列 + 「用户想改哪一层」；改法就是**把那一层的文本片段替换成掩码 token**（`README.md:6-11`、`sample.py:18-148` 的 `infill_type`）。掩码类型共 8 个：`cad / es / extrusion / sketch / face / loop / curve / cla`（`finetune.py:85`），另有 `unconditional` 走纯生成（`sample.py:240-242`）。

**② 中间表示＝扁平文本命令序列**（不是 JSON、不是 AST、不是向量）：
- 曲线：` line,x,y`、` arc,…`、` circle,x1,y1,x2,y2,x3,y3,x4,y4`（`utils/convert.py:17-39`）；
- 层级用四个结束符表达：`<loop_end>` / `<face_end>` / `<sketch_end>` / `<extrusion_end>`（`utils/convert.py:52`、`:55`、`:58`、`:89`）⇒ **层级是符号，不是树结构**；
- 拉伸段固定 18 个整数：操作词 `add|cut|intersect` + 5 个 ext_v/ext_T + 9 个 ext_R + 3 个 scale/offset（`utils/convert.py:67-90`）；
- **所有数字在转换时减去 PAD 偏移**（`COORD_PAD=4`/`CMD_PAD=3`/`EXT_PAD=1`/`R_PAD=2`），使文本里全是从 0 起的整数（`utils/convert.py:11-15`、`:104-106`、`:80-87`）。

**③ 生成**：基座 LLaMA-3-8B 或 LLaMA-3-70B，也支持 LLaMA-2 系列（`finetune.py:423-447`）；LoRA `r=8 / alpha=32 / dropout=0.05`（`finetune.py:461-467`、`:529-531`）；8B 用 bfloat16 + `device_map="auto"`（`sample.py:157`）、70B 走 `load_in_8bit`（`finetune.py:434`）。训练时每样本随机抽一个掩码层级（`finetune.py:86`），12% 的样本退化成无条件生成（`finetune.py:43-46`）。

**④ 编排＝单模型单轮自回归**：无 agent、无工具调用、无迭代修复；`sample.py` 把生成片段**按 end_token 个数拼回原文**（`sample.py:285-340`）。

**⑤ 执行**：文本 → `utils/parser.py` 的 `CADparser` 解成 SketchUp 风格 obj 串（`utils/parser.py:25-51`）→ `utils/visual_obj.py` 用 pythonocc 建成 B-rep 并写 STL/STEP（`utils/visual_obj.py:7-11`、`:11`）→ `utils/cad_img.py` 用 `OCC.Display.OCCViewer.Viewer3d` 渲染成图（`utils/cad_img.py:1-20`）。

**⑥ 验证＝点云数值指标**：均匀采样 2000 点（`README.md:80`、`utils/eval_cad.py:16`），算 `MMD-CD` / `COV-CD` / `JSD`（`utils/eval_cad.py:85-97`、`:100-109`）。

**⑦ 交付**：一行一条的 json（字段 `prompt / output / original`，`sample.py:359-364`），**产物仍是字符串序列**；STL/STEP 只是可视化链路的副产物（`utils/visual_obj.py:11`）。

**★ 学术项补全**：中间表示＝**扁平层级文本**（见 ②）；基座＝LLaMA-3-8B / 70B（`finetune.py:424`、`:431`）；训练数据＝**SkexGen 发布的处理后 pkl**（`README.md:26-33`），具体条数 **查不到**（README 与代码都不打印样本数）；评测指标＝MMD-CD / COV-CD / JSD + 2000 点（`utils/eval_cad.py:16`、`:94-109`）。

## 3. 技术方案要点（可迁移的机制）

| 机制 | 说明（只讲机制，不抄代码） | 证据 |
|---|---|---|
| **结束符＝层级** | 五个 `<*_end>` 符号同时充当分隔符与掩码边界，于是一维字符串就能承载 6 层层级，无需自造 AST | `utils/convert.py:38`、`:52-59`、`:89` |
| **掩码粒度由原文片段决定** | face 掩码会按该 face 里 `face_end` 的个数复制多个 `[face mask]`；loop/curve 同理，**掩码个数不是常量** | `sample.py:59-62`、`:82-86`、`:113-116` |
| **反向重建掩码** | 生成后按生成串里 `face_end/loop_end/curve_end` 的计数重建多掩码，再替换回原文——变长片段插回定长模板的实用解法 | `sample.py:306-340` |
| **数字去偏移整数化** | 减 PAD 偏移后文本里只有小整数，规避小数与科学计数法对 tokenizer 的伤害 | `utils/convert.py:11-15`、`:104-106` |
| **少样本固定示例** | `--use_fixed_demo` 时提示里塞一个完整的四直线矩形示范，把「该生成几个 curve」也交给用户指定 | `sample.py:246-248`、`:333-340` |
| **LoRA 而非全参微调** | 8B/70B 都只训 adaptor，换层级不需要换模型 | `finetune.py:461-469` |
| **统一模型多任务** | 8 种掩码类型共享一套权重，靠提示句模板区分任务（`Below is a partial description …`） | `finetune.py:84-243`、`sample.py:32-42` |

## 4. 运行条件与依赖

- **环境**（`environments.yaml`，conda 环境名 `cadllm`）：`python=3.9.18`（`environments.yaml:7`）、`pythonocc-core=7.7.2`（`environments.yaml:8`）、`torch==2.2.1`（`:57`）、`transformers==4.38.2`（`:61`）、`deepspeed==0.13.0`（`:18`）、`accelerate==0.28.0`（`:10`）、`peft==0.9.0`（`:35`）。训练按多卡起（`README.md:44`），`ds_config.yaml:10` 默认 `num_processes: 4`。
- **显存**：README **没有给明称值（查不到）**。按代码推断：8B 训练/推理分别用 bf16 与 LoRA（`sample.py:157`、`finetune.py:461-467`），70B 走 8bit（`finetune.py:434`）；8B 权重 bf16 约需 16 GB（**来源＝算术估计**：`finetune.py:424` 的 8B 参数量 × `sample.py:157` 的 bf16 两字节，不是 README 声明值）。
- **本机（Windows / Python 3.14.7 / RTX 4080S 16GB）能不能跑**：**不能直接跑**。理由三条：① 环境 pin 死 `python=3.9.18` + conda-only 的 `pythonocc-core=7.7.2`（`environments.yaml:7-8`），本机 3.14.7 与 pip 都装不了；② 16 GB 显存跑 8B bf16 属临界（本机配置 16GB 非仓库声明；依据同 §4 上一条的算术估计：`finetune.py:424` 8B × `sample.py:157` bf16），大概率需量化；③ README 自述可视化最后的渲染步「目前只在 Windows 上成功」（`README.md:75`）——与本机平台相反地**有利**，但该步依赖 OCC 的 GUI viewer（`utils/cad_img.py:15-20`），无桌面会话时仍会挂。
- **未实测**：本卡没有建环境、没有下载权重、没有跑任何 `finetune.py` / `sample.py`（纪律：不装包、不跑训练）。

## 5. 失败模式与已知坑

| # | 坑 | 来源 |
|---|---|---|
| 1 | **序列合法性没有门禁**：生成结果只做 `split(delimiter)` 与字符串替换就写盘，非法串要到 `CADparser` 才变成 `None`，而 `None` 在链路里没有报错出口 | `sample.py:287-305`、`utils/parser.py:35-45` |
| 2 | **掩码抽取可能死循环**：`while i % 2 != 0: i = random.choice(range(lists_len))`——若 `lists_len` 里没有任何满足奇偶要求的下标，就永远出不来（空序列/只有一段时风险最高） | `sample.py:25-26`、`:135-136`、`finetune.py:95-96` |
| 3 | **两份 `CADDataset`、两套 `MAX_LENGTH`**：`dataset.py:9` 写 2048，而训练真正走的是 `finetune.py:18` 的 **512**，且 tokenizer 一律 `truncation=True` ⇒ 长序列被**静默截断** | `dataset.py:9`、`finetune.py:18`、`:52-54` |
| 4 | 生成上限也是 512 token（`max_new_tokens=MAX_LENGTH`），提示本身已经很长的场景下可用预算更少 | `sample.py:8`、`:275` |
| 5 | **评测链路缺三个依赖**：`plyfile`、`scikit-learn`、`chamfer_distance` 都被 import，但 `environments.yaml` 里一个都没有（grep 命中 0） | `utils/eval_cad.py:10-14`、`environments.yaml` 全文 |
| 6 | 可视化要手动加 `timeout 180` 防 OCC 挂死——说明作者自己遇到过挂死 | `README.md:71-73` |
| 7 | 输出目录取的是**模型权重所在目录**（`os.path.dirname(args.model_path)`），换个权重路径结果就到处落 | `sample.py:359`、`:362` |
| 8 | 仓库已归档（archived），不会再修；README 说的「每个 epoch 换一个掩码层级」与实现「每个样本随机抽」不一致 | `gh api` 元数据、`finetune.py:86` |
| 9 | 论文自述的局限我**未读原文 PDF**，故此处不转述（查不到） | — |

## 6. 对我方目标的可用处（机制层面）

我方目标：让**普通模型**也能建出**能用、规范**的模型。

1. **「结构化文本＝可审阅的中间表示」**：它证明一维文本加层级结束符就能表达 6 层层级，人眼可读、字符串可 diff、可局部替换。我方可以让普通模型只产出**同构的建模计划文本**（一步一特征），而不是整段 COM 调用序列——审阅与回改的成本从「读代码」降到「读一行」。
2. **「掩码＝局部重写」这条范式最适合普通模型**：不让它一次写对整个模型，而是「原文 + 一个洞」，只重写洞里那一段。错误被限制在同一层里，且可以逐层迭代修——这正是「普通模型也能做出规范模型」的杠杆点。
3. **变长片段回填的计数技巧**：用生成串里结束符个数决定掩码个数（`sample.py:306-340`），是「定长模板 + 变长内容」接得上的关键一步，我方的特征脚本模板可以照这个思路做。
4. **数字去偏移整数化**：把浮点几何量变成小整数文本，显著降低普通模型写错数字的概率（`utils/convert.py:104-106`）。
5. **反面教材（同样是收获）**：它**只到「字符串」为止**——没有语法校验、没有几何门禁、没有「建不出来就报错」的出口（见 §5 第 1 条）。我方交付前必须有「解析 + 几何/数值门禁」，把它的缺失补成我方的默认项。（来源：本卡 §5 第 1 条）
6. 不适合照搬的：它在 DeepCAD/SkexGen 的 sketch–extrude 子空间里做，没有倒角/圆角/孔/阵列这些工程特征；SolidWorks 的价值恰在特征树与约束，故它的「文本序列」只能借形态，不能借语义。

## 7. 许可与红线

**MIT**（`LICENSE:1` `MIT License`；`LICENSE:3` `Copyright (c) Microsoft Corporation.`；`gh api` 报 `license.spdx_id = MIT`）：**可读、可改、可商用**，义务是保留版权声明与许可文本。仓库已归档（archived），无 CLA 之外的额外约束（`README.md:106-118` 只讲贡献流程与行为准则）。待核：① Hugging Face 上 `microsoft/FlexCAD` 权重的使用条款**未核（查不到）**，权重未必自动继承仓库 MIT；② 数据来自 SkexGen（`README.md:26-29`、`:102`），SkexGen 自身的许可与数据再分发条款**本仓库内没有（查不到）**。⇒ 引用其**机制与文本形态**无碍；**若要把权重或数据搬进我方交付物，必须先核这两项**。

## 8. 证据清单

| 证据 | 出处 |
|---|---|
| 许可原文 | `LICENSE:1`、`LICENSE:3`（全文 21 行） |（来源：本卡 §7 许可）
| 定位与掩码语义 | `README.md:6-13`、`README.md:59` |
| 数据来源与转换命令 | `README.md:26-38`、`utils/convert.py:93-114` |
| 训练入口与多卡 | `README.md:41-55`、`ds_config.yaml:3`、`:8`、`:10` |
| 中间表示（曲线/层级/拉伸 18 字段） | `utils/convert.py:17-90` |
| 掩码构造与回填 | `sample.py:18-148`、`sample.py:285-340` |
| 掩码类型枚举 | `finetune.py:85`、`sample.py:18-148` |
| 基座与 LoRA 超参 | `finetune.py:423-467`、`finetune.py:529-531` |
| 两套 MAX_LENGTH | `dataset.py:9`、`finetune.py:18` |
| 解析器与 None 出口 | `utils/parser.py:25-51` |
| OCC 建模与 STEP/STL | `utils/visual_obj.py:7-11`、`utils/cad_img.py:1-20` |
| 评测指标 | `utils/eval_cad.py:16`、`:85-97`、`:100-109` |
| 环境 pin | `environments.yaml:7-8`、`:10`、`:18`、`:35`、`:57`、`:61` |
| 平台限制自述 | `README.md:71-75` |
| 仓库元数据 | `gh api repos/microsoft/FlexCAD`（2026-10-24 取数） |
| 论文摘要（层级列表） | https://arxiv.org/abs/2411.05823 |
| 权重发布页 | https://huggingface.co/microsoft/FlexCAD |

## 9. 未确认事项

1. **未实测**：没建 conda 环境、没下载权重、没跑过任何 `finetune.py` / `sample.py` ⇒ 生成质量、解析成功率、可视化链路全是读码结论。
2. **训练数据规模查不到**：README 只说下载 SkexGen 处理后的 pkl（`README.md:26-29`），没写 train/val/test 各多少条；代码只 `print("Data loaded: " + str(len(data)))` 在运行时才知道（`utils/convert.py:96`）。
3. **论文里的指标数值未取**（未读 PDF），本卡只记录指标**种类**与采样点数。
4. **Hugging Face 权重条款未核**，见 §7。
5. **「每个 epoch 换掩码层级」到底是 README 这么写、还是实现如此**：实现是每样本随机（`finetune.py:86`），我没有找到按 epoch 轮换的代码，故记为实现与 README 表述不一致。
6. **tag 行 `deliver=sequence` 不在给定枚举内**（枚举是 STEP/mesh/drawing/gcode/none）：按任务模板逐字保留，此处标注以免下游误读——它的真实交付物是「json 里的字符串序列」，STL/STEP 只是可视化副产物。
