import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr, " 宽", cr.right-cr.left)
# 结果页的筛选器 ComboBox（之前验证过能读到）
combos=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle(); ct=c.element_info.control_type
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if ct=="ComboBox":
        combos.append((r.top, r.left, t, c.selected_text().strip()))
print()
print("★ 筛选器 ComboBox %d 个（相对容器）:" % len(combos))
for top,left,t,v in sorted(combos)[:10]:
    print("   y=%-4d x=%-4d %-14s = %s   相对 x=%.1f%% y=%.1f%%"
          % (top, left, t, v,
             100.0*(left-cr.left)/(cr.right-cr.left),
             100.0*(top-cr.top)/(cr.bottom-cr.top)))
print()
print("★ 面包屑 / 型号代码:")
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if "代码：" in t or (10<r.height()<40 and r.top < cr.top+300 and r.width()>100):
        print("   y=%-4d %-24s" % (r.top, t[:22]))