r"""@brief 假模态框：造一个 **类名 `#32770`** 的窗口并停住（给判据当**靶子**）。

## 为什么要有这个文件
`067`/`068` 把「查残留模态框」改成了**不过滤可见性**并**返回扫到的窗口总数**，
但当时**只证明了"在扫"**（窗口数 1 → 49）—— **没有证明它真能抓到一个模态框**。
⇒ ★ 本文件就是那个靶子：**造一个真的 `#32770`**，让判据去抓。

## ⚠ 安全性
* **不连 COM、不碰 SolidWorks**；
* 只在**本进程**里建一个窗口，`stdout` 打印自己的 PID，然后 `sleep` 等被 kill；
* ★ 窗口**故意不置 `WS_VISIBLE`** —— 这正好复现旧判据的失效模式
  （`IsWindowVisible` 过滤会**漏掉**它）。

## 用法
```
python tools/fake_modal_dialog.py            # 打印 PID 后停住（Ctrl-C / kill 结束）
python tests/test_modal_dialogs_can_fire.py  # 测试会自己起/杀它
```

# ── 来源 ──
# 仓库:   本项目自身（测试夹具）
# 文件:   tools/fake_modal_dialog.py
# 定位:   给 Spec Kit `069` 提供「判据能不能真的响」的靶子（事实 62 的精神）。
# 官方依据: Win32 预定义类 `#32770`（对话框）；`CreateWindowExW` / `GetMessageW`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

u = ctypes.windll.user32
u.CreateWindowExW.restype = w.HWND
u.CreateWindowExW.argtypes = [
    w.DWORD,
    w.LPCWSTR,
    w.LPCWSTR,
    w.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    w.HWND,
    w.HMENU,
    w.HINSTANCE,
    w.LPVOID,
]

#: 预定义对话框类（官方常量 `WC_DIALOG` 就是字符串 "#32770"）。
DIALOG_CLASS = "#32770"
#: ⚠ **故意不置 `WS_VISIBLE`** —— 复现旧判据的失效模式。
#: ⚠⚠ **第一版这里写错了**：`0x10000000` **就是 `WS_VISIBLE`**（不是 `WS_OVERLAPPED`，
#:    后者是 `0x00000000`）⇒ 结果窗口**可见**（实测 `visible=1`）⇒ 对照不成立。
#: ⇒ 只用 `WS_POPUP`。
WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000  #: 本夹具**故意不置**它
STYLE = WS_POPUP


def main() -> int:
    hwnd = u.CreateWindowExW(
        0,
        DIALOG_CLASS,
        "MCP 假模态框（测试夹具）",
        STYLE,
        0,
        0,
        320,
        200,
        None,
        None,
        None,
        None,
    )
    if not hwnd:
        print("FAIL: CreateWindowExW 建不出 #32770（err=%d）" % ctypes.get_last_error())
        return 1
    print(
        "PID=%d HWND=%d class=%s visible=%d"
        % (
            ctypes.windll.kernel32.GetCurrentProcessId(),
            hwnd,
            DIALOG_CLASS,
            u.IsWindowVisible(hwnd),
        )
    )
    sys.stdout.flush()
    #: 停住等人来抓（测试会 kill 掉本进程）
    msg = w.MSG()
    deadline = time.time() + 120
    while time.time() < deadline:
        if u.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            u.TranslateMessage(ctypes.byref(msg))
            u.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.05)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
