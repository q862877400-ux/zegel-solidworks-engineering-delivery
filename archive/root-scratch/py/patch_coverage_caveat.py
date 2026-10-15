# -*- coding: utf-8 -*-
"""往 gen_family_coverage.py 的表头插入「编目录 vs 真调用」的口径说明。"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

F = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
lines = F.read_text(encoding="utf-8").splitlines()

start = next((i for i, l in enumerate(lines) if "「触及」的定义" in l), None)
if start is None:
    print("[FATAL] 找不到「触及」的定义 那一行")
    sys.exit(2)

BLOCK = '''
         "> ⚑⚑ **本表两个百分比含义不同，必须分开看**：",
         ">",
         "> | 列 | 含义 |",
         "> |---|---|",
         "> | **编目录** | 该族成员里有多少名字在代码里出现过 —— **含只写在登记表里的** |",
         "> | **真调用** | 有多少**真的被调用过**（get_com_member 传名 或 点调用）|",
         ">",
         "> **合并这两个数字就是误导。** 早先版本只报一个触及率，",
         "> 于是「族触及率 100%」是靠**把名字列进登记表**达成的 ——",
         "> 那证明的是「这份 API 清单做完了」，**不是「这些 API 都能用了」**。",
         "> 当前实测：16,615 个成员里，**编入目录 12,870（77%）**、",
         "> **真调用 2,636（16%）**。",
         ">",
         "> FeatureData 的属性赋值不计入真调用。", "",
'''.splitlines()

out = lines[:start] + BLOCK + lines[start + 3:]
F.write_text("\n".join(out) + "\n", encoding="utf-8")
ast.parse("\n".join(out))
print("已插入口径说明，语法 OK")
