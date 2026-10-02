"""@brief 交付报告数字新鲜度门禁的契约测试（**含负例**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_report_freshness_gate.py
# 定位:   给 `scripts/check_report_freshness.py`（轮 54 新增的**硬门禁**）补契约测试。
#         ⚠ 按本仓库纪律：**门禁必须有负例**（「一个存在但没人用的守卫与没有守卫等价」）。
#         依据是 2026-10-01 实测：`harvest-report.md` 的「偏离上游」落后 **8 倍/20 倍/10 倍**。
# 官方签名依据: 不适用（纯静态：读 markdown + 跑 git，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_report_freshness", ROOT / "scripts" / "check_report_freshness.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_report_freshness"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def test_current_report_is_fresh() -> None:
    """★ 当前 `harvest-report.md` 的那行数字必须与 git 相符（否则门禁该红）。"""
    assert MOD.main(["--repo", str(ROOT)]) == 0


def test_claimed_drift_parses_the_convention(tmp_path: Path) -> None:
    """约定写法（带千分位逗号）要能解析。"""
    p = tmp_path / "r.md"
    p.write_text("> 偏离上游：22 个文件 / +6,162 行 / -27 行 · 16 个 commit · 工作区 clean\n",
                 encoding="utf-8")
    got = MOD.claimed_drift(p)
    assert got == {"files": 22, "add": 6162, "delete": 27, "commits": 16}, got


def test_claimed_drift_returns_none_without_the_line(tmp_path: Path) -> None:
    """没有那行 ⇒ `None`（调用方据此 SKIP，不红）。"""
    p = tmp_path / "r.md"
    p.write_text("# 没有那行\n", encoding="utf-8")
    assert MOD.claimed_drift(p) is None


def test_missing_report_skips(tmp_path: Path) -> None:
    """★ **便携性守卫**：报告不在 ⇒ **SKIP（exit 0）**，不是 fail。"""
    assert MOD.main(["--repo", str(ROOT), "--report", str(tmp_path / "nope.md")]) == 0


def test_missing_origin_skips(tmp_path: Path) -> None:
    """★ **便携性守卫**：拿不到 `origin/main` ⇒ **SKIP（exit 0）**。

    用 `tmp_path` 当 repo（它不是 git 仓库，`git diff origin/main` 必失败）。
    """
    r = tmp_path / "not-a-repo"
    r.mkdir()
    p = tmp_path / "r.md"
    p.write_text("> 偏离上游：1 个文件 / +1 行 / -1 行 · 1 个 commit\n", encoding="utf-8")
    assert MOD.main(["--repo", str(r), "--report", str(p)]) == 0


def test_stale_number_is_reported(tmp_path: Path) -> None:
    """★ **负例**：数字对不上 ⇒ **exit 1**，且**报出是哪个字段** + 给出修法行。

    ⚠ 用真仓库当 `--repo`（能拿到 origin/main），只把**报告**换成一个假的小文件。
    """
    p = tmp_path / "stale.md"
    p.write_text("> 偏离上游：22 个文件 / +6,162 行 / -27 行 · 16 个 commit\n", encoding="utf-8")
    assert MOD.main(["--repo", str(ROOT), "--report", str(p)]) == 1


def test_actual_drift_measures_the_state_that_will_be_committed() -> None:
    """★★ **可用性守卫**：`actual_drift` 量的是「`git add -A && git commit` **之后**会变成什么」。

    ⚠ 这条判据**换过两次**，两次都是被实测打回来的（轮 54、轮 56）：
    ```
    ① 量 HEAD  ⇒ 有未提交改动时，按门禁给的数去写、**提交后必然又红一位**
       （轮 56 实测：门禁报 178/+126589，而我未提交的探针再加 1 文件/+153 行 ⇒ 提交后 179/+126742）
    ② dirty 判据用 `bool(files or untracked)` ⇒ **错**：
       `files` 是**相对 origin 的总漂移**（179，永远 > 0）⇒ `commits` **永远 +1** ⇒ 提交后又红
    ③ **正解（本条守的）**：`files/add/delete` 量工作树（含未跟踪文件的**行数**），
       `commits` = HEAD 的计数 **+（`git status --porcelain` 非空 ? 1 : 0）**
    ```
    ⚠ 它**没有**引入「改报告→数字变大→再改→又变大」的循环：
    改报告只改**行内容**、不改**行数** ⇒ 计数稳定 ⇒ **同长度替换一次写对即自洽**。
    """
    real = MOD.actual_drift(ROOT)
    # ① 必须有这几个键（含诊断用的）
    assert set(real) >= {"files", "add", "delete", "commits", "untracked", "dirty"}, real
    # ② 树干净 ⇒ commits 必须等于 HEAD 的计数（**不能 +1**）
    if not real["dirty"]:
        assert real["commits"] == real["head_commits"], (
            "树干净时 commits 不该 +1：%r" % real)
    # ③ 树脏 ⇒ commits = HEAD + 1（那次提交会让它 +1）
    else:
        assert real["commits"] == real["head_commits"] + 1, real
    # ④ `files` 是**总漂移**，与 `dirty` 无关（这正是 ② 那个 bug 的根）
    assert real["files"] > 0


# ══ 轮 199 加：**两个口径的文档必须互相指认**（防止它们悄悄分叉）════════════════

def test_gap_number_has_exactly_two_named_readings() -> None:
    """@brief ★★★ 「缺口数」有**两个口径**，两份文档必须**互相指认**且**各自标注**。

    ⚠ 轮 199 实测的病：同一个数（`339`）在两处被读成两件事 ——
      ```
      · `harvest-report.md` §10.3 的**判据更正**：那数是
        「四家以 MCP 工具暴露、而本仓库没有以 MCP 工具暴露」的操作数
        ⇒ 「**能力**缺口」≈ **0**（唯一真缺口是模具 1 个，已并入）
      · `union-gap-triage.md`（轮 86 起，四轮人工核）：拆四档后得到的是
        「**操作名**缺口」的数（**不是**能力缺口）
      ⇒ ★ 两处**都没错**，但**只看一处会读错**。
      ```
    ★ 所以判据是**结构性的**（而不是再写一个数）：**两份文档必须指认对方**。
      ⇒ ★★ 这与 `AGENTS.md §一 A2` 那条「① 与 ② 不是同一件事 …… 两条线不该混」同型，
        也与轮 191/192/193 那条主线同型：**能靠结构保证的，不要靠约定**。
    ⚠ 本测试**不复述那两个数** —— 数字会腐坏（事实 187/195），
      它只要求**指认关系**存在，并**指向**唯一权威。
    """
    report = (ROOT / "docs" / "harvest-report.md").read_text(encoding="utf-8")
    triage = (ROOT / "docs" / "union-gap-triage.md").read_text(encoding="utf-8")
    assert "union-gap-triage.md" in report, (
        "`harvest-report.md` 的缺口判据更正段必须**指向** `union-gap-triage.md`"
        "（否则读者会把「能力缺口」读成「操作名缺口」）")
    assert "harvest-report.md" in triage, (
        "`union-gap-triage.md` 必须**指向** `harvest-report.md` 的判据更正段")
    #: ★ 两边都要**明说口径**，而不只是互相链接（链接不能代替声明）
    assert "口径" in triage, "`union-gap-triage.md` 必须**明写它量的是哪个口径**"
    assert "能力" in report and "操作名" in report, (
        "`harvest-report.md` 的更正段要把两个口径**都说出来**")


def test_triage_snapshot_points_at_the_generated_number() -> None:
    """@brief ★★★ 分诊表的「算于」行是**历史快照** ⇒ 必须**指向生成物**（轮 200 加）。

    ⚠ 轮 200 实测的病：
      ```
      · `union-gap-triage.md` 的「算于」行（手写）：并集 **349** · 我们 **65** · 缺口 **339**
      · `union-coverage-matrix.md` 的「合计」行（**生成**）：并集 **424** · 缺 **338** · 独家 **75**
      ⇒ ★ 三个数**全不一样** —— 根因是轮 129 修掉了「暴露面被低估 20 个」的缺陷，
        修完后各数都变，**而那行手写快照没有跟着更新**。
      ★ 它**没有说谎**（明写「算于轮 86」= 快照语义），但**读者无法知道它已过期**。
      ```
    ★★ **判据（结构性）**：快照行必须**指认唯一权威**（生成物的合计行）。
      ⚠ **不要求两个数相等** —— 它们**本就不该相等**（一个历史、一个当前）；
        要求的是**读者能从快照行走到当前值**。
    ★ 而生成物那一侧**已经有门禁**：`check_union_conventions.py` 的 `check_map_fresh()`
      **重跑生成器并逐字比对** ⇒ ★ **复用已有的基础设施，不重造**（objective 约束）。
    """
    triage = (ROOT / "docs" / "union-gap-triage.md").read_text(encoding="utf-8")
    #: ① 快照行必须在
    assert "**算于**" in triage, "`union-gap-triage.md` 要有「算于」快照行"
    #: ⚑⚑ **判据范围必须限定在「算于」那一块之内**（轮 200 的负例当场证明过这一点）：
    #:   第一版断言「整篇 `triage` 含 `union-coverage-matrix.md`」——
    #:   ⚠ 而该文件名在本文件**别处也出现**（口径声明段就提到它）⇒
    #:   **把算于行的指向删掉，断言照样通过** ⇒ ★ 那个负例**什么都没证明**。
    #:   ⇒ ★ 与**事实 51** 同型：**分析范围要贴合代码/文档的组织单元**。
    blk = triage.split("**算于**", 1)[1]
    for stop in ("\n| 类", "\n## "):
        blk = blk.split(stop, 1)[0]
    assert "union-coverage-matrix.md" in blk, (
        "「算于」那一块里必须**指向** `union-coverage-matrix.md`（当前值唯一的家）"
        "—— 别处的提及不算")
    #: ③ 并且**明说它是快照/已过期**，不能让人误读成现值
    assert "快照" in blk or "已经不是当前值" in blk, (
        "快照行必须**明说**它是历史值、不是当前值")
    #: ④ 生成物那边确实有可读出的合计行（否则"指向"是空指）
    matrix = (ROOT / "docs" / "union-coverage-matrix.md").read_text(encoding="utf-8")
    assert "**合计**" in matrix, (
        "`union-coverage-matrix.md` 里要有一行「**合计**：…」供引用")


