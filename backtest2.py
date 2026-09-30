import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_click as K
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
# 取「返回」里**最小**的那个（真正的可点元素，不是容器）
hits=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if t=="返回" and r.width()>0:
            hits.append((c, r, r.width()*r.height()))
    except Exception: continue
hits.sort(key=lambda z: z[2])
c0, r0, _ = hits[0]
print("选最小的「返回」 %s %dx%d" % ((r0.left,r0.top,r0.right,r0.bottom), r0.width(), r0.height()))
S.ensure_front(h)
K.click_control(c0, 1.5)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
print("点后: %s pct=%s combos=%d cats=%d" % (S.page_kind(st), st["pct"], len(st["combos"]), len(st["categories"])))