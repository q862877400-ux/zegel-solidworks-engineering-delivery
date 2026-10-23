# Stable Fast 3D

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/Stability-AI/stable-fast-3d ｜ 项目页 https://stable-fast-3d.github.io ｜ 论文 https://arxiv.org/abs/2408.00653 ｜ 权重 https://huggingface.co/stabilityai/stable-fast-3d（**门控**，须申请）|
| 许可 | **Stability AI Community License Agreement**（`LICENSE.md:1-2`「STABILITY AI COMMUNITY LICENSE AGREEMENT / Last Updated: July 5, 2024」）——★**不是** MIT、也不是标准 SPDX 许可（`gh api` 的 `license.spdx_id` 返回 `NOASSERTION`）。要点：年营收 < US$1,000,000 的组织可免费商用（`LICENSE.md:10`）；商用须在 Stability 注册（`LICENSE.md:22`）；年营收一旦超过 US$1,000,000，本协议下**所有许可自该日起终止**，须另申请企业许可（`LICENSE.md:22`）。完整红线见 §7 |
| 元数据 | 1902 stars · 最近推送 2025-01-22T14:55:42Z · Python（来源：`gh api repos/Stability-AI/stable-fast-3d`，取数日 2026-10-24）|
| 克隆 | D:\ai3d-survey\repos\Stability-AI__stable-fast-3d |
| 证据等级 | 读码（通读 `run.py` / `sf3d/system.py`（532 行）/ `sf3d/models/{mesh,isosurface,network,utils}.py` / `models/tokenizers/*` / `texture_baker/setup.py` / `uv_unwrapper/setup.py` / `requirements*.txt` / `LICENSE.md`；**未安装、未下权重、未推理**）|

## 1. 一句话定位

**单图 → 三平面 → marching-tet 三角网格 + 烘焙好的 PBR 贴图，一步前馈出 GLB**：TripoSR 的加速改进版（`README.md:23`），核心卖点是"出网格时就没瑕疵 + UV 展开 + 光照解耦"，把这套东西直接喂给游戏/引擎管线。**它交付的是资产（GLB + PBR 材质），不是几何模型。**

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

```
输入      一张 RGBA 图；rembg 去背 + 把前景裁到画面 85%（`run.py:31-34, 93-96`、
          `sf3d/utils.py:80-105`）。单视图，无相机、无深度
    ↓
中间表示  可学习三平面嵌入（默认 96×96×1024 每面）→ 图 token（ViT 系 enc）+
          相机嵌入 → 单流 transformer（默认 16 层）→ detokenize → 场景码
                                （`sf3d/models/tokenizers/triplane.py:12-15`、`sf3d/system.py:210-243`、
                                 `sf3d/models/transformers/backbone.py:151-158`）
    ↓
生成      三平面正交投影 grid_sample 三路 → concat → MLP 解出 density / vertex_offset，
          再把 density 减去阈值当成 SDF（解耦"密度阈值"这件事）
                                （`sf3d/system.py:157-178, 180-208`）
    ↓
几何      Marching Tetrahedra（tet 表随仓库放在 `load/tets/160_tets.npz`，15.4 MB），
          顶点形变按 scale/resolution·tanh 归一化防翻面
                                （`sf3d/system.py:137-146`、`sf3d/models/isosurface.py:106-113, 205-229`）
    ↓
纹理      自写 C++ UV 展开（按面复制顶点、缝线处拆点）→ CUDA texture baker 光栅化 UV
          → 重心插值回 3D 位置/法线 → 查三平面 → 解 albedo/roughness/metallic/扰动法线
                                （`sf3d/models/mesh.py:251-275`、`sf3d/system.py:366-405`）
    ↓
编排      single —— `run.py` 里 `from_pretrained` 一次装载，`run_image` 一把出结果；
          ComfyUI 节点只是包了一层（`__init__.py:18-40`）
    ↓
执行      单卡；CUDA 时用 bf16 autocast（`run.py:119-121`）；无 GPU 自动退 CPU（`run.py:74-75`）
    ↓
验证      visual —— 仓内无几何指标、无测试；只把峰值显存打出来（`run.py:128-129`）
    ↓
交付      mesh —— 单个 `.glb`：三角面 + UV + baseColor 贴图（JPEG）+ 法线贴图（JPEG，
          切线空间编码）+ 标量 metallic/roughness（`sf3d/system.py:475-509`、`run.py:136-137`）
```

★ 三问定性：**多视图**（否，单视图；`system.py:211-231` 的代码支持多视输入但 `run_image` 只喂 1 张）· **前馈**（是，无逐场景优化）· **重建式**（是 TripoSR/triplane 系的"图 → 规范 triplane → 等值面"，但**没有**任何多视几何求解）。

