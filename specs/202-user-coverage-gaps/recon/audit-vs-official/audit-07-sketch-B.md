# audit-07 · 域 07-sketch · 核对 B（前置与 mark）

**核对口径**：只报「我们的原文」与「官方原文」对不上之处（前置有没有做、mark 传的对不对、调用序缺没缺步）。
核对范围：`scripts/sw_sketch.py` · `sw_sketch_edit.py` · `sw_sketch_modify_ops.py` · `sw_sketch_edit_ops.py`（四个文件均存在，无替代查找）。
凡给不出官方可搜索原文的一条，未列入。

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `sw_sketch_edit_ops.py`（`select_sketch_segment` 内）：`ok = get_com_member(seg, "Select4", bool(append), _empty_callout())`<br>调用点 `sketch_trim` 内：`_select_spec(model, selection)` | `C:\swapi\types\ISketchManager\SketchTrim.md` Remarks：`Before calling this method, you must edit a sketch and select sketch segments to trim using [[IModelDocExtension::SelectByID2]].`<br>同页 `swSketchTrimTwoEntities` 条：`Use IModelDocExtension::SelectByID2 with Mark = 0 to select two sketch segments, specifying their pick points.`<br>`C:\swapi\examples\Trim_Sketch_Entities_Example_CSharp.md`：`status = swModelDocExt.SelectByID2("Line6", "SKETCHSEGMENT", 0.0391723509933775, -0.0466042594822396, 0, true, 0, null, 0);` | 剪裁的官方前置点名了**具体入口 `SelectByID2`**，并在 TwoEntities 处点名 **mark = 0**、**按 pick point 选**；我们的选择路径是 `Select4`（实参只有 append 与 callout，无 mark、无 pick point）。 | 高 |
| 2 | `sw_sketch_edit_ops.py`（`select_sketch_segment` 内）：`ok = get_com_member(seg, "Select4", bool(append), _empty_callout())`<br>调用点 `sketch_offset` 内：`_select_spec(model, selection)` | `C:\swapi\examples\Sketch_Offset_Example_CSharp.md`：`status = swModelDocExt.SelectByID2("Line3", "SKETCHSEGMENT", 0, 0, 0, false, 1, null, 0);` 紧接 `status = swSketchManager.SketchOffset2(0.00254, true, true, (int)swSkOffsetCapEndType_e.swSkOffsetArcCaps, (int)swSkOffsetMakeConstructionType_e.swSkOffsetMakeBothConstruction, true);` | 官方例子在 `SketchOffset2` 之前用 `SelectByID2` 选草图段、第 7 个实参为 **mark = 1**；我们的 `Select4` 路径**没有任何 mark**。 | 高 |
| 3 | `sw_sketch_edit_ops.py`（`sketch_circular_pattern` 内，调用前一行）：`_select_spec(model, selection)` | `C:\swapi\examples\Create_and_Edit_Circular_Sketch_Pattern_Example_CSharp.md`：`swModel.ClearSelection2(true);` → `vSkLines = swSketchMgr.CreateCornerRectangle(-0.005867589431389, 0.03694408160504, 0, 0.004563680668858, 0.02673012963188, 0);` → `boolstatus = swSketchMgr.CreateCircularSketchStepAndRepeat(0.03184378021964, 4.732863934409, 4, 1.570796326795, true, "", true, true, true);` | 官方例子里这三句之间**没有任何选中动作**（上一步刚 `ClearSelection2(true)`），种子是刚画出的矩形；我们的 `sketch_circular_pattern` 在调用前**无条件先选**一段草图段。 | 中 |
| 4 | `sw_sketch.py`（`merge_points`）：docstring `"""合并重合点。⚠ 容差单位官方无说明。"""`，函数体 `return bool(get_com_member(sketch, "MergePoints", float(tolerance)))` | `C:\swapi\types\ISketch\MergePoints.md` Remarks：`This method requires that only one open contour exists in the sketch.` | 官方写明的前置是「**草图里只能有一个开放轮廓**」；我们的 `merge_points` 全函数只有一句「容差单位官方无说明」，**既未做该前置检查、也未在注释里提到它**。 | 高 |
| 5 | `sw_sketch_edit_ops.py`（`sketch_extend` 内）：`_select_spec(model, selection)` | `C:\swapi\examples\Extend_Sketch_Entity_Example_CSharp.md`：`// Set the selection mode to default` / `swModel.SetPickMode();` / `boolstatus = swModelDocExt.SelectByID2("Line1", "SKETCHSEGMENT", 0.0, 0.0, 0.0, false, 0, null, 0);` / `boolstatus = swSketchMgr.SketchExtend(0.0, 0.0, 0.0);` | 官方例子在选中前有一步 `swModel.SetPickMode()`（把选择模式置为 default），我们的选择路径里**没有这一步**。 | 中 |

## 核对计数

- **核了 57 处** —— 四个文件里的 COM 调用点（`sw_sketch.py` 30 · `sw_sketch_edit.py` 7 · `sw_sketch_modify_ops.py` 8 · `sw_sketch_edit_ops.py` 12）；其中逐条打开官方原文（16 个成员页 + 5 个官方例子）核对的有 21 处。
- **报了 5 条**。
- **置信度为高的是：第 1、2、4 条**。
