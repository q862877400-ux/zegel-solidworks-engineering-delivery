import sys, time, json, ctypes
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")} if BF.is_dir() else set()
J.log("生成前 BuildFile 有 %d 个文件" % len(base))

hwnd = J.sw_window()
J.ensure_window(hwnd)
_root, rect = J.tab_column(hwnd)
# 「📦 生成预览」按钮：裁剪原点 (rect.right-4, rect.top-16)，按钮中心约 (300, 848)
CX = rect.right - 4 + 300
CY = rect.top - 16 + 848
J.log("点「生成预览」(%d,%d)" % (CX, CY))
J.click(CX, CY, pause=2.0)
J.log("等生成（最多 90 秒）…")
new = []
for i in range(18):
    time.sleep(5)
    J.ensure_window(hwnd)
    if BF.is_dir():
        now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
        new = sorted(now - base)
        J.log("  %2ds  BuildFile %d 个, 新增 %d: %s" % ((i+1)*5, len(now), len(new), new[:2]))
        if new:
            break
    else:
        J.log("  %2ds  BuildFile 不存在" % ((i+1)*5))
r = J.ensure_window(hwnd)
_root, rect2 = J.tab_column(hwnd)
J.snap("m5_generated", box=(rect2.right-4, rect2.top-16,
                           min(r[2], rect2.right+470), min(r[3], rect2.top+900)))
J.log("新增文件: %s" % (new if new else "无"))