# Step1X-3D

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/stepfun-ai/Step1X-3D ｜ 项目页 https://stepfun-ai.github.io/Step1X-3D/ ｜ 论文 https://arxiv.org/abs/2505.07747 ｜ 权重 https://huggingface.co/stepfun-ai/Step1X-3D（**不门控**）|
| 许可 | **Apache-2.0**（`LICENSE:1-3`「Apache License / Version 2.0」；`README.md:211` 原文「Step1X-3D is licensed under the Apache License 2.0」）。★但 `LICENSE:189` 版权行仍是模板占位「Copyright [yyyy] [name of copyright owner]」，仓库内**没有** NOTICE、源码头也**没有** Copyright 行 ⇒ §7 有合规空洞；★且纹理模块引用了第三方代码（`README.md:113, 208`），不随 Apache-2.0 自动继承 |
| 元数据 | 897 stars · 最近推送 2025-09-08T22:32:12Z · Python · 仓库体积 834589 KB（来源：`gh api repos/stepfun-ai/Step1X-3D`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\stepfun-ai__Step1X-3D |
| 证据等级 | 读码（通读 `inference.py` / `inference_shape_vae.py` / `app.py` / `configs/train-geometry-diffusion/*.yaml` / `step1x3d_geometry/models/pipelines/{pipeline,pipeline_utils}.py` / `autoencoders/{michelangelo_autoencoder,surface_extractors,volume_decoders}.py` / `step1x3d_texture/pipelines/step1x_3d_texture_synthesis_pipeline.py` / `data/watertight_and_sampling.py` / `requirements.txt`；**未安装、未下权重、未推理**）|

## 1. 一句话定位

**两阶段的 3D 原生生成**：几何级用"TSDF-VAE + 3D DiT（整流流）"直接生成**水密 TSDF 体**再提网格，纹理级用 SD-XL 做 6 视图多视生成 + 纹理同步。四个项目里它**最像"实体"**（TSDF + 水密化 + 锐边采样），也是唯一带**离散设计标签**（对称轴/边缘类型）的（`inference.py:40-48`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      单张图；可选再给 caption 或 label={symmetry, edge_type}；preprocess_image
          去背 + 前景比 0.95（`step1x3d_geometry/models/pipelines/pipeline.py:228, 316`）
    ↓
中间表示  ① 编码侧：32768 个表面点（含锐边点）→ 感知器式交叉注意力 → 形状 latent（来源：本卡 §8 证据清单）
             2048 × 64 维（`configs/train-geometry-diffusion/step1x-3d-geometry-1300m.yaml:24, 56-57`、
             `step1x3d_geometry/models/autoencoders/michelangelo_autoencoder.py:230-311`）
          ② 条件侧：DINOv2-with-registers-large（`image_size=518`）+ T5 caption + label encoder
             （同 configs/…-1300m.yaml `:74, 80`、`pipeline.py:319-361`）
    ↓
生成      FluxDenoiser：宽 1280、12 层双流 + 24 层单流、20 头（同 configs/…-1300m.yaml `:84-88`），
          FlowMatchEulerDiscreteScheduler，推理 50 步、guidance 7.5
                                （`inference.py:24`、`pipeline.py:386-431`）
    ↓
几何      latent → VAE 解码成 TSDF → **分层** marching cubes（octree 384，最粗 63 层起步，
          逐层减半）（`pipeline.py:437-444`、`volume_decoders.py:209-233`、`surface_extractors.py:102-118`）
          → trimesh → 去浮岛 → 减面（默认上限 20 万面；label 变体用 40 万）→ 平滑着色
                                （`pipeline.py:238, 467-475`、`pipeline_utils.py:175-202`）
    ↓
纹理      SD-XL base 1.0（`madebyollin/sdxl-vae-fp16-fix`）+ 自定义 adapter
          （`step1x-3d-ig2v.safetensors`）→ 6 视图 → xatlas UV → 可微光栅烘 2048² 贴图
                                （`step1x3d_texture/pipelines/step1x_3d_texture_synthesis_pipeline.py:33-41, 58-61, 137-157`）
    ↓
