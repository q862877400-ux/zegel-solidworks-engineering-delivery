# -*- coding: utf-8 -*-
"""嘉立创 FA 插件批量抽查引擎 —— 每类抽 N 个差异大的零件，只生成预览不保存。

⚑ 已验证的单件流程（七步，全部实测通过）
# ----------------------------------------------
#   ① 关模态框   —— 「请先完成选型」弹窗，无焦点时吃掉所有按键
#   ② 点标签取焦点 —— 不抢前台，前台=插件子窗（6556410）
#   ③ 点 ComboBox 展开
#   ④ 点坐标选项   —— 键盘选不中，坐标点有效
#   ⑤ 拖滚动条     —— ★ 滚轮完全无效（实测坐标纹丝不动）
#   ⑥ Edit 输入    —— 自由输入类参数（长度等）
#   ⑦ 点「生成预览」—— 不点「插入」/「保存」⇒ **不产生文件，符合抽查要求**

# ⚑⚑ 关键教训（本项目连续九轮失败的根因，勿再犯）
# 「代码执行了」≠「操作生效了」。每步必须**验证**：
#   · 焦点：前台窗口是不是期望的那个
#   · 弹窗：有没有模态框挡着
#   · 填值：ComboBox.selected_text() 变没变
"""
from __future__ import annotations

import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import sw_gui_modal as M
import win32api
import win32con

warnings.filterwarnings("ignore")

BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")


def click(x, y, pause=0.14):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def drag(x1, y1, x2, y2, steps=10):
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.35)


def typ(s):
    for ch in s:
        sc = win32api.VkKeyScan(ch)
        vk, sh = sc & 0xFF, (sc >> 8) & 1
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.032)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.032)
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)


class UI:
    """插件界面的控件缓存 —— 一次读完，按名字查。"""

    def __init__(self):
        self.reconnect()

    def reconnect(self):
        self.hwnd, self.win = ctl.connect()
        self.scan()

    def scan(self):
        self.cb, self.lb, self.ed, self.gen, self.sx = {}, {}, {}, None, None
        for c in self.win.descendants():
            try:
                ct = c.element_info.control_type
                t = (c.window_text() or "").strip()
                r = c.rectangle()
            except Exception:
                continue
            if ct == "ComboBox" and r.height() >= 10:
                self.cb[t] = (c, r)
            elif ct == "Edit" and t:
                self.ed[t] = (c, r)
            elif ct in ("Pane", "Text") and r.width() > 250 and t:
                self.lb[t] = r
            elif ct == "Button":
                if t == "生成预览":
                    self.gen = (c, r)
                elif r.width() <= 30 and r.height() >= 100:
                    self.sx = max(self.sx or 0, r.left)

    def guard(self):
        if M.modal_report(self.hwnd)["count"]:
            M.close_modals(self.hwnd, rounds=2)
            self.reconnect()
            return True
        return False

    def pct(self):
        t = []
        for c in self.win.descendants():
            try:
                if c.element_info.control_type == "Text" and c.window_text():
                    t.append(c.window_text().strip())
            except Exception:
                continue
        m = re.search(r"(\d+)%", " ".join(t))
        return int(m.group(1)) if m else None

    def empties(self):
        out = []
        for n, (c, r) in self.cb.items():
            try:
                if c.selected_text().strip() == "请选择":
                    out.append((n, r))
            except Exception:
                continue
        return out

    def search_box(self):
        for c in self.win.descendants():
            try:
                if c.element_info.control_type != "Edit":
                    continue
                r = c.rectangle()
                if r.top < 300 and r.left > 1400 and r.width() > 200:
                    return c
            except Exception:
                continue
        return None

    def go_home(self):
        for c in self.win.descendants():
            try:
                if c.element_info.control_type == "Text" and \
                        c.window_text().strip() == "返回":
                    c.click_input()
                    time.sleep(1.8)
                    self.reconnect()
                    return True
            except Exception:
                continue
        return False


def fill_params(ui: UI, max_rounds: int = 16, log=print) -> tuple[int, list]:
    """把所有空参数填到 100%。返回 (进度, 过程)。"""
    trail = []
    for it in range(max_rounds):
        if ui.guard():
            continue
        ui.scan()
        p = ui.pct()
        if p == 100:
            return p, trail
        es = ui.empties()
        if not es:
            # 本屏填完 → 往下拖滚动条找下一批
            if ui.sx:
                drag(ui.sx + 8, 700, ui.sx + 8, 460)
                ui.scan()
                if not ui.empties():
                    drag(ui.sx + 8, 460, ui.sx + 8, 700)
                    ui.scan()
                    if not ui.empties():
                        # 还有空的在下面但滚不动了 —— 试 Edit
                        for nm, (e, r) in list(ui.ed.items()):
                            if not nm.strip():
                                continue
                            e.click_input()
                            time.sleep(0.3)
                            typ("400")
                            time.sleep(0.35)
                            win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)
                            time.sleep(0.06)
                            win32api.keybd_event(win32con.VK_TAB, 0,
                                                 win32con.KEYEVENTF_KEYUP, 0)
                            ui.reconnect()
                            trail.append("Edit:%s" % nm)
                            break
                        else:
                            return ui.pct(), trail
                    continue
            continue
        nm, r = es[0]
        lr = ui.lb.get(nm)
        if lr:
            click((lr.left + lr.right) // 2, (lr.top + lr.bottom) // 2, 0.1)
        ui.reconnect()
        ui.scan()
        if nm not in ui.cb:
            trail.append("%s(消失)" % nm)
            continue
        c, r = ui.cb[nm]
        c.click_input()
        time.sleep(0.55)
        if ui.guard():
            continue
        click((r.left + r.right) // 2, r.bottom + 14 + 30, 0.4)
        ui.reconnect()
        ui.scan()
        v = ui.cb.get(nm, (None, None))[0]
        val = v.selected_text().strip() if v is not None else "?"
        trail.append("%s=%s" % (nm, val))
        log("    %-12s -> %-10s %s%%" % (nm, val, ui.pct()))
    return ui.pct(), trail


def generate(ui: UI, log=print):
    """点「生成预览」。⚠ 不点「插入」/「保存」⇒ **不产生文件**。"""
    ui.guard()
    ui.scan()
    if not ui.gen:
        return None, "无「生成预览」按钮"
    ui.gen[0].click_input()
    # 「生成预览」是把模型塞进 SolidWorks，不落 BuildFile
    # ⇒ 判据是 SolidWorks 文档标题变了，不是目录里多了文件
    for _ in range(40):
        time.sleep(0.5)
        t = ui.win.window_text() or ""
        if t and (".SLDPRT" in t or ".SLDASM" in t):
            return t, "OK"
    return ui.win.window_text(), "超时（标题未变）"
