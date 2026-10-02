r"""嘉立创 FA 插件的定位层 —— 与侧边栏宽度无关的三层定位。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装并实测驱动）
# 定位:   把「坐标驱动」换成「控件身份驱动」，让自动化**适配任意侧边栏宽度**。

# ⚑⚑⚑ 为什么必须换掉硬编码坐标（用户 2026-09-30 的指正）
# ------------------------------------------------------------------
# 原话：「这个侧边栏它的宽度是可以随意调整的，我今天默认是这么宽，
#       明天我手动拉一下，那你岂不是就失效了」
# ⇒ 我此前写的 (1390,148) / (1749,931) / (1672,913) 等**全部作废**。
# 本机实测验证：把侧边栏从 581px 拖到 800px，插件整体左移 1179px，
#   **控件名不变、控件树一个不丢** ⇒ 名字就是稳定锚。

# ⚑ 三层定位（自上而下，前一层够用就不走后一层）
# ------------------------------------------------------------------
# ① **控件名** —— ComboBox「滑块类型」/ Button「生成预览」/ Pane「返回」
#    最稳。UIA 树里读得到，且**与宽度无关**（本机 581px / 800px 两次验证）。
# ② **颜色+形状** —— 「全部商品分类」「搜索」这类**自绘控件**在 UIA 树里
#    **没有名字**（实测缺失），但主题蓝底矩形认得出：
#        分类按钮贴容器左端（实测相对左 5.5%）
#        搜索按钮贴容器右端（实测相对左 88.5%）
#    颜色值是**截图采样实测**的 (48,80,224) 与 (0,144,224)，
#    ⚠ 不是凭印象写的值 —— 一开始写 (43,107,228) 阈值太严，一个都找不到。
# ③ **容器相对比例** —— 前两层都拿不到时的兜底。

# ⚑ 取证方式的两个坑（都是实测踩到的）
# ------------------------------------------------------------------
#   ``PrintWindow(hwnd)``  只抓窗口**自身**，**丢掉客户区之外的浮窗**
#                        ⇒ 插件的模态提示框（「请先完成选型」）根本拍不到，
#                          导致连续九轮都误判成「控件不响应」。
#   ``ImageGrab.grab()``  抓整屏，会抓到**遮挡物**
#                        ⇒ 必须先把 SolidWorks 置前再截。
#   二者互补：**看主界面用 PrintWindow，看浮窗用 ImageGrab + 置前**。

# 覆盖:   后续同级定义
# ⚠ 本模块只做**定位**；动作（点击/按键）由调用方发起。
# ⚠ 依赖 ``pywinauto``（UIA 后端）与 ``Pillow``。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
import warnings
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

__all__ = [
    "CONTAINER_NAMES", "THEME_BLUES", "locate", "container_rect",
    "find_blue_groups", "focus_solidworks", "capture_front", "capture_window",
]

# ── 第 1 层：容器 ────────────────────────────────────────────────────
#: 插件任务窗格在 SolidWorks 控件树里的**结构名**（与宽度无关）
CONTAINER_NAMES = ("任务窗格", "swInnerFrame", "EM Frame", "Task Pane Tabs Wnd")

# ── 第 2 层：形状 ────────────────────────────────────────────────────
#: 主题蓝底色（**截图采样实测值**，非凭印象）
THEME_BLUES = ((48, 80, 224), (0, 144, 224))
BLUE_TOL = 45


def _ctl():
    import ctl
    return ctl


def _modal():
    import sw_gui_modal
    return sw_gui_modal


def connect():
    """连上 SolidWorks，顺手关掉可能存在的模态框。"""
    hwnd, win = _ctl().connect()
    if _modal().modal_report(hwnd)["count"]:
        _modal().close_modals(hwnd, rounds=2)
        hwnd, win = _ctl().connect()
    return hwnd, win


def container_element(win):
    """插件容器**元素本身**（不是矩形）。找不到返回 None。"""
    best = None
    try:
        cands = list(win.descendants())
    except Exception:
        return None
    for c in cands:
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
            best = (c, area)
    return best[0] if best else None


def _dedupe_key(c):
    """控件去重键（类型 + 名字 + 粗粒度位置）。读不到就退回 id()。"""
    try:
        r = c.rectangle()
        return (
            c.element_info.control_type,
            (c.window_text() or "").strip()[:40],
            (r.left // 3, r.top // 3, r.right // 3, r.bottom // 3),
        )
    except Exception:
        return ("id", id(c))


def _controls(win):
    """遍历控件 —— ★ **两种根取并集**。

    ⚑⚑⚑ 为什么必须取并集（2026-09-30 本机实测，这是「生成预览按钮时有时无」的真因）

        从主窗口遍历      ``win.descendants()``        1055 节点
          → 过滤到插件容器内 267 个，**「生成预览」不在其中**（一个都没有）
        从容器元素遍历    ``container.descendants()``   134 节点
          → **「生成预览」在里面** ``Button (2362,1271)``

    ⇒ SolidWorks 的 UIA provider 在**主窗口深层遍历时会截断/折叠**，
      页面越复杂（节点越多）越容易丢尾部控件。
      **两种遍历的结果不是包含关系**（各自都缺东西），
      所以必须**并集**，不能只挑一种。
    ⚠ 这也解释了此前「放宽查找条件」「截图兜底」都不稳：
      **根因在遍历漏节点，不在查找条件太严。**
    """
    out = []
    seen = set()
    try:
        for c in win.descendants():
            k = _dedupe_key(c)
            if k not in seen:
                seen.add(k)
                out.append(c)
    except Exception:
        pass
    try:
        cont = container_element(win)
        if cont is not None:
            for c in cont.descendants():
                k = _dedupe_key(c)
                if k not in seen:
                    seen.add(k)
                    out.append(c)
    except Exception:
        pass
    return out


def container_rect(win):
    """插件容器矩形 —— 取面积最大的那个「任务窗格」，**每轮重读**。"""
    best = None
    for c in _controls(win):
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
    return best[2] if best else None


def _overlaps(r, cr) -> bool:
    ov = min(r.right, cr.right) - max(r.left, cr.left)
    return ov > min(r.width(), cr.width()) * 0.5


def locate(win, name: str, ctype: str | None = None):
    """★ 第 1 层：按**控件名**取控件对象。找不到返回 None —— 不猜。

    ⚑⚑⚑ 同名多控件（实测「返回」有 5 个，本机 2026-09-30）
    一个名字会同时命中**容器 Pane / 图标 / 真正的链接**。
    取第一个 ⇒ 点到 568x46 的页脚空壳。
    取面积最小 ⇒ 也错：20x19 的**页脚图标**比 24x30 的**左上角真链接**还小。
    ⚠ **按形状猜哪个才是对的，第三次还是猜错了。**
    ⇒ 正确做法在 ``locate_all()`` + 调用方「**逐个试、用页面变化验收**」。
    本函数只做**确定性**选取：可见 + 在容器内 + **类型为 Text/Button 优先**。
    """
    cr = container_rect(win)
    best = None
    for c in _controls(win):
        try:
            if (c.window_text() or "").strip() != name:
                continue
            if ctype and c.element_info.control_type != ctype:
                continue
            r = c.rectangle()
            if r.width() <= 0 or r.height() <= 0:
                continue
            if cr and not _overlaps(r, cr):
                continue
            try:
                if not c.is_visible():
                    continue
            except Exception:
                pass
        except Exception:
            continue
        # Text/Button 是**可点标签/按钮**；Pane 多半是容器外壳
        rank = (0 if c.element_info.control_type in ("Text", "Button") else 1,
                r.width() * r.height())
        if best is None or rank < best[0]:
            best = (rank, c)
    return best[1] if best else None


def locate_all(win, name: str, ctype: str | None = None):
    """返回所有同名且可见、在插件容器内的控件（**按 y 排序，左上优先**）。

    ⚑ 用法：同名元素有多个且**无法靠形状分辨**时，**逐个试 + 验收**，
      而不是猜哪个对（我连猜三次都错了）。
    """
    cr = container_rect(win)
    out = []
    for c in _controls(win):
        try:
            if (c.window_text() or "").strip() != name:
                continue
            if ctype and c.element_info.control_type != ctype:
                continue
            r = c.rectangle()
            if r.width() <= 0 or r.height() <= 0:
                continue
            if cr and not _overlaps(r, cr):
                continue
            try:
                if not c.is_visible():
                    continue
            except Exception:
                pass
        except Exception:
            continue
        out.append((r.top, r.left, c))
    out.sort()
    return [c for _, _, c in out]


def rect_of(win, name: str, ctype: str | None = None):
    """只要坐标 —— 调用方唯一该用的东西。"""
    c = locate(win, name, ctype)
    if c is None:
        return None
    try:
        return c.rectangle()
    except Exception:
        return None


# ── 第 2 层：颜色形状 ────────────────────────────────────────────────
def _is_blue(p) -> bool:
    r, g, b = p[0], p[1], p[2]
    if b < 130 or b - r < 60 or b - g < 30:
        return False
    return any(abs(r - t[0]) <= BLUE_TOL and abs(g - t[1]) <= BLUE_TOL
               and abs(b - t[2]) <= BLUE_TOL for t in THEME_BLUES)


def find_blue_groups(pane_img, min_run: int = 35, step: int = 3):
    """在插件区截图里找主题蓝矩形块，返回相对插件区的矩形列表。

    ⚠ 实测：整屏 800px 宽时命中 7 组，其中
      · ``x≈44``   贴左端 → 「全部商品分类」
      · ``x≈708``  贴右端 → 「搜索」
    """
    px = pane_img.load()
    w, h = pane_img.size
    groups: list[dict] = []

    def merge(a, b, y):
        for g in groups:
            if abs(g["x0"] - a) < 60 and abs(g["x1"] - b) < 60 and y - g["y1"] <= 12:
                g["x0"] = min(g["x0"], a)
                g["x1"] = max(g["x1"], b)
                g["y1"] = y
                return
        groups.append({"x0": a, "x1": b, "y0": y, "y1": y})

    for y in range(0, h, step):
        st = None
        for x in range(w):
            if _is_blue(px[x, y]):
                if st is None:
                    st = x
            else:
                if st is not None and x - st >= min_run:
                    merge(st, x, y)
                st = None
    return [g for g in groups if g["y1"] - g["y0"] >= 3]


def locate_shape(pane_img, which: str):
    """按形状取自绘控件。``which`` ∈ {category_btn, search_btn}。

    判据：**贴左端 = 分类按钮，贴右端 = 搜索按钮**（实测成立）。
    返回**相对插件区**的 ``(l, t, r, b)``，找不到返回 None。
    """
    gs = find_blue_groups(pane_img)
    if not gs:
        return None
    gs.sort(key=lambda g: g["x0"])
    if which == "category_btn":
        g = gs[0]
    elif which == "search_btn":
        g = gs[-1]
    else:
        return None
    return (g["x0"], g["y0"], g["x1"], g["y1"])


# ── 取证 ────────────────────────────────────────────────────────────
def focus_solidworks(hwnd: int) -> bool:
    """把 SolidWorks 置前（按 Alt 绕过 Win32 前台锁），回读确认。

    ⚠⚠ **2026-10-01 轮 62 修**：原实现在 `try` 里按下 `VK_MENU`、抬起也写在 `try` 内，
    而外层是 `except Exception: pass` ⇒ **`SetForegroundWindow` 或两个 `sleep` 任一抛异常
    （`KeyboardInterrupt` 也算），Alt 就永远不抬起** ⇒ **Alt 卡在按下态**。
    后果：菜单栏被激活、后续按键被吃掉 —— 与用户报告的「忽然 Ctrl/全选」同族的失效模式。
    ⇒ 现在抬起在 **`finally`** 里（且逐个 try，收尾失败不掩盖主异常）。
    """
    import win32api
    import win32con
    import win32gui
    for _ in range(3):
        if win32gui.GetForegroundWindow() == hwnd:
            return True
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        try:
            time.sleep(0.12)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
        except Exception:
            pass
        finally:
            # ⚠ 无论上面发生什么，**必须**抬起 Alt
            try:
                win32api.keybd_event(win32con.VK_MENU, 0,
                                     win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass
            time.sleep(0.35)
    return win32gui.GetForegroundWindow() == hwnd


def capture_front(path: str):
    """★ 置前 + **整屏**截图 —— 唯一能看到**浮窗/模态框**的取证方式。"""
    from PIL import ImageGrab
    img = ImageGrab.grab()
    img.save(path)
    return img


def capture_window(hwnd: int, path: str):
    """★ ``PrintWindow`` 抓窗口自身 —— **不受遮挡**，但**丢客户区外的浮窗**。

    ⚠ 64 位下 GDI 句柄是 64 位，ctypes 必须显式声明 restype/argtypes。
    """
    import ctypes
    from ctypes import wintypes
    from PIL import Image
    import win32gui
    import win32guiui

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    vp, ci = ctypes.c_void_p, ctypes.c_int
    gdi32.CreateCompatibleDC.restype = vp
    gdi32.CreateCompatibleDC.argtypes = [vp]
    gdi32.CreateCompatibleBitmap.restype = vp
    gdi32.CreateCompatibleBitmap.argtypes = [vp, ci, ci]
    gdi32.SelectObject.restype = vp
    gdi32.SelectObject.argtypes = [vp, vp]
    gdi32.DeleteObject.argtypes = [vp]
    gdi32.DeleteDC.argtypes = [vp]
    gdi32.GetDIBits.restype = ci
    gdi32.GetDIBits.argtypes = [vp, vp, ctypes.c_uint, ctypes.c_uint,
                                vp, vp, ctypes.c_uint]
    user32.GetWindowDC.restype = vp
    user32.GetWindowDC.argtypes = [vp]
    user32.ReleaseDC.argtypes = [vp, vp]
    user32.PrintWindow.restype = ctypes.c_bool
    user32.PrintWindow.argtypes = [vp, vp, ctypes.c_uint]

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", ctypes.c_long),
                    ("biHeight", ctypes.c_long), ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD),
                    ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD),
                    ("biXPelsPerMeter", ctypes.c_long),
                    ("biYPelsPerMeter", ctypes.c_long),
                    ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD)]

    class BI(ctypes.Structure):
        _fields_ = [("bmiHeader", BIH), ("bmiColors", wintypes.DWORD * 3)]

    l, t, r, b = win32gui.GetWindowRect(hwnd)
    w, h = r - l, b - t
    hdc = user32.GetWindowDC(hwnd)
    mfc = win32guiui.CreateDCFromHandle(hdc)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    old = gdi32.SelectObject(mem, bmp)
    ok = user32.PrintWindow(hwnd, mem, 2)          # 2 = PW_RENDERFULLCONTENT
    bi = BI()
    bi.bmiHeader.biSize = ctypes.sizeof(BIH)
    bi.bmiHeader.biWidth = w
    bi.bmiHeader.biHeight = -h
    bi.bmiHeader.biPlanes = 1
    bi.bmiHeader.biBitCount = 32
    bi.bmiHeader.biCompression = 0
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bi), 0)
    gdi32.SelectObject(mem, old)
    gdi32.DeleteObject(bmp.GetHandle())
    gdi32.DeleteDC(mem)
    win32guiui.DeleteDC(mfc)
    user32.ReleaseDC(hwnd, hdc)
    img = Image.frombuffer("RGB", (w, h), buf, "raw", "BGRX", 0, 1)
    if path:
        img.save(path)
    return img, bool(ok), w, h
