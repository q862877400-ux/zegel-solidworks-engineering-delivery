# C · 钣金 + 工程图 两域契约摘要（补 `api-02-sheetmetal` / `api-05-drawing` 的缺口）

> ★ 本文件是**对账产出**，不是建议书。每条结论都带**可搜索的原文位置**（文件 + 片段，**不写行号**）。
> ★ 三条纪律照抄 `api-pre/api-03-weldment.md` 开头：查不到就说查不到 · 只抄亲手读到的 · 不下结论、不提建议。
> ★ **本轮没有跑 SolidWorks、没有跑 pytest、没有改动仓内任何既有文件**（只新建本文件）。

---

## 〇 · 先说对账结果：6 处「对不上」

★ 下面每条都能用给出的命令/片段复现。**其中 F1、F3、F4 是「仓内已声明的证据」或「官方源自身」与源文件对不上**，
★ F2、F5、F6 是**覆盖缺口 / 重复计数风险**。

---

### F1 ★★★ 对账铁证：`api-03-weldment.md` 把一个数字挂到了错误的树上

**原文**（`D:\AI\SW\specs\202-user-coverage-gaps\recon\api-pre\api-03-weldment.md`，第 19 行所在段落）：

> `★ [chm-api] 全名含 SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~，只在 sldworksapi\ 树（该树顶层文件按 IFeatureManager~<成员>.html 计数 = **289**）。`

**本轮实测（两棵树分别数）**：

| 树 | 通配 | 计数 |
|---|---|---|
| `…\SWhelp\sldworksapi\`（.NET，api-03 声称 289 的那棵） | `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~*` | **285** |
| `…\SWhelp\sldworksapi\` | `*IFeatureManager~*` | **285** |
| `…\SWhelp\sldworksapivb6\`（VBA） | `SldWorks~FeatureManager~*` | **289** |

⇒ **289 是 VBA 树（`sldworksapivb6\`）的计数，不是它自己说的 .NET 树（`sldworksapi\`）的计数**；.NET 树是 285。
★ 差 4 个文件 ⇒ 若有人拿这 289 去核对 `[chm-api]` 的 `.NET Syntax` 段落，会多对 4 个成员。
★ 同一文件第 20 行关于 VBA 树的另一句（`该树按 IFeatureManager 过滤 = 0 个文件`）本轮实测**仍然成立**（`*IFeatureManager*` 在 `sldworksapivb6\` = 0），**不是同一处错**。

---

### F2 ★★ 官方源自身前后不一致：图纸属性返回数组说「7 个」却列了 8 个名字

**原文 A**（`C:\swapi\types\ISheet\GetProperties.md`，`## Remarks` 段）：

```
The return value is the following array of seven doubles:

 [ paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp ]
```

★ 写的是 **seven**，列的是 **8 个**名字。
★ 而且下面的 `where:` 段（`paperSize = …` 到 `height = Paper height`）**只解释了 7 个**，`sameCustomPrp` **没有定义**。

**原文 B**（`C:\swapi\types\ISheet\GetProperties2.md`，`## Remarks` 段）：

```
The return value is the following array of eight doubles:

 [ paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomProp ]
```

★ 这里写的是 **eight**（对上了），而且**补上了**定义：`*sameCustomProp* = Value is a boolean packed into a double and returns true if the **Same as sheet specified in Document Properties** in the Sheet Properties dialog is selected, false if not`。
★ ★ 最后一个元素的**拼法也不同**：`GetProperties` 写 `sameCustomPrp`，`GetProperties2` 写 `sameCustomProp`。

**[chm-api] 复核结果：查不到。** 本机 `sldworksapi\` 下**没有** `ISheet` 的任何成员页（见 F5），
`…\sldworksapivb6\SldWorks~Sheet~GetProperties.html` 里 `seven` / `eight` / `paperSize` / `sameCustomPr` 的出现次数**全为 0**
⇒ 这条**无法用 CHM 二次互证**，只能按 `[md]` 单一源记录。

---

### F3 ★★★ 官方源引用了**不存在的成员**（工程图域，共 5 处死链，CHM 逐字相同）

| # | 出处（`C:\swapi\types\IDrawingDoc\`） | 原文片段 | 本机核验 |
|---|---|---|---|
| a | `CreateDiamDim4.md` · `## See Also` | `[[IDrawingDoc::IICreateAngDim4 Method]]` / `IICreateLinearDim4` / `IICreateOrdinateDim4` | 三个 `.md` **都不存在**（真名是 `ICreateAngDim4.md` 等，**I×1**） |
| b | `CreateSectionView.md` · `## See Also` | `[[IDrawngDoc::Create1stAngleViews2 Method]]`（**Draw*ng***Doc，多一个 n）等 13 条 | `C:\swapi\types\IDrawngDoc\` **不存在** |
| c | `CreateCustomSymbol.md` / `CreateBlockDefinition.md` · `Obsolete` 行 | `[[ISkethcManager::MakeSketchBlockFromFile]]`、`[[ISketchManager::MakeSketchBlockSelected]]` | `C:\swapi\types\ISkethcManager\` **不存在**；`MakeSketchBlockSelected.md` **不存在**（真名 `MakeSketchBlockFromSelected.md`） |
| d | `Create1stAngleViews.md` · `Obsolete` 行 | `Obsolete. Superseded by [[IDrawingDoc::1stAngleViews2]].` | `C:\swapi\types\IDrawingDoc\1stAngleViews2.md` **不存在**（真名 `Create1stAngleViews2.md`） |
| e | `InsertBreakHorizontal.md` · `## See Also` | `[[IDrawingDoc::UnInsertBreakVertical Method]]` | `UnInsertBreakVertical.md` **不存在**（真名 `InsertBreakVertical.md`） |

★ ★ **五处都在 CHM 对应页里逐字相同**（抽验片段）：
· `…\sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IDrawingDoc~CreateDiamDim4.html` 中 `IICreateAngDim4` / `IICreateLinearDim4` / `IICreateOrdinateDim4` 各出现一次；
· `…~CreateSectionView.html` 中字符串 `IDrawngDoc` 出现 **15** 次；
· `…~CreateCustomSymbol.html` 中 `Obsolete. Superseded by ISkethcManager::MakeSketchBlockFromFile , ISketchManager::MakeSketchBlockSelected , and ISketchManager::MakeSketchBlockFromSketch .`；
· `…~Create1stAngleViews.html` 中 `Obsolete. Superseded by IDrawingDoc::1stAngleViews2 .`；
· `…~InsertBreakHorizontal.html` 中 `UnInsertBreakVertical` 出现 1 次。

⇒ 这是**官方源本身的问题**，不是 `swapi` 转换引入的、也不是本仓引入的；两份摘要都会原样带进来，**核的时候必须知道**。

---

### F4 ★★ 官方参数说明引用了**不存在的枚举成员**（钣金域）

**原文**（`C:\swapi\types\IFeatureManager\InsertSheetMetalLoftedBend2.md`，`## Parameters` 两条）：

> `- **DChordTol**: Chord tolerance or maximum distance between the arc and linear segment of a chord; valid only if EFacetOption is set to swLoftedBendFacetOptions_e.swChordTolerance and BFormed is false`
> `- **DSegLength**: Maximum length of the linear segment; valid only if EFacetOption is set to swLoftedBendFacetOptions_e.swSegmentLength and BFormed is false`
> `- **DSegAngle**: Maximum angle between adjacent linear segments; valid only if EFacetOption is set to swLoftedBendFacetOptions_e.swSegmentAngle and BFormed is false`

**枚举表**（`C:\swapi\enums\swLoftedBendFacetOptions_e.md`，`## Enumeration Members`，描述 `Faceting options for lofted bend facet features.`）只有 **4 个**成员：

| Member | Value |
|---|---|
| `swAngleBetweenSegments` | 3 = Facet by maximum angle between adjacent linear segments |
| `swBendsPerTransitionSegment` | 1 = Facet by maximum number of bends per transition segment |
| `swChordTolerance` | 0 = Facet by maximum distance between the arc and linear segment of a chord on the lofted bend |
| `swMaxSegmentLength` | 2 = Facet by maximum length of a linear segment |

**[chm-en] 复核**：`…\SWhelp\swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swLoftedBendFacetOptions_e.html`
的 `Members` 段逐字相同（`swAngleBetweenSegments 3` / `swBendsPerTransitionSegment 1` / `swChordTolerance 0` / `swMaxSegmentLength 2`）⇒ **两套官方源一致地不存在 `swSegmentLength` / `swSegmentAngle`**。
★ `DSegLength` / `DSegAngle` 的语义描述（最大线段长度 / 相邻线段最大夹角）**对得上**枚举里的 `swMaxSegmentLength`(2) / `swAngleBetweenSegments`(3)，但**名字对不上**。官方没写该用哪个 ⇒ **查不到，不替它选**。

---

### F5 ★★ 源覆盖缺口：工程图域 4 个主力接口在 CHM 的 .NET 树里**整域缺席**

对 `…\SWhelp\sldworksapi\` 用**两种命名**分别查（`SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.<接口>~*` 与 `SolidWorks.Interop.sldworks.<接口>~*`），结果：

| 接口 | .NET 树成员页数 | `SolidWorks.Interop.sldworks.<接口>.html`（接口首页） |
|---|---|---|
| `ISheet` | **0** | 不存在 |
| `IView` | **0** | 不存在 |
| `INote` | **0** | 不存在 |
| `ITableAnnotation` | **0** | 不存在 |
| `IModelView` | **0** | 不存在 |
| `ISectionViewData` | **0** | 不存在 |

★ **能查到的**（本机实测）：`IDrawingDoc` 274 页 · `IDisplayDimension` 141 页 · `IGtol` 119 页 · `IGtolFrame` 9 页 · `IBomTableAnnotation` 25 页 · `IBalloonOptions` 16 页 · `IAutoBalloonOptions` 19 页。
★ ⇒ 工程图域**能三源互证的只有 `IDrawingDoc` / `IDisplayDimension` / `IGtol` 这几族**；
★ `ISheet` / `IView` / `INote` / `ITableAnnotation` 只能靠 **`[md]` + `[chm-vb6]`**——
★ `[chm-vb6]` 里它们按**类名**（不带 `I`）命名，本机实测：`SldWorks~Sheet~*` = 55 · `SldWorks~View~*` = 468 · `SldWorks~Note~*` = 130 · `SldWorks~TableAnnotation~*` = 85。
★ ★ 这与 `api-03-weldment.md` 第 19–20 行的目录说明**不冲突**（那份说的是 `IFeatureManager`，本条说的是这 6 个接口），但**补充**了它没写的一条事实。

---

### F6 ★ 重复计数风险：`InsertSheetMetalCornerTrim` 同时属于两域

`C:\swapi\types\IFeatureManager\InsertSheetMetalCornerTrim.md` 名字带 `SheetMetal`，`## See Also` 指向
`[[IBreakCornerFeatureData Interface]]` 与 `[[ISheetMetalFeatureData Interface]]`。
★ 它**已经被 `api-pre/api-03-weldment.md` 的 §8.1「钣金折弯角修剪」抄过一遍**（该文件把 `InsertSheetMetalGussetFeature{,2,3}` 排除、但把这一条收进去了）。
★ 若本文件按「名字含 SheetMetal」再收一次 ⇒ 两份摘要里同一条会被计两次。
★ 本文件**只做交叉引用、不重抄**，理由写在上文（抄录范围）。

---

## 一 · 抄录范围与源（本轮亲读）

| # | 分域摘要 | 本文件章节 | 成员数 | 逐条读过的 `.md` |
|---|---|---|---|---|
| — | （原拟）`api-02-sheetmetal.md` | §二 | **20** | 20/20 |
| — | （原拟）`api-05-drawing.md` | §三 | **43** | 43/43 |

**格式模板**：`api-pre/api-03-weldment.md`（先读了它，再按它抄）。
**源（三套离线源，全部本机，未联网）**：

| 源 | 本文件简称 | 抄什么 |
|---|---|---|
| `C:\swapi\types\<接口>\<成员>.md` | **[md]** | 精确签名（`System.*` 口径）、`## Parameters`、`## Remarks` 逐字 |
| `C:\swapi\examples\<例子>.md` | **[ex]** | 例子调用序与实参 |
| `C:\swapi\enums\<枚举>.md` | **[en]** | 枚举成员与数值 |
| `…\SWhelp\sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.<接口>~<成员>.html` | **[chm-api]** | `Availability` / `Remarks` / `Obsolete` |
| `…\SWhelp\sldworksapivb6\SldWorks~<类名>~<成员>.html` | **[chm-vb6]** | 仅在 F5 提到的 4 个接口上存在 |
| `…\SWhelp\swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.<枚举>.html` | **[chm-en]** | 枚举 `Members` 段 |

---

# 二 · 钣金域契约摘要（拟 `api-02-sheetmetal.md`）

**抄录范围**：`C:\swapi\types\IFeatureManager\` 下名称含 `SheetMetal` / `Hem` / `MiterFlange` / `LoftedBend` / `3dBend` / `ConvertToSheetMetal` 的成员，
★ 外加 `CreateCustomBendAllowance`（所有钣金折弯余量的入口）与 `GetSheetMetalFolder` / `GetFlatPatternFolder`（两个文件夹取值器），共 **20 条**。
★ **不含** `InsertSheetMetalCornerTrim`（已由 `api-03-weldment.md` §8.1 抄过，见 F6）。

---

## 2.0 名字缺席（铁律 5）

| 想找的 | 结果 | 证据 |
|---|---|---|
| `IFeatureManager` 下**任何**含 `WeldSymbol` 的成员 | **查不到** | `C:\swapi\types\IFeatureManager\*Symbol*` = 0 个文件 |
| `IFeatureManager` 下含 `Kerb` / `Unfold` / `Refold` / `Punch` 的成员 | **查不到** | 同目录文件名表里无这些子串 |
| `IFeatureManager.InsertSheetMetalHem3` / `…EdgeFlange3` / `…BaseFlange3` | **查不到** | 同上；本域最高代次分别是 `Hem2` / `EdgeFlange2`（另有 `IInsertSheetMetalEdgeFlange2`）/ `BaseFlange2` |
| `swLoftedBendFacetOptions_e.swSegmentLength` / `swSegmentAngle` | **查不到** | 见 F4 |

---

## 2.1 `IFeatureManager.CreateCustomBendAllowance` ★ 所有 `PCBA` 形参的入口

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\CreateCustomBendAllowance.md`：

```
CustomBendAllowance CreateCustomBendAllowance()
```

★ **0 个参数（无参）**。描述句逐字：`Creates a custom bend allowance to use when creating a sheet metal feature.`；[md] `## Returns` = `Pointer to the [[ICustomBendAllowance]] object`。

