r"""@brief 探针：找「**定义了却没人用**」的门禁常量（**死守卫**的通用形态）。

## 起因（2026-10-01 轮 134）
`mcp-server/tool_registry.py` 的 `_LEN_SUFFIX = "_mm"` **只在定义处出现过一次** ——
规则 2 的长度那一半**从未生效**，而它一直被算进「五统一门禁通过」。
★ 那是事实 40（「存在但没人用的守卫与没有守卫等价，且更糟」）的教科书例子。

## 本探针做什么
在 `mcp-server/` 与 `scripts/` 里找**模块级常量**，名字像门禁
（`*_RE` / `*_SUFFIX` / `*_NAMES` / `*_MARK` / `*_PATTERN` / `*_ALLOWED` / `*_BANNED` …），
然后数它**在同一个文件里出现几次**：
* **1 次**（只有赋值那一行）⇒ ★ **疑似死守卫**；
* ≥2 次 ⇒ 至少被引用了。

## ⚠ 这是**探针**，不是门禁
「只出现一次」**不等于**「没用」—— 它可能是：
  ① 纯文档性常量（给人读的）；
  ② 被 `__all__` 或字符串引用（本探针数不到）；
  ③ 真的死守卫 ⇒ **那才是发现**。
⇒ **输出清单，人工逐条判**（本项目纪律：按名字的检查先量假阳性率）。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_dead_guards.py
# 定位:   给 Spec Kit `054` 取证：其它规则里有没有同类的「死守卫」。
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

#: 名字像门禁的常量（**有界词表**，刻意保守）
GUARDISH = re.compile(
    r"(_RE|_REGEX|_PATTERN|_SUFFIX|_PREFIX|_NAMES|_MARK|_MARKS|_ALLOWED|_BANNED|"
    r"_FORBIDDEN|_WHITELIST|_BLACKLIST|_REDLINE|_WORDS|_MAX|_MIN)$"
)


def module_constants(path: Path):
    """取模块级赋值：名字 → 行号。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out.append((t.id, node.lineno))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            out.append((node.target.id, node.lineno))
    return out


def main() -> int:
    suspects, checked = [], 0
    for base in ("mcp-server", "scripts"):
        for p in sorted((ROOT / base).glob("*.py")):
            text = p.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            for name, lineno in module_constants(p):
                if not GUARDISH.search(name):
                    continue
                checked += 1
                #: 数**非注释**里出现的次数（形如 `NAME` 的独立词）
                word = re.compile(r"\b%s\b" % re.escape(name))
                hits = [
                    i + 1
                    for i, l in enumerate(lines)
                    if word.search(l) and not l.strip().startswith("#")
                ]
                if len(hits) <= 1:
                    suspects.append((base, p.name, name, lineno, hits))

    print("  扫过的「像门禁的模块级常量」: **%d** 个" % checked)
    print()
    print("  ★ **只出现 1 次（只有赋值那行）** 的: **%d** 个" % len(suspects))
    for base, fname, name, lineno, hits in suspects:
        print("    %s/%s L%-5d %s" % (base, fname, lineno, name))
    print()
    print("⚠ **不下「它们都是死守卫」的结论** —— 逐条人工判三类：")
    print("   ① 纯文档性常量（给人读的）⇒ 假阳性；")
    print("   ② 被 `__all__` / 字符串引用（本探针数不到）⇒ 假阳性；")
    print("   ③ **真的死守卫** ⇒ 那才是发现。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
