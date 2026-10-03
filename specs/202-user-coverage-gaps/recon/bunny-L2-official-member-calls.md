# bunny-L2 · `drawing_workflow.py` 函数 → 官方 COM 成员调用对照

- **被审文件**：`D:\AI\SW\subskills\solidworks-engineering-drawing\scripts\drawing_workflow.py`（2746 行）
- **产出口径**：**纯静态分析**（Python `ast` + `ripgrep` 双源核对行号）。**未运行 SolidWorks、未运行 pytest、未改动任何已有文件**。
- **行号基准**：以 Python 词法/语法分析结果为准（`ast` 的 `lineno`），并与 `ripgrep` 逐行核对一致。
  ⚠ 内置 `read` 工具的行号在本文件上偏移 +2～+5（它把若干行合并显示），**不要用它读出的行号**。

---

## 一、判断口径（"官方 COM 成员"怎么算）

**算**：在**某个函数体自身范围内**，通过下列三条通道触达、且**名字是该函数里写出来的成员名**的调用——

1. `get_com_member(<obj>, "<Name>", …)`
2. `_safe_member(<obj>, "<Name>", …)`
3. 直接属性访问 `<com_obj>.成员名(…)` / `<com_obj>.成员名`（**属性读写也算**，例如 `view.ScaleRatio = …` 记 `ScaleRatio`）

**不算**：

- 本地辅助函数之间的互相调用（**委派不计**）。例：`generate_drawing_from_spec` 调了 `setup_current_sheet`、`create_adaptive_standard_views` 等本地函数 —— 这些本地函数各自的 COM 成员记在**它们自己**那一行，不上浮。
- 标准库 / pywin32：`math.*`、`re.*`、`Path.*`、`Fraction`、`str/upper/casefold/get/append`、`pythoncom.VT_*`、`VARIANT(...)`、`_win32com.GetActiveObject`、`_oleobj_.InvokeTypes`。
- 局部变量名、字符串常量里不是成员名的那些（例如 `"DRAWING_VIEW_CREATE_FAILED"`）、注释与来源块里提到的名字。
- 嵌套 `def` 体内的成员 —— **记在嵌套函数自己那一行**（`line_units` / `view_record` / `move_if_needed`），不并进父函数。

**三条补充裁定**（都已在表内就地标注）：

- **动态派发的成员名**也计入，因为它们最终仍调的是官方成员：`create_adaptive_standard_views` 的 `_safe_member(drawing_model, candidate, …)`、`create_standard_views_with_projection` 与 `_apply_view_layout`/`_set_view_center` 的 `getattr(obj, "…")`、`_table_cell_text` 的成员名循环表、`activate_annotation_view` 的 `method` 变量 —— 各自的候选名**逐个列出**。
- **`getattr(obj, "<Name>")`** 视为成员探测（等价于直接成员调用），计入。
- **`_oleobj_.InvokeTypes(dispid, …)`** 是 pywin32 的按 DISPID 晚期绑定，**成员名不在代码里** ⇒ 记 0 个字面量成员；在下方"四、按 DISPID 晚期绑定的成员（代码里没有名字）"单列，不混进表里的去重名单。

---

## 二、函数 → 官方 COM 成员对照表

`#` 按源码顺序（含私有 `_xxx`，含 3 个嵌套 `def`）。

