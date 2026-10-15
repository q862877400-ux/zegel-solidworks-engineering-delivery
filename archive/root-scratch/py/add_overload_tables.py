# -*- coding: utf-8 -*-
"""把「多重重载」成员的**全部合法 arity** 导出成例外表，附到各模块。"""
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

MODULES = {"sw_simulation_registry": "SIM_ARITY",
           "sw_simulation_full": "ARITY",
           "sw_pdm_full": "ARITY",
           "sw_sldworks_remaining": "ARITY",
           "sw_routing_costing_full": "ARITY"}
ROW = re.compile(r"^(\s+)(['\"])([A-Za-z_]\w*)\2(\s*:\s*)(\d+)(\s*,?\s*)$")
FAM = re.compile(r"^\s{4}['\"](\w+)['\"]\s*:\s*\{")

NOTE = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（各 interop 程序集的纯元数据反射）
# 文件:   D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt 等 6 份
# 定位:   **多重重载**成员的合法 arity 全集。
# ⚑⚑ 为什么要有这张表：上方的 arity 表每个成员只存**一个**数字，
#   但反射实测有 %d 个成员存在**多个合法 arity**（同名不同参的版本）。
#   对这些成员，单一数字会让护栏**误拒**合法调用。
# ⚠ 处理方式：护栏在查到本表时，改用这里的**全集**判定。
#   不改主表，是因为主表要给「典型调用形态」一个默认值。
# ⚠ 本表是**审计产物**，逐条从反射算出，不手抄。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
OVERLOAD_ARITY: dict[str, tuple[int, ...]] = {
%s}
'''

for mod, attr in MODULES.items():
    p = REPO / "scripts" / f"{mod}.py"
    if not p.is_file():
        continue
    lines = p.read_text(encoding="utf-8").splitlines()
    fam = None
    found: dict[str, list[int]] = {}
    for line in lines:
        fm = FAM.match(line)
        if fm:
            fam = fm.group(1)
        rm = ROW.match(line)
        if not rm or fam is None or fam not in pool:
            continue
        mem, ar = rm.group(3), int(rm.group(5))
        real = pool[fam].get(mem)
        if real and len(real) > 1:
            found[f"{fam}.{mem}"] = sorted(real)
    if not found:
        print(f"  {mod}: 无多重成员")
        continue
    body = "".join(f'    "{k}": {tuple(v)},\n' for k, v in sorted(found.items()))
    p.write_text("\n".join(lines) + (NOTE % (len(found), body)), encoding="utf-8")
    print(f"  {mod}: 记录 {len(found)} 个多重成员")
