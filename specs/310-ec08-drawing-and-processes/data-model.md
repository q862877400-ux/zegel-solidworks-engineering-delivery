# Data Model — 310-ec08-drawing-and-processes

**Feature**: `specs/310-ec08-drawing-and-processes/`

**来源**: ★ **从 `scripts/engineering/processes.py` 的 AST 提取**（★ 真源码，★ 不编）

---

### `AnnotationKind`（★ class）

★ 标注种类（★ 逐字承 EC08A：★「★ **功能尺寸/基准/配合**、**公差**、**材料**、

### `Annotation`（★ dataclass）

★★ **一个标注**（★ 带**它标的几何** —— ★ 悬空检测靠它）。

| ★ 字段 | ★ 类型 |
|---|---|
| `kind` | `str` |
| `text` | `str` |
| `target` | `str` |
| `value` | `float | None` |
| `unit` | `str` |

### `DanglingReport`（★ dataclass）

★★ **悬空标注报告**。

| ★ 字段 | ★ 类型 |
|---|---|
| `annotations` | `list` |

### `DrawingEvidence`（★ dataclass）

★★★★ **工程图证据**（★ 逐字承验收：★「★ 尺寸值、基准、公差、**模型配置版本**

| ★ 字段 | ★ 类型 |
|---|---|
| `items` | `list` |
| `model_config` | `str` |
| `model_revision` | `str` |

### `SheetMetalSpec`（★ dataclass）

★★ **钣金规格**（★ 逐字承 EC08B：★「★ 厚度/折弯半径/**工艺参数**、

| ★ 字段 | ★ 类型 |
|---|---|
| `thickness_m` | `float` |
| `bend_radius_m` | `float` |
| `k_factor` | `float` |
| `bends` | `list` |

### `WeldmentCutList`（★ dataclass）

★★ **焊件切割清单**（★ 逐字承 EC08C：★「★ 型材、连接、**切割清单**、

| ★ 字段 | ★ 类型 |
|---|---|
| `rows` | `list` |

### `SurfaceContinuity`（★ dataclass）

★★★★★ **曲面连续性**（★ 逐字承 EC08D）：

| ★ 字段 | ★ 类型 |
|---|---|
| `patches` | `int` |
| `seams` | `list` |
| `max_deviation_mm` | `float` |
| `min_thickness_mm` | `float` |

