import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_click as K
warnings.filterwarnings("ignore")
h, w = L.connect()
for i in range(9):
    S.cache_drop(); h, w = L.connect()
    st = S.read_state(w)
    k = S.page_kind(st)
    r = L.rect_of(w, "返回")
    print("%d) %-10s 控件可见=%-3d 代码卡=%-2d 分类卡=%-2d combos=%-2d  返回=%s"
          % (i, k, len(st["visible"]), len(st["codes"]), len(st["categories"]),
             len(st["combos"]), (r.left, r.top) if r else None))
    if k == "HOME":
        print("   ★ 已到首页"); break
    if r is None:
        print("   没有「返回」了"); break
    S.ensure_front(h)
    S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 1.6)