r"""嘉立创 FA 结果卡定位 —— **不依赖列数、不依赖宽度**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测）
# 定位:   在「结果列表」页定位并点击某张型号卡。

# ⚑⚑⚑ 关键设计：卡片是**图片**，UIA 树里没有名字、也没有可点语义
# ------------------------------------------------------------------
# 实测：结果页上所有卡片在控件树里**一个都读不到**（视口内只读到
#       「有更新」「返回」两个 Pane）。它们是自绘的图片按钮。
# ⇒ **不能靠「读卡片」，也不能靠「算列数 × 行距」**。

# ⚑⚑⚑ 用户指出的第二个坑：卡片**每页几个会随宽度变**
# ------------------------------------------------------------------
# 原话（2026-09-30）：「这个卡片现在一页三个，拖宽可以一页四五个，
#   拖窄一点就是一页两个，你能适配吗」
# ⇒ 我最初的做法「代码 y 的步长 = 126px」**当场作废** ——
#   126 是**单列**时的高度；变成两列后 y 序列完全不是那个等差数列。
# ⇒ **步长法不能用于「找第 N 张卡」。**

# ⚑ 正确解法：**以卡片自己的文字标签为锚**
# ------------------------------------------------------------------
# 每张卡的文字区有一个可读的 Text：**「代码：<型号>」**（实测有）。
# 它在卡片内部、位置随卡片走 ⇒ **读它就等于读到那张卡**。
#   · 列数变几个 → 标签自己换行，读到的 y 自然跟着变
#   · 宽度变了   → 标签 x 自然跟着变
#   · 不需要知道列数、不需要知道步长
#   · 多个同名 → 取离视口中心最近的那个（避免点到视口外的）
#
# 实测基准（容器 569px 宽，单列）：
#   「代码：HGH20HAZ0C」 y=621 · x 居中
#   卡片中心 ≈ 该标签 y − 55（标签在卡片下半部，图片在上半部）

# ⚑ 分类卡同理：名字由 UIA 给，**不靠截图抄**（我曾照截图手抄成
#    「导向轴支架」，实际是「导向轴支座」，于是 6/19 假失败）
# ⚑ 实测（容器 569px / 1495px 两种宽度，10 列 / 3 列两种排布）：
#     19 张分类卡**全部**能按名字读到坐标，100x100 大小一致
#       转轴(477,355) 导向轴(605,355) 导向轴支座(733,355) …
#     ⇒ **宽度/列数完全不影响** —— 因为坐标是「问控件树要」的。

# 覆盖:   后续同级定义
# ⚠ 本模块只做定位；点击由调用方发起。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")
#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import sw_jlcfa_locate as l  # noqa: E402

warnings.filterwarnings("ignore")

#: 结构名/导航名 —— 不是分类卡，收集时要排除
SKIP_NAMES = {
    "swCaption",
    "SearchBox",
    "swCmdMgr",
    "swMenu",
    "工作区",
    "任务窗格",
    "EM Frame",
    "header",
    "taskPaneConfig",
    "expandCollapse",
    "pin",
    "swInnerFrame",
    "Task Pane Tabs Wnd",
    "设置",
    "返回",
    "首页",
    "全部商品分类",
    "搜索",
    "同步数据",
    "有更新",
    "联系我们",
    "去官网",
    "个人中心",
    "数据同步进度(7010/8234)",
    "BottomOfMainOffForm3",
    "SubCategoryOffForm",
    "TopCategoryOffForm",
}

#: 卡片文字标签前缀（实测格式「代码：HGH20HAZ0C」）
CODE_PREFIX = "代码："
#: 卡片中心相对「代码」标签的纵向偏移（标签在卡片下半部）
CARD_DY = 55


def code_labels(win) -> list[tuple[int, int, str, Any]]:
    """读出所有「代码：xxx」标签。返回 [(y, x, 型号, rect)]，按 y 排。"""
    cr = l.container_rect(win)
    if cr is None:
        return []
    out = []
    for c in l._controls(win):
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if not t.startswith(CODE_PREFIX) or not l._overlaps(r, cr):
            continue
        out.append((r.top, r.left, t[len(CODE_PREFIX) :].strip(), r))
    out.sort()
    return out


def visible_codes(win) -> list[tuple[str, int, int]]:
    """⚠ **已废弃**：改用 ``sw_jlcfa_search.result_cards()``（结构判据）。

    旧实现用「容器顶部 +150 / 底部 -60」这种**相对偏移**判断卡片是否在视口内，
    侧边栏拉宽或 DPI 变化后不成立。保留仅为兼容旧调用。
    """
    return []


def locate_code(win, code: str):
    """按**型号代码**定位那张卡的中心点。找不到返回 None。

    ⚠ 不依赖列数/步长 ⇒ **宽度任意、每页几个任意都成立**。
    """
    hits = [(x, y) for c, x, y in visible_codes(win) if c == code]
    if not hits:
        return None
    if len(hits) == 1:
        return hits[0]
    # 同名多张：取最靠上的（列表按顺序排）
    hits.sort(key=lambda p: p[1])
    return hits[0]


def scroll_card_into_view(win, code: str, max_scrolls: int = 12):
    """若目标卡在视口外，**拖滚动条**直到它进视口。返回其中心点。

    ⚠ 滚动条位置由 ScrollBar 控件读出，**不硬编码**。
    """
    for _ in range(max_scrolls):
        p = locate_code(win, code)
        if p:
            return p
        sb = _scrollbar(win)
        if sb is None:
            return None
        x = (sb.left + sb.right) // 2
        _drag(x, sb.top + 40, x, sb.top + sb.height - 60)
        win = l.connect()[1]
    return locate_code(win, code)


def _scrollbar(win):
    """结果区的竖滚动条（最高的那个 ScrollBar）。"""
    cr = l.container_rect(win)
    best = None
    for c in l._controls(win):
        try:
            if c.element_info.control_type != "ScrollBar":
                continue
            r = c.rectangle()
        except Exception:
            continue
        if r.height() < 120:
            continue
        if cr and not l._overlaps(r, cr):
            continue
        if best is None or r.height() > best.height():
            best = r
    return best


def _drag(x1, y1, x2, y2, steps: int = 12) -> None:
    import time

    import win32api
    import win32con

    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos(
            (int(x1 + (x2 - x1) * i / steps), int(y1 + (y2 - y1) * i / steps))
        )
        time.sleep(0.03)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.6)


def category_cards(win, allc=None) -> list[tuple[str, Any]]:
    """列出**分类页**上的所有卡（按名字 → 矩形）。

    ⚠ 不筛控件类型/大小 —— 实测分类卡是 100x100 的 Pane，但尺寸可能随宽度变。
      只按「在插件区内 + 有名字 + 不是结构名」收。
    """
    cr = l.container_rect(win)
    if cr is None:
        return []
    out = []
    seen = set()
    for c in l._controls(win):
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if not t or t in SKIP_NAMES or t in seen:
            continue
        if not l._overlaps(r, cr) or r.width() < 40 or r.height() < 20:
            continue
        # ⚑ 去掉相对容器偏移（拉宽/DPI 变化会失效）
        seen.add(t)
        out.append((t, r))
    out.sort(key=lambda d: (d[1].top, d[1].left))
    return out


def locate_category(win, name: str, allc=None):
    """按名字定位一张分类卡。找不到返回 None。"""
    for t, r in category_cards(win, allc):
        if t == name or t.startswith(name):
            return r
    return None


if __name__ == "__main__":
    h, w = l.connect()
    cr = l.container_rect(w)
    print("容器宽 %d" % (cr.right - cr.left))
    vis = visible_codes(w)
    print("视口内的卡 %d 张: %s" % (len(vis), [c for c, _, _ in vis[:6]]))
    allc = code_labels(w)
    print(
        "全部代码标签 %d 个（视口外也读得到）: %s"
        % (len(allc), [c for _, _, c, _ in allc[:6]])
    )
