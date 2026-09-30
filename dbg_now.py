import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L
from PIL import ImageGrab
warnings.filterwarnings("ignore")
hwnd, win = L.connect()
L.focus_solidworks(hwnd)
time.sleep(1.0)
hwnd, win = L.connect()
cr = L.container_rect(win)
print("容器:", cr, "宽", cr.right-cr.left, "高", cr.bottom-cr.top)
pane = ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom))
pane.save(r"D:\AI\SW\shots\pane_now2.png")
print("插件区截图:", pane.size)
print()
print("★ 插件区顶部 160 行内的控件:")
n = 0
for c in L._controls(win):
    try:
        r = c.rectangle()
        if not L._overlaps(r, cr): continue
        if not (cr.top <= r.top < cr.top + 160): continue
        n += 1
        print("   %-12s %-16r (%d,%d,%d,%d) %dx%d" % (
            c.element_info.control_type, (c.window_text() or "")[:14],
            r.left, r.top, r.right, r.bottom, r.width(), r.height()))
    except Exception: continue
print("  共", n, "个")