# -*- coding: utf-8 -*-
"""自适应原理验证：定位基准从「绝对坐标」改成「相对插件容器」。

⚑ 本轮实测暴露的根因
# ----------------------------------------------
# 我用 ``r.left > 1200`` 过滤插件区控件 —— 这本身就是**硬编码坐标**，
# 只是换了个形式：侧边栏挪到 x=1023 时，所有控件被这个门槛挡掉，
# 结果「一个都找不到」。
# ⇒ 正确的基准不是屏幕坐标，而是**插件容器自身的矩形**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 定位:   嘉立创 FA 插件 GUI 自动化的**定位层**，替换所有硬编码坐标。
#
# ⚑ 三层定位（与侧边栏宽度无关）
# ----------------------------------------------
#   第 1 层 **插件容器**  —— 「任务窗格」窗格本身，由 SolidWorks 布局决定，
#                           宽度可变 ⇒ 每轮**重新读**，绝不缓存。
#   第 2 层 **控件名字**  —— ComboBox/Button/Edit 的 ``window_text()``，
#                           与宽度无关，是**唯一稳定的锚**。
#   第 3 层 **坐标**     —— 只用控件当前读出的 ``rectangle()``，
#                           **绝不自己算、绝不记死**。
#
# 覆盖:   后续同级定义
# ⚠ 本模块只做定位；真正的动作在调用方，但**只接受本模块返回的坐标**。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
import warnings
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import ctl
import sw_gui_modal as M

warnings.filterwarnings("ignore")

#: 插件任务窗格在 SolidWorks 控件树里的**结构名**（与宽度无关）
CONTAINER_NAMES = ("任务窗格", "swInnerFrame", "EM Frame", "Task Pane Tabs Wnd")


def _all_controls(win):
    """遍历控件树，容忍读失败。"""
    try:
        return list(win.descendants())
    except Exception:
        return []


def find_container(win) -> Any | None:
    """找插件容器 —— 按**结构名**，不按坐标。

    ⚠ 取**面积最大**的那个「任务窗格」：SolidWorks 同一层可能有多个同名 Pane。
    """
    best = None
    for c in _all_controls(win):
        try:
            t = (c.window_text() or "").strip()
            if t not in CONTAINER_NAMES:
                continue
            r = c.rectangle()
        except Exception:
            continue
        if r.width() < 40 or r.height() < 40:
            continue
        area = r.width() * r.height()
        if best is None or area > best[1]:
            best = (c, area, r)
    return best


def scan(win) -> dict[str, tuple[str, Any]]:
    """扫描插件区控件，返回 ``{名字: (控件类型, rect)}``。

    ⚑ 判据：控件与插件容器**有横向重叠** ⇒ 属于插件区。
       不用任何绝对坐标，容器多宽都成立。
    """
    cont = find_container(win)
    if cont is None:
        return {}
    cr = cont[2]
    out: dict[str, tuple[str, Any]] = {}
    for c in _all_controls(win):
        try:
            t = (c.window_text() or "").strip()
            ct = c.element_info.control_type
            r = c.rectangle()
        except Exception:
            continue
        if not t or r.width() <= 0:
            continue
        overlap = min(r.right, cr.right) - max(r.left, cr.left)
        if overlap > min(r.width(), cr.width()) * 0.5:      # 与容器横向过半重叠
            out.setdefault(t, (ct, r))
    return out


def by_name(win, name: str, ctype: str | None = None) -> Any | None:
    """按**名字**（可选类型）取控件。找不到返回 None —— 不猜。"""
    for t, (ct, _r) in scan(win).items():
        if t == name and (ctype is None or ct == ctype):
            for c in _all_controls(win):
                try:
                    if (c.window_text() or "").strip() == name and \
                            c.element_info.control_type == ct:
                        return c
                except Exception:
                    continue
    return None


def rect_of(win, name: str, ctype: str | None = None):
    """只要坐标 —— 调用方唯一该用的东西。"""
    for t, (ct, r) in scan(win).items():
        if t == name and (ctype is None or ct == ctype):
            return r
    return None


def connect():
    """连上并顺手关掉可能存在的模态框。"""
    hwnd, win = ctl.connect()
    if M.modal_report(hwnd)["count"]:
        M.close_modals(hwnd, rounds=2)
        hwnd, win = ctl.connect()
    return hwnd, win
