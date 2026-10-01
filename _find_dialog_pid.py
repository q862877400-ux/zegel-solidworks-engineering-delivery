import ctypes
import ctypes.wintypes as w
import sys
sys.stdout.reconfigure(encoding="utf-8")
u = ctypes.windll.user32
rows = []


@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb(h, _l):
    cls = ctypes.create_unicode_buffer(128)
    u.GetClassNameW(h, cls, 128)
    txt = ctypes.create_unicode_buffer(300)
    u.GetWindowTextW(h, txt, 300)
    p = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    #: ★ 找**任何** `#32770`，或标题像 SolidWorks 的
    if cls.value == "#32770" or "SOLIDWORKS" in txt.value.upper():
        r = w.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        rows.append((p.value, h, cls.value, txt.value, bool(u.IsWindowVisible(h)),
                     (r.left, r.top, r.right - r.left, r.bottom - r.top)))
    return True


u.EnumWindows(cb, 0)
print("  全桌面上 class=#32770 或标题含 SOLIDWORKS 的窗口: **%d** 个" % len(rows))
for pid, h, cls, txt, vis, rect in sorted(rows, key=lambda x: x[0]):
    print("    PID=%-8d hwnd=%-9d visible=%-5s class=%-12s rect=%s" % (pid, h, vis, cls[:12], rect))
    print("        标题=%r" % txt[:60])
