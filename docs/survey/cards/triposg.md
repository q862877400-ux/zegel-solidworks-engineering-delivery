# TripoSG

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/VAST-AI-Research/TripoSG ｜ 项目页 https://yg256li.github.io/TripoSG-Page/ ｜ 权重 https://huggingface.co/VAST-AI/TripoSG ｜ 报告 https://arxiv.org/abs/2502.06608 ｜ 在线 demo https://huggingface.co/spaces/VAST-AI/TripoSG |
| 许可 | **根仓 MIT，但内部夹着腾讯社区许可——实际是"MIT 外壳 + 受限内核"**。根 `LICENSE:1,3` 原文「MIT License / Copyright (c) 2025 VAST-AI-Research and contributors.」⇒ 表面可商用。★三处例外必须逐条读：① `triposg/LICENSE:1` 是《TENCENT HUNYUAN FLASHVDM COMMUNITY LICENSE AGREEMENT》，同样带**地域排除（欧盟/英国/韩国）**（`triposg/LICENSE:3,17`）与 MAU 门槛（`triposg/LICENSE:30`）；② 扩散主干文件头内嵌《TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT》全文（`triposg/models/transformers/triposg_transformer.py:1-91`，第 91 行明写「the use of this code is subject to the terms … including the Acceptable Use Policy」）；③ `NOTICE:6-15` 声明含 RMBG（bria-rmbg-1.4）、Diffusers（Apache-2.0）、HunyuanDiT、FlashVDM ⇒ **实际可用范围由最严的那份决定** |
| 元数据 | 1859 stars · 最近推送 2025-04-18T06:58:52Z · Python（来源：`gh api repos/VAST-AI-Research/TripoSG`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\VAST-AI-Research__TripoSG（HEAD `fc5c409`「Update README.md」2025-04-18；shallow clone，`git rev-list --count HEAD` = 1）|
| 证据等级 | 读码（通读 `README.md` / `LICENSE` / `NOTICE` / `triposg/LICENSE` / `requirements.txt` / `scripts/inference_triposg.py` / `scripts/inference_vae.py` / `triposg/pipelines/pipeline_triposg.py` / `triposg/inference_utils.py`；**未装依赖、未下权重、未推理**）|

## 1. 一句话定位

VAST 的**图像→纯几何网格**基础模型：1.5B 参数的 Rectified Flow Transformer 在**2048 个 latent token** 的向量集（vecset）上生成 SDF 隐码，再由以 SDF+法向+程函损失混合监督训练的 VAE 解成连续 SDF 场，最后用**稀疏八叉树分级抽样 + 等值面抽取**落成三角网格（`README.md:17,29-31,36`）。**没有纹理分支**。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      单图；先用 BRIA RMBG 去背，缩放到 518²、灰底合成
          scripts/inference_triposg.py:33,88-89；scripts/image_process.py
              ↓
条件编码  DINOv2（transformers 的 Dinov2Model + BitImageProcessor）
          取 last_hidden_state 当图像 token；无条件分支用全零 embeds
          triposg/pipelines/pipeline_triposg.py:138-149
              ↓
中间表示  vecset latent：(batch, 2048, C) 的随机高斯取初值
          pipeline_triposg.py:151-174,182
              ↓
生成      Rectified Flow：FlowMatchEulerDiscreteScheduler，
          默认 50 步、guidance 7.0；CFG 靠 batch 翻倍后 chunk 相减
          pipeline_triposg.py:181,184,219-220,244-275
              ↓
解码      VAE 的 decoder 当"可查询的 SDF 函数"：给点返回 SDF
          geometric_func = vae.decode(latents, sampled_points=x).sample
          pipeline_triposg.py:299
              ↓
抽面      两条路：① hierarchical —— 先 2^8 稠密网格全查，只在 |SDF|<1.0 的带内用
          max_pool3d 膨胀后加密，逐级到 2^9，末尾 skimage marching_cubes(level=0, lewiner)
          ② flash —— 多分辨率分块查询 + diso 的 DiffDMC；默认走 ②（use_flash_decoder=True）
          inference_utils.py:129-201,170,193,319-472,324,469；pipeline_triposg.py:195,307-314
              ↓
编排      single —— 一条 pipeline 直下；可选后处理只有"减面"
          脚本层用 pymeshlab 二次误差边坍缩降到指定面数
          scripts/inference_triposg.py:59-66
              ↓
验证      visual —— **仓内无任何几何指标代码**（无 Chamfer / IoU / 水密断言），
          质量靠人眼与 demo 图 README.md:21-24
              ↓
