"""★ EC08 判据（四个子域）—— 工程图 / 钣金 / 焊件 / 曲面。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/processes.py`（★ EC08 的实现）
#         `specs/310-ec08-drawing-and-processes/spec.md`
# 定位:   ★ EC08 的判据（★ 逐字承计划 §5 EC08 的四个子域与验收）。
# 官方依据: 不适用（本仓的制图与工艺层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from engineering import processes as P


# ══════════════════════════════════════════════════════════════════════
# EC08A · 工程图
# ══════════════════════════════════════════════════════════════════════

def test_a_eight_annotation_kinds_exist():
    """★★ EC08A：★ **八类标注必须齐**（★ 逐字承 EC08A）。"""
    assert set(P.AnnotationKind.ALL) == {
        "dimension", "datum", "fit", "tolerance", "material",
        "tech_requirement", "bom", "version"}, "★ 八类不齐：%r" % (P.AnnotationKind.ALL,)


def test_a_dangling_annotation_is_detected():
    """★★★★★ EC08A：★ **悬空标注检测**（★ 逐字承验收）。

    ★★ 判据：★ 标注**没有指回几何** ⇒ ★ **悬空**。
    """
    r = P.DanglingReport(annotations=[
        P.Annotation(P.AnnotationKind.DIMENSION, "★ 板厚 10", target="feat:板厚"),
        P.Annotation(P.AnnotationKind.TOLERANCE, "★ ±0.05"),          #: ★ 悬空
    ])
    out = r.verdict()
    assert out["ok"] is False, "★★ 悬空标注**没检出** ⇒ ★ 违反验收"
    assert out["count"] == 1
    assert out["dangling"][0]["kind"] == P.AnnotationKind.TOLERANCE, "★ 没点名哪条悬空"


def test_a_no_dangling_passes():
    """★★ EC08A 负例：★ **全部有指向 ⇒ 通过**。"""
    r = P.DanglingReport(annotations=[
        P.Annotation(P.AnnotationKind.DIMENSION, "★ 10", target="feat:1"),
        P.Annotation(P.AnnotationKind.DATUM, "★ A", target="face:2"),
    ])
    assert r.verdict()["ok"] is True


def test_a_whitespace_target_is_dangling():
    """★★ EC08A：★ **只有空白的 `target` ⇒ 仍算悬空**（★ 不能靠空格蒙混）。"""
    a = P.Annotation(P.AnnotationKind.DIMENSION, "★ 10", target="   ")
    assert a.is_dangling() is True


def test_a_drawing_evidence_requires_readback_for_each():
    """★★★★★ EC08A：★ **尺寸/基准/公差/配置版本都能回读比对**（★ 逐字承验收）。

    ★★ 判据：★ ① 三类**都要有**；★ ② 每项**都要有回读值**；★ ③ **配置+版本都要绑**。
    """
    ev = P.DrawingEvidence(model_config="默认", model_revision="m1")
    ev.add(P.AnnotationKind.DIMENSION, nominal=0.010, readback=0.010, tol=0.0001)
    ev.add(P.AnnotationKind.DATUM, nominal="A", readback="A")
    ev.add(P.AnnotationKind.TOLERANCE, nominal=0.05, readback=0.05, tol=0.001)
    out = ev.verdict()
    assert out["ok"] is True, "★ 齐全却判失败：%r" % out
    assert out["version_bound"] is True
    #: ★★★ **必须带免责声明**
    assert out["mark"] == P.NOT_A_SAFETY_COMPLIANCE_STATEMENT, (
        "★★★ 工程图证据没带「不代表整机安全合规」⇒ ★ 违反验收")


def test_a_missing_readback_blocks():
    """★★★ EC08A：★ **缺回读 ⇒ 不通过**（★ 「回读比对」的前提是有回读）。"""
    ev = P.DrawingEvidence(model_config="默认", model_revision="m1")
    ev.add(P.AnnotationKind.DIMENSION, nominal=0.010, readback=None)
    ev.add(P.AnnotationKind.DATUM, nominal="A", readback="A")
    ev.add(P.AnnotationKind.TOLERANCE, nominal=0.05, readback=0.05)
    out = ev.verdict()
    assert out["ok"] is False, "★★ 缺回读却判通过"
    assert out["no_readback"] == [P.AnnotationKind.DIMENSION]


def test_a_mismatch_beyond_tolerance_blocks():
    """★★★ EC08A：★ **超差 ⇒ 不通过**（★ 且给前后值）。"""
    ev = P.DrawingEvidence(model_config="默认", model_revision="m1")
    ev.add(P.AnnotationKind.DIMENSION, nominal=0.010, readback=0.012, tol=0.0001)
    ev.add(P.AnnotationKind.DATUM, nominal="A", readback="A")
    ev.add(P.AnnotationKind.TOLERANCE, nominal=0.05, readback=0.05)
    out = ev.verdict()
    assert out["ok"] is False
    assert out["mismatches"][0]["nominal"] == 0.010
    assert out["mismatches"][0]["readback"] == 0.012


def test_a_unbound_version_blocks():
    """★★★★ EC08A：★ **模型配置版本未绑 ⇒ 不通过**（★ 逐字承验收）。"""
    ev = P.DrawingEvidence(model_config="", model_revision="m1")
    ev.add(P.AnnotationKind.DIMENSION, nominal=0.01, readback=0.01)
    ev.add(P.AnnotationKind.DATUM, nominal="A", readback="A")
    ev.add(P.AnnotationKind.TOLERANCE, nominal=0.05, readback=0.05)
    out = ev.verdict()
    assert out["ok"] is False, "★★ 配置版本没绑却判通过"
    assert out["version_bound"] is False


# ══════════════════════════════════════════════════════════════════════
# EC08B · 钣金
# ══════════════════════════════════════════════════════════════════════

def test_b_radius_must_be_at_least_thickness():
    """★★★ EC08B：★ **折弯半径 ≥ 板厚**（★ 工艺下限 —— ★ 与 EC05 的失败域同口径）。"""
    ok = P.SheetMetalSpec(thickness_m=0.002, bend_radius_m=0.002)
    assert ok.radius_is_manufacturable()["ok"] is True, "★ R = t 应可制造"
    bad = P.SheetMetalSpec(thickness_m=0.002, bend_radius_m=0.001)
    out = bad.radius_is_manufacturable()
    assert out["ok"] is False, "★★ R < t 却判可制造"
    assert "小于板厚" in out["reason"]


def test_b_bend_allowance_formula_is_independent():
    """★★★ EC08B：★ **折弯补偿**独立复算（★ 手写 `θ(R + K t)`）。"""
    s = P.SheetMetalSpec(thickness_m=0.002, bend_radius_m=0.003, k_factor=0.44)
    got = s.bend_allowance(90.0)
    expected = math.radians(90.0) * (0.003 + 0.44 * 0.002)
    assert abs(got - expected) < 1e-15, "★ 补偿不符：%r vs %r" % (got, expected)
    #: ★ 负角度按绝对值（★ 折弯方向不影响补偿长度）
    assert abs(s.bend_allowance(-90.0) - expected) < 1e-15


def test_b_unfold_consistency_is_checked():
    """★★★★ EC08B：★ **展开一致性**（★ 逐字承 EC08B）。

    ★★ 判据：★ 展开长 = ★ **直线段 + 折弯补偿**（★ 差 ≤ 1e-6 m）。
    """
    s = P.SheetMetalSpec(thickness_m=0.002, bend_radius_m=0.003, k_factor=0.44,
                         bends=[{"angle_deg": 90.0, "length_m": 0.050},
                                {"angle_deg": 90.0, "length_m": 0.030}])
    straight = 0.050 + 0.030
    allowance = 2 * s.bend_allowance(90.0)
    good = P.unfold_consistency(s, flat_length_m=straight + allowance)
    assert good["ok"] is True, "★ 一致的展开被判失败：%r" % good
    #: ★★ **不一致 ⇒ 报出来**（★ 且给差值）
    bad = P.unfold_consistency(s, flat_length_m=straight)      #: ★ 少了补偿
    assert bad["ok"] is False, "★★ 少了折弯补偿却判一致"
    assert bad["diff_m"] > 0


def test_b_bend_interference_is_detected():
    """★★★★ EC08B：★ **折弯干涉**（★ 逐字承 EC08B）。

    ★★ 判据：★ 法兰净空 ≥ `R + t`（★ 否则折弯刀下不去）。
    """
    s = P.SheetMetalSpec(thickness_m=0.002, bend_radius_m=0.003)
    need = 0.005
    ok = P.bend_interference(s, flange_heights_m=[0.010, 0.020])
    assert ok["ok"] is True, "★ 净空够却判干涉"
    assert abs(ok["required_clearance_m"] - need) < 1e-15
    #: ★★ **不够 ⇒ 报出来**
    bad = P.bend_interference(s, flange_heights_m=[0.010, 0.004])
    assert bad["ok"] is False, "★★ 净空不够却判可折"
    assert bad["interferences"][0]["index"] == 1


# ══════════════════════════════════════════════════════════════════════
# EC08C · 焊件
# ══════════════════════════════════════════════════════════════════════

def test_c_cut_list_aggregates_by_profile():
    """★★★ EC08C：★ **切割清单按型材汇总**（★ 逐字承 EC08C）。"""
    w = P.WeldmentCutList()
    w.add("★ 方管 40×40", length_m=0.500, qty=2, material="Q235")
    w.add("★ 方管 40×40", length_m=0.300, qty=1, material="Q235")
    w.add("★ 角钢 30×30", length_m=0.400, qty=4, material="Q235")
    out = w.totals()
    assert out["ok"] is True
    assert out["profiles"] == 2, "★ 型材数不对：%d" % out["profiles"]
    sq = [r for r in out["by_profile"] if "方管" in r["profile"]][0]
    assert abs(sq["total_length_m"] - (0.500 * 2 + 0.300)) < 1e-12, (
        "★ 同型材没合并：%r" % sq)
    assert sq["qty"] == 3
    assert out["pieces"] == 7


def test_c_empty_cut_list_is_not_ok():
    """★★ EC08C：★ **空切割清单 ⇒ 不算 ok**。"""
    assert P.cut_list_totals([])["ok"] is False


def test_c_weld_accessibility_is_checked():
    """★★★★ EC08C：★ **焊接可达性**（★ 逐字承 EC08C）。"""
    w = P.WeldmentCutList()
    good = w.weld_accessibility(joints=[{"torch_angle_deg": 45},
                                        {"torch_angle_deg": 90}])
    assert good["ok"] is True, "★ 可达却判不可达：%r" % good
    #: ★★ **角度超范围 ⇒ 不可达**
    bad = w.weld_accessibility(joints=[{"torch_angle_deg": 45},
                                       {"torch_angle_deg": 200}])
    assert bad["ok"] is False, "★★ 200° 却判可焊"
    assert bad["unreachable"][0]["index"] == 1


# ══════════════════════════════════════════════════════════════════════
# EC08D · 曲面
# ══════════════════════════════════════════════════════════════════════

def test_d_continuity_requires_the_grade_and_the_tolerance():
    """★★★★★ EC08D：★ **连续性要达等级**且**偏差 ≤ 容差**（★ 逐字承 EC08D）。"""
    s = P.SurfaceContinuity(patches=3, seams=[
        {"between": "s1-s2", "level": "G2", "deviation_mm": 0.01},
        {"between": "s2-s3", "level": "G2", "deviation_mm": 0.02},
    ])
    assert s.continuity_verdict(required="G2", tolerance_mm=0.05)["ok"] is True
    #: ★★ **等级不够 ⇒ 不达标**
    low = P.SurfaceContinuity(patches=2, seams=[
        {"between": "s1-s2", "level": "G1", "deviation_mm": 0.01}])
    assert low.continuity_verdict(required="G2")["ok"] is False, (
        "★★ G1 却当成 G2 达标")
    #: ★★ **偏差超容差 ⇒ 不达标**（★ 即使等级够）
    dev = P.SurfaceContinuity(patches=2, seams=[
        {"between": "s1-s2", "level": "G2", "deviation_mm": 0.5}])
    assert dev.continuity_verdict(required="G2", tolerance_mm=0.05)["ok"] is False, (
        "★★ 偏差 0.5 > 容差 0.05 却达标")


def test_d_no_seams_measured_is_not_ok():
    """★★ EC08D：★ **一条接缝都没量 ⇒ 不算通过**。"""
    assert P.SurfaceContinuity(patches=1).continuity_verdict()["ok"] is False


def test_d_thicken_requires_minimum_thickness():
    """★★ EC08D：★ **厚化要求最小厚度**（★ 逐字承 EC08D）。"""
    s = P.SurfaceContinuity(min_thickness_mm=0.8)
    assert s.thicken_verdict(min_required_mm=0.5)["ok"] is True
    assert s.thicken_verdict(min_required_mm=1.0)["ok"] is False, (
        "★★ 0.8 < 1.0 却判可厚化")


def test_d_eyeballing_is_not_accepted():
    """★★★★★ EC08D：★ **「看起来顺」不能当曲率通过**（★ 逐字承 EC08D）。

    ★★★ **判据**：★ 只给视觉判断、★ **没有量化读数** ⇒ ★ **`unknown`** ✗
    """
    out = P.surface_is_not_eyeballed({"looks_smooth": True})
    assert out["ok"] is False, (
        "★★★ 只凭「看着顺」就通过了 ⇒ ★ 违反 EC08D 逐字")
    assert out["verdict"] == "unknown", "★ 该记 `unknown`"
    assert "看起来顺" in out["reason"], "★ 原因没引那句原话"


def test_d_quantified_surface_evidence_is_accepted():
    """★★ EC08D 负例：★ **有量化读数 ⇒ 可以判**（★ 不是一律拒）。"""
    out = P.surface_is_not_eyeballed({"seams": [{"level": "G2"}],
                                      "max_deviation_mm": 0.02})
    assert out["ok"] is True
    assert out["verdict"] == "quantified"


def test_d_disclaimer_statement_exists():
    """★★★★ EC08D/全局：★ **「制图标准符合不代表整机安全合规」必须落成常量**。"""
    assert "不代表" in P.NOT_A_SAFETY_COMPLIANCE_STATEMENT
    assert "EC11" in P.NOT_A_SAFETY_COMPLIANCE_STATEMENT, (
        "★★ 没指明安全合规由谁判（★ EC11）")
