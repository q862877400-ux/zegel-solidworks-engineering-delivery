# -*- coding: utf-8 -*-
"""控件驱动的插件操作 —— 按名字点，不猜坐标。

⚑ 与前一个版本（sw_jlcfa_gui.py，按坐标）的区别：
   · 每个动作都先在 UIA 树里**按名字找控件**，坐标由控件自己给出
   · 每次动作后**重新读树**确认状态，不靠肉眼看截图
   · 找不到控件就**明说**，不退回硬编码坐标
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
from pywinauto import Application

warnings.filterwarnings("ignore")


def sw_hwnd():
    import subprocess
    import win32process
    cands = []

    def cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return
        t = win32gui.GetWindowText(h)
        if not t:
            return
        try:
            pid = win32process.GetWindowThreadProcessId(h)[1]
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO",
                                  "CSV", "/NH"], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace")
            name = out.stdout.split(",")[0].strip('"')
        except Exception:
            name = ""
        if name.lower().endswith("sldworks.exe"):
            cands.append((h, t, win32gui.GetWindowRect(h)))
    win32gui.EnumWindows(cb, None)
    if not cands:
        raise RuntimeError("找不到 SolidWorks 主窗口")
    cands.sort(key=lambda x: (x[2][2]-x[2][0])*(x[2][3]-x[2][1]), reverse=True)
    return cands[0][0]


def connect():
    hwnd = sw_hwnd()
    app = Application(backend="uia").connect(handle=hwnd)
    win = app.window(handle=hwnd)
    win.set_focus()
    time.sleep(0.5)
    return hwnd, win


def find(win, name, ctype="Button"):
    """按名字+类型找控件。找不到返回 None（**不猜**）。"""
    for c in win.descendants():
        try:
            if c.element_info.control_type == ctype and c.window_text() == name:
                return c
        except Exception:
            continue
    return None


def find_all(win, name, ctype=None):
    out = []
    for c in win.descendants():
        try:
            if c.window_text() == name and (ctype is None
                                            or c.element_info.control_type == ctype):
                out.append(c)
        except Exception:
            continue
    return out


def click_named(win, name, ctype="Button"):
    c = find(win, name, ctype)
    if c is None:
        return False, None
    r = c.rectangle()
    c.click_input()
    return True, r


def progress_pct(win):
    """读参数筛选器进度条的比例（0-1）。⚠ 读不到返回 None，不编。"""
    for c in win.descendants():
        try:
            if c.element_info.control_type == "ProgressBar":
                return c
        except Exception:
            continue
    return None
