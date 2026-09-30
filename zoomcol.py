import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, uiautomation as auto, shot
hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
print("  窗口:", repr(win32gui.GetWindowText(hwnd)[:52]))
root = auto.ControlFromHandle(hwnd); root.SetActive(); time.sleep(1.0)
img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\user_sw.png")
print("  截图 %dx%d ok=%s" % (w, h, ok))
col = img.crop((1513, 90, 1561, 390))
col = col.resize((col.width*5, col.height*5), 5)
col.save(r"D:\AI\SW\shots\user_tabcol.png")
print("  标签列放大: D:\\AI\\SW\\shots\\user_tabcol.png", col.size)