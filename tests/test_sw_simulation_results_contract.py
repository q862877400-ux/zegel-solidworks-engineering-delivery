"""sw_simulation_results 的官方签名契约测试（不连接 SolidWorks）。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
    D:\\AI\\SW\\_raw\\reflect\\enum_cosworks.txt

本模块所有封装走 `_checked(<签名表>, target, "成员", *args)` 护栏，
成员名是变量 ⇒ arity 审计只覆盖直接 get_com_member 的少数调用点。
本文件用「源码实参个数 ↔ 签名表 ↔ 本文件独立抄的反射值」三方对账补上这一段。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_simulation_results_contract.py —— 本文件自身
# 定位:   域 13 结果/网格族的签名契约、枚举契约、by-ref 行为锁。
# 被测对象: scripts/sw_simulation_results.py
# 覆盖:   全文件 —— 本文件是自包含测试单元，各测试函数已就地标明核对对象。
# ⚠ 本文件为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import io
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_simulation_results.py"

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt 的 ICWResults / ICWMesh 段
# 定位:   独立抄一遍的反射签名，作为三方对账的第三方基准。
#         **不含**末位 by-ref 出参。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_RESULTS_ARITY = {
    "CreatePlot": 4,
    "CreateDeformedBody": 2,
    "CreateDeformedBody2": 5,
    "ActivatePlot": 1,
    "DeletePlot": 1,
    "GetDisplacementAtPoints": 5,
    "GetBucklingLoadFactors": 0,
    "CreateStressHotSpotPlot": 2,
    "AddIsoClippingToPlot": 5,
}

REFLECTED_MESH_ARITY = {
    "GetNodeLocation": 1,
    "GetElementLocation": 1,
    "GetWorstJacobianRatio": 0,
    "IsComponentFailed": 1,
    "IsComponentFailed2": 1,
    "GetNoOfFailedComponents": 0,
    "GetMeshControlAt": 1,
    "DeleteMeshControl": 1,
    "GetDefaultElementSizeAndTolerance": 1,
    "GetDefaultMaxAndMinElementSize": 1,
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（enum_cosworks.txt）
#         → swsStaticResultNodalStressComponentTypes_e / swsMeshQuality_e /
#           swsMesherType_e 段
# 定位:   锁死三张枚举表。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
EXPECTED_STRESS_COMPONENTS = {
    "sx": 0, "sy": 1, "sz": 2, "txy": 3, "txz": 4, "tyz": 5,
    "p1": 6, "p2": 7, "p3": 8,
}
EXPECTED_QUALITY = {"draft": 0, "high": 1}
EXPECTED_MESHER = {"standard": 0, "alternate": 1, "alternate_cb": 2}


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
    connect.get_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_simulation_results", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_simulation_results"] = module
    spec.loader.exec_module(module)
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink, result="OBJ"):
    m.get_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result


# ── 签名表三方对账 ───────────────────────────────────────────────────

def test_results_arity_table_matches_reflection():
    m = _load()
    assert m.RESULTS_ARITY == REFLECTED_RESULTS_ARITY, (
        f"结果签名表与反射不符:\n  模块 {m.RESULTS_ARITY}\n  反射 {REFLECTED_RESULTS_ARITY}")


def test_mesh_arity_table_matches_reflection():
    m = _load()
    assert m.MESH_ARITY == REFLECTED_MESH_ARITY, (
        f"网格签名表与反射不符:\n  模块 {m.MESH_ARITY}\n  反射 {REFLECTED_MESH_ARITY}")


# ── 调用形态 ─────────────────────────────────────────────────────────

def test_create_plot_passes_four_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.create_plot(object(), 3, 1, 0, True)
    assert seen == [("CreatePlot", (3, 1, 0, True))]


def test_worst_jacobian_ratio_takes_no_arguments():
    m = _load()
    seen = []
    _record(m, seen, result=0.87)
    assert m.get_worst_jacobian_ratio(object()) == 0.87
    assert seen == [("GetWorstJacobianRatio", ())]


def test_component_failed_uses_variant_two_returning_boolean():
    """官方 IsComponentFailed 返回 Int32、IsComponentFailed2 返回 Boolean。
    本封装固定用 2 号（Boolean），不得混用。"""
    m = _load()
    seen = []
    _record(m, seen, result=1)
    assert m.is_component_failed(object(), "Part1") is True
    assert seen == [("IsComponentFailed2", ("Part1",))]


def test_node_location_passes_one_argument_only():
    """官方是 (Int32, Double&, Double&, Double&) —— 三个 by-ref 出参。
    本模块传 1 个实参，**取不到坐标**，这是刻意行为（见模块头）。"""
    m = _load()
    seen = []
    _record(m, seen)
    m.get_mesh_node_location(object(), 7)
    assert seen == [("GetNodeLocation", (7,))]


def test_buckling_load_factors_takes_no_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.get_buckling_load_factors(object())
    assert seen == [("GetBucklingLoadFactors", ())]


# ── 护栏 ─────────────────────────────────────────────────────────────

def test_guard_rejects_wrong_arity_before_calling_com():
    m = _load()
    for table, member, args in (
        (REFLECTED_RESULTS_ARITY, "CreatePlot", (1, 2)),
        (REFLECTED_MESH_ARITY, "GetWorstJacobianRatio", (1,)),
    ):
        try:
            m._checked(table, object(), member, *args)
        except ValueError as exc:
            assert member in str(exc)
            continue
        raise AssertionError(f"{member} 错 arity 未被拦下")


def test_guard_rejects_none_target():
    m = _load()
    try:
        m._checked(REFLECTED_MESH_ARITY, None, "GetNoOfFailedComponents")
    except ValueError as exc:
        assert "None" in str(exc)
        return
    raise AssertionError("None 目标未被拦下")


# ── 枚举契约 ─────────────────────────────────────────────────────────

def test_enum_values_match_reflection():
    m = _load()
    assert m.SWS_NODAL_STRESS_COMPONENTS == EXPECTED_STRESS_COMPONENTS
    assert m.SWS_MESH_QUALITY == EXPECTED_QUALITY
    assert m.SWS_MESHER_TYPES == EXPECTED_MESHER


def test_mesh_evidence_reads_zero_argument_properties():
    """collect_mesh_evidence 里的方法型读取必须都是零参。"""
    m = _load()
    seen = []
    _record(m, seen)
    m.get_com_member = lambda o, n, *a, **k: (
        seen.append((n, a)) or (0.75 if n == "GetWorstJacobianRatio" else 5))
    m.collect_mesh_evidence(object())
    for name, args in seen:
        assert args == (), f"{name} 带实参 {args}，但反射确认是零参属性/方法"


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
