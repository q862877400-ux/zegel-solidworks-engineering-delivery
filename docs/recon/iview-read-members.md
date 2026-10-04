# IView 零参可读成员全表

> **来源**：官方源 `C:\swapi\types\IView\*.md`。本表由脚本**逐个真读**该目录下每个成员 `.md` 的全文后抽取（不是按文件名猜的）：
> 共读到 **462** 个 `.md`，其中 `_overview.md` 是接口总览页、不算成员，故成员文件 **461** 个 ——
> 与 `_overview.md` 页头声明的 `property_count: 34` + `method_count: 427` = 461 完全对上。
>
> **判据（全部按下面三条字面规则，不做推测）**：
> 1. **废弃**：页头（`**Signature**` 那一行**之前**）出现行首 `Obsolete.`。
> 2. **指针**：该页 `## Returns` 段内出现 `in-process, unmanaged C++`。
> 3. **零参**：签名括号内为空 ⇒ `是（空括号）`；签名**根本没有括号** ⇒ `是（无括号）`；括号内非空 ⇒ `否（有形参）`；无签名行 ⇒ `查不到`。
>
> ⚠ **本文件不含任何行号** —— 行号会漂。结论一律带可 `grep` 的原文片段。单元格超长（> 400 字符）截断并以 ` …` 标记。

## 一、统计

| 指标 | 数 |
|---|---|
| 共成员数 **N** | **461** |
| 非废弃且非指针 **M** | **267** |
| 其中零参 **K** | **200** |
| —— 其中「空括号 `Name()`」 | 169 |
| —— 其中「无括号（属性形态）」 | 31 |
| 废弃（页头 `Obsolete.`） | 149 |
| 指针（`in-process, unmanaged C++`） | 45 |
| 同时废弃且指针 | 0 |
| 按页头 `kind:` 统计 property | 34 |
| 按页头 `kind:` 统计 method | 427 |
| 签名行缺失（判为「查不到」） | 1 |
| 无 `## Returns` 段 | 133 |
| 无 `## Remarks` 段 | 232 |
| 指针标记落在 `## Parameters` 段、因而**不**计入上一行 | 1 |

交叉验算：149 + 45 - 0 + 267 = 461（应等于 N = 461）。

## 二、主表 —— 非废弃且非指针的 267 个成员

