import sys, re, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
PAT = re.compile(r"^\[\s*[\d.]+\s*~\s*[\d.]+\s*\]\s*/\s*[\d.]+$")
h, w = L.connect(); S.cache_drop()
allc = S.controls_cached(w); cr = S._container_from(allc)
print("容器 %s" % (cr,))
hits = []
for c in allc:
    try:
        t = (c.window_text() or "").strip()
        if PAT.match(t):
            r = c.rectangle()
            hits.append((t, c, r))
    except Exception: continue
print("★ 精确匹配的插件范围提示 %d 个:" % len(hits))
for t, c, r in hits:
    print("   %-18s (%d,%d) 类型=%s" % (t, r.left, r.top, c.element_info.control_type))
    # 找同一行左侧的 Edit（= 它标注的输入框）
    same = []
    for c2 in allc:
        try:
            if c2.element_info.control_type != "Edit": continue
            r2 = c2.rectangle()
            if abs(r2.top - r.top) <= 12 and r2.right <= r.left + 5:
                same.append(((c2.window_text() or "").strip(), r2))
        except Exception: continue
    for nm, r2 in same:
        print("        ← 同行输入框 %r (%d,%d,%d,%d)" % (nm[:14], r2.left,r2.top,r2.right,r2.bottom))