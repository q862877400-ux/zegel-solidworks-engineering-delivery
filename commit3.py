import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
import win32api, win32con
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
def tap(vk,p=0.08):
    win32api.keybd_event(vk,0,0,0); time.sleep(0.04)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(p)
def un(): 
    S.cache_drop(); h,w = L.connect(); return F.unfilled(w), F.model_line(w)
h, w = L.connect(); S.cache_drop()
row = F.row_for_label(w, "L")
P("起点 未填=%d" % F.unfilled(w))
for label, action in (("Tab", "tab"), ("Enter", "enter"), ("点别处", "click")):
    P()
    P("★ 试 %s" % label)
    P("  焦点=%s" % F.set_front(h))
    S.click((row[2].left+row[2].right)//2, (row[2].top+row[2].bottom)//2, 0.6)
    # 清空重打
    win32api.keybd_event(win32con.VK_CONTROL,0,0,0); tap(ord('A'))
    win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
    tap(win32con.VK_DELETE, 0.1)
    for _ in range(10): tap(win32con.VK_BACK, 0.02)
    for ch in "0.5":
        tap(0x30 + (ord(ch)-48) if ch.isdigit() else 0xBE)
    time.sleep(0.4)
    P("  框内=%r" % (row[1].get_value(),))
    if action == "tab": tap(win32con.VK_TAB, 0.3)
    elif action == "enter": tap(win32con.VK_RETURN, 0.3)
    else:
        S.click(2050, 700, 1.0)     # 点参数区空白/别的行
    time.sleep(2.5)
    u, line = un()
    P("  -> 未填=%d 型号行=%r" % (u, line))
    if u == 0: P("  ★★ %s 生效!" % label); break