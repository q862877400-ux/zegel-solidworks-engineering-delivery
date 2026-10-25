"""★ 端到端：采集 → 判定 → 汇总 → 渲染。

判据来源：`tools/probe_acceptance_report.py`（同一个链路，本文件把它变成断言）。

## 为什么需要这条

`test_acceptance_report.py` 里拼的是**人工构造**的 `CheckResult`，
只能证明汇总逻辑对 —— 不能证明「十对采集器/判定器的输出真能喂进汇总」。

本文件跑**真实**的采集器与判定器（吃 `samples.py` 的样件），
再用 `build_report()` 汇总 —— 证明链路本身通。

★ 这条也是「十对采集器/判定器的返回结构确实一致」的回归：
  任何一个判定器改了返回类型或 check_id，这里就红。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tools"))

from engineering.acceptance.report import CRITERIA, build_report, render_markdown  # noqa: E402
from engineering.acceptance.result import CheckResult  # noqa: E402
from probe_acceptance_report import good_checks, mixed_checks  # noqa: E402


def test_全绿组十项全过() -> None:
    """★★ 核心：用**真实**采集器+判定器跑样件，报告必须 10/10 pass。

    ★ 若这条红了，先看是哪个 check_id 变了 —— 不要直接改断言。
    """
    checks = good_checks()
    assert len(checks) == 11, "★ 检查条数应为 11（第 41 轮拆出 E2.drawing_current），实得 %d" % len(checks)
    assert all(isinstance(c, CheckResult) for c in checks), (
        "★ 有判定器没返回 CheckResult：%r"
        % [type(c).__name__ for c in checks if not isinstance(c, CheckResult)]
    )

    rep = build_report(checks)
    assert rep["overall"] == "pass", (
        "★ 全绿组应为 pass，实得 %s。未全绿：%r"
        % (
            rep["overall"],
            {
                c: rep["criteria"][c]["status"]
                for c in CRITERIA
                if rep["criteria"][c]["status"] != "pass"
            },
        )
    )
    assert rep["counts"]["pass"] == 11
    assert not rep["not_checked"], "★ 不该有未检查的判据：%r" % rep["not_checked"]


def test_全绿组的check_id覆盖七个判据() -> None:
    """★ 七个判据每个都要有至少一条检查（防某个 E 被漏掉）。"""
    rep = build_report(good_checks())
    for crit in CRITERIA:
        assert rep["criteria"][crit]["checks"], (
            "★ %s 一条检查都没有 —— 全绿组也该覆盖它" % crit
        )


def test_多检查判据的条数() -> None:
    """★ 拆分后的形态，必须真的跑到。

    | 判据 | 条数 | 拆出来的子项 |
    |---|---|---|
    | E2 | **3** | rebuild · hole_readback · **drawing_current**（第 41 轮拆） |
    | E3 | 2 | tree · reference_stability |
    | E4 | 2 | dof · interference |
    """
    rep = build_report(good_checks())
    want = {"E2": 3, "E3": 2, "E4": 2}
    for crit, n in want.items():
        got = len(rep["criteria"][crit]["checks"])
        assert got == n, "★ %s 应有 %d 条检查，实得 %d" % (crit, n, got)


def test_混合组三种状态都出现() -> None:
    """★ 混合组要真的含 fail / unknown / not_checked —— 否则它没测到三种状态。"""
    rep = build_report(mixed_checks())
    statuses = {rep["criteria"][c]["status"] for c in CRITERIA}
    assert "fail" in statuses, "★ 混合组应有不合格的判据"
    assert "not_checked" in statuses, "★ 混合组应有未检查的判据"
    assert rep["counts"]["unknown"] >= 1, "★ 混合组应有未测到的检查"


def test_混合组的下标问题被抓到() -> None:
    """★★ E3.reference_stability 必须抓住 `index:0` —— 端到端验证这条判据真生效。"""
    rep = build_report(mixed_checks())
    assert "E3.reference_stability" in rep["criteria"]["E3"]["failed"], (
        "★ 混合组里塞了 index:0，E3.reference_stability 应当 fail。实得 failed=%r"
        % rep["criteria"]["E3"]["failed"]
    )


def test_混合组的孔型缺口报unknown() -> None:
    """★★ 孔型没给 ⇒ `E2.hole_readback` 报 unknown（不是 pass、也不是 fail）。"""
    rep = build_report(mixed_checks())
    assert "E2.hole_readback" in rep["criteria"]["E2"]["unknown"], (
        "★ 混合组没给孔型，应进 unknown。实得 unknown=%r"
        % rep["criteria"]["E2"]["unknown"]
    )


def test_渲染能产出完整报告() -> None:
    """★ 渲染不抛、且含七个判据行。"""
    md = render_markdown(build_report(good_checks()), title="回归")
    for crit in CRITERIA:
        assert "**%s**" % crit in md
    assert "**总体**" in md


def test_两次运行结果一致() -> None:
    """★ 同一输入两次汇总必须一致 —— 报告不该带随机性。"""
    a = build_report(good_checks())
    b = build_report(good_checks())
    assert a["overall"] == b["overall"]
    assert a["counts"] == b["counts"]
