"""★ 常驻弹窗监控的负例（★ 两条真 bug + 一条处置纪律）。

（★ 事实 62：判据要能被机器守住；★ 正例取 **git 里修复前那一版真实源码**）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方 KB（`QA00000299039` —— 框里自己写的那篇）
# 文件:   `tools/sw_dialog_watch.py`（常驻监控）· `tools/sw_guard.py`（判据与处置，被复用）
# 定位:   ★★★ 三条契约（★ 都来自 2026-10-04 用户当场点破的那次）：
#     ① ★★ **`needs_llm` / `forbidden` 一律不许自动点** —— ★ 只有 `auto` 才点
#        （★ 现场那个框是 `是/否/确定` ⇒ `needs_llm` ⇒ **只能记证、交 LLM 判**）✓
#     ② ★★ **pid 只聚焦、不排除**：★ 护栏原来写的是
#        `if pid is not None and p.value != pid: return True` —— ★★ 而 `run_guarded` 传的**永远是**
#        `SLDWORKS.exe` 的 pid ⇒ ★ **`star.exe` 拥有的弹窗被无条件跳过**（★ 实测 `count: 0`）✓
#        ★ 这条用 **git 里修复前的真源码** 自证：★ 判据在它上面**必须报**、在工作副本上**必须不报** ✓
#     ③ ★ **定点处置用 `PostMessage`**（★ 同步的 `SendMessage` 会挂在模态框的消息循环上 ——
#        真机实测 300 s）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_guard                                            # noqa: E402
import sw_dialog_watch as watch                            # noqa: E402


# ── ① 处置纪律：只有 auto 才点 ────────────────────────────────────────────

def _fake_dialog(title="Simulation", mode="auto", buttons=("确定",)):
    return ({"hwnd": 4242, "pid": 46240, "exe": "star.exe", "class": "#32770",
             "title": title, "hung": False,
             "controls": [{"class": "Button", "text": b} for b in buttons]},
            {"mode": mode, "why": "★ 测试"})


def _patch(monkeypatch, mode, *, dismiss_result=True):
    dlg, verdict = _fake_dialog(mode=mode)
    calls = {"dismiss": 0, "input": 0}
    monkeypatch.setattr(sw_guard, "scan_family_windows", lambda *a, **k: [dict(dlg)])
    monkeypatch.setattr(sw_guard, "classify_dialog", lambda *a, **k: dict(verdict))

    def _d(h):
        calls["dismiss"] += 1
        return dismiss_result

    monkeypatch.setattr(sw_guard, "dismiss", _d)
    monkeypatch.setattr(sw_guard, "dismiss_via_input", lambda h: calls.__setitem__("input", calls["input"] + 1) or True)

    class _U:
        @staticmethod
        def IsWindow(_h):
            return False

    monkeypatch.setattr(sw_guard, "_u", _U)
    return calls


def test_auto_tier_is_dismissed(monkeypatch):
    """★ `auto` 档 ⇒ **自动点掉**（★ 那才是"不让调用冻死"的那一档）。"""
    calls = _patch(monkeypatch, "auto")
    snap = watch.scan_now(dismiss=True)
    assert calls["dismiss"] == 1, calls
    assert snap["rows"][0]["dismissed"] is True, snap
    assert snap["pending_needs_llm"] == 0


def test_needs_llm_is_never_dismissed(monkeypatch):
    """★★★ **核心纪律：`needs_llm` 一个都不许点**（★ 现场那个是/否框就是这一档）。"""
    calls = _patch(monkeypatch, "needs_llm")
    snap = watch.scan_now(dismiss=True)
    assert calls["dismiss"] == 0 and calls["input"] == 0, calls
    assert snap["pending_needs_llm"] == 1, snap
    assert snap["rows"][0]["needs_llm"] is True
    assert snap["rows"][0]["controls"], "★ 证据（控件文本）必须留下来"


def test_forbidden_tier_is_never_dismissed(monkeypatch):
    """★★ **`forbidden` 档同样不许点**（★ 危险词：删除/覆盖/不可逆…）。"""
    calls = _patch(monkeypatch, "forbidden")
    snap = watch.scan_now(dismiss=True)
    assert calls["dismiss"] == 0, calls
    assert snap["pending_needs_llm"] == 1, snap


# ── ② pid 只聚焦、不排除（★ 用 git 里的修复前源码自证）──────────────────

#: ★ 被否定的形态：**裸的精确 pid 过滤**（★ 家族进程的窗口会被它跳过）
REFUTED = re.compile(r"if\s+pid\s+is\s+not\s+None\s+and\s+p\.value\s*!=\s*pid\s*:\s*\n\s*return\s+True")


def _has_bare_pid_filter(src: str) -> bool:
    return bool(REFUTED.search(src))


def test_the_refuted_pid_filter_is_detectable_in_the_pre_fix_source():
    """★★★ **负例自证**（★ 事实 62 的手法）：★ 拿 **HEAD（修复前）** 的 `sw_guard.py`
    跑这条判据 ⇒ **必须报**；★ 工作副本 ⇒ **必须不报** ✓

    ★ 为什么这条重要：★ 那个过滤器的后果是**整个弹窗机制静默失效**
      （★ 实测：`scan_family_windows(49384)` 对 `star.exe` 的框回 **0**）——
      ★★ 而它**看起来完全合理**（"只看我们那个进程的窗口"），★ 极易被后人再写回来 ✓
    """
    head = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:tools/sw_guard.py"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert head.returncode == 0 and head.stdout, "★ 取不到 HEAD 版本 ⇒ 这条自证不成立"
    assert _has_bare_pid_filter(head.stdout), "★ 判据在**修复前**的源码上没报 ⇒ 它抓不到那个 bug"
    now = (ROOT / "tools" / "sw_guard.py").read_text(encoding="utf-8")
    assert not _has_bare_pid_filter(now), "★ 修复后的源码里**又出现**了裸 pid 过滤"


def test_family_escape_keeps_other_family_process_dialogs_visible():
    """★ 契约：判据必须留"**同族进程放行**"的口子（★ 否则 `star.exe` 的框又会不见）。"""
    src = (ROOT / "tools" / "sw_guard.py").read_text(encoding="utf-8")
    assert "not sw_family_window(h)" in src, "★ 没有家族放行的口子"
    assert src.count("not sw_family_window(h)") >= 2, "★ 两处扫描路径（主路径 + 兜底）都要有"


# ── ③ 定点处置：PostMessage 而非 SendMessage ──────────────────────────────

def test_targeted_dismiss_uses_post_message_not_send_message():
    """★★ 真机教训（事实 292/376）：★ **`SendMessage` 会挂在模态框的消息循环上（实测 300 s）**
    ⇒ ★ 定点处置必须走 `PostMessage` ✓
    """
    src = (ROOT / "tools" / "sw_guard.py").read_text(encoding="utf-8")
    i = src.find("def dismiss_button")
    assert i > 0, "★ 找不到 `dismiss_button`"
    body = src[i:i + 1800]
    assert "PostMessageW" in body, "★ 定点处置没有用 PostMessage"
    assert "SendMessageW" not in body, "★ 定点处置里出现了同步的 SendMessage"


def test_watcher_status_readback_shape():
    """★ 状态要**读得回来**（★ "监控在不在跑"必须是可查的，不能靠猜）。"""
    st = watch.status()
    for k in ("watcher_pidfile", "watcher_alive", "events_file", "events_lines"):
        assert k in st, "★ 状态里少了 %s" % k
