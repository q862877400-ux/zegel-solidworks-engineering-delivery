# Hunyuan3D-2

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/Tencent/Hunyuan3D-2 ｜ 主页 https://3d.hunyuan.tencent.com ｜ 权重 https://huggingface.co/tencent/Hunyuan3D-2 ｜ 报告 https://arxiv.org/abs/2501.12202 |
| 许可 | **自定义社区许可，非 OSI / 无 SPDX 号**（记作 `LicenseRef-Tencent-Hunyuan-3D-2.0-Community`）：`LICENSE:1` 原文「TENCENT HUNYUAN 3D 2.0 COMMUNITY LICENSE AGREEMENT」，版权行 `LICENSE:28`「Copyright © 2025 Tencent. All Rights Reserved.」。★三条硬限制：① **地域**——欧盟/英国/韩国不适用（`LICENSE:3`、`LICENSE:18`），域外使用「unlicensed and unauthorized」（`LICENSE:39`）；② **MAU 门槛**——发布日前一个月活跃用户 > 100 万须另行向 Tencent 申请（`LICENSE:32`）；③ **禁止反哺其它 AI 模型**（`LICENSE:38`）。分发须随附协议全文（`LICENSE:25`）+ 固定 Notice 文本（`LICENSE:28`），改过的文件须显著标注（`LICENSE:26`）。★仓库内另有一处自相矛盾，见 §7 |
| 元数据 | 15189 stars · 最近推送 2025-10-28T09:58:12Z · Python（来源：`gh api repos/Tencent/Hunyuan3D-2`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\Tencent-Hunyuan__Hunyuan3D-2（HEAD `f8db630`「Update LICENSE」2025-10-28；shallow clone，`git rev-list --count HEAD` = 1）|
| 证据等级 | 读码（通读 `README.md` / `LICENSE`（82 行）/ `docs/source/modelzoo.md` / `hy3dgen/shapegen/` 下 pipelines·postprocessors·surface_extractors·volume_decoders·conditioner / `hy3dgen/texgen/pipelines.py`；**未装依赖、未下权重、未推理**）|

## 1. 一句话定位

腾讯的两段式**图像→带纹理网格**大模型：先用 Hunyuan3D-DiT（flow-matching 扩散 Transformer）从图里生成 vecset 隐码，解码成 SDF 体素场后抽等值面得裸网格；第二段 Hunyuan3D-Paint 用多视角扩散给网格上色烘 UV（`README.md:72-78`、`README.md:96-98`）。产物是 `trimesh.Trimesh`，落 GLB/OBJ（`README.md:202-203`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入/编码 单图（可带 mask）或 2mv 多视角；去背居中 padding 后进双条件塔
          （CLIPImageEncoder + DinoImageEncoder 经 DualImageEncoder 并联）
          hy3dgen/shapegen/preprocessors.py；conditioner.py:120,127,134,214
              ↓
中间表示  vecset latent（DiT 在隐空间去噪）；VAE 把 latent 解成体素 SDF logits
          hy3dgen/shapegen/pipelines.py:659-670
              ↓
生成      Hunyuan3DDiTFlowMatchingPipeline：flow matching，sigmas = linspace(0,1,N)；
          默认 50 步、guidance 5.0；dual_guidance 分支按 CLIP/DINO 两路加权
          pipelines.py:686,690,725,753-755,622-632
              ↓
抽面/后处理 octree_resolution=384、mc_level=0.0；三档体积解码器 Vanilla/Hierarchical/FlashVDM
          → MC（skimage，lewiner）或 DMC（diso）抽面；随后二次误差边坍缩简化 + 去碎片
          volume_decoders.py:141,185,280；surface_extractors.py:67,79,97-100
          pipelines.py:693-694；postprocessors.py:37-51,54-59
              ↓
纹理分支  Hunyuan3D-Paint：xatlas UV 展开 → 渲染 normal/position 多视角图 →
          多视角扩散补全 → 按 cos 权重烘到 UV（bake_exp=4）→ UV 空洞 inpaint
          hy3dgen/texgen/pipelines.py:46,207,214-222,229-238
              ↓
验证      visual —— 仓内只有 CMMD/FID/CLIP-score 这类图像级指标（README.md:110-116），
          **无 Chamfer / 无 IoU / 无水密性检查**
              ↓
交付      mesh —— trimesh 落 glb/obj；api_server.py:289 固定 {uid}.glb，
          gradio_app.py:106-110 分 textured_mesh.glb / white_mesh.glb
