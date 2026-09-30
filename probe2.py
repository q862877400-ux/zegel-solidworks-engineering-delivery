import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc, win32api, win32con, win32gui
from PIL import ImageGrab
warnings.filterwarnings("ignore")
BLUES=((48,80,224),(0,144,224))
def is_blue(p):
    r,g,b=p[0],p[1],p[2]
    if b<130 or b-r<60 or b-g<30: return False
    return any(abs(r-t[0])<=45 and abs(g-t[1])<=45 and abs(b-t[2])<=45 for t in BLUES)
def probe(tag):
    hwnd, win = loc.connect()
    win32api.keybd_event(win32con.VK_MENU,0,0,0); time.sleep(0.15)
    try: win32gui.SetForegroundWindow(hwnd)
    except Exception: pass
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_MENU,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(1.2)
    cr = loc.find_container(win)[2]
    pane = ImageGrab.grab().crop((cr.left,cr.top,cr.right,cr.bottom))
    px=pane.load(); w,h=pane.size
    groups=[]
    for y in range(0,h,3):
        st=None
        for x in range(w):
            if is_blue(px[x,y]):
                if st is None: st=x
            else:
                if st is not None and x-st>=35:
                    _merge(groups,st,x,y)
                st=None
    print("  %s 容器宽 %d" % (tag, cr.right-cr.left))
    for g in sorted(groups,key=lambda z:z["x0"]):
        if g["y1"]-g["y0"] >= 3:
            print("     (%3d,%3d,%3d,%3d)  %3dx%-3d  相对左 %.1f%%"
                  % (g["x0"],g["y0"],g["x1"],g["y1"],g["x1"]-g["x0"],g["y1"]-g["y0"],
                     100.0*g["x0"]/w))
def _merge(gs,a,b,y):
    for g in gs:
        if abs(g["x0"]-a)<60 and abs(g["x1"]-b)<60 and y-g["y1"]<=12:
            g["x0"]=min(g["x0"],a); g["x1"]=max(g["x1"],b); g["y1"]=y; return
    gs.append({"x0":a,"x1":b,"y0":y,"y1":y})
probe("当前宽度")