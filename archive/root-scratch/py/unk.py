import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
st = S.read_state(w)
print("kind=%s  可见=%d" % (S.page_kind(st), len(st["visible"])))
print("容器 %s" % (st["container"],))
print()
print("可见名（前 40）:")
for n in sorted(st["visible"])[:40]:
    print("   %r" % n)
print()
print("方形卡候选 %d: %s" % (len(st["categories"]), st["categories"][:12]))
print()
# 看看有多少 80~220 的方形控件
allc = S.controls_cached(w); cr = S._container_from(allc)
sq=[]
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if 80<=r.width()<=220 and 80<=r.height()<=220 and t and L._overlaps(r,cr):
            sq.append((t[:16], r.left, r.top, r.width(), r.height()))
    except Exception: continue
print("方形控件（不限 y）%d:" % len(sq))
for t,l,tp,w2,h2 in sq[:16]:
    print("   %-16s x=%-5d y=%-5d %dx%d" % (t,l,tp,w2,h2))