**② ## Remarks** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页（`…IFeatureManager~CreateCustomBendAllowance.html`）**也没有 `Remarks` 段**；`Availability` = `SOLIDWORKS 2003 FCS, Revision Number 11.0`。

**③ 官方例子调用序** —— [ex] `C:\swapi\examples\Insert_Sheet_Metal_Hem_Example_VB.md`（本轮读了全文，59→41 行），逐字：

```vbnet
Set CBAObject = Part.FeatureManager.CreateCustomBendAllowance()
CBAObject.Type = 2
CBAObject.KFactor = 0.5
```

★ 调用序：无参建对象 → 设 `Type` → 设 `KFactor` → 把该对象传进钣金特征的 `PCBA` 形参。
★ [md] `## See Also` 逐字列出 **9 个** `SetCustomBendAllowance` 使用方：`BendsFeatureData` / `IEdgeFlangeFeatureData` / `IFeature::InsertSheetMetalBaseFlange` / `IHemFeatureData` / `IJogFeatureData` / `IMiterFlangeFeatureData` / `IOneBendFeatureData` / `ISheetMetalFeatureData` / `ISketchBendFeatureData`。
★ `CBAObject.Type = 2` / `KFactor = 0.5` 这两个实参的**枚举名与单位查不到**（`ICustomBendAllowance.Type` / `.KFactor` 的 md 本轮未读）。

**④ 枚举** —— 无参，无枚举形参。
**⑤ 废弃链** —— [md] 无 `Obsolete` 字样；[chm-api] 无。**查不到后继**。

**前置一句话**：查不到（无 Remarks 段，无参）。
**配方一句话**：无参 `CreateCustomBendAllowance()` → 设 `Type` / `KFactor` → 传 `PCBA`。

---

## 2.2 基体法兰 BaseFlange（2 条）

### 2.2.1 `IFeatureManager.InsertSheetMetalBaseFlange`

**① 精确签名** —— [md] `…\InsertSheetMetalBaseFlange.md`：

```
Feature InsertSheetMetalBaseFlange( System.double Thickness, System.bool ThickenDir, System.double Radius, System.double ExtrudeDist1, System.double ExtrudeDist2, System.bool FlipExtruDir, System.int EndCondition1, System.int EndCondition2, System.int DirToUse, CustomBendAllowance PCBA, System.bool UseDefaultRelief, System.int ReliefType, System.double ReliefWidth, System.double ReliefDepth, System.double ReliefRatio, System.bool UseReliefRatio )
```

★ **16 个参数**。[md] `## Returns` = `Pointer to the [[IFeature]] object`。
★ 形参逐条（`## Parameters`）：`Thickness`: Wall thickness of the sheet metal feature · `ThickenDir`: Direction to thicken the sheet metal · `Radius`: Global bend radius to insert at the corners · `ExtrudeDist1/2`: Distance of the sheet metal extrusion for the Direction 1/2 · `FlipExtruDir`: True to reverse the direction of the extrude, false to not · `EndCondition1/2`: End condition for first/second extrude distance · `DirToUse`: End condition type as defined in `[[swEndConditions_e]]` · `PCBA`: Pointer to the `[[custom bend allowance]]` object · `UseDefaultRelief`: True to use the default relief, false to not · `ReliefType`: Relief type as defined in `[[swSheetMetalReliefTypes_e]]` · `ReliefWidth/Depth/Ratio` · `UseReliefRatio`: True to use the relief ratio, false to not。

★ ★ **名实不符（原文事实）**：形参叫 **`DirToUse`**（"方向"），描述却写 **`End condition type as defined in [[swEndConditions_e]]`**（"端条件类型"）；
★ 而真正叫 `EndCondition1` / `EndCondition2` 的两个形参**没有任何枚举标注**。⇒ 官方文本自相矛盾，本文件只记录，不替它解释。

**② ## Remarks** —— [md] **没有 `## Remarks` 段**（42 行依次是 front-matter / 标题 / Obsolete / Signature / Parameters / Returns / See Also）。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 两个：`DirToUse` → `swEndConditions_e`；`ReliefType` → `swSheetMetalReliefTypes_e`。
[en] `C:\swapi\enums\swEndConditions_e.md`（描述 `End conditions for creation of a variety of features.`）：
`swEndCondBlind` 0 · `swEndCondThroughAll` 1 · `swEndCondThroughNext` 2 · `swEndCondUpToVertex` 3（= *Do not use; superseded by swEndCondUpToSelection*）· `swEndCondUpToSurface` 4（同上）· `swEndCondOffsetFromSurface` 5 · `swEndCondMidPlane` 6 · `swEndCondUpToBody` 7 · `swEndCondThroughAllBoth` 9 · `swEndCondUpToSelection` 10 · `swEndCondUpToNext` 11。

[en] `C:\swapi\enums\swSheetMetalReliefTypes_e.md`（描述 `Sheet metal relief types.`）：
`swSheetMetalReliefRectangular` 1 · `swSheetMetalReliefTear` 2 · `swSheetMetalReliefObround` 3 · `swSheetMetalReliefNone` 4 · `swSheetMetalReliefTearBend` 5。

**⑤ 废弃链** —— [md] 原文（第 12 行，紧跟标题之后）：

> `Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalBaseFlange2]].`

[chm-api] 同句逐字（去标签后）`Obsolete. Superseded by IFeatureManager::InsertSheetMetalBaseFlange2 .`；`Availability` = `SOLIDWORKS 2003 FCS, Revision Number 11.0`。
⇒ **后继 = `InsertSheetMetalBaseFlange2`**。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

### 2.2.2 `IFeatureManager.InsertSheetMetalBaseFlange2` ★ 现行版，★ **唯一点名 mark 的基体法兰**

**① 精确签名** —— [md] `…\InsertSheetMetalBaseFlange2.md`：`…2` 的 16 参 + `Merge` + `UseFeatScope` + `UseAutoSelect`，即

```
Feature InsertSheetMetalBaseFlange2( … 16 个同前 …, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect )
```

★ **19 个参数**（比 `…` 多 3 个）。新增三者逐条：`Merge`: True to connect bodies into a single sheet metal body; false to not · `UseFeatScope`: True to use selected bodies, false to use all bodies · `UseAutoSelect`: True to auto select bodies (**see Remarks**)。[md] `## Returns` = `[[IFeature]]`。

**② ## Remarks 逐字** —— [md] 原文片段 `use selection mark 8`（★ **本节唯一的 mark 前置**）：

> ```
> ## Remarks
> When UseAutoSelect is set to false and bodies are selected using [[IModelDocExtension::SelectByID2]] or other select methods, use selection mark 8 for the bodies.
> ```

[chm-api] 同段逐字（去标签后一致）；`Availability` = `SOLIDWORKS 2010 FCS, Revision Number 18.0`。

**③ 官方例子调用序与配方实参** —— 例子文件名 `Insert_Sheet_Metal_Base_Flange_Example_VB.md`（[ex]，本轮读了全文 59 行；`## Examples` 另列 `…_VBNET` / `…_CSharp` 两个 `.md`，本机**长度 = 1（空壳）**⇒ 逐字调用序查不到）。逐字：

```vbnet
boolstatus = Part.Extension.SelectByID2("", "FACE", -0.0785775433435, 0.01894373057962, 0, True, 0, Nothing, 0)
boolstatus = Part.FeatureManager.InsertConvertToSheetMetal(0.002, False, False, 0.004, 0.002, 0, 0.5)
Part.ClearSelection2 True
…
vSkLines = Part.SketchManager.CreateCornerRectangle(…)
Set myFeature = Part.FeatureManager.InsertSheetMetalBaseFlange2(0.002, False, 0.004, 0.02, 0.01, False, 0, 0, 1, customBendAllowanceData, False, 2, 0.0001, 0.0001, 0.5, True, False, True, True)
Part.ClearSelection2 True
```

★ 调用序：**先 `InsertConvertToSheetMetal` 把两个凸台转成钣金 → `CreateCornerRectangle` 画矩形 → 调 19 参 → `ClearSelection2`**。
★ 实参逐位：`Thickness=0.002` · `ThickenDir=False` · `Radius=0.004` · `ExtrudeDist1=0.02` · `ExtrudeDist2=0.01` · `FlipExtruDir=False` · `EndCondition1=0` · `EndCondition2=0` · `DirToUse=1` · `PCBA=customBendAllowanceData`（一个**只 Dim 未 Set 的 Object**，即空对象）· `UseDefaultRelief=False` · `ReliefType=2`（= `swSheetMetalReliefTear`）· `ReliefWidth=0.0001` · `ReliefDepth=0.0001` · `ReliefRatio=0.5` · `UseReliefRatio=True` · `Merge=False` · `UseFeatScope=True` · `UseAutoSelect=True`。
★ ★ 例子**没有**任何 `SelectByID2(…, 8, …)` —— 因为它把 `UseAutoSelect=True`；Remarks 的 mark 8 是 `UseAutoSelect=False` 时才需要的另一条路。

**④ 枚举** —— 同 §2.2.1（`swEndConditions_e` / `swSheetMetalReliefTypes_e`）。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].`

[chm-api] 同句逐字；`Availability` = `SOLIDWORKS 2010 FCS, Revision Number 18.0`。
⇒ **后继不是 `…3`，而是 `CreateDefinition` + `CreateFeature` 这条通用入口**（`swFmBaseFlange`）。

**前置一句话**：`When UseAutoSelect is set to false … use selection mark 8 for the bodies.`
**配方一句话**：`InsertSheetMetalBaseFlange2(0.002, False, 0.004, 0.02, 0.01, False, 0, 0, 1, customBendAllowanceData, False, 2, 0.0001, 0.0001, 0.5, True, False, True, True)`，第 12 位 `2` = `swSheetMetalReliefTear`，末三位 `False, True, True` = `Merge, UseFeatScope, UseAutoSelect`。

---

## 2.3 边线法兰 EdgeFlange（3 条）

### 2.3.1 `IFeatureManager.InsertSheetMetalEdgeFlange`

**① 精确签名** —— [md] `…\InsertSheetMetalEdgeFlange.md`：

```
Feature InsertSheetMetalEdgeFlange( Edge FlangeEdge, Feature SketchFeat, System.int BooleanOptions, System.double DAngle, System.double DRadius, System.int BendPosition, System.double DOffsetDist, System.int ReliefType, System.double DReliefRatio, System.double DReliefWidth, System.double DReliefDepth, System.int FlangeSharpType, CustomBendAllowance PCBA )
```

★ **13 个参数**。[md] `## Parameters` **13 行全部写 `No description`**；该文件**也没有 `## Returns` 段**。

**② ## Remarks** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**、也**没有 `Availability` 段**（两处都是「无该段」）。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。
★ 但 [ex] `Insert_Sheet_Metal_Edge_Flange_Example_VB.md` 里有它的调用（见 §2.3.2）。

**④ 枚举** —— [md] 的 `## Parameters` 全是 `No description` ⇒ 签名里 `BooleanOptions` / `BendPosition` / `ReliefType` / `FlangeSharpType` 对应哪个枚举，**该文件查不到**（由 §2.3.2 的同族文件补：`swInsertEdgeFlangeOptions_e` / `swFlangePositionTypes_e` / `swSheetMetalReliefTypes_e` / `swFlangeDimTypes_e`）。

**⑤ 废弃链** —— [md] 原文：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalEdgeFlange2]].`
[chm-api] 同句逐字（`Obsolete. Superseded by IFeatureManager::InsertSheetMetalEdgeFlange2 .`）。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

### 2.3.2 `IFeatureManager.InsertSheetMetalEdgeFlange2` ★ 现行版

**① 精确签名** —— [md] `…\InsertSheetMetalEdgeFlange2.md`：

```
Feature InsertSheetMetalEdgeFlange2( System.object FlangeEdges, System.object SketchFeats, System.int BooleanOptions, System.double FlangeAngle, System.double FlangeRadius, System.int BendPosition, System.double FlangeOffsetDist, System.int ReliefType, System.double FlangeReliefRatio, System.double FlangeReliefWidth, System.double FlangeReliefDepth, System.int FlangeSharpType, CustomBendAllowance CustomBendAllowance )
```

★ **13 个参数**（与 `…1` 数量相同，但前两位从单个对象 `Edge`/`Feature` 改成**两个数组** `System.object`）。[md] `## Returns` = `Pointer to the [[IFeature]] object`。
`## Parameters` 逐条：`FlangeEdges`: Array of [[edges]] to which to apply a flange · `SketchFeats`: Array of [[sketches]] to use for the flange · `BooleanOptions`: Flange options as defined by `[[swInsertEdgeFlangeOptions_e]]` · `FlangeAngle`: Flange angle · `FlangeRadius`: Bend radius · `BendPosition`: Flange bend position as defined by `[[swFlangePositionTypes_e]]` · `FlangeOffsetDist`: Length of flange · `ReliefType`: Relief type as defined by `[[swSheetMetalReliefTypes_e]]` · `FlangeReliefRatio/Width/Depth` · `FlangeSharpType`: Flange virtual sharp type as defined by `[[swFlangeDimTypes_e]]` · `CustomBendAllowance`: **If…** / **Then…** / `non-NULL` → `Pointer to [[ICustomBendAllowance]] object for which required values have been set` / `NULL` → `Parent bend's bend allowance is used`。

**② ## Remarks 逐字** —— [md] 原文片段 `Before calling this method`：

> ```
> ## Remarks
> Before calling this method, call [[IModelDoc2::InsertSketchForEdgeFlange]] and create a profile for the flange. After creating the profile, call this method to create the flange.
> ```

[chm-api] 同段逐字（去标签后一致）；`Availability` = `SOLIDWORKS 2007 FCS, Revision Number 15.0`。
★ 官方**没给 mark 数字**；它把「建轮廓」的入口点名为 `IModelDoc2::InsertSketchForEdgeFlange`。

**③ 官方例子调用序与配方实参** —— 例子文件名 `Insert_Sheet_Metal_Edge_Flange_Example_VB.md`（[ex]，本轮读了全文 220 行；注意该 `.md` 的**换行被打散**，但语句完整）。逐字关键段：

