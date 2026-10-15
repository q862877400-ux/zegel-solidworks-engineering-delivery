"""★ EC11 判据 —— 义务可回溯 / 五态 / 证据失效 / 四类批准分开。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/compliance.py`（★ EC11 的实现）
#         `specs/313-ec11-compliance-and-release/spec.md`
#         ★★ **本会话 `ks_answer` 的真实条款**（★ 见 `baseline.md` §二 —— ★ 条款号**来自 KS**）
# 定位:   ★ EC11 的判据（★ 逐字承计划 §5 EC11 的「验收」）。
# 官方依据: ★ 判据里用的标准号/条款/`doc_id` **全部来自本会话 `ks_answer` 的真实读数**。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不调 KS · ★ 不调 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest

from engineering import compliance as C

#: ★★★ **本会话 `ks_answer` 的真实条款**（★ 逐字 —— ★ 不是编的）
#:   ★★ 2026-10-10 补 `content_text`：★ 本判据新增了「★ **`pass` 的条款必须有正文**」
#:     （★ 因为 KS 库里有些条款**只回标题行**）⇒ ★ 夹具要带**真正文** ✓
KS_GB_T_35016 = dict(
    standard_no="GB/T 35016-2018", clause_number="3.5.2.4.1",
    legal_status="effective",
    doc_id="doc_01M2N54M9KCJNJQ3ZBZVZRAYQR", page_start=7,
    clause_revision_id="clrev_01M2N54MDRE753E51YVJPNGDZV",
    evidence_url="http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2N54M9KCJNJQ3ZBZVZRAYQR&page=7",
    #: ★★ **KS 回的**完整正文****（★ 含「应」—— ★ 这才是可据以判的条款）
    content_text="3.5.2.4.1 装卸机械制动器的安全系数应满足相关的设计规范的要求。",
    modality="应")
KS_GB_T_20850 = dict(
    standard_no="GB/T 20850-2025", clause_number="附录A",
    legal_status="effective",
    doc_id="doc_01M2MDJNCQKSXM4ER1DRBVADQ5", page_start=37,
    clause_revision_id="clrev_01M2MDJNF1AHPP9JPCXFKAXFP5",
    evidence_url="http://127.0.0.1:1/__ks_evidence__?doc=doc_01M2MDJNCQKSXM4ER1DRBVADQ5&page=37",
    content_text="附录A（资料性）机械安全国家标准以及国际标准与欧盟相关技术法规的关系。"
                 "正确理解这些关系有助于出口企业正确加贴 CE 标志。")


def _ref(**kw) -> C.ClauseRef:
    base = dict(KS_GB_T_35016)
    base.update(kw)
    return C.ClauseRef(**base)


def _ob(**kw) -> C.Obligation:
    base = dict(id="OB-1", requirement="★ 直线搬运单元的安全规范适用性",
                clause=_ref(), kind=C.ObligationKind.MANDATORY,
                verification_kind="★ 审查", evidence_refs=["★ KS 原文 p1"],
                status=C.ComplianceStatus.PASS, load_case="★ 正常循环")
    base.update(kw)
    return C.Obligation(**base)


# ══════════════════════════════════════════════════════════════════════
# V1 · 义务可回溯到真实证据
# ══════════════════════════════════════════════════════════════════════

def test_v1_clause_needs_ks_locator():
    """★★★★★ V1：★ **条款必须带 KS 定位**（★ 验收逐字：「★ **可回溯到真实证据**」）。

    ★★ 判据：★ 缺 `doc_id` 或 `page_start` ⇒ ★ **不可回溯** ⇒ ★ 那是**编的条款** ✗
    """
    assert _ref().is_traceable() is True, "★ 真实条款被误判不可回溯"
    #: ★★ 缺 doc_id
    assert _ref(doc_id="").is_traceable() is False, "★★ 没有 KS 的 doc_id 却判可回溯"
    #: ★★ 缺页码
    assert _ref(page_start=0).is_traceable() is False, "★★ 没有页码却判可回溯"
    #: ★★ 缺标准号/条款号
    assert _ref(standard_no="").is_traceable() is False
    assert _ref(clause_number="").is_traceable() is False


def test_v1_locator_is_readable():
    """★★ V1：★ **定位要可读**（★ `标准号 条款号 @ doc_id:page`）。"""
    loc = _ref().locator()
    assert "GB/T 35016-2018" in loc and "3.5.2.4.1" in loc
    assert "doc_01M2N54M9KCJNJQ3ZBZVZRAYQR:7" in loc, "★ 定位里缺 doc:page"


def test_v1_pass_without_evidence_is_rejected():
    """★★★★★ V1：★ **`pass` 但没证据 ⇒ 拒**（★ 那是空口）。"""
    ob = _ob(evidence_refs=[])
    out = ob.verdict()
    assert out["ok"] is False, "★★ `pass` 没证据却判 ok"
    assert any("空口" in p for p in out["problems"]), "★ 没点明「空口」"


def test_v1_obligation_without_traceable_clause_is_rejected():
    """★★★★ V1：★ **条款不可回溯 ⇒ 拒**（★ 那是「编了一个条款」）。"""
    ob = _ob(clause=_ref(doc_id="", page_start=0))
    out = ob.verdict()
    assert out["ok"] is False, "★★ 编的条款却判 ok"
    assert any("不可回溯" in p for p in out["problems"])


def test_v1_random_sample_traceability():
    """★★★★ V1：★ **随机抽样可回溯**（★ 验收逐字的动作）。"""
    m = C.ComplianceMatrix(frozen_load_case="★ 正常循环")
    m.add(_ob(id="A"))
    m.add(_ob(id="B", clause=_ref(**KS_GB_T_20850),
              kind=C.ObligationKind.RECOMMENDED, status=C.ComplianceStatus.NOT_APPLICABLE,
              reason="★ 该单元不涉及该附录的适用域"))
    out = m.random_sample_traceability([0, 1])
    assert out["ok"] is True, "★ 两条真实义务却判不可回溯：%r" % out
    assert len(out["sampled"]) == 2
    #: ★★ **抽到坏的 ⇒ 报出来**
    m.add(_ob(id="C", evidence_refs=[]))
    bad = m.random_sample_traceability([2])
    assert bad["ok"] is False, "★★ 抽到没证据的义务却判 ok"
    assert bad["bad"][0]["id"] == "C"


# ══════════════════════════════════════════════════════════════════════
# V2 · 五态与理由
# ══════════════════════════════════════════════════════════════════════

def test_v2_five_statuses_exist():
    """★★★ V2：★ **五态必须齐**（★ 逐字承 EC11-T03）。"""
    assert set(C.ComplianceStatus.ALL) == {
        "pass", "fail", "unknown", "not_applicable", "expired"}, (
        "★ 五态不齐：%r" % (C.ComplianceStatus.ALL,))
    #: ★★ 只有 pass 放行
    assert C.ComplianceStatus.RELEASING == ("pass",)


@pytest.mark.parametrize("status", ["not_applicable", "unknown", "fail", "expired"])
def test_v2_reason_is_mandatory_for_four_statuses(status):
    """★★★★★ V2：★ **不适用/未知/失败/过期 ⇒ 必须给原因**（★ 逐字：「★ 不适用必须有原因」）。"""
    ob = _ob(status=status, reason="")
    out = ob.verdict()
    assert out["ok"] is False, "★★ 状态 %r 没给原因却判 ok" % status
    assert any("没给原因" in p for p in out["problems"])


def test_v2_reason_supplied_passes_the_check():
    """★★ V2 负例：★ **给了原因 ⇒ 该项检查过**（★ 不是一律拒）。"""
    ob = _ob(status=C.ComplianceStatus.NOT_APPLICABLE,
             reason="★ 本单元不涉及该条款的适用设备类别")
    out = ob.verdict()
    assert out["ok"] is True, "★ 给了原因却判失败：%r" % out
    assert out["releasing"] is False, "★ `not_applicable` **不该放行**"


# ══════════════════════════════════════════════════════════════════════
# V3 · 推荐标准不能自动成为强制法律结论
# ══════════════════════════════════════════════════════════════════════

def test_v3_obligation_kinds_match_ec02():
    """★★★ V3：★ **五类义务与 EC02 同一口径**（★ 铁律 1 —— ★ 不另建一套）。"""
    from engineering import rules as R
    assert set(C.ObligationKind.ALL) == set(R.ObligationKind.ALL), (
        "★★ EC11 与 EC02 的义务分类不一致 ⇒ ★ 两处各建了一套")
    assert tuple(C.ObligationKind.HARD) == tuple(R.ObligationKind.HARD), (
        "★★ 「硬义务」的口径不一致")


def test_v3_recommended_standard_cannot_claim_mandatory():
    """★★★★★ V3：★ **推荐标准不能自动成为强制法律结论**（★ 验收逐字）。

    ★★ 判据：★ `RECOMMENDED` 的义务**不许**给出带「强制」字样的失败结论 ✗
    """
    ob = _ob(kind=C.ObligationKind.RECOMMENDED, status=C.ComplianceStatus.FAIL,
             reason="★★ 不满足该要求 ⇒ **强制**不合格")
    out = ob.verdict()
    assert out["ok"] is False, (
        "★★★ 推荐标准给出了「强制」结论却判 ok ⇒ ★ 违反验收")
    assert any("强制" in p for p in out["problems"])


def test_v3_recommended_with_neutral_reason_is_fine():
    """★★ V3 负例：★ **推荐标准的**中性**结论 ⇒ 允许**。"""
    ob = _ob(kind=C.ObligationKind.RECOMMENDED, status=C.ComplianceStatus.FAIL,
             reason="★ 未满足该推荐要求 ⇒ 记为偏差（★ 非强制）")
    out = ob.verdict()
    assert out["ok"] is True, "★ 中性措辞却判失败：%r" % out


def test_v3_recommended_does_not_block_release():
    """★★★★ V3：★ **推荐标准未过**不阻断放行**（★ 它不是强制）。"""
    m = C.ComplianceMatrix(frozen_load_case="★ 正常循环")
    m.add(_ob(id="M1", kind=C.ObligationKind.MANDATORY, status=C.ComplianceStatus.PASS))
    m.add(_ob(id="R1", kind=C.ObligationKind.RECOMMENDED, status=C.ComplianceStatus.FAIL,
              reason="★ 未满足推荐值"))
    out = m.verdict()
    assert out["ok"] is True, (
        "★★ 推荐标准未过就阻断了放行 ⇒ ★ 把推荐当成了强制：%r" % out)
    assert out["blocking"] == []


def test_v3_mandatory_failure_blocks_release():
    """★★★★ V3：★ **强制义务未过 ⇒ 阻断**（★ 逐字承 EC11-T04）。"""
    m = C.ComplianceMatrix(frozen_load_case="★ 正常循环")
    m.add(_ob(id="M1", kind=C.ObligationKind.MANDATORY, status=C.ComplianceStatus.PASS))
    m.add(_ob(id="M2", kind=C.ObligationKind.MANDATORY, status=C.ComplianceStatus.UNKNOWN,
              reason="★ 缺第三方检验报告"))
    out = m.verdict()
    assert out["ok"] is False, "★★ 强制义务 unknown 却放行"
    assert out["blocking"] == ["M2"]


# ══════════════════════════════════════════════════════════════════════
# V4 · 删除证据 / 改工况 ⇒ 失效
# ══════════════════════════════════════════════════════════════════════

def test_v4_removing_evidence_invalidates_release():
    """★★★★★ V4：★ **删除关键证据 ⇒ 合规放行失效**（★ 验收逐字）。"""
    m = C.ComplianceMatrix(frozen_load_case="★ 正常循环")
    m.add(_ob(id="M1", evidence_refs=["★ KS 原文 p1"]))
    assert m.verdict()["ok"] is True, "★ 前置：该放行"
    out = m.invalidate_on_evidence_removal("★ KS 原文 p1")
    assert out["affected"] == ["M1"], "★ 没找到受影响的义务"
    assert out["still_releasing"] is False, (
        "★★★ 删了关键证据却**仍放行** ⇒ ★ 违反验收")
    #: ★★ 状态应降为 unknown（★ 因为没证据了）
    assert m.obligations[0].status == C.ComplianceStatus.UNKNOWN


def test_v4_changing_load_case_invalidates_release():
    """★★★★★ V4：★ **更改工况 ⇒ 合规放行失效**（★ 验收逐字）。"""
    m = C.ComplianceMatrix(frozen_load_case="★ 正常循环")
    m.add(_ob(id="M1", load_case="★ 正常循环"))
    assert m.verdict()["ok"] is True, "★ 前置：该放行"
    #: ★★ **改工况**（★ 把某条义务的工况换成别的）
    m.obligations[0].load_case = "★ 冲击工况"
    out = m.verdict()
    assert out["ok"] is False, "★★★ 改了工况却仍放行 ⇒ ★ 违反验收"
    assert out["load_case_mismatch"] == ["M1"]


def test_v4_no_obligations_is_not_a_pass():
    """★★ V4：★ **一条义务都没有 ⇒ 不算放行**（★ 不能「没义务=合规」）。"""
    out = C.ComplianceMatrix(frozen_load_case="★ 正常循环").verdict()
    assert out["ok"] is False, "★★ 空矩阵被判放行"


# ══════════════════════════════════════════════════════════════════════
# V5 · 四类批准分开
# ══════════════════════════════════════════════════════════════════════

def test_v5_four_release_kinds_exist():
    """★★★ V5：★ **四类批准必须齐**（★ 逐字承 EC11-T06）。"""
    assert set(C.ReleaseKind.ALL) == {
        "software_release", "cad_artifact_done",
        "design_signoff", "machine_conformity"}, (
        "★ 四类不齐：%r" % (C.ReleaseKind.ALL,))


def test_v5_four_fields_are_separate():
    """★★★★ V5：★ **四类各一个字段，不共用一个 approve**（★ 逐字承 EC11-T06）。"""
    r = C.ReleaseRecord()
    out = r.all_four_are_separate()
    assert out["ok"] is True, "★ 四类没分开：%r" % out
    assert len(out["fields"]) == 4


def test_v5_machine_conformity_needs_a_human_approver():
    """★★★★★ V5：★ **整机符合性不能由软件自签**（★ 逐字承 EC11-T08：

    「★ **留足实体检验/第三方/法定程序接口，不宣称软件自动代办**」）。
    """
    r = C.ReleaseRecord(machine_conformity=True)
    out = r.may_claim_machine_conformity()
    assert out["claim_allowed"] is False, (
        "★★★ 整机符合性置了 True 却没批准人 ⇒ ★ 那是**软件自签**（★ 违反 EC11-T08）")
    assert "软件自签" in out["reason"]
    #: ★★ **有人签 ⇒ 允许**
    r2 = C.ReleaseRecord(machine_conformity=True,
                         approvers={C.ReleaseKind.MACHINE_CONFORMITY: "★ 第三方检验机构 X"})
    out2 = r2.may_claim_machine_conformity()
    assert out2["claim_allowed"] is True
    assert out2["approver"] == "★ 第三方检验机构 X"


def test_v5_software_release_does_not_imply_machine_conformity():
    """★★★★ V5：★ **软件包发了 ≠ 整机符合性过了**（★ 四类分开的意义）。"""
    r = C.ReleaseRecord(software_release=True, cad_artifact_done=True)
    out = r.verdict()
    assert out["software_release"] is True
    assert out["machine_conformity"] is False, (
        "★★ 软件包发布被当成了整机符合性 ⇒ ★ 四类没真正分开")
    assert out["machine_conformity_claim"]["claim_allowed"] is False


def test_v5_not_software_delegable_statement_exists():
    """★★★★ V5：★ **「法定程序不可代办」必须落成常量**（★ 逐字承 EC11-T08）。"""
    s = C.STANDARD_NOT_SOFTWARE_DELEGABLE
    assert "必须由人办" in s, "★★ 没写明「必须由人办」"
    assert "不代办" in s, "★★ 没写明「不代办」"
