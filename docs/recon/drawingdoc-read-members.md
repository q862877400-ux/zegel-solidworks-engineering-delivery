# IDrawingDoc 零参可读成员全表

> **来源**：官方源 `C:\swapi\types\IDrawingDoc\*.md`。本表由脚本**逐个真读**该目录下每个成员 `.md` 的全文后抽取
> （不是按文件名猜的）：共读到 **275** 个 `.md`，其中 `_overview.md` 是接口总览页、不算成员，
> 故成员文件 **274** 个 —— 与 `_overview.md` 页头声明的 `property_count: 6` + `method_count: 268`
> = 274 完全对上。
>
> **判据（按 `docs/recon/README.md` 的三条，并**按已知的洞拆开报**）**：
> 1. **废弃**：页头（`**Signature**` 那一行**之前**）出现行首 `Obsolete.` ⇒ 本节记 `obsolete_strict`。
>    ⚠ 另有语义相同但**不以句点结尾**的写法（如 `Obsolete for documents created in SOLIDWORKS 2016 and later.`）
>    只被 `obsolete_loose` 收进 ⇒ **两个数都报，不合并**（见 `docs/recon/family-scan-100-criteria-defects.md` 洞②）。
> 2. **指针**：该页 `## Returns` 段内出现 `in-process, unmanaged C++` ⇒ 主表不收。
>    ⚠ 本仓原判据是**大小写敏感**的字面串匹配；本轮实测官方原文**同时存在大写 `In-process`**
>    （`IView.IGetBreakOutSections` / `IView.IGetVisibleEntities2` 即为此形态）⇒ 本条已改为**大小写不敏感**。
>    ⚠ 官方原文另有笔误 `in-porcess`（`IDrawingDoc.IGetPenInfo`，`process` 拼成 `porcess`）⇒ 一并认上。
>    ⚠ 「标记落在 `## Parameters` 等**非 `## Returns`** 段」的成员**不**计入本条，另有第四节单列。
> 3. **零参**：签名括号内为空 ⇒ `是（空括号）`；签名**根本没有括号** ⇒ `是（无括号）`；
>    括号内非空 ⇒ `否（有形参）`；无签名行 ⇒ `查不到`。
>    ⚠ 「`是（无括号）`」**几乎全是属性**（`5 / 5` 项页头 `kind: property`）⇒
>    与「真·零参方法」**不是一回事**，故统计里**拆两列、永不合并**（洞③）。
>
> ⚠ **本文件不含任何行号** —— 行号会漂。结论一律带可 `grep` 的原文片段。单元格超长（> 400 字符）截断并以 ` …` 标记。

## 一、统计

| 指标 | 数 |
|---|---|
| 共成员数 **N** | **274** |
| 非废弃且非指针 **M**（= 第二节行数） | **160** |
| 其中零参 **K**（严格判据口径） | **78** |
| —— 其中「空括号 `Name()`」**真·零参方法** | 73 |
| —— 其中「无括号（属性形态）」**不是零参方法** | 5 |
| 其余有形参的可用成员 | 81 |
| 可用但签名判不出来 | 1 |
| 废弃（页头行首 `Obsolete.`，**严格**） | 110 |
| 废弃（`Obsolete` 开头即可，**宽松**） | 112（差额 2 见 5.2） |
| 指针（`## Returns` 段含标记，**大小写不敏感 + 认 `in-porcess` 笔误**） | 4 |
| 指针（**全文**任一段含标记） | 4 |
| 同时废弃且指针 | 0 |
| 按页头 `kind:` 统计 property | 6 |
| 按页头 `kind:` 统计 method | 268 |
| 签名行缺失（判为「查不到」） | 1 |
| 空壳页（无签名、无 `## Returns`、无 `## Remarks`） | 1 |
| 无 `## Returns` 段 | 162 |
| 无 `## Remarks` 段 | 174 |
| 指针标记落在 `## Returns` 之外（**不**计入上一行） | 0 |

交叉验算：110 + 4 − 0 + 160 = 274（应等于 N = 274）

## 二、主表 —— 非废弃且非指针的 160 个成员

