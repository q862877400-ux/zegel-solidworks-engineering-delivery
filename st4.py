import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr)
print()
print("★ hover 状态下视口内的分类项：")
items=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        ct=c.element_info.control_type
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if not (cr.top+100 <= r.top <= cr.bottom-20): continue
    if ct in ("Pane","Text") and 8 < r.height() < 160 and r.width() > 150:
        items.append((r.top, ct, t[:26]))
seen=set()
for top,ct,t in sorted(items)[:24]:
    if t in seen: continue
    seen.add(t)
    print("   y=%-5d %-6s %s" % (top, ct, t))
print()
for c in L._controls(w):
    try:
        if c.element_info.control_type=="ScrollBar":
            r=c.rectangle()
            if r.height()>60:
                print("ScrollBar at (%d,%d) %dx%d" % (r.left, r.top, r.width(), r.height()))
    except Exception: continue