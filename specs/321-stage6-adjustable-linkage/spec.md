# Feature Specification: 阶段 6 · 可调连杆：验证受限闭环机构，而非拒绝所有环

**Feature Branch**: `321-stage6-adjustable-linkage`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **阶段 6**（L503–521）
+ 业主指令「全自动持续推进所有的阶段，每轮结束都提交一下」

---

## §0 这一份规格要解决什么

**外部方案阶段 6 的目标**（逐字）：

> **目标**：完成一种受支持的单自由度、单闭环平面连杆夹具；能分辨错误分支、
> 奇异区间与约束错误。
> **前置／接口**：阶段 5 的运动与接口基础；机构图、**独立约束求解器**、
> 分支标识、区间／工况验证报告。

**★★ 本阶段最容易做错的地方**（★ 外部方案 §5 R6 ④ 逐字）：

> 「**将一切图中有环都拒绝，正确闭链正例必须失败**，以防『**保守到失去能力**』」

⇒ ★★ **本规格的核心判据是「正例必须能过」**，★ 不是「把所有环都拒掉」。

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `part_loop.py` 的 `DofPlan` **已有** `is_acceptable()` —— ★★ **逐字承 EC05-T03**：「**有意保留自由度必须标注**，**不机械要求全锁死**」 | ✅ |
| 2 | `DofPlan.add_intentional_dof(name, why)` —— ★ **理由必填**（空理由 ⇒ 拒） | ✅ |
| 3 | `assembly.py` 的 `ConstraintGraph.verdict()` **已有五档**（过约束/冗余/预期运动/欠约束/全约束） | ✅ |
| 4 | `assembly.py` 的 `InterferenceScan.verdict()` **已有三结论** —— ★ 覆盖率 <1 时 **不许说「无干涉」** | ✅ |
| 5 | `DofVerdict.RELEASING = (FULLY_CONSTRAINED, EXPECTED_MOTION)` —— ★ **不要求自由度必须为 0** | ✅ |
| 6 | ★★ **没有平面四杆的闭环求解器**（`residual` / `branch_id` 全仓 0 命中） | ✅ **缺口** |
| 7 | ★★ **没有分支标识**（同一个闭环有两个装配分支） | ✅ **缺口** |
| 8 | ★★ **没有奇异区间检测** | ✅ **缺口** |
| 9 | ★★ **没有「采样证据 ⇒ `INDETERMINATE` + `BLOCKED_VERIFICATION`」** | ✅ **缺口** |

**⇒ 阶段 6 的真实工作量 = 补 4 个缺口（#6~#9）+ 复用 `DofPlan` / `ConstraintGraph` / `InterferenceScan`。**

---

## §2 四件新增契约（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **L1** | **独立约束求解器** | `scripts/engineering/linkage.py` 的 `solve_four_bar()` | 闭环残差 **≤ 容差**；★ **独立算**（★ 不靠 CAD） |
| **L2** | **分支标识** | `linkage.py` 的 `branch_of()` | 同一个输入有**两个解**；★ **选错分支 ⇒ 失败** |
| **L3** | **奇异区间** | `linkage.py` 的 `singular_scan()` | 在**端点与已知危险位置**检出奇异 |
| **L4** | **采样证据 ⇒ `INDETERMINATE`** | `linkage.py` 的 `continuity_verdict()` | 只有采样 ⇒ **`INDETERMINATE` + `BLOCKED_VERIFICATION`**；★ **不得自动交付** |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 用**独立约束求解器**算闭环（★ 不用 CAD 的位姿当输入）
- **FR-002**: 闭环残差 MUST **≤ 冻结容差**
- **FR-003**: 系统 MUST 能**分辨两个装配分支**并给出**分支标识**
- **FR-004**: **选错分支** MUST 被检出（★ 位姿误差超容差）
- **FR-005**: 系统 MUST 在**端点与已知危险位置**检查奇异
- **FR-006**: 系统 MUST 报出**目标自由度**与**实际自由度**是否一致
- **FR-007**: 碰撞**若只采样** ⇒ 验证结果 MUST 为 **`INDETERMINATE`**，
  运行状态 MUST 为 **`BLOCKED_VERIFICATION`**，★ **不能自动交付**
- **FR-008**: 系统 MUST **不拒绝所有环** —— ★ 正确的闭链正例**必须能过**
- **FR-009**: 若订单要求**连续无干涉**而只有采样证据 ⇒ MUST NOT 自动升级为**全行程证明**
- **FR-010**: 系统 MUST **不宣称**已支持通用机构综合

### Key Entities

- **FourBarSolution**：`theta3` · `theta4` · `residual` · `branch`
- **BranchId**：`OPEN`（`θ4 ∈ (0,π)`）/ `CROSSED`（`θ4 ∈ (π,2π)`）
- **SingularPoint**：`theta2_deg` · `kind`（`toggle` / `fold`）· `margin`
- **ContinuityVerdict**：`verdict` · `run_state` · `coverage` · `releasing`
- **LinkageResult**：`solution` · `branch` · `dof` · `singular` · `continuity`

---

## §4 Success Criteria

- **SC-001**: 受支持用例的**机构模型与执行 DAG 均有效**
- **SC-002**: **残差与位姿误差在冻结数值容差内**
- **SC-003**: **目标自由度与分支正确**
- **SC-004**: **没有未解决的指定区间义务**
- **SC-005**: 若要求连续无干涉而只有采样证据 ⇒ **`INDETERMINATE` + `BLOCKED_VERIFICATION`**
- **SC-006**: ★★ **正确的闭链正例必须能过**（★ 防「保守到失去能力」）

---

## §5 反向验证（★ 规格 §5 的四条 + 一条防保守）

| # | 突变 | 期望 |
|---|---|---|
| **T1** | **交换一个运动副连接对象** | 验证必须**失败** |
| **T2** | **选择错误装配分支** | 验证必须**失败** |
| **T3** | **加入锁死自由度的配合** | 验证必须**失败** |
| **T4** | ★★ **将一切图中有环都拒绝** | ★ **正确闭链正例必须失败** ⇒ ★ 即「全拒」策略**被本规格判为错** |
| **T5** | 只给**采样**证据却声称**全行程** | 必须**不自动交付** |

---

## §6 明确不做

- **不做**通用机构综合（★ FR-010：只做**一种**受支持的单自由度单闭环平面连杆）
- **不做**空间机构 / 多闭环
- **不做**阶段 7（独立规格）
- **不重写** `assembly.py` / `part_loop.py`（★ 扩展，不推倒）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/321-stage6-adjustable-linkage/spec.md` | 本文件 |
| 2 | `scripts/engineering/linkage.py` | **L1 闭环求解 · L2 分支 · L3 奇异 · L4 连续性判定** |
| 3 | `tests/test_stage6_linkage.py` | L1~L4 契约 + 反向验证 T1~T5 |
| 4 | `tools/run_stage6_linkage.py` | 验收入口 |
| 5 | `specs/321-stage6-adjustable-linkage/acceptance.md` | 验收记录 |
