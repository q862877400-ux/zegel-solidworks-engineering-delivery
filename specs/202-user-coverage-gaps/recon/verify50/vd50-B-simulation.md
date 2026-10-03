# vd50-B · simulation · 「置信度=高」条目对账

**核的范围**：`specs/202-user-coverage-gaps/recon/audit-vs-official/` 下与 simulation 域有关的三个文件
`audit-09-simulation-A.md` / `audit-09-simulation-B.md` / `audit-09-simulation-C.md`
（`audit-10-misc-*` 三个文件按 `simulation|sw_simulation|cosworks|Simulation|拓扑` 全文检索 **0 命中**，与本域无关，不纳入）。
**只核置信度为「高」的条目**：A 的 #1 #2 #3 · B 的 #1 #2 #3 #4 · C 的 #1 —— **共 8 条**。
（A 的三篇的 #5 / C 的 #2 #3 自评为「中」，按任务要求**未碰**。）

**纪律**：只读核验，**未改仓内任何文件**；本文件是唯一写入。
每条给两段可搜索原文（仓内那一段 + 官方那一段），给不出两段的不写。
不写行号，只写原文片段。查不到就写查不到，不用相似名字顶替。

---

## 〇 · 一条必须先说清的前置事实（否则下面几条会被误判）

**`C:/swapi/` 对 cosworks 一族 0 收录** —— 本任务指定的官方检索根 `C:\swapi\types\` 下的目录名按
`^ICW|^CWMesh|Cosmos` 过滤，**只命中 3 个**：
```
ICosmosMotionStudyProperties, ICosmosMotionStudyResults, swCosmosWorksMat
```
**无 `ICWStudyManager` / `ICWStudy` / `ICWLoadsAndRestraintsManager` / `ICWLoadsAndRestraints` / `ICWTopology*`。**

⇒ 本域 8 条里的官方原文**在 `C:/swapi` 下必然查不到**（不是引错，是该源不收录）。
⇒ 按铁律 3，我**拿 cosworks 官方 VB6 类型库 CHM 解包**（`C:\cworks_vb6\`）与
**官方 Simulation .NET interop CHM 解包**（`D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\`）核对，
并用**出厂类型库反射**（`D:\AI\SW\_raw\reflect\iface_cosworks.txt`）作第三源。
★ 每一处都写明**原文实际在哪个文件**，不拿相似名冒充。

---

## 一 · 总表

| 条目 | 我们的原文在？ | 官方原文在？ | 判定 |
|---|---|---|---|
| A-1 `GetLoadsAndRestraints` 只传 1 个实参 | ✅ 在（逐字） | ✅ 在（逐字，**引用的 VB6 页名有误，见文末 D-1**） | **成立** |
| A-2 `GetEdgeWeldConnector` 只传 1 个实参 | ✅ 在（逐字） | ✅ 在（逐字，**同一处页名有误，见 D-1**） | **成立** |
| A-3 载荷对象用 `GetName`/`GetType`（官方只有 `Name`/`Type`） | ✅ 在（逐字） | ✅ 在（逐字，两源一致缺席） | **成立** |
| B-1 `create_preserved_region` 不调 `SelectFaces` | ✅ 在（逐字） | ✅ 在（逐字） | **成立** |
| B-2 `create_symmetry_control` 不交对称面 | ✅ 在（逐字） | ✅ 在（逐字） | **成立** |
| B-3 `create_demold_control` 不交拔模方向几何 | ✅ 在（逐字） | ✅ 在（逐字） | **成立** |
| B-4 `Create*` 不在管理器层 `BeginEdit…EndEdit` 之间 | ✅ 在（逐字） | ✅ 在（逐字） | **成立** |
| C-1 我们调的是被官方标 Obsolete 的 `AddForce` | ✅ 在（逐字） | ✅ 在（逐字） | **成立** |

★ **8 条全部成立，核心判定 0 条被推翻**；另查出 **1 处引用瑕疵**（D-1，不推翻任何一条判定）。

---

## 二 · 逐条

### A-1 · `scripts/sw_simulation_loads.py::get_loads_and_restraints` 只给 1 个实参 —— **判定：成立**

**仓内那一段** —— `scripts/sw_simulation_loads.py`：
```python
def get_loads_and_restraints(manager, index: int):
    """按序号取载荷/夹具对象。"""
    return _check(manager, "GetLoadsAndRestraints", 1, int(index))
