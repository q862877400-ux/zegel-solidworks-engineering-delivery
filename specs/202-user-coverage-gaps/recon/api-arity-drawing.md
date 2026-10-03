# 工程图 13 成员 · 官方 arity 表（逐字抄自 C:\swapi）

来源：`C:\swapi\types\<接口>\<成员>.md` 的 `**Signature**:` 行，2026-10-03 逐字抄录。

| 成员 | 接口 | 参数个数 | 参数名序列（按官方顺序） | Obsolete | 后继 | 后继 arity |
|---|---|---|---|---|---|---|
| CreateDrawViewFromModelView3 | IDrawingDoc | 5 | ModelName, ViewName, LocX, LocY, LocZ | 否 | — | — |
| CreateSectionViewAt5 | IDrawingDoc | 7 | X, Y, Z, SectionLabel, Options, ExcludedComponents, SectionDepth | 否 | — | — |
| CreateDetailViewAt4 | IDrawingDoc | 12 | X, Y, Z, Style, Scale1, Scale2, LabelIn, Showtype, FullOutline, JaggedOutline, NoOutline, ShapeIntensity | 否 | — | — |
| InsertBreak | IView | 4 | Orientation, Position1, Position2, Style | 是 | InsertBreak2 → InsertBreak3 | 5 → 6 |
| CreateAuxiliaryViewAt2 | IDrawingDoc | 7 | X, Y, Z, NotAligned, Label, Showarrow, Flip | 否 | — | — |
| SetupSheet5 | IDrawingDoc | 11 | Name, PaperSize, TemplateIn, Scale1, Scale2, FirstAngle, TemplateName, Width, Height, PropertyViewName, RemoveModifiedNotes | 是 | SetupSheet6 | 17 |
| InsertSurfaceFinishSymbol3 | IModelDocExtension | 14 | SymType, LeaderType, LocX, LocY, LocZ, LaySymbol, ArrowType, MachAllowance, OtherVals, ProdMethod, SampleLen, MaxRoughness, MinRoughness, RoughnessSpacing | 否 | — | — |
| InsertDatumTag2 | IModelDoc2 | 0 | （无） | 否 | — | — |
| InsertNote | IModelDoc2 | 1 | Text | 否 | —（未标 Obsolete） | — |
| AutoBalloon5 | IDrawingDoc | 1 | BalloonOptions | 否 | — | — |
| InsertHoleTable2 | IView | 6 | UseAnchorPoint, X, Y, AnchorType, StartValue, TableTemplate | 是 | InsertHoleTable3 | 9 |
| InsertRevisionTable2 | ISheet | 7 | UseAnchorPoint, X, Y, AnchorType, TableTemplate, Shape, AutoUpdateZoomCells | 否 | — | — |
| InsertCenterMark3 | IDrawingDoc | 3 | Style, Propagate, Slot | 否 | — | — |

## 相关辅助入口（官方，供核对用）

| 成员 | 接口 | 参数个数 | 参数名序列 | 来源文件 |
|---|---|---|---|---|
| InsertBreak2 | IView | 5 | Orientation, Position1, Position2, Style, ShapeIntensity | `C:\swapi\types\IView\InsertBreak2.md:14` |
| InsertBreak3 | IView | 6 | Orientation, Position1, Position2, Style, ShapeIntensity, BreakSketchBlocks | `C:\swapi\types\IView\InsertBreak3.md:14` |
| SetupSheet6 | IDrawingDoc | 17 | Name, PaperSize, TemplateIn, Scale1, Scale2, FirstAngle, TemplateName, Width, Height, PropertyViewName, RemoveModifiedNotes, ZoneLeftMargin, ZoneRightMargin, ZoneTopMargin, ZoneBottomMargin, ZoneRow, ZoneCol | `C:\swapi\types\IDrawingDoc\SetupSheet6.md:14` |
| InsertHoleTable3 | IView | 9 | UseAnchorPoint, X, Y, AnchorType, StartValue, Template, TagOrder, TagType, ManualTags | `C:\swapi\types\IView\InsertHoleTable3.md:14` |
| CreateAutoBalloonOptions | IDrawingDoc | 0 | （无） | `C:\swapi\types\IDrawingDoc\CreateAutoBalloonOptions.md:14` |
| InsertNewNote3 | IModelDoc2 | 9 | UpperText, NoLeader, BentLeader, ArrowStyle, LeaderSide, Angle, BalloonStyle, BalloonFit, SmartArrow | `C:\swapi\types\IModelDoc2\InsertNewNote3.md:14` |

## 逐字原文（13 条 · 一字不改）

1. `CreateDrawViewFromModelView3` — `View CreateDrawViewFromModelView3( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )`
2. `CreateSectionViewAt5` — `View CreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents, System.double SectionDepth )`
3. `CreateDetailViewAt4` — `System.object CreateDetailViewAt4( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline, System.bool JaggedOutline, System.bool NoOutline, System.int ShapeIntensity )`
4. `InsertBreak` — `BreakLine InsertBreak( System.int Orientation, System.double Position1, System.double Position2, System.int Style )`
5. `CreateAuxiliaryViewAt2` — `System.object CreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )`
6. `SetupSheet5` — `System.bool SetupSheet5( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes )`
7. `InsertSurfaceFinishSymbol3` — `SFSymbol InsertSurfaceFinishSymbol3( System.int SymType, System.int LeaderType, System.double LocX, System.double LocY, System.double LocZ, System.int LaySymbol, System.int ArrowType, System.string MachAllowance, System.string OtherVals, System.string ProdMethod, System.string SampleLen, System.string MaxRoughness, System.string MinRoughness, System.string RoughnessSpacing )`
8. `InsertDatumTag2` — `System.object InsertDatumTag2()`
9. `InsertNote` — `System.object InsertNote( System.string Text )`
10. `AutoBalloon5` — `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )`
11. `InsertHoleTable2` — `HoleTableAnnotation InsertHoleTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )`
12. `InsertRevisionTable2` — `RevisionTableAnnotation InsertRevisionTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Shape, System.bool AutoUpdateZoomCells )`
13. `InsertCenterMark3` — `CenterMark InsertCenterMark3( System.int Style, System.bool Propagate, System.bool Slot )`
