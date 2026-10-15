import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
P("起点 未填=%d 型号行=%r" % (F.unfilled(w), F.model_line(w)))
if F.unfilled(w) == 0:
    P("★ 已齐（上一轮 Enter 已生效）")
else:
    h, w, left = F.fill_all(h, w)
    P("填后 未填=%d 型号行=%r" % (left, F.model_line(w)))
row = F.row_for_label(w, "L")
if row: P("L 框内=%r 范围=%s" % (row[1].get_value(), row[3]))