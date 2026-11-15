"""齿轮方法层 v0 的契约测试：参数域、来源标签、无解诊断、与归档实现交叉校验。"""
from __future__ import annotations

import math

import pytest

from gear_method import (ALPHA_DEG, SOURCES, GearRequest, derive, render)


def test_basic_derivation_hits_center_distance():
    d = derive(GearRequest(ratio=3.0, center_mm=40.0))
    assert d.ok
    vals = {r.key: r.value for r in d.rows}
    assert vals["m"] == "1 mm"
    assert vals["z1"] == "20" and vals["z2"] == "60"
    assert vals["d1"].startswith("20.0") and vals["d2"].startswith("60.0")


def test_every_row_has_a_declared_source():
    d = derive(GearRequest(ratio=3.0, center_mm=40.0))
    assert d.rows
    for r in d.rows:
        assert r.source in SOURCES, f"{r.key} 的来源 {r.source!r} 不在六类里"


def test_geometry_cross_checked_against_archived_implementation():
    d = derive(GearRequest(ratio=3.0, center_mm=40.0))
    row = {r.key: r.evidence for r in d.rows}
    assert "一致" in row["d1"]
    assert "不一致" not in row["d1"]


def test_no_solution_reports_the_nearest_alternatives_not_a_shrug():
    d = derive(GearRequest(ratio=3.0, center_mm=30.0))
    assert not d.ok
    text = "\n".join(d.diagnostics)
    assert "最接近" in text and "mm" in text
    # 必须给出具体数字，不能只说"无解"
    assert any(ch.isdigit() for ch in text)


def test_pinned_z1_is_marked_as_locked_and_the_rest_still_derives():
    d = derive(GearRequest(ratio=2.5, center_mm=43.0, pin_z1=20))
    assert d.ok
    rows = {r.key: r for r in d.rows}
    assert rows["z1"].source == "锁"
    assert rows["m"].source == "选" and rows["z2"].source == "算"
    assert rows["z1"].value == "20"


def test_undercut_policy_is_declared_not_implicit():
    kb = derive(GearRequest(ratio=3.0, center_mm=40.0, z_min_policy="kb"))
    strict = derive(GearRequest(ratio=3.0, center_mm=40.0, z_min_policy="strict"))
    z_kb = next(r for r in kb.rows if r.key == "z_min").value
    z_st = next(r for r in strict.rows if r.key == "z_min").value
    assert z_kb == "17" and z_st == "18"
    assert z_kb != z_st, "两种口径必须能被区分，否则就是在偷偷改判据"


def test_uncovered_items_are_always_present():
    d = derive(GearRequest(ratio=3.0, center_mm=40.0))
    joined = " ".join(d.uncovered)
    assert "强度校核" in joined
    assert "变位" in joined


def test_contact_ratio_is_in_a_plausible_band():
    d = derive(GearRequest(ratio=3.0, center_mm=40.0))
    eps = float(next(r for r in d.rows if r.key == "eps").value)
    assert 1.2 <= eps <= 2.0, f"εα={eps} 超出标准直齿常见范围，公式可能有误"


def test_render_is_markdown_with_uncovered_section():
    out = render(derive(GearRequest(ratio=3.0, center_mm=40.0)))
    assert out.startswith("| # | 参数 |")
    assert "【未覆盖】" in out
