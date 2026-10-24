# Feature Specification: S1 — E1–E7 的验收规范与坏样件

**Feature Branch**: `349-e1-e7-acceptance`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "按 docs/ENGINEERING-PATH.md 第四、六节做 S1：为 E1–E7 每条定义采集器与判定器，写出好输入、已知坏输入、缺证据三组样件；把现有估算器明确限制为预检用途。"

## 来源（宪法原则 I）

| 需求 | 来源 | 出处 |
|---|---|---|
| FR-001～007 | ④ 本项目自身既有模式 | `docs/PROJECT-CHARTER.md` 第四节（E1–E7 定义） |
| FR-008 | ④ 本项目自身既有模式 | `docs/ENGINEERING-PATH.md` 第四节（采集器/判定器分离） |
| FR-009 | ④ 本项目自身既有模式 | `docs/state/facts/R-engineering-path.md` R-04/R-05/R-06/R-09（四个可零成本伪造的判据） |

## 为什么这个特性必须先做

`docs/ENGINEERING-PATH.md` 第十节第 4 条：**每条新检查器必须能拒绝一个真实坏样件**。

现有四个估算器已被实测证明**可用零成本伪造通过**（出处：`R-engineering-path.md`）：

| 判据 | 伪造方式 | 实测结果 |
|---|---|---|
| 草图 DOF（R-04） | 同一条关系重复 8 次 | DOF = 0，`is_acceptable: True` |
| 装配 DOF（R-05） | 同一对组件重复贴 6 次 coincident | `fully_constrained`，`releasing: True` |
| 图纸覆盖率（R-06） | evidence 传空串 | `ratio = 1.0`，`ok: True` |
| 规则服务（R-09） | 只传两个布尔 + 来源标签 | `PASS`，`outputs={}`、`citations=[]` |

S1 的任务就是把这四个洞变成**必被拒绝的负例**。

## User Scenarios & Testing

### User Story 1 - 每条 E 有采集器与判定器 (Priority: P1)

给定一个真实产物，采集器从中取数；判定器对冻结的要求判断。两者不混。

**Why this priority**: 没有采集器与判定器的分离，「我已经检查过」就永远无法被证伪。

**Independent Test**: 对每条 E 单跑其负例测试，必须拒绝。

**Acceptance Scenarios**:

1. **Given** 一个 E1 坏样件（删掉一条定位关系），**When** 采集 + 判定，**Then** 判为 fail
2. **Given** 一个 E1 好样件（全约束），**When** 采集 + 判定，**Then** 判为 pass
3. **Given** 采集失败，**When** 判定，**Then** 判为 unknown，不得判 pass

---

### User Story 2 - 四个已知伪造手法被拒绝 (Priority: P1)

R-04/R-05/R-06/R-09 的伪造方式必须被负例捕获。

**Why this priority**: 这是本项目「判据可被自我认证」这一历史病症的具体形态。

**Independent Test**: 四条负例测试全部红转绿（即从「能伪造」变成「被拒绝」）。

**Acceptance Scenarios**:

1. **Given** 同一配合重复 6 次，**When** 判 E4，**Then** 不得判 `fully_constrained`
2. **Given** 图纸义务 evidence 为空串，**When** 判 E5，**Then** 覆盖率不得为 1.0
3. **Given** 规则请求只带两个布尔，**When** 判 E7，**Then** 不得返回 PASS
4. **Given** 同一条草图关系重复 8 次，**When** 判 E1，**Then** 不得判 DOF = 0

### Edge Cases

- 某条 E 在首件对象上确实不适用（如单件的 E4）——如何记录才不算「失败兜底」？
- 采集器能取到值但值本身不可信（如 API 只返回状态枚举、不返回数值 DOF）——记 `unknown` 还是 fail？
- 判定器自身有 bug 时，如何与「产物不合格」区分？

## Requirements

### Functional Requirements

- **FR-001**～**FR-007**: 为 E1～E7 各提供一个采集器与一个判定器，接口统一
- **FR-008**: 统一结果必须含：检查 ID、要求 ID、对象/配置、观测是否完整、原始值与单位、期望值/依据、状态、原因、证据引用、产物版本、检查器版本
- **FR-009**: 顶层状态取 `pass / fail / unknown / not_applicable` 四值；运行失败另带错误码；**禁止把其他非空字符串当 true**
- **FR-010**: 现有估算器（`part_loop.DofPlan.total_dof`、`assembly.ConstraintGraph.total_dof`、`drawing_obligations.coverage`、`rule_service.evaluate_rule`）必须被明确标注为**预检用途**，且不得直接授权交付
- **FR-011**: 每条 E 必须有至少一个已知坏样件；坏样件必须真实触发拒绝

### Key Entities

- **Collector**：从实际产物取数，不判断
- **Judge**：对冻结要求判断，不取数
- **CheckResult**：统一结果结构（见 FR-008）
- **BadSample**：已知会失败的输入，用于证明判定器有效

## Success Criteria

### Measurable Outcomes

- **SC-001**: E1–E7 各有一条「好输入通过 / 已知坏输入拒绝 / 缺证据 unknown」三态测试，全部绿
- **SC-002**: R-04/R-05/R-06/R-09 四个伪造手法各有一条负例，全部拒绝
- **SC-003**: 四个现有估算器在文档与代码注释里被明确标注为预检用途
- **SC-004**: `python -B scripts/release_check.py` 返回 exit 0
- **SC-005**: 本特性结束时只叫「离线判据成立」，**不叫** E1–E7 真机通过（见 `ENGINEERING-PATH.md` 第六节 S1 完成标准）

## Assumptions

- 首件对象是机加工安装板 + 简单定位装配（`ENGINEERING-PATH.md` 第五节）
- 本特性不连 SolidWorks；真机采集器留到 S3/S4
- 「不适用」必须有理由，缺规则/缺采集能力记 `unknown`，不是不适用