| 成员名 | 零参? | 签名 | Returns | Remarks 首句 |
|---|---|---|---|---|
| AlignDrawingView | 否（有形参） | `System.bool AlignDrawingView( System.int AlignViewType )` | True if auxiliary drawing view alignment is set, false if not | 查不到 |
| AlignWithView | 否（有形参） | `System.bool AlignWithView( System.int AlignType, View BaseView )` | True if view alignment is set, false if not | AlignType tells how to align this view. |
| Angle | 是（无括号） | `System.double Angle {get; set;}` | Rotation angle in radians of the view | 查不到 |
| AutoInsertCenterMarks2 | 否（有形参） | `System.bool AutoInsertCenterMarks2( System.int InsertType, System.int InsertOption, System.bool LinearSlotCenter, System.bool ArcSlotCenter, System.bool UseDocumentDefaults, System.double Size, System.double Gap, System.bool ExtendedLines, System.bool CenterLineFont, System.double Angle )` | True if successful, false if not | Call this method on each active view in which you want to insert center marks. |
| Bodies | 是（无括号） | `System.object Bodies {get; set;}` | [[Bodies]] of a multibody part | 查不到 |
| BreakLineGap | 是（无括号） | `System.double BreakLineGap {get; set;}` | Value for gap | 查不到 |
| Crop2 | 否（有形参） | `System.int Crop2( System.bool JaggedOutline, System.bool NoOutline, System.int ShapeIntensity )` | Crop view status as defined in [[swCropViewErrors_e]] | 查不到 |
| CropViewJaggedOutline | 是（无括号） | `System.bool CropViewJaggedOutline {get; set;}` | True to use a jagged outline, false to not (see **Remarks**) | Call [[IView::IsCropped]] to find out if this drawing view is cropped. |
| CropViewJaggedShapeIntensity | 是（无括号） | `System.int CropViewJaggedShapeIntensity {get; set;}` | Shape intensity of the jagged outline; valid range is 1 (most) to 5 (least) (see **Remarks**) | Call [[IView::IsCropped]] to find out if this drawing view is cropped. |
| CropViewNoOutline | 是（无括号） | `System.bool CropViewNoOutline {get; set;}` | True to not show an outline, false to show an outline | Call [[IView::IsCropped]] to find out if this drawing view is cropped. |
| DisableAutoUpdate | 是（无括号） | `System.bool DisableAutoUpdate {get; set;}` | True to disable the automatic update, false to not | 查不到 |
| DisplayState | 是（无括号） | `System.string DisplayState {get; set;}` | Name of the display state | 查不到 |
| EmphasizeOutline | 是（无括号） | `System.bool EmphasizeOutline {get; set;}` | True if the outlines of section views are outlined, false if not | 查不到 |
| EnumHiddenComponents2 | 是（空括号） | `EnumComponents2 EnumHiddenComponents2()` | [[Hidden component enumeration]] | 查不到 |
| EnumSectionLines2 | 否（有形参） | `EnumDrSections EnumSectionLines2( System.bool IgnoreSuppressed )` | [[Section lines enumeration]] | This method returns section lines whether the view is visible or not. |
| FlipView | 是（无括号） | `System.bool FlipView {get; set;}` | True to flip the flat-pattern view, false to not | 查不到 |
| FocusLocked | 是（无括号） | `System.bool FocusLocked {get; set;}` | True if focus is locked on the view, false if not | 查不到 |
| GetAlignment | 是（空括号） | `System.int GetAlignment()` | Alignment information as defined in [[swViewAlignment_e]] | The alignment information returned indicates if: |
| GetAnnotationCount | 是（空括号） | `System.int GetAnnotationCount()` | Number of annotations | Call this method before [[IView::GetAnnotations]] to determine the size of the array for that method. |
| GetAnnotations | 是（空括号） | `System.object GetAnnotations()` | Array of [[annotations]] | 查不到 |
| GetAnnotationsByType | 否（有形参） | `System.object GetAnnotationsByType( System.int Type )` | Array of [[annotations]] | 查不到 |
| GetArcCount | 是（空括号） | `System.int GetArcCount()` | Number of arcs | Call this method before [[IView::GetArcs4]] to determine the size of the array for that method. |
| GetArcs4 | 是（空括号） | `System.object GetArcs4()` | Array of doubles (see **Remarks**) | This method only returns arcs that were sketched by a user in a drawing view. |
| GetBaseView | 是（空括号） | `System.object GetBaseView()` | Base [[view]] | 查不到 |
| GetBendLineCount | 是（空括号） | `System.int GetBendLineCount()` | Number of bendlines in a flat-pattern drawing view | 查不到 |
| GetBendLines | 是（空括号） | `System.object GetBendLines()` | Array of [[bendlines]] in the flat-pattern drawing view | 查不到 |
| GetBendNoteAttributeString | 否（有形参） | `System.string GetBendNoteAttributeString( System.int Attribute )` | String that is used to format the bend note attribute | Call this method to specify the Format parameter of [[IView::SetBendNoteTextFormat]]. |
| GetBendNoteTextFormat | 是（空括号） | `System.string GetBendNoteTextFormat()` | Format of all bend notes in this drawing view | 查不到 |
| GetBodiesCount | 是（空括号） | `System.int GetBodiesCount()` | Number of bodies of a multibody part in the view | 查不到 |
| GetBomTable | 是（空括号） | `System.object GetBomTable()` | [[BOM table]] | This method only returns a BOM table if there is a Microsoft Excel-based BOM for the drawing view. |
| GetBreakLineCount2 | 否（有形参） | `System.int GetBreakLineCount2( out System.int Size )` | Number of breaks | A drawing view can have break lines without the break being applied. |
| GetBreakLineInfo2 | 是（空括号） | `System.object GetBreakLineInfo2()` | Array of data for all break lines in the view (see **Remarks**) | The return value is a one-dimensional array consisting of the following data: |
| GetBreakLines | 是（空括号） | `System.object GetBreakLines()` | [[Breaks]] in this view | This method gets all of the breaks in the view, regardless if the view is broken. |
| GetBreakOutSectionCount | 是（空括号） | `System.int GetBreakOutSectionCount()` | Number of broken-out sections | Call this method before calling [[IView::IGetBreakOutSections]] to determine the size of the array for that method. |
| GetBreakOutSections | 是（空括号） | `System.object GetBreakOutSections()` | Array of broken-out section [[features]] | 查不到 |
| GetCenterLineCount | 是（空括号） | `System.int GetCenterLineCount()` | Number of centerlines | Call this method before calling [[IView::IGetCenterLines]] to determine the size of the array for that method. |
| GetCenterLines | 是（空括号） | `System.object GetCenterLines()` | Array of [[centerlines]] | Use this method to obtain the array of centerlines all at once instead of calling [[IView::GetFirstCenterLine]] and then repeatedly calling [[ICenterLine::GetNext]] to obtain the remaining centerlines in the drawing view. |
| GetCenterLineSketch | 是（空括号） | `Sketch GetCenterLineSketch()` | [[Sketch]] | All of the centerlines for a drawing view are stored on a sketch. |
| GetCenterMarkCount2 | 否（有形参） | `System.int GetCenterMarkCount2( out System.int Size )` | Number of center marks in the view | Center marks are now annotations. |
| GetCenterMarkInfo | 是（空括号） | `System.object GetCenterMarkInfo()` | Array of doubles (see **Remarks**) | Center marks are now annotations. |
| GetCenterMarks | 是（空括号） | `System.object GetCenterMarks()` | [[Centermarks]] that are features in this view | Center marks are now annotations. |
| GetCorresponding | 否（有形参） | `System.object GetCorresponding( System.object InputObject )` | Pointer to the corresponding object in this drawing view; null or Nothing if none found | InputObject can be any object assigned a persistent reference or object ID; for example, [[IAnnotation]], [[IFeature]], [[ISketch]], [[ISketchSegment]], etc. |
| GetCorrespondingEntity | 否（有形参） | `System.object GetCorrespondingEntity( System.object Entity )` | Corresponding [[entity]] in this drawing view; null or Nothing if none found | Use [[IModelDocExtension::GetCorrespondingEntity2]] to get the part entity that corresponds to a drawing view entity. |
| GetCThreadCount | 是（空括号） | `System.int GetCThreadCount()` | Number of cosmetic threads | Call this method before calling [[IView::IGetCThreads]] to determine the size of the array for that method. |
| GetCThreadQuality | 是（空括号） | `System.bool GetCThreadQuality()` | True if precision quality, false if draft quality | 查不到 |
| GetCThreads | 是（空括号） | `System.object GetCThreads()` | Array of [[cosmetic threads]] | Use this method to obtain the array of cosmetic threads all at once instead of calling [[IView::GetFirstCThread]] and then repeatedly calling [[ICThread::GetNext]] to obtain the remaining cosmetic threads on the drawing view. |
| GetDatumOriginCount | 是（空括号） | `System.int GetDatumOriginCount()` | Number of datum origins | Call this method before calling [[IView::IGetDatumOrigins]] to determine the size of the array for that method. |
| GetDatumOrigins | 是（空括号） | `System.object GetDatumOrigins()` | Array of [[datum origins]] | Use this method to obtain the array of datum origins all at once instead of calling [[IView::GetFirstDatumOrigin]] and then repeatedly calling [[IDatumOrigin::GetNext]] to obtain the remaining datum origins on this drawing view. |
| GetDatumPoints2 | 是（空括号） | `System.object GetDatumPoints2()` | Array of doubles (see **Remarks**) | Return value is an array of doubles with the format: |
| GetDatumPointsCount | 是（空括号） | `System.int GetDatumPointsCount()` | Number of datum points | 查不到 |
| GetDatumTagCount | 是（空括号） | `System.int GetDatumTagCount()` | Number of datum tags | Call this method before calling [[IView::IGetDatumTags]] to determine the size of the array for that method. |
| GetDatumTags | 是（空括号） | `System.object GetDatumTags()` | Array of [[datum tags]] | Use this method to obtain the array of datum tags all at once instead of calling [[IView::GetFirstDatumTag]] and then repeatedly calling [[IDatumTag::GetNext]] to obtain the remaining datum tags on this drawing view. |
| GetDatumTargetSymCount | 是（空括号） | `System.int GetDatumTargetSymCount()` | Number of datum target symbols | Call this method before calling [[IView::IGetDatumTargetSyms]] to determine the size of the array for that method. |
| GetDatumTargetSyms | 是（空括号） | `System.object GetDatumTargetSyms()` | Array of [[datum target symbols]] | Use this method to obtain the array of datum target symbols all at once instead of calling [[IView::GetFirstDatumTargetSym]] and then repeatedly calling [[IDatumTargetSym::GetNext]] to obtain the remaining datum target symbols on this drawing view. |
| GetDependentViewCount | 否（有形参） | `System.int GetDependentViewCount( System.bool AllViews, System.int SpecificViewType )` | Number of dependent views | Call this method before calling [[IView::IGetDependentViews]] to get the size of the array for that method. |
| GetDependentViews | 否（有形参） | `System.object GetDependentViews( System.bool AllViews, System.int SpecificViewType )` | Array of dependent [[views]] | 查不到 |
| GetDesignTableExtent | 是（空括号） | `System.object GetDesignTableExtent()` | Array of 6 doubles; the lower left (x,y,z) and upper right (x,y,z) values indicating the design table extents; values are in meters and refer to drawing view space | 查不到 |
| GetDetail | 是（空括号） | `System.object GetDetail()` | [[Detail circle]] | 查不到 |
| GetDetailCircleCount2 | 否（有形参） | `System.int GetDetailCircleCount2( out System.int Size )` | Number of detail circles in the drawing view | Call this method before calling [[IView::GetDetailCircles]] to get the size of the array for that method. |
| GetDetailCircleInfo2 | 是（空括号） | `System.object GetDetailCircleInfo2()` | Array of doubles (see **Remarks**) | The return value is the following array of doubles: |
| GetDetailCircles | 是（空括号） | `System.object GetDetailCircles()` | [[Detail circles]] | 查不到 |
| GetDetailCircleStrings | 是（空括号） | `System.object GetDetailCircleStrings()` | Array of strings with one string for each detail circle in the view | 查不到 |
| GetDimensionCount4 | 是（空括号） | `System.int GetDimensionCount4()` | Number of dimensions | 查不到 |
| GetDimensionDisplayInfo5 | 是（空括号） | `System.object GetDimensionDisplayInfo5()` | Array of doubles (see **Remarks**) | The data returned is an array of doubles as follows: |
| GetDimensionDisplayInfoSize2 | 是（空括号） | `System.int GetDimensionDisplayInfoSize2()` | Number of dimension lines | Call this method before calling [[IView::IGetDimensionDisplayInfo5]] to get the size of the array for that method. |
| GetDimensionDisplayString5 | 否（有形参） | `System.object GetDimensionDisplayString5( out System.int DimensionSize )` | Array of strings (see **Remarks**) | This method returns a string array of size (*DimensionSize*) x (*number_of_dimensions_in_view*). |
| GetDimensionIds4 | 是（空括号） | `System.object GetDimensionIds4()` | Array of strings; each string represents one dimension name from the current drawing sheet or current drawing view | The order of the dimension names returned align with the order of information returned from [[IView::GetDimensionInfo6]] or [[IView::IGetDimensionInfo6]]. |
| GetDimensionInfo7 | 是（空括号） | `System.object GetDimensionInfo7()` | Array of doubles (see **Remarks**) | The data returned is an array of doubles as follows: |
| GetDimensionString4 | 是（空括号） | `System.object GetDimensionString4()` | Array of strings containing the text associated with each dimension | Use [[IView::GetDimensionCount4]] to determine the number of strings to be returned. |
| GetDisplayData4 | 是（空括号） | `System.object GetDisplayData4()` | [[IDisplayData]] | 查不到 |
| GetDisplayDimensionCount | 是（空括号） | `System.int GetDisplayDimensionCount()` | Number of display dimensions | Call this method before calling [[IView::IGetDisplayDimensions]] to determine the size of the array for that method. |
| GetDisplayDimensions | 是（空括号） | `System.object GetDisplayDimensions()` | Array of [[display dimensions]] | Use this method to obtain the array of display dimensions all at once instead of calling [[IView::GetFirstDisplayDimension5]] and then repeatedly calling [[IDisplayDimension::GetNext5]] to obtain the remaining display dimensions on this drawing view. |
| GetDisplayEdgesInShadedMode | 是（空括号） | `System.bool GetDisplayEdgesInShadedMode()` | True if the edges are displayed when the view is in shaded mode, false if not | **To...** |
| GetDisplayMode2 | 是（空括号） | `System.int GetDisplayMode2()` | Current display mode of the drawing view as defined in [[swDisplayMode_e]] | 查不到 |
| GetDisplayTangentEdges2 | 是（空括号） | `System.int GetDisplayTangentEdges2()` | Tangent edge display mode as defined in [[swDisplayTangentEdges_e]] | 查不到 |
| GetDowelSymbolCount | 是（空括号） | `System.int GetDowelSymbolCount()` | Number of dowel symbols | Call this method before calling [[IView::IGetDowelSymbols]] to determine the size of the array for that method. |
| GetDowelSymbols | 是（空括号） | `System.object GetDowelSymbols()` | Array of [[dowel symbols]] | Use this method to obtain the array of dowel symbols all at once instead of calling [[IView::GetFirstDowelSymbol]] and then repeatedly calling [[IDowelSymbol::GetNext]] to obtain the remaining dowel symbols on this drawing view. |
| GetEllipseCount | 是（空括号） | `System.int GetEllipseCount()` | Number of ellipses in the view | Call this method before calling [[IView::IGetEllipses5]] to get the size of the array for that method. |
| GetEllipses5 | 是（空括号） | `System.object GetEllipses5()` | Array of doubles (**Remarks**) | This method only returns ellipses that were sketched by a user in this drawing view. |
| GetFaceHatchCount | 是（空括号） | `System.int GetFaceHatchCount()` | Number of faces hatches in the view | Call this method before calling [[IView::IGetFaceHatches]] to get the size of the array for that method. |
| GetFaceHatches | 是（空括号） | `System.object GetFaceHatches()` | [[Face hatches]] in the view | To get the number of solid hatches in a detail, broken, or crop view, use [[IView::GetSolidHatchCount]]. |
| GetFacettedHlrDisplay | 是（空括号） | `System.bool GetFacettedHlrDisplay()` | True if the edges should be displayed faceted, false if not | 查不到 |
| GetFirstAnnotation3 | 是（空括号） | `Annotation GetFirstAnnotation3()` | First [[annotation]] in the drawing view | This method gets any display dimension, including suppressed, hidden, or dangling dimensions on the sheet and on the sheet format if it is visible. |
| GetFirstCenterLine | 是（空括号） | `Centerline GetFirstCenterLine()` | First [[centerline]] | 查不到 |
| GetFirstCenterMark2 | 是（空括号） | `System.object GetFirstCenterMark2()` | First [[center mark]] | This method obsoletes IView::GetFirstCenterMark by supporting inactive sheets. |
| GetFirstCenterOfMass | 是（空括号） | `System.object GetFirstCenterOfMass()` | [[ICenterOfMass]] | 查不到 |
| GetFirstCThread | 是（空括号） | `System.object GetFirstCThread()` | First [[cosmetic thread]] | 查不到 |
| GetFirstDatumOrigin | 是（空括号） | `DatumOrigin GetFirstDatumOrigin()` | First [[datum origin]] | 查不到 |
| GetFirstDatumTag | 是（空括号） | `System.object GetFirstDatumTag()` | First [[datum tag]] | 查不到 |
| GetFirstDatumTargetSym | 是（空括号） | `System.object GetFirstDatumTargetSym()` | First [[datum target symbol]] | 查不到 |
| GetFirstDisplayDimension6 | 是（空括号） | `System.object GetFirstDisplayDimension6()` | 查不到 | This method obsoletes IView::GetFirstDisplayDimension5 by supporting inactive sheets. |
| GetFirstDowelSymbol | 是（空括号） | `System.object GetFirstDowelSymbol()` | First [[dowel symbol]] | 查不到 |
| GetFirstGTOL | 是（空括号） | `System.object GetFirstGTOL()` | First [[GTol]] | 查不到 |
| GetFirstMultiJogLeader2 | 是（空括号） | `System.object GetFirstMultiJogLeader2()` | 查不到 | This method obsoletes IView::GetFirstMultiJogLeader by supporting inactive sheets. |
| GetFirstNote2 | 是（空括号） | `System.object GetFirstNote2()` | First [[note]] | This method obsoletes IView::GetFirstNote by supporting inactive sheets. |
| GetFirstRevisionCloud2 | 是（空括号） | `System.object GetFirstRevisionCloud2()` | [[IRevisionCloud]] | This method obsoletes IView::GetFirstRevisionCloud by supporting inactive sheets. |
| GetFirstSFSymbol | 是（空括号） | `System.object GetFirstSFSymbol()` | First [[surface-finish symbol]] | 查不到 |
| GetFirstTableAnnotation2 | 是（空括号） | `System.object GetFirstTableAnnotation2()` | First [[table annotation]] | This method obsoletes IView::GetFirstTableAnnotation by supporting inactive sheets. |
| GetFirstWeldBead | 是（空括号） | `WeldBead GetFirstWeldBead()` | First [[weld bead]] | 查不到 |
| GetFirstWeldSymbol | 是（空括号） | `System.object GetFirstWeldSymbol()` | First [[weld symbol]] | 查不到 |
| GetGTolCount | 是（空括号） | `System.int GetGTolCount()` | Number of geometric tolerances | Call this method before calling [[IView::IGetGTols]] to determine the size of the array for that method. |
| GetGTols | 是（空括号） | `System.object GetGTols()` | Array of [[geometric tolerances]] | Use this method to obtain the array of geometric tolerances all at once instead of calling [[IView::GetFirstGTOL]] and then repeatedly calling [[IGtol::GetNextGTOL]] to obtain the remaining geometric tolerances in the drawing view. |
| GetHiddenComponents | 是（空括号） | `System.object GetHiddenComponents()` | Array of hidden components | 查不到 |
| GetKeepLinkedToBOM | 是（空括号） | `System.bool GetKeepLinkedToBOM()` | True if this drawing view is linked to a BOM or weldment cut-list table, false if not | 查不到 |
| GetKeepLinkedToBOMName | 是（空括号） | `System.string GetKeepLinkedToBOMName()` | Name of BOM or weldment cut-list table feature | 查不到 |
| GetLineCount2 | 否（有形参） | `System.int GetLineCount2( System.short CrossHatchOption )` | Number of lines | Call this method before calling [[IView::IGetLines4]] to get the size of the array for that method. |
| GetLines4 | 否（有形参） | `System.object GetLines4( System.short CrossHatchOption )` | Array of doubles (see **Remarks**) | This method only returns lines that were sketched in this drawing view. |
| GetMirrorViewOrientation | 否（有形参） | `System.bool GetMirrorViewOrientation( out System.bool BIsMirrorView, out System.int LMirrorViewOrientation )` | True if the method executed successfully, false if not | 查不到 |
| GetMultiJogLeaderCount | 是（空括号） | `System.int GetMultiJogLeaderCount()` | Total number of multi-jog leaders on this drawing view | Call this method before calling [[IView::IGetMultiJogLeaders]] to determine the size of the array for that method. |
| GetMultiJogLeaders | 是（空括号） | `System.object GetMultiJogLeaders()` | Array of [[multi-jog leaders]] | Use this method to obtain the array of multi-jog leaders all at once instead of calling [[IView::GetFirstMultiJogLeader]] and then repeatedly calling [[IMultiJogLeader::GetNext]] to obtain the remaining multi-jog leaders in the drawing view. |
| GetName2 | 是（空括号） | `System.string GetName2()` | Name of the drawing view | This method does not return unique names for section views. |
| GetNextView | 是（空括号） | `System.object GetNextView()` | Next [[view]] | 查不到 |
| GetNoteCount | 是（空括号） | `System.int GetNoteCount()` | Number of notes in this drawing view | Call this method before calling [[IView::IGetNotes]] to determine the size of the array for that method. |
| GetNotes | 是（空括号） | `System.object GetNotes()` | Array of [[notes]] | Use this method to obtain the array of notes all at once instead of calling [[IView::GetFirstNote]] and then repeatedly calling [[INote::GetNext]] to obtain the remaining notes on this drawing view. |
| GetOrientationName | 是（空括号） | `System.string GetOrientationName()` | Predefined name of view or an empty string for unnamed views | This method returns the orientation (predefined) name of the view; e.g., *Front, *Top, *Isometric, or a user-defined view name defined in the model. |
| GetOutline | 是（空括号） | `System.object GetOutline()` | Array of doubles (see **Remarks**) | The return value is an array of 4 doubles with the following format: |
| GetParabolaCount | 是（空括号） | `System.int GetParabolaCount()` | Number of parabolas in the view | 查不到 |
| GetParabolas2 | 是（空括号） | `System.object GetParabolas2()` | Array of doubles (see **Remarks**) | The return values are in an array of doubles: |
| GetPolyLineCount5 | 否（有形参） | `System.int GetPolyLineCount5( System.short CrossHatchOption, out System.int PointCount )` | Number of polylines | Call this method before calling [[IView::IGetPolylines6.]] |
| GetPolylines7 | 否（有形参） | `System.object GetPolylines7( System.short CrossHatchOption, out System.object Polylines )` | Array of modeling [[edges]] and [[silhouette edges]] corresponding to polylines in the view | The difference between this method and [[IView::GetPolyLinesAndCurves]] and [[IView::IGetPolyLinesAndCurves]] is that splines and ellipses returned by these methods are returned as equation parameters, which are more precise definitions. |
| GetPolyLinesAndCurves | 否（有形参） | `System.object GetPolyLinesAndCurves( System.short CrossHatchOption )` | Array of lines and parameters in the view (see **Remarks**) | The difference between this method and [[IView::GetPolylines7]] is that splines and ellipses returned by this method are returned as equation parameters, which are more precise definitions. |
| GetPolyLinesAndCurvesCount | 否（有形参） | `System.int GetPolyLinesAndCurvesCount( System.short CrossHatchOption, out System.int PointCount )` | Number of lines | Call this method before calling [[IView::IGetPolyLinesAndCurves]]. |
| GetProjectionArrow | 是（空括号） | `System.object GetProjectionArrow()` | [[Projection arrow]] | 查不到 |
| GetProjectionLineCount | 是（空括号） | `System.int GetProjectionLineCount()` | Number of projection lines in this drawing view | This method only works for base drawing views; it does not work for projected or auxiliary views. |
| GetProjectionLines | 是（空括号） | `System.object GetProjectionLines()` | Array of [[projection lines]] | This method only works for base drawing views; it does not work for projected or auxiliary views. |
| GetReferencedModelName | 是（空括号） | `System.string GetReferencedModelName()` | Name of the model in the drawing view | 查不到 |
| GetRelatedTangentEdgeCount | 否（有形参） | `System.int GetRelatedTangentEdgeCount( System.object BendLine )` | Array of visible tangent edges for the specified bendline | Hidden tangent edges are not returned by this method. |
| GetRelatedTangentEdges | 否（有形参） | `System.object GetRelatedTangentEdges( System.object BendLine )` | Array of visible tangent edges for the specified bendline | Hidden tangent edges are not returned by this method. |
| GetRevisionCloudCount | 是（空括号） | `System.int GetRevisionCloudCount()` | Number of revision cloud annotations in this view | 查不到 |
| GetRevisionClouds | 是（空括号） | `System.object GetRevisionClouds()` | Array of [[IRevisionCloud]]s | 查不到 |
| GetSection | 是（空括号） | `System.object GetSection()` | [[Section]] for this section view | 查不到 |
| GetSectionLineCount2 | 否（有形参） | `System.int GetSectionLineCount2( out System.int Size )` | Number of section lines in the view | 查不到 |
| GetSectionLineInfo2 | 是（空括号） | `System.object GetSectionLineInfo2()` | Array of doubles (see **Remarks**) | This method gets all of the information on section lines in the view. |
| GetSectionLines | 是（空括号） | `System.object GetSectionLines()` | Array of [[section lines]] | This method returns the section lines regardless if the view is visible. |
| GetSectionLineStrings | 是（空括号） | `System.object GetSectionLineStrings()` | Array of strings with one string for each section line in the view | To determine the number of the strings returned, call [[IView::GetSectionLineCount2]]. |
| GetSFSymbolCount | 是（空括号） | `System.int GetSFSymbolCount()` | Total number of surface finish symbols on this drawing view | Call this method before calling [[IView::IGetSFSymbols]] to determine the size of the array for that method. |
| GetSFSymbols | 是（空括号） | `System.object GetSFSymbols()` | Array of [[surface finish symbols]] | Use this method to obtain the array of surface finish symbols all at once instead of calling [[IView::GetFirstSFSymbol]] and then repeatedly calling [[ISFSymbol::GetNext]] to obtain the remaining surface finish symbols in the drawing view. |
| GetSketch | 是（空括号） | `System.object GetSketch()` | [[Sketch]] | Each drawing view contains an underlying sketch. |
| GetSketchPictureCount | 是（空括号） | `System.int GetSketchPictureCount()` | Number of sketch pictures in the view | Only sketch pictures orthogonal to this view are counted. |
| GetSketchPictures | 是（空括号） | `System.object GetSketchPictures()` | Array of [[ISketchPictures]] | Only sketch pictures orthogonal to this view are returned. |
| GetSMBoundaryBoxDisplayData2 | 是（空括号） | `System.object GetSMBoundaryBoxDisplayData2()` | [[Display data]] of boundary-box sketch of a flat-pattern drawing view | 查不到 |
| GetSolidHatchCount | 否（有形参） | `System.int GetSolidHatchCount( out System.int ArraySize )` | Size of the array for the solid-fill hatches boundary data | To get information about solid-fill hatches in drawing views, use [[IView::GetFaceHatchCount]], [[IView::GetFaceHatches]], and [[IView::IGetFaceHatches]]. |
| GetSolidHatchInfo | 是（空括号） | `System.object GetSolidHatchInfo()` | Array of doubles (see **Remarks**) | The return value, which is an array of doubles, describes the geometry for each boundary loop in each visible solid-fill hatch in a detail or broken view. |
| GetSplineCount | 否（有形参） | `System.int GetSplineCount( out System.int PointCount )` | Number of splines in the view | 查不到 |
| GetSplines3 | 是（空括号） | `System.object GetSplines3()` | Array of doubles (see **Remarks**) | This method only returns splines that were sketched by a user in this drawing view. |
| GetTableAnnotationCount | 是（空括号） | `System.int GetTableAnnotationCount()` | Total number of table annotations on this drawing view | Call this method before calling [[IView::IGetTableAnnotations]] to determine the size of the array for that method. |
| GetTableAnnotations | 是（空括号） | `System.object GetTableAnnotations()` | Array of [[table annotations]] | This method can be used to obtain the array of table annotations all at once instead of calling [[IView::GetFirstTableAnnotation]] and then repeatedly calling [[ITableAnnotation::GetNext]] to obtain the table annotations. |
| GetTemporaryAxes | 是（空括号） | `System.object GetTemporaryAxes()` | Array of double of the information about the temporary axes in this view (see **Remarks**) | This array contains the start and end points, in that order, of temporary axes. |
| GetTemporaryAxesCount | 是（空括号） | `System.int GetTemporaryAxesCount()` | Number of temporary axes in this view | Call this method before calling [[IView::IGetTemporaryAxes]] to get the size of the array for that method. |
| GetUniqueName | 是（空括号） | `System.string GetUniqueName()` | Name of this section view | Before selecting a specific section view using [[IModelDocExtension::SelectByID2]], call this method to get the unique name of the section view in "Drawing View*number*" format. |
| GetUseParentDisplayMode | 是（空括号） | `System.bool GetUseParentDisplayMode()` | True if view is using its parent settings, false if using its own local settings | 查不到 |
| GetUserPoints2 | 是（空括号） | `System.object GetUserPoints2()` | Array of doubles (see **Remarks**) | The return value is the following array of doubles: |
| GetUserPointsCount | 是（空括号） | `System.int GetUserPointsCount()` | Number of user points found in the view | 查不到 |
| GetViewXform | 是（空括号） | `System.object GetViewXform()` | Array of doubles (see **Remarks**) | The return value is formatted as the following array of 13 doubles: |
| GetVisible | 是（空括号） | `System.bool GetVisible()` | True if the view is be visible, false if not | 查不到 |
| GetVisibleComponentCount | 是（空括号） | `System.int GetVisibleComponentCount()` | Number of visible components | Visible components are components not completely obscured by other components in the view. |
| GetVisibleComponents | 是（空括号） | `System.object GetVisibleComponents()` | Visible [[components]] in this drawing view | Visible components are components not completely obscured by other components in the view. |
| GetVisibleDrawingComponents | 是（空括号） | `System.object GetVisibleDrawingComponents()` | Visible [[IDrawingComponent]]s in this drawing view | Visible components are components not completely obscured by other components in the view. |
| GetVisibleEntities2 | 否（有形参） | `System.object GetVisibleEntities2( Component2 LpViewComponent, System.int EntityType )` | Array of the visible entities of EntityType in LpViewComponent | Visible entities are entities that are not completely obscured by other entities in the view. |
| GetVisibleEntityCount2 | 否（有形参） | `System.int GetVisibleEntityCount2( Component2 LpViewComponent, System.int EntityType )` | Number of visible entities of EntityType in LpViewComponent | Visible entities are entities that are not completely obscured by other entities in the view. |
| GetWeldBeadCount | 是（空括号） | `System.int GetWeldBeadCount()` | Total number of weld beads on this drawing view | Call this method before calling [[IView::IGetWeldBeads]] to determine the size of the array for that method. |
| GetWeldBeads | 是（空括号） | `System.object GetWeldBeads()` | Array of [[weld beads]] | Use this method to obtain the array of weld beads all at once instead of calling [[IView::GetFirstWeldBead]] and then repeatedly calling [[IWeldBead::GetNext]] to obtain the weld beads. |
| GetWeldSymbolCount | 是（空括号） | `System.int GetWeldSymbolCount()` | Total number of weld symbols on this drawing view | Call this method before calling [[IView::IGetWeldSymbols]] to determine the size of the array for that method. |
| GetWeldSymbols | 是（空括号） | `System.object GetWeldSymbols()` | Array of [[weld symbols]] | This method can be used to obtain the array of annotations all at once instead of calling [[IView::GetFirstWeldSymbol]] and then repeatedly calling [[IWeldSymbol::GetNext]] to obtain the annotations. |
| GetWitnessEntitiesCount | 否（有形参） | `System.int GetWitnessEntitiesCount( out System.int Size )` | Number of virtual sharp witness lines in this drawing view | Call this method to get the sizes of the arrays returned by [[IView::GetWitnessGeomInfo]] and [[IView::IGetWitnessGeomInfo]]. |
| GetWitnessGeomInfo | 是（空括号） | `System.object GetWitnessGeomInfo()` | Array of doubles (see **Remarks**) | This method returns an array containing the following data for each virtual sharp in the view: |
| GetXform | 是（空括号） | `System.object GetXform()` | Array of 3 doubles that describe the location and scale of the drawing view (see **Remarks**) | The first two values returned are the X and Y locations of the view relative to the sheet origin, and the third value returned is the scale of the drawing view. |
| HasDesignTable | 是（空括号） | `System.bool HasDesignTable()` | True if this drawing view has a design table, false if not | 查不到 |
| HiddenEdges | 是（无括号） | `System.object HiddenEdges {get; set;}` | Array of hidden [[edges]] | 查不到 |
| IGetBaseView | 是（空括号） | `View IGetBaseView()` | Base [[view]] | 查不到 |
| IGetBomTable | 是（空括号） | `BomTable IGetBomTable()` | [[BOM table]] | This method only returns a BOM table if there is a Microsoft Excel-based BOM for the drawing view. |
| IGetCenterMarkInfo | 是（空括号） | `System.double IGetCenterMarkInfo()` | Array of doubles (see **Remarks**) | Center marks are now annotations. |
| IGetDependentViews | 否（有形参） | `View IGetDependentViews( System.bool AllViews, System.int SpecificViewType, System.int DependentViewCount )` | Array of dependent [[views]] | Call [[IView::GetDependentViewCount]] before calling this method to get the value of DependentViewCount. |
| IGetDesignTableExtent | 是（空括号） | `System.double IGetDesignTableExtent()` | Array of 6 doubles; the lower left (x,y,z) and upper right (x,y,z) values indicating the design table extents; values are in meters and refer to drawing view space | 查不到 |
| IGetDetail | 是（空括号） | `DetailCircle IGetDetail()` | [[Detail circle]] | 查不到 |
| IGetDetailCircleInfo2 | 否（有形参） | `System.double IGetDetailCircleInfo2( System.int ArraySize )` | Array of doubles (see **Remarks**) | The return value is the following array of doubles: |
| IGetDimensionDisplayInfo5 | 否（有形参） | `System.double IGetDimensionDisplayInfo5( System.int ArraySize )` | Array of doubles (see **Remarks**) | Before calling this method, call [[IView::GetDimensionDisplayInfoSize2]] to get the value for ArraySize. |
| IGetDimensionDisplayString4 | 是（空括号） | `System.string IGetDimensionDisplayString4()` | Array of strings containing the dimension text (see **Remarks**) | For each dimension in the drawing sheet or drawing view, this method returns 10 strings. |
| IGetDimensionString4 | 是（空括号） | `System.string IGetDimensionString4()` | Array of strings containing the text associated with each dimension | Use [[IView::GetDimensionCount4]] to determine the number of strings to be returned. |
| IGetDisplayData3 | 是（空括号） | `DisplayData IGetDisplayData3()` | [[IDisplayData]] object | The data kept with the [[IDisplayData]] object is strictly for display purposes and allows you to recreate unintelligent geometry. |
| IGetFirstCThread | 是（空括号） | `CThread IGetFirstCThread()` | First [[cosmetic thread]] | 查不到 |
| IGetFirstDatumTag | 是（空括号） | `DatumTag IGetFirstDatumTag()` | First [[datum tag]] | 查不到 |
| IGetFirstDatumTargetSym | 是（空括号） | `DatumTargetSym IGetFirstDatumTargetSym()` | First [[datum target symbol]] | 查不到 |
| IGetFirstDowelSymbol | 是（空括号） | `DowelSymbol IGetFirstDowelSymbol()` | First [[dowel symbol]] | 查不到 |
| IGetFirstGTOL | 是（空括号） | `Gtol IGetFirstGTOL()` | First [[GTol]] | 查不到 |
| IGetFirstMultiJogLeader | 是（空括号） | `MultiJogLeader IGetFirstMultiJogLeader()` | First [[multi-jog leader]] | 查不到 |
| IGetFirstNote | 是（空括号） | `Note IGetFirstNote()` | First [[note]] | The sheet must be visible. |
| IGetFirstSFSymbol | 是（空括号） | `SFSymbol IGetFirstSFSymbol()` | First [[surface-finish symbol]] | 查不到 |
| IGetFirstWeldSymbol | 是（空括号） | `WeldSymbol IGetFirstWeldSymbol()` | First [[weld symbol]] | 查不到 |
| IGetNextView | 是（空括号） | `View IGetNextView()` | Next [[view]] | 查不到 |
| IGetOutline | 是（空括号） | `System.double IGetOutline()` | Array of doubles (see **Remarks**) | The return value is an array of 4 doubles with the following format: |
| IGetProjectionArrow | 是（空括号） | `ProjectionArrow IGetProjectionArrow()` | [[Projection arrow]] | 查不到 |
| IGetSection | 是（空括号） | `DrSection IGetSection()` | [[Section]] for this section view | 查不到 |
| IGetSectionLineInfo2 | 否（有形参） | `System.double IGetSectionLineInfo2( System.int ArraySize )` | Array of doubles (see **Remarks**) | This method gets all of the information on section lines in the view. |
| IGetSketch | 是（空括号） | `Sketch IGetSketch()` | [[Sketch]] | Each drawing view contains an underlying sketch. |
| IGetSMBoundaryBoxDisplayData | 是（空括号） | `DisplayData IGetSMBoundaryBoxDisplayData()` | [[Display data]] of boundary-box sketch of a flat-pattern drawing view | 查不到 |
| IGetTemporaryAxes | 否（有形参） | `System.double IGetTemporaryAxes( System.int TempAxesCount )` | 查不到 | Call [[IView::GetTemporaryAxesCount]] before calling this method to get the value for TempAxesCount. |
| IGetViewXform | 是（空括号） | `System.double IGetViewXform()` | Array of doubles (see **Remarks**) | The return value is formatted as the following array of 13 doubles: |
| IGetVisibleComponents | 否（有形参） | `Component2 IGetVisibleComponents( System.int ViewComponentCount )` | Visible [[components]] in this drawing view | Visible components are only those components not completely obscured by other components in the view. |
| IGetXform | 是（空括号） | `System.double IGetXform()` | Array of 3 doubles that describe the location and scale of the drawing view (see **Remarks**) | The first two values returned are the X and Y locations of the view relative to the sheet origin, and the third value returned is the scale of the drawing view. |
| IInsertBomTable | 否（有形参） | `BomTable IInsertBomTable( System.string Template, System.double Xloc, System.double Yloc, out System.int Errors )` | [[BOM table]] | This method creates a default BOM table at the specified location, using the given template. |
| ImportAnnotations | 否（有形参） | `void ImportAnnotations( System.bool IncludeDesignAnnotations, System.bool IncludeCosmeticThreads, System.bool IncludeDimXpertAnnotations, System.bool IncludeHiddenFeatureItems, System.bool Include3DViewAnnotations )` | 查不到 | 查不到 |
| InsertAlternateView | 否（有形参） | `View InsertAlternateView( System.string ConfigurationName )` | Alternate [[drawing view]] | Before using this method, you must select a drawing view on which to superimpose the **Alternate Position View**. |
| InsertBendTable | 否（有形参） | `BendTableAnnotation InsertBendTable( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )` | [[IBendTableAnnotation]] | 查不到 |
| InsertBomTable | 否（有形参） | `System.object InsertBomTable( System.string Template, System.double Xloc, System.double Yloc, out System.int Errors )` | [[BOM table]] | This method creates a default BOM table at the specified location, using the given template. |
| InsertBomTable6 | 否（有形参） | `System.object InsertBomTable6( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.int BomType, System.string Configuration, System.string TableTemplate, System.bool Hidden, System.int IndentedNumberingType, System.bool DetailedCutList, System.bool DissolvePartLevelRows, System.bool DisplayAsOneItem )` | [[BOM table annotation]] | If BomType is swBomType_TopLevelOnly, then do not specify Configuration. |
| InsertBreak3 | 否（有形参） | `System.object InsertBreak3( System.int Orientation, System.double Position1, System.double Position2, System.int Style, System.int ShapeIntensity, System.bool BreakSketchBlocks )` | [[Break line]] | A break in a drawing view consists of a pair of break lines. |
| InsertCutListPropertyNote | 否（有形参） | `void InsertCutListPropertyNote( System.double X, System.double Y, System.double Z )` | 查不到 | This method requires a flat pattern drawing view. |
| InsertHoleTable3 | 否（有形参） | `System.object InsertHoleTable3( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string Template, System.int TagOrder, System.int TagType, System.object ManualTags )` | [[Hole table annotation]] | This method inserts a hole table with the following information for selected holes: |
| InsertPunchTable | 否（有形参） | `PunchTableAnnotation InsertPunchTable( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )` | [[IPunchTableAnnotation]] | Punch tables contain information about the punches that are created by forming tools in sheet metal parts. |
| InsertViewAsBlock | 否（有形参） | `System.bool InsertViewAsBlock( MathPoint InsertionPoint, MathPoint Position )` | True if the view is successfully converted to a sketch block, false if not | 查不到 |
| InsertWeldmentTable | 否（有形参） | `WeldmentCutListAnnotation InsertWeldmentTable( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string Configuration, System.string TableTemplate )` | [[Weldment cut-list annotation]] | The weldment cut-list table template installed with SOLIDWORKS is <*SOLIDWORKS_*install_dir>\**lang**\<language>\**cut list.sldwldtbt**. |
| InsertWeldTable | 否（有形参） | `System.bool InsertWeldTable( System.bool UseAnchorPoint, System.bool IncludeAnnotations, System.bool CombineSameType, System.double X, System.double Y, System.int AnchorType, System.string Configuration, System.string TableTemplate )` | True if successful, false if not | The weld table template installed with SOLIDWORKS is <*SOLIDWORKS_*install_dir>\**lang**\<language>\**weldtable-standard.sldwldtbt**. |
| IPosition | 是（无括号） | `System.double IPosition {get; set;}` | Array of 2 doubles (see **Remarks**) | Any view alignments that might affect this view are handled the same way as if you were using the SOLIDWORKS Design user interface to draw the view to move it. |
| IsBroken | 是（空括号） | `System.bool IsBroken()` | True if the view is displayed with a break, false if not | This method indicates if the view is displayed broken, not if the view has break lines. |
| IScaleRatio | 是（无括号） | `System.double IScaleRatio {get; set;}` | Array of 2 doubles (see **Remarks**) | The two values represent the two numbers if the scale is described as a ratio. |
| IsCropped | 是（空括号） | `System.bool IsCropped()` | True if the drawing view is cropped, false if not | 查不到 |
| ISelectEntity | 否（有形参） | `System.bool ISelectEntity( Entity Entity, System.bool AppendFlag )` | True if the entity was selected, false if not | 查不到 |
| ISetBodies | 否（有形参） | `void ISetBodies( System.int Count, ref Body2 BodyArray )` | 查不到 | 查不到 |
| ISetXform | 否（有形参） | `System.bool ISetXform( ref System.double Transform )` | True if transform successfully set, false if not | The 3 doubles are the X and Y position of the view, relative to the sheet origin, and the scale of the view. |
| IsExploded | 是（空括号） | `System.bool IsExploded()` | True if this drawing view is showing an exploded assembly view, false if collapsed | 查不到 |
| IsFlatPatternView | 是（空括号） | `System.bool IsFlatPatternView()` | True if this drawing view is a flat-pattern drawing view, false if not | 查不到 |
| IsLightweight | 是（空括号） | `System.bool IsLightweight()` | True if lightweight, false if not | 查不到 |
| IsModelBreakState | 是（空括号） | `System.bool IsModelBreakState()` | True if a Model Break View, false if not | 查不到 |
| IsModelLoaded | 是（空括号） | `System.bool IsModelLoaded()` | True if the model has been loaded, false if not | If the drawing document was loaded as Detached, then the return value will be false. |
| IsModelOutOfDate | 是（空括号） | `System.bool IsModelOutOfDate()` | True if the view is out of date, false if not | A model can be out-of-date in a Detached drawing where the model is not loaded, if any of the views in any of the sheets in the drawing refers to a model that has been modified and saved to disk since this drawing was last saved. |
| IsPerspectiveView | 是（空括号） | `System.bool IsPerspectiveView()` | True if perspective view is shown, false if not | 查不到 |
| LinkParentConfiguration | 是（无括号） | `System.bool LinkParentConfiguration {get; set;}` | True to link a projected or auxiliary view with the parent configuration, false to not | After setting this property, call [[IModelDoc2::EditRebuild3]]. |
| LoadModel | 是（空括号） | `System.int LoadModel()` | 0 if the model was loaded, -1 if not | 查不到 |
| MergeBendTags | 否（有形参） | `System.bool MergeBendTags( System.bool Merge, System.object BendNotes )` | True if the bend tags are merged or a merged bend tag is unmerged, false if not | **To...** **Do...** |
| ModelToViewTransform | 是（无括号） | `MathTransform ModelToViewTransform {get; set;}` | [[Math transform]] | 查不到 |
| Position | 是（无括号） | `System.object Position {get; set;}` | Array of 2 doubles (see **Remarks**) | Any view alignments that might affect this view are handled the same way as if you were using the SOLIDWORKS Design user interface to draw the view to move it. |
| PositionLocked | 是（无括号） | `System.bool PositionLocked {get; set;}` | True if view position is locked, false if not | 查不到 |
| ProjectedDimensions | 是（无括号） | `System.bool ProjectedDimensions {get; set;}` | True if the dimensions in this drawing view are projected measurements, false if the dimensions in this drawing view are true measurements | Existing dimensions in this drawing view are deleted when this property is changed. |
| ReferencedConfiguration | 是（无括号） | `System.string ReferencedConfiguration {get; set;}` | Name of the configuration for the drawing view | After changing the configuration, you must call [[IModelDoc2::EditRebuild3]] to see the changes. |
| ReferencedConfigurationID | 是（无括号） | `System.int ReferencedConfigurationID {get;}` | Referenced configuration's persistent reference ID | See [Persistent Reference IDs](<../../docs/Programming with the SOLIDWORKS API/Persistent Reference IDs.md>) for more information. |
| ReferencedDocument | 是（无括号） | `ModelDoc2 ReferencedDocument {get;}` | [[Model document]] | Because section views do not have referenced documents, this method returns an empty string for this type of view. |
| RemoveAlignment | 是（空括号） | `void RemoveAlignment()` | 查不到 | Using this method on a view only removes the alignment information from that view. |
| ReplaceViewWithBlock | 否（有形参） | `System.bool ReplaceViewWithBlock( MathPoint InsertionPoint )` | True if the view is successfully replaced with a sketch block, false if not | 查不到 |
| ReplaceViewWithSketch | 是（空括号） | `System.bool ReplaceViewWithSketch()` | True if the view is successfully replaced with a [[sketch]], false if not | 查不到 |
| ResetSketchVisibility | 是（空括号） | `void ResetSketchVisibility()` | 查不到 | 查不到 |
| RootDrawingComponent2 | 查不到 | 查不到 | 查不到 | 查不到 |
| ScaleDecimal | 是（无括号） | `System.double ScaleDecimal {get; set;}` | Drawing view scale | [[IView::ScaleRatio]] or [[IView::IScaleRatio]] and this property contain the same information, but use the value in different ways: |
| ScaleHatchPattern | 是（无括号） | `System.bool ScaleHatchPattern {get; set;}` | True to scale the hatch pattern to the drawing view, false to not | 查不到 |
| ScaleRatio | 是（无括号） | `System.object ScaleRatio {get; set;}` | Array of 2 doubles (see **Remarks**) | The two values represent the two numbers if the scale is described as a ratio. |
| SelectEntity | 否（有形参） | `System.bool SelectEntity( System.object Entity, System.bool AppendFlag )` | 查不到 | 查不到 |
| SetBendNoteTextFormat | 否（有形参） | `System.bool SetBendNoteTextFormat( System.string Format )` | True if format is successfully set, false if not | Before calling this method, call [[IView::GetBendNoteAttributeString]] to specify Format. |
| SetDisplayMode4 | 否（有形参） | `System.bool SetDisplayMode4( System.bool UseParent, System.int Mode, System.bool Faceted, System.bool Edges, System.bool CThreadHighQuality )` | True if the display mode is reset, false if not | If UseParent is true and a parent view: |
| SetDisplayTangentEdges2 | 否（有形参） | `void SetDisplayTangentEdges2( System.int DisplayIn )` | 查不到 | Tangent edges are the transition lines between, for example, a blend and a face. |
| SetKeepLinkedToBOM | 否（有形参） | `System.bool SetKeepLinkedToBOM( System.bool Linked, System.string Name )` | True if the BOM or weldment cut-list table is linked to this drawing view, false if not | This method returns false if the string specified for Name does not correspond to the name of a BOM or weldment cut-list table feature created for the model in this drawing view. |
| SetLightweightToResolved | 是（空括号） | `void SetLightweightToResolved()` | 查不到 | 查不到 |
| SetMirrorViewOrientation | 否（有形参） | `System.bool SetMirrorViewOrientation( System.bool BSetIsMirrorView, System.int BMirrorVieworientation )` | True if the method executed successfully, false if not | 查不到 |
| SetName2 | 否（有形参） | `System.bool SetName2( System.string Name )` | True if the name of the drawing view is set, false if not | The drawing view name that you specify: |
| SetResolvedToLightweight | 是（空括号） | `void SetResolvedToLightweight()` | 查不到 | 查不到 |
| SetViewPosition | 否（有形参） | `System.bool SetViewPosition( System.object Position, System.bool MoveChildViews )` | True if view position successfully set, false if not | Take careful note of view alignments when specifying Position. |
| SetVisible | 否（有形参） | `void SetVisible( System.bool Visible, System.bool DependentsToo )` | 查不到 | 查不到 |
| SetXform | 否（有形参） | `System.bool SetXform( System.object Transform )` | True if transform successfully set, false if not | The 3 doubles are the X and Y position of the view, relative to the sheet origin, and the scale of the view. |
| Sheet | 是（无括号） | `Sheet Sheet {get;}` | [[Sheet]] | 查不到 |
| ShowExploded | 否（有形参） | `System.bool ShowExploded( System.bool ShowIt )` | True if successful in displaying the exploded assembly state, false if not | The explode state that is displayed is based on the current assembly configuration used by this drawing view |
| ShowModelBreakState | 否（有形参） | `System.bool ShowModelBreakState( System.bool ShowIt, System.string BreakName )` | True if successful, false if not | 查不到 |
| ShowSheetMetalBendNotes | 是（无括号） | `System.bool ShowSheetMetalBendNotes {get; set;}` | True to show sheet metal bend notes, false to not | 查不到 |
| SuppressState | 是（无括号） | `System.int SuppressState {get; set;}` | NO_SUPPRESS = 0 | 查不到 |
| Type | 是（无括号） | `System.int Type {get;}` | Type of drawing view as defined by [[swDrawingViewTypes_e]] | 查不到 |
| UpdateViewDisplayGeometry | 是（空括号） | `void UpdateViewDisplayGeometry()` | 查不到 | This method accesses new view geometry before Microsoft has repainted the window. |
| UseDefaultAlignment | 是（空括号） | `void UseDefaultAlignment()` | 查不到 | The default alignment for a view depends on the [[view type]]. |
| UseParentScale | 是（无括号） | `System.bool UseParentScale {get; set;}` | True if the drawing view's scale is set to be the same as the parent's drawing view scale, false if the drawing view scale is independent of the parent's drawing view scale | Changing this property can cause changes to the graphics of the drawing. |
| UseSheetScale | 是（无括号） | `System.int UseSheetScale {get; set;}` | 1 if the view scale is the same as the sheet scale, 0 if the view scale is independent of the sheet scale | If the property is 0, then it is possible that the view scale is the same as the sheet scale. |

