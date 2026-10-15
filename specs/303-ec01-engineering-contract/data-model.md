# Data Model — 303-ec01-engineering-contract

**Feature**: `specs/303-ec01-engineering-contract/`

**来源**: ★ **从 `scripts/engineering_contract.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `InformationClass`（★ class）

★ 四类信息（★ 计划 §5 EC01-T01 逐字：「划分已知、假设、待确认、必需缺失四类信息」）。

### `ContractState`（★ class）

★ 契约状态机（★ 计划 §5 EC01-T04 逐字：`draft→needs_clarification→frozen→superseded`）。

### `Resolution`（★ class）

★ 引用解析结果（★ **复用 EC00 的封闭词表** —— ★ `specs/302-*/data-model.md` §4.2）。

### `Rejection`（★ class）

★ 拒绝（★ 带**封闭词表**的码 —— ★ 与 EC00 同族）。

### `Quantity`（★ class）

★ 用户提交的原始量值（★ **复用 EC00 的字段语义**）。

| ★ 字段 | ★ 类型 |
|---|---|
| `value` | `float` |
| `unit` | `str` |
| `quantity_kind` | `str` |
| `source` | `str` |

### `NormalizedQuantity`（★ class）

★ 规范化结果（★ **独立结构** ⇒ ★ 防重复换算 —— ★ 承 EC00）。

| ★ 字段 | ★ 类型 |
|---|---|
| `value` | `float` |
| `canonical_unit` | `str` |
| `original` | `Quantity` |
| `rule_version` | `str` |

### `Datum`（★ dataclass）

★ 工程基准。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `semantic_role` | `str` |
| `cad_plane_hint` | `str | None` |

### `LoadCase`（★ dataclass）

★ 工况（★ **缺它不能给强度结论** —— ★ 承计划 §5 EC05-T01）。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `kind` | `str` |
| `magnitude` | `NormalizedQuantity | None` |
| `is_missing` | `bool` |

### `MaterialRef`（★ dataclass）

★ 材料引用（★ **带版本** —— ★ FR-006）。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `standard` | `str` |
| `version` | `str` |
| `properties` | `dict` |

### `ProcessIntent`（★ dataclass）

★ 工艺意图（★ 如 `machined` / `sheet_metal` / `welded` / `3d_printed`）。

| ★ 字段 | ★ 类型 |
|---|---|
| `kind` | `str` |
| `notes` | `str` |

### `ParameterDomain`（★ dataclass）

★ 参数域（★ **逐字段** —— ★ 不搞全局域）。

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `low` | `float` |
| `high` | `float` |
| `unit` | `str` |
| `allow_negative` | `bool` |

### `VerificationObligation`（★ dataclass）

★ 验证义务（★ **Agent 不能删掉硬义务** —— ★ 承 EC00 `data-model.md` §三）。

| ★ 字段 | ★ 类型 |
|---|---|
| `id` | `str` |
| `description` | `str` |
| `mandatory` | `bool` |
| `evidence_kind` | `str` |

### `Assumption`（★ dataclass）

★ 假设（★ **必须给依据** —— ★ S1-3）。

| ★ 字段 | ★ 类型 |
|---|---|
| `field_name` | `str` |
| `value` | `Any` |
| `basis` | `str` |
| `conservative` | `bool` |

### `ApprovalRef`（★ dataclass）

★ 批准引用（★ **绑定内容哈希** ⇒ ★ 内容变了就失效 —— ★ FR-004）。

| ★ 字段 | ★ 类型 |
|---|---|
| `approver` | `str` |
| `content_hash` | `str` |
| `note` | `str` |

### `EngineeringContract`（★ dataclass）

★★★ **EC01 的单一权威工程契约**（★ 计划 §5 EC01 逐字要求）。

| ★ 字段 | ★ 类型 |
|---|---|
| `contract_id` | `str` |
| `intent` | `str` |
| `state` | `str` |
| `information` | `dict` |
| `datums` | `list` |
| `load_cases` | `list` |
| `material` | `MaterialRef | None` |
| `process` | `ProcessIntent | None` |
| `parameter_domains` | `dict` |
| `obligations` | `list` |
| `assumptions` | `list` |
| `approvals` | `list` |
| `clarifications` | `list` |
| `safety_level` | `str | None` |
| `content_hash` | `str` |

