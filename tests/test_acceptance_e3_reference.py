"""★ E3 子项：引用稳定性 —— 跨重建不依赖选区或下标。

判据来源：`docs/ENGINEERING-PATH.md` 第四节 E3「必须读什么」：

> 主尺寸/基准/孔位必须有稳定语义引用，跨重建不依赖选区或下标。

## 为什么这条要单独判

`scripts/engineering/reference_resolver.py` 的 `LIMITATIONS` 自己逐字写着：

> **索引不跨编辑保持** —— "Anchors are exact for **fresh-doc replay**…
> but **NOT durable across edits**" ⇒ 改完模型后，之前算出来的
> face/edge index 全部作废，必须重查

⇒ 计划里若**存**下标，改一个主参数后「第 0 条边」可能已经是另一条边。
   而工具层的 `selection` 只接受 `index:<n>` 与 `__current_selection__` ——
   **两者都不可跨重建**。

本文件把「计划里不该存这种形态」钉成判据。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_reference_stability,
    judge_reference_stability,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-refstab"


def _judge(steps):
    obs = collect_reference_stability(target="plan", steps=tuple(steps))
    return judge_reference_stability(obs, requirement_id=REQ)


# ────────────────── 拒绝的形态 ──────────────────


def test_下标被判为不可跨重建() -> None:
    """★★ 核心：`index:0` 是下标，改几何后会漂。"""
    res = _judge([{"step": "chamfer", "params": {"selection": "index:0"}}])
    assert res.status is Status.FAIL
    assert "不可跨重建" in res.reason
    assert res.observed["fragile"][0]["param"] == "selection"


def test_当前选区被判为不可跨重建() -> None:
    """★ `__current_selection__` 取决于调用时选了什么，不是模型属性。"""
    res = _judge([{"step": "fillet", "params": {"selection": "__current_selection__"}}])
    assert res.status is Status.FAIL


def test_任意数量的下标都报出来() -> None:
    """★ 不能只报第一处 —— 修的人要知道有几处。"""
    steps = [
        {"step": "chamfer", "params": {"selection": "index:0"}},
        {"step": "fillet", "params": {"selection": "index:2"}},
        {"step": "chamfer", "params": {"selection": "index:5"}},
    ]
    res = _judge(steps)
    assert res.status is Status.FAIL
    assert res.observed["count"] == 3


# ────────────────── 接受的形态 ──────────────────


@pytest.mark.parametrize(
    "selector",
    ["+z", "-z", "+x", "-x", "+y", "-y", "top_face"],
    ids=["+z", "-z", "+x", "-x", "+y", "-y", "top_face"],
)
def test_方向语义与top_face被接受(selector) -> None:
    """★ `reference_resolver.resolve()` 支持的语义选择器 —— 几何事实，改参数后仍成立。"""
    res = _judge([{"step": "chamfer", "params": {"selection": selector}}])
    assert res.status is Status.PASS, "★ %r 应被接受，实得 %s" % (selector, res.status.value)


def test_几何锚点被接受() -> None:
    """★ `near:x,y,z` 是几何锚点，`resolve()` 明确说「跨重建稳定」。"""
    res = _judge([{"step": "sketch_start", "params": {"on_face": "near:10,20,30"}}])
    assert res.status is Status.PASS


def test_无选区参数的计划通过() -> None:
    """★ 不涉及选区的步骤不该被判死。"""
    res = _judge([{"step": "extrude_boss", "params": {"depth_mm": 20.0}}])
    assert res.status is Status.PASS


# ────────────────── 三态与结构 ──────────────────


def test_没有步骤时判unknown() -> None:
    """★ 没数据 ⇒ unknown，不是 pass。"""
    obs = collect_reference_stability(target="plan", steps=())
    assert judge_reference_stability(obs, requirement_id=REQ).status is Status.UNKNOWN


def test_check_id可指认() -> None:
    """★ 报告要能说清是「引用稳定性」这一项。"""
    res = _judge([{"step": "chamfer", "params": {"selection": "index:0"}}])
    assert res.check_id == "E3.reference_stability"


# ────────── 用真实 planner 输出做回归 ──────────


def test_planner的倒角候选仍带下标() -> None:
    """★★ 这是**当前实现的真实缺陷**，不是假设。

    `scripts/engineering/planner.py` 三处 chamfer 步骤写的是 `"selection": "index:0"`
    （见 `planner.py:270` / `:568` / `:578`）。
    按 `reference_resolver.LIMITATIONS`，那不是跨编辑稳定的引用。

    ★ 本测试**记录现状**：一旦有人把 planner 改成语义选择器，它会转红 ——
      那时应当**更新这条测试**（把断言反过来），因为缺陷已修。
      这条测试的存在意义是：不让「下标」悄悄留在计划里而没人知道。
    """
    from engineering import planner as PL

    ps = PL.plan_from_requirement("做一块100x60x20的安装板，四角四个φ6的孔，孔心距边10mm")
    fragile_methods = []
    for cand in ps.candidates:
        steps = tuple({"step": s.step, "params": s.params} for s in cand.plan.steps)
        if not steps:
            continue
        if _judge(steps).status is Status.FAIL:
            fragile_methods.append(cand.method_id)

    assert fragile_methods, (
        "★ 所有候选都不含下标了 —— 如果 planner 已改成语义选择器，"
        "请把本测试改成断言「没有任何候选含下标」，并更新"
        "specs/350-first-part-delivery/source-verification.md"
    )


def test_planner的倒角候选命中chamfer_step() -> None:
    """★ 精确定位：被抓到的必须是带 chamfer 的那条（不是别的步骤）。"""
    from engineering import planner as PL

    ps = PL.plan_from_requirement("做一块100x60x20的安装板，四角四个φ6的孔，孔心距边10mm")
    hits = []
    for cand in ps.candidates:
        steps = tuple({"step": s.step, "params": s.params} for s in cand.plan.steps)
        if not steps:
            continue
        res = _judge(steps)
        if res.status is Status.FAIL:
            hits.append(res.observed["fragile"][0]["step"])
    assert hits, "★ 应当至少抓到一处"
    assert all(h == "chamfer" for h in hits), (
        "★ 抓到的步骤应为 chamfer，实得 %r" % hits
    )
