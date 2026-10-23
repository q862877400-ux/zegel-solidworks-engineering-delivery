# cadrille（`AIRI-Institute/cadrille`）

<!-- survey: class=F; repr=code; orchestration=single; verify=numeric; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/AIRI-Institute/cadrille ｜ 论文 https://arxiv.org/abs/2505.22914 ｜ 权重 https://huggingface.co/maksimko123/cadrille（SFT）与 `cadrille-rl`（RL）|
| 许可 | **Apache-2.0** —— `LICENSE:1-3` 原文「Apache License Version 2.0」；版权行 `LICENSE:189`「Copyright 2025 Autonomous non-profit organization "Artificial Intelligence Research Institute"」⇒ **可借鉴**（保留版权声明 + NOTICE 义务 + 声明改动过的文件）|
| 元数据 | 6 stars · 最近推送 2025-06-04T08:51:06Z · 语言未识别（`lang=null`，仓库以 .py + 图片为主）（来源：`gh api repos/AIRI-Institute/cadrille`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\AIRI-Institute__cadrille |
| 证据等级 | **读码**（逐个通读 `cadrille.py` / `dataset.py` / `train.py` / `test.py` / `evaluate.py` / `data/*` / `Dockerfile`，共 7 个源文件；**未安装、未训练、未推理**）|

## 1. 一句话定位

CAD-Recode 的**多模态升级版**：同一个 Qwen2-VL-2B 模型，输入可以是**点云 / 图像 / 文本**任意一种，输出仍是可执行的 CadQuery Python 代码（`README.md:9`）；相对 CAD-Recode 的关键差别是**把点云也做成了序列里的 token 位**，从而与 Qwen2-VL 原生的图像 token 走同一条通路，而不是两个塔。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      三种模态任选其一（默认随机 50/50 混点云与图像）
          · 点云：面采样 8192 → FPS 取 256 点；train/val 除以 100，test 做 (x-0.5)*2
          · 图像：四个固定视角各渲染一张，拼成 2×2 当「一帧视频」喂给 Qwen2-VL
          · 文本：Text2CAD 的自然语言描述
                                        `dataset.py:14-19, 99-102, 131-149, 164-167`
             ↓
中间表示  点云 → 51 维 Fourier → 单层 Linear(51, hidden) → 每点一个 token；
          文本侧在序列头拼 N 个 pad token 占位，前向时按注意力掩码反推起点、
          把这些位置整体覆写成点嵌入          `cadrille.py:75-79, 178-179, 264-270`
             ↓
生成      Qwen2-VL-2B-Instruct 自回归解码，max_new_tokens=768，
          单次贪心（全仓无 do_sample / num_beams / num_return_sequences）  `test.py:67`
             ↓
编排      single —— `test.py` 一批前向到底，无循环重试、无工具、无多智能体      `test.py:58-78`
             ↓
执行      evaluate 侧把生成的 .py 丢进**子进程** `exec`，取全局变量 `r`，
          `join(3)` 后若仍存活就 terminate（CadQuery 内存泄漏的兜底）  `evaluate.py:62-87`
             ↓
验证      numeric —— Chamfer（8192 点）+ 体积 IoU（网格级）+ IR（无效比例），
          并按文件取 min CD / max IoU 汇总            `evaluate.py:31-54, 152-177`
             ↓
