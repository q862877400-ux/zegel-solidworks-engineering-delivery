# -*- coding: utf-8 -*-
"""把 22 个自造访问器收敛成 1 个，并把被全量索引取代的 16 个模块删掉。

⚑ 用户要求：「不要有自创的东西」。
  我此前留了 **11 个不同名字**的访问器（call_index / call_hub / call_member /
  call_sim / call_annotation / call_feature_data / call_entity / call_geometry /
  call_sketch / call_sheet_metal / describe），干的是同一件事，
  而且其中 10 个指向**不完整**的表（已被 sw_api_* 全量索引完全覆盖）。

保留的只有：
  · 6 份 ``sw_api_<程序集>.py`` —— 官方名字 + 官方参数个数 + 一个同形访问器
  · 1 个名字：``call_index``（在 6 份里同名，行为一致，只是读各自的表）

删除的：
  · 16 个「部分索引」模块（表是全量索引的真子集，无独立价值）
  · 10 个重复访问器
  · ``describe``（6 份重复的调试助手）
  · 2 份重复的 ``select_by_id``（转发上游 ``_select_by_id``，纯重复）
"""
from __future__ import annotations

import ast
import io
import re
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO = Path(r"C:\swprojects\sw-skill-fork")
SCRIPTS = REPO / "scripts"

SUPERSEDED = [
    "sw_hubs", "sw_drawing_annotations", "sw_part_features",
    "sw_sketch_sheetmetal", "sw_geometry", "sw_simulation_registry",
    "sw_simulation_full", "sw_pdm_full", "sw_sldworks_remaining",
    "sw_sldworks_lastgap", "sw_routing_costing_full", "sw_sldworks_app",
    "sw_model_doc_extension", "sw_section_view", "sw_table_annotations",
    "sw_document_core",
]
#: 全量索引里保留的两个**行为**（不是 API 成员别名）—— 见 main 末尾说明
KEEP_BEHAVIOUR = {"edit_feature_selection", "edit_sheet_metal_selection"}

# 1) 抽出生存符号，供测试文件改写用
survivors: set[str] = set()
for m in SUPERSEDED:
    p = SCRIPTS / f"{m}.py"
    if not p.is_file():
        continue
    for x in re.finditer(r"^def (\w+)\s*\(", p.read_text(encoding="utf-8"), re.M):
        if not x.group(1).startswith("_") and x.group(1) in KEEP_BEHAVIOUR:
            survivors.add(x.group(1))
print("保留的行为符号:", sorted(survivors))

# 2) 把 16 个模块里**仅供转发的**行为函数搬到一个地方，其余整体删除
host = SCRIPTS / "sw_api_sldworks.py"
moved = []
for m in SUPERSEDED:
    p = SCRIPTS / f"{m}.py"
    if not p.is_file():
        continue
    src = p.read_text(encoding="utf-8")
    for name in sorted(survivors):
        m2 = re.search(rf"\ndef {name}\(.*?(?=\n\ndef |\n\n# ──|\Z)", src, re.S)
        if m2:
            moved.append((name, m2.group(0).strip()))

if moved:
    doc = SCRIPTS / "sw_selection_tx.py"
    body = ['r"""选区事务：``AccessSelections`` / ``ReleaseSelectionAccess`` 的成对管理。',
            "",
            "⚑ 这两个**不是 API 成员的别名** —— 它们只做一件事：保证异常路径也会释放",
            "   选区接管（官方两个成员是 ``AccessSelections(Object, Object)`` 2 参 +",
            "   ``ReleaseSelectionAccess()`` 零参，必须成对调用）。",
            "",
            "签名来源: 对 SolidWorks.Interop.sldworks.dll 的纯元数据反射。",
            "⚠ 本模块为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）。",
            '"""',
            "from __future__ import annotations",
            "",
            "from contextlib import contextmanager",
            "",
            "try:",
            "    from .sw_api_sldworks import call_index",
            "except ImportError:",
            "    from sw_api_sldworks import call_index",
            ""]
    for name, code in moved:
        code = re.sub(r"call_feature_data\(", "call_index(", code)
        code = re.sub(r"call_sheet_metal\(", "call_index(", code)
        body.append(code)
        body.append("")
    doc.write_text("\n".join(body) + "\n", encoding="utf-8")
    ast.parse(doc.read_text(encoding="utf-8"))
    print(f"  行为已集中到 {doc.name}: {[n for n, _ in moved]}")

# 3) 删 16 个被取代的模块
for m in SUPERSEDED:
    p = SCRIPTS / f"{m}.py"
    if p.is_file():
        p.unlink()
        print(f"  删 {m}.py")
print(f"\n删除 {len(SUPERSEDED)} 个被全量索引取代的模块")
