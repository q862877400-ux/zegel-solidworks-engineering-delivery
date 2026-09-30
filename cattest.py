import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_cards as C
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
cards = C.category_cards(w)
print("容器宽 %d  分类卡 %d 张:" % (cr.right-cr.left, len(cards)))
for t, r in cards[:20]:
    print("   %-26s (%d,%d,%d,%d)" % (t, r.left, r.top, r.right, r.bottom))
print()
r = C.locate_category(w, "直线导轨")
print("locate_category('直线导轨') =", r)