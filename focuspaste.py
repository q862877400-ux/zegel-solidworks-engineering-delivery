import sys, time, warnings, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_select as SEL
import win32api, win32con, win32gui
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
# 找 P 字段
eds = SEL.pending_edits(w)
P("待填: %s" % [(e[0], e[3], e[2].top) for e in eds])
tgt = None
for e in eds:
    if e[0].startswith("P") or "[10~15]" in str(e[3]): tgt = e; break
if not tgt and eds: tgt = eds[-1]
if not tgt: P("无待填"); raise SystemExit(0)
name, ctl, r, hint = tgt
P("目标 %r %s %s" % (name, (r.left,r.top,r.right,r.bottom), hint))
# ★ 先确保焦点真的在 SolidWorks
ok = False
for i in range(4):
    if win32gui.GetForegroundWindow() == h: ok=True; break
    L.focus_solidworks(h); time.sleep(0.4)
P("焦点取得: %s (fg=%d want=%d)" % (win32gui.GetForegroundWindow()==h, win32gui.GetForegroundWindow(), h))
# 剪贴板
subprocess.run(["powershell","-NoProfile","-Command","Set-Clipboard -Value '10'"], capture_output=True, timeout=20)
# 点 + 全选 + 粘贴
S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 0.6)
P("已点输入框")
for vk,ctrl in ((ord('A'),True),(win32con.VK_DELETE,False),(ord('V'),True)):
    if ctrl: win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
    win32api.keybd_event(vk,0,0,0); time.sleep(0.06)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0)
    if ctrl: win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
    time.sleep(0.3)
time.sleep(1.0)
P("粘贴后 get_value=%r" % (ctl.get_value(),))
# Tab 提交
win32api.keybd_event(win32con.VK_TAB,0,0,0); time.sleep(0.06)
win32api.keybd_event(win32con.VK_TAB,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(2.0)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
P("进度 %s%%" % st["pct"])
P("型号行: %s" % [n for n in st["visible"] if "BSGY" in n][:2])