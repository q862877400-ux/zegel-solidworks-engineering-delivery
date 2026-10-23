# TripoSR

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/VAST-AI-Research/TripoSR ｜ 技术博客 https://www.tripo3d.ai/research/triposr ｜ 权重 https://huggingface.co/stabilityai/TripoSR ｜ 报告 https://arxiv.org/abs/2403.02151 |
| 许可 | **MIT**——`LICENSE:1-3` 原文「MIT License / Copyright (c) 2024 Tripo AI & Stability AI」；README 另明写「The model is released under the MIT license, which includes the source code, pretrained models, and an interactive online demo」（`README.md:27`）⇒ **含权重在内都是 MIT**，四家里最干净的一份许可；保留版权行即可，无 NOTICE 义务、无地域/规模限制。★注意：`tsr/` 下没有第二份 LICENSE（`Get-ChildItem -Recurse -Filter *LICENSE*` 只命中根一份） |
| 元数据 | 7203 stars · 最近推送 2026-06-04T07:11:09Z · Python（来源：`gh api repos/VAST-AI-Research/TripoSR`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\VAST-AI-Research__TripoSR（HEAD `107cefd`「Update README.md」2026-06-04；shallow clone，`git rev-list --count HEAD` = 1）|
| 证据等级 | 读码（通读 `README.md`（79 行）/ `LICENSE` / `requirements.txt` / `run.py` / `gradio_app.py` / `tsr/system.py` / `tsr/models/isosurface.py` / `tsr/models/tokenizers/{image,triplane}.py` / `tsr/utils.py` / `tsr/bake_texture.py`；**未装依赖、未下权重、未推理**）|

## 1. 一句话定位

Tripo AI 与 Stability AI 合作的**前馈式单图重建**模型：沿用 LRM 的骨架（图 → 三平面 NeRF → 抽面），把「快」做到极限——官方称在 A100 上**不到 0.5 秒**生成一个模型（`README.md:11`）。四家里唯一明确把**权重也按 MIT 放出**的（`README.md:27`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      单图（灰底、正中、前景缩放）；默认走 rembg 去背 + resize_foreground
          run.py:134-152；tsr/utils.py:402,417
              ↓
条件编码  DINO ViT-B/16（facebook/dino-vitb16 的 ViTModel，非 DINOv2）
          取 last_hidden_state 的 patch token 当图像 token
          tsr/models/tokenizers/image.py:12,15,21,52,55
              ↓
中间表示  可学习三平面参数（3 张 plane_size² 平面）→ 摊平成一条 1D token 序列
          tsr/models/tokenizers/triplane.py:11-33
              ↓
生成      **前馈一次前向，无扩散、无采样循环**：backbone（1D Transformer）吃
          [三平面 token + 图像 token]，直接吐回 token，再 detokenize 成三平面
          tsr/system.py:87-120（forward 全文）、tsr/models/transformer/transformer_1d.py
              ↓
执行      NeRF 式解码：renderer.query_triplane 对任意 3D 点返回 {density_act, color}
          同一个函数被用两次——渲染用、抽面网格查询也用
          tsr/system.py:176,194；tsr/models/nerf_renderer.py
              ↓
抽面      分辨率 256 的稠密栅格 → 密度减阈值后取反 → torchmcubes.marching_cubes
          ⇒ 顶点轴序反转为 [z,y,x]、再除以 (res-1) 归一到 0..1
          tsr/models/isosurface.py:44-51；阈值默认 25.0（tsr/system.py:171）
              ↓
编排      single —— 一次前向到底，无重试、无工具、无多智能体
              ↓
验证      visual —— **仓内无 Chamfer / IoU / 水密断言**；README 只给定性对比图
          README.md:18-24
              ↓
交付      mesh —— 默认 OBJ，可 GLB；上色两种：顶点色（默认）或 xatlas 烘纹理图集
          run.py:89-95,173,177-186；tsr/bake_texture.py:9-13
