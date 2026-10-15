# -*- coding: utf-8 -*-
"""往 family-coverage.md 的表头写清三列口径。"""
from __future__ import annotations

import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

F = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
src = F.read_text(encoding="utf-8")

OLD = ('         "> | **真调用** | 有多少**真的被调用过**（get_com_member 传名 或 点调用）|",')
NEW = ('         "> | **护栏可调** | 登记在某模块能力表里，且有 `_checked(target, member, …)` 这样的**可达调用路径** |",\n'
       '         "> | **直接调** | 静态上**看得见**字面量的调用（get_com_member 传名 / 点调用）|",\n'
       '         ">",\n'
       '         "> ⚑ **护栏可调 ⊇ 直接调**。差值来自「调用处传的是变量」——",\n'
       '         "> 模块写成 `_checked(target, member, …)` 时，静态归因看不到字面量。",\n'
       '         "> ⇒ **「直接调」系统性低估，不是精确值。**",')

if OLD in src:
    src = src.replace(OLD, NEW, 1)
    F.write_text(src, encoding="utf-8")
    print("已替换表头口径")
else:
    print("[FATAL] 没找到原口径行，未改")
    sys.exit(2)
