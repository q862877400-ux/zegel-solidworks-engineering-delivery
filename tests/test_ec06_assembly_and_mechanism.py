"""★ EC06 判据 —— 约束图 / 干涉扫描 / 公差链 / 维护（★ 离线部分）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/assembly.py`（★ EC06 的离线部分）
#         `specs/308-ec06-assembly-and-mechanism/spec.md`
# 定位:   ★ EC06 的**离线判据**（★ 逐字承计划 §5 EC06 的「验收」）。
# 官方依据: 不适用（本仓的装配分析层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import assembly as A
from engineering import rules as R


# ══════════════════════════════════════════════════════════════════════
# V1 · 四类约束状态**分开**
# ══════════════════════════════════════════════════════════════════════

def test_v1_five_constraint_states_exist():
    """★★★ V1：★ **五类必须齐**（★ 逐字承 EC06-T02：★「★ 区分**欠约束、冗余、过约束和
    预期运动自由度**」+ ★ 完全约束）。"""
    assert set(A.DofVerdict.ALL) == {
        "under_constrained", "redundant", "over_constrained",
        "expected_motion", "fully_constrained"}, (
        "★ 五类不齐：%r" % (A.DofVerdict.ALL,))


def test_v1_fully_constrained_is_releasing():
    """★★ V1：★ **完全约束 ⇒ 可放行**（★ 自由度 0）。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "plate"),
               A.Mate(A.MateKind.PARALLEL, "base", "plate"),
               A.Mate(A.MateKind.DISTANCE, "base", "plate")],
        target_dof=0)
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.FULLY_CONSTRAINED, "★ 判成 %r" % out["verdict"]
    assert out["releasing"] is True


def test_v1_under_constrained_is_not_releasing():
    """★★★ V1：★ **欠约束 ⇒ 不放行**（★ 且**说清**还有几个没标注）。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("slider")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "slider")],
        target_dof=3)
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.UNDER_CONSTRAINED, "★ 判成 %r" % out["verdict"]
    assert out["releasing"] is False
    assert "没标注" in out["reason"], "★ 没说清为什么"


def test_v1_expected_motion_is_releasing():
    """★★★★ V1：★ **预期运动 ⇒ 可放行**（★ 自由度 > 0 **但逐条标注了**）。

    ★★ 依据（★ EC06-T02 逐字）：★「★ 区分……★ **预期运动自由度**」——
      ★★ 它**不是**欠约束 ✓
    ★ 自由度算法：★ `Σ(非地件组件自由度) − Σ(配合消去)` = ★ `6 − 3 = 3`。
    """
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("slider")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "slider")],
        target_dof=3,
        #: ★★ **逐条标注** —— ★ 有 3 个自由度就要有 3 条
        expected_motions=[
            "★ 沿 X 滑移（★ 行程 ±50 mm —— ★ 功能要求）",
            "★ 绕 X 转动（★ 浮动接头允许）",
            "★ 绕 Y 转动（★ 浮动接头允许）",
        ])
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.EXPECTED_MOTION, "★ 判成 %r" % out["verdict"]
    assert out["releasing"] is True, "★★ 有意保留的运动被判不放行 ⇒ ★ 太保守"
    assert out["dof"] == 3, "★ 自由度应**仍 = 3**（★ 有意保留 ≠ 锁死）"


def test_v1_partially_annotated_motion_is_under_constrained():
    """★★★ V1：★ **只标了一部分 ⇒ 仍是欠约束**（★ 逐条都要交代）。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("slider")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "slider")],
        target_dof=3,
        expected_motions=["★ 只标了一个（★ 还有两个没交代）"])
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.UNDER_CONSTRAINED, (
        "★★ 只标了一部分却判 `expected_motion` ⇒ ★ 没交代的自由度被蒙混过去")
    assert out["expected_count"] == 1


def test_v1_redundant_is_distinct_from_over_constrained():
    """★★★ V1：★ **冗余 ≠ 过约束**（★ 两者必须**分开报** —— ★ 那是本任务的意义）。

    ★★ 依据（★ EC06-T02 逐字）：★「★ 区分**欠约束、冗余、过约束**和预期运动自由度」
      ⇒ ★★ **冗余**（★ 重复但不冲突）与**过约束**（★ 冲突）是**两回事** ✗
    """
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "plate"),
               A.Mate(A.MateKind.COINCIDENT, "base", "plate", redundant=True)],
        target_dof=0)
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.REDUNDANT, (
        "★★ 冗余被判成 %r ⇒ ★ 两类没分开" % out["verdict"])
    assert "redundant" in out, "★ 没列出冗余的那条"
    #: ★★ 且**冗余 ≠ 冲突**
    assert "conflicts" not in out, "★★ 冗余被当成了冲突"


