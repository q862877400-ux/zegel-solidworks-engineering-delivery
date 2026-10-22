"""★ SolidWorks 现在**是不是正忙着**（纯 ctypes 读窗口，**不碰 COM**）—— 忙就别发新调用。

（★ 根因处置：事实 526/527 —— SW 忙时下发 COM 调用会把整条链卡死，且**杀子进程也不一定救回来**）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks Simulicon 官方手册（本机解包 `C:\cworks_manual\`）
# 文件:   `D:\AI\SW\docs\known-facts.md` 事实 296（★ **SolidWorks 家族的进程/窗口判据**
# ）·
#         事实 526（★ **SW 忙时隔离子进程会卡在跨进程 COM 里**）·
#         `tools/sw_guard.py`（★ 弹窗哨兵用的是**同一族**的窗口枚举，但那是"发现弹窗"、
#         本模块是"发现**忙**"—— ★ 两件事：★ 弹窗**等**你点，★ 忙是**在算**、点也没用）✓
# 定位:   ★★★ **为什么需要它**（★ 2026-10-04 真机两连撞）：
#     `tools/probe_analysis_run_long_timeout.py` **两次**卡在 SolidWorks 里：
#       · 第一次（非隔离调用）⇒ SW 被留在计算里，主进程杀掉它**也不停**；
#       · 第二次（**隔离子进程**、timeout=180 s）⇒ 子进程 CPU **0.10 s**、`Responding`、
#         ★ **卡在跨进程 COM 调用里**；★ `subprocess.run` 的超时**没杀掉它**；
#         ★★ 而**杀掉子进程后父进程仍未恢复** ✓
#     ⇒ ★★★ **正解是把"忙"当**前置**判掉**：★ **不发调用 ⇒ 就没有可卡住的调用** ✓
#   ★ 判据（★ 两条，★ **都不认类名**，与事实 296 同口径）：
#     ① ★ **进度状态窗** `OperationStatusWindow`（★ 真机实录标题 `进度` ——
#        ★ 它在"建立刚度矩阵"与"网格化"时都会出现）⇒ 忙；
#     ② ★ **不响应鬼窗** `swPM_GhostWindow` 且标题含 `Not Responding` / `无响应` ⇒ 忙 ✓
# ⚠ ★ **它只判"忙"，不判"弹窗"**：★ 弹窗由 `tools/sw_guard.py` 的哨兵管（那是**等你点**
# 的东西）✓
#   ⚠ ★ **只读、只枚举**：不点、不关、不发消息、不碰 COM；★ 读不到任何窗口 ⇒ 回**不忙**
#     （★ 不因为读不到就误报"忙" —— ★ 那会把正常工作全挡住）✓
#   许可:   本仓库 MIT。★ 只用标准库 `ctypes`。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from typing import Any

__all__ = [
    "solidworks_busy",
    "solidworks_stuck",
    "solver_processes",
    "wait_until_idle",
    "BUSY_BLOCKED_CODE",
]

#: ★ 调用方据此判"被忙挡住了"（★ 与"调用失败"分开 —— ★ 事实 517：别把两类失败混成一种）
BUSY_BLOCKED_CODE = "SOLIDWORKS_BUSY"

#: ★★ **"真在算"的标志进程**（★ 判"卡住"要用它做反证）——
#:   ★ 出处：本机 `…\SOLIDWORKS\Simulation\` 目录实测的文件名（★ 网格器 + 求解内核家族）：
#: `cwbcbfmesh.exe`(★ 实测吃过 38.5 GB 的那个) · `cwmeshproc.exe` · `cwanalysisproc.exe`
#:  ·
#:     `star.exe`/`dstar.exe`/`nstar.exe`/`hstar.exe`(★ COSMOS/M 系求解内核命名) ·
#:     `fat.exe`(疲劳) · `stres.exe` · `ghs3d.exe` ✓
#:   ★★★ **为什么要它**：★ "SW 不响应"**同时**出现在**正常的长求解**与**真卡住**两种情形里
#:     ⇒ ★ **单看鬼窗会把正常求解也杀掉**（★ 那是事实 297 明确禁止的："点掉进度窗 = 中断一个
#:     正在跑的正常任务"）⇒ ★★ **必须加反证**：★ **真有求解进程在 ⇒ 是在算**；
#:     ★ **没有求解进程而有鬼窗 ⇒ 是卡住** ✓（★ 两次真机卡死的现场都是后者：
#:     子进程 CPU **0.10 s**、`cwbcbfmesh` **不存在**、SW 却在烧 1 核）
SOLVER_PROCESS_NAMES = (
    "cwbcbfmesh.exe",
    "cwmeshproc.exe",
    "cwanalysisproc.exe",
    "star.exe",
    "dstar.exe",
    "nstar.exe",
    "hstar.exe",
    "fat.exe",
    "stres.exe",
    "ghs3d.exe",
)

#: ★ 忙的判据（★ 与类名无关的"业务判据"）
_BUSY_CLASSES = ("OperationStatusWindow",)
_BUSY_TITLE_MARKERS = ("not responding", "无响应", "没有响应")

#: ★ SolidWorks **家族**的 exe 路径特征（★ 照事实 296 的两条；★ 不看类名）
_FAMILY_PATH_MARKERS = ("solidworks corp", "solidworks shared")
_FAMILY_EXE_PREFIXES = ("sld", "sw", "cw")  # ★ `cwbcbfmesh` / `cwmeshproc` 也在这族里
#: ★★ **应用本体**的 exe 名 —— ★ 只有它算"SolidWorks 在跑"
#:   ⚠ ★ 只读实测教训：★ 用"**任意家族窗口**"当在场判据**太宽** ——
#:     本机当时 `sldBgDwld.exe`（**安装管理器的后台下载器**）就有 5 个窗口
#:     ⇒ ★ 于是那个**孤儿 `进度` 窗**（属 Explorer、SW 早已关掉）仍被判成"忙" ⇒ **误报** ✓
_APP_EXE = "sldworks.exe"


def _enum_windows() -> list[dict[str, Any]]:
    """★ 枚举**所有有标题的顶层窗口** ⇒ `[{pid, title, cls, exe}]`（★ 纯 ctypes、无 COM）。

    ⚠ ★ 取 exe 全路径要用 `OpenProcess + QueryFullProcessImageNameW`；
    ★ 取不到（权限/已退出）就留空 —— ★ 那时按**类名证据**判（见 `solidworks_busy`）✓
    """
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    out: list[dict[str, Any]] = []

    proc_query = 0x1000  # PROCESS_QUERY_LIMITED_INFORMATION
    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def _cb(hwnd, _lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        n = user32.GetWindowTextLengthW(hwnd)
        title = ""
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            title = buf.value
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        exe = ""
        h = kernel32.OpenProcess(proc_query, False, pid.value)
        if h:
            try:
                path_buf = ctypes.create_unicode_buffer(1024)
                size = wintypes.DWORD(len(path_buf))
                if kernel32.QueryFullProcessImageNameW(
                    h, 0, path_buf, ctypes.byref(size)
                ):
                    exe = path_buf.value
            finally:
                kernel32.CloseHandle(h)
        if title or cls_buf.value:
            out.append(
                {
                    "pid": int(pid.value),
                    "title": title,
                    "cls": cls_buf.value,
                    "exe": exe,
                }
            )
        return True

    user32.EnumWindows(cb(_cb), 0)
    return out


def _is_family(exe: str) -> bool:
    """★ 这条窗口属于 **SolidWorks 家族**吗（★ 按 exe 路径，★ 不按类名）。"""
    low = (exe or "").lower().replace("/", "\\")
    if not low:
        return False
    if any(m in low for m in _FAMILY_PATH_MARKERS):
        return True
    name = low.rsplit("\\", 1)[-1]
    return name.endswith(".exe") and name.startswith(_FAMILY_EXE_PREFIXES)


def _is_app(exe: str) -> bool:
    """★ 这是 **SolidWorks 应用本体**（`SLDWORKS.exe`）的窗口吗 —— ★ "在跑"只认它。"""
    return (exe or "").lower().replace("/", "\\").rsplit("\\", 1)[-1] == _APP_EXE


def solver_processes() -> list[str]:
    """★ 当前活着的**求解/网格内核进程名**（小写）—— ★ 判"**真在算**"的反证。

    ★ 出处见 `SOLVER_PROCESS_NAMES` 上方的注（★ 本机 `…\\SOLIDWORKS\\Simulation\\` 实测的文件名）。
    ★ 实现：`CreateToolhelp32Snapshot` + `Process32FirstW/NextW`（★ **纯 ctypes、不启子进程**）✓
    ⚠ 取不到快照 ⇒ 回**空列表**（★ 那时 `solidworks_stuck` 会偏保守，见它的注）。
    """
    th32cs_snapprocess = 0x00000002
    max_path = 260
    k32 = ctypes.windll.kernel32

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_void_p),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", wintypes.WCHAR * max_path),
        ]

    names: list[str] = []
    snap = k32.CreateToolhelp32Snapshot(th32cs_snapprocess, 0)
    if snap in (None, -1, 0xFFFFFFFF):
        return names
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(entry))
        while ok:
            names.append(str(entry.szExeFile).lower())
            ok = k32.Process32NextW(snap, ctypes.byref(entry))
    except Exception:  # noqa: BLE001
        pass
    finally:
        k32.CloseHandle(snap)
    return names


def solidworks_stuck(
    windows: list[dict[str, Any]] | None = None, processes: list[str] | None = None
) -> dict[str, Any]:
    """★★★ **"SW 不响应"到底是"真在算"还是"真卡住"** ⇒ `{stuck, busy, reasons, solver_alive}`。

    ★★★★ 为什么必须分开（★ 这是本模块存在的第二半理由）：
      ★ "不响应"**同时**出现在**正常的长求解**与**真卡住**两种情形里 ⇒
      ★ 单看鬼窗就动手 = **误杀一个正在跑的正常任务**（★ 事实 297 明令禁止：
      "点掉进度窗 = 中断一个正在跑的正常任务"）✓
    ★ 判据（★ **反证法**，依据是真机实测到的两种现场）：
      · ★ **有求解/网格内核进程**（`cwbcbfmesh.exe` 等）⇒ **在算** ⇒ `stuck=False`
        （★ 真机实录：正常求解时 `cwbcbfmesh.exe` 在跑、吃过 38.5 GB）✓
      · ★★ **有"不响应"却没有任何内核进程** ⇒ **卡住** ⇒ `stuck=True`
        （★ 两次真机卡死的现场**都是这一种**：子进程 CPU **0.10 s**、`cwbcbfmesh` **不存在**、
        而 SW 在烧 1 核、且**一个弹窗都没有**）✓
    ⚠ ★ **保守侧**：★ 取不到进程列表（空）时，只在"**确实看到不响应**"的前提下判卡住 ——
      ★ 那正是我们要抓的那一种；★ 而"列表为空 + 不响应"在真求解时**几乎不会同时出现**
      （★ 真求解必有内核进程）✓

    :returns: `{stuck, busy, solver_alive, solver_names, reasons, evidence}`
    """
    b = solidworks_busy(windows)
    procs = (
        solver_processes() if processes is None else [str(p).lower() for p in processes]
    )
    alive = sorted({p for p in procs if p in SOLVER_PROCESS_NAMES})
    out: dict[str, Any] = {
        "busy": bool(b.get("busy")),
        "solver_alive": bool(alive),
        "solver_names": alive,
        "stuck": False,
        "reasons": [],
        "evidence": b.get("evidence") or [],
        "★": "★ 有内核进程 ⇒ **在算**；★ 不响应且**无**内核进程 ⇒ **卡住**",
    }
    if not b.get("busy"):
        return out
    if alive:
        out["reasons"].append(
            "★ 有求解/网格内核进程在跑（%s）⇒ **判定为「真在算」**，"
            "★ 不当作卡住（★ 免得误杀正常求解）" % ", ".join(alive)
        )
        return out
    out["stuck"] = True
    out["reasons"] = list(b.get("reasons") or []) + [
        "★★ SolidWorks 不响应，**且没有任何求解/网格内核进程**（%s 一个都不在）"
        "⇒ **判定为「卡住」**（★ 真机两次现场都是这一种）"
        % "/".join(SOLVER_PROCESS_NAMES[:4])
    ]
    return out


def solidworks_busy(windows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """★ **SolidWorks 现在是不是正忙** ⇒ `{busy, reasons, evidence}`。

    :param windows: ★ **可注入**的窗口列表（★ 测试用 —— 免得测试依赖真机）；
        ★ `None` ⇒ 现枚举（`_enum_windows`）。
    :returns: `{busy: bool, reasons: [str], evidence: [{pid, cls, title}]}`
        ★ `busy=True` ⇒ **调用方不应再发新的 COM 调用**（★ 发了就可能卡住、且不一定救得回来）。
    ★★ **前置：先要求"SolidWorks 家族窗口在"** —— ★ 只读实测抓到过一个**孤儿** `进度` 窗：
       ★ SolidWorks 已经关掉、而那个 `OperationStatusWindow`（**属 Explorer，pid 14488**）还在
       ⇒ ★ 若不要求家族在，判据会**永远回"忙"**、把正常工作**全挡住**（★ 那比不判更坏）✓
    """
    wins = _enum_windows() if windows is None else windows
    reasons: list[str] = []
    evidence: list[dict[str, Any]] = []
    stray: list[dict[str, Any]] = []
    #: ★ **在场判据 = 应用本体（`SLDWORKS.exe`）有窗口** —— ★ 不是"任意家族进程"（见 `_A
    #: PP_EXE` 的注）
    app_windows = [w for w in wins if _is_app(str(w.get("exe") or ""))]
    if not app_windows:
        #: ★ 本体不在 ⇒ 无论看到什么"进度"窗都**不判忙**；★ 但**如实留下证据**（★ 那是孤
        #: 儿窗）
        for w in wins:
            if str(w.get("cls") or "") in _BUSY_CLASSES:
                stray.append(
                    {
                        "pid": w.get("pid"),
                        "cls": w.get("cls"),
                        "title": str(w.get("title") or "")[:60],
                        "exe": str(w.get("exe") or "")[:80],
                    }
                )
        return {
            "busy": False,
            "reasons": [],
            "evidence": [],
            "app_windows": 0,
            "windows_scanned": len(wins),
            "★_孤儿进度窗": stray,
            "★": "★ SolidWorks 应用本体不在 ⇒ 不判忙（★ 孤儿 `进度` 窗归 Explorer，不作数）",
        }
    for w in wins:
        cls = str(w.get("cls") or "")
        title = str(w.get("title") or "")
        exe = str(w.get("exe") or "")
        low_title = title.lower()
        #: ① 进度状态窗 —— ★★ **必须可归属给 SolidWorks 家族**才作数。
        #:   ★★★ 真机教训（2026-10-04，第二次真机试跑当场抓到）：★ 本机有一个**遗留**的
        #:     `OperationStatusWindow`（标题 `进度`、**属 Explorer pid 14488**），
        #:     ★ 它**从 9:53 一直挂到 12:47**、连 SolidWorks 关掉之后都还在
        #: ⇒ ★ 若只认类名，判据会**一直回"忙"**、把正常工作**全挡住**（★ 实测：探针三次
        #: 读数
        #:     全被 `SOLIDWORKS_BUSY` 拒掉）✓
        #:   ★ 而**真的要报忙**时，现场还有 `swPM_GhostWindow`「Not Responding」（见 ②）——
        #:     那才是**可归属**的信号 ✓
        if cls in _BUSY_CLASSES:
            if _is_family(exe):
                reasons.append(
                    "有**家族进程的进度状态窗**（%s：%r）⇒ SolidWorks 正在跑一项操作"
                    % (cls, title[:40])
                )
                evidence.append(
                    {
                        "pid": w.get("pid"),
                        "cls": cls,
                        "title": title[:80],
                        "exe": exe.rsplit("\\", 1)[-1],
                    }
                )
            else:
                stray.append(
                    {
                        "pid": w.get("pid"),
                        "cls": cls,
                        "title": title[:60],
                        "exe": exe[:80],
                        "why": "★ 进度窗**不属 SolidWorks 家族**（多为 shell/残留）⇒ 不作数",
                    }
                )
            continue
        #: ② 不响应鬼窗（★ 主线程被占住时 Windows 挂的那个壳 —— ★ **可归属**的那条主信号
        #: ）
        if "ghostwindow" in cls.lower() and any(
            m in low_title for m in _BUSY_TITLE_MARKERS
        ):
            reasons.append("有**不响应鬼窗**（%r）⇒ 主线程被占住" % title[:40])
            evidence.append({"pid": w.get("pid"), "cls": cls, "title": title[:80]})
            continue
        #: ③ ★ 兜底：家族进程 + 标题里明写"不响应"（★ 免得鬼窗类名变了就瞎）
        if _is_family(exe) and any(m in low_title for m in _BUSY_TITLE_MARKERS):
            reasons.append(
                "家族进程（%s）的窗口标题写着**不响应**：%r"
                % (exe.rsplit("\\", 1)[-1], title[:40])
            )
            evidence.append({"pid": w.get("pid"), "cls": cls, "title": title[:80]})
    return {
        "busy": bool(reasons),
        "reasons": reasons,
        "evidence": evidence,
        "app_windows": len(app_windows),
        "windows_scanned": len(wins),
        "★_不可归属的进度窗": stray,
        "★": "★ 只判**忙**（在算）；★ 弹窗（等你点）由 `tools/sw_guard.py` 的哨兵管；"
        "★ **进度窗必须可归属给家族**才作数（★ 否则会栽在 shell 残留窗上）",
    }


def wait_until_idle(
    timeout: float = 60.0, interval: float = 3.0, *, sleeper=None
) -> dict[str, Any]:
    """★ **等到 SolidWorks 不忙**（或超时）⇒ `{idle, waited, last, attempts}`。

    ★ 为什么需要（★ 真机：2026-10-04 第二次试跑）：★ 我们**刚把 SolidWorks 拉起来**的那几秒，
      它自己在忙 ⇒ ★ 忙检把探针的三次读数**全拒了**（★ 那是**假警报**：它马上就闲下来了）
      ⇒ ★ 故给调用方一个**有界的等待**：★ 忙 ⇒ 等一会儿再看，★ 超时 ⇒ **如实回 `idle=False`** ✓
    ⚠ ★ **有界**：`timeout` 一到就返回，★ **不无限等**（★ 事实 526 的纪律：不做无界等待）。
    """
    import time as _t

    sleep = sleeper or _t.sleep
    t0 = _t.time()
    attempts = 0
    last: dict[str, Any] = {}
    while True:
        attempts += 1
        last = solidworks_busy()
        if not last.get("busy"):
            return {
                "idle": True,
                "waited": round(_t.time() - t0, 1),
                "attempts": attempts,
                "last": last,
            }
        if _t.time() - t0 >= timeout:
            return {
                "idle": False,
                "waited": round(_t.time() - t0, 1),
                "attempts": attempts,
                "last": last,
                "reason": "等了 %.0fs 还是忙 ⇒ 停（★ 不无限等）：%s"
                % (timeout, "；".join(last.get("reasons") or [])[:200]),
            }
        sleep(interval)


def _main() -> int:
    """★ 命令行：`python scripts/sw_busy.py` ⇒ 打印当前是否忙（只读、可反复跑）。"""
    import json

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    r = solidworks_busy()
    print(json.dumps(r, ensure_ascii=False, indent=1)[:1500])
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
