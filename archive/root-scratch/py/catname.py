import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器: %s 宽 %d" % (cr, cr.right-cr.left))
# 截图上看到的分类名
NAMES = ["转轴","导向轴","导向轴支架","直线轴承","无油衬套","直线导轨",
         "交叉滚子导轨","滚珠丝杠","滚珠丝杠支座组","梯形丝杠","花键",
         "KK模组/单轴","铝基座直线模组","导轨内嵌式直线","电缸","直线电机模组",
         "位移台","拖链","机床防护罩"]
print()
print("★ 分类卡文字能否按名字读到：")
hit = 0
for n in NAMES:
    r = None
    for c in L._controls(w):
        try:
            if (c.window_text() or "").strip() != n: continue
            rr = c.rectangle()
            if L._overlaps(rr, cr): r = rr; break
        except Exception: continue
    if r:
        hit += 1
        print("   ✓ %-14s (%d,%d,%d,%d) %dx%d" % (n, r.left, r.top, r.right, r.bottom, r.width(), r.height()))
    else:
        print("   ✗ %-14s 读不到" % n)
print()
print("命中 %d/%d" % (hit, len(NAMES)))