import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
cr = L.container_rect(w)
print("容器 %s" % (cr,))
print()
# 头部固定区控件的 rect 是否可信（对比截图）
for n in ("搜索","返回","全部商品分类","首页","同步数据","有更新"):
    for c in L.locate_all(w, n):
        r=c.rectangle()
        print("   %-10s %-6s (%d,%d,%d,%d) %dx%d" % (n, c.element_info.control_type[:5],
              r.left,r.top,r.right,r.bottom,r.width(),r.height()))