# Data Model — 312-ec10-install-and-nodes

**Feature**: `specs/312-ec10-install-and-nodes/`

**来源**: ★ **从 `scripts/engineering/nodes.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `DiagnosisResult`（★ dataclass）

★★★ **诊断结果**（★ 逐字承 EC10-T03：★「★ 诊断 **Python/COM/MCP、SW 版本/许可/插件、

| ★ 字段 | ★ 类型 |
|---|---|
| `checks` | `list` |

### `CapabilityPackage`（★ dataclass）

★★★★ **能力包**（★ 逐字承 EC10-T01）：

| ★ 字段 | ★ 类型 |
|---|---|
| `name` | `str` |
| `version` | `str` |
| `version_manifest` | `dict` |
| `compatibility` | `list` |
| `contents` | `list` |
| `files` | `dict` |

### `SessionLeaseRegistry`（★ dataclass）

★★★★★ **单会话注册表**（★ 逐字承验收：★「★ **DSH 和 WorkBuddy 不能同时控制同一会话**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `holder` | `str` |
| `session_id` | `str` |

### `AccessPolicy`（★ dataclass）

★★★★ **访问控制**（★ 逐字承验收：★「★ **未授权用户不能读另一项目产物**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `grants` | `dict` |
| `retention_days` | `int` |
| `log_redaction` | `bool` |
| `download_authorization` | `bool` |
| `external_send_confirmation` | `bool` |

### `UpgradePlan`（★ dataclass）

★★★★★ **升级与回滚**（★ 逐字承验收：★「★ **升级失败可回到已知良好版本**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `from_version` | `str` |
| `to_version` | `str` |
| `known_good_version` | `str` |
| `steps` | `list` |

