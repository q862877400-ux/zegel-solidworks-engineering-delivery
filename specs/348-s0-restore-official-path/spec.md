# Feature Specification: S0 — 恢复首件所需的正式通路，冻结可复现基线

**Feature Branch**: `348-s0-restore-official-path`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "按 docs/ENGINEERING-PATH.md 第六节的 S0 施工：修掉首件链路上的注册阻断与执行入口缺陷，使首件依赖能经正式入口解析/注册，相关测试收集和执行通过，且无放宽断言换绿。"

## 来源（宪法原则 I）

本特性的每个需求都有出处，取值限于 `AGENTS.md` 铁律 1 的四种合法来源。

| 需求 | 来源 | 出处 |
|---|---|---|
| FR-001 | ④ 本项目自身既有模式 | `docs/state/facts/R-engineering-path.md` R-03（14 条失败全为 `spec.allows` 缺失） |
| FR-002 | ④ 本项目自身既有模式 | 同上 R-15（`FinalDod.evaluate` 在重构中消失） |
| FR-003 | ④ 本项目自身既有模式 | 同上 R-14（`build_registry` 被重名打死） |
| FR-004 | ④ 本项目自身既有模式 | 同上 R-16（工程层聚焦测试合计红面） |
| FR-005 | ④ 本项目自身既有模式 | `docs/ENGINEERING-PATH.md` 第六节 S0 第 4 条（审计收尾命令） |

## User Scenarios & Testing

### User Story 1 - 编译入口能跑通 (Priority: P1)

工程师调用方法编译入口，得到一个可执行计划，而不是 `AttributeError`。

**Why this priority**: 编译入口是整条首件链的第一个必经节点。它不通，S2/S3 全部无从谈起。

**Independent Test**: 单跑 `tests/test_ec03_compiler.py`，全绿即成立。

**Acceptance Scenarios**:

1. **Given** 一份合法的 `MethodSpec`，**When** 调用 `compile_contract`，**Then** 返回编译结果而不抛 `AttributeError`
2. **Given** 一个落在适用域外的设备类别，**When** 编译，**Then** 明确拒绝而不是静默通过

---

### User Story 2 - 最终 DoD 入口能跑通 (Priority: P1)

调用 `FinalDod.evaluate()` 得到一个结构化判定结果。

**Why this priority**: 阶段 322 的验收报告依赖它；它不存在，那份「全过」的结论就无法复现。

**Independent Test**: 单跑 `tests/test_stage7_housing.py`，全绿即成立。

**Acceptance Scenarios**:

1. **Given** 一组已收集的案例，**When** 调用 `evaluate()`，**Then** 返回含六条判据的结构化结果
2. **Given** 一个门禁未全过的案例集，**When** 调用 `evaluate()`，**Then** 判定为不通过

---

### User Story 3 - 规划出口能跑通 (Priority: P1)

调用 `plan_from_requirement()` 得到候选方案集，而不是 `RegistryError`。

**Why this priority**: 规划出口是 S2「结构化需求到方法计划单一映射」的落点。

**Independent Test**: 单跑 `tests/test_stage4_planner.py`，全绿即成立。

**Acceptance Scenarios**:

1. **Given** 一份四孔安装板需求，**When** 规划，**Then** 返回 3–5 个可编译候选
2. **Given** 注册表里存在同义重名工具，**When** 构建注册表，**Then** 不抛 `duplicate-canonical-name`

### Edge Cases

- 编译入口的 `allows` 语义若与既有 `applies_to` 冲突，以哪个为准？
- `FinalDod.evaluate` 重建后，历史验收记录里的判定字段是否还能对上？
- 修重名时，若两份声明语义不同，保留哪一份？

## Requirements

### Functional Requirements

- **FR-001**: `compile_contract` 必须能对每个候选方法判定适用性，且该判定有明确定义，不得调用不存在的属性
- **FR-002**: `FinalDod` 必须提供 `evaluate()`，返回含「零失败 / 全门禁 / 人工接管 / 台账证据 / 图样义务 / 范围声明」六类判定的结构
- **FR-003**: `build_registry()` 必须能在存在同义工具时构建成功，或给出**指向具体冲突对**的错误
- **FR-004**: 上述三处修复后，`tests/test_ec03_compiler.py`、`tests/test_stage7_housing.py`、`tests/test_stage4_planner.py` 必须全绿，且**不得通过放宽断言达成**
- **FR-005**: `tools/round_chain.ps1` 的副作用（`git add -A`、关闭 SolidWorks）必须显式化，不得把它当只读检查运行

### Key Entities

- **MethodSpec**：方法定义，持有适用域信息；当前基类 `ApplicabilityMixin` 只有 `applies_to()`
- **FinalDod**：阶段 322 的最终验收对象；当前只剩字段
- **Registry**：工具名 → 实现 的注册表；同名冲突时抛 `RegistryError`

## Success Criteria

### Measurable Outcomes

- **SC-001**: `python -B -m pytest tests/test_ec03_compiler.py -q` 返回 exit 0
- **SC-002**: `python -B -m pytest tests/test_stage7_housing.py -q` 返回 exit 0
- **SC-003**: `python -B -m pytest tests/test_stage4_planner.py -q` 返回 exit 0
- **SC-004**: `python -B scripts/release_check.py` 返回 exit 0 且 `status` 为 `pass`
- **SC-005**: 四个工程层测试文件的合计失败数从 25 降到 0（基线见 `docs/state/facts/R-engineering-path.md` R-16）

## Assumptions

- 三个阻断都是实现层缺陷，不是设计层缺陷；不需要改 E1–E7 判据
- `applies_to()` 的语义足以支撑适用性判定，只需在 `compile_contract` 侧改调用
- `FinalDod.evaluate` 的历史实现可从 git 历史找回（`git show a695ac62`）
- 本特性不引入任何新的外部依赖
