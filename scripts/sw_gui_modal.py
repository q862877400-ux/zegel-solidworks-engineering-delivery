r"""模态弹窗检测与处置 —— 本项目 GUI 自动化的**前置断言**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 定位:   嘉立创 FA 插件 GUI 自动化的**第一道关卡**。

# ⚑⚑⚑ 为什么必须有这个模块（连续九轮失败的真正根因）
# -----------------------------------------------------------
# 现象：点 ComboBox 后按 Alt+↓ / ↓ / Enter **一律无效**，进度条恒为 42%。
# 真因：**插件弹出了一个模态提示框（「请先完成当前产品的选型」），
#       而那个框**没有焦点**。Windows 的输入队列只投递给**前台窗口**，
#       于是所有按键都发给了 SolidWorks 主窗口 —— 插件压根没收到。
# 我把这个误判成「自绘控件读不到选项」，换了三种后端、四种滚法，
# 全部在错因上打转。
#
# ⚑⚑ 之前的三个叠加错误
# ① **PrintWindow 只抓窗口自身**，客户区之外的独立顶层浮窗**全部丢失**
#    ⇒ 我截的每张图里都没有那个弹窗 ⇒ 「肉眼看」永远看不到。
#    ⇒ 取证必须 ``ImageGrab.grab()``（整屏）。
# ② 窗口筛选只认「标题含 SOLIDWORKS」或「进程名 sldworks.exe」，
#    而插件模态框 **标题为空** ⇒ 两道过滤都漏掉。
#    ⇒ 检测**不看标题、不看进程名**，只看结构特征。
# ③ **点完从不验「是否生效」** —— 把「被弹窗拦住」误判成「控件不响应」。
#    ⇒ 每个动作后必须断言结果（见 assert_no_modal）。
#
# ⚑ 判据（本机实测）
#     cls  = ``#32770``   标准 Win32 对话框类
#     title = ``''``      空标题
#     owner != 0          有属主窗口 ⇒ 是对话框而非工具窗
#     同进程 + 独立顶层 + 尺寸合理 ⇒ 候选
# 实测命中：``hwnd=4983664 cls=#32770 title='' owner=6556410
#            rect=(1538,478,1766,680)``

# 覆盖:   后续同级定义
# ⚠ 本模块只做检测与关窗，不操作 SolidWorks 模型。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import time
from typing import Any

import win32con
import win32gui
import win32process

__all__ = [
    "find_modals",
    "modal_report",
    "assert_no_modal",
    "close_modals",
    "screen_png",
]

_DIALOG_CLASSES = ("#32770",)


def find_modals(main_hwnd: int) -> list[dict[str, Any]]:
    """找出同进程、与主窗口分离的**可见顶层对话框**。

    ⚠ 不依赖标题、不依赖进程名 —— 插件的提示框标题为空。
    """
    main_pid = win32process.GetWindowThreadProcessId(main_hwnd)[1]
    out: list[dict[str, Any]] = []

    def cb(h, _):
        if h == main_hwnd or not win32gui.IsWindowVisible(h):
            return
        if win32process.GetWindowThreadProcessId(h)[1] != main_pid:
            return
        r = win32gui.GetWindowRect(h)
        if (r[2] - r[0]) < 60 or (r[3] - r[1]) < 40:
            return
        cls = win32gui.GetClassName(h)
        if cls not in _DIALOG_CLASSES and not win32gui.GetWindow(h, 4):
            return
        out.append(
            {
                "hwnd": h,
                "title": win32gui.GetWindowText(h),
                "cls": cls,
                "rect": r,
                "owner": win32gui.GetWindow(h, 4),
            }
        )

    win32gui.EnumWindows(cb, None)
    return out


def modal_report(main_hwnd: int) -> dict[str, Any]:
    ms = find_modals(main_hwnd)
    return {"count": len(ms), "dialogs": ms}


def assert_no_modal(main_hwnd: int, where: str = "") -> None:
    """★ 每个动作**之前**调用：发现弹窗就抛，不让它吃掉后续输入。"""
    rep = modal_report(main_hwnd)
    if rep["count"]:
        d = rep["dialogs"][0]
        raise RuntimeError(
            "%s 有模态弹窗挡着（hwnd=%d cls=%s rect=%s）—— "
            "输入会全部发给主窗口而插件收不到；先 close_modals()"
            % (where or "操作前", d["hwnd"], d["cls"], d["rect"])
        )


def close_modals(main_hwnd: int, rounds: int = 5) -> int:
    """关掉所有模态框，返回关掉几个。

    顺序经过实测：**置前台 → WM_COMMAND(IDOK) → 回车 → Esc**。
    ⚠ 单纯鼠标点击在弹窗无焦点时**无效**（实测过）。

    ⚠⚠ **2026-10-01 轮 62 修两处**（原来的形态会让**修饰键/回车卡在按下态**）：
    1. `VK_MENU` 的按下与抬起**都在 `try` 内**、外层 `except Exception: pass`
       ⇒ `SetForegroundWindow` 或 `sleep` 抛异常时 **Alt 永不抬起**；
    2. `for vk in (VK_RETURN, VK_ESCAPE)` 是**裸 `keybd_event`**（按下 → sleep → 抬起，无 `finally`）
       ⇒ **Enter / Esc 卡在按下态**。⚠ 这是「**忽然回车**」最可能的出处：
       本函数**每轮发 Enter+Esc、最多 `rounds=5` 轮**。
    ⇒ 现在**全部**走 `sw_gui_input` 的异常安全原语（抬起在 `finally` 里）。
    """
    import win32api

    from scripts import sw_gui_input as _gi

    closed = 0
    for _ in range(rounds):
        ds = find_modals(main_hwnd)
        if not ds:
            break
        dh = ds[0]["hwnd"]
        # Alt 置前台：按下与抬起分别包在 try / finally 里
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        try:
            time.sleep(0.1)
            win32gui.SetForegroundWindow(dh)
            time.sleep(0.25)
        except Exception:
            pass
        finally:
            try:
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass
            time.sleep(0.3)
        win32gui.PostMessage(dh, win32con.WM_COMMAND, 1, 0)  # IDOK
        time.sleep(0.5)
        for vk in (win32con.VK_RETURN, win32con.VK_ESCAPE):
            # ⚠ 走原语 ⇒ 中途异常也不会把 Enter/Esc 留在按下态
            _gi._press(vk, pause=0.35)
        if not find_modals(main_hwnd):
            closed += 1
    return closed


def screen_png(path: str) -> Any:
    """★ 取证一律用**整屏**；PrintWindow 会丢掉客户区外的浮窗。"""
    from PIL import ImageGrab

    img = ImageGrab.grab()
    img.save(path)
    return img
