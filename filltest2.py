import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
import sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("当前型号行: %r  未填=%d" % (F.model_line(w), F.unfilled(w)))
print("— 搜索 BSGY-C7-25 验证判据 —")
SR.search(h, w, "BSGY-C7-25"); time.sleep(5)
S.cache_drop(); h,w = L.connect()
pt = SR.first_result_point(h, w)
if pt: S.click(pt[0], pt[1], 2.5); time.sleep(2)
S.cache_drop(); h,w = L.connect()
print("进详情后型号行: %r  未填=%d" % (F.model_line(w), F.unfilled(w)))
h, w, left = F.fill_all(h, w)
print("★ 补填后 未填=%d  型号行: %r" % (left, F.model_line(w)))
print("  进度 %s%%" % S.read_state(w)["pct"])