```
同文件 `_check` 的末尾出参逻辑与收尾：
```python
    tail = list(args)
    if _wants_error_code(member):
        tail.append(out_i4())
    ...
    return get_com_member(manager, member, *tail)
```
同文件 `_wants_error_code` 与其唯一输入的 frozenset（**逐字可见该 frozenset 里只有 `Add*` 族**，
`GetLoadsAndRestraints` 与 `GetEdgeWeldConnector` 均**不在其中**）：
```python
def _wants_error_code(member: str) -> bool:
    """★ 该成员是否要末尾 `ByRef ErrorCode`（★ 只认已核过的清单）。"""
    return member in _ERRORCODE_MEMBERS

_ERRORCODE_MEMBERS = frozenset({
    "AddBearingConnector", "AddBearingLoad", "AddBoltConnector",
    "AddCable", "AddCentrifugalForce", "AddConvection",
    ...
    "AddUniformBaseExcitation", "AddUniformBaseExcitation2",
})
```
★ 同仓**自相矛盾**的对照也真实存在 —— `scripts/sw_simulation.py` 对同一成员用的是 2 个实参：
```python
                entry = get_com_member(lrm, "GetLoadsAndRestraints", position, out_i4())
```
且 `scripts/sw_simulation_loads.py` 自己 `get_loads_and_restraints` 上方的来源块逐字抄了官方声明、并自述「这两个方法都带 by-ref ErrorCode」：
```python
#   GetLoadsAndRestraints(ByVal NIndex As Integer, ByRef ErrorCode As Integer)
# ⚠ 这两个方法都**带 by-ref ErrorCode**，同样传 0 占位、不据其判成败。
```

**官方那一段** —— `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html`（去标签后逐字）：
```
Function GetLoadsAndRestraints( _ ByVal NIndex As System.Integer, _ ByRef ErrorCode As System.Integer _ ) As CWLoadsAndRestraints
```
同页 C# 段：
```
CWLoadsAndRestraints GetLoadsAndRestraints( System.int NIndex , out System.int ErrorCode )
```
出厂类型库反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWLoadsAndRestraintsManager` 段：
```
  CWLoadsAndRestraints GetLoadsAndRestraints(Int32, Int32&)
```
（★ 引用瑕疵见 **D-1**：条目写的第三个源 `C:/cworks_vb6/CosmosWorksLib~ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html` **不存在**，实名少个 `I`。）

**一句话依据**：官方形参表是 `NIndex` + **非可选的 by-ref `ErrorCode`** 两参，而 `_check` 因该成员漏列在 `_ERRORCODE_MEMBERS` 里**不补**末尾出参，实际发出的调用只有 1 个实参 —— 同一个仓的另一个文件对同一成员传的正是 2 个，源码注释与实参自相矛盾。

---

### A-2 · `scripts/sw_simulation_loads.py::get_edge_weld_connector` 只给 1 个实参 —— **判定：成立**

**仓内那一段** —— `scripts/sw_simulation_loads.py`：
```python
def get_edge_weld_connector(manager, index: int):
    """按序号取边焊连接件对象。"""
    return _check(manager, "GetEdgeWeldConnector", 1, int(index))
```
（`_ERRORCODE_MEMBERS` 里同样**没有** `"GetEdgeWeldConnector"` —— 见 A-1 引的 frozenset 原文。）

**官方那一段** —— `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~GetEdgeWeldConnector.html`（去标签后逐字）：
```
Function GetEdgeWeldConnector( _ ByVal NIndex As System.Integer, _ ByRef ErrorCode As System.Integer _ ) As CWEdgeWeldConnector
```
真实名名的官方 VB6 页 `C:\cworks_vb6\CosmosWorksLib~CWLoadsAndRestraintsManager~GetEdgeWeldConnector.html`：
```
GetEdgeWeldConnector Method (CWLoadsAndRestraintsManager) … Public Function GetEdgeWeldConnector( _ ByVal NIndex As Long, _ ByRef ErrorCode As Long _ ) As CWEdgeWeldConnector
```
出厂类型库反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt`：
```
  CWEdgeWeldConnector GetEdgeWeldConnector(Int32, Int32&)
