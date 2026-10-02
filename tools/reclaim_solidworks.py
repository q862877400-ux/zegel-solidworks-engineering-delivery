"""★ **SolidWorks 会话解卡**：探连接 → 判定能不能安全重启 → 重启 → 复验。

## 一、为什么要有它（★ 2026-10-01 本会话卡了 **7 轮**）
```
★ 轮 24：我在**主进程**调 `create_mesh`（★ 还用了过大的 `element_size = 1999.4`）
   ⇒ 子进程卡住 620 s 以上；★ **杀掉子进程之后 SolidWorks 也连不上了**（连接阻塞 >600 s）。
★★ 此后**连续 7 轮**每轮开头探测都是「`Responding=False` + `SW_MUTEX_TIMEOUT`」——
   ★ 而**每轮都只是"再探一次"**，★ 没有去**处置**它。
⇒ ★★★ **轮 31 才动手**：★ 清残留 python → `Stop-Process` SW → 重连 ⇒ ★ **`connect: True` · `revision 34.4.1`** ✓
   ⇒ ★ **即：★ 卡死的 SW 只能靠重启，★ 而"再探一次"永远解不了**（★ 与事实 53 同族：
     ★ 同一个状态反复观察 ≠ 处置）。
```

## 二、★★ 安全前提（★ 它不是"随便杀"）
```
★ 重启会**丢掉未保存的改动** ⇒ 本脚本**先判定**：
   ① 列出 SW 主窗口标题里的**打开文档**；
   ② 逐个判定它**是不是本会话自己的临时件**（★ 默认：`零件<N>` / `Part<N>` /
      ★ 以及我们探针专用的前缀 `MCP_`）；
   ③ ★★ **只要有一个"不是自己的"文档开着 ⇒ 拒绝重启**，★ 打印它并要求人工处置。
⇒ ★ 依据：全局纪律「**Reclaim GUIs, COM objects, long-lived processes each turn**」
  与「**不删用户数据**」—— ★ **回收自己开的**是允许的，**动用户的**不是。
```

## 三、★ 用法
```
python tools/reclaim_solidworks.py --probe          # 只探（★ 不动任何东西）
python tools/reclaim_solidworks.py --restart        # 探不通且文档安全 ⇒ 重启
python tools/reclaim_solidworks.py --restart --force  # 忽略文档判定（★ 明确知道自己在做什么时）
```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/reclaim_solidworks.py
# 定位:   把"卡死的 SolidWorks 该怎么办"机械化（★ 本会话卡 7 轮的直接产物）。
# 官方依据: 不适用（★ 用 `sw_connect.connect_solidworks` + Win32 进程操作）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 本工具会**结束进程** ⇒ 只在自己的临时件开着时才允许（脚本自己判定，见 `_our_own_docs`）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

#: ★ 我们自己的临时件名字形态（★ 探针建的都是这些）
_OURS = re.compile(r"(零件|Part)\d+|^MCP_", re.I)


def _sw_processes() -> list[tuple[int, str, bool]]:
    """⇒ `[(pid, 主窗口标题, 是否响应)]`（★ 用 PowerShell 取，避免额外依赖）。"""
    ps = ("Get-Process -Name SLDWORKS -ErrorAction SilentlyContinue | "
          "ForEach-Object { \"$($_.Id)`t$($_.Responding)`t$($_.MainWindowTitle)\" }")
    try:
        proc = subprocess.run(["pwsh", "-NoProfile", "-Command", ps],
                              check=False, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=60,
                              stdin=subprocess.DEVNULL)
    except (subprocess.TimeoutExpired, OSError):
        return []
    out = []
    for line in (proc.stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].strip().isdigit():
            out.append((int(parts[0]), parts[2].strip(), parts[1].strip().lower() == "true"))
    return out


def _open_docs(title: str) -> list[str]:
    """★ 从主窗口标题里取 `[...]` 里的文档名（★ 去掉末尾的 `*` = 未保存标记）。"""
    return [m.strip().rstrip("*").strip() for m in re.findall(r"\[([^\]]+)\]", title)]


def _our_own_docs(docs: list[str]) -> tuple[list[str], list[str]]:
    """⇒ `(自己的, 不是自己的)` —— ★ 后者非空就**不许重启**。"""
    mine, others = [], []
    for d in docs:
        (mine if _OURS.search(d) else others).append(d)
    return mine, others


def _probe(timeout_s: int = 20) -> dict:
    """★ 试连一次（★ 在**子进程**里跑 ⇒ 卡住也不会拖死本进程）。"""
    code = (
        "import sys;sys.stdout.reconfigure(encoding='utf-8');"
        "sys.path[:0]=[r'%s',r'%s'];" % (REPO_ROOT, REPO_ROOT / "scripts") +
        "import sw_connect;"
        "sw=sw_connect.connect_solidworks(wait_seconds=8)[0];"
        "print('CONNECT_OK' if sw is not None else 'CONNECT_NONE')"
    )
    try:
        proc = subprocess.run([sys.executable, "-c", code], check=False, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=timeout_s, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"ok": False, "why": "★ 探测在 %d s 内未返回 ⇒ 会话卡死" % timeout_s}
    text = (proc.stdout or "") + (proc.stderr or "")
    if "CONNECT_OK" in text:
        return {"ok": True, "why": "已连上"}
    return {"ok": False, "why": "★ 未连上：%s" % " ".join(text.split())[-160:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="只探（默认行为）")
    ap.add_argument("--restart", action="store_true", help="探不通且文档安全时重启")
    ap.add_argument("--force", action="store_true", help="忽略文档判定")
    args = ap.parse_args()

    procs = _sw_processes()
    print("  SolidWorks 进程 %d 个：" % len(procs))
    for pid, title, resp in procs:
        docs = _open_docs(title)
        mine, others = _our_own_docs(docs)
        print("    PID=%s responding=%s" % (pid, resp))
        print("      打开文档=%s ⇒ 自己的 %s · **不是自己的 %s**"
              % (docs or "<无>", mine or "[]", others or "[]"))

    r = _probe()
    print("  探测: %s（%s）" % ("✓ 通" if r["ok"] else "✗ 不通", r["why"]))
    if r["ok"]:
        print("  ⇒ ★ 会话健康，不需要处置。")
        return 0
    if not args.restart:
        print("  ⇒ ★ 要重启请加 `--restart`（★ 本脚本会先判定打开的文档是不是自己的）。")
        return 1

    #: ★★ 安全判定：不是自己的文档一个都不许开着
    all_others: list[str] = []
    for _pid, title, _resp in procs:
        _mine, others = _our_own_docs(_open_docs(title))
        all_others += others
    if all_others and not args.force:
        print("  ✗ **拒绝重启**：有**不是本会话**的文档开着：%s" % all_others)
        print("     ★ 依据：只回收**自己开的**资源；动用户的文档要人工决定（★ 或加 `--force`）。")
        return 2

    print("  ⇒ 重启（先清残留 python，再结束 SW，再重连）…")
    subprocess.run(["pwsh", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name LIKE 'python%'\" | "
                    "Where-Object { $_.CommandLine -match 'sw_connect|probe|create_mesh' } | "
                    "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"],
                   check=False, capture_output=True, text=True, encoding="utf-8",
                   errors="replace", timeout=90, stdin=subprocess.DEVNULL)
    time.sleep(2)
    subprocess.run(["pwsh", "-NoProfile", "-Command",
                    "Get-Process -Name SLDWORKS -ErrorAction SilentlyContinue | "
                    "Stop-Process -Force -ErrorAction SilentlyContinue"],
                   check=False, capture_output=True, text=True, encoding="utf-8",
                   errors="replace", timeout=90, stdin=subprocess.DEVNULL)
    time.sleep(8)
    r2 = _probe(timeout_s=90)
    print("  重启后探测: %s（%s）" % ("✓ 通" if r2["ok"] else "✗ 不通", r2["why"]))
    return 0 if r2["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
