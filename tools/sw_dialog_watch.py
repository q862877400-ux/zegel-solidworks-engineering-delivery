"""★ 常驻弹窗监控：**本项目一启用就跟着起来**，一直盯着 SolidWorks 家族的弹窗。

（★ 判据与处置**全部复用** `tools/sw_guard.py` —— ★ 它就是当初为这个框做的那个东西）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 判据与处置**不新写**，全部复用既有护栏）
# 文件:   `tools/sw_guard.py` —— ★ `scan_family_windows`（★ 家族 + 像弹窗，★ 与类名无关）·
#           `classify_dialog`（★ 三级：auto / needs_llm / forbidden）· `dismiss` · `dismiss_via_input`
#         `tools/modal_dialog_forensics.py` —— ★ 复现与取证（★ 事实 292 为同一个框写的）
#         `docs/known-facts.md` 事实 174 / 292 / 294 —— ★ 这个框的三次交手
# 定位:   ★★★★ **为什么必须有它**（★ 2026-10-04 · 用户当场点破）：
#   ```
#   ★ 用户原话：★「**弹窗了你还不知道**，而且我刚刚说的弹窗检测诊断的东西，之前已经做好了，
#     你翻出来用，甚至**当时就是为了解决一模一样的这个弹窗而发明的**，你找一下，
#     找出来之后**设置为这个项目运行期间一直监控**，就是别人把我们这个项目部署好之后，
#     **一启用本项目，这个弹窗检测的功能也随之启动**」
#   ```
#   ★★ 而**真根因**（★ 我在本轮实测查清，且已修）：★ 既有护栏的判据里有一句
#     `if pid is not None and p.value != pid: return True` —— ★ 而 `run_guarded` 传的**永远是**
#     `SLDWORKS.exe` 的 pid ⇒ ★★ **`star.exe`（求解内核）拥有的弹窗被无条件跳过** ✓
#     ★ 实测：那个 `[Simulation] 未定义载荷…` 框的 owner 是 **`star.exe`**（pid 46240），
#     而修复前 `scan_family_windows(49384)` **回 0**、`modal_dialog_forensics` 也回 `count: 0` ✓
#   ★★★ 第二个原因：★ 护栏是**按条命令**开哨兵的（`run_guarded` 包一个子进程）——
#     ★ 命令一结束哨兵就停；★ 而 `star.exe` 是 **SolidWorks 自己拉起来的**、会**在我们的命令
#     结束之后**才弹框 ⇒ ★ **那一刻没有任何人在看** ✓
#   ⇒ ★★★ 处置：★ **常驻**（不绑在任何一条命令上）+ ★ **判据只看家族、不看 pid** ✓
# 官方依据: 不适用（纯 Win32 窗口枚举，★ **不碰 COM** ⇒ ★ 与"会话是否挂住"无关，永远能跑）
# 许可:   本仓库 MIT。★ 只用标准库 + 复用本仓既有模块。
# ⚠ 安全：★ `auto` 档才自动点；★ `needs_llm` / `forbidden` **只记证不点**（★ 交 LLM/用户判）——
#   ★ 与 `sw_guard.py` 同一条纪律（★ 事实 297：「点掉进度窗 = 中断一个正在跑的正常任务」）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO / "tools"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

OUT_DIR = REPO / "output" / "dialog-watch"
EVENTS = OUT_DIR / "events.jsonl"
STATUS = OUT_DIR / "status.json"
PIDFILE = OUT_DIR / "watcher.pid"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _write_status(state: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def _append(ev: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")


def scan_now(*, dismiss: bool = True) -> dict:
    """★ 扫一遍（★ 判据**全部复用** `sw_guard`）⇒ 记证 + 按档处置 ⇒ 回本次快照。

    ★★ **`pid=None`** 是有意的：★ 家族里**任一进程**（`star.exe` / `cwbcbfmesh.exe` /
      `sldsurfacing.exe` …）的框都要看得见 —— ★ 那正是"弹窗了你还不知道"的根因所在 ✓
    """
    import sw_guard

    found = sw_guard.scan_family_windows(None)
    rows: list[dict] = []
    for d in found:
        verdict = sw_guard.classify_dialog(d)
        mode = verdict.get("mode")
        row = {"at": _now(), "kind": "dialog", "hwnd": d.get("hwnd"), "pid": d.get("pid"),
               "exe": d.get("exe"), "class": d.get("class"), "title": d.get("title"),
               "controls": d.get("controls") or [], "hung": d.get("hung"),
               "verdict": verdict, "needs_llm": mode != "auto", "dismissed": False}
        #: ★★ **只有 `auto` 档才点** —— ★ `needs_llm` / `forbidden` 一律**只记证**
        if dismiss and mode == "auto":
            fired = False
            try:
                fired = sw_guard.dismiss(d["hwnd"])
                if not fired or sw_guard._u.IsWindow(d["hwnd"]):
                    fired = sw_guard.dismiss_via_input(d["hwnd"]) or fired
                    if sw_guard._u.IsWindow(d["hwnd"]):
                        fired = False
            except Exception:                                   # noqa: BLE001
                fired = False
            row["dismissed"] = bool(fired)
            row["still_present"] = bool(sw_guard._u.IsWindow(d["hwnd"]))
        rows.append(row)
        _append(row)
    pending = [r for r in rows if r.get("needs_llm") and not r.get("dismissed")]
    snap = {"at": _now(), "dialogs": len(rows), "pending_needs_llm": len(pending),
            "pids": sorted({r.get("pid") for r in rows}), "rows": rows}
    return snap


def run(*, interval: float = 1.0, seconds: float | None = None, dismiss: bool = True,
        quiet: bool = False) -> dict:
    """★ **常驻循环**：每 `interval` 秒扫一遍；`seconds` 给了就是有界跑（★ 测试/CI 用）。

    ★ 状态随时落盘到 `output/dialog-watch/status.json` ⇒ ★ **别人（或 LLM）随时读得到** ✓
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        PIDFILE.write_text(str(os.getpid()), encoding="utf-8")
    except Exception:                                           # noqa: BLE001
        pass
    state = {"started": _now(), "pid": os.getpid(), "running": True, "scans": 0,
             "dialogs_seen": 0, "dismissed": 0, "pending_needs_llm": 0, "last": None}
    stop = {"flag": False}

    def _sig(_s, _f):
        stop["flag"] = True

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _sig)
        except Exception:                                       # noqa: BLE001
            pass
    t0 = time.time()
    try:
        while not stop["flag"]:
            snap = scan_now(dismiss=dismiss)
            state["scans"] += 1
            state["dialogs_seen"] += snap["dialogs"]
            state["dismissed"] += sum(1 for r in snap["rows"] if r.get("dismissed"))
            state["pending_needs_llm"] = snap["pending_needs_llm"]
            state["last"] = {"at": snap["at"], "dialogs": snap["dialogs"],
                             "pending_needs_llm": snap["pending_needs_llm"],
                             "rows": [{k: r.get(k) for k in
                                       ("at", "exe", "title", "needs_llm", "dismissed")}
                                      for r in snap["rows"]]}
            state["uptime_s"] = round(time.time() - t0, 1)
            _write_status(state)
            if snap["dialogs"] and not quiet:
                for r in snap["rows"]:
                    print("[%s] %s:%s needs_llm=%s dismissed=%s %r"
                          % (r["at"], r.get("exe"), r.get("pid"), r["needs_llm"],
                             r["dismissed"], str(r.get("title"))[:40]))
            if seconds is not None and time.time() - t0 >= seconds:
                break
            time.sleep(max(0.2, interval))
    finally:
        state["running"] = False
        state["stopped"] = _now()
        _write_status(state)
        try:
            PIDFILE.unlink()
        except Exception:                                       # noqa: BLE001
            pass
    return state


