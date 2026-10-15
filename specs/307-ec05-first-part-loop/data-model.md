# Data Model — 307-ec05-first-part-loop

**Feature**: `specs/307-ec05-first-part-loop/`

**来源**: ★ **从 `scripts/engineering/part_loop.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `Disturbance`（★ dataclass）

★ 一组扰动（★ 带**类型** —— ★ 验收要求「**类型不同**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `id` | `str` |
| `kind` | `str` |
| `description` | `str` |
| `target` | `str` |
| `value` | `Any` |
| `why` | `str` |

### `PartLoopResult`（★ dataclass）

★★★ **闭环结果**（★ 逐字承验收：★「★ **所有通过项都绑定同一模型版本**」）。

| ★ 字段 | ★ 类型 |
|---|---|
| `binding` | `Any` |
| `baseline` | `dict` |
| `disturbances` | `list` |
| `reopen` | `dict` |
| `failures` | `list` |

### `DofPlan`（★ dataclass）

★★★★ **自由度/尺寸图**（★ 逐字承 EC05-T03）：

| ★ 字段 | ★ 类型 |
|---|---|
| `entities` | `int` |
| `relations` | `list` |
| `dimensions` | `list` |
| `intentional_dof` | `list` |

