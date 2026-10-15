# -*- coding: utf-8 -*-
"""按「点标签取焦点 -> 点下拉 -> 键盘选值」填一个参数，验是否生效。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl
import sw_gui_modal as M
from tap import label_rect, tap_label
import win32api
import win32con

warnings.filterwarnings("ignore")

hwnd, win = ctl.connect()


def combo_of(win, name):
    for c in win.descendants():
        try:
            if c.element_info.control_type == "ComboBox" and \
                    c.window_text().strip() == name:
                return c
        except Exception:
            continue
    return None


target = "滑块类型"
M.close_modals(hwnd)
hwnd, win = ctl.connect()
cb = combo_of(win, target)
print("目标: %s  当前值=%r" % (target, cb.selected_text().strip()), flush=True)

print("\n① 点标签取焦点", flush=True)
tap_label(win, hwnd, target)

print("\n② 点下拉框本体", flush=True)
hwnd, win = ctl.connect()
cb = combo_of(win, target)
r = cb.rectangle()
cb.click_input()
time.sleep(0.8)

print("   展开后弹窗数 =", M.modal_report(hwnd)["count"], flush=True)
M.screen_png(r"D:\AI\SW\shots\after_open_combo.png")

print("\n③ 键盘选第一项", flush=True)
for vk in (win32con.VK_DOWN, win32con.VK_RETURN):
    win32api.keybd_event(vk, 0, 0, 0)
    time.sleep(0.08)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

hwnd, win = ctl.connect()
cb = combo_of(win, target)
print("\n★ 结果: 「%s」当前值 = %r" % (target, cb.selected_text().strip()), flush=True)

import re
txt = []
for c in win.descendants():
    try:
        if c.element_info.control_type == "Text" and c.window_text():
            txt.append(c.window_text().strip())
    except Exception:
        continue
m = re.search(r"(\d+)%", " ".join(txt))
print("★ 进度: %s%%" % (m.group(1) if m else "?"), flush=True)
M.screen_png(r"D:\AI\SW\shots\after_pick.png")
