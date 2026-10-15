# -*- coding: utf-8 -*-
"""删掉本任务新建模块里的「逐成员短名」层，只留官方名通道。

用户判断：短名（create_cut / get_title …）**不通用**——官方名到处能用，
短名只有这个仓库认。所以只保留：
  · 登记表（ARITY / PROPERTIES / 枚举常量）—— 抄自官方
  · 通用入口 call_*（官方名的唯一通道，带 arity 护栏）
  · 两个 try/finally 的选区事务（真行为，不是别名）
  · 转发上游 _select_by_id（带「面名随语言变」候选机制，复制会漂移）

⚑ **不动上游自有模块**（sw_part / sw_view / sw_sketch / sw_routing /
  sw_selection / sw_hole_features …）—— 那是项目本来的 API，不是本任务的短名。
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
KEEP = {
    "call_hub", "call_annotation", "call_feature_data", "call_entity",
    "call_member", "call_sim", "call_sheet_metal", "call_sketch",
    "call_geometry", "edit_feature_selection", "edit_sheet_metal_selection",
    "select_by_id",
}


def drop_functions(path: Path) -> list[str]:
    """删掉该文件里要删的顶层函数；返回被删的名字。"""
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    tree = ast.parse(src)
    spans = []
    removed = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith("_") or node.name in KEEP:
            continue
        start = node.lineno - 1
        end = node.end_lineno
        # 连同上方紧邻的注释/空行一起去掉
        while start > 0 and (lines[start - 1].strip().startswith("#")
                             or not lines[start - 1].strip()):
            start -= 1
        spans.append((start, end))
        removed.append(node.name)
    if not spans:
        return []
    for start, end in sorted(spans, reverse=True):
        del lines[start:end]
    out = "\n".join(lines)
    # __all__ 里同步删除
    m = re.search(r"__all__\s*=\s*\[(.*?)\]", out, re.S)
    if m:
        items = [it.strip() for it in m.group(1).split(",") if it.strip()]
        kept = [it for it in items if it.strip('"\'') not in removed]
        new = "__all__ = [\n" + "".join(f"    {it},\n" for it in kept) + "]"
        out = out[:m.start()] + new + out[m.end():]
    path.write_text(out, encoding="utf-8")
    return removed


total = 0
for m in MINE:
    p = REPO / "scripts" / f"{m}.py"
    if not p.is_file():
        continue
    removed = drop_functions(p)
    if removed:
        total += len(removed)
        print(f"  {m:<26} 删 {len(removed):2d} 个")
        # 语法自检：删完必须还能编译
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            print(f"     [FATAL] {m} 删后语法错误: {exc}")
            sys.exit(2)
print(f"合计删除 {total} 个短名")
