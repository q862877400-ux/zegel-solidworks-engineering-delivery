"""★ spec 248：`Name` 的**逐宿主表达式**表态（245 只登记了 2 个证据站点，51 处宿主从未逐条判）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   tests/test_obsolete_multi_successor_impact.py（245 的口径 `_hit_sites` / `_member_calls` / `_HOST_REVIEW`）
#         tests/test_deprecated_entry_interlock.py（`_scan_all_modules` / `_scan_calls`）
#         specs/202-user-coverage-gaps/recon/official-obsolete-index.json（`Name` 两条：IComponent2 / IView）
#         C:/swapi/types/{IView,IFeature,IBody2,IConfiguration,IModelDoc2,IFeatureManager}/*.md
# 定位:   245 把 `Name` 表态成 `mixed`，但**只登记了 2 个证据站点** ⇒ ★ 51 处宿主的接口**从未逐条判过**；
#         ★ 本文件把口径下沉到**宿主表达式**粒度：16 个宿主表达式逐个表态 ⇒ **新增一个宿主即红**。
# 官方依据: IView/Name.md「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]」
#           vs IFeature/Name.md「Gets or sets the name of the current feature.」（非废弃）
#           vs IBody2/Name.md「Gets or sets the name of the selected body.」（非废弃）
#           vs IConfiguration/Name.md「Gets or sets the configuration name.」（非废弃）
#           IModelDoc2/ActiveView.md Returns「Current active [[model view]]」⇒ 宿主 `av` 是 IView
#           IFeatureManager/InsertWrapFeature2.md Returns「Wrap [[feature]]」⇒ 宿主 `obj` 是 IFeature
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读索引 / 官方页 / 真树源码；★ 不改 `tools/build_obsolete_index.py`、不改 `sw_com_traps`
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.test_deprecated_entry_interlock import _scan_all_modules, _scan_calls  # noqa: E402
from tests.test_obsolete_multi_successor_impact import (  # noqa: E402
    FALSE_HIT as _245_FALSE,
    MIXED as _245_MIXED,
    REAL_HIT as _245_REAL,
    _HOST_REVIEW,
    _hit_sites,
    _member_calls,
)

NAME = "Name"

#: ★★ 索引里 `Name` 的**两条**废弃条目所在接口（`IComponent2::Name` · `IView::Name`）。
#: ★ 真命中的判据 = **宿主接口落在这一集合里**；★ 落不进去就是**别的接口的同名成员**（假命中）。
DEPRECATED_NAME_IFACES = ("IComponent2", "IView")

#: ★★★ **spec 256 已换掉 `IView::Name` 的 3 个文件**（★ 4 处：`sw_drawing_query.py` ×2 ·
#:   `sw_drawing_view.py` · `sw_review.py`）⇒ ★ 这些文件里**不再有** `Name` 调用 ⇒
#:   ★★ 它们**合法地**从本表消失（★ 见 `_NAME_HOST_REVIEW` 的墓碑）· ★ 也是棘轮 4 → 0 的**依据**。
SUPERSEDED_BY_256 = ("sw_drawing_query.py", "sw_drawing_view.py", "sw_review.py")

REAL_HIT = "real-hit"
FALSE_HIT = "false-hit"
CODES = {REAL_HIT, FALSE_HIT}

#: ★★★ **逐宿主表达式表态表**（★ 键 = `ast.get_source_segment` 取到的宿主表达式原文）。
#: ★ 值 = (code, 宿主接口, 依据, 站点)；★ 站点 = **站点所在文件的多重集**，★ 必须与重算结果相等。
#: ★★★ **2026-10-10（spec 292）把站点从 `(文件, 行号)` 改成 `(文件,)`** —— ★ 行号会漂（★ 铁律 7）；
#:   ★★ 实测 **~40 个切片里破了 4 次**（★ 256/261 换路由 · 新增站点 · 文档增行）⇒ ★ 那是**假红发生器**。
#: ★★ 为什么按**宿主表达式**而不是按裸名：245 已证同名成员横跨多接口，按裸名算会把假命中当真命中。
_NAME_HOST_REVIEW: dict[str, tuple[str, str, str, tuple[str, ...]]] = {
    "feature": (
        FALSE_HIT,
        "IFeature",
        "宿主来自 `iter_features(model)` / `FeatureByPositionReverse` / `PostIntersect` / `Insert*` "
        "⇒ **IFeature**；★ 官方 `IFeature/Name.md` 首行是「Gets or sets the name of the current feature.」"
        "（**非废弃**）⇒ ★ 不是被废弃的 `IView::Name`。",
        ("sw_boolean_ops.py", "sw_review.py", "sw_sheet_metal.py",
         "sw_sheet_metal.py", "sw_sheet_metal_weld_entry.py", "sw_sketch.py",
         "sw_weldment.py", "sw_weldment.py", "sw_weldment.py",
         "sw_weldment.py", "sw_weldment.py", "sw_weldment.py",
         "sw_weldment.py"),
    ),
    "study": (
        FALSE_HIT,
        "CWStudy",
        "宿主来自 `iter_studies(sw_app)` → `IStudyManager::GetStudy` ⇒ **CWStudy**（cosworks 仿真族）；"
        "★ 该族在 `C:/swapi/types/` **无页**，但 ★ 索引里 `Name` 只有 `IComponent2` / `IView` 两条 ⇒ "
        "★ 本宿主**不可能**落在废弃条目上。",
        ("sw_simulation.py", "sw_simulation.py", "sw_simulation.py",
         "sw_simulation.py", "sw_simulation.py", "sw_simulation_study.py",
         "sw_topology.py", "sw_topology.py", "sw_topology.py",
         "sw_topology.py"),
    ),
    "feat": (
        FALSE_HIT,
        "IFeature",
        "宿主来自 `get_com_member(feat, \"GetNextFeature\")` 链 / `Insert*` 的返回值 ⇒ **IFeature**；"
        "★ `IFeature::Name` 非废弃。",
        ("sw_boolean_ops.py", "sw_helix.py", "sw_mold.py", "sw_mold.py",
         "sw_mold.py", "sw_mold.py", "sw_sensor.py", "sw_sheet_metal.py"),
    ),
    "f": (
        FALSE_HIT,
        "IFeature",
        "宿主来自 `iter_features_recursive(model)` / `_selected_feature_objects(model)` ⇒ **IFeature**；"
        "★ `IFeature::Name` 非废弃。",
        ("sw_sketch.py", "sw_sketch.py", "sw_weldment.py"),
    ),
    #: ★★★ **墓碑（spec 292）**：这里原有 `"view"`（`IView`，真命中 · 3 处）与 `"av"`（`IView`，真命中 · 1 处）
    #:   ⇒ ★★ **spec 256 已把 4 处全换成官方后继 `IView::GetName2`** ⇒ ★ 真树上**不再有** `Name` 的调用
    #:   ⇒ ★ 条目按纪律**删掉**（★ 留着 = 空口表态 ⇒ 判据会报「表里登记的宿主不存在」）。
    #:   ★★★ **⇒ 本表的真命中现在是 `0`** ⇒ ★ `Name` 这条线**已收口**（★ 见 `test_name_route_is_closed_by_256`）。
    "x": (
        FALSE_HIT,
        "IBody2",
        "宿主来自 `get_bodies(cost_manager)` 的元素 ⇒ **IBody2**；★ 官方 `IBody2/Name.md` 首行是"
        "「Gets or sets the name of the selected body.」（**非废弃**）。",
        ("sw_costing.py", "sw_costing.py", "sw_costing.py"),
    ),
    "configuration": (
        FALSE_HIT,
        "IConfiguration",
        "宿主来自 `ConfigurationManager::ActiveConfiguration` ⇒ **IConfiguration**；"
        "★ 官方 `IConfiguration/Name.md` 首行是「Gets or sets the configuration name.」（**非废弃**）。",
        ("sw_weldment.py", "sw_weldment.py"),
    ),
    "active": (
        FALSE_HIT,
        "IConfiguration",
        "同 `configuration`：宿主来自 `ActiveConfiguration` ⇒ **IConfiguration**（非废弃）。",
        ("sw_document_data.py",),
    ),
    #: ★★ **墓碑（spec 292）**：`"av"`（`IView`，真命中 · `sw_review.py`）也**删掉**了 ——
    #:   ★ **spec 256 换路由**把 `sw_review.py` 那处 `av.Name` 换成了 `av.GetName2` ✓
    #:   ★ 与上面 `"view"` 同因（★ 见那段墓碑）。
    "body": (
        FALSE_HIT,
        "IBody2",
        "宿主来自 `model.GetBodies2(SW_SOLID_BODY, False)` 的元素 ⇒ **IBody2**（非废弃）。",
        ("sw_sheet_metal.py",),
    ),
    "cfg": (
        FALSE_HIT,
        "IConfiguration",
        "宿主来自 `_active_configuration(model)` ⇒ **IConfiguration**（非废弃）。",
        ("sw_render_material.py",),
    ),
    "entry": (
        FALSE_HIT,
        "CWLoadsAndRestraints",
        "宿主来自 `CWLoadsAndRestraintsManager::GetLoadsAndRestraints` ⇒ **CWLoadsAndRestraints**"
        "（cosworks 族，`C:/swapi/types/` 无页）⇒ ★ 不可能是 `IView::Name`。",
        ("sw_simulation.py",),
    ),
    "obj": (
        FALSE_HIT,
        "IFeature",
        "宿主是 `FeatureManager::InsertWrapFeature2` 的返回值，★ 官方 Returns 逐字「Wrap [[feature]]」"
        "⇒ **IFeature**（非废弃）。",
        ("sw_wrap.py",),
    ),
    "property_object": (
        FALSE_HIT,
        "ICableProperty",
        "宿主来自 `ICable::GetCableProperty`（注释逐字 `CableProperty GetCableProperty()`）"
        "⇒ **ICableProperty**（routing 族）⇒ ★ 不可能是 `IView::Name`。",
        ("sw_routing.py",),
    ),
    "sk": (
        FALSE_HIT,
        "ISketch",
        "宿主来自 `sw_sketch.active_sketch(model)`（`ISketchManager::ActiveSketch`）⇒ **ISketch**；"
        "★ `C:/swapi/types/` 下**没有** `ISketch/Name.md` ⇒ 该成员不废弃。",
        ("sw_sketch_modify_ops.py",),
    ),
    "table": (
        FALSE_HIT,
        "ISwDMTable6",
        "宿主是本模块 `read_table_name(table)` 的形参 ⇒ **ISwDMTable6**（PDM 家族）"
        "⇒ ★ 不可能是 `IView::Name`。",
        ("sw_pdm.py",),
    ),
}

#: ★ 下界（★ 只允许增不允许减；★ 减少 = 探测器漏了，不是「问题解决了」）。
#: ★★★ **2026-10-10（spec 292）三处下调 —— ★ 每处都写了「为什么是正当减少」**：
#:   · `BASELINE_HOSTS` **16 → 14** · `BASELINE_SITES` **51 → 47** · `BASELINE_REAL_SITES` **4 → 0**
#:   ★★ **真因**：**spec 256 把 `IView::Name` 的 4 处全换成了官方后继 `GetName2`**
#:     （★ `sw_drawing_query.py` ×2 · `sw_drawing_view.py` · `sw_review.py`）
#:   ⇒ ★ 两个真命中宿主 `view`(3 处) / `av`(1 处) 从真树上**消失** ⇒ ★ 条目删除（★ 见墓碑）。
#:   ★★★ **⇒ 本表的真命中现在是 `0`** ⇒ ★ `Name` 这条线**已收口** ✓
#:   ★★ **内容断言**（★ 铁律 22）：`test_name_route_is_closed_by_256` 按**名字**钉住那 4 处已换。
BASELINE_HOSTS = 14
BASELINE_SITES = 47
BASELINE_REAL_SITES = 0
BASELINE_FALSE_SITES = 47


# ── ⑤ ★★★ **内容断言**：`Name` 的 4 处真命中已被 spec 256 换成 `GetName2` ──
def test_name_route_is_closed_by_256():
    """★★★ **棘轮下调的内容断言**（★ 铁律 22）：★ 下界从 16/51/4 降到 14/47/0 **必须能被证明**。

    ★★ 证据 = `IView::Name` 的 4 处已被 **spec 256** 换成官方后继 `IView::GetName2`。
    ★ 判据**按名字定位**（★ 铁律 7）：★ 3 个站点文件里**必须**有 `GetName2`；
    ★★ 且真树上**不得**再出现 `IView` 宿主上的 `Name`（★ 即表里没有 `REAL_HIT`）。
    """
    reals = sorted(h for h, (c, _i, _w, _s) in _NAME_HOST_REVIEW.items() if c == REAL_HIT)
    assert not reals, "还有真命中宿主 %s ⇒ 下界 4 → 0 不成立" % reals
    for fname in ("sw_drawing_query.py", "sw_drawing_view.py", "sw_review.py"):
        src = (SCRIPTS / fname).read_text(encoding="utf-8", errors="replace")
        assert "GetName2" in src, \
            "★ `%s` 里没有官方后继 `GetName2` ⇒ 256 的换路由证据不成立" % fname


def _host_sites() -> dict[str, list[str]]:
    """★ 重算：宿主表达式 → **站点所在文件的多重集**（★ 只取 `Name`，★ 口径逐字同 245 的 `_hit_sites`）。

    ★★★ **spec 292 改成「按文件」** —— 原先按 `(文件, 行号)` ⇒ ★★ **行号一漂全表红**（★ 铁律 7）。
    ★★ 保留**多重集**（不是集合）⇒ ★ 同名文件的**处数**仍被约束（★ 去行号**没有**放宽）。
    """
    out: dict[str, list[str]] = {}
    for (fname, _ln, host) in _hit_sites().get(NAME, set()):
        out.setdefault(host, []).append(fname)
    return out


def _adjudication_failures(
    host_sites: dict[str, list[str]],
    table: dict[str, tuple[str, str, str, tuple[str, ...]]],
) -> list[str]:
    """★ 纯函数：返回问题清单（★ 空 = 通过）。

    ★ 查四样：① 重算出的宿主是否都表了态；② 表里的宿主在真树上是否还在；
    ③ 表态码是否落在封闭词表、且与宿主接口是否**自洽**（真命中 ⟺ 接口 ∈ 索引条目的接口）；
    ④ 证据站点与重算站点是否**按文件多重集相等**（★ spec 292：**不按行号** —— 铁律 7）。
    """
    out: list[str] = []
    for host in sorted(host_sites):
        if host not in table:
            out.append("宿主 %r 未表态（真树上有 %d 处）" % (host, len(host_sites[host])))
    for host in sorted(table):
        code, iface, _why, sites = table[host]
        if code not in CODES:
            out.append("宿主 %r 的表态码 %r 不在封闭词表 %s 里" % (host, code, sorted(CODES)))
            continue
        if host not in host_sites:
            out.append("表里登记的宿主 %r 在真树上**不存在** ⇒ 空口表态（★ 删掉或改名了）" % host)
            continue
        is_real = iface in DEPRECATED_NAME_IFACES
        if is_real != (code == REAL_HIT):
            out.append(
                "宿主 %r 表态 %r 但接口 %s %s 索引里 `Name` 条目的接口 %s ⇒ 表态与接口矛盾"
                % (host, code, iface, "∈" if is_real else "∉", list(DEPRECATED_NAME_IFACES)))
        if Counter(sites) != Counter(host_sites[host]):
            out.append(
                "宿主 %r 的证据文件与重算不符：表里多 %s / 表里少 %s"
                % (host, sorted((Counter(sites) - Counter(host_sites[host])).elements()),
                   sorted((Counter(host_sites[host]) - Counter(sites)).elements())))
    return out


# ── ① 覆盖：每个宿主表达式都要表态（★ 纯函数 + 真树）────────────────
def test_every_host_expression_is_adjudicated():
    """★★ 14 个宿主表达式**全部**要表态；★ 47 处站点**全部**要落进表里。少一个即红。

    ★★★ **spec 292**：★ 真命中 `view`/`av` 已被 **256** 换掉 ⇒ ★ 16 → **14** 名 · 51 → **47** 处。
    """
    hosts = _host_sites()
    total = sum(len(v) for v in hosts.values())
    assert len(hosts) >= BASELINE_HOSTS, \
        "宿主表达式从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_HOSTS, len(hosts))
    assert total >= BASELINE_SITES, \
        "`Name` 站点从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_SITES, total)
    bad = _adjudication_failures(hosts, _NAME_HOST_REVIEW)
    assert not bad, "宿主级表态不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 本判据**能红**：合成负例 ──────────────────────────────────
def test_criterion_catches_unadjudicated_host():
    """★★ 合成负例：★ 真树上冒出一个**未表态**的宿主 ⇒ 纯函数必须报出来（★ 否则是空判据）。

    ★★★ **spec 292 改法**：原先拿真命中宿主 `view` / `av` 当变异体 —— ★ 而 **256 已把它们换掉**
      ⇒ ★ 变异体**不存在**了 ⇒ ★ 改用**合成**变异（★ 不依赖真树现状，★ 更稳）：
      · 把**假命中**宿主 `body` 的接口改成 `IView` ⇒ ★ **表态与接口矛盾**必须被抓到；
      · 删掉宿主 `body` 的表态 ⇒ ★ **覆盖判据**必须抓到「未表态」。
    """
    hosts = _host_sites()

    synthetic = {k: list(v) for k, v in hosts.items()}
    synthetic["__bogus_host__"] = ["sw_probe_synthetic.py"]
    bad = _adjudication_failures(synthetic, _NAME_HOST_REVIEW)
    assert any("__bogus_host__" in b for b in bad), \
        "合成宿主未被判出 ⇒ 覆盖判据是**空判据**：%r" % bad

    #: ★ 合成「矛盾」：★ 假命中宿主 + 真命中接口 ⇒ 必须报
    flipped = dict(_NAME_HOST_REVIEW)
    code, _iface, why, sites = flipped["body"]
    flipped["body"] = (code, "IView", why, sites)
    bad2 = _adjudication_failures(hosts, flipped)
    assert any("表态与接口矛盾" in b for b in bad2), \
        "把 `body` 的接口改成 `IView` 却未被判出 ⇒ 自洽判据是**空判据**：%r" % bad2

    #: ★ 合成「漏表态」：★ 删掉一个**真树上存在**的宿主的表态 ⇒ 必须报
    dropped = {k: v for k, v in _NAME_HOST_REVIEW.items() if k != "body"}
    bad3 = _adjudication_failures(hosts, dropped)
    assert any("body" in b for b in bad3), \
        "删掉 `body` 的表态却未被判出 ⇒ 覆盖判据是**空判据**：%r" % bad3

    #: ★★ 合成「站点证据不符」：★ 给某个宿主的站点**多塞一个文件** ⇒ 必须报（★ 新口径也能红）
    shifted = dict(_NAME_HOST_REVIEW)
    c4, i4, w4, s4 = shifted["body"]
    shifted["body"] = (c4, i4, w4, tuple(s4) + ("sw_probe_synthetic.py",))
    bad4 = _adjudication_failures(hosts, shifted)
    assert any("证据文件与重算不符" in b for b in bad4), \
        "站点证据多一个文件却未被判出 ⇒ **按文件**的新口径是**空判据**：%r" % bad4


# ── ③ 封闭词表 ────────────────────────────────────────────────────────
def test_codes_are_closed_vocabulary():
    """★ 表态码必须落在封闭词表里（★ 不许写「待定 / unknown」糊过去）。"""
    bad = sorted(h for h, (code, _i, _w, _s) in _NAME_HOST_REVIEW.items() if code not in CODES)
    assert not bad, "以下宿主的 code 不在 %s 里：%s" % (sorted(CODES), bad)


# ── ④ 真命中 / 假命中的下界 ───────────────────────────────────────────
def test_real_and_false_site_lower_bounds():
    """★ 真命中站点（4）与假命中站点（47）的下界（★ 只允许增不允许减）。"""
    real = sum(len(s) for (_c, _i, _w, s) in _NAME_HOST_REVIEW.values() if _c == REAL_HIT)
    false = sum(len(s) for (_c, _i, _w, s) in _NAME_HOST_REVIEW.values() if _c == FALSE_HIT)
    assert real >= BASELINE_REAL_SITES, \
        "真命中站点从 %d 降到 %d ⇒ 有站点被误判成假命中" % (BASELINE_REAL_SITES, real)
    assert false >= BASELINE_FALSE_SITES, \
        "假命中站点从 %d 降到 %d ⇒ 有站点被误判成真命中" % (BASELINE_FALSE_SITES, false)
    assert real + false == BASELINE_SITES, \
        "真+假 = %d ≠ %d ⇒ 站点数对不上（★ 有站点没进任何一桶）" % (real + false, BASELINE_SITES)


# ── ⑤ 与 245 的 `_HOST_REVIEW["Name"]` 一致 ───────────────────────────
def test_consistent_with_245_host_review():
    """★★ 245 判 `Name` 是 `mixed`（历史结论）；★ 本表与它的口径必须一致。

    ★ 本判据是**跨规格一致性**守卫：245 的登记与本表若漂移（如 245 改成 real-hit），当场红。

    ★★★ **spec 292 改法（★ 因为 256）**：★ 245 的 `mixed` 是**当时的**结论 ——
      ★★ 它证据里那 4 处真命中（`sw_drawing_query.py` ×2 · `sw_drawing_view.py` · `sw_review.py`）
      **已被 spec 256 换成官方后继 `GetName2`** ⇒ ★ **`Name` 现在 0 真命中** ⇒ ★ 本表**全是假命中**。
      ★★ 所以判据从「245 的证据里**至少有一个**真命中」翻成「**一个都没有**」——
      ★★★ **这正是棘轮 4 → 0 的**内容断言****：★ 若有人**回退 256**，本判据**当场红** ✓
    """
    assert NAME in _HOST_REVIEW, "245 的 `_HOST_REVIEW` 里没有 `Name` ⇒ 本文件的依据来源断了"
    code, _why, sites_245 = _HOST_REVIEW[NAME]
    #: ★★★ **spec 292**：★ 245 的结论已从 `mixed` 改成 **`false-hit`** —— ★ 因为 **256** 把 4 处真命中
    #:   全换成了 `GetName2` ⇒ ★ 真树上**不再**有落在 `IView::Name` 上的调用（★ 见 245 该条目的依据）。
    assert code == _245_FALSE, \
        "245 把 `Name` 表态成 %r ⇒ 256 换路由后应为 `false-hit`（★ spec 292）" % code
    assert _245_MIXED in {"mixed"}, "245 的 `mixed` 常量口径漂了"

    #: ★ 口径按**文件**（★ spec 292 · 铁律 7：不按行号）
    all_files, real_files = set(), set()
    for _h, (c, _i, _w, s) in _NAME_HOST_REVIEW.items():
        all_files |= set(s)
        if c == REAL_HIT:
            real_files |= set(s)

    # ★ ① 245 的证据文件必须落在本表的某个宿主下 **或** 落在「**已被 256 换掉**」的那 3 个文件里。
    #: ★★ **为什么允许后者**：★ 256 把 `IView::Name` 换成了 `GetName2` ⇒ 那 3 个文件里**不再有** `Name`
    #:   ⇒ ★ 它们**合法地**从本表消失（★ 见墓碑）⇒ ★ 不算「口径漂了」。
    orphan = sorted({f for (f, _h) in sites_245
                     if f not in all_files and f not in SUPERSEDED_BY_256})
    assert not orphan, "245 登记的 `Name` 证据文件 %s 不在本表任何宿主下（且不属 256 已换集）" % orphan
    # ★★ ② **256 之后 `Name` 已 0 真命中** ⇒ 245 证据里**不得**再有真命中
    n_real = sum(1 for (f, _h) in sites_245 if f in real_files)
    assert n_real == 0, (
        "★ 245 的证据里还有 %d 处落在**真命中**里 ⇒ 要么 256 的换路由被回退了，"
        "要么下界 4 → 0 不成立：%s" % (n_real, sites_245))
    assert _245_REAL in {REAL_HIT}, "245 的常量口径漂了"
    assert _245_FALSE in {FALSE_HIT}, "245 的常量口径漂了"


# ── ⑥ 口径守卫：与 `_scan_calls` 逐条一致 ─────────────────────────────
def test_scan_parity_with_interlock():
    """★ 口径漂移守卫：★ 若 `_scan_calls` 将来多认一种形态，本文件必须同步（否则红）。"""
    if not (SCRIPTS / "sw_pdm.py").exists():
        pytest.skip("scripts/ 不在本机 ⇒ 无数据源（★ 缺数据源 ≠ 检查失败）")
    for fname, tree in _scan_all_modules():
        text = (SCRIPTS / fname).read_text(encoding="utf-8")
        mine = sorted((ln, m) for ln, m, _h in _member_calls(tree, text))
        theirs = sorted(_scan_calls(tree))
        assert mine == theirs, \
            "%s 的调用口径与 `_scan_calls` 不一致：本文件多 %s / 对方多 %s" \
            % (fname, [x for x in mine if x not in theirs][:5],
               [x for x in theirs if x not in mine][:5])
