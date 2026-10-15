import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 结果卡：裁剪原点 (rect.right-4, rect.top-16)，卡片中心在裁剪图约 (235, 535)
CX = rect.right - 4 + 235
CY = rect.top - 16 + 535
J.log("点结果卡 (%d,%d)" % (CX, CY))
J.click(CX, CY, pause=2.0)
time.sleep(3)
r2 = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("m2_detail", box=(rect2.right-4, rect2.top-16,
                         min(r2[2], rect2.right+470), min(r2[3], rect2.top+860)))
J.log("完成")