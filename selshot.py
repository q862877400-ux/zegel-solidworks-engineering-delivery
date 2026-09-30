import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, importlib.util
warnings.filterwarnings("ignore")
h, w = L.connect()
st = S.read_state(w)
print("kind=%s pct=%s" % (S.page_kind(st), st["pct"]))
print("ComboBox: %s" % st["combos"])
print("Button: %s" % list(st["buttons"]))
spec = importlib.util.spec_from_file_location("shot", r"D:\AI\SW\shot.py")
sh = importlib.util.module_from_spec(spec); sys.modules["shot"]=sh; spec.loader.exec_module(sh)
img, ok, W, H = sh.capture(h, r"D:\AI\SW\shots\select_now.png")
cr = st["container"]
print("容器", cr)
img.crop((cr.left, cr.top, cr.right, cr.bottom)).save(r"D:\AI\SW\shots\select_pane.png")
print("已截图 select_pane.png %dx%d" % (cr.right-cr.left, cr.bottom-cr.top))