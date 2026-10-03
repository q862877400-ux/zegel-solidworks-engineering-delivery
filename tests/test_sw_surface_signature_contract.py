r"""原生曲面接口的**签名契约**测试（不连接 SolidWorks）。

不验证任何运行结果，只验证**调用形态**：参数个数与类型顺序是否与官方签名一致，
以及本域刻意不做的事（指针版本不收录、FeatureData 不封装）是否真的没混进来。

官方签名依据（纯元数据反射，未实例化任何 COM 对象）：
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IModeler / ISldWorks 段

与本仓库既有测试一致：**不依赖 pytest**，纯 assert。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   下方「官方签名表」逐条照抄 IModeler 段中以 Create 开头、非 I 前缀、
#         以 Surface 结尾的 19 个成员的 Signature 行，一个参数都不多不少。
#         测试用它们做长度与位置断言，故错一个名字都跑不过。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import io
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_surface.py"

#: IModeler 上全部非指针 Create*Surface 的官方参数类型序列（照抄反射清单）
OFFICIAL_SIGNATURES = {
    "CreatePlanarSurface": ("Object", "Object"),
    "CreatePlanarSurface2": ("Object", "Object", "Object"),
    "CreateCylindricalSurface": ("Object", "Object", "Double"),
    "CreateCylindricalSurface2": ("Object", "Object", "Object", "Double"),
    "CreateSphericalSurface": ("Object", "Double"),
    "CreateSphericalSurface2": ("Object", "Object", "Object", "Double"),
    "CreateConicalSurface": ("Object", "Object", "Double", "Double"),
    "CreateConicalSurface2": ("Object", "Object", "Object", "Double", "Double"),
    "CreateToroidalSurface": ("Object", "Object", "Object", "Double", "Double"),
    "CreateOffsetSurface": ("Object", "Double"),
    "CreateExtrusionSurface": ("Object", "Object"),
    "CreateRevolutionSurface": ("Object", "Object", "Object", "Object"),
    "CreateRuledSurface": ("Object", "Object", "Object"),
    "CreateSweptSurface": ("Object", "Object"),
    "CreateBsplineSurface": ("Object", "Object", "Object", "Object"),
    "CreateCoonsBSurface": ("Curve", "Curve", "Curve", "Curve", "Boolean"),
    "CreateSheetFromSurface": ("Object", "Object"),
    "CreateLoftSurface": (
        "Object", "Boolean", "Boolean", "Object", "Int32", "Int32", "Object",
        "Object", "Object", "Object", "Boolean", "Boolean", "Object",
        "Object", "Int32", "Int32", "Int32", "Int32",
    ),
    "CreateRuledSurfaceFromEdge": (
        # ⚠ 反射行原文是 `Int32 CreateRuledSurfaceFromEdge(...)`，开头的 Int32
        #   是**返回类型**不是参数。初稿把它也抄进参数表，导致 15 vs 14 被测出来。
        "ModelDoc2", "Object", "Int32", "Double", "Boolean", "Boolean",
        "Boolean", "Double", "Boolean", "Double", "Double", "Double",
        "Boolean", "Object&",
    ),
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

def _faithful_get_com_member(obj, name, *args, **kwargs):
    """复刻 scripts/sw_connect.py::get_com_member：可调用则调用，属性则取值。"""
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


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
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
    connect.get_com_member = _faithful_get_com_member
    connect.call_com_member = _faithful_get_com_member
    sys.modules.setdefault("sw_connect", connect)

    spec = importlib.util.spec_from_file_location("sw_surface_contract", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_surface_contract"] = module
    spec.loader.exec_module(module)
    return module


class _Modeler:
    """记录 Create*Surface 调用的假 IModeler。"""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return f"<{name}>"
        return _call


def _app_with_modeler():
    modeler = _Modeler()
    app = types.SimpleNamespace(GetModeler=lambda: modeler)
    return app, modeler


# ── 签名表完整性 ─────────────────────────────────────────────────────

def test_registered_methods_match_official_arity_exactly():
    """本模块的签名表必须与官方反射清单**逐条等长**，不多不少不少。"""
    sim = _load_module()
    registered = sim.SURFACE_CREATION_METHODS
    assert set(registered) == set(OFFICIAL_SIGNATURES)
    for name, params in OFFICIAL_SIGNATURES.items():
        assert len(registered[name][1]) == len(params), f"{name} 参数个数不符"


def test_no_pointer_variants_are_registered():
    """ICreate*Surface 是进程内非托管 C++ 指针接口，pywin32 不可用，不得收录。"""
    sim = _load_module()
    offenders = [n for n in sim.SURFACE_CREATION_METHODS if n.startswith("ICreate")]
    assert offenders == [], f"指针版本不应被收录: {offenders}"


def test_surface_featuredata_interfaces_are_not_wrapped():
    """本域的 13 个 *FeatureData 是「编辑既有特征」用，不是创建入口。

    模块 docstring 明确说明这一误判已纠正，故这里断言它们**没有**被封装。
    """
    sim = _load_module()
    exported = " ".join(sim.__all__)
    for token in ("FeatureData", "Trim", "Knit", "FillSurface", "OffsetFeature"):
        assert token not in exported, f"不应导出 {token} 相关入口"


# ── 调用形态 ─────────────────────────────────────────────────────────

def test_get_modeler_uses_automation_friendly_entry():
    """用 GetModeler()，不是指针版 IGetModeler()。"""
    sim = _load_module()
    app, modeler = _app_with_modeler()
    assert sim.get_modeler(app) is modeler
    assert not hasattr(app, "IGetModeler")


def test_create_planar_surface_passes_two_arguments():
    """形状层：`_invoke` 把 2 个参数按签名转给 `CreatePlanarSurface`。

    ⚠ 2026-10-01 改：**改调私有的 `_invoke`**（形状层），而不是公开包装器。
    原因：公开包装器现在**先过运行期守卫**，而 `CreatePlanarSurface` **本机实测取不到**
    ⇒ 经公开包装器验不了形状。**⇒ 职责分离：形状归 `_invoke`，守卫归公开包装器**
    （见 `test_unavailable_method_raises_a_reasoned_error`）。
    """
    sim = _load_module()
    _app, modeler = _app_with_modeler()
    sim._invoke(modeler, "CreatePlanarSurface", "point", "normal")
    assert modeler.calls == [("CreatePlanarSurface", ("point", "normal"))]


def test_create_cylindrical_surface_converts_radius_to_float():
    sim = _load_module()
    app, modeler = _app_with_modeler()
    sim.create_cylindrical_surface(app, "origin", "axis", 5)
    name, args = modeler.calls[0]
    assert name == "CreateCylindricalSurface"
    assert args == ("origin", "axis", 5.0) and isinstance(args[2], float)


def test_create_spherical_surface_takes_two_arguments():
    """官方是 (Object, Double)，不是 (Object, Object, Double)。"""
    sim = _load_module()
    app, modeler = _app_with_modeler()
    sim.create_spherical_surface(app, "center", 3)
    name, args = modeler.calls[0]
    assert name == "CreateSphericalSurface"
    assert len(args) == 2 and isinstance(args[1], float)


def test_create_toroidal_surface_takes_five_arguments():
    sim = _load_module()
    app, modeler = _app_with_modeler()
    sim.create_toroidal_surface(app, "o", "ax", "c", 10, 1)
    name, args = modeler.calls[0]
    assert name == "CreateToroidalSurface"
    assert len(args) == 5 and all(isinstance(a, float) for a in args[3:])


def test_create_coons_b_surface_coerces_boolean():
    """形状层：布尔参数被强制成 `True`（同 :func:`test_create_planar_surface_passes_two_arguments`）。

    ⚠ 这里验的是**包装器的参数强制转换**，而 `CreateCoonsBSurface` 也在「本机实测取不到」
    名单里 ⇒ 为了不被守卫挡住，**先临时把它移出不可达名单**（用完恢复），
    这样验的仍是**包装器本体**（而不是绕过它）。
    """
    sim = _load_module()
    app, modeler = _app_with_modeler()
    removed = sim.IMODELER_RUNTIME_UNAVAILABLE
    # frozenset ⇒ 换成去掉该项的临时集合（**只在本测试内生效**）
    sim.IMODELER_RUNTIME_UNAVAILABLE = frozenset(
        m for m in removed if m != "CreateCoonsBSurface"
    )
    sim.IMODELER_RUNTIME_AVAILABLE = sim.IMODELER_RUNTIME_AVAILABLE | {"CreateCoonsBSurface"}
    try:
        sim.create_coons_b_surface(app, "v", "u", "v2", "u2", 1)
    finally:
        sim.IMODELER_RUNTIME_UNAVAILABLE = removed
        sim.IMODELER_RUNTIME_AVAILABLE = frozenset(
            m for m in sim.IMODELER_RUNTIME_AVAILABLE if m != "CreateCoonsBSurface"
        )
    name, args = modeler.calls[0]
    assert name == "CreateCoonsBSurface"
    assert len(args) == 5 and args[4] is True


def test_unavailable_method_raises_a_reasoned_error():
    """**公开包装器对「本机实测取不到」的方法，必须报带原因的错误。**

    ⚠ 这条是本轮修的那个**真 bug** 的守卫：守卫 `require_runtime_available` 早就写了，
    但**没人调它** ⇒ 真机调 `create_planar_surface` 拿到的是
    `TypeError: 'NoneType' object is not callable`（**指向不了真因**）。
    ⇒ 现在公开包装器**先调守卫**，这条断言把那个行为钉住。
    """
    sim = _load_module()
    app, _modeler = _app_with_modeler()
    try:
        sim.create_planar_surface(app, "point", "normal")
    except RuntimeError as exc:
        text = str(exc)
        assert "运行期取不到" in text, "报的是 RuntimeError，但**没带原因**：%s" % text[:80]
        assert "CreatePlanarSurface" in text, "错误信息里没点名该方法"
        return
    raise AssertionError("**公开包装器没有对不可达方法报错** ⇒ 守卫没接上")


def test_create_loft_surface_is_registered_but_not_wrapped():
    """18 参的 Loft 本轮只登记不包装 —— 避免半成品。"""
    sim = _load_module()
    assert len(sim.SURFACE_CREATION_METHODS["CreateLoftSurface"][1]) == 18
    assert not any(name.startswith("create_loft") for name in sim.__all__)


# ── 参数自检 ─────────────────────────────────────────────────────────

def test_invoke_rejects_wrong_argument_count_with_method_name():
    """参数个数错时立刻抛带方法名的错误，而不是让 COM 报语焉不详的异常。"""
    sim = _load_module()
    _, modeler = _app_with_modeler()
    try:
        sim._invoke(modeler, "CreatePlanarSurface", "only-one")
    except TypeError as exc:
        assert "CreatePlanarSurface" in str(exc)
        assert "2" in str(exc)
        return
    raise AssertionError("参数个数不符时应当抛 TypeError")


def test_invoke_rejects_unregistered_method():
    sim = _load_module()
    _, modeler = _app_with_modeler()
    try:
        sim._invoke(modeler, "CreateSomethingElse", 1, 2)
    except KeyError as exc:
        assert "CreateSomethingElse" in str(exc)
        return
    raise AssertionError("未登记的方法应当抛 KeyError")


def test_get_modeler_raises_when_none():
    sim = _load_module()
    try:
        sim.get_modeler(types.SimpleNamespace(GetModeler=lambda: None))
    except RuntimeError as exc:
        assert "GetModeler" in str(exc)
        return
    raise AssertionError("取不到 Modeler 时应当抛 RuntimeError")


# ── 证据回读 ─────────────────────────────────────────────────────────

def test_evidence_reports_no_pointer_variants():
    sim = _load_module()
    app, _ = _app_with_modeler()
    evidence = sim.collect_surface_evidence(app)
    assert evidence["has_modeler"] is True
    assert evidence["registered_count"] == len(OFFICIAL_SIGNATURES)
    assert evidence["pointer_variants_available"] is False


# ── 直接运行 ─────────────────────────────────────────────────────────

def _enable_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


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
    _enable_utf8_stdout()
    raise SystemExit(_main())
