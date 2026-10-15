import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_grid as G
import win32api, win32con
warnings.filterwarnings("ignore")
def key(vk, ctrl=False, p=0.12):
    if ctrl: win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
    win32api.keybd_event(vk,0,0,0); time.sleep(0.05)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0)
    if ctrl: win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
    time.sleep(p)
h, w = L.connect(); S.cache_drop()
pane, cr = G._capture(h, w)
px=pane.load(); W,H=pane.size
best=None
for y in range(60,200):
    st=None
    for x in range(W):
        v=int(0.299*px[x,y][0]+0.587*px[x,y][1]+0.114*px[x,y][2])
        if v>=250:
            if st is None: st=x
        else:
            if st is not None and x-st>=150:
                if best is None or (x-st)>(best[2]-best[0]): best=(st,y,x,y)
            st=None
sx = cr.left + (best[0]+best[2])//2; sy = cr.top + best[1] + 10
print("搜索框屏幕 (%d,%d)" % (sx,sy))
S.ensure_front(h)
S.click(sx, sy, 0.5)
key(ord('A'), ctrl=True); key(win32con.VK_DELETE)
time.sleep(0.3)
key(ord('V'), ctrl=True, p=0.6)
time.sleep(0.5)
G._capture(h,w)[0].save(r"D:\AI\SW\shots\pasted.png")
# 点「搜索」按钮（截图量：pane x 536, y 105）
bx, by = cr.left + 536, cr.top + 105
print("点「搜索」按钮 (%d,%d)" % (bx,by))
S.click(bx, by, 1.0)
time.sleep(4)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
print("结果: kind=%s 代码卡=%d %s" % (S.page_kind(st), len(st["codes"]), st["codes"][:4]))
G._capture(h,w)[0].save(r"D:\AI\SW\shots\search_result.png")