# Feature Specification: 圆形阵列 + 旋转凸台（**并落定规则 2 的角度换算边界**）

**Feature Branch**: `130-angle-deg-boundary` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A6（`docs/backlog-8h.md`）。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `circular_pattern` / `revolve_boss` | **本项目自身**（包装 `scripts/sw_part.py`）| 本仓库 **MIT** |
| ★ 角度换算的实现 | **本项目既有助手** `scripts/sw_connect.py` 的 `deg()`（`value * math.pi / 180.0`）| 本仓库 **MIT** |
| ★ 换算该放在哪一层 | **既有先例** `mcp-server/tool_specs_batch3.py`（`_consumed` + `derived_args`）| 本仓库 **MIT** |
| 规则 2 的判据 | `AGENTS.md` §五 规则 2 + `docs/union-conventions.md` §规则 2 | 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 用**度**填角度，而不是弧度（Priority: P1）
用户在 MCP 上要写「阵列 90°」「旋转 360°」—— ★ 而不是每次自己乘 π/180。
**而目标函数的形参是 `angle_rad`** ⇒ 必须有东西在**边界**上换算一次。

**Independent Test**: 单独跑该批的守卫测试（不连 SolidWorks）。

**Acceptance Scenarios**:
1. **Given** `angle_deg=90`，**When** 走 `derived_args`，**Then** 得到 `angle_rad == π/2`（1.5707963267948966）
2. **Given** ★ **负例**：若只改名不换算，**Then** 目标函数会收到 **90**（≈ 57.3 倍）⇒ 几何静默错
3. **Given** `revolve_boss` 的 `axis_sketch_name=""`，**When** 走 `derived_args`，**Then** 得到 **`None`**（与目标函数默认对齐）

### User Story 2 - 规则 2 的「边界」要有**一个家**（Priority: P2）
换算若散落两处（工具里手写 π/180 + 助手里的 `deg()`）⇒ 迟早分叉。

**Independent Test**: 读 `tool_specs_batch17.py` 的 `_radians_of_deg`，它**import** 既有助手而不是手写常数。

**Acceptance Scenarios**:
1. **Given** 该批的换算函数，**When** 搜 `math.pi` / `180`，**Then** **不出现**（换算只从 `sw_connect.deg` 来）

## 明确不做
| 不做 | 理由 |
|---|---|
| 用 `param_alias` 改名了事 | ★ **只改名不换算会静默出错**（本批的核心）|
| 在工具里手写 `math.radians` | ★ 换算要**一个家**（既有 `deg()` 就是那个家）|
| 真机验证这两个工具 | ★ 暴露 ≠ 验证；且 `revolve_boss` 未在本机跑过 |
