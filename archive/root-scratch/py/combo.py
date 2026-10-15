# -*- coding: utf-8 -*-
"""★ 改用 ComboBox **自身的 API** 选值（不再模拟键盘）。

⚑ 前一版的错：用 Alt+↓ + ↓ 模拟按键去选下拉项，
   结果进度条 42% 纹丝不动 —— 按键事件对这个自绘 ComboBox 不生效。
   ⇒ 正确做法：``combo.select(index)`` / ``combo.item_texts()``，
   让控件自己改自己的值。
"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import warnings

warnings.filterwarnings("ignore")

hwnd, win = ctl.connect()
print("窗口:", win.window_text()[:50], flush=True)

combos = []
for c in win.descendants():
    try:
        if c.element_info.control_type != "ComboBox":
            continue
        r = c.rectangle()
    except Exception:
        continue
    if r.height() < 10:
        continue
    combos.append((c.window_text().strip(), c, r))

print("找到 %d 个 ComboBox" % len(combos), flush=True)
print()
for nm, c, r in combos[:6]:
    try:
        items = c.item_texts()
    except Exception as e:
        items = ["<读不到: %s>" % str(e)[:30]]
    try:
        cur = c.selected_text()
    except Exception:
        cur = "?"
    print("  %-14s 当前=%-12s 选项 %d 个: %s"
          % (nm, cur, len(items), items[:6]), flush=True)
