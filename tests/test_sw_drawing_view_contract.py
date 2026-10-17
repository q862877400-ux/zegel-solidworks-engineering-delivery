"""sw_drawing_view 的官方签名契约测试（不连接 SolidWorks）。

`IView` 是全库最大的接口族（反射实测 496 个成员）。本模块把其中
207 个「不同能力」做成登记表 + 通用访问器，因此本文件的核心是
**把登记表逐条对回反射清单** —— 少一条是漏，多一条是我编的。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → IView 段

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_drawing_view_contract.py —— 本文件自身
# 定位:   域 9 工程图视图族的登记表完整性契约与「编号变体折叠」取舍声明。
# 被测对象: scripts/sw_drawing_view.py
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_drawing_view.py"
REFLECTION = Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect_sldworks" / "iface_sldworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IView 段
# 定位:   独立复算的期望规模（由本测试**自己逐行解析**，不读生成器的中间产物）。
#         构成：原始成员 / I 前缀内部分发口 / 属性 / 方法 / 编号变体。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
EXPECTED_COMPOSITION = {
    "raw_members": 496,
    "internal_dispatch": 134,
    "methods": 301,
    "distinct_capabilities": 207,
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
    #: ★★★ 2026-10-03（轮 470）**删掉我重复加的那块** ——
    #:   本测试在轮 319 就**已经**把 `set_com_member = _faithful_write` 补好了（见上面一行），
    #:   ★ 而我同轮的批量脚本**只看"下一行有没有"** ⇒ 又插了一块，
    #:   而那块把它**覆盖成 `_faithful`**（★ 取/调语义）⇒ **12 个测试一起红** ⚠
    #:   ★ 教训同 `test_sw_simulation_study_options_contract`：**批量脚本必须先看整个作用域**。
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_drawing_view", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_drawing_view"] = module
    spec.loader.exec_module(module)
    module.set_com_member = _faithful_write
    module.get_com_member = _faithful
    module.call_com_member = _faithful
    return module


def _parse_iface():
    """逐行解析 IView 段。

    ⚑ 刻意**不用正则切段** —— 前瞻 ``(?=\\r?\\n## |\\Z)`` 会提前截断
    （实测把 116 行的 IModelView 段截成 3761 字符，导致误判成员归属）。
    """
    if not REFLECTION.is_file():
        return None
    current, out = None, []
    for raw in REFLECTION.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
        if raw.startswith("## "):
            if current == "IView":
                break
            current = raw[3:].strip()
            if current == "IView":
                out = []
        elif current == "IView" and raw.strip():
            out.append(raw.strip())
    return out


# ── 登记表完整性（本文件核心）────────────────────────────────────────

def test_registry_has_expected_size():
    m = _load()
    assert len(m.VIEW_MEMBER_ARITY) == EXPECTED_COMPOSITION["distinct_capabilities"], (
        f"能力登记表应为 {EXPECTED_COMPOSITION['distinct_capabilities']} 项，"
        f"实际 {len(m.VIEW_MEMBER_ARITY)}")


def test_every_registered_name_really_exists_in_iview():
    if _parse_iface() is None:
        print("  (跳过：反射清单不在本机)")
        return
    block = _parse_iface()
    m = _load()
    for name in m.VIEW_MEMBER_ARITY:
        assert any(f"{name}(" in line for line in block), (
            f"{name} 不在 IView 段里 —— 可能编造")


def test_registry_arities_match_reflection():
    """登记表的实参个数必须与反射逐条一致。"""
    if _parse_iface() is None:
        print("  (跳过：反射清单不在本机)")
        return
    block = _parse_iface()
    m = _load()
    sig = re.compile(r"^(\S+)\s+(\w+)\s*\((.*)\)$")
    real: dict[str, list[int]] = {}
    for line in block:
        hit = sig.match(line)
        if not hit:
            continue
        _, name, args = hit.groups()
        real.setdefault(name, []).append(
            len([a for a in args.split(",") if a.strip() and not a.strip().endswith("&")]))
    wrong = []
    for name, arity in m.VIEW_MEMBER_ARITY.items():
        if name not in real:
            continue                      # 折叠后的基础名，见下一条测试
        if arity not in real[name]:
            wrong.append((name, arity, real[name]))
    assert not wrong, f"这些能力的实参个数与反射不符: {wrong[:5]}"


# ── 组成统计（防止后续误读 IView 的规模）──────────────────────────

def test_composition_of_iview_is_as_documented():
    """模块头声称的组成必须与反射实测一致 —— 数字错了文档就在误导人。"""
    if _parse_iface() is None:
        print("  (跳过：反射清单不在本机)")
        return
    block = _parse_iface()
    sig = re.compile(r"^(\S+)\s+(\w+)\s*\((.*)\)$")
    internal = properties = methods = 0
    for line in block:
        hit = sig.match(line)
        if not hit:
            continue
        _, name, _args = hit.groups()
        if re.match(r"^I[A-Z]", name):
            internal += 1
        elif name.startswith(("get_", "set_")):
            properties += 1
        else:
            methods += 1
    assert len(block) == EXPECTED_COMPOSITION["raw_members"], (
        f"原始成员应为 {EXPECTED_COMPOSITION['raw_members']}，实际 {len(block)}")
    assert internal == EXPECTED_COMPOSITION["internal_dispatch"], (
        f"I 前缀内部分发口应为 {EXPECTED_COMPOSITION['internal_dispatch']}，"
        f"实际 {internal}")
    assert methods == EXPECTED_COMPOSITION["methods"], (
        f"方法应为 {EXPECTED_COMPOSITION['methods']}，实际 {methods}")


def test_no_internal_dispatch_members_registered():
    m = _load()
    for name in m.VIEW_MEMBER_ARITY:
        assert not re.match(r"^I[A-Z][a-z]", name), f"{name} 是 COM 内部分发口"


def test_property_names_are_not_in_the_method_registry():
    """属性（get_/set_）不该出现在「方法 arity」表里。"""
    m = _load()
    overlap = set(m.VIEW_PROPERTY_NAMES) & set(m.VIEW_MEMBER_ARITY)
    assert not overlap, f"这些既是属性又登记成方法: {sorted(overlap)[:8]}"


def test_numbered_variants_are_folded_and_declared():
    """编号变体（X2/X3）被折叠到基础名 —— 这是**取舍声明**，不是「它们等价」。"""
    m = _load()
    numbered = [n for n in m.VIEW_MEMBER_ARITY if re.search(r"\d+$", n)]
    # 允许残留的编号名必须是「基础名不在表里」的情况（即基础名本身带数字语义）
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "编号变体已折叠" in source
    assert "明确声明的取舍" in source
    assert numbered, "反射里确有 94 个编号变体，折叠后应仍有少量残留"


# ── 通用访问器 ───────────────────────────────────────────────────────

def test_call_view_rejects_unknown_member_loudly():
    m = _load()
    try:
        m.call_view(object(), "NotARealMember")
    except KeyError as exc:
        assert "NotARealMember" in str(exc)
        return
    raise AssertionError("未登记的成员名被放行了 —— 会静默传错成员给 COM")


def test_call_view_rejects_wrong_arity_before_calling_com():
    m = _load()
    zero = next(n for n, a in m.VIEW_MEMBER_ARITY.items() if a == 0)
    try:
        m.call_view(object(), zero, 1, 2)
    except ValueError as exc:
        assert zero in str(exc)
        return
    raise AssertionError("错 arity 未被拦")


def test_call_view_rejects_none_target():
    m = _load()
    zero = next(n for n, a in m.VIEW_MEMBER_ARITY.items() if a == 0)
    try:
        m.call_view(None, zero)
    except ValueError as exc:
        assert "None" in str(exc)
        return
    raise AssertionError("None 目标未被拦")


def test_call_view_passes_through_on_correct_arity():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or "OK")
    m.set_com_member = lambda o, n, v, **k: sink.append((n, (v,))) or result
    m.call_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or "OK")
    zero = next(n for n, a in m.VIEW_MEMBER_ARITY.items() if a == 0)
    assert m.call_view(object(), zero) == "OK"
    assert seen == [(zero, ())]


# ── 属性型成员（属性 vs 方法）─────────────────────────────────────────

def test_scale_and_name_are_properties_not_methods():
    m = _load()
    seen = []
    m.get_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or 1.0)
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, v: (seen.append((n, (v,))) or 1.0)
    m.call_com_member = lambda o, n, *a, **k: (seen.append((n, a)) or 1.0)
    m.set_view_scale(object(), 2.0)
    #: ★★★ 2026-10-01（轮 293）**契约随证据更新**：
    #:   旧断言写的是 `("Scale", (2.0,))` —— ★ **而 `IView` 上没有 `Scale` 这个成员**：
    #:   真机报 `AttributeError: <unknown>.Scale`（事实 36 的形态）。
    #:   ★★ 官方真名是 **`ScaleRatio`**（`C:\swapi\types\IView\ScaleRatio.md`：
    #:   "Gets or sets the scale of the drawing view, returning the results in ratio format (n:n)"，
    #:   Returns: **Array of 2 doubles**）⇒ ★ 按 `n:1` 写两个数。
    #:
    #: ★★★ 2026-10-03（轮 470）**契约再次随证据更新**（★ 这次更新的是"调用次数"这一维）：
    #:   ★ 轮 467 给 `set_view_scale` **加了回读**（★ 规则 6：不静默成功）⇒ 它现在会
    #:     ① 读 `UseSheetScale` ② 写下它 ③ 读 `ScaleRatio`(before) ④ **写它** ⑤ 读它(after)
    #:   ⇒ ★★ `seen` 里**混了读与写** —— ★ 而那是**更好的实现**，不该为了测试把它退回去。
    #:   ★ 故断言从"**全部**调用等于…"改成"**那次写**在里面"，★ **保留原意图**
    #:     （真名 `ScaleRatio` + 两个数），★ 并且**把"读"的那几次也实名核到** ——
    #:     ★ 这不是放松判据，是把判据拆成"读"与"写"两栏各自核 ✓
    _writes = [(n, a) for n, a in seen if a]                    # ★ 带实参的才是"写"
    assert ("ScaleRatio", ((2.0, 1.0),)) in _writes, _writes
    assert [n for n, _ in _writes] == ["UseSheetScale", "ScaleRatio"], _writes
    assert [n for n, a in seen if not a] == ["UseSheetScale", "ScaleRatio", "ScaleRatio"], seen
    seen2 = []
    m.get_com_member = lambda o, n, *a, **k: (seen2.append((n, a)) or "V1")
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    m.set_com_member = lambda o, n, v: (seen2.append((n, (v,))) or "V1")
    m.call_com_member = lambda o, n, *a, **k: (seen2.append((n, a)) or "V1")
    assert m.get_view_name(object()) == "V1"
    #: ★★★★ 2026-10-04（轮 110）**契约再次随证据更新** —— 处置阶段 2 · T1 ✓
    #:   ★ **官方逐字**（★ `C:\swapi\types\IView\Name.md`）：
    #:     > ★ 「Obsolete. **Superseded by `IView::GetName2` and `IView::SetName2`**」✓
    #:   ★★ **`get_view_name` 现在也走**仓里那两处**的写法**（★
    #:     `sw_drawing_create_missing.py` L193-195 · ★ `sw_drawing_query.py` L191-193）✓
    #:   ★★★ **⚠ 而"两代都试"≠"都调"** —— ★ 实测：★ `GetName2` 回真值 ⇒ **早退**、
    #:     不试 `Name` ⇒ ★★ **`seen2` 只有一条**（★ 我第一版期望两条 ⇒ **红了**）✓
    #:   ★★★★ **⇒ 断言："先试 `GetName2`；★ 它给了值就**只调它一个**"** ——
    #:     那不是放松判据：★ 它守的是**顺序**（★ 后继在前）+ ★ **早退语义** ✓
    assert seen2 == [("GetName2", ())], seen2
    #: ★★★★ **2026-10-10（规格 301）订正：负例已随 `spec 256` 反转** ——
    #:   ★★ **原文**（已作废）逐字是：
    #:     「★★★ **并补一条负例**：★ 当 `GetName2` **给不出值**时，
    #:      ★ **必须**回落到老成员 `Name`（★ 兜底不能丢）✓」
    #:   ★★★ **而 `spec 256` 把兜底**有意删掉**了** —— ★ 它的 docstring 逐字：
    #:     「★ **真机**（SW **34.4.1**）在 **5 个视图**上测得 `Name` == `GetName2` **全部相同**
    #:      ⇒ ★ **两代不等价的风险已排除** ⇒ ★ **不再调用废弃成员**」+
    #:     「★★★ **行为变化（★ 如实记）**：★ 若 `GetName2` 抛异常 ⇒ ★ 现在报 **空串**
    #:      （★ 原先会回落取 `Name`）。★ 这是**有意的**：★ 失败就是**取不到名字**，
    #:      ★ **不换一个废弃成员再试**。」
    #:   ★★★★ **⇒ 本条负例改成守「**不再回落**」**（★ 与 `spec 256` 的结论一致）：
    #:     ★ `GetName2` 给不出值 ⇒ ★ 回**空串**、★ 且 **`Name` 一次都不许被调** ✓
    #:   ★★ **依据**（`MEMORY.md` 规则 28）：「改实现前先搜『有没有测试钉住旧行为』——
    #:     ★ 不同步改就等于**在断言错的东西**」✓
    seen3 = []
    m.get_com_member = lambda o, n, *a, **k: (seen3.append((n, a)) or ("" if n == "GetName2" else "V2"))
    m.set_com_member = lambda o, n, v: (seen3.append((n, (v,))) or "V2")
    m.call_com_member = lambda o, n, *a, **k: (seen3.append((n, a)) or "V2")
    assert m.get_view_name(object()) == "", "★ `GetName2` 给不出值 ⇒ 应回**空串**（★ spec 256 起不再回落）"
    assert seen3 == [("GetName2", ())], (
        "★ 回落到了废弃成员 `Name` ⇒ 与 `spec 256` 的结论（**有意不回落**）矛盾：%r" % seen3)




def test_orient_toward_is_removed_because_it_cannot_be_found():
    """⚑⚑ **删掉了一个查不到的成员**。

    `get_orient_toward` 初稿调 ``IView.OrientToward(Object, Double, Double)``。
    按铁律 4 查**两套官方源**：
      ① 对 sldworks.dll 的纯元数据反射 —— 全程序集无此成员名
      ② CHM 全文检索 ``OrientToward`` —— 无结果
    ⇒ 按铁律 5「查不到就写查不到并停」，**删除该封装**，
      不拿相似名字蒙混。本测试锁住这个决定，防止有人再加回来。
    """
    m = _load()
    assert not hasattr(m, "get_orient_toward"), (
        "OrientToward 两套官方源都查不到，不得提供该封装")
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert '"OrientToward"' not in source, "源码里不应再出现 OrientToward"
    assert "查不到" in source, "应写明「为什么不做」"
    # IView 上真实存在的定向相关成员
    for real in ("ScaleDecimal", "ScaleRatio", "GetOrientationName"):
        assert re.search(rf"\b{real}\b", source), f"{real} 是真实成员，应有交代"




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
