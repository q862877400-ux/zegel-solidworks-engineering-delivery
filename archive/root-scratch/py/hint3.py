import sys, re, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
PAT = re.compile(r"^\[\s*[\d.]+\s*~\s*[\d.]+\s*\]\s*/?\s*[\d.]*$")
h, w = L.connect(); S.cache_drop()
SR.search(h, w, "BSGY-C7-25"); time.sleep(5)
S.cache_drop(); h,w = L.connect()
pt = SR.first_result_point(h, w)
if pt: S.click(pt[0], pt[1], 2.5); time.sleep(2)
S.cache_drop(); h, w = L.connect()
allc = S.controls_cached(w); cr = S._container_from(allc)
print("容器 %s" % (cr,))
hints=[]; edits=[]
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle(); ct=c.element_info.control_type
        if not L._overlaps(r,cr): continue
        if PAT.match(t): hints.append((t,c,r))
        if ct=="Edit" and t and "请输入产品型号" not in t: edits.append((t,c,r))
    except Exception: continue
print("插件范围提示 %d 个:" % len(hints))
for t,c,r in hints: print("   %-16s @(%d,%d)" % (t, r.left, r.top))
print("输入框 %d 个:" % len(edits))
for t,c,r in edits: print("   %-16s @(%d,%d)" % (t[:14], r.left, r.top))
# ★ 关键：提示与输入框在树里是什么关系
if hints and edits:
    hc = hints[0][1]; ec = edits[0][1]
    for label, c in (("提示", hc), ("输入框", ec)):
        try:
            par = c.parent()
            print("%s 的父: %r (%s)" % (label, (par.window_text() or "")[:20], par.element_info.control_type))
        except Exception as e:
            print("%s 取父失败 %s" % (label, str(e)[:40]))
    # 同一父下的子女
    try:
        par = hc.parent()
        kids = [((k.window_text() or "").strip()[:18], k.element_info.control_type) for k in par.children()]
        print("提示之父的子女 %d: %s" % (len(kids), kids[:8]))
    except Exception as e:
        print("列子女失败 %s" % str(e)[:40])