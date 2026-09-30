# Simulation 载荷/夹具 API 官方签名全表（2026-09-27 提取自官方网页）

> 来源：`help.solidworks.com/2021/english/api/swsimulationapi/`，共 33 个方法页，
> 抓取器 `$env:TEMP\swprobe\grab_api.ps1`，签名提取器 `extract_api_sig.ps1`。
> **参数名是官方原文**，比我此前靠反射猜的可靠。

## 提取方法（可复用）

页面是 Next.js SPA，正文靠 JS 渲染，**但签名以 JSON 转义嵌在 HTML 里**：

```powershell
# 关键：在 HTML 里找  id="ParamName" href="#"  就是官方参数名
[regex]::Matches($html,'id=\\?"(\w+)\\?"\s+href=\\?"#\\?"') | % { $_.Groups[1].Value }
```
（`\u003c`=`<`、`\u0026nbsp;`=空格、`\n`=换行 —— 解转义后才能看清 `ByVal` 上下文）

## 全表

| 方法 | 参数 |
|---|---|
| **AddRestraint** | `NRestraintType, DispArray, RefGeom, ErrorCode` |
| **AddPrescribedDisplacement** | `Displacements, NLengthUnit, DispArray, RefGeom, ErrorCode` |
| **AddCyclicSymmetryRestraint** | `FirstFace, SecondFace, Axis, ErrorCode` |
| **AddForce** | `NForceType, DispArray, RefGeom, ErrorCode` |
| **AddForce2** | `NForceType, NSelectionType, DispArray, RefGeom, ErrorCode` |
| **AddForce3** | `ForceType, SelectionType, RefDirType, InterpolationMode, DistPercentageOpt, NumOfRows, DistValue, ForceValue, NonUniformLoading, NULoadingOnBeam, NonUniformLoadDistDef, NonUniformLoadDistType, Ucode, TorqueNFVal, Comps, FlipOrigin, IsCurvedBeam, DispArray, RefGeom, PerUnitLength, ErrorCode`（21 参，最全） |
| AddPressure | `NPressureType, DispArray, RegGeom, ErrorCode` |
| AddGravity | `DispEntity, ErrorCode` |
| AddCentrifugalForce | `DispEntity, ErrorCode` |
| AddRemoteLoad | `NLoadType, DispArray, NLocationUnits, DXValue, DYValue, DZValue, ErrorCode` |
| AddBearingLoad | `CoordinateSystem, FirstFace, ErrorCode` |
| AddDistributedMass | `DispArray, NUnits, DMass, ErrorCode` |
| AddTemperature / AddHeatFlux / AddHeatPower / AddConvection | `DispArray, ErrorCode` |
| AddRadiation | `NRadType, DispArray, ErrorCode` |
| AddUniformBaseExcitation | `NType, DirectionEntity, NUnits, BDir1, DVal1, BDir2, DVal2, BDir3, DVal3, ErrorCode` |
| AddSelectedBaseExcitation | `NType, SFixtureName, NUnits, BDir1..DVal3, ErrorCode`（★接受**夹具名** `SFixtureName`） |
| AddInitialConditionForDynamicStudy | `NType, NSelectionType, DispArray, RefEntity, NUnits, BDir1..DVal3, ErrorCode` |
| AddRigidConnector | `PersistIDFaceArray, PersistIDTargetArray, ErrorCode` |
| AddLinkConnector | `VertexPointforFirstLocation, VertexPointforSecondLocation, ErrorCode` |
| AddPinConnector | `DispArrayComp1, DispArrayComp2, ErrorCode` |
| AddSpringConnector | `NSpringSubType, DispArrayComp1, DispArrayComp2, ErrorCode` |
| AddElasticConnector | `DispArray, ErrorCode` |
| AddBoltConnector | `NBoltType, DispArrayBoltHead, DispArrayBoltNut, ErrorCode` |
| AddSpotWeldConnector | `FirstFace, SecondFace, DispArrayWeldLocations, ErrorCode` |
| AddEdgeWeldConnector | `FirstFace, SecondFace, Edges, NEdgeWeldStyle, ErrorCode` |
| GetLoadsAndRestraints / GetEdgeWeldConnector | `NIndex, ErrorCode` |
| DeleteLoadsAndRestraints | `SName` |
| CopyLoadsAndRestraintsToStudy | `SStudyName, LRNames` |
| Count | （属性） |

## 关键观察

### ① `AddCyclicSymmetryRestraint` 不接数组，只接两个面
```
AddCyclicSymmetryRestraint(FirstFace, SecondFace, Axis, ErrorCode)
```
⇒ 与 `AddRestraint(type, DispArray, …)` **形状完全不同**。
如果 `AddRestraint` 的失败源于 `DispArray` 数组的封送，这条路径**绕开了数组**。

### ② `AddSelectedBaseExcitation` 接受**夹具名** `SFixtureName`
⇒ 官方确实存在"按名字引用夹具"的用法，与"先建选择集再引用"的思路一致。

### ③ 大量方法只用 `DispArray, ErrorCode`（2 参）
`AddTemperature` / `AddHeatFlux` / `AddHeatPower` / `AddConvection` / `AddElasticConnector`
都是这个形状。⇒ `DispArray` 是通用入参，**失败点确实在数组本身**，不是 `AddRestraint` 特有。

### ④ 同一功能有 1/2/3 代（`AddForce` / `AddForce2` / `AddForce3`）
`AddForce3` 参数最全（21 个），**优先试它**——老版本方法常在内部走已废弃路径。
