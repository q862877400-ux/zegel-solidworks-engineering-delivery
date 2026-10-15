# -*- coding: utf-8 -*-
"""自适应验证：侧边栏宽度可变时，控件树能否稳定按名字定位。

⚑ 用户指出的缺陷（2026-09-30）
# ------------------------------------------
# 「这个侧边栏它的宽度是可以随意调整的，我今天默认是这么宽，
#   明天我手动拉一下，那你岂不是就失效了」
# ⇒ 硬编码坐标（1390,148 / 1749,931 / …）**全部作废**。
# ⇒ 长效解法：**每次动作前从控件树按名字定位，坐标由控件自己给出**。
#   侧边栏多宽都不影响 —— 控件的 (left,top,right,bottom) 会跟着变，
#   但**名字不变**。
#
# ⚑ 本脚本验证三件事
#   ① 宽侧边栏下，控件树里能不能按名字拿到关键控件
#   ② 每个控件的坐标是否随侧边栏变化而自洽
#   ③ 同一个控件在「窄→宽」两次读之间，名字是否稳定
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import jlc_auto as JA
import sw_gui_modal as M
import win32gui

warnings.filterwarnings("ignore")

KEYS = ["搜索", "返回", "全部商品分类", "首页", "同步数据",
        "直线运动零件", "机床防护罩", "传动零部件", "轴承附件"]


def snapshot():
    """读一次控件树，返回 {名字: rect}（只取插件区）。"""
    hwnd, win = ctl.connect()
    out = {}
    for c in win.descendants():
        try:
            t = (c.window_text() or "").strip()
            ct = c.element_info.control_type
            r = c.rectangle()
        except Exception:
            continue
        if not t or r.width() <= 0:
            continue
        if r.left < 1200:            # 只看插件区
            continue
        out.setdefault(t, (ct, r))
    return hwnd, win, out


def report(tag, snap):
    _h, _w, out = snap
    print()
    print("  === %s ===" % tag)
    found = [k for k in KEYS if k in out]
    for k in found:
        ct, r = out[k]
        print("    %-14s %-8s (%d,%d,%d,%d)  %dx%d"
              % (k, ct, r.left, r.top, r.right, r.bottom, r.width(), r.height()))
    miss = [k for k in KEYS if k not in out]
    print("    缺失: %s" % (miss or "无"))
    return out


def main():
    hwnd, win = ctl.connect()
    M.close_modals(hwnd)
    _root, rect = JA.tab_column(hwnd)
    print("当前标签列:", rect, flush=True)

    s1 = snapshot()
    o1 = report("当前宽度（默认）", s1)

    # ── 拉窄侧边栏到 240px，验证是否仍能按名字定位 ──
    if rect:
        xe = rect.left - 3
        ym = rect.top + 120
        print()
        print("  ★ 把侧边栏从 %d 拉到 240px 验证自适应…"
              % (rect.right - rect.left), flush=True)
        import win32api
        import win32con

        def drag(x1, y1, x2, y2, steps=14):
            win32api.SetCursorPos((int(x1), int(y1)))
            time.sleep(0.15)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            for i in range(1, steps + 1):
                win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                                      int(y1 + (y2 - y1) * i / steps)))
                time.sleep(0.03)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(1.0)

        drag(xe, ym, xe - (rect.right - rect.left - 240), ym)
        time.sleep(2.5)

        hwnd2, _w2, o2 = snapshot()
        _r2, rect2 = JA.tab_column(hwnd2)
        o2 = report("拉窄后（约 240px）", (hwnd2, _w2, o2))
        print()
        print("  标签列: %s -> %s" % (rect, rect2))

        # ── 对比：同一控件在两种宽度下 ---
        print()
        print("  ★ 自适应判定（同一名字，两次读是否都拿到）:")
        both = [k for k in KEYS if k in o1 and k in o2]
        for k in both:
            r1 = o1[k][1]
            r2 = o2[k][1]
            print("    %-14s 宽 %d->%d  左边 %d->%d  %s"
                  % (k, r1.width(), r2.width(), r1.left, r2.left,
                     "✓ 坐标自变" if r1.left != r2.left else "="))
        print()
        print("  两种宽度下都能按名字定位的: %d/%d -> %s"
              % (len(both), len(KEYS), "✓ 可自适应" if len(both) >= len(KEYS) - 1
                 else "✗ 有缺失"))
        M.screen_png(r"D:\AI\SW\shots\narrow.png")
        print()
        print("  窄侧边栏截图: narrow.png")


if __name__ == "__main__":
    main()