def test_v1_over_constrained_reports_conflicts():
    """★★★ V1：★ **过约束 ⇒ 列出冲突**（★ 且**不放行**）。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "plate",
                      conflicts_with=("distance-10mm",))],
        target_dof=0)
    out = g.verdict()
    assert out["verdict"] == A.DofVerdict.OVER_CONSTRAINED
    assert out["releasing"] is False
    assert out["conflicts"], "★ 没列出冲突"


# ══════════════════════════════════════════════════════════════════════
# V2 · 目标自由度与实际一致
# ══════════════════════════════════════════════════════════════════════

def test_v2_target_must_equal_actual():
    """★★★★ V2：★ **目标自由度与实际一致**（★ 逐字承验收）。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "plate")],
        target_dof=3)
    out = g.target_matches_actual()
    assert out["ok"] is True, "★ 目标 3 = 实际 3 却判不一致：%r" % out
    #: ★★ **不一致 ⇒ 报出来**
    g.target_dof = 0
    bad = g.target_matches_actual()
    assert bad["ok"] is False, "★★ 目标 0 ≠ 实际 3 却判一致"
    assert "不一致" in bad["reason"]


def test_v2_missing_target_is_not_a_pass():
    """★★★ V2：★ **没声明目标 ⇒ 不算「一致」**（★ 不能默认通过）。"""
    g = A.ConstraintGraph(components=[A.Component("plate")])
    out = g.target_matches_actual()
    assert out["ok"] is False, "★★ 没声明目标却判「一致」"
    assert out["target"] is None


# ══════════════════════════════════════════════════════════════════════
# V3 · 错轴向位置必被检测
# ══════════════════════════════════════════════════════════════════════

def test_v3_axis_mismatch_is_detected():
    """★★★★★ V3：★ **错轴向位置必被检测**（★ 逐字承验收）。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "plate", axis="X"),
               A.Mate(A.MateKind.DISTANCE, "base", "plate", axis="Y", value=0.01)],
        target_dof=0)
    errs = g.axis_errors()
    assert errs, "★★★ 同一对组件上轴向不一致却**没检出** ⇒ ★ 违反验收"
    assert set(errs[0]["axes"]) == {"X", "Y"}


def test_v3_consistent_axes_pass():
    """★★ V3 **负例**：★ **轴向一致 ⇒ 无错**。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.COINCIDENT, "base", "plate", axis="X"),
               A.Mate(A.MateKind.DISTANCE, "base", "plate", axis="X", value=0.01)],
        target_dof=0)
    assert g.axis_errors() == [], "★ 轴向一致却报了错"


def test_v3_parallel_and_perpendicular_are_exempt():
    """★★ V3：★ `PARALLEL`/`PERPENDICULAR` **本身表达轴关系** ⇒ ★ 不算轴向冲突。"""
    g = A.ConstraintGraph(
        components=[A.Component("base", is_ground=True), A.Component("plate")],
        mates=[A.Mate(A.MateKind.PARALLEL, "base", "plate", axis="X"),
               A.Mate(A.MateKind.PERPENDICULAR, "base", "plate", axis="Y")],
        target_dof=0)
    assert g.axis_errors() == [], (
        "★★ 把 PARALLEL/PERPENDICULAR 当成轴向冲突 ⇒ ★ 会误报")


# ══════════════════════════════════════════════════════════════════════
# V4 · 干涉扫描：有限采样不冒充全域
# ══════════════════════════════════════════════════════════════════════

def test_v4_no_interference_without_full_proof_is_unknown():
    """★★★★★ V4：★ **无干涉但没有全域证明 ⇒ `unknown`**（★ 逐字承验收：

    「★ **无法证明全域的部分以 `coverage`/`unknown` 记录**」）。

    ★★★ **这条是本特性最要紧的**：★ **有限采样不能冒充连续全域证明** ✗
    """
    s = A.InterferenceScan(positions_scanned=100, is_full_domain_proof=False,
                           uncovered=["t=0.5~0.6 未扫"])
    out = s.verdict()
    assert out["verdict"] == "unknown", (
        "★★★ 采样 100 点无干涉就判 `%s` ⇒ ★ 把有限采样当全域证明" % out["verdict"])
    assert out["releasing"] is False, "★★ `unknown` 竟然放行"
    assert out["coverage"] < 1.0, "★ 覆盖率该 < 1"


