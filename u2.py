import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# ★ 滚轮要点在**内容区**，不是标签列；且这次用较小的滚动量
CX = rect.right + 200      # 内容区中部
CY = rect.top + 300
J.log("在内容区 (%d,%d) 向下滚 3 格" % (CX, CY))
J.wheel(CX, CY, -3)
time.sleep(1.2)
r2 = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("u2_scrolled", box=(rect2.right-4, rect2.top-16, r2[2], r2[3]))
J.log("完成，看 u2_scrolled_z.png")