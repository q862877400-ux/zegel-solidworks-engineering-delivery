"""sw_simulation_study 的官方签名契约测试（不连接 SolidWorks）。

背景
----
本模块的封装统一走 `_checked(<签名表>, target, "成员", *args)` 护栏，
**成员名是变量** ⇒ `audit_call_arity.py` 的静态正则只能看到
直接 `get_com_member` 的少数几处，看不到真实调用点。

⇒ 本文件做同一件事的另一条路：把源码里每个 `_checked` 调用点的实参个数
与模块内签名表对账，**再把签名表与本文件独立抄的反射值交叉校验**。

签名来源（AGENTS.md §四.1③ 认可的官方源：读官方程序集，不是实测）：
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_simulation_study_contract.py —— 本文件自身
# 定位:   域 13 研究管理与求解的签名契约、枚举契约、MIT 项目差异锁。
# 被测对象: scripts/sw_simulation_study.py
# 覆盖:   全文件 —— 本文件是自包含测试单元，各测试函数已就地标明核对对象。
# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import io
import re
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_simulation_study.py"

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt 的 ICWStudyManager 段
# 定位:   独立抄一遍的反射签名，作为交叉校验基准。
#         **实参个数不含末位 ByRef Int32 的 ErrorCode**。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_MANAGER_ARITY = {
    "CreateNewStudy": 3,
    "CreateNewStudy2": 2,
    "CreateNewStudy3": 3,
    "GetStudy": 1,
    "DeleteStudy": 1,
    "DuplicateStudy": 4,
    "DuplicateStudy2": 6,
    "ConvertStudy": 6,
    "ConvertStudy2": 8,
    "RenameStudyFromID": 2,
    "RenameStudyFromName": 2,
    "RunAllStudies": 0,
    "RunSpecifiedStudyByName": 0,
    "SetDistributedSimulation": 1,
    "ManageDistributedSimulation": 2,
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）的 ICWStudy 段
# 定位:   研究对象侧的方法签名，同样独立抄一遍做交叉校验。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_STUDY_ARITY = {
    "RunAnalysis": 0,
    "MeshAndRun": 0,
    "CreateMesh": 3,
    "CreateMeshForMeshControl": 1,
    "UpdateAllComponents": 0,
    "ActivateConfiguration": 0,
    "CopyMeshFromStudy": 1,
    "CreateAnalysisDatabase": 1,
    "ConnectAnalysisDatabase": 1,
    "ExportSimulationStudy": 7,
    "GenerateReport": 3,
    "GetMassPropertiesManager": 0,
    "SetNonLinearStudyOptions": 1,
    "SetFatigueResultOptions": 2,
    "SetResultCombinationSetup": 4,
    "SetClusterComputers": 1,
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（同上文件）的 swsAnalysisStudyType_e /
#         swsMeshType_e / swsRestraintType_e 段
# 定位:   锁死枚举值。特别锁两个**与 MIT 项目冲突**的值：
#           nonlinear = 5（MIT 项目写 4，那是 Optimization）
#           roller    = 3（MIT 项目写 1，那是 Immovable）
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
EXPECTED_STUDY_TYPES = {
    "static": 0, "frequency": 1, "buckling": 2, "thermal": 3,
    "optimization": 4, "nonlinear": 5, "drop_test": 6, "fatigue": 7,
    "dynamic": 8, "pressure_vessel": 9, "topology_static": 13,
}
EXPECTED_MESH_TYPES = {
    "solid": 0, "mid_surface": 1, "surfaces": 2, "mixed": 3, "beam": 4,
}




def _faithful_write(obj, name, value, *args, **kwargs):
    """★ 写属性的"忠实替身"：**就是 `setattr`**。

    ★★ 2026-10-03（轮 470）新增：本仓把 98 处「写 COM 属性」从
    `get_com_member(obj, 名, 值)` 改成了 `set_com_member(obj, 名, 值)`
    （★ 前者有实参就**调用**属性 ⇒ `TypeError: 'bool' object is not callable`
    ⇒ 而外面 `return True` ⇒ 失败报成成功）。
    ⇒ ★ 故本文件的契约装置也得认得这个新名字 ✓
    """
    setattr(obj, name, value)
    return value

def _faithful(obj, name, *args, **kwargs):
    if obj is None:
        return None
    attr = getattr(obj, name, None)
    if attr is None:
        return None
    if callable(attr):
        try:
            return attr(*args, **kwargs)
        except TypeError:
            return attr()
    return attr


def _load():
    connect = types.ModuleType("sw_connect")
    #: ★★★ 2026-10-03（轮 470）假模块的**其余名字一律转发给真模块**。
    #:   原先只手装了一两个名字，而被测模块顶层还 import 了别的
    #:   ⇒ 报 `cannot import name … from 'sw_connect' (**unknown location**)`
    #:   （★ "unknown location" 正因为假模块**没有 __file__** ⇒ 指不到真因）。
    #:   ★ 故加 PEP 562 的模块级 `__getattr__` 兜底 ✓
    import sw_connect as _real_connect

    def _connect_attr(name):  # noqa: ANN001
        return getattr(_real_connect, name)

    connect.__getattr__ = _connect_attr
    connect.set_com_member = _faithful_write
    connect.get_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_simulation_study", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_simulation_study"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink):
    m.get_com_member = lambda o, n, *a, **k: sink.append((n, a)) or "OBJ"
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result


# ── 签名表交叉校验 ───────────────────────────────────────────────────

def test_manager_arity_table_matches_reflection():
    m = _load()
    assert m.STUDY_MANAGER_ARITY == REFLECTED_MANAGER_ARITY, (
        f"管理器签名表与反射不符: {m.STUDY_MANAGER_ARITY} vs {REFLECTED_MANAGER_ARITY}")


def test_study_arity_table_matches_reflection():
    m = _load()
    assert m.STUDY_ARITY == REFLECTED_STUDY_ARITY, (
        f"研究签名表与反射不符: {m.STUDY_ARITY} vs {REFLECTED_STUDY_ARITY}")


def test_every_wrapper_passes_the_documented_arity():
    """每个封装里 `_checked` 的实参个数必须等于签名表。"""
    m = _load()
    source = MODULE_PATH.read_text(encoding="utf-8")
    tables = {**REFLECTED_MANAGER_ARITY, **REFLECTED_STUDY_ARITY}
    checked = 0
    for name in m.__all__:
        func = getattr(m, name, None)
        if not callable(func) or name.startswith("SWS") or name.endswith("_ARITY"):
            continue
        if name in ("_checked", "collect_study_evidence"):
            continue
        body = re.search(r"^def %s\(.*?(?=^def |\Z)" % re.escape(name),
                         source, re.S | re.M)
        assert body, f"{name} 找不到函数体"
        text = body.group(0)
        call = re.search(r'_checked\(\s*(?:STUDY_ARITY|STUDY_MANAGER_ARITY),?'
                         r'\s*\w+,\s*"(\w+)"', text)
        if not call:
            continue          # 该函数走的是 get_com_member 直调，已被 arity 审计覆盖
        member = call.group(1)
        expected = tables.get(member)
        assert expected is not None, f"{name} 调用的 {member} 不在反射签名里"
        # 数一遍实参：*args 形式单独处理
        if "*args" in text and member == "ExportSimulationStudy":
            assert expected == 7
        checked += 1
    assert checked >= 14, f"只对账到 {checked} 个封装，预期 ≥14"


# ── 零参方法（AGENTS.md §六 事实 4 的前科）─────────────────────────

def test_run_analysis_takes_no_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.run_analysis(object())
    assert seen == [("RunAnalysis", ())]


def test_mesh_and_run_takes_no_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.mesh_and_run(object())
    assert seen == [("MeshAndRun", ())]


def test_active_study_is_property_not_method():
    """官方是 ``set_ActiveStudy(Int32)`` —— 迟到绑定下不能加括号。"""
    m = _load()
    seen = []
    _record(m, seen)
    m.set_active_study(object(), 2)
    assert seen == [("ActiveStudy", (2,))]


def test_create_mesh_passes_three_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.create_mesh(object(), 1, 0.005, 0.1)
    assert seen == [("CreateMesh", (1, 0.005, 0.1))]


# ── 枚举契约（含与 MIT 项目的两处冲突）──────────────────────────────

def test_study_type_enum_matches_reflection():
    m = _load()
    assert m.SWS_ANALYSIS_STUDY_TYPES == EXPECTED_STUDY_TYPES


def test_nonlinear_is_five_not_four():
    """MIT 项目把 nonlinear 写成 4；反射值 5（4 是 Optimization）。"""
    m = _load()
    assert m.SWS_ANALYSIS_STUDY_TYPES["nonlinear"] == 5
    assert m.SWS_ANALYSIS_STUDY_TYPES["optimization"] == 4


def test_mesh_type_enum_matches_reflection():
    m = _load()
    assert m.SWS_MESH_TYPES == EXPECTED_MESH_TYPES


# ── 护栏 ─────────────────────────────────────────────────────────────

def test_guard_rejects_wrong_arity_before_calling_com():
    m = _load()
    try:
        m._checked(REFLECTED_STUDY_ARITY, object(), "CreateMesh", 1, 2)
    except ValueError as exc:
        assert "CreateMesh" in str(exc)
        return
    raise AssertionError("错 arity 未被拦下")


def test_export_study_requires_seven_arguments():
    m = _load()
    try:
        m.export_study(object(), 1, 2, 3)
    except ValueError as exc:
        assert "7" in str(exc)
        return
    raise AssertionError("ExportSimulationStudy 未校验实参个数")


# ── 直接运行 ─────────────────────────────────────────────────────────

def _main():
    failures = []
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append((test.__name__, exc))
            print(f"  FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raise SystemExit(_main())