## 三、废弃成员（149 个）—— 原因：页头写明 `Obsolete.`，已被后继成员取代

| 成员名 | 零参? | 签名 | 废弃声明原文 | 后继 |
|---|---|---|---|---|
| AutoInsertCenterMarks | 否（有形参） | `System.bool AutoInsertCenterMarks( System.int InsertType, System.int InsertOption, System.bool LinearSlotCenter, System.bool ArcSlotCenter, System.bool UseDocumentDefaults, System.double Size, System.bool ExtendedLines, System.bool CenterLineFont, System.double Angle )` | Obsolete. Superseded by [[IView::AutoInsertCenterMarks2]]. | `IView::AutoInsertCenterMarks2` |
| Crop | 是（空括号） | `System.int Crop()` | Obsolete. Superseded by [[IView::Crop2]]. | `IView::Crop2` |
| EnumHiddenComponents | 是（空括号） | `EnumComponents EnumHiddenComponents()` | Obsolete. Superseded by [[IView::EnumHiddenComponents2]]. | `IView::EnumHiddenComponents2` |
| EnumSectionLines | 是（空括号） | `EnumDrSections EnumSectionLines()` | Obsolete. Superseded by [[IView::EnumSectionLines2]]. | `IView::EnumSectionLines2` |
| GetArcs | 是（空括号） | `System.object GetArcs()` | Obsolete. Superseded by [[IView::GetArcs4]] and [[IView::IGetArcs4]]. | `IView::GetArcs4` |
| GetArcs2 | 是（空括号） | `System.object GetArcs2()` | Obsolete. Superseded by [[IView::GetArcs4]] and [[IView::IGetArcs4]]. | `IView::GetArcs4` |
| GetArcs3 | 是（空括号） | `System.object GetArcs3()` | Obsolete. Superseded by [[IView::GetArcs4]] and [[IView::IGetArcs4]]. | `IView::GetArcs4` |
| GetBreakLineCount | 否（有形参） | `System.int GetBreakLineCount( out System.int Size )` | Obsolete. Superseded by [[IView::GetBreakLineCount2]]. | `IView::GetBreakLineCount2` |
| GetBreakLineInfo | 是（空括号） | `System.object GetBreakLineInfo()` | Obsolete. Superseded by [[IView::GetBreakLineInfo2]]. | `IView::GetBreakLineInfo2` |
| GetCenterMarkCount | 是（空括号） | `System.int GetCenterMarkCount()` | Obsolete. Superseded by [[IView::GetCenterMarkCount2]]. | `IView::GetCenterMarkCount2` |
| GetDatumPoints | 是（空括号） | `System.object GetDatumPoints()` | Obsolete. Superseded by [[IView::GetDatumPoints2]] and [[IView::IGetDatumPoints2]]. | `IView::GetDatumPoints2` |
| GetDetailCircleCount | 是（空括号） | `System.int GetDetailCircleCount()` | Obsolete. Superseded by [[IView::GetDetailCircleCount2]]. | `IView::GetDetailCircleCount2` |
| GetDetailCircleInfo | 是（空括号） | `System.object GetDetailCircleInfo()` | Obsolete. Superseded by [[IView::GetDetailCircleInfo2]] and [[IView::IGetDetailCircleInfo2]]. | `IView::GetDetailCircleInfo2` |
| GetDimensionCount | 是（空括号） | `System.int GetDimensionCount()` | Obsolete. Superseded by [[IView::GetDimensionCount4]]. | `IView::GetDimensionCount4` |
| GetDimensionCount2 | 是（空括号） | `System.int GetDimensionCount2()` | Obsolete. Superseded by [[IView::GetDimensionCount4]]. | `IView::GetDimensionCount4` |
| GetDimensionCount3 | 是（空括号） | `System.int GetDimensionCount3()` | Obsolete. Superseded by [[IView::GetDimensionCount4]]. | `IView::GetDimensionCount4` |
| GetDimensionDisplayInfo | 是（空括号） | `System.object GetDimensionDisplayInfo()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| GetDimensionDisplayInfo2 | 是（空括号） | `System.object GetDimensionDisplayInfo2()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| GetDimensionDisplayInfo3 | 是（空括号） | `System.object GetDimensionDisplayInfo3()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| GetDimensionDisplayInfo4 | 是（空括号） | `System.object GetDimensionDisplayInfo4()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| GetDimensionDisplayInfoSize | 是（空括号） | `System.int GetDimensionDisplayInfoSize()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfoSize2]]. | `IView::GetDimensionDisplayInfoSize2` |
| GetDimensionDisplayString | 是（空括号） | `System.object GetDimensionDisplayString()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString4]] and [[IView::IGetDimensionDisplayString4]]. | `IView::GetDimensionDisplayString4` |
| GetDimensionDisplayString2 | 是（空括号） | `System.object GetDimensionDisplayString2()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString4]] and [[IView::IGetDimensionDisplayString4]]. | `IView::GetDimensionDisplayString4` |
| GetDimensionDisplayString3 | 是（空括号） | `System.object GetDimensionDisplayString3()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString4]] and [[IView::IGetDimensionDisplayString4]]. | `IView::GetDimensionDisplayString4` |
| GetDimensionDisplayString4 | 是（空括号） | `System.object GetDimensionDisplayString4()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString5]]. | `IView::GetDimensionDisplayString5` |
| GetDimensionIds | 是（空括号） | `System.object GetDimensionIds()` | Obsolete. Superseded by [[IView::GetDimensionIds4]] and [[IView::IGetDimensionIds4]]. | `IView::GetDimensionIds4` |
| GetDimensionIds2 | 是（空括号） | `System.object GetDimensionIds2()` | Obsolete. Superseded by [[IView::GetDimensionIds4]] and [[IView::IGetDimensionIds4]]. | `IView::GetDimensionIds4` |
| GetDimensionIds3 | 是（空括号） | `System.object GetDimensionIds3()` | Obsolete. Superseded by [[IView::GetDimensionIds4]] and [[IView::IGetDimensionIds4]]. | `IView::GetDimensionIds4` |
| GetDimensionInfo | 是（空括号） | `System.object GetDimensionInfo()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| GetDimensionInfo2 | 是（空括号） | `System.object GetDimensionInfo2()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| GetDimensionInfo3 | 是（空括号） | `System.object GetDimensionInfo3()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| GetDimensionInfo4 | 是（空括号） | `System.object GetDimensionInfo4()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| GetDimensionInfo5 | 是（空括号） | `System.object GetDimensionInfo5()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| GetDimensionInfo6 | 是（空括号） | `System.object GetDimensionInfo6()` | Obsolete. Superseded by [[IView::GetDimensionInfo7]]. | `IView::GetDimensionInfo7` |
| GetDimensionString | 是（空括号） | `System.object GetDimensionString()` | Obsolete. Superseded by [[IView::GetDimensionString4]] and [[IView::IGetDimensionString4]]. | `IView::GetDimensionString4` |
| GetDimensionString2 | 是（空括号） | `System.object GetDimensionString2()` | Obsolete. Superseded by [[IView::GetDimensionString4]] and [[IView::IGetDimensionString4]]. | `IView::GetDimensionString4` |
| GetDimensionString3 | 是（空括号） | `System.object GetDimensionString3()` | Obsolete. Superseded by [[IView::GetDimensionString4]] and [[IView::IGetDimensionString4]]. | `IView::GetDimensionString4` |
| GetDisplayData | 是（空括号） | `System.object GetDisplayData()` | Obsolete. Superseded by [[IView::GetDisplayData3]] and [[IView::IGetDisplayData3]]. | `IView::GetDisplayData3` |
| GetDisplayData2 | 是（空括号） | `System.object GetDisplayData2()` | Obsolete. Superseded by [[IView::GetDisplayData3]] and [[IView::IGetDisplayData3]]. | `IView::GetDisplayData3` |
| GetDisplayData3 | 是（空括号） | `System.object GetDisplayData3()` | Obsolete. Superseded by [[IView::GetDisplayData4]]. | `IView::GetDisplayData4` |
| GetDisplayMode | 是（空括号） | `System.int GetDisplayMode()` | Obsolete. Superseded by [[IView::GetDisplayMode2]]. | `IView::GetDisplayMode2` |
| GetDisplayTangentEdges | 是（空括号） | `System.bool GetDisplayTangentEdges()` | Obsolete. Superseded by [[IView::GetDisplayTangentEdges2]]. | `IView::GetDisplayTangentEdges2` |
| GetEllipses | 是（空括号） | `System.object GetEllipses()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| GetEllipses2 | 是（空括号） | `System.object GetEllipses2()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| GetEllipses3 | 是（空括号） | `System.object GetEllipses3()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| GetEllipses4 | 是（空括号） | `System.object GetEllipses4()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| GetFirstAnnotation | 是（空括号） | `System.object GetFirstAnnotation()` | Obsolete. Superseded by [[IView::GetFirstAnnotation3]]. | `IView::GetFirstAnnotation3` |
| GetFirstAnnotation2 | 是（空括号） | `System.object GetFirstAnnotation2()` | Obsolete. Superseded by [[IView::GetFirstAnnotation3]]. | `IView::GetFirstAnnotation3` |
| GetFirstBlockInstance | 是（空括号） | `BlockInstance GetFirstBlockInstance()` | Obsolete. Not superseded. | `（该行未给出后继）` |
| GetFirstCenterMark | 是（空括号） | `CenterMark GetFirstCenterMark()` | Obsolete. Superseded by [[IView::GetFirstCenterMark2]]. | `IView::GetFirstCenterMark2` |
| GetFirstCustomSymbol | 是（空括号） | `System.object GetFirstCustomSymbol()` | Obsolete. Not superseded. | `（该行未给出后继）` |
| GetFirstDisplayDimension | 是（空括号） | `System.object GetFirstDisplayDimension()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| GetFirstDisplayDimension2 | 是（空括号） | `System.object GetFirstDisplayDimension2()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| GetFirstDisplayDimension3 | 是（空括号） | `System.object GetFirstDisplayDimension3()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| GetFirstDisplayDimension4 | 是（空括号） | `DisplayDimension GetFirstDisplayDimension4()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| GetFirstDisplayDimension5 | 是（空括号） | `DisplayDimension GetFirstDisplayDimension5()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension6]]. | `IView::GetFirstDisplayDimension6` |
| GetFirstMultiJogLeader | 是（空括号） | `System.object GetFirstMultiJogLeader()` | Obsolete. Superseded by [[IView::GetFirstMultiJogLeader2]]. | `IView::GetFirstMultiJogLeader2` |
| GetFirstNote | 是（空括号） | `System.object GetFirstNote()` | Obsolete. Superseded by [[IView::GetFirstNote2]]. | `IView::GetFirstNote2` |
| GetFirstRevisionCloud | 是（空括号） | `System.object GetFirstRevisionCloud()` | Obsolete. Superseded by [[IView::GetFirstRevisionCloud2]]. | `IView::GetFirstRevisionCloud2` |
| GetFirstTableAnnotation | 是（空括号） | `TableAnnotation GetFirstTableAnnotation()` | Obsolete. Superseded by [[IView::GetFirstTableAnnotation2]]. | `IView::GetFirstTableAnnotation2` |
| GetLineCount | 是（空括号） | `System.int GetLineCount()` | Obsolete. Superseded by [[IView::GetLineCount2]]. | `IView::GetLineCount2` |
| GetLines | 是（空括号） | `System.object GetLines()` | Obsolete. Superseded by [[IView::GetLines4]] and [[IView::IGetLines4]]. | `IView::GetLines4` |
| GetLines2 | 是（空括号） | `System.object GetLines2()` | Obsolete. Superseded by [[IView::GetLines4]] and [[IView::IGetLines4]]. | `IView::GetLines4` |
| GetLines3 | 是（空括号） | `System.object GetLines3()` | Obsolete. Superseded by [[IView::GetLines4]] and [[IView::IGetLines4]]. | `IView::GetLines4` |
| GetParabolas | 是（空括号） | `System.object GetParabolas()` | Obsolete. Superseded by [[IView::GetParabolas2]] and [[IView::IGetParabolas2]]. | `IView::GetParabolas2` |
| GetPolyLineCount | 否（有形参） | `System.int GetPolyLineCount( out System.int PointCount )` | Obsolete. Superseded by [[IView::GetPolyLineCount5]]. | `IView::GetPolyLineCount5` |
| GetPolyLineCount2 | 否（有形参） | `System.int GetPolyLineCount2( out System.int PointCount )` | Obsolete. Superseded by [[IView::GetPolyLineCount5]]. | `IView::GetPolyLineCount5` |
| GetPolyLineCount3 | 否（有形参） | `System.int GetPolyLineCount3( out System.int PointCount )` | Obsolete. Superseded by [[IView::GetPolyLineCount5]]. | `IView::GetPolyLineCount5` |
| GetPolyLineCount4 | 否（有形参） | `System.int GetPolyLineCount4( out System.int PointCount )` | Obsolete. Superseded by [[IView::GetPolyLineCount5]]. | `IView::GetPolyLineCount5` |
| GetPolylines | 是（空括号） | `System.object GetPolylines()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| GetPolylines2 | 是（空括号） | `System.object GetPolylines2()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| GetPolylines3 | 是（空括号） | `System.object GetPolylines3()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| GetPolylines4 | 是（空括号） | `System.object GetPolylines4()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| GetPolylines5 | 否（有形参） | `System.object GetPolylines5( System.short CrossHatchOption )` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| GetPolylines6 | 否（有形参） | `System.object GetPolylines6( System.short CrossHatchOption, out System.object Polylines )` | Obsolete. Superseded by [[IView::GetPolylines7]]. | `IView::GetPolylines7` |
| GetSectionLineCount | 否（有形参） | `System.int GetSectionLineCount( out System.int Size )` | Obsolete. Superseded by [[IView::GetSectionLineCount2]]. | `IView::GetSectionLineCount2` |
| GetSectionLineInfo | 是（空括号） | `System.object GetSectionLineInfo()` | Obsolete. Superseded by [[IView::GetSectionLineInfo2]] and [[IView::GetSectionLineInfo2]]. | `IView::GetSectionLineInfo2` |
| GetSMBoundaryBoxDisplayData | 是（空括号） | `System.object GetSMBoundaryBoxDisplayData()` | Obsolete. Superseded by [[IVew::GetSMBoundaryBoxDisplayData2]]. | `IVew::GetSMBoundaryBoxDisplayData2` |
| GetSplines | 是（空括号） | `System.object GetSplines()` | Obsolete. Superseded by [[IView::GetSplines3]] and [[IView::IGetSplines3]]. | `IView::GetSplines3` |
| GetSplines2 | 是（空括号） | `System.object GetSplines2()` | Obsolete. Superseded by [[IView::GetSplines3]] and [[IView::IGetSplines3]]. | `IView::GetSplines3` |
| GetUserPoints | 是（空括号） | `System.object GetUserPoints()` | Obsolete. Superseded by [[IView::GetUserPoints2]] and [[IView::IGetUserPoints2]]. | `IView::GetUserPoints2` |
| GetVisibleEntities | 否（有形参） | `System.object GetVisibleEntities( Component2 LpViewComponent, System.int EntityType )` | Obsolete. Superseded by [[IView::GetVisibleEntities2]]. | `IView::GetVisibleEntities2` |
| GetVisibleEntityCount | 否（有形参） | `System.int GetVisibleEntityCount( Component2 LpViewComponent, System.int EntityType )` | Obsolete. Superseded by [[IView::GetVisibleEntityCount2]]. | `IView::GetVisibleEntityCount2` |
| IGetArcs | 是（空括号） | `System.double IGetArcs()` | Obsolete. Superseded by [[IView::GetArcs4]] and [[IView::IGetArcs4]]. | `IView::GetArcs4` |
| IGetArcs2 | 是（空括号） | `System.double IGetArcs2()` | Obsolete. Superseded by [[IView::GetArcs4]] and [[IView::IGetArcs4]]. | `IView::GetArcs4` |
| IGetArcs3 | 是（空括号） | `System.double IGetArcs3()` | Obsolete. Superseded by [[IView::GetArcs4]] and [[IView::IGetArcs4]]. | `IView::GetArcs4` |
| IGetBreakLineInfo | 否（有形参） | `System.double IGetBreakLineInfo( System.int ArraySize )` | Obsolete. Superseded by [[IView::IGetBreakLineInfo2]]. | `IView::IGetBreakLineInfo2` |
| IGetDatumPoints | 是（空括号） | `System.double IGetDatumPoints()` | Obsolete. Superseded by [[IView::GetDatumPoints2]] and [[IView::IGetDatumPoints2]]. | `IView::GetDatumPoints2` |
| IGetDetailCircleInfo | 是（空括号） | `System.double IGetDetailCircleInfo()` | Obsolete. Superseded by [[IView::GetDetailCircleInfo2]] and [[IView::IGetDetailCircleInfo2]]. | `IView::GetDetailCircleInfo2` |
| IGetDimensionDisplayInfo | 是（空括号） | `System.double IGetDimensionDisplayInfo()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| IGetDimensionDisplayInfo2 | 是（空括号） | `System.double IGetDimensionDisplayInfo2()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| IGetDimensionDisplayInfo3 | 是（空括号） | `System.double IGetDimensionDisplayInfo3()` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| IGetDimensionDisplayInfo4 | 否（有形参） | `System.double IGetDimensionDisplayInfo4( System.int ArraySize )` | Obsolete. Superseded by [[IView::GetDimensionDisplayInfo5]] and [[IView::IGetDimensionDisplayInfo5]]. | `IView::GetDimensionDisplayInfo5` |
| IGetDimensionDisplayString | 是（空括号） | `System.string IGetDimensionDisplayString()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString4]] and [[IView::IGetDimensionDisplayString4]]. | `IView::GetDimensionDisplayString4` |
| IGetDimensionDisplayString2 | 是（空括号） | `System.string IGetDimensionDisplayString2()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString4]] and [[IView::IGetDimensionDisplayString4]]. | `IView::GetDimensionDisplayString4` |
| IGetDimensionDisplayString3 | 是（空括号） | `System.string IGetDimensionDisplayString3()` | Obsolete. Superseded by [[IView::GetDimensionDisplayString4]] and [[IView::IGetDimensionDisplayString4]]. | `IView::GetDimensionDisplayString4` |
| IGetDimensionIds | 是（空括号） | `System.string IGetDimensionIds()` | Obsolete. Superseded by [[IView::GetDimensionIds4]] and [[IView::IGetDimensionIds4]]. | `IView::GetDimensionIds4` |
| IGetDimensionIds2 | 是（空括号） | `System.string IGetDimensionIds2()` | Obsolete. Superseded by [[IView::GetDimensionIds4]] and [[IView::IGetDimensionIds4]]. | `IView::GetDimensionIds4` |
| IGetDimensionIds3 | 是（空括号） | `System.string IGetDimensionIds3()` | Obsolete. Superseded by [[IView::GetDimensionIds4]] and [[IView::IGetDimensionIds4]]. | `IView::GetDimensionIds4` |
| IGetDimensionInfo | 是（空括号） | `System.double IGetDimensionInfo()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| IGetDimensionInfo2 | 是（空括号） | `System.double IGetDimensionInfo2()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| IGetDimensionInfo3 | 是（空括号） | `System.double IGetDimensionInfo3()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| IGetDimensionInfo4 | 是（空括号） | `System.double IGetDimensionInfo4()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| IGetDimensionInfo5 | 是（空括号） | `System.double IGetDimensionInfo5()` | Obsolete. Superseded by [[IView::GetDimensionInfo6]] and [[IView::IGetDimensionInfo6]]. | `IView::GetDimensionInfo6` |
| IGetDimensionInfo6 | 是（空括号） | `System.double IGetDimensionInfo6()` | Obsolete. Superseded by [[IView::GetDimensionInfo7]]. | `IView::GetDimensionInfo7` |
| IGetDimensionString | 是（空括号） | `System.string IGetDimensionString()` | Obsolete. Superseded by [[IView::GetDimensionString4]] and [[IView::IGetDimensionString4]]. | `IView::GetDimensionString4` |
| IGetDimensionString2 | 是（空括号） | `System.string IGetDimensionString2()` | Obsolete. Superseded by [[IView::GetDimensionString4]] and [[IView::IGetDimensionString4]]. | `IView::GetDimensionString4` |
| IGetDimensionString3 | 是（空括号） | `System.string IGetDimensionString3()` | Obsolete. Superseded by [[IView::GetDimensionString4]] and [[IView::IGetDimensionString4]]. | `IView::GetDimensionString4` |
| IGetDisplayData | 是（空括号） | `DisplayData IGetDisplayData()` | Obsolete. Superseded by [[IView::GetDisplayData3]] and [[IView::IGetDisplayData3]]. | `IView::GetDisplayData3` |
| IGetDisplayData2 | 是（空括号） | `DisplayData IGetDisplayData2()` | Obsolete. Superseded by [[IView::GetDisplayData3]] and [[IView::IGetDisplayData3]]. | `IView::GetDisplayData3` |
| IGetEllipses | 是（空括号） | `System.double IGetEllipses()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| IGetEllipses2 | 是（空括号） | `System.double IGetEllipses2()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| IGetEllipses3 | 是（空括号） | `System.double IGetEllipses3()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| IGetEllipses4 | 是（空括号） | `System.double IGetEllipses4()` | Obsolete. Superseded by [[IView::GetEllipses5]] and [[IView::IGetEllipses5]]. | `IView::GetEllipses5` |
| IGetFirstAnnotation | 是（空括号） | `Annotation IGetFirstAnnotation()` | Obsolete. Superseded by [[IView::GetFirstAnnotation3]]. | `IView::GetFirstAnnotation3` |
| IGetFirstAnnotation2 | 是（空括号） | `Annotation IGetFirstAnnotation2()` | Obsolete. Superseded by [[IView::GetFirstAnnotation3]]. | `IView::GetFirstAnnotation3` |
| IGetFirstCustomSymbol | 是（空括号） | `CustomSymbol IGetFirstCustomSymbol()` | Obsolete. Not superseded. | `（该行未给出后继）` |
| IGetFirstDisplayDimension | 是（空括号） | `DisplayDimension IGetFirstDisplayDimension()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| IGetFirstDisplayDimension2 | 是（空括号） | `DisplayDimension IGetFirstDisplayDimension2()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| IGetFirstDisplayDimension3 | 是（空括号） | `DisplayDimension IGetFirstDisplayDimension3()` | Obsolete. Superseded by [[IView::GetFirstDisplayDimension5]]. | `IView::GetFirstDisplayDimension5` |
| IGetLines | 是（空括号） | `System.double IGetLines()` | Obsolete. Superseded by [[IView::GetLines4]] and [[IView::IGetLines4]]. | `IView::GetLines4` |
| IGetLines2 | 是（空括号） | `System.double IGetLines2()` | Obsolete. Superseded by [[IView::GetLines4]] and [[IView::IGetLines4]]. | `IView::GetLines4` |
| IGetLines3 | 是（空括号） | `System.double IGetLines3()` | Obsolete. Superseded by [[IView::GetLines4]] and [[IView::IGetLines4]]. | `IView::GetLines4` |
| IGetParabolas | 是（空括号） | `System.double IGetParabolas()` | Obsolete. Superseded by [[IView::GetParabolas2]] and [[IView::IGetParabolas2]]. | `IView::GetParabolas2` |
| IGetPolylines | 是（空括号） | `System.double IGetPolylines()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| IGetPolylines2 | 是（空括号） | `System.double IGetPolylines2()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| IGetPolylines3 | 是（空括号） | `System.double IGetPolylines3()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| IGetPolylines4 | 是（空括号） | `System.double IGetPolylines4()` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| IGetPolylines5 | 否（有形参） | `System.double IGetPolylines5( System.short CrossHatchOption, System.int ArraySize )` | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]]. | `IView::GetPolyLines6` |
| IGetPolylines6 | 否（有形参） | `Edge IGetPolylines6( System.short CrossHatchOption, System.int ArraySize, out System.double Polylines, System.int EdgeArraySize )` | Obsolete. Superseded by [[IView::IGetPolylines7]]. | `IView::IGetPolylines7` |
| IGetSectionLineInfo | 是（空括号） | `System.double IGetSectionLineInfo()` | Obsolete. Superseded by [[IView::GetSectionLineInfo2]] and [[IView::GetSectionLineInfo2]]. | `IView::GetSectionLineInfo2` |
| IGetSplines | 是（空括号） | `System.double IGetSplines()` | Obsolete. Superseded by [[IView::GetSplines3]] and [[IView::IGetSplines3]]. | `IView::GetSplines3` |
| IGetSplines2 | 是（空括号） | `System.double IGetSplines2()` | Obsolete. Superseded by [[IView::GetSplines3]] and [[IView::IGetSplines3]]. | `IView::GetSplines3` |
| IGetUserPoints | 是（空括号） | `System.double IGetUserPoints()` | Obsolete. Superseded by [[IView::GetUserPoints2]] and [[IView::IGetUserPoints2]]. | `IView::GetUserPoints2` |
| IGetVisibleEntities | 否（有形参） | `Entity IGetVisibleEntities( Component2 LpViewComponent, System.int EntityType, System.int ViewEntityCount )` | Obsolete. Superseded by [[IView::IGetVisibleEntities2]]. | `IView::IGetVisibleEntities2` |
| InsertBomTable2 | 否（有形参） | `BomTableAnnotation InsertBomTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.int BomType, System.string Configuration, System.string TableTemplate )` | Obsolete. Superseded by [[IView::InsertBomTable3]]. | `IView::InsertBomTable3` |
| InsertBomTable3 | 否（有形参） | `BomTableAnnotation InsertBomTable3( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.int BomType, System.string Configuration, System.string TableTemplate, System.bool Hidden )` | Obsolete. Superseded by [[IView::InsertBomTable4]]. | `IView::InsertBomTable4` |
| InsertBomTable4 | 否（有形参） | `BomTableAnnotation InsertBomTable4( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.int BomType, System.string Configuration, System.string TableTemplate, System.bool Hidden, System.int IndentedNumberingType, System.bool DetailedCutList )` | Obsolete. Superseded by [[IView::InsertBomTable5]]. | `IView::InsertBomTable5` |
| InsertBomTable5 | 否（有形参） | `System.object InsertBomTable5( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.int BomType, System.string Configuration, System.string TableTemplate, System.bool Hidden, System.int IndentedNumberingType, System.bool DetailedCutList, System.bool DissolvePartLevelRows )` | Obsolete. Superseded by [[IView::InsertBomTable6]]. | `IView::InsertBomTable6` |
| InsertBreak | 否（有形参） | `BreakLine InsertBreak( System.int Orientation, System.double Position1, System.double Position2, System.int Style )` | Obsolete. Superseded by [[IView::InsertBreak2]]. | `IView::InsertBreak2` |
| InsertBreak2 | 否（有形参） | `BreakLine InsertBreak2( System.int Orientation, System.double Position1, System.double Position2, System.int Style, System.int ShapeIntensity )` | Obsolete. Superseded by [[IView::InsertBreak3]]. | `IView::InsertBreak3` |
| InsertHoleTable | 否（有形参） | `HoleTableAnnotation InsertHoleTable( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate )` | Obsolete. Superseded by [[IView::InsertHoleTable2]]. | `IView::InsertHoleTable2` |
| InsertHoleTable2 | 否（有形参） | `HoleTableAnnotation InsertHoleTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )` | Obsolete. Superseded by [[IView::InsertHoleTable3]]. | `IView::InsertHoleTable3` |
| Name | 是（无括号） | `System.string Name {get;}` | Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]. | `IView::GetName2` |
| RootDrawingComponent | 是（无括号） | `DrawingComponent RootDrawingComponent {get;}` | Obsolete. Superseded by [[IView::RootDrawingComponent2]]. | `IView::RootDrawingComponent2` |
| SetDisplayMode | 否（有形参） | `void SetDisplayMode( System.int DisplayIn )` | Obsolete. Superseded by [[IView::SetDisplayMode3]]. | `IView::SetDisplayMode3` |
| SetDisplayMode2 | 否（有形参） | `System.bool SetDisplayMode2( System.int Mode, System.bool Facetted, System.bool Edges )` | Obsolete. Superseded by [[IView::SetDisplayMode3]]. | `IView::SetDisplayMode3` |
| SetDisplayMode3 | 否（有形参） | `System.bool SetDisplayMode3( System.bool UseParent, System.int Mode, System.bool Facetted, System.bool Edges )` | Obsolete. Superseded by [[IView::SetDisplayMode4]]. | `IView::SetDisplayMode4` |
| SetDisplayTangentEdges | 否（有形参） | `void SetDisplayTangentEdges( System.bool DisplayIn )` | Obsolete. Superseded by [[IView::SetDisplayTangentEdges2]]. | `IView::SetDisplayTangentEdges2` |

## 四、指针成员（45 个）—— 原因：`## Returns` 声明 `in-process, unmanaged C++`，pywin32 进程外后端到不了

