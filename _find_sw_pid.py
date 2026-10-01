import ctypes
import ctypes.wintypes as w
import sys
sys.stdout.reconfigure(encoding="utf-8")
u = ctypes.windll.user32
print("  全盘找标题含 SOLIDWORKS 的可见顶层窗口:")
rows = []


@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb(h, _l):
    if not u.IsWindowVisible(h):
        return True
    txt = ctypes.create_unicode_buffer(300)
    u.GetWindowTextW(h, txt, 300)
    t = txt.value
    if "SOLIDWORKS" in t.upper() or "SolidWorks" in t:
        p = w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(h, cls, 128)
        r = w.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        rows.append((p.value, r.right - r.left, r.bottom - r.top, cls.value[:36], t[:52]))
    return True


u.EnumWindows(cb, 0)
for pid, a, b, c, d in sorted(set(rows), key=lambda x: -(x[1] * x[2]))[:10]:
    print("    PID=%-8d %5dx%-5d %-38s %s" % (pid, a, b, c, d))
print()
print("  我一直在用的 SW_PID = 20456 的主窗口尺寸:")
r2 = w.RECT()
for pid, a, b, c, d in rows:
    if pid == 20456:
        print("    %5dx%-5d %s" % (a, b, d))
        break
else:
    print("    （**PID 20456 下没有**含 SOLIDWORKS 的可见窗口）")