交付      mesh —— 只落 STL；STEP 导出那一行被注释掉了          `evaluate.py:70-72`
```

★ **学术类必填三项**

- **模型基座与参数量**：`Qwen/Qwen2-VL-2B-Instruct`（`train.py:60-68` 同处加载 processor 与权重，bf16 + `flash_attention_2`）⇒ **2B 量级**，外加一个 51×hidden 的逐点线性（`cadrille.py:179`）。
- **训练数据从哪来与规模**：CAD-Recode v1.5 的 train/val（`train.py:25-36`，起点 `n_points=256`、`normalize_std_pc=100`）+ Text2CAD 训练集（`train.py:40-46`）；四个数据集清单与下载方式在 `data/README.md:5-8`。**每集样本条数仓库内未给** ⇒ 规模**查不到**。
- **推理是否需要采样多候选择优**：**默认不需要**——`test.py:50` 里 `n_samples = 1` 写死，生成不带采样参数（`test.py:59-67`）。★ 但 `evaluate.py` 的汇总**按多候选择优**（逐文件取 min CD / max IoU，`evaluate.py:152-166`），所以仓库里那套数字是「择优后」口径，不是单次成功率。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **一条序列装三种模态** | 点云占 N 个 pad token 位、图像走 Qwen2-VL 原生 video token（4 视角拼 2×2 当 1 帧）、文本走普通 token ⇒ 不新增视觉塔、不改注意力 | `cadrille.py:75-79`、`dataset.py:145-149` |
| 2 | **按掩码反推注入起点** | 起点 = 序列长度 − 掩码和（左 padding），不写死偏移量 ⇒ 抗 padding 长度变化 | `cadrille.py:267-270` |
| 3 | **只对 assistant 段算 loss** | 用 token id 151644/77091 找 `<|im_start|>assistant`、151645 找段尾，其余位置置 -100 | `cadrille.py:126-141, 112-120` |
| 4 | **一个 batch 混模态** | `is_pc` / `is_img` 布尔向量 + 空嵌入占位，video 张量按 `is_img` 重排成 batch 尺寸 | `cadrille.py:89-106` |
| 5 | **靠数据混合而不是多塔做多模态** | 训练时 50/50 随机丢掉一路输入，让单模型同时见过三种条件 | `dataset.py:99-102` |
| 6 | **逐点小 MLP** | 8 个频率 sin/cos（不乘 π）+ 原坐标 = 51 维 → 单层线性；参数量极小，单卡可训 | `cadrille.py:144-184` |
| 7 | **执行隔离 + 硬超时** | 生成的脚本在独立进程里跑，`join(3)` 超时就 terminate；Pool 改成非 daemon 以允许嵌套进程 | `evaluate.py:14-28, 77-87` |
| 8 | **IR（无效比例）作为一等指标** | 生成的脚本跑不出网格就计一次 IR，并额外报告「丢掉 i 个最差样本后」的均值 | `evaluate.py:153-177` |
| 9 | **交付留了一个空档** | STEP 导出代码在仓库里但被注释，实际只出 STL ⇒ 「能出代码」≠「能出 STEP」 | `evaluate.py:71-72` |

## 4. 运行条件与依赖

- **官方环境**：`pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel`（`Dockerfile:1`）；Open3D 源码 headless 编译（`Dockerfile:6-17`）；`pytorch3d` 与 `cadquery` 钉 commit（`Dockerfile:20-21`）；`flash-attn==2.7.2.post1`（`Dockerfile:31`）、`transformers==4.50.3`（`Dockerfile:57`）、`qwen-vl-utils==0.0.10`（`Dockerfile:60`）。
- **显存**：README **没给任何显存数字** ⇒ **查不到**。可推的只有训练配置：batch 15 × 梯度累积 2、bf16、flash-attn（`train.py:37-38, 67-68`）。
- **本机（Windows / Python 3.14.7 / RTX 4080S 16GB，来源：本机配置）能不能跑**：**不能按仓库给的方式跑**。
  1. 镜像是 Linux CUDA 基础镜像（`Dockerfile:1`）；
  2. `flash-attn` 要 nvcc 编译、Windows 无轮子（`Dockerfile:31`），而代码里 `attn_implementation='flash_attention_2'` 是写死的（`test.py:22`）；
  3. 本机 Python 3.14.7 对 `torch` 2.5.1 没有 cp314 轮子（`Dockerfile:1`）；
  4. 顺带一条：`Dockerfile:4` 把 `git-lfs` 写成了 **`git-lsf`**，这份镜像**连构建都过不去**——想跑得先自己改。
  - 结论：**只读思想**。2B 量级权重在 16GB 卡上放得下（**按参数量推算，未实测**，规模见 `train.py:66`），但依赖链先卡死。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **Dockerfile 拼写错**：`git-lsf`（应为 `git-lfs`）⇒ `apt-get install` 直接失败，镜像构建中断 | `Dockerfile:4` |
| 2 | **裸 `except: pass` 三处**：算 IoU 失败、`exec` 失败、读网格失败都被静默吞掉，只留下 None | `evaluate.py:53-54, 73-74, 109-110` |
| 3 | **训练/推理归一化口径不一致**：train/val 除以 100，test 走 `(x-0.5)*2` ⇒ 自己造数据时容易喂错分布 | `dataset.py:164-167` |
| 4 | **`test.py` 用了模块级 `args`**：`run()` 的形参叫 `py_path`，函数体却用 `args.py_path` ⇒ 只能当脚本跑，被 import 就 NameError | `test.py:14, 16, 87` |
| 5 | **3 秒超时会杀掉「慢但正确」的脚本**，与真·无效混在一起计入 IR | `evaluate.py:77-87` |
| 6 | **IoU 用网格体积近似**（非 BRep 精确布尔），非水密网格会静默变 None 再被算进 IR | `evaluate.py:39-54` |
| 7 | **交付口径缩水**：STEP 导出被注释，实际只有 STL | `evaluate.py:71-72` |
| 8 | **论文数字是择优后的**：IR 还按「丢掉 i 个最差样本」分档报告，直接拿去当单次成功率会高估 | `evaluate.py:171-177` |

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的模型（SolidWorks 自动化）。

1. **「条件 → token 位」比「条件 → prompt 文本」更抗稀释**：它的点云不是塞进自然语言，而是占住序列前 N 个位置（`cadrille.py:75-79`）。⇒ 我们的**尺寸表 / 约束清单 / DFM 规则**同样可以做成位，避免长 prompt 把关键数值稀释掉。
2. **按掩码反推注入位置**（`cadrille.py:267`）是个纯工程收益：左 padding、变长 batch 下都不会错位。我们若自建注入层，这条直接照用。
3. **一个 batch 混模态**（`cadrille.py:89-106`）对小显存机器（16GB）特别有用：同一批里混「读图任务」与「读几何任务」，不用拆两次训练。
4. **逐点小 MLP 的性价比**（`cadrille.py:178-179`）：51 维输入、一层线性，4080S 完全训得动 ⇒ 我们不必上大编码器。
5. **要抄的是它的评估口径，不是它的模型**：`min CD / max IoU + IR 分档`（`evaluate.py:152-177`）给了我们一套**可复核的验收公式**；同时它也是警告——**别用「生成 N 个挑最好的」当成功率**，我们的验收必须固定单次。
6. **执行隔离的写法可直接复用**：子进程 + `join(timeout)` + terminate（`evaluate.py:77-87`）与我们「COM 调用必须有超时、弹窗要护栏」同族，思路可平移。

## 7. 许可与红线

- **Apache-2.0**（`LICENSE:1-3`），**可借鉴**：可以读、抄、改、商用。
- **义务三条**：① 保留版权声明（`LICENSE:189`「Copyright 2025 Autonomous non-profit organization "Artificial Intelligence Research Institute"」）；② 带 NOTICE；③ 声明改动过哪些文件。
- ★ **跨许可风险（本卡重点提示）**：它的训练数据之一是 **CAD-Recode v1.5**（`train.py:25`、`data/README.md:8`），而 CAD-Recode 仓库自身是 **CC BY-NC 4.0 非商用**（见 `cad-recode.md` §7）。**数据集许可不在本仓库内声明** ⇒ 本卡的 Apache-2.0 只覆盖**代码**，**不覆盖权重与训练数据**。若要商用其权重，须自行核实数据许可（本卡未核，见 §9）。
- 代码内无 `Slacker-LLC` 类 NOTICE 依赖；但 `Dockerfile` 拉取的 Open3D / pytorch3d / cadquery 各有自身许可，**本卡未核**。

## 8. 证据清单

| 证据 | 位置 |
|---|---|
| 多模态定位（点云/图像/文本）| `README.md:9` |
| 三基准 SOTA 自述 + 论文 | `README.md:4-7`、`README.md:11` |
| 未提供 RL 微调代码 | `README.md:34` |
| 基座与 bf16/flash-attn | `train.py:60-68` |
| 训练数据来源与超参 | `train.py:25-46, 75` |
| 点云→token 位 | `cadrille.py:75-79` |
| 按掩码反推注入起点 | `cadrille.py:264-270` |
| 逐点 Fourier + 单层线性 | `cadrille.py:144-184` |
| 只对 assistant 段算 loss | `cadrille.py:108-141` |
| batch 混模态 | `cadrille.py:89-106` |
| 采样 / 归一化 / 4 视角拼图 | `dataset.py:14-19, 99-102, 131-149, 164-167` |
| 单候选推理（n_samples=1）| `test.py:50`、`test.py:58-67` |
| 执行隔离 + 3 秒超时 | `evaluate.py:14-28, 77-87` |
| 择优口径与 IR 分档 | `evaluate.py:152-177` |
| STEP 导出被注释 | `evaluate.py:71-72` |
| 镜像与依赖钉版（含 `git-lsf` 拼写）| `Dockerfile:1, 4, 20-21, 31, 57, 60` |
| 许可与版权行 | `LICENSE:1-3`、`LICENSE:189` |
| 元数据 | `gh api repos/AIRI-Institute/cadrille`，2026-10-24 |

## 9. 未确认事项

1. **各数据集样本条数**——`data/README.md` 只给下载地址不给数量，**查不到**；HF 数据集卡片未核。
2. **RL 阶段的训练细节**——README 明说「We don't provide RL fine-tuning code for now」（`README.md:34`），随包只有 SFT 代码，**未确认** RL 是 PPO 还是 GRPO、采样多少候选。
3. **HF 两个权重的实测分数**——仓库内无结果表，**未核**（`README.md:34` 只给链接）。
4. **推理显存实测值**——README 未给，**查不到**；§4 的「放得下」是推算。
5. **`git-lsf` 是否在真实构建中报错**——纯读码推断（`Dockerfile:4`），**未实测**（本机不跑）。
6. **训练数据（CAD-Recode v1.5）的许可**——决定其权重能否商用，**未确认**，见 §7。
7. **star / 推送时间会变**——取数日 2026-10-24（`gh api`）。
