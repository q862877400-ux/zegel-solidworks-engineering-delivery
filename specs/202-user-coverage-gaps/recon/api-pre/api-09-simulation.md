# api-09 — 仿真域官方契约抄录（api-pre）

> 抄录员只写「亲手读到」的内容。每条给 **文件名 + 可搜索的原文片段**，**不写行号**。
> 查不到就写「查不到」。不写建议、不下结论。

## 〇 · 本机资料的实际覆盖（先说结论性的事实）

| 要求的资料源 | 实际状态 | 证据 |
|---|---|---|
| `C:\swapi\types\ICW*\` 全族 | **不存在** | `Get-ChildItem 'C:\swapi\types' \| Where-Object Name -clike 'ICW*'` → count = **0**；`C:\swapi\types` 共 566 个接口目录，无一以 `ICW` 开头 |
| `C:\swapi\types\ICosmosWorks\` | **不存在** | `Test-Path 'C:\swapi\types\ICosmosWorks'` → `False` |
| `C:\swapi\enums\sws*`（Simulation 枚举） | **不存在** | `Get-ChildItem 'C:\swapi\enums' \| Where-Object Name -clike 'sws*'` → count = **0**（大小写敏感；先前 `-Filter 'sws*'` 得到的 142 个全是 `swS*`，属 sldworksapi） |
| `C:\swapi\examples\` 里的 Simulation 例子 | **不存在** | `C:\swapi\examples` 内无 Simulation/CosmosWorks 例子文件 |
| CHM `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\` | **存在**，但只有 **1 个接口** | 该目录共 47 个文件；接口页全部是 `ICWLoadsAndRestraintsManager~*.html`，**没有** `ICosmosWorks` / `ICWStudyManager` / `ICWStudy` / `CWMesh` / `ICWResults` 的成员页 |

`C:\swapi` 全库是 **sldworksapi** 一族（`IComponent2` / `IPartDoc` 等）。`grep -i 'ICW|ICosmosWorks|CosmosWorks' C:\swapi`
只命中 3 处非接口内容：`swCosmosWorksMat`（sldworksapi 自己的枚举，**0 属性 0 方法**）、
`IComponent2.SetCosmosWorksMaterial` / `IPartDoc.SetCosmosWorksMaterial`（材料赋值，非仿真域）。

⇒ **本次能抄的完整成员，全部来自 CHM `cosworks\` 的 `ICWLoadsAndRestraintsManager`。**
算例创建 / 网格 / 结果读取的成员页 **查不到**；只有调用序能从两个官方例子页读到（见 §三）。

---

## 一 · `ICWLoadsAndRestraintsManager`（本地有成员页的 33 个）

> 每节的文件名是 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~<成员>.html`。
> ★ **页面上有 Remarks 段的只有 14 个**；其余页面在 Syntax 与 See Also 之间**没有 Remarks 段**（下表逐条标出）。
> ★ 签名一律抄 **Visual Basic (Declaration)** 原样（官方同时给 C# 与 C++/CLI，三者形参个数一致）。

### 1.1 `AddBearingLoad`

- **精确签名**（4 个形参）：
  ```
  Function AddBearingLoad( _
  ByVal CoordinateSystem As System.Object, _
  ByVal FirstFace As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWBearingLoad
  ```
  C#：`CWBearingLoad AddBearingLoad(System.object CoordinateSystem, System.object FirstFace, ref System.int ErrorCode)`
