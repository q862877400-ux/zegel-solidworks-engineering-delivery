r"""DPI 自适应点击 —— 换显示器/改缩放都不失效。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测驱动）
# 定位:   解决「换显示器 / 改 DPI 缩放 ⇒ 坐标全错 ⇒ 点空」。

# ⚑⚑⚑ 本机实测的故障（2026-09-30 晚）
# ------------------------------------------------------------------
#   系统报告屏幕   2048x1152
#   SolidWorks 窗口 2560x1380          ← 1.25 倍 DPI 缩放
#   控件树报的「返回」 rect (1104,1308)-(2559,1354)   ← 容器**底部**
#   但截图里「返回」在**左上角** ≈(888,175)
# ⇒ **控件树给的 rect 与屏幕像素不是同一坐标系**。
# ⇒ 我按 rect 中心点去 ``SetCursorPos``，**落点偏到别处** ⇒ 点「返回」没反应、
#   点卡片不中。**此前若干次「控件不响应」的真凶就是它**，我误判成控件坏了。

# ⚑ 两条自适应做法（本模块实现）
# ------------------------------------------------------------------
# ① **优先用控件自己的 ``click_input()``** —— pywinauto 内部按控件自己的
#    可访问性接口投递，**不做屏幕坐标换算** ⇒ DPI/多显示器全都免疫。
# ② 实在要坐标时（例如点下拉列表里的某一项，那是**独立窗口**没有控件对象），
#    用 ``ClientToScreen`` 把**客户区坐标**换成屏幕坐标，而不是想当然地
#    把 rect 当屏幕坐标。

# 覆盖:   后续同级定义
# ⚠ 本模块只管「怎么点」，不管「点什么」。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import win32api
import win32con
import win32gui

warnings.filterwarnings("ignore")


def dpi_of(hwnd: int) -> int:
    """窗口的 DPI（96 = 100%）。取不到按 96。"""
    try:
        return int(win32gui.GetDpiForWindow(hwnd)) or 96
    except Exception:
        try:
            win32api.SetProcessDPIAware()
            return 96
        except Exception:
            return 96


def click_control(ctrl, pause: float = 0.6) -> bool:
    """★ 首选：让控件自己点自己。**不做屏幕坐标换算** ⇒ DPI 免疫。

    ⚠ 实测某些自绘控件 ``click_input()`` 无效（ComboBox 就是），
      那种情况调用方再退回 ``click_point()``。
    """
    try:
        ctrl.click_input()
        time.sleep(pause)
        return True
    except Exception:
        return False


def click_point(x: int, y: int, pause: float = 0.5) -> None:
    """在**屏幕坐标** (x, y) 点一下。"""
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def click_rect(ctrl_rect, pause: float = 0.6) -> None:
    """点控件矩形的中心。

    ⚠ 这里**假定 ``rect`` 就是屏幕坐标**。若发现落点偏，
       优先改用 ``click_control(ctrl)``，不要在这里手算缩放。
    """
    x = (ctrl_rect.left + ctrl_rect.right) // 2
    y = (ctrl_rect.top + ctrl_rect.bottom) // 2
    click_point(x, y, pause)


def client_to_screen(hwnd: int, x: int, y: int) -> tuple[int, int]:
    """客户区坐标 -> 屏幕坐标（DPI 正确）。"""
    return win32gui.ClientToScreen(hwnd, (int(x), int(y)))


def verify_click_landed(ctrl, before: str, tries: int = 3) -> bool:
    """点完**验证是否生效**：读控件值/文字，和点前比。

    ⚠ 这是「操作到底生不生效」的唯一可靠判据 —— 本项目反复栽在
      「代码执行了 ≠ 操作生效了」。
    """
    for _ in range(tries):
        click_control(ctrl)
        time.sleep(0.5)
        try:
            after = ctrl.selected_text() if hasattr(ctrl, "selected_text") \
                else ctrl.window_text()
        except Exception:
            after = None
        if after and after != before:
            return True
    return False
