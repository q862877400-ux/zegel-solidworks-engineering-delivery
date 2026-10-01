# Feature Specification: 视图读取 + 体上实体枚举（并**只挂可注入的那 2 个**）

**Feature Branch**: `126-view-selection-batch` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A3（`docs/backlog-8h.md`）—— 原列 4 个，实测后**只挂 2 个**。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `get_active_view` | **本项目自身**（包装 `scripts/sw_view.py`）| 本仓库 **MIT** |
| 暴露 `entities_on_body` | **本项目自身**（包装 `scripts/sw_selection_spec.py`）| 本仓库 **MIT** |
| `kind` 的合法值（`EDGE`/`FACE`） | **本项目自己的常量** `sw_selection_spec.ENTITY_KINDS` | 本仓库 **MIT** |
| 工具声明形状 | 既有 `tool_specs_batch7.py`（`inject="model"` 的先例）| 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能读视图/枚举体上实体（Priority: P1）
用户要问"现在是什么视角"、"这块板上有几条边几个面"，现在只能写脚本。

**Independent Test**: 注册后 `all_specs()` 出现这 2 个名字，规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 51 变 **53**
2. **Given** `entities_on_body`，**When** 传 `kind="EDGE"` 与 `kind="FACE"`，**Then** 都能被接受（`ENTITY_KINDS` 只有这两个）
3. **Given** `entities_on_body` 的描述，**When** 读它，**Then** 看到**序号不保证稳定**的警告（引自该函数 docstring）

### User Story 2 - 挂不了的要说清为什么（Priority: P2）
`activate_view` / `add_perspective` 在队列里，但本批**不挂** —— 这个决定必须留下理由与去处。

**Independent Test**: 读 `tool_specs_batch14.py` 头部，能看到"首参不是约定注入点"+"没有 `view` 注入器"+"记进 A10"。

**Acceptance Scenarios**:
1. **Given** 那两个函数，**When** 查它们的 `inspect.signature`，**Then** 首参是 `view`（**不在** `model`/`sw_app`/`study` 里）
2. **Given** 既有 `tool_specs_batch*.py`，**When** 搜 `ActiveView|sw_view`，**Then** **无先例** ⇒ 不能照抄

## 明确不做
| 不做 | 理由 |
|---|---|
| 挂 `activate_view` / `add_perspective` | ★ 需要 `view` 注入器或包装层 ⇒ 记进 A10，**先定行为** |
| 真机验证这 2 个 | ★ 暴露 ≠ 验证；排 B 组 |
