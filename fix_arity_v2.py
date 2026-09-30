# -*- coding: utf-8 -*-
"""按族严格修正所有登记表模块的 arity（第二轮修正，修正第一轮的越权改动）。"""
from __future__ import annotations

import io
import re
import sys
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

MODULES = ["sw_hubs", "sw_drawing_annotations", "sw_drawing_view",
           "sw_part_features", "sw_sketch_sheetmetal", "sw_geometry",
           "sw_simulation_registry", "sw_simulation_full", "sw_pdm_full",
           "sw_sldworks_remaining", "sw_sldworks_lastgap",
           "sw_routing_costing_full", "sw_simulation_study_options"]
FAM = re.compile(r"^ {4}['\"](\w+)['\"]\s*:\s*\{")
ROW = re.compile(r"^(\s+)(['\"])([A-Za-z_]\w*)\2(\s*:\s*)(\d+)(\s*,?\s*)$")
SKIP = {"SW_DOC_TYPES", "SW_OPEN_DOC_OPTIONS", "SW_SAVE_AS_OPTIONS",
        "SW_SAVE_AS_VERSION", "SW_PREF_STRINGS", "SW_PREF_INTEGERS",
        "SW_PREF_TOGGLES", "SW_PREF_DOUBLES", "SW_SELECT_TYPES"}

total = 0
for mod in MODULES:
    p = REPO / "scripts" / f"{mod}.py"
    if not p.is_file():
        continue
    lines = p.read_text(encoding="utf-8").splitlines()
    fam = None
    tbl = None
    changed = 0
    for i, line in enumerate(lines):
        fm = FAM.match(line)
        if fm:
            fam = fm.group(1)
        tm = re.match(r"^(\w+)\s*:\s*dict\[str, (dict\[str, int\]|int)\]\s*=\s*\{", line)
        if tm:
            tbl = tm.group(1)
        if tbl in SKIP or fam is None or fam not in pool:
            continue
        rm = ROW.match(line)
        if not rm:
            continue
        mem, old = rm.group(3), int(rm.group(5))
        real = pool[fam].get(mem)
        if not real or old in real:
            continue
        # 选**不含 by-ref 时**最贴近的；全不行就用第一个
        new = real[0]
        lines[i] = (f"{rm.group(1)}{rm.group(2)}{mem}{rm.group(2)}"
                    f"{rm.group(4)}{new}{rm.group(6)}")
        changed += 1
    if changed:
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  {mod:<28} 修正 {changed:4d}")
        total += changed
print(f"合计 {total}")
