# InstantMesh

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/TencentARC/InstantMesh ｜ 论文 https://arxiv.org/abs/2404.07191 ｜ 权重 https://huggingface.co/TencentARC/InstantMesh |
| 许可 | **Apache-2.0**（`LICENSE:1-3`「Apache License / Version 2.0, January 2004」）。★但 `LICENSE:189` 的版权行仍是模板占位「Copyright [yyyy] [name of copyright owner]」——仓库内**没有**填好的版权人，也**没有** NOTICE 文件；真实版权声明只散在源码头（`src/models/lrm_mesh.py:1`「Copyright (c) 2023, Tencent Inc」、`src/models/decoder/transformer.py:1`「Copyright (c) 2023, Zexin He」）。★另有 19 个文件带 NVIDIA「严格禁止」头，见 §7 |
| 元数据 | 4575 stars · 最近推送 2025-01-03T09:09:13Z · Python（来源：`gh api repos/TencentARC/InstantMesh`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\TencentARC__InstantMesh |
| 证据等级 | 读码（通读 `run.py` / `app.py` / `configs/*.yaml` / `src/models/lrm_mesh.py` / `decoder/transformer.py` / `encoder/dino_wrapper.py` / `utils/camera_util.py` / `utils/mesh_util.py` / `utils/infer_util.py` / `geometry/rep_3d/flexicubes_geometry.py`；**未安装、未下权重、未推理**）|

## 1. 一句话定位

**单图 → 六视图 → 前馈 LRM**：用 Zero123++ 把一张图"想象"成 6 个固定视角（`run.py:173-176`），再用一个 16 层 transformer 把 6 个视图回归成三平面，最后 FlexiCubes 提网格（`src/models/lrm_mesh.py:88-190`）。**没有逐场景优化**——一次前向出结果，所以它是"前馈式多视重建"，不是 NeRF/SDF 那种每形状迭代的重建。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      单张 PNG/JPG/WebP；rembg 去背 + 把前景缩放到画面 85%（`run.py:167-170`、
          `src/utils/infer_util.py:11-63`）。输入只此一张，没有深度/相机/多视
    ↓
中间表示  Zero123++ v1.2（SD 系多视图扩散，fp16 + EulerAncestral trailing）
          输出 960×640，按 3 行 2 列重排成 6 张 320×320（来源：本卡 §8 证据清单）
                                （`run.py:99-107`、`zero123plus/pipeline.py:336-337`、`run.py:181-183`）
          6 个视图的相机位姿是**写死**的：方位角 30/90/150/210/270/330，（来源：本卡 §8 证据清单）
          俯仰 +20/−10 交替，fov 30°（`src/utils/camera_util.py:99-100, 105`）
    ↓
生成      ViT-B/16（`facebook/dino-vitb16`，768 维）+ 16 维相机嵌入走 adaLN
          → 每视图 patch token 拼接 → 16 层交叉/自注意力 transformer（dim 1024，
          16 头）→ 3×(32×32) token → 反卷积 2× 上采样到 64（`configs/instant-mesh-large.yaml:4-12`、
          `src/models/encoder/dino_wrapper.py:29-33, 52-56`、`src/models/decoder/transformer.py:93-100, 118`）
    ↓
几何      FlexiCubes：128³ 体素网格上每顶点回归 (sdf, 形变, 20 组权重)，
          顶点形变再做 1/(grid_res×4)·tanh 归一化防翻面，然后 marching-tet 提面
                                （`configs/instant-mesh-large.yaml:14-15`、`src/models/lrm_mesh.py:54, 119, 159-190`、
                                 `src/models/geometry/rep_3d/flexicubes_geometry.py:44, 63-71`）
    ↓
纹理      二选一：① 直接查三平面取顶点色（默认）；② xatlas 参数化 UV → nvdiffrast
          光栅化得每像素 3D 位置 → 查纹理场，出 1024² 贴图
                                （`src/models/lrm_mesh.py:360-367, 369-380`、`src/utils/mesh_util.py:161-181`、
                                 `configs/instant-mesh-large.yaml:21`）
    ↓
编排      single —— `run.py` 一把梭：一个进程里先跑扩散再跑重建，中间 `del pipeline`
          腾显存（`run.py:188`）；`app.py` 只是在外面套了层 gradio
    ↓
执行      单卡即可；两卡时**扩散放 cuda:0、重建放 cuda:1**（`app.py:27-32, 101, 111`）
    ↓
