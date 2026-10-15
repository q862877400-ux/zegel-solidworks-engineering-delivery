# -*- coding: utf-8 -*-
"""先给内容区焦点，再滚；并试几种滚法。"""
import ctypes
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api
import win32con
import win32gui
import jlc_auto as J

ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
J.ensure_window(hwnd)
# 焦点放到窗口前台
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.12)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.5)

_root, rect = J.tab_column(hwnd)
# 点参数列表里的空白处（不点控件，只给列表区焦点）
CX = rect.right - 4 + 250
CY = rect.top - 16 + 690          # 「代码」下方那块空白
J.log("点列表空白处 (%d,%d)" % (CX, CY))
J.click(CX, CY, pause=1.0)
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("u4_focus", box=(rect2.right - 4, rect2.top - 16, r[2], r[3]))

# 逐种滚法各试一次，每次后截图
for i, (tag, amount) in enumerate((("wheel-5", -5), ("wheel-20", -20),
                                   ("PageDown", "pg"), ("End", "end")), 1):
    if tag.startswith("wheel"):
        J.wheel(rect.right + 200, rect.top + 300, amount, pause=1.0)
    elif tag == "pg":
        win32api.keybd_event(win32con.VK_NEXT, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_NEXT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.0)
    else:
        win32api.keybd_event(win32con.VK_END, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_END, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1.2)
    r2 = J.ensure_window(hwnd)
    _root, rect3 = J.tab_column(hwnd)
    J.snap("u5_%s" % tag, box=(rect3.right - 4, rect3.top - 16, r2[2], r2[3]))
    J.log("  %s 完成" % tag)
J.log("对比 u5_wheel-5 / u5_PageDown / u5_End 哪张内容不同")
