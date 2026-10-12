# Feature Specification: Q1 + Q5 · 声明式协议、决策追责与检查引用

**Feature Branch**: `325-declarative-protocols-and-decisions`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **Q1**（L10–34）·
**Q5**（L59–94）；业主指令「要」

---

## §0 这一份规格要解决什么

**Q1 的核心**（逐字）：

> LLM 输出都是 `Proposal`，**不能自行晋升为 `Validated` 或 `Approved`**。
> 代码只能裁决**已经形式化的性质**，不能声称证明任意自然语言的完整语义。
>
> 最小追责单位沿用任务／方法／节点／验证义务／执行尝试，另给每个方案决策一个
> `decision_id`，记录**输入版本、备选方案、可见理由、依据和受影响节点**。
> 无需记录模型隐藏思维链。

**Q5 的核心**（逐字）：

> `check_ref` **必须解析到已登记的代码**，禁止任意 Python、`eval` 或 LLM 生成脚本
> 进入生产执行。
> 改协议参数或流程：**改一处源数据，重新生成文档、提示与目录**。
> 增加真正的新判定逻辑：**增加实现与测试，再登记引用**，
> 不能假装只改 YAML 就能获得新能力。

**★★ 这两问是一件事的两面**：
★ Q1 说「**LLM 的产出不能自己变权威**」，★ Q5 说「**权威必须落在已登记的代码上**」。

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | ★★ **没有 `decision_id`** | ✅ **缺口** |
| 2 | ★★ **没有 `Proposal`/`Validated`/`Approved` 三态**（`server.py` 那个 `Approved` 是假阳性） | ✅ **缺口** |
| 3 | ★★ **没有四类协议** | ✅ **缺口** |
| 4 | ★★ **没有「同错误两次停下」诊断触发** | ✅ **缺口** |
| 5 | ★★ **没有「可见理由」与「受影响节点」** | ✅ **缺口** |
| 6 | ★★ **没有任何协议目录**（`metadata/protocols`/`protocols`/`schemas`/`contracts` 全不存在） | ✅ **缺口** |
| 7 | ★★ **没有 `check_ref` 解析器**（那两条命中是 `check_refuted_patterns` 的**子串**） | ✅ **缺口** |
| 8 | ★★ **没有禁止 `eval`/任意 Python 的判据** | ✅ **缺口** |
| 9 | ★★ **没有 8 项必设检查** | ✅ **缺口** |
| 10 | ✅ `WAITING_INPUT` **已有**（阶段 4 的 `design_ir`） | ✅ **可复用** |
| 11 | ✅ 可作 `check_ref` 后端的既有函数**充足**：`rule_verdicts.evaluate` · `design_ir.parse_requirement` · `registry.resolve_step_name` / `bind_params` · `recovery.resume_verdict` / `invalidation_closure` · `catalog.retrieve` / `load_contract` · `compiler.METHOD_LIBRARY` | ✅ |

**⇒ 本规格的工作量 = 补 9 个缺口 + 复用 `WAITING_INPUT` 与既有函数做 `check_ref` 后端。**

---

## §2 交付物

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **R1** | **四类协议** | `metadata/protocols/*.yaml` | **需求 / 方案门槛 / 布局 / 失败转移**四份齐 |
| **R2** | **协议五要素** | 同上 | 每份都有**输入 / 输出 / 触发条件 / 检查函数 / 失败状态** |
| **R3** | **`check_ref` 解析到已登记代码** | `scripts/engineering/protocols.py` | ★ **解析不到 ⇒ 拒**；★ **禁 `eval`/任意 Python** |
| **R4** | **8 项必设检查** | 同上 | ★ 八项**都要在**（schema/引用/单位类型/可达状态/禁止条件/输出兼容/版本依赖/受影响节点失效）+ 负例与突变测试 |
| **R5** | **改一处源数据 ⇒ 重生成三视图** | `protocols.py` 的 `regenerate()` | 文档 / 提示 / 目录**三样都从协议生成** |
| **R6** | **`decision_id` 五要素** | `scripts/engineering/decisions.py` | **输入版本 · 备选方案 · 可见理由 · 依据 · 受影响节点** |
| **R7** | **三态且 LLM 不能自升** | `decisions.py` 的 `promote()` | ★ **`Proposal` → `Approved` 必须经 `Validated`**，★ 且 `Validated` 要**代码裁决** |
| **R8** | **「缺需求先问」转字段门禁** | `protocols.py` | ★ 缺必填字段 ⇒ **`WAITING_INPUT`**，★ **不用"最坏工况"顶替** |
| **R9** | **「同错误两次停下」转诊断触发** | `decisions.py` 的 `SameErrorTrigger` | ★ 两次同错 ⇒ **触发诊断**，★ **不判根因** |
| **R10** | **改 YAML 不能获得新能力** | `protocols.py` | ★ 新增 `check_ref` 若**无实现** ⇒ **拒** |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 有**四类协议**（需求 / 方案门槛 / 布局 / 失败转移）
- **FR-002**: 每份协议 MUST 有**输入 / 输出 / 触发条件 / 检查函数 / 失败状态**
- **FR-003**: `check_ref` MUST **解析到已登记的代码**；解析不到 MUST 拒
- **FR-004**: 系统 MUST **禁止** `eval`/`exec`/任意 Python/LLM 生成脚本进生产执行
- **FR-005**: 系统 MUST 实施**8 项必设检查**
- **FR-006**: 改协议 MUST **只改一处源数据**，然后**重生成**文档/提示/目录
- **FR-007**: 每个方案决策 MUST 有 `decision_id` 与**五要素**
- **FR-008**: LLM 输出 MUST 是 `Proposal`，**不得自升**为 `Validated`/`Approved`
- **FR-009**: `Validated` MUST **由代码裁决**（★ 裁决的是**已形式化的性质**）
- **FR-010**: 缺必填字段 MUST ⇒ `WAITING_INPUT`，★ **不得用"最坏工况"顶替**
- **FR-011**: 同错误码**两次** MUST 触发**诊断**，★ **不得判根因**
- **FR-012**: **只改 YAML 不得获得新能力** —— 新 `check_ref` 无实现 ⇒ 拒
- **FR-013**: 系统 MUST **不记录**模型隐藏思维链

