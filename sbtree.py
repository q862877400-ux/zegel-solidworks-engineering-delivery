import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = L._controls(w); cr = L.container_rect(w)
def show(tag, c):
    try:
        r=c.rectangle()
        print("%s: %-8s %-20r (%d,%d,%d,%d)" % (tag, c.element_info.control_type, (c.window_text() or '')[:18], r.left,r.top,r.right,r.bottom))
        p = c.parent()
        print("    父 %-8s %r" % (p.element_info.control_type, (p.window_text() or '')[:24]))
        kids = [(k.element_info.control_type, (k.window_text() or '')[:18]) for k in p.children()]
        print("    父的子女 %d: %s" % (len(kids), kids[:8]))
    except Exception as e:
        print("%s 失败 %s" % (tag, str(e)[:50]))
# 搜索框 = 容器内无名 Edit
eb=None
for c in allc:
    try:
        if c.element_info.control_type=="Edit" and not (c.window_text() or '').strip() and L._overlaps(c.rectangle(),cr):
            eb=c; break
    except Exception: continue
if eb: show("搜索框", eb)
print()
sb = L.locate(w, "搜索", "Button")
if sb: show("搜索按钮", sb)
print()
print("★ 搜索框所在的父 Pane 的完整子女（看结构）:")
try:
    p = eb.parent()
    for k in p.children():
        r=k.rectangle()
        print("   %-9s %-24r (%d,%d,%d,%d)" % (k.element_info.control_type, (k.window_text() or '')[:22], r.left,r.top,r.right,r.bottom))
except Exception as e:
    print("   失败 %s" % str(e)[:60])