import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_click as K
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
r = L.locate(w, "返回")
S.ensure_front(h)
K.click_control(r, 2.0)
S.cache_drop(); h, w = L.connect()
st = S.read_state(w)
print("点「返回」后 page_kind = %s" % S.page_kind(st))
print("容器 %s" % (st["container"],))
print("pct=%s codes=%d cards=%d" % (st["pct"], len(st["codes"]), len(st["categories"])))
print()
print("★ 容器内所有可见名字（%d）:" % len(st["visible"]))
for n in sorted(st["visible"]):
    print("   %r" % n)
print()
print("★ 卡片（80~220 正方形）%d:" % len(st["categories"]))
for t in st["categories"][:24]:
    print("   %r" % t)