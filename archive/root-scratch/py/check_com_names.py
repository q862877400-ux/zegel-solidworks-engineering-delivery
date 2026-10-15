# -*- coding: utf-8 -*-
"""核对各模块 arity 表里的成员名是否与反射一致，并归一化到 COM 名。

⚑ 关键区别：反射清单里属性形态写作 ``get_Xxx`` / ``set_Xxx``（.NET interop 约定），
  但 ``get_com_member`` 走的是 ``getattr(obj, name)`` —— 传的必须是 **COM 名**，
  即 ``Xxx``。⚑⚑ 传 ``GetXxx``（大写 G）会直接 AttributeError。
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


def com_name(name: str) -> str:
    """把反射里的 get_/set_ 归一化到 COM 名。"""
    return re.sub(r"^(get|set)_", "", name)


def block(iface: str) -> dict[str, list[int]]:
    """该接口段里 {COM 名: [各个重载的实参个数]}。"""
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
            if m:
                n = com_name(m.group(1))
                out.setdefault(n, []).append(
                    len([a for a in m.group(2).split(",") if a.strip()]))
    return out


def load(name: str, filename: str):
    connect = types.ModuleType("sw_connect")
    connect.get_com_member = lambda o, n, *a, **k: None
    sys.modules.setdefault("sw_connect", connect)
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


JOBS = [
    ("sw_sldworks_app", "sw_sldworks_app.py", "ISldWorks", "ISLDWORKS_ARITY"),
    ("sw_model_doc_extension", "sw_model_doc_extension.py",
     "IModelDocExtension", "MDE_ARITY"),
    ("sw_document_core", "sw_document_core.py", None, "DOC_CORE_ARITY"),
]
NESTED = [
    ("sw_section_view", "sw_section_view.py", "ISectionViewData", "SECTION_VIEW_ARITY"),
    ("sw_section_view", "sw_section_view.py", "IAnnotationView", "ANNOTATION_VIEW_ARITY"),
    ("sw_section_view", "sw_section_view.py", "IModelViewManager",
     "MODEL_VIEW_MANAGER_ARITY"),
    ("sw_table_annotations", "sw_table_annotations.py", None, None),
]

bad = 0
for name, filename, iface, attr in JOBS:
    mod = load(name, filename)
    table = getattr(mod, attr)
    if not iface:
        print(f"### {attr}: 跨族表（ISldWorks + IModelDoc2 + IModelDocExtension），"
              f"逐名到三段里找")
        pools = [com_name(x) for f in ("ISldWorks", "IModelDoc2", "IModelDocExtension")
                 for x in block(f)]
    else:
        pools = list(block(iface))
    for member, arity in table.items():
        if member not in pools:
            print(f"  [X] {attr}[{member}] 反射里查不到（归一化后）")
            bad += 1
        elif iface and arity not in block(iface)[member]:
            print(f"  [~] {attr}[{member}] arity {arity}，反射 "
                  f"{block(iface)[member]}")
    print(f"### {attr} 核完")

for name, filename, iface, attr in NESTED:
    mod = load(name, filename)
    if attr:
        fam = iface
        table = {attr: getattr(mod, attr)}
    else:
        fam = None
        table = mod.TABLE_ANNOTATION_ARITY
    for fam_name, members in table.items():
        target = fam_name if fam is None else fam
        pool = block(target)
        for member, arity in members.items():
            if member not in pool:
                print(f"  [X] {target}.{member} 反射里查不到（归一化后）")
                bad += 1
            elif arity not in pool[member]:
                print(f"  [~] {target}.{member} arity {arity}，反射 {pool[member]}")
    print(f"### {attr or 'TABLE_ANNOTATION_ARITY'} 核完")

print(f"\n不一致 = {bad}")
