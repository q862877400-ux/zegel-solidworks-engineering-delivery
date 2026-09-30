import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_grid as G
import win32api, win32con
warnings.filterwarnings("ignore")
def typ(s):
    for ch in s:
        sc=win32api.VkKeyScan(ch); vk,sh=sc&0xFF,(sc>>8)&1
        if sh: win32api.keybd_event(win32con.VK_SHIFT,0,0,0)
        win32api.keybd_event(vk,0,0,0); time.sleep(0.03)
        win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.03)
        if sh: win32api.keybd_event(win32con.VK_SHIFT,0,win32con.KEYEVENTF_KEYUP,0)
h, w = L.connect(); S.cache_drop()
pane, cr = G._capture(h, w)
# 从截图找搜索框：头部区域里最宽的一条白色输入框
px=pane.load(); W,H=pane.size
best=None
for y in range(60, 200):
    st=None
    for x in range(W):
        v=int(0.299*px[x,y][0]+0.587*px[x,y][1]+0.114*px[x,y][2])
        if v>=250:
            if st is None: st=x
        else:
            if st is not None and x-st>=150:
                if best is None or (x-st)>(best[2]-best[0]): best=(st,y,x,y)
            st=None
print("搜索框(相对插件区): %s" % (best,))
if not best: raise SystemExit(1)
sx = cr.left + (best[0]+best[2])//2
sy = cr.top + best[1] + 10
print("屏幕坐标 (%d,%d)  容器 %s" % (sx, sy, cr))
S.ensure_front(h)
S.click(sx, sy, 0.6)
typ("EGH25SAZ0C")
time.sleep(0.4)
win32api.keybd_event(win32con.VK_RETURN,0,0,0); time.sleep(0.08)
win32api.keybd_event(win32con.VK_RETURN,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(4)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
print("搜索后 kind=%s  代码卡=%d %s" % (S.page_kind(st), len(st["codes"]), st["codes"][:4]))
G._capture(h,w)[0].save(r"D:\AI\SW\shots\after_search.png")