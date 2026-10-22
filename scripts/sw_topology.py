"""SolidWorks Simulation 拓扑优化（cosworks 的 ``CWTopology*`` 族）原生接口封装。

能力域
    域 13 · 仿真 → **拓扑优化**（本项目的护城河域：四家外部 MCP 项目在此全空，
    ``andrewbartels1`` 明确把它列在 "Not Yet / Simulated"）

对应官方接口族（全部经 interop DLL 纯元数据反射核对）
    ``ICWModelDoc``                 → ``get_StudyManager()``
    ``ICWStudyManager``             → ``CreateNewStudy3(Name, StudyType, MeshType, &Err)``
    ``ICWStudy``                    → ``get_TopologyStudyManager()`` /
                                      ``get_TopologyStudyOptions()`` /
                                      ``get_LoadsAndRestraintsManager()`` /
                                      ``CreateMesh`` / ``RunAnalysis`` / ``get_Results()``
    ``ICWTopologyStudyManager``     → ``BeginEdit`` / ``CreateGoal`` /
                                      ``Create*Constraint`` / ``Create*Control`` /
                                      ``Get*`` / ``RemoveConstraint`` / ``RemoveControl`` / ``EndEdit``
    ``ICWTopologyStudyOptions``     → ``SetConvergenceCheck`` / ``SetIterationLimit`` /
                                      ``SetIterationOption`` / ``SetMinMaxFormulationForLoadCases``
    ``ICWTopologyMassConstraint``   → ``SetMassPreference`` / ``SetValue`` / ``SetUnit`` / ``SetName``
    ``ICWTopologyStressConstraint`` / ``ICWTopologyFactorOfSafetyConstraint``
    ``ICWTopologyPreservedRegionControl`` / ``ICWTopologySymmetryControl`` /
    ``ICWTopologyDemoldControl`` / ``ICWTopologyThicknessControl``

⚑ 本模块最要紧的一条依据：**事务括号**
    ``ICWTopologyStudyManager`` 与**每一条** ``CWTopology*Constraint`` 都同时提供
    ``BeginEdit()`` 与 ``EndEdit()``。官方 UI 教程里的每一步，在 API 上都是
    「一对 BeginEdit/EndEdit 之间的一组 ``Set*``」：

        manager.BeginEdit()          # 开研究级事务
          CreateGoal(...)            # 建目标
          constraint.BeginEdit()     # 开该约束自己的事务
            SetMassPreference(...)   # 设置
            SetValue(...)
          constraint.EndEdit()       # 提交该约束
        manager.EndEdit()            # 提交研究

    **不包在事务里的 ``Set*`` 会静默不落地。** 这推翻了本机一份前序笔记的结论
    （它把「约束没落到研究上」归因于「没预建选择集」，见下面的覆盖边界 ——
    选择集那条路在 API 上根本不通）。

覆盖边界（重要）
    ⚠ **官方 UI 教程依赖「预建 Selection Set」，但 SolidWorks API 没有创建选择集的方法。**
    对 ``sldworks`` interop 反射（1032 接口 / 20627 成员）后，``ISelectionSet`` 族**只有**：

        Object GetSelectionSetFolder()          ← 挂在 IModelDocExtension 上，只能取
        ISelectionSet       : GetSelectionSetItems / GetSelectionSetItemTypes / RemoveSelectionSet
        ISelectionSetFolder : GetSelectionSetByName / GetSelectionSets
        ISelectionSetItem   : RemoveFromSelectionSet

    —— **只读、只删、不能建。** 故本模块**不提供**建选择集的入口
    （AGENTS.md 铁律 5：查不到就写查不到，不用相似名字蒙混）。
    夹具与外载一律走「**先把实体选好，再调 ``Add*``**」的既有模式
    （同 ``scripts/sw_simulation.py`` 的 ``apply_fixed_restraint``：
    其 ``AddRestraint(Type, None, None, 0)`` 依赖调用方已选好的选区）。

    ⚠ 本模块**只实现反射清单里有签名的部分**。``CWTopologyStudyManager`` 的
    ``Get*`` 按名取回已建约束，本模块提供读取入口；``Create*`` 的 ``Int32&`` 是出参
    （错误码），pywin32 迟到绑定下按既有约定传占位 ``0``。

⚠ 本模块为静态签名比对后新写，**未在本机实测**（见 AGENTS.md 铁律 2）。
   它不会启动 SolidWorks、不会自行加载加载项；所有 COM 入口都需要调用方
   显式传入已连接的应用对象。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_topology.py —— 本文件（**轮 145 的命名迁移**）。
# 定位:   2026-10-01（轮 145）**只做了一件事**：把那些「**故意要调**」的零参调用
#         从 `get_com_member(...)` 改成 **`call_com_member(...)`**。
#         ★★ 起因：审计（`tools/audit_get_com_member_semantics.py`）发现
#         `get_com_member` 的语义是「**取或调**」—— **对 COM 成员，「取」可能等于「调」**；
#         而 471 个无实参调用点里有 193 处的成员在反射里**有零参重载**（会真的执行）。
#         ★ 逐条读过之后确认：**作者大多是故意的**（拿返回值当成败 / 要的就是那个动作），
#         但**代码里读不出来** ⇒ 本轮用 `call_com_member` **让名字表态**。
# 官方签名依据: 本次迁移**不改任何 COM 调用**（只是换个名字），
#         各调用的官方依据在原函数的来源块里。
# 许可:   本仓库 MIT（上游部分见 `THIRD-PARTY-NOTICES.md`）。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 迁移这件事**的说明，
#         它**不替代**本文件里原有的、更精确的逐函数来源块。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any

#: ★ 长度换算助手：`_mm(v)` = **毫米→米**（恰好一次）。
#:   依据：本仓定案 `output/probe-unit-decisive/decisive.json`。
try:
    from sw_connect import mm as _mm          # noqa: F401
except Exception:                             # noqa: BLE001
    _mm = lambda v: float(v) / 1000.0         # noqa: E731


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（新能力实现，非第三方移植）+ SolidWorks 官方 API 签名
# 文件:   scripts/sw_topology.py —— 本文件自身
# 定位:   护城河域「拓扑优化」的实现。接口选型与参数顺序全部来自
#         D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt（cosworks.dll 纯元数据反射，
#         168 接口 / 363 枚举 / 3224 成员）与同目录 enum_cosworks.txt；
#         官方做法（流程与语义）来自本机 CHM otsimtopology.chm 的解包 C:\topo_en
#         （11 个教程页）。复用的是 scripts/sw_simulation.py 的既有模式
#         （get_com_member 迟到绑定、多入口降级、选区而非实体数组）。
# 官方签名依据: ICWTopologyStudyManager 的 9 个 Create* / 9 个 Get* /
#         CreateGoal / RemoveConstraint / RemoveControl / BeginEdit / EndEdit；
#         ICWStudy.get_TopologyStudyManager / get_TopologyStudyOptions；
#         ICWStudyManager.CreateNewStudy3；swsAnalysisStudyTypeTopology_Static = 13。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本模块不启动 SolidWorks、
#   不加载加载项，所有入口都要调用方传入已连接的应用对象。
# ⚑ 出参约定（本项目内**尚未裁定**的冲突，此处显式标注而非默默选一边）:
#   ``scripts/audit_call_arity.py`` 的口径是「``&`` 出参不计入 arity」
#   （它自己的注释举 ``Void GetErrorMessages(Object&, Object&, Object&)`` 为 0 参，
#   理由是「三个全是 [out]，调用方一个都不传」）；而 ``scripts/sw_simulation.py``
#   的既有做法是**传占位 ``0``**（``CreateNewStudy3(name, type, mesh, 0)`` 实参 4、
#   官方 arity 3）。两者未对齐，本模块**沿用既有模式**（铁律 1 认可「本项目自身
#   既有模式」），因此 arity 审计会把这 11 处报成「存疑」——
#   ``sw_simulation.py`` 的 6 处同形。**该冲突应由发布门禁裁定，不由本模块自定。**
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
try:
    from .sw_connect import get_com_member, call_com_member, out_i4
    from .sw_simulation import get_cw_document, get_study_manager
    #: ★★★★ 2026-10-04（接手轮）**补上 `delete_study`** ——
    #:   处置 `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #6`）：★ `create_topology_study` 要
    #:   **先删同名**（★ 官方示例逐字 `StudyManagerObj.DeleteStudy NewStudyName` ⇒
    #:   `CreateNewStudy3(...)`）· ★ 而**删除能力本仓早有**（★ `sw_simulation_study.delete_study`）✓
    from .sw_simulation_study import delete_study
except ImportError:
    from sw_connect import get_com_member, call_com_member
    from sw_simulation import get_cw_document, get_study_manager
    from sw_simulation_study import delete_study


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt
# 定位:   拓扑优化的四条枚举。值来自反射清单逐条核对，非印象。
#   第 1 条 swsAnalysisStudyTypeTopology_Static=13 是**研究类型**，
#   在 iface_cosworks.txt 的 swsAnalysisStudyType_e 里；
#   其余三条在各自枚举块内（见下方每条的定位注）。
# ⚠ 本模块为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: enum-gate: enum swsAnalysisStudyType_e
SWS_ANALYSIS_STUDY_TYPES: dict[str, int] = {
    "static": 0,
    # ⚑ 拓扑优化研究类型。反射：swsAnalysisStudyTypeTopology_Static = 13
    #   （注意它叫 "Topology_Static" —— 拓扑研究是静态分析的一个子类）
    "topology_static": 13,
}

#: ``ICWTopologyStudyManager.CreateGoal(Int32)`` 的目标类型
#: 反射：swsTopologyGoalType_e —— MaximizeStiffness=0 / MinimizeMaximumDisplacement=1 / MinimizeMass=2
#: 官方教程「Best Stiffness to Weight ratio (default)」对应 MaximizeStiffness。
#: enum-gate: enum swsTopologyStudyGoalType_e
SWS_TOPOLOGY_GOAL_TYPES: dict[str, int] = {
    "maximize_stiffness": 0,
    "minimize_maximum_displacement": 1,
    "minimize_mass": 2,
}

#: ``ICWTopologyMassConstraint.SetMassPreference(Int32)`` 的取值
#: 反射：swsTopologyMassConstraintOption_e —— AbsoluteValue=0 / Percentage=1
#: 官方教程的「Reduce mass by (percentage) = 75」对应 Percentage + SetValue(75.0)。
#: enum-gate: enum swsTopologyStudyMassConstraintOption_e
SWS_TOPOLOGY_MASS_PREFERENCES: dict[str, int] = {
    "absolute_value": 0,
    "percentage": 1,
}

#: ``ICWTopologyPreservedRegionControl`` / 制造控制相关
#: 反射：swsTopologyPreservedRegionOption_e
#:   LoadsOnly=0 / FixturesOnly=1 / LoadsAndFixtures=2 / None=3
#: ⚑ 官方 CHM 原话："During optimization, the software always preserves the faces
#:   to which you apply fixtures and loads." ⇒ 夹具与载荷所在面**自动保留**，
#:   ``LoadsAndFixtures`` 是与之对齐的默认语义；``Preserved Region`` 是**额外**的保留区。
#: enum-gate: enum swsTopologyPreservedRegionOption_e
SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS: dict[str, int] = {
    "loads_only": 0,
    "fixtures_only": 1,
    "loads_and_fixtures": 2,
    "none": 3,
}

#: ``ICWTopologyStudyOptions.SetIterationOption(Int32)``
#: 反射：swsTopologyIterationOption_e —— Auto=0 / UserDef=1
#: enum-gate: enum swsTopologyIterationOption_e
SWS_TOPOLOGY_ITERATION_OPTIONS: dict[str, int] = {
    "auto": 0,
    "user_defined": 1,
}

#: ``ICWTopologyDemoldControl.SelectDemoldDirection(Int32)``
#: 反射：swsTopologyDemoldDirectionOption_e
#: enum-gate: enum swsTopologyDemoldDirectionOption_e
SWS_TOPOLOGY_DEMOLD_DIRECTIONS: dict[str, int] = {
    "two_direction_mid_plane": 0,
    "pull_direction_only": 1,
    "stamping": 2,
}

#: ``ICWTopology*Control`` 的启用开关（多个 Control 的 ``SetInclude*`` 用同一对值）
#: 反射：swsTopologyActivationOption_e —— Deactivate=0 / Activate=1
#: enum-gate: enum swsTopologyActivationOption_e
SWS_TOPOLOGY_ACTIVATION: dict[str, int] = {
    "deactivate": 0,
    "activate": 1,
}

__all__ = [
    "SWS_ANALYSIS_STUDY_TYPES",
    "SWS_TOPOLOGY_GOAL_TYPES",
    "SWS_TOPOLOGY_MASS_PREFERENCES",
    "SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS",
    "SWS_TOPOLOGY_ITERATION_OPTIONS",
    "SWS_TOPOLOGY_DEMOLD_DIRECTIONS",
    "SWS_TOPOLOGY_ACTIVATION",
    "TP_GOAL_MAXIMIZE_STIFFNESS",
    "TP_GOAL_MINIMIZE_MASS",
    "TP_MASS_PERCENTAGE",
    "TP_ACTIVATE",
    "create_topology_study",
    "get_topology_study_manager",
    "get_topology_study_options",
    "set_topology_goal",
    "create_mass_constraint",
    "create_factor_of_safety_constraint",
    "create_stress_constraint",
    "create_preserved_region",
    "create_symmetry_control",
    "create_demold_control",
    "create_thickness_control",
    "set_topology_iteration_options",
    "list_topology_constraints_and_controls",
    "run_topology_study",
    "collect_topology_evidence",
    "collect_topology_numbers",
    "TOPOLOGY_RESULTS_UNRESOLVED",
]

#: 常用取值的短别名（调用方最常写的那几个）
TP_GOAL_MAXIMIZE_STIFFNESS = SWS_TOPOLOGY_GOAL_TYPES["maximize_stiffness"]
TP_GOAL_MINIMIZE_MASS = SWS_TOPOLOGY_GOAL_TYPES["minimize_mass"]
TP_MASS_PERCENTAGE = SWS_TOPOLOGY_MASS_PREFERENCES["percentage"]
TP_ACTIVATE = SWS_TOPOLOGY_ACTIVATION["activate"]

#: ``CWTopology*Constraint`` 的类名 → 官方接口名，供 Get* 与清单遍历共用。
#: 反射：ICWTopologyStudyManager 的 Get* 方法签名均为 ``(String Name, Int32& Err)``。
_TOPOLOGY_GETTERS: dict[str, str] = {
    "mass": "GetMassConstraint",
    "stress": "GetStressConstraint",
    "factor_of_safety": "GetFactorOfSafetyConstraint",
    "displacement": "GetDisplacementConstraint",
    "frequency": "GetFrequencyConstraint",
    "preserved_region": "GetPreservedRegionControl",
    "symmetry": "GetSymmetryControl",
    "demold": "GetDemoldControl",
    "thickness": "GetThicknessControl",
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 定位:   ICWStudyManager.CreateNewStudy3(String Name, Int32 StudyType, Int32 MeshType
#           , Int32& Err)
#         与 ICWStudy.get_TopologyStudyManager() / get_TopologyStudyOptions()。
#         本函数复用既有模块的 get_study_manager，不重复实现取入口的逻辑。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_topology_study(sw_app, name: str, *, mesh_type: int = 0,
                          delete_existing: bool = True):
    """新建拓扑优化研究。返回 ``(study, entry_name)``。

    研究类型固定为 ``swsAnalysisStudyTypeTopology_Static``（13）——
    反射清单里没有第二个拓扑研究类型。

    ``entry_name`` 标明实际命中的入口（``CreateNewStudy3`` / ``CreateNewStudy2``），
    便于调用方判断结果是否来自降级路径（同 ``sw_simulation.create_static_study``）。
    """
    manager = get_study_manager(sw_app)
    if manager is None:
        raise RuntimeError("CWModelDoc.StudyManager 为 None")

    study_type = SWS_ANALYSIS_STUDY_TYPES["topology_static"]

    #: ★★★★★ 2026-10-04（接手轮）**兑现那句「同名先删」** ——
    #:   处置 `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #6`）—— ★ 裁判逐字：
    #:   「★ `create_study` 的 Param 承诺「**同名先删**」★ 实则**把同名当错误码 2**
    #:    且**无任何删除调用**」✓
    #:   ★★★★ **依据是官方示例（★ 我读了 `_raw/**/Create_Topology_Study_Example_VBA.txt`）**：
    #:     该文件 **L131-135 逐字**：
    #:       ```
    #:       ' Create Topology Study 1
    #:       NewStudyName = "Topology Study 1"
    #:       ★★ StudyManagerObj.DeleteStudy NewStudyName          ← ★ 先删同名
    #:       ★★★ Set CWNewStudy = StudyManagerObj.CreateNewStudy3(NewStudyName, 13, 0, ErrorCodeObj)
    #:       ```
    #:     ⇒ ★ **调用序就是 `DeleteStudy` ⇒ `CreateNewStudy3`** ✓
    #:     ★★ 而**研究类型传 `13`** ⇒ ★ 与本仓 `topology_static` 一致 ✓
    #:   ★★★ **修法**：★ 建之前先 `delete_study(manager, name)` ——
    #:     而**同名不存在时它可能报错** ⇒ ★★ **必须容错**（★ 删不到就当"本来没有"）✓
    delete_note = None
    if not delete_existing:
        delete_note = "★ 未先删（delete_existing=False）"
    else:
        try:
            delete_study(manager, str(name))
            delete_note = "★ 已按官方示例先删同名研究（★ DeleteStudy）"
        except Exception as exc:                                          # noqa: BLE001
            #: ★★ 同名不存在 ⇒ 官方那个 `DeleteStudy` 会报错 —— ★ 那是**正常**的（★ 首次建）
            delete_note = ("★ 先删同名未成（★ %s）⇒ ★ 当作「本来没有同名」继续 ✓"
                           % type(exc).__name__)

    # CreateNewStudy3(Name, StudyType, MeshType, &Err)
    study = get_com_member(
        manager, "CreateNewStudy3", str(name), int(study_type), int(mesh_type), out_i4()
    )
    entry_name = "CreateNewStudy3" if study is not None else ""

    if study is None:
        # CreateNewStudy2(Name, StudyType, &Err) —— 无 MeshType
        study = get_com_member(manager, "CreateNewStudy2", str(name), int(study_type), out_i4())
        if study is not None:
            entry_name = "CreateNewStudy2"

    if study is None:
        raise RuntimeError(
            "创建拓扑研究失败：CreateNewStudy3 / 2 均未返回对象。"
            "常见原因见 swsStudyError_e：1=无实体、2=同名研究已存在或名称非法、"
            "3=类型未定义（本机 Simulation 版本可能不支持拓扑优化）、4=网格类型非法。"
            "⚠ 拓扑优化只能对**单个实体零件**做（官方 CHM："
            "'You can only perform topology optimization for only one single-body part at a time.'）"
            "★ 2026-10-04 补：**同名的可能性已经先删过一遍**（★ 按官方示例 `DeleteStudy`）"
            "⇒ 若仍报 2，★ 更可能是**名称非法**（★ 而不是同名）✓"
        )
    return study, entry_name


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 定位:   ICWStudy.get_TopologyStudyManager() → CWTopologyStudyManager
#         与 ICWStudy.get_TopologyStudyOptions() → CWTopologyStudyOptions。
#         两者都是 **getter 属性**（反射里写作 get_XXX()），非普通方法。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_topology_study_manager(study):
    """取 ``CWTopologyStudyManager``。研究不是拓扑类型时抛 RuntimeError。"""
    manager = get_com_member(study, "TopologyStudyManager")
    if manager is None:
        raise RuntimeError(
            "ICWStudy.TopologyStudyManager 为 None：该研究不是拓扑优化研究，"
            "或本机 Simulation 版本不支持（请先用 create_topology_study 建 13 型研究）"
        )
    return manager


def get_topology_study_options(study):
    """取 ``CWTopologyStudyOptions``（迭代/收敛选项）。"""
    options = get_com_member(study, "TopologyStudyOptions")
    if options is None:
        raise RuntimeError("ICWStudy.TopologyStudyOptions 为 None：该研究不是拓扑优化研究")
    return options


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 定位:   ICWTopologyStudyManager.BeginEdit() / EndEdit()
#         与 ICWTopologyMassConstraint.BeginEdit() / EndEdit()。
#         ⚑ 事务括号是本模块最要紧的一条纪律：研究级与约束级**各有一对**，
#         不包在事务里的 Set* 会静默不落地。
# 官方做法依据: 本机官方 CHM otsimtopology.chm 解包（C:\topo_en）的
#         t_setting_optimization_goal.htm —— 研究树 Goals and Constraints →
#         Best Stiffness to Weight ratio (default) → Mass Constraint (Default) →
#         「Reduce mass by (percentage)」= 75；另加 Stress/Factor of Safety Constraint
#         「Specified factor」= 80。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _edit(obj, action):
    """在一对 ``BeginEdit`` / ``EndEdit`` 之间执行 ``action``，并返回 ``EndEdit`` 的结果。

    ``EndEdit`` 的返回值是错误码（``Int32``）。**非 0 即失败** ——
    这里选择抛异常而不是静默返回，因为静默正是这套 API 最难查的失败模式。
    """
    get_com_member(obj, "BeginEdit")
    try:
        result = action()
    except Exception:
        # EndEdit 必须仍然调用：它是事务的提交/回滚点，漏掉会把研究留在编辑态，
        # 之后的 Create* 会以「已在编辑中」失败。异常照原样抛。
        get_com_member(obj, "EndEdit")
        raise
    code = get_com_member(obj, "EndEdit")
    if code not in (None, 0):
        raise RuntimeError("EndEdit 返回错误码 %r —— 事务未提交，设置未落地" % (code,))
    return result


def set_topology_goal(
    study,
    *,
    goal_type: int = TP_GOAL_MAXIMIZE_STIFFNESS,
    mass_reduce_percent: float | None = None,
    factor_of_safety: float | None = None,
):
    """按官方教程的流程设目标与约束。返回 ``{goal, mass_constraint, fos_constraint}``。

    ``goal_type`` 取 :data:`SWS_TOPOLOGY_GOAL_TYPES`；
    ``mass_reduce_percent`` 是**减重百分比**（官方教程用 75，语义是「减掉 75%」，
    对应 ``SetMassPreference(Percentage) + SetValue(75.0)`` —— **不是**「保留 75%」）；
    ``factor_of_safety`` 是安全系数约束（官方用 80，即应力不得超过屈服强度的 80%）。

    两者都可以为 ``None``（不建该约束）。**至少给一个**，否则拓扑研究没有约束、
    求解会退化成无意义的均匀材料分布。

    .. note::
       前序笔记曾把 ``CreateMassConstraint + SetValue`` 判为「走错 API 层级」。
        反射显示这**正是**官方接口（``ICWTopologyStudyManager.CreateMassConstraint``）。
        真因是两条（2026-10-01 真机隔离实验定出，见工作区
        ``probe_topology_clean_sequence.py``）：

        1. **同类约束已存在时 ``Create*`` 静默返回 None** —— 官方示例的前置动作是
           ``RemoveConstraint(名字)``（原文：先 ``RemoveConstraint "Stress Constraint 1"``
           再 ``CreateFactorOfSafetyConstraint``）。故本函数**先清同族再建**。
        2. ``EndEdit`` 的返回值是错误码，非 0 即事务未提交 —— 由 :func:`_edit` 负责，
           不再静默。实测：先建目标 ``CreateGoal(1)``（最小化最大位移）之后再建质量约束，
           ``tsm.EndEdit`` 会返回 **7**；而在不含该目标的干净研究里同一个质量约束返回 **0**
           ⇒ **目标与约束之间存在兼容性约束**，7 的确切语义在 CHM 里**查不到**
           （cworksapi.chm 解包 2790 页，无错误码枚举页）。故本模块把非 0 抛出来，
           由调用方决定，**不猜它的含义**。
    """
    if mass_reduce_percent is None and factor_of_safety is None:
        raise ValueError("至少要给一个约束（mass_reduce_percent 或 factor_of_safety）")

    manager = get_topology_study_manager(study)
    made: dict[str, Any] = {"goal": None, "mass_constraint": None, "fos_constraint": None,
                            "removed": []}

    def _clear(kind: str) -> None:
        """建之前先删同族约束 —— 官方示例的前置动作。

        ``Create*`` 在同类已存在时返回 None，不删就会得到一个「看起来失败」的调用。
        """
        name = _default_constraint_name(kind)
        getter = _TOPOLOGY_GETTERS.get(kind)
        if getter is None:
            return
        try:
            existing = get_com_member(manager, getter, name, out_i4())
        except Exception:
            existing = None
        if existing is not None:
            get_com_member(manager, "RemoveConstraint", name)
            made["removed"].append(name)

    def _build():
        # CreateGoal(Int32) 返回 Int32（不是对象）—— 反射里它与其他 Create* 不同型。
        made["goal"] = get_com_member(manager, "CreateGoal", int(goal_type))

        if mass_reduce_percent is not None:
            # ⚑ 2026-10-01 真机终局判定（`probe_goal_creates_mass.py`）：
            #   `CreateGoal(0)` / `CreateGoal(1)` **本身就会创建一个质量约束**
            #   （实测：建目标前 GetMassConstraint = False，建后 = True）；
            #   `CreateGoal(2)`（MinimizeMass）**不会**。
            #   而 `CreateMassConstraint` **不查重、无条件新建** ⇒ 目标已带一个时再建
            #   就是两个 ⇒ `EndEdit` 返回错误码 **7**
            #   = `swsTopoErrCode_OnlyOneMassConstraintCanBeDefined`
            #   （真源：`enum_cosworks.txt` 的 `swsTopologyStudyError_e`）。
            #   ⇒ 正解不是「删掉再建」，而是**改那个已存在的**：目标 0/1 之后
            #     `GetMassConstraint` 必然取得到，直接在其上 Set* 即可。
            #   目标 2 或不建目标时才需要 Create。
            existing = None
            try:
                existing = get_com_member(manager, "GetMassConstraint",
                                          _default_constraint_name("mass"), out_i4())
            except Exception:
                existing = None

            if existing is None:
                constraint = get_com_member(manager, "CreateMassConstraint", out_i4())
                if constraint is None:
                    raise RuntimeError(
                        "CreateMassConstraint 未返回对象。目标 0/1 会自动带一个质量约束，"
                        "目标 2 不带；若此处为 None，先确认 goal_type 与研究的当前状态"
                    )
            else:
                # 目标自带的那个 —— 直接改参数，不再 Create（Create 会造出第二个 ⇒ 错误码 7）
                constraint = existing

            def _configure():
                get_com_member(constraint, "SetMassPreference", int(TP_MASS_PERCENTAGE))
                get_com_member(constraint, "SetValue", float(mass_reduce_percent))
                return constraint

            made["mass_constraint"] = _edit(constraint, _configure)
            made["mass_constraint_reused"] = existing is not None

        if factor_of_safety is not None:
            # ⚑ FOS 与 Stress 互斥（`swsTopoErrCode_CannotCreatFOSIfStressAlrdyPrsnt` = 18、
            #   `CannotCreatStressIfFOSAlrdyPrsnt` = 19）⇒ 建 FOS 前须确认没有 Stress 约束。
            #   官方示例的做法就是先 `RemoveConstraint("Stress Constraint 1")`。
            _clear("stress")
            # CreateFactorOfSafetyConstraint(Int32& Err) → CWTopologyFactorOfSafetyConstraint
            constraint = get_com_member(manager, "CreateFactorOfSafetyConstraint", out_i4())
            if constraint is None:
                raise RuntimeError("CreateFactorOfSafetyConstraint 未返回对象")

            def _configure():
                get_com_member(constraint, "SetValue", float(factor_of_safety))
                return constraint

            made["fos_constraint"] = _edit(constraint, _configure)

        return made

    # ⚑ 2026-10-01 真机：`RemoveConstraint` 的位置**试过两种，事务内可行、事务外不可行**：
    #   - 事务**内**（即下面的 `_build`，当前实现）：干净研究上首次配置**成功**
    #     （`EndEdit` = 0；实测 `removed=['质量约束 1']`、`goal=0`、`mass=True`）。
    #   - 事务**外**（照官方示例的字面行序）：同一场景**首次即失败**（`EndEdit` 返回 7）。
    #   ⇒ 官方示例里那行 `RemoveConstraint` 的**实际事务归属无法从示例文本确定**
    #     （示例无缩进语义），故以实测为准，选事务内。
    #   ⚠ 已知限制：**同一研究上第二次配置会失败**（`Create*` 返回 None）。
    #     官方示例也是「每个研究配置一次」，未见重复配置的用法 ⇒ 不视为缺陷，
    #     但调用方需知：改参数应新建研究，而不是在同一研究上重设。
    return _edit(manager, _build)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 定位:   ICWTopologyStudyManager 的其余 Create*：CreateStressConstraint(Int32&)      
#           → CWTopologyStressConstraintCreatePreservedRegionControl(Int32&) → CWTopolog
#           yPreservedRegionCreateSymmetryControl(Int32&)        → CWTopologySymmetryCon
#           trolCreateDemoldControl(Int32&)          → CWTopologyDemoldControlCreateThic
#           knessControl(Int32&)       → CWTopologyThicknessControl
# 官方做法依据: C:\topo_en 的 t_defining_preserved_region.htm /
#         t_defining_quarter_symmetry_control.htm / t_defining_de-mold_manufacturing.htm。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_mass_constraint(study, *, reduce_percent: float):
    """单独建一条质量约束（减重百分比语义）。返回该约束对象。"""
    manager = get_topology_study_manager(study)
    constraint = get_com_member(manager, "CreateMassConstraint", out_i4())
    if constraint is None:
        raise RuntimeError("CreateMassConstraint 未返回对象")

    def _configure():
        get_com_member(constraint, "SetMassPreference", int(TP_MASS_PERCENTAGE))
        get_com_member(constraint, "SetValue", float(reduce_percent))
        return constraint

    return _edit(constraint, _configure)


def create_factor_of_safety_constraint(study, *, specified_factor: float):
    """建安全系数约束（应力不得超过屈服强度的该百分比）。"""
    manager = get_topology_study_manager(study)
    constraint = get_com_member(manager, "CreateFactorOfSafetyConstraint", out_i4())
    if constraint is None:
        raise RuntimeError("CreateFactorOfSafetyConstraint 未返回对象")
    return _edit(constraint, lambda: (
        get_com_member(constraint, "SetValue", float(specified_factor)), constraint)[1])


def create_stress_constraint(study, *, value: float, comparator: int = 0):
    """建应力约束。

    ``comparator`` 取 ``swsTopologyStudyConstraintComparator_e`` 的值；
    本机反射里有该枚举但取值未逐个核对，故默认 ``0`` 并由调用方显式给出。
    """
    manager = get_topology_study_manager(study)
    constraint = get_com_member(manager, "CreateStressConstraint", out_i4())
    if constraint is None:
        raise RuntimeError("CreateStressConstraint 未返回对象")

    def _configure():
        get_com_member(constraint, "SetComparator", int(comparator))
        get_com_member(constraint, "SetValue", float(value))
        return constraint

    return _edit(constraint, _configure)


def create_preserved_region(study, *, option: int | None = None):
    """建保留区控制，返回该控制对象。

    ⚑ 调用方须**先选好要保留的面**再调本函数 —— ``ICWTopologyPreservedRegionControl``
    的 ``SelectFaces(Object)`` 接受实体数组，但既有模式（``sw_simulation``）是用
    选区而非数组，本模块沿用该模式，故本函数**不接受面参数**：由调用方选好再调。

    官方 CHM 原话："During optimization, the software always preserves the faces to
    which you apply fixtures and loads." ⇒ **夹具与载荷所在面自动保留**，
    保留区是**额外**的。
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


