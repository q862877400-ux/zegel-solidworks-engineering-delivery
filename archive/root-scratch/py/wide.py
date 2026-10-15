import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L, sw_jlcfa_cards as C
from PIL import ImageGrab
warnings.filterwarnings("ignore")
h, w = L.connect()
ok = L.focus_solidworks(h)
print("置前:", ok)
time.sleep(1.5)
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr, "宽", cr.right - cr.left)
if cr:
    ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
        r"D:\AI\SW\shots\wide_now.png")
    print("截图 -> wide_now.png")
vis = C.visible_codes(w)
print("视口内卡 %d: %s" % (len(vis), [(c, x, y) for c, x, y in vis[:8]]))
allc = C.code_labels(w)
print("全部代码标签 %d: %s" % (len(allc), [c for _, _, c, _ in allc[:8]]))