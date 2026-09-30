import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_select as SEL, sw_jlcfa_grid as G
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
st = S.read_state(w)
print("kind=%s pct=%s" % (S.page_kind(st), st["pct"]))
print()
print("待填下拉: %s" % [p[0] for p in SEL.pending_params(w)])
print("待填输入框: %s" % [(e[0], e[3]) for e in SEL.pending_edits(w)])
print()
allc = S.controls_cached(w); cr = S._container_from(allc)
print("★ 参数区 Edit/ComboBox 当前值:")
for c in allc:
    try:
        ct=c.element_info.control_type; t=(c.window_text() or "").strip(); r=c.rectangle()
        if ct not in ("ComboBox","Edit") or not L._overlaps(r,cr): continue
        if t=="请输入产品型号/关键字": continue
        try: v = c.get_value() if ct=="Edit" else c.selected_text()
        except Exception: v="?"
        print("   %-9s %-22s %r" % (ct, t[:20], str(v)[:16]))
    except Exception: continue
G._capture(h,w)[0].save(r"D:\AI\SW\shots\at90.png")