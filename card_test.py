import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr)
print()
KEYS = ["直线运动零件","直线导轨","滚珠丝杠","交叉滚子导轨","导轨轴",
        "导向轴","转轴","无油衬套","花键","返回","搜索","全部商品分类","首页"]
print("★ 分类卡片能否按名字读到：")
for k in KEYS:
    hit = None
    for c in L._controls(w):
        try:
            if (c.window_text() or "").strip() == k and L._overlaps(c.rectangle(), cr):
                hit = c; break
        except Exception: continue
    if hit:
        r = hit.rectangle()
        print("   ✓ %-12s %-10s (%d,%d,%d,%d) %dx%d"
              % (k, hit.element_info.control_type, r.left, r.top, r.right, r.bottom, r.width(), r.height()))
    else:
        print("   ✗ %-12s 读不到" % k)