### Key Entities

- **Protocol**：`protocol_id` · `version` · `entry_check` · `inputs_schema` · `outputs_schema` · `required_inputs` · `checks` · `on_failure` · `source_refs`
- **CheckRef**：`name` · `module` · `function` · `resolved` · `reason`
- **Decision**：`decision_id` · `state` · `input_version` · `alternatives` · `visible_rationale` · `basis` · `affected_nodes` · `proposer`
- **DecisionState**：`Proposal` / `Validated` / `Approved`
- **SameErrorTrigger**：`error_code` · `count` · `triggered` · `★ 不判根因`

---

## §4 Success Criteria

- **SC-001**: 四类协议**都在**，且每份五要素齐
- **SC-002**: `check_ref` **全部解析成功**（★ 解析不到即失败）
- **SC-003**: **`eval`/`exec`/任意 Python 零命中**
- **SC-004**: **8 项必设检查全部实施**
- **SC-005**: 改一处 ⇒ **三视图都变**（文档/提示/目录）
- **SC-006**: 每个决策有 **`decision_id` + 五要素**
- **SC-007**: ★★ **`Proposal` 不能直达 `Approved`**
- **SC-008**: ★★ **LLM 自升被拒**（`proposer=llm` 时不能进 `Validated`）
- **SC-009**: 缺必填 ⇒ `WAITING_INPUT`，★ **无"最坏工况"顶替路径**
- **SC-010**: 两次同错 ⇒ 触发诊断，★ **返回体里没有"根因"字段**
- **SC-011**: ★ **新 `check_ref` 无实现 ⇒ 拒**

---

## §5 反向验证

| # | 突变 | 期望 |
|---|---|---|
| **X1** | **让 `Proposal` 直接晋升 `Approved`** | 必须**失败** |
| **X2** | **让 LLM 自评就能 `Validated`** | 必须**失败** |
| **X3** | **把 `check_ref` 指向不存在的函数** | 必须**拒** |
| **X4** | **在协议里塞一段 `eval` 代码** | 必须**检出** |
| **X5** | **只改 YAML 加一个新检查** | 必须**拒**（★ 无实现） |
| **X6** | **缺必填字段却继续** | 必须 `WAITING_INPUT` |
| **X7** | **两次同错却继续重试** | 必须**触发诊断** |
| **X8** | **把"最坏工况"当默认值填进去** | 必须**检出** |

---

## §6 明确不做

- **不一次转译整个知识库**（★ Q1 逐字：「不一次转译整个知识库」）
- **不记录隐藏思维链**（★ Q1 逐字：「无需记录模型隐藏思维链」）
- **不做 LLM 真调用**（★ 业主已拍板；★ 只做**三态与晋升闸门**）
- **不重写** `design_ir` / `rule_verdicts` / `registry`（★ 扩展，不推倒）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/325-declarative-protocols-and-decisions/spec.md` | 本文件 |
| 2 | `metadata/protocols/{requirement,scheme_gate,layout,failure_transition}.yaml` | **四类协议** |
| 3 | `scripts/engineering/protocols.py` | **R1~R5 · R8 · R10** |
| 4 | `scripts/engineering/decisions.py` | **R6/R7/R9** |
| 5 | `tests/test_s325_protocols.py` | R1~R10 契约 + X1~X8 |
| 6 | `tools/run_s325_protocols.py` | 验收入口 |
| 7 | `specs/325-declarative-protocols-and-decisions/acceptance.md` | 验收记录 |
