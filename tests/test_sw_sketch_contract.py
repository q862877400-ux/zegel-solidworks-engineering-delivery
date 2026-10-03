"""sw_sketch 的官方签名契约测试（不连接 SolidWorks）。

本文件锁三件本项目特有的事：
  1. **零参性** —— ISketch 上那 20 多个按类型取法**全是零参**，
     加了括号会 TypeError。
  2. **刻意不封装的成员要写明理由**（`SKETCH_UNWRAPPED`），
     不许悄悄消失。
  3. **属性 vs 方法** —— RelationManager / ModelToSketchTransform /
     Is3D 在反射里分别是 `get_` 与零参方法，形状各不相同。

签名来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → ISketch 段

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_sketch_contract.py —— 本文件自身
# 定位:   域 2 草图对象层的签名契约与「不封装要说理由」纪律锁。
# 被测对象: scripts/sw_sketch.py
# 覆盖:   全文件 —— 本文件是自包含测试单元，各测试函数已就地标明核对对象。
# ⚑ 2026-10-01（轮 117）：**本模块已真机实测** —— `python tools/verify_sketch_getters_smoke.py`
#   （**17/17**）。⚠ 但**本文件**里的判据仍是**静态**的（零 COM）；真机证据在 capability `sketch_query` 的 `evidence` 里。
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
MODULE_PATH = REPO_ROOT / "scripts" / "sw_sketch.py"
REFLECTION = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISketch 段
# 定位:   独立抄一遍的「按类型分列」零参取法（反射里全部无参）。
#         **不含** I 前缀的 COM 内部分发口。
# 覆盖:   后续同级定义
# ⚑ 2026-10-01（轮 117）：本表所列取法**已真机实测**（见 `tools/verify_sketch_getters_smoke.py`）。⚠ 本表本身仍是**静态照录**。
# ────────────────────────────────────────────────────────────────────
REFLECTED_ZERO_ARG = (
    "GetSketchSegments", "GetSketchContours", "GetSketchRegions",
    "GetSketchHatches", "GetSketchSlots", "GetSketchPictures",
    "GetSketchPaths", "GetSketchBlockInstances", "GetSketchTextSegments",
    "GetLines", "GetArcs", "GetArcs2", "GetEllipses", "GetEllipses2",
    "GetEllipses3", "GetParabolas", "GetParabolas2", "GetPolylines",
    "GetSplines", "GetSplinesInterpolate", "GetSketchPoints",
    "GetSketchPoints2", "GetUserPoints", "GetUserPoints2",
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
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    connect.set_com_member = _faithful
    connect.call_com_member = _faithful
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location("sw_sketch", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["sw_sketch"] = module
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


# ── 分类型取法表 ─────────────────────────────────────────────────────

def test_every_reflected_getter_is_in_the_table():
    m = _load()
    table = {name for members in m.SKETCH_GETTERS.values() for name in members}
    missing = [n for n in REFLECTED_ZERO_ARG if n not in table]
    assert not missing, f"登记表漏了这些官方零参取法: {missing}"


def test_no_internal_dispatch_members_in_table():
    """``I*`` 前缀的成员是 COM 内部分发口。"""
    m = _load()
    for members in m.SKETCH_GETTERS.values():
        for name in members:
            assert not re.match(r"^I[A-Z][a-z]", name), f"{name} 是内部分发口"


def test_getters_table_matches_reflection():
    """@brief 登记表里的每个名字，官方反射里都得**存在**（零参或照登记的参数量）。

    ⚑ 2026-10-01（轮 111）改：官方把 6 个旧取法标了 **Obsolete**，本模块改用后继 ——
    而后继里 **`GetLines2(Int16)` 多一个参数** ⇒ 原来「必须零参」的判据不再成立，
    改成「**在反射里存在**，且**零参的仍须零参**」。
    """
    if not REFLECTION.is_file():
        print("  (跳过：sldworks 反射清单不在本机)")
        return
    text = REFLECTION.read_text(encoding="utf-8", errors="replace")
    block = re.search(r"(?ms)^## ISketch\s*\r?\n(.*?)(?=\r?\n## |\Z)", text)
    assert block, "反射清单里取不到 ISketch 段"
    m = _load()
    #: ⚠ 本模块**刻意**用**带参**的后继（其余后继是零参）
    NON_ZERO_ARG_OK = {"GetLines2"}
    for members in m.SKETCH_GETTERS.values():
        for name in members:
            assert re.search(rf"\b{re.escape(name)}\s*\(", block.group(1)), (
                f"{name} 在官方反射里不存在")
            if name not in NON_ZERO_ARG_OK:
                assert re.search(rf"\b{re.escape(name)}\s*\(\s*\)", block.group(1)), (
                    f"{name} 在反射里不是零参（若它是有意为之，加进 NON_ZERO_ARG_OK 并写明理由）")


# ── 零参性 ───────────────────────────────────────────────────────────

def test_typed_getters_use_the_non_obsolete_successors():
    """@brief ★ 本模块 2026-10-01（轮 111）改用的**后继**取法。

    ⚠ 起因：`029` 的废弃成员台账查出这 6 个旧名**官方已标 `Obsolete`**。
    ⇒ 本测试把「**用的是后继**」钉住（防止有人改回旧名）。
    """
    m = _load()
    for func, member in ((m.get_arcs, "GetArcs2"),
                         (m.get_ellipses, "GetEllipses3"),
                         (m.get_parabolas, "GetParabolas2"),
                         (m.get_sketch_points, "GetSketchPoints2"),
                         (m.get_user_points, "GetUserPoints2"),
                         (m.get_sketch_contours, "GetSketchContours"),
                         (m.get_sketch_regions, "GetSketchRegions"),
                         (m.get_sketch_hatches, "GetSketchHatches"),
                         (m.get_sketch_slots, "GetSketchSlots"),
                         (m.get_sketch_pictures, "GetSketchPictures"),
                         (m.get_sketch_paths, "GetSketchPaths"),
                         (m.get_sketch_block_instances, "GetSketchBlockInstances"),
                         (m.get_sketch_segments, "GetSketchSegments"),
                         (m.get_polylines, "GetPolylines")):
        seen = []
        _record(m, seen, result=())
        func(object())
        assert seen == [(member, ())], f"{func.__name__} 应调 {member}() 零参"


def test_get_lines_passes_the_crosshatch_argument():
    """@brief ★ `GetLines2` 是**唯一带参**的后继：默认 `swCrossHatchInclude`（0）。

    官方：`System.object GetLines2(System.short CrossHatchOption)`，取 `swCrossHatchFilter_e`。
    ⚠ 官方**未说明**「含剖面线」是否等价于旧 `GetLines()` —— 本模块按**语义一致**取 `include`，
    这一点已在源码注释里声明。
    """
    m = _load()
    seen = []
    _record(m, seen, result=())
    m.get_lines(object())
    assert seen == [("GetLines2", (0,))], "应调 GetLines2(swCrossHatchInclude=0)"
    assert m.SKETCH_CROSS_HATCH["include"] == 0


def test_contour_edges_takes_one_argument():
    m = _load()
    seen = []
    _record(m, seen, result=())
    m.get_contour_edges(object(), "CONTOUR")
    assert seen == [("GetContourEdges", ("CONTOUR",))]


# ── 属性 vs 方法 ──────────────────────────────────────────────────────

def test_relation_manager_is_property():
    m = _load()
    seen = []
    _record(m, seen)
    m.get_relation_manager(object())
    assert seen == [("RelationManager", ())]


def test_model_to_sketch_transform_is_property_both_ways():
    m = _load()
    seen = []
    _record(m, seen)
    m.get_model_to_sketch_transform(object())
    assert seen == [("ModelToSketchTransform", ())]
    seen2 = []
    _record(m, seen2)
    m.set_model_to_sketch_transform(object(), "XFRM")
    assert seen2 == [("ModelToSketchTransform", ("XFRM",))]


def test_is_3d_is_zero_argument_method():
    m = _load()
    seen = []
    _record(m, seen, result=True)
    assert m.is_3d_sketch(object()) is True
    assert seen == [("Is3D", ())]


# ── 「不封装要说理由」纪律 ────────────────────────────────────────────

def test_unwrapped_members_each_carry_a_reason():
    m = _load()
    for member, reason in m.SKETCH_UNWRAPPED.items():
        assert reason and len(reason) > 8, f"{member} 缺「为什么不封装」的理由"
        assert member not in m.__all__, f"{member} 既说不封装又在导出清单里"


def test_unwrapped_set_matches_the_documented_reasons():
    m = _load()
    for member in ("GetSplineParams", "GetSplineParams2", "GetSplineParams3",
                   "GetSplineParams4", "SetWorkingPlaneOrientation"):
        assert member in m.SKETCH_UNWRAPPED, f"{member} 应在「刻意不封装」名单里"


# ── as_sequence 的诚实边界 ───────────────────────────────────────────

def test_as_sequence_handles_none_and_scalars():
    m = _load()
    assert m.as_sequence(None) == []
    assert m.as_sequence([1, 2]) == [1, 2]
    assert m.as_sequence((1, 2)) == [1, 2]
    assert m.as_sequence(7) == [7]


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

# ── 轮 140：`get_lines` 的**返回形状**（实测语义）──────────────────────
#
# ⚑ 实测（2026-10-01 轮 140，真机 SW 2026 SP4.1，`tools/probe_getlines_count.py`）：
#   画 1 条 ⇒ `get_sketch_segments`=1 · `get_lines`=**12**（元素类型 float）
#   画 2 条 ⇒ 2 · **24**      画 3 条 ⇒ 3 · **36**
#   ⇒ **每条直线占 12 个 float** ⇒ 它是**数值数组**，不是**对象列表**。
# ★ 这条**钉住语义**而不是"能不能跑" ——
#   ⚠ 此前冒烟只查「非空」⇒ **12 对 1 也照样绿**，于是这个语义**一直没人写下来**。


def test_get_lines_docstring_states_the_measured_shape():
    """@brief ★★ docstring 必须写明「数值数组」与「每条 12 个 float」。"""
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    i = src.index("def get_lines(")
    doc = src[i:i + 1600]
    assert "数值数组" in doc, "要写明返回的是数值数组"
    assert "12" in doc, "要写明每条占 12 个 float"
    assert "get_sketch_segments" in doc, "要给出「要几条线」的正确替代"


def test_get_lines_still_calls_the_successor():
    """@brief 仍是后继 `GetLines2`（轮 111 的结论不能被这次改动回退）。"""
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    i = src.index("def get_lines(")
    assert "GetLines2" in src[i:i + 1600]


def test_no_caller_treats_get_lines_result_as_line_objects():
    """@brief ★★ 仓库里**不许**有人把 `get_lines(...)` 的结果当线对象用。

    ⚠ 判据是**正向**的：结果元素是 `float` ⇒ `.X` / `.GetStartPoint2` 之类**必然错**。
    ⚠ 排除内嵌快照（`resources/skill`）—— 它是**构建产物**，由同步脚本生成。
    """
    bad = []
    for p in list(REPO_ROOT.rglob("*.py")):
        rel = str(p.relative_to(REPO_ROOT))
        if any(x in p.parts for x in (".git", "node_modules", "__pycache__")) \
                or "resources" in rel:
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8",
                                            errors="replace").splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            if re.search(r"get_lines\s*\([^)]*\)\s*\.", line):
                bad.append("%s:%d %s" % (rel, i, line.strip()[:70]))
    assert bad == [], "这些地方把 get_lines 的结果当对象用了:\n  " + "\n  ".join(bad)

# ── 轮 141：`get_*` 系列**都是「数值数组」**（通例，不是孤例）──────────
#
# ⚑ 实测（2026-10-01 轮 141，真机 SW 2026 SP4.1，`tools/probe_sketch_getter_shapes.py`）：
#   | 取法 | 画 1 个 | 画 2 个 | 每个占几个 float |
#   |---|---|---|---|
#   | get_lines    | 12 | 24 | **12** |
#   | get_arcs     | 16 | 32 | **16** |
#   | get_ellipses | 22 | 44 | **22** |
#   ⇒ ★ 三个**都是数值数组**（元素 `float`）⇒ 与轮 140 发现的 `get_lines` **同类**。
#   ⚠⚠ **轮 142 更正**：原写「`get_*` 系列**都是**数值数组」——**错的**。
#   `get_sketch_slots`（1/个）与 `get_sketch_points`（**2**/线）返回的是**对象列表**（`CDispatch`）
#   ⇒ ★ **两种形状都有**；规律**候选**（n=5，当假设）：曲线类 ⇒ 数值数组，点/实体类 ⇒ 对象列表。
#   ⚠ `get_splines` 量到 **0** —— 而根因是**样条根本画不出来**（另见下节）。

_GETTER_SHAPES = {"get_lines": 12, "get_arcs": 16, "get_ellipses": 22}


def test_type_getters_document_the_numeric_array_shape():
    """@brief ★★ 三个按类型取法的 docstring 都要写明「数值数组」与「每个占几个 float」。"""
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    for fn, per in _GETTER_SHAPES.items():
        i = src.index("def %s(" % fn)
        doc = src[i:i + 2000]
        assert "数值数组" in doc, "%s 要写明返回的是数值数组" % fn
        assert str(per) in doc, "%s 要写明每个占 %d 个 float" % (fn, per)
        assert "get_sketch_segments" in doc, "%s 要给出「要几个实体」的替代" % fn


def test_sketch_spline_fails_loudly_instead_of_returning_none():
    """@brief ★★ `sketch_spline` 在 `CreateSpline2` 返回 `None` 时**必须抛**。

    ⚑ 实测（轮 141）：`CreateSpline2` 返回 **`None`** ⇒ `get_sketch_segments` = **0**；
    ★ **重绘后仍是 0** ⇒ 排除了官方 Remarks 那句"必须重绘才看得见"的解释；
    后继 `CreateSpline3` 末参是 **BYREF `Object&`** ⇒ 事实 47/68 的架构限制。
    ⇒ 处置照 `sw_surface._invoke` 的先例（事实 40）：**让失败可见**。
    """
    import importlib.util
    import types
    spec = importlib.util.spec_from_file_location(
        "sw_part_probe", REPO_ROOT / "scripts" / "sw_part.py")
    mod = importlib.util.module_from_spec(spec)
    stub = types.ModuleType("sw_connect")
    stub.get_com_member = lambda obj, name: getattr(obj, name)
    #: ★★ 2026-10-03（轮 470）实现已改走 `set_com_member` 写属性
    #:   ⇒ 猴补丁只补 `get_com_member` **补不到**（★ 那正是本测试曾失败的根因）。
    stub.set_com_member = lambda obj, name: getattr(obj, name)
    sys.modules.setdefault("sw_connect", stub)
    spec.loader.exec_module(mod)

    class _Mgr:
        @staticmethod
        def CreateSpline2(_arr, _flag):      # noqa: N802
            return None

    class _Model:
        SketchManager = _Mgr()

        #: ★★★ 2026-10-01 轮 261（修地基 **D2** 带出的连锁修正）：
        #:   D2 给所有"画几何"的函数加了**"必须先有活动草图"**的守卫（`_require_active_sketch`）
        #:   ⇒ ★ 而本测试原来的 fake `_Model` **没有 `GetActiveSketch2`** ⇒
        #:     ★★ **守卫先于本测试要测的那一步抛错**，于是断言（只认"没建出来"/"None"）不成立。
        #:   ★ **修法不是放宽断言**（★ 那是"巴结门禁"）—— ★ **而是让 fake 更真实**：
        #:     补上 `GetActiveSketch2`，★ **这样测到的就是本测试**本来要测的**那一步**
        #:     （★ `CreateSpline2` 返回 `None` ⇒ 必须抛"没建出来"）。
        #:   ⚠ **为什么原来没写**：★ 那时还没有 D2 守卫，★ 所以这份 fake 够用（★ 而
        #:     「够用」是**当时的**够用 —— ★ 与事实 57 同一族：★ 前置是**隐含**的，
        #:     代码一改，隐含前置就暴露了）。
        @staticmethod
        def GetActiveSketch2():          # noqa: N802
            return object()              #: ★ 非 None ⇒ D2 守卫放行

    try:
        mod.sketch_spline(_Model(), [(0.0, 0.0), (10.0, 10.0)])
    except RuntimeError as exc:
        assert "没建出来" in str(exc) or "None" in str(exc), str(exc)
    else:
        raise AssertionError("sketch_spline 返回 None 时**没有抛** —— 静默空操作")


def test_sketch_spline_docstring_states_the_measured_failure():
    """@brief ★★ docstring 必须写明**实测建不出来**与**为什么**（免得下一个人再试）。"""
    src = (REPO_ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
    i = src.index("def sketch_spline(")
    doc = src[i:i + 2200]
    assert "轮 141" in doc, "要标注实测轮次"
    assert "重绘" in doc, "要写明「重绘后仍为 0」（排除掉那条解释）"
    assert "CreateSpline3" in doc, "要点出后继与它的 BYREF 末参"

def test_object_list_getters_document_their_shape():
    """@brief ★★ `get_sketch_slots` / `get_sketch_points` 返回**对象列表**（实测轮 142）。

    ⚑ 实测：画 1/2 个槽口 ⇒ **1/2** 个 `CDispatch`；画 1/2 条直线 ⇒ **2/4** 个
    （**每条线两个端点**）⇒ ★ 与曲线类取法（数值数组）**不同**。
    """
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    for fn in ("get_sketch_slots", "get_sketch_points"):
        i = src.index("def %s(" % fn)
        doc = src[i:i + 2000]
        assert "对象列表" in doc, "%s 要写明返回的是对象列表" % fn
        assert "轮 142" in doc, "%s 要标注实测轮次" % fn


def test_no_getter_claims_the_whole_family_is_one_shape():
    """@brief ★★ **不许**再出现「`get_*` 系列全都/都返回数值数组」这种一概而论。

    ⚠⚠ 轮 141 曾这样写，**轮 142 被实测推翻**（槽口/点是对象列表）
    ⇒ 这条判据**钉住那次更正**，免得下一个人又概括回去。
    """
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    bad = "get_*` 系列**都**返回数值数组"
    #: ⚠⚠ **判据要区分「引用」与「主张」**：更正文字**本身会引用那句错话**
    #:（"此处原写「…」——那是错的"）⇒ 不能一见到就报。
    #: 判据：每一处出现，**必须在它前面 40 字内**有「原写」或「更正」。
    idx = 0
    occurrences = 0
    while True:
        idx = src.find(bad, idx)
        if idx < 0:
            break
        occurrences += 1
        ctx = src[max(0, idx - 40):idx]
        assert ("原写" in ctx) or ("更正" in ctx), (
            "又出现**主张式**的一概而论（不是引用）：…%s…" % src[max(0, idx - 40):idx + len(bad) + 10])
        idx += len(bad)
    assert occurrences >= 1, "更正说明里应当**引用**那句错话（作为'原写'）"
    #: ✓ 反过来：更正说明必须在
    assert "两种形状都有" in src, "要写明「两种形状都有」"
