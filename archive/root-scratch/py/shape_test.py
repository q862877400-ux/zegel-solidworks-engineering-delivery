import sys, warnings, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc, shape_loc as SL, win32api, win32con, win32gui
from PIL import ImageGrab
warnings.filterwarnings("ignore")
hwnd, win = loc.connect()
win32api.keybd_event(win32con.VK_MENU,0,0,0); time.sleep(0.15)
try: win32gui.SetForegroundWindow(hwnd)
except Exception: pass
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(1.2)
cont = loc.find_container(win); cr = cont[2]
print("容器:", cr, "宽", cr.right-cr.left)
full = ImageGrab.grab()
pane = full.crop((cr.left, cr.top, cr.right, cr.bottom))
pane.save(r"D:\AI\SW\shots\pane_for_shape.png")
print("插件区截图:", pane.size)
rects = SL.find_blue_rects(pane)
print()
print("找到 %d 个蓝色按钮（相对插件区）:" % len(rects))
for r in rects:
    print("   (%d,%d,%d,%d)  %dx%d" % (r[0], r[1], r[2], r[3], r[2]-r[0], r[3]-r[1]))
print()
for which in ("category_btn","search_btn","search_box"):
    r = SL.locate_by_shape(win, pane, which)
    print("  %-14s -> %s" % (which, r))