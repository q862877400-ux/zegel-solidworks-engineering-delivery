# vd50-B-drawing —— 域 05-drawing · 只核「置信度 = 高」的条目

**来源**：`recon/audit-vs-official/audit-05-drawing-A.md` / `-B.md` / `-C.md`（三份里置信度为「中」的 B#5/B#6/B#7 **未碰**，按任务要求只核「高」）。
**核法**：每条两件事各查一遍 —— ①「官方的原文」去 `C:/swapi` 搜；②「我们的原文」去 `D:/AI/SW` 搜，片段要逐字对得上。
**口径**：只读 + 只写本文件；**不写行号**，只写可搜索的原文片段；给不出两段原文的一律不写。

## 总表

| 条目 | 文件 | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|
| A#1 | audit-05-drawing-A.md · #1 | 在 | 在 | **成立** |
| B#1 | audit-05-drawing-B.md · #1 | 在 | 在 | **成立** |
| B#2 | audit-05-drawing-B.md · #2 | 在（但**含义要更正**，见下） | 在 | **成立（附更正）** |
| B#3 | audit-05-drawing-B.md · #3 | 在 | 在 | **成立** |
| B#4 | audit-05-drawing-B.md · #4 | 在 | 在 | **成立** |
| C#1 | audit-05-drawing-C.md · #1 | 在 | 在 | **成立** |
| C#2 | audit-05-drawing-C.md · #2 | 在 | 在 | **成立** |
| C#3 | audit-05-drawing-C.md · #3 | 在 | 在 | **成立** |
| C#4 | audit-05-drawing-C.md · #4 | 在 | 在 | **成立** |

---

## A#1 · `_selection_marks` 把「选区类型」当「mark」存

**我们的原文（`scripts/sw_drawing_expose.py`）**

```python
mark = C.get_com_member(mgr, "GetSelectedObjectType3", i, -1)
if mark is not None:
    out[str(mark)] = out.get(str(mark), 0) + 1
```

docstring 逐字：

```python
"""★ 回读"当前选区里每个 mark 各有几个对象"（★ 判前置用；取不到回空 dict，不猜）。"""
```

下游逐字（`create_hole_table`）：

```python
pre = bool(marks.get("1", 0) >= 1 and marks.get("2", 0) >= 1)
```

**官方的原文（两段）**

`C:\swapi\types\ISelectionMgr\GetSelectedObjectType3.md`：

```
Type of object as defined in [[swSelectType_e]]
```

`C:\swapi\types\ISelectionMgr\GetSelectedObjectMark.md`：

```
**Signature**: `System.int GetSelectedObjectMark( System.int AtIndex )`
Number used as a mark for the selected item; this number is used by certain API functions that require ordered entity selection
```

**判定：成立。** 依据：`GetSelectedObjectType3` 官方逐字把返回值定义为 `swSelectType_e`（选区对象类型），而代码把同一个返回值当 mark 存进字典并按 `marks.get("1")/get("2")` 取值；`C:\swapi\enums\swSelectType_e.md` 里 `swSelEDGES = 1` / `swSelFACES = 2`，即这个 gate 实际判的是「至少一条边 + 至少一个面」，而代码与 `InsertHoleTable3` 的 mark 表要的「顶点=1 · 孔边与面=2」不是一回事；官方取 mark 的成员是另一个、arity 只有 1 的 `GetSelectedObjectMark`。

---

## B#1 · `SetTemplateName` 之前缺 `SetProperties` + `swDwgTemplateCustom`

**我们的原文（`scripts/sw_drawing_expose.py`）**

```python
ret = C.get_com_member(sheet, "SetTemplateName", str(format_path))
```

**官方的原文（`C:\swapi\types\ISheet\SetTemplateName.md` 的 `## Remarks`）**

```
- a custom template name, before calling this method, call [[ISheet::SetProperties]] and specify swDwgTemplates_e.swDwgTemplateCustom for the Templ parameter.
```

**判定：成立。** 依据：`set_sheet_format` 全函数只有上面这一个写调用，且 `scripts/sw_drawing_expose.py`、`scripts/sw_drawing_create_missing.py`、`scripts/sw_drawing.py` 三个点名文件里 grep `SetProperties` 与 `swDwgTemplateCustom` **命中 0 次**，官方要求的「先 `SetProperties` 置 `swDwgTemplateCustom`」这一步确实没做。

---

