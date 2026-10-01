# Feature Specification: 静力学仿真整链**真机复验**

**Feature Branch**: `134-static-simulation-reverified` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 B1（`docs/backlog-8h.md`）—— 把 `simulation_and_fea` 的真机验收重跑一遍。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 重跑既有验收脚本 `tools/capture_simulation_evidence.py` | **本项目自身**（既有真机证据脚本，非新写）| 本仓库 **MIT** |
| 加载项可达性 | 事实 141 / 142 的修复（`ensure_simulation_addin`）| 本项目 **MIT** |

## User Scenarios & Testing

### User Story 1 - 确认静力学那条链也能跑绿（Priority: P1）
拓扑那条已在 `122` 复验 pass；静力学是**另一条链**（`ICWStudy` + 夹具/载荷 + 求解 + 4 张图），
需要单独确认 —— ★ 不能因为"同一根因"就推断它也通（**别用邻接关系代替证据**，事实 143）。

**Independent Test**: 单独跑 `python tools/capture_simulation_evidence.py`，看它自己的 `verdict`。

**Acceptance Scenarios**:
1. **Given** SW 2026 SP4.1 已连、加载项已由 `ensure_simulation_addin` 装上，
   **When** 跑该脚本，**Then** `verdict == "pass"` 且 JSON 里六步全 `ok`
2. **Given** 求解完成，**When** 读 `plot_names`，**Then** 含 `应力*` / `位移*` / `应变*`（而不是只有"品质"）
3. **Given** 该 JSON，**When** 看 `run_analysis_return_is_trustworthy`，**Then** 为 **`false`**
   —— ★ 即：**成功判据不是返回码**

## 明确不做
| 不做 | 理由 |
|---|---|
| 改这条链的任何代码 | 它本来就工作；本轮**只复跑取证据** |
| 声称"求解器不收敛"问题已解决 | ★ 那是另一件事（事实 142 已记：**成因仍未定**）|