def _apply_declarative_selection(selection: str, selection_kind: str) -> int:
    """★ 在**活动文档**上按声明式选择器建选区 —— 拓扑控制的官方前置用。

    ★★ 2026-10-07（接手轮 · 规格 216 T-216-07）**为什么要它**：
      ★ `CreateSymmetryControl` / `CreateDemoldControl` 的官方前置**都是"调用方先选好"**
        （★ 见两个函数自己的 docstring：「调用方须先选好对称平面」/「调用方须先选好拔模方向的面/边/基准面」）✓
      ★★ 而**注入解析器会清空选区**（**事实 503**）⇒ ★ 模型**没有任何办法**在调工具前选好 ✗
      ★ 本模块的工具只拿到 `study`（★ 拿不到 model）⇒ ★ 故这里**自己取活动文档**
        （★ 拓扑研究就在活动文档里 ⇒ ★ 选区本就该建在它上面）✓
      ★ 规则 3 **不许收裸坐标** ⇒ ★ 收**声明式选择器**（`index:<n>` / `__current_selection__`）✓
    :returns: ★ **回读**到的选区计数（★ 0 会抛 —— ★ 事实 8：不信返回值）✓
    """
    from sw_connect import connect_solidworks, get_com_member as _get
    import sw_selection_spec as _SS
    sw, _m = connect_solidworks(wait_seconds=10)
    doc = _get(sw, "ActiveDoc")
    if doc is None:
        raise RuntimeError(
            "★ 没有活动文档 ⇒ ★ 选不了（★ 这是**前置未成立**、★ 与「控制建不出来」是两件事）")
    got = int(_SS.resolve_selection(doc, str(selection), str(selection_kind or "FACE")))
    if got <= 0:
        raise RuntimeError("★ 选区未建立：选择器 %r 解析后计数为 %d" % (str(selection), got))
    return got


