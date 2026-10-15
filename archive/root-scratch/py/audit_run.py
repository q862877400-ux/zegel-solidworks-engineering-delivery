# -*- coding: utf-8 -*-
"""全自动抽查：每个大类抽 3 个差异大的零件，生成预览不保存。

⚑ 全程用 sw_jlcfa_locate 的三层定位（控件名 -> 颜色形状 -> 比例），
   **零硬编码坐标**，侧边栏宽度任意。
⚑ 「生成预览」只把模型塞进 SolidWorks，**不点「插入」/「保存」**
   ⇒ 不产生文件。
"""
import json
import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import sw_jlcfa_locate as L
import draw_loc as D
import win32api
import win32con

warnings.filterwarnings("ignore")
T0 = time.time()
OUT = Path(r"D:\AI\SW\audit")


def el(m):
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


def click(x, y, pause=0.14):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def drag(x1, y1, x2, y2, steps=10):
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.025)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.5)


def typ(s):
    for ch in s:
        sc = win32api.VkKeyScan(ch)
        vk, sh = sc & 0xFF, (sc >> 8) & 1
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.03)
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)


def clear_and_type(s):
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord("A"), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    for _ in range(28):
        win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
        time.sleep(0.01)
        win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)
    typ(s)


def pct_of(win):
    t = []
    for c in L._controls(win):
        try:
            if c.element_info.control_type == "Text" and c.window_text():
                t.append(c.window_text().strip())
        except Exception:
            continue
    m = re.search(r"(\d+)%", " ".join(t))
    return int(m.group(1)) if m else None


def search_box_xy(hwnd, win):
    """★ 搜索框是**自绘 Pane**，UIA 树里不是 Edit ⇒ 用形状定位（第 2 层）。
    ⚠ 实测 598px 窄侧边栏下，Edit 类控件在插件区**一个都没有**。"""
    pts = D.locate_all(hwnd, win, log=lambda m: None)
    return pts.get("search_box")


def fill_params(hwnd, win, log):
    """把所有空 ComboBox 填到 100%。"""
    cr = L.container_rect(win)
    for it in range(18):
        if L._modal().modal_report(hwnd)["count"]:
            L._modal().close_modals(hwnd, rounds=2)
            hwnd, win = L.connect()
            continue
        p = pct_of(win)
        if p == 100:
            return hwnd, win, p
        # 找第一个「请选择」的 ComboBox
        target = None
        for c in L._controls(win):
            try:
                if c.element_info.control_type != "ComboBox":
                    continue
                r = c.rectangle()
                if r.height() < 10 or not L._overlaps(r, cr):
                    continue
                if c.selected_text().strip() == "请选择":
                    target = (c, r, c.window_text().strip())
                    break
            except Exception:
                continue
        if not target:
            break
        cb, r, nm = target
        # 点标签取焦点（同名 Pane/Text，通常在左侧）
        lab = None
        for c in L._controls(win):
            try:
                if (c.window_text() or "").strip() == nm and \
                        c.element_info.control_type in ("Pane", "Text"):
                    lr = c.rectangle()
                    if lr.width() > 200 and L._overlaps(lr, cr):
                        lab = lr
                        break
            except Exception:
                continue
        if lab:
            click((lab.left + lab.right) // 2, (lab.top + lab.bottom) // 2, 0.1)
        hwnd, win = L.connect()
        cr = L.container_rect(win)
        cb = None
        for c in L._controls(win):
            try:
                if c.element_info.control_type == "ComboBox" and \
                        (c.window_text() or "").strip() == nm:
                    cb = c
                    break
            except Exception:
                continue
        if cb is None:
            continue
        rr = cb.rectangle()
        cb.click_input()
        time.sleep(0.55)
        if L._modal().modal_report(hwnd)["count"]:
            L._modal().close_modals(hwnd, rounds=2)
            continue
        # 点第一个非「请选择」项
        click((rr.left + rr.right) // 2, rr.bottom + 14 + 30, 0.4)
        hwnd, win = L.connect()
        log("      %-12s %s%%" % (nm, pct_of(win)))
    return hwnd, win, pct_of(win)


def one_part(hwnd, win, cat, code, log):
    """单个零件的完整流程。"""
    # ① 回首页
    ret = L.locate(win, "返回", "Text")
    if ret:
        ret.click_input()
        time.sleep(2.0)
        hwnd, win = L.connect()
    # ② 搜索
    pt = search_box_xy(hwnd, win)
    if pt is None:
        return hwnd, win, "找不到搜索框"
    click(pt[0], pt[1], 0.4)          # 点搜索框
    time.sleep(0.35)
    clear_and_type(code)
    time.sleep(0.35)
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.06)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    # ③ 等结果卡
    card = None
    for _ in range(20):
        time.sleep(0.6)
        hwnd, win = L.connect()
        for c in L._controls(win):
            try:
                if c.element_info.control_type == "Text" and \
                        code in (c.window_text() or ""):
                    card = c
            except Exception:
                continue
        if card:
            break
    if not card:
        return hwnd, win, "无搜索结果"
    card.click_input()
    time.sleep(3.0)
    hwnd, win = L.connect()
    # ④ 填参数
    hwnd, win, p = fill_params(hwnd, win, log)
    if p != 100:
        return hwnd, win, "未到100%%(%s)" % p
    # ⑤ 生成预览
    btn = L.locate(win, "生成预览", "Button")
    if btn is None:
        return hwnd, win, "无生成按钮"
    btn.click_input()
    time.sleep(2.5)
    return hwnd, win, "OK"


def main():
    OUT.mkdir(exist_ok=True)
    from audit_plan import TARGETS
    hwnd, win = L.connect()
    cr = L.container_rect(win)
    el("容器 %s 宽 %d" % (cr, cr.right - cr.left))
    results = []
    for cat, codes in TARGETS:
        for code in codes:
            el("=== %s / %s ===" % (cat, code))
            hwnd, win, st = one_part(hwnd, win, cat, code, el)
            el("  -> %s" % st)
            results.append({"cat": cat, "code": code, "status": st})
            hwnd, win = L.connect()
    el("=== 汇总 ===")
    for r in results:
        el("  %-14s %-14s %s" % (r["cat"], r["code"], r["status"]))
    (OUT / "result.json").write_text(json.dumps(results, ensure_ascii=False,
                                             indent=1), encoding="utf-8")
    el("结果存 audit/result.json")


if __name__ == "__main__":
    main()
