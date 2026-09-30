# -*- coding: utf-8 -*-
"""修订版：每步截图 + 目标不在屏内时先滚动。

⚑ 上一版死循环的根因：**「滑块数量」等控件的坐标在窗口矩形内，
   但插件自己的滚动容器已经把它们滚出可视区** ⇒ 点空气。
   ⇒ 判据必须用「控件是否在**插件列表的可视高度**内」，
   而不是「在窗口矩形内」。
"""
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
SHOTS = Path(r"D:\AI\SW\shots\auto2")
SHOTS.mkdir(parents=True, exist_ok=True)
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
STEP = [0]


def shot(tag):
    STEP[0] += 1
    p = SHOTS / ("%02d_%s.png" % (STEP[0], tag))
    M.screen_png(str(p))
    return p


def pane_rect(win):
    """插件参数区的可视区（从第一个参数标签到最后一个的下沿）。"""
    labels = []
    for c in win.descendants():
        try:
            if c.element_info.control_type in ("Pane", "Text") and c.window_text():
                r = c.rectangle()
                if r.width() > 250 and 500 < r.height() <= 60 and r.left > 1500:
                    labels.append(r)
        except Exception:
            continue
    if not labels:
        return None
    top = min(r.top for r in labels)
    return top


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
    txt = []
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Text" and c.window_text():
                txt.append(c.window_text().strip())
        except Exception:
            continue
    m = re.search(r"(\d+)%", " ".join(txt))
    return int(m.group(1)) if m else None


def click(x, y, pause=0.25):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def scroll(amount):
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, amount * 120, 0)
    time.sleep(0.5)


def label_of(win, name):
    for c in win.descendants():
        try:
            if c.window_text().strip() == name and \
                    c.element_info.control_type in ("Pane", "Text"):
                r = c.rectangle()
                if r.width() > 250:
                    return r
        except Exception:
            continue
    return None


def main():
    hwnd, win = ctl.connect()
    M.close_modals(hwnd)
    hwnd, win = ctl.connect()
    print("起始进度:", pct(win), "%", flush=True)
    base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    shot("start")

    for rnd in range(1, 30):
        rep = M.modal_report(hwnd)
        if rep["count"]:
            print("[模态] 关", flush=True); shot("modal")
            M.close_modals(hwnd); hwnd, win = ctl.connect()

        cs = combos(win)
        if not cs:
            print("轮%d: 没有 ComboBox" % rnd, flush=True); shot("nocombo"); break
        # 目标 = 第一个值仍为「请选择」的；若都不在屏内，滚动找
        target = None
        for nm, c in cs:
            try:
                if c.selected_text().strip() == "请选择":
                    target = (nm, c); break
            except Exception:
                continue
        if not target:
            print("轮%d: 本屏全填完（进度 %s%%）" % (rnd, pct(win)), flush=True)
            shot("screen_full"); break

        name, cb = target
        r = cb.rectangle()
        top = pane_rect(win) or r.top
        BOT = 900
        if r.top > BOT or r.bottom < top:
            print("   目标「%s」不在可视区(y=%d)，下滚" % (name, r.top), flush=True)
            click(r.left + 150, top + 40)          # 点列表空白取焦点
            scroll(-3)
            shot("scrolled_for_" + name)
            hwnd, win = ctl.connect()
            continue

        print("轮%d: 填「%s」at y=%d（进度 %s%%）" % (rnd, name, r.top, pct(win)),
              flush=True)
        lr = label_of(win, name)
        if lr:
            click((lr.left + lr.right) // 2, (lr.top + lr.bottom) // 2)
        shot("tap_" + name)

        hwnd, win = ctl.connect()
        cb = None
        for nm2, c2 in combos(win):
            if nm2 == name:
                cb = c2; break
        if cb is None:
            print("   控件消失，重排了", flush=True); continue
        r = cb.rectangle()
        cb.click_input(); time.sleep(0.9)
        shot("open_" + name)

        if M.modal_report(hwnd)["count"]:
            print("   ⚠ 弹模态，关", flush=True); shot("modal2")
            M.close_modals(hwnd); hwnd, win = ctl.connect(); continue

        click((r.left + r.right) // 2, r.bottom + 14 + 30, pause=0.7)
        shot("picked_" + name)
        hwnd, win = ctl.connect()
        val = dict((n, c.selected_text().strip()) for n, c in combos(win)).get(
            name, "(不在本屏)")
        print("   -> %s = %r  进度 %s%%" % (name, val, pct(win)), flush=True)
        if pct(win) == 100:
            print("★★ 100%", flush=True); shot("pct100"); break

    hwnd, win = ctl.connect()
    M.close_modals(hwnd); hwnd, win = ctl.connect()
    btn = None
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Button" and \
                    c.window_text().strip() == "生成预览":
                btn = c; break
        except Exception:
            continue
    if not btn:
        print("✗ 无「生成预览」"); shot("nobtn"); return 1
    print("\n点「生成预览」", flush=True)
    btn.click_input(); time.sleep(1.0); shot("clicked")
    for i in range(24):
        time.sleep(5)
        now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
        new = sorted(now - base)
        if new:
            print("★ %ds 新增: %s" % ((i + 1) * 5, new), flush=True)
            shot("done"); return 0
    print("120s 无新增"); shot("timeout"); return 2


if __name__ == "__main__":
    raise SystemExit(main())
