"""★ EC12 判据 —— 留出集 / 增益归因 / 联合考核 / 零事故≠零风险 / 单方法准入 / 分别过门。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/evaluation.py`（★ EC12 的实现）
#         `specs/314-ec12-capability-package-and-eval/spec.md`
# 定位:   ★ EC12 的判据（★ 逐字承计划 §5 EC12 的「验收」）。
# 官方依据: 不适用（本仓的评测层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不调 COM · ★ 不调模型）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from engineering import evaluation as E


# ══════════════════════════════════════════════════════════════════════
# V1 · 留出集可重复
# ══════════════════════════════════════════════════════════════════════

def _set(**kw) -> E.EvalSet:
    s = E.EvalSet(frozen={"data": "v1", "model_version": "m1", "temperature": 0.0,
                          "budget": 100, "allowed_tools": ["a"], "runtime": "py3.14"})
    s.add(E.EvalCase("c1", family="plate", domain="d1", fault="none",
                     split=E.SplitKind.HOLDOUT))
    s.add(E.EvalCase("c2", family="bracket", domain="d2", fault="clamp",
                     split=E.SplitKind.TRAIN))
    return s


def test_v1_holdout_fingerprint_is_reproducible():
    """★★★★ V1：★ **留出集可重复**（★ 验收逐字）。

    ★★ 判据：★ 同批案例 + 同冻结条件 ⇒ **同指纹**。
    """
    a, b = _set(), _set()
    assert a.fingerprint() == b.fingerprint(), (
        "★★ 同一评测集两次指纹不同 ⇒ ★ 不可重复")


def test_v1_fingerprint_changes_when_data_changes():
    """★★ V1：★ **数据变了 ⇒ 指纹变**（★ 否则「可重复」是假的）。"""
    a = _set()
    b = _set()
    b.add(E.EvalCase("c3", family="x", split=E.SplitKind.HOLDOUT))
    assert a.fingerprint() != b.fingerprint(), "★★ 加了案例指纹却没变"


def test_v1_frozen_conditions_must_be_complete():
    """★★★★ V1：★ **六项冻结条件齐**（★ 逐字承 EC12-T05）。"""
    ok = _set()
    assert ok.frozen_conditions_complete()["ok"] is True
    #: ★★ **缺一项 ⇒ 报出来**
    for miss in ("data", "model_version", "temperature", "budget",
                 "allowed_tools", "runtime"):
        f = dict(ok.frozen)
        f.pop(miss)
        out = E.EvalSet(cases=list(ok.cases), frozen=f).frozen_conditions_complete()
        assert out["ok"] is False, "★★ 缺 %r 却判齐" % miss
        assert out["missing"] == [miss]


def test_v1_contamination_is_detected():
    """★★★★ V1：★ **近似复制污染必须检出**（★ 逐字承 EC12-T01：

    「★ 按零件族/参数域/故障划分，★ **避免近似复制污染**」）。

    ★★ 判据：★ 同指纹（★ 同族/同域/同故障/同内容）出现在**多个划分** ⇒ ★ **污染** ✗
    """
    s = _set()
    #: ★★ **把同一个案例同时放进 train 和 holdout**
    s.add(E.EvalCase("dup", family="plate", domain="d1", fault="none",
                     split=E.SplitKind.TRAIN, content="★ 同内容"))
    s.add(E.EvalCase("dup2", family="plate", domain="d1", fault="none",
                     split=E.SplitKind.HOLDOUT, content="★ 同内容"))
    dup = s.duplicate_fingerprints()
    assert dup, "★★ 跨划分的重复案例**没检出** ⇒ ★ 留出集被污染"
    assert set(dup[0]["ids"]) == {"dup", "dup2"}
    #: ★★ 且**整个评测集**判不 ok
    assert s.verdict()["ok"] is False


def test_v1_no_holdout_is_not_ok():
    """★★★ V1：★ **没有留出集 ⇒ 不算 ok**（★ 验收要的正是它）。"""
    s = E.EvalSet(frozen={"data": 1, "model_version": 1, "temperature": 0,
                          "budget": 1, "allowed_tools": [], "runtime": "x"})
    s.add(E.EvalCase("c1", split=E.SplitKind.TRAIN))
    assert s.verdict()["ok"] is False, "★★ 没留出集却判 ok"


# ══════════════════════════════════════════════════════════════════════
# V2 · 增益不是靠无限重试
# ══════════════════════════════════════════════════════════════════════

def test_v2_gain_without_retry_increase_is_attributed_to_system():
    """★★★★ V2：★ **增益不伴随重试上升 ⇒ 归因于系统**。"""
    rep = E.AttributionReport(arms={
        E.ArmKind.MODEL_PROMPT: E.ArmResult(E.ArmKind.MODEL_PROMPT,
                                            passed=5, failed=5, retries=10),
        E.ArmKind.MODEL_SYSTEM: E.ArmResult(E.ArmKind.MODEL_SYSTEM,
                                            passed=9, failed=1, retries=11),
    })
    out = rep.system_gain()
    assert out["ok"] is True, "★ 缺臂：%r" % out
    assert out["gain"] > 0, "★ 应有增益"
    assert out["attributed_to_system"] is True, (
        "★★ 重试没怎么涨，增益却**不归因于系统**：%r" % out)
    assert out["attributed_to_retries"] is False


def test_v2_gain_driven_by_retries_is_not_system_gain():
    """★★★★★ V2：★ **增益靠加无限重试 ⇒ 不算系统增益**（★ 验收逐字：

    「★ **系统增益不是增加无限重试得到**」）。
    """
    rep = E.AttributionReport(arms={
        E.ArmKind.MODEL_PROMPT: E.ArmResult(E.ArmKind.MODEL_PROMPT,
                                            passed=5, failed=5, retries=5),
        #: ★★ **重试暴涨 10 倍**
        E.ArmKind.MODEL_SYSTEM: E.ArmResult(E.ArmKind.MODEL_SYSTEM,
                                            passed=9, failed=1, retries=50),
    })
    out = rep.system_gain()
    assert out["gain"] > 0, "★ 通过率确实涨了"
    assert out["attributed_to_retries"] is True, (
        "★★★ 重试暴涨却**没归因于重试** ⇒ ★ 会把「靠重试」当成「系统好」")
    assert out["attributed_to_system"] is False, (
        "★★★ 增益靠重试却归因于系统 ⇒ ★ 违反验收")
    assert "归因于重试" in out["reason"]


def test_v2_missing_arm_is_reported():
    """★★ V2：★ **缺对照臂 ⇒ 报出来**（★ 不能只跑一组就说有增益）。"""
    rep = E.AttributionReport(arms={E.ArmKind.MODEL_SYSTEM: E.ArmResult("x", passed=9)})
    out = rep.system_gain()
    assert out["ok"] is False
    assert "缺对照臂" in out["reason"]


def test_v2_retries_per_case_is_computed():
    """★★ V2：★ **每案重试数**可算（★ 增益归因的关键量）。"""
    r = E.ArmResult("a", passed=5, failed=5, retries=20)
    assert abs(r.retries_per_case() - 2.0) < 1e-12, "★ 每案重试数不对：%r" % r.retries_per_case()
    #: ★★ **空集 ⇒ 0**（★ 不除零）
    assert E.ArmResult("a").retries_per_case() == 0.0


# ══════════════════════════════════════════════════════════════════════
# V3 · 错误放行与拒绝率联合考核
# ══════════════════════════════════════════════════════════════════════

def test_v3_all_rejecting_system_is_rejected():
    """★★★★★ V3：★ **「全拒」不算安全完成**（★ 逐字承验收 + 计划 §3.2：

    「★ **不把拒绝全部任务当安全完成**」）。

    ★★ 判据：★ 通过率 0 + 拒绝率 100% ⇒ ★ **不 ok**（★ 它什么都没做）✗
    """
    rep = E.AttributionReport(arms={
        "A": E.ArmResult("A", passed=0, failed=0, rejected=100),
    })
    out = rep.joint_verdict()
    assert out["all_rejecting"] is True, "★★ 全拒**没检出**"
    assert out["ok"] is False, (
        "★★★ 全拒被判 ok ⇒ ★ 把「拒绝全部任务」当成了安全完成")


def test_v3_all_releasing_with_false_releases_is_rejected():
    """★★★★ V3：★ **「全放且有错误放行」⇒ 危险**（★ 联合考核的意义）。"""
    rep = E.AttributionReport(arms={
        "A": E.ArmResult("A", passed=90, failed=10, rejected=0, false_releases=10),
    })
    out = rep.joint_verdict()
    assert out["all_releasing"] is True, "★★ 全放**没检出**"
    assert out["ok"] is False


def test_v3_joint_metrics_are_all_reported():
    """★★★★ V3：★ **三率都要报**（★ 通过/拒绝/错误放行 —— ★ 只看一个会骗人）。"""
    rep = E.AttributionReport(arms={
        "A": E.ArmResult("A", passed=70, failed=20, rejected=10, false_releases=2),
    })
    out = rep.joint_verdict()
    row = out["arms"]["A"]
    for key in ("pass_rate", "reject_rate", "false_release_rate"):
        assert key in row, "★★ 缺 `%s` ⇒ ★ 不是联合考核" % key
    assert abs(row["pass_rate"] - 0.70) < 1e-12
    assert abs(row["reject_rate"] - 0.10) < 1e-12
    assert abs(row["false_release_rate"] - 0.02) < 1e-12


def test_v3_healthy_mix_passes():
    """★★ V3 负例：★ **健康的混合 ⇒ ok**（★ 不是一律拒）。"""
    rep = E.AttributionReport(arms={
        "A": E.ArmResult("A", passed=85, failed=10, rejected=5, false_releases=0),
    })
    assert rep.joint_verdict()["ok"] is True


# ══════════════════════════════════════════════════════════════════════
# V4 · 零事故 ≠ 零风险
# ══════════════════════════════════════════════════════════════════════

def test_v4_zero_failures_does_not_mean_zero_risk():
    """★★★★★ V4：★ **零事故样本不等于零风险**（★ 验收逐字）。

    ★★ 判据：★ `failures=0` 时 Wilson **上界 > 0**（★ 没见过 ≠ 不会发生）。
    """
    ub = E.wilson_upper_bound(0, 100)
    assert ub > 0, "★★★ 100 次零事故就被判「零风险」⇒ ★ 违反验收"
    #: ★★ 上界应≈ `z²/(n+z²)` ≈ 0.037
    assert 0.02 < ub < 0.06, "★ 上界数值不对：%r" % ub
    #: ★★★ **样本越多上界越低**（★ 那才是「证据增加」）
    assert E.wilson_upper_bound(0, 1000) < ub, "★★ 样本多了上界没降"


def test_v4_no_trials_means_certainty_of_ignorance():
    """★★ V4：★ **一次都没试 ⇒ 上界 = 1**（★ 不是 0）。"""
    assert E.wilson_upper_bound(0, 0) == 1.0, (
        "★★ 没试验却判「零风险」")


def test_v4_upper_bound_grows_with_failures():
    """★★ V4：★ **有失败 ⇒ 上界更大**（★ 单调）。"""
    assert (E.wilson_upper_bound(5, 100)
            > E.wilson_upper_bound(0, 100)), "★★ 有失败上界反而更小"


# ══════════════════════════════════════════════════════════════════════
# V5 · 各领域分别过门
# ══════════════════════════════════════════════════════════════════════

def test_v5_domains_gate_separately():
    """★★★★ V5：★ **各领域发布分别过门**（★ 验收逐字）。

    ★★ 判据：★ **一个总的 `approve` 不算** —— ★ 每个领域**各自**报 ✗
    """
    g = E.DomainGates()
    g.set_gate("part", gate="G5", passed=True)
    g.set_gate("drawing", gate="G5", passed=False)
    out = g.verdict()
    assert out["ok"] is False, "★★ 有一个领域没过却判整体过"
    assert out["failed"] == ["drawing"]
    assert out["passed"] == ["part"]
    #: ★★ **逐个报**（★ 不是只给一个总论）
    assert "part" in out["per_domain"] and "drawing" in out["per_domain"]
    assert "不合并成一个 approve" in out["reason"]


def test_v5_all_domains_pass():
    """★★ V5：★ **全过 ⇒ ok**。"""
    g = E.DomainGates()
    for d in ("part", "assembly", "drawing"):
        g.set_gate(d, gate="G5", passed=True)
    assert g.verdict()["ok"] is True


def test_v5_no_domains_is_not_ok():
    """★★ V5：★ **一个领域都没过门 ⇒ 不 ok**。"""
    assert E.DomainGates().verdict()["ok"] is False


# ══════════════════════════════════════════════════════════════════════
# V6 · 单方法准入七项
# ══════════════════════════════════════════════════════════════════════

def test_v6_seven_admission_items_are_required():
    """★★★★ V6：★ **七项必须齐**（★ 逐字承 EC12-T06）。"""
    assert len(E.MethodAdmission.REQUIRED) == 7, (
        "★ 不是七项：%r" % (E.MethodAdmission.REQUIRED,))
    full = {k: "★ 有" for k in E.MethodAdmission.REQUIRED}
    assert E.MethodAdmission.check(full)["ok"] is True
    #: ★★ **缺一项 ⇒ 报出来**
    for k in E.MethodAdmission.REQUIRED:
        part = {kk: "★ 有" for kk in E.MethodAdmission.REQUIRED if kk != k}
        out = E.MethodAdmission.check(part)
        assert out["ok"] is False, "★★ 缺 %r 却判可准入" % k
        assert out["missing"] == [k]


# ══════════════════════════════════════════════════════════════════════
# V7 · 沙箱 → 生产需独立审核
# ══════════════════════════════════════════════════════════════════════

def test_v7_sandbox_alone_cannot_promote():
    """★★★★★ V7：★ **沙箱通过还不够**（★ 逐字承 EC12-T08：

    「★ **实验通过后仍需独立审核才变成生产方法**」）。
    """
    g = E.AdmissionGate(sandbox_passed=True, proposer="★ agent-1")
    out = g.may_promote()
    assert out["may_promote"] is False, (
        "★★★ 沙箱通过就进生产 ⇒ ★ 违反 EC12-T08")
    assert "独立审核" in out["reason"]


def test_v7_self_review_is_rejected():
    """★★★★ V7：★ **审核人 = 提出者 ⇒ 自审 ⇒ 拒**（★ 与 EC04-T06 同族）。"""
    g = E.AdmissionGate(sandbox_passed=True, proposer="★ agent-1",
                        independent_reviewer="★ agent-1")
    out = g.may_promote()
    assert out["may_promote"] is False, "★★★ 自审被允许"
    assert "自审" in out["reason"]


def test_v7_independent_review_allows_promotion():
    """★★ V7：★ **沙箱通过 + 独立审核 ⇒ 可进生产**。"""
    g = E.AdmissionGate(sandbox_passed=True, proposer="★ agent-1",
                        independent_reviewer="★ reviewer-2")
    out = g.may_promote()
    assert out["may_promote"] is True, "★ 该准入却拒了：%r" % out
    assert out["reviewer"] == "★ reviewer-2"


def test_v7_unsandboxed_cannot_promote():
    """★★ V7：★ **没进沙箱 ⇒ 不进生产**（★ 逐字承 EC12-T08 前半句）。"""
    g = E.AdmissionGate(sandbox_passed=False, independent_reviewer="★ r2")
    assert g.may_promote()["may_promote"] is False


def test_v7_reuses_ec03_sandbox_prefix():
    """★★★ V7：★ **复用 EC03 的沙箱前缀隔离**（★ 铁律 1 —— ★ 不另建一套）。"""
    from engineering import compiler as C
    assert C.is_production_method("sandbox_explore_1") is False, (
        "★★ EC03 的沙箱隔离失效 ⇒ ★ 本特性要重造一套")
    assert C.is_production_method("plate") is True
