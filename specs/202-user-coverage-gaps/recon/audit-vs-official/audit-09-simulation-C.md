# 核对 C · 废弃链与枚举取值 —— 域 09-simulation

**范围**：`scripts/sw_simulation.py` · `scripts/sw_simulation_loads.py` · `scripts/sw_topology.py`（三个文件均存在）
**只做核对 C**：① 官方标 Obsolete 的成员；② 字面量当枚举传时该值是否为官方枚举成员。

**官方源（本路实际读到的）**
- `C:\swapi\enums\swLoadAddinError_e.md` · `C:\swapi\types\*\*.md`
- `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\`（34 页，含 `members_2013/2014/2016/2021.html`）
- `C:\cworks_vb6\CosmosWorksLib~*.html`（SOLIDWORKS Simulation Type Library 官方 VB6 CHM 解包 —— 本仓 `sw_simulation.py` 自己也引它作 `swsUnit_e` 的出处）
- `C:\topo_en\`（官方 `otsimtopology.chm` 解包，11 个教程页）

★ `C:\swapi\enums\` **没有**任何 `sws*_e` 枚举页（cosworks 不在该源内）；sws 枚举的官方原页在 `C:\cworks_vb6\`。

---

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_simulation_loads.py`：`return _check(manager, "AddForce", 3, int(force_type), entities, ref_geom)`<br>`scripts/sw_simulation_loads.py`：`manager, "AddForce", 3, SWS_FORCE_TYPES["torque"], entities, ref_geom)`<br>`scripts/sw_simulation.py`：`manager, "AddForce", int(force_type), entities,` | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\ICWLoadsAndRestraintsManager~AddForce.html`：`<font color="red">Obsolete. Superseded by <a href="...AddForce2.html">ICWLoadsAndRestraintsManager::AddForce2</a>.</font>`<br>同目录 `members_2021.html` 成员表：`AddForce` / `Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddForce2` · `AddForce2` / `Obsolete. Superseded by ICWloadsAndRestraintsManager::AddForce3`（`members_2013/2014/2016` 同样两行） | 我们三处 COM 调用打的是 **`AddForce`**；官方把 `AddForce` 标为 **Obsolete**，并点名后继为 `AddForce2`，而 `AddForce2` 本身也被标 Obsolete、后继为 `AddForce3`。**我们从未调用 `AddForce2`/`AddForce3`**（只在 `_REFGEOM_POSITIONS` / `_ERRORCODE_MEMBERS` 表里出现过名字，无 COM 调用）。 | 高 |
| 2 | `scripts/sw_simulation.py`：`def default_element_size_and_tolerance(study, units: int = -1) -> tuple[float, float]:`<br>`scripts/sw_simulation.py`：`def mesh_size_report(study, units: int = -1) -> dict[str, Any]:`<br>同文件把该参的枚举标成：`#: ``swsUnit_e`` —— 与 VB6 CHM 的 ``CosmosWorksLib~swsUnit_e`` 页逐条一致。` | `C:\cworks_vb6\CosmosWorksLib~swsUnit_e.html` 枚举表（**全页只有这 3 个成员**）：<br>`swsUnitEnglish \| 1`<br>`swsUnitMetric \| 2`<br>`swsUnitSI \| 0` | 我们把 **`-1`** 当 `swsUnit_e` 的值传（两处默认实参）；官方 `swsUnit_e` 只有 `0 / 1 / 2` 三个成员，**`-1` 不在其中**。<br>⚠ 官方 `CWStudy~CreateMesh` / `CWMesh~GetDefaultElementSizeAndTolerance` 两页的 `NUnits` 形参**未写它属于哪个枚举**（按铁律 5：查不到就说查不到）——「`units` 就是 `swsUnit_e`」这一句是我们自己在本文件里写的，不是官方页写的。 | 中 |
| 3 | `scripts/sw_simulation.py`：`get_com_member(model, "SetMaterialPropertyName2", "", database, material_name)` 紧接 `return get_com_member(model, "MaterialIdName")` | `C:\swapi\types\IModelDoc2\MaterialIdName.md`：`Obsolete. Superseded by [[IPartDoc::GetMaterialPropertyName2]] and [[IPartDoc::SetMaterialPropertyName2]].`<br>**对照源** `C:\swapi\types\IPartDoc\MaterialIdName.md`：`Gets or sets the material name.`（**没有** Obsolete 标注） | 同一个成员名 `MaterialIdName`，官方**两页标注不一致**：`IModelDoc2` 页标 Obsolete（点名后继 `GetMaterialPropertyName2` / `SetMaterialPropertyName2`），`IPartDoc` 页未标。**记成「两源不一致」，不判谁对**——我们的代码用迟到绑定按裸名调用，本文件没有写明 `model` 落到哪个接口（函数 docstring 写「给零件赋材料」）。 | 中 |

