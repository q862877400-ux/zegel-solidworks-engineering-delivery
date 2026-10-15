# Data Model — 304-ec02-rules-and-standards

**Feature**: `specs/304-ec02-rules-and-standards/`

**来源**: ★ **从 `scripts/engineering/rules.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `Verdict`（★ class）

★★ 判定（★ **封闭词表** —— ★ 与 EC00/EC01 同族：★ `unknown` 不放行）。

### `Effectiveness`（★ class）

★ 标准效力（★ **与 KS 引擎的四色对齐** —— ★ `baseline.md` §二 实测）。

### `ObligationKind`（★ class）

★★ 义务种类（★ EC02-T03 逐字：★「**不用 GB/T 标签替代法律适用判断**」）。

### `UnknownReason`（★ class）

★★ **`unknown` 的原因**（★ 逐字承计划 §5 EC02 验收：「过期、缺源、域外、统计假设缺失」）。

### `StandardRef`（★ dataclass）

★★ 标准引用（★ **出处** —— ★ 本模块**不编**条款号，★ 由 KS 引擎给）。

| ★ 字段 | ★ 类型 |
|---|---|
| `standard_no` | `str` |
| `clause` | `str` |
| `effectiveness` | `str` |
| `verified_on` | `str` |
| `license_note` | `str` |
| `applicable_devices` | `tuple` |
| `evidence_kind` | `str` |
| `evidence_url` | `str` |
| `doc_id` | `str` |
| `clause_revision_id` | `str` |

### `Rule`（★ dataclass）

★ 规则（★ 逐字承 EC02-T01：「★ 输入单位、适用域、来源、版本、阈值、输出和 `unknown`」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `id` | `str` |
| `statement` | `str` |
| `obligation` | `str` |
| `unit` | `str` |
| `applicable_devices` | `tuple` |
| `source` | `StandardRef | None` |
| `threshold` | `float | None` |
| `counterexample` | `str` |
| `priority` | `int` |
| `statistical_basis` | `str` |

### `RuleDecision`（★ dataclass）

★ 判定结果（★ **必须带依据** —— ★ T06）。

| ★ 字段 | ★ 类型 |
|---|---|
| `rule_id` | `str` |
| `verdict` | `str` |
| `basis` | `str` |
| `unknown_reason` | `str` |
| `numbers` | `dict` |

### `RuleRegistry`（★ class）

★ 规则登记表（★ **出处可查** —— ★ V1）。

