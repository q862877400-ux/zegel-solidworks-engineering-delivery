import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L, draw_loc as D, sb3
warnings.filterwarnings("ignore")
h, win = L.connect()
L.focus_solidworks(h)
h, win = L.connect()
pane, cr = D.capture_pane(h, win)
print("插件区 %dx%d" % pane.size)
rows = sb3.white_with_text_rows(pane)
print("候选行 %d 个" % len(rows))
for l,y,r,ink in rows[:12]:
    print("   x=%d..%d y=%d 宽=%d 墨=%d" % (l, r, y, r-l, ink))