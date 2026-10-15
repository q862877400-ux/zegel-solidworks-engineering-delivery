# -*- coding: utf-8 -*-
"""步骤 1：确保插件面板正常显示（拖动刷新），再截图标定位置。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import jlc_auto as J

hwnd = J.sw_window()
import win32gui
J.log("窗口: %r" % win32gui.GetWindowText(hwnd)[:52])

root, rect = J.tab_column(hwnd)
J.log("标签列: %s" % (rect,))
if rect is None:
    J.log("✗ 没找到标签列")
    raise SystemExit(1)

# ★ 先拖动刷新（用户口述：从 0 启动后内容会卡住）
J.refresh_pane(hwnd, rect)
time.sleep(2)

# 重新取坐标（布局可能因拖动变了）
root, rect2 = J.tab_column(hwnd)
J.log("拖动后标签列: %s" % (rect2,))
r = rect2 or rect
h_total = r.bottom - r.top
J.log("列高 %d" % h_total)

J.snap("s1_after_drag", box=(r.left - 8, r.top - 20, r.right + 300, min(r.bottom + 40, 700)))

# 逐格估算
J.log("9 格的话每格 %.1f px，最下面那格中心 y≈%d" % (h_total / 9.0, r.top + h_total - h_total / 18.0))
