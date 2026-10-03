# api-03-weldment —— 焊件域 `IFeatureManager` 成员契约抄录

> ★ 本文件只抄**亲手读到**的内容。三条纪律：查不到就说查不到 · 每条给「文件名 + 可搜索原文片段」（不给行号）· 不给建议、不下结论。
>
> **抄录范围**：`C:\swapi\types\IFeatureManager\` 下名称含 Weldment / StructuralMember / EndCap / Gusset / Trim / Extend / WeldBead / FilletBead / WeldSymbol 的成员，共 **32 条**。
>
> **三套离线源（全部本机，未联网）**
>
> | 源 | 本文件简称 | 抄什么 |
> |---|---|---|
> | `C:\swapi\types\IFeatureManager\<成员>.md` | **[md]** | 精确签名（`System.*` 口径）、`## Parameters`、`## Remarks` 逐字 |
> | `C:\swapi\examples\<例子>.md` · `C:\swapi\enums\<枚举>.md` | **[ex]** / **[en]** | 例子调用序 · 枚举成员与数值 |
> | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~<成员>.html` | **[chm-api]** | 签名（VB/C#/C++ 四语）、`Remarks`、`Availability` |
> | `…\SWhelp\sldworksapivb6\SldWorks~FeatureManager~<成员>.html` | **[chm-vb6]** | 签名（VBA 口径） |
> | `…\SWhelp\swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.<枚举>.html` | **[chm-en]** | 枚举成员与数值 |
>
> **★ 关于 CHM 目录结构（事实，不是建议）**
> `SWhelp\` 下有 4 棵子树：`cosworks`(47) / `sldworksapi`(11579) / `sldworksapivb6`(16718) / `swconst`(1353)。
> ★ **[chm-api] 全名含 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~`，只在 `sldworksapi\` 树**（该树顶层文件按 `IFeatureManager~<成员>.html` 计数 = 289）。
> ★ **[chm-vb6] 名叫 `SldWorks~FeatureManager~<成员>.html`，只在 `sldworksapivb6\` 树**，该树按 `IFeatureManager` 过滤 = **0 个文件** —— 用 `*IFeatureManager*` 在 `sldworksapi\` 外搜索会得到「查不到」的假阴性，须按上面的两种命名分别取。

---

## 0. 名字缺席（铁律 5：查不到就说查不到）

| 想找的 | 结果 | 证据 |
|---|---|---|
| `IFeatureManager` 下含 **WeldSymbol** 的成员 | **查不到** | `C:\swapi\types\IFeatureManager\*Symbol*` 返回 0 个文件；`C:\swapi\types\IFeatureManager\` 全量文件名表里无 `Symbol` 子串 |
| `IWeldSymbol` 接口 | **存在，但不是 `IFeatureManager` 成员** | `C:\swapi\types\IWeldSymbol\` 下 46 个文件（`_overview.md` / `GetArcAtIndex.md` / `SetText.md` / `GetFieldWeld.md` …） |
| `swSOLIDWORKSWeldmentEndCondOptions_e`（全大写 SOLIDWORKS） | **查不到该文件**；官方拼法是 `swSolidworksWeldmentEndCondOptions_e` | `C:\swapi\enums\*WeldmentEndCond*` 只命中 `swSolidworksWeldmentEndCondOptions_e.md` 一个 |

> ★ 注：`InsertStructuralWeldment3.md` 的 `## Parameters` 里把枚举名写成 `[[swSOLIDWORKSWeldmentEndCondOptions_e]]`（全大写），而 `InsertStructuralWeldment2.md` 写的是 `[[swSolidworksWeldmentEndCondOptions_e]]`；**本机只存在后者**。以上仅为原文差异记录。

---

# 一、EndCap（3 条）

## 1.1 `IFeatureManager.InsertEndCapFeature`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertEndCapFeature.md` 原文片段 `**Signature**:`：

```
Feature InsertEndCapFeature( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue )
```

★ **6 个参数**。[chm-vb6] `SldWorks~FeatureManager~InsertEndCapFeature.html` 同为 6 参（`ByVal Depth As Double … ByVal ChamferValue As Double`）。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**（文件共 30 行，依次是 front-matter / 标题 / Obsolete 行 / Signature / Parameters / Returns / See Also）。**查不到**。
[chm-api] 同一成员页面**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里无枚举形参。**无**。

**⑤ 废弃链** —— [md] 原文片段（紧跟 `# IFeatureManager.InsertEndCapFeature` 之后的那一行）：

> `Obsolete. Superseded by [[IFeatureManager::InsertEndCapFeature3]].`

[chm-api] 同一句逐字（去标签后）：`Obsolete. Superseded by IFeatureManager::InsertEndCapFeature3 .`
⇒ **后继 = `InsertEndCapFeature3`**（注意不是 2）。[chm-api] 该页**没有 `Availability` 段**（`?`）。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 1.2 `IFeatureManager.InsertEndCapFeature2` ★重点

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertEndCapFeature2.md`：

```
Feature InsertEndCapFeature2( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.object Faces )
```

★ **7 个参数**。

三源互证（[chm-api] 该页 `.NET Syntax` / [chm-vb6] 同名页）：

```vbnet
' [chm-api] .NET Syntax — Visual Basic (Declaration)
 Function InsertEndCapFeature2( _
   ByVal Depth As System.Double, _
   ByVal BIsGivenOffset As System.Boolean, _
   ByVal BIsChamfer As System.Boolean, _
   ByVal OffsetValue As System.Double, _
   ByVal WallThicknessRatio As System.Double, _
   ByVal ChamferValue As System.Double, _
   ByVal Faces As Variant _
) As Feature
```

```vbnet
' [chm-vb6] SldWorks~FeatureManager~InsertEndCapFeature2.html — Visual Basic for Applications (VBA)
 Public Function InsertEndCapFeature2( _
   ByVal Depth As Double, _
   ByVal BIsGivenOffset As Boolean, _
   ByVal BIsChamfer As Boolean, _
   ByVal OffsetValue As Double, _
   ByVal WallThicknessRatio As Double, _
   ByVal ChamferValue As Double, _
   ByVal Faces As Variant _
) As Feature
```

[md] `## Parameters` 逐条：`Depth`: Depth of the end cap · `BIsGivenOffset`: True if end cap is offset, false if not · `BIsChamfer`: True if end cap feature is chamfered, false If not · `OffsetValue`: Value by which to offset the end cap · `WallThicknessRatio`: Wall thickness ratio · `ChamferValue`: Angle of the chamfer · `Faces`: Array of [[Face2]] objects。

**② ## Remarks 逐字** —— [md] 原文片段 `Call [[IFeatureManager::InsertEndCapFeature3]]`：

> ```
> ## Remarks
> Call [[IFeatureManager::InsertEndCapFeature3]] if you want to pre-select the faces to end-cap in the graphics area.
> ```

[chm-api] 同一段逐字（去标签后完全一致）：

> ```
> Remarks
> Call  IFeatureManager::InsertEndCapFeature3  if you want to pre-select the faces to end-cap in the graphics area.
> See Also
> IFeatureManager Interface
> IFeatureManager Members
> IEndCapFeatureData Interface
> Availability
>  SOLIDWORKS 2010 FCS, Revision Number 18.0
> ```

★ 该成员**官方没有写「Before calling…」也没有写 mark**；它把选择责任交给形参 `Faces`（`Array of Face2`）。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Features_Example_VB.md`（[ex] `C:\swapi\examples\Insert_Weldment_Features_Example_VB.md`；[chm-api] 同名 `.htm`，逐行一致）。该例子里的两段原话：

```vbnet
'InsertEndCapFeature
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.6023443450227, 0.6150000000001, -1.013201139555, True, 1, Nothing, 0)
Set face = selMgr.GetSelectedObject6(1, -1)
Set faceECObj1(0) = face
y = faceECObj1
Set endCapFeature = fm.InsertEndCapFeature2(0.005, False, True, 0.003, 0.5, 0.003, y)
```

★ 调用序：**先 `SelectByID2` 选 1 个面（例中 mark 传 `1`）→ `GetSelectedObject6(1, -1)` 取对象 → 装进 1 元素数组 `faceECObj1(0)` → 转 Variant `y` → 传给末位形参 `Faces`**。
★ 实参取值：`Depth=0.005` · `BIsGivenOffset=False` · `BIsChamfer=True` · `OffsetValue=0.003` · `WallThicknessRatio=0.5` · `ChamferValue=0.003`。

**④ 枚举** —— 签名里无枚举形参。**无**。

**⑤ 废弃链** —— **非 Obsolete**。[md] 无 `Obsolete` 字样；[chm-api] 该页无 `Obsolete` 字样（`obsol=no`）。**查不到后继（因为它没被标 Obsolete）**。

**前置一句话**：想在图形区预先选面时官方叫你改用 `InsertEndCapFeature3`，本方法自身靠末位 `Faces`（`Array of Face2`）收面。
**配方一句话**：选面 → `GetSelectedObject6` → 单元素数组 → Variant → 传 `Faces`，实参 `(0.005, False, True, 0.003, 0.5, 0.003, y)`。

---

## 1.3 `IFeatureManager.InsertEndCapFeature3` ★重点 ★本仓在端盖上卡住的那条

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertEndCapFeature3.md`：

```
Feature InsertEndCapFeature3( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.bool BIsCornerTreatment, System.double DepthOffset, System.bool BIsReverse, System.int BIsEndCapInward )
```

★ **10 个参数**。

三源互证：

```vbnet
' [chm-api] .NET Syntax — Visual Basic (Declaration)
 Function InsertEndCapFeature3( _
   ByVal Depth As System.Double, _
   ByVal BIsGivenOffset As System.Boolean, _
   ByVal BIsChamfer As System.Boolean, _
   ByVal OffsetValue As System.Double, _
   ByVal WallThicknessRatio As System.Double, _
   ByVal ChamferValue As System.Double, _
   ByVal BIsCornerTreatment As System.Boolean, _
   ByVal DepthOffset As System.Double, _
   ByVal BIsReverse As System.Boolean, _
   ByVal BIsEndCapInward As System.Integer _
) As Feature
```

```vbnet
' [chm-vb6] SldWorks~FeatureManager~InsertEndCapFeature3.html — VBA
 Public Function InsertEndCapFeature3( _
   ByVal Depth As Double, _
   ByVal BIsGivenOffset As Boolean, _
   ByVal BIsChamfer As Boolean, _
   ByVal OffsetValue As Double, _
   ByVal WallThicknessRatio As Double, _
   ByVal ChamferValue As Double, _
   ByVal BIsCornerTreatment As Boolean, _
   ByVal DepthOffset As Double, _
   ByVal BIsReverse As Boolean, _
   ByVal BIsEndCapInward As Long _
) As Feature
```

★ `BIsEndCapInward`：C# 口径 `System.int`，VB.NET 口径 `System.Integer`，VBA 口径 `Long` —— 三源一致指向 32 位整数。

[md] `## Parameters` 逐条（含全部 **valid only if** 条件，逐字）：

| 形参 | 官方描述（逐字） |
|---|---|
| `Depth` | Thickness of the end cap |
| `BIsGivenOffset` | True to provide an offset value, false to provide a thickness ratio |
| `BIsChamfer` | True if end cap feature is chamfered, false if end cap is filleted |
| `OffsetValue` | Edge offset value; **valid only if BIsGivenOffset is true** |
| `WallThicknessRatio` | Wall thickness ratio; **valid only if BIsGivenOffset is false** |
| `ChamferValue` | Chamfer distance if BIsChamfer is true, fillet radius if BIsChamfer is false |
| `BIsCornerTreatment` | True to chamfer or fillet the end cap corners, false to not; **valid only if BIsGivenOffset is false** |
| `DepthOffset` | Inset distance; **valid only if BIsEndCapInward = 2** |
| `BIsReverse` | True to reverse the offset or thickness ratio, false to not |
| `BIsEndCapInward` | Thickness direction as defined in `[[swEndCapThicknessDirection_e]]` |