| # | 函数名 | 定义行号 | 它调用的官方 COM 成员名（去重，逐个列出） |
|---|---|---|---|
| 1 | `_safe_member` | 102 | —（转发器：`get_com_member(obj, name, …)` 的 `name` 是入参，本体内无字面量成员名） |
| 2 | `_as_sequence` | 113 | — |
| 3 | `_normalise_box` | 122 | — |
| 4 | `_annotation_box` | 148 | `GetAnnotation`、`GetBox` |
| 5 | `_view_display_dimensions` | 154 | `GetDisplayDimensions`、`GetFirstDisplayDimension`、`GetFirstDisplayDimension5`、`GetNextDisplayDimension` |
| 6 | `auto_arrange_drawing_dimensions` | 166 | `AlignDimensions`、`ClearSelection2`、`Extension`、`ForceRebuild3`、`GetAnnotation`、`GetCurrentSheet`、`GetSheetNames`、`GetViews`、`GraphicsRedraw2`、`Name`、`Select`、`Select2`、`Sheet` |
| 7 | `_finite_positive` | 275 | — |
| 8 | `_dimension_text_evidence` | 286 | `GetText` |
| 9 | `estimate_dimension_text_box` | 313 | `CharHeight`、`CharSpacingFactor`、`GetAnnotation`、`GetPosition`、`GetTextFormat`、`WidthFactor` |
| 10 | `line_units`（嵌套于 #9） | 348 | — |
| 11 | `select_drawing_template` | 406 | — |
| 12 | `plan_standard_view_layout` | 453 | — |
| 13 | `view_record`（嵌套于 #12） | 548 | — |
| 14 | `_scale_ratio` | 590 | — |
| 15 | `_apply_view_layout` | 596 | `GetOrientationName`、`Name`、`SetViewPosition`、`UseParentScale`※、`PositionLocked`※、`ScaleRatio`※、`Position`※ |
| 16 | `_normalise_orientation` | 631 | — |
| 17 | `_view_position` | 650 | `Position` |
| 18 | `_set_view_center` | 661 | `SetViewPosition`、`Position`※ |
| 19 | `_refine_standard_view_spacing` | 678 | `GetOutline` |
| 20 | `move_if_needed`（嵌套于 #19） | 694 | `GetOutline` |
| 21 | `_collect_drawing_views` | 738 | `GetCurrentSheet`、`GetFirstView`、`GetNextView`、`GetViews` |
| 22 | `_map_native_standard_views` | 755 | `GetBaseView`、`GetOrientationName`、`GetReferencedModelName`、`Name` |
| 23 | `_map_standard_views_from_sheet_views` | 790 | `GetBaseView`、`GetOrientationName`、`Type` |
| 24 | `create_adaptive_standard_views` | 806 | `CreateDrawViewFromModelView3`、`CreateFirstAngleViews2`◇、`Create3rdAngleViews2`◇、`ForceRebuild3`、`GraphicsRedraw2` |
| 25 | `create_standard_views` | 941 | `Create3rdAngleViews2` |
| 26 | `create_standard_views_with_projection` | 952 | `CreateFirstAngleViews2`◇、`Create3rdAngleViews2`◇ |
| 27 | `add_view` | 978 | `CreateDrawViewFromModelView3`、`ScaleRatio`※ |
| 28 | `add_section_view` | 998 | `CreateSectionViewAt5` |
| 29 | `add_detail_view` | 1022 | `CreateDetailViewAt4` |
| 30 | `insert_dimensions` | 1079 | `ActivateView`、`Extension`、`ForceRebuild3`、`GetCurrentSheet`、`GetViews`、`GraphicsRedraw2`、`InsertModelAnnotations3`、`InsertModelAnnotations4`、`Name`、`SelectByID2` |
| 31 | `_note_text` | 1151 | `GetText` ＋DISPID 2（见第四节） |
| 32 | `_note_annotation` | 1166 | `GetAnnotation` ＋DISPID 85（见第四节） |
| 33 | `_set_annotation_position` | 1183 | `SetPosition2` ＋DISPID 91（见第四节） |
| 34 | `_annotation_position` | 1201 | `GetPosition` |
| 35 | `_note_box` | 1214 | `GetExtent` ＋DISPID 22（见第四节） |
| 36 | `_note_evidence` | 1228 | —（纯本地组合：`_note_annotation` + `_annotation_position` + `_note_box`） |
| 37 | `add_note` | 1238 | `InsertNote`、`ForceRebuild3` |
| 38 | `insert_bom_table` | 1326 | `Extension`、`InsertBomTable4` |
| 39 | `set_sheet_format` | 1400 | `GetCurrentSheet`、`SetTemplateName` |
| 40 | `add_sheet` | 1411 | `NewSheet4` |
| 41 | `add_a3_sheet` | 1426 | —（委派：`select_drawing_template` + `add_sheet`） |
| 42 | `setup_current_sheet_as_a3` | 1453 | `GetCurrentSheet`、`GetName`、`SetupSheet6` |
| 43 | `get_all_views` | 1521 | `GetCurrentSheet`、`GetViews`、`Name`、`Type`、`ScaleRatio` |
| 44 | `_paper_size_from_template` | 1536 | — |
| 45 | `_table_cell_text` | 1556 | `DisplayedText2`、`DisplayedText`、`Text2`、`Text`（◇ 成员名循环表） |
| 46 | `_table_evidence` | 1570 | `BomFeature`、`ColumnCount`、`Configuration`、`RowCount`、`Title`、`Type` |
| 47 | `_annotation_text_parts` | 1605 | `GetTextCount`、`GetTextAtIndex` |
| 48 | `_professional_annotation_record` | 1621 | —（委派：`_annotation_text_parts` + `_annotation_box`） |
| 49 | `_view_center_marks` | 1633 | `GetCenterMarks`、`GetFirstCenterMark`、`GetFirstCenterMark2`、`GetNext` |
| 50 | `_collect_view_professional_annotations` | 1653 | `GetCenterLines`、`GetDatumIdentifier`、`GetDatumTags`、`GetDirectionOfLay`、`GetFrameCount`、`GetFrameSymbols3`、`GetFrameValues`、`GetGTols`、`GetLabel`、`GetSFSymbols`、`GetSymbol`、`GetSymbolType`、`GetWeldSymbols`、`ShowLines`、`Size`、`Style` |
| 51 | `inspect_drawing_structure` | 1707 | `FullName`、`GetCurrentSheet`、`GetDimension`、`GetHoleCalloutVariables`、`GetName`、`GetNameForSelection`、`GetNotes`、`GetOrientationName`、`GetOutline`、`GetSheetNames`、`GetTableAnnotations`、`GetTemplateName`、`GetText`、`GetViews`、`IsHoleCallout`、`Name`、`ScaleRatio`、`Sheet`、`Type` |
| 52 | `auto_insert_center_marks` | 1883 | `ActivateView`、`AutoInsertCenterMarks2`、`ForceRebuild3`、`GetCurrentSheet`、`GetPathName`、`GetViews`、`GraphicsRedraw2`、`Name` |
| 53 | `export_sheet_to_pdf` | 1996 | `Extension`、`GetExportFileData`、`GetSheetNames`、`SaveAs`、`SetSheets` |
| 54 | `setup_current_sheet` | 2042 | `GetCurrentSheet`、`GetName`、`SetupSheet6` |
| 55 | `validate_generic_drawing_generation` | 2094 | —（纯字典校验，不碰 COM） |
| 56 | `generate_drawing_from_spec` | 2169 | —（纯编排：全部经由本地 helper 转调） |
| 57 | `insert_table_annotation` | 2306 | `InsertTableAnnotation`、`InsertTableAnnotation2` |
| 58 | `read_table_text` | 2351 | `Text` |
| 59 | `get_table_shape` | 2358 | `AnchorType`、`Anchored`、`ColumnCount`、`RowCount` |
| 60 | `set_table_row_hidden` | 2370 | `RowHidden` |
| 61 | `set_table_column_hidden` | 2377 | `ColumnHidden` |
| 62 | `delete_table_row` | 2384 | `DeleteRow` |
| 63 | `delete_table_column` | 2390 | `DeleteColumn` |
| 64 | `get_general_table` | 2418 | `GeneralTable` |
| 65 | `get_hole_table` | 2425 | `HoleTable` |
| 66 | `get_bend_table` | 2432 | `BendTable` |
| 67 | `get_weldment_cutlist_table` | 2439 | `WeldmentCutListFeature` |
| 68 | `get_revision_table_feature` | 2446 | `RevisionTableFeature` |
| 69 | `get_table_custom_property_column` | 2453 | `GetColumnCustomProperty` |
| 70 | `set_table_custom_property_column` | 2460 | `SetColumnCustomProperty` |
| 71 | `sort_table` | 2468 | `Sort` |
| 72 | `add_revision` | 2489 | `AddRevision` |
| 73 | `delete_revision` | 2496 | `DeleteRevision` |
| 74 | `get_current_revision` | 2503 | `CurrentRevision` |
| 75 | `get_section_view_data` | 2533 | `GetDefinition` |
| 76 | `set_section_style` | 2540 | `FirstColor`、`FirstOffset`、`GraphicsOnlySection`、`KeepCapColor`、`SecondColor`、`SecondOffset`、`SectionedZones`、`ShowSectionCap`、`ThirdColor`、`ThirdOffset`、`TransparencyValue`、`TransparentSection`、`ZonalSection` |
| 77 | `activate_annotation_view` | 2648 | `Activate`◇、`ActivateAndReorient`◇（成员名由 `reorient` 分支决定） |
| 78 | `get_annotation_view_evidence` | 2656 | `Always2D`、`AngleMadeWithViewHorizontal`、`AnnotationCount`、`FlatPatternView`、`IsShown`、`UnassignedView` |
| 79 | `get_model_view_manager` | 2710 | `GetModelViewManager` |
| 80 | `create_section_view_data` | 2718 | `CreateSectionViewData` |
| 81 | `create_feature_manager_section_view` | 2729 | `CreateSectionView` |
| 82 | `get_feature_manager_section_data` | 2737 | `GetSectionViewData` |
| 83 | `remove_feature_manager_section_view` | 2743 | `RemoveSectionView` |

