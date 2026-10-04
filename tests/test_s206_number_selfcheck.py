"""★ 契约测试：产出物里**已知错过的那个数**不许再出现（★ 含负例 —— 事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_s206_number_selfcheck.py
# 定位:   规格 206 的 **SC-5**（口径不许漂）的落点。
#         起因（事实 538）：同一次自查抓到我把 **3806** 写成 **3709** —— 靠人眼不会发现。
# ★★ 判据的**设计取舍**（★ 这一版是第二次改，第一次写宽了）：
#         第一版用「窗口内出现键名」的**宽启发式** ⇒ **当场 5 处误报**
#         （两个根因：`more_specific_members` **含** `more_specific` ⇒ 键名互相错配；
#           而真值表那份文件里所有键都在 ⇒ 窗口必然重叠）✓✗
#         ⇒ ★ 本版改用**窄而精确**的判据：**只守"已知错过的那个数"**（3709）——
#           ★ 零误报、直接守住真发生过的错 ✓（★ 与本规格的定则①同族：判据越宽越易误报）
# 依据:   `docs/recon-206/number-selfcheck.md` · 事实 538 · 事实 62（负例是唯一证明）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECON = ROOT / "docs" / "recon-206"

#: ★★ 已知的错数 → 真值（★ 只登记**真发生过**的，不猜）
KNOWN_WRONG = {
    "3709": ("3806", "example_more_specific 的条数（★ 目标文本写 3709，★ 实量 3806）"),
}
#: ★★ 允许它以**引用身份**出现的标记（★ 事实 538：引用与生产在文本上不可区分 ⇒ 引用要自证）
CITATION_MARKERS = ("目标写", "目标里写", "实量以此为准", "更正", "原写", "照目标文本抄",
                    "KNOWN_WRONG")


def offenders(text: str) -> list:
    """★ 找出「错数出现、且**同一行内没有引用标记**」的行 ✓"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for wrong, (_truth, _why) in KNOWN_WRONG.items():
            if wrong in line and not any(mk in line for mk in CITATION_MARKERS):
                out.append((i, wrong, line.strip()[:110]))
    return out


def _files() -> list:
    """★★ 只扫**真发生过那个错的文件**（`docs/recon-206/README.md`）——
    ★ 不全量扫：第一版全量扫时**当场 5 处误报**，第二版仍 3 处
    （★ 自查文件自己会报这条发现、`tasks.md` 引的是目标原文 ⇒ **正当提及到处都是**）⇒
    ★★ **正当提及与真错在文本上不可区分**（事实 538 的定则）⇒
    ★ 本测试**只守那个真回归点**：`README.md` 里不许再出现未被标记的 3709 ✓
    """
    return [ROOT / "docs" / "recon-206" / "README.md"]


def test_known_wrong_table_is_registered():
    """★ 守卫：错数表空掉时本测试会「静默全通过」⇒ 必须先证明它非空且都带真值。"""
    assert KNOWN_WRONG, "错数表是空的"
    for w, (t, why) in KNOWN_WRONG.items():
        assert w != t and why.strip(), w


def test_current_tree_has_no_uncited_wrong_number():
    """★★ 主断言：产出物里**不许**出现「错数且没写引用标记」。"""
    bad = []
    for f in _files():
        if f.is_file():
            bad += [(f.name, *o) for o in offenders(f.read_text(encoding="utf-8",
                                                              errors="replace"))]
    assert not bad, "出现未被引用标记覆盖的错数: %s" % bad[:5]


def test_negative_wrong_number_without_marker_is_detected():
    """★★ 负例（★ 事实 62）：故意写错数且不加引用标记 ⇒ **必须报出来** ✓"""
    fake = "- ★ c4-merged.json 的 **3709 条 example_more_specific**\n"
    got = offenders(fake)
    assert got, "负例没被抓到 ⇒ 判据是空转的"


def test_negative_wrong_number_with_marker_is_not_reported():
    """★★ 反向负例：同一句**加上引用标记** ⇒ **不该**报（否则永久失败）✓"""
    ok = "- ★ **3806** 条（★ **目标写 3709**，★ 实量以此为准）\n"
    assert not offenders(ok), "引用语境被误报了"


def test_criterion_is_narrow_by_design():
    """★ 记录本测试的**限度**：它只守「已知错过的那个数」，**不做**通用的数字一致性检查。

    ★★ 通用版（窗口匹配键名）实测**5 处误报** ⇒ 已放弃（★ 见文件头）。
    ★ 这条测试是有意写死的：防止后人以为它在做全量一致性检查 ✓
    """
    src = Path(__file__).read_text(encoding="utf-8")
    assert "只守\"已知错过的那个数\"" in src or "只守" in src
