"""★ EC09 判据 —— 参考解 / 反力平衡 / 网格收敛 / 版本闭合 / 求解成功≠工程通过。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/cae.py`（★ EC09 的实现）
#         `specs/311-ec09-cae-and-topology/spec.md`
# 定位:   ★ EC09 的判据（★ 逐字承计划 §5 EC09 的「验收」）。
# 官方依据: 不适用（本仓的 CAE 可信判据层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不调求解器）
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

from engineering import cae as C


def _ref() -> C.ReferenceSolution:
    """★ 一个**独立**参考解（★ 悬臂梁端部挠度 —— ★ 闭式解）。"""
    v = C.beam_tip_deflection_reference(force_n=100.0, length_m=0.200,
                                        e_pa=210e9, i_m4=1.0e-9)
    return C.ReferenceSolution(name="tip_deflection", value=v, unit="m",
                               source="★ 材料力学闭式解 δ = FL³/(3EI)")


# ══════════════════════════════════════════════════════════════════════
# V1 · 参考解
# ══════════════════════════════════════════════════════════════════════

def test_v1_beam_reference_matches_closed_form():
    """★★★★ V1：★ **参考解与闭式解一致**（★ 独立复算 —— ★ 不共享被测实现）。"""
    got = C.beam_tip_deflection_reference(100.0, 0.200, 210e9, 1.0e-9)
    expected = 100.0 * 0.200 ** 3 / (3.0 * 210e9 * 1.0e-9)     #: ★ 手写
    assert abs(got - expected) < 1e-18, "★ 挠度参考解不符：%r vs %r" % (got, expected)
    #: ★ 弯曲应力
    s = C.beam_bending_stress_reference(50.0, 0.005, 1.0e-9)
    assert abs(s - 50.0 * 0.005 / 1.0e-9) < 1e-3, "★ 应力参考解不符"


def test_v1_reference_from_solver_is_not_usable():
    """★★★★★ V1：★ **取自求解器的「参考解」不算**（★ 那是**自己验自己**）。

    ★★ 依据（★ 验收逐字）：★「★ **参考解**……」+ ★ 承 EC00 的双盲纪律：
      ★「★★ **`tolerance_source` 不得取自被测实现**」。
    """
    r = C.ReferenceSolution(name="x", value=1.0, source="★ 从求解器读的",
                            independent=False)
    out = r.is_usable()
    assert out["ok"] is False, "★★★ 不独立的「参考解」被当成可用 ⇒ ★ 自己验自己"
    assert "不独立" in out["reason"]


def test_v1_reference_without_source_is_not_usable():
    """★★ V1：★ **参考解必须有来源**。"""
    r = C.ReferenceSolution(name="x", value=1.0, source="")
    assert r.is_usable()["ok"] is False
    #: ★ 非有限值也不行
    r2 = C.ReferenceSolution(name="x", value=float("nan"), source="★ 闭式解")
    assert r2.is_usable()["ok"] is False


# ══════════════════════════════════════════════════════════════════════
# V2 · 反力平衡
# ══════════════════════════════════════════════════════════════════════

def test_v2_balanced_reactions_pass():
    """★★★ V2：★ **反力合计 = 外载 ⇒ 通过**（★ 逐字承验收）。"""
    b = C.ReactionBalance(applied_n=100.0, reactions_n=[60.0, 40.0])
    out = b.verdict()
    assert out["ok"] is True, "★ 平衡却判失败：%r" % out
    assert out["relative_error"] < 1e-12


def test_v2_unbalanced_reactions_fail():
    """★★★★ V2：★ **不平衡 ⇒ 不通过**（★ 那是**离散错误**或**边界设错**）。"""
    b = C.ReactionBalance(applied_n=100.0, reactions_n=[60.0, 30.0])
    out = b.verdict()
    assert out["ok"] is False, "★★ 反力 90 ≠ 外载 100 却判平衡"
    assert out["relative_error"] > 0.05


def test_v2_zero_load_is_not_balanced():
    """★★★★ V2：★ **外载为 0 ⇒ 不能判「平衡」**（★ 那是**没信息**不是**平衡**）。"""
    b = C.ReactionBalance(applied_n=0.0, reactions_n=[0.0])
    out = b.verdict()
    assert out["ok"] is False, "★★ 零载荷被判「平衡」"
    assert "不是「平衡」" in out["reason"]


# ══════════════════════════════════════════════════════════════════════
# V3 · 网格收敛
# ══════════════════════════════════════════════════════════════════════

def test_v3_convergence_requires_at_least_three_levels():
    """★★★★ V3：★ **至少三档**（★ 逐字承 EC09-T04）。"""
    two = C.MeshConvergence(levels=[1.00, 1.01], quantity="max_von_mises")
    out = two.verdict()
    assert out["ok"] is False, "★★ 只有两档却判收敛"
    assert out["verdict"] == "insufficient_levels"
    assert "不足三档" in out["reason"]


def test_v3_converged_series_passes():
    """★★★ V3：★ **收敛序列 ⇒ 通过**（★ 相邻变化逐档变小）。"""
    m = C.MeshConvergence(levels=[1.000, 1.020, 1.025], quantity="max_von_mises",
                          rel_tol=0.05)
    out = m.verdict()
    assert out["ok"] is True, "★ 收敛却判失败：%r" % out
    assert out["verdict"] == "converged"


def test_v3_peak_chasing_is_rejected():
    """★★★★★ V3：★ **追峰 ⇒ 拒**（★ 逐字承 EC09-T04：

    「★ **奇异峰值不能单纯细化网格追峰**」）。

    ★★ 判据：★ 关注量**单调上升**且**变化率没降** ⇒ ★ 疑似**奇异点** ✗
    """
    m = C.MeshConvergence(levels=[1.0, 1.5, 2.4], quantity="max_von_mises")
    out = m.verdict()
    assert out["ok"] is False, "★★★ 一直涨的序列被判收敛 ⇒ ★ 那是在追奇异峰"
    assert out["verdict"] == "peak_chasing", "★ 结论应是 peak_chasing：%r" % out["verdict"]
    assert "追峰" in out["reason"], "★ 原因没点明「不能追峰」"


def test_v3_not_converged_is_reported():
    """★★ V3：★ **没收敛 ⇒ 报出来**（★ 不假装收敛）。"""
    m = C.MeshConvergence(levels=[1.00, 1.10, 1.30], quantity="x", rel_tol=0.05)
    out = m.verdict()
    assert out["ok"] is False
    assert out["verdict"] in ("not_converged", "peak_chasing")


# ══════════════════════════════════════════════════════════════════════
# V4 · 版本闭合
# ══════════════════════════════════════════════════════════════════════

def test_v4_closed_versions_pass():
    """★★★ V4：★ **材料/载荷/几何三对都闭合 ⇒ 通过**（★ 逐字承验收）。"""
    c = C.VersionClosure(material_ref="m1", material_used="m1",
                         load_ref="L1", load_used="L1",
                         geometry_ref="g1", geometry_used="g1")
    assert c.verdict()["ok"] is True


@pytest.mark.parametrize("kw", [
    {"material_used": "m2"},      #: ★ 材料换了
    {"load_used": "L2"},          #: ★ 载荷换了
    {"geometry_used": "g2"},      #: ★ 几何换了
])
def test_v4_open_version_pair_fails(kw):
    """★★★★ V4：★ **任何一对不闭合 ⇒ 不通过**（★ 结论不能绑到这个模型）。"""
    base = dict(material_ref="m1", material_used="m1", load_ref="L1", load_used="L1",
                geometry_ref="g1", geometry_used="g1")
    base.update(kw)
    out = C.VersionClosure(**base).verdict()
    assert out["ok"] is False, "★★ %r 未闭合却判通过" % kw
    assert out["open"], "★ 没报出哪一对没闭合"


def test_v4_empty_reference_is_open():
    """★★ V4：★ **空引用 ⇒ 算未闭合**（★ 不能「没记 = 没变」）。"""
    c = C.VersionClosure(material_ref="", material_used="m1",
                         load_ref="L1", load_used="L1",
                         geometry_ref="g1", geometry_used="g1")
    assert c.verdict()["ok"] is False


# ══════════════════════════════════════════════════════════════════════
# V5 · 求解成功 ≠ 工程通过
# ══════════════════════════════════════════════════════════════════════

def test_v5_solved_alone_is_not_engineering_pass():
    """★★★★★ V5：★ **求解成功 ≠ 工程通过**（★ 验收核心）。

    ★★★ **判据**：★ 求解器回 `solved`，★ 而**参考解/平衡/收敛/闭合任一缺失**
      ⇒ ★ `engineering_pass` **必须是 `False`** ✓
    """
    out = C.engineering_verdict(solve_status=C.SolveStatus.SOLVED, reference=None,
                                balance=None, convergence=None, closure=None,
                                validation=None)
    assert out["solved"] is True, "★ 求解状态该是 solved"
    assert out["engineering_pass"] is False, (
        "★★★ 求解成功就判「工程通过」⇒ ★ 违反验收「求解成功不是工程通过」")
    assert out["gates"]["solve"]["note"], "★ 没写明「求解成功只是入场券」"
    #: ★★ 失败的**门**要具名
    assert "reference" in out["reason"] or "balance" in out["reason"]


def test_v5_all_gates_pass_gives_engineering_pass():
    """★★★ V5：★ **六道门全过 ⇒ 工程通过**（★ 不是一律拒）。"""
    out = C.engineering_verdict(
        solve_status=C.SolveStatus.SOLVED, reference=_ref(),
        balance=C.ReactionBalance(applied_n=100.0, reactions_n=[100.0]),
        convergence=C.MeshConvergence(levels=[1.0, 1.02, 1.025], quantity="d",
                                      rel_tol=0.05),
        closure=C.VersionClosure(material_ref="m1", material_used="m1",
                                 load_ref="L1", load_used="L1",
                                 geometry_ref="g1", geometry_used="g1"),
        validation=C.ValidationScope(verification_done=True))
    assert out["engineering_pass"] is True, "★ 全过却判失败：%r" % out["reason"]


def test_v5_optimization_without_reanalysis_fails():
    """★★★★ V5：★ **优化后没复分析 ⇒ 不通过**（★ 逐字承 EC09-T07：

    「★ **拓扑结果重构为可制造设计后重新分析**，★ **不把云图直接交制造**」）。
    """
    out = C.engineering_verdict(
        solve_status=C.SolveStatus.SOLVED, reference=_ref(),
        balance=C.ReactionBalance(applied_n=100.0, reactions_n=[100.0]),
        convergence=C.MeshConvergence(levels=[1.0, 1.02, 1.025], quantity="d"),
        closure=C.VersionClosure(material_ref="m1", material_used="m1",
                                 load_ref="L1", load_used="L1",
                                 geometry_ref="g1", geometry_used="g1"),
        validation=C.ValidationScope(verification_done=True),
        reanalyzed_after_optimization=False)
    assert out["engineering_pass"] is False, "★★ 优化后没复分析却判通过"
    assert out["gates"]["reanalysis"]["ok"] is False
    assert "复分析" in out["gates"]["reanalysis"]["reason"]


def test_v5_not_run_solve_fails_even_with_everything_else():
    """★★ V5：★ **求解没跑 ⇒ 必然不通过**（★ 别的齐也没用）。"""
    out = C.engineering_verdict(
        solve_status=C.SolveStatus.NOT_RUN, reference=_ref(),
        balance=C.ReactionBalance(applied_n=100.0, reactions_n=[100.0]),
        convergence=C.MeshConvergence(levels=[1.0, 1.02, 1.025], quantity="d"),
        closure=C.VersionClosure(material_ref="m1", material_used="m1",
                                 load_ref="L1", load_used="L1",
                                 geometry_ref="g1", geometry_used="g1"),
        validation=C.ValidationScope(verification_done=True))
    assert out["engineering_pass"] is False


# ══════════════════════════════════════════════════════════════════════
# V6 · 没有 validation 证据不写「真实工况已验证」
# ══════════════════════════════════════════════════════════════════════

def test_v6_no_validation_evidence_forbids_the_claim():
    """★★★★★ V6：★ **没有 validation 证据 ⇒ 不写「真实工况已验证」**（★ 验收核心）。"""
    s = C.ValidationScope(verification_done=True, validation_evidence=[])
    out = s.may_claim_real_condition_validated()
    assert out["claim_allowed"] is False, (
        "★★★ 只有计算验证（verification）就允许写「真实工况已验证」⇒ ★ 违反验收")
    assert "不写" in out["reason"]
    #: ★★ 但要**说明**只能写「验证范围」
    assert "验证范围" in out["reason"]


def test_v6_with_validation_evidence_the_claim_is_allowed():
    """★★ V6：★ **有物理验证证据 ⇒ 可以写**（★ 且列出证据）。"""
    s = C.ValidationScope(verification_done=True,
                          validation_evidence=["★ 与应变片实测对照（★ 偏差 4%）"])
    out = s.may_claim_real_condition_validated()
    assert out["claim_allowed"] is True
    assert out["evidence"], "★ 没列出证据"


def test_v6_three_kinds_are_separated():
    """★★★ V6：★ **verification / validation / uncertainty 必须分开**（★ EC09-T05 逐字）。"""
    assert set(C.VerificationKind.ALL) == {"verification", "validation", "uncertainty"}, (
        "★ 三类没分齐：%r" % (C.VerificationKind.ALL,))


def test_v6_engineering_pass_does_not_imply_the_claim():
    """★★★★★ V6：★ **工程通过 ≠ 可以写「真实工况已验证」**（★ 两件事分开）。

    ★★ 依据（★ 验收逐字）：★「★ **没有 validation 证据不写「真实工况已验证」**」——
      ★★ 它管的是**措辞**，★ **不是**「能不能通过」✓
    """
    out = C.engineering_verdict(
        solve_status=C.SolveStatus.SOLVED, reference=_ref(),
        balance=C.ReactionBalance(applied_n=100.0, reactions_n=[100.0]),
        convergence=C.MeshConvergence(levels=[1.0, 1.02, 1.025], quantity="d"),
        closure=C.VersionClosure(material_ref="m1", material_used="m1",
                                 load_ref="L1", load_used="L1",
                                 geometry_ref="g1", geometry_used="g1"),
        validation=C.ValidationScope(verification_done=True))     #: ★ 无物理验证
    assert out["engineering_pass"] is True, "★ 六门全过该通过"
    assert out["may_claim_real_condition_validated"] is False, (
        "★★★ 工程通过就允许写「真实工况已验证」⇒ ★ 两件事没分开")
    assert "不写" in out["validation_note"]


# ══════════════════════════════════════════════════════════════════════
# V7 · AnalysisIR 完整性
# ══════════════════════════════════════════════════════════════════════

def test_v7_incomplete_analysis_ir_is_reported():
    """★★★★ V7：★ **缺条件不能以默认值求解后「通过」**（★ 逐字承 EC09-T03）。"""
    ir = C.AnalysisIR(material="Q235")          #: ★ 只给一项
    out = ir.completeness()
    assert out["ok"] is False
    assert set(out["missing"]) >= {"geometry_simplification", "constitutive",
                                   "target_quantity", "applicability",
                                   "loads", "boundaries"}
    assert "默认值" in out["reason"], "★ 原因没点明「不得以默认值求解后通过」"


def test_v7_complete_analysis_ir_passes():
    """★★ V7：★ **八项齐 ⇒ 完整**。"""
    ir = C.AnalysisIR(
        geometry_simplification="★ 忽略 R2 以下圆角", material="Q235",
        constitutive="★ 线弹性各向同性", loads=[{"kind": "force", "value": 100.0}],
        boundaries=[{"kind": "fixed", "face": "F1"}], contacts=[],
        target_quantity="max_von_mises", applicability="★ 静力线性小变形")
    out = ir.completeness()
    assert out["ok"] is True, "★ 齐全却判不完整：%r" % out


# ══════════════════════════════════════════════════════════════════════
# V8 · 求解状态
# ══════════════════════════════════════════════════════════════════════

def test_v8_four_solve_states_exist():
    """★★ V8：★ **四个求解状态必须齐**。"""
    assert set(C.SolveStatus.ALL) == {"solved", "not_run", "failed", "diverged"}, (
        "★ 状态不齐：%r" % (C.SolveStatus.ALL,))


def test_v8_diverged_is_not_solved():
    """★★★ V8：★ **`diverged` ≠ `solved`**（★ 不能混）。"""
    out = C.engineering_verdict(solve_status=C.SolveStatus.DIVERGED, reference=_ref(),
                                balance=C.ReactionBalance(100.0, [100.0]),
                                convergence=C.MeshConvergence([1.0, 1.02, 1.025], quantity="d"),
                                closure=C.VersionClosure("m1", "m1", "L1", "L1", "g1", "g1"),
                                validation=None)
    assert out["solved"] is False
    assert out["engineering_pass"] is False
