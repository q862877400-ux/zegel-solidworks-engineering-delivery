from pathlib import Path
p = Path(r"D:\AI\SW\locate_sw.py")
s = p.read_text(encoding="utf-8")
old = '''cands = []
def cb(h, _):
    if win32gui.IsWindowVisible(h):
        t = win32gui.GetWindowText(h)
        if t and t.upper().startswith("SOLIDWORKS ") or t.upper() == "SOLIDWORKS":
            cands.append((h, t, win32gui.GetWindowRect(h)))
win32gui.EnumWindows(cb, None)'''
new = '''# ⚠⚑ 靠标题过滤不可靠：浏览器标签页标题「SolidWorks Automation Skil — DSH 本地构建」
#   也以 SolidWorks 开头。⇒ **改按进程名**判定（只有 SLDWORKS.exe 才是本体）。
import win32process
cands = []
def cb(h, _):
    if not win32gui.IsWindowVisible(h):
        return
    t = win32gui.GetWindowText(h)
    if not t:
        return
    try:
        import psutil
        name = psutil.Process(win32process.GetWindowThreadProcessId(h)[1]).name()
    except Exception:
        name = ""
    if name.lower() == "sldworks.exe":
        cands.append((h, t, win32gui.GetWindowRect(h), name))
win32gui.EnumWindows(cb, None)'''
assert old in s
s = s.replace(old, new, 1)
s = s.replace('print("    hwnd=%-9d %-52s %s" % (h, t[:50], r))',
              'print("    hwnd=%-9d pid=%-6s %-46s %s" % (h, win32process.GetWindowThreadProcessId(h)[1], t[:44], r))')
s = s.replace('cands.sort(key=lambda x:(x[2][2]-x[2][0])*(x[2][3]-x[2][1]), reverse=True)\nhwnd = cands[0][0]',
              'cands.sort(key=lambda x:(x[2][2]-x[2][0])*(x[2][3]-x[2][1]), reverse=True)\nhwnd = cands[0][0]')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已改为按进程名过滤")