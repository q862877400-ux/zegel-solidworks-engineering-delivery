"""★ spec 255：**造出多视图工程图**，把 `IView::Name` == `GetName2` 的证据从 1 个伪视图升到**真实模型视图**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/254-iview-name-routing/（★ 254 的**触发条件** = 拿到真实模型视图）
#         output/_probe255_make_drawing.py（★ 真机探针：从现成零件造图并量）
#         output/fixtures/刀柄_Holder.sldprt（★ 零件来源）
# 定位:   ★ 254 的证据只有 **1 个「图纸本身」伪视图** ⇒ ★ 本文件把样本升到 **4 个视图（其中 3 个真实模型视图）**。
# 官方依据: SW rev **34.4.1** 真机 · `ISldWorks::GetUserPreferenceStringValue(10)` = 工程图模板
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读判据；★ 真机部分由 `output/_probe255_make_drawing.py` 跑（★ 已存 `output/_probe255_views.SLDDRW`）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **真机读数**（`output/_probe255_make_drawing.py` · SW rev **34.4.1**）：
#:   从 `output/fixtures/刀柄_Holder.sldprt` 用 `Create3rdAngleViews2` 造图 ⇒ **4 个视图**，全部 `Name` == `GetName2`。
MACHINE = {
    "views": 4,
    "real_model_views": 3,          #: ★ 3 个 `工程图视图N`（★ 第 4 个是「图纸本身」）
    "same": 4,
    "diff": 0,
    "pairs": (("图纸1", "图纸1"),
              ("工程图视图1", "工程图视图1"),
              ("工程图视图2", "工程图视图2"),
              ("工程图视图3", "工程图视图3")),
    "part": "output/fixtures/刀柄_Holder.sldprt",
    "saved_drawing": "output/_probe255_views.SLDDRW",
}

#: ★ 下界（★ 只增不减）。
BASELINE_VIEWS = 4
BASELINE_REAL_VIEWS = 3
#: ★★ 254 立的**换路由门槛**（★ 254 的 `test_sample_is_explicitly_weak` 写的是「views ≥5 可考虑换路由」）。
ROUTING_THRESHOLD = 5

#: ★★ 真机踩的坑（★ 本轮新增两条，★ 都进判据）。
PITFALLS = (
    "sw.GetUserPreferenceStringValue(9) 是**装配**模板（gb_assembly.asmdot）⇒ 建出来的是装配、没有 Create3rdAngleViews2",
    "sw.GetUserPreferenceStringValue(10) 才是**工程图**模板（gb_a4.drwdot）",
    "win32com.VARIANT 不存在 —— 必须 from win32com.client import VARIANT",
)


def _reading_failures(m: dict) -> list[str]:
    """★ 纯函数：读数必须「样本够、且逐对相等」。"""
    out: list[str] = []
    if m["views"] < BASELINE_VIEWS:
        out.append("视图数 %d < 下界 %d" % (m["views"], BASELINE_VIEWS))
    if m["real_model_views"] < BASELINE_REAL_VIEWS:
        out.append("**真实模型视图** %d < 下界 %d ⇒ 证据仍弱" % (m["real_model_views"], BASELINE_REAL_VIEWS))
    if m["diff"]:
        out.append("有 %d 处 `Name` != `GetName2` ⇒ **不能换路由**" % m["diff"])
    if len(m["pairs"]) != m["views"]:
        out.append("逐对读数 %d 条 != 视图数 %d ⇒ 读数不完整" % (len(m["pairs"]), m["views"]))
    for old, new in m["pairs"]:
        if old != new:
            out.append("样本 %r != %r" % (old, new))
    return out


# ── ① ★★ 读数：4 个视图逐对相等 ──────────────────────────────────────
def test_multi_view_equivalence_reading():
    """★★ 4 个视图（含 **3 个真实模型视图**）上 `Name` == `GetName2`。

    ★ 能红的判据：★ 把任一对改成不等 ⇒ 当场红。
    """
    bad = _reading_failures(MACHINE)
    assert not bad, "多视图等价性不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 样本强度：必须**真的**含模型视图（★ 不许再靠伪视图充数）──
def test_sample_has_real_model_views():
    """★★★ 254 的教训：★ 「1 个伪视图」与「N 个模型视图」在只看 same/diff 时**同形**。

    ★ 本判据要求：★ **真实模型视图 ≥3**（★ 名字形如 `工程图视图N`，★ 不是 `图纸N`）。
    """
    real = [n for (n, _g) in MACHINE["pairs"] if n.startswith("工程图视图")]
    assert len(real) >= BASELINE_REAL_VIEWS, \
        "真实模型视图只剩 %d 个（%s）⇒ 证据退化" % (len(real), real)
    assert MACHINE["real_model_views"] == len(real), \
        "`real_model_views` 字段与实际数 %d 不符" % len(real)


# ── ③ ★★ 换路由门槛（★ 未达 ⇒ 明确记进未过门，不许含糊）────────────
def test_routing_threshold_is_not_yet_met():
    """★★ 254 立的门槛是 **views ≥ 5**；★ 本轮只有 **4** ⇒ ★ **门槛未达** ⇒ ★ **本轮仍不改代码**。

    ★ 若哪天样本 ≥5 ⇒ ★ 本判据会红 ⇒ ★ 提醒把 254/255 的「只量不改」一起改掉、**开始换路由**。
    """
    assert MACHINE["views"] < ROUTING_THRESHOLD, (
        "样本已达 %d ≥ 门槛 %d ⇒ ★ 可以换路由了：★ 请同步改掉本判据与 254 的 "
        "`test_sample_is_explicitly_weak`，然后改 `sw_drawing_query.py` / `sw_drawing_view.py` / `sw_review.py`。"
        % (MACHINE["views"], ROUTING_THRESHOLD))


# ── ④ 真机坑进判据 ───────────────────────────────────────────────────
def test_pitfalls_are_recorded():
    """★ 三条真机坑必须留在判据里（★ 否则下一轮重踩）。"""
    joined = " ".join(PITFALLS)
    for key in ("gb_assembly", "gb_a4", "VARIANT"):
        assert key in joined, "真机坑里少了 %s" % key


# ── ⑤ ★★ 纯函数能红 ─────────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 不等价；② 真实视图不足；③ 逐对条数不符。"""
    good = dict(MACHINE)
    assert not _reading_failures(good), "正常读数被判红 ⇒ 判据过严"
    assert _reading_failures(dict(MACHINE, diff=1)), "diff=1 未判出 ⇒ **空判据**"
    assert _reading_failures(dict(MACHINE, real_model_views=0)), "真实视图 0 未判出 ⇒ **空判据**"
    assert _reading_failures(dict(MACHINE, pairs=MACHINE["pairs"][:2])), "读数不完整未判出 ⇒ **空判据**"
