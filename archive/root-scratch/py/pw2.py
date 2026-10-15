import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import importlib.util
spec = importlib.util.spec_from_file_location("shot", r"D:\AI\SW\shot.py")
shot = importlib.util.module_from_spec(spec); sys.modules["shot"]=shot; spec.loader.exec_module(shot)
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L
import win32gui, win32process, subprocess
warnings.filterwarnings("ignore")
# 找 sldworks 窗口
cands=[]
def cb(h,_):
    if win32gui.IsWindowVisible(h):
        t=win32gui.GetWindowText(h)
        if t and t.upper().startswith("SOLIDWORKS"):
            cands.append(h)
win32gui.EnumWindows(cb,None)
print("SOLIDWORKS 窗口:", cands)
if not cands: raise SystemExit(1)
hwnd=cands[0]
img, ok, W, H = shot.capture(hwnd, r"D:\AI\SW\shots\pw_fixed.png")
print("PrintWindow ok=%s  %dx%d" % (ok, W, H))
cr = L.container_rect(L.connect()[1])
print("容器:", cr, "宽", cr.right-cr.left)
c = img.crop((cr.left, cr.top, cr.right, cr.bottom))
c.save(r"D:\AI\SW\shots\pw_pane.png")
print("插件区截图:", c.size)