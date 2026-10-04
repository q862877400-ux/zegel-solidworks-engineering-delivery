# 仿真性能 / 内存 / GPU —— 官方依据 + 社区做法 + 本仓可执行的杠杆

> ★ 起因：2026-10-04 一次真机事故（求解器吃 38.5 GB / 整机 63.8 GB ⇒ 卡死，事实 521）。
> 业主追问两条：① **别人**（多数机器不到 64 GB）到底怎么配；② **有没有第三方办法让这个求解跑在 GPU 上**。
> ★ 本文把**本机官方离线源**与**网上来源**分开标：`〔本机官方〕` / `〔网上〕`。★ 查不到就写查不到（铁律 5）。

---

## 一 · 三句话结论

1. **SW Simulation 自己的求解器**：**没有 GPU**。7 个求解器全是 CPU（迭代 / 直接分解）。
2. **内存不够时官方给的正解有两级**：① 换**省内存的求解器** → ② 走 **out-of-core（磁盘）**；★ 而 out-of-core **不是报错、是"极慢"**。
3. **要吃 GPU 就得换求解器**：SW Simulation 能**导出算例**（官方枚举里有 Abaqus / Ansys / Nastran …），
   而 GPU 加速存在于 **Abaqus / Ansys** 那一侧 ⇒ ★ **路线是"导出 + 外部求解器"，不是"打开某个 GPU 开关"**。

---

## 二 · 〔本机官方〕内存账（逐字）

出处：`C:\cworks_manual\c_Analysis_Solvers.htm` · `IDC_HELP_PRESTATIC_OPTIONS.htm`

| ★ | 逐字 | 含义 |
|---|---|---|
| ① | 「FFEPlus (iterative) … For every 2,000,000 degrees of freedom, you need 1GB of RAM.」 | ★ **内存账的官方公式** |
| ② | 「… requires **less RAM** than the Intel Direct Sparse solver」 | ★ 缺内存先换 FFEPlus |
| ③ | 「If a solver requires more memory than available … the solver **uses disk space** … the solution is **going out of core** … can be **extremely slow**」 | ★ **内存不够 = 极慢，不是报错** ⇒ 必须外部闸 |
| ④ | 「the **Large Problem Direct Sparse** solver can handle simulation problems that **exceed the physical memory** of your computer」 | ★ 超物理内存的专用解 |
| ⑤ | 「**Intel Direct Sparse** … more efficient at taking advantage of **multiple cores**」 | ★ 核多、内存够时最快 |
| ⑥ | 「all solvers are efficient for small problems (**25,000 DOFs or less**)」·「FFEPlus is faster … with **DOF over 100,000**」 | ★ 选型的分档线 |

★ 求解器选择是属性：`CWStaticStudyOptions.SolverType`（`Long`），
取值〔本机官方类型库〕`CosmosWorksLib~swsSolverType_e.html`：
`Automatic=0` · `DirectSparse=1` · `FFEPlus=2` · `CASI=5` · `Abaqus=6` · `INTEL=7` · `INTELCluster=8`。
⚠ ★ **枚举值 ↔ 界面名（"Large Problem Direct Sparse" / "Intel Direct Sparse"）的对应，两套官方源都没写** ⇒ 不猜。

---

## 三 · 〔网上〕别人怎么配（★ 与本机官方那三条**一致**）

### 3.1 先降 DOF，再谈内存（这是社区共识的第一步）

