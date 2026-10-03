"""sw_pattern 的官方签名契约测试（不连接 SolidWorks）。

本文件锁三件事：
  1. **选区事务** —— AccessSelections(2 参) 必须包住全部属性设置，
     且异常路径也要 ReleaseSelectionAccess()（零参）。
  2. **两族形状不同、不许合并** —— 线性阵列有「总数 / 端条件 / 种子参考」，
     沿曲线阵列没有，取而代之的是「等间距 IsEqualSpaced」。
  3. **I* 内部分发口不得被封装**。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_pattern_contract.py —— 本文件自身
# 定位:   域 3 阵列 FeatureData 的签名契约与三条纪律锁。
# 被测对象: scripts/sw_pattern.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_pattern.py"
REFLECTION = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   两族共有的方法型成员签名（属性型成员不进表）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_ARITY = {
    "AccessSelections": 2,
    "ReleaseSelectionAccess": 0,
    "GetD1AxisType": 0,
    "GetD2AxisType": 0,
    "GetTransform": 1,
    "GetPatternBodyCount": 0,
    "GetPatternFaceCount": 0,
    "GetPatternFeatureCount": 0,
    "GetSkippedItemCount": 0,
    "SetFeatureScope": 3,
    "SetInstanceToVaryOptions": 1,
    "GetInstanceToVaryOptions": 0,
    "IsDirection2Specified": 0,
}

#: ILinearPatternFeatureData **没有**、而 ICurveDrivenPatternFeatureData 有的
CURVE_ONLY = ("D1IsEqualSpaced", "D2IsEqualSpaced", "D1Direction",
              "D1FaceNormal", "Dir2Specified")
#: ICurveDrivenPatternFeatureData **没有**、而线性阵列有的
LINEAR_ONLY = ("D1TotalInstances", "D1EndCondition", "D1EndUseSpacing",
               "D1EndSeedReference", "D1EndRefOffset", "StructureSystemToPatternArray")




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
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    connect.set_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_pattern", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_pattern"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink, result=None):
    m.get_com_member = lambda o, n, *a, **k: (sink.append((n, a)) or result)
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.call_com_member = lambda o, n, *a, **k: (sink.append((n, a)) or result)


# ── 签名对账 ─────────────────────────────────────────────────────────

def test_arity_table_matches_reflection():
    m = _load()
    assert m.PATTERN_MEMBER_ARITY == REFLECTED_ARITY, (
        f"签名表与反射不符:\n  模块 {m.PATTERN_MEMBER_ARITY}\n  反射 {REFLECTED_ARITY}")


def test_no_internal_dispatch_members_registered():
    """``I*`` 前缀的成员是 COM 内部分发口，不该登记。"""
    m = _load()
    for member in m.PATTERN_MEMBER_ARITY:
        assert not member.startswith("I") or member in (
            "IsDirection2Specified",), f"{member} 是内部分发口"
    assert "IAccessSelections" not in m.PATTERN_MEMBER_ARITY
    assert "ISetPatternFaceArray" not in m.PATTERN_MEMBER_ARITY


def test_end_condition_enum_is_exhaustive_and_correct():
    """官方 swPatternEndCondition_e **只有 2 项**。"""
    m = _load()
    assert m.SWS_PATTERN_END_CONDITIONS == {
        "spacing_and_instances": 0, "up_to_reference": 1}


# ── 选区事务 ─────────────────────────────────────────────────────────

def test_linear_pattern_wraps_everything_in_selection_transaction():
    m = _load()
    seen = []
    _record(m, seen)
    m.configure_linear_pattern(object(), object(), d1_spacing=5.0,
                               d1_total_instances=4)
    names = [n for n, _ in seen]
    assert names[0] == "AccessSelections", "属性设置前必须先接管选区"
    assert names[-1] == "ReleaseSelectionAccess", "结束后必须释放"
    # 事务成员本身是零参
    assert seen[0][1][1] is None, "AccessSelections 第 2 参按官方语义未知，传 None"
    assert seen[-1] == ("ReleaseSelectionAccess", ())


def test_selection_is_released_even_when_a_setter_raises():
    m = _load()
    seen = []

    def _boom(obj, name, *args, **kwargs):
        seen.append((name, args))
        if name == "D1Spacing":
            raise RuntimeError("设值失败")
        return None

    m.get_com_member = _boom
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = _boom
    m.call_com_member = _boom
    try:
        m.configure_linear_pattern(object(), object(), d1_spacing=1.0)
    except RuntimeError:
        pass
    else:
        raise AssertionError("异常没有向上传播")
    assert [n for n, _ in seen][-1] == "ReleaseSelectionAccess", "异常时也要释放"


def test_context_manager_rejects_none_data_or_model():
    m = _load()
    for data, model in ((None, object()), (object(), None)):
        try:
            with m.edit_selection(data, model):
                pass
        except ValueError as exc:
            assert "None" in str(exc)
            continue
        raise AssertionError(f"({data is None}, {model is None}) 未被拦下")


# ── 两族形状不同，不许合并 ───────────────────────────────────────────

def test_linear_pattern_has_no_equal_spaced_properties():
    """沿曲线阵列的 IsEqualSpaced 不属于线性阵列。"""
    source = MODULE_PATH.read_text(encoding="utf-8")
    linear_block = source[source.index("def configure_linear_pattern("):
                          source.index("def configure_curve_driven_pattern(")]
    for member in CURVE_ONLY:
        assert f'"{member}"' not in linear_block, (
            f"{member} 只属于沿曲线阵列，不该出现在线性阵列的封装里")


def test_curve_driven_pattern_has_no_total_instances_or_end_condition():
    """沿曲线阵列没有「总数 / 端条件」概念。"""
    source = MODULE_PATH.read_text(encoding="utf-8")
    curve_block = source[source.index("def configure_curve_driven_pattern("):
                         source.index("def read_pattern_element(")]
    for member in LINEAR_ONLY:
        assert f'"{member}"' not in curve_block, (
            f"{member} 只属于线性阵列，不该出现在沿曲线阵列的封装里")


def test_both_configurers_set_only_what_was_passed():
    m = _load()
    seen = []
    _record(m, seen)
    m.configure_curve_driven_pattern(object(), object(), d1_spacing=2.0)
    props = [n for n, _ in seen if n not in
             ("AccessSelections", "ReleaseSelectionAccess")]
    assert props == ["D1Spacing"]


# ── 护栏 ─────────────────────────────────────────────────────────────

def test_guard_rejects_wrong_arity():
    m = _load()
    try:
        m._checked(object(), "AccessSelections", "only-one-arg")
    except ValueError as exc:
        assert "AccessSelections" in str(exc)
        return
    raise AssertionError("错 arity 未被拦")


def test_public_entries_reject_none():
    m = _load()
    for func, args in (
        (m.configure_linear_pattern, (object(),)),
        (m.configure_curve_driven_pattern, (object(),)),
        (m.read_pattern_element, ()),
        (m.collect_pattern_evidence, ()),
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
