import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api, win32con, win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
def type_text(s):
    for ch in s:
        scan = win32api.VkKeyScan(ch); vk, sh = scan & 0xFF, (scan>>8)&1
        if sh: win32api.keybd_event(win32con.VK_SHIFT,0,0,0)
        win32api.keybd_event(vk,0,0,0); time.sleep(0.045)
        win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0)
        if sh: win32api.keybd_event(win32con.VK_SHIFT,0,win32con.KEYEVENTF_KEYUP,0)
        time.sleep(0.045)
def focus(h):
    win32api.keybd_event(win32con.VK_MENU,0,0,0); time.sleep(0.12)
    try: win32gui.SetForegroundWindow(h)
    except Exception: pass
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_MENU,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.4)
hwnd = J.sw_window(); focus(hwnd)
J.ensure_window(hwnd)
# 搜索框（之前量到 (1680,132)）
J.click(1680, 132, pause=0.9)
J.ensure_window(hwnd)
# Ctrl+A 清空
win32api.keybd_event(win32con.VK_CONTROL,0,0,0); win32api.keybd_event(ord("A"),0,0,0)
time.sleep(0.1); win32api.keybd_event(ord("A"),0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(0.3)
for _ in range(20):
    win32api.keybd_event(win32con.VK_BACK,0,0,0); time.sleep(0.02)
    win32api.keybd_event(win32con.VK_BACK,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.02)
type_text("E-LMHP13LUU")   # 直线轴承，参数简单
time.sleep(0.6)
win32api.keybd_event(win32con.VK_RETURN,0,0,0); time.sleep(0.1)
win32api.keybd_event(win32con.VK_RETURN,0,win32con.KEYEVENTF_KEYUP,0)
J.log("已搜 E-LMHP13LUU，等结果…")
time.sleep(6)
r = J.ensure_window(hwnd); _root, rect = J.tab_column(hwnd)
J.snap("m7_simple", box=(rect.right-4, rect.top-16,
                        min(r[2], rect.right+470), min(r[3], rect.top+860)))
J.log("完成")