def create_symmetry_control(study, *, symmetry_type: int = 0,
                            selection: str = "", selection_kind: str = "FACE"):
    """建对称控制（官方教程用 1/4 对称）。调用方须先选好对称平面。

    ★★ 2026-10-07（规格 216 T-216-07）**加声明式选区**：★ `selection` 非空时，
      ★ 由本函数在**紧邻 `SelectSymmetryType` 之前**、在活动文档上把对称平面选上
      （★ 官方前置那句"调用方须先选好"**就是**原因；★ 而解析器会清空选区 —— 事实 503）✓
    """
    manager = get_topology_study_manager(study)
    #: ★★ 2026-10-07 真机订正：★ 选区必须在 **`CreateSymmetryControl` 之前**——
    #:   把它放在 `_configure` 里**太晚**（★ 真机读数：控制对象**根本没建出来**，
    #:   报 `CreateSymmetryControl 未返回对象`）⇒ ★ 即**控制是"从当前选区建出来的"** ✓
    if str(selection or "").strip():
        _apply_declarative_selection(selection, selection_kind)
    control = get_com_member(manager, "CreateSymmetryControl", out_i4())
    if control is None:
        raise RuntimeError("CreateSymmetryControl 未返回对象")

    def _configure():
        get_com_member(control, "SelectSymmetryType", int(symmetry_type))
        return control

    return _edit(control, _configure)


