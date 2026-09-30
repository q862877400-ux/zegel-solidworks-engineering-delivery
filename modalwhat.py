import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_gui_modal as M
warnings.filterwarnings("ignore")
h, w = L.connect()
rep = M.modal_report(h)
print("模态框 %d 个:" % rep["count"])
import win32gui
main_pid = __import__("win32process").GetWindowThreadProcessId(h)[1]
def cb(hh,_):
    if not win32gui.IsWindowVisible(hh): return
    if __import__("win32process").GetWindowThreadProcessId(hh)[1]!=main_pid: return
    if hh==h: return
    r=win32gui.GetWindowRect(hh)
    if r[2]-r[0]<60 or r[3]-r[1]<40: return
    cls=win32gui.GetClassName(hh); own=win32gui.GetWindow(hh,4)
    if cls=="#32770" or own:
        print("  hwnd=%d cls=%s owner=%d %r %s" % (hh,cls,own,win32gui.GetWindowText(hh)[:30],r))
        # 读它的子控件文字
        def cb2(c,_):
            t=win32gui.GetWindowText(c)
            if t.strip(): print("      子: %-30r cls=%s" % (t[:28], win32gui.GetClassName(c)))
        try: win32gui.EnumChildWindows(hh, cb2, None)
        except Exception as e: print("      枚举失败", str(e)[:30])
win32gui.EnumWindows(cb, None)