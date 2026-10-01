# Feature Specification: 拓扑族第二批（脱模 / 应力约束 / 对称）

**Feature Branch**: `124-topology-batch2` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A1（`docs/backlog-8h.md`）—— 继续把孤立能力挂成 MCP 工具。

## 来源（宪法 §I：每条需求带来源；§IV：带 license）

| 需求 | 来源 | license |
|---|---|---|
| 暴露 `create_demold_control` / `create_stress_constraint` / `create_symmetry_control` | **本项目自身既有模式**（包装 `scripts/sw_topology.py`，**不是第三方移植**）| 本仓库 **MIT** |
| 三个枚举的**取值** | **出厂反射转储** `D:/AI/SW/_raw/reflect/enum_cosworks.txt`（官方类型库）| 不适用（官方元数据）|
| 对称类型的取值语义 | **官方 VBA 示例** `Create_Topology_Study_Example_VBA.txt` | 不适用（官方示例）|
| 工具声明形状 | 既有 `mcp-server/tool_specs_batch1.py`（`solidworks_topology_*` 三工具）| 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能一句话加"制造约束"（Priority: P1）

用户要对一个拓扑研究加**脱模方向**约束（铸造件必须能拔模），
现在只能写脚本调 `sw_topology.create_demold_control`；希望能在 MCP 里直接点。

**Why this priority**: 拓扑那族里"约束/控制"是**唯一没挂出去**的一环，缺了它拓扑工具链是断的。

**Independent Test**: 单独注册后，`all_specs()` 里出现这三个名字，且规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 45 变 **48**（本批 3 个）
2. **Given** 一个已存在的拓扑研究，**When** 用 `solidworks_topology_create_demold_control`，
   **Then** 工具把 `direction` 透传给 `create_demold_control(study, *, direction)`，**参数名与真名一致**
3. **Given** 本批的 3 个工具，**When** 跑规则 1/2/3 门禁，**Then** 全过（无裸坐标、名带 `solidworks_` 前缀）

### User Story 2 - 枚举取值有据可查（Priority: P2）

用户看到 `direction` / `comparator` 时要知道**能填什么**，而不是去翻转储。

**Independent Test**: 每个带枚举的参数，其 `description` 里**列出取值与含义**。

**Acceptance Scenarios**:
1. **Given** `direction` 参数，**When** 读它的描述，**Then** 看到 `0=TwoDirectionMidPlane / 1=PullDirectionOnly / 2=Stamping`
2. **Given** `comparator` 参数，**When** 读它的描述，**Then** 看到 `0=IsLessThan / 1=IsGreaterThan / 2=IsInBetween`
3. **Given** `symmetry_type` 参数，**When** 读它的描述，**Then** 看到"取值来自**官方 VBA 示例**（0/1/2）"——
   ★ **并注明枚举名在本地转储里未找到**（宪法 §III：查不到就写查不到）

### User Story 3 - 顺带把上批的一个参数说明补全（Priority: P3）

`create_preserved_region` 上批已挂，但 `option` 只写"官方枚举值"—— 现在知道取值了。

**Independent Test**: 读它的 `description`，能看到 `0=LoadsOnly / 1=FixturesOnly / 2=LoadsAndFixtures / 3=None`。

## 明确不做（附理由）
| 不做 | 理由 |
|---|---|
| 给 `symmetry_type` 编一个枚举名 | ★ 本地转储里**查不到**那个枚举名 ⇒ 按铁律 5 **写"查不到"**，不发明 |
| 真机验证这三个工具 | ★ **暴露 ≠ 验证**（宪法接口表）；真机验证排 B 组（`135`）|
