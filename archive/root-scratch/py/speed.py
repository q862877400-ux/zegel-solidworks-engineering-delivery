import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
t=time.time(); h,w = L.connect(); print("connect: %.1fs" % (time.time()-t))
for i in range(3):
    t=time.time(); st = S.read_state(w); dt=time.time()-t
    print("read_state 第%d次: %.1fs  kind=%s pct=%s codes=%d cats=%d combos=%d"
          % (i+1, dt, S.page_kind(st), st["pct"], len(st["codes"]),
             len(st["categories"]), len(st["combos"])))