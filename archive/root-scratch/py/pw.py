import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
from PIL import ImageGrab
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr, "宽", cr.right-cr.left)
# ① PrintWindow 抓窗口自身（不受遮挡）
img, ok, W, H = L.capture_window(h, r"D:\AI\SW\shots\pw_now.png")
print("PrintWindow:", ok, W, "x", H)
# ② 裁容器区域
if img is not None and cr:
    c = img.crop((cr.left, cr.top, cr.right, cr.bottom))
    c.save(r"D:\AI\SW\shots\pw_pane.png")
    print("插件区:", c.size)