- ★ 常规手法：**对称**、**2D 简化**、**梁/壳理想化**、**只在关心处做局部细化**，而不是整件加密。
  〔网上〕`c_Analysis_Solvers.htm` 的在线同页（[Static - Options 2021](https://help.solidworks.com/2021/english/SolidWorks/cworks/IDC_HELP_PRESTATIC_OPTIONS.htm)）与多份经销商硬件指南都是这个口径。
- ★ **硬件侧**：out-of-core 要靠**快盘**——〔网上〕SOLIDBI 的 SOLIDWORKS 2023 需求文档逐字提到
  「考虑使用 **SSD NVMe/PCIe** 而不是标准 SATA SSD」（[PDF](https://solid-bi.es/wp-content/uploads/2023/02/Requisitos-SOLIDWORKS-2023-SOLIDBI.pdf)）。
  ⇒ ★ 这也是"不出内存也要出磁盘 IO"的现实：**out-of-core 的瓶颈落在盘上**。

### 3.2 卸载到另一台机器（原厂功能，★ 但有版本寿命）

- 〔网上〕经销商 GoEngineer 逐字（[Offloaded SOLIDWORKS Simulation](https://www.goengineer.com/blog/solidworks-simulation-offloaded-simulation)）：
  - 「SOLIDWORKS Simulation **2017** introduced the capability of **offloading an analysis to another system**」
  - 「requires a license of **SOLIDWORKS Simulation Premium**」· 「can be used to offload **static and nonlinear** studies」
  - 「The **coordinator** … and the offloaded system as the **worker agent**」· 「connected on the **same network domain**」
  - ★★★ 「**Note: SOLIDWORKS 2021 is the last release to support Offloaded Simulation** in the SOLIDWORKS Simulation product.」
- 〔本机官方类型库〕而同族 API **在我们这台 2026 上仍然在**：
  `CosmosWorksLib~CWStudy~OffLoad.html` ⇒ `Public Property OffLoad As Boolean`；
  `…~CWStudyManager~ManageDistributedSimulation2.html` ⇒
  `ManageDistributedSimulation2(BOffLoad As Boolean, ComputerNames As Variant) As Long`。
  ⇒ ★★ **「功能已退役」与「API 还在」并存** ⇒ ★ 按铁律 5：**本文不判它在本机能不能用**，须真机试（★ 一个可做的单变量实验：读 `study.OffLoad` 是否可设、`ManageDistributedSimulation2` 的返回码）。
- 〔网上〕官方帮助页（2019）：[Offloaded Simulation](https://help.solidworks.com/2019/english/SolidWorks/cworks/c_offload_Simulation.htm)；
  2017 What's New 的 offload 小节见 SolidWorks 自己的 PDF（如 whatsnew 日文/俄文版）。

### 3.3 换更省内存的求解器（与 §二 合并即可执行）

★ 与 §二 ①②④⑤⑥ 同源，不再重复。

---

## 四 · GPU：为什么 SW Simulation 用不上，以及"第三方路线"到底长什么样

### 4.1 〔本机官方〕SW Simulation 没有 GPU 求解器（三条判据）

```
① 求解器枚举 7 个成员**全是 CPU**（见 §二末）：迭代(FFEPlus) 与三种直接分解
   （DirectSparse / INTEL / CASI）+ Abaqus + 两个集群项 ⇒ ★ **没有 GPU 项** ✓
② 把三套 Simulation 文档（手册 2052 / 英文 2790 / 类型库 3000 份）全库 grep
   `GPU|CUDA|OpenCL|graphics card|hardware acceleration` ⇒ 命中 7 处，
   ★★ **全部落在 `c_copyright_solidworks.htm`** —— 那是捆绑 Intel 库的**第三方许可声明**
   （oneAPI Level Zero / OpenCL 驱动 / Intel Graphics Compiler），★ **不是求解器能力** ✓
③ 求解算法本身（矩阵重排 + 分解/迭代）走 **CPU 多核 + 内存 + 磁盘** ✓
⇒ ★ GPU 在 SolidWorks 里服务**图形/渲染**（RealView · Visualize），★ 不服务 FEA ✓
```

### 4.2 〔网上〕GPU 加速 FEA **确实存在** —— ★ 但都在**别的求解器**里

| 求解器 | GPU 证据（网上） |
|---|---|
| **Abaqus** | ★ NVIDIA 白皮书 *Accelerating Abaqus Computations*（[PDF](https://images.nvidia.com/content/tesla/pdf/wp-07843-001-v03-accelerating-abaqus-computations-whitepaper.pdf)）· Dassault 的 HPC 专题（[Abaqus Performance on HPC](https://events.3ds.com/simulia-abaqus-performance-hpc)）· 经销商技术文（[Simulia.cz: GPU akcelerace v Abaqusu](https://www.simulia.cz/blog/gpu-akcelerace-v-abaqusu-kdyz-graficka-karta-promeni-simulacni-workflow/)） |
| **Ansys Mechanical** | ★ Ansys 官方 release notes 里有 **「GPU Acceleration Feature Updates」** 与「Distributed-Memory Parallel Processing」（[Ansys Release Notes](https://ansyshelp.ansys.com/public//Views/Secured/corp/v252/en/pdf/Ansys_Release_Notes.pdf)）· Supermicro/Ansys 的 GPU 方案简报（[PDF](https://www.supermicro.com/solutions/Solution_Brief_SMCI_Ansys_GPU.pdf)） |
| 通用 GPU 直接解 | ★ 学术/HPC 侧有「GPU accelerated sparse direct solver + block low-rank」（[Sagepub 2024](https://journals.sagepub.com/doi/pdf/10.1177/10943420241288567)）⇒ ★ 说明这条路在**别的程序**里成熟，而**不在 SW Simulation 里** |

### 4.3 ★★ 而 SW Simulation 上**真有一条桥**：**把算例导出去跑**

〔本机官方类型库〕★ 导出格式枚举 `swsStudyExportOption_e` 逐字给了：
`Cosmos=0` · `Ansys=1` · `Nastran=2` · `PatranNeutral=3` · `IdeasUniversal=4` · `Exodus=5` · **`Abaqus=6`**；
★ 而 `swsSolverType_e` 里也有 **`swsSolverTypeAbaqus=6`**。
⇒ ★★★ **即：把 SW 里建好的算例导出，交给 Abaqus/Ansys 这类"有 GPU 求解器"的程序去解** ——
★ 这是"第三方让求解跑在 GPU 上"在**本仓语境下**唯一站得住的路线 ✓
⚠ ★ **代价**：★ 导出后**不再是 SW Simulation 的结果树**（后处理、报告、与 CAD 的关联都要另做）；
★ 且 Abaqus/Ansys 的 GPU 许可与版本门槛本文**未核**（★ 网上来源只说"有"，没说"本机这份许可有"）✓
⚠ ★ 另有一条常见路线是**云端**（如 SimScale 等）：★ 本文**没有**找到它 GPU 求解的权威依据 ⇒ ★ **不写它"支持 GPU"**。

---

## 五 · 落到本仓：可执行的杠杆（★ 都是本机官方成员，未经真机验证的已标注）

| 杠杆 | 成员（本机官方类型库） | 对内存的作用 | 状态 |
|---|---|---|---|
| 求解器选择 | `ICWStaticStudyOptions.SolverType`（`swsSolverType_e`） | ★ 缺内存优先 `FFEPlus=2`；超物理内存考虑 `CASI=5`/`INTEL=7` | ★ **已在** `sw_simulation_study_options.py` 的类型表里（★ 未挂成显式参数） |
| ★ 网格质量 | `ICWMesh.Quality`（`Int32`，`swsMeshQuality_e`：`Draft=0` / `High=1`） | ★★ **Draft 用线性单元 ⇒ 节点数大幅下降 ⇒ DOF 与内存都降** | ★ 已定位、**未实现** |
| ★ 节点数（真实 DOF 代理） | `ICWMesh.NodeCount`（`Int32`） | ★★ **DOF ≈ 3 × 节点数**（★ 实测标定：事实 293 的 30,456 自由度 / 11,301 节点 = **2.69**） | ★ 已定位、**未实现** ⇒ 比 `4.2 × 单元数` **更准** |
| 网格类型 | `ICWStudy.MeshType`（`swsMeshType_e`：`Solid=0`/`MidSurface=1`/`Surfaces=2`/`Mixed=3`/`Beam=4`） | ★★ **梁/壳/中面 = 数量级降 DOF** | ★ 已定位、**未实现** |
| 单元尺寸/公差 | `ICWMesh.ElementSize` / `GetDefaultElementSizeAndTolerance` | ★ 直接决定单元数 | ★ 已实现（`mesh_size_report` / `create_mesh`） |
| ★ 本仓三层闸 | `check_mesh_size_sane` · `solve_memory_preflight` · `tools/watch_solver_memory.py` | ★ **内存上限可执行** | ★★ **已实现 + 10 条负例**（事实 521） |

★ **建议的下一步（按性价比）**：
1. ★ **`ICWMesh.NodeCount` 接进 `solve_memory_preflight`** —— 把 `est_dof` 从"4.2×单元数"换成"3×节点数"（★ 更准，且是**第一性原理**：每个节点 3 个平动自由度）；
2. ★ 把 `Quality`（Draft/High）与 `SolverType` 做成可传参数（★ 缺内存时的两个直接旋钮）；
3. ★ 用真机单变量实验判定 `OffLoad` / `ManageDistributedSimulation2` 在本机还能不能用（★ 退役传言 vs 类型库仍在）。

---

## 六 · 来源清单

**〔本机官方〕** `C:\cworks_manual\c_Analysis_Solvers.htm` · `IDC_HELP_PRESTATIC_OPTIONS.htm` ·
`C:\cworks_vb6\CosmosWorksLib~swsSolverType_e.html` · `…~swsStudyExportOption_e.html` ·
`…~CWStudy~OffLoad.html` · `…~CWStudyManager~ManageDistributedSimulation2.html` ·
`…~swsMeshQuality_e.html` · `D:\AI\SW\_raw\reflect\iface_cosworks.txt`（`ICWMesh.Quality` / `NodeCount`）

**〔网上〕** [GoEngineer: Offloaded SOLIDWORKS Simulation](https://www.goengineer.com/blog/solidworks-simulation-offloaded-simulation) ·
[SOLIDWORKS 2019 帮助: Offloaded Simulation](https://help.solidworks.com/2019/english/SolidWorks/cworks/c_offload_Simulation.htm) ·
[SOLIDWORKS 2021 帮助: Static - Options](https://help.solidworks.com/2021/english/SolidWorks/cworks/IDC_HELP_PRESTATIC_OPTIONS.htm) ·
[NVIDIA: Accelerating Abaqus Computations (PDF)](https://images.nvidia.com/content/tesla/pdf/wp-07843-001-v03-accelerating-abaqus-computations-whitepaper.pdf) ·
[Dassault: Abaqus Performance on HPC](https://events.3ds.com/simulia-abaqus-performance-hpc) ·
[Ansys Release Notes (PDF)](https://ansyshelp.ansys.com/public//Views/Secured/corp/v252/en/pdf/Ansys_Release_Notes.pdf) ·
[Supermicro/Ansys GPU (PDF)](https://www.supermicro.com/solutions/Solution_Brief_SMCI_Ansys_GPU.pdf) ·
[GPU sparse direct solver 论文](https://journals.sagepub.com/doi/pdf/10.1177/10943420241288567) ·
[SOLIDBI: SOLIDWORKS 2023 需求（NVMe/PCIe）](https://solid-bi.es/wp-content/uploads/2023/02/Requisitos-SOLIDWORKS-2023-SOLIDBI.pdf)
