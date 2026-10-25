"""★ 常驻弹窗监控：**本项目一启用就跟着起来**，一直盯着 SolidWorks 家族的弹窗。

（★ 判据与处置**全部复用** `tools/sw_guard.py` —— ★ 它就是当初为这个框做的那个东西）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 判据与处置**不新写**，全部复用既有护栏）
# 文件:   `tools/sw_guard.py` —— ★ `scan_family_windows`（★ 家族 + 像弹窗，★ 与类名无关
# ）·
# `classify_dialog`（★ 三级：auto / needs_llm / forbidden）· `dismiss` · `dismiss_via_in
# put`
#         `tools/modal_dialog_forensics.py` —— ★ 复现与取证（★ 事实 292 为同一个框写的）
#         `docs/known-facts.md` 事实 174 / 292 / 294 —— ★ 这个框的三次交手
# 定位:   ★★★★ **为什么必须有它**（★ 2026-10-04 · 用户当场点破）：
#   ```
# ★ 用户原话：★「**弹窗了你还不知道**，而且我刚刚说的弹窗检测诊断的东西，之前已经做好了
# ，
#     你翻出来用，甚至**当时就是为了解决一模一样的这个弹窗而发明的**，你找一下，
#     找出来之后**设置为这个项目运行期间一直监控**，就是别人把我们这个项目部署好之后，
#     **一启用本项目，这个弹窗检测的功能也随之启动**」
#   ```
#   ★★ 而**真根因**（★ 我在本轮实测查清，且已修）：★ 既有护栏的判据里有一句
# `if pid is not None and p.value != pid: return True` —— ★ 而 `run_guarded` 传的**永远
# 是**
#     `SLDWORKS.exe` 的 pid ⇒ ★★ **`star.exe`（求解内核）拥有的弹窗被无条件跳过** ✓
#     ★ 实测：那个 `[Simulation] 未定义载荷…` 框的 owner 是 **`star.exe`**（pid 46240），
# 而修复前 `scan_family_windows(49384)` **回 0**、`modal_dialog_forensics` 也回 `count:
# 0` ✓
#   ★★★ 第二个原因：★ 护栏是**按条命令**开哨兵的（`run_guarded` 包一个子进程）——
#     ★ 命令一结束哨兵就停；★ 而 `star.exe` 是 **SolidWorks 自己拉起来的**、会**在我们的命令
#     结束之后**才弹框 ⇒ ★ **那一刻没有任何人在看** ✓
#   ⇒ ★★★ 处置：★ **常驻**（不绑在任何一条命令上）+ ★ **判据只看家族、不看 pid** ✓
# 官方依据: 不适用（纯 Win32 窗口枚举，★ **不碰 COM** ⇒ ★ 与"会话是否挂住"无关，永远能跑
#           ）
# 许可:   本仓库 MIT。★ 只用标准库 + 复用本仓既有模块。
# ⚠ 安全：★ `auto` 档才自动点；★ `needs_llm` / `forbidden` **只记证不点**（★ 交 LLM/用户
# 判）——
# ★ 与 `sw_guard.py` 同一条纪律（★ 事实 297：「点掉进度窗 = 中断一个正在跑的正常任务」）
# 。
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


#: ★★★ 这些进程是**崩溃/遥测报告器** —— 对我们的工作没有任何用处，
#:   而它们弹的框「点掉即重弹」（CEIP 发送失败会重试）⇒ **结束进程**才是正确处置。
#:   实测依据：`SLDEXITAPP.exe` 的 `SOLIDWORKS Design 错误报告` 在 2 分钟内被点了
#:   13 万余次仍在弹（`output/dialog-watch/events.jsonl`）。
_REPORTER_EXES = frozenset({"sldexitapp.exe"})

#: 同一弹窗的去重窗口（秒）—— 同一 `(exe, class, title, 首文本)` 期间只记一次
_DEDUPE_WINDOW_S = 60.0
_recent: dict = {}


def _signature(row: dict) -> str:
    """★ 去重用的签名：进程 + 类 + 标题 + 第一个非按钮静态文本。

    ★ 不把 `hwnd` 放进去 —— 重弹时 `hwnd` 会变，但那显然是同一个框。
    """
    texts = [
        str(c.get("text") or "").strip()
        for c in (row.get("controls") or [])
        if str(c.get("class") or "").lower() != "button"
    ]
    first = next((x for x in texts if x), "")
    parts = [
        str(row.get("exe") or "").lower(),
        str(row.get("class") or ""),
        str(row.get("title") or ""),
        first,
    ]
    return "|".join(parts)


def _should_log(row: dict) -> bool:
    """★ 同一签名在窗口期内只记第一次；之后只累加记录里的 `repeat`。"""
    import time as _t

    sig = _signature(row)
    now = _t.time()
    hit = _recent.get(sig)
    if hit and (now - hit["at"]) <= _DEDUPE_WINDOW_S:
        hit["repeat"] += 1
        hit["row"]["repeat"] = hit["repeat"]
        return False
    _recent[sig] = {"at": now, "repeat": 0, "row": row}
    return True


#: ★★★ 文档（窗口）数上限 —— 超过 _DOCS_MAX 就清掉我方多余的，只留 _DOCS_KEEP 个。
#:
#:   动机（用户原话）：「如果一次性开了超过 3 个窗口，那么就强制关掉没有用的窗口，
#:   只保留 1 个正在用的窗口。否则无限制地开窗口会导致内存/显存被占满，
#:   真正要测试的东西反而跑不起来。」
#:
#:   ★ 实测背景：第 50 轮 SolidWorks 里堆了 **7 个**文档（1 零件 + 6 未保存装配体），
#:     全是探针收尾失效留下的。
_DOCS_MAX_DEFAULT = 3
_DOCS_KEEP_DEFAULT = 1

#: `output/` 根 —— 归属判据之一（我方产物都落在这儿）
OUTPUT_ROOT = ""


def _doc_owner_ok(info: dict) -> tuple:
    """★ 归属判据（与 `tools/close_my_orphans.py` 同口径）。

    | 情形 | 归属 |
    |---|---|
    | 路径在 `<仓库根>/output/` 下 | 我方 |
    | 无路径且 `type == 2`（装配体） | 我方（探针 `new_document` 建的） |
    | 无路径零件 / 非 output 路径 | **不是我方** ⇒ 不碰 |
    """
    p = str(info.get("path") or "")
    if p:
        root = OUTPUT_ROOT or str(Path(__file__).resolve().parents[1] / "output")
        if p.lower().startswith(root.lower()):
            return True, "路径在 output/ 下"
        return False, "路径不在 output/ 下"
    if int(info.get("type") or 0) == 2:
        return True, "无路径且是装配体"
    return False, "无路径且不是装配体"


def enforce_doc_cap(
    *,
    max_docs: int = _DOCS_MAX_DEFAULT,
    keep: int = _DOCS_KEEP_DEFAULT,
    keep_active: bool = True,
) -> dict:
    """★ 文档数超过 `max_docs` ⇒ 关掉我方多余的，只留 `keep` 个（含正在用的那个）。

    ★ 三条纪律：
      ① 正在用的那个（`ActiveDoc`）**永不关**
      ② **不是我的一个都不碰**（用户可能正在编辑真件）
      ③ 脏文档**先落盘再关**（`CloseDoc` 关不掉 dirty）

    :returns: {before, after, closed, kept_active, skipped_not_ours} 或跳过原因
    """

    out: dict = {"enabled": True}
    try:
        import sw_connect as _sc
        from sw_connect import get_com_member as _gcm

        conn = _sc.connect_solidworks(wait_seconds=8)
        sw = conn[0] if isinstance(conn, tuple) else conn
        if sw is None:
            return {"enabled": True, "skipped": "连不上 SolidWorks"}
    except Exception as exc:  # noqa: BLE001
        return {"enabled": True, "skipped": "连不上：%s" % str(exc)[:80]}

    try:
        docs = list(_gcm(sw, "GetDocuments") or ())
    except Exception as exc:  # noqa: BLE001
        return {"enabled": True, "skipped": "读文档失败：%s" % str(exc)[:80]}

    out["before"] = len(docs)
    if len(docs) <= max_docs:
        out["after"] = len(docs)
        out["action"] = "noop"
        return out

    #: 正在用的那个（标题）
    active_title = ""
    try:
        ad = _gcm(sw, "ActiveDoc")
        if ad is not None:
            active_title = str(_gcm(ad, "GetTitle") or "")
    except Exception:  # noqa: BLE001
        active_title = ""
    out["kept_active"] = active_title

    closed: list = []
    skipped: list = []
    #: ★ `keep` 是「**总共**保留几个」，**含**正在用的那个。
    #:   所以活动文档存在时 `kept` 的初值就是 1 —— 否则会多留一个
    #:   （第 50 轮真机实测：`keep=1` 却剩下 2 个）。
    kept = 1 if (keep_active and active_title) else 0
    for d in docs:
        try:
            title = str(_gcm(d, "GetTitle") or "")
            info = {
                "title": title,
                "type": int(_gcm(d, "GetType") or 0),
                "dirty": bool(_gcm(d, "GetSaveFlag")),
                "path": str(_gcm(d, "GetPathName") or ""),
            }
        except Exception:  # noqa: BLE001
            continue

        #: ★ `keep_active=True`（默认）：正在用的那个**永不关**。
        #:   收尾场景（`max_docs=0, keep=0, keep_active=False`）才允许关它。
        if keep_active and title and title == active_title:
            #: ★ 已算进 `kept` 初值，这里**不再 +1**
            continue
        if kept < keep:
            kept += 1
            continue

        mine, why = _doc_owner_ok(info)
        if not mine:
            skipped.append({"title": title, "why": why})
            continue

        #: ★ 脏文档先落盘再关（`CloseDoc` 关不掉 dirty）
        if info["dirty"]:
            try:
                _root = OUTPUT_ROOT or str(
                    Path(__file__).resolve().parents[1] / "output"
                )
                dest = Path(_root) / "dialog-watch" / "docs"
                dest.mkdir(parents=True, exist_ok=True)
                safe = "".join(
                    c if c.isalnum() or c in "-_" else "_" for c in title
                )[:40]
                _sc.save_document(d, str(dest / (safe or "doc") + ".SLDASM"))
            except Exception:  # noqa: BLE001
                pass
        try:
            sw.CloseDoc(title)
        except Exception as exc:  # noqa: BLE001
            closed.append({"title": title, "ok": False, "err": str(exc)[:60]})
        else:
            closed.append({"title": title, "ok": True})

    try:
        left = len(list(_gcm(sw, "GetDocuments") or ()))
    except Exception:  # noqa: BLE001
        left = -1
    out.update(
        {
            "after": left,
            "closed": closed,
            "skipped_not_ours": skipped,
            "action": "capped",
            "max_docs": max_docs,
            "keep": keep,
        }
    )
    return out


def _terminate_process(pid: int) -> bool:
    """★ 结束一个**报告器**进程（`SLDEXITAPP.exe`）。它的框点不干净，只能让它走。"""
    import ctypes

    process_terminate = 0x0001
    if not pid or int(pid) <= 0:
        return False
    h = ctypes.windll.kernel32.OpenProcess(process_terminate, False, int(pid))
    if not h:
        return False
    try:
        return bool(ctypes.windll.kernel32.TerminateProcess(h, 1))
    finally:
        ctypes.windll.kernel32.CloseHandle(h)


def _append(ev: dict) -> None:
    """★ 写一条事件（**带去重**）—— 同一弹窗 60 秒内只落一行。

    ★ 去重是为了修 254 MB 那个问题：同一框每 2 秒一行完整 JSON，
      两分钟就上千行，十小时就 16 万行。现在只记第一次，之后累加 `repeat`。
    """
    if not _should_log(ev):
        return
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
        row = {
            "at": _now(),
            "kind": "dialog",
            "hwnd": d.get("hwnd"),
            "pid": d.get("pid"),
            "exe": d.get("exe"),
            "class": d.get("class"),
            "title": d.get("title"),
            "controls": d.get("controls") or [],
            "hung": d.get("hung"),
            "verdict": verdict,
            "needs_llm": mode != "auto",
            "dismissed": False,
        }
        #: ★★★ 报告器（`SLDEXITAPP.exe`）**不点，直接结束进程** ——
        #:   它的框点掉即重弹（CEIP 遥测重试），实测 13 万次仍在弹。
        #:   ★ 它对我们没有任何用处：不读它的报告、不依赖它。
        if (
            dismiss
            and str(row.get("exe") or "").lower() in _REPORTER_EXES
            and _terminate_process(int(row.get("pid") or 0))
        ):
            row["dismissed"] = True
            row["action"] = "terminated-reporter"
            rows.append(row)
            _append(row)
            continue

        #: ★★ **只有 `auto` 档才点** —— ★ `needs_llm` / `forbidden` 一律**只记证**
        if dismiss and mode == "auto":
            fired = False
            try:
                fired = sw_guard.dismiss(d["hwnd"])
                if not fired or sw_guard._u.IsWindow(d["hwnd"]):
                    fired = sw_guard.dismiss_via_input(d["hwnd"]) or fired
                    if sw_guard._u.IsWindow(d["hwnd"]):
                        fired = False
            except Exception:  # noqa: BLE001
                fired = False
            row["dismissed"] = bool(fired)
            row["still_present"] = bool(sw_guard._u.IsWindow(d["hwnd"]))
        rows.append(row)
        _append(row)
    pending = [r for r in rows if r.get("needs_llm") and not r.get("dismissed")]
    snap = {
        "at": _now(),
        "dialogs": len(rows),
        "pending_needs_llm": len(pending),
        "pids": sorted({r.get("pid") for r in rows}),
        "rows": rows,
    }
    return snap


def run(
    *,
    interval: float = 1.0,
    seconds: float | None = None,
    dismiss: bool = True,
    quiet: bool = False,
    doc_cap: bool = True,
    max_docs: int = _DOCS_MAX_DEFAULT,
    keep_docs: int = _DOCS_KEEP_DEFAULT,
) -> dict:
    """★ **常驻循环**：每 `interval` 秒扫一遍；`seconds` 给了就是有界跑（★ 测试/CI 用）。

    ★ 状态随时落盘到 `output/dialog-watch/status.json` ⇒ ★ **别人（或 LLM）随时读得到** ✓
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        PIDFILE.write_text(str(os.getpid()), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    state = {
        "started": _now(),
        "pid": os.getpid(),
        "running": True,
        "scans": 0,
        "dialogs_seen": 0,
        "dismissed": 0,
        "pending_needs_llm": 0,
        "last": None,
        #: ★ 文档（窗口）数上限的累计读数
        "doc_cap_enabled": bool(doc_cap),
        "doc_cap_max": int(max_docs),
        "doc_cap_triggers": 0,
        "doc_cap_closed": 0,
        "doc_cap_skipped_not_ours": 0,
        "doc_cap_last": None,
    }
    stop = {"flag": False}

    def _sig(_s, _f):
        stop["flag"] = True

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _sig)
        except Exception:  # noqa: BLE001
            pass
    t0 = time.time()
    try:
        while not stop["flag"]:
            #: ★★★ 每轮先做「文档数上限」—— 超过就关掉我方多余的，只留正在用的那个。
            #:   放在弹窗扫描**之前**：窗口越少，扫描也越快。
            if doc_cap:
                try:
                    cap = enforce_doc_cap(max_docs=max_docs, keep=keep_docs)
                except Exception as exc:  # noqa: BLE001
                    cap = {"enabled": True, "err": "%s: %s" % (type(exc).__name__,
                                                              str(exc)[:80])}
                state["doc_cap_last"] = cap
                if cap.get("action") == "capped":
                    state["doc_cap_triggers"] += 1
                    state["doc_cap_closed"] += len(
                        [c for c in (cap.get("closed") or ()) if c.get("ok")]
                    )
                    state["doc_cap_skipped_not_ours"] += len(
                        cap.get("skipped_not_ours") or ()
                    )
                    if not quiet:
                        print(
                            "★ 文档数 %s → %s（> %s）· 关了我方 %d 个%s"
                            % (
                                cap.get("before"),
                                cap.get("after"),
                                max_docs,
                                len([c for c in (cap.get("closed") or ())
                                     if c.get("ok")]),
                                (
                                    "；★ 跳过 %d 个不是我的"
                                    % len(cap.get("skipped_not_ours") or ())
                                    if cap.get("skipped_not_ours")
                                    else ""
                                ),
                            )
                        )
                    _append(
                        {
                            "at": _now(),
                            "kind": "doc-cap",
                            "before": cap.get("before"),
                            "after": cap.get("after"),
                            "closed": cap.get("closed"),
                            "skipped_not_ours": cap.get("skipped_not_ours"),
                            "kept_active": cap.get("kept_active"),
                        }
                    )
            snap = scan_now(dismiss=dismiss)
            state["scans"] += 1
            state["dialogs_seen"] += snap["dialogs"]
            state["dismissed"] += sum(1 for r in snap["rows"] if r.get("dismissed"))
            state["pending_needs_llm"] = snap["pending_needs_llm"]
            state["last"] = {
                "at": snap["at"],
                "dialogs": snap["dialogs"],
                "pending_needs_llm": snap["pending_needs_llm"],
                "rows": [
                    {
                        k: r.get(k)
                        for k in ("at", "exe", "title", "needs_llm", "dismissed")
                    }
                    for r in snap["rows"]
                ],
            }
            state["uptime_s"] = round(time.time() - t0, 1)
            _write_status(state)
            if snap["dialogs"] and not quiet:
                for r in snap["rows"]:
                    print(
                        "[%s] %s:%s needs_llm=%s dismissed=%s %r"
                        % (
                            r["at"],
                            r.get("exe"),
                            r.get("pid"),
                            r["needs_llm"],
                            r["dismissed"],
                            str(r.get("title"))[:40],
                        )
                    )
            if seconds is not None and time.time() - t0 >= seconds:
                break
            time.sleep(max(0.2, interval))
    finally:
        state["running"] = False
        state["stopped"] = _now()
        _write_status(state)
        try:
            PIDFILE.unlink()
        except Exception:  # noqa: BLE001
            pass
    return state


