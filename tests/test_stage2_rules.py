"""★ 阶段 2 契约测试：七档规则评价 + 图纸义务 + 变更传播（D3/D4/D5）。

★★ 含**反向验证 N3**（★ 规格 §5）：把规则**缺证据分支改成默认通过** ⇒ 必须被发现。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage2_rules.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D3/D4/D5 契约测试
# 官方依据: ① 外部方案阶段 2 的七档（逐字）
#           ② 本仓 `scripts/engineering/rules.py` 的既有 4 档（★ 扩展不推倒）
#           ③ 本仓**事实 71**（`GetPartBox` 回毫米）
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

from scripts.engineering import drawing_obligations as DO               # noqa: E402
from scripts.engineering import rule_verdicts as RV                    # noqa: E402


def _spec(**kw) -> RV.RuleSpec:
    base = dict(id="r1", required_inputs={"load": "N"},
                citation="GB/T 1234-2020 第 5.2 条", effectiveness="effective")
    base.update(kw)
    return RV.RuleSpec(**base)


#: ══ D3 七档 ══════════════════════════════════════════════════════════

def test_seven_verdicts_closed_set() -> None:
    """★ 封闭集就是**七档**（★ 不多不少）。"""
    assert len(RV.ALL_VERDICTS) == 7
    with pytest.raises(AssertionError):
        RV.RuleOutcome("乱写的档", "r1")


def test_releasing_is_pass_only() -> None:
    """★ J9：**只有 PASS 放行**。"""
    assert RV.RELEASING == (RV.PASS,)
    for v in RV.ALL_VERDICTS:
        assert RV.RuleOutcome(v, "r1").releasing is (v == RV.PASS)


def test_missing_input() -> None:
    """★ FR-010：缺必填量 ⇒ `RuleError(MISSING_INPUT)`。"""
    o = RV.evaluate(_spec(), {}, compute=lambda i: True)
    assert o.verdict == RV.ERR_MISSING_INPUT
    assert not o.releasing


def test_unit_mismatch() -> None:
    """★ FR-009：单位不符 ⇒ `RuleError(UNIT_MISMATCH)`（★ **不是 PASS**）。"""
    o = RV.evaluate(_spec(), {"load": 1.0}, units={"load": "kN"},
                    compute=lambda i: True)
    assert o.verdict == RV.ERR_UNIT_MISMATCH
    assert not o.releasing


def test_not_applicable() -> None:
    """★ FR-011：超适用范围 ⇒ `NOT_APPLICABLE`。"""
    o = RV.evaluate(_spec(applicability={"load": (0, 100)}), {"load": 500.0},
                    compute=lambda i: True)
    assert o.verdict == RV.NOT_APPLICABLE
    assert not o.releasing


def test_source_missing_beats_pass() -> None:
    """★★ FR-007：**缺依据** ⇒ `INDETERMINATE(SOURCE_MISSING)`，**不得 PASS**。

    ★★ 这条是本模块的**核心安全判据**：即使 `compute` 返回 True，也必须不 PASS。
    """
    o = RV.evaluate(_spec(citation=""), {"load": 1.0}, compute=lambda i: True)
    assert o.verdict == RV.IND_SOURCE_MISSING, o
    assert not o.releasing


def test_status_unknown_beats_pass() -> None:
    """★★ FR-008：**效力未知** ⇒ `INDETERMINATE(STATUS_UNKNOWN)`，**不得 PASS**。"""
    o = RV.evaluate(_spec(effectiveness="unknown"), {"load": 1.0},
                    compute=lambda i: True)
    assert o.verdict == RV.IND_STATUS_UNKNOWN, o
    assert not o.releasing


def test_pass_and_fail() -> None:
    """★ 依据齐 + 效力明 + 算得出 ⇒ PASS / FAIL。"""
    ok = RV.evaluate(_spec(), {"load": 1.0}, compute=lambda i: i["load"] < 10)
    assert ok.verdict == RV.PASS and ok.releasing
    bad = RV.evaluate(_spec(), {"load": 99.0}, compute=lambda i: i["load"] < 10)
    assert bad.verdict == RV.FAIL and not bad.releasing


def test_no_compute_is_conservative() -> None:
    """★ 没给计算器 ⇒ **保守**报 INDETERMINATE（★ 不默认 PASS）。"""
    o = RV.evaluate(_spec(), {"load": 1.0})
    assert o.verdict == RV.IND_STATUS_UNKNOWN
    assert not o.releasing


def test_release_verdict_blocks_on_any_non_pass() -> None:
    """★ J9：**有任何一条非 PASS ⇒ 不得放行**，且分类报出。"""
    outcomes = [
        RV.RuleOutcome(RV.PASS, "r1"),
        RV.RuleOutcome(RV.IND_SOURCE_MISSING, "r2", detail="缺原文"),
    ]
    r = RV.release_verdict(outcomes)
    assert r["release"] is False
    assert r["passed"] == 1
    assert r["blocking"][0]["rule"] == "r2"
    assert r["indeterminate"] == ["r2"]
    #: ★ 全 PASS ⇒ 放行
    assert RV.release_verdict([RV.RuleOutcome(RV.PASS, "r1")])["release"] is True


#: ══ 反向验证 N3 ═════════════════════════════════════════════════════

def test_n3_missing_evidence_cannot_be_forced_to_pass() -> None:
    """★★ **N3**：把**缺证据分支改成默认通过** ⇒ 本测试必须抓到。

    ★ 做法：模拟一个「被改坏」的评价器 —— 它对缺依据的规则**回 PASS**。
      ⇒ 然后断言「真评价器」与它**不一致**（★ 即真评价器**没有**默认通过）。
    """
    def broken_evaluator(spec, inputs):
        """★ 突变体：**无条件 PASS**（★ 这正是 N3 要抓的形态）。"""
        return RV.RuleOutcome(RV.PASS, spec.id)

    spec = _spec(citation="")                    #: ★ 缺依据
    good = RV.evaluate(spec, {"load": 1.0}, compute=lambda i: True)
    bad = broken_evaluator(spec, {"load": 1.0})
    assert good.verdict == RV.IND_SOURCE_MISSING, good
    assert bad.verdict == RV.PASS
    #: ★★ 判据：**真评价器**对缺依据**不放行** ⇒ 突变体会被抓
    assert good.releasing is False and bad.releasing is True
    assert good.verdict != bad.verdict, "★ 真评价器与突变体一致 ⇒ N3 抓不到"


#: ══ D4 图纸义务 ═════════════════════════════════════════════════════

def test_obligations_from_method() -> None:
    """★ 义务从**方法声明**取（★ 不是手工列）。"""
    obls = DO.obligations_from_method("plate")
    assert obls, "★ plate 方法应有义务"
    names = [o.name for o in obls]
    assert any("回读厚度" in n for n in names), names


def test_coverage_requires_all() -> None:
    """★ SC-005：覆盖率要求 **100%**。"""
    obls = DO.obligations_from_method("plate")
    c0 = DO.coverage(obls)
    assert c0["ok"] is False and c0["ratio"] < 1.0
    for o in obls:
        DO.mark_covered(obls, o.name, evidence="真机回读")
    c1 = DO.coverage(obls)
    assert c1["ok"] is True and c1["ratio"] == 1.0, c1


def test_mark_covered_unknown_returns_false() -> None:
    """★ 标一个不存在的义务 ⇒ 回 False（★ 不静默）。"""
    obls = DO.obligations_from_method("plate")
    assert DO.mark_covered(obls, "绝不存在的义务") is False


#: ══ D5 变更传播 ═════════════════════════════════════════════════════

def test_digest_and_version_consistency(tmp_path: pathlib.Path) -> None:
    """★ SC-006：三类产物齐 + 版本一致 ⇒ ok。"""
    ds = []
    for k in ("model", "drawing", "report"):
        p = tmp_path / ("%s.txt" % k)
        p.write_text("内容 %s" % k, encoding="utf-8")
        ds.append(DO.digest_of(p, kind=k, revision="rev-1"))
    v = DO.version_consistent(ds)
    assert v["ok"] is True, v
    #: ★ 少一类 ⇒ 不 ok
    assert DO.version_consistent(ds[:2])["ok"] is False


def test_changed_after_revision_detects_stale(tmp_path: pathlib.Path) -> None:
    """★★ **N2**：图纸**保留旧版本** ⇒ sha256 不变 ⇒ 必须被发现。"""
    before, after = [], []
    for k in ("model", "drawing", "report"):
        p = tmp_path / ("%s.txt" % k)
        p.write_text("旧 %s" % k, encoding="utf-8")
        before.append(DO.digest_of(p, kind=k, revision="rev-1"))
        #: ★ 只刷新 model 与 report —— **故意不刷新 drawing**（N2 突变）
        p.write_text(("新 %s" % k) if k != "drawing" else ("旧 %s" % k),
                     encoding="utf-8")
        after.append(DO.digest_of(p, kind=k, revision="rev-2"))
    r = DO.changed_after_revision(before, after)
    assert r["ok"] is False, "★ 旧版本没被发现"
    assert r["stale"] == ["drawing"], r


def test_affected_steps_finds_by_param_and_derive() -> None:
    """★ 影响面：按 `params` **和** `derive` 文本找（★ 两个都要看）。"""
    from scripts.engineering import registry as R
    steps = (
        R.PlanStep(step="extrude_boss", params={"depth_mm": 10.0}),
        R.PlanStep(step="hole_group", params={}, derive="★ 4 个孔，count=4"),
        R.PlanStep(step="sketch_end", params={}),
    )
    by_param = DO.affected_steps(steps, "depth_mm")
    assert by_param == (0,), by_param
    #: ★ `count` 只在 `derive` 文本里 ⇒ 也要找得到
    by_derive = DO.affected_steps(steps, "count")
    assert by_derive == (1,), by_derive


def test_propagation_report_flags_unpropagated() -> None:
    """★ SC-010：有受影响步骤却没传播 ⇒ 不算通过。"""
    from scripts.engineering import registry as R
    steps = (R.PlanStep(step="extrude_boss", params={"depth_mm": 10.0}),)
    bad = DO.propagation_report(steps, [DO.ChangeRecord("depth_mm", 10, 20,
                                                        propagated=False)])
    assert bad["ok"] is False and bad["unpropagated"] == ["depth_mm"]
    good = DO.propagation_report(steps, [DO.ChangeRecord("depth_mm", 10, 20,
                                                         propagated=True)])
    assert good["ok"] is True