```vbnet
bValue = swModel.Extension.SelectByID2("", "EDGE", 0.007817329387943, 0.001156559535341, 0.04430115457222, False, 0, Nothing, 0)
Set swEdge = swModel.SelectionManager.GetSelectedObject6(1, -1)
Set swFeature = swModel.InsertSketchForEdgeFlange(swEdge, dAngle, False)
Set swFeature.Select2(False, 0)
swModel.EditSketch
Set swSketch = swModel.GetActiveSketch2
Set swEntity = swEdge
bValue = swEntity.Select4(False, Nothing)
bValue = swModel.SketchManager.SketchUseEdge(False)
…
swModel.CreateLine2 …   ' 6 条线
swModel.InsertSketch2 True
nOptions = swInsertEdgeFlangeOptions_e.swInsertEdgeFlangeUseDefaultRadius + swInsertEdgeFlangeOptions_e.swInsertEdgeFlangeUseDefaultRelief
Set aFlangeEdges(0) = swEdge
Set aSketchFeats(0) = swSketch
vFlangeEdges = aFlangeEdges
vSketchFeats = aSketchFeats
Set swFeature = swModel.FeatureManager.InsertSheetMetalEdgeFlange2((vFlangeEdges), (vSketchFeats), nOptions, dAngle, 0#, swFlangePositionTypes_e.swFlangePositionTypeBendOutside, dLength, swSheetMetalReliefTypes_e.swSheetMetalReliefNone, 0#, 0#, 0#, swFlangeDimTypes_e.swFlangeDimTypeInnerVirtualSharp, Nothing)
```

★ 调用序（19 步，可逐条复核）：`ShowNamedView2 "*Trimetric", -1` → `ViewZoomtofit2` → `SelectByID2("", "EDGE", …, mark 0)` → `GetSelectedObject6(1, -1)` → `InsertSketchForEdgeFlange(swEdge, dAngle, False)` → `swFeature.Select2(False, 0)` → `EditSketch` → `GetActiveSketch2` → `swEntity.Select4(False, Nothing)` → `SketchUseEdge(False)` → 6 次 `CreateLine2` → `InsertSketch2 True` → 调 13 参。
★ 实参逐位：`FlangeEdges=(vFlangeEdges)` · `SketchFeats=(vSketchFeats)` · `BooleanOptions=nOptions`（= `UseDefaultRadius`(1) **+** `UseDefaultRelief`(128)，按 §2.4 枚举表 = 129）· `FlangeAngle=dAngle`（例中 `dAngle = (90# / 180#) * 3.1415926535897`，**弧度**）· `FlangeRadius=0#` · `BendPosition=swFlangePositionTypeBendOutside` · `FlangeOffsetDist=dLength`（例中 `dLength = 0.01`）· `ReliefType=swSheetMetalReliefNone` · `FlangeReliefRatio=0#` · `FlangeReliefWidth=0#` · `FlangeReliefDepth=0#` · `FlangeSharpType=swFlangeDimTypeInnerVirtualSharp` · `CustomBendAllowance=Nothing`。
★ 同一例子用 `#If 0 Then / #Else` 保留了 `InsertSheetMetalEdgeFlange`（旧版）的等价调用，可作两版对照。

**④ 枚举** —— 四个：

`swInsertEdgeFlangeOptions_e`（描述 `Sheet metal edge flange options. [Bitmask]` —— 官方点名 **Bitmask**）：
`swInsertEdgeFlangeUseDefaultRadius` 1/0x1 · `swInsertEdgeFlangeFlipDir` 2/0x2 · `swInsertEdgeFlangeDoOffset` 4/0x4 · `swInsertEdgeFlangeReverseOffsetDir` 8/0x8 · `swInsertEdgeFlangeTearClip` 16/0x10 · `swInsertEdgeFlangeTrimSideBend` 32/0x20 · `swInsertEdgeFlangeUseReliefRatio` 64/0x40 · `swInsertEdgeFlangeUseDefaultRelief` 128/0x80。

`swFlangePositionTypes_e`（描述 `Position types for sheet metal edge flanges.`）：
`swFlangePositionTypeMaterialInside` 1 · `swFlangePositionTypeMaterialOutside` 2 · `swFlangePositionTypeBendOutside` 3 · `swFlangePositionTypeBendCenterLine` 4 · `swFlangePositionTypeBendSharp` 5（= Bend from virtual sharp）· `swFlangePositionTypeBendTangent` 6（= …not valid for the Up To Edge And Merge length end condition）。

`swFlangeDimTypes_e`（描述 `Origins for dimensioning Blind or Up To Edge And Merge flange length end conditions in edge flanges.`）：
`swFlangeDimTypeOuterVirtualSharp` 1 · `swFlangeDimTypeInnerVirtualSharp` 2 · `swFlangeDimTypeBendTangentArc` 3（= …not valid for the Up To Edge And Merge length end condition）。

