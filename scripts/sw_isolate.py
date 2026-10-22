"""**隔离执行**：把"可能永久挂起"的 COM 调用放进**可被杀的子进程**里跑。

## ★★★★★ 为什么这是"从代码层面解决"（而不是看门狗）
```
★ 用户指令（2026-10-01）：「**你不要使用任何看门狗，看门狗这个东西不可靠，
  你就从代码层面解决**」+「**这个弹窗不能是仅适用于本机**」
⇒ ★★ 看门狗的三个死穴：① 轮询有**窗口期**（COM 可能先挂住）② **本机专属**
   ③ 只是**反应**，而且必须先"看见框"
★ 而**根因**早已写在 `AGENTS.md` 铁律 2 里：
    「COM 是 **STA 且线程亲和**，调用一旦开始**无法强制中止**；
      **超时只救「等待」，救不了线程**」
  ⇒ ★★★ 所以"在**同一进程**里加超时 / 加前置守卫"**结构上就不通**
     （本会话为此失败三次：原版 / `Count` 守卫 / 材料守卫 —— 见 known-facts 174）
⇒ ★★★★ **正解 = 换一个能被杀掉的地方跑**：
     主进程 → 起子进程 → 子进程做 COM 调用 → ★ **主进程带超时等它**
     ⇒ 超时 / 挂起 ⇒ **杀掉子进程** ⇒ **主流程继续，SolidWorks 会话不受影响**。
```

## ★★★ 前提已**真机验证**（`tools/experiment_subprocess_com.py`，2026-10-01）
```
★ 三个问题，三条都过（★ 这是"不预设结论"的做法）：
   ① 子进程能连到**同一个** SolidWorks 实例吗？ ⇒ **能**（`CHILD_OK rev=34.4.1`，0.1s）
   ② 子进程连过之后主进程还能用吗？            ⇒ **能**（`ok=True`）
   ③ ★★ **子进程卡住时主进程被阻塞吗？**        ⇒ ★ **不被**（`ok=True`，用时 **0.01s**）
   ④ 卡住的子进程能杀掉吗？                    ⇒ **能**，且 kill 后主进程仍可用
⇒ ★★ 这**修正了已知事实 24 的口径**：
   「多个进程抢同一 COM 连接会死锁」—— ★ 实测是**「并发驱动」**会；
   ★ **「隔离起来、一次一个、可弃」不会**。
```

## ★ 它满足用户提的每一条
```
① **随 skill 发布** —— 本文件在 `scripts/`（能力层），不是某台机器的工具
② **不依赖本机路径** —— 只用 `sys.executable` 与标准库
③ ★ **结构上保证挂起不外溢** —— **不轮询、不需要知道"是什么框"**
④ 规则通用（Windows + SolidWorks 皆然）
```

## 用法
```python
from sw_isolate import run_isolated

#: ★ 会弹模态框的调用，一律走它
result = run_isolated("scripts.sw_simulation", "run_analysis", args=[study_name],
                      timeout=180)
if result["timed_out"]:
    ...  #: ★ 子进程已被杀，会话完好；如实报告"超时"
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_isolate.py
# 定位:   24h 计划的**地基**：让"模态框永久挂起"这一类事故**在结构上不可能外溢**。
# 官方依据: 不适用（纯进程隔离）；★ 判据来自 `tools/experiment_subprocess_com.py` 的真机
#           三条
# 许可:   本仓库 MIT。只用标准库。
# ⚠ 子进程里的异常会**序列化**回来（★ 不吞掉），并带 `isolated: True` 标记。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

__all__ = ["run_isolated", "ISOLATED_MARKER", "kill_tree"]

#: ★★ 隔离执行的**标记** —— 调用方据此知道"这条结果来自子进程"
ISOLATED_MARKER = "__isolated__"

#: 子进程里跑的蹦床代码：把模块/函数/参数/关键字显式传进去，结果以 JSON 从 stdout 回。
_CHILD = r"""
import json, sys, traceback

