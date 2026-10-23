# PlankAssembly

<!-- survey: class=D; repr=sequence; orchestration=single; verify=geometry-gate; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/manycore-research/PlankAssembly · 论文 https://arxiv.org/abs/2308.05744 · ICCV 2023 |
| 许可 | **AGPL-3.0**（读克隆内 `LICENSE:1-2`「GNU AFFERO GENERAL PUBLIC LICENSE / Version 3」；`gh api` 报 `spdx_id=AGPL-3.0`；每个源文件头写「Copyright (c) Manycore Tech Inc. and its affiliates. All Rights Reserved」，如 `plankassembly/models.py:1`）→ **只读思想**。例外：`third_party/` 两个文件自述 Apache-2.0（`README.md:160`，派生自 detectron2，`third_party/boxes.py:1-4`） |
| 元数据 | stars 110 · 最近推送 2025-05-14T07:36:14Z · 语言 Python（来源：https://api.github.com/repos/manycore-research/PlankAssembly ，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\manycore-research__PlankAssembly （HEAD `bd708a0`，末次提交 2024-11-19T04:26:04Z；`git status --porcelain` 为空） |
| 证据等级 | 读码 |

## 1. 一句话定位

「**三张正交视图的矢量线稿 → 板件装配形状程序**」：不预测网格、也不预测建模命令，而是预测**一串轴对齐箱体（每块 6 个自由度）+ 每个箱体依附于谁**，再用这些箱体拼出 3D——把"看图建模"变成"学一个形状程序语言"（ICCV 2023，`README.md:3`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

★ **输入形态**：**三视图矢量线稿**——前 / 上 / 侧三个固定正投影视角（视角定义就是三个 `gp_Ax2` 常量，`dataset/data_utils.py:21-25`），每条线抽出 4 个数字（包围盒的两个角点），另带**视图编号**与**线型**（0=可见、1=隐藏）。三种输入变体：① complete（含隐藏线）② visible（只可见边）③ sideface（把粗线渲染出的窄面当输入）——`README.md:38`，各自有渲染脚本 `dataset/render_complete_svg.py`、`dataset/render_visible_svg.py`、`dataset/render_noisy_svg.py`。★ 不是位图（位图走得走 `README.md:39` 说的 raster 分支），也**不含尺寸标注**。

★ **中间表示（这是本卡的分类要点）**：

1. **输入侧**：每条线的 4 个坐标先量化到 9 bit ⇒ 值词表 512 档（`plankassembly/datasets/data_utils.py:6-12`、`configs/train_complete.yaml:43`），每个 token 再叠四种离散嵌入——值 / 段内位置 / 坐标位（0..3）/ 视图（0..2）/ 线型（0..1），五种嵌入**相加**（`plankassembly/models.py:47-53`、`:103-112`）。输入总长 1200 个 token（`configs/train_complete.yaml:41`）。
2. **输出侧 = 形状程序**：一串 6 自由度箱体（xmin,ymin,zmin,xmax,ymax,zmax），每个箱体再带一个 **attach 指针**（依附到前面某块板，或依附到整体包围盒）。输出上限 128 个 token、每块 6 个 ⇒ **最多 21 个箱体**（`plankassembly/models.py:25-27`、`:258-265`，`configs/train_complete.yaml:37-42`）；其中第 0 个是整体包围盒、不当作独立板，所以**实际板数 ≤ 20**（`misc/mesh_utils.py:33`、`dataset/data_utils.py:55`、`evaluate.py:44` 三处一致地跳过它）。

