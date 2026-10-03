# api-07-sketch · 草图域契约抄录（ISketchManager + ISketch 全成员）

> **抄录员**：契约抄录员。**只抄，不建议、不下结论。**
> **范围**：`C:\swapi\types\ISketchManager\`（92 个成员）与 `C:\swapi\types\ISketch\`（104 个成员）的**全部成员**。
> **资料来源（★ 全部离线，本轮全部亲手读到）**：
> · 精确签名 + Remarks 逐字摘录 + 废弃链 → `C:\swapi\types\<接口>\<成员>.md`
> · 官方例子调用序 → `C:\swapi\examples\*.md` 与 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\*.htm`（CHM 解包）
> · 枚举成员与数值 → `C:\swapi\enums\*.md`
> · 例子里自带枚举表 → CHM 解包 `.htm` 正文
>
> **纪律三条**（本文件遵守）：① 查不到就写「查不到」，不用相似名字蒙混；② 每条给**文件名 + 可搜索原文片段**，不给行号；③ 不给建议、不下结论。
>
> **★ 单位提醒（抄到的原话，不是推断）**：多个成员的 `## Parameters` 原文写着
> `Radius of the fillet in meters`、`X coordinate of start point in meters`（见 `ISketchManager\CreateFillet.md`、`CreateTangentArc.md`），
> 而官方例子 `Create_On-surface_Spline_Example_VB.md` 里 `points(0) = -3.34270787209949E-02`（米量级）。
> 本文件一律**照抄官方原文**，不替官方换算。

---

## 第 0 部分 · 本域签名里出现的枚举（成员与数值，逐字）

| 枚举 | 文件 | 成员与数值 |
| --- | --- | --- |
| `swSketchChamferType_e` | `C:\swapi\enums\swSketchChamferType_e.md` | `swSketchChamfer_DistanceAngle = 0`；`swSketchChamfer_DistanceDistance = -1`；`swSketchChamfer_DistanceEqual = 2` |
| `swConstrainedCornerAction_e` | `C:\swapi\enums\swConstrainedCornerAction_e.md` | `swConstrainedCornerInteract = 0`（Ask the user whether to delete the geometry or stop processing）；`swConstrainedCornerKeepGeometry = 1`（Keep the constraint or dimension by creating a virtual intersection point before adding the fillet）；`swConstrainedCornerDeleteGeometry = 2`（Delete the constraint or dimension and add the fillet）；`swConstrainedCornerStopProcessing = 3`（Do not delete the constraint or dimension and do not create the fillet） |
| `swSketchSlotCreationType_e` | `C:\swapi\enums\swSketchSlotCreationType_e.md` | `swSketchSlotCreationType_line = 0`（Straight）；`swSketchSlotCreationType_center_line = 1`（Centerpoint straight）；`swSketchSlotCreationType_arc = 2`（Centerpoint arc）；`swSketchSlotCreationType_3pointarc = 3`（3-point arc） |
| `swSketchSlotLengthType_e` | `C:\swapi\enums\swSketchSlotLengthType_e.md` | `swSketchSlotLengthType_CenterCenter = 0`；`swSketchSlotLengthType_FullLength = 1` |
| `swTangentArcTypes_e` | `C:\swapi\enums\swTangentArcTypes_e.md` | `swForward = 1`；`swLeft = 2`；`swBack = 3`；`swRight = 4` |
| `swSkOffsetCapEndType_e` | `C:\swapi\enums\swSkOffsetCapEndType_e.md` | `swSkOffsetNoCaps = 0`；`swSkOffsetArcCaps = 1`；`swSkOffsetLineCaps = 2` |
| `swSkOffsetMakeConstructionType_e` | `C:\swapi\enums\swSkOffsetMakeConstructionType_e.md` | `swSkOffsetDontMakeConstruction = 0`；`swSkOffsetMakeOrigConstruction = 1`；`swSkOffsetMakeOffsConstruction = 2`；`swSkOffsetMakeBothConstruction = 3` |
| `swSketchTrimChoice_e` | `C:\swapi\enums\swSketchTrimChoice_e.md` | `swSketchTrimClosest = 0`；`swSketchTrimCorner = 1`；`swSketchTrimTwoEntities = 2`；`swSketchTrimEntityPoint = 3`；`swSketchTrimEntities = 4`；`swSketchTrimOutside = 5`；`swSketchTrimInside = 6`（各成员**原文明写**"must be selected before calling … using this option"，逐条见下节 `SketchTrim`） |
| `swSketchFullyDefineRelationType_e` | `C:\swapi\enums\swSketchFullyDefineRelationType_e.md` | Bitmask：`Equal=1(0x1)`；`Horizontal=2(0x2)`；`Vertical=4(0x4)`；`Tangent=8(0x8)`；`Perpendicular=16(0x10)`；`Colinear=32(0x20)`；`Concentric=64(0x40)`；`Parallel=128(0x80)`；`Midpoint=256(0x100)`；`Coincident=512(0x200)` |
| `swSketchCheckFeatureProfileUsage_e` | `C:\swapi\enums\swSketchCheckFeatureProfileUsage_e.md` | `UNSET=0`；`BASEEXTRUDE=1`；`BASEEXTRUDETHIN=2`；`BOSSEXTRUDE=3`；`BOSSEXTRUDETHIN=4`；`SURFACEEXTRUDE=5`；`BASEREVOLVE=6`；`BASEREVOLVETHIN=7`；`BOSSREVOLVE=8`；`BOSSREVOLVETHIN=9`；`SURFACEREVOLVE=10`；`CUTEXTRUDE=11`；`CUTEXTRUDETHIN=12`；`CUTREVOLVE=13`；`CUTREVOLVETHIN=14`；`SWEEPSECTION=15`；`SURFACESWEEPSECTION=16`；`SWEEPPATHORGUIDE=17`；`LOFTSECTION=18`；`SURFACELOFTSECTION=19`；`LOFTGUIDE=20`；`RIBSECTION=21`；`SHEETMETAL_BASEFLANGE=22`；`MOLD_PARTINGSURFACES=23` |
| `swSketchCheckFeatureStatus_e` | `C:\swapi\enums\swSketchCheckFeatureStatus_e.md` | ★ **本文件未从 `C:\swapi\enums\` 读到该文件**；数值抄自 CHM 解包 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\Determine_If_Sketch_Suitable_for_Feature_Example_VB.htm` 正文的 `Public Enum swSketchCheckFeatureStatus_e`：`UnknownError=-1`；`OK=0`；`EntXEnt=1`；`EntXSelf=2`；`EntUnspecBad=3`；`ThreeEnts=4`；`EmptySketch=5`；`WrongOpen=6`；`WrongManyContours=7`；`ZeroLengthEnt=8`；`ManyOpen=9`；`NoOpen=10`；`MixedContours=11`；`CturXCtur=12`；`DisjCturs=13`；`OpenWantClosed=14`；`ClosedWantOpen=15`；`DoubleContainment=16`；`MoreThanOneContour=17`；`OneOpenContourExpected=18`；`OneClosedContourExpected=19`；`WantSingleOpenOrMultiClosedDisjoint=20`；`NeedsAxis=21`；`OpenOrUnclear=22`；`ContourIntersectsCenterLine=23` |
| `swAutodimEntities_e` | `C:\swapi\enums\swAutodimEntities_e.md` | `swAutodimEntitiesBasedOnPreselect = 0`；`swAutodimEntitiesAll = 1`；`swAutodimEntitiesSelected = 2` |
| `swAutodimScheme_e` | `C:\swapi\enums\swAutodimScheme_e.md` | `swAutodimSchemeBaseline = 1`；`swAutodimSchemeOrdinate = 2`；`swAutodimSchemeChain = 3`；`swAutodimSchemeCenterline = 4`（原文：`Not supported in sketches or drawings; do not use`） |
| `swAutodimHorizontalPlacement_e` | `C:\swapi\enums\swAutodimHorizontalPlacement_e.md` | `swAutodimHorizontalPlacementBelow = -1`；`swAutodimHorizontalPlacementAbove = 1` |
| `swAutodimVerticalPlacement_e` | `C:\swapi\enums\swAutodimVerticalPlacement_e.md` | `swAutodimVerticalPlacementLeft = -1`；`swAutodimVerticalPlacementRight = 1` |
| `swAutodimMark_e` | `C:\swapi\enums\swAutodimMark_e.md` | Bitmask，`Remarks` 原文：`These values are passed by [[IModelDocExtension::SelectByID2]]`。`swAutodimMarkEntities = 1 (0x1)`；`swAutodimMarkHorizontalDatum = 2 (0x2)`；`swAutodimMarkVerticalDatum = 4 (0x4)`；`swAutodimMarkOriginDatum = 8 (0x8)` |
| `swAutodimStatus_e` | `C:\swapi\enums\swAutodimStatus_e.md` | `Success=0`；`BadOptionValue=1`；`NoActiveDoc=2`；`DocTypeNotSupported=3`；`NoActiveSketch=4`；`3DSketchNotSupported=5`；`SketchIsEmpty=6`；`SketchIsOverDefined=7`；`NoEntities=8`；`EntitiesNotValid=9`；`CenterlineNotAllowed=10`；`DatumNotSupplied=11`；`DatumNotUnique=12`；`DatumNotValidType=13`；`DatumLineNotCenterline=14`；`DatumLineNotVertical=15`；`DatumLineNotHorizontal=16`；`AlgorithmFailed=17`；`SketchNoSolutionFound=18` |
| `swConstrainedStatus_e` | `C:\swapi\enums\swConstrainedStatus_e.md` | `swUnknownConstraint=1`；`swUnderConstrained=2`；`swFullyConstrained=3`；`swOverConstrained=4`；`swNoSolution=5`；`swInvalidSolution=6`；`swAutosolveOff=7` |
| `swLineTypes_e` | `C:\swapi\enums\swLineTypes_e.md` | `swLF_VISIBLE=0`；`swLF_HIDDEN=1`；`swLF_SKETCH=2`；`swLF_DETAIL=3`；`swLF_SECTION=4`；`swLF_DIMENSION=5`；`swLF_CENTER=6`；`swLF_HATCH=7`；`swLF_TANGENT=8` |
| `swLineStyles_e` | `C:\swapi\enums\swLineStyles_e.md` | `swLineCONTINUOUS=0`（Solid）；`swLineHIDDEN=1`（Dashed）；`swLinePHANTOM=2`；`swLineCHAIN=3`；`swLineCENTER=4`；`swLineSTITCH=5`；`swLineCHAINTHICK=6`（Thin/Thick Chain）；`swLineDEFAULT=7` |
| `swLineWeights_e` | `C:\swapi\enums\swLineWeights_e.md` | `swLW_THIN=0`；`swLW_NORMAL=1`；`swLW_THICK=2`；`swLW_THICK2=3`；`swLW_THICK3=4`；`swLW_THICK4=5`；`swLW_THICK5=6`；`swLW_THICK6=7`；`swLW_NUMBER=8`；`swLW_LAYER=9`；`swLW_CUSTOM=10`；`swLW_NONE=-1` |
| `swSketchSegments_e` | `C:\swapi\enums\swSketchSegments_e.md` | `swSketchLINE=0`；`swSketchARC=1`；`swSketchELLIPSE=2`；`swSketchSPLINE=3`；`swSketchTEXT=4`；`swSketchPARABOLA=5` |
| `swConstraintType_e` | `C:\swapi\enums\swConstraintType_e.md` | `CreateSketchPlane` 的 `Relation1/2/3` 原文写「as defined in [[swConstraintType_e]]」，**本轮未逐条抄该枚举全部数值** → 逐条数值：**查不到**。★ 但 CHM 例子 `Create_3D_Sketch_Plane_Example_VB.htm` 里的实参是 `CreateSketchPlane(9, 9, 0)`。 |

### 0.1 用户点名要抄、但**签名里没有**的枚举

| 枚举 | 文件 | 结论 |
| --- | --- | --- |
| `swEndCapThicknessDirection_e` | `C:\swapi\enums\swEndCapThicknessDirection_e.md` | 抄录：Description `End cap thickness directions.`；`swExtendOutward = 0`；`swExtendInward = 1`；`swSpecifyInset = 2`。★ **它在 ISketchManager 与 ISketch 两个接口的任何签名、`## Parameters`、`## Remarks` 里都查不到**（已对两目录全文检索）。 |

### 0.2 `ISplineParamData` 的数组形参形状（样条配套，逐字）

来源：`C:\swapi\types\ISplineParamData\<成员>.md`（`CreateSplineParamData` 的返回类型 `SplineParamData` / `GetSplineParams4` 的返回类型）。

