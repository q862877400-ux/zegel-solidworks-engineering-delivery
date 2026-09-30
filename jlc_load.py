import sys, time, ctypes, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
hwnd = J.sw_window()
for i in range(6):
    time.sleep(3)
    r = J.ensure_window(hwnd)
    _root, rect = J.tab_column(hwnd)
    J.snap("m9_load_%d" % (i+1), box=(rect.right-4, rect.top-16,
                                       min(r[2], rect.right+470), min(r[3], rect.top+880)))
    now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    new = sorted(now - base)
    J.log("  %ds 新增: %s" % ((i+1)*3, new if new else "无"))
J.log("完成，看 m9_load_6_z.png")