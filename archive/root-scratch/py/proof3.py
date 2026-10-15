import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
P("起点 未填=%d 型号行=%r" % (F.unfilled(w), F.model_line(w)))
P()
h, w, left = F.fill_all(h, w)
P()
P("★ 填后 未填=%d" % left)
P("  型号行=%r" % F.model_line(w))
row = F.row_for_label(w, "L")
if row:
    v = row[1].get_value()
    try: ok = "✓在范围内" if 0.5 <= float(v) <= 20 else "✗超范围"
    except Exception: ok = "?"
    P("  L 框内=%r 范围=%s  %s" % (v, row[3], ok))
P("  模态框=%d" % L._modal().modal_report(h)["count"])