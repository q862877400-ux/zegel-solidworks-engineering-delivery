import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = S.controls_cached(w); cr = S._container_from(allc)
print("容器 %s" % (cr,))
print()
print("★ 含「产品型号」或「去填写」的控件:")
for c in allc:
    try:
        t = (c.window_text() or "")
        if "产品型号" in t or "去填写" in t or "CPDH" in t:
            r = c.rectangle()
            print("   %-10s %-40r (%d,%d)" % (c.element_info.control_type, t[:38], r.left, r.top))
    except Exception: continue
print()
print("★ 容器内 y<300 的所有文字（型号行应在这里）:")
rows=[]
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if t and L._overlaps(r,cr) and r.top < cr.top+260:
            rows.append((r.top, r.left, c.element_info.control_type, t[:40]))
    except Exception: continue
for top,left,ct,t in sorted(rows)[:20]:
    print("   y=%-5d x=%-5d %-9s %r" % (top-cr.top, left-cr.left, ct[:8], t))