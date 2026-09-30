import sys, time, warnings, subprocess
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_select as SEL
import win32api, win32con
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
eds = SEL.pending_edits(w)
print("待填 Edit: %s" % [(e[0], e[3]) for e in eds])
if not eds: raise SystemExit(0)
name, ctl, r, hint = eds[0]
print("目标「%s」%s 范围 %s" % (name, (r.left,r.top,r.right,r.bottom), hint))
# 读当前值
try: print("  当前 get_value()=%r" % (ctl.get_value(),))
except Exception as e: print("  get_value 失败 %s" % str(e)[:40])
# 点它
S.ensure_front(h)
cx, cy = (r.left+r.right)//2, (r.top+r.bottom)//2
S.click(cx, cy, 0.6)
print("  已点 (%d,%d)" % (cx,cy))
# 粘贴
subprocess.run(["powershell","-NoProfile","-Command","Set-Clipboard -Value '195'"], capture_output=True, timeout=20)
win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
win32api.keybd_event(ord("V"),0,0,0); time.sleep(0.06)
win32api.keybd_event(ord("V"),0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(0.8)
try: print("  粘贴后 get_value()=%r" % (ctl.get_value(),))
except Exception as e: print("  get_value 失败 %s" % str(e)[:40])
S.cache_drop(); h,w = L.connect()
eds2 = SEL.pending_edits(w)
print("  重读待填: %s" % [e[0] for e in eds2])
st = S.read_state(w); print("  进度 %s%%" % st["pct"])
import sw_jlcfa_grid as G; G._capture(h,w)[0].save(r"D:\AI\SW\shots\edit_test.png")