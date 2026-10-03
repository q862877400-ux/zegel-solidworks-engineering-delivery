"""sw_simulation_loads 的官方签名契约测试（不连接 SolidWorks）。

关键背景
--------
本模块的每个 `add_*` 都走共用护栏 `_check(manager, "AddX", <实参个数>, ...)`，
**成员名是变量**，因此 `audit_call_arity.py` 的静态正则看不见真实调用点
（它只能看到 3 处直接 `get_com_member`）。

⇒ 本文件用另一种方式做同一件事：**把模块源码里每个 `_check` 的实参个数
与模块内 `OFFICIAL_LOAD_SIGNATURES` 签名表（照抄官方 VB 声明）逐一对账**。
签名表本身错了，对账也会一起错 —— 所以表的值在测试里**再抄一份**做交叉校验。

官方签名依据（CHM cosworks 册，34 个接口页，已用 JSON 转义解码器提取）：
    D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\
    → D:\\AI\\SW\\_raw\\cosworks_signatures.md

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_simulation_loads_contract.py —— 本文件自身
# 定位:   域 13 Simulation 载荷夹具的签名契约与枚举值契约。
# 被测对象: scripts/sw_simulation_loads.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_simulation_loads.py"

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方文档（CHM cosworks 册）
# 文件:   D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\
#           ICWLoadsAndRestraintsManager~<方法>.html 的 Visual Basic (Declaration) 段
# 定位:   下面这份「官方实参个数」是**独立抄一遍**的交叉校验基准 ——
#         模块内的 OFFICIAL_LOAD_SIGNATURES 若抄错，这里能发现。
# 取值:   逐条从官方 VB 声明数出，**不含**末位 ByRef ErrorCode
#         （pywin32 迟到绑定传 0 占位，见模块头说明）。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
OFFICIAL_ARITY_FROM_DOCS = {
    "AddRestraint": 3,
    "AddCyclicSymmetryRestraint": 3,
    "AddPrescribedDisplacement": 4,
    "AddBearingLoad": 2,
    "AddForce": 3,
    "AddForce2": 4,
    "AddForce3": 20,
    "AddPressure": 3,
    "AddRemoteLoad": 6,
    "AddGravity": 1,
    "AddCentrifugalForce": 1,
    "AddDistributedMass": 3,
    "AddTemperature": 1,
    "AddHeatFlux": 1,
    "AddHeatPower": 1,
    "AddConvection": 1,
    "AddRadiation": 2,
    "AddSpringConnector": 3,
    "AddPinConnector": 2,
    "AddRigidConnector": 2,
    "AddLinkConnector": 2,
    "AddElasticConnector": 1,
    "AddBoltConnector": 3,
    "AddSpotWeldConnector": 3,
    "AddEdgeWeldConnector": 4,
    "GetLoadsAndRestraints": 1,
    "GetEdgeWeldConnector": 1,
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（对 interop 程序集纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\enum_cosworks.txt
# 定位:   下面这组期望值用于锁死枚举表，防止后人凭印象改数值。
# ⚠ 官方 CHM cosworks 册**没有枚举页**，枚举值只能来自反射。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
EXPECTED_ENUM_VALUES = {
    "SWS_RESTRAINT_TYPES": {
        "fixed": 0, "immovable": 1, "symmetric": 2, "roller": 3, "hinge": 4,
        "reference_geometry": 5, "flat_face": 6, "cylindrical_faces": 7,
        "spherical_surface": 8, "cyclic_symmetry": 9,
    },
    "SWS_FORCE_TYPES": {"force_or_moment": 0, "normal": 1, "torque": 2},
    "SWS_PRESSURE_TYPES": {"normal": 0, "use_reference_geometry": 1},
    "SWS_RADIATION_TYPES": {"surface_to_ambient": 0, "surface_to_surface": 1},
    "SWS_SPRING_SUBTYPES": {
        "flat_parallel_faces": 0, "concentric_cylindrical_faces": 1,
        "between_vertices": 2,
    },
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


def _fake_empty_dispatch():
    """★ 空 Dispatch 参数包（★ 与 `sw_connect.create_empty_dispatch_variant` 同形，事实 12）。"""
    import win32com.client as _w

    return _w.VARIANT(_w.pythoncom.VT_DISPATCH | _w.pythoncom.VT_BYREF, None)


def _assert_call(seen, name, *expected):
    """★ 断言"调了 `name`，前几个实参是 `expected`，**末尾多一个 by-ref 出参**"。

    ★★★ 2026-10-01（轮 348）**契约变更** —— 真机确认（`output/loadfamily-evidence.json`）：
      `AddPressure` 那一族官方声明以 **`ByRef ErrorCode`** 收尾，★ **缺它 ⇒
      `DISP_E_PARAMNOTOPTIONAL`「非选择性的参数」**（★ 修前 `L.add_pressure` 就报这个；
      ★ 补上后 `ok=true` 且**回读载荷数 = 1**）。
      ⇒ ★ 修法在**能力层** `_check` 里**统一补 `out_i4()`**（★ 一处 ⇒ 整批受益）。
    ★ 所以本文件里 4 个"断言实参元组**精确相等**"的测试要跟着改。
      ⚠ **不是删掉断言** —— ★ 新断言**更强**：★ 它同时验了
        ① **原来的实参一个没变**（`got_args[:len(expected)] == expected`）·
        ② **末尾确实补了出参**（`isinstance(last, VARIANT)`）。
    """
    import win32com.client as _w

    assert seen, "★ 一次 COM 调用都没有：%r" % (seen,)
    got_name, got_args = seen[0]
    assert got_name == name, got_name
    #: ★★ 逐个比：★ **期望 `None` 的那一位可以是 `None`、也可以是空 Dispatch 参数包** ——
    #:   ★ 因为 `_check` 会把 `None` 换成 `create_empty_dispatch_variant()`（★ 真机必需，位置 3）。
    #:   ★ 而**期望非 `None` 的必须严格相等**（★ 那才验得到"原参数没被改"）。
    for i, want in enumerate(expected):
        got = got_args[i] if i < len(got_args) else "<缺失>"
        if want is None:
            assert got is None or isinstance(got, _w.VARIANT), \
                "★ 第 %d 位期望 None 或空 Dispatch，得到 %r" % (i, got)
        else:
            assert got == want, (i, got, want)
    assert len(got_args) == len(expected) + 1, "★ 末尾应恰好补一个出参：%r" % (got_args,)
    last = got_args[-1]
    assert isinstance(last, _w.VARIANT), "★ 末尾那个应是 by-ref 出参（VARIANT），得到 %r" % (last,)


def _fake_out_i4(value=0):
    """★★ 2026-10-01（轮 348）**假模块也要有 `out_i4`** —— 契约扩展了。

    ★ 真因：`_check` 现在**统一补末尾 `ByRef ErrorCode`** ⇒ 生产代码顶部
      `from sw_connect import …, out_i4` ⇒ ★★ 而这个假模块（`types.ModuleType("sw_connect")`）
      **只提供 `get_com_member` / `call_com_member`** ⇒ `ImportError` ⇒ **本文件 9 个测试全挂**。
    ⚠ **这与轮 344 那次（`set_com_member`）是同一个坑**：
      ★ **mock 是契约的替身 —— 生产代码用了新成员，mock 就要跟上**
      （★ 正解是补 mock，不是让生产代码为测试让步）。
    """
    import win32com.client as _w

    return _w.VARIANT(_w.pythoncom.VT_BYREF | _w.pythoncom.VT_I4, int(value))


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
    connect.out_i4 = _fake_out_i4
    #: ★★★ 2026-10-01（轮 349）**`create_empty_dispatch_variant` 也要提供** ——
    #:   ★ 这是**第三次**同一个坑（前两次：`set_com_member` 轮 344 · `out_i4` 轮 348）：
    #:   ★★ **生产代码多用一个 `sw_connect` 成员，测试的假模块就要跟上**
    #:     （★ 正解是补 mock，不是让生产代码为测试让步）。
    #:   ⚠ 缺它的后果**很隐蔽**：`_check` 里写的是
    #:     `… and create_empty_dispatch_variant is not None`（★ 防御性写法）
    #:     ⇒ ★★ **不会抛错，而是**静默跳过替换**** ⇒ 测试看到 `RefGeom` 仍是裸 `None` ✓
    #:     （★ 比 `ImportError` 更难发现 —— ★ 是那条**新加严的断言**抓到的）。
    connect.create_empty_dispatch_variant = _fake_empty_dispatch
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_simulation_loads", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_simulation_loads"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    module.out_i4 = _fake_out_i4
    module.create_empty_dispatch_variant = _fake_empty_dispatch
    return module


# ── 签名对账 ─────────────────────────────────────────────────────────

def test_module_signature_table_matches_official_docs():
    """模块内的签名表必须与本文件独立抄的官方签名表逐项一致。"""
    m = _load()
    module_table = m.OFFICIAL_LOAD_SIGNATURES
    assert module_table == OFFICIAL_ARITY_FROM_DOCS, (
        "签名表与官方 VB 声明不一致:\n"
        f"  仅模块有: {set(module_table) - set(OFFICIAL_ARITY_FROM_DOCS)}\n"
        f"  仅官方有: {set(OFFICIAL_ARITY_FROM_DOCS) - set(module_table)}\n"
        f"  数值不同: { {k: (module_table.get(k), v) for k, v in OFFICIAL_ARITY_FROM_DOCS.items() if module_table.get(k) != v} }"
    )


def test_every_wrapper_declares_the_documented_arity():
    """`add_*` / `get_*` 封装里 `_check` 的实参个数必须等于官方签名。

    ★ 2026-10-01（24h 段 2.1 / Spec Kit `143`）**收紧范围，而不是放宽**：
      本模块新增了**更高一层的包装** `apply_*_report`（它们调 `add_pressure` 等，
      **不直接**调 `_check`）⇒ 原断言「`__all__` 里每个函数都要有 `_check`」不再成立。
      两条契约分开守，**两层都不丢**：
        · `add_*` / `get_*` ⇒ ★ **必须**直接调 `_check`（原契约，**一个都不放松**）
        · 其余公开函数   ⇒ ★ **必须**调用上面那批之一（新契约：**包的是自家封装**）
    """
    m = _load()
    source = MODULE_PATH.read_text(encoding="utf-8")
    checked = 0
    layered = 0
    #: ★ 先收集"直接调 `_check`"的那批（★ 它们是被包装的对象）
    direct: dict[str, tuple[str, int]] = {}
    for name in m.__all__:
        func = getattr(m, name, None)
        if not callable(func) or name.startswith("SWS"):
            continue
        if name in ("OFFICIAL_LOAD_SIGNATURES", "_require", "_check",
                    "collect_loads_evidence"):
            continue
        body = re.search(r"^def %s\(.*?(?=^def |\Z)" % re.escape(name),
                         source, re.S | re.M)
        assert body, f"{name} 在源码里找不到函数体"
        call = re.search(r'_check\(\s*manager,\s*"(\w+)",\s*(\d+)', body.group(0))
        if call is None:
            continue
        direct[name] = (call.group(1), int(call.group(2)))

    for name in m.__all__:
        func = getattr(m, name, None)
        if not callable(func) or name.startswith("SWS"):
            continue
        if name in ("OFFICIAL_LOAD_SIGNATURES", "_require", "_check",
                    "collect_loads_evidence"):
            continue
        body = re.search(r"^def %s\(.*?(?=^def |\Z)" % re.escape(name),
                         source, re.S | re.M)
        assert body, f"{name} 在源码里找不到函数体"
        text = body.group(0)
        if name in direct:
            member, arity = direct[name]
            expected = OFFICIAL_ARITY_FROM_DOCS.get(member)
            assert expected is not None, f"{name} 调用的 {member} 不在官方签名表里"
            assert arity == expected, (
                f"{name} 声明 {arity} 个实参，官方 {member} 是 {expected} 个")
            checked += 1
            continue
        #: ★ 高层包装：名字以 add_/get_ 开头的**不许**走这条路（★ 那正是原契约的射程）
        assert not (name.startswith("add_") or name.startswith("get_")), (
            f'{name} 是 add_/get_ 封装，必须直接走 _check(manager, "成员", N, ...)')
        #: ★ 它必须调用**上面那批直接调 `_check` 的**函数之一
        assert any(("." + d + "(") in text or (" " + d + "(") in text
                   or ("(" + d + "(") in text for d in direct), (
            f"{name} 既没有直接调 `_check`，也没有调用任何直接调 `_check` 的封装 —— "
            "高层包装必须包自家封装，不许自己发明调用路径")
        layered += 1
    assert checked >= 27, f"只对账到 {checked} 个封装，预期 ≥27"
    assert layered >= 4, f"只对账到 {layered} 个高层包装，预期 ≥4（段 2.1 的四个 apply_*_report）"


def test_arity_guard_rejects_wrong_count_before_calling_com():
    """传错实参个数时，护栏必须在**发起 COM 调用之前**报错。"""
    m = _load()
    try:
        m._check(object(), "AddPressure", 9, "a", "b", "c")
    except ValueError as exc:
        assert "AddPressure" in str(exc) and "9" in str(exc)
        return
    raise AssertionError("错 arity 未被拦下")


def test_arity_guard_passes_through_when_correct():
    m = _load()
    seen = []

    def _record(obj, name, *args, **kwargs):
        seen.append((name, args))
        return "OBJ"

    m.get_com_member = _record
    m.call_com_member = _record
    assert m._check(object(), "AddForce", 3, 1, "E", None) == "OBJ"
    _assert_call(seen, "AddForce", 1, "E", None)


# ── 枚举契约 ─────────────────────────────────────────────────────────

def test_enum_values_match_reflection():
    """五张枚举表逐项对照反射取值。"""
    m = _load()
    for name, expected in EXPECTED_ENUM_VALUES.items():
        actual = getattr(m, name)
        assert actual == expected, f"{name} 与反射值不符：{actual} != {expected}"


def test_reference_geometry_restraint_is_index_five():
    """「参考几何」夹具是唯一需要 RefGeom 的类型（官方 Parameters 段明写）。"""
    m = _load()
    assert m.SWS_RESTRAINT_TYPES["reference_geometry"] == 5
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or "RESTRAINT"
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.add_reference_geometry_restraint(object(), "ENTS", "REFGEOM")
    _assert_call(seen, "AddRestraint", 5, "ENTS", "REFGEOM")


def test_plain_restraint_passes_none_for_ref_geom():
    """非参考几何夹具，RefGeom 传 `None` —— 与官方「valid only if…」一致。

    ★★★ 2026-10-01（轮 349）**而 `_check` 会把它换成空 Dispatch 参数包** ——
      ★ 真机：`AddForce` 的第 3 参裸传 `None` ⇒
        `com_error(-2147352571, '类型不匹配', None, **3**)`（★ 位置 3）。
      ⇒ ★ 正解是项目既有的 `create_empty_dispatch_variant()`（事实 12）。
      ★ 所以 `add_fixed_restraint(object(), "ENTS")` **调用方给的是 `None`**，
        而**真正发出去的是 `VARIANT(VT_DISPATCH, None)`**（★ 本测试验这一点）。
      ⚠ 不能只断言"前缀相同" —— ★ 那只验了调用方传了什么，
        **验不到 `_check` 有没有把 `None` 换掉**（★ 那才是修的那一处）。
    """
    import win32com.client as _w

    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or "RESTRAINT"
    m.add_fixed_restraint(object(), "ENTS")
    _assert_call(seen, "AddRestraint", 0, "ENTS", None)
    #: ★ 第 3 参（RefGeom）必须是**换过**的空 Dispatch，而不是裸 None
    ref_geom = seen[0][1][2]
    assert isinstance(ref_geom, _w.VARIANT), \
        "★ RefGeom 必须换成空 Dispatch 参数包（裸 None 在真机上位置 3 报类型不匹配）：%r" % (ref_geom,)
    assert ref_geom.varianttype == (_w.pythoncom.VT_DISPATCH | _w.pythoncom.VT_BYREF), \
        "★ 应是 by-ref 的 VT_DISPATCH：%r" % (ref_geom.varianttype,)


def test_torque_uses_official_force_type_two():
    """★ 力矩走 `AddForce`，第 1 参是官方 `swsForceTypeTorque = 2`。

    ★ 2026-10-01（24h 段 2.1 / Spec Kit `143`）**按真机证据更新期望值**：
      本测试原本把 `ref_geom` 钉成**裸 `None`**，而真机实测（轮 245）那张形态会报
      ``com_error(-2147352571, '类型不匹配', None, 3)`` —— ★ **位置 3 就是 `RefGeom`**。
      ⇒ 现在的契约是：**`RefGeom` 不许是裸 `None`**；当空 Dispatch 助手可用时必须传它
      （已知事实 12：``VARIANT(VT_DISPATCH, None)``）；
      ★ 在 stub 环境里助手不可用 ⇒ 保持 `None`（**本模块的"不连 COM 也能 import"约束**）。
    """
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or "FORCE"
    m.add_torque(object(), "ENTS")
    member, args = seen[0]
    assert member == "AddForce"
    assert args[0] == 2, "第 1 参必须是官方 swsForceTypeTorque = 2"
    assert args[1] == "ENTS"
    if getattr(m, "create_empty_dispatch_variant", None) is not None:
        assert args[2] is not None, (
            "ref_geom 是裸 None ⇒ 真机会报 类型不匹配@arg3（轮 245 实测）")
    assert m.SWS_FORCE_TYPES["torque"] == 2


def test_gravity_takes_single_entity_not_array():
    """官方参数名 DispEntity（单数）—— 不接受数组。"""
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: seen.append((n, a)) or "GRAV"
    m.add_gravity(object(), "ONE_FACE")
    _assert_call(seen, "AddGravity", "ONE_FACE")


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
