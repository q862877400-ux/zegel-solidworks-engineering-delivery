"""★ spec 245：多后继「命中名」的**宿主级**复核（244 的 14 有一半是别的接口的同名成员）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/202-user-coverage-gaps/recon/official-obsolete-index.json（官方索引）
#         scripts/sw_*.py（真树调用点）· C:/swapi/types/*/<成员>.md（官方页原文）
#         tests/test_deprecated_entry_interlock.py（调用口径**真源**）
#         tests/test_obsolete_multi_successor.py（244 的 `_KNOWN_WRONG` 登记表）
# 定位:   244 按**裸成员名**量出「真树命中的多后继条目名 = 14」；
#         ★ 本文件把口径提到**宿主级** —— 只有**宿主接口 == 废弃条目所在接口**才算**真命中**，
#         ★ 宿主是**另一个接口的同名成员**（如 `ISketch::GetArcs2`、`ISketchManager::SketchTrim`）
#         就是**假命中**（★ 那是"我们调的是非废弃的那一个"）。
# 官方依据: C:/swapi/types/ISketch/GetArcs2.md（首行非 Obsolete）
#           vs C:/swapi/types/IView/GetArcs2.md（首行 `Obsolete. Superseded by …`）
#           C:/swapi/types/ISketchManager/SketchTrim.md（非废弃）
#           vs C:/swapi/types/IModelDoc2/SketchTrim.md（Obsolete）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读索引 / 官方页 / 真树源码；★ 不改 `tools/build_obsolete_index.py`、不改 `sw_com_traps`
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.test_deprecated_entry_interlock import _scan_all_modules, _scan_calls  # noqa: E402
from tests.test_obsolete_multi_successor import _KNOWN_WRONG, _multi  # noqa: E402

#: ★ 官方类型页根（★ 与 `test_deprecated_table_admission.SWAPI_TYPES` 同口径）。
SWAPI_TYPES = Path("C:/swapi/types")

#: ★★ 调用口径 —— ★ **逐字**同 `test_deprecated_entry_interlock._WRAPPERS`（判据 6 会自证一致）。
_WRAPPERS = ("get_com_member", "call_com_member", "call_assembly_doc")

REAL_HIT = "real-hit"          # 宿主接口 == 废弃条目所在接口 ⇒ 我们**确实在调**废弃成员
FALSE_HIT = "false-hit"        # 宿主是**别的接口**的同名（非废弃）成员 ⇒ 索引那条**与我们无关**
MIXED = "mixed"                # 同名成员在多个宿主上都有 ⇒ 部分站点真命中、部分假命中
CODES = {REAL_HIT, FALSE_HIT, MIXED}

#: ★★★ **宿主级复核登记表**（★ 键 = 命中名；值 = (code, 依据, 证据站点)）。
#: ★ 证据站点 = `(文件, 宿主表达式源码)` —— ★ **必须与重算结果对上**（判据 4）。
#: ★★★ **spec 292**：★ 证据里的**行号去掉**了（★ 铁律 7：行号会漂）⇒ ★ 实测 40 个切片里破了 4 次。
#: ★★ 这张表**不是豁免**：`real-hit` 说的是「我们真的在调废弃成员」（★ 由别的门禁管），
#:    `false-hit` 说的是「244 的 14 里这一条是别的接口的同名成员」。
_HOST_REVIEW: dict[str, tuple[str, str, tuple[tuple[str, str], ...]]] = {
    "DeleteRenderMaterial": (
        REAL_HIT,
        "宿主 `extension` = `model.Extension` ⇒ IModelDocExtension，★ 与条目接口**同**"
        "⇒ 我们确实在调废弃成员；索引后继 DeleteDisplayStateSpecificRenderMaterial 正确。",
        (("sw_render_material.py", "extension"),),
    ),
    "FeatureLinearPattern5": (
        REAL_HIT,
        "宿主 = `FeatureManager`（两种写法：`model.FeatureManager` / `get_com_member(model, "
        "\"FeatureManager\")`）⇒ 与条目接口 IFeatureManager **同**；索引后继 CreateFeature 正确。",
        (("sw_part.py", "model.FeatureManager"),
         ("sw_part.py", 'get_com_member(model, "FeatureManager")')),
    ),
    "FeatureLocalCurveDrivenPattern": (
        REAL_HIT,
        "宿主 `fm` = `get_com_member(model, \"FeatureManager\")`（同函数上一行）⇒ IFeatureManager；"
        "索引后继 CreateFeature 正确。",
        (("sw_pattern.py", "fm"),),
    ),
    "GetArcs2": (
        FALSE_HIT,
        "宿主 `sketch` 是 **ISketch**（模块内 `get_arcs(sketch)`，草图实体读取）"
        "⇒ 调的是 `ISketch::GetArcs2`（★ 非废弃），★ 不是被废弃的 `IView::GetArcs2`。",
        (("sw_sketch.py", "sketch"),),
    ),
    "GetEllipses3": (
        FALSE_HIT,
        "同上：宿主 `sketch` = ISketch ⇒ 调 `ISketch::GetEllipses3`（非废弃），"
        "★ 不是 `IView::GetEllipses3`。",
        (("sw_sketch.py", "sketch"),),
    ),
    "GetLines2": (
        FALSE_HIT,
        "同上：宿主 `sketch` = ISketch ⇒ 调 `ISketch::GetLines2(swCrossHatchFilter_e)`（非废弃），"
        "★ 不是 `IView::GetLines2`。",
        (("sw_sketch.py", "sketch"),),
    ),
    "GetMassProperties": (
        FALSE_HIT,
        "宿主 `extension` = `get_extension(model)` ⇒ **IModelDocExtension**，"
        "★ 而条目接口是 `IModelDoc2` ⇒ 我们调的正是**后继**本身（`IModelDocExtension::"
        "GetMassProperties`），★ 没有踩废弃入口。",
        (("sw_export.py", "extension"),),
    ),
    "GetPolylines": (
        FALSE_HIT,
        "同上：宿主 `sketch` = ISketch ⇒ 调 `ISketch::GetPolylines`（非废弃），"
        "★ 不是 `IView::GetPolylines`。",
        (("sw_sketch.py", "sketch"),),
    ),
    "GetSplines": (
        FALSE_HIT,
        "同上：宿主 `sketch` = ISketch ⇒ 调 `ISketch::GetSplines`（非废弃），"
        "★ 不是 `IView::GetSplines` / `ISketchBlockDefinition::GetSplines`。",
        (("sw_sketch.py", "sketch"),),
    ),
    "InsertFormToolFeature": (
        REAL_HIT,
        "宿主 `_mgr` = `get_com_member(model, \"FeatureManager\")`（同函数上一行）⇒ IFeatureManager；"
        "索引后继 CreateDefinition 正确。",
        (("sw_sheet_metal.py", "_mgr"),),
    ),
    "KFactor": (
        FALSE_HIT,
        "★★★ **spec 292 把本条的结论从 `real-hit` 改成 `false-hit`** —— ★ 因为 **spec 261 换路由**："
        "`sw_sheet_metal.py` 的 `_read_k_factor` 原先读 `get_com_member(feature, \"GetDefinition\")`"
        "（⇒ `IBendsFeatureData`，★ 那是**废弃**的 `IBendsFeatureData::KFactor`）⇒ ★ 已换成官方后继 "
        "`GetCustomBendAllowance()`（★ 宿主变量随之改名 `definition` → `cba`）⇒ ★ 真树上**不再**有落在"
        " `IBendsFeatureData::KFactor` 上的调用 ⇒ ★ 本条现在是**别的接口的同名成员**"
        "（`ICustomBendAllowance::KFactor`，★ 官方页「Gets or sets the K-factor.」**不带** Obsolete）。",
        (("sw_sheet_metal.py", "cba"),),
    ),
    #: ★★★ **墓碑（spec 292）**：这里原有 `"MaterialIdName"`（`IModelDoc2` · 真命中 · `sw_simulation.py`）
    #:   ⇒ ★★ **spec 261 已把它换成官方后继 `IPartDoc::GetMaterialPropertyName2`**（★ 真机实测）
    #:   ⇒ ★ 真树上**不再有** `MaterialIdName` 的调用 ⇒ ★ 条目按纪律**删掉**（★ 留着 = 空口表态）。
    #:   ★★ **内容断言**：`test_name_and_material_lines_are_closed` 按**名字**钉住两处后继。
    "Name": (
        FALSE_HIT,
        "★★★ **spec 292 把本条的结论从 `mixed` 改成 `false-hit`** —— ★ 因为 **spec 256 换路由**："
        "★ 原先的**真命中 4 处**（宿主 `view`（IView，`sw_drawing_query.py` ×2 + `sw_drawing_view.py`）"
        "+ 宿主 `av`（`model.ActiveView` ⇒ IView，`sw_review.py`））**已全部换成官方后继 `GetName2`** "
        "⇒ ★ 真树上**不再**有落在 `IView::Name` 上的调用 ⇒ ★ 剩下的 47 处**全是别的接口的同名成员**"
        "（`feature`/`feat`/`f`/`obj`（IFeature）、`x`/`body`（IBody2）、`study`（CWStudy）、"
        "`configuration`/`active`/`cfg`（IConfiguration）、`entry`、`property_object`、"
        "`sk`（ISketch）、`table`（ISwDMTable6）—— ★ 那些 `Name` 页**非废弃**）"
        "⇒ ★★ **本名已收口**（★ 逐站点明细见 `tests/test_obsolete_name_host_adjudication.py`）。",
        (("sw_boolean_ops.py", "feat"),),
    ),
    "SketchTrim": (
        FALSE_HIT,
        "★★★ **244 曾把它当成「唯一落在错后继里的真靶子」—— 那是错的**：宿主是 "
        "`get_com_member(model, \"SketchManager\")` ⇒ **ISketchManager**，"
        "★ 我们调的是 `ISketchManager::SketchTrim`（★ **非废弃**、正是索引该给的那个）"
        "⇒ ★ 索引取错（SketchExtend）**在真树上零影响**。",
        (("sw_sketch_edit_ops.py",           '_sketch(model) and get_com_member(model, "SketchManager")'),),
    ),
}


def _member_calls(tree: ast.AST, text: str):
    """★ 逐条 yield `(行号, 成员名, 宿主表达式源码)` —— ★ 两种形态**都收**（口径同 `_scan_calls`）。

    ★ 与 `_scan_calls` 的唯一差别是**多带一个宿主表达式**（判据 6 自证两者逐条一致）。
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            host = ast.get_source_segment(text, func.value) or ""
            yield getattr(node, "lineno", 0), func.attr, host
        elif isinstance(func, ast.Name) and func.id in _WRAPPERS:
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                host = ast.get_source_segment(text, node.args[0]) or ""
                yield getattr(node, "lineno", 0), node.args[1].value, host


