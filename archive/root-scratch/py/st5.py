import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr, "宽", cr.right-cr.left)
items=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle(); ct=c.element_info.control_type
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if not (cr.top+120 <= r.top <= cr.bottom-30): continue
    if ct in ("Pane","Text") and 8 < r.height() < 120 and r.width() > 100:
        items.append((r.top, r.left, ct, t[:24]))
seen=set(); out=[]
for top,left,ct,t in sorted(items):
    if t in seen: continue
    seen.add(t); out.append((top,left,ct,t))
print()
print("★ 视口内元素 %d 个:" % len(out))
for top,left,ct,t in out[:28]:
    print("   y=%-5d x=%-5d %-6s %s" % (top,left,ct,t))