| 成员名 | 零参? | 签名 | Returns | Remarks 首句 |
|---|---|---|---|---|
| ActivateSheet | 否（有形参） | `System.bool ActivateSheet( System.string Name )` | True if the sheet was activated, false if SOLIDWORKS generated an error | This command makes the specified sheet the active or current sheet, similar to [[IDrawingDoc::SheetNext]] or [[IDrawingDoc::SheetPrevious]]. You can use [[IDrawingDoc::GetCurrentSheet]] or [[IDrawing: … |
| ActivateView | 否（有形参） | `System.bool ActivateView( System.string ViewName )` | True if successful, false if not | This method returns false when trying to activate a drawing sheet. To activate a drawing sheet, use [[IDrawingDoc::ActivateSheet]]. |
| ActiveDrawingView | 是（无括号） | `System.object ActiveDrawingView {get;}` | Currently active drawing view | This property returns the active drawing view, if one is active. If the drawing sheet is active, the property returns NULL and you can use [[IDrawingDoc::GetCurrentSheet]] to get the current sheet for … |
| AddChamferDim | 否（有形参） | `System.object AddChamferDim( System.double X, System.double Y, System.double Z )` | Pointer to the newly created chamfer [[dimension]] | 查不到 |
| AddHoleCallout2 | 否（有形参） | `System.object AddHoleCallout2( System.double X, System.double Y, System.double Z )` | [[Display dimension]] representing the hole callout | When you call this method, the user must click **OK** in the dialog that shows the system-generated hole callout. |
| AddLineStyle | 否（有形参） | `System.bool AddLineStyle( System.string StyleName, System.string StyleDefinition )` | True if successful, false if not | Read about line style options in SOLIDWORKS Help. |
| AlignHorz | 是（空括号） | `void AlignHorz()` | 查不到 | This method aligns the drawing view so that the selected edge is horizontal. |
| AlignOrdinate | 是（空括号） | `void AlignOrdinate()` | 查不到 | 查不到 |
| AlignVert | 是（空括号） | `void AlignVert()` | 查不到 | 查不到 |
| AttachAnnotation | 否（有形参） | `System.bool AttachAnnotation( System.int Option )` | True if attachment is successful, false if not | To attach an annotation to a drawing view: |
| AttachDimensions | 是（空括号） | `void AttachDimensions()` | 查不到 | This method tries to reattach dimensions, for example, in an imported DXF file. |
| AutoBalloon5 | 否（有形参） | `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )` | Array of [[INotes]] | This method automatically inserts BOM balloons for bill of materials items in selected drawing views. If a drawing sheet is selected, BOM balloons are automatically inserted for all of the drawing vie … |
| AutoDimension | 否（有形参） | `System.int AutoDimension( System.int EntitiesToDimension, System.int HorizontalScheme, System.int HorizontalPlacement, System.int VerticalScheme, System.int VerticalPlacement )` | swAutodimStatusSuccess if the view is automatically dimensioned; see [[swAutodimStatus_e]] for reasons for possible failures | This method requires information about the: |
| AutomaticViewUpdate | 是（无括号） | `System.bool AutomaticViewUpdate {get; set;}` | True updates the views automatically, false does not | 查不到 |
| BackgroundProcessingOption | 是（无括号） | `System.int BackgroundProcessingOption {get; set;}` | Background processing option as defined in [[swBackgroundProcessOption_e]] (see **Remarks**) | SOLIDWORKS recommends that you only use this property with [[ISldWorks::IsBackgroundProcessingCompleted]] and [[ISldWorks::EnableBackgroundProcessing]] when you can quickly open a drawing document via … |
| BreakView | 是（空括号） | `void BreakView()` | 查不到 | Use [[IDrawingDoc::InsertBreakHorizontal]] or [[IDrawingDoc::InsertBreakVertical]] to insert break lines to a drawing view. Customize the break by dragging and repositioning the break lines. Then, cal … |
| ChangeComponentLayer | 否（有形参） | `void ChangeComponentLayer( System.string Layername, System.bool AllViews )` | 查不到 | 查不到 |
| ChangeOrdDir | 是（空括号） | `void ChangeOrdDir()` | 查不到 | 查不到 |
| ChangeRefConfigurationOfFlatPatternView | 否（有形参） | `System.bool ChangeRefConfigurationOfFlatPatternView( System.string ModelName, System.string ConfigName )` | True if the configuration was successfully changed, false if not | Before calling this method, you must select the flat-pattern view of the model. |
| Create1stAngleViews2 | 否（有形参） | `System.bool Create1stAngleViews2( System.string ModelName )` | True if successful, false if not | The views honor the automatic scaling behavior as specified in the document setting. |
| Create3rdAngleViews2 | 否（有形参） | `System.bool Create3rdAngleViews2( System.string ModelName )` | True if successful, false if not | The views honor the automatic scaling behavior as specified in the document setting. |
| CreateAngDim4 | 否（有形参） | `System.object CreateAngDim4( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.object P5, System.object P6, System.object TextPoint, System.double TextHeight )` | Newly created display dimension | SOLIDWORKS creates this type of dimension between the two points that you specify. It has no relation to your geometry. |
| CreateAutoBalloonOptions | 是（空括号） | `AutoBalloonOptions CreateAutoBalloonOptions()` | [[IAutoBalloonOptions]] | To automatically create BOM balloons: |
| CreateAuxiliaryViewAt2 | 否（有形参） | `System.object CreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )` | Newly created auxiliary view | 查不到 |
| CreateBreakOutSection | 否（有形参） | `System.bool CreateBreakOutSection( System.double Depth )` | True if the broken-out section was created, false if not | 查不到 |
| CreateCompoundNote | 否（有形参） | `System.object CreateCompoundNote( System.double Height, System.double X, System.double Y, System.double Z )` | Newly created compound note | A compound note is a note that can contain multiple text strings and sketch geometry. |
| CreateConstructionGeometry | 是（空括号） | `void CreateConstructionGeometry()` | 查不到 | This method ignores construction geometry when it generates the solid body. |
| CreateDetailViewAt4 | 否（有形参） | `System.object CreateDetailViewAt4( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline, System.bool JaggedOutline, System.bool NoOutline, System.int ShapeIntensity )` | Detail [[view]] | 查不到 |
| CreateDiamDim4 | 否（有形参） | `System.object CreateDiamDim4( System.object P0, System.object P1, System.object P2, System.object P3, System.object TextPoint, System.double Val, System.double TextHeight )` | Newly created display dimension | SOLIDWORKS creates this type of dimension between the two points you specify. It has no relation to your geometry. |
| CreateDrawViewFromModelView3 | 否（有形参） | `View CreateDrawViewFromModelView3( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )` | Pointer to the newly create [[IView]] object | This method: |
| CreateFlatPatternViewFromModelView3 | 否（有形参） | `View CreateFlatPatternViewFromModelView3( System.string ModelName, System.string ConfigName, System.double LocX, System.double LocY, System.double LocZ, System.bool HideBendLines, System.bool FlipView )` | Flat-pattern [[view]] | 查不到 |
| CreateLayer2 | 否（有形参） | `System.bool CreateLayer2( System.string Layername, System.string LayerDesc, System.int LayerColor, System.int LayerStyle, System.int LayerWidth, System.bool BOn, System.bool BPrint )` | True if the layer was created successfully, false if not | If this layer is not visible, then SOLIDWORKS does not display entities on the layer. |
| CreateLinearDim4 | 否（有形参） | `System.object CreateLinearDim4( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.object TextPoint, System.double Val, System.double Angle, System.double TextHeight )` | Display dimension | SOLIDWORKS creates this type of dimension between the two specified points. The dimension is not related to the geometry. |
| CreateOrdinateDim4 | 否（有形参） | `System.object CreateOrdinateDim4( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.object P5, System.double Val, System.double Angle, System.double TextHeight )` | [[Display dimension]] | SOLIDWORKS creates this type of dimension between the two specified points. The dimension is not related to the geometry. |
| CreateRelativeView | 否（有形参） | `View CreateRelativeView( System.string ModelName, System.double XPos, System.double YPos, System.int ViewDirFront, System.int ViewDirRight )` | [[View]] | Select: |
| CreateSectionView | 是（空括号） | `void CreateSectionView()` | 查不到 | This method prompts the end-user for a name for the new section view. |
| CreateSectionViewAt5 | 否（有形参） | `View CreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents, System.double SectionDepth )` | Section [[view]] | Before calling this method, select the section line or lines to use as a section line. |
| CreateText2 | 否（有形参） | `System.object CreateText2( System.string TextString, System.double TextX, System.double TextY, System.double TextZ, System.double TextHeight, System.double TextAngle )` | Newly created note | The location specifies the position of the upper-left corner of the box containing the text with respect to the lower-left corner of the drawing. |
| CreateUnfoldedViewAt3 | 否（有形参） | `View CreateUnfoldedViewAt3( System.double X, System.double Y, System.double Z, System.bool NotAligned )` | Pointer to the newly created [[IView]] object | 查不到 |
| CreateViewport3 | 否（有形参） | `View CreateViewport3( System.double LowerLeftX, System.double LowerLeftY, System.short SketchSize, System.double Scale )` | Pointer to the newly created [[IView]] object | You cannot set the size of an empty view or resize it. Instead, resizing of the view occurs automatically when you add sketch or model geometry to the view. |
| DeleteAllCosmeticThreads | 是（空括号） | `void DeleteAllCosmeticThreads()` | 查不到 | This method only deletes cosmetic threads in a drawing of an assembly; this method does not delete cosmetic threads in a drawing of a part. |
| DeleteLineStyle | 否（有形参） | `System.bool DeleteLineStyle( System.string StyleName, System.string ReplaceName )` | True if successful, false if not | The following line styles cannot be deleted: |
| Dimensions | 是（空括号） | `void Dimensions()` | 查不到 | This method displays the **Insert Model Items** dialog in the SOLIDWORKS Design user interface. |
| DragModelDimension | 否（有形参） | `void DragModelDimension( System.string ViewName, System.short DropEffect, System.double X, System.double Y, System.double Z )` | The ViewName argument cannot be the current view for the dimension. | 查不到 |
| DrawingViewRotate | 否（有形参） | `System.bool DrawingViewRotate( System.double NewAngle )` | True if successfully rotated, false if not | 查不到 |
| DropDrawingViewFromPalette2 | 否（有形参） | `View DropDrawingViewFromPalette2( System.string PaletteViewName, System.double X, System.double Y, System.double Z )` | [[View]] | The x, y, and z coordinates are in paper space. Thus, the drawing sheet scale is irrelevant. |
| EditCenterMarkProperties | 否（有形参） | `void EditCenterMarkProperties( System.double Angle, System.double Size, System.bool Lines, System.bool DocSettings )` | 查不到 | 查不到 |
| EditOrdinate | 是（空括号） | `void EditOrdinate()` | 查不到 | 查不到 |
| EditSelectedGtol | 是（空括号） | `System.object EditSelectedGtol()` | Existing GTol | 查不到 |
| EditSheet2 | 是（空括号） | `void EditSheet2()` | 查不到 | The drawing sheet in edit mode ensures graphics updates and contains all subsequently created geometry. |
| EditSketch | 是（空括号） | `void EditSketch()` | 查不到 | Creating subsequent geometry resides in this drawing view or sheet. |
| EditTemplate | 是（空括号） | `void EditTemplate()` | 查不到 | Creating subsequent geometry resides on the drawing template. |
| EndDrawing | 是（空括号） | `void EndDrawing()` | 查不到 | Use [[IDrawingDoc::StartDrawing]] and this method to bound your entity creation statements. |
| FeatureByName | 否（有形参） | `System.object FeatureByName( System.string Name )` | Feature | 查不到 |
| FlipSectionLine | 是（空括号） | `void FlipSectionLine()` | 查不到 | SOLIDWORKS creates the corresponding section view, if one exists, on the next rebuild. |
| GenerateViewPaletteViews | 否（有形参） | `System.bool GenerateViewPaletteViews( System.string FileName )` | True if the drawing views are added to the View Palette, false if not | 查不到 |
| GetCurrentSheet | 是（空括号） | `System.object GetCurrentSheet()` | Sheet | The returned [[ISheet]] object includes methods that you can use to access the [[IBomTable]] object. |
| GetDrawingPaletteViewNames | 是（空括号） | `System.object GetDrawingPaletteViewNames()` | Array of the names of the drawing views in the View Palette for the active drawing sheet | If... |
| GetEditSheet | 是（空括号） | `System.bool GetEditSheet()` | True for edit sheet mode, false for edit template mode | Use: |
| GetFirstView | 是（空括号） | `System.object GetFirstView()` | First drawing [[view]] in this drawing document | This method might be useful for starting an iteration through all the drawing views on the current sheet. |
| GetInsertionPoint | 是（空括号） | `System.object GetInsertionPoint()` | Array of 3 doubles (x,y,z) | You might want to use [[ISelectionMgr::GetSelectionPointInSketchSpace2]] to handle multiple selections. |
| GetLineFontCount2 | 是（空括号） | `System.int GetLineFontCount2()` | Number of line fonts supported by this drawing | Each line font is identified by an index in the range [0, (retval -1) ]. |
| GetLineFontId | 否（有形参） | `System.int GetLineFontId( System.int Index )` | Line font ID | SOLIDWORKS uses the line font ID to represent specific line fonts whose names are, for example, Visible, Hidden, Sketch, and so on. |
| GetLineFontInfo2 | 否（有形参） | `System.object GetLineFontInfo2( System.int Index )` | Array containing the line font information (see **Remarks**) | This method breaks down the line font into its individual segment lengths. |
| GetLineFontName2 | 否（有形参） | `System.string GetLineFontName2( System.int Index )` | Line font name | This method can return a font name Hidden, Visible, etc. |
| GetLineStyles | 否（有形参） | `System.bool GetLineStyles( out System.object StyleNameList, out System.object StyleList )` | True if successful, false if not | 查不到 |
| GetPenCount | 是（空括号） | `System.int GetPenCount()` | Number of pens | 查不到 |
| GetPenInfo | 是（空括号） | `System.object GetPenInfo()` | Array containing an array of longs or integers (see Long vs. Integer and see **Remarks**) | The return value is the following array: **[** *font, weight, color* **]** |
| GetSheetCount | 是（空括号） | `System.int GetSheetCount()` | Number of drawing sheets in the drawing | Call this method before call [[IDrawingDoc::IGetSheetNames]] to determine the size of that method's return array. |
| GetSheetNames | 是（空括号） | `System.object GetSheetNames()` | Array containing the names of the drawing sheets in this drawing | 查不到 |
| GetViewCount | 是（空括号） | `System.int GetViewCount()` | Number of views, including the number of sheets, in this drawing document (see **Remarks**) | For example, when: |
| GetViews | 是（空括号） | `System.object GetViews()` | An array of arrays (see **Remarks**) | The return value is an array of arrays with a length equal to the number of sheets in the drawing document. Each of those arrays is a list of views with the first view in the list being the sheet itse … |
| HiddenViewsVisible | 是（无括号） | `System.bool HiddenViewsVisible {get; set;}` | True if views are visible, false if they are hidden | 查不到 |
| HideEdge | 是（空括号） | `void HideEdge()` | 查不到 | 查不到 |
| HideShowDimensions | 是（空括号） | `void HideShowDimensions()` | 查不到 | When SOLIDWORKS displays a suppressed dimension as dimmed, users can select it to turn off suppression. |
| HideShowDrawingViews | 是（空括号） | `void HideShowDrawingViews()` | 查不到 | If this setting is enabled, then SOLIDWORKS shows drawing views that were hidden using [[IDrawingDoc::SuppressView]] with an **X**. |
| IActiveDrawingView | 是（无括号） | `View IActiveDrawingView {get;}` | Pointer to interface object of the currently active drawing [[view]] | This property returns the active drawing view, if one is active. If the drawing sheet is active, the property returns NULL and you can use [[IDrawingDoc::IGetCurrentSheet]] to get the current sheet fo … |
| IAddChamferDim | 否（有形参） | `DisplayDimension IAddChamferDim( System.double X, System.double Y, System.double Z )` | Pointer to the newly created chamfer [[dimension]] | 查不到 |
| IAddHoleCallout2 | 否（有形参） | `DisplayDimension IAddHoleCallout2( System.double X, System.double Y, System.double Z )` | Pointer to [[DisplayDimension]] object representing the hole callout | When you call this method, the user must click **OK** in the dialog that shows the system-generated hole callout. |
| ICreateAngDim4 | 否（有形参） | `DisplayDimension ICreateAngDim4( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, ref System.double P5, ref System.double P6, ref System.double TextPoint, System.double TextHeight )` | Pointer to [[IDisplayDimension]] object | SOLIDWORKS creates this type of dimension between the two points that you specify. It has no relation to your geometry. |
| ICreateAuxiliaryViewAt2 | 否（有形参） | `View ICreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )` | Pointer to the newly created auxiliary [[view]] | 查不到 |
| ICreateCompoundNote | 否（有形参） | `Note ICreateCompoundNote( System.double Height, System.double X, System.double Y, System.double Z )` | Pointer to the newly created compound [[note]] | A compound note is a note that can contain multiple text strings and sketch geometry. |
| ICreateDiamDim4 | 否（有形参） | `DisplayDimension ICreateDiamDim4( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double TextPoint, System.double Val, System.double TextHeight )` | Pointer to the new [[IDisplayDimension]] | SOLIDWORKS creates this type of dimension between the two points you specify. It has no relation to your geometry. |
| ICreateLinearDim4 | 否（有形参） | `DisplayDimension ICreateLinearDim4( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, ref System.double TextPoint, System.double Val, System.double Angle, System.double TextHeight )` | Pointer to [[IDisplayDimension]] object | SOLIDWORKS creates this type of dimension between the two points you specify. It has no relation to your geometry. |
| ICreateOrdinateDim4 | 否（有形参） | `DisplayDimension ICreateOrdinateDim4( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, ref System.double P5, System.double Val, System.double Angle, System.double TextHeight )` | [[Display dimension]] | SOLIDWORKS creates this type of dimension between the two points you specify. It has no relation to your geometry. |
| ICreateSectionViewAt5 | 否（有形参） | `View ICreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.int NumExcludedComponents, ref System.object ExcludedComponents, System.double SectionDepth )` | Section [[view]] | Before calling this method, select the section line or lines to use as a section line. |
| ICreateText2 | 否（有形参） | `Note ICreateText2( System.string TextString, System.double TextX, System.double TextY, System.double TextZ, System.double TextHeight, System.double TextAngle )` | Pointer to the [[note]] | The location specifies the position of the upper-left corner of the box containing the text with respect to the lower-left corner of the drawing. |
| IEditSelectedGtol | 是（空括号） | `Gtol IEditSelectedGtol()` | Pointer to an existing [[GTol]] | 查不到 |
| IFeatureByName | 否（有形参） | `Feature IFeatureByName( System.string Name )` | Pointer to the [[IFeature]] object | 查不到 |
| IGetCurrentSheet | 是（空括号） | `Sheet IGetCurrentSheet()` | Pointer to the [[ISheet]] object | The returned [[ISheet]] object includes methods that you can use to access the [[IBomTable]] object. |
| IGetFirstView | 是（空括号） | `View IGetFirstView()` | Pointer to the first drawing [[view]] in this drawing document | This method might be useful for starting an iteration through all the drawing views on the current sheet. |
| IInsertDowelSymbol | 是（空括号） | `DowelSymbol IInsertDowelSymbol()` | [[Dowel pin symbol]] | 查不到 |
| IInsertMultiJogLeader3 | 否（有形参） | `MultiJogLeader IInsertMultiJogLeader3( System.int PointsCount, ref MathPoint Points, System.int StartPointArrowStyle, System.int EndPointArrowStyle )` | Pointer to the newly created [[multi-jog leader]] | 查不到 |
| INewGtol | 是（空括号） | `Gtol INewGtol()` | Pointer to the newly created [[GTol]] | 查不到 |
| IReorderSheets | 否（有形参） | `System.bool IReorderSheets( System.int SheetCount, ref System.string NewSheetList )` | True if the sheets are reordered per their position in NewSheetList, false if not | 查不到 |
| InsertAngularRunningDim | 是（空括号） | `void InsertAngularRunningDim()` | 查不到 | 查不到 |
| InsertBaseDim | 是（空括号） | `void InsertBaseDim()` | 查不到 | 查不到 |
| InsertBreakHorizontal | 是（空括号） | `void InsertBreakHorizontal()` | 查不到 | To create the break view, use [[IDrawingDoc::BreakView]]. |
| InsertBreakVertical | 是（空括号） | `void InsertBreakVertical()` | 查不到 | To create the break view, use [[IDrawingDoc::BreakView]]. |
| InsertCenterLine2 | 是（空括号） | `Centerline InsertCenterLine2()` | Pointer to the [[ICenterLine]] object | 查不到 |
| InsertCenterMark3 | 否（有形参） | `CenterMark InsertCenterMark3( System.int Style, System.bool Propagate, System.bool Slot )` | [[Center mark]] | Call [[IView::AutoInsertCenterMarks]] to automatically insert center marks in multiple drawing views. |
| InsertCircularNotePattern | 否（有形参） | `System.bool InsertCircularNotePattern( System.double ArcRadius, System.double ArcAngle, System.int PatternNum, System.double PatternSpacing, System.bool PatternRotate, System.string DeleteInstances )` | True if the circular note pattern is created, false if not | 查不到 |
| InsertDowelSymbol | 是（空括号） | `System.object InsertDowelSymbol()` | [[Dowel pin symbol]] | 查不到 |
| InsertGroup | 是（空括号） | `void InsertGroup()` | 查不到 | 查不到 |
| InsertHorizontalOrdinate | 是（空括号） | `void InsertHorizontalOrdinate()` | 查不到 | 查不到 |
| InsertLinearNotePattern | 否（有形参） | `System.bool InsertLinearNotePattern( System.int NumX, System.int NumY, System.double SpacingX, System.double SpacingY, System.double AngleX, System.double AngleY, System.string DeleteInstances )` | True if the linear note pattern is created, false if not | 查不到 |
| InsertModelAnnotations3 | 否（有形参） | `System.object InsertModelAnnotations3( System.int Option, System.int Types, System.bool AllViews, System.bool DuplicateDims, System.bool HiddenFeatureDims, System.bool UsePlacementInSketch )` | Array of inserted [[IAnnotation]] objects | The Option argument was incorrectly documented in versions of the SOLIDWORKS API Help published before SOLIDWORKS 2008 SP3. |
| InsertModelAnnotations4 | 否（有形参） | `System.object InsertModelAnnotations4( System.int Option, System.int Types, System.bool AllViews, System.bool DuplicateDims, System.bool HiddenFeatureDims, System.bool UsePlacementInSketch, System.bool InsertAllAnnotations, System.bool InsertAllReferenceGeometry )` | Array of inserted [[IAnnotation]] objects | 查不到 |
| InsertModelDimensions | 否（有形参） | `void InsertModelDimensions( System.int Option )` | 查不到 | The **Insert Model Items** dialog is not displayed. |
| InsertModelInPredefinedView | 否（有形参） | `System.bool InsertModelInPredefinedView( System.string ModelName )` | True if the model is inserted, false if not | **If you...** |
| InsertMultiJogLeader3 | 否（有形参） | `System.object InsertMultiJogLeader3( System.object Points, System.int StartPointArrowStyle, System.int EndPointArrowStyle )` | Newly created multi-jog leader | 查不到 |
| InsertNewNote2 | 否（有形参） | `void InsertNewNote2( System.string UpperText, System.string LowerText, System.bool NoLeader, System.bool BentLeader, System.short ArrowStyle, System.short LeaderSide, System.double Angle, System.short BalloonStyle, System.short BalloonFit, System.short UpperNoteContent, System.short LowerNoteContent )` | 查不到 | 查不到 |
| InsertOrdinate | 是（空括号） | `void InsertOrdinate()` | 查不到 | 查不到 |
| InsertRefDim | 是（空括号） | `void InsertRefDim()` | 查不到 | Reference dimensions do not drive the model. |
| InsertRevisionCloud | 否（有形参） | `System.object InsertRevisionCloud( System.int CloudShape )` | [[IRevisionCloud]] | After calling this method: |
| InsertRevisionSymbol | 否（有形参） | `Note InsertRevisionSymbol( System.double X, System.double Y )` | Pointer to the newly created [[INote]] object | To attach the revision symbol to entities in the drawing, the end-user must interactively preselect those entities. The revision symbol is then inserted with leaders to those selected entities. If the … |
| InsertTableAnnotation2 | 否（有形参） | `TableAnnotation InsertTableAnnotation2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Rows, System.int Columns )` | Pointer to the [[ITableAnnotation]] object | **If TableTemplate is...** |
| InsertThreadCallout | 是（空括号） | `void InsertThreadCallout()` | 查不到 | 查不到 |
| InsertVerticalOrdinate | 是（空括号） | `void InsertVerticalOrdinate()` | 查不到 | 查不到 |
| InsertWeldSymbol | 否（有形参） | `void InsertWeldSymbol( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric, System.bool FieldWeld, System.bool ShowOtherSide, System.bool DashOnTop, System.bool Peripheral, System.bool HasProcess, System.string ProcessValue )` | 查不到 | Symbol specifies the weld symbol name. You can find a list of weld symbol names in **C:\ProgramData\SolidWorks\SolidWorks 20***nn*\**lang**\**english\gtol.sym**. |
| IsDetailingMode | 是（空括号） | `System.bool IsDetailingMode()` | True if drawing is in detailing mode, false if not | 查不到 |
| IsolateChangedDimensions | 是（空括号） | `void IsolateChangedDimensions()` | 查不到 | This method only works with drawings saved in SOLIDWORKS 2012 and later. |
| LoadLineStyles | 否（有形参） | `System.bool LoadLineStyles( System.string StyleFiles, System.object StyleNameList, System.bool ReplaceExisting )` | True if successful, false if not | 查不到 |
| MakeSectionLine | 是（空括号） | `void MakeSectionLine()` | 查不到 | You must create the sketch lines in the drawing view, not on the drawing sheet. |
| ModifySurfaceFinishSymbol | 否（有形参） | `System.bool ModifySurfaceFinishSymbol( System.int SymType, System.int LeaderType, System.double LocX, System.double LocY, System.double LocZ, System.int LaySymbol, System.int ArrowType, System.string MachAllowance, System.string OtherVals, System.string ProdMethod, System.string SampleLen, System.string MaxRoughness, System.string MinRoughness, System.string RoughnessSpacing )` | 查不到 | 查不到 |
| NewGtol | 是（空括号） | `System.object NewGtol()` | Newly created GTol | 查不到 |
| NewNote | 否（有形参） | `void NewNote( System.string Text, System.double Height )` | 查不到 | 查不到 |
| NewSheet4 | 否（有形参） | `System.bool NewSheet4( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.double ZoneLeftMargin, System.double ZoneRightMargin, System.double ZoneTopMargin, System.double ZoneBottomMargin, System.int ZoneRow, System.int ZoneCol )` | True if drawing sheet creation was successful, false if not | The drawing sheet can be created with zones that annotations in other views can reference. Each zone is referenced by an alphanumeric label that is defined using the Zone Editor. See the SOLIDWORKS He … |
| OnComponentProperties | 是（空括号） | `void OnComponentProperties()` | 查不到 | 查不到 |
| PasteSheet | 否（有形参） | `System.bool PasteSheet( System.int InsertOption, System.int RenameOption )` | True if successful, false if not | Before calling this method, you must: |
| ReorderSheets | 否（有形参） | `System.bool ReorderSheets( System.object NewSheetList )` | True if the sheets are reordered per their position in NewSheetList, false if not | 查不到 |
| ReplaceViewModel | 否（有形参） | `System.bool ReplaceViewModel( System.string NewModelPathName, System.object Views, System.object Instances )` | True if the model is replaced, false if not | This method corresponds to **Tools > Replace Model**. |
| ResolveOutOfDateLightWeightComponents | 是（空括号） | `System.bool ResolveOutOfDateLightWeightComponents()` | True if out-of-date lightweight components are resolved, false if not | This method also resolves a selected out-of-date lightweight component and any out-of-date lightweight sub-components, in a drawing document. |
| RestoreRotation | 是（空括号） | `void RestoreRotation()` | 查不到 | 查不到 |
| SaveLineStyles | 否（有形参） | `System.bool SaveLineStyles( System.string StyleFiles, System.object StyleNameList, System.bool ReplaceExisting )` | True if successful, false if not | 查不到 |
| SetCurrentLayer | 否（有形参） | `System.bool SetCurrentLayer( System.string Layername )` | 查不到 | SOLIDWORKS creates subsequent items on the specified layer. |
| SetLineColor | 否（有形参） | `void SetLineColor( System.int Color )` | 查不到 | 查不到 |
| SetLineStyle | 否（有形参） | `void SetLineStyle( System.string StyleName )` | 查不到 | 查不到 |
| SetLineWidth | 否（有形参） | `void SetLineWidth( System.int Width )` | 查不到 | 查不到 |
| SetLineWidthCustom | 否（有形参） | `void SetLineWidthCustom( System.double Width )` | 查不到 | 查不到 |
| SetSheetsSelected | 否（有形参） | `void SetSheetsSelected( System.object NewSheetList )` | 查不到 | The first drawing sheet in the drawing is automatically included in NewSheetList and need not be specified. |
| SetupSheet6 | 否（有形参） | `System.bool SetupSheet6( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes, System.double ZoneLeftMargin, System.double ZoneRightMargin, System.double ZoneTopMargin, System.double ZoneBottomMargin, System.int ZoneRow, System.int ZoneCol )` | True if drawing sheet setup is successful, false if not | After calling this method, call [[IModelDoc2::ForceRebuild3]] to update any changes to first angle/third angle projections in the drawing views. |
| Sheet | 查不到 | `查不到` | 查不到 | 查不到 |
| SheetNext | 是（空括号） | `void SheetNext()` | 查不到 | 查不到 |
| SheetPrevious | 是（空括号） | `void SheetPrevious()` | 查不到 | 查不到 |
| ShowEdge | 是（空括号） | `void ShowEdge()` | 查不到 | 查不到 |
| SketchDim | 是（空括号） | `void SketchDim()` | 查不到 | 查不到 |
| StartDrawing | 是（空括号） | `void StartDrawing()` | 查不到 | This method automatically disables inferencing to provide faster geometry creation. Use this method and [[IDrawingDoc::EndDrawing]] to bound your entity creation statements. |
| SuppressView | 是（空括号） | `void SuppressView()` | 查不到 | Dependent views are not suppressed. |
| TranslateDrawing | 否（有形参） | `void TranslateDrawing( System.double DeltaX, System.double DeltaY )` | 查不到 | 查不到 |
| UnBreakView | 是（空括号） | `void UnBreakView()` | 查不到 | 查不到 |
| UnsuppressView | 是（空括号） | `void UnsuppressView()` | 查不到 | 查不到 |
| ViewDisplayHidden | 是（空括号） | `void ViewDisplayHidden()` | 查不到 | 查不到 |
| ViewDisplayHiddengreyed | 是（空括号） | `void ViewDisplayHiddengreyed()` | 查不到 | The hidden lines are shown in grey. |
| ViewDisplayShaded | 是（空括号） | `void ViewDisplayShaded()` | 查不到 | 查不到 |
| ViewDisplayWireframe | 是（空括号） | `void ViewDisplayWireframe()` | 查不到 | 查不到 |
| ViewFullPage | 是（空括号） | `void ViewFullPage()` | 查不到 | 查不到 |
| ViewHlrQuality | 是（空括号） | `void ViewHlrQuality()` | 查不到 | 查不到 |
| ViewModelEdges | 是（空括号） | `void ViewModelEdges()` | 查不到 | 查不到 |
| ViewTangentEdges | 是（空括号） | `void ViewTangentEdges()` | 查不到 | 查不到 |

## 三、废弃成员（110 个）—— 原因：页头写明 `Obsolete.`

| 成员名 | 零参? | 页头废弃原文（可 grep） | 签名 |
|---|---|---|---|
| AddCenterMark | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertCenterMark2]]. | `System.bool AddCenterMark( System.double CmSize, System.bool CmShowLines )` |
| AddHoleCallout | 是（空括号） | Obsolete. Superseded by [[IDrawingDoc::AddHoleCallout2]]. | `void AddHoleCallout()` |
| AddOrdinateDimension | 否（有形参） | Obsolete. Superseded by [[IModelDocExtension::AddOrdinateDimension]]. | `System.bool AddOrdinateDimension( System.int DimType, System.double LocX, System.double LocY, System.double LocZ )` |
| AddOrdinateDimension2 | 否（有形参） | Obsolete. Superseded by [[IModelDocExtension::AddOrdinateDimension]]. | `System.int AddOrdinateDimension2( System.int DimType, System.double LocX, System.double LocY, System.double LocZ )` |
| AutoBalloon | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::AutoBalloon3]]. | `System.object AutoBalloon( System.int Layout )` |
| AutoBalloon2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::AutoBalloon3]]. | `System.object AutoBalloon2( System.int Layout, System.bool IgnoreMultiple )` |
| AutoBalloon3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::AutoBalloon4]]. | `System.object AutoBalloon3( System.int Layout, System.bool IgnoreMultiple, System.int Style, System.int Size, System.int UpperTextContent, System.string UpperText, System.int LowerTextContent, System.string LowerText, System.string Layername )` |
| AutoBalloon4 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::AutoBalloon5]]. | `System.object AutoBalloon4( System.int Layout, System.bool IgnoreMultiple, System.int Style, System.int Size, System.int UpperTextContent, System.string UpperText, System.int LowerTextContent, System.string LowerText, System.string Layername, System.bool BalloonsToFaces )` |
| BreakLineSplineCut | 是（空括号） | Obsolete. Superseded by [[IBreakLine::Style]]. | `void BreakLineSplineCut()` |
| BreakLineStraightCut | 是（空括号） | Obsolete. Superseded by [[IBreakLine::Style]]. | `void BreakLineStraightCut()` |
| BreakLineZigZagCut | 是（空括号） | Obsolete. Superseded by [[IBreakLine::Style]]. | `void BreakLineZigZagCut()` |
| CenterMark | 是（空括号） | Obsolete. Not superseded. | `void CenterMark()` |
| Create1stAngleViews | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::1stAngleViews2]]. | `System.bool Create1stAngleViews( System.string ModelName )` |
| Create3rdAngleViews | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::Create3rdAngleViews2]]. | `System.bool Create3rdAngleViews( System.string ModelName )` |
| CreateAngDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateAngDim4]]. | `System.bool CreateAngDim( System.object VP0, System.object VP1, System.object VP2, System.object VP3, System.object VP4, System.object VP5, System.object VP6, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| CreateAngDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateAngDim4]]. | `System.bool CreateAngDim2( System.object VP0, System.object VP1, System.object VP2, System.object VP3, System.object VP4, System.object VP5, System.object VP6, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, System.object VTextPoint )` |
| CreateAngDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateAngDim4]]. | `System.object CreateAngDim3( System.object VP0, System.object VP1, System.object VP2, System.object VP3, System.object VP4, System.object VP5, System.object VP6, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, System.object VTextPoint )` |
| CreateAuxiliaryViewAt | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateAuxiliaryViewAt2]]. | `System.bool CreateAuxiliaryViewAt( System.double X, System.double Y, System.double Z, System.bool NotAligned )` |
| CreateBlockDefinition | 否（有形参） | Obsolete. Superseded by [[ISketchManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `System.object CreateBlockDefinition( System.string Name, System.string XRefFileName, System.bool Instance, System.object Segments, System.object Points, System.object Notes, System.object Dimensions, System.object Blocks )` |
| CreateCustomSymbol | 否（有形参） | Obsolete. Superseded by [[ISkethcManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `System.object CreateCustomSymbol( System.object Segments, System.object Points, System.object Notes )` |
| CreateDetailView | 是（空括号） | Obsolete. Superseded by [[IDrawingDoc::CreateDetailViewAt3]]. | `void CreateDetailView()` |
| CreateDetailViewAt | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDetailViewAt3]]. | `System.bool CreateDetailViewAt( System.double X, System.double Y, System.double Z )` |
| CreateDetailViewAt2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDetailViewAt3]]. | `System.bool CreateDetailViewAt2( System.double X, System.double Y, System.double Z )` |
| CreateDetailViewAt3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDetailViewAt4]]. | `System.object CreateDetailViewAt3( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline )` |
| CreateDiamDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDiamDim4]]. | `System.bool CreateDiamDim( System.double DimVal, System.object VP0, System.object VP1, System.object VP2, System.object VP3, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| CreateDiamDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDiamDim4]]. | `System.bool CreateDiamDim2( System.double DimVal, System.object VP0, System.object VP1, System.object VP2, System.object VP3, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, System.object VTextPoint )` |
| CreateDiamDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDiamDim4]]. | `System.object CreateDiamDim3( System.double DimVal, System.object VP0, System.object VP1, System.object VP2, System.object VP3, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, System.object VTextPoint )` |
| CreateDrawViewFromModelView | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDrawViewFromModelView3]]. | `System.bool CreateDrawViewFromModelView( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )` |
| CreateDrawViewFromModelView2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDrawViewFromModelView3]]. | `View CreateDrawViewFromModelView2( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )` |
| CreateFlatPatternViewFromModelView | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateFlatPatternViewFromModelView2]]. | `System.bool CreateFlatPatternViewFromModelView( System.string ModelName, System.string ConfigName, System.double LocX, System.double LocY, System.double LocZ )` |
| CreateFlatPatternViewFromModelView2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateFlatPatternViewFromModelView3]]. | `System.bool CreateFlatPatternViewFromModelView2( System.string ModelName, System.string ConfigName, System.double LocX, System.double LocY, System.double LocZ, System.bool HideBendLines )` |
| CreateLayer | 否（有形参） | Obsolete. Superseded by IDrawingDoc::CreateLayer2. | `System.bool CreateLayer( System.string Layername, System.string LayerDesc, System.int LayerColor, System.int LayerStyle, System.int LayerWidth, System.bool BOn )` |
| CreateLinearDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateLinearDim4]]. | `System.bool CreateLinearDim( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| CreateLinearDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateLinearDim4]]. | `System.bool CreateLinearDim2( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.double Val, System.int PrimPrec, System.string Text, System.object TextPoint, System.double Angle, System.double TextHeight, System.string Prefix, System.string Suffix, System.string Callout1, System.string Callout2, System.int TolType, System.string TolMin, System.string TolMax, System.int TolPrec, System.double ArrowSize, System.int ArrowStyle, System.int ArrowDir, System.double WitnessGap, System.double WitnessOvershoot, System.bool DualDisplay, System.int DualPrec )` |
| CreateLinearDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateLinearDim4]]. | `System.object CreateLinearDim3( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.double Val, System.int PrimPrec, System.string Text, System.object TextPoint, System.double Angle, System.double TextHeight, System.string Prefix, System.string Suffix, System.string Callout1, System.string Callout2, System.int TolType, System.string TolMin, System.string TolMax, System.int TolPrec, System.double ArrowSize, System.int ArrowStyle, System.int ArrowDir, System.double WitnessGap, System.double WitnessOvershoot, System.bool DualDisplay, System.int DualPrec )` |
| CreateOrdinateDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateOrdinateDim4]]. | `System.bool CreateOrdinateDim( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| CreateOrdinateDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateOrdinateDim4]]. | `System.bool CreateOrdinateDim2( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, System.object P5 )` |
| CreateOrdinateDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateOrdinateDim4]]. | `System.object CreateOrdinateDim3( System.object P0, System.object P1, System.object P2, System.object P3, System.object P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, System.object P5 )` |
| CreateSectionViewAt | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateSectionViewAt4]]. | `System.bool CreateSectionViewAt( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.bool IsOffsetSection )` |
| CreateSectionViewAt2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateSectionViewAt4]]. | `System.object CreateSectionViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.bool IsOffsetSection, System.string Label, System.bool Chgdirection, System.bool Scwithmodel, System.bool Partial, System.bool Dispsurfcut )` |
| CreateSectionViewAt3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateSectionViewAt4]]. | `View CreateSectionViewAt3( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.bool IsOffsetSection, System.string Label, System.bool Chgdirection, System.bool Scwithmodel, System.bool Partial, System.bool Dispsurfcut, System.object ExcludedComponents )` |
| CreateSectionViewAt4 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateSectionViewAt5]]. | `View CreateSectionViewAt4( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents )` |
| CreateText | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateText2]]. | `System.bool CreateText( System.string TextString, System.double TextX, System.double TextY, System.double TextZ, System.double TextHeight, System.double TextAngle )` |
| CreateUnfoldedViewAt | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateUnfoldedViewAt3]]. | `System.bool CreateUnfoldedViewAt( System.double X, System.double Y, System.double Z )` |
| CreateUnfoldedViewAt2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateUnfoldedViewAt3]]. | `System.bool CreateUnfoldedViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned )` |
| CreateViewport | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateViewport3]]. | `System.string CreateViewport( System.double LowerLeftX, System.double LowerLeftY, System.double UpperRightX, System.double UpperRightY, System.short SketchSize )` |
| CreateViewport2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateViewport3]]. | `System.string CreateViewport2( System.double LowerLeftX, System.double LowerLeftY, System.double UpperRightX, System.double UpperRightY, System.short SketchSize, System.double Scale )` |
| DropDrawingViewFromPalette | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::DropDrawingViewFromPalette2]]. | `View DropDrawingViewFromPalette( System.int Layout, System.double X, System.double Y, System.double Z )` |
| EditRebuild | 是（空括号） | Obsolete. Superseded by [[IModelDoc2::EditRebuild3]]. | `void EditRebuild()` |
| EditSheet | 是（空括号） | Obsolete. Superseded by [[IDrawingDoc::EditSheet2]]. | `void EditSheet()` |
| ExplodeBlockInstance | 是（空括号） | Obsolete. Superseded by [[ISketchManager::ExplodeSketchBlockInstance]]. | `System.bool ExplodeBlockInstance()` |
| ExplodeCustomSymbol | 是（空括号） | Obsolete. Superseded by [[ISketchManager::ExplodeSketchBlockInstance]]. | `void ExplodeCustomSymbol()` |
| ForceRebuild | 是（空括号） | Obsolete. Superseded by [[IModel2::ForceRebuild3]]. | `void ForceRebuild()` |
| GetBlockDefinition | 否（有形参） | Obsolete. Superseded by [[SketchManager::GetSketchBlockDefinitions]]. | `BlockDefinition GetBlockDefinition( System.string Name )` |
| GetBlockDefinitionCount | 是（空括号） | Obsolete. Superseded by [[ISketchManager::GetSketchBlockDefinitionCount]]. | `System.int GetBlockDefinitionCount()` |
| GetBlockDefinitions | 是（空括号） | Obsolete. Superseded by [[ISketchManager::GetSketchBlockDefinitions]]. | `System.object GetBlockDefinitions()` |
| GetEditBlock | 是（空括号） | Obsolete. Superseded by [[ISketchManager::EditSketchBlock]] and [[ISketchManager::EndEditSketchBlock]]. | `System.bool GetEditBlock()` |
| GetLineFontCount | 是（空括号） | Obsolete. Superseded by [[IDrawingDoc::GetLineFontCount2]]. | `System.int GetLineFontCount()` |
| GetLineFontInfo | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::GetLineFontInfo2]]. | `System.object GetLineFontInfo( System.int Index )` |
| GetLineFontName | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::GetLineFontName2]]. | `System.string GetLineFontName( System.int Index )` |
| ICreateAngDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateAngDim4]]. | `void ICreateAngDim( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, ref System.double P5, ref System.double P6, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| ICreateAngDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateAngDim4]]. | `void ICreateAngDim2( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, ref System.double P5, ref System.double P6, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, ref System.double TextPoint )` |
| ICreateAngDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateAngDim4]]. | `DisplayDimension ICreateAngDim3( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, ref System.double P5, ref System.double P6, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, ref System.double TextPoint )` |
| ICreateBlockDefinition | 否（有形参） | Obsolete. Superseded by [[ISketchManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `BlockDefinition ICreateBlockDefinition( System.string Name, System.string XRefFileName, System.bool Instance, System.int SegmentCount, ref SketchSegment Segments, System.int PointCount, ref SketchPoint Points, System.int NoteCount, ref Note Notes, System.int DimensionCount, ref DisplayDimension Dimensions, System.int BlockCount, ref BlockInstance Blocks )` |
| ICreateCustomSymbol | 否（有形参） | Obsolete. Superseded by [[ISkethcManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `CustomSymbol ICreateCustomSymbol( System.int SegmentCount, ref SketchSegment Segments, System.int PointCount, ref SketchPoint Points, System.int NoteCount, ref Note Notes )` |
| ICreateDetailViewAt3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::CreateDetailViewAt4]]. | `View ICreateDetailViewAt3( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline )` |
| ICreateDiamDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateDiamDim4]]. | `void ICreateDiamDim( System.double DimValue, ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| ICreateDiamDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateDiamDim4]]. | `void ICreateDiamDim2( System.double DimValue, ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, ref System.double TextPoint )` |
| ICreateDiamDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateDiamDim4]]. | `DisplayDimension ICreateDiamDim3( System.double DimValue, ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, ref System.double TextPoint )` |
| ICreateLinearDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateLinearDim4]]. | `void ICreateLinearDim( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| ICreateLinearDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateLinearDim4]]. | `void ICreateLinearDim2( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, System.double Val, System.int PrimPrec, System.string Text, ref System.double TextPoint, System.double Angle, System.double TextHeight, System.string Prefix, System.string Suffix, System.string Callout1, System.string Callout2, System.int TolType, System.string TolMin, System.string TolMax, System.int TolPrec, System.double ArrowSize, System.int ArrowStyle, System.int ArrowDir, System.double WitnessGap, System.double WitnessOvershoot, System.bool DualDisplay, System.int DualPrecision )` |
| ICreateLinearDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateLinearDim4]]. | `DisplayDimension ICreateLinearDim3( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, System.double Val, System.int PrimPrec, System.string Text, ref System.double TextPoint, System.double Angle, System.double TextHeight, System.string Prefix, System.string Suffix, System.string Callout1, System.string Callout2, System.int TolType, System.string TolMin, System.string TolMax, System.int TolPrec, System.double ArrowSize, System.int ArrowStyle, System.int ArrowDir, System.double WitnessGap, System.double WitnessOvershoot, System.bool DualDisplay, System.int DualPrecision )` |
| ICreateOrdinateDim | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateOrdinateDim4]]. | `void ICreateOrdinateDim( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot )` |
| ICreateOrdinateDim2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateOrdinateDim4]]. | `void ICreateOrdinateDim2( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, ref System.double P5 )` |
| ICreateOrdinateDim3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateOrdinateDim4]]. | `DisplayDimension ICreateOrdinateDim3( ref System.double P0, ref System.double P1, ref System.double P2, ref System.double P3, ref System.double P4, System.double Angle, System.double ArrowSize, System.string Text, System.double TextHeight, System.double WitnessGap, System.double WitnessOvershoot, ref System.double P5 )` |
| ICreateSectionViewAt2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateSectionViewAt4]]. | `View ICreateSectionViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.bool IsOffsetSection, System.string Label, System.bool Chgdirection, System.bool Scwithmodel, System.bool Partial, System.bool Dispsurfcut )` |
| ICreateSectionViewAt3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateSectionViewAt4]]. | `View ICreateSectionViewAt3( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.bool IsOffsetSection, System.string Label, System.bool Chgdirection, System.bool Scwithmodel, System.bool Partial, System.bool Dispsurfcut, System.int NumExcludedComponents, ref System.object PExcludedComponents )` |
| ICreateSectionViewAt4 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::ICreateSectionViewAt5]]. | `View ICreateSectionViewAt4( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.int NumExcludedComponents, ref System.object ExcludedComponents )` |
| IGetBlockDefinitions | 否（有形参） | Obsolete. Superseded by [[SketchManager::GetSketchBlockDefinitions]]. | `BlockDefinition IGetBlockDefinitions( System.int Count )` |
| IInsertCustomSymbol2 | 否（有形参） | Obsolete. Superseded by [[ISketchManager::InsertSketchBlockInstance]]. | `CustomSymbol IInsertCustomSymbol2( System.string FileName )` |
| IInsertMultiJogLeader2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertMultiJogLeader3]]. | `MultiJogLeader IInsertMultiJogLeader2( System.int PointsCount, ref MathPoint Points )` |
| IMakeCustomSymbol2 | 是（空括号） | Obsolete. Superseded by [[ISkethcManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `CustomSymbol IMakeCustomSymbol2()` |
| InsertBlock | 否（有形参） | Obsolete. Superseded by [[ISketchManager::InsertSketchBlockInstance]]. | `BlockInstance InsertBlock( System.string FileName, System.double X, System.double Y, System.double Angle, System.double Scale )` |
| InsertCenterLine | 是（空括号） | Obsolete. Superseded by [[IDrawingDoc::InsertCenterLine2]]. | `System.bool InsertCenterLine()` |
| InsertCenterMark | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertCenterMark2]]. | `CenterMark InsertCenterMark( System.bool UseDoc, System.double Size, System.bool ShowLines, System.double Angle )` |
| InsertCenterMark2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertCenterMark3]]. | `CenterMark InsertCenterMark2( System.int Style, System.bool Propagate )` |
| InsertChainDim | 是（空括号） | Obsolete. Superseded by [[IModelDocExtension::InsertChainDimensions]]. | `void InsertChainDim()` |
| InsertCustomSymbol | 否（有形参） | Obsolete. Superseded by [[ISketchManager::InsertSketchBlockInstance]]. | `void InsertCustomSymbol( System.string SymbolPath )` |
| InsertCustomSymbol2 | 否（有形参） | Obsolete. Superseded by [[ISketchManager::InsertSketchBlockInstance]]. | `System.object InsertCustomSymbol2( System.string FileName )` |
| InsertDatumTag | 是（空括号） | Obsolete. Superseded by [[IModelDoc2::InsertDatumTag2]]. | `void InsertDatumTag()` |
| InsertModelAnnotations | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertModelAnnotations3]]. | `System.bool InsertModelAnnotations( System.int Option, System.bool AllTypes, System.int Types, System.bool AllViews )` |
| InsertModelAnnotations2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertModelAnnotations3]]. | `System.bool InsertModelAnnotations2( System.int Option, System.bool AllTypes, System.int Types, System.bool AllViews, System.bool DuplicateDims, System.bool HiddenFeatureDims )` |
| InsertMultiJogLeader | 是（空括号） | Obsolete. Superseded by [[IDrawingDoc::InsertMultiJogLeader3]]. | `void InsertMultiJogLeader()` |
| InsertMultiJogLeader2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertMultiJogLeader3]]. | `System.object InsertMultiJogLeader2( System.object Points )` |
| InsertNewNote | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertNewNote2]]. | `void InsertNewNote( System.string Text, System.bool NoLeader, System.bool BalloonNote, System.bool BentLeader, System.short ArrowStyle, System.short LeaderSide )` |
| InsertSurfaceFinishSymbol | 否（有形参） | Obsolete. Superseded by [[IModelDocExtension::InsertSurfaceFinishSymbol3]]. | `System.bool InsertSurfaceFinishSymbol( System.int SymType, System.int LeaderType, System.double LocX, System.double LocY, System.double LocZ, System.int LaySymbol, System.int ArrowType, System.string MachAllowance, System.string OtherVals, System.string ProdMethod, System.string SampleLen, System.string MaxRoughness, System.string MinRoughness, System.string RoughnessSpacing )` |
| InsertTableAnnotation | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::InsertTableAnnotation2]]. | `TableAnnotation InsertTableAnnotation( System.double X, System.double Y, System.int AnchorType, System.int Rows, System.int Columns )` |
| MakeBlockDefinition | 否（有形参） | Obsolete. Superseded by [[ISkethcManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `BlockDefinition MakeBlockDefinition( System.string Name, System.string XRefFileName, System.bool Instance )` |
| MakeCustomSymbol | 是（空括号） | Obsolete. Superseded by [[ISkethcManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `void MakeCustomSymbol()` |
| MakeCustomSymbol2 | 是（空括号） | Obsolete. Superseded by [[ISkethcManager::MakeSketchBlockFromFile]], [[ISketchManager::MakeSketchBlockSelected]], and [[ISketchManager::MakeSketchBlockFromSketch]]. | `System.object MakeCustomSymbol2()` |
| NewSheet | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::NewSheet3]]. | `void NewSheet( System.string Name, System.short PaperSize, System.short TemplateIn, System.double Scale1, System.double Scale2 )` |
| NewSheet2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::NewSheet3]]. | `System.bool NewSheet2( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height )` |
| NewSheet3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::NewSheet4]]. | `System.bool NewSheet3( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName )` |
| SaveBlock | 否（有形参） | Obsolete. Superseded by [[ISketchBlockDefinition::Save]]. | `System.bool SaveBlock( System.string FileName )` |
| SetupSheet | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::SetupSheet4]]. | `void SetupSheet( System.string Name, System.short PaperSize, System.short TemplateIn, System.double Scale1, System.double Scale2 )` |
| SetupSheet2 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::SetupSheet4]]. | `void SetupSheet2( System.string Name, System.short PaperSize, System.short TemplateIn, System.double Scale1, System.double Scale2, System.int SkPointsFlag )` |
| SetupSheet3 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::SetupSheet4]]. | `System.bool SetupSheet3( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height )` |
| SetupSheet4 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::SetupSheet5]]. | `System.bool SetupSheet4( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName )` |
| SetupSheet5 | 否（有形参） | Obsolete. Superseded by [[IDrawingDoc::SetupSheet6]]. | `System.bool SetupSheet5( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes )` |
| ToggleGrid | 是（空括号） | Obsolete. Superseded by [[IModelDocExtension::GetUserPreferenceToggle]] and [[IModelDocExtension::SetUserPreferenceToggle]] and swUserPreferenceToggle_e.swGridDisplay. | `void ToggleGrid()` |

## 四、指针成员（4 个）—— 原因：`## Returns` 声明 in-process，pywin32 进程外后端到不了

