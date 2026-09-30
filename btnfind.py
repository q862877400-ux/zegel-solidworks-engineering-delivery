import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("★ 名字为「生成预览」的所有控件（不限条件）:")
n=0
for c in S.controls_cached(w):
    try:
        t=(c.window_text() or "").strip()
        if "生成" in t or "预览" in t:
            r=c.rectangle()
            try: vis=c.is_visible()
            except Exception: vis="?"
            n+=1
            print("   %-8s %-14r (%d,%d,%d,%d) vis=%s" % (c.element_info.control_type, t[:12], r.left,r.top,r.right,r.bottom, vis))
    except Exception: continue
print("  共 %d 个" % n)
print()
print("★ 底部 80px 带内所有 Button:")
cr = L.container_rect(w)
for c in S.controls_cached(w):
    try:
        if c.element_info.control_type != "Button": continue
        r=c.rectangle()
        if cr and r.top > cr.bottom-90:
            print("   %-14r (%d,%d,%d,%d)" % ((c.window_text() or "")[:12], r.left,r.top,r.right,r.bottom))
    except Exception: continue