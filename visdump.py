import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
st = S.read_state(w)
print("当前 kind=%s pct=%s" % (S.page_kind(st), st["pct"]))
print("可见控件名（%d 个）:" % len(st["visible"]))
for n in sorted(st["visible"])[:50]:
    print("   %r" % n)
print()
print("类别候选（前 20）: %s" % st["categories"][:20])