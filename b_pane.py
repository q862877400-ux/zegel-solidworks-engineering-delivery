# -*- coding: utf-8 -*-
"""把右侧任务窗格整条放大，数清标签，找嘉立创。只读。"""
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import win32gui
import uiautomation as auto

sys.path.insert(0, r"D:\AI\SW")
import shot

hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
print("  窗口:", repr(win32gui.GetWindowText(hwnd)[:56]))
root = auto.ControlFromHandle(hwnd)
root.SetActive()
time.sleep(0.8)

img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\full_now.png")
print("  全窗口截图 %dx%d ok=%s" % (w, h, ok))

# 整条任务窗格（含标签列 + 内容区）
TAB = (1705, 194, 1739, 434)
crop = img.crop((TAB[0] - 10, TAB[1] - 60, min(w, 2050), min(h, TAB[3] + 40)))
crop = crop.resize((crop.width * 2, crop.height * 2), 4)
p = Path(r"D:\AI\SW\shots\pane_all.png")
crop.save(p)
print("  任务窗格整条:", p, crop.size)

# 标签列单独放大
col = img.crop((TAB[0] - 6, TAB[1] - 20, TAB[2] + 6, TAB[3] + 20))
col = col.resize((col.width * 5, col.height * 5), 5)
p2 = Path(r"D:\AI\SW\shots\tab_col.png")
col.save(p2)
print("  标签列放大:", p2, col.size)
