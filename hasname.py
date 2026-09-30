import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_cards as C
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
st = S.read_state(w)
print("kind=%s" % S.page_kind(st))
for n in ("直线运动零件","传动零部件","轴承附件","机床防护罩","首页","全部商品分类"):
    r = L.rect_of(w, n)
    print("   %-10s %s" % (n, (r.left,r.top,r.right,r.bottom) if r else "读不到"))
print()
c = C.locate_category(w, "直线运动零件", S.controls_cached(w))
print("locate_category('直线运动零件') = %s" % (c,))