`swSheetMetalReliefTypes_e`：见 §2.2.1。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].`

[chm-api] 同句逐字；`Availability` = `SOLIDWORKS 2007 FCS, Revision Number 15.0`。
★ ★ 注意：`InsertSheetMetalEdgeFlange2` 在 CHM 的 `Availability` 是 **SW2007 FCS R15.0**，比它被废弃所指向的 `CreateDefinition`（`swFmEdgeFlange`）**早**；官方文本本身不解释这点，只记录。

**前置一句话**：`Before calling this method, call IModelDoc2::InsertSketchForEdgeFlange and create a profile for the flange.`
**配方一句话**：选边(mark 0) → `InsertSketchForEdgeFlange` → `EditSketch` + `SketchUseEdge` + 6 条 `CreateLine2` → `InsertSketch2 True` → `InsertSheetMetalEdgeFlange2((vFlangeEdges), (vSketchFeats), nOptions, dAngle, 0#, swFlangePositionTypeBendOutside, dLength, swSheetMetalReliefNone, 0#, 0#, 0#, swFlangeDimTypeInnerVirtualSharp, Nothing)`。

---

### 2.3.3 `IFeatureManager.IInsertSheetMetalEdgeFlange2`（`…2` 的指针变体）

**① 精确签名** —— [md] `…\IInsertSheetMetalEdgeFlange2.md`：

```
Feature IInsertSheetMetalEdgeFlange2( System.int EdgeCount, ref Edge FlangeEdges, System.int SketchFeatCount, ref Feature SketchFeat, … )
```

★ **15 个参数** = `…2` 的 13 参 + 开头两个**计数形参** `EdgeCount` / `SketchFeatCount`（官方描述：`Number of edges for the flange` / `Number of sketches for the flange`）。

**② ## Remarks 逐字** —— [md] 与 `…2` 逐字相同，只把 `InsertSketchForEdgeFlange` 换成 `IInsertSketchForEdgeFlange`：

> ```
> ## Remarks
> Before calling this method, call [[IModelDoc2::IInsertSketchForEdgeFlange]] and create a profile for the flange. After creating the profile, call this method to create the flange.
> ```

[chm-api] 同段逐字；`Availability` = `SOLIDWORKS 2007 FCS, Revision Number 15.0`。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 同 §2.3.2 的四个。

**⑤ 废弃链** —— [md] 原文：`Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].`

**前置一句话**：同 `…2`，只是点名 `IInsertSketchForEdgeFlange`。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 2.4 折边 Hem（2 条）

### 2.4.1 `IFeatureManager.InsertSheetMetalHem`

**① 精确签名** —— [md] `…\InsertSheetMetalHem.md`：

```
Feature InsertSheetMetalHem( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA )
```

★ **9 个参数**。[md] `## Returns` = `Pointer to the [[IFeature]] object`。
`## Parameters` 逐条（**带 valid-only 条件**）：`Type`: Type as defined in `[[swHemTypes_e]]` · `Position`: Position as defined in `[[swHemPositionTypes_e]]` · `Reverse`: True reverses the direction, false does not · `DLength`: Hem length; **valid only for open or closed hems** · `DGap`: Gap distance; **valid only for open hems** · `DAngle`: Hem angle; **valid only for tear-drop or rolled hems** · `DRad`: Hem radius; **valid only for tear-drop or rolled hems** · `DMiterGap`: Hem miter gap · `PCBA`: **If…**/**Then…**（`non-NULL` → 指针 / `NULL` → Parent bend's bend allowance is used）。

**② ## Remarks** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。
★ [chm-api] `Availability` = `SOLIDWORKS 2001Plus FCS, Revision Number 10.0` —— ★ 原文里 **Plus** 这个词是逐字保留的（本机其他成员都没出现过）。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— `swHemTypes_e`（描述 `Hem types.`）：`swHemTypeOpen` 0 · `swHemTypeClosed` 1 · `swHemTypeTearDrop` 2 · `swHemTypeRolled` 3 · `swHemTypeDouble` 4。
`swHemPositionTypes_e`（描述 `Hem position types.`）：`swHemPositionTypeInside` 1 · `swHemPositionTypeOutside` 2。

**⑤ 废弃链** —— [md] 原文：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalHem2]].`

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

### 2.4.2 `IFeatureManager.InsertSheetMetalHem2` ★ 现行版 ★ **前置是四步序**

**① 精确签名** —— [md] `…\InsertSheetMetalHem2.md`：

```
Feature InsertSheetMetalHem2( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA, System.bool UseDefaultRelief, System.int ReliefType, System.int ReliefTearTypes, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth )
```

★ **16 个参数**（`…1` 的 9 参 + 7 个 relief 参数）。描述句逐字：`Inserts a hem of the specified relief type at the selected edges of the current sheet metal part.`；[md] `## Returns` = `[[IFeature]]`。
`## Parameters` 里后 7 个形参的 valid-only 条件是**嵌套三条**（`UseDefaultRelief is false` **and** …），逐字摘录两段：
· `ReliefTearTypes`: Type of relief tear as defined in `[[swReliefTearTypes_e]]`; valid only when: `UseDefaultRelief is false` / `- and -` / `ReliefType is [[swSheetMetalReliefTypes_e]].swSheetMetalReliefTear`
· `ReliefRatio`: Relief ratio; valid only when: `UseDefaultRelief is false` / `- and -` / `UseReliefRatio is true` / `- and -` / `ReliefType is either [[swSheetMetalReliefTypes_e]].swSheetMetalReliefObround or [[swSheetMetalReliefTypes_e]].swSheetMetalReliefRectangular`

**② ## Remarks 逐字** —— [md] 原文片段 `Before calling this method`（★★ **四步序**）：

> ```
> ## Remarks
> Before calling this method:
>
> 1. Call [[IFeatureManager::CreateCustomBendAllowance]] to create an instance of ICustomBendAllowance.
>
> 2. Initialize the CustomBendAllowance object.
>
> 3. Assign PCBA to the initialized CustomBendAllowance object.
>
> 4. Select one or more edges in the sheet metal model to which to add the specified hem.
> ```

[chm-api] 同段逐字（去标签后一致）；`Availability` = `SOLIDWORKS 2011 SP03, Revision Number 19.3`。
★ ★ 官方**没给 mark 数字**（第 4 步只说「Select one or more edges」）。

**③ 官方例子调用序与配方实参** —— 例子文件名 `Insert_Sheet_Metal_Hem_Example_VB.md`（[ex]，本轮读了全文 41 行）。逐字：

```vbnet
Set swApp = Application.SldWorks
Set Part = swApp.ActiveDoc
Set CBAObject = Part.FeatureManager.CreateCustomBendAllowance()
CBAObject.Type = 2
CBAObject.KFactor = 0.5
' Insert an open hem of custom relief type Obround and relief ratio 1.0
Set myFeature = Part.FeatureManager.InsertSheetMetalHem2(swHemTypes_e.swHemTypeOpen, swHemPositionTypes_e.swHemPositionTypeOutside, False, 0.01, 0.01, 0, 0.005, 0.0011, CBAObject, False, swSheetMetalReliefTypes_e.swSheetMetalReliefObround, 0, True, 1#, 0, 0)
Part.ClearSelection2 True
Set myHem = myFeature.GetDefinition
Debug.Print "Hem type as defined in swHemTypes_e: " & myHem.Type
```

★ ★ **例子自己没有 `SelectByID2`** —— 它的**注释头**写死了前置：`Preconditions: 1. Open a sheet metal part. / 2. Select the edge to which you can add a hem.`（由人在 UI 里先选好边）。
★ 实参逐位：`Type=swHemTypeOpen`(0) · `Position=swHemPositionTypeOutside`(2) · `Reverse=False` · `DLength=0.01` · `DGap=0.01` · `DAngle=0` · `DRad=0.005` · `DMiterGap=0.0011` · `PCBA=CBAObject` · `UseDefaultRelief=False` · `ReliefType=swSheetMetalReliefObround`(3) · `ReliefTearTypes=0` · `UseReliefRatio=True` · `ReliefRatio=1#` · `ReliefWidth=0` · `ReliefDepth=0`。
★ 读回序：`myFeature.GetDefinition` → `myHem.Type`。

**④ 枚举** —— 三个：
`swHemTypes_e` / `swHemPositionTypes_e`：见 §2.4.1。
`swReliefTearTypes_e`（描述 `Sheet metal tear-drop relief types.`）：`swReliefTearTypeRip` 1 · `swReliefTearTypeExtend` 2。
`swSheetMetalReliefTypes_e`：见 §2.2.1。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样；[chm-api] 该页有 `Availability` 但无 `obsol` 标记）。**查不到后继**。

**前置一句话**：四步 —— `CreateCustomBendAllowance` → 初始化该对象 → 赋给 `PCBA` → 选中一条或多条边（**官方未给 mark**）。
**配方一句话**：`CreateCustomBendAllowance()` → `Type=2` / `KFactor=0.5` → `InsertSheetMetalHem2(swHemTypeOpen, swHemPositionTypeOutside, False, 0.01, 0.01, 0, 0.005, 0.0011, CBAObject, False, swSheetMetalReliefObround, 0, True, 1#, 0, 0)` → `ClearSelection2 True` → `GetDefinition`。

---

## 2.5 斜接法兰 MiterFlange（1 条）

## 2.5.1 `IFeatureManager.InsertSheetMetalMiterFlange`

**① 精确签名** —— [md] `…\InsertSheetMetalMiterFlange.md`：

```
Feature InsertSheetMetalMiterFlange( System.bool UseDefaultRadius, System.double GlobalRadius, System.double RipGap, System.bool UseDefaultRelief, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth, System.int ReliefType, System.bool TrimSideBends, System.int FlangePos, System.double OffsetDist1, System.double OffsetDist2, CustomBendAllowance PCBA )
```

★ **14 个参数**。描述句逐字：`Inserts a meter flange in a sheet metal part.`（★ 官方把 **miter** 拼成了 **meter**，逐字保留）。
[md] `## Returns` = `Pointer to the [[IFeature]] object **or NULL**`（★ 这是本域唯一明写可能返回 NULL 的）。
`## Parameters` 里 `ReliefType` 与 `FlangePos` 各带**内联 valid selections** 列表：
· `ReliefType`: Relief type as defined by `[[swSheetMetalReliefTypes_e]]`; valid selections: `swSheetMetalRelievObround`（★ 官方把 Obround 拼成 **Reliev**）/ `swSheetMetalReliefRectangular` / `swSheetMetalReliefTear`
· `FlangePos`: …; valid selections: `swFlangePositionTypeMaterialInside` / `swFlangePositionTypeMaterialOutside` / `swFlangePositionTypeBendOutside`

**② ## Remarks** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**；`Availability` = `SOLIDWORKS 2005 FCS, Revision Number 13.0`。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— `swSheetMetalReliefTypes_e`（§2.2.1）/ `swFlangePositionTypes_e`（§2.3.2）。
★ ★ 注意：`## Parameters` 里内联写的是 **`swSheetMetalRelievObround`**，而 [en] 表里的真名是 **`swSheetMetalReliefObround`** ⇒ **拼写对不上**（官方文本自身）。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 2.6 放样折弯 LoftedBend（2 条）

## 2.6.1 `IFeatureManager.InsertSheetMetalLoftedBend`

**① 精确签名** —— [md] `…\InsertSheetMetalLoftedBend.md`：

```
Feature InsertSheetMetalLoftedBend( System.int ThickDirType, System.double Thickness )
```

★ **2 个参数**。`## Parameters` 内联表：`ThickDirType`: Toggles the thickening direction: `0 = outside` / `1 = inside (default value)`；`Thickness`: Thickness of the bend。[md] `## Returns` = `Pointer to the lofted-bend [[feature]] in the sheet metal part`。

**② ## Remarks** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**；`Availability` = `SOLIDWORKS 2003 FCS, Revision Number 11.0`。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**（`ThickDirType` 是裸 `System.int`，取值表内联在 `## Parameters`）。
**⑤ 废弃链** —— [md] 原文：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalLoftedBend2]].`

**前置一句话**：查不到（无 Remarks 段）。
**配方一句话**：查不到（无 Examples 段）。

---

## 2.6.2 `IFeatureManager.InsertSheetMetalLoftedBend2` ★ 现行版 ★ **点名 `Mark = 1`**

**① 精确签名** —— [md] `…\InsertSheetMetalLoftedBend2.md`：

```
Feature InsertSheetMetalLoftedBend2( System.int ThickDirType, System.double Thickness, System.bool BFormed, System.double DRadius, System.bool BReferToEndPoint, System.int EFacetOption, System.double DChordTol, System.int INumBends, System.double DSegLength, System.double DSegAngle )
```

★ **10 个参数**（`…1` 的 2 参 + 8）。[md] `## Returns` = `[[IFeature]]`。
`## Parameters` 里 `BFormed`: True to insert a **formed** lofted bend; false to insert a **bent** lofted bend (default) · `DRadius`: Bend radius; **valid only if BFormed is false** · `BReferToEndPoint`: True to calculate facet transitions using theoretical vertexes, false … using the smallest possible arcs that avoid interference between bend areas · `EFacetOption`: Faceting option as defined in `[[swLoftedBendFacetOptions_e]]` · 后 4 个 `DChordTol` / `INumBends` / `DSegLength` / `DSegAngle` **各带 valid-only 条件**（见 F4 的逐字摘录）。

**② ## Remarks 逐字** —— [md] 原文片段 `with Mark = 1`（★★ **本域第二个点名 mark 的成员**）：

> ```
> ## Remarks
> Before calling this method, you must select at least two sketch profiles that are on parallel planes. You can either multi-select them in the graphics area or call [[IModelDocExtension::SelectByID2]] with Mark = 1 for each sketch profile you want to select.
> ```

[chm-api] 同段逐字（去标签后一致）；`Availability` = `SOLIDWORKS 2014 FCS, Revision Number 22.0`。

**③ 官方例子调用序** —— 例子文件名 `Insert_Lofted_Bend_Feature_Example_VB.md`（[ex] 路径存在，但**本机该 `.md` 文件长度 = 1（空壳）**）⇒ **逐字调用序查不到**（[chm-api] 的 `…sldworksapi\Insert_Lofted_Bend_Feature_Example_VB.htm` 本轮未打开）。

**④ 枚举** —— `EFacetOption` → `swLoftedBendFacetOptions_e`（4 个成员，见 F4）。
★ ★ `DChordTol` / `INumBends` 的条件里引用的 `swChordTolerance`(0) / `swBendsPerTransitionSegment`(1) **存在**；
★ `DSegLength` / `DSegAngle` 引用的 `swSegmentLength` / `swSegmentAngle` **不存在**（F4）。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：`…you must select at least two sketch profiles that are on parallel planes … call IModelDocExtension::SelectByID2 with **Mark = 1** for each sketch profile you want to select.`
**配方一句话**：查不到（3 个例子的 `.md` 在本机是空壳）。

---

## 2.7 三维折弯 3D Bend（1 条）

## 2.7.1 `IFeatureManager.InsertSheetMetal3dBend`

**① 精确签名** —— [md] `…\InsertSheetMetal3dBend.md`：

```
Feature InsertSheetMetal3dBend( System.double Angle, System.bool BUseDefaultRadius, System.double Radius, System.bool FlipDir, System.short BendPos, CustomBendAllowance PCBA )
```

★ **6 个参数**。描述句逐字：`Inserts a 3D bend in sheet metal part.`；[md] `## Returns` = `Pointer to the [[IFeature]] object`。
`## Parameters` 内联表：`Angle`: **Angle of the bend in radians** · `BUseDefaultRadius`: True to use the default radius, false to use the value specified in radius · `BendPos`: Bend position: `0 = bend centerline` / `1 = material inside` / `2 = material outside` / `3 = bend outside` · `PCBA`: **If…**/**Then…**（同 §2.4）。

**② ## Remarks** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**；`Availability` = `SOLIDWORKS 2005 FCS, Revision Number 13.0`。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**（`BendPos` 是裸 `System.short`，取值表内联）。
**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：查不到（无 Remarks 段）。
**配方一句话**：查不到（无 Examples 段）。

---

## 2.8 转钣金 ConvertToSheetMetal（2 条）

| 项 | `InsertConvertToSheetMetal` | `InsertConvertToSheetMetal2` |
|---|---|---|
| [md] 文件 | `…\IFeatureManager\InsertConvertToSheetMetal.md` | `…\IFeatureManager\InsertConvertToSheetMetal2.md` |
| 签名 | `System.bool InsertConvertToSheetMetal( Thickness, ReverseThickDir, FindBends, Radius, Gap, ReliefType, ReliefRatio )` | `System.bool InsertConvertToSheetMetal2( …前 7 同 …, OverlapType, OverlapRatio, KeepBody )` |
| **参数个数** | **7** | **10** |
| [md] `## Returns` | `True if a Convert-Solid sheet metal feature is created, false if not` | 同（逐字） |
| ② `## Remarks` | **没有该段**。**查不到**。[chm-api] 也没有 | 原文片段 `Read the SOLIDWORKS Help`：`Read the SOLIDWORKS Help to learn more about converting to sheet metal.`（**不含任何前置**） |
| ③ 例子 | [md] 无 `## Examples` 段 ⇒ **查不到** | [md] 无 `## Examples` 段 ⇒ **查不到**（`Insert_Convert_to_Sheet_Metal_Example_VB.md` 存在但本轮未读） |
| ④ 枚举 | `ReliefType` → `swSheetMetalReliefTypes_e` | 同上 + `OverlapType` 是**内联表**：`1=Open butt` / `2=Overlap` / `3=Underlap` |
| ⑤ 废弃链 | `Obsolete. Superseded by [[IFeatureManager::InsertConvertToSheetMetal2]].`；[chm-api] 同句逐字；**无 `Availability` 段** | `Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].`；[chm-api] 同句逐字；`Availability` = `SOLIDWORKS 2011 FCS, Revision Number 19.0` |

★ ★ **实参配方**：[ex] `Insert_Sheet_Metal_Base_Flange_Example_VB.md` 里逐字出现两处
`boolstatus = Part.FeatureManager.InsertConvertToSheetMetal(0.002, False, False, 0.004, 0.002, 0, 0.5)`
（`Thickness=0.002` · `ReverseThickDir=False` · `FindBends=False` · `Radius=0.004` · `Gap=0.002` · `ReliefType=0` · `ReliefRatio=0.5`），
★ 且两处**之前紧跟** `boolstatus = Part.Extension.SelectByID2("", "FACE", …, True, 0, Nothing, 0)`（**mark 0**，选面）—— ★ 这是官方例子里唯一透出的转钣金预选口径。

**前置一句话**：两条都**查不到**（`…2` 的 Remarks 只让读者去看 Help）。
**配方一句话**：`SelectByID2("", "FACE", …, mark 0)` → `InsertConvertToSheetMetal(0.002, False, False, 0.004, 0.002, 0, 0.5)`。

---

## 2.9 钣金加强筋 Gusset（3 条 · **与焊件族同名、接口只差一个 `S`**）

★ ★ **归属事实（对账必读）**：这三条的 [md] `## See Also` **全部**指向 `[[ISMGussetFeatureData Interface]]`；
★ 而 `api-03-weldment.md` §2 抄的焊件族 `InsertGussetFeature{,2,3}` 的 See Also 指向 `[[IGussetFeatureData Interface]]`。
★ ⇒ **两族只差一个字母 `S`**，用错接口的表现与本仓 `known-facts.md` 事实 36 记录的一致。
★ 本节只记录原文事实，不作判断。

| 项 | `InsertSheetMetalGussetFeature` | `…2` | `…3` ★现行版 |
|---|---|---|---|
| **参数个数** | **21** | **24**（+`ArrayOfFaces` / `ArrayRefLines` / `ArrayRefPoints`） | **24**（+`BOverrideDoc` / `BShowProfile` / `BShowCenter`） |
| ② `## Remarks` | **有** | **有** | **有**（最长，137 行里约 70 行是 Remarks） |
| ③ 例子 | 无 `## Examples` 段 ⇒ 查不到 | 无 ⇒ 查不到 | [md] 列 `Insert_Sheet_Metal_Gusset_Feature_Example_{VB,VBNET,CSharp}`；**`.md` 本轮未读**（`.htm` 在 [chm-api] 树里存在）⇒ 逐字调用序**查不到** |
| ⑤ 废弃链 | `Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalGussetFeature3]].` | 同（**→ 3，不是 2**） | `Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].` |
| [chm-api] `Availability` | `SOLIDWORKS 2014 FCS, Revision Number 22.0` | `SOLIDWORKS 2014 FCS, Revision Number 22.0` | `SOLIDWORKS 2015 FCS, Revision Number 23.0` |

### `InsertSheetMetalGussetFeature3` 的 `## Remarks` 逐字（★ 三段式预选表，**未给 mark 数字**）

> ```
> Before calling this method to create a sheet metal gusset feature, you must pre-select faces, lines, edges, vertices, or points as follows:
>
> To...  Call [[IModelDocExtension::SelectByID2]] to select...
>
> Specify the legs of the gusset feature
> - Two flat faces of a bend.
> - or - Two flat faces adjacent to a cylindrical bend face.
> - or - One cylindrical bend face.
> - or - One flat face and one non-planar face adjacent to a toroidal bend.
> - or - One toroidal bend face.
>
> Optionally orient the gusset section plane
> One linear edge or sketch segment that is perpendicular to the gusset section plane.
> If you do not pre-select either entity, then the method uses the bend line adjacent to the gusset legs as the reference.
>
> Optionally position the gusset section plane
> One vertex, sketch point, or reference point.
> If you do not pre-select any one of these entities, then you must set BOffset to true and specify DOffset for an assumed reference point. …
> ```

★ 其余形参的 valid-only 条件逐字：
`DIndentDepth`: Gusset depth; **valid only if ProfDimType = 0** · `DLength`: d1 gusset leg length …; **valid only if ProfDimType = 1** · `DAngle`: …; **valid only if ProfDimType = 1 and BUseAngle is true** · `DOffset`: …; **valid only if BOffset is true** · `DOuterCornerFilletRadius`: …; **valid only if BOuterCornerFilletRadius is true**（★ 官方把形参名写成了条件，自身笔误，逐字保留）· `DEdgeFilletRadius`: …; **valid only if BEdgeFillet is true and GussetType = 1** · `BShowProfile` / `BShowCenter`: …; **valid only if BOverrideDoc is true**。
`ProfDimType` / `GussetType` 各带内联表：`0 = indent` / `1 = profile dimensioning`；`0 = rounded back` / `1 = flat back`。

**④ 枚举** —— 签名里**无枚举形参**（两个 `int` 形参都是内联表）。

**前置一句话**：预选「腿」（两种弯折面 / 一条圆柱折弯面 / 圆柱折弯面 + 非平面面 / 一条圆环折弯面）+ 可选「定向边」+ 可选「定位点」—— ★ **官方没给 mark 数字**。
**配方一句话**：查不到（3 个例子的 `.md` 本轮未读）。

---

## 2.10 钣金 / 展开文件夹（2 条）

| 项 | `GetSheetMetalFolder` | `GetFlatPatternFolder` |
|---|---|---|
| 签名 | `System.object GetSheetMetalFolder()` | `System.object GetFlatPatternFolder()` |
| **参数个数** | **0** | **0** |
| 描述句逐字 | `Gets the interface to the sheet metal folder feature in the FeatureManager design tree.` | `Gets the interface to the flat-pattern folder feature in the FeatureManager design tree.` |
| [md] `## Returns` | `[[ISheetMetalFolder]]` | `[[IFlatPatternFolder]]` |
| ② `## Remarks` | **没有该段**。**查不到**。[chm-api] 也没有 | **没有该段**。**查不到**。[chm-api] 也没有 |
| ③ 例子 | [md] 列 `Get_Sheet_Metal_Folder_Feature_Example_{VB,VBNET,CSharp}`；**本轮未读** ⇒ 逐字调用序**查不到** | [md] 列 `Get_Flat_Pattern_Folder_Feature_Example_{VB,VBNET,CSharp}`；**本轮未读** ⇒ **查不到** |
| ⑤ 废弃链 | **非 Obsolete**。**查不到后继** | **非 Obsolete**。**查不到后继** |
| [chm-api] `Availability` | `SOLIDWORKS 2014 FCS, Revision Number 22.0` | `SOLIDWORKS 2014 FCS, Revision Number 22.0` |

---

## 2.11 钣金域汇总表（★ 只列抄到的事实）

| # | 成员 | 形参数 | md 有 Remarks? | 有 Examples? | Obsolete → 后继 | 官方点名 mark? | Availability（[chm-api]） |
|---|---|---|---|---|---|---|---|
| 1 | `CreateCustomBendAllowance` | **0** | ✗ | ✓ | 否 | ✗ | SW2003 FCS R11.0 |
| 2 | `InsertSheetMetalBaseFlange` | 16 | ✗ | ✗ | **是** → `…BaseFlange2` | ✗ | SW2003 FCS R11.0 |
| 3 | `InsertSheetMetalBaseFlange2` | **19** | ✓ | ✓ | **是** → `CreateDefinition`+`CreateFeature` | **✓ mark 8** | SW2010 FCS R18.0 |
| 4 | `InsertSheetMetalEdgeFlange` | 13 | ✗ | ✗ | **是** → `…EdgeFlange2` | ✗ | （无该段） |
| 5 | `InsertSheetMetalEdgeFlange2` | 13 | ✓ | ✓ | **是** → `CreateDefinition`+`CreateFeature` | ✗ | **SW2007 FCS R15.0** |
| 6 | `IInsertSheetMetalEdgeFlange2` | 15 | ✓ | ✗ | **是** → 同上 | ✗ | SW2007 FCS R15.0 |
| 7 | `InsertSheetMetalHem` | 9 | ✗ | ✗ | **是** → `…Hem2` | ✗ | **SW2001Plus** FCS R10.0 |
| 8 | `InsertSheetMetalHem2` | **16** | ✓ | ✓ | 否 | ✗ | SW2011 SP03 R19.3 |
| 9 | `InsertSheetMetalMiterFlange` | 14 | ✗ | ✗ | 否 | ✗ | SW2005 FCS R13.0 |
| 10 | `InsertSheetMetalLoftedBend` | 2 | ✗ | ✗ | **是** → `…LoftedBend2` | ✗ | SW2003 FCS R11.0 |
| 11 | `InsertSheetMetalLoftedBend2` | **10** | ✓ | ✓* | 否 | **✓ Mark = 1** | SW2014 FCS R22.0 |
| 12 | `InsertSheetMetal3dBend` | 6 | ✗ | ✗ | 否 | ✗ | SW2005 FCS R13.0 |
| 13 | `InsertConvertToSheetMetal` | 7 | ✗ | ✗ | **是** → `…ConvertToSheetMetal2` | ✗ | （无该段） |
| 14 | `InsertConvertToSheetMetal2` | 10 | ✓ | ✗ | **是** → `CreateDefinition`+`CreateFeature` | ✗ | SW2011 FCS R19.0 |
| 15 | `InsertSheetMetalGussetFeature` | 21 | ✓ | ✗ | **是** → `…GussetFeature3` | ✗ | SW2014 FCS R22.0 |
| 16 | `InsertSheetMetalGussetFeature2` | 24 | ✓ | ✗ | **是** → `…GussetFeature3` | ✗ | SW2014 FCS R22.0 |
| 17 | `InsertSheetMetalGussetFeature3` | 24 | ✓ | ✓* | **是** → `CreateDefinition`+`CreateFeature` | ✗ | SW2015 FCS R23.0 |
| 18 | `GetSheetMetalFolder` | **0** | ✗ | ✓* | 否 | ✗ | SW2014 FCS R22.0 |
| 19 | `GetFlatPatternFolder` | **0** | ✗ | ✓* | 否 | ✗ | SW2014 FCS R22.0 |
| ↳ | `InsertSheetMetalCornerTrim`（**不在本节，见 F6**） | 5 | ✗ | ✗ | 否 | ✗ | SW2003 FCS R11.0 |

★ 「✓*」= md 的 `## Examples` 列了例子文件，但**本轮未读其内容**，故逐字调用序仍记为「查不到」。
★ **已读出逐字调用序的 4 个成员**：`InsertSheetMetalBaseFlange2` · `InsertSheetMetalEdgeFlange2` · `InsertSheetMetalHem2` · `CreateCustomBendAllowance`（另 `InsertConvertToSheetMetal` 的实参是从 base-flange 例子里抄到的）。

## 2.12 钣金域「查不到」清单（★ 不猜）

1. `InsertSheetMetalBaseFlange` / `InsertSheetMetalEdgeFlange` / `InsertSheetMetalHem` / `InsertSheetMetalMiterFlange` / `InsertSheetMetal3dBend` / `InsertSheetMetalLoftedBend` 的 `## Remarks` 段 —— 文件里没有。
2. `InsertSheetMetalEdgeFlange` 的 13 个形参对应哪个枚举 —— 该文件 `## Parameters` **全写 `No description`**。
3. `InsertSheetMetalHem2` / `InsertSheetMetalGussetFeature3` 的 **mark 数字** —— 官方 Remarks **都没点**（Hem2 只说「Select one or more edges」，Gusset3 只说「you must pre-select faces, lines, edges, vertices, or points」）。
4. `InsertSheetMetalLoftedBend2` / `InsertSheetMetalGussetFeature3` / `GetSheetMetalFolder` / `GetFlatPatternFolder` 的**逐字调用序** —— 其 `## Examples` 指向的 3～4 个例子 `.md` 本轮未读（其中 `Insert_Lofted_Bend_Feature_Example_VB.md` 在本机**长度 = 1，空壳**）。
5. `ICustomBendAllowance.Type` / `.KFactor` 的取值域与单位 —— 其 md 本轮未读。
6. `swLoftedBendFacetOptions_e.swSegmentLength` / `swSegmentAngle` —— 见 F4，两套官方源都不存在。
7. `swSheetMetalRelievObround` —— 只在 `InsertSheetMetalMiterFlange.md` 的内联表里出现，[en]/[chm-en] 表里的真名是 `swSheetMetalReliefObround`。

---

# 三 · 工程图域契约摘要（拟 `api-05-drawing.md`）

**抄录范围**：
`IDrawingDoc` 的**视图族**（普通/剖视/局部放大/断裂/辅助/相对）+ **尺寸族**（非关联 4 族）+ **注释族**（GTol / 基准符号 / 表面粗糙度 / 气泡 / 通用表）；
`ISheet` 的**图纸格式族**；`IGtol` 的公差/基准成员；`IModelDoc2.InsertDatumTag2` / `IModelDocExtension.InsertSurfaceFinishSymbol3` / `InsertBomTable4` 三个现行版落点。共 **43 条**。

---

## 3.0 名字缺席与源缺口（铁律 5）

| 想找的 | 结果 | 证据 |
|---|---|---|
| `ISheet` / `IView` / `INote` / `ITableAnnotation` / `IModelView` / `ISectionViewData` 在 CHM .NET 树的成员页 | **查不到**（各 **0** 个） | 见 F5 的计数表 |
| `IDrawingDoc.CreateTableAnnotation` | **查不到**（名字不存在） | `C:\swapi\types\IDrawingDoc\` 下无此文件；真名是 `InsertTableAnnotation{,2}` |
| `IDrawingDoc.CreateBrokenView` | **查不到** | 同目录无此文件；断裂视图是 **`BreakView`**（执行）+ `InsertBreakHorizontal` / `InsertBreakVertical`（画断裂线） |
| `IDrawingDoc.CreateSurfaceFinishSymbol` | **查不到** | 表面粗糙度现行版在 **`IModelDocExtension.InsertSurfaceFinishSymbol3`**；`IDrawingDoc.InsertSurfaceFinishSymbol` 是被它取代的旧版 |
| `IDrawingDoc.CreateDatumTag` | **查不到** | 基准符号现行版在 **`IModelDoc2.InsertDatumTag2`** |

---

## 3.1 普通视图 DrawViewFromModelView（3 条）

| 项 | `CreateDrawViewFromModelView` | `…2` | `…3` ★现行版 |
|---|---|---|---|
| **参数个数** | 5 | 5 | **5** |
| 返回类型 | `View` | `View` | `View CreateDrawViewFromModelView3( ModelName, ViewName, LocX, LocY, LocZ )` |
| ② `## Remarks` | ✗ | ✗ | ✓（见下） |
| ③ 例子 | ✗ | ✗ | [md] 列 `Insert_Model_Annotations_Example_{CSharp,VBNET,VB}`（本轮未读）⇒ 逐字**查不到** |
| ⑤ 废弃链 | `Obsolete. Superseded by [[IDrawingDoc::CreateDrawViewFromModelView3]].`（★ **跳过 2**） | `… → [[IDrawingDoc::CreateDrawViewFromModelView3]]` | **非 Obsolete** |
| [chm-api] `Availability` | （无该段） | （无该段） | `SOLIDWORKS 2005 SP2, Revision Number 13.2` |

★ ★ `[chm-api]` 与 [md] 一致地**跳过 `2`**：`…~CreateDrawViewFromModelView.html` 里逐字是
`Obsolete. Superseded by IDrawingDoc::CreateDrawViewFromModelView3`（**没有** `…2`）。
★ 但 `CreateDrawViewFromModelView2.md` 自己确实存在、且它自己也写着「→ 3」⇒ 两代都直接指向 3。

### `CreateDrawViewFromModelView3` 的 `## Remarks` 逐字（★ **不含 "Before calling"**）

> ```
> This method:
> - Places the center of the view at the specified location.
> - Uses the [swAutomaticScaling3ViewDrawings](...) setting to set the view scale. …
>
> If a model document  is currently open in SOLIDWORKS and you don't know its full pathname, call [[IModelDoc2::GetPathName]] to populate ModelName. Include the **.sldprt** or **.sldasm** extension in the pathname.
>
> ViewName must exactly match the name of the model view. For example, the names of the standard views begin with an asterisk. This asterisk is part of the view name and must be included (for example, "*Front").
> ```

★ `LocX`/`LocY`/`LocZ` 的 `## Parameters` 描述逐字带单位：**`x location of drawing view center in meters`**。

**④ 枚举** —— 签名里**无枚举形参**（但 Remarks 里点名 `swAutomaticScaling3ViewDrawings` 这个**设置项**，**不是枚举**；其 `.md` 本轮未读）。
**前置一句话**：**查不到**（Remarks 里没有 `Before calling`；它只讲 ModelName/ViewName 怎么填）。
**配方一句话**：查不到（例子的 `.md` 本轮未读）。

---

## 3.2 剖视 SectionView（6 条）

| 项 | 成员 | 参数 | md 有 Remarks? | Obsolete → 后继 | Availability（[chm-api]） |
|---|---|---|---|---|---|
| 1 | `CreateSectionView` | **0** | ✓ | 否 | （无该段） |
| 2 | `CreateSectionViewAt` | 5 | ✗ | **是** → `…At4` | （无该段） |
| 3 | `CreateSectionViewAt2` | 10 | ✗ | **是** → `…At4`（★ 跳过 `At3`） | （无该段） |
| 4 | `CreateSectionViewAt3` | 11 | ✗ | **是** → `…At4` | （无该段） |
| 5 | `CreateSectionViewAt4` | **6** | ✓ | **是** → `…At5` | SW2005 FCS R13.0 |
| 6 | `CreateSectionViewAt5` ★现行 | **7** | ✓ | 否 | SW2010 FCS R18.0 |

★ ★ **形状变过（原文事实）**：`At2`/`At3` 用 **10 个 bool 形参**（`NotAligned` / `IsOffsetSection` / `Label` / `Chgdirection` / `Scwithmodel` / `Partial` / `Dispsurfcut` / …），且 `At2` 的 `## Parameters` **10 行全写 `No description`**；
★ `At4` 起改成 **一个 `System.int Options` 位掩码**（`swCreateSectionViewAtOptions_e`）+ 字符串 `SectionLabel`，参数数从 11 掉到 6（`At5` 再加 `SectionDepth` 到 7）。
★ ★ **返回类型也变过**：`At2` 返回 `System.object`，`At3`/`At4`/`At5` 返回 `View`。
★ ★ **实例里有一处官方笔误**：`CreateSectionViewAt2` 与 `CreateSectionViewAt3` 的 Obsolete 都指向 `At4`，**跳过了 `At3`**；[chm-api] 两页均逐字相同。

### `CreateSectionViewAt5` 的 `## Remarks` 逐字（★ **点名前置，但没给 mark**）

> ```
> Before calling this method, select the section line or lines to use as a section line.
>
> This method runs silently; the end-user is not prompted for a label.
>
> Use [[IView::GetSection]] to get the [[IDrSection]] object, and use [[IDrSection::SetLabel2]] to set the name for the label, which provides a warning if the name is a duplicate and the standard does not accept duplicate names.
> ```

（`CreateSectionViewAt4` 的 Remarks 与此**逐字相同**，只差 `the section line or the lines` 的 `the`。）
★ 对照 `CreateSectionView`（0 参版）的 Remarks **只有一句**：`This method prompts the end-user for a name for the new section view.` ⇒ 它会弹窗，`At*` 版不会。

**③ 官方例子调用序与配方实参** —— [ex] `Create_Section_View_and_Get_Some_Data_Example_VB.md`（本轮读了全文 77 行），逐字：

```vbnet
boolstatus = swDrawing.ActivateView("Drawing View4")
swModel.ClearSelection2 True
Set swSketchMgr = swModel.SketchManager
Set swSketchSegment = swSketchMgr.CreateLine(-1.383705, 2.078706, 0#, 2.747162, 0.0441, 0#)
Set excludedComponents = Nothing
Set swView = swDrawing.CreateSectionViewAt5(0.1604082711061, 0.2048687170364, 0, "D", 32, (excludedComponents), 0.00835)
…
Set swSectionView = swView.GetSection
swSectionView.SetAutoHatch True
swSectionView.SetLabel2 "ABCD"
swSectionView.SetDisplayOnlySurfaceCut False
swSectionView.SetPartialSection False
swSectionView.SetReversedCutDirection False
swSectionView.SetScaleWithModelChanges True
```

★ ★ 调用序（这是本域最关键的一条配方）：**`ActivateView("Drawing View4")` → `ClearSelection2 True` → `SketchManager.CreateLine(...)`（在活动视图里画一条草图线作为剖切线）→ 调 7 参 → `swView.GetSection` → 逐项设置/读取**。
★ 实参逐位：`X=0.1604082711061` · `Y=0.2048687170364` · `Z=0` · `SectionLabel="D"` · `Options=32`（按 §3.9 表 = **`swCreateSectionView_DisplaySurfaceCut`** 32 或 0x20）· `ExcludedComponents=(excludedComponents)`（值为 `Nothing`）· `SectionDepth=0.00835`。
★ ★ **官方没给 mark**：例子里那条剖切线是**用 `SketchManager.CreateLine` 画出来的**，不是 `SelectByID2` 选的。

**④ 枚举** —— `Options` → `swCreateSectionViewAtOptions_e`（描述 `Options that affect the section view that is created. [Bitmask]` —— 官方点名 **Bitmask**）：

| Member | Value |
|---|---|
| `swCreateSectionView_NotAligned` | 1 / 0x1 |
| `swCreateSectionView_OffsetSection` | 2 / 0x2 |
| `swCreateSectionView_ChangeDirection` | 4 / 0x4 |
| `swCreateSectionView_ScaleWithModel` | 8 / 0x8 |
| `swCreateSectionView_Partial` | 16 / 0x10 |
| `swCreateSectionView_DisplaySurfaceCut` | 32 / 0x20 |
| `swCreateSectionView_ExcludeFasteners` | 64 / 0x40 |
| `swCreateSectionView_CutSurfaceBodies` | 128 / 0x80 |

★ ★ **`At2` / `At3` 的那 7 个 bool 形参与这张表是「一位拆成一个 bool」的关系**（`NotAligned`↔1、`IsOffsetSection`↔2、`Chgdirection`↔4、`Scwithmodel`↔8、`Partial`↔16、`Dispsurfcut`↔32；第 7 个 bool 无对应成员，**`ExcludedComponents` 不是位**）。★ 官方没写这条对应关系 ⇒ 这里只作事实对照，不断言。

---

## 3.3 局部放大 DetailView（5 条）

| 项 | 成员 | 参数 | md 有 Remarks? | Obsolete → 后继 | Availability（[chm-api]） |
|---|---|---|---|---|---|
| 1 | `CreateDetailView` | **0** | ✗ | **是** → `…At3` | （无该段） |
| 2 | `CreateDetailViewAt` | 3 | ✗ | **是** → `…At3` | （无该段） |
| 3 | `CreateDetailViewAt2` | 3 | ✗ | **是** → `…At3` | （无该段） |
| 4 | `CreateDetailViewAt3` | 9 | ✗ | **是** → `…At4` | SW2001 FCS R9.0 |
| 5 | `CreateDetailViewAt4` ★现行 | **12** | **✗** | 否 | SW2017 FCS R25.0 |

★ ★ `At2` 的签名逐字是 `System.bool CreateDetailViewAt2( System.double X, System.double Y, System.double Z )` —— ★ **返回 bool**，而现行版 `At4` 返回 `System.object`。
★ `At3` 返回 `System.object`，`At4` 也返回 `System.object`，[md] 的 `## Returns` 都写 `Detail [[view]]`。

### ★★ `CreateDetailViewAt4`：**官方没有 `## Remarks` 段**

[md] `CreateDetailViewAt4.md` 的段序是：front-matter / 标题 / 描述句 / Signature / Parameters / Returns / Examples / See Also —— **没有 `## Remarks`**。
[chm-api] `…~CreateDetailViewAt4.html` 同样**没有 `Remarks` 段**。
⇒ ★ **局部放大视图的调用前置在两套官方源里都「查不到」**，只能从例子反推。

### `CreateDetailViewAt4` 的 12 个形参（逐字）

| 形参 | 官方描述（逐字） |
|---|---|
| `X` / `Y` / `Z` | X / Y / Z position for the detail view |
| `Style` | Style for the detail view as defined in `[[swDetViewStyle_e]]` |
| `Scale1` / `Scale2` | Scale numerator / Scale denominator |
| `LabelIn` | Detail view label |
| `Showtype` | Type of sketch for the detail view as defined in `[[swDetCircleShowType_e]]` |
| `FullOutline` | True to show a full outline, false to not; **valid only if NoOutline is false** |
| `JaggedOutline` | True to show a jagged outline, false to not; **only valid if NoOutline is false** |
| `NoOutline` | True to not show an outline, false to show an outline |
| `ShapeIntensity` | Intensity of jagged outline; **valid range is 1 (most) to 5 (least)** and only valid if JaggedOutline is true and NoOutline is false |

★ `At3`（9 参）只有到 `FullOutline`；`JaggedOutline` / `NoOutline` / `ShapeIntensity` 三个是 `At4` 新增的。

**③ 官方例子调用序与配方实参** —— [ex] `Create_Detail_Circle_and_Detail_View_Example_VB.md`（本轮读了全文 79 行），逐字：

```vbnet
status = swDrawing.ActivateView("Drawing View4")
Set swSketchManager = swModel.SketchManager
Set swSketchSegment = swSketchManager.CreateCircle(0.007581, 0.053509, 0#, 0.013533, 0.016475, 0#)
Set swView = swDrawing.CreateDetailViewAt4(0.22305342706156, 7.62140266484527E-02, 0, swDetViewSTANDARD, 1, 1, "A", swDetCircleCIRCLE, True, True, False, 5)
swModel.ClearSelection2 True
status = swDrawing.ActivateView("Drawing View5")
Set swDetailCircle = swView.GetDetail
Debug.Print " Label: " & swDetailCircle.GetLabel
If Not swDetailCircle.NoOutline Then
    If swDetailCircle.JaggedOutline Then
        swDetailCircle.ShapeIntensity = 2
```

★ ★ **前置只能从这里读出来**：`ActivateView(父视图)` → `SketchManager.CreateCircle(...)`（画详图圆）→ 调 12 参 → `ClearSelection2` → `ActivateView(新视图)` → `swView.GetDetail`。
★ 实参逐位：`X=0.22305342706156` · `Y=7.62140266484527E-02` · `Z=0` · `Style=swDetViewSTANDARD`(0) · `Scale1=1` · `Scale2=1` · `LabelIn="A"` · `Showtype=swDetCircleCIRCLE`(1) · `FullOutline=True` · `JaggedOutline=True` · `NoOutline=False` · `ShapeIntensity=5`。
★ 例子随后把 `ShapeIntensity` 改成 `2` 再打印。

**④ 枚举** —— 两个：
`swDetViewStyle_e`（描述 `Detail view styles.`）：`swDetViewSTANDARD` 0 · `swDetViewBROKEN` 1 · `swDetViewLEADER` 2 · `swDetViewNOLEADER` 3 · `swDetViewCONNECTED` 4。
`swDetCircleShowType_e`（描述 `Types of circles or profiles to use for detail views.`）：`swDetCirclePROFILE` 0 · `swDetCircleCIRCLE` 1 · `swDetCircleDONTSHOW` 2。

**前置一句话**：**查不到**（官方无 Remarks；例子给出的顺序是 `ActivateView` → `SketchManager.CreateCircle` → 调参）。
**配方一句话**：`CreateDetailViewAt4(0.22305342706156, 7.62140266484527E-02, 0, swDetViewSTANDARD, 1, 1, "A", swDetCircleCIRCLE, True, True, False, 5)`。

---

## 3.4 辅助视图 AuxiliaryView（2 条）★ 同上，**现行版也没有 Remarks**

| 项 | 成员 | 参数 | md 有 Remarks? | Obsolete → 后继 | Availability（[chm-api]） |
|---|---|---|---|---|---|
| 1 | `CreateAuxiliaryViewAt` | 4 | ✗ | **是** → `…At2` | （无该段） |
| 2 | `CreateAuxiliaryViewAt2` ★现行 | **7** | **✗** | 否 | SW2001 FCS R9.0 |

`CreateAuxiliaryViewAt2` 描述句逐字：`Creates an auxiliary view based on a selected edge in a drawing view.`
签名逐字：`System.object CreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )`
形参逐条：`NotAligned`: True aligns the view from its owner, false does not · `Label`: String that holds label of the auxiliary view · `Showarrow`: True shows the arrow, false hides the arrow · `Flip`: True flips the side shown in the auxiliary view, false does not。
★ `CreateAuxiliaryViewAt`（旧版）返回 **`System.bool`**，参数只有 `X, Y, Z, NotAligned`，且 `## Parameters` **4 行全写 `No description`**。

**④ 枚举** —— 签名里**无枚举形参**。
**前置一句话**：**查不到**（md 与 [chm-api] 都没有 Remarks 段）；描述句只说「based on a selected edge」，**未给 mark**。
**配方一句话**：查不到（该成员 md 无 `## Examples` 段；[chm-api] 同名页无 Remarks）。

---

## 3.5 相对视图 RelativeView（1 条）★★ **本域唯一被官方点名 mark 数字的成员**

## 3.5.1 `IDrawingDoc.CreateRelativeView`

**① 精确签名** —— [md] `…\IDrawingDoc\CreateRelativeView.md`：

```
View CreateRelativeView( System.string ModelName, System.double XPos, System.double YPos, System.int ViewDirFront, System.int ViewDirRight )
```

★ **5 个参数**。[md] `## Returns` = `[[View]]`。
`## Parameters`：`ModelName`: Path and filename of the model for which to create a relative drawing view · `XPos` / `YPos`: x / y coordinate where to create the relative drawing view · `ViewDirFront` / `ViewDirRight`: Orientation as defined by `[[swRelativeViewCreationDirection_e]]`。

**② ## Remarks 逐字** —— [md] 原文片段 `selection mark 1`（★★ **mark 表**）：

> ```
> ## Remarks
> Select:
>
> - the first orientation component using selection mark 1.
>
> - the second orientation component using selection mark 2.
>
> For multi-body parts only, select bodies to be shown in the created view using selection mark 4.
> ```

[chm-api] 同段逐字（去标签后一致）；`Availability` = `SOLIDWORKS 2007 FCS, Revision Number 15.0`。

**③ 官方例子调用序与配方实参** —— [ex] `Create_Relative_Drawing_View_Example_VB.md`（本轮读了全文 80 行），逐字：

```vbnet
Set swDrawing = swApp.ActiveDoc
numViews = swDrawing.GetDrawingPaletteViewNames
…
Set swView = swDrawing.DropDrawingViewFromPalette2(viewPaletteName, 0#, 0#, 0#)
…
swApp.ActivateDoc3 "maingrip.sldprt", False, swRebuildOnActivation_e.swUserDecision, errors
Set swModel = swApp.ActiveDoc
Set swModelDocExt = swModel.Extension
swModel.ClearSelection2 True
status = swModelDocExt.SelectByID2("", "FACE", 4.66263268498324E-02, 5.58799999987514E-03, -6.17351393179888E-03, False, 1, Nothing, 0)
status = swModelDocExt.SelectByID2("", "FACE", 5.04738910727269E-02, 1.67315253537481E-03, -4.96149996774875E-03, True, 2, Nothing, 0)
swApp.ActivateDoc3 "maingrip - Sheet1", False, swRebuildOnActivation_e.swUserDecision, errors
Set swDrawing = swApp.ActiveDoc
fileName = "C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2018\samples\tutorial\api\maingrip.sldprt"
Set swView = swDrawing.CreateRelativeView(fileName, 0.203608914116486, 0.493530187561698, swRelativeViewCreationDirection_FRONT, swRelativeViewCreationDirection_RIGHT)
status = swDrawing.ActivateView("Drawing View2")
```

★ ★ 调用序：**必须在「零件文档」里预选两个面（mark `1` 和 `2`），再切到「工程图文档」，然后调 `CreateRelativeView`** —— 例子里的注释头逐字写着 `5. Creates and inserts a relative drawing view using the selected faces.`
★ 实参逐位：`ModelName=fileName` · `XPos=0.203608914116486` · `YPos=0.493530187561698` · `ViewDirFront=swRelativeViewCreationDirection_FRONT`(0) · `ViewDirRight=swRelativeViewCreationDirection_RIGHT`(1)。
★ ★ **Remarks 与例子逐字一致**（mark 1 / mark 2）。

**④ 枚举** —— `ViewDirFront` / `ViewDirRight` → `swRelativeViewCreationDirection_e`（描述 `Relative view creation directions.`）：
`swRelativeViewCreationDirection_FRONT` 0 · `_RIGHT` 1 · `_TOP` 2 · `_BACK` 3 · `_LEFT` 4 · `_BOTTOM` 5 · `_AUXILIARY` 6。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：在零件文档里 `SelectByID2("", "FACE", …)` **mark 1 选第一个朝向分量、mark 2 选第二个**；多体零件另用 **mark 4** 选要显示的体。
**配方一句话**：`(fileName, 0.203608914116486, 0.493530187561698, swRelativeViewCreationDirection_FRONT, swRelativeViewCreationDirection_RIGHT)`。

---

## 3.6 断裂视图 BreakView（3 条）

| 项 | 成员 | 参数 | md 有 Remarks? | 有 Examples? | [chm-api] `Availability` |
|---|---|---|---|---|---|
| 1 | `InsertBreakHorizontal` | **0** | ✓ | ✗ | （无该段） |
| 2 | `InsertBreakVertical` | **0** | ✓ | ✗ | （无该段） |
| 3 | `BreakView`（执行） | **0** | ✓ | ✓ | （无该段） |
| 4 | `UnBreakView` | **0** | **✗** | ✓ | （无该段） |

★ ★ **三步调用序完全写在 Remarks 里**（不是参数驱动的）：

`BreakView.md` 的 `## Remarks` 逐字：

> ```
> Use [[IDrawingDoc::InsertBreakHorizontal]] or [[IDrawingDoc::InsertBreakVertical]] to insert break lines to a drawing view. Customize the break by dragging and repositioning the break lines. Then, call this method to create the break view.
>
> You can set the font of the break lines using [[IBreakLine::Style]].
> ```

`InsertBreakHorizontal.md` 的 `## Remarks` 逐字：

> ```
> To create the break view, use [[IDrawingDoc::BreakView]].
>
> You can:
> - Customize the break by dragging and repositioning the break lines.
> - Set the font of the break lines using [[IBreakLine::Style]].
> ```

★ `UnBreakView` 描述句逐字：`Removes a break in the selected drawing view.` —— ★ **没有 `## Remarks` 段**，选哪个视图这个前置**查不到**。
★ ★ `InsertBreakHorizontal.md` 的 `## See Also` 里有一条死链 `[[IDrawingDoc::UnInsertBreakVertical Method]]`（见 F3-e）。

**④ 枚举** —— 四个成员**都无参、无枚举形参**。
**⑤ 废弃链** —— 四条**均非 Obsolete**。**查不到后继**。
**③ 例子** —— `BreakView` / `UnBreakView` 的 md `## Examples` 列 `Create_Broken_View_Example_{CSharp,VBNET,VB}`；★ **本轮未读** ⇒ 逐字调用序**查不到**。

**前置一句话**：先 `InsertBreakHorizontal` / `InsertBreakVertical` 画断裂线，再拖动调整，然后 `BreakView`。
**配方一句话**：查不到（例子的 `.md` 本轮未读）。

---

## 3.7 非关联尺寸 Non-associative Dimension（4 条 ★现行版）

| 成员 | 参数 | 返回类型 | md 有 Remarks? | 有 Examples? |
|---|---|---|---|---|
| `CreateLinearDim4` | **9** | `System.object` | ✓ | ✗ |
| `CreateDiamDim4` | **7** | `System.object` | ✓ | ✓ |
| `CreateAngDim4` | **9** | `System.object` | ✓ | ✗ |
| `CreateOrdinateDim4` | **9** | `System.object` | ✓ | ✗ |

★ ★ **形状（原文事实）**：四条都**不接收任何几何选择**，全部形参都是 `System.object`（`Array of 3 doubles (x,y,z)`）；官方逐字强调「**`The dimension is not related to the geometry.`** / `It has no relation to your geometry.`」。
★ `CreateLinearDim4` 与 `CreateOrdinateDim4` 有 `Val`（`System.double`）形参；`CreateAngDim4` **没有** `Val`、只有 `TextHeight`；`CreateDiamDim4` 有 `Val`（描述 `Dimension value in meters`）但**没有** `Angle`。
★ `Angle` 形参的描述逐字带单位：`Inclination angle of the text **in radians**`；`TextHeight` 描述逐字：`Text height **in meters**`。
★ `CreateAngDim4` 的 Remarks 逐字还有一句：`This method does not replace [[IDrawingDoc::CreateDiamDim4]] or [[IDrawingDoc::ICreateDiamDim4]]; it changes the number of arguments required to construct the [[IDisplayDimension]] object.`

**⑤ 废弃链** —— 逐条（[md] 与 [chm-api] 逐字一致）：

| 旧版 | Obsolete → |
|---|---|
| `CreateLinearDim` / `CreateLinearDim2` / `CreateLinearDim3` | 全部 → **`CreateLinearDim4`** |
| `CreateDiamDim` / `CreateDiamDim2` / `CreateDiamDim3` | 全部 → **`CreateDiamDim4`** |
| `CreateAngDim` / `CreateAngDim2` / `CreateAngDim3` | 全部 → **`CreateAngDim4`**（★ 跳过 3 是「后继」，但三代都指 4） |
| `CreateOrdinateDim` / `CreateOrdinateDim2` / `CreateOrdinateDim3` | 全部 → **`CreateOrdinateDim4`** |

★ 12 条 Obsolete 行在 `C:\swapi\types\IDrawingDoc\` 里都是 `^Obsolete\.` 开头的独立一行；[chm-api] 抽验 `CreateAngDim` / `CreateAngDim2` / `CreateAngDim3` 三页均为 `Obsolete. Superseded by IDrawingDoc::CreateAngDim4 .`（一致）。
★ `CreateLinearDim{,2,3}` / `CreateOrdinateDim{,2,3}` / `CreateDiamDim{,2,3}` 的参数与 Remarks **本轮未逐条读** ⇒ 逐位签名**查不到**。

**★ `CreateDiamDim4.md` 的 See Also 有 3 个死链**（`IICreateAngDim4` / `IICreateLinearDim4` / `IICreateOrdinateDim4`）—— 见 **F3-a**。

**④ 枚举** —— 四条签名里**无枚举形参**。
**前置一句话**：**查不到**（四条现行版的 Remarks 都是「尺寸与几何无关」的说明，没有 `Before calling`；md 也无 `## Examples` 可抄，`CreateDiamDim4` 例外）。
**配方一句话**：只 `CreateDiamDim4` 有可抄实参 —— [ex] `Create_Non-associative_Diameter_Dimension_Example_VB.md`（**本轮未读**）⇒ **查不到**。

---

## 3.8 图纸格式 ISheet（6 条）

| 成员 | kind | 参数 | md 有 Remarks? | Obsolete → 后继 | `## Returns`（逐字） |
|---|---|---|---|---|---|
| `GetProperties` | method | **0** | ✓ | **是** → `GetProperties2` | `Array of doubles (see **Remarks**)` |
| `GetProperties2` ★现行 | method | **0** | ✓ | 否 | 同上 |
| `SetProperties2` ★现行 | method | **8** | ✓ | 否 | （`void`，无 `## Returns`） |
| `SetScale` | method | **4** | ✓ | 否 | `True if the scale is set, false if not` |
| `SetSheetFormatName` | method | **1** | ✓ | 否 | `True if the name of the sheet format is set, false if not` |
| `IPageSetup` | **property** | **0** | ✓ | 否 | `[[Page setup]]` |

★ ★ **`GetProperties` / `GetProperties2` 的返回数组有 F2 的「seven vs eight / `sameCustomPrp` vs `sameCustomProp`」问题** —— 见 §〇 F2。
★ ★ **`ISheet.IPageSetup` 是唯一一条 `kind: property`**（front-matter 逐字 `kind: property`；签名逐字 `PageSetup IPageSetup {get;}`），Remarks 逐字只有一句：
> `Page setup values are overridden on a sheet by sheet basis.`

★ `SetScale` 的 4 个形参逐条：`Numerator`: First value in the scale ratio (n : n) · `Denominator`: Second value in the scale ratio (n : n) · `ScaleAnnoPosition`: True if the position of the annotations is scaled, false if not · `ScaleAnnoTextHeight`: True if the text height of the annotations is scaled, false if not。
★ `SetScale` 的 Remarks 逐字（含一条**方法对比**）：
> ```
> You can get the two scale values from the sheet by using [[ISheet::GetProperties]] or [[ISheet::IGetProperties]].
> You can also set the two scale values by using [[IDrawingDoc::SetupSheet4]] or [[ISheet::SetProperties]]. However, you cannot specify the scaling of the position or text height of the annotations. Instead, both of these methods automatically scale the position of the annotations but do not scale the text height of the annotations when the drawing is changed.
> ```

★ `SetProperties2` 的 8 个形参：`PaperSz` → `[[swDwgPaperSizes_e]]` · `Templ` → `[[swDwgTemplates_e]]` · `Scale1` / `Scale2` · `FirstAngle`: True if you want first angle projection, false if not · `Width` / `Height`: Custom paper width/height **if PaperSz = swDwgPaperSizes_e.swDwgPaperUserDefined** · `SameCustomPropAsSheetInDocProp`。
★ `SetProperties2` 的 Remarks 是一张 **If…Then… 四行表**，逐字摘两条：
> `Specify a value for Templ that does not match PaperSz` → `The template does not fit the paper size. Templ does not override the PaperSz setting.`
> `Set SameCustomPropAsSheetInDocProp to true` → `The **Tools > Options > Document Properties > Drawing Sheets > Use custom property values from the sheet** check box must be preselected.`

★ `SetSheetFormatName` 的 Remarks 是**两个硬条件**：
> ```
> The name that you specify must:
> - be unique in the FeatureManager design tree.
> - Not contain any of the SOLIDWORKS reserved special characters.
> If either of these conditions is not met, then this method returns false, and the name is not changed. If this sheet does not have a sheet format, this method has no effect.
> ```

★ ★ **[chm-vb6] 复核结果**：`SldWorks~Sheet~GetProperties` / `GetProperties2` / `SetProperties2` / `SetScale` / `SetSheetFormatName` / `IPageSetup` 六页**都存在**，但**六页的 `Availability` 段全部缺失**（正则均返回 `NONE`）⇒ **图纸格式这一族的「哪一版引入」查不到**。

**③ 官方例子调用序与配方实参** —— `SetProperties2` 的 `## Examples` 列 `Set_Drawing_Sheet_Properties_Example_{CSharp,VBNET,VB}`；`SetScale` 的 `## Examples` 列 `Get_Annotations_Arrays_Example_{CSharp,VBNET,VB}`；★ **本轮均未读** ⇒ 逐字调用序**查不到**。

---

## 3.9 公差 / 基准符号 / 表面粗糙度 / 气泡 / 通用表（13 条）

| # | 接口.成员 | 参数 | md 有 Remarks? | ⑤ 废弃链 | 备注（逐字片段） |
|---|---|---|---|---|---|
| 1 | `IDrawingDoc.NewGtol` | **0** | ✗ | 否 | 描述 `Creates a new GTol object and returns the pointer to that object.`；`## Returns` = `Newly created GTol` |
| 2 | `IDrawingDoc.INewGtol` | **0** | ✗ | 否 | 同上（指针变体） |
| 3 | `IGtol.SetFrameValues` | **6** | ✗ | **是** → **`IGtol::SetFrameValues2`**（★ 注意 Obsolete 行**没有** `[[…]]` 方括号，与本仓其他成员写法不同，逐字保留） | 形参：`FrameNumber` / `Tol1` / `Tol2` / `Datum1`（primary datum）/ `Datum2`（secondary）/ `Datum3`（tertiary） |
| 4 | `IGtol.SetDatumIdentifier` | **1** | ✗ | 否 | 描述 `Sets the name of the datum being defined.`；形参 `DatumIdentifier`: Name of datum |
| 5 | `IDrawingDoc.InsertDatumTag` | **0** | ✗ | **是** → **`IModelDoc2::InsertDatumTag2`** | 签名 `void InsertDatumTag()` |
| 6 | `IModelDoc2.InsertDatumTag2` ★现行 | **0** | ✗ | 否 | 描述 `Inserts a datum tag symbol at a selected location.`；`## Returns` = `Newly created [[datum tag]]` |
| 7 | `IDrawingDoc.InsertSurfaceFinishSymbol` | **14** | ✗ | **是** → **`IModelDocExtension::InsertSurfaceFinishSymbol3`** | `## Parameters` **14 行全写 `No description`** |
| 8 | `IModelDocExtension.InsertSurfaceFinishSymbol3` ★现行 | **14** | ✓ | 否 | 见下 |
| 9 | `IDrawingDoc.CreateAutoBalloonOptions` | **0** | ✓ | 否 | 见下 |
| 10 | `IDrawingDoc.AutoBalloon5` ★现行 | **1** | ✓ | 否 | 见下 |
| 11 | `IDrawingDoc.InsertTableAnnotation2` ★现行 | **7** | ✓ | 否 | 见下 |
| 12 | `IModelDocExtension.InsertBomTable4` ★现行 | **9** | ✓ | 否 | 见下 |
| 13 | `IDrawingDoc.InsertDatumTag` / `IDrawingDoc.CreateTableAnnotation` | — | — | — | ★ `CreateTableAnnotation` **名字不存在**，见 §3.0 |

### `InsertSurfaceFinishSymbol3`（表面粗糙度现行版）

描述句逐字：`Creates a surface-finish symbol based on the **last selection**.`
签名返回 `SFSymbol`，14 个形参里 **7 个枚举形参**（旧版的 `## Parameters` 全是 `No description`，现行版补全了）：
`SymType` → `[[swSFSymType_e]]` · `LeaderType` → `[[swLeaderStyle_e]]` · `LaySymbol` → `[[swSFLaySym_e]]` · `ArrowType` → `[[swArrowStyle_e]]`；其余 `LocX`/`LocY`/`LocZ`（`x/y/z location for symbol`）+ `MachAllowance`（`Material removal allowance`）+ `OtherVals`（`Other roughness values`）+ `ProdMethod`（`Production method and treatment`）+ `SampleLen`（`Sampling length`）+ `MaxRoughness`（`Maximum roughness`）+ `MinRoughness`（`Minimum roughness`）+ `RoughnessSpacing`（`Roughness spacing`）。

★ ★ **`## Remarks` 逐字（这是本条唯一的硬条件，且是个坑）**：
> ```
> The SOLIDWORKS Design software uses the location parameters for this method only if the surface finish symbol has a leader leaderType != swNO_LEADER.
> ```
（★ 官方原文 `leader leaderType` 连写两次，**逐字保留**。）

★ [chm-api] `Availability` = `SOLIDWORKS 2005 FCS, Revision Number 13.0`；★ `InsertSurfaceFinishSymbol`（旧版）**无 `Availability` 段**。
★ **四处枚举的具体成员与数值本轮未读** ⇒ **查不到**。

### `CreateAutoBalloonOptions` + `AutoBalloon5`（气泡）★ **四步序，两条 Remarks 逐字互相引用**

`CreateAutoBalloonOptions.md` 的 `## Remarks` 逐字（**四步**）：
> ```
> To automatically create BOM balloons:
> 1. Select one or more views or sheets for which to automatically create BOM balloons.
> 2. Call this method to create an [[IAutoBalloonOptions]] object.
> 3. Set the properties on the IAutoBalloonOptions object.
> 4. Pass the IAutoBalloonOptions object in a call to [[IDrawingDoc::AutoBalloon5]].
> ```

`AutoBalloon5.md` 的 `## Remarks` 逐字（**同样四步，措辞不同**）：
> ```
> This method automatically inserts BOM balloons for bill of materials items in selected drawing views. If a drawing sheet is selected, BOM balloons are automatically inserted for all of the drawing views on that drawing sheet.
>
> To automatically insert BOM balloons:
> 1. Select one or more views or sheets for which to automatically create BOM balloons.
> 2. Call [[IDrawingDoc::CreateAutoBalloonOptions]] to create an [[IAutoBalloonOptions]] object.
> 3. Set the properties on the IAutoBalloonOptions object.
> 4. Call this method using the IAutoBalloonOptions object in the BalloonOptions argument.
> ```

★ ★ **两处签名/类型口径不一致（原文事实）**：
· `CreateAutoBalloonOptions` 的签名返回 **`AutoBalloonOptions`**（具体类），但 `## Returns` 与 Remarks 都写 **`[[IAutoBalloonOptions]]`**（接口）；
· `AutoBalloon5` 的形参类型写 **`AutoBalloonOptions BalloonOptions`**，而 `## Parameters` 的描述写 **`[[IAutoBalloonOptions]]`**。
⇒ [chm-api] 抽验两页 `Availability` 都是 `SOLIDWORKS 2012 FCS, Revision Number 20.0`（一致）。
★ ★ `AutoBalloon5` 的 `## See Also` 逐字把气泡的现行落点指到 **`IModelDocExtension::InsertBOMBalloon2` 与 `IModelDocExtension::InsertStackedBalloon2`** —— `IDrawingDoc` 侧只有 `AutoBalloon{,2,3,4,5}` 这一条链。

### `InsertTableAnnotation2`（通用表）

签名逐字：`TableAnnotation InsertTableAnnotation2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Rows, System.int Columns )` —— ★ **7 个参数**。
`## Remarks` 逐字（**If…Then 两行表**）：
> ```
> **If TableTemplate is...**  **Then..**
> A valid path and filename — AnchorType and Columns are ignored, and the information from the table template is used instead
> Empty — General table is inserted based only on the other input arguments
> ```
`## Returns` = `Pointer to the [[ITableAnnotation]] object`。
★ [md] `## See Also` 逐字：`[[IModelDocExtension::InsertGeneralTableAnnotation Method ()]]` ⇒ **通用表的现行入口在 `IModelDocExtension`**。
★ [chm-api] `Availability` = `SOLIDWORKS 2006 FCS, Revision Number 14.0`；`InsertTableAnnotation`（旧版）→ `InsertTableAnnotation2`，**无 `Availability` 段**。

### `InsertBomTable4`（BOM 表现行版）

签名逐字（★ **9 个参数**）：
```
System.object InsertBomTable4( System.string TemplateName, System.int X, System.int Y, System.int BomType, System.string ConfigurationName, System.bool Hidden, System.int IndentedNumberingType, System.bool DetailedCutList, System.bool DissolvePartLevelRows )
```
`## Parameters` 逐条 + 两个枚举：`BomType` → `[[swBomType_e]]` · `IndentedNumberingType` → `[[swNumberingType_e]]`（**valid only if BomType = swBomType_e.swBomType_Indented**）；`DissolvePartLevelRows` → `**valid only if DetailedCutList is true**`。
★ ★ `## Remarks` 逐字（两个硬条件）：
> ```
> The system does not default to the Default configuration when you specify an empty string for Configuration. You must specify the configuration.
> …
> If the BOM table is a parts-only or indented-style BOM and ConfigurationName is invalid, then the BOM is not created.
> ```
> `BOM table templates are in the <*SOLIDWORKS_*install_dir>\**lang**\<language> folder and have a filename extension of **.sldbomtbt**. The template and table must be of the same type.`

★ [chm-api] `Availability` = **`SOLIDWORKS 2024 FCS, Revision Number 32`**（本域最新的一条）。
★ ★ ★ **BOM 表在 `IDrawingDoc` 上没有创建成员** —— `C:\swapi\types\IDrawingDoc\` 下 `*Bom*` / `*BOM*` = **0 个文件**；
★ BOM 的创建在 **`IModelDocExtension.InsertBomTable{,2,3,4}`**（`InsertBomTable4` 的 `## See Also` 还逐字指向 **`IView::InsertBomTable5 Method ()`**）。

**③ 官方例子调用序** —— 上面 9 条的 `## Examples` 都存在（如 `Get_Annotations_Arrays_Example_VB.md` / `Insert_General_Table_Example_VB.md` / `Add_Autoballoon_to_Face_Example_VB.md` / `Insert_and_Show_BOM_Table_in_Assembly_Example_VB.md`），
★ **本轮均未读** ⇒ 逐字调用序与实参**全部查不到**。

---

## 3.10 工程图域汇总表（★ 只列抄到的事实）

| # | 接口.成员 | 参数 | md 有 Remarks? | 有 Examples? | Obsolete → 后继 | 官方点名 mark? | Availability（[chm-api]） |
|---|---|---|---|---|---|---|---|
| 1 | `IDrawingDoc.CreateDrawViewFromModelView` | 5 | ✗ | ✗ | **是** → `…FromModelView3`（跳过 2） | ✗ | （无该段） |
| 2 | `IDrawingDoc.CreateDrawViewFromModelView2` | 5 | ✗ | ✗ | **是** → `…FromModelView3` | ✗ | （无该段） |
| 3 | `IDrawingDoc.CreateDrawViewFromModelView3` | 5 | ✓ | ✓* | 否 | ✗ | SW2005 SP2 R13.2 |
| 4 | `IDrawingDoc.CreateSectionView` | **0** | ✓ | ✗ | 否 | ✗ | （无该段） |
| 5 | `IDrawingDoc.CreateSectionViewAt` | 5 | ✗ | ✗ | **是** → `…At4` | ✗ | （无该段） |
| 6 | `IDrawingDoc.CreateSectionViewAt2` | 10 | ✗ | ✗ | **是** → `…At4` | ✗ | （无该段） |
| 7 | `IDrawingDoc.CreateSectionViewAt3` | 11 | ✗ | ✗ | **是** → `…At4` | ✗ | （无该段） |
| 8 | `IDrawingDoc.CreateSectionViewAt4` | **6** | ✓ | ✗ | **是** → `…At5` | ✗ | SW2005 FCS R13.0 |
| 9 | `IDrawingDoc.CreateSectionViewAt5` | **7** | ✓ | ✓ | 否 | ✗（只说「选剖切线」） | SW2010 FCS R18.0 |
| 10 | `IDrawingDoc.CreateDetailView` | **0** | ✗ | ✗ | **是** → `…At3` | ✗ | （无该段） |
| 11 | `IDrawingDoc.CreateDetailViewAt` | 3 | ✗ | ✗ | **是** → `…At3` | ✗ | （无该段） |
| 12 | `IDrawingDoc.CreateDetailViewAt2` | 3 | ✗ | ✗ | **是** → `…At3` | ✗ | （无该段） |
| 13 | `IDrawingDoc.CreateDetailViewAt3` | 9 | ✗ | ✗ | **是** → `…At4` | ✗ | SW2001 FCS R9.0 |
| 14 | `IDrawingDoc.CreateDetailViewAt4` | **12** | **✗** | ✓* | 否 | ✗ | SW2017 FCS R25.0 |
| 15 | `IDrawingDoc.CreateAuxiliaryViewAt` | 4 | ✗ | ✗ | **是** → `…At2` | ✗ | （无该段） |
| 16 | `IDrawingDoc.CreateAuxiliaryViewAt2` | **7** | **✗** | ✗ | 否 | ✗ | SW2001 FCS R9.0 |
| 17 | `IDrawingDoc.CreateRelativeView` | 5 | ✓ | ✓ | 否 | **✓ 1 / 2 / 4** | SW2007 FCS R15.0 |
| 18 | `IDrawingDoc.InsertBreakHorizontal` | **0** | ✓ | ✗ | 否 | ✗ | （无该段） |
| 19 | `IDrawingDoc.InsertBreakVertical` | **0** | ✓ | ✗ | 否 | ✗ | （无该段） |
| 20 | `IDrawingDoc.BreakView` | **0** | ✓ | ✓* | 否 | ✗ | （无该段） |
| 21 | `IDrawingDoc.UnBreakView` | **0** | **✗** | ✓* | 否 | ✗ | （无该段） |
| 22 | `IDrawingDoc.CreateLinearDim4` | **9** | ✓ | ✗ | 否 | ✗ | （未抽） |
| 23 | `IDrawingDoc.CreateDiamDim4` | **7** | ✓ | ✓* | 否 | ✗ | （未抽） |
| 24 | `IDrawingDoc.CreateAngDim4` | **9** | ✓ | ✗ | 否 | ✗ | （未抽） |
| 25 | `IDrawingDoc.CreateOrdinateDim4` | **9** | ✓ | ✗ | 否 | ✗ | （未抽） |
| 26 | `IDrawingDoc.NewGtol` / `INewGtol` | **0** | ✗ | ✗ | 否 | ✗ | （无该段） |
| 27 | `IGtol.SetFrameValues` | **6** | ✗ | ✗ | **是** → `IGtol::SetFrameValues2` | ✗ | （无该段） |
| 28 | `IGtol.SetDatumIdentifier` | **1** | ✗ | ✗ | 否 | ✗ | （无该段） |
| 29 | `IDrawingDoc.InsertDatumTag` | **0** | ✗ | ✗ | **是** → `IModelDoc2::InsertDatumTag2` | ✗ | （无该段） |
| 30 | `IModelDoc2.InsertDatumTag2` | **0** | ✗ | ✓* | 否 | ✗ | SW2001Plus FCS R10.0 |
| 31 | `IDrawingDoc.InsertSurfaceFinishSymbol` | **14** | ✗ | ✗ | **是** → `IModelDocExtension::InsertSurfaceFinishSymbol3` | ✗ | （无该段） |
| 32 | `IModelDocExtension.InsertSurfaceFinishSymbol3` | **14** | ✓ | ✓* | 否 | ✗ | SW2005 FCS R13.0 |
| 33 | `IDrawingDoc.CreateAutoBalloonOptions` | **0** | ✓ | ✓* | 否 | ✗ | SW2012 FCS R20.0 |
| 34 | `IDrawingDoc.AutoBalloon5` | **1** | ✓ | ✓* | 否 | ✗ | SW2012 FCS R20.0 |
| 35 | `IDrawingDoc.InsertTableAnnotation2` | **7** | ✓ | ✓* | 否 | ✗ | SW2006 FCS R14.0 |
| 36 | `IModelDocExtension.InsertBomTable4` | **9** | ✓ | ✓* | 否 | ✗ | **SW2024 FCS R32** |
| 37 | `ISheet.GetProperties` | **0** | ✓ | ✓* | **是** → `GetProperties2` | ✗ | 查不到（无 .NET 页） |
| 38 | `ISheet.GetProperties2` | **0** | ✓ | ✓* | 否 | ✗ | 查不到（无 .NET 页） |
| 39 | `ISheet.SetProperties2` | **8** | ✓ | ✓* | 否 | ✗ | 查不到（无 .NET 页） |
| 40 | `ISheet.SetScale` | **4** | ✓ | ✓* | 否 | ✗ | 查不到（无 .NET 页） |
| 41 | `ISheet.SetSheetFormatName` | **1** | ✓ | ✗ | 否 | ✗ | 查不到（无 .NET 页） |
| 42 | `ISheet.IPageSetup`（**属性**） | **0** | ✓ | ✗ | 否 | ✗ | 查不到（无 .NET 页） |

★ **官方点名 mark 的只有 1 条**：`CreateRelativeView`（1 / 2 / 4）。
★ **有 Examples 段但本轮未读（✓*）的有 13 条** ⇒ 逐字调用序**查不到**。

## 3.11 工程图域「查不到」清单（★ 不猜）

1. `CreateDetailViewAt4` / `CreateAuxiliaryViewAt2` / `NewGtol` / `INewGtol` / `UnBreakView` / `InsertDatumTag` / `InsertSurfaceFinishSymbol` 的 `## Remarks` 段 —— 文件里没有（[chm-api] 同样没有）。
2. 局部放大视图（`CreateDetailViewAt4`）与辅助视图（`CreateAuxiliaryViewAt2`）的**调用前置** —— 两套官方源都没有，只能从例子反推（§3.3 / §3.4）。
3. `CreateSectionViewAt{,2,3,4,5}` 的 **mark 数字** —— `At4`/`At5` 的 Remarks 只说「select the section line or lines」，**没给 mark**。
4. `ISheet` 全族的 `Availability` —— 本机 CHM 没有 .NET 页，[chm-vb6] 六页也全无该段。
5. `swSFSymType_e` / `swLeaderStyle_e` / `swSFLaySym_e` / `swArrowStyle_e` / `swBomType_e` / `swNumberingType_e` / `swDwgPaperSizes_e` / `swDwgTemplates_e` 的**成员与数值** —— 本轮未读其 `enums` 页。
6. `CreateLinearDim{,2,3}` / `CreateDiamDim{,2,3}` / `CreateAngDim{,2,3}` / `CreateOrdinateDim{,2,3}` 共 **12 个旧版**的逐位签名与 Remarks —— 只抄了它们的 Obsolete 行。
7. `CreateFlatPatternViewFromModelView{,2,3}` 与 `CreateUnfoldedViewAt{,2,3}`（展开/象限爆炸视图）—— ★ **已定位**（`C:\swapi\types\IDrawingDoc\` 下确实有这 6 个 `.md`，Obsolete 行为「→ 2」「→ 3」），但**本轮未逐条抄录** ⇒ **查不到**。
8. `ISheet.SetProperties`（8 参版）与 `IGetProperties` / `SetSheetFormatName` 之外的图纸格式成员（`GetSize` / `SetSize` / `GetTemplateName` / `ReloadTemplate` / `InsertTitleBlock` / `PageSetup` …）—— 本轮未抄。

---

## 四 · 本轮「对不上」总表（★ 复现用）

| # | 一句话 | 复现依据（文件 + 可搜索片段） |
|---|---|---|
| **F1** | `api-03-weldment.md` 说的 `IFeatureManager~` **289** 是 **VBA 树**的数；.NET 树实测 **285** | `api-pre/api-03-weldment.md` 片段 `计数 = 289` ↔ `sldworksapivb6\SldWorks~FeatureManager~*` = 289 / `sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~*` = 285 |
| **F2** | `ISheet.GetProperties` 自称 **seven** 却列 **8** 个名字，且 `sameCustomPrp` 无定义、拼法与 `GetProperties2` 的 `sameCustomProp` 不同 | `C:\swapi\types\ISheet\GetProperties.md` 片段 `array of seven doubles` ↔ `GetProperties2.md` 片段 `array of eight doubles` |
| **F3** | 官方源有 **5 处死链**（`IICreate*4` / `IDrawngDoc` / `ISkethcManager` / `1stAngleViews2` / `UnInsertBreakVertical`），**CHM 逐字相同** | `C:\swapi\types\IDrawingDoc\{CreateDiamDim4, CreateSectionView, CreateCustomSymbol, CreateBlockDefinition, Create1stAngleViews, InsertBreakHorizontal}.md` |
| **F4** | `InsertSheetMetalLoftedBend2` 用 `swSegmentLength` / `swSegmentAngle` 判条件，**枚举里没有这两个** | `C:\swapi\types\IFeatureManager\InsertSheetMetalLoftedBend2.md` 片段 `swSegmentLength` ↔ `C:\swapi\enums\swLoftedBendFacetOptions_e.md` 成员表（只有 4 个） |
| **F5** | `ISheet`/`IView`/`INote`/`ITableAnnotation`/`IModelView`/`ISectionViewData` 在 CHM .NET 树**各 0 页** | `…\SWhelp\sldworksapi\` 下 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.<接口>~*` 与 `SolidWorks.Interop.sldworks.<接口>~*` 两种通配均 0 |
| **F6** | `InsertSheetMetalCornerTrim` 已被 `api-03-weldment.md` §8.1 抄过，本域再收会重复计数 | `api-pre/api-03-weldment.md` 片段 `钣金折弯角修剪` ↔ `C:\swapi\types\IFeatureManager\InsertSheetMetalCornerTrim.md` |

---

## 五 · 本轮明确没做的事（供下一轮接手）

- ★ **没跑** SolidWorks、**没跑** pytest、**没改**仓内任何既有文件（只新建本文件）。
- ★ `api-pre\INDEX.md` §〇 已经写明「`api-02-sheetmetal.md` 与 `api-05-drawing.md` … **全仓库 0 命中**」——
  ★ **本轮复核该结论成立**：`recon\api-pre\` 下仍只有 `api-01/03/04/06/07/08/09/10` 共 8 份 + `INDEX.md`，**本文件没有创建它们**（任务只授权写本文件一个路径）。
- ★ 同级 `recon\sheetmetal.md` 与 `recon\api-arity-drawing.md` **本轮未打开、未采信**（与 `INDEX.md` 的处置一致）。
- ★ 上面每条「✓*」成员（共 **4 + 13 = 17 条**）的官方例子逐字调用序仍**查不到**，下一轮可直接从 `[ex]` 或 `[chm-api]` 的同名 `.htm` 补。