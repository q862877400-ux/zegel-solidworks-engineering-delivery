# CAD-Coder（`anniedoris/CAD-Coder`）

<!-- survey: class=F; repr=code; orchestration=single; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/anniedoris/CAD-Coder ｜ 论文 https://arxiv.org/abs/2505.14646 ｜ 权重 https://huggingface.co/CADCODER/CAD-Coder ｜ 数据集 https://github.com/anniedoris/GenCAD-Code |
| 许可 | **Apache-2.0**（`LICENSE:1-3`，「Apache License Version 2.0」）⇒ **可借鉴**。★ 但 `LICENSE:189` 的版权行仍是**未填模板**「Copyright [yyyy] [name of copyright owner]」——权利人没写进 LICENSE；实际版权线索只有 README 自述「fork of the LLaVA repo」（`README.md:167`）与 `llava/` 下文件保留的「Copyright 2023 Haotian Liu」头（`llava/model/builder.py:1`、`llava/model/llava_arch.py:1`）|
| 元数据 | 211 stars · 最近推送 2025-07-17T17:51:08Z · 主语言 Python（来源：`gh api repos/anniedoris/CAD-Coder`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\anniedoris__CAD-Coder |
| 证据等级 | **读码**（通读 `scripts/*.py`、`SolidAlign/*`、`scripts/v1_5/*.sh`、`pyproject.toml`、`cog.yaml`、`predict.py`、`README.md`；`llava/` 为上游 fork，只抽查不逐读；**未安装、未推理、未训练**）|

## 1. 一句话定位

**图 → CadQuery 代码**的视觉语言模型：拿 LLaVA-1.5 那套「视觉塔 + 投影器 + Vicuna」直接微调，输入一张渲染图，输出一段能被 `subprocess` 跑通、并导出 STEP 的建模脚本（`README.md:6`）。它对本项目最值钱的不是模型，而是**「判活三级 + 惯性轴对齐 IoU」这套验收工程**（`scripts/generate_model_cad.py:25-48`、`SolidAlign/_cq.py:25-52`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      单张渲染图（官方测试是 GenCAD-Code 的 100 样本子集）
                                        `README.md:54`、`inference/cadquery_test_data_subset100.jsonl:1`
             ↓
中间表示  LLaVA-1.5 多模态：CLIP ViT-L/14-336 视觉塔 → mlp2x_gelu 投影器
          → 在图占位位（`<image>`）替换成视觉特征，与文本 token 同序列
                    `scripts/v1_5/phase1_cadcoder.sh:11-12`、`llava/constants.py:8-9`
             ↓
生成      vicuna-13b-v1.5 自回归解码；temperature=0（贪心）、num_beams=1、
          max_new_tokens=3450                      `scripts/v1_5/phase2_cadcoder.sh:8`、
                                                   `scripts/v1_5/eval/test_gencadcode.sh:27-29`
             ↓
编排      single —— 一次前向出一段脚本；无重试、无工具调用、无多智能体
                                                   `scripts/v1_5/eval/test_gencadcode.sh:19-30`
             ↓
执行      ① 剥掉 Markdown 代码围栏 → ② 单独 python 子进程跑一遍判「能不能运行」
          → ③ 追加导出语句再整体重跑 → ④ 等文件出现（上限两秒）
                                        `scripts/generate_model_cad.py:25-48`、
                                        `scripts/utils_generate_model.py:38-49`
             ↓
验证      numeric —— 先用主惯性轴把预测与真值对齐（枚举 4 种轴排列取最优），
          再用 BRep 布尔求交/并算体积 IoU        `SolidAlign/_cq.py:25-52`、
                                                 `scripts/compute_iou.py:91-109`
             ↓
交付      STEP + STL —— 两句固定的 `cq.exporters.export(solid, …)` 追加在模型输出后面
                                                 `scripts/generate_model_cad.py:41-42`
