# -*- coding: utf-8 -*-
"""点直线轴承结果卡 -> 进参数页 -> 截图。"""
import ctypes
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
import jlc_auto as J

ctypes.windll.user32.SetProcessDPIAware()

hwnd = J.sw_window()
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
CX, CY = rect.right - 4 + 235, rect.top - 16 + 535
J.log("点结果卡 (%d,%d)" % (CX, CY))
J.click(CX, CY, pause=2.0)
time.sleep(3.5)
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("m8_bearing", box=(rect2.right - 4, rect2.top - 16,
                         min(r[2], rect2.right + 470), min(r[3], rect2.top + 880)))
J.log("完成")
