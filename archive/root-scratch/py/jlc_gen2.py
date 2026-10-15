import sys, time, ctypes, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
J.log("生成前 BuildFile: %d 个" % len(base))
hwnd = J.sw_window(); J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 「生成预览」按钮：裁剪图里约 (300, 848)
CX, CY = rect.right - 4 + 300, rect.top - 16 + 848
J.log("点「生成预览」(%d,%d)" % (CX, CY))
J.click(CX, CY, pause=2.0)
J.log("等生成…")
new = []
for i in range(24):
    time.sleep(5)
    J.ensure_window(hwnd)
    now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    new = sorted(now - base)
    J.log("  %3ds  BuildFile=%d  新增=%d %s" % ((i+1)*5, len(now), len(new), new[:1]))
    if new:
        break
r = J.ensure_window(hwnd); _root, rect2 = J.tab_column(hwnd)
J.snap("m10_gen", box=(rect2.right-4, rect2.top-16,
                       min(r[2], rect2.right+470), min(r[3], rect2.top+880)))
J.log("★ 新增: %s" % (new if new else "无"))