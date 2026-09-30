# A9 求解步：七次真机尝试的完整记录（2026-10-01）

**结论先行**：**仍未跑通。** 但把「为什么跑不通」从一个模糊现象（「网格器涨到 20 GB」）
收敛成了一组**可复核的确证事实**与**一个明确未解的问题**。

---

## 一、确证事实（每条都有真机证据，可重跑）

| # | 事实 | 证据 |
|---|---|---|
| 1 | **零件确实是 100×60×20 mm** | `GetBodyBox` 返回 `X[-0.05,0.05] Y[-0.03,0.03] Z[-0.02,0]`（API 单位=米）⇒ 0.1×0.06×0.02 m |
| 2 | **文档长度单位 = `swUnitsLinear = 0`** | `GetUserPreferenceIntegerValue(46)` |
| 3 | **`CreateMesh(0, 0, 0)` → 返回码 5** | `swsStudyErrorSpecifyPositiveValue` ⇒ **尺寸/容差必须为正** |
| 4 | **`CreateMesh(0, 0.2467, 4.9339)` → 返回码 0（Succeeded）** | 但产出 **19,539,399 单元 / 26,717,520 节点**，耗时 **222–230 秒** |
| 5 | **`CreateMesh()`（零参）→ 失败** | `DISP_E_PARAMNOTOPTIONAL`（「非选择性的参数」）⇒ 三个参数**都必需** |
| 6 | **网格设置的真宿主是 `ICWMesh`，不是 `ICWStudy`** | `study.Mesh` 可读 `MesherType`/`AutomaticTransition`/`ElementSize`/`Tolerance`/`ElementCount`/`NodeCount`；在 **study 上**访问这些属性一律 `<unknown>.xxx` |
| 7 | **默认值** | `MesherType=2`（`swsMesherTypeAlternateCB` = 文档说的 Blended curvature-based）· `AutomaticTransition=False`（**默认就是关的**）· `ElementSize=0` · `Tolerance=0` · `Quality=1` · `AutomaticLooping=False` |
| 8 | **`GetDefaultElementSizeAndTolerance(0, &size, &tol)` 对本零件返回 size≈4.9339 / tol≈0.2467** | 传第 1 参 `0` = `swsUnitSI` |
| 9 | **`MeshAndRun()` 返回 None**（且耗时 0 秒） | 与 `RunAnalysis` 同现象 |
| 10 | **`RunAnalysis()` 返回 19** | `swsRunAnalysisErrorMaterialNotDefined` —— 但本脚本**已赋材料**（`SetFavLibraryMaterialToSelectedEntities` 返回 0）⇒ 该 19 与材料赋值**并存**，需进一步区分 |

**枚举真源**：`D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt`
```
swsMesherType_e:  Standard=0  Alternate=1  AlternateCB=2
swsMeshType_e:    Solid=0  MidSurface=1  Surfaces=2  Mixed=3  Beam=4
swsUnit_e:        SI=0  English=1  Metric=2
swsStudyMeshError_e:  Succeeded=0  ...  SpecifyPositiveValue=5  ...
swsRunAnalysisError_e: Successful=0  ...  MaterialNotDefined=19  ...
```

---

## 二、⚠ **未解的核心问题**：`size` 的真实量纲/语义

**反推**：19,539,399 个单元 ⇒ 单元体积 = 1.2e5 mm³ ÷ 1.954e7 = **0.00614 mm³** ⇒ 边长 **≈0.183 mm**。

**传入值是 4.9339** ⇒ 实际单元比传入值小 **≈27 倍**。

**三个候选单位都解释不了这个 27 倍**：
| 假设 | 期望单元数 | 实得 | 结论 |
|---|---|---|---|
| size 是毫米（4.93 mm） | ≈1000 | 19.5M | ✗ 差 19,500 倍 |
| size 是米（4.93 m） | ≈0（比零件大） | 19.5M | ✗ 方向相反 |
| size 是微米 | 海量 | 19.5M | 量级不符 |

**⇒ 未解。** 可能的方向（**均未验证，不当作结论**）：
1. `CreateMesh` 的第 1 参不是 meshType 而是别的（如 mesherType 或 quality）
2. `size` 与 `tolerance` 的**位置**与我假设的相反
3. 曲面/混合网格被误启用（`MeshType` 读到 0 = Solid，但研究默认可能不同）
4. `GetDefaultElementSizeAndTolerance` 的返回单位与 `CreateMesh` 的入参单位**不是同一个**

**⇒ 下一轮该做的（**不是再试参数**）**：找 `CreateMesh` 的**官方参数名**。
`cworksapi.chm`（2790 页）里没有该方法的独立页；用户手册里 `CreateMesh` 命中都在
网格 PropertyManager 的**界面**说明里。**可能要去 `C:\swapi` 查，或从 VB6 CHM
（`cworksapivb6.chm`，1.8 MB）取参数名。**

---

## 三、七次尝试的时间线（每次都换了**假设**，不是换参数）

| # | 假设 | 做法 | 结果 |
|---|---|---|---|
| 1 | 网格太细 | `CreateMesh(0, 0.00025, 0.005)`（自以为是 5 mm） | 网格器 3000+ s CPU 未完成 |
| 2 | 更粗就好 | `CreateMesh(0, 0.00075, 0.015)`（15 mm） | 内存涨到 **25 GB** |
| 3 | 拓扑研究的问题 | 换**静力学**研究，`(0, 0.0005, 0.004)` | 20 GB / 1170 s |
| 4 | 显式参数的问题 | **零参** `CreateMesh()` | ✗ 参数必需 |
| 5 | **查文档**（此前一直没读用户手册，解包 2052 页） | 得知默认 BCB、`Global Size` 只对 Standard 有效、`Automatic transition` 会炸单元 | 假设更新 |
| 6 | 在 study 上设 mesher/transition | ✗ **属性不在 study 上** | 查反射 ⇒ 宿主是 `ICWMesh` |
| 7 | 在 `study.Mesh` 上设，用**官方建议值** | `CreateMesh(0, 0.2467, 4.9339)` → 返回 0，但 **19.5M 单元** | **单位/语义疑点** |

**⚠ 第 5 步是本轮唯一的方法论收获**：前 4 次都是「换参数」，按纪律**两次失败就该停下查文档** ——
我第 5 次才做。**代价是前 4 次浪费的时间。**

---

## 四、对 capabilities 的影响（**等级不动**）

`topology_optimization` **维持 `stitched`**。本记录不改变结论，只把「为什么未验」写清楚。

## 五、副作用（已清理）

- 每次尝试都以 `Stop-Process` 停掉 `cwbcbfmesh` 并确认内存回落（最后一次 40.7 GB 可用）
- 所有脚本都**不保存**文档（`CloseDoc` 前未 `SaveAs`）
- 新增探针脚本 7 个，都在 `D:\AI\SW\`（工作区，非代码副本）
