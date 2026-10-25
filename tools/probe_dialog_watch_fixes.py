"""★ 验证第 46 轮两个修复：日志去重 + 报告器结束进程。

## 为什么必须验

用户报「一堆 Rx 窗口」，查证结果是：监控**在跑也抓到了**，但
① `SLDEXITAPP.exe` 的 CEIP 错误框**点掉即重弹**（2 分钟 13 万行）；
② 日志**没去重**（254 MB）。

改完后必须证明这两件事真的变了 —— 否则「改了」只是改字面。

## 怎么验（不依赖真弹窗）

- **去重**：直接调 `_append()` 同一个签名 5 次 ⇒ `events.jsonl` 只应多 **1** 行。
- **结束进程**：起一个 `python -c "import time; time.sleep(60)"` 冒充报告器 PID，
  调 `_terminate_process()` ⇒ 进程应真的消失。

★ 第二条用的是「任意进程」而不是真的 SLDEXITAPP —— 因为不该为了测试去
  crash SolidWorks 复现它。函数行为与目标进程无关（只吃 PID），所以这样验是充分的。
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 弹窗监控修复的自证）
# 文件:   tools/probe_dialog_watch_fixes.py
# 定位:   验证 `sw_dialog_watch` 的两处修复：日志去重、报告器进程结束。
# 官方依据: 不适用（纯本地：文件行数 + 进程存活）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sw_dialog_watch  # noqa: E402


def _lines(p: Path) -> int:
    try:
        with p.open("rb") as fh:
            return sum(1 for _ in fh)
    except FileNotFoundError:
        return 0


def main() -> int:
    ev: dict = {"probe": "dialog-watch-fixes"}
    events = sw_dialog_watch.EVENTS

    #: ① 去重：同一签名连写 5 次
    sw_dialog_watch._recent.clear()
    before = _lines(events)
    sample = {
        "kind": "dialog",
        "exe": "SLDEXITAPP.exe",
        "class": "#32770",
        "title": "SOLIDWORKS Design 错误报告",
        "controls": [
            {"class": "Button", "text": "确定"},
            {"class": "Static", "text": "在尝试发送客户体验改善计划数据时发生错误。"},
        ],
    }
    for _ in range(5):
        sw_dialog_watch._append(dict(sample, at=sw_dialog_watch._now()))
    after = _lines(events)
    ev["dedupe"] = {"before": before, "after": after, "added": after - before}
    print("① 去重：连写 5 次 ⇒ 文件增加 %d 行（期望 1）" % (after - before))

    #: ② 结束进程：起一个假报告器
    victim = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(120)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.5)
    alive_before = sw_dialog_watch._pid_alive(victim.pid)
    killed = sw_dialog_watch._terminate_process(victim.pid)
    #: ★ TerminateProcess 返回 True 后进程还要一点时间才真正退出
    #:   ⇒ 用 Popen.wait() 等它真的结束（比轮询 OpenProcess 可靠：
    #:     句柄仍在内核里时 OpenProcess 可能仍成功）。
    try:
        victim.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    alive_after = victim.poll() is None
    ev["terminate"] = {
        "pid": victim.pid,
        "alive_before": alive_before,
        "terminate_ret": killed,
        "alive_after": alive_after,
    }
    print(
        "② 结束进程：PID %d 之前活着=%s → terminate=%s → 之后活着=%s"
        % (victim.pid, alive_before, killed, alive_after)
    )

    ev["ok"] = bool((after - before) == 1 and killed and not alive_after)
    ev["conclusion"] = (
        "★ 两处修复都生效（去重 1 行；报告器进程被结束）"
        if ev["ok"]
        else "★ 未达：见 dedupe / terminate 两段"
    )
    print(ev["conclusion"])
    dest = R / "output" / "dialog-watch-fixes.json"
    dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("   证据已写：%s" % dest)
    return 0 if ev["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
