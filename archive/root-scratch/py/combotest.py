import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
allc = S.controls_cached(w)
cr = S._container_from(allc)
target=None
for c in allc:
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if c.element_info.control_type=="ComboBox" and t=="滑块类型" and L._overlaps(r,cr):
            target=c; print("找到滑块类型 %s" % ((r.left,r.top,r.right,r.bottom),)); break
    except Exception: continue
if target is None: print("找不到"); raise SystemExit(1)
# A) 展开后读列表项
S.ensure_front(h)
target.click_input(); time.sleep(1.0)
S.cache_drop()
h,w = L.connect()
items=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); ct=c.element_info.control_type
        if t and ct in ("ListItem","ListItem","MenuItem","DataItem"):
            items.append((ct,t))
    except Exception: continue
print("展开后 ListItem 类元素 %d 个: %s" % (len(items), items[:8]))
# B) ComboBox 自身的 items()/texts()
try:
    print("combo.items() -> %s" % (target.texts()[:6],))
except Exception as e:
    print("combo.texts() 失败:", str(e)[:50])
# C) 直接 select
try:
    target.select(0)
    print("select(0) 成功")
except Exception as e:
    print("select(0) 失败:", str(e)[:60])
time.sleep(1.0)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
print("结果: 进度 %s%%  滑块类型=%r" % (st["pct"], st["combos"].get("滑块类型")))