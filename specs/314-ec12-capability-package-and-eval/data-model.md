# Data Model — 314-ec12-capability-package-and-eval

**Feature**: `specs/314-ec12-capability-package-and-eval/`

**来源**: ★ **从 `scripts/engineering/evaluation.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `SplitKind`（★ class）

★★ **数据划分**（★ 逐字承 EC12-T01：★「★ 案例分**训练/开发/留出**，

### `ArmKind`（★ class）

★★★ **三组对照**（★ 逐字承 EC12-T02：★「★ 建立**原模型+工具、模型+提示词、

### `EvalCase`（★ dataclass）

★ 一个评测案例（★ 带**族/域/故障** —— ★ 用于**避免近似复制污染**）。

| ★ 字段 | ★ 类型 |
|---|---|
| `id` | `str` |
| `family` | `str` |
| `domain` | `str` |
| `fault` | `str` |
| `split` | `str` |
| `content` | `str` |

### `EvalSet`（★ dataclass）

★★★★ **评测集**（★ 逐字承 EC12-T01/T05）。

| ★ 字段 | ★ 类型 |
|---|---|
| `cases` | `list` |
| `frozen` | `dict` |

### `ArmResult`（★ dataclass）

★ 一组对照的读数（★ 逐字承 EC12-T04：★「★ 记录**成本/耗时/人工介入/重试/拒绝/成功**，

| ★ 字段 | ★ 类型 |
|---|---|
| `arm` | `str` |
| `passed` | `int` |
| `failed` | `int` |
| `rejected` | `int` |
| `retries` | `int` |
| `cost` | `float` |
| `elapsed_s` | `float` |
| `human_interventions` | `int` |
| `false_releases` | `int` |

### `AttributionReport`（★ dataclass）

★★★★★ **增益归因**（★ 逐字承验收：★「★ **系统增益不是增加无限重试得到**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `arms` | `dict` |
| `retry_tolerance` | `float` |

### `MethodAdmission`（★ class）

★★★★ **单方法准入七项**（★ 逐字承 EC12-T06）：

### `DomainGates`（★ dataclass）

★★★★ **各领域分别过门**（★ 逐字承验收：★「★ **各领域发布分别过门**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `domains` | `dict` |

### `AdmissionGate`（★ dataclass）

★★★★ **准入闸**（★ 逐字承 EC12-T08：★「★ **未见任务进入沙箱**；

| ★ 字段 | ★ 类型 |
|---|---|
| `sandbox_passed` | `bool` |
| `independent_reviewer` | `str` |
| `proposer` | `str` |
| `source` | `str` |

