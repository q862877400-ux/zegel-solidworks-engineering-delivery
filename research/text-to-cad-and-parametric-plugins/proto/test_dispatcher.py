"""工程判断层契约测试：分流表与调度器必须始终一致。"""
from __future__ import annotations

import pytest

from dispatcher import ROUTES, can_build_now, decide, render


def test_buy_route_never_builds_geometry():
    d = decide("bearing-deep-groove")
    assert d.verdict == "买"
    assert "选型" in d.route and not can_build_now("bearing-deep-groove")


def test_gear_has_no_generator_after_polyline_ban():
    """★★ 2026-11-07 业主令：折线齿轮生成器已删；齿轮族当前不得声称能出几何。"""
    d = decide("gear-cylindrical")
    assert d.verdict == "造"
    assert d.source and "cq_gears" in d.source
    assert not can_build_now("gear-cylindrical")


def test_parked_items_are_flagged_not_silently_drawn():
    d = decide("cam")
    assert d.known_gap
    assert "已知缺口" in render(d)
    assert not can_build_now("cam")


def test_unknown_part_is_rejected_not_guessed():
    with pytest.raises(KeyError):
        decide("some-part-nobody-registered")


def test_every_triage_row_has_a_declared_route():
    """53 项分流表里的每一行，都必须落在四个已知去向之一。"""
    from dispatcher import _load
    t = _load()
    assert len(t) == 53
    for pid, r in t.items():
        assert r["verdict"] in ROUTES, f"{pid} 的判定 {r['verdict']} 没有对应路线"


def test_buy_items_all_have_a_source():
    from dispatcher import _load
    for pid, r in _load().items():
        if r["verdict"] == "买":
            assert r.get("where"), f"{pid} 判定为买却没写去哪拿"


def test_only_implemented_generators_report_can_build_now():
    from dispatcher import GENERATORS, _load
    for pid, r in _load().items():
        if r["verdict"] == "造" and pid not in GENERATORS:
            assert not can_build_now(pid), f"{pid} 没有生成器却声称能出几何"
