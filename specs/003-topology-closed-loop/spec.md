# Feature Specification: 拓扑优化闭环（真机跑通并取得 Material Mass）

**Feature Branch**: `003-topology-closed-loop`

**Created**: 2026-10-01

**Status**: Implemented（真机已验证）

**Input**: 用户诉求：「让 AI 会自己设计制作…拓扑…等一切 SolidWorks 功能」中的**拓扑优化**一项；
本条是 A9「空白域护城河」的验收闭环。

---

## 背景：这条特性为什么必须单独成篇

拓扑优化是本项目**唯一的独占资产**（四家外部 MCP 项目**全空** —— 见
`docs/union-coverage-matrix.md` §二 的 `⑯ 高级/专项` 行）。
它的实现早已落地（`scripts/sw_topology.py`，617 行 / 26 导出项 / 8 条契约测试），
但**长期停在 `stitched`** —— 卡在两件事：

1. **求解被许可证挡住**（求解时 Simulation 弹「拓扑算例未获许可」，`Results` 为空）
2. **没有成功取得 Material Mass 结果**（知识页把它列为「主要未决项」）

**⇒ 本特性把「闭环跑通 + 拿到 Material Mass」做成**可复核的制品与可复跑的命令**，
而不是一串只存在于对话里的数字。**

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 一次连续运行走完拓扑闭环（Priority: P1）

工程师要能在**单实体零件**上从「建研究」一路走到「出结果图」，
中间不需要人工介入、不需要在界面上点任何东西。

**Why this priority**: 这是护城河的定义 —— 「把官方拓扑优化 API 做成
**可运行、可测试、可追溯**的工程能力」。分段能跑不等于闭环能跑。

**Independent Test**: 跑 `python tools/capture_topology_evidence.py`，
`output/topology-evidence.json` 的 `verdict` 为 `pass`。

**Acceptance Scenarios**:

1. **Given** 一个单实体零件与含拓扑优化的 Simulation 许可，
   **When** 依次建研究 → 设目标 → 施夹 → 加载 → 划网格 → 求解，
   **Then** `study.Results` **非空**，且 `GetPlotNames` 里出现 **Material Mass** 结果图。
2. **Given** 无拓扑许可的机器，
   **When** 跑同一条链，
   **Then** 脚本**以非零退出**并在证据文件里写明原因，
   **而不是**因 `RunAnalysis` 返回 0 就误判成功。

### User Story 2 - 每一步都有**回读**判据，不靠返回码（Priority: P1）

**Why this priority**: 本项目已累计**五处**「返回码撒谎」（见
`docs/A9-solve-attempts.md`）。用返回码当判据会让失败伪装成成功。

**Independent Test**: 证据 JSON 里每一步都带一个**回读值**（选区计数 /
`MaterialIdName` / `ElementCount` / `Results` 非空 + 图数），而不是单个状态码。

**Acceptance Scenarios**:

1. **Given** 夹具没选中任何面，
   **When** 跑到求解，
   **Then** 判据应在**夹具那一步**就红，而不是等到求解后才发现。
2. **Given** `RunAnalysis` 返回 0 但许可缺失，
   **When** 读证据，
   **Then** `solve.ok` 必须为 `false`（因为它判的是 `Results` 非空）。

### User Story 3 - 节流与安全（Priority: P2）

**Why this priority**: 早期四次尝试把网格器推到 20–25 GB。

**Independent Test**: 证据 JSON 里有 `element_count` 与 `seconds`；
`element_count` 超阈值即判失败。

**Acceptance Scenarios**:

1. **Given** 网格参数被误传（如把毫米当米），
   **When** 划网格，
   **Then** 单元数会远超合理上限 ⇒ `mesh.ok` 为 `false`（阈值 `ELEMENT_SANE_MAX`）。

---

### Edge Cases

- **多实体零件/装配体**：官方硬约束「只能对**单实体零件**做拓扑优化」⇒ 本特性不覆盖，
  登记为限制。
- **零件没有材料**：`RunAnalysis` 报 19；判据应在**赋材料那一步**就红。
- **导出类结果**（`Export Smoothed Mesh` / 收敛曲线）：四源（接口清单 / DLL / CHM /
  运行期 `GetIDsOfNames`）均未查到可调用的公开方法 ⇒ **不在本特性范围**，记为查不到。

---

## Requirements *(mandatory)*

- **FR-001**: 必须有一条**可复跑的命令**产出机器可读的证据文件（含时间戳与逐步回读值）。
- **FR-002**: 每一步的判据必须是**回读值**，不得用返回码。
- **FR-003**: 求解成功的判据是 **`study.Results` 非空 + 图数 > 0**，
  且**必须专门断言 Material Mass 图存在**（本特性的核心判据）。
- **FR-004**: 任一步不达标 ⇒ 进程**非零退出**，且证据文件写明是哪一步、为什么。
- **FR-005**: 必须覆盖「无许可」这一失败形态并给出可诊断的信息，不得静默通过。
- **FR-006**: 不得使用真假值判成功码（`0` 是成功，而 `bool(0)` 为假）。
- **FR-007**: 采集脚本**不得**在 `pytest` 里自动运行（单次求解约 3 分钟且需许可）。
- **FR-008**: 跑完不得留下未关闭的文档与未结束的求解器进程。

---

## Success Criteria *(mandatory)*

- **SC-001**: `python tools/capture_topology_evidence.py` 在**有许可**的机器上
  以退出码 0 结束，`verdict == "pass"`。
- **SC-002**: 证据里 `material_mass_plot.ok == true`，`matched_plots` 含 Material Mass 图名。
- **SC-003**: `capabilities.yaml` 的 `topology_optimization.level == "verified"`
  且 `evidence` 指向**该命令行**（不只是文字）。
- **SC-004**: 四项门禁 + 全量回归与基线逐条相同。
- **SC-005**: 「无许可」时脚本以非零退出，且证据里能看出是**许可**问题
  （而不是笼统的「失败」）。

---

## Assumptions

- 拓扑优化需要 `SOLIDWORKS Simulation Professional/Premium` 许可；
  许可在 **SolidWorks 启动时签出** ⇒ 改许可设置后**必须重启 SolidWorks**。
- 「Material Mass」在中文界面显示为 **`材料质量1`**，英文界面为 `Material Mass 1`
  ⇒ 判据用正则 `(材料质量|Material\s*Mass)`，不硬编码单一语言。