def _hit_sites() -> dict[str, set[tuple[str, int, str]]]:
    """★ 真树命中名 → 站点集合（★ 只收**多后继条目**的成员名；★ 排除 `sw_api_*.py`）。"""
    names = {e["member"] for e in _multi()}
    out: dict[str, set[tuple[str, int, str]]] = {}
    for fname, tree in _scan_all_modules():
        text = (SCRIPTS / fname).read_text(encoding="utf-8")
        for ln, member, host in _member_calls(tree, text):
            if member in names:
                out.setdefault(member, set()).add((fname, ln, host))
    return out


def _first_body_line(path: Path) -> str:
    """★ 页首行 —— ★ 口径同 `tools/build_obsolete_index.py`（标题之后、`## ` 之前首个非头部行）。"""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            for nxt in lines[i + 1:]:
                if nxt.startswith("## "):
                    return ""
                if nxt.strip():
                    return nxt.strip()
            return ""
    return ""


def _names_with_live_same_name_page(names: set[str]) -> set[str]:
    """★ 机械信号：该成员名在**别的接口**下存在**非废弃**页 ⇒ 必须人工表态。"""
    live: set[str] = set()
    for nm in names:
        for p in SWAPI_TYPES.glob("*/%s.md" % nm):
            body = _first_body_line(p)
            if body and not body.startswith("Obsolete."):
                live.add(nm)
                break
    return live


