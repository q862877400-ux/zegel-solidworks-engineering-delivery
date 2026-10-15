# -*- coding: utf-8 -*-
"""A 路线：pywinauto 的 **win32(MSAA)** 后端 —— 对自绘控件比 UIA 宽容。

⚑ UIA 后端读不到 ComboBox 的选项（``item_texts()`` 报
   "'ComboBoxWrapper' object has no attribute ..."）。
   ⇒ 换 win32/MSAA 后端再看一次；不行就换 B（截整屏找浮窗）。
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
from pywinauto import Application

warnings.filterwarnings("ignore")


def sw_hwnd():
    import subprocess
    import win32process
    cands = []

    def cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return
        t = win32gui.GetWindowText(h)
        if not t:
            return
        try:
            pid = win32process.GetWindowThreadProcessId(h)[1]
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO",
                                  "CSV", "/NH"], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace")
            name = out.stdout.split(",")[0].strip('"')
        except Exception:
            name = ""
        if name.lower().endswith("sldworks.exe"):
            cands.append((h, t, win32gui.GetWindowRect(h)))
    win32gui.EnumWindows(cb, None)
    cands.sort(key=lambda x: (x[2][2]-x[2][0])*(x[2][3]-x[2][1]), reverse=True)
    return cands[0][0]


hwnd = sw_hwnd()
print("窗口:", win32gui.GetWindowText(hwnd)[:52], flush=True)

app = Application(backend="win32").connect(handle=hwnd)
win = app.window(handle=hwnd)
win.set_focus()
time.sleep(0.6)

print()
print("  ★ win32/MSAA 后端下的 ComboBox（对比 UIA 的 item_texts 失败）：")
n = 0
for c in win.descendants():
    try:
        cn = c.friendly_class_name()
    except Exception:
        continue
    if cn not in ("ComboBox", "TComboBox", "ComboBoxControl"):
        continue
    r = c.rectangle()
    try:
        items = c.item_texts()
    except Exception as e:
        items = ["<%s>" % str(e)[:34]]
    try:
        txt = c.window_text()
    except Exception:
        txt = "?"
    n += 1
    print("   %-12s text=%-16s 选项 %d: %s"
          % (cn, txt[:14], len(items), items[:6]), flush=True)
    if n >= 10:
        break
print("  共 %d 个" % n, flush=True)