```

**一句话依据**：与 A-1 同一根因（该成员漏列在 `_ERRORCODE_MEMBERS` ⇒ `_check` 不补末尾 by-ref 出参），官方两源 + 出厂反射三处一致给 2 个形参，我们这次只传 1 个。

---

### A-3 · 载荷对象的名称/类型用 `GetName`/`GetType`，官方只有 `Name`/`Type` —— **判定：成立**

**仓内那一段** —— `scripts/sw_simulation_loads.py`：
```python
        items.append({
            "index": index,
            "name": str(get_com_member(item, "GetName") or ""),
            "type": int(get_com_member(item, "GetType") or -1),
        })
```
★ 该函数自己的来源块**逐字声称官方文档化了这两个成员**（此句即被下面官方段否掉）：
```python
#         官方已文档化的载荷对象成员：CWLoadsAndRestraints.GetName /
#         GetType（反射 dump enum_cosworks.txt 侧为 363 个枚举，本处不逐个展开）。
```
★ 同仓对照 `scripts/sw_simulation.py` 对同一类对象用的是**属性名**：
```python
                        "name": str(get_com_member(entry, "Name") or ""),
                        "type": int(get_com_member(entry, "Type") or -1),
```

**官方那一段** —— `C:\cworks_vb6\CosmosWorksLib~CWLoadsAndRestraints_members.html`（去标签后全文尾段）：
```
CWLoadsAndRestraints Object Members Collapse All Expand All Public Methods GetDirection GetEntityAt GetReferenceGeometry SuppressUnSuppress Public Properties EntityCount Name State Type
```
★ 对该页做 `GetName|GetType` 检索：**命中数 0**。
出厂类型库反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWLoadsAndRestraints` 段（**全部 8 行**）：
```
## ICWLoadsAndRestraints
  Int32 get_EntityCount()
  String get_Name()
  Int32 get_State()
  Int32 get_Type()
  Object GetDirection()
  Object GetEntityAt(Int32, Int32&)
  Object GetReferenceGeometry(Int32&)
  Void SuppressUnSuppress()
```
—— 同样**无 `GetName`、无 `GetType`**。

**一句话依据**：`CWLoadsAndRestraints` 的名称与类型在官方**两源一致**地都是**属性** `Name` / `Type`（连 `State` / `EntityCount` 也是属性），我们却按方法名 `GetName` / `GetType` 去取 —— 形参表里根本没有这两个成员可并排，且本仓另一个文件用的就是属性名。

---

### B-1 · `create_preserved_region` 只设 `SetIncludeRegionDepth2`，不交保留面 —— **判定：成立**

**仓内那一段** —— `scripts/sw_topology.py`：
```python
def create_preserved_region(study, *, option: int | None = None):
    """建保留区控制，返回该控制对象。

    ⚑ 调用方须**先选好要保留的面**再调本函数 —— ``ICWTopologyPreservedRegionControl``
    的 ``SelectFaces(Object)`` 接受实体数组，…故本函数**不接受面参数**：由调用方选好再调。
    """
    manager = get_topology_study_manager(study)
    control = get_com_member(manager, "CreatePreservedRegionControl", out_i4())
    if control is None:
        raise RuntimeError("CreatePreservedRegionControl 未返回对象")

    def _configure():
        if option is not None:
            get_com_member(control, "SetIncludeRegionDepth2", True)
        return control

    return _edit(control, _configure)
```
★ 全文件检索 `SelectFaces` —— **0 命中**（函数体既不读选区、也不传面）。

**官方那一段** —— `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`（逐字，连行序）：
```
CWTopoPreservedRegionObj.BeginEdit
Set DispatchObj1 = Part.SelectionManager.GetSelectedObject6(1, -1)
Set DispatchObj2 = Part.SelectionManager.GetSelectedObject6(2, -1)
DispArrayForPreservedRegion = Array(DispatchObj1, DispatchObj2)
ErrorCodeObj =
CWTopoPreservedRegionObj.SelectFaces((DispArrayForPreservedRegion))
If ErrorCodeObj <> 0 Then ErrorMsg swApp, "Failed: CWTopoPreservedRegionObj faces could not be selected": GoTo LastLine
CWTopoPreservedRegionObj.SetIncludeRegionDepth2 True
```

