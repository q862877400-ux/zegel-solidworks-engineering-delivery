"""★ EC11 合规与发布 —— 义务映射 / 五态判定 / 证据失效 / 四类批准分开。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC11**（★ T01–T08 逐字）
#         `specs/313-ec11-compliance-and-release/spec.md`
#         ★★ **本会话 `ks_answer` / `ks_effect_report` 的真实读数**（★ 见 `baseline.md` §二）
# 定位:   ★ **EC11** 的实现。★★★ 计划 §5 EC11 验收逐字：「★ **随机抽取义务可回溯到真实
#           证据**；★ **删除关键证据或更改工况后合规放行失效**； ★ **推荐标准不能自动成
#           为强制法律结论**」
#         ★★★ **纪律（★ 涉国标）**：★ 条款**必须来自 KS 引擎的检索**（★ 带 `doc_id`/`page`），
#           ★★ **本模块不编条款号**（★ 与 EC02 同族）。
# 官方依据: ★ 条款出处由 KS 引擎给；★ 本模块只做**映射与判定**。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 不调 KS · ★ 不调 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = [
    "ObligationKind",
    "ComplianceStatus",
    "ReleaseKind",
    "ClauseRef",
    "Obligation",
    "ComplianceMatrix",
    "ReleaseRecord",
    "STANDARD_NOT_SOFTWARE_DELEGABLE",
    "KS_VERIFIED_CLAUSES",
    "load_ks_clause",
]


#: ★★★ **法定程序不可代办**（★ 逐字承 EC11-T08：★「★ **留足实体检验/第三方/法定程序接口
#: ，
#:   ★ 不宣称软件自动代办**」）
STANDARD_NOT_SOFTWARE_DELEGABLE = (
    "★ 实体检验 / 第三方检验 / 法定程序**必须由人办**（★ 软件只留接口，★ 不代办）"
)

#: ★★★★★ **KS 实检条款登记**（★ 2026-10-10 —— ★ **全部来自本会话真调 `ks_answer` / `ks_r
#: esolve_clause`**）
#:
#: ★★★ **纪律**：★ 每条**逐字**带 KS 给的 `doc_id` / `page_start` / `clause_revision_id`
#:  /
#:   `evidence_url` —— ★★ **本仓不编条款号**（★ 铁律 5）✓
#: ★★★ **粒度实测（★ 本登记的核心价值）**：
#: · ★ 前 4 条**只回标题行**（★ `content_text` 是「4 使用与维护」那类）⇒ ★ `has_clause_b
#: ody() = False`
#:   · ★★ 后 3 条**回完整正文**（★ 含「应」）⇒ ★ `has_clause_body() = True`
#:   ⇒ ★★ **这份登记本身就是「KS 有两种粒度」的证据** ✓
KS_VERIFIED_CLAUSES: tuple = (
    #: ── ★ **只有标题行的**（★ 如实登记 —— ★ 不能据此说「核验了内容」）──
    {
        "standard_no": "GB/T 35016-2018",
        "clause_number": "5",
        "content_text": "5 使用与维护",
        "legal_status": "effective",
        "doc_id": "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR",
        "page_start": 15,
        "clause_revision_id": "clrev_01M2N54ME1GBEEKY9AY8BK0TYW",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=15",
    },
    {
        "standard_no": "GB/T 35016-2018",
        "clause_number": "4.2",
        "content_text": "4.2 调试",
        "legal_status": "effective",
        "doc_id": "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR",
        "page_start": 15,
        "clause_revision_id": "clrev_01M2N54ME1GBEEKY9AY8BK0TY2",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=15",
    },
    {
        "standard_no": "GB/T 35016-2018",
        "clause_number": "前置1",
        "content_text": "中华人民共和国国家标准\n连续搬运机械 装卸机械 安全规范\n"
        "Continuous mechanical handling equipment—Loading and unloading—Safety code\n"
        "2018-05-14 发布\n2018-12-01 实施",
        "legal_status": "effective",
        "doc_id": "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR",
        "page_start": 1,
        "clause_revision_id": "clrev_01M2N54MDMMKY9KAVVPTS4QEC0",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=1",
    },
    {
        "standard_no": "GB/T 14521-2015",
        "clause_number": "1",
        "content_text": "1 范围\n本标准规定了连续搬运机械主要类型、参数和主要装置及零部件的基本术语。\n"
        "本标准适用于输送机械、装卸机械和给料机械。",
        "legal_status": "effective",
        "doc_id": "doc_01M2MB7A58Q1AKX8J9RFH94YAB",
        "page_start": 4,
        "clause_revision_id": "clrev_01M2MB7AJ3VR39JY4QF8ANTR0G",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2MB7A58Q1AKX8J9RFH94YAB&page=4",
    },
    #: ── ★★ **有完整正文的**（★ 这才是「可据以判」的条款）──
    {
        "standard_no": "GB/T 35016-2018",
        "clause_number": "1",
        "content_text": "1 范围\n本标准规定了装卸机械的设计、制造、安装、调试、使用和维护等方面的安全要求。\n"
        "本标准适用于在港口、矿山、电厂等场合下使用的装卸机械，包括散料连续装船机、"
        "散料连续卸船机、斗轮堆取料机、排土机及回转式翻车机等设备，其他类似装卸机械可参照使用。",
        "legal_status": "effective",
        "doc_id": "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR",
        "page_start": 4,
        "clause_revision_id": "clrev_01M2N54MDMMKY9KAVVPTS4QEC6",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=4",
    },
    {
        "standard_no": "GB/T 35016-2018",
        "clause_number": "3.5.2.4.1",
        "content_text": "3.5.2.4.1 装卸机械制动器的安全系数应满足相关的设计规范的要求。",
        "legal_status": "effective",
        "modality": "应",
        "doc_id": "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR",
        "page_start": 7,
        "clause_revision_id": "clrev_01M2N54MDRE753E51YVJPNGDZV",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=7",
    },
    {
        "standard_no": "GB/T 35016-2018",
        "clause_number": "3.11.1",
        "content_text": "3.11.1 装卸机械上的所有安全标志应满足 GB 2894 及其他相关标准的要求。",
        "legal_status": "effective",
        "modality": "应",
        "doc_id": "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR",
        "page_start": 14,
        "clause_revision_id": "clrev_01M2N54ME02ZRBNCZXF5TFYP21",
        "evidence_url": "http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=14",
    },
)


def load_ks_clause(spec: dict) -> "ClauseRef":
    """★★★ **从 KS 登记项建一个 `ClauseRef`**（★ 便于判据/调用方直接用）。"""
    return ClauseRef(
        standard_no=spec["standard_no"],
        clause_number=spec["clause_number"],
        legal_status=spec.get("legal_status", ""),
        doc_id=spec.get("doc_id", ""),
        page_start=int(spec.get("page_start") or 0),
        clause_revision_id=spec.get("clause_revision_id", ""),
        evidence_url=spec.get("evidence_url", ""),
        content_text=spec.get("content_text", ""),
        modality=spec.get("modality", ""),
    )


class ObligationKind:
    """★★ **义务种类**（★ 逐字承 EC11-T03 + 承 EC02 的五类 —— ★ **复用口径**）。"""

    MANDATORY = "mandatory"  #: ★ 强制义务（★ 法规/强制性标准）
    CONTRACTUAL = "contractual"  #: ★ 合同要求
    RECOMMENDED = "recommended"  #: ★ 推荐标准（★ **GB/T 多数是这类**）
    ENTERPRISE = "enterprise"  #: ★ 企业规范
    EXPERIENCE = "experience"  #: ★ 经验规则

    ALL = (MANDATORY, CONTRACTUAL, RECOMMENDED, ENTERPRISE, EXPERIENCE)
    #: ★★★ **只有前两类能产生强制结论**（★ 与 EC02 的 `HARD` **同一口径**）
    HARD = (MANDATORY, CONTRACTUAL)


class ComplianceStatus:
    """★★★ **五态**（★ 逐字承 EC11-T03：★「★ 规定 **pass/fail/unknown/not_applicable/expired**
    ★ 的依据；★ **不适用必须有原因**」）。"""

    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"  #: ★★ **不适用必须有原因**
    EXPIRED = "expired"  #: ★ 证据过期

    ALL = (PASS, FAIL, UNKNOWN, NOT_APPLICABLE, EXPIRED)
    #: ★★★ **只有 `pass` 放行**
    RELEASING = (PASS,)
    #: ★★ **必须给原因的**（★ 逐字：「★ 不适用必须有原因」）
    REQUIRES_REASON = (NOT_APPLICABLE, UNKNOWN, FAIL, EXPIRED)


class ReleaseKind:
    """★★★ **四类批准**（★ 逐字承 EC11-T06：★「★ 区分**软件包发布、CAD 工件完成、
    设计审签、整机符合性**，★ **不共用一个 approve 字段**」）。"""

    SOFTWARE_RELEASE = "software_release"  #: ★ 软件包发布
    CAD_ARTIFACT_DONE = "cad_artifact_done"  #: ★ CAD 工件完成
    DESIGN_SIGNOFF = "design_signoff"  #: ★ 设计审签
    MACHINE_CONFORMITY = "machine_conformity"  #: ★ 整机符合性

    ALL = (SOFTWARE_RELEASE, CAD_ARTIFACT_DONE, DESIGN_SIGNOFF, MACHINE_CONFORMITY)


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ 条款引用与义务（★ EC11-T01/T02）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ClauseRef:
    """★★★★ **条款引用**（★ **必须来自 KS 引擎** —— ★ 带 `doc_id`/`page`/`evidence_url`）。

    ★★★ **纪律**：★ 本模块**不编条款号** —— ★ 每个 `ClauseRef` 都要有 **KS 给的定位**
      （★ `doc_id` + `page_start` + `clause_revision_id`）✓
    """

    standard_no: str
    clause_number: str
    legal_status: str = ""  #: ★ 效力（★ 与 KS 的四色对齐）
    doc_id: str = ""  #: ★★ **KS 的文档 id**
    page_start: int = 0  #: ★★ **KS 的页码**
    clause_revision_id: str = ""  #: ★★ **KS 的条款修订 id**
    evidence_url: str = ""  #: ★★ **KS 给的原文链接**
    #: ★★★ **KS 返回的正文**（★ 空/只有标题 ⇒ **不等于核验过条款内容**）
    content_text: str = ""
    #: ★★ **情态动词**（★ KS 的 `modality` —— ★ 「应」= 强制 · 「可」= 可选）
    modality: str = ""

    #: ★★★ **标题行**的判据阈值（★ KS 对只有标题的条款就回那个短串）
    _HEADING_ONLY_MAX = 24

    def is_traceable(self) -> bool:
        """★★★★ **可回溯**（★ 逐字承验收：★「★ **随机抽取义务可回溯到真实证据**」）。

        ★★ 判据：★ **必须有 KS 的定位**（★ `doc_id` + `page_start` > 0）。
        """
        return (
            bool(self.standard_no)
            and bool(self.clause_number)
            and bool(self.doc_id)
            and int(self.page_start) > 0
        )

    def has_clause_body(self) -> bool:
        """★★★★★ **是不是拿到了**条款正文****（★ 2026-10-10 补 —— ★ **实测驱动**的判据）。

        ★★★ **为什么要有它**：★ 本会话实调 `ks_resolve_clause` / `ks_answer` 发现
          **KS 库里有两种粒度**：
          · ★ 只有**标题行**（★ 如 `GB/T 35016-2018` 的 `4.2` ⇒ 正文只有「4.2 调试」）✗
          · ★★ 有**完整正文**（★ 如 `3.5.2.4.1` ⇒ 「装卸机械制动器的安全系数**应**满足
            相关的设计规范的要求。」）✓
        ★★ **⇒ 只引到标题行**不能**说「核验了条款内容」** —— ★ 那是本判据要挡的 ✓
        """
        txt = str(self.content_text or "").strip()
        if not txt:
            return False
        #: ★ 去掉开头的条款号（★ 如 `4.2 ` / `3.5.2.4.1 `）
        body = txt
        if self.clause_number and body.startswith(self.clause_number):
            body = body[len(self.clause_number) :].strip()
        if len(body) <= self._HEADING_ONLY_MAX:
            return False
        #: ★★ **要有实质内容**（★ 含要求/情态词 —— ★ 纯标题不会含）
        markers = ("应", "不应", "宜", "必须", "不得", "符合", "满足", "规定", "要求")
        return any(m in body for m in markers)

    def locator(self) -> str:
        """★ 可点的定位（★ `标准号 条款号 @ doc_id:page`）。"""
        return "%s %s @ %s:%s" % (
            self.standard_no,
            self.clause_number,
            self.doc_id,
            self.page_start,
        )


@dataclass
class Obligation:
    """★★★★ **一条义务**（★ 逐字承 EC11-T02）：

    「★ **要求 → 条款 → 模型/计算/测试/审查义务 → 证据 → 结论** 映射」。
    """

    id: str
    requirement: str  #: ★ 要求
    clause: ClauseRef  #: ★ 条款
    kind: str = ObligationKind.RECOMMENDED
    verification_kind: str = ""  #: ★ 模型/计算/测试/审查
    evidence_refs: list = field(default_factory=list)
    status: str = ComplianceStatus.UNKNOWN
    reason: str = ""  #: ★★ **不适用/未知/失败/过期必须给原因**
    #: ★★ **工况**（★ 验收：★「★ **更改工况后合规放行失效**」）
    load_case: str = ""

    def verdict(self) -> dict:
        """★★★★★ **单条判定**（★ 五态 + ★ **理由齐全性**）。

        ★★★ **三条硬判据**：
          · ★ **`not_applicable`/`unknown`/`fail`/`expired` ⇒ 必须给 `reason`**（★ T03 逐字）
          · ★★ **`pass` 必须有证据**（★ 否则那是**空口**）
          · ★★★ **推荐标准不得给「强制」结论**（★ 验收逐字）
        """
        problems = []
        #: ★ ① 要原因的四态
        if (
            self.status in ComplianceStatus.REQUIRES_REASON
            and not str(self.reason).strip()
        ):
            problems.append(
                "★★ 状态 %r **没给原因**（★ EC11-T03 逐字：不适用必须有原因）"
                % self.status
            )
        #: ★★ ② `pass` 要有证据
        if self.status == ComplianceStatus.PASS and not self.evidence_refs:
            problems.append(
                "★★★ `pass` 但**没有证据** ⇒ ★ 那是空口（★ 验收：可回溯到真实证据）"
            )
        #: ★★ ③ 条款要可回溯
        if not self.clause.is_traceable():
            problems.append("★★ 条款**不可回溯**（★ 缺 KS 定位）")
        #: ★★★ ③b **`pass` 的条款必须有**正文****（★ 2026-10-10 补 —— ★ 实测驱动的判据）
        #:   ★★ 依据：★ KS 库里有些条款**只回标题行**（★ 如 `4.2 调试`）⇒
        #:     ★ 只引到标题**不能**说「核验了条款内容」✗（★ 与 EC11-T08 的「不宣称」同族）
        if self.status == ComplianceStatus.PASS and not self.clause.has_clause_body():
            problems.append(
                "★★★ `pass` 但条款**只有标题行**（★ 没拿到正文）⇒ "
                "★ 不能说「已核验条款内容」"
            )
        #: ★★★ ④ **推荐标准不能出强制结论**
        #:   ⚠ 第一版直接查 `"强制" in reason` ⇒ ★★ **把「★ 非强制」也当成违规** ✗
        #:     （★ 本判据自己抓出来的）⇒ ★ 现要求**肯定式**的强制措辞。
        if (
            self.kind == ObligationKind.RECOMMENDED
            and self.status == ComplianceStatus.FAIL
        ):
            r = str(self.reason)
            #: ★★ **肯定式的强制措辞**（★ 排除「非强制」/「不是强制」这类否定）
            says_mandatory = bool(
                re.search(
                    r"(?<!非)(?<!不是)(?<!不算)\*{0,2}强制\*{0,2}(?:不合格|不符合|性要求|结论)",
                    r,
                )
                or re.search(r"(?<!非)(?<!不是)必须(?:强制)?(?:满足|符合)", r)
            )
            if says_mandatory:
                problems.append("★★★ 推荐标准给了「**强制**」结论 ⇒ ★ 验收逐字禁止")
        return {
            "ok": not problems,
            "problems": problems,
            "status": self.status,
            "kind": self.kind,
            "releasing": self.status in ComplianceStatus.RELEASING,
            "locator": self.clause.locator(),
            "reason": (
                "★ %s：%s" % (self.id, self.status)
                if not problems
                else "★★ %s 有问题：%s" % (self.id, problems)
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 合规矩阵（★ EC11-T02/T04）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ComplianceMatrix:
    """★★★★ **合规矩阵**（★ 逐字承 EC11-T02/T04）。

    ★★★ **验收（★ 逐字）**：★「★ **删除关键证据或更改工况后合规放行失效**」。
    """

    obligations: list = field(default_factory=list)
    #: ★★ **冻结的工况**（★ 改了就失效 —— ★ 验收逐字）
    frozen_load_case: str = ""

    def add(self, ob: Obligation) -> None:
        self.obligations.append(ob)

    def random_sample_traceability(self, indexes: list) -> dict:
        """★★★★ **随机抽取义务可回溯到真实证据**（★ 验收逐字）。

        ★★ 判据：★ 抽到的每条都要 ① **条款可回溯**（★ KS 定位）② **状态合法**
          ③ **`pass` 有证据**。
        """
        picked = []
        bad = []
        for i in indexes or []:
            if not (0 <= i < len(self.obligations)):
                bad.append({"index": i, "reason": "★★ 索引越界"})
                continue
            ob = self.obligations[i]
            v = ob.verdict()
            picked.append(
                {
                    "id": ob.id,
                    "status": ob.status,
                    "locator": ob.clause.locator(),
                    "evidence_refs": list(ob.evidence_refs),
                    "ok": v["ok"],
                }
            )
            if not v["ok"]:
                bad.append({"index": i, "id": ob.id, "problems": v["problems"]})
        return {
            "ok": bool(picked) and not bad,
            "sampled": picked,
            "bad": bad,
            "reason": (
                "★ %d 条抽样全部可回溯" % len(picked)
                if picked and not bad
                else "★★ %d 条抽样有问题" % len(bad)
            ),
        }

    def verdict(self) -> dict:
        """★★★★★ **总判定**（★ 三条验收合成）。

        ★★ 放行条件（★ 逐字承 EC11-T04：★「★ **关键义务未知或失败时阻断工程合规发布**」）：
          · ★ 每条**硬义务**（★ `MANDATORY`/`CONTRACTUAL`）状态必须 **`pass`**
          · ★★ **有 `unknown`/`fail`/`expired` 的硬义务 ⇒ 阻断**
          · ★ 每条**都要**条款可回溯
        """
        results = [(ob, ob.verdict()) for ob in self.obligations]
        broken = [
            {"id": ob.id, "problems": v["problems"]} for ob, v in results if not v["ok"]
        ]
        hard_blocking = [
            ob.id
            for ob, _v in results
            if ob.kind in ObligationKind.HARD
            and ob.status
            in (
                ComplianceStatus.UNKNOWN,
                ComplianceStatus.FAIL,
                ComplianceStatus.EXPIRED,
            )
        ]
        #: ★★ **工况一致性**（★ 改工况 ⇒ 失效）
        case_mismatch = [
            ob.id
            for ob, _v in results
            if self.frozen_load_case
            and ob.load_case
            and ob.load_case != self.frozen_load_case
        ]
        ok = bool(results) and not broken and not hard_blocking and not case_mismatch
        return {
            "ok": ok,
            "blocking": hard_blocking,
            "broken": broken,
            "load_case_mismatch": case_mismatch,
            "frozen_load_case": self.frozen_load_case,
            "releasing": ok,
            "reason": (
                "★ 全部 %d 条义务通过且可回溯 ⇒ 合规放行" % len(results)
                if ok
                else "★★ 阻断：★ 硬义务未过 %r / ★ 有问题 %d 条 / ★ 工况不符 %r"
                % (hard_blocking, len(broken), case_mismatch)
            ),
        }

    def invalidate_on_evidence_removal(self, removed_ref: str) -> dict:
        """★★★★★ **删除关键证据 ⇒ 合规放行失效**（★ 验收逐字）。

        ★★ 判据：★ 把该证据从义务里摘掉 ⇒ ★ 原来 `pass` 的**变 `unknown`**（★ 因为没证据了）。
        """
        affected = []
        for ob in self.obligations:
            if removed_ref in (ob.evidence_refs or []):
                ob.evidence_refs = [r for r in ob.evidence_refs if r != removed_ref]
                if ob.status == ComplianceStatus.PASS and not ob.evidence_refs:
                    ob.status = ComplianceStatus.UNKNOWN
                    ob.reason = "★★ 关键证据 %r 被删 ⇒ 降为 unknown" % removed_ref
                affected.append(ob.id)
        v = self.verdict()
        return {
            "affected": affected,
            "still_releasing": v["releasing"],
            "verdict": v,
            "reason": (
                "★ 摘掉 %r ⇒ 影响 %d 条；★ 放行=%s"
                % (removed_ref, len(affected), v["releasing"])
            ),
        }


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ 四类批准（★ EC11-T06）
# ══════════════════════════════════════════════════════════════════════


@dataclass
class ReleaseRecord:
    """★★★★ **发布记录**（★ 逐字承 EC11-T06：★「★ 区分软件包发布、CAD 工件完成、
    设计审签、整机符合性，★ **不共用一个 approve 字段**」）。

    ★★★ **本类的意义**：★ 四类**各有一个** `approved` ——
      ★★ 「软件包发了」**不等于**「整机符合性过了」✗
    """

    software_release: bool = False
    cad_artifact_done: bool = False
    design_signoff: bool = False
    machine_conformity: bool = False
    #: ★★ **四类的批准人**（★ 分开 —— ★ 不能一个人签四类）
    approvers: dict = field(default_factory=dict)

    def all_four_are_separate(self) -> dict:
        """★★★ **四类必须各有一个字段**（★ 不能共用一个）。"""
        fields = (
            "software_release",
            "cad_artifact_done",
            "design_signoff",
            "machine_conformity",
        )
        present = [f for f in fields if hasattr(self, f)]
        return {
            "ok": len(present) == 4,
            "fields": present,
            "reason": "★ 四类各一个字段"
            if len(present) == 4
            else "★★ 缺 %r" % [f for f in fields if f not in present],
        }

    def may_claim_machine_conformity(self) -> dict:
        """★★★★★ **能不能声称「整机符合性」**（★ 逐字承 EC11-T08）。

        ★★★ **判据**：★ 整机符合性**需要法定程序/实体检验** ⇒
          ★★ **软件**不能**自己把它置 `True`** —— ★ 必须有**人工批准记录** ✓
        """
        who = str(self.approvers.get(ReleaseKind.MACHINE_CONFORMITY) or "").strip()
        if not self.machine_conformity:
            return {
                "ok": False,
                "claim_allowed": False,
                "reason": "★★ 整机符合性未通过",
            }
        if not who:
            return {
                "ok": False,
                "claim_allowed": False,
                "reason": "★★★ 整机符合性置了 `True` 但**没有批准人** ⇒ ★ "
                "那是**软件自签**（★ 违反 EC11-T08）",
            }
        return {
            "ok": True,
            "claim_allowed": True,
            "approver": who,
            "note": STANDARD_NOT_SOFTWARE_DELEGABLE,
        }

    def verdict(self) -> dict:
        """★★★ **四类**分别**报告**（★ 不合成一个 approve）。"""
        sep = self.all_four_are_separate()
        return {
            "ok": sep["ok"],
            "software_release": self.software_release,
            "cad_artifact_done": self.cad_artifact_done,
            "design_signoff": self.design_signoff,
            "machine_conformity": self.machine_conformity,
            "machine_conformity_claim": self.may_claim_machine_conformity(),
            "note": STANDARD_NOT_SOFTWARE_DELEGABLE,
            "reason": "★ 四类分字段报告（★ 不共用一个 approve）"
            if sep["ok"]
            else sep["reason"],
        }
