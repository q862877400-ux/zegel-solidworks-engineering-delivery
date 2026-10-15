# Feature Specification: 草图关系枚举正名与公开调用契约收敛

**Feature Branch**: `222-relation-enum-and-public-contract`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "阅读施工规范，按 spec 规范施工接手这个项目。221 已把草图关系的**创建重放**风险离线收口，但留下两个已定位、未裁决的冲突：① `scripts/sw_sketch_relations.py::RELATION_TYPES` 与 `scripts/sketch_relations.py::SKETCH_CONSTRAINT_TYPES` 的数值都不等于官方 `swConstraintType_e`；② 已挂出去的 `solidworks_add_sketch_relation` 走 `sw_part.add_sketch_relation` 的字符串入口，无构造前状态门。本切片只做**枚举正名 + 公开契约收敛**，不碰 COM、不做几何验收。"

**前置依赖**: `specs/221-sketch-relation-dispatch-safety/`（已完成，视为不可变历史；本切片不修改它）。

## 现状核实（本切片的事实起点）

以下每条都已在本工作树内实读定位，不是推测：

| # | 事实 | 定位 |
|---|---|---|
| F1 | `RELATION_TYPES` 10 个平面约束的数值**全部**与官方不符，只有 `FIXED=19` 与官方 17 不同而非同表 | `scripts/sw_sketch_relations.py:32-44` |
| F2 | 该表还含官方枚举里**不存在**的名字：`EQUAL`、`MIDPOINT` | 同上；官方为 `SAMELENGTH=14`、`ATMIDDLE=12`，**无** `EQUAL`/`MIDPOINT` 成员 |
| F3 | `SKETCH_CONSTRAINT_TYPES` 19 项数值**同样**与官方不符（如 `coincident` 写 1，官方 9），且缺官方主枚举项 | `scripts/sketch_relations.py:68-88` |
| F4 | 两份官方源 + 出厂反射转储三源**逐项一致**：`C:\swapi\enums\swConstraintType_e.md`（86 项）、CHM 解包 `swconst` 页（86 项）、`_raw/enum_values_sldworks.txt`（86 项） | 三处已比对，数值全同 |
| F5 | `IModelDoc2::SketchAddConstraints` 的合法字符串是 `sgSAMELENGTH` / `sgATMIDDLE`，**没有** `sgEQUAL` / `sgMIDPOINT` | `C:\swapi\types\IModelDoc2\SketchAddConstraints.md` 的 Remarks 清单；官方例亦只用清单内名字 |
| F6 | `sw_part.add_sketch_relation` 的白名单 `_SG_RELATIONS` 含 `sgEQUAL`、`sgMIDPOINT`；加上 `sg` 前缀后原样透传字符串 | `scripts/sw_part.py` `_SG_RELATIONS` / `add_sketch_relation` |
| F7 | **正式挂出**的 `solidworks_add_sketch_relation` 参数说明把这个含错名的清单当合法值写给用户 | `mcp-server/tool_specs_batch16.py:60-74` |
| F8 | 已有契约测试对旧数值**零覆盖**，只断言键存在与项数 | `tests/test_extended_modules_contract.py:182-197` |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 关系名与官方枚举对齐，且非法名不再静默失败 (Priority: P1)

工程师让 Agent 给草图加「相等」或「中点」关系时，传进来的名字必须落到官方真正存在的枚举上；官方根本没有的名字（`EQUAL` / `MIDPOINT`）必须被明确拒绝并给出正确写法，而不是被当成合法值发给 SolidWorks 后静默无效。

**Why this priority**: 这是 221 之后唯一致「加了等于没加、而且看不出来」的缺陷。派发路径已经安全了，但**派发的类型值本身是错的** —— 安全地发一个错误的值，等于把风险从「重复改」换成「静默错」。不修这条，后续所有关系类能力都建在错数字上。

**Independent Test**: 纯离线即可完整验证 —— 断言映射表每个键的数值等于三源一致的官方值；断言 `EQUAL` / `MIDPOINT` 不再被当作合法键，且其拒绝信息里指明官方对应名。

**Acceptance Scenarios**:

1. **Given** 官方 `swConstraintType_e` 三源一致的数值表，**When** 读取 `RELATION_TYPES`，**Then** 表中每个键的数值与官方逐项相等，且不存在官方枚举里没有的键。
2. **Given** 清单里写 `EQUAL`，**When** 解析该条关系，**Then** 返回明确的非法名结果并提示官方对应为 `SAMELENGTH`（而不是带上一个数字继续派发）。
3. **Given** 清单里写 `sgATMIDDLE` 或大小写变体 `atmiddle`，**When** 解析，**Then** 归一为官方 `ATMIDDLE` 且数值取官方 12。