**一句话依据**：官方在同一事务里**先**把选中的面装成 `DispArray` 交给 `SelectFaces`、**再**设 `SetIncludeRegionDepth2`，我们只做了后一步，docstring 要求的「调用方先选好」在函数体里没有任何取选区的语句承接。

---

### B-2 · `create_symmetry_control` 只调 `SelectSymmetryType`，不交对称面 —— **判定：成立**

**仓内那一段** —— `scripts/sw_topology.py`：
```python
def create_symmetry_control(study, *, symmetry_type: int = 0):
    """建对称控制（官方教程用 1/4 对称）。调用方须先选好对称平面。"""
    manager = get_topology_study_manager(study)
    control = get_com_member(manager, "CreateSymmetryControl", out_i4())
    if control is None:
        raise RuntimeError("CreateSymmetryControl 未返回对象")

    def _configure():
        get_com_member(control, "SelectSymmetryType", int(symmetry_type))
        return control

    return _edit(control, _configure)
```
★ 全文件检索 `SelectFirstSymmetryPlane` / `SelectSecondSymmetryPlane` —— **0 命中**。

**官方那一段** —— `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`（逐字，含 1/4 对称两行）：
```
CWTopoSymmetryControlObj.BeginEdit
Set sDispObjPlane1 = Part.SelectionManager.GetSelectedObject6(1, -1)
CWTopoSymmetryControlObj.SelectSymmetryType 0
CWTopoSymmetryControlObj.SelectFirstSymmetryPlane sDispObjPlane1
ErrorCodeObj = CWTopoSymmetryControlObj.EndEdit()
```
（1/4 对称处另一形态）
```
CWTopoSymmetryControlObj.SelectSymmetryType 1
CWTopoSymmetryControlObj.SelectFirstSymmetryPlane sDispObjPlane1
CWTopoSymmetryControlObj.SelectSecondSymmetryPlane sDispObjPlane2
```
官方教程侧 `C:\topo_en\t_defining_quarter_symmetry_control.htm`（去标签后逐字）：
```
For Type , select Quarter Symmetry . Click in Select First Symmetry Plane , and from the brake rotor flyout FeatureManager design tree, select First Symmetry .
```

**一句话依据**：官方调用序是 `SelectSymmetryType` **紧接** `SelectFirstSymmetryPlane <plane>`（1/4 对称再加 `SelectSecondSymmetryPlane`），我们只有前者，没有任何把平面交给控制的调用。

---

### B-3 · `create_demold_control` 只调 `SelectDemoldDirection`，不交方向几何 —— **判定：成立**

**仓内那一段** —— `scripts/sw_topology.py`：
```python
def create_demold_control(study, *, direction: int = 0):
    """建脱模控制（制造约束）。调用方须先选好拔模方向的面/边/基准面。"""
    manager = get_topology_study_manager(study)
    control = get_com_member(manager, "CreateDemoldControl", out_i4())
    if control is None:
        raise RuntimeError("CreateDemoldControl 未返回对象")

    def _configure():
        get_com_member(control, "SelectDemoldDirection", int(direction))
        return control

    return _edit(control, _configure)
```
★ 全文件检索 `SelectPlaneForDirection` / `SelectEdgeForPullDirection` —— **0 命中**。

**官方那一段** —— `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`（逐字，两个形态）：
```
CWTopoDemoldControlObj.BeginEdit
Set sDispObjPlane = Part.SelectionManager.GetSelectedObject6(1, -1)
CWTopoDemoldControlObj.SelectDemoldDirection 0
CWTopoDemoldControlObj.SetAutoDetermineCentralMidPlane2 False
CWTopoDemoldControlObj.SelectPlaneForDirection sDispObjPlane
ErrorCodeObj = CWTopoDemoldControlObj.EndEdit()
```
```
CWTopoDemoldControlObj.SelectDemoldDirection 1
CWTopoDemoldControlObj.SelectEdgeForPullDirection sDispObjEdge
```
官方教程侧 `C:\topo_en\t_defining_de-mold_manufacturing.htm`（去标签后逐字）：
```
select Selection Sets &gt; stamp direction . The preselected edge appears in Select edge to define the direction .
```

