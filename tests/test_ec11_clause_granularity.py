"""★ EC11 补判据 —— **KS 条款的两种粒度**（★ 2026-10-10 实测驱动）。

★★★ **为什么要有它**：★ 本会话实调 `ks_resolve_clause` / `ks_answer` 发现
  **KS 库里同一部标准有两种粒度**：
  · ★ 有些条款**只回标题行**（★ `GB/T 35016-2018` 的 `4.2` ⇒ 正文只有「4.2 调试」）
  · ★★ 有些条款**回完整正文**（★ `3.5.2.4.1` ⇒ 「…安全系数**应**满足相关的设计规范的要求。」）
★★★ **⇒ 只引到标题行不能说「核验了条款内容」** —— ★ 那是本判据要挡的 ✗
★ 与 EC11-T08 同族：★「★ **不宣称软件自动代办**」—— ★ 也不该**宣称核验了没读到的内容** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/compliance.py`（★ `ClauseRef.has_clause_body` ·
#           `KS_VERIFIED_CLAUSES` · `load_ks_clause`）
#         `specs/313-ec11-compliance-and-release/spec.md`
# 定位:   ★ 守卫「条款正文」这条 —— ★ 输入**全部来自本会话真调 KS 的读数**。
# 官方依据: ★ KS 引擎（本机 KnowledgeStation）—— ★ 条款逐字来自它
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不调 KS）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import compliance as C


def test_heading_only_clause_is_not_a_body():
    """★★★★★ **只有标题行 ⇒ 不算拿到正文**（★ 逐字承 EC11-T08 的精神：★ 不宣称）。

    ★★ 依据：★ `ks_resolve_clause("GB/T 35016-2018", "4.2")` 真机回
      `content_text = "4.2 调试"` ⇒ ★ **那只是一个标题** ✗
    """
    ref = C.ClauseRef(standard_no="GB/T 35016-2018", clause_number="4.2",
                      doc_id="doc_x", page_start=15, content_text="4.2 调试")
    assert ref.is_traceable() is True, "★ 它有 KS 定位 ⇒ 可回溯"
    assert ref.has_clause_body() is False, (
        "★★★ 「4.2 调试」被当成了**条款正文** ⇒ ★ 会让人以为核验过内容")


def test_empty_content_is_not_a_body():
    """★★ 空正文 ⇒ 不算（★ 连标题都没有）。"""
    ref = C.ClauseRef(standard_no="X", clause_number="1", doc_id="d", page_start=1,
                      content_text="")
    assert ref.has_clause_body() is False


def test_real_clause_body_is_accepted():
    """★★★★★ **有完整正文 ⇒ 算拿到**（★ 含「应」这类要求词）。

    ★★ 依据：★ `ks_answer` 真机回 `3.5.2.4.1` 的**完整正文**：
      「★ 装卸机械制动器的安全系数**应**满足相关的设计规范的要求。」
    """
    ref = C.ClauseRef(
        standard_no="GB/T 35016-2018", clause_number="3.5.2.4.1", doc_id="doc_x",
        page_start=7, modality="应",
        content_text="3.5.2.4.1 装卸机械制动器的安全系数应满足相关的设计规范的要求。")
    assert ref.has_clause_body() is True, "★★ 真正文被拒了"


def test_pass_with_heading_only_clause_is_rejected():
    """★★★★★ **`pass` 但条款只有标题 ⇒ 拒**（★ 本判据的核心）。

    ★★ 判据：★ `pass` 是**结论** ⇒ ★ 它**必须**建立在**读到的条款正文**上 ——
      ★★ 只有标题 ⇒ ★ 那是**没读内容就下结论** ✗
    """
    ref = C.ClauseRef(standard_no="GB/T 35016-2018", clause_number="4.2",
                      doc_id="doc_x", page_start=15, content_text="4.2 调试")
    ob = C.Obligation(id="OB-1", requirement="★ 调试安全", clause=ref,
                      kind=C.ObligationKind.MANDATORY,
                      evidence_refs=["★ 有证据"], status=C.ComplianceStatus.PASS)
    out = ob.verdict()
    assert out["ok"] is False, (
        "★★★ `pass` 建立在**只有标题**的条款上却判 ok ⇒ ★ 那是「没读内容就下结论」")
    assert any("只有标题行" in p for p in out["problems"])


def test_pass_with_real_body_is_accepted():
    """★★ 负例：★ **有正文 ⇒ `pass` 可接受**（★ 不是一律拒）。"""
    ref = C.ClauseRef(
        standard_no="GB/T 35016-2018", clause_number="3.5.2.4.1", doc_id="doc_x",
        page_start=7,
        content_text="3.5.2.4.1 装卸机械制动器的安全系数应满足相关的设计规范的要求。")
    ob = C.Obligation(id="OB-1", requirement="★ 制动器安全系数", clause=ref,
                      kind=C.ObligationKind.MANDATORY,
                      evidence_refs=["★ 计算书"], status=C.ComplianceStatus.PASS)
    assert ob.verdict()["ok"] is True, "★ 有正文却判失败：%r" % ob.verdict()


def test_ks_registry_carries_both_granularities():
    """★★★★★ **KS 登记**必须**如实**包含两种粒度（★ 那是本判据的实证基础）。

    ★★ 依据：★ 本会话真调 KS 得 7 条 —— ★ 其中**有**只有标题的、**也有**有正文的。
      ★★ 登记若**只留**有正文的 ⇒ ★ 那是**选择性登记**（★ 隐藏了库的局限）✗
    """
    reg = C.KS_VERIFIED_CLAUSES
    assert len(reg) >= 5, "★ 登记条数太少：%d" % len(reg)
    refs = [C.load_ks_clause(x) for x in reg]
    with_body = [r for r in refs if r.has_clause_body()]
    heading_only = [r for r in refs if not r.has_clause_body()]
    assert with_body, "★★ 登记里没有一条**有正文**的 ⇒ 判不了 pass"
    assert heading_only, (
        "★★★ 登记里没有**只有标题**的 ⇒ ★ 那是**选择性登记**，★ 掩盖了 KS 库的粒度局限")
    #: ★★ 每一条都要**可回溯**（★ KS 定位齐）
    for r in refs:
        assert r.is_traceable(), "★★ %s 不可回溯" % r.locator()
        assert r.clause_revision_id, "★★ %s 缺 KS 的 clause_revision_id" % r.locator()


def test_ks_registry_clauses_are_verbatim_from_ks():
    """★★★★ **登记里的条款逐字来自 KS**（★ 抽查两条的正文 —— ★ 防手改）。

    ★★ 抽查：★ `3.5.2.4.1` 的「**应**满足相关的设计规范的要求」与
      ★ `3.11.1` 的「**应**满足 GB 2894」 —— ★ 这两条是本会话真读数 ✓
    """
    by_no = {C.load_ks_clause(x).clause_number: C.load_ks_clause(x)
             for x in C.KS_VERIFIED_CLAUSES}
    assert "3.5.2.4.1" in by_no and "3.11.1" in by_no, (
        "★★ 缺本会话真读到的条款：%r" % sorted(by_no))
    assert "应满足相关的设计规范的要求" in by_no["3.5.2.4.1"].content_text
    assert "应满足 GB 2894" in by_no["3.11.1"].content_text
    #: ★★ 情态是「应」（★ 强制强度 3 —— ★ 不是「可」）
    assert by_no["3.5.2.4.1"].modality == "应", "★★ 情态记错了"