| 成员名 | 零参? | 签名 | Returns 首行（原文） |
|---|---|---|---|
| IGetAnnotations | 否（有形参） | `Annotation IGetAnnotations( System.int NumAnnotations )` | in-process, unmanaged C++: Pointer to an array of [[annotations]] |
| IGetArcs4 | 是（空括号） | `System.double IGetArcs4()` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetBendLines | 否（有形参） | `SketchSegment IGetBendLines( System.int NumberOfBendLine )` | in-process, unmanaged C++: Pointer to an array of bendlines in a flat-pattern view |
| IGetBodies | 否（有形参） | `Body2 IGetBodies( System.int Count )` | in-process, unmanaged C++: Pointer to an array of [[bodies]] |
| IGetBreakLineInfo2 | 否（有形参） | `System.double IGetBreakLineInfo2( System.int ArraySize )` | in-process, unmanaged C++: Pointer to an array of break line information (see **Remarks**) |
| IGetBreakLines | 否（有形参） | `BreakLine IGetBreakLines( System.int Count )` | in-process, unmanaged C++: Pointer to an array of [[breaks]] |
| IGetBreakOutSections | 否（有形参） | `Feature IGetBreakOutSections( System.int Count )` | In-process, unmanaged C++: Pointer to an array of broken-out section [[features]] |
| IGetCenterLines | 否（有形参） | `Centerline IGetCenterLines( System.int NumCenterLine )` | in-process, unmanaged C++: Pointer to an array of [[centerlines]] |
| IGetCenterMarks | 否（有形参） | `CenterMark IGetCenterMarks( System.int Count )` | in-process, unmanaged C++: Pointer to an array of [[centermarks]] that are features in this view |
| IGetCThreads | 否（有形参） | `CThread IGetCThreads( System.int NumCThread )` | in-process, unmanaged C++: Pointer to an array of [[cosmetic threads]] |
| IGetDatumOrigins | 否（有形参） | `DatumOrigin IGetDatumOrigins( System.int NumDatumOrigin )` | in-process, unmanaged C++: Pointer to an array of [[datum origins]] |
| IGetDatumPoints2 | 是（空括号） | `System.double IGetDatumPoints2()` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetDatumTags | 否（有形参） | `DatumTag IGetDatumTags( System.int NumDatumTag )` | in-process, unmanaged C++: Pointer to an array of [[datum tags]] |
| IGetDatumTargetSyms | 否（有形参） | `DatumTargetSym IGetDatumTargetSyms( System.int NumDatumTargetSym )` | in-process, unmanaged C++: Pointer to an array of [[datum target symbols]] |
| IGetDetailCircles | 否（有形参） | `DetailCircle IGetDetailCircles( System.int NumDetailCircles )` | in-process, unmanaged C++: Pointer to an array of [[detail circles]] |
| IGetDetailCircleStrings | 是（空括号） | `System.string IGetDetailCircleStrings()` | in-process, unmanaged C++: Pointer to an array of strings with one string for each detail circle in the view |
| IGetDimensionIds4 | 是（空括号） | `System.string IGetDimensionIds4()` | in-process, unmanaged C++: Pointer to an array of strings; each string represents one dimension name from the current drawing sheet or current drawing view |
| IGetDisplayDimensions | 否（有形参） | `DisplayDimension IGetDisplayDimensions( System.int NumDisplayDim )` | in-process, unmanaged C++: Pointer to an array of [[display dimensions]] |
| IGetDowelSymbols | 否（有形参） | `DowelSymbol IGetDowelSymbols( System.int NumDowelSymbol )` | in-process, unmanaged C++: Pointer to an array of [[dowel symbols]] |
| IGetEllipses5 | 是（空括号） | `System.double IGetEllipses5()` | in-process, unmanaged C++: Pointer to an array of doubles (**Remarks**) |
| IGetFaceHatches | 否（有形参） | `FaceHatch IGetFaceHatches( System.int NumFacesHatches )` | in-process, unmanaged C++: Pointer to an array of [[face hatches]] |
| IGetFirstCenterOfMass | 是（空括号） | `CenterOfMass IGetFirstCenterOfMass()` | in-process, unmanaged C++: Pointer to [[ICenterOfMass]] |
| IGetFirstRevisionCloud | 是（空括号） | `RevisionCloud IGetFirstRevisionCloud()` | in-process, unmanaged C++: Pointer to an |
| IGetGTols | 否（有形参） | `Gtol IGetGTols( System.int NumGTol )` | in-process, unmanaged C++: Pointer to an array of [[geometric tolerances]] |
| IGetLines4 | 否（有形参） | `System.double IGetLines4( System.short CrossHatchOption, System.int ArraySize )` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetMultiJogLeaders | 否（有形参） | `MultiJogLeader IGetMultiJogLeaders( System.int NumMultiJogLeader )` | in-process, unmanaged C++: Pointer to an array of [[multi-jog leaders]] |
| IGetNotes | 否（有形参） | `Note IGetNotes( System.int NumberOfNotes )` | in-process, unmanaged C++: Pointer to an array of [[notes]] |
| IGetParabolas2 | 是（空括号） | `System.double IGetParabolas2()` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetPolylines7 | 否（有形参） | `System.object IGetPolylines7( System.short CrossHatchOption, System.int ArraySize, out System.double Polylines, System.int EdgeArraySize )` | in-process, unmanaged C++: Pointer to an array of modeling [[edges]] and [[silhouette edges]] corresponding to polylines in the view |
| IGetPolyLinesAndCurves | 否（有形参） | `System.double IGetPolyLinesAndCurves( System.short CrossHatchOption, System.int ArraySize )` | in-process, unmanaged C++: Pointer to an array of lines and parameters in the view (see **Remarks**) |
| IGetProjectionLines | 否（有形参） | `ProjectionArrow IGetProjectionLines( System.int Count )` | in-process, unmanaged C++: Pointer to an array of [[projection lines]] |
| IGetRelatedTangentEdges | 否（有形参） | `Edge IGetRelatedTangentEdges( SketchSegment BendLine, System.int NumOfTangentEdges )` | in-process, unmanaged C++: Pointer to an array of visible tangent [[edges]] for the specified bendline |
| IGetRevisionClouds | 否（有形参） | `RevisionCloud IGetRevisionClouds( System.int NumRevClouds )` | in-process, unmanaged C++: Pointer to an array of [[revision cloud annotation]]s |
| IGetSectionLines | 是（空括号） | `DrSection IGetSectionLines()` | in-process, unmanaged C++: Pointer to an array of [[section lines]] |
| IGetSectionLineStrings | 是（空括号） | `System.string IGetSectionLineStrings()` | in-process, unmanaged C++: Pointer to an array of strings with one string for each section line in the view |
| IGetSFSymbols | 否（有形参） | `SFSymbol IGetSFSymbols( System.int NumSFSymbol )` | in-process, unmanaged C++: Pointer to an array of [[surface finish symbols]] |
| IGetSketchPictures | 否（有形参） | `SketchPicture IGetSketchPictures( System.int Count )` | in-process, unmanaged C++: Pointer to an array of [[ISketchPicture]]s |
| IGetSolidHatchInfo | 否（有形参） | `System.double IGetSolidHatchInfo( System.int ArraySize )` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetSplines3 | 是（空括号） | `System.double IGetSplines3()` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetTableAnnotations | 否（有形参） | `TableAnnotation IGetTableAnnotations( System.int NumTableAnnotation )` | in-process, unmanaged C++: Pointer to an array of [[table annotations]] |
| IGetUserPoints2 | 是（空括号） | `System.double IGetUserPoints2()` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |
| IGetVisibleEntities2 | 否（有形参） | `Entity IGetVisibleEntities2( Component2 LpViewComponent, System.int EntityType, System.int ViewEntityCount )` | In-process, unmanaged C++: Pointer to an array of visible entities |
| IGetWeldBeads | 否（有形参） | `WeldBead IGetWeldBeads( System.int NumWeldBead )` | in-process, unmanaged C++: Pointer to an array of [[weld beads]] |
| IGetWeldSymbols | 否（有形参） | `WeldSymbol IGetWeldSymbols( System.int NumWeldSymbol )` | in-process, unmanaged C++: Pointer to an array of [[weld symbols]] |
| IGetWitnessGeomInfo | 否（有形参） | `System.double IGetWitnessGeomInfo( System.int ArraySize )` | in-process, unmanaged C++: Pointer to an array of doubles (see **Remarks**) |

