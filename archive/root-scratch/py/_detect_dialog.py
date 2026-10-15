import ctypes
import ctypes.wintypes as w
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = ctypes.windll.user32
PID = 20456

#: ① 用**新口径**（不过滤可见性）枚举，看 `#32770` 数
rows = []


@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb(h, _l):
    p = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value != PID:
        return True
    cls = ctypes.create_unicode_buffer(128)
    u.GetClassNameW(h, cls, 128)
    txt = ctypes.create_unicode_buffer(300)
    u.GetWindowTextW(h, txt, 300)
    r = w.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    if cls.value == "#32770" or (txt.value and "SOLIDWORKS" in txt.value):
        rows.append({
            "hwnd": h, "class": cls.value, "text": txt.value,
            "visible": bool(u.IsWindowVisible(h)),
            "rect": (r.left, r.top, r.right, r.bottom),
        })
    return True


u.EnumWindows(cb, 0)
print("  PID=%d 上的对话框/主窗口:" % PID)
for r in rows:
    print("    hwnd=%-10d class=%-10s visible=%-5s rect=%s" % (r["hwnd"], r["class"], r["visible"], r["rect"]))
    print("        标题=%r" % r["text"])
print()

#: ② 再看**对话框的子控件**（按钮在哪、叫什么）
for r in rows:
    if r["class"] != "#32770":
        continue
    print("  ── 对话框 hwnd=%d 的子控件 ──" % r["hwnd"])
    kids = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cbc(h, _l):
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(h, cls, 128)
        txt = ctypes.create_unicode_buffer(200)
        u.GetWindowTextW(h, txt, 200)
        cid = u.GetDlgCtrlID(h)
        kids.append((h, cls.value, txt.value, cid))
        return True

    u.EnumChildWindows(r["hwnd"], cbc, 0)
    for h, cls, txt, cid in kids:
        print("    child hwnd=%-10d class=%-12s id=%-6d 文本=%r" % (h, cls, cid, txt))