| 成员名 | 签名 | `## Returns` 原文片段（可 grep） |
|---|---|---|
| IGetInsertionPoint | `System.double IGetInsertionPoint()` | - in-process, unmanaged C++: Pointer to an array of 3 doubles (x,y,z) |
| IGetPenInfo | `System.int IGetPenInfo()` | - in-porcess, unmanaged C++: Pointer to an array of longs (see **Remarks**) |
| IGetSheetNames | `System.string IGetSheetNames( out System.int Count )` | - in-process, unmanaged C++: Pointer to an array containing the names of the drawing sheets in this drawing of size Count |
| IInsertRevisionCloud | `RevisionCloud IInsertRevisionCloud( System.int CloudShape )` | - in-process, unmanaged C++: Pointer to an [[IRevisionCloud]] |

### 4.1 指针标记出现、但**不在** `## Returns` 段里的成员（0 个）

（本接口 **0** 个 —— 全部指针标记都落在 `## Returns` 段内。）

## 五、查不到 / 异常形态（逐个列出，不推测）

### 5.1 空壳页 / 签名行缺失（1 个）

| 成员名 | 文件 | 页内实际有什么（原文） |
|---|---|---|
| Sheet | `Sheet.md` | `--- type: IDrawingDoc member: Sheet kind: property … ---` ＋ `# IDrawingDoc.Sheet` —— **无 `**Signature**` / 无 `## Returns` / 无 `## Remarks`** ⇒ 三项均「查不到」，不补不猜。 |

