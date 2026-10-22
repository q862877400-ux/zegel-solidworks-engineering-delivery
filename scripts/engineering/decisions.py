"""★ Q1 · 决策追责 + 三态晋升 + 同错两次诊断（规格 325 的 R6/R7/R9）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/decisions.py
# 定位:   规格 `specs/325-declarative-protocols-and-decisions` 的 R6（`decision_id`五
#           要素）/ R7（三态且 LLM 不能自升）/ R9（同错两次停下转诊断触发）。★★ 实测（20
#           26-10-12）起点：**没有 `decision_id`、没有三态、没有可见理由、没有受影响节点
#           、没有同错两次的触发**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q1（L22-32）逐字：「LLM 输出
#           都是 `Proposal`，**不能自行晋升为 `Validated` 或 `Approved`**。  代码只能裁
#           决**已经形式化的性质**，不能声称证明任意自然语言的完整语义。」「最小追责单位
#           沿用任务／方法／节点／验证义务／执行尝试，另给每个方案决策  一个 `decision_i
#           d`，记录**输入版本、备选方案、可见理由、依据和  受影响节点**。**无需记录模型
#           隐藏思维链**。」「「**同错误两次停下**」转成**诊断触发**，  **不转成「一定是
#           方法选错」的根因判定**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、三态（★ R7 —— ★ Q1 L22）
#: ══════════════════════════════════════════════════════════════════════

PROPOSAL = "Proposal"
VALIDATED = "Validated"
APPROVED = "Approved"
STATES = (PROPOSAL, VALIDATED, APPROVED)

#: ★★ **谁能产生哪一态**（★ Q1 L22 逐字：「LLM 输出都是 `Proposal`，
#:   **不能自行晋升**」）
#:   ★ 判据：`proposer` 决定**起始态** —— ★ `llm` 只能给 `Proposal`。
PROPOSER_LLM = "llm"
PROPOSER_CODE = "code"
PROPOSER_HUMAN = "human"
PROPOSERS = (PROPOSER_LLM, PROPOSER_CODE, PROPOSER_HUMAN)

#: ★★ **允许的晋升**（★ 封闭表）：
#:   `Proposal → Validated` 只能由**代码裁决**；
#:   `Validated → Approved` 只能由**人**。
TRANSITIONS = {
    PROPOSAL: (VALIDATED,),
    VALIDATED: (APPROVED,),
    APPROVED: (),
}
#: ★★ **每一步谁有权**（★ 这是「不能自行晋升」的**结构性保证**）
STEP_AUTHORITY = {
    (PROPOSAL, VALIDATED): (PROPOSER_CODE,),
    (VALIDATED, APPROVED): (PROPOSER_HUMAN,),
}


class DecisionError(Exception):
    """★ 决策层失败（★ 带封闭码）。"""

    CODES = ("bad-state", "bad-proposer", "illegal-transition",
             "not-authorized", "missing-field", "already-decided",
             "hidden-cot")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法决策拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 二、decision_id 与五要素（★ R6 —— ★ Q1 L24）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ Q1 L24 逐字要的**五要素**
REQUIRED_DECISION_FIELDS = ("input_version", "alternatives",
                            "visible_rationale", "basis", "affected_nodes")


@dataclass
class Decision:
    """★ **一个方案决策**（★ R6）。

    ★★ 五要素（★ Q1 L24 逐字）：**输入版本、备选方案、可见理由、依据、
      受影响节点**。
    ★★ **不含隐藏思维链**（★ Q1 L24 逐字：「无需记录模型隐藏思维链」）。
    """

    decision_id: str = ""
    state: str = PROPOSAL
    proposer: str = PROPOSER_LLM
    input_version: str = ""
    alternatives: list = field(default_factory=list)
    visible_rationale: str = ""
    basis: list = field(default_factory=list)
    affected_nodes: list = field(default_factory=list)
    #: ★ 显式留一个**陷阱字段**：★ 若有人往里塞思维链，`validate()` 会拒
    hidden_cot: str = ""

    def __post_init__(self) -> None:
        if self.state not in STATES:
            raise DecisionError("bad-state", "★ 未知态：%r" % self.state)
        if self.proposer not in PROPOSERS:
            raise DecisionError("bad-proposer", "★ 未知提出者：%r" % self.proposer)

    def missing(self) -> list:
        """★ 五要素缺哪几项。"""
        out = []
        for f in REQUIRED_DECISION_FIELDS:
            v = getattr(self, f, None)
            if v is None or v == "" or v == []:
                out.append(f)
        return out

    def validate(self) -> None:
        miss = self.missing()
        if miss:
            raise DecisionError("missing-field", "★ 缺五要素：%s" % miss)
        if self.hidden_cot:
            #: ★★ Q1 L24 逐字：「**无需记录模型隐藏思维链**」
            #:   ★ 判据：**收进来就拒**（★ 不是"建议别写"）
            raise DecisionError(
                "hidden-cot",
                "★★ 不许记录隐藏思维链（★ Q1 L24 逐字：「无需记录模型隐藏思维链」）")

    def to_dict(self) -> dict:
        return {"decision_id": self.decision_id, "state": self.state,
                "proposer": self.proposer,
                "input_version": self.input_version,
                "alternatives": list(self.alternatives),
                "visible_rationale": self.visible_rationale,
                "basis": list(self.basis),
                "affected_nodes": list(self.affected_nodes),
                "★": "★ 只记**可见理由**，★ 不记隐藏思维链"}


def make_decision(*, proposer: str, input_version: str, alternatives: list,
                  visible_rationale: str, basis: list,
                  affected_nodes: list) -> Decision:
    """★ 造一个**起始态为 `Proposal`** 的决策（★ R6）。

    ★★ 判据：**起始态永远是 `Proposal`** —— ★ 无论谁提的
      （★ Q1 L22 逐字：「LLM 输出**都是** `Proposal`」）。
    """
    d = Decision(
        proposer=proposer, input_version=input_version,
        alternatives=list(alternatives), visible_rationale=visible_rationale,
        basis=list(basis), affected_nodes=list(affected_nodes))
    d.validate()
    #: ★★ `decision_id` = **五要素的摘要**（★ 可复核、不可伪造）
    blob = json.dumps({k: getattr(d, k) for k in REQUIRED_DECISION_FIELDS},
                      ensure_ascii=False, sort_keys=True)
    d.decision_id = "dec-" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
    return d


#: ══════════════════════════════════════════════════════════════════════
# 三、晋升（★ R7 —— ★ 三态闸门）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class Promotion:
    ok: bool = False
    from_state: str = ""
    to_state: str = ""
    by: str = ""
    code: str = ""
    detail: str = ""

    def to_dict(self) -> dict:
        return {"ok": self.ok, "from": self.from_state, "to": self.to_state,
                "by": self.by, "code": self.code, "detail": self.detail}


def promote(d: Decision, to_state: str, *, by: str,
            code_verdict: dict | None = None) -> Promotion:
    """★★ **晋升闸门**（★ R7 —— ★ Q1 L22 逐字）。

    ★★ 判据（★ 四条，★ 最严的在前）：
      ```
      ① 目标态必须合法
      ② 迁移必须在 `TRANSITIONS` 里（★ 封闭表）
      ③ ★★ 谁有权：`Proposal→Validated` 只能 `code`；
         `Validated→Approved` 只能 `human`
         ⇒ ★★ **LLM 一步都升不了**（★ 这是「不能自行晋升」的结构性保证）
      ④ `Proposal→Validated` **必须带代码裁决结果**，且**裁决必须是 PASS**
         （★ Q1 L22 逐字：「代码只能裁决**已经形式化的性质**」）
      ```
    """
    if to_state not in STATES:
        return Promotion(False, d.state, to_state, by, "bad-state",
                         "★ 未知目标态：%r" % to_state)
    if to_state not in TRANSITIONS.get(d.state, ()):
        return Promotion(False, d.state, to_state, by, "illegal-transition",
                         "★★ %s → %s 不在允许的迁移里（★ 不能跳级）"
                         % (d.state, to_state))
    allowed = STEP_AUTHORITY.get((d.state, to_state), ())
    if by not in allowed:
        return Promotion(
            False, d.state, to_state, by, "not-authorized",
            "★★ %s → %s 只能由 %s 做，而你是 %r"
            "（★ Q1 L22：「LLM 输出都是 Proposal，不能自行晋升」）"
            % (d.state, to_state, list(allowed), by))
    if to_state == VALIDATED:
        #: ★★ ④ **必须带代码裁决**，且**必须是 PASS**
        if not code_verdict:
            return Promotion(False, d.state, to_state, by, "not-authorized",
                             "★★ 进 `Validated` 必须带**代码裁决结果**")
        v = str(code_verdict.get("verdict") or code_verdict.get("status") or "")
        if v.upper() not in ("PASS", "OK", "TRUE"):
            return Promotion(False, d.state, to_state, by, "not-authorized",
                             "★ 代码裁决不是 PASS（★ 是 %r）" % v)
    d.state = to_state
    return Promotion(True, d.state, to_state, by, "", "★ 晋升成功")


#: ══════════════════════════════════════════════════════════════════════
# 四、同错两次 ⇒ 诊断触发（★ R9 —— ★ Q1 L32）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ Q1 L32 逐字：「「**同错误两次停下**」转成**诊断触发**，
#:   **不转成「一定是方法选错」的根因判定**」
SAME_ERROR_THRESHOLD = 2


@dataclass
class SameErrorTrigger:
    """★★ **同错两次 ⇒ 诊断触发**（★ R9）。

    ★★ **它不判根因** —— ★ 输出里**没有**「根因」这个字段
      （★ 判据是**结构性**的：`to_dict()` 里根本没有那个键）。
    """

    threshold: int = SAME_ERROR_THRESHOLD
    counts: dict = field(default_factory=dict)

    def observe(self, error_code: str) -> dict:
        """★ 记一次错误，回**触发判定**。"""
        n = int(self.counts.get(error_code, 0)) + 1
        self.counts[error_code] = n
        triggered = n >= self.threshold
        return {"error_code": error_code, "count": n,
                "triggered": triggered,
                "action": "DIAGNOSIS_REQUIRED" if triggered else "continue",
                #: ★★ **显式写"不判根因"** —— ★ 让这件事**看得见**
                "root_cause": None,
                "★": ("★ 只**触发诊断**；★ **不判根因**"
                       "（★ Q1 L32 逐字：「不转成「一定是方法选错」的根因判定」）")}

    def to_dict(self) -> dict:
        #: ★★ **结构性保证**：`to_dict()` 里**没有** `root_cause` 这个键
        return {"threshold": self.threshold, "counts": dict(self.counts),
                "★": "★ 本对象**不产出根因**（★ 字段根本不存在）"}


def check_same_error(observations: list, *,
                     threshold: int = SAME_ERROR_THRESHOLD) -> dict:
    """★ 由一串观察**算**触发（★ 便于测试）。"""
    t = SameErrorTrigger(threshold=threshold)
    last: dict = {}
    for code in observations:
        last = t.observe(code)
    return {"last": last, "counts": t.counts,
            "triggered": [c for c, n in t.counts.items() if n >= threshold]}