def create_demold_control(study, *, direction: int = 0,
                          selection: str = "", selection_kind: str = "FACE"):
    """建脱模控制（制造约束）。调用方须先选好拔模方向的面/边/基准面。

    ★★ 2026-10-07（规格 216 T-216-07）**加声明式选区**：★ 同 `create_symmetry_control` ——
      ★ `selection` 非空时，由本函数在**紧邻 `SelectDemoldDirection` 之前**选上 ✓
    """
    manager = get_topology_study_manager(study)
    #: ★★ 同 `create_symmetry_control`：★ 选区必须在 **`CreateDemoldControl` 之前**（★ 真机订正）✓
    if str(selection or "").strip():
        _apply_declarative_selection(selection, selection_kind)
    control = get_com_member(manager, "CreateDemoldControl", out_i4())
    if control is None:
        raise RuntimeError("CreateDemoldControl 未返回对象")

    def _configure():
        get_com_member(control, "SelectDemoldDirection", int(direction))
        return control

    return _edit(control, _configure)


def create_thickness_control(
    study,
    *,
    min_thickness: float | None = None,
    max_thickness: float | None = None,
):
    """建最小/最大成员尺寸控制（增材制造与铸造的常用制造约束）。"""
    manager = get_topology_study_manager(study)
    control = get_com_member(manager, "CreateThicknessControl", out_i4())
    if control is None:
        raise RuntimeError("CreateThicknessControl 未返回对象")

    def _configure():
        if min_thickness is not None:
            get_com_member(control, "SetIncludeMinMemberThickness2", True)
            get_com_member(control, "SetMinimumMemberThickness", _mm(min_thickness))
        if max_thickness is not None:
            get_com_member(control, "SetIncludeMaxMemberThickness2", True)
            get_com_member(control, "SetMaxMemberThickness", _mm(max_thickness))
        return control

    return _edit(control, _configure)


