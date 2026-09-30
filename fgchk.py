import sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import win32gui, win32process
import sw_gui_focus as F, sw_gui_modal as M, ctl
import warnings; warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
print("  SolidWorks hwnd =", hwnd, repr(win32gui.GetWindowText(hwnd)[:44]))
print("  当前前台        =", F.foreground(), repr(win32gui.GetWindowText(F.foreground())[:44]))
print()
print("  ★ ensure_focus(hwnd) 后：")
ok = F.ensure_focus(hwnd)
print("    返回=%s  前台=%d  一致=%s" % (ok, F.foreground(), F.foreground()==hwnd))
print()
print("  ★ 同进程窗口全景（谁可能是插件面板/弹窗）:")
main_pid = win32process.GetWindowThreadProcessId(hwnd)[1]
def cb(h,_):
    if not win32gui.IsWindowVisible(h): return
    if win32process.GetWindowThreadProcessId(h)[1] != main_pid: return
    r = win32gui.GetWindowRect(h)
    print("    hwnd=%-9d fg=%-5s owner=%-9d cls=%-14s %sx%s  %r"
          % (h, "YES" if h==F.foreground() else "", win32gui.GetWindow(h,4),
             win32gui.GetClassName(h)[:14], r[2]-r[0], r[3]-r[1],
             win32gui.GetWindowText(h)[:26]))
win32gui.EnumWindows(cb, None)