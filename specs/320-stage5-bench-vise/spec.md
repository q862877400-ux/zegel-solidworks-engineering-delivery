# Feature Specification: 阶段 5 · 平口钳：几何与夹紧功能的设计义务汇合

**Feature Branch**: `320-stage5-bench-vise`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **阶段 5**（L483–501）
+ 业主指令「全自动持续推进所有的阶段，每轮结束都提交一下」

---

## §0 这一份规格要解决什么

**外部方案阶段 5 的目标**（逐字）：

> **目标**：在已冻结载荷、行程、接口、材料与制造要求下，生成平口钳零件、装配、
> 图纸和计算资料。
> **前置／接口**：导向、螺杆、螺母、钳口的共享接口；适用的强度／刚度／传动与
> 锁紧计算；已声明的运动学表示。

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `scripts/engineering/assembly.py`（403 行）**已有** `DofVerdict`（5 档）/ `MateKind`（5 种 + `REMOVES` 表）/ `Component` / `Mate` / `ConstraintGraph`（含 `total_dof()` + `verdict()`）/ `InterferenceScan` / `ToleranceChain` / `MaintenanceCheck` | ✅ |
| 2 | `DofVerdict.RELEASING = (FULLY_CONSTRAINED, EXPECTED_MOTION)` —— ★ **「预期运动」是允许的**（★ 那正是平口钳活动钳口需要的） | ✅ |
| 3 | `ConstraintGraph.verdict()` 有**五档保守顺序**（过约束 → 冗余 → 预期运动 → 欠约束 → 全约束） | ✅ |
| 4 | `InterferenceScan.verdict()` 已有**三结论**：`interference` / `unknown`（★ 覆盖率 <1 时**不许说「无干涉」**）/ `pass` | ✅ |
| 5 | `scripts/engineering/part_loop.py`（314 行）**已有** `DofPlan` / `check_dof_plan` / `readback_verdict` / `load_case_allows_strength` | ✅ |
| 6 | `scripts/engineering/rule_verdicts.py`（阶段 2 建的）**已有七档**（含 `INDETERMINATE`） | ✅ |
| 7 | `scripts/engineering/drawing_run.py`（阶段 2 建的）**已有真机出图链** | ✅ |
| 8 | `corpus/l1-mainline.yaml` 提到「平口钳」**11 次**（★ 语料里有它的位置） | ✅ |
| 9 | ★★ **没有平口钳的共享接口模型**（导向 / 螺杆 / 螺母 / 钳口） | ✅ **缺口** |
| 10 | ★★ **没有导程 → 位移的传动计算** | ✅ **缺口** |
| 11 | ★★ **没有「无误固定活动钳口」的检查** | ✅ **缺口** |
| 12 | ★★ **没有螺纹工程定义**（★ 需求点名「核对螺纹规格」） | ✅ **缺口** |

**⇒ 阶段 5 的真实工作量 = 补 4 个缺口（#9~#12）+ 把既有装配/规则/出图资产接起来。**

---

## §2 四件新增契约（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **H1** | **共享接口模型** | `scripts/engineering/vise.py` | 导向 / 螺杆 / 螺母 / 钳口**共享接口**；改一处**受影响件全变** |
| **H2** | **传动计算** | `vise.py` 的 `lead_to_travel()` | 导程 × 圈数 = 位移；★ **独立检查**（★ 不靠 CAD） |
| **H3** | **活动钳口不得被误固定** | `vise.py` 的 `check_jaw_free()` | 活动钳口**有自由度**且**已标注** ⇒ `EXPECTED_MOTION`；★ **固定了就失败** |
| **H4** | **螺纹工程定义** | `vise.py` 的 `ThreadSpec` | 规格 / 螺距 / 公差 / 材料**齐**；★ 缺了 ⇒ 规则 `INDETERMINATE` |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 建**共享接口**（导向 / 螺杆 / 螺母 / 钳口）并可**回读**
- **FR-002**: **接口变更 MUST 传播**到受影响零件（★ 不相关件**可复用**）
- **FR-003**: 导程 → 位移 MUST **独立计算**（★ 与 CAD 位姿**分别**核对）
- **FR-004**: **活动钳口 MUST 有自由度**（★ 不得被固定）
- **FR-005**: 活动钳口的自由度 MUST **逐条标注**（★ 否则是 `UNDER_CONSTRAINED`）
- **FR-006**: 关键规则 MUST **无 `INDETERMINATE`**（★ 缺依据不得算通过）
- **FR-007**: 螺纹 MUST 有**工程定义**（规格 / 螺距 / 公差 / 材料）
- **FR-008**: 系统 MUST 完成**参数变更 + 保存重开**
- **FR-009**: 系统 MUST **不把几何通过当功能通过**（★ 体积通过不能代替功能检查）
- **FR-010**: 若只支持**外部参数化运动学** ⇒ MUST **明确验证该模型**，**不冒称**原生 Motion 算例跑通
- **FR-011**: 实际夹紧力**未做物理试验** ⇒ MUST NOT 标成「实物性能已证实」
- **FR-012**: 默认几何简化 MUST **已在要求中明确批准**，且图纸与计算**保留真实工程定义**

### Key Entities

- **SharedInterface**：`name` · `kind`（`guide`/`screw`/`nut`/`jaw`）· `value` · `unit`
- **ThreadSpec**：`standard` · `designation` · `pitch_mm` · `tolerance_class` · `material`
- **TravelCheck**：`lead_mm` · `turns` · `travel_mm` · `readback_mm` · `consistent`
- **JawFreedom**：`dof` · `annotated_motions` · `verdict`
- **ViseResult**：`interfaces` · `thread` · `travel` · `jaw` · `dof_verdict` · `rules`

---

## §4 Success Criteria

- **SC-001**: 规定工况**全部通过**
- **SC-002**: 关键规则**没有 `INDETERMINATE`**
- **SC-003**: **无误固定的活动钳口**（★ `EXPECTED_MOTION`）
- **SC-004**: 完成**参数变更和保存重开**
- **SC-005**: 图纸与计算**保留真实工程定义**（★ 螺纹规格 / 公差 / 材料都在）
- **SC-006**: 导程与位移关系**独立核对一致**
- **SC-007**: 共享接口变更**正确传播**（★ 不相关件可复用）

---

## §5 反向验证（★ 规格 §5 的四条突变）

| # | 突变 | 期望 |
|---|---|---|
| **R1** | **固定活动钳口** | 相关功能检查必须**失败** |
| **R2** | **删去导向关系** | 接口检查必须**失败** |
| **R3** | 把「**导程**」误绑成**另一字段** | 传动检查必须**失败** |
| **R4** | **删除螺纹工程定义** | 图纸/规则检查必须**失败** |
| **R5** | ★ **仅体积通过** | **不能**使其恢复为成功 |

---

## §6 明确不做

- **不做**真实物理夹紧力试验（★ FR-011：未做就**不得标成已证实**）
- **不冒称**原生 Motion 算例跑通（★ FR-010）
- **不做**阶段 6/7（各自独立规格）
- **不重写** `assembly.py` / `part_loop.py`（★ 扩展，不推倒）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/320-stage5-bench-vise/spec.md` | 本文件 |
| 2 | `scripts/engineering/vise.py` | **H1 共享接口 · H2 传动 · H3 钳口自由 · H4 螺纹定义** |
| 3 | `tests/test_stage5_vise.py` | H1~H4 契约 + 反向验证 R1~R5 |
| 4 | `tools/run_stage5_vise.py` | 验收入口（含真机档） |
| 5 | `specs/320-stage5-bench-vise/acceptance.md` | 验收记录 |
