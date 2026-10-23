# CAD-Recode（`filaPro/cad-recode`）

<!-- survey: class=F; repr=code; orchestration=single; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/filaPro/cad-recode ｜ 项目页 https://cad-recode.github.io/ ｜ 论文 https://arxiv.org/abs/2412.14042 |
| 许可 | **CC BY-NC 4.0（非商用）** —— `LICENSE.md:1` 原文「Attribution-NonCommercial 4.0 International」；**只读思想，不可商用、不抄代码/文本**。★ GitHub API 的 `license` 字段报 `NOASSERTION`（不认这个 SPDX id），一律以仓库内 `LICENSE.md` 原文为准 |
| 元数据 | 273 stars · 最近推送 2025-11-16T14:34:15Z · 主语言 Jupyter Notebook（来源：`gh api repos/filaPro/cad-recode`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\filaPro__cad-recode |
| 证据等级 | **读码**（通读 `demo.ipynb` 全部 438 行 + `README.md` + `CHANGELOG.md` + `Dockerfile`；**未安装、未运行、未训练**）|

## 1. 一句话定位

**点云 → CadQuery Python 代码**的单次确定性生成：把 256 个点各占一个「占位 token」喂进 Qwen2-1.5B，让语言模型直接写出可 `exec` 的建模脚本，再由脚本导出 STEP（`demo.ipynb:333-338`）。它是「代码即 CAD 中间表示」这条学术路线里最轻的一个——1.5B 基座 + 一层 51×hidden 线性投影，不加视觉塔、不改注意力（`README.md:27`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      网格 → 面采样 8192 点 → 最远点采样取 256 点；
          平移中心 + 最大边缩放到 2（丢绝对尺度）        `demo.ipynb:188-197`
             ↓
中间表示  每点 → 51 维 Fourier 特征（三个坐标 + 八个频率的 sin/cos）
          → 单层 Linear(51, hidden) → 1 个 token 嵌入      `demo.ipynb:40-52`
             ↓
生成      input_ids = [pad_token]×256 + '<|im_start|>'；
          attention_mask = [-1]×256 + [1]；前向时把 -1 位置整体覆写成点嵌入、
          mask 复位为 1 → Qwen2-1.5B 自回归解码，max_new_tokens=768，
          单次贪心（无 do_sample、无 best-of-N）           `demo.ipynb:88-89, 293-294, 300`
             ↓
编排      single —— 无循环、无工具调用、无多智能体；一次 generate 出一段脚本
                                                          `demo.ipynb:296-301`
             ↓
执行      exec(py_string, globals()) → 取全局变量 r（Workplane）
          → tessellate(0.001, 0.1)                        `demo.ipynb:333-336`
             ↓
验证      numeric —— 双向 Chamfer（8192 点、平方均值）+ 体积 IoU
          （trimesh 多体两两求交）                        `demo.ipynb:394-411`
             ↓
交付      STEP —— cq.exporters.export(compound, '/tmp/1.step')；同批导出 STL
                                                          `demo.ipynb:337-338`
