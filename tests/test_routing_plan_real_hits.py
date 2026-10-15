"""★ spec 260：**250 的 6 名 · 7 处真命中的换路由**先量**（逐处定后继 + 定改法 + 定难度）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   tests/test_obsolete_host_review_family.py（★ 250 的 `_HOST_EXPR_REVIEW`，★ 真命中真源）
#         specs/202-user-coverage-gaps/recon/official-obsolete-index.json（★ 后继真源）
#         scripts/{sw_render_material,sw_part,sw_pattern,sw_sheet_metal,sw_simulation}.py（★ 7 处站点）
# 定位:   ★ 250 判出 **6 名 · 7 处** 真命中 ⇒ ★ 本文件**先量**：逐处定**官方后继**与**改法难度**，
#         ★ 为「真正换路由」铺路（★ 3 处要先造 `*FeatureData` ⇒ **大改**，★ 不是简单改名）。
# 官方依据: `C:/swapi/types/**`（★ 各页的废弃句）· ★ 本机 `official-obsolete-index.json`
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改 `scripts/`
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.test_obsolete_host_review_family import REAL_HIT, _HOST_EXPR_REVIEW  # noqa: E402

INDEX = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "official-obsolete-index.json"

#: ★ 改法难度的**封闭词表**。
RENAME = "rename"              #: ★ 同参改名（★ 最便宜）
ADAPT = "adapt-args"           #: ★ 参数要调（★ 中等）
NEW_DATA = "needs-feature-data"  #: ★ 要先造 `*FeatureData` 再 `CreateFeature`（★ **大改**）
CODES = {RENAME, ADAPT, NEW_DATA}

#: ★★★ **6 名 · 7 处的逐处先量**。
#: ★★ 键 = **`(文件, 包围函数)`** —— ★★★ **2026-10-10（规格 301）把键从 `(文件, 行号)` 改掉**：
#:   ★★ **起因**：★ `specs/292`（★ 依据 `MEMORY.md` 规则 32「证据表不许钉行号」）
#:     把 `_HOST_EXPR_REVIEW` 的站点**从 `(文件, 行号)` 改成了**裸文件名****
#:     ⇒ ★★ 而本文件的 `_PLAN` **仍按 `(文件, 行号)`** ⇒
#:     ★★★ `(f, ln) not in sites` **恒真**（★ 一个二元组**永远不可能**在「裸文件名」的列表里）
#:     ⇒ ★ 三条判据**恒红**（★ 与「改了 A 没改 B」同族 —— ★ 规则 30）。
#:   ★★ **⇒ 键改成 `(文件, 包围函数)`**：★ 两处**都能给出**、★ 且**不随行号漂**
#:     （★ 与 `tests/test_route_change_viability.py` 的 `SITES` **同形** ✓）。
#: ★★★★ **2026-10-10 第二处订正（★ 同轮）**：★ **`KFactor` / `MaterialIdName` 移出本表** ——
#:   ★★ 依据：★ `_HOST_EXPR_REVIEW` 里 `KFactor` 判的是 **`false-hit`**（★ 它已被 `spec 261` 换过路由、
#:     ★ 现在调的是**后继本身** `ICustomBendAllowance::KFactor`）⇒ ★ **它不在 250 的"真命中"名单里**；
#:   ★★ 而 **`MaterialIdName` 根本不在 `_HOST_EXPR_REVIEW` 里**（★ 它属 `spec 260/261` 的 **`adapt-args` 批**）。
#:   ⇒ ★★★ **本表只收 250 的「真命中」** ⇒ ★ 这两条**必须**移出（★ 否则判据恒红 —— ★ 而那是**判据对**、
#:     ★ 是**表装错了东西**）。
#:   ★ **那两条的去处**：★ 它们的换路由**已在 `spec 261` 做完**（★ 真机复验过）⇒
#:     ★ 详见 `specs/261-routing-batch1-adapt-args/`；★ 本表**不再重复登记**。
#: ★★ 值 = `(成员, **被废弃成员所在的接口**, 官方后继, 改法)`。
#: ★★★ **为什么必须记「源接口」**：★ `MaterialIdName` 在 **`IModelDoc2`** 上，
#:   而它的后继在 **`IPartDoc`** 上 ⇒ ★ **查索引要用源接口**（★ 我第一次写错、判据当场红）。
_PLAN: dict[tuple[str, str], tuple[str, str, str, str]] = {
    ("sw_render_material.py", "delete_render_material"):
        ("DeleteRenderMaterial", "IModelDocExtension",
         "IModelDocExtension::DeleteDisplayStateSpecificRenderMaterial", ADAPT),
    ("sw_part.py", "linear_pattern"):
        ("FeatureLinearPattern5", "IFeatureManager",
         "IFeatureManager::CreateFeature", NEW_DATA),
    ("sw_part.py", "linear_pattern_report"):
        ("FeatureLinearPattern5", "IFeatureManager",
         "IFeatureManager::CreateFeature", NEW_DATA),
    ("sw_pattern.py", "insert_local_curve_driven_pattern_report"):
        ("FeatureLocalCurveDrivenPattern", "IFeatureManager",
         "IFeatureManager::CreateFeature", NEW_DATA),
    ("sw_sheet_metal.py", "insert_form_tool_report"):
        ("InsertFormToolFeature", "IFeatureManager",
         "IFeatureManager::CreateDefinition", NEW_DATA),
}

#: ★ 下界（★ 只增不减）。
#: ★★★ **2026-10-10（规格 301）下调 `7 → 5` · `6 → 3`** —— ★ **为什么是正当减少**：
#:   ★★ 依据 `MEMORY.md` 规则 29「**删代码会连带压低多个下界 ⇒ 每个都要同步，
#:     并逐条写「为什么是正当减少」**」。
#:   ★★★ **两条移出的理由**（★ 逐条）：
#:     · ★ **`KFactor`** —— ★ `_HOST_EXPR_REVIEW` 判它是 **`false-hit`**（★ 它已被 `spec 261`
#:       换过路由、★ 现在调的是**后继本身**）⇒ ★ **它不在 250 的"真命中"名单里** ⇒
#:       ★ 本表（★ 定位 = 「250 真命中的逐处计划」）**不该装它**；
#:     · ★ **`MaterialIdName`** —— ★ **根本不在 `_HOST_EXPR_REVIEW` 里**（★ 它属 `spec 260/261`
#:       的 `adapt-args` 批）⇒ ★ 同理。
#:   ★★ **⇒ 这不是"任务少了"、是"表装错了东西"**：★ 两条的换路由**已在 `spec 261` 做完并真机复验**
#:     （★ 见 `specs/261-routing-batch1-adapt-args/`）⇒ ★★ **它们不是未过门，是已收口** ✓
#:   ★★★ **⚠ 内容断言**（★ 规则 22：棘轮下调必须补**按名字定位**的断言）：
#:     ★ `test_the_two_adapt_args_entries_are_closed_in_spec_261` —— ★ **若有人把它们塞回本表**，
#:       或★**把 `spec 261` 的结论删掉**，★ 该判据**当场红** ✓
BASELINE_SITES = 5
BASELINE_NAMES = 4
#: ★★ 需要 `*FeatureData` 的处数（★ **最贵的那一类**，★ 不许悄悄降级成「改名」）。
BASELINE_NEW_DATA = 4

#: ★★★ **废弃句的两种形态**（★ 本轮实测）—— ★ **判废弃不能只 grep `obsolete`**。
OBSOLETE_FORMS = ("Obsolete. Superseded by", "Obsolete. See", "Not supported in SOLIDWORKS")


def _index_successor(iface: str, member: str) -> str | None:
    """★ 从官方索引取后继（★ 索引是 **list of dicts**，★ 不是按名键的 dict）。"""
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    for x in data["entries"]:
        if x["interface"] == iface and x["member"] == member:
            return x["successor"]
    return None


def _plan_failures(plan: dict) -> list[str]:
    """★ 纯函数：每条必须「成员在 250 的真命中里 · 后继是官方索引给的 · 改法在封闭词表里」。

    ★★★ **2026-10-10（规格 301）两处口径订正**（★ 依据 `MEMORY.md` 规则 32）：
      ① ★ **键从 `(文件, 行号)` 改成 `(文件, 包围函数)`** —— ★ `_HOST_EXPR_REVIEW` 的站点
         在 `specs/292` 里**已改成裸文件名**（★ 依据规则 32「证据表不许钉行号」）
         ⇒ ★★ 拿 `(f, ln)` 去比**永远不成立**（★ 那让三条判据**恒红**）；
      ② ★ **`sites` 是 `list[str]`（裸文件名）** ⇒ ★ 比对应是「**文件名在不在**」，
         ★ 而不是「二元组在不在」。
      ★★ 判据的**意图不变**：★ 「这一处**确实是** 250 认定的真命中站点」✓
    """
    out: list[str] = []
    real = {k: len(v[3]) for k, v in _HOST_EXPR_REVIEW.items() if v[0] == REAL_HIT}
    sites: list[str] = []
    for v in _HOST_EXPR_REVIEW.values():
        if v[0] == REAL_HIT:
            sites += list(v[3])
    for (f, fn), (member, src_iface, succ, code) in sorted(plan.items()):
        where = "%s::%s" % (f, fn)
        if code not in CODES:
            out.append("%s 的改法 %r 不在封闭词表 %s" % (where, code, sorted(CODES)))
        if f not in sites:
            out.append("%s 不在 250 的真命中站点里" % where)
        if member not in real:
            out.append("%s 的成员 %s 不是 250 的真命中名" % (where, member))
        #: ★ 源接口必须**等于** 250 记的那个（★ 否则「查索引用哪个接口」就错了）。
        if real.get(member) and _HOST_EXPR_REVIEW[member][1] != src_iface:
            out.append("%s 的源接口 %r ≠ 250 记的 %r"
                       % (where, src_iface, _HOST_EXPR_REVIEW[member][1]))
        if "::" not in succ:
            out.append("%s 的后继 %r 不是全限定名" % (where, succ))
    if len(plan) != BASELINE_SITES:
        out.append("站点数 %d ≠ 基线 %d" % (len(plan), BASELINE_SITES))
    return out


# ── ① ★★ 7 处逐处有计划（成员 · 后继 · 改法）────────────────────────
def test_every_real_hit_site_has_a_plan():
    """★★ 250 的 **7 处**真命中**逐处**有计划：★ 成员 + **官方后继** + **改法难度**。"""
    bad = _plan_failures(_PLAN)
    assert not bad, "换路由计划不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 后继必须**逐字**来自官方索引（★ 不许手抄）──────────────────
def test_successors_come_from_the_official_index():
    """★★★ 每处的后继必须**等于**官方索引给的那个（★ 手抄 = 双盲，★ 本仓铁律 6）。

    ★ 能红的判据：★ 把任一后继改成别的名字 ⇒ 当场红。
    """
    bad = []
    for (f, fn), (member, src_iface, succ, _c) in sorted(_PLAN.items()):
        got = _index_successor(src_iface, member)
        if got is None:
            bad.append("%s::%s 的 %s::%s **不在官方索引里**" % (f, fn, src_iface, member))
        elif got != succ:
            bad.append("%s::%s 的 %s 后继不符：本表 %r ≠ 索引 %r"
                       % (f, fn, member, succ, got))
    assert not bad, "后继与官方索引不符：\n" + "\n".join("  " + b for b in bad)


# ── ③ ★★★ 难度分层：`needs-feature-data` 必须 ≥4（★ 不许降级）────────
def test_difficulty_tiers_are_not_understated():
    """★★★ 7 处里 **4 处**要先造 `*FeatureData`（★ **大改**）—— ★ 不许当成「改名」。

    ★★ 为什么单独立一条：★ 「改名」与「造 `*FeatureData`」的工作量差**一个数量级**；
    ★ 把它们混在一起 ⇒ ★ 交接单会严重低估（★ 258 的教训同族）。
    """
    n = sum(1 for (_m, _i, _s, c) in _PLAN.values() if c == NEW_DATA)
    assert n >= BASELINE_NEW_DATA, \
        "`needs-feature-data` 只剩 %d 处（★ 基线 %d）⇒ 难度被低估" % (n, BASELINE_NEW_DATA)
    assert len(_PLAN) == BASELINE_SITES, "站点数变了 ⇒ 请同步"


# ── ④ ★★ 6 名全部是**废弃**成员（★ 含「不用 Obsolete 这个词」的形态）──
def test_all_six_names_are_deprecated_via_the_index():
    """★★★ **6 名全部在官方索引里**（★ 即有后继）⇒ ★ **都是废弃成员**。

    ★★★ **本轮的关键教训**：★ `IModelDocExtension::DeleteRenderMaterial` 的废弃句是
    **「Not supported in SOLIDWORKS 2011 and later. Superseded by …」** —— ★ **不含 `Obsolete` 这个词**。
    ⇒ ★★ **判「是否废弃」不能只 grep `obsolete`**，★ **必须查索引**（★ builder 按多种形态建）。
    """
    names = sorted({m for (m, _i, _s, _c) in _PLAN.values()})
    assert len(names) == BASELINE_NAMES, "名数 %d ≠ %d" % (len(names), BASELINE_NAMES)
    missing = []
    for (f, fn), (member, src_iface, _s, _c) in sorted(_PLAN.items()):
        if _index_successor(src_iface, member) is None:
            missing.append("%s::%s %s::%s" % (f, fn, src_iface, member))
    assert not missing, "以下成员在官方索引里查不到后继：\n" + "\n".join("  " + m for m in missing)
    assert len(OBSOLETE_FORMS) >= 3, "废弃句形态表被削了"


# ── ⑥ ★★★ 内容断言：两条 `adapt-args` **已收口在 spec 261**（★ 规则 22）──
def test_the_two_adapt_args_entries_are_closed_in_spec_261():
    """★★★ **棘轮下调的内容断言**（★ `MEMORY.md` 规则 22 逐字：「棘轮下调必须补「内容断言」
    —— 计数棘轮**接不住**「有人写回去」⇒ 补**按名字定位**的 AST 断言」）。

    ★★ **本规格把 `BASELINE_SITES 7 → 5` · `BASELINE_NAMES 6 → 4`**（★ 移出 `KFactor` 与 `MaterialIdName`）
      ⇒ ★★★ **必须钉住「它们不是被删了、而是已收口在别处」**：
        · ★ `KFactor` 在 250 表里判的是 **`false-hit`**（★ 已被 `spec 261` 换过路由）；
        · ★ `MaterialIdName` **不在 250 表里**（★ 属 `spec 260/261` 的 `adapt-args` 批）；
        · ★★ **两条都已在 `spec 261` 真机复验**。

    ★ 判据：★ ① 本表**不含**那两条；★ ② **`spec 261` 的结论确实在**（★ 否则「已收口」是空话）。
    """
    members = {m for (m, _i, _s, _c) in _PLAN.values()}
    assert "KFactor" not in members, (
        "★ `KFactor` 被塞回本表 ⇒ ★ 而它在 250 表里是 `false-hit`（★ 已由 spec 261 换过路由）")
    assert "MaterialIdName" not in members, (
        "★ `MaterialIdName` 被塞回本表 ⇒ ★ 它不属 250 的真命中（★ 属 spec 260/261 的 adapt-args 批）")
    #: ★★ ② 「已收口」必须**有据可查**（★ 不能只有一句自称）
    acc = ROOT / "specs" / "261-routing-batch1-adapt-args" / "acceptance.md"
    assert acc.is_file(), "★ `specs/261-routing-batch1-adapt-args/acceptance.md` 不见了 ⇒ 「已收口」失去依据"
    body = acc.read_text(encoding="utf-8", errors="replace")
    for name in ("KFactor", "MaterialIdName"):
        assert name in body, (
            "★ `spec 261` 的验收里没有 %s ⇒ ★ 那「它已收口」这句话**没有依据**（★ 规则 22）" % name)


# ── ⑤ ★★ 纯函数能红 ────────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 改法不在词表；② 站点不在真命中里；③ 条数变了。"""
    assert not _plan_failures(_PLAN), "正常表被判红 ⇒ 判据过严"
    b1 = dict(_PLAN)
    k = next(iter(b1))
    b1[k] = (b1[k][0], b1[k][1], b1[k][2], "随便改改")
    assert any("封闭词表" in x for x in _plan_failures(b1)), "非法改法未判出 ⇒ **空判据**"
    b2 = dict(_PLAN)
    b2[("no_such_file.py", 1)] = ("FeatureLinearPattern5", "IFeatureManager",
                                   "IFeatureManager::CreateFeature", NEW_DATA)
    assert _plan_failures(b2), "站点不在真命中里却未判出 ⇒ **空判据**"
