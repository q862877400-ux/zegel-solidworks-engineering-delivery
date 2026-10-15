import ctypes
import ctypes.wintypes as w
import sys
import time
sys.stdout.reconfigure(encoding="utf-8")
u = ctypes.windll.user32
PID = 20456

#: ① 找对话框
dlgs = []


@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb(h, _l):
    p = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == PID:
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        if cls.value == "#32770" and u.IsWindowVisible(h):
            dlgs.append(h)
    return True


u.EnumWindows(cb, 0)
print("  可见的 #32770: %s" % dlgs)
for d in dlgs:
    #: ② 找它的「确定」按钮（class=Button, 文本 确定/OK）
    txt = ctypes.create_unicode_buffer(300)
    u.GetWindowTextW(d, txt, 300)
    print("    对话框 hwnd=%d 标题=%r" % (d, txt.value))
    btns = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cbc(h, _l):
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        t2 = ctypes.create_unicode_buffer(120)
        u.GetWindowTextW(h, t2, 120)
        if cls.value.lower() == "button":
            btns.append((h, t2.value))
        return True

    u.EnumChildWindows(d, cbc, 0)
    print("      按钮: %s" % [(h, t) for h, t in btns])
    #: ③ 点「确定 / OK / 是」
    target = None
    for h, t in btns:
        if t.strip() in ("确定", "OK", "是", "&OK", "&Yes"):
            target = h
            break
    if target is None and btns:
        target = btns[0][0]
    if target is None:
        #: 没按钮 ⇒ 直接发 IDOK 给对话框
        u.PostMessageW(d, 0x0111, 1, 0)      #: WM_COMMAND, IDOK
        print("      ⇒ 无按钮，已发 WM_COMMAND(IDOK)")
    else:
        u.SendMessageW(target, 0x00F5, 0, 0)  #: BM_CLICK
        print("      ⇒ 已 BM_CLICK 按钮 hwnd=%d" % target)
    time.sleep(0.4)

time.sleep(1.0)
#: ④ 复核
dlgs2 = []


@ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
def cb2(h, _l):
    p = w.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    if p.value == PID:
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        if cls.value == "#32770" and u.IsWindowVisible(h):
            dlgs2.append(h)
    return True


u.EnumWindows(cb2, 0)
print()
print("  复核：可见的 #32770 现在 = %s ⇒ %s" % (dlgs2, "**已清干净**" if not dlgs2 else "**仍在**"))
