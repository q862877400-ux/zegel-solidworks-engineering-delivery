import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
cr = L.container_rect(w)
print("★ 结果卡标签的父链结构:")
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip()
        if not t.startswith(("型号：","代码：")): continue
        r=c.rectangle()
        print("  标签 %r (%d,%d)" % (t[:20], r.left, r.top))
        p = c.parent()
        print("    父: %-8s %r" % (p.element_info.control_type, (p.window_text() or '')[:20]))
        for k in p.children():
            kr=k.rectangle()
            print("       %-9s %-26r (%d,%d,%d,%d)" % (k.element_info.control_type, (k.window_text() or '')[:24], kr.left,kr.top,kr.right,kr.bottom))
        break
    except Exception as e:
        print("  失败 %s" % str(e)[:50]); break