def status() -> dict:
    """★ 读当前状态（★ 给工具层/LLM 用：★ "监控在不在跑、抓到过什么"）。"""
    alive = None
    if PIDFILE.is_file():
        try:
            pid = int(PIDFILE.read_text(encoding="utf-8").strip())
            alive = _pid_alive(pid)
        except Exception:                                       # noqa: BLE001
            alive = None
    out = {"watcher_pidfile": str(PIDFILE), "watcher_alive": alive}
    if STATUS.is_file():
        try:
            out["status"] = json.loads(STATUS.read_text(encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            out["status"] = None
    out["events_file"] = str(EVENTS)
    out["events_lines"] = (sum(1 for _ in EVENTS.open(encoding="utf-8"))
                           if EVENTS.is_file() else 0)
    return out


def _pid_alive(pid: int) -> bool:
    import ctypes

    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return False
    ctypes.windll.kernel32.CloseHandle(h)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="常驻弹窗监控（复用 sw_guard 的判据与处置）")
    ap.add_argument("--once", action="store_true", help="只扫一遍")
    ap.add_argument("--seconds", type=float, default=None, help="跑这么多秒（默认常驻）")
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--no-dismiss", action="store_true", help="只记证、一个都不点")
    ap.add_argument("--status", action="store_true", help="打印状态后退出")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.status:
        print(json.dumps(status(), ensure_ascii=False, indent=1)[:2500])
        return 0
    if a.once:
        print(json.dumps(scan_now(dismiss=not a.no_dismiss), ensure_ascii=False, indent=1)[:2500])
        return 0
    st = run(interval=a.interval, seconds=a.seconds, dismiss=not a.no_dismiss, quiet=a.quiet)
    print(json.dumps({k: st.get(k) for k in ("started", "stopped", "scans", "dialogs_seen",
                                             "dismissed", "pending_needs_llm")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
