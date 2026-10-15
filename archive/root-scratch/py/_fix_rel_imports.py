"""★ 一次性：把函数内**无兜底的相对导入**改成仓库既有的"try 相对 / 回退绝对"写法。"""
from __future__ import annotations

import re
from pathlib import Path

TARGET = Path(r"D:\AI\SW\scripts\sw_simulation_loads.py")
src = TARGET.read_text(encoding="utf-8")
lines = src.splitlines(keepends=True)

#: ★ 只认**函数体内**、**无 try 兜底**的 `from .X import Y` / `import .X`
PAT = re.compile(r"^(?P<indent>\s+)from \.(?P<mod>[\w.]+) import (?P<names>.+?)\s*$")

out, changed = [], 0
for i, ln in enumerate(lines):
    m = PAT.match(ln.rstrip("\n"))
    if not m:
        out.append(ln)
        continue
    #: ★ 已经在 `try:` 的下一行 ⇒ 已经有兜底 ⇒ 不动 ✓
    prev = lines[i - 1].strip() if i else ""
    if prev == "try:":
        out.append(ln)
        continue
    indent = m.group("indent")
    mod, names = m.group("mod"), m.group("names")
    #: ★★ 仓库既有写法（★ 见本文件第 61–64 行的 `sw_connect` 那处）：
    #:   ★ 先试**相对**（作为 `scripts.` 包导入时成立）；★ 失败回退**绝对**（作为顶层模块时成立）✓
    out.append("%stry:                                                       # noqa: SIM105\n" % indent)
    out.append("%s    from .%s import %s\n" % (indent, mod, names))
    out.append("%sexcept ImportError:                                       # ★ 回退绝对导入 ✓\n"
               % indent)
    out.append("%s    from %s import %s\n" % (indent, mod, names))
    changed += 1

TARGET.write_text("".join(out), encoding="utf-8")
import ast
ast.parse("".join(out))
print("★ 改了 %d 处函数内无兜底的相对导入" % changed)
