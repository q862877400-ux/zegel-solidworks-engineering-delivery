r"""SolidWorks 窗口的 GUI 自动化底座：置顶、控件树枚举、不受遮挡的截图。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本模块的 API 形状沿用上游 ``sw_connect.get_com_member`` 的约定
#         （不裸写 getattr(obj, name)()，成员名一律走索引校验）
# 定位:   给「点插件 / GUI 流程测试」提供**可靠**的窗口操作底座。
#
# ⚑⚑ 为什么需要这个模块（不是「截图看看」那么简单的活）
# -----------------------------------------------------------
# 2026-09-30 实测踩到的坑：直接 ``ImageGrab.grab(bbox=win_rect)``
# **抓到的是屏幕上压在上面的别的窗口**（当时抓到的是浏览器），
# 因为 bbox 是**屏幕坐标**，被遮挡时抓到的就是遮挡物。
# ⇒ 截图必须用 ``PrintWindow``（抓窗口自身缓冲），并**校验返回值**。
#
# ⚑ 三条可靠性要求（缺一条就会误操作）
# --------------------------------------
#   ① 目标窗口必须**确认标题**再操作 —— 同名/相似窗口太多
#   ② 必须**置顶**后才允许点击 —— 否则点下去的是别人
#   ③ 截图/操作后要**回读确认**，不能假定成功
#
# 覆盖:   后续同级定义
# ⚠ 本模块只做窗口层操作；**不创建模型、不发建模调用**。
#   调用方要建文档/建模，须自己显式调用（见 A2 边界说明）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from typing import Any

__all__ = [
    "TITLE_PREFIX", "find_solidworks_window", "focus_window",
    "dump_controls", "capture_window", "wait_for_window",
]

#: SolidWorks 主窗口标题**必须以**该串开头。
#: ⚠⚑ 早先写成「包含」，结果抓到 Edge —— 它的标题里恰好含
#:    「SolidWorks Automation Skil - DSH 本地构建」=> 误判。
#:    教训：窗口匹配要**锚定开头**，不是子串包含。
TITLE_PREFIX = "SOLIDWORKS"


def find_solidworks_window() -> tuple[int, str, tuple[int, int, int, int]] | None:
    """找 SolidWorks 主窗口。返回 ``(hwnd, title, rect)``；**没有就返回 None**。

    ⚠ 不猜、不返回近似窗口 —— 找不到就是找不到，调用方自己决定要不要中止。
    """
    import win32gui

    hits: list[tuple[int, str, tuple[int, int, int, int]]] = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if t and t.upper().startswith(TITLE_PREFIX):
                hits.append((h, t, win32gui.GetWindowRect(h)))

    win32gui.EnumWindows(cb, None)
    if not hits:
        return None
    # 取面积最大的那个（主窗口，而非某个浮窗/对话框）
    hits.sort(key=lambda x: (x[2][2] - x[2][0]) * (x[2][3] - x[2][1]), reverse=True)
    return hits[0]


def wait_for_window(timeout: float = 60.0, poll: float = 1.0) -> tuple[int, str, tuple]:
    """等 SolidWorks 主窗口出现。⚠ **超时抛异常**，不返回 None 当成功。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        w = find_solidworks_window()
        if w:
            return w
        time.sleep(poll)
    raise TimeoutError("等不到 SolidWorks 主窗口（%.0f 秒内没出现）" % timeout)


def focus_window(hwnd: int, retries: int = 4) -> bool:
    """把窗口置顶并激活。⚠ 返回**是否确认成功**，不假定。

    ⚠ Win32 的 ``SetForegroundWindow`` 常被系统拒绝（前台锁），
    所以这里用「先 AttachThreadInput 再置顶」的常规手法，并**逐次回读**验证。
    """
    import win32con
    import win32gui
    import win32process

    for i in range(retries):
        try:
            if win32gui.GetForegroundWindow() == hwnd:
                return True
            cur = win32gui.GetForegroundWindow()
            t1 = win32process.GetWindowThreadProcessId(cur)[0] if cur else 0
            t2 = win32process.GetWindowThreadProcessId(hwnd)[0]
            if t1 and t2 and t1 != t2:
                import ctypes
                ctypes.windll.user32.AttachThreadInput(t1, t2, True)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.4)
            if win32gui.GetForegroundWindow() == hwnd:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return win32gui.GetForegroundWindow() == hwnd


def dump_controls(hwnd: int, max_depth: int = 3) -> list[dict[str, Any]]:
    """枚举控件树（带语义名与坐标）。**只读，不点击。**

    返回每项 ``{type, name, rect}``。⚠ 深度受限 —— SolidWorks 的 UI 树很深，
    全展开会产出上万个节点。
    """
    import uiautomation as auto

    root = auto.ControlFromHandle(hwnd)
    out: list[dict[str, Any]] = []

    def walk(node, depth):
        if depth > max_depth:
            return
        for c in node.GetChildren():
            try:
                out.append({
                    "type": c.ControlTypeName,
                    "name": c.Name,
                    "rect": c.BoundingRectangle,
                    "depth": depth,
                })
            except Exception:
                continue
            walk(c, depth + 1)

    walk(root, 0)
    return out


def capture_window(hwnd: int, path: Any = None) -> Any:
    """用 ``PrintWindow`` 抓**窗口自身**内容，**不受遮挡影响**。

    ⚠ 这一步正是为了避开「bbox 截图抓到遮挡物」的坑。
    ⚠ 返回 PIL Image；``path`` 给了就顺手存盘。
    """
    from PIL import Image

    hwndDC, mfcDC, saveDC, bmp, w, h = _dc_for(hwnd)
    # 2 = PW_RENDERFULLCONTENT，能抓到 DWM 合成的现代界面
    ok = ctypes.windll.user32.PrintWindow(hwnd, saveDC, 2)
    info = bmp.GetInfo()
    bits = bmp.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bits,
                           "raw", "BGRX", 0, 1)
    import win32gui
    import win32ui
    win32ui.DeleteObject(bmp.GetHandle())
    win32ui.DeleteDC(saveDC)
    win32ui.DeleteDC(mfcDC)
    win32gui.ReleaseDC(hwnd, hwndDC)
    if not ok:
        # ⚠ 明确告知：拿到的可能是黑图，**不要当成成功**
        print("[warn] PrintWindow 返回 0，内容可能不完整", file=sys.stderr)
    if path:
        img.save(str(path))
    return img


# ── win32 句柄小工具（内联，保持模块只有一个公开面）──────────────────
def _dc_for(hwnd: int):
    """建 PrintWindow 需要的四个 GDI 句柄，返回 (mfcDC, saveDC, bmp, w, h)。"""
    import win32gui
    import win32ui
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = win32ui.CreateCompatibleDC(mfcDC)
    bmp = win32ui.CreateCompatibleBitmap(mfcDC, w, h)
    win32ui.SelectObject(saveDC, bmp)
    return hwndDC, mfcDC, saveDC, bmp, w, h
