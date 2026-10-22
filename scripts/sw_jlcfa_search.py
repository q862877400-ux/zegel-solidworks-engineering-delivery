r"""搜索取件 —— **全 UIA，不用截图**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测）
# 定位:   从任意页搜索型号并进入选型页。

# ⚑⚑⚑ 三处曾经的「截图依赖」及其根因（2026-09-30 逐个查清）
# ------------------------------------------------------------------
# ① **搜索框**（曾用截图找白条）
#    根因：从主窗口遍历 ``win.descendants()`` **漏节点**。
#    ⇒ 改成「主窗口 ∪ 容器元素」并集遍历后，搜索框直接可读：
#         Edit  ''  (2068,239,2463,264)     ← 无名字、在容器顶部
# ② **「搜索」按钮**（曾用截图推算 x）
#    ⇒ 并集遍历后直接可读：``Button '搜索' (2471,239,2547,271)``
# ③ **结果卡**（曾用截图找白块 + 猜 y 偏移）
#    根因：**两种页面的卡片标签不同名** ——
#         分类结果页写 ``Text '代码：HGH20HAZ0C'``
#         搜索结果页写 ``Text '型号：BSGY-C7-25'``   ← 我一直只找「代码：」
#    ⇒ 两种前缀都认，取标签的矩形中心点击（标签在卡内，卡整块可点）。

# ⚑ 输入方式：**搜索框用 UIA ValuePattern**（它不是选型参数、无校验）；
#   选型页的参数输入框必须**真键盘逐键 + Enter 提交**（见 sw_jlcfa_fill）。

# 覆盖:   后续同级定义
# ⚠ 会驱动鼠标。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import sw_jlcfa_locate as L
import sw_jlcfa_steps as S

warnings.filterwarnings("ignore")

#: 结果卡上的型号标签前缀（**两种页面不同名**，都要认）
CARD_PREFIXES = ("型号：", "代码：")


def search_row(win):
    """搜索行的 **Pane** —— 结构性锚，返回 ``(行Pane, 搜索框控件, 搜索按钮控件)``。

    ⚑⚑⚑ 实测结构（2026-09-30）
        Pane '设置'                                ← 搜索行的父
         ├─ Pane   ''      (1999,240,2067,272)     ← 返回图标
         ├─ Edit   ''      (2068,239,2463,264)     ← ★ 搜索框
         └─ Button '搜索'  (2471,239,2547,271)     ← ★ 搜索按钮

    ⇒ **搜索框与搜索按钮是同一 Pane 的兄弟**。
      所以：先按**名字**找到「搜索」按钮（名字稳定），
      再在**它的父 Pane 的子女**里找那个 ``Edit`` —— 那就是搜索框。
    ⚑ 这样**完全不用 y 偏移**（我先前写「容器顶部 200px 内的 Edit」，
      侧边栏拉宽 / DPI 变化后这个阈值就可能不成立）。
    """
    btn = L.locate(win, "搜索", "Button")
    if btn is None:
        return None, None, None
    try:
        par = btn.parent()
        eb = None
        for k in par.children():
            if k.element_info.control_type == "Edit":
                eb = k
                break
        return par, eb, btn
    except Exception:
        return None, None, btn


def search_box(win):
    """插件容器内的搜索框 ``(控件, 矩形)``。**结构定位，无坐标阈值**。"""
    _row, eb, _btn = search_row(win)
    if eb is None:
        return None, None
    return eb, eb.rectangle()


def search_button(win):
    """「搜索」按钮 ``(控件, 矩形)``。**按名字**。"""
    _row, _eb, btn = search_row(win)
    if btn is None:
        return None, None
    return btn, btn.rectangle()


def search(hwnd: int, win, code: str, log=S.log):
    """在搜索框填入 ``code`` 并点「搜索」。**纯 UIA，不截图**。返回 True/False。"""
    eb, er = search_box(win)
    if eb is None:
        log("      找不到搜索框（UIA）")
        return False
    sb, sr = search_button(win)
    if sb is None:
        log("      找不到「搜索」按钮（UIA）")
        return False
    # 搜索框不是选型参数（无范围校验）⇒ 用 ValuePattern 设值最稳，
    # 且**不依赖键盘焦点**。
    ok = False
    for meth in ("set_edit_text", "set_text"):
        try:
            getattr(eb, meth)(code)
            ok = True
            break
        except Exception:
            continue
    if not ok:
        # 退一步：点进去用键盘（需要焦点）
        if not S.ensure_front(hwnd):
            log("      ValuePattern 与键盘都不可用")
            return False
        S.click((er.left + er.right) // 2, (er.top + er.bottom) // 2, 0.5)
        # ⚠ 2026-10-01 轮 62：原来逐字符裸 `keybd_event`（按下 → sleep → 抬起，无 `final
        # ly`）
        #   ⇒ 中途异常会把**那个字符键卡在按下态**。⇒ 改走 `sw_gui_input._press`。
        import win32api

        from scripts import sw_gui_input as _gi

        for ch in code:
            vk = win32api.VkKeyScan(ch) & 0xFF
            _gi._press(vk, pause=0.03)
    time.sleep(0.4)
    log("      搜索框 = %r" % code)
    S.ensure_front(hwnd)
    S.click((sr.left + sr.right) // 2, (sr.top + sr.bottom) // 2, 1.0)
    return True


def _is_card_pane(c) -> tuple:
    """判断一个控件是不是**结果卡的 Pane**。是则返回 ``(型号, 卡矩形)``，否则 ``(None, None)``。

    ⚑⚑⚑ 实测结构（2026-09-30）—— 结果卡在树里长这样：

        Pane ''                                          ← ★ 卡片
         ├─ Text '产地：中国台湾'
         ├─ Text '型号：BSGY-C7-25'                      ← 型号标签
         ├─ Text '更新于：2026-09-30 11:50:30'           ← **卡片特有**
         └─ …

    ⇒ **判据：同一 Pane 下同时有「型号/代码：」和「更新于：」两个 Text**。
      **不用任何 y/x 阈值**（我先前用「容器顶部 200px 以上跳过」，
      侧边栏拉宽或 DPI 一变就可能误判）。
    """
    try:
        if c.element_info.control_type != "Pane":
            return None, None
        kids = list(c.children())
    except Exception:
        return None, None
    model = None
    has_upd = False
    for k in kids:
        try:
            t = (k.window_text() or "").strip()
        except Exception:
            continue
        if not has_upd and t.startswith("更新于："):
            has_upd = True
        if model is None:
            for p in CARD_PREFIXES:
                if t.startswith(p):
                    model = t[len(p) :].strip()
                    break
    if model is not None and has_upd:
        try:
            return model, c.rectangle()
        except Exception:
            return model, None
    return None, None


def result_cards(win) -> list[tuple[str, object]]:
    """结果卡列表 ``[(型号, 卡矩形)]``，按 y 排序。**结构判据，无坐标阈值**。"""
    cr = L.container_rect(win)
    out = []
    if cr is None:
        return out
    for c in L._controls(win):
        try:
            if c.element_info.control_type != "Pane":
                continue
            r = c.rectangle()
            if not L._overlaps(r, cr) or r.height() < 40:
                continue
        except Exception:
            continue
        model, rr = _is_card_pane(c)
        if model and rr is not None:
            out.append((model, rr))
    out.sort(key=lambda d: (d[1].top, d[1].left))
    return out


def first_result_point(win, log=S.log):
    """首个结果卡的点击点（**卡片矩形中心**）。结构判据，无坐标阈值。

    ⚑ 认**两种**标签：搜索结果页写 ``型号：``，分类结果页写 ``代码：``。
      只认一种就会「结果明明在，却定位不到」——这是我踩过的坑。
    """
    cards = result_cards(win)
    if not cards:
        return None
    model, r = cards[0]
    pt = ((r.left + r.right) // 2, (r.top + r.bottom) // 2)
    log(
        "      结果卡「%s」%s -> 点击 %s"
        % (model, (r.left, r.top, r.right, r.bottom), pt)
    )
    return pt


if __name__ == "__main__":
    h, w = L.connect()
    S.cache_drop()
    eb, er = search_box(w)
    print("搜索框:", (er.left, er.top, er.right, er.bottom) if er else None)
    sb, sr = search_button(w)
    print("搜索按钮:", (sr.left, sr.top, sr.right, sr.bottom) if sr else None)
    print("结果卡:", result_cards(w)[:4])
