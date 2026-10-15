# -*- coding: utf-8 -*-
"""完整流程：焦点守卫 + 弹窗守卫 + 控件驱动，填到 100% 再生成。

⚑ 三条纪律，缺一不可：
   ① 每个动作**之前**：assert_focus（焦点守卫）
   ② 每个动作**之前**：assert_no_modal（弹窗守卫）
   ③ 每个动作**之后**：读控件值判定是否生效（不靠「我觉得」）
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
from pathlib import Path

import ctl
import sw_gui_focus as F
import sw_gui_modal as M

warnings.filterwarnings("ignore")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")

import re
import win32api
import win32con


def guard(hwnd, where):
    """① 关掉可能存在的弹窗 → ② 断言焦点。两道守卫合一。"""
    n = M.close_modals(hwnd, rounds=2)
    if n:
        print("   [守卫] 关掉 %d 个模态框 @%s" % (n, where), flush=True)
    F.assert_focus(hwnd, where)


def combos(win):
    out = []
    for c in win.descendants():
        try:
            if c.element_info.control_type != "ComboBox":
                continue
            r = c.rectangle()
            if r.height() >= 10:
                out.append((c.window_text().strip(), c, r))
        except Exception:
            continue
    return out


def pct(win):
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
print("窗口:", win.window_text()[:52], flush=True)
print("进度:", pct(win), "%   焦点:", F.focus_state(hwnd), flush=True)
base = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
print("BuildFile %d 个\n" % len(base), flush=True)

for rnd in range(1, 16):
    guard(hwnd, "轮%d-扫描" % rnd)
    cs = combos(win)
    empty = [(n, c, r) for n, c, r in cs
             if c.selected_text().strip() == "请选择"]
    if not empty:
        print("轮 %d: 本屏无空项（进度 %s%%）" % (rnd, pct(win)), flush=True)
        break
    name, ctrl, r = empty[0]
    print("轮 %d: 填「%s」 at (%d,%d)" % (rnd, name, r.left, r.top), flush=True)

    guard(hwnd, "轮%d-点击前" % rnd)
    ctrl.click_input()
    time.sleep(0.5)

    # 展开后可能弹提示
    if M.modal_report(hwnd)["count"]:
        print("   ⚠ 展开时弹模态 -> 关掉重来", flush=True)
        M.close_modals(hwnd)
        continue

    guard(hwnd, "轮%d-按键前" % rnd)
    for vk in (win32con.VK_DOWN, win32con.VK_RETURN):
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.06)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.25)

    hwnd, win = ctl.connect()
    p = pct(win)
    still = ctrl.selected_text().strip() if ctrl else "?"
    print("   -> 值=%r 进度=%s%%" % (still, p), flush=True)
    if p == 100:
        print("★★ 100%%", flush=True)
        break

guard(hwnd, "生成前")
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
    print("✗ 没有「生成预览」按钮")
    raise SystemExit(1)
print("\n点「生成预览」", flush=True)
btn.click_input()
time.sleep(1.0)
for i in range(24):
    time.sleep(5)
    now = {p.name for p in BF.iterdir() if p.is_file() and not p.name.startswith("~$")}
    new = sorted(now - base)
    if new:
        print("★ %ds 新增: %s" % ((i + 1) * 5, new), flush=True)
        break
else:
    print("120 秒无新增", flush=True)
M.screen_png(r"D:\AI\SW\shots\final_state.png")
print("整屏: final_state.png", flush=True)