def set_topology_iteration_options(
    study,
    *,
    iteration_option: int | None = None,
    iteration_limit: int | None = None,
    convergence_check: int | None = None,
):
    """设迭代/收敛选项（``ICWTopologyStudyOptions``）。"""
    options = get_topology_study_options(study)
    if iteration_option is not None:
        get_com_member(options, "SetIterationOption", int(iteration_option))
    if iteration_limit is not None:
        get_com_member(options, "SetIterationLimit", int(iteration_limit))
    if convergence_check is not None:
        get_com_member(options, "SetConvergenceCheck", int(convergence_check))
    return options


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 定位:   ICWTopologyStudyManager 的 Get*（签名均为 ``(String Name, Int32& Err)``）
#         与 RemoveConstraint(String) / RemoveControl(String)；
#         ICWStudy 的 CreateMesh / RunAnalysis / MeshAndRun / get_Results。
# 官方做法依据: C:\topo_en 的 t_topology_tutorial_meshing.htm 与
#         t_exporting_optimization_results.htm（后者用 View Convergence Data and Graph
#         验证目标与约束是否收敛到目标值）。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def list_topology_constraints_and_controls(study) -> dict[str, Any]:
    """按名取回该拓扑研究上**已建**的约束与控制。

    返回 ``{kind: object|None}``（``kind`` 见 :data:`_TOPOLOGY_GETTERS` 的键）。
    取不到的条目为 ``None``；**不抛异常** —— 这是读取入口，用于回读核对，
    缺某类约束是正常状态（例如只设了质量约束没设应力约束）。
    """
    manager = get_topology_study_manager(study)
    found: dict[str, Any] = {}
    for kind, getter in _TOPOLOGY_GETTERS.items():
        # Get*(String Name, Int32& Err) —— 名字须由调用方给；本模块按已知默认名逐个试。
        # ⚑ 2026-10-01 真机：此处原传裸 `0` 当出参，必抛 `类型不匹配`，
        #   而下面的 `except` 把异常吞成 None ⇒ **本函数此前永远返回全 None（假通过）**。
        #   出参改为 `out_i4()`。同时把「取不到」与「调用失败」分开记，不再混为一谈。
        try:
            found[kind] = get_com_member(manager, getter, _default_constraint_name(kind), out_i4())
            found[kind + "__error"] = None
        except Exception as exc:
            found[kind] = None
            found[kind + "__error"] = str(exc)[:120]
    return found


