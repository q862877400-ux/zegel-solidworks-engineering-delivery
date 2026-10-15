# -*- coding: utf-8 -*-
"""按用户口述的顺序：先点选型框空白处取焦点，再滚轮/拖滑块翻页。

⚑ 用户口述（2026-09-30）：
  「记得要翻页就得**在这个选型框的空白处点一下**，然后再去用滚轮或者拖动滑块」
  ⇒ 我上一轮点在了控件之间的行上、且点在**面板底部**（不在框内），焦点没落上。
"""
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


def shot(tag, rect, r):
    J.snap(tag, box=(rect.right - 4, rect.top - 16,
                     min(r[2], rect.right + 560), min(r[3], rect.top + 760)))


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
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
J.log("标签列 %s（面板内容区 x>%d, y %d..%d）" % (rect, rect.right, rect.top, rect.bottom))

# ★ 关键：点在「参数筛选器」框**内部**的空白处 —— 两个控件之间的那一行
# 裁剪图原点 (rect.right-4, rect.top-16)；
# 「代码」行 y≈625，下一个空白行 y≈690，x 取标签右侧空白 x≈310
CX = rect.right - 4 + 310
CY = rect.top - 16 + 690
J.log("① 点选型框内部空白处 (%d,%d)" % (CX, CY))
J.click(CX, CY, pause=1.0)
shot("v1_focus_blank", J.tab_column(hwnd)[1], J.ensure_window(hwnd))

# ② 再滚轮
J.log("② 滚轮向下 3 格")
J.wheel(rect.right + 200, rect.top + 300, -3, pause=1.0)
shot("v2_wheel", J.tab_column(hwnd)[1], J.ensure_window(hwnd))

# ③ 若滚轮无效则拖右侧滑块
rect3 = J.tab_column(hwnd)[1]
J.log("③ 拖右侧滑块向下")
SX = rect3.right - 4 + 505
J.drag(SX, rect3.top - 16 + 600, SX, rect3.top - 16 + 250, steps=14)
time.sleep(1.0)
shot("v3_dragbar", J.tab_column(hwnd)[1], J.ensure_window(hwnd))
J.log("完成 —— 对比 v1/v2/v3 哪张内容真的变了")