### ⚠ 指针标记出现、但**不在** `## Returns` 段里的成员

- 共 **1** 个。按上面的字面判据（只看 `## Returns` 段）它们**不计入**指针数。

| 成员名 | 零参? | 签名 | 指针声明出现在哪一段（原文片段） |
|---|---|---|---|
| ISetBodies | 否（有形参） | `void ISetBodies( System.int Count, ref Body2 BodyArray )` | ## Parameters 段：`- **Count**: Number of bodies in a multibody part - **BodyArray**: - in-process, unmanaged C++` |

### 同时属于「废弃」与「指针」的成员

- 无。

## 五、查不到 / 异常形态（逐个列出，不推测）

### 5.1 签名行缺失（真正的异常页）

| 成员名 | 文件 | 页内实际有什么（原文） |
|---|---|---|
| RootDrawingComponent2 | `RootDrawingComponent2.md` | `--- type: IView member: RootDrawingComponent2 kind: property assembly: SolidWorks.Interop.sldworks namespace: SolidWorks.Interop.sldworks category: Drawing Interfaces --- # IView.RootDrawingComponent2 ` |

> 该页只有 YAML 头与 `# IView.RootDrawingComponent2` 标题，**没有描述句、没有 `**Signature**` 行、没有 `## Returns`、没有 `## Remarks`** ⇒ 签名/Returns/Remarks 三项均为「查不到」。不补、不猜。

