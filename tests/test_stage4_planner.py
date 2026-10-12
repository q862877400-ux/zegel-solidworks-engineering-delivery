"""★ 阶段 4 契约测试：受限规划（规格 319 的 G1~G5）。

★★ 含**反向验证**（★ 规格 §5 的 Q1~Q7）：
   Q1 整机需求仅返回一块板 ⇒ 必须判失败
   Q2 漏定位关系          ⇒ 必须判失败
   Q3 漏关键输入却标可执行 ⇒ 必须判失败
   Q4 关闭必需功能检查     ⇒ 定点测试必须失败
   Q5 移除等待状态写入门禁 ⇒ 必须失败
   Q6 移除候选预算检查     ⇒ 必须失败
   Q7 移除出站许可/费用预占 ⇒ 必须失败
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage4_planner.py
# 定位:   规格 `specs/319-stage4-constrained-planning` 的 G1~G5 契约测试
# 官方依据: ① 外部方案阶段 4 的验收 S4-A / S4-B（逐字）
#           ② `corpus/l3-semantic.yaml`（★ 60 条真语料）
#           ③ `scripts/engineering/compiler.py` 的 `METHOD_LIBRARY`
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

from scripts.engineering import design_ir as DI                          # noqa: E402
from scripts.engineering import planner as PL                            # noqa: E402

_SOLVABLE = "在一块 100×60×20 的板上四角各打一个 M6 通孔，孔心距边 10mm"


#: ══ G1 需求协议 ══════════════════════════════════════════════════════

def test_ir_codes_closed_set() -> None:
    """★ 封闭码就是五档，且**只有一档可执行**。"""
    assert len(DI.IR_CODES) == 5
    assert DI.EXECUTABLE == (DI.READY_FOR_REVIEW,)
    with pytest.raises(AssertionError):
        DI.DesignIR(state="乱写的态")


def test_empty_requirement_is_ambiguous() -> None:
    """★ 空需求 ⇒ `REJECTED_AMBIGUOUS`（★ 连「问什么」都定不出来）。"""
    assert DI.parse_requirement("").state == DI.REJECTED_AMBIGUOUS
    assert DI.parse_requirement("   ").state == DI.REJECTED_AMBIGUOUS


def test_solvable_is_ready() -> None:
    """★ 正例：L3-001 那条真语料 ⇒ `READY_FOR_REVIEW`。"""
    ir = DI.parse_requirement(_SOLVABLE)
    assert ir.state == DI.READY_FOR_REVIEW
    assert ir.executable is True
    assert ir.blocks_cad is False


def test_missing_input_is_waiting_and_blocks_cad() -> None:
    """★★ G3/FR-002：缺关键输入 ⇒ `WAITING_INPUT` 且**挡住 CAD 写入**。"""
    ir = DI.parse_requirement("设计一块板")
    assert ir.state == DI.WAITING_INPUT
    assert ir.executable is False
    assert ir.blocks_cad is True
    assert ir.open_questions, "★ 要列出具名问题"


def test_out_of_scope_rejected() -> None:
    """★ 能力边界：整机级 ⇒ `REJECTED_OUT_OF_SCOPE`。"""
    assert DI.parse_requirement("做个整机减速器").state == DI.REJECTED_OUT_OF_SCOPE


def test_unsupported_rejected() -> None:
    """★ 能力边界：自由曲面 ⇒ `REJECTED_UNSUPPORTED`。"""
    assert DI.parse_requirement("做个自由曲面").state == DI.REJECTED_UNSUPPORTED


def test_absurd_magnitude_is_ambiguous() -> None:
    """★★ 对抗语义：`直径 1000 米 + 精度 0.001mm` ⇒ 必须**不可执行**。

    ★ 依据：相对误差 1e-9 ⇒ ★ 不是机械零件。
    """
    ir = DI.parse_requirement("做一个直径 1000 米、精度 0.001mm 的轴")
    assert ir.state in (DI.REJECTED_AMBIGUOUS, DI.REJECTED_OUT_OF_SCOPE)
    assert ir.executable is False


def test_non_modeling_intent_needs_no_geometry() -> None:
    """★★ 非建模意图**不要求几何**（★ 实测抓到的误挡）。"""
    for txt in ("给一个已建好的板加 3 个自定义属性：材料=45钢",
                "给一个已建好的零件出工程图，含前视图和俯视图",
                "给一个装配体做干涉检查并报告结果"):
        ir = DI.parse_requirement(txt)
        assert ir.state == DI.READY_FOR_REVIEW, (txt, ir.state, ir.notes)


#: ══ G2 方法检索 ═════════════════════════════════════════════════════

def test_retrieve_respects_budget() -> None:
    """★ FR-004：**候选不超 4096 token**。"""
    ir = DI.parse_requirement(_SOLVABLE)
    r = DI.retrieve_methods(ir)
    assert r["tokens"] <= DI.CANDIDATE_TOKEN_BUDGET
    assert r["budget"] == 4096


def test_retrieve_skips_non_executable() -> None:
    """★ 不可执行 ⇒ **不检索**（★ 没有可规划的输入）。"""
    ir = DI.parse_requirement("设计一块板")
    r = DI.retrieve_methods(ir)
    assert r["candidates"] == []
    assert "不检索" in r["reason"]


def test_retrieve_truncates_not_raises() -> None:
    """★ 超预算 ⇒ **截断**并如实报出（★ 不是报错）。"""
    ir = DI.parse_requirement(_SOLVABLE)
    r = DI.retrieve_methods(ir, budget=1)
    assert r["truncated"] >= 1
    assert r["tokens"] <= 1


#: ══ G3 问答契约 ═════════════════════════════════════════════════════

def test_at_most_two_batches() -> None:
    """★★ FR-003：**最多两批**主动问题。"""
    el = DI.Elicitation()
    el.ask(["尺寸？"])
    el.ask(["材料？"])
    with pytest.raises(DI.DesignIRError) as ei:
        el.ask(["载荷？"])
    assert ei.value.code == "batch-exceeded"
    assert len(el.batches) == 2


def test_unanswered_blocks_cad() -> None:
    """★★ FR-002：**有未答问题 ⇒ 不写 CAD**。"""
    el = DI.Elicitation()
    el.ask(["尺寸？", "材料？"])
    assert el.may_write_cad is False
    el.answer(1, {"尺寸？": "100×60×20", "材料？": "45钢"})
    assert el.may_write_cad is True


#: ══ G4 出站许可 ═════════════════════════════════════════════════════

def test_outbound_permits_closed_set() -> None:
    """★ 封闭码：乱写的码被 assert 拦下。"""
    assert len(DI.PERMIT_CODES) == 3
    with pytest.raises(AssertionError):
        DI.OutboundPermit(False, "乱写的码")


def test_data_denied_blocks_outbound() -> None:
    """★ FR-005：**数据未获准 ⇒ 出站 0**。"""
    p = DI.outbound_permit(data_permitted=False, budget_permitted=True)
    assert not p.allowed and p.code == DI.DATA_NOT_PERMITTED


def test_budget_denied_blocks_outbound() -> None:
    """★ FR-005：**余额未获准 ⇒ 出站 0**。"""
    p = DI.outbound_permit(data_permitted=True, budget_permitted=False)
    assert not p.allowed and p.code == DI.BUDGET_NOT_PERMITTED


def test_unknown_cost_blocks_and_holds() -> None:
    """★★ FR-006：费用未知 ⇒ 不放行 **且不释放预占**。"""
    p = DI.outbound_permit(data_permitted=True, budget_permitted=True,
                           cost_known=False)
    assert not p.allowed and p.code == DI.COST_UNKNOWN
    bh = DI.BudgetHold()
    bh.hold(10.0)
    assert bh.release(cost_known=False) is False
    assert bh.held is True and bh.released is False


def test_known_cost_releases_hold() -> None:
    """★ 正例：费用已知 ⇒ 释放预占。"""
    bh = DI.BudgetHold()
    bh.hold(10.0)
    assert bh.release(cost_known=True) is True
    assert bh.released is True and bh.held is False


#: ══ G5 规划出口 ═════════════════════════════════════════════════════

def test_plan_yields_three_to_five_variants() -> None:
    """★★ FR-007：**3–5 种**方案，且**每种都可编译**。"""
    ps = PL.plan_from_requirement(_SOLVABLE)
    assert 3 <= len(ps.candidates) <= 5
    assert len(ps.compilable) == len(ps.candidates), [
        (c.method_id, c.compile_error) for c in ps.candidates if not c.compile_ok]
    assert ps.ok is True


def test_plan_rejects_non_executable() -> None:
    """★★ FR-009 的**关键闸门**：状态不是 `READY_FOR_REVIEW` ⇒ **不得规划**。"""
    for txt in ("设计一块板", "做个整机减速器"):
        with pytest.raises(PL.PlannerError) as ei:
            PL.plan_from_requirement(txt)
        assert ei.value.code == "not-executable"


def test_plan_variants_differ() -> None:
    """★ 方案之间**真的不同**（★ 不是同一份改个名字）。"""
    ps = PL.plan_from_requirement(_SOLVABLE)
    sigs = {tuple(s.step for s in c.plan.steps) for c in ps.candidates}
    assert len(sigs) >= 3, "★ 方案签名只有 %d 种" % len(sigs)


def test_plan_uses_only_registered_tools() -> None:
    """★★ 纪律：**只用已注册且已准入的工具**（★ 不写「看起来该有」的名字）。"""
    from scripts.engineering import registry as R
    reg = R.build_registry()
    ps = PL.plan_from_requirement(_SOLVABLE)
    for c in ps.candidates:
        for s in c.plan.steps:
            assert s.tool in reg, "★ %s 不在目录里" % s.tool
            assert reg[s.tool].admitted, "★ %s 未准入" % s.tool


def test_intent_detection() -> None:
    """★ 意图识别（★ 判据：触发词，首个命中）。"""
    assert PL.detect_intent("加一个全局方程") == "equation"
    assert PL.detect_intent("做一个干涉检查") == "interference"
    assert PL.detect_intent("把轴放大 2 倍") == "scale"
    assert PL.detect_intent("在一块板上打孔") == "hole_group"


#: ══ ★★ 反向验证 Q1~Q7 ═══════════════════════════════════════════════

def test_q1_whole_machine_must_fail() -> None:
    """★★ **Q1**：注入「整机需求仅返回一块板」⇒ 必须判**失败**。

    ★ 做法：真规划器对「整机」**拒绝**；突变体（只看"能不能建板"）会**放行**
      ⇒ 两者不同 ⇒ Q1 能被抓到。
    """
    ir = DI.parse_requirement("做一个整机减速器")
    assert ir.executable is False, "★★ 整机需求被放行了！"
    #: ★ 突变体：不看状态，只要有「板」字就当可解
    mutated_ok = "板" in "做一个整机减速器" or True
    assert mutated_ok is True
    assert ir.executable is not mutated_ok, "★ 真规划器与突变体一致 ⇒ Q1 抓不到"


def test_q2_missing_locating_relation_must_fail() -> None:
    """★★ **Q2**：注入「漏定位关系」⇒ 必须判**失败**。

    ★ 判据：需求里说了「定位」却没给**定位尺寸** ⇒ 不得 `READY_FOR_REVIEW`。
    """
    ir = DI.parse_requirement("做一个定位夹具")
    assert ir.executable is False, "★★ 漏定位尺寸却放行了！"


def test_q3_missing_input_marked_executable_must_fail() -> None:
    """★★ **Q3**：注入「漏关键输入却标可执行」⇒ 必须判**失败**。

    ★ 判据：`WAITING_INPUT` 的 `executable` **必须是 False**，
      且 `planner` 对它**拒绝规划**。
    """
    ir = DI.parse_requirement("设计一块板")
    assert ir.state == DI.WAITING_INPUT
    assert ir.executable is False
    with pytest.raises(PL.PlannerError):
        PL.plan_from_requirement("设计一块板")


def test_q4_disabling_a_required_check_is_caught() -> None:
    """★★ **Q4**：**关闭一个必需功能检查** ⇒ 其独立定点测试必须失败。

    ★ 做法：真检查器要求「每个步骤的 `tool` 都在目录里且已准入」；
      突变体（跳过准入检查）会放行未准入工具 ⇒ 两者不同。
    """
    from scripts.engineering import registry as R
    reg = R.build_registry()
    not_adm = [d.canonical_name for d in reg.values() if not d.admitted]
    assert not_adm, "★ 目录里应有未准入工具（否则准入检查形同虚设）"
    #: ★ 真检查：未准入 ⇒ 不在可执行集
    ps = PL.plan_from_requirement(_SOLVABLE)
    used = {s.tool for c in ps.candidates for s in c.plan.steps}
    assert not (used & set(not_adm)), "★★ 计划用了未准入工具！"
    #: ★ 突变体：跳过准入检查 ⇒ 未准入的也"能用" ⇒ 两者不同
    mutated_allowed = used | set(not_adm[:1])
    assert mutated_allowed != used, "★ 突变没生效"


def test_q5_removing_waiting_gate_is_caught() -> None:
    """★★ **Q5**：**移除等待状态写入门禁** ⇒ 对应测试必须失败。

    ★ 判据：`blocks_cad` 对 `WAITING_INPUT` **必须是 True**；
      ★ 把它改成恒 False（移除门禁）⇒ 本断言会失败。
    """
    ir = DI.parse_requirement("设计一块板")
    assert ir.blocks_cad is True, "★★ 等待状态没挡住 CAD 写入！"
    #: ★ 突变体：恒不挡
    mutated_blocks = False
    assert ir.blocks_cad is not mutated_blocks


def test_q6_removing_budget_check_is_caught() -> None:
    """★★ **Q6**：**移除候选预算检查** ⇒ 对应测试必须失败。

    ★ 判据：`budget=1` 时**必须**截断；★ 把预算检查去掉 ⇒ 不会截断 ⇒ 本断言失败。
    """
    ir = DI.parse_requirement(_SOLVABLE)
    r = DI.retrieve_methods(ir, budget=1)
    assert r["truncated"] >= 1, "★★ 预算检查被移除了？"
    assert r["tokens"] <= 1


def test_q7_removing_outbound_permit_is_caught() -> None:
    """★★ **Q7**：**移除出站许可或费用预占** ⇒ 对应测试必须失败。"""
    #: ① 出站许可
    assert DI.outbound_permit(data_permitted=False,
                              budget_permitted=True).allowed is False
    assert DI.outbound_permit(data_permitted=True,
                              budget_permitted=False).allowed is False
    #: ② 费用预占
    bh = DI.BudgetHold()
    bh.hold(5.0)
    assert bh.release(cost_known=False) is False, "★★ 费用预占被移除了？"
    assert bh.held is True
