"""sw_selection 的官方签名契约测试（不连接 SolidWorks）。

本文件锁两件**本项目特有的事**：
  1. 事实 8（AGENTS.md §六）—— AddSelectionListObject 的 Boolean 返回值不可信，
     `add_to_selection_list` 必须**回读计数**而不是返回那个布尔值。
  2. 事实 4 —— EnableSelection / EnableContourSelection / SelectionColor
     是**属性**，迟到绑定下加括号会 TypeError。

另加「20 个 I 前缀的 COM 内部分发口不得被封装」这一条。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → ISelectionMgr 段

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_selection_contract.py —— 本文件自身
# 定位:   域 1 选中管理的签名契约与两个已知坑的行为锁。
# 被测对象: scripts/sw_selection.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_selection.py"
REFLECTION = Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect_sldworks" / "iface_sldworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   独立抄一遍的调用侧签名。**不含**末位 by-ref 出参。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_ARITY = {
    "GetSelectedObjectCount": 0,
    "GetSelectedObjectCount2": 1,
    "GetSelectedObject": 1,
    "GetSelectedObject6": 2,
    "GetSelectedObjectType2": 1,
    "GetSelectedObjectsFace": 2,
    "GetSelectedObjectsComponent3": 2,
    "GetSelectedObjectsDrawingView2": 2,
    "GetSelectionPoint2": 2,
    "GetSelectionPointInSketchSpace2": 2,
    "SetSelectionPoint": 4,
    "DeSelect2": 2,
    "AddSelectionListObject": 2,
    "SuspendSelectionList": 0,
    "ResumeSelectionList": 0,
    "ResumeSelectionList2": 1,
    "GetSelectedObjectMark": 1,
    "SetSelectedObjectMark": 3,
    "IsCoordSysElementSelected": 2,
    "IsInEditTarget2": 2,
}

#: 官方 ISelectionMgr 段里的 I 前缀成员 —— COM 内部分发口，不该给调用方
INTERNAL_DISPATCH = (
    "IDeSelect", "IDeSelect2",
    "IGetSelectedObject", "IGetSelectedObject2", "IGetSelectedObject3",
    "IGetSelectedObject4",
    "IGetSelectedObjectsComponent", "IGetSelectedObjectsComponent2",
    "IGetSelectionPoint", "IGetSelectionPoint2",
    "IGetSelectionPointInSketchSpace", "IGetSelectionPointInSketchSpace2",
)


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


def _faithful_write(obj, name, value, *args, **kwargs):
    """★ 写属性的"忠实替身"：**就是 `setattr`** —— 与 `sw_connect.set_com_member` 同一实现。

    ★★ 2026-10-03（轮 470）新增。为什么要它：本仓把 98 处「写 COM 属性」从
    `get_com_member(obj, 名, 值)` 改成了 `set_com_member(obj, 名, 值)`
    ⇒ ★ 本文件的契约测试（"is property not method"）要能**记录到那次写**
      ⇒ 故假模块上也得有 `set_com_member` 这个名字 ✓
    """
    setattr(obj, name, value)
    return value


def _load():
    connect = types.ModuleType("sw_connect")
    #: ★★★ 2026-10-03（轮 470）：**假模块的其余名字一律转发给真模块**。
    #:   原先这里**只手装了一两个名字**（`get_com_member`），而 `sw_selection.py`
    #:   顶层还 import 了别的（如 `call_com_member`）⇒ ★ 假模块上没有 ⇒ 报
    #:   `cannot import name 'call_com_member' from 'sw_connect' (**unknown location**)`
    #:   —— ★ 而"unknown location"正是因为假模块**没有 `__file__`**，**错误信息指不到真因**。
    #:   ★ 故加 PEP 562 的模块级 `__getattr__` 兜底 ⇒ 以后无论被测模块还 import 什么，
    #:     都能从**真** `sw_connect` 拿到 ⇒ 这份契约装置**不必随实现改名继续手维护** ✓
    import sw_connect as _real_connect

    def _connect_attr(name):                                   # noqa: ANN001
        return getattr(_real_connect, name)

    connect.__getattr__ = _connect_attr
    connect.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）：**契约测试要跟着实现形态一起改**。
    #:   本仓 2026-10-03 把 98 处「写 COM 属性」从 `get_com_member(obj, 名, 值)`
    #:   改成了 `set_com_member(obj, 名, 值)`（★ 前者有实参就**调用**属性 ⇒
    #:   `TypeError: 'bool' object is not callable` ⇒ 而外面 `return True` ⇒ 失败报成成功）。
    #:   ⇒ ★★ 而本文件原先把**假模块的 `get_com_member`** 当成"写"的记录点 ⇒
    #:      改完之后**猴补丁补不到** ⇒ 断言 `seen` 为空而失败。
    #:   ★ 故这里把**两个名字都**装上（★ 读走 get、写走 set），
    #:     这样测试无论走哪条路都记录得到 ✓
    connect.set_com_member = _faithful_write
    sys.modules["sw_connect"] = connect            # ★ 不用 setdefault：要的是"确定装上"
    spec = importlib.util.spec_from_file_location("sw_selection", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_selection"] = module
    spec.loader.exec_module(module)
    module.get_com_member = _faithful
    module.set_com_member = _faithful_write
    return module


def _record(m, sink, result="OBJ"):
    #: ★★ 同 `_load` 的说明：**两个名字都补** —— 实现改为 `set_com_member` 之后，
    #:   只补 `get_com_member` 就记不到任何东西（★ 那正是本文件曾失败的根因）。
    m.get_com_member = lambda o, n, *a, **k: sink.append((n, a)) or result
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result


# ── 签名对账 ─────────────────────────────────────────────────────────

def test_arity_table_matches_reflection_expectation():
    m = _load()
    for member, count in REFLECTED_ARITY.items():
        got = m.SELECTION_ARITY.get(member)
        assert got == count, f"{member} 期望 {count}，登记表是 {got}"


def test_registry_has_no_internal_dispatch_members():
    """``I*`` 前缀的成员是 COM 内部分发口，**不得**登记为可调用 API。"""
    m = _load()
    for member in INTERNAL_DISPATCH:
        assert member not in m.SELECTION_ARITY, (
            f"{member} 是 COM 内部分发口，不该登记")
        assert member not in m.__all__


def test_wrapped_members_exist_in_reflection():
    if not REFLECTION.is_file():
        print("  (跳过：sldworks 反射清单不在本机)")
        return
    text = REFLECTION.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"(?ms)^## ISelectionMgr\s*\r?\n(.*?)(?=\r?\n## |\Z)", text)
    assert block, "反射清单里取不到 ISelectionMgr 段"
    m = _load()
    for member in m.SELECTION_ARITY:
        assert re.search(rf"\b{re.escape(member)}\s*\(", block.group(1)), (
            f"{member} 不在反射清单里 —— 可能编造")


# ── 事实 8：AddSelectionListObject 的返回值不可信 ──────────────────────

def test_add_to_selection_list_returns_count_not_boolean():
    """必须回读计数。返回布尔值就等于把已知的坑再踩一遍。"""
    m = _load()
    seen = []

    def _record_smart(obj, name, *args, **kwargs):
        seen.append((name, args))
        if name == "AddSelectionListObject":
            return False          # ← 官方不可信的返回值：永远 False
        if name == "GetSelectedObjectCount2":
            return 12             # ← 真实计数是 12
        return None

    m.get_com_member = _record_smart
    result = m.add_to_selection_list(object(), "ITEM", "SELDATA")
    assert result == 12, f"必须回读计数（12），实际返回 {result!r}"
    assert result is not False
    assert [n for n, _ in seen] == ["AddSelectionListObject",
                                   "GetSelectedObjectCount2"]


def test_add_to_selection_list_uses_all_kinds_sentinel():
    """回读必须用 -1（所有类型），否则只数到某一类。"""
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or
                                              (False if n == "AddSelectionListObject" else 12))
    m.add_to_selection_list(object(), "I", "D")
    assert seen[-1] == ("GetSelectedObjectCount2", (m.SELECTION_ALL_KINDS,))
    assert m.SELECTION_ALL_KINDS == -1


# ── 事实 4：三个成员是属性不是方法 ─────────────────────────────────────

def test_enable_selection_is_property_not_method():
    m = _load()
    seen = []
    _record(m, seen)
    m.set_enable_selection(object(), True)
    assert seen == [("EnableSelection", (True,))]


def test_enable_contour_selection_is_property_not_method():
    m = _load()
    seen = []
    _record(m, seen)
    m.set_enable_contour_selection(object(), False)
    assert seen == [("EnableContourSelection", (False,))]


def test_selection_color_is_property_not_method():
    m = _load()
    seen = []
    _record(m, seen)
    m.set_selection_color(object(), 3)
    assert seen == [("SelectionColor", (3,))]


# ── 零参与定长参数 ───────────────────────────────────────────────────

def test_zero_arg_members_pass_no_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.suspend_selection_list(object())
    assert seen == [("SuspendSelectionList", ())]
    seen2 = []
    _record(m, seen2)
    m.resume_selection_list(object())
    assert seen2 == [("ResumeSelectionList", ())]


def test_set_selection_point_passes_four_arguments():
    m = _load()
    seen = []
    _record(m, seen, result=True)
    m.set_selection_point(object(), 0, 1.0, 2.0, 3.0)
    assert seen == [("SetSelectionPoint", (0, 1.0, 2.0, 3.0))]


def test_selected_object_uses_v6_with_two_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    m.get_selected_object(object(), 3)
    assert seen == [("GetSelectedObject6", (3, 0))]


def test_evidence_reads_types_for_every_selection():
    m = _load()
    m.get_com_member = lambda o, n, *a, **k: (
        2 if n == "GetSelectedObjectCount2"
        else (7 if n == "GetSelectedObjectType2" else True))
    evidence = m.collect_selection_evidence(object())
    assert evidence["count"] == 2
    assert evidence["types"] == [7, 7]
    assert evidence["type_histogram"] == {"7": 2}


# ── 护栏 ─────────────────────────────────────────────────────────────

def test_guard_rejects_wrong_arity_and_none():
    m = _load()
    try:
        m._checked(object(), "SetSelectionPoint", 1, 2)
    except ValueError as exc:
        assert "SetSelectionPoint" in str(exc)
    else:
        raise AssertionError("错 arity 未被拦")
    try:
        m._checked(None, "SuspendSelectionList")
    except ValueError as exc:
        assert "None" in str(exc)
        return
    raise AssertionError("None 目标未被拦")


def test_public_entries_reject_none():
    m = _load()
    for func, args in (
        (m.get_selection_count, ()),
        (m.get_selected_object, (0,)),
        (m.get_selected_face, (0,)),
        (m.get_selection_point, (0,)),
        (m.set_selection_point, (0, 0.0, 0.0, 0.0)),
        (m.deselect, ("X",)),
        (m.add_to_selection_list, ("X", "D")),
        (m.suspend_selection_list, ()),
        (m.set_selection_color, (1,)),
        (m.set_enable_selection, (True,)),
        (m.is_coord_sys_element_selected, (1, 0)),
        (m.is_in_edit_target, (0,)),
        (m.collect_selection_evidence, ()),
        (m.get_selection_manager, ()),
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
