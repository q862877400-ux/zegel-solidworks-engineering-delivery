# -*- coding: utf-8 -*-
"""步骤 3：回车搜索 -> 等结果 -> 截图。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api
import win32con
import win32gui
import jlc_auto as J

hwnd = J.sw_window()
r = J.ensure_window(hwnd)
J.log("窗口 %dx%d 前台=%d" % (r[2] - r[0], r[3] - r[1], win32gui.GetForegroundWindow()))
J.log("按回车")
win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
time.sleep(0.1)
win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
J.log("等 6 秒看结果…")
for i in range(6):
    time.sleep(1.0)
    r2 = J.ensure_window(hwnd)
    J.log("  %ds  窗口 %s 标题=%r" % (i + 1, (r2[2] - r2[0], r2[3] - r2[1]),
                                       win32gui.GetWindowText(hwnd)[:46]))
_root, rect = J.tab_column(hwnd)
r2 = J.ensure_window(hwnd)
J.snap("s3_search", box=(rect.right - 4, rect.top - 16,
                         min(r2[2], rect.right + 470), min(r2[3], rect.top + 760)))
J.log("截图 s3_search_z.png")