- **生成**：标准 encoder–decoder Transformer（6+6 层、d_model 512、8 头，`configs/train_complete.yaml:56-64`），自回归解码。三个头拼成一个分布：**值头**（词表）+ **指针头**（用解码隐状态与已生成 token 做点积）+ **开关头**（sigmoid 决定这一步是"写新数值"还是"搬用前面某个 token"），拼接成一个长度 = 词表 + 序列长的分布（`plankassembly/models.py:140-188`）。
- **编排**：**单次自回归、无回环、无工具、无人工**；`eval_step` 里就是 `for _ in range(max_output_length)` 直到整批出现 END（`plankassembly/models.py:267-323`）。**训练依赖**（有三个预训练权重，`README.md:154-156`）。
- **执行**：坐标反量化回 [-1,1]（`plankassembly/datasets/data_utils.py:15-21`）→ 每 6 个数一组转成 `trimesh` 的 box 并拼成整网格（`misc/mesh_utils.py:29-37`）→ 导出 `.stl`（`misc/build_pred_mesh.py:27-30`）。
- **验证**：**几何闸门**——先踢掉零厚度的退化箱（`trainer_complete.py:79`、`:100`），再做「预测箱 × 真值箱」的 IoU 矩阵 + 匈牙利指派，IoU ≥ 0.5 才算一个真阳性，据此算 P/R/F1（`third_party/matcher.py:44-59`，阈值来自 `configs/train_complete.yaml:50`）。**注意：没有"这不合法"的判据**（箱体本身不需要合法性检查），也没有导出回读。
- **交付**：STL 网格 + HTML 可视化（`misc/build_html.py`、`README.md:134-148`）。**没有 STEP、没有特征树、没有尺寸/约束**——箱体拼装本身就是它的终点。

## 3. 技术方案要点（可迁移的机制）

- **输入预处理"四件套"（最值得抄的一条）**：先用 OCC 的 HLR 投影得到**可见边 + 隐藏边**两份边集（`dataset/data_utils.py:63-101`，`hlr_shapes.VCompound()` / `HCompound()`），再①按交点切分（`dataset/data_utils.py:113-146`）②按端点切分（`:149-176`）③去重叠线（`:179-205`）④量化（`plankassembly/datasets/data_utils.py:6-12`）。目的很明确：**把连续线稿变成有限词表里的最小单元**，让模型只需要判断"这段线在哪"。
- **结构信息编码进输入，而不是指望模型自己发现**：视图编号、段内位置、坐标位、线型各自一个嵌入相加（`plankassembly/models.py:47-53`）。这四样恰好是"这条线在哪个视图、是这条线第几段、是第几个坐标、可不可见"。
- **"缺失线 / 隐藏线"是一等公民**：`line_type` 只有两值；渲染时红色代表缺失线，解析时**直接跳过**（`dataset/prepare_info.py:22-32`），隐藏线用虚线画（`dataset/data_utils.py:219-221`）。⇒ 把"看不清"变成输入通道而不是噪声。
- **用指针（索引）表达依附关系，而不是用名字**：指针头 + 严格上三角掩码（只能指向已生成的 token）+ 首块只能指包围盒的专用掩码（`plankassembly/models.py:91-101`、`:156-166`）。★ 这一点对我方极关键：SolidWorks 的实体（边/面）**没有可用名字**（本仓已知事实 32），靠索引指代是唯一稳的路子。
- **一个分布同时表达"新值"与"复制已有值"**：词表分布 ×(1−p) 与指针分布 ×p 拼接（`plankassembly/models.py:165-186`）——尺寸要么新给、要么等于前面已有的某个尺寸，这个形态天然适配。
- **排列规范化消歧**：输入先按 (视图, x, y, …) 做 `lexsort`（`plankassembly/datasets/line_data.py:41-46`），同一张图只有一种 token 顺序 ⇒ 消除"同图不同序"的歧义。
- **退化输出在评测前剔除**：零厚度的箱直接不算（`trainer_complete.py:79`、`:100-103`）——输出后处理做合法性过滤，比改模型便宜。
- **判据是几何不是 token**：IoU≥0.5 的匈牙利匹配（`third_party/matcher.py:44-59`）⇒ 评估的是"这块板对不对得上"，不是"第 7 个 token 猜对没"。
- **噪声鲁棒性靠数据增强而非结构**：随机删线 / 两端各缩一点（`plankassembly/datasets/data_utils.py:24-68`），增强比例 0.1、噪声比例 0.15（`configs/train_complete.yaml:45-47`）。

## 4. 运行条件与依赖

