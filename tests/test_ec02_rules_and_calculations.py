"""★ EC02 判据（V1–V8）—— 规则出处 / 效力 / 域外 / 统计假设 / 算法独立复算 / 仲裁。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/rules.py`（★ EC02 的确定性规则与计算层）
#         `specs/304-ec02-rules-and-standards/spec.md`（★ 8 FR · 8 V）
#         `specs/304-ec02-rules-and-standards/baseline.md` §二（★ **KS 引擎实测**）
# 定位:   ★ EC02 的 **V1–V8**（★ 逐字承计划 §5 EC02 的「验收」）。
# 官方依据: ★ 标准条款的**出处**由 KS 引擎给（★ 本判据**不编条款号**，
#           ★ 用的样例标准号都来自本会话 `ks_effect_report` / `ks_answer` 的**真实读数**）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM · ★ 不调 LLM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import rules as R


def _ref(effectiveness: str = R.Effectiveness.EFFECTIVE, **kw) -> R.StandardRef:
    """★ 造一个**可依据**的标准引用（★ 默认现行有效 + 有查证日期）。"""
    base = dict(standard_no="GB/T 1803-2003", clause="1",
                effectiveness=effectiveness, verified_on="2026-10-10",
                evidence_kind="clause")
    base.update(kw)
    return R.StandardRef(**base)


def _rule(**kw) -> R.Rule:
    base = dict(id="R1", statement="孔边距不小于孔半径",
                obligation=R.ObligationKind.RECOMMENDED, unit="m",
                applicable_devices=("plate",), source=_ref(), threshold=0.010,
                counterexample="★ 边距 < 半径 ⇒ fail（★ 孔会破边）")
    base.update(kw)
    return R.Rule(**base)


# ══════════════════════════════════════════════════════════════════════
# V1 · 每条硬规则可查出处与适用域
# ══════════════════════════════════════════════════════════════════════

def test_v1_rule_without_source_cannot_pass():
    """★★★ V1：★ **缺源 ⇒ 不能 `pass`**（★ 计划验收逐字）。"""
    reg = R.RuleRegistry()
    reg.add(_rule(source=None))
    d = reg.decide("R1", "plate", value=0.005)
    assert d.verdict == R.Verdict.UNKNOWN, "★★ 无来源却判了 %s" % d.verdict
    assert d.unknown_reason == R.UnknownReason.NO_SOURCE


def test_v1_rule_without_clause_cannot_pass():
    """★★ V1：★ **没有条款号 ⇒ 不算可查出处**。"""
    reg = R.RuleRegistry()
    reg.add(_rule(source=_ref(clause="")))
    d = reg.decide("R1", "plate", value=0.005)
    assert d.verdict == R.Verdict.UNKNOWN
    assert d.unknown_reason == R.UnknownReason.NO_SOURCE


def test_v1_rule_without_verification_date_cannot_pass():
    """★★ V1：★ **没有查证日期 ⇒ 不算可查出处**（★ 标准效力会变）。"""
    reg = R.RuleRegistry()
    reg.add(_rule(source=_ref(verified_on="")))
    d = reg.decide("R1", "plate", value=0.005)
    assert d.verdict == R.Verdict.UNKNOWN, "★★ 没查证日期却通过了"
    assert d.unknown_reason == R.UnknownReason.NO_SOURCE


def test_v1_unregistered_rule_is_unknown():
    """★★ V1：★ **规则未登记 ⇒ `unknown`**（★ 不是默认通过）。"""
    d = R.RuleRegistry().decide("NOPE", "plate", value=0.001)
    assert d.verdict == R.Verdict.UNKNOWN


def test_v1_pass_carries_a_citable_basis():
    """★★★ V1：★ `pass` **必须带可查出处**（★ 依据里要有标准号与条款号）。"""
    reg = R.RuleRegistry()
    reg.add(_rule())
    d = reg.decide("R1", "plate", value=0.005)
    assert d.verdict == R.Verdict.PASS, "★ 应通过：%r" % d
    assert "GB/T 1803-2003" in d.basis and "1" in d.basis, (
        "★★ `pass` 的依据里没有出处 ⇒ ★ 不可查：%r" % d.basis)


# ══════════════════════════════════════════════════════════════════════
# V2 · 过期 ⇒ 不能通过
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("eff", [R.Effectiveness.WITHDRAWN, R.Effectiveness.UPCOMING,
                                 R.Effectiveness.REFERENCE, R.Effectiveness.UNKNOWN])
def test_v2_non_effective_standard_cannot_pass(eff):
    """★★★ V2：★ **非现行有效 ⇒ 不能 `pass`**（★ 逐字承计划验收：「★ 过期……不能返回通过」）。

    ★★ 四类**都不能**：★ 🔴 已废止 · ★ 🟡 即将实施 · ★ 🔵 参考资料 · ★ ⚪ 未知
      （★ 前三类**本会话 KS 实测**各有 **4 / 11 / 16** 条）。
    """
    reg = R.RuleRegistry()
    reg.add(_rule(source=_ref(effectiveness=eff)))
    d = reg.decide("R1", "plate", value=0.001)     #: ★ 值**明显合格**也不许过
    assert d.verdict == R.Verdict.UNKNOWN, (
        "★★ 效力 %r 却判了 %s ⇒ ★ 会把废止/未生效的标准当依据" % (eff, d.verdict))
    assert d.unknown_reason == R.UnknownReason.EXPIRED


def test_v2_only_effective_is_binding():
    """★★ V2：★ **只有 `effective` 在 `BINDING` 里**。"""
    assert R.Effectiveness.BINDING == (R.Effectiveness.EFFECTIVE,), (
        "★★ `BINDING` 不止一类 ⇒ ★ 可能放过未生效的：%r" % (R.Effectiveness.BINDING,))


# ══════════════════════════════════════════════════════════════════════
# V3 · 缺源 ⇒ 不能通过（★ 与 V1 同族，此处核**接口**）
# ══════════════════════════════════════════════════════════════════════

def test_v3_rule_interface_has_all_required_fields():
    """★★ V3：★ 规则接口必须有 T01 逐字要求的字段（★ 输入单位/适用域/来源/版本/阈值/输出/unknown）。"""
    r = _rule()
    for attr in ("unit", "applicable_devices", "source", "threshold"):
        assert hasattr(r, attr), "★ 规则缺字段 `%s`" % attr
    #: ★★ 「版本」由 `StandardRef.standard_no`（★ 含年号）+ `verified_on` **承载**
    assert r.source is not None and r.source.standard_no and r.source.verified_on
    #: ★★ 「unknown」由 `Verdict.UNKNOWN` + `UnknownReason` **承载**
    assert R.Verdict.UNKNOWN in R.Verdict.ALL
    assert len(R.UnknownReason.ALL) >= 4, "★ `unknown` 的原因太少"


# ══════════════════════════════════════════════════════════════════════
# V4 · 域外 ⇒ 不能通过
# ══════════════════════════════════════════════════════════════════════

def test_v4_out_of_scope_cannot_pass():
    """★★★ V4：★ **域外 ⇒ 不能 `pass`**（★ 逐字承计划验收）。"""
    reg = R.RuleRegistry()
    reg.add(_rule(applicable_devices=("plate",)))
    d = reg.decide("R1", "shaft", value=0.001)     #: ★ 值合格，★ 但**域外**
    assert d.verdict == R.Verdict.UNKNOWN, "★★ 域外却判了 %s" % d.verdict
    assert d.unknown_reason == R.UnknownReason.OUT_OF_SCOPE


def test_v4_empty_applicability_means_no_device():
    """★★★ V4：★ **空适用域 ⇒ 不适用任何类别**（★ **不默认「通用」**）。

    ★★ 依据（★ 计划 §5 EC02-T08 逐字）：★「★ 未知类别返回**待澄清**，★ **不能「无标准适用」**」
      —— ★★ 反过来，★ **空域也不该被当成「对所有类别都适用」** ✗
    """
    reg = R.RuleRegistry()
    reg.add(_rule(applicable_devices=()))
    d = reg.decide("R1", "plate", value=0.001)
    assert d.verdict == R.Verdict.UNKNOWN, (
        "★★ 空适用域被判成适用 ⇒ ★ 会拿一条不该用的规则去判")
    assert d.unknown_reason == R.UnknownReason.OUT_OF_SCOPE


# ══════════════════════════════════════════════════════════════════════
# V5 · 统计假设缺失 ⇒ 不能通过
# ══════════════════════════════════════════════════════════════════════

def test_v5_rss_without_distribution_returns_unknown():
    """★★★★★ V5：★ **RSS 不给分布 ⇒ `unknown`**（★ 逐字承计划验收：「★ 统计假设缺失……不能返回通过」）。"""
    out = R.tolerance_stack_rss([(0.010, 0.0001), (0.020, 0.0002)], distribution="")
    assert out.get("verdict") == R.Verdict.UNKNOWN, (
        "★★ 没声明统计假设却算了 RSS ⇒ ★ 会拿一个没依据的数当结论：%r" % out)
    assert out.get("unknown_reason") == R.UnknownReason.NO_STATISTICAL_BASIS


def test_v5_rss_with_distribution_computes():
    """★★ V5：★ **给了分布才算**（★ 且写明假设）。"""
    out = R.tolerance_stack_rss([(0.010, 0.0003), (0.020, 0.0004)], distribution="正态")
    assert out["ok"] is True, "★ 给了分布应能算：%r" % out
    assert "独立" in out["assumption"], "★★ 没写明统计假设 ⇒ ★ 不可复核"


def test_v5_worst_case_does_not_need_statistics():
    """★★ V5：★ **极限法不需要统计假设**（★ 那是它与 RSS 的本质区别）。"""
    out = R.tolerance_stack_worst_case([(0.010, 0.0003), (0.020, 0.0004)])
    assert out["statistical_basis_required"] is False, (
        "★ 极限法被标成需要统计假设 ⇒ ★ 两者没分开")


# ══════════════════════════════════════════════════════════════════════
# V6 · 算法有不共享实现的参考值
# ══════════════════════════════════════════════════════════════════════

def test_v6_worst_case_reference_is_independent():
    """★★★ V6：★ 极限法**另有独立复算**（★ 本判据**不调实现**，★ 自己算）。"""
    dims = [(0.010, 0.0003), (0.020, 0.0004), (0.005, 0.0001)]
    #: ★★ 独立算（★ 手写 —— ★ 不共享被测实现的任何函数）
    nominal = 0.010 + 0.020 + 0.005
    tol = 0.0003 + 0.0004 + 0.0001
    out = R.tolerance_stack_worst_case(dims)
    assert abs(out["nominal"] - nominal) < 1e-15, "★ 名义值不符"
    assert abs(out["tolerance"] - tol) < 1e-15, "★ 公差不符"
    assert abs(out["upper"] - (nominal + tol)) < 1e-15
    assert abs(out["lower"] - (nominal - tol)) < 1e-15


def test_v6_rss_reference_is_independent():
    """★★★ V6：★ RSS **另有独立复算**（★ 手写 `sqrt(Σt²)`）。"""
    dims = [(0.010, 0.0003), (0.020, 0.0004)]
    out = R.tolerance_stack_rss(dims, distribution="正态")
    expected = math.sqrt(0.0003 ** 2 + 0.0004 ** 2)
    assert abs(out["tolerance"] - expected) < 1e-15, (
        "★ RSS 不符：%r vs %r" % (out["tolerance"], expected))


def test_v6_shaft_strength_reference_is_independent():
    """★★★ V6：★ 轴强度**另有独立复算**（★ 手写 `16T/(πd³)`）。"""
    T, d, allow = 100.0, 0.030, 40e6
    out = R.shaft_strength(T, d, allow)
    expected = 16.0 * T / (math.pi * d ** 3)
    assert abs(out["shear_stress"] - expected) < 1e-6, (
        "★ 剪应力不符：%r vs %r" % (out["shear_stress"], expected))
    assert out["passes"] is (expected <= allow)


def test_v6_hole_edge_margin_reference_is_independent():
    """★★★ V6：★ 孔边距**另有独立复算**。"""
    out = R.hole_edge_margin(hole_d=0.010, hole_x=0.050, part_half_width=0.100)
    expected = 0.100 - (0.050 + 0.005)
    assert abs(out["margin"] - expected) < 1e-15, "★ 边距不符：%r" % out["margin"]
    assert out["sufficient"] is (expected > 0)


def test_v6_power_efficiency_reference_is_independent():
    """★★★ V6：★ 效率**另有独立复算**，★ 且查**物理有效域**。"""
    out = R.power_efficiency_margin(1000.0, 920.0)
    assert abs(out["efficiency"] - 0.92) < 1e-15
    assert out["physically_valid"] is True
    #: ★★ **η > 1 ⇒ 物理不可能**（★ 那是负例）
    bad = R.power_efficiency_margin(1000.0, 1100.0)
    assert bad["physically_valid"] is False, (
        "★★ 效率 > 1 被判成有效 ⇒ ★ 永动机通过了")


def test_v6_reference_values_are_not_taken_from_the_implementation():
    """★★★★ V6：★ **参考值不取自被测实现**（★ 承 EC00 的**双盲**纪律）。

    ★★ 判据：★ 本文件**不许** `from engineering.rules import` 里那些**被测函数**
      ⇒ ★ 只用模块本身（`import ... as R`）+ **手写常量**。
    """
    import ast
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8", errors="replace"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "engineering.rules":
            names = {a.name for a in node.names}
            assert names <= {"rules"}, (
                "★★ 本判据**直接导入了被测函数** %r ⇒ ★ 参考值可能取自实现（★ 双盲）" % names)


def test_v6_monotonicity_and_bounds():
    """★★ V6：★ **单调性 + 边界值 + 区间**检查（★ 逐字承 EC02-T05）。"""
    #: ★ 单调：★ 公差越大 ⇒ RSS 结果越大
    small = R.tolerance_stack_rss([(0.01, 0.0001)], distribution="正态")["tolerance"]
    big = R.tolerance_stack_rss([(0.01, 0.0002)], distribution="正态")["tolerance"]
    assert big > small, "★ RSS 不单调"
    #: ★ 边界：★ 直径 0 ⇒ 拒绝（★ 不是除零崩）
    assert R.shaft_strength(1.0, 0.0, 1e6)["ok"] is False, "★ 直径 0 应被拒"
    #: ★ 区间：★ RSS ≤ 极限法（★ 独立同分布时）
    dims = [(0.01, 0.0003), (0.02, 0.0004)]
    assert (R.tolerance_stack_rss(dims, distribution="正态")["tolerance"]
            <= R.tolerance_stack_worst_case(dims)["tolerance"]), (
        "★ RSS 大于极限法 ⇒ ★ 至少有一个算错了")


# ══════════════════════════════════════════════════════════════════════
# V7 · 矛盾规则按优先级，不多数投票
# ══════════════════════════════════════════════════════════════════════

def test_v7_higher_priority_wins():
    """★★★ V7：★ **优先级高的胜**（★ 不是票数多的胜 —— ★ EC02-T06 逐字）。"""
    reg = R.RuleRegistry()
    reg.add(_rule(id="LOW", threshold=0.001, priority=1))
    reg.add(_rule(id="HIGH", threshold=0.100, priority=10))
    d = reg.arbitrate(["LOW", "HIGH"], "plate", value=0.050)
    assert d.rule_id == "HIGH", "★★ 不是按优先级 ⇒ 胜出的是 %r" % d.rule_id


def test_v7_tie_is_unknown_not_a_vote():
    """★★★★★ V7：★ **优先级相同 ⇒ `unknown`**（★ **不投票**）。

    ★★ 依据（★ 计划 §5 EC02-T06 逐字）：
      「★ 矛盾规则按**优先级和适用性**处理，★ **不能多数投票**」。
    ★★★ **⇒ 两票对一票也不该「按多数」判** —— ★ 平局就是没结论。
    """
    reg = R.RuleRegistry()
    reg.add(_rule(id="A", threshold=0.001, priority=5))
    reg.add(_rule(id="B", threshold=0.100, priority=5))
    d = reg.arbitrate(["A", "B"], "plate", value=0.050)
    assert d.verdict == R.Verdict.UNKNOWN, (
        "★★★ 优先级相同却判了 %s ⇒ ★ 那是**多数投票**（★ T06 明文禁止）" % d.verdict)
    assert "不投票" in d.basis, "★ 没写明「不投票」⇒ ★ 不可复核"


def test_v7_out_of_scope_rules_are_eliminated_first():
    """★★ V7：★ **域外的规则先淘汰**（★ 适用性优先于优先级）。"""
    reg = R.RuleRegistry()
    reg.add(_rule(id="FAR", applicable_devices=("pneumatic",), threshold=0.001, priority=99))
    reg.add(_rule(id="NEAR", applicable_devices=("plate",), threshold=0.100, priority=1))
    d = reg.arbitrate(["FAR", "NEAR"], "plate", value=0.050)
    assert d.rule_id == "NEAR", (
        "★★ 域外的高优先级规则胜出 ⇒ ★ 会拿不适用的规则判：%r" % d.rule_id)


def test_v7_all_out_of_scope_gives_out_of_scope_unknown():
    """★★ V7：★ **全部域外 ⇒ `out_of_applicability`**（★ 不是随便挑一个）。"""
    reg = R.RuleRegistry()
    reg.add(_rule(id="X", applicable_devices=("shaft",), priority=1))
    d = reg.arbitrate(["X"], "plate", value=0.001)
    assert d.verdict == R.Verdict.UNKNOWN
    assert d.unknown_reason == R.UnknownReason.OUT_OF_SCOPE


# ══════════════════════════════════════════════════════════════════════
# V8 · 未知类别 ⇒ 待澄清，不能「无标准适用」
# ══════════════════════════════════════════════════════════════════════

def test_v8_unknown_device_class_asks_for_clarification():
    """★★★★★ V8：★ **未知类别 ⇒ `needs_clarification`**，★ **不是「无标准适用」**。

    ★★ 依据（★ 计划 §5 EC02-T08 逐字）：
      「★ 建立首个限定设备类别的适用性矩阵；★ 未知类别返回**待澄清**，★ **不能「无标准适用」**」。
    ★★★ **为什么**：★ 「无标准适用」是一个**判定**（★ 要**有依据**）；
      ★★ 而「我不认识这个类别」是**信息不足** ⇒ ★ **该问，不该答**。
    """
    matrix = {"plate": ("GB/T 1803-2003",), "shaft": ("GB/T 1803-2003",)}
    out = R.applicability_lookup(matrix, "unknown_thing")
    assert out["verdict"] == R.Verdict.NEEDS_CLARIFICATION, (
        "★★ 未知类别被判成 %r ⇒ ★ 那是「无标准适用」（★ V8 明文禁止）" % out["verdict"])
    assert out.get("no_standard_applies") is not True, (
        "★★★ 未知类别被标成「无标准适用」⇒ ★ 把「信息不足」当成了「判定」")


def test_v8_no_standard_applies_requires_evidence():
    """★★★ V8：★ **「无标准适用」是一个判定 ⇒ 必须**有依据****（★ 不是默认值）。"""
    matrix = {"plate": ()}                       #: ★ plate **确实**没有适用标准
    out = R.applicability_lookup(matrix, "plate")
    #: ★★ 已知类别 + 空标准表 ⇒ ★ 可以判「无标准适用」，★ **但要带依据**
    assert out["verdict"] in (R.Verdict.NO_STANDARD if hasattr(R.Verdict, "NO_STANDARD")
                              else "no_standard_applies",
                              R.Verdict.NEEDS_CLARIFICATION), (
        "★ 已知类别 + 空表 ⇒ 应有明确判定：%r" % out)
    assert out.get("basis"), "★★ 「无标准适用」没有依据 ⇒ ★ 那是默认值不是判定"


def test_v8_known_class_returns_its_standards():
    """★★ V8：★ 已知类别 ⇒ ★ 回它的标准清单（★ 矩阵可用）。"""
    matrix = {"plate": ("GB/T 1803-2003",)}
    out = R.applicability_lookup(matrix, "plate")
    assert out["standards"] == ("GB/T 1803-2003",), "★ 矩阵没生效：%r" % out


# ══════════════════════════════════════════════════════════════════════
# 附 · 义务种类（★ T03：★ 不用 GB/T 标签替代法律适用判断）
# ══════════════════════════════════════════════════════════════════════

def test_obligation_kinds_are_separated():
    """★★ T03：★ **强制/合同/推荐/企业/经验** 必须**分开**（★ 逐字承 EC02-T03）。"""
    assert set(R.ObligationKind.ALL) == {
        "mandatory", "contractual", "recommended", "enterprise", "experience"}, (
        "★ 五类没分齐：%r" % (R.ObligationKind.ALL,))
    assert R.ObligationKind.HARD == (R.ObligationKind.MANDATORY,
                                     R.ObligationKind.CONTRACTUAL), (
        "★★ 「硬判定」的类不止强制与合同 ⇒ ★ 推荐标准可能被当成强制")


def test_recommended_standard_is_not_hard():
    """★★★ T03：★ **推荐标准（GB/T）不是硬义务**（★ 逐字：「不用 GB/T 标签替代法律适用判断」）。"""
    assert R.ObligationKind.RECOMMENDED not in R.ObligationKind.HARD, (
        "★★ GB/T 被当成硬义务 ⇒ ★ 违反 T03")