**② ## Remarks 逐字** —— [md] 原文片段 `Before calling this method`：

> ```
> ## Remarks
> Before calling this method, select one or more end [[faces]] of a structural member in the graphics area.
>
> Instead of using this method, you can pass the faces in an argument array of [[IFeatureManager::InsertEndCapFeature2]].
> ```

[chm-api] 逐字（去标签后）：

> ```
> Remarks
>  Before calling this method, select one or more end  faces of a structural member in the graphics area.
> Instead of using this method, you can pass the faces in an argument array of  IFeatureManager::InsertEndCapFeature2 .
> See Also
> IFeatureManager Interface
> IFeatureManager Members
> IEndCapFeatureData Interface
> Availability
>  SOLIDWORKS 2015 FCS, Revision Number 23.0
> ```

★ **本方法官方没有点名 mark 值**（原文只说 `select one or more end faces ... in the graphics area`，无 Mark 数字）。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_End_Cap_Example_VB.md`（[ex] `C:\swapi\examples\Insert_Weldment_End_Cap_Example_VB.md`），逐字：

```vbnet
boolstatus = Part.Extension.SelectByID2("End cap1", "BODYFEATURE", 0, 0, 0, False, 0, Nothing, 0)
Part.EditDelete
Part.ViewZoomTo2 0.632542197290199, 0.972121141705638, 3.46184961022406E-02, 1.1852319686392, 0.619681287512073, 3.46184961022431E-02
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.58771345904097, 0.614999999999952, -1.01293869257864, True, 0, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("", "FACE", -1.24763445314215E-02, 0.614999999999839, -1.0014248149476, True, 0, Nothing, 0)
Set myFeature = Part.FeatureManager.InsertEndCapFeature3(0.005, False, False, 0.003, 0.6, 0.003, True, 0.002, False, 2)
Set swEndCap = myFeature.GetDefinition
```

★ 调用序：**先删旧 `End cap1` → 连续 2 次 `SelectByID2` 选面（例中 mark 都传 `0`）→ 直接调 10 参 → `GetDefinition` 读回**。
★ 实参取值：`Depth=0.005` · `BIsGivenOffset=False` · `BIsChamfer=False` · `OffsetValue=0.003` · `WallThicknessRatio=0.6` · `ChamferValue=0.003` · `BIsCornerTreatment=True` · `DepthOffset=0.002` · `BIsReverse=False` · `BIsEndCapInward=2`。
★ 例子同一段还逐字打印了 `swEndCap.IsEndCapInward`，并自带口径注释：
`Debug.Print "    Thickness direction (0=outward, 1=inward, 2=inset) = " & swEndCap.IsEndCapInward`

**④ 枚举** —— 签名里唯一的枚举形参是 `BIsEndCapInward` → `swEndCapThicknessDirection_e`。
[en] `C:\swapi\enums\swEndCapThicknessDirection_e.md` 描述 `End cap thickness directions.`，成员表：

| Member | Value |
| --- | --- |
| `swExtendInward` | 1 |
| `swExtendOutward` | 0 |
| `swSpecifyInset` | 2 |

[chm-en] `…\SWhelp\swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swEndCapThicknessDirection_e.html` 的 `Members` 段逐字相同（`swExtendInward 1` / `swExtendOutward 0` / `swSpecifyInset 2`）⇒ **两源一致**。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：调用前必须在图形区选中一个或多个结构构件的**端面**（官方未给 mark 数字，例子传的是 `0`）。
**配方一句话**：`(0.005, False, False, 0.003, 0.6, 0.003, True, 0.002, False, 2)`，末位 `2` = `swSpecifyInset`，且 `DepthOffset` 只在这个取值下有效。

---

# 二、Gusset（焊件族，3 条）

> ★ 见 §2.0：`InsertSheetMetalGussetFeature{,2,3}` 是**另一族**（钣金），官方描述与接口归属不同，本节不收。

## 2.0 旁证：`InsertSheetMetalGussetFeature{,2,3}` 不属于本节

[md] `C:\swapi\types\IFeatureManager\InsertSheetMetalGussetFeature.md` 第 10 行标题下第一句逐字：
`# IFeatureManager.InsertSheetMetalGussetFeature`，其后为 `Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalGussetFeature3]].`；形参含 `ProfDimType`（`0 = indent` / `1 = profile dimensioning`）、`DDraftAngle`、`GussetType`，[md] `See Also` 段列的是 `[[IBreakCornerFeatureData Interface]]` / `[[ISheetMetalFeatureData Interface]]` 族。
⇒ 仅记录「它叫 `SheetMetal` 且 See Also 指向 Sheet Metal 族」这一原文事实。

## 2.1 `IFeatureManager.InsertGussetFeature`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertGussetFeature.md`：

```
Feature InsertGussetFeature( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim )
```

★ **15 个参数**（比 `InsertGussetFeature2` 少末位 `Faces`，比 `…3` 少 `ProfileD5/D6/ProfileChamferAngle/BUseLenDimForChamfer/BNeedChamferInGusset` 五个）。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**（30→57 行依次是 front-matter / 标题 / Obsolete / Signature / Parameters / Returns / See Also）。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**：`DirType` 与 `LocType` 在 [md] 里是**裸整数**，官方在 `## Parameters` 里直接给字面量表：

> `DirType`: Direction in which to extrude the gusset: `0 = left side` / `1 = center` / `2 = right side`
> `LocType`: Location of the reference plane for the sketch of the gusset: `0 = start point` / `1 = midpoint` / `2 = end point`

★ 注意：这里 `DirType` 的 `0/1/2` 与 `InsertGussetFeature3` 的 `swGussetThicknessType_e`（`0=Inner/1=BothSides/2=Outer`）**不是同一张表**。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertGussetFeature3]].`

[chm-api] 逐字：`Obsolete. Superseded by  IFeatureManager::InsertGussetFeature3 .`；[chm-api] `Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。
⇒ **后继 = `InsertGussetFeature3`**（不是 2）。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 2.2 `IFeatureManager.InsertGussetFeature2` ★重点

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertGussetFeature2.md`：

```
Feature InsertGussetFeature2( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.object Faces )
```

★ **16 个参数**。

三源互证（[chm-api] `.NET Syntax` / [chm-vb6]）：

```vbnet
' [chm-vb6] SldWorks~FeatureManager~InsertGussetFeature2.html — VBA
 Public Function InsertGussetFeature2( _
   ByVal Depth As Double, _
   ByVal DirType As Integer, _
   ByVal LocType As Integer, _
   ByVal BIsProfile As Boolean, _
   ByVal ProfileD1 As Double, _
   ByVal ProfileD2 As Double, _
   ByVal ProfileD3 As Double, _
   ByVal ProfileAngle As Double, _
   ByVal ProfileD4 As Double, _
   ByVal BOffset As Boolean, _
   ByVal DProfileOffset As Double, _
   ByVal CrvIndex As Long, _
   ByVal BReverseDir As Boolean, _
   ByVal BReverseFace As Boolean, _
   ByVal BUseLenDim As Boolean, _
   ByVal Faces As Variant _
) As Feature
```

★ 宽度一致：VBA `Integer` = 16 位 = [md] 的 `System.short`；VBA `Long` = 32 位 = `System.int`。

[md] `## Parameters` 里 `ProfileD1/D2/D3`、`ProfileAngle`、`ProfileD4` 五个都指向同一张图，链接逐字为
`[Direction 1](<../../docs/sldworksapiprogguide/Miscellaneous/FeatureManager__InsertGussetFeature_image.md>)`（`D2/D3/Angle/D4` 同图）。

**② ## Remarks 逐字** —— [md] 原文片段 `Instead of using this method, you can:`：

> ```
> ## Remarks
> Instead of using this method, you can:
>
> 1. Select two faces in the graphics area that are the supporting legs of this gusset.
>
> 2. Call [[IFeatureManager::InsertGussetFeature3]].
> ```

[chm-api] 逐字（去标签后）：

> ```
> Remarks
>  Instead of using this method, you can:
> Select two faces in the graphics area that are the supporting legs of this gusset.
>  Call  IFeatureManager::InsertGussetFeature3 .
> See Also
> IFeatureManager Interface
> IFeatureManager Members
> IGussetFeatureData Interface
> Availability
>  SOLIDWORKS 2010 FCS, Revision Number 18.0
> ```

★ 本方法官方**没有点名 mark 值**；它靠末位 `Faces`（`Array of faces that form the bases of this gusset feature`）。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Features_Example_VB.md`（[ex]；[chm-api] 同名 `.htm` 逐行一致）：

```vbnet
'InsertGussetFeature2
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.02539999999988, 1.94542628561, 0.00429028534694, True, 1, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.07780718114736, 1.9746, -0.001856983219, True, 2, Nothing, 0)
Count = selMgr.GetSelectedObjectCount
If Count = 2 Then
    Set faceGFObj(0) = selMgr.GetSelectedObject6(1, 1)
    Set faceGFObj(1) = selMgr.GetSelectedObject6(1, 2)
    z = faceGFObj
    Part.ClearSelection2 True
    Set myFeature = fm.InsertGussetFeature2(0.005, 0, 0, False, 0.025, 0.025, 0.015, 0.7853981633975, 0.015, True, 0.005, 0, False, False, False, z)
End If
```

★ 调用序：**选 2 个面（例中 mark 分别 `1` 与 `2`）→ `GetSelectedObjectCount` 回读为 2 才继续 → 按 mark 分别取对象 → 装 `faceGFObj(0..1)` → Variant `z` → 传末位 `Faces`；且 `ClearSelection2` 在调用之前**。
★ 实参取值：`Depth=0.005` · `DirType=0` · `LocType=0` · `BIsProfile=False` · `ProfileD1=0.025` · `ProfileD2=0.025` · `ProfileD3=0.015` · `ProfileAngle=0.7853981633975` · `ProfileD4=0.015` · `BOffset=True` · `DProfileOffset=0.005` · `CrvIndex=0` · `BReverseDir=False` · `BReverseFace=False` · `BUseLenDim=False`。

**④ 枚举** —— 签名里**无枚举形参**。`DirType` / `LocType` 的取值表见 §2.1（[md] `## Parameters` 内联字面量 `0/1/2`）。
★ 与 §2.3 的对照：本方法用内联 `0/1/2`，`InsertGussetFeature3` 用 `swGussetThicknessType_e` / `swGussetProfileLocationType_e` —— **两套取值语义不同**，此处仅记录差异，不作判断。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：本方法自带面数组（末位 `Faces`），官方说想「在图形区先选两个支撑腿面」就改走 `InsertGussetFeature3`。
**配方一句话**：选 2 面 → 按 mark 取对象 → 数组转 Variant 传 `Faces`，实参 `(0.005, 0, 0, False, 0.025, 0.025, 0.015, 0.7853981633975, 0.015, True, 0.005, 0, False, False, False, z)`。

---

## 2.3 `IFeatureManager.InsertGussetFeature3` ★重点 ★官方唯一点名 mark 的一条

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertGussetFeature3.md`：

```
Feature InsertGussetFeature3( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.double ProfileD5, System.double ProfileD6, System.double ProfileChamferAngle, System.bool BUseLenDimForChamfer, System.bool BNeedChamferInGusset )
```

★ **20 个参数**。

三源互证：

```vbnet
' [chm-vb6] SldWorks~FeatureManager~InsertGussetFeature3.html — VBA
 Public Function InsertGussetFeature3( _
   ByVal Depth As Double, _
   ByVal DirType As Integer, _
   ByVal LocType As Integer, _
   ByVal BIsProfile As Boolean, _
   ByVal ProfileD1 As Double, _
   ByVal ProfileD2 As Double, _
   ByVal ProfileD3 As Double, _
   ByVal ProfileAngle As Double, _
   ByVal ProfileD4 As Double, _
   ByVal BOffset As Boolean, _
   ByVal DProfileOffset As Double, _
   ByVal CrvIndex As Long, _
   ByVal BReverseDir As Boolean, _
   ByVal BReverseFace As Boolean, _
   ByVal BUseLenDim As Boolean, _
   ByVal ProfileD5 As Double, _
   ByVal ProfileD6 As Double, _
   ByVal ProfileChamferAngle As Double, _
   ByVal BUseLenDimForChamfer As Boolean, _
   ByVal BNeedChamferInGusset As Boolean _
) As Feature
```

[md] `## Parameters` 里 **ProfileD1–D4 / ProfileD5 / ProfileD6 / ProfileChamferAngle 共 7 个都只写 `(see **Remarks**)`**，逐字摘录：

