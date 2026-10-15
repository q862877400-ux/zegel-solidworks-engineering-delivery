import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
import win32api, win32con
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
codes=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
    except Exception: continue
    if t.startswith("代码：") and L._overlaps(r,cr):
        codes.append((r.top, t[3:]))
codes.sort()
vis = [(y,c) for y,c in codes if cr.top+520 < y < cr.bottom-140]
print("视口内的卡: %s" % [c for _,c in vis])
if not vis:
    print("没有视口内的卡"); raise SystemExit(1)
y, code = vis[0]
cy = y - 55
cx = (cr.left + cr.right)//2
print("点「%s」卡片中心 (%d,%d)" % (code, cx, cy))
win32api.SetCursorPos((int(cx), int(cy))); time.sleep(0.15)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0); time.sleep(0.06)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
time.sleep(3.0)
h, w = L.connect()
cr = L.container_rect(w)
print()
print("点后状态:")
combos=[]; others=[]
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle(); ct=c.element_info.control_type
    except Exception: continue
    if not t or not L._overlaps(r,cr): continue
    if ct=="ComboBox": combos.append(t)
    if ct in ("Text","Pane") and r.width()>120 and 8<r.height()<80:
        others.append((r.top,t[:24]))
print("  ComboBox %d: %s" % (len(combos), combos[:10]))
gen = L.locate(w, "生成预览", "Button")
print("  生成预览: %s" % (gen.rectangle() if gen else "读不到"))
print("  其它: %s" % others[:8])