# ── ① 覆盖：每个命中名都要表态 ────────────────────────────────────────
def test_every_hit_name_is_reviewed():
    """★★ 命中名集合（重算）必须**全部**在登记表里 —— ★ 少一个即红。

    ★★★ **spec 292**：★ 下界 14 → **13** —— ★ `MaterialIdName` 已被 **261** 换掉 ⇒ 离开命中集
      （★ 内容断言见 `test_name_and_material_lines_are_closed`）。
    """
    hits = set(_hit_sites())
    assert len(hits) >= 13, "命中名从 13 降到 %d ⇒ 读取器可能漏了" % len(hits)
    missing = sorted(hits - set(_HOST_REVIEW))
    assert not missing, "以下命中名未表态（★ 必须逐条写明是 real-hit 还是别的接口的同名成员）：\n%s" \
        % "\n".join("  " + m for m in missing)


# ── ② 机械信号：有非废弃同名页的名必须表态 ────────────────────────────
def test_live_same_name_pages_are_adjudicated():
    """★ 「同名成员在别的接口下**非废弃**」⇒ 该名**必须**人工表态（★ 下界 11，只增不减）。

    ★ 这正是 `SketchTrim` 被 244 误判的根因：`ISketchManager::SketchTrim` 存在且非废弃。
    """
    if not SWAPI_TYPES.exists():
        pytest.skip("C:/swapi/types 不在本机 ⇒ 本判据无数据源（★ 缺数据源 ≠ 检查失败）")
    hits = set(_hit_sites())
    live = _names_with_live_same_name_page(hits)
    #: ★★ **spec 292**：★ 下界 11 → **10** —— ★ `MaterialIdName`（已被 261 换掉）也属这一类。
    assert len(live) >= 10, "有非废弃同名页的名从 10 降到 %d ⇒ 探测器漏了" % len(live)
    missing = sorted(live - set(_HOST_REVIEW))
    assert not missing, "以下名有**非废弃的同名页**却未表态：\n%s" % "\n".join("  " + m for m in missing)