交付      mesh —— trimesh.Trimesh 落 GLB（默认 ./output.glb）
          scripts/inference_triposg.py:41,74,103
```

★ **网络结构**：**Rectified Flow Transformer（非 DDPM、非前馈回归）**——`TripoSGDiTModel` + `FlowMatchEulerDiscreteScheduler`（`pipeline_triposg.py:12-13,95-116`）；**无纹理分支**（全仓 `texgen`/`texture` 相关模块为 0，产物只有几何）；**输出格式 GLB**（`scripts/inference_triposg.py:74`），无 OBJ/PLY 出口。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（只写机制，不贴代码） | 出处 |
|---|---|---|---|
| 1 | **VAE 当"可查询 SDF"用** | 解码器不一次吐体素，而是给一批查询点返回 SDF 值 ⇒ 分辨率由查询策略决定，不写死 | `pipeline_triposg.py:299`、`inference_utils.py:161` |
| 2 | **只在表面附近加密** | 第一级全查 2^8；用 \|SDF\|<1.0 选带，3D max_pool 膨胀成"边缘区"，再只在那些格点查高分辨率 | `inference_utils.py:163-189`、`:72-98` |
| 3 | **膨胀核随分辨率变** | 粗网格(≥512)用 3×3×3、细网格用 5×5×5 的 max_pool 核，保证带宽至少一格 | `inference_utils.py:103-108` |
| 4 | **两级解码器可切换** | 慢但零编译依赖的 skimage 路径 vs 快但要 `diso` 的 FlashVDM 路径，开关在 pipeline 参数上 | `pipeline_triposg.py:195,298-314` |
| 5 | **失败就交空网格而不是崩** | 抽面整段包在 try 里，异常时打信息 + 清缓存并返回 `(None, None)` | `inference_utils.py:190-201` |
| 6 | **减面用二次误差边坍缩** | 先合并重合顶点再坍缩到目标面数，只在超目标时才动 | `scripts/inference_triposg.py:59-66` |
| 7 | **CFG 用 batch 拼而不是两次前向** | 把正负条件 cat 成一个 batch 跑一次，再 chunk 相加，省一次调度开销 | `pipeline_triposg.py:219-220,248-269` |
| 8 | **归一化边界固定 ±1.005** | 生成与 VAE 编码两侧用同一 bbox，避免单位不一致导致的缩放误差 | `pipeline_triposg.py:191`、`scripts/inference_vae.py:54` |

## 4. 可跑性与实测方案

| 项 | 数值 / 结论 | 出处 |
|---|---|---|
| 显存（官方明称） | **至少 8 GB** | `README.md:85` |
| Python / CUDA | 建议 conda python=3.10；torch 按 CUDA 版本自装 | `README.md:48,55` |
| 关键依赖 | `numpy==1.22.3`（钉死）、`diso`、`pymeshlab`；完整 VAE 编码器另需 `torch-cluster` | `requirements.txt:9,13,14`、`README.md:89` |
| 权重体积 | `VAST-AI/TripoSG` 16 文件 **7.40 GB**（transformer 5491.5 MB + VAE 925.7 MB + DINOv2 1161.1 MB）；另需 RMBG-1.4 共 **803.2 MB**（`model.pth` 168.5 MB） | https://huggingface.co/api/models/VAST-AI/TripoSG/tree/main?recursive=true ；https://huggingface.co/api/models/briaai/RMBG-1.4/tree/main?recursive=true |
| 参数量 / 数据 | 主干 1.5B；latent token 2048；训练用 200 万对 image–SDF | `README.md:36`、`pipeline_triposg.py:182`、`README.md:30` |
| 单样本耗时 | **查不到**（README 与脚本均未给秒数） | — |

**本机判定（Windows / Python 3.14.7 / RTX 4080 SUPER 16 GB —— 机器事实来源：本机 `nvidia-smi --query-gpu=memory.total` 16376 MiB 与 `python --version`，取数日 2026-10-24）**

- 显卡实测 16376 MiB（来源：本机 `nvidia-smi --query-gpu=memory.total`，2026-10-24）⇒ 官方 8 GB 要求（`README.md:85`）下有约一倍余量，**显存不是问题**。
- **真正的卡点在 import 期**：`inference_utils.py:7` 是**无条件的 `from diso import DiffDMC`**，而 `pipeline_triposg.py:19` 又无条件 import 它 ⇒ 即使把 `use_flash_decoder` 关掉走 skimage 路，**装不上 `diso` 就整个包 import 不进来**。`diso` 最新 0.1.4 在 PyPI 只有 1 个文件、**无 Windows 轮**（来源：https://pypi.org/pypi/diso/json）⇒ 必须现场编 CUDA 扩展；本机 CUDA Toolkit 13.3（来源：本机 `$env:CUDA_PATH`）需与 torch 自带 CUDA 主版本对齐。
- `numpy==1.22.3` 的 Windows 轮只到 cp310（来源：https://pypi.org/pypi/numpy/1.22.3/json 的 win 文件名仅 cp38/cp39/cp310）⇒ 本机默认 3.14 装不上，必须改用本机已有的 3.10.21（来源：本机 `py -0` 列表）或松开这个钉版。
- 结论：**理论上能跑（官方要 8 GB，`README.md:85`，本卡 16 GB 有余），但 import 期被 `diso` 挡住，未实测**。若跑，最小命令与预期：
  `python -m scripts.inference_triposg --image-input assets/example_data/hjswed.png --output-path ./output.glb`（`README.md:65`），预期得到 `output.glb`（`scripts/inference_triposg.py:74,103`）；想控面数加 `--faces 5000`（`README.md:70`）。
- 盘开销：权重 7.40 GB + 0.80 GB ≈ 8.2 GB（来源：两个 HF 列表 API）；本机 D: 余 2.76 TB（来源：本机 `Get-PSDrive D`）。**全程只读码，未下载、未安装。**

## 5. 失败模式与已知坑

1. **`diso` 是硬 import**：`inference_utils.py:7` 与 `pipeline_triposg.py:19` 都是顶层导入 ⇒ 「关掉 flash decoder 就不用 diso」这个直觉**不成立**，装不上就直接 ImportError，且报错指向 `inference_utils` 而不是"你缺一个可选依赖"。
2. **钉死的老 numpy**：`requirements.txt:9` 写 `numpy==1.22.3`，该版本 Windows 轮只到 cp310（PyPI JSON）⇒ 在 3.11+ 上会尝试源码编译，通常在 `_multiarray_umath` 阶段失败。
3. **抽面失败是静默的**：异常被吞、返回 `(None, None)`（`inference_utils.py:196-199`），随后脚本层对 `None` 建 `trimesh.Trimesh` 会炸在别处，错误信息与真因脱节。
4. **`expand_edge_region_fast` 写死 `device='cuda'`**（`inference_utils.py:101`）⇒ 无 CUDA 环境下连 CPU 回退都没有。
5. **README 有个排版笔误**：权重清单第 2 条以 `=` 开头（`README.md:80`）；另外**几何质量无自动判据**——README 只讲"高保真/鲁棒"（`README.md:21-24`），面数、孔洞、自交全靠人看。

## 6. 对我方目标的可用处（机制层面，含**边界**）

我方目标是**让普通模型建出能用、规范的参数化模型（SolidWorks）**。TripoSG 是四家里**最纯粹的"几何只有几何"**，因此边界最干净：

- ✅ **能用它的地方（视觉/参考级）**
  1. **概念外观**：单图→GLB 的裸几何，没有纹理反而适合当"形体草图"看体量与结构（`README.md:65`）。
  2. **面数可控的参考网格**：`--faces` 直接给目标面数（`README.md:70`），做轻量参考件时不用自己再减面。
  3. **反向渲染校验**：把我方参数化模型渲成正/俯/侧图，与它的生成轮廓比对，作为"语义是否对"的弱校验。
- ✅ **可迁移的机制（这是本卡最值钱的部分）**
  - **"解码器当可查询函数 + 分级加密"**（`inference_utils.py:129-201`）：把"生成分辨率"从模型里拿出来，变成查询策略。我方逆向管线要定位特征区时，完全可以照抄这套"粗扫 → 按阈值选带 → 膨胀 → 局部加密"，把算力花在表面附近。
  - **两条抽面路径的取舍设计**（`pipeline_triposg.py:195,298-314`）：快路依赖编译件、慢路零依赖，开关放在 API 上而不是编译选项上——**给小机器留一条"能跑但慢"的路**，这个设计对我方工具链（不同客户机器）直接可搬。
  - **减面只做"必要的那一刀"**（`scripts/inference_triposg.py:59-66`）：先判是否超目标，再合并重合顶点、再坍缩，避免无谓的质量损失。
- ❌ **不能拿它做的事（硬边界）**
  - **不能当 CAD 数据源**：输出是 marching-cubes / DMC 面片，无特征、无草图、无尺寸、无基准；SolidWorks 里只是 graphics body。
  - **不能当尺寸真相**：无 Chamfer/IoU/水密判据（`README.md:21-24` 只有定性描述），"多大多直"无保证。
  - **不能拿纹理/材质**：本仓**没有纹理分支**，连顶点色都不写（`scripts/inference_triposg.py:41` 只传 vertices/faces）。
  - **不能替代参数化建模**：它解决"像不像"，我方要"改不改得动"。

## 7. 许可与红线

- **不能只看根 LICENSE**：根是 MIT（`LICENSE:1,3`），但 `triposg/` 目录下另有一份腾讯 FlashVDM 社区许可（`triposg/LICENSE:1`），扩散主干文件头内嵌腾讯 Hunyuan 社区许可全文（`triposg/models/transformers/triposg_transformer.py:1-91`），`NOTICE:6-15` 还挂了 RMBG（bria-rmbg-1.4，通常是**非商用**条款）与 Apache-2.0 的 Diffusers。
- **地域与规模限制继承下来了**：FlashVDM 社区许可把适用域限定为「全球**除**欧盟、英国、韩国」（`triposg/LICENSE:3,17`），域外使用无授权（`triposg/LICENSE:37`）；MAU > 100 万须另申请（`triposg/LICENSE:30`）。
- **红线**：① 只搬机制不搬代码（我方的口径：非 MIT/Apache 的**整体**按只读思想处理，即使局部是 MIT）；② 不引用其权重做可分发物；③ 若客户在欧盟/英国/韩国，连"生成参考图"都缺授权；④ 引用 RMBG 做去背时，RMBG 自己的条款要单独核（本卡未核到原文，`查不到`）。
- 若确要复用其 MIT 部分，`NOTICE:2` 的版权行「Copyright (c) 2025 VAST-AI-Research and contributors」必须保留。

## 8. 证据清单

- `LICENSE:1,3` + `triposg/LICENSE:1,3,17,30,37` + `NOTICE:2,6-15` —— 根 MIT / 内层 FlashVDM 社区许可（地域、MAU、域外无授权）/ 第三方组件
- `triposg/models/transformers/triposg_transformer.py:1-91` —— 内嵌的《TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT》全文与适用声明
- `README.md:17,21-24,29-31,30,36,48,55,65,70,80,85,89` + `requirements.txt:9,13,14` —— 一句话定位、四点卖点、SDF 混合监督、200 万对数据、1.5B/2048 token、conda py3.10、torch 自装、运行命令、--faces、排版笔误、8 GB、torch-cluster 说明、numpy==1.22.3 / diso / pymeshlab
- `triposg/pipelines/pipeline_triposg.py:12-13,95-116,138-149,151-174,181,182,184,191,195,219-220,244-275,298-314,315` —— flow matching + Euler 调度、DINOv2 条件、latent 形状、50 步、2048 token、guidance 7.0、±1.005、flash 开关、CFG batch 拼接、去噪循环、两条抽面路径、trimesh 构造
- `triposg/inference_utils.py:7,72-98,101,103-108,129-201,170,190-201,193,319-472,324,469` —— 顶层 import diso、选带函数、写死 cuda、膨胀核、分级解码、band_threshold、异常兜底、lewiner marching cubes、flash 路径、mc_level、dmc
- `scripts/inference_triposg.py:33,41,59-66,74,88-89,103` + `scripts/inference_vae.py:54` —— 预处理、trimesh 构造、减面、默认输出名、权重下载、导出、±1.005 边界
- https://huggingface.co/api/models/VAST-AI/TripoSG/tree/main?recursive=true —— 16 文件 / 7.40 GB / 分项 5491.5 + 925.7 + 1161.1 MB
- https://huggingface.co/api/models/briaai/RMBG-1.4/tree/main?recursive=true —— 803.2 MB / model.pth 168.5 MB
- https://pypi.org/pypi/diso/json + https://pypi.org/pypi/numpy/1.22.3/json —— diso 0.1.4 仅 1 个文件、无 Windows 轮；numpy 1.22.3 的 Windows 轮仅 cp38/cp39/cp310
- https://github.com/VAST-AI-Research/TripoSG —— 仓库页（stars / pushed_at 经 `gh api` 复核）

## 9. 未确认事项

1. **单样本耗时**：README 与脚本均未给秒数，`查不到`；本机未跑。
2. **`diso` 在本机 CUDA 13.3 下能否编过**：未验；这是"能不能跑"的唯一决定性因素。
3. **RMBG-1.4 的确切许可条款**：`NOTICE:6-9` 只给标识符 `bria-rmbg-1.4` 与来源链接，条款原文不在克隆里，`查不到`。
4. **去背与几何质量**：`scripts/inference_triposg.py:33` 把去背写进主流程，但 pipeline 本身只要一张图，不去背的质量损失 `查不到`；仓内也无任何孔洞/自交检查代码，只能自跑并上 `trimesh.is_watertight` 才知道。
