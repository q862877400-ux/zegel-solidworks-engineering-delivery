# -*- coding: utf-8 -*-
"""用右侧滚动条滑块往下翻。"""
import ctypes
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
import jlc_auto as J

ctypes.windll.user32.SetProcessDPIAware()

hwnd = J.sw_window()
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
SX = rect.right - 4 + 505
y_from = rect.top - 16 + 600
y_to = rect.top - 16 + 300
J.log("拖滚动条 x=%d  %d -> %d" % (SX, y_from, y_to))
J.drag(SX, y_from, SX, y_to, steps=14)
time.sleep(1.2)
r2 = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("u3_dragscroll", box=(rect2.right - 4, rect2.top - 16, r2[2], r2[3]))
J.log("完成")
