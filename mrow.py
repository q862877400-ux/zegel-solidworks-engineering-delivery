import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = L._controls(w)
print("★ 「产品型号：」标签的父与兄弟:")
for c in allc:
    try:
        if (c.window_text() or "").strip() not in ("产品型号：","产品型号:"): continue
        r=c.rectangle()
        print("  标签 (%d,%d,%d,%d)" % (r.left,r.top,r.right,r.bottom))
        p=c.parent()
        print("  父: %-8s %r" % (p.element_info.control_type, (p.window_text() or '')[:20]))
        for k in p.children():
            kr=k.rectangle()
            print("     %-9s %-28r (%d,%d,%d,%d)" % (k.element_info.control_type, (k.window_text() or '')[:26], kr.left,kr.top,kr.right,kr.bottom))
        break
    except Exception as e:
        print("  失败 %s" % str(e)[:50]); break