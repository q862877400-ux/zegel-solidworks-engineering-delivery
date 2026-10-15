# -*- coding: utf-8 -*-
"""用控件驱动跑：读状态 -> 填参数 -> 生成。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import win32api
import win32con

BF = (r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin "
      r"Full Version v2.4.1-20260918-1\ForFaceSelector\BuildFile")
from pathlib import Path
BF = Path(BF)

hwnd, win = ctl.connect()
print("窗口已连:", win.window_text()[:56], flush=True)

print()
print("=== 当前可按名字操作的控件 ===", flush=True)
for name in ("生成预览", "插入", "保存", "搜索", "清除所有", "返回"):
    c = ctl.find(win, name)
    r = c.rectangle() if c else None
    print("  %-10s %s" % (name, ("%s (%d,%d,%d,%d)" % (
        c.element_info.control_type, r.left, r.top, r.right, r.bottom)) if c else "**没找到**"),
        flush=True)

print()
print("=== 参数区的下拉框 ===", flush=True)
# ComboBox / 下拉在 UIA 里通常是 ComboBox 或 Pane
combos = []
for c in win.descendants():
    try:
        ct = c.element_info.control_type
    except Exception:
        continue
    if ct in ("ComboBox", "Edit", "Button"):
        r = c.rectangle()
        if r.width() > 80 and 15 < r.height() < 45 and r.left > 1500:
            combos.append((ct, c.window_text(), r))
for ct, nm, r in combos[:14]:
    print("  %-10s %-16s (%d,%d,%d,%d)" % (ct, nm[:14], r.left, r.top, r.right, r.bottom),
          flush=True)
print("  共 %d 个" % len(combos), flush=True)
