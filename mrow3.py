import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
SR.search(h, w, "EGH25SAZ0C")
for i in range(10):
    time.sleep(1.5); S.cache_drop(); h,w = L.connect()
    pt = SR.first_result_point(w)
    if pt:
        S.click(pt[0], pt[1], 2.5); break
time.sleep(2.5); S.cache_drop(); h,w = L.connect()
print("现在 %s" % S.page_kind(S.read_state(w)))
allc = L._controls(w)
for c in allc:
    try:
        t=(c.window_text() or "").strip()
        if "产品型号" not in t: continue
        r=c.rectangle()
        print("标签 %r (%d,%d)" % (t[:12], r.left, r.top))
        p=c.parent()
        pr=p.rectangle()
        print("父 %-8s %r (%d,%d,%d,%d)" % (p.element_info.control_type, (p.window_text() or '')[:16], pr.left,pr.top,pr.right,pr.bottom))
        for k in p.children():
            kr=k.rectangle()
            print("   %-9s %-28r (%d,%d,%d,%d)" % (k.element_info.control_type, (k.window_text() or '')[:26], kr.left,kr.top,kr.right,kr.bottom))
        break
    except Exception as e:
        print("失败 %s" % str(e)[:50]); break