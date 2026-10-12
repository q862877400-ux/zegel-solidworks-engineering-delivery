# ISheet 零参可读成员全表

> **来源**：官方源 `C:\swapi\types\ISheet\*.md`。本表由脚本**逐个真读**该目录下每个成员 `.md` 的全文后抽取
> （不是按文件名猜的）：共读到 **54** 个 `.md`，其中 `_overview.md` 是接口总览页、不算成员，
> 故成员文件 **53** 个 —— 与 `_overview.md` 页头声明的 `property_count: 8` + `method_count: 45`
> = 53 完全对上。
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
>    ⚠ 「`是（无括号）`」**几乎全是属性**（`7 / 7` 项页头 `kind: property`）⇒
>    与「真·零参方法」**不是一回事**，故统计里**拆两列、永不合并**（洞③）。
>
> ⚠ **本文件不含任何行号** —— 行号会漂。结论一律带可 `grep` 的原文片段。单元格超长（> 400 字符）截断并以 ` …` 标记。

## 一、统计

| 指标 | 数 |
|---|---|
| 共成员数 **N** | **53** |
| 非废弃且非指针 **M**（= 第二节行数） | **39** |
| 其中零参 **K**（严格判据口径） | **18** |
| —— 其中「空括号 `Name()`」**真·零参方法** | 11 |
| —— 其中「无括号（属性形态）」**不是零参方法** | 7 |
| 其余有形参的可用成员 | 20 |
| 可用但签名判不出来 | 1 |
| 废弃（页头行首 `Obsolete.`，**严格**） | 13 |
| 废弃（`Obsolete` 开头即可，**宽松**） | 13（差额 0 见 5.2） |
| 指针（`## Returns` 段含标记，**大小写不敏感 + 认 `in-porcess` 笔误**） | 2 |
| 指针（**全文**任一段含标记） | 2 |
| 同时废弃且指针 | 1 |
| 按页头 `kind:` 统计 property | 8 |
| 按页头 `kind:` 统计 method | 45 |
| 签名行缺失（判为「查不到」） | 1 |
| 空壳页（无签名、无 `## Returns`、无 `## Remarks`） | 1 |
| 无 `## Returns` 段 | 14 |
| 无 `## Remarks` 段 | 29 |
| 指针标记落在 `## Returns` 之外（**不**计入上一行） | 0 |

交叉验算：13 + 2 − 1 + 39 = 53（应等于 N = 53）

## 二、主表 —— 非废弃且非指针的 39 个成员

