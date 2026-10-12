# 全量接口台账 —— `C:\swapi\types\` 566 个接口 / 11557 个成员

> **这份文件是「铁律 4（签名三源互证）」的机器底座**：以前是逐处手工对签名，
> 现在**每个接口一行**，七个数一次给全。
>
> **来源与口径**
> - **源**：`C:\swapi\types\` 的 **566** 个接口目录 / **12123** 份 `.md`
>   （其中 **11557** 个成员页 + 566 个 `_overview.md`）。
> - **生成方式**：**逐页真读**（不是按文件名猜）。**本批不用 LLM** —— 用支线已验证过的解析器
>   （`IView` 那一份曾与已发布产物逐项对上）。**566 行交叉验算 0 失败，parse 错误 0**。
> - **判据**（沿用 `docs/recon/README.md`，并按已报的洞拆开）：
>   1. **废弃**：页头（`**Signature**` 之前）出现行首 `Obsolete.` ⇒ `废弃(严)`；
>      另有语义相同但不以句点收尾的写法 ⇒ `废弃(宽)`。**两个数都报，不合并。**
>   2. **指针**：`## Returns` 段含 `in-process, unmanaged C++`（**大小写不敏感**，且认官方笔误
>      `in-porcess`）⇒ `指针(R)`。**全文**任一段含该标记 ⇒ `指针(全)`。**两个数都报。**
>   3. **可用** = 成员数 − 废弃(严) − 指针(R)。**每行都做了这个交叉验算**（0 失败）。
>   4. **零参法** = 可用成员里签名形如 `Name()` 的（**真方法**）；
>      **无括号属性** = 可用成员里签名形如 `T Name {get;set;}` 的（★ **不是零参方法**）。
>      **两列永不合并**（合并会让 `IDSPBRMaterial` 那类整列退化）。
>
> ⚠ **本文件不含行号**。

## 一、总计

| 指标 | 数 |
|---|---|
| 接口目录 | **566** |
| `.md` 总数 | **12123** |
| 成员页（不含 `_overview.md`） | **11557** |
| —— 页头 `kind: property` | 3514 |
| —— 页头 `kind: method` | 8043 |
| **废弃（严格）** | **1642** |
| 废弃（宽松，含不以句点收尾的写法） | 1668 |
| **指针（仅 `## Returns` 段）** | **520** |
| 指针（**全文**任一段） | 739 |
| **可用**（= 成员 − 废弃严 − 指针R） | **9395** |
| —— 其中**零参真方法**（`Name()`） | 2502 |
| —— 其中**无括号属性**（★ 不是零参方法） | 3320 |
| 签名行缺失 | 106 |
| 空壳页（无签名/无 Returns/无 Remarks） | 106 |
| 无 `## Returns` 段 | 2489 |
| 无 `## Remarks` 段 | 5118 |

交叉验算：1642 + 520 + 9395 = 11557（= 成员数 11557，逐行验过）。

## 二、★ 回归：`IView` 与已发布产物**逐项对上**

已发布的 `docs/recon/iview-read-members.md` 是这一套判据的**回归基准**（改判据必须拿它验）：

| 量 | 本台账 | 已发布 | |
|---|---|---|---|
| 成员 | 461 | 461 | ✅ |
| 废弃（严） | 149 | 149 | ✅ |
| 指针（Returns） | 45 | 45 | ✅ |
| 可用 | 267 | 267 | ✅ |
| 零参真方法 | 169 | 169 | ✅ |
| 无括号属性 | 31 | 31 | ✅ |

## 三、逐接口台账（566 行）

