import sys
sys.stdout.reconfigure(encoding="utf-8")
import win32gui
hits = []
def cb(h, _):
    if win32gui.IsWindowVisible(h):
        t = win32gui.GetWindowText(h)
        if t and "SOLID" in t.upper():
            hits.append((h, t))
win32gui.EnumWindows(cb, None)
for h, t in hits:
    print("  hwnd=%-9d %s" % (h, t[:70]))
print("  合计", len(hits))