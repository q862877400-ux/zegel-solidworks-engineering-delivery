"""sw_simulation_loadprops 的官方签名契约测试（不连接 SolidWorks）。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt

本文件锁住三件事：
  1. **编辑事务**（ForceBeginEdit / ForceEndEdit，零参）必须包住属性设置
  2. **同形成员不混用**（IncludeNonUniformDistribution 的 Int32 / Boolean 两版）
  3. **无 setter 的族要显式拒绝**，不静默忽略（压力 / 热流 / 接触对）

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_simulation_loadprops_contract.py —— 本文件自身
# 定位:   域 13 载荷对象属性层的契约。
# 被测对象: scripts/sw_simulation_loadprops.py
#         scripts/sw_simulation.py::apply_normal_force（补正后的编辑事务）
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_simulation_loadprops.py"
SIM_PATH = REPO_ROOT / "scripts" / "sw_simulation.py"

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（cosworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
# 定位:   独立抄一遍的关键签名，作为对账基准。
#     ICWForce      : Void  ForceBeginEdit()      ← 零参
#                      Int32  ForceEndEdit()       ← 零参
#                      Void set_NormalForceOrTorqueValue(Double)
#                      Void set_ForceType(Int32) / set_Unit(Int32)
#                      Void set_IncludeNonUniformDistribution2(Boolean)
#     ICWContactSet : Void  ContactSetBeginEdit() ← 零参
#                      Int32  ContactSetEndEdit()  ← 零参
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
ZERO_ARG_EDIT_MEMBERS = ("ForceBeginEdit", "ForceEndEdit",
                         "ContactSetBeginEdit", "ContactSetEndEdit")


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
    for mod, attrs in (
        ("sw_connect", {"get_com_member": _faithful, "save_document": lambda *a, **k: None}),
        ("sw_document_data", {"set_custom_properties": lambda *a, **k: None}),
        ("sw_part", {"_ensure_sketch_selected": lambda *a, **k: None}),
        ("sw_preflight", {"import_com_dependencies": lambda: (None, None, None)}),
    ):
        module = types.ModuleType(mod)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules.setdefault(mod, module)
    spec = importlib.util.spec_from_file_location("sw_simulation_loadprops", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_simulation_loadprops"] = module
    spec.loader.exec_module(module)
    module.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful
    module.call_com_member = _faithful
    return module


# ── 编辑事务 ─────────────────────────────────────────────────────────

def test_edit_transaction_pairs_are_zero_argument_names():
    m = _load()
    for begin, end in (m.FORCE_BEGIN_EDIT, m.CONTACT_SET_BEGIN_EDIT):
        assert begin in ZERO_ARG_EDIT_MEMBERS and end in ZERO_ARG_EDIT_MEMBERS


def test_configure_force_wraps_everything_in_edit_transaction():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or 0
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, v: (seen.append((n, (v,))) or 0)
    m.configure_force(object(), magnitude=100.0, force_type=1, unit=0)
    names = [n for n, _ in seen]
    assert names[0] == "ForceBeginEdit", "属性设置前必须先开编辑事务"
    assert names[-1] == "ForceEndEdit", "结束后必须收尾"
    assert seen[0][1] == () and seen[-1][1] == (), "Begin/End 反射确认是零参"


def test_edit_transaction_closes_even_when_a_property_raises():
    """异常路径也必须调 EndEdit，否则编辑事务会悬着。"""
    m = _load()
    seen = []

    def _boom(obj, name, *args, **kwargs):
        seen.append((name, args))
        if name == "NormalForceOrTorqueValue":
            raise RuntimeError("属性设置失败")
        return 0

    m.get_com_member = _boom
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = _boom
    m.call_com_member = _boom
    try:
        m.configure_force(object(), magnitude=1.0)
    except RuntimeError:
        pass
    else:
        raise AssertionError("异常没有向上传播")
    names = [n for n, _ in seen]
    assert names[0] == "ForceBeginEdit"
    assert names[-1] == "ForceEndEdit", "异常时也要收尾"


def test_context_manager_rejects_none_target():
    m = _load()
    try:
        with m.edit_transaction(None, m.FORCE_BEGIN_EDIT, "ICWForce"):
            pass
    except ValueError as exc:
        assert "None" in str(exc)
        return
    raise AssertionError("None 目标未被拦下")


# ── 同形成员不混用 ───────────────────────────────────────────────────

def test_non_uniform_uses_boolean_variant_only():
    """反射有 Int32 与 Boolean 两个同形成员；本封装只用 Boolean 版。"""
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or 0
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, v: (seen.append((n, (v,))) or 0)
    m.configure_force(object(), include_non_uniform=True)
    names = [n for n, _ in seen]
    assert "IncludeNonUniformDistribution2" in names
    assert "IncludeNonUniformDistribution" not in names


def test_apply_normal_force_in_simulation_module_also_opens_transaction():
    """scripts/sw_simulation.py::apply_normal_force 初稿没开事务，本轮补正。
    这个测试锁住补正不反弹。

    ⚑ 必须用**带引号**的形式找：裸词 ``ForceBeginEdit`` 会先命中补正说明的
       注释块（偏移 16079/16098），而不是真正的调用（16324/16609）。
       注释里 Begin 与 End 是挨着的，于是用裸词比较会得到
       ``begin < 设置 < end`` 不成立 —— 那是量错了地方，不是代码有问题。
       （本测试初版就栽在这里。）
    """
    source = SIM_PATH.read_text(encoding="utf-8")
    begin = source.index('"ForceBeginEdit"')
    end = source.index('"ForceEndEdit"')
    first_set = min(
        (i for i in [source.find('"ForceType"'), source.find('"Unit"'),
                     source.find('"NormalForceOrTorqueValue"')] if i > 0),
        default=len(source))
    assert begin < first_set < end, (
        f"事务必须包住属性设置：begin={begin} 设置={first_set} end={end}")


# ── 无 setter 的族要显式拒绝 ─────────────────────────────────────────

def test_pressure_rejects_unsupported_argument_loudly():
    m = _load()
    try:
        m.configure_pressure(object(), reverse_direction=True)
    except ValueError as exc:
        assert "setter" in str(exc)
        return
    raise AssertionError("无 setter 的参数被静默忽略了 —— 那比报错更糟")


def test_pressure_readback_uses_boolean_reverse_variant():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append(n) or 7
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, *a, **k: seen.append(n) or 7
    result = m.configure_pressure(object())
    assert result["pressure_type"] == 7
    assert "ReverseDirection2" in seen and "ReverseDirection" not in seen


def test_heat_flux_and_contact_set_are_read_only():
    """反射这两个族无 setter，模块如实只读（不编可写的假象）。"""
    m = _load()
    m.get_com_member = lambda o, n, *a, **k: 1.0
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, *a, **k: 1.0
    assert isinstance(m.configure_heat_flux(object()), dict)
    assert isinstance(m.configure_contact_set(object()), dict)
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "无 setter" in source or "没有任何 set_" in source


def test_all_reject_none_target():
    m = _load()
    for func in (m.configure_force, m.configure_pressure, m.configure_heat_flux,
                 m.configure_contact_set, m.read_material_card,
                 m.collect_load_property_evidence):
        try:
            func(None)
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
