"""★ 测「台账里说的 verdict」与「证据文件里的 verdict」**一致**（★ `JUDGE-A_B` 🔴 V-1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `capabilities.yaml`（`costing` 的 `evidence[0]`）· `output/costing-evidence.json`
# 定位:   ★ `JUDGE-A_B.md` 的 🔴 **A-moldcosting V-1** 逐字：「★ 条目写 `verdict: pass`，
#   文件是 `partial`（5/6）；★ 同仓另两条文字（`costing_readback` + ROADMAP）都写 partial
#   ⇒ ★★ **一个文件被写成两种结论**」✓
#   ★★ **实测复核（★ 我读了那个文件）**：★ 逐字 `"verdict": "partial"` · `"passed": 5` ·
#     `"of": 6` ⇒ ★★★ **5/6**；★ 唯一未过的是 **`list_templates`** ✓
#   ★★★ **本条的教训**：★★★ **台账里那句"verdick: X"是**转述** —— ★ 而转述会漂** ⇒
#     ★ **必须与文件里的原句对照**（★ 与事实 518/519「表里有/没有 ≠ 实际有/没有」**同族**）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _costing_evidence_text() -> str:
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    c = [x for x in d["capabilities"] if x.get("id") == "costing"][0]
    return " ".join(str(x) for x in (c.get("evidence") or []))


def test_evidence_file_really_is_partial() -> None:
    """★★★ **前提断言**：★ 那个文件**确实**是 `partial` / 5-of-6（★ 判据的锚点）✓"""
    f = REPO / "output" / "costing-evidence.json"
    if not f.is_file():
        return                                                            # ★ 证据文件不在本机 ⇒ 跳过
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    assert d.get("verdict") == "partial", "★ 文件的 verdict 变了：%r" % d.get("verdict")
    assert d.get("passed") == 5 and d.get("of") == 6, "★ 5/6 变了：%r" % (d.get("passed"), d.get("of"))


def test_ledger_does_not_claim_pass() -> None:
    """★★★ 核心断言：★ 台账**不许再把**它说成 `pass` —— ★★ 而**引旧句**是允许的 ✓

    ★★★★ **形状（★ 与轮 66 那条**同形**）**：★ 本仓纪律是**「自我否定必须补正而不是删除」** ⇒
      ★ **旧句留在更正里是对的** ⇒
      ★★ **判据是二选一**：★ **旧句不在**（干净）· ★★ **或 旧句在 + 标了「更正/原写」** ✓
      ★★★ **"旧句必须消失"是错的判据** —— ★ 它会把**合格的补正**判成不合格 ✓
    """
    t = _costing_evidence_text()
    if "verdict: pass" in t:
        assert ("更正" in t) or ("原写" in t), (
            "★ 台账里还有 `verdict: pass`、★ 却**没标明那是旧写法** ⇒ 与文件相反")
    assert "partial" in t, "★ 没写明真实 verdict"
    assert "5" in t and "6" in t, "★ 没写清 5/6"


def test_ledger_names_the_failing_step() -> None:
    """★★★ 核心断言：★ 必须点名**哪一步没过**（★ 否则只知道"partial"、★ 不知道差什么）✓"""
    f = REPO / "output" / "costing-evidence.json"
    if not f.is_file():
        return
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    failing = [k for k, v in (d.get("steps") or {}).items() if v is False]
    t = _costing_evidence_text()
    for name in failing:
        assert name in t, "★ 没点名未过的那一步 `%s`" % name


def test_negative_case_correction_quotes_the_old_wording() -> None:
    """★★★ **负例 · 补正而不删除**：★ 更正里**必须**引旧句（★ 否则后人不知道改了什么）✓"""
    t = _costing_evidence_text()
    assert "verdict: pass" in t, "★ 更正里没有引旧写法 ⇒ 「补正而不是删除」这条没落实"
    assert "更正" in t, "★ 没标出这是更正"
