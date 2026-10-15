import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("page_kind=%s" % S.page_kind(S.read_state(w)))
allc = L._controls(w); cr = L.container_rect(w)
panes = []
for c in allc:
    try:
        if c.element_info.control_type=="Pane" and L._overlaps(c.rectangle(), cr) and c.rectangle().height()>=40:
            panes.append(c)
    except Exception: continue
print("候选 Pane %d 个" % len(panes))
t=time.time()
found=[]
for c in panes:
    m, r = SR._is_card_pane(c)
    if m: found.append((m, r))
print("_is_card_pane 耗时 %.1fs，命中 %d" % (time.time()-t, len(found)))
for m,r in found[:3]:
    print("   %r %s" % (m, (r.left,r.top,r.right,r.bottom) if r else None))
print()
print("★ 直接看「型号：」/「代码：」Text 的父 Pane 是否被判为卡:")
for c in allc:
    try:
        t=(c.window_text() or "").strip()
        if not t.startswith(("型号：","代码：")): continue
        p = c.parent()
        m, r = SR._is_card_pane(p)
        print("  标签 %r 父Pnane 判定 -> %r %s" % (t[:16], m, r))
        if m is None:
            print("     父的子女: %s" % [(k.element_info.control_type,(k.window_text() or '')[:16]) for k in p.children()][:8])
        break
    except Exception as e:
        print("  失败 %s" % str(e)[:50]); break