"""★ EC09 CAE 与拓扑 —— 参考解 / 反力平衡 / 网格收敛 / 版本闭合 / 求解成功≠工程通过。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC09**（★ T01–T08 逐字）
#         `specs/311-ec09-cae-and-topology/spec.md`
#         `scripts/engineering/rules.py`（★ EC02 的独立复算口径 —— ★ **复用**）
# 定位:   ★ **EC09** 的实现。★★★ 计划 §5 EC09 验收逐字：「★ 参考解、**反力平衡**、**网
#           格关注量**、**材料/载荷版本闭合**； ★ **优化后复分析**；★ **求解成功不是工程
#           通过**； ★ **没有 validation 证据不写「真实工况已验证」**」
# 官方依据: 不适用（本仓的 CAE 可信判据层 —— ★ **不调求解器**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 求解器调用在工具面）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "SolveStatus",
    "VerificationKind",
    "AnalysisIR",
    "ReferenceSolution",
    "ReactionBalance",
    "MeshConvergence",
    "VersionClosure",
    "ValidationScope",
    "engineering_verdict",
    "beam_tip_deflection_reference",
    "beam_bending_stress_reference",
    "SensitivityScan",
    "beam_stress_under_load",
]


#: ★★★ **求解状态**（★ 逐字承验收：★「★ **求解成功不是工程通过**」）
class SolveStatus:
    """★★ **求解器返回的状态**（★ **与工程结论分开** —— ★ 那是验收的核心）。"""

    SOLVED = "solved"  #: ★ 求解器说解出来了
    NOT_RUN = "not_run"
    FAILED = "failed"
    DIVERGED = "diverged"

    ALL = (SOLVED, NOT_RUN, FAILED, DIVERGED)


class VerificationKind:
    """★★ **三级证据**（★ 逐字承 EC09-T05：★「★ **分开计算 verification、物理 validation
    和不确定性**；★ **无实体/可信实验时只写验证范围**」）。"""

    VERIFICATION = "verification"  #: ★ 计算验证（★ 数值对不对）
    VALIDATION = "validation"  #: ★★ **物理验证**（★ 与真实对照过）
    UNCERTAINTY = "uncertainty"  #: ★ 不确定性

    ALL = (VERIFICATION, VALIDATION, UNCERTAINTY)


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ 独立参考解（★ EC09-T01 · V1）
# ══════════════════════════════════════════════════════════════════════


def beam_tip_deflection_reference(
    force_n: float, length_m: float, e_pa: float, i_m4: float
) -> float:
    """★★★ **悬臂梁端部挠度**（★ 材料力学闭式解 —— ★ **独立于求解器**）。

    ★ 公式：★ `δ = F L³ / (3 E I)`。
    ★★ 依据（★ EC09-T01 逐字）：★「★ 建立简单梁/板静力基准，★ **固定理论或可信独立参考解**」。
    """
    if e_pa <= 0 or i_m4 <= 0:
        return float("nan")
    return force_n * length_m**3 / (3.0 * e_pa * i_m4)


def beam_bending_stress_reference(moment_nm: float, c_m: float, i_m4: float) -> float:
    """★★ **梁弯曲应力**（★ 闭式解）：★ `σ = M c / I`。"""
    if i_m4 <= 0:
        return float("nan")
    return moment_nm * c_m / i_m4


@dataclass
class ReferenceSolution:
    """★★★★ **参考解**（★ 逐字承验收：★「★ **参考解**……」）。

    ★★★ **它必须**独立****：★ 来源是**闭式解/手册**，★ **不是**求解器的输出 ✗
    """

    name: str
    value: float
    unit: str = ""
    #: ★★ **来源**（★ 如 `★ 材料力学闭式解 δ = FL³/(3EI)`）
    source: str = ""
    #: ★★★ **是不是**独立**的**（★ `True` = 闭式解/手册；★ `False` = 从求解器读的 ⇒ **不
    #: 算**）
    independent: bool = True

    def is_usable(self) -> dict:
        """★★★ **可用？**（★ 独立 + 有来源 + 有限值）。"""
        if not self.independent:
            return {
                "ok": False,
                "reason": "★★★ 参考解**不独立**（★ 它取自求解器）⇒ ★ 那是「自己验自己」",
            }
        if not str(self.source).strip():
            return {"ok": False, "reason": "★★ 参考解没有来源"}
        if not math.isfinite(self.value):
            return {"ok": False, "reason": "★★ 参考解不是有限值"}
        return {"ok": True, "reason": "★ 独立参考解可用（★ 来源：%s）" % self.source}


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 反力平衡（★ V2）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ReactionBalance:
    """★★★★ **反力平衡**（★ 逐字承验收：★「★ **反力平衡**」）。

    ★★ 判据：★ 支反力之和**必须**等于外载荷之和（★ 相对容差）。
    """

    applied_n: float = 0.0
    reactions_n: list = field(default_factory=list)  #: ★ 各支反力
    rel_tol: float = 1e-3

    def verdict(self) -> dict:
        """★★★ **判定**（★ 不平衡 ⇒ **不通过** —— ★ 那是**离散错误**或**边界设错**）。"""
        total = sum(float(r) for r in self.reactions_n)
        if self.applied_n == 0:
            return {
                "ok": False,
                "reason": "★★ 外载荷为 0 ⇒ 无法判平衡（★ 不是「平衡」）",
                "applied": 0.0,
                "reaction_total": total,
            }
        err = abs(total - self.applied_n) / abs(self.applied_n)
        ok = err <= self.rel_tol
        return {
            "ok": ok,
            "applied": self.applied_n,
            "reaction_total": total,
            "relative_error": err,
            "rel_tol": self.rel_tol,
            "reason": (
                "★ 反力合计 %.6g ≈ 外载 %.6g（★ 相对误差 %.2e ≤ %.0e）"
                % (total, self.applied_n, err, self.rel_tol)
                if ok
                else "★★ 反力 %.6g ≠ 外载 %.6g（★ 相对误差 %.2e > %.0e）"
                % (total, self.applied_n, err, self.rel_tol)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ 网格收敛（★ EC09-T04 · V3）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class MeshConvergence:
    """★★★★ **网格收敛**（★ 逐字承 EC09-T04）：

    「★ **至少三档**有策略的网格与**关注量收敛**；★ **奇异峰值不能单纯细化网格追峰**」。

    ★★★ **本类的两条判据**：
      · ★ **至少三档**
      · ★★ **收敛**（★ 相邻档的相对变化**单调下降**且**趋于平缓**）
      · ★★★ **不许追峰**（★ 值**一直涨** ⇒ ★ 那可能是**奇异点**，★ **不是收敛**）
    """

    levels: list = field(default_factory=list)  #: ★ 逐档的**关注量**读数（★ 至少 3 个）
    #: ★★ **关注量名**（★ 如 `max_von_mises` / `tip_deflection`）
    quantity: str = ""
    rel_tol: float = 0.05  #: ★★ 相邻档允许的相对变化

    def verdict(self) -> dict:
        """★★★★ **判定**。"""
        if len(self.levels) < 3:
            return {
                "ok": False,
                "verdict": "insufficient_levels",
                "reason": "★★ **不足三档**（★ 逐字要求「至少三档」）⇒ 不能判收敛",
                "levels": len(self.levels),
            }
        vals = [float(v) for v in self.levels]
        deltas = [
            abs(vals[i + 1] - vals[i]) / abs(vals[i])
            for i in range(len(vals) - 1)
            if vals[i] != 0
        ]
        if not deltas:
            return {"ok": False, "verdict": "no_signal", "reason": "★ 读数全为 0"}
        #: ★★★ **追峰检测**：★ 值**单调上升**且**变化率没降** ⇒ ★ 疑似奇异
        rising = all(vals[i + 1] > vals[i] for i in range(len(vals) - 1))
        shrinking = len(deltas) >= 2 and deltas[-1] < deltas[0]
        if rising and not shrinking:
            return {
                "ok": False,
                "verdict": "peak_chasing",
                "levels": vals,
                "deltas": deltas,
                "reason": (
                    "★★★ 关注量**单调上升且变化率没降** ⇒ ★ 疑似**奇异峰值**；"
                    "★ **不能靠细化网格追峰**（★ EC09-T04 逐字）"
                ),
            }
        converged = deltas[-1] <= self.rel_tol
        return {
            "ok": converged,
            "verdict": "converged" if converged else "not_converged",
            "levels": vals,
            "deltas": deltas,
            "rel_tol": self.rel_tol,
            "reason": (
                "★ %d 档收敛（★ 末档相对变化 %.3f ≤ %.3f）"
                % (len(vals), deltas[-1], self.rel_tol)
                if converged
                else "★★ 末档相对变化 %.3f > %.3f ⇒ 未收敛" % (deltas[-1], self.rel_tol)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 版本闭合（★ V4）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class VersionClosure:
    """★★★★ **材料/载荷版本闭合**（★ 逐字承验收：★「★ **材料/载荷版本闭合**」）。

    ★★ 判据：★ **分析用的材料版本** 与 **载荷版本** 必须**与冻结的那份一致**
      （★ 不一致 ⇒ ★ 结论**不能绑到这个模型上**）。
    """

    material_ref: str = ""
    material_used: str = ""
    load_ref: str = ""
    load_used: str = ""
    geometry_ref: str = ""
    geometry_used: str = ""

    def verdict(self) -> dict:
        """★★★ **判定**（★ 三对都要闭合）。"""
        pairs = (
            ("material", self.material_ref, self.material_used),
            ("load", self.load_ref, self.load_used),
            ("geometry", self.geometry_ref, self.geometry_used),
        )
        open_pairs = [
            {"kind": k, "ref": r, "used": u} for k, r, u in pairs if not r or r != u
        ]
        return {
            "ok": not open_pairs,
            "open": open_pairs,
            "reason": (
                "★ 材料/载荷/几何三对都闭合"
                if not open_pairs
                else "★★ %d 对未闭合 ⇒ ★ 结论不能绑到这个模型" % len(open_pairs)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ AnalysisIR（★ EC09-T02）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class AnalysisIR:
    """★★★ **AnalysisIR**（★ 逐字承 EC09-T02）：

    「★ AnalysisIR 定义**几何简化、材料、本构、载荷、边界、接触、目标量和适用域**」。
    """

    geometry_simplification: str = ""
    material: str = ""
    constitutive: str = ""  #: ★ 本构（★ 线弹性/弹塑性…）
    loads: list = field(default_factory=list)
    boundaries: list = field(default_factory=list)
    contacts: list = field(default_factory=list)
    target_quantity: str = ""
    applicability: str = ""

    def completeness(self) -> dict:
        """★★★★ **完整性**（★ 八项；★ **缺项 ⇒ 不能用默认值求解后「通过」**）。

        ★★ 依据（★ EC09-T03 逐字）：★「★ ……★ **缺失条件不能以默认值求解后「通过」**」。
        """
        need = (
            "geometry_simplification",
            "material",
            "constitutive",
            "target_quantity",
            "applicability",
        )
        missing = [k for k in need if not str(getattr(self, k) or "").strip()]
        if not self.loads:
            missing.append("loads")
        if not self.boundaries:
            missing.append("boundaries")
        return {
            "ok": not missing,
            "missing": missing,
            "reason": (
                "★ AnalysisIR 完整"
                if not missing
                else "★★ 缺 %r ⇒ ★ **不得以默认值求解后「通过」**" % missing
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★★ 验证范围（★ EC09-T05 · V7）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ValidationScope:
    """★★★★★ **验证范围**（★ 逐字承 EC09-T05）：

    「★ 分开计算 **verification**、物理 **validation** 和**不确定性**；
    ★ **无实体/可信实验时只写验证范围**」。

    ★★★ **验收（★ 逐字）**：★「★ **没有 validation 证据不写「真实工况已验证」**」。
    """

    verification_done: bool = False
    validation_evidence: list = field(default_factory=list)  #: ★★ **物理验证证据**
    uncertainty_notes: str = ""

    def may_claim_real_condition_validated(self) -> dict:
        """★★★★★ **能不能写「真实工况已验证」**（★ 验收核心）。

        ★★★ **判据**：★ **必须**有 `validation_evidence`（★ 物理验证）——
          ★★ 只有计算验证（★ `verification_done`）**不够** ✗
        """
        if not self.validation_evidence:
            return {
                "ok": False,
                "claim_allowed": False,
                "reason": (
                    "★★★ **没有 validation 证据** ⇒ ★ **不写「真实工况已验证」**；"
                    "★ 只能写**验证范围**（★ 计算 verification 已做=%s）"
                    % self.verification_done
                ),
            }
        return {
            "ok": True,
            "claim_allowed": True,
            "evidence": list(self.validation_evidence),
            "reason": "★ 有物理验证证据 ⇒ 可以写（★ 并列出证据）",
        }


# ══════════════════════════════════════════════════════════════════════
# 七、★★★★★ 工程结论（★ 验收核心：★ 求解成功 ≠ 工程通过）
# ══════════════════════════════════════════════════════════════════════


def engineering_verdict(
    *,
    solve_status: str,
    reference: ReferenceSolution | None,
    balance: ReactionBalance | None,
    convergence: MeshConvergence | None,
    closure: VersionClosure | None,
    validation: ValidationScope | None,
    reanalyzed_after_optimization: bool | None = None,
) -> dict:
    """★★★★★ **工程结论**（★ EC09 的**总判据**）。

    ★★★ **验收逐字**：★「★ **求解成功不是工程通过**」+ ★「★ **优化后复分析**」+
      ★「★ **没有 validation 证据不写「真实工况已验证」**」。

    ★★★ **判据**：★ 即使求解器回 `solved`，★ **下面五道门一道不过 ⇒ 就不是工程通过**：
      · ★ **参考解**独立且可用
      · ★ **反力平衡**
      · ★ **网格收敛**（★ 且不追峰）
      · ★ **版本闭合**
      · ★★ **优化过 ⇒ 必须复分析**
    ★★ 而 **validation** 决定的是**能不能说「真实工况已验证」** —— ★ 不是「能不能通过」。
    """
    gates: dict = {}
    gates["solve"] = {
        "ok": solve_status == SolveStatus.SOLVED,
        "status": solve_status,
        "note": "★★ 求解成功**只是**入场券（★ 不是工程通过）",
    }
    gates["reference"] = (
        reference.is_usable()
        if reference is not None
        else {"ok": False, "reason": "★★ 没有参考解"}
    )
    gates["balance"] = (
        balance.verdict()
        if balance is not None
        else {"ok": False, "reason": "★★ 没做反力平衡"}
    )
    gates["convergence"] = (
        convergence.verdict()
        if convergence is not None
        else {"ok": False, "reason": "★★ 没做网格收敛"}
    )
    gates["closure"] = (
        closure.verdict()
        if closure is not None
        else {"ok": False, "reason": "★★ 没做版本闭合"}
    )
    #: ★★ **优化后复分析**（★ 只有「做过优化」时才要求）
    if reanalyzed_after_optimization is None:
        gates["reanalysis"] = {"ok": True, "note": "★ 未做优化 ⇒ 不要求复分析"}
    else:
        gates["reanalysis"] = {
            "ok": bool(reanalyzed_after_optimization),
            "reason": (
                "★ 优化后已复分析"
                if reanalyzed_after_optimization
                else "★★ **优化后没复分析** ⇒ ★ 不把云图直接交制造（★ EC09-T07）"
            ),
        }
    #: ★★★ **五道门**（★ 不含 validation —— ★ 它管的是**措辞**不是**通过**）
    hard_gates = (
        "solve",
        "reference",
        "balance",
        "convergence",
        "closure",
        "reanalysis",
    )
    passed = all(gates[g]["ok"] for g in hard_gates)
    v = (
        validation.may_claim_real_condition_validated()
        if validation
        else {
            "claim_allowed": False,
            "reason": "★★ 没有 validation 记录 ⇒ 不写「真实工况已验证」",
        }
    )
    return {
        "engineering_pass": passed,
        "solved": solve_status == SolveStatus.SOLVED,
        "gates": gates,
        "may_claim_real_condition_validated": bool(v.get("claim_allowed")),
        "validation_note": v.get("reason"),
        "reason": (
            "★ 六道门全过 ⇒ 工程通过"
            if passed
            else "★★ 求解=%s，★ 但**工程未通过**：★ %r"
            % (solve_status, [g for g in hard_gates if not gates[g]["ok"]])
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# 八、★★★★★ 设计敏感性（★ EC09-T06）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class SensitivityScan:
    """★★★★ **设计敏感性**（★ 逐字承 EC09-T06）：

    「★ **设计敏感性**和**保守边界**；★ 优化输入/**不可改域**/制造约束冻结」。

    ★★ 判据：★ ① **逐参数扰动**（★ 每个输入至少两个点）；★ ② 给出**最敏感**的参数；
      ★★ ③ **不可改域必须冻结**（★ 有清单）。
    """

    perturbations: dict = field(default_factory=dict)  #: `{param: [(value, response)]}`
    frozen_domains: list = field(default_factory=list)  #: ★★ **不可改域**
    manufacturing_constraints: list = field(default_factory=list)

    def sensitivity(self) -> dict:
        """★★★ **算敏感性**（★ 归一化斜率：★ `Δresponse/Δparam` × `param/response`）。

        ★★ 返回**按敏感性降序**的清单 ⇒ ★ 接手方知道**先改哪个**。
        """
        out = []
        for name, pts in (self.perturbations or {}).items():
            if len(pts) < 2:
                continue
            (x0, y0), (x1, y1) = pts[0], pts[-1]
            if x0 == x1:
                continue
            slope = (y1 - y0) / (x1 - x0)
            #: ★★ **归一化**（★ 无量纲 ⇒ 可跨参数比较）
            norm = abs(slope) * (abs(x0) / abs(y0)) if y0 else abs(slope)
            out.append(
                {"param": name, "slope": slope, "normalized": norm, "points": len(pts)}
            )
        out.sort(key=lambda r: -r["normalized"])
        return {
            "ok": bool(out),
            "ranked": out,
            "most_sensitive": out[0]["param"] if out else None,
            "reason": (
                "★ %d 个参数已扫描，★ 最敏感：%s" % (len(out), out[0]["param"])
                if out
                else "★★ 没有一个参数有 ≥2 个扰动点 ⇒ 算不出敏感性"
            ),
        }

    def verdict(self) -> dict:
        """★★★★ **判定**（★ 敏感性可算 + ★ **不可改域已冻结**）。"""
        s = self.sensitivity()
        if not s["ok"]:
            return {"ok": False, "reason": s["reason"], "sensitivity": s}
        if not self.frozen_domains:
            return {
                "ok": False,
                "sensitivity": s,
                "reason": "★★ **不可改域没冻结**（★ EC09-T06 逐字要求）",
            }
        return {
            "ok": True,
            "sensitivity": s,
            "frozen_domains": list(self.frozen_domains),
            "manufacturing_constraints": list(self.manufacturing_constraints),
            "reason": "★ 敏感性可算 + 不可改域已冻结（%r）" % list(self.frozen_domains),
        }


def beam_stress_under_load(moment_nm: float, c_m: float, i_m4: float) -> float:
    """★ 供敏感性扫描用的**响应函数**（★ 闭式解 —— ★ 独立于求解器）。"""
    return beam_bending_stress_reference(moment_nm, c_m, i_m4)
