import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = L._controls(w); cr = L.container_rect(w)
print("★ 结果卡上的标签（含「型号」「代码」「种类」「更新」的控件）:")
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if not t or not L._overlaps(r,cr): continue
        if any(k in t for k in ("型号","代码","种类","更新于")):
            print("   %-9s %-30r (%d,%d)" % (c.element_info.control_type, t[:28], r.left-cr.left, r.top-cr.top))
    except Exception: continue
print()
print("★ 结果卡区 y=380..760 内的所有控件:")
seen=set()
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if not L._overlaps(r,cr): continue
        if not (cr.top+380 < r.top < cr.top+760): continue
        if not t: continue
        k=(r.top//8, r.left//8)
        if k in seen: continue
        seen.add(k)
        print("   y=%-5d x=%-5d %-9s %r" % (r.top-cr.top, r.left-cr.left, c.element_info.control_type[:8], t[:36]))
    except Exception: continue