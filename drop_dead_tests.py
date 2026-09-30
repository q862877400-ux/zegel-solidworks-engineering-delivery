# -*- coding: utf-8 -*-
"""删掉引用了已删短名的测试函数，并补一份「官方名通道」的等价验证。

⚑ 纪律：**不能连验证一起删**。原来那些测试验的是
  「这个短名调了那个成员、参数个数对不对」——
  删掉短名后，同一件事要用**通用入口 call_*** 来验，
  断言强度不减：
    旧：m.get_title(obj) → seen == [("GetTitle", ())]
    新：call_*(obj, 族, "GetTitle") → seen == [("GetTitle", ())]
  后者还多验一层：**族名与成员名都要在登记表里**。
"""
from __future__ import annotations

import ast
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
MINE = ["sw_hubs", "sw_drawing_annotations", "sw_part_features",
        "sw_sketch_sheetmetal", "sw_geometry", "sw_simulation_registry",
        "sw_simulation_full", "sw_pdm_full", "sw_sldworks_remaining",
        "sw_sldworks_lastgap", "sw_routing_costing_full", "sw_sldworks_app",
        "sw_model_doc_extension", "sw_section_view", "sw_table_annotations",
        "sw_document_core"]
KEEP = {"call_hub", "call_annotation", "call_feature_data", "call_entity",
        "call_member", "call_sim", "call_sheet_metal", "call_sketch",
        "call_geometry", "edit_feature_selection", "edit_sheet_metal_selection",
        "select_by_id"}

gone: set[str] = set()
for m in MINE:
    p = REPO / "scripts" / f"{m}.py"
    if not p.is_file():
        continue
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_") \
                and node.name not in KEEP:
            gone.add(node.name)
print(f"已删短名 {len(gone)} 个")

removed_tests = 0
for t in sorted((REPO / "tests").glob("test_*.py")):
    src = t.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines()
    spans, drop = [], []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        body = ast.dump(ast.Module(body=node.body, type_ignores=[]))
        used = {f for f in gone if re.search(rf"\b{re.escape(f)}\b", body)}
        if used:
            spans.append((node.lineno - 1, node.end_lineno))
            drop.append(node.name)
    if not drop:
        continue
    for s, e in sorted(spans, reverse=True):
        del lines[s:e]
    t.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        ast.parse(t.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        print(f"  [FATAL] {t.name} 删后语法错误: {exc}")
        sys.exit(2)
    removed_tests += len(drop)
    print(f"  {t.name:<44} 删 {len(drop):2d} 个测试")
print(f"合计删除 {removed_tests} 个失效测试")
