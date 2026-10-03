# audit-09-simulation-A · 核对 A（签名一致性）

- **域**：09-simulation
- **我们这边的文件**：`scripts/sw_simulation.py`（1225 行）· `scripts/sw_simulation_loads.py`（1104 行）· `scripts/sw_topology.py`（997 行）
  —— 三份**都存在**，无「该域无对应文件」。
- **只做**：核对 A —— 把每个 COM 调用的**实参**与官方签名的**形参表**并排数
  ⇒ 只报「参数个数不符 / 顺序不符 / 明显类型不符 / 成员在官方形参表里根本不存在」。
  ⇒ **不报** Obsolete 标记（属核对 C）、**不报** 前置与 mark（属核对 B）、**不报** 枚举字面量取值（属核对 C）。
- **官方源（只读）**：
  - `D:/AI/SW/AI Solidworks/官方文档/SWhelp/cosworks/` —— 官方 Simulation API CHM 解包（`.NET interop` 册，`ICWLoadsAndRestraintsManager~<成员>.html`）
  - `C:/cworks_vb6/CosmosWorksLib~<类>~<成员>.html` —— 官方 Simulation **VB6 类型库 CHM** 解包（`Public Function/Sub` 声明）
  - `C:/swapi/types/<接口>/<成员>.md` —— sldworks 侧成员的精确签名（**cosworks 接口在此源 0 收录，见下**）
  - `D:/AI/SW/_raw/reflect/iface_cosworks.txt` —— **出厂类型库 `SolidWorks.Interop.cosworks.dll` 纯元数据反射**（本仓铁律 4 的裁决者）
- **未跑**：SolidWorks、pytest。**未改仓内任何文件**（只写本文件）。

## 查不到 / 不予判定（记「查不到」，不写进表）

- **`C:/swapi` 未收录 cosworks 任何接口**：`C:/swapi/types/` 下 566 个接口目录，按 `^ICW|^CWMesh|Cosmos` 过滤只命中 `ICosmeticWeldBeadFeatureData` / `ICosmeticWeldBeadFolder` / `ICosmosMotionStudyProperties` / `ICosmosMotionStudyResults` / `swCosmosWorksMat` —— **无 `ICWStudyManager` / `ICWStudy` / `ICWLoadsAndRestraintsManager` / `ICWTopologyStudyManager`**。`C:/swapi/enums/` 下也无任何 `sws*` 枚举。
  ⇒ 本域 cosworks 侧成员的签名比对**全部改用**「官方 cosworks CHM（.NET 册 + VB6 册）」与「出厂类型库反射」两源。
  **不拿相似名字顶替**（铁律 5）。
- **`ICwAddincallback.CosmosWorks`**（`sw_simulation.py` 的 `get_com_member(addin, "CosmosWorks")`）：
  `C:/cworks_vb6/` 下按 `*Addincallback*` / `*CwAddin*` 过滤 **0 命中**；`D:/AI/SW/_raw/cosworks_pages/` 下亦无该接口页。
  ⇒ **官方页查不到**，本行不判定、不报。
- **`ICWLoadsAndRestraintsManager~Count`**：`C:/cworks_vb6/` 下**无该页**（`Get-ChildItem -Filter "*LoadsAndRestraints*"` 只列出 8 个 `CWLoadsAndRestraints~*` 页，管理器的 `Count` 页不在 VB6 册里）；
  `D:/AI/SW/_raw/cosworks_pages/ICWLoadsAndRestraintsManager~Count.txt` 存在但正文是 JSON 转义 + 大量 CSS，未取到声明。
  ⇒ 改用出厂反射 `Int32 get_Count()`（0 参）与我们的 `get_com_member(manager, "Count")`（0 实参）并排 ⇒ **相符**，故不报。
- **`AddForce2` / `AddForce3`**：官方 .NET 册有完整声明（5 参 / 21 参），我们 `OFFICIAL_LOAD_SIGNATURES` 记 4 / 20（**不含末尾 by-ref `ErrorCode`**，与模块头约定一致）⇒ 相符；
  但这两个成员**在本域三个文件里没有任何调用点**（只出现在常量表 `_REFGEOM_POSITIONS` 里），**没有实参可并排** ⇒ 不报。

