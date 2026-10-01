"""更正第 22 轮的一处**事实错误** + 治住「工作区根遮蔽依赖包」这个**真实陷阱**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁 + 一处更正，非第三方移植）
# 文件:   D:\\AI\\SW\\fix_bare_outparams.py（**存在**，第 22 轮我误称其不存在）
#         D:\\AI\\SW\\find_bare_outparam_sites.py（配套的「找」脚本，同样存在）
#         D:\\AI\\SW\\mcp.py（**遮蔽真 `mcp` 包**的文件）
# 定位:   2026-10-01，两件事：
#
#   **① 更正一处事实错误。**
#     第 22 轮我在文档里写「`fix_bare_outparams.py` **不存在**，所以那条一直悬着」。
#     **⇒ 错了。** 该文件**在**工作区根目录（`D:\\AI\\SW\\`，5 KB，2026-10-01 03:17），
#     配套的 `find_bare_outparam_sites.py` 也在。**我只在代码副本里找，没在工作区里找。**
#     **⇒ 这正是「查不到就说查不到」要防的错：把「我这一处没找到」说成「不存在」。**
#     **⚠ 也意味着：第 22 轮那个「0 处」的结果，很可能是这两个脚本**已经跑过**的结果 ——
#     与我当时「要么已修、要么口径不同」的推测一致，但我当时**没去核实**。
#
#   **② 治住一个**真实陷阱**：工作区根有一个 `mcp.py`。**
#     Python 把**当前目录**放在 `sys.path[0]` ⇒ 任何以 `D:\\AI\\SW` 为 CWD 的 Python
#     进程里，`import mcp` 拿到的是**那个脚本**，不是真的 mcp 包
#     ⇒ `'mcp' is not a package` ⇒ **`server.py` 在该 CWD 下根本 import 不了**。
#     本探针就是在实测接线时撞上它的。
#
# 官方签名依据: 不适用
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"C:\swprojects\sw-skill-fork")
WS = Path(r"D:\AI\SW")
DOC = WS / "docs" / "T-011-expose-capabilities-assessment.md"
CHECK = REPO / "scripts" / "check_workspace_shadowing.py"
TEST = REPO / "tests" / "test_workspace_shadowing.py"

CHECK_SRC = '''"""@brief 检查**工作区根**有没有会遮蔽依赖包的模块（`mcp.py` 这类）。

## 为什么需要它（实测撞上的真实陷阱）
Python 把**当前目录**放在 `sys.path[0]`。工作区根 `D:\\\\AI\\\\SW\\\\` 里有 ~600 个散落的
`.py` 脚本，其中**有一个 `mcp.py`** ⇒ 任何以该目录为 CWD 的 Python 进程里
`import mcp` **拿到的是那个脚本**，不是真的 mcp 包：

    ModuleNotFoundError: No module named 'mcp.server'; 'mcp' is not a package

**⇒ 后果：`mcp-server/server.py` 在 `D:\\\\AI\\\\SW` 这个 CWD 下**根本 import 不了**，
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

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = Path(r"D:\\AI\\SW")
SERVER = ROOT / "mcp-server" / "server.py"

#: 从 server.py 里抽顶层第三方包名（只取第一段）
IMPORT_RE = re.compile(r"^\\s*(?:from|import)\\s+([a-zA-Z_][\\w]*)", re.M)

