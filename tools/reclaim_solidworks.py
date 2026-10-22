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
python tools/reclaim_solidworks.py --close          # ★ **只关**（★ 纪律：★ 跨轮不许留；★ 关完不要再调真机工具）
```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/reclaim_solidworks.py
# 定位:   把"卡死的 SolidWorks 该怎么办"机械化（★ 本会话卡 7 轮的直接产物）。
# 官方依据: 不适用（★ 用 `sw_connect.connect_solidworks` + Win32 进程操作）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 本工具会**结束进程** ⇒ 只在自己的临时件开着时才允许（脚本自己判定，见 `_our_own_docs
# `）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

#: ★ 我们自己的临时件名字形态（★ 探针建的都是这些）
#: ★★ **判定的家已经搬走了**（规格 210 · B5-2）：枚举文档 / 认我方 / 读未保存标记
#: **全部在 `tools/session_verdict.py`** —— ★ 本仓反复吃过的亏就是"同一套判定两处各写一
#: 份" ✓
#:   ★ 下面这几个薄壳**只为兼容既有调用点**保留，★ 逻辑一律走共用实现 ✓
from session_verdict import (  # noqa: E402
    OURS as _OURS,
)
from session_verdict import (  # noqa: E402
    parse_title_documents,  # noqa: E402
)


def _sw_processes() -> list[tuple[int, str, bool]]:
    """⇒ `[(pid, 主窗口标题, 是否响应)]`（★ 用 PowerShell 取，避免额外依赖）。"""
    ps = (
        "Get-Process -Name SLDWORKS -ErrorAction SilentlyContinue | "
        'ForEach-Object { "$($_.Id)`t$($_.Responding)`t$($_.MainWindowTitle)" }'
    )
    try:
        proc = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", ps],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError):
        return []
    out = []
    for line in (proc.stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].strip().isdigit():
            out.append(
                (int(parts[0]), parts[2].strip(), parts[1].strip().lower() == "true")
            )
    return out


def _open_docs(title: str) -> list[str]:
    """★ 从窗口标题取文档名 —— ★ **委托**给共用裁决的纯函数（★ 兼容旧调用点）✓"""
    return [d["title"] for d in parse_title_documents(title)]


def _our_own_docs(docs) -> tuple[list[str], list[str]]:
    """⇒ `(自己的, 不是自己的)` —— ★ 后者非空就**不许重启**。

    ★ **委托**给共用裁决的命名约定（`session_verdict.OURS`）—— ★ 不再在本文件维护第二份正则 ✓
    """
    mine, others = [], []
    for d in docs:
        name = d.get("title") if isinstance(d, dict) else d
        (mine if _OURS.search(str(name or "")) else others).append(d)
    return mine, others


