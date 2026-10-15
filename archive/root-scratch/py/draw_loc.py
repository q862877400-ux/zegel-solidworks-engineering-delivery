# -*- coding: utf-8 -*-
"""自绘控件的形状定位器（第 2 层）—— 截图 + 颜色/边框识别。

⚑ 三个 UIA 树里**没有名字**的自绘控件（实测）：
  「搜索框」        白底 + 浅灰边框的横向长条
  「搜索」按钮      蓝底白字，贴容器右端
  「全部商品分类」   蓝底白字，贴容器左端
  「首页」          纯文字，无底色
  「同步数据」      蓝底白字，贴容器右端（与搜索按钮同侧不同 y）

⚑ 宽度无关性（本机实测 800px 与 598px 两个宽度）
  「全部商品分类」 始终贴左端 x≈42~44
  「搜索」「同步数据」始终贴右端 x≈505~708（随宽度缩放）
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import win32api
import win32con
import win32gui
from PIL import ImageGrab

warnings.filterwarnings("ignore")
import sw_jlcfa_locate as L

BLUES = ((48, 80, 224), (0, 144, 224))


def is_blue(p):
    r, g, b = p[0], p[1], p[2]
    if b < 130 or b - r < 60 or b - g < 30:
        return False
    return any(abs(r - t[0]) <= 45 and abs(g - t[1]) <= 45 and abs(b - t[2]) <= 45
               for t in BLUES)


def is_white(p):
    return p[0] > 235 and p[1] > 235 and p[2] > 235


def capture_pane(hwnd, win):
    """置前 -> 截整屏 -> 裁插件容器。返回 (pane_img, container_rect)。"""
    L.focus_solidworks(hwnd)
    cr = L.container_rect(win)
    if cr is None:
        return None, None
    return ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)), cr


def blue_groups(pane):
    """蓝色块合并。"""
    px = pane.load()
    w, h = pane.size
    gs = []

    def merge(a, b, y):
        for g in gs:
            if abs(g["x0"] - a) < 60 and abs(g["x1"] - b) < 60 and y - g["y1"] <= 12:
                g["x0"] = min(g["x0"], a); g["x1"] = max(g["x1"], b); g["y1"] = y
                return
        gs.append({"x0": a, "x1": b, "y0": y, "y1": y})

    for y in range(0, h, 2):
        st = None
        for x in range(w):
            if is_blue(px[x, y]):
                if st is None:
                    st = x
            else:
                if st is not None and x - st >= 30:
                    merge(st, x, y)
                st = None
    return [g for g in gs if g["y1"] - g["y0"] >= 4]


def white_boxes(pane, min_w=120, y_lo=60, y_hi=200):
    """白色长条（搜索框）。返回 [(l,t,r,b)] 相对插件区。"""
    px = pane.load()
    w, h = pane.size
    out = []
    for y in range(y_lo, min(y_hi, h)):
        st = None
        for x in range(w):
            if is_white(px[x, y]):
                if st is None:
                    st = x
            else:
                if st is not None and x - st >= min_w:
                    out.append((st, y, x, y))
                st = None
    # 合并相邻 y
    rects = []
    for l, t, r, b in out:
        hit = None
        for q in rects:
            if abs(q[0] - l) < 40 and abs(q[2] - r) < 40 and abs(q[1] - t) < 12:
                hit = q
                break
        if hit:
            hit[0] = min(hit[0], l); hit[2] = max(hit[2], r); hit[3] = b
        else:
            rects.append([l, t, r, b])
    return rects


def locate_all(hwnd, win, log=print):
    """一次识别三个自绘控件的**屏幕坐标**。"""
    pane, cr = capture_pane(hwnd, win)
    if pane is None:
        return {}
    log("  插件区 %dx%d" % (pane.size[0], pane.size[1]))
    res = {}
    # 搜索框：白底长条，取最宽的
    boxes = white_boxes(pane)
    boxes.sort(key=lambda b: b[2] - b[0], reverse=True)
    for b in boxes[:3]:
        log("    白色长条 (%d,%d,%d,%d) 宽%d" % (b[0], b[1], b[2], b[3], b[2]-b[0]))
    if boxes:
        b = boxes[0]
        res["search_box"] = (cr.left + (b[0]+b[2])//2, cr.top + b[1])
        log("  ✓ 搜索框 -> %s" % (res["search_box"],))
    gs = blue_groups(pane)
    gs.sort(key=lambda g: g["x0"])
    for g in gs:
        log("    蓝块 (%d,%d,%d,%d)" % (g["x0"], g["y0"], g["x1"], g["y1"]))
    if len(gs) >= 2:
        left = gs[0]
        right = gs[-1]
        res["category_btn"] = (cr.left + (left["x0"]+left["x1"])//2,
                               cr.top + (left["y0"]+left["y1"])//2)
        res["search_btn"] = (cr.left + (right["x0"]+right["x1"])//2,
                             cr.top + (right["y0"]+right["y1"])//2)
        log("  ✓ 分类按钮 -> %s" % (res["category_btn"],))
        log("  ✓ 搜索按钮 -> %s" % (res["search_btn"],))
    return res


if __name__ == "__main__":
    hwnd, win = L.connect()
    r = locate_all(hwnd, win)
    print()
    print("结果:", r)