# ── ②b ★★★ **内容断言**：`Name` / `MaterialIdName` 两条线已收口 ────────
def test_name_and_material_lines_are_closed():
    """★★★ **棘轮下调的内容断言**（★ 铁律 22）：★ 下界 14→13 与 11→10 **必须能被证明**。

    ★★ 证据两条（★ 都**按名字**定位 —— 铁律 7）：
    · `Name` —— ★ **spec 256** 把 4 处真命中换成 `IView::GetName2` ⇒ ★ 本条从 `mixed` 变 **`false-hit`**；
    · `MaterialIdName` —— ★ **spec 261** 换成 `IPartDoc::GetMaterialPropertyName2` ⇒ ★ 条目**已删**。
    """
    assert _HOST_REVIEW["Name"][0] == FALSE_HIT, \
        "★ `Name` 又变回 %r ⇒ 要么 256 被回退，要么下界下调不成立" % _HOST_REVIEW["Name"][0]
    assert "MaterialIdName" not in _HOST_REVIEW, "★ `MaterialIdName` 条目没删干净 ⇒ 空口表态"
    for fname, token in (("sw_drawing_query.py", "GetName2"),
                         ("sw_drawing_view.py", "GetName2"),
                         ("sw_review.py", "GetName2"),
                         ("sw_simulation.py", "GetMaterialPropertyName2")):
        src = (SCRIPTS / fname).read_text(encoding="utf-8", errors="replace")
        assert token in src, "★ `%s` 里没有后继 `%s` ⇒ 换路由证据不成立" % (fname, token)


# ── ③ 封闭词表 ────────────────────────────────────────────────────────
def test_review_codes_are_closed_vocabulary():
    """★ 表态码必须落在封闭词表里（★ 认不出即红 —— ★ 不许写"待定/unknown"糊过去）。"""
    bad = sorted(n for n, (code, _w, _e) in _HOST_REVIEW.items() if code not in CODES)
    assert not bad, "以下条目的 code 不在封闭词表 %s 里：%s" % (sorted(CODES), bad)


