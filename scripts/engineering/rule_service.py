"""★ Q13 · 规则取证服务：公式与依据分开（规格 327 的 T5~T9）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/rule_service.py
# 定位:   规格 `specs/327-release-manifest-rules-and-runs` 的 T5（`RuleRequest`）/T6（
#           `RuleResult`）/ T7（公式与依据分开）/ T8（效力来源不可只引摘要）/T9（30 天新
#           鲜度）。★★ 实测（2026-10-12）起点：四档 verdict（含 `NOT_APPLICABLE`）、`cit
#           ations`、`authority_status`、30 天新鲜度、`INDETERMINATE`**都已具备**（`comp
#           liance.py` / `rules.py` / `rule_verdicts.py`）；★ 而**没有 `RuleRequest` / `
#           RuleResult` / `rule_code_digest`**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q13（L233-259）逐字：L235「规
#           则由规划器和方法共同使用，**不复制进每种方法**。  **规则实现与依据必须分开**
#           ：**一个公式能运行，不表示它对当前材料、  工况和标准版本适用**」L237-251 逐
#           字给的 `RuleRequest` 与 `RuleResult` 两个结构L255「**效力来源不可只引用检索
#           引擎生成的摘要**」L257「本期效力核查采用**交付日前 30 天内**的官方状态记录作
#           为项目  新鲜度政策；……**离线缓存可按其快照日期使用，但不能宣称已经  核对到今
#           天**」L259「不能计算或缺证据就返回 `INDETERMINATE`。……**保留几何方案或  计算
#           草稿，但不授予合规通过**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

#: ★★ Q13 L245 逐字给的四档 verdict
PASS = "PASS"
FAIL = "FAIL"
INDETERMINATE = "INDETERMINATE"
NOT_APPLICABLE = "NOT_APPLICABLE"
VERDICTS = (PASS, FAIL, INDETERMINATE, NOT_APPLICABLE)

#: ★★ **本期效力核查的新鲜度政策**（★ Q13 L257 逐字：**30 天**）
FRESHNESS_DAYS = 30


class RuleError(Exception):
    """★ 规则层失败（★ 带封闭码）。"""

    CODES = (
        "missing-field",
        "bad-verdict",
        "summary-only-source",
        "stale-authority",
        "no-implementation",
        "not-applicable",
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法规则拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、RuleRequest（★ T5 —— ★ Q13 L237-243 逐字）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ Q13 L239-243 逐字给的字段
REQUEST_FIELDS = (
    "rule_id",
    "rule_version",
    "inputs",
    "application_context",
    "required_standard_editions",
    "evidence_bundle_ref",
)


@dataclass
class RuleRequest:
    """★★ **规则请求**（★ T5 —— ★ Q13 L237-243 逐字）。

    ★★ 判据：**`inputs` 带单位与来源**（★ Q13 L240 逐字：「带单位、来源、
      必要时带区间的数据」）；★ `application_context` **必须**有
      （★ Q13 L241 逐字：「产品用途、工况、司法辖区、合同要求、日期」）。
    """

    rule_id: str = ""
    rule_version: int = 0
    inputs: list = field(default_factory=list)  #: [{name,value,unit,source}]
    application_context: dict = field(default_factory=dict)
    required_standard_editions: list = field(default_factory=list)
    evidence_bundle_ref: str = ""

    def missing(self) -> list:
        out = []
        for f in REQUEST_FIELDS:
            v = getattr(self, f, None)
            if v is None or v == "" or v == [] or v == {}:
                out.append(f)
        return out

    def validate(self) -> None:
        miss = self.missing()
        if miss:
            raise RuleError("missing-field", "★ 缺字段：%s" % miss)
        #: ★★ **每个输入都要带单位与来源**（★ Q13 L240 逐字）
        for x in self.inputs:
            for k in ("name", "value", "unit", "source"):
                if not x.get(k) and x.get(k) != 0:
                    raise RuleError(
                        "missing-field",
                        "★ 输入 %r 缺 `%s`（★ Q13 L240：「带单位、来源」）"
                        % (x.get("name"), k),
                    )

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in REQUEST_FIELDS}


#: ══════════════════════════════════════════════════════════════════════
# 二、RuleResult（★ T6 —— ★ Q13 L245-251 逐字）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ Q13 L245-251 逐字给的字段
RESULT_FIELDS = (
    "verdict",
    "outputs",
    "checked_preconditions",
    "failed_obligations",
    "citations",
    "authority_status",
    "missing_evidence",
    "rule_code_digest",
)


@dataclass
class RuleResult:
    """★★ **规则结果**（★ T6 —— ★ Q13 L245-251 逐字）。

    ★★ **★ 关键设计：`rule_code_digest` 与 `citations` 是**两个独立字段****
      —— ★ 一个说「**算的是什么**」，★ 一个说「**依据是什么**」。
      ★ 那正是 Q13 L235 逐字要的「**规则实现与依据必须分开**」。
    """

    verdict: str = INDETERMINATE
    outputs: dict = field(default_factory=dict)
    checked_preconditions: list = field(default_factory=list)
    failed_obligations: list = field(default_factory=list)
    citations: list = field(default_factory=list)
    authority_status: dict = field(default_factory=dict)
    missing_evidence: list = field(default_factory=list)
    rule_code_digest: str = ""
    #: ★★ **适用性**（★ Q13 L235 逐字：「一个公式能运行，**不表示它对当前材料、
    #:   工况和标准版本适用**」）—— ★ 单独一个字段，★ 与 `verdict` 分开
    applicability: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise RuleError("bad-verdict", "★ 未知 verdict：%r" % self.verdict)

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in RESULT_FIELDS} | {
            "applicability": self.applicability,
            "★": "★ `rule_code_digest`（算的是什么）与 `citations`（依据是什么）**分开**",
        }


#: ══════════════════════════════════════════════════════════════════════
# 三、效力来源（★ T8 —— ★ Q13 L255）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **效力来源的种类**（★ Q13 L255 逐字）
SRC_OFFICIAL = "official_status_record"  #: ★ 官方状态记录 —— **可用**
SRC_SUMMARY = "retrieval_summary"  #: ★ 检索引擎生成的摘要 —— **不可单独用**
SRC_CONTRACT = "contract_specified"  #: ★ 合同指定
SRC_CACHED = "offline_cache"  #: ★ 离线缓存（★ 按快照日期用）
AUTHORITY_SOURCES = (SRC_OFFICIAL, SRC_SUMMARY, SRC_CONTRACT, SRC_CACHED)


def check_authority(authority_status: dict) -> dict:
    """★★ **效力来源检查**（★ T8 —— ★ Q13 L255 逐字）。

    ★★ Q13 L255 逐字：「**效力来源不可只引用检索引擎生成的摘要**」。

    ★★ 判据（★ 两条）：
      ```
      ① `source` 必须是封闭值
      ② ★★ 只有 `retrieval_summary` ⇒ **INDETERMINATE**
         （★ 必须另有**官方状态记录**或**合同指定**）
      ```
    """
    src = str(authority_status.get("source") or "")
    if src not in AUTHORITY_SOURCES:
        return {
            "ok": False,
            "code": "summary-only-source",
            "verdict": INDETERMINATE,
            "reason": "★ 未知效力来源：%r" % src,
        }
    if src == SRC_SUMMARY:
        return {
            "ok": False,
            "code": "summary-only-source",
            "verdict": INDETERMINATE,
            "reason": (
                "★★ **只引检索引擎生成的摘要** ⇒ `INDETERMINATE`"
                "（★ Q13 L255 逐字：「效力来源不可只引用检索引擎生成的摘要」）"
            ),
        }
    return {
        "ok": True,
        "code": "",
        "verdict": PASS,
        "source": src,
        "reason": "★ 有官方状态记录／合同指定 ⇒ 可用",
    }


#: ══ T9 新鲜度（★ Q13 L257 逐字）══════════════════════════════════════


def check_freshness(checked_on: str, *, today: str, days: int = FRESHNESS_DAYS) -> dict:
    """★★ **30 天新鲜度政策**（★ T9 —— ★ Q13 L257 逐字）。

    ★★ Q13 L257 逐字：「本期效力核查采用**交付日前 30 天内**的官方状态记录
      作为项目新鲜度政策；……**离线缓存可按其快照日期使用，但不能宣称
      已经核对到今天**」。

    ★★ 判据：`(today - checked_on).days > 30` ⇒ **stale**。
    """
    import datetime as _dt  # noqa: PLC0415

    def _parse(s: str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
            try:
                return _dt.datetime.strptime(s[: len(fmt) + 2].strip(), fmt)
            except ValueError:
                continue
        return None

    a, b = _parse(checked_on), _parse(today)
    if a is None or b is None:
        return {
            "ok": False,
            "stale": True,
            "code": "stale-authority",
            "reason": "★ 日期解析不了：%r / %r" % (checked_on, today),
        }
    age = (b - a).days
    stale = age > days
    return {
        "ok": not stale,
        "stale": stale,
        "age_days": age,
        "limit": days,
        "code": "stale-authority" if stale else "",
        "reason": (
            "★ 效力记录 %d 天前（> %d）⇒ **stale**" % (age, days)
            if stale
            else "★ 在 %d 天内 ⇒ 新鲜" % days
        ),
        "★": "★ Q13 L257：30 天新鲜度政策（★ 离线缓存按快照日期用，不宣称核对到今天）",
    }


#: ══════════════════════════════════════════════════════════════════════
# 四、裁决（★ T7 —— ★ Q13 L235）
#: ══════════════════════════════════════════════════════════════════════


def rule_code_digest(module: str, function: str) -> str:
    """★ 规则**实现**的摘要（★ Q13 L251 逐字要的 `rule_code_digest`）。"""
    import importlib  # noqa: PLC0415

    try:
        mod = importlib.import_module(module)
    except Exception:  # noqa: BLE001
        return ""
    fn = getattr(mod, function, None)
    if fn is None:
        return ""
    src = ""
    try:
        import inspect  # noqa: PLC0415

        src = inspect.getsource(fn)
    except Exception:  # noqa: BLE001
        src = function
    return hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]


def evaluate_rule(
    req: RuleRequest,
    *,
    formula_ok: bool,
    applicability_ok: bool,
    authority_status: dict | None = None,
    checked_on: str = "",
    today: str = "",
) -> RuleResult:
    """★★ **规则裁决**（★ T7 —— ★ Q13 L235 逐字）。

    ★★ Q13 L235 逐字：「**一个公式能运行，不表示它对当前材料、工况和
      标准版本适用**」。

    ★★ 判据顺序（★ 最严的在前）：
      ```
      ① 请求缺字段              ⇒ 拒
      ② 效力来源只引摘要        ⇒ INDETERMINATE
      ③ 效力记录 stale          ⇒ INDETERMINATE
      ④ 公式**跑不通**          ⇒ FAIL
      ⑤ ★★ 公式跑通但**不适用** ⇒ NOT_APPLICABLE
         （★ 这就是「能运行 ≠ 适用」的落地 —— ★ 不是 PASS）
      ⑥ 都过                    ⇒ PASS
      ```
    """
    req.validate()
    auth = authority_status or {}

    #: ② 效力来源
    a = check_authority(auth)
    if not a["ok"]:
        return RuleResult(
            verdict=INDETERMINATE,
            missing_evidence=["authority_status:" + str(a.get("code"))],
            authority_status=auth,
            rule_code_digest=rule_code_digest(
                "engineering.rule_service", "evaluate_rule"
            ),
            applicability={"ok": applicability_ok},
        )

    #: ③ 新鲜度
    if checked_on and today:
        f = check_freshness(checked_on, today=today)
        if f["stale"]:
            return RuleResult(
                verdict=INDETERMINATE,
                missing_evidence=["authority_status:stale"],
                authority_status=auth | {"freshness": f},
                rule_code_digest=rule_code_digest(
                    "engineering.rule_service", "evaluate_rule"
                ),
                applicability={"ok": applicability_ok},
            )

    #: ④ 公式
    if not formula_ok:
        return RuleResult(
            verdict=FAIL,
            failed_obligations=["formula"],
            authority_status=auth,
            rule_code_digest=rule_code_digest(
                "engineering.rule_service", "evaluate_rule"
            ),
            applicability={"ok": applicability_ok},
        )

    #: ⑤ ★★ **能运行 ≠ 适用**
    if not applicability_ok:
        return RuleResult(
            verdict=NOT_APPLICABLE,
            checked_preconditions=list(req.required_standard_editions),
            failed_obligations=["applicability"],
            authority_status=auth,
            rule_code_digest=rule_code_digest(
                "engineering.rule_service", "evaluate_rule"
            ),
            applicability={
                "ok": False,
                "reason": (
                    "★★ 公式**能运行**，但**对当前材料/工况/"
                    "标准版本不适用** ⇒ `NOT_APPLICABLE`"
                    "（★ Q13 L235 逐字）"
                ),
            },
        )

    return RuleResult(
        verdict=PASS,
        authority_status=auth,
        rule_code_digest=rule_code_digest("engineering.rule_service", "evaluate_rule"),
        applicability={"ok": True},
    )
