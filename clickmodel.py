import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_cards as C, sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
st = S.read_state(w)
S.log("当前 %s  型号 %d" % (S.page_kind(st), len(st["codes"])))
pt = C.locate_code(w, "EGH25SAZ0C")
S.log("定位「EGH25SAZ0C」-> %s" % (pt,))
if pt is None:
    S.log("可见: %s" % [c for c,_,_ in C.visible_codes(w)]); raise SystemExit(1)
S.ensure_front(h)
S.log("点击 %s" % (pt,))
S.click(pt[0], pt[1], 1.0)
S.cache_drop()
time.sleep(2.5)
h, w = L.connect()
st = S.read_state(w)
S.log("点后: %s  ComboBox %s  进度 %s  生成按钮 %s"
      % (S.page_kind(st), list(st["combos"])[:8], st["pct"], "生成预览" in st["buttons"]))
S.evidence("model_click", h, w, st, note="点型号卡 EGH25SAZ0C 后")