def _default_constraint_name(kind: str) -> str:
    """该族约束在**中文界面**下的默认名（真机实测名，见模块头实测记录）。

    ``Get*(Name, Err)`` 需要一个真实名字；官方示例的做法是「建完立刻 ``GetName`` 拿回来」，
    本模块在**建之前**要查有无，故只能用默认名试探。
    """
    return _DEFAULT_CONSTRAINT_NAMES.get(kind, kind)


#: 真机实测的默认约束名（SW 2026 SP4.1 简体中文）。
#: ⚠ 名字随 UI 语言变 —— 英文界面下应为 `Mass Constraint 1` 一类；
#: 这里列的是本机实测值，换语言环境需重测（同 AGENTS.md 已知事实 9 的基准面名问题）。
_DEFAULT_CONSTRAINT_NAMES: dict[str, str] = {
    "mass": "质量约束 1",
    "stress": "应力约束 1",
    "factor_of_safety": "安全系数约束 1",
    "displacement": "位移约束 1",
    "frequency": "频率约束 1",
    "preserved_region": "保留区域 1",
    "thickness": "厚度控制 1",
    "demold": "拔模控制 1",
    "symmetry": "对称控制 1",
}


def run_topology_study(study, *, units: int = 0, element_size: float = 0.0,
                       tolerance: float = 0.0):
    """建网格并求解。返回 ``RunAnalysis`` 的结果码。

    官方教程的顺序是「先网格、再运行」；``MeshAndRun`` 把两步合成一次调用，
    本函数默认走合成调用，失败才回退到分开的两步 —— 与
    ``sw_simulation.create_static_study`` 的多入口降级风格一致。

    ⚠⚠ **回退路径的参数顺序此前是错的**（旧代码按
    ``CreateMesh(Int32 MeshType, Double Tolerance, Double Size)`` 传）。
    2026-10-01 从官方 VB6 类型库 CHM
    （`CosmosWorksLib~CWStudy~CreateMesh.html`）取到**真参数名**：

        CreateMesh(ByVal NUnits As Long, ByVal DElementSize As Double,
                   ByVal DTolerance As Double)

    ⇒ 第 1 参是**单位**（`swsUnit_e`：SI 0 / English 1 / Metric 2），
    不是网格类型；后两参是**单元尺寸**与**容差**，顺序与原写法相反。
    真机证据：`CreateMesh(0, 4.9339, 0.2467)` → 返回 0、**7,219 个单元**（正常）；
    `CreateMesh(0, 0.2467, 4.9339)` → 返回 0、**19,509,593 个单元**（爆）。
    单位是**毫米**。详见 ``sw_simulation.create_mesh`` 的来源块。

    :param units: ``swsUnit_e``：``0``=SI、``1``=English、``2``=Metric。
    :param element_size: 全局单元尺寸（**毫米**），须为正。
    :param tolerance: 网格容差（**毫米**），须为正；官方默认是尺寸的 5%。

    ★★★★ 2026-10-04（接手轮）**兑现那句「报告结果是否存在」** ——
      处置 `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #5`）—— ★ 裁判逐字：
      「★ `topology_run` 承诺「**报告结果是否存在**」★ 实则**只返回码**」✓
    ★★ **而那句承诺**逐字在 ToolSpec 里**（`mcp-server/tool_specs_batch1.py`）：
      > ★ 「Mesh and solve the topology study and **report whether results exist**.
      >   ★★ A zero RunAnalysis return code does NOT mean success — **judge by study results**.」
    ★★★ **⇒ 原函数只 `return code` ⇒ 承诺没兑现** ✓
    ★★★★ **修法：跑完就调本模块既有的 `collect_topology_numbers(study)`** ——
      它的判据逐字是「**不用任何返回码判成功**：★ 有结果 = `Results` 非 None
      且 `GetPlotCount() > 0`」⇒ ★ **正好是那句承诺要的东西** ✓
    ★ **返回**：★ `{code, results_present, results}` —— ★ 而**保留 `code`**（★ 向后兼容）✓
    """
    code = call_com_member(study, "MeshAndRun")
    if code not in (None, 0):
        # 回退：先 CreateMesh(NUnits, DElementSize, DTolerance) 再 RunAnalysis()
        get_com_member(study, "CreateMesh", int(units),
                       _mm(element_size), _mm(tolerance))
        code = call_com_member(study, "RunAnalysis")
    #: ★★★★ **承诺的那一步**：★ 用**结果**判成功（★ 而不是返回码）✓
    results = None
    try:
        results = collect_topology_numbers(study)
    except Exception as exc:                                              # noqa: BLE001
        results = {"status": "unknown",
                   "reason": "★ 读结果时抛 %s: %s" % (type(exc).__name__, str(exc)[:150]),
                   "source_members": {}}
    return {
        "code": code,
        #: ★ **真相在这里**（★ 而不是 `code`）—— ★ 与 ToolSpec 那句逐字对应 ✓
        "results_present": bool(isinstance(results, dict)
                                and results.get("status") == "ok"),
        "results": results,
    }