```

★ **网络结构与分支**：形状是 **flow-matching 扩散 Transformer**（非前馈回归）——`Hunyuan3DDiTPipeline`（`pipelines.py:135`）与 `Hunyuan3DDiTFlowMatchingPipeline`（`pipelines.py:680`）两个入口并存；**有独立纹理分支**，且可单独作用于别人给的网格（`README.md:219-221`）。输出格式 **GLB / OBJ**（`README.md:202-203`），无 PLY 出口。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **形状/纹理解耦成两个模型** | 先裸网格再上色，纹理段接受任意手作网格 ⇒ 纹理能力可单独复用 | `README.md:96-98`、`README.md:219-221` |
| 2 | **双条件塔并联 + 双引导** | CLIP 语义 + DINOv2 几何两路各算一个预测，再按两个 scale 叠加 | `conditioner.py:214`、`pipelines.py:622-632` |
| 3 | **分级体积解码** | 先粗网格全量查一遍，只在 \|SDF\| 小的带内插值加密，逐级翻倍分辨率 | `volume_decoders.py:185-268` |
| 4 | **FlashVDM 变体** | 同思路但把下一级查询点先在低分辨率网格分箱去重，减少重复查询 | `volume_decoders.py:280-413` |
| 5 | **抽面算法可切换** | `mc`（skimage，无编译依赖）/ `dmc`（diso，可微）二选一，字典注册 | `surface_extractors.py:97-100` |
| 6 | **简化时显式保拓扑** | 二次误差边坍缩开 `preservenormal` / `preservetopology` / `preserveboundary`，边界权重 3 | `postprocessors.py:41-50` |
| 7 | **去碎片先选后删** | 先按面数占比 0.005 选小连通块，面→点转换后再删点面 | `postprocessors.py:54-58` |
| 8 | **烘 UV 用 cos 权重** | 多视角投影到 UV 时按视角余弦加权并取 `bake_exp` 次幂，抑制掠射角糊化 | `texgen/pipelines.py:46,136` |
| 9 | **失败可见** | 抽面异常时打 traceback 并把该样本置 None，不断整批 | `surface_extractors.py:52-62` |

## 4. 可跑性与实测方案

| 项 | 数值 / 结论 | 出处 |
|---|---|---|
| 显存（官方明称） | **6 GB** 只做形状；**16 GB** 形状+纹理 | `README.md:126` |
| 显存（文档冲突） | 同一仓另一处写 **24.5 GB** | `docs/source/modelzoo.md:3` |
| Python / CUDA | 不钉版本；requirements 列 torch/torchvision 由用户按 pytorch.org 自装；纹理两段自编译需 nvcc | `requirements.txt:1-5`、`README.md:175-186` |
| 权重体积 | `tencent/Hunyuan3D-2` 整仓 112 文件 **69.74 GB**；单份 v2-0 权重仅 **4699.9 MB**（同目录 ckpt/safetensors/fp16 共 5 份副本 ⇒ 该子目录合计 22.95 GB） | https://huggingface.co/api/models/tencent/Hunyuan3D-2/tree/main?recursive=true |
| 小模型替代 | `tencent/Hunyuan3D-2mini` 每个 DiT 子目录 7.12 GB、mini VAE 0.76 GB | https://huggingface.co/api/models/tencent/Hunyuan3D-2mini/tree/main?recursive=true |
| 参数量 | DiT-v2-0 1.1B；Paint-v2-0 1.3B | `README.md:158`、`README.md:159` |
| 单样本耗时 | **查不到**（README 与 docs 均未给推理秒数） | — |

**本机判定（Windows / Python 3.14.7 / RTX 4080 SUPER 16 GB —— 机器事实来源：本机 `nvidia-smi --query-gpu=memory.total` 16376 MiB 与 `python --version`，取数日 2026-10-24）**

- 显卡实测 16376 MiB（来源：本机 `nvidia-smi --query-gpu=memory.total`，2026-10-24）⇒ 形状分支 6 GB 有余量；纹理分支 16 GB **正压线**，无余量跑 batch>1。
- `torch` 2.14.1 已有 Windows `cp314` 轮（来源：https://pypi.org/pypi/torch/json 的 `torch-2.14.1-cp314-cp314-win_amd64.whl`）⇒ 任务书「Py3.14 缺 torch 轮」这条**在 2026-10-24 已不成立**；真正卡住的是**自编译 CUDA 扩展**，不是 torch 本身。
- 纹理分支要 `python3 setup.py install` 编 `custom_rasterizer` 与 `differentiable_renderer`（`README.md:181-186`）；本机 CUDA Toolkit 13.3（来源：本机 `$env:CUDA_PATH`）与 PyTorch 轮自带的 CUDA 主版本不一致 ⇒ **形状分支可试，纹理分支不建议试**。
- 结论：**能跑（仅形状分支），未实测**。最省的做法是 mini + 低显存：`python gradio_app.py --model_path tencent/Hunyuan3D-2mini --subfolder hunyuan3d-dit-v2-mini --low_vram_mode`（`README.md:231`）。
- 最小验证串：把权重放本地并把 `from_pretrained` 指向本地目录（默认走 HF 在线拉取，`minimal_demo.py:8`），跑 `python minimal_demo.py`，预期输出 `demo.glb`（`minimal_demo.py:33`）。
- 盘开销：单份 DiT 权重 4699.9 MB + VAE 子目录 0.80 GB ≈ 5.5 GB 量级（来源：https://huggingface.co/api/models/tencent/Hunyuan3D-2/tree/main?recursive=true）；本机 D: 余 2.76 TB（来源：本机 `Get-PSDrive D`）。**全程只读码，未下载、未安装。**

## 5. 失败模式与已知坑

1. **文档自相矛盾**：显存 16 GB（`README.md:126`）vs 24.5 GB（`docs/source/modelzoo.md:3`）——规划机器要按大的算。
2. **纹理分支在 Windows 上是编译赌局**：两个 CUDA 扩展要源码编译（`README.md:181-186`）；官方自己反而在致谢里给社区「Windows 安装工具 / 整合包」链接（`README.md:331`）⇒ 主仓没把 Windows 当一等公民，尽管 `README.md:165` 声称支持。
3. **抽面失败是静默降级**：异常被吞成 `None` 继续下一批（`surface_extractors.py:59-62`），批量跑只看到少了一个结果，看不到原因。
4. **拓扑只「保」不「修」**：开 `preservetopology=True`（`postprocessors.py:48`）意思是「别弄坏」，不等于输出无自交/无翻面；`Select-String 'watertight|manifold'` 在 `hy3dgen/` 下 0 命中。
5. **按目录整体下载是纯浪费**：69.74 GB 里单份权重只 4.7 GB，其余是格式副本（来源：https://huggingface.co/api/models/tencent/Hunyuan3D-2/tree/main?recursive=true）。
6. **uv 展开依赖 xatlas**：`xatlas` 0.0.11 有 win_amd64 轮但只到 cp313（来源：https://pypi.org/pypi/xatlas/json）⇒ 本机若坚持 3.14 需换 3.12 解释器。

## 6. 对我方目标的可用处（机制层面，含**边界**）

我方目标是**让普通模型建出能用、规范的参数化模型（SolidWorks）**。这批项目的产物是三角网格，**结构上进不了参数化特征树**——边界必须先说清：

- ✅ **能用它的地方（只有三处，且都是「视觉/参考」级）**
  1. **概念外观**：把「用户脑子里的形状」先渲成图给评审锁体量与比例，再让参数化脚本照着建。它产出的**不是**模型数据，是**参考图**。
  2. **参考图/正交视图回灌**：从生成网格渲正/俯/侧三视图，作为草图输入素材（渲染与导出路径现成：`gradio_app.py:106-110`）。
  3. **反向渲染校验**：我方建好的参数化模型渲一张，与生成图做轮廓/剪影比对，作为「语义是否对」的**弱校验**——只能证伪「形状跑偏」，不能证明尺寸对。
- ✅ **可迁移的机制（这几条才是真正的收获）**
  - **只在有信息的地方加密**：`volume_decoders.py:185-268` 的分级解码（粗网格全扫 → \|SDF\| 小的带内才插值翻倍）是通用的由粗到细采样策略，可搬到逆向管线「先粗定位特征区，再局部加密」。
  - **简化时把拓扑约束显式打开**（`postprocessors.py:41-50`）：任何网格降面步骤都该带 `preservetopology/preservenormal/preserveboundary` 与边界权重，可直接搬进我方网格工具。
  - **去碎片先「选」再「删」**（`postprocessors.py:54-58`）：先用面数占比阈值挑出小连通块，再转顶点选择后删，比按体素直接删干净。
- ❌ **不能拿它做的事（硬边界）**
  - **不能当 CAD 数据源**：输出是 marching-cubes 三角面片，无草图、无特征、无尺寸、无基准；SolidWorks 打开只是 graphics body / 网格体，改不了尺寸、出不了带公差的工程图、加不了装配约束。
  - **不能当尺寸真相**：全仓无 Chamfer/IoU/水密判据（`README.md:110-116` 只有图像级指标），生成物「多大、多直、多同心」无任何数值保证。
  - **不能替代参数化建模**：它的强项是「像」，我方要的是「准且可改」，两者不重叠。

## 7. 许可与红线

- **不是 MIT/Apache，也没有 SPDX 号**：`LICENSE:1` 是自定义《TENCENT HUNYUAN 3D 2.0 COMMUNITY LICENSE AGREEMENT》，任何「当开源库直接抄」的做法不成立。
- **★仓库内自相矛盾（如实记录，不下结论）**：`hy3dgen/` 下 45 个 `.py` 文件头写的是「TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT」（例：`hy3dgen/shapegen/postprocessors.py:1`、`hy3dgen/texgen/pipelines.py:1`、`hy3dgen/__init__.py:1`；计数来源：`Select-String 'NON-COMMERCIAL' hy3dgen -r` = 45 个文件），而根 `LICENSE:1` 是 Community 版；同一文件头第 13 行又写「in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT」。**两个说法并存，仓库没解释哪个生效** ⇒ 我方按最严读法处理（视同不可商用）。
- **红线**：① 不抄代码进我方仓库（AGENTS.md 铁律 6：非 MIT/Apache 只读思想）；② 不引用其权重做任何可分发物；③ 地域条款排除欧盟/英国/韩国，客户在这些地区则连「生成参考图」都缺授权。
- 仓库内 `NOTICE` 32279 字节是 Tencent 自己的第三方组件声明，不是我方的合规凭据。

## 8. 证据清单

- `LICENSE:1,3,18,25,26,28,32,38,39,53` —— 许可名称、地域排除、Territory 定义、随附义务、改动标注、Notice 文本、MAU 门槛、禁止反哺、域外无授权、香港法管辖
- `hy3dgen/shapegen/postprocessors.py:1`、`hy3dgen/texgen/pipelines.py:1`、`hy3dgen/__init__.py:1` —— 「NON-COMMERCIAL」文件头（与根 LICENSE 冲突）
- `README.md:72-78,96-98,110-116,126,158,159,165,175-186,202-203,219-221,231,331` —— 两段式架构、图像级指标、6 GB/16 GB、参数量、声称支持 Windows、自编译步骤、glb/obj、纹理可作用于手作网格、低显存命令、社区 Windows 整合包
- `docs/source/modelzoo.md:3` —— 24.5 GB（与 README 冲突）
- `hy3dgen/shapegen/models/conditioner.py:120,127,134,214` —— CLIP / DINOv2 / 多视角 DINO / Dual 条件塔
- `hy3dgen/shapegen/pipelines.py:135,680,686,690,693,694,725,622-632,659-670` —— 两个入口、50 步、guidance 5.0、octree 384、mc_level 0.0、sigmas、双引导加权、latent 解码
- `hy3dgen/shapegen/models/autoencoders/surface_extractors.py:52-62,67,79,97-100` + `volume_decoders.py:141,185-268,280-413` —— 抽面两条路 / 异常吞成 None / 三档体积解码器
- `hy3dgen/shapegen/postprocessors.py:37-51,54-59` + `hy3dgen/texgen/pipelines.py:46,136,207,214-222,229-238` —— 简化保拓扑 / 去碎片 / xatlas UV / cos 权重烘图 / 多视角扩散 / inpaint
- `api_server.py:289`、`gradio_app.py:106-110`、`minimal_demo.py:8,33`、`requirements.txt:1-5`
- https://huggingface.co/api/models/tencent/Hunyuan3D-2/tree/main?recursive=true —— 112 文件 / 69.74 GB / 单文件 4699.9 MB / 子目录 22.95 GB
- https://huggingface.co/api/models/tencent/Hunyuan3D-2mini/tree/main?recursive=true —— mini DiT 7.12 GB / VAE 0.76 GB
- https://pypi.org/pypi/torch/json + https://pypi.org/pypi/xatlas/json —— torch 2.14.1 有 `cp314` win_amd64 轮；xatlas 0.0.11 win_amd64 只到 cp313
- https://github.com/Tencent/Hunyuan3D-2 —— 仓库页（stars / pushed_at 经 `gh api` 复核）

## 9. 未确认事项

1. **单样本推理时间**：README/docs 均未给秒数，`查不到`；要做「预计耗时」必须实测（本机未跑）。
2. **`requirements.txt` 未钉 torch 版本**（只写 `torch`），用哪个 CUDA 主版本编的 wheel `查不到`；纹理两段扩展在本机 CUDA 13.3 下能否编过，未验。
3. **「NON-COMMERCIAL」文件头 vs Community 根许可哪个生效**：仓库无说明，`查不到`；只能按严处理，需法务确认。
4. **16 GB vs 24.5 GB 哪个是真的**：`README.md:126` 与 `docs/source/modelzoo.md:3` 两处官方文档冲突，`查不到`哪个更新；未实测。
5. **抽面失败率与网格质量**：全仓无统计口径也无水密/自交检查，`查不到`；要自跑一批图统计 `None` 比例，并上 `trimesh.is_watertight` / `is_winding_consistent` 才知道。
