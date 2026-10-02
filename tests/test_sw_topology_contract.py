r"""sw_topology 的官方签名与事务纪律契约测试（不连接 SolidWorks）。

这份测试守三件事，每件都用**独立再抄一份**的官方值做交叉校验
（沿用 tests/test_sw_simulation_loads_contract.py 的既定做法：签名表本身错了，
对账也会一起错，所以基准要在测试里再写一遍）：

1. **枚举值契约** —— 模块里的 ``SWS_TOPOLOGY_*`` 取值必须与 interop 反射逐条一致。
2. **调用形状契约** —— 模块里每个 ``get_com_member(obj, "成员名", …)`` 的成员名
   必须真实存在于 cosworks 反射清单里，且实参个数 = 官方 arity + 出参个数
   （见被测模块来源块里那条**尚未裁定的出参约定**注释）。
3. **事务纪律** —— ``_edit`` 必须在 ``BeginEdit``/``EndEdit`` 之间执行动作，
   且 ``EndEdit`` 返回非 0 时必须抛异常（不静默）。这是本模块最要紧的失败模式：
   不包在事务里的 ``Set*`` 会静默不落地。

官方签名与枚举值来源
--------------------
``D:\\AI\\SW\\_raw\\topo-reflect\\`` 下由 ``D:\\AI\\SW\\tools\\reflect-interop.ps1``
对 ``SolidWorks.Interop.cosworks.dll`` 做的**纯元数据反射**
（168 接口 / 363 枚举 / 3224 成员）—— 读官方程序集，不实例化任何 COM 对象。
官方**做法**（流程语义）来自本机 CHM ``otsimtopology.chm`` 的解包 ``C:\\topo_en``。

⚠ 本文件为静态比对，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_topology_contract.py —— 本文件自身
# 定位:   护城河域「拓扑优化」的契约测试。被测对象 scripts/sw_topology.py。
# 官方签名依据: D:\AI\SW\_raw\topo-reflect\{iface,enum}_cosworks.txt
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 未在本机实测（见 AGENTS.md 铁律 2）
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_topology.py"


def _load_module():
    """按路径加载被测模块，避免 import 期连带拉起 scripts 包的其它模块。

    被测模块用的是「``try: from .x import / except ImportError: from x import``」
    依赖解析模式（AGENTS.md §三 对新增模块的硬性要求），**裸导入分支需要
    ``scripts/`` 在 ``sys.path`` 上** —— 否则加载即 ``ModuleNotFoundError``。
    """
    scripts_dir = str(REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("sw_topology_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt
# 定位:   下面这份官方枚举值是**独立再抄一遍**的交叉校验基准，
#         不是从被测模块里读出来的 —— 两边都错才算漏网。
# ⚠ 未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
OFFICIAL_ENUMS = {
    "swsAnalysisStudyTypeTopology_Static": 13,
    "swsTopologyGoalType_MaximizeStiffness": 0,
    "swsTopologyGoalType_MinimizeMaximumDisplacement": 1,
    "swsTopologyGoalType_MinimizeMass": 2,
    "swsTopologyMassConstraintOption_AbsoluteValue": 0,
    "swsTopologyMassConstraintOption_Percentage": 1,
    "swsTopologyPreservedRegionOption_LoadsOnly": 0,
    "swsTopologyPreservedRegionOption_FixturesOnly": 1,
    "swsTopologyPreservedRegionOption_LoadsAndFixtures": 2,
    "swsTopologyPreservedRegionOption_None": 3,
    "swsTopologyIterationOption_Auto": 0,
    "swsTopologyIterationOption_UserDef": 1,
    "swsTopologyDemoldDirection_TwoDirectionMidPlane": 0,
    "swsTopologyDemoldDirection_PullDirectionOnly": 1,
    "swsTopologyDemoldDirection_Stamping": 2,
    "swsTopologyActivationOption_Deactivate": 0,
    "swsTopologyActivationOption_Activate": 1,
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 定位:   ICWTopologyStudyManager 的官方成员名（Create*/Get*/BeginEdit/EndEdit/
#         CreateGoal/Remove*）与 ICWStudy 的两个 topology getter —— 独立再抄一份。
# ⚠ 未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
OFFICIAL_STUDY_MANAGER_MEMBERS = {
    "BeginEdit", "EndEdit", "CreateGoal",
    "CreateDemoldControl", "CreateDisplacementConstraint",
    "CreateFactorOfSafetyConstraint", "CreateFrequencyConstraint",
    "CreateMassConstraint", "CreatePreservedRegionControl",
    "CreateStressConstraint", "CreateSymmetryControl", "CreateThicknessControl",
    "GetDemoldControl", "GetDisplacementConstraint", "GetFactorOfSafetyConstraint",
    "GetFrequencyConstraint", "GetMassConstraint", "GetPreservedRegionControl",
    "GetStressConstraint", "GetSymmetryControl", "GetThicknessControl",
    "RemoveConstraint", "RemoveControl",
}

OFFICIAL_STUDY_MEMBERS = {"TopologyStudyManager", "TopologyStudyOptions"}
OFFICIAL_STUDY_MANAGER_CREATE_ARITY = 1  # Create*(Int32&) —— 一个出参

#: 被测模块调用的**全部**官方成员名（独立再抄一份；与 iface_cosworks.txt /
#: iface_sldworks.txt 做过逐条对账）。含属性形式 —— 反射里这些写作 get_Xxx()。
OFFICIAL_MEMBERS = OFFICIAL_STUDY_MANAGER_MEMBERS | OFFICIAL_STUDY_MEMBERS | {
    # ICWStudyManager
    "CreateNewStudy2", "CreateNewStudy3", "GetStudy", "StudyCount", "StudyManager",
    # ICWStudy
    "AnalysisType", "CreateMesh", "MeshAndRun", "Name", "RunAnalysis",
    # ICWTopologyMassConstraint / StressConstraint / FactorOfSafetyConstraint
    "SetComparator", "SetMassPreference", "SetValue",
    # ICWTopologyPreservedRegionControl
    "SetIncludeRegionDepth2",
    # ICWTopologySymmetryControl
    "SelectSymmetryType",
    # ICWTopologyDemoldControl
    "SelectDemoldDirection",
    # ICWTopologyThicknessControl
    "SetIncludeMaxMemberThickness2", "SetIncludeMinMemberThickness2",
    "SetMaxMemberThickness", "SetMinimumMemberThickness",
    # ICWTopologyStudyOptions
    "SetConvergenceCheck", "SetIterationLimit", "SetIterationOption",
    # ── ICWStudy / ICWResults：T-007 的 `collect_topology_numbers` 新增的调用点 ──
    # ⚑ 按本测试的指示与 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` **逐条对过账**：
    #   · `Results`     ⇒ 反射写作属性 getter **`CWResults get_Results()`**（`## ICWStudy` 段 L2565）
    #     （本测试的判据认 `成员名(` 或 `get_成员名(` 其一，故这里写基名）
    #   · `GetPlotCount`            ⇒ `Int32 GetPlotCount()`             （`## ICWResults` L2234）
    #   · `GetPlotNames`            ⇒ `Object GetPlotNames()`            （同段 L2237）
    #   · `GetMaximumAvailableSteps`⇒ `Int32 GetMaximumAvailableSteps()` （同段 L2214）
    "Results", "GetPlotCount", "GetPlotNames", "GetMaximumAvailableSteps",
}


def test_enum_values_match_official_reflection():
    """模块里的枚举取值与官方反射逐条一致。"""
    m = _load_module()
    actual = {
        "swsAnalysisStudyTypeTopology_Static": m.SWS_ANALYSIS_STUDY_TYPES["topology_static"],
        "swsTopologyGoalType_MaximizeStiffness": m.SWS_TOPOLOGY_GOAL_TYPES["maximize_stiffness"],
        "swsTopologyGoalType_MinimizeMaximumDisplacement": m.SWS_TOPOLOGY_GOAL_TYPES["minimize_maximum_displacement"],
        "swsTopologyGoalType_MinimizeMass": m.SWS_TOPOLOGY_GOAL_TYPES["minimize_mass"],
        "swsTopologyMassConstraintOption_AbsoluteValue": m.SWS_TOPOLOGY_MASS_PREFERENCES["absolute_value"],
        "swsTopologyMassConstraintOption_Percentage": m.SWS_TOPOLOGY_MASS_PREFERENCES["percentage"],
        "swsTopologyPreservedRegionOption_LoadsOnly": m.SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS["loads_only"],
        "swsTopologyPreservedRegionOption_FixturesOnly": m.SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS["fixtures_only"],
        "swsTopologyPreservedRegionOption_LoadsAndFixtures": m.SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS["loads_and_fixtures"],
        "swsTopologyPreservedRegionOption_None": m.SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS["none"],
        "swsTopologyIterationOption_Auto": m.SWS_TOPOLOGY_ITERATION_OPTIONS["auto"],
        "swsTopologyIterationOption_UserDef": m.SWS_TOPOLOGY_ITERATION_OPTIONS["user_defined"],
        "swsTopologyDemoldDirection_TwoDirectionMidPlane": m.SWS_TOPOLOGY_DEMOLD_DIRECTIONS["two_direction_mid_plane"],
        "swsTopologyDemoldDirection_PullDirectionOnly": m.SWS_TOPOLOGY_DEMOLD_DIRECTIONS["pull_direction_only"],
        "swsTopologyDemoldDirection_Stamping": m.SWS_TOPOLOGY_DEMOLD_DIRECTIONS["stamping"],
        "swsTopologyActivationOption_Deactivate": m.SWS_TOPOLOGY_ACTIVATION["deactivate"],
        "swsTopologyActivationOption_Activate": m.SWS_TOPOLOGY_ACTIVATION["activate"],
    }
    assert actual == OFFICIAL_ENUMS, "枚举取值与官方反射不一致（或两边都改动过）"


def test_goal_and_mass_shortcuts():
    """官方教程流程用到的两个短别名必须指向正确的枚举值。

    官方 CHM t_setting_optimization_goal.htm：目标 ``Best Stiffness to Weight
    ratio (default)``、质量约束 ``Reduce mass by (percentage)`` = 75。
    """
    m = _load_module()
    assert m.TP_GOAL_MAXIMIZE_STIFFNESS == 0
    assert m.TP_MASS_PERCENTAGE == 1
    assert m.TP_ACTIVATE == 1


def _member_calls(source: str) -> list[tuple[str, int, int]]:
    """抽出源码里所有 ``get_com_member(obj, "成员名", <实参…>)`` 的调用点。

    返回 ``[(成员名, 实参个数, 行号)]`` —— 实参个数**含那个出参占位**，
    与官方 arity 的差值由调用方按出参约定核算。
    """
    tree = ast.parse(source)
    out: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "id", None) or getattr(func, "attr", None)
        if name != "get_com_member" or len(node.args) < 2:
            continue
        member = node.args[1]
        if not (isinstance(member, ast.Constant) and isinstance(member.value, str)):
            continue
        out.append((member.value, len(node.args) - 2, node.lineno))
    return out


def test_every_called_member_exists_in_official_reflection():
    """模块调用的**每一个** COM 成员名都必须真实存在于官方反射里。

    ⚑ 属性与方法的两种写法都要认：反射清单把 getter 写作 ``get_Xxx()``，
    而 pywin32 迟到绑定下调用方写的是 ``Xxx``（见 AGENTS.md 已知事实 4 ——
    同一成员可能是属性也可能是方法，沿上游 ``get_com_member`` 即可）。
    故判据是「``成员名(`` 或 ``get_成员名(`` 命中其一」。

    ⚠ 本测试**不读** ``D:\\AI\\SW\\_raw\\`` 下的反射转储（那在本工作区被 gitignore，
    换台机器就不在）。它用下面这份**独立再抄一遍**的官方成员集做基准。
    与转储做过一次逐条对账（35 个成员，除 getter 前缀外全部命中）。
    """
    source = MODULE_PATH.read_text(encoding="utf-8")
    called = {name for name, _, _ in _member_calls(source)}
    unknown = called - OFFICIAL_MEMBERS
    assert not unknown, (
        "模块调用了官方反射里不存在的成员：%s\n"
        "（若新增了调用点，请把它加进本文件的 OFFICIAL_MEMBERS 并与 "
        "D:\\AI\\SW\\_raw\\topo-reflect\\iface_cosworks.txt 对账）" % sorted(unknown)
    )


def test_topology_create_calls_pass_one_out_param_placeholder():
    """每个 ``Create*Constraint`` / ``Create*Control`` 必须传 1 个出参占位。

    官方签名是 ``Create*(Int32&)`` —— 一个出参。本项目既有模式
    （``sw_simulation.CreateNewStudy3``）传占位 ``0``，本模块沿用该模式。
    ⚠ 该出参约定在本项目内**尚未裁定**（见被测模块来源块），
    本测试只钉住「模块内部一致」，不裁断对错。
    """
    source = MODULE_PATH.read_text(encoding="utf-8")
    offenders = []
    for member, argc, lineno in _member_calls(source):
        if not member.startswith("Create"):
            continue
        if member in {"CreateGoal", "CreateNewStudy", "CreateNewStudy2", "CreateNewStudy3",
                      "CreateMesh", "CreateMeshForMeshControl", "CreateAnalysisDatabase",
                      "CreateImportedResultsPlot", "CreateTrendTracker"}:
            continue  # 非 CWTopology* 家族，各有各的签名
        if argc != OFFICIAL_STUDY_MANAGER_CREATE_ARITY:
            offenders.append("%s:%d %s() 实参 %d，应为 %d（一个出参占位）"
                             % (MODULE_PATH.name, lineno, member, argc, OFFICIAL_STUDY_MANAGER_CREATE_ARITY))
    assert not offenders, "\n".join(offenders)


def test_study_getters_are_the_two_official_properties():
    """两个取入口必须用官方 getter 名（反射里写作 get_XXX()，迟到绑定读属性名）。"""
    source = MODULE_PATH.read_text(encoding="utf-8")
    called = {name for name, _, _ in _member_calls(source)}
    assert OFFICIAL_STUDY_MEMBERS <= called, (
        "缺少官方取入口：%s" % sorted(OFFICIAL_STUDY_MEMBERS - called)
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_topology_contract.py —— 本文件自身
# 定位:   事务纪律的行为测试。用假对象记录调用序列 ——
#         不连 SolidWorks、不实例化任何 COM 对象（铁律 2）。
# ⚠ 未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
class _FakeCom:
    """记录调用序列的假 COM 对象。

    ``get_com_member`` 会先按属性取、取不到再按方法调；这里统一用属性返回
    **可调用对象**，从而两种取法都落到同一个记录器上。
    """

    def __init__(self, end_edit_code=0):
        self.calls: list[tuple[str, tuple]] = []
        self._end_edit_code = end_edit_code

    def __getattr__(self, name):
        def _recorder(*args):
            self.calls.append((name, args))
            if name == "EndEdit":
                return self._end_edit_code
            return None
        return _recorder

    def names(self):
        return [n for n, _ in self.calls]


def _install_fake_get_com_member(monkeypatch_target, fake):
    """把被测模块的 get_com_member 换成「无视对象、一律返回同一假对象」。"""
    def _get(obj, member, *args):
        return getattr(fake, member)(*args)
    monkeypatch_target.get_com_member = _get
    monkeypatch_target.call_com_member = _get


def test_edit_brackets_action_with_begin_and_end(monkeypatch):
    """``_edit`` 必须以 BeginEdit 开头、EndEdit 结尾，动作在中间。"""
    m = _load_module()
    fake = _FakeCom()
    _install_fake_get_com_member(m, fake)

    m._edit(fake, lambda: fake.SetValue(75.0))

    assert fake.names() == ["BeginEdit", "SetValue", "EndEdit"], (
        "事务括号顺序不对：%s" % fake.names()
    )


def test_edit_raises_on_nonzero_end_edit(monkeypatch):
    """``EndEdit`` 返回非 0 ⇒ 必须抛异常，不能静默。

    这是本模块最要紧的失败模式：不报错的 Set* 会让人以为约束设上了。
    """
    m = _load_module()
    fake = _FakeCom(end_edit_code=7)
    _install_fake_get_com_member(m, fake)

    try:
        m._edit(fake, lambda: None)
    except RuntimeError as exc:
        assert "7" in str(exc), "异常里应带上错误码：%s" % exc
    else:
        raise AssertionError("EndEdit 返回非 0 时未抛异常 —— 事务失败被静默吞掉")


def test_edit_still_calls_end_edit_when_action_raises(monkeypatch):
    """动作抛异常时仍必须调 EndEdit —— 否则研究会留在编辑态。"""
    m = _load_module()
    fake = _FakeCom()
    _install_fake_get_com_member(m, fake)

    def _boom():
        raise ValueError("动作失败")

    try:
        m._edit(fake, _boom)
    except ValueError:
        pass
    else:
        raise AssertionError("动作异常应原样抛出")

    assert "EndEdit" in fake.names(), (
        "动作抛异常后没调 EndEdit —— 研究会留在编辑态：%s" % fake.names()
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**T-008 的契约测试**）+ `specs/001-topology-result-readout`
# 文件:   `tests/test_sw_topology_contract.py` —— 追加 `collect_topology_numbers` 的契约测试
# 官方签名依据: 反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWResults` 段（裁决者）
# 定位:   做 `specs/001-topology-result-readout/tasks.md` 的 **T-008**。
#         spec 的 T-007 验收要求两条**形态契约**：
#           ① 有结果 ⇒ 返回读数，且**每个读数附来源成员名**（可复查）
#           ② **未跑过 ⇒ `{"status": "no_results", …}`，不抛未捕获异常、不静默空 dict**
#         本文件用**假对象**（无 COM）把这两条形态**钉死** ——
#         真机那一次由 `tools/capture_topology_evidence.py` 的闭环负责（003 已证）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本文件**不连 SolidWorks**（沿用本文件既有约定：静态比对）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────


class _FakeResults:
    """`ICWResults` 的替身：只实现本模块**实际调用**的无参数成员。"""

    def __init__(self, plots=None, steps=None):
        self._plots = plots
        self._steps = steps

    GetPlotCount = property(lambda self: 0 if self._plots is None else len(self._plots))
    GetPlotNames = property(lambda self: (() if self._plots is None else tuple(self._plots)))
    GetMaximumAvailableSteps = property(lambda self: self._steps)


class _FakeStudy:
    """`ICWStudy` 的替身。`results=None` 表示**还没跑过**（合法状态，不是异常）。"""

    def __init__(self, results):
        self.Results = results


def _call(study):
    module = _load_module()
    return module.collect_topology_numbers(study)


def test_collect_numbers_without_results_reports_no_results() -> None:
    """★ T-007 形态②：`Results` 为 None ⇒ **明确报无结果**，不抛异常、不空 dict。"""
    got = _call(_FakeStudy(None))
    assert got["status"] == "no_results"
    assert "Results" in got["reason"], got
    assert got["source_members"]["results"] == "ICWStudy.Results"
    assert set(got) >= {"status", "reason", "source_members"}


def test_collect_numbers_with_zero_plots_reports_no_results() -> None:
    """`Results` 非 None 但**零张图** ⇒ 同样是「无结果」（**不用返回码判**）。"""
    got = _call(_FakeStudy(_FakeResults(plots=None)))
    assert got["status"] == "no_results"
    assert "GetPlotCount" in got["reason"], got


def test_collect_numbers_with_plots_reports_ok_and_source_members() -> None:
    """★ T-007 形态①：有图 ⇒ 返回读数，且**每个读数附来源成员名**（spec 硬要求）。"""
    got = _call(_FakeStudy(_FakeResults(plots=["品质1", "材料质量1"], steps=1)))
    assert got["status"] == "ok", got
    assert got["plot_count"] == 2
    assert got["plot_names"] == ["品质1", "材料质量1"]
    assert got["material_mass_plot"] == "材料质量1"
    assert got["max_available_steps"] == 1
    # **可复查性**：每个读数都要指得出是哪个官方成员给的
    assert got["source_members"] == {
        "results": "ICWStudy.Results",
        "plot_count": "ICWResults.GetPlotCount",
        "plot_names": "ICWResults.GetPlotNames",
        "max_available_steps": "ICWResults.GetMaximumAvailableSteps",
    }


def test_collect_numbers_matches_english_material_mass_name() -> None:
    """判据**不硬编码中文**（spec §Assumptions）：英文界面的 `Material Mass 1` 也要命中。"""
    got = _call(_FakeStudy(_FakeResults(plots=["Stress1", "Material Mass 1"], steps=3)))
    assert got["material_mass_plot"] == "Material Mass 1"


def test_collect_numbers_returns_none_when_material_mass_absent() -> None:
    """有图但**没有** Material Mass ⇒ `material_mass_plot` 为 `None`（不是报错）。"""
    got = _call(_FakeStudy(_FakeResults(plots=["应力1"], steps=1)))
    assert got["status"] == "ok"
    assert got["material_mass_plot"] is None


def test_unresolved_members_are_documented_with_reasons() -> None:
    """★ **事实 30/铁律 5 的守卫**：参数语义查不到的成员要**登记原因**，不能悄悄实现。

    ⚠ 6 条里每一条都必须给出「为什么没实现」，否则下一个人会以为「忘了写」。
    """
    module = _load_module()
    unresolved = module.TOPOLOGY_RESULTS_UNRESOLVED
    assert len(unresolved) == 6, sorted(unresolved)
    for name, why in unresolved.items():
        assert why.strip(), "%s 没有给原因" % name
        assert ("无文档" in why or "无官方" in why or "未给" in why or "一源" in why), (
            "%s 的原因没说清是「参数语义查不到」还是「只有一源」" % name)
    # 这几个**正是** T-004 逐个核过「不存在」之外的、反射里**存在**的那批
    assert "GetMinMaxDisplacement" in unresolved
    assert "SavePlotsAseDrawings" in unresolved
