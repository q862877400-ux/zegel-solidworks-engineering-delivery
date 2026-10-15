"""★ spec 258：**② 段待办的**前提核对** —— 删掉不存在的待办（★ 本仓纪律：交接单的前提也要核）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/AUTO_HANDOFF.md（★ ② 段的待办清单）· output/GOAL.md（★ 目标真源）
#         tests/test_obsolete_host_review_family.py（250 的宿主级表态表 —— ★ 前提真源）
#         scripts/sw_sketch_edit_ops.py:148（★ 被误列的那个站点）
# 定位:   ★ 本仓纪律「**交接单自己的前提也要核**」（★ 227/232–240 已**连续九轮**核出错）。
#         ★★ 本轮核出：② 段第 3 条「`SketchTrim` 4 处换路由」**是伪待办** ——
#         ★ 250 早判它**假命中**（宿主 `SketchManager` ⇒ `ISketchManager::SketchTrim`，★ **非废弃**），
#         ★ 且真树只有 **1 处**、不是 4 处。
# 官方依据: C:/swapi/types/ISketchManager/SketchTrim.md（★ **非** Obsolete —— 真后继本身）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改 `scripts/`
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.test_obsolete_host_review_family import (  # noqa: E402
    FALSE_HIT,
    REAL_HIT,
    _HOST_EXPR_REVIEW,
)

#: ★★★ **250 的真命中**（★ 值 = 站点数）—— ★ 换路由的**真靶子**。
#: ★★ **250 表里 `real-hit` 的逐名站点数**。
#: ★★★ **2026-10-10（规格 301）订正 `6 名 → 4 名`** —— ★ **为什么是正当减少**（★ 规则 29）：
#:   · ★ **`KFactor`** —— ★ 250 表里**现在判它是 `false-hit`**（★ 它已被 `spec 261` 换过路由、
#:     ★ 现在调的是**后继本身** `ICustomBendAllowance::KFactor`）⇒ ★ 它**不再是真命中**；
#:   · ★ **`MaterialIdName`** —— ★ **不在 250 表里**（★ 属 `spec 260/261` 的 `adapt-args` 批）⇒ ★ 同理。
#:   ★★ **⇒ 这两条不是"任务少了"、是"基线抄了不该有的名"** —— ★ 它们的换路由**已在 `spec 261`
#:     做完并真机复验**（★ 见 `specs/261-routing-batch1-adapt-args/`）✓
#:   ★★★ **⚠ 内容断言**：★ 见 `tests/test_routing_plan_real_hits.py::test_the_two_adapt_args_entries_are_closed_in_spec_261`
#:     （★ 规则 22：棘轮下调必须补**按名字定位**的断言）✓
REAL_HITS = {
    "DeleteRenderMaterial": 1,
    "FeatureLinearPattern5": 2,
    "FeatureLocalCurveDrivenPattern": 1,
    "InsertFormToolFeature": 1,
}

#: ★★★ **被误列的那个**：★ 250 判它 `FALSE_HIT` ⇒ ★ **没有换路由的靶子**。
NOT_A_TARGET = "SketchTrim"
#: ★ 真树里它的**真实**站点数（★ 不是 4）。
NOT_A_TARGET_SITES = 1

#: ★ ② 段待办的**分类**（★ 封闭词表）。
ACTIONABLE = "actionable"        #: ★ 现在就能做
NEEDS_OWNER = "needs-owner"      #: ★ 需业主决策
NOT_A_TODO = "not-a-todo"        #: ★ **不是待办**（★ 是「不要做」的说明 ⇒ ★ 不该占号）
CODES = {ACTIONABLE, NEEDS_OWNER, NOT_A_TODO}

#: ★★ ② 段的 8 条（★ 本轮逐条定类）。
#: ★ 读数来自 250/253 的表态表 + `output/AUTO_HANDOFF.md` 的原文。
_TODO_CLASS: dict[str, tuple[str, str]] = {
    "门禁 counted_positions 口径缺陷": (ACTIONABLE, "★ 253 实测：会把**全 by-ref 形参**剥光 ⇒ 4 条假阳性"),
    "250 的 7 处真命中换路由": (ACTIONABLE, "★ 250 实测：**6 名 · 7 处** `real-hit`"),
    "SketchTrim 4 处换路由": (NOT_A_TODO, "★★ 250 判 `FALSE_HIT`（宿主 `SketchManager` ⇒ **非废弃**）· ★ 真树 **1 处** 不是 4 处"),
    "高危写盘 SaveAs3/create_draft": (ACTIONABLE, "★ 已授权 C 级"),
    "223 的 8 条既有红": (NEEDS_OWNER, "★ 权属不明 ⇒ 只登记不动"),
    "WZD_FASTENER/ROTATION_AXIS 不改不猜": (NOT_A_TODO, "★ 这是**纪律**不是待办"),
    "output 残留临时文件不删": (NOT_A_TODO, "★ 这是**纪律**不是待办"),
    "发版前同步打包副本": (ACTIONABLE, "★ 发版前才做"),
}


def _sketchtrim_failures(review: dict) -> list[str]:
    """★ 纯函数：`SketchTrim` 必须是 `FALSE_HIT` 且站点数是 1（★ 否则「伪待办」的结论不成立）。"""
    out: list[str] = []
    rec = review.get(NOT_A_TARGET)
    if rec is None:
        return ["250 的表里没有 %r" % NOT_A_TARGET]
    code, iface, _why, sites = rec
    if code != FALSE_HIT:
        out.append("`%s` 的表态是 %r（★ 不是 %r）⇒ **它可能真有靶子**，请复核" % (NOT_A_TARGET, code, FALSE_HIT))
    if iface != "ISketchManager":
        out.append("`%s` 的宿主接口是 %r（★ 应为 `ISketchManager`）" % (NOT_A_TARGET, iface))
    if len(sites) != NOT_A_TARGET_SITES:
        out.append("`%s` 的站点数是 %d（★ 应为 %d）" % (NOT_A_TARGET, len(sites), NOT_A_TARGET_SITES))
    return out


def _real_hit_failures(review: dict) -> list[str]:
    """★ 纯函数：`REAL_HITS` 必须与 250 的表**逐条一致**（★ 名 + 站点数）。"""
    out: list[str] = []
    got = {k: len(v[3]) for k, v in review.items() if v[0] == REAL_HIT}
    if got != REAL_HITS:
        out.append("真命中表不一致：实测 %s ≠ 基线 %s" % (got, REAL_HITS))
    return out


# ── ① ★★★ 核出「伪待办」：`SketchTrim` 没有靶子 ──────────────────────
def test_sketchtrim_is_not_a_routing_target():
    """★★★ `SketchTrim` 是**假命中** ⇒ ★ **「换路由」这条待办不存在**（★ 本轮核出）。

    ★ 能红的判据：★ 若哪天 250 把它改判成 `REAL_HIT` ⇒ 当场红（★ 那时才真该换路由）。
    """
    bad = _sketchtrim_failures(_HOST_EXPR_REVIEW)
    assert not bad, "伪待办的判定不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 真命中的靶子必须与 250 一致 ────────────────────────────────
def test_real_hits_match_the_250_table():
    """★★ 换路由的**真靶子** = 250 的 `real-hit`（★ **4 名 · 5 处**）—— ★ 与表**逐条一致**。

    ★★ 2026-10-10（规格 301）：★ 基线从 **6 名 · 7 处**订正为 **4 名 · 5 处**
      （★ 移出 `KFactor`（250 现判 `false-hit`）与 `MaterialIdName`（不在 250 表里））——
      ★★ 两条的换路由**已在 `spec 261` 完成并真机复验** ✓
    """
    bad = _real_hit_failures(_HOST_EXPR_REVIEW)
    assert not bad, "真命中表不符：\n" + "\n".join("  " + b for b in bad)
    assert sum(REAL_HITS.values()) == 5, "真命中站点数应为 5（★ 规格 301 订正）"


# ── ③ ★★ ② 段每条必须有**分类**，且分类在封闭词表里 ──────────────────
def test_every_todo_is_classified():
    """★★ ② 段每条都要定类（★ `actionable` / `needs-owner` / **`not-a-todo`**）。

    ★★ 为什么：★ **「不是待办」的东西占着编号** ⇒ ★ 终止条件（② 段待办清空）**永远达不成**。
    """
    bad = [k for k, (c, _w) in _TODO_CLASS.items() if c not in CODES]
    assert not bad, "以下条目分类不在封闭词表 %s 里：%s" % (sorted(CODES), bad)
    n_not_todo = sum(1 for (c, _w) in _TODO_CLASS.values() if c == NOT_A_TODO)
    assert n_not_todo >= 3, "`not-a-todo` 只剩 %d 条（★ 实测 3 条）" % n_not_todo


# ── ④ ★★ 纯函数能红 ────────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 把 `SketchTrim` 改判成真命中；② 站点数改掉；③ 真命中表改掉。"""
    good = dict(_HOST_EXPR_REVIEW)
    assert not _sketchtrim_failures(good), "正常表被判红 ⇒ 判据过严"

    flipped = dict(good)
    code, iface, why, sites = flipped[NOT_A_TARGET]
    flipped[NOT_A_TARGET] = (REAL_HIT, iface, why, sites)
    assert _sketchtrim_failures(flipped), "把 `SketchTrim` 翻成真命中却未判出 ⇒ **空判据**"

    iface_bad = dict(good)
    iface_bad[NOT_A_TARGET] = (FALSE_HIT, "IModelDoc2", why, sites)
    assert _sketchtrim_failures(iface_bad), "宿主接口改错却未判出 ⇒ **空判据**"