编排      single，但**两段串联**：先几何出 GLB，再把 GLB 喂给纹理模型
          （`inference.py:14-28` 与 `:54-64`；`app.py:38-50` 是同一套路）
    ↓
执行      单卡；VAE/transformer 有 CPU offload 顺序声明
          （`pipeline.py:88-90`）；bf16 → 提几何前会转 fp16（`pipeline.py:434-436`）
    ↓
验证      visual —— 仓内无几何指标、无 F 分数、无测试；只能看 GLB
    ↓
交付      mesh —— GLB ×2：无贴图几何 GLB 与带贴图 GLB
          （`inference.py:26-27, 50-51, 63-64`、`pipeline.py:452-475`）
```

★ 三问定性：**多视图**（纹理阶段是 6 视图多视扩散，`step1x_3d_texture_synthesis_pipeline.py:39`；几何阶段是单图条件）· **前馈**（**否**，几何是 50 步扩散采样，`inference.py:24`）· **重建式**（**否**，是生成式 latent diffusion，不是多视几何求解）。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（不贴代码） | 出处 |
|---|---|---|---|
| 1 | **TSDF 而不是等值面** | 生成目标是截断符号距离场，因此提面结果天然接近封闭体 ⇒ 后续能做布尔/抽壳的前提 | `volume_decoders.py:137-180`、`surface_extractors.py:102-118` |
| 2 | **分层 marching cubes** | 从 63 起步逐层减半到目标分辨率，粗层只解近表面的体素 ⇒ 高分辨率不必全空间采样 | `volume_decoders.py:209-233, 267-280` |
| 3 | **锐边采样 + 绕数水密化** | 预处理按二面角阈值 30° 单独采"锐边点"参与 VAE 编码（硬边不糊）；多视深度可见性 + 绕数阈值 0.5 判内外，把开放网格封闭 | `data/watertight_and_sampling.py:344, 235-317`（阈值 `:241`） |
| 4 | **★ 离散设计标签当条件** | `symmetry ∈ {x, asymmetry}`、`edge_type ∈ {sharp, normal, smooth}` 经 label encoder 进 DiT ⇒ 少量离散标签就能控几何倾向 | `inference.py:42`、`pipeline.py:326-342`、`app.py:84-91` |
| 5 | **感知器编码点云而非体素** | 用可学习 query 与点特征做交叉注意力，把 32768 点压成 2048 个 latent ⇒ 显存不随分辨率爆炸 | `michelangelo_autoencoder.py:230-311, 486` |
| 6 | **两阶段解耦** | 几何先落 GLB，纹理单独再跑 ⇒ 可以先只验几何、再决定要不要付纹理的代价 | `inference.py:14-28, 54-64` |
| 7 | **VAE 往返通道** | 给定任意网格/点云可走 encode→decode→提面，输出规范化的水密网格（octree 可调到 512） | `inference_shape_vae.py:14-56` |
| 8 | **面数是显式交付约束 + 去浮岛/平滑** | `reduce_face` 默认上限 5 万面、pipeline 默认 20 万、label 变体 40 万；提面后先移除小连通块（避免网格里飘碎片）再平滑法线 | `pipeline_utils.py:175-202`、`pipeline.py:238, 467-475`、`inference.py:45` |

## 4. 可跑性与实测方案

- **官方环境**：conda `python=3.10`（`README.md:94`）、**CUDA 12.4**（`README.md:98`）、`torch==2.5.1/torchvision==0.20.1/torchaudio==2.5.1`（cu124 索引，`README.md:101`）、`torch-cluster`（`README.md:103`）、`pytorch3d`（`README.md:104`）、**`kaolin==0.17.0` 且只能按 `torch-2.5.1_cu124` 的预编译索引装**（`README.md:105`），还要在本地 `python setup.py install` 两个 CUDA 扩展：`custom_rasterizer` 与 `differentiable_renderer`（`README.md:107-111`）。`requirements.txt` 另钉 `diffusers==0.32.2`、`transformers==4.48.0`、`pytorch-lightning==2.2.4`、`sageattention==1.0.6`、`cupy-cuda12x==13.4.1`、`pymeshlab`、`xatlas==0.0.10`，并从 git 装 `nvdiffrast` 与 `pytorch3d`（`requirements.txt:2, 18, 28-29, 36, 43, 46, 50-52`）。
- **权重体积**（HF 文件清单，取数日 2026-10-24）：Geometry-1300m 7.25 GB（transformer 5.27 GB + vae 0.77 GB + visual_encoder 1.22 GB）；Geometry-Label-1300m 8.78 GB（transformer 5.09 GB + visual_encoder 2.93 GB + vae 0.77 GB + label 0.03 GB）；Texture 3.60 GB；纹理还要 SD-XL base 1.0（diffusers 格式，`unet/diffusion_pytorch_model.safetensors` 10.27 GB + text_encoder 0.49 GB + text_encoder_2 2.78 GB + vae 0.33 GB = 13.88 GB，因代码没传 variant 拉的是 fp32，`step1x_3d_texture_synthesis_pipeline.py:137`）。四块相加 7.25 + 8.78 + 3.60 + 13.88 ≈ 33.5 GB，即按 `inference.py:69-74` 全跑一遍所需的磁盘。来源：`https://huggingface.co/api/models/stepfun-ai/Step1X-3D/tree/main?recursive=true` 与 `https://huggingface.co/api/models/stabilityai/stable-diffusion-xl-base-1.0/tree/main?recursive=true`。
- **显存与耗时**：官方表给 **27 G / 29 G**，50 步 **152 秒**（`README.md:117-120`）。
- **本机（Windows + Python 3.14.7 + 4080S 16 GB，来源：本机 `python --version` / `nvidia-smi` 16376 MiB）能不能跑**：**不能**，四条都过不去。
  1. **27 GB > 16 GB**，这是硬门槛，不是调参能解决的（`README.md:119`）。
  2. `kaolin==0.17.0` 只有按 `torch-2.5.1_cu124` 编的预编译包（`README.md:105`），没有对应 16 GB 卡就能跑的替代路径。
  3. 本机 nvcc 是 CUDA 13.3（本机 `nvcc` 路径），与 cu124 钉版不同代，编那两个 CUDA 扩展要先补装 12.4 toolkit。
  4. Python 3.14.7 无 `torch==2.5.1` 轮子（`README.md:101`）；本机虽有 Astral CPython 3.10.21（本机 `py -0`）可用，但前三条已封死。