```

★ **学术类必填三项**

- **模型基座与参数量**：**vicuna-13b-v1.5**（`scripts/v1_5/phase1_cadcoder.sh:7`、`phase2_cadcoder.sh:8`）+ **CLIP ViT-L/14-336** 视觉塔（`phase1_cadcoder.sh:11`）+ `mlp2x_gelu` 投影器（`phase1_cadcoder.sh:12`）⇒ **13B 量级**，架构整体是 LLaVA-1.5（`README.md:167` 自述 fork）。★ 仓库**没有**在任何地方写「13B」这个数字，是从训练脚本与 `predict.py` 的 `llava-v1.5-13b`（`predict.py:28`）推出来的——见 §9。
- **训练数据从哪来与规模**：两段。① phase1 用 **LLaVA-1.5 的预训练集**（`README.md:92` 原文「the same dataset that is used by LLaVA 1.5」）；② phase2 用 **GenCAD-Code** 的 `cadquery_train_data_4096.json`（`scripts/v1_5/phase2_cadcoder.sh:10`），规模 **163k** 图文对（`README.md:9`）。落地数据要 **~30GB** 空间（`README.md:87`）。
- **推理是否需要采样多候选择优**：**不需要（也不做）**。评测脚本 `temperature 0`、`num_beams 1`（`scripts/v1_5/eval/test_gencadcode.sh:27-29`）⇒ 贪心单候选。它对「多解」的处理是给**点云**重采样 3 次（`--pc_reps 3`，`README.md:64`；实现见 `scripts/generate_model_cad.py:52-54`），不是给代码采样——这点很关键（见 §6.6）。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **判活三级** | ① 剥围栏；② 子进程跑一遍（只看退出码）；③ 追加导出语句后再跑一遍；④ 查文件是否真的出现 | `scripts/generate_model_cad.py:25-48` |
| 2 | **变量名契约 + 导出外挂** | 约定最终实体必须叫 `solid`；落盘语句由框架追加而不是模型写 ⇒ 模型只守一个命名约定，判活只看文件 | `scripts/generate_model_cad.py:41-46` |
| 3 | **围栏剥离** | 用正则去掉 Markdown 代码围栏（含语言标注那行），避免因包装而判失败 | `scripts/generate_model_cad.py:25-26` |
| 4 | **惯性轴对齐** | 平移到质心 → 用惯性张量特征值归一化尺度 → 枚举 4 种主惯性轴排列，取 IoU 最高的那个变换 | `SolidAlign/_cq.py:7-52` |
| 5 | **BRep 布尔而非网格近似** | 对齐后用 CadQuery 的 `intersect` / `fuse` 求体积，不用网格采样估计 | `SolidAlign/_cq.py:43-46` |
| 6 | **多解性量化** | 同一个 STL 用不同随机种子重采 3 次点云，把「同一形状多种采样」当独立样本统计 | `scripts/generate_model_cad.py:52-54`、`scripts/utils_generate_model.py:62-67` |
| 7 | **只训适配层再全量微调** | phase1 只开投影器（`--tune_mm_mlp_adapter True`），phase2 再带 `--pretrain_mm_mlp_adapter` 全量训 | `scripts/v1_5/phase1_cadcoder.sh:13`、`phase2_cadcoder.sh:13` |
| 8 | **按模型名路由加载器** | fork 改的判断是「模型名含 `llava` **或含 `cad`**」才走 LLaVA 加载分支 ⇒ 自定义命名必须带这两个词之一 | `llava/model/builder.py:48, 146` |
| 9 | **程序→网格→点云的闭环** | 训练/评测两侧共用同一套「执行脚本 → 导出 → 采样点云」工具，保证口径一致 | `scripts/utils_generate_model.py:38-67` |

## 4. 运行条件与依赖

- **官方环境是两套，必须分开，而且版本口径还不一致**：`llava` 环境（Python 3.10，`README.md:24`）与 `cad_iou` 环境（装 CadQuery）依赖冲突，README 要求保持分离（`README.md:51`）；`pyproject.toml:16-17` 钉 `torch==2.1.2` / `transformers==4.37.2`，`cog.yaml:7, 10` 却写 `python_version: "3.11"` / `torch==2.0.1` ⇒ 两条安装路径不同版本，别混用。
- **flash-attn 是手工活**：作者自述 `pip install flash-attn` 装不上，改用手工下载的 `cp310 + cu12torch2.1 + linux_x86_64` 轮子（`README.md:38`）⇒ **Linux + Python 3.10 硬绑定**。
- **显存**：README **没给推理显存数字** ⇒ **查不到**。训练是 4×H100（`README.md:106, 131`）。
- **本机（Windows / Python 3.14.7 / RTX 4080S 16GB，来源：本机配置）能不能跑**：**不能**。
  1. flash-attn 的可用形态是 Linux-only、py3.10-only 的预编译轮子（`README.md:38`）；
  2. 语言塔是 13B，fp16 权重规模已超出本机 16GB 显存（**按参数量推算，非实测**，规模来源见 `scripts/v1_5/phase2_cadcoder.sh:8`）；
  3. 项目 Python 是 3.10 / 3.11（`README.md:24`、`cog.yaml:7`），本机 3.14.7 对 `torch==2.1.2`（`pyproject.toml:16`）没有轮子；
  4. 量化路径**代码里有但没启用**：`llava/model/builder.py:34-41` 支持 4bit，而 `predict.py:85` 传的是 `load_4bit=False`。
  - 结论：**只读思想**。真要跑得换 Linux + 3.10 + 量化位。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **同一指标两套实现且方向相反**：`_cq.py` 取 **最大** IoU（`best_IOU=0` + `>`），`_OCC.py` 取 **最小**（`best_IOU=inf` + `<`）⇒ OCC 那版对齐挑选逻辑是反的；且 `scripts/compute_iou.py` 又自带一份 `cq_align_shapes`、不 import `SolidAlign`（两份会各自漂移）；`SolidAlign` 包 `__init__` 顶层就 import `_OCC`，没装 pythonocc 连 import 都炸 | `SolidAlign/_cq.py:33,50` vs `_OCC.py:77,96`；`scripts/compute_iou.py:10-64`；`SolidAlign/__init__.py:1` |
| 2 | **只判退出码 + 只等两秒**：子进程返回码为 0 即算「代码有效」，不检查几何是否非空；导出后等文件超时（2 秒）即判无效 ⇒ 慢机器/大模型会被误判 | `scripts/utils_generate_model.py:38-49`、`scripts/generate_model_cad.py:12-19, 47-48` |
| 3 | **pythonocc 分支是空的**：直接 `raise ValueError("Implement STEP generation")` ⇒ 实际只支持 CadQuery | `scripts/generate_model_cad.py:37-39` |
| 4 | **`predict.py` 不是 CAD-Coder 的推理入口**：它加载 `liuhaotian/llava-v1.5-13b`（`predict.py:85`）、用 `llava_v1` 模板（`predict.py:97`），而训练与评测用的是 `vicuna_v1`（`scripts/v1_5/eval/test_gencadcode.sh:29`）⇒ fork 残留，拿它跑会得到与论文不同的格式 | `predict.py:28-52, 85, 97` |
| 5 | README 自陈的未完成项：两套环境依赖冲突待解（`README.md:51`）、推理未收敛成一条命令（`README.md:150`）、无聊天能力（`README.md:151`）|
| 6 | 评测集只有 100 样本（`README.md:54`）⇒ 统计噪声大，别当权威分数 | `README.md:54` |

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的模型（SolidWorks 自动化）。

1. **判活三级是「把验证责任转移出去」的完整样板**（`scripts/generate_model_cad.py:25-48`）：能跑 → 能导出 → 文件真的在。我们收 SW 产物时可以照抄这个递进，而不是让模型自述「建好了」。
2. **★ 惯性轴对齐才是这套仓库最值钱的零件**（`SolidAlign/_cq.py:7-52`）：先按质心 + 惯性张量特征值归一化，再枚举主轴的 4 种排列取最优。⇒ 我们比「建出来的实体 vs 规范件」时，**位姿与尺度差异可以被消掉再比体积**，这才让 IoU 变成可比数。★ 而且它用 **BRep 布尔**（`intersect`/`fuse` 求体积，`SolidAlign/_cq.py:43-46`）而不是网格近似——cad-recode / cadrille 都是网格级 IoU，这一条能把我们的验收等级上限抬高一级。
3. **变量名契约 `solid` + 导出外挂**（`scripts/generate_model_cad.py:41-42`）：模型只守一个命名约定，交付与判活全在框架侧。我们的 SW 侧同理——约定最终实体/特征的命名，导出与读回都由脚本做。
4. **先只训适配层**（`scripts/v1_5/phase1_cadcoder.sh:13`）：普通模型接新模态/新领域时，最省成本的路径是先冻结主干只训投影器，再全量。我们的 16GB 机器能承受的正是这一段。
5. **它对「多解」的处理方式值得抄**：不采样代码（temperature=0），而是重采样**输入**点云 3 次（`scripts/generate_model_cad.py:52-54`）来量化多解性 ⇒ 想评估稳健性时，噪声加在输入上比采样输出更可控。★ 与 cadrille 的「多候选择优」形成对照：**两者都把数字抬高了，一个抬在输入侧、一个抬在输出侧**，我们的验收必须两边都钉死。

## 7. 许可与红线

- **Apache-2.0**（`LICENSE:1-3`）⇒ **可借鉴**：读、抄、改、商用均可。
- **义务**：① 保留版权声明；② 带 NOTICE；③ 声明改动了哪些文件。
- ★ **两处必须如实说明的瑕疵**（不构成许可失效，但影响引用时的严谨性）：
  1. `LICENSE:189` 的版权行**没填**，仍是 Apache 模板「Copyright [yyyy] [name of copyright owner]」⇒ 权利人只在 README/上游头里能查到（`README.md:167`、`llava/model/builder.py:1`）；
  2. 本仓是 **LLaVA 的 fork**（`README.md:167`），`llava/` 下的文件带着「Copyright 2023 Haotian Liu」+ Apache-2.0 头（`llava/model/llava_arch.py:1`）⇒ 分发时**两份版权都要保**，别只保 CAD-Coder 那一份。
- 模型权重托管在 HF（`https://huggingface.co/CADCODER/CAD-Coder`），**权重自身的许可未在本仓库声明** ⇒ 商用前须另行核实（本卡未核，见 §9）。
- 训练数据 GenCAD-Code 在另一个仓库（`https://github.com/anniedoris/GenCAD-Code`），**其许可本卡未核**。