---

## 本路核过但**没有**分歧的项（只列名，不展开）

**枚举取值全部逐条对齐**（27 组官方枚举表 vs 我们代码里的表/字面量）：
`swLoadAddinError_e`（`C:\swapi\enums`）、`swsUnit_e`、`swsForceType_e`、`swsForceUnit_e`、`swsRestraintType_e`、`swsMeshType_e`、`swsAnalysisStudyType_e`（含「10/11/12 = Reserved1..3」与「Topology_Static = 13」）、`swsPressureType_e`、`swsRadiationType_e`、`swsSpringSubType_e`、`swsTopologyStudyGoalType_e`、`swsTopologyStudyMassConstraintOption_e`、`swsTopologyPreservedRegionOption_e`、`swsTopologyIterationOption_e`、`swsTopologyDemoldDirectionOption_e`、`swsTopologyActivationOption_e`、`swsTopologyStudyConstraintComparator_e`、`swsTopologySymmetryControlOption_e`、`swsTopologyStudyError_e`（7 / 18 / 19 三处引用全中）、`swsStudyError_e`、`swsStudyMeshError_e`、`swsMassUnits_e`、`swsLinearUnit_e`、`swsBoltType_e`、`swsEdgeWeldConnectorTypes_e`、`swsRemoteLoadType_e`，另交叉核了 `swsNForceType_e`（AddForce 官方页 `Parameters` 写的是 `swsForceType_e`，与我们取的一致）。

**字面量 0 是合法成员的**：`add_distributed_mass(units=0)` · `add_prescribed_displacement(length_unit=0)` · `add_bolt_connector(bolt_type=0)` · `add_edge_weld_connector(weld_style=0)` · `add_spring_connector(sub_type=0)` · `add_radiation(radiation_type=0)` · `create_mesh_report(units=0)` · `run_topology_study(units=0)` · `create_stress_constraint(comparator=0)` · `create_demold_control(direction=0)` · `apply_fixed_restraint(restraint_type=0)`。

**Obsolete 全量扫描无其它命中**：`SWhelp\cosworks\` 34 页全文扫 `Obsolete` 只有 `AddForce` / `AddForce2` 两处；`C:\cworks_vb6\` 3000 页全文扫 `Obsolete` **0 命中**；`C:\swapi\types\` 里我们调用到的 40 个成员名逐个扫 `Obsolete`，只有 `MaterialIdName`（第 3 条）落在我们实际调用的接口上（`IComponent2::GetBodies2` / `IBomTableAnnotation::GetComponents` / `ICustomPropertyManager::GetType` / `IComponent2::Name` / `IView::Name` 的 Obsolete 属于别的接口，不是我们调的）。

**查不到、故不报**：官方无 `ICWTopology*` 的 Obsolete 标注（`C:\cworks_vb6` 与 `SWhelp\cosworks` 均无）；官方 `CWStudy~CreateMesh` / `CWMesh~GetDefaultElementSizeAndTolerance` 的 `NUnits` 未标注所属枚举；`C:\swapi\enums\` 不收录任何 `sws*` 枚举。

---

**核了 60 处**（27 组官方枚举表 + 33 处成员/废弃链扫描：三个文件共 101 个 COM 成员名对 `C:\swapi\types` 与 `SWhelp\cosworks`、两个文件共 40 行字面量对官方枚举表）· **报了 3 条** · **置信度为高的是第 1 条**（`AddForce` 被官方标 Obsolete）。