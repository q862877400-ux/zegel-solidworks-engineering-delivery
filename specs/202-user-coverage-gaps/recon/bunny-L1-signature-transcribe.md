# L1 · 纯抄录：三个工程图函数的定义行与实际调用的官方 COM 成员

- **档位**：L1 纯抄录（不设计、不补全、不评价）
- **源文件**：`D:\AI\SW\subskills\solidworks-engineering-drawing\scripts\drawing_workflow.py`（读取时 2746 行）
- **抄录范围**：`def …` 定义行（含全部形参与默认值）逐字；函数体内**真的被调用**的官方 COM 成员名逐字（注释里提到的**不**计入）
- **本文件由抄录产生，未改动任何已有文件，未运行 SolidWorks / pytest**

---

## 1. `add_section_view` —— 定义行在第 **996** 行

### 1.1 定义行（逐字，第 996 行）

```python
def add_section_view(drawing_model, x, y):
```

### 1.2 函数体（第 997–998 行）

```python
997:     """在当前选择的剖切线位置创建剖视图"""
998:     return drawing_model.CreateSectionViewAt5(x, y, 0, "", 0, None, 0)
```

### 1.3 函数体内实际调用的官方 COM 成员（逐字）

| 成员名 | 行 | 调用形态 |
|---|---|---|
| `CreateSectionViewAt5` | 998 | `drawing_model.CreateSectionViewAt5(x, y, 0, "", 0, None, 0)` |

共 **1** 个。

---

## 2. `add_detail_view` —— 定义行从第 **1020** 行开始（多行签名，续到 1033 行）

### 2.1 定义行（逐字，第 1020–1033 行）

```python
1020: def add_detail_view(
1021:     drawing_model,
1022:     x,
1023:     y,
1024:     scale=2.0,
1025:     *,
1026:     style=DET_VIEW_STYLES["standard"],
1027:     label="",
1028:     show_type=DET_CIRCLE_SHOW_TYPES["profile"],
1029:     full_outline=False,
1030:     jagged_outline=False,
1031:     no_outline=False,
1032:     shape_intensity=0,
1033: ):
```

### 2.2 调用点（第 1061–1074 行）

```python
1061:     return drawing_model.CreateDetailViewAt4(
1062:         float(x),
1063:         float(y),
1064:         0.0,
1065:         int(style),
1066:         float(scale),
1067:         1.0,
1068:         str(label),
1069:         int(show_type),
1070:         bool(full_outline),
1071:         bool(jagged_outline),
1072:         bool(no_outline),
1073:         int(shape_intensity),
1074:     )
```

### 2.3 函数体内实际调用的官方 COM 成员（逐字）

| 成员名 | 行 | 调用形态 |
|---|---|---|
| `CreateDetailViewAt4` | 1061 | `drawing_model.CreateDetailViewAt4(` … 12 个实参，至 1074 行 |

共 **1** 个。
★ 第 1001–1019 行的「来源」注释块与 1034–1060 行的 docstring 里也出现 `CreateDetailViewAt4`，按规则**不计入**（只是注释/文档字符串）。

---

## 3. `auto_insert_center_marks` —— 定义行在第 **1878** 行

### 3.1 定义行（逐字，第 1878 行）

```python
def auto_insert_center_marks(drawing_model, requirements) -> dict:
```

### 3.2 函数体内实际调用的官方 COM 成员（逐字）

| 成员名 | 行 | 调用形态 |
|---|---|---|
| `GetCurrentSheet` | 1890 | `_safe_member(drawing_model, "GetCurrentSheet")` |
| `GetViews` | 1891 | `_safe_member(sheet, "GetViews", default=[])` |
| `GetPathName` | 1893 | `_safe_member(drawing_model, "GetPathName", default="")` |
| `Name` | 1923 | `_safe_member(view, "Name", default="")` |
| `ActivateView` | 1925 | `_safe_member(drawing_model, "ActivateView", view_name)` |
| `AutoInsertCenterMarks2` | 1927–1940 | `get_com_member(view, "AutoInsertCenterMarks2", …)`（10 个实参） |
| `ForceRebuild3` | 1943 | `_safe_member(drawing_model, "ForceRebuild3", False)` |
| `GraphicsRedraw2` | 1944 | `_safe_member(drawing_model, "GraphicsRedraw2")` |
| `Name` | 1958 | `_safe_member(view, "Name", default="")`（第二次） |

按首次出现去重共 **8** 个不同成员：`GetCurrentSheet`、`GetViews`、`GetPathName`、`Name`、`ActivateView`、`AutoInsertCenterMarks2`、`ForceRebuild3`、`GraphicsRedraw2`。

### 3.3 ★ 区分：函数体里出现但**不是** COM 成员的调用（非官方成员，不计入上表）

| 被调用者 | 行 | 性质 |
|---|---|---|
| `_safe_member` | 1890, 1891, 1893, 1923, 1925, 1943, 1944, 1958 | 本文件内的 Python 辅助函数（第 102 行定义），内部经 `get_com_member` 走 COM |
| `_as_sequence` | 1891 | 本文件内 Python 辅助函数（第 113 行定义） |
| `_map_standard_views_from_sheet_views` | 1892 | 本文件内 Python 函数 |
| `_normalise_orientation` | 1897 | 本文件内 Python 函数 |
| `_view_center_marks` | 1919, 1945 | 本文件内 Python 函数 |
| `get_com_member` | 1927 | 仓库内的 COM 取成员辅助函数 |
| `bool` / `len` / `int` / `max` / `str` | 多处 | Python 内建 |

### 3.4 附注（**不在**「函数体内实际调用」口径内，仅备查）

`_view_center_marks`（本文件第 1633–1650 行）在被本函数调用时，其**自身**函数体内实际调用的 COM 成员是：
`GetFirstCenterMark2`（1635）、`GetFirstCenterMark`（1637）、`GetNext`（1646）、`GetCenterMarks`（1650）。
★ 这四个是**辅助函数体**里的调用，不是 `auto_insert_center_marks` 函数体里的调用，故未并入 3.2 表。

---

## 4. 汇总

| 函数 | 定义行行号 | 定义行是否单行 | 函数体内直接调用的官方 COM 成员数（去重） |
|---|---|---|---|
| `add_section_view` | **996** | 是 | 1（`CreateSectionViewAt5`） |
| `add_detail_view` | **1020**（签名续到 1033） | 否，多行 | 1（`CreateDetailViewAt4`） |
| `auto_insert_center_marks` | **1878** | 是 | 8（见 3.2） |