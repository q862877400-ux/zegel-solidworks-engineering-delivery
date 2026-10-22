r"""@brief 探针：找「**定义了却从没被调用**」的函数 —— 死守卫的**另一种形态**。

## 起因
`053`/`054` 扫出**常量**形态的死守卫（`_LEN_SUFFIX` / `_ANGLE_SUFFIX` —— 规则 2 的两半
都定义了却没人用）。★ 本轮扫**函数**形态：**门禁/工具里的私有辅助函数，定义了却从没被调**。
⚠ 已知事实 61 的定则④就说过这类事：
「**写了一个好用的工具函数，就要在**所有**同类场合用它，别只用在门禁里**」。

## 判法（有界、可复核）
1. 取 `scripts/check_*.py` / `scripts/audit_*.py` / `scripts/gen_*.py` / `tools/*.py`
   里**模块级**的 `def`（含 `_` 开头的私有函数）；
2. **排除入口点**（`main`）与**明确的公开 API**（被别的文件 import 的）；
3. 数该名字**在整个仓库**（`scripts/` + `mcp-server/` + `tools/` + `tests/`）里
   除了定义行之外还出现几次；
4. **0 次** ⇒ 可疑。

## ⚠ 这是**探针**，不是门禁
「从没被调」**不等于**"没用" —— 它可能是：
  ① **入口点**（`main`，由 `if __name__` 调）；
  ② 被**动态**调用（`getattr` / 注册表 / 字符串）；
  ③ 真的死了 ⇒ **那才是发现**。
⇒ **输出清单，人工逐条判**。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_uncalled_helpers.py
# 定位:   给 Spec Kit `055` 取证：门禁/工具里有没有"定义了却没人调"的辅助函数。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

#: 要扫的文件（**门禁 / 工具**这两类最该没有死代码）
PATTERNS = (
    "scripts/check_*.py",
    "scripts/audit_*.py",
    "scripts/gen_*.py",
    "tools/*.py",
)
#: 整个仓库里"哪里的出现算被调用"
SEARCH_DIRS = ("scripts", "mcp-server", "tools", "tests", "subskills")
#: 入口点 / 框架约定：由别处按名字取，不算死
ENTRY_POINTS = {"main", "register", "run"}


def module_defs(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    return [
        (n.name, n.lineno)
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def find_uncalled(root=None, *, search_dirs=None, patterns=None):
    """返回 `(checked, suspects)` —— `suspects` 是 `[(相对路径, 行号, 函数名), …]`。

    ⚑ **把判法抽出来**，让 `main()` 与测试**跑同一份代码** ——
    否则负例测的是「测试自己重写的一份」，那不叫测到了工具（事实 62 的精神）。
    """
    root = Path(root) if root is not None else ROOT
    dirs = tuple(search_dirs) if search_dirs else SEARCH_DIRS
    pats = tuple(patterns) if patterns else PATTERNS

    corpus = {}
    for d in dirs:
        for p in (root / d).rglob("*.py"):
            corpus[p] = p.read_text(encoding="utf-8", errors="replace")

    targets = []
    for pat in pats:
        targets.extend(sorted(root.glob(pat)))

    suspects, checked = [], 0
    for p in targets:
        for name, lineno in module_defs(p):
            if name in ENTRY_POINTS:
                continue
            checked += 1
            word = re.compile(r"\b%s\b" % re.escape(name))
            hits = 0
            for q, text in corpus.items():
                for i, line in enumerate(text.splitlines(), 1):
                    if not word.search(line):
                        continue
                    if q == p and i == lineno:
                        continue
                    if line.strip().startswith("#"):
                        continue
                    hits += 1
            if hits == 0:
                try:
                    rel = str(p.relative_to(root))
                except ValueError:
                    rel = str(p)
                suspects.append((rel, lineno, name))
    return checked, suspects


def main() -> int:
    checked, suspects = find_uncalled()
    print("  扫过的门禁/工具模块函数: **%d** 个" % checked)
    print()
    print("  ★ **在整个仓库里从没被调用** 的: **%d** 个" % len(suspects))
    for f, lineno, name in suspects:
        print("    %-44s L%-5d %s" % (f, lineno, name))
    print()
    print("⚠ **不下「它们都是死代码」的结论** —— 逐条人工判三类：")
    print("   ① **入口点**（由 `if __name__` 或别处按名字调）⇒ 假阳性；")
    print("   ② 被**动态**调用（`getattr` / 注册表 / 字符串）⇒ 假阳性；")
    print("   ③ **真的死了** ⇒ 那才是发现。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
