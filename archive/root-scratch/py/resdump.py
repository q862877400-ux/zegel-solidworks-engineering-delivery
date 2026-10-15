import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = L._controls(w); cr = L.container_rect(w)
print("节点 %d  容器 %s" % (len(allc), cr))
print("page_kind=%s" % S.page_kind(S.read_state(w)))
print("型号行=%r" % F.model_line(w))
print()
print("★ 容器内 y=300..800 的所有控件（结果卡区）:")
rows=[]
for c in allc:
    try:
        r=c.rectangle(); t=(c.window_text() or "").strip()
        if not L._overlaps(r,cr): continue
        if not (cr.top+150 < r.top < cr.top+700): continue
        rows.append((r.top, r.left, c.element_info.control_type, t[:34]))
    except Exception: continue
seen=set()
for top,left,ct,t in sorted(rows):
    k=(top//6,left//6)
    if k in seen: continue
    seen.add(k)
    print("   y=%-5d x=%-5d %-9s %r" % (top-cr.top,left-cr.left,ct[:8],t))
    if len(seen)>26: break