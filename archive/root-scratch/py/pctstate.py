import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
st = S.read_state(w)
print("进度 %s%%" % st["pct"])
for c in S.controls_cached(w):
    try:
        t=(c.window_text() or "").strip()
        if c.element_info.control_type!="ComboBox" or not t: continue
        items=c.texts(); cur=c.selected_text().strip()
        if items:
            print("  %-10s 当前=%-8s 选项=%s" % (t, cur, items))
    except Exception as e: pass