| 形参 | 官方描述（逐字） |
|---|---|
| `Depth` | Thickness of the gusset |
| `DirType` | Thickness direction of the gusset as defined in `[[swGussetThicknessType_e]]` |
| `LocType` | Location of the reference plane for the sketch of the gusset as defined in `[[swGussetProfileLocationType_e]]` |
| `BIsProfile` | True to use a polygon profile, false to use a triangle profile |
| `ProfileD1` | Profile Distance1 (see **Remarks**) |
| `ProfileD2` | Profile Distance2 (see **Remarks**) |
| `ProfileD3` | Profile Distance3 (see **Remarks**) |
| `ProfileAngle` | Profile Angle (see **Remarks**); **valid only if BUseLenDim is false** |
| `ProfileD4` | Profile Distance4 (see **Remarks**); **valid only if BUseLenDim is true** |
| `BOffset` | True to offset the reference plane for the sketch, false to not |
| `DProfileOffset` | Value by which to offset the reference plane for the sketch |
| `CrvIndex` | Index of the edge to use if multiple intersecting edges exist |
| `BReverseDir` | If BOffset set to true, then true to reverse direction, false to not |
| `BReverseFace` | Reverse ProfileD1 and ProfileD2 if triangle profile **- or -** Reverse ProfileD1 and ProfileD2 and reverse ProfileD3 and ProfileD4 if polygon profile |
| `BUseLenDim` | True to use ProfileD4, false to use ProfileAngle |
| `ProfileD5` | Chamfer Distance5 (see **Remarks**); **valid only if BNeedChamferInGusset is true** |
| `ProfileD6` | Chamfer Distance6 (see **Remarks**); **valid only if BNeedChamferInGusset and BUseLenDimForChamber are both true** |
| `ProfileChamferAngle` | Chamfer Angle (see **Remarks**); **valid only if BUseLenDimForChamfer is false and BNeedChamferInGusset is true** |
| `BUseLenDimForChamfer` | True to use ProfileD6, false to use ProfileChamferAngle; **valid only if BNeedChamferInGusset is true** |
| `BNeedChamferInGusset` | True to create a chamfer to allow room for a weld bead under the gusset, false to not |

★ `ProfileD6` 那行官方原文把 `Chamfer` 拼成了 `Chamber`（`BUseLenDimForChamber`），逐字保留。

**② ## Remarks 逐字** —— [md] 原文片段 `you must call`（★★ **本节唯一的 mark 前置**）：

> ```
> ## Remarks
> See the SOLIDWORKS Help for more information about profile and chamfer distances and angles in weldment gussets.
>
> Before calling this method, you must call [[IModelDocExtension::SelectByID2]] to select two faces that are the supporting legs of this gusset with a Mark of 1.
>
> Instead of using this method, you can pass an array of faces to [[IFeatureManager::InsertGussetFeature2]].
> ```

[chm-api] 逐字（去标签后）：

> ```
> Remarks
>  See the SOLIDWORKS Help for more information about profile and chamfer distances and angles in weldment gussets.
> Before calling this method, you must call  IModelDocExtension::SelectByID2 to select two faces that are the supporting legs of this gusset with a Mark of 1.
> Instead of using this method, you can pass an array of faces to  IFeatureManager::InsertGussetFeature2 .
> See Also
> IFeatureManager Interface
> IFeatureManager Members
> IGussetFeatureData Interface
> Availability
>  SOLIDWORKS 2015 FCS, Revision Number 23.0
> ```

**③ 官方例子调用序** —— 例子文件名 `Insert_Gusset_Feature_Example_VB.md`（[ex] `C:\swapi\examples\Insert_Gusset_Feature_Example_VB.md`），逐字：

```vbnet
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.600909534718824, 0.15614125327869, -0.985000000000127, True, 1, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.597259667129663, 1.49999999998727E-02, -0.944257845206607, True, 1, Nothing, 0)
Set myFeature = Part.FeatureManager.InsertGussetFeature3(0.005, swGussetThicknessType_e.swGussetThicknessBothSides, swGussetProfileLocationType_e.swGussetProfileLocationCenter, False, 0.025, 0.025, 0.015, 0.78539816339745, 0.015, False, 0.005, 0, False, False, False, 0.0125, 0.0125, 0.785398163397452, True, False)
```

★ 调用序：**两次 `SelectByID2` 选两个面，两次 mark 都传 `1`（与 Remarks 的 `Mark of 1` 一致）→ 直接调 20 参**；本例子**没有** `ClearSelection2`，**没有**面数组实参。
★ 实参取值：`Depth=0.005` · `DirType=swGussetThicknessBothSides` · `LocType=swGussetProfileLocationCenter` · `BIsProfile=False` · `ProfileD1=0.025` · `ProfileD2=0.025` · `ProfileD3=0.015` · `ProfileAngle=0.78539816339745` · `ProfileD4=0.015` · `BOffset=False` · `DProfileOffset=0.005` · `CrvIndex=0` · `BReverseDir=False` · `BReverseFace=False` · `BUseLenDim=False` · `ProfileD5=0.0125` · `ProfileD6=0.0125` · `ProfileChamferAngle=0.785398163397452` · `BUseLenDimForChamfer=True` · `BNeedChamferInGusset=False`。

**④ 枚举** —— 两个：

`swGussetThicknessType_e` —— [en] `C:\swapi\enums\swGussetThicknessType_e.md` 描述 `Gusset thickness types.`：

| Member | Value |
| --- | --- |
| `swGussetThicknessBothSides` | 1 |
| `swGussetThicknessInner` | 0 |
| `swGussetThicknessOuter` | 2 |

`swGussetProfileLocationType_e` —— [en] `C:\swapi\enums\swGussetProfileLocationType_e.md` 描述 `Gussett profile location types.`（官方拼写 `Gussett`，逐字）：

| Member | Value |
| --- | --- |
| `swGussetProfileLocationCenter` | 1 |
| `swGussetProfileLocationEnd` | 2 |
| `swGussetProfileLocationStart` | 0 |

[chm-en] 两张 CHM 表逐字与上表相同 ⇒ **两源一致**。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：`Before calling this method, you must call IModelDocExtension::SelectByID2 to select two faces that are the supporting legs of this gusset with a **Mark of 1**.`
**配方一句话**：两面同用 mark=1 预选后直接调 20 参，前两位用 `swGussetThicknessType_e.swGussetThicknessBothSides` 与 `swGussetProfileLocationType_e.swGussetProfileLocationCenter`。

---

# 三、StructuralMember（6 条）

## 3.1 `IFeatureManager.InsertStructuralWeldment`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertStructuralWeldment.md`：

```
Feature InsertStructuralWeldment( System.string Path, System.int EndCond, System.double Angle )
```

★ **3 个参数**。[md] `## Parameters` 三行**全部**是 `No description`（`Path`: No description · `EndCond`: No description · `Angle`: No description）；该文件**也没有 `## Returns` 段**。

**② ## Remarks 逐字** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**、也**没有 `Availability` 段**。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— `EndCond` 在签名里是 `System.int`，**该文件的 `## Parameters` 没写它对应哪个枚举**（只写 `No description`）。**查不到**。（同族 `InsertStructuralWeldment2.md` 才点名 `[[swSolidworksWeldmentEndCondOptions_e]]`，见 §3.2。）

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertStructuralWeldment2]].`

[chm-api] 逐字：`Obsolete. Superseded by IFeatureManager::InsertStructuralWeldment2 .`
⇒ **后继 = `InsertStructuralWeldment2`**。[chm-api] 无 `Availability` 段。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 3.2 `IFeatureManager.InsertStructuralWeldment2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertStructuralWeldment2.md`：

```
Feature InsertStructuralWeldment2( System.string Path, System.int EndCond, System.double Angle, System.bool Merge )
```

★ **4 个参数**。[md] `## Parameters` 逐条：`Path`: Path, filename, and name of the type of structural member to insert · `EndCond`: End condition as defined in `[[swSolidworksWeldmentEndCondOptions_e]]` · `Angle`: Angle of rotation of the sketch about the sketch segment · `Merge`: True to merge the bodies of the arc segments to the adjacent bodies, false to not。

**② ## Remarks 逐字** —— [md] **没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] **没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— `EndCond` → `swSolidworksWeldmentEndCondOptions_e`。
[en] `C:\swapi\enums\swSolidworksWeldmentEndCondOptions_e.md` 描述 `Weldment end condition options.`，成员表（[chm-en] 逐字一致）：

| Member | Value |
| --- | --- |
| `swEndConditionButt1` | 2 |
| `swEndConditionButt2` | 3 |
| `swEndConditionMiter` | 1 |
| `swEndConditionNone` | 0 |
| `swEndConditionTrim` | 4 |
| `swEndConditionUseDefault` | 5 |

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertStructuralWeldment3]].`

[chm-api] 逐字：`Obsolete. Superseded by IFeatureManager::InsertStructuralWeldment3 .`；`Availability` = `SOLIDWORKS 2005 FCS, Revision Number 13.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 3.3 `IFeatureManager.InsertStructuralWeldment3`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertStructuralWeldment3.md`：

```
Feature InsertStructuralWeldment3( System.string Path, System.int EndCond, System.double Angle, System.bool Merge, System.object Groups )
```

★ **5 个参数**。形参逐条：`Path`: Path, filename, and name of the type of structural member to insert · `EndCond`: End condition as defined in `[[swSOLIDWORKSWeldmentEndCondOptions_e]]`（★ 原文此处为全大写，见 §0）· `Angle`: Angle of rotation of the sketch about the sketch segment · `Merge`: True to merge the bodies of the arc segments to the adjacent bodies, false to not · `Groups`: Array of `[[IStructuralMemberGroup]]`。

**② ## Remarks 逐字** —— [md] 原文片段 `to populate the *Groups* parameter`：

> ```
> ## Remarks
> Use [[IFeatureManager::CreateStructuralMemberGroup]], [[IStructuralMemberFeatureData::Groups]], or [[IStructuralMemberFeatureData::IGetGroups]] to populate the *Groups* parameter.
> ```

[chm-api] 逐字：`Use IFeatureManager::CreateStructuralMemberGroup , IStructuralMemberFeatureData::Groups , or IStructuralMemberFeatureData::IGetGroups to populate the Groups parameter.`；`Availability` = `SOLIDWORKS 2009 SP5, Revision Number 17.5`。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Features_Example_VB.md`（[ex]；[chm-api] 同名 `.htm` 逐行一致）：

```vbnet
'InsertStructuralWeldment3
Part.ClearSelection2 True
Part.InsertSketch2 True
sketchSegments = Part.SketchManager.CreateCornerRectangle(0, 0, 0, 1#, 2#, 0)
Set group = fm.CreateStructuralMemberGroup
group.Segments = (sketchSegments)
Set GroupArray2(0) = group
vGroups2 = GroupArray2
Part.ViewZoomtofit2
Part.InsertSketch2 True
profilePathName = "C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\weldment profiles\ansi inch\section\5 X 10.SLDLFP"
Set structuralMember = fm.InsertStructuralWeldment3(profilePathName, swSolidworksWeldmentEndCondOptions_e.swEndConditionButt1, 0#, False, (vGroups2))
Part.ClearSelection2 True
```

