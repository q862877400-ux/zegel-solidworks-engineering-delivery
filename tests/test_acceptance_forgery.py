"""★ 四个已知伪造手法必须被拒绝。

判据来源：`specs/349-e1-e7-acceptance/spec.md` 的 FR-009 / SC-002。

这四条不是假设的漏洞 —— 它们是**在本仓实测过**的伪造手法
（出处：`docs/state/facts/R-engineering-path.md` R-04 / R-05 / R-06 / R-09）。
每条对应一个既有估算器，它们的输出可以被**零成本伪造**成「合格」。

本文件证明：新判定器**不接受**这些伪造。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.e1_sketch import judge_sketch_constraint  # noqa: E402
from engineering.acceptance.e4_assembly import judge_assembly  # noqa: E402
from engineering.acceptance.e5_e6_drawing import judge_drawing  # noqa: E402
from engineering.acceptance.e7_provenance import judge_provenance  # noqa: E402
from engineering.acceptance.result import Status  # noqa: E402
from engineering.acceptance.samples import (  # noqa: E402
    bad_e1_duplicate_relation,
    bad_e4_duplicate_mate,
    bad_e5_empty_evidence,
    bad_e7_no_citations,
)

REQ = "R-forgery"


def test_伪造1_重复关系不得算出零自由度() -> None:
    """★★ R-04：同一条草图关系重复 8 次。

    ★ 伪造原理：`part_loop.DofPlan.total_dof` 的公式是 `2E − R − D`，
      重复贴同一条关系会把 DOF 压到 0，而 `is_acceptable` 返回 True。
    ★ 本判据：判定器**按关系唯一性去重**后再算，并直接拒绝含重复的输入。
    """
    obs = bad_e1_duplicate_relation()
    #: 先确认样件确实是「重复 8 次」的形态
    assert len(obs.values["relations"]) == 8
    assert len(set(obs.values["relations"])) == 1

    res = judge_sketch_constraint(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 重复关系必须被拒，实得 %s" % res.status.value
    assert "重复" in res.reason


def test_伪造1_对照_原始公式确实会被骗() -> None:
    """★★ 反证：直接吃 `2E−R−D` 的估算器**会**把 8 条重复关系算成 DOF=0。

    ★ 这条测试的作用不是测新判定器，而是**钉住旧估算器的行为**，
      证明上面那条负例不是在防一个不存在的洞。
    """
    from engineering.part_loop import DofPlan

    #: 4 实体 ⇒ 8 个自由度；8 条**重复**关系 ⇒ 8 − 8 = 0
    plan = DofPlan(entities=4, relations=list(["same"] * 8), dimensions=[])
    assert plan.total_dof() == 0, "★ 旧估算器在这里应算出 0（这就是洞）"
    #: `is_acceptable()` 返回 dict（含 `ok`），不是 bool
    assert plan.is_acceptable()["ok"] is True, "★ 旧估算器在这里应判可接受（这就是洞）"


def test_伪造2_重复配合不得判全约束() -> None:
    """★★ R-05：同一对组件重复贴 6 次 coincident。

    ★ 伪造原理：`assembly.ConstraintGraph.total_dof` 按配合类型扣常数，
      重复贴会把 DOF 压到 0，verdict 判 `fully_constrained` 且 `releasing=True`。
    ★ 本判据：判定器检查**同一对组件 + 同一配合类型**的重复。
    """
    obs = bad_e4_duplicate_mate()
    assert len(obs.values["mates"]) == 6

    res = judge_assembly(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 重复配合必须被拒，实得 %s" % res.status.value
    assert "重复" in res.reason


def test_伪造2_对照_扣常数确实会被骗() -> None:
    """★★ 反证：按配合类型扣常数的估算器**会**把 6 条重复 coincident 算成 DOF=0。"""
    from engineering.assembly import ConstraintGraph, Mate, MateKind

    g = ConstraintGraph()
    #: 一个可动组件 = 6 个自由度；6 条 coincident 各扣 3 ⇒ 封顶到 0
    for _ in range(6):
        g.mates.append(Mate(kind="coincident", a="pin", b="base"))
    assert g.total_dof() == 0, "★ 旧估算器在这里应算出 0（这就是洞）"
    assert g.verdict()["verdict"] == "fully_constrained", "★ 旧估算器判全约束（这就是洞）"
    assert MateKind.REMOVES["coincident"] == 3


def test_伪造3_空证据不得给覆盖率一() -> None:
    """★★ R-06：图纸义务标了 covered 但 evidence 是空串。

    ★ 伪造原理：`drawing_obligations.coverage` 只数 `covered` 布尔，
      不看 `evidence`；`mark_covered` 的 evidence 默认空串 ⇒ 覆盖率仍为 1.0。
    ★ 本判据：判定器要求每条 covered 都有**非空证据**。
    """
    obs = bad_e5_empty_evidence()
    res = judge_drawing(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 空证据必须被拒，实得 %s" % res.status.value
    assert "证据" in res.reason


def test_伪造3_对照_旧覆盖率确实会给出一点零() -> None:
    """★★ 反证：`coverage()` 对空 evidence 的 covered 仍返回 ratio=1.0。"""
    from engineering.drawing_obligations import (
        DrawingObligation,
        coverage,
        mark_covered,
    )

    obls = [DrawingObligation(name="孔位"), DrawingObligation(name="基准A")]
    mark_covered(obls, "孔位")          #: ★ evidence 用默认空串
    mark_covered(obls, "基准A")
    cov = coverage(obls)
    assert cov["ratio"] == 1.0, "★ 旧覆盖率在这里应给出 1.0（这就是洞）"
    assert cov["ok"] is True


def test_伪造4_两个布尔不得给_pass() -> None:
    """★★ R-09：只传 `formula_ok=True` / `applicability_ok=True` + 来源标签。

    ★ 伪造原理：`rule_service.evaluate_rule` 的 PASS 分支不写 `outputs`、
      不写 `citations` ⇒ 一条 PASS 可以不含任何数字和任何条款。
    ★ 本判据：判定器要求有引用、有可复算输出。
    """
    obs = bad_e7_no_citations()
    res = judge_provenance(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 空引用必须被拒，实得 %s" % res.status.value
    assert "引用" in res.reason or "溯源" in res.reason


def test_伪造4_对照_旧规则服务确实会给_pass() -> None:
    """★★ 反证：`evaluate_rule` 在两个布尔为真时返回 PASS，且 outputs/citations 为空。"""
    from engineering.rule_service import RuleRequest, evaluate_rule

    req = RuleRequest(
        rule_id="T-1",
        inputs=[{"name": "t", "value": 20, "unit": "mm", "source": "requirement"}],
        application_context={"device": "plate"},
        required_standard_editions=("GB/T 1804-2000",),
        evidence_bundle_ref="ev-1",
    )
    res = evaluate_rule(
        req,
        formula_ok=True,
        applicability_ok=True,
        authority_status={"source": "official_status_record"},
    )
    assert res.verdict == "PASS", "★ 旧规则服务在这里应给 PASS（这就是洞）"
    assert res.outputs == {}, "★ 旧规则服务在这里 outputs 为空（这就是洞）"
    assert res.citations == [], "★ 旧规则服务在这里 citations 为空（这就是洞）"


@pytest.mark.parametrize(
    "name,judge,factory",
    [
        ("R-04 重复关系", judge_sketch_constraint, bad_e1_duplicate_relation),
        ("R-05 重复配合", judge_assembly, bad_e4_duplicate_mate),
        ("R-06 空证据", judge_drawing, bad_e5_empty_evidence),
        ("R-09 空引用", judge_provenance, bad_e7_no_citations),
    ],
)
def test_四类伪造手法全部被拒(name, judge, factory) -> None:
    """★ SC-002：四条负例一起过。"""
    res = judge(factory(), requirement_id=REQ)
    assert res.status is Status.FAIL, "★ %s 未被拒绝，实得 %s" % (name, res.status.value)
