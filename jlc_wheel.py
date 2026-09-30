import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import jlc_auto as J
hwnd = J.sw_window()
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
mx = rect.right + 200
my = rect.top + 300
J.log("真滚轮下滚 (x=%d,y=%d)" % (mx, my))
J.wheel(mx, my, -6)
time.sleep(1.5)
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("s8_wheel", box=(rect2.right-4, rect2.top-16,
                        min(r[2], rect2.right+470), min(r[3], rect2.top+700)))
J.log("完成")