★ 调用序：**`ClearSelection2` → `InsertSketch2 True` 进草图 → `CreateCornerRectangle` 出线段 → `CreateStructuralMemberGroup` 建组 → `group.Segments = (sketchSegments)` → `InsertSketch2 True` 退草图 → 调 5 参 → `ClearSelection2`**。
★ 实参取值：`Path=profilePathName`（指向 `.SLDLFP` 轮廓）· `EndCond=swSolidworksWeldmentEndCondOptions_e.swEndConditionButt1` · `Angle=0#` · `Merge=False` · `Groups=(vGroups2)`。

**④ 枚举** —— `EndCond` → `swSolidworksWeldmentEndCondOptions_e`（表见 §3.2）。签名里其余形参无枚举。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertStructuralWeldment4]].`

[chm-api] 逐字：`Obsolete. Superseded by IFeatureManager::InsertStructuralWeldment4 .`

**前置一句话**：官方没写图形区预选；它要求先用 `CreateStructuralMemberGroup` / `IStructuralMemberFeatureData::Groups` / `IGetGroups` 把 `Groups` 填出来。
**配方一句话**：草图内 `CreateCornerRectangle` → `CreateStructuralMemberGroup` + `Segments=` → 传 `(profilePathName, swEndConditionButt1, 0#, False, (vGroups2))`。

---

## 3.4 `IFeatureManager.InsertStructuralWeldment4`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertStructuralWeldment4.md`：

```
Feature InsertStructuralWeldment4( System.string Path, System.int ConnectedSegmentsOption, System.bool AllowProtrusion, System.object Groups )
```

★ **4 个参数**。形参逐条：`Path`: Full path name of the type of structural member (**see Remarks**) · `ConnectedSegmentsOption`: Option as defined in `[[swConnectedSegmentsOption_e]]` · `AllowProtrusion`: True to allow protrusion, false to not · `Groups`: Array of `[[IStructuralMemberGroup]]`。

**② ## Remarks 逐字** —— [md] 原文片段 `Populate Path using a weldment profile`：

> ```
> ## Remarks
> Populate Path using a weldment profile (*.**sldlfp**) from *install_dir*\**lang**\*lang*\**weldment profiles**.
>
> Use [[IFeatureManager::CreateStructuralMemberGroup]], [[IStructuralMemberFeatureData::Groups]], or [[IStructuralMemberFeatureData::IGetGroups]] to populate the Groups parameter.
> ```

[chm-api] 逐字：`Populate Path using a weldment profile (*. sldlfp ) from install_dir \ lang \ lang \ weldment profiles .` + 同一句 `Use IFeatureManager::CreateStructuralMemberGroup …`；`Availability` = `SOLIDWORKS 2011 FCS, Revision Number 19.0`。

**③ 官方例子调用序** —— 例子文件名 `Insert_Structural_Weldment_Example_VB.md`（[ex] `C:\swapi\examples\Insert_Structural_Weldment_Example_VB.md`），逐字（第一处；同文件第二处调用逐字相同，只换 `Group2`）：

```vbnet
Set myFeature = Part.FeatureManager.InsertWeldmentFeature()
Dim Group1 As StructuralMemberGroup
Set Group1 = FeatMgr.CreateStructuralMemberGroup
boolstatus = Part.Extension.SelectByID2("Line1@Sketch1", "EXTSKETCHSEGMENT", -0.1495427140733, 0.1133237194389, 0, False, 0, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("Line2@Sketch1", "EXTSKETCHSEGMENT", -0.1872393706766, 0.08238014634844, 0, True, 0, Nothing, 0)
Set segments1(0) = SelMgr.GetSelectedObject6(1, 0)
Set segments1(1) = SelMgr.GetSelectedObject6(2, 0)
vSeg1 = segments1
Group1.Segments = (vSeg1)
Group1.Angle = 0.785714285714286 'radians
Group1.ApplyCornerTreatment = True
Group1.CornerTreatmentType = swEndConditionMiter
Group1.MirrorProfile = True
Group1.MirrorProfileAxis = swMirrorProfileOrAlignmentAxis_Vertical
Group1.GapWithinGroup = 0.0127 'meters
Set GroupArray1(0) = Group1
vGroups1 = GroupArray1
Set myFeature = Part.FeatureManager.InsertStructuralWeldment4("C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\weldment profiles\ansi inch\c channel\3 x 5.sldlfp", 1, False, (vGroups1))
Part.ClearSelection2 True
```

★ 调用序：`InsertWeldmentFeature()` → `CreateStructuralMemberGroup` → 选两条 `EXTSKETCHSEGMENT`（mark 都 `0`）→ `GetSelectedObject6(1,0)/(2,0)` → `Segments=` → 设组属性 → 调 4 参。
★ 实参取值：`Path="…weldment profiles\ansi inch\c channel\3 x 5.sldlfp"` · `ConnectedSegmentsOption=1` · `AllowProtrusion=False` · `Groups=(vGroups1)`。
★ 同一文件还逐字写了读回序：`swWeldFeatData.AccessSelections Part, Nothing` → `GetGroupsCount` / `Groups` / `Group.GetSegmentsCount` → `ReleaseSelectionAccess`。

**④ 枚举** —— `ConnectedSegmentsOption` → `swConnectedSegmentsOption_e`。
[en] `C:\swapi\enums\swConnectedSegmentsOption_e.md` 描述 `Types of structural weldment segment connections.`（[chm-en] 逐字一致）：

| Member | Value |
| --- | --- |
| `swConnectedSegments_CopedCut` | 2 |
| `swConnectedSegments_SimpleCut` | 1 |

★ 组属性里出现的 `swEndConditionMiter`（值 1，见 §3.2 表）与 `swMirrorProfileOrAlignmentAxis_Vertical` 出现在**例子**里而非签名里。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertStructuralWeldment5]].`

[chm-api] 逐字：`Obsolete. Superseded by  IFeatureManager::InsertStructuralWeldment5 .`

**前置一句话**：`Path` 必须是 `install_dir\<lang>\<lang>\weldment profiles` 下的 `.sldlfp` 轮廓；`Groups` 要用 `CreateStructuralMemberGroup` 一类填。
**配方一句话**：`(…\3 x 5.sldlfp, 1, False, (vGroups1))` —— 第二位 `1` = `swConnectedSegments_SimpleCut`。

---

## 3.5 `IFeatureManager.InsertStructuralWeldment5`（本族现行版）

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertStructuralWeldment5.md`：

```
Feature InsertStructuralWeldment5( System.string Path, System.int ConnectedSegmentsOption, System.bool AllowProtrusion, System.object Groups, System.string ConfigurationName )
```

★ **5 个参数**。形参逐条：`Path`: Path and file name of the type of structural member (**see Remarks**) · `ConnectedSegmentsOption`: Option as defined in `[[swConnectedSegmentsOption_e]]` · `AllowProtrusion`: True to allow protrusion, false to not · `Groups`: Array of `[[IStructuralMemberGroup]]` objects · `ConfigurationName`: Name of the configuration in a custom weldment profile **or an empty string** (**see Remarks**)。
[md] `## Returns` = `Structural weldment [[feature]]`。

**② ## Remarks 逐字** —— [md] 原文片段 `Specify Path using either`：

> ```
> ## Remarks
> Specify Path using either:
>
> - SOLIDWORKS-supplied weldment profile (*.**sldlfp**) from *install_dir*\**lang**\*lang*\**weldment profiles* -** or -
>
> - custom weldment profile (*.**sldlfp**); see the SOLIDWORKS Help for details about custom weldment profiles
>
> If using...
> Then specify ConfigurationName as...
>
> SOLIDWORKS-supplied weldment profile
> Empty string
>
> Custom weldment profile
>
> Name of the configuration in the custom weldment profile
>
> Use [[IFeatureManager::CreateStructuralMemberGroup]], [[IStructuralMemberFeatureData::Groups]], or [[IStructuralMemberFeatureData::IGetGroups]] to populate the Groups parameter.
> ```

[chm-api] 逐字：`Specify Path using either:` / `SOLIDWORKS-supplied weldment profile (*. sldlfp ) from install_dir \ lang \ lang \ weldment profiles` / `- or -` / `custom weldment profile (*. sldlfp ); see the SOLIDWORKS Help for details about custom weldment profiles` / `If using... Then specify ConfigurationName as...` / `SOLIDWORKS-supplied weldment profile  Empty string` / `Custom weldment profile  Name of the configuration in the custom weldment profile` / `Use IFeatureManager::CreateStructuralMemberGroup …`。

**③ 官方例子调用序** —— [md] `## Examples` 只列 `Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_*`（C#/VB.NET/VBA）三个；**这三个例子的文件我本轮未读**（`C:\swapi\examples\Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_VB.md` 存在但未打开）⇒ **调用序查不到**。
★ 与 §3.4 例子的差别仅记录事实：本成员**多出第 5 位 `ConfigurationName`**。

**④ 枚举** —— `ConnectedSegmentsOption` → `swConnectedSegmentsOption_e`（表见 §3.4）。`Path` / `ConfigurationName` 是字符串，无枚举。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。
[chm-api] `Availability` = `SOLIDWORKS 2016 FCS, Revision Number 24.0`。

**前置一句话**：官方把 `Path`（出厂 `.sldlfp` vs 自定义 `.sldlfp`）与 `ConfigurationName`（出厂→空串 / 自定义→配置名）配成一对硬约束。
**配方一句话**：查不到（本轮未读其三个 Custom-Profile 例子文件）。

---

## 3.6 `IFeatureManager.CreateStructuralMemberGroup`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\CreateStructuralMemberGroup.md`：

```
StructuralMemberGroup CreateStructuralMemberGroup()
```

★ **0 个参数（无参）**。[md] `## Returns` = `[[Structural-member group]]`（官方原文带连字符，逐字）。

**② ## Remarks 逐字** —— [md] **没有 `## Remarks` 段**（文件共 32 行：front-matter / 标题 / 一句描述 / Signature / Returns / Examples / See Also）。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— 例子文件名 `Insert_Structural_Weldment_Example_VB.md`（[ex]，逐字）：

```vbnet
Dim Group1 As StructuralMemberGroup
Set Group1 = FeatMgr.CreateStructuralMemberGroup
Dim vSeg1 As Variant
Dim segments1(1) As Object
Dim vGroups1 As Variant
Dim GroupArray1(0) As Object
...
Group1.Segments = (vSeg1)
Group1.Angle = 0.785714285714286 'radians
Group1.ApplyCornerTreatment = True
Group1.CornerTreatmentType = swEndConditionMiter
Group1.MirrorProfile = True
Group1.MirrorProfileAxis = swMirrorProfileOrAlignmentAxis_Vertical
Group1.GapWithinGroup = 0.0127 'meters
Set GroupArray1(0) = Group1
vGroups1 = GroupArray1
```

★ 调用序：无参建组 → 设 `Segments` → 设 `Angle`（例子注释 `'radians`）→ 设 `ApplyCornerTreatment` / `CornerTreatmentType` / `MirrorProfile` / `MirrorProfileAxis` / `GapWithinGroup`（例子注释 `'meters`）→ 装 `GroupArray1(0)` → 转 Variant。
★ 同一文件第二处（`Group2`）逐字少了 3 行：`Group2.Segments = (vSeg2)` 后只设 `Group2.AlignAxis = swMirrorProfileOrAlignmentAxis_Vertical`（注意是 **`AlignAxis`**，不是 `MirrorProfileAxis`）。
[md] `## Examples` 另列 `Create_Structural_Member_Group_Example_VB/VBNET/CSharp` 三个例子文件（**本轮未读**）。

**④ 枚举** —— 签名里**无枚举形参**。例子赋值里出现 `swEndConditionMiter`（`swSolidworksWeldmentEndCondOptions_e`，值 1）与 `swMirrorProfileOrAlignmentAxis_Vertical`（**其枚举文件本轮未读** ⇒ 值查不到）。

**⑤ 废弃链** —— **非 Obsolete**。[md] 无 `Obsolete` 字样。[chm-api] `Availability` = `SOLIDWORKS 2009 SP5, Revision 17.5`。

