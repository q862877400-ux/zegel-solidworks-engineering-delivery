import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("模态框 %d" % L._modal().modal_report(h)["count"])
print("未填=%d" % F.unfilled(w))
print("型号行: %r" % F.model_line(w))
print()
print("参数行（树结构）与框内真值:")
for label, ctl, r, hint, lo, hi, step in F.param_rows(w):
    try: v = ctl.get_value()
    except Exception: v = "?"
    inr = ""
    if lo is not None and v not in ("", None):
        try: inr = " ✓在范围内" if lo <= float(v) <= hi else " ✗超范围!"
        except Exception: inr = " (非数字)"
    print("   %-8s 值=%-10r 范围=%-16s%s" % (label[:6], str(v)[:10], hint, inr))