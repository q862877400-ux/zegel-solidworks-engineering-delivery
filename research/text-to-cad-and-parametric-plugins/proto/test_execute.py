"""execute.py 契约测试 —— 全部离线，不碰 COM。

守的是 contracts/execute.contract.md 的 §前置条件 与 §失败契约。
"""
from __future__ import annotations

import json

import pytest

from build_plan import Circle, Expected, Extrude, FeaturePlan, Line
from execute import COORD_MAX, COORD_MIN, ExecuteError, check_plan, write_failure
from shaft_method import ShaftRequest
from build_plan import plan_shaft


def _mk_plan(**over) -> FeaturePlan:
    """造一个最小合法计划，可逐字段覆盖。"""
    base = dict(
        name="T",
        units="mm",
        sketch_entities=[
            Line(2.0, 2.0, 10.0, 2.0),
            Line(10.0, 2.0, 10.0, 10.0),
            Line(10.0, 10.0, 2.0, 10.0),
            Line(2.0, 10.0, 2.0, 2.0),
        ],
        features=[Extrude(depth_mm=5.0)],
        expected=Expected(volume_mm3=320.0, bbox_x_mm=8.0, bbox_y_mm=8.0, bbox_z_mm=5.0),
        provenance={"profile_form": "test"},
    )
    base.update(over)
    return FeaturePlan(**base)


# ── 前置条件（契约 §前置条件 1–4）────────────────────────────────────
def test_valid_plan_passes_check():
    check_plan(_mk_plan())  # 不抛即过


def test_units_must_be_mm():
    with pytest.raises(ValueError, match="units 必须是 'mm'"):
        check_plan(_mk_plan(units="m"))


def test_empty_entities_rejected():
    with pytest.raises(ValueError, match="sketch_entities 为空"):
        check_plan(_mk_plan(sketch_entities=[]))


def test_empty_features_rejected():
    with pytest.raises(ValueError, match="features 为空"):
        check_plan(_mk_plan(features=[]))


def test_first_feature_must_be_extrude():
    with pytest.raises(ValueError, match="必须是 Extrude"):
        check_plan(_mk_plan(features=[object()]))


def test_coordinates_too_small_rejected():
    """★ 防 1000× 事故：米制坐标（0.01）必须被拦。"""
    plan = _mk_plan(sketch_entities=[Line(0.01, 0.01, 0.02, 0.02)])
    with pytest.raises(ValueError, match="坐标量级异常"):
        check_plan(plan)


def test_coordinates_too_large_rejected():
    plan = _mk_plan(sketch_entities=[Line(5000.0, 0.0, 5000.0, 1.0)])
    with pytest.raises(ValueError, match="坐标量级异常"):
        check_plan(plan)


def test_circle_radius_also_checked():
    """★ 米制误传的指纹：圆半径 0.005（=5 mm 误当米）会被拦。"""
    plan = _mk_plan(sketch_entities=[Circle(0.0, 0.0, 0.005)])
    with pytest.raises(ValueError, match="坐标量级异常"):
        check_plan(plan)


def test_coord_window_boundaries():
    """边界：全局最大 |c| == COORD_MIN 与 COORD_MAX 都应通过；略超应拒绝。"""
    # 恰好等于上限
    check_plan(_mk_plan(sketch_entities=[Line(COORD_MIN, COORD_MIN, COORD_MAX, COORD_MAX)]))
    # 恰好等于下限（整条线都在 1.0 附近）
    check_plan(_mk_plan(sketch_entities=[Line(COORD_MIN, COORD_MIN, COORD_MIN, COORD_MIN)]))
    # 上限被突破
    with pytest.raises(ValueError):
        check_plan(_mk_plan(sketch_entities=[Line(1.0, 1.0, COORD_MAX * 1.01, 5.0)]))
    # 下限被突破（全局最大仍小于 1.0）
    with pytest.raises(ValueError):
        check_plan(_mk_plan(sketch_entities=[Line(0.5, 0.5, COORD_MIN * 0.99, 0.9)]))


def test_negative_coords_allowed():
    """★ 回归：真实齿轮轮廓会穿到负坐标（实测 -0.816），必须放行。"""
    check_plan(_mk_plan(sketch_entities=[
        Line(-0.816, -0.816, 10.0, -0.876),
        Line(-0.876, -0.876, -0.878, 10.0),
    ]))


def test_real_shaft_plan_passes_check():
    """真实轴族计划必须通过 —— 否则后面真机跑不起来。"""
    check_plan(plan_shaft(ShaftRequest(torque_nm=120.0, length_mm=300.0)))


# ── 失败留证（契约 §失败契约）───────────────────────────────────────
def test_failure_record_written(tmp_path, monkeypatch):
    import execute as ex
    monkeypatch.setattr(ex, "FAIL_DIR", tmp_path)

    plan = _mk_plan()
    exc = ExecuteError("boom", stage="sketch", plan=plan)
    p = write_failure(exc, plan, stage="sketch")

    assert p.exists()
    rec = json.loads(p.read_text(encoding="utf-8"))
    for k in ("plan_name", "plan_snapshot", "exception_type", "exception_message",
              "stage", "traceback", "screenshot", "timestamp"):
        assert k in rec, f"FailureRecord 缺字段 {k}"
    assert rec["exception_type"] == "ExecuteError"
    assert rec["stage"] == "sketch"
    assert rec["screenshot"] is None  # 未指定时不编造


def test_failure_record_survives_none_plan(tmp_path, monkeypatch):
    """plan 为 None 时也要能落盘（不崩）。"""
    import execute as ex
    monkeypatch.setattr(ex, "FAIL_DIR", tmp_path)
    p = write_failure(RuntimeError("x"), None, stage="newdoc")
    rec = json.loads(p.read_text(encoding="utf-8"))
    assert rec["plan_name"] is None
    assert rec["plan_snapshot"] is None
