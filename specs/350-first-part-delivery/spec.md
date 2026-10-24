# Feature Specification: S2–S6 — 首件交付族的冻结、施工与发布

**Feature Branch**: `350-first-part-delivery`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "按 docs/ENGINEERING-PATH.md 第六节的 S2–S6：冻结首件需求与最小规则包，做成原生可编辑板件真过 E1–E3，接上装配/图样/工艺，真实 DeepSeek 端到端，限定发布。"

## 前置

本特性**依赖** `specs/348-s0-restore-official-path/`（通路修复）与
`specs/349-e1-e7-acceptance/`（判据与坏样件）都已完成。
两者未完成时本特性不得开工。

## 来源（宪法原则 I）

| 需求 | 来源 | 出处 |
|---|---|---|
| FR-001～003 | ④ 本项目自身既有模式 | `docs/ENGINEERING-PATH.md` 第六节 S2 |
| FR-004～006 | ④ 本项目自身既有模式 | 同上 S3 |
| FR-007～009 | ④ 本项目自身既有模式 | 同上 S4 |
| FR-010～012 | ④ 本项目自身既有模式 | 同上 S5 |
| FR-013～014 | ④ 本项目自身既有模式 | 同上 S6 |
| 首件范围 | ④ 本项目自身既有模式 | `docs/PROJECT-CHARTER.md` 第五节 |

## User Scenarios & Testing

### User Story 1 - 首件需求被冻结且可执行 (Priority: P1)

工程负责人确认功能、接口、主参数、材料、工艺、交付范围后，这些要求变成
**有承担者、有验收者**的规则包。

**Why this priority**: 没有冻结的需求，「合格」就没有参照物。

**Independent Test**: 每条硬要求在需求表里能找到执行承担者与验收承担者。

**Acceptance Scenarios**:

1. **Given** 一份四孔安装板需求，**When** 冻结，**Then** 孔数/孔型/位置/材料/图样/配合各有承担节点
2. **Given** 一个缺失的尺寸，**When** 冻结，**Then** 必须提问，不得填默认值

---

### User Story 2 - 板件真过 E1–E3 (Priority: P1)

生成的板件在**已交付件副本**上改主参数后能重建、特征树可编辑、草图全约束。

**Why this priority**: 这是「像机械工程师」与「画得像」的分水岭。

**Independent Test**: 名义件与扰动件都通过 E1–E3 三态检查。

**Acceptance Scenarios**:

1. **Given** 一个已交付板件，**When** 改板宽 100→120，**Then** 孔位随之联动且无特征错误
2. **Given** 一个只能靠初始坐标画对的件，**When** 判 E1，**Then** 不通过

---

### User Story 3 - 装配、图样、工艺接上，形成首个 E1–E7 交付包 (Priority: P2)

**Why this priority**: 单件过了 E1–E3 不等于可交付；图样与工艺是工程交付的另一半。

**Independent Test**: 同一首件的 E1–E7 全部适用义务有实证。

**Acceptance Scenarios**:

1. **Given** 一份图纸，**When** 判 E5，**Then** 必要标注逐项绑定到真实图纸对象
2. **Given** 一份只能导出 PDF 但核不了语义的图，**When** 判 E5，**Then** 不通过

---

### User Story 4 - 真实 DeepSeek 端到端 (Priority: P2)

**Why this priority**: 前面全过但模型接不上，等于系统只对测试脚本有效。

**Independent Test**: 一个真实自然语言任务通过完整链并交付首件。

**Acceptance Scenarios**:

1. **Given** 一句中文需求，**When** 真实模型跑完整链，**Then** 产出首件交付包
2. **Given** 一个域外任务，**When** 提交，**Then** 不写 CAD 且明确拒绝

---

### User Story 5 - 限定发布 (Priority: P3)

**Why this priority**: 不限定范围的「全支持」是虚假承诺。

**Independent Test**: 发布说明写明支持的参数域、工艺、版本、规则包版本、人工审核条件。

**Acceptance Scenarios**:

1. **Given** 一个超出已发布参数域的请求，**When** 提交，**Then** 被拒绝而不是勉强生成

### Edge Cases

- 首件的载荷未知时，能否当「低风险练习」放行？（`ENGINEERING-PATH.md` 第五节：不可）
- 图样 API 到不了必需标注时，S4 是否停线？
- 真实模型理解失败与执行失败，如何分开计数？

## Requirements

### Functional Requirements

- **FR-001**: 首件每条硬要求必须有执行承担者与验收承担者
- **FR-002**: 关键规则必须有原始依据、适用性、输入、独立参考例
- **FR-003**: 换材料/工艺/规则版本、移除引用或未确认参数，均不得继续旧批准
- **FR-004**: 板件的位置/方向/大小由几何约束 + 尺寸约束驱动，不得全固定
- **FR-005**: 主尺寸/基准/孔位/特征必须有稳定语义引用，跨重建不依赖选区或下标
- **FR-006**: 在**已交付件副本**上改主参数后，下游联动、特征无错、保存重开仍成立
- **FR-007**: 装配有地件、有功能配合；回读配合目标与实际剩余运动
- **FR-008**: 必要标注清单由功能/制造/检验要求生成，逐项绑定真实图纸对象
- **FR-009**: 生成图样时不得固定追加材料/公差文字，必须取批准需求
- **FR-010**: 真实 DeepSeek 接收自然语言需求、补问、产出结构化提议
- **FR-011**: 计划冻结后改参数/改文件/换配置/取消/断网/超时/保存失败，均不得自动重放非幂等写入
- **FR-012**: 人工接管单独记录，不藏在成功率里
- **FR-013**: 发布说明写明支持的参数域、工艺、SW 版本/配置、规则包版本、人工审核条件
- **FR-014**: 规则/方法升级必须能识别受影响交付并使旧证据失效

### Key Entities

- **RequirementSheet**：冻结后的首件需求（含承担者与验收者）
- **RulePack**：最小规则包
- **DeliveryPackage**：首件交付包（原生件 + 装配 + 图纸 + PDF + BOM + E1–E7 报告 + 证据）
- **ReleaseManifest**：发布说明（支持范围 + 版本绑定）

## Success Criteria

### Measurable Outcomes

- **SC-001**: 首件每条硬要求在需求表里有承担者与验收者（无遗漏）
- **SC-002**: 名义件与扰动件都真过 E1–E3
- **SC-003**: 同一首件的 E1–E7 全部适用义务有实证；E4/E6 不得靠列「不适用」通过
- **SC-004**: 一个真实自然语言任务通过完整链并交付首件
- **SC-005**: 非法任务不写 CAD；合法任务不能靠全拒绝通过安全测试
- **SC-006**: 他人按发布说明能复现（干净环境）
- **SC-007**: 自动状态只能到「待工程审核」，正式交付需具名批准

## Assumptions

- 首件是机加工安装板 + 简单定位装配
- 具体材料、接口、公差、制造条件在需求冻结时确认，本特性不预选标准等级
- 载荷未知时先补输入，或明确只交几何设计草案
- 所有真机工作串行，不并发控制同一 SolidWorks 会话
