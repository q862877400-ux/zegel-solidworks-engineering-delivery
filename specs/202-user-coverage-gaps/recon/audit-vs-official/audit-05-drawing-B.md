# audit-05-drawing-B — 核对 B（前置与 mark）

- 域：`05-drawing`
- 核对口径：**只做核对 B** —— 官方 `## Remarks` / 官方示例的**前置、先选什么、mark 几、调用序** vs 我们代码里**实际做没做那一步、mark 传的对不对**。
- 我们这边点名要读的文件（`scripts/`）：
  - `scripts/sw_drawing.py` —— ★ **纯桥接文件**，全文 29 行只做 `spec_from_file_location` + `globals()` 再导出，**没有一处 COM 调用** ⇒ 本文件对它核了 **0 处调用**（不是漏读）。
  - `scripts/sw_drawing_expose.py`
  - `scripts/sw_drawing_create_missing.py`
- 官方源：`C:\swapi\types\*.md`（精确签名 + Remarks）、`C:\swapi\examples\*.md`（调用序）。
- ★ 覆盖范围声明（铁律 5）：`sw_drawing_expose.py` 与 `sw_drawing.py` 的**部分** COM 调用发生在桥接目标 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 里，**该文件不属本路点名范围** ⇒ 本表每条的「我们的原文」只取自三个点名文件；对需要跨到 `drawing_workflow.py` 才能下结论的，一律降为「中」置信度或不报。

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_drawing_expose.py` · `ret = C.get_com_member(sheet, "SetTemplateName", str(format_path))`（整个 `set_sheet_format` 只有这一个写调用，没有别的写调用） | `C:\swapi\types\ISheet\SetTemplateName.md` · `## Remarks`：`- a custom template name, before calling this method, call [[ISheet::SetProperties]] and specify swDwgTemplates_e.swDwgTemplateCustom for the Templ parameter.` | 官方写明「用自定义模板时，**调用本方法之前**要先调 `ISheet::SetProperties` 并把 `Templ` 置为 `swDwgTemplateCustom`」；我们直接调 `SetTemplateName`，**这一步前置在整个点名文件里没有出现过** | 高 |
| 2 | `scripts/sw_drawing_expose.py` · docstring 里 `★ 官方 Remarks 逐字：调完要 `ForceRebuild3` 才刷新第一角/第三角投影；★ 这里顺带做掉。`，紧接着代码 `C.get_com_member(drawing_model, "ForceRebuild3", False)` | `C:\swapi\types\ISheet\SetTemplateName.md` · `## Remarks` 全段只有两句：`If you want to use:` / `- a custom template name, before calling this method, call [[ISheet::SetProperties]] …` / `- one of the standard templates provided by SOLIDWORKS, then there is no need to call ISheet::SetTemplateName. …` —— **该页没有 `ForceRebuild3` 任何字样** | 我们把「要 `ForceRebuild3` 刷新第一角/第三角投影」标注成「**官方 Remarks 逐字**」；本机能查到的官方页 `SetTemplateName.md` 的 Remarks 里**查不到**这句话（`D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` 解包目录里只有示例页、无该成员页 ⇒ 记「查不到」，不判定来源真伪） | 高 |
| 3 | `scripts/sw_drawing_expose.py` · `pre = _selection_count(drawing_model)` / `res = D.add_section_view(drawing_model, _mm(x_mm), _mm(y_mm))` / `pre_ok=pre > 0`（`pre` 只是 `GetSelectedObjectCount2(-1)` 的计数） | `C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md` · `## Remarks`：`Before calling this method, select the section line or lines to use as a section line.` | 官方的前置指定了**被选对象的种类**（剖面线 line 或多条）；我们的前置判据只是「选区计数 > 0」，任意类型对象都算成立，**不判是不是剖面线、也不代选** | 高 |
| 4 | `scripts/sw_drawing_expose.py` · docstring `★ 局部视图（`CreateDetailViewAt4`，12 参）—— ★ 前置是"图上有局部圆（草图圆）"。`，函数体只有 `res = D.add_detail_view(drawing_model, _mm(x_mm), _mm(y_mm), scale, style=style, label=label,` 一行 | `C:\swapi\examples\Create_Detail_Circle_and_Detail_View_Example_VB.md` · 调用序：`status = swDrawing.ActivateView("Drawing View4")` → `Set swSketchSegment = swSketchManager.CreateCircle(0.007581, 0.053509, 0#, 0.013533, 0.016475, 0#)` → `Set swView = swDrawing.CreateDetailViewAt4(0.22305342706156, 7.62140266484527E-02, 0, swDetViewSTANDARD, 1, 1, "A", swDetCircleCIRCLE, True, True, False, 5)` | 官方示例在 `CreateDetailViewAt4` 之前有**两步**：`ActivateView(视图名)` 与 `SketchManager.CreateCircle(局部圆)`；我们该函数既不激活视图、也不建局部圆，返回值里也没有这两个前置的字段 | 高 |
| 5 | `scripts/sw_drawing_create_missing.py` · `sel = _selection_count(model)` 与 `"preconditions_held": bool(sel and sel >= 1)` | `C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt2.md` · 首行摘要：`Creates an auxiliary view based on a selected edge in a drawing view.` | 官方前置指明是「**视图里的一条边**」；我们的判据只是「选区里有 ≥1 个对象」，**不判类型、也不判是不是在视图里** | 中 |
| 6 | `scripts/sw_drawing_create_missing.py` · `sel = _selection_count(model)`、`"preconditions_held": bool(sel and sel >= 1)`，docstring 复述为 `★ 官方第 1 步逐字：'Select one or more **views or sheets**'` | `C:\swapi\types\IDrawingDoc\AutoBalloon5.md` · `## Remarks`：`1. Select one or more views or sheets for which to automatically create BOM balloons.` | 官方第 1 步限定被选对象是**视图或图纸**；我们的第 1 步判据只是计数 ≥1，任意类型对象即算成立（★ 第 2/3/4 步我们**逐条照做**，与官方一致） | 中 |
| 7 | `scripts/sw_drawing_expose.py` · `res = D.auto_insert_center_marks(drawing_model, requirements)`（该包装层两步前置都不做、不回读，返回值只有 `_result(...)` 的通用字段） | `C:\swapi\types\IView\AutoInsertCenterMarks2.md` · `## Remarks`：`Before calling this method:` / `1. Call [[IDrawingDoc::ActivateView]] with the name of the view to activate.` / `2. Call [[IDrawingDoc::ActiveDrawingView]] to get a handle on the activated view.` | 官方要求调用前**两步**（激活视图 + 取激活视图句柄）；点名文件这一层两步都没有、也不把前置带进返回值。★ 降为「中」的原因：真正的调用在桥接目标 `drawing_workflow.py`（不属本路点名文件），那里有 `ActivateView` 而**全仓 grep 不到 `ActiveDrawingView` 的调用** | 中 |

