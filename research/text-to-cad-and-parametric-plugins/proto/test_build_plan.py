"""M0 契约测试：FeaturePlan 是纯数据，必须能在没有 SolidWorks 的机器上验证。

# ── 来源 ─────────────────────────────────────────────────────────────
# ★★ 2026-11-07 业主令：折线齿轮生成器 plan_spur_gear 已删除。
#    本测试改为覆盖轴族 plan_shaft（Revolve，真直线半剖轮廓）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math

import pytest

from build_plan import (Expected, Extrude, FeaturePlan, Line, Revolve,
                        plan_shaft, render_plan)
from shaft_method import ShaftRequest


def _shaft_req(**over) -> ShaftRequest:
    base = dict(torque_nm=120.0, length_mm=300.0)
    base.update(over)
    return ShaftRequest(**base)


def test_plan_has_no_solidworks_dependency():
    """计划层不导入任何 COM 相关模块。"""
    import sys
    plan_shaft(_shaft_req())
    assert not any(m.startswith("win32com") for m in sys.modules)


def test_entities_are_metric_not_metres():
    """★ 归档实现曾在米/毫米之间出过 1000× 事故：计划内坐标必须落在毫米量级。"""
    p = plan_shaft(_shaft_req())
    coords = [c for e in p.sketch_entities if isinstance(e, Line)
              for c in (e.x1_mm, e.y1_mm, e.x2_mm, e.y2_mm)]
    assert max(coords) > 1.0, "坐标过小，可能仍是米（1000× 事故）"
    assert max(coords) < 1000.0, "坐标过大，可能被误乘"


def test_revolve_feature_has_axis_entities():
    """Revolve 计划的轴线必须独占 axis_entities。"""
    p = plan_shaft(_shaft_req())
    assert isinstance(p.features[0], Revolve)
    assert p.axis_entities and isinstance(p.axis_entities[0], Line)


def test_bbox_matches_shaft_geometry():
    """d2=40, L=300 ⇒ 包围盒 40×300×40。"""
    p = plan_shaft(_shaft_req())
    assert abs(p.expected.bbox_x_mm - 40.0) < 0.01
    assert abs(p.expected.bbox_y_mm - 300.0) < 0.01
    assert abs(p.expected.bbox_z_mm - 40.0) < 0.01


def test_expected_volume_is_analytic_cylinder_sum():
    """体积判据要能复算：π·r1²·L1 + π·r2²·L2。"""
    p = plan_shaft(_shaft_req())
    d1, d2, L = 28.0, 40.0, 300.0
    L1 = L * 0.4
    L2 = L - L1
    vol = math.pi * (d1 / 2) ** 2 * L1 + math.pi * (d2 / 2) ** 2 * L2
    assert abs(p.expected.volume_mm3 - vol) < 1e-6


def test_unstepped_shaft_uses_one_cylinder():
    p = plan_shaft(_shaft_req(stepped=False))
    vol = math.pi * (28.0 / 2) ** 2 * 300.0
    assert abs(p.expected.volume_mm3 - vol) < 1e-6


def test_plan_refuses_invalid_request():
    with pytest.raises(ValueError):
        plan_shaft(_shaft_req(torque_nm=-1.0))


def test_render_is_human_readable():
    out = render_plan(plan_shaft(_shaft_req()))
    assert "预期体积" in out and "预期包围盒" in out and "旋转" in out


def test_minimal_synthetic_plan_still_checkable():
    """正方形拉伸计划（真直线）仍可用 —— 证明删的只是折线拟合，不是直线原语。"""
    p = FeaturePlan(
        name="T", units="mm",
        sketch_entities=[
            Line(2.0, 2.0, 10.0, 2.0), Line(10.0, 2.0, 10.0, 10.0),
            Line(10.0, 10.0, 2.0, 10.0), Line(2.0, 10.0, 2.0, 2.0),
        ],
        features=[Extrude(depth_mm=5.0)],
        expected=Expected(volume_mm3=320.0, bbox_x_mm=8.0, bbox_y_mm=8.0, bbox_z_mm=5.0),
        provenance={"profile_form": "test"},
    )
    assert abs(p.to_meters()["depth_m"] - 0.005) < 1e-12
