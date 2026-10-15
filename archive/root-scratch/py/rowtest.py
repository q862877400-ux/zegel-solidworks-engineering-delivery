import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("★ 按树结构列参数行（当前页应仍是 BSGY-C7-25）:")
rows = F.param_rows(w)
print("  共 %d 行" % len(rows))
for label, ctl, r, hint, lo, hi, step in rows:
    print("   %-16s 范围=%-14s lo=%-7s hi=%-8s step=%-8s"
          % (label[:14], hint or "无", lo, hi, step))
    if lo is not None:
        print("        应填值 = %r" % F._fmt_value(lo, hi, step))
print()
print("型号行 未填=%d : %r" % (F.unfilled(w), F.model_line(w)))