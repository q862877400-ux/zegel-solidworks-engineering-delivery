# -*- coding: utf-8 -*-
"""点分类菜单里的「直线运动零件」——用插件区相对坐标，验证是否进得去。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import sw_jlcfa_locate as L
import win32api
import win32con
from PIL import ImageGrab

warnings.filterwarnings("ignore")


def click_abs(x, y, pause=1.6):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr)
# 菜单项「直线运动零件」在插件区 y≈228, x≈45~250（截图量）
x = cr.left + 145
y = cr.top + 228
print("点菜单项 (%d,%d)" % (x, y))
click_abs(x, y, 2.5)

h, w = L.connect()
L.focus_solidworks(h)
h, w = L.connect()
cr = L.container_rect(w)
ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
    r"D:\AI\SW\shots\cat_enter.png")
# 判断是否进入了分类页：看有没有「共 N 个」
texts = []
for c in L._controls(w):
    try:
        t = (c.window_text() or "").strip()
        if t:
            texts.append(t)
    except Exception:
        continue
j = " | ".join(texts)
print()
print("是否出现「个」计数:", "个" in j)
print("按钮:", [t for t in texts if t in ("返回", "搜索", "全部商品分类", "首页")])
print("片段:", j[:260])
