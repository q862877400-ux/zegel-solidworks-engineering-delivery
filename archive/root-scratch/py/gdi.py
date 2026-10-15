import sys
sys.stdout.reconfigure(encoding="utf-8")
import win32gui, win32ui, traceback
hwnd = 0
def cb(h, _):
    global hwnd
    if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h).upper().startswith("SOLIDWORKS"):
        hwnd = h
win32gui.EnumWindows(cb, None)
print("找到 SolidWorks hwnd:", hwnd)
if not hwnd:
    raise SystemExit("没有窗口可试")
try:
    hwndDC = win32gui.GetWindowDC(hwnd); print("  GetWindowDC OK")
    mfcDC = win32ui.CreateDCFromHandle(hwndDC); print("  CreateDCFromHandle OK")
    for args, tag in (((mfcDC,), "1arg"), ((mfcDC, mfcDC), "2arg")):
        try:
            dc = win32ui.CreateCompatibleDC(*args); print("  CreateCompatibleDC %s OK" % tag)
            break
        except Exception as e:
            print("  CreateCompatibleDC %s -> %s" % (tag, str(e)[:60]))
except Exception:
    traceback.print_exc()