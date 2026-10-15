import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, win32api, win32con, uiautomation as auto, shot
hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
print("  目标:", repr(win32gui.GetWindowText(hwnd)[:50]))
root = auto.ControlFromHandle(hwnd)
try:
    root.SetActive()
except Exception: pass
time.sleep(0.8)
# DPI：控件坐标 1519..1553 是物理像素，需与光标坐标同空间
X, Y = 1536, 368
print("  点击 (%d,%d) —— 标签列第 9 个（嘉立创）" % (X, Y))
win32api.SetCursorPos((X, Y))
time.sleep(0.4)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.15)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print("  已点，等插件加载…")
time.sleep(6)
t2 = win32gui.GetWindowText(hwnd)
print("  窗口标题:", repr(t2[:56]))
img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\after_click.png")
print("  截图 ok=%s  %dx%d" % (ok, w, h))
pane = img.crop((1510, 60, 2040, 500))
pane.save(r"D:\AI\SW\shots\after_pane.png")
print("  窗格区: D:\\AI\\SW\\shots\\after_pane.png", pane.size)