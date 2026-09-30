# -*- coding: utf-8 -*-
"""点开 ComboBox 后，看展开的选项是否进入 UIA 树（ListItem）。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import warnings

warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()

# 找第一个未填的 ComboBox
target = None
for c in win.descendants():
    try:
        if c.element_info.control_type != "ComboBox":
            continue
        if c.window_text().strip() == "滑块数量" and c.selected_text().strip() == "请选择":
            target = c
            break
    except Exception:
        continue
if target is None:
    print("找不到「滑块数量」空框")
    raise SystemExit(1)

r = target.rectangle()
print("点「滑块数量」%s" % ((r.left, r.top, r.right, r.bottom),))
target.click_input()
time.sleep(1.2)

hwnd, win = ctl.connect()
print()
print("★ 展开后新增的控件（找 ListItem / 带文字的项）:")
n = 0
for c in win.descendants():
    try:
        ct = c.element_info.control_type
        nm = c.window_text().strip()
        rr = c.rectangle()
    except Exception:
        continue
    if ct in ("ListItem", "List", "MenuItem") or (nm and rr.left > 1550
                                                 and rr.width() < 400):
        if not nm:
            continue
        n += 1
        print("   %-10s %-24s (%d,%d,%d,%d)" % (ct, nm[:22], rr.left, rr.top,
                                                 rr.right, rr.bottom))
        if n >= 20:
            break
print("  共 %d 个" % n)
