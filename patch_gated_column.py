# -*- coding: utf-8 -*-
"""给覆盖表加第三列：经护栏可调（gated）。

问题：模块里大量调用写成 `_checked(target, member, …)`，成员名是**变量**，
      覆盖工具只认字符串字面量 ⇒ 这些调用**它看不见**。
      于是「直接调用」那一列系统性**低估**。

对策：加第三列，认「登记在某模块的 ARITY 表里」的成员 ——
      它们确实有护栏保护的可达调用路径，只是静态上看不到字面量。
三列各自含义写进表头，不合并。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

F = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
src = F.read_text(encoding="utf-8")

# 1) 新增：扫 *_ARITY / *_PROPERTIES 表，取出登记过的成员名
NEW_FUNC = '''

#: 模块里形如 ``"MemberName": 3,`` 的登记项（能力表 / arity 表）。
#: ⚑ 这些名字**有护栏保护的可达调用路径**，但因为调用处传的是**变量**
#:   （`_checked(target, member, …)`），静态上��不到字面量 ⇒ 「直接调用」列漏算它们。
REGISTRY_KEY = re.compile(r"^\\s+[\\"']([A-Z]\\w{2,})[\\"']\\s*:")


def repo_gated() -> set[str]:
    """登记在某模块能力表里的成员名。"""
    out: set[str] = set()
    for pat in ("scripts/*.py", "subskills/**/*.py"):
        for p in sorted(REPO.glob(pat)):
            if p.name == "__init__.py":
                continue
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                if SKIP.match(line):
                    continue
                m = REGISTRY_KEY.match(line)
                if m:
                    out.add(m.group(1))
    return out

'''
anchor = "\ndef _parse(iface: str):"
if "def repo_gated" not in src:
    if anchor in src:
        src = src.replace(anchor, NEW_FUNC + anchor, 1)
    else:
        print("[WARN] 找不到 _parse 锚点，尝试 main")
        src = src.replace("\ndef main() -> int:", NEW_FUNC + "\ndef main() -> int:", 1)

# 2) main 里加 gated 集合与逐族计数
old = "    called, catalogued = repo_members()"
new = ("    called, catalogued = repo_members()\n"
       "    gated = repo_gated()")
if old in src and "gated = repo_gated()" not in src:
    src = src.replace(old, new, 1)

old2 = '''            hit = [m for m in mems if m in catalogued]
            used = [m for m in mems if m in called]'''
new2 = '''            hit = [m for m in mems if m in catalogued]
            used = [m for m in mems if m in called]
            # ⚑ 护栏可达：登记在某模块能力表里、且有 `_checked(target, member, …)`
            #   这样的可达调用路径，但调用处传变量 ⇒ 「直接调用」列漏算。
            gated_hits = [m for m in mems if m in gated]'''
if old2 in src and "gated_hits" not in src:
    src = src.replace(old2, new2, 1)

old3 = '''                "used": len(used),
                "used_pct": (round(100.0 * len(used) / len(mems)) if mems else None),'''
new3 = '''                "used": len(used),
                "used_pct": (round(100.0 * len(used) / len(mems)) if mems else None),
                "gated": len(gated_hits),
                "gated_pct": (round(100.0 * len(gated_hits) / len(mems)) if mems else None),'''
if old3 in src and '"gated":' not in src:
    src = src.replace(old3, new3, 1)

F.write_text(src, encoding="utf-8")
import ast
ast.parse(src)
print("已加入 gated 列")
