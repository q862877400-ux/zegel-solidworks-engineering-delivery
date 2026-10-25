"""★ **通用命令护栏**：跑任何命令时，把「弹窗」变成命令输出的一部分。

## 为什么要有它（业主 2026-10-26）

> 你运行一个软件或者运行了一个命令之后，它报错弹窗了，你却发现不了。
> 我怎么能够给你弄一个长效的机制，让你不管是在这个项目还是在别的地方……
> 弹窗报错了你能第一时间发现？

真实事故：我起 `psr.exe /start` 时**上一个 PSR 还在跑**，它弹了
「步骤记录器的某个实例正在运行中。」——然后我就**干等超时**，
因为命令没有输出、也没有退出。

⇒ 护栏把三件事变成自动的：
  ① 命令**开始时**先报告「上一轮之后新出现的弹窗」（遗留弹窗不会漏）
  ② 命令**运行中**每 300ms 扫一次新弹窗；一出现就把**文字 + 截图**抓下来，
     并**杀掉子进程树**（弹窗在等人点，等下去只会浪费时间）
  ③ 结束一定打印 `VERDICT:` 行 —— 我判读输出时**不可能看不到**

## 用法

```bash
python -B tools/guard_run.py --timeout 300 -- python -B tools/demo_capture.py --stop
python -B tools/guard_run.py --timeout 60  -- pwsh -File tools/round_chain.ps1
python -B tools/guard_run.py --since            # 只看「上一轮之后出现的弹窗」
```

## 判读

```
VERDICT: OK                    命令正常结束
VERDICT: EXIT 3                命令退出码 3（没有弹窗）
VERDICT: DIALOG 步骤记录器的…   被弹窗挡住，子进程已杀；截图在 output/dialogs/
```
"""
from __future__ import annotations

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
OUT = R / "output" / "dialogs"
LOG = OUT / "events.jsonl"
SEEN = OUT / "seen.json"

sys.path.insert(0, str(R / "tools"))

u = ctypes.windll.user32
_pol = 0.3


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 通用命令护栏）
# 文件:   tools/guard_run.py
# 定位:   跑任意命令时检测新弹窗：开跑先报遗留弹窗、运行中抓文字+截图并杀子进程、
#          结束必打 VERDICT。起因：2026-10-26 我因 PSR 实例冲突弹窗而干等超时。
# 官方依据: Win32 User32（EnumWindows/GetWindowTextW/GetClassNameW/EnumChildWindows）
#          与 subprocess 进程管理；截图复用 tools/sw_screenshot.capture
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


#: ★ 窗口助手复用 `tools/sw_screenshot.py` —— 复制一份会让「同函数体跨文件」克隆组上升
from sw_screenshot import _cls, _title  # noqa: E402

_text = _title


def _kids(h: int, limit: int = 6) -> list:
    out = []

    def cb(ch, _l):
        if len(out) >= limit:
            return True
        t = _text(ch)
        if t:
            out.append(t[:120])
        return True

    u.EnumChildWindows(
        h,
        ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(cb),
        0,
    )
    return out


def _dialogs() -> dict:
    """当前所有可见 `#32770` 窗口 → {hwnd: {title, kids}}。"""
    out = {}

    def cb(h, _l):
        if u.IsWindowVisible(h) and _cls(h) == "#32770":
            out[int(h)] = {"title": _text(h), "kids": _kids(int(h))}
        return True

    u.EnumWindows(
        ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(cb), 0
    )
    return out


def _shot(tag: str) -> str:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / ("%s-%s.png" % (time.strftime("%H%M%S"), tag))
    try:

        from sw_screenshot import capture, find_sw_window

        hwnd = find_sw_window()
        if hwnd:
            capture(hwnd, p)
    except Exception:  # noqa: BLE001
        pass
    return str(p) if p.is_file() else ""


def _seen_read() -> set:
    if SEEN.is_file():
        try:
            return set(json.loads(SEEN.read_text(encoding="utf-8")).get("titles", []))
        except Exception:  # noqa: BLE001
            return set()
    return set()


def _seen_write(titles: set) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SEEN.write_text(json.dumps({"titles": sorted(titles)[-80:]}, ensure_ascii=False),
                    encoding="utf-8")


def _preamble() -> list:
    """报告「上一轮之后出现、还没被我看见过」的弹窗。"""
    prev = _seen_read()
    cur = _dialogs()
    fresh = [(h, d) for h, d in cur.items()
             if ("%s|%s" % (d["title"], " / ".join(d["kids"]))) not in prev]
    if fresh:
        print("⚠ 上次之后有 %d 个弹窗还开着：" % len(fresh))
        for h, d in fresh:
            print("   「%s」 %s" % (d["title"], " / ".join(d["kids"])[:120]))
            print("   ⇒ 先处理掉再跑新命令（或加 --dismiss 让我点掉）")
    return fresh


def _record(kind: str, dlg: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {
        "t": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": kind,
        "title": dlg.get("title"),
        "kids": dlg.get("kids"),
        "shot": _shot("dlg"),
    }
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run(cmd: list, timeout_s: float, kill_on_dialog: bool = True) -> int:
    base = set(_dialogs())
    _preamble()
    t0 = time.time()
    try:
        #: ★ 必须把子进程的 stdout/stderr **接到本进程的 stdout**：
        #:   否则在 PowerShell 管道里（| Select-Object）子进程输出会丢，
        #:   我只能看到 VERDICT、看不到真实错误（2026-10-26 实测踩过）。
        proc = subprocess.Popen(  # noqa: S603
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=sys.stdout,
            stderr=sys.stdout,
            creationflags=0x08000000,
        )
    except FileNotFoundError:
        print("VERDICT: EXIT 127（命令不存在：%s）" % cmd[0])
        return 127

    hit = None
    while True:
        time.sleep(_pol)
        new = {h: d for h, d in _dialogs().items() if h not in base}
        if new:
            h, d = next(iter(new.items()))
            _record("during", d)
            hit = d
            print("★ 检测到弹窗：「%s」" % d.get("title"))
            print("   内容：%s" % (" / ".join(d.get("kids") or [])[:200]))
            if kill_on_dialog:
                try:
                    subprocess.run(
                        ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                        creationflags=0x08000000, timeout=30, check=False,
                    )
                except Exception:  # noqa: BLE001
                    pass
            break
        if proc.poll() is not None:
            break
        if time.time() - t0 > timeout_s:
            print("★ 超时 %.0fs，结束子进程" % timeout_s)
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    creationflags=0x08000000, timeout=30, check=False,
                )
            except Exception:  # noqa: BLE001
                pass
            print("VERDICT: EXIT 124（超时）")
            return 124

    rc = proc.poll()
    if hit is not None:
        print("VERDICT: DIALOG %s" % (hit.get("kids") or [hit.get("title")])[0][:100])
        return 1
    print("VERDICT: %s" % ("OK" if rc == 0 else "EXIT %s" % rc))
    return rc or 0


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 0
    if "--since" in argv:
        _preamble()
        return 0
    timeout_s = 300.0
    if "--timeout" in argv:
        k = argv.index("--timeout")
        timeout_s = float(argv[k + 1])
        argv = argv[:k] + argv[k + 2:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    if not argv:
        print("★ 没有要跑的命令（用法：-- <命令…>）")
        return 2
    return run(argv, timeout_s)


if __name__ == "__main__":
    raise SystemExit(main())
