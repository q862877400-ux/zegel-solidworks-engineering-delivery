# Feature Specification: 阶段 4 · 受约束的自主规划，交付一套简单定位夹具

**Feature Branch**: `319-stage4-constrained-planning`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **阶段 4**（L453–481）
+ 业主指令「全自动持续推进所有的阶段，每轮结束都提交一下」

---

## §0 这一份规格要解决什么

**外部方案阶段 4 的目标**（逐字）：

> **目标**：一句圈内需求经有限澄清，生成 3–5 种自制件的静态定位夹具及资料包；
> **人工不直接编写工具序列**。
> **前置／接口**：需求与布局协议、语义黄金集、方法检索、问题／回答契约、
> 受控客户端与规划出口。

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | ★★ **`corpus/l3-semantic.yaml` 就是 S4-A 要的 60 条**，分布**完全对得上** | ✅ |
| 2 | 分布：`solvable` **24** · `missing_input` **12** · `capability_boundary` **12** · `adversarial` **12** | ✅ |
| 3 | 分组：`dev` **20** · `blind` **40** | ✅ |
| 4 | 每条带 `labels{function,interface,question,result}` + `needs_owner_judgment` | ✅ |
| 5 | `scripts/engineering/evaluation.py`（359 行）**已有** `EvalCase`/`EvalSet`/`ArmResult`/`AdmissionGate`/`wilson_upper_bound` | ✅ |
| 6 | `scripts/engineering_contract.py`（488 行）**已有** `EngineeringContract`/`Quantity`/`ParameterDomain`/`Assumption` | ✅ |
| 7 | `scripts/engineering/compiler.py`（678 行）**已有** `METHOD_LIBRARY`（4 方法）+ `RejectCode`（8 码） | ✅ |
| 8 | `tools/check_corpus.py`（263 行）+ `tests/test_corpus_315.py`（109 行）**已有** | ✅ |
| 9 | ★★ **没有规划器**（`Planner` / `plan_from_requirement`） | ✅ **缺口** |
| 10 | ★★ **没有方法检索**（按需求找候选方法） | ✅ **缺口** |
| 11 | ★★ **没有 DesignIR**（需求 → 设计意图的中间表示） | ✅ **缺口** |
| 12 | ★★ **没有候选预算检查**（4096 token）与**出站许可**（数据/余额） | ✅ **缺口** |

**⇒ 阶段 4 的真实工作量 = 补 4 个缺口（#9~#12）+ 把语料与评估器接起来。**

---

## §2 五件新增契约（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **G1** | **需求与布局协议** | `scripts/engineering/design_ir.py` | 一句需求 → `DesignIR`（功能/接口/约束/待答）；**缺关键输入 ⇒ `WAITING_INPUT`** |
| **G2** | **方法检索** | `design_ir.py` 的 `retrieve_methods()` | 按 `DesignIR` 找候选方法；**候选不超 4096 token** |
| **G3** | **问题／回答契约** | `design_ir.py` 的 `elicit()` | 关键缺项 ⇒ `WAITING_INPUT` 且 **COM 写调用数 = 0**；**最多两批**主动问题 |
| **G4** | **受控客户端 / 出站许可** | `design_ir.py` 的 `outbound_permit()` | 数据或余额不获准 ⇒ **出站请求数 = 0** |
| **G5** | **规划出口** | `scripts/engineering/planner.py` | `DesignIR` → **3–5 种**方案 → 可编译计划；**人工不写工具序列** |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 把一句需求解析成 `DesignIR`（功能 / 接口 / 约束 / 待答问题）
- **FR-002**: **关键缺项** MUST 保持 `WAITING_INPUT`，且**不写 CAD**（COM 写 = 0）
- **FR-003**: 主动提问 MUST **最多两批**
- **FR-004**: 方法检索的**每次候选** MUST **不超 4096 token**
- **FR-005**: 数据或余额**未获准** ⇒ **出站模型请求数 = 0**
- **FR-006**: 未知费用 MUST **不释放预算预占**
- **FR-007**: 系统 MUST 产出 **3–5 种**方案（★ 不是一种）
- **FR-008**: 每个方案 MUST **可编译**（★ 走阶段 1 的名字解析 + 参数绑定）
- **FR-009**: **应等待或拒绝却进入执行**的次数 MUST = 0（★ 关键误放为零）
- **FR-010**: **关键需求不满足却获放行**的次数 MUST = 0
- **FR-011**: 可解盲题**正确且可编译**率 MUST **≥90%**
- **FR-012**: **近似变体 MUST 不跨组**（★ 开发/盲测不泄漏）
- **FR-013**: 系统 MUST **不把 LLM 自评当语义证明**（★ 保留人工标签）