#: 标准库与本地模块不算（本仓库自己的包名也不必查）
SKIP = {
    "scripts", "tool_registry", "register_capabilities", "typing", "os", "sys",
    "json", "re", "time", "pathlib", "dataclasses", "enum", "abc", "functools",
    "collections", "itertools", "contextlib", "traceback", "logging", "math",
    "subprocess", "tempfile", "shutil", "io", "warnings", "asyncio", "types",
    "importlib", "inspect", "datetime", "uuid", "hashlib", "base64", "threading",
    "queue", "copy", "textwrap", "argparse", "glob", "platform", "socket",
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
        print("[SKIP] 找不到 %s" % SERVER)
        return 0
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
    print("  后果：以该工作区为 CWD 的 Python 进程里，`import %s` 拿到的是**那个本地文件**，"
          % hits[0][0])
    print("        不是真的包 ⇒ 报 `No module named '%s.server'; '%s' is not a package`" % (hits[0][0], hits[0][0]))
    print("  修法（**不自动做**，由人定）：把那些历史脚本移出工作区根，或改名加前缀（如 `_mcp.py`）。")
    print("  ⚠ 本工具**不删任何东西** —— 工作区里的脚本是历史产物。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

TEST_SRC = '''"""工作区遮蔽依赖包的守卫（**不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   scripts/check_workspace_shadowing.py
# 定位:   2026-10-01 实测接线时撞上 `D:\\\\AI\\\\SW\\\\mcp.py` 遮蔽真 `mcp` 包
#         ⇒ `server.py` 在该 CWD 下 import 不了。本测试把这条做成可查项。
# 官方签名依据: 不适用（Python 的 `sys.path[0]` 语义）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK = REPO_ROOT / "scripts" / "check_workspace_shadowing.py"
WORKSPACE = Path(r"D:\\AI\\SW")


def _load():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("ws_shadow", CHECK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ws_shadow"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_checker_runs_and_reports():
    """检查器必须能跑起来并给出结论（**跑不起来也是问题**）。"""
    if not CHECK.is_file():
        pytest.skip("检查器不在")
    proc = subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120,
                          cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL)
    assert proc.stdout.strip(), "检查器没有任何输出"
    assert ("[PASS]" in proc.stdout) or ("[FAIL]" in proc.stdout), proc.stdout[-200:]


def test_checker_detects_a_planted_shadow(tmp_path):
    """**负例**：种一个同名 `mcp.py`，检查器必须报出来。

    ⚠ 与 `tests/test_gate_negative_cases.py` 同一纪律：**先证明工具有牙齿。**
    """
    mod = _load()
    fake_ws = tmp_path / "ws"
    fake_ws.mkdir()
    (fake_ws / "mcp.py").write_text("x = 1\\n", encoding="utf-8")
    hits = mod.shadowing(fake_ws, {"mcp", "pydantic"})
    names = {h[0] for h in hits}
    assert "mcp" in names, "**检查器没报出种下的 mcp.py 遮蔽** ⇒ 假门禁"
    assert "pydantic" not in names, "报了不存在的遮蔽物 ⇒ 误报"


def test_checker_passes_on_a_clean_workspace(tmp_path):
    """**正例**：干净目录必须 PASS（否则它会因误报而被忽略）。"""
    mod = _load()
    clean = tmp_path / "clean"
    clean.mkdir()
    assert mod.shadowing(clean, {"mcp", "pydantic"}) == []


def test_known_shadow_is_recorded_with_a_fix_recipe():
    """`mcp.py` 这个**已知**遮蔽物必须在检查器的输出里给出**修法**（不是只报错）。"""
    if not CHECK.is_file():
        pytest.skip("检查器不在")
    text = CHECK.read_text(encoding="utf-8")
    assert "把那些历史脚本移出工作区根" in text or "改名" in text, (
        "检查器只报错、没给修法 ⇒ 用处减半"
    )
    assert "不删任何东西" in text or "**不删**" in text, (
        "检查器必须写明**不自动删**（工作区脚本是历史产物）"
    )
'''

CORRECTION = """

---

## 二十一、⚠ **更正一处事实错误**（2026-10-01）

### 21.1 我第 22 轮说错了什么
本档「十八」里我写着：
> 「核实：那个工具**不存在**，所以这条一直悬着」

**⇒ 错了。** `fix_bare_outparams.py` **存在**，在**工作区根目录**：
```
D:\\AI\\SW\\fix_bare_outparams.py          5.0 KB  改于 2026-10-01 03:17
D:\\AI\\SW\\find_bare_outparam_sites.py    4.2 KB  改于 2026-10-01 03:16
```
**我**只在代码副本 `C:\\swprojects\\sw-skill-fork\\` 里找，没在工作区 `D:\\AI\\SW\\` 里找**，
就断言「不存在」。

**⇒ 这正是「查不到就说查不到」要防的错：把「我这一处没找到」说成「不存在」。**

### 21.2 连带影响
第 22 轮那个「**0 处**」的结果，很可能是**这两个脚本已经跑过**的结果。
我当时写的是「要么已被后续工作修掉、要么口径不同」—— **推测方向对，但我没去核实**。
**⇒ 现在核实了：工具在，且其时间戳（03:16/03:17）与那批工作同期。**
**⇒ 「0 处」这个**结论**仍然成立（我用独立写的审计器复核过），
但「工具不存在」这个**前提**是错的。**

### 21.3 教训（值得进 AGENTS.md 层面）
> **查「某个东西在不在」时，必须把**两个仓库**都查过**：
> 代码副本 `C:\\swprojects\\sw-skill-fork\\` **与**工作区 `D:\\AI\\SW\\`。
> **只查一处得出的「不存在」，是「我没找到」的另一种说法。**

### 21.4 ⚠ 顺带治住一个**真实陷阱**：工作区根遮蔽依赖包
**这是本轮的另一个实质发现，来自实测接线时撞上：**
```
D:\\AI\\SW\\mcp.py   ← Python 把**当前目录**放在 sys.path[0]
⇒ 任何以 D:\\AI\\SW 为 CWD 的 Python 进程里，`import mcp` 拿到的是**那个脚本**
⇒ ModuleNotFoundError: No module named 'mcp.server'; 'mcp' is not a package
⇒ **`mcp-server/server.py` 在该 CWD 下根本 import 不了**
```
**⚠ 而那个错误信息**看不出是「被本地文件遮蔽」** —— 指向不了真因。**

**⇒ 新增 `scripts/check_workspace_shadowing.py`**：对 `server.py` 用到的顶层第三方包，
检查工作区根有没有同名 `.py`/目录 ⇒ 有就报出 + **给修法**。
**⚠ 它**不自动删任何东西**（工作区里的 ~600 个脚本是历史产物，删不删由人定）。**

**⇒ 并配 4 条测试**（含**负例**：种一个 `mcp.py`，断言检查器报出来）。
"""


def main() -> int:
    (REPO / "scripts" / "check_workspace_shadowing.py").write_text(CHECK_SRC, encoding="utf-8")
    print("  ✓ 已写 scripts/check_workspace_shadowing.py")
    (REPO / "tests" / "test_workspace_shadowing.py").write_text(TEST_SRC, encoding="utf-8")
    print("  ✓ 已写 tests/test_workspace_shadowing.py")
    with DOC.open("a", encoding="utf-8") as fh:
        fh.write(CORRECTION)
    print("  ✓ 已把「更正」追加进 T-011 文档")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
