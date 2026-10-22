"""★ 关掉**你自己开的**那一份 SolidWorks —— 只在确认那些文档都是自己开的时才动手。

（★ 依据：纪律 `资源与环境.md` §一「资源回收」的收工动作那条）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tools/reclaim_solidworks.py`（★ **卡死**那条路；★ 本脚本补的是**健康但该关**
# 那条）·
#         `scripts/sw_connect.py`（`connect_solidworks` / `get_com_member`）·
#         官方 `ISldWorks.ExitApp`（★ **0 参** —— `C:\swapi\types\ISldWorks\ExitApp.md`）
# 定位:   ★ **为什么要有它**：纪律那条要求「**用完你自己的就关掉你自己开的那个 SolidWo
#           rks**」+
#   「**只关你自己开的**、★ 不许误杀别的会话的」⇒ ★★ **而现有工具做不到这件事** ——
#     `tools/reclaim_solidworks.py` 的判据是「**探得通**就算健康、★ 不需要处置」⇒
#     ★★★ **实测（2026-10-04）**：一个 `responding=False`（半卡）的进程**探得通** ⇒
#       `--probe` 与 `--restart` 都回「会话健康，不需要处置」⇒ ★ **它不会关一个"健康的" SW** ✓
#   ★★★★ **判据（★ 保守优先 —— ★ "宁可不关，不可误杀"）**：
#     ★ ① 数 SolidWorks 家族进程：★ **多于一个 ⇒ 拒绝关闭**（★ 分不清哪个是我的）；
#     ★ ② 读那个进程里打开的每个文档的来源路径：★
#       **只要有一个不是本仓产物/不在本仓工作区 ⇒ 拒绝关闭**（★ 那可能是别人的）；
#     ★ ③ **判不出来（读不到文档清单）⇒ 拒绝**；
#     ★ ④ 三条都过才 `ExitApp`（★ 官方 0 参）✓
#   ★★★★★ **★ 只报不动**：★ 默认 `--probe` **零副作用**；★ 只有显式 `--close` 才关，
#     且**关闭前把判定过程全部打印出来**（★ 可复核）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ SolidWorks 家族（★ 判据按 exe 文件名，★ 不按窗口类名 —— ★ 与 `tools/sw_guard.py` 同
#: 源）
FAMILY = (
    "sldworks",
    "sldprocmon",
    "swcefsubproc",
    "cwbcbfmesh",
    "sldsurfacing",
    "sldworks_fs",
)


def family_processes() -> list:
    """★ 数 SolidWorks 家族进程（★ 用 WMI，★ 不改任何东西）。"""
    import subprocess

    ps = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.Name -match '^(%s)' } | "
        "Select-Object ProcessId,Name,ExecutablePath | ConvertTo-Json -Compress"
        % "|".join(FAMILY)
    )
    try:
        r = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        out = (r.stdout or "").strip()
        if not out:
            return []
        import json

        d = json.loads(out)
        return d if isinstance(d, list) else [d]
    except Exception as exc:  # noqa: BLE001
        print("  ⚠ 数进程失败: %s" % str(exc)[:120])
        return []


def open_docs_and_owner() -> dict:
    """★ 连上那个 SW，★ 读它打开的文档与**主人**（★ 只用读接口）。"""
    try:
        import sw_connect

        sw = sw_connect.connect_solidworks(wait_seconds=15)[0]
        titles = []
        #: ★ `ISldWorks.EnumDocuments2` / `GetDocuments` 都可以；★ 用最保守的那个
        docs = sw_connect.safe_get_com_member(sw, "GetDocuments")
        if docs:
            for d in list(docs):
                t = sw_connect.safe_get_com_member(d, "GetPathName")
                if not t:
                    t = sw_connect.safe_get_com_member(d, "GetTitle")
                titles.append(str(t or ""))
        return {"ok": True, "docs": titles}
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "docs": [],
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:150]),
        }


def is_mine(path: str) -> bool:
    """★ 判一个文档是不是**本仓的产物**。

    ★ 判据（★ 保守）：★ 路径在本仓工作区下、★ 或它是个**无路径的新文档**（★ `零件1` 那种 ——
    ★ 那是本轮刚建的、★ 还没存盘 ⇒ ★ 算自己的）✓
    ★★ 反过来说：★ 任何**本仓之外**的已有路径 ⇒ **不是自己的** ✓
    """
    if not path:
        return True  #: ★ 无路径 = 未存盘的新文档 ✓
    p = path.replace("/", "\\").lower()
    if p.startswith(str(REPO).lower()):
        return True
    #: ★ 无路径的标题（★ 如 `零件1`）⇒ 也算自己的（★ 未存盘）
    if "\\" not in p and ":" not in p:
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(
        description="关掉你自己开的 SolidWorks（★ 保守：宁可不关）"
    )
    ap.add_argument("--probe", action="store_true", help="只看（默认行为、零副作用）")
    ap.add_argument(
        "--close", action="store_true", help="四条判据全过才 ExitApp（★ 官方 0 参）"
    )
    a = ap.parse_args()

    procs = family_processes()
    #: ★★★★★★★ **修判据①（★ 第一版写错了）**：★ 第一版数的是**整个家族** ⇒ 实测报「**7
    #: 个**」
    #:   ⇒ ★★ **而其中 6 个是**同一个 SW 的子进程**（`sldProcMon` / `swCefSubProc`×3 /
    #:     `sldsurfacing` / `cwbcbfmesh`）⇒ ★★★ **⇒ 它把子进程当成了第二个会话** ✓
    #:   ⇒ ★ 正确判据：★ **只数 `SLDWORKS.exe` 主进程** —— ★ 因为这里要答的问题是
    #:     「**有几个 SW 会话**」、★ 不是「**有几个 SW 相关进程**」✓
    #:   ★★★★ **⚠ 而 AGENTS.md 那条「认 SolidWorks **家族**进程」是给**弹窗扫描**用的** ——
    #:     ★ 那里**要**覆盖全部子进程（★ 弹窗可能出在子进程上）；★ **这里相反** ✓
    #: ★★★★★ **⇒ 事实 51：★ 判据要贴合被测对象**（★ 同一个"家族"名单、★ 两个用途要**两种
    #: 数法**）✓
    mains = [p for p in procs if str(p.get("Name", "")).lower().startswith("sldworks")]
    print(
        "★ SolidWorks 家族进程 %d 个 · ★ 其中 **SLDWORKS.exe 主进程 %d 个**："
        % (len(procs), len(mains))
    )
    for p in procs:
        print("    PID=%-7s %s" % (p.get("ProcessId"), p.get("Name")))

    #: ── 判据 ①：★ 主进程多于一个 ⇒ 拒绝（★ 分不清哪个是我的）──────────────
    if len(mains) > 1:
        print(
            "★ 判据① **不过**：★ 有 %d 个 SLDWORKS.exe 主进程 ⇒ 分不清哪个是我的 ⇒ **不关**"
            % len(mains)
        )
        print("⇒ ★ 报出来交给人判（★ 宁可不关，不可误杀）")
        return 0
    if not mains:
        print("★ 没有 SolidWorks 主进程在跑 ⇒ 无需处置 ✓")
        return 0
    print(
        "★ 判据① 过：★ SLDWORKS.exe 主进程恰好 1 个（★ 那 %d 个是它的子进程）"
        % (len(procs) - len(mains))
    )

    info = open_docs_and_owner()
    if not info.get("ok"):
        print(
            "★ 判据③ **不过**：★ 读不到它打开的文档（%s）⇒ **不关**" % info.get("error")
        )
        return 0
    docs = info["docs"]
    mine = [d for d in docs if is_mine(d)]
    not_mine = [d for d in docs if not is_mine(d)]
    print("★ 判据② 读到的文档：★ 自己的 %s · **不是自己的 %s**" % (mine, not_mine))

    if not_mine:
        print(
            "★ 判据② **不过**：★ 有 %d 个文档不是本仓产物 ⇒ **那可能是别的会话的** ⇒ **不关**"
            % len(not_mine)
        )
        return 0
    print("★ 判据② 过：★ 打开的文档都是自己的")

    if not a.close:
        print("★ 判据①②③ 都过 ⇒ **可以关**（★ 加 `--close` 才真关）✓")
        return 0

    #: ★ 判据④：★ 真关（★ 官方 `ISldWorks.ExitApp` —— **0 参**）✓
    print("★ 判据④：★ 调 `ISldWorks.ExitApp`（★ 官方 0 参）")
    try:
        import sw_connect

        sw = sw_connect.connect_solidworks(wait_seconds=15)[0]
        sw_connect.get_com_member(sw, "ExitApp")
        print("★ 已调 ExitApp ✓")
    except Exception as exc:  # noqa: BLE001
        print("★ ExitApp 报错：%s: %s" % (type(exc).__name__, str(exc)[:150]))
        return 1

    import time

    time.sleep(4)
    left = family_processes()
    print(
        "★ 复核：★ 剩余家族进程 %d 个 ⇒ %s"
        % (len(left), "已关闭 ✓" if not left else "仍在")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