---

### User Story 2 - 公开工具不再把错误清单写给用户，且不在无状态门的情况下改关系 (Priority: P1)

已挂出去的 `solidworks_add_sketch_relation` 是用户唯一能碰到的关系入口。它的参数说明必须只列官方合法名；它指向的入口在真正改关系之前必须具备与 221 同等的前置检查，不能因为走了字符串路径就绕开状态门。

**Why this priority**: 与 US1 同属 P1 —— 用户实际撞到的是这个工具。枚举修正后如果不改公开面，用户看到的仍是旧错名清单；而字符串入口无门，会造成与 221 已认定的「过定义时继续加」同类后果。

**Independent Test**: 离线断言 ToolSpec 的 `doc`/参数描述里不含 `sgEQUAL`/`sgMIDPOINT` 等非官方名；用假宿主断言字符串入口在非欠定义状态下**不调用** `SketchAddConstraints`。

**Acceptance Scenarios**:

1. **Given** 生成的工具清单，**When** 检索 `solidworks_add_sketch_relation` 的参数描述，**Then** 其中每个候选名都能在 `SketchAddConstraints` 官方 Remarks 清单里找到。
2. **Given** 草图处于非可加状态，**When** 调用字符串入口，**Then** 在任何修改发生前拒绝，并说明当前状态。
3. **Given** 草图可加且名字合法，**When** 调用字符串入口，**Then** 恰好一次修改调用，且保留原有返回语义。

---

### User Story 3 - 数值关系登记为冲突未决，而不是顺手改掉 (Priority: P2)

两份表里还有一批原注释就标了 `swConstraintType_XXX` 名字的项，但数值与官方不符（例如表里写 `tangent: 21`，官方 `TANGENT` 是 6）。其中一部分的正确对应关系**本切片无法从三源唯一确定**（涉及 3D / 角度 / 尺寸类变体）。这类项必须显式登记为冲突未决并禁止用于派发，**不允许**按名字相似猜一个新数字填上。

**Why this priority**: P2 —— 不阻塞 US1/US2 的闭环，但决定了「表还能不能当权威」。猜数字比留着错的更危险，因为它把不确定伪装成确定。

**Independent Test**: 断言所有未决项都在一份显式的待裁决清单里，且对这些键的派发路径被拒绝。

**Acceptance Scenarios**:

1. **Given** 一个数值未与官方对齐的现存键，**When** 读取该表，**Then** 它出现在待裁决登记中，且带有「为什么本切片不能裁决」的说明。
2. **Given** 待裁决清单里的名字，**When** 用于派发，**Then** 在修改前拒绝并指向该登记。

---

### Edge Cases

- 传入 `"sg"` 或空串：必须判非法，不得归一成某个默认关系。
- 同一关系名大小写混合（`Parallel`、`SGparallel`）：必须归一，不得因大小写被判非法。
- 官方枚举中存在但**当前表完全没收录**的项（如 `COLLINEAR=27`、`CORADIAL=28`）：本切片只要求「不臆造数值」，不要求补全 —— 未收录即明确未支持。
- 新增键与既有键数值撞车：必须能被静态检查发现（同名不同类型不允许共用一个数字）。
- 关系数回读不可用的路径：沿用 221 的 `uncertain` 语义，不得因为本切片而放松。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `RELATION_TYPES` 中每个键的数值 MUST 等于官方 `swConstraintType_e` 的对应值，取值来源限定为三处已比对一致的官方源。 *(来源：官方 API 文档 —— `C:\swapi\enums\swConstraintType_e.md`、CHM 解包 `swconst` 页、`_raw/enum_values_sldworks.txt`；许可：官方文档仅作参考，不复制文本)*
- **FR-002**: `RELATION_TYPES` MUST NOT 出现官方枚举里不存在的名字；`EQUAL` / `MIDPOINT` MUST 被移除或改为指向官方名的别名，且别名解析结果 MUST 是官方成员名。 *(来源：本项目既有模式 —— `scripts/sw_sketch_relations.py` 现有表；官方源仅作裁决依据)*
- **FR-003**: `sw_part._SG_RELATIONS` MUST 与 `SketchAddConstraints` 官方 Remarks 清单一致；含非官方名的项 MUST 移除，并保留用户可读的等价说法。 *(来源：官方 API 文档 —— `C:\swapi\types\IModelDoc2\SketchAddConstraints.md`)*
- **FR-004**: `mcp-server/tool_specs_batch16.py` 中 `solidworks_add_sketch_relation` 的参数描述 MUST 只列官方合法名，且 MUST 说明大小写与 `sg` 前缀的归一规则。 *(来源：本项目自身 —— 既有 ToolSpec 声明文件)*
- **FR-005**: `sw_part.add_sketch_relation` MUST 在调用 `SketchAddConstraints` 之前执行与 221 同等的前置检查（活动草图、欠定义状态）；不满足时 MUST 在修改前拒绝。 *(来源：本项目既有模式 —— `specs/221-sketch-relation-dispatch-safety` 的状态门；许可：MIT)*
- **FR-006**: 字符串入口 MUST 对每条关系至多一次修改派发，异常或后态不可读时 MUST 沿用 `uncertain` 语义且不重放。 *(来源：本项目既有模式 —— 221 已实现并离线验收的语义)*
- **FR-007**: `SKETCH_CONSTRAINT_TYPES` 的每一项 MUST 被归入三类之一：①已与官方对齐、②官方别名、③显式登记为冲突未决；MUST NOT 存在第四类「数值不明但照常使用」。 *(来源：官方枚举 + 本项目既有注释里的自称名)*
- **FR-008**: 冲突未决项 MUST 在派发路径上被拒绝，并指向登记位置；MUST NOT 用推测数值替换。 *(来源：AGENTS.md 铁律 4「冲突以出厂类型库为准」+ 铁律 5「查不到就说查不到」)*
- **FR-009**: 既有公开返回字段（`ok` / `applied` / `total` / `results` 等）MUST 保持不变；新增状态字段 MUST 是增量。 *(来源：本项目既有契约 —— 221 已钉住的兼容面)*
- **FR-010**: 221 的 12 例离线回归 MUST 继续全绿；本切片 MUST 为上述每条 FR 补可跑的离线负例。 *(来源：Spec Kit 宪法 §V「验收判据必须能跑」)*

