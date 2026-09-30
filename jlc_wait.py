import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
hwnd = J.sw_window()
for i in range(8):
    time.sleep(3)
    r = J.ensure_window(hwnd)
    _root, rect = J.tab_column(hwnd)
    J.snap("s4_wait_%d" % (i+1), box=(rect.right-4, rect.top-16,
                                       min(r[2], rect.right+470), min(r[3], rect.top+500)))
J.log("8 轮截图完成")