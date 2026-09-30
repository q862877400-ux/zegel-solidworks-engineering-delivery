import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
import win32gui
r = win32gui.GetWindowRect(h)
print("SolidWorks 窗口 rect: %s  (%dx%d)" % (r, r[2]-r[0], r[3]-r[1]))
st = S.read_state(w)
print("容器: %s" % (st["container"],))
print("page_kind = %s  pct=%s  combos=%d  codes=%d" % (S.page_kind(st), st["pct"], len(st["combos"]), len(st["codes"])))
print("「返回」矩形: %s" % (L.rect_of(w, "返回"),))