| 成员 | 签名（逐字） | `## Remarks` 逐字摘录 |
| --- | --- | --- |
| `SetControlPoints` | `System.bool SetControlPoints( System.object ControlPoints )` | `Size of ControlPoints array = [[control points count]] * [[dimension]]`；且逐条列 `dimension = 2 then each control point has 2 doubles ( x, y )`、`= 3 then each control point has 3 doubles ( x, y, z )`、`= 4, and the curve is closed or periodic, then each control point has 4 doubles ( x, y, z, w ), where w = weight`、`= 4, and the curve is open or non-periodic, then each control point has 4 doubles ( w*x, w*y, w*z, w ), where w = weight` |
| `GetControlPoints` | `System.bool GetControlPoints( out System.object ControlPoints )` | 同上（原文 `Size of ControlPoints array = [[control points count]] * [[dimension]]`） |
| `SetKnotPoints` | `System.bool SetKnotPoints( System.object KnotPoints )` | `Together with [[control points]] knots determine the shape and smoothness of a spline.`（**该页未写 KnotPoints 数组长度**） |
| `GetKnotPoints` | `System.bool GetKnotPoints( out System.object KnotPoints )` | `Before calling this method, call [[ISplineParamData::KnotPointsCount]] to get the size of the KnotPoints array.` |
| `KnotPointsCount` | `System.int KnotPointsCount {get;}` | `periodic =1 → control points count + 1`；`periodic =0 → control points count + order` |
| `ControlPointsCount` | `System.int ControlPointsCount {get; set;}` | `The number of control points must be greater than or equal to the [[order]] of the spline.` |
| `Order` | `System.int Order {get; set;}` | 表格原文：`2 → linear polynomial → degree 1`；`3 → quadratic polynomial → degree 2`；`4 → cubic polynomial → degree 3` |
| `Periodic` | `System.int Periodic {get; set;}` | 表格原文：`1 → ControlPointsCount + 1`；`0 → ControlPointsCount + Order` |
| `Dimension` | `System.int Dimension {get; set;}` | （`## Remarks` 段为空 —— 官方没写） |

---

## 第 1 部分 · `ISketchManager` 全 92 成员

> 官方自述（`C:\swapi\types\ISketchManager\_overview.md`，逐字）：
> `## Description` → `Provides access to sketch-creation routines.`
> `property_count: 9` · `method_count: 83`

---

### 1.1 `ActiveSketch`（property）

1. **精确签名**（1 个参数？——★ 0 个形参，是 `{get;}` 只读属性）
   `Sketch ActiveSketch {get;}`
2. **Remarks 逐字摘录**：**该成员页 `## Remarks` 段为空 —— 官方没写。**
3. **官方例子调用序**：`Create_3D_Sketch_Plane_Example_VB`（CHM 解包 `.htm`）：
   ```vbnet
   Set swSketchSegment = swSketchManager.CreateCenterLine(-0.082642, 0.005659, 0#, -0.049926, 0.045073, 0#)
   Set swSketch = swSketchManager.ActiveSketch
   status = swSketch.SetWorkingPlaneOrientation(0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0)
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行）。
**前置一句话**：**查不到**（官方未写前置）。
**配方一句话**：取当前活动草图对象，取到后在例子里紧接着用于 `SetWorkingPlaneOrientation`。

---

### 1.2 `AddAlongXDimension`（method）

1. **精确签名**（**3 个形参**）
   `DisplayDimension AddAlongXDimension( System.double X, System.double Y, System.double Z )`
2. **Remarks 逐字摘录**（`Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md` 三个语种版本同文）：
   > `This method works only for 3D sketches in edit mode, and the display dimension is visible only when the sketch is in edit mode.`
3. **官方例子调用序**（`C:\swapi\examples\Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md`，逐字）：
   ```vbnet
   Part.SketchManager.Insert3DSketch True
   vSkLines = Part.SketchManager.CreateCornerRectangle(-0.05171778666374, 0.01933785938058, 0.03, 0.08445537697179, -0.04142795937025, -0.03)
   Set skSegment = Part.SketchManager.CreateSpline2((pointArray), True)
   Part.SketchManager.InsertSketch True
   Set myDisplayDim = Part.SketchManager.AddAlongXDimension(0.05, -0.091, 0.001)
   ```
   ★ **先选什么**：该例子**没有** `SelectByID2`；它靠 `Insert3DSketch` + 几何 + `InsertSketch` 进草图编辑态。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`This method works only for 3D sketches in edit mode` —— 只有 3D 草图、且处于编辑模式才生效。
**配方一句话**：先 `Insert3DSketch True` 建 3D 草图并造几何，再 `InsertSketch True` 收尾，最后给 `(0.05, -0.091, 0.001)` 三个坐标。

---

### 1.3 `AddAlongYDimension`（method）

1. **精确签名**（**3 个形参**）
   `DisplayDimension AddAlongYDimension( System.double X, System.double Y, System.double Z )`
2. **Remarks 逐字摘录**：`This method works only for 3D sketches in edit mode, and the display dimension is visible only when the sketch is in edit mode.`
3. **官方例子调用序**：例子文件 `Add_Along_Y_Dimension_To_3D_Sketch_Example_{VBNET,CSharp}.md` 存在；**本轮未逐行抄其代码 → 调用序查不到**（`Add_Along_X_...` 那份已抄，见 1.2）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：同 X 版 —— `only for 3D sketches in edit mode`。
**配方一句话**：**查不到**（例子未抄）。

---

### 1.4 `AddAlongZDimension`（method）

1. **精确签名**（**3 个形参**）
   `DisplayDimension AddAlongZDimension( System.double X, System.double Y, System.double Z )`
2. **Remarks 逐字摘录**：`This method works only for 3D sketches in edit mode, and the display dimension is visible only when the sketch is in edit mode.`
3. **官方例子调用序**：例子文件 `Add_Along_Z_Dimension_To_3D_Sketch_Example_{VB,VBNET,CSharp}.md` 存在；**本轮未逐行抄其代码 → 查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：同 X 版 —— `only for 3D sketches in edit mode`。
**配方一句话**：**查不到**。

---

### 1.5 `AddToDB`（property）

1. **精确签名**（0 个形参，`{get; set;}`）
   `System.bool AddToDB {get; set;}`
2. **Remarks 逐字摘录**（重点前置，逐字）：
   > `After setting this property to true:`
   > `- It is not possible to undo the creation of some types of sketch entities.`
   > `- You must reset it to false to restore SOLIDWORKS' normal operating mode.`
   > `This property and [[ISketchManager::DisplayWhenAdded]] improve performance during sketch entity creation. ISketchManager::DisplayWhenAdded requires that this property be set to true.`
   > （开头）`One of the benefits of adding sketch entities directly to the database is that you can avoid grid and entity snapping.`
3. **官方例子调用序**（CHM 解包 `Create_Block_Definition_and_Insert_Block_Instance_Example_VB.htm`，逐字）：
   ```vbnet
   swSketchMgr.AddToDB = True
   ... (造 6 条线 + 4 个点 + 4 个圆)
   swSketchMgr.AddToDB = False
   swModel.GraphicsRedraw2
   ```
   ★ **先选什么**：该例子末尾才 `MultiSelect2(vSkSeg/vSkPt/vSkNote, True, Nothing)` → `MakeSketchBlockFromSelected(Nothing)`。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`DisplayWhenAdded` 要生效**必须**先把 `AddToDB` 置 `true`；置 `true` 后有些实体**不可撤销**。
**配方一句话**：`AddToDB = True` → 造几何 → `AddToDB = False` → `GraphicsRedraw2`。

---

### 1.6 `AutoInference`（property，★ Obsolete）

1. **精确签名**（0 个形参）
   `System.bool AutoInference {get; set;}`
2. **Remarks 逐字摘录**：
   > `Inferencing mode can be seen when creating a sketch segment and your cursor moves past another sketch enitity. If inferencing is turned on, you see a dashed line from your current cursor position to the inferenced position on the existing sketch entity.`
   （原文 `enitity` 拼写如此，逐字照抄。）
3. **官方例子调用序**：**查不到**（该成员页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISldWorks::GetUserPreferenceToggle]] or [[ISldWorks::SetUserPreferenceToggle]] and swUserPreferenceToggle_e.swSketchInference.`
**前置一句话**：**查不到**（页内未写前置）。
**配方一句话**：改用 `ISldWorks::SetUserPreferenceToggle(swUserPreferenceToggle_e.swSketchInference, …)`。

---

### 1.7 `AutoSolve`（property）

1. **精确签名**（0 个形参）
   `System.bool AutoSolve {get; set;}`
2. **Remarks 逐字摘录**：**该成员页 `## Remarks` 段为空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.8 `ConvertEntities`（method）

1. **精确签名**（**0 个形参**）
   `void ConvertEntities()`
2. **Remarks 逐字摘录**：**该成员页 `## Remarks` 段为空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.9 `Create3PointArc`（method）

1. **精确签名**（**9 个形参**）
   `SketchSegment Create3PointArc( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.double X3, System.double Y3, System.double Z3 )`
   参数释义（逐字）：`- **X1**: X coordinate of point 1` …… `- **Z3**: Z coordinate of point 3`
2. **Remarks 逐字摘录**：**该成员页 `## Remarks` 段为空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.10 `Create3PointCenterRectangle`（method）

1. **精确签名**（**9 个形参**）
   `System.object Create3PointCenterRectangle( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.double X3, System.double Y3, System.double Z3 )`
   参数释义（逐字）：`X1/Y1/Z1 = X/Y/Z coordinate of point 1`；`X2/Y2/Z2 = point 2`；`X3/Y3/Z3 = point 3`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.11 `Create3PointCornerRectangle`（method）

1. **精确签名**（**9 个形参**）
   `System.object Create3PointCornerRectangle( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.double X3, System.double Y3, System.double Z3 )`
   参数释义（逐字）：`point 1 / point 2 / point 3`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.12 `CreateArc`（method）

1. **精确签名**（**10 个形参**）
   `SketchSegment CreateArc( System.double XC, System.double YC, System.double Zc, System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.short Direction )`
2. **Remarks 逐字摘录**（逐字，重点前置）：
   > `This method creates a partial arc in the active 2D sketch. If a sketch is not active, then a new sketch is  created. You can check for an active sketch using I[[SketchManager::ActiveSketch]].`
   > `[[ISketchManager::AddToDB]] and [[ISketchManager::DisplayWhenAdded]] increase performance during entity creation by adding entities directly to the SOLIDWORKS database.`
   > `... When you are done creating entities, it is important to call ISketchManager::AddToDB(False), to restore SOLIDWORKS to its normal operating mode.`
3. **官方例子调用序**：例子 `Get_Sketch_Arc_Data_Example_{VB,VBNET,CSharp}.md` 在 `## Examples` 段被列出；**本轮未逐行抄其代码 → 查不到**。
   ★ 可抄的相邻证据（`Create_and_Edit_Circular_Sketch_Pattern_Example_VB.htm`）：
   ```vbnet
   Set swSketchSegment = swSketchMgr.CreateCircle(0#, 0#, 0#, 0.045549, 0.013926, 0#)
   vSkLines = swSketchMgr.CreateCornerRectangle(-0.005867589431389, 0.03694408160504, 0, 0.004563680668858, 0.02673012963188, 0)
   boolstatus = swSketchMgr.CreateCircularSketchStepAndRepeat(0.03184378021964, 4.732863934409, 4, 1.570796326795, True, "", True, True, True)
   ```
