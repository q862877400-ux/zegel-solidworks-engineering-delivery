import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_click as K
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
st = S.read_state(w)
print("当前 %s pct=%s" % (S.page_kind(st), st["pct"]))
# 列出所有名字含「返回」的控件
hits=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if "返回" in t:
            hits.append((c, t, c.element_info.control_type, r))
    except Exception: continue
print("名字含「返回」的控件 %d 个:" % len(hits))
for c,t,ct,r in hits:
    print("   %-8s %-10r (%d,%d,%d,%d) %dx%d" % (ct,t,r.left,r.top,r.right,r.bottom,r.width(),r.height()))
# 用 click_input 点第一个（不管坐标）
if hits:
    c0 = hits[0][0]
    S.ensure_front(h)
    print("用 click_input 点第一个（不碰坐标）…")
    K.click_control(c0, 1.2)
    S.cache_drop(); h,w = L.connect()
    st2 = S.read_state(w)
    print("点后: %s pct=%s" % (S.page_kind(st2), st2["pct"]))