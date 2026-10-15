import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, draw_loc as D
import win32api, win32con
warnings.filterwarnings("ignore")
hwnd, win = L.connect()
L.focus_solidworks(hwnd)
hwnd, win = L.connect()
pt = D.locate_all(hwnd, win, log=print)
print()
print("★ 点搜索框:", pt.get("search_box"))
x, y = pt["search_box"]
win32api.SetCursorPos((int(x), int(y))); time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0); time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0); time.sleep(0.6)
print("  已点，打字 EGW35SA")
for ch in "EGW35SA":
    sc = win32api.VkKeyScan(ch); vk, sh = sc & 0xFF, (sc>>8)&1
    if sh: win32api.keybd_event(win32con.VK_SHIFT,0,0,0)
    win32api.keybd_event(vk,0,0,0); time.sleep(0.05)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.05)
    if sh: win32api.keybd_event(win32con.VK_SHIFT,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(0.6)
D.capture_pane(hwnd, win)
import PIL.ImageGrab as IG
img = IG.grab()
img.save(r"D:\AI\SW\shots\typed_only.png")
print("  截图 typed_only.png（看字有没有进搜索框）")