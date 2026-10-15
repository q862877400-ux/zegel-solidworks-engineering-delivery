# Data Model — 313-ec11-compliance-and-release

**Feature**: `specs/313-ec11-compliance-and-release/`

**来源**: ★ **从 `scripts/engineering/compliance.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `ObligationKind`（★ class）

★★ **义务种类**（★ 逐字承 EC11-T03 + 承 EC02 的五类 —— ★ **复用口径**）。

### `ComplianceStatus`（★ class）

★★★ **五态**（★ 逐字承 EC11-T03：★「★ 规定 **pass/fail/unknown/not_applicable/expired**

### `ReleaseKind`（★ class）

★★★ **四类批准**（★ 逐字承 EC11-T06：★「★ 区分**软件包发布、CAD 工件完成、

### `ClauseRef`（★ dataclass）

★★★★ **条款引用**（★ **必须来自 KS 引擎** —— ★ 带 `doc_id`/`page`/`evidence_url`）。

| ★ 字段 | ★ 类型 |
|---|---|
| `standard_no` | `str` |
| `clause_number` | `str` |
| `legal_status` | `str` |
| `doc_id` | `str` |
| `page_start` | `int` |
| `clause_revision_id` | `str` |
| `evidence_url` | `str` |

### `Obligation`（★ dataclass）

★★★★ **一条义务**（★ 逐字承 EC11-T02）：

| ★ 字段 | ★ 类型 |
|---|---|
| `id` | `str` |
| `requirement` | `str` |
| `clause` | `ClauseRef` |
| `kind` | `str` |
| `verification_kind` | `str` |
| `evidence_refs` | `list` |
| `status` | `str` |
| `reason` | `str` |
| `load_case` | `str` |

### `ComplianceMatrix`（★ dataclass）

★★★★ **合规矩阵**（★ 逐字承 EC11-T02/T04）。

| ★ 字段 | ★ 类型 |
|---|---|
| `obligations` | `list` |
| `frozen_load_case` | `str` |

### `ReleaseRecord`（★ dataclass）

★★★★ **发布记录**（★ 逐字承 EC11-T06：★「★ 区分软件包发布、CAD 工件完成、

| ★ 字段 | ★ 类型 |
|---|---|
| `software_release` | `bool` |
| `cad_artifact_done` | `bool` |
| `design_signoff` | `bool` |
| `machine_conformity` | `bool` |
| `approvers` | `dict` |