**前置一句话**：查不到（该成员官方页无 Remarks 段，且它无参、不涉及预选）。
**配方一句话**：无参建组 → `Segments=` + 组属性 → 装进一元素数组转 Variant 交给 `InsertStructuralWeldment4/5`。

---

# 四、Trim / Extend —— 焊件修剪（2 条）

## 4.1 `IFeatureManager.InsertWeldmentTrimFeature`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature.md`：

```
Feature InsertWeldmentTrimFeature( System.int EndCond )
```

★ **1 个参数**。形参：`EndCond`: End condition as defined by `[[swSolidworksWeldmentEndCondOptions_e]]`。[md] `## Returns` = `Pointer to the [[IFeature]] object`。

**② ## Remarks 逐字** —— [md] 原文片段 `specify the following marks`（★★ **mark 前置**）：

> ```
> ## Remarks
> Use [[IModelDocExtension::SelectByID2]] and specify the following marks to select the body, or bodies, to trim and the trimming boundaries:
>
> - 1 = Body or bodies to trim
>
> - 2 = Trimming boundaries (body or face)
> ```

[chm-api] 逐字（去标签后完全一致）+ `Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— `EndCond` → `swSolidworksWeldmentEndCondOptions_e`（表见 §3.2）。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：`SelectByID2` 用 **mark 1 = 待剪的体**、**mark 2 = 修剪边界（体或面）**。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 4.2 `IFeatureManager.InsertWeldmentTrimFeature2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`：

```
Feature InsertWeldmentTrimFeature2( System.int EndCond, System.int Options, System.double GapValue, System.object BodiesToTrim, System.object BodiesOrFaces )
```

★ **5 个参数**。形参逐条：`EndCond`: End condition as defined by `[[swSolidworksWeldmentEndCondOptions_e]]` · `Options`: Logical sum of values as defined in `[[swWeldmentTrimExtendOptionType_e]]` (**see Remarks**) · `GapValue`: Length to trim (**see Remarks**) · `BodiesToTrim`: Array of bodies to trim · `BodiesOrFaces`: Array of bodies or faces that define the trimming boundaries。

**② ## Remarks 逐字** —— [md] 原文片段 `specify the following marks`：

> ```
> ## Remarks
> Use [[IModelDocExtension::SelectByID2]] and specify the following marks to select the body, or bodies, to trim and the trimming boundaries:
>
> - 1 = Body or bodies to trim
>
> - 2 = Trimming boundaries (body or face)
>
> If you include swWeldmentTrimExtendOption_WeldGap in the Options parameter, then the GapValue parameter is used. Specify 0 for GapValue to ensure that there is no weld gap.
>
> If you exclude swWeldmentTrimExtendOption_WeldGap from the Options parameter, then the weld gap defaults to the last value specified in the SOLIDWORKS Design user-interface.
> ```

[chm-api] 逐字（去标签后一致）+ `Availability` = `SOLIDWORKS 2010 FCS, Revision Number 18.0`。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Features_Example_VB.md`（[ex]；[chm-api] 同名 `.htm` 逐行一致）：

```vbnet
'InsertWeldmentTrimFeature2
boolstatus = Part.Extension.SelectByID2("Structural Member1[2]", "SOLIDBODY", 0, 0, 0, True, 2, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("Structural Member1[1]", "SOLIDBODY", 0, 0, 0, True, 1, Nothing, 0)
Set selMgr = Part.SelectionManager
Dim Count As Long
Count = selMgr.GetSelectedObjectCount
If Count = 2 Then
    Set obj1(0) = selMgr.GetSelectedObject2(1)
    v1 = obj1
    Set obj2(0) = selMgr.GetSelectedObject2(2)
    v2 = obj2
    Part.ClearSelection2 True
    Options = swWeldmentTrimExtendOption_AllowTrimmedExtensionTrim + swWeldmentTrimExtendOption_AllowTrimmingExtensionTrim + swWeldmentTrimExtendOption_CopedCut + swWeldmentTrimExtendOption_WeldGap
    Set myFeature = fm.InsertWeldmentTrimFeature2(1, Options, 0.01, (v1), (v2))
End If
```

★ 调用序：**先选 mark=2 的边界体、再选 mark=1 的待剪体**（顺序与 Remarks 里 1/2 的列举顺序相反）→ `GetSelectedObjectCount` 回读 = 2 → `GetSelectedObject2(1)` 给 `v1`(BodiesToTrim)、`GetSelectedObject2(2)` 给 `v2`(BodiesOrFaces) → `ClearSelection2` → 调 5 参。
★ 实参取值：`EndCond=1` · `Options=AllowTrimmedExtensionTrim + AllowTrimmingExtensionTrim + CopedCut + WeldGap`（按 §4.3 表 = `1+2+4+8 = 15`，此求和为据表的算术，官方未直接给 15）· `GapValue=0.01` · `BodiesToTrim=(v1)` · `BodiesOrFaces=(v2)`。

**④ 枚举** —— 两个：

`swSolidworksWeldmentEndCondOptions_e`（表见 §3.2）· `swWeldmentTrimExtendOptionType_e` —— [en] `C:\swapi\enums\swWeldmentTrimExtendOptionType_e.md` 描述逐字 `Options for weldment trim extensions. [Bitmask](<../docs/Programming with the SOLIDWORKS API/Bitmasks.md>)`（官方点名它是 **Bitmask**），成员表（[chm-en] 逐字一致）：

| Member | Value |
| --- | --- |
| `swWeldmentTrimExtendOption_AllowTrimmedExtensionTrim` | 1 |
| `swWeldmentTrimExtendOption_AllowTrimmingExtensionTrim` | 2 |
| `swWeldmentTrimExtendOption_CopedCut` | 4 |
| `swWeldmentTrimExtendOption_WeldGap` | 8 |

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。

**前置一句话**：`SelectByID2` 用 **mark 1 = 待剪体**、**mark 2 = 修剪边界**；且 `GapValue` 只在 `Options` 含 `WeldGap` 时才被采用。
**配方一句话**：`(1, AllowTrimmedExtensionTrim+AllowTrimmingExtensionTrim+CopedCut+WeldGap, 0.01, (v1), (v2))`。

---

# 五、Trim / Extend —— 曲面修剪与取消修剪（6 条）

> ★ **归属事实**：这 6 条在官方文档里的 See Also 全部指向 `ISurfaceTrimFeatureData` / `ISurfaceExtendFeatureData`，`PreTrimSurface` / `PostTrimSurface` 的描述写的是 `trimming **surfaces**`，`InsertUntrimSurface2` 的 Remarks 写 `is valid only for **surface parts**`。⇒ 它们**不是焊件域**；此处照抄原文，不作归并。

## 5.1 `IFeatureManager.PreTrimSurface`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\PreTrimSurface.md`：

```
System.bool PreTrimSurface( System.bool BMutualTrimIn, System.bool BSplitSystemIn, System.bool BSplitLinearIn, System.bool BRemovePickedIn )
```

★ **4 个参数**。[md] `## Returns` = `True if successful, false if not`。形参逐条：`BMutualTrimIn`: True to use the selected intersecting surfaces as the trimming surfaces (mutual), false to use the selected surface, plane, or sketch as the trim tool (standard) · `BSplitSystemIn`: True to let the SOLIDWORKS Design application determine which surfaces to trim, false to trim all possible surfaces · `BSplitLinearIn`: False to naturally extend any trims along the intersecting surfaces, true to extend any trims linearly along the intersecting surfaces · `BRemovePickedIn`: True to remove the selected surfaces, false to keep the selected surfaces。

**② ## Remarks 逐字** —— [md] 原文片段 `After calling this method`（★★ 三步调用序）：

> ```
> ## Remarks
> After calling this method:
>
> 1. Select the trimming surfaces or trim tool.
>
> 2. Optionally, call [[IFeatureManager::SolidForTrim]].
>
> 3. Call [[IFeatureManager::PostTrimSurface]].
> ```

[chm-api] 逐字：`After calling this method: Select the trimming surfaces or trim tool. Optionally, call IFeatureManager::SolidForTrim . Call IFeatureManager::PostTrimSurface .`；`Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。

**③ 官方例子调用序** —— [md] `## Examples` 列 `Create_Trimmed_Surface_Feature_Example_{CSharp,VBNET,VB}` 与 `Create_Solid_Body_Surface_Trim_Feature_Example_{CSharp,VBNET,VB}`（**这 6 个文件本轮未读**）⇒ **逐字调用序查不到**。

**④ 枚举** —— 签名里**无枚举形参**，四形参全是 `bool`。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：官方给的是**三步序** —— `PreTrimSurface(...)` → 选面/修剪工具 → （可选）`SolidForTrim` → `PostTrimSurface(...)`。
**配方一句话**：查不到（6 个例子文件本轮未读）。

---

## 5.2 `IFeatureManager.PostTrimSurface`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\PostTrimSurface.md`：

```
Feature PostTrimSurface( System.bool BSewSurfaceIn )
```

★ **1 个参数**。形参：`BSewSurfaceIn`: True to sew the resulting trimmed surfaces, false to not。[md] `## Returns` = `[[Feature]]`。

**② ## Remarks 逐字** —— [md] 原文片段 `Before calling this method`：

> ```
> ## Remarks
> Before calling this method:
>
> 1. Call [[IFeatureManager::PreTrimSurface]].
>
> 2. Select the trimming surfaces or trim tool.
>
> 3. Optionally, call [[IFeatureManager::SolidForTrim]].
> ```

[chm-api] 逐字：`Before calling this method: Call IFeatureManager::PreTrimSurface . Select the trimming surfaces or trim tool. Optionally, call IFeatureManager::SolidForTrim .`；`Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。

**③ 官方例子调用序** —— 同 §5.1 的 6 个文件（**本轮未读**）⇒ **查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：`Before calling this method:` 三步 = `PreTrimSurface` → 选面/修剪工具 → （可选）`SolidForTrim`。
**配方一句话**：查不到（本轮未读其例子文件）。

---

## 5.3 `IFeatureManager.SolidForTrim`（★ 唯一一条 `kind: property`）

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\SolidForTrim.md`：

```
System.bool SolidForTrim {get; set;}
```

★ **0 个参数（属性，非方法）**。[md] front-matter 逐字 `kind: property`；描述句 `Gets or sets whether a [[surface trim feature]] is a solid body or a surface body.`；`## Returns` = `True if a solid body, false if a surface body (see **Remarks**)`。

**② ## Remarks 逐字** —— [md] 原文片段 `only available when creating`（★ **窗口期**）：

> ```
> ## Remarks
> This property is only available when creating a surface trim feature. Call this property:
>
> - after calling [[IFeatureManager::PreTrimSurface]]
>
> - before calling [[IFeatureManager::PostTrimSurface]].
> ```

[chm-api] 逐字：`This property is only available when creating a surface trim feature. Call this property: after calling IFeatureManager::PreTrimSurface before calling IFeatureManager::PostTrimSurface .`；`Availability` = `SOLIDWORKS 2016 FCS, Revision Number 24.0`。

**③ 官方例子调用序** —— [md] `## Examples` 列 `Create_Solid_Body_Surface_Trim_Feature_Example_{CSharp,VBNET,VB}`（**本轮未读**）⇒ **查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：它只能在 `PreTrimSurface` 与 `PostTrimSurface` 之间那个窗口里读写。
**配方一句话**：查不到（本轮未读其例子文件）。

---

## 5.4 `IFeatureManager.GetPreTrimmedBodies`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\GetPreTrimmedBodies.md`：

```
System.object GetPreTrimmedBodies( Body2 TargetSurface )
```

★ **1 个参数**。描述句逐字：`Gets the temporary trimmed bodies using the specified target sheet (surface) body according to the trim tools previously defined by [[IFeatureManager::PreTrimSurface]].`；`## Parameters` = `TargetSurface`: Target sheet [[body]]；`## Returns` = `Array of temporary trimmed bodies`。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。[chm-api] `Availability` = `SOLIDWORKS 2008 FCS, Revision Number 16.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段；只有描述句提到「previously defined by `PreTrimSurface`」）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 5.5 `IFeatureManager.InsertUntrimSurface`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertUntrimSurface.md`：