| 成员名 | 零参? | 签名 | Returns | Remarks 首句 |
|---|---|---|---|---|
| CustomPropertyView | 是（无括号） | `System.string CustomPropertyView {get; set;}` | Name of the drawing view from which to get the custom information | You can also use [[IDrawingDoc::SetupSheet4]] to set the name of the drawing view to use to set the custom information for this drawing sheet. |
| FocusLocked | 是（无括号） | `System.bool FocusLocked {get; set;}` | True if focus locked on sheet, false if not | 查不到 |
| GetDrawingZone | 否（有形参） | `System.string GetDrawingZone( System.double X, System.double Y )` | Name of the drawing zone | 查不到 |
| GetID | 是（空括号） | `System.int GetID()` | ID of the drawing sheet | Each drawing sheet: |
| GetMagneticLines | 是（空括号） | `System.object GetMagneticLines()` | Array of [[IMagneticLine]]s | Call [[ISheet::GetMagneticLinesCount]] to get the number of magnetic lines returned by this method. |
| GetMagneticLinesCount | 是（空括号） | `System.int GetMagneticLinesCount()` | Number of magnetic lines on this sheet | 查不到 |
| GetName | 是（空括号） | `System.string GetName()` | Sheet name | 查不到 |
| GetProperties2 | 是（空括号） | `System.object GetProperties2()` | Array of doubles (see **Remarks**) | The return value is the following array of eight doubles: |
| GetSheetFormatName | 是（空括号） | `System.string GetSheetFormatName()` | Name of the sheet format | If the sheet does not have a sheet format, an empty string is returned. |
| GetSize | 否（有形参） | `System.int GetSize( out System.double Width, out System.double Height )` | Paper size as defined in [[swDwgPaperSizes_e]] | 查不到 |
| GetTemplateName | 是（空括号） | `System.string GetTemplateName()` | Template path name | To ensure a correct return value, open the document in edit mode. |
| GetTemplateSketch | 是（空括号） | `Sketch GetTemplateSketch()` | [[Sketch]] | 查不到 |
| GetViews | 是（空括号） | `System.object GetViews()` | Array of drawing [[views]] on this sheet | If this sheet is: |
| GetZoneMargin | 否（有形参） | `System.double GetZoneMargin( System.int ZoneMargin )` | Zone margin | 查不到 |
| GetZoneSizeDistribution | 否（有形参） | `System.int GetZoneSizeDistribution( out System.int Rows, out System.int Columns )` | Zone size distribution as defined by [[swZoneSizeDistribution_e]] | 查不到 |
| GetZoneSizeRegion | 是（空括号） | `System.int GetZoneSizeRegion()` | Type of zone size region as defined by [[swRegionType_e]] | 查不到 |
| IPageSetup | 是（无括号） | `PageSetup IPageSetup {get;}` | [[Page setup]] | Page setup values are overridden on a sheet by sheet basis. |
| InsertFamilyTable | 否（有形参） | `System.object InsertFamilyTable( System.bool AttachToAnchorPoint, System.double X, System.double Y, System.string ModelName, System.string TableTemplateName, System.int DimColumnType, System.bool UseAllConfigs, System.object ConfigArray, System.int ItemNumberStart, System.int ItemNumberIncrement, System.bool FollowConfigTreeOrder )` | [[IFamilyTableAnnotation]] | Family tables display the variations in part and assembly configurations or custom properties in table format. |
| InsertMagneticLine | 否（有形参） | `MagneticLine InsertMagneticLine( MathPoint StartPoint, MathPoint EndPoint )` | [[IMagneticLine]] | 查不到 |
| InsertRevisionTable2 | 否（有形参） | `RevisionTableAnnotation InsertRevisionTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Shape, System.bool AutoUpdateZoomCells )` | [[Revision table]] or null if a revision table already exists | By default, the revision table templates are in install_dir\**lang**\language and have a filename extension of **.sldrevtbt**. The template and table must be of the same type. For example, you must sp … |
| InsertTitleBlock | 否（有形参） | `TitleBlock InsertTitleBlock( System.object Notes )` | [[Title block]] | The Notes parameter can contain one or more more notes or nothing. If the Notes parameter contains a note, or notes, then the note, or notes, is expected to be a Dispatch pointer, or pointers, to the … |
| IsLoaded | 是（空括号） | `System.bool IsLoaded()` | True if the sheet is loaded, false if not | 查不到 |
| PageSetup | 是（无括号） | `System.object PageSetup {get;}` | [[Page setup]] | Page setup values are overridden on a sheet by sheet basis. |
| ReloadTemplate | 否（有形参） | `System.int ReloadTemplate( System.bool KeepNoteChanges )` | Status as defined in [[swReloadTemplateResult_e]] | If new notes are added or existing notes modified or deleted on the sheet format, then specifying true for KeepNoteChanges: |
| RevisionTable | 是（无括号） | `RevisionTableAnnotation RevisionTable {get;}` | [[Revision table annotation]] | 查不到 |
| SaveFormat | 否（有形参） | `System.bool SaveFormat( System.string FileName )` | True if the sheet format is saved to the specified file, false if not | You must specify the path, file name, and filename extension to which to save the sheet format. Use .**slddrt** for the filename extension. |
| SetAsTableAnchor | 否（有形参） | `System.object SetAsTableAnchor( System.int TableType )` | [[ITableAnchor]] | Before calling this method, you must call: |
| SetName | 否（有形参） | `void SetName( System.string NameIn )` | 查不到 | 查不到 |
| SetProperties2 | 否（有形参） | `void SetProperties2( System.int PaperSz, System.int Templ, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.double Width, System.double Height, System.bool SameCustomPropAsSheetInDocProp )` | 查不到 | If you... |
| SetScale | 否（有形参） | `System.bool SetScale( System.double Numerator, System.double Denominator, System.bool ScaleAnnoPosition, System.bool ScaleAnnoTextHeight )` | True if the scale is set, false if not | You can get the two scale values from the sheet by using [[ISheet::GetProperties]] or [[ISheet::IGetProperties]]. |
| SetSheetFormatName | 否（有形参） | `System.bool SetSheetFormatName( System.string Name )` | True if the name of the sheet format is set, false if not | The name that you specify must: |
| SetSize | 否（有形参） | `System.bool SetSize( System.int Size, System.double Width, System.double Height )` | True if the size of the sheet is set, false if not | 查不到 |
| SetTemplateName | 否（有形参） | `void SetTemplateName( System.string NameIn )` | 查不到 | If you want to use: |
| SetZoneMargin | 否（有形参） | `System.bool SetZoneMargin( System.int ZoneMarginType, System.double MarginValue )` | True if zone margin successfully set, false if not | 查不到 |
| SetZoneSizeDistribution | 否（有形参） | `System.bool SetZoneSizeDistribution( System.int Type, System.int Rows, System.int Column )` | True if zone size distribution successfully set, false if not | 查不到 |
| SetZoneSizeRegion | 否（有形参） | `System.bool SetZoneSizeRegion( System.int RegionType )` | True of zone size region successfully set, false if not | 查不到 |
| SheetFormatVisible | 是（无括号） | `System.bool SheetFormatVisible {get; set;}` | True if the sheet format is visible, false if not | 查不到 |
| TableAnchor | 查不到 | `查不到` | 查不到 | 查不到 |
| TitleBlock | 是（无括号） | `TitleBlock TitleBlock {get;}` | [[Title block]] in this sheet | Only one title block can exist in a sheet. This property gets that title block, if it exists. |

