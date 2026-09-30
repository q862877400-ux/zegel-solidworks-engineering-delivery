import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_select as SEL
warnings.filterwarnings("ignore")
h, w = L.connect()
if L._modal().modal_report(h)["count"]:
    L._modal().close_modals(h, rounds=2); h, w = L.connect()
st = S.read_state(w)
print("起点 %s 进度 %s%%" % (S.page_kind(st), st["pct"]))
h, w, pct = SEL.fill_to_100(h, w)
print("填充后进度 %s%%" % pct)
if pct == 100:
    S.cache_drop(); h, w = L.connect()
    btn = L.locate(w, "生成预览", "Button")
    if btn:
        S.ensure_front(h)
        r = btn.rectangle()
        print("点「生成预览」%s" % ((r.left,r.top,r.right,r.bottom),))
        S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 1.0)
        time.sleep(8)
        S.cache_drop(); h, w = L.connect()
        print("SW 标题: %s" % w.window_text()[:74])
        S.evidence("generated", h, w, S.read_state(w), note="生成预览后")