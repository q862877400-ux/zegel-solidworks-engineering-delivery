import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
import win32gui, win32process
warnings.filterwarnings("ignore")
h, w = L.connect()
S.ensure_front(h)
allc = S.controls_cached(w)
cb=None
for c in allc:
    try:
        if (c.window_text() or "").strip()=="滑块类型" and c.element_info.control_type=="ComboBox":
            cb=c; break
    except Exception: continue
pid = win32process.GetWindowThreadProcessId(h)[1]
def snap():
    s=set()
    def cbw(hh,_):
        if not win32gui.IsWindowVisible(hh): return
        if win32process.GetWindowThreadProcessId(hh)[1]!=pid: return
        if hh==h: return
        s.add((hh, win32gui.GetClassName(hh), win32gui.GetWindow(hh,4), win32gui.GetWindowRect(hh)))
    win32gui.EnumWindows(cbw,None)
    return s
before = snap()
print("点之前同进程顶层窗 %d 个" % len(before))
cb.click_input(); time.sleep(1.0)
after = snap()
print("点之后 %d 个" % len(after))
for hh,cls,own,r in sorted(after-before, key=lambda z: z[3][1]):
    print("  NEW hwnd=%d cls=%-18s owner=%d rect=%s" % (hh,cls,own,r))