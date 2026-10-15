# -*- coding: utf-8 -*-
"""B 路线：点开 ComboBox 后截**整屏**（含屏幕外/浮窗部分）。

⚑ 我之前所有截图都只截 SolidWorks 窗口（PrintWindow）。
   若下拉列表是**独立浮窗**（不在 SolidWorks 的客户区里），
   那些截图压根不含它 ⇒ 这可能就是「点开了却没反应/选不中」的真因。
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import win32api
import win32con
import win32gui
from PIL import ImageGrab

warnings.filterwarnings("ignore")

hwnd, win = ctl.connect()

# 找「滑块数量」这个空 ComboBox
cb = None
for c in win.descendants():
    try:
        if c.element_info.control_type == "ComboBox" and \
                c.window_text().strip() == "滑块数量" and \
                c.selected_text().strip() == "请选择":
            cb = c
            break
    except Exception:
        continue
if cb is None:
    print("找不到空的「滑块数量」")
    raise SystemExit(1)

r = cb.rectangle()
print("点「滑块数量」(%d,%d,%d,%d)" % (r.left, r.top, r.right, r.bottom), flush=True)
cb.click_input()
time.sleep(1.5)

# ★ 整屏截图
full = ImageGrab.grab()
full.save(r"D:\AI\SW\shots\screen_after_open.png")
print("整屏截图 %s" % (full.size,), flush=True)

# 同时列出当前所有可见窗口（浮窗会在这里露出来）
print()
print("★ 点开后的可见窗口:")
def cbw(h, _):
    if win32gui.IsWindowVisible(h):
        t = win32gui.GetWindowText(h)
        r2 = win32gui.GetWindowRect(h)
        if t and (r2[2]-r2[0]) > 20:
            print("   hwnd=%-9d %-46s %s" % (h, t[:44], r2), flush=True)
win32gui.EnumWindows(cbw, None)
