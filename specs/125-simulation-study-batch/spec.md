# Feature Specification: 仿真研究族（报告 / 按控制划网格 / 建议网格尺寸）

**Feature Branch**: `125-simulation-study-batch` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A2（`docs/backlog-8h.md`）。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `generate_report` / `create_mesh_for_control` | **本项目自身既有模式**（包装 `scripts/sw_simulation_study.py`）| 本仓库 **MIT** |
| 暴露 `default_element_size_and_tolerance` | **本项目自身既有模式**（包装 `scripts/sw_simulation.py`，★ **不是** `_study`）| 本仓库 **MIT** |
| 工具声明形状 | 既有 `tool_specs_batch1.py` / `batch11` / `batch12` 的 `study` 模板 | 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能出研究报告（Priority: P1）
用户跑完一个算例后要一份报告文件，现在只能写脚本。

**Independent Test**: 注册后 `all_specs()` 里出现这三个名字，规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 48 变 **51**
2. **Given** 三个工具，**When** 跑规则 1/2/3，**Then** 全过
3. **Given** `units` 参数，**When** 读它的描述，**Then** ★ 看到**两源冲突**被**原样写出来**（不合并成一种说法）

### User Story 2 - 把"查不到"和"冲突"都摆在明面上（Priority: P2）
用户不该在踩坑后才知道哪个参数的值查不到、哪两处源互相矛盾。

**Acceptance Scenarios**:
1. **Given** `template` 参数，**When** 读描述，**Then** 明写「合法取值未在本地源中找到」
2. **Given** `units` 参数，**When** 读描述，**Then** 同时看到「既有工具说 -1 被拒」与「该函数真机实测 -1 可用」两句

## 明确不做
| 不做 | 理由 |
|---|---|
| 给 `template` 编候选值 | ★ 本地源查不到 ⇒ 铁律 5 不发明 |
| 合并 `units=-1` 的两处说法 | ★ 与事实 139「两个口径不合并」同型 |
| 真机验证这 3 个 | ★ 暴露 ≠ 验证；排 B 组 |
