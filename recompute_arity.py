# -*- coding: utf-8 -*-
"""按反射**机械重算**各模块 arity 表，不再手打。

⚑ 口径：arity = 调用方要传的实参个数，**排除 by-ref 出参**（`Xxx&`）。
  早先手写时把 by-ref 也数进去了，`GetErrorMessages(Object&,Object&,Object&)`
  被写成 3 —— 实际调用方**一个都不传**。
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
REFL = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
txt = REFL.read_text(encoding="utf-8", errors="replace")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")


def com(n: str) -> str:
    return re.sub(r"^(get|set)_", "", n)


def arities(iface: str) -> dict[str, list[int]]:
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
    return out


def load(name: str, filename: str):
    connect = types.ModuleType("sw_connect")
    connect.get_com_member = lambda o, n, *a, **k: None
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location(
        name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FIX = [
    ("sw_sldworks_app", "sw_sldworks_app.py", "ISLDWORKS_ARITY", ("ISldWorks",)),
    ("sw_model_doc_extension", "sw_model_doc_extension.py", "MDE_ARITY",
     ("IModelDocExtension",)),
    ("sw_document_core", "sw_document_core.py", "DOC_CORE_ARITY",
     ("ISldWorks", "IModelDoc2", "IModelDocExtension")),
]
NESTED = [
    ("sw_section_view", "sw_section_view.py", None, None),
    ("sw_table_annotations", "sw_table_annotations.py", None, None),
]

changes = 0
for name, filename, attr, ifaces in FIX:
    mod = load(name, filename)
    table = getattr(mod, attr)
    pool: dict[str, list[int]] = {}
    for f in ifaces:
        for k, v in arities(f).items():
            pool.setdefault(k, []).extend(v)
    for member, cur in list(table.items()):
        if member not in pool:
            print(f"  [MISS] {name}.{attr}[{member}] 反射里查不到 —— 需人工判断")
            continue
        if cur in pool[member]:
            continue
        print(f"  [FIX ] {name}.{attr}[{member}]: {cur} -> {pool[member]}")
        table[member] = pool[member][0]
        changes += 1

for name, filename, _a, _b in NESTED:
    mod = load(name, filename)
    if hasattr(mod, "TABLE_ANNOTATION_ARITY"):
        groups = [(k, v) for k, v in mod.TABLE_ANNOTATION_ARITY.items()]
    else:
        groups = [
            ("ISectionViewData", mod.SECTION_VIEW_ARITY),
            ("IAnnotationView", mod.ANNOTATION_VIEW_ARITY),
            ("IModelViewManager", mod.MODEL_VIEW_MANAGER_ARITY),
        ]
    for iface, members in groups:
        pool = arities(iface)
        for member, cur in list(members.items()):
            if member not in pool:
                print(f"  [MISS] {name}.{iface}.{member} 反射里查不到")
                continue
            if cur in pool[member]:
                continue
            print(f"  [FIX ] {name}.{iface}.{member}: {cur} -> {pool[member]}")
            members[member] = pool[member][0]
            changes += 1

print(f"\n共需改 {changes} 处")
