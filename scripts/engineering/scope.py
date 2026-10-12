"""★ Q9 + Q11 · v1 难度上界 + DoD 状态 + 止损关口 + Plan B（规格 326 的 S6~S14）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/scope.py
# 定位:   规格 `specs/326-question-persistence-and-boundaries` 的 S6（v1 上界四条）/
#           S7（不承诺清单）/ S8（`DELIVERED` 需人工批准）/ S9（人工接管单独计数）/
#           S10（两个止损关口）/ S11（三次失败停补丁）/ S12（Plan B）/
#           S13（盲题转回开发集）/ S14（叶子方法可增长）。
#           ★★ 实测（2026-10-12）起点：**没有 v1 上界的判据、没有不承诺清单、
#           没有 `DELIVERED`、没有人工接管计数、没有止损关口、没有三次停补丁、
#           没有 Plan B、没有盲题转回、没有叶子方法增长**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q9（L176-199）逐字：
#           L180-182 的四条上界；L185 的不承诺清单；L195「**人工接管的任务要单独
#             计数，不能计作自主完成**」；L197「`READY_FOR_REVIEW` 表示自动流程
#             完成待审核；**`DELIVERED` 还需可信人工批准**」
#           Q11（L201-212）逐字：L203「**两个投入止损关口**」；L205/L206 两个关口；
#             L208「同一假设**连续三次修复失败**停止补丁式尝试」；
#             L210「**Plan B：人工确认 DesignIR／选择方法**」；
#             L206「已看过的失败盲题**转回开发集**」；
#             L212「**允许有契约、可组合、可验证的叶子方法持续增长**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCOPE_FILE = ROOT / "metadata" / "scope-v1.json"


class ScopeError(Exception):
    """★ 范围/关口失败（★ 带封闭码）。"""

    CODES = ("over-scope", "not-promised", "missing-approval", "no-scope-file",
             "patch-limit", "stale-blind")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法范围拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、v1 难度上界（★ S6 —— ★ Q9 L180-182）
#: ══════════════════════════════════════════════════════════════════════

def load_scope() -> dict:
    if not SCOPE_FILE.is_file():
        raise ScopeError("no-scope-file", "★ 没有 %s" % SCOPE_FILE)
    return json.loads(SCOPE_FILE.read_text(encoding="utf-8"))


def check_scope(*, self_made_parts: int = 0, assembly_instances: int = 0,
                assembly_levels: int = 0, driven_dof: int = 0,
                method_level_nodes: int = 0,
                scope: dict | None = None) -> dict:
    """★★ **v1 上界判定**（★ S6 —— ★ Q9 L180-182 逐字）。

    ★★ 判据：**任何一条超界 ⇒ 拒**（★ 五条都要查）：
      ```
      零件 ≤10 · 实例 ≤30 · 层级 ≤2 · 驱动自由度 ≤1 · 方法级节点 ≤100
      ```
    ★★ Q9 L182 逐字：「**不按底层 API 次数衡量产品复杂度**」
      ⇒ ★ 本函数**只看方法级节点**，★ 不收"API 调用次数"。
    """
    sc = (scope or load_scope())["limits"]
    got = {"max_self_made_parts": self_made_parts,
           "max_assembly_instances": assembly_instances,
           "max_assembly_levels": assembly_levels,
           "max_driven_dof": driven_dof,
           "max_method_level_nodes": method_level_nodes}
    over = {k: {"got": got[k], "limit": sc[k]}
            for k in sc if k in got and got[k] > sc[k]}
    return {"ok": not over, "limits": sc, "got": got, "over": over,
            "code": "" if not over else "over-scope",
            "★": "★ 五条上界全查（★ 不按底层 API 次数衡量）"}


def check_not_promised(feature: str, scope: dict | None = None) -> dict:
    """★★ **不进入自主承诺的清单**（★ S7 —— ★ Q9 L185 逐字）。

    ★★ 判据：命中清单 ⇒ **拒**（★ 那五类 + 完整减速器整机）。
    """
    sc = scope or load_scope()
    bad = sc.get("not_promised") or {}
    hit = [k for k, v in bad.items()
           if k == feature or feature in str(v) or k in feature]
    return {"ok": not hit, "hit": hit,
            "detail": {k: bad[k] for k in hit},
            "code": "" if not hit else "not-promised",
            "★": "★ Q9 L185 逐字：这五类**不进入自主承诺**"}


#: ══ S8 `DELIVERED` 需人工批准（★ Q9 L197 逐字）═══════════════════════

READY_FOR_REVIEW = "READY_FOR_REVIEW"
DELIVERED = "DELIVERED"
DELIVERY_STATES = (READY_FOR_REVIEW, DELIVERED)

#: ★★ **可信的批准通道**（★ 与 `questions.TRUSTED_CHANNELS` 同族）
TRUSTED_APPROVERS = ("owner_typed", "local_confirm_ui", "signed_approval")


def delivery_state(*, auto_done: bool, approved_by: str = "") -> dict:
    """★★ **`READY_FOR_REVIEW` vs `DELIVERED`**（★ S8 —— ★ Q9 L197 逐字）。

    ★★ Q9 L197 逐字：「`READY_FOR_REVIEW` 表示**自动流程完成待审核**；
      **`DELIVERED` 还需可信人工批准**」。

    ★★ 判据（★ 结构性）：
      ```
      ① 自动流程没完           ⇒ 连 READY_FOR_REVIEW 都不是
      ② 自动流程完了但没批准   ⇒ READY_FOR_REVIEW（★ **不是 DELIVERED**）
      ③ 有**可信**批准         ⇒ DELIVERED
      ```
    ★★ **LLM 自报批准不算**（★ 与 Q8 同口径 —— ★ 要**通道**，不是字符串）。
    """
    if not auto_done:
        return {"state": "", "delivered": False,
                "reason": "★ 自动流程还没完成"}
    if approved_by not in TRUSTED_APPROVERS:
        return {"state": READY_FOR_REVIEW, "delivered": False,
                "reason": ("★★ `DELIVERED` 还需**可信人工批准**；"
                           "拿到的是 %r ⇒ 停在 `READY_FOR_REVIEW`"
                           % approved_by),
                "code": "missing-approval"}
    return {"state": DELIVERED, "delivered": True,
            "reason": "★ 可信人工批准 ⇒ `DELIVERED`", "code": ""}


#: ══ S9 人工接管单独计数（★ Q9 L195 逐字）════════════════════════════

@dataclass
class TakeoverLedger:
    """★★ **人工接管账**（★ S9 —— ★ Q9 L195 逐字）。

    ★★ Q9 L195 逐字：「正常流程中人工只确认需求、审查方案和批准交付，
      **不手工补建零件、不改脚本救火**。**人工接管的任务要单独计数，
      不能计作自主完成**」。
    """

    autonomous: int = 0
    taken_over: list = field(default_factory=list)

    def record(self, task_id: str, *, hand_built: bool = False,
               script_patched: bool = False) -> None:
        """★ 记一次**人工接管**（★ 两种形态：手工补建 / 改脚本救火）。"""
        self.taken_over.append({"task_id": task_id,
                                "hand_built": hand_built,
                                "script_patched": script_patched})

    def to_dict(self) -> dict:
        return {"autonomous": self.autonomous,
                "taken_over": len(self.taken_over),
                "taken_over_ids": [t["task_id"] for t in self.taken_over],
                "hand_built": sum(1 for t in self.taken_over if t["hand_built"]),
                "script_patched": sum(1 for t in self.taken_over
                                      if t["script_patched"]),
                #: ★★ **结构性保证**：自主数**不含**接管数
                "★": ("★ 人工接管**单独计数**（★ Q9 L195：「不能计作自主完成」）"
                      " ⇒ 自主 %d ≠ 总数 %d"
                      % (self.autonomous,
                         self.autonomous + len(self.taken_over)))}

    @property
    def total(self) -> int:
        return self.autonomous + len(self.taken_over)

    @property
    def autonomous_only(self) -> int:
        """★★ **真自主数**（★ 不含接管）。"""
        return self.autonomous


#: ══════════════════════════════════════════════════════════════════════
# 二、止损关口（★ S10 —— ★ Q11 L203-206）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **两个投入止损关口**（★ Q11 L203 逐字：「**两个投入止损关口**」）
GATE_STAGE2 = "stage2_execution"
GATE_STAGE4 = "stage4_planning"
STOP_GATES = (GATE_STAGE2, GATE_STAGE4)

#: ★ 阶段 2 关口：★ Q11 L205 逐字「**在阶段预算上限内，无法使板＋真实孔组＋
#:   规则校核＋完整工程图稳定通过三次独立启动验证**」
STAGE2_REQUIRED_PASSES = 3

#: ★ 阶段 4 关口：★ Q11 L206 逐字「**在两轮有明确归因的改进后，仍达不到冻结
#:   盲测门槛**，或仍把关键需求不满足的计划放进真实执行」
STAGE4_REQUIRED_ROUNDS = 2


def stage2_gate(*, passes: int, budget_exceeded: bool = False) -> dict:
    """★ **阶段 2 执行关口**（★ S10 —— ★ Q11 L205 逐字）。"""
    stop = (passes < STAGE2_REQUIRED_PASSES) or budget_exceeded
    return {"gate": GATE_STAGE2, "stop": stop,
            "passes": passes, "required": STAGE2_REQUIRED_PASSES,
            "budget_exceeded": budget_exceeded,
            "action": "STOP_EXPANDING_AUTONOMY" if stop else "continue",
            "★": "★ Q11 L205：「无法……稳定通过**三次**独立启动验证 ⇒ 停止扩大自主规划投入」"}


def stage4_gate(*, attributed_rounds: int, meets_threshold: bool,
                misreleased: int = 0) -> dict:
    """★ **阶段 4 规划关口**（★ S10 —— ★ Q11 L206 逐字）。"""
    stop = ((attributed_rounds >= STAGE4_REQUIRED_ROUNDS
             and not meets_threshold) or misreleased > 0)
    return {"gate": GATE_STAGE4, "stop": stop,
            "attributed_rounds": attributed_rounds,
            "required": STAGE4_REQUIRED_ROUNDS,
            "meets_threshold": meets_threshold, "misreleased": misreleased,
            "action": "PAUSE_AUTONOMOUS_RELEASE" if stop else "continue",
            "★": "★ Q11 L206：「两轮有明确归因的改进后仍达不到冻结门槛 ⇒ 暂停自主放行」"}


def check_stop_gates(*, stage2: dict | None = None,
                     stage4: dict | None = None) -> dict:
    """★ 两个关口**一起判**（★ S10）。"""
    rows = []
    if stage2 is not None:
        rows.append(stage2_gate(**stage2))
    if stage4 is not None:
        rows.append(stage4_gate(**stage4))
    return {"gates": rows, "any_stop": any(r["stop"] for r in rows),
            "n": len(rows)}


#: ══ S11 三次失败停补丁（★ Q11 L208 逐字）════════════════════════════

PATCH_LIMIT = 3


@dataclass
class HypothesisTracker:
    """★★ **同一假设连续三次修复失败 ⇒ 停止补丁式尝试**（★ S11）。

    ★★ Q11 L208 逐字：「同一假设**连续三次修复失败**停止补丁式尝试，
      **重新检查契约或架构**」。
    ★★ 与 `decisions.SameErrorTrigger` 的分工：
      ★ 那个管「**同错误码两次** ⇒ 诊断」；★ 这个管「**同假设三次** ⇒ 停补丁」。
    """

    limit: int = PATCH_LIMIT
    attempts: dict = field(default_factory=dict)

    def record(self, hypothesis: str, *, succeeded: bool) -> dict:
        n = 0 if succeeded else int(self.attempts.get(hypothesis, 0)) + 1
        self.attempts[hypothesis] = n
        if succeeded:
            #: ★ 成功 ⇒ 计数器归零（★ 判据是"**连续**三次"）
            return {"hypothesis": hypothesis, "consecutive_failures": 0,
                    "stop_patching": False, "action": "continue"}
        stop = n >= self.limit
        return {"hypothesis": hypothesis, "consecutive_failures": n,
                "stop_patching": stop,
                "action": ("RECHECK_CONTRACT_OR_ARCHITECTURE" if stop
                           else "continue"),
                "★": ("★ Q11 L208：「同一假设连续三次修复失败 ⇒ 停止补丁式尝试，"
                      "**重新检查契约或架构**」" if stop else "")}

    def to_dict(self) -> dict:
        return {"limit": self.limit, "attempts": dict(self.attempts),
                "over_limit": [h for h, n in self.attempts.items()
                               if n >= self.limit]}


#: ══ S12 Plan B（★ Q11 L210 逐字）════════════════════════════════════

@dataclass
class PlanB:
    """★★ **Plan B：人工确认 `DesignIR`／选择方法，系统负责确定性部分**
    （★ S12 —— ★ Q11 L210 逐字）。

    ★★ 判据：**人工做的两件事**与**系统做的五件事**要**分开**
      （★ 否则 Plan B 就退化成"又一套自主流程"）。
    """

    #: ★ 人工负责
    human_confirms: tuple = ("DesignIR", "method_selection")
    #: ★ 系统负责（★ 全是**确定性**的）
    system_does: tuple = ("compile", "execute", "change", "draw", "verify")

    def route(self, *, human_did: list) -> dict:
        """★ 判 Plan B **能不能启动**（★ 人工那两件必须做完）。"""
        missing = [h for h in self.human_confirms if h not in human_did]
        return {"ready": not missing, "missing_human": missing,
                "system_will_do": list(self.system_does),
                "★": "★ Q11 L210：「人工确认 DesignIR／选择方法，系统负责确定性编译、执行、变更、出图和验证」"}

    def to_dict(self) -> dict:
        return {"human_confirms": list(self.human_confirms),
                "system_does": list(self.system_does),
                "★": "★ 已验证的参数化产品族可成为**受限服务**，不必丢弃前序成果"}


#: ══ S13 盲题转回开发集（★ Q11 L206 逐字）════════════════════════════

@dataclass
class BlindSet:
    """★★ **失败盲题转回开发集**（★ S13 —— ★ Q11 L206 逐字）。

    ★★ Q11 L206 逐字：「**已看过的失败盲题转回开发集**，
      下一轮重新补足未见盲题，**不能继续把原题称为盲测**」。
    """

    dev: list = field(default_factory=list)
    blind: list = field(default_factory=list)

    def see_failure(self, case_id: str) -> dict:
        """★★ 一旦**看过**它失败 ⇒ 它**不再算盲题**。"""
        if case_id not in self.blind:
            return {"moved": False, "reason": "★ %s 不在盲测集里" % case_id}
        self.blind.remove(case_id)
        self.dev.append(case_id)
        return {"moved": True, "case_id": case_id,
                "now_in": "dev",
                "★": ("★ Q11 L206：「已看过的失败盲题**转回开发集**，"
                      "不能继续把原题称为盲测」")}

    def to_dict(self) -> dict:
        return {"dev": list(self.dev), "blind": list(self.blind),
                "dev_n": len(self.dev), "blind_n": len(self.blind),
                "★": "★ 看过的题**不在盲测集里**（★ 结构性保证）"}


#: ══ S14 叶子方法可增长（★ Q11 L212 逐字）════════════════════════════

def method_growth_policy() -> dict:
    """★★ **允许叶子方法持续增长**（★ S14 —— ★ Q11 L212 逐字）。

    ★★ Q11 L212 逐字：「原文排除「无限堆产品配方」合理，
      但**排除一切方法增长不合理**。……**允许有契约、可组合、可验证的
      叶子方法持续增长**」。

    ★★ 判据（★ 三条，★ 缺一不可 —— ★ 这是「**增长有门槛**」不是「不许增长」）：
      ```
      ① 有契约（contract）
      ② 可组合（composable）
      ③ 可验证（verifiable）
      ```
    """
    return {
        "allowed": True,
        "requirements": ("contract", "composable", "verifiable"),
        "forbidden": ("infinite_product_recipes",),
        "★": ("★ Q11 L212：「允许**有契约、可组合、可验证**的叶子方法持续增长」"
              "（★ 排除「无限堆产品配方」★ 但**不排除一切方法增长**）"),
    }


def admit_leaf_method(*, has_contract: bool, composable: bool,
                      verifiable: bool) -> dict:
    """★ 准入一个叶子方法（★ S14 的三条门槛）。"""
    miss = [k for k, v in (("contract", has_contract),
                           ("composable", composable),
                           ("verifiable", verifiable)) if not v]
    return {"admitted": not miss, "missing": miss,
            "★": "★ 三条门槛缺一不可（★ 但**不因为「方法多了」就拒绝**）"}
