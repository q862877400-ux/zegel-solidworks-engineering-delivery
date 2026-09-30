import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc, sw_gui_modal as M, win32api, win32con, win32gui
from PIL import ImageGrab
warnings.filterwarnings("ignore")
hwnd, win = loc.connect()
M.focus_solidworks(hwnd) if hasattr(M,"focus_solidworks") else None
# 直接置前
win32api.keybd_event(win32con.VK_MENU,0,0,0); time.sleep(0.15)
try: win32gui.SetForegroundWindow(hwnd)
except Exception: pass
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(1.2)
cr = loc.find_container(win)[2]
pane = ImageGrab.grab().crop((cr.left,cr.top,cr.right,cr.bottom))
pane.save(r"D:\AI\SW\shots\pane_narrow.png")
print("容器宽", cr.right-cr.left)
print("截图", pane.size)
print()
print("★ 插件区前 200 行的控件类型分布（找搜索框是什么类型）:")
from collections import Counter
cnt = Counter()
for c in win.descendants():
    try:
        r = c.rectangle()
        if min(r.right,cr.right)-max(r.left,cr.left) <= 0: continue
        if not (cr.top <= r.top < cr.top+220): continue
        cnt[c.element_info.control_type] += 1
    except Exception: continue
for k, v in cnt.most_common():
    print("   %-16s %d" % (k, v))