4. **枚举**：签名里 `System.short Direction` —— **`C:\swapi\enums\` 里本成员页没有点名任何枚举 → 查不到**。
5. **废弃链**：**查不到**。
**前置一句话**：`If a sketch is not active, then a new sketch is created` —— 无活动草图会自动新建一个。
**配方一句话**：给出圆心 `(XC,YC,Zc)` + 起止两点 + `Direction`；画完记得 `AddToDB(False)`。

---

### 1.13 `CreateBoundaryHatch`（method）

1. **精确签名**（**5 个形参**）
   `System.object CreateBoundaryHatch( System.double Angle, System.double Scale, System.int Color, System.string Hatchname, System.string Layername )`
   参数释义（逐字）：`Angle: Angle of the hatch if hatch is not solid`；`Scale: Scale factor for the hatch if the hatch is not solid`；`Color: COLORREF value describing the color used for this hatch`；`Hatchname: Type or name of the hatch from the **Sldwks.ptn** file`；`Layername: Layer name for the hatch if a drawing document`
2. **Remarks 逐字摘录**（★ **这就是前置原话**）：
   > `Before calling this method, select the closed sketch profile for the area hatch/fill boundary hatch.`
3. **官方例子调用序**：**查不到**（该成员页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`Before calling this method, select the closed sketch profile` —— 先选中闭合草图轮廓。
**配方一句话**：选闭合轮廓后传 `(Angle, Scale, Color, Hatchname, Layername)`。

---

### 1.14 `CreateCenterLine`（method）

1. **精确签名**（**6 个形参**）
   `SketchSegment CreateCenterLine( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2 )`
2. **Remarks 逐字摘录**：
   > `You can also create centerline construction geometry using [[ISketchManager::CreateLine]] and [[ISketchSegment::ConstructionGeometry]].`
3. **官方例子调用序**（CHM 解包 `Create_3D_Sketch_Plane_Example_VB.htm`，逐字）：
   ```vbnet
   swSketchManager.Insert3DSketch True
   Set swSketchSegment = swSketchManager.CreateCenterLine(-0.082642, 0.005659, 0#, -0.049926, 0.045073, 0#)
   ...
   Set swSketchSegment = swSketchManager.CreateCenterLine(-0.049926, 0.045073, 0#, -0.049926, -0.022634, -0.065874)
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（该页未写前置）。
**配方一句话**：先 `Insert3DSketch True` 进 3D 草图，再给两点坐标建中心线。

---

### 1.15 `CreateCenterRectangle`（method）

1. **精确签名**（**6 个形参**）
   `System.object CreateCenterRectangle( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2 )`
   参数释义（逐字）：`X1: X coordinate for point 1` … `Z2: Z coordinate for point 2`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.16 `CreateChamfer`（method）

1. **精确签名**（**3 个形参**）
   `SketchSegment CreateChamfer( System.int Type, System.double Distance, System.double AngleORdist )`
   参数释义（逐字）：`- **Type**: Type of chamfer as defined in [[swSketchChamferType_e]]`；`- **AngleORdist**:` `If Type = swSketchChamfer_DistanceDistance, then the second chamfer distance` / `If Type = swSketchChamfer_DistanceAngle, then the second chamfer angle` / `If Type = swSketchChamfer_DistanceEqual, then this argument is ignored because Distance is used for both edges`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swSketchChamferType_e` → `swSketchChamfer_DistanceAngle = 0`、`swSketchChamfer_DistanceDistance = -1`、`swSketchChamfer_DistanceEqual = 2`（`C:\swapi\enums\swSketchChamferType_e.md`）。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内未写；`AngleORdist` 的取舍规则只在 `## Parameters` 里，见上）。
**配方一句话**：`Type` 决定第三个形参是"第二距离"还是"第二角度"还是"忽略"。

---

### 1.17 `CreateCircle`（method）

1. **精确签名**（**6 个形参**）
   `SketchSegment CreateCircle( System.double XC, System.double YC, System.double Zc, System.double Xp, System.double Yp, System.double Zp )`
2. **Remarks 逐字摘录**（逐字）：
   > `This method creates a full circle in the active 2D sketch. If a sketch is not active, then a new sketch is created. You can check for an active sketch using [[ISketchManager::ActiveSketch]].`
   > `... When you are done creating entities, it is important to ISketchManager::AddToDB(False), to restore SOLIDWORKS to its normal operating mode.`
   > `To create a circle using a center point and radius, see [[ISketchManager::CreateCircleByRadius]]. To create a partial arc, see [[ISketchManager::CreateArc]].`
3. **官方例子调用序**（CHM 解包，逐字）：
   · `Create_and_Edit_Circular_Sketch_Pattern_Example_VB.htm`：
     ```vbnet
     Set swSketchSegment = swSketchMgr.CreateCircle(0#, 0#, 0#, 0.045549, 0.013926, 0#)
     ```
   · `Create_3D_Sketch_Plane_Example_VB.htm`：
     ```vbnet
     status = swModelDocExt.SelectByID2("Front Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
     swModel.ClearSelection2 True
     Set swSketchSegment = swSketchManager.CreateCircle(-0.056401, 0.005985, 0#, -0.054697, -0.005141, 0#)
     ```
   · `Create_Block_Definition_and_Insert_Block_Instance_Example_VB.htm`：
     ```vbnet
     Set swSkSeg(6) = swSketchMgr.CreateCircle(swSkPt(0).X, swSkPt(0).Y, swSkPt(0).Z, 0.03050393605009, 0.169349494074, 0#)
     ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：无活动草图会自动新建；`Create_3D_Sketch_Plane` 例子显式先 `SelectByID2("Front Plane","PLANE",…, 0, …, 0, Nothing, 0)` 再 `ClearSelection2 True`。
**配方一句话**：给圆心 + 圆上一点两坐标（6 个 double）。

---

### 1.18 `CreateCircleByRadius`（method）

1. **精确签名**（**4 个形参**）
   `SketchSegment CreateCircleByRadius( System.double XC, System.double YC, System.double Zc, System.double Radius )`
2. **Remarks 逐字摘录**：
   > `This method creates a full circle in the active 2D sketch. If a sketch is not active, then a new sketch is created. ...`
   > `To create a circle using a center point and a point on the circle, see [[ISketchManager::CreateCircle]]. To create a partial arc, see [[ISketchManager::CreateArc]].`
3. **官方例子调用序**：**查不到**（该成员页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：无活动草图会自动新建（原文同 `CreateCircle`）。
**配方一句话**：`(XC, YC, Zc, Radius)` 四值即可。

---

### 1.19 `CreateCircularSketchStepAndRepeat`（method）

1. **精确签名**（**9 个形参**）
   `System.bool CreateCircularSketchStepAndRepeat( System.double ArcRadius, System.double ArcAngle, System.int PatternNum, System.double PatternSpacing, System.bool PatternRotate, System.string DeleteInstances, System.bool RadiusDim, System.bool AngleDim, System.bool CreateNumOfInstancesDim )`
2. **Remarks 逐字摘录**：
   > `The radius, angle, and number of instances dimensions displayed in the graphics area can be modified by interactive users.`
3. **官方例子调用序**（CHM 解包 `Create_and_Edit_Circular_Sketch_Pattern_Example_VB.htm`，逐字，含"先选什么"）：
   ```vbnet
   Set swSketchMgr = swModel.SketchManager
   Set swSketchSegment = swSketchMgr.CreateCircle(0#, 0#, 0#, 0.045549, 0.013926, 0#)
   swModel.ClearSelection2 True
   swModel.ShowNamedView2 "*Front", 1
   vSkLines = swSketchMgr.CreateCornerRectangle(-0.005867589431389, 0.03694408160504, 0, 0.004563680668858, 0.02673012963188, 0)
   boolstatus = swSketchMgr.CreateCircularSketchStepAndRepeat(0.03184378021964, 4.732863934409, 4, 1.570796326795, True, "", True, True, True)
   swModel.ClearSelection2 True
   swSketchMgr.InsertSketch True
   ```
   ★ 注意：例子建完矩形**没有显式 SelectByID2**，而 `EditCircularSketchStepAndRepeat` 之前有：
   ```vbnet
   boolstatus = swModelDocExt.SelectByID2("Line1@Sketch1", "EXTSKETCHSEGMENT", -0.002390499397973, 0.03694408160504, 0, False, 0, Nothing, 0)
   swModel.EditSketch
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内只写了"尺寸可被交互用户改"）。
**配方一句话**：先造实体 → 再调，实参 `("弧半径, 弧角, 实例数, 间距, 是否旋转, 删除实例串, 半径尺寸, 角度尺寸, 实例数尺寸")`。

---

### 1.20 `CreateConic`（method）

1. **精确签名**（**12 个形参**）
   `SketchSegment CreateConic( System.double XFocus, System.double YFocus, System.double ZFocus, System.double XApex, System.double YApex, System.double ZApex, System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2 )`
   参数释义（逐字）：`XFocus/YFocus/ZFocus = focus 坐标`；`XApex/YApex/ZApex = apex 坐标`；`X1/Y1/Z1 = start point 坐标`；`X2/Y2/Z2 = end point 坐标`
2. **Remarks 逐字摘录**：
   > `This method creates a conic curve (circle, ellipse, parabola, or hyperbola) in the active 2D sketch. If a sketch is not active, then a new sketch is created.`
3. **官方例子调用序**（CHM 解包 `Insert_Conic_Curve_Example_VB.htm`，逐字）：
   ```vbnet
   Set Part = swApp.ActiveDoc
   Dim skSegment As SldWorks.SketchSegment
   Set skSegment = Part.SketchManager.CreateConic(0.109436, 0.080614, 0#, 0.048742, 0.022907, 0#, -0.017812, 0#, 0#, -0.006092, -0.069601, 0#)
   Part.SketchManager.InsertSketch True
   Part.ShowNamedView2 "*Isometric", 7
   ```
   ★ **先选什么**：**没有** 任何 `SelectByID2`；新文档直接调用。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：无活动草图会自动新建（原文）。
**配方一句话**：焦点 + 顶点 + 起止两点，共 12 个 double。

---

### 1.21 `CreateConstructionGeometry`（method）

1. **精确签名**（**0 个形参**）
   `void CreateConstructionGeometry()`
2. **Remarks 逐字摘录**：
   > `This method supports all document types, unlike [[IDrawingDoc::CreateConstructionGeometry]], which only supports drawing documents. Both methods perform the same functionality.`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：支持所有文档类型（**对照**：`IDrawingDoc::CreateConstructionGeometry` 只支持工程图）。
**配方一句话**：**查不到**。

---

### 1.22 `CreateCornerRectangle`（method）

1. **精确签名**（**6 个形参**）
   `System.object CreateCornerRectangle( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2 )`
   参数释义（逐字）：`X1: Upper-left X coordinate for point 1`；`Y1: Upper-left Y coordinate for point 1`；`Z1: Upper-left Z coordinate for point 1`；`X2/Y2/Z2: Lower-right … for point 2`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**（CHM 解包，逐字）：
   · `Create_and_Edit_Circular_Sketch_Pattern_Example_VB.htm`：
     ```vbnet
     vSkLines = swSketchMgr.CreateCornerRectangle(-0.005867589431389, 0.03694408160504, 0, 0.004563680668858, 0.02673012963188, 0)
     ```
   · `Autodimension_a_Sketch_Example_VB.htm`：
     ```vbnet
     sketchLines = swSketchManager.CreateCornerRectangle(0, 0, 0, 0.110951010058045, -0.066328380491143, 0)
     ```
   · `Create_and_Edit_Linear_Sketch_Pattern_Example_VB.htm`：
     ```vbnet
     vSkLines = swSketchMgr.CreateCornerRectangle(-0.07606134448097, 0.04933121484909, 0, 0.07649598073515, -0.0510697598658, 0)
     vSkLines = swSketchMgr.CreateCornerRectangle(-0.00838865116811, 0.00609746454014, 0, 0.00738895920642, -0.007221297464333, 0)
     ```
   · `Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md`：
     ```vbnet
     vSkLines = Part.SketchManager.CreateCornerRectangle(-0.05171778666374, 0.01933785938058, 0.03, 0.08445537697179, -0.04142795937025, -0.03)
     ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：传左上角点 + 右下角点（6 个 double）；返回 `System.object`。

---

### 1.23 `CreateEllipse`（method）

1. **精确签名**（**9 个形参**）
   `SketchSegment CreateEllipse( System.double XC, System.double YC, System.double Zc, System.double XMajor, System.double YMajor, System.double ZMajor, System.double XMinor, System.double YMinor, System.double ZMinor )`
2. **Remarks 逐字摘录**：
   > `This method creates a full ellipse in the active 2D sketch. If a sketch is not active, then a new sketch is created.`
   > `To create a partial ellipse, use [[ISketchManager::CreateEllipticalArc]].`
3. **官方例子调用序**：CHM 解包 `Create_Ellipse_Example_VB.htm` **存在（13321 字节）但正文只到 `Option Explicit` 就没有函数体**（已逐行读）；`C:\swapi\examples\Create_Ellipse_Example_VB.md` 同样只有前置注释 → **调用序查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：无活动草图会自动新建；想做**部分**椭圆改用 `CreateEllipticalArc`。
**配方一句话**：**查不到**（官方例子正文缺函数体）。

---

### 1.24 `CreateEllipticalArc`（method）

1. **精确签名**（**15 个形参**）
   `SketchSegment CreateEllipticalArc( System.double XC, System.double YC, System.double Zc, System.double XMajor, System.double YMajor, System.double ZMajor, System.double XMinor, System.double YMinor, System.double ZMinor, System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.short Direction )`
2. **Remarks 逐字摘录**：
   > `This method creates a full circle in the active 2D sketch. If a sketch is not active, then a new sketch is created. …`（★ 官方原文这里写的是 **"full circle"**，与成员名不符，逐字照抄不改）
   > `To create a complete ellipse, use [[ISketchManager::CreateEllipse]].`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里 `System.short Direction` —— **该成员页未点名任何枚举 → 查不到**。
5. **废弃链**：**查不到**。
**前置一句话**：无活动草图会自动新建（原文如此）。
**配方一句话**：**查不到**。

---

### 1.25 `CreateEquationSpline`（method，★ Obsolete）

1. **精确签名**（**9 个形参**）
   `SketchSpline CreateEquationSpline( System.string YExpression, System.double RangeStart, System.double RangeEnd, System.bool IsAngleRange, System.double RotationAngle, System.double XOffset, System.double YOffset, System.bool LockStart, System.bool LockEnd )`
2. **Remarks 逐字摘录**：
   > `**YExpression:** Any function that you can define as a 2D function in the following form: y-in-the-sketch = f(x-in-the-sketch) will appear as a curve in the sketch. For example: y = sin(x)`
   > `**RangeStart** and **RangeEnd** You cannot specify string values for RangeStart and RangeEnd; you must specify double values.`
   > `**XOffset:** In the equation: y = sin(x) [x=0 to 2Pi] the start point (0,0) is moved by XOffset in the x direction.`
3. **官方例子调用序**（`C:\swapi\examples\Create_Equation-driven_Curve_Example_VB.md`，逐字；★ 那是 **Spline2** 的调用）：
   ```vbnet
   swModel.SketchManager.InsertSketch True
   Set skSegment = swModel.SketchManager.CreateEquationSpline2("", "sin(x)", "", "0", "6.28", False, 0, 0, 0, True, True)
   swModel.SketchManager.InsertSketch True
   ```
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISketchManager::CreateEquationSpline2]].`
**前置一句话**：**查不到**（页内未写前置）。
**配方一句话**：已 Obsolete；同族新写法见 1.26 的实参 `(XExpr, YExpr, ZExpr, RangeStart, RangeEnd, IsAngleRange, RotationAngle, XOffset, YOffset, LockStart, LockEnd)`。

---

### 1.26 `CreateEquationSpline2`（method）

1. **精确签名**（**11 个形参**）
   `SketchSpline CreateEquationSpline2( System.string XExpression, System.string YExpression, System.string ZExpression, System.string RangeStart, System.string RangeEnd, System.bool IsAngleRange, System.double RotationAngle, System.double XOffset, System.double YOffset, System.bool LockStart, System.bool LockEnd )`
2. **Remarks 逐字摘录**：
   > `**XExpression** If you want: - an explicit curve (only in 2D) of the form y=f(x), then this input should be "". - a parametric curve given in terms of the parameter t, then this input is the value of x given in terms of the parameter. For example: x=sin(t)`
   > `**YExpression** … then this input should be a function in terms of x to use to compute the value of y. For example: y=exp(x) … this input is the value of y given in terms of the parameter. For example: y=cos(t)`
   > `**ZExpression** For 3D parametric curves, this input is the value of z given in terms of parameter t. For example: z = t`
   > `**RangeStart** and **RangeEnd** Strings so that you can input dimension names or pi; for example, "10* width_dimension1" or "-pi/2".`
   > `**XOffset**, **YOffset**, **IsAngleRange**, and **RotationAngle** In general, these parameters are not needed. They are for legacy support only. There are no equivalent 3D variables for positioning in 3D.`
3. **官方例子调用序**（`C:\swapi\examples\Create_Equation-driven_Curve_Example_VB.md`，逐字）：
   ```vbnet
   swModel.SketchManager.InsertSketch True
   Set skSegment = swModel.SketchManager.CreateEquationSpline2("", "sin(x)", "", "0", "6.28", False, 0, 0, 0, True, True)
   swModel.SketchManager.InsertSketch True
   ```
   ★ 先 `InsertSketch True`、画完再 `InsertSketch True`。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行）。
**前置一句话**：**查不到**（页内未写"必须先有活动草图"）。
**配方一句话**：显式曲线把 `XExpression` 传 `""`；`RangeStart/RangeEnd` 是**字符串**（可写 `pi` 或尺寸名），与旧版必须是 double 不同。

---

### 1.27 `CreateFillet`（method）

1. **精确签名**（**2 个形参**）
   `SketchSegment CreateFillet( System.double Radius, System.int ConstrainedCorners )`
   参数释义（逐字）：`- **Radius**: Radius of the fillet in meters`；`- **ConstrainedCorners**: Action to take as defined in [[swConstrainedCornerAction_e]] (see **Remarks**)`
2. **Remarks 逐字摘录**：
   > `The ConstrainedCorners parameter indicates what action to take if the corner to fillet is constrained or dimensioned. If the corner is not constrained or dimensioned, then this parameter is ignored.`
3. **官方例子调用序**（CHM 解包 `Edit_Radial_Dimension_Example_VB.htm`，逐字，含"先选什么"）：
   ```vbnet
   status = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, False, 0, Nothing, 0)
   swModel.EditSketch
   swModel.ClearSelection2 True
   status = swModelDocExt.SelectByID2("Point1", "SKETCHPOINT", -8.11067833265636E-02, 3.89478433654258E-02, 0, False, 0, Nothing, 0)
   Set swSketchManager = swModel.SketchManager
   Set swSketchSegment = swSketchManager.CreateFillet(0.01, swConstrainedCornerAction_e.swConstrainedCornerDeleteGeometry)
   ```
4. **枚举**：`swConstrainedCornerAction_e` → `swConstrainedCornerInteract=0` / `swConstrainedCornerKeepGeometry=1` / `swConstrainedCornerDeleteGeometry=2` / `swConstrainedCornerStopProcessing=3`。
5. **废弃链**：**查不到**。
**前置一句话**：先 `SelectByID2("Sketch1","SKETCH",…)` + `swModel.EditSketch` 进编辑态，再 `SelectByID2("Point1","SKETCHPOINT",…)` 选中角点。
**配方一句话**：`CreateFillet(0.01, swConstrainedCornerAction_e.swConstrainedCornerDeleteGeometry)`。

---

### 1.28 `CreateLine`（method）

1. **精确签名**（**6 个形参**）
   `SketchSegment CreateLine( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2 )`
2. **Remarks 逐字摘录**（★ 前置原话）：
   > `If a sketch is not active, then the line is not created and NULL is returned. You can check for an active sketch using the [[ISketchManager::ActiveSketch]] function.`
   > `When this method is used with a drawing document, this method creates the line relative to the active drawing view, [[IDrawingDoc::ActiveDrawingView]] or [[IDrawingDoc::IActiveDrawingView]].`
3. **官方例子调用序**（CHM 解包，逐字）：
   · `Sketch_Offset_Example_VB.htm`：
     ```vbnet
     swSketchManager.InsertSketch True
     status = swModelDocExt.SelectByID2("Top Plane", "PLANE", -7.70466366627886E-02, 2.33041566204965E-03, 3.90732100788036E-02, False, 0, Nothing, 0)
     swModel.ClearSelection2 True
     Set swSketchSegment = swSketchManager.CreateLine(-0.081532, 0.028203, 0#, -0.029228, -0.017264, 0#)
     ```
   · `Split_Open_Sketch_Segment_Example_VB.md`：
     ```vbnet
     swModel.SketchManager.InsertSketch True
     Set swSketchSegment = swModel.SketchManager.CreateLine(-0.055964, 0.033212, 0#, 0.102938, -0.014129, 0#)
     skSegmentArray = swModel.SketchManager.SplitOpenSegment(0.02, 0.01, 0#)
     swModel.SketchManager.Insert3DSketch True
     ```
   · `Create_Sketch_Path_Example_VB.htm`：
     ```vbnet
     swModel.SketchManager.InsertSketch True
     boolstatus = swModel.Extension.SelectByID2("Front Plane", "PLANE", -4.16217612836357E-02, 2.70960165695038E-02, 3.55460240358513E-03, False, 0, Nothing, 0)
     Set skSegment = swModel.SketchManager.CreateLine(-0.055655, 0.037535, 0#, 0.011848, 0.039924, 0#)
     ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`If a sketch is not active, then the line is not created and NULL is returned` —— 与 `CreateArc`/`CreateCircle` 的"自动新建草图"**不同**（逐字照抄，不改写）。
**配方一句话**：先 `InsertSketch True` + `SelectByID2(<plane>,"PLANE",…)` + `ClearSelection2 True`，再给两点坐标。

---

### 1.29 `CreateLinearSketchStepAndRepeat`（method）

1. **精确签名**（**12 个形参**）
   `System.bool CreateLinearSketchStepAndRepeat( System.int NumX, System.int NumY, System.double SpacingX, System.double SpacingY, System.double AngleX, System.double AngleY, System.string DeleteInstances, System.bool XSpacingDim, System.bool YSpacingDim, System.bool AngleDim, System.bool CreateNumOfInstancesDimInXDir, System.bool CreateNumOfInstancesDimInYDir )`
2. **Remarks 逐字摘录**：
   > `The spacing instances, angle, and number of instances dimensions displayed in the graphics area can be modified by interactive users.`
3. **官方例子调用序**（CHM 解包 `Create_and_Edit_Linear_Sketch_Pattern_Example_VB.htm`，逐字）：
   ```vbnet
   swSketchMgr.InsertSketch True
   vSkLines = swSketchMgr.CreateCornerRectangle(-0.07606134448097, 0.04933121484909, 0, 0.07649598073515, -0.0510697598658, 0)
   vSkLines = swSketchMgr.CreateCornerRectangle(-0.00838865116811, 0.00609746454014, 0, 0.00738895920642, -0.007221297464333, 0)
   boolstatus = swSketchMgr.CreateLinearSketchStepAndRepeat(2, 2, 0.0254, 0.0254, 0.296705972839, 1.134464013796, "", True, True, False, True, True)
   swSketchMgr.InsertSketch True
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：`(2, 2, 0.0254, 0.0254, 0.296705972839, 1.134464013796, "", True, True, False, True, True)`。

---

### 1.30 `CreateParabola`（method）

1. **精确签名**（**12 个形参**）
   `SketchSegment CreateParabola( System.double XFocus, System.double YFocus, System.double ZFocus, System.double XApex, System.double YApex, System.double ZApex, System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2 )`
   参数释义（逐字）：`focus 坐标` / `apex 坐标` / `start point 坐标` / `end point 坐标`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.31 `CreateParallelogram`（method）

1. **精确签名**（**9 个形参**）
   `System.object CreateParallelogram( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.double X3, System.double Y3, System.double Z3 )`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.32 `CreatePoint`（method）

1. **精确签名**（**3 个形参**）
   `SketchPoint CreatePoint( System.double X, System.double Y, System.double Z )`
2. **Remarks 逐字摘录**（★ 前置原话）：
   > `This method creates a point in the active 2D or 3D sketch. If a sketch is not active, the point is not created and NULL is returned. Use [[ISketchManager::ActiveSketch]] to check to see if the sketch is active.`
3. **官方例子调用序**（CHM 解包 `Create_Block_Definition_and_Insert_Block_Instance_Example_VB.htm`，逐字）：
   ```vbnet
   swSketchMgr.AddToDB = True
   Set swSkSeg(0) = swSketchMgr.CreateLine(0.008372353756316, 0.207929860362, 0#, 0.05495488122133, 0.207929860362, 0#)
   ...
   Set swSkPt(0) = swSketchMgr.CreatePoint(0.02700536474232, 0.1708856599494, 0#)
   Set swSkPt(1) = swSketchMgr.CreatePoint(0.02700536474232, 0.1815330947985, 0#)
   Set swSkPt(2) = swSketchMgr.CreatePoint(0.03964919362569, 0.1815330947985, 0#)
   Set swSkPt(3) = swSketchMgr.CreatePoint(0.05029662847483, 0.1708856599494, 0#)
   ...
   swSketchMgr.AddToDB = False
   ```
   ★ `C:\swapi\examples\Create_Sketch_Point_Example_VB.md` 与 CHM `Create_Sketch_Point_Example_VB.htm` 正文**只有前置注释、无函数体**（已逐行读）→ 该例调用序查不到。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`If a sketch is not active, the point is not created and NULL is returned`。
**配方一句话**：`(X, Y, Z)` 三个 double；无活动草图会返回 NULL。

---

### 1.33 `CreatePolygon`（method）

1. **精确签名**（**7 个形参**）
   `System.object CreatePolygon( System.double XC, System.double YC, System.double Zc, System.double Xp, System.double Yp, System.double Zp, System.int Sides, System.bool Inscribed )`
   参数释义（逐字）：`Xp: X coordinate of a vertex`；`Sides: Number of sides in the polygon`；`Inscribed: True to show an inscribed construction circle, false to show a circumscribed construction circle`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：中心 + 一个顶点 + 边数 + `Inscribed`（true=内切构造圆，false=外接）。

---

### 1.34 `CreateRegionHatch`（method）

1. **精确签名**（**8 个形参**）
   `SketchHatch CreateRegionHatch( System.double X, System.double Y, System.double Z, System.double Angle, System.double Scale, System.int Color, System.string Hatchname, System.string Layername )`
   参数释义（逐字）：`X/Y/Z: coordinate anywhere within the closed sketch profile`；`Hatchname: Type or name of the hatch from the **Sldwks.ptn** file`
2. **Remarks 逐字摘录**（★ 前置语义原话）：
   > `This method creates a single area hatch/fill region hatch. All three point coordinates are important. This point is compared to all sketch contours to determine one unique external sketch region that contains the point.`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：★ **不要求"先选中轮廓"** —— 官方写的是"把这一点与所有草图轮廓比较，定位唯一包含它的区域"（与 `CreateBoundaryHatch` 的"必须先选中闭合轮廓"**不同**）。
**配方一句话**：传入**落在**闭合轮廓内部的一个点坐标 + 花纹参数。

---

### 1.35 `CreateSketchBelt`（method）

1. **精确签名**（**15 个形参**）
   `System.bool CreateSketchBelt( System.double Length, System.double Thickness, System.int Engage, System.int PulleyCount, System.int Side1, System.int Side2, System.int Side3, System.int Side4, System.int Side5, System.int Side6, System.int Side7, System.int Side8, System.int Side9, System.int Side10, System.int Side11, System.int Side12 )`
   参数释义（逐字）：`Engage: 1 to engage the belt, 0 to not`；`PulleyCount: Number of pulley components`；`Side1..Side12: Place the belt for the corresponding pulley component: - 0 = inside - 1 = outside`
2. **Remarks 逐字摘录**（★ 选择语义原话）：
   > `The order of the sides corresponds to the order of the pulleys in the selection list. For example Side1 indicates on which side of the first pulley component in the selection list you want the belt placed. If only four pulley components exist in the sketch, then Side5 - Side12 are ignored. This method limits you to 12 pulleys.`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无（`Side*` 的 0/1 直接写在 `## Parameters` 里，不是命名枚举）。
5. **废弃链**：**查不到**。
**前置一句话**：★ **`Side1..Side12` 的顺序 = 选区里皮带轮的顺序**（必须先按顺序选好皮带轮）。
**配方一句话**：**查不到**（无例子）。

---

### 1.36 `CreateSketchPlane`（method，3D 草图面）

1. **精确签名**（**3 个形参**）
   `System.bool CreateSketchPlane( System.int Relation1, System.int Relation2, System.int Relation3 )`
   参数释义（逐字）：`- **Relation1**: Relation as defined in [[swConstraintType_e]] for the first selection to position the 3D sketch plane`（`Relation2` / `Relation3` 同构，分别对第二、第三次选择）
2. **Remarks 逐字摘录**（★ 前置原话）：
   > `This method gets the selected items from the selection list in the order in which they were selected and applies the specified relation to them. If fewer than three items were selected, then only the first, or first and second, values are used.`
3. **官方例子调用序**（CHM 解包 `Create_3D_Sketch_Plane_Example_VB.htm`，逐字，含"先选什么"与 mark）：
   ```vbnet
   swSketchManager.Insert3DSketch True
   ...
   status = swModelDocExt.SelectByID2("Line1@3DSketch1", "EXTSKETCHSEGMENT", -5.65609614209999E-02, 3.70796232466087E-02, 0, True, 0, Nothing, 0)
   status = swModelDocExt.SelectByID2("Point2@Sketch1", "EXTSKETCHPOINT", -5.64010297276809E-02, 5.98490302365917E-03, 0, True, 0, Nothing, 0)
   status = swSketchManager.CreateSketchPlane(9, 9, 0)
   status = swModelDocExt.SelectByID2("Plane1", "SKETCHSURFACES", 0, 0, 0, False, 0, Nothing, 0)
   swModel.ActivateSelectedFeature
   swModel.ClearSelection2 True
   swSketchManager.InsertSketch True
   ```
   ★ 例子用的 **mark = 0**（两个选择都是 `SelectByID2(..., True, 0, Nothing, 0)`）。
4. **枚举**：`swConstraintType_e`（参数释义点名）。★ **逐条数值本轮未抄 → 查不到**；官方例子的实参是 `9, 9, 0`。
5. **废弃链**：**查不到**。
**前置一句话**：必须**先在选区里**放好 3D 草图平面要用的实体（例子用 `EXTSKETCHSEGMENT` + `EXTSKETCHPOINT`），调用按选区顺序取。
**配方一句话**：`SelectByID2(…, Append=True, Mark=0)` 两个实体 → `CreateSketchPlane(9, 9, 0)`。

---

### 1.37 `CreateSketchSlot`（method）

1. **精确签名**（**13 个形参**）
   `SketchSlot CreateSketchSlot( System.int SlotCreationType, System.int SlotLengthType, System.double Width, System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.double X3, System.double Y3, System.double Z3, System.int CenterArcDirection, System.bool AddDimension )`
   参数释义（逐字）：`SlotCreationType: Type of sketch slot as defined in [[swSketchSlotCreationType_e]]`；`SlotLengthType: … [[swSketchSlotLengthType_e]]`；`CenterArcDirection: - -1 = Clockwise (CW) - 1 = Counterclockwise (CCW)`；`AddDimension: True to automatically add dimensions, false to not`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**（`C:\swapi\examples\Insert_and_Resize_Sketch_Slot_Example_VB.md`，逐字）：
   ```vbnet
   Set swSketchSlot = skManager.CreateSketchSlot(swSketchSlotCreationType_e.swSketchSlotCreationType_line, swSketchSlotLengthType_e.swSketchSlotLengthType_CenterCenter, 0.05, -0.05, 0, 0, 0.05, 0, 0, 0, 0, 0, 1, False)
   ```
4. **枚举**：`swSketchSlotCreationType_e`（`line=0` / `center_line=1` / `arc=2` / `3pointarc=3`）、`swSketchSlotLengthType_e`（`CenterCenter=0` / `FullLength=1`）。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：`(创建类型, 长度类型, 宽度, 三个点共 9 个坐标, 弧方向, 是否自动加尺寸)`。

---

### 1.38 `CreateSpline`（method，★ Obsolete）

1. **精确签名**（**1 个形参**）
   `SketchSegment CreateSpline( System.object PointData )`
   参数释义（逐字）：`- **PointData**: Array of X,Y,Z point coordinates to use in creating the spline (see **Remarks**)`
2. **Remarks 逐字摘录**（★ **数组形状原话，用户点名要抄的**）：
   > `This method creates a spline in the active 2D sketch. If a sketch is not active, then a new sketch is created. Use [[ISketchManager::ActiveSketch]] to check if the sketch active.`
   > `The PointData array is a set of, at least, two X, Y, Z values. For example, in VBA and VB.NET, the X value for the start point of the spline is PointData[0], the Y value for the start point is PointData[1], and the Z value for the start point is PointData[2]. The X value for the next point is PointData[3], and so on.`
   > `This method does not work with [[ISketchManager::AddToDB]] or [[ISketchManager::DisplayWhenAdded]]. It always adds the spline directly to the database (as if ISketchManager::AddToDB(True) was in effect), and you must redraw your document window to see the entities that you added (as if ISketchManager::DisplayWhenAdded(False) was in effect).`
   > `In 2D sketches, SOLIDWORKS ignores the Z value in PointData.`
3. **官方例子调用序**（CHM 解包 `Get_Each_Splines_Parameters_Example_VB.htm`，逐字）：
   ```vbnet
   Dim points(11) As Double
   ...
   points(0) = -0.185955019567672
   points(1) = 4.16208582005027E-02
   points(2) = 0
   points(3) = -8.62492383138544E-02
   points(4) = 4.03922105323034E-02
   points(5) = 0
   points(6) = -6.72740896322921E-02
   points(7) = 5.40598971292923E-02
   points(8) = 0
   points(9) = -1.41436733240425E-02
   points(10) = -5.70437188125084E-03
   points(11) = 0
   pointArray = points
   Set swSketchMgr = swModel.SketchManager
   Set swSketchSegment = swSketchMgr.CreateSpline((pointArray))
   ```
   ★ 形状：`Dim points(11) As Double` ⇒ **12 个 double = 4 个点 × (X,Y,Z)**，VBA 里 0-based 下标是 `0..11`。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISketchManager::CreateSpline2]].`
**前置一句话**：`This method does not work with ISketchManager::AddToDB or ISketchManager::DisplayWhenAdded`（它恒等价于 `AddToDB(True)` + `DisplayWhenAdded(False)`）。
**配方一句话**：`PointData` 是**扁平** double 数组，`[0]=x0, [1]=y0, [2]=z0, [3]=x1 …`；2D 草图里 Z 被忽略；至少两个 XYZ 三元组。

---

### 1.39 `CreateSpline2`（method，★ Obsolete）

1. **精确签名**（**2 个形参**）
   `SketchSegment CreateSpline2( System.object PointData, System.bool SimulateNaturalEnds )`
2. **Remarks 逐字摘录**：与 `CreateSpline` **逐字相同**（同样四段，含 `The PointData array is a set of, at least, two X, Y, Z values …` 与 `In 2D sketches, SOLIDWORKS ignores the Z value in PointData.`）
   ★ 差异只在签名多出的 `SimulateNaturalEnds`。
3. **官方例子调用序**：
   · `C:\swapi\examples\Insert_a_Composite_Curve_Example_VB.md`（逐字）：
     ```vbnet
     ReDim points(0 To 11) As Double
     points(0) = -5.09020857536935E-02
     …
     pointArray = points
     Set swSketchSegment = swSketchManager.CreateSpline2((pointArray), True)
     ```
   · `C:\swapi\examples\Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md`：
     ```vbnet
     Set skSegment = Part.SketchManager.CreateSpline2((pointArray), True)
     ```
   · CHM `Get_Spline's_Parameters_Example_VB.md` 同族。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISketchManager::CreateSpline3]].`
**前置一句话**：同 `CreateSpline` —— 与 `AddToDB` / `DisplayWhenAdded` **不兼容**。
**配方一句话**：`CreateSpline2((pointArray), True)`；第二形参 `True` = 模拟自然端点。

---

### 1.40 `CreateSpline3`（method，★ 当前代）

1. **精确签名**（**5 个形参**）
   `System.object CreateSpline3( System.object PointData, System.object Surfs, System.object Direction, System.bool SimulateNaturalEnds, out System.object Status )`
   参数释义（逐字）：`- **PointData**: Array of X,Y,Z coordinates of the spline points (see **Remarks**)`；`- **Surfs**: Array of [[ISurface]] objects; null or Nothing for 2D splines`；`- **Direction**: Array of [[IMathVector]] objects; valid only for on-surface splines`；`- **SimulateNaturalEnds**: True to simulate natural ends, false to not; valid only for 2D splines`；`- **Status**: Array of boolean values; empty for 2D splines`
2. **Remarks 逐字摘录**（★ **数组形状 + 前置，用户点名要抄的**）：
   > `To create a 2D spline, specify:`
   > `- PointData with at least six coordinates (for the start and end points of the spline): [*start_pt_x, start_pt_y, start_pt_z, end_pt_x, end_pt_y, end_pt_z*] For 2D sketches, SOLIDWORKS assumes PointData contains no Z values.`
   > `- SimulateNaturalEnds with true for zero curvature end conditions or false to maintain curvature at the ends.`
   > `- All other parameters with null or Nothing.`
   > `To create an on-surface spline, specify:`
   > `- PointData with two or more points anywhere in 3D space. Each spline point will project onto a surface in the Surf array, depending on the direction vector specified for each point in the Direction array.`
   > `- Surf with an array of surfaces onto which the PointData is projected.`
   > `- Direction with an array of vectors, which are projection directions for every point in the PointData array. If Direction is Nothing or null, then the view vector for the current screen view is used to project each point onto a surface.`
   > `For on-surface splines only, Status contains an array of statuses, one for each point in PointArray. True indicates that the point successfully projects onto one of the surfaces.`
   > `This method: - Creates the 2D spline in the active sketch. If a sketch is not active, then a new sketch is created. … - Creates a new 3D sketch to create the on-surface spline. Call [[ISketchManager::InsertSketch]] to finalize the sketch. - Does not work with [[ISketchManager::AddToDB]] or [[ISketchManager::DisplayWhenAdded]].`
3. **官方例子调用序**（`C:\swapi\examples\Create_On-surface_Spline_Example_VB.md`，逐字，含"先选什么"与 mark）：
   ```vbnet
   ReDim points(0 To 11) As Double
   points(0) = -3.34270787209949E-02
   points(1) = 2.23913424029847E-02
   points(2) = 0.053671471463652
   points(3) = 1.53063989576147E-02
   points(4) = 4.78899892864157E-02
   points(5) = 2.50019220828396E-02
   points(6) = 5.11644715447442E-02
   points(7) = 2.72060072570875E-02
   points(8) = 5.78476387745854E-03
   points(9) = 2.59263831071606E-03
   points(10) = 2.62831648993199E-02
   points(11) = -0.053206707614433
   pointArray = points
   boolstatus = Part.Extension.SelectByRay(0.030303902514845, 2.86262382667246E-02, 3.85109058888133E-02, -0.577381545199981, -0.577287712085548, -0.577381545199979, 1.78932209693826E-03, 2, False, 0, 0)
   Set swSelMgr = Part.SelectionManager
   selType = swSelMgr.GetSelectedObjectType3(1, -1)
   surfaceArrUbound = -1
   If selType = swSelFACES Then
     Set swCurFace = swSelMgr.GetSelectedObject6(1, -1)
     surfaceArrUbound = surfaceArrUbound + 1
     ReDim Preserve surfaceArr(0 To surfaceArrUbound) As Surface
     Set surfaceArr(surfaceArrUbound) = swCurFace.GetSurface()
   End If
   surfs = surfaceArr
   'Set Direction parameter to Nothing to use the view vector of the current view
   'to project the points in the pointArray onto the surface in the surfs array
   Set skSegment = Part.SketchManager.CreateSpline3((pointArray), surfs, Nothing, True, statuses)
   Part.SketchManager.InsertSketch True
   ```
   ★ **先选什么**：`Part.Extension.SelectByRay(…, 2, False, 0, 0)` 选中面，再取 `swCurFace.GetSurface()`。
   ★ 收尾：`Part.SketchManager.InsertSketch True`。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行；它是 `CreateSpline2` 点名的后继）。
**前置一句话**：2D 用"全部其他参数 null/Nothing"；曲面上样条必须先建 **3D 草图**并**先选面**取 `ISurface`，收尾要 `InsertSketch`。
**配方一句话**：2D：`PointData` **至少 6 个**坐标（只有首尾两点）；曲面上：`PointData`≥2 点 + `Surfs` 数组 + 可选 `Direction`（Nothing 则用当前视图向量）+ `Status` 布尔数组。

---

### 1.41 `CreateSplineByEqnParams`（method）

1. **精确签名**（**1 个形参**）
   `SketchSegment CreateSplineByEqnParams( System.object Parameters )`
2. **Remarks 逐字摘录**（★ **三个数组的形状原话，用户点名要抄的**）：
   > `The Properties array contains four longs (placed in the first four doubles in the array): - Dimension - Order - Number of Control Points - Periodicity ( true or false)`
   > `The Knots array contains doubles with (Number of Control Points + Order) elements.`
   > `The size of the ControlPoints array is based upon the curve dimension. - Dimension = 2 then each Control Point is an array of 2 doubles ( x, y ) - Dimension = 3 then each Control Point is an array of 3 doubles ( x, y, z ) - Dimension = 4 then each Control Point is an array of 4 doubles ( x, y, z, w ) where w = weight`
   > `The parameters are provided as three arrays.`
   > `Pass the control point coordinates to this routine in sketch space. The Z value is interpreted as 0. In certain situations, you must transform your B-curve parameters to sketch space using [[ISketch::ModelToSketchTransform]].`
   > `**NOTE:** The curve can be either periodic or non-periodic. If the generated spline is a closed spline, then it must be flagged as periodic. Additionally, splines generated in sketches must be G1 continuous. If the data passed to this method does not generate a G1 continuous spline, then it is rejected and a spline is not created. If your data is not G1 continuous, then you must split the spline into multiple G1 segments and call this method for each segment.`
   > `This method does not work with [[ISketchManager::AddToDB]] or [[ISketchManager::DisplayWhenAdded]].`
   > `To create 3D splines, see [[IModelDoc2::InsertCurveFilePoint]] and related functions.`
3. **官方例子调用序**：**查不到**（该成员页无 `## Examples` 段；`## See Also` 只指向同族的 `ICreateSplineByEqnParams` / `ICreateSplinesByEqnParams`）。
4. **枚举**：签名里无（数组里装的是 long/double，不是命名枚举）。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行）。
**前置一句话**：坐标必须**在草图空间**（Z 解释为 0）；不 G1 连续会被**拒绝、不建**；与 `AddToDB`/`DisplayWhenAdded` 不兼容。
**配方一句话**：一个 `Parameters` 对象里装**三个数组**：`Properties`（4 个 long 放在头 4 个 double 槽）、`Knots`（`控制点数+阶数` 个 double）、`ControlPoints`（`控制点数 × 维数` 个 double）。

---

### 1.42 `CreateSplineParamData`（method）

1. **精确签名**（**0 个形参**）
   `SplineParamData CreateSplineParamData()`
2. **Remarks 逐字摘录**：**空 —— 官方没写**（该页无 `## Parameters` 也无 `## Remarks`）。
3. **官方例子调用序**（`C:\swapi\examples\Get_Spline's_Parameters_Example_VB.md`，逐字，★ 当前代样条配方）：
   ```vbnet
   Dim swSplineParaData As SldWorks.SplineParamData
   Dim arrCtrlPts(17) As Double
   Dim arrKnotPts(9) As Double
   ...
   Set swSplineParaData = swSketchMgr.CreateSplineParamData
   swSplineParaData.Dimension = 3
   swSplineParaData.Order = 4
   swSplineParaData.Periodic = 0
   swSplineParaData.ControlPointsCount = 6
   arrCtrlPts(0) = -0.0508
   arrCtrlPts(1) = 0.0254
   arrCtrlPts(2) = 0
   … (18 个)
   boolStatus = swSplineParaData.SetControlPoints(arrCtrlPts)
   arrKnotPts(0) = 0 … arrKnotPts(9) = 1
   boolStatus = swSplineParaData.SetKnotPoints(arrKnotPts)
   varSeg = swSketchMgr.CreateSplinesByEqnParams2(swSplineParaData)
   swSketchMgr.InsertSketch (True)
   …
   Set swSplineParaData = swSketch.GetSplineParams4(True)
   ```
   ★ **数组形状**：`ControlPointsCount = 6`、`Dimension = 3` ⇒ `Dim arrCtrlPts(17) As Double` = **18 个**（6×3）；`Order = 4`、`Periodic = 0` ⇒ `Dim arrKnotPts(9) As Double` = **10 个**（6+4）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内为空）。
**配方一句话**：见上方原话 —— 设 `Dimension/Order/Periodic/ControlPointsCount` → `SetControlPoints` → `SetKnotPoints` → 交给 `CreateSplinesByEqnParams2`。

---

### 1.43 `CreateSplinesByEqnParams`（method，★ Obsolete）

1. **精确签名**（**1 个形参**）
   `System.object CreateSplinesByEqnParams( System.object Parameters )`
2. **Remarks 逐字摘录**（与 1.41 **逐字同文**，唯二差别逐字如下）：
   > `**NOTE:** If the spline being generated is a closed spline, then it must be flagged as periodic. If the data passed to this method does not generate a G1 continuous spline, then it creates multiple G1 continuous spline segments.`
   （★ 与 1.41 的 `it is rejected and a spline is not created` **不同** —— 这里是"拆成多段"；逐字照抄。）
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISketchManager::CreateSplinesByEqnParams2]].`
**前置一句话**：非 G1 连续时**不拒绝**，而是**拆成多个 G1 段**（与 `CreateSplineByEqnParams` 相反）。
**配方一句话**：**查不到**（无例子；数组形状与 1.41 同文）。

---

### 1.44 `CreateSplinesByEqnParams2`（method，★ 当前代）

1. **精确签名**（**1 个形参**）
   `System.object CreateSplinesByEqnParams2( SplineParamData ParamData )`
   参数释义（逐字）：`- **ParamData**: [[ISplineParamData]]`
2. **Remarks 逐字摘录**：**空 —— 官方没写**（该页无 `## Parameters` / `## Remarks`）。
3. **官方例子调用序**（`C:\swapi\examples\Get_Spline's_Parameters_Example_VB.md`，逐字）：
   ```vbnet
   varSeg = swSketchMgr.CreateSplinesByEqnParams2(swSplineParaData)
   swSketchMgr.InsertSketch (True)
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行；它是 1.43 点名的后继）。
**前置一句话**：**查不到**（页内为空）。
**配方一句话**：`ParamData` 由 `CreateSplineParamData()` 造，逐项设好属性再传进来；随后 `InsertSketch (True)` 收尾。

---

### 1.45 `CreateTangentArc`（method）

1. **精确签名**（**7 个形参**）
   `SketchSegment CreateTangentArc( System.double X1, System.double Y1, System.double Z1, System.double X2, System.double Y2, System.double Z2, System.int ArcType )`
   参数释义（逐字）：`X1/Y1/Z1: coordinate of start point in meters`；`X2/Y2/Z2: … end point in meters`；`ArcType: Type of tangent arc as defined in [[swTangentArcTypes_e]]`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swTangentArcTypes_e` → `swForward=1` / `swLeft=2` / `swBack=3` / `swRight=4`。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内未写；`in meters` 原文见 `## Parameters`）。
