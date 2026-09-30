import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
cr = L.container_rect(w)
print("容器 %s" % (cr,))
allc = S.controls_cached(w)
print("全树节点 %d" % len(allc))
inb = [c for c in allc if L._overlaps(c.rectangle(), cr)]
print("容器内 %d" % len(inb))
print()
print("★ 容器内 y > %d 的所有控件（底部条带）:" % (cr.bottom-90))
rows=[]
for c in inb:
    try:
        r=c.rectangle(); t=(c.window_text() or "").strip()
        if r.top > cr.bottom-90:
            rows.append((r.top, r.left, c.element_info.control_type, t[:26]))
    except Exception: continue
for top,left,ct,t in sorted(rows)[:26]:
    print("   y=%-5d x=%-5d %-10s %r" % (top,left,ct[:8],t))
print("   共 %d" % len(rows))
print()
# 树是否被截断：从容器元素本身往下走
cont = None
for c in allc:
    try:
        if (c.window_text() or "").strip() in L.CONTAINER_NAMES:
            r=c.rectangle()
            if r.width()>40 and r.height()>40: cont=c
    except Exception: continue
if cont is not None:
    try:
        sub = list(cont.descendants())
        print("★ 从容器元素自身 descendants(): %d 个" % len(sub))
        hits = [ (c.element_info.control_type, c.rectangle()) for c in sub if (c.window_text() or "").strip()=="生成预览" ]
        print("   其中「生成预览」: %d 个 %s" % (len(hits), [(t,(r.left,r.top)) for t,r in hits]))
    except Exception as e:
        print("   失败 %s" % str(e)[:60])