- 官方条件（自述）：Python 3.8、PyTorch 1.10.0、CUDA 11.3、PyTorch Lightning 1.7.6（`README.md:44`）；`environment.yml` 是一份 **linux-64** 的 conda 显式导出（含 `cudatoolkit=11.3.1`，`environment.yml:13`）。
- 两处 Linux-only 的硬依赖：① `detectron2` 只给了手工 wheel URL，文件名就是 `cp38-cp38-linux_x86_64`（`README.md:69`）；② `pythonocc-core=7.6.2` 走 conda-forge（`README.md:70`）。
- 训练配置按 **4 卡**写（`configs/train_complete.yaml:21` `devices: 4`）、batch 16、1000 epochs（`configs/train_complete.yaml:22`、`:30`）；推理只需 1 卡（`README.md:120-124` 用 `--trainer.devices 1`）。
- 数据要自己造：先下 HF 数据集，再跑三个渲染脚本生成 SVG，再 `dataset/prepare_info.py` 打包成 info JSON（`README.md:76-103`）。
- 本机判断（Windows / 默认 Python 3.14.7 / RTX 4080S 16GB）：**不能按仓库给的方式跑**——`detectron2` 的 cp38-linux wheel 直接排除 Windows，`torch 1.10` 也没有 cp314 wheel（本卡未实测 wheel 清单）。本次**未安装、未运行**。
- 显存：README 没给显存明称值；权重规模只能从架构读（6+6 层、d_model 512，`configs/train_complete.yaml:56-64`），**实际占用未实测**。

## 5. 失败模式与已知坑

- **表示能力被"轴对齐箱体"锁死**：每块板由 bounds 生成，姿态矩阵恒为单位阵（`misc/mesh_utils.py:14-18`）⇒ **表达不了圆柱、斜面、曲面件**；回转体、铸件、钣金折弯都出不来。
- **板数上限 20 块**（21 个箱体 − 1 个整体包围盒；`plankassembly/models.py:25-27` 的 128 ÷ 6；`configs/train_complete.yaml:42`）⇒ 复杂柜体会被硬截断。
- **输入 token 上限**：默认 400（`plankassembly/models.py:26`），训练配置改成 1200（`configs/train_complete.yaml:41`）；线一多就截。
- **只认三种固定正投影**（`dataset/data_utils.py:21-25`）：斜视轴测图、剖视图、局部放大图都不认；线稿里没有尺寸数字、螺纹/公差/表面符号 ⇒ 尺寸只能靠相对比例猜。
- **贪心解码，一步错锁死**：`_sample` 里是 `torch.argmax`（`plankassembly/models.py:235-237`）⇒ 无采样、无回退、无重试。
- **噪声模型只模拟"删线 / 缩短线"**（`plankassembly/datasets/data_utils.py:24-54`），不模拟"线画错位置"或"多画一条线"。
- **数据是它自己的渲染管线生成的**（OCC HLR，`dataset/data_utils.py:63-101`）⇒ 输入分布与真实工程图（有粗细线型、剖面线、中心线）不同，作者未声明跨域能力。
- **评测只覆盖"箱体对不对得上"**，不检查生成的箱体集合是否能拼成一个连通实体（没有连通性/重叠/悬空的判据）。

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的 SolidWorks 模型。

1. **输入预处理器是独立可搬件**：投影 → 按交点切 → 按端点切 → 去重叠 → 量化，这段逻辑与模型无关（`dataset/data_utils.py:63-205`），可以直接用来把工程图/草图拆成"最小可判单元"，再交给普通模型判断。
2. **多通道离散编码**：把"属于哪个视图 / 第几段 / 第几个坐标 / 可不可见"拆成独立嵌入相加（`plankassembly/models.py:47-53`）——我方做"图→特征"时同理，把结构先验编码进输入比让模型学便宜得多。
3. **指针表示依附**：特征依附哪个面/边用**索引**表达（`plankassembly/models.py:91-101`）——正合 SolidWorks 里"实体没有可用名字"的现实（本仓已知事实 32）。
4. **混分布表达"新值 / 复用已有值"**：尺寸经常是"等于上面那个尺寸"或"等于某个标准值"，词表+指针拼接的形态可直接借（`plankassembly/models.py:165-186`）。
5. **验收判据用几何而非 token**：IoU≥0.5 的匹配比 token 准确率更贴近"能不能用"（`third_party/matcher.py:44-59`）——我方导出后的比对也应该是几何级。
6. **退化过滤放在导出前**：零厚度/零面积先剔除（`trainer_complete.py:100-103`），别让坏几何进 SolidWorks。
7. **排列规范化**：同一模型有多种 token 顺序时，先排序再编码（`plankassembly/datasets/line_data.py:41-46`），否则普通模型会把"顺序不同"当成"内容不同"。

## 7. 许可与红线

