import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc
warnings.filterwarnings("ignore")
hwnd, win = loc.connect()
cont = loc.find_container(win)
print("插件容器:", cont[2] if cont else "**找不到**")
s = loc.scan(win)
print("插件区控件 %d 个:" % len(s))
KEYS=["搜索","返回","全部商品分类","首页","同步数据",
      "直线运动零件","机床防护罩","传动零部件","轴承附件"]
for k in KEYS:
    if k in s:
        ct, r = s[k]
        print("   %-14s %-10s (%d,%d,%d,%d) %dx%d" % (k, ct, r.left, r.top, r.right, r.bottom, r.width(), r.height()))
    else:
        print("   %-14s **缺失**" % k)
print()
print("★ 全部插件区控件名:")
for t in sorted(s)[:30]:
    print("   %s" % t[:34])