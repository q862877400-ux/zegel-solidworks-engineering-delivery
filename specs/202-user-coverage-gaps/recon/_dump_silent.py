"""★ 打印 24 条「静默」候选的 spec 段 + 目标函数全文，供人工逐条读。"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
MCP = ROOT / "mcp-server"
SCR = ROOT / "scripts"

SILENT = [
    ("solidworks_mold_parting_line", "sw_mold", "insert_parting_line"),
    ("solidworks_mold_parting_surface", "sw_mold", "insert_parting_surface"),
    ("solidworks_topology_create_preserved_region", "sw_topology", "create_preserved_region"),
    ("solidworks_topology_create_symmetry_control", "sw_topology", "create_symmetry_control"),
    ("solidworks_topology_create_demold_control", "sw_topology", "create_demold_control"),
    ("solidworks_add_sketch_relation", "sw_part", "add_sketch_relation"),
    ("solidworks_part_insert_composite_curve", "sw_part", "insert_composite_curve_report"),
    ("solidworks_part_insert_dome", "sw_part", "insert_dome_report"),
    ("solidworks_weldment_create_profile_center_mate", "sw_weldment", "create_profile_center_mate"),
    ("solidworks_helix_insert", "sw_helix", "insert_helix"),
    ("solidworks_sketch_convert_entities", "sw_sketch_edit", "convert_entities"),
    ("solidworks_sketch_create_chamfer", "sw_sketch_edit", "create_sketch_chamfer"),
    ("solidworks_sketch_mirror", "sw_sketch_edit", "sketch_mirror"),
    ("solidworks_sketch_stretch_entities", "sw_sketch_modify_ops", "sketch_stretch"),
    ("solidworks_insert_planar_surface", "sw_surface_edit_ops", "insert_planar_surface"),
    ("solidworks_insert_offset_surface", "sw_surface_edit_ops", "insert_offset_surface"),
    ("solidworks_insert_ruled_surface", "sw_surface_edit_ops", "insert_ruled_surface"),
    ("solidworks_insert_replace_face", "sw_surface_edit_ops", "insert_replace_face"),
    ("solidworks_insert_lofted_ref_surface", "sw_surface_ref_ops", "insert_lofted_ref_surface"),
    ("solidworks_create_revolved_surface", "sw_surface_ref_ops", "insert_revolved_ref_surface"),
    ("solidworks_insert_ref_plane", "sw_ref_geometry", "insert_ref_plane"),
    ("solidworks_insert_reference_point", "sw_ref_geometry", "insert_reference_point"),
    ("solidworks_insert_global_bounding_box", "sw_ref_geometry", "insert_global_bounding_box"),
    ("solidworks_drawing_add_note", "sw_drawing_expose", "add_drawing_note"),
]

SEP = "=" * 100


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
    outp = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_silent_dump.txt"
    chunks = []
    for tool, mod, fn in SILENT:
        sf, seg = spec_segment(tool)
        ff, fsrc = func_full(mod, fn)
        chunks.append(SEP)
        chunks.append(f"### {tool}    spec={sf}   func={ff}::{fn}")
        chunks.append(SEP)
        chunks.append("---- SPEC ----")
        chunks.append(seg or "<none>")
        chunks.append("---- FUNC ----")
        chunks.append(fsrc or "<none>")
        chunks.append("")
    outp.write_text("\n".join(chunks), encoding="utf-8")
    print("wrote", outp, len(outp.read_text(encoding='utf-8')), "chars")


if __name__ == "__main__":
    main()