# -*- coding: utf-8 -*-
"""点进「直线运动零件」，看子分类树。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import sw_jlcfa_locate as L
import cat_nav as CN
import win32api
import win32con
from PIL import ImageGrab

warnings.filterwarnings("ignore")

h, w, st = CN.fresh()
target = "直线运动零件"
r = None
for c in L._controls(w):
    try:
        if (c.window_text() or "").strip() == target:
            r = c.rectangle()
            break
    except Exception:
        continue
if r is None:
    print("✗ 找不到", target)
    raise SystemExit(1)
print("找到「%s」%s" % (target, (r.left, r.top, r.right, r.bottom)))
x, y = (r.left + r.right) // 2, (r.top + r.bottom) // 2
win32api.SetCursorPos((int(x), int(y)))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print("已点，等 3 秒…")
time.sleep(3)

h, w = L.connect()
L.focus_solidworks(h)
h, w = L.connect()
cr = L.container_rect(w)
ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
    r"D:\AI\SW\shots\cat_linear.png")
st2 = CN.H_observe(h, w)
print()
print("进入后的文字:")
seen = set()
for top, t in sorted(st2["texts"]):
    if t in seen or t.startswith(("sw", "Search", "EM ", "header", "任务", "expand", "pin",
                                    "taskPane", "Task", "设置", "数据")):
        continue
    seen.add(t)
    print("   %s" % t[:34])