def test_v4_interference_is_reported():
    """★★★★ V4：★ **检出干涉 ⇒ 报出来**（★ 且**不放行**）。"""
    s = A.InterferenceScan(positions_scanned=50,
                           interferences=[{"at": "t=0.3", "pair": ["a", "b"],
                                           "volume_mm3": 12.5}])
    out = s.verdict()
    assert out["verdict"] == "interference"
    assert out["releasing"] is False
    assert out["count"] == 1


def test_v4_full_proof_only_passes():
    """★★ V4：★ **只有**全域证明**才 `pass`**（★ 那几乎是解析可证的少数情况）。"""
    s = A.InterferenceScan(positions_scanned=1000, is_full_domain_proof=True)
    out = s.verdict()
    assert out["verdict"] == "pass", "★ 全域证明却没 pass：%r" % out
    assert out["releasing"] is True


def test_v4_coverage_of_empty_scan_is_zero_not_one():
    """★★★ V4：★ **没扫 ⇒ 覆盖率 0**（★ **不是 1** —— ★ 那会把「没做」说成「全做了」）。"""
    s = A.InterferenceScan()
    assert s.coverage() == 0.0, (
        "★★ 空扫描的覆盖率是 %r ⇒ ★ 「没做」被当成「全覆盖」" % s.coverage())
    assert s.verdict()["verdict"] == "unknown"


def test_v4_refinement_is_recorded():
    """★★ V4：★ **自适应局部加密必须留痕**（★ EC06-T04 逐字）。"""
    s = A.InterferenceScan(positions_scanned=10)
    s.refine("t=0.28~0.32", why="★ 该区间接近干涉阈值 ⇒ 加密")
    assert s.refined_intervals, "★ 加密没留痕"
    assert "加密" in s.refined_intervals[0]["why"]


# ══════════════════════════════════════════════════════════════════════
# V5 · 公差链（★ 复用 EC02 —— ★ 铁律 1）
# ══════════════════════════════════════════════════════════════════════

def test_v5_tolerance_chain_reuses_ec02_worst_case():
    """★★★ V5：★ **公差链复用 EC02 的极限法**（★ 不另写一套 —— ★ 铁律 1）。"""
    c = A.ToleranceChain("装配链", links=[(0.010, 0.0003), (0.020, 0.0004)],
                         method="worst_case")
    out = c.compute()
    #: ★★ **与 EC02 直调的结果逐字相同** ⇒ ★ 证明是复用
    direct = R.tolerance_stack_worst_case([(0.010, 0.0003), (0.020, 0.0004)])
    assert out == direct, "★★ 公差链的结果与 EC02 不一致 ⇒ ★ 可能另写了一套"


def test_v5_rss_without_assumption_returns_unknown():
    """★★★★ V5：★ **RSS 不声明统计假设 ⇒ `unknown`**（★ 承 EC02 的 V5）。"""
    c = A.ToleranceChain("装配链", links=[(0.010, 0.0003)], method="rss",
                         statistical_basis="")
    out = c.compute()
    assert out.get("verdict") == R.Verdict.UNKNOWN, (
        "★★ 没声明统计假设却算了 RSS：%r" % out)
    #: ★ 给了假设 ⇒ 能算
    ok = A.ToleranceChain("装配链", links=[(0.010, 0.0003)], method="rss",
                          statistical_basis="正态").compute()
    assert ok["ok"] is True


# ══════════════════════════════════════════════════════════════════════
# V6 · 维护检查
# ══════════════════════════════════════════════════════════════════════

def test_v6_maintenance_requires_checks():
    """★★★ V6：★ **一项都没查 ⇒ 不算通过**（★ 不能「没查=没问题」）。"""
    m = A.MaintenanceCheck()
    out = m.verdict()
    assert out["ok"] is False, "★★ 没检查任何一项却判通过"
    assert "一项都没检查" in out["reason"]


def test_v6_maintenance_reports_failed_items():
    """★★ V6：★ **不满足的项要具名**。"""
    m = A.MaintenanceCheck()
    m.add("紧固件可达", True)
    m.add("装拆次序", False, note="★ 内侧螺栓被挡住")
    out = m.verdict()
    assert out["ok"] is False
    assert [i["kind"] for i in out["failed"]] == ["装拆次序"]
    assert "装拆次序" in out["reason"]


def test_v6_all_satisfied_passes():
    """★★ V6 负例：★ **全满足 ⇒ 通过**。"""
    m = A.MaintenanceCheck()
    for k in ("紧固件可达", "装拆次序", "轴承安装", "润滑", "传感器调整", "维护空间"):
        m.add(k, True)
    assert m.verdict()["ok"] is True
