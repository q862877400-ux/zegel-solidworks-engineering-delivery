# -*- coding: utf-8 -*-
"""**按族**审计所有登记表模块的 arity（正确口径：同名成员只在本族内比）。"""
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
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
REFL = [Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt"),
        Path(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt"),
        Path(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt"),
        Path(r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt"),
        Path(r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt"),
        Path(r"D:\AI\SW\_raw\reflect\iface_fworks.txt")]

pool: dict[str, dict[str, list[int]]] = {}
for r in REFL:
    if not r.is_file():
        continue
    cur = None
    for raw in r.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "):
            cur = raw[3:].strip()
            pool.setdefault(cur, {})
        elif cur and raw.strip():
            m = SIG.match(raw.strip())
            if not m:
                continue
            name = re.sub(r"^(get|set)_", "", m.group(1))
            params = [a.strip() for a in m.group(2).split(",") if a.strip()]
            n = len([a for a in params if not a.endswith("&")])
            lst = pool[cur].setdefault(name, [])
            if n not in lst:
                lst.append(n)

MODULES = ["sw_hubs", "sw_drawing_annotations", "sw_part_features",
           "sw_sketch_sheetmetal", "sw_geometry", "sw_simulation_registry",
           "sw_simulation_full", "sw_pdm_full", "sw_sldworks_remaining",
           "sw_sldworks_lastgap", "sw_routing_costing_full"]
ROW = re.compile(r"^(\s+)(['\"])([A-Za-z_]\w*)\2(\s*:\s*)(\d+)(\s*,?\s*)$")
FAM = re.compile(r"^\s{4}['\"](\w+)['\"]\s*:\s*\{")
SKIP = ("SW_DOC_TYPES", "SW_OPEN_DOC_OPTIONS", "SW_SAVE_AS_OPTIONS",
        "SW_SAVE_AS_VERSION", "SW_PREF_STRINGS", "SW_PREF_INTEGERS",
        "SW_PREF_TOGGLES", "SW_PREF_DOUBLES", "SW_SELECT_TYPES")

total_rows = total_bad = 0
for mod in MODULES:
    p = REPO / "scripts" / f"{mod}.py"
    if not p.is_file():
        continue
    lines = p.read_text(encoding="utf-8").splitlines()
    fam = None
    tbl = None
    rows = bad = 0
    for line in lines:
        fm = FAM.match(line)
        if fm:
            fam = fm.group(1)
        if re.match(r"^(\w+)\s*:\s*dict\[str, (dict\[str, int\]|int)\]\s*=\s*\{", line):
            tbl = line.split(":")[0]
        if tbl in SKIP:
            continue
        rm = ROW.match(line)
        if not rm or fam is None or fam not in pool:
            continue
        rows += 1
        mem, ar = rm.group(3), int(rm.group(5))
        real = pool[fam].get(mem)
        if real and ar not in real:
            bad += 1
            if bad <= 3:
                print(f"      {mod} {fam}.{mem}: 表{ar} 反射{real}")
    total_rows += rows
    total_bad += bad
    print(f"  [{'OK ' if bad == 0 else 'BAD'}] {mod:<26} 表项 {rows:5d} / 错 {bad}")
print(f"\n按族口径：表项 {total_rows}，口径错 {total_bad}")
