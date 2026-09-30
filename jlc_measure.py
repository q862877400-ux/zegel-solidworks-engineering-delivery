# -*- coding: utf-8 -*-
"""量准搜索框：按颜色定位输入框的白底矩形，不靠猜坐标。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import shot
import jlc_auto as J

hwnd = J.sw_window()
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
J.log("窗口 %dx%d  标签列 %s" % (r[2] - r[0], r[3] - r[1], rect))

img, ok, w, h = shot.capture(hwnd)
img.save(r"D:\AI\SW\shots\measure_full.png")

# 搜索框是**白底 + 灰边框**的 Edit。从面板顶部往下扫，找连续的浅色行。
top0, bot0 = max(rect.top - 10, 0), min(rect.top + 70, h)
left0, right0 = rect.right, min(rect.right + 420, w)
band = img.crop((left0, top0, right0, bot0))
J.log("扫描带 (%d,%d)-(%d,%d) %s" % (left0, top0, right0, bot0, band.size))

px = band.load()
bw, bh = band.size
# 找每行里「近白色」像素的连续段
for y in range(bh):
    runs, start = [], None
    for x in range(bw):
        R, G, B = px[x, y][:3]
        white = R > 240 and G > 240 and B > 240
        if white and start is None:
            start = x
        elif not white and start is not None:
            if x - start > 120:                 # 足够长的白条才算输入框
                runs.append((start, x))
            start = None
    if start is not None and bw - start > 120:
        runs.append((start, bw))
    if runs:
        J.log("  行 y=%-4d 白条: %s  -> 窗口坐标 y=%d" % (y, runs, top0 + y))