验证      visual —— 仓内无任何几何指标、无测试；只能看导出的 OBJ/转台视频
          （`run.py:237-261` 用 120 帧渲染 mp4 当自检）
    ↓
交付      mesh —— OBJ。默认带顶点色；`--export_texmap` 时给 OBJ + MTL + PNG
                                （`src/utils/mesh_util.py:18-28` 顶点色路径、`43-89` 贴图路径）
```

★ 三问定性：**多视图**（是，零样本多视扩散出 6 视）· **前馈**（是，一次前向，无优化循环）· **重建式**（是 LRM 式"由带位姿多视回归规范表示"，但**不是**逐场景优化的重建）。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **空集 SDF 的显式兜底** | 若网格内部全为正或全为负（提不出面），把中心顶点顶到正、边界顶点压到负，并让这批样本的梯度断掉 ⇒ 不崩、不静默出空网格，而是给一个退化但合法的形状 | `src/models/lrm_mesh.py:122-157` |
| 2 | **形变幅度按分辨率归一化** | 顶点形变 = 1/(grid_res·4)·tanh(raw)，把位移锁在半个体素量级，防三角形翻面 | `src/models/lrm_mesh.py:54, 119` |
| 3 | **可裁视图数** | 6 视默认，`--view 4` 时取索引 [0,2,4,5] 并把相机一起裁 —— 视图数与相机参数必须同步裁，这是可迁移的对齐纪律 | `run.py:204-207` |
| 4 | **相机位姿写死成常量表** | 6 个方位角/俯仰角/30° fov 全写死在函数里而不是从数据读 ⇒ 输入分布是锁死的，换来免标定 | `src/utils/camera_util.py:95-111` |
| 5 | **几何权重与形变同头回归** | FlexiCubes 的 beta(12)/alpha(8)/gamma(1) 三组权重与 sdf/形变同一网络头输出，一起决定最后的面片拓扑 | `flexicubes_geometry.py:67-71` |
| 6 | **顶点色与 UV 贴图双通道** | 同一几何两种材质出法：顶点色快、贴图慢但通用；写死在同一函数里按 flag 分支 | `src/models/lrm_mesh.py:340-382` |
| 7 | **UV 空间反查 3D 再查场** | xatlas 展开 → 在 UV 栅格上光栅化 → 插值回每个纹素的世界坐标 → 用这些坐标去查三平面 ⇒ 不用可微渲染器也能烘焙 | `src/utils/mesh_util.py:161-181` |
| 8 | **导出时的坐标系修正** | OBJ 路径：Z 取反 + 面序反转；贴图路径额外做纹理 V 翻转 + 3×3 膨胀补边 | `src/utils/mesh_util.py:20-21, 85-89` |
| 9 | **大对象先释放** | 扩散跑完显式 `del pipeline` 再加载重建模型，把峰值摊开 | `run.py:187-188` |
| 10 | **两卡分工** | 扩散与重建分卡，靠 `torch.cuda.device_count() >= 2` 判断 | `app.py:27-32` |

## 4. 可跑性与实测方案

- **官方环境**：`Python>=3.10`、`PyTorch>=2.1.0`、`CUDA>=12.1`（`README.md:31`）；实际钉 `torch==2.1.0 / torchvision==0.16.0 / torchaudio==2.1.0`（cu121 索引）与 `xformers==0.0.22.post7`（`README.md:45-46`）；`requirements.txt` 再钉 `diffusers==0.20.2`、`transformers==4.34.1`，并从 git 装 `nvdiffrast`（`requirements.txt:13, 14, 19`）。
- **权重体积**：Zero123++ v1.2 共 5.58 GB（unet 3.46 GB + text_encoder 0.68 GB + vision_encoder 1.26 GB + vae 0.17 GB），InstantMesh 侧 3.25 GB（`diffusion_pytorch_model.bin` 1.73 GB + `instant_mesh_large.ckpt` 1.51 GB），合计 ≈ 8.8 GB（来源：`https://huggingface.co/api/models/sudo-ai/zero123plus-v1.2/tree/main?recursive=true` 与 `https://huggingface.co/api/models/TencentARC/InstantMesh?blobs=true`，取数日 2026-10-24）。
- **显存**：README **没给数字** ⇒ 查不到。反证很有力：issue #126 在 23.64 GiB 的卡上仍报 `Tried to allocate 15.00 GiB`、进程已占 9.95 GiB（https://github.com/TencentARC/InstantMesh/issues/126）；issue #23 是双 3090（2×24 GB）也 OOM（https://github.com/TencentARC/InstantMesh/issues/23）。
- **预计耗时**：README 全文无耗时数字 ⇒ 查不到。
- **本机（Windows + Python 3.14.7 + 4080S 16 GB，来源：本机 `python --version` / `nvidia-smi`，16376 MiB）能不能跑**：**不能按仓库方式跑**，三条硬阻塞。
  1. `torch==2.1.0` 没有 cp314 轮子（钉版在 `README.md:45`），本机默认解释器是 3.14.7。
  2. `nvdiffrast` 必须用 nvcc 编译（`requirements.txt:29`），本机只有 CUDA 13.3（本机 `nvcc` 路径），与 cu121 钉版不同代。
  3. 即便绕过前两条，16 GB 低于 issue #126 里 24 GB 都 OOM 的占用（同上 URL）。（来源：本卡 §8 证据清单）