- **## Remarks 逐字摘录**：`"The Z-axis of CoordinateSystem must coincide with the axes of the faces in the FirstFace array."`
- **参数逐字**：`CoordinateSystem` — `"Coordinate system (see Remarks)"`；`FirstFace` — `"Array of cylindrical faces or circular shell edges (see Remarks)"`；`ErrorCode` — `"Error as defined in swsLoadsAndRestraintsManagerBearingLoadError_e"`
- **官方例子**：页面 Example 段列 `Add Bearing Load (VBA)` / `(VB.NET)` / `(C#)`。★ **这三个例子文件本机没有**（`cosworks\` 目录里只有 Analyze_Part 与 Copy_Items 两篇）⇒ 调用序 **查不到**。
- **枚举**：`swsLoadsAndRestraintsManagerBearingLoadError_e`（成员与数值 **查不到**，见 §二）
- **废弃链**：页面无 Obsolete 字样 ⇒ 非 Obsolete。
- **Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：`CoordinateSystem` 的 Z 轴必须与 `FirstFace` 数组里各面的轴线重合。
- **配方一句话**：查不到。

### 1.2 `AddBoltConnector`

- **精确签名**（4 个形参）：
  ```
  Function AddBoltConnector( _
  ByVal NBoltType As System.Integer, _
  ByVal DispArrayBoltHead As System.Object, _
  ByVal DispArrayBoltNut As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWBoltConnector
  ```
  C# 用 `ref System.int ErrorCode`（**不是** `out`）。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`NBoltType` — `"Type of bolt as defined in swsBoltType_e"`；`DispArrayBoltHead` — `"Array of bolt heads"`；`DispArrayBoltNut` — `"Array of bolt nuts"`；`ErrorCode` — `"Error as defined in swsBoltConnectorError_e"`
- **官方例子**：`Create and Edit Bolt and Pin Connectors (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsBoltType_e`、`swsBoltConnectorError_e`（数值 **查不到**）
- **废弃链**：非 Obsolete。
- **Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：查不到（页面没写）。
- **配方一句话**：查不到。

### 1.3 `AddCentrifugalForce`

- **精确签名**（2 个形参）：
  ```
  Function AddCentrifugalForce( _
  ByVal DispEntity As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWCentriFugalForce
  ```
  ★ 返回类型官方拼作 `CWCentriFugalForce`（少一个 `u`），照抄。
- **## Remarks 逐字摘录**：`"The density material property must be specified to consider the effect of centrifugal loads."`
- **参数逐字**：`DispEntity` — `"Reference geometry (axis, edge, or cylindrical face) to specify direction"`；`ErrorCode` — `"Error as defined in swsCentrifugalForceError_e"`
- **官方例子**：`Add Centrifugal Load (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsCentrifugalForceError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：必须先指定材料密度，否则离心载荷不生效。
- **配方一句话**：查不到。

### 1.4 `AddConvection`

- **精确签名**（2 个形参）：
  ```
  Function AddConvection( _
  ByVal DispArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWConvection
  ```
- **## Remarks**：**本页无 Remarks 段。**
- **★ 摘要句（算例类型证据，逐字）**：`"Creates a convection load for thermal studies."`
- **参数逐字**：`DispArray` — `"Array of faces or shell edges to apply convection"`；`ErrorCode` — `"Error as defined in swsConvectionError_e"`
- **官方例子**：`Apply Thermostat-controlled Heat Power for Transient Thermal Study (C#/VB.NET/VBA)` ⇒ 本机 **查不到**。
- **枚举**：`swsConvectionError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：摘要明写该载荷是 **for thermal studies**。
- **配方一句话**：查不到。

### 1.5 `AddCyclicSymmetryRestraint`

- **精确签名**（4 个形参）：
  ```
  Function AddCyclicSymmetryRestraint( _
  ByVal FirstFace As System.Object, _
  ByVal SecondFace As System.Object, _
  ByVal Axis As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWRestraint
  ```
- **## Remarks 逐字摘录**（两段）：
  > `"The cyclic symmetry fixture is appropriate for turbines, fans, flywheels, and motor rotors. FirstFace and SecondFace are the faces of a cut section of a model that can be repeated in a cyclical pattern about Axis. The angle between FirstFace and SecondFace should be evenly divisible by 360. You cannot apply a cyclic symmetry restraint to an invalid section. See the Creating Valid Sections for Cyclic Symmetry topic in the SOLIDWORKS Simulation Helps for more information."`
  >
  > `"This method is valid only for static and nonlinear studies."`
  ★ 第二句是本次抄录里**最直接的「算例类型前置」**。
- **参数逐字**：`FirstFace`/`SecondFace`/`Axis` 三个都标 `(see Remarks)`；`ErrorCode` — `"Error code as defined in swsCyclicRestraintError_e"`
- **官方例子**：`Add Cyclic Symmetry Restraint (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsCyclicRestraintError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2017"`
- **前置一句话**：只对 **static 与 nonlinear** 算例有效，且 FirstFace/SecondFace 夹角须被 360 整除。
- **配方一句话**：查不到。

### 1.6 `AddDistributedMass`

- **精确签名**（4 个形参）：
  ```
  Function AddDistributedMass( _
  ByVal DispArray As System.Object, _
  ByVal NUnits As System.Integer, _
  ByVal DMass As System.Double, _
  ByRef ErrorCode As System.Integer _
  ) As CWDistributedMass
  ```
  C# 用 `ref System.int ErrorCode`。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`DispArray` — `"Array of faces or shell edges on which to distribute the mass"`；`NUnits` — `"Units as defined in swsUnitSystem_e"`；`DMass` — `"Mass to distribute"`；`ErrorCode` — `"Error code as defined in swsDistributedMassError_e"`
- **官方例子**：`Create Linear Dynamic Study (C#/VB.NET/VBA)` ⇒ 本机 **查不到**。
- **枚举**：`swsUnitSystem_e`、`swsDistributedMassError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2012"`
- **前置一句话**：查不到（页面没写）。
- **配方一句话**：查不到。

### 1.7 `AddEdgeWeldConnector`

- **精确签名**（5 个形参）：
  ```
  Function AddEdgeWeldConnector( _
  ByVal FirstFace As System.Object, _
  ByVal SecondFace As System.Object, _
  ByVal Edges As System.Object, _
  ByVal NEdgeWeldStyle As System.Integer, _
  ByRef ErrorCode As System.Integer _
  ) As CWEdgeWeldConnector
  ```
- **## Remarks**：**本页无 Remarks 段。** ★ 但 `SecondFace` 的参数说明里内嵌了一张条件表（逐字）：
  | `If NEdgeWeldStyle = swsEdgeWeldConnectorTypes_e...` | `Then SecondFace array contains faces that are...` |
  |---|---|
  | `swsEdgeWeldConnectorGrooveDoubleSided` / `swsEdgeWeldConnectorGrooveSingleSided` | `Parallel to faces in FirstFace array` |
  | `swsEdgeWeldConnectorFilletDoubleSided` / `swsEdgeWeldConnectorFilletSingleSided` | `Perpendicular to faces in FirstFace array` |
- **参数逐字**：`Edges` — `"Array of touching edges between the faces specified in FirstFace and SecondFace arrays"`；`NEdgeWeldStyle` — `"Edge weld style as defined by swsEdgeWeldConnectorTypes_e"`；`ErrorCode` — `"Error code as defined by swsEdgeWeldCreationErrorCode_e"`
- **官方例子**：`Create and Edit Edge Weld Connector (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **See Also** 里本页多一条同接口引用：`ICWLoadsAndRestraintsManager::GetEdgeWeldConnector Method ()`
- **枚举**：`swsEdgeWeldConnectorTypes_e`（页面已抄出 4 个成员**名**：`…GrooveDoubleSided` / `…GrooveSingleSided` / `…FilletDoubleSided` / `…FilletSingleSided`；**数值查不到**）、`swsEdgeWeldCreationErrorCode_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2015"`
- **前置一句话**：`NEdgeWeldStyle` 决定 `SecondFace` 必须与 `FirstFace` 平行（groove）还是垂直（fillet）。
- **配方一句话**：查不到。

### 1.8 `AddElasticConnector`

- **精确签名**（2 个形参）：
  ```
  Function AddElasticConnector( _
  ByVal DispArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWElasticConnector
  ```
  C# 用 `ref System.int ErrorCode`。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`DispArray` — `"Array of faces for the elastic support fixture"`；`ErrorCode` — `"Error as defined in swsElasticConnectorError_e"`
- **官方例子**：`Add Elastic Support Fixture (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsElasticConnectorError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：查不到（页面没写）。
- **配方一句话**：查不到。

### 1.9 `AddForce`

- **精确签名**（4 个形参）：
  ```
  Function AddForce( _
  ByVal NForceType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal RefGeom As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWForce
  ```
- **★ 废弃标记（逐字，位于标题下第一句）**：`"Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddForce2."`
- **## Remarks 逐字摘录**：`"Pass null in RefGeom if reference geometry is not used."`
- **参数逐字**：`NForceType` — `"Type of force as defined in swsForceType_e"`；`DispArray` — `"Array of entities (faces, edges, vertices, or points) to which to apply force"`；`RefGeom` — `"Reference geometry entity to specify direction (see Remarks)"`；`ErrorCode` — `"Error as defined in swsForceError_e"`
- **官方例子**：**本页 Example 段为空**（只有 See Also）⇒ **查不到**。
- **枚举**：`swsForceType_e`、`swsForceError_e`
- **废弃链**：`AddForce` → **`AddForce2`**（官方点名）。
- **Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：不用参考几何时 `RefGeom` 传 `null`。
- **配方一句话**：查不到（已废弃，官方例子页是空的）。

### 1.10 `AddForce2`

- **精确签名**（5 个形参）：
  ```
  Function AddForce2( _
  ByVal NForceType As System.Integer, _
  ByVal NSelectionType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal RefGeom As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWForce
  ```
- **★ 废弃标记（逐字）**：`"Obsolete. Superseded by ICWloadsAndRestraintsManager::AddForce3."`
  ★ 官方原文里接口名是 **`ICWloadsAndRestraintsManager`**（小写 `l`），与其它页的 `ICWLoadsAndRestraintsManager` 不一致 —— 照抄，不代为修正。
- **## Remarks 逐字摘录**：`"Pass null in RefGeom if reference geometry is not used."`
- **参数逐字**：`NSelectionType` — `"Type of selection as defined in swsSelectionType_e"`；`ErrorCode` — `"Error as defined in swsForceError_e"`
- **官方例子**：本页 Example 段为空 ⇒ **查不到**。
- **枚举**：`swsForceType_e`、`swsSelectionType_e`、`swsForceError_e`
- **废弃链**：`AddForce2` → **`AddForce3`**。
- **Availability**：`"SOLIDWORKS Simulation API 2010"`
- **前置一句话**：不用参考几何时 `RefGeom` 传 `null`。
- **配方一句话**：查不到。

### 1.11 `AddForce3`

- **精确签名**（**21 个形参**，本族最大）：
  ```
  Function AddForce3( _
  ByVal ForceType As System.Integer, _
  ByVal SelectionType As System.Integer, _
  ByVal RefDirType As System.Integer, _
  ByVal InterpolationMode As System.Integer, _
  ByVal DistPercentageOpt As System.Integer, _
  ByVal NumOfRows As System.Integer, _
  ByVal DistValue As System.Object, _
  ByVal ForceValue As System.Object, _
  ByVal NonUniformLoading As System.Boolean, _
  ByVal NULoadingOnBeam As System.Boolean, _
  ByVal NonUniformLoadDistDef As System.Integer, _
  ByVal NonUniformLoadDistType As System.Integer, _
  ByVal Ucode As System.Integer, _
  ByVal TorqueNFVal As System.Double, _
  ByVal Comps As System.Object, _
  ByVal FlipOrigin As System.Boolean, _
  ByVal IsCurvedBeam As System.Boolean, _
  ByVal DispArray As System.Object, _
  ByVal RefGeom As System.Object, _
  ByVal PerUnitLength As System.Boolean, _
  ByRef ErrorCode As System.Integer _
  ) As CWForce
  ```
- **## Remarks**（有 Remarks 段，含一张大表）。开头两句逐字：
  > `"You must specify Comps with a non-empty array of non-zero elements for all ForceTypes. Use Ucode to specify which elements of the Comps array to use for forces in a selected direction."`
  >
  > `"If ForceType = swsForceType_e... || Then... || ..."` 标题下是一张按 `ForceType` / `RefDirType` / 模型类别给出 `Comps` 与 `Ucode` 的表，逐字抄录见下：

  | `If ForceType = swsForceType_e...` | `Then...` | Specify |
  |---|---|---|
  | `swsForceTypeNormal` or `swsForceTypeTorque` | — | `Comps` with an array of six values: `[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]` · `Ucode` with `0` |
  | `swsForceTypeForceOrMoment` | `If RefDirType and RefGeom specify direction reference...` / `And the model is a...` | see next 6 rows |

  | `And the model is a...` | `Then specify Comps with array...` | `And Ucode with...` |
  |---|---|---|
  | `Edge` | `Shell or beam` → `[force_along_edge, moment_along_edge]` | `4` / `32` / `36` to use both |
  | `Edge` | `Solid` → `[force_along_edge]` | `4` |
  | `Face or plane` | `Shell or beam` → `[force_along_plane_dir_1, force_along_plane_dir_2, force_along_normal_to_plane, moment_along_plane_dir_1, moment_along_plane_dir_2, moment_along_normal_to_plane]` | `Combinations of values corresponding to the Comps array components to use` |
  | `Face or plane` | `Solid` → `[force_along_plane_dir_1, force_along_plane_dir_2, force_along_normal_to_plane]` | 同上 |
  | `Axis` | `Shell or beam` → `[force_in_radial_direction, force_in_circumferential_direction, force_along_axis, moment_in_radial_direction, moment_in_circumferential_direction, moment_along_axis]` | 同上 |
  | `Axis` | `Solid` → `[force_in_radial_direction, force_in_circumferential_direction, force_along_axis]` | 同上 |

- **参数逐字（关键的「valid only if」逐条）**：
  - `RefDirType`：原文给的是**裸整数**，不是枚举 —— `"Type of RefGeom to specify direction of this force: 0 = edge / 1 = axis / 2 = face or plane / -1 = no direction reference (see Remarks)"`
  - `NonUniformLoadDistDef` — `"…as defined in swsBeamNonUniformLoadDef_e; valid only if NULoadingOnBeam is true"`
  - `NonUniformLoadDistType` — `"…as defined in swsBeamNonUniformLoadType_e; valid only if NULoadingOnBeam is true"`
  - `Ucode` — 逐字：`1 = Fx / 2 = Fy / 4 = Fz / 8 = Mx / 16 = My / 32 = Mz`，并注 `"For combinations of forces and moments in various directions, add up the corresponding values; use 0 for a normal force"`
  - `TorqueNFVal` — `"Torque or normal force value; valid only if: RefDirType is -1 / ForceType is not swsForceType_e.swsForceTypeForceOrMoment / For beams, valid only for swsBeamNonUniformLoadDef_e.swsTotalLoad or swsBeamNonUniformLoadDef_e.swsCentralLoad"`
  - `RefGeom` — `"Reference direction entity used to indicate the direction of force; valid only if RefDirType is not -1 (see Remarks)"`
  - `PerUnitLength` — `"…valid only if SelectionType is swsSelectionType_e.swsSelectionBeams"`
  - `DistValue` / `ForceValue` — `"…specify an empty array for a non-beam force"`
- **官方例子**：`Apply Loads to Beam (C#/VB.NET/VBA)`、`Apply Table-driven Load to Multiple Beams (C#/VB.NET/VBA)`、`Add Nonuniform Force Distribution (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsForceType_e`、`swsSelectionType_e`、`swsTableDrivenInterpolationType_e`、`swsTableDrivenDistOption_e`、`swsBeamNonUniformLoadDef_e`、`swsBeamNonUniformLoadType_e`、`swsForceError_e`
- **废弃链**：非 Obsolete（本族现行版）。**Availability**：`"SOLIDWORKS Simulation API 2011"`
- **前置一句话**：`Comps` 必须是**非空且非零**的数组，`Ucode` 决定用其中哪几个分量。
- **配方一句话**：查不到。

### 1.12 `AddGravity`

- **精确签名**（2 个形参）：
  ```
  Function AddGravity( _
  ByVal DispEntity As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWGravity
  ```
- **## Remarks 逐字摘录**：`"Mass density must be defined to include the effect of gravity."`
- **参数逐字**：`DispEntity` — `"Reference geometry entity for direction"`；`ErrorCode` — `"Error as defined in swsGravityError_e"`
- **官方例子**：`Add Gravity Load (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsGravityError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：必须先定义质量密度，否则重力不生效。
- **配方一句话**：查不到。

### 1.13 `AddHeatFlux`

- **精确签名**（2 个形参）：
  ```
  Function AddHeatFlux( _
  ByVal DispArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWHeatFlux
  ```
- **## Remarks**：**本页无 Remarks 段。**
- **★ 摘要句（算例类型证据，逐字）**：`"Creates a heat flux load for thermal studies."`
- **参数逐字**：`DispArray` — `"Array of entities (faces or shell edges) to which to apply heat flux"`；`ErrorCode` — `"Error as defined in swsHeatFluxError_e"`
- **官方例子**：`Apply Thermostat-controlled Heat Power for Transient Thermal Study (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsHeatFluxError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008 SP1.0"`
  ★ 注意本条 Availability 与别的成员不同，带 `SP1.0`。
- **前置一句话**：摘要明写 **for thermal studies**。
- **配方一句话**：查不到。

### 1.14 `AddHeatPower`

- **精确签名**（2 个形参）：
  ```
  Function AddHeatPower( _
  ByVal DispArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWHeatPower
  ```
- **★ 摘要句（算例类型证据，逐字）**：`"Creates a heat power load for thermal studies."`
- **## Remarks 逐字摘录**：`"The specified value is applied to each entity."`
- **参数逐字**：`DispArray` — `"Array of entities (bodies, faces, edges, and vertices) to which to apply heat power"`；`ErrorCode` — `"Error as defined in swsHeatPowerError_e"`
- **官方例子**：`Apply Thermostat-controlled Heat Power for Transient Thermal Study (C#/VB.NET/VBA)` ⇒ 本机 **查不到**。
- **枚举**：`swsHeatPowerError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：for **thermal studies**；给定的值会施加到**每一个**实体上。
- **配方一句话**：查不到。

### 1.15 `AddInitialConditionForDynamicStudy`

- **精确签名**（12 个形参）：
  ```
  Function AddInitialConditionForDynamicStudy( _
  ByVal NType As System.Integer, _
  ByVal NSelectionType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal RefEntity As System.Object, _
  ByVal NUnits As System.Integer, _
  ByVal BDir1 As System.Integer, _
  ByVal DVal1 As System.Double, _
  ByVal BDir2 As System.Integer, _
  ByVal DVal2 As System.Double, _
  ByVal BDir3 As System.Integer, _
  ByVal DVal3 As System.Double, _
  ByRef ErrorCode As System.Integer _
  ) As CWDynamicInitialCondition
  ```
- **★ 摘要句（算例类型证据，逐字）**：`"Creates the initial (time = 0) condition for displacements, velocities, or accelerations in modal time history and nonlinear dynamic studies."`
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`NType` — `"Type of dynamic initial condition as defined in swsDynamicInitialConditionType_e"`；`NSelectionType` — `"Type of selection as defined in swsSelectionType_e"`；`RefEntity` — `"Face, edge, or plane reference geometry"`；
  `NUnits` 逐字给了一张表：若 `NType` 为 `swsDynamicInitialConditionType_Displacement` → `swsLinearUnit_e`；为 `swsDynamicInitialConditionType_Velocity` → `swsVelocityUnit_e`；为 `swsDynamicInitialConditionType_Acceleration` → `swsAccelerationUnit_e`。
  `BDir1` — `"1 to set a value along plane direction 1 or along a radial direction, 0 to not; valid only if RefEntity is set to a planar face, reference plane, cylindrical face, or null"`；`BDir2`/`BDir3` 同式（`BDir2` 是 plane direction 2 或 circumferential，`BDir3` 是 normal to the plane 或 along an edge）。
- **官方例子**：`Create Linear Dynamic Time History Study (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsDynamicInitialConditionType_e`、`swsSelectionType_e`、`swsLinearUnit_e`、`swsVelocityUnit_e`、`swsAccelerationUnit_e`、`swsDynamicInitialConditionError_e`
- **★ 废弃链（★ 见 §四「不一致」——此处只抄我读到的两处，**不做调和**）**：
  - 成员页 `SOLIDWORKS.Interop.cosworks~SolidWorks.Interop.cosworks.ICWLoadsAndRestraintsManager_members.html` 的 Methods 表里逐字写：`"AddInitialConditionForDynamicStudy || Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddInitialConditionForDynamicStudy2."`
  - 而本页自身**没有** Obsolete 字样，摘要句是 `Creates the initial (time = 0) condition …`，与成员表里 **2** 版那一行的描述文字相同。
- **Availability**：`"SOLIDWORKS Simulation API 2012"`
- **前置一句话**：只对 **modal time history 与 nonlinear dynamic** 算例；`BDir*` 须由 `RefEntity` 的类型决定。
- **配方一句话**：查不到。

### 1.16 `AddLinkConnector`

- **精确签名**（3 个形参）：
  ```
  Function AddLinkConnector( _
  ByVal VertexPointforFirstLocation As System.Object, _
  ByVal VertexPointforSecondLocation As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWLinkConnector
  ```
  ★ 形参名是官方原拼 `VertexPointforFirstLocation` / `VertexPointforSecondLocation`（小写 `f` 在 `for` 后）。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`VertexPointforFirstLocation` — `"Vertex for first location"`；`VertexPointforSecondLocation` — `"Vertex for second location"`；`ErrorCode` — `"Error as defined in swsLinkConnectorError_e"`
- **官方例子**：本页 Example 段是一句散文，逐字：`"See the ICWLinkConnector examples."` ⇒ 具体例子本机 **查不到**。
- **枚举**：`swsLinkConnectorError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：两个端点都是**顶点**（参数名逐字为 `Vertex…`）。
- **配方一句话**：查不到。

### 1.17 `AddPinConnector`

- **精确签名**（3 个形参）：
  ```
  Function AddPinConnector( _
  ByVal DispArrayComp1 As System.Object, _
  ByVal DispArrayComp2 As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWPinConnector
  ```
  C# 用 `ref System.int ErrorCode`。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**（含两条长约束，逐字）：
  `DispArrayComp1` — `"Array of one full cylindrical face or of multiple cylindrical faces of smaller angles belonging to the same body and coaxial with the same radius"`
  `DispArrayComp2` — `"Array of one full cylindrical face or of multiple cylindrical faces of smaller angles belonging to the same body, but different than the body in DispArrayComp1, and coaxial with the same radius"`
  `ErrorCode` — `"Error as defined in swsPinConnectorError_e"`
- **官方例子**：`Add Pin Connector (VBA/VB.NET/C#)`、`Create and Edit Bolt and Pin Connectors (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsPinConnectorError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：两侧必须是**不同实体**上、**同半径且同轴**的圆柱面。
- **配方一句话**：查不到。

### 1.18 `AddPrescribedDisplacement`

- **精确签名**（5 个形参）：
  ```
  Function AddPrescribedDisplacement( _
  ByVal Displacements As System.Object, _
  ByVal NLengthUnit As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal RefGeom As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWRestraint
  ```
- **## Remarks 逐字摘录**：
  > `"The Displacements parameter specifies:"`
  > `"- length for reference geometry or flat faces"`
  > `"- or -"`
  > `"- angle of rotation for cylindrical or spherical faces"`
- **★ `Displacements` 的数组形状（逐字，参数表原文）**：`"Array: [disp_x_coord, disp_y_coord, disp_z_coord, x_bool, y_bool, z_bool]"`，元素说明逐字：`disp_x_coord` = `Double` / `"Prescribed displacement in the x direction"`；`y_bool` = `"0 or 1"` / `"Whether to use disp_y_coord (1 to use, 0 to not)"`（其余同类）。
- **其余参数逐字**：`NLengthUnit` — `"Units of length as defined in swsLinearUnit_e"`；`RefGeom` — `"Reference entity for prescribed displacement direction"`；`ErrorCode` — `"Error code as defined in swsRestraintError_e"`
- **官方例子**：`Add Prescribed Displacement (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsLinearUnit_e`、`swsRestraintError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2015"`
- **前置一句话**：`Displacements` 是 6 元数组，前 3 个是位移/转角值，后 3 个是 0/1 开关。
- **配方一句话**：查不到。

### 1.19 `AddPressure`

- **精确签名**（4 个形参）：
  ```
  Function AddPressure( _
  ByVal NPressureType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal RegGeom As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWPressure
  ```
  ★ 第三个形参官方拼作 **`RegGeom`**（`Ref` 少一个 `e`）。
- **## Remarks 逐字摘录**：`"Pass null or nothing if reference geometry is not used. If you pass a Dispatch pointer, it is ignored."`
- **参数逐字**：`NPressureType` — `"Pressure type as defined in swsPressureType_e"`；`DispArray` — `"Array of entities (faces or shell edges) to which to apply pressure"`；`RegGeom` — `"Reference geometry for direction"`；`ErrorCode` — `"Error as defined in swsPressureError_e"`
- **★ 官方例子的调用序与实参（逐字，本机有文件）** —— 文件 `Analyze_Part_Example_VB.htm`：
  ```vb
  ' Apply pressure normal to selected face
  Set CWPressure = LBCMgr.AddPressure(0, (varArray2), Nothing, errCode)
  If errCode <> 0 Then ErrorMsg SwApp, "No normal pressure created.", True
  Call CWPressure.PressureBeginEdit
  CWPressure.Unit = 1
  CWPressure.Value = 1000
  errCode = CWPressure.PressureEndEdit
  If errCode <> 0 Then ErrorMsg SwApp, "Nonuniform pressure distribution not set.", True
  ```
  ★ `varArray2` 的构造（同文件逐字）：
  ```vb
  varArray1 = Array(pointer1, pointer2)
  varArray2 = Array(pointer3)
  ```
  ★ `pointer3` 的来源（同文件逐字）：`Set pointer3 = Part.Extension.GetObjectByPersistReference3((var3), longstatus)`
- **枚举**：`swsPressureType_e`、`swsPressureError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：不用参考几何时 `RegGeom` 传 `null`/Nothing，且传 Dispatch 指针会被忽略。
- **配方一句话**：先 `AddPressure(0, 面数组, Nothing, errCode)` 建载荷，再 `PressureBeginEdit` → 写 `Unit`/`Value` → `PressureEndEdit(errCode)` 提交。

### 1.20 `AddRadiation`

- **精确签名**（3 个形参）：
  ```
  Function AddRadiation( _
  ByVal NRadType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWRadiation
  ```
- **★ 摘要句（算例类型证据，逐字）**：`"Creates a radiation load for thermal studies."`
- **## Remarks**：**本页有 Remarks 标题但正文为空**（页面里 `Remarks` 与 `See Also` 相邻，无内容）。
- **参数逐字**：`NRadType` — `"Type of radiation as defined in swsRadiationType_e"`；`DispArray` — `"Array of faces or shell edges to which to apply radiation"`；`ErrorCode` — `"Error as defined in swsRadiationError_e"`
- **官方例子**：`Apply Thermostat-controlled Heat Power for Transient Thermal Study (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsRadiationType_e`、`swsRadiationError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：for **thermal studies**。
- **配方一句话**：查不到。

### 1.21 `AddRemoteLoad`

- **精确签名**（7 个形参）：
  ```
  Function AddRemoteLoad( _
  ByVal NLoadType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal NLocationUnits As System.Integer, _
  ByVal DXValue As System.Double, _
  ByVal DYValue As System.Double, _
  ByVal DZValue As System.Double, _
  ByRef ErrorCode As System.Integer _
  ) As CWRemoteLoad
  ```
- **## Remarks**：**本页无 Remarks 段。**
- **★ `DispArray` 的条件表（逐字，参数说明内嵌）**：

  | `If NLoadType is ...` | `Then DispArray is an array of ...` |
  |---|---|
  | `swsRemoteLoadType_e.swsRemoteLoadType_RigidLoadOrMass` 或 `swsRemoteLoadType_e.swsRemoteLoadType_RigidDisplacement` | `Faces, edges, or vertices` |
  | `swsRemoteLoadType_e.swsRemoteLoadType_DirectLoad` 或 `swsRemoteLoadType_e.swsRemoteLoadType_DirectDisplacement` | `Faces` |

- **其余参数逐字**：`NLocationUnits` — `"Units as defined in swsLinearUnit_e"`；`DXValue`/`DYValue`/`DZValue` — `"X-/Y-/Z-coordinate of the point of application of the remote load"`；`ErrorCode` — `"Error code as defined in swsLoadsAndRestraintsError_e"`
- **官方例子**：`Add Remote Load (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsRemoteLoadType_e`、`swsLinearUnit_e`、`swsLoadsAndRestraintsError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2012"`
- **前置一句话**：`NLoadType` 是 rigid 还是 direct，决定 `DispArray` 能放面还是只能放面/边/点。
- **配方一句话**：查不到。

### 1.22 `AddRestraint`

- **精确签名**（4 个形参）：
  ```
  Function AddRestraint( _
  ByVal NRestraintType As System.Integer, _
  ByVal DispArray As System.Object, _
  ByVal RefGeom As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWRestraint
  ```
- **## Remarks**：**本页无 Remarks 段。** ★ 但 `RefGeom` 的参数说明里逐字写了条件：`"Reference geometry entity for direction; valid only if NRestraintType is set to swsRestraintType_e.swsRestraintTypeReferenceGeometry"`
- **参数逐字**：`NRestraintType` — `"Type of restraint as defined in swsRestraintType_e"`；`DispArray` — `"Array of entities to which to apply the restraint"`；`ErrorCode` — `"Error code as defined in swsRestraintError_e"`
- **★ 官方例子的调用序与实参（逐字，本机有文件）** —— 文件 `Analyze_Part_Example_VB.htm`：
  ```vb
  ' Add fixed restraint
  Set LBCMgr = Study.LoadsAndRestraintsManager
  If LBCMgr Is Nothing Then ErrorMsg SwApp, "No loads and restraints manager.", False
  Set CWRes1 = LBCMgr.AddRestraint(0, (varArray1), Nothing, errCode)
  If errCode <> 0 Then ErrorMsg SwApp, "No fixed restraint created.", True
  ```
  ★ 实参取值逐字：`NRestraintType = 0`，`RefGeom = Nothing`，`varArray1 = Array(pointer1, pointer2)`（两个约束面）。
- **枚举**：`swsRestraintType_e`、`swsRestraintError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：只有当 `NRestraintType = swsRestraintTypeReferenceGeometry` 时 `RefGeom` 才被使用。
- **配方一句话**：`LBCMgr.AddRestraint(0, Array(面1, 面2), Nothing, errCode)` —— 官方例子里固定约束就是传 `0` + 面数组 + `Nothing`。

### 1.23 `AddRigidConnector`

- **精确签名**（3 个形参）：
  ```
  Function AddRigidConnector( _
  ByVal PersistIDFaceArray As System.Object, _
  ByVal PersistIDTargetArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWRigidConnector
  ```
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`PersistIDFaceArray` — `"Array of objects of the faces from a solid body"`；`PersistIDTargetArray` — `"Array of objects of the faces from the target solid body"`；`ErrorCode` — `"Error as defined in swsRigidConnectorError_e"`
- **官方例子**：`Add Rigid Connector (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsRigidConnectorError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：查不到（页面没写）。
- **配方一句话**：查不到。

### 1.24 `AddSelectedBaseExcitation`

- **精确签名**（10 个形参）：
  ```
  Function AddSelectedBaseExcitation( _
  ByVal NType As System.Integer, _
  ByVal SFixtureName As System.String, _
  ByVal NUnits As System.Integer, _
  ByVal BDir1 As System.Integer, _
  ByVal DVal1 As System.Double, _
  ByVal BDir2 As System.Integer, _
  ByVal DVal2 As System.Double, _
  ByVal BDir3 As System.Integer, _
  ByVal DVal3 As System.Double, _
  ByRef ErrorCode As System.Integer _
  ) As CWBaseExcitation
  ```
  ★ 形参名 `SFixtureName` 是官方原拼（大写 `S` 前缀）。
- **★ 摘要句（算例类型证据，逐字）**：`"Applies a base excitation to the specified restraint along the specified directions for dynamic studies."`
- **## Remarks 逐字摘录**（两句）：
  > `"Set negative values in DVal1, DVal2, and DVal3 to indicate reverse directions."`
  > `"If this is a random vibration dynamic study, then DVal1, DVal2, and DVal3 are the Power Spectral Densities of the specified NType."`
- **参数逐字**：`SFixtureName` — `"Model entity to which the restraint is applied"`；`NUnits` 表：`…Displacement → swsLinearUnit_e`、`…Velocity → swsVelocityUnit_e`、`…Acceleration → swsAccelerationUnit_e`；`BDir1/2/3` — `"1 to add excitation along plane direction 1 / 2 / along normal to plane, 0 to not"`；`ErrorCode` — `"Error code as defined in swsRestraintError_e"`
- **官方例子**：本页 **没有 Example 段**（直接跳到 Remarks）⇒ **查不到**。
- **See Also** 多出两条：`ICWLoadsAndRestraintsManager::AddUniformBaseExcitation Method`、`ICWBaseExcitation Interface`
- **枚举**：`swsBaseExcitationType_e`、`swsLinearUnit_e`、`swsVelocityUnit_e`、`swsAccelerationUnit_e`、`swsRestraintError_e`
- **★ 废弃链（★ 见 §四「不一致」——只抄两处，不做调和）**：
  - 成员页逐字：`"AddSelectedBaseExcitation || Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddSelectedBaseExcitation2."`
  - 本页自身**无** Obsolete 字样，摘要句与成员表里 **2** 版的描述相同。
- **Availability**：`"SOLIDWORKS Simulation API 2012"`
- **前置一句话**：for **dynamic studies**；`DVal*` 取负号表示反向，随机振动算例下它们是 Power Spectral Density。
- **配方一句话**：查不到。

### 1.25 `AddSpotWeldConnector`

- **精确签名**（4 个形参）：
  ```
  Function AddSpotWeldConnector( _
  ByVal FirstFace As System.Object, _
  ByVal SecondFace As System.Object, _
  ByVal DispArrayWeldLocations As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWSpotWeldConnector
  ```
  C# 用 `ref System.int ErrorCode`。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`FirstFace` — `"Face of a shell or solid body"`；`SecondFace` — `"Face of a shell or solid body that belongs to a different body than FirstFace"`；`DispArrayWeldLocations` — `"Array of vertices or an array of reference points to project on the faces to determine the locations of the spot welds"`；`ErrorCode` — `"Error as defined in swsSpotWeldConnectorError_e"`
- **官方例子**：`Add Spot Weld Connector (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsSpotWeldConnectorError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：两个面必须属于**不同的实体**。
- **配方一句话**：查不到。

### 1.26 `AddSpringConnector`

- **精确签名**（4 个形参）：
  ```
  Function AddSpringConnector( _
  ByVal NSpringSubType As System.Integer, _
  ByVal DispArrayComp1 As System.Object, _
  ByVal DispArrayComp2 As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWSpringConnector
  ```
  C# 用 `ref System.int ErrorCode`。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`NSpringSubType` — `"Spring connector type as defined in swsSpringConnectorType_e"`；`DispArrayComp1` — `"Array of planar faces, cylindrical faces, or vertices from a body depending on NSpringSubType"`；`DispArrayComp2` — `"Array of planar faces, cylindrical faces, or vertices, depending on NSpringSubType, from another body"`；`ErrorCode` — `"Error as defined in swsSpringConnectorError_e"`
- **官方例子**：`Add Spring Connector (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsSpringConnectorType_e`、`swsSpringConnectorError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2009"`
- **前置一句话**：两侧实体必须是「另一个实体」，且实体种类由 `NSpringSubType` 决定。
- **配方一句话**：查不到。

### 1.27 `AddTemperature`

- **精确签名**（2 个形参）：
  ```
  Function AddTemperature( _
  ByVal DispArray As System.Object, _
  ByRef ErrorCode As System.Integer _
  ) As CWTemperature
  ```
- **★ 摘要句（算例类型证据，逐字）**：`"Creates a temperature load for thermal studies."`
- **## Remarks 逐字摘录**：★ 本族**唯一**把允许的算例类型完整列出来的成员 —— `"Temperature can be used with static, nonlinear, frequency, buckling, and thermal studies."`
- **参数逐字**：`DispArray` — `"Array of entities (faces, edges, and vertices) to which to apply temperature"`；`ErrorCode` — `"Error as defined in swsTemperatureError_e"`
- **官方例子**：`Apply Thermostat-controlled Heat Power for Transient Thermal Study (C#/VB.NET/VBA)` ⇒ 本机 **查不到**。
- **枚举**：`swsTemperatureError_e`
- **废弃链**：非 Obsolete。**Availability**（逐字，含官方拼写错误）：`"SOLIDWORKS Simuluation API 200"`
  ★ 官方原文把 `Simulation` 拼成 `Simuluation`，且年份写作 `200`（非 `2008`）—— 照抄，不代为修正。
- **前置一句话**：可用于 **static、nonlinear、frequency、buckling、thermal** 五类算例。
- **配方一句话**：查不到。

### 1.28 `AddUniformBaseExcitation`

- **精确签名**（10 个形参）：
  ```
  Function AddUniformBaseExcitation( _
  ByVal NType As System.Integer, _
  ByVal DirectionEntity As System.Object, _
  ByVal NUnits As System.Integer, _
  ByVal BDir1 As System.Integer, _
  ByVal DVal1 As System.Double, _
  ByVal BDir2 As System.Integer, _
  ByVal DVal2 As System.Double, _
  ByVal BDir3 As System.Integer, _
  ByVal DVal3 As System.Double, _
  ByRef ErrorCode As System.Integer _
  ) As CWBaseExcitation
  ```
- **★ 摘要句（算例类型证据，逐字）**：`"Adds a uniform base excitation to all locations restrained in the specified directions for dynamic studies."`
- **## Remarks 逐字摘录**（两句，与 `AddSelectedBaseExcitation` 同文）：
  > `"Set negative values in DVal1, DVal2, and DVal3 to indicate reverse directions."`
  > `"If this is a random vibration dynamic study, then DVal1, DVal2, and DVal3 are the Power Spectral Densities of the specified NType."`
- **参数逐字**：`DirectionEntity` — `"Face, edge, or plane of direction for the excitation; null for global direction if Response Spectrum study"` ★（该句是本族里对**算例类型**的第三处明写：Response Spectrum）；
  `BDir1` — `"1 to add excitation along plane direction 1, 0 to not; valid only if DirectionEntity is a face, plane, or unspecified"`；`BDir3` — `"…along an edge…; valid only if DirectionEntity is a face, edge plane, or unspecified"`；
  `DVal1` — `"…valid only if BDir1 = 1 and DirectionEntity is a face, plane, or unspecified (see Remarks)"`；`ErrorCode` — `"Error code as defined in swsRestraintError_e"`
- **官方例子**：`Create Linear Dynamic Study (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **See Also** 多出：`ICWLoadsAndRestraintsManager::AddSelectedBaseExcitation Method`、`ICWBaseExcitation Interface`
- **枚举**：`swsBaseExcitationType_e`、`swsLinearUnit_e`、`swsVelocityUnit_e`、`swsAccelerationUnit_e`、`swsRestraintError_e`
- **★ 废弃链（★ 见 §四「不一致」——只抄两处，不做调和）**：
  - 成员页逐字：`"AddUniformBaseExcitation || Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddUniformBaseExcitation2."`
  - 本页自身**无** Obsolete 字样，摘要句与成员表里 **2** 版的描述相同。
- **Availability**：`"SOLIDWORKS Simulation API 2012"`
- **前置一句话**：for **dynamic studies**；`DirectionEntity` 传 `null` 时是全局方向，且**只**对 Response Spectrum 算例这么写。
- **配方一句话**：查不到。

### 1.29 `CopyLoadsAndRestraintsToStudy`

- **精确签名**（2 个形参）：
  ```
  Function CopyLoadsAndRestraintsToStudy( _
  ByVal SStudyName As System.String, _
  ByVal LRNames As System.Object _
  ) As System.Integer
  ```
  ★ 返回 `System.Integer`（错误码），不是对象。
- **## Remarks 逐字摘录**：
  > `"To populate the array of LRNames, either:"` / `"inspect the Simulation study tree."` / `"- or -"` /
  > `"call ICWLoadsAndRestraintsManager::GetLoadsAndRestraints to get each ICWLoadsAndRestraints and then call ICWLoadsAndRestraints::Name to get the name of each load or restraint."` /
  > `"If a load or restraint name already exists, Copy[1] is prepended to the name of the copied load or restraint."`
- **参数逐字**：`SStudyName` — `"Name of study to which to copy loads and restraints"`；`LRNames` — `"Array of names of loads and restraints to copy (see Remarks)"`
- **★ 官方例子的调用序与实参（逐字，本机有文件）** —— 文件 `Copy_Items_to_Another_Study_Example_VB.htm`：
  ```vb
  ' Create array of names of fixtures to copy
  Set lrMngr = Study.LoadsAndRestraintsManager
  For i = 0 To (lrMngr.Count - 1)
      Set Fixture = lrMngr.GetLoadsAndRestraints(i, errCode)
      fixtures(i) = Fixture.Name
  Next
  ' Copy fixtures and contact sets from Ready study to Partial study
  errCode = ContactMgr.CopyContactsToStudy("Partial", contactSets)
  errCode = lrMngr.CopyLoadsAndRestraintsToStudy("Partial", fixtures)
  ```
  ★ 实参取值逐字：目标算例名是字符串 `"Partial"`；名字数组由 `Count` 循环 + `GetLoadsAndRestraints(i, errCode)` + `.Name` 拼出来。
- **枚举**：返回码 `"Error code as defined in swsCopyItemsError_e"`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2016"`
- **前置一句话**：`LRNames` 必须先由 `GetLoadsAndRestraints` + `.Name` 填好；重名时官方会加前缀 `Copy[1]`。
- **配方一句话**：`CopyLoadsAndRestraintsToStudy("<目标算例名>", Array(载荷/约束名…))`。

### 1.30 `Count`（属性，非方法）

- **精确签名**（**0 个形参**；官方标注为 ReadOnly 属性）：
  ```
  ReadOnly Property Count As System.Integer
  ```
  C#：`System.int Count {get;}`
- **## Remarks 逐字摘录**：`"Call this method before calling ICWLoadsAndRestraintsManager::GetLoadsAndRestraints."`
  ★ 官方把它称作 "this method"，但签名是属性。
- **参数/返回值逐字**：`Property Value` — `"Number of loads and restraints"`
- **官方例子**：`Copy Items to Another Study (VBA/VB.NET/C#)` ⇒ 调用序见 §1.29（`For i = 0 To (lrMngr.Count - 1)`）。
- **枚举**：无。
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：★ 官方明确要求 **先取 `Count` 再调 `GetLoadsAndRestraints`**（`GetLoadsAndRestraints` 页也重复了这条）。
- **配方一句话**：`For i = 0 To (lrMngr.Count - 1)` —— 官方例子按 `Count` 递减循环取全部。

### 1.31 `DeleteLoadsAndRestraints`

- **精确签名**（1 个形参）：
  ```
  Sub DeleteLoadsAndRestraints( _
  ByVal SName As System.String _
  )
  ```
  C#：`void DeleteLoadsAndRestraints(System.string SName)` —— 返回 `void`，**没有** `ErrorCode`。
- **## Remarks**：**本页无 Remarks 段。**
- **参数逐字**：`SName` — `"Name of the restraint or load object to delete"`
- **官方例子**：本页**没有 Example 段** ⇒ **查不到**。
- **枚举**：无。
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：只按**名字**删，本接口不提供按索引删。
- **配方一句话**：查不到。

### 1.32 `GetEdgeWeldConnector`

- **精确签名**（2 个形参）：
  ```
  Function GetEdgeWeldConnector( _
  ByVal NIndex As System.Integer, _
  ByRef ErrorCode As System.Integer _
  ) As CWEdgeWeldConnector
  ```
- **## Remarks 逐字摘录**：
  > `"Call ICWLoadsAndRestraintsManager::Count to determine NIndex. The vertical position of a load or restraint in the Simulation Study tree does not correspond to NIndex. You must use ICWLoadsAndRestraintsManager::GetLoadsAndRestraints to determine the mapping between NIndex and the study's loads and restraints."`
- **参数逐字**：`NIndex` — `"Index of the edge weld connector to get (see Remarks)"`；`ErrorCode` — `"Error code as defined by swsEdgeWeldCreationErrorCode_e"`
- **官方例子**：`Create and Edit Edge Weld Connector (VBA/VB.NET/C#)` ⇒ 本机 **查不到**。
- **枚举**：`swsEdgeWeldCreationErrorCode_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2015"`
- **前置一句话**：★ `NIndex` **与算例树里的纵向位置不对应**，必须靠 `Count` + `GetLoadsAndRestraints` 建立映射。
- **配方一句话**：查不到。

### 1.33 `GetLoadsAndRestraints`

- **精确签名**（2 个形参）：
  ```
  Function GetLoadsAndRestraints( _
  ByVal NIndex As System.Integer, _
  ByRef ErrorCode As System.Integer _
  ) As CWLoadsAndRestraints
  ```
- **## Remarks 逐字摘录**（三段）：
  > `"Before calling this method, call ICWLoadsAndRestraintsManager::Count to get a valid value for NIndex. NIndex does not correspond to the vertical position of the load or restraint in the Simulation Study tree."`
  > `"Cast the return object to the load or restraint class of interest (e.g., CWPinConnector in the example)."`
- **参数逐字**：`NIndex` — `"0-based index of load or restraint to get"`；`ErrorCode` — `"Error as defined in swsLoadsAndRestraintsError_e"`
- **官方例子**：`Create and Edit Bolt and Pin Connectors (VBA/VB.NET/C#)` ⇒ 页面举例说返回对象可转成 `CWPinConnector`。调用序见 §1.29 / §三（`Set Fixture = lrMngr.GetLoadsAndRestraints(i, errCode)`）。
- **枚举**：`swsLoadsAndRestraintsError_e`
- **废弃链**：非 Obsolete。**Availability**：`"SOLIDWORKS Simulation API 2008"`
- **前置一句话**：★ 先 `Count` 再用 0 基索引；返回的是基类 `CWLoadsAndRestraints`，要转成具体子类。
- **配方一句话**：`Set Fixture = lrMngr.GetLoadsAndRestraints(i, errCode)` 后取 `Fixture.Name`。

---

## 二 · 枚举：**全部查不到**

签名里出现的 Simulation 枚举，其**名称**在成员页上逐字可抄（见各节「枚举」行），但**成员与数值**在本机任何源里都查不到：

- `C:\swapi\enums\` 里 `sws*`（大小写敏感）**文件数 = 0**；该目录 963 个枚举文件全部属 sldworksapi 一族。
- `sldworksapi` 自己的 `swSimulationForceType_e` / `swSimulationForceActionType_e` / `swSimulationGravityAxisName_e` / `swSimulationDamperType_e` / `swSimulationMotorType_e` / `swSimulationSpringType_e` 等属 **Motion（运动分析）**，不是 Simulation 仿真域 —— 名字相近，不当作同一枚举。

本次抄到的**唯一**带数值的枚举片段来自 `AddForce3` 的 `Ucode` 参数（逐字）：
`1 = Fx` · `2 = Fy` · `4 = Fz` · `8 = Mx` · `16 = My` · `32 = Mz`

以及 `AddForce3` 的 `RefDirType`（**不是**枚举，官方给的是裸整数）：
`0 = edge` · `1 = axis` · `2 = face or plane` · `-1 = no direction reference`

---

## 三 · 官方例子的调用序（本机只有 2 篇，见 §三）

`cosworks\` 目录里的例子文件只有：`Analyze_Part_Example_VB.htm`、`Analyze_Part_Example_VBNET.txt`、
`Copy_Items_to_Another_Study_Example_VB.htm`。其余成员页引用的例子页 **本机没有**。

### 3.1 `Analyze_Part_Example_VB.htm` — 算例创建 / 材料 / 载荷 / 网格 / 求解 / 结果读取

调用序逐字（去掉选择集的 PID 长串，保留调用行与实参）：

```vb
' Connect to SolidWorks
If SwApp Is Nothing Then Set SwApp = Application.SldWorks
Set Part = SwApp.OpenDoc6("...Tutor1.SLDPRT ", swDocPART, 1, "", longstatus, longwarnings)

'Get SolidWorks Simulation object
Set CWObject = SwApp.GetAddInObject("SldWorks.Simulation")
If CWObject Is Nothing Then ErrorMsg SwApp, "CWObject object not found.", True
Set COSMOSWORKS = CWObject.COSMOSWORKS
If COSMOSWORKS Is Nothing Then ErrorMsg SwApp, "CWObject not found.", True

' Get active document
Set ActDoc = COSMOSWORKS.ActiveDoc()
If ActDoc Is Nothing Then ErrorMsg SwApp, "No active document.", True

' Add default static study results plot
errCode = ActDoc.AddDefaultStaticStudyPlot(swsStaticResultElementalStrain, swsStaticElementalStrain_ENERGY)

' Create new static study
Set StudyMngr = ActDoc.StudyManager()
If StudyMngr Is Nothing Then ErrorMsg SwApp, "StudyMngr object not there.", True
Set Study = StudyMngr.CreateNewStudy3("Static_solid", swsAnalysisStudyTypeStatic, swsMeshTypeSolid, errCode)
If Study Is Nothing Then ErrorMsg SwApp, "Study not created.", True

' Set material from the SolidWorks material library
Set SolidMgr = Study.SolidManager
Set SolidComponent = SolidMgr.GetComponentAt(0, errCode)
Set SolidBody = SolidComponent.GetSolidBodyAt(0, errCode)
bApp = SolidBody.SetLibraryMaterial("...sldmaterials\solidworks materials.sldmat", "Ductile Iron (SN)")
If bApp = False Then ErrorMsg SwApp, "No material applied.", True
Set CWMat = SolidBody.GetDefaultMaterial
NSource = CWMat.Source
```

★ **`CreateNewStudy3` 的实参配方**（逐字）：`"Static_solid"`（算例名）、`swsAnalysisStudyTypeStatic`（算例类型）、`swsMeshTypeSolid`（网格类型）、`errCode`（出参）。

面的取法（逐字）：`Set pointer1 = Part.Extension.GetObjectByPersistReference3((var1), longstatus)`，
其中 `var1` 由 `StringtoArray` 把 `"…逗号分隔的 PID…,Type=1"` 串拆成 Byte 数组。

载荷 / 网格 / 求解 / 结果（逐字）：

```vb
varArray1 = Array(pointer1, pointer2)
varArray2 = Array(pointer3)

Set LBCMgr = Study.LoadsAndRestraintsManager
Set CWRes1 = LBCMgr.AddRestraint(0, (varArray1), Nothing, errCode)
Set CWPressure = LBCMgr.AddPressure(0, (varArray2), Nothing, errCode)
Call CWPressure.PressureBeginEdit
CWPressure.Unit = 1
CWPressure.Value = 1000
errCode = CWPressure.PressureEndEdit

' Create mesh
Set CwMesh = Study.Mesh
If CwMesh Is Nothing Then ErrorMsg SwApp, "No mesh object.", False
CwMesh.Quality = 1
Call CwMesh.GetDefaultElementSizeAndTolerance(0, el, tl)
errCode = Study.CreateMesh(0, el, tl)
If errCode <> 0 Then ErrorMsg SwApp, "Mesh failed.", True

'Run analysis
errCode = Study.RunAnalysis
If errCode <> 0 Then ErrorMsg SwApp, "Analysis failed.", True
Set CWResult = Study.Results
If CWResult Is Nothing Then ErrorMsg SwApp, "No result object.", False
stress = CWResult.GetMinMaxStress(0, 0, 1, Nothing, 0, errCode)

For Each selEntity In CWResult.GetStrainForEntities3(True, swsStrainComponent_e.swsStrainComponentESTRN, 1, Nothing, (entity), status, 0, False, errCode)
For Each selEntity In CWResult.GetStressForEntities3(True, swsStressComponent_e.swsStressComponentVON, 1, Nothing, (entity), swsStrengthUnitPascal, status, 0, False, errCode)

Study.ShowOrHideFixtures = False
Study.ShowOrHideForce = False
```

★ 这些调用出现在例子里，但**对应的成员页本机没有** ⇒ 签名 **查不到**，只有调用序与实参：

| 例子里出现的调用 | 实参 | 成员页 |
|---|---|---|
| `SwApp.GetAddInObject("SldWorks.Simulation")` | 加载项名 `SldWorks.Simulation` | 查不到 |
| `CWObject.COSMOSWORKS` | — | 查不到 |
| `COSMOSWORKS.ActiveDoc()` | — | 查不到 |
| `ActDoc.AddDefaultStaticStudyPlot(...)` | `swsStaticResultElementalStrain, swsStaticElementalStrain_ENERGY` | 查不到 |
| `ActDoc.StudyManager()` | — | 查不到 |
| `StudyMngr.CreateNewStudy3(name, type, meshType, errCode)` | `"Static_solid", swsAnalysisStudyTypeStatic, swsMeshTypeSolid, errCode` | 查不到 |
| `Study.SolidManager` / `.GetComponentAt(0, errCode)` / `.GetSolidBodyAt(0, errCode)` | — | 查不到 |
| `Study.Mesh` / `.Quality` / `.GetDefaultElementSizeAndTolerance(0, el, tl)` | `Quality = 1` | 查不到 |
| `Study.CreateMesh(0, el, tl)` | 单位 `0`、单元尺寸 `el`、容差 `tl` | 查不到 |
| `Study.RunAnalysis` | — | 查不到 |
| `Study.Results` | — | 查不到 |
| `CWResult.GetMinMaxStress(0, 0, 1, Nothing, 0, errCode)` | — | 查不到 |
| `CWResult.GetStrainForEntities3(True, swsStrainComponent_e.swsStrainComponentESTRN, 1, Nothing, (entity), status, 0, False, errCode)` | 9 个实参 | 查不到 |
| `CWResult.GetStressForEntities3(True, swsStressComponent_e.swsStressComponentVON, 1, Nothing, (entity), swsStrengthUnitPascal, status, 0, False, errCode)` | 10 个实参 | 查不到 |
| `Study.ShowOrHideFixtures` / `Study.ShowOrHideForce` | `True` / `False` | 查不到 |

### 3.2 `Copy_Items_to_Another_Study_Example_VB.htm` — 多算例切换 + 网格 + 求解

```vb
Set swApp = Application.SldWorks
Set COSMOSObject = swApp.GetAddInObject("SldWorks.Simulation")
Set COSMOSWORKS = COSMOSObject.COSMOSWORKS
swApp.OpenDoc6 fileName, swDocumentTypes_e.swDocASSEMBLY, swOpenDocOptions_Silent, "", errors, warnings
Set ActDoc = COSMOSWORKS.ActiveDoc()
Set StudyMngr = ActDoc.StudyManager()
Set Study = StudyMngr.GetStudy(0)
StudyMngr.ActiveStudy = 0
If (Study.Name <> "Ready") Then ErrorMsg swApp, "Wrong study"

Set ContactMgr = Study.ContactManager
For i = 0 To (ContactMgr.ContactSetCount - 1)
    Set ContactSet = ContactMgr.GetContactSetAt(i)
    contactSets(i) = ContactSet.ContactName
Next

Set lrMngr = Study.LoadsAndRestraintsManager
For i = 0 To (lrMngr.Count - 1)
    Set Fixture = lrMngr.GetLoadsAndRestraints(i, errCode)
    fixtures(i) = Fixture.Name
Next
errCode = ContactMgr.CopyContactsToStudy("Partial", contactSets)
errCode = lrMngr.CopyLoadsAndRestraintsToStudy("Partial", fixtures)

Set Study = StudyMngr.GetStudy(1)
StudyMngr.ActiveStudy = 1
Set CwMesh = Study.Mesh
CwMesh.MesherType = swsMesherTypeAlternate
CwMesh.GrowthRatio = 1.6
CwMesh.MinElementsInCircle = 8
errCode = Study.CreateMesh(swsLinearUnitMillimeters, 20, 1)
If errCode <> 0 Then ErrorMsg swApp, "Mesh failed with error code as defined in swsStudyMeshError_e: " & errCode
errCode = Study.RunAnalysis
If errCode <> 0 Then ErrorMsg swApp, "Analysis failed with error code as defined in swsRunAnalysisError_e: " & errCode
```

★ 例子注释头逐字：`" 2. Copies fixtures and contact sets from Ready to Partial. 3. Activates Partial. 4. Meshes Partial. 5. Analyzes Partial."`

★ **`Study.CreateMesh` 的第二处实参配方**（逐字）：`Study.CreateMesh(swsLinearUnitMillimeters, 20, 1)`
—— 与 §3.1 的 `Study.CreateMesh(0, el, tl)` **口径不同**：此处第二、三参是 `20` 与 `1`（实数），
前者是取自 `GetDefaultElementSizeAndTolerance` 的 `el`/`tl`。⇒ 记为**两处不一致**，不做调和。

---

## 四 · 我读到的「不一致」（只陈述，不调和）

1. **成员页比成员页多 11 个方法。**
   `SOLIDWORKS.Interop.cosworks~SolidWorks.Interop.cosworks.ICWLoadsAndRestraintsManager_members.html`（页内 `version":"2026"`）
   的 Methods 表列 **43 个方法 + 1 个属性（`Count`）= 44 个成员**；本机只有 **33 个**成员页。
   缺页的 11 个（**签名一律查不到**）：
   `AddBearingConnector` · `AddCable` · `AddGeneralSpringConnector` · `AddLinkageRod` ·
   `AddInitialConditionForDynamicStudy2` · `AddSelectedBaseExcitation2` · `AddUniformBaseExcitation2` ·
   `GetBearingConnector` · `GetCable` · `GetGeneralSpringConnector` · `GetLinkageRod`

2. **三个成员的废弃标记，两处源不一致。**
   成员页把 `AddInitialConditionForDynamicStudy` / `AddSelectedBaseExcitation` / `AddUniformBaseExcitation`
   标为 Obsolete 并点名 `…2`；但这三个**各自的成员页正文没有任何 Obsolete 字样**，
   且它们正文的一行摘要与成员表里 **`…2`** 那一行的描述文字相同。
   ⇒ 无法从本机判断这两个 html 文件到底对应 1 版还是 2 版。**记为查不到，不代为判定。**

3. **`AddForce2` 的废弃句里接口名首字母大小写与别处不同。**
   逐字是 `ICWloadsAndRestraintsManager::AddForce3`，而同一页 See Also 与其它成员页都写 `ICWLoadsAndRestraintsManager`。

4. **`Availability` 字符串三处异常**（照抄，不修正）：
   - `AddTemperature` → `"SOLIDWORKS Simuluation API 200"`（`Simuluation` 拼写 + 年份 `200`）
   - `AddHeatFlux` → `"SOLIDWORKS Simulation API 2008 SP1.0"`（其余成员无 `SP1.0`）

5. **同目录另有 4 个 2021 版的重复页**：`AddForce.html` / `AddRestraint.html` /
   `AddPrescribedDisplacement.html` / `AddCyclicSymmetryRestraint.html`
   （页内 `browserTitle` 含 `- 2021 -`），与 `ICWLoadsAndRestraintsManager~<同名>.html` 并存。

---

## 五 · ★ 哪些成员要求算例类型（逐字证据汇总）

本机唯一能抄到的「算例类型前置」共 9 处，全部逐字：

| 成员 | 逐字原文 | 出处文件 |
|---|---|---|
| `AddTemperature` | `"Temperature can be used with static, nonlinear, frequency, buckling, and thermal studies."`（**唯一列全的**） | `ICWLoadsAndRestraintsManager~AddTemperature.html` |
| `AddCyclicSymmetryRestraint` | `"This method is valid only for static and nonlinear studies."` | `…~AddCyclicSymmetryRestraint.html`（Remarks 段） |
| `AddConvection` | `"Creates a convection load for thermal studies."` | `…~AddConvection.html`（摘要句） |
| `AddHeatFlux` | `"Creates a heat flux load for thermal studies."` | `…~AddHeatFlux.html`（摘要句） |
| `AddHeatPower` | `"Creates a heat power load for thermal studies."` | `…~AddHeatPower.html`（摘要句） |
| `AddRadiation` | `"Creates a radiation load for thermal studies."` | `…~AddRadiation.html`（摘要句） |
| `AddInitialConditionForDynamicStudy` | `"…in modal time history and nonlinear dynamic studies."` | `…~AddInitialConditionForDynamicStudy.html`（摘要句） |
| `AddSelectedBaseExcitation` | `"…for dynamic studies."` | `…~AddSelectedBaseExcitation.html`（摘要句） |
| `AddUniformBaseExcitation` | `"…for dynamic studies."`；参数表另写 `"null for global direction if Response Spectrum study"` | `…~AddUniformBaseExcitation.html` |

★ **未写算例类型的成员**（其页面既无 Remarks 段、摘要句也不提算例类型）：
`AddBearingLoad` `AddBoltConnector` `AddCentrifugalForce` `AddDistributedMass` `AddEdgeWeldConnector`
`AddElasticConnector` `AddForce` `AddForce2` `AddForce3` `AddGravity` `AddLinkConnector` `AddPinConnector`
`AddPrescribedDisplacement` `AddPressure` `AddRemoteLoad` `AddRestraint` `AddRigidConnector`
`AddSpotWeldConnector` `AddSpringConnector` `CopyLoadsAndRestraintsToStudy` `Count`
`DeleteLoadsAndRestraints` `GetEdgeWeldConnector` `GetLoadsAndRestraints`
⇒ 对这些成员「是否要求特定算例类型」**查不到**（官方页面没写，不等于不需要）。

---

## 六 · 抄录统计

- **完整抄到五样的成员：33 个**（`ICWLoadsAndRestraintsManager`，本机有成员页的全部）。
  其中 **14 个有 Remarks 段**，19 个无 Remarks 段（已在各节标出）。
- **只抄到部分要素的**：无 —— §一 里 33 个都是「签名 + 例子清单 + 枚举名 + 废弃链 + Availability」齐全，
  仅「枚举数值」与「多数例子的调用序」因本机无源而标「查不到」。
- **完全查不到的成员：11 个**（见 §四.1）。
- **接口层**：`ICosmosWorks` / `ICWStudyManager` / `ICWStudy` / `CWMesh` / `ICWResults` /
  `ICWContactManager` / `ICWSolidManager` 的成员页 **本机一律查不到**（§〇）。