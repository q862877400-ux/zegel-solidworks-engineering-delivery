import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
# 读所有 100x100 的元素（卡片本体）
print("★ 卡片本体（100x100）里存的名字：")
cards=[]
for c in L._controls(w):
    try:
        r=c.rectangle(); ct=c.element_info.control_type; t=(c.window_text() or "").strip()
    except Exception: continue
    if abs(r.width()-100)<=3 and abs(r.height()-100)<=3 and L._overlaps(r,cr):
        cards.append((r.top, r.left, ct, t))
for top,left,ct,t in sorted(cards):
    print("   y=%-4d x=%-4d %-8s %r" % (top,left,ct[:8],t[:30]))
print()
print("★ 卡片附近的可读文字（含被截断的）:")
seen=set()
for c in L._controls(w):
    try:
        r=c.rectangle(); ct=c.element_info.control_type; t=(c.window_text() or "").strip()
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if 340 <= r.top <= 620 and r.width() < 200:
        if t in seen: continue
        seen.add(t)
        print("   %-8s %r" % (ct[:8], t[:36]))