- **若跑，怎么跑（预期）**：本机 `py -0` 已有一个 Astral 管理的 CPython 3.10.21，可用它建 venv 装 cu121 轮子；先用更小的 base 变体压显存（`instant_mesh_base.ckpt` 1.25 GB，见上面的 HF 文件清单），命令 `python run.py configs/instant-mesh-base.yaml examples/hatsune_miku.png --view 4`（`run.py:70-81`）。预期：`outputs/instant-mesh-base/meshes/<name>.obj` 落地（`run.py:136-137, 214`），显存不足时崩在 `run.py:216` 的 `extract_mesh` 里（128³ FlexiCubes 是峰值所在，`configs/instant-mesh-large.yaml:14`）——**此预期未实测**。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **背面靠幻想**：输入只有一张图，背面是 Zero123++ 编出来的，不是观测到的 | `run.py:173-176` |
| 2 | **24 GB 卡都会 OOM**，且失败点在 FlexiCubes 索引选择那一步 | https://github.com/TencentARC/InstantMesh/issues/126 |
| 3 | **`--export_texmap` 很慢**：NeRF 变体默认 iso-surface 分辨率 256，UV 展开会拖很久（README 自己提示可调低） | `README.md:97`、`configs/instant-nerf-large.yaml:20` |
| 4 | **空形状被"补"成合法网格**：全正/全负时被强行改成有面，失败看起来像成功 | `src/models/lrm_mesh.py:129-143` |
| 5 | **没有测试、没有几何指标**：仓库根无 tests 目录，验收只有肉眼与转台视频 | 仓库根文件清单；`run.py:237-261` |
| 6 | **强依赖 rembg 与 nvdiffrast**：rembg 要拉 onnx 权重、nvdiffrast 要编译，两者都是常见安装失败点 | `run.py:159`、`requirements.txt:12, 19` |
| 7 | **视图数写死 4 或 6**：`--view` 只接受 {4,6}，更多视图不支持（README 的 TODO 也确认） | `run.py:77`、`README.md:27` |
| 8 | **训练数据不给**：只有 dataloader，数据集因体积不发布 ⇒ 无法在自有数据上复现 | `README.md:101` |

## 6. 对我方目标的可用处（机制层面，含**边界**）

目标：让普通模型建出**能用、规范**的参数化模型（SolidWorks）。

- **可迁移**：① 「空集兜底」机制（`lrm_mesh.py:122-157`）值得照抄思路——生成失败要**显式产出可诊断的降级结果**，而不是静默给空；我们的 COM 装配链同样需要这种"失败可见"。② 「相机表写死」（`camera_util.py:95-111`）适合当我们自建**标准六视图评估台**的位姿来源。③ 「UV 反查 3D 再查场」的烘焙路径（`mesh_util.py:161-181`）是一套不依赖可微渲染器的贴图回填做法，可用于给已有网格补贴图。
- **★ 边界（这是三角网格的通病，务必写进选型结论）**：
  1. **没有参数化**：输出是三角面片 + 顶点色/贴图，没有草图、没有特征树、没有尺寸约束 ⇒ 进 SolidWorks 只能当"导入的图形实体/网格体"，要拿它做参数化零件得先 ScanTo3D/网格转实体，再人工重建。
  2. **没有真实尺度与单位**：几何被网格尺度 2.1 归一化（`configs/instant-mesh-large.yaml:15`），尺寸全靠自己缩放。
  3. **不保证水密**：FlexiCubes 提的是等值面，仓内没有任何水密/流形检查（`src/models/lrm_mesh.py:159-190` 之后直接导出）⇒ 拿去布尔/抽壳会失败。
  4. **不能用于有背面配合面的零件**（背面是生成的，不是测的），也**不能用于精密特征**：128³ 体素（`configs/instant-mesh-large.yaml:14`）意味着远小于体素的小孔/倒角表达不出来。

