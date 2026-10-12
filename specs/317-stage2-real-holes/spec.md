# Feature Specification: 阶段 2 · 真实孔组、规则、工程图与参数变更

**Feature Branch**: `317-stage2-real-holes`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` 的**阶段 2**
+ 业主指令「按照 spec 的规范，设置好目标，全自动持续推进，每轮结束都提交一下」

---

## §0 这一份规格要解决什么

**外部方案的阶段 2 目标**（逐字）：

> **目标**：得到真正可审核的单零件资料包。
> **新增契约**：子方法展开、共享基准、规则评价、图纸义务、变更传播。

**本规格把上面五件「新增契约」变成可验收的东西。**

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `scripts/engineering/rules.py` 有 **427 行**，`Verdict` 只有 **4 档**（PASS/FAIL/UNKNOWN/NEEDS_CLARIFICATION） | ✅ |
| 2 | 而阶段 2 要求 **七种固定结果**（含 `RuleError(MISSING_INPUT)` / `RuleError(UNIT_MISMATCH)` / `NOT_APPLICABLE` / `INDETERMINATE(SOURCE_MISSING)` / `INDETERMINATE(STATUS_UNKNOWN)`） | ✅ **缺 5 种** |
| 3 | `part_loop.py` 有 8 个函数，**没有孔组**（`reference_hole_positions` 只是"参考孔位"） | ✅ **缺口** |
| 4 | **没有图纸义务模块** —— `processes.py` 只有 4 个工艺函数（钣金/焊件），与"工程图"无关 | ✅ **缺口** |
| 5 | **没有子方法展开** —— 阶段 1 给 `hole_group` 的拒绝码是 `sub-method-not-expanded` | ✅ **缺口** |
| 6 | **没有变更传播** —— 没有「改尺寸 → 重建 → 出图 → 校验」的编排 | ✅ **缺口** |

**⇒ 阶段 2 的真实工作量 = 补 5 个缺口。**

---

## §2 五件新增契约（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **D1** | **子方法展开** | `scripts/engineering/expand.py` | `hole_group` 作为步骤时**展开成具体工具序列**（含参数绑定）；展开后**递归可解析** |
| **D2** | **共享基准** | `registry.py` 的 `PlanStep.datums` | 多步共用一个基准名；**基准改了所有引用它的步骤都改** |
| **D3** | **规则评价（七档）** | `scripts/engineering/rules.py` 扩展 | 七种固定结果**机器可判**；★ **缺依据的关键规则不得报通过** |
| **D4** | **图纸义务** | `scripts/engineering/drawing.py` | 原生工程图 + PDF；**关键尺寸与技术要求覆盖率 100%** |
| **D5** | **变更传播** | `scripts/engineering/change.py` | 改尺寸 ⇒ 重建 ⇒ 出图 ⇒ 校验；**无旧模型/旧尺寸/旧证据混入** |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: `expand_plan()` MUST 把方法 id 形式的步骤展开成工具序列（★ 递归、深度受限）
- **FR-002**: 展开后 MUST **递归可解析**（★ 展开产物里不得再有方法 id）
- **FR-003**: 展开 MUST 带**参数绑定**（★ 子方法要能接收父方法的参数）
- **FR-004**: 展开深度 MUST 有上限（★ 防循环）
- **FR-005**: 系统 MUST 支持**共享基准**：`PlanStep.datums` 声明它用哪个基准
- **FR-006**: 规则评价 MUST 产出**七档**之一：`PASS` / `FAIL` / `RuleError(MISSING_INPUT)` / `RuleError(UNIT_MISMATCH)` / `NOT_APPLICABLE` / `INDETERMINATE(SOURCE_MISSING)` / `INDETERMINATE(STATUS_UNKNOWN)`
- **FR-007**: **缺依据**（无源）MUST ⇒ `INDETERMINATE(SOURCE_MISSING)`，**不得**报 `PASS`
- **FR-008**: **效力未知** MUST ⇒ `INDETERMINATE(STATUS_UNKNOWN)`，**不得**报 `PASS`
- **FR-009**: **单位不符** MUST ⇒ `RuleError(UNIT_MISMATCH)`（★ 不是 PASS）
- **FR-010**: **缺必填量** MUST ⇒ `RuleError(MISSING_INPUT)`
- **FR-011**: **超适用范围** MUST ⇒ `NOT_APPLICABLE`
- **FR-012**: 工程图 MUST 覆盖**全部关键尺寸**与**技术要求**
- **FR-013**: 模型 / 图纸 / 报告 MUST **版本一致**
- **FR-014**: 变更传播 MUST 使受影响产物**全部刷新**（★ 不许留旧版本）
- **FR-015**: 所有产物 MUST 带**内容摘要**（★ 用于判"新旧混入"）
- **FR-016**: 每次执行 MUST 走阶段 1 的**授权 + 名字解析 + 参数绑定**（★ 不绕过）

### Key Entities

- **ExpandedPlan**：`method_id` · `steps`（全是工具步骤）· `expand_trace`（展开过程）
- **DatumSpec**：`name` · `role`（`primary` / `secondary`）· `source_step`
- **RuleOutcome**：`verdict`（七档之一）· `rule_id` · `citation` · `detail`
- **DrawingObligation**：`name` · `kind`（`dimension` / `note` / `tolerance`）· `covered` · `evidence`
- **ArtifactDigest**：`path` · `sha256` · `kind`（`model` / `drawing` / `report`）· `revision`

---

## §4 Success Criteria

- **SC-001**: 孔是**真几何**（★ 回读孔数与孔位，不是"步骤回成功"）
- **SC-002**: **独立计算扣除体积**并与实测对比
- **SC-003**: 孔位、孔轴、尺寸、体积通过冻结判据
- **SC-004**: 工程图**可重开**
- **SC-005**: 关键尺寸及技术要求覆盖率 **100%**
- **SC-006**: 模型 / 图纸 / 报告**版本一致**
- **SC-007**: **三次独立启动全部通过**
- **SC-008**: 缺依据的关键规则**不能报通过**
- **SC-009**: 子方法展开后**递归可解析**（0 个未展开的方法 id）
- **SC-010**: 变更传播后**无旧模型/旧尺寸/旧证据**

---

## §5 反向验证（★ 三类突变必须被发现）

| # | 突变 | 期望 |
|---|---|---|
| **N1** | 让一个**孔步骤只返回成功而不执行** | 检查必须发现（★ 判据是**回读几何**，不是步骤返回值） |
| **N2** | 让**图纸保留旧版本** | 检查必须发现（★ 判据是**内容摘要**） |
| **N3** | 把**规则缺证据分支改成默认通过** | 检查必须发现（★ 判据是 `INDETERMINATE` 不得当 `PASS`） |

---

## §6 明确不做

- **不做**跨零件在位设计（方案 ① 独立攻关）
- **不做**云端 LLM 规划（阶段 4）
- **不做**多物理场 / 自由曲面（Anti-Scope）
- **不重写** `rules.py`（★ 扩展，不推倒）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/317-stage2-real-holes/spec.md` | 本文件 |
| 2 | `specs/317-stage2-real-holes/data-model.md` | 数据结构 |
| 3 | `scripts/engineering/expand.py` | D1 子方法展开 + D2 共享基准 |
| 4 | `scripts/engineering/rules.py` | D3 七档规则评价（扩展） |
| 5 | `scripts/engineering/drawing.py` | D4 图纸义务 |
| 6 | `scripts/engineering/change.py` | D5 变更传播 |
| 7 | `tests/test_stage2_expand.py` | D1/D2 契约 + 反向验证 |
| 8 | `tests/test_stage2_rules.py` | D3 七档契约 + N3 |
| 9 | `tests/test_stage2_drawing.py` | D4/D5 契约 + N1/N2 |
| 10 | `tools/run_stage2_plate.py` | 生产入口（真机，三次独立启动） |
| 11 | `specs/317-stage2-real-holes/acceptance.md` | 验收记录 |