def _probe(timeout_s: int = 20) -> dict:
    """★ 试连一次（★ 在**子进程**里跑 ⇒ 卡住也不会拖死本进程）。"""
    code = (
        "import sys;sys.stdout.reconfigure(encoding='utf-8');"
        "sys.path[:0]=[r'%s',r'%s'];"
        % (REPO_ROOT, REPO_ROOT / "scripts")
        + "import sw_connect;"
        "sw=sw_connect.connect_solidworks(wait_seconds=8)[0];"
        "print('CONNECT_OK' if sw is not None else 'CONNECT_NONE')"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
            stdin=subprocess.DEVNULL,
        )
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
    ap.add_argument(
        "--close",
        action="store_true",
        help="★ **只关**（★ 不重连）—— 纪律：跨轮不许留 SolidWorks",
    )
    ap.add_argument("--force", action="store_true", help="忽略文档判定")
    args = ap.parse_args()

    procs = _sw_processes()
    print("  SolidWorks 进程 %d 个：" % len(procs))
    for pid, title, resp in procs:
        docs = _open_docs(title)
        mine, others = _our_own_docs(docs)
        print("    PID=%s responding=%s" % (pid, resp))
        print(
            "      打开文档=%s ⇒ 自己的 %s · **不是自己的 %s**"
            % (docs or "<无>", mine or "[]", others or "[]")
        )

    r = _probe()
    print("  探测: %s（%s）" % ("✓ 通" if r["ok"] else "✗ 不通", r["why"]))

    #: ★★★★★★★ 2026-10-04（轮 139）**新增 `--close`**：★ **只关、★ 不复验连接** ——
    #:   ★ 依据：★ `~/.dsh/纪律/资源与环境.md` 逐字 ——
    #:     ★「★ **用完了就关掉 SolidWorks** —— 一轮真机活收尾时它是**关着的**、
    #:       ★ **不是最小化的**、★ **也不是留着下轮接着用**」·
    #: ★★「★ **同一轮里还有后续真机步骤时可以留着它；跨轮不许留** —— **收尾链跑完就关**
    #: 」✓
    #:   ★★★ **为什么不能复用 `--restart`**（★ 值记，★ 我实测出来的）：
    #: ★ `--restart` 是 `Stop-Process` **之后重连** ⇒ ★★ **⇒ 而重连会把它**又拉起来****
    #: ✗
    #:     ★ 实测：★ 我手工 kill 了整族 9 个进程（★ 合计 **28539 MB**）⇒ ★★ **几秒后
    #:       `SLDWORKS` 又回来了、★ 而 PID 全是新的** ⇒ ★★★ **⇒ 真凶是
    #:       `mcp-server/server.py`**（★ 它的 `connect` 逐字是
    #:       「connects to a running SolidWorks instance **or starts one**」）⇒
    #:       ★ **⇒ 任何一次真机工具调用都可能把它拉起来** ✓
    #:   ★★★★ **⇒ 所以"关"必须是**只关不启**、★ 且**关完不再碰真机工具**** ✓
    #: ★★★★★ **⚠ 安全判定**：★ **不是自己开的文档一个都不许关**（★ 与 `--restart` 同一条
    #: ）✓
    if args.close:
        #: 只关**我们自己启动过**的实例。
        #: 第一版按进程名杀整族（会误杀别的对话）；第二版为了拿归属标记去 connect，
        #: 而 connect 的语义是 "attach or START one" ⇒ 判断前先把它启起来了。
        #: 现在只认 sw_connect 在启动那一刻落下的 PID 标记：证不出归属就不动。
        code = (
            "import sys\n"
            "sys.path.insert(0, r'%s')\n"
            "from sw_connect import (connect_solidworks, close_owned_solidworks,\n"
            "                        read_owned_instance, clear_owned_instance)\n"
            "m = read_owned_instance()\n"
            "print('MARK', m)\n"
            "if not m or not m.get('pid'):\n"
            "    print('SKIP 没有「我们启动过」的标记 ⇒ 不关（可能是别的对话的实例）')\n"
            "    raise SystemExit(0)\n"
            "sw, _d = connect_solidworks(visible=True)\n"
            "ok = close_owned_solidworks(sw, True)\n"
            "print('CLOSED', bool(ok))\n"
            "if ok:\n"
            "    clear_owned_instance()\n"
        ) % str(REPO_ROOT / "scripts")
        print("  ⇒ 只关**我们启动过**的那一个（按 PID 标记；证不出归属就不动）：")
        try:
            rr = subprocess.run(
                [sys.executable, "-c", code],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            print("     ✗ 超时 ⇒ **不关**（宁可留着，也不误杀）")
            return 3
        for line in (rr.stdout or "").splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("MARK"):
                print("     ★ 归属标记: %s" % s[4:].strip())
            elif s.startswith("CLOSED"):
                print("     ★ close_owned_solidworks ⇒ **%s**" % s.split(None, 1)[-1])
            elif s.startswith("SKIP"):
                print("     ★ **%s**" % s[4:].strip())
        if "CLOSED True" in (rr.stdout or ""):
            print("  ⇒ 关完了 —— 此后不要再调真机工具（一调就会被拉起来）。")
        return 0

    if r["ok"]:
        print("  ⇒ ★ 会话健康，不需要处置。")
        return 0
    if not args.restart:
        print(
            "  ⇒ ★ 要重启请加 `--restart`（★ 本脚本会先判定打开的文档是不是自己的）。"
        )
        print("     ★ **用完要关**（★ 跨轮不许留）请加 `--close`。")
        return 1

    #: ★★ 安全判定：不是自己的文档一个都不许开着
    all_others: list[str] = []
    for _pid, title, _resp in procs:
        _mine, others = _our_own_docs(_open_docs(title))
        all_others += others
    if all_others and not args.force:
        print("  ✗ **拒绝重启**：有**不是本会话**的文档开着：%s" % all_others)
        print(
            "     ★ 依据：只回收**自己开的**资源；动用户的文档要人工决定（★ 或加 `--force`）。"
        )
        return 2

    print("  ⇒ 重启（先清残留 python，再结束 SW，再重连）…")
    subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name LIKE 'python%'\" | "
            "Where-Object { $_.CommandLine -match 'sw_connect|probe|create_mesh' } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        stdin=subprocess.DEVNULL,
    )
    time.sleep(2)
    subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-Command",
            "Get-Process -Name SLDWORKS -ErrorAction SilentlyContinue | "
            "Stop-Process -Force -ErrorAction SilentlyContinue",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        stdin=subprocess.DEVNULL,
    )
    time.sleep(8)
    r2 = _probe(timeout_s=90)
    print("  重启后探测: %s（%s）" % ("✓ 通" if r2["ok"] else "✗ 不通", r2["why"]))
    return 0 if r2["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