### 5.2 只被**宽松**判据收进的废弃（2 个）

> 页头写的是 `Obsolete …` 但**不以 `Obsolete.` 开头**（严格判据漏、语义相同）。**两个数都报、不合并**，由主线决定采用哪个。

| 成员名 | 页头原文（可 grep） |
|---|---|
| CreateCompoundNote | Obsolete for documents created in SOLIDWORKS 2016 and later. Superseded by [[ISketchBlockDefinition]] and [[ISketchBlockInstance]]. Creates and returns a compound note. |
| ICreateCompoundNote | Obsolete for documents created in SOLIDWORKS 2016 and later. Creates and returns a compound note. |

### 5.3 无 `## Returns` 段的成员（162 个）

> 判据 2 在这些文件上**无从适用**（多数是 `void` 成员）。列出成员名，以便主线知道「指针数为 0」在这些页上**不是**「确认非指针」。

| 成员名 |
|---|
| AddCenterMark |
| AddHoleCallout |
| AddOrdinateDimension |
| AddOrdinateDimension2 |
| AlignHorz |
| AlignOrdinate |
| AlignVert |
| AttachDimensions |
| AutoBalloon |
| AutoBalloon2 |
| BreakLineSplineCut |
| BreakLineStraightCut |
| BreakLineZigZagCut |
| BreakView |
| CenterMark |
| ChangeComponentLayer |
| ChangeOrdDir |
| Create1stAngleViews |
| Create3rdAngleViews |
| CreateAngDim |
| CreateAngDim2 |
| CreateAngDim3 |
| CreateAuxiliaryViewAt |
| CreateBlockDefinition |
| CreateConstructionGeometry |
| CreateCustomSymbol |
| CreateDetailView |
| CreateDetailViewAt |
| CreateDetailViewAt2 |
| CreateDiamDim |
| CreateDiamDim2 |
| CreateDiamDim3 |
| CreateDrawViewFromModelView |
| CreateDrawViewFromModelView2 |
| CreateFlatPatternViewFromModelView |
| CreateLinearDim |
| CreateLinearDim2 |
| CreateLinearDim3 |
| CreateOrdinateDim |
| CreateOrdinateDim2 |
| CreateOrdinateDim3 |
| CreateSectionView |
| CreateSectionViewAt |
| CreateSectionViewAt2 |
| CreateSectionViewAt3 |
| CreateText |
| CreateUnfoldedViewAt |
| CreateUnfoldedViewAt2 |
| CreateViewport |
| CreateViewport2 |
| DeleteAllCosmeticThreads |
| Dimensions |
| EditCenterMarkProperties |
| EditOrdinate |
| EditRebuild |
| EditSheet |
| EditSheet2 |
| EditSketch |
| EditTemplate |
| EndDrawing |
| ExplodeBlockInstance |
| ExplodeCustomSymbol |
| FlipSectionLine |
| ForceRebuild |
| GetBlockDefinition |
| GetBlockDefinitionCount |
| GetBlockDefinitions |
| GetEditBlock |
| GetLineFontCount |
| GetLineFontInfo |
| GetLineFontName |
| HideEdge |
| HideShowDimensions |
| HideShowDrawingViews |
| ICreateAngDim |
| ICreateAngDim2 |
| ICreateAngDim3 |
| ICreateBlockDefinition |
| ICreateCustomSymbol |
| ICreateDiamDim |
| ICreateDiamDim2 |
| ICreateDiamDim3 |
| ICreateLinearDim |
| ICreateLinearDim2 |
| ICreateLinearDim3 |
| ICreateOrdinateDim |
| ICreateOrdinateDim2 |
| ICreateOrdinateDim3 |
| ICreateSectionViewAt2 |
| ICreateSectionViewAt3 |
| IGetBlockDefinitions |
| IInsertCustomSymbol2 |
| IInsertMultiJogLeader2 |
| IMakeCustomSymbol2 |
| InsertAngularRunningDim |
| InsertBaseDim |
| InsertBlock |
| InsertBreakHorizontal |
| InsertBreakVertical |
| InsertCenterLine |
| InsertCenterMark |
| InsertChainDim |
| InsertCustomSymbol |
| InsertCustomSymbol2 |
| InsertDatumTag |
| InsertGroup |
| InsertHorizontalOrdinate |
| InsertModelAnnotations |
| InsertModelAnnotations2 |
| InsertModelDimensions |
| InsertMultiJogLeader |
| InsertMultiJogLeader2 |
| InsertNewNote |
| InsertNewNote2 |
| InsertOrdinate |
| InsertRefDim |
| InsertSurfaceFinishSymbol |
| InsertTableAnnotation |
| InsertThreadCallout |
| InsertVerticalOrdinate |
| InsertWeldSymbol |
| IsolateChangedDimensions |
| MakeBlockDefinition |
| MakeCustomSymbol |
| MakeCustomSymbol2 |
| MakeSectionLine |
| ModifySurfaceFinishSymbol |
| NewNote |
| NewSheet |
| NewSheet2 |
| OnComponentProperties |
| RestoreRotation |
| SaveBlock |
| SetCurrentLayer |
| SetLineColor |
| SetLineStyle |
| SetLineWidth |
| SetLineWidthCustom |
| SetSheetsSelected |
| SetupSheet |
| SetupSheet2 |
| SetupSheet3 |
| SetupSheet5 |
| Sheet |
| SheetNext |
| SheetPrevious |
| ShowEdge |
| SketchDim |
| StartDrawing |
| SuppressView |
| ToggleGrid |
| TranslateDrawing |
| UnBreakView |
| UnsuppressView |
| ViewDisplayHidden |
| ViewDisplayHiddengreyed |
| ViewDisplayShaded |
| ViewDisplayWireframe |
| ViewFullPage |
| ViewHlrQuality |
| ViewModelEdges |
| ViewTangentEdges |

