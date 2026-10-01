# Feature Specification: 草图几何关系 + 镜像特征（并**按规则逐条分诊** `sw_part` 那 14 个）

**Feature Branch**: `128-sketch-relation-mirror-batch` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A5（`docs/backlog-8h.md`）—— 原写「`add_sketch_relation` / `add_dimension`」，**实测后只挂 2 个且与队列不同**。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `add_sketch_relation` / `mirror_feature` | **本项目自身**（包装 `scripts/sw_part.py`）| 本仓库 **MIT** |
| `relation_type` 的 12 个合法值 | **目标函数自己的 docstring**（`sw_part.add_sketch_relation`）| 本仓库 **MIT** |
| `sw_part` 14 个孤立能力的规则分诊 | **规则 2/3 + `orphan-capabilities.json` 的签名** | 本仓库 **MIT** |
| `insert_composite_curve` 是坏的 | **已知事实 121 / 124**（`InsertCompositeCurve` 一直返回 False）| 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能加草图关系 / 镜像特征（Priority: P1）
用户要"把这条线设成水平"、"镜像这个特征到另一侧"，现在只能写脚本。

**Independent Test**: 注册后 `all_specs()` 出现这 2 个名字，规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 54 变 **56**
2. **Given** `relation_type`，**When** 读描述，**Then** 看到 **12 个合法值**（`sgFIXED` … `sgCOINCIDENT`）
3. **Given** `mirror_plane_name`，**When** 读描述，**Then** 看到**基准面名随 UI 语言变**的提醒

### User Story 2 - 14 个要**逐个说清为什么挂/不挂**（Priority: P2）
队列只说了 2 个名字；另外 12 个的去处必须留下，否则下一轮又要重查。

**Independent Test**: 读 `tool_specs_batch16.py` 头部，14 个成员**逐条有归属**（本批 / 规则 2 / 规则 3 / 本来就坏）。

**Acceptance Scenarios**:
1. **Given** `add_dimension`，**When** 看它的形参，**Then** 是 `(model, x, y)` ⇒ **碰规则 3** ⇒ 留批
2. **Given** `insert_composite_curve`，**When** 查事实 121/124，**Then** 它**一直返回 False** ⇒ ★ **不挂**（不把已知坏的入口摊给用户）

## 明确不做
| 不做 | 理由 |
|---|---|
| 挂 `add_dimension`（队列原定的第二个）| ★ 形参是**裸坐标** `x, y` ⇒ 碰规则 3 ⇒ 题 A8 |
| 挂 `insert_composite_curve`（它是"干净"的）| ★ **本来就坏**（事实 121/124）⇒ 不假装它会好 |
| 挂其余 11 个 | 规则 2（长度/角度）或规则 3 ⇒ **逐条记明去处** |
| 真机验证这 2 个 | ★ 暴露 ≠ 验证；排 B 组 |
