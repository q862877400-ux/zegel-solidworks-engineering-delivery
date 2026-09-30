# -*- coding: utf-8 -*-
"""搜索框定位 v3 —— 用占位文字的字形特征定位。

⚑ 前两版失败原因（都是自截图证实的）
# --------------------------------------------------
# v1「白底长条」：白色区域太多（header 空栏、表格空白），取到 (394,66) 那种位置
# v2「垂直中点」：仍是同一批白色区域，只是换了取法，错因没除
# ⇒ 根因：**「白色」在这个界面上不是特征**（到处都是）。
#
# v3 特征：搜索框内有**灰色占位文字**「请输入产品型号/关键字」，
#    即「白底 + 有深色字形」的横向长条。
#    判据：在每行里找「连续白 >=120px」且**行内白像素占比不是 100%**
#          （说明这一行穿过文字），取该行的 y。
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


def white_with_text_rows(pane, min_w=100, y_lo=40, y_hi=260):
    """找「白底且行内有深色字」的横向条。返回 [(l, y, r)]。"""
    px = pane.load()
    w, h = pane.size
    out = []
    for y in range(y_lo, min(y_hi, h)):
        whites = []
        run = None
        for x in range(w):
            if D.is_white(px[x, y]):
                if run is None:
                    run = x
            else:
                if run is not None and x - run >= min_w:
                    whites.append((run, x))
                run = None
        if not whites:
            continue
        for l, r in whites:
            seg = r - l
            if seg < min_w:
                continue
            # 这一段里有多少非白（= 字形像素）
            ink = sum(0 if D.is_white(px[x, y]) else 1 for x in range(l, r))
            if 4 <= ink <= seg * 0.25:          # 有字，但不是大字块
                out.append((l, y, r, ink))
    return out


def locate(h, win):
    """返回搜索框屏幕坐标（取候选里 x 起点最靠右 + y 靠上的那个长条）。"""
    pane, cr = D.capture_pane(h, win)
    if pane is None:
        return None, None
    rows = white_with_text_rows(pane)
    if not rows:
        return None, pane
    # 合并成条：同一 x 区间的相邻 y
    boxes = []
    for l, y, r, ink in rows:
        hit = None
        for bx in boxes:
            if abs(bx["x0"] - l) < 50 and abs(bx["x1"] - r) < 50 and abs(bx["y1"] - y) <= 3:
                hit = bx
                break
        if hit:
            hit["y1"] = y
        else:
            boxes.append({"x0": l, "x1": r, "y0": y, "y1": y})
    # 选最宽的一条（搜索框最宽）
    boxes.sort(key=lambda b: b["x1"] - b["x0"], reverse=True)
    b = boxes[0]
    cx = (b["x0"] + b["x1"]) // 2
    cy = (b["y0"] + b["y1"]) // 2
    return (cr.left + cx, cr.top + cy), {"boxes": boxes, "pane_w": pane.size[0], "pane_h": pane.size[1]}


if __name__ == "__main__":
    h, win = L.connect()
    L.focus_solidworks(h)
    h, win = L.connect()
    pt, info = locate(h, win)
    print("候选框:", info["boxes"][:5] if info else None)
    print("搜索框屏幕坐标:", pt)