**配方一句话**：**查不到**。

---

### 1.46 `CurvatureDensity`（property）

1. **精确签名**（0 个形参）
   `System.int CurvatureDensity {get; set;}`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.47 `CurvatureScale`（property）

1. **精确签名**（0 个形参）
   `System.double CurvatureScale {get; set;}`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.48 `DisplayWhenAdded`（property）

1. **精确签名**（0 个形参）
   `System.bool DisplayWhenAdded {get; set;}`
2. **Remarks 逐字摘录**（★ 前置 + 收尾必读，逐字）：
   > `The sketch entities appear on the screen after performing [[IModelView::GraphicsRedraw]] or [[IModelView::IGraphicsRedraw]] or [[IModelDoc2::EditRebuild3]] is performed. Also, [[ISketchManager::AddToDB]] must be true to use this method's settings.`
   > `This display setting remains even after your program run has ended. Therefore, it is recommended that you reset this parameter to TRUE at the end of your program.`
   > `**NOTES:** - IModelView::GraphicsRedraw and IModelView::IGraphicsRedraw are much faster than IModelDoc2::EditRebuild3.`
3. **官方例子调用序**：**查不到**（该成员页无 `## Examples` 段；`AddToDB` 的例子见 1.5）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`ISketchManager::AddToDB must be true to use this method's settings`；且**程序结束前必须复位 TRUE**。
**配方一句话**：`AddToDB = True` → `DisplayWhenAdded = False` → 造完 → `GraphicsRedraw` → 两个都复位。

