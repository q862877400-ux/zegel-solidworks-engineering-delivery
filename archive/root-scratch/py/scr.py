import sys
sys.stdout.reconfigure(encoding="utf-8")
import win32gui, win32process, subprocess
mon = win32api = None
import win32api as A
print("  显示器数:", A.GetSystemMetrics(94), " 虚拟屏:",
      A.GetSystemMetrics(76), A.GetSystemMetrics(77), A.GetSystemMetrics(78), A.GetSystemMetrics(79))
def cb(h, _):
    if win32gui.IsWindowVisible(h):
        t = win32gui.GetWindowText(h)
        if t.startswith("SOLIDWORKS"):
            r = win32gui.GetWindowRect(h)
            print("  hwnd=%d rect=%s  尺寸=%dx%d" % (h, r, r[2]-r[0], r[3]-r[1]))
            print("     最小化=%s 最大化=%s" % (win32gui.IsIconic(h), win32gui.IsZoomed(h)))
win32gui.EnumWindows(cb, None)