**图例**：`※` = 属性读写（无括号）；`◇` = 成员名是变量/循环表动态派发。

---

## 三、统计

> **函数总数 83 / 其中调用了至少一个官方成员的数量 67**（另有 16 个函数未调用任何官方成员，见下）
> 附带：**全文去重后的官方成员名共 143 个。**

**未调用官方成员的 16 个**（按行号）：
`_safe_member`(102，转发器) · `_as_sequence`(113) · `_normalise_box`(122) · `_finite_positive`(275) · `line_units`(348，嵌套) · `select_drawing_template`(406) · `plan_standard_view_layout`(453) · `view_record`(548，嵌套) · `_scale_ratio`(590) · `_normalise_orientation`(631) · `_note_evidence`(1228) · `add_a3_sheet`(1426) · `_paper_size_from_template`(1536) · `_professional_annotation_record`(1621) · `validate_generic_drawing_generation`(2094) · `generate_drawing_from_spec`(2169)

---

## 四、按 DISPID 晚期绑定的成员（代码里**没有**名字，故未并入上面的去重名单）

这 4 处用 `_oleobj_.InvokeTypes(dispid, …)` 绕过 pywin32 的动态代理，成员名只存在于注释里：

| 函数 | 行号 | `InvokeTypes` 的 DISPID | 代码注释标注的成员 |
|---|---|---|---|
| `_note_text` | 1161 | 2 | `INote.GetText` |
| `_note_annotation` | 1178 | 85 | `INote.GetAnnotation` |
| `_set_annotation_position` | 1196 | 91 | `IAnnotation.SetPosition2` |
| `_note_box` | 1222 | 22 | `INote.GetExtent` |

