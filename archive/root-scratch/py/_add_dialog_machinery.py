import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")

NEW = '''

#: 官方 `swProcessType_e` 之类与「模态框」相关的常量**没有官方枚举** ⇒ 本模块只用两个
#: **Win32 公开常量**（不是魔法数）：
_WM_COMMAND = 0x0111        #: Win32 `WM_COMMAND`
_IDOK = 1                   #: Win32 标准「确定 / OK」按钮的命令 ID
_DIALOG_CLASS = "#32770"    #: Win32 **预定义对话框类**（官方常量 `WC_DIALOG`）


def solidworks_process_id(sw):
    """★ **从 COM 拿 SolidWorks 的进程 ID**（官方 `ISldWorks.GetProcessID()`）。

    ⚠⚠⚠ **为什么要有这个函数**（2026-10-01 轮 167）：此前**37 处**工具里**写死**
    `SW_PID = 20456` —— 那是**硬编码**：换机器、换会话、SolidWorks 重启后**全部失效**，
    而失效的表现是「**查不到残留模态框**」⇒ **一个静默失效的安全检查**。
    ★ 官方的 `ISldWorks.GetProcessID()` 直接给出真值 ⇒ **零硬编码**。
    （另有 `GetHWnd64()` / `get_HWnd()` 可取窗口句柄，本模块用不到。）
    """
    return int(call_com_member(sw, "GetProcessID"))


def _resolve_pid(target):
    """`target` 可以是 `ISldWorks`（**自动派生 PID**）或 `int`（显式 PID）。"""
    if isinstance(target, int):
        return target
    return solidworks_process_id(target)


def _dialog_handles(pid, *, only_visible=False):
    """枚举某 PID 的顶层窗口里 class 为 `#32770` 的那些（**Win32 `WC_DIALOG`**）。"""
    import ctypes
    import ctypes.wintypes as _w
    u = ctypes.windll.user32
    out: list = []
    total = [0]

    @ctypes.WINFUNCTYPE(ctypes.c_bool, _w.HWND, _w.LPARAM)
    def cb(h, _l):      # noqa: ANN001
        p = _w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value != pid:
            return True
        if only_visible and not u.IsWindowVisible(h):
            return True
        total[0] += 1
        cls = ctypes.create_unicode_buffer(128)
        u.GetClassNameW(h, cls, 128)
        if cls.value == _DIALOG_CLASS:
            out.append(h)
        return True

    u.EnumWindows(cb, 0)
    return out, total[0]


def dismiss_residual_dialogs(target, *, settle_seconds=0.0, poll_ms=200):
    """★ 把残留的**模态对话框**点掉 —— **不认按钮文本、不依赖可见性、零硬编码**。

    :param target: `ISldWorks`（**自动派生 PID**）或 `int` PID。
    :param settle_seconds: 在返回前**轮询**多久（⚠ **弹窗是异步弹出的**，见下）。
    :param poll_ms: 轮询间隔毫秒。
    :returns: `(dismissed, scanned)` —— 点掉了几个 / 扫到多少个顶层窗口。

    ⚠⚠⚠ **为什么要轮询**（2026-10-01 轮 167 的根因之一）：模态框**不是**在发调用的那一刻
    弹出来的 —— COM 调用返回后它**才**出现。原先各工具在收尾处**只查一次**
    ⇒ **查得太早** ⇒ 报「无残留」而屏幕上明明有一个（★ 那次会话就是这样**卡住的**）。

    ★ **怎么点掉**：给对话框发 `WM_COMMAND` + `IDOK`（Win32 标准命令）——
    **不看按钮叫什么、不按坐标** ⇒ 中英文界面、任何按钮布局都适用（用户明确要求**禁止硬编码**）。
    """
    import ctypes
    import time
    pid = _resolve_pid(target)
    dismissed = 0
    scanned = 0
    deadline = time.time() + max(0.0, float(settle_seconds))
    while True:
        handles, total = _dialog_handles(pid)
        scanned = total
        for h in handles:
            ctypes.windll.user32.PostMessageW(h, _WM_COMMAND, _IDOK, 0)
            dismissed += 1
        if time.time() >= deadline:
            break
        time.sleep(max(0.02, poll_ms / 1000.0))
    return dismissed, scanned
'''

if "def solidworks_process_id(" not in t:
    t = t.replace("def residual_dialogs(", NEW.strip() + "\n\n\ndef residual_dialogs(", 1)
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ok 已加 solidworks_process_id / dismiss_residual_dialogs（共享、零硬编码）")
else:
    print("  已有")
