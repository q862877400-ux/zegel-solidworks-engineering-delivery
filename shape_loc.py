# -*- coding: utf-8 -*-
"""形状/颜色匹配定位器 —— 处理「自绘控件在 UIA 树里读不到」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 定位:   嘉立创 FA 插件的定位层第 2 方案（形状特征）。
#
# ⚑ 为什么需要它（用户 2026-09-30 的两处指正）
# ----------------------------------------------
# ① **侧边栏宽度可随意拖动** —— 硬编码坐标（1390,148 / 1749,931 …）全部作废。
#    ⇒ 第一方案（控件名，见 sw_gui_locate）已解决：名字与宽度无关。
# ② **读不到控件就该看截图** —— 而非反复换方法。
#
# ⚑ 两类控件，只有形状能认
# ----------------------------------------------
#   UIA 树里**有**名字的：ComboBox「滑块类型」、Button「生成预览」、Pane「返回」
#     ⇒ 用名字定位（稳定）。
#   UIA 树里**没有**的：搜索框、「搜索」按钮、「全部商品分类」、「首页」、
#     「同步数据」——它们是 **WinForms 自绘控件**，名字层拿不到。
#     ⇒ 用**颜色 + 形状**在截图里认：
#         · 「全部商品分类」= **蓝底白字**的实心矩形（插件主题色 #2B6BE4 类）
#         · 「搜索框」      = **白底 + 浅灰边框**的横向长条
#         · 「搜索」按钮    = 与分类按钮同色系的小矩形（在搜索框右侧）
#     这些特征**与侧边栏宽度无关** ⇒ 宽度任变都成立。

# 覆盖:   后续同级定义
# ⚠ 只做**定位**，不做动作；返回容器相对矩形（x, y, w, h）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import warnings
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import loc

warnings.filterwarnings("ignore")

#: 插件主题蓝。⚠ 本机实测（截图采样，2026-09-30）真实值是
#:   ``RGB(48,80,224)`` 为主、``RGB(0,144,224)`` 次之 ——
#:   **不是**我一开始凭印象写的 (43,107,228)，那个阈值太严导致一个都找不到。
THEME_BLUES = ((48, 80, 224), (0, 144, 224))
BLUE_TOL = 40          # 各通道容差


def _is_blue(p) -> bool:
    """蓝底判定：命中任一主题蓝，且**明显偏蓝**（排除浅蓝边框/文字）。"""
    r, g, b = p[0], p[1], p[2]
    if b < 130 or b - r < 60 or b - g < 30:
        return False
    return any(abs(r - t[0]) <= BLUE_TOL and abs(g - t[1]) <= BLUE_TOL
               and abs(b - t[2]) <= BLUE_TOL for t in THEME_BLUES)


def _is_white_box(p) -> bool:
    r, g, b = p[0], p[1], p[2]
    return r > 238 and g > 238 and b > 238


def find_blue_rects(pane_img, min_w: int = 40, min_h: int = 18):
    """在插件区截图里找**蓝色实心矩形块**（= 主题按钮）。

    返回按 (top, left) 排序的 ``[(l, t, r, b), ...]``，坐标**相对 pane**。
    """
    w, h = pane_img.size
    px = pane_img.load()
    # 横向扫描每行，连续蓝色 >= min_w 的段
    rows: dict[int, list] = {}
    for y in range(0, h, 2):
        run_start = None
        for x in range(0, w, 2):
            if _is_blue(px[x, y]):
                if run_start is None:
                    run_start = x
            elif run_start is not None:
                if x - run_start >= min_w:
                    rows.setdefault(y, []).append((run_start, x))
                run_start = None
    # 把相邻行的段合并成矩形
    rects = []
    prev = []
    for y in sorted(rows):
        cur = rows[y]
        merged = []
        for a, b in cur:
            hit = None
            for i, (pa, pt, pb) in enumerate(merged):
                if a <= pb + 8 and b >= pa - 8:
                    hit = i
                    break
            if hit is None:
                merged.append([a, y, b])
            else:
                merged[hit][0] = min(merged[hit][0], a)
                merged[hit][2] = max(merged[hit][2], b)
                merged[hit][1] = min(merged[hit][1], y)
        prev = [(m[0], m[1], m[2]) for m in merged]
        rects.extend([(m[0], m[1], m[2], y) for m in merged
                      if m[2] - m[0] >= min_w and y - m[1] >= min_h])
    # 去重（同一按钮被多行记过）
    out, seen = [], set()
    for r in sorted(rects, key=lambda t: (t[1], t[0])):
        k = (r[0] // 20, r[1] // 20)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def locate_by_shape(win, img, which: str):
    """按形状定位。``which`` ∈ {category_btn, search_btn, search_box}。

    返回相对 pane 的 ``(l, t, r, b)``；找不到返回 None。
    """
    rects = find_blue_rects(img)
    if which in ("category_btn", "search_btn"):
        if not rects:
            return None
        # 「搜索」按钮在搜索框右边、通常靠右；「全部商品分类」靠左
        # ⇒ 按 x 排序：最左 = 分类按钮，最右 = 搜索按钮
        rects.sort(key=lambda r: r[0])
        if which == "category_btn":
            return rects[0]
        return rects[-1]
    if which == "search_box":
        # 白底长条：在蓝色按钮左侧、同一行
        w, h = img.size
        px = img.load()
        best = None
        for y in range(60, min(h, 200), 2):
            run = None
            for x in range(0, int(w * 0.75), 2):
                if _is_white_box(px[x, y]):
                    if run is None:
                        run = x
                elif run is not None:
                    if x - run > 150:
                        if best is None or (x - run) > best[2] - best[0]:
                            best = (run, y, x, y)
                    run = None
        return best
    return None