```

★ **网络结构**：**前馈（feed-forward）**，不是扩散也不是流匹配——`TSR.forward` 里没有任何时间步循环（`tsr/system.py:87-120`），这也是它能做到亚秒级的结构性原因。**没有独立纹理分支**：颜色由同一个 NeRF 解码器输出，要么写顶点色、要么用 `bake_texture` 走 xatlas 图集 + OpenGL 位置图栅格化（`tsr/bake_texture.py:9-13,120-125`）。输出格式 **OBJ（默认）/ GLB**（`run.py:89-95`），无 PLY 出口。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **三平面当"可学习的中间画布"** | 不预测体素也不预测点，先随机初始化 3 张平面参数，让 Transformer 改写它们 | `triplane.py:11-33` |
| 2 | **1D 序列装三平面** | 把 3 张平面按 `B×C×(3·H·W)` 摊平，于是 2D 结构问题变成 1D 序列问题，可复用标准 Transformer | `triplane.py:29-33` |
| 3 | **一个查询函数服务两个用途** | 渲染（沿光线取点）与抽面（栅格取点）调同一个 `query_triplane` ⇒ 渲染质量与几何质量天然一致 | `tsr/system.py:176,194` |
| 4 | **分块查询控显存** | 抽面/渲染都按 `chunk_size` 切批（默认 8192），小卡只降速度不降分辨率 | `run.py:60-65,127` |
| 5 | **Marching cubes 的符号取反 + 轴序修正** | 密度先取负再求 `marching_cubes(level, 0.0)`；出网格后顶点按 `[2,1,0]` 换轴、除以 `res-1` 归一 | `isosurface.py:44-51` |
| 6 | **CUDA 缺失时静默退 CPU** | 捕获 `AttributeError`（`torchmcubes` 无 CUDA 符号）后改在 CPU 上算同一件事，并打一行提示 | `isosurface.py:45-49` |
| 7 | **网格栅格存 CPU** | `grid_vertices` 缓存在 CPU 上，避免 256³ 的坐标表常驻显存 | `isosurface.py:26-38` |
| 8 | **纹理烘焙走 GLSL 而非 Python 逐像素** | moderngl 起 GL 上下文，先在位置图集里算每个 texel 的 3D 位置，再回采颜色 | `bake_texture.py:25-26,120-125` |
| 9 | **相机用球面参数化** | 经纬一圈 `get_spherical_cameras`，渲染多视角不用手摆相机 | `tsr/utils.py:341` |

## 4. 可跑性与实测方案

| 项 | 数值 / 结论 | 出处 |
|---|---|---|
| 显存（官方明称） | 单图**约 6 GB** | `README.md:41` |
| 速度 / 分辨率 | A100 上**不到 0.5 秒**；MC 网格 256（`--mc-resolution`）；密度阈值 25.0 写死 | `README.md:11`、`run.py:68`、`tsr/system.py:171` |
| Python / CUDA | Python ≥ 3.8；CUDA 主版本必须与 PyTorch 自带的一致 | `README.md:31,33` |
| 关键依赖 | `torchmcubes`（**从 git 装，不在 PyPI**）、`transformers==4.35.0`、`xatlas==0.0.9`、`moderngl==5.10.0`、`rembg` | `requirements.txt:4,5,11,12,7` |
| 权重体积 | `stabilityai/TripoSR` 7 文件 **1.56 GB** | https://huggingface.co/api/models/stabilityai/TripoSR/tree/main?recursive=true |

**本机判定（Windows / Python 3.14.7 / RTX 4080 SUPER 16 GB —— 机器事实来源：本机 `nvidia-smi --query-gpu=memory.total` 16376 MiB 与 `python --version`，取数日 2026-10-24）**

- 显卡实测 16376 MiB（来源：本机 `nvidia-smi --query-gpu=memory.total`，2026-10-24）⇒ 官方 6 GB 要求（`README.md:41`）下余量充足，**显存完全不是问题**，四家里最轻。
- 唯一硬编译件是 `torchmcubes`：它在 **PyPI 上不存在**（`https://pypi.org/pypi/torchmcubes/json` 返回 404），仓内从 git 装（`requirements.txt:4`），需要本机 nvcc 且 `setuptools>=49.6.0`（`README.md:62`）。本机 CUDA Toolkit 13.3（来源：本机 `$env:CUDA_PATH`）与 torch 轮自带 CUDA 主版本未必一致 ⇒ 编译有失败风险。
- **但这条路有代码级兜底**：`isosurface.py:45-49` 在 `AttributeError` 时退回 CPU 版 marching cubes ⇒ **即便 CUDA 版没编成，抽面仍能出结果，只是慢**。这是本卡最关键的"能不能跑"判据。
- `numpy` 未被钉版（`requirements.txt` 里没有 numpy 行），但 `transformers==4.35.0` 与新版 numpy 2.x 可能存在兼容问题（未验）。`torch` 2.14.1 已有 Windows `cp314` 轮（来源：https://pypi.org/pypi/torch/json）。
- 结论：**四家里本机最可能真跑起来的一个，但未实测**。最小命令与预期：
  `python run.py examples/chair.png --output-dir output/`（`README.md:39`）⇒ 预期在 `output/0/mesh.obj` 得到网格（默认格式 obj，`run.py:91,176`）；要纹理加 `--bake-texture`（`run.py:96-100`）。
