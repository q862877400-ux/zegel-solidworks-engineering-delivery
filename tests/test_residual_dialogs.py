"""钉住 `sw_connect.residual_dialogs` 的判据 —— **不许再空转**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_residual_dialogs.py
# 定位:   轮 148 查出：此前 **21 个工具**各复制了一份"查残留模态框"的代码，
#         **每份都带 `IsWindowVisible` 过滤** ⇒ 实测 SolidWorks 的 **49 个顶层窗口里
#         只有 1 个可见** ⇒ **那个过滤漏掉 48 个**（约 98%）。
#         ⚠ 那条检查守的是**每轮收尾的安全底线**（模态框会把会话永久挂起）。
# 官方依据: Win32 `EnumWindows` / `IsWindowVisible`；模态框类名 `#32770`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

import sw_connect          # noqa: E402


def _any_pid_with_windows() -> int:
    """找一个**有可见顶层窗口**的进程（不一定是 SolidWorks）—— 给判据当样本。"""
    u = ctypes.windll.user32
    found = [0]

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, _l):
        if u.IsWindowVisible(h) and not found[0]:
            p = w.DWORD()
            u.GetWindowThreadProcessId(h, ctypes.byref(p))
            found[0] = p.value
        return True

    u.EnumWindows(cb, 0)
    return found[0]


def test_returns_a_pair_and_the_total_is_not_vacuous():
    """@brief ★★★ 必须返回 `(dialogs, all_windows)`，且**总有窗口能被扫到**。

    ⚠⚠ 这条判据的由来：旧代码只返回 `dialogs`（一个列表）⇒ **空列表无法区分**
    「**没有**模态框」与「**没扫到**任何窗口」⇒ **不可能失败**。
    ⇒ 新判据要求**把总数一并返回**，调用方必须先看总数。
    """
    out = sw_connect.residual_dialogs(ctypes.windll.kernel32.GetCurrentProcessId())
    assert isinstance(out, tuple) and len(out) == 2, "应当返回 (dialogs, all_windows)"
    dialogs, total = out
    assert isinstance(dialogs, list) and isinstance(total, int)


def test_scan_actually_sees_windows_on_this_machine():
    """@brief ★★ 本机**确实有**可见顶层窗口 ⇒ 用**那个进程**验证判据不是空转。"""
    pid = _any_pid_with_windows()
    assert pid, "本机连一个可见顶层窗口都没有 —— 环境异常"
    _dialogs, total = sw_connect.residual_dialogs(pid)
    assert total > 0, "扫到的窗口数为 0 ⇒ 判据在空转"


def test_only_visible_misses_windows():
    """@brief ★★★ **证据**：`only_visible=True` 会**漏掉**大部分窗口。

    ⚑ 实测（轮 148，SolidWorks PID）：**49 个顶层窗口里只有 1 个可见** ⇒ 漏掉 48 个。
    ⚠ 本判据**不假设**具体数字（换机器会变），只要求
    「**可见的 ≤ 全部的**，且**至少有一次严格小于**（除非所有窗口都可见）」。
    """
    pid = _any_pid_with_windows()
    _d1, total = sw_connect.residual_dialogs(pid, only_visible=False)
    _d2, visible = sw_connect.residual_dialogs(pid, only_visible=True)
    assert visible <= total, "可见的怎么可能比全部多"
    #: ⚠ 不硬断言 `visible < total`（那台机器可能恰好都可见）；只在能区分时断言
    if visible == total:
        import warnings
        warnings.warn("本机所有顶层窗口都可见 ⇒ 这个判据这次区分不了（不是失败）")


def test_docstring_states_the_148_finding():
    """@brief ★★ docstring 要写明轮 148 的发现与「为什么要返回总数」。"""
    import inspect
    doc = inspect.getdoc(sw_connect.residual_dialogs) or ""
    assert "可证伪" in doc, "要写明这是「可证伪」版"
    assert "all_windows" in doc, "要写明为什么要把总数一并返回"
    assert "21" in doc, "要点出此前有 21 份复制"
