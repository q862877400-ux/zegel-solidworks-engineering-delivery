# TRELLIS

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/microsoft/TRELLIS ｜ 项目页 https://microsoft.github.io/TRELLIS/ ｜ 权重 https://huggingface.co/microsoft/TRELLIS-image-large ｜ 报告 https://arxiv.org/abs/2412.01506 |
| 许可 | **MIT**——`LICENSE:1-3` 原文「MIT License / Copyright (c) Microsoft Corporation.」⇒ 可读可改可商用，保留版权声明即可。★但 README 自陈**两个子模块另有许可**：`diffoctreerast`（源自 diff-gaussian-rasterization）与「Modified Flexicubes」（`README.md:329-333`）——两者条款只在仓外链接，**克隆里没有它们的 LICENSE 文本**（`Get-ChildItem -Recurse -Filter *LICENSE*` 只命中根 `LICENSE`），子模块 `trellis/representations/mesh/flexicubes/` 在本克隆里是空目录（`.gitmodules:1-3` 指向 `MaxtirError/FlexiCubes`）⇒ **条款查不到，按严处理** |
| 元数据 | 14085 stars · 最近推送 2026-06-26T07:27:56Z · Python（来源：`gh api repos/microsoft/TRELLIS`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\microsoft__TRELLIS（HEAD `442aa1e`「Merge pull request #335 from ForeverFancy/main」，2025-11-05；shallow clone，`git rev-list --count HEAD` = 1）|
| 证据等级 | 读码（通读 `README.md`（349 行）/ `LICENSE` / `.gitmodules` / `trellis/pipelines/trellis_image_to_3d.py` / `pipelines/samplers/flow_euler.py` / `models/structured_latent_vae/decoder_mesh.py` / `representations/mesh/cube2mesh.py` / `utils/postprocessing_utils.py`；**未装子模块、未下权重、未推理**）|

## 1. 一句话定位

微软的**结构化潜变量（SLAT）**路线 3D 生成：把「稀疏占据 + 每体素一个特征」当统一中间表示，同一份潜码可解码成**网格 / 3D 高斯 / 辐射场**三种产物（`README.md:9`）。输入是文本或图像，主流用法是图像条件（`README.md:98`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      单图或多图（文本仅作备选，官方自己说"先用文生图再走图像模型"更好）
          trellis/pipelines/trellis_image_to_3d.py:82-116（去背、按 alpha 收紧、裁方、518²）
              ↓
条件编码  DINOv2（名字从预训练参数里取）→ 取 x_prenorm 特征 → LayerNorm 成 patch token
          trellis_image_to_3d.py:74,141-143
              ↓
中间表示  两级：① 稀疏占据潜码 z_s（稠密 3D 噪声，分辨率 = flow_model.resolution）
          ② SLAT（每占据体素一条特征）trellis_image_to_3d.py:179,235-238
              ↓
生成      Rectified Flow + Euler：第一步采样稀疏占据（SparseStructureFlowModel
          sparse_structure_flow.py:55），阈值 0 取占据体素坐标；第二步在该坐标集上
          采样 SLAT（SLatFlowModel structured_latent_flow.py:69）
          trellis_image_to_3d.py:162-193,219-252；采样器 flow_euler.py:11,122
          默认 steps=12、cfg 7.5（占据）/ 3（SLAT）README.md:143-150
              ↓
解码      decode_slat 按需分派三个解码器：mesh / gaussian / radiance_field
          trellis_image_to_3d.py:195-217
              网格解码器 = 稀疏 Transformer + 2 级稀疏细分 → SparseFeatures2Mesh(res*4)（来源：本卡 §8 证据清单）
              再交给 FlexiCubes 取面  decoder_mesh.py:106-120；cube2mesh.py:5,66
              ↓
编排      single —— 一条 pipeline 直下，无重试、无工具、无多智能体
              ↓
验证      visual —— `trellis/` 下只有 datasets/models/modules/pipelines/renderers/
          representations/trainers/utils **八个子包，无 metrics 包**（`Get-ChildItem trellis -Directory`）
          ⇒ **无 Chamfer / 无 IoU / 无水密断言**，评测口径不在仓内
              ↓
交付      mesh —— to_glb 一条龙：Quadric 简化（默认 simplify=0.95）→ 补洞 →
          去不可见面 → xatlas UV 展开 → 多视角烘纹理（默认 texture_size=1024）
          README.md:166-173,170-171；postprocessing_utils.py:399-463
          另可出 PLY（3D 高斯）README.md:176
