import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api, win32con, win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
J.ensure_window(hwnd)
J.log("按 Alt+Down 展开下拉（或直接按 Down 选第一项）")
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)
time.sleep(0.1)
win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(1.0)
r = J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
J.snap("m4_altdown", box=(rect.right-4, rect.top-16,
                        min(r[2], rect.right+470), min(r[3], rect.top+900)))
J.log("再看 m4，再按 ↓ 选第一项")