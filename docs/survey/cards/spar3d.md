# SPAR3D

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/Stability-AI/stable-point-aware-3d ｜ 项目页 https://spar3d.github.io/ ｜ 论文 https://arxiv.org/abs/2501.04689 ｜ 权重 https://huggingface.co/stabilityai/stable-point-aware-3d（**门控**）|
| 许可 | **Stability AI Community License Agreement**（`LICENSE.md:1-2`「Last Updated: July 5, 2024」）——★**不是** MIT（`gh api` 的 `license.spdx_id` 是 `NOASSERTION`）。与同门 SF3D 那份同版同结构（关键条款行号一致：`:10` 营收门槛、`:22` 注册与终止、`:27` 三条分发义务），逐行对比只有 Section I 等处若干措辞微差。要点见 §7 |
| 元数据 | 1083 stars · 最近推送 2025-05-05T16:44:13Z · Python（来源：`gh api repos/Stability-AI/stable-point-aware-3d`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\Stability-AI__stable-point-aware-3d |
| 证据等级 | 读码（通读 `run.py` / `spar3d/system.py`（921 行，重点 100-160、428-560、562-760）/ `spar3d/models/{mesh,isosurface}.py` / `tokenizers/point.py` / `transformers/point_diffusion.py` / `diffusion/*` / `requirements*.txt` / `LICENSE.md`；**未安装、未下权重、未推理**）|

## 1. 一句话定位

**SF3D + 一层点云扩散**：先由扩散模型从单图**生成 512 个带色点**（或用你给的点云替换它），再以"图 + 点云"为条件回归三平面、marching-tet 出网格并烘 PBR 贴图（`README.md:19`）。它相对 SF3D 的唯一实质升级是：**中间表示变成了可编辑的点云**——背面糊的时候你可以自己补点。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      一张 RGBA 图；用 transparent-background 去背 + 前景比 1.3 裁切
                                （`run.py:8, 39-44, 119-128`、`spar3d/utils.py:121`）
    ↓
中间表示  ★两路点云条件（这是它区别于 SF3D 的地方）：
          ① 自动：图 token + 相机嵌入 → 点扩散 transformer 去噪 → 512 点，再做 bbox 归一化
             （`spar3d/system.py:287-288` 的 num_points=512、`:673-700`）
          ② 手动：调用方直接传一个 N×6（xyz+rgb）点云，跳过扩散
             （`spar3d/system.py:566, 673-686`）
    ↓
生成      点云 tokenizer（6 维 → 1024）+ 图 token 一起喂 transformer → 三平面场景码
                                （`spar3d/system.py:506`、`spar3d/models/tokenizers/point.py:12-19`、`system.py:487-560`）
    ↓
几何      density 减阈值当 SDF → Marching Tetrahedra（tet 表 `load/tets/160_tets.npz`，15.4 MB）＋顶点形变
                                （`spar3d/system.py:440-455`、`spar3d/models/isosurface.py:106-113, 205-229`）
    ↓
纹理      自写 C++ UV 展开 → CUDA texture baker 光栅化 → 插值 3D 位置/法线 → 查三平面 →
          解 albedo/roughness/metallic/扰动法线 → 烘 1024² 贴图（默认）
                                （`spar3d/system.py:749-789`、`run.py:51-56`）
    ↓
编排      single —— `run.py` 一次 `run_image` 出全部结果；`gradio_app.py` 额外允许手改点云
    ↓
执行      单卡；CUDA 时 bf16 autocast（`run.py:161-165`）；低显存模式按模块换入换出（§3 #5）
    ↓
验证      visual —— 仓内无几何指标、无测试；只打峰值显存（`run.py:173-174`）
    ↓
交付      mesh —— `.glb`（三角面 + UV + baseColor/法线贴图 + 标量 metallic/roughness）
          ＋ 额外落一份 `points.ply`（中间点云被当成交付物一起给）
                                （`run.py:180-190`、`spar3d/system.py:796-802` 的材质字典）
