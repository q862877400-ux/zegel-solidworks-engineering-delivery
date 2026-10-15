# -*- coding: utf-8 -*-
"""最大窗口下的完整流程：插件 -> 搜索 -> 结果 -> 详情。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctypes
import win32api
import win32con
import win32gui
import jlc_auto as J

ctypes.windll.user32.SetProcessDPIAware()


def type_text(s: str) -> None:
    for ch in s:
        scan = win32api.VkKeyScan(ch)
        vk, shift = scan & 0xFF, (scan >> 8) & 1
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.045)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.045)


def focus(hwnd):
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    time.sleep(0.12)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)


def measure_search_box(hwnd, rect):
    """颜色扫描量搜索框（不靠猜）。"""
    import shot
    r = J.ensure_window(hwnd)
    img, _ok, w, h = shot.capture(hwnd)
    top0 = max(rect.top - 10, 0)
    left0 = rect.right
    right0 = min(rect.right + 460, w)
    bot0 = min(rect.top + 70, h)
    band = img.crop((left0, top0, right0, bot0))
    px = band.load()
    bw, bh = band.size
    for y in range(bh):
        start = None
        for x in range(bw):
            R, G, B = px[x, y][:3]
            white = R > 240 and G > 240 and B > 240
            if white and start is None:
                start = x
            elif not white and start is not None:
                if x - start > 150:
                    return left0 + (start + x) // 2, top0 + y
                start = None
        if start is not None and bw - start > 150:
            return left0 + (start + bw) // 2, top0 + y
    return None


hwnd = J.sw_window()
focus(hwnd)
_root, rect = J.tab_column(hwnd)
J.log("窗口 %dx%d  标签列 %s" % (*J.ensure_window(hwnd)[2:], rect))

sx, sy = measure_search_box(hwnd, rect)
if sx is None:
    J.log("✗ 量不到搜索框")
    raise SystemExit(1)
J.log("★ 搜索框量到 (%d,%d)" % (sx, sy))
J.click(sx, sy, pause=0.9)
J.ensure_window(hwnd)
type_text(sys.argv[1] if len(sys.argv) > 1 else "HSR25HAM")
time.sleep(0.8)
J.ensure_window(hwnd)
win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
time.sleep(0.1)
win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
J.log("已回车，等结果…")
time.sleep(6)
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("m1_search", box=(rect2.right - 4, rect2.top - 16,
                         min(r[2], rect2.right + 470), min(r[3], rect2.top + 800)))
J.log("完成")
