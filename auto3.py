# -*- coding: utf-8 -*-
"""滚轮无效 -> 改用拖右侧滚动条（用户口述的可行路径）。"""
import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import sw_gui_modal as M
import win32api
import win32con

warnings.filterwarnings("ignore")
SHOTS = Path(r"D:\AI\SW\shots\auto3")
SHOTS.mkdir(parents=True, exist_ok=True)
STEP = [0]


def shot(tag):
    STEP[0] += 1
    M.screen_png(str(SHOTS / ("%02d_%s.png" % (STEP[0], tag))))


def combos(win):
    out = []
    for c in win.descendants():
        try:
            if c.element_info.control_type == "ComboBox" and \
                    c.rectangle().height() >= 10:
                out.append((c.window_text().strip(), c))
        except Exception:
            continue
    return out


def pct(win):
    t = []
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Text" and c.window_text():
                t.append(c.window_text().strip())
        except Exception:
            continue
    m = re.search(r"(\d+)%", " ".join(t))
    return int(m.group(1)) if m else None


def click(x, y, pause=0.25):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def drag(x1, y1, x2, y2, steps=12):
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.03)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.6)


def scrollbar_x(win):
    """插件内容区右侧的竖滚动条 x（最靠右的窄 ScrollBar）。"""
    best = None
    for c in win.descendants():
        try:
            if c.element_info.control_type != "ScrollBar":
                continue
            r = c.rectangle()
            if r.width() > 30 or r.height() < 100:
                continue
            if best is None or r.left > best:
                best = r.left
        except Exception:
            continue
    return best


def main():
    hwnd, win = ctl.connect()
    M.close_modals(hwnd)
    hwnd, win = ctl.connect()
    print("起始:", pct(win), "%", flush=True)
    shot("start")
    sx = scrollbar_x(win)
    print("滚动条 x =", sx, flush=True)

    for rnd in range(1, 12):
        cs = dict(combos(win))
        empty = [n for n, c in combos(win)
                 if c.selected_text().strip() == "请选择"]
        print("轮%d 进度=%s%% 空项=%s" % (rnd, pct(win), empty), flush=True)
        if not empty:
            break
        name = empty[0]
        cb = cs[name]
        r = cb.rectangle()
        if r.top > 880:
            print("   「%s」y=%d 在屏外 -> 拖滚动条" % (name, r.top), flush=True)
            if sx:
                drag(sx + 8, 700, sx + 8, 450, steps=12)
            else:
                click(r.left + 150, r.top - 300)
            shot("scrolled")
            hwnd, win = ctl.connect()
            continue
        print("   填「%s」y=%d" % (name, r.top), flush=True)
        cb.click_input()
        time.sleep(0.9)
        shot("open_" + name)
        if M.modal_report(hwnd)["count"]:
            M.close_modals(hwnd); hwnd, win = ctl.connect(); continue
        click((r.left + r.right) // 2, r.bottom + 14 + 30, pause=0.7)
        shot("picked_" + name)
        hwnd, win = ctl.connect()
        v = dict((n, c.selected_text().strip()) for n, c in combos(win)).get(
            name, "(不在屏)")
        print("   -> %r  %s%%" % (v, pct(win)), flush=True)
        if pct(win) == 100:
            print("★★ 100%"); shot("pct100"); break


if __name__ == "__main__":
    main()