### 5.2 无 `## Returns` 段的成员

共 **133** 个（Returns 列一律为「查不到」）。这是**页面形态**而非解析失败 —— 这类页的签名返回 `void`，官方自然不写 Returns 段。

`EnumHiddenComponents` · `GetArcs` · `GetArcs2` · `GetArcs3` · `GetCenterMarkCount` · `GetDatumPoints` · `GetDetailCircleCount` · `GetDetailCircleInfo` · `GetDimensionCount` · `GetDimensionCount2` · `GetDimensionCount3` · `GetDimensionDisplayInfo` · `GetDimensionDisplayInfo2` · `GetDimensionDisplayInfo3` · `GetDimensionDisplayInfo4` · `GetDimensionDisplayInfoSize` · `GetDimensionDisplayString` · `GetDimensionDisplayString2` · `GetDimensionDisplayString3` · `GetDimensionIds` · `GetDimensionIds2` · `GetDimensionIds3` · `GetDimensionInfo` · `GetDimensionInfo2` · `GetDimensionInfo3` · `GetDimensionInfo4` · `GetDimensionInfo5` · `GetDimensionString` · `GetDimensionString2` · `GetDimensionString3` · `GetDisplayData` · `GetDisplayData2` · `GetDisplayMode` · `GetDisplayTangentEdges` · `GetEllipses` · `GetEllipses2` · `GetEllipses3` · `GetEllipses4` · `GetFirstAnnotation` · `GetFirstAnnotation2` · `GetFirstBlockInstance` · `GetFirstCustomSymbol` · `GetFirstDisplayDimension` · `GetFirstDisplayDimension2` · `GetFirstDisplayDimension3` · `GetFirstDisplayDimension4` · `GetFirstDisplayDimension6` · `GetFirstMultiJogLeader2` · `GetLineCount` · `GetLines` · `GetLines2` · `GetLines3` · `GetParabolas` · `GetPolyLineCount` · `GetPolyLineCount2` · `GetPolyLineCount3` · `GetPolyLineCount4` · `GetPolylines` · `GetPolylines2` · `GetPolylines3` · `GetPolylines4` · `GetPolylines5` · `GetSectionLineCount` · `GetSectionLineInfo` · `GetSplines` · `GetSplines2` · `GetUserPoints` · `IGetArcs` · `IGetArcs2` · `IGetArcs3` · `IGetDatumPoints` · `IGetDetailCircleInfo` · `IGetDimensionDisplayInfo` · `IGetDimensionDisplayInfo2` · `IGetDimensionDisplayInfo3` · `IGetDimensionDisplayInfo4` · `IGetDimensionDisplayString` · `IGetDimensionDisplayString2` · `IGetDimensionDisplayString3` · `IGetDimensionIds` · `IGetDimensionIds2` · `IGetDimensionIds3` · `IGetDimensionInfo` · `IGetDimensionInfo2` · `IGetDimensionInfo3` · `IGetDimensionInfo4` · `IGetDimensionInfo5` · `IGetDimensionString` · `IGetDimensionString2` · `IGetDimensionString3` · `IGetDisplayData` · `IGetDisplayData2` · `IGetEllipses` · `IGetEllipses2` · `IGetEllipses3` · `IGetEllipses4` · `IGetFirstAnnotation` · `IGetFirstAnnotation2` · `IGetFirstCustomSymbol` · `IGetFirstDisplayDimension` · `IGetFirstDisplayDimension2` · `IGetFirstDisplayDimension3` · `IGetLines` · `IGetLines2` · `IGetLines3` · `IGetParabolas` · `IGetPolylines` · `IGetPolylines2` · `IGetPolylines3` · `IGetPolylines4` · `IGetPolylines5` · `IGetSectionLineInfo` · `IGetSplines` · `IGetSplines2` · `IGetTemporaryAxes` · `IGetUserPoints` · `ImportAnnotations` · `InsertCutListPropertyNote` · `ISetBodies` · `Name` · `RemoveAlignment` · `ResetSketchVisibility` · `RootDrawingComponent2` · `SelectEntity` · `SetDisplayMode` · `SetDisplayMode2` · `SetDisplayTangentEdges` · `SetDisplayTangentEdges2` · `SetLightweightToResolved` · `SetResolvedToLightweight` · `SetVisible` · `UpdateViewDisplayGeometry` · `UseDefaultAlignment`

