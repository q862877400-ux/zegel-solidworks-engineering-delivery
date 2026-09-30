import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
import win32api, win32con
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
# 规律：代码 y=621 起，步长 126；卡片中心 = 代码 y - 55（卡比代码大）
codes = []
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
    except Exception: continue
    if t.startswith("代码：") and L._overlaps(r,cr):
        codes.append((r.top, t[3:]))
codes.sort()
print("结果卡 %d 张，y 列表: %s" % (len(codes), [t for _,t in codes[:8]]))
if len(codes) >= 2:
    step = codes[1][0] - codes[0][0]
    print("实测步长: %d px" % step)
    # 算第 5 张卡的中心
    target = codes[4]
    cy = target[0] - 55
    cx = (cr.left + cr.right)//2
    print("第5张「%s」代码 y=%d -> 卡片中心 y=%d" % (target[1], target[0], cy))
    print("点击 (%d,%d)…" % (cx, cy))
    win32api.SetCursorPos((int(cx), int(cy))); time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0); time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
    time.sleep(2.5)
    h, w = L.connect()
    print()
    print("点后是否进入选型页：")
    n_combo = 0; names=[]
    for c in L._controls(w):
        try:
            t=(c.window_text() or "").strip(); r=c.rectangle(); ct=c.element_info.control_type
        except Exception: continue
        if not t or not L._overlaps(r,cr): continue
        if ct=="ComboBox": n_combo+=1; names.append(t)
    print("  ComboBox 数: %d" % n_combo)
    print("  前 12 个: %s" % names[:12])
    gen = L.locate(w, "生成预览", "Button")
    print("  「生成预览」按钮: %s" % (gen.rectangle() if gen else "读不到"))