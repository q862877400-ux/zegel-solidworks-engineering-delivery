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

<!--APPEND-HERE-->