```
Feature InsertUntrimSurface( System.int FaceUntrimType, System.int EdgeUntrimType, System.double Distance, System.bool BMerge )
```

★ **4 个参数**。形参逐条：`FaceUntrimType`: Untrim face as defined in `[[swFaceUntrimType_e]]` · `EdgeUntrimType`: Untrim edge as defined in `[[swEdgeUntrimType_e]]` · `Distance`: Distance by which to untrim surface · `BMerge`: True to create a surface extension that merges with the original surface, false to create a new, separate surface body。

**② ## Remarks 逐字** —— [md] 原文片段 `You must preselect`：

> ```
> ## Remarks
> You must preselect the face or the edges you want to untrim.
> ```

[chm-api] 逐字：`You must preselect the face or the edges you want to untrim.`；`Availability` = `SOLIDWORKS 2004 SP5, Revision Number 12.5`。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 两个（[chm-en] 与 [en] 逐字一致）：

`swFaceUntrimType_e`（描述 `Untrimmed faces types.`）：`swFaceUntrimTypeAllEdges` = 0 · `swFaceUntrimTypeExternalEdges` = 2 · `swFaceUntrimTypeInternalEdges` = 1
`swEdgeUntrimType_e`（描述 `Untrimmed edge types.`）：`swEdgeUntrimTypeConnectEndPoints` = 1 · `swEdgeUntrimTypeExtendEdges` = 2

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertUntrimSurface2]].`

[chm-api] 逐字：`Obsolete. Superseded by  IFeatureManager::InsertUntrimSurface2 .`

**前置一句话**：`You must preselect the face or the edges you want to untrim.`（官方未给 mark 数字）
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 5.6 `IFeatureManager.InsertUntrimSurface2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertUntrimSurface2.md`：

```
Feature InsertUntrimSurface2( System.int FaceUntrimType, System.int EdgeUntrimType, System.double Distance, System.bool BMerge, System.bool BTrimOppositeSide )
```

★ **5 个参数**。形参逐条（含 valid-only 条件）：`FaceUntrimType`: Untrim face edge type as defined by `[[swFaceUntrimType_e]]`; **valid only if a face is selected** · `EdgeUntrimType`: Connect endpoints or extend edges as defined by `[[swEdgeUntrimType_e]]`; **valid only of one or more edges are selected**（★ 官方原文 `valid only of`，非 `if`，逐字保留）· `Distance`: Distance by which to untrim the surface · `BMerge`: True to create a surface extension that merges with the original surface, false to create a new, separate surface body · `BTrimOppositeSide`: True to remove the surface outside the selected surface edges or interior surface holes, false to not; **valid only if BMerge is false**。

**② ## Remarks 逐字** —— [md] 原文片段 `is valid only for surface parts`：

> ```
> ## Remarks
> This method:
>
> - is valid only for surface parts.
>
> - requires preselection of the face or edges you want to untrim.
>
> For learn more about Untrim Surfaces, see the **SOLIDWORKS Help > Parts and Features > Features > Surfaces > Surface Controls > Untrim Surface** topic.
> ```

[chm-api] 逐字：`This method: is valid only for surface parts. requires preselection of the face or edges you want to untrim.` + 同一句 `For learn more about Untrim Surfaces, see the SOLIDWORKS Help > Parts and Features > Features > Surfaces > Surface Controls > Untrim Surface topic.`；`Availability` = `SOLIDWORKS 2024 FCS, Revision Number 32`。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— `swFaceUntrimType_e` / `swEdgeUntrimType_e`（表见 §5.5，两源一致）。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：官方写死两条 —— `is valid only for surface parts` + `requires preselection of the face or edges you want to untrim`。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

# 六、WeldBead / FilletBead（5 条）

## 6.1 `IFeatureManager.InsertFilletBeadFeature`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertFilletBeadFeature.md`：

```
Feature InsertFilletBeadFeature( System.short Type1, System.double Size1, System.double Length1, System.double Pitch, System.short Type2, System.double Size2, System.double Length2, System.int Flag, System.int EdgeNum1, System.object DeSelEdge1, System.int EdgeNum2, System.object DeSelEdge2 )
```

★ **12 个参数**。[md] `## Parameters` 里 `Type1`/`Type2` 各带内联表 `0 = Full length` / `1 = Intermittent` / `2 = Staggered`；`Flag` 带内联表 `0 = One-sided and no tangent propagation` / `1 = Two-sided` / `2 = Tangent propagation` / `3 = Two-sided and tangent propagation`。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**（`Type1/Type2` 是 `short`，取值表内联在 `## Parameters` 里，见上）。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertFilletBeadFeature2]].`

[chm-api] 逐字：`Obsolete. Superseded by  IFeatureManager::InsertFilletBeadFeature2 .`；`Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 6.2 `IFeatureManager.InsertFilletBeadFeature2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertFilletBeadFeature2.md`：

```
Feature InsertFilletBeadFeature2( System.short Type1, System.double Size1, System.double Length1, System.short PenetrationType1, System.double PenetrationValue1, System.double Pitch, System.short Type2, System.double Size2, System.double Length2, System.short PenetrationType2, System.double PenetrationValue2, System.int Flag, System.int EdgeNum1, System.object DeSelEdge1, System.int EdgeNum2, System.object DeSelEdge2 )
```

★ **16 个参数**。描述句逐字：`Inserts a fillet weld bead feature and also fills the gap between the pre-selected part bodies, if any.`
[md] `## Parameters` 里 `PenetrationType1`/`PenetrationType2` 各带内联表 `0 = Full penetration` / `1 = Partial penetration` / `2 = No penetration`，且 `PenetrationValue1`/`PenetrationValue2` 写的是 `If penetrationType1 is set to 1 (Partial penetration), then set its value`（官方小写拼写，逐字）。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**（85 行里有 16 行是 See Also）。**查不到**。[chm-api] 同名页**也没有 `Remarks` 段**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。
★ 但描述句里有 `pre-selected part bodies` 这一原文措辞（见 §6.5 那个例子给出的 mark 口径）。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**（[md] 与 [chm-api] 均无 `Obsolete` 字样）。**查不到后继**。[chm-api] `Availability` = `SOLIDWORKS 2008 FCS, Revision Number 16.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段）；只有描述句提到 `pre-selected part bodies`。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 6.3 `IFeatureManager.InsertFilletBeadFeature3`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertFilletBeadFeature3.md`：

```
Feature InsertFilletBeadFeature3( System.short Type1, System.double Size1, System.double Length1, System.short PenetrationType1, System.double PenetrationValue1, System.double Pitch, System.short Type2, System.double Size2, System.double Length2, System.short PenetrationType2, System.double PenetrationValue2, System.int Flag, System.int EdgeNum1, System.object DeSelEdge1, System.int EdgeNum2, System.object DeSelEdge2, System.object FaceSet1, System.object FaceSet2 )
```

★ **18 个参数**（= `…2` 的 16 参 + 末两位 `FaceSet1` / `FaceSet2`）。形参逐条（末两位）：`FaceSet1`: Array of side 1 [[faces]] whose intersecting edges get fillet beads · `FaceSet2`: Array of side 2 [[faces]] whose intersecting edges get fillet beads。

**② ## Remarks 逐字** —— [md] 原文片段 `two face arrays`：

> ```
> ## Remarks
> This interface specifies two face arrays, one for each side of a part feature. The fillet bead is applied to the edges where each face intersects for each array specified.
> ```

[chm-api] 逐字（去标签后完全一致）+ `Availability` = `SOLIDWORKS 2010 FCS, Revision Number 18.0`。
★ 官方**没写 mark 数字**；面走 `FaceSet1`/`FaceSet2` 两个数组实参。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Features_Example_VB.md`（[ex]；[chm-api] 同名 `.htm` 逐行一致）：

```vbnet
'InsertFilletBeadFeature3
Dim fbFaceObj1(0) As Object
Dim fbFaceObj2(1) As Object
Part.ClearSelection2 True
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.0412896304482, 0.02548020566445, 0, True, 1, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.09804264728081, 0.01499999999999, 8.069730266129E-04, True, 2, Nothing, 0)
boolstatus = Part.Extension.SelectByID2("", "FACE", 0.01364526875011, 0.08738481720087, 0.01330055827532, True, 4, Nothing, 0)
Count = selMgr.GetSelectedObjectCount
' Face Set 1
Set fbFaceObj1(0) = selMgr.GetSelectedObject6(1, 1)
' Face Set 2
Set fbFaceObj2(0) = selMgr.GetSelectedObject6(1, 2)
Set fbFaceObj2(1) = selMgr.GetSelectedObject6(1, 4)
v1 = fbFaceObj1
v2 = fbFaceObj2
Dim fbEdges() As Long
ReDim fbEdges(0 To 0) As Long
fbEdges(0) = 0
Set myFeature = fm.InsertFilletBeadFeature3(0, 0.003, 0.003, 2, 0.003, 0.006, 0, 0.003, 0.003, 2, 0.003, 0, 1, fbEdges, 0, Nothing, v1, v2)
Part.ClearSelection2 True
```

★ 调用序：`ClearSelection2 True` → **连续 3 次 `SelectByID2` 选 3 个面，mark 依次 `1` / `2` / `4`** → 按 mark 分组取：`GetSelectedObject6(1, 1)` 给 `FaceSet1`；`GetSelectedObject6(1, 2)` 与 `GetSelectedObject6(1, 4)` 给 `FaceSet2` → `fbEdges(0) = 0` 填 `DeSelEdge1` → 调 18 参 → `ClearSelection2 True`。
★ 实参取值：`Type1=0` · `Size1=0.003` · `Length1=0.003` · `PenetrationType1=2` · `PenetrationValue1=0.003` · `Pitch=0.006` · `Type2=0` · `Size2=0.003` · `Length2=0.003` · `PenetrationType2=2` · `PenetrationValue2=0.003` · `Flag=0` · `EdgeNum1=1` · `DeSelEdge1=fbEdges` · `EdgeNum2=0` · `DeSelEdge2=Nothing` · `FaceSet1=v1` · `FaceSet2=v2`。

**④ 枚举** —— 签名里**无枚举形参**（`Type1/Type2/PenetrationType1/2` 的 `0/1/2` 表内联在 `## Parameters`，与 §6.1/§6.2 同表）。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：官方只说「两组面数组、每组面之间的交线加焊道」，**未给 mark 数字**；例子用 mark `1` / `2` / `4` 三面分组。
**配方一句话**：三面按 mark `1`(FaceSet1) 与 `2`+`4`(FaceSet2) 预选后调 18 参，末两位传 `v1` / `v2`。

---

## 6.4 `IFeatureManager.InsertCosmeticWeldBead`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertCosmeticWeldBead.md`：

```
Feature InsertCosmeticWeldBead( System.double WeldSize )
```

★ **1 个参数**。形参：`WeldSize`: Size of the weld bead。

**② ## Remarks 逐字** —— [md] 原文片段 `Before calling this method`：

> ```
> ## Remarks
> Before calling this method, select the contact faces for the weld bead.
> ```

[chm-api] 逐字（去标签后完全一致）；`Availability` = `SOLIDWORKS 2013 FCS, Revision Number 21.0`。

**③ 官方例子调用序** —— [md] `## Examples` 列 `Insert_Cosmetic_Weld_Bead_Example_{VB,VBNET,CSharp}`（**本轮未读这 3 个文件**）⇒ **查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— [md] 原文：

> `Obsolete. Superseded by [[IFeatureManager::InsertCosmeticWeldBead2]].`

[chm-api] 逐字：`Obsolete. Superseded by  IFeatureManager::InsertCosmeticWeldBead2 .`

**前置一句话**：`Before calling this method, select the contact faces for the weld bead.`（官方未给 mark 数字）
**配方一句话**：查不到（本轮未读其 3 个例子文件）。

---

