"""@brief 检查**工作区根**有没有会遮蔽依赖包的模块（`mcp.py` 这类）。

## 为什么需要它（实测撞上的真实陷阱）
Python 把**当前目录**放在 `sys.path[0]`。工作区根 `D:\\AI\\SW\\` 里有 ~600 个散落的
`.py` 脚本，其中**有一个 `mcp.py`** ⇒ 任何以该目录为 CWD 的 Python 进程里
`import mcp` **拿到的是那个脚本**，不是真的 mcp 包：

    ModuleNotFoundError: No module named 'mcp.server'; 'mcp' is not a package

**⇒ 后果：`mcp-server/server.py` 在 `D:\\AI\\SW` 这个 CWD 下**根本 import 不了**，
而错误信息（`'mcp' is not a package`）**看不出是「被本地文件遮蔽」**。**

## 它查什么
对 `mcp-server/server.py` 用到的**顶层第三方包**，检查工作区根有没有**同名**
`.py` 文件或目录 ⇒ 有就是遮蔽风险。

**⚠ 不自动删任何东西**（工作区里的脚本是历史产物，删不删由人定）—— **只报告 + 给修法。**

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（静态检查工具）
# 文件:   mcp-server/server.py 的 import（`from mcp.server.fastmcp import FastMCP`）
# 定位:   T-011 接线实测时撞上的陷阱；把「CWD 遮蔽」做成可查项。
# 官方签名依据: 不适用（Python 的 `sys.path[0]` 语义）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 纯静态检查（只列目录与文件名），**不 import 任何东西**。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = Path(Path(__file__).resolve().parents[1])
SERVER = ROOT / "mcp-server" / "server.py"

#: 从 server.py 里抽顶层第三方包名（只取第一段）
IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([a-zA-Z_][\w]*)", re.M)

#: 标准库与本地模块不算（本仓库自己的包名也不必查）
SKIP = {
    "scripts",
    "tool_registry",
    "register_capabilities",
    "typing",
    "os",
    "sys",
    "json",
    "re",
    "time",
    "pathlib",
    "dataclasses",
    "enum",
    "abc",
    "functools",
    "collections",
    "itertools",
    "contextlib",
    "traceback",
    "logging",
    "math",
    "subprocess",
    "tempfile",
    "shutil",
    "io",
    "warnings",
    "asyncio",
    "types",
    "importlib",
    "inspect",
    "datetime",
    "uuid",
    "hashlib",
    "base64",
    "threading",
    "queue",
    "copy",
    "textwrap",
    "argparse",
    "glob",
    "platform",
    "socket",
}


def third_party_packages(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    names = {m.group(1) for m in IMPORT_RE.finditer(text)}
    return {n for n in names if n not in SKIP and not n.startswith("_")}


def shadowing(workspace: Path, packages: set[str]) -> list[tuple[str, str]]:
    """返回 ``[(包名, 遮蔽物路径)]``。"""
    hits: list[tuple[str, str]] = []
    if not workspace.is_dir():
        return hits
    for name in sorted(packages):
        for cand in (workspace / ("%s.py" % name), workspace / name):
            if cand.exists():
                hits.append((name, str(cand)))
    return hits


def main() -> int:
    if not SERVER.is_file():
        # ⚠⚠ **这里曾经无条件 `SKIP`，那是假绿**（2026-10-01 轮 83 系统排查发现）：
        #   `SERVER = ROOT / "mcp-server" / "server.py"` —— **本仓库自己的文件**
        #   （`ROOT` 由 `__file__` 推出 ⇒ 永远是本仓库根）。
        #   ⇒ 「`server.py` 不在」**不是"数据源不可用"**，而是**这份 checkout 坏了**；
        #     而本门禁要守的东西正是「工作区遮蔽依赖包」——
        #     **读不出依赖包清单 ⇒ 它一个包都没查 ⇒ 却报全绿**。
        # ⇒ **区分两件事**：① **`mcp-server/` 目录整个不在** ⇒ 说明这里**根本不是本仓库*
        # *
        #   （例如被单独拷出去跑）⇒ SKIP（便携性）；
        #   ② **目录在、但 `server.py` 不在** ⇒ **FAIL**（仓库不完整）。
        if not SERVER.parent.is_dir():
            print(
                "[SKIP] 找不到 `mcp-server/` 目录（%s）—— **这里不是本仓库**"
                % SERVER.parent
            )
            print("  （**便携性守卫**：脚本被单独拷出去跑时不应无条件红）")
            return 0
        print(
            "[FAIL] `mcp-server/` 目录在，但读不到 `%s` ⇒ **仓库不完整**" % SERVER.name
        )
        print(
            "  ⚠ 这与「数据源不可用」**不是一回事**：本门禁靠它拿「第三方依赖包清单」，"
        )
        print(
            "     读不到 ⇒ **一个包都没查** ⇒ 遮蔽问题会**静默漏过**（而那正是本门禁要抓的）。"
        )
        print(
            "     修法：确认 checkout 完整（`git status` / `git checkout -- mcp-server/`）。"
        )
        return 1
    pkgs = third_party_packages(SERVER)
    hits = shadowing(WORKSPACE, pkgs)
    print("server.py 用到的顶层第三方包 %d 个；工作区 %s" % (len(pkgs), WORKSPACE))
    if not hits:
        print("[PASS] 工作区根没有会遮蔽它们的 .py/目录")
        return 0
    print()
    print("[FAIL] 工作区根有 **%d 个**会遮蔽依赖包的文件/目录：" % len(hits))
    for name, path in hits:
        print("  %-14s ← %s" % (name, path))
    print()
    print(
        "  后果：以该工作区为 CWD 的 Python 进程里，`import %s` 拿到的是**那个本地文件**，"
        % hits[0][0]
    )
    print(
        "        不是真的包 ⇒ 报 `No module named '%s.server'; '%s' is not a package`"
        % (hits[0][0], hits[0][0])
    )
    print(
        "  修法（**不自动做**，由人定）：把那些历史脚本移出工作区根，或改名加前缀（如 `_mcp.py`）。"
    )
    print("  ⚠ 本工具**不删任何东西** —— 工作区里的脚本是历史产物。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