## 三、废弃成员（13 个）—— 原因：页头写明 `Obsolete.`

| 成员名 | 零参? | 页头废弃原文（可 grep） | 签名 |
|---|---|---|---|
| CreateOLEObject | 否（有形参） | Obsolete. Superseded by [[IModelDocExtension::CreateOLEObject]] and [[IModelDocExtension::ICreateOLEObject]]. | `System.bool CreateOLEObject( System.int Aspect, System.object Position, System.object Buffer )` |
| GetBomTable | 是（空括号） | Obsolete. Superseded by [[IView::GetBOMTable]]. | `System.object GetBomTable()` |
| GetOLEObjectCount | 是（空括号） | Obsolete. Superseded by [[IModelDocExtension::GetOLEObjectCount]]. | `System.int GetOLEObjectCount()` |
| GetOLEObjectData | 否（有形参） | Obsolete. Superseded by [[ISwOLEObject]]. | `System.object GetOLEObjectData( System.int Index )` |
| GetOLEObjectSettings | 否（有形参） | Obsolete. Superseded by I[[SwOLEObjectAspect]], [[ISwOLEObject::Boundaries]], [[ISWOLEObject::IGetBoundaries]], [[ISwOLEObject::ISetBoundaries]], [[ISwOLEObject::IGetBuffer]], and [[ISwOLEObject::Buffer]]. | `System.object GetOLEObjectSettings( System.int Index, out System.int ByteCount, out System.int Aspect )` |
| GetProperties | 是（空括号） | Obsolete. Superseded by [[ISheet::GetProperties2]]. | `System.object GetProperties()` |
| ICreateOLEObject | 否（有形参） | Obsolete. Superseded by [[IModelDocExtension::CreateOLEObject]] and [[IModelDocExtension::ICreateOLEObject]]. | `System.bool ICreateOLEObject( System.int Aspect, ref System.double Position, System.int ByteCount, ref System.byte Buffer )` |
| IGetBomTable | 是（空括号） | Obsolete. Superseded by [[IView::IGetBomTable]]. | `BomTable IGetBomTable()` |
| IGetOLEObjectData | 否（有形参） | Obsolete. Superseded by [[ISwOLEObject]]. | `System.bool IGetOLEObjectData( System.int Index, out System.byte Buffer )` |
| IGetOLEObjectSettings | 否（有形参） | Obsolete. Superseded by [[ISwOLEObjectAspect]], [[ISwOLEObject::Boundaries]], [[ISWOLEObject::IGetBoundaries]], [[ISwOLEObject::ISetBoundaries]], [[ISwOLEObject::IGetBuffer]], and [[ISwOLEObject::Buffer]]. | `System.bool IGetOLEObjectSettings( System.int Index, out System.int ByteCount, out System.int Aspect, out System.double Position )` |
| IGetProperties | 是（空括号） | Obsolete. Superseded by [[ISheet::GetProperties2]]. | `System.double IGetProperties()` |
| InsertRevisionTable | 否（有形参） | Obsolete. Superseded by [[ISheet::InsertRevisionTable2]]. | `RevisionTableAnnotation InsertRevisionTable( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate )` |
| SetProperties | 否（有形参） | Obsolete. Superseded by [[ISheet::SetProperties2]]. | `void SetProperties( System.int PaperSz, System.int Templ, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.double Width, System.double Height )` |