## 6.5 `IFeatureManager.InsertCosmeticWeldBead2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertCosmeticWeldBead2.md`：

```
System.object InsertCosmeticWeldBead2( System.int WeldMode, System.object WeldFromFaceOrEdgeSet, System.object WeldToFaceOrEdgeSet, System.double WeldSize )
```

★ **4 个参数**。★ 返回类型是 **`System.object`**（不是 `Feature`），[md] `## Returns` 写 `Array of weld bead [[features]]`。形参逐条：`WeldMode`: Weld mode as defined in`[[swCosmeticWeldBeadMode_e]]`（★ 官方此处缺一个空格，逐字）· `WeldFromFaceOrEdgeSet`: Array of weld-from entities (**see Remarks**) · `WeldToFaceOrEdgeSet`: Array of weld-to entities or Nothing or null (**see Remarks**) · `WeldSize`: Size of weld bead。

**② ## Remarks 逐字** —— [md] 原文片段 `Selection marks`（★★ **mark 表**）：

> ```
> ## Remarks
> **WeldMode**
> **Selected entities**
> **Selection marks**
>
> swCosmeticWeldBeadMode_e.swCosmeticWeldBeadMode_WeldGeometry
> Either [[faces]] or [[edges]] as weld-from and weld-to entities
>
> **NOTE**: Both weld-to and weld-from entities must all be the same type of entities; e.g., all faces or all edges.
>
> - 4 for each weld-from entity in WeldFromFaceOrEdgeSet
>
> - 8 for each weld-to entity in WeldToFaceOrEdgeSet
>
> swCosmeticWeldBeadMode_e.swCosmeticWeldBeadMode_WeldPath
>
> Edges, [[sketches]], or a combination of edges and sketches are selected as weld-from entities
>
> - 0 for each weld-from entity in WeldFromFaceOrEdgeSet
>
> - Nothing or null for WeldToFaceOrEdgeSet
> ```

[chm-api] 逐字（去标签后一致）+ `Availability` = `SOLIDWORKS 2015 FCS, Revision Number 23.0`。

**③ 官方例子调用序** —— 例子文件名 `Insert_Cosmetic_Weld_Bead_Using_Geometric_Entities_Example_VB.htm`（★ 此例的**完整代码在 `C:\swapi\examples\` 那份 `.md` 本轮未读**，逐字取自 [chm-api] 下的同名 `.htm`），逐字：

```vbnet
'From face
status = swModelDocExt.SelectByID2 ("", "FACE", 0.447611268878973, 0.185506718400291, 6.76112086262037E-03, True, 4, Nothing, 0)
'To face
status = swModelDocExt.SelectByID2 ("", "FACE", 0.567647499089958, 8.88999999998532E-02, 2.08831790428121E-03, True, 8, Nothing, 0)
Set swSelMgr = swModel. SelectionManager
Dim weldFromFace(0) As SldWorks.Face2
Dim weldFromArray As Variant
Set weldFromFace(0) = swSelMgr. GetSelectedObject6 (1, 4)
weldFromArray = weldFromFace
Dim weldToFace(0) As SldWorks.Face2
Dim weldToArray As Variant
Set weldToFace(0) = swSelMgr. GetSelectedObject6 (1, 8)
weldToArray = weldToFace
'Create cosmetic weld bead using the selected faces
Dim weldObjs As Variant
Set swFeatureMgr = swModel. FeatureManager
weldObjs = swFeatureMgr. InsertCosmeticWeldBead2 (0, weldFromArray, weldToArray, 15 / 1000)
```

★ 调用序：**from 面 mark 传 `4`、to 面 mark 传 `8`**（与 Remarks 的 `4 for each weld-from` / `8 for each weld-to` 一致）→ 按 mark 取对象 → 各装一元素数组转 Variant → 调 4 参。
★ 实参取值：`WeldMode=0`（= `swCosmeticWeldBeadMode_WeldGeometry`）· `WeldFromFaceOrEdgeSet=weldFromArray` · `WeldToFaceOrEdgeSet=weldToArray` · `WeldSize=15 / 1000`。
★ 例子后半段逐字读回：`swFeatureMgr` 建好后 `SelectByID2 ("Weld Bead1", "COSMETIC_WELD", 0, 0, 0, False, 0, Nothing, 0)` → `GetDefinition` → `AccessSelections swModel, Nothing` → `GetEntitiesWeldFrom (entityType)` / `GetEntitiesWeldTo (entityType)` → `ReleaseSelectionAccess`。

**④ 枚举** —— `WeldMode` → `swCosmeticWeldBeadMode_e`。
[en] `C:\swapi\enums\swCosmeticWeldBeadMode_e.md` 描述 `Cosmetic weld bead modes`（[chm-en] 逐字一致）：

| Member | Value |
| --- | --- |
| `swCosmeticWeldBeadMode_WeldGeometry` | 0 |
| `swCosmeticWeldBeadMode_WeldPath` | 1 |

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：Remarks 给的是 **WeldGeometry 模式 → from 面 mark=4 / to 面 mark=8；WeldPath 模式 → mark=0 且 `WeldToFaceOrEdgeSet` 传 `Nothing or null`**。
**配方一句话**：`InsertCosmeticWeldBead2(0, weldFromArray, weldToArray, 15/1000)`，from 面用 mark `4`、to 面用 mark `8` 预选。

---

# 七、Weldment 文件夹与切割清单（6 条）

## 7.1 `IFeatureManager.InsertWeldmentFeature`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertWeldmentFeature.md`：

```
Feature InsertWeldmentFeature()
```

★ **0 个参数（无参）**。描述句：`Inserts a weldment feature.`；[md] `## Returns` = `Pointer to the [[IFeature]] object`。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。

**③ 官方例子调用序** —— 例子文件名 `Insert_Structural_Weldment_Example_VB.md`（[ex]），逐字：

```vbnet
Part.ClearSelection2 True
Dim vSkLines As Variant
vSkLines = Part.SketchManager.CreateCornerRectangle(-0.1872393706766, 0.1133237194389, 0, -0.07003610048208, 0.009188409684237, 0)
Part.ClearSelection2 True
vSkLines = Part.SketchManager.CreateCornerRectangle(0.06513561531715, 0.03369083550887, 0, 0.1807053904567, -0.08106219210316, 0)
Part.SketchManager.InsertSketch True
Part.ViewZoomtofit2
Dim myFeature As Object
Set myFeature = Part.FeatureManager.InsertWeldmentFeature()
```

★ 调用序：`ClearSelection2` → 两次 `CreateCornerRectangle` → `InsertSketch True` → `ViewZoomtofit2` → **无参**调 `InsertWeldmentFeature()` → 紧接着 `CreateStructuralMemberGroup`。

**④ 枚举** —— 签名里**无枚举形参**（无参）。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。[chm-api] `Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：无参调用 `Part.FeatureManager.InsertWeldmentFeature()`。

---

## 7.2 `IFeatureManager.InsertWeldmentCutList`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertWeldmentCutList.md`：

```
Feature InsertWeldmentCutList()
```

★ **0 个参数（无参）**。描述句逐字：`Inserts a cut-list-item folder feature containing pre-selected weldment bodies.`

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。[md] 的 `See Also` 段列 `[[IFeatureManager::InsertWeldmentCutList2 Method]]`（= 指向 `2`，但**它本身没标 Obsolete**）。[chm-api] `Availability` = `SOLIDWORKS 2004 SP4, Revision Number 12.4`。

**前置一句话**：查不到（无 Remarks 段）；只有描述句里的 `pre-selected weldment bodies`。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 7.3 `IFeatureManager.InsertWeldmentCutList2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md`：

```
Feature InsertWeldmentCutList2( System.object Bodies )
```

★ **1 个参数**。形参：`Bodies`: Array of [[Body2]] objects。描述句：`Inserts a cut-list-item folder feature containing the specified weldment bodies.`

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Cut_List2_Example_VB.md`。
★ 该 `.md`（[ex] `C:\swapi\examples\Insert_Weldment_Cut_List2_Example_VB.md`）**只有注释头、代码体被截断**（末行是 `Option Explicit`）；逐字调用序取自 [chm-api] 下的同名 `.htm`：

```vbnet
Option Explicit
Dim swApp As SldWorks.SldWorks
Dim Part As ModelDoc2
Dim obj() As Object
Dim v As Variant
Sub main()
Dim PartName As String
Set swApp = Application.SldWorks
Set Part = swApp. ActiveDoc
v = Part. GetBodies2 (0, True)
Dim cutListFeature As Feature
Set cutListFeature = Part. FeatureManager . InsertWeldmentCutList2(v)
End Sub
```

★ 调用序：`GetBodies2 (0, True)` 拿体数组 → 转 Variant → 单参调用 `InsertWeldmentCutList2(v)`。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。[chm-api] `Availability` = `SOLIDWORKS 2010 FCS, Revision Number 18.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段；体数组由形参传入、不靠预选）。
**配方一句话**：`v = Part.GetBodies2(0, True)` → `InsertWeldmentCutList2(v)`。

---

## 7.4 `IFeatureManager.InsertSubWeldFolder`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertSubWeldFolder.md`：

```
Feature InsertSubWeldFolder()
```

★ **0 个参数（无参）**。描述句：`Creates a sub weld folder feature containing solid bodies that are pre-selected in the user interface.`

**② ## Remarks 逐字** —— [md] 原文片段 `must contain a weldment folder`（★ 硬前置）：

> ```
> ## Remarks
> The part must contain a weldment folder (Solid Bodies or Cut List) to create a sub-weldment folder. See [[IFeatureManager::InsertWeldmentFeature]].
> ```

[chm-api] 逐字（去标签后完全一致）；`Availability` = `SOLIDWORKS 2004 FCS, Revision Number 12.0`。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。[md] `See Also` 列 `[[IFeatureManager::InsertSubWeldFolder2 Method]]`。**查不到后继（它没标 Obsolete）**。

**前置一句话**：零件里必须先有焊件文件夹（`Solid Bodies` 或 `Cut List`）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

## 7.5 `IFeatureManager.InsertSubWeldFolder2`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertSubWeldFolder2.md`：

```
Feature InsertSubWeldFolder2( System.object BodyArray )
```

★ **1 个参数**。形参：`BodyArray`: Array of [[Body2]] objects。描述句：`Creates a sub weld folder feature containing the specified weldment bodies.`

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**。**查不到**。

**③ 官方例子调用序** —— 例子文件名 `Insert_Weldment_Features_Example_VB.md`（[ex]；[chm-api] 同名 `.htm` 逐行一致），逐字：

```vbnet
'InsertSubWeldFolder2
boolstatus = Part.Extension.SelectByID2("Gusset1", "SOLIDBODY", 0, 0, 0, False, 0, Nothing, 0)
Set obj(0) = selMgr.GetSelectedObject6(1, -1)
v = obj
Set fm = Part.FeatureManager
Set myFeature = fm.InsertSubWeldFolder2((v))
Part.ClearSelection2 True
```

★ 调用序：`SelectByID2("Gusset1", "SOLIDBODY", …, False, 0, …)`（mark `0`，`Append=False`）→ `GetSelectedObject6(1, -1)` → 装 `obj(0)` → 转 Variant `v` → 单参调用 → `ClearSelection2 True`。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。[chm-api] `Availability` = `SOLIDWORKS 2010 FCS, Revision Number 18.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：选体（mark `0`）→ `GetSelectedObject6(1, -1)` → 一元素数组 → Variant → `InsertSubWeldFolder2((v))`。

---

## 7.6 `IFeatureManager.CutListFolderLocation`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\CutListFolderLocation.md`：

```
System.object CutListFolderLocation( System.object QueryObj )
```

★ **1 个参数**。描述句：`Gets the parent folder of the specified solid body / cut list item / body folder.`；形参：`QueryObj`: Solid Body / cut list item / body folder / sub-weldment folder [[feature]]；[md] `## Returns` = `Parent folder feature of QueryObj; null if QueryObj is not a Solid Body / cut list / body folder / sub-weldment folder`。