### 5.4 无 `## Remarks` 段的成员（174 个）

| 成员名 |
|---|
| AddCenterMark |
| AddChamferDim |
| AddHoleCallout |
| AddOrdinateDimension |
| AddOrdinateDimension2 |
| AlignOrdinate |
| AlignVert |
| AutoBalloon |
| AutoBalloon2 |
| AutomaticViewUpdate |
| BreakLineSplineCut |
| BreakLineStraightCut |
| BreakLineZigZagCut |
| ChangeComponentLayer |
| ChangeOrdDir |
| Create1stAngleViews |
| Create3rdAngleViews |
| CreateAngDim |
| CreateAngDim2 |
| CreateAngDim3 |
| CreateAuxiliaryViewAt |
| CreateAuxiliaryViewAt2 |
| CreateBlockDefinition |
| CreateBreakOutSection |
| CreateCustomSymbol |
| CreateDetailView |
| CreateDetailViewAt |
| CreateDetailViewAt2 |
| CreateDetailViewAt3 |
| CreateDetailViewAt4 |
| CreateDiamDim |
| CreateDiamDim2 |
| CreateDiamDim3 |
| CreateDrawViewFromModelView |
| CreateDrawViewFromModelView2 |
| CreateFlatPatternViewFromModelView |
| CreateFlatPatternViewFromModelView2 |
| CreateFlatPatternViewFromModelView3 |
| CreateLinearDim |
| CreateLinearDim2 |
| CreateLinearDim3 |
| CreateOrdinateDim |
| CreateOrdinateDim2 |
| CreateOrdinateDim3 |
| CreateSectionViewAt |
| CreateSectionViewAt2 |
| CreateSectionViewAt3 |
| CreateText |
| CreateUnfoldedViewAt |
| CreateUnfoldedViewAt2 |
| CreateUnfoldedViewAt3 |
| CreateViewport |
| CreateViewport2 |
| DragModelDimension |
| DrawingViewRotate |
| DropDrawingViewFromPalette |
| EditCenterMarkProperties |
| EditOrdinate |
| EditRebuild |
| EditSelectedGtol |
| ExplodeBlockInstance |
| ExplodeCustomSymbol |
| FeatureByName |
| ForceRebuild |
| GenerateViewPaletteViews |
| GetBlockDefinition |
| GetBlockDefinitionCount |
| GetBlockDefinitions |
| GetEditBlock |
| GetLineFontCount |
| GetLineFontInfo |
| GetLineFontName |
| GetLineStyles |
| GetPenCount |
| GetSheetNames |
| HiddenViewsVisible |
| HideEdge |
| IAddChamferDim |
| ICreateAngDim |
| ICreateAngDim2 |
| ICreateAngDim3 |
| ICreateAuxiliaryViewAt2 |
| ICreateBlockDefinition |
| ICreateCustomSymbol |
| ICreateDetailViewAt3 |
| ICreateDiamDim |
| ICreateDiamDim2 |
| ICreateDiamDim3 |
| ICreateLinearDim |
| ICreateLinearDim2 |
| ICreateLinearDim3 |
| ICreateOrdinateDim |
| ICreateOrdinateDim2 |
| ICreateOrdinateDim3 |
| ICreateSectionViewAt2 |
| ICreateSectionViewAt3 |
| IEditSelectedGtol |
| IFeatureByName |
| IGetBlockDefinitions |
| IGetInsertionPoint |
| IInsertCustomSymbol2 |
| IInsertDowelSymbol |
| IInsertMultiJogLeader2 |
| IInsertMultiJogLeader3 |
| IMakeCustomSymbol2 |
| INewGtol |
| IReorderSheets |
| InsertAngularRunningDim |
| InsertBaseDim |
| InsertBlock |
| InsertCenterLine |
| InsertCenterLine2 |
| InsertCenterMark |
| InsertCenterMark2 |
| InsertCircularNotePattern |
| InsertCustomSymbol |
| InsertCustomSymbol2 |
| InsertDatumTag |
| InsertDowelSymbol |
| InsertGroup |
| InsertHorizontalOrdinate |
| InsertLinearNotePattern |
| InsertModelAnnotations |
| InsertModelAnnotations2 |
| InsertModelAnnotations4 |
| InsertMultiJogLeader |
| InsertMultiJogLeader2 |
| InsertMultiJogLeader3 |
| InsertNewNote |
| InsertNewNote2 |
| InsertOrdinate |
| InsertSurfaceFinishSymbol |
| InsertTableAnnotation |
| InsertThreadCallout |
| InsertVerticalOrdinate |
| IsDetailingMode |
| LoadLineStyles |
| MakeBlockDefinition |
| MakeCustomSymbol |
| MakeCustomSymbol2 |
| ModifySurfaceFinishSymbol |
| NewGtol |
| NewNote |
| NewSheet |
| NewSheet2 |
| NewSheet3 |
| OnComponentProperties |
| ReorderSheets |
| RestoreRotation |
| SaveBlock |
| SaveLineStyles |
| SetLineColor |
| SetLineStyle |
| SetLineWidth |
| SetLineWidthCustom |
| SetupSheet |
| SetupSheet2 |
| SetupSheet3 |
| Sheet |
| SheetNext |
| SheetPrevious |
| ShowEdge |
| SketchDim |
| ToggleGrid |
| TranslateDrawing |
| UnBreakView |
| UnsuppressView |
| ViewDisplayHidden |
| ViewDisplayShaded |
| ViewDisplayWireframe |
| ViewFullPage |
| ViewHlrQuality |
| ViewModelEdges |
| ViewTangentEdges |