## 四、指针成员（2 个）—— 原因：`## Returns` 声明 in-process，pywin32 进程外后端到不了

| 成员名 | 签名 | `## Returns` 原文片段（可 grep） |
|---|---|---|
| IGetMagneticLines | `MagneticLine IGetMagneticLines( System.int Count )` | - In-process, unmanaged C++: Array of [[IMagneticLine]]s |
| IGetProperties | `System.double IGetProperties()` | - in-process, unmanaged C++: Array of doubles (see **Remarks**) |

### 4.1 指针标记出现、但**不在** `## Returns` 段里的成员（0 个）

（本接口 **0** 个 —— 全部指针标记都落在 `## Returns` 段内。）

## 五、查不到 / 异常形态（逐个列出，不推测）

### 5.1 空壳页 / 签名行缺失（1 个）

| 成员名 | 文件 | 页内实际有什么（原文） |
|---|---|---|
| TableAnchor | `TableAnchor.md` | `--- type: ISheet member: TableAnchor kind: property … ---` ＋ `# ISheet.TableAnchor` —— **无 `**Signature**` / 无 `## Returns` / 无 `## Remarks`** ⇒ 三项均「查不到」，不补不猜。 |

### 5.2 只被**宽松**判据收进的废弃（0 个）

（本接口 **0** 个 —— 严格与宽松结果完全一致。）

### 5.3 无 `## Returns` 段的成员（14 个）

> 判据 2 在这些文件上**无从适用**（多数是 `void` 成员）。列出成员名，以便主线知道「指针数为 0」在这些页上**不是**「确认非指针」。

| 成员名 |
|---|
| CreateOLEObject |
| GetBomTable |
| GetOLEObjectCount |
| GetOLEObjectData |
| GetOLEObjectSettings |
| ICreateOLEObject |
| IGetBomTable |
| IGetOLEObjectData |
| IGetOLEObjectSettings |
| SetName |
| SetProperties |
| SetProperties2 |
| SetTemplateName |
| TableAnchor |

### 5.4 无 `## Remarks` 段的成员（29 个）

| 成员名 |
|---|
| CreateOLEObject |
| FocusLocked |
| GetBomTable |
| GetDrawingZone |
| GetMagneticLinesCount |
| GetName |
| GetOLEObjectCount |
| GetOLEObjectData |
| GetOLEObjectSettings |
| GetSize |
| GetTemplateSketch |
| GetZoneMargin |
| GetZoneSizeDistribution |
| GetZoneSizeRegion |
| ICreateOLEObject |
| IGetBomTable |
| IGetMagneticLines |
| IGetOLEObjectData |
| IGetOLEObjectSettings |
| InsertMagneticLine |
| IsLoaded |
| RevisionTable |
| SetName |
| SetSize |
| SetZoneMargin |
| SetZoneSizeDistribution |
| SetZoneSizeRegion |
| SheetFormatVisible |
| TableAnchor |