**② ## Remarks 逐字** —— [md] 原文片段 `This method only works for`：

> ```
> ## Remarks
> This method only works for:
>
> - Solid Bodies / cut list items
>
> - Feature / body folders
>
> - Sub-weldment folders
>
> Use [[IFeatureManager::FeatureFolderLocation]] to locate other FeatureManager design tree objects.
> ```

[chm-api] 逐字（去标签后一致）；★ `Availability` = `SOLIDWORKS 2025 SP02, Revision Number 33.2`（本组里最新的一条）。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里**无枚举形参**。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。

**前置一句话**：`This method only works for:` 三类对象（Solid Bodies / cut list items · Feature / body folders · Sub-weldment folders）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

# 八、钣金折弯角修剪（1 条 · 官方归属钣金，非焊件）

## 8.1 `IFeatureManager.InsertSheetMetalCornerTrim`

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertSheetMetalCornerTrim.md`：

```
Feature InsertSheetMetalCornerTrim( System.int InternalCornerFlag, System.int BreakType, System.double BreakDist, System.int ReliefType, System.double Param )
```

★ **5 个参数**。描述句逐字：`Inserts a break corner trim in the sheet metal part.`；[md] `See Also` 段列 `[[IBreakCornerFeatureData Interface]]` 与 `[[ISheetMetalFeatureData Interface]]`。
`## Parameters` 里 `ReliefType` 带内联表 `0 = circular` / `1 = square` / `2 = bend-waist`；`Param` 的描述逐字为 `ReliefType dependent:` + `circular, its diameter` / `square, its side length` / `bend-waist, its radius`。

**② ## Remarks 逐字** —— [md] 该文件**没有 `## Remarks` 段**（43 行里 `## Parameters` 与 `## Returns` 之后直接进 `See Also`）。**查不到**。

**③ 官方例子调用序** —— [md] 该文件**没有 `## Examples` 段**。**查不到**。

**④ 枚举** —— 签名里 `BreakType` 是 `System.int`，[md] 描述为 `Type of break as defined in [[swBreakCornerTypes_e]]`。
[en] `C:\swapi\enums\swBreakCornerTypes_e.md` 描述 `Types of break corners.`（[chm-en] 逐字一致）：`swBreakCornerTypeChamfer` = 2 · `swBreakCornerTypeFillet` = 1。

**⑤ 废弃链** —— **非 Obsolete**。**查不到后继**。[chm-api] `Availability` = `SOLIDWORKS 2003 FCS, Revision Number 11.0`。

**前置一句话**：查不到（该成员官方页无 Remarks 段）。
**配方一句话**：查不到（该成员官方页无 Examples 段）。

---

# 九、清单汇总（★ 只列抄到的事实）

| # | 成员 | 形参数 | md 有 Remarks? | 有 Examples? | Obsolete? | 官方点名 mark? | Availability（[chm-api]） |
|---|---|---|---|---|---|---|---|
| 1 | `InsertEndCapFeature` | 6 | ✗ | ✗ | **是** → `…EndCapFeature3` | ✗ | （无该段） |
| 2 | `InsertEndCapFeature2` | **7** | ✓ | ✓ | 否 | ✗ | SW2010 FCS R18.0 |
| 3 | `InsertEndCapFeature3` | **10** | ✓ | ✓ | 否 | ✗（只说"选端面"） | SW2015 FCS R23.0 |
| 4 | `InsertGussetFeature` | 15 | ✗ | ✗ | **是** → `…GussetFeature3` | ✗ | SW2004 FCS R12.0 |
| 5 | `InsertGussetFeature2` | **16** | ✓ | ✓ | 否 | ✗ | SW2010 FCS R18.0 |
| 6 | `InsertGussetFeature3` | **20** | ✓ | ✓ | 否 | **✓ `Mark of 1`** | SW2015 FCS R23.0 |
| 7 | `InsertStructuralWeldment` | 3 | ✗ | ✗ | **是** → `…Weldment2` | ✗ | （无该段） |
| 8 | `InsertStructuralWeldment2` | 4 | ✗ | ✗ | **是** → `…Weldment3` | ✗ | SW2005 FCS R13.0 |
| 9 | `InsertStructuralWeldment3` | 5 | ✓ | ✓ | **是** → `…Weldment4` | ✗ | SW2009 SP5 R17.5 |
| 10 | `InsertStructuralWeldment4` | 4 | ✓ | ✓ | **是** → `…Weldment5` | ✗ | SW2011 FCS R19.0 |
| 11 | `InsertStructuralWeldment5` | 5 | ✓ | ✓ | 否 | ✗ | SW2016 FCS R24.0 |
| 12 | `CreateStructuralMemberGroup` | **0** | ✗ | ✓ | 否 | ✗ | SW2009 SP5 R17.5 |
| 13 | `InsertWeldmentTrimFeature` | 1 | ✓ | ✗ | 否 | **✓ 1 / 2** | SW2004 FCS R12.0 |
| 14 | `InsertWeldmentTrimFeature2` | 5 | ✓ | ✓ | 否 | **✓ 1 / 2** | SW2010 FCS R18.0 |
| 15 | `PreTrimSurface` | 4 | ✓ | ✓* | 否 | ✗ | SW2004 FCS R12.0 |
| 16 | `PostTrimSurface` | 1 | ✓ | ✓* | 否 | ✗ | SW2004 FCS R12.0 |
| 17 | `SolidForTrim`（属性） | **0** | ✓ | ✓* | 否 | ✗ | SW2016 FCS R24.0 |
| 18 | `GetPreTrimmedBodies` | 1 | ✗ | ✗ | 否 | ✗ | SW2008 FCS R16.0 |
| 19 | `InsertUntrimSurface` | 4 | ✓ | ✗ | **是** → `…UntrimSurface2` | ✗ | SW2004 SP5 R12.5 |
| 20 | `InsertUntrimSurface2` | 5 | ✓ | ✗ | 否 | ✗ | SW2024 FCS R32 |
| 21 | `InsertFilletBeadFeature` | 12 | ✗ | ✗ | **是** → `…BeadFeature2` | ✗ | SW2004 FCS R12.0 |
| 22 | `InsertFilletBeadFeature2` | 16 | ✗ | ✗ | 否 | ✗ | SW2008 FCS R16.0 |
| 23 | `InsertFilletBeadFeature3` | **18** | ✓ | ✓ | 否 | ✗ | SW2010 FCS R18.0 |
| 24 | `InsertCosmeticWeldBead` | 1 | ✓ | ✓* | **是** → `…WeldBead2` | ✗ | SW2013 FCS R21.0 |
| 25 | `InsertCosmeticWeldBead2` | 4 | ✓ | ✓ | 否 | **✓ 4/8 · 0** | SW2015 FCS R23.0 |
| 26 | `InsertWeldmentFeature` | **0** | ✗ | ✓ | 否 | ✗ | SW2004 FCS R12.0 |
| 27 | `InsertWeldmentCutList` | **0** | ✗ | ✗ | 否 | ✗ | SW2004 SP4 R12.4 |
| 28 | `InsertWeldmentCutList2` | 1 | ✗ | ✓ | 否 | ✗ | SW2010 FCS R18.0 |
| 29 | `InsertSubWeldFolder` | **0** | ✓ | ✗ | 否 | ✗ | SW2004 FCS R12.0 |
| 30 | `InsertSubWeldFolder2` | 1 | ✗ | ✓ | 否 | ✗ | SW2010 FCS R18.0 |
| 31 | `CutListFolderLocation` | 1 | ✓ | ✗ | 否 | ✗ | SW2025 SP02 R33.2 |
| 32 | `InsertSheetMetalCornerTrim` | 5 | ✗ | ✗ | 否 | ✗ | SW2003 FCS R11.0 |

★ 「✓*」= md 的 `## Examples` 列了例子文件，但**本轮未读其内容**，故逐字调用序仍记为「查不到」。
★ 「有 Examples?」列指 md 的 `## Examples` 段是否存在，与是否读到内容分开记。

**已读出逐字调用序的 9 个成员**：`InsertEndCapFeature2` · `InsertEndCapFeature3` · `InsertGussetFeature2` · `InsertGussetFeature3` · `InsertStructuralWeldment3` · `InsertStructuralWeldment4` · `CreateStructuralMemberGroup` · `InsertWeldmentTrimFeature2` · `InsertFilletBeadFeature3` · `InsertCosmeticWeldBead2` · `InsertWeldmentFeature` · `InsertSubWeldFolder2` · `InsertWeldmentCutList2`

## 9.1 本轮实际读过的例子文件（★ 逐字调用序的来源）

| 例子文件 | 位置 | 读到完整调用序？ |
|---|---|---|
| `Insert_Weldment_Features_Example_VB.md` | `C:\swapi\examples\` | ✓ 全文 300 行（另与 `SWhelp\sldworksapi\Insert_Weldment_Features_Example_VB.htm` 逐行比对，一致） |
| `Insert_Weldment_End_Cap_Example_VB.md` | `C:\swapi\examples\` | ✓ |
| `Insert_Gusset_Feature_Example_VB.md` | `C:\swapi\examples\` | ✓ |
| `Insert_Structural_Weldment_Example_VB.md` | `C:\swapi\examples\` | ✓ |
| `Insert_Weldment_Cut_List2_Example_VB.md` | `C:\swapi\examples\` | ✗ **代码体被截断**（末行仅 `Option Explicit`）；逐字取自同名 `.htm` |
| `Insert_Cosmetic_Weld_Bead_Using_Geometric_Entities_Example_VB` | `SWhelp\sldworksapi\*.htm` | ✓（`C:\swapi\examples\` 下的 `.md` 本轮未读） |

## 9.2 枚举源（★ 两源逐字核对一致，共 9 个）

`swEndCapThicknessDirection_e`(3) · `swGussetThicknessType_e`(3) · `swGussetProfileLocationType_e`(3) · `swCosmeticWeldBeadMode_e`(2) · `swSolidworksWeldmentEndCondOptions_e`(6) · `swConnectedSegmentsOption_e`(2) · `swWeldmentTrimExtendOptionType_e`(4, 官方标 Bitmask) · `swFaceUntrimType_e`(3) · `swEdgeUntrimType_e`(2) · `swBreakCornerTypes_e`(2)
★ 源：`C:\swapi\enums\<名>.md` × `SWhelp\swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.<名>.html` 的 `Members` 段。

## 9.3 本轮明确「查不到」的项（★ 不猜）

1. `IFeatureManager` 下**任何**含 `WeldSymbol` 的成员 —— 名字缺席。
2. `swSOLIDWORKSWeldmentEndCondOptions_e`（全大写写法）—— 本机只有 `swSolidworksWeldmentEndCondOptions_e`。
3. `InsertEndCapFeature` / `InsertStructuralWeldment` / `InsertGussetFeature` / `InsertFilletBeadFeature` / `InsertFilletBeadFeature2` / `CreateStructuralMemberGroup` / `InsertWeldmentCutList` / `InsertWeldmentCutList2` / `InsertWeldmentFeature` / `InsertSubWeldFolder2` / `CutListFolderLocation` / `GetPreTrimmedBodies` / `InsertSheetMetalCornerTrim` 的 `## Remarks` 段 —— 文件里没有。
4. `InsertStructuralWeldment` 的 `EndCond` 对应哪个枚举 —— 该文件 `## Parameters` 三行全写 `No description`。
5. `InsertStructuralWeldment5` / `InsertCosmeticWeldBead` / `PreTrimSurface` / `PostTrimSurface` / `SolidForTrim` 的**逐字调用序** —— 其 `## Examples` 指向的 3～6 个例子文件本轮未读。
6. `InsertEndCapFeature3` 与 `InsertGussetFeature3` 的 **mark 数字** —— 官方 Remarks **都没点**（Gusset3 点了 `Mark of 1`，EndCap3 只说 `select one or more end faces`）。
7. `swMirrorProfileOrAlignmentAxis_Vertical` 的数值 —— 只出现在例子里，其枚举文件本轮未读。