```

★ 三问定性：**多视图**（否，单图 + 单点云）· **前馈**（几何部分是前馈；点云那级是**64 步扩散采样**，`system.py:107-116`）· **重建式**（是 triplane 等值面式，仍**不是**多视几何求解）。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（不贴代码） | 出处 |
|---|---|---|---|
| 1 | **★ 把中间表示做成可替换的接口** | 点云既是内部产物也是外部输入：有 `pc_cond` 就跳过扩散，没有才生成 ⇒ 生成质量差时人能接管 | `spar3d/system.py:673-700` |
| 2 | **点云扩散的超参显式暴露** | 推理步数 64、guidance 3.0、cosine 噪声表、`sigma_max=120`、`s_churn=3.0` 全在 Config 里 | `spar3d/system.py:107-116` |
| 3 | **点云 bbox 归一化** | 去噪后先统一到单位包围盒再当条件，避免尺度跑飞 | `spar3d/system.py:697` |
| 4 | **点云的 tokenizer 与图的 tokenizer 分离** | 点云走 1D transformer（6→1024，默认 16 层），图走 ViT 系，最后在 backbone 汇合 | `spar3d/models/tokenizers/point.py:12-19`、`spar3d/system.py:506-509` |
| 5 | **低显存的分阶段装载** | 三组模块（主/估计器/点扩散）按阶段 load/unload，权重常驻 CPU 影子副本 | `spar3d/system.py:205-211, 238-297, 355-427` |
| 6 | **低显存切换点放在流程边界** | `get_scene_codes` 进门先换主模块、出门换估计器 ⇒ 换入换出点由调用顺序决定，不用手工调度 | `spar3d/system.py:488-491, 710-713` |
| 7 | **阈值与场解耦** | 几何用 `density − isosurface_threshold`，调阈值不必重训 | `spar3d/system.py:442` |
| 8 | **形变按网格步长归一化** | 位移 = (range/resolution)·tanh(raw)，压在半个体素内防翻面 | `spar3d/models/isosurface.py:106-113` |
| 9 | **UV 展开按面拆点 + 反查烘焙** | 缝线处复制顶点；UV 光栅化后重心插值回 3D 再查场 | `spar3d/models/mesh.py:251-275`、`system.py:766-789` |
| 10 | **输出朝向与光照估计对齐** | 先把最终旋转矩阵算好，估计光照时把同一个旋转传给 `global_estimator` | `spar3d/system.py:704-707, 721-729` |
| 11 | **重网格依赖可选** | `gpytoolbox` / `pynanoinstantmeshes` 缺了就置 flag，`run.py` 的选项随之消失，而不是崩 | `spar3d/models/mesh.py:26-45`、`run.py:67-77` |

## 4. 可跑性与实测方案

- **官方环境**：`Python >= 3.8`（随 PyTorch 版本可到 3.9+）、Windows/MPS 均标 **experimental** 且需 Visual Studio 2022（`README.md:26-32, 50-55`）。`requirements.txt` 钉 `transformers==4.42.3`、`trimesh==4.4.1`、`numpy==1.26.4`，**从 git 装 OpenAI CLIP 与 AlphaCLIP**，去背用 `transparent-background==1.3.3`（不是 rembg），并本地装 `./texture_baker/` 与 `./uv_unwrapper/`（`requirements.txt:1-13`）；重网格两个包在 `requirements-remesh.txt:1-2`。
- **显存**：默认 **10.5 GB**，低显存模式约 **7 GB**（`README.md:48`、`run.py:57-65`）⇒ 16 GB 卡够用，且 7 GB 口径留了余量。
- ★ **README 自相矛盾**：同一份 README 在 `README.md:82` 又写"The default options takes about **6GB VRAM**"（与 SF3D 同句），与 `:48` 的 10.5 GB 打架 ⇒ 以 `:48` 与 `run.py:61-63` 为准，6 GB 那句是复制残留。
- **权重体积**：HF **门控**（`README.md:40-44` 要求申请 + read token + `huggingface-cli login`）⇒ 取不到文件清单，**查不到**（2026-10-24 API 返回 404）。
- **预计耗时**：README 无耗时数字 ⇒ **查不到**。
- **本机（Windows + Python 3.14.7 + 4080S 16 GB，来源：本机 `python --version` / `nvidia-smi` 16376 MiB）能不能跑**：**显存够、软件链不够**（与 SF3D 同源，多两处坑）。
  1. 10.5 GB（或 7 GB）< 16 GB ⇒ 显存通过（`README.md:48`）。
  2. 两个 C++/CUDA 扩展的默认编译选项是 GNU 风格（`-O3/-fopenmp/-march=native`，见 `texture_baker/setup.py:33-41`、`uv_unwrapper/setup.py:23-31`），MSVC 下要先改。
  3. `CLIP` 与 `AlphaCLIP` 走 `git+https` 安装（`requirements.txt:6-7`），本机需能联网拉 GitHub 且能编译。
  4. Python 3.14.7 无配套 torch 轮子；本机已有 Astral CPython 3.10.21（本机 `py -0`）可建 venv。
  5. 权重门控，需 HF 申请。⇒ 结论同上：**读码为主，跑要单独配环境**。
- **若跑，怎么跑（预期）**：`python run.py demo_files/examples/fish.png --output-dir output/ --low-vram-mode`（`README.md:79-82`、`run.py:57-65`）。预期 `output/0/mesh.glb` + `output/0/points.ply`（`run.py:180-190`），峰值显存在 `run.py:173-174` 打印；要验"手改点云"这条独有能力，得改 `gradio_app.py` 或用 Python 直接调 `run_image(..., pointcloud=<Nx6>)`（`system.py:566`）。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **README 两个显存数字打架**（10.5 GB vs 6 GB，别拿 6 GB 做容量规划），且 Windows 小节开头是从 SF3D 复制的"To run **Stable Fast 3D** on Windows" | `README.md:48` 与 `README.md:82`、`README.md:52` |
| 3 | **低显存模式会反复换入换出**：每张图进出都要 unload/load 三组模块 ⇒ 批处理更慢 | `spar3d/system.py:488-491, 710-713` |
| 4 | **CPU 回退"很慢"**（README 原话"really slow"），且不报错 | `README.md:73`、`run.py:104-106` |
| 5 | **空网格静默**：顶点为 0 就返回空 `Trimesh()`，导出成功但没内容 | `spar3d/system.py:745-747` |
| 6 | **点云只有 512 点**：点云分辨率就是"背面可编辑"的分辨率上限，小特征改不出来 | `spar3d/system.py:287-288` |
| 7 | **重网格选项可能整块消失**（缺 `gpytoolbox`/`pynanoinstantmeshes` 时 `--remesh_option` 只剩 `none`）；**无测试、无几何指标**，验收只有肉眼与峰值显存 | `spar3d/models/mesh.py:26-45`、`run.py:67-77`；仓库根文件清单 |
| 8 | **去背换成了 transparent-background**：比 rembg 重（要额外模型），且与 SF3D 的流程不通用 | `requirements.txt:11`、`run.py:8, 119` |

## 6. 对我方目标的可用处（机制层面，含**边界**）

目标：让普通模型建出**能用、规范**的参数化模型（SolidWorks）。

- **可迁移**：① ★最值钱的是「**中间表示可替换**」这个设计（`system.py:673-700`）：我们的生成链只要把中间表示定义成一个**可注入的显式槽位**（比如"关键尺寸/包围盒/必须存在的孔位"），人就有介入点；这比"改 prompt 再抽一次"可控得多。② 「低显存按流程边界换模块」（`system.py:488-491`）是 16 GB 机器跑多阶段管线的通用做法，可直接照搬成我们的调度约定。③ 「重网格依赖可选、选项随之收缩」（`mesh.py:26-45`）是"能力缺失要显式降级"的正面写法。
- **★ 边界**：
  1. **还是三角网格 + 烘焙贴图**：没有草图、没有特征树、没有尺寸约束；进 SolidWorks 只能当导入网格体/图形实体，参数化得人工重建。
  2. **不保证水密/流形**：marching-tet 之后没有任何水密检查（`system.py:742-747` 只判空）。
  3. **点云条件不等于尺寸约束**：512 个点只能表达"大概形状 + 背面隆起"，表达不了孔径、倒角、配合公差。（来源：本卡 §8 证据清单）
  4. **单对象**：一条流水线一个前景物体（`system.py:630-651` 只做单图前景归一化），装配体不支持。
  5. **不能用于"要出图纸的零件"**：`points.ply` 与 `mesh.glb` 都是观感资产，不是可标注的几何。

## 7. 许可与红线

- **许可全名**：Stability AI Community License Agreement（2024-07-05 版，`LICENSE.md:1-2`）。★**别当 MIT**：`gh api` 返回 `NOASSERTION`。
- **年营收门槛**：为年营收低于 US$1,000,000 的组织保留免费访问（`LICENSE.md:10`）；一旦 You 与关联方**合计**年营收超过 US$1,000,000，本协议授予的全部许可**自该日起终止**，须另申请企业许可（`LICENSE.md:22`）。门槛按**公司总营收**算，不按项目营收算。
- **商用须注册**（`LICENSE.md:22`），地址 `https://stability.ai/community-license`。
- **分发义务三条**（`LICENSE.md:27`）：附协议副本；在 Notice 文件保留「Copyright © Stability AI Ltd. All Rights Reserved」；**显著展示「Powered by Stability AI」**（网站/UI/博客/关于页/产品文档任一处）。
- **用途限制**：不得用材料或输出去创建/改进其它**基础生成式 AI 模型**；须遵守 AUP（`LICENSE.md:28`）。
- **输出归属**：输出归使用者（`LICENSE.md:32`）；衍生作品归使用者，Materials 所有权归 Stability（`LICENSE.md:31`）。
- **下游豁免**：第三方作为集成终端产品的一部分从 Licensee 处获得材料时，Section III 不适用（`LICENSE.md:22`）——我们是直接使用者，**不享受**该豁免。
- **权重**：HF 门控；模型卡是否叠加条款——未核（§9）。

