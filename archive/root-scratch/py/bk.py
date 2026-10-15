import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M, win32api, win32con
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
print("当前页面上的 Edit 控件:", flush=True)
for c in win.descendants():
    try:
        if c.element_info.control_type == "Edit":
            r = c.rectangle()
            print("   Edit %-16r (%d,%d,%d,%d)" % (c.window_text()[:14], r.left, r.top, r.right, r.bottom))
    except Exception:
        continue
print()
print("点「返回」回首页:", flush=True)
ret = None
for c in win.descendants():
    try:
        if c.element_info.control_type == "Text" and c.window_text().strip() == "返回":
            ret = c
            break
    except Exception:
        continue
if ret:
    r = ret.rectangle()
    ret.click_input()
    time.sleep(2.0)
    print("  已返回", flush=True)
hwnd, win = ctl.connect()
print()
print("回首页后的 Edit:", flush=True)
for c in win.descendants():
    try:
        if c.element_info.control_type == "Edit":
            r = c.rectangle()
            print("   Edit %-16r (%d,%d,%d,%d)" % (c.window_text()[:14], r.left, r.top, r.right, r.bottom))
    except Exception:
        continue
M.screen_png(r"D:\AI\SW\shots\back_home.png")