- **若跑（按官方 27 G/29 G 口径，需 ≥32 GB 显存的卡，`README.md:119-120`；或租机器）**：`python inference.py`（`README.md:168-170`），它依次跑 geometry → label 变体 → texture → label 变体+texture（`inference.py:67-74`）。预期落 4 个 GLB；要省显存可只跑第一段，并降 `octree_resolution`（默认 384，`pipeline.py:232`）与 `max_facenum`（默认 20 万，`pipeline.py:238`）——注意 README 的 27 G 是"50 步 + 默认参数"口径。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **27 G 显存门槛**，16 GB 卡直接出局 | `README.md:119` |
| 2 | **依赖地狱**：kaolin / pytorch3d / torch-cluster / cupy 逐个钉死到 torch 2.5.1+cu124，任一处版本错位就装不上 | `README.md:101-105`、`requirements.txt:2, 50-52` |
| 3 | **两个 CUDA 扩展要就地编译**（光栅化器与可微渲染器），失败时报错在 setup.py 里，与主流程无关 | `README.md:107-111` |
| 4 | **纹理阶段额外背一个 SD-XL**（显存与磁盘再上一台阶，且代码默认拉 fp32 变体）；**`inference.py` 连续跑四段且每段新建 pipeline**，前一个对象没有显式释放 ⇒ 峰值可能叠加（**未实测**，读码推断） | `step1x_3d_texture_synthesis_pipeline.py:33, 137`、`inference.py:18-20, 34-36, 59, 67-74` |
| 5 | **无 Windows 说明**：README 全文只给 conda + CUDA 12.4 的 Linux 口径；**无测试、无几何指标**（仓库根无 tests，`val_data` 只是 3 个 json 清单） | `README.md:92-111`、仓库根文件清单 |
| 6 | **label 变体只是"另一个权重"**，不是同一模型的可选开关（subfolder 不同） | `inference.py:35`、`README.md:66` |

