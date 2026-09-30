# -*- coding: utf-8 -*-
"""用 sw_gui 跑完整可靠性验证：找窗 -> 置顶 -> 控件树 -> 不受遮挡截图。"""
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32com.client as w32
import sw_gui

OUT = Path(r"D:\AI\SW\shots")
OUT.mkdir(exist_ok=True)

app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(60):
    try:
        _ = app.RevisionNumber
        break
    except Exception:
        time.sleep(1)
print("  SW", app.RevisionNumber)
try:
    app.Visible = True
    time.sleep(4)

    print()
    print("  ① 找窗口")
    w = sw_gui.wait_for_window(timeout=40)
    hwnd, title, rect = w
    print("     hwnd=%d  %r" % (hwnd, title))
    print("     rect=%s" % (rect,))

    print()
    print("  ② 置顶（校验是否真的到前台）")
    ok = sw_gui.focus_window(hwnd)
    import win32gui
    fg = win32gui.GetForegroundWindow()
    print("     focus 返回=%s  当前前台 hwnd=%d  目标=%d  一致=%s"
          % (ok, fg, hwnd, fg == hwnd))

    print()
    print("  ③ 控件树（深度 2，只读）")
    ctrls = sw_gui.dump_controls(hwnd, max_depth=2)
    print("     控件数 %d" % len(ctrls))
    for c in ctrls[:10]:
        print("       %-20s %-22s %s" % (c["type"][:18], c["name"][:20], c["rect"]))

    print()
    print("  ④ PrintWindow 截图（不受遮挡）")
    p = OUT / "sw_printwindow.png"
    img = sw_gui.capture_window(hwnd, p)
    px = img.getpixel((5, 5))
    uniq = len(set(img.getdata())) if img.size[0] * img.size[1] < 400000 else "skip"
    print("     存到 %s  尺寸=%s" % (p, img.size))
    print("     左上角像素=%s  颜色种类=%s" % (px, uniq))
    if uniq != "skip" and uniq < 12:
        print("     ⚠ 颜色过少，很可能是黑图/空图")
finally:
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    try:
        app.ExitApp()
        print("\n  收尾 ExitApp")
    except Exception:
        pass
