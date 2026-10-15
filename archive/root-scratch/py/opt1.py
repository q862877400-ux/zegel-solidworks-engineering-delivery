# -*- coding: utf-8 -*-
"""优化版：目标 30 秒内完成「搜索 -> 填参数 -> 生成」。

⚑ 速度优化点（相对上一版约 2 分钟）
# ------------------------------------------
# ① **缓存控件树**：UIA 读树是最大开销（~1.5s/次）。上一版每步都重连+重读，
#    这里改成「一次读完，局部失效时才重读」。
# ② **去掉每步截图**：只在关键节点（开始/生成前/结果）截。
# ③ **固定滚动位置**：记录滑块拖动量，避免反复试。
# ④ **等待改为状态驱动**：轮询 BuildFile 目录，不固定 sleep。
# ⑤ **免 close_modals 轮询**：只在动作前查一次。
"""
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
T0 = time.time()


def el(msg):
    print("[%5.1fs] %s" % (time.time() - T0, msg), flush=True)


def click(x, y, pause=0.16):
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
    time.sleep(0.4)


# ── 控件索引：一次读完，之后按名字/类型查，不重读 ──
class Pane:
    def __init__(self):
        self.hwnd, self.win = ctl.connect()
        self.refresh()

    def refresh(self):
        self.combos = {}
        self.labels = {}
        self.edits = {}
        self.btn_gen = None
        self.scroll_x = None
        for c in self.win.descendants():
            try:
                ct = c.element_info.control_type
                t = c.window_text().strip()
                r = c.rectangle()
            except Exception:
                continue
            if ct == "ComboBox" and r.height() >= 10:
                self.combos[t] = (c, r)
            elif ct == "Edit" and t:
                self.edits[t] = (c, r)
            elif ct in ("Pane", "Text") and r.width() > 250 and t:
                self.labels[t] = r
            elif ct == "Button":
                if t == "生成预览":
                    self.btn_gen = (c, r)
                elif r.width() <= 30 and r.height() >= 100:
                    self.scroll_x = max(self.scroll_x or 0, r.left)

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

    def modal_ok(self):
        n = M.modal_report(self.hwnd)["count"]
        if n:
            M.close_modals(self.hwnd, rounds=2)
            self.refresh()
        return n == 0


def pick(pane, name, row=1):
    """填一个 ComboBox：点标签取焦点 -> 点开 -> 点选项。"""
    pane.modal_ok()
    lr = pane.labels.get(name)
    if lr:
        click((lr.left + lr.right) // 2, (lr.top + lr.bottom) // 2, 0.12)
    if name not in pane.combos:
        pane.refresh()
        if name not in pane.combos:
            return False, "控件消失"
    cb, r = pane.combos[name]
    cb.click_input()
    time.sleep(0.55)
    if not pane.modal_ok():
        return False, "展开时弹模态"
    click((r.left + r.right) // 2, r.bottom + 14 + row * 30, 0.45)
    pane.refresh()
    v = pane.combos.get(name, (None, None))[0]
    val = v.selected_text().strip() if v is not None else "(不在屏)"
    return val != "请选择", val


def main():
    el("连接")
    pane = Pane()
    el("初始进度 %s%%" % pane.pct())

    # ── 填所有空的 ComboBox ──
    for it in range(1, 14):
        pane.modal_ok()
        pane.refresh()
        if pane.pct() == 100:
            break
        empty = [(n, v) for n, (v, r) in pane.combos.items()
                 if v.selected_text().strip() == "请选择"]
        if not empty:
            # 本屏填完 -> 拖滚动条往下
            if pane.scroll_x:
                drag(pane.scroll_x + 8, 700, pane.scroll_x + 8, 470)
                pane.refresh()
                if not [(n, v) for n, (v, r) in pane.combos.items()
                        if v.selected_text().strip() == "请选择"]:
                    drag(pane.scroll_x + 8, 470, pane.scroll_x + 8, 700)   # 滚回
                    pane.refresh()
                    if not any(v.selected_text().strip() == "请选择"
                               for v, _ in pane.combos.values()):
                        break
            else:
                break
            continue
        name, _ = empty[0]
        ok, val = pick(pane, name)
        el("  填 %-10s -> %-10s  %s%%" % (name, val, pane.pct()))
        if not ok and val == "控件消失":
            break

    # ── Edit 类参数（滑轨长度）──
    pane.refresh()
    # ⚠ 已经 100% 时**不要**再动 Edit —— 改写已提交的值会触发插件校验失败
    for nm, (ed, r) in (list(pane.edits.items()) if pane.pct() != 100 else []):
        if not nm.strip():
            continue
        el("输入 %s" % nm)
        ed.click_input()
        time.sleep(0.35)
        for ch in "1000":
            vk = win32api.VkKeyScan(ch) & 0xFF
            win32api.keybd_event(vk, 0, 0, 0)
            time.sleep(0.035)
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.035)
        time.sleep(0.5)
        pane.refresh()
        el("  -> %s%%" % pane.pct())
        if pane.pct() == 100:
            break

    pane.refresh()
    el("最终进度 %s%%" % pane.pct())
    if pane.pct() != 100:
        M.screen_png(r"D:\AI\SW\shots\opt_not100.png")
        el("⚠ 未到 100%，截图 opt_not100.png")
        return 1

    # ── 生成 ──
    base = {p.name for p in BF.iterdir() if p.is_file()
            and not p.name.startswith("~$")}
    pane.refresh()
    if not pane.btn_gen:
        el("✗ 无「生成预览」")
        return 1
    el("点「生成预览」")
    pane.btn_gen[0].click_input()
    for i in range(40):
        time.sleep(0.4)
        now = {p.name for p in BF.iterdir() if p.is_file()
               and not p.name.startswith("~$")}
        new = sorted(now - base)
        if new:
            el("★ 新增 %s" % new)
            return 0
    el("超时无新增")
    M.screen_png(r"D:\AI\SW\shots\opt_timeout.png")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