- 盘开销：权重 1.56 GB（HF 列表 API）+ 依赖；本机 D: 余 2.76 TB（来源：本机 `Get-PSDrive D`）。**全程只读码，未下载、未安装。**

## 5. 失败模式与已知坑

1. **`torchmcubes` 是最大的一颗雷**：不在 PyPI、要 git + nvcc；README 专门开了一节 Troubleshooting 讲它（`README.md:52-69`），症状是 `AttributeError: module 'torchmcubes_module' has no attribute 'mcubes_cuda'` 或「torchmcubes was not compiled with CUDA support, use CPU version instead」。
2. **阈值 25.0 是硬编码的绝对值**（`tsr/system.py:171`）：不是按样本自适应的相对量 ⇒ 换风格/换尺度输入时表面会整体"胖瘦"漂移，而命令行没有暴露这个参数（`run.py:46-112` 无 `--threshold`）。
3. **单图重建 = 看不见的那一半靠猜**：输入只有一张图，背面完全由先验补（`tsr/system.py:99-120` 只有一路 `rgb_cond`），这是结构性局限而不是 bug。
4. **抽面是稠密栅格**：256³ 全量查询（`isosurface.py:28-38`），分辨率提高是立方级代价，靠 `--chunk-size` 换显存（`run.py:60-65`）。
5. **纹理烘焙依赖 OpenGL**：`moderngl` 要能起 GL 上下文（`bake_texture.py:120-125`），无显示/无驱动的 Windows 会话上可能起不来；不加 `--bake-texture` 就只出顶点色。
6. **质量无自动判据**：README 的对比图是定性（`README.md:18-24`），仓内 `Select-String 'watertight|manifold'` 0 命中 ⇒ 孔洞/自交要自己上 `trimesh` 检查。

## 6. 对我方目标的可用处（机制层面，含**边界**）

我方目标是**让普通模型建出能用、规范的参数化模型（SolidWorks）**。TripoSR 的产物同样是三角网格，**结构上进不了参数化特征树**；但它有几个机制层面的东西值得单独摘出来：

- ✅ **能用它的地方（视觉/参考级）**
  1. **概念外观**：亚秒级出网格（`README.md:11`），适合当"边聊边看"的形体草稿。
  2. **反向渲染校验**：`get_spherical_cameras` + `render` 现成给一圈视角（`tsr/utils.py:341`、`tsr/system.py:122-161`），我方参数化模型渲同样的视角做轮廓比对，是成本最低的"语义对不对"自检。
  3. **参考图回灌**：渲正交三视图当草图素材。
- ✅ **可迁移的机制（本卡的三条硬货）**
  - **"一个查询函数服务两个用途"**（`tsr/system.py:176,194`）：渲染与抽面共用 `query_triplane`，因此**看到的和摸到的必然一致**。这条可直接搬到参数化一侧的"渲染校验即几何校验"——不要另写一套几何探针，复用同一个求值函数。
  - **显存换时间的分块开关放命令行**（`run.py:60-65`）：`--chunk-size` 让同一份代码在小卡上也跑得动。我方工具链要面向不同客户机器时，这类"降速不降分辨率"的旋钮比"自动改分辨率"更安全（分辨率一改，几何就变了）。
  - **编译件缺失时的代码级兜底**（`isosurface.py:45-49`）：CUDA 版不可用就退 CPU 版，并打提示。这是"依赖可选化"的正面样板——对照 TripoSG 的 `from diso import DiffDMC` 顶层硬 import（另一张卡的 §5），差别非常直观。
