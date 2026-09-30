import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = S.controls_cached(w); cr = S._container_from(allc)
# 找带范围提示的文字
hints = [c for c in allc if (c.window_text() or "").strip().startswith("[") and "~" in (c.window_text() or "")]
print("范围提示 %d 个" % len(hints))
if hints:
    hc = hints[0]
    hr = hc.rectangle()
    print("样例: %r @ (%d,%d,%d,%d)" % (hc.window_text().strip(), hr.left,hr.top,hr.right,hr.bottom))
    # 它的父链
    try:
        par = hc.parent()
        print("  父: %r 类型=%s" % ((par.window_text() or "")[:30], par.element_info.control_type))
        sibs = [ ( (s.window_text() or "").strip()[:22], s.element_info.control_type) for s in par.children() ]
        print("  父的子女 %d 个:" % len(sibs))
        for t,ct in sibs[:12]:
            print("      %-10s %r" % (ct, t))
    except Exception as e:
        print("  取父失败 %s" % str(e)[:60])