import sys, time
sys.stdout.reconfigure(encoding="utf-8")
import win32gui, uiautomation as auto
# ⚠⚑ 靠标题过滤不可靠：浏览器标签页标题「SolidWorks Automation Skil — DSH 本地构建」
#   也以 SolidWorks 开头。⇒ **改按进程名**判定（只有 SLDWORKS.exe 才是本体）。
import win32process
cands = []
def cb(h, _):
    if not win32gui.IsWindowVisible(h):
        return
    t = win32gui.GetWindowText(h)
    if not t:
        return
    # ⚠ 不用 psutil（本机没有）：直接问内核要这个窗口所属进程的可执行路径
    import win32api
    import win32con
    name = ""
    try:
        pid = win32process.GetWindowThreadProcessId(h)[1]
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        name = win32process.GetModuleFileNameEx(hproc, 0) or ""
        hproc.Close()
    except Exception:
        # 拿不到路径时退回进程名（同样够用）
        try:
            import subprocess
            pid = win32process.GetWindowThreadProcessId(h)[1]
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace")
            name = out.stdout.split(",")[0].strip('"')
        except Exception:
            name = ""
    if name.lower().endswith("sldworks.exe"):
        cands.append((h, t, win32gui.GetWindowRect(h)))
win32gui.EnumWindows(cb, None)
print("  可见 SOLIDWORKS 窗口 %d 个:" % len(cands))
for h, t, r in cands:
    print("    hwnd=%-9d %-46s %s" % (h, t[:44], r))
if not cands: raise SystemExit(1)
# 取面积最大的（真正的应用主窗口，排除小对话框）
cands.sort(key=lambda x:(x[2][2]-x[2][0])*(x[2][3]-x[2][1]), reverse=True)
hwnd = cands[0][0]
open(r"D:\AI\SW\_sw_hwnd.txt","w").write(str(hwnd))
print()
print("  ★ 选定 hwnd=%d" % hwnd)
root = auto.ControlFromHandle(hwnd); root.SetActive(); time.sleep(0.8)
def find(node, pred, d=0):
    if d>9: return None
    for c in node.GetChildren():
        try:
            if pred(c): return c
        except Exception: continue
        r = find(c, pred, d+1)
        if r is not None: return r
    return None
tp = find(root, lambda c: (c.Name or "")=="Task Pane Tabs Wnd")
if tp:
    r = tp.BoundingRectangle
    print("  标签列: (%d,%d,%d,%d)  %dx%d" % (r.left,r.top,r.right,r.bottom,r.width(),r.height()))
    print("  ★ 最下面那个（嘉立创）中心坐标 ≈ (%d, %d)" % ((r.left+r.right)//2, r.bottom-20))
else:
    print("  ✗ 没找到标签列")