---

### 1.49 `Document`（property）

1. **精确签名**（0 个形参）
   `ModelDoc2 Document {get;}`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.50 `EditCircularSketchStepAndRepeat`（method）

1. **精确签名**（**10 个形参**）
   `System.bool EditCircularSketchStepAndRepeat( System.double ArcRadius, System.double ArcAngle, System.int PatternNum, System.double PatternSpacing, System.bool PatternRotate, System.string DeleteInstances, System.bool RadiusDim, System.bool AngleDim, System.bool CreateNumOfInstancesDim, System.string Seeds )`
2. **Remarks 逐字摘录**：
   > `The radius, angle, and number of instances dimensions displayed in the graphics area can be modified by interactive users.`
3. **官方例子调用序**（CHM 解包 `Create_and_Edit_Circular_Sketch_Pattern_Example_VB.htm`，逐字，含"先选什么"与 `Seeds` 实参）：
   ```vbnet
   boolstatus = swModelDocExt.SelectByID2("Line1@Sketch1", "EXTSKETCHSEGMENT", -0.002390499397973, 0.03694408160504, 0, False, 0, Nothing, 0)
   swModel.EditSketch
   boolstatus = swSketchMgr.EditCircularSketchStepAndRepeat(0.03184378021964, 4.732863934409, 3, 1.570796326795, True, "", True, True, True, "Line2_Line1_Line4_Line3_")
   swModel.ClearSelection2 True
   swSketchMgr.InsertSketch True
   ```
   ★ 第 10 个形参 `Seeds` 的实参是一串下划线结尾的名字列表 `"Line2_Line1_Line4_Line3_"`。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：先 `SelectByID2("Line1@Sketch1","EXTSKETCHSEGMENT",…)`（**mark = 0**）+ `swModel.EditSketch` 进编辑态。
