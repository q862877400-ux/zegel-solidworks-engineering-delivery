"""★ spec 254：`IView::Name`（废弃）⇒ `GetName2`（后继）的**真机等价性先量** + 4 处站点的换路由前提。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_drawing_query.py:194 / :264 · scripts/sw_drawing_view.py:436 · scripts/sw_review.py:637
#         （★ 248 判定的 **4 处 `IView::Name` 真命中**）· output/_probe254_viewname.py（★ 真机探针）
# 定位:   ★ 换路由的**前提** = 后继 `GetName2` 与被废弃的 `Name` **真机等价**。
#         ★ 本文件把那次真机读数**冻成判据**，★ 并把「样本太弱」**显式记进未过门**。
# 官方依据: C:/swapi/types/IView/Name.md「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]」
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改 `scripts/`（★ 本轮**只量不改** —— ★ 样本太弱，不足以支撑改代码）
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

from tests.test_obsolete_multi_successor_impact import _HOST_REVIEW  # noqa: E402

#: ★★ **4 处 `IView::Name` 真命中**（★ 248 的 `_HOST_REVIEW["Name"]` 里 `real-hit` 的那些站点）。
SITES_VIEW = (
    ("sw_drawing_query.py", 194),
    ("sw_drawing_query.py", 264),
    ("sw_drawing_view.py", 436),
)
#: ★ 第 4 处：宿主 `av`（`model.ActiveView` ⇒ IView），★ 248 新发现的那一处。
SITE_AV = ("sw_review.py", 637)

#: ★★★ **真机读数**（`output/_probe254_viewname.py` · SW rev **34.4.1** · 图纸 `output/pdf-probe.SLDDRW`）：
#:   ★ 视图数 **1**（★ **是「图纸本身」那个伪视图**）· `Name` == `GetName2` == `'图纸1'`
#:   ⇒ ★ **同 1 · 异 0 · 失败 0**。
MACHINE = {"views": 1, "same": 1, "diff": 0, "fail": 0,
           "sample": "图纸本身（伪视图）", "name": "图纸1", "getname2": "图纸1"}
#: ★★ **样本下界**（★ 只允许增不允许减）—— ★ 且**必须**记下「样本弱」这件事。
BASELINE_SAMPLE = 1

#: ★★ **真机踩的三个坑**（★ 都写进判据，避免下一轮重踩）。
MACHINE_PITFALLS = (
    "ISheet 上没有 GetFirstView（AttributeError）—— 要用 IModelDoc2::GetFirstView + IView::GetNextView",
    "只读打开时 doc.GetCurrentSheet 回 None —— 别从 sheet 入手",
    "IView::GetName2 在 COM 迟到绑定下**是属性不是方法** —— 不能加括号",
)


def _sites_failures(review: dict, sites: tuple[tuple[str, int], ...]) -> list[str]:
    """★★★ **spec 292 改成「换**后**」判据**：★ 这 4 处**已不再是** 248 的 `Name` 证据（★ 256 换掉了）。

    ★★ 原先判的是「靶子与 248 证据**逐字一致**」（★ 那是**换前**的检查）——
      ★ 256 换完之后它们**必然**从证据里消失 ⇒ ★ 原判据会**永远红**（★ 那是假红）
      ⇒ ★ 改成**换后**的断言（★ 它同时是 248 棘轮下调的**内容断言** · 铁律 22）。
    """
    out: list[str] = []
    ev = review.get("Name")
    if ev is None:
        return ["248 的 `_HOST_REVIEW` 里没有 `Name` 条目"]
    if ev[0] != "false-hit":
        out.append("248 的 `Name` 表态是 %r ⇒ 256 换完后应为 `false-hit`" % ev[0])
    hosts = {h for (_f, h) in ev[2]}
    for h in ("view", "av"):
        if h in hosts:
            out.append("宿主 %r 还在 248 的 `Name` 证据里 ⇒ 256 的换路由被回退" % h)
    return out


def _equiv_failures(m: dict) -> list[str]:
    """★ 纯函数：真机读数必须「有样本、且 Name == GetName2」。"""
    out: list[str] = []
    if m["views"] < BASELINE_SAMPLE:
        out.append("真机视图数 %d < 下界 %d ⇒ 证据不足" % (m["views"], BASELINE_SAMPLE))
    if m["diff"]:
        out.append("真机上 Name 与 GetName2 **不等价** %d 处 ⇒ **不能换路由**" % m["diff"])
    if m["fail"]:
        out.append("真机上有 %d 处取不到值 ⇒ 证据不可用" % m["fail"])
    if m["name"] != m["getname2"]:
        out.append("样本上 %r != %r" % (m["name"], m["getname2"]))
    return out


# ── ① 4 处靶子**已被 256 换掉**（★ spec 292 改成「换后」） ──────────────
def test_four_view_name_sites_are_the_248_ones():
    """★★★ **换后**：★ 248 当年点名的 4 处靶子（3 处 `view` + 1 处 `av`）**已被 256 换掉**。

    ★★ 判据（★ spec 292 改法）：★ ① 248 的 `Name` 表态已是 `false-hit`；
      ★ ② 证据里**不再有** `view` / `av` 宿主；★ ③ 那 3 个文件里**有**官方后继 `GetName2`。
    """
    bad = _sites_failures(_HOST_REVIEW, SITES_VIEW + (SITE_AV,))
    assert not bad, "靶子站点与 248 不符：\n" + "\n".join("  " + b for b in bad)
    for fname in ("sw_drawing_query.py", "sw_drawing_view.py", "sw_review.py"):
        src = (ROOT / "scripts" / fname).read_text(encoding="utf-8", errors="replace")
        assert "GetName2" in src, "★ `%s` 里没有官方后继 `GetName2` ⇒ 256 的换路由证据不成立" % fname


# ── ② ★★ 真机等价性读数 ─────────────────────────────────────────────
def test_machine_equivalence_reading():
    """★★ 真机（SW rev 34.4.1）读数：`Name` == `GetName2` ⇒ ★ 后继与被废弃者**等价**。

    ★★ **但样本只有 1 个视图、且是「图纸本身」** ⇒ ★ 见 `test_sample_is_explicitly_weak`。
    """
    bad = _equiv_failures(MACHINE)
    assert not bad, "真机等价性不合格：\n" + "\n".join("  " + b for b in bad)


# ── ③ ★★★ 样本必须被**显式**标为「弱」──────────────────────────────
def test_sample_is_explicitly_weak():
    """★★★ **不许把弱证据当强证据** —— ★ 本判据要求样本被**显式**标注。

    ★ 为什么单独立一条：★ 「1 个视图」与「20 个模型视图」在**只看 same/diff/fail** 时**同形**
    （★ 都是 同 N · 异 0 · 失败 0）⇒ ★ 必须把**样本规模**单独钉住。
    """
    assert MACHINE["views"] == 1, "样本数变了 ⇒ 请同步更新 `sample` 描述与未过门"
    assert "伪视图" in MACHINE["sample"], \
        "样本描述必须写明它是**图纸本身**（★ 伪视图）—— ★ 不许含糊过去"
    #: ★★ 弱证据 ⇒ ★ **不得**据此改代码（★ 本轮就是「只量不改」）。
    assert MACHINE["views"] < 5, "样本 ≥5 ⇒ 可以考虑换路由；★ 但要把 `test_sample_is_explicitly_weak` 一起改"


# ── ④ ★★ 真机踩的坑必须留在判据里 ──────────────────────────────────
def test_machine_pitfalls_are_recorded():
    """★ 三个真机坑（★ 本轮实测）必须写进判据 —— ★ 否则下一轮会重踩。"""
    assert len(MACHINE_PITFALLS) >= 3, "真机坑只剩 %d 条" % len(MACHINE_PITFALLS)
    joined = " ".join(MACHINE_PITFALLS)
    for key in ("GetFirstView", "GetCurrentSheet", "属性"):
        assert key in joined, "真机坑里少了 %s" % key


# ── ⑤ ★★ 纯函数**能红**（合成负例）──────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 样本为 0；② 不等价；③ 站点漂移。"""
    good = dict(MACHINE)
    assert not _equiv_failures(good), "正常读数被判红 ⇒ 判据过严"

    zero = dict(MACHINE, views=0)
    assert any("证据不足" in b for b in _equiv_failures(zero)), "样本为 0 未被判出 ⇒ **空判据**"

    diff = dict(MACHINE, diff=1)
    assert any("不等价" in b for b in _equiv_failures(diff)), "不等价未被判出 ⇒ **空判据**"

    assert _sites_failures({"Name": ("mixed", "x", ())}, SITES_VIEW), \
        "站点全缺却未判出 ⇒ 空判据"
