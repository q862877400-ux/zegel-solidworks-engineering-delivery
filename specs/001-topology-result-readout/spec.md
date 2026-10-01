# Feature Specification: 拓扑优化结果读取

**Feature Branch**: `001-topology-result-readout`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "P1 —— 让 AI 能读取拓扑优化的结果：Material Mass 图、收敛数据、导出平滑网格"

---

## 背景（**这一节是本 spec 的核心，因为它改变了对需求的判断**）

上游目标（ROADMAP P1）写的是「实现三件事」。但**四源取证**后，
需求的性质变了：**这三件事在公开 API 里可能不存在**。

**已查的四源**（按 AGENTS.md 铁律 4「三源互证」扩展到运行期）：

| # | 源 | 查什么 | 结果 |
|---|---|---|---|
| 1 | `SolidWorks.Interop.cosworks.dll` 接口清单（`iface_cosworks.txt`，168 接口 / 3224 成员） | `SmoothedMesh` / `MaterialMass` / `Convergence` | **0 命中**；唯一 Export 方法是 `ICWStudy.ExportSimulationStudy`（导出研究，非平滑网格） |
| 2 | 同 DLL 的**二进制** | `ExportSmoothedMesh` 字符串 | **12 处命中，但全是 `swsExportSmoothedMesh_*` 枚举值名**；对照组成立（`CreateMassConstraint` 等真方法名在 `#Strings` 堆里各 1 处） |
| 3 | CHM API 参考 `cworksapi.chm`（解包 2790 页） | `Smoothed Mesh` / `Material Mass` / `Convergence Data` | **0 命中** |
| 4 | 运行期 `get_com_member` 试探（`GetIDsOfNames`） | `ICWStudy` 上 6 个候选名 | **全部「名字不存在」** |

**已确认存在的**：
- 枚举 `swsExportSmoothedMeshError_e`（10 值，`Succeeded=0`）与
  `swsExportSmoothedMeshOption_e`（`IntoCurrentActiveConfiguration=0` /
  `IntoNewConfiguration=1` / **`IntoNewPart=2`** ← 对应官方的「New part file」）
- 枚举 `swsPlotResultTypes_e`（14 值，**无 Mass / Material Mass**）
- `ICWResults` 接口 **107 个成员**，含 `CreatePlot` / `GetMinMax*` / `savePlotsAseDrawings` /
  **`GetTimeOrFrequencyAtEachStep`**（疑似收敛数据的来源）
- 官方教程 `t_exporting_optimization_results.htm` 描述的是**纯 UI 操作**：
  右键 `Results` → `View Convergence Data and Graph`；右键 `Material Mass1 (-Material Mass)`
  → `Export Smoothed Mesh` → PropertyManager → **New part file**

**⇒ 待验证的关键假设**：`swsExportSmoothedMesh*` 枚举**存在但无公开方法使用**，
说明该能力要么走内部/UI 通路，要么挂在**结果已存在时**才出现的对象上
（本轮 `study.Results` 返回 False，因为研究还没跑过 ⇒ **`ICWResults` 那关没测到**）。

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 判定「结果读取」到底有没有 API，并留下可复查的证据 (Priority: P1)

一个要建护城河的开发者，**不能靠猜**决定「这个功能 API 做不了」。
他需要一份**四源取证**的记录，让任何人可以重跑并得到同样结论。

**Why this priority**: 这是本特性的**真正交付物**。若三件事真无 API，
那么「写代码去调」就是浪费；若其实有 API 而我没找到，会白丢一个护城河功能。
**两种情况都必须以证据收尾，不能以「试过了不行」收尾。**

**Independent Test**: 重跑 `tools/probe_results_api_surface.py` 与
`find_bare_outparam_sites.py` 式的静态比对，核对本文 §背景 的四张表。