**配方一句话**：比 `CreateCircularSketchStepAndRepeat` 多第 10 个 `Seeds`（字符串）。

---

### 1.51 `EditLinearSketchStepAndRepeat`（method）

1. **精确签名**（**13 个形参**）
   `System.bool EditLinearSketchStepAndRepeat( System.int NumX, System.int NumY, System.double SpacingX, System.double SpacingY, System.double AngleX, System.double AngleY, System.string DeleteInstances, System.bool XSpacingDim, System.bool YSpacingDim, System.bool AngleDim, System.bool CreateNumOfInstancesDimInXDir, System.bool CreateNumOfInstancesDimInYDir, System.string Seeds )`
2. **Remarks 逐字摘录**：
   > `The spacing instances, angle, and number of instances dimensions displayed in the graphics area can be modified by interactive users`（★ 原文句末**无句点**）
3. **官方例子调用序**（CHM 解包 `Create_and_Edit_Linear_Sketch_Pattern_Example_VB.htm`，逐字）：
   ```vbnet
   boolstatus = swSketchMgr.EditLinearSketchStepAndRepeat(3, 2, 0.0254, 0.0254, 0.296705972839, 1.134464013796, "", False, False, False, True, True, "Line2_Line1_Line4_")
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（该页未写；例子片段里未含 `SelectByID2`，前半段与 1.29 同一例子）。
**配方一句话**：第 13 个 `Seeds` 实参形如 `"Line2_Line1_Line4_"`。

---

### 1.52 `EditSketchBlock`（method，块）

1. **精确签名**（**0 个形参**）
   `void EditSketchBlock()`
2. **Remarks 逐字摘录**（★ 前置）：
   > `When done editing the block definition, use [[ISketchManager::EndEditSketchBlock]].`
   > `See [Block Definitions and Block Instances](<../../docs/Programming with the SOLIDWORKS API/Block Definitions and Block Instances.md>) for details.`
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段；CHM 块例子里只见 `MakeSketchBlockFromSelected` / `InsertSketchBlockInstance`）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：编辑完必须配 `EndEditSketchBlock`。
**配方一句话**：**查不到**（无例子）。

---

### 1.53 `EndEditSketchBlock`（method，块）

1. **精确签名**（**1 个形参**）
   `void EndEditSketchBlock( System.bool AcceptChanges )`
2. **Remarks 逐字摘录**（★ 前置）：
   > `Use [[ISketchManager::EditSketchBlock]] to put the block in edit mode.`
   > `See [Block Definitions and Block Instances](<../../docs/Programming with the SOLIDWORKS API/Block Definitions and Block Instances.md>) for details.`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：必须先 `EditSketchBlock` 把块置入编辑模式。
**配方一句话**：**查不到**。

---

### 1.54 `ExplodeSketchBlockInstance`（method，块）

1. **精确签名**（**1 个形参**）
   `void ExplodeSketchBlockInstance( SketchBlockInstance LpSketchBlockInstance )`
   参数释义（逐字）：`- **LpSketchBlockInstance**: [[Block instance]] to explode`
2. **Remarks 逐字摘录**（★ 后果原话）：
   > `If this is the only or last block instance, then: - All sketch entities in the block instances are copied to the owning sketch of the block instance. - Source block definition is destroyed.`
   > `See [Block Definitions and Block Definitions and Block Instances](…) for details.`（★ 原文的 See 行逐字为 `See [Block Definitions and Block Instances](<../../docs/Programming with the SOLIDWORKS API/Block Definitions and Block Instances.md>) for details.`）
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：最后一个块实例被炸开后**源块定义会被销毁**（逐字）。
**配方一句话**：**查不到**。

---

### 1.55 `FullyDefineSketch`（method）

1. **精确签名**（**10 个形参**）
   `System.int FullyDefineSketch( System.bool EntitiesToFullyDefine, System.bool UseRelations, System.int RelationsToApply, System.bool UseDimensions, System.int HorizontalDimScheme, System.object HorizontalDatumDisp, System.int VerticalDimScheme, System.object VerticalDatumDisp, System.int HorizontalDimPlacement, System.int VerticalDimPlacement )`
   参数释义（逐字）：`EntitiesToFullyDefine: True to fully define all entities, false to fully define only the entities selected`；`RelationsToApply: Relations to apply as defined in [[swSketchFullyDefineRelationType_e]]`；`HorizontalDimScheme: - 0 = Chain - 1 = Baseline - 2 = Ordinate`；`HorizontalDatumDisp: Horizontal datum (model edge, model vertex, sketch line, sketch point), or, if Nothing or null, use entity with selection mark = 6`；`VerticalDimScheme: 0 = Chain / 1 = Baseline / 2 = Ordinate`；`HorizontalDimPlacement: - 0 = Above sketch - 1 = Below sketch`；`VerticalDimPlacement: - 0 = Right of sketch - 1 = Left of sketch`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段）。
4. **枚举**：`swSketchFullyDefineRelationType_e`（Bitmask，逐条见第 0 部分）。
5. **废弃链**：**查不到**（它本身是 `ISketch::AutoDimension2` 点名的后继）。
**前置一句话**：★ **mark 规则只在参数释义里**：`HorizontalDatumDisp` / `VerticalDatumDisp` 传 `Nothing/null` 时**用 selection mark = 6 的实体**。
**配方一句话**：**查不到**（无例子）。

---

### 1.56 `GetDynamicMirror`（method）

1. **精确签名**（**0 个形参**）
   `System.bool GetDynamicMirror()`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.57 `GetSketchBlockDefinitionCount`（method，块）

1. **精确签名**（**0 个形参**）
   `System.int GetSketchBlockDefinitionCount()`
2. **Remarks 逐字摘录**（★ 前置）：
   > `Call this method before calling [[ISketchManager::IGetSketchBlockDefinitions]] to get the size of the array for that method.`
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：必须**先调它**再调 `IGetSketchBlockDefinitions` 取数组大小。
**配方一句话**：**查不到**。

---

### 1.58 `GetSketchBlockDefinitions`（method，块）

1. **精确签名**（**0 个形参**）
   `System.object GetSketchBlockDefinitions()`
2. **Remarks 逐字摘录**：
   > `See [Block Definitions and Block Instances](<../../docs/Programming with the SOLIDWORKS API/Block Definitions and Block Instances.md>) for details.`
   （`## Examples` 段列出 `Get_and_Set_Blocks_Data_in_Any_Document_Example_VB.md`、`Get_Block_Definitions_in_Part_or_Assembly_Example_VB.md`、`Get_Block_Information_Example_VB.md`；★ **本轮未逐行抄其代码 → 调用序查不到**。）