## 没报的（防含水，留痕）

- `IView.InsertHoleTable3` 的 mark 表：官方 `InsertHoleTable3.md` 的 mark 表有 4 行（顶点=1 · 孔边与面=2 · X 向参考=4 · Y 向参考=8），我们 `pre` 只 gate 了 1 与 2。★ 但官方示例 `C:\swapi\examples\Insert_Hole_Table_Example_VB.md` 实际只用了 mark 1（`VERTEX`）与 mark 2（`FACE`）⇒ **不构成对不上，不报**。
- `IModelDoc2.InsertNote`：官方 Remarks `The leader attachment points for the new note come from the selections made before calling this method.` 且 `If there are no selections, the note: … Is free standing` ⇒ **零选区是合法的**，我们不 gate 选择正确，**不报**。
- `IModelDocExtension.InsertSurfaceFinishSymbol3`：官方 `uses the location parameters for this method only if … leaderType != swNO_LEADER`，我们在 `leader_type == 0` 时主动传 `0,0,0`，且 `_selection_count` 在调用**之前**读（对应 "based on the last selection"）⇒ **一致，不报**。
- `IDrawingDoc.CreateDrawViewFromModelView3`：官方要求 pathname 含 `.sldprt`/`.sldasm`、`ViewName` 含星号 ⇒ 我们默认 `"*Front"` 且 `pre_ok` 已查后缀，**一致，不报**。
- `Create1stAngleViews2` / `CreateFirstAngleViews2`：本机 `C:\swapi\types\IDrawingDoc\` 下**没有**这两个成员的 md（`CreateSectionViewAt5.md` 的 See Also 里点名的是 `Create1stAngleViews2`）⇒ 官方页查不到，**按铁律 5 不报**。

## 结尾三行

核了 **34** 处（`sw_drawing.py` 0 处：纯桥接、无 COM 调用；`sw_drawing_expose.py` 17 处；`sw_drawing_create_missing.py` 17 处）。
报 **7** 条（核对 B：前置与 mark）。
置信度为**高**的是第 **1、2、3、4** 条（第 5、6、7 条为中）。