import sys, warnings, time
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc, win32api, win32con, win32gui
from PIL import ImageGrab
warnings.filterwarnings("ignore")
hwnd, win = loc.connect()
win32api.keybd_event(win32con.VK_MENU,0,0,0); time.sleep(0.15)
try: win32gui.SetForegroundWindow(hwnd)
except Exception: pass
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(1.2)
cont = loc.find_container(win); cr = cont[2]
pane = ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom))
pane.save(r"D:\AI\SW\shots\pane_now.png")
px = pane.load(); w,h = pane.size
print("插件区 %dx%d" % (w,h))
print()
print("★ 蓝色系像素的真实色值分布（取饱和蓝）:")
cnt = Counter()
for y in range(0, min(h,300), 2):
    for x in range(0, w, 2):
        r,g,b = px[x,y][:3]
        if b > 140 and b - r > 50 and b - g > 30:
            cnt[(r//16*16, g//16*16, b//16*16)] += 1
for c, n in cnt.most_common(8):
    print("   RGB%-16s %d 次" % (str(c), n))
print()
print("★ 前 300 行里蓝色像素的分布（哪一行最多）:")
rows = Counter()
for y in range(0, min(h,300)):
    n = 0
    for x in range(0, w, 3):
        r,g,b = px[x,y][:3]
        if b > 140 and b - r > 50 and b - g > 30: n += 1
    if n > 20: rows[y] = n
top = sorted(rows)[:6]
for y in top:
    print("   y=%-4d 蓝像素 %d" % (y, rows[y]))
if top:
    y0 = top[0]
    xs = [x for x in range(w) if (lambda p: p[2]>140 and p[2]-p[0]>50)(px[x,y0])]
    print()
    print("   在 y=%d 这一行，蓝色 x 从 %d 到 %d（连续 %d 像素）"
          % (y0, min(xs) if xs else -1, max(xs) if xs else -1, len(xs)))