import sys, time
sys.stdout.reconfigure(encoding="utf-8")
import win32com.client as w32
print("  启动 SolidWorks（可见）…")
app = w32.dynamic.Dispatch("SldWorks.Application")
for i in range(90):
    try:
        v = app.RevisionNumber; break
    except Exception:
        time.sleep(1)
print("  版本:", app.RevisionNumber)
app.Visible = True
print("  已请求显示，等待窗口…")
import win32gui
found = None
for i in range(40):
    hits = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if t and t.upper().startswith("SOLIDWORKS"):
                hits.append((h, t))
    win32gui.EnumWindows(cb, None)
    if hits:
        found = hits[0]; break
    time.sleep(1)
if found:
    print("  ★ 窗口出现: hwnd=%d  %r" % (found[0], found[1][:56]))
    print("  rect:", win32gui.GetWindowRect(found[0]))
    # 不关它，留给下一步截图
    import json
    Path = __import__("pathlib").Path
    Path(r"D:\AI\SW\_sw_hwnd.txt").write_text(str(found[0]), encoding="utf-8")
    print("  hwnd 已存 D:\\AI\\SW\\_sw_hwnd.txt")
else:
    print("  ✗ 90 秒内没出现窗口")