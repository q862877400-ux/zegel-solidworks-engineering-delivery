import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_select as SEL
import sw_jlcfa_search as SR, sw_jlcfa_grid as G
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
st = S.read_state(w)
P("当前 %s pct=%s" % (S.page_kind(st), st["pct"]))
if st["pct"] != 100:
    SR.search(h, w, "BSGY-C7-25"); time.sleep(5)
    S.cache_drop(); h,w = L.connect()
    pt = SR.first_result_point(h, w); P("结果卡 %s" % (pt,))
    if pt:
        S.click(pt[0], pt[1], 2.5); time.sleep(2)
    S.cache_drop(); h,w = L.connect()
    h, w, pct = SEL.fill_to_100(h, w)
    P("填后 pct=%s" % pct)
# 点空白处让输入框失焦提交（ValuePattern 不触发正常提交）
S.cache_drop(); h, w = L.connect()
S.click(2050, 700, 0.8)
time.sleep(1.5)
S.cache_drop(); h, w = L.connect()
st = S.read_state(w)
P("失焦后 pct=%s" % st["pct"])
P("产品型号行: %s" % [n for n in st["visible"] if "BSGY" in n or "L19" in n][:3])
btn = L.locate(w, "生成预览", "Button")
P("按钮 %s" % (btn.rectangle() if btn else None))
if not btn: raise SystemExit(1)
r = btn.rectangle()
S.ensure_front(h)
P("点击 (%d,%d)" % ((r.left+r.right)//2, (r.top+r.bottom)//2))
S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 1.0)
for i in range(15):
    time.sleep(2.0)
    S.cache_drop()
    try: h,w = L.connect()
    except Exception: continue
    m = L._modal().modal_report(h)["count"]
    st = S.read_state(w)
    done = "建模完成！" in st["visible"]
    P("  %2ds 模态=%d 建模完成=%s | %s" % ((i+1)*2, m, done, (w.window_text() or "")[-46:]))
    if m: L._modal().close_modals(h, rounds=2)
    if done: break
G._capture(h,w)[0].save(r"D:\AI\SW\shots\bsgy2.png")
P("截图 bsgy2.png")