## 7. 许可与红线

- **整体 Apache-2.0**（`LICENSE:1-3`）：可读、可改、可商用。
- **义务**：保留版权声明、随分发带 NOTICE、声明改动过哪些文件。★但仓库**没有** NOTICE 文件、`LICENSE:189` 的版权行还是占位符 ⇒ 我们能保留的只有源码头里的那两处（`src/models/lrm_mesh.py:1`、`src/models/decoder/transformer.py:1`）；分发时须自己把"版权人"补全并写明改动。
- ★★ **红线（本卡最重要的发现）**：`src/` 下有 **19 个 `.py` 文件**开头是 NVIDIA 的**全版权保留 + 禁止再分发**声明而不是 Apache-2.0：`# Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.` … `Any use, reproduction, disclosure, or distribution … without an express license agreement from NVIDIA … is strictly prohibited.`（样例：`src/utils/mesh_util.py:1-7`、`src/models/geometry/rep_3d/flexicubes_geometry.py:1-7`、`src/models/geometry/rep_3d/dmtet.py:1-6`）。⇒ 这 19 个文件按它们自己的头**不是** Apache-2.0 可抄的；我们**只读思想、不抄代码**。
- **权重与数据**：HF 模型卡是否叠加额外条款——未核（§9）；Zero123++（`sudo-ai/zero123plus-v1.2`）是另一份权重，许可亦未核；训练数据 Objaverse（`README.md:101`）许可未核。

## 8. 证据清单

- Apache 2.0 正文与占位版权行 —— `LICENSE:1-3`、`LICENSE:189`；源码版权头 —— `src/models/lrm_mesh.py:1`、`src/models/decoder/transformer.py:1`
- NVIDIA「禁止再分发」头文件样例 —— `src/utils/mesh_util.py:1-7`、`src/models/geometry/rep_3d/flexicubes_geometry.py:1-7`
- 环境钉版与 Python/CUDA 要求 —— `README.md:31, 45-46`、`requirements.txt:13, 14, 19`
- 6 视图生成 320×320 切分 / 4 视图裁剪 —— `run.py:181-183, 204-207`、`zero123plus/pipeline.py:336-337`
- 相机位姿常量表 —— `src/utils/camera_util.py:95-111`
- 三平面回归网络规模 —— `configs/instant-mesh-large.yaml:4-12`、`src/models/decoder/transformer.py:93-100, 118`
- FlexiCubes 网格与权重 —— `configs/instant-mesh-large.yaml:14-15`、`flexicubes_geometry.py:44, 63-71`
- 空集 SDF 兜底 / 形变归一化 —— `src/models/lrm_mesh.py:54, 119, 122-157`
- 顶点色 vs UV 贴图两条路径 —— `src/models/lrm_mesh.py:340-382`、`src/utils/mesh_util.py:18-28, 43-89, 161-181`
- 两卡分工 —— `app.py:27-32`
- NeRF 变体 256 分辨率提示 —— `README.md:97`、`configs/instant-nerf-large.yaml:20`
- 权重体积（HF 文件清单）—— https://huggingface.co/api/models/TencentARC/InstantMesh?blobs=true 与 https://huggingface.co/api/models/sudo-ai/zero123plus-v1.2/tree/main?recursive=true
- 24 GB 卡 OOM 报告 —— https://github.com/TencentARC/InstantMesh/issues/126 、https://github.com/TencentARC/InstantMesh/issues/23
- 元数据 —— `gh api repos/TencentARC/InstantMesh`，2026-10-24

## 9. 未确认事项

1. **显存实测值与耗时**——README 不给显存也**不给任何耗时数字**（查不到），只能引用 issue 报告（24 GB 卡 OOM）；16 GB 上的真实峰值**未实测**。（来源：本卡 §8 证据清单）
2. **NVIDIA 头的 19 个文件到底能不能用**——按文件头是禁止再分发的，但它来自 NVlabs 的开源项目（FlexiCubes/DMTet 本身有 MIT/Apache 版本）；**未逐文件核上游许可**，一律按"只读思想"处理。（来源：本卡 §8 证据清单）
3. **HF 模型卡条款**——是否在 Apache-2.0 之外叠加限制，**未核**。
4. **Zero123++ 权重许可**——**未核**。
5. **base/large 四个变体的质量差**——仓库内无论文结果表，**未核**。
6. **star / 推送时间会变**——取数日 2026-10-24（`gh api`）。