3. **官方例子调用序**：**查不到**（同上）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（该页只给了 See 链接）。
**配方一句话**：**查不到**。

---

### 1.59 `ICreateSpline`（method，★ Obsolete）

1. **精确签名**（**2 个形参**）
   `SketchSegment ICreateSpline( System.int PointCount, ref System.double PointData )`
2. **Remarks 逐字摘录**（逐字）：
   > `The PointData array is a set of, at least, two X, Y, Z values. The X value for the start point of the spline is PointData[0], the Y value for the start point is PointData[1], and the Z value for the start point is PointData[2]. The X value for the next point is PointData[3], and so on.`
   > `This method does not work with [[ISketchManager::AddToDB]] or [[ISketchManager::DisplayWhenAdded]]. …`
   > `In 2D sketches, SOLIDWORKS ignores the Z value in PointData.`
   ★ **与 `CreateSpline` 的 Remarks 差一字**：`CreateSpline` 写 `For example, in VBA and VB.NET, the X value …`，`ICreateSpline` **没有** `For example, in VBA and VB.NET,` 这一句。
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISketchManager::ICreateSpline2]].`
**前置一句话**：与 `AddToDB` / `DisplayWhenAdded` 不兼容；2D 忽略 Z。
**配方一句话**：`PointCount` 单独传 + `ref double[]` 扁平数组（`[0]=x0,[1]=y0,[2]=z0,…`）。

---

### 1.60 `ICreateSpline2`（method）

1. **精确签名**（**3 个形参**）
   `SketchSegment ICreateSpline2( System.int PointCount, ref System.double PointData, System.bool SimulateNaturalEnds )`
2. **Remarks 逐字摘录**：与 1.59 **逐字相同**（`The PointData array is a set of, at least, two X, Y, Z values. … In 2D sketches, SOLIDWORKS ignores the Z value in PointData.`）
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行）。
**前置一句话**：与 `AddToDB` / `DisplayWhenAdded` 不兼容。
**配方一句话**：**查不到**（无例子）。

---

### 1.61 `ICreateSplineByEqnParams`（method）

1. **精确签名**（**5 个形参**）
   `SketchSegment ICreateSplineByEqnParams( ref System.int Properties, System.int KnotArrayCount, ref System.double Knots, System.int ControlPointArrayCount, ref System.double ControlPoints )`
2. **Remarks 逐字摘录**：与 1.41 `CreateSplineByEqnParams` **逐字同文**（`The Properties array contains four longs (placed in the first four doubles in the array) …` / `The Knots array contains doubles with (Number of Control Points + Order) elements.` / `Dimension = 2 then each Control Point is an array of 2 doubles ( x, y )` … / `The parameters are provided as three arrays.` / G1 NOTE / `Does not work with AddToDB…`）。
   ★ **签名层面的差别**（逐字）：这里 `Properties` 是 `ref System.int`，且**显式**传 `KnotArrayCount` 与 `ControlPointArrayCount` 两个数组长度形参。
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**（该页无 `Obsolete.` 行）。
**前置一句话**：坐标必须在草图空间；非 G1 会被拒绝、不建。
**配方一句话**：`Properties(ref int)` + `Knots 长度 + ref double[]` + `ControlPoints 长度 + ref double[]`。

---

### 1.62 `ICreateSplinesByEqnParams`（method）

1. **精确签名**（**5 个形参**）
   `EnumSketchSegments ICreateSplinesByEqnParams( ref System.int Properties, System.int KnotArrayCount, ref System.double Knots, System.int ControlPointArrayCount, ref System.double ControlPoints )`
2. **Remarks 逐字摘录**：与 1.61 **逐字同文**（G1 NOTE 那段同样是 `it is rejected and a spline is not created`）。
   ★ 签名层面的差别：返回类型是 `EnumSketchSegments`（可枚举多条）。
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：同上；非 G1 **被拒绝**。
**配方一句话**：**查不到**（无例子）。

---

### 1.63 `IGetSketchBlockDefinitions`（method，块）

1. **精确签名**（**1 个形参**）
   `SketchBlockDefinition IGetSketchBlockDefinitions( System.int BlockDefCount )`
2. **Remarks 逐字摘录**（★ 前置原话）：
   > `Before calling this method, call [[ISketchManager::GetSketchBlockDefinitionCount]] to get the value of BlockDefCount.`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：必须先 `GetSketchBlockDefinitionCount()` 拿到 `BlockDefCount`。
**配方一句话**：**查不到**。

---

### 1.64 `InferenceMode`（property，★ Obsolete）

1. **精确签名**（0 个形参）
   `System.bool InferenceMode {get; set;}`
2. **Remarks 逐字摘录**（逐字表格）：
   > `This property affects sketch entity snapping and inferring constraints to other geometry during creation.`
   > `**Setting inference mode to...**` … `True — Inferencing during sketch operations, subject to other settings that may disable inferencing such as [[ISketchManager::AutoInference]], [[ISketchManager::AddToDB]], and [[IDrawingDoc::StartDrawing]].`
   > `False — Faster sketching without inferencing, similar to SketchManager::AddToDB, except that using this method does not disable undo operations.`
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISldWorks::GetUserPreferenceToggle]] or [[ISldWorks::SetUserPreferenceToggle]] and swUserPreferenceToggle_e.swSketchInference.`
**前置一句话**：会受 `AutoInference` / `AddToDB` / `IDrawingDoc::StartDrawing` 的连带设置影响。
**配方一句话**：改用 `ISldWorks::SetUserPreferenceToggle(swUserPreferenceToggle_e.swSketchInference, …)`。

---

### 1.65 `Insert3DSketch`（method，3D 草图）

1. **精确签名**（**1 个形参**）
   `void Insert3DSketch( System.bool UpdateEditRebuild )`
   参数释义（逐字）：`- **UpdateEditRebuild**: True if you want to edit and rebuild, false if not`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**（CHM 解包，逐字）：
   · `Create_3D_Sketch_Plane_Example_VB.htm`：
     ```vbnet
     swSketchManager.Insert3DSketch True
     ```
   · `C:\swapi\examples\Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md`：
     ```vbnet
     Part.SketchManager.Insert3DSketch True
     ```
   · `C:\swapi\examples\Split_Closed_Sketch_Segment_Example_VB.md` / `Split_Open_Sketch_Segment_Example_VB.md`（收尾）：
     ```vbnet
     swModel.SketchManager.Insert3DSketch True
     ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内为空）。
**配方一句话**：官方例子里它既当"开始 3D 草图"（`Insert3DSketch True` 在造几何之前）也当"结束 3D 草图"（在 `SplitOpenSegment` 之后）。

---

### 1.66 `InsertExplodeLineSketch`（method）

1. **精确签名**（**0 个形参**）
   `System.bool InsertExplodeLineSketch()`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**（CHM 解包 `Insert_Exploded_Line_Sketch_and_Route_Line_Example_VB.htm`，逐字）：
   ```vbnet
   swAssembly.AutoExplode
   swModel.EditRebuild3
   swModel.ViewZoomtofit2
   swSketchMgr.InsertExplodeLineSketch
   boolstatus = swModelDocExt.SelectByID2("", "FACE", -5.55234504082591E-03, 2.71707519863185E-02, 3.37956573349629E-03, False, 0, Nothing, 0)
   Set swFace = swSelMgr.GetSelectedObject6(1, -1)
   Set itemsToConnect(0) = swFace
   boolstatus = swModelDocExt.SelectByID2("", "FACE", 5.81777224675761E-03, 2.11322449790146E-02, 0.127676153954326, True, 0, Nothing, 0)
   Set swFace = swSelMgr.GetSelectedObject6(1, -1)
   Set itemsToConnect(1) = swFace
   itemsReverse(0) = False
   itemsReverse(1) = False
   itemsPath(0) = False
   itemsPath(1) = False
   alongXYZ(0) = False
   alongXYZ(1) = False
   Set swSketch = swModel.GetActiveSketch2
   boolstatus = swSketch.InsertRouteLine((itemsToConnect), itemsReverse, itemsPath, alongXYZ)
   Debug.Print "Route line inserted in explode line sketch? " & boolstatus
   swSketchMgr.InsertExplodeLineSketch
   ```
   ★ **先选什么**：先用 `SelectByID2("", "FACE", x,y,z, …, Mark=0)` 选中要连接的面（逐字：例子用的是**空名字 + 坐标**）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内为空；例子前置是先 `swAssembly.AutoExplode` + `EditRebuild3`）。
**配方一句话**：例子在开头和结尾各调一次 `InsertExplodeLineSketch`（开/关爆炸线草图）。

---

### 1.67 `InsertSketch`（method）

1. **精确签名**（**1 个形参**）
   `void InsertSketch( System.bool UpdateEditRebuild )`
2. **Remarks 逐字摘录**（★ 前置）：
   > `This method does not support drawing documents.`
3. **官方例子调用序**（逐字，被大量例子复用）：
   · `C:\swapi\examples\Create_Equation-driven_Curve_Example_VB.md`：
     ```vbnet
     swModel.SketchManager.InsertSketch True
     Set skSegment = swModel.SketchManager.CreateEquationSpline2("", "sin(x)", "", "0", "6.28", False, 0, 0, 0, True, True)
     swModel.SketchManager.InsertSketch True
     ```
   · `C:\swapi\examples\Create_On-surface_Spline_Example_VB.md`：
     ```vbnet
     Set skSegment = Part.SketchManager.CreateSpline3((pointArray), surfs, Nothing, True, statuses)
     Part.SketchManager.InsertSketch True
     ```
   · `C:\swapi\examples\Get_Spline's_Parameters_Example_VB.md`：
     ```vbnet
     varSeg = swSketchMgr.CreateSplinesByEqnParams2(swSplineParaData)
     swSketchMgr.InsertSketch (True)
     ```
   · CHM `Sketch_Offset_Example_VB.htm`：`swSketchManager.InsertSketch True`（开）… `swSketchManager.InsertSketch True`（关）
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`This method does not support drawing documents`。
**配方一句话**：开头、结尾各一次 `InsertSketch True`（`CreateSpline3` 的 Remarks 明写 `Call ISketchManager::InsertSketch to finalize the sketch.`）。