```

★ **网络结构**：两段都是 **Rectified Flow Transformer**（不是 DDPM 也不是纯前馈回归）——占据段是稠密 DiT，SLAT 段是稀疏 Transformer（Swin 窗口注意力，`decoder_mesh.py:82-83`）。**纹理不是独立分支**，而是「高斯/辐射场解码后往网格上烘」——即纹理来自 SLAT 的特征，不来自图像（`postprocessing_utils.py:276-397`）。输出格式 **GLB**（`README.md:166-173`）+ **PLY**（`README.md:176`），无 OBJ 出口。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **一份潜码多产物** | 占据坐标先定，特征在同坐标上采样；三个解码器读同一份 SLAT，互不依赖 | `trellis_image_to_3d.py:195-217` |
| 2 | **两段式但共享坐标** | 第一段只生成"哪里有东西"，第二段只生成"那里长什么样" ⇒ 分辨率不必一致 | `trellis_image_to_3d.py:281-282` |
| 3 | **可插拔采样器注入** | 多图条件不改模型，只在采样循环里按步轮换条件索引（stochastic）或平均多路预测（multidiffusion） | `trellis_image_to_3d.py:285-340` |
| 4 | **补洞用"多视角可见性 + 最小割"** | 渲 1000 个视角统计每面可见率，把「内侧但从小洞连到外侧」的面割掉，再补 | `postprocessing_utils.py:22-200` |
| 5 | **烘纹理是可微优化而非简单投影** | xatlas 展开后把纹理当可训练参数，多视角图做监督 + TV 正则，余弦退火 | `postprocessing_utils.py:259-268,356-397` |
| 6 | **占据阈值即拓扑旋钮** | `decoder(z_s) > 0` 取坐标（`trellis_image_to_3d.py:191`）；改阈值直接改体素数量与厚度 | 同左 |
| 7 | **FlexiCubes 的 sdf_bias 补偿** | 解码出的 SDF 先减 `1/res` 再做 cube2mesh，避免整网格内缩一格 | `cube2mesh.py:66-68` |
| 8 | **归一化参数随权重走** | SLAT 的 mean/std 存在模型配置里，采样后反归一化，训练/推理不必各写一份 | `trellis_image_to_3d.py:248-250` |

## 4. 可跑性与实测方案

| 项 | 数值 / 结论 | 出处 |
|---|---|---|
| 显存（官方明称） | **至少 16 GB**；只在 A100 / A6000 上验过 | `README.md:41` |
| 系统 | **只在 Linux 上测过**；Windows 见 issue #3「not fully tested」 | `README.md:40` |
| Python / CUDA | Python ≥ 3.8；CUDA Toolkit 11.8 或 12.2（编子模块用）；默认 env 是 torch 2.4.0 + CUDA 11.8 | `README.md:43,45,58` |
| 注意力后端 | 默认 `flash-attn`；`ATTN_BACKEND=xformers` 可换 | `README.md:60,121` |
| 权重体积 | `microsoft/TRELLIS-image-large` 19 文件 **3.30 GB**（1.2B 参数） | https://huggingface.co/api/models/microsoft/TRELLIS-image-large?blobs=true ；参数量见 `README.md:93` |
| 其他权重 | text-to-3D 三档 342M / 1.1B / 2.0B；数据集 500K 物体 | `README.md:94-96`、`README.md:9` |
| 单样本耗时 | **查不到**（README 只给 steps=12 的采样设置，不给秒数） | `README.md:143-150` |

**本机判定（Windows / Python 3.14.7 / RTX 4080 SUPER 16 GB —— 机器事实来源：本机 `nvidia-smi --query-gpu=memory.total` 16376 MiB 与 `python --version`，取数日 2026-10-24）**

- 显卡实测 16376 MiB（来源：本机 `nvidia-smi --query-gpu=memory.total`，2026-10-24）⇒ 官方要求「至少 16 GB」（`README.md:41`）刚好等于整卡容量，**没有任何余量**；而官方只在 A100/A6000（更大显存）上验过。
- Windows 上前提依赖大半没有轮子：`flash-attn` 最新 2.8.3.post2 只有 1 个文件、**无 Windows 轮**；`spconv` 2.3.8 有 5 个文件、**无 Windows 轮**；`kaolin` 只有 1 个 sdist；`diffoctreerast` / `nvdiffrast` 在 PyPI **404（未发布）**；`utils3d` 无 Windows 轮（来源：https://pypi.org/pypi/{flash-attn,spconv,kaolin,utils3d}/json）。这些都要 nvcc 现场编译，而本机 CUDA Toolkit 是 13.3（来源：本机 `$env:CUDA_PATH`），与仓内期望的 11.8/12.2 不同主版本。
- `xformers` 兜底也弱：0.0.35 只有 1 个 win_amd64 文件且是 `py39`（来源：https://pypi.org/pypi/xformers/json）⇒ 3.14/3.12 都用不上。
- 结论：**本机不推荐跑**（结论来自上列的轮子可用性查证与 README 的 Windows「not fully tested」自述，**未实测**）。真要跑，只能先 Linux 容器 + ≥16 GB 卡；本机 16 GB 贴线，风险最高的一段是 `to_glb` 里的补洞：默认渲 1000 个视角（`postprocessing_utils.py:433-434`），而不是生成本身。
- 盘开销：权重 3.30 GB（HF API）+ 依赖（未计入）；本机 D: 余 2.76 TB（来源：本机 `Get-PSDrive D`）。**全程只读码，未下载、未安装。**

## 5. 失败模式与已知坑

1. **Windows 是明确的灰色地带**：Linux 是唯一被测过的系统（`README.md:40`），Windows 只有 issue #3 的社区经验；子模块全是 CUDA 编译件（`setup.sh` 的 `--diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast`，`README.md:66`）。
2. **16 GB 是"必要"不是"够用"**：`README.md:41` 只说 necessary；官方验证卡是 A100/A6000。16 GB 卡上开 `fill_holes_num_views=1000`（`postprocessing_utils.py:434`）与 `texture_size` 放大都会撞墙。
3. **子模块不初始化就没有几何能力**：FlexiCubes 在子模块里（`.gitmodules:1-3`），`cube2mesh.py:5` 直接 `from .flexicubes.flexicubes import FlexiCubes` ⇒ 克隆没 `--recurse-submodules` 时，网格解码器直接 import 失败，而其它两个解码器仍能跑（症状很容易被误判成"模型坏了"）。
4. **拓扑靠后处理补，不是生成时就保证**：补洞 `_fill_holes`（`postprocessing_utils.py:22-200`）与去不可见面是**可选开关**（`postprocessing_utils.py:203-209`），关掉就是带洞带内壳的网格。
5. **多图条件是调参不是训练**：README 自己写「tuning-free … may not give the best results」（`README.md:33`）。
6. **文本模型更弱**：官方明说文本条件「less creative and detailed due to data limitations」（`README.md:27`）。

## 6. 对我方目标的可用处（机制层面，含**边界**）

我方目标是**让普通模型建出能用、规范的参数化模型（SolidWorks）**。TRELLIS 的产物同样是三角网格，边界与 Hunyuan3D-2 同一类，但它多出两条**真正值得搬的机制**：

- ✅ **能用它的地方（视觉/参考级）**
  1. **概念外观与体量**：单图→GLB，用来把「客户描述的形状」快速渲出来评审（`README.md:166-173`）。
  2. **反向渲染校验的现成素材**：仓内 `render_utils` 能渲高斯/辐射场/网格三种模式的视频（`README.md:157-163`），我方建好参数化模型后可比轮廓。
  3. **多视角一致性检查的思路**：`_fill_holes` 用「渲很多视角、统计可见性、最小割」判断哪些面该删（`postprocessing_utils.py:22-200`）——这套「多视角投票 + 割」的判据可直接搬到我方「模型是否自遮挡/是否有内壳」的自检里。
- ✅ **可迁移的机制（这两条比网格本身值钱）**
  - **可插拔条件注入**（`trellis_image_to_3d.py:285-340`）：不改模型，只在采样循环里把多路条件按步轮换或平均。这个"条件后置"的结构可以直接套到我方「多张参考图 / 多段文本规格 → 一份参数化脚本」的约束合成上。
  - **补洞用可见性 + 最小割，而不是几何启发式**（`postprocessing_utils.py:22-200`）：判断"这个面该不该删"用多视角可见率而不是法向/体积，抗噪强；对参数化模型的「多视角轮廓一致性」验收是一条可移植的判据。
- ❌ **不能拿它做的事（硬边界）**
  - **不能当 CAD 数据源**：FlexiCubes 输出的是 SDF 面片化结果，无特征、无草图、无尺寸、无基准；SolidWorks 里只是 graphics body。
  - **不能当尺寸真相**：全仓无 Chamfer/IoU/水密断言（`README.md` 通篇只有视觉与图像级评测），"多大多直"无保证。
  - **不能当纹理来源做工程图**：纹理是烘出来的位图（`postprocessing_utils.py:276-397`），与材质/表面粗糙度等工程属性无关。
  - **不能替代参数化建模**：它解决"像不像"，我方要"改不改得动"。
  - **子模块许可未明** ⇒ 即便只想搬机制，也要注意 `diffoctreerast` / Modified Flexicubes 的条款仓内查不到（§7）。

## 7. 许可与红线

- **主仓 MIT**（`LICENSE:1-3`，`Copyright (c) Microsoft Corporation.`）⇒ 代码可读可改可商用，保留版权声明。
- **两个子模块例外**：README 明确 `diffoctreerast`（源自 diff-gaussian-rasterization）与 Modified Flexicubes 另有许可（`README.md:329-333`），但**条款文本不在克隆里**（只有根 `LICENSE`），子模块目录为空（`.gitmodules:1-3`）⇒ 精确条款 `查不到`。`diff-gaussian-rasterization` 一族的原始许可通常带研究性/非商用限制，**在拿到原文前按"不可商用"处理**。
- **红线**：① 只搬机制不搬代码；② 若要复现，先 `git submodule update --init` 读那两份 LICENSE 原文再决定；③ 我方仓库若引用其任何代码片段，需在 `THIRD-PARTY-NOTICES` 记 MIT 版权行；④ 不把权重纳入我方分发。

## 8. 证据清单

- `LICENSE:1-3` + `README.md:329-333` + `.gitmodules:1-3` —— MIT / Copyright (c) Microsoft Corporation.；两个子模块另有许可；FlexiCubes 子模块地址
- `README.md:9,27,33,40,41,43,45,58,60,66,93,94-96,98,121,143-150` —— SLAT 三产物、文本模型较弱、多图非训练、仅 Linux 测过、16 GB、Python≥3.8、CUDA 11.8/12.2、torch 2.4.0、flash-attn 默认、setup.sh 选项、1.2B、三档文本参数量、推荐图像条件、ATTN_BACKEND、steps 12 / cfg 7.5 / 3
- `README.md:157-163,166-173,170-171,176` —— 三种渲染视频、to_glb 用法、simplify 0.95 / texture 1024、PLY 出口
- `trellis/utils/postprocessing_utils.py:22-200,203-209,259-268,276-397,399-463,433-434` —— 多视角可见性+最小割补洞、开关默认值、xatlas 展开、可微烘纹理、to_glb、1000 视图补洞
- `trellis/pipelines/trellis_image_to_3d.py:74,82-116,141-143,162-193,191,195-217,219-252,248-250,281-282,285-340` —— DINOv2 条件、预处理、两段采样、阈值取坐标、三解码器分派、SLAT 采样与反归一化、共享坐标、可插拔条件注入
- `trellis/pipelines/samplers/flow_euler.py:11,80-111,122,135` —— Rectified Flow Euler 采样器 / t 序列 / CFG 采样器
- `trellis/models/structured_latent_vae/decoder_mesh.py:82-83,106-120` + `trellis/models/sparse_structure_flow.py:55` + `trellis/models/structured_latent_flow.py:69` —— Swin 窗口注意力 / 两级稀疏细分 / FlexiCubes 取面 / 两个 flow 主干类名
- `trellis/representations/mesh/cube2mesh.py:5,59-68,97-130` —— FlexiCubes 引入、res 与 sdf_bias、稀疏 cube→顶点
- https://huggingface.co/api/models/microsoft/TRELLIS-image-large?blobs=true —— 19 文件 / 3.30 GB
- https://pypi.org/pypi/flash-attn/json 、.../spconv/json 、.../kaolin/json 、.../utils3d/json 、.../xformers/json —— Windows 轮缺失情况
- https://github.com/microsoft/TRELLIS —— 仓库页（stars / pushed_at 经 `gh api` 复核）

## 9. 未确认事项

1. **单样本推理耗时**：README 只给 steps=12 采样设置，无秒数，`查不到`。
2. **16 GB 卡上能否跑完整 to_glb**：`README.md:41` 只说"necessary"，未给 16 GB 实测；本机未跑 ⇒ 只能判定"贴线、风险高"。
3. **`diffoctreerast` / Modified Flexicubes 的确切许可条款**：克隆内无文本、子模块未初始化，`查不到`；需 `--recurse-submodules` 后读原文。
4. **评测指标口径**：`trellis/` 下无 metrics 子包（`Get-ChildItem trellis -Directory` 只列八个），README 通篇未给几何指标数字，`查不到`；因此 §2 的"验证=visual"是按「仓内无几何评测代码」+ 产物形态判断的。
5. **Windows 是否会崩在哪一步**：只有 issue #3 的社区经验，`查不到`权威结论；未实测。