## 3. 技术方案要点（可迁移的机制）

| # | 机制 | 怎么做（不贴代码） | 出处 |
|---|---|---|---|
| 1 | **可学习三平面当紧凑场景码** | 3 个 96×96×1024 的可学习嵌入做 query，transformer 只更新它们 ⇒ 输出尺寸与输入分辨率解耦 | `sf3d/models/tokenizers/triplane.py:12-15`、`system.py:233-242` |
| 2 | **三路正交投影查询** | 同一批 3D 点分别按 xy / xz / yz 投到三面，双线性采样后拼成特征 | `sf3d/system.py:196-206` |
| 3 | **把阈值从场里拆出来** | 网络出 density，几何用 `density − isosurface_threshold` 当 SDF ⇒ 调阈值不用重训 | `sf3d/system.py:165` |
| 4 | **形变按网格步长归一化** | 顶点位移 = (range/resolution)·tanh(raw)，把位移压在半个体素内 | `sf3d/models/isosurface.py:106-113` |
| 5 | **UV 展开时按面复制顶点** | 缝线处直接拆点，换来"每三角形独立 UV"、避免缝合线撕裂 | `sf3d/models/mesh.py:262-273` |
| 6 | **两种重网格：都先落三角面** | triangle = 抽稀 + Botsch-Kobbelt 重网格；quad = Instant Meshes 出四边面但**导出前仍切成三角形** | `sf3d/models/mesh.py:185-249, 151-183`、`README.md:117` |
| 7 | **反查式贴图烘焙 + 切线空间法线** | 光栅化 UV 得重心坐标 → 插值 3D 位置/法线 → 查场 → 写纹素（不需要可微渲染）；世界法线再用插值切线基转到切线空间、映射 [0,1] 存 JPEG | `sf3d/system.py:369-392, 423-452` |
| 8 | **UV 边缘 padding** | 迭代次数按贴图分辨率算（`bake_resolution // 150`）做 dilate_fill，防 mip 采样渗色 | `sf3d/system.py:457-469` |
| 9 | **输出朝向一次性修正** | 先绕 X 转 −90°、再绕 Y 转 +90°，最后反转面序 | `sf3d/system.py:518-528` |
| 10 | **光照/材质解耦（可选）+ 空网格护栏** | `image_estimator` 出全局光照参数，`global_estimator` 仅 `estimate_illumination=True` 时跑；顶点数为 0 时返回空 `trimesh.Trimesh()` 并 continue，不抛异常 | `sf3d/system.py:334-339, 351-353` |

## 4. 可跑性与实测方案

- **官方环境**：`Python >= 3.8`、自装匹配的 PyTorch、`setuptools==69.5.1`、`wheel`；**Windows 需 Visual Studio 2022**（`README.md:32, 34-35`，且明写 Windows 支持是 **experimental**，`README.md:62-67`）。`requirements.txt` 钉 `transformers==4.42.3`、`trimesh==4.4.1`、`numpy==1.26.4`、`pynanoinstantmeshes==0.0.3`、`gpytoolbox==0.2.0`、`rembg[gpu]==2.0.57`，并本地安装 `./texture_baker/` 与 `./uv_unwrapper/`（`requirements.txt:1-14`）。
- **两个本地 C++/CUDA 扩展是硬依赖**：`system.py` 在 import 失败时**直接 raise**（`sf3d/system.py:32-41`、`sf3d/models/mesh.py:17-26`）⇒ 没编译出来根本起不来。
- ★ **Windows 编译风险（读码发现，未实测）**：两个扩展的默认编译选项是 GNU 风格 —— `-O3`、`-fopenmp`、`-march=native`、`-fdiagnostics-color`（`texture_baker/setup.py:33-41`、`uv_unwrapper/setup.py:23-31`），而唯一的 Windows 分支只出现在 debug 模式里（`texture_baker/setup.py:46-51` 才追加 `/Z7`、`/Od`）⇒ 用本机 MSVC（`C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`）默认方式装，很可能因不识这些选项而失败；要跑得先改 setup.py。
- **权重体积**：HF 是**门控**仓库（`README.md:42-46` 要求申请访问 + 建 read token + `huggingface-cli login`）⇒ 未登录取不到文件清单，**查不到**（2026-10-24 实测 API 返回 404）。
- **显存**：README 自述默认配置**约 6 GB VRAM**（`README.md:80`）⇒ 16 GB 卡有余量。
- **预计耗时**：README 全文无耗时数字 ⇒ **查不到**。
- **本机（Windows + Python 3.14.7 + 4080S 16 GB，来源：本机 `python --version` / `nvidia-smi` 16376 MiB）能不能跑**：**显存够、软件链不够**。
  1. 显存 6 GB（`README.md:80`）vs 16 GB ⇒ 通过。
  2. Python 3.14.7 没有与 `transformers==4.42.3` / `trimesh==4.4.1` 配套的 torch 轮子可用性未核；可行路径是用本机已有的 Astral CPython 3.10.21（本机 `py -0` 列出）建 venv。
  3. 本机 nvcc 是 CUDA 13.3（本机 `nvcc` 路径），与常见 cu121/cu124 轮子不同代，编扩展要另装匹配的 toolkit。
  4. 两个扩展的 GNU 编译选项要先改（见上）。
  5. 权重门控，需 HF 账号申请。
