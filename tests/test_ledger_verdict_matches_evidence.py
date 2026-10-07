"""★ 测「台账里说的 verdict」与「证据文件里的 verdict」**一致**（★ `JUDGE-A_B` 🔴 V-1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `capabilities.yaml`（`costing` 的 `evidence[0]`）· `output/costing-evidence.json`
# 定位:   ★ `JUDGE-A_B.md` 的 🔴 **A-moldcosting V-1** 逐字：「★ 条目写 `verdict: pass`，
#   文件是 `partial`（5/6）；★ 同仓另两条文字（`costing_readback` + ROADMAP）都写 partial
#   ⇒ ★★ **一个文件被写成两种结论**」✓
#   ★★ **实测复核（★ 我读了那个文件）**：★ 逐字 `"verdict": "partial"` · `"passed": 5` ·
#     `"of": 6` ⇒ ★★★ **5/6**；★ 唯一未过的是 **`list_templates`** ✓
#   ★★★ **本条的教训**：★★★ **台账里那句"verdict: X"是**转述** —— ★ 而转述会漂** ⇒
#     ★ **必须与文件里的原句对照**（★ 与事实 518/519「表里有/没有 ≠ 实际有/没有」**同族**）✓
#   ★★★ 2026-10-07（接手轮 · 规格 216）**按实测升级**（★ 起因：本文件当场红了）：
#     ★ 上面那条「**前提断言**：文件**确实**是 partial / 5-of-6」**把一次瞬时读数钉死了** ✗ ——
#       ★ 而实测：`tools/verify_costing_e2e.py` 的**现版本**（自建零件 + 7 步 + 3 条断言）
#       跑出来是 **`verdict: pass`**、`assertions` **3/3** ⇒ ★ 那条前提**不再成立** ✓
#     ⇒ ★★ **改法：不删这条守卫、把它升级成真正的不变量** ——
#       ★ **不再钉某个具体读数**，★ 而是判「★ **台账的现状句** 与 ★ **文件的原句** 一致」✓
#       ★ 这才是 V-1 的本意（★ 那句抱怨是"**一个文件被写成两种结论**"，★ 不是"必须是 partial"）✓
#     ⚠ 同时把「引旧句必须标明是旧的」从**写死 `verdict: pass`** 泛化成
#       「**凡引旧句就要带标记**」⇒ ★ 以后无论往哪个方向变，这条守卫都还站得住 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: ★ 认定「这一句是**旧句/被推翻**」的标记词 —— ★ 引旧句**必须**带其中之一 ✓
SUPERSEDED_MARKS = ("更正", "原写", "作废", "旧一版", "旧写法")


def _costing_evidence_text() -> str:
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    c = [x for x in d["capabilities"] if x.get("id") == "costing"][0]
    return " ".join(str(x) for x in (c.get("evidence") or []))


def _evidence_file():
    """★ 证据文件的顶层 dict —— ★ 文件不在本机就回 `None`（★ 便携性：跳而不红）✓"""
    f = REPO / "output" / "costing-evidence.json"
    if not f.is_file():
        return None
    return json.loads(f.read_text(encoding="utf-8", errors="replace"))


# ── ① 文件自洽（★ 换了形状也站得住）────────────────────────────────────
def test_evidence_file_has_a_recognised_verdict() -> None:
    """★★ 断言（★ 2026-10-07 升级版）：★ 文件的 `verdict` 要么是 `pass`、要么**带原因** ✓

    ⚠ 原来这里是「**前提断言**：文件确实是 partial / 5-of-6」——
      ★ 那是**把一次瞬时读数钉死** ⇒ ★ 文件一更新它就红，★ 而它红的时候**不代表有错** ✗
      ★ 现在改成判**形状**：★ `pass` ⟺ `assertions` 全 true；★ 非 `pass` ⇒ 必须写明差什么 ✓
    """
    d = _evidence_file()
    if d is None:
        return
    v = str(d.get("verdict") or "")
    assert v, "★ 文件里没有 verdict"
    a = d.get("assertions")
    if a is not None:
        #: ★ 新形状（2026-10-07 实测）：`assertions` 是若干条布尔断言 ✓
        if v == "pass":
            assert all(a.values()), "★ verdict=pass 而 assertions 里有 false：%r" % a
        else:
            assert not all(a.values()), "★ verdict=%r 而 assertions 全 true ⇒ 两者自相矛盾" % v
    else:
        #: ★ 旧形状：`passed`/`of` 计数 —— ★ 只要求"数得出来"，★ 不钉具体值 ✓
        assert isinstance(d.get("passed"), int) and isinstance(d.get("of"), int), (
            "★ 既没有 assertions、也没有 passed/of ⇒ 这个文件判不出 verdict：%r" % list(d))


# ── ② 核心不变量：台账现状 ⟺ 文件原句（★ V-1 的本意）──────────────────
def test_ledger_current_claim_matches_the_evidence_file() -> None:
    """★★★ **核心断言**：★ 台账**现状句**说的 verdict，必须与**文件原句**一致 ✓

    ★ 这正是 `JUDGE-A_B` V-1 抱怨的那件事 —— ★ 它抱怨的是「**一个文件被写成两种结论**」，
      ★ **不是**"必须是 partial" ⇒ ★ 判据就该是**一致性**，★ 而不是某个具体值 ✓
    ★★ **锚点（★ 比"某个词出现在文里"强得多）**：★ 台账文本里**必须**出现
      「`verdict` + 至多 12 个字符 + **文件里那个词**」的**相邻形态** ——
      ★ 即「★ 台账**确实写出了一句 verdict 声明**」，★ 而不是只在别处顺口提到那个词 ✓
    ★★ **负例已证**（★ 事实 62：负例是门禁有效的唯一证明）—— ★ 实测手法：
      ★ 把台账里那处 `verdict: pass` 抹掉（其余不动）⇒ ★ 本条**当场红** ✓
    """
    d = _evidence_file()
    if d is None:
        return
    v = str(d.get("verdict") or "")
    word = v.split(":")[0].strip()                    #: 'pass' / 'partial' / 'fail' …
    t = _costing_evidence_text()
    assert re.search(r"verdict[^\n]{0,12}?%s" % re.escape(word), t), (
        "★ 台账里**没有**写出与文件一致的 verdict 声明（文件是 %r）⇒ 又变成两种结论" % v)
    #: ★ 旧句若还在 ⇒ **必须**标明它是旧的（★ 本仓纪律：自我否定要**补正**而不是删除）✓
    for stale in ("partial", "verdict: pass"):
        if stale in t:
            assert any(m in t for m in SUPERSEDED_MARKS), (
                "★ 台账里还有 `%s`、★ 却**没标**它是旧写法 ⇒ 与文件相反" % stale)


# ── ③ 非 pass 时必须点名"差哪一步"（★ 2026-10-07：空集时自然成立）────────
def test_ledger_names_the_failing_step_when_there_is_one() -> None:
    """★★★ 核心断言：★ 有未过的步骤 ⇒ 必须点名（★ 否则只知道 partial、不知道差什么）✓"""
    d = _evidence_file()
    if d is None:
        return
    failing = [k for k, v in (d.get("steps") or {}).items() if v is False]
    t = _costing_evidence_text()
    for name in failing:
        assert name in t, "★ 没点名未过的那一步 `%s`" % name


# ── ④ 负例：补正而不删除（★ 泛化后仍要能抓到"引旧句却不标"）─────────────
def test_negative_case_correction_marks_the_old_wording() -> None:
    """★★★ **负例 · 补正而不删除**：★ 更正里**必须**引旧句、★ 且**标出**它是旧的 ✓

    ⚠ 2026-10-07 泛化：原来这条写死 `assert "verdict: pass" in t`（★ 只覆盖"从 pass 改 partial"
      那一个方向）⇒ ★ 现在改成判**规则**：★ **凡引旧句 ⇒ 必带标记** ✓
      ★ 并**保留**它作为负例的意义：★ 台账若声称是"更正"、★ 却把旧句删干净，
      ★ 后人就不知道改了什么（★ 本仓纪律逐字：**自我否定必须补正而不是删除**）✓
    """
    t = _costing_evidence_text()
    if any(m in t for m in SUPERSEDED_MARKS):
        assert any(s in t for s in ("partial", "pass")), (
            "★ 标了「更正」★ 却没引被更正的那句 ⇒ 后人看不出改了什么")
    else:
        #: ★ 没有更正标记 ⇒ 台账应当**只**说现状（★ 那就必须与文件一致，由 ② 守着）✓
        assert "partial" not in t and "verdict: pass" not in t, (
            "★ 引了旧句、★ 却连一个更正标记都没有 ⇒ 「补正而不删除」这条没落实")
