"""钉住 **NOTICE 与现实的对应关系**（A6 的可机器化部分）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_notice_consistency.py
# 定位:   轮 131：A6（许可无越界 + Apache-2.0 带 NOTICE 义务）此前**只靠人读**。
#         本文件把它**可机器化的那一半**钉住：
#           ① `THIRD-PARTY-NOTICES.md` 必须在；
#           ② ★ **能力条目里出现的外部来源，NOTICE 里必须都有登记**；
#           ③ NOTICE 必须写明"哪些是包含 / 哪些只是评估过"。
# 官方依据: 不适用（本项目内部的许可纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTICE = REPO_ROOT / "THIRD-PARTY-NOTICES.md"
CAPS = REPO_ROOT / "capabilities.yaml"

#: ⚠ 这两个**不是**外部来源，是"我们自己"与"上游基底"
SELF_OWNERS = ("wzyn20051216", "microsoft")


def _notice_text() -> str:
    assert NOTICE.is_file(), "THIRD-PARTY-NOTICES.md 不在：%s" % NOTICE
    return NOTICE.read_text(encoding="utf-8")


def test_notice_exists_and_separates_included_from_evaluated():
    """@brief NOTICE 必须**区分**「实际包含」与「只评估过、未并入」。"""
    t = _notice_text()
    assert "实际包含" in t or "实际**包含**" in t, "要有「实际包含」段"
    assert "尚未并入" in t or "未并入" in t, "要有「未并入」段"


def test_every_external_owner_in_capabilities_is_registered_in_the_notice():
    """@brief ★★ **能力条目里出现的每个外部 owner，NOTICE 里都要有登记**。

    这是 A6 的可机器化部分：**参考了谁，就要登记谁**。
    ⚠ 找不到就说明"某个来源被用到了但没登记" —— 那正是许可义务会漏的地方。
    """
    caps = json.loads(CAPS.read_text(encoding="utf-8"))["capabilities"]
    notice = _notice_text()
    owners: set = set()
    for c in caps:
        for p in (c.get("provenance") or []):
            repo = str(p.get("repo") or "")
            if "/" in repo:
                owners.add(repo.split("/")[0])
    #: 我们自己与上游基底不算"第三方"
    owners -= set(SELF_OWNERS)
    missing = sorted(o for o in owners if o not in notice)
    assert not missing, "这些 owner 被能力条目引用，但 NOTICE 里没有登记: %s" % missing


def test_every_registered_provenance_has_the_four_required_fields():
    """@brief ★ 能力级 `provenance` 的四字段要齐（A2 第②层）。

    ⚠ 官方四字段：`repo` / `license` / `files` / `upstream_verified`。
    """
    caps = json.loads(CAPS.read_text(encoding="utf-8"))["capabilities"]
    for c in caps:
        for p in (c.get("provenance") or []):
            for field in ("repo", "license", "files", "upstream_verified"):
                assert field in p, "%s 的 provenance 缺 %s" % (c["id"], field)
            assert re.match(r"^[\w.-]+/[\w.-]+$", str(p["repo"])), \
                "%s 的 repo 要写 owner/repo 全名，实际 %r" % (c["id"], p["repo"])
            assert p["license"], "%s 的 license 不能空" % c["id"]


def test_notice_records_a_history_table():
    """@brief ★ NOTICE 要有**登记历史**，且**不止一条**（初版之后有变化就要记）。

    ⚑ 轮 131：此前只有 1 条「初版」，而 fork 已有 200+ 提交 ⇒ **历史过时**。
    """
    t = _notice_text()
    assert "登记历史" in t, "要有登记历史段"
    seg = t[t.index("登记历史"):]
    rows = [l for l in seg.splitlines() if l.strip().startswith("| 20")]
    assert len(rows) >= 2, "登记历史至少要有「初版」之外的条目，实际 %d 条" % len(rows)


def test_notice_names_the_apache_source_obligation():
    """@brief ★ Apache-2.0 的义务要**点名写明**（`Slacker-LLC` + 版权行）。"""
    t = _notice_text()
    assert "Slacker-LLC" in t, "要点名 Apache-2.0 来源"
    assert "JIALE LIU" in t, "要带版权行"
    assert "Apache-2.0" in t, "要写明许可"


# ══ 轮 195 补的两条：**"可重跑核验"必须真的可重跑** + **数字不许另一个家** ══════════

#: NOTICE 里那条「可重跑核验」命令的注释形如 `# → ['mold_tools']   （说明…）`
#: ⚠ `re.M` **必须有** —— 否则 `^` 只匹配**整个字符串的开头**（第一版就栽在这，找不到任何注释）
_EXPECTED = re.compile(r"^#\s*→\s*(\[.*?\]|\S+)", re.M)


def test_notice_runnable_check_matches_reality():
    """@brief ★★ NOTICE 里**号称可重跑核验**的命令，其**注释的预期输出必须与实跑一致**。

    ⚠ 轮 195 实测出的病：那条命令的注释写着 `# → []`（0 条带 `provenance`），
      而**实跑输出是 `['mold_tools']`** —— ★ 且与本文件 §一.3 和「登记历史」**自相矛盾**。
    ⇒ ★★ 一条**预期输出写错**的"可重跑核验"**证明不了任何事** ——
      它只是把**印象**写成了**注释**（而这正是文件开头说它要避免的事）。
    ★ 本测试**实跑**那条查询并**逐字比对**注释 ⇒ 于是它**真的可重跑**了。
    """
    t = _notice_text()
    m = _EXPECTED.search(t)
    assert m, "NOTICE 里找不到 `# → …` 形式的预期输出注释"
    want = m.group(1).strip()
    #: ★ 实跑那条查询（与 NOTICE 里的命令等价；不依赖 NOTICE 的排版）
    caps = json.loads(CAPS.read_text(encoding="utf-8"))["capabilities"]
    got = repr([c["id"] for c in caps if c.get("provenance")])
    assert got == want, (
        "NOTICE 的预期输出已与现实不符：\n  注释写 %s\n  实跑为 %s\n"
        "⇒ 要么改注释，要么改清单 —— **两者必须一致**（否则它证明不了任何事）" % (want, got))


def test_notice_does_not_carry_its_own_drift_number():
    """@brief ★★ NOTICE **不许**再写"偏离上游"的精确数字 —— **一个事实一个家**。

    ⚠ 轮 195 实测：本文件曾被改成「只写量级」的 `179 个文件 / +126,7xx 行`，
      并注明"不再重复维护一个会腐坏的数字"——
      ★★★ **而那个"量级"本身也腐坏了**（真实 `343 个文件 / +155,707 行`，差近一倍）。
    ⇒ ★ 真正的修法不是"写个粗略的"，而是**不在这里写**：唯一权威是
      `docs/harvest-report.md` 开篇那行（有 `check_report_freshness.py` 守着）。
    ⚠ **本测试的判据是"形如 `N 个文件 / +M 行` 的精确样式不得出现"** ——
      它**不禁止**指向 harvest-report 的散文（那正是要留的）。
    """
    t = _notice_text()
    bad = re.findall(r"\d[\d,]*\s*个文件\s*/\s*\+\s*[\d,x]+", t)
    #: ⚠ 允许出现在**更正说明**里（本轮那段"原写…真实是…"就是**历史记录**，不是"维护着一个数"）
    #:   ⇒ 只对**非引用行**报。引用行以 `> ` 开头（引用块）。
    live = [b for b in bad if not any(b in l and l.lstrip().startswith(">") for l in t.splitlines())]
    assert not live, (
        "NOTICE 里出现了「偏离上游」的精确数字 %s ⇒ **一个事实一个家**：\n"
        "  唯一权威是 docs/harvest-report.md 开篇那行（有门禁守）\n"
        "  ⇒ 本文件只**指向**它，不重复维护" % live)


# ══ 轮 196 补的一条：NOTICE 对**第三方**的方法名论断必须可核 ══════════════════

#: 官方反射转储（本机）—— 「某成员名在官方 API 里存不存在」的**权威源**
REFLECT = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
#: NOTICE 段里点名的成员名（反引号包着，可能带 arity 后缀）
_BACKTICK = re.compile(r"`((?:I)?[A-Z][a-z]\w*)\s*(?:\([^`]*\))?`")
#: 句子切分：**中文分号 / 句号**（★ NOTICE 那段用 `；` 分开「查不到」与「真名是」两半）
#: ⚠⚠ **换行不算分隔符**（2026-10-01 轮 196 第一版把它算进去了 ⇒ 只解析到 **1** 个名字）：
#:   那两处散文**跨行**书写 —— 名字在上一行、"查不到"/"官方真名是"在下一行
#:   ⇒ 按 `\n` 切会**把它们分到不同片段**，于是两半**都匹配不上**。
#:   ★ 与本项目反复出现的"判据太窄"同型（事实 51 / 185 / 190 / 192 / 193）。
_SENT = re.compile(r"[；;。]")


def _notice_sentences() -> list:
    """把 NOTICE 切成**论断句**（`\\n` 视作空格 —— 散文会换行，换行不是句界）。"""
    return _SENT.split(_notice_text().replace("\n", " "))


def _notice_name_claims() -> tuple:
    """从 NOTICE 里解析出**可核的方法名论断** ⇒ `(必须存在的, 必须不存在的)`。

    ★ **为什么解析而不是在测试里硬编码**：NOTICE 是**会长的** ——
      以后再加一条"某来源的某方法名是错的"论断时，本测试**应当自动覆盖它**，
      否则就得有人记得回来补测试（那正是"靠约定"）。
    ⚠ 句子形态（**判据就锚在这里，写出来**）：
      · 含「**官方真名**」的句子里反引号点的成员名 ⇒ **必须在**官方反射里
      · 含「**查不到**」的句子里反引号点的成员名 ⇒ **必须不在**官方反射里
    ⚠ 与本形态不符的散文 ⇒ **未覆盖**（本函数不猜），由 `test_..._is_actually_covered` 如实报出。
    """
    must_exist: set = set()
    must_not: set = set()
    for sent in _notice_sentences():
        names = set(_BACKTICK.findall(sent))
        if not names:
            continue
        if "官方真名" in sent:
            must_exist |= names
        if "查不到" in sent:
            must_not |= names
    return must_exist, must_not


def _reflection_has(name: str) -> bool:
    """官方反射转储里有没有这个成员名（**本机权威**）。

    :raises RuntimeError: 反射转储不在本机时 —— ★★ **不许静默返回 `False`**。

    ⚠⚠⚠ **2026-10-01（轮 197）修的是轮 196 自己记下的限度**：
      第一版在转储缺失时 `return False` ⇒ ★ 那会把「**无从判定**」变成「**查不到**」，
      即**把缺源误报成论断不成立**（而本项目已多次记录这一族：
      **兜底会把「我不知道」变成「它有错」** —— 事实 113/114/115/116）。
      ⇒ 现在：**缺源 ⇒ 抛**；调用方（测试）用 `_require_reflection()` 先 **skip 并说明原因**
        （沿用本项目既有的便携性守卫写法：`pytest.skip("拿不到…（便携性）")`）。
    """
    if not REFLECT.is_file():
        raise RuntimeError(
            "拿不到反射转储 %s ⇒ 「`%s` 在不在官方 API 里」**无从判定**"
            "（**不要当成 False**）" % (REFLECT, name))
    t = REFLECT.read_text(encoding="utf-8", errors="replace")
    return re.search(r"\b%s\b" % re.escape(name), t) is not None


def _require_reflection() -> None:
    """**便携性守卫**：拿不到本机反射转储 ⇒ `skip` 并**说明原因**（不是静默通过，也不是误报）。"""
    if not REFLECT.is_file():
        pytest.skip("拿不到反射转储 %s ⇒ 本机无法核「成员名存不存在」（便携性守卫）" % REFLECT)


def test_notice_external_method_name_claims_are_verifiable():
    """★★★ NOTICE 对**第三方**的方法名论断必须**逐条可核**（这是"归属"问题）。

    ⚠ 为什么值得钉：`THIRD-PARTY-NOTICES.md` 里写着
      「该来源对模具域的**两个方法名都是错的**（… 在官方反射里查不到；官方真名是 …）」——
      ★ 这是我们**对第三方下的判断**。若那半说反了，就不是遗漏而是**错误论断**
      （而文件开头自己写着「**归属造假比遗漏更严重**」）。
    ★ 实测（轮 196）：那 4 个名字**逐条属实**（2 个确不在反射里、2 个确在）。
      ⇒ 本测试把这 4 条（以及**将来新加的同类论断**）钉住。
    ⚠ **便携性**（轮 197 加）：拿不到反射转储时 **skip 并说明** ——
      否则「无从判定」会被误读成「查不到」。
    """
    _require_reflection()
    must_exist, must_not = _notice_name_claims()
    assert must_exist or must_not, "没解析到任何可核的方法名论断 ⇒ 判据没生效（**不等于没问题**）"
    bad = []
    for n in sorted(must_exist):
        if not _reflection_has(n):
            bad.append("NOTICE 说 `%s` 是**官方真名**，而本机反射里**查不到它**" % n)
    for n in sorted(must_not):
        if _reflection_has(n):
            bad.append("NOTICE 说 `%s` **在官方反射里查不到**，而本机反射里**有它**" % n)
    assert not bad, "NOTICE 对第三方的方法名论断与官方反射不符：\n  - " + "\n  - ".join(bad)


def test_notice_name_claim_criterion_has_teeth():
    """★★ **负例**（事实 62）：把"真名"换成反射里没有的名字 ⇒ 判据必须报。

    ★ 用**临时文档**（monkeypatch `NOTICE`）⇒ **不动真文件**（轮 193 的教训）。
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "NOTICE.md"
        #: ① 真名**在**反射里 ⇒ 通过
        p.write_text("官方真名是 `InsertMoldPartingLine(Boolean)`。\n", encoding="utf-8")
        old = globals()["NOTICE"]
        globals()["NOTICE"] = p
        try:
            ex, notx = _notice_name_claims()
            assert ex == {"InsertMoldPartingLine"} and not notx, (ex, notx)
            assert all(_reflection_has(n) for n in ex)
            #: ② 真名**不在**反射里 ⇒ 必须报
            p.write_text("官方真名是 `InsertTotallyMadeUpName(Boolean)`。\n", encoding="utf-8")
            ex2, _ = _notice_name_claims()
            assert ex2 == {"InsertTotallyMadeUpName"}, ex2
            assert not _reflection_has("InsertTotallyMadeUpName"), "这个假名不该在反射里（负例前提）"
        finally:
            globals()["NOTICE"] = old

def test_reflection_guard_never_turns_unknown_into_false():
    """**负例**（事实 62）：**缺源必须抛**，不许静默 `False`（轮 197 修的那一条）。

    ⚠ 本项目的既有教训：**兜底会把「我不知道」变成「它有错」**（事实 113/114/115/116 那一族）。
      若 `_reflection_has` 在缺源时返回 `False`，那么"真名"那一半会**误报不成立** ——
      ★ 而**恰好在别的机器上**（没有 `D:/AI/SW/_raw`）才会发生，**最难被发现**。
    """
    old = globals()["REFLECT"]
    globals()["REFLECT"] = Path("D:/definitely/not/here/iface_sldworks.txt")
    try:
        with pytest.raises(RuntimeError) as ei:
            _reflection_has("InsertMoldPartingLine")
        assert "无从判定" in str(ei.value), "错误信息要说清是「无从判定」"
        #: 便携性守卫本身：缺源 ⇒ 抛 `Skipped`（**可见**，不是静默通过）
        with pytest.raises(pytest.skip.Exception):
            _require_reflection()
    finally:
        globals()["REFLECT"] = old
