# -*- coding: utf-8 -*-
"""步骤 4：清空搜索框，输入嘉立创真实存在的型号，再搜。"""
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


kw = sys.argv[1] if len(sys.argv) > 1 else "HSR25HAM"
hwnd = J.sw_window()
J.ensure_window(hwnd)
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.12)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.4)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.5)

_root, rect = J.tab_column(hwnd)
SX, SY = 1390, 148
J.log("点搜索框 (%d,%d) 并全选清空" % (SX, SY))
J.click(SX, SY, pause=0.8)
J.ensure_window(hwnd)
# Ctrl+A 全选，再删
win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
win32api.keybd_event(ord("A"), 0, 0, 0)
time.sleep(0.1)
win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.3)
for _ in range(24):
    win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
time.sleep(0.4)
J.log("输入 %s" % kw)
type_text(kw)
time.sleep(0.8)
J.ensure_window(hwnd)
J.log("回车")
win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
time.sleep(0.1)
win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
for i in range(6):
    time.sleep(2.5)
    r = J.ensure_window(hwnd)
    _root, rect2 = J.tab_column(hwnd)
    J.snap("s5_%s_%d" % (kw, i + 1),
           box=(rect2.right - 4, rect2.top - 16,
                min(r[2], rect2.right + 470), min(r[3], rect2.top + 560)))
J.log("完成，看 s5_%s_6_z.png" % kw)
