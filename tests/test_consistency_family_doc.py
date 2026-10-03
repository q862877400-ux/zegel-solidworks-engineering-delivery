"""★ 测：★ `docs/consistency-family.md` 点名的那些**机制真的在仓里**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `docs/consistency-family.md`（★ 新 —— 本族的沉淀）
# 定位:   ★ 2026-10-04（轮 121）：★ 全量从 **`25 failed / 1711 passed`** 清到
#   **`1752 passed / 0 failed`**（★ 22 条存量全部有偿处置）⇒
#   ★★ **而那 22 条的真因都落在**同一族****：★ 「改了实现、★ 配套的没跟上」⇒
#   ★★★ **⇒ 把七类形态与四条跨类手法写成 `docs/consistency-family.md`** ✓
#   ★★★★ **⇒ 本测试守的是那份文档的**点名不许落空**** ——
#     ★ 它提到的每个**工具/文件**都必须在仓里**真的存在** ✓
#     （★ 与**事实 62**「写了不等于有效」同族：★ **一份只说不做的文档也是死守卫**）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "docs" / "consistency-family.md"


def test_the_doc_exists_and_is_reachable_from_a_known_door() -> None:
    """★★★ 核心断言：★ 文档在、★ 且**够长**（★ 不是占位）✓"""
    assert DOC.is_file(), "★ `docs/consistency-family.md` 不见了"
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert len(t) > 2500, "★ 文档太短（★ %d 字）⇒ 像是占位" % len(t)
    #: ★★ 七类都必须列出来（★ 否则"七类"这个说法是空的）✓
    for k in ("mock 落后", "stub 少装", "对象归属", "登记表落后",
              "定位漂移", "返回形态", "冻结快照"):
        assert k in t, "★ 文档里少了 `%s` 这一类" % k


def test_every_mechanism_it_names_really_exists() -> None:
    """★★★★ 核心断言：★ 文档点名的**每个文件**都真的在仓里 ✓

    ★★ **为什么**：★ 一份"说有个帮手 `X`"、★ 而 `X` **不存在**的文档
      ★★★ **会把人引到空处** —— ★ 那比没有文档更坏 ✓
    """
    named = [
        "tests/_funcbody.py",          # ★ 取函数体的 `ast` 帮手
        "tests/_codescan.py",          # ★ 剥注释与字符串
        "tests/unattended_baseline.json",
        "scripts/audit_call_arity.py",  # ★ 含 `COMTYPES_CALL_SITES`
        "tests/test_no_uncalled_helpers.py",   # ★ 含 `UNCALLED_EXEMPT`
    ]
    t = DOC.read_text(encoding="utf-8", errors="replace")
    for rel in named:
        assert rel.split("/")[-1] in t, "★ 文档没点名 `%s`" % rel
        assert (REPO / rel).is_file(), "★ 文档点名的 `%s` 在仓里**不存在**" % rel


def test_the_functions_it_names_exist() -> None:
    """★★★ 核心断言：★ 它点名的**函数**也要在 ✓"""
    checks = [
        ("tests/_funcbody.py", "def func_source"),
        ("tests/_codescan.py", "def code_only"),
    ]
    for rel, needle in checks:
        f = REPO / rel
        assert f.is_file(), "★ 缺 `%s`" % rel
        assert needle in f.read_text(encoding="utf-8", errors="replace"), (
            "★ `%s` 里没有 `%s` ⇒ 文档把它指到了空处" % (rel, needle))


def test_negative_case_the_readout_is_the_real_one() -> None:
    """★★★★ **负例 · 文档里那个读数**要与实际相符**（★ 至少自洽）✓

    ★★ **判据**：★ 文档写的收口读数是 **`0 failed` / `1752 passed`** ⇒
      ★★★ **本测试不重跑全量**（★ 那要 4.5 分钟、★ 而纪律说不要每轮跑），
      ★★ **而是核**三个读数的形状与次序**：
        ★ 起始 `25 failed` ⇒ ★ 中间 `3 failed` ⇒ ★★ **收口 `0 failed`** ✓
      ★★★ **⇒ 若有人只改了其中一个数字，★ 次序就断了** ✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    for s in ("25 failed / 1711 passed", "3 failed / 1741 passed",
              "0 failed / 1752 passed"):
        assert s in t, "★ 读数里少了 `%s`" % s
    #: ★★ 三者的**次序**必须是 25 → 3 → 0（★ 单调下降）✓
    i25 = t.find("25 failed / 1711 passed")
    i3 = t.find("3 failed / 1741 passed")
    i0 = t.find("0 failed / 1752 passed")
    assert i25 < i3 < i0, "★ 三个读数的次序断了（★ 25 → 3 → 0）"
