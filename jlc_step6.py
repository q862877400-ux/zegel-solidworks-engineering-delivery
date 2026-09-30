# -*- coding: utf-8 -*-
"""步骤 6：滚下面板，看剩余参数 + 生成按钮在哪。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
import jlc_auto as J

hwnd = J.sw_window()
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
J.log("标签列 %s" % (rect,))
# 在面板内容区里滚（x 取内容区中部，避开标签列）
mx = rect.right + 200
my_top = rect.top + 200
my_bot = rect.bottom - 20
for i in range(4):
    my = my_top + (my_bot - my_top) * 0.5
    J.log("  滚轮下滚 (x=%d,y=%d)" % (mx, my))
    J.drag(mx, my, mx, my - 400, steps=14)   # 用拖动模拟滚轮
    time.sleep(1.2)
    r2 = J.ensure_window(hwnd)
    _root, rect2 = J.tab_column(hwnd)
    J.snap("s7_scroll_%d" % (i + 1),
           box=(rect2.right - 4, rect2.top - 16,
                min(r2[2], rect2.right + 470), min(r2[3], rect2.top + 700)))
J.log("完成，看 s7_scroll_4_z.png")
