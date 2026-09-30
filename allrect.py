import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
allc = S.controls_cached(w)
cr = S._container_from(allc)
print("容器 %s" % (cr,))
print()
print("★ 所有「直线运动零件」控件:")
for c in allc:
    try:
        t=(c.window_text() or "").strip()
        if t != "直线运动零件": continue
        r=c.rectangle()
        print("   %-8s (%5d,%5d,%5d,%5d) %dx%-5d 在容器内=%s"
              % (c.element_info.control_type, r.left,r.top,r.right,r.bottom,
                 r.width(), r.height(), L._overlaps(r,cr)))
    except Exception: continue
print()
print("★ 所有 100x100 卡片（看 y 范围）:")
ys=[]
for c in allc:
    try:
        r=c.rectangle(); t=(c.window_text() or "").strip()
        if abs(r.width()-100)<=3 and abs(r.height()-100)<=3 and t:
            ys.append((r.top, t[:14]))
    except Exception: continue
ys.sort()
print("   共 %d 个，y 从 %s 到 %s" % (len(ys), ys[0][0] if ys else None, ys[-1][0] if ys else None))
for y,t in ys[:12]:
    print("      y=%-6d %s" % (y,t))