```

★ **学术类必填三项**

- **模型基座与参数量**：Qwen2-1.5B。原文「trained upon Qwen2-1.5B, keeping original tokenizer, and adding a single additional linear layer」（`README.md:27`）；tokenizer 也直接取自 `Qwen/Qwen2-1.5B`（`demo.ipynb:155-158`）⇒ **1.5B 量级 + 一层 51×hidden 线性**，无视觉塔。
- **训练数据从哪来与规模**：权重与数据都在 HF（`README.md:4` 给 model / dataset 链接，v1 与 v1.5 各一套；`CHANGELOG.md:5`）。**仓库内没有训练代码，也没有样本条数**——`README.md:28` 明说「In this repo we provide simple inference demo」⇒ 规模**查不到**。
- **推理是否需要采样多候选择优**：**不需要**。`model.generate` 不带 `do_sample` / `num_return_sequences` / `num_beams`（`demo.ipynb:296-301`）⇒ 贪心，单候选。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **几何塞进 token 位** | 序列头放 N 个 pad token 占位，前向时把这些位置的 embedding 整体覆写成几何嵌入 | `demo.ipynb:293-294, 88` |
| 2 | **用 -1 当「几何位」哨兵** | attention_mask 里用 -1 标记占位位，覆写后立刻复位成 1，不去改 Qwen 的因果 mask 语义 | `demo.ipynb:88-89` |
| 3 | **逐点小 MLP 而非重型编码器** | 8 个频率的 sin/cos（不乘 π）+ 原坐标 = 51 维，单层线性投到 hidden | `demo.ipynb:43-52` |
| 4 | **只在 prefill 注入** | 仅当 `past_key_values` 为空时注入点嵌入，decode 步不重复注入 | `demo.ipynb:84` |
| 5 | **尺度归一化** | 平移中心 + 最大边缩放到 2，用跨样本一致性换掉绝对尺度 | `demo.ipynb:195-197` |
| 6 | **FPS 而非随机采样** | 先从面采 8192 点，再做最远点采样取 256 点 | `demo.ipynb:188-192` |
| 7 | **导出语句外挂** | 模型只写建模脚本，导出（STL/STEP）由外部固定语句追加，判活只看文件是否生成 | `demo.ipynb:335-338` |
| 8 | **变量名契约** | 约定生成脚本把最终实体放进全局变量 `r`，执行侧直接取 `globals()['r'].val()` | `demo.ipynb:334` |
| 9 | **指标可脱离模型** | CD / IoU 全在导出网格上算，模型不参与验证 | `demo.ipynb:388-413` |

## 4. 运行条件与依赖

- **官方环境**：单镜像 `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel`（`Dockerfile:1`）；Open3D 从源码 headless 编译（`Dockerfile:6-17`）；`pytorch3d` 与 `cadquery` 都钉到具体 commit（`Dockerfile:20-21`）；`flash-attn==2.7.2.post1`（`Dockerfile:30`）、`transformers==4.47.1`（`Dockerfile:56`）。
- **显存**：README **没给推理显存数字** ⇒ **查不到**。唯一硬件线索是训练从 4×H100 降到 1×H100（`CHANGELOG.md:13`）。
- **本机（Windows / Python 3.14.7 / RTX 4080S 16GB，来源：本机配置）能不能跑**：**不能按仓库给的方式跑**，三条硬冲突——
  1. 镜像是 Linux CUDA 基础镜像（`Dockerfile:1`），Windows 上要么 WSL2、要么重搭环境；
  2. `flash-attn` 要 nvcc 现场编译，Windows 无官方轮子（`Dockerfile:30`）；
  3. 本机 Python 3.14.7 对 `torch` 2.5.1 没有 cp314 轮子（`Dockerfile:1`）。
  - 补一条：notebook 自述可在 CPU 上跑（`demo.ipynb:8`），那条路只覆盖 demo，不含 flash-attn 分支（`demo.ipynb:154`）。
  - 结论：**只读思想，不在本机复现**。真要跑走 WSL2 + 官方镜像；1.5B 量级权重在 16GB 卡上余量充足（**按参数量推算，未实测**，规模见 `README.md:27`）。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **生成的代码可能直接无效**；CadQuery 执行还可能内存泄漏（正文引 cadquery issue 1665），官方建议独立进程 + 3 秒超时 | `demo.ipynb:313-324` |
| 2 | demo **主动省略了安全隔离**，直接 `exec` 生成物：无沙箱、无超时，只适合可信样本 | `demo.ipynb:324, 333` |
| 3 | **对输入分布敏感**：v1.5 去掉法向、随机采样改 FPS、「按 z 排序」改「不排序」、整数范围 -50…+50 改 -100…+100 | `CHANGELOG.md:8-19` |
| 4 | 指标是**网格近似**：CD 在 8192 个采样点上算，IoU 用网格体积布尔，不是 BRep 精确体积 | `demo.ipynb:394-411` |
| 5 | **变量名契约脆弱**：执行侧写死取全局 `r`，生成的脚本换个变量名即判失败 | `demo.ipynb:334` |
| 6 | 归一化**丢掉绝对尺寸** ⇒ 生成的脚本里尺寸是相对的，未必是可用工程尺寸 | `demo.ipynb:195-197` |

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的模型（SolidWorks 自动化）。这张卡最值得抄的不是模型，是**接口契约**。

1. **「几何 → token 位」的最小注入法**：不动模型结构、不加视觉塔，只在序列头放占位 token、前向时覆写 embedding（`demo.ipynb:88`）。⇒ 我们可以把 SolidWorks 读回的几何事实（包围盒、面数、草图是否完全定义）按同样办法塞给普通模型，代价只有一层线性。
2. **「外挂导出」把生成与判活解耦**：模型不管落盘，导出语句由框架追加，验证只查文件（`demo.ipynb:335-338`）——与本仓「把验证责任转移到静态比对」同一条思路，且比让模型自证可靠得多。
3. **验证可以完全脱离模型**：CD / IoU 只吃导出网格（`demo.ipynb:388-413`）⇒ 换模型、换提示词都不用改验证器。
4. **哨兵位设计可直接复用**：用 mask 里的特殊值标记「这里不是文本」，比另造一套 embedding 拼接逻辑更不容易和上游 `transformers` 打架（`demo.ipynb:88-89`）。
5. **反例价值（重要）**：它**故意丢掉绝对尺寸**（归一化到最大边=2，`demo.ipynb:197`），因为它的目标是「重建形状」而非「建出能加工的零件」⇒ 我们的目标与它相反，**不能照搬归一化**，参数化尺寸必须保真。

## 7. 许可与红线

- ★★ **CC BY-NC 4.0（非商用）**：`LICENSE.md:1` 原文「Attribution-NonCommercial 4.0 International」。
- ⇒ **只读思想，不可商用、不抄代码、不抄文本**。按本仓六条铁律的判档，属于「无许可 / 非商用」一档，与 AGPL/GPL 同等待遇。
- GitHub API 的 `license.spdx_id` 返回 `NOASSERTION`（`gh api repos/filaPro/cad-recode`，2026-10-24）——**不要**据此判「无许可」，也不得据此判「MIT/Apache」，以 `LICENSE.md` 原文为准。
- 它的输出脚本运行时依赖 CadQuery（`Dockerfile:21` 钉到 commit），CadQuery 自身许可是另一件事，**本卡未核**（见 §9）。

## 8. 证据清单

| 证据 | 位置 |
|---|---|
| 基座与「只加一层线性」 | `README.md:27` |
| 权重 / 数据 HF 链接 | `README.md:4`；`CHANGELOG.md:5` |
| 仅推理 demo、无训练代码 | `README.md:28` |
| 模型类与点编码器 | `demo.ipynb:40-52`（编码器）、`demo.ipynb:55-63`（模型）|
| token 占位与 -1 哨兵 | `demo.ipynb:293-294`、`demo.ipynb:88-89` |
| 采样与归一化 | `demo.ipynb:188-197` |
| 执行与导出 STL/STEP | `demo.ipynb:333-338` |
| CD / IoU 算法 | `demo.ipynb:388-413` |
| demo 样例指标（CD 0.283 / IoU 0.943）| `demo.ipynb:383` |
| 内存泄漏告警 + 3 秒超时建议 | `demo.ipynb:313-324` |
| v1.5 架构 / 训练 / 数据改动 | `CHANGELOG.md:8-19` |
| 镜像与依赖钉版 | `Dockerfile:1, 6-17, 20-21, 30, 56` |
| 许可原文 | `LICENSE.md:1` |
| 元数据（stars / 推送 / 语言）| `gh api repos/filaPro/cad-recode`，2026-10-24 |

## 9. 未确认事项

1. **训练数据规模**（多少条 CAD 程序、多少点云）——仓库内既无训练代码也无统计，**查不到**；HF dataset 卡片未核。
2. **是否 / 如何做多候选择优、是否含 RL**——仓库只有推理 demo（`README.md:28`），**未确认**；论文正文未读。
3. **推理显存实测值**——README 未给，**查不到**；§4 的「有余量」是推算，不是实测。
4. **CadQuery 自身许可**——本卡未核（`Dockerfile:21` 只给 commit）。
5. **CPU 路径的真实可用性**——notebook 自述 CPU 可跑（`demo.ipynb:8`），但没给耗时，**未实测**。
6. **star / 推送时间会变**——取数日 2026-10-24（`gh api`），之后不再保证。
