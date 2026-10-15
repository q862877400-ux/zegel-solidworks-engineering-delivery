import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F, sw_jlcfa_select as SEL
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
P("起点 未填=%d 型号=%r" % (F.unfilled(w), F.model_line(w)))
eds = F._all_edits(w)
P("参数区 Edit: %s" % [(e[0][:14], e[3]) for e in eds])
if not eds: raise SystemExit(0)
name, ctl, r, hint = eds[0]
rg = SEL._parse_hint(hint); val = str(int(rg[0])) if rg else "100"
P("① set_edit_text('%s') 到 %r" % (val, name[:14]))
try: ctl.set_edit_text(val); P("   get_value=%r" % (ctl.get_value(),))
except Exception as e: P("   失败 %s" % str(e)[:50])
time.sleep(0.6); S.cache_drop(); h,w = L.connect()
P("   未填=%d 型号=%r" % (F.unfilled(w), F.model_line(w)))
P("② 点别处失焦（容器空白处）")
S.click(2100, 700, 1.0)
time.sleep(1.5); S.cache_drop(); h,w = L.connect()
P("   未填=%d 型号=%r" % (F.unfilled(w), F.model_line(w)))
P("③ 再 Tab 一次")
import win32api, win32con
win32api.keybd_event(win32con.VK_TAB,0,0,0); time.sleep(0.06)
win32api.keybd_event(win32con.VK_TAB,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(1.5); S.cache_drop(); h,w = L.connect()
P("   未填=%d 型号=%r" % (F.unfilled(w), F.model_line(w)))