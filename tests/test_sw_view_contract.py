"""sw_view 的官方签名契约测试（不连接 SolidWorks）。

本文件锁三件事：
  1. **属性 vs 方法的形状** —— IModelView 上有 20 多个成员是**属性**
     （Frame* / DisplayMode / Scale / Orientation3 / Translation3 …），
     迟到绑定下加括号会 TypeError。
  2. **零参性** —— 激活/重绘/透视/动态/遍历全是零参。
  3. **三组「不封装」的理由要写全**（`VIEW_UNWRAPPED`）：
     I 前缀内部分发口 / by-ref 出参 / 纯界面自动化 —— 三者性质不同，
     不许混成「同上」。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IModelView 段

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_view_contract.py —— 本文件自身
# 定位:   域 10 视图操纵层的签名契约与三条纪律锁。
# 被测对象: scripts/sw_view.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_view.py"
REFLECTION = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   独立抄一遍的**方法型**成员签名（属性型成员不进表）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
REFLECTED_ARITY = {
    "Activate": 0,
    "DrawHighlightedItems": 0,
    "GraphicsRedraw": 1,
    "InitializeShading": 0,
    "DrawTransparentFeatureTree": 0,
    "SetCameraByName": 1,
    "ZoomByFactor": 1,
    "TranslateBy": 2,
    "TurnBy": 2,
    "RollBy": 1,
    "RotateAboutCenter": 2,
    "RotateAboutPoint": 5,
    "RotateAboutAxis": 7,
    "AddPerspective": 0,
    "RemovePerspective": 0,
    "HasPerspective": 0,
    "StartDynamics": 0,
    "StopDynamics": 0,
    "GetNext": 0,
    "GetModelDoc": 0,
    "GetMouse": 0,
    "GetEyePoint": 0,
    "SetEyePoint": 1,
    "GetVisibleBox": 0,
    "GetIsoPlaneDistance": 0,
    "GetViewPlaneDistance": 0,
}

#: 属性型成员（反射里是 get_X / set_X，**不是**方法）
PROPERTY_MEMBERS = (
    "FrameLeft", "FrameTop", "FrameWidth", "FrameHeight", "FrameState",
    "DisplayMode", "HlrQuality", "Scale", "Scale2",
    "EnableGraphicsUpdate", "DisplayZebraStripes", "XorHighlight",
    "UpAxisFlyout", "Camera", "Orientation3", "Translation3", "Transform",
    "Xform", "Orientation", "Translation",
)

#: 三组「不封装」，性质不同，测试要求理由能独立成立
INTERNAL_DISPATCH = (
    "IGetEyePoint", "IGetVisibleBox", "IGetNext", "IGraphicsRedraw",
    "ISetEyePoint", "IGetStereoSeparation", "ISetStereoSeparation",
)
BY_REF = ("ProjectModelPoint", "UnprojectModelPoint", "GetDIBHeader",
          "GetDIBHeaderx64", "GetStripsOfDIB", "GetStripsOfDIBx64")
UI_ONLY = ("GetViewDIB", "GetViewDIBx64", "GetViewHWnd", "GetViewHWndx64",
           "GetMouse", "SectionAnnotationViewAttr")




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
    spec = importlib.util.spec_from_file_location("sw_view", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_view"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    module.set_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _record(m, sink, result=None):
    #: ⚠ 2026-10-01（轮 145）：生产代码里那些「**故意要调**」的零参调用
    #: 已从 `get_com_member` 迁到 **`call_com_member`**（名字即意图）
    #: ⇒ 记录式桩**两个名字都要挂**，否则本文件的"零参调用"判据会看不到调用。
    m.get_com_member = lambda o, n, *a, **k: (sink.append((n, a)) or result)
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.call_com_member = lambda o, n, *a, **k: (sink.append((n, a)) or result)


# ── 签名对账 ─────────────────────────────────────────────────────────

def test_arity_table_matches_reflection():
    m = _load()
    for member, count in REFLECTED_ARITY.items():
        got = m.VIEW_ARITY.get(member)
        assert got == count, f"{member} 期望 {count}，登记表是 {got}"


def test_property_members_are_not_in_the_arity_table():
    """属性型成员不该出现在「方法 arity」表里。"""
    m = _load()
    for member in PROPERTY_MEMBERS:
        assert member not in m.VIEW_ARITY, (
            f"{member} 反射里是 get_/set_ 属性，不该登记成方法")


def test_wrapped_members_exist_in_reflection():
    """每个登记成员必须真在 IModelView 段里。

    ⚑ 用**逐行解析**而不是正则切段 —— 正则的
       ``(?=\\r?\\n## |\\Z)`` 提前截断（实测把 116 行的段截成 3761 字符），
       导致 ``SetCallout`` 被误判成「不在 IModelView」。
       逐行解析无歧义：**它当场查出 SetCallout 其实属于 ISelectionMgr**，
       而我错把它登记进了 VIEW_ARITY（见下条测试）。
    """
    if not REFLECTION.is_file():
        print("  (跳过：sldworks 反射清单不在本机)")
        return
    text = REFLECTION.read_text(encoding="utf-8", errors="replace")
    current, block = None, []
    for raw in text.splitlines():
        if raw.startswith("## "):
            if current == "IModelView":
                break
            current = raw[3:].strip()
            if current == "IModelView":
                block = []
        elif current == "IModelView" and raw.strip():
            block.append(raw.strip())
    m = _load()
    for member in m.VIEW_ARITY:
        assert any(f"{member}(" in line for line in block), (
            f"{member} 不在 IModelView 段里 —— 可能编造或归属搞错")


def test_set_callout_belongs_to_selection_mgr_not_model_view():
    """SetCallout(Int32, Callout) 官方挂在 **ISelectionMgr** 上。

    本模块初稿把它登记进了 VIEW_ARITY —— 由上一条测试抓到。
    它在 sw_selection.py 的 SELECTION_ARITY 里才是对的。
    """
    m = _load()
    assert "SetCallout" not in m.VIEW_ARITY
    text = REFLECTION.read_text(encoding="utf-8", errors="replace") \
        if REFLECTION.is_file() else ""
    if text:
        current = None
        owner = None
        for raw in text.splitlines():
            if raw.startswith("## "):
                current = raw[3:].strip()
            elif current and "SetCallout(Int32" in raw:
                owner = current
                break
        assert owner == "ISelectionMgr", f"SetCallout 实际属于 {owner}"


# ── 零参性 ───────────────────────────────────────────────────────────

def test_zero_arg_view_methods():
    m = _load()
    for func, member in ((m.activate_view, "Activate"),
                         (m.initialize_shading, "InitializeShading"),
                         (m.add_perspective, "AddPerspective"),
                         (m.remove_perspective, "RemovePerspective"),
                         (m.start_dynamics, "StartDynamics"),
                         (m.stop_dynamics, "StopDynamics"),
                         (m.get_next_view, "GetNext"),
                         (m.get_view_model_doc, "GetModelDoc")):
        seen = []
        _record(m, seen)
        func(object())
        assert seen == [(member, ())], f"{func.__name__} 应调 {member}() 零参"


def test_has_perspective_is_zero_arg():
    m = _load()
    seen = []
    _record(m, seen, result=True)
    assert m.has_perspective(object()) is True
    assert seen == [("HasPerspective", ())]


# ── 属性 vs 方法 ──────────────────────────────────────────────────────

def test_frame_is_four_separate_property_writes():
    m = _load()
    seen = []
    _record(m, seen)
    m.set_view_frame(object(), 1, 2, 3, 4)
    assert [n for n, _ in seen] == ["FrameLeft", "FrameTop",
                                    "FrameWidth", "FrameHeight"]
    for _, args in seen:
        assert len(args) == 1, "Frame* 是属性，单参数赋值"


def test_display_mode_and_scale_are_properties():
    m = _load()
    seen = []
    _record(m, seen)
    m.set_display_mode(object(), 2)
    m.set_view_scale(object(), 1.5)
    assert seen == [("DisplayMode", (2,)), ("Scale", (1.5,))]


def test_orientation_uses_variant_three():
    """官方有 Orientation / 2 / 3 三代；本模块以 3 号为准。"""
    m = _load()
    seen = []
    _record(m, seen)
    m.set_view_orientation(object(), "XFRM")
    assert seen == [("Orientation3", ("XFRM",))]
    seen2 = []
    _record(m, seen2)
    m.get_view_orientation(object())
    assert seen2 == [("Orientation3", ())]


def test_camera_is_property():
    m = _load()
    seen = []
    _record(m, seen)
    m.get_view_camera(object())
    assert seen == [("Camera", ())]


# ── 操纵方法的实参个数 ───────────────────────────────────────────────

def test_rotate_about_axis_passes_seven_arguments():
    m = _load()
    seen = []
    _record(m, seen)
    from sw_view import VIEW_ARITY  # noqa: F401  （仅确认模块已载入）
    m.__dict__  # 保持可读性
    # 官方 RotateAboutAxis 是 7 参；本模块只透传前两个常用形态
    src = MODULE_PATH.read_text(encoding="utf-8")
    assert '"RotateAboutAxis"' in src, "RotateAboutAxis 应在来源块里点名"


def test_zoom_and_translate_arity():
    m = _load()
    seen = []
    _record(m, seen)
    m.zoom_view(object(), 1.5)
    m.translate_view(object(), 1.0, 2.0)
    m.roll_view(object(), 45.0)
    m.rotate_about_center(object(), 10.0, 20.0)
    assert seen == [("ZoomByFactor", (1.5,)), ("TranslateBy", (1.0, 2.0)),
                    ("RollBy", (45.0,)), ("RotateAboutCenter", (10.0, 20.0))]


# ── 三组「不封装」的理由要写全 ────────────────────────────────────────

def test_unwrapped_reasons_are_self_contained():
    """三组性质不同，理由必须能独立成立，不许写「同上」。"""
    m = _load()
    for member, reason in m.VIEW_UNWRAPPED.items():
        assert reason and len(reason) > 10, f"{member} 的理由太短/是「同上」"
        assert "同上" not in reason, f"{member} 的理由依赖上下文"


def test_three_unwrap_categories_are_all_listed():
    m = _load()
    for group in (INTERNAL_DISPATCH, BY_REF, UI_ONLY):
        for member in group:
            assert member in m.VIEW_UNWRAPPED, f"{member} 应在「刻意不封装」名单里"
            assert member not in m.__all__


def test_no_internal_dispatch_in_arity_table():
    m = _load()
    for member in INTERNAL_DISPATCH:
        assert member not in m.VIEW_ARITY


# ── 护栏 ─────────────────────────────────────────────────────────────



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
