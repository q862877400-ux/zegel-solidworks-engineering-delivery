"""★ 打印 17 条「函数体内有选区 token」的候选：spec 段 + 目标函数全文。"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
MCP = ROOT / "mcp-server"
SCR = ROOT / "scripts"

TOK = [
    ("solidworks_surface_fill", "sw_surface_features", "insert_fill_surface_report"),
    ("solidworks_measure_selection", "sw_measure", "measure_selection_report"),
    ("solidworks_part_loft", "sw_loft", "create_loft_report"),
    ("solidworks_part_sweep", "sw_sweep", "create_sweep_report"),
    ("solidworks_part_axis", "sw_part", "create_axis_report"),
    ("solidworks_part_wrap", "sw_wrap", "create_wrap_report"),
    ("solidworks_selection_count", "sw_selection_spec", "get_selection_count"),
    ("solidworks_resolve_selection", "sw_selection_spec", "resolve_selection"),
    ("solidworks_selection_point", "sw_selection_spec", "selection_point"),
    ("solidworks_resolve_entity", "sw_selection_spec", "resolve_entity_report"),
    ("solidworks_drawing_create_auxiliary_view", "sw_drawing_create_missing", "create_auxiliary_view"),
    ("solidworks_drawing_insert_surface_finish_symbol", "sw_drawing_create_missing", "insert_surface_finish_symbol"),
    ("solidworks_drawing_insert_datum_tag", "sw_drawing_create_missing", "insert_datum_tag"),
    ("solidworks_sheet_metal_insert_miter_flange", "sw_sheet_metal_weld_entry", "insert_sheet_metal_miter_flange"),
    ("solidworks_sheet_metal_insert_closed_corner", "sw_sheet_metal_weld_entry", "insert_sheet_metal_closed_corner"),
    ("solidworks_drawing_create_section_view", "sw_drawing_expose", "create_section_view"),
    ("solidworks_drawing_create_hole_table", "sw_drawing_expose", "create_hole_table"),
]


def spec_segment(tool):
    for f in MCP.glob("tool_specs_batch*.py"):
        txt = f.read_text(encoding="utf-8")
        if f'"{tool}"' not in txt:
            continue
        tree = ast.parse(txt)
        lines = txt.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
            if fn not in ("ToolSpec", "_spec"):
                continue
            lits = []
            try:
                for a in list(node.args) + [k.value for k in node.keywords]:
                    lits.append(ast.literal_eval(a))
            except Exception:
                pass
            if tool not in lits:
                continue
            return f.name, "\n".join(lines[node.lineno - 1:node.end_lineno])
    return None, None


def func_full(module, function):
    p = SCR / f"{module}.py"
    txt = p.read_text(encoding="utf-8")
    tree = ast.parse(txt)
    lines = txt.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            return p.name, "\n".join(lines[node.lineno - 1:node.end_lineno])
    return None, None


def main():
    chunks = []
    for tool, mod, fn in TOK:
        sf, seg = spec_segment(tool)
        ff, fsrc = func_full(mod, fn)
        chunks.append("=" * 100)
        chunks.append(f"### {tool}    spec={sf}   func={ff}::{fn}")
        chunks.append("=" * 100)
        chunks.append("---- SPEC ----")
        chunks.append(seg or "<none>")
        chunks.append("---- FUNC ----")
        chunks.append(fsrc or "<none>")
        chunks.append("")
    outp = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_tokened_dump.txt"
    outp.write_text("\n".join(chunks), encoding="utf-8")
    print("wrote", outp)


if __name__ == "__main__":
    main()