---

### 1.68 `InsertSketchBlockInstance`（method，块）

1. **精确签名**（**4 个形参**）
   `SketchBlockInstance InsertSketchBlockInstance( SketchBlockDefinition BlockDef, MathPoint Position, System.double Scale, System.double Angle )`
   参数释义（逐字）：`BlockDef: [[Block]] for this block instance`；`Position: [[Position]] of this block instance`；`Scale: Scale for this block instance`；`Angle: Rotation angle for this block instance`
2. **Remarks 逐字摘录**（★ 前置 + 禁忌，逐字）：
   > `This method creates a block definition if the block definition does not exist.`
   > `If the definition exists, then this method uses that block definition to create the block instance. The name of the block instance is the same as the filename of the block file, without the filename extension.`
   > `The block instance is inserted on the current drawing layer.`
   > `**TIP:** If inserting the same sketch block multiple times, do not create the block definition more than once. Instead, use the same block definition for each call to SketchManager::InsertSketchBlockInstance.`
   > `To save a block instance and its definition into a block file (**.sldblk**), use [[ISketchBlockDefinition::Save]].`
   > `This method does not work for drawings opened in view-only mode.`
3. **官方例子调用序**（CHM 解包 `Create_Block_Definition_and_Insert_Block_Instance_Example_VB.htm`，逐字，含"先选什么"）：
   ```vbnet
   swSketchMgr.AddToDB = True
   Set swSkSeg(0) = swSketchMgr.CreateLine(0.008372353756316, 0.207929860362, 0#, 0.05495488122133, 0.207929860362, 0#)
   … (共 6 条线)
   swModel.ClearSelection2 True
   Set swSkNote(0) = swModel.InsertNote("Cell 1")
   …
   Set swSkPt(0) = swSketchMgr.CreatePoint(0.02700536474232, 0.1708856599494, 0#)
   …
   Set swSkSeg(6) = swSketchMgr.CreateCircle(swSkPt(0).X, swSkPt(0).Y, swSkPt(0).Z, 0.03050393605009, 0.169349494074, 0#)
   …
   vSkSeg = swSkSeg
   vSkPt = swSkPt
   vSkNote = swSkNote
   nbrSelObjects = swModelDocExt.MultiSelect2(vSkSeg, True, Nothing)
   nbrSelObjects = swModelDocExt.MultiSelect2(vSkPt, True, Nothing)
   nbrSelObjects = swModelDocExt.MultiSelect2(vSkNote, True, Nothing)
   Set swSketchBlockDef = swSketchMgr.MakeSketchBlockFromSelected(Nothing)
   nPt(0) = 60# / 1000#
   nPt(1) = 60# / 1000#
   nPt(2) = 0#
   vPt = nPt
   Set swMathPoint = swMathUtil.CreatePoint(vPt)
   Set swBlockInst = swSketchMgr.InsertSketchBlockInstance(swSketchBlockDef, swMathPoint, 1, 0)
   swSketchMgr.AddToDB = False
   swModel.GraphicsRedraw2
   ```
   ★ **实参**：`Scale = 1`、`Angle = 0`；`Position` 是 `swMathUtil.CreatePoint(vPt)` 造的 `MathPoint`（`nPt(2) = 0#`）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：必须先 `MultiSelect2(..., True, Nothing)` 选中实体、再 `MakeSketchBlockFromSelected(Nothing)` 拿到 `BlockDef`；同一块**不要重复建定义**。
**配方一句话**：`InsertSketchBlockInstance(swSketchBlockDef, swMathPoint, 1, 0)`。

---

### 1.69 `InsertSketchPicture`（method，★ Obsolete）

1. **精确签名**（**1 个形参**）
   `SketchPicture InsertSketchPicture( System.string FileName )`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：CHM `Flip_Sketch_Picture_Example_VB.htm` 的**前置注释**逐字提到 `Replace image_file in the ISketchManager::InsertSketchPicture parameter with the name of the copied file.`；但**正文调用的是 `InsertSketchPicture2`**（见 1.70）⇒ **本成员的调用序查不到**。
4. **枚举**：签名里无。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISketchManager::InsertSketchPicture2]].`
**前置一句话**：**查不到**。
**配方一句话**：**查不到**（Obsolete，官方例子已改用 `InsertSketchPicture2`）。

---

### 1.70 `InsertSketchPicture2`（method）

1. **精确签名**（**2 个形参**）
   `SketchPicture InsertSketchPicture2( System.string FileName, System.bool HighestResolution )`
   参数释义（逐字）：`FileName: Path to image file including file extension`；`HighestResolution: True to insert images up to 8192 pixels without compression, false to compress images to 2048 pixels before insertion (see **Remarks**)`
2. **Remarks 逐字摘录**：
   > `If the document type is not a drawing, then HighestResolution defaults to false.`
3. **官方例子调用序**（CHM 解包 `Flip_Sketch_Picture_Example_VB.htm`，逐字）：
   ```vbnet
   swModel.SketchManager.InsertSketch True
   Set swSketchPicture = swModel.SketchManager.InsertSketchPicture2("c:\temp\image_file", False)
   swModel.SketchManager.InsertSketch True
   boolstatus = swModel.Extension.SelectByID2("Sketch Picture1", "SKETCHBITMAP", 0, 0, 0, False, 0, Nothing, 0)
   Set swFeat = swSelMgr.GetSelectedObject6(1, -1)
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内只写了"非工程图文档时 `HighestResolution` 默认为 false"）。
**配方一句话**：`InsertSketchPicture2("c:\temp\image_file", False)`，外面要 `InsertSketch True` 包住。

---

### 1.71 `IntersectCurves`（method）

1. **精确签名**（**0 个形参**）
   `void IntersectCurves()`
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

---

### 1.72 `MakeSketchBlockFromFile`（method，块）

1. **精确签名**（**5 个形参**）
   `SketchBlockDefinition MakeSketchBlockFromFile( MathPoint InsertionPoint, System.string FileName, System.bool LinkedToFile, System.double Scale, System.double Angle )`
   参数释义（逐字）：`InsertionPoint: [[Insertion point]], which is a 2D point with z = 0.0, for the block definition`；`FileName: Name of the external file to use to create the block definition`；`LinkedToFile: True to link the block definition to the file, false to not`
2. **Remarks 逐字摘录**：
   > `If the entities of a block are associated with one or more layers and those layers do not already exist in the drawing, then the layers are inserted in the drawing and the associations between the entities of the block and the layers are maintained.`
   > `The block instance is inserted on the current drawing layer.`
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：`InsertionPoint` 必须是 **z = 0.0** 的 2D 点（原文）。
**配方一句话**：**查不到**（无例子）。

---

### 1.73 `MakeSketchBlockFromSelected`（method，块）

1. **精确签名**（**1 个形参**）
   `SketchBlockDefinition MakeSketchBlockFromSelected( MathPoint InsertionPoint )`
   参数释义（逐字）：`InsertionPoint: [[Insertion point]], which is a 2D point with z = 0.0, for the block definition`
2. **Remarks 逐字摘录**：
   > `See [Block Definitions and Block Instances](<../../docs/Programming with the SOLIDWORKS API/Block Definitions and Block Instances.md>) for details.`
3. **官方例子调用序**（CHM 解包 `Create_Block_Definition_and_Insert_Block_Instance_Example_VB.htm`，逐字，含"先选什么"）：
   ```vbnet
   nbrSelObjects = swModelDocExt.MultiSelect2(vSkSeg, True, Nothing)
   nbrSelObjects = swModelDocExt.MultiSelect2(vSkPt, True, Nothing)
   nbrSelObjects = swModelDocExt.MultiSelect2(vSkNote, True, Nothing)
   Set swSketchBlockDef = swSketchMgr.MakeSketchBlockFromSelected(Nothing)
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：必须先 `MultiSelect2(..., True, Nothing)` 把实体放进选区；`InsertionPoint` 官方例子传 **`Nothing`**。
**配方一句话**：`MakeSketchBlockFromSelected(Nothing)`。

---

### 1.74 `MakeSketchBlockFromSketch`（method，块）

1. **精确签名**（**2 个形参**）
   `SketchBlockDefinition MakeSketchBlockFromSketch( MathPoint InsertionPoint, Sketch Sketch )`
   参数释义（逐字）：`InsertionPoint: [[Insertion point]], which is a 2D point with z = 0.0, for the block definition`；`Sketch: [[Sketch]] to use`
2. **Remarks 逐字摘录**：同 1.73 —— `See [Block Definitions and Block Instances](…) for details.`
3. **官方例子调用序**：**查不到**（该页无 `## Examples` 段）。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**（页内只有 See 链接）。
**配方一句话**：**查不到**。

---

### 1.75 `MakeSketchChain`（method）

1. **精确签名**（**0 个形参**）
   `System.bool MakeSketchChain()`
2. **Remarks 逐字摘录**（★ 前置 + 禁忌，逐字）：
   > `This method is not valid: - unless a sketch is in edit mode. - for 3D sketches.`
3. **官方例子调用序**（CHM 解包 `Create_Sketch_Path_Example_VB.htm`，逐字，含"先选什么"）：
   ```vbnet
   bRet = swModel.Extension.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, False, 0, Nothing, 0)
   Set swFeat = swSelMgr.GetSelectedObject6(1, -1)
   Set swSketch = swFeat.GetSpecificFeature2
   swModel.EditSketch
   vSketchSeg = swSketch.GetSketchSegments
   For i = 0 To UBound(vSketchSeg)
       Set swSketchSeg = vSketchSeg(i)
       swSketchSeg.Select4 True, Nothing
   Next
   bRet = swSketchMgr.MakeSketchChain
   swModel.ClearSelection2(True)
   vSketchPath = swSketch.GetSketchPaths
   ```
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：★ `unless a sketch is in edit mode`（例子用 `swModel.EditSketch`）+ ★ `for 3D sketches` **无效**。
**配方一句话**：先把草图段 `Select4 True, Nothing` 选中，再 `MakeSketchChain`。

---

### 1.76 `PerimeterCircle`（method）

1. **精确签名**（**6 个形参**）
   `System.object PerimeterCircle( System.double X1, System.double Y1, System.double X2, System.double Y2, System.double X3, System.double Y3 )`
   参数释义（逐字）：`X1: coordinate for first point`；`Y1: y coordinate for first point`；`X2/Y2: second point`；`X3/Y3: third point`
   ★ **注意**：这一族的形参名是**小写 `x2`/`y2`/`x3`/`y3`**，与本接口其他成员的 `X2/Y2/X3/Y3` 不同（逐字照抄）。
2. **Remarks 逐字摘录**：**空 —— 官方没写。**
3. **官方例子调用序**：**查不到**。
4. **枚举**：签名里无。
5. **废弃链**：**查不到**。
**前置一句话**：**查不到**。
**配方一句话**：**查不到**。

<!--APPEND-HERE-->