## B#2 · 标成「官方 Remarks 逐字」的那句不在 `SetTemplateName.md` 上

**我们的原文（`scripts/sw_drawing_expose.py` docstring + 紧随的调用）**

```
    ★ 官方 Remarks 逐字：调完要 `ForceRebuild3` 才刷新第一角/第三角投影；★ 这里顺带做掉。
```

```python
C.get_com_member(drawing_model, "ForceRebuild3", False)
```

**官方的原文（`C:\swapi\types\ISheet\SetTemplateName.md` 的 `## Remarks` 全段）**

```
If you want to use:

- a custom template name, before calling this method, call [[ISheet::SetProperties]] and specify swDwgTemplates_e.swDwgTemplateCustom for the Templ parameter.

- one of the standard templates provided by SOLIDWORKS, then there is no need to call ISheet::SetTemplateName. Instead, call ISheet::SetProperties and specify the appropriate enumerator for the Templ parameter.
```

（该页全文读完，**没有** `ForceRebuild3` 任何字样。）

**判定：成立 —— 但必须附一条更正，否则下游会被这条误导。**
依据：该条报的两件事都逐字对上了 —— 我们的 docstring 确实写着「官方 Remarks 逐字」，而 `SetTemplateName.md` 的 Remarks 里确实查不到这句话。
⚠ **更正**：这句话**不是编的，它在官方文档里逐字存在**，只是挂错了成员 ——

```
C:\swapi\types\IDrawingDoc\SetupSheet6.md
After calling this method, call [[IModelDoc2::ForceRebuild3]] to update any changes to first angle/third angle projections in the drawing views.
```

同款逐字还在 `C:\swapi\types\IDrawingDoc\SetupSheet5.md`（`Call [[IModelDoc2::ForceRebuild3]] after calling IDrawingDoc::SetupSheet5 to update any changes to first angle/third angle projections in the drawing views.`）与 `SetupSheet4.md`。
⇒ 所以缺陷性质是**出处挂错成员**（把 `SetupSheet*` 的 Remarks 写在 `SetTemplateName` 的函数里），不是「查不到出处」。清单原文已声明「不判定来源真伪」，此处把判定补上：**出处为真、归属为假**。

---

## B#3 · 剖面视图的前置只判「选区计数 > 0」

**我们的原文（`scripts/sw_drawing_expose.py`）**

```python
    pre = _selection_count(drawing_model)
    res = D.add_section_view(drawing_model, _mm(x_mm), _mm(y_mm))
    return _result("create_section_view", {"ok": res is not None, "view": res},
                   "视图数增量（★ 前置成立才算）", pre_ok=pre > 0)
```

**官方的原文（`C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md` 的 `## Remarks`）**

```
Before calling this method, select the section line or lines to use as a section line.
```

**判定：成立。** 依据：官方前置点明被选对象的**种类**是剖面线，而我们的前置判据只有 `pre > 0`（`GetSelectedObjectCount2(-1)` 的计数），任意类型对象入选区即算前置成立。

---

## B#4 · 局部视图缺官方示例里的两步前置

**我们的原文（`scripts/sw_drawing_expose.py`）**

docstring：

```
    """★ 局部视图（`CreateDetailViewAt4`，12 参）—— ★ 前置是"图上有局部圆（草图圆）"。
```

函数体（该函数里唯一的 COM 调用行）：

```python
    res = D.add_detail_view(drawing_model, _mm(x_mm), _mm(y_mm), scale, style=style, label=label,
```

**官方的原文（`C:\swapi\examples\Create_Detail_Circle_and_Detail_View_Example_VB.md`）**

```
    status = swDrawing.ActivateView("Drawing View4")
```

```
    Set swSketchSegment = swSketchManager.CreateCircle(0.007581, 0.053509, 0#, 0.013533, 0.016475, 0#)
```

```
    Set swView = swDrawing.CreateDetailViewAt4(0.22305342706156, 7.62140266484527E-02, 0, swDetViewSTANDARD, 1, 1, "A", swDetCircleCIRCLE, True, True, False, 5)
```

**判定：成立。** 依据：官方示例在 `CreateDetailViewAt4` 之前有 `ActivateView` 与 `SketchManager.CreateCircle` 两步，而 `create_detail_view` 函数体里既不激活视图、也不建局部圆，返回值里也没有这两个前置的字段。

---

## C#1 · `IView.Name` 是官方标 Obsolete 的成员（第 1 处调用）

