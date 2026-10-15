# Data Model — 306-ec04-safe-jobs-and-evidence

**Feature**: `specs/306-ec04-safe-jobs-and-evidence/`

**来源**: ★ **从 `scripts/engineering/jobs.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `JobState`（★ class）

★★ Job 状态（★ 逐字承 EC04-T01）：

### `JobError`（★ class）

★ 作业错误（★ 带**封闭码** —— ★ 与 EC00/EC01/EC02/EC03 同族）。

### `FenceToken`（★ dataclass）

★★★ **围栏令牌**（★ EC04-T02 逐字：★「★ 单 SW 会话互斥、租约续期、围栏令牌；

| ★ 字段 | ★ 类型 |
|---|---|
| `value` | `int` |

### `Lease`（★ dataclass）

★★ 租约（★ 带**过期时刻** —— ★ 续期可延长）。

| ★ 字段 | ★ 类型 |
|---|---|
| `holder` | `str` |
| `token` | `int` |
| `expires_at` | `float` |
| `ttl_seconds` | `float` |

### `NodeLease`（★ dataclass）

★★★ **节点级租约**（★ 单 SW 会话互斥 —— ★ **EC04 的交付**，★ 承 EC00 的边界声明）。

| ★ 字段 | ★ 类型 |
|---|---|
| `session_id` | `str` |
| `fence` | `FenceToken` |
| `current` | `Lease | None` |
| `_acquisitions` | `int` |

### `VersionBinding`（★ dataclass）

★★★ **批准绑三个版本**（★ EC04-T03 逐字：★「★ 比较并交换模型版本；

| ★ 字段 | ★ 类型 |
|---|---|
| `contract_hash` | `str` |
| `plan_hash` | `str` |
| `model_revision` | `str` |

### `ArtifactRecord`（★ dataclass）

★ 工件记录（★ EC04-T07 逐字：★「★ `Artifact`/`EvidenceManifest` **哈希、相对路径**、

| ★ 字段 | ★ 类型 |
|---|---|
| `relative_path` | `str` |
| `sha256` | `str` |
| `bytes_size` | `int` |
| `retention_days` | `int` |

### `EvidenceChain`（★ dataclass）

★★ **证据链**（★ 逐条**绑定版本** —— ★ 「旧证据不能放行新模型」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `records` | `list` |

### `IndependentVerifier`（★ dataclass）

★★★ **独立验收器**（★ EC04-T06 逐字：★「★ **独立验收器只读最终模型**；

| ★ 字段 | ★ 类型 |
|---|---|
| `executor_id` | `str` |
| `verifier_id` | `str` |
| `read_only` | `bool` |

### `RecoveryPlan`（★ dataclass）

★★★ **阶段检查点与前向补偿**（★ EC04-T05 逐字：★「★ 阶段检查点与前向补偿；

| ★ 字段 | ★ 类型 |
|---|---|
| `checkpoints` | `list` |

### `InjectionKind`（★ class）

★★ 可**离线**注入的故障（★ EC04-T08 逐字点名的四类里，★ **前三类不需要 COM**）。

