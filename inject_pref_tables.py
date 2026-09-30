# -*- coding: utf-8 -*-
"""往 sw_sldworks_app.py 注入首选项与选择类型的枚举常量表（机械生成）。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO = Path(r"C:\swprojects\sw-skill-fork")
TARGET = REPO / "scripts" / "sw_sldworks_app.py"
RAW = Path(r"D:\AI\SW\_raw\enum_values_sldworks.txt")
SWCONST = r"D:\AI\SW\_raw\enum_values_sldworks.txt"

blocks: dict[str, list[tuple[str, int]]] = {}
cur = None
for line in RAW.read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        cur = line[3:].strip()
        blocks[cur] = []
    elif cur and line.strip():
        m = re.match(r"(\w+)\s*=\s*(-?\d+)", line.strip())
        if m:
            blocks[cur].append((m.group(1), int(m.group(2))))

TABLES = [
    ("SW_PREF_STRINGS", "swUserPreferenceStringValue_e"),
    ("SW_PREF_INTEGERS", "swUserPreferenceIntegerValue_e"),
    ("SW_PREF_TOGGLES", "swUserPreferenceToggle_e"),
    ("SW_PREF_DOUBLES", "swUserPreferenceDoubleValue_e"),
    ("SW_SELECT_TYPES", "swSelectType_e"),
]
for name, enum in TABLES:
    if enum not in blocks:
        print(f"[FATAL] 反射清单里没有 {enum}，不生成")
        sys.exit(2)

L = ["# ── 来源 ─────────────────────────────────────────────────────────────",
     "# 仓库:   官方 swconst 程序集的纯元数据反射",
     f"# 文件:   {SWCONST}",
     "# 定位:   首选项与选择类型的**完整字面值表**。**逐项机械生成，不手抄**。",
     "# ⚑ 这些枚举各有 141~828 项，本模块**整表收下** ——",
     "#   理由：只收「常用几项」等于要求调用方猜数字，违反铁律 4。",
     "# ⚠ 本表的数值来自对 SolidWorks.Interop.swconst.dll 的元数据读取。"]
for name, enum in TABLES:
    L.append(f"#     {name:<20} ← {enum}（{len(blocks[enum])} 项）")
L += ["# 覆盖:   后续同级定义",
      "# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）",
      "# ────────────────────────────────────────────────────────────────────",
      f'SWCONST_SOURCE = r"{SWCONST}"',
      ""]
for name, enum in TABLES:
    L.append(f"{name}: dict[str, int] = {{")
    for k, v in blocks[enum]:
        L.append(f'    "{k}": {v},')
    L.append("}")
    L.append("")

src = TARGET.read_text(encoding="utf-8")
anchor = "\n\ndef _require(obj, what: str):"
if anchor not in src:
    print("[FATAL] 找不到注入锚点")
    sys.exit(2)
src = src.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
TARGET.write_text(src, encoding="utf-8")
total = sum(len(blocks[e]) for _, e in TABLES)
print(f"已注入 {len(TABLES)} 张表，合计 {total} 个枚举字面值")
