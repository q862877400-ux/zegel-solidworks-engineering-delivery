# -*- coding: utf-8 -*-
"""**原地**修正所有登记表模块的 arity 数值（族名单与键名一律不动）。

⚑ 为什么原地改而不重新生成：重新生成要求先从源码反解族名单，
  ���则匹配会漏族（本轮实测：sw_simulation_full 84→82、
  sw_routing_costing_full 31→12）⇒ 覆盖式生成会**丢族**。
  原地改只动右边的数字，键名与结构 100% 保持。
"""
from __future__ import annotations

import importlib.util
import io
import re
import sys
import types
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO = Path(r"C:\swprojects\sw-skill-fork")
SCRIPTS = REPO / "scripts"
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
_cache: dict[str, dict[str, list[int]]] = {}


def com(n: str) -> str:
    return re.sub(r"^(get|set)_", "", n)


def real_arities(refl: Path, iface: str) -> dict[str, list[int]]:
    key = f"{refl}|{iface}"
    if key in _cache:
        return _cache[key]
    txt = refl.read_text(encoding="utf-8", errors="replace")
    cur, out = None, {}
    for raw in txt.splitlines():
        if raw.startswith("## "):
            if cur == iface:
                break
            cur = raw[3:].strip()
            if cur == iface:
                out = {}
        elif cur == iface and raw.strip():
            m = SIG.match(raw.strip())
            if not m:
                continue
            params = [a.strip() for a in m.group(2).split(",") if a.strip()]
            out.setdefault(com(m.group(1)), []).append(
                len([a for a in params if not a.endswith("&")]))
    _cache[key] = out
    return out


# 模块 → (族所属的反射文件, 匹配 arity 表行的正则)
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
CW = Path(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt")
PDM = Path(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt")
RT = Path(r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt")
CO = Path(r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt")
FW = Path(r"D:\AI\SW\_raw\reflect\iface_fworks.txt")

MODULES = {
    "sw_hubs": [SW], "sw_drawing_annotations": [SW], "sw_part_features": [SW],
    "sw_sketch_sheetmetal": [SW], "sw_geometry": [SW],
    "sw_simulation_registry": [CW], "sw_simulation_full": [CW],
    "sw_pdm_full": [PDM], "sw_sldworks_remaining": [SW],
    "sw_sldworks_lastgap": [SW],
    "sw_routing_costing_full": [RT, CO, SW, CW, PDM, FW],
}

# 匹配一行 arity 表项： `'Member': 3,` 或 `"Member": 3,`
ROW = re.compile(r"^(\s+)(['\"])([A-Za-z_]\w*)\2(\s*:\s*)(\d+)(\s*,?\s*)$")

# 用来判断「当前这一段属于哪个族」：向上找最近的 `    'IXxx': {`
FAM = re.compile(r"^\s{4}['\"](I\w+)['\"]\s*:\s*\{")
# 用来判断「这一段属于哪张表」：向上找最近的顶层 `NAME: dict[...] = {`
TBL = re.compile(r"^(\w+)\s*:\s*dict\[str, dict\[str, int\]\]\s*=\s*\{")
TBL1 = re.compile(r"^(\w+)\s*:\s*dict\[str, int\]\s*=\s*\{")

SKIP_TABLES = ("SW_DOC_TYPES", "SW_OPEN_DOC_OPTIONS", "SW_SAVE_AS_OPTIONS",
               "SW_SAVE_AS_VERSION", "SW_PREF_STRINGS", "SW_PREF_INTEGERS",
               "SW_PREF_TOGGLES", "SW_PREF_DOUBLES", "SW_SELECT_TYPES")

total = 0
for mod, refl_list in MODULES.items():
    p = SCRIPTS / f"{mod}.py"
    if not p.is_file():
        continue
    pools: dict[str, list[int]] = {}
    # 把该模块可能所属的各反射文件的全部成员并进池子（名字冲突以先到为准）
    for r in refl_list:
        if not r.is_file():
            continue
        txt = r.read_text(encoding="utf-8", errors="replace")
        cur = None
        for raw in txt.splitlines():
            if raw.startswith("## "):
                cur = raw[3:].strip()
            elif cur and raw.strip():
                m = SIG.match(raw.strip())
                if m:
                    params = [a.strip() for a in m.group(2).split(",") if a.strip()]
                    n = len([a for a in params if not a.endswith("&")])
                    key = com(m.group(1))
                    if key not in pools:
                        pools[key] = []
                    if n not in pools[key]:
                        pools[key].append(n)
    lines = p.read_text(encoding="utf-8").splitlines()
    cur_fam = None
    cur_tbl = None
    changed = 0
    for i, line in enumerate(lines):
        fm = FAM.match(line)
        if fm:
            cur_fam = fm.group(1)
        tm = TBL.match(line) or TBL1.match(line)
        if tm:
            cur_tbl = tm.group(1)
        if cur_tbl in SKIP_TABLES:
            continue
        rm = ROW.match(line)
        if not rm:
            continue
        member = rm.group(3)
        old = int(rm.group(5))
        if member not in pools:
            continue
        if old in pools[member]:
            continue
        lines[i] = (f"{rm.group(1)}{rm.group(2)}{member}{rm.group(2)}"
                    f"{rm.group(4)}{pools[member][0]}{rm.group(6)}")
        changed += 1
    if changed:
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  {mod:<26} 修正 {changed:4d} 条")
        total += changed
print(f"\n合计修正 {total} 条")
