# -*- coding: utf-8 -*-
"""简化版形状定位：按行找蓝色连续段，合并成矩形。"""
import sys
import time
import warnings
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc
import win32api
import win32con
import win32gui
from PIL import ImageGrab

warnings.filterwarnings("ignore")
BLUES = ((48, 80, 224), (0, 144, 224))


def is_blue(p):
    r, g, b = p[0], p[1], p[2]
    if b < 130 or b - r < 60 or b - g < 30:
        return False
    return any(abs(r - t[0]) <= 45 and abs(g - t[1]) <= 45 and abs(b - t[2]) <= 45
               for t in BLUES)


hwnd, win = loc.connect()
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.15)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(1.2)
cont = loc.find_container(win)
cr = cont[2]
pane = ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom))
pane.save(r"D:\AI\SW\shots\pane_v3.png")
px = pane.load()
w, h = pane.size
print("插件区 %dx%d" % (w, h))

# 每 3 行取一次，纵向合并
row_runs = {}
for y in range(0, h, 3):
    runs = []
    start = None
    for x in range(w):
        if is_blue(px[x, y]):
            if start is None:
                start = x
        else:
            if start is not None and x - start >= 35:
                runs.append((start, x))
            start = None
    if start is not None and w - start >= 35:
        runs.append((start, w))
    if runs:
        row_runs[y] = runs

print("有蓝色段的行数:", len(row_runs))
rows = sorted(row_runs)
# 打印每段的纵向范围
print()
print("蓝色块（按 x 从左到右分组）:")
groups = []
for y in rows:
    for a, b in row_runs[y]:
        hit = None
        for g in groups:
            if abs(g["x0"] - a) < 60 and abs(g["x1"] - b) < 60 and \
                    y - g["y1"] <= 12:
                hit = g
                break
        if hit is None:
            groups.append({"x0": a, "x1": b, "y0": y, "y1": y})
        else:
            hit["x0"] = min(hit["x0"], a)
            hit["x1"] = max(hit["x1"], b)
            hit["y1"] = y

for g in sorted(groups, key=lambda z: z["x0"]):
    print("   (%d,%d,%d,%d)  %dx%d"
          % (g["x0"], g["y0"], g["x1"], g["y1"],
             g["x1"] - g["x0"], g["y1"] - g["y0"]))
print()
print("共 %d 个蓝色块" % len(groups))