- **若跑，怎么跑（预期）**：`pip install -r requirements.txt` 后再 `python run.py demo_files/examples/chair1.png --output-dir output/`（`README.md:77-79`）。预期产物 `output/0/mesh.glb` + `output/0/input.png`（`run.py:97-98, 136-137`），控制台会打 `Peak Memory: ... MB`（`run.py:128-129`）——这就是最省事的显存实测口子。想验证 UV/材质是否正确，加 `--texture-resolution 512 --remesh_option triangle --target_vertex_count 20000`（`run.py:42-59`）。

## 5. 失败模式与已知坑

| # | 坑 | 证据 |
|---|---|---|
| 1 | **Windows 支持是 experimental**，官方只保证"能起来"，不保证质量与性能 | `README.md:62-67` |
| 2 | **扩展编译选项是 GNU 风格**，MSVC 下大概率过不去（未实测） | `texture_baker/setup.py:33-41, 46-51`、`uv_unwrapper/setup.py:23-31` |
| 3 | **无 GPU 时静默退 CPU**：不报错、只是很慢 ⇒ 容易误判"跑通了" | `run.py:74-75`、`sf3d/utils.py:13-22` |
| 4 | **空网格静默成空 GLB**：顶点为 0 就返回空 `Trimesh()`，导出成功但文件里没东西 | `sf3d/system.py:351-353` |
| 5 | **权重门控**：不登录 HF 直接 401/404，且模型卡条款可能叠加 | `README.md:42-46` |
| 6 | **`quad` 重网格拿不到四边面**（GLB 导出前被切成三角形）；**`remesh=none` 时 `target_vertex_count` 被忽略**，只打一行 warning | `README.md:117`、`sf3d/system.py:360-363` |
| 7 | **isosurface 分辨率与 tet 文件绑定**：文件名按 `cfg.isosurface_resolution` 拼，仓库里只有 160 那一份 ⇒ 想改分辨率要自备 tet 表 | `sf3d/system.py:137-146` |
| 8 | **单视图，背面靠先验**（兄弟项目 SPAR3D 的动机就写着"改进 SF3D 的背面"）；**MPS 比 CUDA 更吃内存**，官方建议内存小于 32 GB 走 CPU | `https://github.com/Stability-AI/stable-point-aware-3d` 的 `README.md:19`；`README.md:60` |

## 6. 对我方目标的可用处（机制层面，含**边界**）

目标：让普通模型建出**能用、规范**的参数化模型（SolidWorks）。

- **可迁移**：① 「按面复制顶点做 UV 展开」（`mesh.py:262-273`）是一套现成的"任意三角网格 → 可贴图资产"规范化步骤，我们做"多边形 → 带材质资产"时可直接照这个纪律。② 「UV 边缘按分辨率算迭代次数做 padding」（`system.py:457-469`）是防贴图渗色的**可量化判据**，比"多 pad 几像素"靠谱。③ 「形变按网格步长归一化」（`isosurface.py:106-113`）是"防止生成网格自交"的可迁移约束，我们可以把它写成后置校验。④ PBR 打进 glTF（标量 metallic/roughness + 法线图，`system.py:504-509`）比 OBJ+顶点色更接近"能用的资产"规范。
- **★ 边界**：
  1. **交付物是"贴图资产"不是"模型"**：三角网格 + 一张烘焙贴图，没有特征、没有尺寸、没有配合面、没有材料定义（只有渲染意义的 albedo/roughness）。
  2. **不保证水密/流形**：marching-tet 出来的面可以是开边界的，全程无水密检查（`system.py:346-353` 只判"空不空"）。
  3. **背面是编的** ⇒ 任何需要背面定位的装配关系都不可用。
  4. **进 SolidWorks 只能当"导入的图形实体/网格体"**：没有草图与特征树，改一个圆角就得重生成，做不了参数化驱动；对 16 GB 卡来说它的价值在"快速占位/概念件"，不在"可交付图纸"。（来源：本卡 §8 证据清单）
  5. **单对象**：整条链路假设"画面里一个前景物体"，多零件装配体不支持（`system.py:294-315` 只做单图前景归一化）。

