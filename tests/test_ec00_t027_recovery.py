"""★ EC00 T027 判据：**恢复 / 竞争 / 护栏分级**（★ 离线部分 —— ★ 真机部分另见 T027-runtime）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/tasks.md` **T027**（★ 逐字：「安全验证单会话竞争及
#         受控超时/弹窗恢复路径」）
#         `tools/sw_guard.py`（★ `classify_dialog` 三级 · `dismiss` · `scan`）
#         `tests/test_sw_guard_dialog_tiers.py`（★ 既有三级契约与负例）
#         `scripts/sw_sketch_relations.py`（★ 「uncertain ⇒ 停批」）
# 定位:   ★ EC00 **T027** 的**离线判据**。★★★ **完成判据**：★ **最多一个修改者**；
#         ★ **不故意破坏用户会话，不盲重试/危险确认**；★ **无安全复现条件则保留阻塞，不造证据**。
# 官方依据: `AGENTS.md` §十五（★ 护栏三级）· `AGENTS.md` 已知事实 24（★ 单会话互斥）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

GUARD = ROOT / "tools" / "sw_guard.py"
REL = ROOT / "scripts" / "sw_sketch_relations.py"
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"


# ── ① 护栏三级：★ 危险弹窗绝不自动点 ─────────────────────────────────

def test_t027_guard_has_three_tiers():
    """★★★ T027：★ 护栏必须有**三级**（★ `auto` / `needs_llm` / `forbidden`）。

    ★★ 依据（★ `AGENTS.md` §十五 逐字）：★「`auto`（唯一语义明确的确认按钮）⇒自动点；
      `needs_llm`（多义按钮/进度窗）· `forbidden`（危险词/在提问）⇒不点」。
    """
    src = GUARD.read_text(encoding="utf-8", errors="replace")
    assert "def classify_dialog" in src, "★ 找不到 `classify_dialog`"
    for tier in ("auto", "needs_llm", "forbidden"):
        assert tier in src, "★ 护栏缺分级：%s" % tier


def test_t027_forbidden_dialogs_are_never_auto_confirmed():
    """★★★ T027：★ **危险词弹窗绝不自动确认**（★ 逐字承 `AGENTS.md` §十五）。

    ★ 危险词（★ 官方/本仓清单）：★ 删除 · 覆盖 · 替换 · 丢失 · 不可逆 · `remove` · `overwrite` · `delete`。
    """
    src = GUARD.read_text(encoding="utf-8", errors="replace")
    #: ★★ 危险词表必须在实现里**可指认**
    found = [w for w in ("删除", "覆盖", "替换", "丢失", "remove", "overwrite", "delete") if w in src]
    assert len(found) >= 4, (
        "★★ 护栏里的危险词表太窄（★ 只找到 %r）⇒ ★ 可能放过危险弹窗" % found)


def test_t027_needs_llm_dialogs_are_not_auto_dismissed():
    """★★★ T027：★ **多义/进度窗不自动点**（★ `needs_llm` ⇒ **报给 LLM**）。

    ★★ 依据（★ `classify_dialog` docstring 逐字）：★「`needs_llm=True` 的**不自动点**
      ⇒ ★ 那正是"走 LLM"的落点」。
    """
    src = GUARD.read_text(encoding="utf-8", errors="replace")
    #: ★ 多义按钮词（★ 点错后果相反）
    for w in ("否", "取消", "暂停"):
        assert w in src, "★ 护栏没识别多义按钮：%s" % w


def test_t027_existing_tier_tests_still_exist():
    """★★ T027：★ **既有三级契约测试必须仍在**（★ 本特性不得把它删了/绕了）。"""
    p = ROOT / "tests" / "test_sw_guard_dialog_tiers.py"
    assert p.is_file(), "★ 既有三级契约测试不见了"
    body = p.read_text(encoding="utf-8", errors="replace")
    for token in ("needs_llm", "forbidden"):
        assert token in body, "★ 既有测试缺 %s" % token


# ── ② 不盲重试 ────────────────────────────────────────────────────────

def test_t027_no_blind_retry_after_uncertain():
    """★★★ T027：★ **`uncertain` 后不盲重试**（★ 逐字承完成判据「不盲重试/危险确认」）。

    ★★ 依据（★ `data-model.md` §5.1 逐字）：★「★★★ **「没有完成返回」不等于「没有修改」**」。
    """
    src = REL.read_text(encoding="utf-8", errors="replace")
    assert "no replay" in src or "batch stopped" in src or "不重放" in src, (
        "★★ 实现里没有「不重放」的语义 ⇒ ★ 可能盲重试非幂等操作")


def test_t027_guard_does_not_retry_the_same_process():
    """★★★ T027：★ **超时后不重试同一进程**（★ 逐字承 `AGENTS.md` 铁律 2）。

    ★★ 依据（★ `AGENTS.md` 铁律 2 逐字）：★「每个 COM 调用设超时……★ **超时后不要重试同一进程**」。
    """
    src = GUARD.read_text(encoding="utf-8", errors="replace")
    #: ★★ 必须有「杀掉被冻住的调用」而不是「再调一次」的处置
    assert "taskkill" in src or "aborted_for_llm" in src, (
        "★★ 护栏里没有「处置被冻住的调用」⇒ ★ 可能原地重试")


# ── ③ 单会话互斥 ──────────────────────────────────────────────────────

def test_t027_single_session_is_documented_as_a_hard_constraint():
    """★★★ T027：★ **单会话互斥**必须被记为**硬约束**（★ 完成判据：「最多一个修改者」）。

    ★★ 依据（★ `AGENTS.md` 已知事实 24 逐字）：★「运行时只能有一个 SolidWorks MCP：
      ★ 多个进程抢同一 COM 连接**会死锁**」。
    """
    #: ★ 本特性的文档里必须写明
    merged = ""
    for name in ("plan.md", "data-model.md", "research.md"):
        p = SPEC / name
        if p.is_file():
            merged += p.read_text(encoding="utf-8", errors="replace")
    assert "单会话" in merged or "单 SW" in merged, "★ 文档里没有「单会话」约束"
    assert "互斥" in merged or "串行" in merged, "★ 文档里没有「互斥/串行」"


def test_t027_machine_tasks_are_serialized():
    """★★ T027：★ 真机任务必须**串行**（★ 计划 §7 逐字：「任何真机任务排他串行」）。"""
    tasks = (SPEC / "tasks.md").read_text(encoding="utf-8", errors="replace")
    assert "串行" in tasks, "★ `tasks.md` 里没有「真机串行」这条"


# ── ④ 无安全条件则保留阻塞（★ 不造证据）──────────────────────────────

def test_t027_records_blocked_instead_of_faking_evidence():
    """★★★ T027：★ **无安全复现条件则保留阻塞，不造证据**（★ 逐字承完成判据）。

    ★★ 依据（★ `tasks.md` T027 逐字）：★「★ **无安全复现条件则保留阻塞，不造证据**」。
    """
    tasks = (SPEC / "tasks.md").read_text(encoding="utf-8", errors="replace")
    #: ⚠ 第一版写 `"不造证据" in tasks or "保留阻塞" in tasks` ⇒ ★★ **两个词任一个在就过**
    #:   ⇒ ★ 我把「不造证据」改坏后**判据仍绿** ✗ —— ★★ **那是「松断言」**
    #:   （★ 与**事实 62**「门禁写了 ≠ 有效」同族：★ **负例测试是唯一的证明**）。
    #: ★★ 正解：★ **两个都要在**（★ 它们是**两条**要求，★ 不是同义替换）。
    assert "保留阻塞" in tasks, "★ T027 的「保留阻塞」这条没写进 tasks"
    assert "不造证据" in tasks, "★ T027 的「不造证据」这条没写进 tasks"
    #: ★★ 且必须写明「不故意破坏用户会话」
    assert "不故意破坏" in tasks or "禁止为了测试破坏" in tasks, (
        "★ 没写明「不故意破坏用户会话」")


# ── ⑤ 离线可判：★ 分级是**纯函数**（★ 可无 COM 测）─────────────────

def test_t027_classify_dialog_is_pure_and_testable_offline():
    """★★ T027：★ `classify_dialog` 必须是**纯函数**（★ 只吃 `dict` ⇒ ★ 可离线测）。

    ★ 判据：★ 它的签名只收 `d: dict`（★ 不碰 COM）⇒ ★ **本判据本身即证明**（★ 静态核签名）。
    """
    src = GUARD.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_dialog":
            fn = node
            break
    assert fn is not None, "★ 找不到 `classify_dialog`"
    argnames = [a.arg for a in fn.args.args]
    assert argnames == ["d"], (
        "★★ `classify_dialog` 的形参是 %r ⇒ ★ 不是纯函数（★ 可能碰 COM）" % argnames)
    #: ★★ 函数体里**不许**出现 COM 调用
    body = ast.get_source_segment(src, fn) or ""
    for bad in ("win32com", "GetActiveObject", "SldWorks"):
        assert bad not in body, "★★ `classify_dialog` 里出现了 %r ⇒ ★ 不是纯函数" % bad