### 5.3 无 `## Remarks` 段的成员

共 **232** 个（Remarks 列一律为「查不到」）。同样是页面形态：官方该页没写 Remarks，不是抽取失败。

`AlignDrawingView` · `Angle` · `Bodies` · `BreakLineGap` · `Crop` · `Crop2` · `DisableAutoUpdate` · `DisplayState` · `EmphasizeOutline` · `EnumHiddenComponents` · `EnumHiddenComponents2` · `FlipView` · `FocusLocked` · `GetAnnotations` · `GetAnnotationsByType` · `GetArcs` · `GetArcs2` · `GetArcs3` · `GetBaseView` · `GetBendLineCount` · `GetBendLines` · `GetBendNoteTextFormat` · `GetBodiesCount` · `GetBreakOutSections` · `GetCenterMarkCount` · `GetCThreadQuality` · `GetDatumPoints` · `GetDatumPointsCount` · `GetDependentViews` · `GetDesignTableExtent` · `GetDetail` · `GetDetailCircleCount` · `GetDetailCircleInfo` · `GetDetailCircles` · `GetDetailCircleStrings` · `GetDimensionCount` · `GetDimensionCount2` · `GetDimensionCount3` · `GetDimensionCount4` · `GetDimensionDisplayInfo` · `GetDimensionDisplayInfo2` · `GetDimensionDisplayInfo3` · `GetDimensionDisplayInfo4` · `GetDimensionDisplayInfoSize` · `GetDimensionDisplayString` · `GetDimensionDisplayString2` · `GetDimensionDisplayString3` · `GetDimensionIds` · `GetDimensionIds2` · `GetDimensionIds3` · `GetDimensionInfo` · `GetDimensionInfo2` · `GetDimensionInfo3` · `GetDimensionInfo4` · `GetDimensionInfo5` · `GetDimensionString` · `GetDimensionString2` · `GetDimensionString3` · `GetDisplayData` · `GetDisplayData2` · `GetDisplayData4` · `GetDisplayMode` · `GetDisplayMode2` · `GetDisplayTangentEdges` · `GetDisplayTangentEdges2` · `GetEllipses` · `GetEllipses2` · `GetEllipses3` · `GetEllipses4` · `GetFacettedHlrDisplay` · `GetFirstAnnotation` · `GetFirstAnnotation2` · `GetFirstBlockInstance` · `GetFirstCenterLine` · `GetFirstCenterMark` · `GetFirstCenterOfMass` · `GetFirstCThread` · `GetFirstCustomSymbol` · `GetFirstDatumOrigin` · `GetFirstDatumTag` · `GetFirstDatumTargetSym` · `GetFirstDisplayDimension` · `GetFirstDisplayDimension2` · `GetFirstDisplayDimension3` · `GetFirstDisplayDimension4` · `GetFirstDowelSymbol` · `GetFirstGTOL` · `GetFirstMultiJogLeader` · `GetFirstRevisionCloud` · `GetFirstSFSymbol` · `GetFirstTableAnnotation` · `GetFirstWeldBead` · `GetFirstWeldSymbol` · `GetHiddenComponents` · `GetKeepLinkedToBOM` · `GetKeepLinkedToBOMName` · `GetLineCount` · `GetLines` · `GetLines2` · `GetLines3` · `GetMirrorViewOrientation` · `GetNextView` · `GetParabolaCount` · `GetParabolas` · `GetPolyLineCount` · `GetPolyLineCount2` · `GetPolyLineCount3` · `GetPolyLineCount4` · `GetPolylines` · `GetPolylines2` · `GetPolylines3` · `GetPolylines4` · `GetPolylines5` · `GetProjectionArrow` · `GetReferencedModelName` · `GetRevisionCloudCount` · `GetRevisionClouds` · `GetSection` · `GetSectionLineCount` · `GetSectionLineCount2` · `GetSectionLineInfo` · `GetSMBoundaryBoxDisplayData` · `GetSMBoundaryBoxDisplayData2` · `GetSplineCount` · `GetSplines` · `GetSplines2` · `GetUseParentDisplayMode` · `GetUserPoints` · `GetUserPointsCount` · `GetVisible` · `HasDesignTable` · `HiddenEdges` · `IGetArcs` · `IGetArcs2` · `IGetArcs3` · `IGetBaseView` · `IGetDatumPoints` · `IGetDesignTableExtent` · `IGetDetail` · `IGetDetailCircleInfo` · `IGetDetailCircleStrings` · `IGetDimensionDisplayInfo` · `IGetDimensionDisplayInfo2` · `IGetDimensionDisplayInfo3` · `IGetDimensionDisplayInfo4` · `IGetDimensionDisplayString` · `IGetDimensionDisplayString2` · `IGetDimensionDisplayString3` · `IGetDimensionIds` · `IGetDimensionIds2` · `IGetDimensionIds3` · `IGetDimensionInfo` · `IGetDimensionInfo2` · `IGetDimensionInfo3` · `IGetDimensionInfo4` · `IGetDimensionInfo5` · `IGetDimensionString` · `IGetDimensionString2` · `IGetDimensionString3` · `IGetDisplayData` · `IGetDisplayData2` · `IGetEllipses` · `IGetEllipses2` · `IGetEllipses3` · `IGetEllipses4` · `IGetFirstAnnotation` · `IGetFirstAnnotation2` · `IGetFirstCenterOfMass` · `IGetFirstCThread` · `IGetFirstCustomSymbol` · `IGetFirstDatumTag` · `IGetFirstDatumTargetSym` · `IGetFirstDisplayDimension` · `IGetFirstDisplayDimension2` · `IGetFirstDisplayDimension3` · `IGetFirstDowelSymbol` · `IGetFirstGTOL` · `IGetFirstMultiJogLeader` · `IGetFirstRevisionCloud` · `IGetFirstSFSymbol` · `IGetFirstWeldSymbol` · `IGetLines` · `IGetLines2` · `IGetLines3` · `IGetNextView` · `IGetParabolas` · `IGetPolylines` · `IGetPolylines2` · `IGetPolylines3` · `IGetPolylines4` · `IGetPolylines5` · `IGetProjectionArrow` · `IGetSection` · `IGetSectionLineInfo` · `IGetSMBoundaryBoxDisplayData` · `IGetSplines` · `IGetSplines2` · `IGetUserPoints` · `ImportAnnotations` · `InsertBendTable` · `InsertViewAsBlock` · `IsCropped` · `ISelectEntity` · `ISetBodies` · `IsExploded` · `IsFlatPatternView` · `IsLightweight` · `IsModelBreakState` · `IsPerspectiveView` · `LoadModel` · `ModelToViewTransform` · `Name` · `PositionLocked` · `ReplaceViewWithBlock` · `ReplaceViewWithSketch` · `ResetSketchVisibility` · `RootDrawingComponent` · `RootDrawingComponent2` · `ScaleHatchPattern` · `SelectEntity` · `SetDisplayMode` · `SetDisplayMode2` · `SetDisplayTangentEdges` · `SetLightweightToResolved` · `SetMirrorViewOrientation` · `SetResolvedToLightweight` · `SetVisible` · `Sheet` · `ShowModelBreakState` · `ShowSheetMetalBendNotes` · `SuppressState` · `Type`
