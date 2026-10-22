r"""嘉立创 FA 选型插件的 GUI 自动化 —— 实测跑通全链路（2026-09-30）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机已安装并实测驱动）
# 定位:   用脚本驱动插件完成「搜索型号 -> 选参数 -> 生成预览」，
#         产出真实 .SLDPRT 到插件 BuildFile 目录。
#
# ⚑ 已实测跑通的完整链路
# ----------------------------------------
#   找窗口(按进程名) -> 拖动面板刷新 -> 点插件标签(第 9 个 JLC)
#   -> 颜色扫描量搜索框 -> 输入型号 -> 回车 -> 点结果卡
#   -> 等参数页加载 -> 点「生成预览」 -> **文件落盘**
#   实测产出：经济型法兰型直线轴承 引导式 双衬(E-LMHP13LUU).SLDPRT  133.3 KB
#   cadmpeg 复核：format: sldprt (detected high)，entries: 61
#
# ⚑⚑ 本轮踩的七个坑（详见各函数注释）
# --------------------------------------
# 1. 拖动幅度过大会把 SolidWorks 拖到最小化（rect 变 -32000）→ ensure_window() 断言
# 2. 不能用「标签列坐标」当搜索框坐标（实测偏 97 像素）→ 颜色扫描量白底矩形
# 3. 窗口标题不能用来过滤（浏览器标签页标题也含 SolidWorks）→ 按进程名 sldworks.exe
# 4. pywin32 的 win32ui 不含 GDI 绘图函数 → 截图走 ctypes（见 sw_capture.py）
# 5. ctypes 不声明 restype/argtypes 报 "int too long to convert"（64 位句柄）
# 6. 拖动不能代替滚轮（WinForms Panel 不响应拖动滚动）→ MOUSEEVENTF_WHEEL
# 7. 参数太复杂的型号跑不通（带【去填写】的空规格段填不满时按钮禁用）
#
# ⚠ 已知不足（未解决，勿当已支持）
# ----------------------------------
# · 带【去填写】空规格段的型号**跑不通**（插件面板可能比窗口宽，右侧在屏幕外）
# · 每个坐标都要重新量（布局会变），不能硬编码
# · 插件内部子控件读不到，只能按坐标点
#
# 覆盖:   后续同级定义
# ⚠ 本模块会**驱动 GUI 并操作 SolidWorks**，调用方须先读上方「已知不足」。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, Path(__file__).resolve().parents[1])

import uiautomation as auto
import win32api
import win32con
import win32gui

import shot

SHOTS = Path(Path(__file__).resolve().parents[1] / "shots")
SHOTS.mkdir(exist_ok=True)
BF = Path(
    "D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
    "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile"
)
STATE = Path(Path(__file__).resolve().parents[1] / "bf_state.json")


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

            out = subprocess.run(
                ["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
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
            "窗口状态异常 rect=%s 尺寸=%dx%d —— 拒绝操作（可能又被最小化/移出屏幕）"
            % (r, w, h)
        )
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
        win32api.SetCursorPos(
            (int(x1 + (x2 - x1) * i / steps), int(y1 + (y2 - y1) * i / steps))
        )
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
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, clicks * 120, 0)
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