- 主仓 **AGPL-3.0**（`LICENSE:1-2`）⇒ **只读思想**，红线最重：AGPL 的网络分发条款会传染，**一行代码都不能进本仓**（本仓以 MIT 分发）。源文件头还逐个写「All Rights Reserved」（如 `plankassembly/models.py:1`），与 AGPL 并存，按最严的读。
- `third_party/boxes.py`、`third_party/matcher.py` 是 detectron2（Apache-2.0）的改作（`third_party/boxes.py:1-4`、`third_party/matcher.py:1-3`），`README.md:160` 声明它们走 Apache-2.0 ⇒ 若要用这两个文件，**去 detectron2 上游取**，不要从本仓取（本仓的副本已被 AGPL 仓库整体笼罩）。
- 数据集与权重另有条款：数据托管在 HF（`README.md:78`）、权重在 HF 与 CDN（`README.md:150-156`），仓库 LICENSE 不覆盖它们。
- 可写进文档的只有机制描述与我方自己的实现；**不得**复制它的渲染脚本、数据增强、模型代码。

## 8. 证据清单

- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\LICENSE:1-2`（AGPL-3.0 首两行）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\README.md:38`（三种输入变体）、`:39`（raster 分支）、`:44`（Python3.8/Torch1.10/CUDA11.3/PL1.7.6）、`:69-70`（detectron2 linux wheel / pythonocc）、`:154-156`（三个 checkpoint，文件名自带指标）、`:160`（许可与 third_party 例外）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\dataset\data_utils.py:21-25`（三个投影视角）、`:49-60`（bounds→box，跳过第 0 块）、`:63-101`（HLR 出可见/隐藏边）、`:113-205`（切分/去重叠）、`:219-221`（隐藏线画虚线）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\dataset\prepare_info.py:22-32`（红色缺失线跳过、虚线→type=1）、`:56-70`（coords/attach 落 info JSON）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\plankassembly\datasets\data_utils.py:6-21`（9 bit 量化/反量化）、`:24-68`（加噪）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\plankassembly\datasets\line_data.py:34-83`（输入序列：量化+lexsort+五通道）、`:85-109`（输出序列：值+attach 标签）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\plankassembly\models.py:47-53`（五种嵌入）、`:91-101`（指针掩码）、`:140-188`（值/指针/开关三头拼分布）、`:235-256`（argmax 采样）、`:258-265`（解析成箱体）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\configs\train_complete.yaml:21-22`、`:30`、`:37-43`、`:45-47`、`:50`、`:56-64`（4 卡 / epochs / 维度 / 增强 / IoU 阈值 / 模型规模）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\third_party\matcher.py:44-59`（IoU + 匈牙利 + P/R/F1）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\trainer_complete.py:79`、`:100-118`（退化过滤 + pred_jsons 落盘）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\misc\mesh_utils.py:14-37`（bounds→trimesh box，姿态恒为单位阵）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\misc\build_pred_mesh.py:27-30`（导出 stl）
- `D:\ai3d-survey\repos\manycore-research__PlankAssembly\evaluate.py:32-44`（pred/gt 都跳第 0 块）
- https://api.github.com/repos/manycore-research/PlankAssembly （stars/推送/语言/`license=AGPL-3.0`，取数日 2026-10-24）

## 9. 未确认事项

- **未安装、未运行**：全部结论读码得来；Windows 下是否能用 conda 装出 `pythonocc-core=7.6.2` + 绕过 detectron2 **未验证**。
- **品类范围**：README 没写"只做柜类/板式家具"这类明文限制；从"轴对齐箱体装配"这一表示推断适用面很窄，但**没有原文依据**，故不写成断言。
- `README.md:154-156` 三个 checkpoint 文件名里带的 precision/recall/f1 是**作者自述值**，本卡未复现，也未核对论文表格是否一致。
- **显存实测值未知**：只有架构参数，没有显存明称值。
- `sideface` 输入变体（`README.md:38`）的完整语义（是把窄色块当线，还是真的给面）本卡只读了 `plankassembly/datasets/sideface_data.py:22-38` 的解析段，未读论文对应章节。
- `class=D`（序列/DSL）是按本仓 A–J 枚举的判读：它的输出确实是一个"形状程序"，但输入是**图纸逆向**；若 R7 汇总改按"输入形态"优先分类，它会与 Img2CAD / Drawing2CAD 一起落到 F（逆向）。★ 需 R7 统一裁决。
