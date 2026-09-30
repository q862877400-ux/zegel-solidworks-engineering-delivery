# -*- coding: utf-8 -*-
"""抓「常用商品分类」完整菜单（hover 展开 + 滚轮往下翻）。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import sw_gui_modal as M
import win32api
import win32con

warnings.filterwarnings("ignore")

hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()

# 「常用商品分类」可能在「全部商品分类」旁；先全量列出插件区文字
base = set()
for c in win.descendants():
    try:
        t = (c.window_text() or "").strip()
        r = c.rectangle()
    except Exception:
        continue
    if t and r.left > 1350 and r.top < 1000 and r.width() > 20:
        base.add((r.top, t))
print("当前可见项 %d 个:" % len(base))
for top, t in sorted(base)[:24]:
    print("   y=%-5d %s" % (top, t[:28]))

# hover 在分类区
anchor = None
for c in win.descendants():
    try:
        t = (c.window_text() or "").strip()
        if "商品分类" in t:
            anchor = c.rectangle()
            print()
            print("hover 目标: %r %s" % (t[:16], (anchor.left, anchor.top,
                                                 anchor.right, anchor.bottom)))
            break
    except Exception:
        continue
if anchor is None:
    print("没有「商品分类」字样，用区域中心 hover")
    anchor = (1400, 330, 1900, 370)

cx, cy = (anchor[0] + anchor[2]) // 2, (anchor[1] + anchor[3]) // 2
win32api.SetCursorPos((int(cx), int(cy)))
time.sleep(1.6)
print("已 hover (%d,%d)" % (cx, cy))
M.screen_png(r"D:\AI\SW\shots\menu_now.png")

hwnd, win = ctl.connect()
items = set()
for c in win.descendants():
    try:
        t = (c.window_text() or "").strip()
        r = c.rectangle()
    except Exception:
        continue
    if t and r.left > 1350 and 150 < r.top < 1050 and r.width() > 25:
        items.add((r.top, t[:26]))
print()
print("★ hover 后的项 %d 个:" % len(items))
for top, t in sorted(items):
    print("   y=%-5d %s" % (top, t))
