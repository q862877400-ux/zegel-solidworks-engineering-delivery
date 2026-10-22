"""★ **常驻弹窗监视器**：发现弹窗就**主动把内容打印出来**（★ 那就是对 LLM 的"报信"），**不点**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/watch_dialogs.py
# 定位:   ★ 2026-10-02（轮 376）**用户立的形态**：检测器要**常驻 + 主动报信**，
#   ★★ 而**不是**让调用方去轮询它 —— ★ 调用方一去查，就又会卡住（那正是上一轮的病）。
# 官方依据: 不适用（★ 用 Win32 `EnumWindows` / `EnumChildWindows`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
# ★ 为什么这样设计（★ 用户原话的意思）：
#   ① **它主动报**：★ 每发现一个**新的**弹窗，就把「标题 + 全部控件文本」打一行
#      ⇒ ★ 那一行会经后台任务的输出**推给 LLM** ⇒ LLM 据此研判"什么触发了它" ✓
#   ② **它不点**：★ 报信之后由 LLM 决定怎么处置（★ 点 / 改代码防复发）——
#      ★ 与用户那条纪律一致：「先让 LLM 分析根因，然后再点，点完了还得改」。
#   ③ **它不卡**：★ 枚举是纯 `ctypes`（★ 实测 0.00 s），★ **不碰 COM、不截屏** ——
#      ★ 而`PrintWindow`/`BitBlt` 那类截图**留给"要看画面"时再做**（★ 那时另跑取证）。
#   ④ **调用方不查**：★ 它自己循环、自己打印 ⇒ ★ 调用方**只等通知**。

from __future__ import annotations

import argparse
import ctypes
import json
import sys
import time
from ctypes import wintypes as wt
from datetime import datetime

u = ctypes.windll.user32
_EnumWindows = u.EnumWindows
_EnumChildWindows = u.EnumChildWindows
_GetPid = u.GetWindowThreadProcessId
_GetCls = u.GetClassNameW
_GetTxt = u.GetWindowTextW
_GetLen = u.GetWindowTextLengthW
_IsVis = u.IsWindowVisible

_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)


def _text(hwnd: int) -> str:
    n = _GetLen(hwnd)
    if n <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(n + 2)
    _GetTxt(hwnd, buf, n + 2)
    return buf.value


def _class(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    _GetCls(hwnd, buf, 256)
    return buf.value


def _children(hwnd: int) -> list[dict]:
    """★ 抓该弹窗的**全部子控件文本** —— ★ 那是"它在问什么"（★ 纯 ctypes，★ 秒回）。"""
    rows: list[dict] = []

    def _cb(ch, _l):
        t = _text(ch).strip()
        if t:
            rows.append({"class": _class(ch), "text": t[:300]})
        return True

    _EnumChildWindows(hwnd, _PROC(_cb), 0)
    return rows


def snapshot(pid: int | None = None) -> list[dict]:
    """★ 一次快照：**可见的 `#32770`** 及其内容（★ 纯枚举，★ 不含截图 ⇒ 不会卡）。"""
    out: list[dict] = []

    def _cb(h, _l):
        p = wt.DWORD()
        _GetPid(h, ctypes.byref(p))
        if pid is not None and p.value != pid:
            return True
        if not _IsVis(h):
            return True
        if _class(h) != "#32770":
            return True
        out.append(
            {
                "hwnd": int(h),
                "pid": int(p.value),
                "title": _text(h)[:120],
                "controls": _children(h),
            }
        )
        return True

    _EnumWindows(_PROC(_cb), 0)
    return out


def _sw_pid() -> int | None:
    """★ SLDWORKS 的 PID（★ 用父窗口类名 `Afx:…` 判定，★ 不跑子进程）。"""
    best: int | None = None

    def _cb(h, _l):
        nonlocal best
        if not _IsVis(h):
            return True
        if _class(h).startswith("Afx:") and _text(h).startswith("SOLIDWORKS"):
            p = wt.DWORD()
            _GetPid(h, ctypes.byref(p))
            best = p.value
            return False
        return True

    _EnumWindows(_PROC(_cb), 0)
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=1.5, help="轮询间隔秒")
    ap.add_argument("--seconds", type=float, default=0.0, help="跑多久（0 = 一直跑）")
    ap.add_argument(
        "--all-reminders", action="store_true", help="连「非本进程」的弹窗也报"
    )
    args = ap.parse_args()

    pid = _sw_pid()
    print(
        "[watch] 启动 · SLDWORKS pid=%s · 间隔 %.1fs · **发现新弹窗即报信（不点）**"
        % (pid, args.interval),
        flush=True,
    )
    seen: set[tuple] = set()
    #: ★ 首轮把**已存在**的弹窗也报出来（★ 否则"启动前就有的"会被漏掉）
    deadline = (time.time() + args.seconds) if args.seconds > 0 else None
    first = True
    while True:
        try:
            items = snapshot(None if args.all_reminders else pid)
        except Exception as exc:  # noqa: BLE001
            print("[watch] 枚举异常：%s" % str(exc)[:120], flush=True)
            items = []
        for d in items:
            key = (d["hwnd"], d["title"], json.dumps(d["controls"], ensure_ascii=False))
            if key in seen:
                continue
            seen.add(key)
            stamp = datetime.now().strftime("%H:%M:%S")
            tag = "首轮已有" if first else "**新弹窗**"
            print("=" * 68, flush=True)
            print(
                "[watch %s] %s ⇒ PID=%s HWND=%s" % (stamp, tag, d["pid"], d["hwnd"]),
                flush=True,
            )
            print("[watch] 标题：%s" % d["title"], flush=True)
            for c in d["controls"]:
                print("[watch]   %-12s %s" % (c["class"], c["text"]), flush=True)
            print(
                "[watch] ⇒ **请研判根因**（什么触发了它），决定点掉并改代码防复发。",
                flush=True,
            )
            print("=" * 68, flush=True)
        first = False
        if deadline is not None and time.time() >= deadline:
            break
        time.sleep(max(0.2, args.interval))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