## 7. 许可与红线

- **许可全名**：Stability AI Community License Agreement，2024-07-05 版（`LICENSE.md:1-2`）。★**别当 MIT**：`gh api` 返回 `NOASSERTION`，它不是 OSI 标准许可。
- **年营收门槛（核心）**：协议明写"为年营收低于 US$1,000,000 的组织保留免费访问"（`LICENSE.md:10`）；一旦 You 或关联方**合计**年营收超过 US$1,000,000，本协议授予的**全部许可自该日起终止**，必须另向 Stability 申请企业许可（`LICENSE.md:22`）。⇒ 对我们：**门槛按公司总营收算，不按本项目营收算**。
- **商用须注册**：以 Commercial Purpose 使用或分发，须在 `https://stability.ai/community-license` 注册（`LICENSE.md:22`）。
- **分发义务三条**（`LICENSE.md:27`）：① 随分发附本协议副本；② 在 Notice 文件里保留「This Stability AI Model is licensed under the Stability AI Community License, Copyright © Stability AI Ltd. All Rights Reserved」；③ 在网站/UI/博客/关于页/产品文档**显著展示**「Powered by Stability AI」。改动过还要写明改了什么。
- **用途限制**：不得用本材料或其输出去**创建或改进其它基础生成式 AI 模型**；须遵守 Stability 的 AUP（`LICENSE.md:28`）。
- **输出归属**：输出归你（`LICENSE.md:32`）；衍生作品归你，但 Stability 保留对 Materials 的所有权（`LICENSE.md:31`）。
- **下游豁免**：若第三方是"作为集成终端产品的一部分"从 Licensee 处拿到材料，则 Section III（商用条款）**不适用于该第三方**（`LICENSE.md:22`）——这条对"我们是下游买家"的场景重要，但我们是**直接使用者**，不享受该豁免。
- **权重**：HF 门控仓库，模型卡是否在社区许可之外再加条款——未核（§9）。

## 8. 证据清单

- 许可全文与各条行号 —— `LICENSE.md:1-2`（版本）、`:10`（100 万美元门槛）、`:22`（注册 + 超阈值终止 + 下游豁免）、`:27`（三条分发义务）、`:28`（用途限制）、`:31-32`（衍生/输出归属）
- 6 GB 显存与 Windows experimental —— `README.md:80`、`README.md:32, 62-67`
- 权重门控申请流程 —— `README.md:42-46`
- 依赖钉版与两个本地扩展 —— `requirements.txt:1-14`
- 扩展 import 失败即 raise / 扩展编译选项（GNU 风格，Windows 仅在 debug 分支）—— `sf3d/system.py:32-41`、`sf3d/models/mesh.py:17-26`、`texture_baker/setup.py:33-41, 46-51`、`uv_unwrapper/setup.py:23-31`
- 三平面尺寸与 transformer 层数 / 场景码生成链路 —— `sf3d/models/tokenizers/triplane.py:12-15`、`sf3d/models/transformers/backbone.py:151-158`、`sf3d/system.py:210-243`
- 三平面查询与阈值重参数化 / 形变归一化与 marching tet —— `sf3d/system.py:180-208, 165`、`sf3d/models/isosurface.py:106-113, 205-229`、`sf3d/system.py:137-146`
- UV 展开按面拆点 / 两种重网格 —— `sf3d/models/mesh.py:251-275, 151-249`、`README.md:117`
- 烘焙 / 材质打包 / 旋转修正 / 峰值显存打印口 —— `sf3d/system.py:366-405, 423-469, 475-528`、`run.py:128-129`
- 设备回退与 CPU 开关 —— `run.py:74-75`、`sf3d/utils.py:13-22`
- 元数据 —— `gh api repos/Stability-AI/stable-fast-3d`，2026-10-24

## 9. 未确认事项

1. **权重体积与 `config.yaml` 关键超参**——HF 门控，未登录取不到文件清单（API 返回 404），**查不到**；`cond_image_size`、`isosurface_resolution` 的真实取值只在门控仓库里，仓库内唯一的 tet 文件是 `load/tets/160_tets.npz`（15.4 MB），据此**推断**分辨率是 160，但**未确认**。
2. **耗时**——README 无数字，**查不到**。
3. **Windows 上两个扩展能否编译**——只读码发现 GNU 选项，**未实测**；`README.md:62-67` 说 Windows 是 experimental 也印证有坑。
4. **HF 模型卡是否叠加条款、训练数据与数据许可**——README 只交代结构不交代训练集组成，模型卡条款**未核**；这会直接改变 §7 的结论（例如是否允许商用输出）。
5. **star / 推送时间会变**——取数日 2026-10-24（`gh api`）。