### Key Entities

- **DesignIR**：`requirement` · `function` · `interface` · `constraints` · `open_questions` · `state`
- **MethodCandidate**：`method_id` · `score` · `tokens` · `applicable`
- **ElicitBatch**：`batch_index` · `questions` · `answers`
- **OutboundPermit**：`allowed` · `reason`（`DATA_NOT_PERMITTED` / `BUDGET_NOT_PERMITTED` / `COST_UNKNOWN`）
- **PlanCandidate**：`variant_index` · `plan`（`ExecutablePlan`）· `compile_ok`

---

## §4 Success Criteria

- **SC-001**: **应等待或拒绝却进入执行 = 0**
- **SC-002**: **关键需求不满足却获放行 = 0**
- **SC-003**: 可解盲题**正确且可编译**率 **≥90%**
- **SC-004**: 关键缺项一直 `WAITING_INPUT`，**COM 写 = 0**
- **SC-005**: **最多两批**主动问题
- **SC-006**: 每次候选 **≤4096 token**
- **SC-007**: 数据/余额拒绝时**出站请求 = 0**
- **SC-008**: 未知费用**不释放预算预占**
- **SC-009**: 每例产出 **3–5 种**方案
- **SC-010**: **近似变体不跨组**

---

## §5 反向验证（★ 规格要求的三类已标定坏计划）

| # | 突变 | 期望 |
|---|---|---|
| **Q1** | 注入「**整机需求仅返回一块板**」 | 评估器必须判**失败** |
| **Q2** | 注入「**漏定位关系**」 | 评估器必须判**失败** |
| **Q3** | 注入「**漏关键输入却标可执行**」 | 评估器必须判**失败** |
| **Q4** | **关闭一个必需功能检查** | 其独立定点测试必须**失败** |
| **Q5** | **移除等待状态写入门禁** | 对应测试必须失败 |
| **Q6** | **移除候选预算检查** | 对应测试必须失败 |
| **Q7** | **移除出站许可或费用预占** | 对应测试必须失败 |

---

## §6 明确不做

- **不做**云端 LLM 真调用（★ 那是**业主的决定**：不认证未纳管客户端 → 业主已说「这个也不管」；
  ★ 本规格只做**受控客户端与出站许可**的**结构**，不真发请求）
- **不做**阶段 5~7（各自独立规格）
- **不重写** `evaluation.py` / `engineering_contract.py` / `compiler.py`（★ 扩展，不推倒）
- **不把 LLM 打分包装成确定性认证**（★ 外部方案 §新增风险 7 逐字）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/319-stage4-constrained-planning/spec.md` | 本文件 |
| 2 | `specs/319-stage4-constrained-planning/data-model.md` | 数据结构 |
| 3 | `scripts/engineering/design_ir.py` | **G1 需求协议 · G2 方法检索 · G3 问答 · G4 出站许可** |
| 4 | `scripts/engineering/planner.py` | **G5 规划出口**（3–5 方案） |
| 5 | `tests/test_stage4_planner.py` | G1~G5 契约 + 反向验证 Q1~Q7 |
| 6 | `tools/run_stage4_corpus.py` | 60 条语料评估入口（20 开发 / 40 盲测） |
| 7 | `specs/319-stage4-constrained-planning/acceptance.md` | 验收记录 |
