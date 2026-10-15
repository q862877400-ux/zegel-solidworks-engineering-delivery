# -*- coding: utf-8 -*-
"""步骤 2c：护栏就位后重试搜索（每步先校验窗口状态）。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api
import win32con
import win32gui
import shot
import jlc_auto as J


def type_text(s: str) -> None:
    for ch in s:
        scan = win32api.VkKeyScan(ch)
        vk, shift = scan & 0xFF, (scan >> 8) & 1
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.04)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.04)


keyword = sys.argv[1] if len(sys.argv) > 1 else "HGR20"
hwnd = J.sw_window()
r = J.ensure_window(hwnd)               # ★ 护栏
J.log("窗口 %s 尺寸 %dx%d  标题 %r" % (r, r[2] - r[0], r[3] - r[1],
                                      win32gui.GetWindowText(hwnd)[:40]))
# 置顶（带 Alt 绕过前台锁）
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.12)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.4)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.5)
J.log("前台 = %d (目标 %d)" % (win32gui.GetForegroundWindow(), hwnd))

_root, rect = J.tab_column(hwnd)
J.log("标签列: %s" % (rect,))
tr = rect
panel_left = tr.right + 2
sx, sy = panel_left + 130, tr.top + 28
J.log("点搜索框 (%d,%d)" % (sx, sy))
J.click(sx, sy, pause=0.8)
J.ensure_window(hwnd)                    # 点完再校验一次
J.log("输入 %s" % keyword)
type_text(keyword)
time.sleep(0.8)
J.ensure_window(hwnd)
J.snap("s2c_typed", box=(panel_left - 14, tr.top - 14,
                         min(r[2], panel_left + 420), tr.top + 70))
J.log("按回车")
win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
time.sleep(0.08)
win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(5.0)
r2 = J.ensure_window(hwnd)
J.snap("s3c_result", box=(panel_left - 14, tr.top - 14,
                          min(r2[2], panel_left + 470), min(r2[3], tr.top + 720)))
J.log("完成")
