"""★ 规格 298 判据：二级文档 `phase2-obsolete-status.md` 的旧措辞必须与 `sw_part.py` 的订正对齐。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `docs/phase2-obsolete-status.md`（★ 二级文档 · 那份「处置阶段 2」的状态表）
#         `scripts/sw_part.py:1457-1466`（★ spec 293 的**订正块** —— 一级真源）
#         `C:\swapi\types\IFeatureManager\FeatureLinearPattern5.md:12`（★ 官方逐字给了后继）
# 定位:   ★★ 起因：`AUTO_HANDOFF.md` ④ 段登记项 **⑥** 逐字 ——
#         「★ `docs/phase2-obsolete-status.md:36` 的旧措辞（「`5` 就是现行那代」）★ 与 `sw_part.py` 的订正对齐」。
#         ★★★ 为什么必须修：★★ `MEMORY.md` 规则 30 逐字 ——
#         「**「同一事实被写在 N 处」⇒ 必须有一条判据把 N 处串起来** ——
#          ★ 291 实测：`AddMate5` 的分流语义被写在 **5 处** ⇒ ★ 前 3 处改了、后 2 处漏了
#          ⇒ ★★ 「改了 A 没改 B」**永远发现不了**（★ 且 docstring 是**施工指令**，会骗下一轮）」。
# 官方依据: `C:/swapi/types/IFeatureManager/FeatureLinearPattern5.md`（★ 后继 `CreateFeature`）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "phase2-obsolete-status.md"
SRC = ROOT / "scripts" / "sw_part.py"

#: ★★ 官方逐字（★ `FeatureLinearPattern5.md:12`）
OFFICIAL = "See `IFeatureManager::CreateFeature`"

#: ★★★ **撤回标记**（★ 逐字沿用 `scripts/check_official_md_claims.py` 的 `QUOTED_MARKERS` 同款口径）——
#:   ★★ 本仓的规矩是：★ 订正**要引旧话**（★ 否则读者不知道改了什么），
#:   ★ 而「引旧话」与「仍在主张旧话」**必须能分开** ⇒ ★ 判据是**同行有没有撤回标记**。
#:   ★★ 依据：★ `check_official_md_claims.py` 的 `_is_retracted()` 逐字
#:   「★ 该行是不是「**已被我撤回的引述**」」✓
RETRACTED_MARKERS = ("更正", "此前", "原写", "原先", "曾经", "是错的", "错了", "撤销")


def _is_retracted(line: str) -> bool:
    """★ 该行是不是「**已被撤回的引述**」（★ 引旧话来说明「那句话错了」）。"""
    return any(mk in line for mk in RETRACTED_MARKERS)


def test_doc_no_longer_says_five_is_the_current_generation():
    """★★★ 旧措辞「`5` **就是现行那代**」不得**作为主张**存在（★ 撤回式引述除外）。

    ★★ 真因（★ spec 293）：★ 官方**给了**后继 —— ★ 而且是**跨族**的 `CreateFeature`
      ⇒ ★ 「本族最高代」**≠**「没有后继」。
    ★★ 引旧话**说明它错了**是**允许且应该**的（★ 否则读者不知道订正了什么）——
      ★ 判据因此是「**这一行有没有撤回标记**」。
    """
    lines = DOC.read_text(encoding="utf-8", errors="replace").splitlines()
    bad = []
    for i, line in enumerate(lines, 1):
        if "就是现行那代" not in line:
            continue
        if not _is_retracted(line):
            bad.append("L%d: %s" % (i, line.strip()[:140]))
    assert not bad, (
        "★ 二级文档把旧措辞「`5` 就是现行那代」当成**主张**在写（★ 无撤回标记）—— "
        "★ 它会被读成「没有后继」，★ 而官方逐字给了后继 `CreateFeature`（★ `MEMORY.md` 规则 30）：\n  "
        + "\n  ".join(bad))


def test_doc_carries_the_official_successor():
    """★★★ 订正后必须写出**官方后继**（★ 不能只把旧话删掉、不留结论）。"""
    body = DOC.read_text(encoding="utf-8", errors="replace")
    assert OFFICIAL in body, (
        "★ 二级文档里没有官方逐字的后继句 %r ⇒ ★ 只删旧话、没留结论" % OFFICIAL)
    assert "跨族" in body, "★ 没写清「后继是**跨族**的」—— ★ 那是本条最容易读反的地方"
    assert "本族最高代" in body, "★ 没写清「`5` 是**本族最高代**」的正确口径"


def test_the_two_places_agree_on_the_verdict():
    """★★★ **两处必须一致**（★ 规则 30 的形态：把 N 处串起来）。

    ★ 一级真源 = `scripts/sw_part.py` 的订正块；★ 二级文档 = `docs/phase2-obsolete-status.md`。
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    doc = DOC.read_text(encoding="utf-8", errors="replace")
    #: ★ 两处都要有官方后继句
    assert OFFICIAL in src, "★ 一级真源（`sw_part.py`）里没有官方后继句"
    assert OFFICIAL in doc, "★ 二级文档里没有官方后继句"
    #: ★ 两处都要点明「跨族」
    assert "跨族" in src, "★ 一级真源里没写「跨族」"
    assert "跨族" in doc, "★ 二级文档里没写「跨族」"


def test_doc_points_back_to_the_primary_source():
    """★★ 二级文档必须**指回一级真源**（★ 否则下次又是"改了 A 没改 B"）。"""
    body = DOC.read_text(encoding="utf-8", errors="replace")
    assert "sw_part.py" in body, "★ 订正处没指回 `scripts/sw_part.py` 的订正块"


def test_no_stale_no_successor_claim_anywhere_in_the_doc():
    """★★★ **全篇**不得再有「后继为空 / 没有后继」这类**针对 `5`** 的**主张**。

    ★ 依据：★ 规则 30 的教训是「**改了 A 没改 B**」——
      ★ 所以判据要**扫全篇**，★ 不是只看那一行。
    ★★ 撤回式引述（★ 同行带撤回标记）**不算主张** ⇒ 不报（★ 与上一条同口径）。
    """
    lines = DOC.read_text(encoding="utf-8", errors="replace").splitlines()
    bad = []
    for i, line in enumerate(lines, 1):
        if "FeatureLinearPattern" not in line:
            continue
        if ("后继为空" in line) or ("没有后继" in line):
            if not _is_retracted(line):
                bad.append("L%d: %s" % (i, line.strip()[:120]))
    assert not bad, (
        "★ 二级文档里仍有「`5` 没有后继」类的**主张**（★ 官方给了跨族后继）：\n  " + "\n  ".join(bad))