- ❌ **不能拿它做的事（硬边界）**
  - **不能当 CAD 数据源**：marching-cubes 三角面片，无特征、无草图、无尺寸、无基准；SolidWorks 里只是 graphics body / 网格体，改不了尺寸、出不了带公差的工程图、加不了装配约束。
  - **不能当尺寸真相**：阈值硬编码（`tsr/system.py:171`）、无任何几何指标，输出没有"单位/比例/平行度/同轴度"这类语义。
  - **不能当背面真相**：单图输入，看不见的部分是生成而非测量（`tsr/system.py:99-120`）⇒ 不能用于任何需要"另一侧也确实如此"的场合。
  - **不能替代参数化建模**：它解决"像不像"，我方要"改不改得动"。

## 7. 许可与红线

- **MIT，且覆盖权重**：`LICENSE:1-3`「MIT License / Copyright (c) 2024 Tripo AI & Stability AI」；`README.md:27` 明说「source code, pretrained models, and an interactive online demo」都在 MIT 内。
- **义务**：保留版权声明与许可声明（`LICENSE:12-13`）。无 Apache 那种 NOTICE，也无附加的地域/规模条款——四家里唯一可以直接当 MIT 开源件对待的。
- **红线**：① 仍然不抄代码（我方口径是先搬机制，需要时再按 MIT 引入并记出处）；② 权重虽 MIT，但仍按"不进我方分发物"处理，避免仓库膨胀；③ 它训练数据来自 Objaverse 等公开集，**上游数据的权利不在 MIT 覆盖范围内**（本条为一般性提醒，具体清单本仓未给，`查不到`）。

## 8. 证据清单

- `LICENSE:1-3,12-13` —— MIT / Copyright (c) 2024 Tripo AI & Stability AI / 保留声明义务
- `README.md:9,11,18-24,27,31,33,39,41,43,45,52-69,62` —— 协作方、亚秒级、定性对比图、权重也 MIT、Python≥3.8、CUDA 主版本一致、运行命令、约 6 GB、--bake-texture、--texture-resolution、torchmcubes 排错、setuptools≥49.6.0
- `requirements.txt:4,5,11,12,7` —— torchmcubes（git 装）/ transformers==4.35.0 / xatlas==0.0.9 / moderngl==5.10.0 / rembg
- `tsr/system.py:87-120,99-120,122-161,171,176,194,199-204` —— 前馈一次前向、单路条件、渲染、阈值 25.0、共用查询函数、trimesh 构造
- `tsr/models/tokenizers/image.py:12,15,21,52,55` —— DINOSingleImageTokenizer / facebook-dino-vitb16 / ViTModel / patch token
- `tsr/models/tokenizers/triplane.py:11-33` —— 可学习三平面 / 摊平成 1D token
- `tsr/models/isosurface.py:26-38,44-51,45-49` —— 坐标表缓存 CPU、取负+轴序修正+归一、CPU 兜底
- `tsr/bake_texture.py:9-13,25-26,120-125` + `tsr/utils.py:341,402,417` —— xatlas 图集、位置图集栅格化、moderngl 纹理、球面相机、去背、前景缩放
- `run.py:46-112,60-65,68,89-95,127,134-152,173,177-186` —— 参数全集（无阈值参数）、分块、mc 分辨率 256、obj/glb 选择、chunk_size 应用、预处理、抽面调用、纹理烘焙
- https://huggingface.co/api/models/stabilityai/TripoSR/tree/main?recursive=true —— 7 文件 / 1.56 GB
- https://pypi.org/pypi/torchmcubes/json + https://pypi.org/pypi/torch/json —— torchmcubes 404（不在 PyPI）；torch 2.14.1 有 `cp314` win_amd64 轮
- https://github.com/VAST-AI-Research/TripoSR —— 仓库页（stars / pushed_at 经 `gh api` 复核）

## 9. 未确认事项

1. **非 A100 卡上的墙钟**：官方只给 A100 的 0.5 秒级声明（`README.md:11`），4080 SUPER 上是多少 `查不到`；本机未跑。
2. **`torchmcubes` 在本机 CUDA 13.3 + torch 2.14.1 下能否编过**：未验；不过即便编不过也有 CPU 兜底（`isosurface.py:45-49`），只影响速度。
3. **密度阈值 25.0 的物理含义与可调范围**：代码里是字面量，README 未解释，`查不到`；要调只能改源码。
4. **训练数据来源清单与依赖兼容性**：README 未列数据来源，`查不到`（MIT 只覆盖代码与权重，不覆盖上游数据权利）；`transformers==4.35.0` 与 numpy 2.x / Python 3.12+ 的兼容性未验，`查不到`，这是本机装依赖时最可能先撞上的一处。
