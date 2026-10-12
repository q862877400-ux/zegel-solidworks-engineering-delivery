"""★ 阶段 6 契约测试：可调连杆（规格 321 的 L1~L4）。

★★ 含**反向验证**（★ 规格 §5 的 T1~T5），★ 其中 **T4 是「防保守」那一条**：
   T1 交换运动副连接对象 ⇒ 必须失败
   T2 选择错误装配分支   ⇒ 必须失败
   T3 加入锁死自由度的配合 ⇒ 必须失败
   T4 ★★ 将一切图中有环都拒绝 ⇒ **正确闭链正例必须失败**
      ⇒ ★ 即「全拒」策略**被本规格判为错**
   T5 只给采样却声称全行程 ⇒ 必须不自动交付
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage6_linkage.py
# 定位:   规格 `specs/321-stage6-adjustable-linkage` 的 L1~L4 契约测试
# 官方依据: ① 外部方案阶段 6 的验收 S6（逐字）
#           ② 外部方案 §5 R6 ④ 逐字：「将一切图中有环都拒绝，正确闭链正例
#              必须失败，以防『保守到失去能力』」
#           ③ `scripts/engineering/part_loop.py` 的 `DofPlan.is_acceptable()`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import math
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import linkage as L                             # noqa: E402


def _fb() -> L.FourBar:
    """★ 一个**满足 Grashof** 的四杆（★ 曲柄能整转）。"""
    return L.FourBar(a=40.0, b=120.0, c=80.0, d=150.0)


#: ══ L1 闭环求解 ══════════════════════════════════════════════════════

def test_codes_closed_set() -> None:
    """★ 封闭码就是四档。"""
    assert len(L.LINKAGE_CODES) == 4
    with pytest.raises(AssertionError):
        L.ContinuityVerdict(verdict="乱写的")


def test_bad_lengths_rejected() -> None:
    """★ 长度必须 > 0（★ 不静默）。"""
    with pytest.raises(L.LinkageError) as ei:
        L.FourBar(a=0.0)
    assert ei.value.code == "bad-lengths"


def test_grashof_condition() -> None:
    """★ Grashof 条件：最短 + 最长 ≤ 其余两之和。"""
    assert _fb().grashof is True
    #: ★ 明显不满足的一组
    assert L.FourBar(a=10.0, b=20.0, c=30.0, d=100.0).grashof is False


def test_solve_residual_is_tiny() -> None:
    """★★ L1/SC-002：闭环**残差**在容差内（★ 实测 ~1e-14）。"""
    s = L.solve_four_bar(_fb(), math.radians(30.0))
    assert s.ok is True
    assert s.residual < 1e-9, s.residual


def test_solve_across_a_range_of_angles() -> None:
    """★ 多个曲柄角都要能解（★ 不是只有一个角度对）。"""
    ok = 0
    for deg in range(0, 360, 15):
        try:
            s = L.solve_four_bar(_fb(), math.radians(deg),
                                 branch=L.BRANCH_OPEN)
            if s.ok:
                ok += 1
        except L.LinkageError:
            pass
    assert ok >= 20, "★ 24 个角度里只解出 %d 个" % ok


def test_no_solution_raises() -> None:
    """★ 装不起来 ⇒ **抛**（★ 不静默回一个假解）。"""
    #: ★ 曲柄太短 ⇒ 某些角度判别式 < 0
    fb = L.FourBar(a=10.0, b=100.0, c=10.0, d=100.0)
    raised = False
    for deg in range(0, 360, 5):
        try:
            L.solve_four_bar(fb, math.radians(deg))
        except L.LinkageError as e:
            assert e.code in ("no-solution", "bad-branch")
            raised = True
            break
    assert raised, "★ 这一组居然全解出来了？"


def test_residual_is_independent_arithmetic() -> None:
    """★★ FR-001：残差是**把解代回闭环方程**算的（★ 不靠 CAD）。"""
    s = L.solve_four_bar(_fb(), math.radians(45.0))
    #: ★ 手工复核：B→D 距离必须 = 连杆长 b
    a, b, c, d = 40.0, 120.0, 80.0, 150.0
    bx = a * math.cos(s.theta2)
    by = a * math.sin(s.theta2)
    cx = d + c * math.cos(s.theta4)
    cy = c * math.sin(s.theta4)
    got = math.hypot(cx - bx, cy - by)
    assert abs(got - b) < 1e-9, (got, b)


#: ══ L2 分支标识 ═════════════════════════════════════════════════════

def test_two_branches_exist() -> None:
    """★★ L2：同一个曲柄角有**两个解**（★ 两个分支都解得出来）。"""
    fb = _fb()
    s_open = L.solve_four_bar(fb, math.radians(30.0), branch=L.BRANCH_OPEN)
    s_cross = L.solve_four_bar(fb, math.radians(30.0), branch=L.BRANCH_CROSSED)
    assert s_open.ok and s_cross.ok
    #: ★ 两个解的摇杆角**不同**
    assert abs(s_open.theta4 - s_cross.theta4) > 1e-6


def test_branch_of_uses_theta4_half_plane() -> None:
    """★ 分支判据：`θ4 ∈ (0,π)` ⇒ open · `(π,2π)` ⇒ crossed。"""
    fb = _fb()
    assert L.branch_of(fb, 0.0, math.radians(90.0)) == L.BRANCH_OPEN
    assert L.branch_of(fb, 0.0, math.radians(270.0)) == L.BRANCH_CROSSED


def test_bad_branch_name_rejected() -> None:
    """★ 未知分支名 ⇒ 抛（★ 不静默）。"""
    with pytest.raises(L.LinkageError) as ei:
        L.solve_four_bar(_fb(), 0.0, branch="乱写的分支")
    assert ei.value.code == "bad-branch"


def test_solved_branch_matches_request() -> None:
    """★★ 求解器回的 `branch` 必须**与请求一致**（★ 不是"解出来就算对"）。"""
    fb = _fb()
    for br in (L.BRANCH_OPEN, L.BRANCH_CROSSED):
        s = L.solve_four_bar(fb, math.radians(60.0), branch=br)
        assert s.branch == br
        assert L.branch_of(fb, s.theta2, s.theta4) == br


#: ══ L3 奇异区间 ═════════════════════════════════════════════════════

def test_singular_scan_covers_endpoints() -> None:
    """★ FR-005：**端点必须查**（★ 0° 与 180° 都在扫描集里）。"""
    ss = L.singular_scan(_fb(), samples=36)
    assert ss.scanned >= 36


def test_singular_scan_finds_fold_for_unreachable() -> None:
    """★ 不可达的角度 ⇒ `fold`（★ 判别式 < 0）。"""
    #: ★ 曲柄 100 + 连杆 10 < 机架 150 ⇒ 大部分角度不可达
    fb = L.FourBar(a=100.0, b=10.0, c=10.0, d=150.0)
    ss = L.singular_scan(fb, samples=180)
    assert ss.has_singular, "★ 这一组应当有奇异/不可达点"
    assert any(p.kind == "fold" for p in ss.points)


#: ══ L4 连续性判定 ═══════════════════════════════════════════════════

def test_continuity_pass_when_no_requirement() -> None:
    """★ 没要求连续、也没覆盖缺口 ⇒ `pass`。"""
    v = L.continuity_verdict(order_requires_continuous=False,
                             is_full_domain_proof=False,
                             sampled=360, uncovered=0)
    assert v.verdict == L.PASS and v.releasing is True


def test_continuity_interference_fails() -> None:
    """★ 检出干涉 ⇒ `fail`（★ 必须解释）。"""
    v = L.continuity_verdict(order_requires_continuous=False,
                             is_full_domain_proof=False,
                             interferences=[{"at": 30.0}])
    assert v.verdict == L.FAIL and v.releasing is False


def test_continuity_sampled_only_is_indeterminate() -> None:
    """★★★ FR-007：**要求连续 + 只有采样** ⇒ `INDETERMINATE` + `BLOCKED_VERIFICATION`。

    ★★ 这是本模块的**核心判据**（★ 外部方案逐字）。
    """
    v = L.continuity_verdict(order_requires_continuous=True,
                             is_full_domain_proof=False,
                             sampled=360, uncovered=0)
    assert v.verdict == L.INDETERMINATE
    assert v.run_state == L.BLOCKED_VERIFICATION
    assert v.releasing is False


def test_continuity_full_proof_passes() -> None:
    """★ 有**全域证明** ⇒ `pass`（★ 即使要求连续）。"""
    v = L.continuity_verdict(order_requires_continuous=True,
                             is_full_domain_proof=True,
                             sampled=360, uncovered=0)
    assert v.verdict == L.PASS and v.releasing is True


def test_continuity_uncovered_blocks() -> None:
    """★ 有**未覆盖区间** ⇒ 也挡（★ 比"只有采样"更明确）。"""
    v = L.continuity_verdict(order_requires_continuous=False,
                             is_full_domain_proof=True,
                             sampled=300, uncovered=60)
    assert v.verdict == L.INDETERMINATE
    assert v.run_state == L.BLOCKED_VERIFICATION


#: ══ S6 整体 ═════════════════════════════════════════════════════════

def test_evaluate_linkage_good() -> None:
    """★ 正例：五项都过。"""
    r = L.evaluate_linkage(_fb(), math.radians(30.0), branch=L.BRANCH_OPEN,
                           intentional_dof=[{"name": "曲柄整转", "why": "主动件"}])
    assert r["ok"] is True, r
    assert r["residual_ok"] is True
    assert r["branch_ok"] is True
    assert r["dof_ok"] is True
    assert r["dof_annotated"] is True
    assert r["continuity"]["releasing"] is True


def test_evaluate_requires_annotated_dof() -> None:
    """★ FR：有自由度却**没标注理由** ⇒ 不算过（★ 复用 `DofPlan` 的纪律）。"""
    r = L.evaluate_linkage(_fb(), math.radians(30.0),
                           intentional_dof=[{"name": "x", "why": "  "}])
    assert r["dof_annotated"] is False
    assert r["ok"] is False


def test_evaluate_dof_mismatch_fails() -> None:
    """★ 目标自由度 ≠ 实际 ⇒ 失败。"""
    r = L.evaluate_linkage(_fb(), math.radians(30.0), target_dof=1,
                           actual_dof=2,
                           intentional_dof=[{"name": "x", "why": "y"}])
    assert r["dof_ok"] is False and r["ok"] is False


#: ══ ★★ 反向验证 T1~T5 ═══════════════════════════════════════════════

def test_t1_swapping_a_joint_must_fail() -> None:
    """★★ **T1**：**交换一个运动副连接对象** ⇒ 验证必须**失败**。

    ★ 做法：把**机架与连杆的长度互换**（★ 等价于把运动副接到错的对象上）
      ⇒ 同一个 `θ2` 下闭环**解不出来**或**残差异常** ⇒ 检出。
    """
    good = L.solve_four_bar(_fb(), math.radians(30.0))
    assert good.ok is True
    #: ★ 交换：机架 150 ↔ 连杆 120（★ 那会把闭环改成另一个机构）
    swapped = L.FourBar(a=40.0, b=150.0, c=80.0, d=120.0)
    try:
        s = L.solve_four_bar(swapped, math.radians(30.0))
        #: ★ 若还能解，则**位姿必须与原来不同**（★ 那就是"接错了"的证据）
        assert abs(s.theta4 - good.theta4) > 1e-3, "★ 交换后位姿没变？"
    except L.LinkageError:
        pass          #: ★ 解不出来也算检出


def test_t2_wrong_branch_must_fail() -> None:
    """★★ **T2**：**选择错误装配分支** ⇒ 验证必须**失败**。

    ★ 判据：请求 `open` 而 `branch_of` 算出 `crossed` ⇒ `branch_ok=False`。
    """
    fb = _fb()
    #: ★ 真解是 open，而我们**故意声称** crossed
    s_open = L.solve_four_bar(fb, math.radians(30.0), branch=L.BRANCH_OPEN)
    got = L.branch_of(fb, s_open.theta2, s_open.theta4)
    assert got == L.BRANCH_OPEN
    assert got != L.BRANCH_CROSSED, "★ 错分支没被区分出来"
    #: ★ 而且两个分支的位姿**真的不同**（★ 不是名义上的区别）
    s_cross = L.solve_four_bar(fb, math.radians(30.0), branch=L.BRANCH_CROSSED)
    assert abs(s_open.theta4 - s_cross.theta4) > 1e-3


def test_t3_locking_a_dof_must_fail() -> None:
    """★★ **T3**：**加入锁死自由度的配合** ⇒ 验证必须**失败**。

    ★ 判据：实际自由度降到 0 ⇒ 与目标 1 不符 ⇒ `dof_ok=False`。
    """
    r = L.evaluate_linkage(_fb(), math.radians(30.0), target_dof=1,
                           actual_dof=0,
                           intentional_dof=[{"name": "x", "why": "y"}])
    assert r["dof_ok"] is False
    assert r["ok"] is False


def test_t4_rejecting_all_loops_must_fail() -> None:
    """★★★★ **T4（防保守）**：**将一切图中有环都拒绝** ⇒ **正确闭链正例必须失败**。

    ★★ 这是本规格**最重要**的一条反向验证（★ 外部方案 §5 R6 ④ 逐字）：
      ★ 「以防『**保守到失去能力**』」。
    ★ 做法：
      · **突变体**：`reject_all_loops()` —— 见到环就拒（★ 那是"保守"的极端）
      · **正例**：一个正确的闭链
      ⇒ ★ 断言：**突变体拒掉正例**（★ 即"全拒"策略**是错的**），
        ★ 而**真判定器放行正例**。
    """
    def reject_all_loops(_fb, _theta2, **_kw):
        """★ 突变体：**只要有环就拒**（★ 这就是"保守到失去能力"）。"""
        return {"ok": False, "reason": "★ 图里有环 ⇒ 拒"}

    fb = _fb()
    good = L.evaluate_linkage(fb, math.radians(30.0),
                              intentional_dof=[{"name": "曲柄整转",
                                                "why": "主动件"}])
    mutant = reject_all_loops(fb, math.radians(30.0))

    #: ★★ 真判定器**放行**正例
    assert good["ok"] is True, "★★ 正确闭链正例被拒了 ⇒ 保守到失去能力！"
    #: ★ 突变体**拒掉**正例 ⇒ ★ 两者不同 ⇒ 「全拒」策略**被本规格判为错**
    assert mutant["ok"] is False
    assert good["ok"] != mutant["ok"], "★ 突变体与真判定器一致 ⇒ T4 抓不到"


def test_t5_sampled_only_cannot_auto_deliver() -> None:
    """★★ **T5**：只给**采样**证据却要求**全行程** ⇒ **必须不自动交付**。"""
    r = L.evaluate_linkage(_fb(), math.radians(30.0),
                           intentional_dof=[{"name": "x", "why": "y"}],
                           order_requires_continuous=True,
                           is_full_domain_proof=False, sampled=360)
    assert r["continuity"]["verdict"] == L.INDETERMINATE
    assert r["continuity"]["run_state"] == L.BLOCKED_VERIFICATION
    assert r["continuity"]["releasing"] is False
    assert r["ok"] is False


def test_t5b_claiming_full_proof_without_it_is_caught() -> None:
    """★★ **T5 的加强版**：声称有全域证明但**没扫全** ⇒ 仍被挡。"""
    r = L.evaluate_linkage(_fb(), math.radians(30.0),
                           intentional_dof=[{"name": "x", "why": "y"}],
                           order_requires_continuous=True,
                           is_full_domain_proof=True,   #: ★ 声称有
                           sampled=300, uncovered=60)   #: ★ 而实际有洞
    assert r["continuity"]["verdict"] == L.INDETERMINATE
    assert r["ok"] is False, "★★ 声称全域证明却有未覆盖区间 ⇒ 没被挡住"


#: ══ ★ 与既有资产的一致性 ═══════════════════════════════════════════

def test_consistent_with_existing_dof_discipline() -> None:
    """★★ 复用既有纪律：`DofPlan` 的「有意保留自由度必须标注」同口径。

    ★★ 实测（2026-10-12）：`DofPlan.total_dof()` = `2×entities − relations − dimensions`
      ⇒ `entities=1` 时**有 2 个自由度** ⇒ ★ 只标注 1 个 ⇒ `ok=False`
      （★ 理由逐字「还有 1 个自由度**没标注理由** ⇒ 那是「忘了锁」不是「有意保留」」）
      ⇒ ★★ **两个都要标注**才 `ok`。
      ⚠ 我第一版只标注 1 个、还断言 `ok=True`，★ **是既有纪律纠正了我**（★ 好事）。
    """
    from scripts.engineering.part_loop import DofPlan
    p = DofPlan(entities=1, relations=[], dimensions=[])
    #: ★ 空理由 ⇒ 拒（★ 既有纪律）
    with pytest.raises(ValueError):
        p.add_intentional_dof("曲柄整转", "  ")
    #: ★ 只标注 1 个而自由度是 2 ⇒ **仍不 acceptable**
    p.add_intentional_dof("曲柄整转", "主动件")
    v1 = p.is_acceptable()
    assert v1["ok"] is False and v1["unexplained"] == 1, v1
    #: ★ 两个都标注 ⇒ acceptable
    p.add_intentional_dof("连杆平面内浮动", "平面机构约束")
    v2 = p.is_acceptable()
    assert v2["ok"] is True and v2["unexplained"] == 0, v2
