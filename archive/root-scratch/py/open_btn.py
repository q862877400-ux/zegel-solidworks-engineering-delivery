# -*- coding: utf-8 -*-
"""点 ComboBox 右侧的「打开」按钮，再读展开的选项。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import warnings

warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()


def find_combo(win, name):
    for c in win.descendants():
        try:
            if c.element_info.control_type == "ComboBox" and \
                    c.window_text().strip() == name:
                return c
        except Exception:
            continue
    return None


cb = find_combo(win, "滑块数量")
if cb is None:
    print("找不到滑块数量")
    raise SystemExit(1)

r = cb.rectangle()
# 同一行的「打开」按钮：右侧贴边
bx, by = r.right - 20, (r.top + r.bottom) // 2
print("点「滑块数量」右侧的打开按钮 (%d,%d)" % (bx, by))
import win32api
import win32con
win32api.SetCursorPos((int(bx), int(by)))
time.sleep(0.15)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.08)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(1.5)

hwnd, win = ctl.connect()
print()
print("★ 展开后 y>950 区域的新控件（下拉列表通常在这里）:")
n = 0
for c in win.descendants():
    try:
        ct = c.element_info.control_type
        nm = c.window_text().strip()
        rr = c.rectangle()
    except Exception:
        continue
    if not nm:
        continue
    if ct in ("ListItem", "MenuItem", "TreeItem") or (rr.top > 400 and rr.width() < 300
                                                      and rr.height() < 60):
        n += 1
        print("   %-10s %-22s (%d,%d,%d,%d)" % (ct, nm[:20], rr.left, rr.top,
                                                 rr.right, rr.bottom))
        if n >= 24:
            break
print("  共 %d 个" % n)
