# 09-simulation · 核对 B（前置与 mark）· audit-09-simulation-B

**范围**：`scripts/sw_simulation.py` · `scripts/sw_simulation_loads.py` · `scripts/sw_topology.py`
**只做**：核对 B —— 官方 Remarks / 官方例子的**前置**（先选什么、mark 几、调用序）与我们代码实际做没做那一步。
**纪律**：给不出两段可搜索原文的一律不写；不下结论、不给建议；宁少勿滥。

**官方源（本轮实际读到的）**
- `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~<成员>.html`（正文以 `\u003c` JSON 转义嵌在 script 标签里）
- `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\Analyze_Part_Example_VB.htm`
- `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`
- `C:\topo_en\t_defining_preserved_region.htm` / `t_defining_quarter_symmetry_control.htm` / `t_defining_de-mold_manufacturing.htm`
- `C:\swapi\types\ISldWorks\GetAddInObject.md` / `LoadAddIn.md`
- ★ `C:\swapi\types\` **无任何 `ICW*` / cosworks 接口目录**（已递归列过：只有 `ICosmeticThreadFeatureData` 等 6 个含 `CW/Cos` 的目录，无一个是 cosworks）⇒ cosworks 一族的 Signature/Remarks 只能取 CHM 册。

---

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_topology.py` · `create_preserved_region`：<br>`    def _configure():`<br>`        if option is not None:`<br>`            get_com_member(control, "SetIncludeRegionDepth2", True)`<br>`        return control` | `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`：<br>`CWTopoPreservedRegionObj.BeginEdit`<br>`Set DispatchObj1 = Part.SelectionManager.GetSelectedObject6(1, -1)`<br>`Set DispatchObj2 = Part.SelectionManager.GetSelectedObject6(2, -1)`<br>`DispArrayForPreservedRegion = Array(DispatchObj1, DispatchObj2)`<br>`ErrorCodeObj =`<br>`CWTopoPreservedRegionObj.SelectFaces((DispArrayForPreservedRegion))`<br>`If ErrorCodeObj <> 0 Then ErrorMsg swApp, "Failed: CWTopoPreservedRegionObj faces could not be selected"` | 官方在 `BeginEdit` 内**先**把保留面装成 `DispArray` 传给 `SelectFaces`，**再**设 `SetIncludeRegionDepth2`；我们这 4 行里只有 `SetIncludeRegionDepth2`，`SelectFaces` 一次都没调 —— 函数体既不读选区、也不传面。（函数 docstring 写「⚑ 调用方须**先选好要保留的面**再调本函数」，但正文没有任何取选区的语句） | 高 |
| 2 | `scripts/sw_topology.py` · `create_symmetry_control`：<br>`    def _configure():`<br>`        get_com_member(control, "SelectSymmetryType", int(symmetry_type))`<br>`        return control` | `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`：<br>`CWTopoSymmetryControlObj.BeginEdit`<br>`Set sDispObjPlane1 = Part.SelectionManager.GetSelectedObject6(1, -1)`<br>`CWTopoSymmetryControlObj.SelectSymmetryType 0`<br>`CWTopoSymmetryControlObj.SelectFirstSymmetryPlane sDispObjPlane1`<br>（1/4 对称处另有 `CWTopoSymmetryControlObj.SelectSecondSymmetryPlane sDispObjPlane2`） | 官方调用序是 `SelectSymmetryType` **紧接** `SelectFirstSymmetryPlane <plane>`（1/4 对称再加 `SelectSecondSymmetryPlane`）；我们只调 `SelectSymmetryType`，没有任何「取平面并交给控制」的调用。官方教程侧同一步骤：`C:\topo_en\t_defining_quarter_symmetry_control.htm` —— `Click in Select First Symmetry Plane, and from the brake rotor flyout FeatureManager design tree, select First Symmetry.` | 高 |
| 3 | `scripts/sw_topology.py` · `create_demold_control`：<br>`    def _configure():`<br>`        get_com_member(control, "SelectDemoldDirection", int(direction))`<br>`        return control` | `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`：<br>`CWTopoDemoldControlObj.SelectDemoldDirection 0`<br>`CWTopoDemoldControlObj.SetAutoDetermineCentralMidPlane2 False`<br>`CWTopoDemoldControlObj.SelectPlaneForDirection sDispObjPlane`<br>（另一形态）`CWTopoDemoldControlObj.SelectDemoldDirection 1`<br>`CWTopoDemoldControlObj.SelectEdgeForPullDirection sDispObjEdge` | 官方在 `SelectDemoldDirection` 之后**必须**再交出方向几何（`SelectPlaneForDirection` 或 `SelectEdgeForPullDirection`）；我们这 3 行只有 `SelectDemoldDirection`，没有把面/边交给控制的那一步。官方教程侧：`C:\topo_en\t_defining_de-mold_manufacturing.htm` —— `The preselected edge appears in Select edge to define the direction.` | 高 |
| 4 | `scripts/sw_topology.py` · `create_stress_constraint`（同形还有 `create_mass_constraint` / `create_factor_of_safety_constraint` / `create_preserved_region` / `create_symmetry_control` / `create_demold_control` / `create_thickness_control`）：<br>`    manager = get_topology_study_manager(study)`<br>`    constraint = get_com_member(manager, "CreateStressConstraint", out_i4())`<br>`    if constraint is None:`<br>`        raise RuntimeError("CreateStressConstraint 未返回对象")` | `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`：<br>`' Create topology stress constraint`<br>`CWTopologyStudyManagerObj.BeginEdit`<br>`Set CWTopoStressConstraintObj =`<br>`CWTopologyStudyManagerObj.CreateStressConstraint(ErrorCodeObj)`<br>`...`<br>`ErrorCodeObj = CWTopologyStudyManagerObj.EndEdit()`<br>（质量约束处同形：`CWTopologyStudyManagerObj.BeginEdit` → `GetMassConstraint("Mass Constraint 1", ErrorCodeObj)` → … → `ErrorCodeObj = CWTopologyStudyManagerObj.EndEdit()`） | 官方把 `Create*` 放在**管理器层** `CWTopologyStudyManagerObj.BeginEdit` … `EndEdit()` 之间；这 7 个独立 `create_*` 只在**约束对象**上开事务（`return _edit(constraint, _configure)`），管理器层的事务括号一次都没调。（同文件里的 `set_topology_goal` 走的是 `_edit(manager, _build)`，即有管理器层括号 —— 同一模块两种形态） | 高 |
| 5 | `scripts/sw_simulation.py` · `get_cosmosworks`：<br>`    cosmos = get_com_member(addin, "CosmosWorks")` | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\Analyze_Part_Example_VB.htm`：<br>`Set CWObject = SwApp. GetAddInObject ("SldWorks.Simulation")`<br>`Set COSMOSWORKS = CWObject. COSMOSWORKS `<br>另 `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`：<br>`Set CWAddinCallBack = swApp.GetAddInObject("CosmosWorks.CosmosWorks")`<br>`Set COSMOSWORKS = CWAddinCallBack.COSMOSWORKS` | 官方两个例子的调用序第 2 步都写**全大写** `COSMOSWORKS`；我们写 `CosmosWorks`（驼峰），与两处官方原文都不一致。我们 `sw_simulation.py` 的来源块自述「本反射清单里该成员的 getter 名为 `get_CosmosWorks`，即 COM 属性名是 `CosmosWorks`」并把全大写写法归给外部项目 —— 官方两例与之相反。（`GetAddInObject` 的 ProgID 一侧**不构成**分歧：`Analyze_Part_Example_VB.htm` 用的正是 `"SldWorks.Simulation"`，与我们常量逐字相同） | 中 |

---

**查不到、故不报（铁律 5）**
- `CreateNewStudy2` / `CreateNewStudy`：CHM cosworks 册**没有**这两个方法的页（`ICWLoadsAndRestraintsManager~*` 之外无 `ICWStudyManager~*` 页）⇒ 我们 `create_static_study` 的降级分支与官方**无原文可比**，不写。
- `ForceBeginEdit` / `ForceEndEdit`：官方两个例子里出现的是 `CWPressure. PressureBeginEdit` / `PressureEndEdit`（压力族），**没有** `Force*Edit` 的任何官方原文 ⇒ `apply_normal_force` 的这一对调用**查不到**，不写。
- `AddRestraint` / `AddForce` / `AddPressure` 第 3 参（`RefGeom`）传空 Dispatch 与官方 `Nothing` / `Pass null` 的差异：`ICWLoadsAndRestraintsManager~AddPressure.html` 的 Remarks 明写 `If you pass a Dispatch pointer, it is ignored.` ⇒ **官方文本允许**该形态，**不构成**分歧，不写。
- `AddCyclicSymmetryRestraint` 的 `This method is valid only for static and nonlinear studies.`（该页 Remarks 原文）：官方给的是**算例类型有效性**约束，我们 `add_cyclic_symmetry_restraint` 是薄封装、类型判定归调用方，**无可并排的两段代码原文**，不写。
- `GetLoadsAndRestraints` 页 Remarks 的前置 `Before calling this method, call ICWLoadsAndRestraintsManager::Count to get a valid value for NIndex.`：我们 `sw_simulation_loads.py::collect_loads_evidence` 是 `count = int(get_com_member(manager, "Count") or 0)` 先取 Count 再循环、`sw_simulation.py::collect_study_evidence` 同形 ⇒ **已做该前置**，不写。

---

**核了几处**：59 处（`sw_simulation.py` 20 · `sw_simulation_loads.py` 25 个 `Add*`/读取成员逐页比对 Syntax+Parameters+Remarks · `sw_topology.py` 14 个 `create_*`/事务/回读入口对官方示例调用序）
**报了几条**：5 条
**置信度为高的**：#1 · #2 · #3 · #4（#5 为中）