# -*- coding: utf-8 -*-
"""A 路线：分类菜单导航（替代不稳定的搜索框）。

⚑ 为什么换路（四版搜索框定位全部失败的实测记录）
# --------------------------------------------------
#   v1 白底长条 / v2 垂直中点 / v3 白底带字墨迹 / v4「搜索」按钮反推
#   —— 颜色形状在这个界面上不是可靠特征，同一个控件在 UIA 树里还时有时无。
# ⇒ 改走**分类菜单**：「全部商品分类」是**蓝色按钮**（已多次命中，贴容器左端），
#    点开是一棵分类树，树里的项**带名字**（直线运动零件/机床防护罩/…），
#    名字可读 ⇒ 结构锚，比像素可靠。
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


def fresh():
    h, w = L.connect()
    return h, w, H_observe(h, w)


def H_observe(h, w):
    cr = L.container_rect(w)
    st = {"cr": cr, "buttons": {}, "texts": [], "pct": None}
    if cr is None:
        return st
    for c in L._controls(w):
        try:
            ct = c.element_info.control_type
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if not L._overlaps(r, cr):
            continue
        if ct == "Button" and t:
            st["buttons"][t] = r
        if ct in ("Text", "Pane") and t:
            st["texts"].append((r.top, t))
    return st


def click_category_menu(h, w):
    """点「全部商品分类」——优先按名字，退回按蓝块形状。"""
    st = H_observe(h, w)
    c = L.locate(w, "全部商品分类", "Button")
    pt = None
    if c is not None:
        r = c.rectangle()
        pt = ((r.left + r.right) // 2, (r.top + r.bottom) // 2)
    if pt is None:
        pts = D.locate_all(h, w, log=lambda m: None)
        pt = pts.get("category_btn")
    if pt is None:
        return None
    win32api.SetCursorPos((int(pt[0]), int(pt[1])))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1.8)
    return pt


if __name__ == "__main__":
    h, w, st = fresh()
    print("容器:", st["cr"])
    print("Button:", list(st["buttons"].keys())[:10])
    pt = click_category_menu(h, w)
    print("点了分类菜单:", pt)
    time.sleep(1.2)
    h, w = L.connect()
    L.focus_solidworks(h)
    h, w = L.connect()
    cr = L.container_rect(w)
    ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
        r"D:\AI\SW\shots\cat_menu.png")
    st2 = H_observe(h, w)
    print()
    print("点开后的可见文字（按 y）:")
    seen = set()
    for top, t in sorted(st2["texts"]):
        if t in seen:
            continue
        seen.add(t)
        print("   %s" % t[:30])
