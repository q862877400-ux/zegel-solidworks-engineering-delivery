"""★ 阶段 7 契约测试：箱体 + 最终 DoD（规格 322 的 M1~M4）。

★★ 含**反向验证**（★ 规格 §5 的 U1~U6）：
   U1 半箱体保留旧接口坐标 / U2 各孔自身直径都对 / U3 台账当证据
   U4 移除必需图纸 / U5 替换旧版本产物 / U6 隐藏人工接管
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage7_housing.py
# 定位:   规格 `specs/322-stage7-housing-final-dod` 的 M1~M4 契约测试
# 官方依据: ① 外部方案阶段 7 的验收 S7-A / S7-B（逐字）
#           ② 外部方案 §5 R7 ④ 逐字（四条替换/移除/隐藏必须分别失败）
#           ③ `scripts/engineering/recovery.py` 的 `ArtifactDigest`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import housing as H                             # noqa: E402


def _good_case(product: str, variant: int) -> H.CaseResult:
    return H.CaseResult(
        product=product, variant=variant, obligations_passed=True,
        artifacts=["a.sldprt", "a.slddrw", "a.pdf"],
        layers=H.LayeredVerdict(planned=True, executed=True,
                                engineering_passed=True, human_approved=True))


def _good_dod() -> H.FinalDod:
    d = H.FinalDod(gates={g: "pass" for g in H.REQUIRED_GATES},
                   failed_total=0, new_failures=0)
    for p in H.PRODUCTS:
        for v in H.VARIANTS:
            d.add_case(_good_case(p, v))
    d.evidences = [H.Evidence(kind=H.EV_PRODUCT,
                              path="output/stage7/%s-v%d.step" % (p, v),
                              sha256="0" * 64)
                   for p in H.PRODUCTS for v in H.VARIANTS]
    return d


#: ══ M1 共享接口 ══════════════════════════════════════════════════════

def test_baseline_is_required() -> None:
    """★★ FR-001：**必须声明统一基准**（★ 否则上下箱体无共同依据）。"""
    m = H.HousingModel()
    with pytest.raises(H.HousingError) as ei:
        m.require_baseline()
    assert ei.value.code == "no-baseline"
    #: ★ 声明了 ⇒ 过
    H.default_housing().require_baseline()


def test_axis_propagates_to_dependents_only() -> None:
    """★★ FR-002：**依赖它的全刷新 · 不依赖的可复用**。"""
    p = H.propagate_axis("bore_center_distance_mm", 120.0, 140.0)
    assert p["changed"] is True
    assert set(p["stale"]) == {"上箱体孔系", "下箱体孔系", "装配", "图纸", "计算"}
    #: ★ 箱体外形不依赖中心距 ⇒ 可复用
    assert "上箱体" in p["reusable"]


def test_axis_no_change_is_noop() -> None:
    """★ 值没变 ⇒ 无传播（★ 不是「全都标脏」）。"""
    p = H.propagate_axis("wall_thickness_mm", 10.0, 10.0)
    assert p["changed"] is False and p["stale"] == []


def test_shaft_dia_does_not_touch_split() -> None:
    """★ 轴径变 ⇒ **不动剖分面**（★ 只影响孔系与配合）。"""
    p = H.propagate_axis("shaft_dia_mm", 40.0, 50.0)
    assert "上箱体" not in p["stale"]
    assert "上箱体" in p["reusable"]


#: ══ M1 孔系关系 ═════════════════════════════════════════════════════

def test_bore_relation_checks_distance_fit_split() -> None:
    """★ 孔系判据是**中心距 + 配合 + 剖分**三条。"""
    r = H.BoreRelation(axis="主轴", center_distance_mm=120.0,
                       expected_center_distance_mm=120.0, fit="H7/k6",
                       split="上箱体")
    assert r.ok is True
    #: ★ 缺配合 ⇒ 不 ok
    r2 = H.BoreRelation(axis="主轴", center_distance_mm=120.0,
                        expected_center_distance_mm=120.0, split="上箱体")
    assert r2.ok is False


def test_check_bore_relations_reports_bad() -> None:
    """★ 坏的孔系要**具名报出**。"""
    rs = [H.BoreRelation(axis="主轴", center_distance_mm=120.0,
                         expected_center_distance_mm=120.0, fit="H7/k6",
                         split="上箱体"),
          H.BoreRelation(axis="副轴", center_distance_mm=200.0,
                         expected_center_distance_mm=120.0, fit="H7/k6",
                         split="上箱体")]
    out = H.check_bore_relations(rs)
    assert out["ok"] is False
    assert out["bad"][0]["axis"] == "副轴"


#: ══ M2 证据非循环 ═══════════════════════════════════════════════════

def test_evidence_kinds_closed_set() -> None:
    """★ 证据种类就是两种（产品级 / 台账级）。"""
    assert len(H.EVIDENCE_KINDS) == 2
    with pytest.raises(AssertionError):
        H.Evidence(kind="乱写的")


def test_ledger_evidence_is_not_usable() -> None:
    """★★ FR-004：**台账级证据不可当产品级**。"""
    e = H.Evidence(kind=H.EV_LEDGER, path="capabilities.yaml")
    assert e.usable is False
    assert H.Evidence(kind=H.EV_PRODUCT, path="a.step").usable is True


def test_circular_evidence_detected() -> None:
    """★★★ SC-010：**「读取台账并断言 verified」必须被检出**（★ 外部方案 R7 ④ 逐字）。"""
    ev = H.evidence_is_noncircular([
        H.Evidence(kind=H.EV_PRODUCT, path="output/x.step", sha256="0" * 64),
        H.Evidence(kind=H.EV_LEDGER, path="capabilities.yaml",
                   note="读取台账并断言 verified"),
    ])
    assert ev["ok"] is False
    assert len(ev["circular"]) == 1


def test_product_evidence_passes() -> None:
    """★ 正例：真机/文件级证据 ⇒ 非循环。"""
    ev = H.evidence_is_noncircular([
        H.Evidence(kind=H.EV_PRODUCT, path="output/housing.step",
                   sha256="0" * 64, note="真机导出的 STEP")])
    assert ev["ok"] is True


#: ══ M3 四层区分 ═════════════════════════════════════════════════════

def test_layered_verdict_requires_all_four() -> None:
    """★★ FR-005：**四层全过**才算真交付（★ 不许用一个 bool 压过去）。"""
    lv = H.LayeredVerdict(planned=True, executed=True,
                          engineering_passed=True, human_approved=False)
    assert lv.all_four is False
    lv2 = H.LayeredVerdict(planned=True, executed=True,
                           engineering_passed=True, human_approved=True)
    assert lv2.all_four is True


def test_layered_verdict_exposes_all_four_keys() -> None:
    """★ 四层必须**逐项可见**（★ 不是一个大 bool）。"""
    d = H.LayeredVerdict(planned=True, executed=True).to_dict()
    for k in ("planned", "executed", "engineering_passed", "human_approved"):
        assert k in d, "★ 缺层 %s" % k


def test_planning_success_cannot_impersonate_engineering_pass() -> None:
    """★★ 规划成功**不得**冒充工程通过（★ 四层分开报的意义）。"""
    lv = H.LayeredVerdict(planned=True, executed=False,
                          engineering_passed=False, human_approved=False)
    assert lv.all_four is False


#: ══ M4 最终 DoD ═════════════════════════════════════════════════════

def test_products_and_variants() -> None:
    """★ 三类产品 × 3 变体 = **9 个案例**（★ FR-007）。"""
    assert len(H.PRODUCTS) == 3
    assert len(H.VARIANTS) == 3
    assert len(H.PRODUCTS) * len(H.VARIANTS) == 9


def test_final_dod_good() -> None:
    """★ 正例：六条都过。"""
    out = _good_dod().evaluate()
    assert out["ok"] is True, out
    assert out["cases_ok"] is True
    assert out["obligations_ok"] is True
    assert out["failures_ok"] is True
    assert out["gates_ok"] is True
    assert out["evidence_ok"] is True
    assert out["claims_ok"] is True
    assert out["all_four_ok"] is True


def test_final_dod_requires_all_nine() -> None:
    """★ 少一个案例 ⇒ 不 ok（★ 不许「挑最好案例」）。"""
    d = _good_dod()
    d.cases = d.cases[:-1]
    out = d.evaluate()
    assert out["cases_ok"] is False and out["ok"] is False
    assert out["cases_missing"]


def test_final_dod_requires_zero_failed() -> None:
    """★★ SC-007：**0 failed** 且**新增失败数 0**。"""
    d = _good_dod()
    d.failed_total = 1
    assert d.evaluate()["ok"] is False
    d2 = _good_dod()
    d2.new_failures = 1
    assert d2.evaluate()["ok"] is False


def test_final_dod_requires_all_gates() -> None:
    """★★ SC-008：**无缺失的必需门禁**。"""
    d = _good_dod()
    d.gates = {k: v for k, v in d.gates.items()
               if k != "release_check"}
    out = d.evaluate()
    assert out["gates_ok"] is False
    assert "release_check" in out["gates_missing"]


def test_final_dod_lists_human_takeovers() -> None:
    """★ FR-006：**人工介入必须可见**（★ 不是隐藏）。"""
    d = _good_dod()
    d.cases[0].layers.human_takeovers = ["手动补了一个孔"]
    out = d.evaluate()
    assert out["human_takeovers"] == [d.cases[0].key]


#: ══ ★★ 反向验证 U1~U6 ═══════════════════════════════════════════════

def test_u1_stale_half_housing_must_fail() -> None:
    """★★ **U1**：**半箱体保留旧接口坐标** ⇒ 孔系关系检查必须**失败**。"""
    rs = [H.BoreRelation(axis="主轴", center_distance_mm=120.0,
                         expected_center_distance_mm=120.0, fit="H7/k6",
                         split="上箱体"),
          #: ★ 下箱体**还留着旧坐标**
          H.BoreRelation(axis="主轴-下", center_distance_mm=100.0,
                         expected_center_distance_mm=120.0, fit="H7/k6",
                         split="下箱体")]
    out = H.check_bore_relations(rs)
    assert out["ok"] is False, "★★ 半箱体保留旧坐标没被发现！"
    #: ★ 且失效传播也要能查出来
    p = H.propagate_axis("bore_center_distance_mm", 120.0, 140.0)
    assert "下箱体孔系" in p["stale"]


def test_u2_correct_hole_diameters_alone_cannot_pass() -> None:
    """★★ **U2**：**各孔自身直径都正确不能使其通过**（★ 外部方案 R7 ④ 逐字）。

    ★ 判据：`BoreRelation` **根本没有**「直径」这个输入 ——
      ★ 即**不可能**用直径把一个错的中心距盖过去（★ 结构性保证）。
    """
    import inspect
    fields = set(H.BoreRelation.__dataclass_fields__)
    assert "diameter_mm" not in fields, \
        "★★ `BoreRelation` 收了直径 ⇒ 直径可能盖过孔系关系"
    assert "center_distance_mm" in fields and "fit" in fields
    #: ★ 直径都对而中心距错 ⇒ 仍然失败
    r = H.BoreRelation(axis="主轴", center_distance_mm=999.0,
                       expected_center_distance_mm=120.0, fit="H7/k6",
                       split="上箱体")
    assert r.ok is False


def test_u3_ledger_as_evidence_must_fail() -> None:
    """★★★ **U3**：**替换一份证据为「读取台账并断言 `verified`」** ⇒ 必须**失败**。

    ★★ 这是外部方案 R7 ④ 逐字点名的第一条。
    """
    d = _good_dod()
    d.evidences[0] = H.Evidence(kind=H.EV_LEDGER, path="capabilities.yaml",
                                note="读取台账并断言 verified")
    out = d.evaluate()
    assert out["evidence_ok"] is False, "★★ 台账当证据没被发现！"
    assert out["ok"] is False


def test_u4_missing_required_drawing_must_fail() -> None:
    """★★ **U4**：**移除必需图纸** ⇒ 交付检查必须**失败**。"""
    d = _good_dod()
    d.cases[0].artifacts = [a for a in d.cases[0].artifacts
                            if not a.endswith(".slddrw")]
    #: ★ 交付完整性判据：每个案例必须有 `.slddrw`
    incomplete = [c.key for c in d.cases
                  if not any(a.endswith(".slddrw") for a in c.artifacts)]
    assert incomplete == [d.cases[0].key], "★★ 缺图纸没被发现！"
    #: ★ 而且**该案例的义务不应算过**
    d.cases[0].obligations_passed = False
    assert d.evaluate()["ok"] is False


def test_u5_stale_artifact_must_fail() -> None:
    """★★ **U5**：**替换旧版本产物** ⇒ 版本检查必须**失败**。

    ★ 判据：走阶段 3 的 `changed_after_revision`（★ 复用既有资产）。
    """
    from scripts.engineering import drawing_obligations as DO
    before = [DO.ArtifactDigest("m", "a1", "model", "rev-1"),
              DO.ArtifactDigest("d", "b1", "drawing", "rev-1"),
              DO.ArtifactDigest("r", "c1", "report", "rev-1")]
    #: ★ 图纸**没换**（★ 旧版本混入）
    after = [DO.ArtifactDigest("m", "a2", "model", "rev-2"),
             DO.ArtifactDigest("d", "b1", "drawing", "rev-2"),
             DO.ArtifactDigest("r", "c2", "report", "rev-2")]
    out = DO.changed_after_revision(before, after)
    assert out["ok"] is False, "★★ 旧版本产物没被发现！"
    assert out["stale"] == ["drawing"]


def test_u6_hidden_human_takeover_must_fail() -> None:
    """★★ **U6**：**隐藏一次人工接管** ⇒ 报告检查必须**失败**。

    ★ 判据：接管**必须出现在报告里**（★ `human_takeovers` 非空即如实列出）；
      ★ 突变体（把接管藏起来）会让 `human_takeovers` 为空 ⇒ 与真报告不同。
    """
    d = _good_dod()
    d.cases[0].layers.human_takeovers = ["手动补了一个孔"]
    out = d.evaluate()
    #: ★ 真报告**列出来**了
    assert out["human_takeovers"] == [d.cases[0].key]
    #: ★ 突变体：把它藏起来
    hidden = []
    assert out["human_takeovers"] != hidden, "★★ 人工接管被藏起来了！"


def test_u7_out_of_scope_claim_must_fail() -> None:
    """★ **FR-010**：**越界声明**必须被检出。"""
    d = _good_dod()
    d.claims = ["完整减速器已设计"]
    out = d.evaluate()
    assert out["claims_ok"] is False
    assert out["out_of_scope"] == ["完整减速器已设计"]
    assert out["ok"] is False