**我们的原文（`scripts/sw_drawing_expose.py` 的 `_view_by_name`）**

```python
            if str(C.get_com_member(view, "Name") or "") == str(view_name):
```

**官方的原文（`C:\swapi\types\IView\Name.md`）**

```
Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].
```

**判定：成立。** 依据：官方逐字把 `IView.Name` 标为 Obsolete 且点名后继是 `GetName2`/`SetName2`，而 `_view_by_name` 整个函数（`GetFirstView`/`GetNextView` 链）里取视图名只有这一行、走的正是被废弃的成员；`create_hole_table` 逐字 `view = _view_by_name(drawing_model, view_name)` 靠它按名解析视图。

---

## C#2 · `IView.Name` 是 Obsolete 成员（第 2 处调用）

**我们的原文（`scripts/sw_drawing_create_missing.py` 的 `_view_name`）**

```python
def _view_name(view) -> str | None:
    raw = _read(view, "GetName2")
    if raw is None:
        raw = _read(view, "Name")
```

**官方的原文（`C:\swapi\types\IView\Name.md`）**

```
Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].
```

**判定：成立。** 依据：同一 Obsolete 成员的第二个调用点 —— `GetName2` 回 `None` 时兜底去读 `Name`，逐字对上。

---

## C#3 · 修订表 `shape` 默认值 0 不在官方枚举里

**我们的原文（`scripts/sw_drawing_expose.py`）**

```python
def create_revision_table(drawing_model, *, x_mm: float, y_mm: float, anchor_type: int,
                          template: str = "", shape: int = 0,
                          auto_update_zoom_cells: bool = True) -> dict:
```

该值逐字流向 `Shape` 形参：

```python
        tbl = C.get_com_member(sheet, "InsertRevisionTable2", False, _mm(x_mm), _mm(y_mm),
                               int(anchor_type), str(template), int(shape),
                               bool(auto_update_zoom_cells))
```

**官方的原文（`C:\swapi\types\ISheet\InsertRevisionTable2.md`）**

```
- **Shape**: Revision symbol shape as defined in [[swRevisionTableSymbolShape_e]]
```

`C:\swapi\enums\swRevisionTableSymbolShape_e.md`：

```
enum_member_count: 4
| swRevisionTable_CircleSymbol | 1 |
| swRevisionTable_SquareSymbol | 2 |
| swRevisionTable_TriangleSymbol | 3 |
| swRevisionTable_HexagonSymbol | 4 |
```

**判定：成立。** 依据：官方把该实参逐字绑定到 `swRevisionTableSymbolShape_e`，而该枚举 4 个成员穷举为 1/2/3/4、**没有 0**，故默认值 `shape: int = 0` 不是任何合法成员。

---

## C#4 · 局部视图 `shape_intensity` 默认值 0 落在官方有效范围外

**我们的原文（`scripts/sw_drawing_expose.py`）**

```python
                       no_outline: bool = False, shape_intensity: int = 0) -> dict:
```

逐字透传：

```python
                            shape_intensity=shape_intensity)
```

**官方的原文（`C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md` 的 Parameters）**

```
- **ShapeIntensity**: Intensity of jagged outline; valid range is 1 (most) to 5 (least) and only valid if JaggedOutline is true and NoOutline is false
```

**判定：成立。** 依据：官方逐字给的有效范围是 1(most)–5(least)，默认值取 0 落在范围外。
⚠ 一句补充（不改变判定）：同一句还写明该形参「only valid if JaggedOutline is true」，而默认 `jagged_outline: bool = False` ⇒ **默认值下这个越界值是惰性的**，只有调用方显式开启锯齿轮廓时才会被官方拒。

---

## 三行

- **核了几处**：**9 处**（A#1 · B#1 · B#2 · B#3 · B#4 · C#1 · C#2 · C#3 · C#4；B#5/B#6/B#7 置信度为「中」，按要求未碰）
- **对不上几处**：**0 处** —— 9 条的两段原文全部逐字对上，判定全为「成立」
- **唯一需要更正的一条**：**B#2** —— 被判「不在官方页」的那句话**确实逐字存在于官方文档**（`IDrawingDoc\SetupSheet6.md` / `SetupSheet5.md` / `SetupSheet4.md` 的 Remarks），只是挂错了成员 ⇒ 缺陷性质是**出处挂错**，不是「查不到出处」；该条清单原文已声明不判定来源真伪，此处补上：**出处为真、归属为假**。