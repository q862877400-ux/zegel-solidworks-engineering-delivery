# Data Model — 309-ec07-automation-slice

**Feature**: `specs/309-ec07-automation-slice/`

**来源**: ★ **从 `scripts/engineering/automation.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `SafetyLevel`（★ class）

★ 安全等级（★ EC07-T04 逐字：★「★ **风险/安全等级的确定需要适用方法与审核责任**」）。

### `InterlockKind`（★ class）

★★ **互锁种类**（★ EC07-T04 逐字：★「★ **分开普通互锁和安全功能**」）。

### `FaultKind`（★ class）

★★ **故障种类**（★ EC07-T05 逐字点名的七类 —— ★ 见 `FaultMatrix.DEFAULT_KINDS`）。

### `MotionIR`（★ dataclass）

★★★ **MotionIR**（★ 逐字承 EC07-T02）：

| ★ 字段 | ★ 类型 |
|---|---|
| `stroke_m` | `float` |
| `cycle_time_s` | `float` |
| `payload_kg` | `float` |
| `moving_mass_kg` | `float` |
| `efficiency` | `float` |
| `braking` | `str` |
| `thermal_limit_c` | `float` |
| `profile` | `str` |

### `AutomationIR`（★ dataclass）

★★★ **AutomationIR**（★ 逐字承 EC07-T03）：

| ★ 字段 | ★ 类型 |
|---|---|
| `io_points` | `list` |
| `sensors` | `list` |
| `interlocks` | `list` |
| `timeouts` | `dict` |
| `recovery` | `dict` |

### `SafetyFunctionIR`（★ dataclass）

★★★★★ **SafetyFunctionIR**（★ 逐字承 EC07-T04）：

| ★ 字段 | ★ 类型 |
|---|---|
| `functions` | `list` |
| `safety_level` | `str` |
| `assessment_method` | `str` |
| `accountable_person` | `str` |

### `StateMachine`（★ dataclass）

★★★★ **有限状态机**（★ 逐字承 EC07-T05）：

| ★ 字段 | ★ 类型 |
|---|---|
| `initial` | `str` |
| `transitions` | `dict` |
| `states` | `tuple` |

### `FaultMatrix`（★ dataclass）

★★★★ **故障矩阵**（★ 逐字承验收：★「★ 至少一个正常循环和**具名故障矩阵**可重复验证」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `rows` | `list` |

### `SelectionResult`（★ dataclass）

★ 选型结果（★ **带依据** —— ★ 不是「就它了」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `kind` | `str` |
| `model` | `str` |
| `margin` | `float` |
| `basis` | `str` |
| `mark` | `str` |

### `CrossCheckKind`（★ class）

★★ **交叉检查的项**（★ 逐字承 EC07-T06）：★「★ 机械**行程止挡**、**制动/保持**、

### `CrossCheck`（★ dataclass）

★★★★ **交叉检查**（★ EC07-T06 逐字）。

| ★ 字段 | ★ 类型 |
|---|---|
| `items` | `dict` |

