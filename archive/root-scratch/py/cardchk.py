import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_cards as C
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr, "宽", cr.right-cr.left)
vis = C.visible_codes(w)
print("视口内卡 %d: %s" % (len(vis), [(c,x,y) for c,x,y in vis[:5]]))
allc = C.code_labels(w)
print("全部标签 %d: %s" % (len(allc), [c for _,_,c,_ in allc[:6]]))
sb = C._scrollbar(w)
print("滚动条: %s" % (sb,))