**一句话依据**：官方在 `SelectDemoldDirection` 之后**必须**再交出方向几何（`SelectPlaneForDirection` 或 `SelectEdgeForPullDirection`），我们这 3 行只有方向枚举，没有任何把面/边交给控制的那一步。

---

### B-4 · 7 个 `create_*` 不在**管理器层** `BeginEdit…EndEdit` 之间 —— **判定：成立**

**仓内那一段** —— `scripts/sw_topology.py::create_stress_constraint`：
```python
    manager = get_topology_study_manager(study)
    constraint = get_com_member(manager, "CreateStressConstraint", out_i4())
    if constraint is None:
        raise RuntimeError("CreateStressConstraint 未返回对象")

    def _configure():
        get_com_member(constraint, "SetComparator", int(comparator))
        get_com_member(constraint, "SetValue", float(value))
        return constraint

    return _edit(constraint, _configure)
```
★ 全文件 `_edit(` 的调用点分布（逐字）：**`_edit(manager, …)` 只出现 1 处**（`set_topology_goal` 里的 `return _edit(manager, _build)`），
其余 9 处全是 `_edit(constraint, …)` / `_edit(control, …)`；
7 个约束/控制工厂 `create_mass_constraint` / `create_factor_of_safety_constraint` / `create_stress_constraint` /
`create_preserved_region` / `create_symmetry_control` / `create_demold_control` / `create_thickness_control` **全部**只开约束对象层事务。
★ 同一模块自述的两种形态：
```python
        manager.BeginEdit()          # 开研究级事务
          …
            constraint.BeginEdit()     # 开该约束自己的事务
          …
        constraint.EndEdit()       # 提交该约束
        manager.EndEdit()            # 提交研究
```

**官方那一段** —— `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`（逐字）：
```
' Create topology stress constraint
CWTopologyStudyManagerObj.BeginEdit
Set CWTopoStressConstraintObj =
CWTopologyStudyManagerObj.CreateStressConstraint(ErrorCodeObj)
        If
ErrorCodeObj <> 0 Then ErrorMsg swApp, "Failed to create stress constraint.":
GoTo LastLine
```
（同文件里 `CWTopologyStudyManagerObj.BeginEdit` 与 `CWTopologyStudyManagerObj.EndEdit` 各出现 **26** 次，即每个 `Create*` 都套在管理器层事务里。）

**一句话依据**：官方把 `Create*` 放在 `CWTopologyStudyManagerObj.BeginEdit` … `EndEdit()` 之间，这 7 个工厂却只在**约束对象**上开事务，管理层的事务括号一次都没调（同一模块的 `set_topology_goal` 反而有 ⇒ 两种形态并存）。

---

### C-1 · 我们调的是官方标 **Obsolete** 的 `AddForce` —— **判定：成立**

**仓内那一段** —— 三处 COM 调用点，逐字：
```python
# scripts/sw_simulation_loads.py
    return _check(manager, "AddForce", 3, int(force_type), entities, ref_geom)
```
```python
# scripts/sw_simulation_loads.py（力矩）
        manager, "AddForce", 3, SWS_FORCE_TYPES["torque"], entities, ref_geom)
```
```python
# scripts/sw_simulation.py
    force = get_com_member(
        manager, "AddForce", int(force_type), entities,
        create_empty_dispatch_variant(), out_i4(),
    )
```
★ 全仓检索 `AddForce2` / `AddForce3`：**只出现在常量表与注释**（`_ERRORCODE_MEMBERS`、`_REFGEOM_POSITIONS`、`OFFICIAL_LOAD_SIGNATURES`、docstring），
**没有任何一处把它当 COM 成员名发起调用**。

**官方那一段** —— `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~AddForce.html`（去标签后逐字）：
```
Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddForce2
Function AddForce( _ ByVal NForceType As System.Integer, _ ByVal DispArray As System.Object, _ ByVal RefGeom As System.Object, _ ByRef Err…
```
同目录成员表 `members_2013.html` / `members_2014.html` / `members_2016.html` / `members_2021.html` **四页逐页都有**这两行：
```
AddForce Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddForce2
AddForce2 Obsolete. Superseded by ICWloadsAndRestraintsManager::AddForce3
```

