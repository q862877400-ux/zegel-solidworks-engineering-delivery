# -*- coding: utf-8 -*-
"""控件驱动：逐个填参数 -> 100% -> 生成。"""
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api
import win32con
import ctl

BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")

PICK = ("滑块固定方式", "滑块类型", "滑块数量", "防尘配件",
        "预压", "精度等级", "代码", "滑块形状", "直线导轨类型", "种类")


def all_combos(win):
    out = []
    for c in win.descendants():
        try:
            if c.element_info.control_type != "ComboBox":
                continue
            r = c.rectangle()
        except Exception:
            continue
        out.append((c.window_text().strip(), c, r))
    return out


def pick_first(ctrl):
    """ComboBox：Alt+↓ 展开，↓ 选第一项。"""
    ctrl.click_input()
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)
    time.sleep(0.08)
    win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.25)
    win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)
    time.sleep(0.06)
    win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.25)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.06)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.4)


def read_progress(win):
    """从界面文字里读「共有 N 个备选型号」和进度（进度条百分比读不到就明说）。"""
    txt = []
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Text" and c.window_text():
                txt.append(c.window_text().strip())
        except Exception:
            continue
    joined = " | ".join(txt)
    m = re.search(r"共有\s*(\d+)\s*个备选型号\s*(\d+)%", joined)
    if m:
        return int(m.group(1)), int(m.group(2)), joined
    m = re.search(r"(\d+)%", joined)
    return None, (int(m.group(1)) if m else None), joined


hwnd, win = ctl.connect()
print("窗口:", win.window_text()[:52], flush=True)
n, pct, joined = read_progress(win)
print("  备选型号=%s 进度=%s%%" % (n, pct), flush=True)
print()
print("  读到的界面文字（节选）:", flush=True)
print("   ", joined[:220], flush=True)
print()

base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
print("生成前 BuildFile %d 个" % len(base), flush=True)

for round_no in range(1, 10):
    combos = all_combos(win)
    empty = [(nm, c, r) for nm, c, r in combos if nm in PICK and r.height() > 0]
    if not empty:
        print("  轮 %d: 本屏没有待填的 ComboBox" % round_no, flush=True)
        break
    nm, c, r = empty[0]
    print("  轮 %d: 填「%s」(%d,%d)" % (round_no, nm, r.left, r.top), flush=True)
    pick_first(c)
    time.sleep(0.5)
    hwnd, win = ctl.connect()          # ★ 动作后重连（ref 会失效）
    n2, p2, _ = read_progress(win)
    print("      -> 进度 %s%%" % p2, flush=True)
    if p2 == 100:
        print("  ★★ 100% 达成", flush=True)
        break

hwnd, win = ctl.connect()
n, pct, joined = read_progress(win)
print()
print("最终: 备选 %s 进度 %s%%" % (n, pct), flush=True)

btn = None
for c in win.descendants():
    try:
        if c.element_info.control_type == "Button" and \
                c.window_text().strip() == "生成预览":
            btn = c
            break
    except Exception:
        continue
if btn:
    r = btn.rectangle()
    print("点「生成预览」%s" % ((r.left, r.top, r.right, r.bottom),), flush=True)
    btn.click_input()
    time.sleep(1.0)
    for i in range(18):
        time.sleep(5)
        now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
        new = sorted(now - base)
        if new:
            print("  ★ %ds 新增: %s" % ((i+1)*5, new), flush=True)
            break
    else:
        print("  90 秒无新增", flush=True)
else:
    print("✗ 找不到「生成预览」按钮", flush=True)