# ── ④ 证据必须与重算站点逐字对上 ──────────────────────────────────────
def test_evidence_sites_match_recomputed_sites():
    """★★ 证据站点必须是**重算站点集合的子集**（★ 改了调用点 ⇒ 本判据红）。

    ★★ **检查量下界**：★ 登记表为空时"逐条比对"会**一条都不比** ⇒ 那是**空判据**
    （事实 46：检查量为 0 判失败）⇒ ★ 先钉住**检查量**（表条数 + 证据站点数）。
    """
    hits = _hit_sites()
    checked_sites = sum(len(s) for (_c, _w, s) in _HOST_REVIEW.values())
    assert len(_HOST_REVIEW) >= 13, "登记表只剩 %d 条 ⇒ 检查量不足" % len(_HOST_REVIEW)
    assert checked_sites >= 14, "证据站点只剩 %d 个 ⇒ 检查量不足" % checked_sites
    bad = []
    for name, (_code, _why, sites) in _HOST_REVIEW.items():
        assert sites, "%s 的证据站点为空（★ 不许空口表态）" % name
        for (fname, host) in sites:
            if (fname, host) not in {(f, h) for (f, _ln, h) in hits.get(name, set())}:
                bad.append("%s 的证据 %s 宿主=%r 不在重算站点里" % (name, fname, host))
    assert not bad, "证据与重算站点不符：\n" + "\n".join("  " + b for b in bad)


# ── ⑤ 下界：真命中 / 假命中各自不许减少 ───────────────────────────────
def test_real_and_false_hit_lower_bounds():
    """★ 真命中（real-hit + mixed）与假命中各自的下界（★ 只允许增不允许减）。

    ★★★ **2026-10-10（spec 292）两处下调 —— ★ 写了「为什么是正当减少」**：
      · `real` **7 → 4** · `false` **7 → 9**
      ★★ **真因（三条，都是后续切片**真的**换了路由）**：
      ① `MaterialIdName` —— ★ **261** 换成 `IPartDoc::GetMaterialPropertyName2` ⇒ ★ 条目**删掉**；
      ② `KFactor` —— ★ **261** 换成 `ICustomBendAllowance` ⇒ ★ 宿主不再是 `IBendsFeatureData` ⇒ **假命中**；
      ③ `Name` —— ★ **256** 换成 `IView::GetName2` ⇒ ★ 从 `mixed` 变 **`false-hit`**。
      ★★ **内容断言**（★ 铁律 22）：`test_name_and_material_lines_are_closed` 按**名字**钉住 ①②③。
    """
    codes = [c for (c, _w, _e) in _HOST_REVIEW.values()]
    real = codes.count(REAL_HIT) + codes.count(MIXED)
    false = codes.count(FALSE_HIT)
    assert real >= 4, "真命中从 4 降到 %d ⇒ 有条目被误判成假命中" % real
    assert false >= 9, "假命中从 9 降到 %d ⇒ 有条目被误判成真命中" % false
    assert real + false == len(_HOST_REVIEW), "每条必须表态成 real-hit / false-hit / mixed"


# ── ⑥ ★★ 核心：真命中里没有一条落在「索引取错」的后继上 ────────────────
def test_no_real_hit_falls_in_a_known_wrong_successor():
    """★★★ 244 的 6 条「索引取错」里，**落在真命中上的必须为 0** —— ★ 这就是待办 1 的关闭依据。

    ★ 能红的判据：★ 把 `SketchTrim` 改成 `real-hit` ⇒ 本判据当场红
      （★ 244 正是那么判的，★ 而实测证明它是 `ISketchManager::SketchTrim`）。
    """
    wrong_members = {m for (_iface, m) in _KNOWN_WRONG}
    offenders = sorted(n for n, (code, _w, _e) in _HOST_REVIEW.items()
                       if code in (REAL_HIT, MIXED) and n in wrong_members)
    assert not offenders, (
        "以下名被索引**取错**了后继、**且**我们真在调它 ⇒ 待办 1 有靶子，不能关闭：%s"
        % offenders)


# ── ⑦ 口径守卫：本文件的宿主抽取必须与 `_scan_calls` 逐条一致 ─────────
def test_scan_parity_with_interlock():
    """★ 口径漂移守卫：★ 若 `_scan_calls` 将来多认一种形态，本文件必须同步（否则红）。"""
    for fname, tree in _scan_all_modules():
        text = (SCRIPTS / fname).read_text(encoding="utf-8")
        mine = sorted((ln, m) for ln, m, _h in _member_calls(tree, text))
        theirs = sorted(_scan_calls(tree))
        assert mine == theirs, (
            "%s 的调用口径与 `test_deprecated_entry_interlock._scan_calls` 不一致：\n"
            "  本文件多出 %s\n  对方多出 %s"
            % (fname, [x for x in mine if x not in theirs][:5],
               [x for x in theirs if x not in mine][:5]))
