"""★ 阶段 2 · 七档规则评价（规格 317 的 D3）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/rule_verdicts.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D3（规则评价七档）。
#           ★★ 实测（2026-10-12）缺口：`scripts/engineering/rules.py` 的 `Verdict`
#           只有 **4 档**（PASS/FAIL/UNKNOWN/NEEDS_CLARIFICATION），而阶段 2 要求
#           **七种固定结果**（含 `RuleError(MISSING_INPUT)` / `RuleError(UNIT_MISMATCH)` /
#           `NOT_APPLICABLE` / `INDETERMINATE(SOURCE_MISSING)` / `INDETERMINATE(STATUS_UNKNOWN)`）。
#           ★ 本模块**扩展**它（★ 不推倒 —— 既有 4 档继续有效）。
# 官方依据: ① 外部方案阶段 2 的七档（逐字）
#           ② 本仓 `scripts/engineering/rules.py` 的既有 4 档与 `StandardRef`
#           ③ 涉法规/标准结论**必须先用 `ks` 工具核验**（业主常驻纪律）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（★ 规则层是纯计算，无真机依赖）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、七档（★ 封闭集 —— 新增档必须同时加进 `ALL_VERDICTS`）
#: ══════════════════════════════════════════════════════════════════════

PASS = "PASS"
FAIL = "FAIL"
ERR_MISSING_INPUT = "RuleError(MISSING_INPUT)"
ERR_UNIT_MISMATCH = "RuleError(UNIT_MISMATCH)"
NOT_APPLICABLE = "NOT_APPLICABLE"
IND_SOURCE_MISSING = "INDETERMINATE(SOURCE_MISSING)"
IND_STATUS_UNKNOWN = "INDETERMINATE(STATUS_UNKNOWN)"

ALL_VERDICTS = (PASS, FAIL, ERR_MISSING_INPUT, ERR_UNIT_MISMATCH,
                NOT_APPLICABLE, IND_SOURCE_MISSING, IND_STATUS_UNKNOWN)

#: ★★ **放行集 = 只有 PASS**（★ 不变式 J9 —— ★ 别的都不得放行）
RELEASING = (PASS,)
#: ★ 「算得出数但不算通过」的那几档（★ 判据顺序把它们排在 PASS 之前）
NON_RELEASING_DETERMINATE = (FAIL, ERR_MISSING_INPUT, ERR_UNIT_MISMATCH,
                             NOT_APPLICABLE)
#: ★ 「缺依据」的那几档
INDETERMINATE = (IND_SOURCE_MISSING, IND_STATUS_UNKNOWN)


@dataclass(frozen=True)
class RuleOutcome:
    verdict: str
    rule_id: str
    citation: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        assert self.verdict in ALL_VERDICTS, "★ 非法判定：%r" % self.verdict

    @property
    def releasing(self) -> bool:
        return self.verdict in RELEASING


#: ══════════════════════════════════════════════════════════════════════
# 二、规则声明（★ 最小形状 —— 够判七档即可）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RuleSpec:
    """★ 一条规则（★ 判七档所需的全部输入都在这里）。"""

    id: str
    #: ★ 必填量：`{名: 单位}` —— ★ 单位是 `UNIT_MISMATCH` 的判据
    required_inputs: dict = field(default_factory=dict)
    #: ★ 适用范围：`{名: (min, max)}` —— ★ 超出 ⇒ `NOT_APPLICABLE`
    applicability: dict = field(default_factory=dict)
    #: ★ 依据（★ 空 ⇒ `SOURCE_MISSING`）
    citation: str = ""
    #: ★ 效力（★ `unknown` ⇒ `STATUS_UNKNOWN`）
    effectiveness: str = "effective"


def evaluate(spec: RuleSpec, inputs: dict, *, units: dict | None = None,
             compute=None) -> RuleOutcome:
    """★ 七档评价（★ 判据顺序**最严的在前**）。

    ★★ 判据顺序（★ 见 data-model §3）—— **④⑤ 必须在 ⑥ 之前**：
      ```
      ① 缺必填量      ⇒ RuleError(MISSING_INPUT)
      ② 单位不符      ⇒ RuleError(UNIT_MISMATCH)
      ③ 超适用范围    ⇒ NOT_APPLICABLE
      ④ 缺原文        ⇒ INDETERMINATE(SOURCE_MISSING)
      ⑤ 效力未知      ⇒ INDETERMINATE(STATUS_UNKNOWN)
      ⑥ 算得出且满足  ⇒ PASS
      ⑦ 算得出且不满足⇒ FAIL
      ```
      ★★ 若把 ④⑤ 放到 ⑥ 之后，「缺原文但公式算得出数」就会**报 PASS**
        —— ★ 那正是 **N3 突变**要抓的。
    """
    units = units or {}

    #: ① 缺必填量
    missing = [k for k in (spec.required_inputs or {}) if k not in inputs]
    if missing:
        return RuleOutcome(ERR_MISSING_INPUT, spec.id,
                           citation=spec.citation,
                           detail="★ 缺必填量：%s" % missing)

    #: ② 单位不符
    bad_units = []
    for k, want in (spec.required_inputs or {}).items():
        got = units.get(k)
        if got is not None and want and got != want:
            bad_units.append("%s: 要 %s 得 %s" % (k, want, got))
    if bad_units:
        return RuleOutcome(ERR_UNIT_MISMATCH, spec.id,
                           citation=spec.citation,
                           detail="★ 单位不符：%s" % bad_units)

    #: ③ 超适用范围
    out_of = []
    for k, (lo, hi) in (spec.applicability or {}).items():
        v = inputs.get(k)
        if v is None:
            continue
        try:
            if (lo is not None and v < lo) or (hi is not None and v > hi):
                out_of.append("%s=%s 不在 [%s, %s]" % (k, v, lo, hi))
        except TypeError:
            pass
    if out_of:
        return RuleOutcome(NOT_APPLICABLE, spec.id,
                           citation=spec.citation,
                           detail="★ 超适用范围：%s" % out_of)

    #: ④ 缺原文（★ 必须在 PASS 之前）
    if not (spec.citation or "").strip():
        return RuleOutcome(IND_SOURCE_MISSING, spec.id,
                           detail="★ 缺依据（citation 为空）⇒ 不得报 PASS")

    #: ⑤ 效力未知（★ 必须在 PASS 之前）
    if (spec.effectiveness or "").lower() in ("unknown", ""):
        return RuleOutcome(IND_STATUS_UNKNOWN, spec.id,
                           citation=spec.citation,
                           detail="★ 效力未知 ⇒ 不得报 PASS")

    #: ⑥⑦ 计算
    if compute is None:
        #: ★ 没给计算器 ⇒ 只能到「依据齐、效力明」为止
        #:   ★ 但那**不是**「满足要求」⇒ 按**保守**报 INDETERMINATE
        return RuleOutcome(IND_STATUS_UNKNOWN, spec.id, citation=spec.citation,
                           detail="★ 没给计算器 ⇒ 无法判满足与否（★ 保守）")
    ok = bool(compute(inputs))
    return RuleOutcome(PASS if ok else FAIL, spec.id, citation=spec.citation,
                       detail="★ 计算完成：%s" % ("满足" if ok else "不满足"))


#: ══════════════════════════════════════════════════════════════════════
# 三、批量评价 + 放行判据
#: ══════════════════════════════════════════════════════════════════════

def release_verdict(outcomes: list[RuleOutcome]) -> dict:
    """★ 整批放行判据（★ J9：**只有 PASS 能放行**）。

    ★★ 判据（★ 与外部方案「缺依据的关键规则不能报通过」一致）：
      · 有**任何一条**非 PASS ⇒ **不得放行**
      · 且要**分类报出**：几条 PASS · 几条 FAIL · 几条 INDETERMINATE
    """
    n_pass = sum(1 for o in outcomes if o.verdict == PASS)
    bad = [o for o in outcomes if o.verdict != PASS]
    return {
        "release": not bad,
        "total": len(outcomes),
        "passed": n_pass,
        "blocking": [{"rule": o.rule_id, "verdict": o.verdict,
                      "detail": o.detail} for o in bad],
        "indeterminate": [o.rule_id for o in outcomes
                          if o.verdict in INDETERMINATE],
        "★": "★ 只有 PASS 能放行（★ J9）",
    }
