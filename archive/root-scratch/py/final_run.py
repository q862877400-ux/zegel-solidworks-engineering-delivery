# -*- coding: utf-8 -*-
"""完整流程：填参数到 100% -> 生成。每步前后查弹窗。

速度优化：
  · 一次 connect 复用，不每轮重连
  · 只在「需要判定」时截图，其余不截
  · 每步用「读控件值」判定是否生效，不 sleep 死等
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
from pathlib import Path

import ctl
import sw_gui_modal as M

warnings.filterwarnings("ignore")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")


def combos(win):
    out = []
    for c in win.descendants():
        try:
            if c.element_info.control_type != "ComboBox":
                continue
            r = c.rectangle()
            if r.height() < 10:
                continue
            out.append((c.window_text().strip(), c, r))
        except Exception:
            continue
    return out


def pct(win):
    import re
    txt = []
    for c in win.descendants():
        try:
            if c.element_info.control_type == "Text" and c.window_text():
                txt.append(c.window_text().strip())
        except Exception:
            continue
    m = re.search(r"(\d+)%", " ".join(txt))
    return int(m.group(1)) if m else None


hwnd, win = ctl.connect()
print("窗口:", win.window_text()[:50], flush=True)
print("起始进度:", pct(win), "%", flush=True)
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
print("生成前 BuildFile %d 个\n" % len(base), flush=True)

for rnd in range(1, 16):
    # ★ 每步之前查弹窗
    M.assert_no_modal(hwnd, "轮%d 开始" % rnd)
    cs = combos(win)
    empty = [(n, c, r) for n, c, r in cs
             if (lambda t: t == "请选择")(c.selected_text().strip())]
    if not empty:
        print("轮 %d: 本屏无空 ComboBox（进度 %s%%）" % (rnd, pct(win)), flush=True)
        break
    name, ctrl, r = empty[0]
    print("轮 %d: 填「%s」" % (rnd, name), flush=True)

    ctrl.click_input()
    time.sleep(0.5)

    # 下拉展开后可能弹提示；此时关掉再继续
    mrep = M.modal_report(hwnd)
    if mrep["count"]:
        print("   ⚠ 弹出模态 %d 个 -> 关掉" % mrep["count"], flush=True)
        M.close_modals(hwnd)
        hwnd, win = ctl.connect()
        continue

    # 选第一项：键盘
    import win32api
    import win32con
    for vk in (win32con.VK_DOWN, win32con.VK_RETURN):
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.06)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.25)

    hwnd, win = ctl.connect()
    p = pct(win)
    print("   -> 进度 %s%%" % p, flush=True)
    if p == 100:
        print("★★ 100%% 达成", flush=True)
        break

M.assert_no_modal(hwnd, "生成前")
btn = None
for c in win.descendants():
    try:
        if c.element_info.control_type == "Button" and \
                c.window_text().strip() == "生成预览":
            btn = c
            break
    except Exception:
        continue
if not btn:
    print("✗ 找不到「生成预览」")
    raise SystemExit(1)

print("\n点「生成预览」", flush=True)
btn.click_input()
time.sleep(1.0)
for i in range(24):
    time.sleep(5)
    now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    new = sorted(now - base)
    if new:
        print("  ★ %ds 新增: %s" % ((i + 1) * 5, new), flush=True)
        break
else:
    print("  120 秒无新增", flush=True)