## 8. 证据清单

| 证据 | 位置 |
|---|---|
| 定位（图 → CadQuery）| `README.md:6` |
| 数据集 163k 图文对 | `README.md:9` |
| 100 样本子集 | `README.md:54`、`inference/cadquery_test_data_subset100.jsonl:1` |
| 两套环境 + 依赖冲突 | `README.md:51`、`README.md:24` |
| flash-attn 手工轮子（Linux/py3.10）| `README.md:38` |
| 训练成本与数据体积 | `README.md:87, 106, 131` |
| phase1 只训投影器 | `scripts/v1_5/phase1_cadcoder.sh:7-13` |
| phase2 全量 + 数据文件 | `scripts/v1_5/phase2_cadcoder.sh:8-13` |
| 推理参数（贪心、3450）| `scripts/v1_5/eval/test_gencadcode.sh:27-29` |
| 判活三级与变量契约 | `scripts/generate_model_cad.py:12-48`；只判退出码见 `scripts/utils_generate_model.py:38-49` |
| 惯性轴对齐（`_cq` 取最大 / `_OCC` 取最小 / 另有一份副本）| `SolidAlign/_cq.py:7-52`、`SolidAlign/_OCC.py:77, 96`、`scripts/compute_iou.py:10-64` |
| IoU 汇总与「None 计数」| `scripts/compute_iou.py:74-117` |
| 按名字路由加载器 | `llava/model/builder.py:48, 146` |
| 4bit 路径存在但未启用 | `llava/model/builder.py:34-41` vs `predict.py:85` |
| 版本口径不一致 | `pyproject.toml:16-17` vs `cog.yaml:7, 10` |
| 许可原文、未填版权行、fork 与上游头 | `LICENSE:1-3`、`LICENSE:189`、`README.md:167`、`llava/model/builder.py:1` |
| 元数据 | `gh api repos/anniedoris/CAD-Coder`，2026-10-24 |

## 9. 未确认事项

1. **权重实际参数量**——仓库全文未写「13B」；本卡按训练脚本的 `vicuna-13b-v1.5`（`scripts/v1_5/phase2_cadcoder.sh:8`）与 `predict.py` 的 `llava-v1.5-13b`（`predict.py:28`）推断 ⇒ **推断，未核 HF config**。
2. **163k 的 train/val/test 划分**、是否与 100 样本测试集重叠、该 100 样本是否代表整体——**查不到 / 未确认**（数据集在另一个仓库，本卡未读；`README.md:54` 只写「假设在这个子集上测」）。
3. **权重与 GenCAD-Code 数据集的许可**——**未核**，直接影响能否商用（§7）。
4. **推理显存实测值**——README 未给，**查不到**；§4 的「超出本机显存」是推算，非实测。
5. **`_OCC.py` 的 `<` 是否真是 bug 而非有意**——纯读码判断（`SolidAlign/_OCC.py:96`）；该函数只经 `SolidAlign/__init__.py:1` 暴露，官方评测脚本走的是 `compute_iou.py` 里那份 `_cq` 逻辑，所以**对论文数字无影响**，但作为可复用件是坑。
6. **star / 推送时间会变**——取数日 2026-10-24（`gh api`）。
