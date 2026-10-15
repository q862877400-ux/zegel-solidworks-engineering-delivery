import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_grid as G
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = S.controls_cached(w); cr = S._container_from(allc)
print("★ 参数区 y=860..1100 的所有控件（含文字）:")
rows=[]
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle(); ct=c.element_info.control_type
        if not (860 <= r.top <= 1100): continue
        if not L._overlaps(r,cr): continue
        rows.append((r.top, r.left, ct, t[:34]))
    except Exception: continue
for top,left,ct,t in sorted(rows):
    print("   y=%-5d x=%-5d %-9s %r" % (top,left,ct[:8],t))