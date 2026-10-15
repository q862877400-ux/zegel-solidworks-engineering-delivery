# -*- coding: utf-8 -*-
"""用 pywinauto 的 UIAWrapper 探插件窗格 —— 看能不能按控件而非坐标操作。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
import jlc_auto as J
from pywinauto.application import Application  # 0.6.x 用 Application(backend='uia')
import pywinauto


def sw_hwnd():
    cands = []
    import win32process
    import subprocess

    def cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return
        t = win32gui.GetWindowText(h)
        if not t:
            return
        try:
            pid = win32process.GetWindowThreadProcessId(h)[1]
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid,
                                  "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True,
                                 encoding="utf-8", errors="replace")
            name = out.stdout.split(",")[0].strip('"')
        except Exception:
            name = ""
        if name.lower().endswith("sldworks.exe"):
            cands.append((h, t, win32gui.GetWindowRect(h)))
    win32gui.EnumWindows(cb, None)
    if not cands:
        raise RuntimeError("找不到 SolidWorks")
    cands.sort(key=lambda x: (x[2][2]-x[2][0])*(x[2][3]-x[2][1]), reverse=True)
    return cands[0][0]


hwnd = sw_hwnd()
print("  hwnd=%d %r" % (hwnd, win32gui.GetWindowText(hwnd)[:48]))

app = Application(backend="uia").connect(handle=hwnd)
w = app.window(handle=hwnd)   # ← UIA 后端（不是 win32），能按控件语义操作
print("  UIAWrapper 已连上，开始打印控件树（前 12 层）")
print()

count = 0
try:
    for c in w.descendants():
        try:
            ct = c.element_info.control_type
            nm = c.window_text()
            r = c.rectangle()
        except Exception:
            continue
        if not nm:
            continue
        count += 1
        if count <= 60:
            print("   %-18s %-34s (%d,%d,%d,%d)" % (ct, nm[:32], r.left, r.top,
                                                       r.right, r.bottom))
except Exception as e:
    print("  遍历异常:", str(e)[:80])
print()
print("  ★ 共读到 %d 个有名字的控件" % count)
