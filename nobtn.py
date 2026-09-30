import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_grid as G
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
st = S.read_state(w)
print("kind=%s pct=%s" % (S.page_kind(st), st["pct"]))
print("可见按钮: %s" % sorted(k for k in st["buttons"]))
print("可见名里有「生成」? %s" % [n for n in st["visible"] if "生成" in n])
print("可见名里有「插入」「保存」? %s" % [n for n in st["visible"] if n in ("插入","保存","选型PDF")])
print()
print("★ 所有名为「生成预览」的控件（不限可见）:")
allc = S.controls_cached(w); cr = S._container_from(allc)
for c in allc:
    try:
        if (c.window_text() or "").strip() != "生成预览": continue
        r=c.rectangle()
        try: vis=c.is_visible()
        except Exception: vis="?"
        print("   %-6s (%d,%d,%d,%d) vis=%s 容器内=%s" % (c.element_info.control_type, r.left,r.top,r.right,r.bottom, vis, L._overlaps(r,cr)))
    except Exception: continue
print()
pane,_ = G._capture(h,w); pane.save(r"D:\AI\SW\shots\nobtn.png")
print("截图 nobtn.png %s" % (pane.size,))