## 表

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_simulation_loads.py` —— `get_loads_and_restraints()`：<br>`return _check(manager, "GetLoadsAndRestraints", 1, int(index))`<br>而 `_check` 补末尾出参的条件是 `if _wants_error_code(member): tail.append(out_i4())`，`_wants_error_code` 只认 `_ERRORCODE_MEMBERS` frozenset —— 该 frozenset 里**没有** `"GetLoadsAndRestraints"` ⇒ 本次调用**只给 1 个实参**（`int(index)`）。<br>★ 同仓对照：`scripts/sw_simulation.py` 的 `collect_study_evidence()` 里同一成员是<br>`entry = get_com_member(lrm, "GetLoadsAndRestraints", position, out_i4())` —— **2 个实参**。 | **① 官方 .NET CHM `D:/AI/SW/AI Solidworks/官方文档/SWhelp/cosworks/ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html`**：<br>`Function GetLoadsAndRestraints( _`<br>`ByVal <i><a class="parameter" id="NIndex" ...>NIndex</a></i> As System.Integer, _`<br>`ByRef <i><a class="parameter" id="Err`…（该页另有 `value = instance.GetLoadsAndRestraints(NIndex, ErrorCode)` 与 C# 段 `CWLoadsAndRestraints GetLoadsAndRestraints( System.int NIndex , out System.int ErrorCode )`）<br>**② 官方 VB6 CHM `C:/cworks_vb6/CosmosWorksLib~ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html`**：<br>`GetLoadsAndRestraints n=2 ::  _ ByVal NIndex As Long, _ ByRef ErrorCode As Long _`<br>**③ 出厂类型库反射 `D:/AI/SW/_raw/reflect/iface_cosworks.txt` 的 `## ICWLoadsAndRestraintsManager` 段**：<br>`CWLoadsAndRestraints GetLoadsAndRestraints(Int32, Int32&)` | **参数个数不符**：官方形参表是 **2 个**（`NIndex` + by-ref `ErrorCode`），我们这次只传 **1 个**。两处根因同时成立 —— ① `GetLoadsAndRestraints` 不在 `_ERRORCODE_MEMBERS` 里 ⇒ `_check` 不补 `out_i4()`；② 本模块**自己的来源块**（`get_loads_and_restraints` 上方）已逐字抄下 `GetLoadsAndRestraints(ByVal NIndex As Integer, ByRef ErrorCode As Integer)` 并写明「这两个方法都带 by-ref ErrorCode」，源码注释与实际实参数自相矛盾。 | 高（官方 CHM .NET 册 + 官方 VB6 册 + 出厂反射**三源一致**都是 2 形参） |
| 2 | `scripts/sw_simulation_loads.py` —— `get_edge_weld_connector()`：<br>`return _check(manager, "GetEdgeWeldConnector", 1, int(index))`<br>同样地，`_ERRORCODE_MEMBERS` frozenset 里**没有** `"GetEdgeWeldConnector"` ⇒ **只给 1 个实参**。 | **① 官方 .NET CHM `D:/AI/SW/AI Solidworks/官方文档/SWhelp/cosworks/ICWLoadsAndRestraintsManager~GetEdgeWeldConnector.html` 的 VB 声明**（解包后逐字）：<br>`Function GetEdgeWeldConnector( _ ByVal NIndex As System.Integer, _ ByRef ErrorCode As System.Integer _ ) As CWEdgeWeldConnector`<br>**② 官方 VB6 CHM `C:/cworks_vb6/CosmosWorksLib~ICWLoadsAndRestraintsManager~GetEdgeWeldConnector.html`**：<br>`GetEdgeWeldConnector n=2 ::  _ ByVal NIndex As Long, _ ByRef ErrorCode As Long _`<br>**③ 出厂类型库反射 `D:/AI/SW/_raw/reflect/iface_cosworks.txt` 的 `## ICWLoadsAndRestraintsManager` 段**：<br>`CWEdgeWeldConnector GetEdgeWeldConnector(Int32, Int32&)` | **参数个数不符**：官方形参表 **2 个**（`NIndex` + by-ref `ErrorCode`），我们只传 **1 个**；与第 1 条同一根因（该成员漏列在 `_ERRORCODE_MEMBERS` 里，`_check` 因此不补末尾出参）。 | 高（官方 CHM .NET 册 + 官方 VB6 册 + 出厂反射**三源一致**都是 2 形参） |
| 3 | `scripts/sw_simulation_loads.py` —— `collect_loads_evidence()`：<br>`items.append({`<br>`    "index": index,`<br>`    "name": str(get_com_member(item, "GetName") or ""),`<br>`    "type": int(get_com_member(item, "GetType") or -1),`<br>`})`<br>⇒ 对载荷/夹具对象 `item` 调 **2 个零参成员** `GetName` / `GetType`。<br>★ 同仓对照：`scripts/sw_simulation.py` 的 `collect_study_evidence()` 对同一类对象用的是 `get_com_member(entry, "Name")` / `get_com_member(entry, "Type")` —— **属性名，不是 `Get*`**。 | **① 官方 VB6 CHM 成员索引页 `C:/cworks_vb6/CosmosWorksLib~CWLoadsAndRestraints_members.html`**（去标签后的正文全文）：<br>`Properties EntityCount Name State Type `<br>—— 整页**只有这 4 个属性**，`GetName` / `GetType` 在该页 **0 命中**（对同页做 `Select-String -Pattern "GetName|GetType"` ⇒ 命中数 **0**）。<br>该目录下 `CWLoadsAndRestraints~*` 逐页清单同样只有 `EntityCount` / `GetDirection` / `GetEntityAt` / `GetReferenceGeometry` / `Name` / `State` / `SuppressUnSuppress` / `Type`，**无 `GetName` 页、无 `GetType` 页**。<br>**② 出厂类型库反射 `D:/AI/SW/_raw/reflect/iface_cosworks.txt` 的 `## ICWLoadsAndRestraints` 段（8 行，逐行）**：<br>`Int32 get_EntityCount()`<br>`String get_Name()`<br>`Int32 get_State()`<br>`Int32 get_Type()`<br>`Object GetDirection()`<br>`Object GetEntityAt(Int32, Int32&)`<br>`Object GetReferenceGeometry(Int32&)`<br>`Void SuppressUnSuppress()`<br>—— **无 `GetName`、无 `GetType`**。 | **成员缺席（形参表里根本没有这两个成员可并排）**：`CWLoadsAndRestraints` / `ICWLoadsAndRestraints` 的名称与类型读数在官方**两源**里都是**属性** `Name` / `Type`（另有 `State` / `EntityCount`），不是 `GetName` / `GetType` 方法；我们这两行给它们的实参个数（0）本身没错，错在**成员名**。⇒ 两源一致缺席，非「两源不一致」。 | 高（官方 VB6 CHM 成员索引页 + 出厂类型库反射 `## ICWLoadsAndRestraints` 全段**两源一致**都没有 `GetName`/`GetType`） |

## 已并排且**相符**、故不列进表的（抽样，供复核）

- **载荷族 25 个 `_check` 调用点**（`AddRestraint` / `AddForce` / `AddForce2` 表 / `AddPressure` / `AddRemoteLoad` / `AddGravity` / `AddCentrifugalForce` / `AddDistributedMass` / `AddTemperature` / `AddHeatFlux` / `AddHeatPower` / `AddConvection` / `AddRadiation` / `AddSpringConnector` / `AddPinConnector` / `AddRigidConnector` / `AddLinkConnector` / `AddElasticConnector` / `AddBoltConnector` / `AddSpotWeldConnector` / `AddEdgeWeldConnector` / `AddCyclicSymmetryRestraint` / `AddPrescribedDisplacement` / `AddBearingLoad`）：
  逐个把「`OFFICIAL_LOAD_SIGNATURES` 记的 N」+1（末尾 by-ref `ErrorCode`）与官方 .NET CHM 的 VB 声明参数个数并排，**25/25 全对**；形参顺序也逐条比过（如 `AddRemoteLoad(NLoadType, DispArray, NLocationUnits, DXValue, DYValue, DZValue, ErrorCode)` 对我们 `int(load_type), entities, int(units), float(dx), float(dy), float(dz)`）。
- **`_REFGEOM_POSITIONS` 的位置**：`AddForce`=2 / `AddForce2`=3 / `AddForce3`=18，与官方 VB 声明里 `RefGeom` 所在的 0 基序号逐一核对**全对**（`AddForce3` 官方声明第 19 个形参即 `ByVal RefGeom As System.Object`，0 基 18）。
- **拓扑族 26 个调用点**：`CreateGoal(1)` / `Create{Mass,Stress,FactorOfSafety,PreservedRegionControl,SymmetryControl,Demold,Thickness}Constraint|Control(ByRef ErrorCode)` / 9 个 `Get*(SName, ByRef ErrorCode)` / `RemoveConstraint(1)` / `BeginEdit`(0) / `EndEdit`(0) / `SetMassPreference(1)` / `SetValue(1)` / `SetComparator(1)` / `SetIncludeRegionDepth2(1)` / `SelectSymmetryType(1)` / `SelectDemoldDirection(1)` / `SetInclude{Min,Max}MemberThickness2(1)` / `Set{Minimum,Max}MemberThickness(1)` / `Set{IterationOption,IterationLimit,ConvergenceCheck}(1)` —— 与 `C:/cworks_vb6/CosmosWorksLib~ICWTopology*` 各页的 VB 声明**全部相符**。
- **`sw_simulation.py` 59 个调用点**：`GetAddInObject(1)` / `LoadAddIn(1)`（对 `C:/swapi/types/ISldWorks/`）、`CreateNewStudy3(4)` / `CreateNewStudy2(3)` / `CreateNewStudy(4)` / `GetStudy(1)`（对 `C:/cworks_vb6/CosmosWorksLib~CWStudyManager~*`）、`AddRestraint(4)` / `AddForce(4)`、`CreateMesh(3)`（`NUnits, DElementSize, DTolerance`）、`GetDefaultElementSizeAndTolerance(3)`（`NUnits, ByRef DElementSize, ByRef DTolerance`）、`GetSelectedObject6(2)` / `GetSelectedObjectCount2(1)` / `SelectByID2(9)` / `ClearSelection2(1)` / `GetBodies2(2)` / `GetBodyBox(0)`（对 `C:/swapi/types/`）、`SetMaterialPropertyName2(3)`（对 `C:/swapi/types/IPartDoc/SetMaterialPropertyName2.md`）—— **全部相符**。
- **`sw_topology.py`**：`MeshAndRun(0)` / `RunAnalysis(0)` / `CreateMesh(3)` / `Results` / `GetPlotCount(0)` / `GetPlotNames(0)` / `GetMaximumAvailableSteps(0)` / `StudyCount` / `ActiveStudy` / `Name` / `AnalysisType` / `MeshType` / `ConfigurationName` / `TopologyStudyManager` / `TopologyStudyOptions` —— 与 `C:/cworks_vb6/CosmosWorksLib~CWStudy*.html` 的 `Public Property … As …` / `Public Sub …()` 声明**全部相符**。

## 结尾三行

核了 **149** 处（`sw_simulation.py` 59 个直接 COM 调用点 + `sw_simulation_loads.py` 9 个直接调用点与 27 个 `_check(...)` 汇聚点 + `sw_topology.py` 54 个直接调用点，其中含 1 个按 `_TOPOLOGY_GETTERS` 循环覆盖 9 个 `Get*` 的动态调用；逐个把实参个数 / 顺序 / 类型与官方签名的形参表并排）。
报了 **3** 条（全部落在 `scripts/sw_simulation_loads.py`；`sw_simulation.py` 与 `sw_topology.py` 零条）。
置信度为高的是第 **1、2、3** 条 —— 三条各自都有**两个及以上**官方源（官方 cosworks CHM 的 .NET 册与 VB6 册、或出厂类型库反射 `iface_cosworks.txt`）逐字给出一致的形参表 / 成员表，且**无一处出现「文档与出厂类型库参数个数不同」的两源冲突**。