import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_cards as C
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = L._controls(w)
cr = L.container_rect(w)
print("并集节点 %d  容器 %s" % (len(allc), cr))
print()
print("★ ① 搜索框（此前靠截图找）：插件区内的 Edit")
n=0
for c in allc:
    try:
        ct=c.element_info.control_type; t=(c.window_text() or "").strip(); r=c.rectangle()
        if ct!="Edit": continue
        if not L._overlaps(r,cr): continue
        n+=1
        print("   Edit %-22r (%d,%d,%d,%d)" % (t[:20], r.left,r.top,r.right,r.bottom))
    except Exception: continue
print("   共 %d 个" % n)
print()
print("★ ② 「搜索」按钮（此前靠截图推出搜索框位置）:")
for c in allc:
    try:
        if (c.window_text() or "").strip()=="搜索":
            r=c.rectangle()
            print("   %-8s (%d,%d,%d,%d)" % (c.element_info.control_type, r.left,r.top,r.right,r.bottom))
    except Exception: continue
print()
print("★ ③ 结果卡（「代码：xxx」标签）:")
codes = [ (t, c.rectangle()) for c in allc for t in [(c.window_text() or "").strip()] if t.startswith("代码：") ]
print("   共 %d 个: %s" % (len(codes), [t[:14] for t,_ in codes[:5]]))
for t,r in codes[:3]:
    print("      %-18s (%d,%d,%d,%d)" % (t[:16], r.left,r.top,r.right,r.bottom))