## 8. 证据清单

- 许可版本 / 门槛 / 注册与终止 / 分发义务 / 用途限制 / 输出归属 —— `LICENSE.md:1-2, 10, 22, 27, 28, 31-32`
- 显存 10.5 GB / 7 GB 低显存 / 6 GB 那句矛盾表述 —— `README.md:48, 82`、`run.py:57-65`
- 权重门控流程与定位（点云条件、背面可编辑）—— `README.md:40-44`、`README.md:19`
- Python/Windows/MPS 要求与复制残留 —— `README.md:26-32, 50-55, 73`
- 依赖（CLIP/AlphaCLIP/transparent-background/两个本地扩展）—— `requirements.txt:1-13`、`requirements-remesh.txt:1-2`
- 扩展 GNU 编译选项 —— `texture_baker/setup.py:33-41`、`uv_unwrapper/setup.py:23-31`
- 点扩散超参与 512 点 / 点云两路来源与 bbox 归一化 / 点 tokenizer —— `spar3d/system.py:107-116, 287-288, 566, 673-700, 506-509`、`spar3d/models/tokenizers/point.py:12-19`
- 低显存装载/切换 —— `spar3d/system.py:205-211, 238-297, 355-427, 488-491, 710-713`
- 几何提取与阈值 —— `spar3d/system.py:440-455`、`spar3d/models/isosurface.py:106-113, 205-229`
- UV / 烘焙 / 材质 / 输出旋转与光照对齐 —— `spar3d/models/mesh.py:251-275`、`spar3d/system.py:749-789, 796-802, 704-707, 721-729`
- 空网格与重网格可选 —— `spar3d/system.py:745-747`、`spar3d/models/mesh.py:26-45`、`run.py:67-77`
- 产物（glb + ply）与峰值显存 —— `run.py:173-190`
- 元数据 —— `gh api repos/Stability-AI/stable-point-aware-3d`，2026-10-24

## 9. 未确认事项

1. **权重体积与真实显存峰值**——HF 门控（API 404），README 两个数字互相矛盾，**查不到**；7 GB 低显存是否在 16 GB 卡上真能跑满流程**未实测**。（来源：本卡 §8 证据清单）
2. **耗时与 `config.yaml` 超参**——README 无耗时数字（**查不到**）；`cond_image_size`、`isosurface_resolution` 只在门控仓库，仓库内唯一 tet 文件是 `load/tets/160_tets.npz`（15.4 MB），据此**推断** 160，**未确认**。
3. **手改点云这条链路的实际效果**——`gradio_app.py` 有 UI，但我们只读码未跑；"补背面到底能补到什么程度"**未验证**。
4. **HF 模型卡是否叠加条款、训练数据许可**——**未核**，直接影响 §7 结论。
5. **star / 推送时间会变**——取数日 2026-10-24（`gh api`）。
