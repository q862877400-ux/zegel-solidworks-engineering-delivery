# -*- coding: utf-8 -*-
"""自愈式单步执行器 —— 每步自己验证，错了自动退回去重来。

⚑⚑⚑ 三条铁律（用户 2026-09-30 定）
# --------------------------------------------------
# ① **小步验证小步闭环**：一次只做一个动作，做完**自己**截图判定，
#    不用人来盯。
# ② **全自动 + 自我纠错 + 自我纠偏 + 自动愈合**：
#    每步都有「预期」和「实测」，不符就**自动回退到上一个已验证状态**，
#    换策略重试，且**永不无限循环**（有总预算、有退避）。
# ③ 「数据同步进度(7010/8234)」**只是界面上的一个展示**，
#    不影响任何操作（用户明确说明）——
#    ⚠ 我此前把它当成「插件卡死」的证据，连着两小时白等，那是错的。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装）
# 定位:   把「盲点坐标 + 事后肉眼看」换成「按控件身份定位 + 每步自验 + 失败自愈」。
#
# 覆盖:   后续同级定义
# ⚠ 本模块会**驱动鼠标键盘**；调用方须先向用户说明。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
import warnings
from typing import Any, Callable

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import win32api
import win32con
import win32gui

warnings.filterwarnings("ignore")

import sw_jlcfa_locate as L
import draw_loc as D

T0 = time.time()
BUDGET = {"steps": 0, "max_steps": 240, "heals": 0, "max_heals": 12}


def log(msg: str) -> None:
    print("[%6.1fs] %s" % (time.time() - T0, msg), flush=True)


def out_of_budget(what: str) -> bool:
    if (BUDGET["steps"] >= BUDGET["max_steps"]
            or BUDGET["heals"] >= BUDGET["max_heals"]):
        log("!! 预算耗尽（步骤 %d / 自愈 %d）—— 放弃「%s」"
            % (BUDGET["steps"], BUDGET["heals"], what))
        return True
    return False


# ── 基础动作 ────────────────────────────────────────────────────────
def click(x: int, y: int, pause: float = 0.18) -> None:
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def drag(x1: int, y1: int, x2: int, y2: int, steps: int = 10) -> None:
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.025)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.5)


def key(vk: int, pause: float = 0.16) -> None:
    win32api.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(pause)


def typ(text: str) -> None:
    for ch in text:
        sc = win32api.VkKeyScan(ch)
        v, sh = sc & 0xFF, (sc >> 8) & 1
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(v, 0, 0, 0)
        time.sleep(0.028)
        win32api.keybd_event(v, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.028)
        if sh:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)


# ── 状态观测（自验的依据）────────────────────────────────────────────
def observe(hwnd: int, win) -> dict[str, Any]:
    """读一次当前状态：所有可判据的量。**只读**。"""
    cr = L.container_rect(win)
    st: dict[str, Any] = {"container": cr, "pct": None, "combos": {},
                          "buttons": {}, "edits": {}, "modal": 0}
    st["modal"] = L._modal().modal_report(hwnd)["count"]
    if cr is None:
        return st
    texts = []
    for c in L._controls(win):
        try:
            ct = c.element_info.control_type
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if not L._overlaps(r, cr):
            continue
        if ct == "ComboBox":
            try:
                st["combos"][t] = c.selected_text().strip()
            except Exception:
                pass
        elif ct == "Button" and t:
            st["buttons"][t] = r
        elif ct == "Edit" and t:
            st["edits"][t] = r
        if ct in ("Text", "Pane") and t:
            texts.append(t)
    joined = " ".join(texts)
    import re
    m = re.search(r"(\d+)%", joined)
    if m:
        st["pct"] = int(m.group(1))
    st["has_return"] = "返回" in joined
    st["has_result"] = "个结果" in joined
    st["has_model"] = "个备选型号" in joined
    return st


def screenshot(path: str, hwnd: int, win):
    """自取证：截图存盘（供事后复盘，不需要人盯）。"""
    L.focus_solidworks(hwnd)
    pane, cr = D.capture_pane(hwnd, win)
    if pane is not None:
        pane.save(path)
    return pane, cr


# ── 自愈执行：动作 → 验证 → 不符则回退重来 ──────────────────────────
def do_with_verify(name: str, act: Callable[[], None],
                   check: Callable[[], bool],
                   heal: Callable[[], None] | None = None,
                   tries: int = 3) -> bool:
    """执行一个动作并自验。失败则调用 heal() 后重试，超过 tries 返回 False。

    ⚠ **不再让��盯**：每一步都自己截图 + 读状态判定。
    """
    BUDGET["steps"] += 1
    if out_of_budget(name):
        return False
    for t in range(1, tries + 1):
        try:
            act()
        except Exception as exc:
            log("  %s 第%d次异常: %s" % (name, t, str(exc)[:60]))
        ok = False
        try:
            ok = bool(check())
        except Exception as exc:
            log("  %s 校验异常: %s" % (name, str(exc)[:60]))
        if ok:
            log("  ✓ %s（第%d次）" % (name, t))
            return True
        log("  ✗ %s 未达预期（第%d次）" % (name, t))
        BUDGET["heals"] += 1
        if out_of_budget(name + " 自愈"):
            return False
        if heal:
            try:
                heal()
            except Exception as exc:
                log("  自愈动作异常: %s" % str(exc)[:60])
    log("  ✗✗ %s 重试 %d 次仍失败" % (name, tries))
    return False
