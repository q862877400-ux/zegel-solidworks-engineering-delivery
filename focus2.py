import sys, time
sys.stdout.reconfigure(encoding="utf-8")
import win32gui, win32con, win32api
hwnd = 990124
r = win32gui.GetWindowRect(hwnd)
print("  恢复后:", r, "尺寸 %dx%d" % (r[2]-r[0], r[3]-r[1]), "最小化=", win32gui.IsIconic(hwnd))
# 前台锁定：按住 Alt 再 SetForegroundWindow 是常规绕过
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.15)
try:
    win32gui.SetForegroundWindow(hwnd)
    print("  置顶(带Alt): OK")
except Exception as e:
    print("  置顶失败:", str(e)[:50])
time.sleep(0.4)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.5)
print("  当前前台 hwnd =", win32gui.GetForegroundWindow(), " 目标 =", hwnd)