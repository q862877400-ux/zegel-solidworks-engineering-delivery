"""★ EC00 残留 ③ 判据 —— 九份草案的**事实裁定**必须落盘且可复核。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/_probe_ec00_drafts_audit.json`（★ 审计读数）
#         `tools/ec00_drafts_audit.py`（★ 审计器 —— ★ 可重跑）
#         `output/DSH_DECISIONS.md` **D8**（★ 逐字：「★ 那是**事实缺口**，不是**决策缺口**」）
# 定位:   ★ 清 **EC00 残留 ③**。★★★ **判据**：★ 事实已核（★ 4 齐 / 7 不齐）、
#         ★ 且**没有**把它拍成「达标」（★ 那会违反 D8）。
# 官方依据: 不适用（本仓自产）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
AUDIT = ROOT / "output" / "_probe_ec00_drafts_audit.json"
RULING = SPEC / "acceptance" / "residual-03-drafts-audit.md"
AUDITOR = ROOT / "tools" / "ec00_drafts_audit.py"


def _audit() -> dict:
    assert AUDIT.is_file(), "★ 缺审计读数 `output/_probe_ec00_drafts_audit.json`"
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_audit_covers_all_engineering_drafts():
    """★★ 残留 ③：★ 审计必须覆盖**全部** `ENGINEERING_*.md`（★ 不能挑着核）。"""
    d = _audit()
    on_disk = sorted(p.name for p in (ROOT / "output").glob("ENGINEERING_*.md"))
    audited = sorted(r["file"] for r in d.get("engineering_rows", []))
    assert audited == on_disk, (
        "★★ 审计的文件集与盘上不一致：\n  盘上 %r\n  审计 %r" % (on_disk, audited))


def test_audit_reports_each_of_the_three_items():
    """★★★ 残留 ③：★ **三项**必须**逐份**给出读数（★ 不是只给一个总分）。"""
    d = _audit()
    for r in d["engineering_rows"]:
        for key in ("provenance", "license", "runnable_acceptance"):
            assert key in r, "★★ `%s` 缺 `%s` 读数" % (r["file"], key)
            assert "ok" in r[key], "★★ `%s` 的 `%s` 没有布尔读数" % (r["file"], key)
        #: ★ `three_of_three` 必须与三项**一致**（★ 不能自相矛盾）
        expected = all(r[k]["ok"] for k in ("provenance", "license", "runnable_acceptance"))
        assert r["three_of_three"] == expected, (
            "★★ `%s` 的 `three_of_three` 与三项不符" % r["file"])


def test_audit_finds_d8_qualitative_claim_holds():
    """★★★★★ 残留 ③ 的**结论判据**：★ 「D8 的定性成立」= **有不齐的**。

    ★★ 依据（★ D8 逐字）：★「★ 判为「参考草案、不是契约」……★ 本轮**未逐份核对**这三项」
    ★★★ **⇒ 若核出来**全部齐**，★ 那 D8 的**理由**就不成立了**（★ 要改 D8）；
    ★★ 若**有**不齐 ⇒ ★ **D8 的定性成立** ✓
    """
    d = _audit()
    total = d["engineering_total"]
    ok = d["engineering_three_of_three"]
    assert total >= 11, "★ 审计的份数太少：%d" % total
    assert ok < total, (
        "★★★ 若**全部**三项齐（%d/%d）⇒ ★ 应**改 D8**（★ 它的理由不再成立）"
        " —— ★ 而实测有 %d 份不齐 ⇒ ★ 结论要按实测写" % (ok, total, total - ok))
    #: ★★ 结论必须**写死**成「不齐的有几份」（★ 可复核）
    assert (total - ok) >= 1, "★ 不齐的份数应为正"


def test_ruling_does_not_declare_them_qualified():
    """★★★★★ 残留 ③：★ 裁定**不得**把它们拍成「达标」（★ 那违反 D8 逐字）。

    ★★ D8 逐字：★「**不得因为业主说"你决定"就把它判成达标** ✗」。
    """
    body = RULING.read_text(encoding="utf-8", errors="replace")
    #: ★★ 必须**显式**写明「不能用授权拍板」这条理由
    assert "事实缺口" in body and "决策缺口" in body, (
        "★★ 裁定里没有区分「事实缺口 / 决策缺口」⇒ ★ 会被误读成拍板")
    assert "不是拍板" in body or "不是**拍板**" in body or "事实裁定" in body, (
        "★★ 裁定没写明它是**事实结论**（★ 不是拍板）")
    #: ★★ 且**不许**出现「判为达标」这种话
    for bad in ("判为达标", "裁定达标", "三项齐即达标"):
        assert bad not in body, "★★ 裁定里出现了「%s」⇒ ★ 违反 D8" % bad


def test_auditor_is_rerunnable_and_documents_its_own_correction():
    """★★ 残留 ③：★ 审计器必须**可重跑**，★ 且**记下自己订正过一版**（★ 判据也要被审）。"""
    assert AUDITOR.is_file(), "★ 缺审计器"
    body = AUDITOR.read_text(encoding="utf-8", errors="replace")
    assert "订正" in body, "★ 审计器没记下自己订正过（★ 判据也要被审）"
    #: ★★ 收紧后的判据必须**在**（★ 要求可跑的命令行）
    assert "可跑的命令行" in body, "★★ 审计器的「可运行验收」判据没收紧"


def test_ruling_records_both_counts():
    """★★ 残留 ③：★ 裁定里必须**同时**有「齐」与「不齐」两个数（★ 可复核）。"""
    body = RULING.read_text(encoding="utf-8", errors="replace")
    d = _audit()
    assert str(d["engineering_three_of_three"]) in body, "★ 裁定里没写「齐」的份数"
    assert str(d["engineering_total"] - d["engineering_three_of_three"]) in body, (
        "★ 裁定里没写「不齐」的份数")