⇒ 4 个名字（`GetText` / `GetAnnotation` / `SetPosition2` / `GetExtent`）在上表里**已通过同名通道出现**，
所以把它们并入第三节的 143 不会重复计数；本节单列只为标明**这 4 处静态审计/正则工具看不见**（来源块里已记录该现象为第 3、4 种形态）。

---

## 五、读码时顺带发现的两条（只记录，未改动）

1. **`Any` 未导入** —— L2358 `get_table_shape(table) -> dict[str, Any]` 与 L2656 `get_annotation_view_evidence(...) -> dict[str, Any]` 用了 `typing.Any`，但文件顶部只 `import math / re / fractions.Fraction / pathlib.Path`，**没有 `from typing import Any`，也没有 `from __future__ import annotations`**。
   - 本机 Python **3.14.7** 下 PEP 649 让注解默认延迟求值 ⇒ **不会报错**。
   - ⚠ 同一文件在 **≤3.13** 上 import 即 `NameError`。属于跨解释器版本的可移植性隐患，不是当前环境的功能缺陷。

2. **`_safe_member` 是全文件的唯一收敛通道** —— 83 个函数里 67 个直接命中官方成员，其余间接命中的几乎全部经由 `_safe_member`（L102）转发。
   ⇒ **任何以正则匹配 `get_com_member(...)` 为准的覆盖率统计，都会在 `_safe_member` 这一行产生系统性低估**；本表用的是「按函数体逐个归因」，未受影响。

---

### 复核方法（可重跑，不碰 SolidWorks）

```powershell
python -c "import ast,sys; t=ast.parse(open(r'D:\AI\SW\subskills\solidworks-engineering-drawing\scripts\drawing_workflow.py',encoding='utf-8').read()); fs=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef)]; print(len(fs))"   # → 83
```

行号用 `ripgrep` 的 `^\s*def \w+` 独立复核过一遍，与 `ast` 完全一致（最大行号 2743）。
