r"""GUI 焦点守卫 —— 每个动作之前强制检查并修复输入焦点。

# ── 来源 ─────────────────────────────────────────────────────────────
# 定位:   嘉立创 FA 插件 GUI 自动化的**前置关卡**，与 sw_gui_modal 配套。

# ⚑⚑⚑ 为什么必须有（本项目连续九轮失败的真正根因）
# -----------------------------------------------------------
# 现象：点 ComboBox 后按 Alt+↓ / ↓ / Enter **一律无效**，进度条恒为 42%。
# 真因：插件弹出模态提示框「请先完成当前产品的选型」，而**那个框没有焦点**。
#       Windows 的输入队列**只投递给前台窗口**，于是按键全部发给 SolidWorks
#       主窗口，插件压根没收到 —— 表现却是「控件不响应」。
# 我把它误判成「自绘控件读不到选项」，先后换了 UIA / win32(MSAA) 两种后端、
# 四种滚法、坐标与控件两种定位，全部打在错因上。
#
# ⚑⚑ 焦点问题的三条长效规则（本模块实现）
# -----------------------------------------------------------
# ① **每次动作前**断言前台窗口 == 期望窗口；不是就修复（置前 + 校验）
# ② **每次动作后**断言焦点没被弹窗/浮窗抢走；被抢就关掉再继续
# ③ **焦点可能丢**在「按键发送」这个动作本身之前（点击会把焦点带走），
#    ⇒ 断言要放在**动作前**，不是动作后。
#
# ⚑ 实测有效的置前手法（pywinauto 的 set_focus() 在这里**不可靠**）
#     按住 Alt 再 SetForegroundWindow —— 绕过 Win32 的前台锁。
#     实测：`set_focus()` 后 GetForegroundWindow() 仍是别的窗口；
#           加 Alt 后一次成功。

# 覆盖:   后续同级定义
# ⚠ 本模块只管焦点，不操作 SolidWorks 模型。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
import time
from typing import Any

import win32api
import win32con
import win32gui

__all__ = ["foreground", "ensure_focus", "assert_focus", "focus_state"]


def foreground() -> int:
    """当前前台窗口句柄。"""
    return win32gui.GetForegroundWindow()


def focus_state(want: int) -> dict[str, Any]:
    fg = foreground()
    return {
        "want": want,
        "got": fg,
        "ok": fg == want,
        "title": win32gui.GetWindowText(fg)[:60] if fg else "",
    }


def ensure_focus(hwnd: int, retries: int = 3, settle: float = 0.3) -> bool:
    """把 ``hwnd`` 置为前台并**回读确认**；返回是否真的成功。

    ⚠ 不用 pywinauto 的 ``set_focus()`` —— 实测它在这里不可靠
      （调用后 GetForegroundWindow() 仍不是目标窗口）。
    ⚠ Win32 前台锁：直接 SetForegroundWindow 常被拒，
      常规绕法是**按住 Alt** 再调（见下）。
    ⚠⚠ **2026-10-01 轮 62 修**：原来 Alt 的按下与抬起**都在 `try` 内**、外层 `except: pass`
      ⇒ 任一步抛异常（含 `KeyboardInterrupt`）时 **Alt 永不抬起** ⇒ **Alt 卡在按下态**
      （菜单栏被激活、后续按键被吃掉）。⇒ 现在抬起在 **`finally`** 里。
    """
    for _ in range(retries):
        if foreground() == hwnd:
            return True
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        try:
            time.sleep(0.1)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(settle)
        except Exception:
            pass
        finally:
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass
            time.sleep(settle)
    return foreground() == hwnd


def assert_focus(hwnd: int, where: str = "") -> None:
    """★ 每个动作**之前**调用。焦点不对就修复，**修不好就抛**。

    ⚠ 为什么不自动修完就算了 —— 实测有修不回来的情形，
      静默继续会导致「操作全被丢弃」且**无从察觉**（本项目踩了九轮）。
    """
    if foreground() == hwnd:
        return
    st = focus_state(hwnd)
    if ensure_focus(hwnd):
        return
    raise RuntimeError(
        "%s 焦点丢失且修复失败：期望 hwnd=%d，实际前台=%d(%r)"
        % (where or "操作前", st["want"], st["got"], st["title"])
    )
