import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
t=time.time(); st = S.read_state(w); print("第1次(遍历) %.1fs kind=%s cats=%d" % (time.time()-t, S.page_kind(st), len(st["categories"])))
for i in range(3):
    t=time.time(); st = S.read_state(w)
    print("第%d次(缓存) %.2fs kind=%s cats=%d" % (i+2, time.time()-t, S.page_kind(st), len(st["categories"])))
S.cache_drop()
t=time.time(); st = S.read_state(w); print("丢缓存后 %.1fs" % (time.time()-t))