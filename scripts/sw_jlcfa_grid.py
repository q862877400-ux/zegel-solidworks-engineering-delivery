r"""按**截图网格**定位卡片 —— UIA 对滚动内容给虚拟坐标，rect 不可用。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测）
# 定位:   卡片区（分类网格 / 结果网格）的点击坐标求解。

# ⚑⚑⚑ 为什么不能用 UIA 的 rect（2026-09-30 本机实测）
# ------------------------------------------------------------------
#   容器 rect          (1955, 115, 2563, 1361)   ← 视口坐标，正确
#   125 张分类卡片的 y  2509 … 8975               ← **远超容器**
#   「直线运动零件」Pane (1991, 309)               ← 与截图里 833 的位置**对不上**
# ⇒ 插件的**滚动内容区**在 UIA 里报的是**虚拟/内容坐标系**，
#   而固定头部（返回/搜索/全部商品分类）报的是视口坐标。
# ⇒ **卡片 rect 一律不可用于点击**。此前「点卡片不中」的根因就在这里。

# ⚑ 本模块的解法：**截图找格子 + UIA 给顺序**
# ------------------------------------------------------------------
#   ① 截图（PrintWindow，不受遮挡）里卡片是**浅色圆角矩形**，
#      按行扫描能稳定找出每个格子的视口坐标 —— 与 UIA 坐标系无关。
#   ② UIA 里卡片的**名字**是可靠的，且**按 (y, x) 排序 = 视觉阅读顺序**
#      （虚拟坐标的绝对值错，**相对顺序不错**）。
#   ③ 两者**按序 zip** ⇒ 「第 n 个名字」对应「第 n 个格子」。
#      ⇒ 既拿到正确坐标，又拿到正确名字，**且与侧边栏宽度无关**
#        （格子坐标是从当次截图量的）。

# 覆盖:   后续同级定义
# ⚠ 只做定位；点击由调用方发起。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import sw_jlcfa_locate as L
import sw_jlcfa_steps as S
import sw_jlcfa_cards as C

warnings.filterwarnings("ignore")

#: 卡片底色判定：浅色（近白）——实测卡片是白色圆角块，背景是浅灰
CARD_MIN_LUMA = 243
#: 一个格子的最小边长比例（相对容器宽）——用于排除小图标
MIN_CELL_RATIO = 0.08


def _luma(p) -> float:
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def card_rows(pane, min_h: int = 40) -> list[tuple[int, int, int, int]]:
    """从截图里扫出**卡片行带**（整行浅色区域的 y 范围与 x 范围）。

    做法：逐行统计浅色像素占比；占比高的连续行段 = 一行卡片；
    再在该行带内找出各列的分段。
    返回 ``[(x0, y0, x1, y1), ...]``，**按 (y, x) 排序**（阅读顺序）。
    """
    px = pane.load()
    w, h = pane.size
    light_rows = []
    for y in range(h):
        n = 0
        for x in range(0, w, 4):
            if _luma(px[x, y]) >= CARD_MIN_LUMA:
                n += 1
        light_rows.append(n * 4)

    # 连续「浅色像素数 > 宽度的 30%」的行段 = 卡片行
    bands = []
    start = None
    thr = w * 0.30
    for y, n in enumerate(light_rows):
        if n >= thr:
            if start is None:
                start = y
        else:
            if start is not None and y - start >= min_h:
                bands.append((start, y))
            start = None
    if start is not None and h - start >= min_h:
        bands.append((start, h))

    out = []
    for y0, y1 in bands:
        ym = (y0 + y1) // 2
        cols = []
        st = None
        for x in range(w):
            if _luma(px[x, ym]) >= CARD_MIN_LUMA:
                if st is None:
                    st = x
            else:
                if st is not None and x - st >= max(20, int(w * MIN_CELL_RATIO)):
                    cols.append((st, x))
                st = None
        if st is not None and w - st >= max(20, int(w * MIN_CELL_RATIO)):
            cols.append((st, w))
        for x0, x1 in cols:
            out.append((x0, y0, x1, y1))
    out.sort(key=lambda t: (t[1], t[0]))
    return out


def named_cards_in_order(win) -> list[str]:
    """UIA 里卡片名字的**阅读顺序**（按虚拟 y,x 排序，顺序可靠）。

    ⚑ 不含「代码：」前缀的结果卡 —— 那是另一类（结果页）。
    """
    allc = S.controls_cached(win)
    cr = S._container_from(allc)
    if cr is None:
        return []
    rows = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            if not t or t in C.SKIP_NAMES:
                continue
            if t.startswith(C.CODE_PREFIX):
                continue
            # 卡片本体是近似正方形；文字标签是细长条也在卡内
            if not (60 <= r.width() <= 260 and 60 <= r.height() <= 260):
                continue
            rows.append((r.top, r.left, t))
        except Exception:
            continue
    rows.sort()
    names = []
    for _, _, t in rows:
        if t not in names:
            names.append(t)
    return names


def locate_card(hwnd: int, win, name: str, log=S.log):
    """★ 按名字定位一张卡片的**屏幕坐标中心**。找不到返回 None。"""
    pane, cr = _capture(hwnd, win)
    if pane is None:
        return None
    cells = card_rows(pane)
    names = named_cards_in_order(win)
    log("      格子 %d 个 · 名字 %d 个" % (len(cells), len(names)))
    if not cells or not names:
        return None
    n = min(len(cells), len(names))
    try:
        i = names.index(name)
    except ValueError:
        log("      名字表里没有「%s」（前 8: %s）" % (name, names[:8]))
        return None
    if i >= n:
        log("      「%s」在第 %d 位，超出本屏 %d 格" % (name, i, n))
        return None
    x0, y0, x1, y1 = cells[i]
    cx = cr.left + (x0 + x1) // 2
    cy = cr.top + (y0 + y1) // 2
    log("      「%s」= 第%d格 pane(%d,%d,%d,%d) -> 屏幕(%d,%d)"
        % (name, i, x0, y0, x1, y1, cx, cy))
    return cx, cy


def _capture(hwnd: int, win):
    """PrintWindow 抓窗口自身并裁到插件容器（不受遮挡）。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("shot", r"D:\AI\SW\shot.py")
    sh = importlib.util.module_from_spec(spec)
    sys.modules["shot"] = sh
    spec.loader.exec_module(sh)
    cr = L.container_rect(win)
    if cr is None:
        return None, None
    img, ok, _W, _H = sh.capture(hwnd, "")
    if img is None:
        return None, None
    return img.crop((cr.left, cr.top, cr.right, cr.bottom)), cr


if __name__ == "__main__":
    h, w = L.connect()
    S.cache_drop()
    pane, cr = _capture(h, w)
    print("容器 %s  截图 %s" % (cr, pane.size))
    cells = card_rows(pane)
    print("格子 %d 个:" % len(cells))
    for c in cells[:12]:
        print("   %s" % (c,))
    names = named_cards_in_order(w)
    print("名字顺序（前 16）: %s" % names[:16])
