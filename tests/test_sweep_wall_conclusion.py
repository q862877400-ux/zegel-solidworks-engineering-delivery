"""★ 测「薄壁那条路的结论」+「最近候选判据」（★ 含负例 · 轮 128）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md` +
#         真机证据 `output/sweep-wall-units-capability-recheck.json`
# 文件:   tests/test_sweep_wall_conclusion.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 128）**三条真读数**：
#     ★ **① 事实**：★ `ThinFeature=True` 经 `ModifyDefinition` **没被采纳**
#       （★ `volume_before = volume_after = **1130.973**`、★ 与实体解析值 **1130.97** 距离 **0.0**）✓
#     ★★ **② 真因（★ 官方逐字）**：★「**You cannot make a thin-walled sweep feature after
#       the sweep has been created**, and **you cannot edit a sweep feature to make it
#       thin walled**」⇒ ★ **必须在 `CreateFeature` 之前设** ✓
#     ★★★ **③ 而那是**我漏读 `## Remarks` 造成的****（★ 我只读了 `## Returns`）⇒
#       ★ 本仓 AGENTS.md 明写「官方是第 0 步：签名 + `## Remarks` + 例子」✓
#   ★★★★ **两条判据**：
#     · **判定"落在哪个候选上"要用**最近候选**、★ 不要用一串容差带**（★ 本轮两版都误判）·
#     · **判据**漏了候选**就会把读数塞给最近的那个**（★ 本轮第一版漏了"没生效"那个候选）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_feature_readback.py"
PROBE = REPO / "tools" / "probe_sweep_wall_units_recheck.py"


def test_the_conclusion_is_recorded_with_the_official_reason() -> None:
    """★★★ 核心断言：★ 那条结论与**官方那句**都记在能力里 ✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "sweep_params")
    assert "不能" in body and "先建后改" in body, "★ 没记下「不能先建后改」这条结论"
    #: ★★ 官方那句要**逐字**在（★ 那是依据）✓
    #: ★★★★ **⚠ 而判据要**避开跨行****（★ 值记）：
    #:   我第一版查的是整句 `"cannot edit a sweep feature to make it thin walled"` ⇒
    #:   ★★ **红了** —— ★ 因为那句在 docstring 里**跨了两行**（★ 中间有换行与缩进）⇒
    #:   ★★★ **⇒ 连续子串匹配**看不到它**** ✓
    #:   ★★ **⇒ 判据改成查**不跨行的片段**** ✓
    #:   ★★★★★ **可复用判据**：★★★ **在 docstring 里查"某句话在不在"时，
    #:     要**避开跨行** —— ★ 否则判据会因**排版**而红（★ 而那**不是内容缺失**）** ✓
    assert "sweep feature to make it thin walled" in body, (
        "★ 官方那句逐字理由没记下来")
    assert "before calling" in body, "★ 那个「必须在 CreateFeature 之前设」没记下来"


def test_the_measured_evidence_is_recorded() -> None:
    """★★★ 核心断言：★ 真机那两个体积写进去（★ 那是"怎么知道的"）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "sweep_params")
    assert "1130.973" in body, "★ 实测体积没记下"
    assert "125.664" in body or "125.66" in body, "★ 次近候选的距离没记下"


def test_negative_case_the_probe_uses_nearest_candidate() -> None:
    """★★★★ 核心断言：★ 判定用 **最近候选**、★ **不是容差带** ✓

    ★★ **为什么**：★ 本轮**两版容差带都误判了** ——
      ★ 第一版 `max(30, M*0.15)=150.8` ⇒ 把 1130.97 判成"米"；
      ★★ 第二版改成「两候选距离的 1/4」= **250.9** ⇒ **更宽** ⇒ **又误判** ✗
      ★★★ **⇒ 正解是**最近候选分类****（★ 而它要求**候选表不漏**）✓
    """
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "min(_cands, key=" in t, "★ 没走最近候选分类"
    #: ★★ 而**三个候选都要在**（★ 第一版就是漏了"没生效"那个）✓
    for need in ("薄壁没生效", "米", "毫米"):
        assert need in t, "★ 候选表里少了 `%s`" % need


def test_negative_case_the_official_remarks_lesson_is_recorded() -> None:
    """★★★★ 核心断言：★ 「漏读 `## Remarks`」这条教训要留在探针里 ✓

    ★★ **为什么**：★ 本仓 AGENTS.md 明写「官方是第 0 步：★ **签名 + `## Remarks` + 例子**」⇒
      ★★ **而那正是本轮出错的地方**（★ 我只读了 `## Returns`）⇒
      ★★★ **⇒ 记号要留下、★ 免得下一个人重犯** ✓
    """
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "Remarks" in t, "★ 探针里没提到 `## Remarks` 这条教训"