**一句话依据**：官方把 `AddForce` 标 Obsolete 并点名后继 `AddForce2`，而 `AddForce2` 自身也是 Obsolete（后继 `AddForce3`）—— 我们三处 COM 调用全部打在 `AddForce` 上，且全仓从未调用过任一后继成员。

---

## 三 · D-1 · 唯一的「引用瑕疵」（不推翻任何一条判定）

**A-1 / A-2 的第二个官方源，条目引的文件名不存在。**

**仓内那一段（核对表里写的）** —— `audit-09-simulation-A.md` 第 1 / 2 条的官方列：
> **② 官方 VB6 CHM `C:/cworks_vb6/CosmosWorksLib~ICWLoadsAndRestraintsManager~GetLoadsAndRestraints.html`**：
> `GetLoadsAndRestraints n=2 ::  _ ByVal NIndex As Long, _ ByRef ErrorCode As Long _`
> `GetEdgeWeldConnector n=2 ::  _ ByVal NIndex As Long, _ ByRef ErrorCode As Long _`
> （两条并称「官方 CHM .NET 册 + 官方 VB6 册 + 出厂反射**三源一致**」）

**目标那一段（该目录的实际清单）** —— `C:\cworks_vb6\` 按 `*ICWLoadsAndRestraints*` 过滤：**命中 0**。
同名内容的真实文件是（少一个 `I`，VB6 册按类名 `CW…` 命名）：
```
C:\cworks_vb6\CosmosWorksLib~CWLoadsAndRestraintsManager~GetLoadsAndRestraints.html
C:\cworks_vb6\CosmosWorksLib~CWLoadsAndRestraintsManager~GetEdgeWeldConnector.html
```
其页内标题本身就写着 `GetLoadsAndRestraints Method (CWLoadsAndRestraintsManager)`。

**判定：成立（瑕疵，非推翻）** —— 引用**路径**错（`ICW…` 无此文件）、引用**排版**也不是逐字（`n=2 ::` 与逗号是核对方自己的归一化，页内原文是
`Public Function GetLoadsAndRestraints( _ ByVal NIndex As Long, _ ByRef ErrorCode As Long _ ) As CWLoadsAndRestraints`）；
但 A-1 / A-2 的**结论**另有两处**逐字可查**的官方源撑着（.NET 册原路径命中、出厂反射 `GetLoadsAndRestraints(Int32, Int32&)` 命中），
**结论不受影响** ⇒ 只记瑕疵，不改判定。
★ 顺带：A-3 引的 `C:/cworks_vb6/CosmosWorksLib~CWLoadsAndRestraints_members.html` 路径**是真实的**（本轮已逐字读到原文），不属此类。

---

## 四 · 查不到、故不写的（铁律 3）

- **`C:/swapi/` 下无 cosworks 任何接口/枚举** —— 8 条里的官方原文在该源**一律查不到**，已在开头按事实说明并改用 cosworks 官方 CHM + 出厂反射；**未拿 sldworks 侧的相似名字顶替**。
- `ICWLoadsAndRestraintsManager~Count`（A 篇「不予判定」项）本轮**未核** —— 不在「高置信度」范围。
- B 篇 #5（`CosmosWorks` 全大写 vs 驼峰）、C 篇 #2（`units=-1` 不在 `swsUnit_e`）、C 篇 #3（`MaterialIdName` 两页 Obsolete 标注不一致）—— 三条**自评为「中」**，按任务要求**未碰**。

---

## 结尾三行

**核了 8 处**（A-1 / A-2 / A-3 · B-1 / B-2 / B-3 / B-4 · C-1）—— 每处两侧都取到了**可搜索的原文片段**（仓内 + 官方）。
**对不上 0 处** —— 8 条核心判定全部**成立**（官方原文逐字在、我们的原文逐字在）。
**另 1 处引用瑕疵**（D-1：A-1/A-2 引用的 VB6 页名 `…~ICWLoadsAndRestraintsManager~…` 不存在，实名为 `…~CWLoadsAndRestraintsManager~…`；不推翻判定）。