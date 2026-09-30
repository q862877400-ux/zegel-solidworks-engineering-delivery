import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api, win32con, win32gui, jlc_auto as J
hwnd = J.sw_window()
r0 = J.ensure_window(hwnd)
J.log("当前 %s 尺寸 %dx%d" % (r0, r0[2]-r0[0], r0[3]-r0[1]))
# 最大化
win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
time.sleep(1.8)
r = J.ensure_window(hwnd)
J.log("最大化后 %s 尺寸 %dx%d" % (r, r[2]-r[0], r[3]-r[1]))
import ctypes
sw = ctypes.windll.user32
sw.SetProcessDPIAware()
r2 = win32gui.GetWindowRect(hwnd)
J.log("DPIAware 后 rect=%s 尺寸 %dx%d" % (r2, r2[2]-r2[0], r2[3]-r2[1]))
_root, rect = J.tab_column(hwnd)
J.log("标签列 %s  列高=%d" % (rect, rect.bottom-rect.top if rect else -1))
import shot
img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\max.png")
J.log("截图 %dx%d ok=%s" % (w, h, ok))