# -*- coding: utf-8 -*-
"""最后一步：填「滑轨长度」（Edit 自由输入），然后生成。"""
import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import sw_gui_modal as M
import win32api
import win32con

warnings.filterwarnings("ignore")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}


def pct(win):
    t = []
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Text" and c.window_text():
                t.append(c.window_text().strip())
        except Exception:
            continue
    m = re.search(r"(\d+)%", " ".join(t))
    return int(m.group(1)) if m else None


def edit_of(win, name):
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Edit" and \
                    c.window_text().strip() == name:
                return c
        except Exception:
            continue
    return None


def click(x, y, pause=0.25):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
print("填前进度:", pct(win), "%", flush=True)

ed = edit_of(win, "滑轨长度")
if ed is None:
    print("✗ 找不到「滑轨长度」Edit 控件")
    M.screen_png(r"D:\AI\SW\shots\no_len.png")
    raise SystemExit(1)

r = ed.rectangle()
print("滑轨长度 Edit:", (r.left, r.top, r.right, r.bottom), flush=True)
ed.click_input()
time.sleep(0.5)
for ch in "1000":
    win32api.keybd_event(win32api.VkKeyScan(ch) & 0xFF, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32api.VkKeyScan(ch) & 0xFF, 0,
                         win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
time.sleep(0.8)
hwnd, win = ctl.connect()
print("输入后进度:", pct(win), "%", flush=True)
M.screen_png(r"D:\AI\SW\shots\len_typed.png")

if pct(win) != 100:
    print("⚠ 未到 100%，按 Tab 提交再试", flush=True)
    win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1.2)
    hwnd, win = ctl.connect()
    print("Tab 后进度:", pct(win), "%", flush=True)

hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
btn = None
for c in win.descendants():
    try:
        if c.element_info.control_type == "Button" and \
                c.window_text().strip() == "生成预览":
            btn = c
            break
    except Exception:
        continue
if not btn:
    print("✗ 无「生成预览」")
    M.screen_png(r"D:\AI\SW\shots\no_gen.png")
    raise SystemExit(1)

print("\n★ 点「生成预览」", flush=True)
btn.click_input()
time.sleep(1.0)
M.screen_png(r"D:\AI\SW\shots\gen_clicked.png")
for i in range(24):
    time.sleep(5)
    now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    new = sorted(now - base)
    if new:
        print("★ %ds 新增: %s" % ((i + 1) * 5, new), flush=True)
        M.screen_png(r"D:\AI\SW\shots\gen_done.png")
        break
else:
    print("120 秒无新增")
    M.screen_png(r"D:\AI\SW\shots\gen_timeout.png")