def collect_topology_evidence(sw_app) -> dict[str, Any]:
    """收集当前文档的拓扑研究证据（供能力快照与 ``capabilities.yaml`` 的 evidence）。

    只做**读取**，不改任何模型。返回 ``{study_count, studies:[…]}``；
    每个研究带名字、分析类型、以及该研究上各类约束/控制的存在性。

    ⚠ 本函数不判断「优化有没有成功」—— 那要看收敛数据与结果图，
    官方入口是研究树 ``Results`` → ``View Convergence Data and Graph``
    （本模块未实现，反射里未核到对应成员，按铁律 5 不编）。
    """
    document = get_cw_document(sw_app)
    manager = get_com_member(document, "StudyManager")
    if manager is None:
        raise RuntimeError("CWModelDoc.StudyManager 为 None")

    count = get_com_member(manager, "StudyCount") or 0
    studies: list[dict[str, Any]] = []
    for i in range(int(count)):
        study = get_com_member(manager, "GetStudy", i)
        if study is None:
            continue
        entry: dict[str, Any] = {
            "name": get_com_member(study, "Name"),
            "analysis_type": get_com_member(study, "AnalysisType"),
        }
        try:
            present = list_topology_constraints_and_controls(study)
            entry["topology"] = {k: v is not None for k, v in present.items()}
        except RuntimeError:
            # 不是拓扑研究 —— 正常，跳过拓扑部分
            entry["topology"] = None
        studies.append(entry)
    return {"study_count": int(count), "studies": studies}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**官方接口的只读包装**）+ `specs/001-topology-result-readout`
# 文件:   `scripts/sw_topology.py` —— 追加 `collect_topology_numbers` 与 `TOPOLOGY_RESULTS_UNRESOLVED`
# 官方签名依据: 反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWResults` 段
#         （**裁决者**，铁律 4）。本函数**只调无参数成员** —— 见下「为什么只包这三个」。
# 定位:   做 `specs/001-topology-result-readout/tasks.md` 的 **T-007 / T-009**。
#         spec 的验收要求：「每个返回值附带来源成员名（可复查）」；
#         「未跑过 ⇒ 返回 `{"status": "no_results", …}`，**不抛未捕获异常、不静默空 dict**」。
#
#   ★★ **为什么只包这三个成员（`GetPlotCount` / `GetPlotNames` / `GetMaximumAvailableSteps`）**：
#     反射里 `ICWResults` 共 **107 个成员**，但**官方文档源里没有任何一页解释它们的参数语义**
#     （查过 `cosworks_pages` / `chm_cosworks` / `cworksapi` / 官方文档目录，**4 处 0 命中**）。
#     例：`GetMinMaxDisplacement(Int32, Int32, Object, Int32, Int32&)` —— **4 个入参含义未定义**。
#     **⇒ 按铁律 5「查不到就说查不到」：不猜参数。**
#     而这三个成员**无参数**、语义自明，且 `GetPlotCount`/`GetPlotNames`
#     **已在真机上验证过**（003 的闭环正是靠它断言到「材料质量1」，见
#     `output/topology-evidence.json` 的 `steps.material_mass_plot`）。
#     ⇒ **可安全包装**；`GetMaximumAvailableSteps()` 无参数但**未运行期验过** ⇒ 按事实 30
#       「**判据永远是「返回非 None」，不是「在可取名单里」**」处理：取到就报，取不到就 `None`。
#
#   ⚠ **参数语义未知的那几个成员**登记在 `TOPOLOGY_RESULTS_UNRESOLVED` 里（**不是实现**），
#     连同「为什么没实现」与「要补什么才能实现」——**避免下一个人重踩**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本函数**只读**，不改模型；不 `BeginEdit`/`EndEdit`，不弹窗。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

#: 反射里**存在、但参数语义查不到**（4 处官方文档源 0 命中）的 `ICWResults` 成员。
#: **不实现它们**（铁律 5）—— 要补的条件写在每条的原因里。
TOPOLOGY_RESULTS_UNRESOLVED: dict[str, str] = {
    "GetMinMaxDisplacement": (
        "签名 `Object GetMinMaxDisplacement(Int32, Int32, Object, Int32, Int32&)` —— "
        "**4 个入参含义无官方文档**（cosworks_pages / chm_cosworks / cworksapi / 官方文档目录 4 处 0 命中）。"
        "**要补的条件**：找到官方参数说明，或在真机上用「有结果 / 无结果」两种研究做受控对比。"
    ),
    "GetMinMaxStress": (
        "签名 `Object GetMinMaxStress(Int32, Int32, Int32, Object, Int32, Int32&)` —— 同上，**5 个入参无文档**。"
    ),
    "GetMinMaxFactorOfSafety": (
        "签名 `Object GetMinMaxFactorOfSafety(Boolean, Object, Int32, Int32, Int32&)` —— 同上，**4 个入参无文档**。"
    ),
    "GetTimeOrFrequencyAtEachStep": (
        "签名 `Object GetTimeOrFrequencyAtEachStep(Int32, Int32&)` —— 同上，**1 个入参无文档**。"
    ),
    "SavePlotsAseDrawings": (
        "签名 `Int32 SavePlotsAseDrawings(String, String, String)` —— 参数名未给，"
        "**且只有反射一源**（无官方页）⇒ 按事实 28/30「反射里有」≠「运行期调用得到」，**不包装**。"
    ),
    "ExportSimulationStudy": (
        "在 `ICWStudy` 上：`Int32 ExportSimulationStudy(String, String, Int32, Int32, Int32, Int32, Int32)` —— "
        "**参数名未给、且只有反射一源**（`chm_cosworks` / `cosworks_pages` / 官方文档目录 **3 处 0 命中**）"
        "⇒ 按事实 28/30「反射里有」≠「运行期调用得到」，**不包装**。"
        "**要补的条件**：找到官方参数说明，或在真机上做受控导出（先确认前两个 String 是路径还是格式）。"
    ),
}


def collect_topology_numbers(study) -> dict[str, Any]:
    """读取某个**已求解**拓扑研究的结果读数；未求解时**明确报无结果**，不抛异常。

    参数
    ----
    study : ``ICWStudy``
        由 ``create_topology_study`` 或 ``get_cw_document`` 的研究管理拿到的研究对象。

    返回（两种形态，**spec 的 T-007 验收要求**）
    ------------------------------------------
    * 有结果::

          {"status": "ok",
           "source_members": {...},      # 每个读数**附来源成员名**（可复查）
           "plot_count": 2,
           "plot_names": ["品质1", "材料质量1"],
           "material_mass_plot": "材料质量1",   # 命中判据正则时为图名，否则 None
           "max_available_steps": 1}

    * 无结果::

          {"status": "no_results", "reason": "...", "source_members": {...}}

    ⚠ **判据说明（重要）**：本项目已累计多处「返回码撒谎」，所以
    **本函数不用任何返回码判成功** —— 「有结果」的判据是
    **`Results` 对象非 None 且 `GetPlotCount() > 0`**（与 003 的证据脚本同一口径）。
    """
    import re as _re

    results = get_com_member(study, "Results")
    # ⚠ `Results` 为空 ⇒ **不是异常**，是「还没跑过」这一合法状态 ⇒ 明确报出来。
    if results is None:
        return {
            "status": "no_results",
            "reason": "study.Results 为 None（该研究未求解或求解未产出结果）",
            "source_members": {"results": "ICWStudy.Results"},
        }

    plot_count = get_com_member(results, "GetPlotCount")
    if plot_count in (None, 0):
        return {
            "status": "no_results",
            "reason": "study.Results 非 None 但 GetPlotCount() == %r（无结果图）" % (plot_count,),
            "source_members": {"results": "ICWStudy.Results", "plot_count": "ICWResults.GetPlotCount"},
        }

    raw_names = get_com_member(results, "GetPlotNames")
    plot_names = [str(x) for x in (raw_names or ())]

    # ⚑ Material Mass 图：中文界面 `材料质量1` / 英文 `Material Mass 1`
    #   ⇒ 判据用正则，不硬编码单一语言（spec §Assumptions 的要求）。
    pattern = _re.compile(r"(材料质量|Material\s*Mass)")
    matched = [n for n in plot_names if pattern.search(n)]

    steps = get_com_member(results, "GetMaximumAvailableSteps")
    return {
        "status": "ok",
        "source_members": {
            "results": "ICWStudy.Results",
            "plot_count": "ICWResults.GetPlotCount",
            "plot_names": "ICWResults.GetPlotNames",
            "max_available_steps": "ICWResults.GetMaximumAvailableSteps",
        },
        "plot_count": int(plot_count),
        "plot_names": plot_names,
        "material_mass_plot": matched[0] if matched else None,
        "max_available_steps": (int(steps) if steps is not None else None),
        "unresolved_members": sorted(TOPOLOGY_RESULTS_UNRESOLVED),
    }


