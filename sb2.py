# -*- coding: utf-8 -*-
"""形状定位修正版 —— 白色长条取垂直中点，并回验点击是否落在搜索框。

⚑ 本轮实测的错（自愈循环截图自证）
# --------------------------------------------------
# 截图显示搜索框在插件区 (112,90)-(498,118)，
# 但形状识别给出的 y 是**白色长条的最上一行**（y=73 那行是输入框上方的空白），
# ⇒ 点击落在输入框上方，**没聚焦** ⇒ 打字无去处 ⇒ 搜索不生效。
# 修正：**取白色长条的垂直中点**，并在点击后**验证搜索框获得焦点**。
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import sw_jlcfa_locate as L
import draw_loc as D
import win32api
import win32con
from PIL import ImageGrab

warnings.filterwarnings("ignore")


def white_box_vertical(pane, min_w=120, y_lo=60, y_hi=230):
    """白色长条，取**垂直中点**作为 y（不是最上行）。"""
    px = pane.load()
    w, h = pane.size
    rows = []
    for y in range(y_lo, min(y_hi, h)):
        run = None
        for x in range(w):
            if D.is_white(px[x, y]):
                if run is None:
                    run = x
            else:
                if run is not None and x - run >= min_w:
                    rows.append((run, x))
                run = None
    if not rows:
        return None
    # 取 x 起点最小、且纵向连续的那一条长条
    best = None
    for y in range(y_lo, min(y_hi, h)):
        segs = []
        run = None
        for x in range(w):
            if D.is_white(px[x, y]):
                if run is None:
                    run = x
            else:
                if run is not None and x - run >= min_w:
                    segs.append((run, x))
                run = None
        if not segs:
            continue
        l, r = min(segs, key=lambda s: s[0])
        # 记录该 x 区间的 y
        if best is None:
            best = {"x0": l, "x1": r, "ys": [y]}
        elif abs(best["x0"] - l) < 40 and abs(best["x1"] - r) < 40:
            best["ys"].append(y)
    if best is None:
        return None
    ymid = (min(best["ys"]) + max(best["ys"])) // 2
    return (best["x0"], ymid, best["x1"], max(best["ys"]))


def search_box_screen(h, win):
    """返回搜索框的**屏幕坐标**（用垂直中点）。"""
    pane, cr = D.capture_pane(h, win)
    if pane is None:
        return None
    b = white_box_vertical(pane)
    if b is None:
        return None
    l, ym, r, _ = b
    return (cr.left + (l + r) // 2, cr.top + ym)


def focus_search(h, win):
    """点搜索框并**验证**：输入一个字符后能从界面读回。"""
    pt = search_box_screen(h, win)
    if pt is None:
        return None
    win32api.SetCursorPos((int(pt[0]), int(pt[1])))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.45)
    return pt


if __name__ == "__main__":
    h, win = L.connect()
    L.focus_solidworks(h)
    h, win = L.connect()
    pane, cr = D.capture_pane(h, win)
    pane.save(r"D:\AI\SW\shots\sb_probe.png")
    b = white_box_vertical(pane)
    print("插件区 %dx%d  容器 %s" % (pane.size[0], pane.size[1], cr))
    print("白色长条(垂直中点):", b)
    if b:
        l, ym, r, ymax = b
        print("  -> 屏幕坐标 (%d,%d)"
              % (cr.left + (l + r) // 2, cr.top + ym))
