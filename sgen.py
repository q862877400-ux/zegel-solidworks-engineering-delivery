import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_grid as G, sw_jlcfa_select as SEL
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
st = S.read_state(w)
print("当前 %s pct=%s 可见「建模完成」=%s" % (S.page_kind(st), st["pct"], "建模完成！" in st["visible"]))
# 先填参数（若需要）
h, w, pct = SEL.fill_to_100(h, w)
print("填参后 %s%%" % pct)
S.cache_drop(); h, w = L.connect()
btn = L.locate(w, "生成预览", "Button")
if btn is None:
    print("✗ 找不到「生成预览」"); raise SystemExit(1)
r = btn.rectangle()
print("点「生成预览」%s" % ((r.left,r.top,r.right,r.bottom),))
S.ensure_front(h)
S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 1.0)
for i in range(20):
    time.sleep(1.5)
    S.cache_drop()
    try: h,w = L.connect()
    except Exception: continue
    st = S.read_state(w)
    if "建模完成！" in st["visible"]:
        print("★ 建模完成（%ds）" % int((i+1)*1.5)); break
else:
    print("未出现「建模完成」")
print("SW 标题: %s" % (w.window_text() or "")[:90])
G._capture(h,w)[0].save(r"D:\AI\SW\shots\s3.png")