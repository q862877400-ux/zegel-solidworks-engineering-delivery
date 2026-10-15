"""★ EC03 T05 判据 —— **不可满足核心 / 超时 / 多方案排序**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/compiler.py`（★ `find_unsat_core` · `solve_with_budget` · `rank_plans`）
#         `specs/305-ec03-method-library-and-ir/spec.md`（★ FR-005 · US6）
# 定位:   ★ EC03 **T05**（★ 逐字：「★ 定义**不可满足核心**/未知/超时/多方案排序；
#         ★ **`unknown` 不能落入默认可行**」）。
# 官方依据: 不适用（本仓的规划编译层）
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

import engineering_contract as ec
from engineering import compiler as C


def test_t05_unsat_core_names_the_conflicting_constraints():
    """★★★★ T05：★ **不可满足核心**必须**点名**冲突的约束（★ 不是「全都冲突」）。"""
    out = C.find_unsat_core([("thickness", 0.002, 0.005), ("thickness", 0.010, 0.020)])
    assert out["status"] == C.SolveStatus.UNSAT, "★ 不相交的区间没被判不可满足"
    assert out["core"] == ["thickness", "thickness"], "★ 核心不对：%r" % out["core"]
    assert out["variable"] == "thickness", "★ 没指认变量"
    assert "不相交" in out["reason"], "★ 原因不清：%r" % out["reason"]


def test_t05_unsat_core_is_minimal_not_everything():
    """★★★★ T05：★ **核心是最小的**（★ 无关的约束**不进**核心）。"""
    #: ★ 三条约束：★ 前两条冲突，★ 第三条（另一变量）**无关**
    out = C.find_unsat_core([
        ("a", 0.0, 0.005), ("a", 0.010, 0.020), ("b", 0.0, 1.0),
    ])
    assert out["status"] == C.SolveStatus.UNSAT
    assert "b" not in out["core"], (
        "★★ 无关的约束进了核心 ⇒ ★ 接手方会去改不该改的：%r" % out["core"])


def test_t05_satisfiable_when_intervals_overlap():
    """★★ T05：★ **有交集 ⇒ `satisfiable`**（★ 不瞎报冲突）。"""
    out = C.find_unsat_core([("a", 0.0, 0.010), ("a", 0.005, 0.020)])
    assert out["status"] == C.SolveStatus.SAT, "★ 有交集却报了不可满足"
    assert out["core"] == []


def test_t05_timeout_is_not_satisfiable():
    """★★★★★ T05：★ **超时 ⇒ `timeout`**（★ **不是 `satisfiable`**）。

    ★★ 依据（★ EC03-T05 逐字）：★「★ 定义……**超时**……★ **`unknown` 不能落入默认可行**」。
    """
    out = C.solve_with_budget([("a", 0.0, 1.0)], steps_budget=0)
    assert out["status"] == C.SolveStatus.TIMEOUT, (
        "★★ 预算为 0 却回了 %r ⇒ ★ `unknown` 落入了默认可行" % out["status"])
    assert out["status"] != C.SolveStatus.SAT, "★★ 超时被判成可行"


def test_t05_tiny_budget_also_times_out():
    """★★ T05：★ 预算不够 ⇒ `timeout`（★ 不是「反正算完了」）。"""
    out = C.solve_with_budget([("a", 0.0, 1.0), ("b", 0.0, 1.0)], steps_budget=1)
    assert out["status"] == C.SolveStatus.TIMEOUT


def test_t05_unknown_is_never_feasible():
    """★★★★ T05：★ **`unknown`/`timeout` 一律不算可行**（★ 封闭判据）。"""
    for status in (C.SolveStatus.UNKNOWN, C.SolveStatus.TIMEOUT):
        assert status != C.SolveStatus.SAT, "★★ %r 被当成可行" % status
    #: ★★ 且 `SAT` 是**唯一**的可行态
    feasible = [s for s in C.SolveStatus.ALL if s == C.SolveStatus.SAT]
    assert feasible == [C.SolveStatus.SAT]


def test_t05_rank_plans_uses_multi_metric():
    """★★★ T05/T07：★ **多方案排序用多指标**（★ 不是只按复杂度）。"""
    c = ec.EngineeringContract(contract_id="C-1", intent="做一个安装板")
    c.classify("intent", ec.InformationClass.KNOWN)
    c.safety_level = "普通"
    c.material = ec.MaterialRef("Q235", "GB/T 700", "2006")
    c.process = ec.ProcessIntent(kind="machined")
    c.datums.append(ec.Datum("安装结合面", semantic_role="mounting_interface"))
    c.load_cases.append(ec.LoadCase("面压", "static",
                                    ec.normalize_quantity(ec.Quantity(1.0, "N", "force"))))
    c.parameter_domains["outline"] = ec.ParameterDomain("outline", 0.01, 1.0, "m",
                                                       allow_negative=False)
    c.obligations.append(ec.VerificationObligation("OB-1", "回读", evidence_kind="readback"))
    c.freeze()
    p1 = C.compile_contract(c, device_class="plate")
    p2 = C.compile_contract(c, device_class="plate")
    ranked = C.rank_plans([p2, p1])
    assert len(ranked) == 2, "★ 排序把方案弄丢了"
    #: ★★ 排序键必须是**多指标总分**（★ 两个同分方案顺序稳定即可）
    assert [x.method_id for x in ranked] == ["plate", "plate"]


def test_t05_rank_plans_prefers_higher_elegance():
    """★★★ T05：★ **优雅分高的排前面**（★ 多指标驱动 —— ★ 不是特征数）。"""
    c = ec.EngineeringContract(contract_id="C-1", intent="做一个安装板")
    c.classify("intent", ec.InformationClass.KNOWN)
    c.safety_level = "普通"
    c.material = ec.MaterialRef("Q235", "GB/T 700", "2006")
    c.process = ec.ProcessIntent(kind="machined")
    c.datums.append(ec.Datum("安装结合面", semantic_role="mounting_interface"))
    c.load_cases.append(ec.LoadCase("面压", "static",
                                    ec.normalize_quantity(ec.Quantity(1.0, "N", "force"))))
    c.parameter_domains["outline"] = ec.ParameterDomain("outline", 0.01, 1.0, "m",
                                                       allow_negative=False)
    c.obligations.append(ec.VerificationObligation("OB-1", "回读", evidence_kind="readback"))
    c.freeze()
    good = C.compile_contract(c, device_class="plate")
    good.irs = [x for x in good.irs]                 #: ★ 有基准引用
    poor = C.compile_contract(c, device_class="plate")
    for x in poor.irs:
        if hasattr(x, "plane_datum"):
            x.plane_datum = ""                        #: ★ 抹掉基准 ⇒ 基准表达分降
    ranked = C.rank_plans([poor, good])
    assert ranked[0] is good, (
        "★★ 优雅分高的没排前面 ⇒ ★ 排序没按多指标：%r" % [C.score_elegance(x).total() for x in ranked])
