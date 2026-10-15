import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M, win32api, win32con
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
print("准备搜索另一个型号", flush=True)
# 点搜索框
for c in win.descendants():
    try:
        if c.element_info.control_type == "Edit" and c.rectangle().top < 260 and c.rectangle().left > 1500:
            r = c.rectangle(); break
    except Exception:
        continue
else:
    print("找不到搜索框"); raise SystemExit(1)
c.click_input(); time.sleep(0.4)
win32api.keybd_event(win32con.VK_CONTROL,0,0,0); win32api.keybd_event(ord("A"),0,0,0)
time.sleep(0.08); win32api.keybd_event(ord("A"),0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(0.2)
for _ in range(24):
    win32api.keybd_event(win32con.VK_BACK,0,0,0); time.sleep(0.015)
    win32api.keybd_event(win32con.VK_BACK,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.015)
for ch in "EGW35SA":
    vk = win32api.VkKeyScan(ch) & 0xFF; sh = (win32api.VkKeyScan(ch) >> 8) & 1
    if sh: win32api.keybd_event(win32con.VK_SHIFT,0,0,0)
    win32api.keybd_event(vk,0,0,0); time.sleep(0.04)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.04)
    if sh: win32api.keybd_event(win32con.VK_SHIFT,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(0.5)
win32api.keybd_event(win32con.VK_RETURN,0,0,0); time.sleep(0.08)
win32api.keybd_event(win32con.VK_RETURN,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(4.5)
hwnd, win = ctl.connect()
res = [c for c in win.descendants() if c.element_info.control_type=="Text" and "结果" in (c.window_text() or "")]
print("搜索结果:", [c.window_text().strip() for c in res][:2], flush=True)
M.screen_png(r"D:\AI\SW\shots\opt_search.png")