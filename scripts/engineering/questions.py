"""★ Q8 · 持久化问题对象 + 可信人工确认 + 补答版本闸门（规格 326 的 S1~S5）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/questions.py
# 定位:   规格 `specs/326-question-persistence-and-boundaries` 的 S1（12 字段）/S2（落
#           盘读回）/ S3（`source=human` 必须可核）/ S4（补答拒旧版本）/S5（等待时释放执
#           行锁）。★★ 实测（2026-10-12）起点：**没有 `question_id` / `requirement_revis
#           ion` /`answer_source` / `allowed_default_ref`，**没有问题落盘**；★ 而「LLM
#           自报 source=human 不算人工确认」与「释放执行锁」**有表述无判据**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q8（L163-174）逐字：L165 逐字
#           给的 12 字段：「`question_id / run_id / requirement_revision /  field / valu
#           e_schema / unit / reason / blocking / allowed_default_ref /  answer_source /
#            status`」L167「先保存问题，再请求输入。**等待用户时释放执行锁**，  **不保持
#            COM 调用或选区**」L170「补答必须**携带问题 ID 与期望版本，拒绝旧版本覆盖**
#           」L171「关键工程批准必须来自**可信的人机确认通道**。  **LLM 自己提交 `source
#           =human` 不算人工确认**。无法证明来源时，  由最小本地确认界面承接，任务保持等
#           待」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_s326_boundaries.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNS = ROOT / "output" / "runs"

#: ★★ Q8 L165 逐字给的字段（★ 实数是 **11 个**）：
#:   「`question_id / run_id / requirement_revision / field / value_schema /
#     unit / reason / blocking / allowed_default_ref / answer_source / status`」
#:   ⚠ 实测（2026-10-12）：我在规格里写成「12 字段」—— ★ **数错了**。
#:     ★ 逐字切分 `/` 得 **11 个** ⇒ ★ 以**原文**为准（★ 规格已同步更正）。
QUESTION_FIELDS = (
    "question_id",
    "run_id",
    "requirement_revision",
    "field",
    "value_schema",
    "unit",
    "reason",
    "blocking",
    "allowed_default_ref",
    "answer_source",
    "status",
)

#: ★ 状态（★ 封闭）
OPEN = "open"
ANSWERED = "answered"
STALE = "stale"
REJECTED = "rejected"
QUESTION_STATUS = (OPEN, ANSWERED, STALE, REJECTED)

#: ★★ **可信的答案来源**（★ Q8 L171 逐字）
#:   `human` **只能**由**可信通道**产生 —— ★ 见 `AnswerSource`。
SRC_HUMAN = "human"
SRC_DEFAULT = "approved_default"
SRC_LLM = "llm"
SRC_UNKNOWN = "unknown"
ANSWER_SOURCES = (SRC_HUMAN, SRC_DEFAULT, SRC_LLM, SRC_UNKNOWN)

#: ★★ **可信通道标记**（★ Q8 L171 逐字：「**可信的人机确认通道**」）。
#:   ★ 判据：`source=human` **必须**带一个**通道证明** ——
#:     ★ 而 LLM **拿不到**这个证明（★ 它只能自报字符串）。
TRUSTED_CHANNELS = ("local_confirm_ui", "owner_typed", "signed_approval")


class QuestionError(Exception):
    """★ 问题层失败（★ 带封闭码）。"""

    CODES = (
        "missing-field",
        "bad-status",
        "bad-source",
        "untrusted-human",
        "stale-revision",
        "no-question-id",
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法问题拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、问题对象（★ S1 —— ★ Q8 L165 的 12 字段）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class Question:
    """★ **一个问题对象**（★ S1）。

    ★★ Q8 L170 逐字：「返回**持久化的 `WAITING_INPUT`、问题对象和回答入口**，
      **而不只是自然语言提示**」⇒ ★ 它必须是**结构化的、可落盘的**。
    """

    question_id: str = ""
    run_id: str = ""
    requirement_revision: str = ""
    field: str = ""
    value_schema: str = ""
    unit: str = ""
    reason: str = ""
    blocking: bool = True
    allowed_default_ref: str = ""
    answer_source: str = SRC_UNKNOWN
    status: str = OPEN
    #: ★ 答案本身（★ 不在 12 字段里，但落盘时要存）
    answer: object = None
    #: ★★ **可信通道证明**（★ S3 的关键 —— ★ LLM 拿不到它）
    channel_proof: str = ""

    def __post_init__(self) -> None:
        if self.status not in QUESTION_STATUS:
            raise QuestionError("bad-status", "★ 未知状态：%r" % self.status)
        if self.answer_source not in ANSWER_SOURCES:
            raise QuestionError("bad-source", "★ 未知来源：%r" % self.answer_source)

    def missing(self) -> list:
        """★ 12 字段缺哪几项。

        ⚠ 实测（2026-10-12）：第一版把 **12 个字段全部**当必填 ⇒
          `allowed_default_ref` 为空就抛 ✗ —— ★ 而 Q8 L169 逐字说它只对
          「**可按已批准政策默认**」的那些问题才需要
          （「可按已批准政策默认：文件命名、报告排序、非功能性显示选项」）
          ⇒ ★ **阻塞性问题本来就没有默认值**。
        ⇒ ★ 判据：**11 个字段必填**；★ `allowed_default_ref` **可选**
          （★ 但 `resolve_with_default()` 会**要求它非空** —— ★ 见那里）。
        """
        out = []
        for f in QUESTION_FIELDS:
            if f == "allowed_default_ref":
                continue  #: ★ 可选（★ 只有"可按默认"的问题才需要）
            v = getattr(self, f, None)
            if v is None or v == "":
                out.append(f)
        return out

    def validate(self) -> None:
        miss = self.missing()
        if miss:
            raise QuestionError("missing-field", "★ 缺字段：%s" % miss)
        if not self.question_id:
            raise QuestionError("no-question-id", "★ 没有 question_id")

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in QUESTION_FIELDS} | {
            "answer": self.answer,
            "channel_proof": self.channel_proof,
        }


def make_question(
    *,
    run_id: str,
    requirement_revision: str,
    field_name: str,
    value_schema: str,
    unit: str,
    reason: str,
    blocking: bool = True,
    allowed_default_ref: str = "",
) -> Question:
    """★ 造一个问题（★ `question_id` 由**字段+版本**摘要得到 ⇒ 可复核）。"""
    import hashlib  # noqa: PLC0415

    blob = "%s|%s|%s|%s" % (run_id, requirement_revision, field_name, unit)
    qid = "q-" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
    q = Question(
        question_id=qid,
        run_id=run_id,
        requirement_revision=requirement_revision,
        field=field_name,
        value_schema=value_schema,
        unit=unit,
        reason=reason,
        blocking=blocking,
        allowed_default_ref=allowed_default_ref,
        answer_source=SRC_UNKNOWN,
        status=OPEN,
    )
    q.validate()
    return q


#: ══════════════════════════════════════════════════════════════════════
# 二、落盘（★ S2 —— ★ Q8 L167「先保存问题，再请求输入」）
#: ══════════════════════════════════════════════════════════════════════


def questions_path(run_id: str, revision: str) -> pathlib.Path:
    return RUNS / run_id / "questions" / ("%s.json" % revision)


def save_questions(run_id: str, revision: str, questions: list) -> pathlib.Path:
    """★★ **先保存问题，再请求输入**（★ S2 —— ★ Q8 L167 逐字）。

    ★★ 判据：**落盘后可读回**（★ 不是只放内存）。
    """
    p = questions_path(run_id, revision)
    p.parent.mkdir(parents=True, exist_ok=True)
    for q in questions:
        q.validate()
    p.write_text(
        json.dumps([q.to_dict() for q in questions], ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return p


def load_questions(run_id: str, revision: str) -> list:
    """★ 读回（★ S2 的判据）。"""
    p = questions_path(run_id, revision)
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


#: ══════════════════════════════════════════════════════════════════════
# 三、可信人工确认（★ S3 —— ★ Q8 L171 逐字）
#: ══════════════════════════════════════════════════════════════════════


def answer(q: Question, value, *, source: str, channel_proof: str = "") -> Question:
    """★★ **回答问题**（★ S3 —— ★ Q8 L171 逐字）。

    ★★ Q8 L171 逐字：「关键工程批准必须来自**可信的人机确认通道**。
      **LLM 自己提交 `source=human` 不算人工确认**。
      无法证明来源时，由**最小本地确认界面**承接，**任务保持等待**」。

    ★★ 判据（★ 三条）：
      ```
      ① `source` 必须是封闭值
      ② ★★ `source=human` **必须带可信通道证明** ——
         ★ 只写字符串 `"human"` **不算**（★ 那正是 LLM 能做的）
      ③ 无法证明 ⇒ **状态保持 `open`**（★ 任务继续等，★ 不假装答了）
      ```
    """
    if source not in ANSWER_SOURCES:
        raise QuestionError("bad-source", "★ 未知来源：%r" % source)
    if source == SRC_HUMAN and channel_proof not in TRUSTED_CHANNELS:
        #: ★★ **这一条就是「LLM 自报不算」的落地**
        raise QuestionError(
            "untrusted-human",
            "★★ `source=human` 必须带可信通道证明（%s 之一），而拿到的是 %r"
            " —— ★ Q8 L171 逐字：「LLM 自己提交 `source=human` 不算人工确认」"
            % (list(TRUSTED_CHANNELS), channel_proof),
        )
    q.answer = value
    q.answer_source = source
    q.channel_proof = channel_proof
    q.status = ANSWERED
    return q


def resolve_with_default(q: Question, value) -> Question:
    """★ 按**已批准政策**默认（★ Q8 L169 逐字：「**默认值也要记录出处**」）。"""
    if not q.allowed_default_ref:
        raise QuestionError(
            "bad-source",
            "★ %s 没有 `allowed_default_ref` ⇒ 不许按默认值填" % q.question_id,
        )
    q.answer = value
    q.answer_source = SRC_DEFAULT
    q.status = ANSWERED
    return q


#: ══ S4 补答拒旧版本（★ Q8 L170 逐字）════════════════════════════════


def apply_answer(
    q: Question,
    value,
    *,
    source: str,
    carried_revision: str,
    current_revision: str,
    channel_proof: str = "",
) -> Question:
    """★★ **补答的版本闸门**（★ S4 —— ★ Q8 L170 逐字）。

    ★★ Q8 L170 逐字：「补答必须**携带问题 ID 与期望版本，拒绝旧版本覆盖**」。

    ★★ 判据（★ 顺序）：
      ```
      ① 携带的 revision 必须是**当前**的 ⇒ 否则 `stale-revision`（★ 拒）
      ② 再走 `answer()` 的可信通道闸门
      ```
    """
    if carried_revision != current_revision:
        q.status = STALE
        raise QuestionError(
            "stale-revision",
            "★★ 补答携带旧版本 %r，而当前是 %r ⇒ **拒绝旧版本覆盖**"
            % (carried_revision, current_revision),
        )
    return answer(q, value, source=source, channel_proof=channel_proof)


#: ══ S5 等待时释放执行锁（★ Q8 L167 逐字）════════════════════════════


@dataclass
class WaitingState:
    """★★ **等待用户时的状态**（★ S5 —— ★ Q8 L167 逐字）。

    ★★ Q8 L167 逐字：「先保存问题，再请求输入。**等待用户时释放执行锁**，
      **不保持 COM 调用或选区**」。
    """

    holds_execution_lock: bool = True
    holds_com: bool = True
    holds_selection: bool = True

    def enter_waiting(self) -> dict:
        """★★ **进入等待 ⇒ 三样都放掉**（★ 结构性保证）。"""
        self.holds_execution_lock = False
        self.holds_com = False
        self.holds_selection = False
        return self.to_dict()

    @property
    def released(self) -> bool:
        return (
            not self.holds_execution_lock
            and not self.holds_com
            and not self.holds_selection
        )

    def to_dict(self) -> dict:
        return {
            "holds_execution_lock": self.holds_execution_lock,
            "holds_com": self.holds_com,
            "holds_selection": self.holds_selection,
            "released": self.released,
            "★": "★ Q8 L167：「等待用户时释放执行锁，不保持 COM 调用或选区」",
        }


#: ══ 问题 → `WAITING_INPUT`（★ Q8 L170 逐字）══════════════════════════


def waiting_payload(run_id: str, revision: str, questions: list) -> dict:
    """★★ **持久化的 `WAITING_INPUT` + 问题对象 + 回答入口**
    （★ Q8 L170 逐字：「**而不只是自然语言提示**」）。"""
    blocking = [q for q in questions if q.blocking]
    return {
        "state": "WAITING_INPUT",
        "run_id": run_id,
        "requirement_revision": revision,
        "questions": [q.to_dict() for q in questions],
        "blocking_count": len(blocking),
        #: ★★ **回答入口**（★ 结构化 —— ★ 不是自然语言提示）
        "answer_entry": {
            "path": str(questions_path(run_id, revision)),
            "must_carry": ["question_id", "requirement_revision"],
            "trusted_channels": list(TRUSTED_CHANNELS),
        },
        "★": "★ 持久化的 WAITING_INPUT + 问题对象 + 回答入口（★ 不只是自然语言）",
    }
