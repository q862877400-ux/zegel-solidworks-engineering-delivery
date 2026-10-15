import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
from PIL import ImageGrab
warnings.filterwarnings("ignore")
h, w = L.connect()
L.focus_solidworks(h)
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr, "宽", cr.right-cr.left)
ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
    r"D:\AI\SW\explore\step1_catmenu.png")
print("截图 -> step1_catmenu.png")
names = []
for c in L._controls(w):
    try:
        t = (c.window_text() or "").strip(); r = c.rectangle()
    except Exception: continue
    if not t or not L._overlaps(r, cr): continue
    if r.height() < 8: continue
    names.append((r.top, r.left, c.element_info.control_type[:8], t[:24]))
print("可读元素 %d 个，前 30:" % len(names))
for top,left,ct,t in sorted(names)[:30]:
    print("   y=%-4d x=%-4d %-8s %s" % (top,left,ct,t))