# -*- coding: utf-8 -*-
"""自主模式：每步截图确认 —— 跑通全流程用。

纪律：
  · 每个动作后**立即整屏截图**（PrintWindow 会丢客户区外的弹窗）
  · 每步检查模态窗，有就报出来并关掉
  · 控件找不到/读不到**不崩**，记录后换策略
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

SHOTS = Path(r"D:\AI\SW\shots\auto")
SHOTS.mkdir(parents=True, exist_ok=True)
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")

STEP = [0]


def shot(tag):
    STEP[0] += 1
    p = SHOTS / ("%02d_%s.png" % (STEP[0], tag))
    M.screen_png(str(p))
    return p


def snap_state(win):
    """读当前界面状态。"""
    out = {"combos": [], "pct": None, "texts": []}
    for c in win.descendants():
        try:
            ct = c.element_info.control_type
            t = c.window_text().strip()
            if ct == "ComboBox" and c.rectangle().height() >= 10:
                out["combos"].append((t, c.selected_text().strip()))
            elif ct == "Text" and t:
                out["texts"].append(t)
        except Exception:
            continue
    m = re.search(r"(\d+)%", " ".join(out["texts"]))
    if m:
        out["pct"] = int(m.group(1))
    return out


def label_rect(win, name):
    best = None
    for c in win.descendants():
        try:
            if c.window_text().strip() != name:
                continue
            if c.element_info.control_type not in ("Pane", "Text"):
                continue
            r = c.rectangle()
            if r.width() < 30:
                continue
            if best is None or r.width() > best.width():
                best = r
        except Exception:
            continue
    return best


def combo_obj(win, name):
    for c in win.descendants():
        try:
            if c.element_info.control_type == "ComboBox" and \
                    c.window_text().strip() == name:
                return c
        except Exception:
            continue
    return None


def click(x, y, pause=0.25):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def main():
    hwnd, win = ctl.connect()
    st = snap_state(win)
    print("起始: 进度=%s%%  空下拉=%s" % (st["pct"], [n for n, v in st["combos"]
                                              if v == "请选择"]), flush=True)
    base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    print("BuildFile %d 个\n" % len(base), flush=True)
    shot("start")

    for rnd in range(1, 25):
        rep = M.modal_report(hwnd)
        if rep["count"]:
            print("[模态] %d 个 -> 关" % rep["count"], flush=True)
            shot("modal")
            M.close_modals(hwnd)
            hwnd, win = ctl.connect()

        st = snap_state(win)
        empty = [n for n, v in st["combos"] if v == "请选择"]
        if not empty:
            print("轮%d: 本屏无空下拉（进度 %s%%）" % (rnd, st["pct"]), flush=True)
            shot("no_empty")
            break
        name = empty[0]
        print("轮%d: 填「%s」（进度 %s%%）" % (rnd, name, st["pct"]), flush=True)

        # ① 点标签取焦点
        lr = label_rect(win, name)
        if lr:
            click((lr.left + lr.right) // 2, (lr.top + lr.bottom) // 2)
        shot("tap_label_" + name)

        # ② 点下拉展开
        hwnd, win = ctl.connect()
        cb = combo_obj(win, name)
        if cb is None:
            print("   下拉找不到（可能已填/重排），跳过", flush=True)
            continue
        r = cb.rectangle()
        cb.click_input()
        time.sleep(0.9)
        shot("open_" + name)

        rep = M.modal_report(hwnd)
        if rep["count"]:
            print("   ⚠ 展开时弹模态 -> 关", flush=True)
            shot("modal_on_open")
            M.close_modals(hwnd)
            hwnd, win = ctl.connect()
            continue

        # ③ 点第一个非「请选择」项
        item_y = r.bottom + 14 + 30
        item_x = (r.left + r.right) // 2
        click(item_x, item_y, pause=0.7)
        shot("picked_" + name)

        hwnd, win = ctl.connect()
        st2 = snap_state(win)
        newval = dict(st2["combos"]).get(name, "(不在本屏)")
        print("   -> %s = %r  进度 %s%%" % (name, newval, st2["pct"]), flush=True)
        if st2["pct"] == 100:
            print("★★ 100% 达成", flush=True)
            shot("pct100")
            break

    # 生成
    hwnd, win = ctl.connect()
    M.close_modals(hwnd)
    hwnd, win = ctl.connect()
    btn = None
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Button" and \
                    c.window_text().strip() == "生成预览":
                btn = c
                break
        except Exception:
            continue
    if not btn:
        print("✗ 没有「生成预览」按钮", flush=True)
        shot("no_button")
        return 1
    print("\n点「生成预览」", flush=True)
    btn.click_input()
    time.sleep(1.0)
    shot("clicked_generate")
    for i in range(24):
        time.sleep(5)
        now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
        new = sorted(now - base)
        if new:
            print("★ %ds 新增: %s" % ((i + 1) * 5, new), flush=True)
            shot("generated")
            return 0
    print("120 秒无新增", flush=True)
    shot("timeout")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