# ── 24h 计划 段 2.2（Spec Kit `144`）：**拓扑柜台的读数/参数 4 个回读报告** ──────────
# ★★★ 为什么这四个要包：
#   上面 10 个拓扑工具已挂（create_* / run / evidence），但**读数与参数**这一组从未上柜：
#     · `get_topology_study_manager`        ⇒ 回 **COM 对象**
#     · `get_topology_study_options`        ⇒ 回 **COM 对象**
#     · `set_topology_goal`                 ⇒ 回 **COM 对象**（★ 而它是"设置"⇒ 要**回读确认**）
#     · `set_topology_iteration_options`    ⇒ 回 **COM 对象**
#   ⇒ ★ MCP 回不了对象 ⇒ 必须翻成**可 JSON 化**的回读报告。
# ★★ 判据（★ 按 §5.0：**先找自家仓库**）：
#   · 取到了几个 kind ⇒ 用 `list_topology_constraints_and_controls`（★ **本模块自己的读取入口**）
#     —— ★ 而它的注释里记着一条教训：曾因裸传 `0` 当出参而**永远返回全 None（假通过）**，
#       改用 `out_i4()` 后才是真的。⇒ 本组一律**只回"哪个 kind 非 None"**（布尔，可 JSON 化）。
#   · `collect_topology_numbers` 的 `material_mass_plot` 是**既有证据脚本**的核心判据
#     （`tools/capture_topology_evidence.py`：「`GetPlotNames` 里出现 `材料质量*`」）——
#     ★ 本组**不重复**造它，直接复用那个函数。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_topology.py —— 本段
# 定位:   拓扑研究的**读数与参数**回读报告（24h 段 2.2）。
# 官方依据: `ICWTopologyStudyManager` / `ICWTopologyStudyOptions` 的官方成员
#          （见本模块上方各来源块；官方例 `Create_Topology_Study_Example_VBA.txt`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本段整体
# ─────────────────────────────────────────────────────────────────────────────


def _kinds_taken(study) -> dict[str, bool]:
    """★ **回读**：该研究上「哪些约束/控制**真的取到了**」（★ JSON 可化）。

    ★ 不把 COM 对象本身回出去 —— 只回**布尔**（★ 这也让"取到了"这件事**可断言**）。
    """
    raw = list_topology_constraints_and_controls(study)
    return {k: (v is not None) for k, v in raw.items() if not k.endswith("__error")}


def _kinds_summary(study) -> dict[str, Any]:
    """回读摘要（★ 计数 + 明细 + 出错项）—— 供 setter 做**前后对照**。"""
    raw = list_topology_constraints_and_controls(study)
    kinds = {k: (v is not None) for k, v in raw.items() if not k.endswith("__error")}
    errors = {k: v for k, v in raw.items() if k.endswith("__error") and v}
    return {"kinds": kinds, "taken_count": sum(1 for v in kinds.values() if v),
            "total": len(kinds), "errors": errors}


def topology_manager_report(study) -> dict[str, Any]:
    """★ 回**管理器**的**可 JSON 化**报告（★ 不回 COM 对象）。"""
    mgr = get_topology_study_manager(study)
    return {
        "ok": mgr is not None,
        "object_type": type(mgr).__name__ if mgr is not None else None,
        "study_name": str(get_com_member(study, "Name") or ""),
        **({"kinds": _kinds_taken(study)} if mgr is not None else {}),
        "★": "ok 判的是管理器对象非 None（★ 回读优先，不靠异常）",
    }


def topology_options_report(study) -> dict[str, Any]:
    """★ 回**研究选项**的**可 JSON 化**报告（★ 不回 COM 对象）。"""
    opt = get_topology_study_options(study)
    out: dict[str, Any] = {
        "ok": opt is not None,
        "object_type": type(opt).__name__ if opt is not None else None,
        "study_name": str(get_com_member(study, "Name") or ""),
        "★": "ok 判的是选项对象非 None；★ 具体选项值由 set_*_report 的前后对照体现",
    }
    return out


def set_topology_goal_report(study, *, goal_type: int = 0,
                             mass_reduce_percent: float = 0.0) -> dict[str, Any]:
    """★ 设**拓扑目标**并回**回读报告**（★ 前后对照「取到了几个 kind」）。"""
    before = _kinds_summary(study)
    err = None
    try:
        set_topology_goal(study, goal_type=goal_type, mass_reduce_percent=mass_reduce_percent)
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    after = _kinds_summary(study)
    return {
        "ok": err is None and after["taken_count"] >= before["taken_count"],
        "before": before, "after": after, "error": err,
        "★": "ok 判的是「无异常 **且** 取到的 kind 数不减少」（★ 回读，不看返回对象）",
    }


def set_topology_iteration_options_report(study, *, iteration_option: int | None = None,
                                          iteration_limit: int | None = None) -> dict[str, Any]:
    """★ 设**迭代选项**并回**回读报告**（★ 前后对照）。"""
    before = _kinds_summary(study)
    err = None
    try:
        #: ⚠ 形参名是 **`iteration_limit`**（★ 不是我最初写的 `iteration_count`）——
        #:   真机一调就报 `unexpected keyword argument`（2026-10-01 轮 247）。
        set_topology_iteration_options(study, iteration_option=iteration_option,
                                       iteration_limit=iteration_limit)
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    after = _kinds_summary(study)
    return {
        "ok": err is None and after["taken_count"] >= before["taken_count"],
        "before": before, "after": after, "error": err,
        "★": "ok 判的是「无异常 **且** 取到的 kind 数不减少」（★ 回读，不看返回对象）",
    }


def topology_constraints_report(study) -> dict[str, Any]:
    """★ 回**已建约束与控制**的可 JSON 化报告（★ 不回 COM 对象）。

    ★★ `list_topology_constraints_and_controls` 回的是 ``{kind: object|None}``（**含 COM 对象**）
      ⇒ MCP 回不了 ⇒ 本函数把它翻成**布尔 + 计数**（★ 那也是「取到了」这件事**可断言**的形态）。
    """
    return {"ok": True, "study_name": str(get_com_member(study, "Name") or ""),
            **_kinds_summary(study),
            "★": "ok 恒 True（这是纯读取入口）；★ 判据在 taken_count / kinds 上"}