## 6. 对我方目标的可用处（机制层面，含**边界**）

目标：让普通模型建出**能用、规范**的参数化模型（SolidWorks）。

- **可迁移**：① ★「**锐边阈值 30° 单独采样**」（`data/watertight_and_sampling.py:344`）是一套可直接用的**判据**：我们可以用同一个二面角阈值判断"这个网格能不能被少量平面/圆柱拟合"，从而决定是否值得往参数化方向走。② ★「**绕数 0.5 + 可见性做水密化**」（同文件 `:235-317`）是我们最缺的一道检查——SolidWorks 收网格前必须先过水密/流形关。③ 「**离散设计标签控几何**」（`inference.py:42`、`app.py:84-91`）证明了"用极少量离散开关影响生成"可行，这是最接近"参数化意图"的可借形态：我们的尺寸/特征清单可以先用少量枚举标签承载。④ 分层 marching cubes（`volume_decoders.py:209-233`）是"高分辨率但显存有限"的通用解法。
- **★ 边界**：
  1. **依然是无参数三角网格**：没有草图、没有特征树、没有尺寸；GLB 进 SolidWorks 只能当网格体/图形实体，参数化要人工重建。
  2. **分辨率决定特征下限**：VAE 用 32768 个采样点（yaml `:24`）、octree 384（`pipeline.py:232`）⇒ 远小于采样尺度的孔/倒角表达不出来；它是"造型级"不是"零件级"。
  3. **可控粒度极粗**：全部控制面只有 `symmetry` 与 `edge_type` 两个维度（`app.py:84-91`），达不到参数化驱动。
  4. **纹理是烘焙图**，不是材料定义；无公差、无粗糙度工艺含义。
  5. **27 G 显存**（`README.md:119`）意味着这条路线在我方只能是"离线/租卡"环节，不能进本机闭环。

## 7. 许可与红线

- **主许可 Apache-2.0**（`LICENSE:1-3`、`README.md:211`）：可读、可改、可商用。
- ★ **合规空洞**：`LICENSE:189` 的版权行仍是 `Copyright [yyyy] [name of copyright owner]`，仓库内**没有** NOTICE 文件，源码文件头也**没有** Copyright 行（抽查 `step1x3d_geometry/models/pipelines/pipeline.py:1-3` 只有一句"refer to Hugging Face Diffusers library"）⇒ 我们若引用/分发，**须自己指定版权人**（合理做法是按 repo owner `stepfun-ai` 署名并注明改动），否则 Apache-2.0 的"保留版权声明"义务无处落地。
- ★ **不随主许可继承的第三方成分**（`README.md:113, 208`）：纹理模块复用了 **Hunyuan3D 2.0** 的 `custom_rasterizer` 与 `differentiable_renderer`（代码在 `step1x3d_texture/custom_rasterizer/`、`step1x3d_texture/differentiable_renderer/`），多视生成部分参考 **MV-Adapter**、多视渲染参考 **bpy-render**；纹理还要求下载 **SD-XL base 1.0**（`stabilityai/stable-diffusion-xl-base-1.0`）与 `sdxl-vae-fp16-fix`。这些各有自己的许可，**不在本仓库 Apache-2.0 的授权范围内**——本卡未逐份核（§9）。
- **权重**：HF 仓库**不门控**（可直接拉清单，见 §4），但模型卡是否在 Apache-2.0 之外叠加条款——未核（§9）。
- **训练数据**：README 自述数据来自 Objaverse / Objaverse-XL 等（`README.md:71-75`），数据集自身的许可未核。

