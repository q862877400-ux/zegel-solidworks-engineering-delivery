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
# 官方依据: 不适用（纯进程隔离）；★ 判据来自 `tools/experiment_subprocess_com.py` 的真机三条
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

__all__ = ["run_isolated", "ISOLATED_MARKER"]

#: ★★ 隔离执行的**标记** —— 调用方据此知道"这条结果来自子进程"
ISOLATED_MARKER = "__isolated__"

#: 子进程里跑的蹦床代码：把模块/函数/参数/关键字显式传进去，结果以 JSON 从 stdout 回。
_CHILD = r'''
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
'''


def run_isolated(module: str, function: str, *, args: list | None = None,
                 kwargs: dict | None = None, timeout: float = 180.0,
                 python: str | None = None) -> dict[str, Any]:
    """在**可被杀的子进程**里调用 `scripts.<module>.<function>`。

    :param module: **点分模块路径**，如 `"scripts.sw_simulation"`（★ 见下例）。
    :param function: 函数名。
    :param args/kwargs: 实参（★ 必须**可 JSON 化** —— 因为要跨进程传）。
    :param timeout: 秒。★ **超时 = 杀子进程**（这正是本模块存在的理由）。
    :returns: `{"ok": bool, "result": ... | None, "error": str | None,
               "timed_out": bool, "seconds": float, "...": ...}`
        ★★ **`timed_out=True` 时子进程已被杀**，且**主进程与会话完好**
        （★ 这是与"同进程内加超时"的本质区别 —— 后者救不了挂住的线程）。
    """
    req = {"module": module, "function": function,
           "args": list(args or []), "kwargs": dict(kwargs or {})}
    root = Path(__file__).resolve().parents[1]
    env_paths = [str(root), str(root / "scripts"), str(root / "mcp-server")]
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(env_paths + [env.get("PYTHONPATH", "")]).strip(os.pathsep)
    env["PYTHONIOENCODING"] = "utf-8"

    t0 = time.time()
    try:
        proc = subprocess.run(
            [python or sys.executable, "-c", _CHILD],
            input=json.dumps(req, ensure_ascii=False),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, env=env, cwd=str(root),
        )
    except subprocess.TimeoutExpired:
        #: ★★★ **超时 ⇒ 子进程已被 subprocess 杀掉** ⇒ 挂起**不外溢**
        return {"ok": False, "result": None, ISOLATED_MARKER: True,
                "timed_out": True, "seconds": round(time.time() - t0, 1),
                "error": "隔离执行超时（%.0fs）—— ★ 子进程已被杀，会话完好；"
                         "若这是已知会弹模态框的调用，说明前置条件不成立" % timeout}
    dt = round(time.time() - t0, 1)
    out = proc.stdout or ""
    if "@@DSH_ISOLATED@@" not in out:
        return {"ok": False, "result": None, ISOLATED_MARKER: True, "timed_out": False,
                "seconds": dt,
                "error": "子进程没有回结果（★ 可能崩在导入阶段）：stdout=%r stderr=%r"
                         % (out[-300:], (proc.stderr or "")[-300:])}
    payload = json.loads(out.split("@@DSH_ISOLATED@@", 1)[1])
    payload.update({"timed_out": False, "seconds": dt,
                    "child_returncode": proc.returncode})
    return payload
