# -*- coding: utf-8 -*-
"""嘉立创 FA 完整通路：首页图标 -> 子分类 -> 型号 -> 选型 -> 生成预览。

⚑ 导航路径（用户 2026-09-30 给的两张截图 + 本机控件树核对）
# --------------------------------------------------
#   首页  → 点「直线运动零件」图标        （Text 可按名字读到 ✓）
#        → 点「直线导轨」子分类图标      （Text 可按名字读到 ✓）
#        → 结果列表（共 12 页，需滚右侧滚动条）
#        → 点某个型号（代码如 HGH20HAZC）
#        → 选型页：填 ComboBox 到 100%    （ComboBox 可按名字读到 ✓）
#        → 点「生成预览」                （Button 可按名字读到 ✓）
# ⚠ 「全部商品分类」**不是必经入口**（用户指出）—— 直接点首页图标即可。
# ⚠ 「生成预览」不点「插入」/「保存」⇒ **不产生文件**。
"""
import json
import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import sw_jlcfa_locate as L
import win32api
import win32con
from PIL import ImageGrab

warnings.filterwarnings("ignore")
SHOTS = Path(r"D:\AI\SW\shots\flow")
SHOTS.mkdir(parents=True, exist_ok=True)
T0 = time.time()
STEP = [0]


def log(m):
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


def click(x, y, pause=0.5):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def snap(tag):
    STEP[0] += 1
    try:
        h, w = L.connect()
        L.focus_solidworks(h)
        h, w = L.connect()
        cr = L.container_rect(w)
        if cr:
            ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
                str(SHOTS / ("%02d_%s.png" % (STEP[0], tag))))
    except Exception as e:
        log("  截图失败: %s" % str(e)[:40])


def texts(win):
    out = []
    cr = L.container_rect(win)
    if cr is None:
        return out
    for c in L._controls(win):
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if t and L._overlaps(r, cr):
            out.append((r.top, r.left, t, r))
    return out


def click_text(name, win, exact=True, tries=3):
    """按名字点插件区里的文字。读不到就返回 False。"""
    for t in range(tries):
        h, w = L.connect()
        hit = None
        for c in L._controls(w):
            try:
                if (c.window_text() or "").strip() != name:
                    continue
                r = c.rectangle()
                cr = L.container_rect(w)
                if cr and L._overlaps(r, cr):
                    hit = r
                    break
            except Exception:
                continue
        if hit:
            click((hit.left + hit.right) // 2, (hit.top + hit.bottom) // 2, 1.6)
            log("  ✓ 点「%s」%s" % (name, (hit.left, hit.top)))
            return True
        log("  ✗ 读不到「%s」（第%d次）" % (name, t + 1))
        time.sleep(0.5)
    return False


def main():
    h, w = L.connect()
    cr = L.container_rect(w)
    log("容器 %s 宽 %d" % (cr, cr.right - cr.left))
    snap("start")

    # ① 首页 -> 直线运动零件
    log("① 点「直线运动零件」")
    if not click_text("直线运动零件", w):
        snap("fail_no_cat")
        return
    snap("after_cat")
    h, w = L.connect()
    log("  面包屑/可见: %s" % [t[2][:12] for t in texts(w)[:8]])

    # ② -> 直线导轨
    log("② 点「直线导轨」")
    if not click_text("直线导轨", w):
        snap("fail_no_sub")
        return
    snap("after_sub")
    h, w = L.connect()
    ts = texts(w)
    log("  结果页可见前 14: %s" % [t[2][:14] for t in ts[:14]])
    Path(r"D:\AI\SW\flow_state.json").write_text(
        json.dumps([{"top": t[0], "left": t[1], "text": t[2]} for t in ts],
                   ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
