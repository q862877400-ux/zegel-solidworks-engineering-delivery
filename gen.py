# -*- coding: utf-8 -*-
"""100% 已达成 -> 点「生成预览」并等文件。"""
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl
import sw_gui_modal as M

warnings.filterwarnings("ignore")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
print("生成前 %d 个" % len(base), flush=True)

hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
btn = None
for c in win.descendants():
    try:
        if c.element_info.control_type == "Button" and \
                c.window_text().strip() == "生成预览":
            btn = c
            break
    except Exception:
        continue
print("按钮:", (btn.rectangle().left, btn.rectangle().top,
                btn.rectangle().right, btn.rectangle().bottom), flush=True)
btn.click_input()
M.screen_png(r"D:\AI\SW\shots\g1_clicked.png")
print("已点，截图 g1_clicked.png", flush=True)

for i in range(30):
    time.sleep(5)
    hwnd, win = ctl.connect()
    m = M.modal_report(hwnd)["count"]
    now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    new = sorted(now - base)
    print("  %3ds 文件=%d 新增=%d 弹窗=%d %s"
          % ((i + 1) * 5, len(now), len(new), m, new[:1]), flush=True)
    if new:
        M.screen_png(r"D:\AI\SW\shots\g2_done.png")
        print("★ 成功:", new, flush=True)
        break
    if m:
        M.screen_png(r"D:\AI\SW\shots\g_modal.png")
        M.close_modals(hwnd)
else:
    M.screen_png(r"D:\AI\SW\shots\g3_timeout.png")
    print("150 秒无新增", flush=True)
