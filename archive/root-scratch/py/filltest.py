import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("型号行: %r" % F.model_line(w))
print("未填数: %d" % F.unfilled(w))
print("焦点: %s" % F.set_front(h))
h, w, left = F.fill_all(h, w)
print("补填后 未填=%d 型号行: %r" % (left, F.model_line(w)))
print("进度: %s%%" % S.read_state(w)["pct"])