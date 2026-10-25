"""★ E7 结论可溯源：采集器与判定器。

## 判据（`docs/ENGINEERING-PATH.md` 第四节）

**必须读什么**：每条工程判断解析到有效证据或可复算依据；
核原文/算法、适用性、版本、来源完整性、输入与产物绑定。

**必须能拒绝的负例**：假引用、摘要冒原文、旧版本证据、随意填来源标签、空 citations、缺文件。

**不能当替代品**：标准号字符串、台账 verified、生成者的结论文本。

## ★★ 关键：两个布尔 + 来源标签不得给 PASS

`rule_service.evaluate_rule` 在 `formula_ok=True` / `applicability_ok=True` 时直接返回
`PASS`，而 `outputs={}`、`citations=[]`
（出处：`docs/state/facts/R-engineering-path.md` R-09）。

判定器必须要求：**有输出、有引用、引用可解析**，而不是只看两个布尔。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/e7_provenance.py
# 定位:   `specs/349-e1-e7-acceptance` 的 E7（结论可溯源）。
#          ★ 判定器要求引用非空且可解析、有可复算输出、版本一致 ——
#            因为 `rule_service.evaluate_rule` 在 `formula_ok`/`applicability_ok`
#            两个布尔为真时直接返回 PASS，而 outputs 与 citations 都是空的
#            （实测出处 `docs/state/facts/R-engineering-path.md` R-09）。
# 官方依据: 不适用（本文件不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

import re

from .result import CheckResult, Observation, Status

CHECKER_VERSION = "s1-1"


#: ★ 明确不是出处的一批占位符（**归一化后完全相等**才拒 —— 不做模糊匹配，免得误伤真词）
PLACEHOLDER_LOCATORS = frozenset(
    {
        "",
        "-",
        "--",
        "?",
        "x",
        "n/a",
        "na",
        "none",
        "null",
        "无",
        "略",
        "见上",
        "见前",
        "见下",
        "同上",
        "同前",
        "同上文",
        "见附件",
        "见原文",
        "待补",
        "待定",
        "tbd",
        "todo",
        "placeholder",
    }
)

#: ★ 可指认的定位形态（命中任一即算「像出处」）
_LOCATOR_PATTERNS = (
    r"[表图]\s*\d",                                  # 表1 / 图3
    r"第\s*[0-9一二三四五六七八九十百.]+\s*[条款节项]",
    r"§\s*\d",
    r"(?i)\b(annex|appendix|clause|section|chapter)\s*[A-Z0-9]",
    r"\b[A-Z]{2,}(?:/[A-Z]{1,2})?\s*\d",             # GB/T 1804 · GB 30871 · ISO 2768
    r"\d+\s*\.\s*\d+",                            # 5.2 · 4.1.3
    #: ★★★ 第 64 轮：`measured` 类证据的自然出处是「**文件 + 字段**」。
    #:   `output/e3-feature-tree.json#features` / `output/x.json → features`
    #:   ★ 只给文件名**不算**（没有指认到哪一条读数，与「见附件」同类）。
    r"\S+\.(?:json|md|csv|txt|yaml|yml)\s*(?:#|::|→)\s*\S+",
)


def locator_looks_cited(locator: object) -> tuple[bool, str]:
    """★ 判一个 `locator` 是不是**可指认的出处**，回 `(是否像, 理由)`。

    ★ 只拦「明显不是出处」的占位符 —— **不能**证明那个条款真的存在。
      真正核对要靠本地知识库（`ks_*`）。这是硬边界的如实陈述。

    返回 `(True, "")` 或 `(False, 原因)`。
    """
    raw = str(locator or "")
    norm = raw.strip().lower()
    if norm in PLACEHOLDER_LOCATORS:
        return False, "占位符 %r 不是可指认的出处" % raw.strip()
    for pat in _LOCATOR_PATTERNS:
        if re.search(pat, raw):
            return True, ""
    return False, (
        "定位串 %r 里没有任何可指认的形态（表/图/条/§/标准号/点分条款号）"
        % raw.strip()
    )


#: ★ 允许的来源标签（封闭词表 —— 表外一律不算有效来源）
VALID_SOURCES = (
    "official_doc",       #: 官方 API 文档 / 标准原文
    "standard_clause",    #: 标准条款（带条款号）
    "code_algorithm",     #: 本仓可复算的算法
    "measured",           #: 本机实测读数
)


def collect_provenance(
    *, target: str, claims: tuple, citations: tuple, outputs: dict,
    source_kind: str, source_ref: str, artifact_version: str = "",
    evidence_version: str = "", version: str = "",
) -> Observation:
    """★ 采集器：把「结论、引用、输出、来源」原样记下来。

    `claims` 每项形如 `{"id": str, "text": str}`；
    `citations` 每项形如 `{"claim_id": str, "locator": str, "resolved": bool}`。
    """
    return Observation(
        target=target,
        #: ★★★ 第 36 轮修：版本必须**两边都声明**。
        #:
        #:   原判据 `if v["evidence_version"] and v["artifact_version"]:`
        #:   ⇒ 任一为空就整条跳过 ⇒ 「旧版本证据」可靠「不声明产物版本」绕过
        #:   （实测三种为空情形全部 pass）。
        #:   ⇒ 把义务提到采集层：没声明 = 没取到必要输入 = 采集不完整 ⇒ unknown。
        #:   ★ 不是放宽：修之前是**静默 pass**（最糟），现在是明确的 unknown。
        complete=(
            bool(claims)
            and bool(source_kind)
            and bool(str(artifact_version or "").strip())
            and bool(str(evidence_version or "").strip())
        ),
        values={
            "claims": list(claims),
            "citations": list(citations),
            "outputs": dict(outputs or {}),
            "source_kind": source_kind,
            "source_ref": source_ref,
            "artifact_version": artifact_version,
            "evidence_version": evidence_version,
            "version": version,
        },
        note=(
            ""
            if (
                claims
                and source_kind
                and str(artifact_version or "").strip()
                and str(evidence_version or "").strip()
            )
            else (
                "没声明产物或证据版本 ⇒ 无法判「旧版本证据」"
                if claims and source_kind
                else "没有判断或来源标签 ⇒ 采集不完整"
            )
        ),
    )


def judge_provenance(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E7 结论可溯源。"""
    base = dict(
        check_id="E7.provenance",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E7：每条工程判断解析到有效证据或可复算依据",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values

    #: ★★ ① 来源标签必须在封闭词表里（「随意填来源标签」是负例）
    if v["source_kind"] not in VALID_SOURCES:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"source_kind": v["source_kind"]},
            expected={"in": list(VALID_SOURCES)},
            reason="★ 来源标签 %r 不在有效来源表里（不得随意填）" % v["source_kind"],
        )

    #: ② 来源引用不能空（「标准号字符串」不是依据）
    if not str(v["source_ref"]).strip():
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"source_ref": ""}, expected={"source_ref": "非空"},
            reason="★ 来源引用为空 ⇒ 只有标签没有依据",
        )

    #: ★★ ③ 引用不能空（R-09 的伪造手法：citations=[] 仍给 PASS）
    cites = v["citations"]
    if not cites:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"citations": 0}, expected={"citations": "≥1"},
            reason=(
                "★ 一条引用都没有 ⇒ 这不是可溯源，是自我认证"
                "（R-09 的伪造手法：两个布尔 + 来源标签就给 PASS）"
            ),
        )

    #: ④ 每条判断都要有解析得到的引用
    covered = {str(c.get("claim_id", "")) for c in cites if c.get("resolved")}
    uncovered = [c.get("id") for c in v["claims"] if str(c.get("id", "")) not in covered]
    if uncovered:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"uncovered_claims": uncovered[:8], "count": len(uncovered)},
            expected={"uncovered_claims": 0},
            reason="★ %d 条判断没有解析到引用：%s" % (len(uncovered), uncovered[:5]),
        )

    #: ★★ ④b 每条引用的 `locator` 必须像真出处（**假引用**是 E7 的第一条负例）
    #:
    #:   ★ 为什么需要：`resolved=True` 是**调用方自己声明**的，
    #:     「解析得到」这件事没有第三方校验 ⇒ 填 `locator="见上"` + `resolved=True` 就能过。
    #:   ⚠ 本判据只能拦「明显不是出处」的占位符，**不能**证明条款真实存在。
    bad_locators = []
    for c in cites:
        if not c.get("resolved"):
            continue
        ok_loc, why = locator_looks_cited(c.get("locator"))
        if not ok_loc:
            bad_locators.append({"claim_id": c.get("claim_id"), "why": why})
    if bad_locators:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"bad_locators": bad_locators[:8], "count": len(bad_locators)},
            expected={"locator": "表/图/条/§/标准号/点分条款号 任一形态"},
            reason=(
                "★ %d 条引用声明 resolved=True 但 locator 不是可指认的出处：%s"
                % (len(bad_locators), [b["why"] for b in bad_locators[:3]])
            ),
        )

    #: ⑤ 证据版本必须与产物版本绑定（「旧版本证据」是负例）
    if v["evidence_version"] and v["artifact_version"]:
        if v["evidence_version"] != v["artifact_version"]:
            return CheckResult(
                **base, status=Status.FAIL,
                observed={
                    "evidence_version": v["evidence_version"],
                    "artifact_version": v["artifact_version"],
                },
                reason="★ 证据版本与产物版本不一致 ⇒ 引用的是旧版本证据",
            )

    #: ⑥ 可复算依据必须真的产出东西（「空 outputs」是负例）
    if not v["outputs"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"outputs": {}}, expected={"outputs": "非空"},
            reason="★ 结论没有任何计算输出 ⇒ 无复算依据",
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"claims": len(v["claims"]), "citations": len(cites)},
        reason="来源在有效表内、引用非空且全部解析、版本一致、有可复算输出",
    )
