"""★ EC09 T06 判据 —— **设计敏感性扫描** + 不可改域冻结。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/cae.py`（★ `SensitivityScan` · `beam_stress_under_load`）
#         `specs/311-ec09-cae-and-topology/spec.md`（★ EC09-T06）
# 定位:   ★ EC09 **T06**（★ 逐字：★「★ **设计敏感性和保守边界**；★ 优化输入/**不可改域**/
#         ★ 制造约束冻结」）。
# 官方依据: 不适用（本仓的 CAE 可信判据层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不调求解器）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import cae as C


def _scan(**kw) -> C.SensitivityScan:
    base = dict(
        #: ★★ 两个参数：★ `moment` 变化 50% ⇒ 应力变化 50%（★ 线性）；★ `c` 变化 100% ⇒ 100%
        perturbations={
            "moment_nm": [(50.0, 2.5e8), (75.0, 3.75e8)],
            "c_m": [(0.005, 2.5e8), (0.010, 5.0e8)],
        },
        frozen_domains=["★ 安装孔位（★ 由装配决定，不可改）"],
        manufacturing_constraints=["★ 最小壁厚 ≥ 2 mm"],
    )
    base.update(kw)
    return C.SensitivityScan(**base)


def test_t06_sensitivity_ranks_parameters():
    """★★★★ T06：★ **敏感性要排序**（★ 接手方才知道**先改哪个**）。"""
    s = _scan()
    out = s.sensitivity()
    assert out["ok"] is True, "★ 算不出敏感性：%r" % out
    assert out["ranked"], "★ 没有排序结果"
    assert out["most_sensitive"] in ("moment_nm", "c_m")
    #: ★★ 降序
    norms = [r["normalized"] for r in out["ranked"]]
    assert norms == sorted(norms, reverse=True), "★★ 没按敏感性降序"


def test_t06_single_point_parameter_is_not_scanable():
    """★★★ T06：★ **只有一个点的参数 ⇒ 算不出敏感性**（★ 不能凭一个点说话）。"""
    s = _scan(perturbations={"only_one": [(1.0, 1.0)]})
    out = s.sensitivity()
    assert out["ok"] is False, "★★ 单点参数被算出了敏感性"
    assert "≥2 个扰动点" in out["reason"] or "2 个扰动点" in out["reason"]


def test_t06_unfrozen_domain_blocks():
    """★★★★ T06：★ **不可改域没冻结 ⇒ 不通过**（★ 逐字承 EC09-T06）。"""
    s = _scan(frozen_domains=[])
    out = s.verdict()
    assert out["ok"] is False, "★★ 不可改域没冻结却判通过"
    assert "不可改域" in out["reason"]


def test_t06_full_scan_with_frozen_domain_passes():
    """★★ T06：★ **敏感性可算 + 不可改域已冻结 ⇒ 通过**。"""
    out = _scan().verdict()
    assert out["ok"] is True, "★ 齐全却判失败：%r" % out
    assert out["frozen_domains"], "★ 没带出冻结的域"
    assert out["manufacturing_constraints"], "★ 没带出制造约束"


def test_t06_sensitivity_is_computed_from_the_closed_form():
    """★★★ T06：★ 敏感性**从闭式解算**（★ 独立于求解器 —— ★ 与 V1 同族）。"""
    #: ★ 应力 ∝ M ⇒ 归一化敏感性 = 1.0（★ 精确）
    stress_50 = C.beam_stress_under_load(50.0, 0.005, 1.0e-9)
    stress_75 = C.beam_stress_under_load(75.0, 0.005, 1.0e-9)
    assert abs(stress_75 / stress_50 - 1.5) < 1e-9, "★ 线性关系不符（★ 闭式解应严格线性）"
    s = C.SensitivityScan(perturbations={"moment_nm": [(50.0, stress_50),
                                                       (75.0, stress_75)]},
                          frozen_domains=["★ 孔位"])
    ranked = s.sensitivity()["ranked"]
    assert abs(ranked[0]["normalized"] - 1.0) < 1e-9, (
        "★ 线性参数的归一化敏感性应为 1.0：%r" % ranked[0])


def test_t06_most_sensitive_is_named_not_guessed():
    """★★ T06：★ **最敏感的参数要具名**（★ 不是「都差不多」）。"""
    s = C.SensitivityScan(
        perturbations={
            #: ★ `c` 的归一化敏感性 = 1.0；★ `moment` 的也 = 1.0 ⇒ 并列
            "c_m": [(0.005, 2.5e8), (0.010, 5.0e8)],
            #: ★ `i` 翻倍 ⇒ 应力减半 ⇒ 归一化 |−0.5|×... ⇒ 明显
            "i_m4": [(1.0e-9, 2.5e8), (2.0e-9, 1.25e8)],
        },
        frozen_domains=["★ 孔位"])
    out = s.sensitivity()
    assert out["most_sensitive"] in ("c_m", "i_m4"), "★ 没给出最敏感参数"
    #: ★★ 每条都要有点数
    assert all(r["points"] >= 2 for r in out["ranked"])
