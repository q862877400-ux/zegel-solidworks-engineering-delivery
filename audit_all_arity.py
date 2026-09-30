# -*- coding: utf-8 -*-
"""审计所有登记表模块的 arity，看有多少条把 by-ref 出参算成了实参。"""
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
REFL = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
txt = REFL.read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")


def com(n: str) -> str:
    return re.sub(r"^(get|set)_", "", n)


_blocks: dict[str, dict[str, list[int]]] = {}


def real_arities(iface: str) -> dict[str, list[int]]:
    """某接口段 {COM 名: [各重载的「真实实参」个数]}（排除 by-ref 出参）。"""
    if iface in _blocks:
        return _blocks[iface]
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
            real = len([a for a in params if not a.endswith("&")])
            out.setdefault(com(m.group(1)), []).append(real)
    _blocks[iface] = out
    return out


MODULES = [
    "sw_hubs", "sw_drawing_annotations", "sw_part_features",
    "sw_sketch_sheetmetal", "sw_simulation_registry", "sw_simulation_full",
    "sw_pdm_full", "sw_sldworks_remaining", "sw_sldworks_lastgap",
    "sw_routing_costing_full", "sw_geometry", "sw_view", "sw_sketch",
    "sw_assembly_doc", "sw_drawing_view", "sw_selection", "sw_pattern",
]


def load(name: str):
    connect = types.ModuleType("sw_connect")
    connect.get_com_member = lambda o, n, *a, **k: None
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def tables_of(mod) -> list[tuple[str, dict]]:
    """把模块里所有 arity 表收出来（含一层与两层）。"""
    out = []
    for attr in dir(mod):
        v = getattr(mod, attr)
        if not isinstance(v, dict) or not v:
            continue
        if all(isinstance(x, int) for x in v.values()):
            out.append((attr, v))
        elif all(isinstance(x, dict) and x
                 and all(isinstance(y, int) for y in x.values())
                 for x in v.values()):
            for fam, sub in v.items():
                out.append((f"{attr}[{fam}]", sub))
    return out


total_bad = 0
total_rows = 0
for name in MODULES:
    path = REPO / "scripts" / f"{name}.py"
    if not path.is_file():
        continue
    mod = load(name)
    # 该模块的 arity 表对应的接口：先从表名里找 I* 前缀的族
    fams = set()
    for attr, _t in tables_of(mod):
        for h in re.findall(r"\[(I\w+)\]", attr):
            fams.add(h)
    if not fams:
        for attr, _t in tables_of(mod):
            src = path.read_text(encoding="utf-8")
            m = re.search(re.escape(attr.split("[")[0]) + r"[^=]*=\s*\{", src)
            if m:
                for h in re.findall(r"'(I\w+)':", src[m.start():m.start() + 200000]):
                    fams.add(h)
                    break
    pools = {}
    for f in fams:
        pools.update({k: v for k, v in real_arities(f).items()})
    if not pools:
        continue
    bad = 0
    rows = 0
    for attr, t in tables_of(mod):
        for member, cur in t.items():
            rows += 1
            if member in pools and cur not in pools[member]:
                bad += 1
    if rows:
        total_rows += rows
        total_bad += bad
        flag = "OK " if bad == 0 else "BAD"
        print(f"  [{flag}] {name:<28} 表项 {rows:5d} / arity 口径错 {bad}")
print(f"\n合计：表项 {total_rows}，口径错 {total_bad}")
