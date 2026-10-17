"""sw_featureworks 的官方签名契约测试（不连接 SolidWorks）。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect\\iface_fworks.txt   （版本 34.4.1.1011）

本模块的全部调用都走 `_checked(target, "成员", *args)` 护栏，
成员名是变量 ⇒ ``audit_call_arity.py`` 的静态正则看到 **0 个调用点**。
所以签名对账只能靠本文件（与 sw_simulation_loads / study / results 同一套路）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_featureworks_contract.py —— 本文件自身
# 定位:   域 14 FeatureWorks 的签名契约与两条纪律锁：
#         ① 回调成员不得被封装；② 没有可读属性就不编「状态回读」。
# 被测对象: scripts/sw_featureworks.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_featureworks.py"
REFLECTION = Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect" / "iface_fworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（fworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_fworks.txt 的 IFeatureWorksApp 段
# 定位:   独立抄一遍的反射签名（7 个成员全录），作为对账基准。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_ARITY = {
    "CreateFeatures": 1,
    "RecognizeFeatureAutomatic": 1,
    "RecognizeFeatureInteractive": 2,
    "SetAdvancedOptions": 1,
    "SetPerformanceOptions": 1,
}
REFLECTED_CALLBACKS = ("BubbleTipCallback", "HelpErrCallback")




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
    spec = importlib.util.spec_from_file_location("sw_featureworks", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_featureworks"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink, result="OBJ"):
    m.get_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.call_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result


# ── 签名对账 ─────────────────────────────────────────────────────────

def test_arity_table_matches_reflection():
    m = _load()
    assert m.FEATUREWORKS_ARITY == REFLECTED_ARITY, (
        f"签名表与反射不符: {m.FEATUREWORKS_ARITY} vs {REFLECTED_ARITY}")


def test_every_wrapper_uses_a_reflected_member():
    m = _load()
    source = MODULE_PATH.read_text(encoding="utf-8")
    found = re.findall(r'_checked\(\s*featureworks,\s*"(\w+)"', source)
    assert found, "没找到任何 _checked 调用点"
    for member in found:
        assert member in REFLECTED_ARITY, f"{member} 不在反射签名里 —— 可能编造"
    assert len(set(found)) >= 4, f"只对账到 {len(set(found))} 个封装，预期 ≥4"


def test_registry_has_no_invented_members():
    if not REFLECTION.is_file():
        print("  (跳过：fworks 反射清单不在本机)")
        return
    text = REFLECTION.read_text(encoding="utf-8", errors="replace")
    m = _load()
    for member in list(m.FEATUREWORKS_ARITY) + list(m.CALLBACK_MEMBERS):
        assert re.search(rf"\b{re.escape(member)}\s*\(", text), (
            f"{member} 不在反射清单里")


# ── 回调成员不得被封装 ───────────────────────────────────────────────

def test_callbacks_are_listed_not_wrapped():
    """``BubbleTipCallback`` / ``HelpErrCallback`` 是宿主回调点，不是脚本 API。"""
    m = _load()
    assert tuple(m.CALLBACK_MEMBERS) == REFLECTED_CALLBACKS
    exported = set(m.__all__)
    for member in REFLECTED_CALLBACKS:
        assert member not in exported
        assert member not in m.FEATUREWORKS_ARITY, (
            f"{member} 是回调，不该登记成可调用 API")


# ── 没有可读属性就不编「状态回读」────────────────────────────────────

def test_state_reader_does_not_invent_object_fields():
    """IFeatureWorksApp 7 个成员**全是方法**、零个可读属性 ⇒ 状态只能从调用侧拿。"""
    m = _load()
    state = m.read_featureworks_state(
        [("CreateFeatures", (1,)), ("SetAdvancedOptions", (0,))])
    assert state["call_count"] == 2
    assert state["has_recognize"] is True
    # 不得凭空出现来自 FeatureWorks 对象的字段
    for fabricated in ("entity_count", "recognized_count", "version",
                       "is_busy", "last_result"):
        assert fabricated not in state, f"{fabricated} 是编造的字段"


def test_state_reader_accepts_none_and_returns_empty():
    m = _load()
    state = m.read_featureworks_state()
    assert state["call_count"] == 0 and state["members"] == []


# ── 调用形态 ─────────────────────────────────────────────────────────

def test_recognize_and_create_passes_one_argument():
    m = _load()
    seen = []
    _record(m, seen)
    m.recognize_and_create(object(), 3)
    assert seen == [("CreateFeatures", (3,))]


def test_interactive_recognize_passes_two_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.recognize_interactive(object(), "model.sldprt", 0)
    assert seen == [("RecognizeFeatureInteractive", ("model.sldprt", 0))]


def test_options_setters_pass_one_argument_each():
    m = _load()
    for func, member in ((m.set_advanced_options, "SetAdvancedOptions"),
                         (m.set_performance_options, "SetPerformanceOptions")):
        seen = []
        _record(m, seen)
        func(object(), 7)
        assert seen == [(member, (7,))]


def test_guard_rejects_wrong_arity():
    m = _load()
    try:
        m._checked(object(), "CreateFeatures", 1, 2)
    except ValueError as exc:
        assert "CreateFeatures" in str(exc)
    else:
        raise AssertionError("错 arity 未被拦")


def test_guard_rejects_none_with_actionable_message():
    m = _load()
    try:
        m._checked(None, "CreateFeatures", 1)
    except ValueError as exc:
        assert "调用方" in str(exc), "错误信息应告诉调用方该做什么"
        return
    raise AssertionError("None 目标未被拒")


# ── 「ProgID 查不到」纪律 ────────────────────────────────────────────

def test_source_refuses_to_hardcode_progid():
    """本机未注册 FeatureWorks 加载项 ⇒ 不硬编 ProgID（连「待确认」都不给）。

    ⚑ 只查「**调用**」不查「提及」：模块 docstring 里要解释「为什么不用
       GetAddInObject 取」，那处提及是必需的。
       ⚑ 本测试初版断言「源码不含 GetAddInObject」——把自己需要的说明
          也判成了违规。**同一个错在 test_sw_routing_contract.py 上犯过一次**，
          这次没把教训带过来。
    """
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "get_com_member(.*GetAddInObject" not in source
    for token in ("FeatureWorks.FeatureWorksApp", "SldWorks.FeatureWorks"):
        assert token not in source, f"不得硬编 ProgID: {token}"


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
