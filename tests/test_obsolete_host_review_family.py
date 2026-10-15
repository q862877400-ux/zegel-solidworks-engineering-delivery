"""★ spec 250：245 其余 **13 条**命中名的**宿主表达式级**表态（245 只给了名级结论 + 1~2 个证据站点）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   tests/test_obsolete_multi_successor_impact.py（245 的 `_hit_sites` / `_HOST_REVIEW`）
#         tests/test_obsolete_multi_successor.py（`_multi`：多后继条目的 `interface` / `member`）
#         tests/test_obsolete_name_host_adjudication.py（248 的 `_adjudication_failures` 形态 —— ★ 同法）
#         tests/test_deprecated_entry_interlock.py（`_scan_all_modules` / `_scan_calls`）
# 定位:   248 只把 `Name` 一个名做到了宿主表达式级；★ 本文件把**其余 13 个名**一次做完
#         ⇒ ★ 每个 (名, 宿主表达式) 都要表态，且 `real-hit` 必须与**该名的全部条目接口**自洽。
# 官方依据: C:/swapi/types/IModelDocExtension/DeleteRenderMaterial.md（Obsolete）
#           · IFeatureManager/FeatureLinearPattern5.md（Obsolete）· IView/GetArcs2.md（Obsolete）
#           · IModelDoc2/GetMassProperties.md（Obsolete）· ISldWorks/GetMassProperties.md（Obsolete）
#           · IBendsFeatureData/KFactor.md（Obsolete）· IModelDoc2/MaterialIdName.md（Obsolete）
#           · IModelDoc2/SketchTrim.md（Obsolete）· ISketchBlockDefinition/GetSplines.md（Obsolete）
#           · ISketchManager/SketchTrim.md（**非**废弃 —— 真后继）
#           · IModelDoc2/ActiveView.md Returns「Current active [[model view]]」⇒ IView
#           · IModelDoc2/Extension.md / FeatureManager.md / GetBodies2.md（返回类型）
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
from tests.test_obsolete_multi_successor import _multi  # noqa: E402
from tests.test_obsolete_multi_successor_impact import (  # noqa: E402
    FALSE_HIT as _245_FALSE,
    MIXED as _245_MIXED,
    REAL_HIT as _245_REAL,
    _HOST_REVIEW,
    _hit_sites,
    _member_calls,
)

REAL_HIT = "real-hit"
FALSE_HIT = "false-hit"
CODES = {REAL_HIT, FALSE_HIT}

#: ★ 248 已做掉的**跳过集**（★ 本文件只做其余 13 个）。
DONE_IN_248 = {"Name"}

#: ★★★ **逐 (名, 宿主表达式) 表态表**。
#: ★ 值 = (code, 宿主接口, 依据, 站点)；★ 站点必须与重算结果**逐字相等**。
_HOST_EXPR_REVIEW: dict[str, tuple[str, str, str, tuple[str, ...]]] = {
    "DeleteRenderMaterial": (
        REAL_HIT, "IModelDocExtension",
        "宿主 `extension` = `model.Extension` ⇒ **IModelDocExtension**，★ 与条目接口**同** ⇒ 真命中。",
        ("sw_render_material.py",),
    ),
    "FeatureLinearPattern5": (
        REAL_HIT, "IFeatureManager",
        "宿主两种写法都是 **IFeatureManager**（`model.FeatureManager` / "
        "`get_com_member(model, \"FeatureManager\")`），★ 与条目接口**同** ⇒ 真命中。",
        ("sw_part.py", "sw_part.py"),
    ),
    "FeatureLocalCurveDrivenPattern": (
        REAL_HIT, "IFeatureManager",
        "宿主 `fm` = `get_com_member(model, \"FeatureManager\")`（同函数上一行）⇒ **IFeatureManager** ⇒ 真命中。",
        ("sw_pattern.py",),
    ),
    "GetArcs2": (
        FALSE_HIT, "ISketch",
        "宿主 `sketch` 是**草图实体读取器的形参**（模块内 `_require(sketch)` + `GetArcs2`）⇒ **ISketch**；"
        "★ 条目接口是 `IView` ⇒ 假命中。",
        ("sw_sketch.py",),
    ),
    "GetEllipses3": (
        FALSE_HIT, "ISketch",
        "同上：宿主 `sketch` ⇒ **ISketch**（★ 条目是 `IView::GetEllipses3`）⇒ 假命中。",
        ("sw_sketch.py",),
    ),
    "GetLines2": (
        FALSE_HIT, "ISketch",
        "同上：宿主 `sketch` ⇒ **ISketch::GetLines2(swCrossHatchFilter_e)**（★ 条目是 `IView::GetLines2`）⇒ 假命中。",
        ("sw_sketch.py",),
    ),
    "GetMassProperties": (
        FALSE_HIT, "IModelDocExtension",
        "宿主 `extension` = `model.Extension` ⇒ **IModelDocExtension**，★ 而条目接口是 `IModelDoc2` / `ISldWorks` "
        "⇒ ★ 我们调的正是**后继**本身（`IModelDocExtension::GetMassProperties`）⇒ 假命中。",
        ("sw_export.py",),
    ),
    "GetPolylines": (
        FALSE_HIT, "ISketch",
        "同上：宿主 `sketch` ⇒ **ISketch**（★ 条目是 `IView::GetPolylines`）⇒ 假命中。",
        ("sw_sketch.py",),
    ),
    "GetSplines": (
        FALSE_HIT, "ISketch",
        "同上：宿主 `sketch` ⇒ **ISketch**；★ 条目是 `ISketchBlockDefinition` / `IView` ⇒ 假命中。",
        ("sw_sketch.py",),
    ),
    "InsertFormToolFeature": (
        REAL_HIT, "IFeatureManager",
        "宿主 `_mgr` = `get_com_member(model, \"FeatureManager\")`（同函数上一行）⇒ **IFeatureManager** ⇒ 真命中。",
        ("sw_sheet_metal.py",),
    ),
    "KFactor": (
        FALSE_HIT, "ICustomBendAllowance",
        "★★★ **spec 292 把本条的结论从 `real-hit` 改成 `false-hit`** —— ★ 因为 **spec 261 换路由**："
        "`sw_sheet_metal.py` 的 `_read_k_factor` 原先读 `get_com_member(feature, \"GetDefinition\")`"
        "（⇒ **IBendsFeatureData**，★ 那是**废弃**条目）⇒ ★ 已换成官方后继 `GetCustomBendAllowance()`"
        "（★ 宿主变量随之改名 `definition` → `cba`）⇒ ★ 现在读的是 **`ICustomBendAllowance`**，"
        "★ **不在**该名的三个条目接口（`IBendsFeatureData`/`IOneBendFeatureData`/`ISheetMetalFeatureData`）里"
        "⇒ ★ 本条现在是**别的接口的同名成员**（★ 官方页「Gets or sets the K-factor.」**不带** Obsolete）。",
        ("sw_sheet_metal.py",),
    ),
    #: ★★★ **墓碑（spec 292）**：这里原有 `"MaterialIdName"`（`IModelDoc2` · 真命中 · `sw_simulation.py`）
    #:   ⇒ ★★ **spec 261 已把它换成官方后继 `IPartDoc::GetMaterialPropertyName2`**（★ 真机实测）
    #:   ⇒ ★ 真树上**不再有** `MaterialIdName` 的调用 ⇒ ★ 条目按纪律**删掉**（★ 留着 = 空口表态）。
    #:   ★★ **内容断言**：`test_material_id_name_route_is_closed_by_261` 按**名字**钉住该后继。
    "SketchTrim": (
        FALSE_HIT, "ISketchManager",
        "★★ 宿主 = `get_com_member(model, \"SketchManager\")` ⇒ **ISketchManager**，"
        "★ 我们调的是 `ISketchManager::SketchTrim`（★ **非废弃**、正是索引**该给**的那个）"
        "⇒ ★ 条目 `IModelDoc2::SketchTrim` 与我们**无关** ⇒ 假命中。",
        ("sw_sketch_edit_ops.py",),
    ),
}

#: ★ 下界（★ 只允许增不允许减）。
#: ★★★ **2026-10-10（spec 292）三处下调 —— ★ 每处都写了「为什么是正当减少」**：
#:   · `BASELINE_NAMES` **13 → 12** · `BASELINE_SITES` **14 → 13** · `BASELINE_REAL_SITES` **7 → 5**
#:   ★★ **真因（两条，都是后续切片**真的**换了路由）**：
#:   ① **spec 261** 把 `IModelDoc2::MaterialIdName` 换成 `IPartDoc::GetMaterialPropertyName2`
#:      （★ `sw_simulation.py`，★ 真机实测）⇒ ★ 命中名 `MaterialIdName`（真命中 · 1 处）**消失** ⇒ 条目删；
#:   ② **spec 261** 也把 `KFactor` 的读点换成 `ICustomBendAllowance`
#:      （★ `sw_sheet_metal.py` 的 `_read_k_factor`，★ 宿主 `definition` → `cba`）⇒ ★ `KFactor` 变**假命中**。
#:   ★★ **内容断言**（★ 铁律 22）：`test_material_id_name_route_is_closed_by_261` 按**名字**钉住。
BASELINE_NAMES = 12
BASELINE_SITES = 13
BASELINE_REAL_SITES = 5
BASELINE_FALSE_SITES = 8


# ── ⑤ ★★★ **内容断言**：`MaterialIdName` 已被 spec 261 换成 `GetMaterialPropertyName2` ──
def test_material_id_name_route_is_closed_by_261():
    """★★★ **棘轮下调的内容断言**（★ 铁律 22）：★ 下界 13/14/7 → 12/13/6 **必须能被证明**。

    ★★ 证据 = `sw_simulation.py` 里 `MaterialIdName` 已被 **spec 261** 换成官方后继
    `IPartDoc::GetMaterialPropertyName2`。★ 判据**按名字定位**（★ 铁律 7）。
    """
    assert "MaterialIdName" not in _HOST_EXPR_REVIEW, "条目没删干净 ⇒ 空口表态"
    src = (SCRIPTS / "sw_simulation.py").read_text(encoding="utf-8", errors="replace")
    assert "GetMaterialPropertyName2" in src, \
        "★ `sw_simulation.py` 里没有官方后继 `GetMaterialPropertyName2` ⇒ 261 的换路由证据不成立"
    assert "spec 261" in src, "★ 换路由的**记档**不见了（★ 该函数头应写清为什么换）"


def _entry_ifaces() -> dict[str, set[str]]:
    """★ 每个命中名在**多后继条目**里的**全部**接口（★ 一名可跨多接口）。"""
    out: dict[str, set[str]] = {}
    for e in _multi():
        out.setdefault(e["member"], set()).add(e["interface"])
    return out


def _host_sites() -> dict[str, list[str]]:
    """★ 重算：名 → **站点所在文件的多重集**（★ 跳过 248 已做掉的）。

    ★★★ **spec 292 改成「按文件」** —— ★ 原先按 `(文件, 行号)` ⇒ ★★ 行号一漂全表红（★ 铁律 7）。
    """
    out: dict[str, list[str]] = {}
    for nm, sites in _hit_sites().items():
        if nm in DONE_IN_248:
            continue
        out[nm] = [f for (f, _ln, _h) in sites]
    return out


def _adjudication_failures(
    host_sites: dict[str, list[str]],
    table: dict[str, tuple[str, str, str, tuple[str, ...]]],
    entry_ifaces: dict[str, set[str]],
) -> list[str]:
    """★ 纯函数：问题清单（★ 空 = 通过）。查四样：覆盖 / 失效 / 自洽 / 站点**按文件多重集**相等。"""
    out: list[str] = []
    for nm in sorted(host_sites):
        if nm not in table:
            out.append("命中名 %r 未表态（真树上有 %d 处）" % (nm, len(host_sites[nm])))
    for nm in sorted(table):
        code, iface, _why, sites = table[nm]
        if code not in CODES:
            out.append("名 %r 的表态码 %r 不在封闭词表 %s 里" % (nm, code, sorted(CODES)))
            continue
        if nm not in host_sites:
            out.append("表里登记的 %r 在真树上**不存在** ⇒ 空口表态" % nm)
            continue
        ifaces = entry_ifaces.get(nm, set())
        if not ifaces:
            out.append("名 %r 不在多后继条目里 ⇒ 不该出现在本表" % nm)
            continue
        if (iface in ifaces) != (code == REAL_HIT):
            out.append("名 %r 表态 %r 但宿主接口 %s %s 该名的条目接口 %s ⇒ 表态与接口矛盾"
                       % (nm, code, iface, "∈" if iface in ifaces else "∉", sorted(ifaces)))
        if Counter(sites) != Counter(host_sites[nm]):
            out.append("名 %r 的证据文件与重算不符：表里多 %s / 表里少 %s"
                       % (nm, sorted((Counter(sites) - Counter(host_sites[nm])).elements()),
                          sorted((Counter(host_sites[nm]) - Counter(sites)).elements())))
    return out


# ── ① 覆盖 + 自洽 + 站点逐字 ──────────────────────────────────────────
def test_every_remaining_name_is_adjudicated():
    """★★ 12 个名、13 处站点**全部**表态；★ 表态与**该名的全部条目接口**自洽。

    ★★★ **spec 292**：★ 真命中 `MaterialIdName` 已被 **261** 换掉 ⇒ ★ 13 → **12** 名 · 14 → **13** 处。
    """
    hosts = _host_sites()
    total = sum(len(v) for v in hosts.values())
    assert len(hosts) >= BASELINE_NAMES, \
        "命中名从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_NAMES, len(hosts))
    assert total >= BASELINE_SITES, \
        "站点从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_SITES, total)
    bad = _adjudication_failures(hosts, _HOST_EXPR_REVIEW, _entry_ifaces())
    assert not bad, "宿主表达式级表态不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 判据**能红**（合成负例）─────────────────────────────────────
def test_criterion_is_red_able():
    """★★ 三组负例：① 冒出新名；② 表态与接口矛盾；③ 表里登记的名被删掉。"""
    hosts = _host_sites()
    ifaces = _entry_ifaces()

    synthetic = {k: set(v) for k, v in hosts.items()}
    synthetic["__bogus_name__"] = {"sw_probe_synthetic.py"}
    bad = _adjudication_failures(synthetic, _HOST_EXPR_REVIEW, ifaces)
    assert any("__bogus_name__" in b for b in bad), "合成名未被判出 ⇒ 空判据：%r" % bad

    flipped = dict(_HOST_EXPR_REVIEW)
    code, iface, why, sites = flipped["SketchTrim"]
    flipped["SketchTrim"] = (REAL_HIT, iface, why, sites)
    bad2 = _adjudication_failures(hosts, flipped, ifaces)
    assert any("矛盾" in b for b in bad2), "把 `SketchTrim` 翻成真命中却未被判出 ⇒ 空判据：%r" % bad2

    dropped = {k: v for k, v in _HOST_EXPR_REVIEW.items() if k != "KFactor"}
    bad3 = _adjudication_failures(hosts, dropped, ifaces)
    assert any("KFactor" in b for b in bad3), "删掉 `KFactor` 却未被判出 ⇒ 空判据：%r" % bad3


# ── ③ 封闭词表 ────────────────────────────────────────────────────────
def test_codes_are_closed_vocabulary():
    """★ 表态码必须落在封闭词表里。"""
    bad = sorted(n for n, (c, _i, _w, _s) in _HOST_EXPR_REVIEW.items() if c not in CODES)
    assert not bad, "以下名的 code 不在 %s 里：%s" % (sorted(CODES), bad)


# ── ④ 下界 ────────────────────────────────────────────────────────────
def test_lower_bounds():
    """★ 真命中站点 7 · 假命中站点 7（★ 只增不减）。"""
    real = sum(len(s) for (_c, _i, _w, s) in _HOST_EXPR_REVIEW.values() if _c == REAL_HIT)
    false = sum(len(s) for (_c, _i, _w, s) in _HOST_EXPR_REVIEW.values() if _c == FALSE_HIT)
    assert real >= BASELINE_REAL_SITES, "真命中站点从 %d 降到 %d" % (BASELINE_REAL_SITES, real)
    assert false >= BASELINE_FALSE_SITES, "假命中站点从 %d 降到 %d" % (BASELINE_FALSE_SITES, false)
    assert real + false == BASELINE_SITES, \
        "真+假 = %d ≠ %d ⇒ 站点数对不上" % (real + false, BASELINE_SITES)


# ── ⑤ ★★ 与 245 的**名级**表态跨规格一致 ─────────────────────────────
def test_consistent_with_245_name_level_verdict():
    """★★ 本表的**宿主级**结论必须与 245 的**名级**结论一致：

    ★ 有名级真命中 ⇒ 245 的 code ∈ {`real-hit`, `mixed`}；★ 全假 ⇒ 245 的 code == `false-hit`。
    ★ 本判据是**跨规格一致性**守卫 —— ★ 两表漂移当场红。
    """
    hosts = _host_sites()
    for nm, sites in sorted(hosts.items()):
        assert nm in _HOST_REVIEW, "245 的 `_HOST_REVIEW` 里没有 %r" % nm
        code_245 = _HOST_REVIEW[nm][0]
        has_real = _HOST_EXPR_REVIEW[nm][0] == REAL_HIT
        if has_real:
            assert code_245 in (_245_REAL, _245_MIXED), \
                "本表判 %r 有真命中，245 却写 %r ⇒ 两表漂移" % (nm, code_245)
        else:
            assert code_245 == _245_FALSE, \
                "本表判 %r 全假命中，245 却写 %r ⇒ 两表漂移" % (nm, code_245)
    assert _245_REAL in (REAL_HIT,) and _245_FALSE in (FALSE_HIT,), "245 的常量口径漂了"


# ── ⑥ 口径守卫 ────────────────────────────────────────────────────────
def test_scan_parity_with_interlock():
    """★ 口径漂移守卫：★ 若 `_scan_calls` 将来多认一种形态，本文件必须同步（否则红）。"""
    if not (SCRIPTS / "sw_sketch.py").exists():
        pytest.skip("scripts/ 不在本机 ⇒ 无数据源（★ 缺数据源 ≠ 检查失败）")
    for fname, tree in _scan_all_modules():
        text = (SCRIPTS / fname).read_text(encoding="utf-8")
        mine = sorted((ln, m) for ln, m, _h in _member_calls(tree, text))
        theirs = sorted(_scan_calls(tree))
        assert mine == theirs, \
            "%s 的调用口径与 `_scan_calls` 不一致：本文件多 %s / 对方多 %s" \
            % (fname, [x for x in mine if x not in theirs][:5],
               [x for x in theirs if x not in mine][:5])
