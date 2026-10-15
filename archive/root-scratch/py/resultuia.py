import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
import win32api, win32con
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
cr = L.container_rect(w)
# 用 UIA 找搜索框（插件区内的 Edit）
eb = None
for c in L._controls(w):
    try:
        if c.element_info.control_type=="Edit" and L._overlaps(c.rectangle(), cr):
            eb = c; break
    except Exception: continue
P("搜索框(Edit) = %s" % (eb.rectangle() if eb else None))
# 搜索按钮
sb = L.locate(w, "搜索", "Button")
P("搜索按钮 = %s" % (sb.rectangle() if sb else None))
if not eb or not sb: raise SystemExit(1)
# UIA ValuePattern 设值（搜索框不是选型参数，不需要逐键）
import subprocess
subprocess.run(["powershell","-NoProfile","-Command","Set-Clipboard -Value 'BSGY-C7-25'"], capture_output=True, timeout=20)
S.ensure_front(h)
r = eb.rectangle()
S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 0.5)
win32api.keybd_event(win32con.VK_CONTROL,0,0,0); 
win32api.keybd_event(ord('A'),0,0,0); time.sleep(0.05)
win32api.keybd_event(ord('A'),0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.2)
win32api.keybd_event(win32con.VK_DELETE,0,0,0); time.sleep(0.05)
win32api.keybd_event(win32con.VK_DELETE,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.2)
win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
win32api.keybd_event(ord('V'),0,0,0); time.sleep(0.06)
win32api.keybd_event(ord('V'),0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(0.6)
P("框内=%r" % (eb.get_value(),))
rb = sb.rectangle()
S.click((rb.left+rb.right)//2, (rb.top+rb.bottom)//2, 1.0)
time.sleep(4)
S.cache_drop(); h,w = L.connect()
allc = L._controls(w)
P()
P("★ 结果页 UIA 里的「代码：」标签:")
codes=[(c.window_text().strip(), c.rectangle()) for c in allc if (c.window_text() or "").strip().startswith("代码：")]
P("   共 %d 个" % len(codes))
for t,r in codes[:5]: P("      %-18s (%d,%d,%d,%d)" % (t[:16], r.left,r.top,r.right,r.bottom))