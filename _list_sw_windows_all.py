import ctypes
import ctypes.wintypes as w
import sys
sys.stdout.reconfigure(encoding="utf-8")
u = ctypes.windll.user32
PID = 20456
rows = []


@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb(h, _l):
    p = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == PID:
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(h, cls, 128)
        txt = ctypes.create_unicode_buffer(300)
        u.GetWindowTextW(h, txt, 300)
        r = w.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        rows.append((u.IsWindowVisible(h), r.right - r.left, r.bottom - r.top,
                     cls.value[:40], txt.value[:46], h))
    return True


u.EnumWindows(cb, 0)
print("  PID=%d 的顶层窗口共 %d 个（**含不可见**，按面积降序）:" % (PID, len(rows)))
for vis, a, b, c, d, h in sorted(rows, key=lambda x: -(x[1] * x[2]))[:12]:
    print("    可见=%-5s %5dx%-5d %-42s %s" % (vis, a, b, c, d))
print()
big = [r for r in rows if r[1] * r[2] > 100000]
print("  面积 > 100000 的: %d 个" % len(big))
for vis, a, b, c, d, h in big[:6]:
    print("    可见=%-5s %5dx%-5d %s" % (vis, a, b, d))
print()
print("  ★★ 结论要看：**有没有一个可见的大窗口** —— 若没有，")
print("     那么所有要求 `IsWindowVisible` 的检查（含模态框检查）**都扫不到它**。")
