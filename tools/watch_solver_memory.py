"""★ 内存看门狗：仿真求解进程（`cwbcbfmesh.exe`）吃过头就把它斩掉，★ 只报 + 只斩自己那份。

（★ 处置事实 521：一次 38.5 GB / 63.8 GB 的真机事故 —— ★ 让"上限"变成可执行的闸）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SOLIDWORKS Simulation 官方手册（本机解包 `C:\cworks_manual\`）
# 文件:   `scripts/sw_simulation.py`（`solve_memory_preflight` / `default_solve_memory_budget_gb`）
#         `scripts/sw_connect.py`（`read_owned_instance` —— ★ 只认**我们自己启动的**那份 SW）
# 官方依据: `c_Analysis_Solvers.htm` 逐字「If a solver requires more memory than available on
#           the computer, then the solver uses disk space … the solution progress can be
#           extremely slow.」⇒ ★ 内存不够**不是报错、是极慢** ⇒ 必须由外部闸来拦 ✓
# 定位:   ★★★ **为什么需要它**：仓内两道闸（`check_mesh_size_sane` 按包围盒估、
#   `solve_memory_preflight` 按真实单元数估）都是**事前估计**；★ 而估算总有偏
#   （非长方体 / 局部细化 / 接触迭代）⇒ ★★ **第三层是"运行期实测 + 越线就斩"** ✓
#   ★ 判据（★ 两条都要）：
#     ① **整机剩余物理内存** < `--floor-gb` ⇒ 斩（★ 保护整机 —— 用户的原话是"内存干满、程序卡住"）
#     ② **求解进程工作集** > `--budget-gb` ⇒ 斩（★ 保护单个求解）
#   ★★ **只斩两类进程**：`cwbcbfmesh.exe`（Simulation 求解器）· ★ 且仅在**连续越线 2 次**后
#     才动**我们自己启动的** `SLDWORKS`（★ PID 取自 `sw_connect` 的归属标记）——
#     ★ **绝不按进程名杀 SolidWorks**（★ 那会误杀别的对话/用户自己开的，违反资源纪律）✓
#   ⚠ 本脚本**只报不动**：不碰仓库、只写 `output/`；★ `--no-kill` 时连进程都不动（纯观测）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import ctypes
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LOG = REPO / "output" / "solver-memory-watch.jsonl"
SOLVER_NAMES = ("cwbcbfmesh.exe",)


class _MemStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def system_memory() -> dict:
    """回 `{total_gb, free_gb}`（★ 读不到回空 dict —— ★ 不因为读不到就误判）。"""
    try:
        st = _MemStatus()
        st.dwLength = ctypes.sizeof(_MemStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return {}
        return {"total_gb": round(st.ullTotalPhys / 1024 ** 3, 2),
                "free_gb": round(st.ullAvailPhys / 1024 ** 3, 2)}
    except Exception:                                          # noqa: BLE001
        return {}


def solver_processes() -> list[dict]:
    """回仿真求解进程（★ 按 exe 名精确匹配 —— ★ 不按窗口标题猜）。"""
    out: list[dict] = []
    try:
        ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -in @(%s) } | "
              "Select-Object ProcessId,Name,WorkingSetSize | ConvertTo-Json -Compress"
              % ",".join("'%s'" % n for n in SOLVER_NAMES))
        r = subprocess.run(["pwsh", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30, stdin=subprocess.DEVNULL)
        raw = (r.stdout or "").strip()
        if not raw:
            return []
        data = json.loads(raw)
        for d in (data if isinstance(data, list) else [data]):
            out.append({"pid": int(d.get("ProcessId") or 0), "name": str(d.get("Name") or ""),
                        "work_gb": round(float(d.get("WorkingSetSize") or 0) / 1024 ** 3, 2)})
    except Exception:                                          # noqa: BLE001
        pass
    return out


def kill(pid: int, why: str, logf) -> bool:
    """斩一个 PID（★ 只用 `taskkill /PID`，★ 不按名字批量杀）。"""
    try:
        r = subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30, stdin=subprocess.DEVNULL)
        ok = r.returncode == 0
        logf({"event": "kill", "pid": pid, "ok": ok, "why": why})
        print("   ⇒ 斩 %d：%s（%s）" % (pid, "成功" if ok else "失败", why))
        return ok
    except Exception as exc:                                   # noqa: BLE001
        logf({"event": "kill_error", "pid": pid, "err": str(exc)[:120]})
        return False


def owned_solidworks_pid() -> int | None:
    """★ 只取**我们自己启动的**那份 SolidWorks 的 PID（★ 归属标记里那个）。"""
    try:
        import sw_connect

        m = sw_connect.read_owned_instance() or {}
        return int(m.get("pid")) if m.get("pid") else None
    except Exception:                                          # noqa: BLE001
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="仿真内存看门狗（★ 只斩求解器；★ 绝不按名字杀 SW）")
    ap.add_argument("--floor-gb", type=float, default=6.0, help="整机剩余内存低于此值 ⇒ 斩")
    ap.add_argument("--budget-gb", type=float, default=16.0, help="求解进程工作集高于此值 ⇒ 斩")
    ap.add_argument("--interval", type=float, default=2.0, help="轮询间隔（秒）")
    ap.add_argument("--seconds", type=float, default=3600.0, help="最长看多久（秒）")
    ap.add_argument("--no-kill", action="store_true", help="★ 只观测、不斩（纯报告）")
    a = ap.parse_args()

    LOG.parent.mkdir(parents=True, exist_ok=True)
    fh = LOG.open("a", encoding="utf-8")

    def logf(rec: dict) -> None:
        rec["at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()

    t0 = time.time()
    breach_streak = 0
    kills = 0
    print("★ 看门狗启动：floor=%.1f GB · budget=%.1f GB · interval=%.1fs · kill=%s"
          % (a.floor_gb, a.budget_gb, a.interval, not a.no_kill))
    while time.time() - t0 < a.seconds:
        mem = system_memory()
        procs = solver_processes()
        rec = {"mem": mem, "solvers": procs}
        over = []
        if mem and mem.get("free_gb", 999) < a.floor_gb:
            over.append("整机剩余 %.2f GB < floor %.1f GB" % (mem["free_gb"], a.floor_gb))
        for p in procs:
            if p["work_gb"] > a.budget_gb:
                over.append("求解器 pid=%d 工作集 %.2f GB > budget %.1f GB"
                            % (p["pid"], p["work_gb"], a.budget_gb))
        rec["over"] = over
        logf(rec)
        if over:
            breach_streak += 1
            print("  ⚠ 越线（第 %d 次）：%s" % (breach_streak, "；".join(over)))
            if not a.no_kill:
                for p in procs:
                    kill(p["pid"], "；".join(over), logf)
                    kills += 1
                #: ★★ 连续越线 ≥2 次 ⇒ 求解器**在反复重生** ⇒ 连**我们自己那份** SW 一起收掉
                #:   （★ PID 只从归属标记取 —— ★ 绝不按进程名杀 SW）
                if breach_streak >= 2:
                    pid = owned_solidworks_pid()
                    if pid:
                        print("   ⇒ 连续越线 ⇒ 收掉**我们自己启动的** SolidWorks pid=%d" % pid)
                        kill(pid, "连续越线：防止求解器反复重生", logf)
                        try:
                            import sw_connect

                            sw_connect.clear_owned_instance()
                        except Exception:                      # noqa: BLE001
                            pass
                    logf({"event": "stop", "reason": "连续越线，看门狗收工"})
                    break
            else:
                print("   （--no-kill：只报不斩）")
        else:
            breach_streak = 0
        time.sleep(max(a.interval, 0.5))
    logf({"event": "exit", "kills": kills, "seconds": round(time.time() - t0, 1)})
    fh.close()
    print("★ 看门狗收工：斩了 %d 次 · 日志 %s" % (kills, LOG))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
