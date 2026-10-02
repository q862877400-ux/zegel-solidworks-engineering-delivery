r"""@brief 小实验：**子进程能否安全地连到**同一个** SolidWorks 实例**（进程隔离方案的前提）。

## ★★★ 为什么必须先做这个实验（★ 不猜）
```
★ 用户指令：「**从代码层面解决**」（否掉了看门狗）⇒ ★ 我给出的正解是**进程隔离**：
    把"会弹模态框的调用"放进**可被杀的子进程** ⇒ 挂起不外溢。
★ 但这个方案有一个**前提**：★ **子进程能连到**同一个** SolidWorks 实例**。
⚠ 而**已知事实 24** 说：「运行时只能有**一个** SolidWorks MCP ——
  **多个进程抢同一 COM 连接会死锁**」⇒ ★★ **与本方案的前提直接冲突**！
⇒ ★★★ 所以**必须先实测**：① 能不能连上 ② 连上后**主进程还能不能用**
  ③ 子进程挂住时**主进程受不受影响**。★ 三条都要，缺一条方案就不成立。
```

## 三个实验（★ 都不碰仿真 ⇒ 不会弹框，安全）
```
① **能不能连**：子进程 `GetActiveObject("SldWorks.Application")` ⇒ 拿到对象吗？
② **主进程还活着吗**：子进程连过并做过调用之后，主进程再调一次（`RevisionNumber`）⇒ 还行吗？
③ **挂起是否外溢**：子进程**故意卡住**（sleep 很久）⇒ 主进程**立刻**调一次 ⇒ 被阻塞吗？
```

## ⚠ 安全
**只做只读调用**（`RevisionNumber` / `GetTitle`）· 不建文档、不跑仿真 ·
子进程**用 `subprocess` 起、带超时、超时就 `kill`**（★ 这正是方案的机制本身）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机小实验）
# 文件:   tools/experiment_subprocess_com.py
# 定位:   给 known-facts 176 的"进程隔离"方案**验前提**；产物 `output/subprocess-com.json`。
# 官方依据: 不适用（探的是"同一 COM 实例能否被两个进程用"这一事实）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\subprocess-com.json")

#: ★ 子进程要跑的一段：连 COM、读一个值、然后（可选）卡住
CHILD_CODE = r"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
import pythoncom, win32com.client as w
try:
    pythoncom.CoInitialize()
    app = w.GetActiveObject("SldWorks.Application")
    #: ★ `RevisionNumber` 是**属性**（迟到绑定下），不是方法 —— 加括号会 TypeError
    print("CHILD_OK rev=%s" % app.RevisionNumber)
    if "--hang" in sys.argv:
        print("CHILD_HANGING")
        sys.stdout.flush()
        time.sleep(3600)          #: ★ 故意卡住 —— 看主进程受不受影响
except Exception as e:
    print("CHILD_ERR %s: %s" % (type(e).__name__, str(e)[:120]))
"""


def _revision() -> tuple[bool, str]:
    """主进程调一次（★ 只读）。"""
    import win32com.client as w

    try:
        app = w.GetActiveObject("SldWorks.Application")
        return True, str(app.RevisionNumber)   #: ★ 属性，不加括号
    except Exception as exc:                                   # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:100])


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    child_file = Path(r"D:\AI\SW\output\_child_com.py")
    child_file.parent.mkdir(parents=True, exist_ok=True)
    child_file.write_text(CHILD_CODE, encoding="utf-8")

    #: 基线：主进程先调一次
    ok0, rev0 = _revision()
    ev["steps"]["main_before"] = {"ok": ok0, "revision": rev0}
    print("  [0] 主进程（子进程之前）: ok=%s rev=%s" % (ok0, rev0))

    #: ① ★ 子进程能不能连
    t0 = time.time()
    r1 = subprocess.run([sys.executable, str(child_file)], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=60)
    ev["steps"]["child_connect"] = {
        "ok": "CHILD_OK" in (r1.stdout or ""),
        "stdout": (r1.stdout or "").strip()[:200],
        "stderr": (r1.stderr or "").strip()[:200],
        "seconds": round(time.time() - t0, 1),
    }
    print("  [1] 子进程连接: %s" % json.dumps(ev["steps"]["child_connect"], ensure_ascii=False)[:200])

    #: ② ★ 子进程连过之后，主进程还能用吗
    ok1, rev1 = _revision()
    ev["steps"]["main_after_child"] = {
        "ok": ok1, "revision": rev1,
        "still_usable": bool(ok1 and rev0),
    }
    print("  [2] 主进程（子进程连过之后）: ok=%s rev=%s" % (ok1, rev1))

    #: ③ ★★ 子进程**卡住**时，主进程受不受影响（★ 这是方案的核心）
    print("  [3] ★ 起一个**故意卡住**的子进程，看主进程是否被阻塞…")
    p = subprocess.Popen([sys.executable, str(child_file), "--hang"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace")
    #: 等它先连上（读一行输出）
    line = ""
    deadline = time.time() + 30
    while time.time() < deadline:
        line = p.stdout.readline() if p.stdout else ""
        if line.strip():
            break
    ev["steps"]["hang_child_first_line"] = line.strip()[:80]
    print("        子进程首行: %r" % line.strip()[:60])

    t1 = time.time()
    ok2, rev2 = _revision()
    dt = round(time.time() - t1, 2)
    ev["steps"]["main_while_child_hung"] = {
        "ok": ok2, "revision": rev2, "seconds": dt,
        "blocked": dt > 5.0,
        "★": "★★ 若 ok 且 dt 很小 ⇒ **子进程卡住**不影响主进程** ⇒ 进程隔离方案成立",
    }
    print("  [4] ★★ 子进程卡住时主进程: ok=%s rev=%s 用时=%ss ⇒ %s"
          % (ok2, rev2, dt, "**没被阻塞**" if not ev["steps"]["main_while_child_hung"]["blocked"]
             else "**被阻塞了**"))

    #: 收尾：杀掉卡住的子进程（★ 这正是方案的机制）
    try:
        p.kill()
        p.wait(timeout=10)
        ev["steps"]["kill_child"] = {"ok": True, "★": "★ 子进程可被 kill ⇒ 挂起可弃"}
        print("  [5] 卡住的子进程已 kill ✓")
    except Exception as exc:                                   # noqa: BLE001
        ev["steps"]["kill_child"] = {"ok": False, "err": str(exc)[:80]}

    #: 杀完之后主进程还能用吗
    ok3, rev3 = _revision()
    ev["steps"]["main_after_kill"] = {"ok": ok3, "revision": rev3}
    print("  [6] 主进程（kill 子进程之后）: ok=%s rev=%s" % (ok3, rev3))

    #: ★ 判读
    ev["steps"]["verdict"] = {
        "child_can_connect": ev["steps"]["child_connect"]["ok"],
        "main_unaffected_by_hung_child": ok2 and not ev["steps"]["main_while_child_hung"]["blocked"],
        "child_killable": ev["steps"]["kill_child"]["ok"],
        "★": "★ 三条都为真 ⇒ **进程隔离方案成立**（子进程能连、卡住不阻塞主进程、可被杀）",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ── 判读 ──")
    print("     %s" % json.dumps(ev["steps"]["verdict"], ensure_ascii=False)[:280])
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
