import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_grid as G
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
st = S.read_state(w)
print("kind=%s pct=%s" % (S.page_kind(st), st["pct"]))
allc = S.controls_cached(w); cr = S._container_from(allc)
print("容器 %s" % (cr,))
print()
print("★ 参数区所有 输入类/下拉 控件:")
for c in allc:
    try:
        ct=c.element_info.control_type; t=(c.window_text() or "").strip(); r=c.rectangle()
        if ct not in ("ComboBox","Edit"): continue
        if not L._overlaps(r,cr): continue
        val=""
        try:
            val = c.selected_text() if ct=="ComboBox" else (c.get_value() if hasattr(c,"get_value") else c.window_text())
        except Exception: val="?"
        print("   %-9s %-22s val=%-12s (%d,%d,%d,%d)" % (ct, t[:20], str(val)[:10], r.left,r.top,r.right,r.bottom))
    except Exception: continue