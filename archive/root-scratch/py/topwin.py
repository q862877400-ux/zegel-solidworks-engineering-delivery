import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
from pywinauto import Application
import win32gui, win32process
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
pid = win32process.GetWindowThreadProcessId(h)[1]
print("SolidWorks hwnd=%d pid=%d" % (h, pid))
print()
print("★ 该进程的所有**顶层窗口**（每个都查一遍有无「生成预览」）:")
found = []
def cb(hh, _):
    try:
        if win32process.GetWindowThreadProcessId(hh)[1] != pid: return
        r = win32gui.GetWindowRect(hh)
        vis = win32gui.IsWindowVisible(hh)
        cls = win32gui.GetClassName(hh)
        txt = win32gui.GetWindowText(hh)
        # 用 pywinauto 包一层看有没有「生成预览」
        try:
            ww = Application(backend="uia").connect(handle=hh).window(handle=hh)
            names = []
            for c in ww.descendants():
                t = (c.window_text() or "").strip()
                if t == "生成预览":
                    names.append((c.element_info.control_type, c.rectangle()))
            if names:
                found.append((hh, cls, [ (t,(r2.left,r2.top)) for t,r2 in names ]))
        except Exception:
            pass
        print("   hwnd=%-9d vis=%-5s %-20s %-28s %s" % (hh, vis, cls[:20], txt[:26], r))
    except Exception: pass
win32gui.EnumWindows(cb, None)
print()
print("★ 在哪个窗口里找到了「生成预览」:")
for hh, cls, lst in found:
    print("   hwnd=%d cls=%s -> %s" % (hh, cls, lst))
if not found:
    print("   ★ 任何顶层窗口里都没有")