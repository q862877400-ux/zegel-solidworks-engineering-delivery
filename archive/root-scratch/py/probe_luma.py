import sys, warnings
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_grid as G, sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
pane, cr = G._capture(h, w)
px = pane.load(); W,H = pane.size
print("插件区 %dx%d" % (W,H))
# 取几条横线看亮度分布
for y in (300, 310, 330, 400, 700, 720, 760):
    vals = [int(G._luma(px[x,y])) for x in range(0,W,8)]
    c = Counter(vals)
    print("y=%-4d 最常见亮度: %s" % (y, c.most_common(4)))
print()
# 取一条穿过卡片的横线，打印亮度序列的跳变点
y=330
prev=None; edges=[]
for x in range(W):
    v=int(G._luma(px[x,y]))
    b = v>=251
    if prev is not None and b!=prev: edges.append((x,v))
    prev=b
print("y=%d 亮度>=251 的跳变点 %d 个: %s" % (y, len(edges), edges[:12]))