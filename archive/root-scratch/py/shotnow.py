import sys, time, warnings, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("shot", r"D:\AI\SW\shot.py")
sh = importlib.util.module_from_spec(spec); sys.modules["shot"]=sh; spec.loader.exec_module(sh)
h, w = L.connect()
S.cache_drop()
st = S.read_state(w)
print("kind=%s 容器=%s" % (S.page_kind(st), st["container"]))
img, ok, W, H = sh.capture(h, r"D:\AI\SW\shots\now_state.png")
cr = st["container"]
img.crop((cr.left, cr.top, cr.right, cr.bottom)).save(r"D:\AI\SW\shots\now_pane.png")
print("截图 now_pane.png %dx%d" % (cr.right-cr.left, cr.bottom-cr.top))