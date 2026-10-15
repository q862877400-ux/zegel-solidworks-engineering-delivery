# Data Model — 305-ec03-method-library-and-ir

**Feature**: `specs/305-ec03-method-library-and-ir/`

**来源**: ★ **从 `scripts/engineering/compiler.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `RejectCode`（★ class）

★★ 编译期拒绝码（★ 逐字承计划 §5 EC03 验收）。

### `PlanError`（★ class）

★ 编译期失败（★ 带**封闭码** —— ★ 与 EC00/EC01/EC02 同族）。

### `Complexity`（★ class）

★ 方法复杂度（★ 用于**多方案排序** —— ★ 不是唯一指标）。

### `MethodSpec`（★ dataclass）

★★ `MethodSpec`（★ 逐字承计划 §5 EC03-T01）：

| ★ 字段 | ★ 类型 |
|---|---|
| `id` | `str` |
| `goal` | `str` |
| `applicable_devices` | `tuple` |
| `preconditions` | `tuple` |
| `postconditions` | `tuple` |
| `steps` | `tuple` |
| `forbidden` | `tuple` |
| `complexity` | `str` |
| `modification_domain` | `tuple` |
| `verification_obligations` | `tuple` |
| `failure_domain` | `tuple` |
| `rationale` | `str` |
| `alternatives` | `tuple` |

### `SketchIR`（★ dataclass）

★ 草图 IR（★ 设计语义引用 —— ★ **不写裸坐标**）。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `plane_datum` | `str` |
| `entities` | `tuple` |
| `version` | `str` |

### `FeatureIR`（★ dataclass）

★ 特征 IR。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `kind` | `str` |
| `source_sketch` | `str` |
| `params` | `dict` |
| `depends_on` | `tuple` |
| `version` | `str` |

### `AssemblyIR`（★ dataclass）

★ 装配 IR。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `components` | `tuple` |
| `mates` | `tuple` |
| `degrees_of_freedom` | `int` |
| `version` | `str` |

### `DrawingIR`（★ dataclass）

★ 工程图 IR。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `views` | `tuple` |
| `dimensions` | `tuple` |
| `version` | `str` |

### `DAGNode`（★ dataclass）

★ DAG 节点（★ 带**前后置**与**验证步骤** —— ★ EC03-T06 逐字）。

| ★ 字段 | ★ 类型 |
|---|---|
| `tool` | `str` |
| `preconditions` | `tuple` |
| `postconditions` | `tuple` |
| `verification` | `tuple` |
| `depends_on` | `tuple` |

### `ToolDAG`（★ dataclass）

★ 工具 DAG。

| ★ 字段 | ★ 类型 |
|---|---|
| `nodes` | `list` |

### `CompiledPlan`（★ dataclass）

★★ **编译产物**（★ 冻结带内容哈希 —— ★ V6 的核心）。

| ★ 字段 | ★ 类型 |
|---|---|
| `contract_hash` | `str` |
| `method_id` | `str` |
| `dag` | `ToolDAG` |
| `irs` | `list` |
| `frozen` | `bool` |
| `plan_hash` | `str` |
| `warnings` | `list` |

### `EleganceScore`（★ dataclass）

★★ **优雅的多指标**（★ 逐字承 EC03-T07）：

| ★ 字段 | ★ 类型 |
|---|---|
| `modification_stability` | `float` |
| `datum_expression` | `float` |
| `intent_readability` | `float` |
| `tool_risk` | `float` |
| `manufacturability` | `float` |

### `SolveStatus`（★ class）

★★ 求解状态（★ **`unknown` 不是「可行」** —— ★ FR-005 逐字）。

