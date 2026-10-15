# -*- coding: utf-8 -*-
"""完整演示：换一个新类别（欧标 4040 铝型材），从搜索到生成，全程计时。"""
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
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
T0 = time.time()


def el(msg):
    print("[%5.1fs] %s" % (time.time() - T0, msg), flush=True)


def click(x, y, pause=0.15):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.05)
    win32api.mouse_event(win32con.VOUSEEVENTF_LEFTDOWN if False else
                        win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def drag(x1, y1, x2, y2, steps=10):
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.35)


def typ(s):
    for ch in s:
        sc = win32api.VkKeyScan(ch)
        vk, sh = sc & 0xFF, (sc >> 8) & 1
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.035)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.035)
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)


class P:
    def __init__(self):
        self.hwnd, self.win = ctl.connect()
        self.refresh()

    def refresh(self):
        self.cb, self.lb, self.ed, self.btn, self.sx = {}, {}, {}, None, None
        for c in self.win.descendants():
            try:
                ct = c.element_info.control_type
                t = c.window_text().strip()
                r = c.rectangle()
            except Exception:
                continue
            if ct == "ComboBox" and r.height() >= 10:
                self.cb[t] = (c, r)
            elif ct == "Edit" and t:
                self.ed[t] = (c, r)
            elif ct in ("Pane", "Text") and r.width() > 250 and t:
                self.lb[t] = r
            elif ct == "Button":
                if t == "生成预览":
                    self.btn = (c, r)
                elif r.width() <= 30 and r.height() >= 100:
                    self.sx = max(self.sx or 0, r.left)

    def pct(self):
        t = []
        for c in self.win.descendants():
            try:
                if c.element_info.control_type == "Text" and c.window_text():
                    t.append(c.window_text().strip())
            except Exception:
                continue
        m = re.search(r"(\d+)%", " ".join(t))
        return int(m.group(1)) if m else None

    def guard(self):
        if M.modal_report(self.hwnd)["count"]:
            M.close_modals(self.hwnd, rounds=2)
            self.hwnd, self.win = ctl.connect()
            self.refresh()


def main():
    KEY = "TXCL-H6-4040R"
    p = P()
    el("连接，进度 %s%%" % p.pct())
    base = {x.name for x in BF.iterdir() if x.is_file() and not x.name.startswith("~$")}

    # ① 搜索框
    sb = None
    for c in p.win.descendants():
        try:
            if c.element_info.control_type != "Edit":
                continue
            r = c.rectangle()
            # 搜索框：无标题、位于插件顶部（top<300）、横向较宽
            if r.top < 300 and r.left > 1400 and r.width() > 200:
                sb = c
                break
        except Exception:
            continue
    if sb is None:
        el("✗ 找不到搜索框"); return 1
    sb.click_input(); time.sleep(0.35)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord("A"), 0, 0, 0); time.sleep(0.06)
    win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    for _ in range(26):
        win32api.keybd_event(win32con.VK_BACK, 0, 0, 0); time.sleep(0.012)
        win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.012)
    typ(KEY); time.sleep(0.4)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0); time.sleep(0.06)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    el("已搜索 %s，等结果" % KEY)

    # ② 等结果卡
    card = None
    for _ in range(20):
        time.sleep(0.7)
        p.hwnd, p.win = ctl.connect(); p.refresh()
        for c in p.win.descendants():
            try:
                if c.element_info.control_type == "Text" and KEY in (c.window_text() or ""):
                    card = c
            except Exception:
                continue
        if card:
            break
    if not card:
        el("✗ 没等到结果卡"); M.screen_png(r"D:\AI\SW\shots\demo_nocard.png"); return 1
    el("结果卡出现，点它")
    card.click_input()
    time.sleep(3.2)
    p.hwnd, p.win = ctl.connect(); p.refresh()
    el("进详情，进度 %s%%" % p.pct())

    # ③ 填参数
    for it in range(1, 14):
        p.guard()
        p.refresh()
        if p.pct() == 100:
            break
        empty = [n for n, (c, r) in p.cb.items()
                 if c.selected_text().strip() == "请选择"]
        if not empty:
            if p.sx:
                drag(p.sx + 8, 700, p.sx + 8, 460); p.refresh()
                if not any(c.selected_text().strip() == "请选择"
                           for c, _ in p.cb.values()):
                    drag(p.sx + 8, 460, p.sx + 8, 700); p.refresh()
                    if not any(c.selected_text().strip() == "请选择"
                               for c, _ in p.cb.values()):
                        break
                continue
            break
        nm = empty[0]
        lr = p.lb.get(nm)
        if lr:
            click((lr.left + lr.right) // 2, (lr.top + lr.bottom) // 2, 0.1)
        p.hwnd, p.win = ctl.connect(); p.refresh()
        if nm not in p.cb:
            continue
        c, r = p.cb[nm]
        c.click_input(); time.sleep(0.6)
        p.guard()
        click((r.left + r.right) // 2, r.bottom + 14 + 30, 0.4)
        p.hwnd, p.win = ctl.connect(); p.refresh()
        el("  %-10s  %s%%" % (nm, p.pct()))

    # ④ Edit
    p.refresh()
    if p.pct() != 100:
        for nm, (e, r) in list(p.ed.items()):
            if not nm.strip():
                continue
            e.click_input(); time.sleep(0.3)
            typ("400")
            time.sleep(0.4)
            win32api.keybd_event(win32con.VK_TAB, 0, 0, 0); time.sleep(0.06)
            win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)
            p.hwnd, p.win = ctl.connect(); p.refresh()
            el("  输入 %s -> %s%%" % (nm, p.pct()))
            break

    p.guard(); p.refresh()
    el("最终进度 %s%%" % p.pct())
    M.screen_png(r"D:\AI\SW\shots\demo_before_gen.png")
    if p.pct() != 100:
        el("⚠ 未到 100%"); return 1

    # ⑤ 生成
    p.refresh()
    if not p.btn:
        el("✗ 无生成按钮"); return 1
    el("点「生成预览」")
    p.btn[0].click_input()
    for _ in range(60):
        time.sleep(0.4)
        now = {x.name for x in BF.iterdir() if x.is_file()
               and not x.name.startswith("~$")}
        new = sorted(now - base)
        if new:
            el("★★ %s" % new)
            M.screen_png(r"D:\AI\SW\shots\demo_done.png")
            return 0
    el("超时"); M.screen_png(r"D:\AI\SW\shots\demo_timeout.png")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
