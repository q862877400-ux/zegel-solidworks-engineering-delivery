import ctypes
import ctypes.wintypes as w
import sys
import time
sys.stdout.reconfigure(encoding="utf-8")
u = ctypes.windll.user32
PID = 20456
WM_COMMAND = 0x0111
IDOK = 1


def visible_dlgs():
    out = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, _l):
        p = w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == PID:
            cls = ctypes.create_unicode_buffer(64)
            u.GetClassNameW(h, cls, 64)
            if cls.value == "#32770" and u.IsWindowVisible(h):
                out.append(h)
        return True

    u.EnumWindows(cb, 0)
    return out


def find_button(dlg):
    got = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, _l):
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        t = ctypes.create_unicode_buffer(120)
        u.GetWindowTextW(h, t, 120)
        if cls.value.lower() == "button":
            r = w.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            got.append((h, t.value, r))
        return True

    u.EnumChildWindows(dlg, cb, 0)
    return got


for round_no in range(1, 4):
    dlgs = visible_dlgs()
    print("  ── 第 %d 轮 · 可见对话框 %s ──" % (round_no, dlgs))
    if not dlgs:
        print("  ★ **已清干净**")
        break
    for d in dlgs:
        #: ① 先试标准的 WM_COMMAND(IDOK)
        u.PostMessageW(d, WM_COMMAND, IDOK, 0)
        time.sleep(0.5)
        if not visible_dlgs():
            break
        #: ② 再试**真实鼠标点击**按钮中心（窗口可见，坐标可用）
        btns = find_button(d)
        print("     按钮: %s" % [(h, t) for h, t, _r in btns])
        for h, t, r in btns:
            if t.strip() not in ("确定", "OK", "是"):
                continue
            cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
            print("     ⇒ 真点 (%d, %d)" % (cx, cy))
            u.SetCursorPos(cx, cy)
            time.sleep(0.15)
            u.mouse_event(0x0002, 0, 0, 0, 0)      #: LEFTDOWN
            time.sleep(0.05)
            u.mouse_event(0x0004, 0, 0, 0, 0)      #: LEFTUP
            time.sleep(0.6)
            break
    time.sleep(0.5)

print()
rest = visible_dlgs()
print("  最终：可见的 #32770 = %s ⇒ %s" % (rest, "**已清干净**" if not rest else "**仍在**"))
