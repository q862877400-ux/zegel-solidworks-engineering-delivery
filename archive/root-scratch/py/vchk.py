import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
st = S.read_state(w)
print("page_kind = %s  pct=%s codes=%d combos=%d cats=%d 可见项=%d"
      % (S.page_kind(st), st["pct"], len(st["codes"]), len(st["combos"]),
         len(st["categories"]), len(st["visible"])))
r = L.locate(w, "返回")
print("locate('返回') -> %s" % (r.rectangle() if r else None))