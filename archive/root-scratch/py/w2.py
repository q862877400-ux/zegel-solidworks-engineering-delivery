import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc
warnings.filterwarnings("ignore")
hwnd, win = loc.connect()
cont = loc.find_container(win)
s = loc.scan(win)
print("容器:", cont[2] if cont else "无", " 宽=", (cont[2].right-cont[2].left) if cont else 0)
print("插件区控件:", len(s))
for k in ["返回","直线运动零件","机床防护罩","传动零部件","轴承附件"]:
    if k in s:
        ct, r = s[k]
        print("   %-12s (%d,%d,%d,%d) %dx%d" % (k, r.left, r.top, r.right, r.bottom, r.width(), r.height()))
    else:
        print("   %-12s 缺失" % k)
loc.M.screen_png(r"D:\AI\SW\shots\user_dragged.png")
print()
print("整屏: user_dragged.png")