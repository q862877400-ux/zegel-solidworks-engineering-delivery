import sys, win32gui, win32process
sys.stdout.reconfigure(encoding="utf-8")
PID = 8692
found = []
def cb(h, _):
    try:
        _, pid = win32process.GetWindowThreadProcessId(h)
        if pid != PID: return
        r = win32gui.GetWindowRect(h)
        found.append((h, win32gui.GetClassName(h), win32gui.GetWindowText(h),
                      win32gui.IsWindowVisible(h), win32gui.IsIconic(h), r))
    except Exception: pass
win32gui.EnumWindows(cb, None)
print("PID %d 的顶层窗口 %d 个:" % (PID, len(found)))
for h, cls, t, vis, ico, r in found[:20]:
    print("  hwnd=%-9d vis=%-5s iconic=%-5s %-22s %-40r %s"
          % (h, vis, ico, cls[:22], t[:38], r))