## Key Entities *(include if feature involves data)*

- **关系名映射表**：从用户可写的名字到官方 `swConstraintType_e` 数值的归一表；键为规范名，值为官方整数。
- **别名登记**：用户习惯写法（含 `sg` 前缀、大小写变体、历史错名）到规范名的解析规则，且必须能表达「历史错名 → 官方正确名」的纠正关系。
- **冲突未决登记**：数值无法从三源唯一确定的项 + 不能裁决的原因 + 被拒绝的派发路径。
- **公开工具声明**：`ToolSpec` 中面向用户的参数描述，是「用户看到什么合法值」的唯一来源。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 映射表中每个键的数值与官方三源一致，逐项比对为 0 处差异（含负例：故意写错一个数字时静态检查必须报错）。
- **SC-002**: 表中不再存在官方枚举里没有的名字；`EQUAL` / `MIDPOINT` 的派发路径被拒绝，拒绝信息里包含官方对应名。
- **SC-003**: 公开工具的参数描述中，非官方名出现次数为 0。
- **SC-004**: 非欠定义状态下调用字符串入口，修改调用次数为 0。
- **SC-005**: 221 的 12 例 + 本切片新增用例全部通过，且新增用例在修改前**至少失败 1 次**（证明用例真能抓到缺陷）。
- **SC-006**: 本切片全程不调用 COM、不安装依赖、不提交、不部署；运行时与产品级结论仍为未验收。

## Assumptions

- 官方 `swConstraintType_e` 的 86 项数值在本工作树的三处离线源中一致，因此可作为本切片的裁决依据；真机复核另属授权范围外。
- 本切片沿用 221 的写入门槛（主代理自行实现，机械核对才委派 DeepSeek V4.1 Flash），不因切片变化而放宽。
- `SKETCH_CONSTRAINT_TYPES` / `RELATION_TYPES` **确实有生产消费者**（2026-10-08 由独立核对确认，原假设「没有」**已被推翻**）：
  - `scripts/sw_sketch_relations.py` 内 `add_relation(payload, RELATION_TYPES[kind])` —— 把表内数值**直接当 COM 实参**送给 `ISketchRelationManager::AddRelation`。⇒ ★ 这正是「安全地派发错误数值」的落点：221 保证只派发一次，但派发的数字本身是错的。
  - `scripts/sw_part.py::add_sketch_relation` 走字符串入口 `SketchAddConstraints`，其白名单 `_SG_RELATIONS` 与前者同源同错。
  - `tests/test_extended_modules_contract.py` 曾把 `coincident` 的数值**硬编码成 1**（官方 9），已改为引用模块自身常量。
  ⇒ 因此本次修正**是**行为变更（从错值改为对值），不是纯收敛；已按此重估并逐项留判据。
- 修正前无任何判据钉住这些数值（既有测试只断言键存在与项数），故缺陷可长期存活 —— 本切片新增的逐项断言即为补上这一层。
- 本切片不承诺「关系几何正确」——计数增加仍只是计数证据，关系类型 / 实体对应 / 自由度 / 持久性仍为未验收。
