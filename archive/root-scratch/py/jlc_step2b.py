# -*- coding: utf-8 -*-
"""步骤 2b：重新量准搜索框坐标再输入。"""
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
        vk = win32api.VkKeyScan(ch) & 0xFF
        shift = (win32api.VkKeyScan(ch) >> 8) & 1
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.04)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.04)


hwnd = J.sw_window()
J.log("窗口 %dx%d  %r" % (*win32gui.GetWindowRect(hwnd)[2:], win32gui.GetWindowText(hwnd)[:44]))
_root, rect = J.tab_column(hwnd)
r = rect
J.log("标签列: %s" % (r,))

# ★ 用整窗截图量搜索框：它就在面板顶部、标签列右侧
img, ok, w, h = shot.capture(hwnd)
img.save(r"D:\AI\SW\shots\s2b_full.png")
# 裁面板顶部 120px 高，放大 2 倍，便于目视定位
top = img.crop((r.right - 2, r.top - 6, min(w, r.right + 420), r.top + 60))
top = top.resize((top.width * 2, top.height * 2), 3)
top.save(r"D:\AI\SW\shots\s2b_top.png")
J.log("面板顶部放大图: s2b_top.png  %s  裁剪原点=(%d,%d)" % (top.size, r.right - 2, r.top - 6))
J.log("  ⇒ 搜索框在放大图里大约 y=%d，x 从 30 到 340" % 60)
J.log("  ⇒ 换算回窗口坐标：y ≈ %d, x ≈ %d" % (r.top - 6 + 30, r.right - 2 + 185))
