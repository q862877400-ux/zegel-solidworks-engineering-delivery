import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr)
# 分类区现在滚到哪了
cats = []
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if r.top < cr.top+100 or r.top > cr.bottom: continue
    if c.element_info.control_type=="Pane" and 8<r.height()<200 and r.width()>200:
        cats.append((r.top, t[:24]))
print()
print("当前视口内的分类项（前 20）:")
for top,t in sorted(cats)[:20]:
    print("   y=%-5d %s" % (top, t))
print()
# 找滚动条，确认可拖
for c in L._controls(w):
    try:
        if c.element_info.control_type=="ScrollBar":
            r=c.rectangle()
            if r.height()>60:
                print("ScrollBar %s %dx%d at (%d,%d)" % (c.window_text()[:6], r.width(), r.height(), r.left, r.top))
    except Exception: continue