# -*- coding: utf-8 -*-
"""点「滑块数量」下拉框，展开选项并截图。"""
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
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.12)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.4)
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 「滑块数量」的 [请选择 ▼]：裁剪图里约 (315, 344)；原点 (rect.right-4, rect.top-16)
CX = rect.right - 4 + 315
CY = rect.top - 16 + 344
J.log("点「滑块数量」下拉 (%d,%d)" % (CX, CY))
J.click(CX, CY, pause=1.0)
time.sleep(0.8)
# 下拉列表通常在控件下方弹出，截整个下半部分
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("u6_dropdown", box=(rect2.right - 4, rect2.top - 16,
                          min(r[2], rect2.right + 560), min(r[3], rect2.top + 700)))
J.log("完成，看 u6_dropdown_z.png")
