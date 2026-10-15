import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F, sw_jlcfa_select as SEL
import win32api, win32con
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
def tap(vk):
    win32api.keybd_event(vk,0,0,0); time.sleep(0.05)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(0.08)
VK = {c: 0x30+i for i, c in enumerate("0123456789")}
h, w = L.connect(); S.cache_drop()
P("起点 未填=%d" % F.unfilled(w))
eds = F._all_edits(w)
name, ctl, r, hint = eds[0]
rg = SEL._parse_hint(hint); val = str(int(rg[0]))
P("目标 %r 值 %s" % (name[:14], val))
P("焦点: %s" % F.set_front(h))
S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 0.6)
P("已点输入框")
# 全选 + 删
win32api.keybd_event(win32con.VK_CONTROL,0,0,0); tap(ord('A'))
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
tap(win32con.VK_DELETE)
time.sleep(0.3)
# ★ 逐键打
for ch in val:
    tap(VK[ch])
time.sleep(0.5)
P("打完后 get_value=%r" % (ctl.get_value(),))
# Tab 提交
tap(win32con.VK_TAB)
time.sleep(2.0)
S.cache_drop(); h,w = L.connect()
P("★ 未填=%d  型号=%r" % (F.unfilled(w), F.model_line(w)))
P("  进度 %s%%" % S.read_state(w)["pct"])