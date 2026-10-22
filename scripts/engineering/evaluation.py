"""★ EC12 能力包与评测 —— 留出集 / 增益归因 / 联合考核 / 零事故≠零风险 / 单方法准入。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC12**（★ T01–T08 逐字）
#         `specs/314-ec12-capability-package-and-eval/spec.md`
#         `scripts/engineering/compiler.py`（★ EC03 的沙箱隔离 —— ★ **复用**）
# 定位:   ★ **EC12** 的实现。★★★ 计划 §5 EC12 验收逐字：「★ **留出集可重复**；★ **系统
#           增益不是增加无限重试得到**； ★ **错误放行与拒绝率联合考核**；★ **零事故样本
#           不等于零风险**； ★ **各领域发布分别过门**」
# 官方依据: 不适用（本仓的评测层 —— ★ 不调 COM · ★ 不调模型）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field

__all__ = [
    "SplitKind",
    "ArmKind",
    "MethodAdmission",
    "EvalCase",
    "EvalSet",
    "ArmResult",
    "AttributionReport",
    "AdmissionGate",
    "DomainGates",
    "wilson_upper_bound",
]


class SplitKind:
    """★★ **数据划分**（★ 逐字承 EC12-T01：★「★ 案例分**训练/开发/留出**，
    ★ 按**零件族/参数域/故障**划分，★ **避免近似复制污染**」）。"""

    TRAIN = "train"
    DEV = "dev"
    HOLDOUT = "holdout"  #: ★★ **留出集**（★ 验收要它**可重复**）

    ALL = (TRAIN, DEV, HOLDOUT)


class ArmKind:
    """★★★ **三组对照**（★ 逐字承 EC12-T02：★「★ 建立**原模型+工具、模型+提示词、
    模型+工程系统**三组对照；★ **强模型只是参考，不是解法**」）。"""

    MODEL_TOOLS = "model_plus_tools"  #: ★ 原模型 + 工具
    MODEL_PROMPT = "model_plus_prompt"  #: ★ 模型 + 提示词
    MODEL_SYSTEM = "model_plus_engineering"  #: ★★ **模型 + 工程系统**

    ALL = (MODEL_TOOLS, MODEL_PROMPT, MODEL_SYSTEM)


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ 留出集（★ EC12-T01/T05 · V1）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class EvalCase:
    """★ 一个评测案例（★ 带**族/域/故障** —— ★ 用于**避免近似复制污染**）。"""

    id: str
    family: str = ""  #: ★ 零件族
    domain: str = ""  #: ★ 参数域
    fault: str = ""  #: ★ 故障类型
    split: str = SplitKind.TRAIN
    content: str = ""

    def fingerprint(self) -> str:
        """★★ **内容指纹**（★ 用于**近似复制检测** —— ★ EC12-T01 逐字）。"""
        blob = json.dumps(
            {"f": self.family, "d": self.domain, "x": self.fault, "c": self.content},
            ensure_ascii=False,
            sort_keys=True,
        )
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass
class EvalSet:
    """★★★★ **评测集**（★ 逐字承 EC12-T01/T05）。

    ★★★ **验收（★ 逐字）**：★「★ **留出集可重复**」+ ★「★ **冻结数据、模型版本、温度、
    预算、允许工具和运行环境**；★ **重复试验与置信区间**」。
    """

    cases: list = field(default_factory=list)
    #: ★★★ **冻结的运行条件**（★ 逐字承 EC12-T05）
    frozen: dict = field(default_factory=dict)

    def add(self, case: EvalCase) -> None:
        self.cases.append(case)

    def holdout(self) -> list:
        return [c for c in self.cases if c.split == SplitKind.HOLDOUT]

    def duplicate_fingerprints(self) -> list:
        """★★★★ **近似复制检测**（★ 逐字承 EC12-T01：★「★ **避免近似复制污染**」）。

        ★★ 判据：★ 同指纹出现在**多个划分**里 ⇒ ★ **污染**（★ 留出集不独立了）✗
        """
        by_fp: dict = {}
        for c in self.cases:
            by_fp.setdefault(c.fingerprint(), []).append(c)
        bad = []
        for fp, items in by_fp.items():
            splits = {c.split for c in items}
            if len(splits) > 1:
                bad.append(
                    {
                        "fingerprint": fp,
                        "ids": [c.id for c in items],
                        "splits": sorted(splits),
                    }
                )
        return bad

    def frozen_conditions_complete(self) -> dict:
        """★★★ **冻结条件齐**（★ 逐字承 EC12-T05 的六项）。"""
        need = (
            "data",
            "model_version",
            "temperature",
            "budget",
            "allowed_tools",
            "runtime",
        )
        missing = [k for k in need if k not in (self.frozen or {})]
        return {
            "ok": not missing,
            "missing": missing,
            "reason": (
                "★ 六项冻结条件齐" if not missing else "★★ 缺 %r ⇒ ★ 不可重复" % missing
            ),
        }

    def fingerprint(self) -> str:
        """★★★ **留出集指纹**（★ 验收：「★ **留出集可重复**」）。

        ★★ 判据：★ 同一批案例 + 同一冻结条件 ⇒ **同一指纹** ⇒ ★ 可复现。
        """
        ids = sorted(c.id for c in self.cases)
        blob = json.dumps(
            {"ids": ids, "frozen": self.frozen or {}},
            ensure_ascii=False,
            sort_keys=True,
        )
        return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def verdict(self) -> dict:
        """★★★ **评测集判定**（★ 三条：★ 有留出集 · ★ 无污染 · ★ 条件冻结齐）。"""
        h = self.holdout()
        dup = self.duplicate_fingerprints()
        fc = self.frozen_conditions_complete()
        ok = bool(h) and not dup and fc["ok"]
        return {
            "ok": ok,
            "holdout_count": len(h),
            "contamination": dup,
            "frozen": fc,
            "fingerprint": self.fingerprint(),
            "reason": (
                "★ 留出集 %d 条 · ★ 无污染 · ★ 条件已冻结 ⇒ 可重复" % len(h)
                if ok
                else "★★ 留出集 %d / ★ 污染 %d / ★ 冻结 %s"
                % (len(h), len(dup), fc["ok"])
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 增益归因（★ V2）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ArmResult:
    """★ 一组对照的读数（★ 逐字承 EC12-T04：★「★ 记录**成本/耗时/人工介入/重试/拒绝/成功**，
    ★ **不能只挑成功案例**」）。"""

    arm: str
    passed: int = 0
    failed: int = 0
    rejected: int = 0  #: ★ **拒绝数**（★ 与错误放行**联合考核**）
    retries: int = 0  #: ★★ **重试数**（★ 增益归因靠它）
    cost: float = 0.0
    elapsed_s: float = 0.0
    human_interventions: int = 0
    #: ★★★ **错误放行**（★ 验收要它与拒绝率**联合考核**）
    false_releases: int = 0

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.rejected

    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0

    def reject_rate(self) -> float:
        return self.rejected / self.total if self.total else 0.0

    def false_release_rate(self) -> float:
        """★★★ **错误放行率**（★ 验收：「★ **错误放行与拒绝率联合考核**」）。"""
        return self.false_releases / self.total if self.total else 0.0

    def retries_per_case(self) -> float:
        """★★★ **每案重试数**（★ 增益归因的关键量）。"""
        return self.retries / self.total if self.total else 0.0


@dataclass
class AttributionReport:
    """★★★★★ **增益归因**（★ 逐字承验收：★「★ **系统增益不是增加无限重试得到**」）。

    ★★★ **判据**：★ 比较 `model_system` 与 `model_prompt`（★ 两组对照）——
      ★★ **若增益伴随重试数**显著上升** ⇒ ★ 增益**不归因于系统**，★ 归因于**重试** ✗
    """

    arms: dict = field(default_factory=dict)  #: `{arm: ArmResult}`
    #: ★★ 重试数允许的相对上升（★ 超过就算「靠重试」）
    retry_tolerance: float = 0.5

    def system_gain(self) -> dict:
        """★★★★ **系统增益**（★ 三组对照 + ★ **重试归因**）。"""
        a = self.arms.get(ArmKind.MODEL_PROMPT)
        b = self.arms.get(ArmKind.MODEL_SYSTEM)
        if a is None or b is None:
            return {
                "ok": False,
                "gain": 0.0,
                "reason": "★★ 缺对照臂（★ 需要 `model_plus_prompt` 与 "
                "`model_plus_engineering`）",
            }
        gain = b.pass_rate() - a.pass_rate()
        ra, rb = a.retries_per_case(), b.retries_per_case()
        retry_up = ((rb - ra) / ra) if ra > 0 else (float("inf") if rb > 0 else 0.0)
        retry_driven = retry_up > self.retry_tolerance
        return {
            "ok": True,
            "gain": gain,
            "baseline_pass_rate": a.pass_rate(),
            "system_pass_rate": b.pass_rate(),
            "retries_per_case_baseline": ra,
            "retries_per_case_system": rb,
            "retry_increase": retry_up,
            "attributed_to_retries": retry_driven,
            "attributed_to_system": bool(gain > 0 and not retry_driven),
            "reason": (
                "★★★ 增益 %.3f 伴随重试上升 %.0f%% ⇒ ★ **归因于重试，不是系统**"
                % (gain, retry_up * 100)
                if retry_driven and gain > 0
                else (
                    "★ 增益 %.3f（★ 重试未显著上升）⇒ ★ 归因于**系统**" % gain
                    if gain > 0
                    else "★ 没有增益（%.3f）" % gain
                )
            ),
        }

    def joint_verdict(self) -> dict:
        """★★★★ **错误放行与拒绝率联合考核**（★ 逐字承验收）。

        ★★ 判据：★ **只看通过率会骗人** —— ★★ 一个「全部拒绝」的系统通过率 0、
          ★ 拒绝率 100%、★ 错误放行 0，★ **但它什么都没做** ✗
        ★★★ **⇒ 必须**联合**看**（★ 通过率 · ★ 拒绝率 · ★ 错误放行率）。
        """
        rows = {}
        for name, r in (self.arms or {}).items():
            rows[name] = {
                "pass_rate": r.pass_rate(),
                "reject_rate": r.reject_rate(),
                "false_release_rate": r.false_release_rate(),
                "retries_per_case": r.retries_per_case(),
                "total": r.total,
            }
        #: ★★ **「全拒」检测**：★ 拒绝率 100% 且通过 0 ⇒ ★ 那是**逃避**不是**能力**
        all_rejecting = bool(rows) and all(
            v["reject_rate"] >= 1.0 and v["pass_rate"] == 0.0 for v in rows.values()
        )
        #: ★★ **「全放」检测**：★ 错误放行率 > 0 且拒绝率 0 ⇒ ★ 危险
        all_releasing = bool(rows) and all(
            v["reject_rate"] == 0.0 and v["false_release_rate"] > 0
            for v in rows.values()
        )
        return {
            "ok": not all_rejecting and not all_releasing,
            "arms": rows,
            "all_rejecting": all_rejecting,
            "all_releasing": all_releasing,
            "reason": (
                "★★ 所有臂都「全拒」⇒ ★ **拒绝全部任务不是安全完成**（★ 计划 §3.2 逐字）"
                if all_rejecting
                else (
                    "★★ 所有臂都「全放且有错误放行」⇒ ★ 危险"
                    if all_releasing
                    else "★ 三率联合考核（★ 通过/拒绝/错误放行）"
                )
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ 零事故 ≠ 零风险（★ V4）
# ══════════════════════════════════════════════════════════════════════


def wilson_upper_bound(failures: int, trials: int, *, z: float = 1.96) -> float:
    """★★★★ **Wilson 上界**（★ 逐字承验收：★「★ **零事故样本不等于零风险**」）。

    ★★★ **判据**：★ `failures == 0` 时，★ 风险上界**不是 0** ——
      ★★ 它是 `z²/(n + z²)`（★ 即「没见过失败」**不等于**「失败率为 0」）✓
    ★ 公式（★ Wilson 区间上界）：★ `(p̂ + z²/2n + z·√(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n)`。
    """
    if trials <= 0:
        return 1.0  #: ★★ **没试验 ⇒ 上界 1**（★ 不是 0）
    p = failures / trials
    n = trials
    denom = 1.0 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (centre + margin) / denom)


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 单方法准入（★ EC12-T06 · V6）
# ══════════════════════════════════════════════════════════════════════


class MethodAdmission:
    """★★★★ **单方法准入七项**（★ 逐字承 EC12-T06）：

    「★ **来源许可 / 适用域 / 正负例 / 参考 oracle / 修改域 / 保存重开 / 失败说明** 齐全」。
    """

    #: ★★ **七项**（★ 逐字）
    REQUIRED = (
        "source_license",
        "applicability",
        "positive_negative_cases",
        "reference_oracle",
        "modification_domain",
        "save_reopen",
        "failure_notes",
    )

    @staticmethod
    def check(method: dict) -> dict:
        """★★★ **检查七项**（★ 缺一项 ⇒ **不准入**）。"""
        missing = [k for k in MethodAdmission.REQUIRED if not method.get(k)]
        return {
            "ok": not missing,
            "missing": missing,
            "checked": len(MethodAdmission.REQUIRED),
            "reason": (
                "★ 七项齐全 ⇒ 可准入"
                if not missing
                else "★★ 缺 %r ⇒ **不准入生产方法库**" % missing
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ 各领域分别过门（★ V5）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class DomainGates:
    """★★★★ **各领域分别过门**（★ 逐字承验收：★「★ **各领域发布分别过门**」）。

    ★★ 判据：★ **一个总的 `approve` 不算** —— ★ 每个领域**各自**过门 ✗
    """

    domains: dict = field(
        default_factory=dict
    )  #: `{domain: {"gate": str, "passed": bool}}`

    def set_gate(self, domain: str, *, gate: str, passed: bool) -> None:
        self.domains[domain] = {"gate": gate, "passed": bool(passed)}

    def verdict(self) -> dict:
        """★★★ **判定**（★ **逐个领域**报 —— ★ 不给一个合成结论）。"""
        if not self.domains:
            return {"ok": False, "reason": "★★ 一个领域都没过门", "per_domain": {}}
        per = {d: v for d, v in sorted(self.domains.items())}
        passed = [d for d, v in per.items() if v["passed"]]
        failed = [d for d, v in per.items() if not v["passed"]]
        return {
            "ok": not failed,
            "per_domain": per,
            "passed": passed,
            "failed": failed,
            "reason": (
                "★ %d 个领域**分别**过门" % len(passed)
                if not failed
                else "★★ %d 个领域未过门：%r（★ **不合并成一个 approve**）"
                % (len(failed), failed)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★★ 沙箱 → 生产的门槛（★ EC12-T08 · V7）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class AdmissionGate:
    """★★★★ **准入闸**（★ 逐字承 EC12-T08：★「★ **未见任务进入沙箱**；
    ★ **实验通过后仍需独立审核才变成生产方法**」）。

    ★★★ **判据**：★ 沙箱实验通过**还不够** —— ★ **必须**有**独立审核** ✓
    """

    sandbox_passed: bool = False
    independent_reviewer: str = ""  #: ★★ **独立审核人**
    proposer: str = ""  #: ★ 提出者
    source: str = ""  #: ★ 来源

    def may_promote(self) -> dict:
        """★★★★★ **能不能进生产**（★ 逐字承 EC12-T08）。"""
        if not self.sandbox_passed:
            return {
                "ok": False,
                "may_promote": False,
                "reason": "★★ 沙箱实验未通过 ⇒ 不进生产",
            }
        if not str(self.independent_reviewer).strip():
            return {
                "ok": False,
                "may_promote": False,
                "reason": "★★★ 沙箱通过但**没有独立审核** ⇒ ★ "
                "**实验通过后仍需独立审核**（★ EC12-T08 逐字）",
            }
        if self.independent_reviewer == self.proposer:
            return {
                "ok": False,
                "may_promote": False,
                "reason": "★★★ 审核人**就是提出者** ⇒ ★ 那是**自审**（★ 与 EC04-T06 同族）",
            }
        return {
            "ok": True,
            "may_promote": True,
            "reviewer": self.independent_reviewer,
            "reason": "★ 沙箱通过 + **独立审核**（★ %s）⇒ 可进生产"
            % self.independent_reviewer,
        }
