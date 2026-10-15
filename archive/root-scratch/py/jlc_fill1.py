import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 「【去填写】」第一段：裁剪图里约 (135, 176)
CX = rect.right - 4 + 135
CY = rect.top - 16 + 176
J.log("点第一个【去填写】(%d,%d)" % (CX, CY))
J.click(CX, CY, pause=1.5)
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("m6_fill1", box=(rect2.right-4, rect2.top-16,
                       min(r[2], rect2.right+470), min(r[3], rect2.top+900)))
J.log("完成")