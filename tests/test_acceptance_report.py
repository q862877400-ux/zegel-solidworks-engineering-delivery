"""★ E1–E7 报告的汇总判据。

判据来源：`AGENTS.md` 验收判据 A8 ——
「进度按 S0–S6 报：走到哪步、该步完成标准是否满足、
**首件 E1–E7 逐条状态与证据变化**」。

## 为什么汇总本身要判

10 条判据各自正确，**不代表**汇总出来的报告可信。三个坑：

① 一个 E 下有多条检查时，只报「有绿的」⇒ 拆分变成放宽
② `unknown` 混进 `fail` ⇒ 把「我们没测到」说成「东西不合格」
③ 一条检查都没跑 ⇒ 报成「通过」

本文件把这三条钉住。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.report import (  # noqa: E402
    CRITERIA,
    CRITERIA_NAMES,
    build_report,
    deltas,
    render_markdown,
)
from engineering.acceptance.result import CheckResult, Status  # noqa: E402

REQ = "R-report"


def _r(check_id: str, status: Status, reason: str = "原因") -> CheckResult:
    return CheckResult(
        check_id=check_id,
        requirement_id=REQ,
        target="t",
        observation_complete=True,
        status=status,
        reason=reason,
    )


def _all_pass() -> list:
    """★ 10 条检查全绿（对应代码里真实的 10 个 check_id）。"""
    return [
        _r("E1.dof", Status.PASS),
        _r("E2.rebuild", Status.PASS),
        _r("E2.hole_readback", Status.PASS),
        _r("E3.tree", Status.PASS),
        _r("E3.reference_stability", Status.PASS),
        _r("E4.dof", Status.PASS),
        _r("E4.interference", Status.PASS),
        _r("E5.drawing", Status.PASS),
        _r("E6.process", Status.PASS),
        _r("E7.provenance", Status.PASS),
    ]


# ────────────────── ① 拆分不放宽 ──────────────────


def test_同一E下有一条未测到就不绿() -> None:
    """★★ 核心：E4 有两条检查，一条 pass 一条 unknown ⇒ E4 不能是 pass。

    ★ 这是「拆分不放宽」的最小形态。若汇总只看「有没有绿的」，
      拆分就成了放宽判据的借口。
    """
    checks = [
        _r("E4.dof", Status.UNKNOWN, "DOF 读不到"),
        _r("E4.interference", Status.PASS, "无干涉"),
    ] + [_r(c, Status.PASS) for c in ("E1.dof", "E2.rebuild", "E3.tree", "E5.drawing",
                                      "E6.process", "E7.provenance")]
    rep = build_report(checks)
    assert rep["criteria"]["E4"]["status"] == "unknown"
    assert rep["criteria"]["E4"]["unknown"] == ["E4.dof"]
    assert rep["overall"] != "pass"


def test_同一E下有一条不合格就报fail() -> None:
    """★ fail 比 unknown 严重，优先报 fail。"""
    checks = (
        _all_pass()
        [:4]
        + [_r("E3.reference_stability", Status.PASS)]
        + [_r("E4.dof", Status.UNKNOWN), _r("E4.interference", Status.FAIL, "有干涉")]
        + _all_pass()[7:]
    )
    rep = build_report(checks)
    assert rep["criteria"]["E4"]["status"] == "fail"
    assert rep["criteria"]["E4"]["failed"] == ["E4.interference"]


def test_一条检查都不跑时不是pass() -> None:
    """★★ 空集合不得判绿 —— 没检查过 ≠ 合格。"""
    rep = build_report([])
    assert rep["overall"] == "not_checked"
    assert len(rep["not_checked"]) == 7


def test_部分判据没检查时整体不绿() -> None:
    """★ 只跑了 E1，其余六条没跑 ⇒ 整体不能是 pass。"""
    rep = build_report([_r("E1.dof", Status.PASS)])
    assert rep["criteria"]["E1"]["status"] == "pass"
    assert rep["overall"] == "unknown"
    assert "E2" in rep["not_checked"]


# ────────────────── ② unknown 与 fail 分列 ──────────────────


def test_unknown与fail分开计数() -> None:
    """★★ 两者语义不同：没测到 vs 测到了不合格。"""
    checks = [_r("E1.dof", Status.UNKNOWN), _r("E2.rebuild", Status.FAIL)]
    rep = build_report(checks)
    assert rep["counts"]["unknown"] == 1
    assert rep["counts"]["fail"] == 1
    assert rep["criteria"]["E1"]["unknown"] == ["E1.dof"]
    assert rep["criteria"]["E2"]["failed"] == ["E2.rebuild"]


def test_报告里unknown单列一段() -> None:
    """★ 渲染时未测到的必须单独成段，不能混在「不合格」里。"""
    checks = [_r("E4.dof", Status.UNKNOWN, "DOF 读不到")]
    md = render_markdown(build_report(checks))
    assert "未测到的项（不等于合格）" in md
    assert "E4.dof" in md


def test_报告里不合格单列一段() -> None:
    checks = [_r("E5.drawing", Status.FAIL, "少关键尺寸")]
    md = render_markdown(build_report(checks))
    assert "不合格的项" in md
    assert "少关键尺寸" in md


# ────────────────── ③ not_applicable 的处理 ──────────────────


def test_全部不适用时该E判绿() -> None:
    """★ 有理由的不适用不算失败（理由由判定器保证）。"""
    checks = [_r("E6.process", Status.NOT_APPLICABLE)]
    rep = build_report(checks)
    assert rep["criteria"]["E6"]["status"] == "pass"
    assert rep["criteria"]["E6"]["not_applicable"] == ["E6.process"]


# ────────────────── 结构 ──────────────────


def test_七个判据都在报告里() -> None:
    """★ 即使没检查也要留位置 —— 漏掉一条等于报告有洞。"""
    rep = build_report([])
    for c in CRITERIA:
        assert c in rep["criteria"]
        assert rep["criteria"][c]["name"] == CRITERIA_NAMES[c]


def test_check_id按点号前缀归类() -> None:
    """★ `E4.dof` → `E4`。"""
    rep = build_report([_r("E4.dof", Status.PASS)])
    assert len(rep["criteria"]["E4"]["checks"]) == 1


def test_拼错的check_id被单列出来() -> None:
    """★★ 拼错的 `check_id` 不该悄悄消失 —— 那会让报告漏一条检查。"""
    rep = build_report([_r("E9.dof", Status.PASS)])
    assert rep["unassigned"], "★ 无法归类的检查必须列出来"
    assert rep["unassigned"][0]["check_id"] == "E9.dof"
    md = render_markdown(rep)
    assert "无法归类" in md


def test_非CheckResult被拒绝() -> None:
    with pytest.raises(TypeError):
        build_report([{"check_id": "E1.dof"}])


def test_十项全绿时总体pass() -> None:
    rep = build_report(_all_pass())
    assert rep["overall"] == "pass"
    for c in CRITERIA:
        assert rep["criteria"][c]["status"] == "pass", "★ %s 应为 pass" % c


# ────────────────── 证据变化（A8 的「证据变化」） ──────────────────


def test_deltas报出改善() -> None:
    """★ A8 要求「证据变化」，这里给两次报告的差异。"""
    before = build_report([_r("E4.dof", Status.UNKNOWN)])
    after = build_report([_r("E4.dof", Status.PASS)])
    d = deltas(before, after)
    assert "E4" in d["improved"]
    assert d["changed"][0] == {"criterion": "E4", "from": "unknown", "to": "pass"}


def test_deltas报出回退() -> None:
    """★ 回退也要报 —— 只报改善的报告是广告，不是验收记录。"""
    before = build_report([_r("E5.drawing", Status.PASS)])
    after = build_report([_r("E5.drawing", Status.FAIL)])
    d = deltas(before, after)
    assert "E5" in d["regressed"]


def test_deltas无变化时为空() -> None:
    same = build_report([_r("E1.dof", Status.PASS)])
    d = deltas(same, same)
    assert d["changed"] == []


# ────────────────── 渲染不丢信息 ──────────────────


def test_渲染包含全部七行() -> None:
    md = render_markdown(build_report(_all_pass()))
    for c in CRITERIA:
        assert "**%s**" % c in md


def test_渲染标出未检查的判据() -> None:
    md = render_markdown(build_report([_r("E1.dof", Status.PASS)]))
    assert "未检查的判据" in md
    assert "不能当成通过" in md


def test_渲染出总体状态() -> None:
    md = render_markdown(build_report(_all_pass()))
    assert "**总体**" in md
    assert "pass" in md