def _main() -> int:
    req = json.loads(sys.stdin.read() or "{}")
    #: ★ 仓库根与 scripts 由父进程通过 PYTHONPATH 给（见 run_isolated）
    import importlib
    out = {"__isolated__": True}
    try:
        #: ★ `module` 是**点分路径**（如 "scripts.sw_simulation"）—— ★ 不写死 `scripts.` 前缀，
        #:   那样调用方也能隔离 `tools.*` 或第三方模块（★ 也更便于测试）。
        mod = importlib.import_module(req["module"])
        fn = getattr(mod, req["function"])
        r = fn(*req.get("args", []), **req.get("kwargs", {}))
        #: ★ 只回**可 JSON 化**的东西；不可序列化的按 repr 回（★ 不假装它能序列化）
        try:
            json.dumps(r)
            out["result"] = r
        except TypeError:
            out["result"] = repr(r)[:2000]
            out["result_not_json_able"] = True
        out["ok"] = True
    except BaseException as exc:                              # noqa: BLE001
        out["ok"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:600])
        out["traceback"] = traceback.format_exc()[-1500:]
    sys.stdout.write("@@DSH_ISOLATED@@" + json.dumps(out, ensure_ascii=False))
    return 0

raise SystemExit(_main())
"""


def _kill_tree(pid: int, *, timeout: float = 20.0) -> dict[str, Any]:
    """★ 用 `taskkill /T /F` 杀**整棵进程树**（★ 这是本仓**实测**唯一有效的那条路）。

    ★★★ 为什么不用 `Popen.kill()`（★ 2026-10-04 真机实测 · 事实 526）：
      · 一个**卡在跨进程 COM 调用里**的子进程，`Popen.kill()`（= `TerminateProcess`）
        **没有让它消失** —— ★ 它在我手动 `taskkill /PID … /F /T` **之前一直活着**；
      · ★ 而 `taskkill /F /T` **一秒就杀掉了它** ✓
      ⚠ ★ 机制：`TerminateProcess` 对**正处于内核态等待**的进程只是**置一个标记**，
        ★ 要等它回到用户态才真正退出；★ `taskkill` 走的是同一族 API 但**带上整棵树 + 强制**，
        在实测里**就是更可靠** ✓

    :returns: `{ok, returncode, seconds, stdout, error}` —— ★ **自己不抛异常**（★ 杀不掉也要如实回）。
    """
    import subprocess as _sp
    import time as _t

    t0 = _t.time()
    try:
        p = _sp.run(
            ["taskkill", "/PID", str(int(pid)), "/F", "/T"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=_sp.DEVNULL,
        )
        return {
            "ok": p.returncode == 0,
            "returncode": p.returncode,
            "seconds": round(_t.time() - t0, 2),
            "stdout": (p.stdout or "").strip()[:200],
            "error": None
            if p.returncode == 0
            else (p.stderr or p.stdout or "").strip()[:200],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "returncode": None,
            "seconds": round(_t.time() - t0, 2),
            "stdout": "",
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
        }


#: ★ 公开别名（★ 看门狗/调用方也可以用同一条"杀整棵树"的路）
kill_tree = _kill_tree


def run_isolated(
    module: str,
    function: str,
    *,
    args: list | None = None,
    kwargs: dict | None = None,
    timeout: float = 180.0,
    drain_timeout: float = 10.0,
    python: str | None = None,
) -> dict[str, Any]:
    """在**可被杀的子进程**里调用 `scripts.<module>.<function>`。

    :param module: **点分模块路径**，如 `"scripts.sw_simulation"`（★ 见下例）。
    :param function: 函数名。
    :param args/kwargs: 实参（★ 必须**可 JSON 化** —— 因为要跨进程传）。
    :param timeout: 秒。★ **超时 = 杀子进程**（这正是本模块存在的理由）。
    :param drain_timeout: ★ 杀掉之后**有界地**收尾多少秒（★ **不做无界等待** —— 见下）。
    :returns: `{"ok": bool, "result": ... | None, "error": str | None,
               "timed_out": bool, "seconds": float, "child_killed": bool, "kill": {...}, ...}`
        ★★ **`timed_out=True` 时子进程已被杀**，且**主进程与会话完好**
        （★ 这是与"同进程内加超时"的本质区别 —— 后者救不了挂住的线程）。

    ★★★★ 2026-10-04（接手轮）**两处加固**（★ 都来自真机实测 · 事实 526）：
      ① ★ **超时后改走 `taskkill /T /F`**（见 `_kill_tree`）—— ★ `TerminateProcess`
         对**卡在跨进程 COM 里**的子进程**不一定生效**（实测：子进程一直活着）；
      ② ★★ **超时后不再做无界等待** —— 原来那句 `proc.communicate()`（在 `subprocess.run`
         的超时分支里）会**无限期**等子进程的管道 ⇒ ★ 现场就是"**父进程一直不返回**"。
         ⇒ ★ 现在：杀掉之后**最多等 `drain_timeout` 秒**收残余输出，
         ★★ 无论收没收到**都返回**，并把 `drained=False` / `child_alive=True` **如实报出来** ✓
    """
    req = {
        "module": module,
        "function": function,
        "args": list(args or []),
        "kwargs": dict(kwargs or {}),
    }
    root = Path(__file__).resolve().parents[1]
    env_paths = [str(root), str(root / "scripts"), str(root / "mcp-server")]
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(env_paths + [env.get("PYTHONPATH", "")]).strip(
        os.pathsep
    )
    env["PYTHONIOENCODING"] = "utf-8"

    t0 = time.time()
    try:
        proc = subprocess.Popen(
            [python or sys.executable, "-c", _CHILD],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=str(root),
        )
    except OSError as exc:
        return {
            "ok": False,
            "result": None,
            ISOLATED_MARKER: True,
            "timed_out": False,
            "seconds": round(time.time() - t0, 1),
            "error": "子进程**起不来**（OSError）：%s" % (str(exc)[:200],),
        }
    try:
        try:
            out, err = proc.communicate(
                input=json.dumps(req, ensure_ascii=False), timeout=timeout
            )
        except subprocess.TimeoutExpired:
            kill = _kill_tree(proc.pid)  #: ★ ① 杀**整棵树**（实测有效的那条路）
            drained, alive = True, False
            try:
                out, err = proc.communicate(timeout=drain_timeout)  #: ★ ② **有界**收尾
            except subprocess.TimeoutExpired:
                #: ★★ 收不干净也**必须返回**（★ 原来就是在这里无限等下去的）
                out, err, drained = "", "", False
                alive = proc.poll() is None
            return {
                "ok": False,
                "result": None,
                ISOLATED_MARKER: True,
                "timed_out": True,
                "seconds": round(time.time() - t0, 1),
                "child_killed": bool(kill.get("ok")),
                "kill": kill,
                "drained": drained,
                "child_alive": alive,
                "error": (
                    "隔离执行超时（%.0fs）—— ★ 已用 `taskkill /T /F` 杀子进程"
                    "（child_killed=%s · 用时 %ss）；★ 会话完好。"
                    "若这是已知会弹模态框/会算很久的调用，说明前置不成立"
                    % (timeout, kill.get("ok"), kill.get("seconds"))
                ),
            }
    finally:
        if proc.poll() is None:
            _kill_tree(proc.pid)  #: ★ 兜底：任何异常路径都不留活子进程
    dt = round(time.time() - t0, 1)
    out = out or ""
    if "@@DSH_ISOLATED@@" not in out:
        return {
            "ok": False,
            "result": None,
            ISOLATED_MARKER: True,
            "timed_out": False,
            "seconds": dt,
            "child_killed": False,
            "drained": True,
            "child_alive": False,
            "error": "子进程没有回结果（★ 可能崩在导入阶段）：stdout=%r stderr=%r"
            % (out[-300:], (err or "")[-300:]),
        }
    payload = json.loads(out.split("@@DSH_ISOLATED@@", 1)[1])
    payload.update(
        {
            "timed_out": False,
            "seconds": dt,
            "drained": True,
            "child_alive": False,
            "child_returncode": proc.returncode,
        }
    )
    return payload
