# -*- coding: utf-8 -*-
"""嘉立创 FA 插件 GUI 自动化 —— 完整选型→生成流程。

⚑ 关键前置（用户口述，2026-09-30）
--------------------------------------
**从 0 启动后点开插件，右侧菜单会卡住、内容不显示，拖动一下面板才正常。**
⇒ 每步操作前先 ``refresh_pane()``：按住窗格边缘拖一下再拖回。

⚑ 坐标基准
----------
控件坐标（uiautomation 给的）与鼠标坐标**同一物理像素空间**，但窗口在
(0,0,2048,1152)，故可直接用。⚠ 每次操作前重新取一次标签列坐标 ——
SolidWorks 布局会变，硬编码坐标已经错过一次。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")

import win32api
import win32con
import win32gui
import uiautomation as auto

import shot

SHOTS = Path(r"D:\AI\SW\shots")
SHOTS.mkdir(exist_ok=True)
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
STATE = Path(r"D:\AI\SW\bf_state.json")


def log(msg: str) -> None:
    print("  %s" % msg, flush=True)


def sw_window() -> int:
    """按**进程名**找 SolidWorks 主窗口（不信标题 —— 浏览器标签页会冒充）。"""
    import win32process
    hits = []

    def cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return
        t = win32gui.GetWindowText(h)
        if not t:
            return
        try:
            pid = win32process.GetWindowThreadProcessId(h)[1]
            import subprocess
            out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid,
                                  "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True,
                                 encoding="utf-8", errors="replace")
            name = out.stdout.split(",")[0].strip('"')
        except Exception:
            name = ""
        if name.lower().endswith("sldworks.exe"):
            hits.append((h, t, win32gui.GetWindowRect(h)))

    win32gui.EnumWindows(cb, None)
    if not hits:
        raise RuntimeError("找不到 SolidWorks 主窗口（按进程名 sldworks.exe 过滤）")
    hits.sort(key=lambda x: (x[2][2] - x[2][0]) * (x[2][3] - x[2][1]), reverse=True)
    return hits[0][0]




def ensure_window(hwnd: int) -> tuple:
    """★ 护栏：每次操作前确认窗口**没被最小化、尺寸正常**。

    ⚠⚑ 加这条的原因（2026-09-30 实测踩坑）：
    早先 refresh_pane() 拖动幅度过大，**把 SolidWorks 拖到最小化**，
    窗口 rect 变成 (-32000,-32000,-31801,-31966)（Win32 最小化的固定坐标），
    之后所有点击都落在屏幕外 —— 表现为「点搜索框没反应」，
    实则是窗口根本不在屏幕上。**症状离原因很远**，只能靠状态断言拦住。
    """
    import win32con
    if win32gui.IsIconic(hwnd):
        log("  [护栏] 窗口已最小化 -> 恢复")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(1.2)
    r = win32gui.GetWindowRect(hwnd)
    w, h = r[2] - r[0], r[3] - r[1]
    if w < 600 or h < 400 or r[0] < -100:
        raise RuntimeError(
            "窗口状态异常 rect=%s 尺寸=%dx%d —— 拒绝操作（可能又被最小化/移出屏幕）" % (r, w, h))
    return r


def click(x: int, y: int, pause: float = 0.35, dbl: bool = False) -> None:
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    if dbl:
        time.sleep(0.06)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.06)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def drag(x1: int, y1: int, x2: int, y2: int, steps: int = 12) -> None:
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.15)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.03)
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.5)




def wheel(x: int, y: int, clicks: int = -3, pause: float = 0.4) -> None:
    """真滚轮事件（MOUSEEVENTF_WHEEL）。

    ⚠⚑ **不能用拖动代替滚轮**（2026-09-30 实测）：拖动只是移动光标，
    WinForms 的 Panel 不会滚动 —— 截图字节数完全一样，内容零变化。
    """
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.2)
    for _ in range(abs(clicks)):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0,
                             clicks * 120, 0)
        time.sleep(0.12)
    time.sleep(pause)


def find_node(root, name: str, depth: int = 0, maxd: int = 10):
    """按 Name 精确/包含找节点。找不到返回 None（不猜）。"""
    if depth > maxd:
        return None
    for c in root.GetChildren():
        try:
            if c.Name == name:
                return c
        except Exception:
            continue
        r = find_node(c, name, depth + 1, maxd)
        if r is not None:
            return r
    return None


def tab_column(hwnd: int):
    root = auto.ControlFromHandle(hwnd)
    n = find_node(root, "Task Pane Tabs Wnd")
    return root, (n.BoundingRectangle if n is not None else None)


def refresh_pane(hwnd: int, rect) -> None:
    """★ 用户口述的关键动作：拖动右侧面板，让卡住的内容刷新。"""
    if rect is None:
        return
    # ⚠⚑ 幅度必须小：早先拖 120px 把整个 SolidWorks 窗口拖到最小化了。
    #   只在**标签列左边缘**做 30px 往返，不碰标题栏、不跨出面板。
    r = rect
    x_edge = max(r.left - 2, 1)
    y_mid = r.top + 60
    drag(x_edge, y_mid, x_edge - 30, y_mid, steps=8)
    drag(x_edge - 30, y_mid, x_edge, y_mid, steps=8)
    log("  已拖动面板（30px 小幅度，刷新卡住的内容）")


def snap(name: str, box=None, scale: int = 1):
    hwnd = sw_window()
    img, ok, w, h = shot.capture(hwnd, str(SHOTS / f"{name}.png"))
    if box:
        img = img.crop(box)
    if scale > 1:
        img = img.resize((img.width * scale, img.height * scale), scale)
    p = SHOTS / f"{name}_z.png"
    img.save(p)
    log("  截图 -> %s (%s)" % (p.name, img.size))
    return p