## 8. 证据清单

- Apache-2.0 与占位版权行 / 第三方成分声明 —— `LICENSE:1-3, 189`、`README.md:211, 113, 207-208`
- 环境与钉版（python3.10 / cuda12.4 / torch2.5.1 / kaolin / 两个扩展）—— `README.md:94, 98, 101-111`
- requirements 钉版 —— `requirements.txt:2, 18, 28-29, 36, 43, 46, 50-52`
- 显存 27 G / 29 G 与 50 步 152 秒 —— `README.md:117-120`
- 权重参数量表（1.3B / 1.3B / 3.5B / 6.1B）—— `README.md:65-68`
- latent 规格、条件编码器、参数规模注释（191 M / 731 M / 1.3 B / 2.2 B）、Denoiser 规模 —— `configs/train-geometry-diffusion/step1x-3d-geometry-1300m.yaml:24, 56-57, 63-65, 74, 80, 4-6, 8-10, 84-88`
- 推理调用（50 步 / guidance 7.5 / label / octree / max_facenum）—— `inference.py:24, 42-45`
- pipeline 默认参数（前景 0.95 / octree 384 / 上限 20 万面）+ 条件编码与 CFG —— `pipeline.py:228, 232, 238, 319-361, 386-431`
- 提几何 / 后处理 / 分层 marching cubes / 提面器 —— `pipeline.py:437-475`、`volume_decoders.py:209-233, 267-280`、`surface_extractors.py:102-135`
- 感知器 VAE 与 num_latents —— `michelangelo_autoencoder.py:230-311, 486`
- 锐边采样 30° / 绕数 0.5 水密化 —— `data/watertight_and_sampling.py:344, 235-317, 241`
- 去浮岛与减面默认值 / VAE 往返通道 —— `pipeline_utils.py:175-184, 198`、`inference_shape_vae.py:14-56`
- 纹理管线（SD-XL / 6 视图 / 2048 渲染与贴图 / 无 variant）—— `step1x_3d_texture_synthesis_pipeline.py:33-41, 58-61, 137-157`
- gradio 控制面 —— `app.py:24, 83-91`
- 权重文件体积 —— `https://huggingface.co/api/models/stepfun-ai/Step1X-3D/tree/main?recursive=true`（2026-10-24）
- SD-XL base 文件体积 —— `https://huggingface.co/api/models/stabilityai/stable-diffusion-xl-base-1.0/tree/main?recursive=true`（2026-10-24）
- 元数据 —— `gh api repos/stepfun-ai/Step1X-3D`，2026-10-24

## 9. 未确认事项

1. **本机 16 GB 上"降参数后到底要多少显存"**——README 只给默认口径 27 G（`README.md:119`），降到 octree 256 / 小 `max_facenum` 后的真实峰值**未实测**，无法判断是否擦到 16 GB 边缘。
2. **耗时**——只有"50 步 152 秒"这一个官方数（`README.md:119`），不含纹理阶段与模型加载，端到端**查不到**。
3. **`inference.py` 四段连跑是否显存叠加**——读码推断（`inference.py:67-74`），**未实测**。
4. **第三方组件许可与 HF 模型卡条款**——Hunyuan3D 2.0 的 rasterizer/renderer、MV-Adapter、bpy-render、SD-XL base 各自许可**未逐份核**，模型卡是否叠加条款也**未核**，直接影响"能不能商用输出"。
5. **"水密"到什么程度**——README 没给量化指标（如闭合性/流形通过率），仓内也无测试，**查不到**。
6. **star / 推送时间会变**——取数日 2026-10-24（`gh api`）。
