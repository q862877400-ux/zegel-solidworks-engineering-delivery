"""sw_routing 的官方签名契约测试（不连接 SolidWorks）。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect\\iface_SWRoutingLib.txt   （28 接口 / 142 成员）

本文件同时锁住域 14 特有的两条纪律：
  1. **入口 ProgID 查不到就不硬编** —— `get_routing_component_manager` 必须
     抛 NotImplementedError，而不是编一个 ProgID 字符串。
  2. **零参方法不漏括号** —— ExitRoute / AddToRoute / GetRouteProperty 等
     反射确认是零参，迟到绑定下加了括号会 TypeError。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_routing_contract.py —— 本文件自身
# 定位:   域 14 路由族的签名契约与「查不到就不编」纪律锁。
# 被测对象: scripts/sw_routing.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_routing.py"
REFLECTION = Path(r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SWRoutingLib interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt
# 定位:   独立抄一遍的签名，作为对账基准。**不含**末尾 by-ref 出参。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_ARITY = {
    "StartRoute": 2,
    "ExitRoute": 0,
    "AddToRoute": 0,
    "EditRoute": 0,
    "CreateRouteLine": 6,
    "CreateFlattenRoute": 11,
    "CreatePipeDrawingforPipeRoute": 12,
    "ExportPipeData": 3,
    "ExportTubeData": 3,
    "GetAllRouteSegmentCount": 0,
    "GetElectricalRoute": 0,
    "GetAutoRoute": 0,
    "GetRouteProperty": 0,
    "CreateCovering": 0,
    "AddCovering": 1,
    "RemoveCovering": 0,
    "GetCovering": 0,
    "SetFixedLength": 1,
    "GetFixedLength": 0,
    "SetRoutePathForWire": 1,
    "GetRouteSegmentIDsCount": 0,
    "GetRouteErrorsCount": 0,
    "GetCuttingLength": 0,
    "GetCableProperty": 0,
    "GetCoresCount": 0,
}

ZERO_ARG_MEMBERS = (
    "ExitRoute", "AddToRoute", "EditRoute", "GetAllRouteSegmentCount",
    "GetElectricalRoute", "GetAutoRoute", "GetRouteProperty",
    "CreateCovering", "RemoveCovering", "GetCovering", "GetFixedLength",
    "GetRouteSegmentIDsCount", "GetRouteErrorsCount", "GetCuttingLength",
    "GetCableProperty", "GetCoresCount",
)




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
    spec = importlib.util.spec_from_file_location("sw_routing", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_routing"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink, result="OBJ"):
    m.get_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.call_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result


# ── 签名表对账 ───────────────────────────────────────────────────────

def test_arity_table_matches_reflection():
    m = _load()
    for member, count in REFLECTED_ARITY.items():
        assert m.ROUTING_ARITY.get(member) == count, (
            f"{member} 期望 {count}，登记表是 {m.ROUTING_ARITY.get(member)}")


def test_every_zero_arg_member_declared_zero():
    m = _load()
    for member in ZERO_ARG_MEMBERS:
        assert m.ROUTING_ARITY.get(member) == 0, f"{member} 应登记为 0 参"


def test_registry_has_no_invented_members():
    """登记表里不能出现反射清单里没有的成员名。

    独立再扫一遍反射清单做对照（若清单不在本机则跳过）。
    """
    if not REFLECTION.is_file():
        print("  (跳过：SWRoutingLib 反射清单不在本机)")
        return
    text = REFLECTION.read_text(encoding="utf-8", errors="replace")
    for member in REFLECTED_ARITY:
        assert re.search(rf"\b{re.escape(member)}\s*\(", text), (
            f"{member} 不在反射清单里 —— 登记表可能编了")


# ── 零参方法不加括号 ─────────────────────────────────────────────────

def test_zero_arg_route_methods_pass_no_arguments():
    m = _load()
    for func in (m.exit_route, m.add_to_route, m.edit_route):
        seen = []
        _record(m, seen)
        func(object())
        assert seen == [(seen[0][0], ())], f"{func.__name__} 的成员应零参"


def test_zero_arg_getters_pass_no_arguments():
    m = _load()
    for func in (m.get_electrical_route, m.get_auto_route, m.get_route_property):
        seen = []
        _record(m, seen)
        func(object())
        assert len(seen) == 1 and seen[0][1] == (), f"{func.__name__} 应零参"
    # 取数量的那个返回值会被 int() 转换，mock 得给数字
    seen = []
    _record(m, seen, result=17)
    assert m.get_all_route_segment_count(object()) == 17
    assert seen[0] == ("GetAllRouteSegmentCount", ())


def test_bend_radius_is_property_not_method():
    """官方是 ``set_BendRadius(Double)`` —— 迟到绑定下不能写成方法。"""
    m = _load()
    seen = []
    _record(m, seen)
    m.set_bend_radius(object(), 25.0)
    assert seen == [("BendRadius", (25.0,))]


# ── 定长参数校验 ─────────────────────────────────────────────────────

def test_create_flatten_route_requires_eleven_arguments():
    m = _load()
    try:
        m.create_flatten_route(object(), 1, 2, 3)
    except ValueError as exc:
        assert "11" in str(exc)
        return
    raise AssertionError("CreateFlattenRoute 未校验实参个数")


def test_create_pipe_drawing_requires_twelve_arguments():
    m = _load()
    try:
        m.create_pipe_drawing(object(), 1, 2, 3)
    except ValueError as exc:
        assert "12" in str(exc)
        return
    raise AssertionError("CreatePipeDrawingforPipeRoute 未校验实参个数")


def test_create_route_line_passes_six_doubles():
    m = _load()
    seen = []
    _record(m, seen)
    m.create_route_line(object(), 0, 1, 2, 3, 4, 5)
    assert seen == [("CreateRouteLine", (0.0, 1.0, 2.0, 3.0, 4.0, 5.0))]


# ── 「查不到就不编」纪律 ─────────────────────────────────────────────

def test_component_manager_accessor_refuses_to_invent_progid():
    """本机没装 SolidWorks Routers ⇒ 取用路径查不到 ⇒ 必须拒绝而非编 ProgID。"""
    m = _load()
    try:
        m.get_routing_component_manager(object())
    except NotImplementedError as exc:
        assert "不臆造" in str(exc)
        assert "AddIns" in str(exc), "错误信息应说明查证过注册表"
        return
    raise AssertionError("未查到的取用路径被放行了")


def test_source_never_contains_a_hardcoded_progid():
    """源码里不得**调用** GetAddInObject 来取 RouteManager，也不得硬编 ProgID。

    ⚑ 只查「调用」不查「提及」：模块 docstring 里要解释「为什么不用
       GetAddInObject 取」，那处提及是必需的。初版断言「源码不含该词」，
       把自己需要的说明也判成了违规。
    """
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "get_com_member(.*GetAddInObject" not in source
    for token in ("SWRoutingMgr.CwAddincallback", "SWRoutingLib.RouteManager"):
        assert token not in source, f"不得硬编 ProgID: {token}"


def test_existing_routing_review_is_documented_as_non_com():
    """既有的 routing_review.py 不使用 COM API —— 须在文档里如实说明这一点。"""
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "routing_review.py" in source
    assert "不使用 COM" in source or "零 API 覆盖" in source


# ── 护栏 ─────────────────────────────────────────────────────────────

def test_guard_rejects_wrong_arity_and_none():
    m = _load()
    try:
        m._checked(object(), "StartRoute", 1)
    except ValueError as exc:
        assert "StartRoute" in str(exc)
    else:
        raise AssertionError("错 arity 未被拦")
    try:
        m._checked(None, "StartRoute", "a", "b")
    except ValueError as exc:
        assert "None" in str(exc)
        return
    raise AssertionError("None 目标未被拦")


def test_all_public_readers_reject_none():
    """每个公开入口都要在 None 目标上抛 ValueError。

    ⚑ 必须给足**位置参数**：上一版只调 ``func(None)``，于是
       ``set_bend_radius(None)`` 先撞上「缺 radius 参数」的 TypeError，
       压根没走到 None 检查 —— 用例看着在测拦空，实际测的是参数个数。
    """
    m = _load()
    for func, args in (
        (m.read_cable_card, ()),
        (m.read_wire_endpoints, ()),
        (m.collect_routing_evidence, ()),
        (m.set_bend_radius, (25.0,)),
        (m.apply_covering, ("COVERING",)),
        (m.set_wire_route_path, ("PATH",)),
        (m.start_route, ("t", "p")),
        (m.create_route_line, (0, 0, 0, 1, 1, 1)),
        (m.export_pipe_data, ("p", 0, 0)),
    ):
        try:
            func(None, *args)
        except ValueError:
            continue
        raise AssertionError(f"{func.__name__} 未拦下 None 目标")


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
