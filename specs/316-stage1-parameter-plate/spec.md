# Feature Specification: 阶段 1 · 经方法入口安全建成参数板

**Feature Branch**: `316-stage1-parameter-plate`

**Created**: 2026-10-11

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` 的**阶段 1**
+ 业主指令「阶段一开工开始做吧，按照 spec 的规范，设置好目标，全自动进行」

---

## §0 这一份规格要解决什么

**外部方案的阶段 1 目标**（逐字）：

> **目标**：人工提供方法参数，生产入口经过编译器和既有执行器，真实建板、保存、重开。
> **新增契约**：统一目录、最小方法与计划契约、名字解析、参数绑定、公共授权、执行意图记录。

**本规格把上面六件「新增契约」变成可验收的东西。**

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `scripts/engineering/` 有 **12 个模块**（EC 系列） | ✅ |
| 2 | `compiler.py` 有 `METHOD_LIBRARY` = **4 个方法** | ✅ |
| 3 | `DAGNode.tool` 存的是**裸步名**（`tool=step`） | ✅ **实测源码逐字** |
| 4 | **名字解析层不存在** —— 全仓 grep 不到「裸步名 → `solidworks_*`」的拼装 | ✅ **缺口** |
| 5 | `tools/tool_caller.py` **是执行器**（`call()` 能执行 `solidworks_*` 全名） | ✅ |
| 6 | **授权器不存在** —— 没有 `TOOL_NOT_ADMITTED` / `PATH_OUTSIDE_WORKSPACE` / `DOCUMENT_NOT_OWNED` | ✅ **缺口** |
| 7 | 参数绑定：`DAGNode` 只有 `tool`，**没有参数** | ✅ **缺口** |

**⇒ 阶段 1 的真实工作量 = 补 4 个缺口（#4 #6 #7 + 目录合成）。**

---

## §2 六件新增契约（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **C1** | **统一目录** | `scripts/engineering/registry.py` | 每个工具合成一个 `ToolDescriptor`；缺元数据的工具**不得进入执行集** |
| **C2** | **最小方法与计划契约** | 复用 `compiler.py` + 新 `PlanStep` | 计划里的每步都有 `tool` + `params` + `derive` |
| **C3** | **名字解析** | `registry.resolve_step_name()` | 裸步名 → 唯一规范工具名；**解析不到 ⇒ 拒绝**（不静默） |
| **C4** | **参数绑定** | `registry.bind_params()` | 声明的参数名 → 函数形参；单位**恰好换算一次** |
| **C5** | **公共授权** | `scripts/engineering/authorization.py` | 未准入 / 圈外路径 / 非自有文档 ⇒ **拒绝且 COM 写调用数 = 0** |
| **C6** | **执行意图记录** | `scripts/engineering/executor.py` | 每次写 COM **之前**先落盘意图；返回后落结果 |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 把裸步名（如 `sketch_start`）解析成**唯一**规范工具名（如 `solidworks_sketch_start`）
- **FR-002**: 解析不到时 MUST 抛 `RejectCode.UNRESOLVED_STEP_NAME`，**不得**静默跳过或猜
- **FR-003**: 一个裸步名若映射到**多个**规范名（歧义），MUST 拒绝
- **FR-004**: 系统 MUST 给每个工具合成 `ToolDescriptor`（含 `canonical_name` / `step_name` / `module` / `function` / `effect` / `admitted`）
- **FR-005**: 只有 `admitted=True` 的工具**才能**进入执行集
- **FR-006**: 系统 MUST 在执行前检查**路径**：任何写盘路径必须落在 `D:\AI\SW` 内，否则 `PATH_OUTSIDE_WORKSPACE`
- **FR-007**: 系统 MUST 在执行前检查**文档身份**：只操作**本任务创建**的文档，否则 `DOCUMENT_NOT_OWNED`
- **FR-008**: 拒绝发生时，**COM 写调用数 MUST = 0**（可被调用计数器证明）
- **FR-009**: 每个 `PlanStep` MUST 带 `params`（参数字典）与 `derive`（参数的推导说明）
- **FR-010**: 参数进 COM 前 MUST **恰好换算一次**（复用 `scripts/check_unit_conversion_count.py` 的口径）
- **FR-011**: 执行器 MUST 在每次写 COM **之前**记录意图（`intent`），返回后记录结果
- **FR-012**: 执行器 MUST NOT 绕过方法层直接调内部函数（即只走 `solidworks_*` 全名）
- **FR-013**: 不适用（`device_class` 不匹配）MUST 返回 `NOT_APPLICABLE`
- **FR-014**: 生产入口 MUST 可被**独立启动**执行（不依赖前一次的进程状态）

### Key Entities

- **ToolDescriptor**：`canonical_name` · `step_name` · `module` · `function` · `inject` · `params` · `effect` · `admitted` · `reject_reason`
- **PlanStep**：`step`（裸步名）· `params`（dict）· `derive`（str）· `tool`（解析后的全名）
- **ExecutablePlan**：`method_id` · `steps`（PlanStep 列表）· `device_class`
- **AuthorizationVerdict**：`ok` · `code`（`TOOL_NOT_ADMITTED` / `PATH_OUTSIDE_WORKSPACE` / `DOCUMENT_NOT_OWNED`）· `detail`
- **ExecutionRecord**：`step` · `tool` · `params` · `intent_at` · `result` · `com_write_count`

---

## §4 Success Criteria

### Measurable Outcomes

- **SC-001**: **3 个不同参数用例**独立启动，经生产入口真机建成正确的参数板
- **SC-002**: 尺寸与体积符合**冻结判据**（相对误差 ≤1e-6）
- **SC-003**: **所有执行节点解析为唯一规范工具**（0 个未解析）
- **SC-004**: **无绕过方法层的内部函数捷径**（执行轨迹里全是 `solidworks_*`）
- **SC-005**: 不适用返回 `NOT_APPLICABLE`
- **SC-006**: 未准入返回 `TOOL_NOT_ADMITTED`
- **SC-007**: 路径越权返回 `PATH_OUTSIDE_WORKSPACE`
- **SC-008**: 文档越权返回 `DOCUMENT_NOT_OWNED`
- **SC-009**: **上述负例的 COM 写调用数全部为 0**
- **SC-010**: 两种注册来源（`all_specs()` 476 + `server.py` 45）**均进入清单**，不漏

---

## §5 反向验证（★ 四条突变必须失败）

| # | 突变 | 期望 |
|---|---|---|
| **M1** | 把规范名改回**裸名** | 定点测试必须失败 |
| **M2** | 把深度绑定 **×1000** | 定点测试必须失败 |
| **M3** | **取消适用性检查** | 定点测试必须失败 |
| **M4** | 使授权器**恒允** | 定点测试必须失败 |

---

## §6 明确不做

- **不做**跨零件在位设计（那是方案 ① 的攻关，独立进行）
- **不做**云端 LLM 规划（阶段 4 的事）
- **不做**孔组 / 工程图（阶段 2 的事）
- **不重写** `tool_caller.py`（它是既有执行器；只在**必要处**扩展）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/316-stage1-parameter-plate/spec.md` | 本文件 |
| 2 | `specs/316-stage1-parameter-plate/data-model.md` | 数据结构定义 |
| 3 | `scripts/engineering/registry.py` | C1 目录 + C3 名字解析 + C4 参数绑定 |
| 4 | `scripts/engineering/authorization.py` | C5 公共授权 |
| 5 | `scripts/engineering/executor.py` | C6 执行意图记录 + 执行 |
| 6 | `scripts/engineering/compiler.py` | 扩展：`PlanStep` + `compile_method()` |
| 7 | `tests/test_stage1_registry.py` | C1/C3/C4 的契约测试 + 反向验证 M1/M2 |
| 8 | `tests/test_stage1_authorization.py` | C5 的契约测试 + 反向验证 M3/M4 |
| 9 | `tools/run_stage1_plate.py` | 生产入口（3 个参数用例，真机） |
| 10 | `specs/316-stage1-parameter-plate/acceptance.md` | 验收记录 |