> ⚠ **2026-10-01（轮 56）更正**：本行原写裸文件名 `probe_results_api_surface.py`，
> 而它当时**只在工作区根** `D:\AI\SW\` ⇒ **换机器 / CI 跑不了**。
> **⇒ 已按仓库规范收进 `tools/`**（可移植路径 + 来源块），并在下方加了一条
> 「验收命令必须在仓库内」的**门禁**（`scripts/check_spec_acceptance_paths.py`）。

**Acceptance Scenarios**:

1. **Given** 一个**已跑过拓扑优化**的研究（有 `Material Mass1` 结果项），
   **When** 在 `ICWResults` 上试探 `ExportSmoothedMesh` / `GetSmoothedMesh` /
   `ViewConvergenceData` / `MaterialMass` 及其变体，
   **Then** 得到一个**明确的**结论：存在（给出签名与调用示例）或不存在（给出 `GetIDsOfNames` 的报错原文）。
2. **Given** 上述结论，**When** 写进 `capabilities.yaml` 的 `limitations`，
   **Then** 该条目里**不得**出现「试过了不行」这类不可复查的措辞。

---

### User Story 2 - 把「能读到的」读出来 (Priority: P2)

即使三件事没有 API，`ICWResults` 的 107 个成员里仍有可用的读数入口
（`GetMinMaxStress` / `GetMinMaxDisplacement` / `GetMinMaxFactorOfSafety` /
`GetTimeOrFrequencyAtEachStep`）。用户希望这些**能被真的读出来**，
而不是因为「读不到图」就整个域标成不做。

**Why this priority**: 「读不到图」≠「读不到数」。分开处理才能保住已有的护城河价值。

**Independent Test**: 在一个**已跑过优化**的研究上调用读数函数，
返回非空且数值合理（如位移 > 0、安全系数 > 0）。

**Acceptance Scenarios**:

1. **Given** 一个已跑过拓扑优化的研究，
   **When** 调 `collect_topology_numbers(study)`，
   **Then** 返回 `{min_max_displacement, min_max_stress, min_max_fos, steps}`，
   且每个值附带它来自哪个 `ICWResults` 成员（可复查）。
2. **Given** 一个**没跑过**的研究，
   **When** 调同一函数，
   **Then** 明确返回「无结果」（不得抛未捕获异常、不得静默返回空 dict）。

---

### User Story 3 - 导出平滑网格的可替代路径 (Priority: P3)

若 API 确实没有 `ExportSmoothedMesh`，用户希望知道**替代路径**：
能不能用 `ICWResults.savePlotsAseDrawings` + 别的接口拼出来，
或者只能走 UI（此时应记录「需人工/需 computer-use」而不是说「做不到」。

**Why this priority**: 这是「做不到」与「换个法子做到」的分界，价值低于前两者。

**Independent Test**: 给出至少一条**已实测**的替代路径，或明确写「无替代路径，只能 UI」。

**Acceptance Scenarios**:

1. **Given** API 无 `ExportSmoothedMesh`，
   **When** 评估 `savePlotsAseDrawings` / `ICWStudy.ExportSimulationStudy` /
   UI 自动化三条路，
   **Then** 每条给出「能/不能 + 依据」。

---

### Edge Cases

- 研究**跑失败**（未收敛）时，`Results` 是否仍可访问？读数函数应如何表现？
- 研究有**多个** `Material Mass*` 图时，按名字取哪一个？
- `swsExportSmoothedMeshOption_IntoNewPart = 2` 需要文件名与路径 ——
  路径非法时错误码是 `InvalidPath = 5`，可否用来反推方法签名？
- 中文界面下的结果项名（`Material Mass1` vs 本地化名）是否影响按名取用？

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 必须在一个**真的跑过拓扑优化**的研究上完成运行期试探
  （本轮只测到 `ICWStudy`，`ICWResults` 因无结果而跳过 —— 这是**已知的取证缺口**）。
- **FR-002**: 试探必须覆盖**至少** `ExportSmoothedMesh` / `GetSmoothedMesh` /
  `ExportSmoothedMesh2` / `ViewConvergenceData` / `MaterialMass` / `GetMaterialMassPlot`
  六个名字，并逐个记录 `GetIDsOfNames` 的报错原文。
- **FR-003**: 结论必须写进 `capabilities.yaml` 的 `limitations`，**不得**用
  「试过了不行」这类不可复查措辞（对照 A2/A7 的可追溯要求）。
- **FR-004**: 必须实现读数函数（US2），把 `ICWResults` 里**确实可用**的读数入口包出来，
  并在返回值里标注来源成员名。
- **FR-005**: 每个断言都要有**可重跑的命令**（AGENTS.md「验收判据写成可 grep 项」）。
- **FR-006**: 若结论是「无 API」，必须在 spec / capabilities 里同时写明
  **替代路径的评估结论**（US3），而不是只写「做不到」。

### Key Entities

- **`ICWResults`** —— 结果读数入口，107 个成员；由 `ICWStudy.get_Results()` 取得。
- **`swsExportSmoothedMeshOption_e` / `swsExportSmoothedMeshError_e`** ——
  **存在但未被任何公开方法引用**的枚举（本特性的核心谜题）。
- **`swsPlotResultTypes_e`** —— 建图类型（14 值，**无 Mass**）。
- **`Material Mass1 (-Material Mass)`** —— 官方的结果树节点名（UI 层概念）。

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `tools/probe_results_api_surface.py` 能在**已跑过优化**的研究上跑完，
  ⚠ **命令来自仓库内**（轮 56 从工作区根搬入；见上方 Independent Test 的更正说明）
  并对六个候选名逐个给出「存在 / 不存在 + 原文报错」。
- **SC-002**: `capabilities.yaml` 的 `topology_optimization` 条目里，
  「看结果」三件事各有一条**可复查**的结论行（含证据来源）。
- **SC-003**: 读数函数在已跑过优化的研究上返回**非空**且来源可追溯的值；
  在未跑过的研究上**明确报「无结果」**。
- **SC-004**: 四源取证表可被**独立重跑**复核（每条给出命令）。

---

## Assumptions

- 本机能继续使用 SolidWorks 2026 SP4.1 + Simulation 加载项（已实测可用）。
- 跑一次拓扑优化（网格 + 求解）在本机**可行且耗时可控**（尚未实测 —— 这是 FR-001 的前提）。
- 官方教程描述的 UI 操作与 API 能力**不一定一一对应** —— 本特性正是要判定这一点。
