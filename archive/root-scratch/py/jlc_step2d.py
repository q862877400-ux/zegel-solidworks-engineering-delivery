# -*- coding: utf-8 -*-
"""步骤 2d：用颜色量出的准确坐标点搜索框并搜索。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api
import win32con
import win32gui
import jlc_auto as J


def type_text(s: str) -> None:
    for ch in s:
        scan = win32api.VkKeyScan(ch)
        vk, shift = scan & 0xFF, (scan >> 8) & 1
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)


keyword = sys.argv[1] if len(sys.argv) > 1 else "HGR20"
hwnd = J.sw_window()
r = J.ensure_window(hwnd)
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.12)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.4)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.6)
_root, rect = J.tab_column(hwnd)
J.log("标签列 %s  前台=%d" % (rect, win32gui.GetForegroundWindow()))

# ★ 颜色量出来的搜索框：x 1244..1535, y 141..156
SX, SY = 1390, 148
J.log("点搜索框 (%d,%d)  ← 颜色量出的中心，不是估的" % (SX, SY))
J.click(SX, SY, pause=1.0)
J.ensure_window(hwnd)
# 有没有获得焦点？先试着输入
J.log("输入 %s" % keyword)
type_text(keyword)
time.sleep(1.0)
r2 = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("s2d_typed", box=(rect2.right - 4, rect2.top - 16,
                         min(r2[2], rect2.right + 430), rect2.top + 60))
J.log("完成（先看 s2d_typed_z.png 确认文字是否进去了）")
