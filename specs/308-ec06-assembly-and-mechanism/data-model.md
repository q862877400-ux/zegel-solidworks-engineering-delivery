# Data Model — 308-ec06-assembly-and-mechanism

**Feature**: `specs/308-ec06-assembly-and-mechanism/`

**来源**: ★ **从 `scripts/engineering/assembly.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `DofVerdict`（★ class）

★★ 约束状态（★ 逐字承 EC06-T02：★「★ 区分**欠约束、冗余、过约束和预期运动自由度**」）。

### `MateKind`（★ class）

★ 配合种类（★ 与工具面对齐 —— ★ 铁律 1：★ 不另建一套）。

### `Component`（★ dataclass）

★ 组件（★ 带**是否地件** —— ★ EC06-T01 逐字）。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `is_ground` | `bool` |
| `dof` | `int` |

### `Mate`（★ dataclass）

★ 配合（★ 带**轴向**信息 —— ★ 「错轴向位置必被检测」靠它）。

| ★ 字段 | ★ 类型 |
|---|---|
| `kind` | `str` |
| `a` | `str` |
| `b` | `str` |
| `axis` | `str` |
| `value` | `float | None` |
| `redundant` | `bool` |
| `conflicts_with` | `tuple` |

### `ConstraintGraph`（★ dataclass）

★★★★ **约束图**（★ EC06-T02 的核心）。

| ★ 字段 | ★ 类型 |
|---|---|
| `components` | `list` |
| `mates` | `list` |
| `target_dof` | `int | None` |
| `expected_motions` | `list` |

### `InterferenceScan`（★ dataclass）

★★★★ **位置扫描 + 自适应局部加密**（★ EC06-T04 逐字）。

| ★ 字段 | ★ 类型 |
|---|---|
| `positions_scanned` | `int` |
| `interferences` | `list` |
| `refined_intervals` | `list` |
| `is_full_domain_proof` | `bool` |
| `uncovered` | `list` |

### `ToleranceChain`（★ dataclass）

★★★ **基准与配合链 → 公差链**（★ EC06-T03 逐字：★「★ 基准与配合链映射到公差链；

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `links` | `list` |
| `method` | `str` |
| `statistical_basis` | `str` |

### `MaintenanceCheck`（★ dataclass）

★★ **维护可达性**（★ EC06-T05 逐字：★「★ 验证**紧固件可达、装拆次序、轴承安装、润滑、

| ★ 字段 | ★ 类型 |
|---|---|
| `items` | `list` |

