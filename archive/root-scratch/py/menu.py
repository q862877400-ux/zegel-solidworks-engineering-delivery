# -*- coding: utf-8 -*-
"""hover「全部商品分类」展开菜单，读出全部大类（含可滚动的）。"""
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

# 找「全部商品分类」
cat = None
for c in win.descendants():
    try:
        t = (c.window_text() or "").strip()
        if "全部商品分类" in t or "商品分类" in t:
            cat = c
            break
    except Exception:
        continue
if cat is None:
    print("✗ 找不到「全部商品分类」")
    for c in win.descendants():
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            if t and r.left > 1350 and r.top < 500 and r.width() > 30:
                print("   %-12s %-22s (%d,%d,%d,%d)"
                      % (c.element_info.control_type, t[:20],
                         r.left, r.top, r.right, r.bottom))
        except Exception:
            continue
    raise SystemExit(1)

r = cat.rectangle()
cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
print("找到「%s」%s -> hover" % (cat.window_text().strip()[:12],
                             (r.left, r.top, r.right, r.bottom)))
win32api.SetCursorPos((int(cx), int(cy)))
time.sleep(1.5)
print("已 hover，等菜单展开")
M.screen_png(r"D:\AI\SW\shots\menu_hover.png")

hwnd, win = ctl.connect()
print()
print("★ hover 后出现的菜单项:")
items = []
for c in win.descendants():
    try:
        t = (c.window_text() or "").strip()
        rr = c.rectangle()
    except Exception:
        continue
    if not t or rr.width() < 20:
        continue
    if rr.left > 1350 and 150 < rr.top < 1000:
        items.append((rr.top, t[:22], rr))
seen = set()
for top, t, rr in sorted(items):
    if t in seen:
        continue
    seen.add(t)
    print("   y=%-5d %-24s (%d,%d,%d,%d)"
          % (top, t, rr.left, rr.top, rr.right, rr.bottom))
print()
print("共 %d 个唯一项" % len(seen))