def status() -> dict:
    """★ 读当前状态（★ 给工具层/LLM 用：★ "监控在不在跑、抓到过什么"）。"""
    alive = None
    if PIDFILE.is_file():
        try:
            pid = int(PIDFILE.read_text(encoding="utf-8").strip())
            alive = _pid_alive(pid)
        except Exception:  # noqa: BLE001
            alive = None
    out = {"watcher_pidfile": str(PIDFILE), "watcher_alive": alive}
    if STATUS.is_file():
        try:
            out["status"] = json.loads(STATUS.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            out["status"] = None
    out["events_file"] = str(EVENTS)
    out["events_lines"] = (
        sum(1 for _ in EVENTS.open(encoding="utf-8")) if EVENTS.is_file() else 0
    )
    return out


def _pid_alive(pid: int) -> bool:
    import ctypes

    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return False
    ctypes.windll.kernel32.CloseHandle(h)
    return True


def _ensure_running() -> int:
    """★ 幂等：监控在跑 ⇒ 返回 0；没跑 ⇒ 后台起一个再返回 0。

    ★ 给 `round_chain.ps1` 每轮调用 —— 这样「常驻」不靠人记得手动起。
    """
    import subprocess
    import sys as _sys

    pid_file = OUT_DIR / "watcher.pid"
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        pid = 0
    if pid and _pid_alive(pid):
        print("★ 弹窗监控已在跑（PID %d）⇒ 不需要重启" % pid)
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    flags = 0
    if _sys.platform == "win32":
        #: ★ 脱离当前控制台，收尾链退出后监控继续活着
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        [_sys.executable, "-B", str(Path(__file__).resolve()), "--quiet"],
        cwd=str(Path(__file__).resolve().parents[1]),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    pid_file.write_text(str(proc.pid), encoding="utf-8")
    print("★ 弹窗监控已后台启动（PID %d）" % proc.pid)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="常驻弹窗监控（复用 sw_guard 的判据与处置）"
    )
    ap.add_argument("--once", action="store_true", help="只扫一遍")
    ap.add_argument(
        "--seconds", type=float, default=None, help="跑这么多秒（默认常驻）"
    )
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--no-dismiss", action="store_true", help="只记证、一个都不点")
    ap.add_argument("--status", action="store_true", help="打印状态后退出")
    ap.add_argument(
        "--ensure",
        action="store_true",
        help="★ 幂等：已在跑就返回 0，没跑就后台起一个（给每轮收尾链调用）",
    )
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument(
        "--no-doc-cap",
        action="store_true",
        help="★ 关掉「文档数上限」（默认开：超过 --max-docs 就清掉我方多余的窗口）",
    )
    ap.add_argument(
        "--max-docs",
        type=int,
        default=_DOCS_MAX_DEFAULT,
        help="★ 文档数超过这个值才清理（默认 %d）" % _DOCS_MAX_DEFAULT,
    )
    ap.add_argument(
        "--keep-docs",
        type=int,
        default=_DOCS_KEEP_DEFAULT,
        help="★ 清理后保留几个（含正在用的那个，默认 %d）" % _DOCS_KEEP_DEFAULT,
    )
    a = ap.parse_args()
    if a.ensure:
        return _ensure_running()
    if a.status:
        print(json.dumps(status(), ensure_ascii=False, indent=1)[:2500])
        return 0
    if a.once:
        if not a.no_doc_cap:
            print(
                json.dumps(
                    enforce_doc_cap(max_docs=int(a.max_docs), keep=int(a.keep_docs)),
                    ensure_ascii=False,
                    indent=1,
                )[:1500]
            )
        print(
            json.dumps(
                scan_now(dismiss=not a.no_dismiss), ensure_ascii=False, indent=1
            )[:2500]
        )
        return 0
    st = run(
        interval=a.interval,
        seconds=a.seconds,
        dismiss=not a.no_dismiss,
        quiet=a.quiet,
        doc_cap=not a.no_doc_cap,
        max_docs=int(a.max_docs),
        keep_docs=int(a.keep_docs),
    )
    print(
        json.dumps(
            {
                k: st.get(k)
                for k in (
                    "started",
                    "stopped",
                    "scans",
                    "dialogs_seen",
                    "dismissed",
                    "pending_needs_llm",
                    "doc_cap_triggers",
                    "doc_cap_closed",
                    "doc_cap_skipped_not_ours",
                )
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
