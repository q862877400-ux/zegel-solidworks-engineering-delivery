# Data Model — 311-ec09-cae-and-topology

**Feature**: `specs/311-ec09-cae-and-topology/`

**来源**: ★ **从 `scripts/engineering/cae.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `SolveStatus`（★ class）

★★ **求解器返回的状态**（★ **与工程结论分开** —— ★ 那是验收的核心）。

### `VerificationKind`（★ class）

★★ **三级证据**（★ 逐字承 EC09-T05：★「★ **分开计算 verification、物理 validation

### `ReferenceSolution`（★ dataclass）

★★★★ **参考解**（★ 逐字承验收：★「★ **参考解**……」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `value` | `float` |
| `unit` | `str` |
| `source` | `str` |
| `independent` | `bool` |

### `ReactionBalance`（★ dataclass）

★★★★ **反力平衡**（★ 逐字承验收：★「★ **反力平衡**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `applied_n` | `float` |
| `reactions_n` | `list` |
| `rel_tol` | `float` |

### `MeshConvergence`（★ dataclass）

★★★★ **网格收敛**（★ 逐字承 EC09-T04）：

| ★ 字段 | ★ 类型 |
|---|---|
| `levels` | `list` |
| `quantity` | `str` |
| `rel_tol` | `float` |

### `VersionClosure`（★ dataclass）

★★★★ **材料/载荷版本闭合**（★ 逐字承验收：★「★ **材料/载荷版本闭合**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `material_ref` | `str` |
| `material_used` | `str` |
| `load_ref` | `str` |
| `load_used` | `str` |
| `geometry_ref` | `str` |
| `geometry_used` | `str` |

### `AnalysisIR`（★ dataclass）

★★★ **AnalysisIR**（★ 逐字承 EC09-T02）：

| ★ 字段 | ★ 类型 |
|---|---|
| `geometry_simplification` | `str` |
| `material` | `str` |
| `constitutive` | `str` |
| `loads` | `list` |
| `boundaries` | `list` |
| `contacts` | `list` |
| `target_quantity` | `str` |
| `applicability` | `str` |

### `ValidationScope`（★ dataclass）

★★★★★ **验证范围**（★ 逐字承 EC09-T05）：

| ★ 字段 | ★ 类型 |
|---|---|
| `verification_done` | `bool` |
| `validation_evidence` | `list` |
| `uncertainty_notes` | `str` |

### `SensitivityScan`（★ dataclass）

★★★★ **设计敏感性**（★ 逐字承 EC09-T06）：

| ★ 字段 | ★ 类型 |
|---|---|
| `perturbations` | `dict` |
| `frozen_domains` | `list` |
| `manufacturing_constraints` | `list` |

