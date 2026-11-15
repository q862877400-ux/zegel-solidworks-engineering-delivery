"""verify.py 判据测试 —— 全部离线，喂假读数验三条判据。

守的是 contracts/verify.contract.md。
真机路径不在这里测（那是 T024）。
"""
from __future__ import annotations

import pytest

from build_plan import Expected, Extrude, FeaturePlan, Line
from verify import (
    BBOX_TOL_MM,
    M3_TO_MM3,
    VIEW_NAMES,
    VOLUME_TOL_PCT,
    Verification,
    _read_bbox,
    _read_volume_mm3,
    verify,
)


# ── 夹具：可注入假读数的 plan ────────────────────────────────────────
def _plan(volume_mm3=1000.0, bbox=(20.0, 20.0, 5.0)) -> FeaturePlan:
    return FeaturePlan(
        name="T",
        units="mm",
        sketch_entities=[Line(2.0, 2.0, 10.0, 2.0)],
        features=[Extrude(depth_mm=5.0)],
        expected=Expected(volume_mm3=volume_mm3, bbox_x_mm=bbox[0],
                          bbox_y_mm=bbox[1], bbox_z_mm=bbox[2]),
        provenance={"profile_form": "test"},
    )


# ── 常量自检 ────────────────────────────────────────────────────────
def test_tolerances_are_the_contract_values():
    assert VOLUME_TOL_PCT == 1.0
    assert BBOX_TOL_MM == 0.5
    assert M3_TO_MM3 == 1e9
    assert VIEW_NAMES == ("isometric", "front", "top", "right")


def test_verification_dataclass_has_contract_fields():
    fields = set(Verification.__dataclass_fields__)
    for k in ("ok", "measured_volume_mm3", "expected_volume_mm3", "volume_deviation_pct",
              "measured_bbox_mm", "expected_bbox_mm", "bbox_deviation_mm", "views", "failure"):
        assert k in fields, f"Verification 缺字段 {k}"


# ── 体积判据 ────────────────────────────────────────────────────────
class _FakeModel:
    """只用来让 verify 的 monkeypatch 生效，不碰 COM。"""


def test_volume_within_tolerance_passes(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1005.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    v = verify(_FakeModel(), _plan())
    assert v.ok
    assert v.volume_deviation_pct == pytest.approx(0.5)


def test_volume_over_tolerance_fails(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1015.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    v = verify(_FakeModel(), _plan())
    assert not v.ok
    assert "体积偏差" in (v.failure or "")


def test_volume_edge_exactly_at_1pct_fails(monkeypatch):
    """契约：通过条件是 < 1.0，等于 1.0 不过。"""
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1010.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    v = verify(_FakeModel(), _plan())
    assert v.volume_deviation_pct == pytest.approx(1.0)
    assert not v.ok


def test_volume_unreadable_fails_with_reason(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (None, "mass_properties 回空"))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    v = verify(_FakeModel(), _plan())
    assert not v.ok
    assert "mass_properties 回空" in (v.failure or "")


# ── 包围盒判据 ──────────────────────────────────────────────────────
def test_bbox_within_tolerance_passes(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1000.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.2, 19.8, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    v = verify(_FakeModel(), _plan())
    assert v.ok


def test_bbox_over_tolerance_fails(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1000.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.9), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    v = verify(_FakeModel(), _plan())
    assert not v.ok
    assert "包围盒偏差超限" in (v.failure or "")


# ── 三视图判据 ──────────────────────────────────────────────────────
def test_missing_views_fail(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1000.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b"], "三视图只出了 2/4"))
    v = verify(_FakeModel(), _plan())
    assert not v.ok
    assert "三视图只出了 2/4" in (v.failure or "")


# ── 多条失败必须全列，不许掩盖 ──────────────────────────────────────
def test_multiple_failures_all_listed(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (2000.0, None))   # 体积翻倍
    monkeypatch.setattr("verify._read_bbox", lambda m: ((30.0, 20.0, 5.0), None))  # x 超 10
    monkeypatch.setattr("verify._export_views", lambda m, p, d: ([], "三视图只出了 0/4"))
    v = verify(_FakeModel(), _plan())
    assert not v.ok
    for frag in ("体积偏差", "包围盒偏差超限", "三视图只出了 0/4"):
        assert frag in (v.failure or ""), f"failure 漏了 {frag}"


# ── 前置条件 ────────────────────────────────────────────────────────
def test_none_model_raises():
    with pytest.raises(ValueError, match="model 为 None"):
        verify(None, _plan())


def test_non_mm_units_raises():
    p = _plan()
    bad = FeaturePlan(name=p.name, units="m", sketch_entities=p.sketch_entities,
                      features=p.features, expected=p.expected, provenance=p.provenance)
    with pytest.raises(ValueError, match="units 必须是 'mm'"):
        verify(_FakeModel(), bad)


def test_zero_expected_volume_raises():
    with pytest.raises(ValueError, match="必须 > 0"):
        verify(_FakeModel(), _plan(volume_mm3=0.0))


# ── 报告格式 ────────────────────────────────────────────────────────
def test_report_ok_has_verdict_line(monkeypatch):
    monkeypatch.setattr("verify._read_volume_mm3", lambda m: (1000.0, None))
    monkeypatch.setattr("verify._read_bbox", lambda m: ((20.0, 20.0, 5.0), None))
    monkeypatch.setattr("verify._export_views", lambda m, p, d: (["a", "b", "c", "d"], None))
    out = verify(_FakeModel(), _plan()).report()
    assert "VERDICT: OK" in out
    assert "三视图 4/4" in out


# ── 真机读数函数：m³ → mm³ 的换算（T004 的回归）────────────────────
def test_m3_to_mm3_conversion_is_applied(monkeypatch):
    """★ T004 实测：raw 是 m³。2.0e-06 必须变成 2000 mm³。"""
    class _MP:
        @staticmethod
        def mass_properties(_m):
            return {"volume": 2.0e-06}

    monkeypatch.setitem(__import__("sys").modules, "sw_mass_property", _MP)
    val, err = _read_volume_mm3(_FakeModel())
    assert err is None
    assert val == pytest.approx(2000.0)


def test_bbox_reader_surfaces_error_field(monkeypatch):
    class _FR:
        @staticmethod
        def solid_body_extent_mm(_m):
            return {"ok": False, "error": "GetBodies2 回空"}

    monkeypatch.setitem(__import__("sys").modules, "sw_feature_readback", _FR)
    val, err = _read_bbox(_FakeModel())
    assert val is None
    assert "GetBodies2 回空" in (err or "")
