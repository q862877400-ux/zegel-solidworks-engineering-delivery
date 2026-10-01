# Feature Specification: 结构化审查报告（并**只挂 1 个**、且**不暴露 list 型参数**）

**Feature Branch**: `127-review-report-batch` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A4（`docs/backlog-8h.md`）—— 原列 2 个，实测后**只挂 1 个**。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `build_review_report` | **本项目自身**（包装 `scripts/sw_review.py`）| 本仓库 **MIT** |
| 工具声明形状 | 既有 `tool_specs_batch7.py`（`inject="model"` + 无参/简单参的先例）| 本仓库 **MIT** |
| 「`list` 型参数无先例」这一判断 | **本项目既有 `tool_specs_batch*.py` 全量扫描**（见 T-12702）| 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能出结构化审查报告（Priority: P1）
用户要"看一眼这个零件、出一份审查报告 + 预览图"，现在只能写脚本。

**Independent Test**: 注册后 `all_specs()` 出现该名字，规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 53 变 **54**
2. **Given** 该工具，**When** 读它的 `params`，**Then** 只有 `output_dir` 与 `basename`（★ **`views`/`expected_outputs` 不暴露**）
3. **Given** 该工具的描述，**When** 读它，**Then** 能看到"另两个参数未暴露"的指向说明

### User Story 2 - 挂不了 / 不好挂的都要留理由（Priority: P2）
`activate_plot` 在队列里但不挂；`views`/`expected_outputs` 能挂但不挂 —— 两个决定都要有据。

**Acceptance Scenarios**:
1. **Given** `activate_plot`，**When** 看签名，**Then** 首参是 `results`（**不在** `model`/`sw_app`/`study` 里）
2. **Given** 既有批次，**When** 搜 `list` 型 `Param`，**Then** **空** ⇒ 无先例 ⇒ 不顺手引入

## 明确不做
| 不做 | 理由 |
|---|---|
| 挂 `activate_plot` | ★ 需 `results` 注入器或包装层 ⇒ 记进 A10，先定行为 |
| 暴露 `views` / `expected_outputs` | ★ `list` 型**无先例**；且它们是**可选参数**，不暴露不影响主要用途 ⇒ 记进 A10 |
| 真机验证这个工具 | ★ 暴露 ≠ 验证；排 B 组 |
