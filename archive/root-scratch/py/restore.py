import sys, time
sys.stdout.reconfigure(encoding="utf-8")
import win32gui, win32con
hwnd = 990124
print("  恢复前:", win32gui.GetWindowRect(hwnd), "最小化=", win32gui.IsIconic(hwnd))
win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
time.sleep(1.5)
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.8)
r = win32gui.GetWindowRect(hwnd)
print("  恢复后:", r, "尺寸 %dx%d" % (r[2]-r[0], r[3]-r[1]), "最小化=", win32gui.IsIconic(hwnd))