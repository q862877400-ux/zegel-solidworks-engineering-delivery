# -*- coding: utf-8 -*-
"""重开后的第一步：激活插件标签 → 拖动刷新 → 读首页状态。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import jlc_auto as JA
import sw_gui_modal as M
import win32api
import win32con

warnings.filterwarnings("ignore")

hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
_root, rect = JA.tab_column(hwnd)
print("标签列:", rect, flush=True)
if rect is None:
    raise SystemExit("没有标签列")

# 点最下面那个（嘉立创）
x = (rect.left + rect.right) // 2
y = rect.bottom - 15
print("点插件标签 (%d,%d)" % (x, y), flush=True)
win32api.SetCursorPos((int(x), int(y)))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print("等插件加载 8 秒…", flush=True)
time.sleep(8)

hwnd, win = ctl.connect()
_root, rect = JA.tab_column(hwnd)
print("拖动刷新面板（30px 小幅度）…", flush=True)


def drag(x1, y1, x2, y2, steps=8):
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.03)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.6)


xe = max(rect.left - 2, 1)
ym = rect.top + 60
drag(xe, ym, xe - 30, ym)
drag(xe - 30, ym, xe, ym)
time.sleep(3)

hwnd, win = ctl.connect()
t = []
for c in win.descendants():
    try:
        if c.element_info.control_type in ("Text", "Pane"):
            x = (c.window_text() or "").strip()
            if x and len(x) < 44 and c.rectangle().left > 1300:
                t.append((c.rectangle().top, x))
    except Exception:
        continue
print()
print("插件区内容:")
seen = set()
for top, x in sorted(t):
    if x in seen:
        continue
    seen.add(x)
    print("   y=%-5d %s" % (top, x))
M.screen_png(r"D:\AI\SW\shots\after_restart.png")
print()
print("整屏: after_restart.png")
