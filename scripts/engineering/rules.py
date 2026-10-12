"""★ EC02 领域规则与确定性计算 —— **证据（KS）与判定（代码）物理分开**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC02**（★ T01–T08 逐字）
#         `specs/304-ec02-rules-and-standards/spec.md`（★ 8 FR · 8 V）
#         `specs/304-ec02-rules-and-standards/baseline.md` §二（★ **KS 引擎实测**：★ LLM 401 ⇒ `is_valid: false`）
# 定位:   ★ **EC02** 的确定性规则与计算层。★★★ 计划 §5 EC02 逐字要求：
#           「★ **不让检索片段直接当规则执行**」
#         ★★ 本会话实测（★ `baseline.md` §二）：★ KS 引擎 `healthy` 但 **LLM 不可用（401）**
#           ⇒ ★★ **「检索能回证据」≠「推理可用」** ⇒ ★★★ **判定必须由本模块的确定性代码做**。
# 官方依据: ★ 标准条款的**出处**由 KS 引擎给（★ 本模块**不编条款号**）；
#           ★ 本模块只做**确定性算术**与**登记模型**。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 不碰 COM · ★ 不调 LLM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Verdict", "Effectiveness", "ObligationKind", "UnknownReason",
    "StandardRef", "Rule", "RuleDecision", "RuleRegistry",
    "tolerance_stack_worst_case", "tolerance_stack_rss",
    "hole_edge_margin", "shaft_strength", "power_efficiency_margin",
    "applicability_lookup", "version_impact",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★ 三态判定（★ **只有 `pass` 是「通过」**）
# ══════════════════════════════════════════════════════════════════════

class Verdict:
    """★★ 判定（★ **封闭词表** —— ★ 与 EC00/EC01 同族：★ `unknown` 不放行）。"""

    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"                       #: ★★ **不得当通过**（★ FR-001）
    NEEDS_CLARIFICATION = "needs_clarification"   #: ★★ 未知类别 ⇒ **问**，★ 不是「无标准适用」

    ALL = (PASS, FAIL, UNKNOWN, NEEDS_CLARIFICATION)
    #: ★★★ **只有这个算「通过」**
    RELEASING = (PASS,)


class Effectiveness:
    """★ 标准效力（★ **与 KS 引擎的四色对齐** —— ★ `baseline.md` §二 实测）。"""

    EFFECTIVE = "effective"          #: ★ 🟢 现行有效（★ KS 实测 **8946**）
    UPCOMING = "upcoming"            #: ★ 🟡 即将实施（★ KS 实测 **11**）
    WITHDRAWN = "withdrawn"          #: ★ 🔴 在用已废止（★ KS 实测 **4**）
    REFERENCE = "reference"          #: ★ 🔵 参考资料（★ KS 实测 **16**）
    UNKNOWN = "unknown"              #: ★ ⚪ 状态未知

    ALL = (EFFECTIVE, UPCOMING, WITHDRAWN, REFERENCE, UNKNOWN)
    #: ★★★ **只有现行有效能作为硬规则依据**（★ V2）
    BINDING = (EFFECTIVE,)


class ObligationKind:
    """★★ 义务种类（★ EC02-T03 逐字：★「**不用 GB/T 标签替代法律适用判断**」）。"""

    MANDATORY = "mandatory"          #: ★ 强制义务（★ 法规/强制性标准）
    CONTRACTUAL = "contractual"      #: ★ 合同要求
    RECOMMENDED = "recommended"      #: ★ 推荐标准（★ **GB/T 多数是这类**）
    ENTERPRISE = "enterprise"        #: ★ 企业规范
    EXPERIENCE = "experience"        #: ★ 经验规则

    ALL = (MANDATORY, CONTRACTUAL, RECOMMENDED, ENTERPRISE, EXPERIENCE)
    #: ★★ **能产生「硬判定」的只有前两类**
    HARD = (MANDATORY, CONTRACTUAL)


class UnknownReason:
    """★★ **`unknown` 的原因**（★ 逐字承计划 §5 EC02 验收：「过期、缺源、域外、统计假设缺失」）。"""

    EXPIRED = "standard_not_effective"       #: ★ 过期 / 未生效
    NO_SOURCE = "missing_source"             #: ★ 缺源
    OUT_OF_SCOPE = "out_of_applicability"    #: ★ 域外
    NO_STATISTICAL_BASIS = "missing_statistical_basis"   #: ★ 统计假设缺失
    NO_THRESHOLD = "missing_threshold"       #: ★ 缺阈值

    ALL = (EXPIRED, NO_SOURCE, OUT_OF_SCOPE, NO_STATISTICAL_BASIS, NO_THRESHOLD)


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★ 标准登记模型（★ FR-002）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class StandardRef:
    """★★ 标准引用（★ **出处** —— ★ 本模块**不编**条款号，★ 由 KS 引擎给）。

    ★★ 字段逐字承计划 §5 EC02-T02：「★ 标准号、版本、实施/废止状态**查证日期**、许可、
      适用设备、条款索引、证据类型」。
    """

    standard_no: str                     #: ★ 如 `GB/T 1803-2003`
    clause: str                          #: ★ 条款号（★ 如 `3.2.4`）
    effectiveness: str = Effectiveness.UNKNOWN
    verified_on: str = ""                #: ★★ **查证日期**（★ 没有它 ⇒ 缺源）
    license_note: str = ""               #: ★ 许可说明
    applicable_devices: tuple = ()       #: ★ 适用设备类别
    evidence_kind: str = ""              #: ★ 证据类型（★ `clause` / `table` / `annex`）
    evidence_url: str = ""               #: ★ KS 给的**原文链接**（★ 可点开）
    doc_id: str = ""                     #: ★ KS 的 `doc_id`
    clause_revision_id: str = ""         #: ★ KS 的条款修订 id

    def is_binding(self) -> bool:
        """★★ **只有现行有效 + 有查证日期 + 有出处**才算可依据。"""
        return (self.effectiveness in Effectiveness.BINDING
                and bool(self.verified_on)
                and bool(self.standard_no) and bool(self.clause))


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★ 规则（★ FR-001 · FR-006）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Rule:
    """★ 规则（★ 逐字承 EC02-T01：「★ 输入单位、适用域、来源、版本、阈值、输出和 `unknown`」）。"""

    id: str
    statement: str                                    #: ★ 规则陈述
    obligation: str = ObligationKind.RECOMMENDED      #: ★ 义务种类（★ T03）
    unit: str = ""                                    #: ★ 输入单位（★ T01）
    applicable_devices: tuple = ()                    #: ★ 适用域
    source: StandardRef | None = None                 #: ★ 来源
    threshold: float | None = None                    #: ★ 阈值
    #: ★★ **反例**（★ T06 逐字：「规则决策保留依据与**反例**」）
    counterexample: str = ""
    #: ★★ **优先级**（★ T06：★「矛盾规则按**优先级**和适用性处理，**不能多数投票**」）
    priority: int = 0
    #: ★★ **统计假设**（★ 需要它而没给 ⇒ `unknown` —— ★ V5）
    statistical_basis: str = ""

    def applies_to(self, device_class: str) -> bool:
        """★ 适用性（★ **空适用域 = 不适用任何类别** —— ★ 不默认「通用」）。"""
        return device_class in (self.applicable_devices or ())


@dataclass
class RuleDecision:
    """★ 判定结果（★ **必须带依据** —— ★ T06）。"""

    rule_id: str
    verdict: str
    basis: str = ""                                   #: ★ 依据（★ 出处 + 计算过程）
    unknown_reason: str = ""                          #: ★ 若是 `unknown`，★ 给原因
    numbers: dict = field(default_factory=dict)       #: ★ 可复核的中间量

    def is_releasing(self) -> bool:
        return self.verdict in Verdict.RELEASING


class RuleRegistry:
    """★ 规则登记表（★ **出处可查** —— ★ V1）。"""

    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}

    def add(self, rule: Rule) -> None:
        self._rules[rule.id] = rule

    def get(self, rule_id: str) -> Rule | None:
        return self._rules.get(rule_id)

    def all(self) -> list[Rule]:
        return list(self._rules.values())

    # ── 单条判定 ────────────────────────────────────────────────────
    def decide(self, rule_id: str, device_class: str, *,
               value: float | None = None) -> RuleDecision:
        """★★★ **判定**（★ 确定性 —— ★ 不调 LLM · ★ 不把检索片段当规则）。

        ★★★ 四条**不能通过**的路（★ 逐字承计划验收）：
          ① **过期**（★ 效力非现行）⇒ `unknown/standard_not_effective`
          ② **缺源**（★ 没标准号/条款/查证日期）⇒ `unknown/missing_source`
          ③ **域外**（★ 设备类别不在适用域）⇒ `unknown/out_of_applicability`
          ④ **统计假设缺失**（★ 该规则需要它而没给）⇒ `unknown/missing_statistical_basis`
        """
        r = self._rules.get(rule_id)
        if r is None:
            return RuleDecision(rule_id, Verdict.UNKNOWN, basis="★ 规则未登记",
                                unknown_reason=UnknownReason.NO_SOURCE)
        #: ① 来源与效力
        src = r.source
        if src is None or not src.is_binding():
            reason = UnknownReason.NO_SOURCE
            if src is not None and src.effectiveness not in Effectiveness.BINDING:
                reason = UnknownReason.EXPIRED
            return RuleDecision(rule_id, Verdict.UNKNOWN,
                                basis="★ 来源不可依据（★ 标准号/条款/查证日期/效力 有一项不满足）",
                                unknown_reason=reason)
        #: ② 适用域
        if not r.applies_to(device_class):
            return RuleDecision(rule_id, Verdict.UNKNOWN,
                                basis="★ 设备类别 %r 不在适用域 %r" % (device_class,
                                                                     list(r.applicable_devices)),
                                unknown_reason=UnknownReason.OUT_OF_SCOPE)
        #: ③ 阈值
        if r.threshold is None:
            return RuleDecision(rule_id, Verdict.UNKNOWN, basis="★ 规则没有阈值",
                                unknown_reason=UnknownReason.NO_THRESHOLD)
        #: ④ 统计假设（★ 只有**需要**它时才要求 —— ★ 由规则自己声明）
        if r.statistical_basis == "" and r.unit == "statistical":
            return RuleDecision(rule_id, Verdict.UNKNOWN,
                                basis="★ 该规则需要统计假设但未声明",
                                unknown_reason=UnknownReason.NO_STATISTICAL_BASIS)
        if value is None:
            return RuleDecision(rule_id, Verdict.UNKNOWN, basis="★ 没有实测值可判",
                                unknown_reason=UnknownReason.NO_THRESHOLD)
        #: ★★ 判定（★ 带**可复核的中间量**）
        ok = value <= r.threshold
        basis = ("★ %s：★ 实测 %g %s ≤ 阈值 %g ⇒ pass（★ 出处：%s %s）"
                 % (r.id, value, r.unit or "-", r.threshold, src.standard_no, src.clause))
        return RuleDecision(rule_id, Verdict.PASS if ok else Verdict.FAIL, basis=basis,
                            numbers={"value": value, "threshold": r.threshold})

    # ── 矛盾仲裁（★ **不能多数投票**）──────────────────────────────
    def arbitrate(self, rule_ids: list[str], device_class: str, *,
                  value: float | None = None) -> RuleDecision:
        """★★★ **矛盾仲裁**（★ EC02-T06 逐字：★「按**优先级和适用性**处理，★ **不能多数投票**」）。

        ★★ 规则：★ 先筛**适用**的 ⇒ ★ 再取**优先级最高**的 ⇒ ★ **优先级相同 ⇒ `unknown`**
          （★ **不投票** —— ★ 平局就是没结论）。
        """
        decisions = [self.decide(rid, device_class, value=value) for rid in rule_ids]
        #: ★★ **先看适用性**（★ 域外的直接淘汰 —— ★ 不参与仲裁）
        usable = [d for d in decisions if d.unknown_reason != UnknownReason.OUT_OF_SCOPE]
        if not usable:
            return RuleDecision("+".join(rule_ids), Verdict.UNKNOWN,
                                basis="★ 全部规则都域外 ⇒ 无适用规则",
                                unknown_reason=UnknownReason.OUT_OF_SCOPE)
        #: ★★ **按优先级**（★ 不是按票数）
        ranked = sorted(usable, key=lambda d: -(self._rules[d.rule_id].priority
                                                if d.rule_id in self._rules else 0))
        top = ranked[0]
        top_rule = self._rules.get(top.rule_id)
        top_pri = top_rule.priority if top_rule else 0
        #: ★★★ **优先级相同 ⇒ 平局 ⇒ `unknown`**（★ **不投票**）
        tied = [d for d in ranked
                if (self._rules.get(d.rule_id).priority if self._rules.get(d.rule_id) else 0)
                == top_pri]
        if len(tied) > 1:
            return RuleDecision("+".join(rule_ids), Verdict.UNKNOWN,
                                basis="★★ 优先级相同（%r）⇒ **不投票**，平局即无结论" % top_pri,
                                unknown_reason=UnknownReason.NO_THRESHOLD)
        return top


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 第一批确定性算法（★ FR-004）
# ══════════════════════════════════════════════════════════════════════

def tolerance_stack_worst_case(dims: list[tuple[float, float]]) -> dict:
    """★★ **尺寸链极限法**（★ 逐字承 EC02-T04）。

    ★ 输入：★ `[(名义值, 公差)]`（★ 单位**米**）· ★ 输出：★ 闭合环的**极限**。
    ★★ 判据：★ 极限法**不需要统计假设** ⇒ ★ `statistical_basis_required=False`。
    """
    if not dims:
        return {"ok": False, "reason": "★ 空尺寸链"}
    nominal = sum(n for n, _t in dims)
    tol = sum(abs(t) for _n, t in dims)
    return {"ok": True, "nominal": nominal, "tolerance": tol,
            "upper": nominal + tol, "lower": nominal - tol,
            "method": "worst_case",
            "statistical_basis_required": False}


def tolerance_stack_rss(dims: list[tuple[float, float]], *,
                        distribution: str = "") -> dict:
    """★★★ **RSS**（★ 逐字承 EC02-T04：★「**明确统计假设的** RSS」）。

    ★★★ **关键（★ V5）**：★ **不给 `distribution` ⇒ 回 `unknown`**，★ **不算**。
    ★★ 依据（★ 计划验收逐字）：★「★ **统计假设缺失均不能返回通过**」。
    """
    if not dims:
        return {"ok": False, "reason": "★ 空尺寸链"}
    if not distribution.strip():
        return {"ok": False, "verdict": Verdict.UNKNOWN,
                "reason": "★ RSS 需要**统计假设**（★ 分布未声明）⇒ 不计算",
                "unknown_reason": UnknownReason.NO_STATISTICAL_BASIS}
    nominal = sum(n for n, _t in dims)
    #: ★ RSS：★ 公差**平方和开根**（★ 假设各环独立同分布）
    rss = math.sqrt(sum(t * t for _n, t in dims))
    return {"ok": True, "nominal": nominal, "tolerance": rss,
            "upper": nominal + rss, "lower": nominal - rss,
            "method": "rss", "distribution": distribution,
            "assumption": "★ 各环**独立**且**同分布**（★ %s）" % distribution}


def hole_edge_margin(hole_d: float, hole_x: float, part_half_width: float) -> dict:
    """★★ **孔边距**（★ 逐字承 EC02-T04：★「孔边距/工具可达性」）。

    ★ 边距 = ★ 件半宽 − (孔心距 + 孔半径) ⇒ ★ **负值 = 孔出边**。
    """
    radius = hole_d / 2.0
    margin = part_half_width - (abs(hole_x) + radius)
    return {"ok": True, "margin": margin, "radius": radius,
            "edge_distance": abs(hole_x) + radius,
            "sufficient": margin > 0.0,
            #: ★★ 工具可达性（★ 边距**至少要**留出孔半径 ⇒ ★ 那是常见工艺下限）
            "tool_accessible": margin >= radius}


def shaft_strength(torque: float, diameter: float, allowable_shear: float) -> dict:
    """★★ **基本轴强度**（★ 逐字承 EC02-T04）。

    ★ 扭转剪应力：★ `τ = 16T / (π d³)` ⇒ ★ 与许用剪应力比。
    ★★ **单位**：★ `T` = **N·m** · ★ `d` = **m** · ★ `allowable_shear` = **Pa**。
    """
    if diameter <= 0:
        return {"ok": False, "reason": "★ 直径必须为正"}
    tau = 16.0 * torque / (math.pi * diameter ** 3)
    return {"ok": True, "shear_stress": tau, "allowable": allowable_shear,
            "safety_factor": (allowable_shear / tau) if tau > 0 else float("inf"),
            "passes": tau <= allowable_shear,
            "formula": "tau = 16T / (pi d^3)"}


def power_efficiency_margin(input_power: float, output_power: float) -> dict:
    """★★ **传动功率/效率边界**（★ 逐字承 EC02-T04）。

    ★ 效率 `η = P_out / P_in` ⇒ ★ 必须在 `(0, 1]` 内。
    """
    if input_power <= 0:
        return {"ok": False, "reason": "★ 输入功率必须为正"}
    eta = output_power / input_power
    return {"ok": True, "efficiency": eta,
            "physically_valid": 0.0 < eta <= 1.0,
            "loss": input_power - output_power}


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ 适用性矩阵（★ FR-008 · V8）
# ══════════════════════════════════════════════════════════════════════

def applicability_lookup(matrix: dict, device_class: str) -> dict:
    """★★★★★ **适用性矩阵查询**（★ EC02-T08 逐字：「★ 建立首个**限定设备类别**的适用性矩阵；
    ★ **未知类别返回待澄清**，★ **不能「无标准适用」**」）。

    ★★★ **本函数的核心区分**（★ 那是 V8 的全部意义）：
      · ★ **类别不认识** ⇒ `needs_clarification` —— ★★ **信息不足 ⇒ 该问**
      · ★ **类别认识、但确实没有适用标准** ⇒ `no_standard_applies` —— ★★ **那是一个判定，
        ★ 必须带依据**（★ 不能是默认值）
    ★★★ **⇒ 把这两者混起来，就是计划禁止的「无标准适用」** ✗
    """
    if device_class not in matrix:
        return {
            "verdict": Verdict.NEEDS_CLARIFICATION,
            "device_class": device_class,
            "standards": (),
            "basis": ("★ 设备类别 %r **不在**适用性矩阵里（★ 矩阵只覆盖 %r）"
                      "⇒ ★ 信息不足 ⇒ **待澄清**，★ 不是「无标准适用」"
                      % (device_class, sorted(matrix))),
            "no_standard_applies": False,          #: ★★★ **明确不是那个判定**
        }
    standards = tuple(matrix[device_class] or ())
    if not standards:
        return {
            "verdict": "no_standard_applies",      #: ★★ 这是一个**判定**（★ 不是「不知道」）
            "device_class": device_class,
            "standards": (),
            "basis": ("★ 类别 %r **已知**，★ 且矩阵里它的标准表**为空**"
                      "⇒ ★ 据矩阵判「无标准适用」（★ 有依据）" % device_class),
            "no_standard_applies": True,
        }
    return {
        "verdict": Verdict.PASS,                   #: ★ 有标准可用
        "device_class": device_class,
        "standards": standards,
        "basis": "★ 类别 %r 有 %d 条适用标准" % (device_class, len(standards)),
        "no_standard_applies": False,
    }


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★★ 标准版本变化的影响清单（★ FR-007 · EC02-T07）
# ══════════════════════════════════════════════════════════════════════

def version_impact(decisions: list[RuleDecision], registry: "RuleRegistry",
                   changed: dict) -> dict:
    """★★★★ **版本变化的影响清单**（★ EC02-T07 逐字：★「★ 标准版本变化形成**影响清单**；
    ★ 证据**自动标过期**；★ **不能只改数据库版本号**」）。

    ★★ 输入：
      · `decisions` —— ★ 已做出的判定（★ 每条带 `rule_id`）
      · `registry` —— ★ 规则表（★ 用来查每条规则**依据的是哪个标准号**）
      · `changed` —— ★ `{标准号: (旧版本, 新版本)}`

    ★★★ **输出**：★ 受影响的判定清单（★ **带原因**）+ ★ **自动标 `expired`**
      ⇒ ★★ **那就是「不能只改版本号」的意思** —— ★ 换版**必须**回头清点结论 ✓
    """
    affected: list[dict] = []
    unaffected: list[str] = []
    for d in decisions:
        rule = registry.get(d.rule_id)
        std = rule.source.standard_no if (rule and rule.source) else ""
        if std and std in changed:
            old, new = changed[std]
            affected.append({
                "rule_id": d.rule_id,
                "verdict_before": d.verdict,
                #: ★★★ **自动标过期** —— ★ 旧结论**不能**继续放行
                "verdict_after": Verdict.UNKNOWN,
                "expired": True,
                "standard_no": std,
                "version_change": {"from": old, "to": new},
                "basis": ("★ 规则 %s 依据的 %s 从 %s 换到 %s ⇒ 旧结论**失效**，"
                          "★ 需按新版本重判（★ **不能只改版本号**）"
                          % (d.rule_id, std, old, new)),
            })
        else:
            unaffected.append(d.rule_id)
    return {
        "ok": True,
        "affected": affected,
        "unaffected": unaffected,
        "affected_count": len(affected),
        #: ★★ **换版不是「改个号」** —— ★ 有受影响就必须重判
        "requires_rejudgement": bool(affected),
    }
