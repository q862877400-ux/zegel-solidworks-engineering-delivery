# -*- coding: utf-8 -*-
"""步骤 5：点搜索结果卡，进型号详情页。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
import jlc_auto as J

hwnd = J.sw_window()
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 结果卡在面板里大约 y = rect.top + 400（从截图量：s5 图里卡片顶部在裁剪图 y≈490）
# 裁剪原点是 (rect.right-4, rect.top-16)，卡片图片中心在裁剪图约 (110, 530)
# ⇒ 窗口坐标 (rect.right-4+110, rect.top-16+530)
CX = rect.right - 4 + 110
CY = rect.top - 16 + 530
J.log("结果卡位置约 (%d,%d) —— 点它" % (CX, CY))
J.click(CX, CY, pause=2.5)
J.ensure_window(hwnd)
for i in range(4):
    time.sleep(2.5)
    r2 = J.ensure_window(hwnd)
    _root, rect2 = J.tab_column(hwnd)
    J.snap("s6_detail_%d" % (i + 1),
           box=(rect2.right - 4, rect2.top - 16,
                min(r2[2], rect2.right + 470), min(r2[3], rect2.top + 700)))
J.log("完成，看 s6_detail_4_z.png")
