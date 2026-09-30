import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 「请选择」下拉框：裁剪原点 (rect.right-4, rect.top-16)
# 裁剪图里它在 x≈300, y≈793
CX = rect.right - 4 + 300
CY = rect.top - 16 + 793
J.log("点「滑块数量」下拉 (%d,%d)" % (CX, CY))
J.click(CX, CY, pause=1.2)
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("m3_dropdown", box=(rect2.right-4, rect2.top-16,
                          min(r[2], rect2.right+470), min(r[3], rect2.top+880)))
J.log("完成，看 m3_dropdown_z.png")