| 接口 | 成员 | property | method | 废弃(严) | 废弃(宽) | 指针(R) | 指针(全) | 可用 | 零参法 | 无括号属性 | 签名缺 | 空壳 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `IModelDoc2` | 721 | 31 | 690 | 344 | 344 | 8 | 8 | 369 | 177 | 23 | 7 | 7 |
| `IView` | 461 | 34 | 427 | 149 | 149 | 45 | 46 | 267 | 169 | 31 | 1 | 1 |
| `IModelDocExtension` | 342 | 27 | 315 | 44 | 44 | 10 | 18 | 288 | 73 | 17 | 9 | 9 |
| `ISldWorks` | 333 | 20 | 313 | 75 | 77 | 7 | 9 | 251 | 53 | 18 | 0 | 0 |
| `IFeatureManager` | 286 | 23 | 263 | 116 | 116 | 1 | 5 | 169 | 28 | 22 | 1 | 1 |
| `IDrawingDoc` | 274 | 6 | 268 | 110 | 112 | 4 | 4 | 160 | 73 | 5 | 1 | 1 |
| `IBody2` | 220 | 10 | 210 | 43 | 43 | 10 | 14 | 167 | 50 | 7 | 0 | 0 |
| `IAssemblyDoc` | 196 | 8 | 188 | 65 | 65 | 6 | 6 | 125 | 44 | 8 | 0 | 0 |
| `IComponent2` | 165 | 20 | 145 | 32 | 32 | 10 | 12 | 123 | 48 | 15 | 1 | 1 |
| `IPartDoc` | 144 | 4 | 140 | 52 | 52 | 7 | 8 | 85 | 30 | 4 | 0 | 0 |
| `IDisplayDimension` | 141 | 38 | 103 | 28 | 28 | 0 | 1 | 113 | 41 | 36 | 1 | 1 |
| `INote` | 127 | 17 | 110 | 13 | 31 | 15 | 15 | 99 | 43 | 17 | 0 | 0 |
| `IFeature` | 125 | 10 | 115 | 24 | 24 | 5 | 8 | 96 | 42 | 10 | 0 | 0 |
| `IModeler` | 124 | 1 | 123 | 34 | 34 | 0 | 1 | 90 | 3 | 1 | 0 | 0 |
| `IGtol` | 121 | 2 | 119 | 17 | 17 | 21 | 21 | 83 | 35 | 2 | 0 | 0 |
| `IFace2` | 120 | 7 | 113 | 6 | 6 | 16 | 19 | 98 | 48 | 7 | 0 | 0 |
| `ISketch` | 104 | 4 | 100 | 28 | 28 | 17 | 17 | 59 | 43 | 2 | 0 | 0 |
| `IRenderMaterial` | 103 | 82 | 21 | 9 | 9 | 1 | 1 | 93 | 5 | 79 | 0 | 0 |
| `IAnnotation` | 101 | 18 | 83 | 17 | 17 | 4 | 5 | 80 | 37 | 18 | 0 | 0 |
| `ISketchManager` | 92 | 9 | 83 | 12 | 12 | 2 | 4 | 78 | 10 | 7 | 0 | 0 |
| `ITableAnnotation` | 85 | 26 | 59 | 10 | 10 | 0 | 0 | 75 | 6 | 18 | 8 | 8 |
| `IMacroFeatureData` | 84 | 19 | 65 | 7 | 7 | 0 | 17 | 77 | 17 | 18 | 0 | 0 |
| `IConfiguration` | 82 | 20 | 62 | 9 | 9 | 2 | 4 | 71 | 21 | 18 | 1 | 1 |
| `ISurface` | 82 | 11 | 71 | 17 | 17 | 4 | 4 | 61 | 22 | 10 | 0 | 0 |
| `IModelView` | 75 | 31 | 44 | 11 | 15 | 0 | 0 | 64 | 23 | 22 | 0 | 0 |
| `IWizardHoleFeatureData2` | 75 | 61 | 14 | 1 | 1 | 1 | 1 | 73 | 5 | 60 | 0 | 0 |
| `ISimpleFilletFeatureData2` | 70 | 24 | 46 | 0 | 0 | 7 | 14 | 63 | 8 | 23 | 1 | 1 |
| `ICurve` | 68 | 4 | 64 | 15 | 15 | 5 | 7 | 48 | 16 | 4 | 0 | 0 |
| `IExtrudeFeatureData2` | 67 | 20 | 47 | 9 | 9 | 2 | 5 | 56 | 7 | 20 | 0 | 0 |
| `ISelectionMgr` | 62 | 3 | 59 | 29 | 29 | 1 | 1 | 32 | 4 | 2 | 1 | 1 |
| `ILinearPatternFeatureData` | 60 | 37 | 23 | 1 | 1 | 4 | 8 | 55 | 9 | 37 | 0 | 0 |
| `IDisplayData` | 55 | 0 | 55 | 12 | 12 | 10 | 10 | 33 | 10 | 0 | 0 | 0 |
| `ILocalLinearPatternFeatureData` | 54 | 38 | 16 | 1 | 1 | 2 | 4 | 51 | 6 | 38 | 0 | 0 |
| `IBaseFlangeFeatureData` | 53 | 39 | 14 | 7 | 7 | 2 | 2 | 44 | 6 | 33 | 0 | 0 |
| `ISheet` | 53 | 8 | 45 | 13 | 13 | 2 | 2 | 38 | 11 | 7 | 1 | 1 |
| `ISweepFeatureData` | 53 | 29 | 24 | 8 | 8 | 3 | 5 | 42 | 11 | 27 | 0 | 0 |
| `IDimension` | 52 | 10 | 42 | 20 | 20 | 2 | 3 | 30 | 7 | 8 | 0 | 0 |
| `IDSPBRMaterial` | 52 | 52 | 0 | 0 | 0 | 0 | 0 | 52 | 0 | 52 | 0 | 0 |
| `IDrSection` | 51 | 9 | 42 | 2 | 2 | 3 | 5 | 46 | 22 | 9 | 0 | 0 |
| `ISFSymbol` | 51 | 7 | 44 | 4 | 4 | 7 | 7 | 40 | 18 | 5 | 0 | 0 |
| `ILoftFeatureData` | 48 | 28 | 20 | 0 | 0 | 4 | 7 | 44 | 7 | 28 | 0 | 0 |
| `IEdge` | 47 | 1 | 46 | 8 | 8 | 2 | 3 | 37 | 18 | 1 | 0 | 0 |
| `ITessellation` | 46 | 13 | 33 | 4 | 4 | 5 | 6 | 37 | 4 | 13 | 0 | 0 |
| `ICircularPatternFeatureData` | 45 | 24 | 21 | 1 | 1 | 4 | 8 | 40 | 7 | 24 | 0 | 0 |
| `IVariableFilletFeatureData2` | 45 | 11 | 34 | 2 | 2 | 2 | 4 | 41 | 4 | 11 | 0 | 0 |
| `IWeldSymbol` | 45 | 0 | 45 | 0 | 0 | 7 | 7 | 38 | 19 | 0 | 0 | 0 |
| `ICurveDrivenPatternFeatureData` | 44 | 27 | 17 | 0 | 0 | 4 | 8 | 40 | 5 | 27 | 0 | 0 |
| `IEdgeFlangeFeatureData` | 42 | 30 | 12 | 2 | 2 | 1 | 2 | 39 | 4 | 29 | 0 | 0 |
| `IModelViewManager` | 42 | 5 | 37 | 8 | 8 | 0 | 0 | 34 | 11 | 5 | 0 | 0 |
| `ISketchBlockDefinition` | 41 | 3 | 38 | 2 | 2 | 10 | 10 | 29 | 21 | 3 | 0 | 0 |
| `IDesignTable` | 40 | 12 | 28 | 1 | 1 | 0 | 0 | 39 | 17 | 10 | 2 | 2 |
| `ISw3DPrinter` | 40 | 0 | 40 | 0 | 0 | 0 | 0 | 40 | 26 | 0 | 0 | 0 |
| `IPropertyManagerPage2Handler9` | 37 | 0 | 37 | 0 | 0 | 0 | 0 | 37 | 9 | 0 | 0 | 0 |
| `ISketchSegment` | 37 | 7 | 30 | 4 | 4 | 3 | 3 | 30 | 18 | 7 | 0 | 0 |
| `IBoundaryBossFeatureData` | 36 | 14 | 22 | 0 | 0 | 0 | 0 | 36 | 2 | 13 | 1 | 1 |
| `IDatumTargetSym` | 36 | 0 | 36 | 0 | 0 | 0 | 0 | 36 | 14 | 0 | 0 | 0 |
| `IRayTraceRendererOptions` | 36 | 35 | 1 | 1 | 1 | 0 | 0 | 35 | 1 | 34 | 0 | 0 |
| `IFillPatternFeatureData` | 35 | 33 | 2 | 0 | 0 | 0 | 0 | 35 | 1 | 33 | 0 | 0 |
| `ISectionViewData` | 35 | 31 | 4 | 0 | 0 | 0 | 0 | 35 | 0 | 31 | 0 | 0 |
| `ISwScene` | 35 | 28 | 7 | 0 | 0 | 0 | 0 | 35 | 4 | 28 | 0 | 0 |
| `ITablePatternFeatureData` | 35 | 10 | 25 | 1 | 1 | 5 | 10 | 29 | 9 | 10 | 0 | 0 |
| `IThreadFeatureData` | 35 | 30 | 5 | 0 | 0 | 0 | 0 | 35 | 3 | 30 | 0 | 0 |
| `IDatumTag` | 34 | 4 | 30 | 0 | 0 | 0 | 0 | 34 | 12 | 4 | 0 | 0 |
| `IDetailCircle` | 34 | 6 | 28 | 0 | 0 | 4 | 4 | 30 | 14 | 6 | 0 | 0 |
| `ISketchSpline` | 34 | 10 | 24 | 4 | 4 | 2 | 2 | 28 | 7 | 10 | 0 | 0 |
| `IMate2` | 33 | 15 | 18 | 1 | 1 | 1 | 1 | 31 | 8 | 13 | 1 | 1 |
| `IOneBendFeatureData` | 33 | 22 | 11 | 9 | 9 | 2 | 2 | 22 | 4 | 16 | 0 | 0 |
| `ICamera` | 32 | 19 | 13 | 0 | 0 | 0 | 0 | 32 | 5 | 19 | 0 | 0 |
| `IMeasure` | 32 | 30 | 2 | 0 | 0 | 0 | 0 | 32 | 0 | 30 | 0 | 0 |
| `IDragOperator` | 31 | 16 | 15 | 0 | 0 | 0 | 0 | 31 | 2 | 15 | 1 | 1 |
| `IMotionStudy` | 31 | 5 | 26 | 0 | 0 | 0 | 0 | 31 | 13 | 5 | 0 | 0 |
| `ISketchPatternFeatureData` | 31 | 13 | 18 | 1 | 1 | 4 | 6 | 26 | 6 | 13 | 0 | 0 |
| `ISurfExtrudeFeatureData` | 31 | 12 | 19 | 0 | 0 | 0 | 0 | 31 | 1 | 12 | 0 | 0 |
| `ISweptFlangeFeatureData` | 31 | 23 | 8 | 0 | 0 | 0 | 0 | 31 | 5 | 23 | 0 | 0 |
| `ICoordinateSystemFeatureData` | 30 | 8 | 22 | 0 | 0 | 6 | 9 | 24 | 10 | 8 | 0 | 0 |
| `ISimpleHoleFeatureData2` | 30 | 20 | 10 | 0 | 0 | 1 | 1 | 29 | 2 | 20 | 0 | 0 |
| `ISMGussetFeatureData` | 30 | 28 | 2 | 0 | 0 | 0 | 0 | 30 | 1 | 28 | 0 | 0 |
| `IBomFeature` | 29 | 16 | 13 | 1 | 1 | 2 | 3 | 26 | 5 | 16 | 0 | 0 |
| `IChamferFeatureData2` | 29 | 12 | 17 | 0 | 0 | 3 | 6 | 26 | 3 | 12 | 0 | 0 |
| `ILocalCircularPatternFeatureData` | 29 | 14 | 15 | 1 | 1 | 2 | 4 | 26 | 5 | 14 | 0 | 0 |
| `ILoop2` | 29 | 0 | 29 | 0 | 0 | 2 | 4 | 27 | 16 | 0 | 0 | 0 |
| `IRevolveFeatureData2` | 28 | 12 | 16 | 0 | 0 | 2 | 4 | 26 | 6 | 12 | 0 | 0 |
| `IConvertSolidFeatureData` | 27 | 20 | 7 | 0 | 0 | 0 | 0 | 27 | 4 | 20 | 0 | 0 |
| `IFrame` | 27 | 3 | 24 | 6 | 6 | 2 | 2 | 19 | 4 | 3 | 0 | 0 |
| `IHoleSeriesFeatureData2` | 27 | 14 | 13 | 0 | 0 | 2 | 2 | 25 | 5 | 12 | 2 | 2 |
| `ISketchBlockInstance` | 27 | 12 | 15 | 1 | 1 | 2 | 2 | 24 | 7 | 11 | 0 | 0 |
| `ISketchPoint` | 27 | 8 | 19 | 8 | 8 | 1 | 1 | 18 | 8 | 8 | 0 | 0 |
| `ISplitLineFeatureData` | 27 | 12 | 15 | 0 | 0 | 4 | 8 | 23 | 6 | 12 | 0 | 0 |
| `ICosmeticWeldBeadFeatureData` | 26 | 14 | 12 | 2 | 2 | 0 | 0 | 24 | 4 | 14 | 0 | 0 |
| `ICustomPropertyManager` | 26 | 3 | 23 | 12 | 12 | 1 | 1 | 13 | 1 | 3 | 0 | 0 |
| `IDocumentSpecification` | 26 | 26 | 0 | 0 | 0 | 0 | 0 | 26 | 0 | 26 | 0 | 0 |
| `ILibraryFeatureData` | 26 | 4 | 22 | 5 | 5 | 5 | 6 | 16 | 4 | 4 | 0 | 0 |
| `ISpring` | 26 | 24 | 2 | 0 | 0 | 0 | 0 | 26 | 2 | 24 | 0 | 0 |
| `IStructuralMemberFeatureData` | 26 | 13 | 13 | 0 | 0 | 3 | 5 | 23 | 5 | 12 | 1 | 1 |
| `IBomTableAnnotation` | 25 | 1 | 24 | 3 | 3 | 4 | 4 | 18 | 3 | 1 | 0 | 0 |
| `ICommandGroup` | 25 | 18 | 7 | 6 | 6 | 0 | 0 | 19 | 1 | 12 | 2 | 2 |
| `IEquationMgr` | 25 | 11 | 14 | 1 | 1 | 0 | 2 | 24 | 4 | 6 | 5 | 5 |
| `IExplodeStep` | 25 | 10 | 15 | 0 | 0 | 1 | 1 | 24 | 5 | 10 | 0 | 0 |
| `ILocalCurvePatternFeatureData` | 25 | 20 | 5 | 0 | 0 | 0 | 0 | 25 | 3 | 20 | 0 | 0 |
| `IMirrorComponentFeatureData` | 25 | 23 | 2 | 0 | 0 | 0 | 0 | 25 | 1 | 23 | 0 | 0 |
| `IPageSetup` | 25 | 19 | 6 | 1 | 1 | 0 | 0 | 24 | 2 | 18 | 0 | 0 |
| `IChainPatternFeatureData` | 24 | 20 | 4 | 0 | 0 | 0 | 0 | 24 | 3 | 20 | 0 | 0 |
| `ICommandManager` | 24 | 2 | 22 | 3 | 3 | 2 | 3 | 19 | 2 | 2 | 0 | 0 |
| `IDraftFeatureData2` | 24 | 10 | 14 | 0 | 0 | 3 | 5 | 21 | 5 | 10 | 0 | 0 |
| `IFlatPatternFeatureData` | 24 | 13 | 11 | 2 | 2 | 1 | 2 | 21 | 2 | 12 | 0 | 0 |
| `IMiterFlangeFeatureData` | 24 | 15 | 9 | 1 | 1 | 1 | 2 | 22 | 3 | 15 | 0 | 0 |
| `IMoveFaceFeatureData` | 24 | 9 | 15 | 0 | 0 | 3 | 6 | 21 | 3 | 9 | 0 | 0 |
| `IDimensionTolerance` | 23 | 4 | 19 | 3 | 3 | 0 | 0 | 20 | 10 | 4 | 0 | 0 |
| `IFillSurfaceFeatureData` | 23 | 6 | 17 | 0 | 0 | 2 | 4 | 21 | 5 | 6 | 0 | 0 |
| `IMidSurface3` | 23 | 0 | 23 | 0 | 0 | 1 | 3 | 22 | 8 | 0 | 0 | 0 |
| `IPartingLineFeatureData` | 23 | 8 | 15 | 0 | 0 | 3 | 5 | 20 | 4 | 8 | 0 | 0 |
| `IPropertyManagerPage2` | 23 | 2 | 21 | 8 | 8 | 0 | 0 | 15 | 1 | 2 | 0 | 0 |
| `IPropertyManagerPageSelectionbox` | 23 | 12 | 11 | 0 | 0 | 1 | 1 | 22 | 4 | 10 | 2 | 2 |
| `ISheetMetalFeatureData` | 23 | 11 | 12 | 7 | 7 | 0 | 0 | 16 | 2 | 7 | 0 | 0 |
| `IDimXpertPart` | 22 | 1 | 21 | 0 | 0 | 2 | 2 | 20 | 8 | 1 | 0 | 0 |
| `IInterferenceDetectionMgr` | 22 | 9 | 13 | 0 | 0 | 2 | 3 | 20 | 5 | 9 | 0 | 0 |
| `IJogFeatureData` | 22 | 14 | 8 | 0 | 0 | 1 | 2 | 21 | 3 | 14 | 0 | 0 |
| `IMirrorPartFeatureData` | 22 | 16 | 6 | 0 | 0 | 0 | 0 | 22 | 5 | 16 | 0 | 0 |
| `IRefPlaneFeatureData` | 22 | 16 | 6 | 1 | 1 | 1 | 2 | 20 | 2 | 11 | 4 | 4 |
| `ISimulationForceFeatureData` | 22 | 14 | 8 | 0 | 0 | 0 | 0 | 22 | 0 | 14 | 0 | 0 |
| `ICenterMark` | 21 | 10 | 11 | 0 | 0 | 0 | 0 | 21 | 4 | 10 | 0 | 0 |
| `IConfigurationManager` | 21 | 7 | 14 | 2 | 2 | 0 | 2 | 19 | 1 | 7 | 0 | 0 |
| `IDerivedPartFeatureData` | 21 | 16 | 5 | 0 | 0 | 0 | 0 | 21 | 3 | 16 | 0 | 0 |
| `IDimPatternFeatureData` | 21 | 1 | 20 | 0 | 0 | 0 | 0 | 21 | 4 | 1 | 0 | 0 |
| `IImportDxfDwgData` | 21 | 8 | 13 | 0 | 0 | 0 | 0 | 21 | 0 | 2 | 6 | 6 |
| `IMirrorPatternFeatureData` | 21 | 7 | 14 | 1 | 1 | 3 | 6 | 17 | 5 | 7 | 0 | 0 |
| `IPackAndGo` | 21 | 8 | 13 | 1 | 1 | 0 | 3 | 20 | 2 | 8 | 0 | 0 |
| `ISafeArrayUtility` | 21 | 0 | 21 | 0 | 0 | 0 | 0 | 21 | 0 | 0 | 0 | 0 |
| `ISketchEllipse` | 21 | 0 | 21 | 10 | 10 | 0 | 0 | 11 | 11 | 0 | 0 | 0 |
| `ISketchHatch` | 21 | 9 | 12 | 6 | 6 | 0 | 0 | 15 | 6 | 8 | 0 | 0 |
| `ITabAndSlotGroupData` | 21 | 21 | 0 | 0 | 0 | 0 | 0 | 21 | 0 | 21 | 0 | 0 |
| `IBomTable` | 20 | 0 | 20 | 4 | 4 | 1 | 1 | 15 | 9 | 0 | 0 | 0 |
| `ICallout` | 20 | 14 | 6 | 1 | 1 | 0 | 0 | 19 | 0 | 9 | 5 | 5 |
| `IMBD3DPdfData` | 20 | 8 | 12 | 0 | 0 | 0 | 0 | 20 | 6 | 8 | 0 | 0 |
| `IMoveCopyBodyFeatureData` | 20 | 13 | 7 | 0 | 0 | 1 | 2 | 19 | 2 | 13 | 0 | 0 |
| `IPrintSpecification` | 20 | 17 | 3 | 0 | 0 | 0 | 0 | 20 | 2 | 17 | 0 | 0 |
| `ISimulationMotorFeatureData` | 20 | 14 | 6 | 0 | 0 | 0 | 0 | 20 | 0 | 14 | 0 | 0 |
| `ISplineParamData` | 20 | 12 | 8 | 0 | 0 | 0 | 3 | 20 | 0 | 12 | 0 | 0 |
| `IAutoBalloonOptions` | 19 | 19 | 0 | 0 | 0 | 0 | 0 | 19 | 0 | 19 | 0 | 0 |
| `ICosmeticThreadFeatureData` | 19 | 14 | 5 | 0 | 0 | 1 | 1 | 18 | 2 | 14 | 0 | 0 |
| `IDrawingComponent` | 19 | 9 | 10 | 0 | 0 | 0 | 0 | 19 | 4 | 9 | 0 | 0 |
| `IHoleTable` | 19 | 10 | 9 | 0 | 0 | 1 | 1 | 18 | 6 | 9 | 1 | 1 |
| `ICalloutVariable` | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0 | 18 | 0 | 0 |
| `ICoEdge` | 18 | 0 | 18 | 3 | 3 | 1 | 1 | 14 | 12 | 0 | 0 | 0 |
| `IDerivedPatternFeatureData` | 18 | 7 | 11 | 1 | 1 | 2 | 4 | 15 | 3 | 7 | 0 | 0 |
| `IGussetFeatureData` | 18 | 14 | 4 | 0 | 0 | 0 | 0 | 18 | 1 | 14 | 0 | 0 |
| `IHemFeatureData` | 18 | 10 | 8 | 0 | 0 | 1 | 2 | 17 | 3 | 10 | 0 | 0 |
| `ILoftedBendsFeatureData` | 18 | 11 | 7 | 0 | 0 | 1 | 2 | 17 | 3 | 11 | 0 | 0 |
| `IMassProperty2` | 18 | 13 | 5 | 0 | 0 | 0 | 0 | 18 | 2 | 12 | 1 | 1 |
| `IMathVector` | 18 | 2 | 16 | 0 | 0 | 1 | 1 | 17 | 4 | 1 | 0 | 0 |
| `ISketchArc` | 18 | 0 | 18 | 6 | 6 | 1 | 1 | 11 | 10 | 0 | 0 | 0 |
| `IStackedBalloonOptions` | 18 | 18 | 0 | 0 | 0 | 0 | 0 | 18 | 0 | 18 | 0 | 0 |
| `ISurfaceExtendFeatureData` | 18 | 9 | 9 | 0 | 0 | 2 | 4 | 16 | 3 | 9 | 0 | 0 |
| `IVertex` | 18 | 0 | 18 | 0 | 0 | 3 | 4 | 15 | 7 | 0 | 0 | 0 |
| `IWeldmentBeadFeatureData` | 18 | 6 | 12 | 0 | 0 | 1 | 4 | 17 | 1 | 2 | 4 | 4 |
| `IAnnotationView` | 17 | 6 | 11 | 2 | 2 | 2 | 2 | 13 | 7 | 5 | 0 | 0 |
| `IHelixFeatureData` | 17 | 12 | 5 | 0 | 0 | 0 | 0 | 17 | 0 | 12 | 0 | 0 |
| `IPartingSurfaceFeatureData` | 17 | 11 | 6 | 0 | 0 | 1 | 2 | 16 | 3 | 11 | 0 | 0 |
| `ISimulationSpringFeatureData` | 17 | 15 | 2 | 0 | 0 | 0 | 0 | 17 | 0 | 15 | 0 | 0 |
| `ISketchParabola` | 17 | 0 | 17 | 8 | 8 | 0 | 0 | 9 | 8 | 0 | 0 | 0 |
| `IStructureSystemMemberProfile` | 17 | 16 | 1 | 0 | 0 | 0 | 0 | 17 | 1 | 16 | 0 | 0 |
| `ITextFormat` | 17 | 16 | 1 | 0 | 0 | 0 | 0 | 17 | 1 | 16 | 0 | 0 |
| `IToolingSplitFeatureData` | 17 | 6 | 11 | 0 | 0 | 3 | 6 | 14 | 4 | 5 | 1 | 1 |
| `IUserUnit` | 17 | 9 | 8 | 0 | 0 | 0 | 0 | 17 | 3 | 9 | 0 | 0 |
| `IBalloonOptions` | 16 | 16 | 0 | 0 | 0 | 0 | 0 | 16 | 0 | 16 | 0 | 0 |
| `IDimXpertTolerance` | 16 | 1 | 15 | 0 | 0 | 6 | 6 | 10 | 9 | 1 | 0 | 0 |
| `IEntity` | 16 | 2 | 14 | 4 | 4 | 0 | 1 | 12 | 4 | 2 | 0 | 0 |
| `IRevisionTableAnnotation` | 16 | 2 | 14 | 0 | 0 | 2 | 2 | 14 | 3 | 2 | 0 | 0 |
| `IRibFeatureData2` | 16 | 12 | 4 | 0 | 0 | 0 | 0 | 16 | 2 | 12 | 0 | 0 |
| `IRuledSurfaceFeatureData` | 16 | 7 | 9 | 0 | 0 | 0 | 2 | 16 | 2 | 7 | 0 | 0 |
| `IScaleFeatureData` | 16 | 8 | 8 | 0 | 0 | 1 | 2 | 15 | 2 | 8 | 0 | 0 |
| `ISheetMetalGaugeTableParameters` | 16 | 4 | 12 | 0 | 0 | 0 | 0 | 16 | 7 | 4 | 0 | 0 |
| `IShutOffSurfaceFeatureData` | 16 | 4 | 12 | 0 | 0 | 2 | 3 | 14 | 4 | 2 | 2 | 2 |
| `ISketchedBendFeatureData` | 16 | 8 | 8 | 1 | 1 | 0 | 0 | 15 | 2 | 8 | 0 | 0 |
| `IStructuralMemberGroup` | 16 | 13 | 3 | 0 | 0 | 1 | 2 | 15 | 1 | 13 | 0 | 0 |
| `ITaskpaneView` | 16 | 0 | 16 | 3 | 3 | 0 | 0 | 13 | 7 | 0 | 0 | 0 |
| `IAttribute` | 15 | 1 | 14 | 2 | 2 | 0 | 0 | 13 | 8 | 1 | 0 | 0 |
| `IAVIParameter` | 15 | 15 | 0 | 0 | 0 | 0 | 0 | 15 | 0 | 15 | 0 | 0 |
| `IBeltChainFeatureData` | 15 | 10 | 5 | 0 | 0 | 0 | 0 | 15 | 2 | 10 | 0 | 0 |
| `IBodyFolder` | 15 | 1 | 14 | 0 | 0 | 1 | 1 | 14 | 10 | 1 | 0 | 0 |
| `IDimXpertFeature` | 15 | 2 | 13 | 0 | 0 | 3 | 3 | 12 | 9 | 2 | 0 | 0 |
| `IEnvironment` | 15 | 0 | 15 | 2 | 2 | 6 | 6 | 7 | 0 | 0 | 0 | 0 |
| `ILibraryFormToolFeatureData` | 15 | 10 | 5 | 0 | 0 | 0 | 0 | 15 | 2 | 10 | 0 | 0 |
| `IPropertyManagerPageNumberbox` | 15 | 7 | 8 | 1 | 1 | 0 | 1 | 14 | 1 | 6 | 1 | 1 |
| `IShellFeatureData` | 15 | 5 | 10 | 0 | 0 | 2 | 4 | 13 | 2 | 5 | 0 | 0 |
| `ISplineHandle` | 15 | 13 | 2 | 0 | 0 | 0 | 0 | 15 | 1 | 12 | 1 | 1 |
| `ISplitBodyFeatureData` | 15 | 4 | 11 | 2 | 2 | 1 | 4 | 12 | 3 | 4 | 0 | 0 |
| `IThickenFeatureData` | 15 | 8 | 7 | 0 | 0 | 1 | 2 | 14 | 3 | 8 | 0 | 0 |
| `IBendsFeatureData` | 14 | 7 | 7 | 5 | 5 | 0 | 0 | 9 | 3 | 3 | 0 | 0 |
| `IDomeFeatureData2` | 14 | 8 | 6 | 2 | 2 | 1 | 2 | 11 | 2 | 6 | 0 | 0 |
| `IFaceDecalProperties` | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 14 | 0 | 14 | 0 | 0 |
| `IFamilyTableFeature` | 14 | 0 | 14 | 0 | 0 | 0 | 0 | 14 | 8 | 0 | 0 | 0 |
| `IFlyoutGroup` | 14 | 9 | 5 | 4 | 4 | 0 | 0 | 10 | 1 | 5 | 0 | 0 |
| `IMathPoint` | 14 | 2 | 12 | 0 | 0 | 1 | 1 | 13 | 2 | 1 | 0 | 0 |
| `IMirrorSolidFeatureData` | 14 | 6 | 8 | 1 | 1 | 1 | 2 | 12 | 3 | 6 | 0 | 0 |
| `IParagraphs` | 14 | 2 | 12 | 0 | 0 | 0 | 0 | 14 | 2 | 2 | 0 | 0 |
| `IPMIDimensionItem` | 14 | 13 | 1 | 0 | 0 | 0 | 0 | 14 | 1 | 13 | 0 | 0 |
| `IPropertyManagerPageListbox` | 14 | 5 | 9 | 0 | 0 | 1 | 2 | 13 | 3 | 4 | 1 | 1 |
| `ISimulation3DContactFeatureData` | 14 | 14 | 0 | 0 | 0 | 0 | 0 | 14 | 0 | 13 | 1 | 1 |
| `ISketchPicture` | 14 | 2 | 12 | 0 | 0 | 1 | 1 | 13 | 2 | 2 | 0 | 0 |
| `ISlicingData` | 14 | 6 | 8 | 0 | 0 | 0 | 0 | 14 | 4 | 6 | 0 | 0 |
| `ISurfaceKnitFeatureData` | 14 | 8 | 6 | 0 | 0 | 1 | 2 | 13 | 2 | 8 | 0 | 0 |
| `IAdvancedHoleElementData` | 13 | 13 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 13 | 0 | 0 |
| `ICoreFeatureData` | 13 | 9 | 4 | 0 | 0 | 0 | 0 | 13 | 1 | 7 | 2 | 2 |
| `ICosmosMotionStudyProperties` | 13 | 13 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 13 | 0 | 0 |
| `IEndCapFeatureData` | 13 | 11 | 2 | 0 | 0 | 0 | 0 | 13 | 1 | 11 | 0 | 0 |
| `IFaceHatch` | 13 | 13 | 0 | 1 | 1 | 0 | 0 | 12 | 0 | 12 | 0 | 0 |
| `IInstanceToVaryOptions` | 13 | 2 | 11 | 0 | 0 | 0 | 0 | 13 | 0 | 2 | 0 | 0 |
| `ILocalSketchPatternFeatureData` | 13 | 6 | 7 | 0 | 0 | 0 | 0 | 13 | 5 | 6 | 0 | 0 |
| `IMassPropertyOverrideOptions` | 13 | 3 | 10 | 0 | 0 | 0 | 0 | 13 | 2 | 3 | 0 | 0 |
| `IPropertyManagerPageControl` | 13 | 9 | 4 | 0 | 0 | 0 | 0 | 13 | 1 | 9 | 0 | 0 |
| `IRoutingSettings` | 13 | 0 | 13 | 0 | 0 | 0 | 0 | 13 | 1 | 0 | 0 | 0 |
| `ISketchRelation` | 13 | 1 | 12 | 2 | 2 | 4 | 4 | 7 | 6 | 1 | 0 | 0 |
| `ISMNormalCutFeatureData2` | 13 | 7 | 6 | 0 | 0 | 0 | 0 | 13 | 2 | 7 | 0 | 0 |
| `ISurfaceOffsetFeatureData` | 13 | 4 | 9 | 4 | 4 | 2 | 4 | 7 | 2 | 3 | 0 | 0 |
| `ISwOLEObject` | 13 | 7 | 6 | 0 | 0 | 0 | 2 | 13 | 1 | 7 | 0 | 0 |
| `IView3D` | 13 | 10 | 3 | 0 | 0 | 0 | 0 | 13 | 1 | 10 | 0 | 0 |
| `IClosedCornerFeatureData` | 12 | 5 | 7 | 1 | 1 | 1 | 2 | 10 | 2 | 5 | 0 | 0 |
| `IColorTable` | 12 | 0 | 12 | 0 | 0 | 2 | 2 | 10 | 6 | 0 | 0 | 0 |
| `IConnectionPointFeatureData` | 12 | 9 | 3 | 0 | 0 | 0 | 0 | 12 | 1 | 9 | 0 | 0 |
| `ICornerReliefFeatureData` | 12 | 2 | 10 | 0 | 0 | 0 | 0 | 12 | 2 | 2 | 0 | 0 |
| `IDatumOrigin` | 12 | 3 | 9 | 2 | 2 | 1 | 2 | 9 | 4 | 3 | 0 | 0 |
| `IDimXpertAnnotation` | 12 | 3 | 9 | 0 | 0 | 1 | 1 | 11 | 8 | 3 | 0 | 0 |
| `IMathTransform` | 12 | 2 | 10 | 2 | 2 | 1 | 1 | 9 | 2 | 1 | 0 | 0 |
| `IMultiJogLeader` | 12 | 0 | 12 | 0 | 0 | 2 | 2 | 10 | 8 | 0 | 0 | 0 |
| `IParameter` | 12 | 0 | 12 | 3 | 3 | 0 | 0 | 9 | 5 | 0 | 0 | 0 |
| `IPartialEdgeFilletData` | 12 | 11 | 1 | 0 | 0 | 0 | 0 | 12 | 0 | 11 | 0 | 0 |
| `IPMIGtolData` | 12 | 5 | 7 | 0 | 0 | 0 | 0 | 12 | 6 | 5 | 0 | 0 |
| `IProjectionArrow` | 12 | 1 | 11 | 0 | 0 | 1 | 1 | 11 | 9 | 1 | 0 | 0 |
| `IRevisionCloud` | 12 | 3 | 9 | 0 | 0 | 3 | 3 | 9 | 4 | 3 | 0 | 0 |
| `ISecondaryMemberBetweenPointsFeatureData` | 12 | 10 | 2 | 0 | 0 | 0 | 0 | 12 | 1 | 10 | 0 | 0 |
| `ISecondaryMemberUpToMembersFeatureData` | 12 | 6 | 6 | 0 | 0 | 0 | 0 | 12 | 1 | 6 | 0 | 0 |
| `ISketchLine` | 12 | 2 | 10 | 4 | 4 | 0 | 0 | 8 | 6 | 2 | 0 | 0 |
| `ISketchPath` | 12 | 0 | 12 | 0 | 0 | 3 | 3 | 9 | 8 | 0 | 0 | 0 |
| `ISketchText` | 12 | 1 | 11 | 1 | 1 | 1 | 1 | 10 | 6 | 1 | 0 | 0 |
| `ISurfaceCutFeatureData` | 12 | 5 | 7 | 0 | 0 | 1 | 1 | 11 | 3 | 5 | 0 | 0 |
| `ISurfaceParameterizationData` | 12 | 12 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 12 | 0 | 0 |
| `ISurfaceTrimFeatureData` | 12 | 2 | 10 | 0 | 0 | 2 | 4 | 10 | 4 | 2 | 0 | 0 |
| `ITexture` | 12 | 11 | 1 | 0 | 0 | 0 | 0 | 12 | 0 | 11 | 0 | 0 |
| `IWeldmentTrimExtendFeatureData` | 12 | 2 | 10 | 0 | 0 | 2 | 4 | 10 | 3 | 2 | 0 | 0 |
| `IAppearanceSetting` | 11 | 11 | 0 | 0 | 0 | 0 | 0 | 11 | 0 | 11 | 0 | 0 |
| `IAttributeDef` | 11 | 0 | 11 | 8 | 8 | 0 | 0 | 3 | 1 | 0 | 0 | 0 |
| `IBreakCornerFeatureData` | 11 | 5 | 6 | 0 | 0 | 1 | 2 | 10 | 2 | 5 | 0 | 0 |
| `IBSurfParamData` | 11 | 9 | 2 | 0 | 0 | 1 | 1 | 10 | 0 | 9 | 0 | 0 |
| `ICavityFeatureData` | 11 | 4 | 7 | 0 | 0 | 0 | 2 | 11 | 2 | 4 | 0 | 0 |
| `ICosmeticWeldBeadFolder` | 11 | 11 | 0 | 0 | 0 | 0 | 0 | 11 | 0 | 11 | 0 | 0 |
| `IDimXpertCompositePositionTolerance` | 11 | 7 | 4 | 0 | 0 | 0 | 0 | 11 | 0 | 7 | 0 | 0 |
| `IDisplayStateSetting` | 11 | 5 | 6 | 0 | 0 | 2 | 4 | 9 | 2 | 5 | 0 | 0 |
| `IFeatureStatistics` | 11 | 10 | 1 | 0 | 0 | 0 | 0 | 11 | 1 | 10 | 0 | 0 |
| `IImport3DInterconnectData` | 11 | 8 | 3 | 0 | 0 | 0 | 0 | 11 | 2 | 8 | 0 | 0 |
| `IIndentFeatureData` | 11 | 8 | 3 | 0 | 0 | 0 | 0 | 11 | 2 | 8 | 0 | 0 |
| `IIntersectFeatureData` | 11 | 3 | 8 | 0 | 0 | 0 | 0 | 11 | 4 | 3 | 0 | 0 |
| `ILayerMgr` | 11 | 0 | 11 | 0 | 0 | 1 | 1 | 10 | 3 | 0 | 0 | 0 |
| `IMateControllerFeatureData` | 11 | 1 | 10 | 0 | 0 | 0 | 0 | 11 | 2 | 1 | 0 | 0 |
| `IProjectionCurveFeatureData` | 11 | 4 | 7 | 1 | 1 | 1 | 2 | 9 | 2 | 4 | 0 | 0 |
| `IPropertyManagerPageLabel` | 11 | 11 | 0 | 0 | 0 | 0 | 0 | 11 | 0 | 3 | 8 | 8 |
| `IReplaceFaceFeatureData` | 11 | 2 | 9 | 0 | 0 | 2 | 4 | 9 | 3 | 2 | 0 | 0 |
| `ISketchContour` | 11 | 1 | 10 | 1 | 1 | 2 | 2 | 8 | 6 | 1 | 0 | 0 |
| `ISMCornerReliefData` | 11 | 10 | 1 | 0 | 0 | 0 | 0 | 11 | 0 | 10 | 0 | 0 |
| `ISurfaceRadiateFeatureData` | 11 | 5 | 6 | 0 | 0 | 1 | 2 | 10 | 2 | 5 | 0 | 0 |
| `ISwHtmlInterface` | 11 | 0 | 11 | 0 | 0 | 0 | 0 | 11 | 6 | 0 | 0 | 0 |
| `ISwManipulatorHandler2` | 11 | 0 | 11 | 0 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 |
| `IAdvancedHoleFeatureData` | 10 | 4 | 6 | 0 | 0 | 0 | 0 | 10 | 3 | 4 | 0 | 0 |
| `IAdvancedSaveAsOptions` | 10 | 7 | 3 | 0 | 0 | 0 | 0 | 10 | 0 | 7 | 0 | 0 |
| `IBoundingBoxFeatureData` | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 1 | 8 | 0 | 0 |
| `ICThread` | 10 | 2 | 8 | 0 | 0 | 1 | 1 | 9 | 7 | 2 | 0 | 0 |
| `IDimXpertCompositeDistanceBetweenDimTol` | 10 | 3 | 7 | 0 | 0 | 0 | 0 | 10 | 1 | 3 | 0 | 0 |
| `IHealEdgesFeatureData` | 10 | 3 | 7 | 0 | 0 | 1 | 2 | 9 | 3 | 3 | 0 | 0 |
| `IMagneticLine` | 10 | 5 | 5 | 0 | 0 | 1 | 1 | 9 | 2 | 5 | 0 | 0 |
| `IPMIGtolBoxData` | 10 | 7 | 3 | 0 | 0 | 0 | 0 | 10 | 3 | 7 | 0 | 0 |
| `IPrimaryMemberPointLengthFeatureData` | 10 | 7 | 3 | 0 | 0 | 0 | 0 | 10 | 2 | 7 | 0 | 0 |
| `IPropertyManagerPageCombobox` | 10 | 5 | 5 | 0 | 0 | 0 | 1 | 10 | 1 | 4 | 1 | 1 |
| `IPunchTable` | 10 | 6 | 4 | 0 | 0 | 1 | 1 | 9 | 3 | 6 | 0 | 0 |
| `IRefPointFeatureData` | 10 | 4 | 6 | 0 | 0 | 1 | 2 | 9 | 2 | 4 | 0 | 0 |
| `IRipFeatureData` | 10 | 2 | 8 | 0 | 0 | 1 | 2 | 9 | 2 | 2 | 0 | 0 |
| `ISketchRelationManager` | 10 | 0 | 10 | 0 | 0 | 2 | 2 | 8 | 1 | 0 | 0 | 0 |
| `IStructureSystemMemberFeatureData` | 10 | 5 | 5 | 0 | 0 | 0 | 0 | 10 | 4 | 5 | 0 | 0 |
| `ISurfaceFlattenFeatureData` | 10 | 8 | 2 | 0 | 0 | 0 | 0 | 10 | 1 | 8 | 0 | 0 |
| `ITreeControlItem` | 10 | 5 | 5 | 0 | 0 | 0 | 0 | 10 | 5 | 5 | 0 | 0 |
| `ITriadManipulator` | 10 | 7 | 3 | 0 | 0 | 0 | 0 | 10 | 1 | 7 | 0 | 0 |
| `IUserNotificationDefinition` | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 10 | 0 | 0 |
| `IWeldmentCutListFeature` | 10 | 5 | 5 | 0 | 0 | 1 | 1 | 9 | 4 | 5 | 0 | 0 |
| `IAdvancedSelectionCriteria` | 9 | 0 | 9 | 2 | 2 | 0 | 0 | 7 | 2 | 0 | 0 | 0 |
| `IBreakLine` | 9 | 5 | 4 | 0 | 0 | 0 | 0 | 9 | 1 | 5 | 0 | 0 |
| `IBrokenOutSectionFeatureData` | 9 | 4 | 5 | 0 | 0 | 1 | 1 | 8 | 2 | 4 | 0 | 0 |
| `ICollisionDetectionManager` | 9 | 1 | 8 | 0 | 0 | 0 | 0 | 9 | 3 | 1 | 0 | 0 |
| `ICommandTab` | 9 | 3 | 6 | 0 | 0 | 1 | 1 | 8 | 3 | 3 | 0 | 0 |
| `IComplexCornerTreatmentFeatureData` | 9 | 3 | 6 | 0 | 0 | 0 | 0 | 9 | 2 | 3 | 0 | 0 |
| `ICosmosMotionStudyResults` | 9 | 0 | 9 | 0 | 0 | 1 | 1 | 8 | 5 | 0 | 0 | 0 |
| `IDeleteFaceFeatureData` | 9 | 1 | 8 | 0 | 0 | 1 | 2 | 8 | 3 | 1 | 0 | 0 |
| `IDragArrowManipulator` | 9 | 8 | 1 | 0 | 0 | 0 | 0 | 9 | 1 | 8 | 0 | 0 |
| `IFoldsFeatureData` | 9 | 2 | 7 | 1 | 1 | 1 | 2 | 7 | 2 | 2 | 0 | 0 |
| `IGtolFrame` | 9 | 0 | 9 | 0 | 0 | 0 | 0 | 9 | 2 | 0 | 0 | 0 |
| `ILayer` | 9 | 7 | 2 | 0 | 0 | 0 | 0 | 9 | 1 | 7 | 0 | 0 |
| `IMathUtility` | 9 | 0 | 9 | 0 | 0 | 0 | 2 | 9 | 0 | 0 | 0 | 0 |
| `IMessageBarDefinition` | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 9 | 0 | 0 |
| `IMotionStudyResults` | 9 | 0 | 9 | 0 | 0 | 0 | 0 | 9 | 1 | 0 | 0 | 0 |
| `IPlaneManipulator` | 9 | 8 | 1 | 0 | 0 | 0 | 0 | 9 | 1 | 8 | 0 | 0 |
| `IPMIGtolFrameDatum` | 9 | 9 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 9 | 0 | 0 |
| `IPrimaryMemberRefPlaneFeatureData` | 9 | 0 | 9 | 0 | 0 | 0 | 0 | 9 | 6 | 0 | 0 | 0 |
| `IRefAxisFeatureData` | 9 | 1 | 8 | 0 | 0 | 1 | 2 | 8 | 2 | 1 | 0 | 0 |
| `IReferenceCurve` | 9 | 0 | 9 | 0 | 0 | 1 | 1 | 8 | 6 | 0 | 0 | 0 |
| `IRenamedDocumentReferences` | 9 | 3 | 6 | 0 | 0 | 0 | 0 | 9 | 3 | 3 | 0 | 0 |
| `ISaveBodyFeatureData` | 9 | 3 | 6 | 0 | 0 | 0 | 0 | 9 | 2 | 3 | 0 | 0 |
| `ISensor` | 9 | 6 | 3 | 0 | 0 | 0 | 0 | 9 | 2 | 6 | 0 | 0 |
| `ISwQuickTip` | 9 | 7 | 2 | 0 | 0 | 0 | 0 | 9 | 0 | 7 | 0 | 0 |
| `IAngleMateFeatureData` | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 8 | 0 | 0 |
| `IClearanceVerificationMgr` | 8 | 3 | 5 | 0 | 0 | 0 | 0 | 8 | 3 | 3 | 0 | 0 |
| `ICombineBodiesFeatureData` | 8 | 3 | 5 | 0 | 0 | 1 | 2 | 7 | 2 | 3 | 0 | 0 |
| `IDecal` | 8 | 5 | 3 | 0 | 0 | 1 | 2 | 7 | 1 | 5 | 0 | 0 |
| `IDimXpertCompoundNotchFeature` | 8 | 1 | 7 | 0 | 0 | 0 | 0 | 8 | 4 | 1 | 0 | 0 |
| `IDimXpertExtrudeFeature` | 8 | 1 | 7 | 0 | 0 | 1 | 1 | 7 | 6 | 1 | 0 | 0 |
| `IInterference` | 8 | 5 | 3 | 0 | 0 | 1 | 1 | 7 | 2 | 5 | 0 | 0 |
| `IJoinFeatureData` | 8 | 3 | 5 | 0 | 0 | 1 | 2 | 7 | 2 | 3 | 0 | 0 |
| `IManipulator` | 8 | 4 | 4 | 0 | 0 | 0 | 0 | 8 | 2 | 4 | 0 | 0 |
| `IMateReference` | 8 | 7 | 1 | 0 | 0 | 0 | 0 | 8 | 0 | 2 | 5 | 5 |
| `IMaterialVisualPropertiesData` | 8 | 8 | 0 | 1 | 1 | 0 | 0 | 7 | 0 | 7 | 0 | 0 |
| `IMotionStudyManager` | 8 | 0 | 8 | 0 | 0 | 0 | 0 | 8 | 4 | 0 | 0 | 0 |
| `IPartExplodeStep` | 8 | 4 | 4 | 0 | 0 | 0 | 0 | 8 | 1 | 4 | 0 | 0 |
| `IPMIDatumTarget` | 8 | 7 | 1 | 0 | 0 | 0 | 0 | 8 | 1 | 7 | 0 | 0 |
| `IProfileGroupFolder` | 8 | 3 | 5 | 0 | 0 | 0 | 0 | 8 | 5 | 3 | 0 | 0 |
| `IPropertyManagerPageBitmapButton` | 8 | 2 | 6 | 3 | 3 | 0 | 0 | 5 | 0 | 2 | 0 | 0 |
| `IPropertyManagerPageGroup` | 8 | 5 | 3 | 2 | 2 | 0 | 0 | 6 | 0 | 5 | 0 | 0 |
| `IPropertyManagerPageSlider` | 8 | 6 | 2 | 0 | 0 | 0 | 0 | 8 | 0 | 6 | 0 | 0 |
| `IReferencePointCurveFeatureData` | 8 | 1 | 7 | 0 | 0 | 1 | 2 | 7 | 2 | 1 | 0 | 0 |
| `ISelectData` | 8 | 6 | 2 | 0 | 0 | 0 | 0 | 8 | 0 | 6 | 0 | 0 |
| `ISketchRegion` | 8 | 1 | 7 | 1 | 1 | 1 | 1 | 6 | 4 | 1 | 0 | 0 |
| `ISketchSlot` | 8 | 5 | 3 | 0 | 0 | 0 | 0 | 8 | 3 | 5 | 0 | 0 |
| `IStraightElementData` | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 8 | 0 | 0 |
| `IStructureSystemSplitMember` | 8 | 5 | 3 | 0 | 0 | 0 | 0 | 8 | 2 | 5 | 0 | 0 |
| `ISWDesignCheck` | 8 | 0 | 8 | 4 | 4 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IWrapSketchFeatureData` | 8 | 6 | 2 | 0 | 0 | 0 | 0 | 8 | 1 | 6 | 0 | 0 |
| `IBalloonStack` | 7 | 5 | 2 | 0 | 0 | 1 | 1 | 6 | 0 | 5 | 0 | 0 |
| `ICompositeCurveFeatureData` | 7 | 0 | 7 | 0 | 0 | 1 | 2 | 6 | 2 | 0 | 0 | 0 |
| `ICurveParamData` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 7 | 0 | 0 |
| `IDeleteBodyFeatureData` | 7 | 2 | 5 | 0 | 0 | 1 | 2 | 6 | 2 | 2 | 0 | 0 |
| `IDimXpertCompositeLineProfileTolerance` | 7 | 6 | 1 | 0 | 0 | 0 | 0 | 7 | 0 | 6 | 0 | 0 |
| `IDimXpertCompoundClosedSlot3DFeature` | 7 | 1 | 6 | 0 | 0 | 0 | 0 | 7 | 1 | 1 | 0 | 0 |
| `IDimXpertCompoundHoleFeature` | 7 | 2 | 5 | 0 | 0 | 1 | 1 | 6 | 4 | 2 | 0 | 0 |
| `IDistanceMateFeatureData` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 7 | 0 | 0 |
| `IDowelSymbol` | 7 | 1 | 6 | 0 | 0 | 1 | 1 | 6 | 5 | 1 | 0 | 0 |
| `IFeatMgrView` | 7 | 0 | 7 | 1 | 1 | 0 | 0 | 6 | 6 | 0 | 0 | 0 |
| `IHoleDataTable` | 7 | 3 | 4 | 0 | 0 | 0 | 0 | 7 | 0 | 3 | 0 | 0 |
| `IImportIgesData` | 7 | 6 | 1 | 0 | 0 | 0 | 0 | 7 | 0 | 6 | 0 | 0 |
| `ILinearCouplerMateFeatureData` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 7 | 0 | 0 |
| `IMateEntity2` | 7 | 5 | 2 | 1 | 1 | 1 | 1 | 5 | 1 | 4 | 0 | 0 |
| `IMateLoadReference` | 7 | 3 | 4 | 0 | 0 | 1 | 1 | 6 | 1 | 2 | 1 | 1 |
| `IPropertyManagerPageTab` | 7 | 1 | 6 | 2 | 2 | 0 | 0 | 5 | 1 | 1 | 0 | 0 |
| `IRayTraceRenderer` | 7 | 1 | 6 | 0 | 0 | 0 | 0 | 7 | 5 | 1 | 0 | 0 |
| `IRefPlane` | 7 | 3 | 4 | 2 | 2 | 2 | 2 | 3 | 0 | 3 | 0 | 0 |
| `ISilhouetteEdge` | 7 | 0 | 7 | 1 | 1 | 0 | 0 | 6 | 5 | 0 | 0 | 0 |
| `ISimulationDamperFeatureData` | 7 | 5 | 2 | 0 | 0 | 0 | 0 | 7 | 0 | 5 | 0 | 0 |
| `IStraightTapElementData` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 7 | 0 | 0 |
| `ISurfacePlanarFeatureData` | 7 | 1 | 6 | 0 | 0 | 2 | 2 | 5 | 2 | 1 | 0 | 0 |
| `ISurfRevolveFeatureData` | 7 | 2 | 5 | 0 | 0 | 0 | 0 | 7 | 1 | 2 | 0 | 0 |
| `IWeldmentCutListAnnotation` | 7 | 1 | 6 | 0 | 0 | 1 | 1 | 6 | 2 | 1 | 0 | 0 |
| `IBendTable` | 6 | 2 | 4 | 0 | 0 | 1 | 1 | 5 | 3 | 2 | 0 | 0 |
| `IBomTableSortData` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 4 | 2 | 2 |
| `ICenterOfMass` | 6 | 0 | 6 | 0 | 0 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| `ICollisionDetectionGroup` | 6 | 0 | 6 | 0 | 0 | 0 | 0 | 6 | 4 | 0 | 0 | 0 |
| `ICommandTabBox` | 6 | 0 | 6 | 0 | 0 | 0 | 3 | 6 | 0 | 0 | 0 | 0 |
| `ICornerTreatmentFeatureData` | 6 | 3 | 3 | 0 | 0 | 0 | 0 | 6 | 2 | 3 | 0 | 0 |
| `ICrossBreakFeatureData` | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 6 | 1 | 4 | 0 | 0 |
| `ICustomBendAllowance` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 |
| `IDimXpertAutoDimSchemeOption` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 |
| `IDimXpertCompositeSurfaceProfileTolerance` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 |
| `IDimXpertDimensionTolerance` | 6 | 3 | 3 | 0 | 0 | 0 | 0 | 6 | 1 | 3 | 0 | 0 |
| `IDimXpertOrientationTolerance` | 6 | 2 | 4 | 0 | 0 | 0 | 0 | 6 | 1 | 2 | 0 | 0 |
| `IFreePointCurveFeatureData` | 6 | 1 | 5 | 0 | 0 | 1 | 2 | 5 | 1 | 1 | 0 | 0 |
| `IHingeMateFeatureData` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 5 | 1 | 1 |
| `IMBDSTEP242Data` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 |
| `IPMIFrameData` | 6 | 2 | 4 | 0 | 0 | 0 | 0 | 6 | 2 | 2 | 0 | 0 |
| `IPrimaryMemberFacePlaneIntersectionFeatureData` | 6 | 1 | 5 | 0 | 0 | 0 | 0 | 6 | 3 | 1 | 0 | 0 |
| `ISecondaryMemberSupportPlaneFeatureData` | 6 | 1 | 5 | 0 | 0 | 0 | 0 | 6 | 3 | 1 | 0 | 0 |
| `ISlotMateFeatureData` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 |
| `ITitleBlock` | 6 | 0 | 6 | 0 | 0 | 1 | 1 | 5 | 3 | 0 | 0 | 0 |
| `ITwoMemberCornerTreatmentFeatureData` | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 6 | 2 | 4 | 0 | 0 |
| `IWidthMateFeatureData` | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 6 | 0 | 0 |
| `ICommentFolder` | 5 | 0 | 5 | 0 | 0 | 1 | 1 | 4 | 3 | 0 | 0 | 0 |
| `IDimXpertAngleBetweenCircularDimTol` | 5 | 3 | 2 | 0 | 0 | 0 | 0 | 5 | 0 | 3 | 0 | 0 |
| `IDimXpertChamferFeature` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `IDimXpertCylinderFeature` | 5 | 1 | 4 | 0 | 0 | 0 | 0 | 5 | 0 | 1 | 0 | 0 |
| `IDimXpertDimensionOption` | 5 | 5 | 0 | 1 | 1 | 0 | 0 | 4 | 0 | 4 | 0 | 0 |
| `IDimXpertManager` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `IDimXpertPositionTolerance` | 5 | 2 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 2 | 0 | 0 |
| `IDimXpertStraightnessTolerance` | 5 | 2 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 2 | 0 | 0 |
| `IExportPdfData` | 5 | 2 | 3 | 0 | 0 | 0 | 0 | 5 | 2 | 2 | 0 | 0 |
| `IImportedCurveFeatureData` | 5 | 1 | 4 | 0 | 0 | 1 | 2 | 4 | 1 | 1 | 0 | 0 |
| `IMateInPlace` | 5 | 4 | 1 | 0 | 0 | 0 | 0 | 5 | 1 | 1 | 3 | 3 |
| `IModelWindow` | 5 | 4 | 1 | 1 | 1 | 0 | 0 | 4 | 1 | 3 | 0 | 0 |
| `IMotionPlotFeatureData` | 5 | 1 | 4 | 0 | 0 | 1 | 1 | 4 | 2 | 1 | 0 | 0 |
| `IPMIDatumFeature` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `IProfileCenterMateFeatureData` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `IScrewMateFeatureData` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `ISelectionSet` | 5 | 0 | 5 | 0 | 0 | 0 | 0 | 5 | 5 | 0 | 0 | 0 |
| `ISimpleCornerTreatmentFeatureData` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `ISWPropertySheet` | 5 | 0 | 5 | 1 | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| `ITaperedTapElementData` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `ITextAndCustomProperty` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `IToolBoxConfiguratorApplication` | 5 | 2 | 3 | 0 | 0 | 0 | 0 | 5 | 2 | 2 | 0 | 0 |
| `IVersionCompatibilityItem` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 |
| `IComment` | 4 | 3 | 1 | 0 | 0 | 0 | 0 | 4 | 1 | 3 | 0 | 0 |
| `IConcentricMateFeatureData` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 4 | 0 | 0 |
| `ICornerManagementFolder` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 0 |
| `ICornerTreatmentGroupFolder` | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 4 | 3 | 1 | 0 | 0 |
| `ICountersinkElementData` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 4 | 0 | 0 |
| `IDiagnoseResult` | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 3 | 1 | 0 | 0 | 0 |
| `IDimXpertBestfitPlaneFeature` | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 3 | 2 | 0 | 0 | 0 |
| `IDimXpertCompoundWidthFeature` | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 1 | 0 | 0 |
| `IDimXpertConeFeature` | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 1 | 0 | 0 |
| `IDimXpertDistanceBetweenDimTol` | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 1 | 0 | 0 |
| `IDimXpertPatternFeature` | 4 | 1 | 3 | 0 | 0 | 1 | 1 | 3 | 2 | 1 | 0 | 0 |
| `IEdgePoint` | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 4 | 0 | 2 | 0 | 0 |
| `IEnumBodies2` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumCoEdges` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumComponents2` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumDisplayDimensions` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumDocuments2` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumDrSections` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumEdges` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumFaces2` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumLoops2` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumModelViews` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumSketchHatches` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumSketchPoints` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IEnumSketchSegments` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `IFacet` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 3 | 0 | 0 | 0 |
| `IFaultEntity` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 1 | 3 | 3 |
| `IGearMateFeatureData` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 4 | 0 | 0 |
| `IGeneralTableFeature` | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 3 | 3 | 0 | 0 | 0 |
| `IGraphicsBody` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 3 | 0 | 0 | 0 |
| `IGroundPlaneFeatureData` | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 4 | 1 | 2 | 0 | 0 |
| `IHoleStandardsData` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| `IMeshBody` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 3 | 0 | 0 | 0 |
| `IMotionPlotAxisFeatureData` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 4 | 0 | 0 |
| `IPrimaryMemberPathSegmentFeatureData` | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 4 | 2 | 1 | 0 | 0 |
| `IPropertyManagerPageActiveX` | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 4 | 2 | 1 | 0 | 0 |
| `IRackPinionMateFeatureData` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 3 | 1 | 1 |
| `IRefAxis` | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 3 | 3 | 0 | 0 | 0 |
| `IRevisionTableFeature` | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 3 | 3 | 0 | 0 | 0 |
| `ISimulationGravityFeatureData` | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 4 | 0 | 0 |
| `ISnapShot` | 4 | 3 | 1 | 0 | 0 | 0 | 0 | 4 | 1 | 3 | 0 | 0 |
| `IStructureSystemFolder` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 0 |
| `ISwColorContour1` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `ITabAndSlotFeatureData` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 3 | 0 | 0 | 0 |
| `ITitleBlockTableFeature` | 4 | 0 | 4 | 0 | 0 | 1 | 1 | 3 | 3 | 0 | 0 | 0 |
| `IUserNotificationHandler` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 2 | 0 | 0 | 0 |
| `IUserProgressBar` | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| `ICalloutLengthVariable` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IClearanceResult` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `ICoincidentMateFeatureData` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `ICollision` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 0 |
| `ICornerMember` | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 3 | 1 | 2 | 0 | 0 |
| `ICutListSortOptions` | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | 1 | 1 | 0 | 0 |
| `IDimXpertAngleBetweenDimTol` | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 2 | 0 | 0 |
| `IDimXpertBlockTolerances` | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 0 | 0 |
| `IDimXpertDiameterDimTol` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IDimXpertIntersectCircleFeature` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `IDimXpertIntersectPointFeature` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `IDimXpertSymmetryTolerance` | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 0 | 0 |
| `IFeatureFolder` | 3 | 0 | 3 | 0 | 0 | 1 | 1 | 2 | 2 | 0 | 0 | 0 |
| `IFlatPatternFolder` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 0 |
| `IMessageBarHandler` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 1 | 0 | 0 | 0 |
| `IMouse` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `IParallelMateFeatureData` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IPDMDocManager` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `IPMIDatumData` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 0 |
| `IPMIDimensionData` | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | 1 | 1 | 0 | 0 |
| `IPropertyManagerPageCheckbox` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IPropertyManagerPageOption` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IPropertyManagerPageTextbox` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IPropertyManagerPageWindowFromHandle` | 3 | 1 | 2 | 1 | 1 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `IScanto3D` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 1 | 0 | 0 | 0 |
| `ISheetMetalFolder` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 0 |
| `ISwComFeature` | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| `ISymmetricMateFeatureData` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `ITableAnchor` | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 3 | 1 | 2 | 0 | 0 |
| `ITangentMateFeatureData` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IUniversalJointMateFeatureData` | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| `IWeldBead` | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 3 | 2 | 1 | 0 | 0 |
| `IApplication` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `ICalloutAngleVariable` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `ICamFollowerMateFeatureData` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 1 | 1 |
| `ICenterLine` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| `ICoordinateSystemElement` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| `ICounterboreElementData` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `IDimensionSensorData` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 |
| `IDimXpertConcentricityTolerance` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `IDimXpertDepthDimTol` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 |
| `IDimXpertFilletFeature` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `IDimXpertIntersectLineFeature` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| `IDimXpertIntersectPlaneFeature` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| `IDimXpertLineProfileTolerance` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `IDimXpertSphereFeature` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `IFamilyTableAnnotation` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 |
| `IGeneralTableAnnotation` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `IGeneralToleranceTableFeature` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| `IHoleTableAnnotation` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `ILightDialog` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `IMateFeatureData` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `IMotionPlotFeatureOutput` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `IMotionStudyProperties` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `IPerpendicularMateFeatureData` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `IPhysicalSimulationMotionStudyProperties` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `IPropertyManagerPageBitmap` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| `ISaveTo3DExperienceOptions` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 |
| `ISelectionSetFolder` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `ISelectionSetItem` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| `ISmartComponentFeatureData` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `ISMNormalCutGroupData` | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 |
| `IStatusBarPane` | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | 0 |
| `ISwAddin` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `ISwAddinAdvancedOptionBroker` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| `ISwAddinBroker` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| `ISwUndoAPIHandler` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 |
| `IToolboxConfiguratorAddin` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| `IBendTableAnnotation` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `ICalloutStringVariable` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `ICutListItem` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertChamferDimTol` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertCounterBoreDimTol` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertCounterSinkAngleDimTol` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertCounterSinkDiameterDimTol` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertDatum` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertFlatnessTolerance` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `IDimXpertGtol` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertPlaneFeature` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `IDimXpertRadiusDimTol` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertRefPlaneFeature` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `IDimXpertSurfaceProfileTolerance` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IDimXpertTangencyTolerance` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IGeneralToleranceTableAnnotation` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IImportStepData` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `ILight` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| `ILockMateFeatureData` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IPLMObjectSpecification` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IPrimaryStructuralMemberFeatureData` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IPrint3DDialog` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| `IPropertyManagerPageButton` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IPunchTableAnnotation` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `IRefPoint` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| `ISecondaryStructuralMemberFeatureData` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `ISwCalloutHandler` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `ISwPEClassFactory` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `ISwPEManager` | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| `ITitleBlockTableAnnotation` | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 |
| `CTbcApplication` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `ISwPEToken` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `MessageBarHandler` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `Scanto3D` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swArrowPosition` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swAssemblyExplodeStepType` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swBitMaps` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swConcentricPositionType` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swCosmosWorksMat` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swCreateCommandGroupErrors` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swLinkString` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swObjectEquality` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `SwPEManager` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swPropertyManagerPageMessageExpanded` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swPropertyManagerPageMessageVisibility` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swRayTraceRenderType_e` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swRemoveCommandGroupErrors` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `swSolidBodiesDescriptionPropertyIndex` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `ToolboxConfiguratorAddin` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `UserNotificationHandler` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## 四、这个台账能回答什么（**给主线用的三个用法**）

1. **查某接口有多少可用成员 / 零参方法** ⇒ 直接查表，不用再翻页。
2. **`指针(全) ≠ 指针(R)` 的接口** ⇒ 那些接口里有「标记落在 `## Parameters` 等非 Returns 段」的成员
   （已报过的判据洞）。这类接口共 **108** 个。
3. **`废弃(宽) ≠ 废弃(严)` 的接口** ⇒ 那些接口有「`Obsolete` 开头但不以句点收尾」的页。
   共 **4** 个接口、**26** 个成员。

## ⚠ 明确记下的限度

* ⚠ **只扫 `C:\swapi\types\`**：**没扫** `C:\swapi\enums\`（963 页）·
  `examples\`（2839）· `docs\`；`D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包 29697 份）也没扫。
* ⚠ **「可用」不等于「能用」**：本表只按**页面文字**判废弃与指针，**没跑真机**。
  一个成员「可用」只表示它的页没被标废弃、没标进程内指针。
* ⚠ **索引顺序不稳定**：官方页的 `## Parameters` / `## Returns` 段落位置**未承诺稳定**，
  本解析器按**段落标题**取，不按行号。
