import sys
sys.stdout.reconfigure(encoding="utf-8")
import win32gui
allw = []
def cb(h, _):
    t = win32gui.GetWindowText(h)
    if t and ("SOLIDWORKS" in t.upper() or "SolidWorks" in t):
        allw.append((h, bool(win32gui.IsWindowVisible(h)), t))
win32gui.EnumWindows(cb, None)
for h, vis, t in allw:
    print("  hwnd=%-9d 可见=%-6s %s" % (h, vis, t[:66]))
print("  合计", len(allw))